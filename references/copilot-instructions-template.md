# 🛡️ Instruções de Governança para Copilot e Agentes de IA

Este modelo define regras compartilhadas para GitHub Copilot, Cursor, Claude Code, Windsurf e outros agentes que trabalham neste repositório. Antes de adotá-lo, substitua os campos entre colchetes, remova as orientações irrelevantes e confirme que cada regra corresponde à arquitetura real do projeto.

## 1. Escopo e Precedência

- Estas instruções valem para todo o repositório, exceto quando houver orientações mais específicas para um diretório ou arquivo.
- Leia as instruções locais aplicáveis antes de editar. Em caso de conflito, siga a regra mais específica; se a decisão continuar ambígua, peça esclarecimento.
- Considere documentação, código e testes existentes como fonte de evidência. Não invente convenções, comandos, APIs ou requisitos.
- Preserve as escolhas arquiteturais existentes. Proponha mudanças estruturais apenas quando forem necessárias para o requisito e explicite seus impactos.

## 2. Arquitetura e Limites entre Componentes

- **Estrutura adotada:** [Descreva as camadas, módulos ou componentes e a responsabilidade de cada um.]
- **Direção das dependências:** [Registre quais componentes podem depender de quais outros.]
- **Propriedade de dados:** [Defina quem é responsável por cada conjunto de dados e quais acessos são permitidos.]
- **Comunicação entre serviços:** [Especifique contratos REST, eventos, filas ou outros mecanismos aprovados.]
- **Contratos e compatibilidade:** [Documente regras para APIs, DTOs, eventos, esquemas e migrações.]

Em uma arquitetura de microsserviços, um serviço não deve consultar diretamente as tabelas privadas de outro. Use os contratos de integração definidos pelo projeto. Não aplique esse exemplo se ele não corresponder à arquitetura adotada.

## 3. Padrões de Implementação

- Siga os padrões já usados no módulo afetado para nomenclatura, estrutura, tratamento de erros, logging e configuração.
- Mantenha cada alteração focada no requisito. Evite refatorações não relacionadas e não altere APIs públicas sem necessidade ou autorização.
- Reutilize dependências e utilitários existentes. Adicione uma dependência somente quando houver necessidade clara e compatibilidade com as políticas do projeto.
- Preserve compatibilidade com as versões de linguagem, frameworks e ferramentas declaradas pelo repositório.
- Mantenha código, documentação e testes coerentes com os contratos e comportamentos existentes.

## 4. Segurança e Privacidade

- Nunca inclua credenciais, tokens, chaves privadas, connection strings ou dados pessoais reais no código, em testes, exemplos, logs ou documentação versionada.
- Use o mecanismo aprovado pelo projeto para carregar segredos, como [gerenciador de segredos / variáveis de ambiente / outro mecanismo]. Não invente nem exponha valores secretos.
- Preserve autenticação, autorização, validação de entrada, proteção contra abuso e trilhas de auditoria existentes.
- Não amplie o acesso a dados nem registre informações sensíveis. Use dados sintéticos em testes e exemplos.
- Respeite as políticas de licenciamento, privacidade e tratamento de dados aplicáveis ao repositório.

## 5. Testes e Verificação

- Para uma correção, adicione ou ajuste um teste que reproduza o comportamento esperado ou a regressão.
- Para uma funcionalidade, cubra os fluxos relevantes, casos de erro e limites de entrada; prefira os frameworks de teste já adotados.
- Execute as verificações pertinentes à área alterada. Não declare que uma verificação passou se ela não foi executada.

| Verificação | Comando confirmado | Quando executar |
|---|---|---|
| Testes | `[comando]` | [escopo ou filtro] |
| Lint / análise estática | `[comando]` | [quando aplicável] |
| Build / compilação | `[comando]` | [quando aplicável] |

## 6. Contexto e Arquivos Excluídos

- Respeite `.copilotignore`, `.gitignore` e as instruções locais de exclusão.
- Não carregue artefatos de build, dependências instaladas, caches, logs, segredos ou dados locais como contexto, salvo quando forem indispensáveis à tarefa e seu acesso for permitido.
- Prefira inspecionar os arquivos diretamente relacionados ao requisito em vez de ler diretórios inteiros sem necessidade.

## 7. Fluxo de Trabalho do Agente

1. Identifique o comportamento solicitado, o módulo responsável e os critérios de aceitação conhecidos.
2. Leia as instruções aplicáveis, a implementação relevante e os testes próximos antes de propor uma alteração.
3. Faça uma mudança pequena e verificável; preserve alterações preexistentes e não sobrescreva trabalho do usuário.
4. Atualize testes e documentação quando contratos, comportamento ou operação forem afetados.
5. Execute as verificações documentadas que se aplicam e informe claramente qualquer bloqueio ou teste não executado.
6. Na resposta final, resuma as alterações, as verificações realizadas e as limitações restantes. Não afirme resultados que não foram confirmados.
