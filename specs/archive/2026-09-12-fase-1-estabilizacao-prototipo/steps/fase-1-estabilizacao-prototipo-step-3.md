# Passo 3: Sensibilidade a contexto para atributos de objetos

## Contexto mínimo

O executor (`/implement-step`) lê o contrato completo deste step.

- Paths: [`transpilador_pt/transpiler.py`], [`tests/test_transpiler.py`]
- Contrato: AC-04
- Seam: Teste unitário via `unittest` em `tests/test_transpiler.py`

## Goal

Fazer com que o transpilador preserve tokens identificadores precedidos pelo operador ponto (`.`), evitando que acessos e atribuições a atributos de instâncias ou classes (como `self.tipo = 1` ou `objeto.tipo`) sofram tradução indevida ou disparem falsos erros de palavra reservada.

## Tarefas

1. Em `transpilador_pt/transpiler.py`:
   - No loop principal de `transpila`:
     - Inspecionar o token anterior na lista de tokens (`anterior = fluxo[i - 1] if i > 0 else None`).
     - Se `anterior and anterior.type == token.OP and anterior.string == "."`:
       - Não aplicar a substituição por `MAPA`.
       - Não disparar a checagem de palavra reservada em atribuição.
2. Em `tests/test_transpiler.py`:
   - Remover `@unittest.expectedFailure` do teste `test_regressao_atribuicao_atributo_objeto`.
   - Adicionar asserções cobrindo acesso a atributos (`objeto.tipo`) e atribuições de atributos (`self.tipo = valor`).

## Delta de complexidade planejado

- Abstrações: none
- Dependências: none (stdlib Python)
- Configuração: none
- Extension points: none
- Camadas arquiteturais: none

## Fora de Escopo

- Modificar `erros.py` ou tratamento de `SyntaxError` (escopo do Passo 4).
- Modificar `dicionario.py` ou `executor.py`.

## Critério de Pronto

- `python3 -m unittest tests/test_transpiler.py` passa 100% verde sem qualquer `expectedFailure`.
- Códigos como `self.tipo = 1` e `carro.tipo` transpilam preservando o nome original do atributo.

## Seam de teste

- `tests/test_transpiler.py` via `unittest`.

## Dependências

- Passo 2 (`specs/steps/fase-1-estabilizacao-prototipo-step-2.md`).

## Documentation impact

- Nenhum — documentação será sincronizada no Passo 4.

## Checklist pré-handoff

- [x] ≤ 5 arquivos lógicos afetados no total? (2 arquivos: `transpilador_pt/transpiler.py`, `tests/test_transpiler.py`).
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
Arquivos: @transpilador_pt/transpiler.py @tests/test_transpiler.py
Fora de escopo: Alterações em erros.py, executor.py ou dicionario.py.
Critério de pronto: python3 -m unittest tests/test_transpiler.py passa 100% verde sem falhas esperadas; self.tipo = 1 e objeto.tipo preservam o atributo.

---

@specs/steps/fase-1-estabilizacao-prototipo-step-3.md
@specs/fase-1-estabilizacao-prototipo.md
```
