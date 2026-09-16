"""
Modelos de dados (DTOs) para gerenciamento e vínculo de Entidades com Dioceses da CNBB.
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class EntidadeDioceseDTO:
    """Representa os dados de uma entidade cadastrada e sua associação com Diocese CNBB."""
    entcod: str
    entnome: str
    cidcod: str = ""
    cidnomecomp: str = ""
    ufsigla: str = ""
    user_diocese_id: Optional[str] = None
    user_nome_diocese: Optional[str] = None
    user_jana_sve: Optional[str] = None  # 'S', 'N' ou None

    @property
    def tem_diocese(self) -> bool:
        """Indica se a entidade já possui diocese associada."""
        return bool(self.user_diocese_id and str(self.user_diocese_id).strip())

    @property
    def status_sve_formatado(self) -> str:
        """Formata o status de inclusão na plataforma SVE."""
        if self.user_jana_sve == 'S':
            return "DISPONÍVEL NA SVE"
        elif self.user_jana_sve == 'N':
            return "NÃO INCLUÍDA NA SVE"
        return "NÃO INFORMADO"


@dataclass
class DioceseCNBBDTO:
    """Representa os dados de uma Diocese cadastrada pela CNBB."""
    id: str
    nome: str
    estado_id: str = ""
    cidade: str = ""
    ufsigla: str = ""
    nome_estado: str = ""

    @property
    def display_completo(self) -> str:
        """Retorna representação textual da diocese com UF/cidade."""
        uf = f" ({self.ufsigla})" if self.ufsigla else ""
        cid = f" - {self.cidade}" if self.cidade else ""
        return f"{self.nome}{uf}{cid}"


@dataclass
class FiltroVinculoDioceseDTO:
    """Parâmetros de filtro para consulta de entidades."""
    data_inicial: Optional[date] = None
    data_final: Optional[date] = None
    apenas_sem_diocese: bool = True
    termo_busca: Optional[str] = None


@dataclass
class ResultadoOperacaoDiocese:
    """Resultado estruturado de operações de vinculação ou desvinculação."""
    sucesso: bool
    mensagem: str
    afetados: int = 0
