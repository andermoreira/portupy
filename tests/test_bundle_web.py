import json
import re
import tempfile
import unittest
from pathlib import Path

from transpilador_pt.bundle_web import ARQUIVOS_MODULO, gera_bundle_web


class TestBundleWeb(unittest.TestCase):

    def test_bundle_reproduz_fontes_atuais_do_modulo(self):
        """O payload Web deve permanecer sincronizado com o pacote Python."""
        with tempfile.TemporaryDirectory() as diretorio_temp:
            caminho_bundle = gera_bundle_web(Path(diretorio_temp) / "bundle.js")
            conteudo = caminho_bundle.read_text(encoding="utf-8")

        correspondencia = re.search(
            r"window\.TRANSPILADOR_PT_SOURCES = (.*);\s*$",
            conteudo,
            re.DOTALL,
        )
        self.assertIsNotNone(correspondencia)
        fontes_bundle = json.loads(correspondencia.group(1))
        pasta_modulo = Path(__file__).resolve().parent.parent / "transpilador_pt"

        self.assertEqual(set(ARQUIVOS_MODULO), set(fontes_bundle))
        for nome_arquivo in ARQUIVOS_MODULO:
            fonte_atual = (pasta_modulo / nome_arquivo).read_text(encoding="utf-8")
            self.assertEqual(fonte_atual, fontes_bundle[nome_arquivo])

    def test_shell_web_referencia_arquivos_necessarios(self):
        """O HTML deve apontar para o runtime local e o Service Worker."""
        pasta_web = Path(__file__).resolve().parent.parent / "web"
        html = (pasta_web / "index.html").read_text(encoding="utf-8")
        app = (pasta_web / "app.js").read_text(encoding="utf-8")

        for nome_arquivo in (
            "app.js",
            "bundle_pt.js",
            "pyodide-worker.js",
            "service-worker.js",
        ):
            self.assertTrue((pasta_web / nome_arquivo).is_file())
            self.assertIn(nome_arquivo, html + app)

        self.assertIn('id="syntax-highlight"', html)
        self.assertIn("atualizaSyntaxHighlight", app)


if __name__ == "__main__":
    unittest.main()
