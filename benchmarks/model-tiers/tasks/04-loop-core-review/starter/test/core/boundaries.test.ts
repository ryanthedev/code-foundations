/**
 * Dependency-rule guard: the core layer must not import infrastructure.
 * Scans every module under src/core/ for forbidden import specifiers.
 */
import { describe, expect, test } from 'bun:test';
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const CORE_DIR = join(import.meta.dir, '../../src/core');

/** Infra packages the core layer must never import. */
const FORBIDDEN_SPECIFIERS = [
  'drizzle',
  'node:fs',
  'node:child_process',
  'node:net',
  'node:http',
  'node:os',
];

describe('core layer purity (dependency rule)', () => {
  const files = readdirSync(CORE_DIR).filter((f) => f.endsWith('.ts'));

  test('src/core contains the expected modules', () => {
    expect(files.sort()).toEqual(['loop.ts', 'ports.ts', 'types.ts']);
  });

  test.each(files)('%s imports no infrastructure', (file) => {
    const source = readFileSync(join(CORE_DIR, file), 'utf-8');
    const importLines = source
      .split('\n')
      .filter((l) => /^\s*import\b|\brequire\(/.test(l));
    for (const specifier of FORBIDDEN_SPECIFIERS) {
      const hits = importLines.filter((l) => l.includes(specifier));
      expect(hits).toEqual([]);
    }
  });
});
