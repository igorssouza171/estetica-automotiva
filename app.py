"""Interface Streamlit para cadastro e consulta de clientes, veículos e serviços."""

from __future__ import annotations

import os
import time
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

import streamlit as st

from xano_client import XanoAPIError, XanoClient


st.set_page_config(page_title="Clientes, veículos e serviços", page_icon="🚘", layout="wide")
st.title("Clientes, veículos e serviços")
st.caption("Cadastro e consulta integrados à API do Xano")

base_url = os.getenv("XANO_API_BASE_URL", "").strip()
token = os.getenv("XANO_API_TOKEN", "").strip()
if not base_url or not token:
    st.error(
        "Configure XANO_API_BASE_URL e XANO_API_TOKEN no ambiente antes de usar os cadastros. "
        "A API deve estar protegida e aceitar autenticação Bearer."
    )
    st.stop()

client = XanoClient(base_url, token)
section = st.sidebar.radio("Cadastro", ("Clientes", "Veículos", "Serviços", "Ordens de Serviço"))

STATUS_OS_SEQUENCIA = ("Aguardando", "Em Andamento", "Concluído", "Entregue")
STATUS_OS_CANCELADO = "Cancelado"
SESSION_CACHE_TTL_SECONDS = 60
SPINNER_XANO = "Processando informações no Xano..."


def session_cached_xano_data(key: str, fetch_data: Any) -> Any:
    cache_key = f"xano_session_{key}"
    cached = st.session_state.get(cache_key)
    if (
        isinstance(cached, dict)
        and time.monotonic() - cached["loaded_at"] < SESSION_CACHE_TTL_SECONDS
    ):
        return cached["data"]

    with st.spinner(SPINNER_XANO):
        data = fetch_data()
    st.session_state[cache_key] = {"data": data, "loaded_at": time.monotonic()}
    return data


def invalidate_session_xano_data(key: str) -> None:
    st.session_state.pop(f"xano_session_{key}", None)


def limpar_selecao_veiculo_os() -> None:
    st.session_state["os_veiculo"] = None


def optional_text(label: str, key: str) -> str | None:
    value = st.text_input(label, key=key).strip()
    return value or None


def show_error(error: Exception) -> None:
    st.error(str(error))


def show_records(records: list[dict[str, Any]], columns: dict[str, str]) -> None:
    if not records:
        st.info("Nenhum registro encontrado.")
        return
    st.dataframe(
        [{label: record.get(field) for field, label in columns.items()} for record in records],
        hide_index=True,
        width="stretch",
    )


def format_brl(value: Any) -> str:
    if value is None:
        return ""
    try:
        amount = Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return str(value)
    formatted = f"{amount:,.2f}".translate(str.maketrans({",": ".", ".": ","}))
    return f"R$ {formatted}"


def format_datetime(value: Any) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, datetime):
        timestamp = value
    else:
        try:
            timestamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return str(value)
    return timestamp.strftime("%d/%m/%Y %H:%M")


def transicoes_os_permitidas(status_atual: str) -> list[str]:
    if status_atual == STATUS_OS_CANCELADO:
        return []
    try:
        indice = STATUS_OS_SEQUENCIA.index(status_atual)
    except ValueError:
        return [STATUS_OS_CANCELADO]
    proximos = list(STATUS_OS_SEQUENCIA[indice + 1 : indice + 2])
    proximos.append(STATUS_OS_CANCELADO)
    return proximos


