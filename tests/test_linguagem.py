import unittest

from portupy.dicionario import BUILTINS_CANONICOS, BUILTINS_PT, PALAVRAS_CHAVE
from portupy.transpiler import transpila, transpila_canonico


class TestContratoDeLinguagem(unittest.TestCase):

    def test_estruturas_em_portugues_geram_python_compilavel(self):
        casos = {
            "condicionais": (
                "se valor eh nulo:\n"
                "    passe\n"
                "senao se valor eh 1:\n"
                "    passe\n"
                "senao:\n"
                "    passe\n"
            ),
            "lacos": "para item em itens:\n    enquanto item:\n        quebre\n",
            "declaracoes": "classe Pessoa:\n    funcao nome(self):\n        retorne self.nome\n",
            "importacao": "importe math\nde math importe sqrt\n",
            "contexto": "com recurso como valor:\n    passe\n",
            "excecoes": (
                "tente:\n"
                "    passe\n"
                "exceto ValueError:\n"
                "    levante\n"
                "finalmente:\n"
                "    passe\n"
            ),
            "assinc-gerador": (
                "assincrono funcao roda():\n"
                "    aguarde tarefa()\n"
                "funcao conta():\n"
                "    produza 1\n"
            ),
        }

        for nome, codigo in casos.items():
            with self.subTest(nome=nome):
                compile(transpila(codigo), f"<{nome}>", "exec")

    def test_variantes_acentuadas_e_legadas_tem_o_mesmo_resultado(self):
        variantes = ("senao se", "senão se", "senaose", "senãose", "ouse")
        for variante in variantes:
            with self.subTest(variante=variante):
                codigo = transpila(f"se pronto:\n    passe\n{variante} fallback:\n    passe\n")
                self.assertIn("elif fallback", codigo)

    def test_strings_comentarios_e_atributos_nao_sao_traduzidos(self):
        codigo = (
            "# se mostre tamanho\n"
            "mensagem = 'se mostre tamanho'\n"
            "objeto.tamanho = mensagem\n"
        )
        canonico = transpila_canonico(codigo)

        self.assertIn("# se mostre tamanho", canonico)
        self.assertIn("'se mostre tamanho'", canonico)
        self.assertIn("objeto.tamanho", canonico.replace(" ", ""))

    def test_todos_os_builtins_de_runtime_tem_destino_canonico(self):
        self.assertEqual(set(BUILTINS_PT), set(BUILTINS_CANONICOS))
        for nome_pt, nome_py in BUILTINS_CANONICOS.items():
            with self.subTest(nome_pt=nome_pt):
                codigo = transpila_canonico(f"resultado = {nome_pt}(valor)\n")
                self.assertIn(f"{nome_py}(valor)", codigo.replace(" ", ""))

    def test_builtins_runtime_e_canonicos_permanecem_sincronizados(self):
        """Garante que o objeto injetado em runtime é exatamente o builtin
        nomeado na exportação canônica, prevenindo dessincronização entre
        BUILTINS_PT e BUILTINS_CANONICOS (fonte única em dicionario.py)."""
        import builtins

        self.assertEqual(BUILTINS_PT.keys(), BUILTINS_CANONICOS.keys())
        for nome_pt, nome_py in BUILTINS_CANONICOS.items():
            with self.subTest(nome_pt=nome_pt):
                self.assertIs(BUILTINS_PT[nome_pt], getattr(builtins, nome_py))

    def test_mapa_de_palavras_estruturais_tem_destinos_unicos(self):
        self.assertIn("se", PALAVRAS_CHAVE)
        self.assertEqual("elif", PALAVRAS_CHAVE["senaose"])
        self.assertEqual("None", PALAVRAS_CHAVE["nulo"])
        self.assertEqual("async", PALAVRAS_CHAVE["assincrono"])


if __name__ == "__main__":
    unittest.main()
