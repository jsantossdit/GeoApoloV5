"""
Repositório de Acesso a Dados para o Módulo Contábil e Financeiro.
Preserva otimizações WITH (NOLOCK) e transações atômicas no SQL Server.
"""

import logging
from typing import List, Optional
from datetime import date
from entidades.database import obter_conexao_banco
from .models import (
    LancamentoContabilDTO,
    ValidacaoExclusaoDTO,
    FiltroExclusaoModuloDTO,
    ResultadoExclusaoContabilDTO,
    DebxCredItemDTO,
)

logger = logging.getLogger(__name__)


class ContabilidadeRepository:
    """Operações de banco de dados para lançamentos e conciliação contábil."""

    def __init__(self, connection=None):
        self._conn = connection

    def _get_cursor(self):
        if self._conn is None:
            self._conn = obter_conexao_banco()
        return self._conn.cursor()

    def commit(self):
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()

    def rollback(self):
        if self._conn and hasattr(self._conn, "rollback"):
            self._conn.rollback()

    def pesquisar_lancamentos(
        self,
        campo: str = "contablancchv",
        valor: str = "",
        empresa_cod: str = "001",
        origem: str = "",
        limite: int = 200,
    ) -> List[LancamentoContabilDTO]:
        campo_map = {
            "contablancchv": "cl.contablancchv",
            "contablancorignum": "cl.contablancorignum",
            "contablancmod": "cl.contablancmod",
            "contablancctadeb": "cl.contablancctadeb",
            "contablancctacred": "cl.contablancctacred",
        }
        coluna = campo_map.get(campo.lower(), "cl.contablancchv")
        cursor = self._get_cursor()

        sql = f"""
            SELECT TOP ({limite})
                cl.contablancchv, cl.contablancorignum, cl.contablancorigchv,
                cl.contablancmod, cl.contablancmodfin, cl.contablancdata, cl.planoctaempcod,
                cl.contablancval, ISNULL(cl.contablanchist, ''),
                ISNULL(cl.contablancctadeb, ''), ISNULL(cl.contablancctacred, '')
            FROM contab_lancamento cl WITH (NOLOCK)
            WHERE cl.planoctaempcod = ?
        """
        params = [empresa_cod]

        if valor and valor.strip():
            sql += f" AND {coluna} LIKE ?"
            params.append(f"%{valor.strip()}%")

        if origem and origem.strip():
            sql += " AND cl.contablancmod = ?"
            params.append(origem.strip())

        sql += " ORDER BY cl.contablancdata DESC, cl.contablancchv DESC"
        cursor.execute(sql, params)

        resultados = []
        for r in cursor.fetchall():
            dt = r[5].date() if hasattr(r[5], "date") else r[5]
            resultados.append(
                LancamentoContabilDTO(
                    chave=str(r[0]).strip(),
                    numero_origem=str(r[1]).strip() if r[1] else "",
                    origem_chave=str(r[2]).strip() if r[2] else "",
                    modulo=str(r[3]).strip() if r[3] else "",
                    submodulo=str(r[4]).strip() if r[4] else "",
                    data=dt,
                    empresa_cod=str(r[6]).strip(),
                    valor=float(r[7]) if r[7] is not None else 0.0,
                    historico=str(r[8]).strip(),
                    conta_debito=str(r[9]).strip(),
                    conta_credito=str(r[10]).strip(),
                )
            )
        return resultados

    def obter_lancamento(self, chave: str) -> Optional[LancamentoContabilDTO]:
        cursor = self._get_cursor()
        sql = """
            SELECT cl.contablancchv, cl.contablancorignum, cl.contablancorigchv,
                   cl.contablancmod, cl.contablancmodfin, cl.contablancdata, cl.planoctaempcod,
                   cl.contablancval, ISNULL(cl.contablanchist, ''),
                   ISNULL(cl.contablancctadeb, ''), ISNULL(cl.contablancctacred, '')
            FROM contab_lancamento cl WITH (NOLOCK)
            WHERE cl.contablancchv = ?
        """
        cursor.execute(sql, [chave])
        r = cursor.fetchone()
        if not r:
            return None

        dt = r[5].date() if hasattr(r[5], "date") else r[5]
        return LancamentoContabilDTO(
            chave=str(r[0]).strip(),
            numero_origem=str(r[1]).strip() if r[1] else "",
            origem_chave=str(r[2]).strip() if r[2] else "",
            modulo=str(r[3]).strip() if r[3] else "",
            submodulo=str(r[4]).strip() if r[4] else "",
            data=dt,
            empresa_cod=str(r[6]).strip(),
            valor=float(r[7]) if r[7] is not None else 0.0,
            historico=str(r[8]).strip(),
            conta_debito=str(r[9]).strip(),
            conta_credito=str(r[10]).strip(),
        )

    def validar_integridade_origem(self, lanc: LancamentoContabilDTO) -> ValidacaoExclusaoDTO:
        cursor = self._get_cursor()

        # 1. Financeiro Realizado -> bancário
        if lanc.modulo.lower() == "financeiro" and "realizado" in lanc.submodulo.lower():
            if lanc.numero_origem:
                cursor.execute(
                    "SELECT TOP 1 movctrlbancnum FROM lanc_mov_ctrl_banc WITH (NOLOCK) WHERE movctrlbancnum = ?",
                    [lanc.numero_origem],
                )
                if cursor.fetchone():
                    return ValidacaoExclusaoDTO(
                        permitido=False,
                        mensagem=f"Lançamento possui origem no Movimento Bancário (Nº {lanc.numero_origem}). Estorne pela tesouraria.",
                        origem_detectada=lanc.numero_origem,
                    )

        # 2. Financeiro Id.Depósito -> bancário entidades
        if lanc.modulo.lower() == "financeiro" and "dep" in lanc.submodulo.lower():
            if lanc.numero_origem:
                cursor.execute(
                    "SELECT TOP 1 movctrlbancnum FROM lanc_mov_ctrl_banc_ent WITH (NOLOCK) WHERE movctrlbancnum = ?",
                    [lanc.numero_origem],
                )
                if cursor.fetchone():
                    return ValidacaoExclusaoDTO(
                        permitido=False,
                        mensagem=f"Lançamento vinculado a Depósitos de Entidades (Nº {lanc.numero_origem}).",
                        origem_detectada=lanc.numero_origem,
                    )

        # 3. Financeiro Provisão -> contas a pagar/receber
        if lanc.modulo.lower() == "financeiro" and "prov" in lanc.submodulo.lower():
            if lanc.origem_chave:
                cursor.execute(
                    "SELECT TOP 1 docfinchv FROM doc_fin WITH (NOLOCK) WHERE docfinchv = ?",
                    [lanc.origem_chave],
                )
                if cursor.fetchone():
                    return ValidacaoExclusaoDTO(
                        permitido=False,
                        mensagem=f"Lançamento possui origem em Título a Pagar/Receber (Chave {lanc.origem_chave}).",
                        origem_detectada=lanc.origem_chave,
                    )

        # 4. Estoque -> mov_estq
        if lanc.modulo.lower() == "estoque":
            if lanc.origem_chave:
                cursor.execute(
                    "SELECT TOP 1 movestqchv FROM mov_estq WITH (NOLOCK) WHERE movestqchv = ?",
                    [lanc.origem_chave],
                )
                if cursor.fetchone():
                    return ValidacaoExclusaoDTO(
                        permitido=False,
                        mensagem=f"Lançamento originado de Movimentação de Estoque (Chave {lanc.origem_chave}).",
                        origem_detectada=lanc.origem_chave,
                    )

        # 5. Vendas -> nota fiscal
        if lanc.modulo.lower() == "vendas":
            if lanc.numero_origem:
                cursor.execute(
                    "SELECT TOP 1 nfnum FROM nota_fiscal WITH (NOLOCK) WHERE nfnum = ?",
                    [lanc.numero_origem],
                )
                if cursor.fetchone():
                    return ValidacaoExclusaoDTO(
                        permitido=False,
                        mensagem=f"Lançamento originado de Nota Fiscal (Nº {lanc.numero_origem}).",
                        origem_detectada=lanc.numero_origem,
                    )

        return ValidacaoExclusaoDTO(permitido=True, mensagem="Exclusão permitida.")

    def excluir_lancamento(self, chave: str, usuario: str = "") -> ResultadoExclusaoContabilDTO:
        cursor = self._get_cursor()
        try:
            sql = "DELETE FROM contab_lancamento WHERE contablancchv = ?"
            cursor.execute(sql, [chave])
            afetados = cursor.rowcount if cursor.rowcount > 0 else 0
            self.commit()
            return ResultadoExclusaoContabilDTO(
                sucesso=True,
                mensagem=f"Lançamento contábil '{chave}' excluído com sucesso.",
                registros_excluidos=afetados,
            )
        except Exception as e:
            self.rollback()
            logger.exception("Erro ao excluir lançamento contábil: %s", e)
            return ResultadoExclusaoContabilDTO(
                sucesso=False,
                mensagem=f"Erro ao excluir lançamento contábil:\n{e}",
                registros_excluidos=0,
            )

    def pesquisar_por_modulo(self, filtro: FiltroExclusaoModuloDTO) -> List[LancamentoContabilDTO]:
        cursor = self._get_cursor()
        sql = """
            SELECT cl.contablancchv, cl.contablancorignum, cl.contablancorigchv,
                   cl.contablancmod, cl.contablancmodfin, cl.contablancdata, cl.planoctaempcod,
                   cl.contablancval, ISNULL(cl.contablanchist, ''),
                   ISNULL(cl.contablancctadeb, ''), ISNULL(cl.contablancctacred, '')
            FROM contab_lancamento cl WITH (NOLOCK)
            WHERE cl.contablancdata >= ? AND cl.contablancdata <= ?
              AND cl.planoctaempcod = ?
        """
        params = [filtro.data_inicial, filtro.data_final, filtro.empresa_cod]

        if filtro.modulo:
            sql += " AND cl.contablancmod = ?"
            params.append(filtro.modulo)

        if filtro.submodulo:
            sql += " AND cl.contablancmodfin = ?"
            params.append(filtro.submodulo)

        sql += " ORDER BY cl.contablancdata ASC"
        cursor.execute(sql, params)

        resultados = []
        for r in cursor.fetchall():
            dt = r[5].date() if hasattr(r[5], "date") else r[5]
            resultados.append(
                LancamentoContabilDTO(
                    chave=str(r[0]).strip(),
                    numero_origem=str(r[1]).strip() if r[1] else "",
                    origem_chave=str(r[2]).strip() if r[2] else "",
                    modulo=str(r[3]).strip() if r[3] else "",
                    submodulo=str(r[4]).strip() if r[4] else "",
                    data=dt,
                    empresa_cod=str(r[6]).strip(),
                    valor=float(r[7]) if r[7] is not None else 0.0,
                    historico=str(r[8]).strip(),
                    conta_debito=str(r[9]).strip(),
                    conta_credito=str(r[10]).strip(),
                )
            )
        return resultados

    def excluir_em_lote_por_modulo(
        self, filtro: FiltroExclusaoModuloDTO, usuario: str = ""
    ) -> ResultadoExclusaoContabilDTO:
        cursor = self._get_cursor()
        try:
            sql = """
                DELETE FROM contab_lancamento
                WHERE contablancdata >= ? AND contablancdata <= ?
                  AND planoctaempcod = ?
            """
            params = [filtro.data_inicial, filtro.data_final, filtro.empresa_cod]

            if filtro.modulo:
                sql += " AND contablancmod = ?"
                params.append(filtro.modulo)

            if filtro.submodulo:
                sql += " AND contablancmodfin = ?"
                params.append(filtro.submodulo)

            cursor.execute(sql, params)
            afetados = cursor.rowcount if cursor.rowcount > 0 else 0
            self.commit()
            return ResultadoExclusaoContabilDTO(
                sucesso=True,
                mensagem=f"Exclusão em lote concluída. {afetados} lançamentos removidos.",
                registros_excluidos=afetados,
            )
        except Exception as e:
            self.rollback()
            logger.exception("Erro na exclusão em lote por módulo: %s", e)
            return ResultadoExclusaoContabilDTO(
                sucesso=False,
                mensagem=f"Erro na exclusão em lote:\n{e}",
                registros_excluidos=0,
            )

    def conciliar_debxcred(
        self,
        data_ini: date,
        data_fim: date,
        cod_reduzido: Optional[str] = None,
        somente_divergentes: bool = False,
    ) -> List[DebxCredItemDTO]:
        cursor = self._get_cursor()
        sql = """
            SELECT cl.contablancchv, cl.contablancdata,
                   ISNULL(cl.contablancctadeb, ''), ISNULL(cl.contablancctacred, ''),
                   CASE WHEN cl.contablancctadeb IS NOT NULL AND cl.contablancctadeb <> '' THEN cl.contablancval ELSE 0.0 END AS val_debito,
                   CASE WHEN cl.contablancctacred IS NOT NULL AND cl.contablancctacred <> '' THEN cl.contablancval ELSE 0.0 END AS val_credito,
                   ISNULL(cl.contablanchist, ''), ISNULL(cl.contablancorignum, ''),
                   ISNULL(cl.contablancmod, '')
            FROM contab_lancamento cl WITH (NOLOCK)
            WHERE cl.contablancdata >= ? AND cl.contablancdata <= ?
        """
        params = [data_ini, data_fim]

        if cod_reduzido and cod_reduzido.strip():
            sql += " AND (cl.contablancctadeb = ? OR cl.contablancctacred = ?)"
            params.extend([cod_reduzido.strip(), cod_reduzido.strip()])

        sql += " ORDER BY cl.contablancdata ASC, cl.contablancchv ASC"
        cursor.execute(sql, params)

        itens = []
        for r in cursor.fetchall():
            dt = r[1].date() if hasattr(r[1], "date") else r[1]
            val_deb = float(r[4]) if r[4] is not None else 0.0
            val_cred = float(r[5]) if r[5] is not None else 0.0
            item = DebxCredItemDTO(
                chave=str(r[0]).strip(),
                data=dt,
                conta_debito=str(r[2]).strip(),
                conta_credito=str(r[3]).strip(),
                valor_debito=val_deb,
                valor_credito=val_cred,
                historico=str(r[6]).strip(),
                documento=str(r[7]).strip(),
                modulo_origem=str(r[8]).strip(),
            )
            if somente_divergentes and not item.eh_divergente:
                continue
            itens.append(item)
        return itens

    def obter_nome_conta_contabil(self, cod_reduzido: str) -> str:
        cursor = self._get_cursor()
        sql = """
            SELECT TOP 1 planoctanome
            FROM plano_cta WITH (NOLOCK)
            WHERE planoctared = ?
        """
        cursor.execute(sql, [cod_reduzido.strip()])
        r = cursor.fetchone()
        return str(r[0]).strip() if r else ""
