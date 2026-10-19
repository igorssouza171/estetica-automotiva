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
Representa o registro do atendimento de um veículo específico em uma data e horário determinados.
- **Atributos Conceituais:** Data/Hora Agendada, Data/Hora de Entrada, Data/Hora de Conclusão, Status (`Aguardando`, `Em Execução`, `Aguardando Retirada`, `Entregue`, `Cancelado`), Valor Total, Observações sobre o Estado do Veículo.
- **Relacionamentos:**
  - Pertence a um *Cliente* e a um *Veículo*.
  - Contém um ou mais *Serviços*.
  - Registrada/atualizada por um *Usuário* do sistema.

## 5. Produto / Insumo (Estoque)
Representa os materiais de consumo utilizados nos serviços (ex: Shampoos, Ceras, Compostos Polidores, Boinas).
- **Atributos Conceituais:** Nome do Produto, Marca, Unidade de Medida (ml, L, unidade), Quantidade em Estoque, Estoque Mínimo.
- **Relacionamentos:** Pode estar vinculado ao consumo de *Serviços*.

## 6. Usuário / Funcional
Representa os colaboradores que acessam o sistema.
- **Atributos Conceituais:** Nome, E-mail, Perfil (`Administrador`, `Atendente`, `Operador`).
- **Relacionamentos:** Responsável pela criação ou alteração de status de *Ordens de Serviço*.