"""
Modelos de Dados e DTOs para CRM & Campanhas.
GeoApolo V5
Clean Architecture: DTOs imutáveis/dataclass para Ocorrências, Campanhas e Tratamentos.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TipoCampanhaDTO:
    """Tipo de Campanha de CRM (USER_geoapolo_tipocampanha)."""
    codigo_tipocampanha: str
    descricaotipocamp: str
    ativo: str = "S"
    geracampanha: str = "S"

    @property
    def is_ativo(self) -> bool:
        return (self.ativo or "").strip().upper() == "S"

    @property
    def is_gera_campanha(self) -> bool:
        return (self.geracampanha or "").strip().upper() == "S"

    @property
    def display(self) -> str:
        return f"{self.codigo_tipocampanha} - {self.descricaotipocamp}"


@dataclass
class TipoTratamentoDTO:
    """Tipo de Tratamento de Atendimento (USER_geoapolo_tipotratamento)."""
    tipotratcod: str
    abreviatura: str
    descricao_tratamento: str

    @property
    def display(self) -> str:
        return f"{self.abreviatura} - {self.descricao_tratamento}"


@dataclass
class OcorrenciaDTO:
    """Ocorrência ou Chamado de Suporte/Atendimento (OCORRENCIA)."""
    ocorcod: str
    ocorstat: str = "Pendente"
    entcod: str = ""
    ocorentnome: str = ""
    ocorrespsol: str = ""
    ocordata: str = ""
    motocorcodestr: str = ""
    motocordescr: str = ""
    ocortexto: str = ""
    ocorresptexto: str = ""
    origcodestr: str = ""
    orignome: str = ""
    empcod: str = ""
    ocordatacanc: str = ""
    ocorrespcanc: str = ""
    ocormotcanc: str = ""

    @property
    def is_pendente(self) -> bool:
        return (self.ocorstat or "").strip() == "Pendente"

    @property
    def is_cancelado(self) -> bool:
        return (self.ocorstat or "").strip() == "Cancelado"

    @property
    def is_resolvido(self) -> bool:
        return (self.ocorstat or "").strip() == "Resolvido"

    @property
    def is_em_andamento(self) -> bool:
        return (self.ocorstat or "").strip() == "Em Andamento"


@dataclass
class MotivoOcorrenciaDTO:
    """Motivo ou Área de Ocorrência (MOTIVO_OCOR)."""
    motocorcodestr: str
    motocordescr: str
    motocorgrupo: str = "F"  # 'T' para área/grupo, 'F' para sub-motivo
    motocorresp1: str = ""
    motocorresp2: str = ""
    motocorresp3: str = ""

    @property
    def is_area(self) -> bool:
        return (self.motocorgrupo or "").strip().upper() == "T"


@dataclass
class OrigemDTO:
    """Origem do contato ou ocorrência (ORIGEM)."""
    origcodestr: str
    orignome: str


@dataclass
class SolicitanteDTO:
    """Entidade solicitante de ocorrência (ENTIDADE)."""
    entcod: str
    entnome: str
    categcodestr: str = ""
    entstatdescr: str = ""


@dataclass
class ResultadoCRM:
    """Resultado padronizado de operações do módulo CRM."""
    sucesso: bool = True
    mensagem: str = ""
    id_gerado: str = ""
