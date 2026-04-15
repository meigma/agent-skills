---
name: cobra-viper-cli
description: |
  Build production-ready Go CLI applications with Cobra and Viper. Use when: (1) Creating new CLI tools in Go, (2) Adding commands or subcommands to Cobra apps, (3) Managing flags and configuration with Viper, (4) Integrating environment variables and config files, (5) Implementing graceful shutdown or signal handling in CLIs, (6) Refactoring CLI code to follow current Cobra/Viper best practices. Covers parsed-flag config initialization, configuration precedence, instance-based Viper usage, command/package structure, and common footguns.
---

# Cobra + Viper CLI Development

## Version Target

This skill is grounded in the latest released versions available during review:

- Cobra `v1.10.2`
- Viper `v1.21.0`

Primary sources:

- Cobra docs: [working with flags](https://cobra.dev/docs/how-to-guides/working-with-flags/), [working with commands](https://cobra.dev/docs/how-to-guides/working-with-commands/), [shell completion](https://cobra.dev/docs/how-to-guides/shell-completion/), [context and tracing](https://cobra.dev/docs/how-to-guides/context-and-tracing/), [12-factor tutorial](https://cobra.dev/docs/tutorials/12-factor-app/)
- Cobra source: [user_guide.md at v1.10.2](https://github.com/spf13/cobra/blob/v1.10.2/site/content/user_guide.md), [command.go at v1.10.2](https://github.com/spf13/cobra/blob/v1.10.2/command.go)
- Viper source: [README at v1.21.0](https://github.com/spf13/viper/blob/v1.21.0/README.md), [TROUBLESHOOTING.md at v1.21.0](https://github.com/spf13/viper/blob/v1.21.0/TROUBLESHOOTING.md), [viper.go at v1.21.0](https://github.com/spf13/viper/blob/v1.21.0/viper.go)

## Default Production Pattern

1. Use `signal.NotifyContext` in `main.go`, then call `cmd.ExecuteContext(ctx)`.
2. Put config initialization in root `PersistentPreRunE`, not `cobra.OnInitialize`, so it runs after flags are parsed and before `RunE`.
3. Prefer an explicit `*viper.Viper` instance from `viper.New()` over the package-global singleton.
4. If a flag participates in config precedence, bind it to Viper and read it through Viper or a config struct loaded from Viper.
5. Ignore only config-not-found errors; surface parse, permission, and type errors.
6. Use `RunE` by default. Set `SilenceUsage` and `SilenceErrors` intentionally.
7. Use `cmd.Context()` for cancellation, deadlines, and tracing only. Do not use it as a dependency bag.

Compatibility note:

- `cobra.OnInitialize` still works and Cobra still documents it in older generator-style examples.
- For new code, prefer root `PersistentPreRunE`. It has the parsed command in hand, works cleanly with `ExecuteContext`, and keeps the config flow close to command execution.

## Configuration Precedence

Viper merges configuration sources in this order, highest first:

```text
1. viper.Set()
2. flags
3. environment variables
4. config file
5. remote key/value store
6. defaults
```

That order comes from Viper `v1.21.0` source and README.

## Quick Start

The following four files are a minimal, compile-checked example for Cobra `v1.10.2` and Viper `v1.21.0`.

```go
// main.go
package main

import (
	"context"
	"os"
	"os/signal"
	"syscall"

	"example.com/myapp/cmd"
)

func main() {
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	if err := cmd.ExecuteContext(ctx); err != nil {
		os.Exit(1)
	}
}
```

```go
// cmd/root.go
package cmd

import (
	"context"
	"errors"
	"os"
	"strings"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var (
	cfgFile string
	vp      = viper.New()
)

var rootCmd = &cobra.Command{
	Use:          "myapp",
	Short:        "Example Cobra/Viper CLI",
	SilenceUsage: true,
	PersistentPreRunE: func(cmd *cobra.Command, args []string) error {
		return initializeConfig(cmd)
	},
}

func Execute() error {
	return rootCmd.Execute()
}

func ExecuteContext(ctx context.Context) error {
	return rootCmd.ExecuteContext(ctx)
}

func initializeConfig(cmd *cobra.Command) error {
	vp.SetDefault("log-level", "info")
	vp.SetDefault("port", 8080)

	vp.SetEnvPrefix("MYAPP")
	vp.SetEnvKeyReplacer(strings.NewReplacer("-", "_", ".", "_"))
	vp.AutomaticEnv()

	if cfgFile != "" {
		vp.SetConfigFile(cfgFile)
	} else {
		vp.SetConfigName("config")
		vp.SetConfigType("yaml")
		vp.AddConfigPath(".")

		home, err := os.UserHomeDir()
		if err == nil {
			vp.AddConfigPath(home + "/.myapp")
		}
	}

	if err := vp.BindPFlags(cmd.Flags()); err != nil {
		return err
	}

	if err := vp.ReadInConfig(); err != nil {
		var notFound viper.ConfigFileNotFoundError
		if !errors.As(err, &notFound) {
			return err
		}
	}

	return nil
}

func init() {
	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file path")
	rootCmd.PersistentFlags().String("log-level", "info", "log level")
}
```

```go
// cmd/serve.go
package cmd

import (
	"fmt"

	"example.com/myapp/internal/config"
	"github.com/spf13/cobra"
)

var serveCmd = &cobra.Command{
	Use:   "serve",
	Short: "Print the resolved server config",
	RunE: func(cmd *cobra.Command, args []string) error {
		cfg, err := config.Load(vp)
		if err != nil {
			return err
		}

		fmt.Printf("Serving on :%d (log-level=%s)\n", cfg.Port, cfg.LogLevel)
		return nil
	},
}

func init() {
	serveCmd.Flags().Int("port", 8080, "port to listen on")
	rootCmd.AddCommand(serveCmd)
}
```

```go
// internal/config/config.go
package config

import (
	"fmt"

	"github.com/spf13/viper"
)

type Config struct {
	LogLevel string `mapstructure:"log-level"`
	Port     int    `mapstructure:"port"`
}

func Load(vp *viper.Viper) (Config, error) {
	var cfg Config
	if err := vp.Unmarshal(&cfg); err != nil {
		return Config{}, fmt.Errorf("unmarshal config: %w", err)
	}
	return cfg, nil
}
```

Why this pattern:

- `PersistentPreRunE` sees the exact command being executed, so `BindPFlags(cmd.Flags())` can include local flags defined on subcommands.
- `ExecuteContext` lets `cmd.Context()` carry cancellation to command logic.
- `viper.New()` keeps tests and larger CLIs predictable.
- The quick start uses `Unmarshal`, not `UnmarshalExact`, because a full bound flag set can include Cobra-managed keys like `help` that do not belong in your app config struct.

## Rules of Thumb

- Read flags with `cmd.Flags().Get*()` when you only care about the flag itself.
- Read through Viper or an unmarshaled config struct when you want flag/env/config/default precedence.
- Use local flags by default. Promote to persistent flags only for truly global concerns.
- Use `PreRunE` for command-local validation and root `PersistentPreRunE` for shared initialization.
- Keep `cmd/` thin. Push business logic into `internal/`.

## Common Footguns

| Footgun | Why it bites | Preferred pattern |
|---|---|---|
| Using `cmd.Flags().Get*()` after binding to Viper | It sees the flag/default, not env/config overrides | Use `vp.Get*()` or unmarshal config from Viper |
| Swallowing every `ReadInConfig` error | Bad config silently looks like "no config" | Ignore only `ConfigFileNotFoundError` |
| Using package-global Viper everywhere | Harder tests, unexpected cross-command coupling | Create `vp := viper.New()` and pass it intentionally |
| Assuming root persistent hooks always chain | Cobra runs only the first persistent hook by default | Set `cobra.EnableTraverseRunHooks = true` only when you need full chaining |
| Storing config/logger/app in `context.Context` | Conflicts with Go context guidance | Pass dependencies explicitly or capture them in constructors |
| Expecting `AutomaticEnv` to magically populate every `Unmarshal` field | Environment-backed struct loading has edge cases | Set defaults, bind env keys explicitly, or use advanced bind-struct support |

## Detailed References

- **[Project Structure](references/project-structure.md)**: small vs modular layouts, constructor-based command packages
- **[Commands](references/commands.md)**: hooks, groups, aliases, errors, completions
- **[Configuration](references/configuration.md)**: flags, env vars, config files, unmarshaling, Viper caveats
- **[Patterns](references/patterns.md)**: cancellation, graceful shutdown, DI, versioning, compatibility notes
