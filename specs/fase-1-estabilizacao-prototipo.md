# Spec: Fase 1 — Estabilização do Protótipo

## Goal
Estabilizar o protótipo do Transpilador PT corrigindo a execução de f-strings com funções embutidas, liberando nomes comuns de variáveis (`lista`, `texto`, `tipo`), preservando o acesso a atributos de objetos e garantindo indicação correta de linha em erros de compilação (`SyntaxError` e `IndentationError`).

## Non-goals
- Reescrever a gramática de estruturas compostas como `senao se` e `nao eh` (escopo da Fase 2).
- Desenvolver interface gráfica web ou empacotamento com Pyodide/WASM (escopo da Fase 4).
- Traduzir métodos internos de tipos padrão do Python como `.append()`, `.split()` ou `.upper()`.
- Criar um novo parser sintático completo ou AST customizado (a ferramenta continuará utilizando a abordagem leve de tokenização com injeção de runtime).

## User stories
- **Story 1 (Caminho feliz - f-strings e builtins):**
  - **Given** um arquivo `.ptpy` contendo f-strings que interpolam funções embutidas (ex.: `{tamanho(nomes)}`),
  - **When** o estudante executar o código via CLI,
  - **Then** a função deve ser resolvida em tempo de execução e a saída formatada deve ser exibida sem erro de `NameError`.
- **Story 2 (Caminho feliz - nomes de variáveis naturais):**
  - **Given** um estudante declarando variáveis com nomes em português comuns como `lista = [1, 2, 3]`, `texto = "olá"` ou `tipo = "admin"`,
  - **When** o código for transpilado e executado,
  - **Then** a atribuição deve ocorrer normalmente sem disparar bloqueios artificiais de palavra reservada.
- **Story 3 (Caminho feliz - atributos de instâncias e classes):**
  - **Given** uma classe com métodos manipulando atributos (ex.: `self.tipo = tipo`),
  - **When** o transpilador processar o código,
  - **Then** tokens precedidos por `.` não devem ser alterados nem considerados alvos de atribuição ilegal.
- **Story 4 (Caminho de erro amigável - sintaxe e indentação):**
  - **Given** um estudante que esqueceu os dois pontos `:` em um bloco ou desalinhou a indentação,
  - **When** o interpretador disparar `SyntaxError` ou `IndentationError`,
  - **Then** o sistema deve exibir a linha exata e o trecho correspondente no arquivo `.ptpy` original, acompanhados de mensagem em português.

## Assumptions
- O ambiente de execução é Python 3.9 ou superior utilizando apenas a biblioteca padrão (`tokenize`, `io`, `unittest`) [VERIFIED: Python 3.9.6 local].
- A execução ocorre em processo via `exec()` no ambiente educacional controlado do usuário.
- Builtins em português podem ser injetados no escopo global/builtin de execução sem necessidade de reescrever tokens literais em f-strings [ADR-001].

## Risks
- **Poluição de namespace global:** A injeção de builtins em português em `exec()` pode colidir com código Python padrão se não for isolada por execução.
  - *Mitigação:* Passar um dicionário isolado contendo `{"__name__": "__main__", **BUILTINS_PT}` no boundary de execução de `executor.py`.
- **Regressão de palavras-chave estruturais:** Ao afrouxar a restrição de variáveis, garantir que palavras de controle de fluxo (`se`, `para`, `enquanto`, `funcao`, `retorne`) continuem estritamente protegidas contra atribuição indevida.
  - *Mitigação:* Manter conjunto `PALAVRAS_CHAVE` explicitamente isolado e validado em testes unitários.

## Error handling
- Erros de compilação em `executor.py` (`SyntaxError`, `IndentationError`, `TabError`) devem ser interceptados antes de `exec()`.
- O formatador amigável deve extrair metadados diretamente de `exc.lineno`, `exc.text` e `exc.offset` quando `exc.__traceback__` for nulo.
- Exceções do transpilador (`ErroDeTraducao`) continuam fornecendo feedback imediato em caso de tokenização corrompida ou tentativa de atribuição a palavras de sintaxe (`para = 5`).

