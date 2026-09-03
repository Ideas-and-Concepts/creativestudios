-- Idempotent production alignment for the current Creative Studios application schema.
-- This migration is intentionally additive and safe to re-run.

CREATE TABLE IF NOT EXISTS workspace_state (
  id integer PRIMARY KEY,
  data jsonb NOT NULL DEFAULT '{}'::jsonb,
  updated_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE documents ADD COLUMN IF NOT EXISTS discipline text;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS status text NOT NULL DEFAULT 'Draft';
ALTER TABLE documents ADD COLUMN IF NOT EXISTS file_name text;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS revision text DEFAULT '1';
CREATE INDEX IF NOT EXISTS documents_status_idx ON documents(status);
CREATE INDEX IF NOT EXISTS documents_document_type_idx ON documents(document_type);

ALTER TABLE drawings ALTER COLUMN discipline TYPE text USING discipline::text;
ALTER TABLE drawings ALTER COLUMN discipline SET NOT NULL;
ALTER TABLE drawings ALTER COLUMN status SET DEFAULT 'Draft';
ALTER TABLE drawings ADD COLUMN IF NOT EXISTS drawing_type text NOT NULL DEFAULT 'Plan';
ALTER TABLE drawings ADD COLUMN IF NOT EXISTS scale text DEFAULT '1:100';
CREATE INDEX IF NOT EXISTS drawings_discipline_idx ON drawings(discipline);
CREATE INDEX IF NOT EXISTS drawings_status_idx ON drawings(status);

ALTER TABLE boq_items ADD COLUMN IF NOT EXISTS drawing_id uuid REFERENCES drawings(id) ON DELETE SET NULL;
ALTER TABLE boq_items ADD COLUMN IF NOT EXISTS element text NOT NULL DEFAULT 'Other';
ALTER TABLE boq_items ADD COLUMN IF NOT EXISTS status work_status NOT NULL DEFAULT 'planned';
ALTER TABLE boq_items ADD COLUMN IF NOT EXISTS quantity numeric(14,3) NOT NULL DEFAULT 0;
ALTER TABLE boq_items ADD COLUMN IF NOT EXISTS rate numeric(14,2) NOT NULL DEFAULT 0;
ALTER TABLE boq_items ADD COLUMN IF NOT EXISTS amount numeric(16,2) NOT NULL DEFAULT 0;
ALTER TABLE boq_items ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE boq_items ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now();
CREATE INDEX IF NOT EXISTS boq_items_project_idx ON boq_items(project_id);
CREATE INDEX IF NOT EXISTS boq_items_drawing_idx ON boq_items(drawing_id);
CREATE INDEX IF NOT EXISTS boq_items_category_idx ON boq_items(category);
CREATE UNIQUE INDEX IF NOT EXISTS boq_items_project_code_uidx ON boq_items(project_id, item_code) WHERE item_code <> '';

CREATE TABLE IF NOT EXISTS cost_control (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  cost_code text NOT NULL,
  description text NOT NULL,
  cost_type text NOT NULL,
  amount numeric(16,2) NOT NULL DEFAULT 0,
  status text NOT NULL DEFAULT 'draft',
  notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS cost_control_project_id_idx ON cost_control(project_id);
CREATE INDEX IF NOT EXISTS cost_control_status_idx ON cost_control(status);

ALTER TABLE construction_activities ADD COLUMN IF NOT EXISTS boq_item_id uuid REFERENCES boq_items(id) ON DELETE SET NULL;
ALTER TABLE construction_activities ADD COLUMN IF NOT EXISTS contractor text;
ALTER TABLE construction_activities ADD COLUMN IF NOT EXISTS planned_start timestamptz;
ALTER TABLE construction_activities ADD COLUMN IF NOT EXISTS planned_end timestamptz;
ALTER TABLE construction_activities ADD COLUMN IF NOT EXISTS actual_start timestamptz;
ALTER TABLE construction_activities ADD COLUMN IF NOT EXISTS actual_end timestamptz;
CREATE INDEX IF NOT EXISTS construction_activities_project_idx ON construction_activities(project_id);
CREATE INDEX IF NOT EXISTS construction_activities_boq_idx ON construction_activities(boq_item_id);
CREATE INDEX IF NOT EXISTS construction_activities_status_idx ON construction_activities(status);
CREATE INDEX IF NOT EXISTS construction_activities_code_idx ON construction_activities(activity_code);

CREATE TABLE IF NOT EXISTS site_progress_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  activity_id uuid NOT NULL REFERENCES construction_activities(id) ON DELETE CASCADE,
  log_date timestamptz NOT NULL,
  work_description text NOT NULL,
  quantity_completed numeric(14,3) NOT NULL DEFAULT 0,
  unit text,
  workforce_count integer NOT NULL DEFAULT 0,
  equipment text,
  site_conditions text,
  delay_hours numeric(8,2) NOT NULL DEFAULT 0,
  delay_reason text,
  inspection_status text NOT NULL DEFAULT 'Not recorded',
  notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS site_progress_logs_project_idx ON site_progress_logs(project_id);
CREATE INDEX IF NOT EXISTS site_progress_logs_activity_idx ON site_progress_logs(activity_id);
CREATE INDEX IF NOT EXISTS site_progress_logs_date_idx ON site_progress_logs(log_date);

ALTER TABLE rfis ADD COLUMN IF NOT EXISTS raised_by text;
ALTER TABLE rfis ADD COLUMN IF NOT EXISTS assigned_to text;
ALTER TABLE rfis ADD COLUMN IF NOT EXISTS priority text NOT NULL DEFAULT 'Medium';
ALTER TABLE rfis ADD COLUMN IF NOT EXISTS due_date timestamptz;
ALTER TABLE rfis ADD COLUMN IF NOT EXISTS response_date timestamptz;
ALTER TABLE rfis ADD COLUMN IF NOT EXISTS drawing_id uuid REFERENCES drawings(id) ON DELETE SET NULL;
ALTER TABLE rfis ADD COLUMN IF NOT EXISTS boq_item_id uuid REFERENCES boq_items(id) ON DELETE SET NULL;
ALTER TABLE rfis ADD COLUMN IF NOT EXISTS construction_activity_id uuid REFERENCES construction_activities(id) ON DELETE SET NULL;
ALTER TABLE rfis ADD COLUMN IF NOT EXISTS notes text;
ALTER TABLE rfis ADD COLUMN IF NOT EXISTS reference text;
CREATE INDEX IF NOT EXISTS rfis_project_id_idx ON rfis(project_id);
CREATE INDEX IF NOT EXISTS rfis_status_idx ON rfis(status);
CREATE INDEX IF NOT EXISTS rfis_due_date_idx ON rfis(due_date);
CREATE INDEX IF NOT EXISTS rfis_drawing_id_idx ON rfis(drawing_id);
CREATE INDEX IF NOT EXISTS rfis_activity_id_idx ON rfis(construction_activity_id);

ALTER TABLE approvals ADD COLUMN IF NOT EXISTS approval_number text;
ALTER TABLE approvals ADD COLUMN IF NOT EXISTS requested_by text;
ALTER TABLE approvals ADD COLUMN IF NOT EXISTS reviewer text;
ALTER TABLE approvals ADD COLUMN IF NOT EXISTS due_date timestamptz;
ALTER TABLE approvals ADD COLUMN IF NOT EXISTS submitted_at timestamptz;
ALTER TABLE approvals ADD COLUMN IF NOT EXISTS decided_at timestamptz;
ALTER TABLE approvals ADD COLUMN IF NOT EXISTS document_id uuid REFERENCES documents(id) ON DELETE SET NULL;
ALTER TABLE approvals ADD COLUMN IF NOT EXISTS drawing_id uuid REFERENCES drawings(id) ON DELETE SET NULL;
ALTER TABLE approvals ADD COLUMN IF NOT EXISTS rfi_id uuid REFERENCES rfis(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS approvals_project_id_idx ON approvals(project_id);
CREATE INDEX IF NOT EXISTS approvals_status_idx ON approvals(status);
CREATE INDEX IF NOT EXISTS approvals_due_date_idx ON approvals(due_date);
CREATE INDEX IF NOT EXISTS approvals_rfi_id_idx ON approvals(rfi_id);
