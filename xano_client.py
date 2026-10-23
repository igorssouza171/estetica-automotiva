"""Cliente REST mínimo para operações de clientes, veículos e serviços no Xano."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import streamlit as st
import requests


XANO_GET_CACHE_TTL_SECONDS = 60


class XanoAPIError(RuntimeError):
    """Erro retornado pela API Xano ou de comunicação com ela."""


def _perform_request(
    base_url: str,
    token: str,
    timeout: float,
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> Any:
    url = base_url.rstrip("/") + "/" + path.lstrip("/")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(
        url,
        data=body,
        method=method,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            response_body = response.read()
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise XanoAPIError(XanoClient._error_message(detail, error.code)) from error
    except URLError as error:
        raise XanoAPIError("Não foi possível conectar à API Xano.") from error
    except TimeoutError as error:
        raise XanoAPIError("A API Xano excedeu o tempo limite de resposta.") from error

    if not response_body:
        return None
    try:
        return json.loads(response_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise XanoAPIError("A API Xano retornou uma resposta inválida.") from error


@st.cache_data(ttl=XANO_GET_CACHE_TTL_SECONDS, max_entries=128, show_spinner=False)
def _cached_clientes(base_url: str, token: str, timeout: float) -> Any:
    return _perform_request(base_url, token, timeout, "GET", "cliente")


@st.cache_data(ttl=XANO_GET_CACHE_TTL_SECONDS, max_entries=256, show_spinner=False)
def _cached_veiculos(
    base_url: str,
    token: str,
    timeout: float,
    cliente_id: str | int | None,
) -> Any:
    path = "veiculo"
    if cliente_id is not None:
        path += "?" + urlencode({"cliente_id": cliente_id})
    return _perform_request(base_url, token, timeout, "GET", path)


@st.cache_data(ttl=XANO_GET_CACHE_TTL_SECONDS, max_entries=128, show_spinner=False)
def _cached_servicos(base_url: str, token: str, timeout: float) -> Any:
    return _perform_request(base_url, token, timeout, "GET", "servico")


@st.cache_data(ttl=XANO_GET_CACHE_TTL_SECONDS, max_entries=128, show_spinner=False)
def _cached_ordens_servico(base_url: str, token: str, timeout: float) -> Any:
    return _perform_request(base_url, token, timeout, "GET", "ordem_servico")


@st.cache_data(ttl=XANO_GET_CACHE_TTL_SECONDS, max_entries=256, show_spinner=False)
def _cached_itens_ordem_servico(
    base_url: str,
    token: str,
    timeout: float,
    ordem_servico_id: str | int,
) -> Any:
    path = "item_ordem_servico?" + urlencode({"ordem_servico_id": ordem_servico_id})
    return _perform_request(base_url, token, timeout, "GET", path)


class XanoClient:
    def __init__(self, base_url: str, token: str, timeout: float = 15.0) -> None:
        if not base_url.strip():
            raise ValueError("A URL base da API Xano é obrigatória.")
        if not token.strip():
            raise ValueError("O token de acesso à API Xano é obrigatório.")

        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        return _perform_request(self.base_url, self.token, self.timeout, method, path, payload)

    @staticmethod
    def clear_read_cache() -> None:
        _cached_clientes.clear()
        _cached_veiculos.clear()
        _cached_servicos.clear()
        _cached_ordens_servico.clear()
        _cached_itens_ordem_servico.clear()

    @staticmethod
    def _error_message(detail: str, status: int) -> str:
        try:
            parsed = json.loads(detail)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, str) and parsed.strip():
            return parsed.strip()
        if isinstance(parsed, dict):
            message = parsed.get("message") or parsed.get("error")
            if message:
                return str(message)
        if detail.strip():
            return detail.strip()
        return f"A API Xano rejeitou a operação (HTTP {status})."

    @staticmethod
    def _records(response: Any) -> list[dict[str, Any]]:
        if isinstance(response, list):
            records = response
        elif isinstance(response, dict):
            records = next(
                (response[key] for key in ("items", "records", "results", "data") if key in response),
                None,
            )
            if isinstance(records, dict):
                records = records.get("items", records.get("records", records.get("results")))
        else:
            records = None

        if not isinstance(records, list) or not all(isinstance(item, dict) for item in records):
            raise XanoAPIError("A API Xano retornou uma lista em formato não reconhecido.")
        return records

    def list_clientes(self) -> list[dict[str, Any]]:
        return self._records(_cached_clientes(self.base_url, self.token, self.timeout))

    def create_cliente(self, payload: dict[str, Any]) -> Any:
        response = self._request("POST", "cliente", payload)
        _cached_clientes.clear()
        return response

    def list_veiculos(self, cliente_id: str | int | None = None) -> list[dict[str, Any]]:
        return self._records(
            _cached_veiculos(self.base_url, self.token, self.timeout, cliente_id)
        )

    def create_veiculo(self, payload: dict[str, Any]) -> Any:
        response = self._request("POST", "veiculo", payload)
        _cached_veiculos.clear()
        return response

    def list_servicos(self) -> list[dict[str, Any]]:
        servicos = self._records(_cached_servicos(self.base_url, self.token, self.timeout))
        return [
            {
                **servico,
                "tempo_estimado_min": int(servico["tempo_estimado_min"]),
            }
            if servico.get("tempo_estimado_min") is not None
            else servico
            for servico in servicos
        ]

    def create_servico(self, payload: dict[str, Any]) -> Any:
        dados = dict(payload)
        if dados.get("tempo_estimado_min") is not None:
            dados["tempo_estimado_min"] = int(dados["tempo_estimado_min"])
        response = self._request("POST", "servico", dados)
        _cached_servicos.clear()
        return response

    def list_ordens_servico(self) -> list[dict[str, Any]]:
        return self._records(_cached_ordens_servico(self.base_url, self.token, self.timeout))

    def list_itens_ordem_servico(self, ordem_servico_id: int) -> list[dict[str, Any]]:
        return self._records(
            _cached_itens_ordem_servico(
                self.base_url,
                self.token,
                self.timeout,
                self._integer_id(ordem_servico_id, "ordem_servico_id"),
            )
        )

    def atualizar_total_os(self, ordem_servico_id: int) -> dict:
        res = requests.post(
            f"{self.base_url}/atualizar_total_os",
            json={"ordem_servico_id": self._integer_id(ordem_servico_id, "ordem_servico_id")},
            headers=self.headers,
            timeout=self.timeout,
        )
        res.raise_for_status()
        return res.json()

    def criar_ordem_servico(
        self,
        cliente_id: int,
        veiculo_id: int,
        valor_total: float,
        observacoes: str = "",
        status: str = "Aguardando",
    ) -> dict:
        cliente_id_int = self._integer_id(cliente_id, "cliente_id")
        veiculo_id_int = self._integer_id(veiculo_id, "veiculo_id")
        payload = {
            "cliente_id": cliente_id_int,
            "veiculo_id": veiculo_id_int,
            "status": status,
            "valor_total": float(Decimal(str(valor_total)).quantize(Decimal("0.01"))),
            "observacoes": observacoes,
        }
        res = requests.post(
            f"{self.base_url}/ordem_servico",
            json=payload,
            headers=self.headers,
            timeout=self.timeout,
        )
        res.raise_for_status()
        ordem = res.json()
        if not isinstance(ordem, dict):
            raise XanoAPIError("A API Xano retornou uma resposta inválida para a O.S.")
        _cached_ordens_servico.clear()
        return ordem

    def adicionar_item_ordem_servico(
        self,
        ordem_servico_id: int,
        servico_id: int,
        preco_unitario: float,
    ) -> dict:
        payload = {
            "ordem_servico_id": self._integer_id(ordem_servico_id, "ordem_servico_id"),
            "servico_id": self._integer_id(servico_id, "servico_id"),
            "preco_unitario": float(Decimal(str(preco_unitario)).quantize(Decimal("0.01"))),
        }
        res = requests.post(
            f"{self.base_url}/item_ordem_servico",
            json=payload,
            headers=self.headers,
            timeout=self.timeout,
        )
        res.raise_for_status()
        return res.json()

    @staticmethod
    def _integer_id(value: Any, field_name: str) -> int:
        if isinstance(value, bool):
            raise XanoAPIError(f"O campo {field_name} deve conter IDs inteiros.")
        try:
            numeric_value = Decimal(str(value).strip())
        except (InvalidOperation, ValueError):
            raise XanoAPIError(f"O campo {field_name} deve conter IDs inteiros.") from None
        if not numeric_value.is_finite() or numeric_value != numeric_value.to_integral_value():
            raise XanoAPIError(f"O campo {field_name} deve conter IDs inteiros.")
        return int(numeric_value)

    def update_ordem_servico_status(self, ordem_id: str | int, status: str) -> Any:
        path = f"ordem_servico/{quote(str(ordem_id), safe='')}"
        response = self._request("PATCH", path, {"status": status})
        _cached_ordens_servico.clear()
        return response
