"""
Modelos e DTOs para Cadastro e Manutenção de Centros de Controle / Custos.
GeoApolo V5
Equivalente funcional a unt_principal (mnucad_mancentrocontrole) e unt_consultav3 no Delphi.
Tabela base: USER_geoapolo_centrocontrole.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class CentroControleDTO:
    """Representação de um Centro de Controle / Custo (USER_geoapolo_centrocontrole)."""
    geocctrlcodestr: str = ""         # Código estruturado (ex: '004.001.001')
    geocctrlcodreduzido: str = ""     # Código reduzido (ex: '05')
    geocctrlnome: str = ""            # Nome / Descrição do centro de controle
    geocctrlcodestrniv: str = ""      # Código do nível superior (ex: '004.001')
    geocctrlgrupo: str = "A"          # 'T' = Sintético / Grupo, 'A' = Analítico
    geocctrlcusto: str = ""           # Código de centro de custo auxiliar
    geodatavalidadeinicial: Optional[str] = None  # Data validade inicial (ISO ou DD/MM/AAAA)
    geodatavalidadefinal: Optional[str] = None    # Data validade final (ISO ou DD/MM/AAAA)
    empcod: str = "1.01"              # Código da empresa

    @property
    def display_tipo(self) -> str:
        return "Sintético (Grupo)" if self.geocctrlgrupo == "T" else "Analítico"

    @property
    def is_sintetico(self) -> bool:
        return self.geocctrlgrupo == "T"

    @property
    def display(self) -> str:
        return f"{self.geocctrlcodestr} - {self.geocctrlnome}"


@dataclass
class ResultadoCentroControleDTO:
    """Resultado padronizado de operações em centros de controle."""
    sucesso: bool = True
    mensagem: str = ""
    codigo: Optional[str] = None
    objeto: Optional[CentroControleDTO] = None
