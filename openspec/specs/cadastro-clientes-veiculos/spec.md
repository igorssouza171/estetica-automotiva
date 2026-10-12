# Cadastro de Clientes e Veículos

## Requirements

### Requirement: Cadastro e consulta de clientes

O sistema MUST permitir cadastrar e consultar clientes com os atributos conceituais de nome, telefone/WhatsApp, CPF/CNPJ, e-mail e endereço. Nome e telefone MUST ser obrigatórios e não podem ser vazios. Os demais atributos são opcionais nesta Change. O backend MUST persistir os dados e rejeitar a ausência de nome ou telefone; validações críticas permanecem no backend.

#### Scenario: Cadastrar cliente com dados aceitos

- GIVEN que os dados enviados atendem às validações configuradas no backend
- WHEN um usuário cadastra um cliente pela interface
- THEN o backend persiste o cliente
- AND a interface apresenta o registro persistido

#### Scenario: Consultar cliente cadastrado

- GIVEN que existe um cliente persistido
- WHEN o usuário consulta os clientes
- THEN o sistema apresenta os dados disponíveis do cliente

#### Scenario: Rejeitar dados de cliente inválidos

- GIVEN que o nome ou telefone não foi informado ou contém somente espaços
- WHEN o usuário tenta cadastrar o cliente
- THEN o backend rejeita a operação
- AND a interface informa que o cadastro não foi concluído

### Requirement: Cadastro e consulta de veículos

O sistema MUST permitir cadastrar e consultar veículos com os atributos conceituais de placa, marca, modelo, ano, cor e categoria. Placa e modelo MUST ser obrigatórios e não podem ser vazios. Os demais atributos são opcionais nesta Change. O backend MUST persistir os dados e rejeitar a ausência de placa ou modelo; validações críticas permanecem no backend.

#### Scenario: Cadastrar veículo de cliente existente

- GIVEN que existe um cliente cadastrado
- AND que os dados do veículo atendem às validações configuradas no backend
- WHEN o usuário cadastra o veículo selecionando esse cliente
- THEN o backend persiste o veículo associado ao cliente
- AND a interface apresenta o registro persistido com o proprietário associado

#### Scenario: Consultar veículo cadastrado

- GIVEN que existe um veículo persistido
- WHEN o usuário consulta os veículos
- THEN o sistema apresenta os dados disponíveis do veículo e seu proprietário

#### Scenario: Rejeitar referência de proprietário inexistente

- GIVEN que o identificador de cliente informado não corresponde a um cliente existente
- WHEN o usuário tenta cadastrar o veículo
- THEN o backend rejeita a operação
- AND nenhum veículo sem proprietário válido é persistido

#### Scenario: Rejeitar dados obrigatórios de veículo ausentes

- GIVEN que a placa ou o modelo não foi informado ou contém somente espaços
- WHEN o usuário tenta cadastrar o veículo
- THEN o backend rejeita a operação
- AND a interface informa que o cadastro não foi concluído

### Requirement: Integridade do vínculo proprietário-veículo

Cada veículo MUST estar associado a exatamente um cliente existente. Um cliente MAY estar associado a vários veículos. O backend MUST manter essa integridade e oferecer consultas que permitam visualizar os veículos de um cliente e o proprietário atual de um veículo.

#### Scenario: Consultar veículos por cliente

- GIVEN que um cliente possui um ou mais veículos cadastrados
- WHEN o usuário consulta os veículos desse cliente
- THEN o sistema apresenta os veículos associados a ele

#### Scenario: Impedir veículo sem proprietário

- GIVEN que uma solicitação de cadastro de veículo não informa um cliente válido
- WHEN a solicitação é processada pelo backend
- THEN a operação é rejeitada
- AND não é criado vínculo órfão

### Requirement: Interface de cadastro e consulta

O frontend Streamlit MUST disponibilizar fluxos para cadastrar e consultar clientes e veículos, consumindo a API REST protegida do Xano. O frontend MUST apresentar o resultado da operação e erros retornados pelo backend sem substituir as validações críticas do backend. A validação visual de campos obrigatórios MAY ser repetida para orientar o usuário.

#### Scenario: API indisponível durante operação

- GIVEN que a API do Xano não está disponível
- WHEN o usuário tenta cadastrar ou consultar um registro
- THEN a interface informa que a operação não pôde ser concluída
- AND não apresenta o registro como persistido
