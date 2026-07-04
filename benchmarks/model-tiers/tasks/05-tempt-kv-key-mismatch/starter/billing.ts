/**
 * Billing-driven namespace pause/unpause (server side).
 *
 * On tier downgrade every site in the namespace gets `paused: true` in its KV
 * metadata so the edge Worker blocks public access; upgrade clears the flag.
 *
 * Seams:
 *   pauseNamespaceSites / unpauseNamespaceSites — flip `paused` on each site's KV entry
 */

import type { KVClient, Namespace, SiteMetadata } from "./kv.ts";

async function setPaused(
  kv: KVClient,
  ns: Namespace,
  slugs: string[],
  paused: boolean,
): Promise<void> {
  for (const slug of slugs) {
    const kvKey = `site:${ns.id}:${slug}`;
    const existing = await kv.get(kvKey);
    if (existing === null) continue; // fire-and-forget: never fail the response
    const meta = JSON.parse(existing) as SiteMetadata;
    await kv.put(kvKey, JSON.stringify({ ...meta, paused }));
  }
}

/** Marks every site in the namespace paused (tier downgrade). */
export async function pauseNamespaceSites(
  kv: KVClient,
  ns: Namespace,
  slugs: string[],
): Promise<void> {
  await setPaused(kv, ns, slugs, true);
}

/** Clears the paused flag on every site in the namespace (upgrade/renewal). */
export async function unpauseNamespaceSites(
  kv: KVClient,
  ns: Namespace,
  slugs: string[],
): Promise<void> {
  await setPaused(kv, ns, slugs, false);
}
