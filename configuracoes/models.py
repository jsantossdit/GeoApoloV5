"""
Modelos e DTOs para Configurações Gerais e Parâmetros do Sistema.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ConfiguracaoSistemaDTO:
    empresa_codigo: str
    caminho_backup: str = ""
    instalacao_local: str = ""
    local_novas_versoes: str = ""
    local_instalador_versoes: str = ""
    caminho_convenio: str = ""
    caminho_inventario: str = ""
    caminho_doc_ti: str = ""
    caminho_doc_missao: str = ""
    caminho_base_alvo_loja: str = ""
    entidade_parceira: str = ""
    consumidor_final: str = ""
    origem_padrao: str = ""
    motivo_ocorrencia: str = ""
    integra_entidades_apolo: str = "Integra"
    grupo_hardware: str = ""
    grupo_software: str = ""
    tempo_maximo_missao: str = "30"
    status_fecha_pic: str = ""


@dataclass
class ServidorEmailDTO:
    codigo_servidor: str
    protocolo: str = "SMTP"
    servidor_envio: str = "smtp.office365.com"
    porta_envio: int = 587
    servidor_recebimento: str = "outlook.office365.com"
    porta_recebimento: int = 993


@dataclass
class ContaEmailDTO:
    codigo_conta: str
    conta_email: str
    senha: str = ""
    codigo_servidor: str = ""


@dataclass
class ResultadoOperacao:
    sucesso: bool
    mensagem: str
    codigo: Optional[str] = None
