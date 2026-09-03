"""Creative Studios Approvals module."""
from __future__ import annotations
from datetime import date
from typing import Any
import streamlit as st
from modules.module_utils import ensure_collection, now_iso, project_records, project_selector, remove_record, save_new_record, save_updated_record

STATUSES=["Pending","In Review","Approved","Rejected","Returned","Cancelled"]
TYPES=["Drawing","Document","BOQ","RFI Response","Material","Method Statement","Design Decision","Other"]

def _index(options:list[str],value:Any)->int:return options.index(value) if value in options else 0
def _date(v:Any)->date|None:
    if not v:return None
    try:return date.fromisoformat(str(v)[:10])
    except ValueError:return None
def _options(records:list[dict[str,Any]],keys:tuple[str,...]):
    labels=["None"]+[" · ".join(str(r.get(k,"")) for k in keys if r.get(k)) for r in records]
    return labels,{labels[i+1]:str(r.get("id")) for i,r in enumerate(records)}

def render_approvals_module(database:dict[str,Any])->None:
    st.title("Approvals");st.caption("Controlled review and approval of project deliverables and decisions.")
    records=ensure_collection(database,"approvals");project_id,projects=project_selector(database,"approvals_project")
    if project_id is None:return
    items=project_records(records,project_id);docs=project_records(ensure_collection(database,"documents"),project_id);drawings=project_records(ensure_collection(database,"drawings"),project_id);rfis=project_records(ensure_collection(database,"rfis"),project_id)
    overdue=sum(bool(r.get("due_date")) and str(r.get("due_date"))[:10]<date.today().isoformat() and r.get("status") not in ("Approved","Rejected","Cancelled") for r in items)
    c1,c2,c3,c4,c5=st.columns(5);c1.metric("Requests",len(items));c2.metric("Pending",sum(r.get("status")=="Pending" for r in items));c3.metric("In Review",sum(r.get("status")=="In Review" for r in items));c4.metric("Approved",sum(r.get("status")=="Approved" for r in items));c5.metric("Overdue",overdue)
    dlabels,dmap=_options(docs,("title",));drlabels,drmap=_options(drawings,("drawing_number","title"));rlabels,rmap=_options(rfis,("rfi_number","subject"))
    for record in list(items):
        rid=record.get("id")
        with st.expander(f"{record.get('approval_number','Approval')} | {record.get('subject','Approval request')}"):
            with st.form(f"approval_edit_{rid}"):
                a,b=st.columns(2);number=a.text_input("Approval Number",value=str(record.get("approval_number","")));subject=b.text_input("Subject",value=str(record.get("subject",record.get("title",""))))
                a,b=st.columns(2);requested=a.text_input("Requested By",value=str(record.get("requested_by","")));reviewer=b.text_input("Reviewer / Approver",value=str(record.get("reviewer",record.get("approver",""))))
                a,b,c=st.columns(3);approval_type=a.selectbox("Approval Type",TYPES,index=_index(TYPES,record.get("approval_type")));status=b.selectbox("Status",STATUSES,index=_index(STATUSES,record.get("status")));due=c.date_input("Due Date",value=_date(record.get("due_date")) or date.today())
                dl=next((x for x,i in dmap.items() if i==str(record.get("document_id"))),"None");document=a.selectbox("Document",dlabels,index=_index(dlabels,dl));drl=next((x for x,i in drmap.items() if i==str(record.get("drawing_id"))),"None");drawing=b.selectbox("Drawing",drlabels,index=_index(drlabels,drl));rl=next((x for x,i in rmap.items() if i==str(record.get("rfi_id"))),"None");rfi=c.selectbox("RFI",rlabels,index=_index(rlabels,rl));comments=st.text_area("Comments / Decision",value=str(record.get("comments","")));submitted=st.form_submit_button("Save Changes",use_container_width=True)
            if submitted:
                if not number.strip() or not subject.strip():st.error("Approval Number and Subject are required.")
                else:
                    save_updated_record(database,"approvals",rid,{"project_id":project_id,"approval_number":number.strip(),"subject":subject.strip(),"requested_by":requested.strip(),"reviewer":reviewer.strip(),"approval_type":approval_type,"status":status,"due_date":due.isoformat(),"submitted_at":record.get("submitted_at") or now_iso(),"decided_at":now_iso() if status in ("Approved","Rejected") else None,"document_id":dmap.get(document),"drawing_id":drmap.get(drawing),"rfi_id":rmap.get(rfi),"comments":comments.strip(),"updated_at":now_iso()});st.success("Approval updated.");st.rerun()
            if st.button("Delete Approval",key=f"approval_delete_{rid}",use_container_width=True):
                if remove_record(database,"approvals",rid):st.success("Approval deleted.");st.rerun()
    st.divider();st.subheader("Add Approval")
    with st.form("approval_add",clear_on_submit=True):
        a,b=st.columns(2);number=a.text_input("Approval Number");subject=b.text_input("Subject");a,b=st.columns(2);requested=a.text_input("Requested By");reviewer=b.text_input("Reviewer / Approver");a,b,c=st.columns(3);approval_type=a.selectbox("Approval Type",TYPES);status=b.selectbox("Status",STATUSES);due=c.date_input("Due Date",value=date.today());document=a.selectbox("Document",dlabels);drawing=b.selectbox("Drawing",drlabels);rfi=c.selectbox("RFI",rlabels);comments=st.text_area("Comments / Decision");submitted=st.form_submit_button("Add Approval",use_container_width=True)
    if submitted:
        if not number.strip() or not subject.strip():st.error("Approval Number and Subject are required.")
        else:
            save_new_record(database,"approvals",{"project_id":project_id,"approval_number":number.strip(),"subject":subject.strip(),"requested_by":requested.strip(),"reviewer":reviewer.strip(),"approval_type":approval_type,"status":status,"due_date":due.isoformat(),"submitted_at":now_iso(),"decided_at":now_iso() if status in ("Approved","Rejected") else None,"document_id":dmap.get(document),"drawing_id":drmap.get(drawing),"rfi_id":rmap.get(rfi),"comments":comments.strip(),"created_at":now_iso(),"updated_at":now_iso()});st.success("Approval added.");st.rerun()
