"""
Modelos e DTOs para Gestão de Localidades, Cidades e Distritos.
GeoApolo V5
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CidadeDistritoDTO:
    """Representa um registro da tabela cidade/distrito do Apolo."""
    cid_cod: str
    nome: str
    uf: str
    ibge: str = ""
    eh_distrito: bool = False
    total_entidades: int = 0


@dataclass
class EntidadeLocalidadeDTO:
    """Entidade vinculada a uma cidade ou distrito para saneamento cadastral."""
    ent_cod: str
    nome: str
    documento: str
    cep: str
    endereco: str
    bairro: str


@dataclass
class ResultadoCorrecaoLocalidadeDTO:
    """Resultado da transferência de vínculos de distrito para a cidade mãe."""
    sucesso: bool
    mensagem: str
    entidades_migradas: int = 0
