"""
Repositório de Dados para Transações Vindi e Conciliação com o Alvo.
GeoApolo V5
"""

import logging
from typing import List, Optional, Tuple
from datetime import date
from entidades.database import obter_conexao_banco
from .models import TransacaoVindiDTO

logger = logging.getLogger(__name__)


class VindiRepository:
    """Acesso ao banco de dados para conciliação das doações e transações da Vindi."""

    def __init__(self, connection=None):
        self._conn = connection
        self._is_sql_server = not hasattr(connection, "isolation_level") if connection is not None else True

    def _get_cursor(self):
        if self._conn is None:
            self._conn = obter_conexao_banco()
            self._is_sql_server = not hasattr(self._conn, "isolation_level")
        return self._conn.cursor()

    def commit(self):
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()

    def rollback(self):
        if self._conn and hasattr(self._conn, "rollback"):
            self._conn.rollback()

    def listar_transacoes(
        self, data_ini: date, data_fim: date, apenas_nao_integradas: bool = False
    ) -> List[TransacaoVindiDTO]:
        cursor = self._get_cursor()
        nolock = "WITH (NOLOCK)" if self._is_sql_server else ""

        # 1. Tenta consultar a View oficial de Conciliação Vindi (VW_USER_ConciliaVindi)
        try:
            sql_view = f"""
                SELECT pedidoid, COALESCE(cpfcnpj, ''), COALESCE(Nome, ''),
                       alterado, COALESCE(precooriginal, 0.0), COALESCE(taxa, 0.0),
                       COALESCE(precopago, 0.0), COALESCE(status, 'Paga'),
                       COALESCE(flagapolo, 'N')
                FROM VW_USER_ConciliaVindi {nolock}
                WHERE CAST(alterado AS date) >= ? AND CAST(alterado AS date) <= ?
            """
            if apenas_nao_integradas:
                sql_view += " AND (flagapolo = 'N' OR flagapolo IS NULL)"

            sql_view += " ORDER BY alterado ASC, pedidoid ASC"
            cursor.execute(sql_view, [data_ini, data_fim])

            resultados = []
            for r in cursor.fetchall():
                dt = r[3].date() if hasattr(r[3], "date") else r[3]
                flag = str(r[8] or "").strip().upper()
                integrada = (flag == "S" or flag == "1" or flag == "SIM")
                resultados.append(
                    TransacaoVindiDTO(
                        pedido_id=str(r[0]).strip(),
                        cpf_cnpj=str(r[1]).strip(),
                        nome_cliente=str(r[2]).strip(),
                        data_transacao=dt,
                        valor_bruto=float(r[4] or 0.0),
                        valor_tarifa=float(r[5] or 0.0),
                        valor_liquido=float(r[6] or 0.0),
                        status_vindi=str(r[7]).strip(),
                        integrada_apolo=integrada,
                    )
                )
            return resultados
        except Exception as e:
            logger.debug("Tentando fallback para transacoes_vindi: %s", e)

        # 2. Fallback para tabela transacoes_vindi (ex: ambientes SQLite ou schemas de teste)
        try:
            sql = f"""
                SELECT pedidoid, COALESCE(cpfcnpj, ''), COALESCE(nomecliente, ''),
                       datatransacao, COALESCE(valorbruto, 0.0), COALESCE(valortarifa, 0.0),
                       COALESCE(valorliquido, 0.0), COALESCE(statusvindi, 'Paga'),
                       COALESCE(integradaapolo, 0), entcod, categcod
                FROM transacoes_vindi {nolock}
                WHERE datatransacao >= ? AND datatransacao <= ?
            """
            if apenas_nao_integradas:
                sql += " AND (integradaapolo = 0 OR integradaapolo IS NULL)"

            sql += " ORDER BY datatransacao ASC, pedidoid ASC"
            cursor.execute(sql, [data_ini, data_fim])

            resultados = []
            for r in cursor.fetchall():
                dt = r[3].date() if hasattr(r[3], "date") else r[3]
                resultados.append(
                    TransacaoVindiDTO(
                        pedido_id=str(r[0]).strip(),
                        cpf_cnpj=str(r[1]).strip(),
                        nome_cliente=str(r[2]).strip(),
                        data_transacao=dt,
                        valor_bruto=float(r[4] or 0.0),
                        valor_tarifa=float(r[5] or 0.0),
                        valor_liquido=float(r[6] or 0.0),
                        status_vindi=str(r[7]).strip(),
                        integrada_apolo=bool(r[8]),
                        ent_cod=str(r[9]).strip() if r[9] else None,
                        categoria_cod=str(r[10]).strip() if r[10] else None,
                    )
                )
            return resultados
        except Exception as ex:
            logger.exception("Erro ao listar transações Vindi: %s", ex)
            return []

    def buscar_entidade_por_cpf(self, cpf: str) -> Optional[Tuple[str, str]]:
        cursor = self._get_cursor()
        nolock = "WITH (NOLOCK)" if self._is_sql_server else ""
        doc_limpo = cpf.replace(".", "").replace("-", "").replace("/", "").strip()

        # Schema padrão do Alvo: EntCpfCgc
        try:
            sql = f"""
                SELECT TOP 1 EntCod, EntNome
                FROM entidade {nolock}
                WHERE REPLACE(REPLACE(REPLACE(COALESCE(EntCpfCgc, ''), '.', ''), '-', ''), '/', '') = ?
            """
            cursor.execute(sql, [doc_limpo])
            r = cursor.fetchone()
            if r:
                return str(r[0]).strip(), str(r[1]).strip()
        except Exception:
            pass

        # Schema alternativo / SQLite: entcpf / entcnpj
        try:
            sql_legado = f"""
                SELECT TOP 1 entcod, entnome
                FROM entidade {nolock}
                WHERE REPLACE(REPLACE(REPLACE(COALESCE(entcpf, ''), '.', ''), '-', ''), '/', '') = ?
                   OR REPLACE(REPLACE(REPLACE(COALESCE(entcnpj, ''), '.', ''), '-', ''), '/', '') = ?
            """
            cursor.execute(sql_legado, [doc_limpo, doc_limpo])
            r = cursor.fetchone()
            if r:
                return str(r[0]).strip(), str(r[1]).strip()
        except Exception:
            pass

        return None

    def buscar_categorias_entidade(self, ent_cod: str) -> List[str]:
        cursor = self._get_cursor()
        nolock = "WITH (NOLOCK)" if self._is_sql_server else ""
        try:
            sql = f"""
                SELECT CategCodEstr
                FROM ent_categ {nolock}
                WHERE EntCod = ?
            """
            cursor.execute(sql, [ent_cod])
            return [str(r[0]).strip() for r in cursor.fetchall()]
        except Exception:
            try:
                sql_legado = f"""
                    SELECT categcodestr
                    FROM ent_categ {nolock}
                    WHERE entcod = ?
                """
                cursor.execute(sql_legado, [ent_cod])
                return [str(r[0]).strip() for r in cursor.fetchall()]
            except Exception:
                return []

    def marcar_transacao_integrada(self, pedido_id: str) -> bool:
        cursor = self._get_cursor()
        # 1. Atualiza USER_YapayTransacoes (tabela oficial)
        try:
            sql = "UPDATE USER_YapayTransacoes SET flagapolo = 'S' WHERE pedidoid = ?"
            cursor.execute(sql, [pedido_id])
            self.commit()
            if cursor.rowcount > 0:
                return True
        except Exception as e:
            logger.warning("Erro ao atualizar USER_YapayTransacoes: %s", e)

        # 2. Fallback para transacoes_vindi (SQLite / mock)
        try:
            sql2 = "UPDATE transacoes_vindi SET integradaapolo = 1 WHERE pedidoid = ?"
            cursor.execute(sql2, [pedido_id])
            self.commit()
            return cursor.rowcount > 0
        except Exception as e:
            self.rollback()
            logger.exception("Erro ao marcar transação integrada: %s", e)
            return False
