"""
Modelos de dados e DTOs para Cadastro e Manutenção de Produtos.
GeoApolo V5
Equivalente a unt_cadprodutos.pas do Delphi.
"""

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class GrupoProdutoDTO:
    """Grupo de produtos (USER_geoapolo_produto_grupo)."""
    grupocod: int = 0
    codigo_estruturado: str = ""
    nome_grupo: str = ""

    @property
    def display(self) -> str:
        if self.codigo_estruturado:
            return f"{self.codigo_estruturado} - {self.nome_grupo}"
        return f"{self.grupocod:02d} - {self.nome_grupo}"


@dataclass
class ProdutoDTO:
    """Produto (USER_geoapolo_produtos)."""
    prodcod: int = 0
    prodnome: str = ""
    descricao_alternativa: str = ""
    grupocod: Optional[int] = None
    nome_grupo: str = ""
    codigo_marca: Optional[int] = None
    nome_marca: str = ""
    cores_codigos: List[int] = field(default_factory=list)
    cores_nomes: List[str] = field(default_factory=list)
    unidade_medida: str = ""
    tamanho: str = ""
    codigo_inmetro: str = ""
    codigo_lote: str = ""
    observacoes: str = ""

    def __post_init__(self):
        if not self.unidade_medida and self.tamanho:
            self.unidade_medida = self.tamanho
        elif not self.tamanho and self.unidade_medida:
            self.tamanho = self.unidade_medida
        elif not self.unidade_medida and not self.tamanho:
            self.unidade_medida = "UN"
            self.tamanho = "UN"

    @property
    def display_cores(self) -> str:
        return ", ".join(self.cores_nomes) if self.cores_nomes else "-"

    @property
    def display(self) -> str:
        return f"{self.prodcod} - {self.prodnome}"


@dataclass
class ResultadoProdutoDTO:
    """Resultado padronizado de operações do cadastro de produtos."""
    sucesso: bool = True
    mensagem: str = ""
    codigo: Optional[int] = None
