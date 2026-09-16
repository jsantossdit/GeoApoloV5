"""
Cliente HTTP para comunicação com a API Alvo (https://alvo.rccbrasil.org.br/api).
Substitui a lógica legada com tokens hardcoded e gravações inseguras em c:\\temp.
"""

import json
import logging
import os
import tempfile
from typing import Dict, Any, Tuple, Optional
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)


class AlvoAPIClient:
    """
    Cliente REST puro para o Alvo.
    Utiliza urllib da biblioteca padrão para evitar dependências externas obrigatórias.
    """

    def __init__(self, base_url: str = "https://alvo.rccbrasil.org.br/api"):
        self.base_url = base_url.rstrip("/")
        self.token: Optional[str] = None

    def _salvar_dump_debug(self, nome_arquivo: str, conteudo: str):
        """Salva logs de depuração de forma segura no diretório temporário do sistema operacional."""
        try:
            caminho = os.path.join(tempfile.gettempdir(), nome_arquivo)
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(conteudo)
            logger.debug("Dump salvo em: %s", caminho)
        except Exception as exc:
            logger.warning("Falha ao salvar dump de debug: %s", exc)

    def autenticar(self, usuario: str, senha_plana: str) -> bool:
        """
        Realiza login na API Alvo e obtém o token Bearer para a sessão.
        """
        url = f"{self.base_url}/auth/login"
        payload = json.dumps({"usuario": usuario, "senha": senha_plana}).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status == 200:
                    dados = json.loads(resp.read().decode("utf-8"))
                    self.token = dados.get("token") or dados.get("Token")
                    logger.info("Autenticação com a API Alvo realizada com sucesso.")
                    return bool(self.token)
        except urllib.error.HTTPError as exc:
            logger.error("Erro HTTP ao autenticar no Alvo: %d - %s", exc.code, exc.read().decode("utf-8", errors="ignore"))
        except Exception as exc:
            logger.exception("Falha de conexão ao autenticar no Alvo: %s", exc)

        return False

    def enviar_entidade(self, payload_dict: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Envia a entidade criada ou atualizada para a API do Alvo.
        """
        url = f"{self.base_url}/entidades"
        payload_str = json.dumps(payload_dict, indent=2, ensure_ascii=False)
        self._salvar_dump_debug("dump_entidade_enviada.json", payload_str)

        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        req = urllib.request.Request(
            url,
            data=payload_str.encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                resposta_texto = resp.read().decode("utf-8")
                return True, resposta_texto
        except urllib.error.HTTPError as exc:
            erro_texto = exc.read().decode("utf-8", errors="ignore")
            self._salvar_dump_debug("dump_erro_export.json", erro_texto)
            return False, f"Erro HTTP {exc.code}: {erro_texto}"
        except Exception as exc:
            return False, f"Falha de conexão: {str(exc)}"
