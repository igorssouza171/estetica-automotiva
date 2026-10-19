# Catálogo de Serviços

## ADDED Requirements

### Requirement: Cadastro e consulta de serviços

O sistema MUST permitir cadastrar e consultar serviços do estabelecimento com os atributos nome, descrição, preço base, tempo estimado em minutos e categoria. Nome e preço base MUST ser obrigatórios. O preço base MUST ser representado em Real (BRL) com duas casas decimais. Tempo estimado e categoria são opcionais nesta Change; quando informado, o tempo estimado MUST ser expresso em minutos e a categoria MUST ser texto simples. O backend MUST persistir os dados e aplicar essas regras. Nomes duplicados MUST ser permitidos; o ID MUST identificar cada serviço.

#### Scenario: Cadastrar serviço com dados aceitos

- GIVEN que os dados enviados atendem às validações aprovadas e configuradas no backend
- WHEN um usuário cadastra um serviço pela interface Streamlit
- THEN o backend persiste o serviço
- AND a interface informa que o cadastro foi concluído

#### Scenario: Cadastrar serviços com nomes duplicados

- GIVEN que já existe um serviço com determinado nome
- WHEN o usuário cadastra outro serviço com o mesmo nome e dados válidos
- THEN o backend persiste o novo serviço com um ID próprio
- AND os dois serviços permanecem consultáveis como registros distintos

#### Scenario: Consultar serviços cadastrados

- GIVEN que existem serviços persistidos no Xano
- WHEN o usuário abre a consulta do catálogo
- THEN o sistema apresenta os dados disponíveis de cada serviço

#### Scenario: Consultar catálogo sem serviços

- GIVEN que não há serviços cadastrados
- WHEN o usuário abre a consulta do catálogo
- THEN a interface informa que não há serviços cadastrados

#### Scenario: Rejeitar campos obrigatórios ausentes

- GIVEN que nome ou preço base está ausente
- WHEN o usuário tenta cadastrar o serviço
- THEN o backend rejeita a operação
- AND a interface informa que o cadastro não foi concluído

### Requirement: Interface Streamlit integrada ao Xano

O frontend Streamlit MUST oferecer os fluxos de cadastro e consulta de serviços por meio da API REST do Xano. O frontend MUST usar `GET /servico` para listar e `POST /servico` para cadastrar. O frontend MUST apresentar falhas de comunicação ou erros retornados pelo backend sem informar que a operação foi concluída.

#### Scenario: API indisponível durante consulta ou gravação

- GIVEN que a API do Xano não está disponível
- WHEN o usuário consulta ou cadastra um serviço
- THEN a interface informa que a operação não pôde ser concluída
- AND não apresenta a operação como persistida
