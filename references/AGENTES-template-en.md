# 🤖 AGENTS.md — Agent Guide for [SYSTEM NAME]

This file provides shared guidance for AI assistants working in this repository. Fill in the bracketed fields, remove sections that do not apply, and keep only information that is verified and useful for working with the codebase.

## 1. Scope and Precedence

- These instructions apply across the repository unless a more specific `AGENTS.md` exists in a subdirectory.
- Before changing a module, read any applicable local instructions as well.
- If instructions conflict or an important decision is undocumented, do not guess; ask for clarification.
- Follow established conventions. Treat examples and placeholders in this template as prompts, not as facts about the project.

## 2. Repository Overview

- **Purpose:** [Describe in one or two sentences what problem the system solves.]
- **Architecture:** [Monolith, monorepo, microservices, or other structure; briefly explain how the parts fit together.]
- **Core technologies:** [Relevant languages, frameworks, databases, and infrastructure.]
- **Entry points:** [Main application, API, UI, or process.]

### Module map

| Module | Responsibility | Technologies | Port/entry point | Local instructions |
|---|---|---|---|---|
| `[name]` | [responsibility] | [stack] | [port or entry point] | [`./path/AGENTS.md`](./path/AGENTS.md) |
| `[name]` | [responsibility] | [stack] | [port or entry point] | [`./path/AGENTS.md`](./path/AGENTS.md) |

## 3. Architecture and Boundaries

- **Module ownership:** [Define what belongs to each service or package and what should remain outside it.]
- **Inter-component communication:** [Document allowed REST contracts, events, queues, or other mechanisms.]
- **Data ownership:** [Identify which components own each data set and how other components may access it.]
- **Layers and dependencies:** [Describe the architecture layers and permitted dependency direction.]
- **Compatibility:** [Document rules for public APIs, events, persisted formats, or migrations.]

Do not introduce a dependency, architectural pattern, or cross-module integration without checking the project's conventions and impact.

## 4. Security and Sensitive Data

- Never place credentials, tokens, private keys, connection strings, or real personal data in code, examples, logs, or versioned documentation.
- Load secrets through the project's approved mechanism, such as a secret manager or environment variables.
- Do not weaken authentication, authorization, input validation, or audit controls to make an implementation easier.
- Handle configuration files, migrations, and production data according to the project's access policies; inspect only what the task requires.

## 5. Project Commands

Use commands confirmed by the documentation or configuration files. Do not invent commands; update this table when the workflow changes.

| Purpose | Command | Notes |
|---|---|---|
| Install dependencies | `[command]` | [prerequisites or working directory] |
| Build / prepare | `[command]` | [scope or profile] |
| Run tests | `[command]` | [suite or filters] |
| Lint / static analysis | `[command]` | [when applicable] |
| Run locally | `[command]` | [required configuration] |

## 6. Context Exclusions

Do not read, index, or use the following as context unless the task explicitly requires it:

- Build output and installed dependencies: `target/`, `build/`, `dist/`, `node_modules/`, `.venv/`
- Logs, temporary files, and caches: `*.log`, `*.tmp`, `.cache/`
- Secrets, local data, or protected files: [add repository-specific patterns]

Also honor `.gitignore`, `.copilotignore`, and any local exclusion rules.

## 7. Working in This Repository

1. Identify the affected module and review its instructions, nearby implementation, and related tests before editing.
2. Make the smallest change that satisfies the requirement; avoid unrelated refactoring or scope expansion.
3. Preserve existing user changes and do not overwrite files or data unnecessarily.
4. Update tests and documentation when behavior, contracts, or operational workflows change.
5. Run relevant tests and checks using the documented commands. If they cannot be run, state that clearly.
6. When finished, summarize the changes, checks performed, and any relevant limitations.

## 8. Definition of Done

Consider a task complete when:

- [ ] The change meets the requirement and respects this repository's architectural boundaries.
- [ ] Relevant tests and checks pass, or their limitations are documented.
- [ ] Affected documentation and contracts are up to date.
- [ ] No secrets, sensitive data, or generated artifacts were included unintentionally.
