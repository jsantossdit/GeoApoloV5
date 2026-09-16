"""
Cliente de Integração com a API pública ViaCEP (consulta de endereços por CEP).
Utiliza a biblioteca padrão urllib.request e json (zero dependências externas).
"""

import json
import logging
import urllib.request
import urllib.error
from typing import Optional, Dict
from core.validators import limpar_formatacao

logger = logging.getLogger(__name__)


def consultar_cep(cep: str, timeout: int = 5) -> Optional[Dict[str, str]]:
    """
    Consulta o CEP na API ViaCEP.
    Retorna dicionário com os campos do endereço ou None caso não localize.
    """
    cep_limpo = limpar_formatacao(cep)
    if len(cep_limpo) != 8:
        logger.warning("CEP inválido para consulta: %s", cep)
        return None

    url = f"https://viacep.com.br/ws/{cep_limpo}/json/"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "GeoAlvo-Desktop/5.0"},
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                dados = json.loads(response.read().decode("utf-8"))
                if dados.get("erro"):
                    logger.info("CEP não encontrado na base do ViaCEP: %s", cep_limpo)
                    return None
                return {
                    "cep": dados.get("cep", ""),
                    "logradouro": dados.get("logradouro", ""),
                    "complemento": dados.get("complemento", ""),
                    "bairro": dados.get("bairro", ""),
                    "cidade": dados.get("localidade", ""),
                    "uf": dados.get("uf", ""),
                    "ibge": dados.get("ibge", ""),
                    "ddd": dados.get("ddd", ""),
                }
    except urllib.error.URLError as exc:
        logger.error("Falha ao consultar ViaCEP para o CEP %s: %s", cep_limpo, exc)
        return None
    except Exception as exc:
        logger.exception("Erro inesperado na consulta ao ViaCEP: %s", exc)
        return None


class ViaCEPClient:
    """Cliente orientado a objetos para consultas ao serviço ViaCEP."""

    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    def consultar_cep(self, cep: str) -> Optional[Dict[str, str]]:
        """Consulta endereço pelo CEP."""
        return consultar_cep(cep, timeout=self.timeout)

