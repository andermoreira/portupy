import hashlib
import json
import unittest
from pathlib import Path


class TestWebAssets(unittest.TestCase):

    def setUp(self):
        self.pasta_projeto = Path(__file__).resolve().parent.parent
        self.pasta_web = self.pasta_projeto / "web"
        self.manifest_path = self.pasta_web / "vendor" / "pyodide" / "manifest.json"
        self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def test_assets_pyodide_locais_correspondem_ao_manifesto(self):
        for arquivo in self.manifest["files"]:
            caminho = self.manifest_path.parent / arquivo["path"]
            self.assertTrue(caminho.is_file(), caminho)
            conteudo = caminho.read_bytes()
            self.assertEqual(arquivo["bytes"], len(conteudo), caminho)
            self.assertEqual(
                arquivo["sha256"],
                hashlib.sha256(conteudo).hexdigest(),
                caminho,
            )

    def test_playground_nao_depende_de_cdn_para_o_runtime(self):
        html = (self.pasta_web / "index.html").read_text(encoding="utf-8")
        worker = (self.pasta_web / "pyodide-worker.js").read_text(encoding="utf-8")
        service_worker = (self.pasta_web / "service-worker.js").read_text(encoding="utf-8")

        self.assertNotIn("cdn.jsdelivr.net", html)
        self.assertNotIn("cdn.jsdelivr.net", worker)
        self.assertNotIn("cdn.jsdelivr.net", service_worker)
        self.assertIn("vendor/pyodide/v0.26.4/full/", worker)
        self.assertIn("python_stdlib.zip", service_worker)

    def test_service_worker_embute_hashes_do_manifesto(self):
        from portupy.bundle_web import PREFIXO_PATH_PYODIDE

        service_worker = (self.pasta_web / "service-worker.js").read_text(encoding="utf-8")
        self.assertIn("crypto.subtle.digest", service_worker)
        self.assertIn("PYODIDE_INTEGRITY", service_worker)
        for arquivo in self.manifest["files"]:
            self.assertIn(PREFIXO_PATH_PYODIDE + arquivo["path"], service_worker)
            self.assertIn(arquivo["sha256"], service_worker)

    def test_worker_restringe_cache_storage_apos_inicializar(self):
        worker = (self.pasta_web / "pyodide-worker.js").read_text(encoding="utf-8")
        self.assertIn("restringeApisPersistentesDoWorker", worker)
        self.assertIn("importScriptsBloqueado", worker)


if __name__ == "__main__":
    unittest.main()
