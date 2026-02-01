# Checklists: cc-integration-practices

Source: Code Complete 2nd Edition, Chapter 29

---

## Integration Strategy Checklist (pp. 706-707)

- [ ] IS-1: "Does the strategy identify the optimal order in which subsystems, classes, and routines should be integrated?" → Red flag: Random integration order leads to impossible defect diagnosis
- [ ] IS-2: "Is the integration order coordinated with the construction order so that classes will be ready for integration at the right time?" (Good: Construction schedule drives integration readiness, Bad: Integration blocked waiting for incomplete components)
- [ ] IS-3: "Does the strategy lead to easy diagnosis of defects?" → Red flag: Multiple simultaneous integrations make fault isolation impossible
- [ ] IS-4: "Does the strategy keep scaffolding to a minimum?" (Good: < 20% effort on scaffolding, Bad: More scaffolding than production code)
- [ ] IS-5: "Is the strategy better than other approaches?" → Compare phased vs. incremental vs. T-shaped integration
- [ ] IS-6: "Have the interfaces between components been specified well? (Specifying interfaces isn't an integration task, but verifying that they have been specified well is.)" → Red flag: Integration reveals undefined interface contracts

---

## Daily Build and Smoke Test Checklist (p. 707)

- [ ] DB-1: "Is the project building frequently—ideally, daily—to support incremental integration?" → Red flag: Builds less than once per day create integration debt
- [ ] DB-2: "Is a smoke test run with each build so that you know whether the build works?" (Good: Automated pass/fail in < 5 minutes, Bad: Manual testing or no verification)
- [ ] DB-3: "Have you automated the build and the smoke test?" → Red flag: Manual builds create inconsistency and waste time
- [ ] DB-4: "Do developers check in their code frequently—going no more than a day or two between check-ins?" → Red flag: Long-lived branches cause merge hell and integration delays
- [ ] DB-5: "Is the smoke test kept up to date with the code, expanding as the code expands?" (Good: Test coverage grows with features, Bad: Tests lag behind implementation)
- [ ] DB-6: "Is a broken build a rare occurrence?" → Red flag: Frequent build breakage indicates quality process failure
- [ ] DB-7: "Do you build and smoke test the software even when you're under pressure?" (Good: Never skip builds, Bad: "We'll integrate later when there's time")

---

## Red Flags

- [ ] RF-1: "Big bang integration?" - Integrating all components simultaneously → Impossible to diagnose failures, use incremental integration
- [ ] RF-2: "No scaffolding budget?" - Avoiding test harnesses to save time → False economy, scaffolding enables faster debugging
- [ ] RF-3: "Broken build normal?" - Team treats failures as routine → Build breakage must be exceptional event requiring immediate fix
- [ ] RF-4: "Manual build process?" - Human-driven compilation and deployment → Automation eliminates inconsistency and saves hours daily
- [ ] RF-5: "Integration surprises?" - Interface mismatches discovered late → Verify interfaces specified before integration begins
- [ ] RF-6: "Infrequent check-ins?" - Developers hold code for days/weeks → Integration debt compounds, merge conflicts multiply
- [ ] RF-7: "Smoke test lag?" - Tests don't cover new features → False confidence, bugs escape detection
- [ ] RF-8: "Skip builds under pressure?" - "Too busy to build today" → Pressure is when you need builds MOST to catch regressions
- [ ] RF-9: "Bottom-up only?" - Starting with low-level utilities → Can't test real functionality until late, consider T-shaped integration
- [ ] RF-10: "No integration strategy?" - Ad-hoc "integrate whatever's ready" → Chaotic debugging, unpredictable progress

---

Total items: 23
