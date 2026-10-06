"""
Repositório de Dados para o Cadastro de Cargos.
GeoApolo V5
Opera sobre a tabela USER_geoapolo_cargos (SQL Server / SQLite) e sincroniza com o Alvo (cargo).
"""

import logging
from typing import List, Optional, Tuple

from .models import CargoDTO

logger = logging.getLogger(__name__)


class CargoRepository:
    """Repositório de persistência para cargos."""

    def __init__(self, connection=None):
        self.conn = connection
        self._garantir_tabela()

    @property
    def _is_sql_server(self) -> bool:
        return self.conn is not None and not hasattr(self.conn, "isolation_level")

    def _get_cursor(self):
        if not self.conn:
            raise RuntimeError("Conexão com o banco de dados não estabelecida.")
        return self.conn.cursor()

    def commit(self):
        if self.conn:
            try:
                self.conn.commit()
            except Exception:
                pass

    def rollback(self):
        if self.conn:
            try:
                self.conn.rollback()
            except Exception:
                pass

    def _nolock(self) -> str:
        return "WITH (NOLOCK)" if self._is_sql_server else ""

    def _garantir_tabela(self):
        """Garante a existência da tabela USER_geoapolo_cargos."""
        if not self.conn:
            return
        try:
            cur = self._get_cursor()
            if self._is_sql_server:
                cur.execute("""
                    IF OBJECT_ID('USER_geoapolo_cargos', 'U') IS NULL
                    BEGIN
                        CREATE TABLE USER_geoapolo_cargos
                        (
                            geocargocodestr NUMERIC(5,0) NOT NULL,
                            geocargonome VARCHAR(80) NOT NULL,
                            geofaixasalarial VARCHAR(14) NULL,
                            CONSTRAINT PK_USER_geoapolo_cargos PRIMARY KEY (geocargocodestr)
                        );
                    END
                """)
            else:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS USER_geoapolo_cargos (
                        geocargocodestr INTEGER PRIMARY KEY,
                        geocargonome TEXT NOT NULL,
                        geofaixasalarial TEXT
                    )
                """)
            self.commit()
        except Exception as e:
            logger.warning("Aviso ao verificar tabela USER_geoapolo_cargos: %s", e)

    def listar_cargos(self, termo: str = "", limite: int = 500) -> List[CargoDTO]:
        """Lista os cargos cadastrados ordenados por código ou nome."""
        cur = self._get_cursor()
        nolock = self._nolock()
        where = []
        params = []

        if termo and str(termo).strip():
            t = f"%{str(termo).strip().upper()}%"
            where.append("(UPPER(geocargonome) LIKE ? OR CAST(geocargocodestr AS VARCHAR) LIKE ?)")
            params.extend([t, t])

        where_str = f"WHERE {' AND '.join(where)}" if where else ""

        sql = f"""
            SELECT geocargocodestr, geocargonome, COALESCE(geofaixasalarial, '')
            FROM USER_geoapolo_cargos {nolock}
            {where_str}
            ORDER BY geocargocodestr ASC
        """
        cur.execute(sql, params)
        cargos = []
        for r in cur.fetchall()[:limite]:
            cargos.append(CargoDTO(
                geocargocodestr=int(r[0]),
                geocargonome=str(r[1] or "").strip(),
                geofaixasalarial=str(r[2] or "").strip(),
            ))
        return cargos

    def obter_cargo_por_codigo(self, codigo: int) -> Optional[CargoDTO]:
        """Busca cargo por código."""
        cur = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT geocargocodestr, geocargonome, COALESCE(geofaixasalarial, '')
            FROM USER_geoapolo_cargos {nolock}
            WHERE geocargocodestr = ?
        """
        cur.execute(sql, [codigo])
        r = cur.fetchone()
        if not r:
            return None
        return CargoDTO(
            geocargocodestr=int(r[0]),
            geocargonome=str(r[1] or "").strip(),
            geofaixasalarial=str(r[2] or "").strip(),
        )

    def obter_proximo_codigo(self) -> int:
        """Gera o próximo código numérico sequencial para novo cargo."""
        cur = self._get_cursor()
        nolock = self._nolock()
        sql = f"SELECT COALESCE(MAX(geocargocodestr), 0) + 1 FROM USER_geoapolo_cargos {nolock}"
        cur.execute(sql)
        r = cur.fetchone()
        return int(r[0]) if r and r[0] is not None else 1

    def salvar_cargo(self, cargo: CargoDTO) -> Tuple[bool, str, int]:
        """Salva cargo (inserção ou atualização)."""
        cur = self._get_cursor()
        nolock = self._nolock()

        if not cargo.geocargocodestr or cargo.geocargocodestr <= 0:
            cargo.geocargocodestr = self.obter_proximo_codigo()

        # Verifica se já existe
        cur.execute(f"SELECT COUNT(1) FROM USER_geoapolo_cargos {nolock} WHERE geocargocodestr = ?", [cargo.geocargocodestr])
        existe = (cur.fetchone()[0] > 0)

        nome = str(cargo.geocargonome or "").strip().upper()
        faixa = str(cargo.geofaixasalarial or "").strip().upper()

        try:
            if existe:
                cur.execute("""
                    UPDATE USER_geoapolo_cargos
                    SET geocargonome = ?, geofaixasalarial = ?
                    WHERE geocargocodestr = ?
                """, [nome, faixa, cargo.geocargocodestr])
                msg = f"Cargo Nº {cargo.geocargocodestr} atualizado com sucesso."
            else:
                cur.execute("""
                    INSERT INTO USER_geoapolo_cargos (geocargocodestr, geocargonome, geofaixasalarial)
                    VALUES (?, ?, ?)
                """, [cargo.geocargocodestr, nome, faixa])
                msg = f"Cargo Nº {cargo.geocargocodestr} inserido com sucesso."

            # Sincronização opcional com Alvo (tabela cargo)
            self._sincronizar_alvo(cargo.geocargocodestr, nome, faixa)

            self.commit()
            return True, msg, cargo.geocargocodestr
        except Exception as e:
            self.rollback()
            logger.error("Erro ao salvar cargo: %s", e)
            return False, f"Erro ao salvar cargo: {e}", cargo.geocargocodestr

    def excluir_cargo(self, codigo: int) -> Tuple[bool, str]:
        """Exclui cargo do sistema caso não esteja em uso."""
        cur = self._get_cursor()
        nolock = self._nolock()

        # Verifica vínculo em funcionários se a tabela existir
        em_uso, tab_origem = self.verificar_uso_cargo(codigo)
        if em_uso:
            return False, f"Não é possível excluir o cargo Nº {codigo}: existem vínculos na tabela {tab_origem}."

        try:
            cur.execute("DELETE FROM USER_geoapolo_cargos WHERE geocargocodestr = ?", [codigo])
            # Remove da tabela do Alvo se existir
            self._remover_alvo(codigo)
            self.commit()
            return True, f"Cargo Nº {codigo} excluído com sucesso."
        except Exception as e:
            self.rollback()
            logger.error("Erro ao excluir cargo: %s", e)
            return False, f"Erro ao excluir cargo: {e}"

    def verificar_uso_cargo(self, codigo: int) -> Tuple[bool, str]:
        """Verifica se o cargo está vinculado a colaboradores/funcionários."""
        cur = self._get_cursor()
        nolock = self._nolock()
        tabelas_checar = [
            ("USER_geoapolo_funcionarios", "geocargocodestr"),
            ("FUNCIONARIO", "CargoCodEstr"),
        ]
        for tab, col in tabelas_checar:
            try:
                if self._is_sql_server:
                    cur.execute(f"SELECT COUNT(1) FROM sysobjects WHERE name = ? AND xtype = 'U'", [tab])
                    if not cur.fetchone()[0]:
                        continue
                else:
                    cur.execute(f"SELECT COUNT(1) FROM sqlite_master WHERE type='table' AND name = ?", [tab])
                    if not cur.fetchone()[0]:
                        continue

                cur.execute(f"SELECT COUNT(1) FROM {tab} {nolock} WHERE {col} = ? OR {col} = CAST(? AS VARCHAR)", [codigo, codigo])
                r = cur.fetchone()
                if r and r[0] > 0:
                    return True, tab
            except Exception:
                continue
        return False, ""

    def _sincronizar_alvo(self, codigo: int, nome: str, faixa: str):
        """Sincroniza registro com a tabela CARGO do Alvo caso ela exista."""
        cur = self._get_cursor()
        nolock = self._nolock()
        try:
            if self._is_sql_server:
                cur.execute("SELECT 1 FROM sysobjects WHERE name = 'CARGO' AND xtype = 'U'")
                if not cur.fetchone():
                    return
                cod_str = str(codigo)
                cur.execute(f"SELECT 1 FROM CARGO {nolock} WHERE CargoCodEstr = ?", [cod_str])
                if cur.fetchone():
                    cur.execute("""
                        UPDATE CARGO
                        SET CargoNome = ?, FaixaSalCod = ?
                        WHERE CargoCodEstr = ?
                    """, [nome, faixa, cod_str])
                else:
                    cur.execute("""
                        INSERT INTO CARGO (CargoCodEstr, CargoNome, FaixaSalCod, CargoGrupo, CargoNivel)
                        VALUES (?, ?, ?, '1', '1')
                    """, [cod_str, nome, faixa])
        except Exception as e:
            logger.debug("Sincronização com Alvo ignorada: %s", e)

    def _remover_alvo(self, codigo: int):
        """Remove registro da tabela CARGO do Alvo caso exista."""
        cur = self._get_cursor()
        try:
            if self._is_sql_server:
                cur.execute("SELECT 1 FROM sysobjects WHERE name = 'CARGO' AND xtype = 'U'")
                if cur.fetchone():
                    cur.execute("DELETE FROM CARGO WHERE CargoCodEstr = ?", [str(codigo)])
        except Exception:
            pass
