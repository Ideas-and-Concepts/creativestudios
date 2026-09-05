"""Shared, UI-free project controls calculations for Creative Studios.

The calculation contract is intentionally independent of Streamlit so the same
rules can be mirrored by other clients such as the Vercel application.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone
from typing import Any


def number(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def as_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time(), tzinfo=timezone.utc)
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def planned_value_at(amount: float, start: Any, end: Any, as_of: datetime) -> float:
    start_dt = as_datetime(start)
    end_dt = as_datetime(end)
    if amount <= 0 or start_dt is None or end_dt is None or end_dt <= start_dt:
        return 0.0
    if as_of <= start_dt:
        return 0.0
    if as_of >= end_dt:
        return amount
    return amount * ((as_of - start_dt).total_seconds() / (end_dt - start_dt).total_seconds())


def _field(record: dict[str, Any], *names: str) -> Any:
    for name in names:
        value = record.get(name)
        if value not in (None, ""):
            return value
    return None


def _boq_indexes(boq_items: list[dict[str, Any]]) -> tuple[dict[str, float], dict[str, float]]:
    by_id: dict[str, float] = {}
    by_code: dict[str, float] = {}
    for item in boq_items:
        amount = number(_field(item, "amount"))
        if _field(item, "id") is not None:
            by_id[str(_field(item, "id"))] = amount
        code = _field(item, "item_code", "itemCode")
        if code not in (None, ""):
            by_code[str(code)] = amount
    return by_id, by_code


def _activity_baselines(
    boq_items: list[dict[str, Any]],
    construction_activities: list[dict[str, Any]],
    site_progress_logs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Collapse multiple construction activities onto each BOQ item once.

    A BOQ item is a budget baseline, so linking two activities to the same BOQ
    item must not double-count its value. Progress is the highest usable
    activity progress for that BOQ item. Quantity progress is preferred when a
    planned quantity exists and the units match the site logs.
    """
    by_id, by_code = _boq_indexes(boq_items)
    logs_by_activity: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for log in site_progress_logs:
        activity_id = _field(log, "activity_id", "activityId")
        if activity_id is not None:
            logs_by_activity[str(activity_id)].append(log)

    grouped: dict[str, dict[str, Any]] = {}
    for activity in construction_activities:
        boq_id = _field(activity, "boq_item_id", "boqItemId")
        amount = by_id.get(str(boq_id), 0.0) if boq_id is not None else 0.0
        if amount <= 0:
            code = _field(activity, "boq_item_code", "boqItemCode", "item_code", "itemCode")
            amount = by_code.get(str(code), 0.0) if code not in (None, "") else 0.0
        if amount <= 0:
            continue

        activity_id = _field(activity, "id")
        planned_qty = number(_field(activity, "planned_quantity", "plannedQuantity"))
        actual_qty = number(_field(activity, "actual_quantity", "actualQuantity"))
        unit = str(_field(activity, "unit") or "").strip().lower()
        progress = clamp(number(_field(activity, "progress")))

        logs = logs_by_activity.get(str(activity_id), []) if activity_id is not None else []
        logged_qty = 0.0
        if logs and unit:
            for log in logs:
                log_unit = str(_field(log, "unit") or "").strip().lower()
                if log_unit == unit:
                    logged_qty += number(_field(log, "quantity_completed", "quantityCompleted"))
        elif logs:
            logged_qty = sum(number(_field(log, "quantity_completed", "quantityCompleted")) for log in logs)

        quantity_actual = max(actual_qty, logged_qty)
        if planned_qty > 0 and quantity_actual > 0:
            progress = max(progress, clamp(quantity_actual / planned_qty * 100.0))

        key = str(boq_id) if boq_id is not None else f"code:{_field(activity, 'boq_item_code', 'boqItemCode', 'item_code', 'itemCode')}"
        start = as_datetime(_field(activity, "planned_start", "plannedStart"))
        end = as_datetime(_field(activity, "planned_end", "plannedEnd"))
        current = grouped.get(key)
        if current is None:
            grouped[key] = {"amount": amount, "progress": progress, "start": start, "end": end, "activities": 1}
        else:
            current["progress"] = max(current["progress"], progress)
            current["start"] = min(filter(None, [current["start"], start]), default=None)
            current["end"] = max(filter(None, [current["end"], end]), default=None)
            current["activities"] += 1
    return list(grouped.values())


def calculate_evm(
    boq_items: list[dict[str, Any]],
    construction_activities: list[dict[str, Any]],
    cost_records: list[dict[str, Any]] | None = None,
    site_progress_logs: list[dict[str, Any]] | None = None,
    as_of: Any | None = None,
) -> dict[str, Any]:
    """Calculate the Creative Studios EVM contract.

    BAC is the complete BOQ baseline. EV and PV use each BOQ item once, even
    when multiple construction activities point to it. Site progress logs can
    improve activity physical progress when quantity and unit data are usable.
    """
    snapshot = as_datetime(as_of) or datetime.now(timezone.utc)
    costs = cost_records or []
    logs = site_progress_logs or []
    bac = sum(number(_field(item, "amount")) for item in boq_items)
    actual_cost = sum(number(_field(row, "amount")) for row in costs if str(_field(row, "cost_type", "costType") or "").strip().lower() == "actual cost")

    baselines = _activity_baselines(boq_items, construction_activities, logs)
    pv = sum(planned_value_at(row["amount"], row["start"], row["end"], snapshot) for row in baselines)
    ev = sum(row["amount"] * row["progress"] / 100.0 for row in baselines)
    covered = sum(1 for row in baselines if row["amount"] > 0 and row["start"] and row["end"])

    cv = ev - actual_cost
    sv = ev - pv
    cpi = ev / actual_cost if actual_cost > 0 else None
    spi = ev / pv if pv > 0 else None
    eac = bac / cpi if cpi and cpi > 0 else bac
    etc = max(0.0, eac - actual_cost)
    vac = bac - eac
    tcpi_bac = (bac - ev) / (bac - actual_cost) if bac - actual_cost > 0 else None
    tcpi_eac = (bac - ev) / (eac - actual_cost) if eac - actual_cost > 0 else None

    return {
        "as_of": snapshot,
        "bac": bac,
        "pv": pv,
        "ev": ev,
        "ac": actual_cost,
        "cv": cv,
        "sv": sv,
        "cpi": cpi,
        "spi": spi,
        "eac": eac,
        "etc": etc,
        "vac": vac,
        "tcpi_bac": tcpi_bac,
        "tcpi_eac": tcpi_eac,
        "physical": clamp(ev / bac * 100.0) if bac > 0 else 0.0,
        "financial": clamp(actual_cost / bac * 100.0) if bac > 0 else 0.0,
        "covered": covered,
        "activities": len(construction_activities),
        "baseline_items": len(baselines),
        "site_logs": len(logs),
    }
