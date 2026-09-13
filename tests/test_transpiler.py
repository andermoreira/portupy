import unittest
from portupy.transpiler import transpila, transpila_canonico, ErroDeTraducao
from portupy.dicionario import BUILTINS_CANONICOS, BUILTINS_PT




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
        self.assertIn("def dobro(n):", codigo_py)
        self.assertIn("return n * 2", codigo_py)

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
        self.assertIn("elif y:", codigo_py)

    def test_traducao_senao_se_e_variacoes(self):
        """Valida suporte a 'senao se', 'senão se', 'senaose' e 'senãose' -> 'elif'."""
        for trecho in ("senao se x > 0:", "senão se x > 0:", "senaose x > 0:", "senãose x > 0:"):
            with self.subTest(trecho=trecho):
                codigo_py = transpila(f"se x == 0:\n    pass\n{trecho}\n    pass\n")
                self.assertIn("elif x > 0:", codigo_py)

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

    def test_transpila_canonico_substitui_builtins_essenciais(self):
        """Valida que transpila_canonico gera Python puro traduzindo builtins (AC-01)."""
        codigo_pt = (
            "para i em intervalo(3):\n"
            "    mostre(f'indice: {i}')\n"
            "nome = leia('Nome: ')\n"
            "t = tamanho(nome)\n"
        )
        codigo_py = transpila_canonico(codigo_pt)
        codigo_sem_espaco = codigo_py.replace(" ", "")
        self.assertIn("foriinrange(3):", codigo_sem_espaco)
        self.assertIn("print(f'indice:{i}')", codigo_sem_espaco)
        self.assertIn("input('Nome:')", codigo_sem_espaco)
        self.assertIn("len(nome)", codigo_sem_espaco)

    def test_transpila_canonico_preserva_atributos_de_objetos(self):
        """Valida que atributos precedidos por '.' não são renomeados (AC-02)."""
        codigo_pt = "self.tamanho = 10\nx = carro.tipo\nobj.mostre()"
        codigo_py = transpila_canonico(codigo_pt)
        codigo_sem_espaco = codigo_py.replace(" ", "")
        self.assertIn("self.tamanho=10", codigo_sem_espaco)
        self.assertIn("carro.tipo", codigo_sem_espaco)
        self.assertIn("obj.mostre()", codigo_sem_espaco)
        self.assertNotIn("len", codigo_py)

    def test_transpila_canonico_preserva_variavel_em_atribuicao(self):
        """Valida que variáveis criadas com nome de builtin não sofrem colisão indevida."""
        codigo_pt = "lista = [1, 2, 3]\nmostre(tamanho(lista))"
        codigo_py = transpila_canonico(codigo_pt)
        codigo_sem_espaco = codigo_py.replace(" ", "")
        self.assertIn("lista=[1,2,3]", codigo_sem_espaco)
        self.assertIn("print(len(lista))", codigo_sem_espaco)
        self.assertNotIn("list=[1,2,3]", codigo_sem_espaco)
        self.assertNotIn("len(list)", codigo_sem_espaco)

    def test_transpila_canonico_execucao_autonoma(self):
        """Valida que o código exportado executa diretamente sem globals especiais (AC-03)."""
        codigo_pt = (
            "itens = [10, 20]\n"
            "se tamanho(itens) eh 2:\n"
            "    resultado = 'ok'\n"
        )
        codigo_py = transpila_canonico(codigo_pt)
        ns = {}
        # Executa em namespace limpo sem BUILTINS_PT
        exec(codigo_py, {}, ns)
        self.assertEqual("ok", ns.get("resultado"))

    def test_transpila_canonico_preserva_sombreamento_de_builtin(self):
        """Valida que uma função do aluno mantém o nome mesmo se colidir com builtin."""
        codigo_pt = (
            "funcao mostre(valor):\n"
            "    retorne valor + 1\n"
            "resultado = mostre(1)\n"
        )

        codigo_py = transpila_canonico(codigo_pt)
        ns = {}
        exec(codigo_py, {}, ns)

        self.assertEqual(2, ns.get("resultado"))
        self.assertIn("resultado=mostre", codigo_py.replace(" ", ""))
        self.assertNotIn("resultado=print", codigo_py.replace(" ", ""))

    def test_transpila_canonico_preserva_parametro_sombreado_em_chamada_nomeada(self):
        """Valida que parâmetros builtin não são renomeados no cabeçalho."""
        codigo_pt = (
            "funcao aplicar(mostre):\n"
            "    retorne mostre\n"
            "resultado = aplicar(mostre=5)\n"
        )

        codigo_py = transpila_canonico(codigo_pt)
        ns = {}
        exec(codigo_py, {}, ns)

        self.assertEqual(5, ns.get("resultado"))

    def test_transpila_canonico_preserva_sombreamento_de_builtin_em_fstring(self):
        """Valida que expressões de f-string respeitam o escopo da função."""
        codigo_pt = (
            "funcao rotulo(tamanho):\n"
            "    retorne f'valor: {tamanho}'\n"
            "resultado = rotulo('ok')\n"
        )

        codigo_py = transpila_canonico(codigo_pt)
        ns = {}
        exec(codigo_py, {}, ns)

        self.assertEqual("valor: ok", ns.get("resultado"))

    def test_transpila_canonico_preserva_sombreamento_em_lambda_e_compreensao(self):
        """Valida que escopos implícitos também preservam nomes locais."""
        casos = (
            (
                "resultado = (lambda tamanho: tamanho(1))(lambda x: x + 1)\n",
                2,
            ),
            (
                "resultado = [tamanho(1) for tamanho in [lambda x: x + 1]]\n",
                [2],
            ),
        )

        for codigo_pt, esperado in casos:
            with self.subTest(codigo_pt=codigo_pt):
                codigo_py = transpila_canonico(codigo_pt)
                ns = {}
                exec(codigo_py, {}, ns)
                self.assertEqual(esperado, ns.get("resultado"))

    def test_estruturas_de_controle_adicionais_geram_python_compilavel(self):
        """Garante que classes e tratamento de exceções permaneçam parte do contrato."""
        codigo_pt = (
            "classe Pessoa:\n"
            "    funcao __init__(self, nome):\n"
            "        self.nome = nome\n"
            "\n"
            "funcao descreva(pessoa):\n"
            "    tente:\n"
            "        retorne pessoa.nome\n"
            "    exceto AttributeError:\n"
            "        retorne nulo\n"
        )

        codigo_py = transpila(codigo_pt)
        compile(codigo_py, "<teste_transpilador>", "exec")
        self.assertIn("class Pessoa", codigo_py)
        self.assertIn("try", codigo_py)
        self.assertIn("except AttributeError", codigo_py)

    def test_identificadores_unicode_sao_preservados(self):
        """Identificadores válidos em português devem continuar válidos no Python."""
        codigo_py = transpila("ação = 2\nresultado = ação + 1\n")
        namespace = {}

        exec(codigo_py, {}, namespace)

        self.assertEqual(3, namespace["resultado"])

    def test_mapas_de_builtins_runtime_e_canonico_permanecem_sincronizados(self):
        """Todo builtin disponível no runtime deve ter destino na exportação canônica."""
        self.assertEqual(set(BUILTINS_PT), set(BUILTINS_CANONICOS))


