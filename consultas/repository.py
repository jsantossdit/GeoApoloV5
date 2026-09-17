"""
Repositório de dados para Consultas Dinâmicas e Gestão de Permissões de Consultas.
GeoApolo V5
Compatível com SQL Server nativo (WITH NOLOCK) e SQLite em memória.
"""

from typing import List, Optional, Tuple, Any
from consultas.models import ConsultaConfigDTO, PermissaoConsultaDTO, ResultadoConsultaDTO


class ConsultasRepository:
    """Repositório de persistência e execução de Consultas Dinâmicas."""

    def __init__(self, connection):
        self.conn = connection
        self._is_sql_server = not hasattr(connection, "isolation_level")

    def _nolock(self) -> str:
        return "WITH (NOLOCK)" if self._is_sql_server else ""

    def listar_consultas(self) -> List[ConsultaConfigDTO]:
        """Lista todas as consultas dinâmicas cadastradas."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT codigo_consulta, descricao_consulta, sql_consulta, tipo_consulta, banco_consulta
            FROM USER_geoapolo_consultas {nolock}
            ORDER BY descricao_consulta ASC
        """
        cur.execute(sql)
        return [
            ConsultaConfigDTO(
                codigo_consulta=str(r[0]),
                descricao_consulta=str(r[1] or ""),
                sql_consulta=str(r[2] or ""),
                tipo_consulta=str(r[3] or "T"),
                banco_consulta=str(r[4] or "Apolo"),
            )
            for r in cur.fetchall()
        ]

    def obter_consulta(self, codigo_consulta: str) -> Optional[ConsultaConfigDTO]:
        """Localiza configuração de consulta pelo código."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT codigo_consulta, descricao_consulta, sql_consulta, tipo_consulta, banco_consulta
            FROM USER_geoapolo_consultas {nolock}
            WHERE codigo_consulta = ?
        """
        cur.execute(sql, [codigo_consulta])
        r = cur.fetchone()
        if not r:
            return None
        return ConsultaConfigDTO(
            codigo_consulta=str(r[0]),
            descricao_consulta=str(r[1] or ""),
            sql_consulta=str(r[2] or ""),
            tipo_consulta=str(r[3] or "T"),
            banco_consulta=str(r[4] or "Apolo"),
        )

    def salvar_consulta(self, c: ConsultaConfigDTO) -> bool:
        """Cria ou atualiza uma consulta configurável."""
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM USER_geoapolo_consultas WHERE codigo_consulta = ?", [c.codigo_consulta])
        if cur.fetchone():
            sql = """
                UPDATE USER_geoapolo_consultas
                SET descricao_consulta = ?, sql_consulta = ?, tipo_consulta = ?, banco_consulta = ?
                WHERE codigo_consulta = ?
            """
            cur.execute(sql, [c.descricao_consulta, c.sql_consulta, c.tipo_consulta, c.banco_consulta, c.codigo_consulta])
        else:
            sql = """
                INSERT INTO USER_geoapolo_consultas (codigo_consulta, descricao_consulta, sql_consulta, tipo_consulta, banco_consulta)
                VALUES (?, ?, ?, ?, ?)
            """
            cur.execute(sql, [c.codigo_consulta, c.descricao_consulta, c.sql_consulta, c.tipo_consulta, c.banco_consulta])
        self.conn.commit()
        return True

    def excluir_consulta(self, codigo_consulta: str) -> bool:
        """Remove consulta e suas permissões associadas."""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM USER_geoapolo_permissaoconsulta WHERE codigo_consulta = ?", [codigo_consulta])
        cur.execute("DELETE FROM USER_geoapolo_consultas WHERE codigo_consulta = ?", [codigo_consulta])
        self.conn.commit()
        return True

    def listar_permissoes_consulta(self, codigo_consulta: str) -> List[PermissaoConsultaDTO]:
        """Lista permissões de usuários para determinada consulta."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT p.usucod, p.codigo_consulta, COALESCE(c.descricao_consulta, ''), p.autorizacao
            FROM USER_geoapolo_permissaoconsulta p {nolock}
            LEFT JOIN USER_geoapolo_consultas c {nolock} ON p.codigo_consulta = c.codigo_consulta
            WHERE p.codigo_consulta = ?
            ORDER BY p.usucod ASC
        """
        cur.execute(sql, [codigo_consulta])
        return [
            PermissaoConsultaDTO(
                usucod=str(r[0]),
                codigo_consulta=str(r[1]),
                descricao_consulta=str(r[2]),
                autorizacao=str(r[3] or "S"),
            )
            for r in cur.fetchall()
        ]

    def atualizar_permissao_consulta(self, usucod: str, codigo_consulta: str, autorizacao: str) -> bool:
        """Define se o usuário está autorizado a ver os dados da consulta."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT 1 FROM USER_geoapolo_permissaoconsulta WHERE usucod = ? AND codigo_consulta = ?",
            [usucod, codigo_consulta],
        )
        if cur.fetchone():
            cur.execute(
                "UPDATE USER_geoapolo_permissaoconsulta SET autorizacao = ? WHERE usucod = ? AND codigo_consulta = ?",
                [autorizacao, usucod, codigo_consulta],
            )
        else:
            cur.execute(
                "INSERT INTO USER_geoapolo_permissaoconsulta (usucod, codigo_consulta, autorizacao) VALUES (?, ?, ?)",
                [usucod, codigo_consulta, autorizacao],
            )
        self.conn.commit()
        return True

    def executar_sql_dinamico(self, sql: str, params: List[Any]) -> ResultadoConsultaDTO:
        """Executa instrução SQL parametrizada retornando colunas e linhas."""
        cur = self.conn.cursor()
        try:
            cur.execute(sql, params)
            colunas = [d[0] for d in cur.description] if cur.description else []
            linhas = cur.fetchall()
            return ResultadoConsultaDTO(
                colunas=colunas,
                linhas=[list(r) for r in linhas],
                total_registros=len(linhas),
                sucesso=True,
            )
        except Exception as exc:
            return ResultadoConsultaDTO(
                colunas=[],
                linhas=[],
                total_registros=0,
                sucesso=False,
                mensagem=f"Erro na execução da consulta: {str(exc)}",
            )
