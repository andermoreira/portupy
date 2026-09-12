#!/usr/bin/env python3
"""Interface de linha de comando para o Transpilador PT.

Uso:
    python3 cli.py arquivo.ptpy [--mostrar-python] [--lado-a-lado] [--exportar [destino.py]]
"""

from __future__ import annotations

import sys

from transpilador_pt import (
    ErroDeTraducao,
    executa_arquivo,
    renderiza_lado_a_lado,
    transpila_canonico,
)


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(
            "Uso: python3 cli.py arquivo.ptpy [--mostrar-python] [--lado-a-lado] [--exportar [destino.py]]",
            file=sys.stderr,
        )
        return 1

    # Identifica o arquivo de entrada (primeiro argumento posicional não-flag)
    caminho_pt = None
    for arg in args:
        if not arg.startswith("--"):
            caminho_pt = arg
            break

    if caminho_pt is None:
        print("Erro: nenhum arquivo de entrada informado.", file=sys.stderr)
        return 1

    # Modo Exportar (--exportar [destino.py])
    if "--exportar" in args:
        idx = args.index("--exportar")
        destino = None
        if idx + 1 < len(args) and not args[idx + 1].startswith("--"):
            destino = args[idx + 1]

        try:
            with open(caminho_pt, "r", encoding="utf-8") as f:
                codigo_pt = f.read()
        except OSError as exc:
            print(f"Não consegui ler o arquivo: {exc}", file=sys.stderr)
            return 1

        try:
            codigo_py = transpila_canonico(codigo_pt)
        except ErroDeTraducao as exc:
            print(f"Erro ao traduzir: {exc}", file=sys.stderr)
            return 1

        if destino is None:
            print(codigo_py)
            return 0

        try:
            with open(destino, "w", encoding="utf-8") as f:
                f.write(codigo_py)
            print(f"✨ Código Python canônico exportado com sucesso para: {destino}")
            return 0
        except OSError as exc:
            print(f"⚠️ Não consegui salvar o arquivo exportado: {exc}", file=sys.stderr)
            return 1

    # Modo Lado a Lado / Transição (--lado-a-lado ou --modo-transicao)
    if "--lado-a-lado" in args or "--modo-transicao" in args:
        try:
            with open(caminho_pt, "r", encoding="utf-8") as f:
                codigo_pt = f.read()
            codigo_py = transpila_canonico(codigo_pt)
            print(renderiza_lado_a_lado(codigo_pt, codigo_py))
            print()
        except OSError as exc:
            print(f"Não consegui ler o arquivo: {exc}", file=sys.stderr)
            return 1
        except ErroDeTraducao as exc:
            print(f"Erro ao traduzir: {exc}", file=sys.stderr)
            return 1

    mostrar_python = "--mostrar-python" in args
    return executa_arquivo(caminho_pt, mostrar_python=mostrar_python)


if __name__ == "__main__":
    sys.exit(main())
