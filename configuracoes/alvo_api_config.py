"""
Módulo de Configuração e Gerenciamento do Token da API Alvo (Riosoft).
Suporta armazenamento persistente em AppData (settings.json / alvo_api_config.json)
e fallback local, com validação de período de vigência (data inicial e final).
"""

import json
import logging
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

ARQUIVO_CONFIG_NOME = "alvo_api_config.json"
APP_DIR_NOME = "GeoApoloV5"


@dataclass
class AlvoAPIConfig:
    """Modelo de dados para parametrização do Web Service API Alvo."""
    token: str = ""
    data_inicial: str = ""  # Formato DD/MM/AAAA
    data_final: str = ""    # Formato DD/MM/AAAA
    base_url: str = "https://alvo.rccbrasil.org.br/api"
    timeout: int = 45
    ativo: bool = True
    ambiente: str = "Produção"
    usuario_padrao: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, dados: Dict[str, Any]) -> "AlvoAPIConfig":
        if not dados or not isinstance(dados, dict):
            return cls()
        return cls(
            token=str(dados.get("token") or "").strip(),
            data_inicial=str(dados.get("data_inicial") or "").strip(),
            data_final=str(dados.get("data_final") or "").strip(),
            base_url=str(dados.get("base_url") or "https://alvo.rccbrasil.org.br/api").strip(),
            timeout=int(dados.get("timeout") or 45),
            ativo=bool(dados.get("ativo", True)),
            ambiente=str(dados.get("ambiente") or "Produção").strip(),
            usuario_padrao=str(dados.get("usuario_padrao") or "").strip(),
        )


def _obter_diretorio_appdata() -> Path:
    """Retorna o diretório em AppData/Roaming ou equivalente do usuário."""
    if os.name == "nt" and "APPDATA" in os.environ:
        caminho = Path(os.environ["APPDATA"]) / APP_DIR_NOME
    else:
        caminho = Path.home() / f".{APP_DIR_NOME}"
    caminho.mkdir(parents=True, exist_ok=True)
    return caminho


def _obter_caminhos_arquivo_config() -> list[Path]:
    """Retorna lista de caminhos possíveis para carregar e salvar a configuração."""
    caminhos = []
    try:
        caminhos.append(_obter_diretorio_appdata() / ARQUIVO_CONFIG_NOME)
    except Exception:
        pass

    # Raiz do projeto como fallback/paralelo
    raiz_projeto = Path(__file__).resolve().parent.parent
    caminhos.append(raiz_projeto / ARQUIVO_CONFIG_NOME)
    return caminhos


def parse_data_br(val: Any) -> Optional[date]:
    """Converte string de data no formato DD/MM/AAAA para objeto date."""
    if not val:
        return None
    s = str(val).strip()
    match = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if match:
        d, m, y = map(int, match.groups())
        try:
            return date(y, m, d)
        except ValueError:
            return None
    # Suporte a ISO caso esteja salvo assim
    match_iso = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if match_iso:
        y, m, d = map(int, match_iso.groups())
        try:
            return date(y, m, d)
        except ValueError:
            return None
    return None


def validar_status_token(config: AlvoAPIConfig) -> Tuple[str, str, bool]:
    """
    Avalia a vigência do token configurado contra a data atual do sistema.
    Retorna:
      (status_codigo, mensagem_formatada, is_valido)
      status_codigo: 'ATIVO', 'EXPIRADO', 'FUTURO', 'SEM_TOKEN', 'SEM_DATAS'
    """
    token = (config.token or "").strip()
    if not token:
        return "SEM_TOKEN", "Nenhum token configurado.", False

    if not config.ativo:
        return "DESATIVADO", "Integração API Alvo desativada nas configurações.", False

    dt_ini = parse_data_br(config.data_inicial)
    dt_fim = parse_data_br(config.data_final)
    hoje = date.today()

    if not dt_ini and not dt_fim:
        return "ATIVO_SEM_DATAS", "Token configurado (sem data limite de validade).", True

    if dt_ini and hoje < dt_ini:
        dias_para_iniciar = (dt_ini - hoje).days
        return "FUTURO", f"Token ainda não vigente. Inicia em {dt_ini.strftime('%d/%m/%Y')} (em {dias_para_iniciar} dia(s)).", False

    if dt_fim:
        if hoje > dt_fim:
            dias_expirado = (hoje - dt_fim).days
            return "EXPIRADO", f"Token expirado em {dt_fim.strftime('%d/%m/%Y')} (há {dias_expirado} dia(s)).", False
        else:
            dias_restantes = (dt_fim - hoje).days
            if dias_restantes <= 15:
                return "EXPIRANDO", f"Token ativo, mas expira em breve: restam {dias_restantes} dia(s) (até {dt_fim.strftime('%d/%m/%Y')}).", True
            return "ATIVO", f"Token válido e ativo até {dt_fim.strftime('%d/%m/%Y')} (restam {dias_restantes} dias).", True

    return "ATIVO", "Token ativo e vigente.", True


