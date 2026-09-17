"""
Repositório de Dados para Cores de Produtos (USER_geoapolo_produto_cores).
GeoApolo V5
Clean Architecture: Suporte híbrido a SQL Server nativo (WITH NOLOCK) e SQLite em memória.
"""

import logging
from typing import List, Optional
from entidades.database import obter_conexao_banco
from .models import CorDTO

logger = logging.getLogger(__name__)


class CoresRepository:
    """Repositório de persistência para cores de produtos."""

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

    def obter_proximo_codigo(self) -> int:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"SELECT COALESCE(MAX(codigo_cor), 0) + 1 AS proximo FROM USER_geoapolo_produto_cores {nolock}"
        cursor.execute(sql)
        row = cursor.fetchone()
        return int(row[0]) if row and row[0] is not None else 1

    def listar_cores(self) -> List[CorDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"SELECT codigo_cor, descricao_cor FROM USER_geoapolo_produto_cores {nolock} ORDER BY codigo_cor ASC"
        cursor.execute(sql)
        return [
            CorDTO(codigo_cor=int(r[0]), descricao_cor=str(r[1] or "").strip())
            for r in cursor.fetchall()
        ]

    def obter_cor(self, codigo: int) -> Optional[CorDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"SELECT codigo_cor, descricao_cor FROM USER_geoapolo_produto_cores {nolock} WHERE codigo_cor = ?"
        cursor.execute(sql, [codigo])
        r = cursor.fetchone()
        if not r:
            return None
        return CorDTO(codigo_cor=int(r[0]), descricao_cor=str(r[1] or "").strip())

    def existe_descricao(self, descricao: str, codigo_ignorar: int = 0) -> bool:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT COUNT(1) FROM USER_geoapolo_produto_cores {nolock}
            WHERE UPPER(RTRIM(LTRIM(descricao_cor))) = UPPER(RTRIM(LTRIM(?)))
              AND codigo_cor <> ?
        """
        cursor.execute(sql, [descricao, codigo_ignorar])
        row = cursor.fetchone()
        return (row[0] if row else 0) > 0

    def salvar_cor(self, cor: CorDTO) -> bool:
        cursor = self._get_cursor()
        cursor.execute("SELECT 1 FROM USER_geoapolo_produto_cores WHERE codigo_cor = ?", [cor.codigo_cor])
        existe = cursor.fetchone() is not None
        if existe:
            sql = "UPDATE USER_geoapolo_produto_cores SET descricao_cor = ? WHERE codigo_cor = ?"
            cursor.execute(sql, [cor.descricao_cor, cor.codigo_cor])
        else:
            sql = "INSERT INTO USER_geoapolo_produto_cores (codigo_cor, descricao_cor) VALUES (?, ?)"
            cursor.execute(sql, [cor.codigo_cor, cor.descricao_cor])
        self.commit()
        return True

    def excluir_cor(self, codigo: int) -> bool:
        cursor = self._get_cursor()
        cursor.execute("DELETE FROM USER_geoapolo_produto_cores WHERE codigo_cor = ?", [codigo])
        self.commit()
        return True
