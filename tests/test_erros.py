import unittest

from transpilador_pt.erros import formata_erro_amigavel, traduz_excecao


class TestErros(unittest.TestCase):

    def test_traduz_excecao_index_error(self):
        try:
            [][0]
        except IndexError as exc:
            traducao = traduz_excecao(exc)
            self.assertIsNotNone(traducao)
            self.assertIn("posição que não existe", traducao)

    def test_traduz_excecao_name_error(self):
        try:
            variavel_inexistente_xyz  # noqa: F821
        except NameError as exc:
            traducao = traduz_excecao(exc)
            self.assertIsNotNone(traducao)
            self.assertIn("usada antes de existir", traducao)

    def test_traduz_excecao_comparacao_incompativel(self):
        traducao = traduz_excecao(
            TypeError("'>=' not supported between instances of 'str' and 'int'")
        )
        self.assertIsNotNone(traducao)
        self.assertIn("tipos str e int não são compatíveis", traducao)

    def test_traduz_excecao_tamanho_de_tipo_invalido(self):
        traducao = traduz_excecao(TypeError("object of type 'int' has no len()"))
        self.assertIsNotNone(traducao)
        self.assertIn("não possui tamanho", traducao)

    def test_traduz_excecao_chamada_de_valor(self):
        traducao = traduz_excecao(TypeError("'int' object is not callable"))
        self.assertIsNotNone(traducao)
        self.assertIn("como se fosse uma função", traducao)

    def test_traduz_excecao_argumentos_no_plural(self):
        traducao = traduz_excecao(
            TypeError("funcao() missing 2 required positional arguments: 'a' and 'b'")
        )
        self.assertIsNotNone(traducao)
        self.assertIn("2 argumento(s)", traducao)

    def test_traduz_excecao_variavel_local_sem_valor(self):
        traducao = traduz_excecao(
            UnboundLocalError("cannot access local variable 'total' where it is not associated with a value")
        )
        self.assertIsNotNone(traducao)
        self.assertIn("receber um valor", traducao)

    def test_traduz_excecao_sintaxe_com_doispontos(self):
        traducao = traduz_excecao(SyntaxError("expected ':'"))
        self.assertIsNotNone(traducao)
        self.assertIn("dois pontos", traducao)

    def test_traduz_excecao_modulo_com_subpacote(self):
        traducao = traduz_excecao(
            ModuleNotFoundError("No module named 'pacote.interno.modulo'")
        )
        self.assertIsNotNone(traducao)
        self.assertIn("pacote.interno.modulo", traducao)

    def test_formata_erro_amigavel_runtime_com_linha(self):
        try:
            compilado = compile("1 / 0", "<codigo_pt>", "exec")
            exec(compilado, {})
        except Exception as exc:
            mensagem = formata_erro_amigavel(exc, ["1 / 0"])
            self.assertIn("Na linha 1: 1 / 0", mensagem)
            self.assertIn("dividir um número por zero", mensagem)

    def test_formata_erro_syntax_error(self):
        """Valida que SyntaxError exibe a linha, o trecho e explicação em português."""
        try:
            compile("se x > 0", "<codigo_pt>", "exec")
        except SyntaxError as exc:
            mensagem = formata_erro_amigavel(exc, ["se x > 0"])
            self.assertIn("Na linha 1: se x > 0", mensagem)
            self.assertIn("Erro de escrita no código", mensagem)
            self.assertNotIn("ainda sem tradução", mensagem)

    def test_formata_erro_mapeia_coluna_do_codigo_traduzido(self):
        try:
            compile("if x \n    mostre (1 )\n", "<codigo_pt>", "exec")
        except SyntaxError as exc:
            mensagem = formata_erro_amigavel(
                exc,
                ["se x", "    mostre(1)"],
                ["if x ", "    mostre (1 )"],
            )
            linhas = mensagem.splitlines()
            self.assertEqual(linhas[1].index("se x") + len("se x"), linhas[2].index("^"))

    def test_formata_erro_indentation_error(self):
        """Valida que IndentationError exibe a linha e explicação sobre recuo."""
        try:
            compile("if True:\nprint(1)", "<codigo_pt>", "exec")
        except IndentationError as exc:
            mensagem = formata_erro_amigavel(exc, ["if True:", "print(1)"])
            self.assertIn("Na linha 2: print(1)", mensagem)
            self.assertIn("esperava que esta linha estivesse com recuo", mensagem)


if __name__ == "__main__":
    unittest.main()
