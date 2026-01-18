# cc-table-driven-methods - Checklists

Source: Code Complete 2nd Edition, Chapter 18 (pp. 411-430)

---

## Table-Driven Methods Checklist (Verbatim from Book)

- [ ] Have you considered table-driven methods as an alternative to complicated logic?
- [ ] Have you considered table-driven methods as an alternative to complicated inheritance structures?
- [ ] Have you considered storing the table's data externally and reading it at run time so that the data can be modified without changing code?
- [ ] If the table cannot be accessed directly via a straightforward array index (as in the age example), have you put the access-key calculation into a routine rather than duplicating the index calculation in the code?

---

## Table Opportunity Identification Checklist

Use this to identify when tables may be better than logic:

### Logic Complexity Signals
- [ ] Writing 4th or more if/else branch for same classification
- [ ] Switch statement has >5 cases and growing
- [ ] Deeply nested conditionals for factor combinations
- [ ] Same conditional logic repeated in multiple places
- [ ] Multiple switch statements on same discriminator

### Data Volatility Signals
- [ ] Data changes more frequently than code
- [ ] Customer or user controls the values
- [ ] Values are likely to be A/B tested
- [ ] Format is customer-specific or configurable
- [ ] New "types" added regularly

### OOP Warning Signs
- [ ] Creating subclass just to change a data value
- [ ] Subclass hierarchy mirrors data variants, not behavior
- [ ] Polymorphism used but behavior doesn't actually vary
- [ ] 10+ subclasses differing mainly in configuration

---

## Table Design Checklist

Before implementing a table-driven solution:

### Access Method Selection
- [ ] Determined whether data keys directly (Direct Access)
- [ ] If sparse keyspace, considered Indexed Access
- [ ] If range-based, considered Stair-Step Access
- [ ] Documented rationale for access method choice

### Key Design
- [ ] Key transformation isolated in dedicated routine
- [ ] Key routine has clear name (e.g., `KeyFromAge()`)
- [ ] Key transformation tested at boundaries
- [ ] No duplicated key calculation code

### Table Content Design
- [ ] Determined what to store: data, action codes, or routine references
- [ ] Table entries have consistent structure
- [ ] Default/fallback value defined if needed
- [ ] Edge cases handled (empty, out-of-range)

### Maintenance Considerations
- [ ] Considered external storage for volatile data
- [ ] Table initialization is centralized
- [ ] Table is const/readonly if values don't change at runtime
- [ ] Adding new entry doesn't require code changes (if appropriate)

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
- [ ] Array bounds match expected key range
- [ ] Off-by-one errors checked (0-based vs 1-based)
- [ ] Out-of-range keys handled
- [ ] Table initialization verified correct

### Indexed Access
- [ ] Index array populated correctly
- [ ] Invalid keys return distinguishable value
- [ ] Index and main table kept in sync
- [ ] Space savings vs complexity tradeoff acceptable

### Stair-Step Access
- [ ] Range boundaries correct (check `<` vs `<=`)
- [ ] Top of each range covered
- [ ] Loop terminates correctly for highest range
- [ ] Consider binary search for large lists

---

## Code Review Checklist for Table-Driven Code

When reviewing existing table implementations:

- [ ] Access method appropriate for the data characteristics
- [ ] Key transformation isolated (not duplicated)
- [ ] Table initialization is readable and correct
- [ ] Edge cases handled (empty input, boundary values)
- [ ] Table vs logic tradeoff justified (not over-engineered)
- [ ] External storage considered if data is volatile
- [ ] Comments explain what table contains and how it's used

---

## Migration Checklist: Logic to Table

When converting existing if/else chains to tables:

1. **Analyze**
   - [ ] Identified all branches in current logic
   - [ ] Mapped each branch to data value
   - [ ] Verified no side effects in conditions

2. **Design**
   - [ ] Chose appropriate access method
   - [ ] Designed table structure
   - [ ] Defined key transformation (if needed)

3. **Implement**
   - [ ] Created table with all values
   - [ ] Implemented lookup routine
   - [ ] Handled edge cases

4. **Verify**
   - [ ] All original test cases pass
   - [ ] Boundary values tested
   - [ ] Performance acceptable
   - [ ] Code is simpler (not just different)

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
