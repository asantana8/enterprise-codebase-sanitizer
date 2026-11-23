# 🛡️ Governance Instructions for Copilot and AI Agents

This template defines shared rules for GitHub Copilot, Cursor, Claude Code, Windsurf, and other agents working in this repository. Before adopting it, replace the bracketed fields, remove irrelevant guidance, and confirm that every rule reflects the project's actual architecture.

## 1. Scope and Precedence

- These instructions apply across the repository unless more specific guidance exists for a directory or file.
- Read applicable local instructions before editing. When rules conflict, follow the more specific instruction; if the decision remains unclear, ask for clarification.
- Treat existing documentation, code, and tests as evidence. Do not invent conventions, commands, APIs, or requirements.
- Preserve established architectural choices. Propose structural changes only when needed to meet the requirement, and explain their impact.

## 2. Architecture and Component Boundaries

- **Architecture:** [Describe the layers, modules, or components and their responsibilities.]
- **Dependency direction:** [Document which components may depend on one another.]
- **Data ownership:** [Define who owns each data set and what access is permitted.]
- **Service communication:** [Specify approved REST contracts, events, queues, or other mechanisms.]
- **Contracts and compatibility:** [Document rules for APIs, DTOs, events, schemas, and migrations.]

In a microservices architecture, a service must not query another service's private tables directly. Use the integration contracts defined by the project. Do not apply this example if it does not match the chosen architecture.

## 3. Implementation Standards

- Follow the affected module's existing patterns for naming, structure, error handling, logging, and configuration.
- Keep each change focused on the requirement. Avoid unrelated refactoring, and do not change public APIs without need or authorization.
- Reuse existing dependencies and utilities. Add a dependency only when there is a clear need and it complies with project policy.
- Preserve compatibility with the language, framework, and tool versions declared by the repository.
- Keep code, documentation, and tests consistent with existing contracts and behavior.

## 4. Security and Privacy

- Never place credentials, tokens, private keys, connection strings, or real personal data in code, tests, examples, logs, or versioned documentation.
- Load secrets through the project's approved mechanism, such as [secret manager / environment variables / other mechanism]. Never invent or expose secret values.
- Preserve existing authentication, authorization, input validation, abuse protections, and audit trails.
- Do not broaden data access or log sensitive information. Use synthetic data in tests and examples.
- Follow the licensing, privacy, and data-handling policies that apply to this repository.

## 5. Testing and Verification

- For a bug fix, add or update a test that captures the expected behavior or regression.
- For a feature, cover relevant user flows, error cases, and input boundaries; prefer the project's existing test frameworks.
- Run checks relevant to the changed area. Do not claim a check passed unless it was actually run.

| Check | Confirmed command | When to run |
|---|---|---|
| Tests | `[command]` | [scope or filter] |
| Lint / static analysis | `[command]` | [when applicable] |
| Build / compile | `[command]` | [when applicable] |

## 6. Context and Excluded Files

- Honor `.copilotignore`, `.gitignore`, and any local exclusion instructions.
- Do not load build artifacts, installed dependencies, caches, logs, secrets, or local data into context unless essential to the task and access is permitted.
- Prefer inspecting files directly related to the requirement over reading entire directories without a clear need.

## 7. Agent Workflow

1. Identify the requested behavior, the responsible module, and any known acceptance criteria.
2. Review applicable instructions, relevant implementation, and nearby tests before proposing a change.
3. Make a small, verifiable change; preserve pre-existing changes and do not overwrite the user's work.
4. Update tests and documentation when contracts, behavior, or operations are affected.
5. Run applicable documented checks and clearly report any blockers or checks that were not run.
6. In the final response, summarize the changes, checks performed, and remaining limitations. Do not claim results that have not been verified.
