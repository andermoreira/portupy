import unittest
from transpilador_pt.transpiler import transpila, ErroDeTraducao


class TestTranspiler(unittest.TestCase):

    def test_traducao_condicional_se_senao(self):
        codigo_pt = "se x:\n    y\nsenao:\n    z\n"
        codigo_py = transpila(codigo_pt)
        self.assertIn("if", codigo_py)
        self.assertIn("else", codigo_py)

    def test_traducao_loop_para(self):
        codigo_pt = "para i em intervalo(5):\n    pass\n"
        codigo_py = transpila(codigo_pt)
        self.assertIn("for i in", codigo_py)

    def test_traducao_funcao_e_retorno(self):
        codigo_pt = "funcao dobro(n):\n    retorne n * 2\n"
        codigo_py = transpila(codigo_pt)
        self.assertIn("def dobro (n ):", codigo_py)
        self.assertIn("return n *2", codigo_py)

    def test_bloqueio_atribuicao_palavra_chave_estrutural(self):
        for codigo in ("para = 10", "para += 1", "para: inteiro = 1", "para, valor = (1, 2)"):
            with self.subTest(codigo=codigo), self.assertRaises(ErroDeTraducao) as ctx:
                transpila(codigo)
            self.assertIn("palavra reservada", str(ctx.exception))
            self.assertIn("para", str(ctx.exception))

    def test_erro_de_tokenizacao(self):
        with self.assertRaises(ErroDeTraducao):
            transpila('mostre("texto sem fechar\n')

    def test_atribuicao_variavel_com_nome_builtin(self):
        """Valida que 'lista = [1, 2, 3]' é permitida normalmente (ADR-001)."""
        codigo_py = transpila("lista = [1, 2, 3]")
        self.assertIn("lista", codigo_py)

    def test_atribuicao_e_acesso_atributo_objeto(self):
        """Valida que atributos precedidos por ponto não sofrem substituição nem bloqueio."""
        codigo_atribuicao = transpila("self.tipo = 1")
        self.assertIn("self.tipo", codigo_atribuicao.replace(" ", ""))

        codigo_acesso = transpila("carro.tipo")
        self.assertIn("carro.tipo", codigo_acesso.replace(" ", ""))

        codigo_classe = transpila("classe A:\n    funcao __init__(self, tipo):\n        self.tipo = tipo\n        self.se = 10\n")
        self.assertIn("self.tipo=tipo", codigo_classe.replace(" ", ""))
        self.assertIn("self.se=10", codigo_classe.replace(" ", ""))


if __name__ == "__main__":
    unittest.main()
