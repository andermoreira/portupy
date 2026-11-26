/**
 * Transpilador PT — Motor da Aplicação Web (Pyodide WebAssembly)
 */

(function () {
  'use strict';

  // --- Catálogo de Exemplos Didáticos --------------------------------------
  // O bundle é a fonte única compartilhada pela CLI e pelo playground.
  const EXEMPLOS = window.PORTUPY_EXEMPLOS || {};

  // --- Elementos do DOM ----------------------------------------------------
  const editor = document.getElementById('code-editor');
  const lineNumbers = document.getElementById('line-numbers');
  const editorStats = document.getElementById('editor-stats');
  const selectExemplo = document.getElementById('select-exemplo');
  const btnExecutar = document.getElementById('btn-executar');
  const btnLimpar = document.getElementById('btn-limpar');
  const btnRestaurarRascunho = document.getElementById('btn-restaurar-rascunho');
  const btnBaixarPython = document.getElementById('btn-baixar-python');
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
  let pythonExportavel = '';
  let btnLinhaErro = null;

  function defineSaidaTerminal(classe, texto) {
    const linha = document.createElement('div');
    linha.className = `terminal-line ${classe}`;
    linha.textContent = texto;
    terminalOutput.replaceChildren(linha);
  }

  // Os grupos de realce vêm do bundle, derivados da fonte única em
  // portupy/dicionario.py, evitando listas paralelas mantidas à mão.
  // O fallback cobre apenas o caso do bundle não expor os grupos (ex.: bundle
  // antigo em cache), preservando um realce mínimo funcional.
  const DESTAQUE = window.PORTUPY_DESTAQUE || {};
  const PALAVRAS_CHAVE_DESTAQUE = new Set(DESTAQUE.palavrasChave || [
    'se', 'senao', 'senão', 'senaose', 'senãose', 'ouse', 'para',
    'enquanto', 'funcao', 'função', 'retorne', 'classe', 'importe',
    'de', 'como', 'com', 'tente', 'exceto', 'finalmente', 'levante',
    'quebre', 'continue', 'passe', 'em', 'nao', 'não', 'e', 'ou',
    'lambda', 'global', 'assincrono', 'aguarde', 'produza', 'del',
    'assert', 'def', 'if', 'else', 'elif', 'for', 'while', 'return',
    'class', 'import', 'from', 'as', 'with', 'try', 'except', 'finally',
    'raise', 'break', 'yield', 'async', 'await'
  ]);
  const BUILTINS_DESTAQUE = new Set(DESTAQUE.builtins || [
    'mostre', 'leia', 'tamanho', 'intervalo', 'some', 'maximo', 'minimo',
    'abs', 'arredonde', 'lista', 'dicionario', 'dicionário', 'conjunto',
    'tupla', 'texto', 'inteiro', 'decimal', 'booleano', 'print', 'input',
    'len', 'range', 'sum', 'max', 'min', 'dict', 'set', 'tuple', 'str',
    'int', 'float', 'bool', 'enumerate', 'zip', 'sorted'
  ]);
  const BOOLEANOS_DESTAQUE = new Set(DESTAQUE.booleanos || [
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

  function geraHtmlDestaque(codigo) {
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

    return html;
  }

  function atualizaSyntaxHighlight() {
    syntaxHighlightCode.innerHTML = geraHtmlDestaque(editor.value);
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

  // Rascunho local: evita perder o código ao recarregar a página. O acesso ao
  // localStorage pode falhar (modo privado, bloqueio de cookies), então é opcional.
  const CHAVE_RASCUNHO = 'portupy:rascunho';

  function leRascunho() {
    try {
      return window.localStorage.getItem(CHAVE_RASCUNHO);
    } catch (error) {
      return null;
    }
  }

  let rascunho = leRascunho();

  function salvaRascunho() {
    rascunho = editor.value;
    try {
      window.localStorage.setItem(CHAVE_RASCUNHO, rascunho);
    } catch (error) {
      // Sem armazenamento disponível: o editor segue funcionando normalmente.
    }
  }

  function aposEdicao({ salvar = true } = {}) {
    atualizaLinhas();
    atualizaCursorStats();
    atualizaSyntaxHighlight();
    if (salvar) {
      salvaRascunho();
      selectExemplo.value = '';
    }
    btnRestaurarRascunho.hidden = rascunho === null || editor.value === rascunho;
    if (pythonExportavel || btnLinhaErro) {
      outputStatus.textContent = 'Código alterado. Execute novamente.';
    }
    invalidaAcoesDaSaida();
  }

  function invalidaAcoesDaSaida() {
    pythonExportavel = '';
    btnBaixarPython.disabled = true;
    btnLinhaErro?.remove();
    btnLinhaErro = null;
  }

  btnRestaurarRascunho.addEventListener('click', () => {
    editor.value = rascunho;
    aposEdicao();
    editor.focus();
    if (workerReady && !btnExecutar.disabled) {
      executaCodigo();
    }
  });

  editor.addEventListener('input', aposEdicao);

  editor.addEventListener('click', atualizaCursorStats);
  editor.addEventListener('keyup', atualizaCursorStats);

  editor.addEventListener('scroll', () => {
    lineNumbers.scrollTop = editor.scrollTop;
    syntaxHighlight.scrollTop = editor.scrollTop;
    syntaxHighlight.scrollLeft = editor.scrollLeft;
  });

  const RECUO = '    ';

  // Substitui o trecho [inicio, fim) preservando o histórico de desfazer
  // (Ctrl+Z) quando o navegador suporta insertText.
  function substituiTrecho(inicio, fim, texto) {
    editor.focus();
    editor.setSelectionRange(inicio, fim);
    let inserido = false;
    try {
      inserido = document.execCommand('insertText', false, texto);
    } catch (error) {
      inserido = false;
    }
    if (!inserido) {
      editor.setRangeText(texto, inicio, fim, 'end');
      aposEdicao();
    }
  }

  function inicioDaLinha(posicao) {
    if (posicao === 0) return 0;
    return editor.value.lastIndexOf('\n', posicao - 1) + 1;
  }

  function removeRecuo() {
    const inicio = inicioDaLinha(editor.selectionStart);
    const espacos = editor.value.slice(inicio).match(/^ {1,4}/);
    if (!espacos) return;
    const cursor = editor.selectionStart;
    substituiTrecho(inicio, inicio + espacos[0].length, '');
    const novaPosicao = Math.max(inicio, cursor - espacos[0].length);
    editor.setSelectionRange(novaPosicao, novaPosicao);
  }

  function quebraLinhaComRecuo() {
    const inicio = inicioDaLinha(editor.selectionStart);
    const linhaAteCursor = editor.value.slice(inicio, editor.selectionStart);
    let recuo = linhaAteCursor.match(/^[ \t]*/)[0];
    // Após o cabeçalho de um bloco (se ...:, para ...:) o corpo vai um nível à direita.
    if (!/^\s*#/.test(linhaAteCursor) && /:\s*(#.*)?$/.test(linhaAteCursor)) {
      recuo += RECUO;
    }
    substituiTrecho(editor.selectionStart, editor.selectionEnd, '\n' + recuo);
  }

  // Tab recua; Esc libera o próximo Tab para mover o foco para fora do editor,
  // para quem navega só pelo teclado não ficar preso na área de código.
  let tabLiberado = false;

  editor.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      tabLiberado = true;
      return;
    }
    if (e.key === 'Tab' && tabLiberado) {
      tabLiberado = false;
      return;
    }
    tabLiberado = false;

    if (e.key === 'Tab') {
      e.preventDefault();
      if (e.shiftKey) {
        removeRecuo();
      } else {
        substituiTrecho(editor.selectionStart, editor.selectionEnd, RECUO);
      }
    } else if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      if (!btnExecutar.disabled) {
        executaCodigo();
      }
    } else if (e.key === 'Enter' && !e.shiftKey && !e.altKey && !e.isComposing) {
      e.preventDefault();
      quebraLinhaComRecuo();
    }
  });

  editor.addEventListener('blur', () => {
    tabLiberado = false;
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
      // Cada linha do terminal é um <div> irmão (ex.: stdout e stderr).
      // Juntar por '\n' preserva a separação entre blocos sem depender de
      // innerText (que varia com o layout renderizado entre navegadores).
      texto = Array.from(terminalOutput.children)
        .map((linha) => linha.textContent)
        .join('\n');
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

  btnBaixarPython.addEventListener('click', () => {
    if (!pythonExportavel) return;
    const arquivo = new Blob([pythonExportavel], { type: 'text/x-python;charset=utf-8' });
    const endereco = URL.createObjectURL(arquivo);
    const link = document.createElement('a');
    link.href = endereco;
    link.download = 'script.py';
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(endereco), 1000);
  });

  function mostraAcaoLinhaErro(linha, codigo) {
    const linhas = codigo.split('\n');
    if (!Number.isInteger(linha) || linha < 1 || linha > linhas.length) return;
    const inicio = linhas.slice(0, linha - 1)
      .reduce((total, trecho) => total + trecho.length + 1, 0);
    btnLinhaErro = document.createElement('button');
    btnLinhaErro.type = 'button';
    btnLinhaErro.className = 'btn btn-secondary terminal-error-action';
    btnLinhaErro.textContent = `Ir para a linha ${linha}`;
    btnLinhaErro.addEventListener('click', () => {
      editor.focus();
      editor.setSelectionRange(inicio, inicio + linhas[linha - 1].length);
      const alturaLinha = parseFloat(getComputedStyle(editor).lineHeight);
      editor.scrollTop = Math.max(0, (linha - 1) * alturaLinha - editor.clientHeight / 3);
      atualizaCursorStats();
    });
    terminalOutput.append(btnLinhaErro);
  }

  // Botão Limpar
  btnLimpar.addEventListener('click', () => {
    editor.value = '';
    aposEdicao();
    defineSaidaTerminal('terminal-system', '[Editor limpo. Digite ou escolha um exemplo acima.]');
    bilingueOutput.textContent = 'Execute o código para visualizar a comparação lado a lado.';
    canonicoOutput.innerHTML = geraHtmlDestaque('# O código Python puro canônico aparecerá aqui após a transpilação.');
    outputStatus.textContent = 'Status: Pronto';
    executionTime.textContent = 'Tempo: -- ms';
  });

  // Seletor de Exemplos
  selectExemplo.addEventListener('change', () => {
    const chave = selectExemplo.value;
    if (EXEMPLOS[chave]) {
      editor.value = EXEMPLOS[chave];
      aposEdicao({ salvar: false });
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
      sources: window.PORTUPY_SOURCES || {}
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
        `⚠️ Não foi possível inicializar o ambiente Python no navegador.\n${err.message}\n\nOs assets locais do runtime WebAssembly podem estar ausentes ou incompletos.`
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
    if (!pyodideWorker || !workerReady || pendingExecution) return;

    invalidaAcoesDaSaida();
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
      if (editor.value !== codigo) {
        outputStatus.textContent = 'Código alterado. Execute novamente.';
        return;
      }

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

      if (dados.status !== 0) {
        ativaAba('terminal');
        mostraAcaoLinhaErro(dados.linha_erro, codigo);
      }

      // Atualiza Lado a Lado
      bilingueOutput.textContent = dados.lado_a_lado || 'Nenhuma saída comparativa gerada.';

      // Atualiza Canônico (com realce de sintaxe reaproveitado do editor)
      canonicoOutput.innerHTML = geraHtmlDestaque(dados.canonico || '# Nenhum código gerado.');

      if (dados.exportavel) {
        pythonExportavel = dados.canonico;
        btnBaixarPython.disabled = false;
      }

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

  // Restaura o rascunho salvo; sem rascunho, abre o exemplo 1.
  editor.value = rascunho !== null ? rascunho : (EXEMPLOS.ola || '');
  if (rascunho !== null) {
    selectExemplo.value = '';
  }
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
