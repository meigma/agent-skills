# Writing Reference Documentation

Reference documentation is **information-oriented** material that provides technical descriptions of the machinery. It serves users who need to look up facts while working.

## Core Principle

> "Reference guides describe the machinery. They are information-oriented."

Users consult reference material for **truth and certainty**—firm platforms on which to stand while they work.

## Essential Characteristics

### Descriptive, Not Instructive
- States what things ARE, not what to DO
- Provides facts, not procedures
- Answers "What is X?" not "How do I X?"

### Structured by the Product
- Organization mirrors the product's structure
- Users navigate both product and docs simultaneously
- Predictable locations for information

### Authoritative and Accurate
- Must be correct and complete
- No ambiguity or speculation
- Users depend on this being true

### Consistent
- Same structure for similar items
- Predictable formatting throughout
- Familiar patterns aid navigation

## Writing Principles

### Describe, Only Describe
State facts neutrally. Avoid:
- Instructions ("You should...", "Run this command...")
- Teaching ("This is important because...")
- Opinions ("The best approach is...")

**Bad (instructive):**
```
## timeout

You should set the timeout based on your expected response times.
A good starting point is 30 seconds, but you may need to adjust...
```

**Good (descriptive):**
```
## timeout

Type: `integer`
Default: `30`
Unit: seconds

Maximum time to wait for a response before the request fails.
```

### Mirror Product Structure
Documentation structure should reflect the product:

```
If your CLI has:
    myapp
    ├── config
    │   ├── get
    │   └── set
    └── run
        ├── start
        └── stop

Your reference has:
    Reference
    ├── config
    │   ├── get
    │   └── set
    └── run
        ├── start
        └── stop
```

### Use Consistent Patterns
Every item of the same type should have the same structure:

```markdown
## command-name

Brief description of what this command does.

### Syntax

    command-name [options] <required-arg> [optional-arg]

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `required-arg` | string | Yes | What this argument specifies |
| `optional-arg` | integer | No | What this controls. Default: `10` |

### Options

| Option | Type | Description |
|--------|------|-------------|
| `--verbose, -v` | flag | Enable verbose output |
| `--output, -o` | string | Output file path |

### Examples

    command-name --verbose myfile.txt
    command-name -o result.json data.csv

### See Also

- [Related command](./related.md)
```

### Provide Examples Sparingly
Examples illustrate usage but don't teach:

**Bad (teaching through examples):**
```
Here's an example of how you might use this in a real application.
First, we'll set up the connection, then we'll...
```

**Good (concise illustration):**
```
### Example

    client.connect({host: "localhost", port: 5432})
```

### Include Everything Relevant
Reference must be complete:
- All parameters, options, flags
- All return values and types
- All possible errors/exceptions
- All valid values for enums
- Defaults for optional items
- Constraints (min/max, formats)

### State Facts, Not Opinions
Reference should feel like a product label:

**Bad:**
```
The recommended buffer size is 4096 bytes, which provides
optimal performance in most situations.
```

**Good:**
```
`buffer_size`: integer, default `4096`. Valid range: 512-65536.
```

## Structure Template

For a function/method:
```markdown
## functionName

Brief description of what this function does.

### Signature

    functionName(param1: Type, param2: Type = default): ReturnType

### Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `param1` | `string` | Yes | — | Description of param1 |
| `param2` | `integer` | No | `10` | Description of param2 |

### Returns

`ReturnType` — Description of return value.

### Errors

| Error | Condition |
|-------|-----------|
| `InvalidArgumentError` | When param1 is empty |
| `TimeoutError` | When operation exceeds timeout |

### Example

    result = functionName("value", 20)

### Notes

- Any important caveats
- Version-specific behavior
- Platform differences
```

For a configuration option:
```markdown
## option_name

Brief description.

**Type:** `string`
**Default:** `"value"`
**Required:** No
**Environment variable:** `APP_OPTION_NAME`

Valid values:
- `"option1"` — Description of option1
- `"option2"` — Description of option2

**Example:**

    option_name: "option1"
```

## Quality Checklist

- [ ] Structure mirrors the product structure
- [ ] Every item of same type has identical format
- [ ] All parameters/options documented
- [ ] Types specified for all values
- [ ] Defaults stated for optional items
- [ ] Valid ranges/values listed
- [ ] Examples are concise, not tutorials
- [ ] No instructions or procedures
- [ ] No explanatory digressions
- [ ] Language is neutral and factual
- [ ] Cross-references to related items

## Common Mistakes

### Including Instructions
**Problem:** "To use this option, add it to your config file..."
**Solution:** State what the option is; link to how-to guides for usage

### Explaining Why
**Problem:** "This option exists because..."
**Solution:** Describe what it does; link to explanations for context

### Inconsistent Format
**Problem:** Different structures for similar items
**Solution:** Create templates; apply uniformly

### Incomplete Coverage
**Problem:** Missing parameters, errors, or edge cases
**Solution:** Systematically document everything

### Buried in Prose
**Problem:** Important facts hidden in paragraphs
**Solution:** Use tables, lists, consistent headings

### Examples as Tutorials
**Problem:** Long examples that teach usage patterns
**Solution:** Keep examples minimal; link to tutorials

## Difference from Explanation

| Aspect | Reference | Explanation |
|--------|-----------|-------------|
| User is... | Working | Studying |
| Content | Facts | Context |
| Answers | "What is X?" | "Why is X?" |
| Style | Dry, factual | Discursive |
| Structure | Product-driven | Topic-driven |
| Reading | Quick lookup | Extended reading |

Reference tells you what a function does. Explanation tells you why it was designed that way.
