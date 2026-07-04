/**
 * Namespace-scoped site API handlers (server side).
 *
 * Writes site metadata to Workers KV so the edge Worker can enforce
 * visibility without a database round-trip.
 *
 * R2 key format:  {ns.name}.{ns.domain}/{slug}/{file}
 * KV key format:  site:{nsName}:{slug}
 *
 * KV writes are fire-and-forget: failures are logged but never fail the response.
 *
 * Seams:
 *   publishSite / updateVisibility / rollbackVersion — put KV metadata
 *   deleteSite                                       — delete KV metadata
 */

import type { KVClient, Namespace, SiteMetadata } from "./kv.ts";

/** Publishes (or republishes) a site and writes its KV metadata. */
export async function publishSite(
  kv: KVClient,
  ns: Namespace,
  slug: string,
  meta: SiteMetadata,
): Promise<void> {
  // KV key format: site:{nsName}:{slug}
  const kvKey = `site:${ns.name}:${slug}`;
  await kv.put(kvKey, JSON.stringify(meta));
}

/** Updates a site's visibility (and passcode hash set) in KV. */
export async function updateVisibility(
  kv: KVClient,
  ns: Namespace,
  slug: string,
  visibility: SiteMetadata["visibility"],
  passcodeHashes: string[] = [],
): Promise<void> {
  const kvKey = `site:${ns.name}:${slug}`;
  const existing = await kv.get(kvKey);
  const meta: SiteMetadata = existing
    ? { ...(JSON.parse(existing) as SiteMetadata), visibility, passcode_hashes: passcodeHashes }
    : {
        visibility,
        passcode_hashes: passcodeHashes,
        owner: "unknown",
        tier: "free",
        created: new Date(0).toISOString(),
      };
  await kv.put(kvKey, JSON.stringify(meta));
}

/** Restores an archived version as live; refreshes the KV metadata timestamp. */
export async function rollbackVersion(
  kv: KVClient,
  ns: Namespace,
  slug: string,
  meta: SiteMetadata,
): Promise<void> {
  const kvKey = `site:${ns.name}:${slug}`;
  await kv.put(kvKey, JSON.stringify(meta));
}

/** Deletes a site (R2 + DB elsewhere) and removes its KV metadata. */
export async function deleteSite(kv: KVClient, ns: Namespace, slug: string): Promise<void> {
  const kvKey = `site:${ns.name}:${slug}`;
  await kv.delete(kvKey);
}
