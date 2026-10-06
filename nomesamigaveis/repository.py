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

    def _get_connection(self):
        if self._conn is None:
            self._conn = obter_conexao_banco()
        return self._conn

    def _get_cursor(self):
        return self._get_connection().cursor()

    @property
    def _is_sql_server(self) -> bool:
        conn = self._get_connection()
        return conn is not None and not hasattr(conn, "isolation_level")

    def _nolock(self) -> str:
        return "WITH (NOLOCK)" if self._is_sql_server else ""

    def commit(self):
        conn = self._get_connection()
        if conn and hasattr(conn, "commit"):
            conn.commit()

    def rollback(self):
        conn = self._get_connection()
        if conn and hasattr(conn, "rollback"):
            conn.rollback()

    def _obter_colunas(self) -> set:
        try:
            cur = self._get_cursor()
            cur.execute("SELECT * FROM USER_geoapolo_objetos WHERE 1=0")
            if cur.description:
                return {desc[0].lower() for desc in cur.description}
        except Exception:
            pass
        return set()

    def _garantir_estrutura_tabela(self):
        colunas = self._obter_colunas()
        if not colunas:
            return

        cur = self._get_cursor()
        alterou = False

        if "nome_amigavel" not in colunas:
            try:
                cur.execute("ALTER TABLE USER_geoapolo_objetos ADD nome_amigavel VARCHAR(150) NULL")
                if "nome_oficial" in colunas:
                    cur.execute("UPDATE USER_geoapolo_objetos SET nome_amigavel = COALESCE(nome_oficial, nome_objeto) WHERE nome_amigavel IS NULL")
                else:
                    cur.execute("UPDATE USER_geoapolo_objetos SET nome_amigavel = nome_objeto WHERE nome_amigavel IS NULL")
                alterou = True
            except Exception as e:
                logger.warning(f"Não foi possível adicionar coluna nome_amigavel: {e}")

        if "categoria" not in colunas:
            try:
                cur.execute("ALTER TABLE USER_geoapolo_objetos ADD categoria VARCHAR(80) NULL")
                cur.execute("UPDATE USER_geoapolo_objetos SET categoria = 'Geral' WHERE categoria IS NULL")
                alterou = True
            except Exception as e:
                logger.warning(f"Não foi possível adicionar coluna categoria: {e}")

        if alterou:
            try:
                self.commit()
            except Exception:
                pass

    def listar_objetos(self, categoria: str = "", filtro: str = "") -> List[ObjetoSistemaDTO]:
        self._garantir_estrutura_tabela()
        cursor = self._get_cursor()
        nolock = self._nolock()
        colunas = self._obter_colunas()

        cat_limpa = (categoria or "").strip()
        filtro_limpo = (filtro or "").strip()

        tem_cat = "categoria" in colunas
        if tem_cat:
            col_cat = "COALESCE(categoria, 'Geral')"
            order_cat = "categoria ASC, "
        else:
            col_cat = "'Geral'"
            order_cat = ""

        if "nome_amigavel" in colunas and "nome_oficial" in colunas:
            col_amigavel = "COALESCE(nome_amigavel, nome_oficial, nome_objeto)"
        elif "nome_amigavel" in colunas:
            col_amigavel = "COALESCE(nome_amigavel, nome_objeto)"
        elif "nome_oficial" in colunas:
            col_amigavel = "COALESCE(nome_oficial, nome_objeto)"
        else:
            col_amigavel = "nome_objeto"

        clausulas = ["1=1"]
        params = []

        if tem_cat and cat_limpa and cat_limpa.upper() != "TODAS":
            clausulas.append("UPPER(COALESCE(categoria, 'Geral')) = UPPER(?)")
            params.append(cat_limpa)

        if filtro_limpo:
            clausulas.append(f"(UPPER(nome_objeto) LIKE UPPER(?) OR UPPER({col_amigavel}) LIKE UPPER(?))")
            termo = f"%{filtro_limpo}%"
            params.extend([termo, termo])

        where_clause = " AND ".join(clausulas)
        sql = f"""
            SELECT nome_objeto, {col_amigavel} AS nome_amigavel, {col_cat} AS categoria
            FROM USER_geoapolo_objetos {nolock}
            WHERE {where_clause}
            ORDER BY {order_cat} {col_amigavel} ASC, nome_objeto ASC
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
        self._garantir_estrutura_tabela()
        cursor = self._get_cursor()
        nolock = self._nolock()
        colunas = self._obter_colunas()

        col_cat = "COALESCE(categoria, 'Geral')" if "categoria" in colunas else "'Geral'"
        if "nome_amigavel" in colunas and "nome_oficial" in colunas:
            col_amigavel = "COALESCE(nome_amigavel, nome_oficial, nome_objeto)"
        elif "nome_amigavel" in colunas:
            col_amigavel = "COALESCE(nome_amigavel, nome_objeto)"
        elif "nome_oficial" in colunas:
            col_amigavel = "COALESCE(nome_oficial, nome_objeto)"
        else:
            col_amigavel = "nome_objeto"

        sql = f"""
            SELECT nome_objeto, {col_amigavel} AS nome_amigavel, {col_cat} AS categoria
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
        self._garantir_estrutura_tabela()
        cursor = self._get_cursor()
        cursor.execute(
            "SELECT 1 FROM USER_geoapolo_objetos WHERE UPPER(nome_objeto) = UPPER(?)",
            [dto.nome_objeto.strip()],
        )
        existe = cursor.fetchone() is not None

        colunas = self._obter_colunas()
        categ = dto.categoria.strip() or "Geral"
        nome_amig = dto.nome_amigavel.strip()

        if existe:
            sets = []
            params = []
            if "nome_amigavel" in colunas:
                sets.append("nome_amigavel = ?")
                params.append(nome_amig)
            if "nome_oficial" in colunas:
                sets.append("nome_oficial = ?")
                params.append(nome_amig)
            if "categoria" in colunas:
                sets.append("categoria = ?")
                params.append(categ)

            if sets:
                params.append(dto.nome_objeto.strip())
                sql = f"UPDATE USER_geoapolo_objetos SET {', '.join(sets)} WHERE UPPER(nome_objeto) = UPPER(?)"
                cursor.execute(sql, params)
        else:
            campos = ["nome_objeto"]
            params = [dto.nome_objeto.strip()]
            if "nome_amigavel" in colunas:
                campos.append("nome_amigavel")
                params.append(nome_amig)
            if "nome_oficial" in colunas:
                campos.append("nome_oficial")
                params.append(nome_amig)
            if "categoria" in colunas:
                campos.append("categoria")
                params.append(categ)

            cols_str = ", ".join(campos)
            placeholders = ", ".join("?" for _ in campos)
            sql = f"INSERT INTO USER_geoapolo_objetos ({cols_str}) VALUES ({placeholders})"
            cursor.execute(sql, params)

        self.commit()
        return True

    def atualizar_nome_amigavel(self, nome_objeto: str, nome_amigavel: str, categoria: str) -> bool:
        self._garantir_estrutura_tabela()
        cursor = self._get_cursor()
        colunas = self._obter_colunas()
        categ = categoria.strip() or "Geral"
        nome_amig = nome_amigavel.strip()

        sets = []
        params = []
        if "nome_amigavel" in colunas:
            sets.append("nome_amigavel = ?")
            params.append(nome_amig)
        if "nome_oficial" in colunas:
            sets.append("nome_oficial = ?")
            params.append(nome_amig)
        if "categoria" in colunas:
            sets.append("categoria = ?")
            params.append(categ)

        if sets:
            params.append(nome_objeto.strip())
            sql = f"UPDATE USER_geoapolo_objetos SET {', '.join(sets)} WHERE UPPER(nome_objeto) = UPPER(?)"
            cursor.execute(sql, params)
            self.commit()
        return True

    def listar_categorias(self) -> List[str]:
        self._garantir_estrutura_tabela()
        colunas = self._obter_colunas()
        if "categoria" not in colunas:
            return ["Geral"]

        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT DISTINCT COALESCE(categoria, 'Geral') AS cat
            FROM USER_geoapolo_objetos {nolock}
            WHERE categoria IS NOT NULL AND RTRIM(LTRIM(categoria)) <> ''
            ORDER BY cat ASC
        """
        cursor.execute(sql)
        categorias = [str(r[0]).strip() for r in cursor.fetchall() if r[0]]
        return categorias or ["Geral"]
