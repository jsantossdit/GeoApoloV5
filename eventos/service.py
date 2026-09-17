"""
Camada de Serviços e Regras de Negócio para Eventos e Congressos.
GeoApolo V5
"""

import logging
from typing import List, Optional, Callable
from .models import (
    InscricaoEventoDTO,
    ResultadoImportacaoDTO,
    EventoResumoDTO,
    TipoEventoDTO,
    EventoDTO,
    ResultadoEventoDTO,
)
from .repository import EventosRepository
from .importer import PlanilhaInscricoesReader

logger = logging.getLogger(__name__)


class EventosService:
    """Orquestração de importação de planilhas e vínculo com a base de entidades Apolo."""

    def __init__(self, repository: EventosRepository):
        self._repo = repository

    def carregar_planilha(self, caminho_arquivo: str, evento_id: str) -> List[InscricaoEventoDTO]:
        return PlanilhaInscricoesReader.ler_arquivo(caminho_arquivo, evento_id)

    def cruzar_com_apolo(
        self,
        inscricoes: List[InscricaoEventoDTO],
        callback_progresso: Optional[Callable[[int, int], None]] = None,
    ) -> ResultadoImportacaoDTO:
        total = len(inscricoes)
        com_doc = 0
        vinculados = 0

        for idx, item in enumerate(inscricoes):
            if item.documento:
                com_doc += 1
                ent_cod, colabora, anomes = self._repo.buscar_vinculo_apolo(item.documento)
                item.ent_cod = ent_cod
                item.colabora_projetos = colabora
                item.ano_mes_ultima_contribuicao = anomes
                if ent_cod:
                    vinculados += 1

            if callback_progresso and (idx % 20 == 0 or idx == total - 1):
                callback_progresso(idx + 1, total)

        return ResultadoImportacaoDTO(
            total_linhas=total,
            total_com_documento=com_doc,
            total_vinculados_apolo=vinculados,
            sucesso=True,
            mensagem="Cruzamento com base Apolo realizado com sucesso.",
        )

    def evento_ja_importado(self, evento_id: str) -> bool:
        e = str(evento_id or "").strip()
        if not e:
            return False
        return self._repo.evento_ja_importado(e)

    def remover_importacao_anterior(self, evento_id: str) -> int:
        e = str(evento_id or "").strip()
        if not e:
            return 0
        return self._repo.remover_importacao_anterior(e)

    def salvar_inscricoes(
        self, evento_id: str, inscricoes: List[InscricaoEventoDTO]
    ) -> ResultadoImportacaoDTO:
        e = str(evento_id or "").strip()
        if not e:
            return ResultadoImportacaoDTO(sucesso=False, mensagem="Identificador do evento obrigatório.")

        if not inscricoes:
            return ResultadoImportacaoDTO(sucesso=False, mensagem="Nenhuma inscrição para salvar.")

        try:
            total_salvos = self._repo.salvar_inscricoes(e, inscricoes)
            com_doc = sum(1 for it in inscricoes if it.documento)
            vinculados = sum(1 for it in inscricoes if it.vinculado_apolo)

            return ResultadoImportacaoDTO(
                total_linhas=len(inscricoes),
                total_com_documento=com_doc,
                total_vinculados_apolo=vinculados,
                total_salvos=total_salvos,
                sucesso=True,
                mensagem=f"Importação concluída! {total_salvos} inscrições salvas no evento '{e}'.",
            )
        except Exception as exc:
            logger.exception("Erro ao salvar inscrições: %s", exc)
            return ResultadoImportacaoDTO(
                sucesso=False,
                mensagem=f"Falha ao persistir inscrições no banco de dados:\n{exc}",
            )

    def listar_inscricoes_evento(self, evento_id: str) -> List[InscricaoEventoDTO]:
        e = str(evento_id or "").strip()
        if not e:
            return []
        return self._repo.listar_inscricoes_evento(e)

    def listar_eventos(self) -> List[EventoResumoDTO]:
        return self._repo.listar_eventos_cadastrados()

    def listar_eventos_completos(self, filtro_tema: str = "") -> List[EventoDTO]:
        return self._repo.listar_eventos_cadastrados_completos(filtro_tema)

    def obter_evento(self, id_evento: str) -> Optional[EventoDTO]:
        if not id_evento or not id_evento.strip():
            return None
        return self._repo.obter_evento(id_evento.strip())

    def salvar_evento(self, evento: EventoDTO) -> ResultadoEventoDTO:
        if not evento.id_evento or not evento.id_evento.strip():
            return ResultadoEventoDTO(sucesso=False, mensagem="Identificador do evento é obrigatório.")
        if not evento.descricao or not evento.descricao.strip():
            return ResultadoEventoDTO(sucesso=False, mensagem="Descrição do evento é obrigatória.")

        try:
            self._repo.salvar_evento(evento)
            return ResultadoEventoDTO(
                sucesso=True,
                mensagem=f"Evento '{evento.descricao}' salvo com sucesso.",
                id_gerado=evento.id_evento,
            )
        except Exception as exc:
            logger.exception("Erro ao salvar evento: %s", exc)
            return ResultadoEventoDTO(sucesso=False, mensagem=f"Erro ao salvar evento: {exc}")

    def excluir_evento(self, id_evento: str) -> ResultadoEventoDTO:
        if not id_evento or not id_evento.strip():
            return ResultadoEventoDTO(sucesso=False, mensagem="Identificador do evento é obrigatório.")

        try:
            self._repo.excluir_evento(id_evento.strip())
            return ResultadoEventoDTO(sucesso=True, mensagem="Evento excluído com sucesso.", id_gerado=id_evento)
        except Exception as exc:
            logger.exception("Erro ao excluir evento: %s", exc)
            return ResultadoEventoDTO(sucesso=False, mensagem=f"Erro ao excluir evento: {exc}")

    def listar_tipos_evento(self) -> List[TipoEventoDTO]:
        return self._repo.listar_tipos_evento()

    def salvar_tipo_evento(self, tipo: TipoEventoDTO) -> ResultadoEventoDTO:
        if not tipo.tipo_event_cod or not tipo.tipo_event_cod.strip():
            return ResultadoEventoDTO(sucesso=False, mensagem="Código do tipo de evento é obrigatório.")
        if not tipo.descricao_tipo_evento or not tipo.descricao_tipo_evento.strip():
            return ResultadoEventoDTO(sucesso=False, mensagem="Descrição do tipo de evento é obrigatória.")

        try:
            self._repo.salvar_tipo_evento(tipo)
            return ResultadoEventoDTO(
                sucesso=True,
                mensagem=f"Tipo de evento '{tipo.descricao_tipo_evento}' salvo com sucesso.",
                id_gerado=tipo.tipo_event_cod,
            )
        except Exception as exc:
            logger.exception("Erro ao salvar tipo de evento: %s", exc)
            return ResultadoEventoDTO(sucesso=False, mensagem=f"Erro ao salvar tipo de evento: {exc}")

    def excluir_tipo_evento(self, tipo_cod: str) -> ResultadoEventoDTO:
        if not tipo_cod or not tipo_cod.strip():
            return ResultadoEventoDTO(sucesso=False, mensagem="Código do tipo de evento é obrigatório.")

        try:
            self._repo.excluir_tipo_evento(tipo_cod.strip())
            return ResultadoEventoDTO(sucesso=True, mensagem="Tipo de evento excluído com sucesso.")
        except Exception as exc:
            logger.exception("Erro ao excluir tipo de evento: %s", exc)
            return ResultadoEventoDTO(sucesso=False, mensagem=f"Erro ao excluir tipo de evento: {exc}")

