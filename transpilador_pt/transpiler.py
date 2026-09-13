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

import ast
import difflib
import io
import keyword
import symtable
import token
import tokenize
from dataclasses import dataclass

from .dicionario import MAPA, BUILTINS_CANONICOS


class ErroDeTraducao(Exception):
    """Erro ao tentar transpilar o código-fonte em português."""


ASSIGNMENT_OPERATORS = {
    "=", ":=", "+=", "-=", "*=", "/=", "//=", "%=", "**=",
    "<<=", ">>=", "&=", "|=", "^=", "@=",
}


def _has_assignment_until_statement_end(
    tokens: list[tokenize.TokenInfo], start: int,
) -> bool:
    """Check whether an assignment operator appears before the statement ends."""
    nesting = 0
    for tok in tokens[start + 1:]:
        if tok.type == token.OP:
            if tok.string in "([{":
                nesting += 1
            elif tok.string in ")]}":
                nesting = max(0, nesting - 1)
            elif tok.string in ASSIGNMENT_OPERATORS and nesting == 0:
                return True
        elif tok.type == token.NEWLINE and nesting == 0:
            return False
    return False


SINGLETONS_DE_IDENTIDADE = {"nulo", "None", "verdadeiro", "falso", "True", "False"}


@dataclass(frozen=True)
class _ScopeInfo:
    """Binding information for the body of one Python lexical scope."""

    start_line: int
    start_column: int
    end_line: int
    protected_names: frozenset[str]


def _scope_key(node: ast.AST) -> tuple[str, str, int] | None:
    """Return the symbol-table identity for a scope-bearing AST node."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return "function", node.name, node.lineno
    if isinstance(node, ast.ClassDef):
        return "class", node.name, node.lineno
    if isinstance(node, ast.Lambda):
        return "function", "lambda", node.lineno
    if isinstance(node, ast.ListComp):
        return "function", "listcomp", node.lineno
    if isinstance(node, ast.SetComp):
        return "function", "setcomp", node.lineno
    if isinstance(node, ast.DictComp):
        return "function", "dictcomp", node.lineno
    if isinstance(node, ast.GeneratorExp):
        return "function", "genexpr", node.lineno
    return None


def _scope_span(node: ast.AST) -> tuple[ast.AST, int, int] | None:
    """Return the AST start node and line range covered by a scope."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        if not node.body:
            return None
        start_node = node.body[0]
        end_node = node.body[-1]
    elif isinstance(node, ast.Lambda):
        start_node = end_node = node.body
    elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
        start_node = node
        end_node = node
    else:
        return None
    return (
        start_node,
        start_node.lineno,
        getattr(end_node, "end_lineno", end_node.lineno),
    )


def _map_canonical_column_to_source(
    canonical_line: str,
    source_line: str,
    canonical_column: int,
) -> int:
    """Map an AST byte column through spacing and keyword substitutions."""
    try:
        canonical_char_column = len(
            canonical_line.encode("utf-8")[:canonical_column].decode("utf-8")
        )
    except UnicodeDecodeError:
        canonical_char_column = canonical_column

    matcher = difflib.SequenceMatcher(
        None,
        canonical_line,
        source_line,
        autojunk=False,
    )
    for tag, canonical_start, canonical_end, source_start, source_end in matcher.get_opcodes():
        if canonical_start <= canonical_char_column <= canonical_end:
            if tag == "equal":
                return source_start + (canonical_char_column - canonical_start)
            if canonical_char_column == canonical_end:
                return source_end
            return source_start
    return min(canonical_char_column, len(source_line))


def _source_column_for_ast_node(
    node: ast.AST,
    canonical_lines: list[str],
    source_lines: dict[int, str],
) -> int:
    """Convert an AST node column to the original PT source column."""
    canonical_line = canonical_lines[node.lineno - 1] if node.lineno <= len(canonical_lines) else ""
    source_line = source_lines.get(node.lineno, "")
    return _map_canonical_column_to_source(
        canonical_line,
        source_line,
        getattr(node, "col_offset", 0),
    )


def _all_symbol_tables(table: symtable.SymbolTable) -> list[symtable.SymbolTable]:
    """Flatten a symbol-table tree while preserving source order."""
    resultado = [table]
    for filho in table.get_children():
        resultado.extend(_all_symbol_tables(filho))
    return resultado


