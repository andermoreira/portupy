# Passo 1: Suíte de testes para construções compostas e comparações semânticas

## Contexto mínimo

O executor (`/implement-step`) lê o contrato completo deste step. Não alterar código de produção em `transpilador_pt/` neste passo; o foco exclusivo é estabelecer a linha de base de testes para a Fase 2.

- Paths: [`tests/test_transpiler.py`], [`tests/test_executor.py`]
- Contrato: AC-01, AC-02, AC-04, AC-05, AC-06, AC-07, ADR-002
- Seam: Teste unitário e de integração via `unittest` da stdlib em `tests/`

## Goal

Adicionar casos de teste para estruturas condicionais encadeadas (`senao se`, `senão se`, `senaose`), operadores de negação compostos (`nao eh`, `nao em`) e resolução semântica de `eh` / `é`, marcando com `@unittest.expectedFailure` os novos comportamentos esperados.

## Tarefas

1. Em `tests/test_transpiler.py`:
   - Adicionar testes marcados com `@unittest.expectedFailure` para:
     - `senao se` e `senão se` transpilando para `elif` (AC-01).
     - `senaose` e `senãose` transpilando para `elif` (AC-02).
     - `eh` seguido de `nulo` transpilando para `is None` (AC-04).
     - `eh` seguido de literais (`10`, `"Ana"`) ou variáveis transpilando para `==` (AC-05).
     - `nao eh` seguido de `nulo` transpilando para `is not None` (AC-06).
     - `nao eh` seguido de literais transpilando para `!=` (AC-06).
     - `nao em` transpilando para `not in` (AC-07).
   - Adicionar teste confirmando que a forma legada `ouse` continua transpilando para `elif` (AC-03).
2. Em `tests/test_executor.py`:
   - Adicionar teste de execução condicional completa (`se ... senao se ... senao:`) via `executa_codigo`.
   - Adicionar teste de execução avaliando `x eh 10`, `x eh nulo` e `item nao em lista`.

## Delta de complexidade planejado

- Abstrações: none
- Dependências: none (utiliza exclusivamente `unittest` da stdlib)
- Configuração: none
- Extension points: none
- Camadas arquiteturais: none

## Fora de Escopo

- Modificar o código de produção em `transpilador_pt/` (implementações nos passos 2 e 3).
- Adicionar bibliotecas externas (pytest, tox).

## Critério de Pronto

- `python3 -m unittest discover -s tests -p "test_*.py"` executa com sucesso (todos os 20 testes anteriores passam normalmente e os novos testes de comportamento passam como `expected failure`).

## Seam de teste

- `tests/test_transpiler.py` e `tests/test_executor.py` via runner `unittest`.

## Dependências

- Nenhuma (primeiro passo da Fase 2).

## Documentation impact

- Nenhum — suíte de testes interna sem impacto em documentação pública.

## Checklist pré-handoff

- [x] ≤ 5 arquivos lógicos afetados no total? (2 arquivos: `tests/test_transpiler.py`, `tests/test_executor.py`).
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
Arquivos: @tests/test_transpiler.py @tests/test_executor.py
Fora de escopo: Modificar código em transpilador_pt/ ou cli.py; dependências externas.
Critério de pronto: python3 -m unittest discover -s tests -p "test_*.py" roda com 100% de sucesso (testes existentes passam, novos testes marcados com expectedFailure).

---

@specs/steps/fase-2-ergonomia-semantica-step-1.md
@specs/fase-2-ergonomia-semantica.md
@adr/002-ergonomia-semantica-condicionais-e-operadores-compostos.md
```
