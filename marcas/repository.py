"""
Repositório de Dados para Marcas de Produtos (USER_geoapolo_produto_marcas).
GeoApolo V5
Clean Architecture: Suporte híbrido a SQL Server nativo (WITH NOLOCK) e SQLite em memória.
"""

import logging
from typing import List, Optional
from entidades.database import obter_conexao_banco
from .models import MarcaDTO

logger = logging.getLogger(__name__)


class MarcasRepository:
    """Repositório de persistência para marcas de produtos."""

    def __init__(self, connection=None):
        self._conn = connection

    def _get_cursor(self):
        if self._conn is None:
            self._conn = obter_conexao_banco()
        return self._conn.cursor()

    @property
    def _is_sql_server(self) -> bool:
        return self._conn is not None and not hasattr(self._conn, "isolation_level")

    def _nolock(self) -> str:
        return "WITH (NOLOCK)" if self._is_sql_server else ""

    def commit(self):
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()

    def rollback(self):
        if self._conn and hasattr(self._conn, "rollback"):
            self._conn.rollback()

    @property
    def _tabela_marcas(self) -> str:
        """Determina dinamicamente a tabela que armazena o catálogo de marcas com a coluna descricao_marca."""
        if not hasattr(self, "_cached_tabela_marcas"):
            cursor = self._get_cursor()
            tab = "USER_geoapolo_produto_marcas"
            for t in ("USER_geoapolo_marcas", "USER_geoapolo_produto_marcas"):
                try:
                    cursor.execute(f"SELECT descricao_marca FROM {t} WHERE 1 = 0")
                    tab = t
                    break
                except Exception:
                    pass
            self._cached_tabela_marcas = tab
        return self._cached_tabela_marcas

    def obter_proximo_codigo(self) -> int:
        cursor = self._get_cursor()
        nolock = self._nolock()
        tab = self._tabela_marcas
        sql = f"SELECT COALESCE(MAX(codigo_marca), 0) + 1 AS proximo FROM {tab} {nolock}"
        cursor.execute(sql)
        row = cursor.fetchone()
        return int(row[0]) if row and row[0] is not None else 1

    def listar_marcas(self) -> List[MarcaDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        tab = self._tabela_marcas
        sql = f"SELECT codigo_marca, descricao_marca FROM {tab} {nolock} ORDER BY codigo_marca ASC"
        cursor.execute(sql)
        return [
            MarcaDTO(codigo_marca=int(r[0]), descricao_marca=str(r[1] or "").strip())
            for r in cursor.fetchall()
        ]

    def obter_marca(self, codigo: int) -> Optional[MarcaDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        tab = self._tabela_marcas
        sql = f"SELECT codigo_marca, descricao_marca FROM {tab} {nolock} WHERE codigo_marca = ?"
        cursor.execute(sql, [codigo])
        r = cursor.fetchone()
        if not r:
            return None
        return MarcaDTO(codigo_marca=int(r[0]), descricao_marca=str(r[1] or "").strip())

    def obter_por_descricao(self, descricao: str) -> Optional[MarcaDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        tab = self._tabela_marcas
        sql = f"""
            SELECT codigo_marca, descricao_marca FROM {tab} {nolock}
            WHERE UPPER(RTRIM(LTRIM(descricao_marca))) = UPPER(RTRIM(LTRIM(?)))
        """
        cursor.execute(sql, [descricao])
        r = cursor.fetchone()
        if not r:
            return None
        return MarcaDTO(codigo_marca=int(r[0]), descricao_marca=str(r[1] or "").strip())

    def existe_descricao(self, descricao: str, codigo_ignorar: int = 0) -> bool:
        cursor = self._get_cursor()
        nolock = self._nolock()
        tab = self._tabela_marcas
        sql = f"""
            SELECT COUNT(1) FROM {tab} {nolock}
            WHERE UPPER(RTRIM(LTRIM(descricao_marca))) = UPPER(RTRIM(LTRIM(?)))
              AND codigo_marca <> ?
        """
        cursor.execute(sql, [descricao, codigo_ignorar])
        row = cursor.fetchone()
        return (row[0] if row else 0) > 0

    def salvar_marca(self, marca: MarcaDTO) -> bool:
        cursor = self._get_cursor()
        tab = self._tabela_marcas
        cursor.execute(f"SELECT 1 FROM {tab} WHERE codigo_marca = ?", [marca.codigo_marca])
        existe = cursor.fetchone() is not None
        if existe:
            sql = f"UPDATE {tab} SET descricao_marca = ? WHERE codigo_marca = ?"
            cursor.execute(sql, [marca.descricao_marca, marca.codigo_marca])
        else:
            sql = f"INSERT INTO {tab} (codigo_marca, descricao_marca) VALUES (?, ?)"
            cursor.execute(sql, [marca.codigo_marca, marca.descricao_marca])
        self.commit()
        return True

    def excluir_marca(self, codigo: int) -> bool:
        cursor = self._get_cursor()
        tab = self._tabela_marcas
        cursor.execute(f"DELETE FROM {tab} WHERE codigo_marca = ?", [codigo])
        self.commit()
        return True