def _protected_names(
    table: symtable.SymbolTable,
    module_table: symtable.SymbolTable,
) -> frozenset[str]:
    """Find names whose references must keep the Portuguese spelling.

    ``symtable`` already accounts for assignments, parameters, imports,
    ``global`` and ``nonlocal`` declarations. A global reference is also
    protected when the module binds that name, because that binding shadows
    the injected Portuguese builtin at runtime.
    """
    protected = set()
    for name in table.get_identifiers():
        symbol = table.lookup(name)
        is_nonlocal = getattr(symbol, "is_nonlocal", lambda: False)()
        if symbol.is_local() or symbol.is_free() or is_nonlocal:
            protected.add(name)
            continue
        if symbol.is_global():
            if symbol.is_assigned():
                protected.add(name)
                continue
            try:
                module_symbol = module_table.lookup(name)
            except KeyError:
                continue
            if module_symbol.is_local():
                protected.add(name)
    return frozenset(protected)


def _meaningful_token_indices(
    tokens: list[tokenize.TokenInfo],
) -> list[int]:
    """Return token indices that can delimit a function signature."""
    ignored = {
        token.ENCODING,
        token.NL,
        token.NEWLINE,
        token.INDENT,
        token.DEDENT,
        token.COMMENT,
        token.ENDMARKER,
    }
    return [idx for idx, tok in enumerate(tokens) if tok.type not in ignored]


def _parameter_binding_indices(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    source_tokens: list[tokenize.TokenInfo],
) -> set[int]:
    """Locate parameter declaration tokens in the original PT token stream."""
    argument_names = {
        arg.arg
        for arg in (
            *getattr(node.args, "posonlyargs", []),
            *node.args.args,
            *node.args.kwonlyargs,
        )
    }
    if node.args.vararg:
        argument_names.add(node.args.vararg.arg)
    if node.args.kwarg:
        argument_names.add(node.args.kwarg.arg)
    if not argument_names:
        return set()

    meaningful = _meaningful_token_indices(source_tokens)
    definition_index = None
    for position, idx in enumerate(meaningful):
        tok = source_tokens[idx]
        if tok.start[0] != node.lineno or tok.type != token.NAME:
            continue
        if tok.string not in ("funcao", "função", "def"):
            continue
        if position + 1 < len(meaningful):
            next_tok = source_tokens[meaningful[position + 1]]
            if next_tok.type == token.NAME and next_tok.string == node.name:
                definition_index = idx
                break
    if definition_index is None:
        return set()

    open_index = None
    for idx in range(definition_index + 1, len(source_tokens)):
        tok = source_tokens[idx]
        if tok.type == token.OP and tok.string == "(":
            open_index = idx
            break
        if tok.type in (token.NEWLINE, token.INDENT, token.DEDENT):
            break
    if open_index is None:
        return set()

    depth = 0
    close_index = None
    for idx in range(open_index, len(source_tokens)):
        tok = source_tokens[idx]
        if tok.type != token.OP:
            continue
        if tok.string == "(":
            depth += 1
        elif tok.string == ")":
            depth -= 1
            if depth == 0:
                close_index = idx
                break
    if close_index is None:
        return set()

    result = set()
    segment: list[int] = []
    nested_depth = 0

    def mark_segment(indices: list[int]) -> None:
        for candidate_index in indices:
            candidate = source_tokens[candidate_index]
            if candidate.type == token.NAME:
                if candidate.string in argument_names:
                    result.add(candidate_index)
                break

    for idx in range(open_index + 1, close_index):
        tok = source_tokens[idx]
        if tok.type == token.OP:
            if tok.string in "([{":
                nested_depth += 1
            elif tok.string in ")]}":
                nested_depth = max(0, nested_depth - 1)
            elif tok.string == "," and nested_depth == 0:
                mark_segment(segment)
                segment = []
                continue
        segment.append(idx)
    mark_segment(segment)
    return result


def _lambda_parameter_binding_indices(
    node: ast.Lambda,
    source_tokens: list[tokenize.TokenInfo],
    canonical_lines: list[str],
    source_lines: dict[int, str],
) -> set[int]:
    """Locate lambda parameter declarations in the original PT token stream."""
    argument_names = {
        arg.arg
        for arg in (
            *getattr(node.args, "posonlyargs", []),
            *node.args.args,
            *node.args.kwonlyargs,
        )
    }
    if node.args.vararg:
        argument_names.add(node.args.vararg.arg)
    if node.args.kwarg:
        argument_names.add(node.args.kwarg.arg)
    if not argument_names:
        return set()

    expected_column = _source_column_for_ast_node(
        node,
        canonical_lines,
        source_lines,
    )
    lambda_candidates = [
        idx
        for idx, tok in enumerate(source_tokens)
        if tok.type == token.NAME
        and tok.string == "lambda"
        and tok.start[0] == node.lineno
    ]
    if not lambda_candidates:
        return set()
    lambda_index = min(
        lambda_candidates,
        key=lambda idx: abs(source_tokens[idx].start[1] - expected_column),
    )

    result = set()
    segment: list[int] = []
    nested_depth = 0

    def mark_segment(indices: list[int]) -> None:
        for candidate_index in indices:
            candidate = source_tokens[candidate_index]
            if candidate.type == token.NAME:
                if candidate.string in argument_names:
                    result.add(candidate_index)
                break

    for idx in range(lambda_index + 1, len(source_tokens)):
        tok = source_tokens[idx]
        if tok.type == token.OP:
            if tok.string in "([{":
                nested_depth += 1
            elif tok.string in ")]}":
                nested_depth = max(0, nested_depth - 1)
            elif tok.string == "," and nested_depth == 0:
                mark_segment(segment)
                segment = []
                continue
            elif tok.string == ":" and nested_depth == 0:
                mark_segment(segment)
                break
        segment.append(idx)
    return result


