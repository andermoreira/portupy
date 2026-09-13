/**
 * Worker de execução do Transpilador PT.
 *
 * Manter o Pyodide fora da thread da interface impede que um programa do
 * usuário bloqueie os controles do playground. O Worker é descartável: a
 * aplicação pode terminá-lo e criar outro quando o tempo limite for excedido.
 */

const PYODIDE_ASSETS_ROOT = new URL(
  './vendor/pyodide/v0.26.4/full/',
  self.location.href
).href;
const PYODIDE_SCRIPT = `${PYODIDE_ASSETS_ROOT}pyodide.js`;
const PYODIDE_INDEX_URL = PYODIDE_ASSETS_ROOT;

let pyodideInstance = null;

function restringeApisPersistentesDoWorker() {
  const recusar = () => Promise.reject(
    new Error('A Cache Storage não está disponível no worker de execução.')
  );
  const cacheStorageStub = {
    open: recusar,
    match: recusar,
    has: recusar,
    delete: recusar,
    keys: recusar,
  };
  try {
    Object.defineProperty(self, 'caches', {
      configurable: false,
      enumerable: true,
      get() {
        return cacheStorageStub;
      },
    });
  } catch (error) {
    self.caches = cacheStorageStub;
  }
  self.importScripts = function importScriptsBloqueado() {
    throw new Error('importScripts não está disponível após a inicialização do runtime.');
  };
}

async function inicializaPyodide(sources) {
  if (typeof importScripts !== 'function') {
    throw new Error('O navegador não disponibiliza Web Workers para executar Python.');
  }

  importScripts(PYODIDE_SCRIPT);
  if (typeof loadPyodide !== 'function') {
    throw new Error('A biblioteca Pyodide não foi carregada pelo navegador.');
  }

  pyodideInstance = await loadPyodide({ indexURL: PYODIDE_INDEX_URL });
  restringeApisPersistentesDoWorker();

  if (!sources || Object.keys(sources).length === 0) {
    throw new Error('O bundle do Transpilador PT não foi carregado.');
  }

  pyodideInstance.FS.mkdirTree('/home/pyodide/portupy');
  for (const [filename, content] of Object.entries(sources)) {
    pyodideInstance.FS.writeFile(`/home/pyodide/portupy/${filename}`, content);
  }

  await pyodideInstance.runPythonAsync(`
import sys
if '/home/pyodide' not in sys.path:
    sys.path.insert(0, '/home/pyodide')

import builtins
import contextlib
import io
import json
import portupy
from portupy.erros import EntradaIndisponivelError


def _entrada_indisponivel(*args, **kwargs):
    raise EntradaIndisponivelError()


# No navegador, 'leia'/input nao tem stdin interativo. Substituimos as duas
# referencias (o builtin e a entrada curada em portupy) por uma versao que
# explica a limitacao em portugues, em vez de estourar EOFError/OSError cru.
builtins.input = _entrada_indisponivel
portupy.dicionario.BUILTINS_PT["leia"] = _entrada_indisponivel


def _processa_codigo_web(codigo_pt):
    resultado = {
        "status": 0,
        "stdout": "",
        "stderr": "",
        "canonico": "",
        "lado_a_lado": ""
    }

    try:
        resultado["canonico"] = portupy.transpila_canonico(codigo_pt)
    except Exception as exc:
        resultado["canonico"] = f"# Erro ao gerar Python canonico: {exc}"

    try:
        resultado["lado_a_lado"] = portupy.renderiza_lado_a_lado(
            codigo_pt,
            resultado["canonico"],
            largura_terminal=80
        )
    except Exception as exc:
        resultado["lado_a_lado"] = f"Erro na visualizacao lado a lado: {exc}"

    stdout_buf = io.StringIO()
    stderr_buf = io.StringIO()
    with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
        try:
            resultado["status"] = portupy.executa_codigo(codigo_pt)
        except Exception as exc:
            resultado["status"] = 1
            stderr_buf.write(f"Excecao inesperada: {exc}\\n")

    resultado["stdout"] = stdout_buf.getvalue()
    resultado["stderr"] = stderr_buf.getvalue()
    return json.dumps(resultado)
`);
}

self.addEventListener('message', async (event) => {
  const mensagem = event.data || {};

  try {
    if (mensagem.type === 'init') {
      await inicializaPyodide(mensagem.sources);
      self.postMessage({ type: 'ready' });
      return;
    }

    if (mensagem.type === 'execute') {
      if (!pyodideInstance) {
        throw new Error('O ambiente Python ainda não foi inicializado.');
      }

      pyodideInstance.globals.set('_codigo_aluno', mensagem.codigo);
      const resultado = await pyodideInstance.runPythonAsync(
        '_processa_codigo_web(_codigo_aluno)'
      );
      self.postMessage({ type: 'result', resultado });
    }
  } catch (error) {
    self.postMessage({
      type: 'error',
      message: error && error.message ? error.message : String(error)
    });
  }
});
