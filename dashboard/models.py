"""
Modelos e DTOs para o Dashboard de Doações & Inteligência Analítica (Empresa 1.01).
Alimentado pelas regras e colunas do arquivo Dashboard-menuprincipal.sql.
GeoApolo V5
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from datetime import date


@dataclass
class DoadorPerfilDTO:
    """
    Registro individual de doador extraído da query do Dashboard-menuprincipal.sql.
    """
    entcod: str
    entnome: str
    uf: str
    codigo_dio: str
    diocese: str
    categcodestr: str
    categnome: str
    tipocobcod: str
    forma_contribuicao: str
    data_doacao_mescorrente: Optional[date]
    valor_doado: float
    data_doacao_anterior: Optional[date]
    valor_doado_mesanterior: float
    docfinchv: str
    status_doador: str  # 'Novo Doador', 'Retorno Doador', 'Doador Recorrente'


@dataclass
class StatusDoadorMetricaDTO:
    """Métrica agregada por status do doador (Novo, Recorrente, Retorno)."""
    status: str
    qtd: int
    total: float
    percentual: float
    ticket_medio: float
    cor: str = "#2563EB"


@dataclass
class DioceseMetricaDTO:
    """Métrica agregada por diocese e UF."""
    codigo: str
    nome: str
    uf: str
    qtd: int
    total: float
    percentual: float
    ticket_medio: float


@dataclass
class TipoCobrancaMetricaDTO:
    """Métrica agregada por tipo de cobrança / forma de doação (BOL, DEB, VND, PIX)."""
    codigo: str
    nome: str
    qtd: int
    total: float
    percentual: float
    ticket_medio: float
    ranking: int = 1
    tendencia: str = "ESTAVEL"  # "ALTA", "BAIXA", "ESTAVEL"


@dataclass
class EvolucaoMesDTO:
    """Consolidação mensal dentro do ano selecionado."""
    mes: int
    nome_mes: str
    qtd: int
    doadores: int
    total: float
    ticket_medio: float


@dataclass
class EvolucaoAnoDTO:
    """Consolidação histórica anual de arrecadação."""
    ano: int
    total: float
    qtd: int
    doadores: int
    ticket_medio: float
    meses: Dict[int, float] = field(default_factory=dict)


@dataclass
class HistoricoAnoMetodoDTO:
    """Registro histórico anual do meio de pagamento líder e consolidação do ano."""
    ano: int
    metodo_lider: str
    total_lider: float
    pct_lider: float
    total_ano: float
    qtd_ano: int
    ticket_medio: float
    metodos: List[TipoCobrancaMetricaDTO] = field(default_factory=list)


@dataclass
class InsightIADTO:
    """Diagnóstico ou recomendação gerada pelo motor analítico de IA."""
    tipo: str  # 'TENDENCIA', 'OPORTUNIDADE', 'ALERTA', 'FORECAST', 'DESTAQUE', 'FIDELIZACAO'
    icone: str
    titulo: str
    descricao: str
    impacto: str  # 'ALTO', 'MEDIO', 'INFO'
    cor_destaque: str = "#1A365D"


@dataclass
class FiltroDashboardDTO:
    """Parâmetros de filtragem para o painel de doações."""
    empresa: str = "1.01"
    tipo_periodo: str = "10_DIAS"  # "10_DIAS", "15_DIAS", "30_DIAS", "MES", "PERSONALIZADO"
    data_inicial: Optional[date] = None
    data_final: Optional[date] = None
    ano: int = 2026
    mes: int = 9  # 1 a 12
    carregar_historico_completo: bool = False
    anos: List[int] = field(default_factory=lambda: list(range(2018, 2027)))
    ano_filtro: Optional[int] = None
    status_filtro: str = "TODOS"  # "TODOS", "Novo Doador", "Doador Recorrente", "Retorno Doador"
    forma_filtro: str = "TODAS"   # "TODAS", "BOL", "DEB", "VND", "PIX"
    situacao: str = "TODAS"
    termo_busca: str = ""
    subgrupos: Tuple[str, ...] = (
        "02.001", "02.002",
        "03.001", "03.002", "03.003", "03.004", "03.005"
    )


@dataclass
class ResumoDoacoesDTO:
    """Indicadores Chave de Desempenho (KPIs) consolidados do dashboard."""
    ano: int = 2026
    mes: int = 9
    tipo_periodo: str = "10_DIAS"
    data_inicial: Optional[date] = None
    data_final: Optional[date] = None
    total_arrecadado: float = 0.0
    total_recebido: float = 0.0
    total_aberto: float = 0.0
    total_mes_anterior: float = 0.0
    variacao_mes_anterior_pct: float = 0.0
    qtd_doacoes: int = 0
    qtd_doadores: int = 0
    ticket_medio: float = 0.0

    # Métricas de Perfil de Doador (Dashboard-menuprincipal.sql)
    qtd_novos: int = 0
    total_novos: float = 0.0
    qtd_recorrentes: int = 0
    total_recorrentes: float = 0.0
    qtd_retorno: int = 0
    total_retorno: float = 0.0

    metodo_campeao: str = "Nenhum"
    metodo_campeao_valor: float = 0.0
    metodo_campeao_pct: float = 0.0
    crescimento_yoy_pct: float = 0.0
    taxa_quitacao_pct: float = 0.0
    periodo_descricao: str = "Últimos 10 Dias de Movimento"

    status_metricas: List[StatusDoadorMetricaDTO] = field(default_factory=list)
    tipos_cobranca: List[TipoCobrancaMetricaDTO] = field(default_factory=list)
    top_dioceses: List[DioceseMetricaDTO] = field(default_factory=list)
    evolucao_meses: List[EvolucaoMesDTO] = field(default_factory=list)
    evolucao_anos: List[EvolucaoAnoDTO] = field(default_factory=list)
    historico_metodos: List[HistoricoAnoMetodoDTO] = field(default_factory=list)
    doadores: List[DoadorPerfilDTO] = field(default_factory=list)
    insights_ia: List[InsightIADTO] = field(default_factory=list)
