"""
Camada de Serviços e Regras de Negócio para Centros de Controle / Custos.
GeoApolo V5
Validações de integridade, hierarquia estruturada e vigência.
"""

import re
import logging
from typing import List, Optional
from datetime import datetime

from .models import CentroControleDTO, ResultadoCentroControleDTO
from .repository import CentroControleRepository

logger = logging.getLogger(__name__)


class CentroControleService:
    """Regras de negócio e operações de Centros de Controle."""

    def __init__(self, repository: CentroControleRepository):
        self._repo = repository

    def listar_centros(self, termo: str = "", empcod: str = "") -> List[CentroControleDTO]:
        """Lista os centros de controle cadastrados com suporte a busca."""
        return self._repo.listar_centros(termo=termo, empcod=empcod)

    def obter_centro(self, geocctrlcodestr: str) -> Optional[CentroControleDTO]:
        """Retorna os dados de um centro de controle específico."""
        if not geocctrlcodestr or not geocctrlcodestr.strip():
            return None
        return self._repo.obter_centro(geocctrlcodestr.strip().upper())

    def listar_niveis_superiores(self) -> List[CentroControleDTO]:
        """Retorna níveis que podem ser pais de outros centros."""
        return self._repo.listar_niveis_superiores()

    def obter_sugestao_codigo_reduzido(self) -> str:
        """Sugere o próximo código reduzido livre."""
        return self._repo.obter_proximo_codigo_reduzido()

    def salvar_centro(self, dto: CentroControleDTO) -> ResultadoCentroControleDTO:
        """Valida e salva centro de controle."""
        cod_estr = (dto.geocctrlcodestr or "").strip().upper()
        if not cod_estr:
            return ResultadoCentroControleDTO(sucesso=False, mensagem="O Código Estruturado do Centro de Controle é obrigatório.")

        # Validação de formato (ex: 004, 004.001, 004.001.001, etc.)
        if not re.match(r"^[A-Z0-9\.\-_]+$", cod_estr):
            return ResultadoCentroControleDTO(sucesso=False, mensagem="O Código Estruturado contém caracteres inválidos. Utilize números, letras, pontos ou hífens.")

        nome = (dto.geocctrlnome or "").strip().upper()
        if not nome:
            return ResultadoCentroControleDTO(sucesso=False, mensagem="A Descrição / Nome do Centro de Controle é obrigatória.")

        cod_red = (dto.geocctrlcodreduzido or "").strip()
        if not cod_red:
            cod_red = self.obter_sugestao_codigo_reduzido()

        grupo = (dto.geocctrlgrupo or "A").strip().upper()
        if grupo not in ("T", "A", "F"):
            grupo = "A"

        # Validação de Nível Superior (não pode ser pai de si mesmo)
        niv_pai = (dto.geocctrlcodestrniv or "").strip().upper()
        if niv_pai and niv_pai == cod_estr:
            return ResultadoCentroControleDTO(sucesso=False, mensagem="O Centro de Controle não pode ser nível superior de si mesmo.")

        # Padroniza DTO higienizado
        dto_sanitizado = CentroControleDTO(
            geocctrlcodestr=cod_estr,
            geocctrlcodreduzido=cod_red,
            geocctrlnome=nome,
            geocctrlcodestrniv=niv_pai,
            geocctrlgrupo=grupo,
            geocctrlcusto=(dto.geocctrlcusto or "").strip(),
            geodatavalidadeinicial=dto.geodatavalidadeinicial,
            geodatavalidadefinal=dto.geodatavalidadefinal,
            empcod=(dto.empcod or "1.01").strip(),
        )

        try:
            self._repo.salvar_centro(dto_sanitizado)
            return ResultadoCentroControleDTO(
                sucesso=True,
                mensagem=f"Centro de Controle '{cod_estr} - {nome}' salvo com sucesso!",
                codigo=cod_estr,
                objeto=dto_sanitizado
            )
        except Exception as e:
            logger.error("Erro ao salvar centro de controle: %s", e)
            return ResultadoCentroControleDTO(sucesso=False, mensagem=f"Erro ao salvar centro de controle: {e}")

    def excluir_centro(self, geocctrlcodestr: str) -> ResultadoCentroControleDTO:
        """Valida e exclui centro de controle."""
        cod_estr = (geocctrlcodestr or "").strip().upper()
        if not cod_estr:
            return ResultadoCentroControleDTO(sucesso=False, mensagem="Código do Centro de Controle não informado.")

        centro = self._repo.obter_centro(cod_estr)
        if not centro:
            return ResultadoCentroControleDTO(sucesso=False, mensagem=f"Centro de Controle '{cod_estr}' não encontrado.")

        # Verifica se há centros filhos subordinados a este nível
        todos = self._repo.listar_centros()
        filhos = [c for c in todos if c.geocctrlcodestrniv.upper() == cod_estr]
        if filhos:
            return ResultadoCentroControleDTO(
                sucesso=False,
                mensagem=f"Não é possível excluir o centro '{cod_estr}' pois existem {len(filhos)} centros de controle vinculados como subníveis a ele."
            )

        try:
            self._repo.excluir_centro(cod_estr)
            return ResultadoCentroControleDTO(
                sucesso=True,
                mensagem=f"Centro de Controle '{cod_estr}' excluído com sucesso!",
                codigo=cod_estr
            )
        except Exception as e:
            logger.error("Erro ao excluir centro de controle: %s", e)
            return ResultadoCentroControleDTO(sucesso=False, mensagem=f"Erro ao excluir centro de controle: {e}")
