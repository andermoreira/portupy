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

    def test_traducao_ouse_retrocompatibilidade(self):
        """Valida que 'ouse' continua transpilando para 'elif' por compatibilidade."""
        codigo_py = transpila("se x:\n    pass\nouse y:\n    pass\n")
        self.assertIn("elif y :", codigo_py)

    def test_traducao_senao_se_e_variacoes(self):
        """Valida suporte a 'senao se', 'senão se', 'senaose' e 'senãose' -> 'elif'."""
        for trecho in ("senao se x > 0:", "senão se x > 0:", "senaose x > 0:", "senãose x > 0:"):
            with self.subTest(trecho=trecho):
                codigo_py = transpila(f"se x == 0:\n    pass\n{trecho}\n    pass\n")
                self.assertIn("elif x >0 :", codigo_py.replace(" > ", ">"))

    def test_traducao_eh_contextual(self):
        """Valida que 'eh'/'é' vira 'is' para nulo/booleanos e '==' para literais/valores."""
        self.assertIn("x is None", transpila("se x eh nulo:\n    pass"))
        self.assertIn("x is None", transpila("se x é nulo:\n    pass"))
        self.assertIn("x==10", transpila("se x eh 10:\n    pass").replace(" ", ""))
        self.assertIn('nome=="Ana"', transpila('se nome eh "Ana":\n    pass').replace(" ", ""))

    def test_traducao_nao_eh_e_nao_em(self):
        """Valida 'nao eh' -> 'is not' (nulo) ou '!=' e 'nao em' -> 'not in'."""
        self.assertIn("x is not None", transpila("se x nao eh nulo:\n    pass"))
        self.assertIn("x is not None", transpila("se x não é nulo:\n    pass"))
        self.assertIn("x!=10", transpila("se x nao eh 10:\n    pass").replace(" ", ""))
        self.assertIn("x not in lista", transpila("se x nao em lista:\n    pass"))
        self.assertIn("x not in lista", transpila("se x não em lista:\n    pass"))

    def test_atribuicoes_aninhadas_nao_sao_confundidas_com_palavras_reservadas(self):
        """Permite defaults e argumentos nomeados dentro de estruturas traduzidas."""
        codigo_funcao = transpila("funcao saudacao(nome=\"mundo\"):\n    retorne nome\n")
        self.assertIn("def saudacao", codigo_funcao)

        codigo_condicional = transpila(
            "se valida(valor=1):\n    passe\n"
            "senao se valida(valor=2):\n    passe\n"
        )
        self.assertIn("if valida", codigo_condicional)
        self.assertIn("elif valida", codigo_condicional)

        codigo_comparacao = transpila("se valor eh valida(alvo=1):\n    passe\n")
        self.assertIn("valor ==", codigo_comparacao)


if __name__ == "__main__":
    unittest.main()
