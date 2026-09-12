# Spec: Fase 3 — Modo de Transição Bilíngue e Exportador Canônico

## Goal
Fornecer visualização comparativa bilíngue lado a lado e capacidade de exportação para código Python puro e independente, facilitando a transição pedagógica do estudante para o ecossistema Python profissional.

## Non-goals
- Desenvolver interface gráfica web interativa via Pyodide ou servidor HTTP (escopo da Fase 4).
- Criar empacotador de binários executáveis (.exe ou instaladores).
- Implementar suporte a temas customizados complexos ou formatação Rich/Curses com dependências externas pesadas (a renderização de terminal deve usar stdlib).

## User stories
- **Story 1 (Caminho feliz - visualização lado a lado):**
  - **Given** um arquivo `.ptpy` escrito por um estudante,
  - **When** ele executar com a flag `--lado-a-lado` ou `--modo-transicao`,
  - **Then** o terminal deve exibir duas colunas sincronizadas (Português à esquerda, Python Canônico à direita) com números de linha correspondentes.
- **Story 2 (Caminho feliz - exportação para arquivo .py):**
  - **Given** um código em português pronto para ser compartilhado ou submetido,
  - **When** o estudante executar `python3 cli.py script.ptpy --exportar script.py`,
  - **Then** um arquivo Python canônico independente deve ser gerado, onde funções como `mostre` viram `print`, `tamanho` vira `len`, etc., capaz de rodar diretamente com `python3 script.py` sem o transpilador instalado.
- **Story 3 (Caminho feliz - exportação para stdout):**
  - **Given** um estudante ou ferramenta externa utilizando pipelines de shell,
  - **When** executar `python3 cli.py script.ptpy --exportar` (sem informar arquivo de destino),
  - **Then** o Python canônico gerado deve ser impresso no stdout.
- **Story 4 (Caminho de erro - destino inválido):**
  - **Given** uma tentativa de exportação para um caminho inacessível ou sem permissão de escrita,
  - **When** a CLI tentar salvar o arquivo,
  - **Then** deve retornar código de saída `1` com mensagem clara em português sem despejar traceback cru.

## Assumptions
- A stdlib do Python possui recursos suficientes para manipulação de strings, larguras de terminal (`shutil.get_terminal_size`) e I/O de arquivos sem dependências externas [ADR-003].
- O código canônico gerado deve ser compatível com interpretadores Python 3 padrão (PEP 8) [ADR-003].

## Risks
- **Terminais estreitos ou redimensionados:** Terminais com menos de 80 colunas podem quebrar a exibição lado a lado.
  - *Mitigação:* Ajustar dinamicamente a largura das colunas com base em `shutil.get_terminal_size()` ou degradar para exibição empilhada/truncada segura com aviso se o terminal for menor que 60 colunas.
- **Divergência entre código de execução e código exportado:**
  - *Mitigação:* `transpila_canonico` reutiliza as mesmas regras centrais de `transpila`, adicionando apenas o mapeamento formal de builtins para nomes nativos em escopos não-atribuídos.

## Error handling
- Falhas de gravação em disco ao exportar são capturadas e formatadas como `⚠️ Não consegui salvar o arquivo exportado: <motivo>`.
- Arquivos de entrada inexistentes ou com erro de sintaxe são reportados antes de iniciar a renderização lado a lado.

## Observability
- Mensagens de sucesso com o caminho do arquivo gerado ao utilizar `--exportar`.
- Preservação dos códigos de retorno padrão (`0` para sucesso, `1` para erros com saída em stderr).

## Threat model
- **I/O de arquivos:** O comando `--exportar` escreve no caminho especificado pelo usuário com as mesmas permissões do usuário do sistema operacional.

## Acceptance criteria
- **AC-01:** A função `transpila_canonico` gera Python puro, traduzindo palavras estruturais e builtins (`mostre` -> `print`, `tamanho` -> `len`, `leia` -> `input`, `intervalo` -> `range`, etc.) [pedido] [ADR-003]
- **AC-02:** Chamadas a atributos precedidos por ponto (ex.: `self.tamanho` ou `carro.tipo`) NÃO são alteradas na exportação canônica [código: transpilador_pt/transpiler.py:70]
- **AC-03:** O script Python exportado executa diretamente via `python3` de forma idêntica e sem depender do pacote `transpilador_pt` [ADR-003]
- **AC-04:** A função `renderiza_lado_a_lado` gera uma tabela formatada no terminal com duas colunas identificadas, separador vertical e números de linha [pedido] [ADR-003]
- **AC-05:** A CLI suporta `--lado-a-lado` (e alias `--modo-transicao`), exibindo a comparação antes de executar o script [pedido] [ADR-003]
- **AC-06:** A CLI suporta `--exportar [caminho.py]`, gravando o código canônico no destino ou exibindo no stdout se nenhum arquivo for passado [pedido] [ADR-003]
- **AC-07:** Uma suíte de testes automatizados cobre `transpila_canonico`, `renderiza_lado_a_lado` e os argumentos de linha de comando da CLI [derivado]
- **AC-08:** O [README.md](file:///Users/andersonalves/dev/transpilador-pt/README.md) documenta o uso das flags `--lado-a-lado` e `--exportar` com exemplos práticos [código: README.md:25]

## Open questions
- Nenhuma questão bloqueadora para a execução da Fase 3.

## Implementation plan
1. Criar suíte de testes automatizados para `transpila_canonico`, `renderiza_lado_a_lado` e novas opções da CLI [AC-07]
2. Implementar `transpila_canonico` em `transpilador_pt/transpiler.py` suportando tradução pura de builtins e gramática [AC-01] [AC-02] [AC-03]
3. Implementar módulo `transpilador_pt/transicao.py` com `renderiza_lado_a_lado` e formatação responsiva de colunas [AC-04]
4. Integrar flags `--lado-a-lado` e `--exportar` em `cli.py` e sincronizar documentação no `README.md` [AC-05] [AC-06] [AC-08]

## Documentation impact
- [README.md](file:///Users/andersonalves/dev/transpilador-pt/README.md): Adicionar instruções e exemplos de `--lado-a-lado` e `--exportar`, e atualizar o status do roadmap para Fase 3 concluída (Step 4).
