---
name: go-testscript
description: |
  Write CLI integration tests using go-internal/testscript. Use when testing Go command-line applications with .txtar script files, setting up TestMain for CLI binaries, writing exec/stdout/stderr assertions, or troubleshooting testscript failures. Triggers on testscript, txtar, CLI testing, or command-line tool testing in Go.
---

# Go testscript

The `github.com/rogpeppe/go-internal/testscript` package provides filesystem-based CLI testing using `.txtar` script files. Each script runs in an isolated temporary directory with its own file system.

## Setup

### TestMain Pattern

Register CLI binaries in `TestMain` so scripts can invoke them directly:

```go
package main_test

import (
    "os"
    "testing"

    "github.com/rogpeppe/go-internal/testscript"
)

func TestMain(m *testing.M) {
    os.Exit(testscript.RunMain(m, map[string]func() int{
        "mycli": func() int {
            // Call your CLI's main logic here
            main()
            return 0
        },
    }))
}

func TestCLI(t *testing.T) {
    testscript.Run(t, testscript.Params{
        Dir: "testdata/script",
    })
}
```

### Returning Exit Codes

For proper exit code testing, return int from your main:

```go
// cmd/mycli/main.go
func main() { os.Exit(run()) }

func run() int {
    if err := rootCmd.Execute(); err != nil {
        return 1
    }
    return 0
}

// cmd/mycli/main_test.go
func TestMain(m *testing.M) {
    os.Exit(testscript.RunMain(m, map[string]func() int{
        "mycli": run,  // Use run directly
    }))
}
```

## Script Format (.txtar)

Scripts use txtar format: commands at top, files at bottom:

```txtar
# Test description (comment)
exec mycli version
stdout 'v1\.0\.0'
! stderr .

-- config.yaml --
setting: value

-- input.txt --
test input
```

## Core Commands

### Execution

```txtar
exec mycli arg1 arg2       # Run command (must succeed)
! exec mycli bad-arg       # Must fail (non-zero exit)
exec mycli server &        # Run in background
wait                       # Wait for background commands
```

### Output Assertions

```txtar
stdout 'expected text'     # Stdout must contain (regex)
stdout -count=2 'pattern'  # Must match exactly 2 times
! stdout 'forbidden'       # Must NOT contain
stderr 'error message'     # Check stderr
```

### File Operations

```txtar
exists file.txt            # File must exist
! exists deleted.txt       # Must not exist
cmp output.txt expected.txt    # Compare files exactly
cmpenv output.txt golden.txt   # Compare with env expansion
cp source.txt dest.txt     # Copy file
rm unwanted.txt            # Remove file
mkdir newdir               # Create directory
```

### Environment & Flow

```txtar
env HOME=/custom/home      # Set environment variable
env                        # Print all env vars
cd subdir                  # Change directory
skip 'reason'              # Skip this test
stop                       # Stop test early (pass)
stdin input.txt            # Set stdin for next exec
```

## Common Patterns

### Testing Help Output

```txtar
exec mycli --help
stdout 'Usage:'
stdout 'Available Commands:'
! stderr .
```

### Testing Error Handling

```txtar
! exec mycli --invalid-flag
stderr 'unknown flag'

! exec mycli missing-file.txt
stderr 'no such file'
```

### Testing File Processing

```txtar
exec mycli process input.txt -o output.txt
exists output.txt
cmp output.txt expected.txt

-- input.txt --
raw data

-- expected.txt --
processed data
```

### Testing with Config Files

```txtar
exec mycli --config config.yaml
stdout 'loaded setting: value'

-- config.yaml --
setting: value
debug: true
```

### Testing JSON Output

```txtar
exec mycli list --json
stdout '"name": "item1"'
stdout '"count": 42'
```

### Conditional Tests

```txtar
[unix] exec mycli unix-only
[windows] exec mycli windows-only
[!windows] skip 'unix only test'
[short] skip 'long test'
```

## Params Configuration

```go
testscript.Run(t, testscript.Params{
    Dir:                 "testdata/script",   // Script directory
    Setup: func(env *testscript.Env) error {  // Pre-test setup
        env.Setenv("API_KEY", "test-key")
        return nil
    },
    Cmds: map[string]func(*testscript.TestScript, bool, []string){
        "custom": customCmd,  // Register custom commands
    },
    UpdateScripts: os.Getenv("UPDATE") != "", // Update golden files
    TestWork:      false,                      // Keep work dirs for debugging
})
```

### Custom Commands

```go
Cmds: map[string]func(*testscript.TestScript, bool, []string){
    "jsonpath": func(ts *testscript.TestScript, neg bool, args []string) {
        // args[0] is the jsonpath expression
        // neg is true if command prefixed with !
        result := extractJSON(ts.ReadFile(args[1]), args[0])
        if neg {
            if result != "" {
                ts.Fatalf("jsonpath matched unexpectedly")
            }
        } else if result == "" {
            ts.Fatalf("jsonpath did not match")
        }
        fmt.Fprintln(ts.Stdout(), result)
    },
},
```

## Troubleshooting

### Debugging Failures

1. **Preserve work directory**: Run with `-testwork` flag or set `TestWork: true`
   ```bash
   go test -run TestCLI/mytest -testwork
   ```

2. **Verbose output**: Use `-v` flag
   ```bash
   go test -v -run TestCLI
   ```

3. **Run single script**: Use test name matching
   ```bash
   go test -run TestCLI/script_name
   ```

### Common Issues

| Problem | Solution |
|---------|----------|
| "executable not found" | Ensure binary registered in TestMain |
| Regex not matching | Use `.*` not `*`; escape special chars (`\.`) |
| File comparison fails | Check line endings; use `cmpenv` for env vars |
| Background cmd hangs | Add timeout or use `wait` command |
| Wrong working directory | Scripts run in `$WORK`, not repo root |

### Environment Variables

Scripts have access to these special variables:

```
$WORK     - Temporary working directory
$HOME     - Set to /no-home (isolated)
$TMPDIR   - Set to $WORK/.tmp
$exe      - Empty on Unix, ".exe" on Windows
$/        - Path separator (/ or \)
$:        - Path list separator (: or ;)
```

## Command Reference

See [references/commands.md](references/commands.md) for the complete command reference with all options.
