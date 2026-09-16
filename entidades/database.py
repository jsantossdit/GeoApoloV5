"""
Gerenciador de Conexão de Banco de Dados com suporte a SQL Server e pyodbc.
Integra com o ConfigManager do GeoAlvo (settings.json + keyring).
"""

import logging
import pyodbc
from config_banco import ConfigManager

logger = logging.getLogger(__name__)


def obter_conexao_banco():
    """
    Carrega as configurações salvas em settings.json e credenciais do keyring
    e retorna uma conexão ativa pyodbc para o SQL Server.
    """
    config_mgr = ConfigManager()
    settings = config_mgr.load_settings()
    credentials = config_mgr.get_db_credentials()

    endereco = settings.get("endereco", "localhost")
    porta = settings.get("porta", "1433")
    usuario = credentials.get("user", "")
    senha = credentials.get("password", "")

    # Monta string de conexão para ODBC Driver 17/18 for SQL Server
    server_str = f"{endereco},{porta}" if porta else endereco

    drivers_disponiveis = pyodbc.drivers()
    driver_escolhido = "ODBC Driver 17 for SQL Server"
    if "ODBC Driver 18 for SQL Server" in drivers_disponiveis:
        driver_escolhido = "ODBC Driver 18 for SQL Server"
    elif "ODBC Driver 17 for SQL Server" in drivers_disponiveis:
        driver_escolhido = "ODBC Driver 17 for SQL Server"
    elif "SQL Server" in drivers_disponiveis:
        driver_escolhido = "SQL Server"

    conn_str = (
        f"DRIVER={{{driver_escolhido}}};"
        f"SERVER={server_str};"
        f"DATABASE=GeoApolo;"
        f"UID={usuario};"
        f"PWD={senha};"
        "TrustServerCertificate=yes;"
    )

    try:
        conn = pyodbc.connect(conn_str, timeout=10)
        return conn
    except Exception as exc:
        logger.error("Falha ao conectar ao banco de dados: %s", exc)
        raise
