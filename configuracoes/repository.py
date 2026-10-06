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

    def _garantir_colunas(self):
        """Garante que colunas necessárias existam na tabela USER_geoapolo_configuracoes."""
        try:
            cursor = self._get_cursor()
            cursor.execute("""
                IF NOT EXISTS (
                    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = 'USER_geoapolo_configuracoes' AND COLUMN_NAME = 'permite_estoque_negativo'
                )
                BEGIN
                    ALTER TABLE USER_geoapolo_configuracoes ADD permite_estoque_negativo VARCHAR(3) DEFAULT 'Nao';
                END
            """)
            if self._conn and hasattr(self._conn, "commit"):
                self._conn.commit()
        except Exception as e:
            logger.debug("Aviso ao verificar/criar coluna permite_estoque_negativo: %s", e)

    def obter_configuracoes(self, empresa_codigo: str) -> Dict[str, Any]:
        self._garantir_colunas()
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
                ISNULL(status_fechapic, '') AS status_fechapic,
                ISNULL(permite_estoque_negativo, 'Nao') AS permite_estoque_negativo
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
        self._garantir_colunas()
        cursor = self._get_cursor()
        # Verifica se registro existe
        cursor.execute("SELECT COUNT(*) FROM USER_geoapolo_configuracoes WITH (NOLOCK) WHERE empcod = ?", [empresa_codigo])
        existe = cursor.fetchone()[0] > 0

        # Normaliza permite_estoque_negativo
        perm_neg = str(dados.get("permite_estoque_negativo", "Nao")).strip()
        if perm_neg in ("Sim", "S", "1", "True", "true"):
            perm_neg = "Sim"
        else:
            perm_neg = "Nao"

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
                    status_fechapic = ?,
                    permite_estoque_negativo = ?
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
                perm_neg,
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
                    gruposoftware, tempomaximomissao, status_fechapic,
                    permite_estoque_negativo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                perm_neg,
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

    # -------------------------------------------------------------------------
    # CONSULTAS DE APOIO: ENTIDADES, ORIGENS, MOTIVOS E CATEGORIAS
    # -------------------------------------------------------------------------
    def buscar_entidades(self, termo: str = "", limite: int = 100) -> List[Dict[str, str]]:
        """Pesquisa entidades/clientes (ex: Consumidor Final) por código ou nome."""
        cursor = self._get_cursor()
        t = f"%{termo.strip()}%" if termo.strip() else "%"
        try:
            sql = f"""
                SELECT TOP ({limite})
                    RTRIM(LTRIM(CAST(entcod AS VARCHAR(20)))) AS codigo,
                    RTRIM(LTRIM(CAST(entnome AS VARCHAR(100)))) AS descricao
                FROM ENTIDADE WITH (NOLOCK)
                WHERE entnome LIKE ? OR CAST(entcod AS VARCHAR(20)) LIKE ?
                ORDER BY entnome ASC
            """
            cursor.execute(sql, [t, t])
            return [{"codigo": str(r[0] or "").strip(), "descricao": str(r[1] or "").strip()} for r in cursor.fetchall()]
        except Exception as e:
            logger.debug("Erro ao consultar ENTIDADE: %s", e)
            try:
                sql_fallback = f"""
                    SELECT TOP ({limite})
                        RTRIM(LTRIM(CAST(entcod AS VARCHAR(20)))) AS codigo,
                        RTRIM(LTRIM(CAST(entnome AS VARCHAR(100)))) AS descricao
                    FROM USER_geoapolo_entidade WITH (NOLOCK)
                    WHERE entnome LIKE ? OR CAST(entcod AS VARCHAR(20)) LIKE ?
                    ORDER BY entnome ASC
                """
                cursor.execute(sql_fallback, [t, t])
                return [{"codigo": str(r[0] or "").strip(), "descricao": str(r[1] or "").strip()} for r in cursor.fetchall()]
            except Exception:
                return []

    def obter_nome_entidade(self, entcod: str) -> str:
        """Retorna o nome da entidade dado o código."""
        cod = str(entcod).strip()
        if not cod:
            return ""
        cursor = self._get_cursor()
        try:
            cursor.execute("SELECT TOP 1 RTRIM(LTRIM(entnome)) FROM ENTIDADE WITH (NOLOCK) WHERE entcod = ?", [cod])
            row = cursor.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
        except Exception:
            pass
        try:
            cursor.execute("SELECT TOP 1 RTRIM(LTRIM(entnome)) FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE entcod = ?", [cod])
            row = cursor.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
        except Exception:
            pass
        return ""

    def buscar_origens(self, modo_integra: str = "Integra", termo: str = "", limite: int = 100) -> List[Dict[str, str]]:
        """Pesquisa origens padrão de acordo com a regra de integração."""
        cursor = self._get_cursor()
        t = f"%{termo.strip()}%" if termo.strip() else "%"
        usar_apolo = (modo_integra in ("Integra", "Mescla"))
        if usar_apolo:
            try:
                sql = f"""
                    SELECT TOP ({limite})
                        RTRIM(LTRIM(CAST(OrigCodEstr AS VARCHAR(30)))) AS codigo,
                        RTRIM(LTRIM(CAST(OrigNome AS VARCHAR(100)))) AS descricao
                    FROM ORIGEM WITH (NOLOCK)
                    WHERE (OrigCodEstr LIKE ? OR OrigNome LIKE ?)
                    ORDER BY OrigCodEstr ASC
                """
                cursor.execute(sql, [t, t])
                res = [{"codigo": str(r[0] or "").strip(), "descricao": str(r[1] or "").strip()} for r in cursor.fetchall()]
                if res:
                    return res
            except Exception as e:
                logger.debug("Erro ao consultar ORIGEM apolo: %s", e)

        # Fallback ou tabela própria
        try:
            sql = f"""
                SELECT TOP ({limite})
                    RTRIM(LTRIM(CAST(geo_origcodestr AS VARCHAR(30)))) AS codigo,
                    RTRIM(LTRIM(CAST(geo_orignome AS VARCHAR(100)))) AS descricao
                FROM USER_geoapolo_origens WITH (NOLOCK)
                WHERE (geo_origcodestr LIKE ? OR geo_orignome LIKE ?)
                ORDER BY geo_origcodestr ASC
            """
            cursor.execute(sql, [t, t])
            return [{"codigo": str(r[0] or "").strip(), "descricao": str(r[1] or "").strip()} for r in cursor.fetchall()]
        except Exception as e:
            logger.debug("Erro ao consultar USER_geoapolo_origens: %s", e)
            return []

    def obter_nome_origem(self, modo_integra: str, origcodestr: str) -> str:
        cod = str(origcodestr).strip()
        if not cod:
            return ""
        cursor = self._get_cursor()
        usar_apolo = (modo_integra in ("Integra", "Mescla"))
        if usar_apolo:
            try:
                cursor.execute("SELECT TOP 1 RTRIM(LTRIM(OrigNome)) FROM ORIGEM WITH (NOLOCK) WHERE OrigCodEstr = ?", [cod])
                row = cursor.fetchone()
                if row and row[0]:
                    return str(row[0]).strip()
            except Exception:
                pass
        try:
            cursor.execute("SELECT TOP 1 RTRIM(LTRIM(geo_orignome)) FROM USER_geoapolo_origens WITH (NOLOCK) WHERE geo_origcodestr = ?", [cod])
            row = cursor.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
        except Exception:
            pass
        return ""

    def buscar_motivos_ocorrencia(self, modo_integra: str = "Integra", termo: str = "", limite: int = 100) -> List[Dict[str, str]]:
        """Pesquisa motivos de ocorrência padrão."""
        cursor = self._get_cursor()
        t = f"%{termo.strip()}%" if termo.strip() else "%"
        usar_apolo = (modo_integra in ("Integra", "Mescla"))
        if usar_apolo:
            try:
                sql = f"""
                    SELECT TOP ({limite})
                        RTRIM(LTRIM(CAST(MotOcorCodEstr AS VARCHAR(30)))) AS codigo,
                        RTRIM(LTRIM(CAST(MotOcorDescr AS VARCHAR(100)))) AS descricao
                    FROM MOTIVO_OCOR WITH (NOLOCK)
                    WHERE (MotOcorCodEstr LIKE ? OR MotOcorDescr LIKE ?)
                    ORDER BY MotOcorCodEstr ASC
                """
                cursor.execute(sql, [t, t])
                res = [{"codigo": str(r[0] or "").strip(), "descricao": str(r[1] or "").strip()} for r in cursor.fetchall()]
                if res:
                    return res
            except Exception as e:
                logger.debug("Erro ao consultar MOTIVO_OCOR apolo: %s", e)

        try:
            sql = f"""
                SELECT TOP ({limite})
                    RTRIM(LTRIM(CAST(geo_motocorcodestr AS VARCHAR(30)))) AS codigo,
                    RTRIM(LTRIM(CAST(geo_motocordescr AS VARCHAR(100)))) AS descricao
                FROM USER_geoapolo_motivo_ocor WITH (NOLOCK)
                WHERE (geo_motocorcodestr LIKE ? OR geo_motocordescr LIKE ?)
                ORDER BY geo_motocorcodestr ASC
            """
            cursor.execute(sql, [t, t])
            return [{"codigo": str(r[0] or "").strip(), "descricao": str(r[1] or "").strip()} for r in cursor.fetchall()]
        except Exception as e:
            logger.debug("Erro ao consultar USER_geoapolo_motivo_ocor: %s", e)
            return []

    def obter_nome_motivo_ocorrencia(self, modo_integra: str, motocorcodestr: str) -> str:
        cod = str(motocorcodestr).strip()
        if not cod:
            return ""
        cursor = self._get_cursor()
        usar_apolo = (modo_integra in ("Integra", "Mescla"))
        if usar_apolo:
            try:
                cursor.execute("SELECT TOP 1 RTRIM(LTRIM(MotOcorDescr)) FROM MOTIVO_OCOR WITH (NOLOCK) WHERE MotOcorCodEstr = ?", [cod])
                row = cursor.fetchone()
                if row and row[0]:
                    return str(row[0]).strip()
            except Exception:
                pass
        try:
            cursor.execute("SELECT TOP 1 RTRIM(LTRIM(geo_motocordescr)) FROM USER_geoapolo_motivo_ocor WITH (NOLOCK) WHERE geo_motocorcodestr = ?", [cod])
            row = cursor.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
        except Exception:
            pass
        return ""

    def buscar_categorias_parceiras(self, modo_integra: str = "Integra", termo: str = "", limite: int = 100) -> List[Dict[str, str]]:
        """Pesquisa categorias parceiras."""
        cursor = self._get_cursor()
        t = f"%{termo.strip()}%" if termo.strip() else "%"
        try:
            sql = f"""
                SELECT TOP ({limite})
                    RTRIM(LTRIM(CAST(geocategcodestr AS VARCHAR(30)))) AS codigo,
                    RTRIM(LTRIM(CAST(geocategnome AS VARCHAR(100)))) AS descricao
                FROM USER_geoapolo_categoria WITH (NOLOCK)
                WHERE (geocategcodestr LIKE ? OR geocategnome LIKE ?)
                ORDER BY geocategcodestr ASC
            """
            cursor.execute(sql, [t, t])
            res = [{"codigo": str(r[0] or "").strip(), "descricao": str(r[1] or "").strip()} for r in cursor.fetchall()]
            if res:
                return res
        except Exception as e:
            logger.debug("Erro ao consultar USER_geoapolo_categoria: %s", e)

        try:
            sql = f"""
                SELECT TOP ({limite})
                    RTRIM(LTRIM(CAST(categcodestr AS VARCHAR(30)))) AS codigo,
                    RTRIM(LTRIM(CAST(categnome AS VARCHAR(100)))) AS descricao
                FROM CATEGORIA WITH (NOLOCK)
                WHERE (categcodestr LIKE ? OR categnome LIKE ?)
                ORDER BY categcodestr ASC
            """
            cursor.execute(sql, [t, t])
            return [{"codigo": str(r[0] or "").strip(), "descricao": str(r[1] or "").strip()} for r in cursor.fetchall()]
        except Exception as e:
            logger.debug("Erro ao consultar CATEGORIA apolo: %s", e)
            return []

    def obter_nome_categoria(self, modo_integra: str, geocategcodestr: str) -> str:
        cod = str(geocategcodestr).strip()
        if not cod:
            return ""
        cursor = self._get_cursor()
        try:
            cursor.execute("SELECT TOP 1 RTRIM(LTRIM(geocategnome)) FROM USER_geoapolo_categoria WITH (NOLOCK) WHERE geocategcodestr = ?", [cod])
            row = cursor.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
        except Exception:
            pass
        try:
            cursor.execute("SELECT TOP 1 RTRIM(LTRIM(categnome)) FROM CATEGORIA WITH (NOLOCK) WHERE categcodestr = ?", [cod])
            row = cursor.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
        except Exception:
            pass
        return ""
