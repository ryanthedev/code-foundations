# Checklists: cc-integration-practices

Source: Code Complete 2nd Edition, Chapter 29

## Integration Strategy Checklist (pp. 706-707)

- [ ] "Does the strategy identify the optimal order in which subsystems, classes, and routines should be integrated?"
- [ ] "Is the integration order coordinated with the construction order so that classes will be ready for integration at the right time?"
- [ ] "Does the strategy lead to easy diagnosis of defects?"
- [ ] "Does the strategy keep scaffolding to a minimum?"
- [ ] "Is the strategy better than other approaches?"
- [ ] "Have the interfaces between components been specified well? (Specifying interfaces isn't an integration task, but verifying that they have been specified well is.)"

## Daily Build and Smoke Test Checklist (p. 707)

- [ ] "Is the project building frequently—ideally, daily—to support incremental integration?"
- [ ] "Is a smoke test run with each build so that you know whether the build works?"
- [ ] "Have you automated the build and the smoke test?"
- [ ] "Do developers check in their code frequently—going no more than a day or two between check-ins?"
- [ ] "Is the smoke test kept up to date with the code, expanding as the code expands?"
- [ ] "Is a broken build a rare occurrence?"
- [ ] "Do you build and smoke test the software even when you're under pressure?"

---
Total items: 13
