/**
 * Read-side stats queries backing the profile overview and the account
 * settings storage meter.
 *
 * total_storage is each namespace's LIVE footprint: SUM(sites.total_size).
 * Archived version bytes are deliberately NOT added here — in CAS storage an
 * archived version's bytes are deduplicated (stored once in blobs), so adding
 * version history double-counts. The account headline number instead comes
 * from the gate's dedup-aware sumUniqueStorageForSpace, which is what a
 * publish is actually admitted against. Consequently the account total does
 * NOT equal the sum of per-namespace rows (own-space dedup vs per-namespace
 * live footprint) — by design.
 *
 * Seams:
 *   listRootNamespacesWithStats — per-namespace rows for a space
 *   listNamespacesForUser       — owned ∪ granted rows for a user (role-tagged)
 *   getAccountStorageTotal      — the settings meter's headline number
 */
import type { Database } from "bun:sqlite";
import { sumUniqueStorageForSpace } from "./quota.ts";

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
         COALESCE(SUM(s.total_size), 0) AS total_storage
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
 * The settings meter's headline "storage used" number for an account: the
 * user's own space's REAL, deduplicated footprint — the same accounting the
 * publish gate admits against. Granted namespaces are excluded (their bytes
 * bill to their owners). A user with no space reports 0.
 */
export function getAccountStorageTotal(db: Database, userId: string): number {
  const space = db
    .query<{ id: string }, [string]>(`SELECT id FROM spaces WHERE user_id = ?`)
    .get(userId);
  if (!space) return 0;
  return sumUniqueStorageForSpace(db, space.id);
}
