"""Deixa `import corretor` funcionar rodando o pytest de qualquer diretório.

Sem isto, `pytest porte_fastapi/testes/` a partir da raiz do repositório não
encontra o pacote (o pytest põe no sys.path a pasta dos testes, não a pasta pai).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
