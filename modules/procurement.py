"""Creative Studios production procurement module."""
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Any
import pandas as pd
import streamlit as st
from modules.database import database_backend, get_records, save_memory
from modules.project_context import project_label, project_options
from modules.procurement_repository import (
    create_relational_purchase_order, create_relational_supplier,
    delete_relational_purchase_order, delete_relational_supplier,
    get_relational_purchase_orders, get_relational_suppliers,
    update_relational_supplier,
)

STATUSES = ["draft", "requested", "approved", "ordered", "partially_received", "received", "cancelled"]
STATUS_LABELS = {"draft":"Draft","requested":"Requested","approved":"Approved","ordered":"Ordered","partially_received":"Partially received","received":"Received","cancelled":"Cancelled"}
CATEGORIES = ["Building materials","Electrical","Mechanical","Plumbing","Plant and equipment","Professional services","Transport and logistics","Other"]

def money(value: Any) -> Decimal:
    try: return Decimal(str(value or 0)).quantize(Decimal("0.01"))
    except Exception: return Decimal("0.00")

def suppliers(db):
    return get_relational_suppliers() if database_backend() == "neon" else get_records("suppliers", db)

def orders(db, project_id):
    if database_backend() == "neon": return get_relational_purchase_orders(str(project_id))
    return [r for r in get_records("procurement", db) if str(r.get("project_id")) == str(project_id)]

def boq_for_project(db, project_id):
    if database_backend() == "neon":
        from modules.boq_repository import get_relational_boq_items
        return get_relational_boq_items(str(project_id))
    return [r for r in get_records("boq", db) if str(r.get("project_id")) == str(project_id)]

