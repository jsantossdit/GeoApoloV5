"""
Modelos de dados e DTOs para o Motor de Consultas Dinâmicas e Permissões de Consulta.
GeoApolo V5
"""

from dataclasses import dataclass, field
from typing import List, Any, Optional


@dataclass
class ConsultaConfigDTO:
    """Configuração e definição de uma consulta dinâmica cadastrada."""
    codigo_consulta: str
    descricao_consulta: str
    sql_consulta: str
    tipo_consulta: str = "T"
    banco_consulta: str = "Apolo"


@dataclass
class PermissaoConsultaDTO:
    """Permissão de acesso a uma consulta por usuário."""
    usucod: str
    codigo_consulta: str
    descricao_consulta: str = ""
    autorizacao: str = "S"

    @property
    def autorizado(self) -> bool:
        return self.autorizacao.upper() == "S"

    @property
    def status_display(self) -> str:
        return "Autorizado" if self.autorizado else "Bloqueado"


@dataclass
class FiltroConsultaDTO:
    """Parâmetros para execução de busca dinâmica."""
    controle: str = "CLIENTES"
    campo_busca: str = ""
    texto_busca: str = ""
    campo_ordem: str = ""
    ordem_asc: bool = True
    limite: int = 50


@dataclass
class ResultadoConsultaDTO:
    """Resultado da execução de uma consulta parametrizada."""
    colunas: List[str] = field(default_factory=list)
    linhas: List[List[Any]] = field(default_factory=list)
    total_registros: int = 0
    sucesso: bool = True
    mensagem: str = ""
