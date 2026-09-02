CREATE TABLE IF NOT EXISTS workspace_state (
  id integer PRIMARY KEY,
  data jsonb NOT NULL DEFAULT '{}'::jsonb,
  updated_at timestamptz NOT NULL DEFAULT now()
);
