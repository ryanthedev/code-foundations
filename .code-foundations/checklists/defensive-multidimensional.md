# Multi-Dimensional Defensive Checks (25)

Checks that span multiple defensive concerns simultaneously.

---

## Input + Error Handling (5)

- [ ] **DEF-MD-1**: Does input validation fail BEFORE any side effects occur?
- [ ] **DEF-MD-2**: Are validation errors specific enough to debug but vague enough to not leak internals?
- [ ] **DEF-MD-3**: Does the error path clean up any resources acquired during validation?
- [ ] **DEF-MD-4**: Are validation failures logged with context but WITHOUT the invalid input (PII/injection risk)?
- [ ] **DEF-MD-5**: Do validation errors include correlation IDs for tracing without exposing internal state?

---

## Error Handling + State Management (5)

- [ ] **DEF-MD-6**: After a caught exception, is the object still in a valid state for subsequent calls?
- [ ] **DEF-MD-7**: Do partial failures leave the system in a recoverable state (not corrupted)?
- [ ] **DEF-MD-8**: Are error handlers free of side effects that could fail (no errors in error handling)?
- [ ] **DEF-MD-9**: Does retry logic preserve idempotency of the overall operation?
- [ ] **DEF-MD-10**: Are compensating actions (rollback) atomic or do they have their own failure modes?

---

## Security + Logging (5)

- [ ] **DEF-MD-11**: Are security-sensitive operations logged BEFORE execution (audit trail even if crash)?
- [ ] **DEF-MD-12**: Do logs avoid recording credentials, tokens, PII, or data that could enable replay attacks?
- [ ] **DEF-MD-13**: Are authorization failures logged differently from authentication failures (detection signal)?
- [ ] **DEF-MD-14**: Is timing information in logs insufficient for timing attacks (e.g., password comparison)?
- [ ] **DEF-MD-15**: Do error messages in responses differ from error messages in logs (separate audiences)?

---

## Boundaries + Trust (5)

- [ ] **DEF-MD-16**: Is data re-validated when crossing trust boundaries (even if validated earlier)?
- [ ] **DEF-MD-17**: Are external API responses treated as untrusted input (validated before use)?
- [ ] **DEF-MD-18**: Do internal service calls have timeouts AND circuit breakers (defense in depth)?
- [ ] **DEF-MD-19**: Are deserialized objects validated for invariants (not just schema)?
- [ ] **DEF-MD-20**: Is there a clear trust boundary diagram and does code match it?

---

## Concurrency + Safety (5)

- [ ] **DEF-MD-21**: Do concurrent error handlers avoid racing to the same recovery action?
- [ ] **DEF-MD-22**: Are shared resources released in finally/defer even under concurrent cancellation?
- [ ] **DEF-MD-23**: Do timeouts account for all resources (not just the main operation)?
- [ ] **DEF-MD-24**: Are rate limits applied BEFORE expensive validation (fail fast under load)?
- [ ] **DEF-MD-25**: Under partial system failure, do remaining components degrade gracefully (not cascade)?

---

## Summary

| Category | Checks | Focus |
|----------|--------|-------|
| Input + Error | 5 | Validation failure paths |
| Error + State | 5 | Consistency after errors |
| Security + Logging | 5 | Audit without leakage |
| Boundaries + Trust | 5 | Defense in depth |
| Concurrency + Safety | 5 | Failure under load |
| **Total** | **25** | Multi-dimensional defensive |
