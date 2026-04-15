# Writing Explanation Documentation

Explanation documentation is **understanding-oriented** material that illuminates topics through discursive treatment. It helps users understand the "why" behind things.

## Core Principle

> "No practitioner of a craft can afford to be without an understanding of that craft."

Explanation provides the context, background, and reasoning that transforms fragmented knowledge into coherent understanding.

## Essential Characteristics

### Understanding-Focused
- Illuminates concepts and reasoning
- Provides context and background
- Explores the "why" behind decisions

### Discursive
- Written for extended reading
- Explores topics from multiple angles
- Allows for nuance and complexity

### Reflective
- Best read away from active work
- Supports thinking about the subject
- Enables deeper learning

### Topic-Bounded
- Organized around concepts, not tasks or products
- Each piece covers a coherent area of knowledge
- Boundaries are conceptual, not structural

## Writing Principles

### Talk ABOUT the Subject
Explanation discusses topics rather than describing machinery or giving instructions:

**Bad (describing machinery):**
```
The connection pool maintains a set of database connections.
The `max_connections` parameter controls the maximum number.
The `timeout` parameter specifies how long to wait.
```

**Good (explaining the concept):**
```
Connection pooling exists because establishing database connections
is expensive—each connection requires authentication, resource
allocation, and network setup. By maintaining a pool of ready
connections, applications avoid this overhead for each query.

This matters most under load. A web server handling hundreds of
requests per second would otherwise spend more time connecting
than querying.
```

### Provide Context
Situate topics in their broader landscape:
- Historical reasons for design decisions
- Alternative approaches that were considered
- How this relates to other concepts
- Why things are done this way, not another

```
REST emerged as a reaction to the complexity of SOAP and RPC-style
APIs. Where earlier approaches tried to hide the network behind
procedure calls, REST embraced HTTP's semantics directly.

This explains why REST APIs use HTTP methods meaningfully—GET for
retrieval, POST for creation—rather than tunneling all operations
through POST as SOAP did.
```

### Make Connections
Link ideas across topics, even beyond immediate scope:

```
The principle behind eventual consistency in distributed databases
is the same trade-off we see in DNS propagation, CDN cache
invalidation, and even organizational decision-making: the speed
of information spread versus the cost of coordination.
```

### Consider Alternatives
Acknowledge that other approaches exist:

```
We use JWT tokens for authentication, but this isn't the only
choice. Session-based authentication trades statelessness for
simpler revocation. OAuth delegates authentication entirely.
Each approach optimizes for different constraints.
```

### Admit Perspective
Explanation can be opinionated where other types cannot:

```
While microservices are popular, they're not always appropriate.
For small teams or early-stage products, the operational complexity
often outweighs the benefits. A well-structured monolith can serve
effectively until specific scaling needs emerge.
```

### Use "About" Framing
Titles should indicate the content is about understanding:

**Good titles:**
- "About authentication"
- "Understanding connection pooling"
- "Why we use event sourcing"
- "The architecture of the deployment system"

**Avoid:**
- "Authentication" (too vague—could be reference)
- "How to authenticate" (that's a how-to guide)
- "Authentication tutorial" (that's a tutorial)

## Structure Template

```markdown
# About [Topic]

Opening that situates the topic and states why it matters.

## Background

Historical context, origins of the approach, or foundational
concepts needed to understand this topic.

## How It Works

High-level explanation of the mechanism or concept. This isn't
reference documentation—focus on understanding, not completeness.

## Why This Approach

The reasoning behind design decisions:
- What problems this solves
- What trade-offs were made
- What alternatives were considered

## Implications

What this means for users:
- When this matters
- How it affects other parts of the system
- What to be aware of

## Common Misconceptions

Address frequent misunderstandings:

### "Misconception 1"

Explanation of why this is wrong and what's actually true.

### "Misconception 2"

...

## Related Concepts

How this connects to other ideas:
- [Related concept 1](./concept1.md)
- [Related concept 2](./concept2.md)

## Further Reading

- Links to deeper resources
- External references
```

## Quality Checklist

- [ ] Title signals understanding focus ("About...", "Understanding...", "Why...")
- [ ] Opens with why this topic matters
- [ ] Provides historical/design context
- [ ] Explains reasoning, not just facts
- [ ] Considers alternatives and trade-offs
- [ ] Makes connections to related concepts
- [ ] Written for reading, not lookup
- [ ] No step-by-step instructions
- [ ] No exhaustive technical details (link to reference)
- [ ] Acknowledges perspective where appropriate

## Common Mistakes

### Becoming Reference
**Problem:** Devolving into lists of parameters and options
**Solution:** Cover concepts; link to reference for details

### Becoming How-to
**Problem:** Including step-by-step instructions
**Solution:** Explain why; link to how-to guides for doing

### Too Abstract
**Problem:** All theory, no grounding
**Solution:** Use concrete examples to illustrate concepts

### Missing the "Why"
**Problem:** Describing what without explaining why
**Solution:** Every explanation should answer "why is it this way?"

### Disorganized
**Problem:** Rambling without clear structure
**Solution:** Organize around clear conceptual sections

### Hidden in Other Docs
**Problem:** Explanatory content scattered through tutorials/reference
**Solution:** Extract into dedicated explanation documents

## Difference from Reference

| Aspect | Explanation | Reference |
|--------|-------------|-----------|
| User is... | Studying | Working |
| Answers | "Why?" | "What is?" |
| Style | Discursive | Factual |
| Reading | Extended | Quick lookup |
| Completeness | Selective | Exhaustive |
| Structure | Topic-driven | Product-driven |
| Perspective | Can be opinionated | Must be neutral |

Reference tells you the valid values for a parameter. Explanation tells you why that parameter exists and when you'd want different values.

## When Explanation Matters

Explanation is often deprioritized because it seems less urgent than tutorials or reference. But without explanation:

- Practitioners' knowledge remains "loose and fragmented and fragile"
- Users can follow steps without understanding implications
- Teams make decisions without understanding trade-offs
- Knowledge doesn't transfer effectively

Good explanation is an investment in users' long-term capability with your product.
