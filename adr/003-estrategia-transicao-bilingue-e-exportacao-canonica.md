# ADR 003 — Estratégia de Transição Bilíngue e Exportação para Python Canônico

**Status:** Accepted

## Context

Nas Fases 1 e 2, o Transpilador PT adotou a estratégia de injetar funções e tipos embutidos (`mostre`, `tamanho`, etc.) diretamente no escopo de execução em runtime ([ADR 001](001-separacao-builtins-runtime-transpilacao-sintaxe.md)). Isso destravou f-strings e liberou variáveis normais como `lista = [1, 2]`.

Contudo, a missão pedagógica central do projeto declarada no [README.md](../README.md) é atuar como uma **rampa de acesso para o Python real**, e não criar um dialeto permanente ou ecossistema isolado:
1. O estudante precisa visualizar lado a lado a correspondência entre o que escreveu em português e como aquilo é expresso no Python canônico (`mostre` -> `print`, `se ... eh nulo` -> `if ... is None`, `tamanho` -> `len`).
2. O estudante precisa de uma forma de "graduar" seu projeto: gerar um arquivo `.py` independente e idiomático que possa ser versionado no GitHub, executado diretamente por qualquer pessoa com `python3 script.py` (sem necessitar do transpilador instalado) e submetido a linters ou IDEs padrão.

## Problem

Como oferecer uma ferramenta de transição didática (modo bilíngue) e um mecanismo de exportação para Python canônico puro, sem quebrar o modelo leve de execução rápida e segura já existente?

## Alternatives Considered

### A. Exibir apenas o código intermediário atual de `--mostrar-python`
- **Pros:** Custo zero de implementação.
- **Cons:** O código intermediário atual mantém `mostre` e `tamanho` sem traduzir (pois dependem do runtime do executor). O estudante não aprende as palavras reais `print` e `len`, frustrando o objetivo de transição.

### B. Módulo dedicado de tradução canônica e renderização lado a lado (Escolhida)
- **Pros:**
  - Gera Python 100% puro e canônico na exportação (`--exportar`), substituindo builtins e sintaxe sem depender de runtime proprietário.
  - O visualizador bilíngue (`--lado-a-lado` / `--modo-transicao`) alinha as duas colunas linha a linha no terminal com formatação limpa.
  - Mantém a execução rápida in-process inalterada para o dia a dia, adicionando os recursos de transição como ferramentas ativadas por flag.
- **Cons:**
  - Exige uma função especializada de pós-processamento léxico (`transpila_canonico`) para traduzir builtins apenas no contexto de exportação.

## Decision

Adotamos a **Alternativa B**:

1. **Função `transpila_canonico(codigo_pt: str) -> str`:**
   - Converte o código `.ptpy` em Python puro e autônomo.
   - Aplica as regras sintáticas da Fase 1 e 2 (`if`, `elif`, `for`, `is None`, `is not None`, etc.).
   - Substitui identificadores de builtins PT por seus equivalentes em Python (`mostre` -> `print`, `leia` -> `input`, `tamanho` -> `len`, `intervalo` -> `range`, etc.), respeitando preservação de atributos de objetos (`.` antecedente).
2. **Renderizador Bilíngue (`transpilador_pt/transicao.py`):**
   - Função `renderiza_lado_a_lado(codigo_pt: str, codigo_py: str) -> str` que formata o código original e o Python canônico em duas colunas alinhadas com números de linha.
3. **Extensões da CLI (`cli.py`):**
   - `--lado-a-lado` / `--modo-transicao`: exibe a comparação visual antes da execução.
   - `--exportar [destino.py]`: salva o código Python puro no arquivo de destino ou imprime no stdout.

## Consequences

- **Positive:**
  - O aluno compreende visualmente a correspondência direta entre o português e o Python idiomático.
  - Facilidade de exportação de código para projetos reais e repositórios externos.
  - O projeto cumpre plenamente sua premissa de scaffolding pedagógico.
- **Negative:**
  - Acréscimo do módulo de visualização e manipulação de largura de colunas para terminais de tamanhos variados.
- **Neutral / to monitor:**
  - Observar se iniciantes preferem ativar o modo bilíngue por padrão ou via flag explícita.

## Trade-offs

Separamos intencionalmente o código interno de execução (que prioriza velocidade e compatibilidade de variáveis) do código de exportação canônica (que prioriza conformidade com o ecossistema Python padrão).
