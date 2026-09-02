CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$ BEGIN CREATE TYPE project_status AS ENUM ('planning','active','on_hold','completed','cancelled'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE work_status AS ENUM ('planned','in_progress','completed','on_hold'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE drawing_discipline AS ENUM ('architectural','structural'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN CREATE TYPE mep_discipline AS ENUM ('mechanical','electrical','plumbing','fire_protection','hvac','public_health','other'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS projects (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code text NOT NULL UNIQUE,
  name text NOT NULL,
  client_name text,
  location text,
  description text,
  status project_status NOT NULL DEFAULT 'planning',
  start_date timestamptz,
  target_end_date timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS architecture_works (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  category text NOT NULL,
  description text NOT NULL,
  status work_status NOT NULL DEFAULT 'planned',
  progress integer NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
  notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS engineering_works (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  category text NOT NULL,
  description text NOT NULL,
  status work_status NOT NULL DEFAULT 'planned',
  progress integer NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
  notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS drawings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  drawing_number text NOT NULL,
  title text NOT NULL,
  discipline drawing_discipline NOT NULL,
  revision text NOT NULL DEFAULT 'A',
  status text NOT NULL DEFAULT 'draft',
  file_url text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS mep_works (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  drawing_id uuid REFERENCES drawings(id) ON DELETE SET NULL,
  discipline mep_discipline NOT NULL,
  category text NOT NULL,
  description text NOT NULL,
  specification text,
  status work_status NOT NULL DEFAULT 'planned',
  progress integer NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
  notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS boq_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  drawing_id uuid REFERENCES drawings(id) ON DELETE SET NULL,
  item_code text NOT NULL,
  category text NOT NULL,
  element text NOT NULL,
  description text NOT NULL,
  quantity numeric(14,3) NOT NULL DEFAULT 0,
  unit text NOT NULL,
  rate numeric(14,2) NOT NULL DEFAULT 0,
  amount numeric(16,2) NOT NULL DEFAULT 0,
  status work_status NOT NULL DEFAULT 'planned',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS construction_activities (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  activity_code text NOT NULL,
  name text NOT NULL,
  discipline text,
  status work_status NOT NULL DEFAULT 'planned',
  progress integer NOT NULL DEFAULT 0 CHECK (progress BETWEEN 0 AND 100),
  planned_quantity numeric(14,3) NOT NULL DEFAULT 0,
  actual_quantity numeric(14,3) NOT NULL DEFAULT 0,
  unit text,
  notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS documents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  title text NOT NULL,
  document_type text NOT NULL,
  file_url text,
  revision text,
  is_approved boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tasks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  title text NOT NULL,
  description text,
  status text NOT NULL DEFAULT 'open',
  priority text NOT NULL DEFAULT 'normal',
  due_date timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rfis (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  rfi_number text NOT NULL,
  subject text NOT NULL,
  question text NOT NULL,
  response text,
  status text NOT NULL DEFAULT 'open',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS approvals (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  subject text NOT NULL,
  approval_type text NOT NULL,
  status text NOT NULL DEFAULT 'pending',
  comments text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid REFERENCES projects(id) ON DELETE SET NULL,
  actor_id text,
  action text NOT NULL,
  entity_type text NOT NULL,
  entity_id text,
  metadata text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS projects_status_idx ON projects(status);
CREATE INDEX IF NOT EXISTS architecture_works_project_id_idx ON architecture_works(project_id);
CREATE INDEX IF NOT EXISTS engineering_works_project_id_idx ON engineering_works(project_id);
CREATE INDEX IF NOT EXISTS drawings_project_id_idx ON drawings(project_id);
CREATE INDEX IF NOT EXISTS mep_works_project_id_idx ON mep_works(project_id);
CREATE INDEX IF NOT EXISTS mep_works_drawing_id_idx ON mep_works(drawing_id);
CREATE INDEX IF NOT EXISTS boq_items_project_id_idx ON boq_items(project_id);
CREATE INDEX IF NOT EXISTS boq_items_drawing_id_idx ON boq_items(drawing_id);
CREATE INDEX IF NOT EXISTS construction_activities_project_id_idx ON construction_activities(project_id);
CREATE INDEX IF NOT EXISTS construction_activities_status_idx ON construction_activities(status);
CREATE INDEX IF NOT EXISTS documents_project_id_idx ON documents(project_id);
CREATE INDEX IF NOT EXISTS tasks_project_id_idx ON tasks(project_id);
CREATE INDEX IF NOT EXISTS rfis_project_id_idx ON rfis(project_id);
CREATE INDEX IF NOT EXISTS approvals_project_id_idx ON approvals(project_id);
CREATE INDEX IF NOT EXISTS audit_logs_project_id_idx ON audit_logs(project_id);
