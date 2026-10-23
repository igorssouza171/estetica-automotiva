# Project Overview — Sistema de Administração para Estética Automotiva

## 1. Visão Geral
O projeto consiste em uma plataforma web de gestão voltada para estéticas automotivas, oficinas de detalhamento (detailing) e lava-rápidos especializados. O sistema centraliza o agendamento de serviços, o acompanhamento do status do veículo em tempo real e a gestão básica de clientes e estoque.

## 2. Problema
Muitas estéticas automotivas gerenciam agendamentos e ordens de serviço (OS) de forma manual (papel ou WhatsApp), gerando conflitos de horários, falta de histórico dos veículos dos clientes e descontrole no uso de produtos químicos de alto custo (como ceras e vitrificadores).

## 3. Objetivos
- Digitalizar o fluxo de atendimento desde o agendamento até a entrega do veículo.
- Permitir ao gestor/atendente emitir Ordens de Serviço (OS) com status atualizados.
- Manter histórico centralizado de clientes, veículos e serviços prestados.
- Fornecer controle básico de insumos/estoque consumidos nos serviços.

## 4. Público-Alvo / Usuários
- **Administrador/Gerente:** Visualiza relatórios, gerencia catálogo de serviços e estoque.
- **Atendente/Recepcionista:** Realiza agendamentos, cadastra clientes/veículos e abre Ordens de Serviço.
- **Detalhador/Operador:** Atualiza o status da execução do serviço no veículo (ex: "Em lavagem", "Em polimento", "Pronto").

## 5. Escopo Inicial
- Cadastro e consulta de Clientes e Veículos.
- Catálogo de Serviços com preços e tempo médio de execução.
- Agendamento de Horários e Gestão de Ordens de Serviço (OS).
- Controle simples de Estoque de Produtos.

## 6. Principais Funcionalidades
- **Gestão de Clientes e Veículos:** Associação de múltiplos veículos a um mesmo cliente (modelo, marca, placa, cor).
- **Gestão de Serviços:** Cadastro de procedimentos (Lavagem Detalhada, Polimento Técnico, Higienização Interna, Vitrificação).
- **Abertura e Status de OS:** Criação de OS associada ao cliente, veículo e serviços, com avanço sequencial de status (`Aguardando`, `Em Andamento`, `Concluído`, `Entregue`) ou cancelamento.
- **Agendamento:** Agenda visual de horários dos serviços.
- **Controle de Insumos:** Baixa de estoque associada ao uso nos serviços.

## 7. Requisitos e Restrições Importantes
- Interface intuitiva para uso rápido no balcão de atendimento.
- Regras de negócio e validações devem ser centralizadas no backend.
- O idioma oficial dos artefatos do projeto e interface é o Português do Brasil (pt-BR).

## 8. Arquitetura Tecnológica
- **Backend:** Xano (Backend-as-a-Service) com XanoScript / REST APIs.
- **Frontend:** Streamlit (Python).
- **Banco de Dados:** Estrutura relacional mantida no Xano.
- **Controle de Versão:** Git + GitHub.

## 9. Princípios de Desenvolvimento
- Desenvolvimento incremental guiado pelo OpenSpec (Propose → Review → Apply → Archive).
- Código limpo, modular e com responsabilidades bem separadas.