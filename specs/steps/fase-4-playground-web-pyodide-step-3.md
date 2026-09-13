# Passo 3: Integração Pyodide Wasm e Motor JavaScript da Aplicação

## Contexto mínimo

O executor lê o contrato deste step. Implementar o gerador de bundle estático dos fontes em `transpilador_pt/bundle_web.py` e a lógica de orquestração do cliente em `web/app.js`, executando o Transpilador PT no Pyodide WebAssembly com captura de E/S, modo bilíngue, exportação e catálogo de exemplos.

- Paths: [`transpilador_pt/bundle_web.py`], [`web/bundle_pt.js`], [`web/app.js`]
- Contrato: AC-02, AC-04, AC-05, AC-06, ADR-004
- Seam: Execução de código no navegador e captura de stdout/stderr

## Goal

Criar o gerador do bundle de fontes e a lógica interativa completa em `web/app.js`: carregar Pyodide via CDN, montar o pacote `transpilador_pt` no virtual filesystem Wasm, sincronizar editor com numeração de linhas, capturar `stdout`/`stderr`, renderizar as abas "Terminal", "Lado a Lado" e "Python Canônico", e disponibilizar o catálogo de exemplos didáticos.

## Tarefas

1. Criar `transpilador_pt/bundle_web.py`:
   - Ler os arquivos do pacote `transpilador_pt` (`__init__.py`, `dicionario.py`, `transpiler.py`, `transicao.py`, `erros.py`, `executor.py`).
   - Gerar `web/bundle_pt.js` contendo o objeto global `window.TRANSPILADOR_PT_SOURCES` com o conteúdo dos arquivos codificado em string JSON segura.
   - Fornecer função `gera_bundle_web(diretorio_destino)` para uso automatizado.
2. Executar `transpilador_pt/bundle_web.py` para gerar `web/bundle_pt.js`.
3. Criar `web/app.js`:
   - Inicialização do Pyodide:
     - Chamar `loadPyodide()`.
     - Criar diretório `/home/pyodide/transpilador_pt` no `pyodide.FS`.
     - Gravar cada arquivo de `window.TRANSPILADOR_PT_SOURCES` no sistema de arquivos virtual.
     - Atualizar status visual da navbar para `🟢 Python Pronto (Wasm)`.
   - Execução de código:
     - Capturar `stdout` e `stderr` através de redirecionamento ou wrappers Python no Pyodide.
     - Executar `transpilador_pt.executa_codigo(codigo)`.
     - Atualizar a aba "Terminal" com a saída produzida e formatar erros pedagógicos com cursor `^`.
     - Calcular e atualizar tempo de execução no rodapé.
   - Modos de transição e exportação:
     - Obter `transpila_canonico(codigo)` e atualizar a aba "Python Canônico".
     - Obter `renderiza_lado_a_lado(codigo, codigo_py)` e atualizar a aba "Lado a Lado".
     - Implementar botão "Copiar" na barra superior com feedback visual temporário ("Copiado!").
   - Ergonomia do Editor:
     - Sincronizar numeração de linhas conforme o usuário digita ou rola.
     - Tratar tecla `Tab` para inserir 4 espaços.
     - Atalho `Ctrl+Enter` e `Cmd+Enter` para executar.
     - Seletor de exemplos: trocar exemplo atualiza o editor e executa automaticamente.

## Delta de complexidade planejado

- Abstrações: none
- Dependências: Pyodide v0.26 via CDN (carregado pelo navegador)
- Configuração: none
- Extension points: objeto `window.TRANSPILADOR_PT_SOURCES`
- Camadas arquiteturais: camada de integração web e execução Wasm (`web/`)

## Fora de Escopo

- Flag `--web` na CLI principal e atualização do README (Step 4).

## Critério de Pronto

- `web/bundle_pt.js` e `web/app.js` criados e válidos.
- O carregamento do Pyodide inicializa sem erros de console e executa código Python em português no navegador.

## Seam de teste

- Inspeção no navegador e validação de scripts.

## Dependências

- Steps 1 e 2 concluídos.

## Documentation impact

- Nenhum nesta etapa (consolidado no Step 4).

## Checklist pré-handoff

- [x] ≤ 5 arquivos lógicos afetados no total? (3 arquivos: `transpilador_pt/bundle_web.py`, `web/bundle_pt.js`, `web/app.js`).
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
Arquivos: @transpilador_pt/bundle_web.py @web/bundle_pt.js @web/app.js
Fora de escopo: Modificar cli.py ou README.md; dependências externas npm.
Critério de pronto: bundle_web.py gera bundle_pt.js e app.js executa código em português via Pyodide.

---

@specs/steps/fase-4-playground-web-pyodide-step-3.md
@specs/fase-4-playground-web-pyodide.md
@adr/004-arquitetura-playground-web-client-side-pyodide.md
```
