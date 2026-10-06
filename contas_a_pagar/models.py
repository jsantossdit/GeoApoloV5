"""
Modelos e DTOs para o Módulo de Contas a Pagar / Documentos Financeiros.
GeoApolo V5
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import date, datetime


@dataclass
class DocumentoPagarDTO:
    """Representa um documento/título financeiro de contas a pagar."""
    codigo_documento: Optional[int] = None
    codigo_empresa: str = "1.01"
    numero_documento: str = ""
    serie_documento: str = "1"
    parcela: int = 1
    total_parcelas: int = 1
    entcod: str = ""
    fornecedor_nome: str = ""
    cnpj_cpf: str = ""
    data_emissao: str = ""      # YYYY-MM-DD
    data_vencimento: str = ""   # YYYY-MM-DD
    data_pagamento: Optional[str] = None  # YYYY-MM-DD
    valor_original: float = 0.0
    valor_desconto: float = 0.0
    valor_juros_multa: float = 0.0
    valor_pago: float = 0.0
    saldo_aberto: float = 0.0
    situacao: str = "ABERTO"    # ABERTO, QUITADO, CANCELADO
    tipo_documento: str = "ENTRADA_ESTOQUE"
    origem: str = "COMPRA_ESTOQUE"
    centro_custo: str = ""
    codigo_movimento_estoque: Optional[int] = None
    observacoes: str = ""
    data_inclusao: Optional[str] = None
    usuario_inclusao: str = ""

    @property
    def display_valor(self) -> str:
        return f"R$ {self.valor_original:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @property
    def display_saldo(self) -> str:
        return f"R$ {self.saldo_aberto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@dataclass
class FiltroContasPagarDTO:
    """Filtros para listagem e conciliação de contas a pagar."""
    codigo_empresa: str = "1.01"
    data_ini: Optional[str] = None
    data_fim: Optional[str] = None
    situacao: str = "TODAS"  # TODAS, ABERTO, QUITADO, CANCELADO
    termo_busca: str = ""    # Busca por fornecedor, número doc ou código
    centro_custo: str = ""


@dataclass
class ResumoContasPagarDTO:
    """Totalizadores e indicadores da grade financeira."""
    total_titulos: int = 0
    total_original: float = 0.0
    total_aberto: float = 0.0
    total_pago: float = 0.0
    qtd_abertos: int = 0
    qtd_quitados: int = 0


@dataclass
class BaixaDocumentoDTO:
    """Parâmetros para baixa/quitação total ou parcial de um título."""
    codigo_documento: int
    data_pagamento: str  # YYYY-MM-DD
    valor_pago: float
    valor_desconto: float = 0.0
    valor_juros_multa: float = 0.0
    observacao_baixa: str = ""
