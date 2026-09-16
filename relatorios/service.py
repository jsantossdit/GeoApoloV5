"""
Serviço de extração de dados para relatórios do GeoAlvo.
Preserva as otimizações nativas SQL Server e hints WITH (NOLOCK).
"""

import logging
from typing import List, Dict, Any
from relatorios.models import FiltroRelatorio, TipoRelatorio
from entidades.database import obter_conexao_banco

logger = logging.getLogger(__name__)


class RelatorioService:

    def __init__(self, connection=None):
        self._conn = connection

    def _get_cursor(self):
        if self._conn is None:
            self._conn = obter_conexao_banco()
        return self._conn.cursor()

    def obter_dados_relatorio(self, filtro: FiltroRelatorio) -> List[Dict[str, Any]]:
        cursor = self._get_cursor()

        if filtro.tipo_relatorio == TipoRelatorio.ENTIDADES_GERAL:
            sql = """
                SELECT TOP (500)
                    e.geoentcod AS [Código],
                    e.geoentnome AS [Nome],
                    ISNULL(uged.geonumerodocumento, '') AS [CPF/CNPJ],
                    e.geoentender AS [Endereço],
                    e.geoenderno AS [Nº],
                    e.geoentbair AS [Bairro],
                    c.cidnomecomp AS [Cidade],
                    c.ufsigla AS [UF],
                    e.geoentcep AS [CEP],
                    CASE WHEN ue.atualizou_apolo = 'S' THEN 'Sim' ELSE 'Não' END AS [Sincronizado Alvo],
                    CONVERT(VARCHAR(10), e.geoentdatacad, 103) AS [Data Cadastro]
                FROM USER_geoapolo_entidade e WITH (NOLOCK)
                LEFT JOIN user_geoapolo_cidades c WITH (NOLOCK) ON e.geocidcod = c.geocidcod
                LEFT JOIN user_geoapolo_entidade ue WITH (NOLOCK) ON e.geoentcod = ue.geoentcod
                LEFT JOIN USER_geoapolo_entidade_documentos uged WITH (NOLOCK)
                       ON e.geoentcod = uged.geoentcod AND uged.geotipodocumento = 'CPF/CNPJ'
                ORDER BY e.geoentnome ASC
            """
            cursor.execute(sql)

        elif filtro.tipo_relatorio == TipoRelatorio.ENTIDADES_SINCRONIZADAS:
            sql = """
                SELECT TOP (500)
                    e.geoentcod AS [Código SVE],
                    ue.entcod AS [Código Alvo],
                    e.geoentnome AS [Nome],
                    ISNULL(uged.geonumerodocumento, '') AS [CPF/CNPJ],
                    c.cidnomecomp AS [Cidade],
                    c.ufsigla AS [UF],
                    CONVERT(VARCHAR(10), ue.data_atualizou_apolo, 103) AS [Data Sincronização]
                FROM USER_geoapolo_entidade e WITH (NOLOCK)
                INNER JOIN user_geoapolo_entidade ue WITH (NOLOCK) ON e.geoentcod = ue.geoentcod
                LEFT JOIN user_geoapolo_cidades c WITH (NOLOCK) ON e.geocidcod = c.geocidcod
                LEFT JOIN USER_geoapolo_entidade_documentos uged WITH (NOLOCK)
                       ON e.geoentcod = uged.geoentcod AND uged.geotipodocumento = 'CPF/CNPJ'
                WHERE ue.atualizou_apolo = 'S'
                ORDER BY ue.data_atualizou_apolo DESC, e.geoentnome ASC
            """
            cursor.execute(sql)

        elif filtro.tipo_relatorio == TipoRelatorio.ENTIDADES_PENDENTES:
            sql = """
                SELECT TOP (500)
                    e.geoentcod AS [Código SVE],
                    e.geoentnome AS [Nome],
                    ISNULL(uged.geonumerodocumento, '') AS [CPF/CNPJ],
                    e.geoentender AS [Endereço],
                    c.cidnomecomp AS [Cidade],
                    c.ufsigla AS [UF],
                    ISNULL(e.geoobservacoes, '') AS [Observações Pendentes]
                FROM USER_geoapolo_entidade e WITH (NOLOCK)
                INNER JOIN user_geoapolo_entidade ue WITH (NOLOCK) ON e.geoentcod = ue.geoentcod
                LEFT JOIN user_geoapolo_cidades c WITH (NOLOCK) ON e.geocidcod = c.geocidcod
                LEFT JOIN USER_geoapolo_entidade_documentos uged WITH (NOLOCK)
                       ON e.geoentcod = uged.geoentcod AND uged.geotipodocumento = 'CPF/CNPJ'
                WHERE ue.atualizou_apolo = 'N'
                ORDER BY e.geoentnome ASC
            """
            cursor.execute(sql)

        elif filtro.tipo_relatorio == TipoRelatorio.OCORRENCIAS_SISTEMA:
            sql = """
                SELECT TOP (500)
                    e.geoentcod AS [Código],
                    e.geoentnome AS [Entidade],
                    ue.ocorcod AS [Nº Ocorrência],
                    ue.usucod_atualizou_apolo AS [Usuário],
                    'Atualização Ignorada por Estar Conforme' AS [Motivo]
                FROM USER_geoapolo_entidade e WITH (NOLOCK)
                INNER JOIN user_geoapolo_entidade ue WITH (NOLOCK) ON e.geoentcod = ue.geoentcod
                WHERE ue.ocorcod IS NOT NULL AND ue.ocorcod <> ''
                ORDER BY e.geoentcod DESC
            """
            cursor.execute(sql)

        else:
            # Fallback
            sql = "SELECT TOP (100) geoentcod AS [Código], geoentnome AS [Nome] FROM USER_geoapolo_entidade WITH (NOLOCK)"
            cursor.execute(sql)

        colunas = [c[0] for c in cursor.description]
        registros = []
        for row in cursor.fetchall():
            registros.append(dict(zip(colunas, row)))

        return registros
