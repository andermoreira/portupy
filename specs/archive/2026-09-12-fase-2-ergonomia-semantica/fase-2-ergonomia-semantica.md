# Spec: Fase 2 — Ergonomia e Semântica

## Goal
Permitir a escrita natural de condicionais encadeadas (`senao se`) e operadores de negação e comparação compostos (`nao eh`, `nao em`, `eh`), resolvendo desvios de sintaxe e prevenindo falhas sutis de identidade de objetos para alunos iniciantes.

## Non-goals
- Desenvolver o modo de transição bilíngue lado a lado ou comando de exportação `--exportar` (escopo da Fase 3).
- Implementar interface gráfica ou empacotamento web via Pyodide/WASM (escopo da Fase 4).
- Criar tradução de métodos nativos do Python (`.append()`, `.upper()`, `.split()`).
- Suportar gramáticas complexas de linguagem natural com múltiplos advérbios e preposições encadeadas além das regras curadas.

## User stories
- **Story 1 (Caminho feliz - condicionais encadeadas):**
  - **Given** um estudante escrevendo uma estrutura com `se ... senao se ... senao:`,
  - **When** o código for transpilado e executado,
  - **Then** `senao se` deve ser convertido para `elif`, executando a lógica condicional sem erro de sintaxe.
- **Story 2 (Caminho feliz - igualdade por valor com 'eh'):**
  - **Given** um estudante comparando valores com literais (ex.: `se nota eh 10:` ou `se nome eh "Ana":`),
  - **When** o código for transpilado,
  - **Then** `eh` deve ser convertido para `==`, evitando `SyntaxWarning` do Python e garantindo comparação determinística por valor.
- **Story 3 (Caminho feliz - verificação de nulo com 'eh'):**
  - **Given** um estudante verificando ausência de valor (ex.: `se valor eh nulo:`),
  - **When** o código for transpilado,
  - **Then** `eh nulo` deve ser convertido para `is None` conforme a convenção idiomática da PEP 8.
- **Story 4 (Caminho feliz - negação composta):**
  - **Given** um estudante escrevendo `se x nao eh nulo:` ou `se item nao em lista:`,
  - **When** o código for transpilado,
  - **Then** as expressões devem ser convertidas respectivamente para `is not None` e `not in lista`, sem gerar `not is` ou erro de compilação.
- **Story 5 (Caminho de erro - atribuição a operadores):**
  - **Given** um estudante tentando atribuir a `senaose = 1`,
  - **When** o transpilador analisar a declaração,
  - **Then** um `ErroDeTraducao` deve ser disparado alertando sobre o uso de palavra reservada.

## Assumptions
- A biblioteca padrão `tokenize` do Python preserva a linha e a ordem sequencial de tokens adjacentes na mesma linha [VERIFIED: Python 3.9.6 local].
- A fusão de tokens (`senao` + `se` -> `elif`) na mesma linha preserva a correspondência 1:1 de números de linha para o formatador de tracebacks [ADR-002].
- A intenção pedagógica de `eh` para literais numéricos e strings é igualdade por valor; por isso a implementação gera `==`, sem depender de identidade ou de string interning [ADR-002].

## Risks
- **Desalinhamento de colunas em erros:** A fusão de dois tokens (`senao se` tem 8 caracteres, `elif` tem 4) pode alterar o offset de tokens posteriores na mesma linha.
  - *Mitigação:* O algoritmo `_mapeia_coluna_para_fonte` em [transpilador_pt/erros.py](file:///Users/andersonalves/dev/transpilador-pt/transpilador_pt/erros.py) utiliza difflib para recalcular a coluna na linha original independentemente do tamanho do token transpilado.
- **Interpretação ambígua de 'eh':** Casos onde o usuário realmente quisesse comparar identidade de dois objetos arbitrários (`a eh b`).
  - *Mitigação:* Em nível introdutório, estudantes comparam valores (`==`). Para comparação com `nulo` e booleanos, `is` continua sendo gerado.

## Error handling
- O transpilador continua lançando `ErroDeTraducao` caso palavras reservadas compostas ou novos identificadores de sintaxe sejam alvos de atribuição (`senaose = 1`, `ouse = 2`).
- Erros de sintaxe em blocos `senao se` continuam sendo formatados com apontador visual `^` na linha correta do arquivo `.ptpy`.

## Observability
- Transparência total via flag `--mostrar-python` para inspecionar a conversão de `senao se` para `elif` e `nao eh` para `is not`/`!=`.
- Manutenção dos códigos de saída da CLI (`0` para sucesso, `1` para erros com saída em `stderr`).

## Threat model
- Mesma superfície da Fase 1: compilação local de arquivos `.ptpy` em ambiente controlado via CLI. Sem novas dependências ou execução de rede.

## Acceptance criteria
- **AC-01:** Condicionais com `senao se` e `senão se` transpilam para `elif` e executam corretamente [pedido] [ADR-002]
- **AC-02:** Variações unificadas `senaose` e `senãose` transpilam para `elif` [ADR-002]
- **AC-03:** A forma legada `ouse` continua transpilando para `elif` por retrocompatibilidade [ADR-002]
- **AC-04:** Expressões com `eh` / `é` seguidas de `nulo` transpilam para `is None` [ADR-002]
- **AC-05:** Expressões com `eh` / `é` seguidas de literais numéricos, literais de texto ou variáveis transpilam para `==` sem gerar `SyntaxWarning` [ADR-002]
- **AC-06:** Expressões com `nao eh` / `não é` transpilam para `is not None` quando seguidas de `nulo`, e para `!=` nos demais casos [código: transpilador_pt/transpiler.py:40] [ADR-002]
- **AC-07:** Expressões com `nao em` / `não em` transpilam para `not in` e executam sem erro de sintaxe [ADR-002]

## Open questions
- Nenhuma questão bloqueadora para a execução da Fase 2.

## Implementation plan
1. Criar testes automatizados cobrindo `senao se`, `senaose`, `eh` contextual, `nao eh` e `nao em` [AC-01] [AC-02] [AC-04] [AC-05] [AC-06] [AC-07]
2. Implementar suporte a `senao se`, `senão se`, `senaose` e `senãose` no transpilador léxico [AC-01] [AC-02] [AC-03]
3. Implementar resolução contextual de `eh` / `é` e fusão de `nao eh` / `não é` no transpilador [AC-04] [AC-05] [AC-06] [AC-07]
4. Criar exemplo demonstrativo `transpilador_pt/exemplos/condicionais.ptpy` e sincronizar documentação no `README.md` [código: README.md:40]

## Documentation impact
- [README.md](file:///Users/andersonalves/dev/transpilador-pt/README.md): Documentar suporte oficial a `senao se`, `nao eh`, `nao em`, e explicar o comportamento semântico seguro de `eh` (Step 4).
