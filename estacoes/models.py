"""
Modelos e Estruturas de Dados (DTOs) para Estações de Trabalho (TI e Ativo Fixo).
"""

from dataclasses import dataclass
from typing import Optional
from datetime import date, datetime


@dataclass
class EstacaoDTO:
    codigo_estacao: str
    descricao: str
    codigo_departamento: str = ""
    nome_departamento: str = ""
    data_cadastro: Optional[str] = None
    codigo_usuario: str = ""
    usuario_responsavel: str = ""
    tag_servico: str = ""
    geoentcod: str = ""
    nome_entidade: str = ""
    modelo_estacao: str = ""
    codigo_localizacao: str = ""
    nome_localizacao: str = ""
    endereco_ip: str = ""
    observacoes: str = ""


@dataclass
class HardwareDTO:
    codigo_hardware: str
    descricao: str
    valor: float = 0.0
    data_compra: Optional[str] = None
    data_ativacao: Optional[str] = None
    tempo_garantia: int = 365
    codigo_status: int = 1
    nome_status: str = ""
    codigo_estacao: str = ""
    codigo_classe: int = 0
    nome_classe: str = ""
    observacoes: str = ""
    nf: str = ""
    marca: str = ""
    endereco_ip: str = ""
    rack: str = ""
    patch_panel: str = ""


@dataclass
class SoftwareDTO:
    codigo_software: str
    descricao: str
    nf: str = ""
    valor: float = 0.0
    data_compra: Optional[str] = None
    data_vencimento: Optional[str] = None
    tipo_licenca: str = ""
    codigo_estacao: str = ""
    codigo_classe: int = 0
    observacoes: str = ""


@dataclass
class UsuarioEstacaoDTO:
    codigo_usuario: str
    nome_usuario: str
    codigo_estacao: str
    data_vinculo: Optional[str] = None
    responsavel: str = "Sim"


@dataclass
class EstacaoFiltro:
    campo_busca: str = "descricao"
    texto_busca: str = ""
    campo_ordem: str = "descricao"
    ordem_asc: bool = True
    departamento: str = ""
    limite: int = 100


@dataclass
class ResultadoOperacao:
    sucesso: bool
    mensagem: str
    codigo: Optional[str] = None
