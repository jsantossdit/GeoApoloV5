"""
Camada de Serviços e Regras de Negócio para Gestão de Vínculos Diocese x Entidades RCC.
GeoApolo V5
"""

import logging
from typing import List, Optional
from .models import (
    EntidadeDioceseDTO,
    DioceseCNBBDTO,
    FiltroVinculoDioceseDTO,
    ResultadoOperacaoDiocese,
)
from .repository import DiocesesRepository

logger = logging.getLogger(__name__)


class DiocesesService:
    """Regras de negócio e orquestração para relacionamento entre Entidades e Dioceses CNBB."""

    def __init__(self, repository: Optional[DiocesesRepository] = None):
        self._repository = repository or DiocesesRepository()

    def listar_entidades(self, filtro: FiltroVinculoDioceseDTO) -> List[EntidadeDioceseDTO]:
        """
        Consulta entidades e validações de período.
        """
        if filtro.data_inicial and filtro.data_final:
            if filtro.data_inicial > filtro.data_final:
                raise ValueError("A data inicial não pode ser posterior à data final.")

        return self._repository.listar_entidades(filtro)

    def obter_entidade(self, entcod: str) -> Optional[EntidadeDioceseDTO]:
        """Busca entidade por código."""
        if not entcod or not str(entcod).strip():
            return None
        return self._repository.obter_entidade(str(entcod).strip())

    def listar_dioceses(
        self,
        uf: Optional[str] = None,
        cidade: Optional[str] = None,
        termo: Optional[str] = None
    ) -> List[DioceseCNBBDTO]:
        """Consulta catálogo de dioceses cadastradas."""
        return self._repository.listar_dioceses(uf=uf, cidade=cidade, termo=termo)

    def sugerir_diocese(self, cidade: str, uf: str) -> Optional[DioceseCNBBDTO]:
        """
        Tenta localizar automaticamente a diocese da cidade e UF informadas.
        """
        if not cidade or not cidade.strip():
            return None
        return self._repository.sugerir_diocese_por_cidade(cidade=cidade.strip(), uf=uf.strip() if uf else "")

    def vincular(
        self,
        entcod: str,
        diocese_id: Optional[str],
        nome_diocese: Optional[str]
    ) -> ResultadoOperacaoDiocese:
        """
        Vincula ou atualiza a diocese da entidade. Se diocese_id for nulo ou vazio, desvincula.
        """
        entcod_limpo = str(entcod).strip() if entcod else ""
        if not entcod_limpo:
            return ResultadoOperacaoDiocese(
                sucesso=False,
                mensagem="Código da Entidade deve ser informado.",
                afetados=0
            )

        dio_id_limpo = str(diocese_id).strip() if diocese_id else ""
        dio_nome_limpo = str(nome_diocese).strip() if nome_diocese else ""

        try:
            if not dio_id_limpo:
                # Trata como desvinculação
                self._repository.desvincular_diocese(entcod_limpo)
                return ResultadoOperacaoDiocese(
                    sucesso=True,
                    mensagem=f"Diocese desvinculada com sucesso da entidade {entcod_limpo}.",
                    afetados=1
                )

            self._repository.vincular_diocese(
                entcod=entcod_limpo,
                diocese_id=dio_id_limpo,
                nome_diocese=dio_nome_limpo
            )
            return ResultadoOperacaoDiocese(
                sucesso=True,
                mensagem=f"Entidade {entcod_limpo} vinculada com sucesso à Diocese '{dio_nome_limpo}'.",
                afetados=1
            )
        except Exception as e:
            logger.exception("Falha ao salvar vínculo da diocese")
            return ResultadoOperacaoDiocese(
                sucesso=False,
                mensagem=f"Erro operacional ao salvar vínculo: {e}",
                afetados=0
            )

    def desvincular(self, entcod: str) -> ResultadoOperacaoDiocese:
        """Remove o vínculo entre entidade e diocese."""
        return self.vincular(entcod=entcod, diocese_id=None, nome_diocese=None)
