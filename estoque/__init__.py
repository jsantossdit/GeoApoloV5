"""
Módulo de Estoque, Requisições e Movimentações - GeoApolo V5.
Clean Architecture: Models, Repository, Service e Views.
"""

from .models import (
    RequisicaoDTO,
    ItemRequisicaoDTO,
    MovimentoEstoqueDTO,
    FichaEstoqueLinhaDTO,
    SaldoProdutoDTO,
    ResultadoEstoqueDTO,
)
from .repository import EstoqueRepository
from .service import EstoqueService
from .nova_requisicao_view import (
    NovaRequisicaoView,
    abrir_nova_requisicao_material,
)
from .requisicoes_view import (
    RequisicoesView,
    abrir_atendimento_requisicoes,
    abrir_cancelamento_requisicoes,
    abrir_devolucao_requisicoes,
)
from .movimentacao_view import (
    MovimentacaoView,
    abrir_movimentacao_estoque,
)
from .consultas_view import (
    ConsultasEstoqueView,
    abrir_consulta_ficha_estoque,
    abrir_consulta_saldo_produto,
    abrir_consulta_requisicoes,
)

__all__ = [
    "RequisicaoDTO",
    "ItemRequisicaoDTO",
    "MovimentoEstoqueDTO",
    "FichaEstoqueLinhaDTO",
    "SaldoProdutoDTO",
    "ResultadoEstoqueDTO",
    "EstoqueRepository",
    "EstoqueService",
    "NovaRequisicaoView",
    "abrir_nova_requisicao_material",
    "RequisicoesView",
    "abrir_atendimento_requisicoes",
    "abrir_cancelamento_requisicoes",
    "abrir_devolucao_requisicoes",
    "MovimentacaoView",
    "abrir_movimentacao_estoque",
    "ConsultasEstoqueView",
    "abrir_consulta_ficha_estoque",
    "abrir_consulta_saldo_produto",
    "abrir_consulta_requisicoes",
]
