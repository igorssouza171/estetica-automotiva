# Domain Model — Sistema de Administração para Estética Automotiva

Este documento descreve os principais conceitos e entidades do domínio da estética automotiva e suas relações conceituais.

## 1. Cliente
Representa a pessoa física ou jurídica proprietária dos veículos atendidos na estética.
- **Atributos Conceituais:** Nome (obrigatório), Telefone/WhatsApp (obrigatório), CPF/CNPJ, E-mail, Endereço.
- **Relacionamentos:** Um cliente pode possuir um ou mais *Veículos*. Um cliente pode ter várias *Ordens de Serviço*.

## 2. Veículo
Representa o automóvel cadastrado no sistema para realização dos serviços.
- **Atributos Conceituais:** Placa (obrigatória), Marca, Modelo (obrigatório), Ano, Cor, Categoria (Hatch, Sedã, SUV, Picape, Esportivo).
- **Relacionamentos:** Pertence a um único *Cliente*. Pode estar associado a várias *Ordens de Serviço*.

## 3. Serviço
Representa os tipos de procedimentos oferecidos pelo estabelecimento.
- **Atributos Conceituais:** Nome do serviço (obrigatório), Descrição, Preço Base (obrigatório, em Real/BRL com duas casas decimais), Tempo Estimado (opcional, em minutos), Categoria (opcional, texto simples).
- **Identificação:** Cada serviço é identificado pelo seu ID; nomes duplicados são permitidos.
- **Relacionamentos:** Um serviço pode estar presente em várias *Ordens de Serviço*. Pode consumir um ou mais *Produtos/Insumos*.

## 4. Ordem de Serviço (OS) / Agendamento
Representa o atendimento de um veículo em uma estrutura compartilhada com o agendamento e evolui por status.
- **Atributos Conceituais:** Data/Hora de Abertura (gerada automaticamente), Previsão de Entrega (calculada pela soma dos tempos dos serviços ou informada manualmente), Data/Hora de Entrada, Data/Hora de Conclusão, Status (`Aguardando`, `Em Andamento`, `Concluído`, `Entregue`, `Cancelado`), Valor Total (soma dos itens), Observações sobre o Estado do Veículo.
- **Transições:** Avanço sequencial de `Aguardando` para `Em Andamento`, depois `Concluído` e `Entregue`; pode ser cancelada a partir de qualquer status não cancelado. `Cancelado` é terminal.
- **Relacionamentos:**
  - Pertence a um *Cliente* e a um *Veículo*.
  - Contém um ou mais itens de serviço identificados por *Serviço* e com preço unitário congelado no momento da abertura.
  - Registrada/atualizada por um *Usuário* do sistema.

## 5. Produto / Insumo (Estoque)
Representa os materiais de consumo utilizados nos serviços (ex: Shampoos, Ceras, Compostos Polidores, Boinas).
- **Atributos Conceituais:** Nome do Produto, Marca, Unidade de Medida (ml, L, unidade), Quantidade em Estoque, Estoque Mínimo.
- **Relacionamentos:** Pode estar vinculado ao consumo de *Serviços*.

## 6. Usuário / Funcional
Representa os colaboradores que acessam o sistema.
- **Atributos Conceituais:** Nome, E-mail, Perfil (`Administrador`, `Atendente`, `Operador`).
- **Relacionamentos:** Responsável pela criação ou alteração de status de *Ordens de Serviço*.