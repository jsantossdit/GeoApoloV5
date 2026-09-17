"""
Regras de Negócio e Serviços para Departamentos e Seções.
GeoApolo V5
Clean Architecture: Validações de integridade, auto-numeração e regras de negócio.
"""

import logging
from typing import List, Optional

from .models import DepartamentoDTO, ResultadoDepartamentoDTO
from .repository import DepartamentosRepository

logger = logging.getLogger(__name__)


class DepartamentosService:
    """Regras de negócio para cadastro de departamentos, seções e vínculo com centros de custos."""

    def __init__(self, repository: DepartamentosRepository):
        self._repo = repository

    def listar_departamentos(self, empcod: str = "", filtro: str = "") -> List[DepartamentoDTO]:
        return self._repo.listar_departamentos(empcod, filtro)

    def obter_departamento(self, codigo: int) -> Optional[DepartamentoDTO]:
        if codigo <= 0:
            return None
        return self._repo.obter_departamento(codigo)

    def obter_proximo_codigo(self) -> int:
        return self._repo.obter_proximo_codigo()

    def salvar_departamento(self, dto: DepartamentoDTO) -> ResultadoDepartamentoDTO:
        nome_limpo = dto.nome_departamento.strip()
        if not nome_limpo:
            return ResultadoDepartamentoDTO(sucesso=False, mensagem="Nome do departamento é obrigatório.")

        emp_limpa = dto.empcod.strip()
        if not emp_limpa:
            return ResultadoDepartamentoDTO(sucesso=False, mensagem="Empresa associada ao departamento é obrigatória.")

        if dto.codigo_departamento <= 0:
            dto.codigo_departamento = self._repo.obter_proximo_codigo()

        dto.nome_departamento = nome_limpo
        dto.empcod = emp_limpa
        dto.flagativo = "A" if dto.is_ativo else "I"

        try:
            self._repo.salvar_departamento(dto)
            return ResultadoDepartamentoDTO(
                sucesso=True,
                mensagem=f"Departamento '{nome_limpo}' gravado com sucesso!",
                codigo=dto.codigo_departamento,
            )
        except Exception as exc:
            logger.exception("Erro ao salvar departamento: %s", exc)
            return ResultadoDepartamentoDTO(sucesso=False, mensagem=f"Erro ao salvar departamento:\n{exc}")

    def excluir_departamento(self, codigo: int) -> ResultadoDepartamentoDTO:
        if codigo <= 0:
            return ResultadoDepartamentoDTO(sucesso=False, mensagem="Código do departamento inválido para exclusão.")

        try:
            self._repo.excluir_departamento(codigo)
            return ResultadoDepartamentoDTO(
                sucesso=True,
                mensagem="Departamento excluído com sucesso.",
                codigo=codigo,
            )
        except Exception as exc:
            logger.exception("Erro ao excluir departamento: %s", exc)
            return ResultadoDepartamentoDTO(sucesso=False, mensagem=f"Erro ao excluir departamento:\n{exc}")
