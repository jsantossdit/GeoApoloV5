"""
Modelos de Dados e DTOs para Licenciamento, Segurança e Manutenção de Versões.
GeoApolo V5
Clean Architecture: DTOs imutáveis e desacoplados de persistência ou interface.
"""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class LicencaDTO:
    """Dados da licença mensal (user_geoapolo_dicionario)."""
    id_palavra: str = ""
    data_inicial: Optional[date] = None
    data_final: Optional[date] = None
    flag_bloqueia: str = "N"
    tempo_bloqueio_dias: int = 15
    flag_ativar: str = "S"
    mes_referencia: int = 0
    ano_referencia: int = 0

    @property
    def is_bloqueada(self) -> bool:
        return (self.flag_bloqueia or "").upper() == "S"

    @property
    def is_ativa(self) -> bool:
        return (self.flag_ativar or "").upper() == "S"

    def calcular_dias_restantes(self, data_ref: Optional[date] = None) -> int:
        if not self.data_final:
            return 0
        ref = data_ref or date.today()
        dias = (self.data_final - ref).days
        return max(0, dias)


@dataclass
class ResultadoValidacaoLicencaDTO:
    """Resultado da checagem de licença do período."""
    sucesso: bool = True
    status: str = "OK"  # 'OK', 'AVISO_EXPIRACAO', 'BLOQUEADA', 'NAO_ATIVADA', 'ERRO_CONSULTA'
    mensagem: str = ""
    dias_restantes: int = 0
    licenca: Optional[LicencaDTO] = None


@dataclass
class VersaoSistemaDTO:
    """Dados de release/versão do sistema (USER_geoapolo_novversao)."""
    idversao: str = ""
    data_lancamento: str = ""
    textonovaversao: str = ""
    statusversao: str = "N"  # 'S' = Liberada, 'N' = Não Liberada

    @property
    def is_liberada(self) -> bool:
        return (self.statusversao or "").upper() == "S"

    @property
    def display(self) -> str:
        status_label = "Liberada" if self.is_liberada else "Em Edição"
        return f"v{self.idversao} ({self.data_lancamento}) - [{status_label}]"


@dataclass
class ResultadoOperacaoVersaoDTO:
    """Resultado padronizado de operações em versões."""
    sucesso: bool = True
    mensagem: str = ""
    idversao: Optional[str] = None
