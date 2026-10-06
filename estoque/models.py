"""
Modelos e DTOs para Gestão de Estoque, Requisições de Materiais e Movimentações.
GeoApolo V5
Clean Architecture: Suporte aos padrões Apolo ERP (REQ_MAT, ITEM_REQ_MAT, MOV_ESTQ, ITEM_MOV_ESTQ).
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class ItemRequisicaoDTO:
    """Item de requisição de material (ITEM_REQ_MAT)."""
    req_num: str = ""
    item_seq: int = 1
    empcod: str = "1.01"
    prodcod_estr: str = ""
    prodnome: str = ""
    unidade: str = "UN"
    qtd_solicitada: float = 0.0
    qtd_atendida: float = 0.0
    saldo_pendente: float = 0.0
    status_item: str = "Pendente"  # Pendente, Atendido Parcial, Atendido, Cancelado
    observacao: str = ""

    @property
    def unidade_medida(self) -> str:
        return self.unidade

    @unidade_medida.setter
    def unidade_medida(self, val: str):
        self.unidade = val or "UN"

    @property
    def unidademedida(self) -> str:
        return self.unidade

    @unidademedida.setter
    def unidademedida(self, val: str):
        self.unidade = val or "UN"

    @property
    def tamanho(self) -> str:
        return self.unidade

    @tamanho.setter
    def tamanho(self, val: str):
        self.unidade = val or "UN"

    @property
    def display_saldo(self) -> str:
        return f"{self.saldo_pendente:.2f}"


@dataclass
class RequisicaoDTO:
    """Cabeçalho de requisição de materiais (REQ_MAT)."""
    req_num: str = ""
    empcod: str = "1.01"
    data_req: str = ""
    tipo_requisicao: str = "Produto"  # 'Produto' ou 'Serviço'
    solicitante_cod: str = ""
    requerente: str = ""
    centro_custo: str = ""
    status: str = "Aberta"  # Aberta, Atendida Parcial, Atendida Total, Cancelada
    observacao: str = ""
    itens: List[ItemRequisicaoDTO] = field(default_factory=list)

    @property
    def total_itens(self) -> int:
        return len(self.itens)

    @property
    def total_solicitado(self) -> float:
        return sum(it.qtd_solicitada for it in self.itens)

    @property
    def total_atendido(self) -> float:
        return sum(it.qtd_atendida for it in self.itens)

    @property
    def total_pendente(self) -> float:
        return sum(it.saldo_pendente for it in self.itens)


@dataclass
class MovimentoEstoqueDTO:
    """Registro de movimentação de estoque (MOV_ESTQ e ITEM_MOV_ESTQ)."""
    mov_chv: int = 0
    empcod: str = "1.01"
    data_movimento: str = ""
    tipo_movimento: str = "S"  # 'E' = Entrada, 'S' = Saída
    prodcod_estr: str = ""
    prodnome: str = ""
    unidade: str = "UN"
    quantidade: float = 0.0
    valor_unitario: float = 0.0
    valor_total: float = 0.0
    origem_movimento: str = "REQUISICAO"  # REQUISICAO, COMPRA, SAIDA_DIRETA, DEVOLUCAO
    doc_origem: str = ""
    centro_custo: str = ""
    codigo_fornecedor: str = ""
    codigo_almoxarifado: str = ""
    descricao_almoxarifado: str = ""
    numero_lote: str = ""
    id_produto_lote: Optional[int] = None
    observacao: str = ""

    @property
    def unidade_medida(self) -> str:
        return self.unidade

    @unidade_medida.setter
    def unidade_medida(self, val: str):
        self.unidade = val or "UN"

    @property
    def unidademedida(self) -> str:
        return self.unidade

    @unidademedida.setter
    def unidademedida(self, val: str):
        self.unidade = val or "UN"

    @property
    def tamanho(self) -> str:
        return self.unidade

    @tamanho.setter
    def tamanho(self, val: str):
        self.unidade = val or "UN"


@dataclass
class FichaEstoqueLinhaDTO:
    """Linha do extrato de Ficha de Estoque (Kardex)."""
    data: str = ""
    doc_num: str = ""
    tipo_mov: str = "E"  # 'E' = Entrada, 'S' = Saída
    origem: str = ""
    qtd_entrada: float = 0.0
    qtd_saida: float = 0.0
    saldo_acumulado: float = 0.0
    observacao: str = ""


@dataclass
class SaldoProdutoDTO:
    """Consulta consolidada de saldo de produto."""
    prodcod_estr: str = ""
    prodnome: str = ""
    unidade: str = "UN"
    nome_grupo: str = ""
    saldo_atual: float = 0.0
    quantidade_reservada: float = 0.0
    saldo_disponivel: float = 0.0

    @property
    def unidade_medida(self) -> str:
        return self.unidade

    @unidade_medida.setter
    def unidade_medida(self, val: str):
        self.unidade = val or "UN"

    @property
    def unidademedida(self) -> str:
        return self.unidade

    @unidademedida.setter
    def unidademedida(self, val: str):
        self.unidade = val or "UN"

    @property
    def tamanho(self) -> str:
        return self.unidade

    @tamanho.setter
    def tamanho(self, val: str):
        self.unidade = val or "UN"


@dataclass
class ResultadoEstoqueDTO:
    """Resultado padronizado de operações de estoque."""
    sucesso: bool = True
    mensagem: str = ""
    codigo: Optional[int] = None
    documento: str = ""


@dataclass
class AlmoxarifadoDTO:
    """Cadastro básico de Almoxarifado."""
    codigo_almoxarifado: str = ""
    descricao: str = ""
    centro_custo: str = ""
    data_criacao: str = ""
    finalidade: str = ""
    status: str = "A"


@dataclass
class ProdutoAlmoxarifadoDTO:
    """Vínculo de Produto com Almoxarifado e saldo específico."""
    id_produto_almoxarifado: int = 0
    codigo_almoxarifado: str = ""
    descricao_almoxarifado: str = ""
    prodcod: int = 0
    prodnome: str = ""
    saldo_atual: float = 0.0
    data_ultima_movimentacao: str = ""
    data_vinculo: str = ""
    status: str = "A"
