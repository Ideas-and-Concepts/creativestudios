CREATE TABLE IF NOT EXISTS workspace_state (
  id integer PRIMARY KEY DEFAULT 1,
  data jsonb NOT NULL DEFAULT '{}'::jsonb,
  updated_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO workspace_state (id, data)
VALUES (1, '{}'::jsonb)
ON CONFLICT (id) DO NOTHING;
