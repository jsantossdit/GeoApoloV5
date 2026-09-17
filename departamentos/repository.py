"""
Repositório de Dados para Departamentos e Seções (USER_geoapolo_departamentos).
GeoApolo V5
Clean Architecture: Suporte híbrido a SQL Server nativo (WITH NOLOCK) e SQLite em memória.
"""

import logging
from typing import List, Optional

from entidades.database import obter_conexao_banco
from .models import DepartamentoDTO

logger = logging.getLogger(__name__)


class DepartamentosRepository:
    """Repositório de persistência para departamentos e vínculo com centros de controle."""

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
        sql = f"SELECT COALESCE(MAX(codigo_departamento), 0) + 1 AS proximo FROM USER_geoapolo_departamentos {nolock}"
        cursor.execute(sql)
        row = cursor.fetchone()
        return int(row[0]) if row and row[0] is not None else 1

    def listar_departamentos(self, empcod: str = "", filtro: str = "") -> List[DepartamentoDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()

        emp_limpa = (empcod or "").strip()
        filtro_limpo = (filtro or "").strip()

        clausulas = ["1=1"]
        params = []

        if emp_limpa and emp_limpa.upper() != "TODAS":
            clausulas.append("d.empcod = ?")
            params.append(emp_limpa)

        if filtro_limpo:
            clausulas.append("UPPER(d.nome_departamento) LIKE UPPER(?)")
            params.append(f"%{filtro_limpo}%")

        where_str = " AND ".join(clausulas)
        sql = f"""
            SELECT d.codigo_departamento, d.nome_departamento, d.empcod,
                   COALESCE(e.empnome, '') AS empnome, COALESCE(d.flagativo, 'A') AS flagativo,
                   COALESCE(v.cctrlcodestr, '') AS cctrlcodestr,
                   COALESCE(cc.cctrlnome, '') AS cctrlnome
            FROM USER_geoapolo_departamentos d {nolock}
            LEFT JOIN USER_geoapolo_empresas e {nolock} ON d.empcod = e.empcod
            LEFT JOIN geoapolo_secoescctrlapolo v {nolock} ON d.codigo_departamento = v.codigo_secao
            LEFT JOIN centro_ctrl cc {nolock} ON v.cctrlcodestr = cc.cctrlcodestr
            WHERE {where_str}
            ORDER BY d.codigo_departamento ASC
        """
        cursor.execute(sql, params)

        return [
            DepartamentoDTO(
                codigo_departamento=int(r[0]),
                nome_departamento=str(r[1] or "").strip(),
                empcod=str(r[2] or "").strip(),
                empnome=str(r[3] or "").strip(),
                flagativo=str(r[4] or "A").strip().upper(),
                cctrlcodestr=str(r[5] or "").strip(),
                cctrlnome=str(r[6] or "").strip(),
            )
            for r in cursor.fetchall()
        ]

    def obter_departamento(self, codigo: int) -> Optional[DepartamentoDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT d.codigo_departamento, d.nome_departamento, d.empcod,
                   COALESCE(e.empnome, '') AS empnome, COALESCE(d.flagativo, 'A') AS flagativo,
                   COALESCE(v.cctrlcodestr, '') AS cctrlcodestr,
                   COALESCE(cc.cctrlnome, '') AS cctrlnome
            FROM USER_geoapolo_departamentos d {nolock}
            LEFT JOIN USER_geoapolo_empresas e {nolock} ON d.empcod = e.empcod
            LEFT JOIN geoapolo_secoescctrlapolo v {nolock} ON d.codigo_departamento = v.codigo_secao
            LEFT JOIN centro_ctrl cc {nolock} ON v.cctrlcodestr = cc.cctrlcodestr
            WHERE d.codigo_departamento = ?
        """
        cursor.execute(sql, [codigo])
        r = cursor.fetchone()
        if not r:
            return None

        return DepartamentoDTO(
            codigo_departamento=int(r[0]),
            nome_departamento=str(r[1] or "").strip(),
            empcod=str(r[2] or "").strip(),
            empnome=str(r[3] or "").strip(),
            flagativo=str(r[4] or "A").strip().upper(),
            cctrlcodestr=str(r[5] or "").strip(),
            cctrlnome=str(r[6] or "").strip(),
        )

    def salvar_departamento(self, dto: DepartamentoDTO) -> bool:
        cursor = self._get_cursor()
        cursor.execute("SELECT 1 FROM USER_geoapolo_departamentos WHERE codigo_departamento = ?", [dto.codigo_departamento])
        existe = cursor.fetchone() is not None

        if existe:
            sql = """
                UPDATE USER_geoapolo_departamentos
                SET nome_departamento = ?, empcod = ?, flagativo = ?
                WHERE codigo_departamento = ?
            """
            cursor.execute(sql, [dto.nome_departamento.strip(), dto.empcod.strip(), dto.flagativo.strip().upper(), dto.codigo_departamento])
        else:
            sql = """
                INSERT INTO USER_geoapolo_departamentos (codigo_departamento, nome_departamento, empcod, flagativo)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(sql, [dto.codigo_departamento, dto.nome_departamento.strip(), dto.empcod.strip(), dto.flagativo.strip().upper()])

        # Vínculo com centro de controle
        cursor.execute("DELETE FROM geoapolo_secoescctrlapolo WHERE codigo_secao = ?", [dto.codigo_departamento])
        if dto.cctrlcodestr.strip():
            cursor.execute(
                "INSERT INTO geoapolo_secoescctrlapolo (codigo_secao, cctrlcodestr) VALUES (?, ?)",
                [dto.codigo_departamento, dto.cctrlcodestr.strip()],
            )

        self.commit()
        return True

    def excluir_departamento(self, codigo: int) -> bool:
        cursor = self._get_cursor()
        cursor.execute("DELETE FROM geoapolo_secoescctrlapolo WHERE codigo_secao = ?", [codigo])
        cursor.execute("DELETE FROM USER_geoapolo_departamentos WHERE codigo_departamento = ?", [codigo])
        self.commit()
        return True
