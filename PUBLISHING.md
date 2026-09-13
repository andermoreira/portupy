# Publicação do PortuPy no PyPI

Guia para publicar uma nova versão do pacote `portupy`.

> A publicação é **irreversível**: uma versão enviada ao PyPI não pode ser
> reenviada nem realmente removida. Sempre ensaie no TestPyPI antes.

## Pré-requisitos

- Conta no [PyPI](https://pypi.org) e no [TestPyPI](https://test.pypi.org).
- Um **token de API** de cada um (Account settings → API tokens). Use tokens,
  não senha.
- `build` e `twine` disponíveis. Com [uv](https://docs.astral.sh/uv/):
  não precisa instalar nada — use `uvx`.

## 1. Atualizar a versão

A versão vem de `portupy/__init__.py` (`__version__`). Faça o bump seguindo
[SemVer](https://semver.org/lang/pt-BR/) e faça commit antes de publicar.

## 2. Build limpo

O diretório `build/` reaproveita artefatos entre builds e pode contaminar o
pacote (ex.: arquivos de um nome de módulo antigo). **Sempre limpe antes.**

```bash
rm -rf build dist
uvx --from build pyproject-build     # ou: python -m build
```

Gera `dist/portupy-<versão>.tar.gz` (sdist) e `dist/portupy-<versão>-py3-none-any.whl` (wheel).

## 3. Validar

```bash
uvx twine check dist/*
```

Deve reportar `PASSED` para os dois artefatos.

## 4. Ensaiar no TestPyPI

```bash
uvx twine upload --repository testpypi dist/*
```

Informe `__token__` como usuário e o token do TestPyPI como senha. Depois,
teste a instalação num ambiente limpo (o `--extra-index-url` é necessário
porque as dependências não existem no TestPyPI):

```bash
uv run --python 3.12 --with "portupy" \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  portupy --version
```

## 5. Publicar no PyPI

Só depois que o ensaio no TestPyPI estiver OK:

```bash
uvx twine upload dist/*
```

Usuário `__token__`, senha = token do PyPI real.

## 6. Verificar

```bash
uv run --python 3.12 --with portupy portupy --version
```

## Dica: automação por tag (opcional)

Dá para publicar automaticamente ao criar uma tag `vX.Y.Z` via GitHub Actions
usando [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC,
sem guardar tokens no repositório). Peça ajuda para configurar quando quiser.
