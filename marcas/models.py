"""
Modelos e DTOs para Marcas de Produtos e Estoque Auxiliar.
GeoApolo V5
Equivalente a unt_cadmarcas.pas do Delphi.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MarcaDTO:
    """Marca de produto (USER_geoapolo_produto_marcas)."""
    codigo_marca: int = 0
    descricao_marca: str = ""

    @property
    def display(self) -> str:
        return f"{self.codigo_marca:03d} - {self.descricao_marca}"


@dataclass
class ResultadoMarcaDTO:
    """Resultado padronizado de operações do cadastro de marcas."""
    sucesso: bool = True
    mensagem: str = ""
    codigo: Optional[int] = None
