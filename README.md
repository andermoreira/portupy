# Transpilador PT — protótipo

Protótipo funcional de um transpilador Python-em-português, construído
com o módulo `tokenize` da stdlib (sem parser próprio).

## Estrutura

```
transpilador_pt/
├── dicionario.py   # palavras-chave estruturais + builtins PT em runtime
├── transpiler.py   # transpilador com fusão de tokens e sensibilidade a contexto
├── erros.py        # tradução de exceções e formatação com apontador visual
├── executor.py      # compila e roda com injeção de builtins PT
└── exemplos/
    ├── ola.ptpy
    ├── erro.ptpy
    └── condicionais.ptpy
adr/                # Architecture Decision Records (ADR 001, ADR 002)
specs/              # especificações arquivadas e passos de implementação
tests/              # suíte de testes automatizados (unittest)
cli.py              # python3 cli.py arquivo.ptpy [--mostrar-python]
```

## Como rodar

```bash
# Executar scripts de exemplo
python3 cli.py transpilador_pt/exemplos/ola.ptpy
python3 cli.py transpilador_pt/exemplos/condicionais.ptpy
python3 cli.py transpilador_pt/exemplos/erro.ptpy
python3 cli.py transpilador_pt/exemplos/condicionais.ptpy --mostrar-python   # ver o Python gerado

# Executar a suíte de testes automatizados
python3 -m unittest discover -s tests -p "test_*.py"
```

A CLI retorna código `0` em caso de sucesso e `1` quando há erro no código ou no arquivo informado.

## O que já funciona

- **Injeção de builtins em runtime (ADR-001):** Funções e tipos curados (`mostre`, `leia`, `tamanho`, `intervalo`, `lista`, `texto`, etc.) são injetados diretamente no ambiente de execução.
- **f-strings nativas:** Expressões interpoladas como `f"Total: {tamanho(nomes)}"` funcionam sem atrito em qualquer versão do Python.
- **Condicionais encadeadas naturais (ADR-002):** Suporte completo a `senao se`, `senão se`, `senaose` e `senãose` transpilando para `elif` do Python (com `ouse` mantido por retrocompatibilidade).
- **Resolução semântica segura de 'eh'/'é' (ADR-002):** Traduz para `is` quando comparado a singletons (`nulo`, `verdadeiro`, `falso`) e para `==` quando comparado a literais e variáveis, prevenindo `SyntaxWarning` e armadilhas de identidade de objetos.
- **Operadores compostos de negação e pertinência (ADR-002):** Expressões como `nao eh` (`is not` / `!=`) e `nao em` (`not in`) funcionam naturalmente.
- **Variáveis intuitivas liberadas:** Nomes comuns como `lista = [1, 2, 3]`, `texto = "olá"` ou `tipo = 10` são permitidos livremente e não colidem com palavras reservadas.
- **Preservação de atributos de objetos:** Acessos e atribuições como `objeto.tipo` e `self.tipo = valor` são preservados sem substituição indevida de tokens.
- **Números de linha e apontador visual:** Tracebacks apontam 1:1 para a linha do `.ptpy` original, e erros de compilação exibem o trecho de código com o cursor `^`.
- **Tradução didática de erros:** Cobertura de `SyntaxError`, `IndentationError`, `IndexError`, `NameError`, `ZeroDivisionError`, `TypeError`, `AttributeError`, `ValueError`, entre outros.
- **Detecção antecipada de colisão:** Tentar atribuir a palavras-chave estruturais da sintaxe (`para = 5`, `se = 1`, `senao se = 2`) gera uma explicação amigável antes de disparar erro de sintaxe cru do interpretador.

## Limitações conhecidas (por design)

- **Apenas a gramática inicial e builtins curados são em português.** Bibliotecas externas (`requests`, `pandas`) continuam em inglês por design para servir de rampa de acesso, não de ecossistema isolado.
- **Colisão de palavras estruturais.** `para`, `em`, `e`, `ou`, `com` são reservadas para a gramática, exatamente como `for`/`in`/`and`/`or`/`with` são em inglês.
- **Modo de transição bilíngue.** A exibição lado a lado em tempo real e o exportador limpo para Python canônico estão planejados para a Fase 3.

## Próximos passos sugeridos

1. **Fase 3:** Implementar o modo de transição bilíngue (`--modo-transicao`) e comando de exportação para `.py` canônico (`--exportar`).
2. **Fase 4:** Empacotar com **Pyodide** para execução 100% no navegador sem instalação local.
