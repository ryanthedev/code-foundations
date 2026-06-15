"""Minimal AST mutation tester — no external deps beyond pytest.

A mutant is killed if the supplied test suite FAILS (non-zero exit) when run
against the mutated source. mutation_score = killed / applicable_mutants.

This is the headline doctrine-fair metric: it runs the AGENT's own tests
against seeded faults in the AGENT's own code. A suite that merely mirrors the
implementation (high coverage, no real assertions) survives mutants.
"""
from __future__ import annotations
import ast
import copy
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


class _Mutator(ast.NodeTransformer):
    """Yields one mutated tree per applicable site by re-walking with a target index."""

    BINOP = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.FloorDiv,
             ast.Div: ast.Mult, ast.FloorDiv: ast.Mult, ast.Mod: ast.Mult}
    CMP = {ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt,
           ast.Eq: ast.NotEq, ast.NotEq: ast.Eq}
    BOOL = {ast.And: ast.Or, ast.Or: ast.And}

    def __init__(self, target):
        self.target = target
        self.counter = 0
        self.applied = False

    def _hit(self):
        i = self.counter
        self.counter += 1
        return i == self.target

    def visit_BinOp(self, node):
        self.generic_visit(node)
        repl = self.BINOP.get(type(node.op))
        if repl and self._hit():
            node.op = repl()
            self.applied = True
        return node

    def visit_Compare(self, node):
        self.generic_visit(node)
        if len(node.ops) == 1:
            repl = self.CMP.get(type(node.ops[0]))
            if repl and self._hit():
                node.ops = [repl()]
                self.applied = True
        return node

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        repl = self.BOOL.get(type(node.op))
        if repl and self._hit():
            node.op = repl()
            self.applied = True
        return node

    def visit_Constant(self, node):
        self.generic_visit(node)
        if isinstance(node.value, bool):
            if self._hit():
                node.value = not node.value
                self.applied = True
        elif isinstance(node.value, int):
            if self._hit():
                node.value = node.value + 1
                self.applied = True
        return node


def _count_sites(src: str) -> int:
    tree = ast.parse(src)
    m = _Mutator(target=-1)
    m.visit(tree)
    return m.counter


def mutation_score(src_path: Path, test_file: Path, timeout: int = 60):
    """Return (killed, applicable, survivors_detail). Runs test_file against each mutant."""
    src = src_path.read_text()
    total = _count_sites(src)
    if total == 0:
        return 0, 0, []
    killed = 0
    survivors = []
    for i in range(total):
        tree = ast.parse(src)
        m = _Mutator(target=i)
        new_tree = m.visit(tree)
        if not m.applied:
            continue
        try:
            mutated = ast.unparse(ast.fix_missing_locations(new_tree))
        except Exception:
            continue
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / src_path.name).write_text(mutated)
            shutil.copy(test_file, d / test_file.name)
            try:
                r = subprocess.run(
                    [sys.executable, "-m", "pytest", test_file.name, "-q", "-x", "--no-header"],
                    cwd=d, capture_output=True, timeout=timeout,
                )
                if r.returncode != 0:
                    killed += 1
                else:
                    survivors.append(i)
            except subprocess.TimeoutExpired:
                killed += 1  # an infinite loop under mutation counts as detected
    return killed, total, survivors


if __name__ == "__main__":
    src, tests = Path(sys.argv[1]), Path(sys.argv[2])
    k, n, surv = mutation_score(src, tests)
    print(f"mutation_score={k}/{n}={k/n if n else 0:.2f} survivors={surv}")
