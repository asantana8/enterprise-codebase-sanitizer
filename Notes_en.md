# Note on `AGENTS.md` Compatibility

`AGENTS.md` is a shared instruction file that helps AI coding agents understand a repository's architecture, conventions, commands, and boundaries. It can be used with any AI coding tool that supports this format; automatic discovery and loading depend on each tool and its configuration.

## Claude Code

Anthropic added native `AGENTS.md` support in Claude Code `v2.1.277`, released on **September 18, 2026**. Starting with that version, Claude Code can use a project's `AGENTS.md` as its instructions without requiring a copy in `CLAUDE.md` or a manual import.

By default, Claude Code loads `AGENTS.md` when it does not find `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` in the working directory or any parent directory. To load both `AGENTS.md` and `CLAUDE.md`, set **Project instructions** to `claude-md-and-agents-md` in `/config`. Support may differ in older versions or in certain configurations and provider-backed sessions; check the official documentation for the behavior supported by the version in use.

## Cross-Tool Compatibility

Keeping general project rules in `AGENTS.md` makes them easier to share across compatible coding agents and reduces duplicated guidance. It does not replace tool-specific files when those are needed. Check whether each tool recognizes `AGENTS.md`, how it handles precedence when other instruction files are present, and whether local settings affect loading.

## Official Sources

- [Claude Code: How Claude remembers your project](https://code.claude.com/docs/en/memory#agents-md)
- [Claude Code v2.1.277 release notes](https://github.com/anthropics/claude-code/releases/tag/v2.1.277)
