# Ordens de Serviço

## ADDED Requirements

### Requirement: Abertura de Ordem de Serviço

O sistema MUST permitir abrir uma OS associando um cliente existente, um veículo existente pertencente a esse cliente e um ou mais serviços existentes, identificados por seus IDs. O frontend MUST calcular `valor_total` como a soma dos preços dos serviços selecionados. O backend MUST validar essas referências e persistir a OS com status `Aguardando`, cliente, veículo, total e observações em `POST /ordem_servico`. Após receber o ID da OS, o cliente MUST criar um item por serviço em `POST /item_ordem_servico`, congelando o preço unitário do serviço. A OS compartilha a estrutura base do agendamento.

#### Scenario: Abrir OS com vínculos válidos

- GIVEN que o cliente existe
- AND que o veículo pertence ao cliente selecionado
- AND que um ou mais serviços existem
- WHEN o atendente abre uma OS com essas referências
- THEN o backend persiste a OS e suas associações
- AND a OS recebe um ID e o status inicial `Aguardando`
- AND o payload da OS contém status `Aguardando` e o total calculado
- AND cada item é persistido com seu preço unitário
- AND a interface informa sucesso somente após a resposta bem-sucedida

#### Scenario: Rejeitar vínculos inválidos

- GIVEN que o cliente, o veículo ou algum serviço não existe, ou que o veículo pertence a outro cliente
- WHEN a interface tenta abrir a OS
- THEN o backend rejeita a operação
- AND não persiste uma OS com associações inválidas
- AND a interface apresenta a rejeição sem indicar sucesso

### Requirement: Atualização de status da OS

O sistema MUST permitir atualizar o status de uma OS existente. Os status válidos MUST ser `Aguardando`, `Em Andamento`, `Concluído`, `Entregue` e `Cancelado`. O backend MUST permitir avanço de somente um estado por vez na sequência `Aguardando` → `Em Andamento` → `Concluído` → `Entregue`, ou cancelamento a partir de qualquer status não cancelado. `Cancelado` MUST ser terminal. O backend MUST rejeitar saltos ou transições após cancelamento e persistir a mudança antes de a interface apresentar sucesso.

#### Scenario: Atualizar status por transição permitida

- GIVEN que existe uma OS
- AND que a transição solicitada é permitida pela matriz aprovada
- WHEN um usuário autorizado atualiza o status
- THEN o backend persiste o novo status
- AND a listagem apresenta o status atualizado

#### Scenario: Rejeitar transição não permitida

- GIVEN que existe uma OS
- AND que a transição solicitada não é permitida pela matriz aprovada
- WHEN um usuário tenta atualizar o status
- THEN o backend rejeita a mudança
- AND a OS mantém o status anterior
- AND a interface informa que a atualização não foi concluída

#### Scenario: Cancelar O.S. a partir de qualquer status não cancelado

- GIVEN que existe uma O.S. em qualquer status diferente de `Cancelado`
- WHEN um usuário solicita `Cancelado`
- THEN o backend persiste o status `Cancelado`
- AND não permite novas transições após o cancelamento

### Requirement: Preço histórico dos itens da O.S.

O backend MUST obter o preço vigente de cada serviço ao abrir a O.S., salvar esse valor como preço unitário do item e calcular o total da O.S. a partir dos itens. Alterações futuras no preço-base do catálogo MUST NOT alterar os itens nem o total de O.S. já persistidas.

#### Scenario: Preservar preço após alteração no catálogo

- GIVEN que uma O.S. possui itens com preço unitário congelado
- WHEN o preço-base do serviço no catálogo é alterado posteriormente
- THEN o preço unitário do item da O.S. permanece inalterado
- AND o valor total histórico da O.S. permanece igual à soma dos itens

### Requirement: Listagem de Ordens de Serviço

O sistema MUST permitir listar OS persistidas e apresentar, no mínimo, o ID, o cliente, o veículo, os serviços associados, o status atual e o valor total. Os preços unitários congelados devem ser apresentados quando retornados pelo backend. Os dados relacionados apresentados MUST corresponder aos IDs persistidos no backend.

#### Scenario: Consultar OS e suas entidades relacionadas

- GIVEN que existem OS com cliente, veículo e serviços associados
- WHEN o usuário consulta a listagem
- THEN a interface apresenta cada OS com os dados relacionados e o status atual
- AND apresenta preços unitários congelados e valor total quando retornados pelo backend

#### Scenario: Consultar listagem vazia

- GIVEN que não há OS cadastradas
- WHEN o usuário abre a listagem
- THEN a interface informa que não existem OS para apresentar

### Requirement: Integração da OS entre Streamlit e Xano

O frontend Streamlit MUST usar `GET /ordem_servico` para listar, `POST /ordem_servico` para abrir e `PATCH /ordem_servico/{id}/status` para atualizar status. O frontend MUST apresentar erros de comunicação ou rejeições do backend sem indicar persistência ou atualização bem-sucedida.

#### Scenario: API indisponível no fluxo da OS

- GIVEN que a API do Xano está indisponível
- WHEN o usuário lista, abre ou atualiza uma OS
- THEN a interface informa que a operação não pôde ser concluída
- AND não apresenta a operação como persistida
