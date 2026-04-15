# Configuration

The end-to-end, compile-checked example lives in `SKILL.md`.

Unless otherwise noted, snippets in this file are partial and show only the lines that matter for the pattern being discussed.

## Flag Definition Basics

Use local flags by default and persistent flags only for truly global concerns.

```go
func init() {
	serveCmd.Flags().Int("port", 8080, "port to listen on")
	serveCmd.Flags().Duration("timeout", 30*time.Second, "request timeout")
	serveCmd.Flags().StringSlice("tag", nil, "repeatable tag")

	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file path")
	rootCmd.PersistentFlags().Bool("verbose", false, "enable verbose logging")
}
```

Useful flag-group helpers from Cobra:

```go
func init() {
	exportCmd.Flags().Bool("json", false, "output JSON")
	exportCmd.Flags().Bool("yaml", false, "output YAML")

	if err := exportCmd.MarkFlagsOneRequired("json", "yaml"); err != nil {
		panic(err)
	}
	if err := exportCmd.MarkFlagsMutuallyExclusive("json", "yaml"); err != nil {
		panic(err)
	}

	loginCmd.Flags().String("username", "", "username")
	loginCmd.Flags().String("password", "", "password")
	if err := loginCmd.MarkFlagsRequiredTogether("username", "password"); err != nil {
		panic(err)
	}
}
```

## Binding Flags to Viper

Two valid binding styles:

1. Bind a specific flag when the flag is defined.
2. Bind the full parsed flag set in root `PersistentPreRunE`.

Specific flag binding:

```go
func init() {
	serveCmd.Flags().String("db-host", "localhost", "database host")
	if err := vp.BindPFlag("database.host", serveCmd.Flags().Lookup("db-host")); err != nil {
		panic(err)
	}
}
```

Binding the currently executed command's full flag set:

```go
func initializeConfig(cmd *cobra.Command) error {
	return vp.BindPFlags(cmd.Flags())
}
```

Important behavior from Viper:

- `BindPFlag` and `BindPFlags` are lazy. The flag value is read when you call `vp.Get*()` or `vp.Unmarshal*()`.
- If you want env/config/default precedence, do not read the original flag variable after binding. Read through Viper instead.
- `cmd.Flags().Get*()` does not become Viper-aware.

## Environment Variables

Recommended setup:

```go
vp.SetEnvPrefix("MYAPP")
vp.SetEnvKeyReplacer(strings.NewReplacer("-", "_", ".", "_"))
vp.AutomaticEnv()
```

Common mappings:

| Config key | Environment variable |
|---|---|
| `port` | `MYAPP_PORT` |
| `log-level` | `MYAPP_LOG_LEVEL` |
| `database.host` | `MYAPP_DATABASE_HOST` |

Important Viper rules:

- Viper config keys are case-insensitive.
- Environment variable names are case-sensitive.
- If you call `BindEnv("port", "SERVER_PORT")`, Viper looks for `SERVER_PORT` exactly. It does not prepend the configured prefix when you pass an explicit env var name.
- Empty env vars are treated as unset by default. Call `vp.AllowEmptyEnv(true)` only when an empty string is a real, intentional value in your app.

Example:

```go
vp.SetEnvPrefix("MYAPP")
vp.AutomaticEnv()
vp.AllowEmptyEnv(true) // only if empty string should override lower-precedence sources
```

## Config Files

Recommended loader shape:

```go
func initializeConfig(cmd *cobra.Command) error {
	if cfgFile != "" {
		vp.SetConfigFile(cfgFile)
	} else {
		vp.SetConfigName("config")
		vp.SetConfigType("yaml")
		vp.AddConfigPath(".")
		vp.AddConfigPath("/etc/myapp/")
		if home, err := os.UserHomeDir(); err == nil {
			vp.AddConfigPath(home + "/.myapp")
		}
	}

	if err := vp.BindPFlags(cmd.Flags()); err != nil {
		return err
	}

	if err := vp.ReadInConfig(); err != nil {
		var notFound viper.ConfigFileNotFoundError
		if !errors.As(err, &notFound) {
			return fmt.Errorf("read config: %w", err)
		}
	}

	return nil
}
```

Guidance:

- In Viper `v1.21.0`, the not-found type is `viper.ConfigFileNotFoundError`.
- Ignore only the not-found case. A malformed config file should fail the command.
- If you need to report which file won, use `vp.ConfigFileUsed()`.
- If you watch config changes, add all config paths before `WatchConfig()`.

Watching for changes:

```go
vp.OnConfigChange(func(e fsnotify.Event) {
	log.Printf("config changed: %s", e.Name)
})
vp.WatchConfig()
```

## Unmarshaling into Structs

Use `mapstructure` tags, not `yaml` or `json` tags, for Viper unmarshaling.

```go
type Config struct {
	LogLevel string        `mapstructure:"log-level"`
	Port     int           `mapstructure:"port"`
	Timeout  time.Duration `mapstructure:"timeout"`
}
```

Default app-level loader:

```go
func Load(vp *viper.Viper) (Config, error) {
	var cfg Config
	if err := vp.Unmarshal(&cfg); err != nil {
		return Config{}, fmt.Errorf("unmarshal config: %w", err)
	}
	return cfg, nil
}
```

When to use which:

- `Unmarshal`: default for app-level config when the same Viper instance also has bound flags
- `UnmarshalExact`: fail fast on typos when the Viper key space intentionally matches the target struct

Useful Viper behavior:

- The default decode hooks already handle `time.Duration` strings and comma-separated string slices.
- `vp.AllSettings()` is a good debugging view when precedence is confusing.
- `vp.IsSet(key)` is safer than inferring "unset" from a zero value returned by `Get*()`.

## Important Viper Gotchas

### `AutomaticEnv` plus `Unmarshal`

This is the biggest footgun in real projects.

`AutomaticEnv()` works naturally with `vp.Get*()`. For `Unmarshal`, env-backed values are easiest when the key already exists through one of these:

- a default
- a bound flag
- a config file key
- an explicit `BindEnv`

Practical rule:

- For stable app config, set defaults or bind env keys explicitly.
- If you need env-only, struct-driven loading with no prior keys, Viper exposes `viper.NewWithOptions(viper.ExperimentalBindStruct())`, but that is advanced and should not be the default pattern in this skill.

### `BindPFlags(cmd.Flags())` plus `UnmarshalExact`

Another common surprise: strict unmarshaling can fail if you bind the entire parsed command flag set.

Why:

- Cobra adds keys like `help`.
- Your own root flags may include operational keys like `config`.
- Those keys end up in the same Viper instance even if they are not part of your config struct.

Use one of these approaches:

- default to `Unmarshal` for the app-level config loader
- bind only the config-participating flags explicitly
- unmarshal a narrower subtree with `vp.Sub(...)`
- use `UnmarshalExact` only when the Viper key space is intentionally aligned with the target struct

### Nested-key shadowing

Higher-precedence immediate values can shadow an entire subtree.

If `database` is set to a scalar or flat value at a higher precedence layer, `database.host` and friends become undefined.

### Concurrent read/write safety

Viper `v1.21.0` is not safe for concurrent reads and writes without your own synchronization. Reads plus hot reloads can panic if you mutate the same instance concurrently.

### Debugging precedence

Use this when behavior looks wrong:

```go
fmt.Printf("%#v\n", vp.AllSettings())
```

That often reveals a naming mismatch, shadowed subtree, or missing flag binding immediately.
