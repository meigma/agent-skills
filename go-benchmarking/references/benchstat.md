# Benchstat Reference

Complete guide to analyzing Go benchmarks with benchstat.

## Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Understanding Output](#understanding-output)
4. [Filtering](#filtering)
5. [Projections and Grouping](#projections-and-grouping)
6. [Custom Labels](#custom-labels)
7. [Interpreting Statistics](#interpreting-statistics)

---

## Installation

```bash
go install golang.org/x/perf/cmd/benchstat@latest
```

---

## Basic Usage

### Single File Analysis

```bash
go test -bench=. -count=10 > results.txt
benchstat results.txt
```

### Before/After Comparison

```bash
go test -bench=. -count=10 > old.txt
# make changes
go test -bench=. -count=10 > new.txt
benchstat old.txt new.txt
```

---

## Understanding Output

### Single File Output

```
         │ results.txt │
         │   sec/op    │
Encode-8   1.234µ ± 2%
Decode-8   2.456µ ± 3%
geomean    1.741µ
```

- **1.234µ**: Median time per operation
- **± 2%**: 95% confidence interval
- **geomean**: Geometric mean of all benchmarks

### Comparison Output

```
         │   old.txt   │              new.txt               │
         │   sec/op    │   sec/op     vs base               │
Encode-8   1.234µ ± 2%   1.023µ ± 1%  -17.10% (p=0.000 n=10)
Decode-8   2.456µ ± 3%   2.489µ ± 2%       ~ (p=0.342 n=10)
geomean    1.741µ        1.596µ        -8.33%
```

- **-17.10%**: Percentage change (negative = faster)
- **~**: No statistically significant difference
- **p=0.000**: P-value (probability change is random)
- **n=10**: Number of samples used

### Memory Statistics

With `-benchmem` flag:

```
         │   old.txt    │               new.txt               │
         │    B/op      │    B/op      vs base                │
Encode-8   1024.0 ± 0%    512.0 ± 0%   -50.00% (p=0.000 n=10)

         │  old.txt   │              new.txt               │
         │ allocs/op  │ allocs/op   vs base                │
Encode-8   10.00 ± 0%    5.00 ± 0%  -50.00% (p=0.000 n=10)
```

---

## Filtering

Filter benchmarks using the `-filter` flag with expressions.

### Syntax

```
key:value              # Exact match
key:"value"            # Quoted value
key:/regexp/           # Regular expression
key:(val1 OR val2)     # Multiple values
-expression            # Negation
exp1 AND exp2          # Both must match (also: exp1 exp2)
exp1 OR exp2           # Either matches
```

### Available Keys

| Key | Description |
|-----|-------------|
| `.name` | Base benchmark name |
| `.fullname` | Full name with configuration |
| `.file` | Input file |
| `/{name-key}` | Sub-benchmark parameter |
| `.unit` | Metric unit |

### Examples

```bash
# Only benchmarks containing "Encode"
benchstat -filter ".name:/Encode/" results.txt

# Specific sub-benchmark parameter
benchstat -filter "/size:1024" results.txt

# Exclude specific benchmarks
benchstat -filter "-.name:/Parallel/" results.txt

# Multiple conditions
benchstat -filter ".name:/Encode/ /format:json" results.txt

# Filter by unit
benchstat -filter ".unit:B/op" results.txt
```

---

## Projections and Grouping

Control how benchmarks are organized with `-table`, `-row`, and `-col` flags.

### Default Behavior

```bash
benchstat old.txt new.txt
# Equivalent to:
benchstat -table .config -row .fullname -col .file old.txt new.txt
```

### Compare Across Sub-benchmark Dimension

Given benchmarks like `BenchmarkEncode/format=json-8` and `BenchmarkEncode/format=gob-8`:

```bash
# Compare formats side-by-side
benchstat -col /format results.txt
```

Output:
```
         │    json     │     gob     │
         │   sec/op    │   sec/op    │
Encode-8   1.234µ ± 2%   2.345µ ± 1%
```

### Multiple Dimensions

```bash
# Rows by name, columns by format
benchstat -row .name -col /format results.txt

# Filter and project
benchstat -filter "/size:1024" -col /format results.txt
```

### Sorting

Control sort order within projections:

```bash
# Alphabetic sort
benchstat -col "/format@alpha" results.txt

# Numeric sort
benchstat -col "/size@num" results.txt

# Fixed order
benchstat -col "/format@(json gob xml)" results.txt
```

---

## Custom Labels

Replace filenames with meaningful labels:

```bash
# Single label
benchstat baseline=old.txt optimized=new.txt

# Multiple comparisons
benchstat v1=v1.txt v2=v2.txt v3=v3.txt
```

Output:
```
         │  baseline   │            optimized             │
         │   sec/op    │   sec/op     vs base             │
Encode-8   1.234µ ± 2%   1.023µ ± 1%  -17.10% (p=0.000 n=10)
```

---

## Interpreting Statistics

### P-Value

The p-value indicates the probability that the observed difference occurred by chance.

| P-Value | Interpretation |
|---------|----------------|
| p < 0.01 | Very strong evidence of real change |
| p < 0.05 | Strong evidence (standard threshold) |
| p < 0.10 | Weak evidence |
| p ≥ 0.10 | No significant evidence |

benchstat shows `~` when p ≥ 0.05 (default alpha).

### Confidence Interval

The `± X%` shows the 95% confidence interval around the median.

- **± 1-2%**: Very stable measurements
- **± 3-5%**: Normal variance
- **± 10%+**: High variance, consider more runs or reducing noise

### Geomean

The geometric mean provides a single summary across all benchmarks:

- Reflects proportional changes fairly
- A 10% improvement in one benchmark and 10% regression in another yields ~0% geomean change
- More meaningful than arithmetic mean for ratios

### Sample Size Warnings

```
¹ need >= 6 samples for confidence interval at level 0.95
```

This warning indicates insufficient data. Use `-count=10` or higher.

---

## Advanced Examples

### Multi-dimensional Comparison

Benchmarks: `BenchmarkEncode/format=json/size=1024-8`

```bash
# Compare sizes within each format
benchstat -row /format -col /size results.txt

# Compare old vs new, grouped by format
benchstat -row /format -col .file old.txt new.txt
```

### CI/CD Integration

```bash
#!/bin/bash
go test -bench=. -count=10 > new.txt

# Compare against baseline
if ! benchstat -filter ".unit:sec/op" baseline.txt new.txt | grep -q "^\w.*+[0-9]"; then
    echo "No performance regressions detected"
    exit 0
else
    echo "Potential performance regression!"
    benchstat baseline.txt new.txt
    exit 1
fi
```

### Filtering by Threshold

Check for regressions greater than 5%:

```bash
benchstat old.txt new.txt | awk '
    /\+[0-9]+\.[0-9]+%/ {
        match($0, /\+([0-9]+\.[0-9]+)%/, arr)
        if (arr[1] > 5.0) print "REGRESSION:", $0
    }
'
```
