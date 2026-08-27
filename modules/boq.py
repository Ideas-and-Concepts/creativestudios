"""
Creative Studios
Bill of Quantities Module
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from modules.database import save_memory
from modules.document_storage import render_module_files


CATEGORIES = [
    "Preliminaries",
    "Earthworks",
    "Concrete",
    "Reinforcement",
    "Formwork",
    "Masonry",
    "Walls",
    "Doors",
    "Windows",
    "Roofing",
    "Finishes",
    "Structural",
    "Plumbing",
    "Electrical",
    "Mechanical",
    "External Works",
    "Other",
]

UNITS = [
    "item",
    "m",
    "m2",
    "m3",
    "kg",
    "ton",
    "No.",
    "set",
    "lot",
]


def _normalize(
    database: dict[str, Any],
) -> list[dict[str, Any]]:

    value = database.get(
        "boq",
        [],
    )

    if not isinstance(value, list):
        value = []

    records = []

    for index, item in enumerate(
        value,
        start=1,
    ):

        if isinstance(item, dict):

            record = dict(item)

            if not record.get("id"):
                record["id"] = index

            records.append(record)

    database["boq"] = records

    return records


def _next_id(
    records: list[dict[str, Any]],
) -> int:

    ids = []

    for record in records:

        try:
            ids.append(
                int(record.get("id", 0))
            )

        except (
            TypeError,
            ValueError,
        ):
            pass

    return max(ids, default=0) + 1


def render_boq_module(
    database: dict[str, Any],
) -> None:

    st.title("Bill of Quantities")

    st.caption(
        "Construction quantities, materials, elements "
        "and cost information."
    )

    records = _normalize(database)

    overview, register, files = st.tabs(
        [
            "Overview",
            "BOQ Register",
            "Files & Documents",
        ]
    )

    with overview:

        total_quantity = sum(
            float(
                r.get(
                    "quantity",
                    0,
                )
                or 0
            )
            for r in records
            if str(
                r.get(
                    "quantity",
                    "",
                )
            ).replace(
                ".",
                "",
                1,
            ).isdigit()
        )

        total_amount = sum(
            float(
                r.get(
                    "quantity",
                    0,
                )
                or 0
            )
            * float(
                r.get(
                    "rate",
                    0,
                )
                or 0
            )
            for r in records
            if str(
                r.get(
                    "quantity",
                    "",
                )
            ).replace(
                ".",
                "",
                1,
            ).isdigit()
            and str(
                r.get(
                    "rate",
                    "",
                )
            ).replace(
                ".",
                "",
                1,
            ).isdigit()
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "BOQ Items",
            len(records),
        )

        c2.metric(
            "Total Quantity",
            f"{total_quantity:,.2f}",
        )

        c3.metric(
            "Estimated Amount",
            f"{total_amount:,.2f}",
        )

        st.divider()

        st.write(
            "BOQ elements include columns, beams, slabs, "
            "walls, doors, windows, finishes, services and "
            "other construction work items."
        )

    with register:

        search = st.text_input(
            "Search BOQ"
        ).strip().lower()

        visible = records

        if search:

            visible = [
                r
                for r in records
                if search in " ".join(
                    [
                        str(
                            r.get(
                                "description",
                                "",
                            )
                        ),
                        str(
                            r.get(
                                "category",
                                "",
                            )
                        ),
                        str(
                            r.get(
                                "project",
                                "",
                            )
                        ),
                    ]
                ).lower()
            ]

        for index, record in enumerate(visible):

            item_id = record.get(
                "id",
                index + 1,
            )

            with st.expander(
                str(
                    record.get(
                        "description",
                        "BOQ Item",
                    )
                ),
                expanded=False,
            ):

                with st.form(
                    f"boq_edit_{item_id}"
                ):

                    description = st.text_input(
                        "Description",
                        value=str(
                            record.get(
                                "description",
                                "",
                            )
                        ),
                    )

                    project = st.text_input(
                        "Project",
                        value=str(
                            record.get(
                                "project",
                                "",
                            )
                        ),
                    )

                    category = st.selectbox(
                        "Category",
                        CATEGORIES,
                        index=(
                            CATEGORIES.index(
                                record.get(
                                    "category",
                                    "Other",
                                )
                            )
                            if record.get(
                                "category",
                                "Other",
                            )
                            in CATEGORIES
                            else len(CATEGORIES) - 1
                        ),
                    )

                    unit = st.selectbox(
                        "Unit",
                        UNITS,
                        index=(
                            UNITS.index(
                                record.get(
                                    "unit",
                                    "item",
                                )
                            )
                            if record.get(
                                "unit",
                                "item",
                            )
                            in UNITS
                            else 0
                        ),
                    )

                    quantity = st.number_input(
                        "Quantity",
                        min_value=0.0,
                        value=float(
                            record.get(
                                "quantity",
                                0,
                            )
                            or 0
                        ),
                    )

                    rate = st.number_input(
                        "Rate",
                        min_value=0.0,
                        value=float(
                            record.get(
                                "rate",
                                0,
                            )
                            or 0
                        ),
                    )

                    notes = st.text_area(
                        "Notes",
                        value=str(
                            record.get(
                                "notes",
                                "",
                            )
                        ),
                    )

                    save = st.form_submit_button(
                        "Save Changes",
                        use_container_width=True,
                    )

                if save:

                    if not description.strip():

                        st.error(
                            "Description is required."
                        )

                    else:

                        record.update(
                            {
                                "description": description.strip(),
                                "project": project.strip(),
                                "category": category,
                                "unit": unit,
                                "quantity": quantity,
                                "rate": rate,
                                "amount": quantity * rate,
                                "notes": notes.strip(),
                            }
                        )

                        save_memory(database)

                        st.success(
                            "BOQ item updated."
                        )

                        st.rerun()

                if st.button(
                    "Delete Item",
                    key=f"boq_delete_{item_id}",
                    use_container_width=True,
                ):

                    records.remove(record)

                    save_memory(database)

                    st.rerun()

        st.divider()

        with st.form(
            "boq_add",
            clear_on_submit=True,
        ):

            description = st.text_input(
                "Description"
            )

            project = st.text_input(
                "Project"
            )

            category = st.selectbox(
                "Category",
                CATEGORIES,
            )

            unit = st.selectbox(
                "Unit",
                UNITS,
            )

            quantity = st.number_input(
                "Quantity",
                min_value=0.0,
                value=1.0,
            )

            rate = st.number_input(
                "Rate",
                min_value=0.0,
                value=0.0,
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
                        "id": _next_id(records),
                        "description": description.strip(),
                        "project": project.strip(),
                        "category": category,
                        "unit": unit,
                        "quantity": quantity,
                        "rate": rate,
                        "amount": quantity * rate,
                        "notes": notes.strip(),
                    }
                )

                save_memory(database)

                st.success(
                    "BOQ item added."
                )

                st.rerun()

    with files:

        projects = sorted(
            {
                str(
                    r.get(
                        "project",
                        "",
                    )
                )
                for r in records
                if r.get("project")
            }
        )

        render_module_files(
            database,
            "BOQ",
            project_options=projects,
        )