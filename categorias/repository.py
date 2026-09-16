"""
Repositório de Dados para Relacionamento de Usuários e Grupos com Categorias e Entidades.
Preserva as otimizações SQL Server e hints WITH (NOLOCK).
"""

import logging
from typing import List, Dict, Any
from entidades.database import obter_conexao_banco

logger = logging.getLogger(__name__)


class CategoriaEntidadeRepository:
    """Acesso ao banco para operações de vínculos entre categorias e usuários."""

    def __init__(self, connection=None):
        self._conn = connection

    def _get_cursor(self):
        if self._conn is None:
            self._conn = obter_conexao_banco()
        return self._conn.cursor()

    def listar_usuarios_ativos(self) -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        sql = """
            SELECT usucod, ISNULL(usunome, usucod) AS usunome
            FROM usuario WITH (NOLOCK)
            WHERE UsuStat = 'Ativo'
            ORDER BY usucod ASC
        """
        cursor.execute(sql)
        return [{"codigo": str(r[0]), "nome": str(r[1])} for r in cursor.fetchall()]

    def listar_grupos(self) -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        sql = """
            SELECT GrpUsuCod, ISNULL(GrpUsuNome, GrpUsuCod) AS GrpUsuNome
            FROM grp_usuario WITH (NOLOCK)
            ORDER BY GrpUsuCod ASC
        """
        cursor.execute(sql)
        return [{"codigo": str(r[0]), "descricao": str(r[1])} for r in cursor.fetchall()]

    def listar_usuarios_do_grupo(self, grupo_id: str) -> List[str]:
        cursor = self._get_cursor()
        sql = """
            SELECT gu.usucod
            FROM grp_x_usuario gu WITH (NOLOCK)
            INNER JOIN usuario u WITH (NOLOCK) ON gu.usucod = u.usucod
            WHERE gu.grpusucod = ?
            ORDER BY gu.usucod ASC
        """
        cursor.execute(sql, [grupo_id])
        return [str(r[0]) for r in cursor.fetchall()]

    def listar_categorias_usuario(self, usuario_id: str) -> List[Dict[str, Any]]:
        cursor = self._get_cursor()
        sql = """
            SELECT
                c.categcodestr AS codigo_categoria,
                ISNULL(c.categnome, c.categcodestr) AS descricao,
                ISNULL((SELECT COUNT(ec.entcod) FROM entidade_categ ec WITH (NOLOCK) WHERE ec.categcodestr = c.categcodestr), 0) AS total_entidades,
                CASE WHEN uc.categcodestr IS NOT NULL THEN 1 ELSE 0 END AS vinculada
            FROM categoria c WITH (NOLOCK)
            LEFT JOIN usuario_categ uc WITH (NOLOCK)
                   ON c.categcodestr = uc.categcodestr AND uc.usucod = ?
            ORDER BY c.categcodestr ASC
        """
        cursor.execute(sql, [usuario_id])
        cols = [c[0] for c in cursor.description]
        registros = []
        for row in cursor.fetchall():
            registros.append(dict(zip(cols, row)))
        return registros

    def vincular_categoria_usuario(self, usuario_id: str, categoria_codigo: str) -> bool:
        cursor = self._get_cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM usuario_categ WITH (NOLOCK) WHERE usucod = ? AND categcodestr = ?",
            [usuario_id, categoria_codigo],
        )
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO usuario_categ (usucod, categcodestr, UsuCategTodasEnt) VALUES (?, ?, 'N')",
                [usuario_id, categoria_codigo],
            )
            if self._conn and hasattr(self._conn, "commit"):
                self._conn.commit()
        return True

    def relacionar_entidades_categoria_usuario(self, usuario_id: str, categoria_codigo: str) -> bool:
        cursor = self._get_cursor()
        # Garante o vínculo da categoria primeiro
        self.vincular_categoria_usuario(usuario_id, categoria_codigo)

        sql = """
            INSERT INTO usuario_ent (UsuCod, EntCod, UsuEntRelacAvulso)
            SELECT ?, ec.entcod, 'N'
            FROM entidade_categ ec WITH (NOLOCK)
            WHERE ec.categcodestr = ?
              AND NOT EXISTS (
                  SELECT 1 FROM usuario_ent ue WITH (NOLOCK)
                  WHERE ue.usucod = ? AND ue.entcod = ec.entcod
              )
        """
        cursor.execute(sql, [usuario_id, categoria_codigo, usuario_id])
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def remover_categoria_usuario(self, usuario_id: str, categoria_codigo: str) -> bool:
        cursor = self._get_cursor()
        # Remove entidades associadas
        sql_ent = """
            DELETE FROM usuario_ent
            WHERE usucod = ?
              AND entcod IN (SELECT ec.entcod FROM entidade_categ ec WITH (NOLOCK) WHERE ec.categcodestr = ?)
        """
        cursor.execute(sql_ent, [usuario_id, categoria_codigo])

        # Remove vínculo da categoria
        cursor.execute(
            "DELETE FROM usuario_categ WHERE usucod = ? AND categcodestr = ?",
            [usuario_id, categoria_codigo],
        )
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()
        return True
