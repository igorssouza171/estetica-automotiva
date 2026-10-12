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


if __name__ == "__main__":
    unittest.main()
