"""
Modelos de dados e DTOs para Unificação e Mesclagem de Cadastros (MatchCode).
GeoApolo V5
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MatchCodeUsuarioDTO:
    """Parâmetros para unificação de usuários duplicados."""
    origem_usucod: str
    destino_usucod: str
    origem_nome: str = ""
    destino_nome: str = ""


@dataclass
class MatchCodeEntidadeDTO:
    """Parâmetros para unificação de pessoas ou entidades duplicadas."""
    origem_entcod: str
    destino_entcod: str
    origem_nome: str = ""
    destino_nome: str = ""


@dataclass
class ResultadoMatchCodeDTO:
    """Resultado da rotina atômica de unificação e mesclagem."""
    sucesso: bool
    mensagem: str
    tabelas_afetadas: int = 0
    registros_migrados: int = 0
