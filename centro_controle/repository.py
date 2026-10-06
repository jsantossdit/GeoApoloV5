"""
Repositório de Dados para Centros de Controle / Custos.
GeoApolo V5
Opera sobre a tabela USER_geoapolo_centrocontrole (SQL Server / SQLite).
"""

import logging
from typing import List, Optional
from datetime import datetime

from .models import CentroControleDTO

logger = logging.getLogger(__name__)


class CentroControleRepository:
    """Repositório de Centros de Controle / Custos do GeoApolo."""

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
        """Garante a existência da tabela USER_geoapolo_centrocontrole."""
        if not self.conn:
            return
        try:
            cur = self._get_cursor()
            if self._is_sql_server:
                cur.execute("""
                    IF OBJECT_ID('USER_geoapolo_centrocontrole', 'U') IS NULL
                    BEGIN
                        CREATE TABLE USER_geoapolo_centrocontrole
                        (
                            geocctrlcodestr varchar(30) NOT NULL,
                            geocctrlcodreduzido varchar(7) NOT NULL,
                            geocctrlnome varchar(60) NULL,
                            geocctrlcodestrniv varchar(30) NULL,
                            geocctrlgrupo char(1) NULL DEFAULT 'A',
                            geocctrlcusto varchar(10) NULL,
                            geodatavalidadeinicial datetime NULL,
                            geodatavalidadefinal datetime NULL,
                            empcod varchar(20) NULL DEFAULT '1.01',
                            CONSTRAINT PK_USER_geoapolo_centrocontrole PRIMARY KEY (geocctrlcodestr)
                        );
                    END
                """)
            else:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS USER_geoapolo_centrocontrole (
                        geocctrlcodestr VARCHAR(30) PRIMARY KEY,
                        geocctrlcodreduzido VARCHAR(7) NOT NULL,
                        geocctrlnome VARCHAR(60),
                        geocctrlcodestrniv VARCHAR(30),
                        geocctrlgrupo CHAR(1) DEFAULT 'A',
                        geocctrlcusto VARCHAR(10),
                        geodatavalidadeinicial TEXT,
                        geodatavalidadefinal TEXT,
                        empcod VARCHAR(20) DEFAULT '1.01'
                    )
                """)
            self.commit()
        except Exception as e:
            logger.warning("Aviso ao verificar tabela USER_geoapolo_centrocontrole: %s", e)

    def listar_centros(self, termo: str = "", empcod: str = "") -> List[CentroControleDTO]:
        """Lista centros de controle ordenados pelo código estruturado."""
        cur = self._get_cursor()
        nolock = self._nolock()
        where = []
        params = []

        if empcod and str(empcod).strip():
            where.append("empcod = ?")
            params.append(str(empcod).strip())

        if termo and str(termo).strip():
            t = f"%{str(termo).strip().upper()}%"
            where.append("(UPPER(geocctrlcodestr) LIKE ? OR UPPER(geocctrlnome) LIKE ? OR UPPER(geocctrlcodreduzido) LIKE ?)")
            params.extend([t, t, t])

        where_str = f"WHERE {' AND '.join(where)}" if where else ""
        sql = f"""
            SELECT geocctrlcodestr, geocctrlcodreduzido, geocctrlnome,
                   geocctrlcodestrniv, geocctrlgrupo, geocctrlcusto,
                   geodatavalidadeinicial, geodatavalidadefinal, empcod
            FROM USER_geoapolo_centrocontrole {nolock}
            {where_str}
            ORDER BY geocctrlcodestr ASC
        """
        cur.execute(sql, params)
        centros = []
        for r in cur.fetchall():
            d_ini = str(r[6])[:10] if r[6] else ""
            d_fim = str(r[7])[:10] if r[7] else ""
            centros.append(CentroControleDTO(
                geocctrlcodestr=str(r[0] or "").strip(),
                geocctrlcodreduzido=str(r[1] or "").strip(),
                geocctrlnome=str(r[2] or "").strip(),
                geocctrlcodestrniv=str(r[3] or "").strip(),
                geocctrlgrupo=str(r[4] or "A").strip().upper(),
                geocctrlcusto=str(r[5] or "").strip(),
                geodatavalidadeinicial=d_ini,
                geodatavalidadefinal=d_fim,
                empcod=str(r[8] or "1.01").strip(),
            ))
        return centros

    def obter_centro(self, geocctrlcodestr: str) -> Optional[CentroControleDTO]:
        """Obtém um centro de controle pelo código estruturado."""
        cur = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT geocctrlcodestr, geocctrlcodreduzido, geocctrlnome,
                   geocctrlcodestrniv, geocctrlgrupo, geocctrlcusto,
                   geodatavalidadeinicial, geodatavalidadefinal, empcod
            FROM USER_geoapolo_centrocontrole {nolock}
            WHERE UPPER(geocctrlcodestr) = ?
        """
        cur.execute(sql, [geocctrlcodestr.strip().upper()])
        r = cur.fetchone()
        if not r:
            return None
        d_ini = str(r[6])[:10] if r[6] else ""
        d_fim = str(r[7])[:10] if r[7] else ""
        return CentroControleDTO(
            geocctrlcodestr=str(r[0] or "").strip(),
            geocctrlcodreduzido=str(r[1] or "").strip(),
            geocctrlnome=str(r[2] or "").strip(),
            geocctrlcodestrniv=str(r[3] or "").strip(),
            geocctrlgrupo=str(r[4] or "A").strip().upper(),
            geocctrlcusto=str(r[5] or "").strip(),
            geodatavalidadeinicial=d_ini,
            geodatavalidadefinal=d_fim,
            empcod=str(r[8] or "1.01").strip(),
        )

    def salvar_centro(self, dto: CentroControleDTO) -> bool:
        """Insere ou atualiza um centro de controle."""
        cur = self._get_cursor()
        existente = self.obter_centro(dto.geocctrlcodestr)

        # Trata datas (vazias viram None no banco)
        d_ini = dto.geodatavalidadeinicial if dto.geodatavalidadeinicial and dto.geodatavalidadeinicial.strip() else None
        d_fim = dto.geodatavalidadefinal if dto.geodatavalidadefinal and dto.geodatavalidadefinal.strip() else None

        if existente:
            sql = """
                UPDATE USER_geoapolo_centrocontrole
                SET geocctrlcodreduzido = ?,
                    geocctrlnome = ?,
                    geocctrlcodestrniv = ?,
                    geocctrlgrupo = ?,
                    geocctrlcusto = ?,
                    geodatavalidadeinicial = ?,
                    geodatavalidadefinal = ?,
                    empcod = ?
                WHERE UPPER(geocctrlcodestr) = ?
            """
            cur.execute(sql, [
                dto.geocctrlcodreduzido.strip(),
                dto.geocctrlnome.strip().upper(),
                dto.geocctrlcodestrniv.strip(),
                dto.geocctrlgrupo.strip().upper() or "A",
                dto.geocctrlcusto.strip(),
                d_ini,
                d_fim,
                dto.empcod.strip() or "1.01",
                dto.geocctrlcodestr.strip().upper(),
            ])
        else:
            sql = """
                INSERT INTO USER_geoapolo_centrocontrole (
                    geocctrlcodestr, geocctrlcodreduzido, geocctrlnome,
                    geocctrlcodestrniv, geocctrlgrupo, geocctrlcusto,
                    geodatavalidadeinicial, geodatavalidadefinal, empcod
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cur.execute(sql, [
                dto.geocctrlcodestr.strip(),
                dto.geocctrlcodreduzido.strip(),
                dto.geocctrlnome.strip().upper(),
                dto.geocctrlcodestrniv.strip(),
                dto.geocctrlgrupo.strip().upper() or "A",
                dto.geocctrlcusto.strip(),
                d_ini,
                d_fim,
                dto.empcod.strip() or "1.01",
            ])
        self.commit()
        return True

    def excluir_centro(self, geocctrlcodestr: str) -> bool:
        """Exclui um centro de controle pelo código estruturado."""
        cur = self._get_cursor()
        cur.execute("DELETE FROM USER_geoapolo_centrocontrole WHERE UPPER(geocctrlcodestr) = ?", [geocctrlcodestr.strip().upper()])
        self.commit()
        return True

    def listar_niveis_superiores(self) -> List[CentroControleDTO]:
        """Retorna os centros de controle sintéticos ou de níveis superiores disponíveis."""
        cur = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT geocctrlcodestr, geocctrlcodreduzido, geocctrlnome,
                   geocctrlcodestrniv, geocctrlgrupo, geocctrlcusto,
                   geodatavalidadeinicial, geodatavalidadefinal, empcod
            FROM USER_geoapolo_centrocontrole {nolock}
            WHERE geocctrlgrupo = 'T' OR geocctrlcodestrniv IS NULL OR geocctrlcodestrniv = ''
            ORDER BY geocctrlcodestr ASC
        """
        cur.execute(sql)
        niveis = []
        for r in cur.fetchall():
            niveis.append(CentroControleDTO(
                geocctrlcodestr=str(r[0] or "").strip(),
                geocctrlcodreduzido=str(r[1] or "").strip(),
                geocctrlnome=str(r[2] or "").strip(),
                geocctrlcodestrniv=str(r[3] or "").strip(),
                geocctrlgrupo=str(r[4] or "T").strip().upper(),
                geocctrlcusto=str(r[5] or "").strip(),
                empcod=str(r[8] or "1.01").strip(),
            ))
        return niveis

    def obter_proximo_codigo_reduzido(self) -> str:
        """Calcula o próximo código reduzido numérico livre."""
        try:
            cur = self._get_cursor()
            nolock = self._nolock()
            cur.execute(f"SELECT geocctrlcodreduzido FROM USER_geoapolo_centrocontrole {nolock}")
            nums = []
            for r in cur.fetchall():
                val = str(r[0] or "").strip()
                if val.isdigit():
                    nums.append(int(val))
            prox = (max(nums) + 1) if nums else 1
            return f"{prox:02d}"
        except Exception:
            return "01"
