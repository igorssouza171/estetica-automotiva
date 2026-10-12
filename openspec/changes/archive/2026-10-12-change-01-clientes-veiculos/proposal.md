# Cadastro de Clientes e Veículos

## Problema

O projeto ainda não possui uma capacidade especificada para registrar e consultar clientes e veículos. Sem esses dados e seu vínculo de propriedade, os atendimentos futuros não poderão identificar de forma confiável quem é o responsável pelo veículo.

## Objetivo

Implementar o cadastro e a consulta de clientes e veículos para um único estabelecimento, mantendo no backend a persistência, as validações e a integridade do vínculo proprietário-veículo.

## Escopo

- Cadastrar e consultar clientes com os atributos conceituais definidos no modelo de domínio: nome, telefone/WhatsApp, CPF/CNPJ, e-mail e endereço.
- Cadastrar e consultar veículos com os atributos conceituais definidos no modelo de domínio: placa, marca, modelo, ano, cor e categoria.
- Associar cada veículo cadastrado a um cliente existente e permitir consultar os veículos de um cliente e o proprietário associado a um veículo.
- Disponibilizar fluxos de interface para cadastro e consulta, consumindo a API REST do Xano.
- Manter regras de validação e integridade no backend.

A escolha do frontend desta Change está definida como Streamlit. Nome e telefone são obrigatórios para Cliente; placa e modelo são obrigatórios para Veículo. Os demais atributos conceituais permanecem opcionais nesta Change. Nenhuma regra de unicidade, formato específico ou normalização além da rejeição de valores obrigatórios vazios foi aprovada.

## Fora de escopo

- Agendamentos, ordens de serviço, serviços, estoque e relatórios.
- Autenticação, gestão de usuários e definição de permissões, que não estão especificadas nesta Change.
- Exclusão de registros, transferência de propriedade com histórico e políticas de arquivamento.
- Regras de deduplicação de clientes ou veículos além das validações que forem aprovadas antes do Apply.
- Suporte a múltiplos estabelecimentos.

## Critérios de sucesso

- Um cliente pode ser cadastrado e consultado pela interface através da API.
- Um veículo pode ser cadastrado associado a um cliente existente e consultado com seu proprietário.
- O backend impede a criação de veículo sem referência válida a um cliente.
- A consulta de um cliente permite identificar os veículos associados a ele.

## Impacto

A Change estabelece os cadastros-base para agenda/OS e histórico de atendimentos. Afeta o modelo relacional e as APIs no Xano e os fluxos de cadastro e consulta no frontend Python escolhido para o projeto.
