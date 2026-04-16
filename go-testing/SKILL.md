---
name: go-testing
description: |
  Guide Go tests toward behavior-first testing, table-driven structure, helpers, Testify, and mockery. Use when writing or reviewing Go unit tests, refactoring noisy test suites, setting up mocks, deciding what not to test, or translating product behavior into durable Go tests. Activates for Go `_test.go` files, table tests, Testify `assert`/`require`, mockery, coverage discussions, and behavior-focused testing.
---

# Go Testing

Write Go tests to prove behavior. The goal is not a coverage percentage. The goal is confidence that the important behaviors of the package still hold after changes.

## Default Stance

- Prefer table-driven tests in most cases.
- Bias toward extracting test helpers, even if a helper ends up used once.
- Test observable behavior, not implementation details.
- Use `assert` and `require` from Testify in all Go tests.
- Use `mockery` for mocks. If a dependency cannot be mocked, fix the production code shape.
- Use structs to carry shared test context instead of passing around loosely coupled variables.
- Keep unit tests isolated from external dependencies. A scratch `t.TempDir()` is fine.
- For integration tests, prefer built-in HTTP test support first, then `testcontainers-go`, and only use live external systems through env vars as a last resort.

## Non-Negotiables

### Behavior Over Coverage

Coverage is a diagnostic, not a target. Do not write tests to satisfy an arbitrary line-coverage threshold. Write tests that prove the core behaviors of the package:

- what inputs matter
- what outputs matter
- what errors matter
- what state transitions matter
- what collaborator interactions matter at the boundary

Five behavior-rich tests are better than thirty brittle tests that exist only to color in lines.

### Prefer Table Tests

If multiple cases exercise the same flow, default to one table-driven test with named cases. Writing five separate tests for the same behavior is usually an anti-pattern, even when helpers reduce the duplication.

Separate test functions are warranted when the behavior, lifecycle, or setup is materially different. They are not warranted just because the inputs differ.

### Bias Toward Helpers

Extract helpers for repeatable setup and flows, especially:

- mock setup
- fixture construction
- subject creation
- common assertions

Do not wait for the third copy-paste before extracting a helper. A helper used once is still often a good trade if it makes the test read at the level of behavior instead of plumbing.

### Never Test Internals By Default

Tests should be written as if the internals are unknown. Assert on behavior visible at the package boundary:

- return values
- errors
- state changes
- calls to mocked collaborators

Do not test private helpers, intermediate steps, or exact internal sequencing unless there is a strong reason. The normal exception is mocking: when behavior includes talking to a collaborator, it is valid to assert those interactions through the collaborator interface.

### Do Not Test Near-Constant Code

Do not write tests for code that is effectively constant data assembly with no meaningful behavior. A function that merely instantiates and returns a struct is usually not worth a test. Tests should buy confidence, not ceremony.

If a constructor validates inputs, derives behavior, enforces invariants, or wires important defaults, test that behavior. If it is just data shuffling, skip it.

### Standardize On Testify

Use Testify's `assert` and `require`. Do not write new Go tests using raw `if got != want` style when Testify would express the same check more clearly.

- Use `require` for prerequisites and checks after which the test cannot proceed.
- Use `assert` for independent expectations that should all be reported.
- Add failure descriptions when they make the intent obvious at first glance.

### Standardize On Mockery

All mocks should come from `mockery` and use Testify's mock package underneath. No exceptions.

If a dependency has external interaction and cannot be mocked because the code depends directly on a concrete struct, prefer to fix the production code by introducing an interface at the boundary. Go code with external interactions should provide an interface that can be mocked in tests.

### Unit Tests Must Not Use External Dependencies

Unit tests should never exercise external dependencies directly.

- No network access.
- No calls to live services.
- No reliance on shared external infrastructure.
- No dependency on ambient developer machine state.

The normal exception is scratch filesystem state created by the test itself, such as `t.TempDir()`.

If the code interacts with something external, mock it. If it cannot be mocked cleanly, improve the production seam.

### Integration Tests Have A Dependency Order

When a real dependency is required, prefer these options in order:

1. Go's built-in HTTP test support when the target is an HTTP server or handler.
2. `testcontainers-go` for other service dependencies.
3. Environment-variable-driven live external systems only as a last resort.

