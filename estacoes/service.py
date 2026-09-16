"""
Camada de Negócio e Serviços para o Módulo de Estações de Trabalho.
Regras de validação, cálculo de garantia e orquestração.
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, Optional
from estacoes.models import ResultadoOperacao
from estacoes.repository import EstacoesRepository

logger = logging.getLogger(__name__)


class EstacoesService:
    """Regras de negócio e validações para inventário de estações, hardware e software."""

    def __init__(self, repository: EstacoesRepository):
        self._repo = repository

    @staticmethod
    def validar_ip(ip: str) -> bool:
        if not ip or not ip.strip():
            return True  # Campo opcional
        padrao = r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        return bool(re.match(padrao, ip.strip()))

    def validar_estacao(self, dados: Dict[str, Any]) -> Tuple[bool, str]:
        if not str(dados.get("codigo_estacao") or "").strip():
            return False, "O código da estação é obrigatório."

        if not str(dados.get("descricao") or "").strip():
            return False, "A descrição da estação é obrigatória."

        ip = str(dados.get("enderecoip") or "").strip()
        if ip and not self.validar_ip(ip):
            return False, f"O endereço IP '{ip}' possui formato inválido."

        return True, ""

    def validar_hardware(self, dados: Dict[str, Any]) -> Tuple[bool, str]:
        if not str(dados.get("codigo_hardware") or "").strip():
            return False, "O código do hardware é obrigatório."

        if not str(dados.get("descricao") or "").strip():
            return False, "A descrição do hardware é obrigatória."

        if not str(dados.get("codigo_estacao") or "").strip():
            return False, "O hardware deve estar vinculado a uma estação."

        try:
            val = float(dados.get("valor", 0.0) or 0.0)
            if val < 0:
                return False, "O valor do hardware não pode ser negativo."
        except (ValueError, TypeError):
            return False, "O valor informado é inválido."

        ip = str(dados.get("ip") or "").strip()
        if ip and not self.validar_ip(ip):
            return False, f"O IP do hardware '{ip}' possui formato inválido."

        return True, ""

    def validar_software(self, dados: Dict[str, Any]) -> Tuple[bool, str]:
        if not str(dados.get("codigo_software") or "").strip():
            return False, "O código do software é obrigatório."

        if not str(dados.get("descricao") or "").strip():
            return False, "A descrição do software é obrigatória."

        if not str(dados.get("codigo_estacao") or "").strip():
            return False, "O software deve estar vinculado a uma estação."

        return True, ""

    @staticmethod
    def calcular_dias_garantia_restante(data_compra_str: str, dias_garantia: int) -> int:
        if not data_compra_str or dias_garantia <= 0:
            return 0
        try:
            # Aceita DD/MM/YYYY ou YYYY-MM-DD
            if "/" in data_compra_str:
                dt_compra = datetime.strptime(data_compra_str.strip(), "%d/%m/%Y")
            else:
                dt_compra = datetime.strptime(data_compra_str.strip()[:10], "%Y-%m-%d")

            dt_limite = dt_compra + timedelta(days=dias_garantia)
            hoje = datetime.now()
            delta = (dt_limite - hoje).days
            return delta
        except Exception:
            return 0

    def salvar_estacao(self, dados: Dict[str, Any], modo_inclusao: bool = True) -> ResultadoOperacao:
        valido, msg = self.validar_estacao(dados)
        if not valido:
            return ResultadoOperacao(sucesso=False, mensagem=msg)

        try:
            self._repo.salvar_estacao(dados, modo_inclusao=modo_inclusao)
            cod = dados.get("codigo_estacao")
            return ResultadoOperacao(
                sucesso=True,
                mensagem=f"Estação {cod} gravada com sucesso!",
                codigo=str(cod),
            )
        except Exception as exc:
            logger.exception("Falha ao salvar estação: %s", exc)
            return ResultadoOperacao(sucesso=False, mensagem=f"Erro ao salvar estação:\n{exc}")

    def excluir_estacao(self, codigo: str) -> ResultadoOperacao:
        if not codigo or not codigo.strip():
            return ResultadoOperacao(sucesso=False, mensagem="Código não informado.")

        try:
            self._repo.excluir_estacao(codigo.strip())
            return ResultadoOperacao(
                sucesso=True,
                mensagem=f"Estação {codigo} excluída com sucesso!",
                codigo=codigo,
            )
        except Exception as exc:
            logger.exception("Falha ao excluir estação: %s", exc)
            return ResultadoOperacao(sucesso=False, mensagem=f"Erro ao excluir estação:\n{exc}")

    def salvar_hardware(self, dados: Dict[str, Any], modo_inclusao: bool = True) -> ResultadoOperacao:
        valido, msg = self.validar_hardware(dados)
        if not valido:
            return ResultadoOperacao(sucesso=False, mensagem=msg)

        try:
            self._repo.salvar_hardware(dados, modo_inclusao=modo_inclusao)
            cod = dados.get("codigo_hardware")
            return ResultadoOperacao(sucesso=True, mensagem="Hardware gravado com sucesso!", codigo=str(cod))
        except Exception as exc:
            logger.exception("Falha ao salvar hardware: %s", exc)
            return ResultadoOperacao(sucesso=False, mensagem=f"Erro ao salvar hardware:\n{exc}")

    def excluir_hardware(self, codigo: str) -> ResultadoOperacao:
        if not codigo or not codigo.strip():
            return ResultadoOperacao(sucesso=False, mensagem="Código não informado.")
        try:
            self._repo.excluir_hardware(codigo.strip())
            return ResultadoOperacao(sucesso=True, mensagem="Hardware excluído com sucesso!", codigo=codigo)
        except Exception as exc:
            logger.exception("Falha ao excluir hardware: %s", exc)
            return ResultadoOperacao(sucesso=False, mensagem=f"Erro ao excluir hardware:\n{exc}")
