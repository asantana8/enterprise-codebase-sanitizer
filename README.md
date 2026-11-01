# Enterprise Codebase Sanitizer & Context Architect (SKILL.md)

[![Buy on Gumroad](https://img.shields.io/badge/Gumroad-Buy%20Global%20(%2419.99)-orange?style=for-the-badge&logo=gumroad)](https://asantana3.gumroad.com/l/codebase-sanitizer-ai-notebooklm)
[![Comprar no Kiwify](https://img.shields.io/badge/Kiwify-Comprar%20no%20Brasil%20(R%2497)-green?style=for-the-badge)]([SEU_LINK_DO_KIWIFY_AQUI](https://pay.kiwify.com.br/RrSx0KC))

> **Sanitize enterprise codebases into lean, highly context-aware inputs for NotebookLM, Claude Code, Cursor, and IDE AI Agents.**

---

## 🎯 The Problem

When feeding entire repositories to LLMs or RAG pipelines, developers face three major bottlenecks:
1. **Token Bloat & High Costs:** Build artifacts, lockfiles, minified JS, and deep directory trees waste up to 80% of your context window.
2. **Security & Data Leaks:** Accidental exposure of `.env` secrets, API keys, certificates, and private configs to external AI models.
3. **Context Hallucinations:** AI agents lose track of architecture when flooded with noise instead of core domain logic.

---

## 💡 The Solution

**Enterprise Codebase Sanitizer** is a deterministic Python toolchain coupled with an enterprise-grade agent orchestration methodology (`SKILL.md` + `AGENTS.md`).

It systematically parses, sanitizes, and consolidates complex source code structures into a unified, secure, token-optimized context payload designed specifically for AI models.

---

## ✨ Key Features

* 🔐 **Automated Secret Scrubbing:** Strips API keys, connection strings, credentials, and sensitive environmental parameters before AI exposure.
* 🧹 **Aggressive Token Optimization:** Eliminates binary noise, vendor directories (`node_modules`, `target`, `.git`), build artifacts, and auto-generated lockfiles.
* 🧠 **Architectural Alignment:** Embeds standardized `AGENTS.md` and `SKILL.md` instruction layers so AI coding tools (Claude Code, GitHub Copilot, Cursor) follow strict project constraints.
* ⚡ **NotebookLM & RAG Ready:** Formats consolidated outputs into structured single-file representations optimized for Google NotebookLM source uploads and vector index ingestion.

---

## 📦 What's Included in the Suite?

When you acquire the suite via Gumroad or Kiwify, you receive the full distribution package (`enterprise-codebase-sanitizer.zip`):

1. **`consolidador_lm.py`** – Core sanitizer & consolidation engine.
2. **`setup_agents.py`** – Automated prompt & context governance bootstrapping script.
3. **`SKILL.md`** – Complete methodology guide for AI-assisted code orchestration.
4. **`AGENTS.md` Template** – Battle-tested prompt engineering framework for agentic workflows.
5. **Execution Guide (PDF)** – Step-by-step setup documentation.

---

## 🚀 Getting Started (Quick Preview)

```bash
# Clone this repository
git clone [https://github.com/SEU_USUARIO/enterprise-codebase-sanitizer.git](https://github.com/SEU_USUARIO/enterprise-codebase-sanitizer.git)
cd enterprise-codebase-sanitizer

# Run the sanitizer on your project directory (requires full suite package)
python consolidador_lm.py --path /path/to/your/codebase --output consolidated_context.txt
