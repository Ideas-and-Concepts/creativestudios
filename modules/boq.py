"""
Creative Studios
Bill of Quantities Module

Construction-oriented BOQ management.

Features:
- Structural elements
- Architectural elements
- Civil/external works
- MEP works
- Preliminaries
- Editable BOQ records
- Add, edit and delete
- Category and element filtering
- Automatic amount calculation
- BOQ summary and totals
- JSON persistence through modules.database
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from modules.database import save_memory


# ============================================================
# CONSTANTS
# ============================================================

CATEGORIES = [
    "Preliminaries",
    "Substructure",
    "Structural",
    "Walls",
    "Openings",
    "Roofing",
    "Architectural Finishes",
    "Civil Works",
    "Electrical",
    "Mechanical",
    "Plumbing",
    "External Works",
    "Other",
]


ELEMENTS_BY_CATEGORY: dict[str, list[str]] = {
    "Preliminaries": [
        "Site Establishment",
        "Mobilisation",
        "Demobilisation",
        "Setting Out",
        "Temporary Works",
        "Health and Safety",
        "Site Supervision",
        "Other",
    ],
    "Substructure": [
        "Excavation",
        "Backfilling",
        "Blinding Concrete",
        "Pad Foundation",
        "Strip Foundation",
        "Raft Foundation",
        "Ground Beam",
        "Foundation Wall",
        "Damp Proof Membrane",
        "Other",
    ],
    "Structural": [
        "Column",
        "Beam",
        "Slab",
        "Structural Wall",
        "Staircase",
        "Lintel",
        "Reinforcement",
        "Formwork",
        "Structural Concrete",
        "Other",
    ],
    "Walls": [
        "External Wall",
        "Internal Wall",
        "Block Wall",
        "Brick Wall",
        "Partition Wall",
        "Retaining Wall",
        "Parapet Wall",
        "Other",
    ],
    "Openings": [
        "Door",
        "Window",
        "Louver",
        "Glazed Screen",
        "Roller Shutter",
        "Fire Door",
        "Other",
    ],
    "Roofing": [
        "Roof Structure",
        "Roof Covering",
        "Roof Truss",
        "Roof Sheet",
        "Roof Tile",
        "Gutter",
        "Downpipe",
        "Roof Insulation",
        "Other",
    ],
    "Architectural Finishes": [
        "Plaster",
        "Rendering",
        "Screed",
        "Floor Tiling",
        "Wall Tiling",
        "Ceiling",
        "Painting",
        "Floor Finish",
        "Skirting",
        "Cladding",
        "Other",
    ],
    "Civil Works": [
        "Road Works",
        "Drainage",
        "Kerbs",
        "Pavement",
        "Concrete Works",
        "Earthworks",
        "Stormwater Drain",
        "Manhole",
        "Other",
    ],
    "Electrical": [
        "Lighting Point",
        "Socket Outlet",
        "Switch",
        "Distribution Board",
        "Cable",
        "Conduit",
        "Electrical Panel",
        "Earthing",
        "Generator Connection",
        "Other",
    ],
    "Mechanical": [
        "Air Conditioning",
        "Ventilation",
        "Mechanical Equipment",
        "Ductwork",
        "Pump",
        "Fire Protection",
        "Other",
    ],
    "Plumbing": [
        "Water Pipe",
        "Drainage Pipe",
        "Water Tank",
        "Pump",
        "Water Closet",
        "Wash Hand Basin",
        "Sink",
        "Shower",
        "Floor Drain",
        "Other",
    ],
    "External Works": [
        "Paving",
        "Landscaping",
        "Boundary Wall",
        "Fence",
        "Gate",
        "External Drainage",
        "External Lighting",
        "Parking Area",
        "Other",
    ],
    "Other": [
        "Construction Item",
        "Material",
        "Labour",
        "Equipment",
        "Other",
    ],
}


UNITS = [
    "item",
    "m",
    "m²",
    "m³",
    "kg",
    "tonne",
    "No.",
    "set",
    "lot",
    "hour",
    "day",
]


STATUSES = [
    "Draft",
    "Measured",
    "Priced",
    "Approved",
    "Issued",
]


# ============================================================
# HELPERS
# ============================================================

def _safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert a value to float."""

    try:
        if value is None:
            return default

        if isinstance(value, str):
            cleaned = (
                value.replace(",", "")
                .replace(" ", "")
            )

            if not cleaned:
                return default

            return float(cleaned)

        return float(value)

    except (TypeError, ValueError):
        return default


