# Spec: Fase 4 — Playground Web Interativo com Pyodide

## Goal
Disponibilizar um ambiente web interativo (Playground) que execute o Transpilador PT 100% no navegador via WebAssembly (Pyodide), permitindo que estudantes e professores escrevam, executem, comparem em modo bilíngue e exportem código em português sem instalar nada no computador.

## Non-goals
- Desenvolver backend proprietário com execução remota de código em servidores (RCE).
- Implementar sistema de contas, autenticação de usuários ou persistência em banco de dados na nuvem (escopo futuro/autônomo).
- Adicionar frameworks pesados (React/Next/Vue) que exijam toolchain complexa de build (npm/webpack), mantendo o projeto acessível como aplicação estática pura em Vanilla JS/CSS.

## User stories
- **Story 1 (Caminho feliz - execução direta no navegador):**
  - **Given** um estudante acessando o Playground Web pela primeira vez,
  - **When** ele digitar código em português (ou selecionar um exemplo) e clicar em "Executar ▶" (ou teclar `Ctrl+Enter`),
  - **Then** o código é compilado e executado pelo Pyodide no navegador, e a saída é impressa no terminal virtual da tela.
- **Story 2 (Caminho feliz - seleção de exemplos didáticos):**
  - **Given** um professor ou iniciante buscando referências de código,
  - **When** ele clicar no menu de "Exemplos" e escolher "Olá Mundo", "Condicionais e Operadores" ou "Tratamento de Erros",
  - **Then** o editor é preenchido instantaneamente com o código correspondente e fica pronto para execução.
- **Story 3 (Caminho feliz - visualização bilíngue e exportação):**
  - **Given** um estudante no Playground que quer entender a tradução ou salvar o projeto,
  - **When** ele alternar para a aba "Lado a Lado" ou "Python Canônico",
  - **Then** ele visualiza a tabela comparativa sincronizada ou o código Python puro gerado, com botão de 1 clique para copiar para a área de transferência.
- **Story 4 (Caminho feliz - servidor local pela CLI):**
  - **Given** um usuário em sala de aula sem conexão com a internet externa ou querendo testar localmente,
  - **When** ele executar `python3 cli.py --web`,
  - **Then** um servidor HTTP leve da stdlib é iniciado e abre o navegador apontando para o Playground.
- **Story 5 (Caminho de erro - diagnóstico visual de erros na web):**
  - **Given** um código com erro de sintaxe ou exceção de execução,
  - **When** o estudante executar o código no Playground,
  - **Then** o console exibe a mensagem de erro pedagógica traduzida com o apontador visual `^` formatado, sem quebrar o ambiente do navegador.

## Assumptions
- O pacote `transpilador_pt` utiliza exclusivamente a biblioteca padrão do Python e é 100% compatível com a runtime Pyodide no navegador [ADR-004].
- O navegador do usuário possui suporte padrão a WebAssembly (presente em todos os navegadores modernos há anos) [ADR-004].
- A stdlib do Python (`http.server`, `webbrowser`) é suficiente para servir os arquivos estáticos localmente via CLI sem dependências adicionais [ADR-004].

## Risks
- **Tempo de carregamento inicial do Pyodide:** O download inicial do runtime Wasm (~10 a 15 MB) pode demorar alguns segundos em conexões lentas.
  - *Mitigação:* Exibir banner visual com barra de progresso / spinner animado indicando "Carregando ambiente Python..." e desabilitar o botão de execução até a inicialização completa.
- **Loop infinito no código do usuário:** O estudante pode escrever `enquanto verdadeiro: passe`, travando a thread principal do navegador.
  - *Mitigação:* Implementar monitoramento visual ou instrução clara, e opcionalmente preparar worker isolado ou interrupção de execução.

## Error handling
- Erros de compilação ou execução capturam `sys.stderr` e renderizam com estilo visual de alerta (vermelho/âmbar) no console da UI.
- Falhas no download do Pyodide (ex.: offline na primeira visita) exibem aviso amigável explicando a necessidade de conexão inicial para baixar o runtime.
- Falha ao iniciar o servidor web na porta padrão tenta automaticamente a próxima porta livre ou informa o erro claramente.

