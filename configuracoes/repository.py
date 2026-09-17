"""
Repositório de Dados para Parâmetros do Sistema e E-mails.
Preserva as otimizações SQL Server e hints WITH (NOLOCK).
"""

import os
import json
import socket
import time
import logging
from typing import Dict, Any, List, Optional
from entidades.database import obter_conexao_banco
from .models import ConfiguracaoBancoDTO, ResultadoTesteConexaoDTO


logger = logging.getLogger(__name__)


class ConfiguracoesRepository:
    """Repositório de persistência para as configurações gerais e corporativas."""

    def __init__(self, connection=None):
        self._conn = connection

    def _get_cursor(self):
        if self._conn is None:
            self._conn = obter_conexao_banco()
        return self._conn.cursor()

    def obter_configuracoes(self, empresa_codigo: str) -> Dict[str, Any]:
        cursor = self._get_cursor()
        sql = """
            SELECT TOP (1)
                ISNULL(caminhobackupsistema, '') AS caminhobackupsistema,
                ISNULL(instalacaolocal, '') AS instalacaolocal,
                ISNULL(localnovasversoes, '') AS localnovasversoes,
                ISNULL(localinstaladorversoes, '') AS localinstaladorversoes,
                ISNULL(caminhoarquivoconvenio, '') AS caminhoarquivoconvenio,
                ISNULL(caminhoinventario, '') AS caminhoinventario,
                ISNULL(caminhodocti, '') AS caminhodocti,
                ISNULL(caminhodocmissaopopular, '') AS caminhodocmissaopopular,
                ISNULL(caminhobasealvoloja, '') AS caminhobasealvoloja,
                ISNULL(entcategparceira, '') AS entcategparceira,
                ISNULL(entcod_consumidorfinal, '') AS entcod_consumidorfinal,
                ISNULL(origcodestr, '') AS origcodestr,
                ISNULL(motocorcodestr, '') AS motocorcodestr,
                ISNULL(integra_entidades_apolo, 'Integra') AS integra_entidades_apolo,
                ISNULL(grupohardware, '') AS grupohardware,
                ISNULL(gruposoftware, '') AS gruposoftware,
                ISNULL(tempomaximomissao, '30') AS tempomaximomissao,
                ISNULL(status_fechapic, '') AS status_fechapic
            FROM USER_geoapolo_configuracoes WITH (NOLOCK)
            WHERE empcod = ?
        """
        cursor.execute(sql, [empresa_codigo])
        row = cursor.fetchone()
        if not row:
            return {}
        cols = [c[0] for c in cursor.description]
        return dict(zip(cols, row))

    def salvar_configuracoes(self, dados: Dict[str, Any], empresa_codigo: str) -> bool:
        cursor = self._get_cursor()
        # Verifica se registro existe
        cursor.execute("SELECT COUNT(*) FROM USER_geoapolo_configuracoes WITH (NOLOCK) WHERE empcod = ?", [empresa_codigo])
        existe = cursor.fetchone()[0] > 0

        if existe:
            sql = """
                UPDATE USER_geoapolo_configuracoes SET
                    caminhobackupsistema = ?,
                    instalacaolocal = ?,
                    localnovasversoes = ?,
                    localinstaladorversoes = ?,
                    caminhoarquivoconvenio = ?,
                    caminhoinventario = ?,
                    caminhodocti = ?,
                    caminhodocmissaopopular = ?,
                    caminhobasealvoloja = ?,
                    entcategparceira = ?,
                    entcod_consumidorfinal = ?,
                    origcodestr = ?,
                    motocorcodestr = ?,
                    integra_entidades_apolo = ?,
                    grupohardware = ?,
                    gruposoftware = ?,
                    tempomaximomissao = ?,
                    status_fechapic = ?
                WHERE empcod = ?
            """
            params = [
                dados.get("caminhobackupsistema", ""),
                dados.get("instalacaolocal", ""),
                dados.get("localnovasversoes", ""),
                dados.get("localinstaladorversoes", ""),
                dados.get("caminhoarquivoconvenio", ""),
                dados.get("caminhoinventario", ""),
                dados.get("caminhodocti", ""),
                dados.get("caminhodocmissaopopular", ""),
                dados.get("caminhobasealvoloja", ""),
                dados.get("entcategparceira", ""),
                dados.get("entcod_consumidorfinal", ""),
                dados.get("origcodestr", ""),
                dados.get("motocorcodestr", ""),
                dados.get("integra_entidades_apolo", "Integra"),
                dados.get("grupohardware", ""),
                dados.get("gruposoftware", ""),
                dados.get("tempomaximomissao", "30"),
                dados.get("status_fechapic", ""),
                empresa_codigo,
            ]
        else:
            sql = """
                INSERT INTO USER_geoapolo_configuracoes (
                    empcod, caminhobackupsistema, instalacaolocal, localnovasversoes,
                    localinstaladorversoes, caminhoarquivoconvenio, caminhoinventario,
                    caminhodocti, caminhodocmissaopopular, caminhobasealvoloja,
                    entcategparceira, entcod_consumidorfinal, origcodestr,
                    motocorcodestr, integra_entidades_apolo, grupohardware,
                    gruposoftware, tempomaximomissao, status_fechapic
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = [
                empresa_codigo,
                dados.get("caminhobackupsistema", ""),
                dados.get("instalacaolocal", ""),
                dados.get("localnovasversoes", ""),
                dados.get("localinstaladorversoes", ""),
                dados.get("caminhoarquivoconvenio", ""),
                dados.get("caminhoinventario", ""),
                dados.get("caminhodocti", ""),
                dados.get("caminhodocmissaopopular", ""),
                dados.get("caminhobasealvoloja", ""),
                dados.get("entcategparceira", ""),
                dados.get("entcod_consumidorfinal", ""),
                dados.get("origcodestr", ""),
                dados.get("motocorcodestr", ""),
                dados.get("integra_entidades_apolo", "Integra"),
                dados.get("grupohardware", ""),
                dados.get("gruposoftware", ""),
                dados.get("tempomaximomissao", "30"),
                dados.get("status_fechapic", ""),
            ]

        cursor.execute(sql, params)
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def listar_servidores_email(self) -> List[Dict[str, Any]]:
        cursor = self._get_cursor()
        sql = """
            SELECT
                codigo_servidor,
                protocolo,
                servidor_envio,
                porta_envio,
                servidor_recebimento,
                porta_recebimento
            FROM USER_geoapolo_mail_server WITH (NOLOCK)
            ORDER BY codigo_servidor ASC
        """
        cursor.execute(sql)
        cols = [c[0] for c in cursor.description]
        registros = []
        for row in cursor.fetchall():
            registros.append(dict(zip(cols, row)))
        return registros

    def salvar_servidor_email(self, dados: Dict[str, Any], modo_inclusao: bool = True) -> bool:
        cursor = self._get_cursor()
        if modo_inclusao:
            sql = """
                INSERT INTO USER_geoapolo_mail_server (
                    codigo_servidor, protocolo, servidor_envio, porta_envio,
                    servidor_recebimento, porta_recebimento
                ) VALUES (?, ?, ?, ?, ?, ?)
            """
            params = [
                dados.get("codigo_servidor", ""),
                dados.get("protocolo", "SMTP"),
                dados.get("servidor_envio", "smtp.office365.com"),
                int(dados.get("porta_envio", 587) or 587),
                dados.get("servidor_recebimento", ""),
                int(dados.get("porta_recebimento", 993) or 993),
            ]
        else:
            sql = """
                UPDATE USER_geoapolo_mail_server SET
                    protocolo = ?, servidor_envio = ?, porta_envio = ?,
                    servidor_recebimento = ?, porta_recebimento = ?
                WHERE codigo_servidor = ?
            """
            params = [
                dados.get("protocolo", "SMTP"),
                dados.get("servidor_envio", "smtp.office365.com"),
                int(dados.get("porta_envio", 587) or 587),
                dados.get("servidor_recebimento", ""),
                int(dados.get("porta_recebimento", 993) or 993),
                dados.get("codigo_servidor", ""),
            ]

        cursor.execute(sql, params)
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def excluir_servidor_email(self, codigo: str) -> bool:
        cursor = self._get_cursor()
        cursor.execute("DELETE FROM USER_geoapolo_mail_server WHERE codigo_servidor = ?", [codigo])
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def carregar_config_banco(self, arquivo_json: str = "") -> ConfiguracaoBancoDTO:
        """Carrega parâmetros de conexão do banco de dados salvos localmente."""
        path = arquivo_json or os.path.join(os.path.expanduser("~"), ".geoapolo_db.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                return ConfiguracaoBancoDTO(
                    tipo_banco=dados.get("tipo_banco", "MSSQL"),
                    servidor=dados.get("servidor", "localhost"),
                    porta=int(dados.get("porta", 1433)),
                    banco=dados.get("banco", "Apolo"),
                    usuario=dados.get("usuario", "sa"),
                    senha=dados.get("senha", ""),
                    timeout=int(dados.get("timeout", 15)),
                    protocolo=dados.get("protocolo", "TCPIP"),
                    driver=dados.get("driver", "ODBC Driver 17 for SQL Server"),
                )
            except Exception as e:
                logger.warning("Falha ao ler arquivo de configuracao de banco: %s", e)
        return ConfiguracaoBancoDTO()

    def salvar_config_banco(self, config: ConfiguracaoBancoDTO, arquivo_json: str = "") -> bool:
        """Persiste parâmetros de conexão do banco de dados localmente."""
        path = arquivo_json or os.path.join(os.path.expanduser("~"), ".geoapolo_db.json")
        try:
            dados = {
                "tipo_banco": config.tipo_banco,
                "servidor": config.servidor,
                "porta": config.porta,
                "banco": config.banco,
                "usuario": config.usuario,
                "senha": config.senha,
                "timeout": config.timeout,
                "protocolo": config.protocolo,
                "driver": config.driver,
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=2)
            return True
        except Exception as e:
            logger.exception("Erro ao salvar arquivo de configuracao de banco: %s", e)
            return False

    def testar_conexao_socket(self, servidor: str, porta: int, timeout: int = 5) -> ResultadoTesteConexaoDTO:
        """Testa a conectividade via socket TCP com medição de latência em milissegundos."""
        inicio = time.time()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect((servidor, porta))
            duracao_ms = round((time.time() - inicio) * 1000, 2)
            return ResultadoTesteConexaoDTO(
                sucesso=True,
                mensagem=f"Conexão TCP com {servidor}:{porta} estabelecida com sucesso ({duracao_ms} ms).",
                tempo_ms=duracao_ms,
            )
        except Exception as e:
            duracao_ms = round((time.time() - inicio) * 1000, 2)
            return ResultadoTesteConexaoDTO(
                sucesso=False,
                mensagem=f"Falha ao conectar em {servidor}:{porta}: {e}",
                tempo_ms=duracao_ms,
            )
