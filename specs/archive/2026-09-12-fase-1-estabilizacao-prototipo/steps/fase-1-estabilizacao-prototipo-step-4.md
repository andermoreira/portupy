# Passo 4: Formatação de SyntaxError, IndentationError e sincronização documental

## Contexto mínimo

O executor (`/implement-step`) lê o contrato completo deste step.

- Paths: [`transpilador_pt/erros.py`], [`tests/test_erros.py`], [`README.md`]
- Contrato: AC-05, AC-07
- Seam: Teste unitário via `unittest` em `tests/test_erros.py` e execução manual/automatizada de CLI

## Goal

Habilitar a captura e formatação rica de erros de compilação (`SyntaxError`, `IndentationError`), exibindo o número da linha, o trecho do código original e explicações pedagógicas em português, e atualizar a documentação no [README.md](file:///Users/andersonalves/dev/transpilador-pt/README.md) sincronizando o estado real do projeto.

## Tarefas

1. Em `transpilador_pt/erros.py`:
   - No `formata_erro_amigavel`:
     - Se `isinstance(exc, SyntaxError)`: obter `linha_numero = exc.lineno` e `coluna = exc.offset`.
     - Se `linha_numero` for válido em `linhas_fonte_pt`, incluir a linha do código original e, se `coluna` estiver disponível, incluir apontador visual `^`.
   - Adicionar regras no catálogo `REGRAS`:
     - `IndentationError` (`expected an indented block`): explicar que faltou indentar o bloco para a direita.
     - `IndentationError` (`unindent does not match any outer indentation level`): explicar desalinhamento de recuo.
     - `SyntaxError` (`invalid syntax`): explicar erros comuns de escrita como esquecer dois pontos (`:`) ou parênteses.
     - `SyntaxError` (`unexpected EOF while parsing`): explicar falta de fechamento de parêntese, colchete ou aspas.
     - `SyntaxError` (`unterminated string literal` / `EOL while scanning string literal`): explicar aspas não fechadas na linha.
2. Em `tests/test_erros.py`:
   - Remover `@unittest.expectedFailure` de `test_regressao_formata_erro_syntax_error`.
   - Adicionar teste cobrindo `IndentationError` com indicação de linha.
3. Em `README.md`:
   - Atualizar a lista de recursos funcionais para refletir:
     - Execução de f-strings com builtins em runtime (ADR-001).
     - Liberdade para declarar variáveis com nomes de tipos (`lista`, `texto`, `tipo`).
     - Preservação de atributos de objetos (`self.tipo`, `objeto.tipo`).
     - Detecção e tradução de `SyntaxError` e `IndentationError` com indicação visual de linha.
   - Atualizar a suíte de testes documentada com instrução de execução via `unittest`.

## Delta de complexidade planejado

- Abstrações: none
- Dependências: none (stdlib Python)
- Configuração: none
- Extension points: none
- Camadas arquiteturais: none

## Fora de Escopo

- Modificar regras da Fase 2 (`senao se` / `nao eh`).
- Alterações em `transpiler.py` ou `dicionario.py`.

## Critério de Pronto

- `python3 -m unittest discover -s tests -p "test_*.py"` passa 100% verde (0 falhas, 0 falhas esperadas).
- Erros de sintaxe exibem `Na linha X: ...` com mensagem em português.
- O [README.md](file:///Users/andersonalves/dev/transpilador-pt/README.md) reflete fielmente as capacidades e testes do repositório.

## Seam de teste

- `tests/test_erros.py` via `unittest`.

## Dependências

- Passo 3 (`specs/steps/fase-1-estabilizacao-prototipo-step-3.md`).

## Documentation impact

- [README.md](file:///Users/andersonalves/dev/transpilador-pt/README.md): atualizar seções "O que já funciona", "Limitações conhecidas" e instruções de testes.

## Checklist pré-handoff

- [x] ≤ 5 arquivos lógicos afetados no total? (3 arquivos: `transpilador_pt/erros.py`, `tests/test_erros.py`, `README.md`).
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
Arquivos: @transpilador_pt/erros.py @tests/test_erros.py @README.md
Fora de escopo: Alterações em dicionario.py, transpiler.py ou executor.py.
Critério de pronto: python3 -m unittest discover -s tests -p "test_*.py" roda com 100% de aprovação (0 falhas esperadas); README.md atualizado.

---

@specs/steps/fase-1-estabilizacao-prototipo-step-4.md
@specs/fase-1-estabilizacao-prototipo.md
```
