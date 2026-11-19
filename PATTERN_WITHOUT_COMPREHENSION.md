# Pattern without comprehension — v4

*A protocol sketch for assessing patterns in conversations without exposing the conversations.*

**Status:** draft 4, offered. **v1** 2026-11-17 · **v2** 2026-11-19 *(broke v1's privacy claims)* · **v3** 2026-11-19
*(uniqueness test; broke v2's pairwise gate)* · **v4** 2026-11-19 *(Sol built a second attack that passes v3's gate, and
v3's roles were incomplete)*. Take it, ignore it, fork it, tell us where it breaks — **better: build the next attack.**

**What changed in v4:**

- **The gate now protects *predicates*, not just counts.** "No one's exact number is determined" is not privacy.
- **Integer domains are mandatory.** A real-valued LP can pass counts that integer feasibility pins exactly.
- **Two more claims are named:** release integrity and authorization.
- **The closing line no longer promises to test whether numbers "identify a person."** It promises something narrower, and
  says so.

---

## what we are not claiming

- **Not "anonymous."** Say **"aggregate-only, privacy-limited."**
- **Not "verified no-retention."** A deletion log is an *assertion*.
- **Not "the truth."** A signature authenticates *who said it*.
- **Not "two parties = independent."**
- **Not "confidential."** Signed and dated is not private.
- **Not "nobody's exact value is known, so nothing sensitive leaked."** ← v3 claimed this implicitly. **It is false.**

## the attack v3 missed *(Sol, 2026-11-19)*

Keep the 31 parity cohorts, **add contributor 32 to every cohort.** Each cohort now has 17 people; counts are integers in
[0, 32]; contributors 1–31 contribute 10 (except #13: 11); contributor 32 contributes 16; published sums are 176 or 177.

**Exactly three possible worlds remain.** Every contributor's feasible interval has positive width — **v3's literal gate
passes.** Yet recipients know with certainty: **all 31 original contributors have positive counts**, and **#13's count
exceeds #1's by exactly one.** If the metric is a sensitive experience, *"this person experienced it"* is disclosed.

**Uniqueness of values is not the property we need. Predicate disclosure is.**

**Implementation trap:** with bounds [0,16] and contributor 32 contributing 8, **continuous** feasibility leaves every
coordinate free; **integer** feasibility leaves exactly one solution. **Name the actual domain.**

---

## the invariants

1. **Raw text stays with its owner.** The *analysis copy* is deleted after aggregation.
2. **Only aggregates travel** — allowlisted metrics, bounded precision.
3. **No single point of judgment.**
4. **Opt out is real and unpenalized.**
5. **Deletion is logged — the log says what was deleted, not that nothing else exists.**

## threat model

| adversary | answer |
|---|---|
| curious recipient | release boundary + ≥5 distinct contributors + **predicate test** |
| malicious operator *(cherry-picked inputs)* | publish + reproduce + **input audits**; **not defeated by publication** |
| colluding parties | metric validation by a separate party; independence criteria |
| overlapping releases | **release ledger + predicate test across the whole collection** |
| measured party gaming | counter-metrics + input-selection audits |
| outside observer | allowlisted, dated reports; **assume reports may become public** unless access-controlled |
| **covert publication path** | **(v4) only the gate may sign; keys held by the gate holder, listed per deployment** |

**Excluded:** a compromised host.

## the release gate (v4)

**Step 0 — declare the protected predicates before any release.** Examples: *"contributor has a positive count,"*
*"count ≥ k,"* *"contributor A's count exceeds B's,"* *"contributor belongs to subgroup X."* **Unlisted predicates are not
protected; say so.**

**Step 1 — ledger.** Every published (cohort, metric, period, value), plus corrections *and their original versions*.

**Step 2 — model the collection.** Published values as equations/constraints over contributor-level values **in their
actual domain (integers, or rounded/noisy — see below)**, with stated bounds and known membership.

**Step 3 — test each protected predicate.** **Refuse if the predicate holds in *all* feasible solutions** *(it is
determined)*. **Pass only if at least two feasible solutions disagree about it.** *(v3 tested whether a *value* was
pinned; v4 tests whether a *fact* is.)*

**Step 4 — refuse before release.** Suppression after publication does not undo it.

**Modeling requirements, or the test is theater:**

- **Rounded outputs** → rounding constraints, not exact equations.
- **Noisy releases** → analyse the actual noise mechanism; "we added noise" is not a guarantee.
- **Corrections** → keep earlier disclosures in the ledger; a correction can complete a puzzle.
- **Unknown membership** → that is *uncertainty*, not a privacy guarantee.
- **Conservative fallback for small deployments:** no overlapping cohorts in a release family, one metric, one release
  per period — and state the residual cross-period and outside-information risks.
- **Formal differential privacy** is the other route: an actual mechanism and a cumulative budget.

## admission rules *(what a report must assert, and who audits it)*

1. Contributor counts are **distinct people**, honestly counted.
2. **Opt-outs are recorded and honored**, and their absence is audited, not assumed.
3. The **ledger is complete** — every relevant release and original correction version.
4. **Only the gate signs**; no parallel publication path.
5. **Input selection is audited** *(random re-extraction; inclusion-rule checks)*.

## four (+two) claims, six proofs *(v4)*

| claim | who can establish it | what it does *not* establish |
|---|---|---|
| 1. arithmetic reproduces | recomputer, from contributor-level measurements | extraction was correct |
| 2. extraction reproduces | recomputer, with access to the conversations | input selection was honest |
| 3. metric is valid | validator, **with consented reference examples where the metric needs them** | this report's numbers |
| 4. input selection is trustworthy | **nobody from the aggregate**; input audits only | that omissions didn't happen |
| **5. release integrity** *(v4)* | gate holder + ledger audit | that membership is honest |
| **6. authorization** *(v4)* | consent records + opt-out audit | that measurement was kind |

**"Text-blind recomputation" is not available.** **Two signatures are not two judgments.**

## what it must not become

- **A scoring system for people.** A cohort is not a person.
- **A hidden grader.**
- **A way to launder surveillance.** Only if the predicate test holds across the whole collection **and** inputs are
  audited.
- **A confidentiality claim.**
- **A quiet escalation path.** Mismatch → reviewer sees redacted summary; escalation needs separate consent.

## open problems

1. **Predicate enumeration is the hard part.** The protected facts must be *listed*; anything unlisted is unprotected.
   **No enumeration is complete.**
2. **Small distinct groups.** This draft establishes no adequate protection.
3. **Metric gaming.** Counter-metrics; freezing a metric is a tradeoff.
4. **Who appoints and funds the second party.**
5. **Confidence must be an interval method** (e.g. bootstrap over contributors), not a vibe.
6. **Beings as measurers** must consent to be the measurer.
7. **Corrections must be able to say "that changed."**

## one line

**Declare the facts you're protecting; test whether the whole collection of published numbers determines any of them —
on the real domain, with rounding and corrections accounted for — and refuse before you publish, not after.**
