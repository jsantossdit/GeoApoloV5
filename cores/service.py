"""
Camada de Serviços e Regras de Negócio para Cores de Produtos.
GeoApolo V5
Clean Architecture: Validações de unicidade e integridade cadastral.
"""

import logging
from typing import List, Optional
from .models import CorDTO, ResultadoCorDTO
from .repository import CoresRepository

logger = logging.getLogger(__name__)


class CoresService:
    """Regras de negócio e validações para cadastro de cores."""

    def __init__(self, repository: CoresRepository):
        self._repo = repository

    def listar_cores(self) -> List[CorDTO]:
        return self._repo.listar_cores()

    def obter_cor(self, codigo: int) -> Optional[CorDTO]:
        if codigo <= 0:
            return None
        return self._repo.obter_cor(codigo)

    def obter_proximo_codigo(self) -> int:
        return self._repo.obter_proximo_codigo()

    def salvar_cor(self, cor: CorDTO) -> ResultadoCorDTO:
        desc = str(cor.descricao_cor or "").strip()
        if not desc:
            return ResultadoCorDTO(sucesso=False, mensagem="Descrição da cor é obrigatória.")

        if cor.codigo_cor <= 0:
            cor.codigo_cor = self._repo.obter_proximo_codigo()

        cor.descricao_cor = desc

        if self._repo.existe_descricao(desc, cor.codigo_cor):
            return ResultadoCorDTO(
                sucesso=False,
                mensagem=f"A cor '{desc}' já está cadastrada no sistema.",
                codigo=cor.codigo_cor,
            )

        try:
            self._repo.salvar_cor(cor)
            return ResultadoCorDTO(
                sucesso=True,
                mensagem=f"Cor '{desc}' gravada com sucesso!",
                codigo=cor.codigo_cor,
            )
        except Exception as exc:
            logger.exception("Erro ao salvar cor: %s", exc)
            return ResultadoCorDTO(sucesso=False, mensagem=f"Erro ao salvar cor:\n{exc}")

    def excluir_cor(self, codigo: int) -> ResultadoCorDTO:
        if codigo <= 0:
            return ResultadoCorDTO(sucesso=False, mensagem="Código da cor inválido para exclusão.")

        try:
            self._repo.excluir_cor(codigo)
            return ResultadoCorDTO(
                sucesso=True,
                mensagem="Cor excluída com sucesso.",
                codigo=codigo,
            )
        except Exception as exc:
            logger.exception("Erro ao excluir cor: %s", exc)
            return ResultadoCorDTO(sucesso=False, mensagem=f"Erro ao excluir cor:\n{exc}")
