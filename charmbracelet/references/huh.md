Validated against April 10, 2026.

Official sources:
- https://github.com/charmbracelet/huh/blob/main/README.md
- https://github.com/charmbracelet/huh/blob/main/examples/theme/main.go
- https://github.com/charmbracelet/huh/blob/main/examples/dynamic/dynamic-country/main.go
- https://github.com/charmbracelet/huh/blob/main/examples/spinner/static/main.go
- https://github.com/charmbracelet/huh/blob/main/theme.go
- https://pkg.go.dev/charm.land/huh/v2

# Huh

Use Huh when the job is interactive input: blocking forms, prompts, grouped pages, validation, dynamic field values, themes, and accessible text-mode prompting. It is especially good for form-like flows in CLIs.

## Why and When

- Use `Form` and `Group` when you need multi-step input collection.
- Use field-level `Run` when you only need a single quick prompt.
- Use themes when you want a consistent visual system and `WithAccessible(true)` when screen-reader-friendly prompting is needed.
- Use dynamic `*Func` APIs when later choices depend on earlier answers.

## Common UI Patterns

Source lineage: README tutorial, field reference, accessibility, and themes sections.

```go
package main

import (
	"errors"
	"fmt"
	"os"

	"charm.land/huh/v2"
)

func main() {
	accessibleMode := os.Getenv("ACCESSIBLE") != ""

	var (
		name string
		env  string
	)

	form := huh.NewForm(
		huh.NewGroup(
			huh.NewInput().
				Title("Name").
				Validate(func(s string) error {
					if s == "" {
						return errors.New("name is required")
					}
					return nil
				}).
				Value(&name),
			huh.NewSelect[string]().
				Title("Environment").
				Options(
					huh.NewOption("Development", "dev"),
					huh.NewOption("Production", "prod"),
				).
				Value(&env),
		),
	).WithAccessible(accessibleMode).WithTheme(huh.ThemeFunc(huh.ThemeCharm))

	if err := form.Run(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	fmt.Printf("%s -> %s\n", name, env)
}
```

Source lineage: README dynamic-forms section and `examples/dynamic/dynamic-country/main.go`.

```go
package main

import (
	"fmt"
	"os"
	"time"

	"charm.land/huh/v2"
)

func main() {
	var (
		country string
		state   string
	)

	states := map[string][]string{
		"Canada":        {"Ontario", "Quebec", "Yukon"},
		"United States": {"California", "Texas", "Washington"},
	}

	form := huh.NewForm(
		huh.NewGroup(
			huh.NewSelect[string]().
				Title("Country").
				Options(huh.NewOptions("United States", "Canada")...).
				Value(&country),
			huh.NewSelect[string]().
				Value(&state).
				Height(5).
				TitleFunc(func() string {
					if country == "Canada" {
						return "Province"
					}
					return "State"
				}, &country).
				OptionsFunc(func() []huh.Option[string] {
					time.Sleep(250 * time.Millisecond)
					return huh.NewOptions(states[country]...)
				}, &country),
		),
	)

	if err := form.Run(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	fmt.Printf("%s, %s\n", state, country)
}
```

Source lineage: README spinner section and `examples/spinner/static/main.go`.

```go
package main

import (
	"fmt"
	"os"

	"charm.land/huh/v2/spinner"
)

func main() {
	if err := spinner.New().
		Title("Loading").
		WithAccessible(os.Getenv("ACCESSIBLE") != "").
		Run(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	fmt.Println("Done!")
}
```

## Best Practices

- Bind fields to pointers with `Value(&x)`. The README and examples consistently use pointer bindings.
- Make accessible mode user-controlled. The README explicitly recommends wiring it to configuration or an environment variable.
- Use `Group` boundaries as pages and treat fields as the unit of validation and data binding.
- Use `TitleFunc`, `OptionsFunc`, and similar APIs only when the form is genuinely dynamic.
- Handle `huh.ErrUserAborted` as a normal user exit when building a polished CLI flow; the theme example does this explicitly.

## Footguns

- Do not pass non-pointer values to `Value`. Official examples always bind with pointers because the form writes back into caller-owned variables.
- Do not omit the narrow binding argument to `*Func` callbacks. The README calls out `&country` specifically to avoid unnecessary recomputation and API calls.
- Do not force accessible mode on or off globally. The README recommends letting the user control it.
- Keep Bubble Tea details light here. The README notes that `huh.Form` is a `tea.Model`, but deeper MVU work belongs in the Bubble Tea skill.
