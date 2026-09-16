"""
Repositório de Dados para Transações Vindi e Conciliação Apolo.
GeoApolo V5
"""

import logging
from typing import List, Optional, Tuple
from datetime import date
from entidades.database import obter_conexao_banco
from .models import TransacaoVindiDTO

logger = logging.getLogger(__name__)


class VindiRepository:
    """Acesso ao SQL Server para conciliação das doações e transações da Vindi."""

    def __init__(self, connection=None):
        self._conn = connection

    def _get_cursor(self):
        if self._conn is None:
            self._conn = obter_conexao_banco()
        return self._conn.cursor()

    def commit(self):
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()

    def rollback(self):
        if self._conn and hasattr(self._conn, "rollback"):
            self._conn.rollback()

    def listar_transacoes(
        self, data_ini: date, data_fim: date, apenas_nao_integradas: bool = False
    ) -> List[TransacaoVindiDTO]:
        cursor = self._get_cursor()
        sql = """
            SELECT pedidoid, ISNULL(cpfcnpj, ''), ISNULL(nomecliente, ''),
                   datatransacao, ISNULL(valorbruto, 0.0), ISNULL(valortarifa, 0.0),
                   ISNULL(valorliquido, 0.0), ISNULL(statusvindi, 'Paga'),
                   ISNULL(integradaapolo, 0), entcod, categcod
            FROM transacoes_vindi WITH (NOLOCK)
            WHERE datatransacao >= ? AND datatransacao <= ?
        """
        params = [data_ini, data_fim]
        if apenas_nao_integradas:
            sql += " AND (integradaapolo = 0 OR integradaapolo IS NULL)"

        sql += " ORDER BY datatransacao ASC, pedidoid ASC"
        cursor.execute(sql, params)

        resultados = []
        for r in cursor.fetchall():
            dt = r[3].date() if hasattr(r[3], "date") else r[3]
            resultados.append(
                TransacaoVindiDTO(
                    pedido_id=str(r[0]).strip(),
                    cpf_cnpj=str(r[1]).strip(),
                    nome_cliente=str(r[2]).strip(),
                    data_transacao=dt,
                    valor_bruto=float(r[4]),
                    valor_tarifa=float(r[5]),
                    valor_liquido=float(r[6]),
                    status_vindi=str(r[7]).strip(),
                    integrada_apolo=bool(r[8]),
                    ent_cod=str(r[9]).strip() if r[9] else None,
                    categoria_cod=str(r[10]).strip() if r[10] else None,
                )
            )
        return resultados

    def buscar_entidade_por_cpf(self, cpf: str) -> Optional[Tuple[str, str]]:
        cursor = self._get_cursor()
        doc_limpo = cpf.replace(".", "").replace("-", "").replace("/", "").strip()
        sql = """
            SELECT TOP 1 entcod, entnome
            FROM entidade WITH (NOLOCK)
            WHERE REPLACE(REPLACE(REPLACE(ISNULL(entcpf, ''), '.', ''), '-', ''), '/', '') = ?
               OR REPLACE(REPLACE(REPLACE(ISNULL(entcnpj, ''), '.', ''), '-', ''), '/', '') = ?
        """
        cursor.execute(sql, [doc_limpo, doc_limpo])
        r = cursor.fetchone()
        if r:
            return str(r[0]).strip(), str(r[1]).strip()
        return None

    def buscar_categorias_entidade(self, ent_cod: str) -> List[str]:
        cursor = self._get_cursor()
        sql = """
            SELECT categcodestr
            FROM ent_categ WITH (NOLOCK)
            WHERE entcod = ?
        """
        cursor.execute(sql, [ent_cod])
        return [str(r[0]).strip() for r in cursor.fetchall()]

    def marcar_transacao_integrada(self, pedido_id: str) -> bool:
        cursor = self._get_cursor()
        try:
            sql = "UPDATE transacoes_vindi SET integradaapolo = 1 WHERE pedidoid = ?"
            cursor.execute(sql, [pedido_id])
            self.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.rollback()
            logger.exception("Erro ao marcar transação integrada: %s", e)
            return False
