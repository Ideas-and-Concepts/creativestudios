from datetime import datetime, timezone

from modules.project_controls import calculate_evm, planned_value_at


def test_planned_value_is_time_phased():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 1, 11, tzinfo=timezone.utc)
    as_of = datetime(2026, 1, 6, tzinfo=timezone.utc)
    assert planned_value_at(1000, start, end, as_of) == 500


def test_evm_does_not_double_count_shared_boq_item():
    boq = [{"id": "b1", "amount": 1000}]
    activities = [
        {"id": "a1", "boq_item_id": "b1", "progress": 25, "planned_start": "2026-01-01", "planned_end": "2026-01-11"},
        {"id": "a2", "boq_item_id": "b1", "progress": 50, "planned_start": "2026-01-03", "planned_end": "2026-01-13"},
    ]
    result = calculate_evm(boq, activities, [{"cost_type": "Actual Cost", "amount": 200}])
    assert result["bac"] == 1000
    assert result["ev"] == 500
    assert result["physical"] == 50
    assert result["ac"] == 200


def test_site_progress_quantity_can_drive_activity_progress():
    boq = [{"id": "b1", "amount": 1000}]
    activities = [{
        "id": "a1",
        "boq_item_id": "b1",
        "progress": 10,
        "planned_quantity": 100,
        "actual_quantity": 0,
        "unit": "m3",
        "planned_start": "2026-01-01",
        "planned_end": "2026-01-11",
    }]
    logs = [{"activity_id": "a1", "quantity_completed": 40, "unit": "m3"}]
    result = calculate_evm(boq, activities, [], logs)
    assert result["ev"] == 400
    assert result["physical"] == 40
    assert result["site_logs"] == 1


def test_actual_cost_ignores_commitments():
    boq = [{"id": "b1", "amount": 1000}]
    activities = [{"id": "a1", "boq_item_id": "b1", "progress": 50}]
    costs = [
        {"cost_type": "Committed Cost", "amount": 900},
        {"cost_type": "Actual Cost", "amount": 300},
    ]
    result = calculate_evm(boq, activities, costs)
    assert result["ac"] == 300
    assert result["cv"] == 200
