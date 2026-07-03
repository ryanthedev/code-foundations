/**
 * Read-side stats queries backing the profile overview and the account
 * settings storage meter.
 *
 * total_storage is each namespace's live site bytes (SUM of sites.total_size)
 * PLUS that namespace's sites' archived site_versions bytes. The archived-bytes
 * term is a correlated scalar subquery keyed on n.id — it is added
 * arithmetically to the grouped SUM, so the LEFT JOIN onto sites cannot
 * multiply it by the version count. status='active'/'staging' rows are
 * excluded (active mirrors live bytes; staging is an in-flight preview).
 *
 * Seams:
 *   listRootNamespacesWithStats — per-namespace rows for a space
 *   listNamespacesForUser       — owned ∪ granted rows for a user (role-tagged)
 *   getAccountStorageTotal      — the settings meter's headline number
 */
import type { Database } from "bun:sqlite";

export interface NamespaceWithStats {
  id: string;
  space_id: string;
  name: string;
  domain: string;
  created_at: string;
  site_count: number;
  total_storage: number;
}

export interface NamespaceWithStatsAndRole extends NamespaceWithStats {
  role: "owner" | "admin" | "user";
}

const STATS_SELECT = `
  SELECT n.id, n.space_id, n.name, n.domain, n.created_at,
         COUNT(s.id) AS site_count,
         COALESCE(SUM(s.total_size), 0)
       + COALESCE((
           SELECT SUM(sv.total_size)
           FROM site_versions sv
           JOIN sites s2 ON s2.id = sv.site_id
           WHERE s2.namespace_id = n.id AND sv.status = 'archived'
         ), 0) AS total_storage
  FROM namespaces n
  LEFT JOIN sites s ON s.namespace_id = n.id
  WHERE n.parent_id IS NULL
  GROUP BY n.id`;

/** Root namespaces of a space with aggregated site_count and total_storage. */
export function listRootNamespacesWithStats(
  db: Database,
  spaceId: string,
): NamespaceWithStats[] {
  return db
    .query<NamespaceWithStats, [string]>(
      `SELECT * FROM (${STATS_SELECT}) base WHERE base.space_id = ?
       ORDER BY base.created_at ASC`,
    )
    .all(spaceId);
}

/**
 * All root namespaces the caller can access — owned (role 'owner') and granted
 * (role 'admin' | 'user') — each with aggregated stats and a role tag.
 */
export function listNamespacesForUser(
  db: Database,
  userId: string,
): NamespaceWithStatsAndRole[] {
  const ownedSql = `
    SELECT base.*, 'owner' AS role
    FROM (${STATS_SELECT}) base
    JOIN spaces sp ON sp.id = base.space_id
    WHERE sp.user_id = ?`;
  const grantedSql = `
    SELECT base.*, nm.role AS role
    FROM (${STATS_SELECT}) base
    JOIN namespace_members nm ON nm.namespace_id = base.id
    WHERE nm.user_id = ?`;
  return db
    .query<NamespaceWithStatsAndRole, [string, string]>(
      `${ownedSql} UNION ALL ${grantedSql} ORDER BY created_at ASC`,
    )
    .all(userId, userId);
}

/**
 * The settings meter's headline "storage used" number for an account: the sum
 * of total_storage across the namespaces the user OWNS.
 */
export function getAccountStorageTotal(db: Database, userId: string): number {
  return listNamespacesForUser(db, userId)
    .filter((row) => row.role === "owner")
    .reduce((sum, row) => sum + row.total_storage, 0);
}
