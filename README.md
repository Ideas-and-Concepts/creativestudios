Creative Studios

AEC Collaboration Platform

Creative Studios is an integrated Architecture, Engineering and Construction (AEC) collaboration platform designed to manage project information, technical design, drawings, construction quantities and project documentation from a single workspace.

The platform is being developed as a practical construction-management system with a focus on connecting design information to actual construction activities.

---

Overview

Creative Studios provides a centralized workspace for:

- Project management
- Architecture
- Engineering
- Architectural drawings
- Structural drawings
- Bill of Quantities
- Documents
- MEP coordination
- Construction information
- Future procurement integration
- Future cost-control integration

The platform is designed around a connected construction information workflow rather than isolated modules.

---

Core Workflow

PROJECT
   |
   +----------------------+
   |                      |
   v                      v
ARCHITECTURE          ENGINEERING
   |                      |
   |                      |
   v                      v
ARCHITECTURAL         STRUCTURAL /
DRAWINGS              ENGINEERING
   |                   DRAWINGS
   |                      |
   +----------+-----------+
              |
              v
             BOQ
              |
              v
         PROCUREMENT
              |
              v
         CONSTRUCTION
              |
              v
         COST CONTROL

The objective is to progressively connect project design information with quantities, procurement and construction costs.

---

Current Modules

Dashboard

The Dashboard provides a high-level view of the Creative Studios workspace.

Typical information includes:

- Project counts
- Current project status
- Activity summaries
- Construction information
- Module navigation

---

Projects

The Projects module is the parent context for project information.

Projects are intended to provide the common reference used by:

- Architecture
- Engineering
- Drawings
- BOQ
- Documents
- MEP
- Procurement
- Construction
- Cost control

A project should eventually act as the central object connecting all construction information.

---

Architecture

The Architecture module manages architectural design and construction information.

Architectural work can include:

- Floor planning
- Walls
- Doors
- Windows
- Rooms
- Roofs
- Finishes
- Partitions
- Architectural design stages
- Design documentation
- Architectural notes

Typical design stages include:

Concept
   |
Schematic Design
   |
Design Development
   |
Construction Documentation
   |
Issued

Architecture records are editable and persisted through the application database.

---

Engineering

The Engineering module manages engineering and structural construction information.

Engineering elements include:

- Foundations
- Columns
- Beams
- Slabs
- Structural walls
- Staircases
- Lintels
- Reinforcement
- Formwork
- Structural concrete
- Civil works
- Infrastructure
- Geotechnical works
- Transportation works
- Environmental works

Engineering records can be associated with projects and managed throughout their design lifecycle.

---

Drawings

The Drawings module manages the project's technical drawing register.

Drawings are divided into two primary construction disciplines:

DRAWINGS
   |
   +-- Architectural Drawings
   |
   +-- Structural Drawings

Additional engineering drawing disciplines may include:

- Civil
- Electrical
- Mechanical
- Plumbing
- Other

Drawing information can include:

- Drawing number
- Drawing title
- Project
- Discipline
- Revision
- Scale
- Status
- Creation date

Typical drawing statuses include:

Draft
   |
In Review
   |
Approved
   |
Issued
   |
Superseded

---

Bill of Quantities

The BOQ module provides the construction quantity and pricing register.

It is designed around actual construction elements rather than a generic product catalogue.

Construction Elements

Preliminaries

- Site establishment
- Mobilisation
- Demobilisation
- Setting out
- Temporary works
- Health and safety
- Site supervision

Substructure

- Excavation
- Backfilling
- Blinding concrete
- Pad foundations
- Strip foundations
- Raft foundations
- Ground beams
- Foundation walls
- Damp proofing

Structural

- Columns
- Beams
- Slabs
- Structural walls
- Staircases
- Lintels
- Reinforcement
- Formwork
- Structural concrete

Walls

- External walls
- Internal walls
- Block walls
- Brick walls
- Partition walls
- Retaining walls
- Parapets

Openings

- Doors
- Windows
- Louvers
- Glazed screens
- Roller shutters
- Fire doors

Roofing

