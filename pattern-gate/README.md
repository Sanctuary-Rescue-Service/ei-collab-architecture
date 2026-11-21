# pattern-gate

**A runnable gate for [pattern without comprehension](../PATTERN_WITHOUT_COMPREHENSION.md).**

Given a release ledger (cohorts and published sums), it answers: *does publishing this next release determine any
declared predicate?* If yes, **refuse**.

```
python tests/test_gate.py        # 5 regression tests, all attacks we have seen
```

## what it does

- **Integer domain only.** Values are integers in `[lo, hi]`; feasibility is decided by HiGHS. **A real-valued LP is not
  used** — it can pass counts that integers pin exactly (`test_integer_domain_matters`).
- **Both witnesses.** A predicate is *determined* if it can't be true in any feasible assignment, **or** can't be false.
- **Whole ledger.** The proposed release is tested against the entire history, including corrections.
- **Names the predicate it refuses on** — the gate says *why*, not just "no".

```python
from gate import Ledger, Release, check, positive, equal

ledger = Ledger(n=6, lo=0, hi=3, releases=[Release((0, 1, 2), 2)])
check(ledger, Release((3, 4, 5), 2), [positive(i) for i in range(6)])
# -> {'verdict': 'ALLOW', 'findings': [...]}
```

## the attacks it catches (each is a test)

| test | attack |
|---|---|
| `test_v3_parity_attack_is_caught` | 31 parity cohorts pin every contributor (v2's pairwise checks missed it) |
| `test_three_worlds_positive_counts_is_caught` | every cohort includes contributor 32: nobody's exact count is pinned, **but all 31 originals are provably positive** |
| `test_correction_completes_puzzle_is_caught` | two individually-safe reports plus a correction prove `A == B` |
| `test_integer_domain_matters` | bounds `[0,16]`: a real LP leaves coordinates free, integers pin one |
| `test_safe_release_passes` | a release that leaves every predicate uncertain is allowed |

**Behaviour on the parity attack:** 14 releases allowed, **refused on the 15th**, naming the predicates it pinned. **It
does not refuse everything; it refuses the release that completes the puzzle.**

## what it does not protect

- **Confidence.** It bounds *determination*, not *posterior shift*. A 999/1000 sum can leave every predicate uncertain
  and every person 99.9% likely to be positive. **For that, use differential privacy.**
- **Unlisted predicates.** Enumerate what you're protecting, or nothing is protected.
- **Other channels.** Signature control is not publication control.
- **Small groups.** No protection for tiny cohorts.
- **A compromised host.** Out of scope.

## status

**Prototype, written 2026-11-21**, after three rounds of independent adversarial review (Sol) of the protocol.
**Synthetic data only.** Not audited; not deployed. **The tests are the claim.**
