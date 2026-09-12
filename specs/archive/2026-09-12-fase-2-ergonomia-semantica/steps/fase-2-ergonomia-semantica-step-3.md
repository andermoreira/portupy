# Passo 3: Resolução contextual de eh/é e negação composta com nao eh

## Contexto mínimo

O executor (`/implement-step`) lê o contrato completo deste step.
Este passo implementa a semântica segura de igualdade e negação conforme o [ADR-002](../../adr/002-ergonomia-semantica-condicionais-e-operadores-compostos.md).

- Paths: [`transpilador_pt/dicionario.py`], [`transpilador_pt/transpiler.py`], [`tests/test_transpiler.py`], [`tests/test_executor.py`]
- Contrato: AC-04, AC-05, AC-06, AC-07, ADR-002
- Seam: Teste unitário e de integração via `unittest` em `tests/test_transpiler.py` e `tests/test_executor.py`

## Goal

Implementar no transpilador a resolução contextual de `eh` / `é` (`is` para `nulo` e `==` para literais/valores), a fusão de `nao eh` / `não é` (`is not` para `nulo` e `!=` para os demais casos) e o suporte a `nao em` (`not in`).

## Tarefas

1. Em `transpilador_pt/dicionario.py`:
   - Remover `eh` e `é` de `PALAVRAS_CHAVE` com tradução fixa para `is`, permitindo que o transpilador trate sua semântica contextualmente conforme o operando seguinte.
2. Em `transpilador_pt/transpiler.py`:
   - No loop de tokens em `transpila(codigo_pt)`:
     - Detectar negação composta `nao` ou `não` seguida na mesma linha por `eh` ou `é`:
       - Inspecionar o token seguinte: se for `nulo`, `verdadeiro`, `falso` (ou `None`, `True`, `False`), emitir `(token.NAME, "is")` e `(token.NAME, "not")` (`is not`).
       - Caso contrário: emitir `(token.OP, "!=")`.
       - Avançar o índice em 2 tokens.
     - Detectar `eh` ou `é` isolado (não precedido por `.`):
       - Inspecionar o próximo token: se for `nulo`, `verdadeiro`, `falso` (ou `None`, `True`, `False`), emitir `(token.NAME, "is")`.
       - Caso contrário (literais numéricos, strings, identificadores): emitir `(token.OP, "==")`.
3. Em `tests/test_transpiler.py` e `tests/test_executor.py`:
   - Remover os decorators `@unittest.expectedFailure` de:
     - `test_traducao_eh_contextual`
     - `test_traducao_nao_eh_e_nao_em`
     - `test_executa_codigo_operadores_compostos_eh_e_nao`
   - Validar que todos os 26 testes passam com 100% de sucesso.

## Delta de complexidade planejado

- Abstrações: none
- Dependências: none (stdlib Python)
- Configuração: none
- Extension points: none
- Camadas arquiteturais: none

## Fora de Escopo

- Arquivo de exemplos demonstrativos e documentação no `README.md` (escopo do Passo 4).

## Critério de Pronto

- `python3 -m unittest discover -s tests -p "test_*.py"` executa com 0 falhas e 0 falhas esperadas (todos os 26 testes passando como `ok`).
- `x eh 10` vira `x == 10`, `x eh nulo` vira `x is None`, `x nao eh nulo` vira `x is not None`, `x nao eh 10` vira `x != 10`.

## Seam de teste

- `tests/test_transpiler.py` e `tests/test_executor.py` via `unittest`.

## Dependências

- Passo 2 (`specs/steps/fase-2-ergonomia-semantica-step-2.md`).

## Documentation impact

- Nenhum — documentação será sincronizada no Passo 4.

## Checklist pré-handoff

- [x] ≤ 5 arquivos lógicos afetados no total? (4 arquivos: `transpilador_pt/dicionario.py`, `transpilador_pt/transpiler.py`, `tests/test_transpiler.py`, `tests/test_executor.py`).
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
Arquivos: @transpilador_pt/dicionario.py @transpilador_pt/transpiler.py @tests/test_transpiler.py @tests/test_executor.py
Fora de escopo: Arquivos em exemplos/ e alterações em README.md.
Critério de pronto: python3 -m unittest discover -s tests -p "test_*.py" passa 100% verde (0 falhas esperadas).

---

@specs/steps/fase-2-ergonomia-semantica-step-3.md
@specs/fase-2-ergonomia-semantica.md
@adr/002-ergonomia-semantica-condicionais-e-operadores-compostos.md
```
