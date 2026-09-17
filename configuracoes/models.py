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


@dataclass
class ConfiguracaoBancoDTO:
    """Configurações de Conexão com Banco de Dados e Parâmetros de Rede."""
    tipo_banco: str = "MSSQL"  # 'MSSQL', 'MySQL', 'SQLite'
    servidor: str = "localhost"
    porta: int = 1433
    banco: str = "Apolo"
    usuario: str = "sa"
    senha: str = ""
    timeout: int = 15
    protocolo: str = "TCPIP"
    driver: str = "ODBC Driver 17 for SQL Server"

    @property
    def connection_string(self) -> str:
        if self.tipo_banco.upper() == "MSSQL":
            port_str = f",{self.porta}" if self.porta and self.porta != 1433 else ""
            return (
                f"DRIVER={{{self.driver}}};SERVER={self.servidor}{port_str};"
                f"DATABASE={self.banco};UID={self.usuario};PWD={self.senha};"
                f"Connection Timeout={self.timeout};"
            )
        elif self.tipo_banco.upper() == "MYSQL":
            return (
                f"host={self.servidor};port={self.porta};db={self.banco};"
                f"user={self.usuario};passwd={self.senha}"
            )
        return f"sqlite:///{self.banco}"


@dataclass
class ResultadoTesteConexaoDTO:
    """Resultado de teste de conectividade com servidor de banco de dados."""
    sucesso: bool = False
    mensagem: str = ""
    tempo_ms: float = 0.0

