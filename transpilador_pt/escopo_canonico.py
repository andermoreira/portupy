"""Análise de escopo léxico para a exportação canônica (ADR-003).

Extraído de ``transpiler.py`` para isolar uma responsabilidade coesa: mapear,
via ``ast`` e ``symtable``, quais nomes de cada escopo devem manter a grafia em
português (parâmetros, locais, nomes que sombreiam builtins) e localizar, no
fluxo de tokens original em PT, as declarações de parâmetros. O núcleo léxico
do transpilador consome apenas ``ScopeInfo`` e ``build_scope_context``.

Este módulo é puramente derivado da stdlib e não depende do dicionário de
tradução nem do núcleo léxico, mantendo a dependência em sentido único
(transpiler -> escopo_canonico).
"""

from __future__ import annotations

import ast
import difflib
import symtable
import token
import tokenize
from dataclasses import dataclass


@dataclass(frozen=True)
class ScopeInfo:
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


def build_scope_context(
    canonical_syntax: str,
    source_tokens: list[tokenize.TokenInfo],
) -> tuple[list[ScopeInfo], set[int], frozenset[str]]:
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
            ScopeInfo(
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
