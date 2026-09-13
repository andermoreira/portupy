"""
Transpilador PT -> Python baseado no módulo `tokenize` da stdlib.

Estratégia: em vez de escrever um parser do zero, usamos o tokenizer
do próprio Python para separar o código em tokens, trocamos apenas o
texto dos tokens NAME que constam no dicionário, e remontamos com
`tokenize.untokenize`. Isso significa que strings, comentários,
números e indentação nunca são tocados -- só identificadores que
batem exatamente com uma entrada do dicionário.
"""

from __future__ import annotations

import io
import keyword
import token
import tokenize

from .dicionario import MAPA, BUILTINS_CANONICOS
from .escopo_canonico import ScopeInfo, build_scope_context


class ErroDeTraducao(Exception):
    """Erro ao tentar transpilar o código-fonte em português."""


# FSTRING_MIDDLE só existe no Python 3.12+ (PEP 701). Nas versões anteriores a
# f-string é um único token STRING, então usamos um sentinela que nunca casa.
_FSTRING_MIDDLE = getattr(token, "FSTRING_MIDDLE", -1)


ASSIGNMENT_OPERATORS = {
    "=", ":=", "+=", "-=", "*=", "/=", "//=", "%=", "**=",
    "<<=", ">>=", "&=", "|=", "^=", "@=",
}


def _has_assignment_until_statement_end(
    tokens: list[tokenize.TokenInfo], start: int,
) -> bool:
    """Check whether an assignment operator appears before the statement ends.

    No Python 3.12+ (PEP 701) o marcador de depuração de f-string ``f"{expr=}"``
    aparece como um token ``OP '='`` no fluxo. Ele não é uma atribuição: é
    seguido de ``}`` (ou de ``!`` de conversão / ``:`` de format spec). Ignorá-lo
    evita tratar o builtin à esquerda como alvo de atribuição e deixá-lo sem
    tradução na exportação canônica.
    """
    resto = tokens[start + 1:]
    nesting = 0
    for pos, tok in enumerate(resto):
        if tok.type == token.OP:
            if tok.string in "([{":
                nesting += 1
            elif tok.string in ")]}":
                nesting = max(0, nesting - 1)
            elif tok.string == "=" and nesting == 0:
                # '=' de depuração de f-string: seguido de '}', '!' ou ':'.
                # No 3.12+, o format spec após o '=' surge como FSTRING_MIDDLE.
                proximo = resto[pos + 1] if pos + 1 < len(resto) else None
                tipos_sufixo_debug = (token.OP, _FSTRING_MIDDLE)
                if (
                    proximo is not None
                    and proximo.type in tipos_sufixo_debug
                    and proximo.string[:1] in ("}", "!", ":")
                ):
                    continue
                return True
            elif tok.string in ASSIGNMENT_OPERATORS and nesting == 0:
                return True
        elif tok.type == token.NEWLINE and nesting == 0:
            return False
    return False


SINGLETONS_DE_IDENTIDADE = {"nulo", "None", "verdadeiro", "falso", "True", "False"}


