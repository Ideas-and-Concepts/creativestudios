"""Creative Studios Requests for Information module."""
from __future__ import annotations
from datetime import date
from typing import Any
import streamlit as st
from modules.module_utils import ensure_collection, now_iso, project_records, project_selector, remove_record, save_new_record, save_updated_record

STATUSES=["Open","Under Review","Answered","Closed","Cancelled"]
PRIORITIES=["Low","Medium","High","Critical"]

def _index(options:list[str],value:Any,default:int=0)->int:return options.index(value) if value in options else default

def _options(records:list[dict[str,Any]],label_keys:tuple[str,...])->tuple[list[str],dict[str,str]]:
    labels=["None"]+[" · ".join(str(r.get(k,"")) for k in label_keys if r.get(k)) for r in records]
    return labels,{labels[i+1]:str(r.get("id")) for i,r in enumerate(records)}

def _date(v:Any)->date|None:
    if not v:return None
    try:return date.fromisoformat(str(v)[:10])
    except ValueError:return None

def render_rfis_module(database:dict[str,Any])->None:
    st.title("RFIs");st.caption("Requests for Information, technical queries, responses and close-out.")
    records=ensure_collection(database,"rfis");project_id,projects=project_selector(database,"rfis_project")
    if project_id is None:return
    items=project_records(records,project_id)
    drawings=project_records(ensure_collection(database,"drawings"),project_id);boq=project_records(ensure_collection(database,"boq"),project_id);activities=project_records(ensure_collection(database,"construction"),project_id)
    overdue=sum(bool(r.get("due_date")) and str(r.get("due_date"))[:10]<date.today().isoformat() and r.get("status") not in ("Closed","Cancelled","Answered") for r in items)
    c1,c2,c3,c4,c5=st.columns(5);c1.metric("RFIs",len(items));c2.metric("Open",sum(r.get("status")=="Open" for r in items));c3.metric("Under Review",sum(r.get("status")=="Under Review" for r in items));c4.metric("Answered",sum(r.get("status")=="Answered" for r in items));c5.metric("Overdue",overdue)
    dlabels,dmap=_options(drawings,("drawing_number","title"));blabels,bmap=_options(boq,("item_code","description"));alabels,amap=_options(activities,("activity_code","name"))
    for record in list(items):
        rid=record.get("id")
        with st.expander(f"{record.get('rfi_number','RFI')} | {record.get('subject','Information request')}"):
            with st.form(f"rfi_edit_{rid}"):
                a,b=st.columns(2);number=a.text_input("RFI Number",value=str(record.get("rfi_number","")));subject=b.text_input("Subject",value=str(record.get("subject","")))
                a,b=st.columns(2);raised_by=a.text_input("Raised By",value=str(record.get("raised_by","")));assigned_to=b.text_input("Assigned To",value=str(record.get("assigned_to","")))
                a,b,c=st.columns(3);priority=a.selectbox("Priority",PRIORITIES,index=_index(PRIORITIES,record.get("priority"),1));status=b.selectbox("Status",STATUSES,index=_index(STATUSES,record.get("status")));due=a.date_input("Due Date",value=_date(record.get("due_date")) or date.today())
                drawing_label=next((x for x,i in dmap.items() if i==str(record.get("drawing_id"))),"None");drawing=b.selectbox("Drawing",dlabels,index=_index(dlabels,drawing_label));boq_label=next((x for x,i in bmap.items() if i==str(record.get("boq_item_id"))),"None");boq_item=c.selectbox("BOQ Item",blabels,index=_index(blabels,boq_label))
                activity_label=next((x for x,i in amap.items() if i==str(record.get("construction_activity_id"))),"None");activity=st.selectbox("Construction Activity",alabels,index=_index(alabels,activity_label))
                question=st.text_area("Question",value=str(record.get("question","")));response=st.text_area("Response",value=str(record.get("response","")));notes=st.text_area("Notes",value=str(record.get("notes","")));reference=st.text_input("Reference",value=str(record.get("reference","")))
                submitted=st.form_submit_button("Save Changes",use_container_width=True)
            if submitted:
                if not number.strip() or not subject.strip() or not question.strip():st.error("RFI Number, Subject and Question are required.")
                else:
                    save_updated_record(database,"rfis",rid,{"project_id":project_id,"rfi_number":number.strip(),"subject":subject.strip(),"raised_by":raised_by.strip(),"assigned_to":assigned_to.strip(),"priority":priority,"status":status,"due_date":due.isoformat(),"response_date":now_iso() if response.strip() else None,"drawing_id":dmap.get(drawing),"boq_item_id":bmap.get(boq_item),"construction_activity_id":amap.get(activity),"question":question.strip(),"response":response.strip(),"notes":notes.strip(),"reference":reference.strip(),"updated_at":now_iso()});st.success("RFI updated.");st.rerun()
            if st.button("Delete RFI",key=f"rfi_delete_{rid}",use_container_width=True):
                if remove_record(database,"rfis",rid):st.success("RFI deleted.");st.rerun()
    st.divider();st.subheader("Add RFI")
    with st.form("rfi_add",clear_on_submit=True):
        a,b=st.columns(2);number=a.text_input("RFI Number");subject=b.text_input("Subject");a,b=st.columns(2);raised_by=a.text_input("Raised By");assigned_to=b.text_input("Assigned To");a,b,c=st.columns(3);priority=a.selectbox("Priority",PRIORITIES,index=1);status=b.selectbox("Status",STATUSES);due=c.date_input("Due Date",value=date.today());drawing=a.selectbox("Drawing",dlabels);boq_item=b.selectbox("BOQ Item",blabels);activity=c.selectbox("Construction Activity",alabels);question=st.text_area("Question");response=st.text_area("Response");notes=st.text_area("Notes");reference=st.text_input("Reference");submitted=st.form_submit_button("Add RFI",use_container_width=True)
    if submitted:
        if not number.strip() or not subject.strip() or not question.strip():st.error("RFI Number, Subject and Question are required.")
        else:
            save_new_record(database,"rfis",{"project_id":project_id,"rfi_number":number.strip(),"subject":subject.strip(),"raised_by":raised_by.strip(),"assigned_to":assigned_to.strip(),"priority":priority,"status":status,"due_date":due.isoformat(),"response_date":now_iso() if response.strip() else None,"drawing_id":dmap.get(drawing),"boq_item_id":bmap.get(boq_item),"construction_activity_id":amap.get(activity),"question":question.strip(),"response":response.strip(),"notes":notes.strip(),"reference":reference.strip(),"created_at":now_iso(),"updated_at":now_iso()});st.success("RFI added.");st.rerun()
