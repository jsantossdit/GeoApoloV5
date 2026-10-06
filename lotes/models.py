"""
Modelos e DTOs para Cadastro e Controle de Lotes de Produtos.
GeoApolo V5
Tabela base: user_geoapolo_produto_lote.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class ProdutoLoteDTO:
    """Registro de lote de produto (user_geoapolo_produto_lote)."""
    id_produto_lote: int = 0
    prodcod: int = 0
    prodnome: str = ""
    numero_lote: str = ""
    data_fabricacao: Optional[str] = None  # Formato ISO (YYYY-MM-DD) ou DD/MM/AAAA
    data_validade: Optional[str] = None    # Formato ISO (YYYY-MM-DD) ou DD/MM/AAAA
    quantidade_inicial: float = 0.0
    quantidade_atual: float = 0.0
    data_entrada: str = ""
    entcod_fornecedor: Optional[int] = None
    nome_fornecedor: str = ""
    status: str = "A"                      # 'A' = Ativo, 'I' = Inativo
    observacao: str = ""
    data_cadastro: str = ""
    usucod: str = ""

    @property
    def is_ativo(self) -> bool:
        return self.status == "A"

    @property
    def display_status(self) -> str:
        return "Ativo" if self.status == "A" else "Inativo"

    @property
    def display(self) -> str:
        return f"{self.numero_lote} (Saldo: {self.quantidade_atual:.2f})"


@dataclass
class ResultadoLoteDTO:
    """Resultado padronizado de operações no módulo de lotes."""
    sucesso: bool = True
    mensagem: str = ""
    codigo: Optional[int] = None
    lote: Optional[ProdutoLoteDTO] = None
