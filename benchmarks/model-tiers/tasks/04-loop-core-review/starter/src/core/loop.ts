/**
 * meeseeks pure loop / stop logic.
 *
 * A pure reducer over loop state: no timers, no I/O, no port calls. The async
 * external predicate is evaluated elsewhere (PredicateEvaluator port) and its
 * boolean result threaded onto LoopState before resolveStop is called, so this
 * module stays pure and fully testable.
 */

import type {
  LoopState,
  RunEvent,
  StopCondition,
  StopDecision,
  StopReason,
} from './types';

/**
 * Safe default iteration cap, applied when a StopCondition specifies no explicit
 * `maxIterations`. Guarantees a loop is never unbounded.
 */
export const DEFAULT_MAX_ITERATIONS = 25;

/**
 * Deterministic "first-to-trip wins" ordering. When two or more conditions trip
 * in the same iteration, the earliest one in this array is the reported reason:
 *
 *  1. self-declared  — the agent intentionally declared completion (most meaningful)
 *  2. predicate      — an explicit external success condition was met
 *  3. max-tokens     — budget backstop exhausted
 *  4. max-iterations — iteration backstop; the guaranteed-bounded ultimate cap
 */
export const STOP_PRECEDENCE: readonly StopReason[] = [
  'self-declared',
  'predicate',
  'max-tokens',
  'max-iterations',
];

/** A fresh, zeroed loop state. */
export function initialLoopState(): LoopState {
  return {
    iterations: 0,
    tokensUsed: 0,
    selfDeclared: false,
    predicateTripped: false,
  };
}

/**
 * Fold a single executor event into loop state (pure). Only `done` and `usage`
 * carry loop-relevant signal; other events leave state unchanged. Iteration
 * counting and predicate evaluation are the orchestrator's responsibility and
 * are threaded in separately.
 */
export function applyEvent(state: LoopState, event: RunEvent): LoopState {
  switch (event.type) {
    case 'done':
      return {
        ...state,
        selfDeclared: true,
        ...(event.result !== undefined ? { declaredResult: event.result } : {}),
      };
    case 'usage':
      return {
        ...state,
        tokensUsed: state.tokensUsed + event.outputTokens,
      };
    case 'text':
    case 'tool_use':
    case 'error':
    case 'session':
      return state;
  }
}

/**
 * Decide whether the loop should stop given its current state and config.
 *
 * Evaluates every stop condition, then returns the first tripped condition in
 * STOP_PRECEDENCE order (deterministic when several trip together). The
 * iteration cap always applies (`maxIterations` defaults to
 * DEFAULT_MAX_ITERATIONS), so the loop is never unbounded.
 */
export function resolveStop(state: LoopState, cfg: StopCondition): StopDecision {
  const effectiveMaxIterations =
    cfg.maxIterations ??
    (cfg.maxTokens !== undefined || cfg.predicate !== undefined
      ? Number.MAX_SAFE_INTEGER
      : DEFAULT_MAX_ITERATIONS);

  const tripped: Record<StopReason, boolean> = {
    'self-declared': state.selfDeclared,
    predicate: state.predicateTripped,
    'max-tokens': cfg.maxTokens !== undefined && state.tokensUsed >= cfg.maxTokens,
    'max-iterations': state.iterations >= effectiveMaxIterations,
  };

  for (const reason of STOP_PRECEDENCE) {
    if (tripped[reason]) {
      return { stop: true, reason };
    }
  }
  return { stop: false };
}

/**
 * Per-iteration reducer: fold the latest event into state, then decide. Returns
 * both the next state (for the orchestrator to thread forward) and the decision.
 * This is the pure `(state, lastEvent, config) -> StopDecision` step from the plan.
 */
export function loopStep(
  state: LoopState,
  lastEvent: RunEvent,
  cfg: StopCondition,
): { state: LoopState; decision: StopDecision } {
  const next = applyEvent(state, lastEvent);
  return { state: next, decision: resolveStop(next, cfg) };
}
