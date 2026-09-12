from __future__ import annotations

import sys

from .dicionario import BUILTINS_PT
from .erros import formata_erro_amigavel
from .transpiler import ErroDeTraducao, transpila


def executa_codigo(codigo_pt: str, mostrar_python: bool = False) -> None:
    linhas_fonte_pt = codigo_pt.splitlines()

    try:
        codigo_python = transpila(codigo_pt)
    except ErroDeTraducao as exc:
        print(f"⚠️  Erro ao traduzir seu código: {exc}")
        return

    if mostrar_python:
        print("--- código Python gerado ---")
        print(codigo_python)
        print("----------------------------")

    try:
        # nome de arquivo especial: é assim que formata_erro_amigavel
        # reconhece qual frame do traceback pertence ao código do usuário
        compilado = compile(codigo_python, "<codigo_pt>", "exec")
        contexto = {"__name__": "__main__", **BUILTINS_PT}
        exec(compilado, contexto)
    except Exception as exc:
        print(formata_erro_amigavel(exc, linhas_fonte_pt))


def executa_arquivo(caminho: str, mostrar_python: bool = False) -> None:
    with open(caminho, "r", encoding="utf-8") as f:
        codigo_pt = f.read()
    executa_codigo(codigo_pt, mostrar_python=mostrar_python)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python -m transpilador_pt.executor arquivo.ptpy [--mostrar-python]")
        sys.exit(1)
    executa_arquivo(sys.argv[1], mostrar_python="--mostrar-python" in sys.argv)
