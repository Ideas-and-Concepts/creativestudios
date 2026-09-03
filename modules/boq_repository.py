"""Relational BOQ persistence helpers for Creative Studios."""
from __future__ import annotations
from typing import Any
from .database import _neon_connect, _rows_as_dicts

BOQ_FIELDS={"project_id","drawing_id","item_code","category","element","description","quantity","unit","rate","amount","status"}
BOQ_SELECT="id,project_id,drawing_id,item_code,category,element,description,quantity,unit,rate,amount,status,created_at,updated_at"

def get_relational_boq_items(project_id: str|None=None, drawing_id: str|None=None)->list[dict[str,Any]]:
    clauses=[]; params=[]
    if project_id: clauses.append("project_id=%s"); params.append(project_id)
    if drawing_id: clauses.append("drawing_id=%s"); params.append(drawing_id)
    where=(" WHERE "+" AND ".join(clauses)) if clauses else ""
    with _neon_connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT {BOQ_SELECT} FROM boq_items{where} ORDER BY created_at DESC",params)
            return _rows_as_dicts(cursor)

def create_relational_boq_item(values: dict[str,Any])->dict[str,Any]:
    unknown=set(values)-BOQ_FIELDS
    if unknown: raise ValueError(f"Unsupported BOQ fields: {', '.join(sorted(unknown))}")
    required={"project_id","item_code","category","element","description","quantity","unit","rate","amount"}
    if not required.issubset(values): raise ValueError("Project, item code, category, element, description, quantity, unit, rate and amount are required.")
    with _neon_connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"INSERT INTO boq_items (project_id,drawing_id,item_code,category,element,description,quantity,unit,rate,amount,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING {BOQ_SELECT}",(values["project_id"],values.get("drawing_id"),values["item_code"],values["category"],values["element"],values["description"],values["quantity"],values["unit"],values["rate"],values["amount"],values.get("status","planned")))
            rows=_rows_as_dicts(cursor)
        connection.commit()
    return rows[0]

def update_relational_boq_item(item_id: str, values: dict[str,Any])->dict[str,Any]|None:
    unknown=set(values)-BOQ_FIELDS
    if unknown: raise ValueError(f"Unsupported BOQ fields: {', '.join(sorted(unknown))}")
    if not values: raise ValueError("No BOQ changes supplied.")
    assignments=", ".join(f"{field}=%s" for field in values)
    with _neon_connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE boq_items SET {assignments},updated_at=now() WHERE id=%s RETURNING {BOQ_SELECT}",[ *values.values(), item_id])
            rows=_rows_as_dicts(cursor)
        connection.commit()
    return rows[0] if rows else None

def delete_relational_boq_item(item_id: str)->bool:
    with _neon_connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM boq_items WHERE id=%s RETURNING id",(item_id,)); deleted=cursor.fetchone() is not None
        connection.commit()
    return deleted
