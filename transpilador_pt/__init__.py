from .transpiler import transpila, transpila_canonico, ErroDeTraducao
from .executor import executa_codigo, executa_arquivo
from .transicao import renderiza_lado_a_lado

__all__ = [
    "transpila",
    "transpila_canonico",
    "ErroDeTraducao",
    "executa_codigo",
    "executa_arquivo",
    "renderiza_lado_a_lado",
]


