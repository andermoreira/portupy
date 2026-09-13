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
  - **Segurança Total (Sandboxed by Design):** O código do aluno roda exclusivamente dentro da sandbox WebAssembly do navegador do próprio usuário, sem risco de comprometer servidores externos.
  - **Compatibilidade 100% com CPython:** O Pyodide é uma distribuição oficial do CPython para Wasm, o que garante paridade idêntica de comportamento com o ambiente local.
  - **Funciona Offline:** Após o primeiro carregamento, o playground funciona sem conexão com a internet.
  - **Fidelidade ao Pacote:** Como o `transpilador_pt` é Python puro (sem bibliotecas em C), ele pode ser carregado diretamente no virtual filesystem (`MEMFS`) do Pyodide.
- **Cons:**
  - Download inicial do runtime WebAssembly (~10 a 15 MB na primeira visita, cacheado em seguida).

## Decision

Adotamos a **Alternativa B (Playground 100% Client-Side com Pyodide)**:

1. **Estrutura da Aplicação Web:**
   - Criar diretório `web/` com HTML5 semântico, Vanilla CSS moderno e JavaScript modular (ES6).
   - Sem frameworks pesados ou ferramentas de build complexas, mantendo o projeto leve, rápido e fácil de servir localmente ou no GitHub Pages.
2. **Carregamento do Transpilador no Pyodide:**
   - O runtime Pyodide é carregado via CDN oficial (`pyodide.js`).
   - Os arquivos-fonte do `transpilador_pt` (`dicionario.py`, `transpiler.py`, `transicao.py`, `erros.py`, `executor.py`) são montados no sistema de arquivos virtual do Pyodide (`/home/pyodide/transpilador_pt/`) ou agrupados em um loader estático para disponibilidade offline/standalone.
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
  - Custo zero de manutenção de servidores; segurança inerente do modelo Wasm client-side.
  - Experiência visual moderna e atrativa com feedback imediato.
  - Sincronização direta com as regras consolidadas nas Fases 1, 2 e 3.
- **Negative:**
  - Tempo de espera de 2 a 3 segundos no primeiro carregamento do Pyodide (mitigado por indicador de progresso e cache do navegador).
- **Neutral / to monitor:**
  - Compatibilidade com dispositivos móveis (layout responsivo com alternância entre editor e console).

## Trade-offs

Priorizamos segurança e custo zero de infraestrutura via WebAssembly no navegador em detrimento do tamanho do download inicial do runtime CPython.
