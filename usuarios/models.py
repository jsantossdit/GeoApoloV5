"""
Modelos de dados e DTOs para Gestão de Usuários, Grupos e Perfis de Acesso.
GeoApolo V5
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class UsuarioDTO:
    """Dados de usuário do sistema GeoApolo."""
    usucod: str
    nome_completo: str
    login: str
    codigo_usuario: str = ""
    flagativo: str = "A"  # 'A' (Ativo), 'I' (Inativo)
    email: str = ""
    data_nascimento: Optional[str] = None
    codigo_departamento: str = ""
    nome_departamento: str = ""
    usucod_apolo: str = ""
    senha_alvo: str = ""
    senha: str = ""

    @property
    def ativo(self) -> bool:
        return self.flagativo in ("A", "S")

    @property
    def status_display(self) -> str:
        return "Ativo" if self.ativo else "Inativo"


@dataclass
class DepartamentoDTO:
    """Departamento ou setor corporativo."""
    codigo_departamento: str
    nome_departamento: str
    empcod: str = ""
    empnome: str = ""
    flagativo: str = "S"


@dataclass
class SistemaDTO:
    """Sistema ou módulo do ecossistema corporativo."""
    codigo_sistema: str
    descricao: str
    sigla: str = ""


@dataclass
class GrupoUsuarioDTO:
    """Grupo de usuários para atribuição de papéis e permissões."""
    codigo_grupo: str
    descricao: str
    total_usuarios: int = 0


@dataclass
class VinculoGrupoUsuarioDTO:
    """Associação entre um usuário e um grupo de acesso."""
    codigo_grupo: str
    nome_grupo: str
    usucod: str
    login: str
    nome_completo: str


@dataclass
class ObjetoAcessoDTO:
    """Objeto, tela ou ação com controle de segurança."""
    codigo_objeto: str
    nome_objeto: str
    nome_amigavel: str
    categoria: str = "Geral"


@dataclass
class PerfilAcessoItemDTO:
    """Status de permissão de um objeto para um grupo específico."""
    codigo_objeto: str
    nome_objeto: str
    nome_amigavel: str
    categoria: str = "Geral"
    codigo_grupo: str = ""
    statusacesso: str = "N"  # 'A' = Autorizado, 'N' = Negado

    @property
    def liberado(self) -> bool:
        return self.statusacesso.upper() == "A"

    @property
    def status_display(self) -> str:
        return "Liberado" if self.liberado else "Bloqueado"


@dataclass
class ResultadoOperacaoUsuario:
    """Resultado padronizado para operações de usuário, grupo e perfil."""
    sucesso: bool
    mensagem: str
    id_gerado: str = ""
