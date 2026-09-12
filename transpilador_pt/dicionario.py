"""
Dicionário de tradução PT -> Python.

Um único mapa cobre tanto palavras reservadas (se, para, enquanto...)
quanto builtins comuns (mostre, leia, tamanho...), porque para o
tokenizer do Python ambos são apenas tokens NAME -- não existe
distinção sintática entre "palavra reservada" e "nome de função" no
nível de token, só no nível de parser/AST.

IMPORTANTE (limitação conhecida, discutida na conversa): algumas
chaves aqui são palavras muito comuns no português cotidiano
("em", "e", "ou", "com", "como"). Isso significa que essas palavras
ficam indisponíveis como nomes de variável, exatamente como "in",
"and", "or" também são reservadas em inglês. É um trade-off
inerente a essa abordagem, não um bug.
"""

# --- Palavras-chave estruturais -------------------------------------------
PALAVRAS_CHAVE = {
    "se": "if",
    "senao": "else",          # sem acento, teclado-friendly
    "senão": "else",
    "senaose": "elif",
    "senãose": "elif",
    "ouse": "elif",           # legado / retrocompatibilidade
    "para": "for",
    "enquanto": "while",
    "funcao": "def",
    "função": "def",
    "retorne": "return",
    "classe": "class",
    "importe": "import",
    "de": "from",
    "como": "as",
    "com": "with",
    "tente": "try",
    "exceto": "except",
    "finalmente": "finally",
    "levante": "raise",
    "quebre": "break",
    "continue": "continue",
    "passe": "pass",
    "em": "in",
    "nao": "not",
    "não": "not",
    "e": "and",
    "ou": "or",
    "lambda": "lambda",
    "global": "global",
    "assincrono": "async",
    "aguarde": "await",
    "produza": "yield",
    "del": "del",
    "assert": "assert",
    "verdadeiro": "True",
    "falso": "False",
    "nulo": "None",
}

# --- Builtins curados injetados em runtime (ADR-001) ------------------------
BUILTINS_PT = {
    "mostre": print,
    "mostra": print,
    "leia": input,
    "tamanho": len,
    "intervalo": range,
    "tipo": type,
    "texto": str,
    "inteiro": int,
    "decimal": float,
    "booleano": bool,
    "lista": list,
    "dicionario": dict,
    "dicionário": dict,
    "conjunto": set,
    "tupla": tuple,
    "ordene": sorted,
    "inverta": reversed,
    "some": sum,
    "maximo": max,
    "máximo": max,
    "minimo": min,
    "mínimo": min,
    "absoluto": abs,
    "arredonde": round,
    "enumere": enumerate,
    "zip": zip,
    "mapeie": map,
    "filtre": filter,
}

# MAPA utilizado pelo transpilador léxico para alterar tokens sintáticos
MAPA = PALAVRAS_CHAVE

# Mapeamento de builtins pedagógicos para nomes canônicos do Python (ADR-003)
BUILTINS_CANONICOS = {
    "mostre": "print",
    "mostra": "print",
    "leia": "input",
    "tamanho": "len",
    "intervalo": "range",
    "tipo": "type",
    "texto": "str",
    "inteiro": "int",
    "decimal": "float",
    "booleano": "bool",
    "lista": "list",
    "dicionario": "dict",
    "dicionário": "dict",
    "conjunto": "set",
    "tupla": "tuple",
    "ordene": "sorted",
    "inverta": "reversed",
    "some": "sum",
    "maximo": "max",
    "máximo": "max",
    "minimo": "min",
    "mínimo": "min",
    "absoluto": "abs",
    "arredonde": "round",
    "enumere": "enumerate",
    "zip": "zip",
    "mapeie": "map",
    "filtre": "filter",
}

