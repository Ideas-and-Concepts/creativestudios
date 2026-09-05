"""Creative Studios production BOQ module."""
from __future__ import annotations
from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import Any
import pandas as pd
import streamlit as st
from modules.database import database_backend, get_records, next_id, save_memory, get_relational_drawings
from modules.project_context import filter_project_records, project_label, project_options, select_project
from modules.boq_repository import create_relational_boq_item, delete_relational_boq_item, get_relational_boq_items, update_relational_boq_item
CATEGORIES=["Preliminaries","Earthworks","Foundations","Concrete","Reinforcement","Formwork","Columns","Beams","Slabs","Masonry","Walls","Doors","Windows","Roofing","Finishes","Civil Works","Plumbing","Electrical","Mechanical","External Works","Other"]
ELEMENTS=["Building","Substructure","Superstructure","Architecture","Structure","Civil","MEP","External Works","Other"]
UNITS=["item","m","m2","m3","kg","ton","No.","set","lot"]
STATUSES=["planned","in_progress","completed","on_hold"]
def _num(v:Any)->float:
    try:return float(v or 0)
    except (TypeError,ValueError):return 0.0
def _money(v:Any)->Decimal:
    try:return Decimal(str(v or 0)).quantize(Decimal("0.01"))
    except (InvalidOperation,ValueError,TypeError):return Decimal("0.00")
def _amount(q:Any,r:Any)->Decimal:return (_money(q)*_money(r)).quantize(Decimal("0.01"))
def _records(db,project_id,drawing_id=None):
    if database_backend()=="neon":return get_relational_boq_items(str(project_id),str(drawing_id) if drawing_id else None)
    return [r for r in filter_project_records(get_records("boq",db),project_id) if not drawing_id or str(r.get("drawing_id"))==str(drawing_id)]
