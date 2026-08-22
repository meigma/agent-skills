---
name: cue
description: >
  Author, review, and publish CUE modules and CUE-based configuration. Use
  when creating or refactoring `.cue` files, designing CUE schemas and
  definitions, using disjunctions, defaults, bounds, custom errors, built-in
  packages, JSON/YAML renderers, `cue export`, `cue vet`, or `cue mod`
  workflows, including publishing CUE modules to OCI registries.
---

# CUE

Use this skill as the default CUE authoring guide. CUE is a constraint language:
schemas, policy, defaults, and data are all values that unify into a final
configuration. Prefer small definitions, narrow constraints, and concrete export
checks over duplicated object literals or ad hoc string generation.

## Verified Against

- Official CUE docs and package references checked on 2026-04-28.
- Local CLI: `cue version` reports CUE language `v0.16.0`.
- The current docs describe `cmd/cue v0.16.1`; re-check `cue help <command>`
  before depending on exact flags in automation.

Read [references/source-map.md](references/source-map.md) when a task needs
current source grounding, command details, or package-specific references.

## Default Stance

1. Start with definitions. Put reusable schema under `#Name`, not in repeated
   output objects.
2. Keep output values concrete. `cue export` should fail until every emitted
   field is fully determined.
3. Use disjunctions to model real choices and defaults, not as a loose escape
   hatch.
4. Use bounds, regex constraints, closed definitions, and custom `error()`
   messages to make invalid input fail close to the field that caused it.
5. Use CUE modules for shared schemas. Do not copy definitions between repos.
6. Use `cue mod tidy --check`, `cue vet -c`, and representative `cue export`
   commands as the minimum validation loop.

## Module Workflow

Create each reusable CUE package inside a module with a controlled module path:

```bash
cue mod init --source=git example.com/glab/platform@v0
cue fmt ./...
cue mod tidy
cue vet -c ./...
cue export ./... --out yaml
```

Use a module path under a DNS name or source namespace you control, and include
the major version suffix (`@v0`, `@v1`, ...). Publish versions with semantic
versions whose major component matches the suffix.

Use `--source=git` for publishable modules in Git. That makes publishing use
Git's file list and requires the working tree for the module contents to be
clean. Use `--source=self` only for non-Git or deliberately self-contained
module directories.

Structure modules around stable package boundaries:

```text
cue.mod/module.cue
schemas/networking/ipam.cue
schemas/kubernetes/app.cue
templates/bootstrap/config.cue
```

Inside packages, keep public schemas as definitions and output values as regular
fields:

```cue
package app

#Image: {
	registry: *"ghcr.io" | string
	repository!: string
	tag!:        string
	ref:         "\(registry)/\(repository):\(tag)"
}

#Workload: {
	name!:     =~"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$"
	image!:    #Image
	replicas: *1 | int & >=1 & <=10
}

workload: #Workload & {
	name: "api"
	image: {
		repository: "gilmanlab/api"
		tag:        "v0.1.0"
	}
}
```

Pull native CUE dependencies with imports plus `cue mod tidy`, or explicitly
change a dependency with `cue mod get`:

```bash
cue mod get example.com/glab/schemas@v0.3.1
cue mod tidy
cue mod tidy --check
```

For non-CUE dependencies generated from other ecosystems, use the appropriate
`cue get` subcommand, such as `cue get go` or `cue get crd`. Keep generated
definitions separate from handwritten constraints.

## Publishing To OCI Registries

CUE modules publish to OCI-compliant registries as CUE module artifacts. Treat
them like OCI artifacts, not runnable container images.

```bash
export CUE_REGISTRY=registry.example.com/cue-modules
cue login registry.example.com
cue mod tidy --check
cue mod publish --dry-run v0.1.0
cue mod publish v0.1.0
```

Use `CUE_REGISTRY` to map module paths to registry hosts and repository prefixes.
For mixed registries, use prefix mappings:

```bash
export CUE_REGISTRY='example.com/glab=registry.example.com/cue,registry.cue.works'
```

Use `cue mod publish --out ./oci-layout v0.1.0` when you need an OCI Image
Layout directory for inspection, mirroring, or offline promotion. Use
`cue mod registry localhost:5001` only as a scratch registry for local tests; it
is an in-memory helper and should not become durable infrastructure.

## Definitions And Disjunctions

Use definitions for schemas and reusable object shapes. Definitions are not
exported as data and, when referenced, close structs recursively unless you keep
them open with `...`.

```cue
package platform

#Environment: "dev" | "stage" | "prod" | error("environment must be dev, stage, or prod")

#Service: {
	name!: =~"^[a-z0-9-]+$" | error("name must use lowercase DNS-label characters")
	env!:  #Environment
	team!: string & !="" | error("team must be a non-empty string")
	ports: [...#Port]
}

#Port: {
	name!:     =~"^[a-z][a-z0-9-]*$"
	number!:   (int & >=1 & <=65535) | error("port number must be 1..65535")
	protocol: *"TCP" | "UDP" | "SCTP"
}
```

Use disjunctions for enumerations, alternatives, and defaults:

```cue
#Size: "small" | "medium" | "large" | error("size must be small, medium, or large")

#Replicas: *2 | int & >=1 & <=20
```

Use the default marker (`*`) only when the default is a real product or platform
convention. Avoid `*value | _` unless any override is truly acceptable; prefer a
bounded type such as `*2 | int & >=1 & <=20`.

Avoid hardcoding the same object repeatedly. Name the reusable definition, unify
it at each use site, and put the concrete differences in the use site:

