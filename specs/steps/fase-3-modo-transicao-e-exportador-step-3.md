# Passo 3: Módulo de transição bilíngue com visualização lado a lado

## Contexto mínimo

O executor lê o contrato deste step. Implementar o módulo `transpilador_pt/transicao.py` contendo `renderiza_lado_a_lado`, formatando código em português e Python canônico em colunas paralelas e sincronizadas no terminal com stdlib.

- Paths: [`transpilador_pt/transicao.py`], [`tests/test_transicao.py`]
- Contrato: AC-04, ADR-003
- Seam: Testes unitários em `tests/test_transicao.py`

## Goal

Criar a função `renderiza_lado_a_lado(codigo_pt: str, codigo_py: str, largura_terminal: int | None = None) -> str` com cabeçalhos bilíngues claros, separadores de tabela, numeração de linhas e adaptação responsiva para diferentes larguras de terminal via `shutil.get_terminal_size()`.

## Tarefas

1. Criar `transpilador_pt/transicao.py`:
   - Implementar `renderiza_lado_a_lado(codigo_pt: str, codigo_py: str, largura_terminal: int | None = None) -> str`:
     - Determinar largura das colunas baseada em `shutil.get_terminal_size(fallback=(80, 24)).columns` quando `largura_terminal is None` [ADR-003].
     - Dividir os códigos linha a linha com `itertools.zip_longest(fillvalue="")`.
     - Formatar cabeçalho com identificadores: `Linha`, `Código em Português` e `Python Canônico` [AC-04].
     - Usar divisores elegantes (`│`, `─`, `┼`) e numeração de linha à esquerda.
     - Garantir que terminais estreitos (< 60 colunas) ajustem o espaçamento sem estourar quebra de linhas.
2. Em `transpilador_pt/__init__.py`:
   - Exportar `renderiza_lado_a_lado`.
3. Em `tests/test_transicao.py`:
   - Remover `@unittest.skipIf` dos 4 testes de transição e verificar execução 100% verde [AC-04].

## Delta de complexidade planejado

- Abstrações: none
- Dependências: none (utiliza exclusivamente `shutil`, `itertools` da stdlib)
- Configuração: none
- Extension points: `renderiza_lado_a_lado` exportada no pacote
- Camadas arquiteturais: camada de visualização/transição pedagógica (`transicao.py`)

## Fora de Escopo

- Integração com flags da CLI e exportação para disco (Step 4).
- Bibliotecas externas de UI/TUI (Rich, Textual, Curses).

## Critério de Pronto

- `python3 -m unittest tests/test_transicao.py` executa todos os testes com 100% de sucesso sem nenhum teste pulado.

## Seam de teste

- `tests/test_transicao.py` via runner `unittest`.

## Dependências

- Step 2 concluído.

## Documentation impact

- Nenhum nesta etapa (documentação consolidada no Step 4).

## Checklist pré-handoff

- [x] ≤ 5 arquivos lógicos afetados no total? (3 arquivos: `transpilador_pt/transicao.py`, `transpilador_pt/__init__.py`, `tests/test_transicao.py`).
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
Arquivos: @transpilador_pt/transicao.py @transpilador_pt/__init__.py @tests/test_transicao.py
Fora de escopo: Modificar cli.py ou README.md; dependências externas.
Critério de pronto: python3 -m unittest tests/test_transicao.py roda com 100% de sucesso sem skips.

---

@specs/steps/fase-3-modo-transicao-e-exportador-step-3.md
@specs/fase-3-modo-transicao-e-exportador.md
@adr/003-estrategia-transicao-bilingue-e-exportacao-canonica.md
```
