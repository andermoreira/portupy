# Passo 2: Condicionais encadeadas com senao se e variações

## Contexto mínimo

O executor (`/implement-step`) lê o contrato completo deste step.
Este passo implementa a unificação de tokens para condicionais encadeadas conforme o [ADR-002](../../adr/002-ergonomia-semantica-condicionais-e-operadores-compostos.md).

- Paths: [`transpilador_pt/dicionario.py`], [`transpilador_pt/transpiler.py`], [`tests/test_transpiler.py`], [`tests/test_executor.py`]
- Contrato: AC-01, AC-02, AC-03, ADR-002
- Seam: Teste unitário e de integração via `unittest` em `tests/test_transpiler.py` e `tests/test_executor.py`

## Goal

Permitir que os estudantes escrevam estruturas condicionais encadeadas naturais utilizando `senao se`, `senão se`, `senaose` e `senãose`, fundindo os tokens na mesma linha em `elif` e garantindo execução semântica correta.

## Tarefas

1. Em `transpilador_pt/dicionario.py`:
   - Adicionar `"senaose": "elif"` e `"senãose": "elif"` ao dicionário `PALAVRAS_CHAVE`.
2. Em `transpilador_pt/transpiler.py`:
   - No loop de `transpila(codigo_pt)`:
     - Adicionar suporte a pular token consumido por fusão prévia (ex.: flag ou índice).
     - Quando o token for `senao` ou `senão` e não for atributo:
       - Verificar se o próximo token `proximo` é `token.NAME` com valor `"se"` na mesma linha (`proximo.start[0] == tok.start[0]`).
       - Se for: emitir `(token.NAME, "elif")` e marcar o token `"se"` para ser ignorado na próxima iteração.
3. Em `tests/test_transpiler.py` e `tests/test_executor.py`:
   - Remover os decorators `@unittest.expectedFailure` de:
     - `test_traducao_senao_se_e_variacoes` (em `test_transpiler.py`)
     - `test_executa_codigo_senao_se_encadeado` (em `test_executor.py`)
   - Validar que ambos passam como `ok`.

## Delta de complexidade planejado

- Abstrações: none
- Dependências: none (stdlib Python)
- Configuração: none
- Extension points: none
- Camadas arquiteturais: none

## Fora de Escopo

- Resolução contextual de `eh` / `é` e `nao eh` (escopo do Passo 3).
- Criação de exemplos no diretório `exemplos/` (escopo do Passo 4).

## Critério de Pronto

- `python3 -m unittest tests/test_transpiler.py tests/test_executor.py` passa com sucesso para os testes de `senao se`.
- Código com `senao se` transpila para `elif` e executa com saída esperada.

## Seam de teste

- `tests/test_transpiler.py` e `tests/test_executor.py` via `unittest`.

## Dependências

- Passo 1 (`specs/steps/fase-2-ergonomia-semantica-step-1.md`).

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
Fora de escopo: Resolução de eh/é e nao eh (Passo 3); arquivos em exemplos/.
Critério de pronto: python3 -m unittest tests/test_transpiler.py tests/test_executor.py passa 100% para os testes de senao se.

---

@specs/steps/fase-2-ergonomia-semantica-step-2.md
@specs/fase-2-ergonomia-semantica.md
@adr/002-ergonomia-semantica-condicionais-e-operadores-compostos.md
```
