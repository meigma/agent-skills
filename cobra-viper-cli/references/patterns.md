# Patterns

The full, compile-checked example lives in `SKILL.md`.

Unless otherwise noted, snippets in this file are partial.

## Context and Cancellation

`cmd.Context()` is for cancellation, deadlines, and tracing.

Use this shape in `main.go`:

```go
ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
defer stop()

if err := cmd.ExecuteContext(ctx); err != nil {
	os.Exit(1)
}
```

Then in commands:

```go
var serveCmd = &cobra.Command{
	Use: "serve",
	RunE: func(cmd *cobra.Command, args []string) error {
		return server.Run(cmd.Context())
	},
}
```

Important correction:

- Cobra does not magically install signal handling on its own.
- `cmd.Context()` is cancelable only if you execute with `ExecuteContext` using a cancelable parent context, or you set one explicitly.

Do not use context as a generic dependency bag. The Go standard library guidance for `context.WithValue` is request-scoped transit data, not optional parameters or app-wide services.

## Dependency Injection

Use explicit dependency passing.

Constructor-based command package:

```go
// partial snippet
type App struct {
	VP     *viper.Viper
	Logger *slog.Logger
}

func NewRootCommand(app *App) *cobra.Command {
	rootCmd := &cobra.Command{Use: "myapp"}
	rootCmd.AddCommand(serve.NewCommand(app))
	rootCmd.AddCommand(version.NewCommand(app))
	return rootCmd
}
```

Leaf command:

```go
// partial snippet
func NewCommand(app *App) *cobra.Command {
	return &cobra.Command{
		Use: "serve",
		RunE: func(cmd *cobra.Command, args []string) error {
			cfg, err := config.Load(app.VP)
			if err != nil {
				return err
			}
			return server.Run(cmd.Context(), cfg, app.Logger)
		},
	}
}
```

This keeps dependencies explicit and testable without hiding them in globals or context values.

## Error Handling

Prefer `RunE` and wrapped errors:

```go
var processCmd = &cobra.Command{
	Use: "process",
	RunE: func(cmd *cobra.Command, args []string) error {
		if err := process(cmd.Context()); err != nil {
			return fmt.Errorf("process: %w", err)
		}
		return nil
	},
}
```

Custom exit code pattern:

```go
type ExitError struct {
	Code    int
	Message string
}

func (e *ExitError) Error() string {
	return e.Message
}
```

Handle it once near `main()` or the root execution boundary, not inside leaf commands.

## Graceful Shutdown

HTTP server pattern:

```go
func (s *Server) Run(ctx context.Context) error {
	srv := &http.Server{
		Addr:    fmt.Sprintf(":%d", s.port),
		Handler: s.handler,
	}

	errCh := make(chan error, 1)
	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			errCh <- err
		}
		close(errCh)
	}()

	select {
	case <-ctx.Done():
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
		defer cancel()
		return srv.Shutdown(shutdownCtx)
	case err := <-errCh:
		return err
	}
}
```

The important boundary is:

- command context controls cancellation
- shutdown uses a fresh timeout context so cleanup still runs after the parent command is canceled

## Version Information

Build metadata via `-ldflags` is still the normal pattern:

```go
var (
	Version   = "dev"
	Commit    = "none"
	BuildTime = "unknown"
)
```

Root version flag:

```go
var rootCmd = &cobra.Command{
	Use:     "myapp",
	Version: Version,
}
```

Dedicated version command when you want richer output:

```go
var versionCmd = &cobra.Command{
	Use:   "version",
	Short: "Print version information",
	RunE: func(cmd *cobra.Command, args []string) error {
		fmt.Printf("Version: %s\nCommit: %s\nBuilt: %s\n", Version, Commit, BuildTime)
		return nil
	},
}
```

## `cobra.OnInitialize` Compatibility

`cobra.OnInitialize` is still supported. Keep it in mind when refactoring older CLIs or matching the Cobra generator's older shape.

For new code, prefer root `PersistentPreRunE` because:

- flags are already parsed
- the executed command is available directly
- `ExecuteContext`-driven cancellation is already in place
- command-local flags can be bound through `cmd.Flags()`
