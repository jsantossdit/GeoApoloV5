"""
Camada de Serviços e Regras de Negócio para Gestão de Lotes de Produtos.
GeoApolo V5
Validações de datas, quantidades, unicidade e regras de negócio.
"""

import logging
from typing import List, Optional, Tuple
from datetime import datetime

from .models import ProdutoLoteDTO, ResultadoLoteDTO
from .repository import LotesRepository

logger = logging.getLogger(__name__)


class LotesService:
    """Serviço com regras de negócio para Lotes de Produtos."""

    def __init__(self, repository: LotesRepository):
        self._repo = repository

    def listar_lotes(
        self,
        prodcod: Optional[int] = None,
        termo: str = "",
        apenas_ativos: bool = False,
    ) -> List[ProdutoLoteDTO]:
        """Lista lotes cadastrados com filtros."""
        return self._repo.listar_lotes(prodcod=prodcod, termo=termo, apenas_ativos=apenas_ativos)

    def obter_lote(self, id_produto_lote: int) -> Optional[ProdutoLoteDTO]:
        """Obtém lote por ID."""
        return self._repo.obter_lote_por_id(id_produto_lote)

    def obter_lote_por_numero(self, prodcod: int, numero_lote: str) -> Optional[ProdutoLoteDTO]:
        """Obtém lote por produto e número."""
        return self._repo.obter_lote_por_numero(prodcod, numero_lote)

    def lote_existe(self, prodcod: int, numero_lote: str) -> bool:
        """Verifica se determinado número de lote já existe para o produto."""
        if not prodcod or prodcod <= 0:
            return False
        return self._repo.lote_existe(prodcod, numero_lote)

    def produto_controla_lote(self, prodcod: int) -> bool:
        """Verifica se o produto possui controle de lote no Alvo ou GeoApolo."""
        if not prodcod or prodcod <= 0:
            return False
        return self._repo.produto_controla_lote(prodcod)

    def verificar_vencimento_lote(
        self,
        prodcod: int,
        numero_lote: str,
        data_base: Optional[datetime] = None,
    ) -> Tuple[str, int, str]:
        """
        Calcula os dias restantes para o vencimento do lote e classifica nas faixas de alerta e bloqueio:
        - 'ROXO' (dias <= 5 ou vencido): Alerta roxo e BLOQUEIO OBRIGATÓRIO de atendimento/saída.
        - 'VERMELHO' (5 < dias <= 10): Alerta vermelho de lote muito perto do vencimento.
        - 'AMARELO' (10 < dias <= 30): Alerta amarelo de lote perto do vencimento.
        - 'NORMAL' (dias > 30): Lote regular sem restrições.
        - 'SEM_VALIDADE': Lote sem data de validade informada.
        - 'NAO_ENCONTRADO': Lote não localizado para o produto.

        Retorna: (nivel_alerta, dias_restantes, data_validade_formatada)
        """
        lote = self._repo.obter_lote_por_numero(prodcod, numero_lote)
        if not lote:
            return "NAO_ENCONTRADO", 0, ""

        d_val_str = (lote.data_validade or "").strip()
        if not d_val_str:
            return "SEM_VALIDADE", 9999, ""

        try:
            if "-" in d_val_str:
                dt_val = datetime.strptime(d_val_str[:10], "%Y-%m-%d").date()
            else:
                dt_val = datetime.strptime(d_val_str[:10], "%d/%m/%Y").date()
        except Exception:
            return "SEM_VALIDADE", 9999, d_val_str

        hoje = data_base.date() if isinstance(data_base, datetime) else datetime.now().date()
        dias = (dt_val - hoje).days
        data_fmt = dt_val.strftime("%d/%m/%Y")

        if dias <= 5:
            return "ROXO", dias, data_fmt
        elif 5 < dias <= 10:
            return "VERMELHO", dias, data_fmt
        elif 10 < dias <= 30:
            return "AMARELO", dias, data_fmt
        else:
            return "NORMAL", dias, data_fmt

    def salvar_lote(self, dto: ProdutoLoteDTO) -> ResultadoLoteDTO:
        """Valida e salva lote de produto (inclusão ou edição)."""
        if not dto.prodcod or dto.prodcod <= 0:
            return ResultadoLoteDTO(sucesso=False, mensagem="O Código do Produto é obrigatório e deve ser válido.")

        num_lote = str(dto.numero_lote or "").strip().upper()
        if not num_lote:
            return ResultadoLoteDTO(sucesso=False, mensagem="O Número do Lote é obrigatório.")

        # Validação de unicidade para o mesmo produto
        lote_existente = self._repo.obter_lote_por_numero(dto.prodcod, num_lote)
        if lote_existente and lote_existente.id_produto_lote != dto.id_produto_lote:
            return ResultadoLoteDTO(
                sucesso=False,
                mensagem=f"Já existe um lote cadastrado com o número '{num_lote}' para este produto (ID: {lote_existente.id_produto_lote})."
            )

        # Validação de Quantidades
        try:
            qtd_ini = float(dto.quantidade_inicial)
            qtd_atu = float(dto.quantidade_atual)
        except (ValueError, TypeError):
            return ResultadoLoteDTO(sucesso=False, mensagem="Valores de quantidades inválidos.")

        if qtd_ini < 0 or qtd_atu < 0:
            return ResultadoLoteDTO(sucesso=False, mensagem="As quantidades inicial e atual não podem ser negativas.")

        # Validação de Datas (se ambas fornecidas no formato ISO ou string comparável)
        d_fab = (dto.data_fabricacao or "").strip()
        d_val = (dto.data_validade or "").strip()
        if d_fab and d_val:
            try:
                # Compara datas
                dt_fab = datetime.strptime(d_fab[:10], "%Y-%m-%d") if "-" in d_fab else datetime.strptime(d_fab[:10], "%d/%m/%Y")
                dt_val = datetime.strptime(d_val[:10], "%Y-%m-%d") if "-" in d_val else datetime.strptime(d_val[:10], "%d/%m/%Y")
                if dt_val < dt_fab:
                    return ResultadoLoteDTO(sucesso=False, mensagem="A Data de Validade não pode ser anterior à Data de Fabricação.")
            except Exception:
                pass

        dto_sanitizado = ProdutoLoteDTO(
            id_produto_lote=dto.id_produto_lote,
            prodcod=dto.prodcod,
            prodnome=dto.prodnome,
            numero_lote=num_lote,
            data_fabricacao=d_fab or None,
            data_validade=d_val or None,
            quantidade_inicial=qtd_ini,
            quantidade_atual=qtd_atu,
            data_entrada=dto.data_entrada,
            entcod_fornecedor=dto.entcod_fornecedor,
            nome_fornecedor=dto.nome_fornecedor,
            status=dto.status.strip().upper() or "A",
            observacao=(dto.observacao or "").strip(),
            data_cadastro=dto.data_cadastro,
            usucod=dto.usucod or "",
        )

        try:
            novo_id = self._repo.salvar_lote(dto_sanitizado)
            dto_sanitizado.id_produto_lote = novo_id
            return ResultadoLoteDTO(
                sucesso=True,
                mensagem=f"Lote '{num_lote}' salvo com sucesso! (ID: {novo_id})",
                codigo=novo_id,
                lote=dto_sanitizado,
            )
        except Exception as e:
            logger.error("Erro ao salvar lote: %s", e)
            return ResultadoLoteDTO(sucesso=False, mensagem=f"Erro ao salvar lote: {e}")

    def inativar_lote(self, id_produto_lote: int) -> ResultadoLoteDTO:
        """Inativa um lote no sistema."""
        try:
            self._repo.inativar_lote(id_produto_lote)
            return ResultadoLoteDTO(sucesso=True, mensagem="Lote inativado com sucesso.", codigo=id_produto_lote)
        except Exception as e:
            logger.error("Erro ao inativar lote: %s", e)
            return ResultadoLoteDTO(sucesso=False, mensagem=f"Erro ao inativar lote: {e}")

    def excluir_lote(self, id_produto_lote: int) -> ResultadoLoteDTO:
        """Exclui um lote do sistema."""
        try:
            self._repo.excluir_lote(id_produto_lote)
            return ResultadoLoteDTO(sucesso=True, mensagem="Lote excluído com sucesso.", codigo=id_produto_lote)
        except Exception as e:
            logger.error("Erro ao excluir lote: %s", e)
            return ResultadoLoteDTO(sucesso=False, mensagem=f"Erro ao excluir lote: {e}")
