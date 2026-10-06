"""
Camada de Serviços e Regras de Negócio para Marcas de Produtos.
GeoApolo V5
Clean Architecture: Validações de unicidade e integridade cadastral.
"""

import logging
from typing import List, Optional, Tuple
from .models import MarcaDTO, ResultadoMarcaDTO
from .repository import MarcasRepository

logger = logging.getLogger(__name__)


class MarcasService:
    """Regras de negócio e validações para cadastro de marcas."""

    def __init__(self, repository: MarcasRepository):
        self._repo = repository

    def listar_marcas(self) -> List[MarcaDTO]:
        return self._repo.listar_marcas()

    def obter_marca(self, codigo: int) -> Optional[MarcaDTO]:
        if codigo <= 0:
            return None
        return self._repo.obter_marca(codigo)

    def obter_proximo_codigo(self) -> int:
        return self._repo.obter_proximo_codigo()

    def obter_ou_criar_marca(self, descricao: str) -> Tuple[int, str, bool]:
        """
        Localiza marca pela descrição (case-insensitive e sem espaços extras).
        Se já existir, retorna (codigo, descricao_armazenada, False).
        Se não existir, gera o próximo código sequencial, insere no banco e retorna (novo_codigo, descricao_limpa, True).
        """
        desc = str(descricao or "").strip().upper()
        if not desc:
            raise ValueError("Descrição da marca não pode ser vazia.")

        existente = self._repo.obter_por_descricao(desc)
        if existente:
            return existente.codigo_marca, existente.descricao_marca, False

        novo_codigo = self._repo.obter_proximo_codigo()
        dto = MarcaDTO(codigo_marca=novo_codigo, descricao_marca=desc)
        self._repo.salvar_marca(dto)
        return novo_codigo, desc, True

    def salvar_marca(self, marca: MarcaDTO) -> ResultadoMarcaDTO:
        desc = str(marca.descricao_marca or "").strip().upper()
        if not desc:
            return ResultadoMarcaDTO(sucesso=False, mensagem="Descrição da marca é obrigatória.")

        if marca.codigo_marca <= 0:
            marca.codigo_marca = self._repo.obter_proximo_codigo()

        marca.descricao_marca = desc

        if self._repo.existe_descricao(desc, marca.codigo_marca):
            return ResultadoMarcaDTO(
                sucesso=False,
                mensagem=f"A marca '{desc}' já está cadastrada no sistema.",
                codigo=marca.codigo_marca,
            )

        try:
            self._repo.salvar_marca(marca)
            return ResultadoMarcaDTO(
                sucesso=True,
                mensagem=f"Marca '{desc}' gravada com sucesso!",
                codigo=marca.codigo_marca,
            )
        except Exception as exc:
            logger.exception("Erro ao salvar marca: %s", exc)
            return ResultadoMarcaDTO(sucesso=False, mensagem=f"Erro ao salvar marca:\n{exc}")

    def excluir_marca(self, codigo: int) -> ResultadoMarcaDTO:
        if codigo <= 0:
            return ResultadoMarcaDTO(sucesso=False, mensagem="Código da marca inválido para exclusão.")

        try:
            self._repo.excluir_marca(codigo)
            return ResultadoMarcaDTO(
                sucesso=True,
                mensagem="Marca excluída com sucesso.",
                codigo=codigo,
            )
        except Exception as exc:
            logger.exception("Erro ao excluir marca: %s", exc)
            return ResultadoMarcaDTO(sucesso=False, mensagem=f"Erro ao excluir marca:\n{exc}")