if section == "Clientes":
    form_column, list_column = st.columns((1, 1.5), gap="large")
    with form_column:
        st.subheader("Novo cliente")
        with st.form("novo_cliente", clear_on_submit=True):
            nome = st.text_input("Nome *")
            telefone = st.text_input("Telefone *")
            cpf_cnpj = optional_text("CPF/CNPJ", "cliente_cpf_cnpj")
            email = optional_text("E-mail", "cliente_email")
            endereco = optional_text("Endereço", "cliente_endereco")
            submitted = st.form_submit_button("Cadastrar cliente", type="primary")

        if submitted:
            payload = {"nome": nome.strip(), "telefone": telefone.strip()}
            payload.update(
                {
                    key: value
                    for key, value in {
                        "cpf_cnpj": cpf_cnpj,
                        "email": email,
                        "endereco": endereco,
                    }.items()
                    if value is not None
                }
            )
            if not payload["nome"] or not payload["telefone"]:
                st.warning("Nome e telefone são obrigatórios.")
            else:
                try:
                    with st.spinner(SPINNER_XANO):
                        client.create_cliente(payload)
                    invalidate_session_xano_data("clientes")
                    st.success("Cliente cadastrado.")
                    st.rerun()
                except XanoAPIError as error:
                    show_error(error)

    with list_column:
        st.subheader("Clientes cadastrados")
        try:
            clientes = session_cached_xano_data("clientes", client.list_clientes)
            show_records(
                clientes,
                {
                    "id": "ID",
                    "nome": "Nome",
                    "telefone": "Telefone",
                    "cpf_cnpj": "CPF/CNPJ",
                    "email": "E-mail",
                    "endereco": "Endereço",
                },
            )
        except XanoAPIError as error:
            show_error(error)

elif section == "Serviços":
    form_column, list_column = st.columns((1, 1.5), gap="large")
    with form_column:
        st.subheader("Novo serviço")
        if st.session_state.pop("servico_criado", False):
            st.success("Serviço cadastrado.")
        with st.form("novo_servico", clear_on_submit=True):
            nome = st.text_input("Nome *", key="servico_nome")
            preco_base = st.number_input(
                "Preço base (R$) *",
                value=None,
                step=0.01,
                format="%.2f",
                required=True,
                key="servico_preco_base",
            )
            descricao = st.text_area("Descrição", key="servico_descricao")
            tempo_estimado_min = st.number_input(
                "Tempo estimado (minutos)",
                value=None,
                step=1,
                format="%d",
                key="servico_tempo_estimado_min",
            )
            categoria = st.text_input("Categoria", key="servico_categoria")
            submitted = st.form_submit_button(
                "Cadastrar serviço",
                type="primary",
                key="create_servico",
            )

        if submitted:
            if not nome.strip():
                st.warning("Nome é obrigatório.")
            elif preco_base is None:
                st.warning("Preço base é obrigatório.")
            else:
                try:
                    preco_decimal = Decimal(str(preco_base))
                    preco_centavos = preco_decimal.quantize(Decimal("0.01"))
                except (InvalidOperation, ValueError):
                    st.warning("Informe um preço base válido em reais.")
                else:
                    if preco_decimal != preco_centavos:
                        st.warning("Informe o preço base com no máximo duas casas decimais.")
                    else:
                        payload: dict[str, Any] = {
                            "nome": nome.strip(),
                            "preco_base": float(preco_centavos),
                        }
                        if descricao.strip():
                            payload["descricao"] = descricao.strip()
                        if tempo_estimado_min is not None:
                            payload["tempo_estimado_min"] = int(tempo_estimado_min)
                        if categoria.strip():
                            payload["categoria"] = categoria.strip()

                        try:
                            with st.spinner(SPINNER_XANO):
                                client.create_servico(payload)
                            invalidate_session_xano_data("servicos")
                            st.session_state["servico_criado"] = True
                            st.rerun()
                        except XanoAPIError as error:
                            show_error(error)

    with list_column:
        st.subheader("Serviços cadastrados")
        try:
            servicos = session_cached_xano_data("servicos", client.list_servicos)
            registros = [
                {
                    "id": servico.get("id"),
                    "nome": servico.get("nome"),
                    "descricao": servico.get("descricao"),
                    "preco_base": format_brl(servico.get("preco_base")),
                    "tempo_estimado_min": servico.get("tempo_estimado_min"),
                    "categoria": servico.get("categoria"),
                }
                for servico in servicos
            ]
            show_records(
                registros,
                {
                    "id": "ID",
                    "nome": "Nome",
                    "descricao": "Descrição",
                    "preco_base": "Preço base",
                    "tempo_estimado_min": "Tempo (minutos)",
                    "categoria": "Categoria",
                },
            )
        except XanoAPIError as error:
            show_error(error)

