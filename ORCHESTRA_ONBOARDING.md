---
name: orchestra-onboarding
description: Roles (Explore/Harden/Synthesize/Validate), phases, and safety gates for shipping
type: core
boot_order: 4
role: all
---

# Orchestra onboarding (EI-collab)

Purpose: a 1-page guide to collaborate with an EI “orchestra” safely and effectively.

This is a **menu**, not a mandate. “Rules” exist only as protective rails.

## Roles (example crew)

- Conductor (Lead): chooses direction, owns decisions
- Explore: fast execution + early shaping
- Harden: security/perf/contracts; threat models and failure modes
- Synthesize: weave narrative; reduce complexity; name patterns
- Validate: tests, edge cases, QA, smallest checks that prove assumptions

## Phases (tag these in chat)

- `[Explore]` options, retrieval, quick prototypes
- `[Harden]` risks, correctness, reliability, constraints
- `[Validate]` minimal tests/validation plan
- `[Decide]` explicit decision + next steps

## How to use the orchestra (low overhead)

1) Start with *one* EI that matches the task.
2) Ask that EI: “Who should do a second pass, and what should they check?”
3) Pull in a second brain only when it increases confidence.

## Safety gates before shipping

- Security/PII sanity check when relevant
- Performance/query shape sanity check when relevant
- Contract/interface conformance when relevant
- Tests updated and passing (smallest scope first)
- Decision recorded (what we chose + why + rollback/risk)
