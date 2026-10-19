# Design — Catálogo de Serviços

## Contexto

O domínio define Serviço pelos atributos nome, descrição, preço base, tempo estimado e categoria, e prevê que serviços possam ser selecionados em várias ordens de serviço e consumir produtos. O projeto usa Streamlit no frontend e Xano com API REST para persistência e regras de negócio. A Change 01 estabeleceu no app o padrão de consumo de endpoints Xano singulares por recurso.

## Objetivos

- Manter o catálogo no Xano como fonte de verdade.
- Permitir cadastro e consulta de serviços no app Streamlit existente.
- Manter validações críticas no backend e comunicar claramente sucesso e falha no frontend.
- Deixar explícitas as decisões de domínio necessárias antes do Apply.

## Não objetivos

- Associar serviços a OS/agendamentos ou guardar snapshots de preço e duração nas linhas de atendimento.
- Configurar consumo de estoque por serviço.
- Implementar atualização, exclusão, arquivamento ou estados ativo/inativo.
- Implementar autenticação, gestão de colaboradores ou permissões por perfil.

## Modelo conceitual

Um serviço contém nome, descrição, preço base, tempo estimado e categoria. Nome e preço base são obrigatórios. O preço base é em BRL com duas casas decimais. O tempo estimado, quando informado, é armazenado em minutos. A categoria, quando informada, é texto simples. Nomes duplicados são permitidos; cada registro é identificado por ID. Descrição, tempo e categoria são opcionais nesta Change.

Atualização de serviços não faz parte desta Change. Antes de implementar OS, deve-se decidir se preço e duração são copiados para o atendimento no momento da contratação.

## Integração proposta

O frontend reutiliza o cliente REST existente. As únicas operações desta Change são `GET /servico` para listar e `POST /servico` para cadastrar. O payload usa `nome`, `preco_base`, `descricao`, `tempo_estimado_min` e `categoria`; os campos opcionais ausentes não são enviados. O preço é enviado como número JSON arredondado a duas casas, e `tempo_estimado_min` como inteiro em minutos. O Xano retorna IDs para diferenciar registros com nomes iguais. O usuário confirmou que a integração do catálogo e o mapeamento de `tempo_estimado_min` foram testados e funcionam.

A interface adiciona a área de catálogo à navegação já existente e utiliza formulários Streamlit para criação/edição e apresentação dos registros. Não são necessárias novas bibliotecas além das dependências já declaradas pelo projeto.

## Decisões aprovadas e resultado

- Decididos e aplicados: nome e preço base obrigatórios; BRL com duas casas decimais; tempo armazenado em minutos no campo Xano `tempo_estimado_min`; categoria como texto simples; nomes duplicados permitidos com identidade por ID; `GET /servico` e `POST /servico`.
- A integração real e o mapeamento do campo de tempo foram confirmados como testados pelo usuário. Os testes locais desta Change também passaram.
- A autorização continua seguindo a configuração existente do Xano; a Change não adiciona perfis ou mecanismo de autenticação novo.
- Atualização e ciclo de vida dos serviços permanecem fora do escopo.

## Riscos e dependências

- Alterar o preço base sem snapshot futuro pode modificar a interpretação de atendimentos passados; snapshots pertencem ao desenho de OS, mas precisam ser considerados ao definir o contrato do catálogo.
- Mudanças futuras no schema ou payload Xano exigirão alinhamento do adaptador e da spec ativa.
- Sem um ciclo de vida definido, a remoção de um serviço que venha a ser referenciado por uma OS pode causar inconsistência; por isso exclusão não está incluída.
- A relação serviço-insumo é prevista no modelo conceitual, mas depende de regras de consumo ainda não aprovadas e fica fora desta Change.

## Verificação

Os cenários de cadastro, nomes duplicados, consulta, catálogo vazio, rejeição de campos obrigatórios e falha da API foram cobertos por testes locais; o usuário confirmou a integração remota. A suíte local executada no Archive passou com 15 testes.
