import { describe, expect, test } from 'bun:test';
import {
  DEFAULT_MAX_ITERATIONS,
  STOP_PRECEDENCE,
  applyEvent,
  initialLoopState,
  loopStep,
  resolveStop,
} from '../../src/core/loop';
import type { LoopState, StopCondition } from '../../src/core/types';

/** Build a LoopState with overrides on top of a zeroed base. */
function state(overrides: Partial<LoopState> = {}): LoopState {
  return { ...initialLoopState(), ...overrides };
}

describe('initialLoopState', () => {
  test('is zeroed and not tripped', () => {
    expect(initialLoopState()).toEqual({
      iterations: 0,
      tokensUsed: 0,
      selfDeclared: false,
      predicateTripped: false,
    });
  });
});

describe('resolveStop: single condition first-to-trip', () => {
  test('continues when nothing tripped', () => {
    const cfg: StopCondition = { maxIterations: 10 };
    expect(resolveStop(state({ iterations: 3 }), cfg)).toEqual({ stop: false });
  });

  test('self-declared stops the loop', () => {
    const cfg: StopCondition = { maxIterations: 10 };
    expect(resolveStop(state({ selfDeclared: true }), cfg)).toEqual({
      stop: true,
      reason: 'self-declared',
    });
  });

  test('max-iterations stops at and above the cap', () => {
    const cfg: StopCondition = { maxIterations: 5 };
    expect(resolveStop(state({ iterations: 5 }), cfg)).toEqual({
      stop: true,
      reason: 'max-iterations',
    });
    expect(resolveStop(state({ iterations: 7 }), cfg).stop).toBe(true);
  });

  test('max-tokens stops at the budget', () => {
    const cfg: StopCondition = { maxIterations: 100, maxTokens: 1000 };
    expect(resolveStop(state({ tokensUsed: 1000 }), cfg)).toEqual({
      stop: true,
      reason: 'max-tokens',
    });
    expect(resolveStop(state({ tokensUsed: 999 }), cfg)).toEqual({ stop: false });
  });

  test('predicate stops the loop', () => {
    const cfg: StopCondition = {
      maxIterations: 100,
      predicate: { kind: 'file', path: '/done' },
    };
    expect(resolveStop(state({ predicateTripped: true }), cfg)).toEqual({
      stop: true,
      reason: 'predicate',
    });
  });
});

describe('resolveStop: deterministic precedence when >=2 trip', () => {
  test('all four trip -> self-declared wins', () => {
    const cfg: StopCondition = {
      maxIterations: 5,
      maxTokens: 100,
      predicate: { kind: 'shell', command: 'true' },
    };
    const s = state({
      selfDeclared: true,
      predicateTripped: true,
      tokensUsed: 100,
      iterations: 5,
    });
    expect(resolveStop(s, cfg)).toEqual({ stop: true, reason: 'self-declared' });
  });

  test('predicate beats the caps', () => {
    const cfg: StopCondition = {
      maxIterations: 5,
      maxTokens: 100,
      predicate: { kind: 'shell', command: 'true' },
    };
    const s = state({ predicateTripped: true, tokensUsed: 100, iterations: 5 });
    expect(resolveStop(s, cfg)).toEqual({ stop: true, reason: 'predicate' });
  });

  test('tokens beat iterations', () => {
    const cfg: StopCondition = { maxIterations: 5, maxTokens: 100 };
    const s = state({ tokensUsed: 100, iterations: 5 });
    expect(resolveStop(s, cfg)).toEqual({ stop: true, reason: 'max-tokens' });
  });

  test('the precedence array is the documented ordering', () => {
    expect(STOP_PRECEDENCE).toEqual([
      'self-declared',
      'predicate',
      'max-tokens',
      'max-iterations',
    ]);
  });
});

describe('default cap', () => {
  test('empty stop condition defaults the iteration cap', () => {
    const cfg: StopCondition = {};
    expect(resolveStop(state({ iterations: DEFAULT_MAX_ITERATIONS - 1 }), cfg)).toEqual({
      stop: false,
    });
    expect(resolveStop(state({ iterations: DEFAULT_MAX_ITERATIONS }), cfg)).toEqual({
      stop: true,
      reason: 'max-iterations',
    });
  });

  test('explicit zero cap is honored, not defaulted', () => {
    const cfg: StopCondition = { maxIterations: 0 };
    expect(resolveStop(state({ iterations: 0 }), cfg)).toEqual({
      stop: true,
      reason: 'max-iterations',
    });
  });
});

describe('edge cases: zero-iteration and one-shot', () => {
  test('zero-iteration job stops before any work', () => {
    const cfg: StopCondition = { maxIterations: 0 };
    expect(resolveStop(state(), cfg).stop).toBe(true);
  });

  test('fresh state with the default cap continues', () => {
    expect(resolveStop(initialLoopState(), {})).toEqual({ stop: false });
  });
});

describe('applyEvent (pure event fold)', () => {
  test('done sets selfDeclared and carries result', () => {
    const next = applyEvent(initialLoopState(), { type: 'done', result: 'ok' });
    expect(next.selfDeclared).toBe(true);
    expect(next.declaredResult).toBe('ok');
  });

  test('done without result leaves declaredResult absent', () => {
    const next = applyEvent(initialLoopState(), { type: 'done' });
    expect(next.selfDeclared).toBe(true);
    expect(next.declaredResult).toBeUndefined();
  });

  test('usage accumulates tokens', () => {
    const s = applyEvent(initialLoopState(), {
      type: 'usage',
      inputTokens: 10,
      outputTokens: 5,
    });
    expect(s.tokensUsed).toBeGreaterThan(0);
  });

  test.each([
    { type: 'text', text: 'hi' } as const,
    { type: 'tool_use', name: 'x' } as const,
    { type: 'error', message: 'boom' } as const,
  ])('non-loop events leave state unchanged (%o)', (event) => {
    const before = state({ iterations: 2, tokensUsed: 3 });
    expect(applyEvent(before, event)).toEqual(before);
  });

  test('does not mutate the input state', () => {
    const before = initialLoopState();
    const snapshot = { ...before };
    applyEvent(before, { type: 'usage', inputTokens: 9, outputTokens: 9 });
    expect(before).toEqual(snapshot);
  });
});

describe('loopStep (fold + decide)', () => {
  test('a done event folds and resolves to a self-declared stop', () => {
    const { state: next, decision } = loopStep(initialLoopState(), { type: 'done' }, {
      maxIterations: 10,
    });
    expect(next.selfDeclared).toBe(true);
    expect(decision).toEqual({ stop: true, reason: 'self-declared' });
  });

  test('a usage event that crosses the token budget stops on tokens', () => {
    const { decision } = loopStep(
      state({ tokensUsed: 95 }),
      { type: 'usage', inputTokens: 0, outputTokens: 6 },
      { maxIterations: 100, maxTokens: 100 },
    );
    expect(decision).toEqual({ stop: true, reason: 'max-tokens' });
  });
});
