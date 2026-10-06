"""
Módulo de Cadastro e Manutenção de Produtos.
GeoApolo V5
Equivalente a unt_cadprodutos do Delphi.
"""

from produtos.models import ProdutoDTO, GrupoProdutoDTO, ResultadoProdutoDTO
from produtos.repository import ProdutosRepository
from produtos.service import ProdutosService
from produtos.view import ProdutosView, abrir_janela_produtos
from produtos.grupos_view import GruposProdutosView, abrir_janela_grupos_produtos

__all__ = [
    "ProdutoDTO",
    "GrupoProdutoDTO",
    "ResultadoProdutoDTO",
    "ProdutosRepository",
    "ProdutosService",
    "ProdutosView",
    "abrir_janela_produtos",
    "GruposProdutosView",
    "abrir_janela_grupos_produtos",
]
