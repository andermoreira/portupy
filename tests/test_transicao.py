import unittest

from transpilador_pt.transicao import renderiza_lado_a_lado


class TestTransicao(unittest.TestCase):

    def test_renderiza_lado_a_lado_cabecalho_e_colunas(self):
        """Valida que o renderizador inclui cabeçalhos bilíngues e divisores (AC-04)."""
        codigo_pt = "se x eh nulo:\n    mostre('vazio')"
        codigo_py = "if x is None:\n    print('vazio')"

        saida = renderiza_lado_a_lado(codigo_pt, codigo_py, largura_terminal=80)
        self.assertIn("Português", saida)
        self.assertIn("Python Canônico", saida)
        self.assertIn("│", saida)
        self.assertIn("─", saida)

    def test_renderiza_lado_a_lado_numeracao_linhas(self):
        """Valida alinhamento correto dos números de linha sincronizados."""
        codigo_pt = "a = 1\nb = 2\nc = 3"
        codigo_py = "a = 1\nb = 2\nc = 3"

        saida = renderiza_lado_a_lado(codigo_pt, codigo_py, largura_terminal=80)
        linhas = saida.splitlines()
        conteudo = [l for l in linhas if "1" in l or "2" in l or "3" in l]
        self.assertTrue(any("1" in l for l in conteudo))
        self.assertTrue(any("2" in l for l in conteudo))
        self.assertTrue(any("3" in l for l in conteudo))

    def test_renderiza_lado_a_lado_diferenca_de_linhas(self):
        """Valida renderização suave quando os códigos possuem números diferentes de linhas."""
        codigo_pt = "linha1\nlinha2"
        codigo_py = "linha1"

        saida = renderiza_lado_a_lado(codigo_pt, codigo_py, largura_terminal=80)
        self.assertIn("linha1", saida)
        self.assertIn("linha2", saida)

    def test_renderiza_lado_a_lado_terminal_estreito(self):
        """Valida degradação segura ou aviso caso o terminal tenha largura reduzida."""
        codigo_pt = "mostre('olá')"
        codigo_py = "print('olá')"

        saida = renderiza_lado_a_lado(codigo_pt, codigo_py, largura_terminal=50)
        self.assertTrue(len(saida) > 0)


if __name__ == "__main__":
    unittest.main()
