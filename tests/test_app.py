import json
import os
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import URLError

from streamlit.testing.v1 import AppTest
from xano_client import XanoClient


class FakeResponse:
    def __init__(self, payload):
        import json

        self.payload = json.dumps(payload).encode("utf-8")

    def read(self):
        return self.payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def fake_urlopen(request, timeout):
    if request.full_url.endswith("/cliente"):
        return FakeResponse([{"id": 10, "nome": "Cliente Teste", "telefone": "11999990000"}])
    if "/veiculo" in request.full_url:
        return FakeResponse(
            [
                {
                    "id": 20,
                    "placa": "ABC1D23",
                    "modelo": "Modelo Teste",
                    "cliente_id": 10,
                }
            ]
        )
    if request.full_url.endswith("/servico"):
        if request.get_method() == "POST":
            payload = json.loads(request.data.decode("utf-8"))
            return FakeResponse({"id": 16, **payload})
        return FakeResponse(
            [
                {
                    "id": 15,
                    "nome": "Lavagem detalhada",
                    "descricao": "Limpeza completa",
                    "preco_base": 89.9,
                    "tempo_estimado_min": 60,
                    "categoria": "Lavagem",
                }
            ]
        )
    if request.full_url.endswith("/ordem_servico"):
        if request.get_method() == "POST":
            payload = json.loads(request.data.decode("utf-8"))
            return FakeResponse(
                {
                    "id": 44,
                    "status": "Aguardando",
                    "created_at": "2026-10-19T12:00:00",
                    "valor_total": 89.9,
                    **payload,
                    "itens_servico": [
                        {"servico_id": 15, "preco_unitario": 89.9, "tempo_estimado_min": 60}
                    ],
                }
            )
        return FakeResponse(
            [
                {
                    "id": 44,
                    "cliente_id": 10,
                    "cliente": {"id": 10, "nome": "Cliente Teste"},
                    "veiculo_id": 20,
                    "veiculo": {
                        "id": 20,
                        "placa": "ABC1D23",
                        "modelo": "Modelo Teste",
                    },
                    "servicos": [
                        {"servico_id": 15, "preco_unitario": 89.9, "tempo_estimado_min": 60}
                    ],
                    "status": "Aguardando",
                    "created_at": "2026-10-19T12:00:00",
                    "previsao_entrega": "2026-10-19T13:00:00",
                    "valor_total": 89.9,
                }
            ]
        )
    if request.full_url.startswith("https://example.xano.io/api:group/item_ordem_servico"):
        if request.get_method() == "GET":
            return FakeResponse([{"servico_id": 15, "preco_unitario": 89.9}])
        return FakeResponse({"id": 101})
    if "/ordem_servico/" in request.full_url and request.get_method() == "PATCH":
        payload = json.loads(request.data.decode("utf-8"))
        return FakeResponse({"id": 44, **payload})
    raise AssertionError(f"Rota inesperada: {request.full_url}")


def fake_urlopen_sem_duracao(request, timeout):
    if request.full_url.endswith("/servico") and request.get_method() == "GET":
        return FakeResponse([{"id": 15, "nome": "Lavagem detalhada", "preco_base": 89.9}])
    return fake_urlopen(request, timeout)


def fake_urlopen_os_entregue(request, timeout):
    if request.full_url.endswith("/ordem_servico") and request.get_method() == "GET":
        return FakeResponse(
            [
                {
                    "id": 44,
                    "cliente_id": 10,
                    "veiculo_id": 20,
                    "servicos": [{"servico_id": 15, "preco_unitario": 89.9}],
                    "status": "Entregue",
                }
            ]
        )
    return fake_urlopen(request, timeout)


def fake_urlopen_os_multiplos_clientes(request, timeout):
    if request.full_url.endswith("/cliente"):
        return FakeResponse(
            [
                {"id": 10, "nome": "Cliente Teste", "telefone": "11999990000"},
                {"id": 11, "nome": "Outro Cliente", "telefone": "11888880000"},
            ]
        )
    if request.full_url.endswith("/veiculo?cliente_id=10") or request.full_url.endswith(
        "/veiculo?cliente_id=11"
    ):
        return FakeResponse(
            [
                {"id": 20, "placa": "ABC1D23", "modelo": "Modelo Teste", "cliente_id": 10},
                {"id": 21, "placa": "XYZ9Z99", "modelo": "Outro Modelo", "cliente_id": 11},
            ]
        )
    return fake_urlopen(request, timeout)


