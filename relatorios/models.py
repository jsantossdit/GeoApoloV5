"""
Modelos de dados e definições de relatórios do GeoAlvo.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import date, datetime


class TipoRelatorio(Enum):
    ENTIDADES_GERAL = "Entidades - Listagem Geral"
    ENTIDADES_SINCRONIZADAS = "Entidades - Já Sincronizadas com Alvo"
    ENTIDADES_PENDENTES = "Entidades - Pendentes de Sincronização"
    ENTIDADES_DIVERGENTES = "Entidades - Divergências SVE x Alvo"
    OCORRENCIAS_SISTEMA = "Auditoria - Ocorrências e Registros Ignorados"


class FormatoExportacao(Enum):
    EXCEL = "Excel (.xlsx)"
    HTML_PDF = "Visualizar / Imprimir (HTML/PDF)"
    CSV = "Arquivo CSV (.csv)"


@dataclass
class FiltroRelatorio:
    tipo_relatorio: TipoRelatorio = TipoRelatorio.ENTIDADES_GERAL
    data_inicial: Optional[date] = None
    data_final: Optional[date] = None
    base_dados: str = "GeoApolo"
    cidade: str = ""
    uf: str = ""
    status_sincronizacao: str = "TODOS"  # 'TODOS', 'S', 'N'
    termo_busca: str = ""
