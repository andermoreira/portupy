# Passo 2: Estrutura HTML e Design System CSS do Playground

## Contexto mínimo

O executor lê o contrato deste step. Construir a interface visual estática do Playground Web em `web/index.html` e `web/style.css`, aplicando Rich Aesthetics (dark mode, glassmorphism, Google Fonts, layout dividido em dois painéis responsivos).

- Paths: [`web/index.html`], [`web/style.css`]
- Contrato: AC-01, AC-03, AC-05, ADR-004
- Seam: Renderização estática no navegador e responsividade de layout

## Goal

Criar o esqueleto HTML semântico e o design system CSS do Playground Web, contendo header de controle com branding e status, painel do editor de código com numeração de linha e barra de ferramentas, e painel de resultados com abas ("Terminal", "Lado a Lado", "Python Canônico").

## Tarefas

1. Criar `web/index.html`:
   - Header com logo/branding do Transpilador PT, badge visual de status do Pyodide (`Carregando...` / `Pronto`), seletor de exemplos pré-definidos (`ola.ptpy`, `condicionais.ptpy`, `erro.ptpy`) e link para o GitHub do projeto [AC-01] [AC-06].
   - Painel esquerdo (Editor):
     - Barra de ferramentas: Botão principal "Executar ▶" (destaque visual), "Limpar 🗑", contador de linhas e atalho `Ctrl+Enter`.
     - Área de edição: Linhas numeradas sincronizadas com `textarea` acessível e monoespaçado [AC-03].
   - Painel direito (Visualização e Saída):
     - Abas de navegação: "💻 Terminal / Saída", "⇄ Lado a Lado (Bilíngue)", "🐍 Python Canônico" [AC-05].
     - Conteúdo da Aba 1: Terminal virtual estilizado com suporte a mensagens de saída e erros com cursor `^`.
     - Conteúdo da Aba 2: Tabela de visualização comparativa sincronizada com rolagem suave.
     - Conteúdo da Aba 3: Exibição do código canônico puro com botão flutuante "Copiar Código 📋".
     - Barra de rodapé do console com tempo de execução e status.
2. Criar `web/style.css`:
   - Design System completo com tokens CSS customizados (`--bg-primary`, `--bg-surface`, `--accent-color`, etc.).
   - Estética refinada (Dark mode, glassmorphism suave, bordas translúcidas, sombras sutis).
   - Tipografia moderna (Inter para interface, JetBrains Mono / Fira Code para código).
   - Layout responsivo com CSS Grid e Flexbox (duas colunas no desktop, empilhado no mobile).
   - Micro-interações em botões, abas ativas e estados de foco.

## Delta de complexidade planejado

- Abstrações: none
- Dependências: none (utiliza exclusivamente HTML5 e Vanilla CSS nativo)
- Configuração: none
- Extension points: estrutura DOM para scripts em `web/app.js`
- Camadas arquiteturais: camada de apresentação web (`web/`)

## Fora de Escopo

- Lógica de carregamento do Pyodide e execução em JS (Step 3).
- Integração da flag `--web` na CLI (Step 4).

## Critério de Pronto

- `web/index.html` e `web/style.css` são criados e renderizam sem erros de sintaxe.
- A interface é responsiva, apresenta os três painéis e todas as abas de navegação.

## Seam de teste

- Inspeção visual de arquivo e validação estática.

## Dependências

- Step 1 concluído.

## Documentation impact

- Nenhum nesta etapa (consolidado no Step 4).

## Checklist pré-handoff

- [x] ≤ 5 arquivos lógicos afetados no total? (2 arquivos de produção: `web/index.html`, `web/style.css`).
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
Arquivos: @web/index.html @web/style.css
Fora de escopo: Modificar app.js ou transpilador_pt/; bibliotecas externas.
Critério de pronto: web/index.html e web/style.css criados com layout responsivo e design dark moderno.

---

@specs/steps/fase-4-playground-web-pyodide-step-2.md
@specs/fase-4-playground-web-pyodide.md
@adr/004-arquitetura-playground-web-client-side-pyodide.md
```
