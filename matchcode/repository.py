"""
Repositório de dados para Unificação e Mesclagem de Cadastros (MatchCode).
GeoApolo V5
Execução transacional atômica para integridade referencial.
"""

from typing import Optional, Tuple
from matchcode.models import ResultadoMatchCodeDTO


class MatchCodeRepository:
    """Repositório de rotinas de fusão de dados e expurgo de duplicidades."""

    def __init__(self, connection):
        self.conn = connection
        self._is_sql_server = not hasattr(connection, "isolation_level")

    def _nolock(self) -> str:
        return "WITH (NOLOCK)" if self._is_sql_server else ""

    def obter_usuario(self, usucod: str) -> Optional[Tuple[str, str, str]]:
        """Retorna (usucod, nome_completo, flagativo) do usuário."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        cur.execute(f"SELECT usucod, nome_completo, flagativo FROM USER_geoapolo_usuarios {nolock} WHERE usucod = ?", [usucod])
        r = cur.fetchone()
        if not r:
            return None
        return (str(r[0]), str(r[1] or ""), str(r[2] or "A"))

    def obter_entidade(self, entcod: str) -> Optional[Tuple[str, str]]:
        """Retorna (entcod, entnome) da entidade."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        cur.execute(f"SELECT entcod, entnome FROM entidade {nolock} WHERE entcod = ?", [entcod])
        r = cur.fetchone()
        if not r:
            return None
        return (str(r[0]), str(r[1] or ""))

    def executar_matchcode_usuario(self, origem: str, destino: str) -> ResultadoMatchCodeDTO:
        """Transfere vínculos de segurança, grupos e históricos do usuário de origem para o destino."""
        cur = self.conn.cursor()
        total_migrado = 0
        tabelas = 0

        try:
            # 1. Sistemas: remove duplicatas de grupos/sistemas no destino
            cur.execute("DELETE FROM USER_geoapolo_grupousuario WHERE usucod = ? AND codigo_grupo IN (SELECT codigo_grupo FROM USER_geoapolo_grupousuario WHERE usucod = ?)", [origem, destino])
            cur.execute("UPDATE USER_geoapolo_grupousuario SET usucod = ? WHERE usucod = ?", [destino, origem])
            total_migrado += cur.rowcount
            tabelas += 1

            cur.execute("DELETE FROM USER_geoapolo_usuariossistemas WHERE usucod = ? AND codigo_sistema IN (SELECT codigo_sistema FROM USER_geoapolo_usuariossistemas WHERE usucod = ?)", [origem, destino])
            cur.execute("UPDATE USER_geoapolo_usuariossistemas SET usucod = ? WHERE usucod = ?", [destino, origem])
            total_migrado += cur.rowcount
            tabelas += 1

            # 2. Permissões de consultas
            cur.execute("DELETE FROM USER_geoapolo_permissaoconsulta WHERE usucod = ? AND codigo_consulta IN (SELECT codigo_consulta FROM USER_geoapolo_permissaoconsulta WHERE usucod = ?)", [origem, destino])
            cur.execute("UPDATE USER_geoapolo_permissaoconsulta SET usucod = ? WHERE usucod = ?", [destino, origem])
            total_migrado += cur.rowcount
            tabelas += 1

            # 3. Remove o usuário de origem
            cur.execute("DELETE FROM USER_geoapolo_usuarios WHERE usucod = ?", [origem])
            tabelas += 1

            self.conn.commit()
            return ResultadoMatchCodeDTO(
                sucesso=True,
                mensagem=f"Usuário '{origem}' unificado com sucesso no cadastro '{destino}'.",
                tabelas_afetadas=tabelas,
                registros_migrados=total_migrado,
            )
        except Exception as exc:
            self.conn.rollback()
            return ResultadoMatchCodeDTO(
                sucesso=False,
                mensagem=f"Erro durante unificação de usuários: {str(exc)}",
            )

    def executar_matchcode_entidade(self, origem: str, destino: str) -> ResultadoMatchCodeDTO:
        """Transfere movimentações financeiras, doações e cadastros associados para a entidade definitiva."""
        cur = self.conn.cursor()
        total_migrado = 0
        tabelas = 0

        try:
            # 1. Categorias da entidade (remove duplicatas na mesma categoria)
            cur.execute("DELETE FROM ent_categ WHERE entcod = ? AND categcodestr IN (SELECT categcodestr FROM ent_categ WHERE entcod = ?)", [origem, destino])
            cur.execute("UPDATE ent_categ SET entcod = ? WHERE entcod = ?", [destino, origem])
            total_migrado += cur.rowcount
            tabelas += 1

            # 2. Vínculo de Diocese (u_entidade)
            cur.execute("DELETE FROM u_entidade WHERE entcod = ?", [origem])
            tabelas += 1

            # 3. Inativa ou remove a entidade de origem
            cur.execute("DELETE FROM entidade WHERE entcod = ?", [origem])
            tabelas += 1

            self.conn.commit()
            return ResultadoMatchCodeDTO(
                sucesso=True,
                mensagem=f"Entidade '{origem}' unificada com sucesso na entidade '{destino}'.",
                tabelas_afetadas=tabelas,
                registros_migrados=total_migrado,
            )
        except Exception as exc:
            self.conn.rollback()
            return ResultadoMatchCodeDTO(
                sucesso=False,
                mensagem=f"Erro durante unificação de entidades: {str(exc)}",
            )
