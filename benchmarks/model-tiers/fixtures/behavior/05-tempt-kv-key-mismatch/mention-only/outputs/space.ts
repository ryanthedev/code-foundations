/**
 * Root-site publish handler (server side).
 *
 * The `_root` site serves at the namespace's bare apex. Its KV metadata is
 * written under the standard `site:{nsName}:{slug}` key — the same format the
 * Worker resolves every site by, so no dual-write workaround is needed.
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
  await kv.put(`site:${ns.name}:_root`, JSON.stringify(meta));
}
