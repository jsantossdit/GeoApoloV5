"""
Modelos de dados e DTOs para Multi-Empresas e Contexto Corporativo.
GeoApolo V5
"""

from dataclasses import dataclass


@dataclass
class EmpresaDTO:
    """Dados cadastrais de uma empresa ou filial corporativa."""
    empcod: str
    empnome: str
    ativa: bool = True

    @property
    def display_completo(self) -> str:
        return f"{self.empcod} - {self.empnome}"


@dataclass
class ResultadoEmpresaDTO:
    """Resultado padronizado para operações cadastrais de empresas."""
    sucesso: bool
    mensagem: str
    total_afetado: int = 0
