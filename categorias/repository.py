"""
Repositório de Dados para Relacionamento de Usuários e Grupos com Categorias e Entidades.
Preserva as otimizações SQL Server e hints WITH (NOLOCK).
"""

import logging
from typing import List, Dict, Any, Optional
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

    def listar_todas_categorias(self) -> List[Dict[str, Any]]:
        """Retorna todas as categorias cadastradas na base USER_geoapolo_categoria."""
        cursor = self._get_cursor()
        sql = """
            SELECT
                geocategcodestr AS codigo,
                geocategnome AS descricao,
                ISNULL(geocateggrupo, 'N') AS grupo,
                ISNULL(geocategcodalt, '') AS codigo_alternativo
            FROM USER_geoapolo_categoria WITH (NOLOCK)
            ORDER BY geocategcodestr ASC
        """
        try:
            cursor.execute(sql)
            cols = [col[0].lower() for col in cursor.description]
            res = []
            for row in cursor.fetchall():
                d = dict(zip(cols, row))
                if "geocategcodestr" in d and "codigo" not in d:
                    d["codigo"] = d["geocategcodestr"]
                if "geocategnome" in d and "descricao" not in d:
                    d["descricao"] = d["geocategnome"]
                if "geocateggrupo" in d and "grupo" not in d:
                    d["grupo"] = d["geocateggrupo"]
                if "geocategcodalt" in d and "codigo_alternativo" not in d:
                    d["codigo_alternativo"] = d["geocategcodalt"]
                res.append(d)
            return res
        except Exception as exc:
            logger.warning("Falha ao listar todas as categorias: %s", exc)
            return []

    def obter_categoria(self, codigo_estruturado: str) -> Optional[Dict[str, Any]]:
        """Busca uma categoria específica pelo código estruturado."""
        cursor = self._get_cursor()
        sql = """
            SELECT
                geocategcodestr AS codigo,
                geocategnome AS descricao,
                ISNULL(geocateggrupo, 'N') AS grupo,
                ISNULL(geocategcodalt, '') AS codigo_alternativo
            FROM USER_geoapolo_categoria WITH (NOLOCK)
            WHERE geocategcodestr = ?
        """
        try:
            cursor.execute(sql, [codigo_estruturado])
            row = cursor.fetchone()
            if not row:
                return None
            cols = [col[0].lower() for col in cursor.description]
            d = dict(zip(cols, row))
            if "geocategcodestr" in d and "codigo" not in d:
                d["codigo"] = d["geocategcodestr"]
            if "geocategnome" in d and "descricao" not in d:
                d["descricao"] = d["geocategnome"]
            if "geocateggrupo" in d and "grupo" not in d:
                d["grupo"] = d["geocateggrupo"]
            if "geocategcodalt" in d and "codigo_alternativo" not in d:
                d["codigo_alternativo"] = d["geocategcodalt"]
            return d
        except Exception as exc:
            logger.warning("Falha ao obter categoria %s: %s", codigo_estruturado, exc)
            return None

    def obter_proximo_codigo_alternativo(self) -> str:
        """Obtém o próximo código sequencial de categoria via geoapolo_configcod ou MAX."""
        try:
            from core.recursos import geoapolo_configcod
            cod = geoapolo_configcod("1.01", "USER_geoapolo_categoria", "Sim", connection=self._conn)
            if cod:
                return str(cod).strip()
        except Exception:
            pass

        cursor = self._get_cursor()
        try:
            cursor.execute("""
                SELECT ISNULL(MAX(CAST(geocategcodalt AS INT)), 0) + 1
                  FROM USER_geoapolo_categoria WITH (NOLOCK)
                 WHERE ISNUMERIC(geocategcodalt) = 1
            """)
            val = cursor.fetchone()[0]
            return str(val) if val else "1"
        except Exception:
            return "1"

    def salvar_categoria(self, dados: Dict[str, Any], modo_inclusao: bool = True) -> bool:
        """Insere ou atualiza uma categoria na base USER_geoapolo_categoria."""
        cursor = self._get_cursor()
        cod_estr = str(dados.get("codigo") or dados.get("geocategcodestr") or "").strip().upper()
        nome = str(dados.get("descricao") or dados.get("geocategnome") or "").strip().upper()
        cod_alt = str(dados.get("codigo_alternativo") or dados.get("geocategcodalt") or "").strip()
        grupo = "S" if str(dados.get("grupo") or dados.get("geocateggrupo") or "").upper().startswith("S") else "N"
        cod_antigo = str(dados.get("codigo_antigo") or cod_estr).strip()

        if modo_inclusao:
            sql = """
                INSERT INTO USER_geoapolo_categoria (
                    geocategcodestr, geocategcodalt, geocategnome, geocategcodniv, geocateggrupo, geoempcod
                ) VALUES (?, ?, ?, 'F', ?, '01')
            """
            cursor.execute(sql, [cod_estr, cod_alt, nome, grupo])
        else:
            sql = """
                UPDATE USER_geoapolo_categoria
                   SET geocategcodestr = ?, geocategcodalt = ?, geocategnome = ?, geocateggrupo = ?
                 WHERE geocategcodestr = ?
            """
            cursor.execute(sql, [cod_estr, cod_alt, nome, grupo, cod_antigo])

        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def excluir_categoria(self, codigo_estruturado: str) -> bool:
        """Remove a categoria pelo código estruturado."""
        cursor = self._get_cursor()
        cursor.execute("DELETE FROM USER_geoapolo_categoria WHERE geocategcodestr = ?", [codigo_estruturado])
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

