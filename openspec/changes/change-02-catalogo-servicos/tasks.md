# Tarefas — Catálogo de Serviços

## 1. Decisões e contrato

- [x] 1.1 Definir nome e preço base como obrigatórios; descrição, tempo estimado e categoria como opcionais.
- [x] 1.2 Definir preço em BRL com duas casas decimais.
- [x] 1.3 Definir tempo estimado armazenado em minutos.
- [x] 1.4 Definir categoria como texto simples.
- [x] 1.5 Permitir nomes duplicados e usar ID como identidade; manter atualização e ciclo de vida fora do escopo.
- [x] 1.6 Definir `GET /servico` para listagem e `POST /servico` para cadastro.
- [ ] 1.7 Confirmar os nomes de campos, schema e formato de resposta no ambiente Xano.

## 2. Backend e persistência no Xano

- [ ] 2.1 Confirmar que a tabela Xano contém os campos aprovados e a precisão decimal necessária.
- [ ] 2.2 Confirmar que `GET /servico` lista serviços e que `POST /servico` cadastra e retorna o ID.
- [ ] 2.3 Validar no Xano obrigatoriedade de nome/preço, duas casas decimais e ausência de unicidade por nome.
- [ ] 2.4 Confirmar que os endpoints respeitam a política de acesso configurada no ambiente Xano.

## 3. Cliente REST e interface Streamlit

- [x] 3.1 Adicionar ao cliente Xano métodos `list_servicos` e `create_servico` para GET/POST `/servico`.
- [x] 3.2 Incluir a área de catálogo na navegação do Streamlit preservando os fluxos de clientes e veículos.
- [x] 3.3 Implementar formulário de cadastro e apresentação/consulta da lista de serviços.
- [x] 3.4 Apresentar preço em BRL com duas casas decimais e tempo estimado em minutos.
- [x] 3.5 Apresentar estados sem registros, sucesso, validação e falha da API sem afirmar persistência quando a gravação falhar.

## 4. Validação

- [x] 4.1 Testar as operações GET/POST do cliente REST para `/servico` com chamadas simuladas.
- [x] 4.2 Testar os cenários de cadastro, nomes duplicados permitidos, consulta, catálogo vazio, campos obrigatórios ausentes e falha de API com `AppTest` e mock.
- [ ] 4.3 Confirmar que as regras de domínio permanecem no backend e que os requisitos estão atendidos antes do Archive.
