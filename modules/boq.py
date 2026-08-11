"""
Creative Studios
Bill of Quantities (BOQ) Module

Manages project BOQs, sections, items, quantities,
rates, amounts and approval status.

Structure:

Project
   └── BOQ
        ├── Section
        │    ├── Item
        │    ├── Item
        │    └── Item
        └── Section
             └── Item

Amount = Quantity × Rate
"""

from datetime import date

import streamlit as st

from .database import (
    add_record,
    delete_record,
    get_collection,
    update_record,
)


BOQ_STATUSES = [
    "Draft",
    "For Review",
    "For Approval",
    "Approved",
    "Issued",
    "Superseded",
]

UNITS = [
    "No.",
    "m",
    "m²",
    "m³",
    "kg",
    "ton",
    "mm",
    "cm",
    "L",
    "Set",
    "Lot",
    "Item",
    "Hour",
    "Day",
]


# ============================================================
# DATABASE HELPERS
# ============================================================

def _get_projects(db):
    return get_collection(db, "projects")


def _get_boqs(db):
    return get_collection(db, "boqs")


def _get_boq_items(db):
    return get_collection(db, "boq_items")


def _project_name(db, project_id):

    for project in _get_projects(db):

        if str(project.get("id")) == str(project_id):

            return project.get(
                "name",
                project_id,
            )

    return project_id


def _current_user():

    user = st.session_state.get("user")

    if isinstance(user, dict):

        return user.get(
            "username",
            "System",
        )

    return str(
        user or "System"
    )


def _money(value):

    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return "0.00"


def _next_boq_number(db, project_id):

    count = 0

    for boq in _get_boqs(db):

        if str(
            boq.get("project_id")
        ) == str(project_id):

            count += 1

    return f"BOQ-{project_id}-{count + 1:03d}"


def _next_item_number(db, boq_id):

    count = 0

    for item in _get_boq_items(db):

        if str(
            item.get("boq_id")
        ) == str(boq_id):

            count += 1

    return f"{count + 1:03d}"


def _boq_items(db, boq_id):

    return [
        item
        for item in _get_boq_items(db)
        if str(
            item.get("boq_id")
        ) == str(boq_id)
    ]


def _boq_total(db, boq_id):

    total = 0.0

    for item in _boq_items(
        db,
        boq_id,
    ):

        try:

            quantity = float(
                item.get(
                    "quantity",
                    0,
                )
            )

            rate = float(
                item.get(
                    "rate",
                    0,
                )
            )

            total += quantity * rate

        except (
            TypeError,
            ValueError,
        ):

            continue

    return total


