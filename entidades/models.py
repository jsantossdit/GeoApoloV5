"""
Modelos de dados e Schemas para o módulo de Entidades do GeoAlvo.
Correspondente a unt_entidades_types.pas.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any


class DecisaoLinha(Enum):
    NENHUMA = "Nenhuma"
    MANTER_SVE = "ManterSVE"
    MANTER_ALVO = "ManterAlvo"


@dataclass
class EntidadeFiltro:
    base_dados: str = "GeoApolo"          # 'GeoApolo' ou 'Alvo'
    tipo_pesquisa: str = "Consulta"       # 'Consulta' ou 'Especifica'
    filtro_especial: str = ""             # 'JAEXPORTADA' ou ''
    campo_busca: str = "entnome"
    texto_busca: str = ""
    campo_ordenacao: str = "entnome"
    ordem_asc: bool = True
    limite: int = 50
    offset: int = 0


@dataclass
class ItemComparacao:
    indice_mapa: int
    rotulo: str
    campo_sve: str
    campo_alvo: str
    valor_sve: str
    valor_alvo: str
    decisao: DecisaoLinha = DecisaoLinha.NENHUMA

    @property
    def eh_diferente(self) -> bool:
        return (self.valor_sve or "").strip().lower() != (self.valor_alvo or "").strip().lower()


@dataclass
class ResultadoOperacao:
    sucesso: bool
    mensagem: str
    codigo: Optional[str] = None
    dados: Optional[Dict[str, Any]] = None


@dataclass
class CredencialAlvo:
    usuario_alvo: str = ""
    senha_alvo_cripto: str = ""
    token_alvo: str = ""


@dataclass
class EntidadeEdicao:
    codigo: str = ""
    codigo_alternativo: str = ""
    tipo_tratamento: str = ""
    nome: str = ""
    nome_fantasia: str = ""
    cpf_cnpj: str = ""
    rg_ie: str = ""
    cep: str = ""
    logradouro: str = ""
    endereco: str = ""
    numero: str = ""
    complemento: str = ""
    bairro: str = ""
    codigo_cidade: str = ""
    nome_cidade: str = ""
    uf: str = ""
    genero: str = ""
    estado_civil: str = ""
    data_nascimento: str = ""
    data_cadastro: str = ""
    nome_pai: str = ""
    nome_mae: str = ""
    possui_filhos: bool = False
    numero_filhos: int = 0
    valor_contribuicao: float = 25.0
    diocese_id: str = ""
    nome_diocese: str = ""
    observacoes: str = ""
    atualizou_apolo: str = "N"
    modo_integracao: str = ""
    telefones: List[Dict[str, Any]] = field(default_factory=list)
    emails: List[Dict[str, Any]] = field(default_factory=list)
    categorias: List[str] = field(default_factory=list)
