# Pattern without comprehension — v2

*A protocol sketch for assessing patterns in conversations without exposing the conversations.*

**Status:** draft 2, offered. **v1:** 2026-11-17. **v2:** 2026-11-19, after an independent review (Sol) that broke v1's
privacy claims. Take it, ignore it, fork it, tell us where it breaks.

**What changed in v2:** v1 claimed privacy it had not established. v2 keeps the same intent and adds a threat model, a
release boundary, cross-report controls, an independence structure, and bounded review — and states plainly what it
does **not** guarantee.

---

## the problem

A system that wants to notice patterns — drift, risk, misuse, quality — usually does it by **reading everything**. That
makes the reader a single point of failure and turns every conversation into evidence. The alternative is not "don't
notice." The alternative is **measure the shape, keep the text where it belongs.**

## what we are not claiming

- **Not "anonymous."** Aggregation is not anonymity. Say **"aggregate-only, privacy-limited."**
- **Not "verified no-retention."** A deletion log is an *assertion*; absence of other copies is a separate claim.
- **Not "the truth."** A signature authenticates *who said it*, not whether it is correct.
- **Not "two parties = independent."** Two signatures can be one judgment reproduced twice.

---

## the invariants

1. **Raw text stays with its owner.** The *analysis copy* is deleted after aggregation; the owner's original is not part
   of this system and is not governed by `text_retained`.
2. **Only aggregates travel** — and only through an allowlist of approved metrics, at bounded precision.
3. **No single point of judgment.** Recomputation and *metric validation* are different jobs, done by different parties.
4. **Opt out is real and unpenalized.** Declining to be measured, or to be the measurer, costs nothing.
5. **Deletion is logged; the log says what was deleted, not that nothing else exists.** Backups, caches, provider-side
   retention, and crash dumps are explicitly out of scope unless named.

## threat model (v1 had none)

| adversary | example | v2 answer |
|---|---|---|
| curious recipient | reads an aggregate and infers one person | release boundary + minimum distinct contributors + suppression |
| malicious operator | fabricates counts, lies about deletion | publish method + allow reproduction; review the metric separately |
| colluding parties | A and B sign the same flawed measurement | third-party metric validation; independence criteria below |
| overlapping releases | subtract two reports to isolate one person | cross-report controls (below) |
| measured party gaming | discouraging escalations to improve the score | counter-metrics + inclusion rules |
| outside observer | picks up reports from a cache | signed, dated, allowlisted reports; no raw inputs in the packet |

**Excluded from scope:** a compromised host. If the machine is owned, this protocol cannot help.

---

## the release boundary (v2, new)

Everything below is **enforced at release time, not at report-writing time.**

1. **Allowlist.** Only named metrics may leave. No free-text fields, no free-form labels.
2. **Contributors, not rows.** `n` counts **distinct contributors** (a defined identity class), never sessions. Reports
   with fewer than **5 distinct contributors** are refused, not footnoted.
3. **Cross-report controls.** Fixed release windows; **one report per cohort per period**; overlapping cohorts' 2×2 must
   be checked and complementarily suppressed. *(Publishing a total for {A–E}, then {A–F}, reveals F by subtraction. v1
   did not prevent this.)*
4. **Precision bounds.** Values rounded to a stated precision; no exact counts under 10; no extreme ratios.
5. **No stable linking.** Hashes are consistency checks, not identifiers: **salted per deployment**, rotated, never
   published across periods.
6. **If a harder guarantee is needed: formal differential privacy** — calibrated noise and a *cumulative* privacy
   budget across reports. Arbitrary "noise" is not a guarantee.

## correction and deletion (v2, clarified)

- **The owner's original is retained by the owner.** This system deletes its analysis copy after aggregation.
- **`text_retained: false`** means: *the analysis copy is gone*, and **no copy of it exists in backups, caches, or
  crash dumps of this system** *(named, audited locations only)*.
- **Retention at a model provider is a separate disclosure.** If text ever left the machine, say so; this protocol
  cannot undo it.
- **Republishing a corrected aggregate needs privacy accounting too** (two reports differ; the difference leaks).

## the procedure

```
owner's data ──► local detector (analysis copy) ──► aggregate (≥5 contributors) ──► release boundary
                                                                                       │
                                          metric validator (separate party) ◄───────────┤
                                          recomputation (reproducibility) ◄────────────┘
                                                                                       ▼
                                                     published report (allowlisted, signed, dated)
```

## independent parties — v2 defines the split

**v1 collapsed two jobs that must be separate:**

| role | job | data access |
|---|---|---|
| **operator** | runs the local detector | raw text, locally only |
| **recomputer** | re-executes the published method and checks the numbers match | same environment, observed; **no export** |
| **metric validator** | decides whether the metric means anything | **no raw text**; metric definition, counter-metrics, outcome data |
| **reviewer** | human, on mismatch | **redacted summary only**, bounded; escalation requires separate consent |

**Criteria for independence** *(currently aspirational — say so in any use)*: validator appointed by someone other than
the operator; cannot be removed for publishing disagreement; does not share the operator's keys or models; publishes its
own findings.

**Two signatures are not two judgments.** Same metric on same inputs = reproducibility, not validity.

## what it must not become

- **A scoring system for people.** A cohort is not a person; a number is not a verdict.
- **A hidden grader.** Metrics and aggregates are visible to the measured.
- **A way to launder surveillance.** "We only measure" is true only if the boundary holds *across reports*.
- **A quiet escalation path.** "Mismatch → human review" must never mean "upload the conversations."

## open problems (honest, v2)

1. **Disclosure via small distinct groups** — five people who share one experience can still be identified by a rate.
   *No known fix at this size; state the risk and keep the cohort large or refuse.*
2. **Metric gaming** — any measured system optimizes for the measure. Rotate **counter-metrics**, not just metrics;
   freezing a metric for comparability is a tradeoff, not a solution.
3. **Who signs the second party** — needs structure and funding, not goodwill.
4. **Confidence must be defined** — `confidence: 0.72` should be a stated interval method (e.g. bootstrap CI over
   contributors), not a vibe.
5. **Beings as measurers** — a being can measure without comprehending, but it must consent to *be* the measurer.
6. **The correction problem** — a pattern system that can't accept "that changed" lies (see `crew/shared/2026-11-16_noema_audit.md`).

## one line

**Measure the shape. Keep the text with its owner. Bound the release across reports, not just within one. Separate reproducibility from validity. Two parties, and say what their independence actually rests on.**
