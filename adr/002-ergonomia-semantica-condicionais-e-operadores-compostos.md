# ADR 002 — Ergonomia Semântica de Condicionais e Operadores Compostos

**Status:** Accepted

## Context

No protótipo inicial do Transpilador PT:
1. O ramo condicional intermediário (`elif` do Python) foi mapeado para a palavra `ouse`. Em português, "ouse" é a conjugação imperativa do verbo ousar ("ouse sonhar"), sendo totalmente antinatural para estudantes. A forma idiomática em português e em ambientes pedagógicos (Portugol, Visualg) é `senao se` ou `senão se`. No entanto, ao escrever `senao se x > 0:`, o transpilador ingênuo gerava `else if x > 0:`, que é sintaxe inválida no Python.
2. A palavra `eh` / `é` foi mapeada cegamente para o operador `is` do Python. Em Python, `is` compara a identidade do objeto na memória (ponteiro), enquanto `==` compara igualdade de valor. Quando um estudante escreve `se x eh 10:` ou `se nome eh "Ana":`, o Python emite `SyntaxWarning: "is" with a literal. Did you mean "=="?`, além de produzir comportamentos não-determinísticos com coleções (`lista eh [1, 2]` avalia para `False`).
3. Ao tentar negar uma comparação, a construção natural em português `se x nao eh nulo:` resultava na tradução token a token `if x not is None:`, que gera `SyntaxError: invalid syntax` imediato, pois em Python a ordem sintática obrigatória é `is not`.

## Problem

Como permitir construções gramaticais naturais e compostas em português (`senao se`, `nao eh`, `nao em`) e tratar a semântica de `eh` / `é` sem violar a sintaxe do Python e sem induzir os estudantes a erros graves de comparação de valores?

## Alternatives Considered

### A. Exigir palavras únicas inventadas (ex.: manter `ouse`, exigir `naoeh`)
- **Pros:** Fácil de processar no tokenizer (1 token NAME = 1 token Python).
- **Cons:** Experiência de aprendizado terrível; força os estudantes a decorarem jargões artificiais que não existem nem no português nem no Python.

### B. Mapeamento contextual de pares de tokens e resolução semântica de `eh` (Escolhida)
- **Pros:**
  - `senao se` e `senão se` (dois tokens NAME adjacentes na mesma linha) fundem-se em um único token `elif`.
  - `nao eh` e `não é` fundem-se em `is not` (ou `!=`), gerando Python 100% válido.
  - `eh` / `é` traduz para `is` quando comparado a singletons canônicos (`nulo`, `verdadeiro`, `falso`), gerando Python idiomático (PEP 8: `is None`), e traduz para `==` quando comparado a literais (números, textos, coleções), eliminando `SyntaxWarning` e falsos negativos de identidade.
  - `nao em` / `não em` traduz para `not in`.
- **Cons:**
  - O transpilador precisa de lookahead simples (`fluxo[i + 1]`) para inspecionar o próximo token antes de emitir a tradução.

## Decision

Adotamos a **Alternativa B**:

1. **Fusão de `senao se` / `senão se`:** O transpilador inspeciona pares de tokens na mesma linha. A sequência `senao` (ou `senão`) + `se` é unificada e transpilada como `elif`. Adicionalmente, as palavras grudadas `senaose` e `senãose` são suportadas. A palavra `ouse` permanece aceita apenas para retrocompatibilidade com códigos legados do protótipo.
2. **Resolução de `eh` / `é`:**
   - Se o operando seguinte for singleton de controle (`nulo`, `verdadeiro`, `falso`, `None`, `True`, `False`), traduz para `is`.
   - Nos demais casos (literais numéricos, literais de texto, variáveis), traduz para `==` para garantir comparação por valor.
3. **Fusão de `nao eh` / `não é`:**
   - Se o operando seguinte for singleton (`nulo`, etc.), traduz para `is not`.
   - Se for literal ou outro identificador, traduz para `!=`.
4. **Preservação de linhas:** Todas as fusões de múltiplos tokens na mesma linha preservam exatamente a linha do arquivo original para tracebacks.

## Consequences

- **Positive:**
  - Alunos podem escrever naturalmente `se ... senao se ... senao:` sem erros de sintaxe.
  - Comparações com `eh` funcionam tanto para `x eh nulo` (`x is None`) quanto para `x eh 10` (`x == 10`), sem warnings crípticos.
  - Expressões como `se item nao em lista:` e `se x nao eh nulo:` geram Python perfeitamente idiomático.
- **Negative:**
  - Pequeno aumento de lógica de lookahead no loop do tokenizer em `transpiler.py`.
- **Neutral / to monitor:**
  - Avaliar na Fase 3 como essas construções serão apresentadas no modo de transição bilíngue.

## Trade-offs

Priorizamos a linguagem natural e a ausência de armadilhas sutis de igualdade de objetos para o aluno iniciante, mantendo a compatibilidade do código gerado com as convenções da PEP 8 para verificações com `None`.
