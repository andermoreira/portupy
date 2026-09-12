import unittest

from transpilador_pt.transicao import renderiza_lado_a_lado


class TestTransicao(unittest.TestCase):

    def test_renderiza_lado_a_lado_cabecalho_e_colunas(self):
        """Valida que o renderizador inclui cabeçalhos bilíngues e divisores (AC-04)."""
        codigo_pt = "se x eh nulo:\n    mostre('vazio')"
        codigo_py = "if x is None:\n    print('vazio')"

        saida = renderiza_lado_a_lado(codigo_pt, codigo_py, largura_terminal=80)
        self.assertIn("Linha", saida)
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
        linhas_codigo = linhas[2:]
        numeros = [linha.split("│", 1)[0].strip() for linha in linhas_codigo]
        self.assertEqual(["1", "2", "3"], numeros)

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
        self.assertIn("colunas empilhadas", saida)
        self.assertTrue(all(len(linha) <= 50 for linha in saida.splitlines()))

    def test_renderiza_lado_a_lado_respeita_largura_em_tabela(self):
        """Valida que a tabela não ultrapassa a largura solicitada."""
        saida = renderiza_lado_a_lado("mostre('olá')", "print('olá')", largura_terminal=80)

        self.assertTrue(all(len(linha) <= 80 for linha in saida.splitlines()))
        self.assertEqual(len(saida.splitlines()[0]), len(saida.splitlines()[1]))

    def test_renderiza_lado_a_lado_terminal_extremamente_estreito(self):
        """Valida que até uma largura mínima não produz linhas maiores que o terminal."""
        saida = renderiza_lado_a_lado("mostre('olá')", "print('olá')", largura_terminal=1)

        self.assertTrue(all(len(linha) <= 1 for linha in saida.splitlines()))


if __name__ == "__main__":
    unittest.main()
