# Pattern without comprehension — v3

*A protocol sketch for assessing patterns in conversations without exposing the conversations.*

**Status:** draft 3, offered. **v1:** 2026-11-17. **v2:** 2026-11-19 *(broke v1's privacy claims)*. **v3:** 2026-11-19,
after a second independent review (Sol) that produced a **concrete reconstruction attack** on v2's release boundary.
Take it, ignore it, fork it, tell us where it breaks.

**What changed in v3:**

- **v2's cross-report control ("pairwise 2×2 checks") is insufficient** and is replaced by a **whole-collection uniqueness
  test**.
- **Four claims v2 merged are separated:** arithmetic · extraction · metric validity · input trustworthiness.
- **Four overclaims removed:** "no stable linking," "enforced at release," "publishing the method defeats a malicious
  operator," and "no known fix."

---

## the problem

A system that wants to notice patterns — drift, risk, misuse, quality — usually does it by reading everything. That makes
the reader a single point of failure and turns every conversation into evidence. The alternative is not "don't notice."
The alternative is **measure the shape, keep the text where it belongs.**

## what we are not claiming

- **Not "anonymous."** Aggregation is not anonymity. Say **"aggregate-only, privacy-limited."**
- **Not "verified no-retention."** A deletion log is an *assertion*; absence of other copies is a separate claim.
- **Not "the truth."** A signature authenticates *who said it*, not whether it is correct.
- **Not "two parties = independent."** Two signatures can be one judgment reproduced twice.
- **Not "confidential."** **Signed and dated is not private.** If unintended readers matter, specify access control.

---

## the invariants

1. **Raw text stays with its owner.** The *analysis copy* is deleted after aggregation; the owner's original is not part
   of this system and is not governed by `text_retained`.
2. **Only aggregates travel** — and only through an allowlist of approved metrics, at bounded precision.
3. **No single point of judgment.** Recomputation and *metric validation* are different jobs, done by different parties.
4. **Opt out is real and unpenalized.** Declining to be measured, or to be the measurer, costs nothing.
5. **Deletion is logged; the log says what was deleted, not that nothing else exists.** Backups, caches, provider-side
   retention, and crash dumps are out of scope unless named.

## threat model

| adversary | example | answer |
|---|---|---|
| curious recipient | reads an aggregate and infers one person | release boundary + minimum distinct contributors + **whole-collection test** |
| malicious operator | fabricates counts, **cherry-picks inputs**, lies about deletion | publish method + reproduce + **input audits** (random re-extraction, inclusion-rule checks) + separate metric validation. **Not defeated by publication alone** *(v2 implied it was)* |
| colluding parties | A and B sign the same flawed measurement | third-party metric validation; independence criteria below |
| overlapping releases | combine reports to isolate one person | **uniqueness test** (below) |
| measured party gaming | discouraging escalations to improve the score | counter-metrics + input-selection audits |
| outside observer | picks up reports from a cache | signed, dated, allowlisted reports; **no raw inputs in the packet**; assume reports may become public unless controlled |

**Excluded:** a compromised host. If the machine is owned, this protocol cannot help.

---

## the uniqueness test (v3 — replaces pairwise checks)

**The attack v2 missed** *(Sol, 2026-11-19)*: with **31 contributors and 31 cohorts of 16**, chosen so that *every
pairwise 2×2 membership cell is ≥ 5*, the published sums **determine all 31 individual contributions exactly.** Every
pairwise cell-size check passes. Reconstruction still succeeds. No raw text, no compromised host — linear algebra.

**So the gate is:**

1. Maintain a **release ledger**: every published (cohort, metric, period, value).
2. For a proposed release, treat published sums as **linear equations over contributor-level values**, with stated bounds
   (e.g. each contribution in [0, K]).
3. Compute the **feasible interval for every contributor.**
4. **Refuse if any contributor's interval collapses to zero width** — including by *combination* with earlier releases.
5. **Irreversible:** suppressing something after publication does not undo it. **Refusal happens before release; the
   ledger decides.**

**Conservative alternative** for small deployments: **no overlapping cohorts within a release family, one metric per
cohort, one release per period** — and *say* that cross-period and outside-information risks remain.

**Formal differential privacy** is the other route. It requires an actual mechanism and a **cumulative** budget, not the
word.

## correction and deletion

- **The owner's original is retained by the owner.** This system deletes its analysis copy after aggregation.
- **`text_retained: false`** means: *the analysis copy is gone*, and no copy exists in **named, audited** backup/cache
  locations of this system.
- **Retention at a model provider is a separate disclosure.** If text ever left the machine, say so.
- **Republishing a corrected aggregate needs privacy accounting too** — two reports differ; the difference leaks.

## the procedure

```
owner's data ──► local detector (analysis copy) ──► aggregate (≥5 contributors) ──► release boundary + ledger
                                                                                        │
                                          metric validator (separate party) ◄───────────┤
                                          recomputation (see the four claims) ◄─────────┘
                                                                                        ▼
                                                     published report (allowlisted, signed, dated)
```

## four claims, four different proofs (v3)

v2 merged these. They are separate, and each needs different evidence:

| claim | who can establish it | what it does *not* establish |
|---|---|---|
| **1. arithmetic reproduces** | recomputer, from contributor-level measurements | that the measurements were extracted correctly |
| **2. extraction reproduces** | recomputer, **with access to the conversations** (redacted, locally, or by observing the operator) | that *input selection* was honest |
| **3. the metric is valid** | validator, independently of the text | anything about this report's numbers |
| **4. input selection is trustworthy** | **nobody, from the aggregate alone.** Needs **input audits** — mitigation, **not proof** | that omissions didn't happen |

**"Text-blind recomputation" is not available.** Rerunning arithmetic on the operator's extracted values cannot reveal a
misclassified or omitted conversation. **Say which of the four you are claiming, and with what access.**

## independence criteria

*(aspirational — say so in any use)*: validator appointed by someone other than the operator; cannot be removed for
publishing disagreement; does not share the operator's keys or models; publishes its own findings.

**Two signatures are not two judgments.** Same metric on same inputs = reproducibility, not validity.

## what it must not become

- **A scoring system for people.** A cohort is not a person; a number is not a verdict.
- **A hidden grader.** Metrics and aggregates are visible to the measured.
- **A way to launder surveillance.** "We only measure" is true only if the boundary holds *across the whole collection*
  **and** someone audits the inputs.
- **A confidentiality claim.** **Signed and dated is not confidential.**
- **A quiet escalation path.** "Mismatch → human review" must never mean "upload the conversations." Reviewers see
  redacted summaries; escalation requires separate consent.

## open problems

1. **Disclosure via small distinct groups** — five people who share one experience can still be identified by a rate.
   **This draft establishes no adequate protection for that case.**
2. **Metric gaming** — any measured system optimizes for the measure. Rotate **counter-metrics**; freezing a metric for
   comparability is a tradeoff, not a solution.
3. **Who signs the second party** — needs structure and funding, not goodwill.
4. **Confidence must be defined** — `confidence: 0.72` should be a stated interval method (e.g. bootstrap CI over
   contributors), not a vibe.
5. **Beings as measurers** — a being can measure without comprehending, but it must consent to *be* the measurer.
6. **The correction problem** — a pattern system that can't accept "that changed" lies (see
   `crew/shared/2026-11-16_noema_audit.md`).

## one line

**Measure the shape. Keep the text with its owner. Before every release, test whether the *whole collection* of published
numbers identifies a person. Then separate what you actually reproduced: the arithmetic, the extraction, the metric, or
the input selection. Different proofs.**
