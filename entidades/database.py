"""
Gerenciador de Conexão de Banco de Dados com suporte a SQL Server e pyodbc.
Integra com o ConfigManager do GeoAlvo (settings.json + keyring).
"""

import os
import sys
import logging
from pathlib import Path
import pyodbc

# Garante que a raiz do projeto esteja no sys.path para importar config_banco
_raiz_projeto = str(Path(__file__).resolve().parent.parent)
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

from config_banco import ConfigManager

logger = logging.getLogger(__name__)


_conexao_ativa = None


def testar_conexao(conn) -> bool:
    """Verifica de forma rápida e segura se a conexão pyodbc ainda está viva e funcional."""
    if conn is None:
        return False
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        return True
    except Exception:
        return False


def sanitizar_nome_servidor(endereco: str) -> str:
    """Higieniza o nome do servidor, removendo barras extras ou formatação inválida."""
    if not endereco:
        return ""
    s = endereco.strip()
    while s.startswith("\\") or s.startswith("/"):
        s = s[1:]
    s = s.replace("/", "\\")
    while "\\\\" in s:
        s = s.replace("\\\\", "\\")
    return s.strip()


def is_base_local(endereco: str) -> bool:
    """
    Verifica se o endereço do servidor aponta para uma instância local do SQL Server.
    Considera localhost, 127.0.0.1, ., (local), nome do computador local e instâncias locais nomeadas.
    """
    if not endereco:
        return True
    end = sanitizar_nome_servidor(endereco).lower()
    comp_name = os.environ.get("COMPUTERNAME", "").lower()

    if end in ("localhost", "127.0.0.1", ".", "(local)"):
        return True
    if comp_name and (end == comp_name or end.startswith(f"{comp_name}\\")):
        return True

    return (
        end.startswith("localhost\\")
        or end.startswith("127.0.0.1\\")
        or end.startswith(".\\")
        or end.startswith("(local)\\")
        or end.startswith("localhost,")
        or end.startswith("127.0.0.1,")
        or end.startswith(".,")
    )


def obter_conexao_banco(forcar_nova: bool = False):
    """
    Carrega as configurações salvas em settings.json e credenciais do keyring
    e retorna uma conexão ativa pyodbc para o SQL Server.
    Se forcar_nova for False e já houver uma conexão válida ativa, reutiliza-a.
    """
    global _conexao_ativa

    if not forcar_nova and _conexao_ativa is not None:
        if testar_conexao(_conexao_ativa):
            return _conexao_ativa

    config_mgr = ConfigManager()
    settings = config_mgr.load_settings()
    credentials = config_mgr.get_db_credentials()

    endereco = sanitizar_nome_servidor(settings.get("endereco", "localhost"))
    porta = str(settings.get("porta", "") or "").strip()
    banco = settings.get("banco", "RCC").strip()
    usuario = credentials.get("user", "")
    senha = credentials.get("password", "")

    # Monta string de conexão: para instâncias nomeadas (ex: SDIT-02\SDITBD)
    # não devemos concatenar a porta 1433 padrão, pois ela força TCP direto e quebra Memória Compartilhada
    if porta and porta != "1433" and "," not in endereco:
        server_str = f"{endereco},{porta}"
    else:
        server_str = endereco

    drivers_disponiveis = pyodbc.drivers()
    driver_escolhido = "ODBC Driver 17 for SQL Server"
    if "ODBC Driver 18 for SQL Server" in drivers_disponiveis:
        driver_escolhido = "ODBC Driver 18 for SQL Server"
    elif "ODBC Driver 17 for SQL Server" in drivers_disponiveis:
        driver_escolhido = "ODBC Driver 17 for SQL Server"
    elif "SQL Server" in drivers_disponiveis:
        driver_escolhido = "SQL Server"

    # Configuração de timeout de conexão: respeita a configuração do usuário
    # e garante timeout ampliado (mínimo 60s) para bases locais.
    try:
        timeout_seg = int(settings.get("timeout", 60) or 60)
    except (ValueError, TypeError):
        timeout_seg = 60

    if is_base_local(endereco):
        if timeout_seg < 60:
            timeout_seg = 60
    elif timeout_seg < 15:
        timeout_seg = 15

    def _conectar(srv_target):
        c_str = (
            f"DRIVER={{{driver_escolhido}}};"
            f"SERVER={srv_target};"
            f"DATABASE={banco};"
            f"UID={usuario};"
            f"PWD={senha};"
            f"Connection Timeout={timeout_seg};"
            "TrustServerCertificate=yes;"
        )
        return pyodbc.connect(c_str, timeout=timeout_seg)

    try:
        conn = _conectar(server_str)
    except Exception as exc:
        conn = None
        # Fallback inteligente para base local com instância nomeada (ex: SDIT-02\SDITBD)
        if is_base_local(endereco) and "\\" in endereco:
            instancia = endereco.split("\\", 1)[1]
            for fallback_srv in (f"localhost\\{instancia}", f".\\{instancia}"):
                if fallback_srv.lower() != server_str.lower():
                    try:
                        logger.info("Tentando conexão de contingência local com '%s'...", fallback_srv)
                        conn = _conectar(fallback_srv)
                        logger.info("Conexão de contingência com '%s' estabelecida com sucesso!", fallback_srv)
                        break
                    except Exception:
                        pass
        if conn is None:
            _conexao_ativa = None
            logger.error(
                "Falha ao conectar ao banco de dados (%s em %s, timeout=%ss): %s",
                banco, server_str, timeout_seg, exc
            )
            raise exc

    # Desativa o timeout de execução de comandos (query timeout) para queries analíticas pesadas
    conn.timeout = 0
    _conexao_ativa = conn
    logger.info("Conexão com o banco de dados (%s) estabelecida com sucesso.", banco)
    return conn


