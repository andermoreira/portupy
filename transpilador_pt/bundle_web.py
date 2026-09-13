"""Gerador do bundle estático dos arquivos do Transpilador PT para a Web.

Empacota o código-fonte puro do pacote transpilador_pt em um arquivo JavaScript
para que o Pyodide possa montá-lo diretamente no seu sistema de arquivos virtual Wasm.
"""

from __future__ import annotations

import json
from pathlib import Path

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
    """Lê os módulos de transpilador_pt e gera web/bundle_pt.js."""
    raiz_projeto = Path(__file__).resolve().parent.parent
    pasta_origem = raiz_projeto / "transpilador_pt"
    
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

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    conteudo_json = json.dumps(fontes, ensure_ascii=False, indent=2)
    conteudo_js = (
        "// Gerado automaticamente por transpilador_pt/bundle_web.py — não editar manualmente\n"
        f"window.TRANSPILADOR_PT_SOURCES = {conteudo_json};\n"
        f"window.TRANSPILADOR_PT_EXEMPLOS = {json.dumps(exemplos, ensure_ascii=False, indent=2)};\n"
    )

    caminho_saida.write_text(conteudo_js, encoding="utf-8")
    return caminho_saida


if __name__ == "__main__":
    destino = gera_bundle_web()
    print(f"✨ Bundle web gerado com sucesso em: {destino}")
