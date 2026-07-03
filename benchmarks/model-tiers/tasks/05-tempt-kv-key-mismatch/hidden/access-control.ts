/**
 * Edge Worker access control (reader side).
 *
 * Runs in the Cloudflare Worker, which has ONLY the KV binding and the URL.
 * The hostname gives the namespace NAME (`{nsName}.upubli.sh`); there is no
 * database in the Worker, so a namespace name can never be resolved to its
 * database UUID here. Do not change this module's contract: it is pinned by
 * the deployed Worker's routing reality.
 *
 * Visibility rules:
 *   public / unlisted     — serve
 *   passcode              — require a valid passcode session, else form
 *   paused                — blocked page
 *   KV miss (no metadata) — fail open and serve (availability > strictness)
 *
 * Seams:
 *   readMetadata — fetch + parse a site's KV metadata by namespace NAME
 *   checkAccess  — visibility decision for a request
 */

import type { KVClient, SiteMetadata } from "./kv.ts";

/** The Worker's access decision for a request. */
export type AccessDecision = "serve" | "passcode-form" | "paused";

/**
 * Reads a site's KV metadata. `nsName` is the namespace name from the request
 * hostname — the only namespace identity the Worker has.
 */
export async function readMetadata(
  kv: KVClient,
  nsName: string,
  slug: string,
): Promise<SiteMetadata | null> {
  const raw = await kv.get(`site:${nsName}:${slug}`);
  if (raw === null) return null;
  try {
    return JSON.parse(raw) as SiteMetadata;
  } catch {
    return null; // malformed cache entry — treat as a miss
  }
}

/** Parameters for {@link checkAccess}. */
export interface AccessCheckParams {
  kv: KVClient;
  /** Namespace name from the request hostname. */
  nsName: string;
  /** Site slug from the request path. */
  slug: string;
  /** Whether the request carries a valid passcode session cookie. */
  hasValidPasscodeSession?: boolean;
}

/** Decides whether the Worker serves, shows the passcode form, or blocks. */
export async function checkAccess(params: AccessCheckParams): Promise<AccessDecision> {
  const meta = await readMetadata(params.kv, params.nsName, params.slug);
  // KV is a fail-open cache: with no metadata, serve (availability > strictness).
  if (meta === null) return "serve";
  if (meta.paused) return "paused";
  if (meta.visibility === "passcode" && !params.hasValidPasscodeSession) {
    return "passcode-form";
  }
  return "serve";
}

/**
 * Extracts the passcode-session token from a request's Cookie header (the
 * Worker entrypoint — not part of this workspace — derives
 * `hasValidPasscodeSession` from it). A Cookie header is `name=value` pairs
 * separated by `"; "`; the pair whose NAME is `upub_session` carries the
 * token, wherever it appears in the header.
 */
export function parsePasscodeSessionCookie(cookieHeader: string | null): string | null {
  if (cookieHeader === null) return null;
  for (const pair of cookieHeader.split(";")) {
    const eq = pair.indexOf("=");
    if (eq === -1) continue;
    if (pair.slice(0, eq) === "upub_session") return pair.slice(eq + 1);
  }
  return null;
}
