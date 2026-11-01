# Enterprise Codebase Sanitizer

Transforme repositórios complexos em contexto Markdown menor para NotebookLM,
Claude Code, Cursor e Copilot. Ferramenta Python **offline**, sem dependências
externas, que remove lixo técnico e omite arquivos com possíveis segredos.

## Uso

Requer Python 3.10+ em Linux/macOS (a saída segura utiliza hard links).

```sh
python3 sanitizer.py /caminho/do/repositorio -o /tmp/context.sanitized.md
# Alternativa com o script:
sh scripts/sanitize.sh /caminho/do/repositorio -o /tmp/context.sanitized.md
```

O diretório de saída deve existir. Uma saída existente só é substituída com
`--force`; links simbólicos de saída são recusados. A saída pode ficar dentro
do repositório e não será incluída na leitura seguinte.

```sh
python3 sanitizer.py /caminho/do/repositorio \
  -o /tmp/context.sanitized.md --max-file-bytes 256000 \
  --max-context-bytes 2000000 --force
python3 -m unittest discover -s tests -v
```

## Filtros e segurança

- Exclui controle de versão, dependências, caches e artefatos (`.git`,
  `node_modules`, `vendor`, `dist`, `build`, etc.), lockfiles e logs.
- Exclui `.env*`, credenciais conhecidas, chaves privadas e diretórios de
  credenciais (`.aws`, `.ssh`, `.gnupg`).
- Não segue links simbólicos; ignora arquivos especiais, binários, texto não
  UTF-8 e arquivos maiores que o limite (256 KB por padrão).
- Detecta atribuições de senha/token/chave, chaves privadas, tokens comuns,
  JWTs, cabeçalhos de autorização e URLs com usuário/senha. **Omite o arquivo
  inteiro**, evitando deixar fragmentos de segredos multilinha na saída.
- Compacta linhas vazias consecutivas e espaços finais, preservando comentários
  e código. Ordena os arquivos e limita os trechos incluídos a 2 MB por padrão;
  os cabeçalhos e separadores Markdown acrescentam um pequeno overhead.
- Publica a saída atomicamente, com permissões `0600` desde a criação, sem
  modificar os arquivos de origem e sem chamadas de rede.

**Limitações:** proteção heurística, não certificação de segurança corporativa.
Segredos ofuscados, formatos desconhecidos ou valores sem identificação podem
passar; falsos positivos podem excluir arquivos úteis. Execute sobre uma cópia
estável e confiável do repositório, não sobre diretórios alterados por terceiros
durante a leitura. Revise a saída e use o scanner de segredos aprovado pela sua
organização antes de compartilhar. Contexto sanitizado ainda pode conter código
confidencial e prompt injection; a ferramenta não torna seu compartilhamento
automaticamente autorizado ou seguro.

## Redução de tokens e uso com IAs

A remoção de dependências e artefatos pode reduzir **até 80% ou mais** em
repositórios com muito lixo técnico, mas não há garantia: projetos pequenos
podem até produzir um documento maior. A CLI mostra estimativas por
`caracteres / 4` do texto efetivamente lido e do documento final, não uma
medição pelo tokenizer da IA nem de todo o repositório (diretórios excluídos
não são percorridos). Ajuste os limites ao orçamento da ferramenta escolhida.

Após revisão humana, carregue o Markdown como fonte no NotebookLM ou como
contexto nas demais ferramentas. O sanitizador não envia nem integra
automaticamente com esses serviços. O template em
[`templates/AGENTS.md`](templates/AGENTS.md) pode ser adaptado para instruções
de agentes; use os mecanismos de instrução suportados por cada ferramenta.

Link de venda: https://asantana3.gumroad.com/l/codebase-sanitizer-ai-notebooklm
