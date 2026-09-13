# PortuPy — protótipo

Protótipo funcional de um transpilador Python-em-português, construído
com o módulo `tokenize` da stdlib (sem parser próprio).

## Estrutura

```
portupy/
├── dicionario.py   # palavras-chave estruturais + builtins PT em runtime e canônicos
├── transpiler.py   # núcleo léxico: fusão de tokens, sensibilidade a contexto e exportador canônico
├── escopo_canonico.py # análise de escopo (ast/symtable) que protege nomes locais na exportação
├── transicao.py    # renderizador bilíngue lado a lado para transição pedagógica
├── erros.py        # tradução de exceções e formatação com apontador visual
├── executor.py      # compila e roda com injeção de builtins PT
├── servidor.py      # servidor HTTP estático local para o Playground Web
├── bundle_web.py   # gerador do payload dos fontes para o ambiente WebAssembly
└── exemplos/
    ├── ola.ptpy
    ├── erro.ptpy
    ├── erro_sintaxe.ptpy
    ├── condicionais.ptpy
    ├── loop.ptpy
    └── funcoes.ptpy
web/                # Playground Web 100% client-side com Pyodide (Wasm)
├── index.html      # interface com editor, console e abas bilíngues
├── style.css       # design system dark mode moderno com Rich Aesthetics
├── app.js          # motor de integração Pyodide e execução no navegador
├── pyodide-worker.js # execução isolada do Pyodide com limite de tempo
├── service-worker.js # cache do shell e dos assets Pyodide após o primeiro acesso
└── bundle_pt.js    # fontes do transpilador empacotados para o filesystem Wasm
adr/                # Architecture Decision Records (ADR 001, ADR 002, ADR 003, ADR 004)
specs/              # especificações ativas, arquivadas e passos de implementação
tests/              # suíte de testes automatizados (unittest)
cli.py              # interface de linha de comando com modos de execução, transição, exportação e web
```

## Como rodar

```bash
# 1. Executar scripts de exemplo normalmente no terminal
python3 cli.py portupy/exemplos/ola.ptpy
python3 cli.py portupy/exemplos/condicionais.ptpy
python3 cli.py portupy/exemplos/erro.ptpy

# 2. Modo de transição bilíngue (lado a lado)
python3 cli.py portupy/exemplos/condicionais.ptpy --lado-a-lado
# (ou use o alias: python3 cli.py portupy/exemplos/condicionais.ptpy --modo-transicao)

# 3. Exportar para código Python canônico independente
python3 cli.py portupy/exemplos/ola.ptpy --exportar                # imprime no terminal
python3 cli.py portupy/exemplos/ola.ptpy --exportar meu_script.py  # salva em arquivo
python3 meu_script.py                                                      # roda sem o transpilador!

# 4. Iniciar o Playground Web no navegador (100% client-side via Pyodide)
python3 cli.py --web        # abre http://localhost:8000 automaticamente
python3 cli.py --web 8080   # porta customizada opcional
python3 cli.py --web --sem-navegador  # inicia sem abrir interface gráfica

# 5. Ver o Python intermediário de compilação
python3 cli.py portupy/exemplos/condicionais.ptpy --mostrar-python

# 6. Executar a suíte completa de testes automatizados
python3 -m unittest discover -s tests -p "test_*.py"

# 7. Instalar o pacote e usar a CLI globalmente (opcional)
python3 -m pip install .
portupy portupy/exemplos/ola.ptpy
portupy --web --sem-navegador

# 8. Consultar ajuda e versão da CLI
python3 cli.py --help
python3 cli.py --version

# 9. Executar os testes E2E do playground (requer Node.js e Chromium)
npm ci
node_modules/.bin/playwright install chromium
npm run test:e2e
```

O pacote inclui localmente o runtime Pyodide 0.26.4, o módulo Python padrão e os
assets do playground. Por isso, depois que a página ou o servidor local estiverem
disponíveis, a primeira execução pode ocorrer sem baixar o runtime de uma CDN. O
Service Worker também mantém o shell e esses assets em cache para reaberturas
offline. O acesso a um site ainda depende de o shell ter sido obtido por uma visita
online anterior ou ser servido localmente pela CLI.

Os assets versionados e seus hashes estão em
[`web/vendor/pyodide/manifest.json`](web/vendor/pyodide/manifest.json). A cópia é
distribuída sob Apache-2.0, conforme [`web/vendor/pyodide/LICENSE.txt`](web/vendor/pyodide/LICENSE.txt).

Para executar arquivos `.ptpy` locais, a CLI usa `exec` no processo Python atual e
não oferece sandbox; execute somente código confiável.

A CLI retorna código `0` em caso de sucesso e `1` quando há erro no código ou no arquivo informado.

## O que já funciona