## Observability
- Indicador de status visual na barra superior do Playground:
  - `🟡 Inicializando Python...`
  - `🟢 Python pronto para executar`
  - `🔴 Erro ao carregar ambiente`
- Medição de tempo de execução exibida no rodapé do console (`Executado em X ms`).

## Threat model
- **Isolamento de Segurança:** O código executado roda estritamente dentro da sandbox WebAssembly do navegador do cliente (zero acesso a arquivos do sistema operacional do usuário ou rede interna sem permissão explícita de CORS do browser).
- **Sem Servidor de Backend:** A aplicação estática não possui endpoints com estado nem aceita comandos de terceiros, eliminando qualquer risco de RCE (Remote Code Execution) em infraestrutura compartilhada.

## Acceptance criteria
- **AC-01:** O diretório `web/` contém uma aplicação web estática autônoma (`index.html`, `style.css`, `app.js`) sem necessidade de compilação externa (`npm`/`webpack`) [pedido] [ADR-004]
- **AC-02:** A interface web carrega o Pyodide e injeta o pacote `transpilador_pt` diretamente na memória virtual Wasm [pedido] [ADR-004]
- **AC-03:** O editor de código suporta digitação livre com numeração de linhas, tabulação inteligente e atalho `Ctrl+Enter` / `Cmd+Enter` para executar [pedido] [ADR-004]
- **AC-04:** O console web exibe a saída de `mostre()` e mensagens de diagnóstico amigáveis de erros com preservação do cursor `^` [pedido] [ADR-004]
- **AC-05:** A interface disponibiliza abas ou painéis para "Terminal", "Lado a Lado" (bilíngue) e "Python Canônico" com botão de cópia [pedido] [ADR-004]
- **AC-06:** O menu de exemplos permite carregar com 1 clique scripts como `ola.ptpy`, `condicionais.ptpy` e `erro.ptpy` [pedido] [ADR-004]
- **AC-07:** A CLI do projeto suporta o comando `python3 cli.py --web [porta]`, iniciando um servidor HTTP local para testes [pedido] [ADR-004]
- **AC-08:** A suíte de testes automatizados valida o módulo do servidor CLI `--web` e a integridade do empacotamento estático do playground [derivado]
- **AC-09:** O `README.md` documenta como acessar ou rodar o Playground Web [código: README.md]

## Open questions
- Nenhuma questão bloqueadora para o início da implementação.

## Implementation plan

1. **Step 1: Suíte de testes e módulo de serviço web da CLI (`tests/test_cli_web.py`, `transpilador_pt/servidor.py`)** [AC-07] [AC-08]
   - Criar módulo de servidor web local leve e testes automatizados para a flag `python3 cli.py --web`.
2. **Step 2: Estrutura HTML e Design System CSS do Playground (`web/index.html`, `web/style.css`)** [AC-01] [AC-03] [AC-05]
   - Construir o layout do Playground com Rich Aesthetics (dark mode, glassmorphism, tipografia Inter/JetBrains Mono, editor, abas de saída e console).
3. **Step 3: Motor JavaScript de Integração Pyodide e Execução (`web/app.js`, `web/bundle_pt.js`)** [AC-02] [AC-04] [AC-05] [AC-06]
   - Implementar carregamento do Pyodide, injeção dos fontes do `transpilador_pt`, captura de stdout/stderr, exibição lado a lado, exportação e catálogo de exemplos.
4. **Step 4: Integração CLI `--web`, Validação E2E e Documentação (`cli.py`, `README.md`)** [AC-07] [AC-09]
   - Habilitar flag `--web` na CLI principal, validar ponta a ponta no navegador e atualizar a documentação pública.

## Documentation impact
- [README.md](file:///Users/andersonalves/dev/transpilador-pt/README.md): Documentar o uso de `python3 cli.py --web` e instruções para deploy no GitHub Pages (Step 4).
