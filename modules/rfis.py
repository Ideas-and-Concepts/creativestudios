"""Creative Studios Requests for Information workspace."""
from __future__ import annotations
from datetime import date
from typing import Any
import pandas as pd
import plotly.express as px
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

def _overdue(r:dict[str,Any])->bool:
    return bool(r.get("due_date")) and str(r.get("due_date"))[:10] < date.today().isoformat() and r.get("status") not in ("Closed","Cancelled","Answered")

def render_rfis_module(database:dict[str,Any])->None:
    st.title("Requests for Information")
    st.caption("Technical queries, responses, ownership, due dates and close-out across the project delivery workflow.")
    records=ensure_collection(database,"rfis"); project_id,projects=project_selector(database,"rfis_project")
    if project_id is None:return
    items=project_records(records,project_id)
    drawings=project_records(ensure_collection(database,"drawings"),project_id)
    boq=project_records(ensure_collection(database,"boq"),project_id)
    activities=project_records(ensure_collection(database,"construction"),project_id)

    overdue=sum(_overdue(r) for r in items); open_count=sum(r.get("status")=="Open" for r in items); review_count=sum(r.get("status")=="Under Review" for r in items); answered_count=sum(r.get("status")=="Answered" for r in items)
    st.markdown("### RFI control center")
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("Total RFIs",len(items),help="All RFI records for the selected project")
    c2.metric("Open",open_count,help="Awaiting technical action or response")
    c3.metric("Under Review",review_count)
    c4.metric("Answered",answered_count)
    c5.metric("Overdue",overdue,delta="Action required" if overdue else "On track",delta_color="inverse" if overdue else "normal")

    left,right=st.columns([1.35,1])
    with left:
        st.markdown("#### Workflow distribution")
        status_df=pd.DataFrame({"Status":STATUSES,"RFIs":[sum(r.get("status")==s for r in items) for s in STATUSES]})
        fig=px.bar(status_df,x="RFIs",y="Status",orientation="h",text="RFIs")
        fig.update_layout(height=260,margin=dict(l=0,r=10,t=10,b=10),showlegend=False,xaxis_title=None,yaxis_title=None)
        st.plotly_chart(fig,use_container_width=True)
    with right:
        st.markdown("#### Priority mix")
        priority_df=pd.DataFrame({"Priority":PRIORITIES,"RFIs":[sum((r.get("priority") or "Medium")==p for r in items) for p in PRIORITIES]})
        fig=px.pie(priority_df,names="Priority",values="RFIs",hole=.58)
        fig.update_layout(height=260,margin=dict(l=0,r=0,t=5,b=5),showlegend=True)
        st.plotly_chart(fig,use_container_width=True)

    st.markdown("#### Attention queue")
    attention=[r for r in items if _overdue(r)]
    if attention:
        st.dataframe(pd.DataFrame([{"RFI":r.get("rfi_number"),"Subject":r.get("subject"),"Priority":r.get("priority") or "Medium","Status":r.get("status"),"Due":str(r.get("due_date"))[:10],"Assigned To":r.get("assigned_to") or "Unassigned"} for r in attention]),use_container_width=True,hide_index=True)
    else: st.success("No overdue RFIs for the selected project.")

    dlabels,dmap=_options(drawings,("drawing_number","title")); blabels,bmap=_options(boq,("item_code","description")); alabels,amap=_options(activities,("activity_code","name"))
    st.markdown("#### RFI register")
    search=st.text_input("Search RFIs",placeholder="Number, subject, person, reference...")
    f1,f2=st.columns(2); status_filter=f1.multiselect("Status",STATUSES); priority_filter=f2.multiselect("Priority",PRIORITIES)
    visible=[r for r in items if (not status_filter or r.get("status") in status_filter) and (not priority_filter or (r.get("priority") or "Medium") in priority_filter) and (not search.strip() or any(search.lower() in str(v or "").lower() for v in r.values()))]
    st.caption(f"Showing {len(visible)} of {len(items)} RFIs")
    for record in visible:
        rid=record.get("id")
        label=f"{record.get('rfi_number','RFI')} · {record.get('subject','Information request')} · {record.get('status','Open')}"
        with st.expander(label):
            st.markdown(f"**Question**\n\n{record.get('question') or 'No question recorded.'}")
            if record.get("response"): st.info(f"Response: {record.get('response')}")
            with st.form(f"rfi_edit_{rid}"):
                a,b=st.columns(2);number=a.text_input("RFI Number",value=str(record.get("rfi_number","")));subject=b.text_input("Subject",value=str(record.get("subject","")))
                a,b=st.columns(2);raised_by=a.text_input("Raised By",value=str(record.get("raised_by","")));assigned_to=b.text_input("Assigned To",value=str(record.get("assigned_to","")))
                a,b,c=st.columns(3);priority=a.selectbox("Priority",PRIORITIES,index=_index(PRIORITIES,record.get("priority"),1));status=b.selectbox("Status",STATUSES,index=_index(STATUSES,record.get("status")));due=c.date_input("Due Date",value=_date(record.get("due_date")) or date.today())
                drawing_label=next((x for x,i in dmap.items() if i==str(record.get("drawing_id"))),"None");drawing=a.selectbox("Drawing",dlabels,index=_index(dlabels,drawing_label));boq_label=next((x for x,i in bmap.items() if i==str(record.get("boq_item_id"))),"None");boq_item=b.selectbox("BOQ Item",blabels,index=_index(blabels,boq_label));activity_label=next((x for x,i in amap.items() if i==str(record.get("construction_activity_id"))),"None");activity=c.selectbox("Construction Activity",alabels,index=_index(alabels,activity_label))
                question=st.text_area("Question",value=str(record.get("question","")));response=st.text_area("Response",value=str(record.get("response","")));notes=st.text_area("Notes",value=str(record.get("notes","")));reference=st.text_input("Reference",value=str(record.get("reference","")))
                submitted=st.form_submit_button("Save Changes",use_container_width=True)
            if submitted:
                if not number.strip() or not subject.strip() or not question.strip():st.error("RFI Number, Subject and Question are required.")
                else:
                    save_updated_record(database,"rfis",rid,{"project_id":project_id,"rfi_number":number.strip(),"subject":subject.strip(),"raised_by":raised_by.strip(),"assigned_to":assigned_to.strip(),"priority":priority,"status":status,"due_date":due.isoformat(),"response_date":now_iso() if response.strip() else None,"drawing_id":dmap.get(drawing),"boq_item_id":bmap.get(boq_item),"construction_activity_id":amap.get(activity),"question":question.strip(),"response":response.strip(),"notes":notes.strip(),"reference":reference.strip(),"updated_at":now_iso()});st.success("RFI updated.");st.rerun()
            if st.button("Delete RFI",key=f"rfi_delete_{rid}",use_container_width=True):
                if remove_record(database,"rfis",rid):st.success("RFI deleted.");st.rerun()

    st.markdown("#### Add RFI")
    with st.form("rfi_add",clear_on_submit=True):
        a,b=st.columns(2);number=a.text_input("RFI Number");subject=b.text_input("Subject");a,b=st.columns(2);raised_by=a.text_input("Raised By");assigned_to=b.text_input("Assigned To");a,b,c=st.columns(3);priority=a.selectbox("Priority",PRIORITIES,index=1);status=b.selectbox("Status",STATUSES);due=c.date_input("Due Date",value=date.today());drawing=a.selectbox("Drawing",dlabels);boq_item=b.selectbox("BOQ Item",blabels);activity=c.selectbox("Construction Activity",alabels);question=st.text_area("Question");response=st.text_area("Response");notes=st.text_area("Notes");reference=st.text_input("Reference");submitted=st.form_submit_button("Add RFI",use_container_width=True)
    if submitted:
        if not number.strip() or not subject.strip() or not question.strip():st.error("RFI Number, Subject and Question are required.")
        else:
            save_new_record(database,"rfis",{"project_id":project_id,"rfi_number":number.strip(),"subject":subject.strip(),"raised_by":raised_by.strip(),"assigned_to":assigned_to.strip(),"priority":priority,"status":status,"due_date":due.isoformat(),"response_date":now_iso() if response.strip() else None,"drawing_id":dmap.get(drawing),"boq_item_id":bmap.get(boq_item),"construction_activity_id":amap.get(activity),"question":question.strip(),"response":response.strip(),"notes":notes.strip(),"reference":reference.strip(),"created_at":now_iso(),"updated_at":now_iso()});st.success("RFI added.");st.rerun()
