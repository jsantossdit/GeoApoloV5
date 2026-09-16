"""
Camada de Serviços e Regras de Negócio para Configurações do Sistema.
"""

import os
import logging
from typing import Dict, Any, Tuple
from configuracoes.models import ResultadoOperacao
from configuracoes.repository import ConfiguracoesRepository

logger = logging.getLogger(__name__)


class ConfiguracoesService:
    """Regras de negócio, sanitização de diretórios e persistência de parâmetros."""

    def __init__(self, repository: ConfiguracoesRepository):
        self._repo = repository

    @staticmethod
    def normalizar_caminho(caminho: str) -> str:
        """Normaliza caminho de arquivos, removendo marcadores legados ($ ou #) e padronizando barras."""
        if not caminho:
            return ""
        s = str(caminho).strip()
        s = s.replace("$", os.sep).replace("#", "-").replace("/", os.sep)
        return s.rstrip(os.sep)

    @staticmethod
    def validar_diretorio(caminho: str, criar_se_nao_existir: bool = False) -> bool:
        """Verifica se o diretório existe ou tenta criá-lo com segurança."""
        if not caminho or not caminho.strip():
            return True
        c = ConfiguracoesService.normalizar_caminho(caminho)
        if os.path.exists(c) and os.path.isdir(c):
            return True
        if criar_se_nao_existir:
            try:
                os.makedirs(c, exist_ok=True)
                return os.path.exists(c)
            except Exception:
                return False
        return False

    def salvar_parametros(self, dados: Dict[str, Any], empresa_codigo: str) -> ResultadoOperacao:
        if not empresa_codigo or not empresa_codigo.strip():
            return ResultadoOperacao(sucesso=False, mensagem="Código da empresa é obrigatório.")

        # Normaliza todos os campos de caminhos
        dados_normalizados = dict(dados)
        campos_caminho = [
            "caminhobackupsistema",
            "instalacaolocal",
            "localnovasversoes",
            "localinstaladorversoes",
            "caminhoarquivoconvenio",
            "caminhoinventario",
            "caminhodocti",
            "caminhodocmissaopopular",
            "caminhobasealvoloja",
        ]
        for c in campos_caminho:
            if c in dados_normalizados:
                dados_normalizados[c] = self.normalizar_caminho(dados_normalizados[c])

        try:
            self._repo.salvar_configuracoes(dados_normalizados, empresa_codigo.strip())
            return ResultadoOperacao(
                sucesso=True,
                mensagem="Configurações do sistema gravadas com sucesso!",
                codigo=empresa_codigo,
            )
        except Exception as exc:
            logger.exception("Erro ao salvar configurações do sistema: %s", exc)
            return ResultadoOperacao(
                sucesso=False,
                mensagem=f"Erro ao salvar configurações no banco:\n{exc}",
            )

    def obter_parametros(self, empresa_codigo: str) -> Dict[str, Any]:
        return self._repo.obter_configuracoes(empresa_codigo)
