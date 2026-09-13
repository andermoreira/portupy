import http.client
import socket
import tempfile
import threading
import unittest
from pathlib import Path

from transpilador_pt.servidor import (
    PlaygroundHTTPRequestHandler,
    cria_servidor_web,
    encontra_porta_disponivel,
    inicia_servidor_web,
)


class TestServidorWeb(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path_temp = Path(self.temp_dir.name)
        # Cria um arquivo estático para testar
        (self.path_temp / "index.html").write_text("<h1>Playground</h1>", encoding="utf-8")
        (self.path_temp / "teste.ptpy").write_text("mostre('ola')", encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_encontra_porta_disponivel_livre(self):
        """Valida que encontra uma porta livre a partir de um valor base."""
        porta = encontra_porta_disponivel(8800)
        self.assertGreaterEqual(porta, 8800)

    def test_encontra_porta_disponivel_pula_ocupada(self):
        """Valida que pula a porta inicial se ela estiver em uso por outro processo/socket."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", 8880))
        s.listen(1)
        try:
            # Deve detectar 8880 ocupada e retornar 8881
            proxima = encontra_porta_disponivel(8880)
            self.assertEqual(8881, proxima)
        finally:
            s.close()

    def test_encontra_porta_disponivel_rejeita_tentativas_invalidas(self):
        """A busca de portas exige pelo menos uma tentativa."""
        with self.assertRaises(ValueError):
            encontra_porta_disponivel(8880, max_tentativas=0)

    def test_cria_servidor_web_diretorio_inexistente(self):
        """Valida que levanta FileNotFoundError para diretório inválido."""
        with self.assertRaises(FileNotFoundError):
            cria_servidor_web("/diretorio/inexistente/transpilador_pt_nao_existe", porta=8900)

    def test_cria_servidor_web_rejeita_porta_fora_do_intervalo(self):
        """A criação do servidor aplica a mesma validação da busca de portas."""
        with self.assertRaises(ValueError):
            cria_servidor_web(self.path_temp, porta=65536)

    def test_cria_servidor_web_sucesso_e_requisicao_http(self):
        """Valida criação de servidor e resposta HTTP de arquivos estáticos."""
        httpd, porta = cria_servidor_web(self.path_temp, porta=8920)
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        try:
            conn = http.client.HTTPConnection("127.0.0.1", porta, timeout=2)
            conn.request("GET", "/index.html")
            res = conn.getresponse()
            self.assertEqual(200, res.status)
            corpo = res.read().decode("utf-8")
            self.assertIn("Playground", corpo)
        finally:
            httpd.shutdown()
            httpd.server_close()

    def test_mime_types_customizados(self):
        """Valida que extensões essenciais possuem MIME types definidos."""
        exts = PlaygroundHTTPRequestHandler.extensions_map
        self.assertEqual("application/javascript", exts.get(".js"))
        self.assertEqual("application/wasm", exts.get(".wasm"))
        self.assertIn("text/plain", exts.get(".ptpy"))

    def test_inicia_servidor_web_nao_bloqueante(self):
        """Valida inicialização com flag bloquear=False para uso programático."""
        httpd, porta = inicia_servidor_web(
            self.path_temp,
            porta=8950,
            abrir_navegador=False,
            bloquear=False,
        )
        try:
            self.assertGreaterEqual(porta, 8950)
            conn = http.client.HTTPConnection("127.0.0.1", porta, timeout=2)
            conn.request("GET", "/index.html")
            self.assertEqual(200, conn.getresponse().status)
        finally:
            httpd.shutdown()
            httpd.server_close()

    def test_cria_servidor_web_porta_dinamica_retorna_porta_real(self):
        """Porta 0 deve retornar a porta efêmera efetivamente vinculada."""
        httpd, porta = cria_servidor_web(self.path_temp, porta=0)
        try:
            self.assertGreater(porta, 0)
            self.assertEqual(porta, httpd.server_address[1])
        finally:
            httpd.server_close()


if __name__ == "__main__":
    unittest.main()
