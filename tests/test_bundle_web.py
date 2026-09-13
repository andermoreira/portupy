import json
import re
import tempfile
import unittest
from pathlib import Path

from portupy.bundle_web import ARQUIVOS_EXEMPLOS, ARQUIVOS_MODULO, gera_bundle_web


class TestBundleWeb(unittest.TestCase):

    def test_bundle_reproduz_fontes_atuais_do_modulo(self):
        """O payload Web deve permanecer sincronizado com o pacote Python."""
        with tempfile.TemporaryDirectory() as diretorio_temp:
            caminho_bundle = gera_bundle_web(Path(diretorio_temp) / "bundle.js")
            conteudo = caminho_bundle.read_text(encoding="utf-8")

        def extrai_bloco(nome_variavel: str) -> str:
            # Cada bloco termina em ';' seguido de nova linha e da próxima
            # atribuição 'window.' (ou do fim do arquivo). Ancorar assim mantém
            # o parsing robusto à adição de novos blocos ao bundle.
            correspondencia = re.search(
                rf"window\.{nome_variavel} = (.*?);\n(?:window\.|\Z)",
                conteudo,
                re.DOTALL,
            )
            self.assertIsNotNone(
                correspondencia, f"bloco {nome_variavel} não encontrado no bundle"
            )
            return correspondencia.group(1)

        fontes_bundle = json.loads(extrai_bloco("PORTUPY_SOURCES"))
        exemplos_bundle = json.loads(extrai_bloco("PORTUPY_EXEMPLOS"))
        pasta_modulo = Path(__file__).resolve().parent.parent / "portupy"

        self.assertEqual(set(ARQUIVOS_MODULO), set(fontes_bundle))
        for nome_arquivo in ARQUIVOS_MODULO:
            fonte_atual = (pasta_modulo / nome_arquivo).read_text(encoding="utf-8")
            self.assertEqual(fonte_atual, fontes_bundle[nome_arquivo])

        self.assertEqual(
            {Path(nome).stem for nome in ARQUIVOS_EXEMPLOS},
            set(exemplos_bundle),
        )
        for nome_arquivo in ARQUIVOS_EXEMPLOS:
            exemplo_atual = (pasta_modulo / "exemplos" / nome_arquivo).read_text(encoding="utf-8")
            self.assertEqual(exemplo_atual, exemplos_bundle[Path(nome_arquivo).stem])

        # Os grupos de realce expostos ao playground devem refletir a fonte única.
        from portupy.dicionario import conjuntos_de_destaque

        destaque_bundle = json.loads(extrai_bloco("PORTUPY_DESTAQUE"))
        self.assertEqual(conjuntos_de_destaque(), destaque_bundle)

    def test_bundle_versionado_esta_atualizado(self):
        """O artefato versionado deve ser exatamente o bundle que o gerador produz."""
        pasta_projeto = Path(__file__).resolve().parent.parent
        bundle_versionado = pasta_projeto / "web" / "bundle_pt.js"

        with tempfile.TemporaryDirectory() as diretorio_temp:
            bundle_gerado = gera_bundle_web(Path(diretorio_temp) / "bundle.js")
            self.assertEqual(bundle_gerado.read_bytes(), bundle_versionado.read_bytes())

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
        self.assertIn('id="btn-tentar-novamente"', html)
        self.assertIn("copiaTexto", app)
        self.assertIn("botoesAbas", app)


if __name__ == "__main__":
    unittest.main()
