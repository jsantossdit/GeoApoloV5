"""
Repositório de Dados Fiscal para Auditoria de Cupons e NFC-e.
GeoApolo V5
"""

import sqlite3
import logging
from typing import List, Optional
from datetime import date
from entidades.database import obter_conexao_banco
from .models import AuditoriaCupomDTO

logger = logging.getLogger(__name__)


class FiscalRepository:
    """Acesso às bases de PDV (SQLite) e de retaguarda (SQL Server Apolo)."""

    def __init__(self, caminho_sqlite: Optional[str] = None, conexao_apolo=None):
        self.caminho_sqlite = caminho_sqlite
        self._conn_apolo = conexao_apolo

    def _get_cursor_apolo(self):
        if self._conn_apolo is None:
            self._conn_apolo = obter_conexao_banco()
        return self._conn_apolo.cursor()

    def _get_conexao_sqlite(self):
        if not self.caminho_sqlite:
            raise ValueError("Caminho da base SQLite do PDV não foi informado.")
        return sqlite3.connect(self.caminho_sqlite)

    def listar_cupons_pdv(self, data_ini: date, data_fim: date) -> List[AuditoriaCupomDTO]:
        conn_sqlite = self._get_conexao_sqlite()
        cursor = conn_sqlite.cursor()

        sql = """
            SELECT nf.empcod, nf.entcod, substr(e.entnome, 1, 45) as entnome,
                   nf.ctrldfserie, nf.nfnum, nf.nfvaltotnota,
                   (CASE WHEN (SELECT count(1) FROM nota_fiscal_eletronica_trans WHERE nfnum = nf.nfnum) > 0
                         THEN 'Transmitiu' ELSE 'Não Transmitiu' END) AS sefaz,
                   nf.nfinteg, nf.nfintegfin, nf.nfintegfisc, nf.nfbxaestq
            FROM nota_fiscal nf
            INNER JOIN entidade e ON nf.entcod = e.entcod
            WHERE date(nf.nfdataemis) BETWEEN date(?) AND date(?)
            ORDER BY nf.nfnum ASC
        """
        cursor.execute(sql, [str(data_ini), str(data_fim)])
        cupons = []
        for r in cursor.fetchall():
            cupons.append(
                AuditoriaCupomDTO(
                    empresa_cod=str(r[0]).strip(),
                    entidade_cod=str(r[1]).strip(),
                    entidade_nome=str(r[2]).strip(),
                    serie=str(r[3]).strip(),
                    numero=str(r[4]).strip(),
                    valor_total=float(r[5]) if r[5] is not None else 0.0,
                    status_sefaz=str(r[6]).strip(),
                    integrado_alvo=str(r[7]).strip().lower() in ("sim", "s", "true", "1"),
                    integrado_financ=str(r[8]).strip().lower() in ("sim", "s", "true", "1"),
                    integrado_fiscal=str(r[9]).strip().lower() in ("sim", "s", "true", "1"),
                    baixou_estoque=str(r[10]).strip().lower() in ("sim", "s", "true", "1"),
                )
            )
        conn_sqlite.close()
        return cupons

    def verificar_cupom_no_apolo(self, nf_num: str, serie: str) -> bool:
        cursor = self._get_cursor_apolo()
        sql = "SELECT TOP 1 1 FROM nota_fiscal WITH (NOLOCK) WHERE nfnum = ? AND ctrldfserie = ?"
        cursor.execute(sql, [nf_num.strip(), serie.strip()])
        return cursor.fetchone() is not None

    def atualizar_flags_pdv(
        self, nf_num: str, integrado: str = "Sim", financ: str = "Sim", fiscal: str = "Sim", estoque: str = "Sim"
    ) -> bool:
        conn_sqlite = self._get_conexao_sqlite()
        cursor = conn_sqlite.cursor()
        sql = """
            UPDATE nota_fiscal
            SET nfinteg = ?, nfintegfin = ?, nfintegfisc = ?, nfbxaestq = ?
            WHERE nfnum = ?
        """
        cursor.execute(sql, [integrado, financ, fiscal, estoque, nf_num.strip()])
        linhas = cursor.rowcount
        conn_sqlite.commit()
        conn_sqlite.close()
        return linhas > 0
