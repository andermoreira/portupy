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

    def test_executa_codigo_aponta_chamada_quando_sintaxe_falha_em_outra_fonte(self):
        codigo = (
            "fonte = 'x = 1\\nif True'\n"
            "arquivo = 'outro.py'\n"
            "compile(fonte, arquivo, 'exec')\n"
        )
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            status = executa_codigo(codigo)
        self.assertEqual(1, status)
        self.assertIn("Na linha 3: compile(fonte, arquivo, 'exec')", stderr.getvalue())
        self.assertNotIn("^", stderr.getvalue())

    def test_executa_codigo_isola_flags_de_anotacoes_do_executor(self):
        codigo = (
            "funcao exemplo() -> int:\n"
            "    passe\n"
            "mostre(exemplo.__annotations__['return'] is int)\n"
        )
        for futuro, esperado in (("", "True\n"), ("de __future__ importe annotations\n", "False\n")):
            with self.subTest(futuro=futuro):
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    status = executa_codigo(futuro + codigo)
                self.assertEqual(0, status)
                self.assertEqual(esperado, stdout.getvalue())

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


class TestMensagensParaIniciantes(unittest.TestCase):
    """Common beginner mistakes must be explained in Portuguese, never raw."""

    def _erro(self, codigo_pt):
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            status = executa_codigo(codigo_pt)
        self.assertEqual(1, status)
        saida = f.getvalue()
        self.assertNotIn("ainda sem tradução", saida)
        self.assertNotIn("Traceback", saida)
        return saida

    def test_parentese_nao_fechado_aponta_a_linha_de_abertura(self):
        saida = self._erro("x = 1\nmostre((1)\ny = 2\n")
        self.assertIn("linha 2", saida)
        self.assertIn("'('", saida)
        self.assertNotIn("unexpected EOF", saida)

    def test_aspas_nao_fechadas_tem_prioridade_sobre_parentese(self):
        saida = self._erro('mostre("abc\n')
        self.assertIn("aspas", saida)
        self.assertNotIn("'('", saida)

    def test_continuacao_de_linha_no_fim_nao_culpa_aspas(self):
        saida = self._erro("x = 1 + \\\n")
        self.assertNotIn("aspas", saida)

    def test_anotacao_em_palavra_de_condicao_continua_reservada(self):
        saida = self._erro("se: inteiro = 1\n")
        self.assertIn("palavra reservada", saida)

    def test_atribuicao_no_lugar_de_comparacao_em_condicao(self):
        for codigo_pt in ("x = 1\nse x = 1:\n    passe\n", "x = 1\nenquanto x = 1:\n    passe\n"):
            with self.subTest(codigo_pt=codigo_pt):
                saida = self._erro(codigo_pt)
                self.assertIn("==", saida)
                self.assertNotIn("nome de variável", saida)

    def test_recuo_inesperado(self):
        saida = self._erro("x = 1\n    y = 2\n")
        self.assertIn("recuo", saida)

    def test_operacao_entre_tipos_incompativeis(self):
        saida = self._erro('x = "a" - 1\n')
        self.assertIn("str", saida)
        self.assertIn("int", saida)

    def test_nome_parecido_com_builtin_sugere_correcao(self):
        saida = self._erro('mostrar("oi")\n')
        self.assertRegex(saida, r"Você quis dizer 'mostr[ae]'\?")

    def test_interrupcao_pelo_teclado_encerra_sem_traceback(self):
        from unittest import mock
        f = io.StringIO()
        with mock.patch("builtins.exec", side_effect=KeyboardInterrupt), contextlib.redirect_stderr(f):
            status = executa_codigo("mostre(1)\n")
        self.assertEqual(130, status)
        self.assertIn("interrompido", f.getvalue())


if __name__ == "__main__":
    unittest.main()
