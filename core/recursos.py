"""
Utilitário para Resolução de Recursos e Imagens.
GeoApolo V5
Compatível com desenvolvimento e execução empacotada com PyInstaller (sys._MEIPASS).
"""

import os
import sys


def obter_caminho_recurso(caminho_relativo: str) -> str:
    """Retorna o caminho absoluto de um recurso/imagem, tanto em desenvolvimento
    quanto em executáveis empacotados pelo PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        base_dir = getattr(sys, "_MEIPASS")
    else:
        # Diretório raiz do projeto GeoApoloV5
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    caminho_normalizado = os.path.join(base_dir, caminho_relativo.replace("/", os.sep).replace("\\", os.sep))
    return caminho_normalizado
