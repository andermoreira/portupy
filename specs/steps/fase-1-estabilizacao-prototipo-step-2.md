# Passo 2: Desacoplamento de builtins e injeção em runtime

## Contexto mínimo

O executor (`/implement-step`) lê o contrato completo deste step.
Este passo implementa a decisão arquitetural formalizada no [ADR-001](../../adr/001-separacao-builtins-runtime-transpilacao-sintaxe.md).

- Paths: [`transpilador_pt/dicionario.py`], [`transpilador_pt/transpiler.py`], [`transpilador_pt/executor.py`], [`tests/test_executor.py`], [`tests/test_transpiler.py`]
- Contrato: AC-01, AC-02, AC-03, ADR-001
- Seam: Teste unitário e de integração via `unittest` em `tests/test_transpiler.py` e `tests/test_executor.py`

## Goal

Desacoplar funções e tipos embutidos (`BUILTINS`) das palavras-chave sintáticas (`PALAVRAS_CHAVE`), fazendo o transpilador substituir apenas a gramática da linguagem e injetando as funções em português diretamente no escopo de execução do executor, resolvendo f-strings e liberando o uso de nomes de variáveis como `lista` e `texto`.

## Tarefas

1. Em `transpilador_pt/dicionario.py`:
   - Separar claramente `PALAVRAS_CHAVE` (palavras que o interpretador precisa na sintaxe: `se`, `para`, `funcao`, `retorne`, `enquanto`, `classe`, etc.).
   - Criar e exportar o mapeamento de funções/tipos reais `BUILTINS_PT` associando os nomes em português aos respectivos objetos do Python (`"mostre": print`, `"tamanho": len`, `"intervalo": range`, `"texto": str`, `"inteiro": int`, `"decimal": float`, `"booleano": bool`, `"lista": list`, `"dicionario": dict`, `"dicionário": dict`, `"conjunto": set`, `"tupla": tuple`, `"ordene": sorted`, `"inverta": reversed`, `"some": sum`, `"maximo": max`, `"máximo": max`, `"minimo": min`, `"mínimo": min`, `"absoluto": abs`, `"arredonde": round`, `"enumere": enumerate`, `"zip": zip`, `"mapeie": map`, `"filtre": filter`, `"leia": input`).
   - Manter `MAPA = PALAVRAS_CHAVE` para o transpilador léxico.
2. Em `transpilador_pt/transpiler.py`:
   - Atualizar a checagem de atribuição: apenas tokens contidos em `PALAVRAS_CHAVE` devem disparar o `ErroDeTraducao` de palavra reservada (`para = 1`).
   - Não interferir em atribuições a nomes de builtins (`lista = [1, 2, 3]` deve transpilar normalmente como atribuição).
3. Em `transpilador_pt/executor.py`:
   - Importar `BUILTINS_PT` de `dicionario.py`.
   - Na chamada `exec(compilado, contexto)`, garantir que o contexto global contenha `{"__name__": "__main__", **BUILTINS_PT}`.
4. Em `tests/test_transpiler.py` e `tests/test_executor.py`:
   - Remover os decorators `@unittest.expectedFailure` de:
     - `test_regressao_atribuicao_variavel_com_nome_builtin`
     - `test_regressao_executa_codigo_fstring_com_builtin`
     - `test_regressao_arquivo_exemplo_ola`
   - Validar que todos agora passam como `ok`.

## Delta de complexidade planejado

- Abstrações: none
- Dependências: none (stdlib Python)
- Configuração: none
- Extension points: none
- Camadas arquiteturais: none

## Fora de Escopo

- Modificar manipulação de atributos de objetos com ponto (`self.tipo = 1`) — escopo do Passo 3.
- Modificar o formatador de mensagens para `SyntaxError` / `IndentationError` — escopo do Passo 4.
- Implementar suporte a `senao se` / `nao eh` — escopo da Fase 2.

## Critério de Pronto

- `python3 -m unittest tests/test_transpiler.py tests/test_executor.py` passa 100% sem falhas esperadas para esses 3 testes.
- `python3 cli.py transpilador_pt/exemplos/ola.ptpy` executa até o fim imprimindo `Total de nomes: 3` sem qualquer `NameError`.

## Seam de teste

- `tests/test_transpiler.py` e `tests/test_executor.py` via `unittest`.

## Dependências

- Passo 1 (`specs/steps/fase-1-estabilizacao-prototipo-step-1.md`).

## Documentation impact

- Nenhum — documentação será atualizada no Passo 4 ao concluir a Fase 1.

## Checklist pré-handoff

- [x] ≤ 5 arquivos lógicos afetados no total? (5 arquivos: `transpilador_pt/dicionario.py`, `transpilador_pt/transpiler.py`, `transpilador_pt/executor.py`, `tests/test_transpiler.py`, `tests/test_executor.py`).
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
Arquivos: @transpilador_pt/dicionario.py @transpilador_pt/transpiler.py @transpilador_pt/executor.py @tests/test_transpiler.py @tests/test_executor.py
Fora de escopo: Modificar tratamento de atributos após ponto; alterar tratamento de SyntaxError em erros.py.
Critério de pronto: python3 -m unittest tests/test_transpiler.py tests/test_executor.py passa 100% verde; python3 cli.py transpilador_pt/exemplos/ola.ptpy executa com sucesso.

---

@specs/steps/fase-1-estabilizacao-prototipo-step-2.md
@specs/fase-1-estabilizacao-prototipo.md
@adr/001-separacao-builtins-runtime-transpilacao-sintaxe.md
```
