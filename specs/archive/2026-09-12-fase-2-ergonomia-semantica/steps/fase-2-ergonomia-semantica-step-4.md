# Passo 4: Exemplo demonstrativo e sincronização documental da Fase 2

## Contexto mínimo

O executor (`/implement-step`) lê o contrato completo deste step.

- Paths: [`transpilador_pt/exemplos/condicionais.ptpy`], [`tests/test_executor.py`], [`README.md`]
- Contrato: AC-01 a AC-07, ADR-002
- Seam: Teste de integração via `unittest` em `tests/test_executor.py` e execução manual/CLI

## Goal

Criar um script de exemplo educativo [transpilador_pt/exemplos/condicionais.ptpy](file:///Users/andersonalves/dev/transpilador-pt/transpilador_pt/exemplos/condicionais.ptpy) demonstrando as construções da Fase 2 (`senao se`, `eh nulo`, `eh valor`, `nao eh`, `nao em`), adicionar teste automatizado para o novo exemplo e atualizar a documentação no [README.md](file:///Users/andersonalves/dev/transpilador-pt/README.md).

## Tarefas

1. Criar `transpilador_pt/exemplos/condicionais.ptpy` contendo:
   - Estrutura com `se ... senao se ... senao:`.
   - Comparação por valor com `eh` (ex.: `nota eh 10`).
   - Verificação de ausência de valor com `eh nulo` (ex.: `usuario eh nulo`).
   - Negação de presença com `nao em` (ex.: `item nao em lista`).
   - Negação de igualdade com `nao eh` (ex.: `status nao eh 'erro'`).
2. Em `tests/test_executor.py`:
   - Adicionar o teste `test_arquivo_exemplo_condicionais` validando que `condicionais.ptpy` executa via `executa_arquivo` retornando status `0` e saída esperada.
3. Em `README.md`:
   - Incluir `condicionais.ptpy` na árvore de arquivos e nas instruções de execução do CLI.
   - Atualizar a seção "O que já funciona" destacando `senao se` (`elif`), operadores compostos `nao eh` e `nao em`, e a segurança semântica de `eh`.
   - Atualizar a lista de próximos passos indicando a conclusão da Fase 2.

## Delta de complexidade planejado

- Abstrações: none
- Dependências: none (stdlib Python)
- Configuração: none
- Extension points: none
- Camadas arquiteturais: none

## Fora de Escopo

- Implementar o modo bilíngue lado a lado da Fase 3.
- Modificar o transpilador léxico ou dicionário (já finalizados nos passos 2 e 3).

## Critério de Pronto

- `python3 cli.py transpilador_pt/exemplos/condicionais.ptpy` executa com sucesso e imprime as saídas esperadas.
- `python3 -m unittest discover -s tests -p "test_*.py"` executa com 100% de aprovação em todos os testes (incluindo o novo exemplo).
- O [README.md](file:///Users/andersonalves/dev/transpilador-pt/README.md) reflete as novas capacidades.

## Seam de teste

- `tests/test_executor.py` via `unittest`.

## Dependências

- Passo 3 (`specs/steps/fase-2-ergonomia-semantica-step-3.md`).

## Documentation impact

- [README.md](file:///Users/andersonalves/dev/transpilador-pt/README.md): atualizar árvore, exemplos de execução e lista de capacidades com os recursos da Fase 2.

## Checklist pré-handoff

- [x] ≤ 5 arquivos lógicos afetados no total? (3 arquivos: `transpilador_pt/exemplos/condicionais.ptpy`, `tests/test_executor.py`, `README.md`).
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
Arquivos: @transpilador_pt/exemplos/condicionais.ptpy @tests/test_executor.py @README.md
Fora de escopo: Alterações de lógica em transpiler.py, dicionario.py ou erros.py.
Critério de pronto: python3 cli.py transpilador_pt/exemplos/condicionais.ptpy executa com sucesso; python3 -m unittest discover -s tests -p "test_*.py" passa 100% verde.

---

@specs/steps/fase-2-ergonomia-semantica-step-4.md
@specs/fase-2-ergonomia-semantica.md
@adr/002-ergonomia-semantica-condicionais-e-operadores-compostos.md
```
