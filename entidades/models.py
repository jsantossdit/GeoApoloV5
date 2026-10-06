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
    categoria_busca: str = ""             # Código ou descrição da categoria para filtro
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
        v_sve = (self.valor_sve or "").strip().lower()
        v_alvo = (self.valor_alvo or "").strip().lower()
        if self.rotulo == "Gênero":
            m_sve = "m" if v_sve in ("m", "masculino") else ("f" if v_sve in ("f", "feminino") else v_sve)
            m_alvo = "m" if v_alvo in ("m", "masculino") else ("f" if v_alvo in ("f", "feminino") else v_alvo)
            return m_sve != m_alvo
        if self.rotulo == "CPF / CNPJ":
            import re
            d_sve = re.sub(r"\D", "", v_sve)
            d_alvo = re.sub(r"\D", "", v_alvo)
            if d_sve or d_alvo:
                return d_sve != d_alvo
        if self.rotulo in ("Código Alvo (entcod)", "Código Alvo"):
            v1 = v_sve.lstrip("0")
            v2 = v_alvo.lstrip("0")
            return v1 != v2
        return v_sve != v_alvo


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
