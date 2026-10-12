"""Interface Streamlit para cadastro e consulta de clientes e veículos."""

from __future__ import annotations

import os
from typing import Any

import streamlit as st

from xano_client import XanoAPIError, XanoClient


st.set_page_config(page_title="Clientes e veículos", page_icon="🚘", layout="wide")
st.title("Clientes e veículos")
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
section = st.sidebar.radio("Cadastro", ("Clientes", "Veículos"))


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
                    client.create_cliente(payload)
                    st.success("Cliente cadastrado.")
                    st.rerun()
                except XanoAPIError as error:
                    show_error(error)

    with list_column:
        st.subheader("Clientes cadastrados")
        try:
            show_records(
                client.list_clientes(),
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

else:
    client_load_error = None
    try:
        clientes = client.list_clientes()
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
