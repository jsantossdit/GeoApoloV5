"""
Modelos e DTOs para Cores de Produtos e Estoque Auxiliar.
GeoApolo V5
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CorDTO:
    """Cor de produto (USER_geoapolo_produto_cores)."""
    codigo_cor: int = 0
    descricao_cor: str = ""

    @property
    def display(self) -> str:
        return f"{self.codigo_cor:03d} - {self.descricao_cor}"


@dataclass
class ResultadoCorDTO:
    """Resultado padronizado de operações do cadastro de cores."""
    sucesso: bool = True
    mensagem: str = ""
    codigo: Optional[int] = None
