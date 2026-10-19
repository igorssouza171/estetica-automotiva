# Catálogo de Serviços de Estética Automotiva

## Problema

O domínio prevê um catálogo de procedimentos, mas o projeto ainda não possui uma especificação ativa para cadastrar, consultar e manter serviços. Esse catálogo será necessário para que atendimentos e ordens de serviço possam selecionar os procedimentos oferecidos pelo estabelecimento.

## Objetivo

Especificar a gestão do catálogo de serviços no Streamlit e no Xano, mantendo persistência e regras de negócio no backend e permitindo que colaboradores autorizados mantenham os dados utilizados pela operação.

## Escopo

- Cadastrar e consultar serviços com os atributos conceituais do domínio: nome, descrição, preço base, tempo estimado e categoria.
- Disponibilizar os fluxos de cadastro e consulta na aplicação Streamlit existente, consumindo a API REST do Xano.
- Centralizar validações e persistência no Xano; a interface apresenta erros retornados pela API e pode oferecer validações básicas para orientar o usuário.
- Usar `GET /servico` para listar e `POST /servico` para cadastrar serviços, conforme o padrão confirmado para esta Change.

Nome e preço base são obrigatórios. O preço será tratado em Real (BRL), com duas casas decimais; o tempo estimado será armazenado em minutos; a categoria será texto simples. Nomes duplicados são permitidos, e a identidade de cada serviço será seu ID. A descrição, o tempo estimado e a categoria são opcionais, pois não foram definidos como obrigatórios.

## Fora de escopo

- Seleção de serviços em agendamentos ou ordens de serviço e preservação de preço/duração históricos em atendimentos.
- Associação de serviços a produtos e regras de consumo de estoque.
- Pagamentos, descontos, orçamentos e relatórios.
- Atualização, exclusão física, arquivamento ou ativação/desativação de serviços; o contrato aprovado nesta Change cobre somente listagem e cadastro.
- Autenticação e autorização por perfil, já que não há política de acesso especificada para este catálogo.

## Critérios de sucesso

- Um serviço pode ser cadastrado com os atributos aprovados e persistido pelo Xano.
- Os serviços existentes podem ser consultados na aplicação Streamlit.
- O preço é apresentado com símbolo BRL e duas casas decimais, e o tempo estimado é exibido em minutos.
- Falhas e rejeições da API não são apresentadas como operações concluídas.
- Os requisitos e cenários de `specs/catalogo-servicos/spec.md` são verificados antes do Archive.

## Impacto e dependências

A Change acrescenta a capacidade de catálogo ao app Streamlit e ao backend Xano. Ela não depende diretamente de clientes ou veículos, mas é pré-requisito para selecionar procedimentos em futuras Changes de agenda/OS. Integração com estoque e preservação dos dados históricos da OS permanecem dependências de decisões futuras.
