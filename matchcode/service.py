"""
Serviço de lógica de negócio e validações para Unificação de Cadastros (MatchCode).
GeoApolo V5
"""

from matchcode.models import (
    MatchCodeUsuarioDTO,
    MatchCodeEntidadeDTO,
    ResultadoMatchCodeDTO,
)
from matchcode.repository import MatchCodeRepository


class MatchCodeService:
    """Orquestra validações críticas de segurança antes da mesclagem de cadastros."""

    def __init__(self, repository: MatchCodeRepository):
        if not repository:
            raise ValueError("MatchCodeRepository é obrigatório.")
        self._repo = repository

    def obter_usuario(self, usucod: str):
        if not usucod or not usucod.strip():
            return None
        return self._repo.obter_usuario(usucod.strip().upper())

    def obter_entidade(self, entcod: str):
        if not entcod or not entcod.strip():
            return None
        return self._repo.obter_entidade(entcod.strip().upper())

    def unificar_usuarios(self, origem_usucod: str, destino_usucod: str) -> ResultadoMatchCodeDTO:
        """Valida e unifica dois usuários em um cadastro definitivo."""
        if not origem_usucod or not origem_usucod.strip():
            return ResultadoMatchCodeDTO(False, "Código do usuário de origem deve ser fornecido.")
        if not destino_usucod or not destino_usucod.strip():
            return ResultadoMatchCodeDTO(False, "Código do usuário de destino deve ser fornecido.")

        orig = origem_usucod.strip().upper()
        dest = destino_usucod.strip().upper()

        if orig == dest:
            return ResultadoMatchCodeDTO(False, "O usuário de origem e o usuário de destino não podem ser iguais.")

        user_orig = self._repo.obter_usuario(orig)
        if not user_orig:
            return ResultadoMatchCodeDTO(False, f"Usuário de origem '{orig}' não encontrado.")

        user_dest = self._repo.obter_usuario(dest)
        if not user_dest:
            return ResultadoMatchCodeDTO(False, f"Usuário de destino '{dest}' não encontrado.")

        return self._repo.executar_matchcode_usuario(orig, dest)

    def unificar_entidades(self, origem_entcod: str, destino_entcod: str) -> ResultadoMatchCodeDTO:
        """Valida e unifica duas entidades/pessoas em um cadastro definitivo."""
        if not origem_entcod or not origem_entcod.strip():
            return ResultadoMatchCodeDTO(False, "Código da entidade de origem deve ser fornecido.")
        if not destino_entcod or not destino_entcod.strip():
            return ResultadoMatchCodeDTO(False, "Código da entidade de destino deve ser fornecido.")

        orig = origem_entcod.strip().upper()
        dest = destino_entcod.strip().upper()

        if orig == dest:
            return ResultadoMatchCodeDTO(False, "A entidade de origem e de destino não podem ser iguais.")

        ent_orig = self._repo.obter_entidade(orig)
        if not ent_orig:
            return ResultadoMatchCodeDTO(False, f"Entidade de origem '{orig}' não encontrada.")

        ent_dest = self._repo.obter_entidade(dest)
        if not ent_dest:
            return ResultadoMatchCodeDTO(False, f"Entidade de destino '{dest}' não encontrada.")

        return self._repo.executar_matchcode_entidade(orig, dest)