elif section == "Ordens de Serviço":
    if st.session_state.pop("ordem_servico_criada", False):
        st.success("Ordem de Serviço aberta.")
    status_atualizado = st.session_state.pop("ordem_servico_status_atualizado", None)
    if status_atualizado:
        st.success(f"Status da O.S. {status_atualizado[0]} atualizado para {status_atualizado[1]}.")

    os_data_loaded = True
    try:
        clientes_os = session_cached_xano_data("clientes", client.list_clientes)
        servicos_os = session_cached_xano_data("servicos", client.list_servicos)
        with st.spinner(SPINNER_XANO):
            ordens_servico = client.list_ordens_servico()
    except XanoAPIError as error:
        os_data_loaded = False
        clientes_os = []
        servicos_os = []
        ordens_servico = []
        st.error(f"Não foi possível carregar as Ordens de Serviço e seus cadastros: {error}")

    clientes_por_opcao_os = {
        f"{cliente.get('nome', 'Cliente sem nome')} · ID {cliente.get('id')}": cliente
        for cliente in clientes_os
        if cliente.get("id") is not None
    }
    servicos_por_opcao_os = {
        f"{servico.get('nome', 'Serviço sem nome')} · ID {servico.get('id')}": servico
        for servico in servicos_os
        if servico.get("id") is not None
    }

    form_column, list_column = st.columns((1, 1.5), gap="large")
    with form_column:
        st.subheader("Abrir O.S.")
        cliente_opcao_os = st.selectbox(
            "Cliente *",
            tuple(clientes_por_opcao_os),
            index=None,
            key="os_cliente",
            on_change=limpar_selecao_veiculo_os,
        )
        cliente_selecionado_os = clientes_por_opcao_os.get(cliente_opcao_os)
        veiculos_cliente_os = []
        erro_veiculos_os = None
        if cliente_selecionado_os:
            cliente_selecionado_id = cliente_selecionado_os["id"]
            try:
                with st.spinner(SPINNER_XANO):
                    veiculos_retornados = client.list_veiculos(cliente_selecionado_id)
                veiculos_cliente_os = [
                    veiculo
                    for veiculo in veiculos_retornados
                    if veiculo.get("cliente_id") == cliente_selecionado_id
                ]
            except XanoAPIError as error:
                erro_veiculos_os = error
                st.error(f"Não foi possível carregar os veículos deste cliente: {error}")
        veiculos_por_opcao_os = {
            f"{veiculo.get('placa', 'Sem placa')} · {veiculo.get('modelo', '')} · ID {veiculo.get('id')}": veiculo
            for veiculo in veiculos_cliente_os
            if veiculo.get("id") is not None
        }
        veiculo_opcao_os = st.selectbox(
            "Veículo *",
            tuple(veiculos_por_opcao_os),
            index=None,
            key="os_veiculo",
            disabled=not cliente_selecionado_os or erro_veiculos_os is not None,
        )
        with st.form("abrir_ordem_servico", clear_on_submit=True):
            servicos_selecionados_os = st.multiselect(
                "Serviços *",
                tuple(servicos_por_opcao_os),
                key="os_servicos",
            )
            observacoes_os = st.text_area("Observações sobre o veículo", key="os_observacoes")
            submitted_os = st.form_submit_button(
                "Abrir O.S.",
                type="primary",
                key="create_ordem_servico",
            )

        if submitted_os:
            veiculo_selecionado_os = veiculos_por_opcao_os.get(veiculo_opcao_os)
            servicos_selecionados = [
                servicos_por_opcao_os[opcao]
                for opcao in servicos_selecionados_os
                if opcao in servicos_por_opcao_os
            ]
            if not cliente_selecionado_os:
                st.warning("Selecione um cliente.")
            elif not veiculo_selecionado_os:
                st.warning("Selecione um veículo pertencente ao cliente.")
            elif not servicos_selecionados:
                st.warning("Selecione pelo menos um serviço.")
            else:
                valor_total_os = sum(
                    (Decimal(str(servico["preco_base"])) for servico in servicos_selecionados),
                    Decimal("0.00"),
                ).quantize(Decimal("0.01"))

                try:
                    with st.spinner(SPINNER_XANO):
                        time.sleep(2)
                        nova_os = client.criar_ordem_servico(
                            cliente_selecionado_os["id"],
                            veiculo_selecionado_os["id"],
                            valor_total_os,
                            observacoes_os.strip(),
                        )
                        for servico in servicos_selecionados:
                            client.adicionar_item_ordem_servico(
                                nova_os["id"],
                                servico["id"],
                                float(Decimal(str(servico["preco_base"]))),
                            )
                        client.atualizar_total_os(nova_os["id"])
                    st.session_state["ordem_servico_criada"] = True
                    st.rerun()
                except XanoAPIError as error:
                    show_error(error)

    with list_column:
        st.subheader("Ordens de Serviço")
        clientes_por_id_os = {
            str(cliente.get("id")): cliente for cliente in clientes_os if cliente.get("id") is not None
        }
        servicos_por_id_os = {
            str(servico.get("id")): servico for servico in servicos_os if servico.get("id") is not None
        }

        registros_os = []
        for ordem in ordens_servico:
            cliente_ordem = ordem.get("cliente") or clientes_por_id_os.get(str(ordem.get("cliente_id")), {})
            veiculo_ordem = ordem.get("veiculo") or {}
            try:
                with st.spinner(SPINNER_XANO):
                    itens_ordem = client.list_itens_ordem_servico(ordem["id"])
            except (KeyError, XanoAPIError) as error:
                itens_ordem = []
                show_error(error)
            nomes_servicos_ordem = []
            for item in itens_ordem:
                if isinstance(item, dict):
                    servico_id = item.get("servico_id", item.get("id"))
                    servico_item = item.get("servico") or servicos_por_id_os.get(str(servico_id), {})
                    nomes_servicos_ordem.append(
                        str(item.get("nome_servico") or servico_item.get("nome", "Serviço"))
                    )
                else:
                    servico_item = servicos_por_id_os.get(str(item), {})
                    nomes_servicos_ordem.append(servico_item.get("nome", f"ID {item}"))

            registros_os.append(
                {
                    "id": ordem.get("id"),
                    "cliente": cliente_ordem.get("nome", ordem.get("cliente_nome", "")),
                    "veiculo": " ".join(
                        value
                        for value in (
                            veiculo_ordem.get(
                                "placa",
                                ordem.get("placa", f"Veículo ID {ordem.get('veiculo_id', '')}"),
                            ),
                            veiculo_ordem.get("modelo", ordem.get("modelo", "")),
                        )
                        if value
                    ),
                    "servicos": ", ".join(nomes_servicos_ordem),
                    "status": ordem.get("status", ""),
                    "data_abertura": format_datetime(ordem.get("created_at")),
                    "valor_total": format_brl(ordem.get("valor_total")),
                }
            )

        if os_data_loaded:
            show_records(
                registros_os,
                {
                    "id": "O.S.",
                    "cliente": "Cliente",
                    "veiculo": "Veículo",
                    "servicos": "Serviços",
                    "status": "Status",
                    "data_abertura": "Abertura",
                    "valor_total": "Valor total",
                },
            )

        for ordem in ordens_servico:
            ordem_id = ordem.get("id")
            status_atual = ordem.get("status", "Aguardando")
            if ordem_id is None:
                continue
            with st.expander(f"O.S. {ordem_id} · {status_atual}"):
                opcoes_status = transicoes_os_permitidas(status_atual)
                if not opcoes_status:
                    st.caption("Esta O.S. não possui transições de status disponíveis.")
                    continue
                with st.form(f"atualizar_status_os_{ordem_id}"):
                    novo_status = st.selectbox(
                        "Avançar status",
                        opcoes_status,
                        key=f"novo_status_os_{ordem_id}",
                    )
                    atualizar_status = st.form_submit_button(
                        "Atualizar status",
                        key=f"submit_status_os_{ordem_id}",
                    )
                if atualizar_status:
                    try:
                        with st.spinner(SPINNER_XANO):
                            client.update_ordem_servico_status(ordem_id, novo_status)
                        st.session_state["ordem_servico_status_atualizado"] = (ordem_id, novo_status)
                        st.rerun()
                    except XanoAPIError as error:
                        show_error(error)

