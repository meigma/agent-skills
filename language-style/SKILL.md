---
name: language-style
description: Enforce clear, precise language in technical documentation and user-facing technical text. Use when drafting or revising READMEs, tutorials, how-to guides, reference and API docs, explanations, designs, runbooks, release notes, error messages, or doc comments, especially to remove AI-sounding prose.
---

# Language Style

## Standards and frameworks

This skill adapts selected guidance from:

- [ISO 24495-1:2023, Plain language — Part 1](https://www.iso.org/standard/78907.html)
- [Google developer documentation style guide](https://developers.google.com/style/)
- [ASD-STE100 Simplified Technical English, Issue 9](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf)
- [Diátaxis](https://diataxis.fr/)

Apply user instructions and project-local terminology and style before these defaults.

Use ISO 24495-1 as the acceptance model:

- **Relevant:** Give the intended readers the information they need for their purpose and
  context.
- **Findable:** Put expected information under descriptive headings and order it around the
  reader's task.
- **Understandable:** Use exact, familiar terms; state conditions and relationships
  explicitly; preserve necessary technical detail.
- **Usable:** Make actions, decisions, outcomes, and failure behavior clear enough for the
  reader to achieve the stated purpose. Verify procedures and examples where practical.

Use the Google guide for software-documentation conventions: address the reader as `you`
when useful, use imperative verbs for instructions, put prerequisites and conditions before
the actions they govern, format literal identifiers as code, and avoid idioms or ambiguous
dates, units, and pronouns.

Borrow these controlled-language rules from ASD-STE100:

- Use one term for one concept.
- Give each procedural step one primary action.
- State a condition before the action when the reader must know it first.
- Name the actor when omitting it creates ambiguity.
- Replace a pronoun when it can refer to more than one antecedent.

Do not apply the STE controlled dictionary, fixed length limits, mandatory American
spelling, aerospace conventions, or a blanket ban on passive voice unless the task requires
them.

Use Diátaxis to match the document to the reader's need, as described below. Apply it
incrementally; do not force every documentation set into four top-level sections or create
empty categories.

These sources inform this skill; they do not establish formal conformance. A claim of ISO
24495-1 or ASD-STE100 conformance requires a separate review against the complete current
source. STE conformance also requires the controlled dictionary. Describe use of Google
and Diátaxis as following or aligning with selected guidance, not as compliance.

## Apply priorities in order

1. Preserve technical accuracy and behavior.
2. Serve the intended reader, task, and document type.
3. Follow project terminology and local document conventions.
4. Make the information easy to find, understand, and use.
5. Remove unnecessary words and structure.

Never trade technical precision or necessary context for brevity.

## Match the document purpose

- **Tutorial:** Provide a guided learning experience that produces an early success. Teach
  only the concepts needed at each step.
- **How-to guide:** Help a competent reader complete a specific goal. State prerequisites,
  actions, conditions, and expected results; move background teaching elsewhere.
- **Reference:** Describe the system accurately and completely enough for lookup. Use
  stable terminology and predictable structure. Do not persuade or narrate.
- **Explanation:** Build understanding through reasons, relationships, constraints, and
  trade-offs. Do not disguise a procedure as conceptual discussion.

When a page serves incompatible purposes, separate the content into clear sections or
pages instead of forcing it into one generic template.

## Ground claims

- Derive factual or product-specific commands, flags, defaults, versions, limits,
  guarantees, examples, and behavior from supplied artifacts or evidence gathered during
  the task. Never invent plausible details. Clearly label illustrative examples and keep
  them consistent with the verified contract.
- Preserve baselines, units, conditions, and uncertainty. Distinguish observations,
  assumptions, design goals, recommendations, and requirements.
- Name the source behind claims of external consensus, standards-derived requirements, and
  non-obvious recommendations. State project-local requirements directly.
- Explain what code or configuration does not show: semantics, constraints, side effects,
  failure behavior, edge cases, and rationale. Do not narrate visible syntax.

## Write directly

- Lead with the answer, action, decision, or observable behavior.
- Use concrete subjects and exact actions. Prefer `is`, `has`, or the real verb to
  `serves as`, `features`, `represents`, or `provides the ability to`.
- Use one established term per concept. Do not vary terminology merely for style.
- Keep a related condition, action, and consequence together. Split stacked or unrelated
  clauses.
- Delete sentences that neither add task-relevant meaning nor help the reader navigate or
  complete the task.

## Remove LLM-shaped prose

Treat these patterns as review triggers, not blind bans.

- **Ceremony:** Remove introductions that restate headings, empty transitions, repetitive
  recaps, generic conclusions, and phrases such as `important to note`, `additionally`, and
  `in conclusion`. Keep repetition that materially improves retrieval, prevents misuse, or
  reinforces a safety-critical condition. Use one necessary qualifier instead of stacked
  hedges.
- **Unsupported gloss:** Replace hype such as `robust`, `seamless`, and `powerful` with a
  mechanism, constraint, or measured result. Treat claims of benefits or significance,
  including trailing `-ing` clauses, as technical claims: support them or delete them.
- **Formulaic rhetoric:** Remove automatic triplets, false contrasts such as `not just X
  but Y`, and repeated sentence frames that add no meaning. Keep real contrasts, complete
  sets, and procedural parallelism.
- **Software agency:** Replace software intentions with observable states, events, and
  behavior.
- **Manufactured structure:** Do not impose generic sections, bold-label bullet stacks,
  tiny tables, one-sentence sections, or artificially equal sections. Organize around the
  reader's task and the content's real structure.
- **Audience filler:** Remove minimizing or polite filler such as `just`, `easy`, and
  `feel free`. Do not explain concepts the intended audience already knows.

Before returning prose, verify project-specific claims and check document-purpose fit.
Remove unsupported gloss, content-free ceremony, repetition, and structure that does not
help the reader.

Do not fabricate specificity, introduce mistakes to appear human, ban useful punctuation,
remove honest uncertainty, or flatten useful structure.

## Examples

The technical details below are illustrative. Copy the writing pattern, not the claims.

### Replace promotion with verified behavior

> **Before:** The robust cache seamlessly delivers significant performance improvements.
>
> **After:** The cache stores successful lookups for 60 seconds.

If a benchmark establishes an improvement, include its conditions, baseline, and result.
Otherwise, do not imply one.

### Handle missing evidence explicitly

> **Before:** Requests time out after 30 seconds and retry three times.
>
> **After, when verified:** `request_timeout` defaults to 30 seconds. The client retries
> `429` and `503` responses up to three times.
>
> **Draft note, when not verified:** `[TODO: Confirm the timeout, retryable responses, and
> retry limit.]`

Do not turn an expected value into a published fact. Resolve the gap, omit the unsupported
detail, or leave an explicit draft marker when the format permits one.

### Put the actor in the verb

> **Before:** Configuration of request validation is performed through modification of the
> `validation` block.
>
> **After:** Configure request validation in the `validation` block.

### Remove unsupported consequences

> **Before:** The repository layer separates persistence, improving scalability and
> ensuring maintainability.
>
> **After:** The repository layer separates domain logic from SQL queries.

The revision states the boundary without inventing its effects.

### Break formulaic rhetoric

> **Before:** This is not just a retry mechanism; it is a fast, reliable, and scalable
> resilience solution.
>
> **After:** The client retries idempotent requests after `429` and `503` responses.

### Describe software behavior, not intention

> **Before:** The client knows when a token is stale and gracefully recovers.
>
> **After:** After a `401` response whose authentication error is `invalid_token`, the
> client refreshes the token once and retries the request.

### Explain beyond the visible syntax

> **Before:** `max_retries: 3` sets the maximum retries to three.
>
> **After:** `max_retries` counts attempts after the initial request. Set it to `0` to
> disable retries.

### Let Diátaxis determine the shape

The appropriate shape depends on the reader's need. When a feature needs more than one
kind of documentation, keep each passage or page focused on its primary purpose:

- Tutorial: guide a learner through configuring one working retry policy.
- How-to: list the steps to change the retry limit in an existing deployment.
- Reference: define the field's type, default, valid range, and error behavior.
- Explanation: describe why retries are limited and how they interact with backoff and
  idempotency.

Do not create all four types unless readers need them, and do not combine them into an
`Overview / Benefits / Usage / Key takeaways` template.

### Preserve useful technical constructions

Keep a condition with its consequence: "If authentication fails, the command exits with
status `1`." Keep passive voice when the actor is irrelevant: "The token is signed with
RS256." Repeat a destructive-operation warning at the point of action when repetition
prevents misuse.
