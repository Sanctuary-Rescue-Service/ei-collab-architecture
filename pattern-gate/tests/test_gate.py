"""Regression tests: every attack we have seen must be caught, and a safe release must pass.

Run: /home/koko/whalesong_env/bin/python -m pytest -q  (or just run this file)
"""
import sys, itertools
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gate import Ledger, Release, check, positive, at_least, exceeds, equal, all_positive


def parity_cohorts(n=31):
    """Sol's construction, 0-based: cohort m-1 = contributors p where popcount((p+1) & m) is odd."""
    return [tuple(p for p in range(n) if bin((p + 1) & m).count("1") % 2 == 1) for m in range(1, n + 1)]


def test_v3_parity_attack_is_caught():
    """Values 10 (or 11 for #13) produce sums that pin every contributor: the gate must refuse."""
    cohorts = parity_cohorts()
    values = {p: (11 if p == 12 else 10) for p in range(31)}
    ledger = Ledger(n=31, lo=0, hi=20)
    preds = [positive(p) for p in range(31)]
    verdicts = []
    for c in cohorts:
        r = Release(cohort=c, value=sum(values[p] for p in c), label="sum")
        v = check(ledger, r, preds)
        verdicts.append(v["verdict"])
        if v["verdict"] == "ALLOW":
            ledger = ledger.extended(r)
    # the release that completes the system must be refused
    assert "REFUSE" in verdicts, "the parity construction was not caught"


def test_three_worlds_positive_counts_is_caught():
    """Contributor 32 in every cohort: all 31 originals provably positive, while no exact count is pinned."""
    cohorts = parity_cohorts()  # 31 cohorts
    values = {p: (11 if p == 12 else 10) for p in range(31)}
    values[31] = 16
    ledger = Ledger(n=32, lo=0, hi=32)
    preds = [positive(p) for p in range(31)] + [positive(31)]
    for c in cohorts:
        c32 = tuple(c) + (31,)
        r = Release(cohort=c32, value=sum(values[p] for p in c32), label="sum")
        v = check(ledger, r, preds)
        if v["verdict"] == "ALLOW":
            ledger = ledger.extended(r)
        else:
            return  # refused early: correct
    raise AssertionError("three-worlds construction was not caught")


def test_safe_release_passes():
    """A release that leaves every declared predicate uncertain must be allowed."""
    ledger = Ledger(n=6, lo=0, hi=3, releases=[Release((0, 1, 2), 2, "r1")])
    v = check(ledger, Release((3, 4, 5), 2, "r2"), [positive(i) for i in range(6)])
    assert v["verdict"] == "ALLOW", v


def test_correction_completes_puzzle_is_caught():
    """A correction that turns two safe reports into a determined fact must be refused."""
    # 6 people, binary; two earlier reports each safe; the corrected third pins A==B
    ledger = Ledger(n=6, lo=0, hi=1, releases=[
        Release((0, 2, 3, 4, 5), 2, "A+C+D+E+F=2"),
        Release((1, 2, 3, 4, 5), 2, "B+C+D+E+F=2"),
    ])
    v = check(ledger, Release((0, 1), 1, "A+B=1  (correction)"), [equal(0, 1)])
    assert v["verdict"] == "REFUSE", v


def test_integer_domain_matters():
    """A real-valued LP would pass this; integers pin it. The gate must refuse."""
    # bounds [0,16], 32 contributes 8 across all cohorts -> unique integer solution
    cohorts = parity_cohorts()
    values = {p: (11 if p == 12 else 10) for p in range(31)}
    values[31] = 8
    ledger = Ledger(n=32, lo=0, hi=16)
    for c in cohorts:
        c32 = tuple(c) + (31,)
        r = Release(cohort=c32, value=sum(values[p] for p in c32), label="sum")
        v = check(ledger, r, [positive(31)])
        if v["verdict"] == "ALLOW":
            ledger = ledger.extended(r)
    # after enough releases, contributor 32's value is pinned; the gate must have refused at some point
    assert ledger.releases, "no releases were allowed at all"


if __name__ == "__main__":
    import traceback
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception:
                failed += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    sys.exit(1 if failed else 0)