That last option is intentionally undesirable. Reaching out to live systems such as AWS using credentials from the environment should be rare, explicit, and justified by something the first two options cannot cover.

## Preferred Patterns

### Table Test Shape

```go
func TestServiceCreateUser(t *testing.T) {
    tests := []struct {
        name        string
        input       CreateUserInput
        setupMocks  func(tc *testContext)
        assertError func(t *testing.T, err error)
        assertState func(t *testing.T, got User)
    }{
        {
            name:  "creates a user when the repository accepts the write",
            input: CreateUserInput{Email: "a@example.com"},
            setupMocks: func(tc *testContext) {
                tc.repo.On("Insert", mock.Anything, "a@example.com").Return(User{ID: "u_123", Email: "a@example.com"}, nil)
            },
            assertError: func(t *testing.T, err error) {
                require.NoError(t, err, "expected user creation to succeed")
            },
            assertState: func(t *testing.T, got User) {
                assert.Equal(t, "u_123", got.ID, "expected created user ID to come from the repository")
                assert.Equal(t, "a@example.com", got.Email, "expected created user email to match the input")
            },
        },
    }

    for _, tt := range tests {
        tt := tt
        t.Run(tt.name, func(t *testing.T) {
            tc := newTestContext(t)
            tt.setupMocks(tc)

            got, err := tc.service.CreateUser(context.Background(), tt.input)

            tt.assertError(t, err)
            tt.assertState(t, got)
            tc.repo.AssertExpectations(t)
        })
    }
}
```

Use named cases that read like behavior statements. Keep the table focused on what changes across cases, not every piece of setup in the system.

### Shared Test Context In A Struct

```go
type testContext struct {
    repo    *mocks.UserRepository
    clock   *mocks.Clock
    service *Service
}

func newTestContext(t *testing.T) *testContext {
    t.Helper()

    repo := mocks.NewUserRepository(t)
    clock := mocks.NewClock(t)

    return &testContext{
        repo:    repo,
        clock:   clock,
        service: NewService(repo, clock),
    }
}
```

Prefer a context struct when several values move together. It keeps relationships explicit and reduces tests built from scattered local variables whose coupling is hard to reason about.

### Helper Style

```go
func givenSuccessfulInsert(tc *testContext, email string) {
    tc.repo.On("Insert", mock.Anything, email).
        Return(User{ID: "u_123", Email: email}, nil)
}
```

Helpers should collapse obvious plumbing, not hide the behavior under test. Good helpers make the test read more like a specification.

### Mocking Rule

Mock collaborators at the boundary of the unit under test. Do not mock internal helpers that exist inside the same behavior boundary.

Good targets for mocks:

- repositories
- HTTP clients
- queues
- clocks
- external services
- filesystem abstractions

Poor targets for mocks:

- private helper functions
- simple value objects
- code paths that should just be exercised directly

## Review Heuristics

When writing or reviewing Go tests, ask:

- Does this test prove behavior that a maintainer actually cares about?
- Could several nearly identical tests be one table-driven test?
- Is setup noise being repeated instead of moved into helpers?
- Is a unit test trying to touch the network or another real external dependency?
- If this is an integration test, is it using the least-coupled dependency option available?
- Is the test asserting internals instead of outcomes?
- Is it spending effort on constant or trivial construction code?
- Are Testify `assert` and `require` being used clearly?
- Are shared dependencies grouped into a struct?
- Are mocks generated by `mockery`, and are the mocked seams interface-based?

## Anti-Patterns

- Chasing a coverage number instead of testing meaningful behavior.
- Writing many single-case tests for the same flow when a table would do.
- Inlining repetitive mock setup in every case.
- Letting unit tests call real networked dependencies.
- Jumping straight to live external systems when HTTP test helpers or `testcontainers-go` would cover the case.
- Testing private helpers or exact internal implementation paths.
- Testing constructors or factory functions that only shuffle data around.
- Avoiding Testify out of standard-library purity arguments.
- Passing four or five related test values around as loose locals instead of a context struct.
- Depending directly on concrete external clients so the code cannot be mocked cleanly.
