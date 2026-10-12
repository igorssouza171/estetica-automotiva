# Tarefas — Cadastro de Clientes e Veículos

> Estado do Archive: o usuário confirmou que a integração e os cadastros estão funcionando. As tarefas de integração com o Xano são consideradas concluídas com base nessa confirmação; esta sessão não acessou o workspace Xano para repetir testes remotos. Os critérios de duplicidade, formato e normalização além dos campos obrigatórios foram explicitamente mantidos fora do escopo.

## 1. Decisões e contratos

- [x] 1.1 Confirmar a tecnologia de frontend: Streamlit.
- [x] 1.2 Definir campos obrigatórios: nome e telefone para Cliente; placa e modelo para Veículo. Os demais atributos conceituais são opcionais; regras adicionais de formato e normalização ficam fora desta Change.
- [x] 1.3 Manter regras de duplicidade para CPF/CNPJ e placa fora do escopo desta Change.
- [x] 1.4 Confirmar que transferência de propriedade, histórico de proprietários e exclusão/arquivamento ficam fora desta Change.
- [x] 1.5 Integração via Bearer token confirmada como funcional pelo usuário; gestão de usuários e permissões por perfil permanecem fora do escopo.

## 2. Backend e persistência no Xano

- [x] 2.1 Criar a estrutura de persistência para Cliente e Veículo com os atributos aprovados (conclusão confirmada pelo usuário).
- [x] 2.2 Implementar a referência obrigatória de Veículo para Cliente e a integridade do relacionamento no backend (conclusão confirmada pelo usuário).
- [x] 2.3 Implementar operações REST de cadastro e consulta de clientes (conclusão confirmada pelo usuário).
- [x] 2.4 Implementar operações REST de cadastro e consulta de veículos, incluindo o proprietário associado (conclusão confirmada pelo usuário).
- [x] 2.5 Implementar consulta dos veículos associados a um cliente (conclusão confirmada pelo usuário).
- [x] 2.6 Verificar validações e integridade do vínculo no fluxo funcional confirmado pelo usuário; testes locais cobrem o contrato HTTP do cliente.

## 3. Interface

- [x] 3.1 Implementar os fluxos de cadastro e consulta de clientes no frontend Streamlit.
- [x] 3.2 Implementar os fluxos de cadastro e consulta de veículos, permitindo selecionar um cliente existente.
- [x] 3.3 Apresentar o vínculo de proprietário nas consultas de veículo e de veículos por cliente.
- [x] 3.4 Apresentar erros de validação, falhas de API e estados sem registros sem indicar persistência incorretamente.

## 4. Validação da Change

- [x] 4.1 Verificar os cenários de cadastro, consulta, validação e integridade descritos na especificação (conclusão do fluxo confirmada pelo usuário; testes locais cobrem chamadas HTTP e interface simulada).
- [x] 4.2 Confirmar que a interface consome a API e não substitui as validações críticas do backend.
- [x] 4.3 Confirmar que todos os requisitos desta Change foram atendidos antes do Archive, com base na confirmação do usuário e nos testes locais.
