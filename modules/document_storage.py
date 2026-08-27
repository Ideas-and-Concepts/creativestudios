"""
Creative Studios
Shared Document and File Storage

Provides a common file repository for all Creative Studios
modules.

Files are stored on disk while metadata is stored in the
application database.
"""

from __future__ import annotations

import mimetypes
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from modules.database import save_memory


# ============================================================
# STORAGE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

STORAGE_DIR = (
    BASE_DIR
    / "storage"
    / "documents"
)

MAX_FILE_SIZE_MB = 100

ALLOWED_EXTENSIONS = {
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "csv",
    "txt",
    "rtf",
    "ppt",
    "pptx",
    "dwg",
    "dxf",
    "ifc",
    "rvt",
    "rfa",
    "nwc",
    "nwd",
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webp",
    "svg",
    "zip",
    "rar",
    "7z",
}


# ============================================================
# HELPERS
# ============================================================

def _safe_filename(filename: str) -> str:
    """Return a filesystem-safe filename."""

    name = Path(filename or "file").name

    name = re.sub(
        r"[^A-Za-z0-9._-]+",
        "_",
        name,
    )

    name = name.strip("._")

    return name or "file"


def _extension(filename: str) -> str:
    """Return a lowercase file extension without the dot."""

    return Path(filename).suffix.lower().lstrip(".")


