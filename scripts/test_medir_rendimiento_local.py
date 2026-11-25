"""Barreras del medidor: HTTP sintético en loopback, sin bases de datos."""
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

import medir_rendimiento_local as measurement


class MeasurementBoundariesTests(unittest.TestCase):
    def test_redirect_size_and_route_guards_do_not_expand_the_sample(self):
        seen = []

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_GET(self):
                seen.append(self.path)
                if self.path.endswith("?exceso=1"):
                    body = b"x" * (1024 * 1024 + 1)
                    self.send_response(200)
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    self.send_response(302)
                    self.send_header("Location", "/destino-que-no-debe-consultarse")
                    self.send_header("Content-Length", "0")
                    self.end_headers()

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            with patch.object(measurement, "BASE", f"http://127.0.0.1:{server.server_port}"):
                with self.assertRaisesRegex(ValueError, "redirecciones"):
                    measurement.get("/api/reportes/publicos/")
                self.assertEqual(seen, ["/api/reportes/publicos/"])
                with self.assertRaisesRegex(ValueError, "1 MiB"):
                    measurement.get("/api/reportes/publicos/?exceso=1")
                for path in ("https://example.invalid/", "/api/seguridad/", "/api/reportes/publicos/../privado/"):
                    with self.assertRaisesRegex(ValueError, "fuera del ensayo"):
                        measurement.get(path)
                self.assertEqual(len(seen), 2)
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
