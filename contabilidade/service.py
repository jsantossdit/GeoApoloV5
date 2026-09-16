"""
Camada de Serviços e Regras de Negócio para o Módulo Contábil e Financeiro.
GeoApolo V5
"""

import logging
from typing import List, Optional, Tuple
from datetime import date
from .models import (
    LancamentoContabilDTO,
    ValidacaoExclusaoDTO,
    FiltroExclusaoModuloDTO,
    ResultadoExclusaoContabilDTO,
    DebxCredItemDTO,
    ResumoConciliacaoDTO,
)
from .repository import ContabilidadeRepository

logger = logging.getLogger(__name__)


class ContabilidadeService:
    """Regras de validação, auditoria de integridade e conciliação contábil."""

    def __init__(self, repository: ContabilidadeRepository):
        self._repo = repository

    def pesquisar_lancamentos(
        self,
        campo: str = "contablancchv",
        valor: str = "",
        empresa_cod: str = "001",
        origem: str = "",
        limite: int = 200,
    ) -> List[LancamentoContabilDTO]:
        return self._repo.pesquisar_lancamentos(campo, valor, empresa_cod, origem, limite)

    def obter_lancamento(self, chave: str) -> Optional[LancamentoContabilDTO]:
        chv = str(chave or "").strip()
        if not chv:
            return None
        return self._repo.obter_lancamento(chv)

    def validar_exclusao(self, chave: str) -> ValidacaoExclusaoDTO:
        chv = str(chave or "").strip()
        if not chv:
            return ValidacaoExclusaoDTO(False, "Informe o número de chave do lançamento.")

        lanc = self._repo.obter_lancamento(chv)
        if not lanc:
            return ValidacaoExclusaoDTO(False, f"Lançamento contábil '{chv}' não encontrado.")

        return self._repo.validar_integridade_origem(lanc)

    def excluir_lancamento(
        self, chave: str, usuario: str = "", forcar: bool = False
    ) -> ResultadoExclusaoContabilDTO:
        chv = str(chave or "").strip()
        if not chv:
            return ResultadoExclusaoContabilDTO(False, "Chave do lançamento é obrigatória.")

        if not forcar:
            val = self.validar_exclusao(chv)
            if not val.permitido:
                return ResultadoExclusaoContabilDTO(False, val.mensagem, 0)

        return self._repo.excluir_lancamento(chv, usuario)

    def pesquisar_por_modulo(self, filtro: FiltroExclusaoModuloDTO) -> List[LancamentoContabilDTO]:
        if filtro.data_inicial > filtro.data_final:
            raise ValueError("A data inicial não pode ser maior que a data final.")
        return self._repo.pesquisar_por_modulo(filtro)

    def excluir_em_lote_por_modulo(
        self, filtro: FiltroExclusaoModuloDTO, usuario: str = ""
    ) -> ResultadoExclusaoContabilDTO:
        if filtro.data_inicial > filtro.data_final:
            return ResultadoExclusaoContabilDTO(False, "Data inicial superior à data final.")
        return self._repo.excluir_em_lote_por_modulo(filtro, usuario)

    def conciliar_debxcred(
        self,
        data_ini: date,
        data_fim: date,
        cod_reduzido: Optional[str] = None,
        somente_divergentes: bool = False,
    ) -> Tuple[List[DebxCredItemDTO], ResumoConciliacaoDTO]:
        if data_ini > data_fim:
            raise ValueError("A data inicial não pode ser superior à data final.")

        itens = self._repo.conciliar_debxcred(data_ini, data_fim, cod_reduzido, somente_divergentes)

        total_deb = sum(it.valor_debito for it in itens)
        total_cred = sum(it.valor_credito for it in itens)
        saldo = total_deb - total_cred
        divergentes = sum(1 for it in itens if it.eh_divergente)

        resumo = ResumoConciliacaoDTO(
            total_debito=round(total_deb, 2),
            total_credito=round(total_cred, 2),
            saldo_divergencia=round(saldo, 2),
            total_registros=len(itens),
            total_divergentes=divergentes,
        )
        return itens, resumo

    def obter_nome_conta_contabil(self, cod_reduzido: str) -> str:
        cod = str(cod_reduzido or "").strip()
        if not cod:
            return ""
        return self._repo.obter_nome_conta_contabil(cod)
