# cc-table-driven-methods - Evidence and Hard Data

Source: Code Complete 2nd Edition, Chapter 18 (pp. 411-430)

---

## Key Points (Author-Marked)

1. **Table-driven code is simpler than complicated logic, easier to modify, and more efficient** (p.411)
   - Qualifier: "in appropriate circumstances"
   - In simple cases, logic statements are easier and more direct
   - As logic chain becomes complex, tables become increasingly attractive

2. **Two issues in table-driven methods:** (p.412-413)
   - How to look up entries in the table (access method)
   - What you should store in the table (data vs action codes vs routine references)

3. **Direct access tables replace complicated logical control structures** (p.413)
   - Simplest and most direct access method
   - Use when data can key directly into table

4. **What to store: data, action codes, or routine references** (p.413)
   - Data: Direct values (days per month, rates)
   - Action codes: Enum indicating what to do
   - Routine references: Function pointers for different behaviors

---

## Core Claims

### Data vs Logic
> "You put your program's knowledge into its data rather than into its logic—in the table instead of in the if tests." (p.412)

**Implication:** Design choice between encoding knowledge in data structures vs control flow.

### Tables Become Attractive with Complexity
> "In simple cases, logic statements are easier and more direct. As the logic chain becomes more complex, tables become increasingly attractive." (p.411)

**Threshold:** ~3+ branches for same classification = consider table.

### Data Flexibility
> "Data is more flexible than logic. Data is easy to change when a message format changes. If you have to add a new kind of message, you can just add another element to the data table." (p.420-421)

**Implication:** Tables provide better maintainability for volatile requirements.

### OOP Not Automatically Better
> "The fact that a design uses inheritance and polymorphism doesn't make it a good design." (p.423)

> "A rote object-oriented design would require as much code as a rote functional design—or more."

> "The key design insight is neither object orientation nor functional orientation—it's the use of a well thought out lookup table."

**Implication:** Don't assume OOP inheritance is superior to table-driven approach.

### Table Lookup Efficiency
> "Table lookups are less error-prone, more maintainable, and more efficient than lengthy if statements, case statements, or copious subclasses." (p.423)

### Design Choice Philosophy
> "The point of design is choosing one of the several good options for your case. Don't worry too much about choosing the best one. It's better to strive for a good solution and avoid disaster rather than trying to find the best solution." (p.429, citing Butler Lampson 1984)

---

## Anti-Patterns (CODING HORROR)

### Long If-Else Chains for Multi-Factor Lookup
**Example:** Insurance rates varying by age, gender, marital status, smoking status

**Anti-Pattern Code:**
```java
if (gender == MALE) {
    if (maritalStatus == SINGLE) {
        if (smokingStatus == SMOKING) {
            if (age < 18) { ... }
            else if (age < 25) { ... }
            // ... deeply nested horror
        }
    }
}
```

**Problems:**
- Hard to read
- Hard to modify
- Error-prone
- Exponential growth with factors

**Table Solution:**
```vb
Dim rateTable(SmokingStatus_Last, Gender_Last, MaritalStatus_Last, MAX_AGE) As Double
rate = rateTable(smokingStatus, gender, maritalStatus, age)
```

### Creating Subclass Per Data Variant
**Example:** 20 message types → 20 subclasses

**Problems:**
- Each subclass differs only in data, not behavior
- Rote OOP adds complexity without benefit
- Code changes required for new types

**Table Solution:**
- Define field types as enum
- Describe message formats in table
- One generic routine interprets table
- New types = new table entries, no code changes

---

## Qualifiers and Scope

| Claim | Qualifier | Context |
|-------|-----------|---------|
| Tables simpler than logic | "in appropriate circumstances" | Not for simple 2-way decisions |
| OOP not automatically better | When behavior differs only in data | Genuinely polymorphic behavior still benefits from OOP |
| Tables more efficient | For lookup-heavy code paths | Setup overhead exists |
| Data more flexible | For volatile requirements | Truly static data can stay in code |

---

## Cross-References

| Topic | Reference | Relevance |
|-------|-----------|-----------|
| Information hiding | Section 5.3 | Tables hide implementation details |
| Class design | Chapter 6 | When to use table vs inheritance |
| Decision tables | Section 19.1 | Related technique for complicated logic |
| Complicated expressions | Section 26.1 | Table lookups can replace |
| Binding time | Section 10.6 | External table data decisions |
| Design in Construction | Chapter 5 | Where tables fit in design |
| Memory paging | Section 25.3 | Performance consideration for large tables |

---

## Access Method Comparison

| Method | Use When | Space | Time | Example |
|--------|----------|-------|------|---------|
| **Direct** | Key maps to small contiguous range | O(range) | O(1) | Month → days |
| **Indexed** | Large sparse keyspace, few entries | O(keyspace + entries) | O(1) + index | Part numbers |
| **Stair-Step** | Ranges rather than points | O(ranges) | O(n) or O(log n) | Grade cutoffs |

### Indexed Access Space Savings Example (p.425-426)

**Problem:** 100 items with 4-digit part numbers (0000-9999)

| Approach | Calculation | Total Space |
|----------|-------------|-------------|
| Without Index | 10,000 entries × 100 bytes | 1,000,000 bytes |
| With Index | (10,000 × 2) + (100 × 100) | 30,000 bytes |
| **Savings** | | **97%** |

### Stair-Step for Irregular Data

Probability distributions with values like 0.458747, 0.547651 defy transformation functions but work naturally with stair-step:

| Probability | Claim Amount |
|-------------|--------------|
| 0.458747 | $0.00 |
| 0.547651 | $254.32 |
| 0.627764 | $514.77 |
| ... | ... |

---

## Key Design Decisions

### What to Store in Table

| Store | When | Example |
|-------|------|---------|
| **Data** | Lookup returns the answer directly | Days per month |
| **Action code** | Different actions per entry | Command processing |
| **Routine reference** | Complex behavior per entry | Message parsing |

### Key Transformation Strategies

| Strategy | Benefit | Drawback |
|----------|---------|----------|
| Duplicate information | Straightforward access | Wastes space, risks inconsistency |
| Transform the key | Works with existing data | Must recognize pattern |
| Isolate in routine | Consistent, maintainable | Extra function call |

**Best Practice:** Always isolate key transformation in dedicated routine (e.g., `KeyFromAge()`).

---

## Code Examples from Chapter

### Character Classification
**Before (Logic):**
```java
if ((('a' <= inputChar) && (inputChar <= 'z')) ||
    (('A' <= inputChar) && (inputChar <= 'Z'))) {
   charType = CharacterType.Letter;
}
else if ((inputChar == ' ') || (inputChar == ',') || ...) {
   charType = CharacterType.Punctuation;
}
// ... more branches
```

**After (Table):**
```java
charType = charTypeTable[inputChar];
```

### Days Per Month
**Before:** 12-branch if-else chain
**After:**
```vb
Dim daysPerMonth() As Integer = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 }
days = daysPerMonth(month-1)

' With leap year support:
days = daysPerMonth(month-1, LeapYearIndex())
```

---

## Key Quote

> "Tables provide an alternative to complicated logic and inheritance structures. If you find that you're confused by a program's logic or inheritance tree, ask yourself whether you could simplify by using a lookup table." (Chapter Summary)
