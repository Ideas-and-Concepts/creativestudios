"""Relational procurement persistence helpers for Creative Studios."""
from __future__ import annotations
from typing import Any
from .database import _neon_connect, _rows_as_dicts

SUPPLIER_FIELDS = {"code", "name", "contact_name", "email", "phone", "address", "tax_number", "category", "notes", "is_active"}
SUPPLIER_SELECT = "id,code,name,contact_name,email,phone,address,tax_number,category,notes,is_active,created_at,updated_at"
ORDER_FIELDS = {"project_id", "supplier_id", "po_number", "status", "order_date", "expected_delivery_date", "subtotal", "tax_amount", "total_amount", "notes"}
ORDER_SELECT = "id,project_id,supplier_id,po_number,status,order_date,expected_delivery_date,subtotal,tax_amount,total_amount,notes,created_at,updated_at"
ITEM_FIELDS = {"purchase_order_id", "boq_item_id", "description", "quantity", "unit", "unit_rate", "amount"}
ITEM_SELECT = "id,purchase_order_id,boq_item_id,description,quantity,unit,unit_rate,amount,created_at,updated_at"


def get_relational_suppliers(active_only: bool = False) -> list[dict[str, Any]]:
    where = " WHERE is_active = true" if active_only else ""
    with _neon_connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT {SUPPLIER_SELECT} FROM suppliers{where} ORDER BY name")
            return _rows_as_dicts(cursor)


def create_relational_supplier(values: dict[str, Any]) -> dict[str, Any]:
    unknown = set(values) - SUPPLIER_FIELDS
    if unknown:
        raise ValueError(f"Unsupported supplier fields: {', '.join(sorted(unknown))}")
    if not {"code", "name"}.issubset(values):
        raise ValueError("Supplier code and name are required.")
    with _neon_connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO suppliers (code,name,contact_name,email,phone,address,tax_number,category,notes,is_active) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING {SUPPLIER_SELECT}",
                (values["code"], values["name"], values.get("contact_name"), values.get("email"), values.get("phone"), values.get("address"), values.get("tax_number"), values.get("category"), values.get("notes"), values.get("is_active", True)),
            )
            rows = _rows_as_dicts(cursor)
        connection.commit()
    return rows[0]


def update_relational_supplier(supplier_id: str, values: dict[str, Any]) -> dict[str, Any] | None:
    unknown = set(values) - SUPPLIER_FIELDS
    if unknown:
        raise ValueError(f"Unsupported supplier fields: {', '.join(sorted(unknown))}")
    if not values:
        raise ValueError("No supplier changes supplied.")
    assignments = ", ".join(f"{field}=%s" for field in values)
    with _neon_connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE suppliers SET {assignments},updated_at=now() WHERE id=%s RETURNING {SUPPLIER_SELECT}", [*values.values(), supplier_id])
            rows = _rows_as_dicts(cursor)
        connection.commit()
    return rows[0] if rows else None


def delete_relational_supplier(supplier_id: str) -> bool:
    with _neon_connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM suppliers WHERE id=%s RETURNING id", (supplier_id,))
            deleted = cursor.fetchone() is not None
        connection.commit()
    return deleted


def get_relational_purchase_orders(project_id: str | None = None) -> list[dict[str, Any]]:
    where = " WHERE po.project_id=%s" if project_id else ""
    params = (project_id,) if project_id else ()
    with _neon_connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT po.id,po.project_id,po.supplier_id,po.po_number,po.status,po.order_date,po.expected_delivery_date,po.subtotal,po.tax_amount,po.total_amount,po.notes,po.created_at,po.updated_at,s.code AS supplier_code,s.name AS supplier_name FROM purchase_orders po JOIN suppliers s ON s.id=po.supplier_id{where} ORDER BY po.created_at DESC",
                params,
            )
            orders = _rows_as_dicts(cursor)
            for order in orders:
                cursor.execute(f"SELECT {ITEM_SELECT} FROM purchase_order_items WHERE purchase_order_id=%s ORDER BY created_at", (order["id"],))
                order["items"] = _rows_as_dicts(cursor)
            return orders


def create_relational_purchase_order(values: dict[str, Any], items: list[dict[str, Any]]) -> dict[str, Any]:
    unknown = set(values) - ORDER_FIELDS
    if unknown:
        raise ValueError(f"Unsupported purchase order fields: {', '.join(sorted(unknown))}")
    required = {"project_id", "supplier_id", "po_number"}
    if not required.issubset(values):
        raise ValueError("Project, supplier and PO number are required.")
    with _neon_connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM suppliers WHERE id=%s AND is_active=true", (values["supplier_id"],))
            if not cursor.fetchone():
                raise ValueError("Supplier is not active or does not exist.")
            cursor.execute("SELECT id FROM projects WHERE id=%s", (values["project_id"],))
            if not cursor.fetchone():
                raise ValueError("Project does not exist.")
            subtotal = sum(float(item.get("quantity", 0) or 0) * float(item.get("unit_rate", 0) or 0) for item in items)
            tax_amount = float(values.get("tax_amount", 0) or 0)
            total_amount = subtotal + tax_amount
            cursor.execute(
                f"INSERT INTO purchase_orders (project_id,supplier_id,po_number,status,order_date,expected_delivery_date,subtotal,tax_amount,total_amount,notes) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING {ORDER_SELECT}",
                (values["project_id"], values["supplier_id"], values["po_number"], values.get("status", "draft"), values.get("order_date"), values.get("expected_delivery_date"), subtotal, tax_amount, total_amount, values.get("notes")),
            )
            order = _rows_as_dicts(cursor)[0]
            for item in items:
                if not item.get("description"):
                    raise ValueError("Every purchase order item requires a description.")
                boq_item_id = item.get("boq_item_id")
                if boq_item_id:
                    cursor.execute("SELECT id FROM boq_items WHERE id=%s AND project_id=%s", (boq_item_id, values["project_id"]))
                    if not cursor.fetchone():
                        raise ValueError("A selected BOQ item does not belong to the purchase order project.")
                quantity = float(item.get("quantity", 0) or 0)
                unit_rate = float(item.get("unit_rate", 0) or 0)
                amount = round(quantity * unit_rate, 2)
                cursor.execute(
                    f"INSERT INTO purchase_order_items (purchase_order_id,boq_item_id,description,quantity,unit,unit_rate,amount) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (order["id"], boq_item_id, item["description"], quantity, item.get("unit") or "No.", unit_rate, amount),
                )
        connection.commit()
    return order


def delete_relational_purchase_order(order_id: str) -> bool:
    with _neon_connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM purchase_orders WHERE id=%s RETURNING id", (order_id,))
            deleted = cursor.fetchone() is not None
        connection.commit()
    return deleted
