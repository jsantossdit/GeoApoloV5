"""
Modelos de Dados e DTOs para Gestão de Departamentos e Seções do Sistema.
GeoApolo V5
Clean Architecture: DTOs imutáveis para organização estrutural corporativa e centros de custo.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DepartamentoDTO:
    """Departamento ou Seção da Empresa (USER_geoapolo_departamentos)."""
    codigo_departamento: int = 0
    nome_departamento: str = ""
    empcod: str = "01"
    empnome: str = ""
    flagativo: str = "A"  # 'A' = Ativo, 'I' = Inativo
    cctrlcodestr: str = ""
    cctrlnome: str = ""

    @property
    def is_ativo(self) -> bool:
        return (self.flagativo or "").upper() in ("A", "S", "1", "TRUE")

    @property
    def display(self) -> str:
        status_label = "Ativo" if self.is_ativo else "Inativo"
        emp_label = f"[{self.empcod}]" if self.empcod else ""
        return f"{self.codigo_departamento:03d} - {self.nome_departamento} {emp_label} ({status_label})"


@dataclass
class ResultadoDepartamentoDTO:
    """Resultado padronizado de operações de Departamentos e Seções."""
    sucesso: bool = True
    mensagem: str = ""
    codigo: Optional[int] = None
