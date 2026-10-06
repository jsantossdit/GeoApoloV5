"""
Módulo de Dashboard de Doações & Inteligência Analítica (Empresa 1.01).
Alimentado por USERPerfilFinanceiro_de_Doador conforme Dashboard-menuprincipal.sql.
GeoApolo V5
"""

from dashboard.models import (
    FiltroDashboardDTO,
    DoadorPerfilDTO,
    StatusDoadorMetricaDTO,
    DioceseMetricaDTO,
    TipoCobrancaMetricaDTO,
    EvolucaoMesDTO,
    EvolucaoAnoDTO,
    HistoricoAnoMetodoDTO,
    InsightIADTO,
    ResumoDoacoesDTO,
)
from dashboard.repository import DashboardRepository
from dashboard.service import DashboardService
from dashboard.gauge import DashboardGaugeWidget, GaugeOverlay
from dashboard.view import (
    DashboardDoacoesFrame,
    DashboardDoacoesView,
    abrir_dashboard_doacoes,
)

__all__ = [
    "FiltroDashboardDTO",
    "DoadorPerfilDTO",
    "StatusDoadorMetricaDTO",
    "DioceseMetricaDTO",
    "TipoCobrancaMetricaDTO",
    "EvolucaoMesDTO",
    "EvolucaoAnoDTO",
    "HistoricoAnoMetodoDTO",
    "InsightIADTO",
    "ResumoDoacoesDTO",
    "DashboardRepository",
    "DashboardService",
    "DashboardGaugeWidget",
    "GaugeOverlay",
    "DashboardDoacoesFrame",
    "DashboardDoacoesView",
    "abrir_dashboard_doacoes",
]
