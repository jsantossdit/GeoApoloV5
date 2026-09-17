"""
Modelos e DTOs para Gestão de Eventos e Importação de Inscrições.
GeoApolo V5
"""

from dataclasses import dataclass
from typing import Optional
from datetime import date, datetime


@dataclass
class EventoResumoDTO:
    """Dados cadastrais de um evento ou congresso."""
    id: str
    descricao: str
    total_inscritos: int = 0


@dataclass
class InscricaoEventoDTO:
    """Registro individual de um participante de evento importado da planilha."""
    evento_id: str
    documento: str
    nome: str
    email: str = ""
    telefone: str = ""
    fatura: str = ""
    status_inscricao: str = "Aprovado"
    forma_pagamento: str = ""
    valor_venda: float = 0.0
    data_criacao: Optional[date] = None
    data_pagamento: Optional[date] = None
    endereco: str = ""
    cidade: str = ""
    uf: str = ""
    cep: str = ""
    ent_cod: Optional[str] = None
    colabora_projetos: bool = False
    ano_mes_ultima_contribuicao: str = ""

    @property
    def vinculado_apolo(self) -> bool:
        return bool(self.ent_cod and self.ent_cod.strip())


@dataclass
class ResultadoImportacaoDTO:
    """Resumo estatístico do processamento de um lote de inscrições."""
    total_linhas: int = 0
    total_com_documento: int = 0
    total_vinculados_apolo: int = 0
    total_salvos: int = 0
    sucesso: bool = True
    mensagem: str = ""


@dataclass
class TipoEventoDTO:
    """Tipo ou categoria de evento cadastrado no sistema."""
    tipo_event_cod: str
    descricao_tipo_evento: str


@dataclass
class EventoDTO:
    """Dados cadastrais completos de um evento (USER_geoapolo_eventos)."""
    id_evento: str
    descricao: str
    data_inicial: str = ""
    data_final: str = ""
    tema_principal: str = ""
    tipo_event_cod: str = ""
    descricao_tipo_evento: str = ""


@dataclass
class ResultadoEventoDTO:
    """Resultado de operações de cadastro de eventos."""
    sucesso: bool = True
    mensagem: str = ""
    id_gerado: str = ""