def _duplicate_code(records,code,record_id=None):return bool(code and any(str(r.get("item_code","")).strip().lower()==code.lower() and str(r.get("id"))!=str(record_id) for r in records))
def render_boq_module(database:dict[str,Any])->None:
    st.title("Bill of Quantities");st.caption("Project-linked quantities, construction elements and cost planning.")
    project_id=select_project(database,label="Project",key="cs_boq_project")
    if not project_id:return
    if database_backend()=="neon":all_drawings=[r for r in get_relational_drawings(str(project_id))]
    else:all_drawings=filter_project_records(get_records("drawings",database),project_id)
    drawing_labels=["All drawings"]+[f"{d.get('drawing_number','')} | {d.get('title','')}" for d in all_drawings];drawing_choice=st.selectbox("Drawing filter",drawing_labels,key="boq_drawing_filter")
    drawing_id=None if drawing_choice=="All drawings" else all_drawings[drawing_labels.index(drawing_choice)-1].get("id")
    records=_records(database,project_id,drawing_id);total=sum(_amount(r.get("quantity"),r.get("rate")) for r in records);quantity=sum(_num(r.get("quantity")) for r in records)
    c1,c2,c3,c4=st.columns(4);c1.metric("BOQ Items",len(records));c2.metric("Total Quantity",f"{quantity:,.2f}");c3.metric("Estimated Amount",f"{total:,.2f}");c4.metric("Backend",database_backend().upper())
    if records:
        category_totals={}
        for r in records:category_totals[r.get("category","Other")]=category_totals.get(r.get("category","Other"),Decimal("0"))+_amount(r.get("quantity"),r.get("rate"))
        st.subheader("Category Summary");st.dataframe(pd.DataFrame([{"Category":k,"Amount":float(v)} for k,v in sorted(category_totals.items())]),use_container_width=True,hide_index=True)
    st.subheader("BOQ Register");search=st.text_input("Search BOQ").strip().lower();visible=[r for r in records if not search or search in str(r).lower()]
    for record in list(visible):
        rid=record.get("id");current_drawing=record.get("drawing_id")
        with st.expander(f"{record.get('item_code','')} | {record.get('description','BOQ Item')} | {record.get('category','Other')}"):
            with st.form(f"boq_edit_{rid}"):
                code=st.text_input("Item Code",value=str(record.get("item_code","")));element=st.selectbox("Element",ELEMENTS,index=ELEMENTS.index(record.get("element","Other")) if record.get("element","Other") in ELEMENTS else len(ELEMENTS)-1);description=st.text_input("Description",value=str(record.get("description","")));category=st.selectbox("Category",CATEGORIES,index=CATEGORIES.index(record.get("category","Other")) if record.get("category","Other") in CATEGORIES else len(CATEGORIES)-1);unit=st.selectbox("Unit",UNITS,index=UNITS.index(record.get("unit","item")) if record.get("unit","item") in UNITS else 0);quantity=st.number_input("Quantity",min_value=0.0,value=_num(record.get("quantity")),format="%.3f");rate=st.number_input("Rate",min_value=0.0,value=_num(record.get("rate")),format="%.2f");status=st.selectbox("Status",STATUSES,index=STATUSES.index(record.get("status","planned")) if record.get("status","planned") in STATUSES else 0)
                drawing_options=[("None",None)]+[(f"{d.get('drawing_number','')} | {d.get('title','')}",d.get("id")) for d in all_drawings];drawing_names=[x[0] for x in drawing_options];existing_name=next((n for n,i in drawing_options if str(i)==str(current_drawing)),"None");drawing_name=st.selectbox("Design / Drawing Reference",drawing_names,index=drawing_names.index(existing_name));notes=st.text_area("Notes",value=str(record.get("notes","")));save=st.form_submit_button("Save Changes",use_container_width=True)
            if save:
                if not description.strip():st.error("Description is required.")
                elif _duplicate_code(records,code.strip(),rid):st.error("Item Code must be unique within the project.")
                else:
                    values={"item_code":code.strip(),"element":element,"description":description.strip(),"category":category,"unit":unit,"quantity":f"{quantity:.3f}","rate":f"{rate:.2f}","amount":str(_amount(quantity,rate)),"status":status,"drawing_id":dict(drawing_options)[drawing_name]}
                    if database_backend()=="neon":update_relational_boq_item(str(rid),values)
                    else:record.update(values);record["notes"]=notes.strip();record["updated_at"]=datetime.now().isoformat(timespec="seconds");save_memory(database)
                    st.success("BOQ item updated.");st.rerun()
            if st.button("Delete Item",key=f"boq_delete_{rid}",use_container_width=True):
                if database_backend()=="neon":delete_relational_boq_item(str(rid))
                else:database["boq"].remove(record);save_memory(database)
                st.rerun()
    st.divider();st.subheader("Add BOQ Item")
    with st.form("boq_add",clear_on_submit=True):
        code=st.text_input("Item Code");element=st.selectbox("Element",ELEMENTS);description=st.text_input("Description");category=st.selectbox("Category",CATEGORIES);unit=st.selectbox("Unit",UNITS);quantity=st.number_input("Quantity",min_value=0.0,value=1.0,format="%.3f");rate=st.number_input("Rate",min_value=0.0,value=0.0,format="%.2f");status=st.selectbox("Status",STATUSES);drawing_options=[("None",None)]+[(f"{d.get('drawing_number','')} | {d.get('title','')}",d.get("id")) for d in all_drawings];drawing_name=st.selectbox("Design / Drawing Reference",[x[0] for x in drawing_options]);notes=st.text_area("Notes");submitted=st.form_submit_button("Add BOQ Item",use_container_width=True)
    if submitted:
        code=code.strip();description=description.strip()
        if not description:st.error("Description is required.")
        elif _duplicate_code(records,code):st.error("Item Code must be unique within the project.")
        else:
            drawing_id=dict(drawing_options)[drawing_name];amount=_amount(quantity,rate)
            if database_backend()=="neon":create_relational_boq_item({"project_id":str(project_id),"drawing_id":drawing_id,"item_code":code,"element":element,"description":description,"category":category,"unit":unit,"quantity":f"{quantity:.3f}","rate":f"{rate:.2f}","amount":str(amount),"status":status})
            else:database["boq"].append({"id":next_id("boq",database),"project_id":project_id,"drawing_id":drawing_id,"item_code":code,"element":element,"description":description,"category":category,"unit":unit,"quantity":quantity,"rate":rate,"amount":float(amount),"status":status,"notes":notes,"created_at":datetime.now().isoformat(timespec="seconds")});save_memory(database)
            st.success("BOQ item added.");st.rerun()