class StreamlitAppTests(unittest.TestCase):
    def setUp(self):
        XanoClient.clear_read_cache()
        self.app_path = Path(__file__).resolve().parents[1] / "app.py"

    def test_vehicle_page_loads_owner_and_vehicle_records(self):
        with patch.dict(
            os.environ,
            {
                "XANO_API_BASE_URL": "https://example.xano.io/api:group",
                "XANO_API_TOKEN": "test-token",
            },
        ), patch("xano_client.urlopen", side_effect=fake_urlopen):
            app = AppTest.from_file(str(self.app_path)).run()
            app.sidebar.radio[0].set_value("Veículos")
            app.run()

        self.assertEqual(len(app.exception), 0)
        self.assertIn("Cliente Teste · ID 10", app.selectbox[0].options)
        self.assertEqual(len(app.dataframe), 1)

    def test_vehicle_page_distinguishes_api_failure_from_empty_list(self):
        with patch.dict(
            os.environ,
            {
                "XANO_API_BASE_URL": "https://example.xano.io/api:group",
                "XANO_API_TOKEN": "test-token",
            },
        ), patch("xano_client.urlopen", side_effect=URLError("offline")):
            app = AppTest.from_file(str(self.app_path)).run()
            app.sidebar.radio[0].set_value("Veículos")
            app.run()

        self.assertEqual(len(app.exception), 0)
        info_messages = [element.value for element in app.info]
        self.assertIn(
            "Não é possível carregar o formulário sem consultar os clientes na API.",
            info_messages,
        )
        self.assertNotIn("Cadastre um cliente antes de cadastrar um veículo.", info_messages)

    def test_services_page_lists_price_in_brl(self):
        with patch.dict(
            os.environ,
            {
                "XANO_API_BASE_URL": "https://example.xano.io/api:group",
                "XANO_API_TOKEN": "test-token",
            },
        ), patch("xano_client.urlopen", side_effect=fake_urlopen):
            app = AppTest.from_file(str(self.app_path), default_timeout=10).run()
            app.sidebar.radio[0].set_value("Serviços")
            app.run(timeout=10)

        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.dataframe), 1)
        row = app.dataframe[0].value.iloc[0]
        self.assertEqual(row["Nome"], "Lavagem detalhada")
        self.assertEqual(row["Preço base"], "R$ 89,90")
        self.assertEqual(row["Tempo (minutos)"], 60)

    def test_service_form_posts_payload_and_optional_fields(self):
        with patch.dict(
            os.environ,
            {
                "XANO_API_BASE_URL": "https://example.xano.io/api:group",
                "XANO_API_TOKEN": "test-token",
            },
        ), patch("xano_client.urlopen", side_effect=fake_urlopen) as urlopen:
            app = AppTest.from_file(str(self.app_path), default_timeout=10).run()
            app.sidebar.radio[0].set_value("Serviços")
            app.run(timeout=10)
            app.text_input(key="servico_nome").set_value("Lavagem detalhada")
            app.number_input(key="servico_preco_base").set_value(349.9)
            app.text_area(key="servico_descricao").set_value("Polimento em duas etapas")
            app.number_input(key="servico_tempo_estimado_min").set_value(180)
            app.text_input(key="servico_categoria").set_value("Polimento")
            app.button(key="create_servico").click().run()

        self.assertEqual(len(app.exception), 0)
        self.assertIn("Serviço cadastrado.", [item.value for item in app.success])
        post_requests = [
            call.args[0]
            for call in urlopen.call_args_list
            if call.args[0].get_method() == "POST"
        ]
        self.assertEqual(len(post_requests), 1)
        self.assertEqual(post_requests[0].full_url, "https://example.xano.io/api:group/servico")
        payload = json.loads(post_requests[0].data.decode("utf-8"))
        self.assertEqual(payload["nome"], "Lavagem detalhada")
        self.assertEqual(payload["preco_base"], 349.9)
        self.assertEqual(payload["descricao"], "Polimento em duas etapas")
        self.assertEqual(payload["tempo_estimado_min"], 180)
        self.assertEqual(payload["categoria"], "Polimento")

    def test_service_form_rejects_more_than_two_decimal_places(self):
        with patch.dict(
            os.environ,
            {
                "XANO_API_BASE_URL": "https://example.xano.io/api:group",
                "XANO_API_TOKEN": "test-token",
            },
        ), patch("xano_client.urlopen", side_effect=fake_urlopen) as urlopen:
            app = AppTest.from_file(str(self.app_path), default_timeout=10).run()
            app.sidebar.radio[0].set_value("Serviços")
            app.run(timeout=10)
            app.text_input(key="servico_nome").set_value("Lavagem")
            app.number_input(key="servico_preco_base").set_value(10.123)
            app.button(key="create_servico").click().run()

        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len([call for call in urlopen.call_args_list if call.args[0].get_method() == "POST"]), 0)
        self.assertIn("Informe o preço base com no máximo duas casas decimais.", [item.value for item in app.warning])

    def test_service_form_rejects_missing_name(self):
        with patch.dict(
            os.environ,
            {
                "XANO_API_BASE_URL": "https://example.xano.io/api:group",
                "XANO_API_TOKEN": "test-token",
            },
        ), patch("xano_client.urlopen", side_effect=fake_urlopen) as urlopen:
            app = AppTest.from_file(str(self.app_path), default_timeout=10).run()
            app.sidebar.radio[0].set_value("Serviços")
            app.run(timeout=10)
            app.number_input(key="servico_preco_base").set_value(10.0)
            app.button(key="create_servico").click().run(timeout=10)

        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len([call for call in urlopen.call_args_list if call.args[0].get_method() == "POST"]), 0)
        self.assertIn("Nome é obrigatório.", [item.value for item in app.warning])

    def test_services_page_shows_empty_catalog(self):
        with patch.dict(
            os.environ,
            {
                "XANO_API_BASE_URL": "https://example.xano.io/api:group",
                "XANO_API_TOKEN": "test-token",
            },
        ), patch("xano_client.urlopen", return_value=FakeResponse([])):
            app = AppTest.from_file(str(self.app_path), default_timeout=10).run()
            app.sidebar.radio[0].set_value("Serviços")
            app.run(timeout=10)

        self.assertEqual(len(app.exception), 0)
        self.assertIn("Nenhum registro encontrado.", [item.value for item in app.info])

    def test_services_page_reports_api_failure(self):
        with patch.dict(
            os.environ,
            {
                "XANO_API_BASE_URL": "https://example.xano.io/api:group",
                "XANO_API_TOKEN": "test-token",
            },
        ), patch("xano_client.urlopen", side_effect=URLError("offline")):
            app = AppTest.from_file(str(self.app_path), default_timeout=10).run()
            app.sidebar.radio[0].set_value("Serviços")
            app.run(timeout=10)

        self.assertEqual(len(app.exception), 0)
        self.assertIn("Não foi possível conectar à API Xano.", [item.value for item in app.error])

    def test_service_order_page_lists_snapshotted_items_and_status(self):
        with patch.dict(
            os.environ,
            {
                "XANO_API_BASE_URL": "https://example.xano.io/api:group",
                "XANO_API_TOKEN": "test-token",
            },
        ), patch("xano_client.urlopen", side_effect=fake_urlopen):
            app = AppTest.from_file(str(self.app_path), default_timeout=10).run()
            app.sidebar.radio[0].set_value("Ordens de Serviço")
            app.run(timeout=10)

        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.dataframe), 1)
        row = app.dataframe[0].value.iloc[0]
        self.assertEqual(row["Cliente"], "Cliente Teste")
        self.assertEqual(row["Veículo"], "ABC1D23 Modelo Teste")
        self.assertEqual(row["Serviços"], "Lavagem detalhada")
        self.assertEqual(row["Status"], "🟡 Aguardando")
        self.assertEqual(row["Abertura"], "19/10/2026 12:00")

    def test_service_order_loads_vehicles_only_after_customer_selection(self):
        with patch.dict(
            os.environ,
            {
                "XANO_API_BASE_URL": "https://example.xano.io/api:group",
                "XANO_API_TOKEN": "test-token",
            },
        ), patch("xano_client.urlopen", side_effect=fake_urlopen) as urlopen:
            app = AppTest.from_file(str(self.app_path), default_timeout=10).run()
            app.sidebar.radio[0].set_value("Ordens de Serviço")
            app.run(timeout=10)

            vehicle_requests = [
                call.args[0]
                for call in urlopen.call_args_list
                if "/veiculo" in call.args[0].full_url
            ]
            self.assertEqual(vehicle_requests, [])

            app.selectbox(key="os_cliente").set_value("Cliente Teste · ID 10").run(timeout=10)

        vehicle_requests = [
            call.args[0]
            for call in urlopen.call_args_list
            if "/veiculo" in call.args[0].full_url
        ]
        self.assertEqual(len(vehicle_requests), 1)
        self.assertEqual(
            vehicle_requests[0].full_url,
            "https://example.xano.io/api:group/veiculo?cliente_id=10",
        )
        self.assertEqual(
            len([call for call in urlopen.call_args_list if call.args[0].full_url.endswith("/cliente")]),
            1,
        )
        self.assertEqual(
            len([call for call in urlopen.call_args_list if call.args[0].full_url.endswith("/servico")]),
            1,
        )

    def test_service_order_filters_vehicle_ids_and_clears_selection_on_customer_change(self):
        with patch.dict(
            os.environ,
            {
                "XANO_API_BASE_URL": "https://example.xano.io/api:group",
                "XANO_API_TOKEN": "test-token",
            },
        ), patch("xano_client.urlopen", side_effect=fake_urlopen_os_multiplos_clientes) as urlopen:
            app = AppTest.from_file(str(self.app_path), default_timeout=10).run()
            app.sidebar.radio[0].set_value("Ordens de Serviço")
            app.run(timeout=10)

            self.assertEqual(app.selectbox(key="os_veiculo").options, [])

            app.selectbox(key="os_cliente").set_value("Cliente Teste · ID 10").run(timeout=10)
            self.assertEqual(
                app.selectbox(key="os_veiculo").options,
                ["ABC1D23 · Modelo Teste · ID 20"],
            )
            app.selectbox(key="os_veiculo").set_value(
                "ABC1D23 · Modelo Teste · ID 20"
            ).run(timeout=10)

            app.selectbox(key="os_cliente").set_value("Outro Cliente · ID 11").run(timeout=10)

        self.assertEqual(len(app.exception), 0)
        self.assertEqual(
            app.selectbox(key="os_veiculo").options,
            ["XYZ9Z99 · Outro Modelo · ID 21"],
        )
        self.assertIsNone(app.selectbox(key="os_veiculo").value)
        vehicle_urls = [
            call.args[0].full_url
            for call in urlopen.call_args_list
            if "/veiculo?cliente_id=" in call.args[0].full_url
        ]
        self.assertEqual(
            vehicle_urls,
            [
                "https://example.xano.io/api:group/veiculo?cliente_id=10",
                "https://example.xano.io/api:group/veiculo?cliente_id=11",
            ],
        )

    def test_service_order_creation_posts_total_and_items(self):
        with patch.dict(
            os.environ,
            {
                "XANO_API_BASE_URL": "https://example.xano.io/api:group",
                "XANO_API_TOKEN": "test-token",
            },
        ), patch("xano_client.urlopen", side_effect=fake_urlopen) as urlopen, patch(
            "xano_client.requests.post"
        ) as post:
            ordem_response = MagicMock()
            ordem_response.json.return_value = {"id": 44, "status": "Aguardando"}
            item_response = MagicMock()
            item_response.json.return_value = {"id": 101}
            total_response = MagicMock()
            total_response.json.return_value = {"id": 44, "valor_total": 89.9}
            post.side_effect = [ordem_response, item_response, total_response]
            app = AppTest.from_file(str(self.app_path), default_timeout=10).run()
            app.sidebar.radio[0].set_value("Ordens de Serviço")
            app.run(timeout=10)
            app.selectbox(key="os_cliente").set_value("Cliente Teste · ID 10").run(timeout=10)
            app.selectbox(key="os_veiculo").set_value(
                "ABC1D23 · Modelo Teste · ID 20"
            )
            app.multiselect(key="os_servicos").set_value(
                ["Lavagem detalhada · ID 15"]
            )
            app.button(key="create_ordem_servico").click().run(timeout=10)

        self.assertEqual(len(app.exception), 0)
        self.assertIn("Ordem de Serviço aberta.", [item.value for item in app.success])
        self.assertEqual(post.call_count, 3)
        payload = post.call_args_list[0].kwargs["json"]
        self.assertEqual(payload["cliente_id"], 10)
        self.assertEqual(payload["veiculo_id"], 20)
        self.assertEqual(payload["status"], "Aguardando")
        self.assertEqual(payload["valor_total"], 89.9)
        self.assertEqual(post.call_args_list[0].args[0], "https://example.xano.io/api:group/ordem_servico")
        item_request = post.call_args_list[1]
        self.assertEqual(item_request.args[0], "https://example.xano.io/api:group/item_ordem_servico")
        self.assertEqual(
            item_request.kwargs["json"],
            {"ordem_servico_id": 44, "servico_id": 15, "preco_unitario": 89.9},
        )
        self.assertEqual(
            post.call_args_list[2].args[0],
            "https://example.xano.io/api:group/atualizar_total_os",
        )

    def test_service_order_status_uses_sequential_transition(self):
        with patch.dict(
            os.environ,
            {
                "XANO_API_BASE_URL": "https://example.xano.io/api:group",
                "XANO_API_TOKEN": "test-token",
            },
        ), patch("xano_client.urlopen", side_effect=fake_urlopen) as urlopen:
            app = AppTest.from_file(str(self.app_path), default_timeout=10).run()
            app.sidebar.radio[0].set_value("Ordens de Serviço")
            app.run(timeout=10)
            self.assertEqual(
                app.selectbox(key="novo_status_os_44").options,
                ["Em Andamento", "Cancelado"],
            )
            app.selectbox(key="novo_status_os_44").set_value("Em Andamento")
            app.button(key="submit_status_os_44").click().run(timeout=10)

        self.assertEqual(len(app.exception), 0)
        patch_requests = [
            call.args[0]
            for call in urlopen.call_args_list
            if call.args[0].get_method() == "PATCH"
        ]
        self.assertEqual(len(patch_requests), 1)
        self.assertEqual(
            patch_requests[0].full_url,
            "https://example.xano.io/api:group/ordem_servico/44",
        )
        self.assertEqual(
            json.loads(patch_requests[0].data.decode("utf-8")),
            {"status": "Em Andamento"},
        )
        self.assertIn("Status da O.S. 44 atualizado para Em Andamento.", [item.value for item in app.success])

    def test_service_order_can_be_cancelled_even_after_delivery(self):
        with patch.dict(
            os.environ,
            {
                "XANO_API_BASE_URL": "https://example.xano.io/api:group",
                "XANO_API_TOKEN": "test-token",
            },
        ), patch("xano_client.urlopen", side_effect=fake_urlopen_os_entregue):
            app = AppTest.from_file(str(self.app_path), default_timeout=10).run()
            app.sidebar.radio[0].set_value("Ordens de Serviço")
            app.run(timeout=10)

        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.selectbox(key="novo_status_os_44").options, ["Cancelado"])

    def test_service_order_api_failure_does_not_show_empty_list(self):
        with patch.dict(
            os.environ,
            {
                "XANO_API_BASE_URL": "https://example.xano.io/api:group",
                "XANO_API_TOKEN": "test-token",
            },
        ), patch("xano_client.urlopen", side_effect=URLError("offline")):
            app = AppTest.from_file(str(self.app_path), default_timeout=10).run()
            app.sidebar.radio[0].set_value("Ordens de Serviço")
            app.run(timeout=10)

        self.assertEqual(len(app.exception), 0)
        self.assertTrue(
            any(
                message.startswith("Não foi possível carregar as Ordens de Serviço")
                for message in (item.value for item in app.error)
            )
        )
        self.assertNotIn("Nenhum registro encontrado.", [item.value for item in app.info])


if __name__ == "__main__":
    unittest.main()
