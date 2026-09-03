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
