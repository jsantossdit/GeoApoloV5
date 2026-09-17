"""
Camada de Serviços e Regras de Negócio do Módulo CRM.
GeoApolo V5
Clean Architecture: Validações, sanitização de dados e orquestração de regras de negócio.
"""

import logging
from typing import List, Optional
from .models import (
    TipoCampanhaDTO,
    TipoTratamentoDTO,
    OcorrenciaDTO,
    MotivoOcorrenciaDTO,
    OrigemDTO,
    SolicitanteDTO,
    ResultadoCRM,
)
from .repository import CRMRepository

logger = logging.getLogger(__name__)


class CRMService:
    """Regras de negócio e validações para Campanhas, Tratamentos e Ocorrências."""

    def __init__(self, repository: CRMRepository):
        self._repo = repository

    # =========================================================================
    # TIPOS DE CAMPANHA
    # =========================================================================

    def listar_tipos_campanha(self, apenas_ativos: bool = False) -> List[TipoCampanhaDTO]:
        return self._repo.listar_tipos_campanha(apenas_ativos)

    def obter_tipo_campanha(self, codigo: str) -> Optional[TipoCampanhaDTO]:
        cod = str(codigo or "").strip()
        if not cod:
            return None
        return self._repo.obter_tipo_campanha(cod)

    def salvar_tipo_campanha(self, dto: TipoCampanhaDTO) -> ResultadoCRM:
        cod = str(dto.codigo_tipocampanha or "").strip()
        desc = str(dto.descricaotipocamp or "").strip()

        if not cod:
            return ResultadoCRM(sucesso=False, mensagem="Código do tipo de campanha é obrigatório.")
        if not desc:
            return ResultadoCRM(sucesso=False, mensagem="Descrição do tipo de campanha é obrigatória.")

        dto.codigo_tipocampanha = cod
        dto.descricaotipocamp = desc
        dto.ativo = "S" if (dto.ativo or "").strip().upper() == "S" else "N"
        dto.geracampanha = "S" if (dto.geracampanha or "").strip().upper() == "S" else "N"

        try:
            self._repo.salvar_tipo_campanha(dto)
            return ResultadoCRM(
                sucesso=True,
                mensagem=f"Tipo de campanha '{desc}' salvo com sucesso.",
                id_gerado=cod,
            )
        except Exception as exc:
            logger.exception("Erro ao salvar tipo de campanha: %s", exc)
            return ResultadoCRM(sucesso=False, mensagem=f"Erro ao salvar tipo de campanha: {exc}")

    def excluir_tipo_campanha(self, codigo: str) -> ResultadoCRM:
        cod = str(codigo or "").strip()
        if not cod:
            return ResultadoCRM(sucesso=False, mensagem="Código do tipo de campanha é obrigatório.")

        try:
            self._repo.excluir_tipo_campanha(cod)
            return ResultadoCRM(sucesso=True, mensagem="Tipo de campanha excluído com sucesso.", id_gerado=cod)
        except Exception as exc:
            logger.exception("Erro ao excluir tipo de campanha: %s", exc)
            return ResultadoCRM(sucesso=False, mensagem=f"Erro ao excluir tipo de campanha: {exc}")

    # =========================================================================
    # TIPOS DE TRATAMENTO
    # =========================================================================

    def listar_tipos_tratamento(self) -> List[TipoTratamentoDTO]:
        return self._repo.listar_tipos_tratamento()

    def obter_tipo_tratamento(self, codigo: str) -> Optional[TipoTratamentoDTO]:
        cod = str(codigo or "").strip()
        if not cod:
            return None
        return self._repo.obter_tipo_tratamento(cod)

    def salvar_tipo_tratamento(self, dto: TipoTratamentoDTO) -> ResultadoCRM:
        cod = str(dto.tipotratcod or "").strip()
        abrev = str(dto.abreviatura or "").strip()
        desc = str(dto.descricao_tratamento or "").strip()

        if not cod:
            return ResultadoCRM(sucesso=False, mensagem="Código do tipo de tratamento é obrigatório.")
        if not abrev:
            return ResultadoCRM(sucesso=False, mensagem="Abreviatura do tipo de tratamento é obrigatória.")
        if not desc:
            return ResultadoCRM(sucesso=False, mensagem="Descrição do tipo de tratamento é obrigatória.")

        dto.tipotratcod = cod
        dto.abreviatura = abrev
        dto.descricao_tratamento = desc

        try:
            self._repo.salvar_tipo_tratamento(dto)
            return ResultadoCRM(
                sucesso=True,
                mensagem=f"Tipo de tratamento '{desc}' salvo com sucesso.",
                id_gerado=cod,
            )
        except Exception as exc:
            logger.exception("Erro ao salvar tipo de tratamento: %s", exc)
            return ResultadoCRM(sucesso=False, mensagem=f"Erro ao salvar tipo de tratamento: {exc}")

    def excluir_tipo_tratamento(self, codigo: str) -> ResultadoCRM:
        cod = str(codigo or "").strip()
        if not cod:
            return ResultadoCRM(sucesso=False, mensagem="Código do tipo de tratamento é obrigatório.")

        try:
            self._repo.excluir_tipo_tratamento(cod)
            return ResultadoCRM(sucesso=True, mensagem="Tipo de tratamento excluído com sucesso.", id_gerado=cod)
        except Exception as exc:
            logger.exception("Erro ao excluir tipo de tratamento: %s", exc)
            return ResultadoCRM(sucesso=False, mensagem=f"Erro ao excluir tipo de tratamento: {exc}")

    # =========================================================================
    # OCORRÊNCIAS
    # =========================================================================

    def listar_ocorrencias(
        self, status: str = "", empcod: str = "", filtro: str = ""
    ) -> List[OcorrenciaDTO]:
        return self._repo.listar_ocorrencias(status, empcod, filtro)

    def obter_ocorrencia(self, ocorcod: str) -> Optional[OcorrenciaDTO]:
        cod = str(ocorcod or "").strip()
        if not cod:
            return None
        return self._repo.obter_ocorrencia(cod)

    def salvar_ocorrencia(self, dto: OcorrenciaDTO) -> ResultadoCRM:
        entcod = str(dto.entcod or "").strip()
        motcod = str(dto.motocorcodestr or "").strip()
        texto = str(dto.ocortexto or "").strip()

        if not entcod:
            return ResultadoCRM(sucesso=False, mensagem="Identificador do solicitante é obrigatório.")
        if not motcod:
            return ResultadoCRM(sucesso=False, mensagem="Motivo da ocorrência é obrigatório.")
        if not texto:
            return ResultadoCRM(sucesso=False, mensagem="Descrição da solicitação é obrigatória.")

        if not str(dto.ocorcod or "").strip():
            dto.ocorcod = self._repo.proximo_codigo_ocorrencia()

        if not str(dto.ocorstat or "").strip():
            dto.ocorstat = "Pendente"

        try:
            self._repo.salvar_ocorrencia(dto)
            return ResultadoCRM(
                sucesso=True,
                mensagem=f"Ocorrência {dto.ocorcod} gravada com sucesso.",
                id_gerado=dto.ocorcod,
            )
        except Exception as exc:
            logger.exception("Erro ao salvar ocorrência: %s", exc)
            return ResultadoCRM(sucesso=False, mensagem=f"Erro ao salvar ocorrência: {exc}")

    def cancelar_ocorrencia(
        self, ocorcod: str, data_canc: str, resp_canc: str, mot_canc: str
    ) -> ResultadoCRM:
        cod = str(ocorcod or "").strip()
        dt = str(data_canc or "").strip()
        mot = str(mot_canc or "").strip()

        if not cod:
            return ResultadoCRM(sucesso=False, mensagem="Código da ocorrência é obrigatório.")
        if not dt:
            return ResultadoCRM(sucesso=False, mensagem="Data de cancelamento é obrigatória.")
        if not mot:
            return ResultadoCRM(sucesso=False, mensagem="Motivo do cancelamento é obrigatório.")

        # Verifica se ocorrência existe e status atual
        atual = self._repo.obter_ocorrencia(cod)
        if not atual:
            return ResultadoCRM(sucesso=False, mensagem=f"Ocorrência {cod} não foi localizada.")
        if atual.is_cancelado:
            return ResultadoCRM(sucesso=False, mensagem="Esta ocorrência já se encontra cancelada.")

        try:
            self._repo.cancelar_ocorrencia(cod, dt, str(resp_canc or "").strip(), mot)
            return ResultadoCRM(
                sucesso=True,
                mensagem=f"Ocorrência {cod} cancelada com sucesso.",
                id_gerado=cod,
            )
        except Exception as exc:
            logger.exception("Erro ao cancelar ocorrência: %s", exc)
            return ResultadoCRM(sucesso=False, mensagem=f"Erro ao cancelar ocorrência: {exc}")

    def atualizar_solucao(
        self, ocorcod: str, resp_texto: str, status: str = "Resolvido", resp_sol: str = ""
    ) -> ResultadoCRM:
        cod = str(ocorcod or "").strip()
        texto = str(resp_texto or "").strip()

        if not cod:
            return ResultadoCRM(sucesso=False, mensagem="Código da ocorrência é obrigatório.")
        if not texto:
            return ResultadoCRM(sucesso=False, mensagem="Texto da solução/resposta é obrigatório.")

        try:
            self._repo.atualizar_solucao(cod, texto, status, resp_sol)
            return ResultadoCRM(
                sucesso=True,
                mensagem=f"Solução da ocorrência {cod} registrada com sucesso.",
                id_gerado=cod,
            )
        except Exception as exc:
            logger.exception("Erro ao atualizar solução: %s", exc)
            return ResultadoCRM(sucesso=False, mensagem=f"Erro ao atualizar solução: {exc}")

    # =========================================================================
    # AUXILIARES
    # =========================================================================

    def listar_areas_disponiveis(self) -> List[MotivoOcorrenciaDTO]:
        return self._repo.listar_areas_disponiveis()

    def listar_motivos_por_area(self, prefixo_area: str) -> List[MotivoOcorrenciaDTO]:
        pref = str(prefixo_area or "").strip()
        return self._repo.listar_motivos_por_area(pref)

    def listar_origens(self) -> List[OrigemDTO]:
        return self._repo.listar_origens()

    def listar_solicitantes(self, filtro: str = "") -> List[SolicitanteDTO]:
        return self._repo.listar_solicitantes(str(filtro or "").strip())
