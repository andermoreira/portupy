# ADR 001 — Separação entre Injeção de Builtins em Runtime e Transpilação Léxica de Sintaxe

**Status:** Accepted

## Context

O protótipo inicial do Transpilador PT unificou palavras-chave estruturais da gramática (`se`, `para`, `enquanto`, `funcao`) e funções embutidas curadas (`mostre`, `leia`, `tamanho`, `lista`, `texto`) em um único mapa (`MAPA = {**PALAVRAS_CHAVE, **BUILTINS}`).

Durante a análise da Fase 1, identificou-se que essa unificação produz efeitos colaterais severos:
1. Em versões do Python anteriores à PEP 701 (e dependendo de como strings são processadas), o `tokenize` trata f-strings como um único token `STRING`, impedindo que funções como `tamanho(...)` dentro de `{}` sejam transpiladas para `len(...)`. Isso quebrou o próprio script de exemplo oficial (`ola.ptpy`).
2. O transpilador possui uma checagem preventiva que bloqueia qualquer atribuição a identificadores presentes no `MAPA`. Como `lista`, `texto`, `tipo`, `minimo` e `maximo` estavam nesse mapa, iniciantes foram impedidos de criar variáveis legítimas como `lista = [1, 2, 3]` ou `texto = "olá"`.
3. Em Python nativo, palavras-chave estruturais (`keywords`) são restrições da gramática sintática, enquanto funções e tipos embutidos (`builtins`) vivem no escopo do módulo `builtins` e admitem sombreamento local.

## Problem

Como disponibilizar funções e tipos com nomes em português para os estudantes sem depender de substituição cega no código-fonte por meio do tokenizer e sem restringir indevidamente o vocabulário de variáveis dos alunos?

## Alternatives Considered

### A. Substituição integral via Tokenizer com parsing de f-strings
- **Pros:** Mantém o código Python gerado 100% puro e idêntico ao que um programador fluente em inglês escreveria.
- **Cons:** Exige re-tokenizar o conteúdo interno de f-strings manualmente; não resolve o conflito de sombreamento de variáveis (`lista = [1, 2]` continuaria sendo substituído por `list = [1, 2]`); complexidade desproporcional para o protótipo.

### B. Injeção de Builtins em Runtime no ambiente de execução do executor (Escolhida)
- **Pros:**
  - Resolve f-strings imediatamente em qualquer versão do Python sem necessidade de re-tokenização.
  - Libera palavras naturais (`lista`, `texto`, `tipo`, `dicionario`) para serem usadas como variáveis normais, respeitando as regras padrão de escopo do Python.
  - Simplifica radicalmente o transpilador léxico, que passa a se concentrar exclusivamente em palavras-chave da gramática (`se`, `para`, `retorne`, etc.).
  - Preserva compatibilidade quando o código é executado via `exec()`.
- **Cons:**
  - Ao inspecionar o código Python gerado via `--mostrar-python`, chamadas como `mostre(...)` ou `tamanho(...)` continuam escritas em português, dependendo do runtime para resolução.
  - Código gerado não roda diretamente no terminal com `python3 arquivo_gerado.py` a menos que os helpers estejam no escopo de builtins.

### C. Parser e AST próprio do zero
- **Pros:** Controle total sobre escopos, árvore sintática e semântica.
- **Cons:** Viola a premissa de simplicidade e baixo custo de manutenção do protótipo; alto esforço de implementação.

## Decision

Adotamos a **Alternativa B (Injeção de Builtins em Runtime)** para o motor de execução:

1. `PALAVRAS_CHAVE` e `BUILTINS` são formalmente desacoplados em `dicionario.py`.
2. O transpilador léxico (`transpiler.py`) substitui apenas palavras-chave estruturais da linguagem que interferem na sintaxe (`se` -> `if`, `para` -> `for`, `funcao` -> `def`, `retorne` -> `return`, etc.).
3. O executor (`executor.py`) injeta os equivalentes em português diretamente na tabela de símbolos builtins do contexto de execução (`mostre` -> `print`, `tamanho` -> `len`, `inteiro` -> `int`, etc.).
4. A restrição preventiva de atribuição passa a valer apenas para palavras estruturais da gramática, permitindo que os alunos declarem variáveis com nomes como `lista`, `texto` ou `tipo`.

## Consequences

- **Positive:**
  - O exemplo `ola.ptpy` funciona imediatamente com interpolação f-string (`{tamanho(nomes)}`).
  - Alunos podem utilizar livremente nomes intuitivos de variáveis em português (`lista = [1, 2, 3]`).
  - O transpilador fica mais resiliente, com menor probabilidade de corrupção semântica acidental.
- **Negative:**
  - A exibição do Python gerado por `--mostrar-python` mostrará uma versão mista (sintaxe em Python padrão, funções auxiliares em português) até que um passo de tradução opcional ou modo de exportação limpa seja implementado.
- **Neutral / to monitor:**
  - Monitorar se o uso de builtins em português atrasa ou auxilia a associação com os nomes em inglês (`tamanho` vs `len`). Isso será mitigado na Fase 3 pelo modo bilíngue.

## Trade-offs

Aceitamos que o código intermediário gerado mantenha chamadas a builtins em português em troca de destravar f-strings, eliminar bugs de substituição cega e não impedir o vocabulário básico de variáveis dos estudantes. O gatilho para revisitar essa decisão será a implementação da ferramenta de exportação definitiva para código Python de produção (Fase 3).
