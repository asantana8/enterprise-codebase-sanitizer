# Enterprise Codebase Sanitizer & Context Architect (`SKILL.md`)

Pacote completo de habilidade (`SKILL.md`) e scripts de automação em Python para otimizar bases de código corporativas, preparar contextos higienizados para o NotebookLM/RAG e estabelecer governança para agentes de IA (Claude Code, Cursor, Windsurf, Copilot).

---

## 📦 Conteúdo do Pacote

- `SKILL.md`: Especificação técnica principal no padrão de marketplaces (Agensi).
- `scripts/consolidador_lm.py`: Script Python para remoção de comentários, filtro de credenciais sensíveis e consolidação de código.
- `scripts/setup_agents-v2.py`: Script Python agnóstico que inspeciona manifestos (`pom.xml`, `package.json`, etc.), detecta portas e gera arquivos `AGENTS.md` locais e globais.
- `references/copilot-instructions-template.md`: Template de governança para `.github/copilot-instructions.md`.
- `references/AGENTS-template.md`: Template de guia de orientação para monorepos.

---

## 🚀 Como Utilizar

### 1. Upload em Marketplaces (Agensi)
Envie o arquivo `.zip` diretamente para a plataforma. O pacote atende a todas as exigências do *security scan* por utilizar scripts Python em código-fonte original.

### 2. Execução Local
```bash
# Consolidação e higienização de fontes
python scripts/consolidador_lm.py --raiz . --perfil java

# Mapeamento e geração de governança de agentes
python scripts/setup_agents-v2.py --raiz . --nome-sistema "MeuSistema"
```
