"""
Modelos e DTOs para Conciliação de Pagamentos Recorrentes Vindi.
GeoApolo V5
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date


@dataclass
class TransacaoVindiDTO:
    """Registro de transação / fatura recorrente da Vindi."""
    pedido_id: str
    cpf_cnpj: str
    nome_cliente: str
    data_transacao: Optional[date]
    valor_bruto: float
    valor_tarifa: float
    valor_liquido: float
    status_vindi: str = "Paga"
    integrada_apolo: bool = False
    ent_cod: Optional[str] = None
    categoria_cod: Optional[str] = None
    erros: List[str] = field(default_factory=list)

    @property
    def tem_erros(self) -> bool:
        return len(self.erros) > 0


@dataclass
class ResumoConciliacaoVindiDTO:
    """Consolidação financeira e operacional das transações Vindi."""
    total_transacoes: int = 0
    total_bruto: float = 0.0
    total_tarifas: float = 0.0
    total_liquido: float = 0.0
    total_integradas: int = 0
    total_com_inconsistencias: int = 0


@dataclass
class ResultadoIntegracaoVindiDTO:
    """Resultado da operação de integração/conciliação com a base Apolo."""
    sucesso: bool
    mensagem: str
    transacoes_processadas: int = 0
