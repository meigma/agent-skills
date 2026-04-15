# Just Built-in Functions Reference

Complete reference for all built-in functions available in justfiles.

## Table of Contents

- [System Information](#system-information)
- [Environment Variables](#environment-variables)
- [Path Manipulation](#path-manipulation)
- [File System](#file-system)
- [String Manipulation](#string-manipulation)
- [Encoding](#encoding)
- [Hashing](#hashing)
- [Random Values](#random-values)
- [Utilities](#utilities)
- [Error Handling](#error-handling)

---

## System Information

### os()
Returns the operating system name.

```just
current_os := os()  # "linux", "macos", "windows", "freebsd", etc.
```

### os_family()
Returns the OS family.

```just
family := os_family()  # "unix" or "windows"
```

### arch()
Returns the CPU architecture.

```just
cpu := arch()  # "x86_64", "aarch64", "arm", "x86", etc.
```

### num_cpus()
Returns the number of logical CPUs.

```just
cpus := num_cpus()  # "8"
```

### is_dependency()
Returns "true" if the current recipe is running as a dependency.

```just
check := is_dependency()  # "true" or "false"
```

---

## Environment Variables

### env(key) / env(key, default)
Gets an environment variable value. Returns default if not set (or errors if no default).

```just
home := env('HOME')
port := env('PORT', '8080')
```

**Deprecated aliases**: `env_var(key)`, `env_var_or_default(key, default)`

---

## Path Manipulation

### absolute_path(path)
Converts a relative path to absolute, relative to the working directory.

```just
abs := absolute_path("src/main.rs")  # "/home/user/project/src/main.rs"
```

### canonicalize(path)
Resolves symlinks and returns the canonical absolute path.

```just
real := canonicalize("./link")
```

### clean(path)
Simplifies a path by removing `.`, `..`, and extra separators.

```just
cleaned := clean("./foo/../bar//baz")  # "bar/baz"
```

### extension(path)
Returns the file extension (without the dot).

```just
ext := extension("file.tar.gz")  # "gz"
```

### file_name(path)
Returns the filename portion of a path.

```just
name := file_name("/path/to/file.txt")  # "file.txt"
```

### file_stem(path)
Returns the filename without extension.

```just
stem := file_stem("/path/to/file.txt")  # "file"
```

### parent_directory(path)
Returns the parent directory.

```just
parent := parent_directory("/a/b/c")  # "/a/b"
```

### without_extension(path)
Returns the path with the extension removed.

```just
base := without_extension("/path/file.txt")  # "/path/file"
```

### join(a, b, ...)
Joins path components with the platform separator.

```just
full := join("src", "lib", "util.rs")  # "src/lib/util.rs" (Unix)
```

---

## File System

### path_exists(path)
Returns "true" if the path exists, "false" otherwise.

```just
exists := path_exists("config.toml")  # "true" or "false"
```

### read(path)
Reads file contents as a string.

```just
content := read("VERSION")
version := trim(read("VERSION"))
```

### source_file()
Returns the path to the current justfile.

```just
this := source_file()
```

### source_directory()
Returns the directory containing the current justfile.

```just
dir := source_directory()
```

### justfile()
Returns the path to the root justfile.

```just
root := justfile()
```

### justfile_directory()
Returns the directory containing the root justfile.

```just
root_dir := justfile_directory()
```

### invocation_directory()
Returns the directory where `just` was invoked.

```just
cwd := invocation_directory()
```

### invocation_directory_native()
Same as above but uses native path separators on Windows.

```just
cwd := invocation_directory_native()
```

---

## String Manipulation

### capitalize(s)
Capitalizes the first character, lowercases the rest.

```just
cap := capitalize("hELLO")  # "Hello"
```

### uppercase(s)
Converts to uppercase.

```just
upper := uppercase("hello")  # "HELLO"
```

### lowercase(s)
Converts to lowercase.

```just
lower := lowercase("HELLO")  # "hello"
```

### trim(s)
Removes leading and trailing whitespace.

```just
clean := trim("  hello  ")  # "hello"
```

### trim_start(s)
Removes leading whitespace.

```just
clean := trim_start("  hello  ")  # "hello  "
```

### trim_end(s)
Removes trailing whitespace.

```just
clean := trim_end("  hello  ")  # "  hello"
```

### trim_start_match(s, prefix)
Removes a prefix if present.

```just
clean := trim_start_match("hello world", "hello ")  # "world"
```

### trim_end_match(s, suffix)
Removes a suffix if present.

```just
clean := trim_end_match("hello.txt", ".txt")  # "hello"
```

### replace(s, from, to)
Replaces all occurrences of a substring.

```just
new := replace("foo bar foo", "foo", "baz")  # "baz bar baz"
```

### replace_regex(s, regex, replacement)
Replaces using a regular expression.

```just
new := replace_regex("foo123bar", "[0-9]+", "X")  # "fooXbar"
```

### quote(s)
Wraps string in single quotes, escaping existing quotes.

```just
quoted := quote("it's")  # "'it'\\''s'"
```

### append(s, suffix)
Appends a suffix to each whitespace-separated word.

```just
result := append("foo bar", ".o")  # "foo.o bar.o"
```

### prepend(s, prefix)
Prepends a prefix to each whitespace-separated word.

```just
result := prepend("foo bar", "lib")  # "libfoo libbar"
```

### shoutykebabcase(s), shoutysnakecase(s)
Converts to SHOUTY-KEBAB-CASE or SHOUTY_SNAKE_CASE.

```just
sk := shoutykebabcase("foo bar")  # "FOO-BAR"
ss := shoutysnakecase("foo bar")  # "FOO_BAR"
```

### snakecase(s)
Converts to snake_case.

```just
snake := snakecase("fooBar")  # "foo_bar"
```

### kebabcase(s)
Converts to kebab-case.

```just
kebab := kebabcase("fooBar")  # "foo-bar"
```

### titlecase(s)
Converts to Title Case.

```just
title := titlecase("hello world")  # "Hello World"
```

### lowercamelcase(s), uppercamelcase(s)
Converts to lowerCamelCase or UpperCamelCase.

```just
lower := lowercamelcase("foo_bar")  # "fooBar"
upper := uppercamelcase("foo_bar")  # "FooBar"
```

---

## Encoding

### encode_uri_component(s)
URL-encodes a string.

```just
encoded := encode_uri_component("hello world")  # "hello%20world"
```

### blake3(s), blake3_file(path)
Returns BLAKE3 hash.

```just
hash := blake3("hello")
file_hash := blake3_file("Cargo.toml")
```

### sha256(s), sha256_file(path)
Returns SHA-256 hash.

```just
hash := sha256("hello")
file_hash := sha256_file("Cargo.toml")
```

---

## Hashing

### cache_directory()
Returns the user's cache directory.

```just
cache := cache_directory()  # "~/.cache" on Linux
```

### config_directory()
Returns the user's config directory.

```just
config := config_directory()  # "~/.config" on Linux
```

### config_local_directory()
Returns the local config directory.

```just
local := config_local_directory()
```

### data_directory()
Returns the user's data directory.

```just
data := data_directory()  # "~/.local/share" on Linux
```

### data_local_directory()
Returns the local data directory.

```just
local := data_local_directory()
```

### executable_directory()
Returns the directory containing the `just` executable.

```just
exe_dir := executable_directory()
```

### home_directory()
Returns the user's home directory.

```just
home := home_directory()  # "/home/user" on Linux
```

---

## Random Values

### uuid()
Generates a random UUID v4.

```just
id := uuid()  # "550e8400-e29b-41d4-a716-446655440000"
```

### datetime(format)
Returns the current UTC datetime.

```just
now := datetime("%Y-%m-%d")  # "2024-01-15"
timestamp := datetime("%Y%m%d%H%M%S")
```

### datetime_utc(format)
Same as `datetime()`.

---

## Utilities

### assert(condition, message)
Halts if condition is false (requires `set unstable`).

```just
set unstable

check := assert(path_exists("config.toml") == "true", "config.toml missing")
```

### just_executable()
Returns the path to the `just` binary.

```just
just_path := just_executable()
```

### just_pid()
Returns the process ID of `just`.

```just
pid := just_pid()
```

### semver_matches(version, requirement)
Checks if a version matches a semver requirement.

```just
matches := semver_matches("1.2.3", ">=1.0.0")  # "true"
```

### shell(command, args...)
Runs a command and returns its stdout.

```just
result := shell("echo", "hello")  # "hello\n"
```

### which(command)
Returns the path to an executable, or empty string if not found.

```just
go_path := which("go")  # "/usr/local/go/bin/go"
```

---

## Error Handling

### error(message)
Halts execution and displays an error message.

```just
check := if path_exists("required.txt") == "true" {
    "ok"
} else {
    error("required.txt is missing")
}
```

Use in conditionals to validate requirements:

```just
version := if semver_matches(env('GO_VERSION', '0.0.0'), '>=1.21') == "true" {
    env('GO_VERSION')
} else {
    error("Go 1.21+ required")
}
```
