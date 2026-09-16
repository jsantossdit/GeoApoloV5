"""
Camada de Serviços e Auditoria Fiscal de Cupons.
GeoApolo V5
"""

import logging
from typing import List, Tuple
from datetime import date
from .models import (
    AuditoriaCupomDTO,
    ResumoAuditoriaCupomDTO,
    ResultadoSincronizacaoCupomDTO,
)
from .repository import FiscalRepository

logger = logging.getLogger(__name__)


class FiscalService:
    """Regras de auditoria e sincronização entre PDV e retaguarda Apolo."""

    def __init__(self, repository: FiscalRepository):
        self._repo = repository

    def executar_auditoria(
        self, data_ini: date, data_fim: date
    ) -> Tuple[List[AuditoriaCupomDTO], ResumoAuditoriaCupomDTO]:
        if data_ini > data_fim:
            raise ValueError("A data inicial não pode ser superior à data final.")

        cupons = self._repo.listar_cupons_pdv(data_ini, data_fim)

        resumo = ResumoAuditoriaCupomDTO(
            total_cupons=len(cupons),
            total_transmitidos=sum(1 for c in cupons if c.status_sefaz == "Transmitiu"),
            total_nao_transmitidos=sum(1 for c in cupons if c.status_sefaz != "Transmitiu"),
            total_integrados=sum(1 for c in cupons if c.integrado_alvo),
            total_pendentes=sum(1 for c in cupons if c.eh_pendente),
            total_integrados_financ=sum(1 for c in cupons if c.integrado_financ),
            total_integrados_fiscal=sum(1 for c in cupons if c.integrado_fiscal),
            total_baixou_estoque=sum(1 for c in cupons if c.baixou_estoque),
        )
        return cupons, resumo

    def sincronizar_flags_com_apolo(
        self, cupons: List[AuditoriaCupomDTO]
    ) -> ResultadoSincronizacaoCupomDTO:
        if not cupons:
            return ResultadoSincronizacaoCupomDTO(True, "Nenhum cupom para sincronizar.", 0)

        atualizados = 0
        for c in cupons:
            # Se consta no Apolo mas está marcado como não integrado no PDV
            try:
                if self._repo.verificar_cupom_no_apolo(c.numero, c.serie):
                    if not c.integrado_alvo:
                        if self._repo.atualizar_flags_pdv(c.numero, "Sim", "Sim", "Sim", "Sim"):
                            c.integrado_alvo = True
                            c.integrado_financ = True
                            c.integrado_fiscal = True
                            c.baixou_estoque = True
                            atualizados += 1
            except Exception as e:
                logger.warning("Falha ao verificar cupom %s: %s", c.numero, e)

        return ResultadoSincronizacaoCupomDTO(
            sucesso=True,
            mensagem=f"Sincronização concluída! {atualizados} cupons atualizados no PDV.",
            cupons_atualizados=atualizados,
        )
