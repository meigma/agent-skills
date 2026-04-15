# testscript Command Reference

Complete reference for all built-in testscript commands.

## Execution Commands

### exec
Run an executable.

```
[!] exec program [args...] [&]
```

- `!` prefix: command must fail (non-zero exit)
- `&` suffix: run in background
- Named background: `[&name&] exec program` then `wait name`

### wait
Wait for background commands to complete.

```
wait [name]
```

- No args: wait for all background commands
- With name: wait for specific named command

### kill
Terminate a background process.

```
kill [-signal] [name]
```

- Default signal: SIGKILL
- Examples: `kill -INT server`, `kill -TERM`

### stdin
Set stdin for the next exec command.

```
stdin file
```

### ttyin
Attach a pseudo-terminal for interactive input.

```
ttyin [-stdin] file
```

- `-stdin`: also use as stdin (not just tty)

## Output Assertions

### stdout
Assert stdout matches a pattern.

```
[!] stdout [-count=N] pattern
```

- Pattern is a Go regexp
- `!` prefix: must NOT match
- `-count=N`: must match exactly N times

### stderr
Assert stderr matches a pattern.

```
[!] stderr [-count=N] pattern
```

### ttyout
Assert terminal output matches a pattern.

```
[!] ttyout [-count=N] pattern
```

## File Operations

### exists
Check if files exist.

```
[!] exists [-readonly] file...
```

- `-readonly`: file must also be read-only
- `!` prefix: files must NOT exist

### cmp
Compare files for exact match.

```
[!] cmp file1 file2
```

- `file2` can reference archive files: `cmp output.txt golden.txt`
- `!` prefix: files must differ

### cmpenv
Compare files with environment variable expansion.

```
[!] cmpenv file1 file2
```

- Expands `$VAR` in both files before comparing

### grep
Search for pattern in file.

```
[!] grep [-count=N] pattern file
```

- Pattern is a Go regexp
- `-count=N`: must match exactly N times
- `!` prefix: pattern must NOT match

### cp
Copy files.

```
cp src... dst
```

- Multiple sources: `cp a.txt b.txt dir/`
- Single source to file: `cp src.txt dst.txt`

### rm
Remove files or directories.

```
rm file...
```

- Removes files and directories recursively

### mv
Move/rename files.

```
mv src dst
```

### mkdir
Create directories.

```
mkdir path...
```

- Creates parent directories as needed

### chmod
Change file permissions.

```
chmod perm path...
```

- Perm is octal: `chmod 755 script.sh`

### symlink
Create symbolic link.

```
symlink link -> target
```

- Arrow syntax: `symlink mylink -> /path/to/target`

### unquote
Remove leading `>` from file lines.

```
unquote file...
```

- Useful for preserving leading whitespace in archive files

## Environment

### env
Set or display environment variables.

```
env [key=value...]
```

- No args: print all env vars
- With args: set variables

### cd
Change working directory.

```
cd dir
```

## Flow Control

### skip
Skip the current test.

```
skip [message]
```

### stop
Stop test early (pass).

```
stop [message]
```

## Conditions

Prefix any command with a condition:

```
[condition] command args...
[!condition] command args...  # negated
```

### Built-in Conditions

| Condition | True when |
|-----------|-----------|
| `[short]` | `-test.short` flag set |
| `[net]` | External network available |
| `[link]` | Hard links supported |
| `[symlink]` | Symbolic links supported |
| `[exec:prog]` | Program `prog` is in PATH |
| `[gc]` | Built with gc compiler |
| `[gccgo]` | Built with gccgo |
| `[go1.X]` | Go version >= 1.X |
| `[unix]` | Unix-like OS |
| `[GOOS]` | Current OS (darwin, linux, windows) |
| `[GOARCH]` | Current arch (amd64, arm64) |

### Examples

```txtar
[unix] exec ./unix-script.sh
[windows] exec windows-script.bat
[!short] exec slow-test
[exec:docker] exec docker run alpine echo hi
[go1.21] exec go run -cover .
```

## Special Variables

Available in scripts:

| Variable | Value |
|----------|-------|
| `$WORK` | Temporary working directory |
| `$HOME` | `/no-home` (isolated) |
| `$TMPDIR` | `$WORK/.tmp` |
| `$exe` | `.exe` on Windows, empty otherwise |
| `$/` | Path separator (`/` or `\`) |
| `$:` | Path list separator (`:` or `;`) |
| `$$` | Literal `$` |

## Quoting

String arguments support:
- Single quotes: `'literal text'`
- Double quotes: `"text with $expansion"`
- Backquotes: `` `raw text` ``
- Unquoted words

Escape sequences in double quotes:
- `\n` newline
- `\t` tab
- `\\` backslash
- `\"` double quote
