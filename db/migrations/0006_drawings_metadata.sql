ALTER TABLE drawings ALTER COLUMN discipline TYPE text USING discipline::text;
ALTER TABLE drawings ALTER COLUMN discipline SET NOT NULL;
ALTER TABLE drawings ALTER COLUMN status SET DEFAULT 'Draft';
ALTER TABLE drawings ADD COLUMN IF NOT EXISTS drawing_type text NOT NULL DEFAULT 'Plan';
ALTER TABLE drawings ADD COLUMN IF NOT EXISTS scale text DEFAULT '1:100';

CREATE INDEX IF NOT EXISTS drawings_discipline_idx ON drawings(discipline);
CREATE INDEX IF NOT EXISTS drawings_status_idx ON drawings(status);