- **Injeção de builtins em runtime (ADR-001):** Funções e tipos curados (`mostre`, `leia`, `tamanho`, `intervalo`, `lista`, `texto`, etc.) são injetados diretamente no ambiente de execução.
- **f-strings nativas:** Expressões interpoladas como `f"Total: {tamanho(nomes)}"` funcionam sem atrito em qualquer versão do Python.
- **Condicionais encadeadas naturais (ADR-002):** Suporte completo a `senao se`, `senão se`, `senaose` e `senãose` transpilando para `elif` do Python (com `ouse` mantido por retrocompatibilidade).
- **Resolução semântica segura de 'eh'/'é' (ADR-002):** Traduz para `is` quando comparado a singletons (`nulo`, `verdadeiro`, `falso`) e para `==` quando comparado a literais e variáveis, prevenindo `SyntaxWarning` e armadilhas de identidade de objetos.
- **Operadores compostos de negação e pertinência (ADR-002):** Expressões como `nao eh` (`is not` / `!=`) e `nao em` (`not in`) funcionam naturalmente.
- **Modo de Transição Bilíngue (ADR-003):** Flag `--lado-a-lado` (ou `--modo-transicao`) exibe tabela comparativa sincronizada linha a linha entre o código em português e o Python canônico com ajuste automático à largura do terminal.
- **Exportador para Python Canônico Puro (ADR-003):** Flag `--exportar [destino.py]` traduz chamadas de builtins pedagógicos (`mostre` -> `print`, `tamanho` -> `len`, `intervalo` -> `range`, etc.) gerando scripts Python 100% autônomos que rodam diretamente em qualquer interpretador Python padrão sem requerer o transpilador.
- **Playground Web Interativo com Pyodide (ADR-004):** Aplicação web moderna executando 100% no navegador do cliente via WebAssembly (Wasm), com editor de código em português, visualização bilíngue lado a lado, exportação instantânea e catálogo de exemplos didáticos sem necessidade de instalação local ou servidores backend.
- **Execução isolada no navegador:** O Pyodide roda em Worker dedicado; execuções que ultrapassam 10 segundos encerram o Worker e inicializam um ambiente novo sem congelar a interface.
- **Variáveis intuitivas liberadas:** Nomes comuns como `lista = [1, 2, 3]`, `texto = "olá"` ou `tipo = 10` são permitidos livremente e não colidem com palavras reservadas nem são alterados indevidamente na exportação.
- **Preservação de atributos de objetos:** Acessos e atribuições como `objeto.tipo` e `self.tipo = valor` são preservados sem substituição indevida de tokens.
- **Números de linha e apontador visual:** Tracebacks apontam 1:1 para a linha do `.ptpy` original, e erros de compilação exibem o trecho de código com o cursor `^`.
- **Tradução didática de erros:** Cobertura de `SyntaxError`, `IndentationError`, `IndexError`, `NameError`, `ZeroDivisionError`, `TypeError`, `AttributeError`, `ValueError`, entre outros.
- **Detecção antecipada de colisão:** Tentar atribuir a palavras-chave estruturais da sintaxe (`para = 5`, `se = 1`, `senao se = 2`) gera uma explicação amigável antes de disparar erro de sintaxe cru do interpretador.

A superfície suportada está detalhada na [matriz de suporte da linguagem](docs/matriz-de-suporte.md),
que também aponta os testes responsáveis por proteger cada grupo de construções.

## Limitações conhecidas (por design)

- **Apenas a gramática inicial e builtins curados são em português.** Bibliotecas externas (`requests`, `pandas`) continuam em inglês por design para servir de rampa de acesso, não de ecossistema isolado.
- **Colisão de palavras estruturais.** `para`, `em`, `e`, `ou`, `com` são reservadas para a gramática, exatamente como `for`/`in`/`and`/`or`/`with` são em inglês.
- **Execução local sem sandbox.** O executor da CLI é apropriado para scripts locais confiáveis, mas não deve ser usado para executar código de terceiros como se fosse um ambiente isolado.
- **Runtime Web versionado no pacote.** O primeiro carregamento do shell hospedado ainda precisa chegar ao navegador por uma conexão ou por um servidor local; o runtime Pyodide não é mais uma dependência de CDN em tempo de execução.

## Roadmap

1. [x] **Fase 1:** Estabilização do protótipo (injeção em runtime, f-strings, preservação de atributos, diagnóstico rico com cursor `^`).
2. [x] **Fase 2:** Ergonomia semântica de condicionais (`senao se`, resolução contextual de `eh`/`é`, operadores `nao eh` e `nao em`).
3. [x] **Fase 3:** Modo de transição bilíngue (`--lado-a-lado`) e exportador autônomo para Python canônico (`--exportar`).
4. [x] **Fase 4:** Playground Web empacotado com **Pyodide** para experimentação direta no navegador sem instalação local.

## Distribuição

O `pyproject.toml` publica a CLI como `portupy` e inclui os exemplos, o
playground estático e o runtime Pyodide local no wheel. A suíte de CI constrói esse
artefato para verificar que uma instalação do pacote continua capaz de localizar o
servidor web e seus assets.
