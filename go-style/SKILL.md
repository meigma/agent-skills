---
name: go-style
description: |
  Guide Go code toward modular package boundaries, disciplined godoc, restrained inline comments, hexagonal seams, and opt-in observability. Use when structuring Go modules, writing exported APIs, reviewing package layout, deciding where interfaces belong, or adding logging and metrics to production Go code. Activates for Go package design, exported function comments, exported struct fields, `slog.Logger`, OpenMetrics, ports and adapters, and Go style reviews.
---

# Go Style

Write Go code that stays easy to change. Optimize for package boundaries, clear contracts, strong exported API docs, and observability that consumers can opt into rather than inherit by surprise.

## Default Stance

- Keep root packages small and split growing code into subpackages with clear contractual boundaries.
- Add godoc comments to every exported function, method, and exported struct field.
- Keep function-body comments rare and purposeful.
- Bias toward hexagonal structure and ports-and-adapters thinking unless the module is too small or the existing project style would make that disruptive.
- Standardize core code on `slog.Logger`, defaulting to a no-op logger when the caller does not provide one.
- Make metrics optional and OpenMetrics-compatible. Never force registration or emission by default.

## Non-Negotiables

### Avoid Large Root Packages

Do not treat the root package as a dumping ground. When creating a module, prefer subpackages with clear boundaries over one oversized package that accumulates handlers, storage, business logic, transport code, and glue in the same namespace.

The same rule applies below the root. If a subpackage becomes large enough that private types and helpers are effectively shared across unrelated concerns, split it before the coupling hardens.

Break packages on contracts and responsibilities, not on arbitrary type buckets. `foo/httpapi`, `foo/store`, and `foo/runtime` are usually better boundaries than `foo/models`, `foo/helpers`, or `foo/misc`.

### Document Exported Functions And Methods

Every exported function and method gets a godoc comment.

- Start with a single top-level sentence that begins with the identifier name.
- Add a second paragraph only when the behavior needs more explanation than one sentence can carry.
- For high-traffic APIs used by external consumers, prefer to include at least one example in the doc comment.
- If the reader needs supporting material from elsewhere, link directly rather than naming a file and making them hunt for it.

Use doc comments to explain contract and behavior, not to restate parameter names mechanically.

### Document Exported Struct Fields

Every exported struct field gets a godoc-style comment explaining its purpose. Do not leave field meaning implicit just because the struct itself has a comment.

This matters especially for:

- options structs
- config structs
- API request and response types
- externally consumed data models

### Keep Inline Comments Sparse

Avoid superfluous comments inside function bodies. Comment code only when a typical engineer would need real help understanding why the code exists or why it is written that way.

A useful rule of thumb: if the pattern is uncommon, non-obvious, or would take more than about thirty seconds to grok, a comment is justified. This is especially important when the code deliberately deviates from a standard pattern for a strong reason. Document the reason there.

Do not narrate obvious control flow or variable assignment.

### Bias Toward Hexagonal Design

Prefer ports-and-adapters design, isolated business logic, and clear seams around external systems. That does not mean every tiny module needs a full ceremony of layers and interfaces, but even small projects should usually preserve the spirit:

- business logic separated from transport and storage
- interfaces at external boundaries
- adapters around infrastructure concerns

If an existing codebase does not use hexagonal patterns, stay consistent with the project unless you are specifically asked to reshape it. Do not introduce a half-hexagonal island into the middle of a codebase that is otherwise organized differently.

### Observability Must Be Useful And Optional

Production-facing or externally consumed Go code should include sufficient logging and optional metrics.

- Use `slog.Logger` throughout core code.
- Default to a no-op logger when no logger is provided.
- Keep metrics opt-in.
- Prefer OpenMetrics-compatible instrumentation.
- Do not register or emit metrics automatically unless the caller explicitly enables them.

When integration with another logging or metrics system is needed, adapt at the edge. The core should still speak `slog.Logger` and optional metrics interfaces or adapters.

## Preferred Patterns

### Package Shape

Keep the root package thin. Put behavior behind clear package seams.

```text
example.com/project/
  client.go
  options.go
  internal/runtime/
  internal/store/
  httpapi/
```

The exact tree will vary, but the pattern should be stable: small public surface, clear internal boundaries, and no giant kitchen-sink package.

### Exported Function Comment Shape

```go
// BuildClient constructs a Client from the provided Options.
//
// BuildClient validates the supplied endpoints, wires the selected adapters,
// and returns an error when the configuration cannot support a working client.
//
// Example:
//
//	client, err := BuildClient(Options{
//		BaseURL: "https://api.example.com",
//	})
//	if err != nil {
//		return err
//	}
//
// For a full wiring example, see
// https://github.com/example/project/blob/main/examples/client/main.go.
func BuildClient(opts Options) (*Client, error) {
    // ...
}
```

Lead with the contract. Expand only when behavior needs it. When you reference supporting material, use a direct link instead of saying "see client_example.go".

### Exported Struct Field Comment Shape

```go
type Options struct {
    // BaseURL is the upstream API endpoint used for all client requests.
    BaseURL string

    // Logger receives operational logs. Nil selects a no-op logger.
    Logger *slog.Logger

    // Metrics enables optional OpenMetrics-compatible instrumentation when set.
    Metrics Metrics
}
```

Field comments should explain purpose, not echo the field name with no added meaning.

### Logging And Metrics Injection

```go
func NewService(logger *slog.Logger, metrics Metrics, repo Repository) *Service {
    if logger == nil {
        logger = slog.New(slog.NewTextHandler(io.Discard, nil))
    }
    if metrics == nil {
        metrics = noopMetrics{}
    }

    return &Service{
        logger:  logger,
        metrics: metrics,
        repo:    repo,
    }
}
```

Let callers opt in to observability. Do not force global loggers, mandatory registries, or always-on collectors into the core package API.

## Review Heuristics

When writing or reviewing Go code, ask:

- Is the root package carrying too many responsibilities?
- Is a large subpackage starting to hide multiple concerns behind one namespace?
- Do exported functions and methods have real godoc comments, not placeholder summaries?
- If exported docs point to other material, do they link directly instead of naming a file vaguely?
- Do exported struct fields explain their purpose individually?
- Are inline comments only present where the code would otherwise be slow or risky to understand?
- Does the design preserve the spirit of ports and adapters where that makes sense?
- If the codebase is not hexagonal today, is this change staying consistent instead of introducing a partial rewrite?
- Does core code accept `slog.Logger` rather than committing the project to another logging shape?
- Are metrics optional and disabled by default unless the caller enables them?

## Anti-Patterns

- One oversized root package that mixes unrelated responsibilities.
- Letting subpackages grow so large that private helpers become shared coupling across unrelated code.
- Exported APIs without godoc comments.
- Exported struct fields without comments.
- Function-body comments that merely narrate obvious code.
- Dropping in interfaces, ports, and adapters halfway through a non-hexagonal codebase without a deliberate migration.
- Hardwiring production code to a concrete logger instead of `slog.Logger`.
- Emitting or registering metrics by default so every consumer pays for instrumentation they did not ask for.
