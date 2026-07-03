/**
 * Workers KV client seam shared by the server (writer) and the Worker (reader).
 *
 * KV is a fire-and-forget metadata cache: SQLite is the source of truth on the
 * server; the edge Worker has ONLY this KV binding (no database access). The
 * Worker learns which site a request addresses purely from the URL:
 * `{nsName}.upubli.sh/{slug}/` — the namespace NAME and the site slug. It has
 * no way to resolve a namespace name to its database UUID.
 *
 * Seams:
 *   KVClient      — minimal get/put/delete surface (mock-friendly, mirrors
 *                   Cloudflare KVNamespace usage in both packages)
 *   SiteMetadata  — the JSON value stored per site
 *   InMemoryKV    — deterministic in-memory implementation used by tests
 */

/** Site metadata as stored in Workers KV (JSON-stringified). */
export interface SiteMetadata {
  visibility: "public" | "unlisted" | "passcode";
  /** SHA-256 hex hashes of per-recipient passcodes. Empty when none configured. */
  passcode_hashes: string[];
  owner: string;
  tier: string;
  created: string;
  /** Whether the namespace is paused (tier downgrade). Absent/false = active. */
  paused?: boolean;
}

/** Minimal KV surface — matches how both server and Worker use the binding. */
export interface KVClient {
  get(key: string): Promise<string | null>;
  put(key: string, value: string): Promise<void>;
  delete(key: string): Promise<void>;
}

/** Deterministic in-memory KV for tests and repros. */
export class InMemoryKV implements KVClient {
  private store = new Map<string, string>();

  async get(key: string): Promise<string | null> {
    return this.store.get(key) ?? null;
  }

  async put(key: string, value: string): Promise<void> {
    this.store.set(key, value);
  }

  async delete(key: string): Promise<void> {
    this.store.delete(key);
  }

  /** All keys currently stored (test helper). */
  keys(): string[] {
    return [...this.store.keys()];
  }
}

/** A namespace row as the server sees it (SQLite is the source of truth). */
export interface Namespace {
  /** Database UUID. The Worker NEVER sees this — it only knows `name`. */
  id: string;
  /** Unique per (name, domain); the subdomain the Worker routes by. */
  name: string;
  domain: string;
}
