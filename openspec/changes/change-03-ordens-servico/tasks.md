# Tarefas — Ordens de Serviço

## 1. Decisões e contrato

- [x] 1.1 Reutilizar o mesmo registro-base para agendamento e OS, evoluindo por status, conforme decisão aprovada anteriormente.
- [x] 1.2 Definir status válidos, avanço sequencial e cancelamento a partir de qualquer estado não cancelado.
- [x] 1.3 Definir abertura com status inicial `Aguardando`; previsão de entrega não faz parte do formulário desta entrega.
- [x] 1.4 Definir que observações de abertura são opcionais; datas de entrada/conclusão e edição posterior não fazem parte desta entrega.
- [x] 1.5 Definir itens da OS por IDs de serviços; o seletor não permite repetir o mesmo ID na mesma abertura.
- [x] 1.6 Definir `valor_total` calculado localmente como soma dos preços selecionados; congelar preço unitário nos itens enviados após a criação da OS.
- [x] 1.7 Definir GET `/ordem_servico`, POST `/ordem_servico` e PATCH `/ordem_servico/{id}/status`.
- [x] 1.8 Manter autorização sob configuração existente do Xano; não criar política de perfil nesta Change.

## 2. Backend e persistência Xano

- [ ] 2.1 Criar ou ajustar persistência da OS e associação relacional com serviços.
- [ ] 2.2 Implementar abertura com IDs de cliente, veículo e um ou mais serviços.
- [ ] 2.3 Validar existência das referências e consistência entre cliente e proprietário do veículo.
- [ ] 2.4 Implementar listagem de OS com dados ou IDs necessários para apresentar cliente, veículo e serviços.
- [ ] 2.5 Implementar atualização de status com validação da matriz de transições.
- [ ] 2.6 Cobrir persistência, referências inválidas, status e regras aprovadas com testes no Xano.

## 3. Cliente REST e interface Streamlit

- [x] 3.1 Adicionar ao `XanoClient` métodos `list_ordens_servico`, `criar_ordem_servico` e `update_ordem_servico_status`.
- [x] 3.2 Adicionar “Ordens de Serviço” à navegação do Streamlit preservando os cadastros existentes.
- [x] 3.3 Implementar seleção de cliente, veículo pertencente ao cliente e um ou mais serviços.
- [x] 3.4 Implementar abertura sem previsão, calculando o total no Streamlit e enviando status, total e observações.
- [x] 3.5 Persistir cada item via `/item_ordem_servico` e listar OS com cliente, veículo, itens, preços unitários e total.
- [x] 3.6 Permitir transições aprovadas e exibir sucesso somente após resposta bem-sucedida da API.
- [x] 3.7 Apresentar estados vazios, falhas e validações sem indicar persistência incorretamente.

## 4. Validação

- [x] 4.1 Testar GET/POST/PATCH e serialização de payloads do cliente REST com mocks.
- [x] 4.2 Testar abertura, previsões, vínculos, listagem, transições e falhas com `AppTest` e mocks.
- [ ] 4.3 Validar integração real, regras no backend e todos os requisitos antes do Archive.
