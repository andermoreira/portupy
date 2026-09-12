# Passo 1: Suíte de testes automatizados e casos de regressão

## Contexto mínimo

O executor (`/implement-step`) lê o contrato completo deste step. Não alterar código de produção em `transpilador_pt/` neste passo; o foco exclusivo é estabelecer a linha de base de testes e registrar as falhas atuais.

- Paths: [`transpilador_pt/transpiler.py`], [`transpilador_pt/executor.py`], [`transpilador_pt/erros.py`]
- Contrato: AC-06, Regra do Escoteiro para Legado
- Seam: Teste unitário e de integração via `unittest` da stdlib em `tests/`

## Goal

Estabelecer o harness de testes automatizados utilizando `unittest` e registrar casos de teste para o comportamento atual do transpilador, executor e formatador de erros, incluindo testes de regressão para os bugs identificados (f-strings, nomes de variáveis, atributos e erros de compilação).

## Tarefas

1. Criar `tests/__init__.py` para inicializar o pacote de testes do projeto.
2. Criar `tests/test_transpiler.py` testando a função `transpila`:
   - Casos felizes de tradução básica (`se`, `para`, `funcao`, `retorne`).
   - Detecção de atribuição ilegal a palavras estruturais (`para = 5` dispara `ErroDeTraducao`).
   - Casos de regressão marcados: registrar o comportamento atual que bloqueia `lista = [1, 2]` e corrompe `self.tipo = 1`.
3. Criar `tests/test_executor.py` testando `executa_codigo`:
   - Execução de script simples com saída capturada (ex.: `mostre("teste")`).
   - Caso de regressão marcado: registrar a falha atual do script [transpilador_pt/exemplos/ola.ptpy](file:///Users/andersonalves/dev/transpilador-pt/transpilador_pt/exemplos/ola.ptpy) com `NameError` em `{tamanho(nomes)}` (usando `unittest.expectedFailure` ou captura de saída de erro).
4. Criar `tests/test_erros.py` testando `traduz_excecao` e `formata_erro_amigavel`:
   - Casos conhecidos de runtime (`IndexError`, `ZeroDivisionError`, `NameError`).
   - Caso de regressão marcado: registrar que `SyntaxError` e `IndentationError` emitem `Detalhe técnico (ainda sem tradução)` e omitem a indicação da linha (`Na linha X`).

## Delta de complexidade planejado

- Abstrações: none
- Dependências: none (utiliza exclusivamente `unittest` da biblioteca padrão do Python)
- Configuração: none
- Extension points: none
- Camadas arquiteturais: none

## Fora de Escopo

- Modificar o código de produção em `transpilador_pt/` ou `cli.py` (correções pertencem aos passos 2, 3 e 4).
- Adicionar dependências externas como `pytest`, `coverage` ou linters.
- Implementar novas palavras-chave ou regras de tradução da Fase 2.

## Critério de Pronto

- Comando `python3 -m unittest discover -s tests -p "test_*.py"` roda com sucesso (testes regulares passam e falhas conhecidas de f-string/variáveis passam como `expectedFailure` ou asserções do estado atual documentado).

## Seam de teste

- `tests/test_transpiler.py`, `tests/test_executor.py` e `tests/test_erros.py` via runner `unittest` da stdlib.

## Dependências

- Nenhuma (primeiro passo).

## Documentation impact

- Nenhum — harness interno de testes sem impacto na documentação de usuário.

## Checklist pré-handoff

- [x] ≤ 5 arquivos lógicos afetados no total? (4 arquivos novos: `tests/__init__.py`, `tests/test_transpiler.py`, `tests/test_executor.py`, `tests/test_erros.py`).
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
Arquivos: @transpilador_pt/transpiler.py @transpilador_pt/executor.py @transpilador_pt/erros.py @tests/
Fora de escopo: Modificar código de produção em transpilador_pt/ ou cli.py; adicionar dependências externas (pytest, tox).
Critério de pronto: python3 -m unittest discover -s tests -p "test_*.py" executa e passa 100% de forma determinística (falhas de f-string e nomes de variáveis documentadas ou marcadas com expectedFailure).

---

@specs/steps/fase-1-estabilizacao-prototipo-step-1.md
@specs/fase-1-estabilizacao-prototipo.md
```
