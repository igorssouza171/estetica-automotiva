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

O frontend reutiliza o cliente REST existente. As únicas operações desta Change são `GET /servico` para listar e `POST /servico` para cadastrar. O payload usa `nome`, `preco_base`, `descricao`, `tempo_estimado_min` e `categoria`; os campos opcionais ausentes não devem ser enviados. O preço será enviado como número JSON arredondado a duas casas, e `tempo_estimado_min` como inteiro em minutos. A API deve retornar IDs estáveis para diferenciar registros com nomes iguais. O shape exato das respostas deve permanecer compatível com o comportamento do Xano e o adaptador de listagem já usado no projeto.

A interface adiciona a área de catálogo à navegação já existente e utiliza formulários Streamlit para criação/edição e apresentação dos registros. Não são necessárias novas bibliotecas além das dependências já declaradas pelo projeto.

## Decisões aprovadas e pendências

- Decididos: nome e preço base obrigatórios; BRL com duas casas decimais; tempo armazenado em minutos; categoria como texto simples; nomes duplicados permitidos com identidade por ID; `GET /servico` e `POST /servico`.
- Antes de Apply, confirmar os nomes reais das colunas Xano e o formato da resposta de `POST /servico`, em especial a representação de `preco_base` e o retorno do ID.
- A política de autorização segue a configuração atual do Xano e do app; a Change não cria perfis ou autenticação nova.
- Atualização e ciclo de vida dos serviços não fazem parte desta Change.

## Riscos e dependências

- Alterar o preço base sem snapshot futuro pode modificar a interpretação de atendimentos passados; snapshots pertencem ao desenho de OS, mas precisam ser considerados ao definir o contrato do catálogo.
- Divergência entre nomes de colunas e payloads Xano pode exigir ajuste do adaptador.
- Sem um ciclo de vida definido, a remoção de um serviço que venha a ser referenciado por uma OS pode causar inconsistência; por isso exclusão não está incluída.
- A relação serviço-insumo é prevista no modelo conceitual, mas depende de regras de consumo ainda não aprovadas e fica fora desta Change.

## Verificação

Cobrir no backend e na interface os cenários da especificação: cadastro, nomes duplicados, consulta, catálogo vazio, rejeição de campos obrigatórios ausentes e falha da API. Testes Streamlit devem usar `AppTest` e chamadas HTTP simuladas; testar a integração remota requer endpoint e acesso Xano disponíveis.
