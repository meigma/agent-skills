# Writing How-to Guides

How-to guides are **goal-oriented** documentation that helps users accomplish specific tasks. They provide directions through a problem toward a result.

## Core Principle

> "How-to guides serve users who are at work, applying their skills to real problems."

The user already knows what they want to do. Your job is to show them how to do it correctly and safely.

## Essential Characteristics

### Goal-Focused
- Address a specific, real-world objective
- Start with the end in mind
- Every step moves toward the goal

### Assumes Competence
- User understands the domain
- User knows what they want to achieve
- No need to teach foundational concepts

### Practical and Flexible
- Applies to real-world situations with variations
- Provides guidance that can be adapted
- Acknowledges that circumstances differ

### Problem-Solving
- Addresses actual challenges users face
- Anticipates complications
- Includes edge cases when relevant

## Writing Principles

### Name the Goal Precisely
Title should state the exact outcome:

**Bad titles:**
- "Deployment" (too vague)
- "Working with Databases" (not goal-oriented)
- "Authentication Guide" (not actionable)

**Good titles:**
- "How to deploy to production"
- "How to migrate a PostgreSQL database"
- "How to configure OAuth2 authentication"

### Start Immediately
No preamble. Get to the action:

**Bad (too much setup):**
```
Authentication is an important part of any application. There
are many ways to implement it, including sessions, tokens, and
OAuth. In this guide, we'll look at OAuth2 because...
```

**Good (immediate action):**
```
## Prerequisites
- Admin access to your OAuth provider
- Your application's callback URL

## Steps

1. Register your application with the OAuth provider...
```

### Use Direct Instructions
Write imperatives. Tell users what to do:

**Bad:**
```
You might want to consider backing up your database before
proceeding with the migration.
```

**Good:**
```
Back up your database:
    $ pg_dump mydb > backup.sql
```

### Handle Variations Concisely
Real-world situations vary. Address this efficiently:

```
3. Configure the connection string:

   For PostgreSQL:
       DATABASE_URL=postgres://user:pass@host:5432/db

   For MySQL:
       DATABASE_URL=mysql://user:pass@host:3306/db
```

### Provide Escape Routes
Tell users what to do if something goes wrong:

```
If the migration fails, restore from backup:
    $ psql mydb < backup.sql
```

### Don't Explain Why
Skip the reasoning. Link to explanations if users want context:

**Bad:**
```
We use connection pooling because it reduces the overhead of
establishing new connections, which improves performance under
load...
```

**Good:**
```
Enable connection pooling:
    pool_size: 10

See [About connection pooling](../explanation/connection-pooling.md)
for why this matters.
```

## Structure Template

```markdown
# How to [Specific Goal]

One-sentence description of what this guide accomplishes.

## Prerequisites

- Required access/permissions
- Required tools (with version if relevant)
- Required prior setup (link to other guides)

## Steps

### 1. [First Action]

Direct instruction.

    [command or code]

### 2. [Second Action]

Next instruction.

    [command or code]

If [variation condition]:
    [alternative instruction]

### 3. [Continue as needed...]

## Verification

How to confirm success:

    [verification command]

Expected result:
    [success indicator]

## Troubleshooting

### Problem: [Common issue]
**Solution:** [How to fix it]

### Problem: [Another issue]
**Solution:** [How to fix it]

## Related

- [How to undo this](./undo-this.md)
- [Reference: Configuration options](../reference/config.md)
```

## Quality Checklist

- [ ] Title is "How to [specific goal]"
- [ ] Goal is concrete and achievable
- [ ] Prerequisites are complete and specific
- [ ] Steps are numbered and sequential
- [ ] Each step has ONE action
- [ ] Uses imperative mood ("Run...", "Add...", "Configure...")
- [ ] Handles common variations
- [ ] Includes verification of success
- [ ] Has troubleshooting for likely problems
- [ ] Links to explanations rather than explaining inline
- [ ] No teaching or conceptual content

## Common Mistakes

### Teaching Instead of Directing
**Problem:** "First, let's understand how X works..."
**Solution:** Link to tutorials/explanations; give directions

### Vague Titles
**Problem:** "Database Guide"
**Solution:** "How to migrate from PostgreSQL 14 to 15"

### Missing Prerequisites
**Problem:** Guide fails partway because user lacks something
**Solution:** List everything needed upfront

### Too Rigid
**Problem:** Only works for one exact scenario
**Solution:** Note common variations; provide alternatives

### No Verification
**Problem:** User doesn't know if they succeeded
**Solution:** Always end with how to confirm success

### Mixing with Reference
**Problem:** Including complete API documentation inline
**Solution:** Link to reference docs for details

## Difference from Tutorials

| Aspect | Tutorial | How-to Guide |
|--------|----------|--------------|
| User is... | Learning | Working |
| Setting | Safe, controlled | Real-world, varied |
| Responsibility | Teacher's | User's |
| Path | Single, managed | Can branch |
| Complexity | Progressive | Direct |
| Failure | Must prevent | Help recover |

A tutorial teaches someone to drive. A how-to guide gives directions to a destination.
