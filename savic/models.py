"""
Modelos e DTOs para o Módulo de Integração SAVIC x GeoAlvo/Apolo.
Define estruturas para resumo estatístico, filtros, grupos de oração e coordenadores.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List, Dict, Any


@dataclass
class SavicResumoStatusDTO:
    """Subtotais estatísticos de grupos de oração no SAVIC."""
    total_go: int = 0
    total_homologados: int = 0
    total_nao_homologados: int = 0
    total_em_andamento: int = 0


@dataclass
class SavicFiltroDTO:
    """Parâmetros de filtro para consulta e apuração no SAVIC."""
    data_inicial: Optional[date] = None
    data_final: Optional[date] = None
    apenas_vigentes_ou_indeterminados: bool = True


@dataclass
class SavicCoordenadorDTO:
    """Dados de coordenador vindos da base SAVIC."""
    cadastroid_coord: str = ""
    coordenador: str = ""
    genero_coord: str = "M"
    cpf_coordenador: str = ""
    rgcoord: str = ""
    rgcoordemissor: str = ""
    endereco_coordenador: str = ""
    numero_casa_coord: str = ""
    compl_coord: str = ""
    bairro_coord: str = ""
    cep_coord: str = ""
    cidade: str = ""
    estado: str = ""
    caixa_postal: str = ""
    telefone_coord: str = ""
    tel_com_coord: str = ""
    celular_coord1: str = ""
    celular_coord2: str = ""
    email: str = ""
    diocese_id: str = ""
    diocese_coordenador: str = ""
    mandato_indeterminado: str = "Não"
    dataini_coordenacao: Optional[date] = None
    datafim_coordenacao: Optional[date] = None
    user_atualizacao: str = ""
    ultima_alteracao_feita_por: str = ""


@dataclass
class SavicGrupoOracaoDTO:
    """Dados de grupo de oração vindos da base SAVIC (view_go_ativosv2)."""
    goid: str = ""
    grupo_de_oracao: str = ""
    cidade: str = ""
    estado: str = ""
    dias_semana: str = ""
    horario: str = ""
    situacao: str = ""
    caracteristica_grupo: str = ""
    local_reuniao: str = ""
    tipo_local_reuniao: str = ""
    datainclusao_go: Optional[date] = None
    dataatualizacao_go: Optional[date] = None
    coordenador: SavicCoordenadorDTO = field(default_factory=SavicCoordenadorDTO)


@dataclass
class ResultadoImportacaoSavicDTO:
    """Resultado detalhado da rotina de importação e sincronização."""
    sucesso: bool = False
    total_registros_apurados: int = 0
    total_coordenadores_inseridos: int = 0
    total_coordenadores_atualizados: int = 0
    total_grupos_inseridos: int = 0
    total_grupos_atualizados: int = 0
    total_entidades_go_inseridas: int = 0
    total_entidades_go_atualizadas: int = 0
    registros_inseridos_entidades: List[Dict[str, Any]] = field(default_factory=list)
    registros_apenas_grupos: List[Dict[str, Any]] = field(default_factory=list)
    caminho_arquivo_ocorrencias: str = ""
    erros: List[str] = field(default_factory=list)
    mensagem: str = ""

