import contextlib
import io
import unittest

from transpilador_pt.executor import executa_codigo, executa_arquivo


class TestExecutor(unittest.TestCase):

    def test_executa_codigo_sucesso(self):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            executa_codigo('mostre("Ola, Mundo!")')
        self.assertIn("Ola, Mundo!", f.getvalue())

    def test_executa_codigo_com_erro_runtime(self):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            executa_codigo("mostre(1 / 0)")
        saida = f.getvalue()
        self.assertIn("ZeroDivisionError", saida)
        self.assertIn("dividir um número por zero", saida)

    def test_executa_codigo_fstring_com_builtin(self):
        """Valida que funções embutidas funcionam dentro de f-strings (ADR-001)."""
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            executa_codigo('nomes = ["Ana", "Bruno"]\nmostre(f"Total: {tamanho(nomes)}")')
        saida = f.getvalue()
        self.assertNotIn("NameError", saida)
        self.assertIn("Total: 2", saida)

    def test_arquivo_exemplo_ola(self):
        """Valida a execução completa do script oficial ola.ptpy com f-string."""
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            executa_arquivo("transpilador_pt/exemplos/ola.ptpy")
        saida = f.getvalue()
        self.assertNotIn("NameError", saida)
        self.assertIn("Total de nomes: 3", saida)


if __name__ == "__main__":
    unittest.main()
