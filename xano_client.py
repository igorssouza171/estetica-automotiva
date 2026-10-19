"""Cliente REST mínimo para operações de clientes, veículos e serviços no Xano."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class XanoAPIError(RuntimeError):
    """Erro retornado pela API Xano ou de comunicação com ela."""


class XanoClient:
    def __init__(self, base_url: str, token: str, timeout: float = 15.0) -> None:
        if not base_url.strip():
            raise ValueError("A URL base da API Xano é obrigatória.")
        if not token.strip():
            raise ValueError("O token de acesso à API Xano é obrigatório.")

        self.base_url = base_url.rstrip("/") + "/"
        self.token = token
        self.timeout = timeout

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        url = self.base_url + path.lstrip("/")
        body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = Request(
            url,
            data=body,
            method=method,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                response_body = response.read()
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise XanoAPIError(self._error_message(detail, error.code)) from error
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

    @staticmethod
    def _error_message(detail: str, status: int) -> str:
        try:
            parsed = json.loads(detail)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            message = parsed.get("message") or parsed.get("error")
            if message:
                return str(message)
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
        return self._records(self._request("GET", "cliente"))

    def create_cliente(self, payload: dict[str, Any]) -> Any:
        return self._request("POST", "cliente", payload)

    def list_veiculos(self, cliente_id: str | int | None = None) -> list[dict[str, Any]]:
        path = "veiculo"
        if cliente_id is not None:
            path += "?" + urlencode({"cliente_id": cliente_id})
        return self._records(self._request("GET", path))

    def create_veiculo(self, payload: dict[str, Any]) -> Any:
        return self._request("POST", "veiculo", payload)

    def list_servicos(self) -> list[dict[str, Any]]:
        servicos = self._records(self._request("GET", "servico"))
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
        return self._request("POST", "servico", dados)