def _documents(
    database: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return the normalized document metadata collection."""

    value = database.get(
        "documents",
        [],
    )

    if not isinstance(value, list):
        value = []

    records: list[dict[str, Any]] = []

    for index, item in enumerate(
        value,
        start=1,
    ):

        if not isinstance(item, dict):
            continue

        record = dict(item)

        if not record.get("id"):
            record["id"] = index

        records.append(record)

    database["documents"] = records

    return records


def _next_id(
    records: list[dict[str, Any]],
) -> int:
    """Generate the next numeric document ID."""

    values: list[int] = []

    for record in records:

        try:
            values.append(
                int(record.get("id", 0))
            )

        except (
            TypeError,
            ValueError,
        ):
            continue

    return max(values, default=0) + 1


def ensure_storage() -> None:
    """Create the storage directory."""

    STORAGE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def module_directory(
    module_name: str,
) -> Path:
    """Return the storage directory for a module."""

    safe_module = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        str(module_name).strip().lower(),
    )

    directory = (
        STORAGE_DIR
        / safe_module
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return directory


# ============================================================
# SAVE FILE
# ============================================================

def save_uploaded_file(
    database: dict[str, Any],
    uploaded_file: Any,
    module_name: str,
    *,
    title: str = "",
    description: str = "",
    project: str = "",
    document_type: str = "General",
    revision: str = "A",
    status: str = "Draft",
) -> dict[str, Any]:
    """
    Save an uploaded Streamlit file and its metadata.
    """

    if uploaded_file is None:
        raise ValueError("No file was selected.")

    original_name = str(
        getattr(
            uploaded_file,
            "name",
            "file",
        )
    )

    extension = _extension(
        original_name
    )

    if (
        extension
        and extension not in ALLOWED_EXTENSIONS
    ):
        raise ValueError(
            f".{extension} files are not supported."
        )

    data = uploaded_file.getvalue()

    if not isinstance(data, bytes):
        data = bytes(data)

    max_bytes = (
        MAX_FILE_SIZE_MB
        * 1024
        * 1024
    )

    if len(data) > max_bytes:

        raise ValueError(
            f"File exceeds the maximum "
            f"size of {MAX_FILE_SIZE_MB} MB."
        )

    ensure_storage()

    directory = module_directory(
        module_name
    )

    safe_name = _safe_filename(
        original_name
    )

    unique_name = (
        f"{uuid.uuid4().hex[:12]}"
        f"_{safe_name}"
    )

    file_path = (
        directory
        / unique_name
    )

    file_path.write_bytes(data)

    records = _documents(
        database
    )

    now = datetime.now().isoformat(
        timespec="seconds"
    )

    record = {
        "id": _next_id(records),
        "module": str(module_name),
        "title": (
            title.strip()
            or Path(original_name).stem
        ),
        "description": description.strip(),
        "project": project.strip(),
        "document_type": document_type,
        "revision": revision.strip() or "A",
        "status": status,
        "original_name": original_name,
        "stored_name": unique_name,
        "relative_path": str(
            file_path.relative_to(
                BASE_DIR
            )
        ),
        "mime_type": (
            getattr(
                uploaded_file,
                "type",
                None,
            )
            or mimetypes.guess_type(
                original_name
            )[0]
            or "application/octet-stream"
        ),
        "size_bytes": len(data),
        "created_at": now,
        "updated_at": now,
    }

    records.append(record)

    save_memory(database)

    return record


# ============================================================
# QUERY
# ============================================================

def list_module_files(
    database: dict[str, Any],
    module_name: str,
) -> list[dict[str, Any]]:
    """Return files belonging to a module."""

    records = _documents(
        database
    )

    target = str(
        module_name
    ).strip().lower()

    return [
        record
        for record in records
        if str(
            record.get(
                "module",
                "",
            )
        ).strip().lower()
        == target
    ]


def get_file_bytes(
    record: dict[str, Any],
) -> bytes | None:
    """Read a stored file."""

    relative_path = record.get(
        "relative_path"
    )

    if not relative_path:
        return None

    path = (
        BASE_DIR
        / str(relative_path)
    )

    try:

        if not path.exists():
            return None

        return path.read_bytes()

    except OSError:

        return None


# ============================================================
# DELETE
# ============================================================

def delete_file(
    database: dict[str, Any],
    document_id: Any,
) -> bool:
    """Delete both metadata and the physical file."""

    records = _documents(
        database
    )

    target = None

    for record in records:

        if str(
            record.get("id")
        ) == str(document_id):

            target = record
            break

    if target is None:
        return False

    relative_path = target.get(
        "relative_path"
    )

    if relative_path:

        path = (
            BASE_DIR
            / str(relative_path)
        )

        try:

            if path.exists():
                path.unlink()

        except OSError:
            pass

    records.remove(target)

    save_memory(database)

    return True


# ============================================================
# FORMATTING
# ============================================================

def format_file_size(
    size_bytes: Any,
) -> str:
    """Format bytes into a human-readable size."""

    try:
        size = float(size_bytes)

    except (
        TypeError,
        ValueError,
    ):
        return "Unknown size"

    if size < 1024:
        return f"{int(size)} B"

    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"

    if size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"

    return f"{size / (1024 * 1024 * 1024):.1f} GB"


# ============================================================
# STREAMLIT FILE MANAGER
# ============================================================

def render_module_files(
    database: dict[str, Any],
    module_name: str,
    *,
    project_options: list[str] | None = None,
) -> None:
    """
    Render a complete file/document manager for a module.
    """

    st.subheader(
        "Files & Documents"
    )

    st.caption(
        f"Store drawings, reports, specifications, "
        f"calculations and other {module_name.lower()} records."
    )

    files = list_module_files(
        database,
        module_name,
    )

    upload_tab, library_tab = st.tabs(
        [
            "Add File",
            "File Library",
        ]
    )

    with upload_tab:

        with st.form(
            f"upload_{module_name.lower()}_file",
            clear_on_submit=True,
        ):

            uploaded_file = st.file_uploader(
                "Select File",
                type=sorted(
                    ALLOWED_EXTENSIONS
                ),
            )

            title = st.text_input(
                "Document Title"
            )

            description = st.text_area(
                "Description / Notes"
            )

            if project_options:

                project = st.selectbox(
                    "Project",
                    [
                        "General",
                        *project_options,
                    ],
                )

            else:

                project = st.text_input(
                    "Project"
                )

            document_type = st.selectbox(
                "Document Type",
                [
                    "General",
                    "Drawing",
                    "Specification",
                    "Calculation",
                    "Report",
                    "Schedule",
                    "Model",
                    "Contract",
                    "Correspondence",
                    "Photo",
                    "Survey",
                    "Certificate",
                    "Other",
                ],
            )

            revision = st.text_input(
                "Revision",
                value="A",
            )

            status = st.selectbox(
                "Status",
                [
                    "Draft",
                    "In Review",
                    "Approved",
                    "Issued",
                    "Superseded",
                ],
            )

            submitted = st.form_submit_button(
                "Save File",
                use_container_width=True,
            )

        if submitted:

            if uploaded_file is None:

                st.error(
                    "Please select a file."
                )

            else:

                try:

                    record = save_uploaded_file(
                        database,
                        uploaded_file,
                        module_name,
                        title=title,
                        description=description,
                        project=project,
                        document_type=document_type,
                        revision=revision,
                        status=status,
                    )

                    st.success(
                        f"'{record['title']}' "
                        "was saved successfully."
                    )

                    st.rerun()

                except Exception as exc:

                    st.error(
                        f"Unable to save file: {exc}"
                    )

    with library_tab:

        search = st.text_input(
            "Search files",
            key=(
                f"file_search_"
                f"{module_name.lower()}"
            ),
        ).strip().lower()

        filtered = files

        if search:

            filtered = [
                record
                for record in files
                if search in " ".join(
                    [
                        str(
                            record.get(
                                "title",
                                "",
                            )
                        ),
                        str(
                            record.get(
                                "original_name",
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
                                "document_type",
                                "",
                            )
                        ),
                        str(
                            record.get(
                                "status",
                                "",
                            )
                        ),
                    ]
                ).lower()
            ]

        if not filtered:

            st.info(
                "No files have been registered "
                "for this module."
            )

            return

        st.write(
            f"{len(filtered)} file(s)"
        )

        for record in filtered:

            document_id = record.get(
                "id"
            )

            title = str(
                record.get(
                    "title",
                    "Untitled",
                )
            )

            filename = str(
                record.get(
                    "original_name",
                    "File",
                )
            )

            with st.expander(
                title,
                expanded=False,
            ):

                col1, col2 = st.columns(
                    2
                )

                with col1:

                    st.write(
                        f"**File:** {filename}"
                    )

                    st.write(
                        f"**Project:** "
                        f"{record.get('project', '') or 'General'}"
                    )

                    st.write(
                        f"**Type:** "
                        f"{record.get('document_type', 'General')}"
                    )

                    st.write(
                        f"**Revision:** "
                        f"{record.get('revision', 'A')}"
                    )

                with col2:

                    st.write(
                        f"**Status:** "
                        f"{record.get('status', 'Draft')}"
                    )

                    st.write(
                        f"**Size:** "
                        f"{format_file_size(record.get('size_bytes', 0))}"
                    )

                    st.write(
                        f"**Added:** "
                        f"{record.get('created_at', '')}"
                    )

                description = record.get(
                    "description",
                    "",
                )

                if description:
                    st.write(
                        f"**Notes:** {description}"
                    )

                file_bytes = get_file_bytes(
                    record
                )

                if file_bytes is not None:

                    st.download_button(
                        "Download File",
                        data=file_bytes,
                        file_name=filename,
                        mime=record.get(
                            "mime_type",
                            "application/octet-stream",
                        ),
                        key=(
                            f"download_"
                            f"{module_name.lower()}_"
                            f"{document_id}"
                        ),
                        use_container_width=True,
                    )

                else:

                    st.warning(
                        "The file metadata exists, "
                        "but the physical file is "
                        "not currently available."
                    )

                if st.button(
                    "Delete File",
                    key=(
                        f"delete_"
                        f"{module_name.lower()}_"
                        f"{document_id}"
                    ),
                    use_container_width=True,
                ):

                    delete_file(
                        database,
                        document_id,
                    )

                    st.success(
                        "File deleted."
                    )

                    st.rerun()