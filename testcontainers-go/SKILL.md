---
name: testcontainers-go
description: Guide for writing integration tests using Testcontainers for Go. Use when writing Go tests that need real databases (Postgres, MySQL, Redis, MongoDB), message brokers, or any containerized dependencies. Activates for integration testing, container-based test fixtures, database testing, or when the user mentions testcontainers, GenericContainer, or container-based testing in Go.
---

# Testcontainers for Go

## Overview

Testcontainers for Go provides lightweight, throwaway containers for integration tests. It enables programmatic container lifecycle management within Go tests, eliminating the need for external Docker Compose files or manual container orchestration.

## Basic Usage

### GenericContainer (Low-Level API)

```go
package mytest

import (
    "context"
    "testing"

    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/wait"
)

func TestWithContainer(t *testing.T) {
    ctx := context.Background()

    container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
        ContainerRequest: testcontainers.ContainerRequest{
            Image:        "redis:7-alpine",
            ExposedPorts: []string{"6379/tcp"},
            WaitingFor:   wait.ForLog("Ready to accept connections"),
        },
        Started: true,
    })
    testcontainers.CleanupContainer(t, container) // Registers cleanup with t.Cleanup()
    if err != nil {
        t.Fatal(err)
    }

    // Get connection details
    host, _ := container.Host(ctx)
    port, _ := container.MappedPort(ctx, "6379")
    // Use host:port.Port() to connect
}
```

### Run Helper (Preferred for Simple Cases)

```go
func TestWithRun(t *testing.T) {
    ctx := context.Background()

    container, err := testcontainers.Run(ctx,
        "nginx:alpine",
        testcontainers.WithExposedPorts("80/tcp"),
        testcontainers.WithWaitStrategy(wait.ForHTTP("/").WithPort("80/tcp")),
    )
    testcontainers.CleanupContainer(t, container)
    if err != nil {
        t.Fatal(err)
    }
}
```

## Modules (High-Level API)

Modules provide pre-configured containers for common services. Always prefer modules over GenericContainer when available.

### PostgreSQL

```go
import (
    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/modules/postgres"
)

func TestPostgres(t *testing.T) {
    ctx := context.Background()

    pgContainer, err := postgres.Run(ctx,
        "postgres:16-alpine",
        postgres.WithDatabase("testdb"),
        postgres.WithUsername("user"),
        postgres.WithPassword("password"),
        postgres.WithInitScripts("testdata/init.sql"),
        postgres.BasicWaitStrategies(),
    )
    testcontainers.CleanupContainer(t, pgContainer)
    if err != nil {
        t.Fatal(err)
    }

    connStr, _ := pgContainer.ConnectionString(ctx, "sslmode=disable")
    // Use connStr to connect
}
```

### MySQL

```go
import "github.com/testcontainers/testcontainers-go/modules/mysql"

mysqlContainer, err := mysql.Run(ctx,
    "mysql:8.0",
    mysql.WithDatabase("testdb"),
    mysql.WithUsername("root"),
    mysql.WithPassword("password"),
    mysql.WithScripts("testdata/schema.sql"),
)
```

### Redis

```go
import tcredis "github.com/testcontainers/testcontainers-go/modules/redis"

redisContainer, err := tcredis.Run(ctx,
    "redis:7",
    tcredis.WithLogLevel(tcredis.LogLevelVerbose),
)
```

### MongoDB

```go
import "github.com/testcontainers/testcontainers-go/modules/mongodb"

mongoContainer, err := mongodb.Run(ctx, "mongo:6")
```

## Wait Strategies

Never use `time.Sleep()`. Always use explicit wait strategies.

### Common Strategies

```go
// Wait for log message
wait.ForLog("Ready to accept connections")

// Wait for log with multiple occurrences (useful for Postgres)
wait.ForLog("database system is ready to accept connections").WithOccurrence(2)

// Wait for HTTP endpoint
wait.ForHTTP("/health").WithPort("8080/tcp").WithStatusCodeMatcher(func(status int) bool {
    return status == 200
})

// Wait for port to be listening
wait.ForListeningPort("5432/tcp")

// Wait for command execution
wait.ForExec([]string{"pg_isready", "-U", "postgres"})

// Combine multiple strategies (all must pass)
wait.ForAll(
    wait.ForLog("Started"),
    wait.ForListeningPort("8080/tcp"),
)

// Add timeout to any strategy
wait.ForLog("Ready").WithStartupTimeout(60 * time.Second)
```

## Container Configuration

### Environment Variables

```go
testcontainers.WithEnv(map[string]string{
    "POSTGRES_PASSWORD": "secret",
    "POSTGRES_DB":       "testdb",
})
```

### File Mounts

```go
testcontainers.ContainerRequest{
    Files: []testcontainers.ContainerFile{
        {
            HostFilePath:      "testdata/config.yaml",
            ContainerFilePath: "/etc/app/config.yaml",
            FileMode:          0644,
        },
    },
}
```

### Custom Networks

```go
import "github.com/testcontainers/testcontainers-go/network"

nw, err := network.New(ctx)
testcontainers.CleanupNetwork(t, nw)

container, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
    ContainerRequest: testcontainers.ContainerRequest{
        Image:    "nginx",
        Networks: []string{nw.Name},
        NetworkAliases: map[string][]string{
            nw.Name: {"web"},
        },
    },
    Started: true,
})
```

## Test Patterns

### Shared Container Across Subtests

