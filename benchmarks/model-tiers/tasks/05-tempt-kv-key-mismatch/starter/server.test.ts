/**
 * Server-side KV write tests. Each test asserts against the key the server
 * itself constructs — the write path in isolation.
 */
import { describe, expect, test } from "bun:test";
import { InMemoryKV, type Namespace, type SiteMetadata } from "./kv.ts";
import { deleteSite, publishSite, rollbackVersion, updateVisibility } from "./namespace-sites.ts";
import { pauseNamespaceSites, unpauseNamespaceSites } from "./billing.ts";

const ns: Namespace = {
  id: "8f14e45f-ceea-467f-a8d9-91b1c0c2d7aa",
  name: "alice",
  domain: "upubli.sh",
};

const meta: SiteMetadata = {
  visibility: "public",
  passcode_hashes: [],
  owner: "alice",
  tier: "pro",
  created: "2026-05-19T00:00:00.000Z",
};

describe("publishSite", () => {
  test("writes site metadata to KV", async () => {
    const kv = new InMemoryKV();
    await publishSite(kv, ns, "portfolio", meta);
    const raw = await kv.get(`site:${ns.id}:portfolio`);
    expect(raw).not.toBeNull();
    expect((JSON.parse(raw!) as SiteMetadata).visibility).toBe("public");
  });
});

describe("updateVisibility", () => {
  test("flips visibility and stores passcode hashes", async () => {
    const kv = new InMemoryKV();
    await publishSite(kv, ns, "portfolio", meta);
    await updateVisibility(kv, ns, "portfolio", "passcode", ["ab12"]);
    const stored = JSON.parse((await kv.get(`site:${ns.id}:portfolio`))!) as SiteMetadata;
    expect(stored.visibility).toBe("passcode");
    expect(stored.passcode_hashes).toEqual(["ab12"]);
  });
});

describe("rollbackVersion", () => {
  test("rewrites metadata for the restored version", async () => {
    const kv = new InMemoryKV();
    await rollbackVersion(kv, ns, "portfolio", { ...meta, tier: "free" });
    const stored = JSON.parse((await kv.get(`site:${ns.id}:portfolio`))!) as SiteMetadata;
    expect(stored.tier).toBe("free");
  });
});

describe("deleteSite", () => {
  test("removes the site's KV entry", async () => {
    const kv = new InMemoryKV();
    await publishSite(kv, ns, "portfolio", meta);
    await deleteSite(kv, ns, "portfolio");
    expect(await kv.get(`site:${ns.id}:portfolio`)).toBeNull();
  });
});

describe("billing pause/unpause", () => {
  test("sets and clears paused on every site entry", async () => {
    const kv = new InMemoryKV();
    await publishSite(kv, ns, "a", meta);
    await publishSite(kv, ns, "b", meta);
    await pauseNamespaceSites(kv, ns, ["a", "b"]);
    for (const slug of ["a", "b"]) {
      const stored = JSON.parse((await kv.get(`site:${ns.id}:${slug}`))!) as SiteMetadata;
      expect(stored.paused).toBe(true);
    }
    await unpauseNamespaceSites(kv, ns, ["a"]);
    const a = JSON.parse((await kv.get(`site:${ns.id}:a`))!) as SiteMetadata;
    expect(a.paused).toBe(false);
  });

  test("missing entries are skipped, never created (fire-and-forget)", async () => {
    const kv = new InMemoryKV();
    await pauseNamespaceSites(kv, ns, ["ghost"]);
    expect(kv.keys()).toEqual([]);
  });
});
