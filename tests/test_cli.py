import contextlib
import io
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

import cli


class TestCLI(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.script_pt = os.path.join(self.temp_dir.name, "teste.ptpy")
        with open(self.script_pt, "w", encoding="utf-8") as f:
            f.write("mostre('ola mundo')\n")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_cli_sem_argumentos_retorna_erro_uso(self):
        """CLI sem argumentos imprime mensagem de uso e retorna 1."""
        stderr = io.StringIO()
        with patch.object(sys, "argv", ["cli.py"]), contextlib.redirect_stderr(stderr):
            status = cli.main()
        self.assertEqual(1, status)
        self.assertIn("Uso:", stderr.getvalue())

    def test_cli_executa_arquivo_padrao(self):
        """CLI executa o arquivo e retorna 0."""
        stdout = io.StringIO()
        with patch.object(sys, "argv", ["cli.py", self.script_pt]), contextlib.redirect_stdout(stdout):
            status = cli.main()
        self.assertEqual(0, status)
        self.assertIn("ola mundo", stdout.getvalue())

    def test_cli_exportar_para_stdout(self):
        """CLI com --exportar sem caminho imprime código Python canônico no stdout (AC-06)."""
        stdout = io.StringIO()
        with patch.object(sys, "argv", ["cli.py", self.script_pt, "--exportar"]), contextlib.redirect_stdout(stdout):
            status = cli.main()
        self.assertEqual(0, status)
        saida = stdout.getvalue()
        self.assertIn("print", saida)
        self.assertIn("'ola mundo'", saida)

    def test_cli_exportar_para_arquivo(self):
        """CLI com --exportar destino.py salva o código canônico no arquivo informado (AC-06)."""
        destino = os.path.join(self.temp_dir.name, "exportado.py")
        stdout = io.StringIO()
        with patch.object(sys, "argv", ["cli.py", self.script_pt, "--exportar", destino]), contextlib.redirect_stdout(stdout):
            status = cli.main()
        self.assertEqual(0, status)
        self.assertTrue(os.path.exists(destino))
        with open(destino, "r", encoding="utf-8") as f:
            conteudo = f.read()
        self.assertIn("print", conteudo)
        self.assertIn("'ola mundo'", conteudo)



    def test_cli_exportar_destino_invalido_retorna_erro_amigavel(self):
        """CLI com caminho de exportação inacessível reporta erro amigável sem traceback (AC-06)."""
        destino_invalido = "/caminho/completamente/inexistente/e/impossivel/script.py"
        stderr = io.StringIO()
        with patch.object(sys, "argv", ["cli.py", self.script_pt, "--exportar", destino_invalido]), contextlib.redirect_stderr(stderr):
            status = cli.main()
        self.assertEqual(1, status)
        self.assertIn("Não consegui salvar o arquivo exportado", stderr.getvalue())

    def test_cli_modo_lado_a_lado(self):
        """CLI com --lado-a-lado exibe visualização comparativa antes da execução (AC-05)."""
        stdout = io.StringIO()
        with patch.object(sys, "argv", ["cli.py", self.script_pt, "--lado-a-lado"]), contextlib.redirect_stdout(stdout):
            status = cli.main()
        self.assertEqual(0, status)
        saida = stdout.getvalue()
        self.assertIn("Português", saida)
        self.assertIn("Python Canônico", saida)
        self.assertIn("ola mundo", saida)

    def test_cli_modo_transicao_alias(self):
        """CLI com alias --modo-transicao exibe visualização comparativa (AC-05)."""
        stdout = io.StringIO()
        with patch.object(sys, "argv", ["cli.py", self.script_pt, "--modo-transicao"]), contextlib.redirect_stdout(stdout):
            status = cli.main()
        self.assertEqual(0, status)
        saida = stdout.getvalue()

        self.assertIn("Português", saida)
        self.assertIn("Python Canônico", saida)



if __name__ == "__main__":
    unittest.main()
