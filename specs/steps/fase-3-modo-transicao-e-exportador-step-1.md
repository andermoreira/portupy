# Passo 1: Suíte de testes para exportação canônica, renderização lado a lado e CLI

## Contexto mínimo

O executor lê o contrato deste step. Estabelecer a suíte de testes de unidade e regressão para todas as funcionalidades da Fase 3 antes de alterar o código de produção em `transpilador_pt/` ou `cli.py` (TDD / Regra do Escoteiro).

- Paths: [`tests/test_transpiler.py`], [`tests/test_transicao.py`], [`tests/test_cli.py`]
- Contrato: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, ADR-003
- Seam: Testes automatizados via `unittest` da stdlib em `tests/`

## Goal

Criar casos de teste cobrindo:
1. `transpila_canonico`: tradução de builtins (`mostre` -> `print`, `tamanho` -> `len`, etc.), preservação de atributos após ponto (`objeto.tamanho`) e preservação de variáveis atribuídas (`lista = [1, 2]`).
2. `renderiza_lado_a_lado`: formatação bilíngue em colunas, cabeçalhos, números de linha e responsividade a larguras de terminal.
3. `cli.py`: suporte a `--lado-a-lado`, `--modo-transicao`, `--exportar` com destino e para stdout, e tratamento de erro de arquivo.

## Tarefas

1. Em `tests/test_transpiler.py`:
   - Adicionar casos de teste para `transpila_canonico`:
     - Tradução de builtins essenciais (`mostre` -> `print`, `tamanho` -> `len`, `leia` -> `input`, `intervalo` -> `range`) [AC-01].
     - Preservação estrita de atributos após ponto (`self.tamanho = 10`, `carro.tipo`) [AC-02].
     - Preservação de variáveis atribuídas como `lista = [1, 2, 3]` evitando colisão indevida [AC-01].
     - Validação de que o código gerado por `transpila_canonico` executa diretamente no Python nativo sem depender de `BUILTINS_PT` [AC-03].
2. Criar `tests/test_transicao.py`:
   - Testar `renderiza_lado_a_lado` com código simples, validando presença de cabeçalhos ("Português", "Python Canônico") e delimitadores de linha [AC-04].
   - Testar alinhamento com números de linha sincronizados [AC-04].
   - Testar com largura fixa configurável de terminal (ex.: 80 colunas).
3. Criar `tests/test_cli.py`:
   - Testar invocação com `--lado-a-lado` e alias `--modo-transicao` [AC-05].
   - Testar `--exportar` sem destino (saída em stdout) [AC-06].
   - Testar `--exportar arquivo.py` (criação do arquivo e saída) [AC-06].
   - Testar caminho de erro de exportação para diretório inacessível [AC-06].

*(Nota: os testes que chamam componentes ainda não implementados nos steps 2-4 devem usar `@unittest.expectedFailure` ou importar sob fallback para permitir execução verde da suíte nesta etapa inicial).*

## Delta de complexidade planejado

- Abstrações: none
- Dependências: none (utiliza exclusivamente `unittest`, `tempfile` e stdlib)
- Configuração: none
- Extension points: none
- Camadas arquiteturais: none

## Fora de Escopo

- Implementação do código de produção em `transpilador_pt/` ou `cli.py` (passos 2 a 4).
- Bibliotecas externas de formatação (Rich, Curses).

## Critério de Pronto

- `python3 -m unittest discover -s tests -p "test_*.py"` executa com sucesso (testes anteriores 100% aprovados, e novos testes passando ou marcados como expected failure até a implementação dos passos seguintes).

## Seam de teste

- Runner `unittest` da biblioteca padrão em `tests/`.

## Dependências

- Nenhuma (primeiro passo da Fase 3).

## Documentation impact

- Nenhum (suíte interna de testes).

## Checklist pré-handoff

- [x] ≤ 5 arquivos lógicos afetados no total? (3 arquivos: `tests/test_transpiler.py`, `tests/test_transicao.py`, `tests/test_cli.py`).
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
Arquivos: @tests/test_transpiler.py @tests/test_transicao.py @tests/test_cli.py
Fora de escopo: Modificar código de produção em transpilador_pt/ ou cli.py; bibliotecas externas.
Critério de pronto: python3 -m unittest discover -s tests -p "test_*.py" roda com 100% de sucesso.

---

@specs/steps/fase-3-modo-transicao-e-exportador-step-1.md
@specs/fase-3-modo-transicao-e-exportador.md
@adr/003-estrategia-transicao-bilingue-e-exportacao-canonica.md
```
