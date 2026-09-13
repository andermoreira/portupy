# PortuPy

**Escreva Python em português.** O PortuPy traduz palavras-chave e funções
embutidas para os equivalentes em português (`se`, `para`, `funcao`, `mostre`,
`tamanho`...), executa o código e explica os erros em português. A proposta é
reduzir a barreira de entrada para quem está começando a programar.

O PortuPy foi pensado como uma etapa de entrada no Python padrão. O mesmo código
pode ser exportado para Python canônico (`mostre` → `print`, `tamanho` → `len`)
e executado em qualquer interpretador, sem o PortuPy. As bibliotecas do
ecossistema (`math`, `requests`, ...) permanecem como são. O aluno encontra os
mesmos nomes ao usar essas bibliotecas no Python padrão.

O PortuPy usa o módulo `tokenize` da biblioteca padrão em vez de um parser
próprio. Substitui apenas os tokens necessários e preserva strings, comentários,
números e indentação.

## Exemplo

```python
funcao saudacao(nome):
    se nome eh nulo:
        retorne "sem nome"
    senao:
        retorne "Ola, " + nome

nomes = ["Ana", "Bruno", "Carla"]
para nome em nomes:
    mostre(saudacao(nome))
mostre(f"Total de nomes: {tamanho(nomes)}")
```

```text
Ola, Ana
Ola, Bruno
Ola, Carla
Total de nomes: 3
```

Esse arquivo pode ser exportado para Python canônico (`--exportar`) e executado
sem o PortuPy. Também pode ser experimentado no navegador pelo playground web.

## Instalação

```bash
pip install portupy
```

