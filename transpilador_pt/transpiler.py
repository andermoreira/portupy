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

from .dicionario import MAPA


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
            elif tok.string in ASSIGNMENT_OPERATORS:
                return True
        elif tok.type == token.NEWLINE and nesting == 0:
            return False
    return False


def transpila(codigo_pt: str) -> str:
    """Converte código-fonte em português para código Python equivalente.

    Preserva números de linha 1:1 com o original, o que permite que
    tracebacks apontem para a linha certa do arquivo .ptpy do usuário.
    """
    tokens_saida = []
    leitor = io.StringIO(codigo_pt).readline

    try:
        fluxo = list(tokenize.generate_tokens(leitor))
    except (tokenize.TokenError, IndentationError) as exc:
        raise ErroDeTraducao(f"Não consegui interpretar o código: {exc}") from exc

    for i, tok in enumerate(fluxo):
        tipo, valor, inicio, fim, linha = tok

        # Se for precedido por '.', é acesso ou definição de atributo (ex.: obj.se, self.tipo = 1)
        # e não deve sofrer substituição nem checagem de palavra reservada.
        anterior = fluxo[i - 1] if i > 0 else None
        eh_atributo = anterior is not None and anterior.type == token.OP and anterior.string == "."

        if tipo == token.NAME and valor in MAPA and not eh_atributo:
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

        tokens_saida.append((tipo, valor))

    try:
        return tokenize.untokenize(tokens_saida)
    except ValueError as exc:
        raise ErroDeTraducao(f"Falha ao remontar o código traduzido: {exc}") from exc


def palavra_e_reservada_em_pt(nome: str) -> bool:
    """Útil para avisar o usuário se ele tentar nomear uma variável
    com uma palavra que é reservada nesta camada (ex.: 'para', 'em')."""
    return nome in MAPA or keyword.iskeyword(nome)
