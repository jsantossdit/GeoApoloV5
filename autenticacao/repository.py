"""
Repositório de Dados para Autenticação e Logon.
GeoApolo V5
Clean Architecture: Suporte híbrido a SQL Server nativo (WITH NOLOCK) e SQLite em memória.
"""

import logging
from typing import List, Optional

from entidades.database import obter_conexao_banco

logger = logging.getLogger(__name__)


class AutenticacaoRepository:
    """Acesso ao banco para credenciais de usuários e empresas ativas."""

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

    def obter_usuario_login(self, login: str) -> Optional[dict]:
        """Localiza o usuário por login ou código de acesso."""
        cursor = self._get_cursor()
        nolock = self._nolock()
        login_limpo = (login or "").strip().lower()

        sql = f"""
            SELECT usucod, login, nome_completo, flagativo, senha, senha_alvo
            FROM USER_geoapolo_usuarios {nolock}
            WHERE LOWER(login) = ? OR LOWER(usucod) = ?
        """
        cursor.execute(sql, [login_limpo, login_limpo])
        r = cursor.fetchone()
        if not r:
            return None

        return {
            "usucod": str(r[0] or "").strip(),
            "login": str(r[1] or "").strip(),
            "nome_completo": str(r[2] or "").strip(),
            "flagativo": str(r[3] or "A").strip().upper(),
            "senha": str(r[4] or ""),
            "senha_alvo": str(r[5] or ""),
        }

    def listar_empresas_ativas(self) -> List[dict]:
        """Lista as empresas ativas cadastradas no GeoApolo."""
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT empcod, empnome, empcod_apolo
            FROM USER_geoapolo_empresas {nolock}
            WHERE COALESCE(flagativo, 'S') = 'S'
            ORDER BY empcod ASC
        """
        cursor.execute(sql)
        empresas = []
        for r in cursor.fetchall():
            empresas.append({
                "empcod": str(r[0] or "").strip(),
                "empnome": str(r[1] or "").strip(),
                "empcod_apolo": str(r[2] or "").strip(),
            })
        return empresas

    def obter_empresa(self, empcod: str) -> Optional[dict]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT empcod, empnome, empcod_apolo
            FROM USER_geoapolo_empresas {nolock}
            WHERE empcod = ?
        """
        cursor.execute(sql, [empcod.strip()])
        r = cursor.fetchone()
        if not r:
            return None
        return {
            "empcod": str(r[0] or "").strip(),
            "empnome": str(r[1] or "").strip(),
            "empcod_apolo": str(r[2] or "").strip(),
        }