def _substitui_em_fstring(
    literal_fstring: str,
    protected_names: frozenset[str] = frozenset(),
    traduzir_builtins: bool = False,
) -> str:
    """Translate interpolations inside f-string STRING tokens (Python < 3.12).

    Runtime (`traduzir_builtins=False`) still rewrites structural keywords so
    `f"{nulo}"` becomes `f"{None}"`. Canonical export also rewrites builtins.
    """
    quote_idx = -1
    for idx, c in enumerate(literal_fstring[:4]):
        if c in ('"', "'"):
            quote_idx = idx
            break
    if quote_idx == -1:
        return literal_fstring

    prefixo = literal_fstring[:quote_idx].lower()
    if "f" not in prefixo:
        return literal_fstring

    delimitador = literal_fstring[quote_idx:]
    if delimitador.startswith(('"""', "'''")):
        quotes = delimitador[:3]
        miolo = delimitador[3:-3]
    else:
        quotes = delimitador[:1]
        miolo = delimitador[1:-1]

    resultado = []
    i = 0
    n = len(miolo)
    while i < n:
        if miolo[i : i + 2] == "{{":
            resultado.append("{{")
            i += 2
            continue
        if miolo[i : i + 2] == "}}":
            resultado.append("}}")
            i += 2
            continue
        if miolo[i] == "{":
            inicio = i + 1
            nivel_chaves = 0
            nivel_paren = 0
            nivel_colch = 0
            em_aspas = None
            j = inicio
            # Fim da expressão de código dentro do campo (antes de sufixos
            # como o '=' de depuração, a conversão '!r' ou o format spec ':').
            fim_expr = -1
            # Sufixo preservado literalmente: '=' de depuração + '!conv' + ':spec'.
            sufixo = ""
            while j < n:
                ch = miolo[j]
                if em_aspas:
                    if ch == "\\" and j + 1 < n:
                        j += 2
                        continue
                    if ch == em_aspas:
                        em_aspas = None
                else:
                    if ch in ('"', "'"):
                        em_aspas = ch
                    elif ch == "(":
                        nivel_paren += 1
                    elif ch == ")":
                        nivel_paren = max(0, nivel_paren - 1)
                    elif ch == "[":
                        nivel_colch += 1
                    elif ch == "]":
                        nivel_colch = max(0, nivel_colch - 1)
                    elif ch == "{":
                        nivel_chaves += 1
                    elif ch == "}":
                        if nivel_chaves == 0 and nivel_paren == 0 and nivel_colch == 0:
                            break
                        nivel_chaves -= 1
                    elif (
                        nivel_chaves == 0
                        and nivel_paren == 0
                        and nivel_colch == 0
                    ):
                        # '=' de depuração (PEP: f"{expr=}"): um '=' isolado, não
                        # parte de '==', '!=', '<=', '>=', ':='. Marca o fim da
                        # expressão; tudo dali em diante é preservado literal.
                        if (
                            ch == "="
                            and miolo[j + 1 : j + 2] != "="
                            and miolo[j - 1 : j] not in ("=", "!", "<", ">", ":")
                        ):
                            fim_expr = j
                            k = j
                            while k < n and miolo[k] != "}":
                                k += 1
                            sufixo = miolo[j:k]
                            j = k
                            break
                        # Conversão '!r'/'!s'/'!a', só quando seguida de '}' ou ':'
                        # (evita confundir com o operador '!=').
                        if (
                            ch == "!"
                            and miolo[j + 1 : j + 2] in ("r", "s", "a")
                            and miolo[j + 2 : j + 3] in ("}", ":")
                        ):
                            fim_expr = j
                            k = j
                            while k < n and miolo[k] != "}":
                                k += 1
                            sufixo = miolo[j:k]
                            j = k
                            break
                        # Início do format spec ':' no nível do campo.
                        if ch == ":":
                            fim_expr = j
                            k = j
                            while k < n and miolo[k] != "}":
                                k += 1
                            sufixo = miolo[j:k]
                            j = k
                            break
                j += 1

            if fim_expr == -1:
                fim_expr = j
            expr_bruta = miolo[inicio:fim_expr]

            expr_traduzida = _transpila_core(
                expr_bruta,
                traduzir_builtins=traduzir_builtins,
                protected_names=protected_names,
            ).strip()

            resultado.append("{" + expr_traduzida + sufixo + "}")
            i = j + 1
        else:
            resultado.append(miolo[i])
            i += 1

    return literal_fstring[:quote_idx] + quotes + "".join(resultado) + quotes



