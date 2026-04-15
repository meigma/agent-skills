# Project Structure

## Small CLI

For a small CLI with only a few commands, a single `cmd/` package is still fine:

```text
myapp/
├── main.go
├── cmd/
│   ├── root.go
│   ├── serve.go
│   └── version.go
├── internal/
│   └── config/
│       └── config.go
├── go.mod
└── go.sum
```

Use this when the whole command surface fits comfortably in one package and one team owns it.

## Medium CLI

Once the CLI grows past a handful of commands, keep business logic out of `cmd/`:

```text
myapp/
├── main.go
├── cmd/
│   └── root.go
├── internal/
│   ├── cli/
│   │   ├── serve/
│   │   │   └── command.go
│   │   ├── export/
│   │   │   └── command.go
│   │   └── version/
│   │       └── command.go
│   ├── config/
│   │   └── config.go
│   └── server/
│       └── server.go
├── go.mod
└── go.sum
```

This constructor-based layout matches current Cobra guidance better for medium and large CLIs.

## Large CLI

For complex CLIs with many domains, treat command packages as an interface layer:

```text
myapp/
├── main.go
├── cmd/
│   └── root.go
├── internal/
│   ├── app/
│   │   └── app.go
│   ├── cli/
│   │   ├── backup/
│   │   │   └── command.go
│   │   ├── db/
│   │   │   ├── command.go
│   │   │   ├── migrate.go
│   │   │   └── seed.go
│   │   ├── serve/
│   │   │   ├── command.go
│   │   │   ├── http.go
│   │   │   └── grpc.go
│   │   └── version/
│   │       └── command.go
│   ├── config/
│   │   ├── config.go
│   │   └── validate.go
│   ├── database/
│   └── server/
├── pkg/   # only if you intentionally expose public Go APIs
├── go.mod
└── go.sum
```

## Recommended File Roles

| Path | Role |
|---|---|
| `main.go` | install signal-aware context and execute the root command |
| `cmd/root.go` | root command, shared flags, config initialization, command wiring |
| `internal/cli/<feature>/command.go` | constructor returning `*cobra.Command` for one feature |
| `internal/config/config.go` | config structs and Viper-backed loaders |
| `internal/<domain>/...` | business logic, clients, services, storage |

## Keep `cmd/` Thin

Keep the command layer focused on:

- Cobra command definitions
- flag definitions
- Viper setup and bindings
- handoff into business logic

Avoid putting real domain logic in command files.

## Constructor Pattern

Recommended pattern at scale:

```go
// partial snippet
func NewCommand(vp *viper.Viper) *cobra.Command {
	cmd := &cobra.Command{
		Use:   "serve",
		Short: "Run the HTTP server",
		RunE: func(cmd *cobra.Command, args []string) error {
			cfg, err := config.Load(vp)
			if err != nil {
				return err
			}
			return server.Run(cmd.Context(), cfg)
		},
	}

	cmd.Flags().Int("port", 8080, "port to listen on")
	return cmd
}
```

That gives you:

- explicit dependencies
- smaller imports per package
- cleaner tests
- easier ownership boundaries across teams

## Anti-Patterns

Avoid these in new code:

- package-global mutable `*viper.Viper` used from every package
- storing app services in `context.Context`
- root packages importing every feature's internal implementation details
- command packages doing real business logic instead of delegating

## Bootstrap Notes

If you want scaffolding fast, `cobra-cli` is still the quickest start:

```bash
go install github.com/spf13/cobra-cli@latest
cobra-cli init
cobra-cli add serve
```

The generated layout is a starting point, not the final architecture. As the CLI grows, migrate toward constructor-based command packages and instance-based Viper usage.
