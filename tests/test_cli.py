import contextlib
import io
import os
import subprocess
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

    def test_cli_exibe_ajuda(self):
        """A CLI oferece ajuda sem exigir arquivo de entrada."""
        stdout = io.StringIO()
        with patch.object(sys, "argv", ["cli.py", "--help"]), contextlib.redirect_stdout(stdout):
            status = cli.main()
        self.assertEqual(0, status)
        self.assertIn("portupy", stdout.getvalue())
        self.assertIn("--exportar", stdout.getvalue())

    def test_cli_exibe_versao(self):
        """A versão pública do pacote pode ser consultada pela CLI."""
        stdout = io.StringIO()
        with patch.object(sys, "argv", ["cli.py", "--version"]), contextlib.redirect_stdout(stdout):
            status = cli.main()
        self.assertEqual(0, status)
        self.assertIn("portupy 0.1.0", stdout.getvalue())

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

        processo = subprocess.run(
            [sys.executable, destino],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, processo.returncode)
        self.assertEqual("ola mundo\n", processo.stdout)



    def test_cli_exportar_destino_invalido_retorna_erro_amigavel(self):
        """CLI com caminho de exportação inacessível reporta erro amigável sem traceback (AC-06)."""
        destino_invalido = "/caminho/completamente/inexistente/e/impossivel/script.py"
        stderr = io.StringIO()
        with patch.object(sys, "argv", ["cli.py", self.script_pt, "--exportar", destino_invalido]), contextlib.redirect_stderr(stderr):
            status = cli.main()
        self.assertEqual(1, status)
        self.assertIn("Não consegui salvar o arquivo exportado", stderr.getvalue())

    def test_cli_exportar_arquivo_com_encoding_invalido_retorna_erro_amigavel(self):
        """CLI não despeja traceback quando o arquivo não é UTF-8 válido."""
        caminho_invalido = os.path.join(self.temp_dir.name, "invalido.ptpy")
        with open(caminho_invalido, "wb") as f:
            f.write(b"mostre('\xff')\n")

        stderr = io.StringIO()
        with patch.object(
            sys,
            "argv",
            ["cli.py", caminho_invalido, "--exportar"],
        ), contextlib.redirect_stderr(stderr):
            status = cli.main()

        self.assertEqual(1, status)
        self.assertIn("Não consegui ler o arquivo", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

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

    def test_cli_web_padrao(self):
        """CLI com --web chama inicia_servidor_web na porta padrão 8000 (AC-07)."""
        with patch("cli.inicia_servidor_web") as mock_inicia:
            with patch.object(sys, "argv", ["cli.py", "--web"]):
                status = cli.main()
        self.assertEqual(0, status)
        mock_inicia.assert_called_once()
        self.assertEqual(8000, mock_inicia.call_args.kwargs.get("porta"))

    def test_cli_web_porta_customizada(self):
        """CLI com --web 9000 passa porta customizada (AC-07)."""
        with patch("cli.inicia_servidor_web") as mock_inicia:
            with patch.object(sys, "argv", ["cli.py", "--web", "9000"]):
                status = cli.main()
        self.assertEqual(0, status)
        mock_inicia.assert_called_once()
        self.assertEqual(9000, mock_inicia.call_args.kwargs.get("porta"))

    def test_cli_web_sem_navegador(self):
        """A CLI permite iniciar o playground em ambiente sem interface gráfica."""
        with patch("cli.inicia_servidor_web") as mock_inicia:
            with patch.object(sys, "argv", ["cli.py", "--web", "--sem-navegador"]):
                status = cli.main()
        self.assertEqual(0, status)
        mock_inicia.assert_called_once()
        self.assertFalse(mock_inicia.call_args.kwargs.get("abrir_navegador"))

    def test_cli_web_porta_invalida(self):
        """CLI com porta inválida exibe erro amigável em stderr e retorna 1 (AC-07)."""
        stderr = io.StringIO()
        with patch.object(sys, "argv", ["cli.py", "--web", "porta_invalida"]), contextlib.redirect_stderr(stderr):
            status = cli.main()
        self.assertEqual(1, status)
        self.assertIn("porta inválida", stderr.getvalue())

    def test_cli_flag_desconhecida_retorna_erro_de_uso(self):
        """Flags desconhecidas não são ignoradas silenciosamente."""
        stderr = io.StringIO()
        with patch.object(sys, "argv", ["cli.py", "--nao-existe"]), contextlib.redirect_stderr(stderr):
            status = cli.main()
        self.assertEqual(1, status)
        self.assertIn("unrecognized arguments", stderr.getvalue())

    def test_cli_sem_navegador_exige_modo_web(self):
        """A opção operacional não deve ser aceita silenciosamente no modo de arquivo."""
        stderr = io.StringIO()
        with patch.object(sys, "argv", ["cli.py", self.script_pt, "--sem-navegador"]), contextlib.redirect_stderr(stderr):
            status = cli.main()
        self.assertEqual(1, status)
        self.assertIn("só pode ser usado com --web", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