- Roof structures
- Roof coverings
- Roof trusses
- Roof sheets
- Roof tiles
- Gutters
- Downpipes
- Roof insulation

Architectural Finishes

- Plaster
- Rendering
- Screed
- Floor tiling
- Wall tiling
- Ceilings
- Painting
- Floor finishes
- Skirting
- Cladding

Civil Works

- Earthworks
- Roads
- Drainage
- Kerbs
- Pavements
- Concrete works
- Stormwater drainage
- Manholes

Electrical

- Lighting points
- Socket outlets
- Switches
- Distribution boards
- Cables
- Conduits
- Electrical panels
- Earthing

Mechanical

- Air conditioning
- Ventilation
- Mechanical equipment
- Ductwork
- Pumps
- Fire protection

Plumbing

- Water pipes
- Drainage pipes
- Water tanks
- Pumps
- Water closets
- Wash-hand basins
- Sinks
- Showers
- Floor drains

External Works

- Paving
- Landscaping
- Boundary walls
- Fencing
- Gates
- External drainage
- External lighting
- Parking areas

---

BOQ Data Structure

A BOQ item contains construction and commercial information such as:

Item Number
Project
Category
Construction Element
Description
Specification
Unit
Quantity
Rate
Amount
Status
Notes

The line amount is calculated automatically:

Amount = Quantity × Rate

The BOQ can therefore become the foundation for future project cost control.

---

BOQ Status

BOQ items can progress through:

Draft
   |
Measured
   |
Priced
   |
Approved
   |
Issued

This provides a foundation for controlling quantities and commercial information throughout the project lifecycle.

---

Documents

The Documents module is intended to provide a central document repository for project records.

Documents may eventually include:

- Contracts
- Specifications
- Reports
- Drawings
- Correspondence
- RFIs
- Approvals
- Method statements
- Inspection records
- Certificates
- Project photographs
- Commercial documents

---

MEP

The MEP module provides a dedicated area for mechanical, electrical and plumbing information.

The module is intended to support:

- Mechanical systems
- Electrical systems
- Plumbing systems
- Building services
- Equipment
- Services coordination

MEP information will eventually connect with drawings, BOQ items and procurement.

---

Data Persistence

Creative Studios currently uses a lightweight JSON-based persistence layer.

The database module provides:

load_memory()
save_memory(database)

The application database is stored as:

creativestudios_db.json

The database structure is intentionally simple during the current development stage.

This allows rapid development while keeping the application independent of a database server.

A relational database can be introduced later when the project's data relationships require it.

---

Application Architecture

The application uses a modular Streamlit architecture.

The main application is:

streamlit_app.py

Modules are stored in:

modules/

Current module structure:

modules/
├── __init__.py
├── database.py
├── dashboard.py
├── projects.py
├── documents.py
├── architecture.py
├── engineering.py
├── drawings.py
├── boq.py
└── mep.py

The main application uses lazy module loading.

Instead of importing every module when the application starts, the selected module is loaded dynamically.

Conceptually:

importlib.import_module(...)

This reduces the impact of errors in unrelated modules and keeps the application architecture modular.

---

Navigation

The current application navigation is:

Dashboard
Projects
Documents
Architecture
Engineering
Drawings
BOQ
MEP

The application also supports:

- Dark mode
- Light mode
- Responsive Streamlit layout
- Sidebar branding
- Creative Studios logo
- Editable records
- Persistent records

Authentication has currently been removed from the Streamlit application.

---

Branding

The application is branded as:

Creative Studios

Subtitle:

AEC Collaboration Platform

The primary logo asset is expected at:

assets/creative_studios.png

The application uses a restrained professional interface designed for architecture, engineering and construction workflows.

---

Design Principles

Creative Studios follows several core principles.

1. Construction First

The system is designed around real construction workflows rather than generic business software.

2. Modular Architecture

Each major AEC discipline is implemented as an independent module.

3. Editable Information

Users should be able to create, update and remove project records directly from the interface.

4. Persistent Data

Changes made through the application should be persisted through the database layer.

5. Cross-Module Integration

Information should progressively move through the construction lifecycle.

