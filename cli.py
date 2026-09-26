#!/usr/bin/env python3
"""Atalho para rodar a CLI a partir do repositório: ``python3 cli.py ...``.

A implementação vive em ``portupy/cli.py``; instalado, o comando é ``portupy``.
"""

import sys

from portupy.cli import main

if __name__ == "__main__":
    sys.exit(main())
