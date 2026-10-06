"""
Modelos e DTOs para o Cadastro de Cargos.
GeoApolo V5
Clean Architecture: DTOs e resultados padronizados para cargos.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CargoDTO:
    """Registro de Cargo (USER_geoapolo_cargos / cargo)."""
    geocargocodestr: int = 0
    geocargonome: str = ""
    geofaixasalarial: str = ""

    def __post_init__(self):
        if self.geocargonome:
            self.geocargonome = str(self.geocargonome).strip().upper()
        if self.geofaixasalarial:
            self.geofaixasalarial = str(self.geofaixasalarial).strip().upper()

    @property
    def codigo(self) -> int:
        return self.geocargocodestr

    @codigo.setter
    def codigo(self, valor: int):
        self.geocargocodestr = int(valor or 0)

    @property
    def nome(self) -> str:
        return self.geocargonome

    @nome.setter
    def nome(self, valor: str):
        self.geocargonome = (valor or "").strip().upper()

    @property
    def faixa_salarial(self) -> str:
        return self.geofaixasalarial

    @faixa_salarial.setter
    def faixa_salarial(self, valor: str):
        self.geofaixasalarial = (valor or "").strip().upper()


@dataclass
class ResultadoCargoDTO:
    """Resultado padronizado de operações sobre cargos."""
    sucesso: bool = True
    mensagem: str = ""
    codigo: Optional[int] = None
    cargo: Optional[CargoDTO] = None
