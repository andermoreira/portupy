# Matriz de suporte da linguagem

Este documento descreve o contrato atual do PortuPy. A implementação usa o
tokenizador da biblioteca padrão e traduz somente os tokens e contextos listados aqui. A
presença de uma construção no Python não significa que exista uma tradução equivalente em
português.

## Estruturas e operadores

| Categoria | Formas em português | Resultado canônico | Cobertura |
| --- | --- | --- | --- |
| Condicional | `se`, `senao`, `senão`, `senaose`, `senãose`, `ouse` | `if`, `else`, `elif` | Testada |
| Laços | `para`, `em`, `enquanto` | `for`, `in`, `while` | Testada |
| Declarações | `funcao`, `função`, `classe`, `retorne` | `def`, `class`, `return` | Testada |
| Importação e contexto | `importe`, `de`, `como`, `com` | `import`, `from`, `as`, `with` | Testada |
| Exceções | `tente`, `exceto`, `finalmente`, `levante` | `try`, `except`, `finally`, `raise` | Testada |
| Controle de fluxo | `quebre`, `continue`, `passe`, `del`, `assert` | `break`, `continue`, `pass`, `del`, `assert` | Testada |
| Lógica | `nao`, `não`, `e`, `ou` | `not`, `and`, `or` | Testada |
| Comparação contextual | `eh`, `é`, `nao eh`, `não é` | `is`/`==`, `is not`/`!=` | Testada |
| Assíncrono e geradores | `assincrono`, `aguarde`, `produza` | `async`, `await`, `yield` | Compilação testada |
| Outros | `lambda`, `global` | `lambda`, `global` | Compilação testada |
| Literais | `verdadeiro`, `falso`, `nulo` | `True`, `False`, `None` | Testada |

As formas sem acento continuam disponíveis para facilitar a digitação em teclados sem layout
português. `ouse` é mantido apenas por compatibilidade com versões anteriores.

## Builtins pedagógicos

| Português | Python canônico |
| --- | --- |
| `mostre`, `mostra` | `print` |
| `leia` | `input` |
| `tamanho` | `len` |
| `intervalo` | `range` |
| `tipo` | `type` |
| `texto`, `inteiro`, `decimal`, `booleano` | `str`, `int`, `float`, `bool` |
| `lista`, `dicionario`, `dicionário`, `conjunto`, `tupla` | `list`, `dict`, `set`, `tuple` |
| `ordene`, `inverta` | `sorted`, `reversed` |
| `some`, `maximo`, `máximo`, `minimo`, `mínimo` | `sum`, `max`, `min` |
| `absoluto`, `arredonde` | `abs`, `round` |
| `enumere`, `zip`, `mapeie`, `filtre` | `enumerate`, `zip`, `map`, `filter` |

Esses nomes são injetados no executor local. O modo `--exportar` os substitui pelos nomes
canônicos para que o arquivo gerado não dependa do pacote. Um nome que o programa vincula
(variável, parâmetro, função, import) continua com a grafia do aluno: em
`lista = [1, 2]` o nome `lista` é preservado. Sem vínculo, o nome vira o builtin mesmo quando
usado como valor, como em `isinstance(x, inteiro)` → `isinstance(x, int)`.

## O que permanece Python

- Strings, comentários, números, indentação e identificadores Unicode são preservados.
- Métodos e atributos, como `lista.append()`, `texto.split()` e `objeto.tipo`, permanecem com
  a grafia original. `split()` separa um texto em partes e, sem argumentos, usa os
  espaços em branco como separadores.
- O primeiro parâmetro de um método de instância pode usar qualquer identificador válido.
  O exemplo `classes.ptpy` usa `instância`. Em Python, a convenção é `self`. O nome
  especial `__init__` mantém a grafia exigida pelo Python.
- Bibliotecas e nomes externos, como `requests`, `pandas` e `math`, permanecem em inglês.
- A gramática que não aparece nesta matriz segue as regras do parser Python; o transpilador não
  implementa um parser de linguagem natural próprio.

## Limites operacionais

- Palavras estruturais como `para`, `em`, `e`, `ou` e `com` não podem ser usadas como nomes de
  variáveis nesta camada.
- A CLI executa arquivos locais no processo Python atual e não fornece sandbox.
- No navegador, o Pyodide e o transpilador rodam localmente em um Worker WebAssembly. O runtime
  usado pelo playground é versionado em `web/vendor/pyodide/` e os hashes ficam no manifesto.
- O playground seleciona a linha de um diagnóstico que aponta para o programa aberto. O download
  de `script.py` requer que a tradução da execução atual compile no Python do playground.
  Programas baixados podem precisar de bibliotecas importadas pelo próprio código.
- O rascunho editado fica no armazenamento local do navegador, quando disponível, e permanece
  acessível ao trocar de exemplo. Alterar o conteúdo do editor atualiza o rascunho.

Os testes em `tests/test_linguagem.py`, `tests/test_transpiler.py` e `tests/test_web_assets.py`
guardam as partes executáveis deste contrato.
