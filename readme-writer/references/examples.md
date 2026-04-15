# README Examples

Complete, production-ready README examples for different project types.

## Table of Contents

- [Example 1: Go Library](#example-1-go-library)
- [Example 2: CLI Tool](#example-2-cli-tool)
- [Example 3: Web Application](#example-3-web-application)

---

## Example 1: Go Library

A data validation library. Note the focus on API documentation and usage examples.

```markdown
# validate

A struct validation library for Go with support for custom rules and nested structs.

## Installation

```bash
go get github.com/example/validate
```

Requires Go 1.21 or later.

## Usage

```go
package main

import "github.com/example/validate"

type User struct {
    Email    string `validate:"required,email"`
    Age      int    `validate:"min=18,max=120"`
    Username string `validate:"required,alphanum,min=3,max=32"`
}

func main() {
    user := User{
        Email:    "user@example.com",
        Age:      25,
        Username: "johndoe",
    }

    if err := validate.Struct(user); err != nil {
        // Handle validation errors
        for _, e := range err.(validate.Errors) {
            fmt.Printf("Field %s: %s\n", e.Field, e.Message)
        }
    }
}
```

## Validation Tags

| Tag | Description | Example |
|-----|-------------|---------|
| `required` | Field must not be zero value | `validate:"required"` |
| `email` | Must be valid email format | `validate:"email"` |
| `min` | Minimum value (numbers) or length (strings) | `validate:"min=3"` |
| `max` | Maximum value or length | `validate:"max=100"` |
| `alphanum` | Alphanumeric characters only | `validate:"alphanum"` |
| `oneof` | Must be one of specified values | `validate:"oneof=active inactive"` |

## Custom Validators

Register custom validation functions:

```go
validate.Register("customtag", func(value any, param string) bool {
    // Return true if valid
    return someCondition(value)
})
```

## Nested Structs

Nested structs are validated automatically:

```go
type Address struct {
    Street string `validate:"required"`
    City   string `validate:"required"`
}

type Company struct {
    Name    string  `validate:"required"`
    Address Address // Validated recursively
}
```

## Error Handling

```go
err := validate.Struct(data)
if err != nil {
    errors := err.(validate.Errors)
    for _, e := range errors {
        fmt.Printf("%s: %s (got: %v)\n", e.Field, e.Message, e.Value)
    }
}
```

## Contributing

Issues and pull requests are welcome. Please run `go test ./...` before submitting.

## License

MIT License. See [LICENSE](LICENSE) for details.
```

---

## Example 2: CLI Tool

A file synchronization tool. Note the command reference format and practical examples.

```markdown
# fsync

A command-line tool for synchronizing files between local directories and remote servers.

## Installation

### Homebrew (macOS/Linux)

```bash
brew install example/tap/fsync
```

### Binary Release

Download the latest release from the [releases page](https://github.com/example/fsync/releases) and add it to your PATH.

### From Source

```bash
go install github.com/example/fsync@latest
```

## Quick Start

```bash
# Sync local directory to remote server
fsync push ./local user@server:/remote

# Sync from remote to local
fsync pull user@server:/remote ./local

# Preview changes without syncing
fsync push ./local user@server:/remote --dry-run
```

## Commands

### fsync push

Push local files to a remote destination.

```bash
fsync push <source> <destination> [flags]
```

**Flags:**
- `--dry-run` - Show what would be transferred without making changes
- `--delete` - Delete files on destination that don't exist in source
- `--exclude <pattern>` - Exclude files matching pattern (can be repeated)
- `--progress` - Show transfer progress

**Examples:**

```bash
# Basic push
fsync push ./dist user@server:/var/www/app

# Exclude node_modules and show progress
fsync push . server:/backup --exclude node_modules --progress

# Mirror mode (delete extra files on remote)
fsync push ./src server:/src --delete
```

### fsync pull

Pull remote files to local destination.

```bash
fsync pull <source> <destination> [flags]
```

Accepts the same flags as `push`.

### fsync diff

Show differences between source and destination.

```bash
fsync diff ./local user@server:/remote
```

## Configuration

Create `~/.fsync.yaml` for persistent settings:

```yaml
defaults:
  exclude:
    - .git
    - node_modules
    - "*.log"
  progress: true

profiles:
  production:
    host: user@prod.example.com
    path: /var/www/app
  staging:
    host: user@staging.example.com
    path: /var/www/app
```

Use profiles:

```bash
fsync push ./dist @production
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FSYNC_CONFIG` | Config file path | `~/.fsync.yaml` |
| `FSYNC_SSH_KEY` | SSH private key path | `~/.ssh/id_rsa` |
| `FSYNC_TIMEOUT` | Connection timeout | `30s` |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Connection failed |
| 3 | Authentication failed |
| 4 | File not found |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

Apache License 2.0. See [LICENSE](LICENSE) for details.
```

---

## Example 3: Web Application

A task management API. Note the quick start focus and architecture overview.

```markdown
# TaskAPI

A REST API for task management with user authentication, team collaboration, and webhook integrations.

## Quick Start

### Prerequisites

- Go 1.22+
- PostgreSQL 15+
- Redis 7+ (optional, for caching)

### Setup

```bash
git clone https://github.com/example/taskapi.git
cd taskapi

# Copy environment template
cp .env.example .env

# Edit .env with your database credentials
vim .env

# Run database migrations
go run ./cmd/migrate up

# Start the server
go run ./cmd/server
```

The API is now available at `http://localhost:8080`.

### Verify Installation

```bash
curl http://localhost:8080/health
# {"status":"ok","version":"1.2.0"}
```

## API Overview

### Authentication

All endpoints except `/health` and `/auth/*` require a Bearer token:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8080/api/tasks
```

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create new account |
| POST | `/auth/login` | Get access token |
| GET | `/api/tasks` | List tasks |
| POST | `/api/tasks` | Create task |
| GET | `/api/tasks/:id` | Get task |
| PUT | `/api/tasks/:id` | Update task |
| DELETE | `/api/tasks/:id` | Delete task |

Full API documentation is available at `/docs` when running in development mode.

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `JWT_SECRET` | Secret for signing tokens | Yes | - |
| `PORT` | Server port | No | `8080` |
| `REDIS_URL` | Redis connection string | No | - |
| `LOG_LEVEL` | Logging verbosity | No | `info` |

### Example `.env`

```bash
DATABASE_URL=postgres://user:pass@localhost:5432/taskapi
JWT_SECRET=your-secret-key-here
PORT=8080
LOG_LEVEL=debug
```

## Project Structure

```
taskapi/
├── cmd/
│   ├── server/      # Main application entry point
│   └── migrate/     # Database migration tool
├── internal/
│   ├── api/         # HTTP handlers and middleware
│   ├── auth/        # Authentication logic
│   ├── model/       # Data models
│   ├── store/       # Database operations
│   └── service/     # Business logic
├── migrations/      # SQL migration files
└── docs/            # API documentation
```

## Development

### Running Tests

```bash
# Unit tests
go test ./...

# With coverage
go test -cover ./...

# Integration tests (requires test database)
DATABASE_URL=postgres://localhost:5432/taskapi_test go test -tags=integration ./...
```

### Database Migrations

```bash
# Create new migration
go run ./cmd/migrate create add_users_table

# Run pending migrations
go run ./cmd/migrate up

# Rollback last migration
go run ./cmd/migrate down
```

## Deployment

### Docker

```bash
docker build -t taskapi .
docker run -p 8080:8080 --env-file .env taskapi
```

### Docker Compose

```bash
docker compose up -d
```

This starts the API, PostgreSQL, and Redis.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/add-labels`)
3. Run tests (`go test ./...`)
4. Commit changes (`git commit -m "Add label support"`)
5. Push to branch (`git push origin feature/add-labels`)
6. Open a Pull Request

## License

MIT License. See [LICENSE](LICENSE) for details.
```

---

## Key Patterns Across Examples

1. **Installation comes early** - Users need to get the software before using it
2. **Quick wins first** - Show the simplest useful example immediately
3. **Tables for structured data** - Commands, environment variables, exit codes
4. **Code blocks are complete** - Runnable, not fragments
5. **Consistent heading hierarchy** - Predictable structure throughout
6. **License at the end** - Important but not the first thing users need
