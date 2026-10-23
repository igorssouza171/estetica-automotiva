# Fluxo de Ordens de Serviço

## Problema

O projeto já especifica cadastros de clientes, veículos e serviços, mas ainda não possui uma capacidade para registrar e acompanhar um atendimento que reúna esses dados. Sem a OS, o estabelecimento não tem um ponto único para identificar o cliente, o veículo atendido, os serviços escolhidos e o andamento do trabalho.

## Objetivo

Especificar o fluxo inicial de abertura, listagem e acompanhamento de status das Ordens de Serviço no Streamlit e no Xano, reutilizando as entidades das Changes 01 e 02 e mantendo validação, persistência e transições de status no backend.

A OS e o agendamento usarão uma estrutura base compartilhada que evolui pelos status aprovados: `Aguardando`, `Em Andamento`, `Concluído`, `Entregue` e `Cancelado`.

## Escopo

- Abrir uma OS vinculando um cliente existente, um veículo pertencente a esse cliente e um ou mais serviços existentes.
- Gerar automaticamente a data/hora de abertura no backend e calcular a previsão de entrega pela soma das durações dos serviços, ou aceitar uma previsão manual.
- Congelar o preço-base de cada serviço no item da O.S. no momento da abertura e calcular o total pela soma dos preços unitários dos itens.
- Listar OS com identificador, cliente, veículo, serviços, data/hora quando definida e status atual.
- Consultar e atualizar status em sequência (`Aguardando` → `Em Andamento` → `Concluído` → `Entregue`) ou cancelar a partir de qualquer status não cancelado, por operação validada no Xano.
- Usar `GET /ordem_servico`, `POST /ordem_servico` e `PATCH /ordem_servico/{id}/status`.
- Disponibilizar os fluxos na aplicação Streamlit existente, consumindo a API REST do Xano.
- Validar no backend a existência e a integridade dos vínculos entre cliente, veículo e serviços.

## Fora de escopo

- Cadastro ou edição de clientes, veículos e serviços, já tratados em Changes anteriores.
- Baixa ou associação de produtos/insumos, pagamentos, descontos, emissão fiscal e relatórios.
- Portal público ou notificações externas para acompanhamento por clientes.
- Definição de agenda completa, expediente, capacidade, recursos/baias e prevenção de conflitos de horário.
- Registro de histórico/auditoria detalhado das transições, além do status atual, salvo se uma decisão de domínio o tornar requisito para esta Change.

## Critérios de sucesso

- A OS é persistida com referências válidas a cliente, veículo e um ou mais serviços.
- O backend rejeita referências inexistentes e vínculo de veículo que não corresponda ao cliente selecionado.
- A listagem apresenta o status atual e os dados relacionados necessários para identificar cada OS.
- A alteração de status segue as transições aprovadas e é persistida pelo Xano antes de a interface indicar sucesso.
- A data de abertura, os preços unitários dos itens e o total são determinados pelo backend; alterações futuras no catálogo não alteram o total histórico da OS.
- Falhas da API não são apresentadas como operações concluídas.
- Os requisitos e cenários de `specs/ordens-servico/spec.md` são verificados antes do Archive.

## Impacto e dependências

A Change depende das capacidades de clientes/veículos e catálogo de serviços (Changes 01 e 02). Ela estabelece a ligação operacional entre essas entidades e é base para futuras Changes de estoque, execução detalhada, histórico e relatórios. O preço base do serviço não deve ser tratado como preço histórico da OS sem uma decisão explícita sobre cópia de valores no momento da contratação.
