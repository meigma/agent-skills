---
name: go-benchmarking
description: |
  Write, run, and analyze Go benchmarks effectively. Use when writing benchmark functions, analyzing benchmark results with benchstat, optimizing code based on benchmark data, or avoiding common benchmarking pitfalls. Triggers on: benchmark functions, performance testing, b.N loops, b.Loop(), ResetTimer, benchstat, ns/op analysis, or "benchmark" in Go contexts.
---

# Go Benchmarking

Write accurate benchmarks, analyze results statistically, and make data-driven optimizations.

## Quick Reference

```go
// Modern approach (Go 1.24+)
func BenchmarkFoo(b *testing.B) {
    for b.Loop() {
        foo()
    }
}

// Legacy approach
func BenchmarkFoo(b *testing.B) {
    for i := 0; i < b.N; i++ {
        foo()
    }
}
```

Run and analyze:
```bash
go test -bench=. -benchmem -count=10 > bench.txt
benchstat bench.txt
```

## Writing Benchmarks

### Basic Structure

```go
func BenchmarkOperation(b *testing.B) {
    // Setup (not measured)
    data := setupTestData()

    b.ResetTimer()
    for b.Loop() {  // or: for i := 0; i < b.N; i++
        result := operation(data)
        _ = result  // Prevent optimization
    }
}
```

### Preventing Compiler Optimization

The compiler eliminates unused results. Always consume the result:

```go
var sink int  // Package-level sink

func BenchmarkCompute(b *testing.B) {
    var v int
    for b.Loop() {
        v = compute(42)
    }
    sink = v  // Escape to prevent elimination
}
```

Alternative with `runtime.KeepAlive`:
```go
func BenchmarkCompute(b *testing.B) {
    var v int
    for b.Loop() {
        v = compute(42)
    }
    runtime.KeepAlive(v)
}
```

### Timer Control

```go
func BenchmarkWithSetup(b *testing.B) {
    expensiveSetup()
    b.ResetTimer()  // Discard setup time

    for b.Loop() {
        operation()
    }
}

func BenchmarkWithPerIterSetup(b *testing.B) {
    for i := 0; i < b.N; i++ {
        b.StopTimer()
        data := freshData()  // Per-iteration setup
        b.StartTimer()
        operation(data)
    }
}
```

### Memory Allocation Tracking

```go
func BenchmarkAllocs(b *testing.B) {
    b.ReportAllocs()
    for b.Loop() {
        _ = makeSlice()
    }
}
```

Or via command line: `go test -bench=. -benchmem`

### Sub-benchmarks for Multiple Cases

```go
func BenchmarkEncode(b *testing.B) {
    sizes := []int{64, 256, 1024, 4096}
    for _, size := range sizes {
        b.Run(fmt.Sprintf("size=%d", size), func(b *testing.B) {
            data := make([]byte, size)
            for b.Loop() {
                encode(data)
            }
        })
    }
}
```

### Parallel Benchmarks

```go
func BenchmarkParallel(b *testing.B) {
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            operation()
        }
    })
}
```

Run with: `go test -bench=. -cpu=1,2,4,8`

## Running Benchmarks

```bash
# Basic run
go test -bench=.

# Skip tests, run benchmarks with memory stats
go test -run='^$' -bench=. -benchmem

# Multiple runs for statistical analysis (recommended: 10+)
go test -bench=. -count=10 > bench.txt

# Longer duration for more stable results
go test -bench=. -benchtime=5s

# Specific benchmark pattern
go test -bench=BenchmarkEncode
```

## Analyzing Results with benchstat

Install: `go install golang.org/x/perf/cmd/benchstat@latest`

### Single File Analysis

```bash
go test -bench=. -count=10 > bench.txt
benchstat bench.txt
```

Output shows median and 95% confidence interval:
```
         │  bench.txt  │
         │   sec/op    │
Encode-8   1.234µ ± 2%
```

### Comparing Before/After

```bash
# Before changes
go test -bench=. -count=10 > old.txt

# After changes
go test -bench=. -count=10 > new.txt

# Compare
benchstat old.txt new.txt
```

Output:
```
         │   old.txt   │              new.txt               │
         │   sec/op    │   sec/op     vs base               │
Encode-8   1.234µ ± 2%   1.023µ ± 1%  -17.10% (p=0.000 n=10)
```

- `~` means no statistically significant change
- `p=0.000` indicates high confidence the change is real
- Lower p-value = more statistically significant

### Custom Labels

```bash
benchstat before=old.txt after=new.txt
```

### Filtering and Projections

```bash
# Filter specific benchmarks
benchstat -filter "/size:1024" bench.txt

# Compare across sub-benchmark dimensions
benchstat -col /size bench.txt
```

See [references/benchstat.md](references/benchstat.md) for advanced usage.

## Common Pitfalls

See [references/pitfalls.md](references/pitfalls.md) for detailed examples. Summary:

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Unused result | ~0.3 ns/op (unrealistic) | Assign to package-level sink |
| Setup in loop | Inflated times | Use `b.ResetTimer()` or `b.StopTimer()` |
| Reusing data | Cache effects mask reality | Fresh data per iteration |
| Single run | High variance | Use `-count=10` + benchstat |
| Using b.N as input | Benchmark never terminates | Only use b.N for iteration count |

## Optimization Workflow

1. **Establish baseline**: `go test -bench=. -benchmem -count=10 > baseline.txt`
2. **Profile to find bottleneck**: `go test -bench=BenchmarkX -cpuprofile=cpu.prof`
3. **Analyze profile**: `go tool pprof cpu.prof`
4. **Make targeted change**
5. **Measure after**: `go test -bench=. -benchmem -count=10 > optimized.txt`
6. **Compare statistically**: `benchstat baseline.txt optimized.txt`
7. **Verify significance**: Check p-value < 0.05 and meaningful delta

## Best Practices

- Run benchmarks on idle machines (not on battery, no thermal throttling)
- Use at least 10 runs (`-count=10`) for statistical significance
- Interleave before/after runs when possible to reduce environmental variance
- Pre-compile with `go test -c` to exclude compilation time
- Don't rerun until you get desired results (selection bias)
- Expect ~5% false positives in large benchmark suites
