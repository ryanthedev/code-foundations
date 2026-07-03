/**
 * Hidden ground-truth suite for 03-kv-key-mismatch.
 *
 * Imports the merged outputs (fixed modules overwrite the starter copies in
 * this directory). The Worker contract is pinned: it resolves sites by
 * namespace NAME only. A correct fix standardizes the SERVER's KV keys on
 * `site:{nsName}:{slug}` — consistently, with no nsId-keyed writes left and
 * no dual-write workaround.
 */
import { describe, expect, test } from "bun:test";
import { InMemoryKV, type Namespace, type SiteMetadata } from "./kv.ts";
import { deleteSite, publishSite, updateVisibility } from "./namespace-sites.ts";
import { pauseNamespaceSites, unpauseNamespaceSites } from "./billing.ts";
import { publishRootSite } from "./space.ts";
import { checkAccess, readMetadata } from "./access-control.ts";

const ns: Namespace = {
  id: "8f14e45f-ceea-467f-a8d9-91b1c0c2d7aa",
  name: "alice",
  domain: "upubli.sh",
};

const otherNs: Namespace = {
  id: "0c445639-1c34-45cf-8d3e-2b6b8d1f9b01",
  name: "bob",
  domain: "upubli.sh",
};

const meta: SiteMetadata = {
  visibility: "public",
  passcode_hashes: [],
  owner: "alice",
  tier: "pro",
  created: "2026-05-19T00:00:00.000Z",
};

describe("fix: server writes are readable by the Worker (by namespace name)", () => {
  test("test_dw_R31_publish_metadata_reachable_by_worker", async () => {
    const kv = new InMemoryKV();
    await publishSite(kv, ns, "portfolio", meta);
    const found = await readMetadata(kv, ns.name, "portfolio");
    expect(found).not.toBeNull();
    expect(found?.owner).toBe("alice");
  });

  test("test_dw_R31_passcode_site_protected_end_to_end", async () => {
    const kv = new InMemoryKV();
    await publishSite(kv, ns, "secret", {
      ...meta,
      visibility: "passcode",
      passcode_hashes: ["ab12"],
    });
    expect(await checkAccess({ kv, nsName: ns.name, slug: "secret" })).toBe("passcode-form");
    expect(
      await checkAccess({ kv, nsName: ns.name, slug: "secret", hasValidPasscodeSession: true }),
    ).toBe("serve");
  });

  test("test_dw_R31_pause_and_unpause_visible_to_worker", async () => {
    const kv = new InMemoryKV();
    await publishSite(kv, ns, "portfolio", meta);
    await pauseNamespaceSites(kv, ns, ["portfolio"]);
    expect(await checkAccess({ kv, nsName: ns.name, slug: "portfolio" })).toBe("paused");
    await unpauseNamespaceSites(kv, ns, ["portfolio"]);
    expect(await checkAccess({ kv, nsName: ns.name, slug: "portfolio" })).toBe("serve");
  });

  test("test_dw_R31_visibility_update_visible_to_worker", async () => {
    const kv = new InMemoryKV();
    await publishSite(kv, ns, "portfolio", meta);
    await updateVisibility(kv, ns, "portfolio", "passcode", ["cd34"]);
    expect(await checkAccess({ kv, nsName: ns.name, slug: "portfolio" })).toBe("passcode-form");
  });

  test("test_dw_R31_delete_removes_worker_visible_entry", async () => {
    const kv = new InMemoryKV();
    await publishSite(kv, ns, "portfolio", meta);
    await deleteSite(kv, ns, "portfolio");
    expect(await readMetadata(kv, ns.name, "portfolio")).toBeNull();
  });

  test("test_dw_R31_root_site_still_served", async () => {
    const kv = new InMemoryKV();
    await publishRootSite(kv, ns, meta);
    expect(await readMetadata(kv, ns.name, "_root")).not.toBeNull();
  });
});

describe("fix quality: one consistent key format, no workaround left", () => {
  test("test_dw_R31_no_nsid_keyed_writes_remain", async () => {
    const kv = new InMemoryKV();
    await publishSite(kv, ns, "portfolio", meta);
    await updateVisibility(kv, ns, "portfolio", "unlisted");
    await pauseNamespaceSites(kv, ns, ["portfolio"]);
    await publishRootSite(kv, ns, meta);
    const offenders = kv.keys().filter((k) => k.includes(ns.id));
    expect(offenders).toEqual([]);
  });

  test("test_dw_R31_root_publish_writes_exactly_one_key", async () => {
    const kv = new InMemoryKV();
    await publishRootSite(kv, ns, meta);
    expect(kv.keys()).toEqual([`site:${ns.name}:_root`]);
  });
});

describe("preserved behavior + dirty edges", () => {
  test("test_offdw_worker_fail_open_on_kv_miss", async () => {
    expect(
      await checkAccess({ kv: new InMemoryKV(), nsName: "alice", slug: "unknown" }),
    ).toBe("serve");
  });

  test("test_offdw_malformed_kv_entry_treated_as_miss", async () => {
    const kv = new InMemoryKV();
    await kv.put("site:alice:bad", "{not json");
    expect(await readMetadata(kv, "alice", "bad")).toBeNull();
    expect(await checkAccess({ kv, nsName: "alice", slug: "bad" })).toBe("serve");
  });

  test("test_offdw_same_slug_in_two_namespaces_is_isolated", async () => {
    const kv = new InMemoryKV();
    await publishSite(kv, ns, "blog", meta);
    await publishSite(kv, otherNs, "blog", { ...meta, owner: "bob", paused: true });
    expect(await checkAccess({ kv, nsName: "alice", slug: "blog" })).toBe("serve");
    expect(await checkAccess({ kv, nsName: "bob", slug: "blog" })).toBe("paused");
  });

  test("test_offdw_pause_of_unpublished_slug_creates_nothing", async () => {
    const kv = new InMemoryKV();
    await pauseNamespaceSites(kv, ns, ["ghost"]);
    expect(kv.keys()).toEqual([]);
  });

  test("test_offdw_visibility_update_preserves_other_fields", async () => {
    const kv = new InMemoryKV();
    await publishSite(kv, ns, "portfolio", meta);
    await updateVisibility(kv, ns, "portfolio", "unlisted");
    const found = await readMetadata(kv, ns.name, "portfolio");
    expect(found?.owner).toBe("alice");
    expect(found?.tier).toBe("pro");
    expect(found?.visibility).toBe("unlisted");
  });
});