def render_procurement_module(database: dict[str, Any]) -> None:
    st.title("Procurement")
    st.caption("Suppliers, BOQ-linked purchasing and controlled purchase orders.")
    projects = project_options(database)
    if not projects:
        st.warning("Create a project first in Projects."); return
    labels = [project_label(p) for p in projects]
    selected = st.selectbox("Project", labels, key="procurement_project")
    project_id = projects[labels.index(selected)]["id"]
    supplier_rows = suppliers(database)
    order_rows = orders(database, project_id)
    boq_rows = boq_for_project(database, project_id)

    committed = sum(money(o.get("total_amount", o.get("amount", 0))) for o in order_rows if o.get("status") != "cancelled")
    ordered = sum(money(o.get("total_amount", o.get("amount", 0))) for o in order_rows if o.get("status") == "ordered")
    received = sum(money(o.get("total_amount", o.get("amount", 0))) for o in order_rows if o.get("status") == "received")
    c1,c2,c3,c4=st.columns(4); c1.metric("Purchase Orders",len(order_rows)); c2.metric("Committed",f"{committed:,.2f}"); c3.metric("Ordered",f"{ordered:,.2f}"); c4.metric("Received",f"{received:,.2f}")

    orders_tab, suppliers_tab = st.tabs(["Purchase Orders", "Suppliers"])
    with orders_tab:
        query=st.text_input("Search purchase orders",key="procurement_search").strip().lower()
        status=st.selectbox("Status",["All"]+STATUSES,key="procurement_status",format_func=lambda x:"All" if x=="All" else STATUS_LABELS[x])
        visible=[o for o in order_rows if (not query or query in str(o).lower()) and (status=="All" or o.get("status")==status)]
        if visible:
            st.dataframe(pd.DataFrame([{ "PO Number":o.get("po_number",""),"Supplier":o.get("supplier_name",o.get("supplier","")),"Status":STATUS_LABELS.get(o.get("status"),o.get("status","")),"Subtotal":float(money(o.get("subtotal",o.get("amount",0)))),"Total":float(money(o.get("total_amount",o.get("amount",0)))),"Expected":str(o.get("expected_delivery_date",o.get("expected_delivery","")) or "") } for o in visible]),use_container_width=True,hide_index=True)
        else: st.info("No purchase orders match the selected project and filters.")

        active=[s for s in supplier_rows if s.get("is_active",True)]
        if not active:
            st.info("Add an active supplier before creating a purchase order.")
        else:
            with st.form("purchase_order_add",clear_on_submit=True):
                supplier_labels=[f"{s.get('code','')} | {s.get('name','')}" for s in active]
                supplier_choice=st.selectbox("Supplier",supplier_labels)
                po_number=st.text_input("PO Number")
                po_status=st.selectbox("Status",STATUSES,format_func=lambda x:STATUS_LABELS[x])
                order_date=st.date_input("Order Date",datetime.now().date())
                expected=st.date_input("Expected Delivery Date",None)
                tax_rate=st.number_input("Tax Rate (%)",min_value=0.0,value=0.0,format="%.2f")
                notes=st.text_area("Notes")
                st.markdown("**Order Items**")
                count=st.number_input("Number of items",1,20,1,1)
                boq_options=[("No BOQ link",None)]+[(f"{b.get('item_code','')} | {b.get('description','')}",b.get('id')) for b in boq_rows]
                item_forms=[]
                for i in range(int(count)):
                    a,b=st.columns(2)
                    with a:
                        link=st.selectbox(f"BOQ Item {i+1}",[x[0] for x in boq_options],key=f"po_boq_{i}")
                        description=st.text_input(f"Description {i+1}",key=f"po_desc_{i}")
                        quantity=st.number_input(f"Quantity {i+1}",min_value=0.0,value=1.0,key=f"po_qty_{i}")
                    with b:
                        unit=st.text_input(f"Unit {i+1}",value="No.",key=f"po_unit_{i}")
                        rate=st.number_input(f"Unit Rate {i+1}",min_value=0.0,value=0.0,key=f"po_rate_{i}")
                    item_forms.append((link,description,quantity,unit,rate))
                submit=st.form_submit_button("Create Purchase Order",use_container_width=True)
            if submit:
                try:
                    if not po_number.strip(): raise ValueError("PO Number is required.")
                    supplier=active[supplier_labels.index(supplier_choice)]
                    items=[]
                    for link,description,quantity,unit,rate in item_forms:
                        boq_id=dict(boq_options)[link]
                        if boq_id and not description.strip():
                            boq=next((b for b in boq_rows if str(b.get("id"))==str(boq_id)),{})
                            description=str(boq.get("description", ""))
                            unit=str(boq.get("unit",unit))
                            rate=float(boq.get("rate",rate) or rate)
                        if not description.strip(): raise ValueError("Every purchase order item requires a description.")
                        items.append({"boq_item_id":boq_id,"description":description.strip(),"quantity":quantity,"unit":unit.strip() or "No.","unit_rate":rate})
                    subtotal=sum(money(i["quantity"])*money(i["unit_rate"]) for i in items)
                    tax=(subtotal*money(tax_rate)/Decimal("100")).quantize(Decimal("0.01"))
                    values={"project_id":str(project_id),"supplier_id":str(supplier["id"]),"po_number":po_number.strip(),"status":po_status,"order_date":datetime.combine(order_date,datetime.min.time()),"expected_delivery_date":datetime.combine(expected,datetime.min.time()) if expected else None,"tax_amount":str(tax),"notes":notes.strip()}
                    if database_backend()=="neon": create_relational_purchase_order(values,items)
                    else:
                        next_id=max([int(x.get("id",0)) for x in database.get("procurement",[]) if str(x.get("id","")).isdigit()] or [0])+1
                        database.setdefault("procurement",[]).append({"id":next_id,"project_id":project_id,"po_number":po_number.strip(),"supplier":supplier.get("name",""),"status":po_status,"quantity":sum(float(i["quantity"]) for i in items),"unit_price":float(subtotal),"amount":float(subtotal+tax),"expected_delivery":expected.isoformat() if expected else "","notes":notes.strip(),"created_at":datetime.now().isoformat(timespec="seconds")}); save_memory(database)
                    st.success("Purchase order created."); st.rerun()
                except Exception as exc: st.error(str(exc))
        if order_rows:
            choices=[f"{o.get('po_number','')} | {o.get('supplier_name',o.get('supplier',''))}" for o in order_rows]
            selected_po=st.selectbox("Purchase order actions",choices,key="po_action")
            order=order_rows[choices.index(selected_po)]
            if st.button("Delete Purchase Order",key="delete_po"):
                try:
                    if database_backend()=="neon": delete_relational_purchase_order(str(order["id"]))
                    else: database["procurement"]=[r for r in database.get("procurement",[]) if str(r.get("id"))!=str(order.get("id"))]; save_memory(database)
                    st.success("Purchase order deleted."); st.rerun()
                except Exception as exc: st.error(f"Unable to delete purchase order: {exc}")

    with suppliers_tab:
        if supplier_rows: st.dataframe(pd.DataFrame([{ "Code":s.get("code",""),"Supplier":s.get("name",""),"Category":s.get("category",""),"Contact":s.get("contact_name",""),"Phone":s.get("phone",""),"Active":s.get("is_active",True) } for s in supplier_rows]),use_container_width=True,hide_index=True)
        with st.form("supplier_add",clear_on_submit=True):
            code=st.text_input("Supplier Code"); name=st.text_input("Supplier Name"); contact=st.text_input("Contact Name"); email=st.text_input("Email"); phone=st.text_input("Phone"); address=st.text_input("Address"); tax=st.text_input("Tax Number"); category=st.selectbox("Category",CATEGORIES); notes=st.text_area("Notes"); active=st.checkbox("Active",True); submit_supplier=st.form_submit_button("Add Supplier",use_container_width=True)
        if submit_supplier:
            try:
                if not code.strip() or not name.strip(): raise ValueError("Supplier Code and Supplier Name are required.")
                values={"code":code.strip(),"name":name.strip(),"contact_name":contact.strip(),"email":email.strip(),"phone":phone.strip(),"address":address.strip(),"tax_number":tax.strip(),"category":category,"notes":notes.strip(),"is_active":active}
                if database_backend()=="neon": create_relational_supplier(values)
                else:
                    next_id=max([int(x.get("id",0)) for x in database.get("suppliers",[]) if str(x.get("id","")).isdigit()] or [0])+1; database.setdefault("suppliers",[]).append({"id":next_id,**values}); save_memory(database)
                st.success("Supplier added."); st.rerun()
            except Exception as exc: st.error(str(exc))
        if supplier_rows:
            labels=[f"{s.get('code','')} | {s.get('name','')}" for s in supplier_rows]; choice=st.selectbox("Supplier actions",labels,key="supplier_action"); supplier=supplier_rows[labels.index(choice)]
            with st.form("supplier_edit"):
                name=st.text_input("Name",str(supplier.get("name",""))); category=st.selectbox("Category",CATEGORIES,index=CATEGORIES.index(supplier.get("category")) if supplier.get("category") in CATEGORIES else len(CATEGORIES)-1); active=st.checkbox("Active",bool(supplier.get("is_active",True))); save=st.form_submit_button("Save Supplier")
            if save:
                try:
                    if database_backend()=="neon": update_relational_supplier(str(supplier["id"]),{"name":name.strip(),"category":category,"is_active":active})
                    else: supplier.update({"name":name.strip(),"category":category,"is_active":active}); save_memory(database)
                    st.success("Supplier updated."); st.rerun()
                except Exception as exc: st.error(str(exc))
            if st.button("Delete Supplier",key="delete_supplier"):
                try:
                    if database_backend()=="neon": delete_relational_supplier(str(supplier["id"]))
                    else: database["suppliers"]=[s for s in database.get("suppliers",[]) if str(s.get("id"))!=str(supplier.get("id"))]; save_memory(database)
                    st.success("Supplier deleted."); st.rerun()
                except Exception as exc: st.error(f"Unable to delete supplier: {exc}")
