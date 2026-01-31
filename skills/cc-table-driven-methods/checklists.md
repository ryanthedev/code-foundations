# cc-table-driven-methods - Checklists

Source: Code Complete 2nd Edition, Chapter 18 (pp. 411-430)

---

## Table-Driven Methods Checklist (Verbatim from Book)

- [ ] BK-1: "Have you considered table-driven methods as an alternative to complicated logic?"
- [ ] BK-2: "Have you considered table-driven methods as an alternative to complicated inheritance structures?"
- [ ] BK-3: "Have you considered storing the table's data externally and reading it at run time so that the data can be modified without changing code?"
- [ ] BK-4: "If the table cannot be accessed directly via a straightforward array index (as in the age example), have you put the access-key calculation into a routine rather than duplicating the index calculation in the code?"

---

## Table Opportunity Identification

Use this to identify when tables may be better than logic:

### Logic Complexity Signals

- [ ] LC-1: "Writing 4th or more if/else branch for same classification?" → Red flag: Deep conditional chains
- [ ] LC-2: "Switch statement has >5 cases and growing?" → Red flag: Unbounded case growth
- [ ] LC-3: "Deeply nested conditionals for factor combinations?" → Red flag: Combinatorial explosion
- [ ] LC-4: "Same conditional logic repeated in multiple places?" → Red flag: Duplicated decision logic
- [ ] LC-5: "Multiple switch statements on same discriminator?" → Red flag: Scattered classification logic

### Data Volatility Signals

- [ ] DV-1: "Data changes more frequently than code?" → Good: External table; Bad: Hardcoded logic
- [ ] DV-2: "Customer or user controls the values?" → Good: Editable table; Bad: Requires code deployment
- [ ] DV-3: "Values are likely to be A/B tested?" → Good: Table variations; Bad: Code branches
- [ ] DV-4: "Format is customer-specific or configurable?" → Good: External data; Bad: Per-customer code paths
- [ ] DV-5: "New 'types' added regularly?" → Good: Add table row; Bad: Add code branch

### OOP Warning Signs

- [ ] OW-1: "Creating subclass just to change a data value?" → Red flag: Data disguised as behavior
- [ ] OW-2: "Subclass hierarchy mirrors data variants, not behavior?" → Red flag: Type explosion
- [ ] OW-3: "Polymorphism used but behavior doesn't actually vary?" → Red flag: False abstraction
- [ ] OW-4: "10+ subclasses differing mainly in configuration?" → Red flag: Class-per-configuration antipattern

---

## Table Design Checklist

Before implementing a table-driven solution:

### Access Method Selection

- [ ] AM-1: "Determined whether data keys directly (Direct Access)?"
- [ ] AM-2: "If sparse keyspace, considered Indexed Access?"
- [ ] AM-3: "If range-based, considered Stair-Step Access?"
- [ ] AM-4: "Documented rationale for access method choice?"

### Key Design

- [ ] KD-1: "Key transformation isolated in dedicated routine?" → Good: `KeyFromAge()`; Bad: Inline calculations
- [ ] KD-2: "Key routine has clear name (e.g., `KeyFromAge()`)?" → Good: Descriptive; Bad: `getKey()`, `transform()`
- [ ] KD-3: "Key transformation tested at boundaries?" → Red flag: Untested edge cases
- [ ] KD-4: "No duplicated key calculation code?" → Red flag: Copy-pasted key logic

### Table Content Design

- [ ] TC-1: "Determined what to store: data, action codes, or routine references?"
- [ ] TC-2: "Table entries have consistent structure?" → Red flag: Mixed data types/formats
- [ ] TC-3: "Default/fallback value defined if needed?"
- [ ] TC-4: "Edge cases handled (empty, out-of-range)?" → Red flag: Missing boundary handling

### Maintenance Considerations

- [ ] MC-1: "Considered external storage for volatile data?" → Good: JSON/CSV file; Bad: Hardcoded array
- [ ] MC-2: "Table initialization is centralized?" → Red flag: Scattered initialization
- [ ] MC-3: "Table is const/readonly if values don't change at runtime?"
- [ ] MC-4: "Adding new entry doesn't require code changes (if appropriate)?" → Good: Data-driven; Bad: Code-driven

---

## Access Method Selection Quick Reference

| Question | If YES → | If NO → |
|----------|----------|---------|
| Can data key directly into small contiguous range? | Direct Access | Continue |
| Is keyspace large/sparse but entries few? | Indexed Access | Continue |
| Are entries valid for ranges, not points? | Stair-Step Access | Reconsider fit |