def _transpila_core(
    codigo_pt: str,
    traduzir_builtins: bool = False,
    protected_names: frozenset[str] | None = None,
) -> str:
    """Núcleo de tradução léxica PT -> Python com controle de tradução de builtins."""
    tokens_saida = []
    leitor = io.StringIO(codigo_pt).readline

    try:
        fluxo = list(tokenize.generate_tokens(leitor))
    except (tokenize.TokenError, IndentationError) as exc:
        raise ErroDeTraducao(f"Não consegui interpretar o código: {exc}") from exc

    scope_infos: list[ScopeInfo] = []
    parameter_indices: set[int] = set()
    inherited_protected_names = protected_names or frozenset()
    module_protected_names = inherited_protected_names
    if traduzir_builtins:
        canonical_syntax = _transpila_core(codigo_pt, traduzir_builtins=False)
        (
            scope_infos,
            parameter_indices,
            discovered_module_names,
        ) = build_scope_context(
            canonical_syntax,
            fluxo,
        )
        module_protected_names = inherited_protected_names | discovered_module_names

    def names_protected_for(tok: tokenize.TokenInfo) -> frozenset[str]:
        candidates = [
            scope
            for scope in scope_infos
            if scope.start_line <= tok.start[0] <= scope.end_line
            and (
                tok.start[0] > scope.start_line
                or tok.start[1] >= scope.start_column
            )
        ]
        if not candidates:
            return module_protected_names
        return inherited_protected_names | max(
            candidates,
            key=lambda scope: (scope.start_column, scope.start_line),
        ).protected_names

    i = 0
    n = len(fluxo)

    while i < n:
        tok = fluxo[i]
        tipo, valor, inicio, fim, linha = tok

        # Se for precedido por '.', é acesso ou definição de atributo (ex.: obj.se, self.tipo = 1)
        # e não deve sofrer substituição nem checagem de palavra reservada.
        anterior = fluxo[i - 1] if i > 0 else None
        eh_atributo = anterior is not None and anterior.type == token.OP and anterior.string == "."

        if tipo == token.NAME and not eh_atributo:
            proximo = fluxo[i + 1] if i + 1 < n else None
            proximo_2 = fluxo[i + 2] if i + 2 < n else None

            # Reconhece "senao se" ou "senão se" na mesma linha e funde em "elif"
            if (
                valor in ("senao", "senão")
                and proximo is not None
                and proximo.type == token.NAME
                and proximo.string == "se"
                and proximo.start[0] == inicio[0]
            ):
                if _has_assignment_until_statement_end(fluxo, i):
                    raise ErroDeTraducao(
                        f"linha {inicio[0]}: '{valor} se' é uma palavra reservada nesta "
                        f"linguagem (equivale a 'elif' em Python) e não pode "
                        f"ser usada como nome de variável."
                    )
                tokens_saida.append((token.NAME, "elif", inicio, proximo.end, linha))
                i += 2
                continue

            # Reconhece negação composta "nao eh" ou "não é" na mesma linha
            if (
                valor in ("nao", "não")
                and proximo is not None
                and proximo.type == token.NAME
                and proximo.string in ("eh", "é")
                and proximo.start[0] == inicio[0]
            ):
                if _has_assignment_until_statement_end(fluxo, i):
                    raise ErroDeTraducao(
                        f"linha {inicio[0]}: '{valor} {proximo.string}' é uma expressão reservada nesta "
                        f"linguagem e não pode ser usada como nome de variável."
                    )
                if proximo_2 is not None and proximo_2.string in SINGLETONS_DE_IDENTIDADE:
                    # 'is not' vira dois tokens; damos posições crescentes e sem
                    # sobreposição (o untokenize exige ordem monotônica).
                    fim_is = (inicio[0], inicio[1] + 2)
                    inicio_not = (inicio[0], inicio[1] + 3)
                    tokens_saida.append((token.NAME, "is", inicio, fim_is, linha))
                    tokens_saida.append((token.NAME, "not", inicio_not, proximo.end, linha))
                else:
                    tokens_saida.append((token.OP, "!=", inicio, proximo.end, linha))
                i += 2
                continue

            # Resolução contextual de "eh" e "é" (ADR-002)
            if valor in ("eh", "é"):
                if _has_assignment_until_statement_end(fluxo, i):
                    raise ErroDeTraducao(
                        f"linha {inicio[0]}: '{valor}' é uma palavra reservada nesta "
                        f"linguagem e não pode ser usada como nome de variável."
                    )
                if proximo is not None and proximo.string in SINGLETONS_DE_IDENTIDADE:
                    tokens_saida.append((token.NAME, "is", inicio, fim, linha))
                else:
                    tokens_saida.append((token.OP, "==", inicio, fim, linha))
                i += 1
                continue

            if valor in MAPA:
                # Checagem amigável: usar uma palavra reservada como alvo de
                # atribuição ("para = 5") gera um SyntaxError confuso depois
                # da tradução. Detectamos aqui e explicamos o motivo real.
                if _has_assignment_until_statement_end(fluxo, i):
                    raise ErroDeTraducao(
                        f"linha {inicio[0]}: '{valor}' é uma palavra reservada nesta "
                        f"linguagem (equivale a '{MAPA[valor]}' em Python) e não pode "
                        f"ser usada como nome de variável. Escolha outro nome, "
                        f"ex.: '{valor}_valor'."
                    )
                valor = MAPA[valor]
            elif traduzir_builtins and valor in BUILTINS_CANONICOS:
                # Na exportação canônica, substitui builtins pedagógicos por seus equivalentes Python.
                # Mantém identificadores vinculados ao escopo atual, preservando
                # o comportamento normal de sombreamento de nomes em Python.
                eh_definicao_funcao = anterior is not None and anterior.type == token.NAME and anterior.string in ("def", "funcao", "função")
                eh_alvo_atribuicao = _has_assignment_until_statement_end(fluxo, i)
                eh_nome_vinculado = (
                    i in parameter_indices
                    or valor in names_protected_for(tok)
                )
                
                # Tipos embutidos ("lista", "conjunto", "tupla", etc.) só viram "list", "set", etc.
                # se forem chamados como construtores com '(' ou usados em anotação de tipo.
                # Caso contrário, representam variáveis do aluno (ex.: tamanho(lista)).
                eh_tipo_embutido = valor in ("lista", "dicionario", "dicionário", "conjunto", "tupla", "texto", "inteiro", "decimal", "booleano")
                eh_chamada_ou_anotacao = (proximo is not None and proximo.string == "(") or (anterior is not None and anterior.string in (":", "->", "["))
                
                if (
                    not eh_definicao_funcao
                    and not eh_alvo_atribuicao
                    and not eh_nome_vinculado
                ):
                    if not eh_tipo_embutido or eh_chamada_ou_anotacao:
                        valor = BUILTINS_CANONICOS[valor]

        elif tipo == token.STRING:
            # Pre-3.12 f-strings are a single STRING token. Without rewriting
            # the interpolation, keywords like nulo survive into exec and
            # become NameError. Builtins stay in Portuguese unless exporting.
            valor = _substitui_em_fstring(
                valor,
                names_protected_for(tok),
                traduzir_builtins=traduzir_builtins,
            )

        # 5-tupla (com posições originais) faz o untokenize preservar o
        # espaçamento do código-fonte, mesmo quando o texto do token muda
        # (ex.: funcao -> def). Evita os espaços espúrios do modo compat.
        tokens_saida.append((tipo, valor, inicio, fim, linha))
        i += 1


    try:
        return tokenize.untokenize(tokens_saida)
    except ValueError as exc:
        raise ErroDeTraducao(f"Falha ao remontar o código traduzido: {exc}") from exc


def transpila(codigo_pt: str) -> str:
    """Converte código-fonte em português para código Python equivalente.

    Preserva números de linha 1:1 com o original, o que permite que
    tracebacks apontem para a linha certa do arquivo .ptpy do usuário.
    """
    return _transpila_core(codigo_pt, traduzir_builtins=False)


def transpila_canonico(codigo_pt: str) -> str:
    """Converte código-fonte em português para código Python canônico e autônomo (ADR-003).

    Substitui tanto a sintaxe estrutural quanto nomes de funções embutidas (mostre -> print,
    tamanho -> len, etc.), permitindo execução pura sem necessidade do pacote portupy.
    """
    return _transpila_core(codigo_pt, traduzir_builtins=True)


def palavra_e_reservada_em_pt(nome: str) -> bool:
    """Útil para avisar o usuário se ele tentar nomear uma variável
    com uma palavra que é reservada nesta camada (ex.: 'para', 'em', 'eh')."""
    return nome in MAPA or nome in ("eh", "é") or keyword.iskeyword(nome)
