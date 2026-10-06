"""
Camada de Serviço para Regras de Negócio de Produtos.
GeoApolo V5
Equivalente a unt_cadprodutos do Delphi.
"""

from typing import List, Optional, Tuple
from produtos.models import ProdutoDTO, GrupoProdutoDTO, ResultadoProdutoDTO
from produtos.repository import ProdutosRepository


class ProdutosService:
    """Regras de negócio e validação para cadastro de produtos."""

    def __init__(self, repository: ProdutosRepository):
        self._repo = repository

    def contar_produtos(self) -> int:
        return self._repo.contar_produtos()

    def obter_proximo_codigo(self) -> int:
        return self._repo.obter_proximo_codigo()

    def listar_grupos(self) -> List[GrupoProdutoDTO]:
        return self._repo.listar_grupos()

    def gerar_codigo_configcod(self, tabela: str = "USER_geoapolo_produtos", empresa: str = "1.01") -> int:
        return self._repo.gerar_codigo_configcod(tabela=tabela, empresa=empresa)

    def obter_grupo(self, grupocod: int) -> Optional[GrupoProdutoDTO]:
        if grupocod <= 0:
            return None
        return self._repo.obter_grupo(grupocod)

    def salvar_grupo(self, g: GrupoProdutoDTO, empresa: str = "1.01") -> ResultadoProdutoDTO:
        if not g.nome_grupo or not g.nome_grupo.strip():
            return ResultadoProdutoDTO(sucesso=False, mensagem="O nome do grupo de produtos é obrigatório.")

        g.nome_grupo = g.nome_grupo.strip().upper()
        g.codigo_estruturado = (g.codigo_estruturado or "").strip().upper()

        if g.grupocod <= 0:
            g.grupocod = self._repo.gerar_codigo_configcod(tabela="USER_geoapolo_produto_grupo", empresa=empresa)

        try:
            self._repo.salvar_grupo(g)
            return ResultadoProdutoDTO(
                sucesso=True,
                mensagem=f"Grupo '{g.nome_grupo}' (Cód: {g.grupocod}) gravado com sucesso!",
                codigo=g.grupocod,
            )
        except Exception as e:
            return ResultadoProdutoDTO(sucesso=False, mensagem=f"Erro ao salvar grupo: {str(e)}")

    def excluir_grupo(self, grupocod: int) -> ResultadoProdutoDTO:
        if grupocod <= 0:
            return ResultadoProdutoDTO(sucesso=False, mensagem="Código de grupo inválido para exclusão.")
        try:
            grp = self._repo.obter_grupo(grupocod)
            nome = grp.nome_grupo if grp else str(grupocod)
            self._repo.excluir_grupo(grupocod)
            return ResultadoProdutoDTO(
                sucesso=True,
                mensagem=f"Grupo '{nome}' (Cód: {grupocod}) excluído com sucesso!",
                codigo=grupocod,
            )
        except Exception as e:
            return ResultadoProdutoDTO(sucesso=False, mensagem=f"Erro ao excluir grupo: {str(e)}")

    def listar_produtos(self, filtro: str = "", grupocod: Optional[int] = None) -> List[ProdutoDTO]:
        return self._repo.listar_produtos(filtro=filtro, grupocod=grupocod)

    def obter_produto(self, prodcod: int) -> Optional[ProdutoDTO]:
        if prodcod <= 0:
            return None
        return self._repo.obter_produto(prodcod)

    def listar_marcas(self) -> List[Tuple[int, str]]:
        return self._repo.listar_marcas()

    def listar_cores(self) -> List[Tuple[int, str]]:
        return self._repo.listar_cores()

    def obter_ou_criar_marca(self, descricao: str) -> Tuple[int, str]:
        return self._repo.obter_ou_criar_marca(descricao)

    def salvar_produto(self, p: ProdutoDTO) -> ResultadoProdutoDTO:
        """Valida e persiste dados do produto."""
        if not p.prodnome or not p.prodnome.strip():
            return ResultadoProdutoDTO(
                sucesso=False,
                mensagem="A descrição/nome do produto é obrigatória.",
            )

        p.prodnome = p.prodnome.strip().upper()
        p.descricao_alternativa = (p.descricao_alternativa or "").strip().upper()

        # Normalização da Unidade de Medida
        raw_unid = (p.unidade_medida or p.tamanho or "UN").strip().upper()
        if " - " in raw_unid:
            raw_unid = raw_unid.split(" - ")[0].strip()
        mapa_unidades = {
            "UNIDADE": "UN", "UN": "UN",
            "CAIXA": "CX", "CX": "CX",
            "PACOTE": "PCT", "PCT": "PCT",
            "PECA": "PC", "PEÇA": "PC", "PC": "PC",
            "QUILO": "KG", "QUILOGRAMA": "KG", "KG": "KG",
            "LITRO": "LT", "LT": "LT",
            "METRO": "MT", "MT": "MT",
            "PAR": "PAR",
            "DUZIA": "DZ", "DÚZIA": "DZ", "DZ": "DZ",
            "FARDO": "FD", "FD": "FD",
            "CONJUNTO": "CJ", "CJ": "CJ",
            "ROLO": "RL", "RL": "RL",
            "M2": "M2", "M3": "M3",
        }
        sigla_unid = mapa_unidades.get(raw_unid, raw_unid)
        p.unidade_medida = sigla_unid
        p.tamanho = sigla_unid

        p.codigo_inmetro = (p.codigo_inmetro or "").strip().upper()
        p.codigo_lote = (p.codigo_lote or "").strip().upper()
        p.observacoes = (p.observacoes or "").strip().upper()
        p.nome_marca = (p.nome_marca or "").strip().upper()

        # Se foi informado nome da marca sem código, resolve ou cria automaticamente
        if p.nome_marca and (not p.codigo_marca or p.codigo_marca <= 0):
            cod_m, nome_m = self._repo.obter_ou_criar_marca(p.nome_marca)
            p.codigo_marca = cod_m
            p.nome_marca = nome_m

        if p.prodcod <= 0:
            p.prodcod = self._repo.obter_proximo_codigo()

        try:
            self._repo.salvar_produto(p)
            return ResultadoProdutoDTO(
                sucesso=True,
                mensagem=f"Produto '{p.prodnome}' (Cód: {p.prodcod}) gravado com sucesso!",
                codigo=p.prodcod,
            )
        except Exception as e:
            return ResultadoProdutoDTO(
                sucesso=False,
                mensagem=f"Erro ao salvar produto: {str(e)}",
            )

    def excluir_produto(self, prodcod: int) -> ResultadoProdutoDTO:
        """Exclui o produto especificado."""
        if prodcod <= 0:
            return ResultadoProdutoDTO(
                sucesso=False,
                mensagem="Código de produto inválido para exclusão.",
            )

        try:
            prod = self._repo.obter_produto(prodcod)
            nome = prod.prodnome if prod else str(prodcod)
            self._repo.excluir_produto(prodcod)
            return ResultadoProdutoDTO(
                sucesso=True,
                mensagem=f"Produto '{nome}' (Cód: {prodcod}) excluído com sucesso!",
                codigo=prodcod,
            )
        except Exception as e:
            return ResultadoProdutoDTO(
                sucesso=False,
                mensagem=f"Erro ao excluir produto: {str(e)}",
            )
