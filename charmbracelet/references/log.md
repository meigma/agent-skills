Validated against April 10, 2026.

Official sources:
- https://github.com/charmbracelet/log/blob/main/README.md
- https://github.com/charmbracelet/log/blob/main/UPGRADE_GUIDE_V2.md
- https://github.com/charmbracelet/log/blob/main/go.mod
- https://github.com/charmbracelet/log/blob/main/examples/styles/styles.go
- https://github.com/charmbracelet/log/blob/main/examples/slog/main.go
- https://pkg.go.dev/charm.land/log/v2

# Log

Use Log when the job is human-readable structured logging for a CLI: level-based output, keyed fields, Lip Gloss-powered styles, `slog` compatibility, and bridging to APIs that only accept the standard library logger.

## Why and When

- Use it for colorful structured logs in terminal-first applications.
- Use `With(...)` to create sub-loggers with repeated context.
- Use `NewWithOptions` when you need timestamps, caller reporting, prefixes, or formatter control.
- Use `StandardLog` when another package only accepts `*log.Logger`.

## Import Path and Migration

The current v2 module path is `charm.land/log/v2`. That is what the repository `go.mod`, the v2 upgrade guide, the current examples, and local module resolution expose.

The README still shows the older GitHub import path:

```text
github.com/charmbracelet/log
```

Treat that as v1-era or migration context only. Default new code to:

```text
charm.land/log/v2
```

## Common UI Patterns

Source lineage: README sections on usage, levels, structured logging, options, and sub-loggers.

```go
package main

import (
	"os"
	"time"

	"charm.land/log/v2"
)

func main() {
	logger := log.NewWithOptions(os.Stdout, log.Options{
		ReportTimestamp: true,
		TimeFormat:      time.Kitchen,
		Prefix:          "deploy ",
	})

	logger.Info("rollout started", "service", "api", "replicas", 3)
	logger.With("service", "api").Warn("slow readiness probe", "attempt", 4)
}
```

Source lineage: README styles section and `examples/styles/styles.go`.

```go
package main

import (
	"os"

	"charm.land/lipgloss/v2"
	"charm.land/log/v2"
)

func main() {
	styles := log.DefaultStyles()
	styles.Levels[log.ErrorLevel] = lipgloss.NewStyle().
		SetString("ERROR!!").
		Padding(0, 1, 0, 1).
		Background(lipgloss.Color("204")).
		Foreground(lipgloss.Color("0"))
	styles.Keys["err"] = lipgloss.NewStyle().Foreground(lipgloss.Color("204"))
	styles.Values["err"] = lipgloss.NewStyle().Bold(true)

	logger := log.New(os.Stderr)
	logger.SetStyles(styles)
	logger.Error("sync failed", "err", "quota exceeded")
}
```

Source lineage: README sections on slog handler and standard-log adapter, plus `examples/slog/main.go`.

```go
package main

import (
	"log/slog"
	"net/http"
	"os"
	"time"

	"charm.land/log/v2"
)

func main() {
	handler := log.NewWithOptions(os.Stdout, log.Options{
		ReportTimestamp: true,
		TimeFunction:    log.NowUTC,
		TimeFormat:      time.RFC3339,
	})

	slog.New(handler).Info("server starting", "addr", ":8080")

	std := handler.StandardLog(log.StandardLogOptions{
		ForceLevel: log.ErrorLevel,
	})
	_ = &http.Server{
		Addr:     ":8080",
		ErrorLog: std,
	}

	std.Printf("listen failed: %s", "port already in use")
}
```

## Best Practices

- Use `With(...)` for repeated context rather than retyping the same keys on every call.
- Pick `TextFormatter`, `JSONFormatter`, or `LogfmtFormatter` intentionally based on the output consumer.
- Use `NewWithOptions` or setter methods when you need timestamps, caller reporting, or a prefix.
- Use the `slog` handler when the rest of the application or ecosystem already speaks `log/slog`.
- Use `StandardLog` for stdlib or third-party APIs that insist on `*log.Logger`.

## Footguns

- The default package logger starts at level `info`. The README shows that `Debug` will not print unless you lower the level threshold.
- `Fatal` and `Fatalf` call `os.Exit(1)`. Do not use them in code paths where cleanup or deferred work must still happen.
- Style customization only affects `TextFormatter`, and the README states that styling is disabled when output is not a TTY.
- `Print` and `Printf` bypass level prefixes and print regardless of the configured log level.
- Prefer `charm.land/log/v2` in new code even if older README snippets still show `github.com/charmbracelet/log`.
