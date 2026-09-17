"""
Camada de Serviços e Regras de Negócio para Configurações do Sistema.
"""

import os
import logging
from typing import Dict, Any, Tuple, Optional
from configuracoes.models import (
    ResultadoOperacao,
    ConfiguracaoBancoDTO,
    ResultadoTesteConexaoDTO,
)
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

    def obter_config_banco(self, arquivo_json: str = "") -> ConfiguracaoBancoDTO:
        """Obtém as configurações de banco de dados locais."""
        return self._repo.carregar_config_banco(arquivo_json)

    @staticmethod
    def validar_config_banco(config: ConfiguracaoBancoDTO) -> Tuple[bool, str]:
        """Valida se os parâmetros de conexão estão preenchidos e válidos."""
        if not config.servidor or not config.servidor.strip():
            return False, "Nome ou IP do servidor é obrigatório."
        if not config.banco or not config.banco.strip():
            return False, "Nome do banco de dados é obrigatório."
        if config.porta < 1 or config.porta > 65535:
            return False, "Porta TCP inválida (deve estar entre 1 e 65535)."
        if not config.usuario or not config.usuario.strip():
            return False, "Usuário de autenticação é obrigatório."
        return True, "Parâmetros válidos."

    def salvar_config_banco(
        self, config: ConfiguracaoBancoDTO, arquivo_json: str = ""
    ) -> ResultadoOperacao:
        """Valida e persiste as configurações de banco de dados."""
        valido, msg = self.validar_config_banco(config)
        if not valido:
            return ResultadoOperacao(sucesso=False, mensagem=msg)

        if self._repo.salvar_config_banco(config, arquivo_json):
            return ResultadoOperacao(
                sucesso=True,
                mensagem="Configurações de banco de dados salvas com sucesso!",
            )
        return ResultadoOperacao(
            sucesso=False,
            mensagem="Falha ao salvar arquivo de configurações de banco.",
        )

    def testar_conexao_banco(self, config: ConfiguracaoBancoDTO) -> ResultadoTesteConexaoDTO:
        """Executa teste de conectividade com o servidor especificado."""
        valido, msg = self.validar_config_banco(config)
        if not valido:
            return ResultadoTesteConexaoDTO(sucesso=False, mensagem=msg, tempo_ms=0.0)

        return self._repo.testar_conexao_socket(config.servidor, config.porta, config.timeout)

