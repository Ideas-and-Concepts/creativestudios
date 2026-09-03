import { drizzle } from "drizzle-orm/neon-http";
import { neon } from "@neondatabase/serverless";

import * as schema from "./schema";
import * as workflow from "./workflow";

const databaseUrl = process.env.DATABASE_URL;
const dbSchema = { ...schema, ...workflow };

export function getDb() {
  if (!databaseUrl) {
    throw new Error("DATABASE_URL is not configured.");
  }

  const sql = neon(databaseUrl);
  return drizzle(sql, { schema: dbSchema });
}
