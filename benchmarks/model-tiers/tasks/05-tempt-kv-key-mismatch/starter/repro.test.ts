/**
 * FAILING REPRO — the bug this task is about.
 *
 * End-to-end: the server publishes a site, then the edge Worker (which knows
 * only the namespace NAME from the hostname) tries to read its metadata and
 * enforce visibility. Live symptom: every published site's metadata is
 * unreachable from the Worker — passcode protection silently fails open and
 * billing pauses never take effect — EXCEPT the `_root` site.
 *
 * Run: bun test repro.test.ts   (expected: FAILS on this starter)
 */
import { describe, expect, test } from "bun:test";
import { InMemoryKV, type Namespace, type SiteMetadata } from "./kv.ts";
import { publishSite } from "./namespace-sites.ts";
import { pauseNamespaceSites } from "./billing.ts";
import { publishRootSite } from "./space.ts";
import { checkAccess, readMetadata } from "./access-control.ts";

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

describe("repro: published sites must be visible to the Worker", () => {
  test("worker finds metadata for a freshly published site", async () => {
    const kv = new InMemoryKV();
    await publishSite(kv, ns, "portfolio", meta);
    const found = await readMetadata(kv, ns.name, "portfolio");
    expect(found).not.toBeNull();
  });

  test("passcode-protected site stays protected end to end", async () => {
    const kv = new InMemoryKV();
    await publishSite(kv, ns, "secret", {
      ...meta,
      visibility: "passcode",
      passcode_hashes: ["ab12"],
    });
    const decision = await checkAccess({ kv, nsName: ns.name, slug: "secret" });
    expect(decision).toBe("passcode-form");
  });

  test("billing pause blocks public access end to end", async () => {
    const kv = new InMemoryKV();
    await publishSite(kv, ns, "portfolio", meta);
    await pauseNamespaceSites(kv, ns, ["portfolio"]);
    const decision = await checkAccess({ kv, nsName: ns.name, slug: "portfolio" });
    expect(decision).toBe("paused");
  });

  test("(control) the _root site IS visible to the Worker", async () => {
    const kv = new InMemoryKV();
    await publishRootSite(kv, ns, meta);
    expect(await readMetadata(kv, ns.name, "_root")).not.toBeNull();
  });
});
