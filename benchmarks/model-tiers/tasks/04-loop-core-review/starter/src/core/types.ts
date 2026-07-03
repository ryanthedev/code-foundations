/**
 * meeseeks core domain types.
 *
 * PURE layer — no infrastructure imports (no Bun, Drizzle, SQLite, fs, network,
 * child_process). These types are the contract every adapter and the runtime
 * build against. See the hexagonal/dependency-rule constraint in the plan.
 */

// ---------------------------------------------------------------------------
// Identifiers
// ---------------------------------------------------------------------------

/** Opaque job identifier (string-backed; adapters choose the encoding). */
export type JobId = string;

/** Opaque run identifier (string-backed; adapters choose the encoding). */
export type RunId = string;

// ---------------------------------------------------------------------------
// Policy enums (Strategy variants, dispatched by the runtime)
// ---------------------------------------------------------------------------

/** What to do when a tick fires while a prior run of the same job is in flight. */
export type OverlapPolicy = 'skip' | 'queue' | 'concurrent';

/** What to do for ticks missed while the daemon was down. */
export type MissedRunPolicy = 'skip' | 'catch-up' | 'replay';

/** Lifecycle status of a single run. */
export type RunStatus = 'running' | 'success' | 'failed' | 'cancelled';

// ---------------------------------------------------------------------------
// Loop / stop configuration
// ---------------------------------------------------------------------------

/**
 * External success predicate. A Strategy set keyed by `kind` — the
 * `PredicateEvaluator` port dispatches on it.
 */
export type PredicateSpec =
  | { kind: 'shell'; command: string; expectExitCode?: number }
  | { kind: 'http'; url: string; expectStatus?: number; timeoutMs?: number }
  | { kind: 'file'; path: string; mustExist?: boolean };

/**
 * The conditions under which a loop stops. "First-to-trip wins" across:
 *  - self-declare (the in-run `meeseeks_done` tool; always available)
 *  - `maxIterations` / `maxTokens` caps
 *  - external `predicate`
 *
 * Any unset cap falls back to a safe default iteration cap at resolve time, so
 * a loop is NEVER unbounded (see DEFAULT_MAX_ITERATIONS).
 */
export interface StopCondition {
  /** Hard cap on completed iterations. Defaults to DEFAULT_MAX_ITERATIONS if unset. */
  maxIterations?: number;
  /** Cumulative token budget; stop once reached. Unset = no token cap. */
  maxTokens?: number;
  /** External success check; stop once it evaluates true. Unset = no predicate. */
  predicate?: PredicateSpec;
}

/** Per-job loop configuration. `enabled: false` means a one-shot (single invocation). */
export interface LoopConfig {
  enabled: boolean;
  stop: StopCondition;
}

// ---------------------------------------------------------------------------
// Notification (channel-agnostic — no file/transport-specific fields)
// ---------------------------------------------------------------------------

/** Per-job notification configuration. `channel` is open-ended so new notifiers drop in. */
export interface NotifyConfig {
  channel: string;
  /** Adapter-private options, opaque to the core. */
  options?: Record<string, unknown>;
}

/**
 * Everything a notifier of ANY channel needs to deliver a result. Kept
 * channel-agnostic so swapping file -> text/push requires zero core change.
 */
export interface NotifierPayload {
  jobId: JobId;
  jobName: string;
  runId: RunId;
  status: RunStatus;
  /** Short human-readable summary, if available. */
  summary?: string;
  /** Full result text, if available. */
  result?: string;
  /** Error message when the run failed. */
  error?: string;
  startedAt: Date;
  finishedAt: Date;
}

// ---------------------------------------------------------------------------
// Job
// ---------------------------------------------------------------------------

/** The fields a caller supplies to create or update a job. */
export interface JobSpec {
  name: string;
  /** Cron expression; parsed by the CronParser port, not by the core. */
  cron: string;
  /** Prompt sent to the headless Claude invocation. */
  prompt: string;
  /** Optional skill to invoke. */
  skill?: string;
  /** Working directory the invocation runs in. */
  cwd: string;
  /** Tools the invocation is allowed to use. */
  allowedTools?: string[];
  loop: LoopConfig;
  overlap: OverlapPolicy;
  missedRun: MissedRunPolicy;
  notify: NotifyConfig;
  enabled: boolean;
}

/** A persisted job: its spec plus identity, timestamps, and scheduling state. */
export interface Job extends JobSpec {
  id: JobId;
  createdAt: Date;
  updatedAt: Date;
  /** Last time a tick fired (drives missed-run computation on restart). */
  lastFiredAt?: Date;
  /** Next scheduled fire time. */
  nextFireAt?: Date;
}

// ---------------------------------------------------------------------------
// Run + events
// ---------------------------------------------------------------------------

/** A single recorded execution of a job (may span multiple loop iterations). */
export interface Run {
  id: RunId;
  jobId: JobId;
  status: RunStatus;
  startedAt: Date;
  finishedAt?: Date;
  /** Number of loop iterations executed in this run. */
  iterations: number;
  /** Why the loop stopped, when applicable. */
  stopReason?: StopReason;
  /** Final result text, if any. */
  result?: string;
  /** Error message when the run failed. */
  error?: string;
}

/**
 * One MCP server the executor should make available to the invocation.
 * Channel-agnostic config; the executor adapter maps it to CLI flags.
 */
export interface McpServerSpec {
  name: string;
  command: string;
  args?: string[];
  env?: Record<string, string>;
}

/**
 * A single headless Claude invocation request. The ClaudeExecutor consumes it;
 * the loop orchestrator builds one per iteration, threading `resumeSessionId`
 * to continue a conversation.
 */
export interface ExecRequest {
  prompt: string;
  skill?: string;
  cwd: string;
  allowedTools?: string[];
  /** Additional MCP servers to expose to the invocation. */
  mcpServers?: McpServerSpec[];
  /** When set, resume the prior session instead of starting fresh. */
  resumeSessionId?: string;
}

/**
 * One event from a single Claude invocation's stream. The ClaudeExecutor port
 * yields these; this discriminated union is the seam isolating stream-json
 * parsing from the rest of the system.
 *
 * `session` carries the claude session ID so the orchestrator can thread it
 * into the next ExecRequest.resumeSessionId for loop continuation.
 */
export type RunEvent =
  | { type: 'text'; text: string }
  | { type: 'tool_use'; name: string; input?: any }
  | { type: 'usage'; inputTokens: number; outputTokens: number }
  | { type: 'done'; result?: string }
  | { type: 'error'; message: string }
  | { type: 'session'; sessionId: string };

// ---------------------------------------------------------------------------
// Loop runtime state + decision (consumed by the pure logic in loop.ts)
// ---------------------------------------------------------------------------

/** Accumulated state across loop iterations. Pure data; threaded by the orchestrator. */
export interface LoopState {
  /** Completed iterations so far. */
  iterations: number;
  /** Cumulative tokens consumed (input + output) across iterations. */
  tokensUsed: number;
  /** True once the in-run `meeseeks_done` tool fired. */
  selfDeclared: boolean;
  /** Result payload carried by the `done` event, if any. */
  declaredResult?: string;
  /** Result of the most recent external predicate evaluation. */
  predicateTripped: boolean;
}

/** The reason a loop stopped. Also the precedence vocabulary for "first-to-trip". */
export type StopReason =
  | 'self-declared'
  | 'predicate'
  | 'max-tokens'
  | 'max-iterations';

/** The outcome of evaluating stop conditions: continue, or stop with a reason. */
export type StopDecision =
  | { stop: false }
  | { stop: true; reason: StopReason };
