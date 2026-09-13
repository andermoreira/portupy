# Passo 4: Integração CLI --web, validação do Playground e documentação no README

## Contexto mínimo

O executor lê o contrato deste step. Conectar o servidor web local à CLI (`cli.py --web [porta]`), adicionar testes de integração para o comando `--web` em `tests/test_cli.py` e atualizar a documentação pública no `README.md` marcando a Fase 4 como concluída.

- Paths: [`cli.py`], [`tests/test_cli.py`], [`README.md`]
- Contrato: AC-07, AC-08, AC-09, ADR-004
- Seam: CLI `cli.py` e documentação pública

## Goal

Adicionar suporte ao argumento `--web [porta]` na CLI principal que inicia o servidor local da pasta `web/` e abre o navegador, validar testes unitários e ponta a ponta, e atualizar o `README.md` com exemplos práticos.

## Tarefas

1. Em `cli.py`:
   - Tratar flag `--web [porta]`:
     - Se `--web` for passado, localizar o diretório `web/` na raiz do projeto.
     - Identificar porta opcional (ex.: `python3 cli.py --web 8080`, padrão 8000).
     - Chamar `inicia_servidor_web(diretorio_web, porta=porta, abrir_navegador=True)`.
     - Atualizar a mensagem de ajuda/uso da CLI:
       `Uso: python3 cli.py [arquivo.ptpy | --web [porta]] [--mostrar-python] [--lado-a-lado] [--exportar [destino.py]]`
2. Em `tests/test_cli.py`:
   - Adicionar teste validando invocação de `cli.py --web` com mock de `inicia_servidor_web` [AC-07] [AC-08].
3. Em `README.md`:
   - Adicionar seção explicando o Playground Web e o comando `python3 cli.py --web` [AC-09].
   - Atualizar a árvore do projeto com a pasta `web/`.
   - Atualizar o status da Fase 4 no roadmap para concluído [AC-09].

## Delta de complexidade planejado

- Abstrações: none
- Dependências: none (stdlib)
- Configuração: none
- Extension points: flag `--web` na CLI
- Camadas arquiteturais: camada de interface de linha de comando (`cli.py`)

## Fora de Escopo

- Modificação dos motores de transpilação e execução.
- Ferramentas de build adicionais (npm).

## Critério de Pronto

- `python3 -m unittest discover -s tests -p "test_*.py"` roda com 100% de sucesso.
- `python3 cli.py --web` sobe o servidor da pasta `web/` e retorna código adequado.
- `README.md` documenta a Fase 4 como concluída.

## Seam de teste

- `tests/test_cli.py` e `tests/test_cli_web.py` via runner `unittest`.

## Dependências

- Steps 1, 2 e 3 concluídos.

## Documentation impact

- [README.md](file:///Users/andersonalves/dev/transpilador-pt/README.md) atualizado com documentação da Fase 4 e Playground Web.

## Checklist pré-handoff

- [x] ≤ 5 arquivos lógicos afetados no total? (3 arquivos de produção/teste/doc: `cli.py`, `tests/test_cli.py`, `README.md`).
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
Fora de escopo: Modificar motores internos; bibliotecas externas.
Critério de pronto: python3 -m unittest discover passa 100% verde e cli.py suporta --web.

---

@specs/steps/fase-4-playground-web-pyodide-step-4.md
@specs/fase-4-playground-web-pyodide.md
@adr/004-arquitetura-playground-web-client-side-pyodide.md
```
