"""
Tradução de erros comuns.

Esta é a parte do projeto com maior retorno pedagógico: a maioria da
frustração de um iniciante não vem das ~30 palavras-chave, vem de não
entender o que uma mensagem de erro em inglês está dizendo. Cobrir os
20-30 padrões de erro mais comuns já resolve a maior parte da dor real.

Cada entrada é (TipoDeExcecao, regex sobre str(exc)) -> função que
gera a mensagem em português. Os padrões são checados em ordem; o
primeiro que casar vence.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Callable

Regra = tuple[type[BaseException], re.Pattern, Callable[[re.Match], str]]


def _regra(excecao: type[BaseException], padrao: str, gerador: Callable[[re.Match], str]) -> Regra:
    return (excecao, re.compile(padrao), gerador)


REGRAS: list[Regra] = [
    _regra(
        IndexError, r"list index out of range",
        lambda m: "Você tentou acessar uma posição que não existe na lista "
                  "(o índice é maior que a quantidade de itens, ou a lista está vazia). "
                  "Lembre-se: a primeira posição é a 0, não a 1.",
    ),
    _regra(
        IndexError, r"string index out of range",
        lambda m: "Você tentou acessar uma posição que não existe no texto "
                  "(o índice é maior que a quantidade de caracteres).",
    ),
    _regra(
        KeyError, r".*",
        lambda m: f"Você tentou acessar a chave {m.group(0)} num dicionário, "
                  "mas essa chave não existe nele.",
    ),
    _regra(
        ZeroDivisionError, r"division by zero",
        lambda m: "Você tentou dividir um número por zero, o que não é permitido.",
    ),
    _regra(
        TypeError, r"unsupported operand type\(s\) for \+: '(\w+)' and '(\w+)'",
        lambda m: f"Você tentou somar um valor do tipo {m.group(1)} com um do "
                  f"tipo {m.group(2)}. Provavelmente precisa converter um deles "
                  "antes (ex.: com 'texto(...)' ou 'inteiro(...)').",
    ),
    _regra(
        TypeError, r'can only concatenate str \(not "(\w+)"\) to str',
        lambda m: f"Você tentou juntar (+) um texto com um valor do tipo "
                  f"{m.group(1)}. Para juntar os dois, converta o valor para "
                  "texto primeiro, ex.: 'texto(numero)'.",
    ),
    _regra(
        TypeError, r"'(\w+)' object is not subscriptable",
        lambda m: f"Você tentou acessar uma posição (com [ ]) de algo do tipo "
                  f"{m.group(1)}, mas esse tipo não permite isso.",
    ),
    _regra(
        TypeError, r"(\w+)\(\) missing (\d+) required positional argument",
        lambda m: f"A função '{m.group(1)}' precisa de {m.group(2)} argumento(s) "
                  "a mais do que você passou.",
    ),
    _regra(
        TypeError, r"(\w+)\(\) takes (\d+) positional argument.* but (\d+) (?:were|was) given",
        lambda m: f"A função '{m.group(1)}' espera {m.group(2)} argumento(s), "
                  f"mas você passou {m.group(3)}.",
    ),
    _regra(
        AttributeError, r"'(\w+)' object has no attribute '(\w+)'",
        lambda m: f"Um valor do tipo {m.group(1)} não tem '{m.group(2)}'. "
                  "Confira se digitou o nome certo ou se é o tipo de objeto esperado.",
    ),
    _regra(
        NameError, r"name '(\w+)' is not defined",
        lambda m: f"A variável ou função '{m.group(1)}' foi usada antes de existir. "
                  "Confira se você não esqueceu de criá-la antes, ou se digitou "
                  "o nome certo (lembre-se que maiúsculas/minúsculas importam).",
    ),
    _regra(
        ValueError, r"invalid literal for int\(\) with base 10: '(.*)'",
        lambda m: f"Você tentou converter \"{m.group(1)}\" para número inteiro, "
                  "mas esse texto não representa um número inteiro válido.",
    ),
    _regra(
        ModuleNotFoundError, r"No module named '(\w+)'",
        lambda m: f"O módulo '{m.group(1)}' não foi encontrado. Confira o nome "
                  "ou se ele precisa ser instalado.",
    ),
    _regra(
        RecursionError, r".*",
        lambda m: "Sua função está chamando a si mesma sem parar "
                  "(ela nunca chega numa condição de parada).",
    ),
    _regra(
        IndentationError, r"expected an indented block",
        lambda m: "O Python esperava que esta linha estivesse com recuo (espaços/indentação) "
                  "para a direita, pois ela faz parte do bloco acima. Use 4 espaços ou Tab.",
    ),
    _regra(
        IndentationError, r"unindent does not match any outer indentation level",
        lambda m: "A indentação desta linha não está alinhada com nenhuma linha anterior. "
                  "Verifique os espaços no início da linha para alinhar com o bloco correspondente.",
    ),
    _regra(
        SyntaxError, r"unexpected EOF while parsing",
        lambda m: "O código terminou antes do esperado. Confira se você não esqueceu "
                  "de fechar algum parêntese, colchete ou aspas.",
    ),
    _regra(
        SyntaxError, r"(?:EOL while scanning string literal|unterminated string literal)",
        lambda m: "Você abriu aspas para um texto, mas esqueceu de fechar antes do fim da linha.",
    ),
    _regra(
        SyntaxError, r"invalid syntax",
        lambda m: "Erro de escrita no código. Confira se você não esqueceu de colocar "
                  "dois pontos (:) no final da linha ou se digitou algo fora de ordem.",
    ),
]


def traduz_excecao(exc: BaseException) -> str | None:
    """Retorna uma explicação em português para a exceção, ou None se
    nenhuma regra conhecida bater (nesse caso, mostre o erro original)."""
    texto_busca = exc.msg if isinstance(exc, SyntaxError) and getattr(exc, "msg", None) else str(exc)
    for tipo, padrao, gerador in REGRAS:
        if isinstance(exc, tipo):
            casamento = padrao.search(texto_busca)
            if casamento:
                return gerador(casamento)
    return None


def _map_generated_column_to_source(column: int, source_line: str, generated_line: str) -> int:
    """Map a column from translated Python back to the original source line."""
    generated_position = max(0, column - 1)
    opcodes = SequenceMatcher(
        None, source_line, generated_line, autojunk=False,
    ).get_opcodes()

    # A replacement can be followed by a deletion when untokenize adds spacing.
    # A parser position after the translated text then maps to the source end.
    for tag, source_start, source_end, generated_start, generated_end in opcodes:
        if tag == "delete" and generated_start == generated_end == generated_position:
            return source_end + 1

    for tag, source_start, source_end, generated_start, generated_end in opcodes:
        if generated_start <= generated_position <= generated_end:
            if tag == "equal":
                return source_start + (generated_position - generated_start) + 1
            if tag == "replace":
                if generated_position == generated_end:
                    return source_end + 1
                if generated_position == generated_start:
                    return source_start + 1
                ratio = (generated_position - generated_start) / max(
                    1, generated_end - generated_start,
                )
                return round(source_start + ratio * (source_end - source_start)) + 1
            return source_start + 1

    return min(generated_position, len(source_line)) + 1


def formata_erro_amigavel(
    exc: BaseException,
    linhas_fonte_pt: list[str],
    linhas_fonte_py: list[str] | None = None,
) -> str:
    """Monta uma mensagem de erro amigável apontando para a linha do
    arquivo .ptpy original (não do Python gerado internamente)."""
    linha_numero = None
    coluna = None

    if isinstance(exc, SyntaxError):
        linha_numero = exc.lineno
        coluna = exc.offset
    else:
        tb = exc.__traceback__
        # Anda até o último frame que pertence ao código do usuário
        # (compilado com o nome de arquivo especial "<codigo_pt>")
        while tb is not None:
            if tb.tb_frame.f_code.co_filename == "<codigo_pt>":
                linha_numero = tb.tb_lineno
            tb = tb.tb_next

    partes = [f"⚠️  Deu erro do tipo: {type(exc).__name__}"]
    if linha_numero and 1 <= linha_numero <= len(linhas_fonte_pt):
        trecho = linhas_fonte_pt[linha_numero - 1]
        prefixo_trecho = f"   Na linha {linha_numero}: "
        partes.append(prefixo_trecho + trecho.strip())
        if coluna is not None and coluna > 0:
            if linhas_fonte_py and linha_numero <= len(linhas_fonte_py):
                coluna = _map_generated_column_to_source(
                    coluna,
                    trecho,
                    linhas_fonte_py[linha_numero - 1],
                )
            recuo_original = len(trecho) - len(trecho.lstrip())
            coluna_ajustada = max(1, coluna - recuo_original)
            partes.append(" " * len(prefixo_trecho) + " " * (coluna_ajustada - 1) + "^")

    explicacao = traduz_excecao(exc)
    if explicacao:
        partes.append(f"   {explicacao}")
    else:
        partes.append(f"   Detalhe técnico (ainda sem tradução): {exc}")

    return "\n".join(partes)
