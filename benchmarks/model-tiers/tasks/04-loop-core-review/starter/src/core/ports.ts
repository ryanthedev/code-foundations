/**
 * meeseeks core ports.
 *
 * Deep, minimal interfaces. Each hides large adapter complexity behind a tiny
 * surface (Clean Architecture: interfaces live in the inner layer; adapters in
 * the outer layer implement them, so dependencies point inward). PURE — no infra.
 */

import type { Database } from 'bun:sqlite';
import type {
  ExecRequest,
  Job,
  JobSpec,
  NotifierPayload,
  PredicateSpec,
  Run,
  RunEvent,
  RunStatus,
} from './types';

/**
 * Convenience alias for the SQLite handle the persistence adapter opens —
 * re-exported here so adapter signatures can share one name for it.
 */
export type DbHandle = Database;

/** Persisted scheduling timestamps for a job. `null` clears a stored value. */
export interface FireTimes {
  lastFiredAt?: Date | null;
  nextFireAt?: Date | null;
}

// ExecRequest is part of the executor contract; declared here next to its port.
export type { ExecRequest, McpServerSpec } from './types';

// ---------------------------------------------------------------------------
// Persistence ports
// ---------------------------------------------------------------------------

/** Stores and retrieves jobs. Implemented by the persistence adapter. */
export interface JobStore {
  create(spec: JobSpec): Job;
  get(id: string): Job | null;
  list(): Job[];
  update(id: string, patch: Partial<JobSpec>): Job;
  delete(id: string): void;
  /**
   * Persist scheduling timestamps (`lastFiredAt`/`nextFireAt`) without touching
   * the job spec. The runtime calls this when scheduling and when a tick fires,
   * so missed-run reconciliation survives a daemon restart.
   */
  setFireTimes(id: string, times: FireTimes): void;
}

/** Stores and retrieves runs and their output. */
export interface RunStore {
  start(jobId: string): Run;
  appendOutput(runId: string, chunk: string): void;
  finish(runId: string, status: RunStatus): Run;
  get(id: string): Run | null;
  list(jobId?: string): Run[];
}

// ---------------------------------------------------------------------------
// Execution port
// ---------------------------------------------------------------------------

/**
 * Runs ONE headless Claude invocation and yields its events as a stream. Deep
 * by design: a single method hides spawning, stream-json parsing, session
 * resume, and the in-run done-tool MCP. The loop/stop logic lives outside
 * this port.
 */
export interface ClaudeExecutor {
  run(req: ExecRequest): AsyncIterable<RunEvent>;
}

// ---------------------------------------------------------------------------
// Notification port
// ---------------------------------------------------------------------------

/** Delivers a run result over some channel. Implemented by notifier adapters. */
export interface Notifier {
  notify(payload: NotifierPayload): Promise<void>;
}

// ---------------------------------------------------------------------------
// Time + predicate ports (injected for testability — never read the wall clock
// or run external checks directly from the core/runtime decision logic)
// ---------------------------------------------------------------------------

/** Supplies the current time. Inject a fake in tests for deterministic scheduling. */
export interface Clock {
  now(): Date;
}

/** Evaluates an external success predicate to a boolean. */
export interface PredicateEvaluator {
  evaluate(spec: PredicateSpec): Promise<boolean>;
}

// ---------------------------------------------------------------------------
// Cron parsing port ("cron-expression parsing contract — port, not impl")
// ---------------------------------------------------------------------------

/** A parsed cron schedule. Deep: computes fire times without exposing internals. */
export interface CronSchedule {
  /** The next fire time strictly after `after`, or null if the schedule never fires again. */
  next(after: Date): Date | null;
}

/** Parses cron expressions into schedules. Throws on an invalid expression. */
export interface CronParser {
  parse(expression: string): CronSchedule;
}
