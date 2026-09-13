"""Módulo de servidor web local para o Playground do Transpilador PT.

Fornece um servidor HTTP estático leve baseado na stdlib para executar
e testar a aplicação WebAssembly localmente com auto-alocação de portas.
"""

from __future__ import annotations

import functools
import http.server
import socket
import socketserver
import threading
import time
import webbrowser
from pathlib import Path

HOST_LOCAL = "127.0.0.1"


class PlaygroundTCPServer(socketserver.TCPServer):
    """Servidor do playground restrito à interface de loopback."""

    allow_reuse_address = True


class PlaygroundHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler HTTP customizado com mapeamento de tipos MIME adequados para Wasm/Web."""

    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "application/javascript",
        ".mjs": "application/javascript",
        ".wasm": "application/wasm",
        ".css": "text/css",
        ".html": "text/html; charset=utf-8",
        ".ptpy": "text/plain; charset=utf-8",
        ".json": "application/json",
    }

    def log_message(self, format: str, *args) -> None:
        """Silencia logs padrão de requisição para manter o terminal limpo."""
        pass


def encontra_porta_disponivel(porta_inicial: int = 8000, max_tentativas: int = 10) -> int:
    """Procura a primeira porta livre a partir da porta_inicial."""
    if not 0 <= porta_inicial <= 65535:
        raise ValueError("A porta deve estar entre 0 e 65535.")
    if max_tentativas < 1:
        raise ValueError("A quantidade de tentativas deve ser positiva.")
    if porta_inicial == 0:
        return 0

    ultima_porta = min(65535, porta_inicial + max_tentativas - 1)
    for porta in range(porta_inicial, ultima_porta + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((HOST_LOCAL, porta))
                return porta
            except OSError:
                continue
    raise OSError(
        f"Não foi possível encontrar uma porta disponível após {max_tentativas} tentativas "
        f"(iniciando em {porta_inicial})."
    )


def cria_servidor_web(
    diretorio: str | Path,
    porta: int = 8000,
) -> tuple[socketserver.TCPServer, int]:
    """Cria e vincula o servidor HTTP estático no diretório especificado."""
    caminho_dir = Path(diretorio).resolve()
    if not caminho_dir.is_dir():
        raise FileNotFoundError(f"Diretório web não encontrado: {caminho_dir}")
    if not 0 <= porta <= 65535:
        raise ValueError("A porta deve estar entre 0 e 65535.")

    handler = functools.partial(PlaygroundHTTPRequestHandler, directory=str(caminho_dir))

    if porta == 0:
        portas = (0,)
    else:
        ultima_porta = min(65535, porta + 9)
        portas = range(porta, ultima_porta + 1)

    ultimo_erro = None
    for porta_tentativa in portas:
        try:
            httpd = PlaygroundTCPServer((HOST_LOCAL, porta_tentativa), handler)
            return httpd, int(httpd.server_address[1])
        except OSError as exc:
            ultimo_erro = exc

    raise OSError(
        f"Não foi possível iniciar o servidor em uma porta disponível "
        f"a partir de {porta}."
    ) from ultimo_erro


def inicia_servidor_web(
    diretorio: str | Path,
    porta: int = 8000,
    abrir_navegador: bool = True,
    bloquear: bool = True,
) -> tuple[socketserver.TCPServer, int]:
    """Inicia o servidor web local para o Playground.

    Args:
        diretorio: Caminho para os arquivos estáticos (HTML/CSS/JS).
        porta: Porta desejada inicial (padrão: 8000).
        abrir_navegador: Se True, abre automaticamente no navegador padrão.
        bloquear: Se True, executa `serve_forever()` bloqueando a thread atual.

    Returns:
        Tupla (instancia_servidor, porta_utilizada).
    """
    httpd, porta_usada = cria_servidor_web(diretorio, porta=porta)
    url = f"http://localhost:{porta_usada}"

    print(f"🌐 Transpilador PT Playground iniciado!")
    print(f"👉 Acesse: {url}")
    print("Pressione Ctrl+C para encerrar o servidor.\n")

    if abrir_navegador:
        def _abrir():
            time.sleep(0.2)
            webbrowser.open(url)

        threading.Thread(target=_abrir, daemon=True).start()

    if bloquear:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Servidor encerrado.")
        finally:
            httpd.server_close()
    else:
        threading.Thread(target=httpd.serve_forever, daemon=True).start()

    return httpd, porta_usada
