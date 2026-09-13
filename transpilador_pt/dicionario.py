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

import builtins

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

# MAPA utilizado pelo transpilador léxico para alterar tokens sintáticos
MAPA = PALAVRAS_CHAVE

# --- Builtins curados (fonte única) -----------------------------------------
# Mapeia o nome pedagógico em português para o nome canônico do builtin Python.
# Esta é a única fonte de verdade: tanto a injeção em runtime (ADR-001) quanto a
# exportação canônica (ADR-003) são derivadas daqui, evitando dessincronização.
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

# Builtins injetados em runtime (ADR-001), derivados da fonte única acima
# resolvendo cada nome canônico para o objeto builtin correspondente.
BUILTINS_PT = {
    nome_pt: getattr(builtins, nome_canonico)
    for nome_pt, nome_canonico in BUILTINS_CANONICOS.items()
}

