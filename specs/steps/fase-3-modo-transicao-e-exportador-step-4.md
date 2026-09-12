# Passo 4: Integração CLI e sincronização da documentação no README

## Contexto mínimo

O executor lê o contrato deste step. Conectar os módulos `transpila_canonico` e `renderiza_lado_a_lado` à interface de linha de comando `cli.py`, remover os expected failures de `tests/test_cli.py` e atualizar a documentação no `README.md`.

- Paths: [`cli.py`], [`tests/test_cli.py`], [`README.md`]
- Contrato: AC-05, AC-06, AC-08, ADR-003
- Seam: Testes de ponta a ponta da CLI em `tests/test_cli.py`

## Goal

Integrar na CLI as opções `--lado-a-lado` (e alias `--modo-transicao`) e `--exportar [caminho.py]`, com tratamento amigável de erros de gravação em disco e documentação no `README.md`.

## Tarefas

1. Em `cli.py`:
   - Tratar argumentos de linha de comando:
     - Detectar `--lado-a-lado` e `--modo-transicao`: transpilar para canônico e exibir tabela com `renderiza_lado_a_lado` antes de prosseguir com a execução [AC-05].
     - Detectar `--exportar [destino.py]`:
       - Se informado destino, salvar o código Python canônico com confirmação amigável no stdout [AC-06].
       - Se nenhum destino for passado, imprimir o código Python canônico em stdout [AC-06].
       - Em caso de falha de escrita em disco, exibir `⚠️ Não consegui salvar o arquivo exportado: <motivo>` em stderr e retornar código de saída `1` [AC-06].
       - O comando `--exportar` apenas exporta e não executa o script [AC-06].
     - Atualizar mensagem de ajuda/uso da CLI.
2. Em `tests/test_cli.py`:
   - Remover `@unittest.expectedFailure` dos 5 testes da CLI e assegurar que passem 100% verde [AC-07].
3. Em `README.md`:
   - Adicionar seção e exemplos explicando `--lado-a-lado` e `--exportar` [AC-08].
   - Atualizar status da Fase 3 para concluída no roadmap pedagógico.

## Delta de complexidade planejado

- Abstrações: none
- Dependências: none (stdlib)
- Configuração: none
- Extension points: novas flags na CLI
- Camadas arquiteturais: camada de entrada/saída de linha de comando (`cli.py`)

## Fora de Escopo

- Interface web Pyodide (Fase 4).
- Alteração da lógica interna do executor ou transpilador.

## Critério de Pronto

- `python3 -m unittest discover -s tests -p "test_*.py"` roda com 100% de sucesso sem nenhum failure, error ou expectedFailure.
- Execução manual de `python3 cli.py transpilador_pt/exemplos/ola.ptpy --lado-a-lado` exibe a tabela comparativa e o resultado.
- Execução manual de `python3 cli.py transpilador_pt/exemplos/ola.ptpy --exportar` imprime o código puro no stdout.

## Seam de teste

- `tests/test_cli.py` via runner `unittest`.

## Dependências

- Steps 1, 2 e 3 concluídos.

## Documentation impact

- [README.md](file:///Users/andersonalves/dev/transpilador-pt/README.md) atualizado com a documentação do modo de transição e exportador.

## Checklist pré-handoff

- [x] ≤ 5 arquivos lógicos afetados no total? (3 arquivos: `cli.py`, `tests/test_cli.py`, `README.md`).
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
Arquivos: @cli.py @tests/test_cli.py @README.md
Fora de escopo: Modificar motor de transpilação; bibliotecas externas.
Critério de pronto: python3 -m unittest discover -s tests -p "test_*.py" roda com 100% de sucesso (44 testes verdes).

---

@specs/steps/fase-3-modo-transicao-e-exportador-step-4.md
@specs/fase-3-modo-transicao-e-exportador.md
@adr/003-estrategia-transicao-bilingue-e-exportacao-canonica.md
```