def carregar_configuracao_alvo() -> AlvoAPIConfig:
    """Carrega as configurações salvas da API Alvo a partir dos arquivos de configuração."""
    caminhos = _obter_caminhos_arquivo_config()
    for p in caminhos:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    if isinstance(dados, dict):
                        return AlvoAPIConfig.from_dict(dados)
            except Exception as exc:
                logger.warning("Falha ao ler configuração da API Alvo de %s: %s", p, exc)

    # Tenta ler do settings.json corporativo se existir
    try:
        from config_banco import ConfigManager
        cm = ConfigManager(APP_DIR_NOME)
        st = cm.load_settings()
        if "api_alvo" in st and isinstance(st["api_alvo"], dict):
            return AlvoAPIConfig.from_dict(st["api_alvo"])
    except Exception:
        pass

    return AlvoAPIConfig()


def salvar_configuracao_alvo(config: AlvoAPIConfig) -> bool:
    """Persiste a configuração da API Alvo em disco."""
    sucesso = False
    caminhos = _obter_caminhos_arquivo_config()
    for p in caminhos:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            sucesso = True
        except Exception as exc:
            logger.warning("Erro ao salvar configuração da API Alvo em %s: %s", p, exc)

    # Salva também no settings.json geral
    try:
        from config_banco import ConfigManager
        cm = ConfigManager(APP_DIR_NOME)
        st = cm.load_settings()
        st["api_alvo"] = config.to_dict()
        cm.save_settings(st)
        sucesso = True
    except Exception:
        pass

    return sucesso


def testar_comunicacao_alvo(config: AlvoAPIConfig) -> Tuple[bool, str, int]:
    """
    Executa teste de conectividade e validação do token contra a API Alvo.
    Retorna: (sucesso, mensagem, status_http)
    """
    if not config.token.strip():
        return False, "Token de integração não informado.", 0

    base_url = (config.base_url or "https://alvo.rccbrasil.org.br/api").rstrip("/")
    # Endpoints de verificação suportados no Alvo
    urls_teste = [
        f"{base_url}/Auth/VerificaToken",
        f"{base_url}/Entidade/ConsultarEntidadePorDocumento",
        f"{base_url}/Entidade",
    ]

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {config.token.strip()}",
        "Riosoft-Token": config.token.strip(),
        "User-Agent": "GeoAlvo-V5/Python",
    }

    ultima_mensagem = ""
    ultimo_status = 0

    for url in urls_teste:
        try:
            req = urllib.request.Request(url, headers=headers, method="GET")
            timeout = max(config.timeout or 15, 10)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = resp.status
                corpo = resp.read().decode("utf-8", errors="ignore")
                if status in (200, 201, 204):
                    return True, f"Conexão com a API Alvo realizada com sucesso!\nEndpoint: {url}\nStatus HTTP: {status}", status
        except urllib.error.HTTPError as exc:
            ultimo_status = exc.code
            corpo_erro = exc.read().decode("utf-8", errors="ignore")
            # 404 em endpoint específico não significa token inválido; pode significar que endpoint exige parâmetros
            if exc.code == 401 or exc.code == 403:
                return False, f"Token rejeitado pela API Alvo (HTTP {exc.code} - Não Autorizado):\n{corpo_erro or 'Credenciais inválidas ou token expirado.'}", exc.code
            elif exc.code in (400, 404, 405):
                # O servidor respondeu autenticado porém o método precisa de corpo ou parâmetros
                return True, f"Servidor Alvo contactado com sucesso (Token aceito pelo gateway, HTTP {exc.code}).", exc.code
            ultima_mensagem = f"Erro HTTP {exc.code}: {corpo_erro}"
        except urllib.error.URLError as exc:
            return False, f"Falha de rede/conexão ao contactar servidor Alvo:\n{exc.reason}", 0
        except Exception as exc:
            return False, f"Exceção durante teste de comunicação:\n{str(exc)}", 0

    return False, ultima_mensagem or "Falha ao validar token com o servidor Alvo.", ultimo_status