else:
    client_load_error = None
    try:
        clientes = session_cached_xano_data("clientes", client.list_clientes)
    except XanoAPIError as error:
        clientes = []
        client_load_error = error
        show_error(error)

    form_column, list_column = st.columns((1, 1.5), gap="large")
    with form_column:
        st.subheader("Novo veículo")
        if client_load_error:
            st.info("Não é possível carregar o formulário sem consultar os clientes na API.")
        elif not clientes:
            st.info("Cadastre um cliente antes de cadastrar um veículo.")
        else:
            cliente_por_opcao = {
                f"{cliente.get('nome', 'Cliente sem nome')} · ID {cliente.get('id')}": cliente
                for cliente in clientes
                if cliente.get("id") is not None
            }
            if not cliente_por_opcao:
                st.warning("A API não retornou identificadores de cliente utilizáveis.")
            else:
                with st.form("novo_veiculo", clear_on_submit=True):
                    proprietario = st.selectbox("Proprietário *", tuple(cliente_por_opcao))
                    placa = st.text_input("Placa *")
                    modelo = st.text_input("Modelo *")
                    marca = optional_text("Marca", "veiculo_marca")
                    ano = st.number_input("Ano", min_value=1900, max_value=2100, value=None, step=1)
                    cor = optional_text("Cor", "veiculo_cor")
                    categoria = st.selectbox(
                        "Categoria",
                        ("", "Hatch", "Sedã", "SUV", "Picape", "Esportivo"),
                    )
                    submitted = st.form_submit_button("Cadastrar veículo", type="primary")

                if submitted:
                    payload: dict[str, Any] = {
                        "cliente_id": cliente_por_opcao[proprietario]["id"],
                        "placa": placa.strip(),
                        "modelo": modelo.strip(),
                    }
                    payload.update(
                        {
                            key: value
                            for key, value in {
                                "marca": marca,
                                "ano": int(ano) if ano is not None else None,
                                "cor": cor,
                                "categoria": categoria or None,
                            }.items()
                            if value is not None
                        }
                    )
                    if not payload["placa"] or not payload["modelo"]:
                        st.warning("Placa e modelo são obrigatórios.")
                    else:
                        try:
                            with st.spinner(SPINNER_XANO):
                                client.create_veiculo(payload)
                            st.success("Veículo cadastrado.")
                            st.rerun()
                        except XanoAPIError as error:
                            show_error(error)

    with list_column:
        st.subheader("Veículos cadastrados")
        filtro = st.selectbox(
            "Filtrar por proprietário",
            ("Todos", *tuple(
                f"{cliente.get('nome', 'Cliente sem nome')} · ID {cliente.get('id')}"
                for cliente in clientes
                if cliente.get("id") is not None
            )),
        )
        cliente_id = None if filtro == "Todos" else cliente_por_opcao[filtro]["id"]
        try:
            with st.spinner(SPINNER_XANO):
                veiculos = client.list_veiculos(cliente_id)
            nomes_clientes = {
                str(cliente.get("id")): cliente.get("nome", "") for cliente in clientes
            }
            for veiculo in veiculos:
                veiculo["proprietario"] = nomes_clientes.get(str(veiculo.get("cliente_id")), "")
            show_records(
                veiculos,
                {
                    "id": "ID",
                    "placa": "Placa",
                    "marca": "Marca",
                    "modelo": "Modelo",
                    "ano": "Ano",
                    "cor": "Cor",
                    "categoria": "Categoria",
                    "proprietario": "Proprietário",
                },
            )
        except XanoAPIError as error:
            show_error(error)