> O PortuPy é distribuído no PyPI como [`portupy`](https://pypi.org/project/portupy/).
> Enquanto o pacote não estiver publicado, use a instalação a partir do código
> (`pip install .` na raiz do repositório) — veja a seção [Como rodar](#como-rodar).

Depois de instalado, a CLI fica disponível como `portupy`:

```bash
portupy meu_programa.ptpy          # executa
portupy meu_programa.ptpy --exportar programa.py   # gera Python canônico
portupy --web                      # abre o playground no navegador
```

## Estrutura

```
portupy/
├── dicionario.py   # palavras-chave estruturais + builtins PT em runtime e canônicos
├── transpiler.py   # núcleo léxico: fusão de tokens, sensibilidade a contexto e exportador canônico
├── escopo_canonico.py # análise de escopo (ast/symtable) que protege nomes locais na exportação
├── transicao.py    # renderizador bilíngue lado a lado para transição pedagógica
├── erros.py        # tradução de exceções e formatação com apontador visual
├── executor.py      # compila e roda com injeção de builtins PT
├── servidor.py      # servidor HTTP estático local para o playground web
├── bundle_web.py   # gera o payload das fontes para o ambiente WebAssembly
└── exemplos/
    ├── ola.ptpy
    ├── condicionais.ptpy
    ├── erro_sintaxe.ptpy
    ├── erro.ptpy
    ├── loop.ptpy
    ├── funcoes.ptpy
    ├── enquanto.ptpy
    ├── classes.ptpy
    ├── tratamento_erros.ptpy
    ├── fizzbuzz.ptpy
    ├── fibonacci.ptpy
    └── textos.ptpy
web/                # playground web executado no cliente com Pyodide (Wasm)
├── index.html      # interface com editor, console e abas bilíngues
├── style.css       # estilos do playground em modo escuro
├── app.js          # integração com Pyodide e execução no navegador
├── pyodide-worker.js # execução do Pyodide com limite de tempo
├── service-worker.js # cache do shell e dos assets Pyodide após o primeiro acesso
└── bundle_pt.js    # fontes do transpilador empacotados para o filesystem do Wasm
adr/                # Architecture Decision Records (ADR 001, ADR 002, ADR 003, ADR 004)
specs/              # especificações ativas, arquivadas e passos de implementação
tests/              # suíte de testes automatizados (unittest)
cli.py              # interface de linha de comando com modos de execução, transição, exportação e web
LICENSE             # licença MIT
PUBLISHING.md       # guia de publicação no PyPI
```

## Como rodar

Os exemplos abaixo executam `python3 cli.py` diretamente no repositório. Depois
de instalar o pacote, substitua `python3 cli.py` por `portupy`.

```bash
# 1. Executar exemplos no terminal
python3 cli.py portupy/exemplos/ola.ptpy
python3 cli.py portupy/exemplos/condicionais.ptpy
python3 cli.py portupy/exemplos/erro.ptpy

# 2. Usar o modo de transição bilíngue (lado a lado)
python3 cli.py portupy/exemplos/condicionais.ptpy --lado-a-lado
# (alias: python3 cli.py portupy/exemplos/condicionais.ptpy --modo-transicao)

# 3. Exportar para Python canônico
python3 cli.py portupy/exemplos/ola.ptpy --exportar                # imprime no terminal
python3 cli.py portupy/exemplos/ola.ptpy --exportar meu_script.py  # salva em arquivo
python3 meu_script.py                                                      # roda sem o transpilador!

# 4. Iniciar o playground web no navegador via Pyodide
python3 cli.py --web        # abre http://localhost:8000 automaticamente
python3 cli.py --web 8080   # porta customizada opcional
python3 cli.py --web --sem-navegador  # inicia sem abrir interface gráfica

# 5. Ver o Python intermediário de compilação
python3 cli.py portupy/exemplos/condicionais.ptpy --mostrar-python

# 6. Executar os testes automatizados
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
assets do playground. Depois que a página ou o servidor local estiverem
disponíveis, a primeira execução pode ocorrer sem baixar o runtime de uma CDN. O
Service Worker mantém o shell e esses assets em cache para reaberturas offline.
No site hospedado, o shell precisa ter sido obtido em uma visita online anterior;
com a CLI, ele é servido localmente.

Os assets versionados e seus hashes estão em
[`web/vendor/pyodide/manifest.json`](web/vendor/pyodide/manifest.json). A cópia é
distribuída sob Apache-2.0, conforme [`web/vendor/pyodide/LICENSE.txt`](web/vendor/pyodide/LICENSE.txt).

Para executar arquivos `.ptpy` locais, a CLI usa `exec` no processo Python atual e
não oferece sandbox; execute somente código confiável.

A CLI retorna código `0` em caso de sucesso e `1` quando há erro no código ou no arquivo informado.

## O que já funciona

- **Injeção de builtins no runtime (ADR-001):** Funções e tipos selecionados (`mostre`, `leia`, `tamanho`, `intervalo`, `lista`, `texto`, etc.) são injetados diretamente no ambiente de execução.
- **f-strings nativas:** Expressões interpoladas como `f"Total: {tamanho(nomes)}"` são aceitas diretamente.
- **Condicionais encadeadas (ADR-002):** Suporte completo a `senao se`, `senão se`, `senaose` e `senãose`, transpilados para `elif` do Python. `ouse` é mantido por retrocompatibilidade.
- **Resolução contextual de `eh`/`é` (ADR-002):** A expressão é traduzida para `is` quando comparada a singletons (`nulo`, `verdadeiro`, `falso`) e para `==` quando comparada a literais e variáveis, evitando `SyntaxWarning` e comparações de identidade indevidas.
- **Operadores compostos de negação e pertinência (ADR-002):** Expressões como `nao eh` (`is not` / `!=`) e `nao em` (`not in`) funcionam naturalmente.
- **Modo de transição bilíngue (ADR-003):** A flag `--lado-a-lado` (ou `--modo-transicao`) exibe uma tabela comparativa sincronizada linha a linha entre o código em português e o Python canônico, com ajuste automático à largura do terminal.
- **Exportador para Python canônico (ADR-003):** A flag `--exportar [destino.py]` traduz chamadas de builtins pedagógicos (`mostre` → `print`, `tamanho` → `len`, `intervalo` → `range`, etc.) e gera scripts Python independentes, que rodam diretamente em qualquer interpretador padrão sem o transpilador.
- **Playground web com Pyodide (ADR-004):** Aplicação que executa o código no navegador via WebAssembly (Wasm). Inclui editor em português, visualização bilíngue lado a lado, exportação e catálogo de exemplos didáticos. Não requer instalação local nem servidor backend.
- **Execução em Worker no navegador:** O Pyodide roda em um Worker dedicado. Se a execução ultrapassar 10 segundos, o Worker é encerrado e um ambiente novo é inicializado sem bloquear a interface.
- **Nomes de variáveis comuns:** Nomes como `lista = [1, 2, 3]`, `texto = "olá"` e `tipo = 10` podem ser usados sem colidir com palavras reservadas nem ser alterados indevidamente na exportação.
- **Preservação de atributos de objetos:** Acessos e atribuições como `objeto.tipo` e `self.tipo = valor` são preservados sem substituição indevida de tokens.
- **Números de linha e apontador visual:** Tracebacks apontam 1:1 para a linha do `.ptpy` original, e erros de compilação exibem o trecho de código com o cursor `^`.
- **Tradução de erros:** Cobertura de `SyntaxError`, `IndentationError`, `IndexError`, `NameError`, `ZeroDivisionError`, `TypeError`, `AttributeError`, `ValueError`, entre outros.
- **Detecção de colisão com palavras estruturais:** Tentar atribuir a palavras-chave da sintaxe (`para = 5`, `se = 1`, `senao se = 2`) gera uma explicação antes que o interpretador produza um erro de sintaxe.

A [matriz de suporte da linguagem](docs/matriz-de-suporte.md) detalha a superfície
suportada e aponta os testes que protegem cada grupo de construções.

## Limitações conhecidas

- **Gramática inicial e builtins selecionados.** O PortuPy traduz esses elementos para o português. Bibliotecas externas (`requests`, `pandas`) continuam em inglês, mantendo os nomes usados no ecossistema Python.
- **Colisão de palavras estruturais.** `para`, `em`, `e`, `ou`, `com` são reservadas para a gramática, exatamente como `for`/`in`/`and`/`or`/`with` são em inglês.
- **Execução local sem sandbox.** O executor da CLI é apropriado para scripts locais confiáveis, mas não deve ser usado para executar código de terceiros como se fosse um ambiente isolado.
- **Runtime web versionado no pacote.** No primeiro acesso ao shell hospedado, o navegador ainda precisa de uma conexão ou de um servidor local. Depois disso, o runtime Pyodide não depende de uma CDN em tempo de execução.

## Roadmap

1. [x] **Fase 1:** Estabilização do protótipo (injeção em runtime, f-strings, preservação de atributos, diagnóstico rico com cursor `^`).
2. [x] **Fase 2:** Ergonomia semântica de condicionais (`senao se`, resolução contextual de `eh`/`é`, operadores `nao eh` e `nao em`).
3. [x] **Fase 3:** Modo de transição bilíngue (`--lado-a-lado`) e exportador independente para Python canônico (`--exportar`).
4. [x] **Fase 4:** Playground web empacotado com **Pyodide** para executar exemplos no navegador sem instalação local.

## Distribuição

O `pyproject.toml` publica a CLI como `portupy` e inclui no wheel os exemplos, o
playground estático e o runtime Pyodide local. A suíte de CI constrói esse artefato
e verifica se o pacote instalado localiza o servidor web e seus assets.

O passo a passo de release (build, verificação e envio ao PyPI) está em
[`PUBLISHING.md`](PUBLISHING.md).

## Licença

Distribuído sob a licença [MIT](LICENSE). O runtime Pyodide incluído em
`web/vendor/pyodide/` mantém sua própria licença Apache-2.0.
