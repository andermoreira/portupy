#!/usr/bin/env python3
"""Uso: python3 cli.py caminho/arquivo.ptpy [--mostrar-python]"""
import sys

from transpilador_pt.executor import executa_arquivo


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python3 cli.py arquivo.ptpy [--mostrar-python]", file=sys.stderr)
        return 1

    return executa_arquivo(sys.argv[1], mostrar_python="--mostrar-python" in sys.argv)


if __name__ == "__main__":
    sys.exit(main())
