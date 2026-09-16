"""
Camada de Serviços para Saneamento e Correção de Cidades e Distritos.
GeoApolo V5
"""

import logging
from typing import List, Optional, Dict, Any
from core.viacep import ViaCEPClient
from .models import (
    CidadeDistritoDTO,
    EntidadeLocalidadeDTO,
    ResultadoCorrecaoLocalidadeDTO,
)
from .repository import LocalidadesRepository

logger = logging.getLogger(__name__)


class LocalidadesService:
    """Regras de saneamento de cadastro de municípios, distritos e consulta ViaCEP."""

    def __init__(self, repository: LocalidadesRepository, viacep_client: Optional[ViaCEPClient] = None):
        self._repo = repository
        self._viacep = viacep_client or ViaCEPClient()

    def buscar_cidades(self, termo: str = "", uf: str = "") -> List[CidadeDistritoDTO]:
        return self._repo.listar_cidades(termo, uf)

    def obter_entidades_localidade(self, cid_cod: str) -> List[EntidadeLocalidadeDTO]:
        c = str(cid_cod or "").strip()
        if not c:
            return []
        return self._repo.listar_entidades_por_cidade(c)

    def consultar_cep(self, cep: str) -> Optional[Dict[str, Any]]:
        return self._viacep.consultar_cep(cep)

    def corrigir_distrito_para_cidade(
        self, cid_origem: str, cid_destino: str
    ) -> ResultadoCorrecaoLocalidadeDTO:
        orig = str(cid_origem or "").strip()
        dest = str(cid_destino or "").strip()

        if not orig:
            return ResultadoCorrecaoLocalidadeDTO(False, "Selecione o distrito de origem.")
        if not dest:
            return ResultadoCorrecaoLocalidadeDTO(False, "Selecione a cidade mãe de destino.")
        if orig == dest:
            return ResultadoCorrecaoLocalidadeDTO(False, "A localidade de origem e destino não podem ser as mesmas.")

        try:
            total = self._repo.migrar_entidades(orig, dest)
            return ResultadoCorrecaoLocalidadeDTO(
                sucesso=True,
                mensagem=f"Correção concluída com sucesso! {total} entidades foram reatribuídas à cidade destino.",
                entidades_migradas=total,
            )
        except Exception as e:
            logger.exception("Erro na correção de localidades: %s", e)
            return ResultadoCorrecaoLocalidadeDTO(False, f"Erro ao migrar entidades:\n{e}", 0)
