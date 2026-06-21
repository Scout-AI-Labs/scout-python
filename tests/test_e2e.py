"""End-to-end tests for the Scout Python SDK against a local mock server.

Uses only the standard library, so the suite runs with `python -m unittest`
and needs no third-party packages.
"""

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

import scout


class _Handler(BaseHTTPRequestHandler):
    flaky_hits = 0

    def log_message(self, *args):  # silence
        pass

    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("x-request-id", "req_abc123")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("content-length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        if self.path == "/v1/search":
            self._send(200, {
                "ok": True,
                "auth": self.headers.get("authorization"),
                "idem": self.headers.get("idempotency-key"),
                "echo": body,
            })
        elif self.path == "/v1/flaky":
            type(self).flaky_hits += 1
            if type(self).flaky_hits < 3:
                self._send(500, {"detail": "transient"})
            else:
                self._send(200, {"ok": True, "tries": type(self).flaky_hits})
        elif self.path == "/v1/nope":
            self._send(401, {"detail": "invalid api key"})
        else:
            self._send(404, {})

    def do_GET(self):
        self._send(200, {"items": [{"id": 1}], "path": self.path})


class EndToEndTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _Handler.flaky_hits = 0
        cls.server = HTTPServer(("127.0.0.1", 0), _Handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.client = scout.Scout(
            api_key="sk_live_xyz",
            base_url=f"http://127.0.0.1:{cls.port}",
            max_retries=3,
        )

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_post_round_trip_sends_auth_and_idempotency(self):
        res = self.client.search.create(["hello world"], depth="standard")
        self.assertTrue(res["ok"])
        self.assertEqual(res["auth"], "Bearer sk_live_xyz")
        self.assertTrue(res["idem"])
        self.assertEqual(res["echo"]["depth"], "standard")
        self.assertEqual(res["echo"]["queries"], ["hello world"])

    def test_get_encodes_query(self):
        res = self.client.search.list(limit=5)
        self.assertEqual(res["items"], [{"id": 1}])
        self.assertIn("limit=5", res["path"])

    def test_retries_on_500_then_succeeds(self):
        res = self.client.request("POST", "/v1/flaky", body={})
        self.assertTrue(res["ok"])
        self.assertEqual(res["tries"], 3)

    def test_401_maps_to_authentication_error(self):
        with self.assertRaises(scout.AuthenticationError) as ctx:
            self.client.request("POST", "/v1/nope", body={})
        err = ctx.exception
        self.assertEqual(err.status, 401)
        self.assertEqual(err.request_id, "req_abc123")
        self.assertIn("invalid api key", err.message)

    def test_pagination_iterates(self):
        items = list(self.client.search.iterate(limit=5))
        self.assertEqual(items, [{"id": 1}])


if __name__ == "__main__":
    unittest.main()
