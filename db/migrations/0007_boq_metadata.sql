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
