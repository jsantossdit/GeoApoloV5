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
    Cliente REST puro para o Alvo (https://alvo.rccbrasil.org.br/api).
    Compatível com unt_AlvoEntidade.pas e unt_alvo_api_client.pas do Delphi.
    Utiliza urllib da biblioteca padrão para evitar dependências externas obrigatórias.
    """

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        if base_url is None or token is None:
            try:
                from configuracoes.alvo_api_config import carregar_configuracao_alvo
                cfg = carregar_configuracao_alvo()
                if base_url is None:
                    base_url = cfg.base_url or "https://alvo.rccbrasil.org.br/api"
                if token is None and cfg.token:
                    token = cfg.token
            except Exception:
                if base_url is None:
                    base_url = "https://alvo.rccbrasil.org.br/api"
        self.base_url = (base_url or "https://alvo.rccbrasil.org.br/api").rstrip("/")
        self.token: Optional[str] = token

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
        Realiza login na API Alvo e obtém o token JWT / Riosoft-Token para a sessão.
        Equivalente a TAlvoAPI.Login em unt_AlvoEntidade.pas.
        """
        url = f"{self.base_url}/Auth/Login"
        payload = json.dumps({"usuario": usuario, "senha": senha_plana}).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                if resp.status in (200, 201):
                    dados = json.loads(resp.read().decode("utf-8"))
                    self.token = dados.get("token") or dados.get("Token") or dados.get("jwt")
                    logger.info("Autenticação com a API Alvo realizada com sucesso.")
                    return bool(self.token)
        except urllib.error.HTTPError as exc:
            erro_texto = exc.read().decode("utf-8", errors="ignore")
            logger.error("Erro HTTP ao autenticar no Alvo: %d - %s", exc.code, erro_texto)
            self._salvar_dump_debug("dump_erro_login.json", erro_texto)
            self.token = None
        except Exception as exc:
            logger.exception("Falha de conexão ao autenticar no Alvo: %s", exc)
            self.token = None

        return False

    def obter_token_valido(self) -> Optional[str]:
        """Retorna o token atual caso exista."""
        return self.token

    def garantir_autenticacao(self, usuario: str = "", senha_plana: str = "") -> bool:
        """Garante que haja um token válido obtido, autenticando se necessário."""
        if self.token:
            return True
        if usuario and senha_plana:
            return self.autenticar(usuario, senha_plana)
        return False

    def testar_comunicacao(self) -> Tuple[bool, str]:
        """Testa conectividade e aceitação do token configurado na API Alvo."""
        from configuracoes.alvo_api_config import AlvoAPIConfig, testar_comunicacao_alvo
        cfg = AlvoAPIConfig(token=self.token or "", base_url=self.base_url)
        sucesso, msg, _ = testar_comunicacao_alvo(cfg)
        return sucesso, msg

    def inserir_alterar_entidade(
        self, payload_dict: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Envia a entidade para o endpoint oficial Entidade/InserirAlterarEntidade.
        Equivalente a TAlvoAPI.InserirAlterarEntidade em unt_AlvoEntidade.pas.
        """
        url = f"{self.base_url}/Entidade/InserirAlterarEntidade"
        payload_str = json.dumps(payload_dict, indent=2, ensure_ascii=False)
        self._salvar_dump_debug("dump_entidade_enviada.json", payload_str)

        headers = {"Content-Type": "application/json"}
        if self.token:
            # Header proprietário Riosoft-Token utilizado pelo Alvo no Delphi + Authorization padrão
            headers["Riosoft-Token"] = self.token
            headers["Authorization"] = f"Bearer {self.token}"

        req = urllib.request.Request(
            url,
            data=payload_str.encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                resposta_texto = resp.read().decode("utf-8")
                dados_json: Optional[Dict[str, Any]] = None
                try:
                    dados_json = json.loads(resposta_texto)
                except Exception:
                    dados_json = None
                return True, resposta_texto, dados_json
        except urllib.error.HTTPError as exc:
            erro_texto = exc.read().decode("utf-8", errors="ignore")
            self._salvar_dump_debug("dump_erro_export.json", erro_texto)
            dados_erro: Optional[Dict[str, Any]] = None
            try:
                dados_erro = json.loads(erro_texto)
            except Exception:
                dados_erro = None
            return False, f"Erro HTTP {exc.code}: {erro_texto}", dados_erro
        except Exception as exc:
            return False, f"Falha de conexão: {str(exc)}", None

    def enviar_entidade(self, payload_dict: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Método de compatibilidade para envio de entidade.
        Retorna (sucesso, mensagem_ou_conteudo).
        """
        sucesso, msg, _ = self.inserir_alterar_entidade(payload_dict)
        return sucesso, msg

    @staticmethod
    def extrair_entcod_mensagem_ja_existe(texto: str) -> Optional[str]:
        """
        Extrai o código da entidade quando a API Alvo informa que o CPF/CNPJ já existe.
        Exemplo: 'Atenção: O CPF 00000000000 já existe na Entidade 0017325.' -> '0017325'
        """
        if not texto:
            return None
        import re
        # Padrão mais direto: "já existe na Entidade XXXXX"
        match = re.search(r'já\s+(?:existe|cadastrad[oa])\s+na\s+Entidade\s+([0-9]{1,7})', texto, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        # Padrão: menção a "Entidade XXXXX" com indicativo de que já existe
        if re.search(r'(?:já\s+existe|duplicad[oa]|já\s+cadastrad[oa])', texto, re.IGNORECASE):
            m2 = re.search(r'Entidade\s+([0-9]{1,7})', texto, re.IGNORECASE)
            if m2:
                return m2.group(1).strip()
        return None

    @staticmethod
    def extrair_entcod_resposta(
        resposta_texto: str, dados_json: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Extrai o código gerado ou atualizado no Alvo (entcod / Codigo / id)
        a partir do objeto JSON ou string de retorno da API.
        Também captura o código caso a API retorne mensagem de documento já existente.
        """
        if dados_json and isinstance(dados_json, dict):
            for chave in ("entcod", "EntCod", "codigo", "Codigo", "id", "Id"):
                val = dados_json.get(chave)
                if val:
                    return str(val).strip()
            ent = dados_json.get("Entidade") or dados_json.get("entidade")
            if isinstance(ent, dict):
                for chave in ("entcod", "EntCod", "codigo", "Codigo", "id", "Id"):
                    val = ent.get(chave)
                    if val:
                        return str(val).strip()
            for chave_msg in ("Mensagem", "mensagem", "Message", "message", "Erro", "erro", "error"):
                msg = dados_json.get(chave_msg)
                if msg and isinstance(msg, str):
                    ent_exist = AlvoAPIClient.extrair_entcod_mensagem_ja_existe(msg)
                    if ent_exist:
                        return ent_exist

        if resposta_texto:
            ent_exist = AlvoAPIClient.extrair_entcod_mensagem_ja_existe(resposta_texto)
            if ent_exist:
                return ent_exist

        # Fallback de busca textual caso retorne número ou texto direto
        import re
        match = re.search(r'"(?:entcod|codigo|id)"\s*:\s*"?(\d+)"?', resposta_texto or "", re.IGNORECASE)
        if match:
            return match.group(1)
        if resposta_texto and resposta_texto.strip().isdigit():
            return resposta_texto.strip()
        return None

