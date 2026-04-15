Validated against April 10, 2026.

Official sources:
- https://github.com/charmbracelet/lipgloss/blob/main/README.md
- https://github.com/charmbracelet/lipgloss/blob/main/examples/layout/main.go
- https://github.com/charmbracelet/lipgloss/blob/main/examples/table/languages/main.go
- https://github.com/charmbracelet/lipgloss/blob/main/examples/list/simple/main.go
- https://pkg.go.dev/charm.land/lipgloss/v2

# Lip Gloss

Use Lip Gloss when the job is presentation: styling, layout, spacing, borders, alignment, terminal-safe colors, tables, lists, trees, and measuring rendered output. Do not use it as a state-management layer.

## Why and When

- Use it for styled terminal output in standalone CLIs and as a view-layer companion for bigger TUIs.
- Reach for `JoinHorizontal`, `JoinVertical`, `Place`, `Width`, `Height`, and `Size` when you need layout that survives ANSI styling and wide characters.
- Use the `table`, `list`, and `tree` subpackages when you want richer terminal output without hand-building strings.

## Common UI Patterns

Source lineage: README sections on borders, block formatting, joining paragraphs, measuring width and height, advanced color usage, and the `examples/layout/main.go` layout example.

```go
package main

import (
	"fmt"
	"os"

	"charm.land/lipgloss/v2"
)

func main() {
	hasDarkBG := lipgloss.HasDarkBackground(os.Stdin, os.Stdout)
	lightDark := lipgloss.LightDark(hasDarkBG)

	accent := lightDark(lipgloss.Color("#874BFD"), lipgloss.Color("#7D56F4"))
	subtle := lightDark(lipgloss.Color("#D9DCCF"), lipgloss.Color("#383838"))

	card := lipgloss.NewStyle().
		Border(lipgloss.RoundedBorder()).
		BorderForeground(accent).
		Padding(1, 2).
		Width(28)

	left := card.Render("Services\n- api\n- worker")
	right := card.Render("Status\nhealthy")
	footer := lipgloss.NewStyle().
		Foreground(subtle).
		Render("left card width: " + fmt.Sprint(lipgloss.Width(left)))

	output := lipgloss.JoinVertical(
		lipgloss.Left,
		lipgloss.JoinHorizontal(lipgloss.Top, left, right),
		footer,
	)

	lipgloss.Println(output)
}
```

Source lineage: README sections on rendering tables and lists, plus `examples/table/languages/main.go` and `examples/list/simple/main.go`.

```go
package main

import (
	"fmt"

	"charm.land/lipgloss/v2"
	"charm.land/lipgloss/v2/list"
	"charm.land/lipgloss/v2/table"
)

func main() {
	headerStyle := lipgloss.NewStyle().
		Foreground(lipgloss.Color("99")).
		Bold(true).
		Align(lipgloss.Center)
	cellStyle := lipgloss.NewStyle().Padding(0, 1).Width(12)
	borderStyle := lipgloss.NewStyle().Foreground(lipgloss.Color("99"))

	rows := [][]string{
		{"api", "healthy"},
		{"worker", "warning"},
	}

	t := table.New().
		Border(lipgloss.ThickBorder()).
		BorderStyle(borderStyle).
		StyleFunc(func(row, col int) lipgloss.Style {
			if row == table.HeaderRow {
				return headerStyle
			}
			return cellStyle
		}).
		Headers("SERVICE", "STATE").
		Rows(rows...)

	tasks := list.New("ship release", "rotate key", "clean cache").Enumerator(list.Roman)

	lipgloss.Println(lipgloss.JoinHorizontal(
		lipgloss.Top,
		fmt.Sprint(t),
		lipgloss.NewStyle().MarginLeft(2).Render(fmt.Sprint(tasks)),
	))
}
```

## Best Practices

- Treat `lipgloss.Style` as a pure value type. Assignment copies styles, and chained calls create modified copies.
- Use measurement helpers such as `Width`, `Height`, and `Size` on rendered output rather than byte counts.
- In standalone CLIs, use `lipgloss.Print*` and `lipgloss.Sprint*` helpers so colors are downsampled or stripped appropriately for the output device.
- Use `LightDark` and `HasDarkBackground` only when the terminal background really matters to the palette.
- Prefer layout helpers over manual string padding once multiple blocks, borders, or ANSI styles are involved.

## Footguns

- Do not use `len` to measure styled output. Lip Gloss documents `Width`, `Height`, and `Size` for rendered text blocks.
- Do not assume truecolor output. The README explicitly recommends Lip Gloss print helpers for standalone programs so downsampling happens automatically.
- Do not reach for the `compat` package in new code. The README positions it as migration help from v1, not the preferred v2 API surface.
- Remember that tab rendering is normalized by default. If literal tab behavior matters, set `TabWidth` explicitly.
