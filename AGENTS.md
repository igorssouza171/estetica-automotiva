# Instruções para Agentes de IA — Estética Automotiva

Este arquivo estabelece as regras e restrições operacionais para os agentes de IA que atuarem neste repositório.

## 1. Regras de Contexto
- Antes de propor ou implementar qualquer alteração, consulte obrigatoriamente:
  - `docs/project-overview.md`
  - `docs/domain-model.md`
  - `openspec/config.yaml`
- Todas as alterações devem respeitar o modelo conceitual do domínio e a arquitetura tecnológica definida.

## 2. Metodologia de Desenvolvimento
- Toda alteração funcional ou técnica deve utilizar a metodologia **OpenSpec**.
- Siga estritamente o ciclo de vida do OpenSpec:
  - **Explore:** Investigar e analisar antes de implementar.
  - **Propose:** Criar a especificação e o plano de tarefas (*tasks.md*).
  - **Apply:** Executar apenas as tarefas aprovadas.
  - **Archive:** Consolidar e arquivar a *Change*.

## 3. Arquitetura e Código
- Respeite as tecnologias definidas no `project-overview.md`. Não introduza novas bibliotecas ou frameworks sem autorização prévia.
- Mantenha as regras de negócio e validações críticas centralizadas no backend (Xano/API).
- O frontend deve focar na experiência do usuário e na exibição correta das informações.
- Não modifique funcionalidades existentes sem relação com a *Change* atual.

## 4. Idioma e Documentação
- Todos os documentos, especificações, artefatos OpenSpec, comentários de código e mensagens de commit devem ser escritos em **Português do Brasil (pt-BR)**.