---

## Table Implementation Checklist

During implementation:

### Direct Access

- [ ] DA-1: "Array bounds match expected key range?" → Red flag: Buffer overflow risk
- [ ] DA-2: "Off-by-one errors checked (0-based vs 1-based)?" → Red flag: Common indexing bug
- [ ] DA-3: "Out-of-range keys handled?" → Red flag: Unchecked array access
- [ ] DA-4: "Table initialization verified correct?"

### Indexed Access

- [ ] IA-1: "Index array populated correctly?" → Red flag: Missing index entries
- [ ] IA-2: "Invalid keys return distinguishable value?" → Good: -1 or null; Bad: Silent failure
- [ ] IA-3: "Index and main table kept in sync?" → Red flag: Orphaned entries
- [ ] IA-4: "Space savings vs complexity tradeoff acceptable?"

### Stair-Step Access

- [ ] SS-1: "Range boundaries correct (check `<` vs `<=`)?" → Red flag: Off-by-one at boundaries
- [ ] SS-2: "Top of each range covered?" → Red flag: Gap in coverage
- [ ] SS-3: "Loop terminates correctly for highest range?" → Red flag: Infinite loop
- [ ] SS-4: "Consider binary search for large lists?" → Good: O(log n); Bad: Linear scan for 100+ entries

---

## Code Review Checklist for Table-Driven Code

When reviewing existing table implementations:

- [ ] CR-1: "Access method appropriate for the data characteristics?"
- [ ] CR-2: "Key transformation isolated (not duplicated)?" → Red flag: Copy-pasted key logic
- [ ] CR-3: "Table initialization is readable and correct?"
- [ ] CR-4: "Edge cases handled (empty input, boundary values)?" → Red flag: Missing validation
- [ ] CR-5: "Table vs logic tradeoff justified (not over-engineered)?" → Red flag: Table for 2-3 cases
- [ ] CR-6: "External storage considered if data is volatile?" → Good: Configurable; Bad: Hardcoded volatile data
- [ ] CR-7: "Comments explain what table contains and how it's used?"

---

## Migration Checklist: Logic to Table

When converting existing if/else chains to tables:

### 1. Analyze

- [ ] MA-1: "Identified all branches in current logic?"
- [ ] MA-2: "Mapped each branch to data value?"
- [ ] MA-3: "Verified no side effects in conditions?" → Red flag: Conditionals with mutations

### 2. Design

- [ ] MD-1: "Chose appropriate access method?"
- [ ] MD-2: "Designed table structure?"
- [ ] MD-3: "Defined key transformation (if needed)?"

### 3. Implement

- [ ] MI-1: "Created table with all values?"
- [ ] MI-2: "Implemented lookup routine?"
- [ ] MI-3: "Handled edge cases?" → Red flag: Missing boundary handling

### 4. Verify

- [ ] MV-1: "All original test cases pass?"
- [ ] MV-2: "Boundary values tested?" → Red flag: Untested edge cases
- [ ] MV-3: "Performance acceptable?"
- [ ] MV-4: "Code is simpler (not just different)?" → Red flag: Complexity relocated, not reduced

---

## Quick Decision: Table vs Logic

| Criteria | Points for Table | Points for Logic |
|----------|------------------|------------------|
| Branches | 4+ | 2-3 |
| Data volatility | Changes often | Stable |
| Pattern | Lookup/classification | Complex conditions |
| Similar code | Repeated elsewhere | Unique |
| Inheritance use | Subclass per data value | True polymorphism |

**Scoring:** 3+ points for table → strongly consider table-driven approach.

---

## Red Flags

- [ ] RF-1: "Deep if/else chains (4+ levels)?" → Replace with table lookup
- [ ] RF-2: "Switch statement growing unbounded?" → Migrate to data-driven table
- [ ] RF-3: "Subclass per configuration value?" → Replace inheritance with table + data
- [ ] RF-4: "Duplicated key calculation?" → Extract to dedicated routine
- [ ] RF-5: "Hardcoded volatile data?" → Move to external storage (JSON/CSV)
- [ ] RF-6: "Table for 2-3 simple cases?" → Keep as logic, over-engineered
- [ ] RF-7: "Missing boundary validation?" → Add range checks and defaults
- [ ] RF-8: "Index and data out of sync?" → Validate consistency on initialization
- [ ] RF-9: "Linear search on large table?" → Use indexed or stair-step access
- [ ] RF-10: "Mixed data types in table?" → Standardize structure

---

Total items: 79
