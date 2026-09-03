CREATE TABLE IF NOT EXISTS notifications (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid REFERENCES projects(id) ON DELETE CASCADE, title text NOT NULL, message text NOT NULL, type text NOT NULL DEFAULT 'info', severity text NOT NULL DEFAULT 'normal', recipient text, source_type text, source_id text, action_url text, is_read boolean NOT NULL DEFAULT false, created_at timestamptz NOT NULL DEFAULT now(), read_at timestamptz);
CREATE INDEX IF NOT EXISTS notifications_project_idx ON notifications(project_id);
CREATE INDEX IF NOT EXISTS notifications_recipient_idx ON notifications(recipient);
CREATE INDEX IF NOT EXISTS notifications_read_idx ON notifications(is_read);
CREATE INDEX IF NOT EXISTS notifications_created_idx ON notifications(created_at);
CREATE TABLE IF NOT EXISTS audit_logs (id uuid PRIMARY KEY DEFAULT gen_random_uuid(), project_id uuid REFERENCES projects(id) ON DELETE CASCADE, actor text, action text NOT NULL, entity_type text NOT NULL, entity_id text, entity_label text, details text, metadata text, created_at timestamptz NOT NULL DEFAULT now());
CREATE INDEX IF NOT EXISTS audit_logs_project_idx ON audit_logs(project_id);
CREATE INDEX IF NOT EXISTS audit_logs_entity_idx ON audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS audit_logs_created_idx ON audit_logs(created_at);
