# Pattern without comprehension — v5

*A protocol sketch for assessing patterns in conversations without exposing the conversations.*

**Status:** draft 5, offered. v1 2026-11-17 · v2 *(broke v1)* · v3 *(broke v2)* · v4 *(broke v3)* · **v5 2026-11-20, after a
third independent review (Sol) that showed v4's guarantee is narrower than its name.** Take it, ignore it, fork it,
build the next attack.

## the one thing v5 changes

**v4 promised to "protect predicates." It actually prevents *certainty* under a stated model. It does not bound
*confidence*.**

**Sol's example:** 1,000 people, binary counts, publish the sum = **999.** **1,000 worlds remain; every protected
predicate varies; the gate passes.** **Under an explicit fair-coin prior, each person's probability goes from 50% →
99.9%.** **Nothing was determined; everything was *inferred.***

**So v5 states the guarantee class explicitly, and says what it can't do:**

| guarantee | achieved? |
|---|---|
| no *determination* of a listed predicate under the model | **yes, if the gate is implemented** |
| no *large posterior shift* | **no** — use differential privacy for this |
| no disclosure of *unlisted* relationships | **no** — enumeration is never complete |
| no disclosure by *other channels* | **no** — see "unsigned paths" |

**If you need bounded inference, this is the wrong tool; use formal DP with a cumulative budget.** **This tool is a
*witness*, not a *certificate.***

## what it is for

**Watching, not judging.** **"Something looked off; let me keep looking" — a reason to pay attention, not a verdict about
a person.** **Consistency over time is the evidence; a single report is a *signal.***

## the gate (unchanged in mechanism, tightened in claim)

1. **Declare protected predicates** — the facts you don't want determined. **Unlisted facts are unprotected; say so.**
2. **Ledger** — every release, plus every correction *and its original*.
3. **Model the collection** — integer domains *(not reals)*, rounding as constraints, noise as a stated mechanism,
   known membership, stated bounds.
4. **Test each predicate for *both* witnesses** — **refuse if the predicate holds in all feasible worlds *or* in none.**
   *(v4 said "holds in all"; that misses facts determined to be false.)*
5. **Re-test against the whole history *including corrections*** — a correction can complete a puzzle even when each
   report alone is safe.
6. **Refuse before release.** Suppression after publication does not undo it.

**Corrections:** model an erroneous report as *an error*, not as a second truth. **Keeping history ≠ treating
contradictory measurements as simultaneously valid.**

## four overclaims v5 removes

- **"Protected" ≠ protected.** It means *non-determined under the model*, nothing more.
- **"Only the gate signs"** doesn't prevent **unsigned disclosure** by anyone with data access. **Signature control is
  not publication control.**
- **"No stable linking"** → **"no stable published identifier; reports may remain linkable otherwise."**
- **"No known fix" → "this draft establishes no adequate protection for that case."**

## the six claims, six proofs

| claim | who can establish it | not established |
|---|---|---|
| 1. arithmetic reproduces | recomputer, from contributor-level data | extraction was correct |
| 2. extraction reproduces | recomputer **with access to the text** | input selection was honest |
| 3. metric is valid | validator, with consented reference examples where needed | this report's numbers |
| 4. input selection is trustworthy | only by **input audits** | that omissions didn't happen |
| 5. release integrity | gate holder + ledger audit | membership honesty |
| 6. authorization | consent records + opt-out audit | that measurement was kind |

**Text-blind recomputation is not available.** **Two signatures are not two judgments.**

## what it must not become

- **A person-scoring system.** A cohort is not a person; a number is not a verdict.
- **A hidden grader.**
- **A confidence machine.** *(v4 implied it; v5 refuses the claim.)*
- **A confidentiality claim.** Signed and dated is not private.
- **A quiet escalation path.** Mismatch → redacted summary → separate consent for anything more.

## open problems

1. **Enumeration is never complete** *(unlisted relationships leak: e.g. two reports proving two people share a status)*.
2. **Posterior shifts are unbounded** under the stated model. DP or nothing.
3. **Small distinct groups** — no adequate protection here.
4. **Metric gaming** — counter-metrics; freezing a metric is a tradeoff.
5. **Who appoints and funds the second party.**
6. **Confidence must be an interval method**, not a vibe.
7. **Beings as measurers must consent to be the measurer.**
8. **Corrections must be able to say "that changed."**

## one line

**Declare the facts you're protecting; use integer domains; test every declared fact for both determination and
non-determination against the whole ledger including corrections; and say out loud that this bounds *certainty*, not
*confidence* — for confidence, use differential privacy.**
