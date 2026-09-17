"""
Repositório de Dados para Manutenção de Códigos do Sistema (USER_geoapolo_configcod).
GeoApolo V5
Clean Architecture: Suporte híbrido a SQL Server nativo (WITH NOLOCK) e SQLite em memória.
"""

import logging
from typing import List, Optional

from entidades.database import obter_conexao_banco
from .models import ConfigCodDTO

logger = logging.getLogger(__name__)


class ConfigCodRepository:
    """Repositório de persistência para controle de códigos e sequenciais."""

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

    def listar_tabelas(self, filtro: str = "") -> List[ConfigCodDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        filtro_limpo = (filtro or "").strip()

        if filtro_limpo:
            sql = f"""
                SELECT ugcc.geotabela, ugcc.proximo_codigo, ugcc.tabela_ativa,
                       ugcc.empcod, COALESCE(uge.empnome, '') AS empnome
                FROM USER_geoapolo_configcod ugcc {nolock}
                LEFT JOIN USER_geoapolo_empresas uge {nolock} ON ugcc.empcod = uge.empcod
                WHERE UPPER(ugcc.geotabela) LIKE UPPER(?)
                ORDER BY ugcc.geotabela ASC
            """
            cursor.execute(sql, [f"%{filtro_limpo}%"])
        else:
            sql = f"""
                SELECT ugcc.geotabela, ugcc.proximo_codigo, ugcc.tabela_ativa,
                       ugcc.empcod, COALESCE(uge.empnome, '') AS empnome
                FROM USER_geoapolo_configcod ugcc {nolock}
                LEFT JOIN USER_geoapolo_empresas uge {nolock} ON ugcc.empcod = uge.empcod
                ORDER BY ugcc.geotabela ASC
            """
            cursor.execute(sql)

        return [
            ConfigCodDTO(
                geotabela=str(r[0] or "").strip(),
                proximo_codigo=int(r[1] or 0),
                tabela_ativa=str(r[2] or "N").strip().upper(),
                empcod=str(r[3] or "").strip(),
                empnome=str(r[4] or "").strip(),
            )
            for r in cursor.fetchall()
        ]

    def obter_config_cod(self, geotabela: str) -> Optional[ConfigCodDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT ugcc.geotabela, ugcc.proximo_codigo, ugcc.tabela_ativa,
                   ugcc.empcod, COALESCE(uge.empnome, '') AS empnome
            FROM USER_geoapolo_configcod ugcc {nolock}
            LEFT JOIN USER_geoapolo_empresas uge {nolock} ON ugcc.empcod = uge.empcod
            WHERE UPPER(ugcc.geotabela) = UPPER(?)
        """
        cursor.execute(sql, [geotabela.strip()])
        r = cursor.fetchone()
        if not r:
            return None

        return ConfigCodDTO(
            geotabela=str(r[0] or "").strip(),
            proximo_codigo=int(r[1] or 0),
            tabela_ativa=str(r[2] or "N").strip().upper(),
            empcod=str(r[3] or "").strip(),
            empnome=str(r[4] or "").strip(),
        )

    def salvar_config_cod(self, dto: ConfigCodDTO) -> bool:
        cursor = self._get_cursor()
        cursor.execute(
            "SELECT 1 FROM USER_geoapolo_configcod WHERE UPPER(geotabela) = UPPER(?)",
            [dto.geotabela.strip()],
        )
        existe = cursor.fetchone() is not None

        if existe:
            sql = """
                UPDATE USER_geoapolo_configcod
                SET proximo_codigo = ?, tabela_ativa = ?, empcod = ?
                WHERE UPPER(geotabela) = UPPER(?)
            """
            cursor.execute(sql, [
                dto.proximo_codigo,
                dto.tabela_ativa.strip().upper(),
                dto.empcod.strip(),
                dto.geotabela.strip(),
            ])
        else:
            sql = """
                INSERT INTO USER_geoapolo_configcod (geotabela, proximo_codigo, tabela_ativa, empcod)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(sql, [
                dto.geotabela.strip(),
                dto.proximo_codigo,
                dto.tabela_ativa.strip().upper(),
                dto.empcod.strip(),
            ])
        self.commit()
        return True

    def atualizar_proximo_codigo(self, geotabela: str, proximo_codigo: int, tabela_ativa: str) -> bool:
        cursor = self._get_cursor()
        sql = """
            UPDATE USER_geoapolo_configcod
            SET proximo_codigo = ?, tabela_ativa = ?
            WHERE UPPER(geotabela) = UPPER(?)
        """
        cursor.execute(sql, [proximo_codigo, tabela_ativa.strip().upper(), geotabela.strip()])
        self.commit()
        return True

    def gerar_e_incrementar_codigo(self, geotabela: str) -> int:
        """Obtém o código atual e avança o contador em +1 atomicamente."""
        cfg = self.obter_config_cod(geotabela)
        if not cfg:
            # Inicializa registro padrão se não existir (retorna 1 e deixa próximo como 2)
            cfg = ConfigCodDTO(geotabela=geotabela.strip(), proximo_codigo=2, tabela_ativa="S")
            self.salvar_config_cod(cfg)
            return 1

        codigo_atual = cfg.proximo_codigo
        self.atualizar_proximo_codigo(geotabela, codigo_atual + 1, cfg.tabela_ativa)
        return codigo_atual

