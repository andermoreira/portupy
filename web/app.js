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
  const btnTentarNovamente = document.getElementById('btn-tentar-novamente');
  
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
  const editorCodeArea = document.getElementById('editor-code-area');
  const syntaxHighlight = document.getElementById('syntax-highlight');
  const syntaxHighlightCode = document.getElementById('syntax-highlight-code');

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

  const PALAVRAS_CHAVE_DESTAQUE = new Set([
    'se', 'senao', 'senão', 'senaose', 'senãose', 'ouse', 'para',
    'enquanto', 'funcao', 'função', 'retorne', 'classe', 'importe',
    'de', 'como', 'com', 'tente', 'exceto', 'finalmente', 'levante',
    'quebre', 'continue', 'passe', 'em', 'nao', 'não', 'e', 'ou',
    'lambda', 'global', 'assincrono', 'aguarde', 'produza', 'del',
    'assert', 'def', 'if', 'else', 'elif', 'for', 'while', 'return',
    'class', 'import', 'from', 'as', 'with', 'try', 'except', 'finally',
    'raise', 'break', 'yield', 'async', 'await'
  ]);
  const BUILTINS_DESTAQUE = new Set([
    'mostre', 'leia', 'tamanho', 'intervalo', 'some', 'maximo', 'minimo',
    'abs', 'arredonde', 'lista', 'dicionario', 'dicionário', 'conjunto',
    'tupla', 'texto', 'inteiro', 'decimal', 'booleano', 'print', 'input',
    'len', 'range', 'sum', 'max', 'min', 'dict', 'set', 'tuple', 'str',
    'int', 'float', 'bool', 'enumerate', 'zip', 'sorted'
  ]);
  const BOOLEANOS_DESTAQUE = new Set([
    'verdadeiro', 'falso', 'nulo', 'True', 'False', 'None'
  ]);

  function escapaHtml(texto) {
    return texto.replace(/[&<>"']/g, (caractere) => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    }[caractere]));
  }

  function marcaToken(classe, token) {
    return `<span class="syntax-${classe}">${escapaHtml(token)}</span>`;
  }

  function encontraFimString(codigo, inicioAspas) {
    const delimitador = codigo.startsWith('"""', inicioAspas)
      ? '"""'
      : codigo.startsWith("'''", inicioAspas) ? "'''" : codigo[inicioAspas];
    let indice = inicioAspas + delimitador.length;

    while (indice < codigo.length) {
      if (codigo[indice] === '\\') {
        indice += 2;
      } else if (codigo.startsWith(delimitador, indice)) {
        return indice + delimitador.length;
      } else {
        indice += 1;
      }
    }
    return codigo.length;
  }

  function atualizaSyntaxHighlight() {
    const codigo = editor.value;
    let html = '';
    let indice = 0;

    while (indice < codigo.length) {
      const trecho = codigo.slice(indice);
      const prefixoString = trecho.match(/^(?:[fFrRbBuU]{1,2})(?:"""|'''|"|')/);
      const aspasDiretas = trecho.match(/^(?:"""|'''|"|')/);

      if (prefixoString || aspasDiretas) {
        const abertura = prefixoString ? prefixoString[0] : aspasDiretas[0];
        const deslocamentoAspas = prefixoString ? abertura.search(/["']/) : 0;
        const fim = encontraFimString(codigo, indice + deslocamentoAspas);
        html += marcaToken('string', codigo.slice(indice, fim));
        indice = fim;
        continue;
      }

      if (codigo[indice] === '#') {
        const fimLinha = codigo.indexOf('\n', indice);
        const fim = fimLinha === -1 ? codigo.length : fimLinha;
        html += marcaToken('comment', codigo.slice(indice, fim));
        indice = fim;
        continue;
      }

      const numero = trecho.match(/^(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?/);
      if (numero) {
        html += marcaToken('number', numero[0]);
        indice += numero[0].length;
        continue;
      }

      const identificador = trecho.match(/^[A-Za-zÀ-ÿ_][A-Za-z0-9À-ÿ_]*/);
      if (identificador) {
        const token = identificador[0];
        const depois = codigo.slice(indice + token.length);
        let classe = '';
        if (BOOLEANOS_DESTAQUE.has(token)) {
          classe = 'boolean';
        } else if (PALAVRAS_CHAVE_DESTAQUE.has(token)) {
          classe = 'keyword';
        } else if (BUILTINS_DESTAQUE.has(token)) {
          classe = 'builtin';
        } else if (/^\s*\(/.test(depois)) {
          classe = 'function';
        }
        html += classe ? marcaToken(classe, token) : escapaHtml(token);
        indice += token.length;
        continue;
      }

      const operador = trecho.match(/^(?:==|!=|<=|>=|\*\*|\/\/|->|:=|[+\-*/%<>=])/);
      if (operador) {
        html += marcaToken('operator', operador[0]);
        indice += operador[0].length;
        continue;
      }

      if (/^[()[\]{},.:;]/.test(trecho)) {
        html += marcaToken('punctuation', codigo[indice]);
        indice += 1;
        continue;
      }

      html += escapaHtml(codigo[indice]);
      indice += 1;
    }

    syntaxHighlightCode.innerHTML = html;
  }

  editorCodeArea.classList.add('syntax-highlight-enabled');

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
    atualizaSyntaxHighlight();
  });

  editor.addEventListener('click', atualizaCursorStats);
  editor.addEventListener('keyup', atualizaCursorStats);

  editor.addEventListener('scroll', () => {
    lineNumbers.scrollTop = editor.scrollTop;
    syntaxHighlight.scrollTop = editor.scrollTop;
    syntaxHighlight.scrollLeft = editor.scrollLeft;
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
      atualizaSyntaxHighlight();
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
    tabBtnTerminal.tabIndex = nomeAba === 'terminal' ? 0 : -1;
    tabBtnBilingue.tabIndex = nomeAba === 'bilingue' ? 0 : -1;
    tabBtnCanonico.tabIndex = nomeAba === 'canonico' ? 0 : -1;

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

  const botoesAbas = [tabBtnTerminal, tabBtnBilingue, tabBtnCanonico];
  botoesAbas.forEach((botao, indice) => {
    botao.addEventListener('keydown', (event) => {
      if (!['ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp', 'Home', 'End'].includes(event.key)) {
        return;
      }
      event.preventDefault();
      let proximoIndice;
      if (event.key === 'Home') {
        proximoIndice = 0;
      } else if (event.key === 'End') {
        proximoIndice = botoesAbas.length - 1;
      } else {
        const deslocamento = ['ArrowRight', 'ArrowDown'].includes(event.key) ? 1 : -1;
        proximoIndice = (indice + deslocamento + botoesAbas.length) % botoesAbas.length;
      }
      botoesAbas[proximoIndice].focus();
      botoesAbas[proximoIndice].click();
    });
  });

  async function copiaTexto(texto) {
    if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
      await navigator.clipboard.writeText(texto);
      return;
    }

    const areaTransferencia = document.createElement('textarea');
    areaTransferencia.value = texto;
    areaTransferencia.setAttribute('readonly', '');
    areaTransferencia.style.position = 'fixed';
    areaTransferencia.style.opacity = '0';
    document.body.appendChild(areaTransferencia);
    areaTransferencia.select();
    const copiado = document.execCommand('copy');
    areaTransferencia.remove();
    if (!copiado) {
      throw new Error('O navegador recusou o acesso à área de transferência.');
    }
  }

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
        await copiaTexto(texto);
        const originalText = btnCopiar.innerHTML;
        btnCopiar.innerHTML = '<span>✓ Copiado!</span>';
        setTimeout(() => {
          btnCopiar.innerHTML = originalText;
        }, 2000);
      } catch (err) {
        console.error('Falha ao copiar:', err);
        outputStatus.textContent = 'Status: Não foi possível copiar';
      }
    }
  });

  // Botão Limpar
  btnLimpar.addEventListener('click', () => {
    editor.value = '';
    atualizaLinhas();
    atualizaCursorStats();
    atualizaSyntaxHighlight();
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
      atualizaSyntaxHighlight();
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
    btnTentarNovamente.hidden = true;
    statusDot.className = 'status-dot status-loading';
    statusText.textContent = 'Baixando Python Wasm...';

    try {
      await inicializaWorker();

      statusText.textContent = 'Montando Transpilador PT...';

      statusDot.className = 'status-dot status-ready';
      statusText.textContent = 'Python Pronto (Wasm)';
      btnExecutar.disabled = false;
      btnTentarNovamente.hidden = true;

      // Executa o exemplo inicial
      if (executarInicial) {
        executaCodigo();
      }

    } catch (err) {
      console.error('Erro ao inicializar Pyodide:', err);
      encerraWorker();
      statusDot.className = 'status-dot status-error';
      statusText.textContent = 'Falha ao carregar Python';
      btnTentarNovamente.hidden = false;
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
  btnTentarNovamente.addEventListener('click', () => inicializaPyodide());

  // Inicializa com o exemplo 1
  editor.value = EXEMPLOS.ola;
  atualizaLinhas();
  atualizaCursorStats();
  atualizaSyntaxHighlight();

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('service-worker.js').catch((err) => {
      console.warn('Cache offline indisponível:', err);
    });
  }

  // Inicia o download e setup do Pyodide
  inicializaPyodide();

})();
