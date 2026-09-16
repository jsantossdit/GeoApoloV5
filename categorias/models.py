"""
Modelos e DTOs para Relacionamento de Categorias, Usuários e Entidades.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CategoriaResumoDTO:
    codigo_categoria: str
    descricao: str
    total_entidades: int = 0
    vinculada: bool = False


@dataclass
class UsuarioItemDTO:
    codigo: str
    nome: str


@dataclass
class GrupoItemDTO:
    codigo: str
    descricao: str


@dataclass
class ResultadoOperacao:
    sucesso: bool
    mensagem: str
    codigo: Optional[str] = None
