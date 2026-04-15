Validated against April 10, 2026.

Official sources:
- https://github.com/charmbracelet/lipgloss/blob/main/README.md
- https://github.com/charmbracelet/lipgloss/blob/main/examples/layout/main.go
- https://github.com/charmbracelet/huh/blob/main/README.md
- https://github.com/charmbracelet/huh/blob/main/examples/theme/main.go
- https://github.com/charmbracelet/huh/blob/main/examples/dynamic/dynamic-country/main.go
- https://github.com/charmbracelet/huh/blob/main/theme.go
- https://github.com/charmbracelet/log/blob/main/README.md
- https://github.com/charmbracelet/log/blob/main/UPGRADE_GUIDE_V2.md
- https://github.com/charmbracelet/log/blob/main/examples/styles/styles.go
- https://github.com/charmbracelet/log/blob/main/examples/slog/main.go

# Cross-Package Patterns

These patterns stay inside officially documented APIs and example surfaces. They are intended as integration recipes, not new abstractions.

## Themed Form, Styled Summary, Structured Completion Log

Source lineage: Huh tutorial and theme example, Lip Gloss layout primitives from the README, and Log structured logging from the README.

```go
package main

import (
	"fmt"
	"os"

	"charm.land/huh/v2"
	"charm.land/lipgloss/v2"
	"charm.land/log/v2"
)

func main() {
	var (
		service string
		region  string
	)

	form := huh.NewForm(
		huh.NewGroup(
			huh.NewInput().Title("Service").Value(&service),
			huh.NewSelect[string]().
				Title("Region").
				Options(
					huh.NewOption("us-west-2", "us-west-2"),
					huh.NewOption("eu-west-1", "eu-west-1"),
				).
				Value(&region),
		),
	).WithTheme(huh.ThemeFunc(huh.ThemeCharm))

	if err := form.Run(); err != nil {
		log.Fatal(err)
	}

	summary := lipgloss.NewStyle().
		Border(lipgloss.RoundedBorder()).
		BorderForeground(lipgloss.Color("63")).
		Padding(1, 2).
		Render(fmt.Sprintf("Deploy queued\nservice: %s\nregion: %s", service, region))

	lipgloss.Println(summary)

	logger := log.New(os.Stdout)
	logger.Info("deployment queued", "service", service, "region", region)
}
```

## Shared Palette Across Huh, Lip Gloss, and Log

Source lineage: Huh theme system from `theme.go` and `examples/theme/main.go`, Log style customization from `examples/styles/styles.go`, and Lip Gloss style composition from the README.

```go
package main

import (
	"fmt"
	"os"

	"charm.land/huh/v2"
	"charm.land/lipgloss/v2"
	"charm.land/log/v2"
)

var (
	accent  = lipgloss.Color("#874BFD")
	success = lipgloss.Color("#02BA84")
)

func sharedTheme(isDark bool) *huh.Styles {
	t := huh.ThemeBase(isDark)
	t.Focused.Title = t.Focused.Title.Foreground(accent).Bold(true)
	t.Focused.FocusedButton = t.Focused.FocusedButton.
		Foreground(lipgloss.Color("#FFFDF5")).
		Background(accent)
	t.Focused.SelectedOption = t.Focused.SelectedOption.Foreground(success)
	t.Group.Title = t.Focused.Title
	return t
}

func main() {
	var confirm bool

	form := huh.NewForm(
		huh.NewGroup(
			huh.NewConfirm().
				Title("Apply shared palette?").
				Value(&confirm),
		),
	).WithTheme(huh.ThemeFunc(sharedTheme))

	styles := log.DefaultStyles()
	styles.Levels[log.InfoLevel] = lipgloss.NewStyle().
		SetString("INFO").
		Foreground(accent)
	styles.Levels[log.WarnLevel] = lipgloss.NewStyle().
		SetString("WARN").
		Foreground(success)

	logger := log.New(os.Stdout)
	logger.SetStyles(styles)

	if err := form.Run(); err != nil {
		log.Fatal(err)
	}

	banner := lipgloss.NewStyle().Foreground(accent).Bold(true).Render("Shared palette ready")
	fmt.Println(banner)
	logger.Info("palette applied", "confirm", confirm)
}
```

## Validation and Abort Handling with Styled Feedback

Source lineage: Huh validation and `ErrUserAborted` handling from the README and theme example, Lip Gloss output styling from the README, and Log warning and error output from the README.

```go
package main

import (
	"errors"
	"fmt"
	"os"

	"charm.land/huh/v2"
	"charm.land/lipgloss/v2"
	"charm.land/log/v2"
)

func main() {
	logger := log.New(os.Stderr)
	var email string

	form := huh.NewForm(
		huh.NewGroup(
			huh.NewInput().
				Title("Email").
				Validate(func(s string) error {
					if s == "" {
						return errors.New("email is required")
					}
					return nil
				}).
				Value(&email),
		),
	)

	if err := form.Run(); err != nil {
		if err == huh.ErrUserAborted {
			lipgloss.Println(lipgloss.NewStyle().
				Foreground(lipgloss.Color("245")).
				Render("Canceled by user"))
			logger.Warn("prompt aborted")
			return
		}

		logger.Error("prompt failed", "err", err)
		os.Exit(1)
	}

	lipgloss.Println(lipgloss.NewStyle().
		Foreground(lipgloss.Color("42")).
		Render(fmt.Sprintf("Using %s", email)))
}
```

## Accessible Forms and Terminal-Safe Output

Source lineage: Huh accessibility guidance from the README, Lip Gloss standalone print helpers from the README, and Log structured output from the README.

```go
package main

import (
	"os"

	"charm.land/huh/v2"
	"charm.land/lipgloss/v2"
	"charm.land/log/v2"
)

func main() {
	accessibleMode := os.Getenv("ACCESSIBLE") != ""
	var project string

	form := huh.NewForm(
		huh.NewGroup(
			huh.NewInput().Title("Project").Value(&project),
		),
	).WithAccessible(accessibleMode)

	if err := form.Run(); err != nil {
		log.Fatal(err)
	}

	summary := lipgloss.NewStyle().
		Border(lipgloss.NormalBorder()).
		Padding(0, 1).
		Render("Project: " + project)
	lipgloss.Println(summary)

	logger := log.New(os.Stdout)
	logger.Info("accessible mode configured", "accessible", accessibleMode)
}
```