## Observability
A ferramenta é uma CLI síncrona local para estudantes. A observabilidade é garantida por meio de:
- Saída amigável em stdout/stderr com código de saída (`exit code`) apropriado.
- Inspeção transparente do código intermediário através da flag `--mostrar-python`.
- Logs externos ou métricas de telemetria não se aplicam e estão fora de escopo para manter a ferramenta livre de dependências e invasão de privacidade.

## Threat model
- **Superfície de Ataque:** Leitura de arquivos `.ptpy` do disco e compilação via `compile()`/`exec()`.
- **Controle de Acesso:** O CLI executa com as permissões do próprio usuário do sistema operacional, similar ao interpretador `python3`.
- **Injeção / Sanitização:** Não há parsing de rede ou múltiplos tenants. O uso de `exec()` é inerente ao modelo de execução in-process da CLI educacional.

## Fatos verificados
- Em Python 3.9.6, `tokenize.generate_tokens` trata f-strings inteiras como token único `token.STRING`, não gerando `token.NAME` para identificadores dentro de `{}` [evidência: `python3 cli.py transpilador_pt/exemplos/ola.ptpy` resulta em `NameError: 'tamanho'`].
- Em `SyntaxError` originado em `compile()`, `exc.__traceback__` é `None`, fazendo com que [erros.py](file:///Users/andersonalves/dev/transpilador-pt/transpilador_pt/erros.py#L118) falhe em identificar a linha do erro [evidência: execução de `executa_codigo('se verdadeiro:\nmostre(1)')` omite o trecho da linha].

## Acceptance criteria
- **AC-01:** O arquivo [transpilador_pt/exemplos/ola.ptpy](file:///Users/andersonalves/dev/transpilador-pt/transpilador_pt/exemplos/ola.ptpy) executa via CLI com sucesso, imprimindo as saudações e o total de nomes sem disparar `NameError` [pedido]
- **AC-02:** Atribuições a variáveis com nomes de builtins em português (`lista = [1, 2]`, `texto = "abc"`, `tipo = 10`, `minimo = 0`) transpilam e executam sem disparar `ErroDeTraducao` [ADR-001]
- **AC-03:** Tentativas de atribuição a palavras-chave estruturais (`para = 1`, `se = 2`, `enquanto = 3`) disparam `ErroDeTraducao` explicativo [código: transpilador_pt/transpiler.py:48]
- **AC-04:** Acessos e atribuições a atributos de objetos (`objeto.tipo`, `self.tipo = valor`, `df.maximo()`) não sofrem substituição de tokens e não disparam erro de palavra reservada [código: transpilador_pt/transpiler.py:43]
- **AC-05:** Erros de sintaxe (`SyntaxError`) e indentação (`IndentationError`) exibem a linha e o trecho de código formatados com mensagem amigável no terminal [código: transpilador_pt/erros.py:115]
- **AC-06:** Uma suíte de testes automatizados com `unittest` cobre transpilação, execução, builtins e tratamento de erros de compilação, com 100% de aprovação [derivado]
- **AC-07:** O arquivo [README.md](file:///Users/andersonalves/dev/transpilador-pt/README.md) documenta o modelo de builtins em runtime e tem seus exemplos sincronizados com o comportamento real [código: README.md:28]

## Open questions
- Nenhuma questão bloqueadora para a execução da Fase 1.

## Implementation plan
1. Criar harness de testes automatizados com `unittest` reproduzindo as falhas atuais em f-strings, nomes de variáveis e erros de compilação [AC-06]
2. Desacoplar `BUILTINS` de `PALAVRAS_CHAVE` no transpilador e implementar injeção de builtins em runtime no `executor.py` [AC-01] [AC-02] [AC-03] [ADR-001]
3. Implementar sensibilidade a contexto no `transpiler.py` para ignorar tokens precedidos pelo operador ponto `.` [AC-04]
4. Implementar captura e formatação enriquecida de `SyntaxError` e `IndentationError` em `erros.py` e sincronizar documentação [AC-05] [AC-07]

## Documentation impact
- [README.md](file:///Users/andersonalves/dev/transpilador-pt/README.md): Atualizar a seção "O que já funciona" e "Limitações conhecidas" para refletir a injeção em runtime e o suporte robusto a f-strings e erros de sintaxe (Step 4).