```cue
#HTTPProbe: {
	path: *"/healthz" | string
	port: int & >=1 & <=65535
}

api: probe: #HTTPProbe & {port: 8080}
web: probe: #HTTPProbe & {path: "/ready", port: 3000}
```

## Constraints For Better UX

Prefer constraints that explain the valid shape at the field boundary:

```cue
#DNSLabel: =~"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$" |
	error("must be a lowercase DNS label")

#PositiveTimeoutSeconds: (int & >=1 & <=300) |
	error("timeout must be between 1 and 300 seconds")

#Mode: "read-only" | "read-write" |
	error("mode must be read-only or read-write")
```

Use built-in bounds for numeric, string, bytes, and `null` constraints. Use
predefined integer bounds such as `uint16`, `int32`, or `uint64` when that is
the exact domain. Use regex constraints for simple string shape checks and
package functions when the check is semantic, such as `net.IPCIDR` or
`time.Duration`.

Use `error()` mainly inside disjunctions that already express the allowed
domain. The official docs also show assertion-style custom errors, but current
best practice is to keep normal CUE constraints as the primary validation model
and add custom errors where the default failure would be hard to read.

## Common Built-Ins

Predeclared built-ins:

- `len(v)` for strings, bytes, lists, and structs.
- `close(v)` when an open struct must become closed.
- `and(list)` to unify a computed list of constraints.
- `or(list)` to build a disjunction from a computed list.
- `div`, `mod`, `quo`, `rem` for integer division semantics.
- `error("message")` for custom validation failures.

Common standard-library packages:

- `strings`: `HasPrefix`, `HasSuffix`, `Contains`, `Join`, `ToLower`,
  `TrimSpace`, `MinRunes`, and `MaxRunes`.
- `list`: `MinItems`, `MaxItems`, `UniqueItems`, `Contains`, `SortStrings`,
  `Range`, and `Sum`.
- `regexp`: `Match`, `FindSubmatch`, `ReplaceAll`, and `Valid`. Prefer CUE's
  `=~` and `!~` operators for simple field constraints.
- `encoding/json`: `Marshal`, `Unmarshal`, `Validate`, `Compact`, and `Indent`.
- `encoding/yaml`: `Marshal`, `Unmarshal`, `Validate`, and stream variants.
- `strconv`: parse and format stringified booleans and numbers.
- `net`: `IP`, `IPCIDR`, `FQDN`, `URL`, `JoinHostPort`, and `InCIDR`.
- `time`: `Time`, `Duration`, `ParseDuration`, `FormatString`, and `Unix`.
- `math`: `Floor`, `Ceil`, `Round`, `Pow`, `Sqrt`, and `MultipleOf`.

Import only the package you need:

```cue
import (
	"list"
	"net"
	"strings"
)

cidr: net.IPCIDR
name: strings.MaxRunes(63)
tags: list.UniqueItems
```

## Rendering JSON And YAML Inside Fields

Use the built-in encoding packages when a target format requires raw JSON or
YAML embedded as a string field, such as Kubernetes `ConfigMap.data`.

```cue
package configmap

import (
	"encoding/json"
	"encoding/yaml"
)

#Settings: {
	logLevel: "debug" | "info" | "warn" | "error"
	outputs: [...string]
}

settings: #Settings & {
	logLevel: "info"
	outputs: ["stdout"]
}

configMap: {
	apiVersion: "v1"
	kind:       "ConfigMap"
	metadata: name: "app-settings"
	data: {
		"settings.json": json.Marshal(settings)
		"settings.yaml": yaml.Marshal(settings)
	}
}
```

Exporting the outer object as YAML keeps `settings.json` and `settings.yaml` as
string fields whose contents are rendered by the encoding packages:

```bash
cue export config.cue -e configMap --out yaml
```

Use `json.Unmarshal` or `yaml.Unmarshal` when input arrives as encoded text and
must be constrained as structured CUE. Use `json.Validate` or `yaml.Validate`
when the field should remain encoded text but must satisfy a schema.

## CLI Export And Validation

Use `cue fmt` before review and `cue vet -c` before treating a configuration as
valid:

```bash
cue fmt ./...
cue mod tidy --check
cue vet -c ./...
```

Use `cue export` to render concrete values for downstream tools:

```bash
cue export ./... --out json
cue export ./... --out yaml
cue export . -e configMap --out yaml
cue export config.cue values.yaml --out yaml
cue export . -e renderedScript --out text
```

Common `--out` encodings include `json`, `yaml`, `toml`, `cue`, `text`, and
`binary`. JSON is the default. Use `-e <expr>` to export a specific expression
instead of the whole package. Use `cue eval -c` while developing when you want to
inspect the evaluated CUE value before choosing an export format.

`cue export` is a contract: it should fail when emitted values are incomplete,
invalid, or not representable in the selected data format. Do not paper over
that failure with `--ignore`; fix the schema, defaults, or selected expression.

## Maintenance Checklist

Re-verify this skill when CUE changes minor versions or when module behavior
changes:

1. Re-open the modules reference, `cue help modules`, `cue help mod`, and
   `cue help registryconfig`.
2. Re-check `cue help mod init`, `tidy`, `get`, and `publish`.
3. Re-check the language spec sections for definitions, bounds, disjunctions,
   built-ins, validators, and `error()`.
4. Re-check `encoding/json`, `encoding/yaml`, `list`, `strings`, `regexp`,
   `net`, `time`, and `math` package docs.
5. Run the examples in this skill against the local `cue` binary.