def _section_total(
    db,
    boq_id,
    section,
):

    total = 0.0

    for item in _boq_items(
        db,
        boq_id,
    ):

        if item.get(
            "section"
        ) != section:

            continue

        try:

            total += (
                float(
                    item.get(
                        "quantity",
                        0,
                    )
                )
                *
                float(
                    item.get(
                        "rate",
                        0,
                    )
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            pass

    return total


def _boq_sections(
    db,
    boq_id,
):

    sections = []

    for item in _boq_items(
        db,
        boq_id,
    ):

        section = item.get(
            "section",
            "General",
        )

        if section not in sections:

            sections.append(
                section
            )

    return sections


# ============================================================
# CREATE BOQ
# ============================================================

def _render_create_boq(db):

    projects = _get_projects(db)

    st.subheader(
        "Create BOQ"
    )

    if not projects:

        st.warning(
            "Create a project before creating a BOQ."
        )

        return

    project_options = {
        _project_name(
            db,
            project.get("id"),
        ):
            project.get("id")
        for project in projects
    }

    with st.form(
        "create_boq_form"
    ):

        project_label = st.selectbox(
            "Project *",
            list(
                project_options.keys()
            ),
        )

        project_id = project_options[
            project_label
        ]

        col1, col2 = st.columns(2)

        with col1:

            title = st.text_input(
                "BOQ Title *",
                placeholder=(
                    "Main Construction BOQ"
                ),
            )

            reference = st.text_input(
                "Reference",
                placeholder=(
                    "e.g. NMF/BOQ/001"
                ),
            )

        with col2:

            status = st.selectbox(
                "Status",
                BOQ_STATUSES,
            )

            prepared_by = st.text_input(
                "Prepared By",
                value=_current_user(),
            )

        description = st.text_area(
            "Description",
            height=100,
        )

        submitted = st.form_submit_button(
            "Create BOQ",
            use_container_width=True,
        )

    if not submitted:

        return

    title = title.strip()

    if not title:

        st.error(
            "BOQ title is required."
        )

        return

    boq_number = _next_boq_number(
        db,
        project_id,
    )

    boq = {

        "id": boq_number,

        "project_id": project_id,

        "boq_number": boq_number,

        "title": title,

        "reference": reference.strip(),

        "description": description.strip(),

        "status": status,

        "prepared_by": prepared_by.strip(),

        "created_by": _current_user(),

        "created_at": str(
            date.today()
        ),

        "approved_by": "",

        "approved_date": "",

    }

    add_record(
        db,
        "boqs",
        boq,
    )

    st.success(
        f"{boq_number} created successfully."
    )

    st.rerun()


# ============================================================
# CREATE BOQ ITEM
# ============================================================

def _render_create_item(
    db,
    boq,
):

    boq_id = boq.get(
        "id"
    )

    st.subheader(
        f"Add BOQ Item — "
        f"{boq.get('boq_number', '')}"
    )

    with st.form(
        f"create_item_{boq_id}"
    ):

        col1, col2 = st.columns(2)

        with col1:

            section = st.text_input(
                "Section *",
                placeholder=(
                    "A. Preliminaries"
                ),
            )

            description = st.text_area(
                "Item Description *",
                placeholder=(
                    "Provide and install..."
                ),
                height=100,
            )

        with col2:

            unit = st.selectbox(
                "Unit",
                UNITS,
            )

            quantity = st.number_input(
                "Quantity",
                min_value=0.0,
                value=1.0,
                step=0.01,
            )

            rate = st.number_input(
                "Rate",
                min_value=0.0,
                value=0.0,
                step=100.0,
            )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Calculated Amount",
                _money(
                    quantity * rate
                ),
            )

        with col2:

            item_code = st.text_input(
                "Item Code",
                placeholder=(
                    "e.g. PRE-001"
                ),
            )

        with col3:

            notes = st.text_input(
                "Notes",
            )

        submitted = st.form_submit_button(
            "Add Item",
            use_container_width=True,
        )

    if not submitted:

        return

    section = section.strip()

    description = description.strip()

    if not section:

        st.error(
            "Section is required."
        )

        return

    if not description:

        st.error(
            "Item description is required."
        )

        return

    item_number = _next_item_number(
        db,
        boq_id,
    )

    item_id = (
        f"{boq_id}-ITEM-{item_number}"
    )

    item = {

        "id": item_id,

        "boq_id": boq_id,

        "item_number": item_number,

        "item_code": item_code.strip(),

        "section": section,

        "description": description,

        "unit": unit,

        "quantity": float(
            quantity
        ),

        "rate": float(
            rate
        ),

        "amount": float(
            quantity * rate
        ),

        "notes": notes.strip(),

        "created_at": str(
            date.today()
        ),

        "created_by": _current_user(),

    }

    add_record(
        db,
        "boq_items",
        item,
    )

    st.success(
        f"Item {item_number} added."
    )

    st.rerun()


# ============================================================
# EDIT ITEM
# ============================================================

def _render_edit_item(
    db,
    item,
):

    st.subheader(
        f"Edit Item "
        f"{item.get('item_number', '')}"
    )

    with st.form(
        f"edit_item_{item.get('id')}"
    ):

        section = st.text_input(
            "Section",
            value=item.get(
                "section",
                "",
            ),
        )

        description = st.text_area(
            "Description",
            value=item.get(
                "description",
                "",
            ),
            height=100,
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            current_unit = item.get(
                "unit",
                UNITS[0],
            )

            unit = st.selectbox(
                "Unit",
                UNITS,
                index=(
                    UNITS.index(
                        current_unit
                    )
                    if current_unit in UNITS
                    else 0
                ),
            )

        with col2:

            quantity = st.number_input(
                "Quantity",
                min_value=0.0,
                value=float(
                    item.get(
                        "quantity",
                        0,
                    )
                ),
                step=0.01,
            )

        with col3:

            rate = st.number_input(
                "Rate",
                min_value=0.0,
                value=float(
                    item.get(
                        "rate",
                        0,
                    )
                ),
                step=100.0,
            )

        item_code = st.text_input(
            "Item Code",
            value=item.get(
                "item_code",
                "",
            ),
        )

        notes = st.text_area(
            "Notes",
            value=item.get(
                "notes",
                "",
            ),
            height=80,
        )

        save = st.form_submit_button(
            "Save Changes",
            use_container_width=True,
        )

    if not save:

        return

    section = section.strip()

    description = description.strip()

    if not section or not description:

        st.error(
            "Section and description are required."
        )

        return

    updates = {

        "section": section,

        "description": description,

        "unit": unit,

        "quantity": float(
            quantity
        ),

        "rate": float(
            rate
        ),

        "amount": float(
            quantity * rate
        ),

        "item_code": item_code.strip(),

        "notes": notes.strip(),

        "updated_at": str(
            date.today()
        ),

        "updated_by": _current_user(),

    }

    update_record(
        db,
        "boq_items",
        item.get("id"),
        updates,
    )

    st.session_state.pop(
        "edit_boq_item",
        None,
    )

    st.success(
        "BOQ item updated."
    )

    st.rerun()


# ============================================================
# DELETE ITEM
# ============================================================

def _render_delete_item(
    db,
    item,
):

    st.warning(
        f"Delete BOQ item "
        f"**{item.get('item_number', '')}**?"
    )

    st.write(
        item.get(
            "description",
            "",
        )
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Delete Item",
            type="primary",
            use_container_width=True,
        ):

            delete_record(
                db,
                "boq_items",
                item.get("id"),
            )

            st.session_state.pop(
                "delete_boq_item",
                None,
            )

            st.success(
                "BOQ item deleted."
            )

            st.rerun()

    with col2:

        if st.button(
            "Cancel",
            use_container_width=True,
        ):

            st.session_state.pop(
                "delete_boq_item",
                None,
            )

            st.rerun()


# ============================================================
# BOQ CARD
# ============================================================

def _render_boq_card(
    db,
    boq,
):

    boq_id = boq.get(
        "id"
    )

    total = _boq_total(
        db,
        boq_id,
    )

    items = _boq_items(
        db,
        boq_id,
    )

    with st.container(
        border=True
    ):

        col1, col2 = st.columns(
            [4, 1]
        )

        with col1:

            st.markdown(
                f"### "
                f"{boq.get('boq_number', '')} "
                f"— "
                f"{boq.get('title', '')}"
            )

            st.caption(
                f"{_project_name(db, boq.get('project_id'))}"
            )

        with col2:

            status = boq.get(
                "status",
                "Draft",
            )

            if status == "Approved":

                st.success(
                    status
                )

            elif status == "For Approval":

                st.warning(
                    status
                )

            elif status == "For Review":

                st.info(
                    status
                )

            else:

                st.caption(
                    status
                )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Items",
                len(items),
            )

        with col2:

            st.metric(
                "Sections",
                len(
                    _boq_sections(
                        db,
                        boq_id,
                    )
                ),
            )

        with col3:

            st.metric(
                "BOQ Total",
                _money(total),
            )

        with st.expander(
            "BOQ Details"
        ):

            if boq.get(
                "reference"
            ):

                st.markdown(
                    f"**Reference:** "
                    f"{boq.get('reference')}"
                )

            if boq.get(
                "description"
            ):

                st.markdown(
                    f"**Description:** "
                    f"{boq.get('description')}"
                )

            st.markdown(
                f"**Prepared By:** "
                f"{boq.get('prepared_by', '')}"
            )

            st.markdown(
                f"**Created:** "
                f"{boq.get('created_at', '')}"
            )

        open_col, add_col = st.columns(2)

        with open_col:

            if st.button(
                "Open BOQ",
                key=f"open_boq_{boq_id}",
                use_container_width=True,
            ):

                st.session_state[
                    "open_boq_id"
                ] = boq_id

                st.rerun()

        with add_col:

            if st.button(
                "Add Item",
                key=f"quick_add_{boq_id}",
                use_container_width=True,
            ):

                st.session_state[
                    "open_boq_id"
                ] = boq_id

                st.session_state[
                    "add_boq_item"
                ] = True

                st.rerun()


# ============================================================
# OPEN BOQ
# ============================================================

def _render_open_boq(
    db,
    boq,
):

    boq_id = boq.get(
        "id"
    )

    st.subheader(
        f"{boq.get('boq_number', '')} "
        f"— "
        f"{boq.get('title', '')}"
    )

    st.caption(
        _project_name(
            db,
            boq.get("project_id"),
        )
    )

    total = _boq_total(
        db,
        boq_id,
    )

    items = _boq_items(
        db,
        boq_id,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Items",
            len(items),
        )

    with col2:

        st.metric(
            "Sections",
            len(
                _boq_sections(
                    db,
                    boq_id,
                )
            ),
        )

    with col3:

        st.metric(
            "BOQ Total",
            _money(total),
        )

    with col4:

        st.metric(
            "Status",
            boq.get(
                "status",
                "Draft",
            ),
        )

    st.divider()

    # --------------------------------------------------------
    # ADD ITEM
    # --------------------------------------------------------

    add_item = st.session_state.get(
        "add_boq_item",
        False,
    )

    if add_item:

        _render_create_item(
            db,
            boq,
        )

        st.divider()

    # --------------------------------------------------------
    # ITEM EDIT
    # --------------------------------------------------------

    edit_id = st.session_state.get(
        "edit_boq_item"
    )

    if edit_id:

        edit_item = next(
            (
                item
                for item in items
                if str(item.get("id"))
                == str(edit_id)
            ),
            None,
        )

        if edit_item:

            _render_edit_item(
                db,
                edit_item,
            )

            st.divider()

    # --------------------------------------------------------
    # ITEM DELETE
    # --------------------------------------------------------

    delete_id = st.session_state.get(
        "delete_boq_item"
    )

    if delete_id:

        delete_item = next(
            (
                item
                for item in items
                if str(item.get("id"))
                == str(delete_id)
            ),
            None,
        )

        if delete_item:

            _render_delete_item(
                db,
                delete_item,
            )

            st.divider()

    # --------------------------------------------------------
    # BOQ SECTIONS
    # --------------------------------------------------------

    sections = _boq_sections(
        db,
        boq_id,
    )

    if not sections:

        st.info(
            "No BOQ items have been added yet."
        )

    else:

        for section in sections:

            section_items = [
                item
                for item in items
                if item.get(
                    "section"
                ) == section
            ]

            section_total = _section_total(
                db,
                boq_id,
                section,
            )

            st.markdown(
                f"### {section}"
            )

            st.caption(
                f"{len(section_items)} items "
                f"• Section Total: "
                f"{_money(section_total)}"
            )

            for item in section_items:

                quantity = float(
                    item.get(
                        "quantity",
                        0,
                    )
                )

                rate = float(
                    item.get(
                        "rate",
                        0,
                    )
                )

                amount = quantity * rate

                with st.container(
                    border=True
                ):

                    col1, col2, col3, col4, col5 = st.columns(
                        [0.7, 3.5, 0.8, 1.2, 1.5]
                    )

                    with col1:

                        st.write(
                            item.get(
                                "item_number",
                                "",
                            )
                        )

                    with col2:

                        st.markdown(
                            f"**"
                            f"{item.get('description', '')}"
                            f"**"
                        )

                        if item.get(
                            "item_code"
                        ):

                            st.caption(
                                f"Code: "
                                f"{item.get('item_code')}"
                            )

                    with col3:

                        st.write(
                            f"{quantity:g} "
                            f"{item.get('unit', '')}"
                        )

                    with col4:

                        st.write(
                            _money(rate)
                        )

                    with col5:

                        st.write(
                            _money(amount)
                        )

                    action_col1, action_col2, action_col3 = st.columns(
                        [1, 1, 4]
                    )

                    with action_col1:

                        if st.button(
                            "Edit",
                            key=f"edit_{item.get('id')}",
                            use_container_width=True,
                        ):

                            st.session_state[
                                "edit_boq_item"
                            ] = item.get(
                                "id"
                            )

                            st.rerun()

                    with action_col2:

                        if st.button(
                            "Delete",
                            key=f"delete_{item.get('id')}",
                            use_container_width=True,
                        ):

                            st.session_state[
                                "delete_boq_item"
                            ] = item.get(
                                "id"
                            )

                            st.rerun()

            st.divider()

    # --------------------------------------------------------
    # TOTAL
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div style="
            text-align:right;
            font-size:24px;
            font-weight:700;
            padding:15px;
        ">
            BOQ TOTAL: {_money(total)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "← Back to BOQ Register",
        use_container_width=True,
    ):

        st.session_state.pop(
            "open_boq_id",
            None,
        )

        st.session_state.pop(
            "add_boq_item",
            None,
        )

        st.session_state.pop(
            "edit_boq_item",
            None,
        )

        st.session_state.pop(
            "delete_boq_item",
            None,
        )

        st.rerun()


# ============================================================
# MAIN MODULE
# ============================================================

def render_boq_module(db):

    boqs = _get_boqs(db)

    st.markdown(
        """
        <div class="module-header">
            <div class="module-title">
                Bill of Quantities
            </div>
            <div class="module-subtitle">
                Project quantities, rates, costs and
                BOQ control.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
    # KPI
    # ========================================================

    total_boqs = len(boqs)

    draft = sum(
        1
        for boq in boqs
        if boq.get("status")
        == "Draft"
    )

    review = sum(
        1
        for boq in boqs
        if boq.get("status")
        == "For Review"
    )

    approved = sum(
        1
        for boq in boqs
        if boq.get("status")
        == "Approved"
    )

    portfolio_value = sum(
        _boq_total(
            db,
            boq.get("id"),
        )
        for boq in boqs
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "Total BOQs",
            total_boqs,
        )

    with col2:

        st.metric(
            "Draft",
            draft,
        )

    with col3:

        st.metric(
            "For Review",
            review,
        )

    with col4:

        st.metric(
            "Approved",
            approved,
        )

    with col5:

        st.metric(
            "Portfolio Value",
            _money(
                portfolio_value
            ),
        )

    st.divider()

    # ========================================================
    # OPEN BOQ
    # ========================================================

    open_id = st.session_state.get(
        "open_boq_id"
    )

    if open_id:

        boq = next(
            (
                item
                for item in boqs
                if str(item.get("id"))
                == str(open_id)
            ),
            None,
        )

        if boq:

            _render_open_boq(
                db,
                boq,
            )

            return

    # ========================================================
    # TABS
    # ========================================================

    tab_register, tab_create = st.tabs(
        [
            "BOQ Register",
            "Create BOQ",
        ]
    )

    # ========================================================
    # REGISTER
    # ========================================================

    with tab_register:

        if not boqs:

            st.info(
                "No BOQs have been created yet."
            )

        else:

            search = st.text_input(
                "Search BOQs",
                placeholder=(
                    "BOQ number, title, reference "
                    "or project..."
                ),
            )

            status_filter = st.selectbox(
                "Status",
                ["All"]
                + BOQ_STATUSES,
            )

            search_term = (
                search.strip().lower()
            )

            filtered = []

            for boq in boqs:

                searchable = " ".join(
                    [
                        str(
                            boq.get(
                                "id",
                                "",
                            )
                        ),
                        str(
                            boq.get(
                                "boq_number",
                                "",
                            )
                        ),
                        str(
                            boq.get(
                                "title",
                                "",
                            )
                        ),
                        str(
                            boq.get(
                                "reference",
                                "",
                            )
                        ),
                        str(
                            boq.get(
                                "project_id",
                                "",
                            )
                        ),
                        _project_name(
                            db,
                            boq.get(
                                "project_id",
                                "",
                            ),
                        ),
                    ]
                ).lower()

                if (
                    search_term
                    and search_term
                    not in searchable
                ):

                    continue

                if (
                    status_filter != "All"
                    and boq.get(
                        "status"
                    )
                    != status_filter
                ):

                    continue

                filtered.append(
                    boq
                )

            st.caption(
                f"Showing {len(filtered)} "
                f"of {len(boqs)} BOQs"
            )

            for boq in filtered:

                _render_boq_card(
                    db,
                    boq,
                )

    # ========================================================
    # CREATE
    # ========================================================

    with tab_create:

        _render_create_boq(
            db
        )