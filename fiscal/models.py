"""
Modelos e DTOs para Auditoria Fiscal de Cupons (NFC-e / PDV).
GeoApolo V5
"""

from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass
class AuditoriaCupomDTO:
    """Registro auditado de uma NFC-e emitida no Caixa/PDV."""
    empresa_cod: str
    entidade_cod: str
    entidade_nome: str
    serie: str
    numero: str
    valor_total: float
    status_sefaz: str  # 'Transmitiu' ou 'Não Transmitiu'
    integrado_alvo: bool
    integrado_financ: bool
    integrado_fiscal: bool
    baixou_estoque: bool

    @property
    def eh_pendente(self) -> bool:
        return not (self.integrado_alvo and self.integrado_financ and self.integrado_fiscal and self.baixou_estoque)


@dataclass
class ResumoAuditoriaCupomDTO:
    """Resumo estatístico consolidado do caixa."""
    total_cupons: int = 0
    total_transmitidos: int = 0
    total_nao_transmitidos: int = 0
    total_integrados: int = 0
    total_pendentes: int = 0
    total_integrados_financ: int = 0
    total_integrados_fiscal: int = 0
    total_baixou_estoque: int = 0


@dataclass
class ResultadoSincronizacaoCupomDTO:
    """Resultado da conciliação e sincronização de flags com a base Apolo."""
    sucesso: bool
    mensagem: str
    cupons_atualizados: int = 0
