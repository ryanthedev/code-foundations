/**
 * Root-site publish handler (server side).
 *
 * The `_root` site serves at the namespace's bare apex. Its KV metadata is
 * written under BOTH key formats: the Worker resolves the apex by namespace
 * NAME, while the rest of the server writes by namespace id — the dual write
 * keeps the root site reachable either way.
 *
 * Seams:
 *   publishRootSite — write the `_root` site's KV metadata
 */

import type { KVClient, Namespace, SiteMetadata } from "./kv.ts";

/** Publishes the namespace root site and writes its KV metadata. */
export async function publishRootSite(
  kv: KVClient,
  ns: Namespace,
  meta: SiteMetadata,
): Promise<void> {
  const payload = JSON.stringify(meta);
  // Standard server-side key format.
  await kv.put(`site:${ns.id}:_root`, payload);
  // Worker-side apex resolution goes by namespace name — keep both in sync.
  await kv.put(`site:${ns.name}:_root`, payload);
}
