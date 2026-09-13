"""Módulo de transição pedagógica bilíngue (Português -> Python Canônico).

Fornece renderização visual comparativa lado a lado com numeração de linhas,
permitindo ao estudante entender a correspondência direta entre as linguagens.
"""

from __future__ import annotations

import itertools
import shutil


def _trunca(texto: str, largura: int) -> str:
    """Trunca o texto caso exceda a largura permitida, adicionando reticências."""
    if len(texto) <= largura:
        return texto
    if largura <= 3:
        return texto[:largura]
    return texto[: largura - 1] + "…"


def _renderiza_empilhado(
    codigo_pt: str,
    codigo_py: str,
    largura_terminal: int,
) -> str:
    """Renderiza cada idioma em sua própria seção em terminais estreitos."""
    largura = max(1, largura_terminal)
    linhas_pt = codigo_pt.splitlines()
    linhas_py = codigo_py.splitlines()
    total_linhas = max(len(linhas_pt), len(linhas_py), 1)
    largura_num = max(1, len(str(total_linhas)))

    def renderiza_secao(titulo: str, linhas: list[str]) -> list[str]:
        resultado = [_trunca(titulo, largura)]
        for idx, linha in enumerate(linhas, start=1):
            prefixo = f"{idx:>{largura_num}} │ "
            resultado.append(
                _trunca(
                    prefixo + _trunca(linha, max(1, largura - len(prefixo))),
                    largura,
                )
            )
        return resultado

    aviso = "Aviso: terminal estreito; colunas empilhadas e linhas truncadas."
    linhas_saida = [_trunca(aviso, largura)]
    linhas_saida.extend(renderiza_secao("Código em Português", linhas_pt))
    linhas_saida.extend(renderiza_secao("Python Canônico", linhas_py))
    return "\n".join(linhas_saida)


def renderiza_lado_a_lado(
    codigo_pt: str,
    codigo_py: str,
    largura_terminal: int | None = None,
) -> str:
    """Renderiza os códigos em português e Python canônico lado a lado em duas colunas.

    Args:
        codigo_pt: Código-fonte original em português.
        codigo_py: Código Python canônico gerado.
        largura_terminal: Largura total em colunas (obtida dinamicamente se None).

    Returns:
        String formatada com tabela comparativa pronta para exibição no terminal.
    """
    if largura_terminal is None:
        largura_terminal = shutil.get_terminal_size(fallback=(80, 24)).columns

    largura_terminal = max(1, largura_terminal)
    if largura_terminal < 60:
        return _renderiza_empilhado(codigo_pt, codigo_py, largura_terminal)

    linhas_pt = codigo_pt.splitlines()
    linhas_py = codigo_py.splitlines()
    total_linhas = max(len(linhas_pt), len(linhas_py), 1)

    largura_num = max(3, len(str(total_linhas)))
    largura_col_num = max(largura_num, len("Linha"))
    # Formato de cada linha: ' {num} │ {pt} │ {py}'
    # Espaço consumido por margens e separadores: largura_col_num + 7.
    largura_fixa = largura_col_num + 7
    espaco_colunas = max(20, largura_terminal - largura_fixa)
    largura_col_pt = espaco_colunas // 2
    largura_col_py = espaco_colunas - largura_col_pt

    # Títulos das colunas
    titulo_pt = "Código em Português" if largura_col_pt >= 20 else "Português"
    titulo_py = "Python Canônico" if largura_col_py >= 16 else "Python"

    cabecalho_num = f"{'Linha':>{largura_col_num}}"
    cabecalho_pt = f"{titulo_pt:<{largura_col_pt}}"
    cabecalho_py = f"{titulo_py:<{largura_col_py}}"

    cabecalho = f" {cabecalho_num} │ {cabecalho_pt} │ {cabecalho_py}"
    divisor = f"{'─' * (largura_col_num + 2)}┼{'─' * (largura_col_pt + 2)}┼{'─' * (largura_col_py + 1)}"

    linhas_saida = [cabecalho, divisor]

    for idx, (l_pt, l_py) in enumerate(
        itertools.zip_longest(linhas_pt, linhas_py, fillvalue=""),
        start=1,
    ):
        num_str = f"{idx:>{largura_col_num}}"
        col_pt = _trunca(l_pt, largura_col_pt)
        col_py = _trunca(l_py, largura_col_py)
        linha_formatada = (
            f" {num_str} │ {col_pt:<{largura_col_pt}} │ {col_py:<{largura_col_py}}"
        )
        linhas_saida.append(linha_formatada)

    return "\n".join(linhas_saida)
