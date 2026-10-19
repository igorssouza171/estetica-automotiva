# Catálogo de Serviços

## Requirements

### Requirement: Cadastro e consulta de serviços

O sistema MUST permitir cadastrar e consultar serviços do estabelecimento com nome, descrição, preço base, tempo estimado e categoria. Nome e preço base MUST ser obrigatórios. O preço base MUST ser tratado em Real (BRL) com duas casas decimais. Descrição, tempo estimado e categoria são opcionais. Quando informado, o tempo estimado MUST ser armazenado e enviado em minutos usando o campo `tempo_estimado_min`; a categoria MUST ser texto simples. Nomes duplicados MUST ser permitidos, e cada serviço MUST ser identificado pelo ID retornado pelo Xano.

#### Scenario: Cadastrar serviço com dados válidos

- GIVEN que o usuário informa nome e preço base válidos
- AND que os campos opcionais informados são válidos
- WHEN a interface envia `POST /servico`
- THEN o Xano persiste o serviço e retorna seu ID
- AND a interface informa o cadastro concluído somente após a resposta bem-sucedida

#### Scenario: Cadastrar serviço com nome duplicado

- GIVEN que já existe serviço com o mesmo nome
- WHEN o usuário cadastra outro serviço com nome duplicado e dados válidos
- THEN o Xano persiste um novo registro com ID próprio
- AND ambos os serviços permanecem identificáveis pelo ID

#### Scenario: Rejeitar nome ou preço ausente

- GIVEN que nome ou preço base não foi informado
- WHEN o usuário tenta cadastrar o serviço
- THEN o cadastro não é enviado ou o Xano rejeita a solicitação
- AND a interface informa que o cadastro não foi concluído

#### Scenario: Listar serviços e tempo em minutos

- GIVEN que existem serviços cadastrados, incluindo um serviço com `tempo_estimado_min`
- WHEN a interface consulta `GET /servico`
- THEN apresenta os serviços retornados pelo Xano
- AND exibe o preço em BRL com duas casas decimais
- AND apresenta `tempo_estimado_min` como tempo em minutos

#### Scenario: Exibir catálogo vazio

- GIVEN que o Xano retorna uma lista sem serviços
- WHEN o usuário consulta o catálogo
- THEN a interface informa que não há serviços cadastrados

### Requirement: Integração Streamlit com a API Xano

O frontend Streamlit MUST usar `GET /servico` para listar e `POST /servico` para cadastrar serviços. O payload MUST usar o campo `tempo_estimado_min` para o tempo estimado, quando informado. A interface MUST apresentar erros de comunicação ou rejeições retornados pelo Xano sem indicar que os dados foram persistidos.

#### Scenario: Xano indisponível durante consulta ou cadastro

- GIVEN que a API do Xano está indisponível
- WHEN o usuário consulta ou tenta cadastrar um serviço
- THEN a interface informa que a operação não pôde ser concluída
- AND não apresenta o cadastro como persistido
