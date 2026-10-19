# Tarefas — Catálogo de Serviços

## 1. Decisões e contrato

- [x] 1.1 Definir nome e preço base como obrigatórios; descrição, tempo estimado e categoria como opcionais.
- [x] 1.2 Definir preço em BRL com duas casas decimais.
- [x] 1.3 Definir tempo estimado armazenado em minutos.
- [x] 1.4 Definir categoria como texto simples.
- [x] 1.5 Permitir nomes duplicados e usar ID como identidade; manter atualização e ciclo de vida fora do escopo.
- [x] 1.6 Definir `GET /servico` para listagem e `POST /servico` para cadastro.
- [x] 1.7 Confirmar o campo Xano `tempo_estimado_min` e o funcionamento da integração (confirmação do usuário).

## 2. Backend e persistência no Xano

- [x] 2.1 Confirmar que a persistência Xano atende aos campos aprovados e à precisão decimal necessária (confirmação do usuário).
- [x] 2.2 Confirmar que `GET /servico` lista serviços e que `POST /servico` cadastra (integração testada pelo usuário).
- [x] 2.3 Confirmar obrigatoriedade, precisão e nomes duplicados permitidos no fluxo validado pelo usuário.
- [x] 2.4 Confirmar integração autenticada conforme configuração existente; autorização por perfil permanece fora desta Change.

## 3. Cliente REST e interface Streamlit

- [x] 3.1 Adicionar ao cliente Xano métodos `list_servicos` e `create_servico` para GET/POST `/servico`.
- [x] 3.2 Incluir a área de catálogo na navegação do Streamlit preservando os fluxos de clientes e veículos.
- [x] 3.3 Implementar formulário de cadastro e apresentação/consulta da lista de serviços.
- [x] 3.4 Apresentar preço em BRL com duas casas decimais e tempo estimado em minutos.
- [x] 3.5 Apresentar estados sem registros, sucesso, validação e falha da API sem afirmar persistência quando a gravação falhar.

## 4. Validação

- [x] 4.1 Testar as operações GET/POST do cliente REST para `/servico` com chamadas simuladas.
- [x] 4.2 Testar os cenários de cadastro, nomes duplicados permitidos, consulta, catálogo vazio, campos obrigatórios ausentes e falha de API com `AppTest` e mock.
- [x] 4.3 Confirmar que os requisitos foram atendidos com os testes locais aprovados e a integração Xano confirmada pelo usuário; as regras críticas permanecem no backend.
