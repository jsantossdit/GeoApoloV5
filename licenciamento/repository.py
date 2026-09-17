"""
Repositório de Persistência para Licenciamento e Manutenção de Versões.
GeoApolo V5
Clean Architecture: Acesso desacoplado com suporte a SQL Server (WITH NOLOCK) e SQLite.
"""

from datetime import date, datetime
import logging
from typing import List, Optional

from entidades.database import obter_conexao_banco
from .models import LicencaDTO, VersaoSistemaDTO

logger = logging.getLogger(__name__)


class LicenciamentoRepository:
    """Repositório de dados para licenças, controle de versões e leitura de novidades."""

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

    # -------------------------------------------------------------
    # Licenciamento (user_geoapolo_dicionario)
    # -------------------------------------------------------------
    def buscar_licenca_mes(self, mes: int, ano: int) -> Optional[LicencaDTO]:
        """Busca a licença cadastrada para o mês e ano especificados."""
        cursor = self._get_cursor()
        nolock = self._nolock()

        if self._is_sql_server:
            sql = f"""
                SELECT id_palavra, data_inicial, data_final, flag_bloqueia,
                       tempo_bloqueio_dias, flag_ativar
                FROM user_geoapolo_dicionario {nolock}
                WHERE MONTH(data_inicial) = ? AND YEAR(data_inicial) = ?
            """
            cursor.execute(sql, [mes, ano])
        else:
            # Compatibilidade SQLite: strftime('%m', ...) e strftime('%Y', ...)
            sql = f"""
                SELECT id_palavra, data_inicial, data_final, flag_bloqueia,
                       tempo_bloqueio_dias, flag_ativar
                FROM user_geoapolo_dicionario {nolock}
                WHERE CAST(strftime('%m', data_inicial) AS INTEGER) = ?
                  AND CAST(strftime('%Y', data_inicial) AS INTEGER) = ?
            """
            cursor.execute(sql, [mes, ano])

        row = cursor.fetchone()
        if not row:
            return None

        dt_ini = row[1]
        dt_fim = row[2]

        if isinstance(dt_ini, str):
            try:
                dt_ini = datetime.strptime(dt_ini[:10], "%Y-%m-%d").date()
            except Exception:
                dt_ini = None
        elif isinstance(dt_ini, datetime):
            dt_ini = dt_ini.date()

        if isinstance(dt_fim, str):
            try:
                dt_fim = datetime.strptime(dt_fim[:10], "%Y-%m-%d").date()
            except Exception:
                dt_fim = None
        elif isinstance(dt_fim, datetime):
            dt_fim = dt_fim.date()

        return LicencaDTO(
            id_palavra=str(row[0] or "").strip(),
            data_inicial=dt_ini,
            data_final=dt_fim,
            flag_bloqueia=str(row[3] or "N").strip(),
            tempo_bloqueio_dias=int(row[4] or 15),
            flag_ativar=str(row[5] or "S").strip(),
            mes_referencia=mes,
            ano_referencia=ano,
        )

    def bloquear_licenca(self, id_palavra: str) -> bool:
        """Marca a licença como bloqueada no banco."""
        cursor = self._get_cursor()
        sql = "UPDATE user_geoapolo_dicionario SET flag_bloqueia = 'S' WHERE id_palavra = ?"
        cursor.execute(sql, [id_palavra])
        self.commit()
        return True

    def ativar_licenca(self, id_palavra: str) -> bool:
        """Ativa a licença e remove bloqueio ativo."""
        cursor = self._get_cursor()
        sql = "UPDATE user_geoapolo_dicionario SET flag_ativar = 'S', flag_bloqueia = 'N' WHERE id_palavra = ?"
        cursor.execute(sql, [id_palavra])
        self.commit()
        return True

    def salvar_licenca(self, licenca: LicencaDTO) -> bool:
        """Cria ou atualiza registro de licença no dicionário."""
        cursor = self._get_cursor()
        cursor.execute("SELECT 1 FROM user_geoapolo_dicionario WHERE id_palavra = ?", [licenca.id_palavra])
        existe = cursor.fetchone() is not None

        str_ini = licenca.data_inicial.isoformat() if licenca.data_inicial else None
        str_fim = licenca.data_final.isoformat() if licenca.data_final else None

        if existe:
            sql = """
                UPDATE user_geoapolo_dicionario
                SET data_inicial = ?, data_final = ?, flag_bloqueia = ?,
                    tempo_bloqueio_dias = ?, flag_ativar = ?
                WHERE id_palavra = ?
            """
            cursor.execute(sql, [
                str_ini,
                str_fim,
                licenca.flag_bloqueia,
                licenca.tempo_bloqueio_dias,
                licenca.flag_ativar,
                licenca.id_palavra,
            ])
        else:
            sql = """
                INSERT INTO user_geoapolo_dicionario
                (id_palavra, data_inicial, data_final, flag_bloqueia, tempo_bloqueio_dias, flag_ativar)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql, [
                licenca.id_palavra,
                str_ini,
                str_fim,
                licenca.flag_bloqueia,
                licenca.tempo_bloqueio_dias,
                licenca.flag_ativar,
            ])
        self.commit()
        return True

    # -------------------------------------------------------------
    # Manutenção de Versões (USER_geoapolo_novversao)
    # -------------------------------------------------------------
    def listar_versoes(self) -> List[VersaoSistemaDTO]:
        """Lista todas as versões cadastradas ordenadas por idversao desc."""
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT idversao, data_lancamento, textonovaversao, statusversao
            FROM USER_geoapolo_novversao {nolock}
            ORDER BY data_lancamento DESC, idversao DESC
        """
        cursor.execute(sql)
        versoes = []
        for r in cursor.fetchall():
            versoes.append(VersaoSistemaDTO(
                idversao=str(r[0] or "").strip(),
                data_lancamento=str(r[1] or "").strip(),
                textonovaversao=str(r[2] or "").strip(),
                statusversao=str(r[3] or "N").strip().upper(),
            ))
        return versoes

    def obter_versao(self, idversao: str) -> Optional[VersaoSistemaDTO]:
        """Recupera detalhes de uma versão específica."""
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT idversao, data_lancamento, textonovaversao, statusversao
            FROM USER_geoapolo_novversao {nolock}
            WHERE idversao = ?
        """
        cursor.execute(sql, [idversao.strip()])
        r = cursor.fetchone()
        if not r:
            return None
        return VersaoSistemaDTO(
            idversao=str(r[0] or "").strip(),
            data_lancamento=str(r[1] or "").strip(),
            textonovaversao=str(r[2] or "").strip(),
            statusversao=str(r[3] or "N").strip().upper(),
        )

    def salvar_versao(self, dto: VersaoSistemaDTO) -> bool:
        """Salva (insert ou update) uma versão do sistema."""
        cursor = self._get_cursor()
        cursor.execute("SELECT 1 FROM USER_geoapolo_novversao WHERE idversao = ?", [dto.idversao.strip()])
        existe = cursor.fetchone() is not None

        if existe:
            sql = """
                UPDATE USER_geoapolo_novversao
                SET data_lancamento = ?, textonovaversao = ?, statusversao = ?
                WHERE idversao = ?
            """
            cursor.execute(sql, [
                dto.data_lancamento.strip(),
                dto.textonovaversao,
                dto.statusversao.strip().upper(),
                dto.idversao.strip(),
            ])
        else:
            sql = """
                INSERT INTO USER_geoapolo_novversao
                (idversao, data_lancamento, textonovaversao, statusversao)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(sql, [
                dto.idversao.strip(),
                dto.data_lancamento.strip(),
                dto.textonovaversao,
                dto.statusversao.strip().upper(),
            ])
        self.commit()
        return True

    def excluir_versao(self, idversao: str) -> bool:
        """Remove o registro de uma versão do sistema."""
        cursor = self._get_cursor()
        cursor.execute("DELETE FROM USER_geoapolo_novversao WHERE idversao = ?", [idversao.strip()])
        self.commit()
        return True

    # -------------------------------------------------------------
    # Controle de Leitura por Usuário (USER_geoapolo_userversao)
    # -------------------------------------------------------------
    def usuario_ja_viu_versao(self, idversao: str, usucod: str) -> bool:
        """Verifica se o usuário já marcou a leitura das novidades da versão."""
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT COUNT(1) FROM USER_geoapolo_userversao {nolock}
            WHERE idversao = ? AND usucod = ?
        """
        cursor.execute(sql, [idversao.strip(), usucod.strip()])
        row = cursor.fetchone()
        return (row[0] if row else 0) > 0

    def marcar_versao_vista(self, idversao: str, usucod: str) -> bool:
        """Registra que o usuário visualizou as novidades da versão."""
        if self.usuario_ja_viu_versao(idversao, usucod):
            return True

        cursor = self._get_cursor()
        sql = "INSERT INTO USER_geoapolo_userversao (idversao, usucod) VALUES (?, ?)"
        cursor.execute(sql, [idversao.strip(), usucod.strip()])
        self.commit()
        return True
