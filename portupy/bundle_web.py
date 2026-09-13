"""Gerador do bundle estático dos arquivos do PortuPy para a Web.

Empacota o código-fonte puro do pacote portupy em um arquivo JavaScript
para que o Pyodide possa montá-lo diretamente no seu sistema de arquivos virtual Wasm.
"""

from __future__ import annotations

import json
from pathlib import Path

from .dicionario import conjuntos_de_destaque

ARQUIVOS_MODULO = [
    "__init__.py",
    "dicionario.py",
    "escopo_canonico.py",
    "transpiler.py",
    "transicao.py",
    "erros.py",
    "executor.py",
]

PASTA_EXEMPLOS = Path(__file__).resolve().parent / "exemplos"
ARQUIVOS_EXEMPLOS = tuple(
    caminho.name for caminho in sorted(PASTA_EXEMPLOS.glob("*.ptpy"))
)


def gera_bundle_web(caminho_saida: str | Path | None = None) -> Path:
    """Lê os módulos de portupy e gera web/bundle_pt.js."""
    pasta_origem = Path(__file__).resolve().parent
    raiz_projeto = pasta_origem.parent

    if caminho_saida is None:
        caminho_saida = raiz_projeto / "web" / "bundle_pt.js"
    else:
        caminho_saida = Path(caminho_saida)

    fontes: dict[str, str] = {}
    for nome_arquivo in ARQUIVOS_MODULO:
        caminho_arq = pasta_origem / nome_arquivo
        if caminho_arq.is_file():
            fontes[nome_arquivo] = caminho_arq.read_text(encoding="utf-8")
        else:
            raise FileNotFoundError(f"Arquivo necessário do módulo não encontrado: {caminho_arq}")

    exemplos: dict[str, str] = {}
    for nome_arquivo in ARQUIVOS_EXEMPLOS:
        caminho_exemplo = PASTA_EXEMPLOS / nome_arquivo
        exemplos[Path(nome_arquivo).stem] = caminho_exemplo.read_text(encoding="utf-8")

    destaque = conjuntos_de_destaque()

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    conteudo_json = json.dumps(fontes, ensure_ascii=False, indent=2)
    conteudo_js = (
        "// Gerado automaticamente por portupy/bundle_web.py — não editar manualmente\n"
        f"window.PORTUPY_SOURCES = {conteudo_json};\n"
        f"window.PORTUPY_EXEMPLOS = {json.dumps(exemplos, ensure_ascii=False, indent=2)};\n"
        f"window.PORTUPY_DESTAQUE = {json.dumps(destaque, ensure_ascii=False, indent=2)};\n"
    )

    caminho_saida.write_text(conteudo_js, encoding="utf-8")
    return caminho_saida


if __name__ == "__main__":
    destino = gera_bundle_web()
    print(f"✨ Bundle web gerado com sucesso em: {destino}")