def _format_money(value: float) -> str:
    """Format a monetary value for display."""

    return f"{value:,.2f}"


def _normalize_records(
    database: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Normalize BOQ records.

    Supports:
    - dictionaries
    - legacy string records
    """

    value = database.get("boq", [])

    if not isinstance(value, list):
        value = []

    records: list[dict[str, Any]] = []

    for index, item in enumerate(value, start=1):

        if isinstance(item, dict):

            record = dict(item)

            if not record.get("id"):
                record["id"] = index

            record.setdefault(
                "item_number",
                f"{index:03d}",
            )

            record.setdefault(
                "project",
                "",
            )

            record.setdefault(
                "category",
                "Other",
            )

            record.setdefault(
                "element",
                "Other",
            )

            record.setdefault(
                "description",
                "",
            )

            record.setdefault(
                "specification",
                "",
            )

            record.setdefault(
                "unit",
                "item",
            )

            record.setdefault(
                "quantity",
                0.0,
            )

            record.setdefault(
                "rate",
                0.0,
            )

            record.setdefault(
                "status",
                "Draft",
            )

            record.setdefault(
                "notes",
                "",
            )

            records.append(record)

        elif isinstance(item, str):

            records.append(
                {
                    "id": index,
                    "item_number": f"{index:03d}",
                    "project": "",
                    "category": "Other",
                    "element": "Other",
                    "description": item,
                    "specification": "",
                    "unit": "item",
                    "quantity": 1.0,
                    "rate": 0.0,
                    "status": "Draft",
                    "notes": "",
                }
            )

    database["boq"] = records

    return records


def _next_id(
    records: list[dict[str, Any]],
) -> int:
    """Return the next available BOQ record ID."""

    ids: list[int] = []

    for record in records:

        try:
            ids.append(
                int(record.get("id", 0))
            )

        except (
            TypeError,
            ValueError,
        ):
            continue

    return max(ids, default=0) + 1


def _next_item_number(
    records: list[dict[str, Any]],
) -> str:
    """Generate the next BOQ item number."""

    numbers: list[int] = []

    for record in records:

        value = str(
            record.get(
                "item_number",
                "",
            )
        ).strip()

        try:
            numbers.append(
                int(value)
            )

        except ValueError:
            continue

    return f"{max(numbers, default=0) + 1:03d}"


def _record_amount(
    record: dict[str, Any],
) -> float:
    """Calculate BOQ line amount."""

    quantity = _safe_float(
        record.get("quantity")
    )

    rate = _safe_float(
        record.get("rate")
    )

    return quantity * rate


# ============================================================
# SUMMARY
# ============================================================

def _render_summary(
    records: list[dict[str, Any]],
) -> None:
    """Render BOQ summary metrics."""

    total_items = len(records)

    total_value = sum(
        _record_amount(record)
        for record in records
    )

    priced_items = sum(
        1
        for record in records
        if _safe_float(
            record.get("rate")
        )
        > 0
    )

    approved_items = sum(
        1
        for record in records
        if str(
            record.get(
                "status",
                "",
            )
        ).lower()
        == "approved"
    )

    columns = st.columns(4)

    columns[0].metric(
        "BOQ Items",
        total_items,
    )

    columns[1].metric(
        "Priced Items",
        priced_items,
    )

    columns[2].metric(
        "Approved Items",
        approved_items,
    )

    columns[3].metric(
        "Total Value",
        _format_money(total_value),
    )


# ============================================================
# REGISTER TABLE
# ============================================================

def _render_register_table(
    records: list[dict[str, Any]],
) -> None:
    """Render a compact BOQ register."""

    if not records:

        st.info(
            "No BOQ items match the current filters."
        )

        return

    table_data = []

    for record in records:

        table_data.append(
            {
                "Item": record.get(
                    "item_number",
                    "",
                ),
                "Category": record.get(
                    "category",
                    "",
                ),
                "Element": record.get(
                    "element",
                    "",
                ),
                "Description": record.get(
                    "description",
                    "",
                ),
                "Unit": record.get(
                    "unit",
                    "",
                ),
                "Quantity": _safe_float(
                    record.get("quantity")
                ),
                "Rate": _safe_float(
                    record.get("rate")
                ),
                "Amount": _record_amount(
                    record
                ),
                "Status": record.get(
                    "status",
                    "",
                ),
            }
        )

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Quantity": st.column_config.NumberColumn(
                "Quantity",
                format="%.2f",
            ),
            "Rate": st.column_config.NumberColumn(
                "Rate",
                format="%.2f",
            ),
            "Amount": st.column_config.NumberColumn(
                "Amount",
                format="%.2f",
            ),
        },
    )


# ============================================================
# MAIN MODULE
# ============================================================

def render_boq_module(
    database: dict[str, Any],
) -> None:
    """Render the editable Bill of Quantities module."""

    st.title("Bill of Quantities")

    st.caption(
        "Measure, describe, price and manage construction work items."
    )

    records = _normalize_records(
        database
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    _render_summary(records)

    st.divider()

    # --------------------------------------------------------
    # Main tabs
    # --------------------------------------------------------

    (
        tab_overview,
        tab_register,
        tab_add,
    ) = st.tabs(
        [
            "Overview",
            "BOQ Register",
            "Add Item",
        ]
    )

    # ========================================================
    # OVERVIEW
    # ========================================================

    with tab_overview:

        st.subheader(
            "Construction Cost Summary"
        )

        if records:

            category_totals: dict[
                str,
                float,
            ] = {}

            for record in records:

                category = str(
                    record.get(
                        "category",
                        "Other",
                    )
                )

                category_totals[category] = (
                    category_totals.get(
                        category,
                        0.0,
                    )
                    + _record_amount(record)
                )

            summary_rows = []

            for category, value in sorted(
                category_totals.items()
            ):

                item_count = sum(
                    1
                    for record in records
                    if str(
                        record.get(
                            "category",
                            "Other",
                        )
                    )
                    == category
                )

                summary_rows.append(
                    {
                        "Category": category,
                        "Items": item_count,
                        "Value": value,
                    }
                )

            st.dataframe(
                summary_rows,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Items": st.column_config.NumberColumn(
                        "Items",
                        format="%d",
                    ),
                    "Value": st.column_config.NumberColumn(
                        "Value",
                        format="%.2f",
                    ),
                },
            )

        else:

            st.info(
                "Add BOQ items to begin building the construction cost plan."
            )

    # ========================================================
    # BOQ REGISTER
    # ========================================================

    with tab_register:

        st.subheader(
            "BOQ Register"
        )

        filter_columns = st.columns(3)

        category_options = [
            "All Categories",
            *CATEGORIES,
        ]

        selected_category = (
            filter_columns[0].selectbox(
                "Category",
                category_options,
            )
        )

        element_options = [
            "All Elements"
        ]

        if selected_category == "All Categories":

            all_elements = sorted(
                {
                    str(
                        record.get(
                            "element",
                            "Other",
                        )
                    )
                    for record in records
                }
            )

            element_options.extend(
                all_elements
            )

        else:

            element_options.extend(
                ELEMENTS_BY_CATEGORY.get(
                    selected_category,
                    ["Other"],
                )
            )

        selected_element = (
            filter_columns[1].selectbox(
                "Element",
                element_options,
            )
        )

        search = filter_columns[2].text_input(
            "Search",
            placeholder="Search BOQ...",
        )

        filtered_records = []

        search_text = search.strip().lower()

        for record in records:

            if (
                selected_category
                != "All Categories"
                and record.get("category")
                != selected_category
            ):
                continue

            if (
                selected_element
                != "All Elements"
                and record.get("element")
                != selected_element
            ):
                continue

            if search_text:

                searchable = " ".join(
                    [
                        str(
                            record.get(
                                "item_number",
                                "",
                            )
                        ),
                        str(
                            record.get(
                                "project",
                                "",
                            )
                        ),
                        str(
                            record.get(
                                "category",
                                "",
                            )
                        ),
                        str(
                            record.get(
                                "element",
                                "",
                            )
                        ),
                        str(
                            record.get(
                                "description",
                                "",
                            )
                        ),
                        str(
                            record.get(
                                "specification",
                                "",
                            )
                        ),
                    ]
                ).lower()

                if search_text not in searchable:
                    continue

            filtered_records.append(
                record
            )

        _render_register_table(
            filtered_records
        )

        st.divider()

        # ----------------------------------------------------
        # Editable records
        # ----------------------------------------------------

        for index, record in enumerate(
            filtered_records
        ):

            record_id = record.get(
                "id",
                index + 1,
            )

            item_number = record.get(
                "item_number",
                "",
            )

            description = record.get(
                "description",
                "BOQ Item",
            )

            amount = _record_amount(
                record
            )

            heading = (
                f"{item_number} — "
                f"{description} "
                f"({_format_money(amount)})"
            )

            with st.expander(
                heading,
                expanded=False,
            ):

                with st.form(
                    f"edit_boq_{record_id}"
                ):

                    first_row = st.columns(2)

                    edited_project = (
                        first_row[0].text_input(
                            "Project",
                            value=str(
                                record.get(
                                    "project",
                                    "",
                                )
                                or ""
                            ),
                        )
                    )

                    edited_item_number = (
                        first_row[1].text_input(
                            "Item Number",
                            value=str(
                                item_number
                                or ""
                            ),
                        )
                    )

                    category = str(
                        record.get(
                            "category",
                            "Other",
                        )
                    )

                    category_index = (
                        CATEGORIES.index(
                            category
                        )
                        if category in CATEGORIES
                        else len(CATEGORIES) - 1
                    )

                    edited_category = (
                        st.selectbox(
                            "Category",
                            CATEGORIES,
                            index=category_index,
                        )
                    )

                    available_elements = (
                        ELEMENTS_BY_CATEGORY.get(
                            edited_category,
                            ["Other"],
                        )
                    )

                    current_element = str(
                        record.get(
                            "element",
                            "Other",
                        )
                    )

                    element_index = (
                        available_elements.index(
                            current_element
                        )
                        if current_element
                        in available_elements
                        else 0
                    )

                    edited_element = (
                        st.selectbox(
                            "Construction Element",
                            available_elements,
                            index=element_index,
                        )
                    )

                    edited_description = (
                        st.text_input(
                            "Description",
                            value=str(
                                record.get(
                                    "description",
                                    "",
                                )
                                or ""
                            ),
                        )
                    )

                    edited_specification = (
                        st.text_area(
                            "Specification",
                            value=str(
                                record.get(
                                    "specification",
                                    "",
                                )
                                or ""
                            ),
                        )
                    )

                    quantity_columns = (
                        st.columns(3)
                    )

                    current_unit = str(
                        record.get(
                            "unit",
                            "item",
                        )
                    )

                    unit_index = (
                        UNITS.index(
                            current_unit
                        )
                        if current_unit in UNITS
                        else 0
                    )

                    edited_unit = (
                        quantity_columns[0].selectbox(
                            "Unit",
                            UNITS,
                            index=unit_index,
                        )
                    )

                    edited_quantity = (
                        quantity_columns[1].number_input(
                            "Quantity",
                            min_value=0.0,
                            value=_safe_float(
                                record.get(
                                    "quantity"
                                )
                            ),
                            step=0.01,
                        )
                    )

                    edited_rate = (
                        quantity_columns[2].number_input(
                            "Rate",
                            min_value=0.0,
                            value=_safe_float(
                                record.get(
                                    "rate"
                                )
                            ),
                            step=0.01,
                        )
                    )

                    edited_amount = (
                        edited_quantity
                        * edited_rate
                    )

                    st.metric(
                        "Calculated Amount",
                        _format_money(
                            edited_amount
                        ),
                    )

                    current_status = str(
                        record.get(
                            "status",
                            "Draft",
                        )
                    )

                    status_index = (
                        STATUSES.index(
                            current_status
                        )
                        if current_status
                        in STATUSES
                        else 0
                    )

                    edited_status = (
                        st.selectbox(
                            "Status",
                            STATUSES,
                            index=status_index,
                        )
                    )

                    edited_notes = (
                        st.text_area(
                            "Notes",
                            value=str(
                                record.get(
                                    "notes",
                                    "",
                                )
                                or ""
                            ),
                        )
                    )

                    submitted = (
                        st.form_submit_button(
                            "Save Changes",
                            use_container_width=True,
                        )
                    )

                if submitted:

                    if not edited_description.strip():

                        st.error(
                            "Description is required."
                        )

                    elif not edited_item_number.strip():

                        st.error(
                            "Item number is required."
                        )

                    else:

                        record[
                            "project"
                        ] = edited_project.strip()

                        record[
                            "item_number"
                        ] = (
                            edited_item_number.strip()
                        )

                        record[
                            "category"
                        ] = edited_category

                        record[
                            "element"
                        ] = edited_element

                        record[
                            "description"
                        ] = (
                            edited_description.strip()
                        )

                        record[
                            "specification"
                        ] = (
                            edited_specification.strip()
                        )

                        record[
                            "unit"
                        ] = edited_unit

                        record[
                            "quantity"
                        ] = edited_quantity

                        record[
                            "rate"
                        ] = edited_rate

                        record[
                            "status"
                        ] = edited_status

                        record[
                            "notes"
                        ] = edited_notes.strip()

                        save_memory(
                            database
                        )

                        st.success(
                            "BOQ item updated successfully."
                        )

                        st.rerun()

                if st.button(
                    "Delete BOQ Item",
                    key=f"delete_boq_{record_id}",
                    use_container_width=True,
                ):

                    records.remove(
                        record
                    )

                    save_memory(
                        database
                    )

                    st.success(
                        "BOQ item deleted successfully."
                    )

                    st.rerun()

    # ========================================================
    # ADD BOQ ITEM
    # ========================================================

    with tab_add:

        st.subheader(
            "Add Construction Item"
        )

        with st.form(
            "add_boq_item_form",
            clear_on_submit=True,
        ):

            project = st.text_input(
                "Project"
            )

            category = st.selectbox(
                "Category",
                CATEGORIES,
            )

            elements = ELEMENTS_BY_CATEGORY.get(
                category,
                ["Other"],
            )

            element = st.selectbox(
                "Construction Element",
                elements,
            )

            description = st.text_input(
                "Description",
                placeholder=(
                    "Example: Reinforced concrete column"
                ),
            )

            specification = st.text_area(
                "Specification",
                placeholder=(
                    "Example: 300 x 300 mm reinforced concrete column"
                ),
            )

            quantity_columns = st.columns(3)

            unit = quantity_columns[0].selectbox(
                "Unit",
                UNITS,
            )

            quantity = quantity_columns[1].number_input(
                "Quantity",
                min_value=0.0,
                value=0.0,
                step=0.01,
            )

            rate = quantity_columns[2].number_input(
                "Rate",
                min_value=0.0,
                value=0.0,
                step=0.01,
            )

            status = st.selectbox(
                "Status",
                STATUSES,
            )

            notes = st.text_area(
                "Notes"
            )

            submitted = st.form_submit_button(
                "Add BOQ Item",
                use_container_width=True,
            )

        if submitted:

            if not description.strip():

                st.error(
                    "Description is required."
                )

            else:

                records.append(
                    {
                        "id": _next_id(
                            records
                        ),
                        "item_number": (
                            _next_item_number(
                                records
                            )
                        ),
                        "project": (
                            project.strip()
                        ),
                        "category": category,
                        "element": element,
                        "description": (
                            description.strip()
                        ),
                        "specification": (
                            specification.strip()
                        ),
                        "unit": unit,
                        "quantity": quantity,
                        "rate": rate,
                        "status": status,
                        "notes": notes.strip(),
                    }
                )

                save_memory(
                    database
                )

                st.success(
                    "BOQ item added successfully."
                )

                st.rerun()