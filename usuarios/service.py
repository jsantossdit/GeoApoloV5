"""
Serviço de regras de negócio para Gestão de Usuários, Grupos e Perfis de Acesso.
GeoApolo V5
"""

import sys
from pathlib import Path

# Garante que o diretório raiz esteja no sys.path
_raiz_projeto = str(Path(__file__).resolve().parent.parent)
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

from typing import List, Optional
try:
    from usuarios.models import (
        UsuarioDTO,
        DepartamentoDTO,
        SistemaDTO,
        GrupoUsuarioDTO,
        VinculoGrupoUsuarioDTO,
        PerfilAcessoItemDTO,
        ResultadoOperacaoUsuario,
    )
    from usuarios.repository import UsuariosRepository
except (ImportError, ModuleNotFoundError):
    from models import (
        UsuarioDTO,
        DepartamentoDTO,
        SistemaDTO,
        GrupoUsuarioDTO,
        VinculoGrupoUsuarioDTO,
        PerfilAcessoItemDTO,
        ResultadoOperacaoUsuario,
    )
    from repository import UsuariosRepository


class UsuariosService:
    """Regras de negócio e orquestração para Usuários e Perfis de Acesso."""

    def __init__(self, repository: UsuariosRepository):
        if not repository:
            raise ValueError("UsuariosRepository é obrigatório.")
        self._repo = repository

    def listar_usuarios(self, filtro_nome: str = "", apenas_ativos: bool = True) -> List[UsuarioDTO]:
        return self._repo.listar_usuarios(filtro_nome, apenas_ativos)

    def obter_usuario(self, usucod: str) -> Optional[UsuarioDTO]:
        if not usucod or not usucod.strip():
            raise ValueError("Identificador (usucod) do usuário deve ser informado.")
        return self._repo.obter_usuario_por_usucod(usucod.strip())

    def salvar_usuario(self, u: UsuarioDTO) -> ResultadoOperacaoUsuario:
        """Valida regras de negócio e persiste o usuário."""
        if not u.usucod or not u.usucod.strip():
            return ResultadoOperacaoUsuario(False, "O identificador (usucod) do usuário é obrigatório.")

        if not u.login or not u.login.strip():
            return ResultadoOperacaoUsuario(False, "O login de acesso é obrigatório.")

        if not u.nome_completo or not u.nome_completo.strip():
            return ResultadoOperacaoUsuario(False, "O nome completo do usuário é obrigatório.")

        # Sanitização
        u.usucod = u.usucod.strip().upper()
        u.login = u.login.strip().lower()
        u.nome_completo = u.nome_completo.strip()
        u.email = u.email.strip().lower() if u.email else ""
        u.flagativo = u.flagativo.strip().upper() if u.flagativo else "A"

        # Verifica unicidade de login
        existente = self._repo.obter_usuario_por_login(u.login)
        if existente and existente.usucod.strip().upper() != u.usucod:
            return ResultadoOperacaoUsuario(
                False,
                f"O login '{u.login}' já está em uso por outro colaborador ({existente.nome_completo})."
            )

        try:
            self._repo.salvar_usuario(u)
            return ResultadoOperacaoUsuario(
                True,
                "Usuário gravado com sucesso.",
                id_gerado=u.usucod
            )
        except Exception as e:
            return ResultadoOperacaoUsuario(False, f"Erro ao salvar usuário: {str(e)}")

    def excluir_usuario(self, usucod: str) -> ResultadoOperacaoUsuario:
        """Remove o usuário e limpa seus relacionamentos."""
        if not usucod or not usucod.strip():
            return ResultadoOperacaoUsuario(False, "Código do usuário deve ser informado.")

        usucod_limpo = usucod.strip().upper()
        usuario = self._repo.obter_usuario_por_usucod(usucod_limpo)
        if not usuario:
            return ResultadoOperacaoUsuario(False, "Usuário não localizado para exclusão.")

        try:
            self._repo.excluir_usuario(usucod_limpo)
            return ResultadoOperacaoUsuario(
                True,
                f"Usuário '{usuario.nome_completo}' ({usucod_limpo}) excluído com sucesso.",
                id_gerado=usucod_limpo
            )
        except Exception as e:
            return ResultadoOperacaoUsuario(False, f"Erro ao excluir usuário: {str(e)}")

    def listar_departamentos(self, empcod: str = "") -> List[DepartamentoDTO]:
        return self._repo.listar_departamentos(empcod)

    def listar_sistemas(self) -> List[SistemaDTO]:
        return self._repo.listar_sistemas()

    def listar_sistemas_usuario(self, usucod: str) -> List[SistemaDTO]:
        if not usucod or not usucod.strip():
            return []
        return self._repo.listar_sistemas_usuario(usucod.strip())

    def vincular_sistema(self, usucod: str, codigo_sistema: str) -> ResultadoOperacaoUsuario:
        if not usucod or not codigo_sistema:
            return ResultadoOperacaoUsuario(False, "Usuário e Sistema são obrigatórios.")
        try:
            self._repo.vincular_sistema_usuario(usucod.strip(), codigo_sistema.strip())
            return ResultadoOperacaoUsuario(True, "Sistema vinculado com sucesso.")
        except Exception as e:
            return ResultadoOperacaoUsuario(False, f"Erro ao vincular sistema: {str(e)}")

    def desvincular_sistema(self, usucod: str, codigo_sistema: str) -> ResultadoOperacaoUsuario:
        if not usucod or not codigo_sistema:
            return ResultadoOperacaoUsuario(False, "Identificadores inválidos.")
        try:
            self._repo.desvincular_sistema_usuario(usucod.strip(), codigo_sistema.strip())
            return ResultadoOperacaoUsuario(True, "Vínculo com sistema removido com sucesso.")
        except Exception as e:
            return ResultadoOperacaoUsuario(False, f"Erro ao desvincular sistema: {str(e)}")

    def listar_grupos(self) -> List[GrupoUsuarioDTO]:
        return self._repo.listar_grupos()

    def obter_grupo(self, codigo_grupo: str) -> Optional[GrupoUsuarioDTO]:
        if not codigo_grupo or not codigo_grupo.strip():
            return None
        return self._repo.obter_grupo(codigo_grupo.strip().upper())

    def salvar_grupo(self, codigo_grupo: str, descricao: str) -> ResultadoOperacaoUsuario:
        if not codigo_grupo or not codigo_grupo.strip():
            return ResultadoOperacaoUsuario(False, "O código do grupo é obrigatório.")
        if not descricao or not descricao.strip():
            return ResultadoOperacaoUsuario(False, "A descrição do grupo não pode ser vazia.")

        try:
            self._repo.salvar_grupo(codigo_grupo.strip().upper(), descricao.strip())
            return ResultadoOperacaoUsuario(True, "Grupo salvo com sucesso.", id_gerado=codigo_grupo.strip().upper())
        except Exception as e:
            return ResultadoOperacaoUsuario(False, f"Erro ao salvar grupo: {str(e)}")

    def excluir_grupo(self, codigo_grupo: str) -> ResultadoOperacaoUsuario:
        if not codigo_grupo or not codigo_grupo.strip():
            return ResultadoOperacaoUsuario(False, "Código do grupo deve ser fornecido.")

        try:
            self._repo.excluir_grupo(codigo_grupo.strip().upper())
            return ResultadoOperacaoUsuario(True, "Grupo excluído com sucesso.")
        except Exception as e:
            return ResultadoOperacaoUsuario(False, f"Erro ao excluir grupo: {str(e)}")

    def listar_usuarios_grupo(self, codigo_grupo: str) -> List[VinculoGrupoUsuarioDTO]:
        if not codigo_grupo or not codigo_grupo.strip():
            return []
        return self._repo.listar_usuarios_grupo(codigo_grupo.strip().upper())

    def vincular_usuario_grupo(self, codigo_grupo: str, usucod: str) -> ResultadoOperacaoUsuario:
        if not codigo_grupo or not usucod:
            return ResultadoOperacaoUsuario(False, "Grupo e usuário são obrigatórios.")
        try:
            self._repo.vincular_usuario_grupo(codigo_grupo.strip().upper(), usucod.strip().upper())
            return ResultadoOperacaoUsuario(True, "Usuário vinculado ao grupo com sucesso.")
        except Exception as e:
            return ResultadoOperacaoUsuario(False, f"Erro ao vincular usuário: {str(e)}")

    def desvincular_usuario_grupo(self, codigo_grupo: str, usucod: str) -> ResultadoOperacaoUsuario:
        if not codigo_grupo or not usucod:
            return ResultadoOperacaoUsuario(False, "Identificadores inválidos.")
        try:
            self._repo.desvincular_usuario_grupo(codigo_grupo.strip().upper(), usucod.strip().upper())
            return ResultadoOperacaoUsuario(True, "Usuário removido do grupo.")
        except Exception as e:
            return ResultadoOperacaoUsuario(False, f"Erro ao desvincular usuário: {str(e)}")

    def listar_objetos_perfil(self, codigo_grupo: str, categoria: str = "") -> List[PerfilAcessoItemDTO]:
        if not codigo_grupo or not codigo_grupo.strip():
            return []
        return self._repo.listar_objetos_perfil(codigo_grupo.strip().upper(), categoria)

    def listar_categorias_objetos(self) -> List[str]:
        return self._repo.listar_categorias_objetos()

    def atualizar_acesso(self, codigo_grupo: str, codigo_objeto: str, liberado: bool) -> ResultadoOperacaoUsuario:
        if not codigo_grupo or not codigo_objeto:
            return ResultadoOperacaoUsuario(False, "Grupo e objeto são obrigatórios.")

        status = "A" if liberado else "N"
        try:
            self._repo.atualizar_status_acesso(codigo_grupo.strip().upper(), codigo_objeto.strip(), status)
            msg = "Permissão concedida (Liberado)." if liberado else "Permissão revogada (Bloqueado)."
            return ResultadoOperacaoUsuario(True, msg)
        except Exception as e:
            return ResultadoOperacaoUsuario(False, f"Erro ao atualizar permissão: {str(e)}")
