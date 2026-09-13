# Passo 1: Servidor web local leve e suíte de testes da CLI

## Contexto mínimo

O executor lê o contrato deste step. Implementar o módulo de servidor HTTP local leve utilizando exclusivamente a biblioteca padrão do Python (`http.server`, `socketserver`) e estabelecer a suíte de testes automatizados para a inicialização do Playground Web.

- Paths: [`transpilador_pt/servidor.py`], [`tests/test_cli_web.py`]
- Contrato: AC-07, AC-08, ADR-004
- Seam: Testes unitários com `unittest` da stdlib em `tests/test_cli_web.py`

## Goal

Criar a função `inicia_servidor_web(diretorio: str, porta: int = 8000, abrir_navegador: bool = True) -> None` em `transpilador_pt/servidor.py` e cobrir com testes automatizados em `tests/test_cli_web.py`, garantindo que o diretório `web/` possa ser servido localmente de forma limpa e segura com auto-detecção de porta disponível.

## Tarefas

1. Criar `transpilador_pt/servidor.py`:
   - Implementar `inicia_servidor_web(diretorio: str, porta: int = 8000, abrir_navegador: bool = True, max_tentativas: int = 10)`:
     - Configurar `http.server.SimpleHTTPRequestHandler` customizado com MIME types corretos (`.js`, `.css`, `.html`, `.wasm`, `.ptpy`).
     - Tentar vincular à porta informada; caso esteja em uso (`OSError` / `EADDRINUSE`), tentar a próxima porta incremental (até `max_tentativas`).
     - Exibir mensagem amigável no terminal: `🌐 Transpilador PT Playground disponível em: http://localhost:{porta}`.
     - Se `abrir_navegador` for True, disparar `webbrowser.open(...)` em thread separada com pequeno atraso (200ms).
     - Permitir encerramento gracioso via `KeyboardInterrupt` sem exibir traceback no terminal.
2. Criar `tests/test_cli_web.py`:
   - Testar resolução de porta livre quando a porta inicial estiver ocupada [AC-07].
   - Testar que o handler serve arquivos com cabeçalhos e MIME types adequados [AC-08].
   - Testar tratamento de encerramento gracioso (`KeyboardInterrupt`) [AC-07].

## Delta de complexidade planejado

- Abstrações: none
- Dependências: none (utiliza exclusivamente `http.server`, `socketserver`, `webbrowser`, `threading` da stdlib)
- Configuração: none
- Extension points: `inicia_servidor_web` exportada no pacote
- Camadas arquiteturais: camada de infraestrutura/servidor local (`servidor.py`)

## Fora de Escopo

- Criação dos arquivos de interface HTML/CSS (Step 2).
- Integração com Pyodide Wasm e JavaScript (Step 3).
- Modificação de `cli.py` e `README.md` (Step 4).

## Critério de Pronto

- `python3 -m unittest tests/test_cli_web.py` roda com 100% de sucesso.
- O servidor é capaz de subir, servir arquivos estáticos e encerrar sem vazar sockets.

## Seam de teste

- `tests/test_cli_web.py` via runner `unittest`.

## Dependências

- Spec da Fase 4 e ADR 004 aceitos.

## Documentation impact

- Nenhum nesta etapa (documentação consolidada no Step 4).

## Checklist pré-handoff

- [x] ≤ 5 arquivos lógicos afetados no total? (2 arquivos: `transpilador_pt/servidor.py`, `tests/test_cli_web.py`).
- [x] Rename inequívoco do Git conta um e delete+add/rename ambíguo conta dois?
- [x] O envelope operacional bloqueia o handoff acima de cinco, sem justificativa ou override?
- [x] O step mantém uma preocupação, estado válido e testes necessários, mesmo abaixo do teto?
- [x] O plano evitou fragmentação horizontal criada apenas para satisfazer file count?
- [x] Se uma unidade coerente não coube em fatias verticais válidas, o planejamento parou para decisão humana antes de gerar este handoff?
- [x] Paths reais no prompt (sem placeholders)?
- [x] Critério de pronto claro e testável?
- [x] O step declara o seam de teste (o mais alto possível, idealmente um) e o usuário confirmou?
- [x] Open questions da spec mestre não bloqueiam este passo?
- [x] Toda task e item não vazio do delta aponta para AC atual, ADR aceito ou restrição obrigatória, conforme `spec-process.md` § Contrato de rastreabilidade de escopo?
- [x] Considerações futuras permanecem fora das Tarefas e do delta planejado?

---

## Prompt Cursor

```text
@model-routing @token-budget

Implemente APENAS o passo abaixo — não expanda escopo.
Arquivos: @transpilador_pt/servidor.py @tests/test_cli_web.py
Fora de escopo: Modificar index.html, style.css ou app.js; bibliotecas externas.
Critério de pronto: python3 -m unittest tests/test_cli_web.py passa 100% verde.

---

@specs/steps/fase-4-playground-web-pyodide-step-1.md
@specs/fase-4-playground-web-pyodide.md
@adr/004-arquitetura-playground-web-client-side-pyodide.md
```
