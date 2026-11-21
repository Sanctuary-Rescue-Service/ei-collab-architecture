"""pattern-gate — does a release determine a declared predicate?

Implements the gate from PATTERN_WITHOUT_COMPREHENSION.md v5.

Model: N contributors, integer values in [lo, hi]. A release is the sum over a cohort. Given the whole ledger plus a
proposed release, each declared predicate is tested twice: can it be true in *some* feasible integer assignment? can it
be false in *some*? If either side is impossible, the predicate is *determined* -> refuse the release.

Sound by construction: predicates are compiled to explicit integer constraints (no heuristics), and feasibility is
decided by HiGHS through scipy.optimize.milp. Integer domain only — a real-valued LP is not used, because it can pass
counts that integers pin exactly (see tests: test_three_worlds_positive_counts).

Requires: numpy, scipy.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

MAXID = 10 ** 6  # sentinel: infinite upper bound


@dataclass(frozen=True)
class Release:
    cohort: tuple[int, ...]
    value: int
    label: str = ""


@dataclass
class Ledger:
    n: int
    lo: int = 0
    hi: int = 20
    releases: list[Release] = field(default_factory=list)

    def extended(self, r: Release) -> "Ledger":
        return Ledger(self.n, self.lo, self.hi, self.releases + [r])


# --- constraints: a set is a list of (coefficients: dict[int,int], sense, rhs) ---
def _row(n: int, coeffs: dict[int, int]) -> np.ndarray:
    a = np.zeros(n)
    for i, c in coeffs.items():
        a[i] = c
    return a


def _feasible(ledger: Ledger, extra: Sequence[tuple[dict[int, int], str, int]]) -> bool:
    n = ledger.n
    rows, senses, rhs = [], [], []
    for r in ledger.releases:
        rows.append(_row(n, {i: 1 for i in r.cohort}))
        senses.append("eq")
        rhs.append(r.value)
    for coeffs, sense, b in extra:
        rows.append(_row(n, coeffs))
        senses.append(sense)
        rhs.append(b)
    if not rows:
        return True
    A = np.vstack(rows)
    lb = np.array([b if s in ("eq", "ge") else -np.inf for s, b in zip(senses, rhs)], dtype=float)
    ub = np.array([b if s in ("eq", "le") else np.inf for s, b in zip(senses, rhs)], dtype=float)
    try:
        res = milp(c=np.zeros(n), constraints=LinearConstraint(A, lb, ub),
                   integrality=np.ones(n), bounds=Bounds(np.full(n, ledger.lo), np.full(n, ledger.hi)))
    except Exception:
        return False
    return bool(res.success)


# --- predicates: each has alternatives for its true side and for its false side (disjunctions) ---
@dataclass(frozen=True)
class Predicate:
    name: str
    true_sets: tuple[tuple[tuple[dict[int, int], str, int], ...], ...]
    false_sets: tuple[tuple[tuple[dict[int, int], str, int], ...], ...]


def positive(i: int) -> Predicate:
    return Predicate(f"contributor {i} has a positive value",
                     ((({i: 1}, "ge", 1),),),
                     ((({i: 1}, "le", 0),),))


def at_least(i: int, k: int) -> Predicate:
    return Predicate(f"contributor {i} >= {k}",
                     ((({i: 1}, "ge", k),),),
                     ((({i: 1}, "le", k - 1),),))


def exceeds(a: int, b: int) -> Predicate:
    return Predicate(f"contributor {a} > contributor {b}",
                     ((({a: 1, b: -1}, "ge", 1),),),
                     ((({a: 1, b: -1}, "le", 0),),))


def equal(a: int, b: int) -> Predicate:
    d = {a: 1, b: -1}
    return Predicate(f"contributor {a} == contributor {b}",
                     (((d, "eq", 0),),),
                     (((d, "ge", 1),), ((d, "le", -1),)))


def all_positive(ids: Iterable[int]) -> Predicate:
    ids = tuple(ids)
    return Predicate(f"all of {ids} have positive values",
                     tuple((({i: 1}, "ge", 1),) for i in ids),
                     tuple((( ({i: 1}, "le", 0),),) for i in ids))


def side_possible(ledger: Ledger, alternatives) -> bool:
    return any(_feasible(ledger, list(alt)) for alt in alternatives)


def check(ledger: Ledger, proposed: Release, predicates: Sequence[Predicate]) -> dict:
    """Decide whether publishing `proposed` (on top of the whole ledger) determines any predicate."""
    full = ledger.extended(proposed)
    findings = []
    for p in predicates:
        t = side_possible(full, p.true_sets)
        f = side_possible(full, p.false_sets)
        findings.append({"predicate": p.name, "true_possible": t, "false_possible": f,
                         "determined": not (t and f)})
    return {"release": proposed,
            "verdict": "REFUSE" if any(x["determined"] for x in findings) else "ALLOW",
            "findings": findings}
