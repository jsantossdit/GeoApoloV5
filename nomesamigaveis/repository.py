"""
Repositório de Dados para Nomes Amigáveis de Objetos (USER_geoapolo_objetos).
GeoApolo V5
Clean Architecture: Suporte híbrido a SQL Server nativo (WITH NOLOCK) e SQLite em memória.
"""

import logging
from typing import List, Optional

from entidades.database import obter_conexao_banco
from .models import ObjetoSistemaDTO

logger = logging.getLogger(__name__)


class NomesAmigaveisRepository:
    """Repositório de persistência para nomes amigáveis de objetos e controles."""

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

    def listar_objetos(self, categoria: str = "", filtro: str = "") -> List[ObjetoSistemaDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()

        cat_limpa = (categoria or "").strip()
        filtro_limpo = (filtro or "").strip()

        clausulas = ["1=1"]
        params = []

        if cat_limpa and cat_limpa.upper() != "TODAS":
            clausulas.append("UPPER(COALESCE(categoria, 'Geral')) = UPPER(?)")
            params.append(cat_limpa)

        if filtro_limpo:
            clausulas.append("(UPPER(nome_objeto) LIKE UPPER(?) OR UPPER(nome_amigavel) LIKE UPPER(?))")
            termo = f"%{filtro_limpo}%"
            params.extend([termo, termo])

        where_clause = " AND ".join(clausulas)
        sql = f"""
            SELECT nome_objeto, nome_amigavel, COALESCE(categoria, 'Geral') AS categoria
            FROM USER_geoapolo_objetos {nolock}
            WHERE {where_clause}
            ORDER BY categoria ASC, nome_amigavel ASC, nome_objeto ASC
        """
        cursor.execute(sql, params)

        return [
            ObjetoSistemaDTO(
                nome_objeto=str(r[0] or "").strip(),
                nome_amigavel=str(r[1] or "").strip(),
                categoria=str(r[2] or "Geral").strip(),
            )
            for r in cursor.fetchall()
        ]

    def obter_objeto(self, nome_objeto: str) -> Optional[ObjetoSistemaDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT nome_objeto, nome_amigavel, COALESCE(categoria, 'Geral') AS categoria
            FROM USER_geoapolo_objetos {nolock}
            WHERE UPPER(nome_objeto) = UPPER(?)
        """
        cursor.execute(sql, [nome_objeto.strip()])
        r = cursor.fetchone()
        if not r:
            return None

        return ObjetoSistemaDTO(
            nome_objeto=str(r[0] or "").strip(),
            nome_amigavel=str(r[1] or "").strip(),
            categoria=str(r[2] or "Geral").strip(),
        )

    def salvar_objeto(self, dto: ObjetoSistemaDTO) -> bool:
        cursor = self._get_cursor()
        cursor.execute(
            "SELECT 1 FROM USER_geoapolo_objetos WHERE UPPER(nome_objeto) = UPPER(?)",
            [dto.nome_objeto.strip()],
        )
        existe = cursor.fetchone() is not None

        categ = dto.categoria.strip() or "Geral"
        if existe:
            sql = """
                UPDATE USER_geoapolo_objetos
                SET nome_amigavel = ?, categoria = ?
                WHERE UPPER(nome_objeto) = UPPER(?)
            """
            cursor.execute(sql, [dto.nome_amigavel.strip(), categ, dto.nome_objeto.strip()])
        else:
            sql = """
                INSERT INTO USER_geoapolo_objetos (nome_objeto, nome_amigavel, categoria)
                VALUES (?, ?, ?)
            """
            cursor.execute(sql, [dto.nome_objeto.strip(), dto.nome_amigavel.strip(), categ])

        self.commit()
        return True

    def atualizar_nome_amigavel(self, nome_objeto: str, nome_amigavel: str, categoria: str) -> bool:
        cursor = self._get_cursor()
        categ = categoria.strip() or "Geral"
        sql = """
            UPDATE USER_geoapolo_objetos
            SET nome_amigavel = ?, categoria = ?
            WHERE UPPER(nome_objeto) = UPPER(?)
        """
        cursor.execute(sql, [nome_amigavel.strip(), categ, nome_objeto.strip()])
        self.commit()
        return True

    def listar_categorias(self) -> List[str]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT DISTINCT COALESCE(categoria, 'Geral') AS cat
            FROM USER_geoapolo_objetos {nolock}
            ORDER BY cat ASC
        """
        cursor.execute(sql)
        categorias = [str(r[0]).strip() for r in cursor.fetchall() if r[0]]
        return categorias or ["Geral"]
