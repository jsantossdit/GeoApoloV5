"""
Modelos de Dados e DTOs para Manutenção de Códigos e Sequenciais do Sistema.
GeoApolo V5
Clean Architecture: DTOs imutáveis para controle sequencial de chaves primárias.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ConfigCodDTO:
    """Configuração de sequencial numérico de uma tabela do GeoApolo (USER_geoapolo_configcod)."""
    geotabela: str = ""
    proximo_codigo: int = 1
    tabela_ativa: str = "S"
    empcod: str = ""
    empnome: str = ""

    @property
    def is_ativa(self) -> bool:
        return (self.tabela_ativa or "").upper() == "S"

    @property
    def display(self) -> str:
        status_label = "Ativa" if self.is_ativa else "Inativa"
        return f"{self.geotabela} (Próximo: {self.proximo_codigo}) - [{status_label}]"


@dataclass
class ResultadoConfigCodDTO:
    """Resultado padronizado de operações em configurações de sequenciais."""
    sucesso: bool = True
    mensagem: str = ""
    geotabela: Optional[str] = None
    proximo_codigo: Optional[int] = None
