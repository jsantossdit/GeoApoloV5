"""
Módulo de Gestão de Usuários, Grupos e Perfis de Acesso.
GeoApolo V5
"""

import sys
from pathlib import Path

# Garante que o diretório raiz esteja no sys.path
_raiz_projeto = str(Path(__file__).resolve().parent.parent)
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

try:
    from usuarios.models import (
        UsuarioDTO,
        DepartamentoDTO,
        SistemaDTO,
        GrupoUsuarioDTO,
        VinculoGrupoUsuarioDTO,
        ObjetoAcessoDTO,
        PerfilAcessoItemDTO,
        ResultadoOperacaoUsuario,
    )
    from usuarios.repository import UsuariosRepository
    from usuarios.service import UsuariosService
    from usuarios.view import UsuariosView
except (ImportError, ModuleNotFoundError):
    from .models import (
        UsuarioDTO,
        DepartamentoDTO,
        SistemaDTO,
        GrupoUsuarioDTO,
        VinculoGrupoUsuarioDTO,
        ObjetoAcessoDTO,
        PerfilAcessoItemDTO,
        ResultadoOperacaoUsuario,
    )
    from .repository import UsuariosRepository
    from .service import UsuariosService
    from .view import UsuariosView

__all__ = [
    "UsuarioDTO",
    "DepartamentoDTO",
    "SistemaDTO",
    "GrupoUsuarioDTO",
    "VinculoGrupoUsuarioDTO",
    "ObjetoAcessoDTO",
    "PerfilAcessoItemDTO",
    "ResultadoOperacaoUsuario",
    "UsuariosRepository",
    "UsuariosService",
    "UsuariosView",
]
