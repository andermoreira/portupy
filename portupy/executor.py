from __future__ import annotations

import sys

from .dicionario import BUILTINS_PT
from .erros import formata_erro_amigavel
from .transpiler import ErroDeTraducao, transpila


def executa_codigo(codigo_pt: str, mostrar_python: bool = False) -> int:
    """Traduz e executa código-fonte em português no processo Python atual.

    Segurança (decisão deliberada): a execução NÃO é isolada. O código roda com
    `exec` no mesmo processo e com acesso aos builtins reais do Python (além dos
    curados em `BUILTINS_PT`), permitindo `importe`, entrada/saída e acesso ao
    sistema de arquivos — recursos necessários à missão pedagógica de servir como
    rampa para o Python real (ver ADR-001/003). Restringir `__builtins__` daria
    apenas uma falsa sensação de sandbox (é contornável) e mutilaria esses
    recursos. Destina-se a scripts locais confiáveis, como `python3 arquivo.py`.
    No playground web o código roda em WebAssembly no navegador do aluno, fora
    do sistema de arquivos da máquina — isso reduz a superfície da CLI, mas não
    é garantia absoluta de sandbox (ver ADR-004). Ver também o aviso no README.
    """
    linhas_fonte_pt = codigo_pt.splitlines()

    try:
        codigo_python = transpila(codigo_pt)
    except ErroDeTraducao as exc:
        print(f"⚠️  Erro ao traduzir seu código: {exc}", file=sys.stderr)
        return 1

    if mostrar_python:
        print("--- código Python gerado ---")
        print(codigo_python)
        print("----------------------------")

    try:
        # nome de arquivo especial: é assim que formata_erro_amigavel
        # reconhece qual frame do traceback pertence ao código do usuário
        compilado = compile(codigo_python, "<codigo_pt>", "exec")
        # Sem '__builtins__' restrito: o Python injeta os builtins reais, o que é
        # intencional (não é sandbox). Ver a docstring da função para o porquê.
        contexto = {"__name__": "__main__", **BUILTINS_PT}
        exec(compilado, contexto)
    except Exception as exc:
        print(
            formata_erro_amigavel(exc, linhas_fonte_pt, codigo_python.splitlines()),
            file=sys.stderr,
        )
        return 1

    return 0


def executa_arquivo(caminho: str, mostrar_python: bool = False) -> int:
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            codigo_pt = f.read()
    except (OSError, UnicodeError):
        print("⚠️  Não consegui ler o arquivo informado.", file=sys.stderr)
        return 1

    return executa_codigo(codigo_pt, mostrar_python=mostrar_python)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Uso: python -m portupy.executor arquivo.ptpy [--mostrar-python]",
            file=sys.stderr,
        )
        sys.exit(1)
    sys.exit(executa_arquivo(sys.argv[1], mostrar_python="--mostrar-python" in sys.argv))