```go
func TestSuite(t *testing.T) {
    ctx := context.Background()

    pgContainer, err := postgres.Run(ctx, "postgres:16-alpine",
        postgres.WithDatabase("testdb"),
        postgres.BasicWaitStrategies(),
    )
    testcontainers.CleanupContainer(t, pgContainer)
    if err != nil {
        t.Fatal(err)
    }

    connStr, _ := pgContainer.ConnectionString(ctx, "sslmode=disable")

    t.Run("TestInsert", func(t *testing.T) {
        // Use connStr
    })

    t.Run("TestQuery", func(t *testing.T) {
        // Use connStr
    })
}
```

### Parallel Container Startup

```go
func TestParallel(t *testing.T) {
    ctx := context.Background()

    requests := testcontainers.ParallelContainerRequest{
        {
            ContainerRequest: testcontainers.ContainerRequest{
                Image:        "postgres:16-alpine",
                ExposedPorts: []string{"5432/tcp"},
                Env:          map[string]string{"POSTGRES_PASSWORD": "test"},
                WaitingFor:   wait.ForLog("ready to accept connections").WithOccurrence(2),
            },
            Started: true,
        },
        {
            ContainerRequest: testcontainers.ContainerRequest{
                Image:        "redis:7-alpine",
                ExposedPorts: []string{"6379/tcp"},
                WaitingFor:   wait.ForLog("Ready to accept connections"),
            },
            Started: true,
        },
    }

    containers, err := testcontainers.ParallelContainers(ctx, requests, testcontainers.ParallelContainersOptions{})
    for _, c := range containers {
        testcontainers.CleanupContainer(t, c)
    }
    if err != nil {
        t.Fatal(err)
    }
}
```

### Custom Container Wrapper

```go
type PostgresTestContainer struct {
    testcontainers.Container
    ConnStr string
}

func SetupPostgres(ctx context.Context, t *testing.T) *PostgresTestContainer {
    t.Helper()

    container, err := postgres.Run(ctx, "postgres:16-alpine",
        postgres.WithDatabase("testdb"),
        postgres.BasicWaitStrategies(),
    )
    testcontainers.CleanupContainer(t, container)
    if err != nil {
        t.Fatal(err)
    }

    connStr, _ := container.ConnectionString(ctx, "sslmode=disable")

    return &PostgresTestContainer{
        Container: container,
        ConnStr:   connStr,
    }
}
```

## Best Practices

### Cleanup

- Always use `testcontainers.CleanupContainer(t, container)` immediately after creation
- Call cleanup before checking errors to ensure cleanup runs even on partial success
- For networks: use `testcontainers.CleanupNetwork(t, nw)`
- For volumes: use `testcontainers.TerminateContainer(c, testcontainers.RemoveVolumes("vol1", "vol2"))`

### Wait Strategies

- Never rely on `time.Sleep()` - containers have variable startup times
- PostgreSQL requires `WithOccurrence(2)` for the ready log (logs twice during startup)
- Combine `ForLog` with `ForListeningPort` for reliability
- Set explicit timeouts with `WithStartupTimeout()`

### Test Organization

- Use `t.Helper()` in setup functions for better error reporting
- Share containers across subtests when tests don't modify state
- Use table-driven tests with shared containers for read-only operations
- Create fresh containers for tests that modify data

### Error Handling

```go
container, err := testcontainers.Run(ctx, "redis:7")
testcontainers.CleanupContainer(t, container) // Register cleanup BEFORE checking error
if err != nil {
    t.Fatal(err)
}
```

## Performance Considerations

### Ryuk (Garbage Collector)

Ryuk automatically cleans up containers after tests. It runs as a sidecar container.

- Enabled by default - ensures cleanup even if tests crash
- Disable only in CI with native cleanup: `TESTCONTAINERS_RYUK_DISABLED=true`
- For privileged environments: `TESTCONTAINERS_RYUK_CONTAINER_PRIVILEGED=true`

### Minimizing Startup Time

1. **Use Alpine images**: `postgres:16-alpine` vs `postgres:16`
2. **Pre-pull images**: Run `docker pull` in CI setup
3. **Parallel startup**: Use `ParallelContainers()` for multiple dependencies
4. **Share containers**: Reuse across subtests when possible

### CI Configuration

```yaml
# GitHub Actions
- name: Run tests
  run: go test ./... -v
  env:
    TESTCONTAINERS_RYUK_DISABLED: true  # GHA cleans up automatically

# GitLab CI
services:
  - docker:dind
variables:
  DOCKER_HOST: "tcp://docker:2375"
  TESTCONTAINERS_RYUK_DISABLED: "true"
```

### Parallel Test Execution

When running `go test -parallel N`:

- Each parallel test should create its own container
- Use unique database names or schemas per test
- Don't share mutable state across parallel tests

```go
func TestParallelSafe(t *testing.T) {
    tests := []struct {
        name string
    }{
        {"test1"},
        {"test2"},
    }

    for _, tt := range tests {
        tt := tt // Capture range variable
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()

            // Each parallel test gets its own container
            ctx := context.Background()
            container, err := postgres.Run(ctx, "postgres:16-alpine",
                postgres.WithDatabase(tt.name), // Unique DB per test
                postgres.BasicWaitStrategies(),
            )
            testcontainers.CleanupContainer(t, container)
            if err != nil {
                t.Fatal(err)
            }
            // Test logic
        })
    }
}
```

## Lifecycle Hooks

For advanced setup/teardown logic:

```go
hooks := testcontainers.ContainerLifecycleHooks{
    PostStarts: []testcontainers.ContainerHook{
        func(ctx context.Context, c testcontainers.Container) error {
            // Run migrations, seed data, etc.
            return nil
        },
    },
    PostReadies: []testcontainers.ContainerHook{
        func(ctx context.Context, c testcontainers.Container) error {
            // Container is fully ready
            return nil
        },
    },
}

container, err := testcontainers.Run(ctx, "postgres:16-alpine",
    testcontainers.WithLifecycleHooks(hooks),
)
```
