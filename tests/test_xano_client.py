import json
import unittest
from unittest.mock import patch

from xano_client import XanoClient


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def read(self):
        return self.payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class XanoClientTests(unittest.TestCase):
    def setUp(self):
        self.client = XanoClient("https://example.xano.io/api:group", "test-token")

    @patch("xano_client.urlopen")
    def test_list_clientes_sends_bearer_token_and_reads_items(self, urlopen):
        urlopen.return_value = FakeResponse({"items": [{"id": 7, "nome": "Ana"}]})

        records = self.client.list_clientes()

        self.assertEqual(records, [{"id": 7, "nome": "Ana"}])
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://example.xano.io/api:group/cliente")
        self.assertEqual(request.headers["Authorization"], "Bearer test-token")

    @patch("xano_client.urlopen")
    def test_list_veiculos_filters_by_cliente(self, urlopen):
        urlopen.return_value = FakeResponse([])

        self.client.list_veiculos(12)

        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://example.xano.io/api:group/veiculo?cliente_id=12",
        )

    @patch("xano_client.urlopen")
    def test_create_cliente_sends_json_payload(self, urlopen):
        urlopen.return_value = FakeResponse({"id": 3})
        payload = {"nome": "Ana", "telefone": "11999990000"}

        result = self.client.create_cliente(payload)

        self.assertEqual(result, {"id": 3})
        request = urlopen.call_args.args[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.full_url, "https://example.xano.io/api:group/cliente")
        self.assertEqual(json.loads(request.data.decode("utf-8")), payload)

    @patch("xano_client.urlopen")
    def test_create_veiculo_posts_to_singular_route(self, urlopen):
        urlopen.return_value = FakeResponse({"id": 9})
        payload = {"cliente_id": 7, "placa": "ABC1D23", "modelo": "Civic"}

        result = self.client.create_veiculo(payload)

        self.assertEqual(result, {"id": 9})
        request = urlopen.call_args.args[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.full_url, "https://example.xano.io/api:group/veiculo")
        self.assertEqual(json.loads(request.data.decode("utf-8")), payload)

    def test_requires_base_url_and_token(self):
        with self.assertRaises(ValueError):
            XanoClient("", "test-token")
        with self.assertRaises(ValueError):
            XanoClient("https://example.xano.io/api:group", "")


if __name__ == "__main__":
    unittest.main()
