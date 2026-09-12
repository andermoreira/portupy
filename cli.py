#!/usr/bin/env python3
"""Uso: python3 cli.py caminho/arquivo.ptpy [--mostrar-python]"""
import sys

from transpilador_pt.executor import executa_arquivo

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 cli.py arquivo.ptpy [--mostrar-python]")
        sys.exit(1)
    executa_arquivo(sys.argv[1], mostrar_python="--mostrar-python" in sys.argv)
