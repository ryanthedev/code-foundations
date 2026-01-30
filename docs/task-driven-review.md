# Task-Driven Review Flow

> **Note:** This was the initial design exploration. The actual implementation uses a hybrid approach - see `commands/review.md` (Standard/Deep mode).
>
> **Final architecture:**
> - JSONL for streaming units/results (handles large diffs)
> - TaskList only for coordination (`triage:complete` signal)

## Initial Design (Superseded)

---

## Architecture

```
Triage Agent                    Skill Agents (parallel)
     │                          ┌─────────────────────┐
     │ TaskCreate()             │ cc-defensive        │──┐
     │ TaskCreate()             │ aposd-simplifying   │  │
     │ TaskCreate()             │ aposd-reviewing     │  │ TaskList()
     ▼                          │ cc-code-layout      │  │ → filter
┌─────────────┐                 │ cc-control-flow     │  │ → claim
│ Task Pool   │◄────────────────│ aposd-verifying     │  │ → process
│             │                 │ cc-quality-practices│──┘
└─────────────┘                 └─────────────────────┘
```

All agents dispatched simultaneously. Skill agents poll until tasks appear.

---

## Task Schema

```typescript
interface ReviewTask {
  subject: string;           // "defensive:validateInput"
  description: string;       // Full context for agent
  metadata: {
    // Routing
    skill: string;           // "cc-defensive-programming"
    category: string;        // "defensive"

    // Unit info
    file: string;            // "src/auth.ts"
    name: string;            // "validateInput"
    type: string;            // "function"
    lines: [number, number]; // [10, 25]

    // Characteristics (for filtering)
    has_try_catch: boolean;
    has_loops: boolean;
    has_async: boolean;
    has_io_calls: boolean;
    nesting_depth: number;

    // Results (populated by skill agent)
    findings?: Finding[];
    verdict?: string;
  };
}
```

---

## Step 1: Triage Agent (Producer)

Dispatch immediately with all skill agents:

```
Task(
  subagent_type: "general-purpose",
  model: "haiku",
  description: "Triage: create review tasks",
  prompt: """
## Triage Agent

Extract units and create review tasks.

### Phase 1: Extract Units

```bash
cd agents/lens
./extract-units.sh {DIFF_ARGS}
```

For fallback files, extract manually.

### Phase 2: Create Tasks

For each unit, determine which skills should review it:

| Characteristic | Skills |
|----------------|--------|
| has_try_catch | cc-defensive-programming |
| has_io_calls | cc-defensive-programming |
| has_loops | cc-performance-tuning |
| has_async | cc-performance-tuning, aposd-optimizing-critical-paths |
| nesting_depth >= 3 | cc-control-flow-quality |
| type: test | aposd-verifying-correctness, cc-quality-practices |
| (all units) | aposd-reviewing-module-design, cc-code-layout-and-style |

For each unit-skill pair, create a task:

```
TaskCreate(
  subject: "{skill}:{unit.name}",
  description: "Review {unit.name} in {unit.file}:{unit.lines[0]}-{unit.lines[1]}",
  activeForm: "Reviewing {unit.name}",
  metadata: {
    skill: "{skill}",
    category: "{category}",
    file: "{unit.file}",
    name: "{unit.name}",
    type: "{unit.type}",
    lines: {unit.lines},
    ...unit.characteristics
  }
)
```

### Phase 3: Signal Completion

Create sentinel task when done:

```
TaskCreate(
  subject: "triage:complete",
  description: "All units extracted. {N} tasks created.",
  metadata: {sentinel: true, total_tasks: N}
)
```

Return task count.
"""
)
```

---

## Step 2: Skill Agents (Consumers)

Dispatch ALL skill agents in parallel with triage:

```
Task(
  subagent_type: "general-purpose",
  model: "sonnet",
  description: "Lens: {SKILL}",
  prompt: """
## Skill Agent: {SKILL}

You review units assigned to you via the task system.

### Phase 1: Load Skill

```
Skill(code-foundations:{SKILL})
Read(skills/{SKILL}/checklists.md)
```

### Phase 2: Poll for Tasks

Loop until sentinel task appears:

```
while true:
  tasks = TaskList()

  # Check for sentinel
  if any task has metadata.sentinel == true:
    break

  # Find unclaimed tasks for this skill
  my_tasks = tasks.filter(t =>
    t.metadata.skill == "{SKILL}" &&
    t.status == "pending"
  )

  if my_tasks.empty:
    # Wait briefly, retry
    continue

  # Claim and process each task
  for task in my_tasks:
    TaskUpdate(taskId: task.id, status: "in_progress", owner: "{SKILL}")

    # Read the code
    Read(task.metadata.file)

    # Execute checklist against lines task.metadata.lines
    findings = execute_checklist(task.metadata.lines)

    # Complete with results
    TaskUpdate(
      taskId: task.id,
      status: "completed",
      metadata: {findings: findings, verdict: "..."}
    )
```

### Phase 3: Output

Write summary to {BASE_DIR}/{CATEGORY}/{SKILL}.md

Return: file path
"""
)
```

---

## Step 3: Coordinator

After all agents complete, collect results:

```
tasks = TaskList()

# Group by category
by_category = group_by(tasks, t => t.metadata.category)

# Merge findings
for category in by_category:
  all_findings = flatten(category.tasks.map(t => t.metadata.findings))
  write_summary(category, all_findings)

# Generate final report
```

---

## Task Lifecycle

```
┌─────────┐   TaskCreate    ┌─────────┐   TaskUpdate    ┌─────────────┐
│ (none)  │ ───────────────►│ pending │ ───────────────►│ in_progress │
└─────────┘                 └─────────┘   owner={SKILL}  └─────────────┘
                                                               │
                                                               │ TaskUpdate
                                                               │ findings=...
                                                               ▼
                                                         ┌───────────┐
                                                         │ completed │
                                                         └───────────┘
```

---

## Benefits

1. **Granular visibility**: See exactly which units are being reviewed
2. **Parallel execution**: All agents work simultaneously
3. **Resume capability**: Interrupted review continues from pending tasks
4. **Results in metadata**: Findings stored on tasks, easy to aggregate
5. **No file coordination**: Tasks replace {category}.json files

---

## Edge Cases

### No tasks for a skill

Skill agent finds no matching tasks → writes "No units assigned - PASS" → exits.

### Slow triage

Skill agents poll and wait. Sentinel task signals triage complete.

### Same unit, multiple skills

Each skill gets its own task. Unit reviewed independently by each.

Example for `validateInput` with `has_try_catch: true`:
- Task: `cc-defensive-programming:validateInput`
- Task: `aposd-reviewing-module-design:validateInput`
- Task: `cc-code-layout-and-style:validateInput`

---

## Migration from Current Flow

| Current | Task-Driven |
|---------|-------------|
| Write {category}.json | TaskCreate per unit-skill |
| Agent reads JSON file | Agent calls TaskList, filters |
| No progress visibility | TaskList shows pending/in_progress/completed |
| Results in {skill}.md | Results in task metadata + summary file |

---

## Open Questions

1. **Polling frequency**: How long should skill agents wait between TaskList calls?
2. **Task limits**: What if triage creates 500+ tasks? Pagination?
3. **Error handling**: If skill agent crashes, tasks stay in_progress forever?
4. **Deduplication**: If unit unchanged from last review, skip?
