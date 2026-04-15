# Common Go Benchmarking Pitfalls

Detailed examples of benchmark mistakes and their corrections.

## Contents

1. [Compiler Optimization Elimination](#compiler-optimization-elimination)
2. [Benchmarking the Wrong Thing](#benchmarking-the-wrong-thing)
3. [Timer Mismanagement](#timer-mismanagement)
4. [Observer Effect (Cache Artifacts)](#observer-effect-cache-artifacts)
5. [Misusing b.N](#misusing-bn)
6. [Statistical Insignificance](#statistical-insignificance)

---

## Compiler Optimization Elimination

**The most critical pitfall.** Go's compiler aggressively optimizes away unused computations.

### Wrong: Unused Result

```go
func BenchmarkPopcntWrong(b *testing.B) {
    for i := 0; i < b.N; i++ {
        popcnt(uint64(i))  // Result discarded
    }
}
// Result: 0.28 ns/op (one CPU cycle - impossible for real work)
```

The compiler inlines `popcnt`, sees the result is unused, and eliminates the call entirely.

### Wrong: Constant Input

```go
func BenchmarkIsCondWrong(b *testing.B) {
    for i := 0; i < b.N; i++ {
        isCond(201)  // Constant - computed at compile time
    }
}
// Result: 0.24 ns/op (empty loop)
```

With constant input and unused result, the compiler evaluates at compile time.

### Correct: Sink Variable Pattern

```go
var sink uint64  // Package-level prevents escape analysis optimization

func BenchmarkPopcntCorrect(b *testing.B) {
    var v uint64
    for i := 0; i < b.N; i++ {
        v = popcnt(uint64(i))
    }
    sink = v
}
// Result: 1.99 ns/op (realistic)
```

### Correct: runtime.KeepAlive Pattern

```go
func BenchmarkPopcntKeepAlive(b *testing.B) {
    var v uint64
    for i := 0; i < b.N; i++ {
        v = popcnt(uint64(i))
    }
    runtime.KeepAlive(v)
}
```

### Detecting This Problem

- **Symptom**: Sub-nanosecond times (~0.2-0.5 ns/op)
- **Verification**: Check assembly output:
  ```bash
  go test -gcflags="-S" -bench=BenchmarkFoo 2>&1 | grep -A20 BenchmarkFoo
  ```

---

## Benchmarking the Wrong Thing

Measuring something other than intended due to state mutation.

### Wrong: Sorting Already-Sorted Data

```go
func BenchmarkSortIntsWrong(b *testing.B) {
    ints := makeRandomInts(100000)
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        slices.Sort(ints)  // First iteration sorts; rest are no-ops
    }
}
// Result: 312 ns/op (sorting already sorted data)
```

### Correct: Fresh Data Each Iteration

```go
func BenchmarkSortIntsCorrect(b *testing.B) {
    for i := 0; i < b.N; i++ {
        b.StopTimer()
        ints := makeRandomInts(100000)
        b.StartTimer()
        slices.Sort(ints)
    }
}
// Result: 33547 ns/op (actual sorting performance)
```

The corrected version is ~100x slower because it measures real work.

---

## Timer Mismanagement

### Wrong: Measuring Setup

```go
func BenchmarkWithSetupWrong(b *testing.B) {
    for i := 0; i < b.N; i++ {
        conn := openDBConnection()  // Expensive setup measured
        query(conn)
        conn.Close()
    }
}
```

### Correct: One-time Setup

```go
func BenchmarkWithSetupCorrect(b *testing.B) {
    conn := openDBConnection()
    defer conn.Close()
    b.ResetTimer()  // Exclude setup time

    for i := 0; i < b.N; i++ {
        query(conn)
    }
}
```

### Correct: Per-iteration Setup (When Required)

```go
func BenchmarkPerIterSetup(b *testing.B) {
    for i := 0; i < b.N; i++ {
        b.StopTimer()
        data := generateFreshData()  // Not measured
        b.StartTimer()

        process(data)
    }
}
```

**Note**: `StopTimer`/`StartTimer` have overhead (~100ns). For very fast operations, consider batch approaches.

---

## Observer Effect (Cache Artifacts)

Repeated access to the same data benefits from CPU cache, hiding real-world performance.

### Wrong: Reusing Cached Data

```go
func BenchmarkMatrixSumWrong(b *testing.B) {
    matrix := createMatrix512(1000)  // Created once
    b.ResetTimer()

    var sum int64
    for i := 0; i < b.N; i++ {
        sum = calculateSum(matrix)  // Cache-warm after first iteration
    }
    sink = sum
}
// Result: 15073 ns/op (L1/L2 cache hits)
```

### Correct: Fresh Data Eliminates Cache Effects

```go
func BenchmarkMatrixSumCorrect(b *testing.B) {
    var sum int64
    for i := 0; i < b.N; i++ {
        b.StopTimer()
        matrix := createMatrix512(1000)  // Fresh, uncached data
        b.StartTimer()

        sum = calculateSum(matrix)
    }
    sink = sum
}
// Result: 33547 ns/op (realistic cache-cold performance)
```

### When Cache Effects Matter

- Benchmarking data structure traversal
- Memory-bound algorithms
- Comparing algorithms with different access patterns
- Any operation touching significant memory

---

## Misusing b.N

`b.N` is the iteration count determined by the framework. Using it for anything else breaks benchmark calibration.

### Wrong: No Loop

```go
func BenchmarkNoLoopWrong(b *testing.B) {
    rand.Prime(rand.Reader, 200)  // Runs once per calibration step
}
// Result: 0.0001234 ns/op (nonsensical)
```

### Wrong: Using b.N as Input

```go
func BenchmarkBadInputWrong(b *testing.B) {
    for i := 0; i < b.N; i++ {
        rand.Prime(rand.Reader, i)  // i grows with b.N!
    }
}
// Result: Benchmark never terminates
```

**Why it fails**: The framework increases b.N exponentially (1, 2, 5, 10, 20, 50..., up to 1B) to achieve ~1s runtime. When b.N affects work done, calibration diverges.

### Correct: Fixed Inputs

```go
func BenchmarkPrimeCorrect(b *testing.B) {
    for i := 0; i < b.N; i++ {
        rand.Prime(rand.Reader, 200)  // Constant size
    }
}
```

---

## Statistical Insignificance

Single benchmark runs have high variance due to OS scheduling, thermal throttling, etc.

### Wrong: Single Run

```bash
go test -bench=.
# BenchmarkFoo-8    1234567    987 ns/op
```

A single run tells you almost nothing about true performance.

### Correct: Multiple Runs with Statistical Analysis

```bash
go test -bench=. -count=10 > bench.txt
benchstat bench.txt
```

Output:
```
         │  bench.txt  │
         │   sec/op    │
Foo-8      987.2n ± 3%
```

The `± 3%` shows the 95% confidence interval.

### Minimum Runs

- **10 runs**: Minimum for meaningful statistics
- **20+ runs**: Better for detecting small differences
- **Use benchstat**: Don't eyeball averages

### Interleaved Comparison

For before/after comparison, interleave runs to reduce environmental variance:

```bash
# Better than running all "before" then all "after"
for i in {1..10}; do
    go test -bench=. >> old.txt
    # apply changes
    go test -bench=. >> new.txt
    # revert changes
done
benchstat old.txt new.txt
```
