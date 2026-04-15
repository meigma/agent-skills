---
name: diataxis
description: Provides guidance on writing documentation using the Diátaxis framework. Use when writing documentation, creating doc structure, organizing content into tutorials, how-to guides, explanations, or reference materials, or when deciding what type of documentation to write.
---

# Writing Documentation with Diátaxis

Diátaxis is a systematic framework for technical documentation that organizes content into four types based on user needs. Each type serves a distinct purpose and requires a different writing approach.

## The Four Documentation Types

| Type | Orientation | User Mode | Answers |
|------|-------------|-----------|---------|
| **Tutorial** | Learning | Studying | "Can you teach me...?" |
| **How-to Guide** | Goals | Working | "How do I...?" |
| **Reference** | Information | Working | "What is...?" |
| **Explanation** | Understanding | Studying | "Why...?" |

## Quick Decision Guide

```
What does the reader need?

├─ To LEARN something new
│  ├─ Through doing → Tutorial
│  └─ Through thinking → Explanation
│
└─ To ACCOMPLISH something now
   ├─ Complete a task → How-to Guide
   └─ Look up facts → Reference
```

## The Diátaxis Map

Two axes define the four quadrants:

|                        | Acquisition (Study) | Application (Work) |
|------------------------|--------------------|--------------------|
| **Action** (Doing)     | Tutorial           | How-to Guide       |
| **Cognition** (Thinking) | Explanation      | Reference          |

## Type Summaries

### Tutorials
- **Purpose:** Teach skills through guided hands-on experience
- **Audience:** Learners acquiring new abilities
- **Approach:** Concrete steps, visible results, minimal explanation
- **Voice:** "We will..." (teacher guiding student)
- **Details:** [tutorials.md](tutorials.md)

### How-to Guides
- **Purpose:** Help accomplish specific real-world tasks
- **Audience:** Practitioners applying existing knowledge
- **Approach:** Direct steps, flexible for variations, goal-focused
- **Voice:** "To do X, do Y" (practical directions)
- **Details:** [how-to-guides.md](how-to-guides.md)

### Reference
- **Purpose:** Provide accurate technical descriptions
- **Audience:** Practitioners needing facts during work
- **Approach:** Dry descriptions, consistent structure, comprehensive
- **Voice:** "X is/does Y" (neutral, factual)
- **Details:** [reference.md](reference.md)

### Explanation
- **Purpose:** Illuminate concepts and provide understanding
- **Audience:** Learners seeking to understand "why"
- **Approach:** Discursive, contextual, explores alternatives
- **Voice:** "X exists because..." (thoughtful discussion)
- **Details:** [explanation.md](explanation.md)

## Critical Rules

### Keep Types Separate
Each piece of documentation should be ONE type. Mixing types creates confusion:
- Don't explain concepts in tutorials (link to explanations instead)
- Don't teach in how-to guides (assume competence)
- Don't instruct in reference (just describe)
- Don't include reference details in explanations (link instead)

### Guard Against "Blur"
Adjacent types naturally blur together. Actively maintain boundaries:
- Tutorials → How-to guides: Don't lose pedagogical structure
- How-to guides → Tutorials: Don't add unnecessary teaching
- Reference → Explanation: Don't clutter facts with discussion
- Explanation → Reference: Don't lose discursive depth

### Structure Emerges Organically
- Don't create empty four-part scaffolding upfront
- Apply Diátaxis principles to individual pieces
- Let the structure emerge from following the principles
- Every improvement is worth publishing immediately

## Common Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| "Explain everything first" | Users feel like they're studying for a test | Lead with tutorials; link to explanations |
| Mixing types in one doc | Confuses purpose, frustrates readers | Split into separate documents by type |
| Tutorial as simplified how-to | Loses learning structure | Focus on skill acquisition, not task completion |
| Reference with digressions | Hard to find facts quickly | Keep descriptions dry; link to explanations |
| Empty Diátaxis structure | Hollow sections with no content | Build incrementally based on need |

## Writing Checklist

Before publishing any documentation:

- [ ] Identified the single documentation type this content serves
- [ ] Title clearly signals the type (Tutorial: "Learn X", How-to: "How to X", Reference: "X Reference", Explanation: "About X")
- [ ] Content stays within the boundaries of that type
- [ ] Cross-references link to other types rather than mixing content
- [ ] Structure matches the type's requirements
