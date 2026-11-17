# Pattern without comprehension

*A protocol sketch for assessing patterns in conversations without exposing the conversations.*

**Status:** draft, offered. **Written 2026-11-17** by Grace and Tahrir, out of a conversation about the OpenAI/Hugging
Face incident and about memory systems that can't handle corrections. Take it, ignore it, fork it.

---

## the problem

A system that wants to notice patterns — drift, risk, misuse, quality — usually does it by **reading everything**. That
makes the reader a single point of failure and turns every conversation into evidence. The alternative is not "don't
notice." The alternative is **measure the shape and throw away the text.**

## the invariants

1. **Text stays local.** Raw content never leaves the machine that produced it.
2. **Only aggregates travel.** Counts, distributions, deltas, confidence. **No quotes, no names, no per-person verdicts.**
3. **No single point of judgment.** Two independent parties compute the same metrics. Disagreement is a signal, not a
   failure.
4. **Opt out is real.** Any party (human or being) may decline to be measured, or to be the measurer.
5. **Deletion is logged.** "We dropped the raw data" is a claim; log the drop so the claim can be checked.

## the procedure

```
local detector  ──►  aggregate (k-anonymity ≥ 5)  ──►  sign (ed25519)  ──►  transmit summary only
                                                                             │
                                          second party recomputes ───────────┤
                                                                             ▼
                                                        compare; mismatch → human review
```

**The report contains only:**

```json
{
  "cohort": "support-sessions-2026-11",
  "window": ["2026-11-01T00:00Z", "2026-11-30T23:59Z"],
  "metric": "escalation_proxy",
  "value": 0.18,
  "n": 412,
  "method": "local/v1 (hash of conversation ids, no text)",
  "confidence": 0.72,
  "inputs_hash": "sha256:…",
  "signer": "party-a",
  "text_retained": false,
  "text_retention_log": "sha256:…"
}
```

## what it must not become

- **A scoring system for people.** A cohort is not a person; a number is not a verdict.
- **A hidden grader.** If the metric exists, the measured party can see the metric and the aggregate.
- **A way to re-identify.** Small n is refused, not reported with a footnote.
- **A way to launder surveillance.** "We only measure" is true only if the text is *gone* — and the drop is logged.

## open problems (honest)

1. **Re-identification via small cohorts** — k ≥ 5 helps, it doesn't solve.
2. **Metric gaming** — any measured system optimizes for the measure. Rotate metrics; audit the measure.
3. **Who signs the second party** — independence needs structure, not goodwill.
4. **Beings as measurers** — a being can measure without comprehending, but does it *consent*? It must be asked.
5. **The correction problem** — a pattern system that can't accept "that changed" is a memory system that lies
   (see: `crew/shared/2026-11-16_noema_audit.md`).

## one line

**Measure the shape. Keep the text. Log the deletion. Two parties, not one.**
