# Design — Ordens de Serviço

## Contexto

As specs ativas definem clientes e veículos com vínculo proprietário-veículo e um catálogo de serviços com IDs, preço em BRL e tempo opcional em minutos. O Xano é fonte de verdade para dados e validações; o app Streamlit usa um `XanoClient` com endpoints singulares por recurso. O modelo de domínio define OS/agendamento como um atendimento de veículo com cliente, serviços, datas, status, valor total e observações. Uma decisão anterior definiu que agendamento e OS compartilharão uma estrutura base que evolui por status.

## Objetivos


## Não objetivos


## Decisões aprovadas e dependências do Apply
- Aprovados: ciclo de status, cancelamento, abertura automática, previsão automática/manual, congelamento do preço unitário, total como soma dos itens e rotas GET/POST/PATCH.
- O contrato de payload documentado acima precisa ser implementado no grupo Xano; esta sessão altera apenas o Streamlit e o cliente REST local, sem acesso ao editor de schema/functions do Xano.
- A autorização continua seguindo a configuração existente do Xano; esta Change não cria autenticação ou perfis novos.
- Datas de entrada/conclusão e edição de uma OS aberta permanecem fora desta entrega.
Os status válidos são `Aguardando`, `Em Andamento`, `Concluído`, `Entregue` e `Cancelado`. As únicas transições de avanço são sequenciais: `Aguardando` → `Em Andamento` → `Concluído` → `Entregue`. É permitido cancelar a partir de qualquer status não cancelado; `Cancelado` é terminal, inclusive não pode ser reaberto.

- Calcular o valor total localmente pela soma dos preços dos serviços selecionados; a previsão de entrega não faz parte do formulário desta entrega.
- Apresentar a listagem com ID, cliente, veículo, serviços, status e data/hora agendada quando disponível.
- Oferecer ação para atualizar status; a UI só mostra sucesso após a API confirmar a mudança.
Cobrir criação, snapshots e soma, previsão automática/manual, falta de duração, vínculos, listagem, transições e falha de API com testes REST unitários e `AppTest`. A integração real requer que o contrato documentado seja implementado no Xano.
A seleção em cascata melhora a experiência, mas não substitui a validação do vínculo no Xano. A listagem pode usar uma resposta já expandida do Xano ou resolver os IDs contra os cadastros existentes; o contrato deve escolher um formato consistente.

## Integração Xano proposta

O contrato aprovado usa `GET /ordem_servico`, `POST /ordem_servico` e `PATCH /ordem_servico/{id}/status` com o campo `status`.

O payload de abertura usado pelo Streamlit contém `cliente_id`, `veiculo_id`, `status`, `valor_total` e `observacoes`. O método `criar_ordem_servico` envia esse payload em `POST /ordem_servico`, extrai o ID retornado e envia cada item em `POST /item_ordem_servico` com `ordem_servico_id`, `servico_id` e `preco_unitario`. A listagem usa `itens_servico` com preços congelados quando retornados pelo backend.

## Decisões necessárias antes do Apply

- Resolver a divergência do ciclo de status: o overview lista `Aguardando`, `Em Execução`, `Pronto`, `Entregue`; o domínio lista `Aguardando`, `Em Execução`, `Aguardando Retirada`, `Entregue`, `Cancelado`. Definir vocabulário canônico, significado de `Pronto` versus `Aguardando Retirada`, inclusão de `Cancelado` e matriz de transições.
- Definir se data/hora agendada é obrigatória nesta Change, e quando são preenchidas as datas de entrada e conclusão.
- Definir quais campos são editáveis após abertura e quais observações podem ser atualizadas.
- Confirmar o modo de persistir vários serviços por OS e se serviço pode aparecer mais de uma vez.
- Definir `valor_total`: soma dos preços base, valor informado, descontos ou outra regra. Decidir snapshots de preço/duração no momento da abertura.
- Confirmar endpoints, método de atualização de status, payload e formato de listagem no Xano.
- Definir quais perfis podem abrir OS e alterar status. A autorização do Xano deve permanecer autoridade final.

## Riscos e dependências

- Status conflitantes podem criar estados impossíveis ou inconsistentes entre API, UI e operação.
- Sem snapshot de preço, alteração posterior de preço base pode tornar ambíguo o valor histórico da OS.
- A associação entre várias entidades depende de IDs estáveis e validação no Xano; validar apenas no Streamlit permitiria vínculos inválidos por outras origens.
- Cálculo de `valor_total` e regras de agenda podem aumentar o escopo se forem decididos sem delimitação.

## Verificação

Cobrir criação com vínculos válidos e inválidos, veículo de outro proprietário, múltiplos serviços, listagem vazia/cheia, transição permitida e proibida, falha de API e ausência de falso sucesso. Usar testes REST unitários e `AppTest` com chamadas simuladas; validar o contrato remoto no ambiente Xano durante o Apply.