def reconectar_banco():
    """Força uma reconexão com o banco de dados principal."""
    logger.info("Executando rotina de reconexão ao banco de dados...")
    return obter_conexao_banco(forcar_nova=True)


def obter_conexao_savic(timeout_seg: int = 15):
    """
    Carrega as configurações salvas do SAVIC e retorna uma conexão ativa pymysql.
    """
    import pymysql
    config_mgr = ConfigManager()
    settings = config_mgr.load_savic_settings()
    credentials = config_mgr.get_savic_credentials()

    host = settings.get("host", "191.252.53.94")
    try:
        port = int(settings.get("port", 3306) or 3306)
    except ValueError:
        port = 3306
    db = settings.get("database", "rccbrasilsavic")
    user = credentials.get("user", "rccbrasilsavic")
    passwd = credentials.get("password", "b2J4earCJuNcM7")

    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=passwd,
            database=db,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=timeout_seg
        )
        return conn
    except Exception as exc:
        logger.error("Falha ao conectar ao banco SAVIC (MySQL em %s:%s, db=%s): %s", host, port, db, exc)
        raise


def obter_conexao_aplicativo_rcc(timeout_seg: int = 15):
    """
    Restaura em segundo plano as configurações salvas do Aplicativo RCC (MySQL)
    e retorna uma conexão ativa pymysql, tratando os erros padrões com mensagens claras.
    """
    import pymysql
    config_mgr = ConfigManager()
    settings = config_mgr.load_app_rcc_settings()
    credentials = config_mgr.get_app_rcc_credentials()

    host = str(settings.get("host") or "").strip()
    try:
        port = int(settings.get("port", 3306) or 3306)
    except ValueError:
        port = 3306
    db = str(settings.get("database") or "").strip()
    user = str(credentials.get("user") or "").strip()
    passwd = credentials.get("password") or ""

    if not host or not db or not user:
        raise ValueError(
            "Configurações do Banco de Dados do Aplicativo RCC não preenchidas ou incompletas.\n\n"
            "Por favor, acesse o menu principal: Configurações > Banco de Dados > Banco Dados Aplicativo RCC "
            "e configure o Servidor, Porta, Banco e Usuário de conexão."
        )

    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=passwd,
            database=db,
            charset="utf8mb4",
            connect_timeout=timeout_seg
        )
        return conn
    except pymysql.err.OperationalError as exc:
        code, msg = exc.args if len(exc.args) == 2 else (0, str(exc))
        if code == 1045:
            erro_msg = (
                f"Acesso Negado ao Banco de Dados do Aplicativo RCC!\n\n"
                f"O usuário '{user}' ou a senha informada não foram autorizados pelo servidor MySQL em {host}:{port}.\n"
                f"Verifique as credenciais no menu Configurações > Banco de Dados > Banco Dados Aplicativo RCC.\n"
                f"Código do erro: {code} ({msg})"
            )
        elif code in (2002, 2003):
            erro_msg = (
                f"Não foi possível conectar ao servidor MySQL do Aplicativo RCC!\n\n"
                f"Servidor inacessível no endereço {host}:{port}.\n"
                f"Verifique se o servidor MySQL está ligado, se o IP e a porta estão corretos ou se há bloqueio de firewall.\n"
                f"Código do erro: {code} ({msg})"
            )
        elif code == 1049:
            erro_msg = (
                f"Banco de Dados não encontrado no Aplicativo RCC!\n\n"
                f"O banco de dados '{db}' não existe no servidor MySQL ({host}:{port}).\n"
                f"Verifique o nome do catálogo no menu Configurações > Banco de Dados.\n"
                f"Código do erro: {code} ({msg})"
            )
        else:
            erro_msg = (
                f"Falha de conexão com o banco do Aplicativo RCC ({host}:{port}, Banco: {db}):\n\n"
                f"{msg} (Código {code})"
            )
        logger.error(erro_msg)
        raise ConnectionError(erro_msg) from exc
    except Exception as exc:
        erro_msg = (
            f"Erro inesperado ao conectar ao banco do Aplicativo RCC ({host}:{port}, Banco: {db}):\n\n"
            f"{str(exc)}"
        )
        logger.error(erro_msg)
        raise ConnectionError(erro_msg) from exc