class TestFStringCanonica(unittest.TestCase):
    """Casos de borda da tradução de expressões dentro de f-strings.

    O objetivo é traduzir os builtins pedagógicos que aparecem nas expressões
    interpoladas sem tocar em texto literal, format spec, conversão (!r/!s/!a)
    ou no marcador de depuração (=). Todos os resultados devem permanecer
    Python válido e compilável.
    """

    def _canonico_compilavel(self, codigo_pt: str) -> str:
        codigo_py = transpila_canonico(codigo_pt)
        compile(codigo_py, "<fstring>", "exec")
        return codigo_py.replace(" ", "")

    def test_builtin_simples_em_fstring(self):
        saida = self._canonico_compilavel('x = f"n={tamanho(a)}"\n')
        self.assertIn('f"n={len(a)}"', saida)

    def test_conversao_nao_confunde_com_desigualdade(self):
        """'!=' é operador, não conversão: o builtin após ele deve ser traduzido."""
        saida = self._canonico_compilavel('x = f"{a != tamanho(b)}"\n')
        self.assertIn("a!=len(b)", saida)

    def test_conversao_repr_preservada_e_builtin_traduzido(self):
        saida = self._canonico_compilavel('x = f"{tamanho(a)!r}"\n')
        self.assertIn("{len(a)!r}", saida)

    def test_depuracao_igual_traduz_expressao_e_preserva_marcador(self):
        """f"{expr=}" deve traduzir a expressão à esquerda do '=' de depuração."""
        for codigo_pt in (
            'x = f"{tamanho(a)=}"\n',
            'x = f"{tamanho(a) = }"\n',
            'x = f"{tamanho(a)=!r}"\n',
            'x = f"{tamanho(a)=:>5}"\n',
        ):
            with self.subTest(codigo_pt=codigo_pt):
                saida = self._canonico_compilavel(codigo_pt)
                self.assertIn("len(a)=", saida)
                self.assertNotIn("tamanho", saida)

    def test_depuracao_igual_executa_com_texto_canonico(self):
        """No runtime, o '=' de depuração ecoa a expressão já traduzida."""
        codigo_py = transpila_canonico('a = [1, 2, 3]\nx = f"{tamanho(a)=}"\n')
        namespace = {}
        exec(compile(codigo_py, "<fstring>", "exec"), namespace)
        self.assertNotIn("tamanho", namespace["x"])
        self.assertEqual("len(a)=3", namespace["x"].replace(" ", ""))

    def test_format_spec_e_slice_nao_sao_traduzidos_como_campo(self):
        """':' de format spec e de slice não devem quebrar a extração da expressão."""
        saida_spec = self._canonico_compilavel('x = f"{tamanho(a):>10}"\n')
        self.assertIn("{len(a):>10}", saida_spec)
        saida_slice = self._canonico_compilavel('x = f"{lista[1:2]}"\n')
        self.assertIn("lista[1:2]", saida_slice)

    def test_fstring_aninhada_e_aspas_triplas(self):
        saida_aninhada = self._canonico_compilavel('x = f"{f\'{tamanho(a)}\'}"\n')
        self.assertIn("len(a)", saida_aninhada)
        saida_triplas = self._canonico_compilavel('x = f"""linha {tamanho(a)} fim"""\n')
        self.assertIn("linha{len(a)}fim", saida_triplas)

    def test_chaves_literais_preservadas(self):
        saida = self._canonico_compilavel('x = f"{{literal}} {tamanho(a)}"\n')
        self.assertIn("{{literal}}", saida)
        self.assertIn("{len(a)}", saida)


class TestFStringRuntime(unittest.TestCase):
    """Runtime must rewrite keywords inside pre-3.12 STRING f-tokens."""

    def test_literais_em_fstring_viram_singletons_python(self):
        casos = (
            ('x = f"{nulo}"\n', "None", "nulo"),
            ('x = f"{verdadeiro}"\n', "True", "verdadeiro"),
            ('x = f"{falso}"\n', "False", "falso"),
        )
        for codigo_pt, esperado, original in casos:
            with self.subTest(codigo_pt=codigo_pt):
                codigo_py = transpila(codigo_pt)
                self.assertIn(esperado, codigo_py)
                self.assertNotIn(original, codigo_py)

    def test_runtime_preserva_builtin_pedagogico_na_fstring(self):
        codigo_py = transpila('mostre(f"{tamanho(nomes)}")')
        self.assertIn("tamanho", codigo_py)
        self.assertNotIn("len", codigo_py)

    def test_palavra_reservada_em_fstring_nao_e_engolida(self):
        with self.assertRaises(ErroDeTraducao):
            transpila('x = f"{(se := 1)}"\n')


if __name__ == "__main__":
    unittest.main()
