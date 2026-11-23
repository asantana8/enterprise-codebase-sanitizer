# 🤖 AGENTS.md — Guia de Agentes para [NOME DO SISTEMA]

Este arquivo reúne as orientações compartilhadas para assistentes de IA que atuam neste repositório. Preencha os campos entre colchetes, remova as seções que não se aplicam e mantenha aqui apenas informações verificadas e úteis para o trabalho no código.

## 1. Escopo e Precedência

- Estas orientações se aplicam a todo o repositório, salvo quando houver um `AGENTS.md` mais específico em um subdiretório.
- Antes de alterar um módulo, leia também as instruções locais aplicáveis.
- Se instruções entrarem em conflito ou uma decisão importante não estiver documentada, interrompa a suposição e peça esclarecimento.
- Preserve as convenções existentes. Não trate exemplos ou placeholders deste modelo como fatos do projeto.

## 2. Visão Geral do Repositório

- **Propósito:** [Descreva em uma ou duas frases o problema que o sistema resolve.]
- **Arquitetura:** [Monólito, monorepo, microsserviços ou outra forma; resuma como as partes se relacionam.]
- **Tecnologias principais:** [Linguagens, frameworks, bancos de dados e infraestrutura relevantes.]
- **Pontos de entrada:** [Aplicação, API, interface ou processo principal.]

### Mapa de módulos

| Módulo | Responsabilidade | Tecnologias | Porta/entrada | Instruções locais |
|---|---|---|---|---|
| `[nome]` | [responsabilidade] | [stack] | [porta ou entrada] | [`./caminho/AGENTS.md`](./caminho/AGENTS.md) |
| `[nome]` | [responsabilidade] | [stack] | [porta ou entrada] | [`./caminho/AGENTS.md`](./caminho/AGENTS.md) |

## 3. Arquitetura e Limites

- **Responsabilidade dos módulos:** [Defina o que pertence a cada serviço ou pacote e o que deve permanecer fora dele.]
- **Comunicação entre componentes:** [Documente contratos REST, eventos, filas ou outros mecanismos permitidos.]
- **Propriedade dos dados:** [Indique quais componentes são donos de cada conjunto de dados e como os demais podem acessá-los.]
- **Camadas e dependências:** [Registre as camadas adotadas e a direção permitida das dependências.]
- **Compatibilidade:** [Explique regras para APIs públicas, eventos, formatos persistidos ou migrações.]

Não introduza uma nova dependência, padrão arquitetural ou integração entre módulos sem verificar as convenções e os impactos no projeto.

## 4. Segurança e Dados Sensíveis

- Nunca inclua credenciais, tokens, chaves privadas, connection strings ou dados pessoais reais no código, em exemplos, logs ou documentação versionada.
- Carregue segredos por meio do mecanismo aprovado pelo projeto, como um gerenciador de segredos ou variáveis de ambiente.
- Não enfraqueça autenticação, autorização, validação de entrada ou controles de auditoria para facilitar uma implementação.
- Trate arquivos de configuração, migrações e dados de produção conforme as políticas de acesso do projeto; consulte apenas o necessário para a tarefa.

## 5. Comandos do Projeto

Use comandos confirmados pela documentação ou pelos arquivos de configuração. Não invente comandos; atualize esta tabela quando o fluxo mudar.

| Finalidade | Comando | Observações |
|---|---|---|
| Instalar dependências | `[comando]` | [pré-requisitos ou diretório] |
| Compilar / preparar | `[comando]` | [escopo ou perfil] |
| Executar testes | `[comando]` | [suite ou filtros] |
| Lint / análise estática | `[comando]` | [quando aplicável] |
| Executar localmente | `[comando]` | [configuração necessária] |

## 6. Exclusões de Contexto

Não leia, indexe ou use como contexto, a menos que a tarefa exija explicitamente:

- Saídas de build e dependências instaladas: `target/`, `build/`, `dist/`, `node_modules/`, `.venv/`
- Logs, temporários e caches: `*.log`, `*.tmp`, `.cache/`
- Segredos, dados locais ou arquivos protegidos: `[adicione padrões específicos do repositório]`

Respeite também `.gitignore`, `.copilotignore` e quaisquer regras locais de exclusão.

## 7. Como Trabalhar Neste Repositório

1. Identifique o módulo afetado e leia suas instruções, implementação próxima e testes relacionados antes de editar.
2. Faça a menor alteração que resolva o requisito; evite refatorações ou mudanças fora do escopo.
3. Preserve alterações existentes do usuário e não sobrescreva arquivos ou dados sem necessidade.
4. Atualize testes e documentação quando o comportamento, contrato ou fluxo operacional mudar.
5. Execute os testes e verificações pertinentes usando os comandos documentados. Se não puder executá-los, informe isso claramente.
6. Ao concluir, resuma o que mudou, quais verificações foram executadas e quaisquer limitações relevantes.

## 8. Critérios de Conclusão

Considere a tarefa concluída quando:

- [ ] A mudança atende ao requisito e respeita os limites arquiteturais deste repositório.
- [ ] Testes e verificações relevantes passaram, ou as limitações foram registradas.
- [ ] Documentação e contratos afetados foram atualizados.
- [ ] Nenhum segredo, dado sensível ou artefato gerado foi incluído por engano.
