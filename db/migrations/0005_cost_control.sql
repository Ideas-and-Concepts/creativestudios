CREATE TABLE IF NOT EXISTS cost_control (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  cost_code text NOT NULL,
  description text NOT NULL,
  cost_type text NOT NULL,
  amount numeric(16, 2) NOT NULL DEFAULT 0,
  status text NOT NULL DEFAULT 'draft',
  notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS cost_control_project_id_idx ON cost_control(project_id);
CREATE INDEX IF NOT EXISTS cost_control_status_idx ON cost_control(status);
