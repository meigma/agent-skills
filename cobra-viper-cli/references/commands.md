# Commands

The full, compile-checked example lives in `SKILL.md`.

Unless otherwise noted, snippets in this file are partial and focus on one command feature at a time.

## Root Command

Keep the root command small and explicit:

```go
var rootCmd = &cobra.Command{
	Use:          "myapp",
	Short:        "Short summary for humans",
	SilenceUsage: true,
}
```

Practical defaults:

- `RunE` over `Run`
- `SilenceUsage: true` for runtime failures
- `SilenceErrors: true` only if you want to format and print errors yourself

## Adding Subcommands

Simple package-local command:

```go
var serveCmd = &cobra.Command{
	Use:   "serve",
	Short: "Run the HTTP server",
	RunE: func(cmd *cobra.Command, args []string) error {
		return runServer(cmd.Context())
	},
}

func init() {
	rootCmd.AddCommand(serveCmd)
}
```

For larger CLIs, prefer constructor-based feature packages:

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

That pattern matches Cobra's current "modular at scale" docs better than growing one giant `cmd/` package forever.

## Argument Validation

Built-in validators cover most cases:

```go
var statusCmd = &cobra.Command{
	Use:  "status",
	Args: cobra.NoArgs,
	RunE: runStatus,
}

var renameCmd = &cobra.Command{
	Use:  "rename [old] [new]",
	Args: cobra.ExactArgs(2),
	RunE: runRename,
}

var deleteCmd = &cobra.Command{
	Use:  "delete [files...]",
	Args: cobra.MinimumNArgs(1),
	RunE: runDelete,
}
```

Use `PreRunE` for relationships between flags and `Args` for positional argument shape.

```go
var exportCmd = &cobra.Command{
	Use: "export",
	PreRunE: func(cmd *cobra.Command, args []string) error {
		if stdout && outPath != "" {
			return fmt.Errorf("--stdout and --out are mutually exclusive")
		}
		return nil
	},
	RunE: runExport,
}
```

## Lifecycle Hooks

Execution order is:

1. persistent pre-run
2. pre-run
3. run / `RunE`
4. post-run
5. persistent post-run

The footgun:

- By default, Cobra runs only the first persistent hook it finds in the command chain.
- If you want parent hooks to chain from root to leaf and back, set `cobra.EnableTraverseRunHooks = true`.

That matters for CLIs with nested parent commands like `myapp db migrate`.

Typical use:

```go
var rootCmd = &cobra.Command{
	Use: "myapp",
	PersistentPreRunE: func(cmd *cobra.Command, args []string) error {
		return initializeConfig(cmd)
	},
}

var exportCmd = &cobra.Command{
	Use: "export",
	PreRunE: func(cmd *cobra.Command, args []string) error {
		return validateExportFlags()
	},
	RunE: runExport,
}
```

## Groups, Aliases, and Deprecated Commands

Group help output once the CLI has enough surface area to justify it:

```go
func init() {
	rootCmd.AddGroup(
		&cobra.Group{ID: "manage", Title: "Management Commands"},
		&cobra.Group{ID: "query", Title: "Query Commands"},
	)

	backupCmd.GroupID = "manage"
	searchCmd.GroupID = "query"
}
```

Aliases:

```go
var deleteCmd = &cobra.Command{
	Use:     "delete",
	Aliases: []string{"rm", "remove"},
	RunE:    runDelete,
}
```

Hidden or deprecated commands:

```go
var debugCmd = &cobra.Command{
	Use:    "debug",
	Hidden: true,
	RunE:   runDebug,
}

var oldCmd = &cobra.Command{
	Use:        "old",
	Deprecated: "use 'new' instead",
	RunE:       runOld,
}
```

Keep deprecated flags and commands around long enough for a clean migration, then remove them deliberately.

## Shell Completion

Prefer the portable completion APIs Cobra now promotes:

- `ValidArgsFunction` for positional completions
- `RegisterFlagCompletionFunc` for flag value completions
- `MarkFlagFilename` / `MarkFlagDirname` for file and directory filtering

Positional completion:

```go
var getCmd = &cobra.Command{
	Use: "get [resource]",
	ValidArgsFunction: func(cmd *cobra.Command, args []string, toComplete string) ([]cobra.Completion, cobra.ShellCompDirective) {
		return []cobra.Completion{"pod", "service", "deployment"}, cobra.ShellCompDirectiveNoFileComp
	},
	RunE: runGet,
}
```

Flag completion:

```go
func init() {
	if err := getCmd.RegisterFlagCompletionFunc("output", func(cmd *cobra.Command, args []string, toComplete string) ([]cobra.Completion, cobra.ShellCompDirective) {
		return []cobra.Completion{"json", "yaml", "wide"}, cobra.ShellCompDirectiveDefault
	}); err != nil {
		panic(err)
	}

	if err := getCmd.MarkFlagFilename("config", "yaml", "yml", "json"); err != nil {
		panic(err)
	}
}
```

Completion gotchas:

- `ValidArgsFunction` runs after Cobra has parsed flags, so it can inspect flag state safely.
- Prefer the portable completion APIs above over old shell-specific completion hooks.
- Debug custom completion with the hidden `__complete` command.

## Error Handling

Prefer:

```go
var openCmd = &cobra.Command{
	Use:  "open <file>",
	Args: cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		b, err := os.ReadFile(args[0])
		if err != nil {
			return fmt.Errorf("read %s: %w", args[0], err)
		}
		fmt.Printf("%d bytes\n", len(b))
		return nil
	},
}
```

Avoid:

- `os.Exit()` inside commands
- printing usage for normal runtime failures
- assuming Cobra will format errors the way you want unless you have configured `SilenceErrors`
