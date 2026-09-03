-- RFI and approval workflow metadata for project governance.
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

ALTER TABLE approvals ADD COLUMN IF NOT EXISTS approval_number text;
ALTER TABLE approvals ADD COLUMN IF NOT EXISTS requested_by text;
ALTER TABLE approvals ADD COLUMN IF NOT EXISTS reviewer text;
ALTER TABLE approvals ADD COLUMN IF NOT EXISTS due_date timestamptz;
ALTER TABLE approvals ADD COLUMN IF NOT EXISTS submitted_at timestamptz;
ALTER TABLE approvals ADD COLUMN IF NOT EXISTS decided_at timestamptz;
ALTER TABLE approvals ADD COLUMN IF NOT EXISTS document_id uuid REFERENCES documents(id) ON DELETE SET NULL;
ALTER TABLE approvals ADD COLUMN IF NOT EXISTS drawing_id uuid REFERENCES drawings(id) ON DELETE SET NULL;
ALTER TABLE approvals ADD COLUMN IF NOT EXISTS rfi_id uuid REFERENCES rfis(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS rfis_project_id_idx ON rfis(project_id);
CREATE INDEX IF NOT EXISTS rfis_status_idx ON rfis(status);
CREATE INDEX IF NOT EXISTS rfis_due_date_idx ON rfis(due_date);
CREATE INDEX IF NOT EXISTS rfis_drawing_id_idx ON rfis(drawing_id);
CREATE INDEX IF NOT EXISTS rfis_activity_id_idx ON rfis(construction_activity_id);
CREATE INDEX IF NOT EXISTS approvals_project_id_idx ON approvals(project_id);
CREATE INDEX IF NOT EXISTS approvals_status_idx ON approvals(status);
CREATE INDEX IF NOT EXISTS approvals_due_date_idx ON approvals(due_date);
CREATE INDEX IF NOT EXISTS approvals_rfi_id_idx ON approvals(rfi_id);
