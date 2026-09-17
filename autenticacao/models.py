"""
Modelos de Dados e DTOs para Autenticação, Logon e Sessão do Usuário.
GeoApolo V5
Clean Architecture: DTOs desacoplados para controle de acesso e sessão.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CredenciaisDTO:
    """Credenciais informadas na tela de logon."""
    login: str = ""
    senha: str = ""
    empcod: str = "01"


@dataclass
class UsuarioSessaoDTO:
    """Dados da sessão do usuário autenticado no sistema."""
    usucod: str = ""
    login: str = ""
    nome_usuario: str = ""
    empcod: str = "01"
    empnome: str = ""
    perfil_admin: bool = False
    token_sessao: str = ""

    @property
    def display(self) -> str:
        return f"{self.nome_usuario} ({self.login}) @ Empresa {self.empcod} - {self.empnome}"


@dataclass
class ResultadoAutenticacaoDTO:
    """Resultado padronizado da tentativa de autenticação."""
    sucesso: bool = True
    mensagem: str = ""
    sessao: Optional[UsuarioSessaoDTO] = None
    bloqueio_licenca: bool = False
