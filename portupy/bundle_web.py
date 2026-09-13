"""Gerador do bundle estático dos arquivos do PortuPy para a Web.

Empacota o código-fonte puro do pacote portupy em um arquivo JavaScript
para que o Pyodide possa montá-lo diretamente no seu sistema de arquivos virtual Wasm.
"""

from __future__ import annotations

import json
from pathlib import Path

from .dicionario import conjuntos_de_destaque

MARCADOR_INTEGRIDADE_INICIO = "/* pyodide-integrity:begin */"
MARCADOR_INTEGRIDADE_FIM = "/* pyodide-integrity:end */"
PREFIXO_PATH_PYODIDE = "/vendor/pyodide/"

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


def hashes_pyodide_do_manifesto(pasta_web: Path) -> dict[str, str]:
    """Read sha256 hashes from the vendored Pyodide manifest."""
    manifesto = json.loads(
        (pasta_web / "vendor" / "pyodide" / "manifest.json").read_text(encoding="utf-8")
    )
    hashes = {
        PREFIXO_PATH_PYODIDE + arquivo["path"]: arquivo["sha256"]
        for arquivo in manifesto["files"]
    }
    if not hashes:
        raise ValueError("Manifesto Pyodide sem arquivos.")
    return hashes


def bloco_integridade_pyodide(hashes: dict[str, str]) -> str:
    corpo = json.dumps(hashes, indent=2, sort_keys=True)
    return (
        f"{MARCADOR_INTEGRIDADE_INICIO}\n"
        f"const PYODIDE_INTEGRITY = {corpo};\n"
        f"{MARCADOR_INTEGRIDADE_FIM}"
    )


def aplica_integridade_service_worker(
    caminho_sw: str | Path,
    hashes: dict[str, str],
) -> None:
    """Replace the integrity block embedded in the service worker script."""
    caminho_sw = Path(caminho_sw)
    texto = caminho_sw.read_text(encoding="utf-8")
    inicio = texto.find(MARCADOR_INTEGRIDADE_INICIO)
    fim = texto.find(MARCADOR_INTEGRIDADE_FIM)
    if inicio == -1 or fim == -1 or fim < inicio:
        raise ValueError("Marcadores de integridade ausentes no service worker.")
    fim += len(MARCADOR_INTEGRIDADE_FIM)
    caminho_sw.write_text(
        texto[:inicio] + bloco_integridade_pyodide(hashes) + texto[fim:],
        encoding="utf-8",
    )


if __name__ == "__main__":
    destino = gera_bundle_web()
    pasta_web = destino.parent
    aplica_integridade_service_worker(
        pasta_web / "service-worker.js",
        hashes_pyodide_do_manifesto(pasta_web),
    )
    print(f"✨ Bundle web gerado com sucesso em: {destino}")
