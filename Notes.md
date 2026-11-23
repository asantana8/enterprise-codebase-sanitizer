# Nota sobre compatibilidade do `AGENTS.md`

O `AGENTS.md` é um arquivo de instruções compartilhado, criado para orientar agentes de programação com IA sobre a arquitetura, as convenções, os comandos e os limites de um repositório. Ele pode ser usado por qualquer ferramenta de codificação com IA que ofereça suporte a esse formato; a descoberta e o carregamento automáticos dependem de cada ferramenta e de sua configuração.

## Claude Code

A Anthropic adicionou suporte nativo a `AGENTS.md` no Claude Code `v2.1.277`, publicado em **18 de setembro de 2026**. A partir dessa versão, Claude Code pode usar o `AGENTS.md` do projeto como instruções sem exigir uma cópia em `CLAUDE.md` ou uma importação manual.

Por padrão, Claude Code carrega `AGENTS.md` quando não encontra `CLAUDE.md`, `.claude/CLAUDE.md` ou `CLAUDE.local.md` no diretório de trabalho ou em um diretório ancestral. Para carregar os arquivos `AGENTS.md` e `CLAUDE.md` em conjunto, ajuste **Project instructions** em `/config` para `claude-md-and-agents-md`. A disponibilidade pode variar em versões antigas ou em determinadas configurações e provedores; consulte a documentação oficial para confirmar o comportamento da instalação em uso.

## Compatibilidade entre ferramentas

Manter as regras gerais do projeto em `AGENTS.md` facilita o compartilhamento entre agentes compatíveis e reduz a duplicação de instruções. Isso não substitui arquivos específicos de cada ferramenta quando eles forem necessários. Verifique se o agente adotado reconhece `AGENTS.md`, qual precedência aplica quando há outros arquivos de instruções e se há configurações locais que alteram o carregamento.

## Fontes oficiais

- [Claude Code: How Claude remembers your project](https://code.claude.com/docs/en/memory#agents-md)
- [Claude Code v2.1.277 release notes](https://github.com/anthropics/claude-code/releases/tag/v2.1.277)
