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
