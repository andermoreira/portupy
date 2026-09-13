import contextlib
import io
import unittest
from pathlib import Path

from portupy.executor import executa_codigo, executa_arquivo


class TestExecutor(unittest.TestCase):

    def test_executa_codigo_sucesso(self):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            status = executa_codigo('mostre("Ola, Mundo!")')
        self.assertEqual(0, status)
        self.assertIn("Ola, Mundo!", f.getvalue())

    def test_executa_codigo_com_erro_runtime(self):
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            status = executa_codigo("mostre(1 / 0)")
        self.assertEqual(1, status)
        saida = f.getvalue()
        self.assertIn("ZeroDivisionError", saida)
        self.assertIn("dividir um número por zero", saida)

    def test_executa_codigo_fstring_com_builtin(self):
        """Valida que funções embutidas funcionam dentro de f-strings (ADR-001)."""
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            status = executa_codigo('nomes = ["Ana", "Bruno"]\nmostre(f"Total: {tamanho(nomes)}")')
        self.assertEqual(0, status)
        saida = f.getvalue()
        self.assertNotIn("NameError", saida)
        self.assertIn("Total: 2", saida)

    def test_arquivo_exemplo_ola(self):
        """Valida a execução completa do script oficial ola.ptpy com f-string."""
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            status = executa_arquivo("portupy/exemplos/ola.ptpy")
        self.assertEqual(0, status)
        saida = f.getvalue()
        self.assertNotIn("NameError", saida)
        self.assertIn("Total de nomes: 3", saida)

    def test_arquivo_exemplo_condicionais(self):
        """Valida a execução completa do script exemplo condicionais.ptpy."""
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            status = executa_arquivo("portupy/exemplos/condicionais.ptpy")
        self.assertEqual(0, status)
        saida = f.getvalue()
        self.assertIn("Excelente (gabaritou!)", saida)
        self.assertIn("Nota ausente", saida)
        self.assertIn("Acesso liberado para: Ana", saida)

    def test_executa_codigo_com_erro_de_tokenizacao(self):
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            status = executa_codigo('mostre("texto sem fechar\n')
        self.assertEqual(1, status)
        self.assertIn("Erro ao traduzir", f.getvalue())

    def test_executa_codigo_com_erro_de_sintaxe(self):
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            status = executa_codigo("se verdadeiro\n    passe\n")
        self.assertEqual(1, status)
        self.assertIn("Na linha 1: se verdadeiro", f.getvalue())
        self.assertNotIn("Traceback", f.getvalue())

    def test_executa_arquivo_inexistente(self):
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            status = executa_arquivo("arquivo-que-nao-existe.ptpy")
        self.assertEqual(1, status)
        self.assertIn("Não consegui ler o arquivo", f.getvalue())

    def test_executa_codigo_senao_se_encadeado(self):
        """Valida execução de múltiplos ramos com senao se."""
        codigo = (
            "x = 0\n"
            "se x > 0:\n"
            "    mostre('positivo')\n"
            "senao se x < 0:\n"
            "    mostre('negativo')\n"
            "senao:\n"
            "    mostre('zero')\n"
        )
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            status = executa_codigo(codigo)
        self.assertEqual(0, status)
        self.assertEqual("zero\n", f.getvalue())

    def test_executa_codigo_operadores_compostos_eh_e_nao(self):
        """Valida execução de eh/é contextual, nao eh e nao em."""
        codigo = (
            "nome = 'Ana'\n"
            "se nome eh 'Ana':\n"
            "    mostre('eh Ana')\n"
            "se nome nao eh 'Bruno':\n"
            "    mostre('nao eh Bruno')\n"
            "v = nulo\n"
            "se v eh nulo:\n"
            "    mostre('v eh nulo')\n"
            "itens = [1, 2]\n"
            "se 3 nao em itens:\n"
            "    mostre('3 nao em itens')\n"
        )
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            status = executa_codigo(codigo)
        self.assertEqual(0, status)
        self.assertIn("eh Ana", f.getvalue())
        self.assertIn("nao eh Bruno", f.getvalue())
        self.assertIn("v eh nulo", f.getvalue())
        self.assertIn("3 nao em itens", f.getvalue())

    def test_executa_codigo_com_defaults_e_argumentos_nomeados(self):
        """Valida defaults e argumentos nomeados em estruturas traduzidas."""
        codigo = (
            "funcao valida(valor=1):\n"
            "    retorne valor\n"
            "se valida(valor=1) eh 1:\n"
            "    mostre('funciona')\n"
            "senao se valida(valor=2) eh 2:\n"
            "    mostre('falhou')\n"
        )
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            status = executa_codigo(codigo)
        self.assertEqual(0, status)
        self.assertEqual("funciona\n", f.getvalue())

    def test_executa_codigo_literais_em_fstring(self):
        """Keywords inside f-strings must resolve at runtime on every supported Python."""
        codigo = 'mostre(f"{nulo}")\nmostre(f"{verdadeiro}")\nmostre(f"{falso}")\n'
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = executa_codigo(codigo)
        self.assertEqual(0, status, stderr.getvalue())
        self.assertEqual("None\nTrue\nFalse\n", stdout.getvalue())

    def test_todos_os_arquivos_de_exemplo(self):
        pasta = Path(__file__).resolve().parent.parent / "portupy" / "exemplos"
        esperam_erro = {"erro.ptpy", "erro_sintaxe.ptpy"}
        for caminho in sorted(pasta.glob("*.ptpy")):
            with self.subTest(exemplo=caminho.name):
                stdout = io.StringIO()
                stderr = io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    status = executa_arquivo(str(caminho))
                if caminho.name in esperam_erro:
                    self.assertEqual(1, status, stderr.getvalue())
                    self.assertNotIn("Traceback", stderr.getvalue())
                else:
                    self.assertEqual(0, status, stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
