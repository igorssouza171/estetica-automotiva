import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from streamlit.testing.v1 import AppTest


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
    raise AssertionError(f"Rota inesperada: {request.full_url}")


class StreamlitAppTests(unittest.TestCase):
    def setUp(self):
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


if __name__ == "__main__":
    unittest.main()
