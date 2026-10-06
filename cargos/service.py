"""
Camada de Serviços e Regras de Negócio para o Cadastro de Cargos.
GeoApolo V5
Clean Architecture: Validações de campos, maiúsculas, integridade e regras de negócio.
"""

import logging
from typing import List, Optional

from .models import CargoDTO, ResultadoCargoDTO
from .repository import CargoRepository

logger = logging.getLogger(__name__)


class CargoService:
    """Serviço com regras de negócio para Cargos."""

    def __init__(self, repository: CargoRepository):
        self._repo = repository

    def listar_cargos(self, termo: str = "") -> List[CargoDTO]:
        """Lista cargos com base em termo de busca opcional."""
        return self._repo.listar_cargos(termo=termo)

    def obter_cargo(self, codigo: int) -> Optional[CargoDTO]:
        """Obtém cargo por código."""
        if not codigo or codigo <= 0:
            return None
        return self._repo.obter_cargo_por_codigo(codigo)

    def obter_proximo_codigo(self) -> int:
        """Obtém o próximo código numérico para novo cargo."""
        return self._repo.obter_proximo_codigo()

    def salvar_cargo(self, dto: CargoDTO) -> ResultadoCargoDTO:
        """Valida e salva o cargo (inclusão ou alteração)."""
        nome = str(dto.geocargonome or "").strip().upper()
        if not nome:
            return ResultadoCargoDTO(
                sucesso=False,
                mensagem="O Nome do Cargo é de preenchimento obrigatório.",
                codigo=dto.geocargocodestr,
            )

        if len(nome) > 80:
            return ResultadoCargoDTO(
                sucesso=False,
                mensagem="O Nome do Cargo não pode ter mais de 80 caracteres.",
                codigo=dto.geocargocodestr,
            )

        faixa = str(dto.geofaixasalarial or "").strip().upper()
        if len(faixa) > 14:
            return ResultadoCargoDTO(
                sucesso=False,
                mensagem="A Faixa Salarial não pode ter mais de 14 caracteres.",
                codigo=dto.geocargocodestr,
            )

        dto_sanitizado = CargoDTO(
            geocargocodestr=int(dto.geocargocodestr or 0),
            geocargonome=nome,
            geofaixasalarial=faixa,
        )

        sucesso, msg, cod = self._repo.salvar_cargo(dto_sanitizado)
        dto_sanitizado.geocargocodestr = cod
        return ResultadoCargoDTO(
            sucesso=sucesso,
            mensagem=msg,
            codigo=cod,
            cargo=dto_sanitizado if sucesso else None,
        )

    def excluir_cargo(self, codigo: int) -> ResultadoCargoDTO:
        """Valida e remove o cargo do sistema."""
        if not codigo or codigo <= 0:
            return ResultadoCargoDTO(sucesso=False, mensagem="Código de cargo inválido para exclusão.")

        sucesso, msg = self._repo.excluir_cargo(codigo)
        return ResultadoCargoDTO(sucesso=sucesso, mensagem=msg, codigo=codigo)
