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

  const TEMPO_MAX_EXECUCAO_MS = 10000;
  let pyodideWorker = null;
  let workerReady = false;
  let workerInitPromise = null;
  let pendingExecution = null;
  let abaAtiva = 'terminal';

  function defineSaidaTerminal(classe, texto) {
    const linha = document.createElement('div');
    linha.className = `terminal-line ${classe}`;
    linha.textContent = texto;
    terminalOutput.replaceChildren(linha);
  }

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
    defineSaidaTerminal('terminal-system', '[Editor limpo. Digite ou escolha um exemplo acima.]');
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
      if (workerReady && !btnExecutar.disabled) {
        executaCodigo();
      }
    }
  });

  // --- Inicialização do Worker/Pyodide e Montagem do Módulo ----------------
  function encerraWorker() {
    if (pyodideWorker) {
      pyodideWorker.terminate();
    }
    pyodideWorker = null;
    workerReady = false;
    workerInitPromise = null;
  }

  function inicializaWorker() {
    encerraWorker();

    const worker = new Worker('pyodide-worker.js');
    pyodideWorker = worker;
    let resolveReady;
    let rejectReady;
    workerInitPromise = new Promise((resolve, reject) => {
      resolveReady = resolve;
      rejectReady = reject;
    });

    worker.addEventListener('message', (event) => {
      const mensagem = event.data || {};

      if (mensagem.type === 'ready') {
        workerReady = true;
        resolveReady();
        return;
      }

      if (mensagem.type === 'result' && pendingExecution) {
        const execucao = pendingExecution;
        pendingExecution = null;
        clearTimeout(execucao.timeoutId);
        execucao.resolve(mensagem.resultado);
        return;
      }

      if (mensagem.type === 'error') {
        const erro = new Error(mensagem.message || 'Falha inesperada no Worker Python.');
        if (!workerReady) {
          rejectReady(erro);
        } else if (pendingExecution) {
          const execucao = pendingExecution;
          pendingExecution = null;
          clearTimeout(execucao.timeoutId);
          execucao.reject(erro);
        }
        encerraWorker();
      }
    });

    worker.addEventListener('error', (event) => {
      const erro = new Error(event.message || 'Falha inesperada no Worker Python.');
      if (!workerReady) {
        rejectReady(erro);
      } else if (pendingExecution) {
        const execucao = pendingExecution;
        pendingExecution = null;
        clearTimeout(execucao.timeoutId);
        execucao.reject(erro);
      }
      encerraWorker();
    });

    worker.postMessage({
      type: 'init',
      sources: window.TRANSPILADOR_PT_SOURCES || {}
    });

    return workerInitPromise;
  }

  async function inicializaPyodide({ executarInicial = true } = {}) {
    btnExecutar.disabled = true;
    statusDot.className = 'status-dot status-loading';
    statusText.textContent = 'Baixando Python Wasm...';

    try {
      await inicializaWorker();

      statusText.textContent = 'Montando Transpilador PT...';

      statusDot.className = 'status-dot status-ready';
      statusText.textContent = 'Python Pronto (Wasm)';
      btnExecutar.disabled = false;

      // Executa o exemplo inicial
      if (executarInicial) {
        executaCodigo();
      }

    } catch (err) {
      console.error('Erro ao inicializar Pyodide:', err);
      encerraWorker();
      statusDot.className = 'status-dot status-error';
      statusText.textContent = 'Falha ao carregar Python';
      defineSaidaTerminal(
        'terminal-stderr',
        `⚠️ Não foi possível inicializar o ambiente Python no navegador.\n${err.message}\n\nVerifique sua conexão com a internet para carregar o runtime WebAssembly.`
      );
    }
  }

  // --- Execução de Código --------------------------------------------------
  function solicitaExecucao(codigo) {
    if (!pyodideWorker || !workerReady) {
      return Promise.reject(new Error('O ambiente Python ainda não está pronto.'));
    }

    return new Promise((resolve, reject) => {
      const execucao = { resolve, reject, timeoutId: null };
      execucao.timeoutId = setTimeout(() => {
        if (pendingExecution !== execucao) return;
        pendingExecution = null;
        encerraWorker();
        const erro = new Error(
          `A execução ultrapassou o limite de ${TEMPO_MAX_EXECUCAO_MS / 1000} segundos.`
        );
        erro.name = 'ExecucaoTimeoutError';
        reject(erro);
      }, TEMPO_MAX_EXECUCAO_MS);
      pendingExecution = execucao;
      try {
        pyodideWorker.postMessage({ type: 'execute', codigo });
      } catch (error) {
        pendingExecution = null;
        clearTimeout(execucao.timeoutId);
        reject(error);
      }
    });
  }

  async function executaCodigo() {
    if (!pyodideWorker || !workerReady) return;

    const codigo = editor.value;
    if (!codigo.trim()) {
      defineSaidaTerminal('terminal-system', '[Código vazio. Digite algo no editor.]');
      return;
    }

    btnExecutar.disabled = true;
    outputStatus.textContent = 'Status: Executando...';
    const inicio = performance.now();

    try {
      const jsonStr = await solicitaExecucao(codigo);
      const dados = JSON.parse(jsonStr);

      const duracao = Math.round(performance.now() - inicio);
      executionTime.textContent = `Tempo: ${duracao} ms`;

      // Atualiza Terminal
      terminalOutput.replaceChildren();
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
        defineSaidaTerminal('terminal-success', '✓ Código executado com sucesso (sem saída gerada).');
      }

      // Atualiza Lado a Lado
      bilingueOutput.textContent = dados.lado_a_lado || 'Nenhuma saída comparativa gerada.';

      // Atualiza Canônico
      canonicoOutput.textContent = dados.canonico || '# Nenhum código gerado.';

      outputStatus.textContent = (dados.status === 0) ? 'Status: Sucesso (0)' : 'Status: Erro (1)';

    } catch (err) {
      if (err.name === 'ExecucaoTimeoutError') {
        defineSaidaTerminal(
          'terminal-stderr',
          `⚠️ ${err.message}\nO Worker foi reiniciado; revise laços ou cálculos muito longos antes de executar novamente.`
        );
        outputStatus.textContent = 'Status: Tempo limite excedido';
        executionTime.textContent = 'Tempo: limite excedido';
        inicializaPyodide({ executarInicial: false });
      } else {
        defineSaidaTerminal('terminal-stderr', `⚠️ Erro durante a execução: ${err.message}`);
        outputStatus.textContent = 'Status: Erro';
        if (!workerReady) {
          inicializaPyodide({ executarInicial: false });
        }
      }
    } finally {
      btnExecutar.disabled = !workerReady;
    }
  }

  btnExecutar.addEventListener('click', executaCodigo);

  // Inicializa com o exemplo 1
  editor.value = EXEMPLOS.ola;
  atualizaLinhas();
  atualizaCursorStats();

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('service-worker.js').catch((err) => {
      console.warn('Cache offline indisponível:', err);
    });
  }

  // Inicia o download e setup do Pyodide
  inicializaPyodide();

})();
