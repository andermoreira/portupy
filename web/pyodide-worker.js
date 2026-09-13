/**
 * Worker de execução do Transpilador PT.
 *
 * Manter o Pyodide fora da thread da interface impede que um programa do
 * usuário bloqueie os controles do playground. O Worker é descartável: a
 * aplicação pode terminá-lo e criar outro quando o tempo limite for excedido.
 */

const PYODIDE_SCRIPT = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js';
const PYODIDE_INDEX_URL = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/';

let pyodideInstance = null;

async function inicializaPyodide(sources) {
  if (typeof importScripts !== 'function') {
    throw new Error('O navegador não disponibiliza Web Workers para executar Python.');
  }

  importScripts(PYODIDE_SCRIPT);
  if (typeof loadPyodide !== 'function') {
    throw new Error('A biblioteca Pyodide não foi carregada pelo navegador.');
  }

  pyodideInstance = await loadPyodide({ indexURL: PYODIDE_INDEX_URL });

  if (!sources || Object.keys(sources).length === 0) {
    throw new Error('O bundle do Transpilador PT não foi carregado.');
  }

  pyodideInstance.FS.mkdirTree('/home/pyodide/transpilador_pt');
  for (const [filename, content] of Object.entries(sources)) {
    pyodideInstance.FS.writeFile(`/home/pyodide/transpilador_pt/${filename}`, content);
  }

  await pyodideInstance.runPythonAsync(`
import sys
if '/home/pyodide' not in sys.path:
    sys.path.insert(0, '/home/pyodide')

import contextlib
import io
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

    try:
        resultado["canonico"] = transpilador_pt.transpila_canonico(codigo_pt)
    except Exception as exc:
        resultado["canonico"] = f"# Erro ao gerar Python canonico: {exc}"

    try:
        resultado["lado_a_lado"] = transpilador_pt.renderiza_lado_a_lado(
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
            resultado["status"] = transpilador_pt.executa_codigo(codigo_pt)
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
