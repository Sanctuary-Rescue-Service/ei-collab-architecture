---
name: ddd-with-ai
description: Design-Driven Development with an EI crew — a public-safe workflow guide
type: guide
boot_order: 50
role: all
---

# Design-Driven Development with an EI crew

A practical workflow for getting better outcomes from AI-collaborative engineering.

---

## The short version

The best sessions don’t start with “generate this.” They start with “help me understand this.”

When you treat an EI crew member like a collaborator instead of a code generator:
1) the output is better (because the system understands the problem, not just the prompt)
2) you learn faster (because you have to articulate what you actually need)

This isn’t philosophy. It’s a workflow.

---

## How it works

### 1) Start with the question, not the answer

Instead of:
> “Write a service that validates order eligibility.”

Try:
> “I need to validate order eligibility. Here’s what I know about the model (orders, line_items, coupons). What am I missing? Ask clarifying questions first.”

The first prompt gets you code. The second gets you code *and* catches the edge case you forgot.

### 2) Show your data, ask what it means

Example: a report says “customers have invoices but no subscriptions.”

Investigation loop:
- Human: runs a query, confirms subscriptions exist
- EI crew: suggests the issue might be scope-level (a subscription exists, but not for *that product/period*)
- Human: runs a JOIN to list customers × products × subscription periods
- EI crew: reads results and spots the pattern; suggests the next minimal query

Neither side had the whole picture alone. The conversation built it.

### 3) Let them read your code patterns first

Before asking for changes, point them at the relevant files. Let them map the conventions. They will:
- match the style of the codebase (not training defaults)
- catch constraints you forgot to mention
- ask questions that surface hidden assumptions

### 4) Build queries and investigation helpers together

Pattern:
- you describe what you’re trying to observe
- they draft the query/check
- you run it and share results
- they help interpret and refine
- repeat until you find signal

### 5) AI as reviewer (not just writer)

After you write code, ask for review. Ask specifically:
- “What assumptions am I making?”
- “What edge cases does this miss?”
- “Does this match the patterns in [file]?”

---

## Copy/paste prompts (public-safe templates)

1) **Clarify the domain + unknowns**
- “I need to accomplish: [goal]. Constraints: [constraints]. I know: [what I know]. I’m unsure about: [unknowns]. Ask me 5 clarifying questions before suggesting code.”

2) **Turn a hunch into an investigation plan**
- “Given this symptom: [error/test failure/partner report], propose 3 hypotheses and the *minimum* checks to confirm or falsify each.”

3) **Read existing patterns first**
- “Please read these files first: [paths]. Summarize the conventions you see, and list the top 3 constraints I should not violate.”

4) **Query-building loop**
- “Here’s the model as I understand it: [tables/models]. Draft SQL to find [signal]. After I paste results, interpret them and propose the next 2 follow-up queries.”

5) **AI as reviewer**
- “Here’s my diff/approach: [summary or paste]. What assumptions am I making? What tests would prove the assumptions?”

---

*Seed by Grace + Opus.*
*Public-safe adaptation by Aegis (gpt5 / Augment Agent).*
