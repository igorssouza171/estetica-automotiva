# Design — Cadastro de Clientes e Veículos

## Contexto

O modelo de domínio já identifica Cliente e Veículo e declara que um cliente pode possuir vários veículos e que cada veículo pertence a um cliente. O repositório ainda não contém código de aplicação nem especificações OpenSpec existentes. Esta Change cria a primeira especificação funcional para esses cadastros.

As decisões do projeto determinam um único estabelecimento, que agendamento e OS compartilharão uma estrutura base evolutiva por status e que o frontend desta Change será Streamlit. Nome e telefone são obrigatórios para Cliente; placa e modelo são obrigatórios para Veículo.

## Objetivos

- Registrar clientes e veículos na persistência relacional do Xano.
- Representar o vínculo de propriedade no backend, sem aceitar veículo sem cliente válido.
- Permitir cadastro e consulta por meio de uma interface que consome a API REST.
- Evitar definir políticas de negócio ainda não aprovadas.

## Não objetivos

- Implementar autenticação, autorização ou gestão de colaboradores.
- Definir exclusão, arquivamento ou transferência histórica de propriedade.
- Incluir OS, agenda, serviços, estoque ou relatórios.
- Suportar mais de um estabelecimento.

## Modelo proposto

- **Cliente:** nome e telefone/WhatsApp obrigatórios; CPF/CNPJ, e-mail e endereço opcionais.
- **Veículo:** placa e modelo obrigatórios; marca, ano, cor e categoria opcionais.
- **Relacionamento:** referência obrigatória do veículo para um cliente existente. A relação é de muitos veículos para um cliente. A persistência relacional deve impedir referência inexistente.

Além da rejeição de valores obrigatórios ausentes ou compostos somente por espaços, não foram definidas regras de unicidade, normalização ou formato. A Change cobre o vínculo atual; não define histórico de proprietários.

## Arquitetura e fluxo

1. A interface solicita cadastro ou consulta.
2. A API REST do Xano valida a entrada e a referência de proprietário, persiste ou consulta os dados e devolve um resultado explícito.
3. A interface apresenta o resultado ou o erro recebido, sem ser a autoridade das regras de domínio.

O cliente Streamlit usa as seguintes operações REST relativas à URL base configurada: `GET /cliente`, `POST /cliente`, `GET /veiculo`, `POST /veiculo` e `GET /veiculo?cliente_id={id}`. Os payloads e registros usam chaves em português (`nome`, `telefone`, `cliente_id` etc.) e identificador `id`. A integração ponta a ponta foi confirmada pelo usuário como funcional.

A aplicação lê `XANO_API_BASE_URL` e `XANO_API_TOKEN` do ambiente, envia o token como Bearer e não inicia operações se qualquer configuração estiver ausente. A implantação do Xano deve restringir o token às operações necessárias e proteger os dados pessoais.

## Decisões e pendências

- Regras de formato, normalização e duplicidade além dos campos obrigatórios não foram definidas e permanecem fora do escopo desta Change.
- Definir se o vínculo de proprietário poderá ser alterado após o cadastro e se será necessário preservar histórico.
- Definir política de exclusão/arquivamento e o que ocorre quando há registros relacionados.
- Configurar e verificar no Xano a autenticação Bearer e as permissões restritas do token antes de disponibilizar a aplicação fora de ambiente controlado. A gestão de usuários e permissões por perfil não faz parte desta Change.

## Riscos

- Regras não definidas para campos e duplicidade podem levar a dados inconsistentes ou impedir cadastros legítimos.
- O cliente local depende dos nomes de campos e do formato de resposta descritos acima; divergências futuras no Xano exigirão alinhamento do contrato.
- O envio de um token Bearer pelo frontend não comprova, por si só, que o Xano está configurado para restringir o acesso aos dados pessoais.
- Alterar proprietário sem histórico pode comprometer interpretações futuras de OS; esta Change não habilita um fluxo de transferência.
- O funcionamento da integração foi confirmado pelo usuário; esta sessão não acessou diretamente o workspace Xano para repetir a validação.

## Verificação

Validar os cenários definidos em `specs/cadastro-clientes-veiculos/spec.md`, incluindo persistência, consulta, vínculo válido, rejeição de proprietário inexistente e apresentação de falha de API. As verificações devem cobrir a regra no backend e o fluxo da interface após a decisão de tecnologia.
