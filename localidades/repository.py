"""
Repositório de Acesso a Dados para Cidades, Distritos e Localidades.
GeoApolo V5
"""

import logging
from typing import List, Optional
from entidades.database import obter_conexao_banco
from .models import CidadeDistritoDTO, EntidadeLocalidadeDTO

logger = logging.getLogger(__name__)


class LocalidadesRepository:
    """Consultas e correções cadastrais na base SQL Server Apolo com WITH (NOLOCK)."""

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

    def listar_cidades(self, termo: str = "", uf: str = "") -> List[CidadeDistritoDTO]:
        cursor = self._get_cursor()
        sql = """
            SELECT c.cidcod, c.cidnomecomp, ISNULL(c.ufsigla, ''),
                   ISNULL(c.cidibge, ''),
                   (SELECT COUNT(1) FROM entidade e WITH (NOLOCK) WHERE e.cidcod = c.cidcod) AS total_ent
            FROM cidade c WITH (NOLOCK)
            WHERE 1=1
        """
        params = []
        if termo and termo.strip():
            sql += " AND c.cidnomecomp LIKE ?"
            params.append(f"%{termo.strip()}%")
        if uf and uf.strip():
            sql += " AND c.ufsigla = ?"
            params.append(uf.strip().upper())

        sql += " ORDER BY c.cidnomecomp ASC"
        cursor.execute(sql, params)

        resultados = []
        for r in cursor.fetchall():
            resultados.append(
                CidadeDistritoDTO(
                    cid_cod=str(r[0]).strip(),
                    nome=str(r[1]).strip(),
                    uf=str(r[2]).strip(),
                    ibge=str(r[3]).strip(),
                    total_entidades=int(r[4]),
                )
            )
        return resultados

    def listar_entidades_por_cidade(self, cid_cod: str) -> List[EntidadeLocalidadeDTO]:
        cursor = self._get_cursor()
        sql = """
            SELECT entcod, entnome, ISNULL(entcpf, ISNULL(entcnpj, '')),
                   ISNULL(entcep, ''), ISNULL(entend, ''), ISNULL(entbairro, '')
            FROM entidade WITH (NOLOCK)
            WHERE cidcod = ?
            ORDER BY entnome ASC
        """
        cursor.execute(sql, [cid_cod.strip()])
        resultados = []
        for r in cursor.fetchall():
            resultados.append(
                EntidadeLocalidadeDTO(
                    ent_cod=str(r[0]).strip(),
                    nome=str(r[1]).strip(),
                    documento=str(r[2]).strip(),
                    cep=str(r[3]).strip(),
                    endereco=str(r[4]).strip(),
                    bairro=str(r[5]).strip(),
                )
            )
        return resultados

    def obter_cidade(self, cid_cod: str) -> Optional[CidadeDistritoDTO]:
        cursor = self._get_cursor()
        sql = """
            SELECT cidcod, cidnomecomp, ISNULL(ufsigla, ''), ISNULL(cidibge, '')
            FROM cidade WITH (NOLOCK)
            WHERE cidcod = ?
        """
        cursor.execute(sql, [cid_cod.strip()])
        r = cursor.fetchone()
        if r:
            return CidadeDistritoDTO(
                cid_cod=str(r[0]).strip(),
                nome=str(r[1]).strip(),
                uf=str(r[2]).strip(),
                ibge=str(r[3]).strip(),
            )
        return None

    def migrar_entidades(self, cid_origem: str, cid_destino: str) -> int:
        cursor = self._get_cursor()
        try:
            sql = "UPDATE entidade SET cidcod = ? WHERE cidcod = ?"
            cursor.execute(sql, [cid_destino.strip(), cid_origem.strip()])
            afetados = cursor.rowcount if cursor.rowcount > 0 else 0
            self.commit()
            return afetados
        except Exception as e:
            self.rollback()
            logger.exception("Erro ao migrar entidades entre localidades: %s", e)
            raise e
