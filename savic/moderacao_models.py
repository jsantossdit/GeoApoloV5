"""
Modelos de Dados (DTOs) para o Módulo de Moderação de Grupos de Oração SAVIC x Apolo.
Estruturas para filtros, dados de coordenadores, grupos de oração, ficha financeira e comparação Apolo.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any


@dataclass
class EstadoDTO:
    """Dados de Estado (UF) para preenchimento de combobox."""
    id: int = 0
    sigla: str = ""
    nome: str = ""


@dataclass
class DioceseDTO:
    """Dados de Diocese vinculada ao Estado."""
    id: int = 0
    estado_id: int = 0
    nome: str = ""
    ativo: int = 1


@dataclass
class CidadeDioceseDTO:
    """Dados de Cidade vinculada à Diocese."""
    id: int = 0
    estado_id: int = 0
    descricao: str = ""
    ibge: Optional[int] = None
    diocese_id: int = 0


@dataclass
class FiltroModeracaoDTO:
    """Filtros para busca de coordenadores e grupos de oração."""
    uf: str = ""
    diocese_nome: str = ""
    cidade_nome: str = ""
    situacao_grupo: str = "HOMOLOGADO"  # HOMOLOGADO, EM ANDAMENTO, NÃO HOMOLOGADO, TODOS
    categoria_apolo: str = "02.001"


@dataclass
class CoordenadorModeracaoDTO:
    """Dados cadastrais do coordenador exibidos na grid principal de moderação."""
    id_savic: str = ""
    codigo_apolo: str = ""
    coordenador: str = ""
    genero: str = ""
    cpf: str = ""
    rg: str = ""
    orgao_emissor: str = ""
    mandato_indeterminado: str = "Não"
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    telefone_fixo: str = ""
    telefone_comercial: str = ""
    celular: str = ""
    celular2: str = ""
    email: str = ""
    endereco: str = ""
    numero: str = ""
    complemento: str = ""
    bairro: str = ""
    cep: str = ""
    cidade: str = ""
    uf: str = ""
    diocese_id: str = ""
    diocese_nome: str = ""
    flagexportado: str = "Não"


@dataclass
class GrupoOracaoModeracaoDTO:
    """Dados do grupo de oração vinculado ao coordenador na moderação."""
    gocodigo: str = ""
    codigo_apolo: str = ""
    nome_grupo: str = ""
    local_reuniao: str = ""
    tipo_local: str = ""
    endereco: str = ""
    numero: str = ""
    complemento: str = ""
    bairro: str = ""
    cep: str = ""
    geocidcod: str = ""
    cidade: str = ""
    uf: str = ""
    dias_reuniao: str = ""
    horario: str = ""
    situacao_grupo: str = ""
    caracteristica_grupo: str = ""
    data_inclusao_savic: Optional[datetime] = None
    ultima_atualizacao: Optional[datetime] = None
    flagexportado: str = "Não"
    cadastroid_coordenador: str = ""


@dataclass
class ResultadoExportacaoEntidadeDTO:
    """Relatório do processamento de exportação para a tabela de Entidades."""
    sucesso: bool = False
    total_coordenadores_processados: int = 0
    total_coordenadores_inseridos: int = 0
    total_coordenadores_atualizados: int = 0
    total_grupos_processados: int = 0
    total_grupos_inseridos: int = 0
    total_grupos_atualizados: int = 0
    total_categorias_vinculadas: int = 0
    erros: List[str] = field(default_factory=list)
    mensagem: str = ""


@dataclass
class FichaFinanceiraDTO:
    """Resumo de arrecadação/doações financeiras da entidade (F5)."""
    empresa: str = ""
    tipo_cobranca_cod: str = ""
    tipo_cobranca_nome: str = ""
    primeiro_registro: Optional[datetime] = None
    ultimo_registro: Optional[datetime] = None
    vr_total_doado: Decimal = Decimal("0.00")


@dataclass
class EntidadeApoloComparativoDTO:
    """Dados cadastrais de entidade no Apolo na mesma cidade (F6)."""
    entcod: str = ""
    tipotratcod: str = ""
    entnome: str = ""
    entlograd: str = ""
    entender: str = ""
    entenderno: str = ""
    entendercomp: str = ""
    entbair: str = ""
    entcep: str = ""
    cidade: str = ""
    uf: str = ""
    cidcod: str = ""
