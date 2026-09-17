"""
Repositório de Dados do Módulo CRM.
GeoApolo V5
Clean Architecture: Acesso desacoplado com suporte a SQL Server nativo (WITH NOLOCK) e SQLite em memória.
"""

import logging
from typing import List, Optional
from entidades.database import obter_conexao_banco
from .models import (
    TipoCampanhaDTO,
    TipoTratamentoDTO,
    OcorrenciaDTO,
    MotivoOcorrenciaDTO,
    OrigemDTO,
    SolicitanteDTO,
)

logger = logging.getLogger(__name__)


class CRMRepository:
    """Repositório de persistência e consultas do CRM (Ocorrências, Campanhas, Tratamentos)."""

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

    # =========================================================================
    # TIPOS DE CAMPANHA (USER_geoapolo_tipocampanha)
    # =========================================================================

    def listar_tipos_campanha(self, apenas_ativos: bool = False) -> List[TipoCampanhaDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"SELECT codigo_tipocampanha, descricaotipocamp, ativo, geracampanha FROM USER_geoapolo_tipocampanha {nolock} "
        if apenas_ativos:
            sql += "WHERE ativo = 'S' "
        sql += "ORDER BY codigo_tipocampanha ASC"
        cursor.execute(sql)
        return [
            TipoCampanhaDTO(
                codigo_tipocampanha=str(r[0]).strip(),
                descricaotipocamp=str(r[1] or "").strip(),
                ativo=str(r[2] or "S").strip().upper(),
                geracampanha=str(r[3] or "S").strip().upper(),
            )
            for r in cursor.fetchall()
        ]

    def obter_tipo_campanha(self, codigo: str) -> Optional[TipoCampanhaDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"SELECT codigo_tipocampanha, descricaotipocamp, ativo, geracampanha FROM USER_geoapolo_tipocampanha {nolock} WHERE codigo_tipocampanha = ?"
        cursor.execute(sql, [codigo])
        r = cursor.fetchone()
        if not r:
            return None
        return TipoCampanhaDTO(
            codigo_tipocampanha=str(r[0]).strip(),
            descricaotipocamp=str(r[1] or "").strip(),
            ativo=str(r[2] or "S").strip().upper(),
            geracampanha=str(r[3] or "S").strip().upper(),
        )

    def salvar_tipo_campanha(self, dto: TipoCampanhaDTO) -> bool:
        cursor = self._get_cursor()
        cursor.execute("SELECT 1 FROM USER_geoapolo_tipocampanha WHERE codigo_tipocampanha = ?", [dto.codigo_tipocampanha])
        existe = cursor.fetchone() is not None
        if existe:
            sql = """
                UPDATE USER_geoapolo_tipocampanha
                SET descricaotipocamp = ?, ativo = ?, geracampanha = ?
                WHERE codigo_tipocampanha = ?
            """
            cursor.execute(sql, [dto.descricaotipocamp, dto.ativo, dto.geracampanha, dto.codigo_tipocampanha])
        else:
            sql = """
                INSERT INTO USER_geoapolo_tipocampanha (codigo_tipocampanha, descricaotipocamp, ativo, geracampanha)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(sql, [dto.codigo_tipocampanha, dto.descricaotipocamp, dto.ativo, dto.geracampanha])
        self.commit()
        return True

    def excluir_tipo_campanha(self, codigo: str) -> bool:
        cursor = self._get_cursor()
        cursor.execute("DELETE FROM USER_geoapolo_tipocampanha WHERE codigo_tipocampanha = ?", [codigo])
        self.commit()
        return True

    # =========================================================================
    # TIPOS DE TRATAMENTO (USER_geoapolo_tipotratamento)
    # =========================================================================

    def listar_tipos_tratamento(self) -> List[TipoTratamentoDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"SELECT tipotratcod, abreviatura, descricao_tratamento FROM USER_geoapolo_tipotratamento {nolock} ORDER BY abreviatura ASC"
        cursor.execute(sql)
        return [
            TipoTratamentoDTO(
                tipotratcod=str(r[0]).strip(),
                abreviatura=str(r[1] or "").strip(),
                descricao_tratamento=str(r[2] or "").strip(),
            )
            for r in cursor.fetchall()
        ]

    def obter_tipo_tratamento(self, codigo: str) -> Optional[TipoTratamentoDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"SELECT tipotratcod, abreviatura, descricao_tratamento FROM USER_geoapolo_tipotratamento {nolock} WHERE tipotratcod = ?"
        cursor.execute(sql, [codigo])
        r = cursor.fetchone()
        if not r:
            return None
        return TipoTratamentoDTO(
            tipotratcod=str(r[0]).strip(),
            abreviatura=str(r[1] or "").strip(),
            descricao_tratamento=str(r[2] or "").strip(),
        )

    def salvar_tipo_tratamento(self, dto: TipoTratamentoDTO) -> bool:
        cursor = self._get_cursor()
        cursor.execute("SELECT 1 FROM USER_geoapolo_tipotratamento WHERE tipotratcod = ?", [dto.tipotratcod])
        existe = cursor.fetchone() is not None
        if existe:
            sql = """
                UPDATE USER_geoapolo_tipotratamento
                SET abreviatura = ?, descricao_tratamento = ?
                WHERE tipotratcod = ?
            """
            cursor.execute(sql, [dto.abreviatura, dto.descricao_tratamento, dto.tipotratcod])
        else:
            sql = """
                INSERT INTO USER_geoapolo_tipotratamento (tipotratcod, abreviatura, descricao_tratamento)
                VALUES (?, ?, ?)
            """
            cursor.execute(sql, [dto.tipotratcod, dto.abreviatura, dto.descricao_tratamento])
        self.commit()
        return True

    def excluir_tipo_tratamento(self, codigo: str) -> bool:
        cursor = self._get_cursor()
        cursor.execute("DELETE FROM USER_geoapolo_tipotratamento WHERE tipotratcod = ?", [codigo])
        self.commit()
        return True

    # =========================================================================
    # OCORRÊNCIAS (OCORRENCIA, MOTIVO_OCOR, ORIGEM)
    # =========================================================================

    def listar_ocorrencias(
        self, status: str = "", empcod: str = "", filtro: str = ""
    ) -> List[OcorrenciaDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT o.OcorCod, o.OcorStat, o.EntCod, o.ocorentnome, o.OcorRespSol,
                   COALESCE(o.OcorData, '') AS ocordata_str,
                   o.MotOcorCodEstr, COALESCE(mo.MotOcorDescr, '') AS MotOcorDescr,
                   COALESCE(o.ocortexto, '') AS ocortexto,
                   COALESCE(o.ocorresptexto, '') AS ocorresptexto,
                   COALESCE(o.origcodestr, '') AS origcodestr,
                   COALESCE(orig.OrigNome, '') AS orignome,
                   COALESCE(o.empcod, '') AS empcod,
                   COALESCE(o.ocordatacanc, '') AS ocordatacanc_str,
                   COALESCE(o.ocorrespcanc, '') AS ocorrespcanc,
                   COALESCE(o.ocormotcanc, '') AS ocormotcanc
            FROM OCORRENCIA o {nolock}
            LEFT JOIN MOTIVO_OCOR mo {nolock} ON o.MotOcorCodEstr = mo.MotOcorCodEstr
            LEFT JOIN ORIGEM orig {nolock} ON o.origcodestr = orig.OrigCodEstr
            WHERE 1=1
        """
        params = []
        if status and status.strip():
            sql += " AND o.OcorStat = ?"
            params.append(status.strip())
        if empcod and empcod.strip():
            sql += " AND o.empcod = ?"
            params.append(empcod.strip())
        if filtro and filtro.strip():
            sql += " AND (o.ocorentnome LIKE ? OR o.ocortexto LIKE ? OR o.OcorCod LIKE ?)"
            f_termo = f"%{filtro.strip()}%"
            params.extend([f_termo, f_termo, f_termo])

        sql += " ORDER BY o.OcorData DESC"
        cursor.execute(sql, params)
        itens = []
        for r in cursor.fetchall():
            itens.append(
                OcorrenciaDTO(
                    ocorcod=str(r[0]).strip(),
                    ocorstat=str(r[1] or "Pendente").strip(),
                    entcod=str(r[2] or "").strip(),
                    ocorentnome=str(r[3] or "").strip(),
                    ocorrespsol=str(r[4] or "").strip(),
                    ocordata=str(r[5] or "").strip(),
                    motocorcodestr=str(r[6] or "").strip(),
                    motocordescr=str(r[7] or "").strip(),
                    ocortexto=str(r[8] or "").strip(),
                    ocorresptexto=str(r[9] or "").strip(),
                    origcodestr=str(r[10] or "").strip(),
                    orignome=str(r[11] or "").strip(),
                    empcod=str(r[12] or "").strip(),
                    ocordatacanc=str(r[13] or "").strip(),
                    ocorrespcanc=str(r[14] or "").strip(),
                    ocormotcanc=str(r[15] or "").strip(),
                )
            )
        return itens

    def obter_ocorrencia(self, ocorcod: str) -> Optional[OcorrenciaDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT o.OcorCod, o.OcorStat, o.EntCod, o.ocorentnome, o.OcorRespSol,
                   COALESCE(o.OcorData, '') AS ocordata_str,
                   o.MotOcorCodEstr, COALESCE(mo.MotOcorDescr, '') AS MotOcorDescr,
                   COALESCE(o.ocortexto, '') AS ocortexto,
                   COALESCE(o.ocorresptexto, '') AS ocorresptexto,
                   COALESCE(o.origcodestr, '') AS origcodestr,
                   COALESCE(orig.OrigNome, '') AS orignome,
                   COALESCE(o.empcod, '') AS empcod,
                   COALESCE(o.ocordatacanc, '') AS ocordatacanc_str,
                   COALESCE(o.ocorrespcanc, '') AS ocorrespcanc,
                   COALESCE(o.ocormotcanc, '') AS ocormotcanc
            FROM OCORRENCIA o {nolock}
            LEFT JOIN MOTIVO_OCOR mo {nolock} ON o.MotOcorCodEstr = mo.MotOcorCodEstr
            LEFT JOIN ORIGEM orig {nolock} ON o.origcodestr = orig.OrigCodEstr
            WHERE o.OcorCod = ?
        """
        cursor.execute(sql, [ocorcod])
        r = cursor.fetchone()
        if not r:
            return None
        return OcorrenciaDTO(
            ocorcod=str(r[0]).strip(),
            ocorstat=str(r[1] or "Pendente").strip(),
            entcod=str(r[2] or "").strip(),
            ocorentnome=str(r[3] or "").strip(),
            ocorrespsol=str(r[4] or "").strip(),
            ocordata=str(r[5] or "").strip(),
            motocorcodestr=str(r[6] or "").strip(),
            motocordescr=str(r[7] or "").strip(),
            ocortexto=str(r[8] or "").strip(),
            ocorresptexto=str(r[9] or "").strip(),
            origcodestr=str(r[10] or "").strip(),
            orignome=str(r[11] or "").strip(),
            empcod=str(r[12] or "").strip(),
            ocordatacanc=str(r[13] or "").strip(),
            ocorrespcanc=str(r[14] or "").strip(),
            ocormotcanc=str(r[15] or "").strip(),
        )

    def proximo_codigo_ocorrencia(self) -> str:
        """Gera o próximo código sequencial de ocorrência formatado."""
        cursor = self._get_cursor()
        sql = "SELECT COUNT(1) FROM OCORRENCIA"
        cursor.execute(sql)
        row = cursor.fetchone()
        prox = (row[0] if row else 0) + 1
        return f"{prox:07d}"

    def salvar_ocorrencia(self, dto: OcorrenciaDTO) -> bool:
        cursor = self._get_cursor()
        cursor.execute("SELECT 1 FROM OCORRENCIA WHERE OcorCod = ?", [dto.ocorcod])
        existe = cursor.fetchone() is not None
        if existe:
            sql = """
                UPDATE OCORRENCIA
                SET EntCod = ?, ocorentnome = ?, OcorRespSol = ?,
                    MotOcorCodEstr = ?, ocortexto = ?, ocorresptexto = ?,
                    origcodestr = ?, ocorstat = ?, empcod = ?
                WHERE OcorCod = ?
            """
            cursor.execute(
                sql,
                [
                    dto.entcod,
                    dto.ocorentnome,
                    dto.ocorrespsol,
                    dto.motocorcodestr,
                    dto.ocortexto,
                    dto.ocorresptexto,
                    dto.origcodestr,
                    dto.ocorstat,
                    dto.empcod,
                    dto.ocorcod,
                ],
            )
        else:
            sql = """
                INSERT INTO OCORRENCIA (
                    OcorCod, OcorStat, EntCod, ocorentnome, OcorRespSol,
                    OcorData, MotOcorCodEstr, ocortexto, ocorresptexto,
                    origcodestr, empcod
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            data_val = dto.ocordata if dto.ocordata else "2026-01-01"
            cursor.execute(
                sql,
                [
                    dto.ocorcod,
                    dto.ocorstat,
                    dto.entcod,
                    dto.ocorentnome,
                    dto.ocorrespsol,
                    data_val,
                    dto.motocorcodestr,
                    dto.ocortexto,
                    dto.ocorresptexto,
                    dto.origcodestr,
                    dto.empcod,
                ],
            )
        self.commit()
        return True

    def cancelar_ocorrencia(
        self, ocorcod: str, data_canc: str, resp_canc: str, mot_canc: str
    ) -> bool:
        cursor = self._get_cursor()
        sql = """
            UPDATE OCORRENCIA
            SET ocordatacanc = ?, ocorrespcanc = ?, ocormotcanc = ?, ocorstat = 'Cancelado'
            WHERE OcorCod = ?
        """
        cursor.execute(sql, [data_canc, resp_canc, mot_canc, ocorcod])
        self.commit()
        return True

    def atualizar_solucao(
        self, ocorcod: str, resp_texto: str, status: str = "Resolvido", resp_sol: str = ""
    ) -> bool:
        cursor = self._get_cursor()
        sql = """
            UPDATE OCORRENCIA
            SET ocorresptexto = ?, ocorstat = ?, OcorRespSol = ?
            WHERE OcorCod = ?
        """
        cursor.execute(sql, [resp_texto, status, resp_sol, ocorcod])
        self.commit()
        return True

    # =========================================================================
    # AUXILIARES (ÁREAS, MOTIVOS, ORIGENS, SOLICITANTES)
    # =========================================================================

    def listar_areas_disponiveis(self) -> List[MotivoOcorrenciaDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"SELECT MotOcorCodEstr, MotOcorDescr FROM motivo_ocor {nolock} WHERE MotOcorGrupo = 'T' ORDER BY MotOcorDescr ASC"
        cursor.execute(sql)
        return [
            MotivoOcorrenciaDTO(
                motocorcodestr=str(r[0]).strip(),
                motocordescr=str(r[1] or "").strip(),
                motocorgrupo="T",
            )
            for r in cursor.fetchall()
        ]

    def listar_motivos_por_area(self, prefixo_area: str) -> List[MotivoOcorrenciaDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT MotOcorCodEstr, MotOcorDescr,
                   COALESCE(MotOcorResp1, '') AS r1,
                   COALESCE(MotOcorResp2, '') AS r2,
                   COALESCE(MotOcorResp3, '') AS r3
            FROM motivo_ocor {nolock}
            WHERE MotOcorGrupo = 'F' AND MotOcorCodEstr LIKE ?
            ORDER BY MotOcorDescr ASC
        """
        cursor.execute(sql, [f"{prefixo_area.strip()}%"])
        return [
            MotivoOcorrenciaDTO(
                motocorcodestr=str(r[0]).strip(),
                motocordescr=str(r[1] or "").strip(),
                motocorgrupo="F",
                motocorresp1=str(r[2] or "").strip(),
                motocorresp2=str(r[3] or "").strip(),
                motocorresp3=str(r[4] or "").strip(),
            )
            for r in cursor.fetchall()
        ]

    def listar_origens(self) -> List[OrigemDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"SELECT OrigCodEstr, OrigNome FROM ORIGEM {nolock} ORDER BY OrigCodEstr ASC"
        cursor.execute(sql)
        return [
            OrigemDTO(
                origcodestr=str(r[0]).strip(),
                orignome=str(r[1] or "").strip(),
            )
            for r in cursor.fetchall()
        ]

    def listar_solicitantes(self, filtro: str = "") -> List[SolicitanteDTO]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT e.entcod, e.entnome, ec.categcodestr, COALESCE(e.entstatdescr, '') AS entstatdescr
            FROM ENTIDADE e {nolock}
            LEFT JOIN ENT_CATEG ec {nolock} ON e.EntCod = ec.EntCod
            WHERE 1=1
        """
        params = []
        if filtro and filtro.strip():
            sql += " AND (e.entnome LIKE ? OR e.entcod LIKE ?)"
            termo = f"%{filtro.strip()}%"
            params.extend([termo, termo])
        sql += " GROUP BY e.entcod, e.EntNome, ec.categcodestr, e.EntStatDescr ORDER BY e.EntNome ASC"
        cursor.execute(sql, params)
        return [
            SolicitanteDTO(
                entcod=str(r[0]).strip(),
                entnome=str(r[1] or "").strip(),
                categcodestr=str(r[2] or "").strip(),
                entstatdescr=str(r[3] or "").strip(),
            )
            for r in cursor.fetchall()
        ]
