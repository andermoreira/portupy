#!/usr/bin/env python3
"""Interface de linha de comando para o PortuPy.

Uso:
    python3 cli.py arquivo.ptpy [--mostrar-python] [--lado-a-lado] [--exportar [destino.py]]
    python3 cli.py --web [porta] [--sem-navegador]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from portupy import (
    ErroDeTraducao,
    __version__,
    executa_arquivo,
    renderiza_lado_a_lado,
    transpila_canonico,
)
from portupy.servidor import inicia_servidor_web


MENSAGEM_USO = (
    "Uso: python3 cli.py [arquivo.ptpy | --web [porta]] "
    "[--mostrar-python] [--lado-a-lado] [--exportar [destino.py]]"
)


def _porta_argumento(valor: str) -> int:
    try:
        porta = int(valor)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"porta inválida '{valor}'") from exc
    if not 0 <= porta <= 65535:
        raise argparse.ArgumentTypeError("porta inválida: use um valor entre 0 e 65535")
    return porta


def cria_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="portupy",
        description="Traduz e executa código Python escrito em português.",
    )
    parser.add_argument(
        "arquivo",
        nargs="?",
        help="arquivo .ptpy para executar ou exportar",
    )
    parser.add_argument(
        "--web",
        nargs="?",
        const=8000,
        type=_porta_argumento,
        metavar="PORTA",
        help="inicia o playground web na porta informada (padrão: 8000)",
    )
    parser.add_argument(
        "--sem-navegador",
        action="store_true",
        help="não abre o navegador automaticamente ao iniciar o playground",
    )
    parser.add_argument(
        "--mostrar-python",
        action="store_true",
        help="mostra o código Python intermediário antes da execução",
    )
    parser.add_argument(
        "--lado-a-lado",
        "--modo-transicao",
        dest="modo_transicao",
        action="store_true",
        help="mostra o código em português e o Python canônico lado a lado",
    )
    parser.add_argument(
        "--exportar",
        nargs="?",
        const="-",
        metavar="DESTINO",
        help="exporta para Python canônico; sem destino, imprime no stdout",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = cria_parser()
    argumentos = sys.argv[1:] if argv is None else argv
    try:
        args = parser.parse_args(argumentos)
    except SystemExit as exc:
        # Mantém a API testável e os códigos de saída da CLI sob controle.
        return 0 if exc.code == 0 else 1

    if not argumentos:
        print(MENSAGEM_USO, file=sys.stderr)
        return 1

    # Modo Playground Web (--web [porta])
    if args.web is not None:
        if args.arquivo or args.mostrar_python or args.modo_transicao or args.exportar is not None:
            print("Erro: --web não pode ser combinado com arquivo ou outros modos.", file=sys.stderr)
            return 1
        diretorio_web = Path(__file__).resolve().parent / "web"
        try:
            inicia_servidor_web(
                diretorio_web,
                porta=args.web,
                abrir_navegador=not args.sem_navegador,
                bloquear=True,
            )
            return 0
        except Exception as exc:
            print(f"⚠️ Erro ao iniciar servidor web: {exc}", file=sys.stderr)
            return 1

    if args.sem_navegador:
        print("Erro: --sem-navegador só pode ser usado com --web.", file=sys.stderr)
        return 1

    if args.arquivo is None:
        print("Erro: nenhum arquivo de entrada informado.", file=sys.stderr)
        return 1

    caminho_pt = args.arquivo

    # Modo Exportar (--exportar [destino.py])
    if args.exportar is not None:
        destino = None if args.exportar == "-" else args.exportar

        try:
            with open(caminho_pt, "r", encoding="utf-8") as f:
                codigo_pt = f.read()
        except (OSError, UnicodeError) as exc:
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
    if args.modo_transicao:
        try:
            with open(caminho_pt, "r", encoding="utf-8") as f:
                codigo_pt = f.read()
            codigo_py = transpila_canonico(codigo_pt)
            print(renderiza_lado_a_lado(codigo_pt, codigo_py))
            print()
        except (OSError, UnicodeError) as exc:
            print(f"Não consegui ler o arquivo: {exc}", file=sys.stderr)
            return 1

        except ErroDeTraducao as exc:
            print(f"Erro ao traduzir: {exc}", file=sys.stderr)
            return 1

    return executa_arquivo(caminho_pt, mostrar_python=args.mostrar_python)


if __name__ == "__main__":
    sys.exit(main())
