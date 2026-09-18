"""
Repositório de dados para Multi-Empresas e Filiais.
GeoApolo V5
Compatível com SQL Server nativo (WITH NOLOCK) e SQLite em memória.
"""

import sys
from pathlib import Path

# Garante que o diretório raiz esteja no sys.path
_raiz_projeto = str(Path(__file__).resolve().parent.parent)
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

from typing import List, Optional
try:
    from empresas.models import EmpresaDTO, ResultadoEmpresaDTO
except (ImportError, ModuleNotFoundError):
    from models import EmpresaDTO, ResultadoEmpresaDTO


class EmpresasRepository:
    """Repositório de persistência e consultas de Empresas e Filiais."""

    def __init__(self, connection):
        self.conn = connection
        self._is_sql_server = not hasattr(connection, "isolation_level")

    def _nolock(self) -> str:
        return "WITH (NOLOCK)" if self._is_sql_server else ""

    def listar_empresas(self) -> List[EmpresaDTO]:
        """Lista todas as empresas cadastradas no GeoApolo."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"SELECT empcod, empnome FROM USER_geoapolo_empresas {nolock} ORDER BY empcod ASC"
        cur.execute(sql)
        return [
            EmpresaDTO(
                empcod=str(r[0]),
                empnome=str(r[1] or ""),
                ativa=True,
            )
            for r in cur.fetchall()
        ]

    def obter_empresa(self, empcod: str) -> Optional[EmpresaDTO]:
        """Busca empresa pelo código identificador."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"SELECT empcod, empnome FROM USER_geoapolo_empresas {nolock} WHERE empcod = ?"
        cur.execute(sql, [empcod])
        r = cur.fetchone()
        if not r:
            return None
        return EmpresaDTO(
            empcod=str(r[0]),
            empnome=str(r[1] or ""),
            ativa=True,
        )

    def salvar_empresa(self, e: EmpresaDTO) -> bool:
        """Cria ou atualiza uma empresa."""
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM USER_geoapolo_empresas WHERE empcod = ?", [e.empcod])
        if cur.fetchone():
            cur.execute(
                "UPDATE USER_geoapolo_empresas SET empnome = ? WHERE empcod = ?",
                [e.empnome, e.empcod],
            )
        else:
            cur.execute(
                "INSERT INTO USER_geoapolo_empresas (empcod, empnome) VALUES (?, ?)",
                [e.empcod, e.empnome],
            )
        self.conn.commit()
        return True

    def excluir_empresa(self, empcod: str) -> bool:
        """Remove a empresa cadastrada."""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM USER_geoapolo_empresas WHERE empcod = ?", [empcod])
        self.conn.commit()
        return True

    def sincronizar_empresas_apolo(self) -> int:
        """Importa empresas/filiais existentes na base principal Apolo (empresa_filial)."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"""
            INSERT INTO USER_geoapolo_empresas (empcod, empnome)
            SELECT f.empcod, f.empnome
            FROM empresa_filial f {nolock}
            WHERE NOT EXISTS (
                SELECT 1 FROM USER_geoapolo_empresas g WHERE g.empcod = f.empcod
            )
        """
        cur.execute(sql)
        self.conn.commit()
        return cur.rowcount
