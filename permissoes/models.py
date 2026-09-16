"""
Modelos e DTOs para Clonagem e Gestão de Permissões de Usuários.
GeoApolo V5
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class OpcoesClonagemDTO:
    """Opções modulares para controle refinado da clonagem de permissões."""
    direitos_sistema: bool = True
    relatorios: bool = True
    contas_financeiras: bool = True
    formularios: bool = True
    categorias_entidades: bool = True
    tipo_pagar_receber: bool = True
    grupos_usuario: bool = True
    favoritos: bool = True
    tour_usuario: bool = True
    empresas_filiais: bool = True


@dataclass
class UsuarioResumoDTO:
    """Dados resumidos de usuário para seleção de perfil."""
    codigo: str
    nome: str


@dataclass
class RelatorioClonagemDTO:
    """Contagem detalhada de permissões clonadas por módulo."""
    total_direitos_sistema: int = 0
    total_relatorios: int = 0
    total_contas_financeiras: int = 0
    total_formularios: int = 0
    total_categorias_entidades: int = 0
    total_tipo_pagar_receber: int = 0
    total_grupos_usuario: int = 0
    total_favoritos: int = 0
    total_tour_usuario: int = 0
    total_empresas_filiais: int = 0
    total_geral: int = 0


@dataclass
class ResultadoClonagemDTO:
    """Resultado padronizado da operação de clonagem de acessos."""
    sucesso: bool
    mensagem: str
    total_itens: int = 0
    relatorio: Optional[RelatorioClonagemDTO] = None


@dataclass
class ContaFinanceiraDTO:
    """Dados de uma conta financeira para relacionamento com usuários."""
    codigo: str
    nome: str
    conta_corrente: str = ""

    @property
    def texto_formatado(self) -> str:
        return f"{self.codigo.strip()} -> {self.nome.strip()}"


@dataclass
class ResultadoContasFinDTO:
    """Resultado da sincronização de contas financeiras de um usuário."""
    sucesso: bool
    mensagem: str
    total_afetado: int = 0


@dataclass
class UsuarioDesligamentoDTO:
    """Dados cadastrais de usuário para rotina de desligamento."""
    codigo: str
    nome: str
    departamento: str = ""
    status: str = "Ativo"


@dataclass
class ResultadoDesligamentoDTO:
    """Resultado com contadores de remoção de privilégios no desligamento."""
    sucesso: bool
    mensagem: str
    vinculos_entidades: int = 0
    vinculos_categorias: int = 0
    permissoes_relatorios: int = 0
    permissoes_contas_fin: int = 0

