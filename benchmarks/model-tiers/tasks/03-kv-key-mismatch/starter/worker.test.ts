/**
 * Worker-side access-control tests. KV entries are seeded directly under the
 * key the Worker looks up — the read path in isolation.
 */
import { describe, expect, test } from "bun:test";
import { InMemoryKV, type SiteMetadata } from "./kv.ts";
import { checkAccess, readMetadata } from "./access-control.ts";

const meta: SiteMetadata = {
  visibility: "public",
  passcode_hashes: [],
  owner: "alice",
  tier: "pro",
  created: "2026-05-19T00:00:00.000Z",
};

function seeded(key: string, value: SiteMetadata): InMemoryKV {
  const kv = new InMemoryKV();
  void kv.put(key, JSON.stringify(value));
  return kv;
}

describe("readMetadata", () => {
  test("returns metadata stored under site:{nsName}:{slug}", async () => {
    const kv = seeded("site:alice:portfolio", meta);
    const found = await readMetadata(kv, "alice", "portfolio");
    expect(found?.owner).toBe("alice");
  });

  test("returns null on a KV miss", async () => {
    expect(await readMetadata(new InMemoryKV(), "alice", "nope")).toBeNull();
  });

  test("returns null on a malformed cache entry", async () => {
    const kv = new InMemoryKV();
    await kv.put("site:alice:bad", "{not json");
    expect(await readMetadata(kv, "alice", "bad")).toBeNull();
  });
});

describe("checkAccess", () => {
  test("public site serves", async () => {
    const kv = seeded("site:alice:portfolio", meta);
    expect(await checkAccess({ kv, nsName: "alice", slug: "portfolio" })).toBe("serve");
  });

  test("passcode site without a session shows the form", async () => {
    const kv = seeded("site:alice:secret", {
      ...meta,
      visibility: "passcode",
      passcode_hashes: ["ab12"],
    });
    expect(await checkAccess({ kv, nsName: "alice", slug: "secret" })).toBe("passcode-form");
  });

  test("passcode site with a valid session serves", async () => {
    const kv = seeded("site:alice:secret", {
      ...meta,
      visibility: "passcode",
      passcode_hashes: ["ab12"],
    });
    expect(
      await checkAccess({
        kv,
        nsName: "alice",
        slug: "secret",
        hasValidPasscodeSession: true,
      }),
    ).toBe("serve");
  });

  test("paused site is blocked", async () => {
    const kv = seeded("site:alice:portfolio", { ...meta, paused: true });
    expect(await checkAccess({ kv, nsName: "alice", slug: "portfolio" })).toBe("paused");
  });

  test("KV miss fails open and serves", async () => {
    expect(
      await checkAccess({ kv: new InMemoryKV(), nsName: "alice", slug: "unknown" }),
    ).toBe("serve");
  });
});
