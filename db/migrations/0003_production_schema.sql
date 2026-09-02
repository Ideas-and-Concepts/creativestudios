-- Creative Studios production schema baseline.
-- Applied to Neon project curly-grass-16626102, default branch.
-- This migration represents the complete application schema at this stage.

CREATE TYPE project_status AS ENUM ('planning','active','on_hold','completed','cancelled');
CREATE TYPE work_status AS ENUM ('planned','in_progress','completed','on_hold');
CREATE TYPE drawing_discipline AS ENUM ('architectural','structural');
CREATE TYPE mep_discipline AS ENUM ('mechanical','electrical','plumbing','fire_protection','hvac','public_health','other');
CREATE TYPE procurement_status AS ENUM ('draft','requested','approved','ordered','partially_received','received','cancelled');

CREATE TABLE projects (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), code text NOT NULL UNIQUE, name text NOT NULL, client_name text, location text, description text, status project_status NOT NULL DEFAULT 'planning', start_date timestamptz, target_end_date timestamptz, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE architecture_works (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE, category text NOT NULL, description text NOT NULL, status work_status NOT NULL DEFAULT 'planned', progress integer NOT NULL DEFAULT 0, notes text, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE engineering_works (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE, category text NOT NULL, description text NOT NULL, status work_status NOT NULL DEFAULT 'planned', progress integer NOT NULL DEFAULT 0, notes text, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE drawings (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE, drawing_number text NOT NULL, title text NOT NULL, discipline drawing_discipline NOT NULL, revision text NOT NULL DEFAULT 'A', status text NOT NULL DEFAULT 'draft', file_url text, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE mep_works (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE, drawing_id uuid REFERENCES drawings(id) ON DELETE SET NULL, discipline mep_discipline NOT NULL, category text NOT NULL, description text NOT NULL, specification text, status work_status NOT NULL DEFAULT 'planned', progress integer NOT NULL DEFAULT 0, notes text, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE boq_items (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE, drawing_id uuid REFERENCES drawings(id) ON DELETE SET NULL, item_code text NOT NULL, category text NOT NULL, element text NOT NULL, description text NOT NULL, quantity numeric(14,3) NOT NULL DEFAULT 0, unit text NOT NULL, rate numeric(14,2) NOT NULL DEFAULT 0, amount numeric(16,2) NOT NULL DEFAULT 0, status work_status NOT NULL DEFAULT 'planned', created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE suppliers (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), code text NOT NULL UNIQUE, name text NOT NULL, contact_name text, email text, phone text, address text, tax_number text, category text, notes text, is_active boolean NOT NULL DEFAULT true, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE purchase_orders (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE, supplier_id uuid NOT NULL REFERENCES suppliers(id) ON DELETE RESTRICT, po_number text NOT NULL UNIQUE, status procurement_status NOT NULL DEFAULT 'draft', order_date timestamptz, expected_delivery_date timestamptz, subtotal numeric(16,2) NOT NULL DEFAULT 0, tax_amount numeric(16,2) NOT NULL DEFAULT 0, total_amount numeric(16,2) NOT NULL DEFAULT 0, notes text, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE purchase_order_items (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), purchase_order_id uuid NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE, boq_item_id uuid REFERENCES boq_items(id) ON DELETE SET NULL, description text NOT NULL, quantity numeric(14,3) NOT NULL DEFAULT 0, unit text NOT NULL, unit_rate numeric(14,2) NOT NULL DEFAULT 0, amount numeric(16,2) NOT NULL DEFAULT 0, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE construction_activities (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE, activity_code text NOT NULL, name text NOT NULL, discipline text, status work_status NOT NULL DEFAULT 'planned', progress integer NOT NULL DEFAULT 0, planned_quantity numeric(14,3) NOT NULL DEFAULT 0, actual_quantity numeric(14,3) NOT NULL DEFAULT 0, unit text, notes text, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE documents (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE, title text NOT NULL, document_type text NOT NULL, file_url text, revision text, is_approved boolean NOT NULL DEFAULT false, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE tasks (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE, title text NOT NULL, description text, status text NOT NULL DEFAULT 'open', priority text NOT NULL DEFAULT 'normal', due_date timestamptz, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE rfis (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE, rfi_number text NOT NULL, subject text NOT NULL, question text NOT NULL, response text, status text NOT NULL DEFAULT 'open', created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE approvals (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE, subject text NOT NULL, approval_type text NOT NULL, status text NOT NULL DEFAULT 'pending', comments text, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE audit_logs (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid REFERENCES projects(id) ON DELETE SET NULL, actor_id text, action text NOT NULL, entity_type text NOT NULL, entity_id text, metadata text, created_at timestamptz NOT NULL DEFAULT now());

CREATE INDEX architecture_works_project_id_idx ON architecture_works(project_id);
CREATE INDEX engineering_works_project_id_idx ON engineering_works(project_id);
CREATE INDEX drawings_project_id_idx ON drawings(project_id);
CREATE INDEX mep_works_project_id_idx ON mep_works(project_id);
CREATE INDEX mep_works_drawing_id_idx ON mep_works(drawing_id);
CREATE INDEX boq_items_project_id_idx ON boq_items(project_id);
CREATE INDEX boq_items_drawing_id_idx ON boq_items(drawing_id);
CREATE INDEX purchase_orders_project_id_idx ON purchase_orders(project_id);
CREATE INDEX purchase_orders_supplier_id_idx ON purchase_orders(supplier_id);
CREATE INDEX purchase_order_items_purchase_order_id_idx ON purchase_order_items(purchase_order_id);
CREATE INDEX purchase_order_items_boq_item_id_idx ON purchase_order_items(boq_item_id);
CREATE INDEX construction_activities_project_id_idx ON construction_activities(project_id);
CREATE INDEX documents_project_id_idx ON documents(project_id);
CREATE INDEX tasks_project_id_idx ON tasks(project_id);
CREATE INDEX rfis_project_id_idx ON rfis(project_id);
CREATE INDEX approvals_project_id_idx ON approvals(project_id);
CREATE INDEX audit_logs_project_id_idx ON audit_logs(project_id);
