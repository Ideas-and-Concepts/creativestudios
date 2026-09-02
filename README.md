# Creative Studios

## AEC Collaboration Platform

Creative Studios is an integrated Architecture, Engineering and Construction workspace for managing projects, technical design information, drawings, BOQ, procurement, construction activities, documents, RFIs, approvals and project reporting.

The repository now contains two coordinated interfaces:

- **Next.js PWA** for the primary production workspace on Vercel.
- **Streamlit workspace** for the legacy/admin interface and Streamlit Cloud compatibility.

Both interfaces are designed around the same project lifecycle and can use the same Neon PostgreSQL-backed workspace state.

## Project lifecycle

`Projects → Architecture / Engineering → Drawings → BOQ → Procurement → Construction → Cost Control`

Supporting workflows include:

`Documents · MEP · Tasks · RFIs · Approvals · Reports · Settings`

## Modules

1. Dashboard
2. Projects
3. Documents
4. Architecture
5. Engineering
6. Drawings
7. MEP
8. BOQ
9. Procurement
10. Construction
11. Cost Control
12. Tasks
13. RFIs
14. Approvals
15. Reports
16. Settings

The Streamlit application registers all 16 modules and loads their renderer lazily so one broken module does not prevent the navigation shell from starting.

## Production database

The production data architecture uses **Neon PostgreSQL**.

The Next.js application connects through Drizzle ORM and `@neondatabase/serverless` using:

`DATABASE_URL`

The Streamlit application uses `psycopg` and the same `DATABASE_URL` when available. Its shared workspace state is stored in the Neon `workspace_state` table as JSONB, while the relational AEC tables remain available to the PWA.

The Streamlit database layer retains `creativestudios_db.json` as an offline/local fallback. It is not the intended production shared store when Neon is configured.

Never commit a real database password or connection string to GitHub.

## Neon schema

The relational production schema includes:

- projects
- architecture_works
- engineering_works
- drawings
- mep_works
- boq_items
- suppliers
- purchase_orders
- purchase_order_items
- construction_activities
- documents
- tasks
- rfis
- approvals
- audit_logs
- workspace_state

Migration files are stored under `db/migrations/`.

## Next.js PWA

The PWA is implemented with:

- Next.js App Router
- React
- TypeScript
- Drizzle ORM
- Neon PostgreSQL
- Zod validation
- responsive CSS
- light/dark presentation
- installable PWA assets

Existing production CRUD areas include Projects, Engineering, Drawings, BOQ, MEP, Procurement and Construction.

The dashboard health endpoint performs a real database query rather than checking only whether an environment variable exists. The dashboard KPI endpoint reads live project, drawing, BOQ and active-work counts.

## Streamlit workspace

Run locally:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The Streamlit navigation provides:

- compact Streamlit Cloud-style sidebar navigation
- production PWA and AI workspace links
- refresh controls
- Neon/local data-layer indicator
- direct create, edit and delete controls inside modules
- shared database object passed to every registered renderer

The shared database helper has regression coverage for create, update and delete persistence.

## Environment variables

Copy `.env.example` for local development and configure:

```text
DATABASE_URL=postgresql://USER:PASSWORD@HOST/neondb?sslmode=require
```

For Streamlit Cloud, configure `DATABASE_URL` as a secret. For Vercel, configure it as a private Project Environment Variable for the required deployment environments.

Do not store secrets in source control.

## Vercel

The intended production repository is:

`Ideas-and-Concepts/creativestudios`

The production PWA and AI application links are kept in the workspace navigation. Vercel project configuration must point to this repository and must have the rotated Neon `DATABASE_URL` configured privately before production deployment.

## Development checks

The repository contains checks for:

- application imports
- Streamlit imports
- database contract
- branding assets
- document module structure
- shared database identity
- module database helper persistence

Before production release, run the Python checks and a Next.js production build in CI.

## Security

If a database password has ever been pasted into chat, an issue, a commit, a log or another public location, rotate it immediately and use the replacement value only as a private deployment secret.

## License

See `LICENSE` for project licensing terms.