def _build_scope_context(
    canonical_syntax: str,
    source_tokens: list[tokenize.TokenInfo],
) -> tuple[list[_ScopeInfo], set[int], frozenset[str]]:
    """Build lexical binding context for canonical builtin substitution."""
    try:
        tree = ast.parse(canonical_syntax)
        module_table = symtable.symtable(canonical_syntax, "<codigo_pt>", "exec")
    except (SyntaxError, ValueError):
        return [], set(), frozenset()

    canonical_lines = canonical_syntax.splitlines()
    source_lines = {
        tok.start[0]: tok.line
        for tok in source_tokens
        if tok.line is not None
    }
    tables_by_key: dict[tuple[str, str, int], list[symtable.SymbolTable]] = {}
    for table in _all_symbol_tables(module_table):
        key = (table.get_type(), table.get_name(), table.get_lineno())
        tables_by_key.setdefault(key, []).append(table)

    scopes = []
    parameter_indices = set()
    for node in ast.walk(tree):
        key = _scope_key(node)
        span = _scope_span(node)
        if key is None or span is None:
            continue
        matching_tables = tables_by_key.get(key, [])
        if not matching_tables:
            continue
        table = matching_tables.pop(0)
        start_node, start_line, end_line = span
        scopes.append(
            _ScopeInfo(
                start_line=start_line,
                start_column=_source_column_for_ast_node(
                    start_node,
                    canonical_lines,
                    source_lines,
                ),
                end_line=end_line,
                protected_names=_protected_names(table, module_table),
            )
        )
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            parameter_indices.update(_parameter_binding_indices(node, source_tokens))
        elif isinstance(node, ast.Lambda):
            parameter_indices.update(
                _lambda_parameter_binding_indices(
                    node,
                    source_tokens,
                    canonical_lines,
                    source_lines,
                )
            )

    return scopes, parameter_indices, _protected_names(module_table, module_table)


def _substitui_em_fstring(
    literal_fstring: str,
    protected_names: frozenset[str] = frozenset(),
) -> str:
    """Traduz expressões interpoladas dentro de f-strings para Python canônico."""
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

            try:
                expr_traduzida = _transpila_core(
                    expr_bruta,
                    traduzir_builtins=True,
                    protected_names=protected_names,
                ).strip()
            except Exception:
                expr_traduzida = expr_bruta

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

    scope_infos: list[_ScopeInfo] = []
    parameter_indices: set[int] = set()
    inherited_protected_names = protected_names or frozenset()
    module_protected_names = inherited_protected_names
    if traduzir_builtins:
        canonical_syntax = _transpila_core(codigo_pt, traduzir_builtins=False)
        (
            scope_infos,
            parameter_indices,
            discovered_module_names,
        ) = _build_scope_context(
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
                tokens_saida.append((token.NAME, "elif"))
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
                    tokens_saida.append((token.NAME, "is"))
                    tokens_saida.append((token.NAME, "not"))
                else:
                    tokens_saida.append((token.OP, "!="))
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
                    tokens_saida.append((token.NAME, "is"))
                else:
                    tokens_saida.append((token.OP, "=="))
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

        elif tipo == token.STRING and traduzir_builtins:
            valor = _substitui_em_fstring(
                valor,
                names_protected_for(tok),
            )

        tokens_saida.append((tipo, valor))
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
    tamanho -> len, etc.), permitindo execução pura sem necessidade do pacote transpilador_pt.
    """
    return _transpila_core(codigo_pt, traduzir_builtins=True)


def palavra_e_reservada_em_pt(nome: str) -> bool:
    """Útil para avisar o usuário se ele tentar nomear uma variável
    com uma palavra que é reservada nesta camada (ex.: 'para', 'em', 'eh')."""
    return nome in MAPA or nome in ("eh", "é") or keyword.iskeyword(nome)
