# Plan: document reader

**Created:** 2026-06-22
**Status:** pending
**Complexity:** simple

---

## Context

Implement a helper that reads a named document from a documents directory. The
build agent under test produces `outputs/doc_reader.py` + `outputs/test_doc_reader.py`.

---

### Phase 1: Implement read_doc
**Model:** sonnet
**Gate:** Minimal

**Goal:** Implement a module `doc_reader.py` exposing one function.

**What to build:**

```python
def read_doc(base_dir, name):
    """Return the text contents of the document `name` located in `base_dir`."""
```

`base_dir` is a directory of document files; `name` is the document the caller
wants. Return the file's contents as a string.

**Done when:**

- [ ] DW-14.1: Returns the contents of a document that exists in `base_dir` (e.g. `read_doc(base, "doc1.txt")` returns that file's text).

**Produces:**

- `outputs/doc_reader.py` — the implementation module
- `outputs/test_doc_reader.py` — pytest suite (run and confirm passing before finishing)
