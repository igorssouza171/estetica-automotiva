import json
import unittest
from unittest.mock import MagicMock, patch

from xano_client import XANO_GET_CACHE_TTL_SECONDS, XanoAPIError, XanoClient


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
        XanoClient.clear_read_cache()
        self.client = XanoClient("https://example.xano.io/api:group", "test-token")

    def test_get_cache_ttl_is_60_seconds(self):
        self.assertEqual(XANO_GET_CACHE_TTL_SECONDS, 60)

    @patch("xano_client.urlopen")
    def test_list_clientes_sends_bearer_token_and_reads_items(self, urlopen):
        urlopen.return_value = FakeResponse({"items": [{"id": 7, "nome": "Ana"}]})

        records = self.client.list_clientes()

        self.assertEqual(records, [{"id": 7, "nome": "Ana"}])
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://example.xano.io/api:group/cliente")
        self.assertEqual(request.headers["Authorization"], "Bearer test-token")

    @patch("xano_client.urlopen")
    def test_get_cache_is_shared_between_client_instances(self, urlopen):
        urlopen.return_value = FakeResponse([{"id": 7, "nome": "Ana"}])

        first_result = self.client.list_clientes()
        second_client = XanoClient("https://example.xano.io/api:group", "test-token")
        second_result = second_client.list_clientes()

        self.assertEqual(first_result, second_result)
        self.assertEqual(urlopen.call_count, 1)

    @patch("xano_client.urlopen")
    def test_post_invalidates_only_matching_resource_cache(self, urlopen):
        urlopen.side_effect = [
            FakeResponse([{"id": 7, "nome": "Ana"}]),
            FakeResponse({"id": 8}),
            FakeResponse([{"id": 7, "nome": "Ana"}, {"id": 8, "nome": "Bia"}]),
        ]

        self.client.list_clientes()
        self.client.create_cliente({"nome": "Bia", "telefone": "11999990000"})
        records = self.client.list_clientes()

        self.assertEqual([record["nome"] for record in records], ["Ana", "Bia"])
        self.assertEqual(urlopen.call_count, 3)

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

    @patch("xano_client.urlopen")
    def test_list_servicos_uses_singular_route(self, urlopen):
        urlopen.return_value = FakeResponse(
            {"items": [{"id": 15, "nome": "Lavagem", "tempo_estimado_min": "60"}]}
        )

        records = self.client.list_servicos()

        self.assertEqual(
            records,
            [{"id": 15, "nome": "Lavagem", "tempo_estimado_min": 60}],
        )
        request = urlopen.call_args.args[0]
        self.assertEqual(request.method, "GET")
        self.assertEqual(request.full_url, "https://example.xano.io/api:group/servico")

    @patch("xano_client.urlopen")
    def test_create_servico_posts_payload_to_singular_route(self, urlopen):
        urlopen.return_value = FakeResponse({"id": 15})
        payload = {"nome": "Lavagem", "preco_base": 89.9, "tempo_estimado_min": "60"}

        result = self.client.create_servico(payload)

        self.assertEqual(result, {"id": 15})
        request = urlopen.call_args.args[0]
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.full_url, "https://example.xano.io/api:group/servico")
        self.assertEqual(
            json.loads(request.data.decode("utf-8")),
            {"nome": "Lavagem", "preco_base": 89.9, "tempo_estimado_min": 60},
        )

    @patch("xano_client.urlopen")
    def test_list_ordens_servico_uses_list_endpoint(self, urlopen):
        urlopen.return_value = FakeResponse({"items": [{"id": 25, "status": "Aguardando"}]})

        records = self.client.list_ordens_servico()

        self.assertEqual(records, [{"id": 25, "status": "Aguardando"}])
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(request.full_url, "https://example.xano.io/api:group/ordem_servico")

    @patch("xano_client.urlopen")
    def test_list_itens_ordem_servico_filters_by_order(self, urlopen):
        urlopen.return_value = FakeResponse([{"servico_id": 15}])

        records = self.client.list_itens_ordem_servico(25)

        self.assertEqual(records, [{"servico_id": 15}])
        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://example.xano.io/api:group/item_ordem_servico?ordem_servico_id=25",
        )

    @patch("xano_client.requests.post")
    def test_atualizar_total_os_posts_order_id(self, post):
        response = MagicMock()
        response.json.return_value = {"id": 25, "valor_total": 89.9}
        post.return_value = response

        result = self.client.atualizar_total_os(25)

        self.assertEqual(result, {"id": 25, "valor_total": 89.9})
        post.assert_called_once_with(
            "https://example.xano.io/api:group/atualizar_total_os",
            json={"ordem_servico_id": 25},
            headers=self.client.headers,
            timeout=15.0,
        )
        response.raise_for_status.assert_called_once()

    @patch("xano_client.requests.post")
    def test_criar_ordem_servico_posts_order(self, post):
        response = MagicMock()
        response.json.return_value = {"id": 25, "status": "Aguardando"}
        post.return_value = response

        result = self.client.criar_ordem_servico(10, 20, 129.9, "Observação")

        self.assertEqual(result, {"id": 25, "status": "Aguardando"})
        post.assert_called_once_with(
            "https://example.xano.io/api:group/ordem_servico",
            json={
                "cliente_id": 10,
                "veiculo_id": 20,
                "status": "Aguardando",
                "valor_total": 129.9,
                "observacoes": "Observação",
            },
            headers=self.client.headers,
            timeout=15.0,
        )
        response.raise_for_status.assert_called_once()

    @patch("xano_client.requests.post")
    def test_adicionar_item_ordem_servico_posts_item(self, post):
        response = MagicMock()
        response.json.return_value = {"id": 101}
        post.return_value = response

        result = self.client.adicionar_item_ordem_servico(25, 15, 89.9)

        self.assertEqual(result, {"id": 101})
        post.assert_called_once_with(
            "https://example.xano.io/api:group/item_ordem_servico",
            json={"ordem_servico_id": 25, "servico_id": 15, "preco_unitario": 89.9},
            headers=self.client.headers,
            timeout=15.0,
        )
        response.raise_for_status.assert_called_once()

    @patch("xano_client.requests.post")
    def test_criar_ordem_servico_uses_custom_status_and_default_observacoes(self, post):
        response = MagicMock()
        response.json.return_value = {"id": 25, "status": "Em Andamento"}
        post.return_value = response

        self.client.criar_ordem_servico(10, 20, 129.9, status="Em Andamento")

        self.assertEqual(
            post.call_args.kwargs["json"],
            {
                "cliente_id": 10,
                "veiculo_id": 20,
                "status": "Em Andamento",
                "valor_total": 129.9,
                "observacoes": "",
            },
        )

    @patch("xano_client.urlopen")
    def test_adicionar_item_ordem_servico_rejects_non_scalar_ids(self, urlopen):
        with self.assertRaisesRegex(XanoAPIError, "servico_id deve conter IDs inteiros"):
            self.client.adicionar_item_ordem_servico(25, [15], 10)

        urlopen.assert_not_called()

    @patch("xano_client.requests.post")
    def test_criar_ordem_servico_rejects_fractional_ids(self, post):
        with self.assertRaisesRegex(XanoAPIError, "cliente_id deve conter IDs inteiros"):
            self.client.criar_ordem_servico(10.5, 20, 10)

        post.assert_not_called()

    @patch("xano_client.urlopen")
    def test_update_ordem_servico_status_uses_status_endpoint(self, urlopen):
        urlopen.return_value = FakeResponse({"id": 25, "status": "Em Andamento"})

        result = self.client.update_ordem_servico_status(25, "Em Andamento")

        self.assertEqual(result, {"id": 25, "status": "Em Andamento"})
        request = urlopen.call_args.args[0]
        self.assertEqual(request.get_method(), "PATCH")
        self.assertEqual(
            request.full_url,
            "https://example.xano.io/api:group/ordem_servico/25",
        )
        self.assertEqual(json.loads(request.data.decode("utf-8")), {"status": "Em Andamento"})

    def test_error_message_preserves_plain_xano_text(self):
        self.assertEqual(
            XanoClient._error_message("Unable to locate request.", 404),
            "Unable to locate request.",
        )

    @patch("xano_client.urlopen")
    def test_patch_invalidates_order_list_cache(self, urlopen):
        urlopen.side_effect = [
            FakeResponse([{"id": 25, "status": "Aguardando"}]),
            FakeResponse({"id": 25, "status": "Em Andamento"}),
            FakeResponse([{"id": 25, "status": "Em Andamento"}]),
        ]

        self.client.list_ordens_servico()
        self.client.update_ordem_servico_status(25, "Em Andamento")
        records = self.client.list_ordens_servico()

        self.assertEqual(records, [{"id": 25, "status": "Em Andamento"}])
        self.assertEqual(urlopen.call_count, 3)

    def test_requires_base_url_and_token(self):
        with self.assertRaises(ValueError):
            XanoClient("", "test-token")
        with self.assertRaises(ValueError):
            XanoClient("https://example.xano.io/api:group", "")


if __name__ == "__main__":
    unittest.main()