For example:

Architectural Design
        ↓
Architectural Drawing
        ↓
BOQ Item
        ↓
Procurement Requirement
        ↓
Construction Activity
        ↓
Cost

And:

Structural Design
        ↓
Structural Drawing
        ↓
Structural BOQ
        ↓
Materials
        ↓
Construction
        ↓
Cost Control

---

Development Roadmap

Phase 1 — Core Workspace

- Dashboard
- Projects
- Documents
- Architecture
- Engineering
- Drawings
- BOQ
- MEP

Phase 2 — Construction Integration

Planned improvements:

- Shared project IDs
- Cross-module project selection
- Architecture-to-drawing relationships
- Engineering-to-drawing relationships
- Drawing-to-BOQ relationships
- BOQ item references
- Construction elements
- Quantity tracking

Phase 3 — Procurement

Planned workflow:

Approved BOQ
      ↓
Material Requirement
      ↓
Purchase Request
      ↓
Purchase Order
      ↓
Supplier
      ↓
Goods Received
      ↓
Warehouse

Phase 4 — Construction Management

Planned functionality:

- Site activities
- Work packages
- Daily site records
- Labour
- Equipment
- Materials
- Inspections
- RFIs
- Approvals
- Progress tracking

Phase 5 — Cost Control

Planned functionality:

- BOQ budget
- Committed costs
- Actual costs
- Variations
- Payment certificates
- Project cost reports
- Budget versus actual
- Cost forecasting

Phase 6 — Advanced AEC Platform

Future functionality may include:

- BIM integration
- Drawing viewer
- Document version control
- RFI workflows
- Approval workflows
- Project scheduling
- Site reporting
- Procurement automation
- Financial integration
- AI-assisted project analysis

---

Installation

Clone the repository:

git clone <repository-url>
cd creativestudios

Install dependencies:

pip install -r requirements.txt

Run the application:

streamlit run streamlit_app.py

The application should then be available through the Streamlit server URL.

---

Requirements

The application currently relies primarily on:

- Python
- Streamlit

Additional dependencies may be added as modules evolve.

---

Project Structure

A typical repository structure is:

creativestudios/
│
├── streamlit_app.py
├── requirements.txt
├── README.md
├── creativestudios_db.json
│
├── assets/
│   └── creative_studios.png
│
└── modules/
    ├── __init__.py
    ├── database.py
    ├── dashboard.py
    ├── projects.py
    ├── documents.py
    ├── architecture.py
    ├── engineering.py
    ├── drawings.py
    ├── boq.py
    └── mep.py

---

Data Model Direction

The long-term data model is intended to evolve toward:

Project
  |
  +-- Architecture
  |      |
  |      +-- Architectural Elements
  |      +-- Architectural Drawings
  |
  +-- Engineering
  |      |
  |      +-- Structural Elements
  |      +-- Structural Drawings
  |
  +-- BOQ
  |      |
  |      +-- Construction Items
  |      +-- Quantities
  |      +-- Rates
  |      +-- Costs
  |
  +-- Documents
  |
  +-- MEP
  |
  +-- Procurement
  |
  +-- Construction
  |
  +-- Cost Control

This structure is intended to prevent the platform from becoming a collection of disconnected forms.

---

Contributing

Development should preserve the modular architecture.

When adding a new module:

1. Create the module under "modules/".
2. Provide a clearly defined renderer function.
3. Use the shared database layer.
4. Normalize legacy records where necessary.
5. Keep records editable.
6. Avoid introducing unnecessary dependencies.
7. Register the module in "streamlit_app.py".
8. Test the module independently before integrating it with other modules.

---

Development Philosophy

Creative Studios is being developed incrementally.

The priority is:

Working
    ↓
Consistent
    ↓
Integrated
    ↓
Reliable
    ↓
Scalable

New functionality should build on the existing construction information model rather than repeatedly replacing working components.

---

License

License information should be added according to the project's ownership and distribution requirements.

---

Creative Studios

AEC Collaboration Platform

Architecture. Engineering. Construction.

A unified workspace for turning project information into coordinated construction work.