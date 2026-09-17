"""
Modelos de Dados e DTOs para Nomes Amigáveis de Controles e Telas do GeoApolo.
GeoApolo V5
Clean Architecture: DTOs imutáveis para mapeamento de metadados e nomes humanizados.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ObjetoSistemaDTO:
    """Metadados de um controle/objeto do sistema (USER_geoapolo_objetos)."""
    nome_objeto: str = ""
    nome_amigavel: str = ""
    categoria: str = "Geral"

    @property
    def display(self) -> str:
        cat = self.categoria or "Geral"
        return f"[{cat}] {self.nome_amigavel or self.nome_objeto} ({self.nome_objeto})"


@dataclass
class ResultadoNomesAmigaveisDTO:
    """Resultado padronizado de operações do dicionário de nomes amigáveis."""
    sucesso: bool = True
    mensagem: str = ""
    total_afetados: int = 0
    nome_objeto: Optional[str] = None
