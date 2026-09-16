"""
Modelos e DTOs para Gestão de Ativo Imobilizado e Depreciação Contábil.
GeoApolo V5
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CalculoDepreciacaoDTO:
    """Resultado do cálculo de depreciação contábil pelo método de linha reta."""
    data_aquisicao: Optional[str] = None
    valor_compra: float = 0.0
    taxa_depreciacao_anual: float = 0.0
    anos_em_uso: float = 0.0
    depreciacao_anual: float = 0.0
    depreciacao_acumulada: float = 0.0
    valor_atual: float = 0.0
    valido: bool = False
    mensagem: str = ""


@dataclass
class AtivoImobilizadoDTO:
    """Dados cadastrais e patrimoniais de um bem de ativo imobilizado."""
    numero_do_bem: str
    descricao_do_bem: str
    empcod: str = "001"
    empnome: str = ""
    geocctrlcodestr: str = ""
    geocctrlnome: str = ""
    codigo_barrasativo: str = ""
    numero_de_serie: str = ""
    codigo_categoria_bem: str = ""
    categoria_bem: str = ""
    codigo_classificacaoativoimobilizado: str = ""
    classificacao: str = ""
    codigo_localizacao: str = ""
    localizacao: str = ""
    codigo_func_responsavel: str = ""
    nome_func_responsavel: str = ""
    codigo_da_marca: str = ""
    marca: str = ""
    codigo_status_bem: str = ""
    descricao_status_bem: str = ""
    data_aquisicao: Optional[str] = None
    valor_compra: float = 0.0
    taxa_depreciacao_anual: float = 0.0
    data_ultima_revisao: Optional[str] = None
    caminho_foto: str = ""
    observacoes: str = ""
    depreciacao: Optional[CalculoDepreciacaoDTO] = None


@dataclass
class LookupItemDTO:
    """Item genérico para combos e seletores de apoio."""
    codigo: str
    descricao: str
    extra: str = ""


@dataclass
class ResultadoOperacaoAtivo:
    """Resultado padronizado de operações no módulo de ativo imobilizado."""
    sucesso: bool
    mensagem: str
    codigo: Optional[str] = None
