/**
 * Transpilador PT — Motor da Aplicação Web (Pyodide WebAssembly)
 */

(function () {
  'use strict';

  // --- Catálogo de Exemplos Didáticos --------------------------------------
  const EXEMPLOS = {
    ola: `# Exemplo 1: Olá Mundo e f-strings com funções embutidas
funcao saudacao(nome):
    se nome eh nulo:
        retorne "sem nome"
    senao:
        retorne "Ola, " + nome

nomes = ["Ana", "Bruno", "Carla"]
para nome em nomes:
    mostre(saudacao(nome))

mostre(f"Total de nomes: {tamanho(nomes)}")
`,

    condicionais: `# Exemplo 2: Condicionais encadeadas e resolução semântica
funcao classificar_nota(nota):
    se nota eh nulo:
        retorne "Nota ausente"
    senao se nota eh 10:
        retorne "Excelente (gabaritou!)"
    senao se nota >= 7:
        retorne "Aprovado"
    senao:
        retorne "Em recuperacao"

notas = [10, 8.5, 4.0, nulo]
para valor em notas:
    mostre(f"Nota: {valor} -> {classificar_nota(valor)}")

# Operadores de pertinência e negação
bloqueados = ["Bruno", "Carlos"]
aluno = "Ana"

se aluno nao em bloqueados:
    mostre(f"Acesso liberado para: {aluno}")

se aluno nao eh "Bruno":
    mostre("Confirmado: aluno nao eh o Bruno")
`,

    erro: `# Exemplo 3: Diagnóstico didático de erro com apontador visual
# Tente executar e veja como o erro aponta exatamente onde está o problema!

x = 10
se x > 5
    mostre("x eh maior que cinco")
`,

    loop: `# Exemplo 4: Laço 'para', listas e dicionários
frutas = ["Maca", "Banana", "Laranja", "Uva"]

mostre("--- Lista de Frutas ---")
para item em frutas:
    mostre(f"- Fruta: {item} (letras: {tamanho(item)})")

precos = {
    "Maca": 3.50,
    "Banana": 2.20,
    "Laranja": 4.00,
}

mostre("")
mostre(f"Preco da Maca: R$ {precos['Maca']:.2f}")
`,

    funcoes: `# Exemplo 5: Funções matemáticas e builtins curados
funcao potencia(base, expoente=2):
    retorne base ** expoente

valores = [1, 2, 3, 4, 5]
quadrados = []

para n em valores:
    quadrados.append(potencia(n))

mostre(f"Original: {valores}")
mostre(f"Quadrados: {quadrados}")
mostre(f"Soma total: {some(quadrados)}")
mostre(f"Maior valor: {maximo(quadrados)}")
mostre(f"Menor valor: {minimo(quadrados)}")
`
  };

  // --- Elementos do DOM ----------------------------------------------------
  const editor = document.getElementById('code-editor');
  const lineNumbers = document.getElementById('line-numbers');
  const editorStats = document.getElementById('editor-stats');
  const selectExemplo = document.getElementById('select-exemplo');
  const btnExecutar = document.getElementById('btn-executar');
  const btnLimpar = document.getElementById('btn-limpar');
  const btnCopiar = document.getElementById('btn-copiar-saida');
  
  const statusDot = document.getElementById('status-dot');
  const statusText = document.getElementById('status-text');
  const outputStatus = document.getElementById('output-status');
  const executionTime = document.getElementById('execution-time');

  const tabBtnTerminal = document.getElementById('tab-btn-terminal');
  const tabBtnBilingue = document.getElementById('tab-btn-bilingue');
  const tabBtnCanonico = document.getElementById('tab-btn-canonico');

  const tabTerminal = document.getElementById('tab-terminal');
  const tabBilingue = document.getElementById('tab-bilingue');
  const tabCanonico = document.getElementById('tab-canonico');

  const terminalOutput = document.getElementById('terminal-output');
  const bilingueOutput = document.getElementById('bilingue-output');
  const canonicoOutput = document.getElementById('canonico-output');

  let pyodideInstance = null;
  let abaAtiva = 'terminal';

  // --- Sincronização e Linhas do Editor ------------------------------------
  function atualizaLinhas() {
    const linhas = editor.value.split('\n').length;
    const numeros = Array.from({ length: linhas }, (_, i) => i + 1).join('\n');
    lineNumbers.textContent = numeros;
  }

  function atualizaCursorStats() {
    const pos = editor.selectionStart;
    const linhasAteCursor = editor.value.substring(0, pos).split('\n');
    const linha = linhasAteCursor.length;
    const coluna = linhasAteCursor[linhasAteCursor.length - 1].length + 1;
    editorStats.textContent = `Linha ${linha}, Coluna ${coluna}`;
  }

  editor.addEventListener('input', () => {
    atualizaLinhas();
    atualizaCursorStats();
  });

  editor.addEventListener('click', atualizaCursorStats);
  editor.addEventListener('keyup', atualizaCursorStats);

  editor.addEventListener('scroll', () => {
    lineNumbers.scrollTop = editor.scrollTop;
  });

  // Trata tecla Tab (insere 4 espaços)
  editor.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = editor.selectionStart;
      const end = editor.selectionEnd;
      editor.value = editor.value.substring(0, start) + '    ' + editor.value.substring(end);
      editor.selectionStart = editor.selectionEnd = start + 4;
      atualizaLinhas();
      atualizaCursorStats();
    } else if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      if (!btnExecutar.disabled) {
        executaCodigo();
      }
    }
  });

  // --- Alternância de Abas -------------------------------------------------
  function ativaAba(nomeAba) {
    abaAtiva = nomeAba;
    
    // Atualiza botões
    tabBtnTerminal.classList.toggle('active', nomeAba === 'terminal');
    tabBtnBilingue.classList.toggle('active', nomeAba === 'bilingue');
    tabBtnCanonico.classList.toggle('active', nomeAba === 'canonico');

    tabBtnTerminal.setAttribute('aria-selected', nomeAba === 'terminal');
    tabBtnBilingue.setAttribute('aria-selected', nomeAba === 'bilingue');
    tabBtnCanonico.setAttribute('aria-selected', nomeAba === 'canonico');

    // Atualiza painéis
    tabTerminal.hidden = (nomeAba !== 'terminal');
    tabBilingue.hidden = (nomeAba !== 'bilingue');
    tabCanonico.hidden = (nomeAba !== 'canonico');

    tabTerminal.classList.toggle('active', nomeAba === 'terminal');
    tabBilingue.classList.toggle('active', nomeAba === 'bilingue');
    tabCanonico.classList.toggle('active', nomeAba === 'canonico');
  }

  tabBtnTerminal.addEventListener('click', () => ativaAba('terminal'));
  tabBtnBilingue.addEventListener('click', () => ativaAba('bilingue'));
  tabBtnCanonico.addEventListener('click', () => ativaAba('canonico'));

  // Botão Copiar Conteúdo
  btnCopiar.addEventListener('click', async () => {
    let texto = '';
    if (abaAtiva === 'terminal') {
      texto = terminalOutput.innerText;
    } else if (abaAtiva === 'bilingue') {
      texto = bilingueOutput.textContent;
    } else if (abaAtiva === 'canonico') {
      texto = canonicoOutput.textContent;
    }

    if (texto) {
      try {
        await navigator.clipboard.writeText(texto);
        const originalText = btnCopiar.innerHTML;
        btnCopiar.innerHTML = '<span>✓ Copiado!</span>';
        setTimeout(() => {
          btnCopiar.innerHTML = originalText;
        }, 2000);
      } catch (err) {
        console.error('Falha ao copiar:', err);
      }
    }
  });

  // Botão Limpar
  btnLimpar.addEventListener('click', () => {
    editor.value = '';
    atualizaLinhas();
    atualizaCursorStats();
    terminalOutput.innerHTML = '<div class="terminal-line terminal-system">[Editor limpo. Digite ou escolha um exemplo acima.]</div>';
    bilingueOutput.textContent = 'Execute o código para visualizar a comparação lado a lado.';
    canonicoOutput.textContent = '# O código Python puro canônico aparecerá aqui após a transpilação.';
    outputStatus.textContent = 'Status: Pronto';
    executionTime.textContent = 'Tempo: -- ms';
  });

  // Seletor de Exemplos
  selectExemplo.addEventListener('change', () => {
    const chave = selectExemplo.value;
    if (EXEMPLOS[chave]) {
      editor.value = EXEMPLOS[chave];
      atualizaLinhas();
      atualizaCursorStats();
      if (pyodideInstance && !btnExecutar.disabled) {
        executaCodigo();
      }
    }
  });

  // --- Inicialização do Pyodide e Montagem do Módulo -----------------------
  async function inicializaPyodide() {
    btnExecutar.disabled = true;
    statusDot.className = 'status-dot status-loading';
    statusText.textContent = 'Baixando Python Wasm...';

    try {
      if (typeof loadPyodide !== 'function') {
        throw new Error('A biblioteca Pyodide não foi carregada pelo navegador.');
      }

      pyodideInstance = await loadPyodide();

      statusText.textContent = 'Montando Transpilador PT...';

      // Cria a pasta do módulo no filesystem virtual
      pyodideInstance.FS.mkdirTree('/home/pyodide/transpilador_pt');

      // Grava os fontes se estiverem disponíveis no bundle
      if (window.TRANSPILADOR_PT_SOURCES) {
        for (const [filename, content] of Object.entries(window.TRANSPILADOR_PT_SOURCES)) {
          pyodideInstance.FS.writeFile(`/home/pyodide/transpilador_pt/${filename}`, content);
        }
      }

      // Adiciona ao sys.path e importa o pacote
      await pyodideInstance.runPythonAsync(`
import sys
if '/home/pyodide' not in sys.path:
    sys.path.insert(0, '/home/pyodide')

import json
import transpilador_pt

def _processa_codigo_web(codigo_pt):
    resultado = {
        "status": 0,
        "stdout": "",
        "stderr": "",
        "canonico": "",
        "lado_a_lado": ""
    }
    
    # 1. Transpilação canônica
    try:
        canonico = transpilador_pt.transpila_canonico(codigo_pt)
        resultado["canonico"] = canonico
    except Exception as exc:
        resultado["canonico"] = f"# Erro ao gerar Python canonico: {exc}"

    # 2. Renderização lado a lado
    try:
        resultado["lado_a_lado"] = transpilador_pt.renderiza_lado_a_lado(
            codigo_pt, 
            resultado["canonico"], 
            largura_terminal=80
        )
    except Exception as exc:
        resultado["lado_a_lado"] = f"Erro na visualizacao lado a lado: {exc}"

    # 3. Execução in-process com captura de stdout/stderr
    import io, contextlib
    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()

    with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
        try:
            status_code = transpilador_pt.executa_codigo(codigo_pt)
            resultado["status"] = status_code
        except Exception as exc:
            resultado["status"] = 1
            stderr_buf.write(f"Excecao inesperada: {exc}\\n")

    resultado["stdout"] = stdout_buf.getvalue()
    resultado["stderr"] = stderr_buf.getvalue()
    return json.dumps(resultado)
`);

      statusDot.className = 'status-dot status-ready';
      statusText.textContent = 'Python Pronto (Wasm)';
      btnExecutar.disabled = false;

      // Executa o exemplo inicial
      executaCodigo();

    } catch (err) {
      console.error('Erro ao inicializar Pyodide:', err);
      statusDot.className = 'status-dot status-error';
      statusText.textContent = 'Falha ao carregar Python';
      terminalOutput.innerHTML = `
        <div class="terminal-line terminal-stderr">
          ⚠️ Não foi possível inicializar o ambiente Python no navegador:
          <br>${err.message}
          <br><br>Verifique sua conexão com a internet para carregar o runtime WebAssembly.
        </div>
      `;
    }
  }

  // --- Execução de Código --------------------------------------------------
  async function executaCodigo() {
    if (!pyodideInstance) return;

    const codigo = editor.value;
    if (!codigo.trim()) {
      terminalOutput.innerHTML = '<div class="terminal-line terminal-system">[Código vazio. Digite algo no editor.]</div>';
      return;
    }

    btnExecutar.disabled = true;
    outputStatus.textContent = 'Status: Executando...';
    const inicio = performance.now();

    try {
      pyodideInstance.globals.set('_codigo_aluno', codigo);
      const jsonStr = await pyodideInstance.runPythonAsync('_processa_codigo_web(_codigo_aluno)');
      const dados = JSON.parse(jsonStr);

      const duracao = Math.round(performance.now() - inicio);
      executionTime.textContent = `Tempo: ${duracao} ms`;

      // Atualiza Terminal
      terminalOutput.innerHTML = '';
      if (dados.stdout) {
        const divOut = document.createElement('div');
        divOut.className = 'terminal-line terminal-stdout';
        divOut.textContent = dados.stdout;
        terminalOutput.appendChild(divOut);
      }

      if (dados.stderr) {
        const divErr = document.createElement('div');
        divErr.className = 'terminal-line terminal-stderr';
        divErr.textContent = dados.stderr;
        terminalOutput.appendChild(divErr);
      }

      if (!dados.stdout && !dados.stderr) {
        terminalOutput.innerHTML = '<div class="terminal-line terminal-success">✓ Código executado com sucesso (sem saída gerada).</div>';
      }

      // Atualiza Lado a Lado
      bilingueOutput.textContent = dados.lado_a_lado || 'Nenhuma saída comparativa gerada.';

      // Atualiza Canônico
      canonicoOutput.textContent = dados.canonico || '# Nenhum código gerado.';

      outputStatus.textContent = (dados.status === 0) ? 'Status: Sucesso (0)' : 'Status: Erro (1)';

    } catch (err) {
      terminalOutput.innerHTML = `<div class="terminal-line terminal-stderr">⚠️ Erro durante a execução: ${err.message}</div>`;
      outputStatus.textContent = 'Status: Erro';
    } finally {
      btnExecutar.disabled = false;
    }
  }

  btnExecutar.addEventListener('click', executaCodigo);

  // Inicializa com o exemplo 1
  editor.value = EXEMPLOS.ola;
  atualizaLinhas();
  atualizaCursorStats();

  // Inicia o download e setup do Pyodide
  inicializaPyodide();

})();
