"""
Regras de Negócio e Serviços para Manutenção de Códigos do Sistema.
GeoApolo V5
Clean Architecture: Validações de integridade sequencial e controle de tabelas ativas.
"""

import logging
from typing import List, Optional

from .models import ConfigCodDTO, ResultadoConfigCodDTO
from .repository import ConfigCodRepository

logger = logging.getLogger(__name__)


class ConfigCodService:
    """Regras de negócio para gerenciar a numeração e sequenciais de tabelas do GeoApolo."""

    def __init__(self, repository: ConfigCodRepository):
        self._repo = repository

    def listar_tabelas(self, filtro: str = "") -> List[ConfigCodDTO]:
        return self._repo.listar_tabelas(filtro)

    def obter_config_cod(self, geotabela: str) -> Optional[ConfigCodDTO]:
        if not geotabela.strip():
            return None
        return self._repo.obter_config_cod(geotabela)

    def atualizar_config_cod(
        self, geotabela: str, proximo_codigo: int, tabela_ativa: str
    ) -> ResultadoConfigCodDTO:
        tab_limpa = geotabela.strip()
        if not tab_limpa:
            return ResultadoConfigCodDTO(sucesso=False, mensagem="Nome da tabela é obrigatório.")

        if proximo_codigo < 0:
            return ResultadoConfigCodDTO(
                sucesso=False,
                mensagem="Não é permitido definir um código sequencial negativo.",
                geotabela=tab_limpa,
            )

        status = "S" if (tabela_ativa or "").strip().upper() in ("S", "TRUE", "SIM", "1") else "N"

        try:
            self._repo.atualizar_proximo_codigo(tab_limpa, proximo_codigo, status)
            return ResultadoConfigCodDTO(
                sucesso=True,
                mensagem=f"Sequencial da tabela '{tab_limpa}' atualizado para {proximo_codigo} com sucesso!",
                geotabela=tab_limpa,
                proximo_codigo=proximo_codigo,
            )
        except Exception as exc:
            logger.exception("Erro ao atualizar sequencial da tabela %s: %s", tab_limpa, exc)
            return ResultadoConfigCodDTO(sucesso=False, mensagem=f"Erro ao atualizar sequencial:\n{exc}")

    def salvar_config_cod(self, dto: ConfigCodDTO) -> ResultadoConfigCodDTO:
        tab_limpa = dto.geotabela.strip()
        if not tab_limpa:
            return ResultadoConfigCodDTO(sucesso=False, mensagem="Nome da tabela é obrigatório.")

        if dto.proximo_codigo < 0:
            return ResultadoConfigCodDTO(
                sucesso=False,
                mensagem="O próximo código não pode ser negativo.",
                geotabela=tab_limpa,
            )

        dto.geotabela = tab_limpa
        dto.tabela_ativa = "S" if dto.is_ativa else "N"

        try:
            self._repo.salvar_config_cod(dto)
            return ResultadoConfigCodDTO(
                sucesso=True,
                mensagem=f"Configuração da tabela '{tab_limpa}' gravada com sucesso!",
                geotabela=tab_limpa,
                proximo_codigo=dto.proximo_codigo,
            )
        except Exception as exc:
            logger.exception("Erro ao salvar configuração da tabela %s: %s", tab_limpa, exc)
            return ResultadoConfigCodDTO(sucesso=False, mensagem=f"Erro ao salvar configuração:\n{exc}")

    def obter_proximo_codigo(self, geotabela: str, auto_incrementar: bool = False) -> int:
        """Recupera o próximo código numérico da tabela, com opção de auto-incrementar."""
        tab_limpa = geotabela.strip()
        if not tab_limpa:
            return 1

        if auto_incrementar:
            return self._repo.gerar_e_incrementar_codigo(tab_limpa)

        cfg = self._repo.obter_config_cod(tab_limpa)
        return cfg.proximo_codigo if cfg else 1
