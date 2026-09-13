# ADR 004 — Arquitetura do Playground Web Client-Side com Pyodide

**Status:** Accepted

## Context

Nas Fases 1, 2 e 3, o Transpilador PT foi consolidado como uma ferramenta CLI para terminal, com execução rápida, tratamento amigável de erros, modo bilíngue lado a lado e exportador canônico.
Entretanto, a barreira de entrada para estudantes iniciantes (especialmente em escolas, oficinas ou autodidatas sem Python instalado localmente) ainda é alta quando se exige instalação de ambiente, terminal, git e editor de código.

A **Fase 4** tem como objetivo fornecer um **Playground Web interativo**, permitindo que qualquer pessoa experimente o Transpilador PT diretamente pelo navegador, sem necessidade de instalar nada na máquina.

## Problem

Como disponibilizar uma experiência interativa completa (edição, execução de código, visualização bilíngue lado a lado e exportação de código) na web de forma segura, leve, de baixo custo operacional e sem dependência de servidores de backend custosos ou vulneráveis a execução remota de código (RCE)?

## Alternatives Considered

### A. Backend Python com servidor HTTP / WebSocket (FastAPI, Flask, etc.)
- **Pros:** Reutilização direta do interpretador local do servidor.
- **Cons:**
  - Risco crítico de segurança (RCE - execução arbitrária de código do usuário no servidor). Exigiria sandboxing pesado (gVisor, containers descartáveis, Firecracker).
  - Custo operacional contínuo de hospedagem de servidores e manutenção de infraestrutura.
  - Latência de rede para cada execução de código.

### B. Playground 100% Client-Side com Pyodide / WebAssembly (Escolhida)
- **Pros:**
  - **Zero Backend / Custo Zero de Infraestrutura:** Pode ser hospedado como página estática no GitHub Pages, Vercel ou qualquer CDN estático.
  - **Isolamento no navegador:** O código do aluno roda dentro do Worker WebAssembly do navegador do próprio usuário; isso evita executar o código em uma infraestrutura compartilhada do projeto, sem transformar essa fronteira em uma garantia de segurança absoluta.
  - **Base CPython via Pyodide:** O Pyodide fornece CPython compilado para Wasm, mas bibliotecas, APIs do navegador e limites de execução continuam sujeitos ao ambiente Web.
  - **Runtime distribuído localmente:** O playground pode funcionar sem CDN porque os assets essenciais do Pyodide são versionados em `web/vendor/pyodide/` e precacheados pelo Service Worker.
  - **Fidelidade ao Pacote:** Como o `transpilador_pt` é Python puro (sem bibliotecas em C), ele pode ser carregado diretamente no virtual filesystem (`MEMFS`) do Pyodide.
- **Cons:**
  - O carregamento inicial do runtime WebAssembly ainda transfere alguns megabytes de assets locais do site ou do servidor da CLI.

## Decision

Adotamos a **Alternativa B (Playground 100% Client-Side com Pyodide)**:

1. **Estrutura da Aplicação Web:**
   - Criar diretório `web/` com HTML5 semântico, Vanilla CSS moderno e JavaScript modular (ES6).
   - Sem frameworks pesados ou ferramentas de build complexas, mantendo o projeto leve, rápido e fácil de servir localmente ou no GitHub Pages.
2. **Carregamento do Transpilador no Pyodide:**
   - O runtime Pyodide 0.26.4 é distribuído localmente em `web/vendor/pyodide/`, com manifesto de hashes e aviso de licença.
   - A aplicação usa o mesmo diretório local como `indexURL`, sem depender de rede para o runtime.
   - Os arquivos-fonte do `transpilador_pt` (`dicionario.py`, `transpiler.py`, `transicao.py`, `erros.py`, `executor.py`) são montados no sistema de arquivos virtual do Pyodide (`/home/pyodide/transpilador_pt/`) a partir do bundle estático.
     - _Nota (pós-Fase 4): a análise de escopo canônico foi extraída de `transpiler.py` para `escopo_canonico.py`, que passou a integrar o conjunto de fontes montado no Pyodide (via `ARQUIVOS_MODULO` em `bundle_web.py`)._
3. **Fluxos de Interação na Interface:**
   - **Editor:** Área de edição com numeração de linhas, atalhos de teclado (`Ctrl+Enter` / `Cmd+Enter` para rodar) e seletor de exemplos integrados (`ola.ptpy`, `condicionais.ptpy`, etc.).
   - **Console / Terminal Virtual:** Captura de `stdout` e `stderr` com renderização limpa e indicação de status de execução.
   - **Aba Bilíngue Lado a Lado:** Renderiza a visão comparativa gerada por `renderiza_lado_a_lado`.
   - **Aba de Exportação Canônica:** Exibe o Python puro gerado por `transpila_canonico` com botão de "Copiar Código".
4. **Comando CLI para Servidor Local:**
   - Adicionar à CLI opção simples para subir um servidor web local (`python3 cli.py --web [porta]`), facilitando o teste e uso offline em sala de aula sem necessidade de configuração manual.

## Consequences

- **Positive:**
  - Zero barreira de instalação para estudantes e professores.
  - Custo zero de manutenção de servidores; o modelo Wasm client-side reduz a superfície de execução no servidor.
  - Experiência visual moderna e atrativa com feedback imediato.
  - Sincronização direta com as regras consolidadas nas Fases 1, 2 e 3.
- **Negative:**
  - O carregamento inicial do runtime local ainda pode levar alguns segundos, conforme o dispositivo e o servidor que entrega os assets.
- **Neutral / to monitor:**
  - Compatibilidade com dispositivos móveis (layout responsivo com alternância entre editor e console).

## Trade-offs

Priorizamos a execução no navegador e o custo zero de infraestrutura em detrimento do tamanho do download inicial do runtime CPython. A distribuição local elimina a dependência de CDN durante a execução, mas não transforma a CLI em um sandbox para arquivos não confiáveis.
