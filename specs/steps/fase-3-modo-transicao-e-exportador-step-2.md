# Passo 2: Implementação de transpila_canonico para Python puro

## Contexto mínimo

O executor lê o contrato deste step. Implementar a função `transpila_canonico` e a tabela de mapeamento de builtins canônicos em `transpilador_pt/`, gerando Python puro sem depender de builtins em runtime.

- Paths: [`transpilador_pt/dicionario.py`], [`transpilador_pt/transpiler.py`], [`tests/test_transpiler.py`]
- Contrato: AC-01, AC-02, AC-03, ADR-003
- Seam: Testes unitários em `tests/test_transpiler.py`

## Goal

Adicionar o mapeamento `BUILTINS_CANONICOS` e a função `transpila_canonico(codigo_pt: str) -> str`, traduzindo builtins pedagógicos para suas funções equivalentes no Python canônico (`mostre` -> `print`, `tamanho` -> `len`, etc.), preservando atributos de objetos e variáveis locais de atribuição.

## Tarefas

1. Em `transpilador_pt/dicionario.py`:
   - Definir `BUILTINS_CANONICOS`, mapeando identificadores em português para nomes canônicos do Python (ex: `"mostre": "print"`, `"tamanho": "len"`, `"leia": "input"`, `"intervalo": "range"`, etc.) [AC-01] [ADR-003].
2. Em `transpilador_pt/transpiler.py`:
   - Implementar `transpila_canonico(codigo_pt: str) -> str` reutilizando a lógica léxica e de desambiguação de `transpila`:
     - Preservar atributos de objetos precedidos por `.` (`self.tamanho`, `carro.tipo`) [AC-02].
     - Preservar identificadores que são alvos de atribuição (`_has_assignment_until_statement_end`), como `lista = [1, 2, 3]` [AC-01].
     - Substituir chamadas e identificadores de builtins restantes pelos nomes em `BUILTINS_CANONICOS`.
3. Em `tests/test_transpiler.py`:
   - Remover `@unittest.skipIf` dos 4 testes de `transpila_canonico` criados no Step 1 e verificar que todos passam 100% verde [AC-01] [AC-02] [AC-03].

## Delta de complexidade planejado

- Abstrações: none
- Dependências: none (stdlib `tokenize`, `io`, `keyword`)
- Configuração: none
- Extension points: `transpila_canonico` exportada publicamente no pacote
- Camadas arquiteturais: camada de transpilação léxica (`transpiler.py`)

## Fora de Escopo

- Implementação do renderizador lado a lado (Step 3).
- Flags e CLI (Step 4).

## Critério de Pronto

- `python3 -m unittest tests/test_transpiler.py` executa todos os testes com 100% de sucesso sem nenhum skip.
- O código canônico gerado executa de forma autônoma no Python nativo sem injeção de `BUILTINS_PT`.

## Seam de teste

- `tests/test_transpiler.py` via runner `unittest`.

## Dependências

- Step 1 concluído.

## Documentation impact

- Nenhum nesta etapa (documentação consolidada no Step 4).

## Checklist pré-handoff

- [x] ≤ 5 arquivos lógicos afetados no total? (3 arquivos: `transpilador_pt/dicionario.py`, `transpilador_pt/transpiler.py`, `tests/test_transpiler.py`).
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
Arquivos: @transpilador_pt/dicionario.py @transpilador_pt/transpiler.py @tests/test_transpiler.py
Fora de escopo: Modificar transicao.py ou cli.py; bibliotecas externas.
Critério de pronto: python3 -m unittest tests/test_transpiler.py passa 100% verde sem nenhum teste pulado.

---

@specs/steps/fase-3-modo-transicao-e-exportador-step-2.md
@specs/fase-3-modo-transicao-e-exportador.md
@adr/003-estrategia-transicao-bilingue-e-exportacao-canonica.md
```
