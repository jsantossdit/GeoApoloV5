"""
Modelos e DTOs para Módulo Contábil e Financeiro.
GeoApolo V5
"""

from dataclasses import dataclass
from typing import Optional
from datetime import date, datetime


@dataclass
class LancamentoContabilDTO:
    """Representa um registro de lançamento contábil."""
    chave: str
    numero_origem: str
    origem_chave: str
    modulo: str
    submodulo: str
    data: Optional[date]
    empresa_cod: str
    valor: float
    historico: str
    conta_debito: str
    conta_credito: str


@dataclass
class ValidacaoExclusaoDTO:
    """Resultado da validação de integridade referencial antes da exclusão."""
    permitido: bool
    mensagem: str
    origem_detectada: str = ""


@dataclass
class FiltroExclusaoModuloDTO:
    """Filtro para exclusão contábil em lote por período e módulo."""
    data_inicial: date
    data_final: date
    modulo: str = ""
    submodulo: str = ""
    empresa_cod: str = "001"


@dataclass
class ResultadoExclusaoContabilDTO:
    """Resultado de operações de exclusão individual ou em lote."""
    sucesso: bool
    mensagem: str
    registros_excluidos: int = 0


@dataclass
class DebxCredItemDTO:
    """Item do relatório de conciliação Débito x Crédito."""
    chave: str
    data: Optional[date]
    conta_debito: str
    conta_credito: str
    valor_debito: float
    valor_credito: float
    historico: str
    documento: str = ""
    modulo_origem: str = ""

    @property
    def eh_divergente(self) -> bool:
        return abs(self.valor_debito - self.valor_credito) > 0.001


@dataclass
class ResumoConciliacaoDTO:
    """Estatísticas consolidadas da conciliação contábil."""
    total_debito: float = 0.0
    total_credito: float = 0.0
    saldo_divergencia: float = 0.0
    total_registros: int = 0
    total_divergentes: int = 0
