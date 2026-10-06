"""
Repositório de dados para Entidades em Python / SQL Server.
Correspondente a unt_entidades_repository.pas.

Preserva rigorosamente:
- Hints de leitura T-SQL: WITH (NOLOCK)
- Parametrização segura contra SQL Injection
- Chamada de Stored Procedure nativa User_geraocorrencia_projetosv2 com parâmetros vinculados
- Mapeamento resiliente de nomes de colunas e registro detalhado de divergências em arquivo de log
"""

import re
import os
import sys
from pathlib import Path
from datetime import datetime
import traceback
import logging
from typing import List, Dict, Any, Optional, Tuple


def _sanitizar_str(val: Any) -> Optional[str]:
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def _sanitizar_inteiro(val: Any) -> Optional[int]:
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    apenas_digitos = re.sub(r"[^\d-]", "", s)
    if not apenas_digitos or apenas_digitos == "-":
        return None
    try:
        return int(apenas_digitos)
    except (ValueError, TypeError):
        return None


def _sanitizar_float(val: Any) -> Optional[float]:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace("R$", "").replace(" ", "")
    if not s:
        return None
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def _sanitizar_data(val: Any) -> Optional[str]:
    if val is None:
        return None
    s = str(val).strip()
    if not s or s in ("None", "null") or not re.search(r"\d", s):
        return None
    partes = s.split("/")
    if len(partes) == 3:
        dia, mes, ano = partes[0].strip(), partes[1].strip(), partes[2].strip()
        if dia.isdigit() and mes.isdigit() and ano.isdigit() and len(ano) == 4:
            return f"{ano.zfill(4)}-{mes.zfill(2)}-{dia.zfill(2)}"
    partes_iso = s.split("-")
    if len(partes_iso) == 3 and len(partes_iso[0]) == 4:
        return s[:10]
    return s if s else None


def _sanitizar_obs(val: Any, max_len: int = 200) -> Optional[str]:
    s = _sanitizar_str(val)
    if s is None:
        return None
    return s[:max_len]


def _resolver_tipolograd(cursor, val: Any) -> Optional[int]:
    """Converte identificador ou sigla de tipo de logradouro para o ID numérico da tabela USER_geoapolo_tipologradouro."""
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    if s.isdigit():
        return int(s)

    # Mapeamento rápido de siglas e nomes comuns
    norm = s.upper().replace(".", "").replace("Ç", "C").replace("Ã", "A").strip()
    mapa_comuns = {
        "RUA": 1,
        "R": 1,
        "AV": 115,
        "AVENIDA": 115,
        "AL": 3,
        "ALAMEDA": 3,
        "PCA": 4,
        "PRACA": 4,
        "PC": 4,
        "ROD": 472,
        "RODOVIA": 472,
        "TRV": 583,
        "TRAVESSA": 583,
        "EST": 251,
        "ESTRADA": 251,
        "LOT": 349,
        "LOTEAMENTO": 349,
        "RES": 464,
        "RESIDENCIAL": 464,
        "VIA": 605,
        "VL": 609,
        "VILA": 609,
    }
    if norm in mapa_comuns:
        return mapa_comuns[norm]
    if s.upper() in ("PÇ", "PÇA", "PRAÇA"):
        return 4

    try:
        cursor.execute(
            "SELECT tipolograd FROM USER_geoapolo_tipologradouro WITH (NOLOCK) WHERE UPPER(tipologradabrev) = UPPER(?) OR UPPER(tipologradouro) = UPPER(?)",
            (s, s)
        )
        r = cursor.fetchone()
        if r and r[0] is not None:
            return int(r[0])
        cursor.execute(
            "SELECT tipolograd FROM USER_geoapolo_tipologradouro WITH (NOLOCK) WHERE UPPER(tipologradabrev) LIKE UPPER(?) OR UPPER(tipologradouro) LIKE UPPER(?)",
            (f"{s}%", f"{s}%")
        )
        r = cursor.fetchone()
        if r and r[0] is not None:
            return int(r[0])
    except Exception:
        pass
    return None



def _resolver_grauescolaridade(cursor, val: Any) -> Optional[int]:
    """Extrai ou resolve o código numérico de grau de escolaridade para USER_geoapolo_grauescolaridade."""
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    # 1. Se começa com dígito ou contém número isolado (ex: "8 - SUPERIOR", "8")
    m = re.search(r"^\s*(\d+)", s)
    if m:
        try:
            return int(m.group(1))
        except (ValueError, TypeError):
            pass
    num = _sanitizar_inteiro(s)
    if num is not None:
        return num
    try:
        cursor.execute(
            "SELECT codigo_grauescolaridade FROM USER_geoapolo_grauescolaridade WITH (NOLOCK) WHERE grau_escolaridade LIKE ?",
            (f"%{s}%",)
        )
        r = cursor.fetchone()
        if r and r[0] is not None:
            return int(r[0])
    except Exception:
        pass
    return None



# Garante que a raiz do projeto esteja no sys.path
_raiz_projeto = str(Path(__file__).resolve().parent.parent)
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

try:
    from entidades.models import EntidadeFiltro, CredencialAlvo
except (ImportError, ModuleNotFoundError):
    from models import EntidadeFiltro, CredencialAlvo

logger = logging.getLogger(__name__)

# Mapeamento de colunas canônicas entre UI, Views e Tabelas
MAPA_COLUNAS = {
    # Nomes
    "geoentnome": "entnome",
    "nome": "entnome",
    "entnome": "entnome",
    "razao_social": "entnome",
    "nome_fantasia": "entnomefant",
    "entnomefant": "entnomefant",
    "geoentnomefantasia": "entnomefant",
    "fantasia": "entnomefant",

    # Documentos
    "documento": "EntCpfCgc",
    "cpf": "EntCpfCgc",
    "cnpj": "EntCpfCgc",
    "entcpfcgc": "EntCpfCgc",
    "rg": "EntRgIe",
    "rg_ie": "EntRgIe",
    "entrgie": "EntRgIe",
    "inscricao_estadual": "EntRgIe",

    # Endereço
    "geoentender": "entender",
    "endereco": "entender",
    "entender": "entender",
    "logradouro": "entender",
    "entlograd": "entlograd",
    "geoenderno": "entenderno",
    "numero": "entenderno",
    "entenderno": "entenderno",
    "geoentendercomp": "entendercomp",
    "complemento": "entendercomp",
    "entendercomp": "entendercomp",
    "geoentbair": "entbair",
    "bairro": "entbair",
    "entbair": "entbair",
    "geoentcep": "entcep",
    "cep": "entcep",
    "entcep": "entcep",
    "cidade": "cidnomecomp",
    "cidnomecomp": "cidnomecomp",
    "uf": "ufsigla",
    "ufsigla": "ufsigla",
    "estado": "ufsigla",

    # Códigos e datas
    "geoentcod": "geoentcod",
    "codigo": "geoentcod",
    "cod_geo": "geoentcod",
    "entcod": "entcod",
    "cod_alvo": "entcod",
    "entdatacad": "entdatacad",
    "data_cadastro": "entdatacad",
    "geoentdatacad": "entdatacad",
    "entdesdedata": "EntDesdeData",
    "entdataanivfund": "entdataanivfund",

    # Dados cadastrais complementares
    "tipo_fj": "enttipofj",
    "enttipofj": "enttipofj",
    "geotipofj": "enttipofj",
    "genero": "entgenero",
    "entgenero": "entgenero",
    "geoentgenero": "entgenero",
    "estado_civil": "EntEstCivil",
    "entestcivil": "EntEstCivil",
    "cargo": "cargonome",
    "cargonome": "cargonome",
    "geocargonome": "cargonome",
    "escolaridade": "EntGrauEscol",
    "entgrauescol": "EntGrauEscol",
    "grau_escolaridade": "EntGrauEscol",
    "origem": "OrigNome",
    "orignome": "OrigNome",
    "geo_orignome": "OrigNome",
    "categoria": "categnome",
    "categnome": "categnome",
    "diocese": "USERNomeDiocese",
    "usernomediocese": "USERNomeDiocese",
    "observacoes": "Entobservacoes",
    "entobservacoes": "Entobservacoes",
    "geoobservacoes": "Entobservacoes",
}


class EntidadeRepository:
    """
    Camada de Acesso a Dados (Repository) para a entidade no SQL Server.
    Pode receber uma conexão pyodbc ou sqlalchemy.engine.Connection via injeção de dependência.
    """

    def __init__(self, connection=None):
        self._conn = connection

    def set_connection(self, connection):
        self._conn = connection

    def _get_cursor(self):
        from entidades.database import obter_conexao_banco, testar_conexao
        if self._conn is None or not testar_conexao(self._conn):
            try:
                self._conn = obter_conexao_banco(forcar_nova=True)
            except Exception as e:
                logger.warning("Tentativa de reconexão do repositório falhou: %s", e)
        if self._conn is None:
            raise RuntimeError("Conexão com o banco de dados não foi inicializada no Repositório.")
        return self._conn.cursor()


    def _registrar_log_erro_sql(self, operacao: str, sql: str, params: Any, erro: Exception):
        """
        Registra detalhadamente erros de SQL e campos faltantes em arquivo no diretório
        para pesquisa e diagnóstico posterior, conforme diretriz do sistema.
        """
        caminho_log = os.path.join(_raiz_projeto, "relatorio_erros_sql_entidades.txt")
        try:
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(caminho_log, "a", encoding="utf-8") as f:
                f.write(f"[{agora}] OPERAÇÃO: {operacao}\n")
                f.write(f"SQL EXECUTADO:\n{sql.strip()}\n")
                f.write(f"PARÂMETROS: {params}\n")
                f.write(f"ERRO RETORNADO: {erro}\n")
                f.write(f"STACK TRACE:\n{traceback.format_exc()}\n")
                f.write("-" * 80 + "\n\n")
            logger.error("Erro de SQL registrado em %s: %s", caminho_log, erro)
        except Exception as ex_log:
            logger.exception("Falha ao gravar arquivo de log de erros SQL: %s", ex_log)

    def obter_parametro_integracao(self, empcod: str) -> str:
        """
        Consulta se a empresa possui integração com o Alvo (Integra / Não Integra / Mescla).
        não Preserva WITH (NOLOCK).
        """
        sql = """
            SELECT integra_entidades_apolo 
              FROM USER_geoapolo_configuracoes  
             WHERE empcod = ?
        """
        try:
            cursor = self._get_cursor()
            cursor.execute(sql, (empcod,))
            row = cursor.fetchone()
            if row:
                return row[0] or ""
            return ""
        except Exception as exc:
            self._registrar_log_erro_sql("obter_parametro_integracao", sql, (empcod,), exc)
            return ""

    def view_existe(self, nome_view: str) -> bool:
        """Verifica a existência de view no catálogo de metadados do SQL Server."""
        sql = "SELECT 1 FROM sys.views WHERE name = ?"
        try:
            cursor = self._get_cursor()
            cursor.execute(sql, (nome_view,))
            return cursor.fetchone() is not None
        except Exception as exc:
            self._registrar_log_erro_sql("view_existe", sql, (nome_view,), exc)
            return False

    def consultar_lista(self, filtro: EntidadeFiltro) -> List[Dict[str, Any]]:
        """
        Executa a busca otimizada de entidades na base selecionada (GeoApolo ou Alvo).
        Normaliza os campos de busca e ordenação para evitar erros de colunas inexistentes.
        """
        direcao = "ASC" if filtro.ordem_asc else "DESC"
        raw_busca = (filtro.campo_busca or "entnome").strip().lower()
        campo_busca = MAPA_COLUNAS.get(raw_busca, raw_busca)

        raw_ordem = (filtro.campo_ordenacao or "entnome").strip().lower()
        ordem_col = MAPA_COLUNAS.get(raw_ordem, raw_ordem)

        cursor = self._get_cursor()

        # 1. Base Alvo
        if filtro.base_dados == "Alvo":
            tem_busca = bool((filtro.texto_busca or "").strip())
            condicoes = []
            params = []
            if filtro.categoria_busca:
                cat_alvo = filtro.categoria_busca.split(" - ")[0].strip()
                condicoes.append(
                    "EXISTS (SELECT 1 FROM ENT_CATEG ec WITH (NOLOCK) "
                    "        WHERE ec.entcod = e.entcod AND ec.categcodestr = ?)"
                )
                params.append(cat_alvo)

            if tem_busca:
                if campo_busca.lower() in ("categnome", "categoria", "categoria(s)", "categcodestr"):
                    condicoes.append(
                        "(e.categcodestr LIKE ? "
                        "OR e.entcod IN (SELECT ec.entcod FROM ENT_CATEG ec WITH (NOLOCK) "
                        "   WHERE ec.categcodestr LIKE ? OR ec.categcodestr IN "
                        "       (SELECT c.categcodestr FROM CATEGORIA c WITH (NOLOCK) WHERE c.categnome LIKE ?)))"
                    )
                    params.extend([f"%{filtro.texto_busca.strip()}%", f"%{filtro.texto_busca.strip()}%", f"%{filtro.texto_busca.strip()}%"])
                else:
                    condicoes.append(f"e.{campo_busca} LIKE ?")
                    params.append(f"%{filtro.texto_busca.strip()}%")
            where_str = ("WHERE " + " AND ".join(condicoes)) if condicoes else ""
            sql = f"""
                SELECT *
                  FROM entidades_apolo e WITH (NOLOCK)
                 {where_str}
                 ORDER BY e.{ordem_col} {direcao}
                OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            """
            limite_alvo = int(filtro.limite) if filtro.limite is not None else 50000
            params_alvo = list(params) + [int(filtro.offset or 0), limite_alvo]

            try:
                cursor.execute(sql, params_alvo)
                colunas = [column[0] for column in cursor.description]
                return [dict(zip(colunas, row)) for row in cursor.fetchall()]
            except Exception as exc:
                self._registrar_log_erro_sql("consultar_lista_alvo", sql, params_alvo, exc)
                # Fallback direto na tabela entidade caso a view entidades_apolo tenha erro
                try:
                    where_fb = f"WHERE {campo_busca} LIKE ?" if tem_busca else ""
                    sql_fallback = f"""
                        SELECT entcod, entnome, entnomefant, entender, entenderno, entbair, entcep,
                               cidcod, enttipofj, EntCpfCgc, EntRgIe, entdatacad
                          FROM entidade 
                         {where_fb}
                         ORDER BY {ordem_col} {direcao}
                        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
                    """
                    params_fb = (params if tem_busca else []) + [int(filtro.offset or 0), limite_alvo]
                    cursor.execute(sql_fallback, params_fb)
                    colunas = [column[0] for column in cursor.description]
                    return [dict(zip(colunas, row)) for row in cursor.fetchall()]
                except Exception as exc_fb:
                    self._registrar_log_erro_sql("consultar_lista_alvo_fallback", sql_fallback, params, exc_fb)
                    raise exc

        # 2. Base GeoApolo
        else:
            tem_busca = bool((filtro.texto_busca or "").strip())
            texto_busca_str = (filtro.texto_busca or "").strip()
            texto_apenas_digitos = re.sub(r"\D", "", texto_busca_str)
            condicoes = []
            params = []

            # Filtro de sincronização (JAEXPORTADA vs PENDENTES):
            # Se for busca específica com termo digitado pelo usuário, pesquisa em toda a base
            # a menos que o usuário tenha marcado especificamente 'JAEXPORTADA'
            if filtro.filtro_especial == "JAEXPORTADA":
                condicoes.append("ue.atualizou_apolo = 'S'")
            elif not tem_busca or filtro.tipo_pesquisa != "Especifica":
                if filtro.filtro_especial == "PENDENTES":
                    condicoes.append("(ue.atualizou_apolo = 'N' OR ue.atualizou_apolo IS NULL)")

            if filtro.categoria_busca:
                cat_geo = filtro.categoria_busca.split(" - ")[0].strip()
                condicoes.append(
                    "EXISTS (SELECT 1 FROM USER_geoapolo_entcateg uec WITH (NOLOCK) "
                    "        WHERE uec.geoentcod = e.geoentcod AND uec.geocategcodestr = ?)"
                )
                params.append(cat_geo)

            if tem_busca:
                # Tratamento especial para busca por código GeoApolo
                if campo_busca.lower() in ("geoentcod", "codigo", "cod_geo"):
                    pad_7 = texto_apenas_digitos.zfill(7) if texto_apenas_digitos else texto_busca_str
                    condicoes.append("(e.geoentcod = ? OR e.geoentcod = ? OR e.geoentcod LIKE ?)")
                    params.extend([texto_busca_str, pad_7, f"%{texto_busca_str}%"])
                # Tratamento especial para busca por documento (CPF / CNPJ)
                elif campo_busca.lower() in ("entcpfcgc", "documento", "cpf", "cnpj", "geonumerodocumento") or (texto_apenas_digitos and len(texto_apenas_digitos) in (11, 14)):
                    if texto_apenas_digitos:
                        condicoes.append(
                            "(e.EntCpfCgc LIKE ? OR e.geonumerodocumento LIKE ? "
                            "OR REPLACE(REPLACE(REPLACE(ISNULL(e.EntCpfCgc, ''), '.', ''), '-', ''), '/', '') LIKE ? "
                            "OR REPLACE(REPLACE(REPLACE(ISNULL(e.geonumerodocumento, ''), '.', ''), '-', ''), '/', '') LIKE ?)"
                        )
                        params.extend([f"%{texto_busca_str}%", f"%{texto_busca_str}%", f"%{texto_apenas_digitos}%", f"%{texto_apenas_digitos}%"])
                    else:
                        condicoes.append("(e.EntCpfCgc LIKE ? OR e.geonumerodocumento LIKE ?)")
                        params.extend([f"%{texto_busca_str}%", f"%{texto_busca_str}%"])
                # Tratamento especial para busca por Categoria
                elif campo_busca.lower() in ("categnome", "categoria", "categoria(s)", "geocategnome", "geocategcodestr"):
                    condicoes.append(
                        "(e.geocategnome LIKE ? OR e.geocategcodestr LIKE ? "
                        "OR e.geoentcod IN (SELECT uec.geoentcod FROM USER_geoapolo_entcateg uec WITH (NOLOCK) "
                        "   WHERE uec.geocategcodestr LIKE ? OR uec.geocategcodestr IN "
                        "       (SELECT gc.geocategcodestr FROM USER_geoapolo_categoria gc WITH (NOLOCK) WHERE gc.geocategnome LIKE ?)))"
                    )
                    params.extend([f"%{texto_busca_str}%", f"%{texto_busca_str}%", f"%{texto_busca_str}%", f"%{texto_busca_str}%"])
                else:
                    col_busca_geo = "geoentnome" if campo_busca == "entnome" else campo_busca
                    condicoes.append(f"e.{col_busca_geo} LIKE ?")
                    params.append(f"%{texto_busca_str}%")

            where_str = ("WHERE " + " AND ".join(condicoes)) if condicoes else ""

            # Ajusta coluna de ordenação específica para as colunas da view entidades_geoapolo
            mapa_ordem_geo = {
                "entnome": "geoentnome",
                "entobservacoes": "geoobservacoes",
                "entnomefant": "geoentnomefantasia",
                "entdatacad": "geoentdatacad",
                "entender": "geoentender",
                "entenderno": "geoenderno",
                "entbair": "geoentbair",
                "entcep": "geoentcep",
            }
            ordem_col_geo = mapa_ordem_geo.get(ordem_col.lower(), ordem_col)

            # Se a busca foi por código, prioriza exibição do match exato no topo
            prioridade_match = ""
            if tem_busca and campo_busca.lower() in ("geoentcod", "codigo", "cod_geo"):
                pad_7_val = texto_apenas_digitos.zfill(7) if texto_apenas_digitos else texto_busca_str
                prioridade_match = f"CASE WHEN e.geoentcod = '{texto_busca_str}' OR e.geoentcod = '{pad_7_val}' THEN 0 ELSE 1 END, "

            sql = f"""
                SELECT e.*, ue.atualizou_apolo AS status_sincronizacao,
                       ue.geoentrgie, ue.geoentrgie AS EntRgIe, ue.geoentrgie AS entrgie
                  FROM entidades_geoapolo e 
                 INNER JOIN user_geoapolo_entidade ue 
                    ON e.geoentcod = ue.geoentcod
                 {where_str}
                 ORDER BY {prioridade_match}CASE WHEN ISNULL(ue.atualizou_apolo, 'N') = 'N' AND e.geoobservacoes IS NULL THEN 0 ELSE 1 END, e.{ordem_col_geo} {direcao}
                OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            """
            params_geo = list(params) + [int(filtro.offset or 0), int(filtro.limite or 100)]

            try:
                cursor.execute(sql, params_geo)
                colunas = [column[0] for column in cursor.description]
                return [dict(zip(colunas, row)) for row in cursor.fetchall()]
            except Exception as exc:
                self._registrar_log_erro_sql("consultar_lista_geoapolo", sql, params_geo, exc)
                # Fallback direto na tabela user_geoapolo_entidade caso a view entidades_geoapolo tenha erro
                try:
                    fb_conds = []
                    fb_params = []
                    if filtro.filtro_especial == "JAEXPORTADA":
                        fb_conds.append("atualizou_apolo = 'S'")
                    elif not tem_busca or filtro.tipo_pesquisa != "Especifica":
                        if filtro.filtro_especial == "PENDENTES":
                            fb_conds.append("(atualizou_apolo = 'N' OR atualizou_apolo IS NULL)")

                    if tem_busca:
                        if campo_busca.lower() in ("geoentcod", "codigo", "cod_geo"):
                            pad_7 = texto_apenas_digitos.zfill(7) if texto_apenas_digitos else texto_busca_str
                            fb_conds.append("(geoentcod = ? OR geoentcod = ? OR geoentcod LIKE ?)")
                            fb_params.extend([texto_busca_str, pad_7, f"%{texto_busca_str}%"])
                        elif campo_busca.lower() in ("entcpfcgc", "documento", "cpf", "cnpj", "geonumerodocumento") or (texto_apenas_digitos and len(texto_apenas_digitos) in (11, 14)):
                            fb_conds.append(
                                "EXISTS (SELECT 1 FROM USER_geoapolo_entidade_documentos uged WITH (NOLOCK) "
                                "WHERE uged.geoentcod = user_geoapolo_entidade.geoentcod "
                                "AND (uged.geonumerodocumento LIKE ? "
                                "OR REPLACE(REPLACE(REPLACE(ISNULL(uged.geonumerodocumento, ''), '.', ''), '-', ''), '/', '') LIKE ?))"
                            )
                            fb_params.extend([f"%{texto_busca_str}%", f"%{texto_apenas_digitos or texto_busca_str}%"])
                        elif campo_busca.lower() in ("entnome", "geoentnome", "razao_social"):
                            fb_conds.append("geoentnome LIKE ?")
                            fb_params.append(f"%{texto_busca_str}%")
                        else:
                            col_fb = "geoentnome" if campo_busca == "entnome" else campo_busca
                            fb_conds.append(f"{col_fb} LIKE ?")
                            fb_params.append(f"%{texto_busca_str}%")

                    fb_where = ("WHERE " + " AND ".join(fb_conds)) if fb_conds else ""
                    sql_fallback = f"""
                        SELECT TOP ({filtro.limite})
                               geoentcod, entcod, geoentnome AS entnome, geoentnomefantasia AS entnomefant,
                               geoentender AS entender, geoenderno AS entenderno, geoentbair AS entbair,
                               geoentcep AS entcep, geocidcod AS cidcod, geotipofj AS enttipofj,
                               atualizou_apolo, geoobservacoes AS Entobservacoes, geoentdatacad AS entdatacad
                          FROM user_geoapolo_entidade 
                         {fb_where}
                         ORDER BY geoentnome ASC
                    """
                    cursor.execute(sql_fallback, fb_params)
                    colunas = [column[0] for column in cursor.description]
                    return [dict(zip(colunas, row)) for row in cursor.fetchall()]
                except Exception as exc_fb:
                    self._registrar_log_erro_sql("consultar_lista_geoapolo_fallback", sql_fallback, fb_params, exc_fb)
                    raise exc

    def registrar_log_atividade(self, usucod: str, descricao: str) -> bool:
        """
        Registra uma atividade operacional na tabela USER_geoapolo_logatividades.
        Compatível com unt_funcoes.pas do Delphi.
        """
        if not descricao:
            return False
        cursor = self._get_cursor()
        agora = datetime.now()
        data_str = agora.strftime("%Y-%m-%d")
        hora_str = agora.strftime("%H:%M:%S")
        usucod_limpo = (usucod or "SISTEMA").strip().upper()[:20]
        desc_limpa = str(descricao).strip()

        for tabela in ("USER_geoapolo_logatividades", "USER_geoapolo_logatividade"):
            try:
                sql = f"INSERT INTO {tabela} (data, hora, usucod, descricao) VALUES (?, ?, ?, ?)"
                cursor.execute(sql, (data_str, hora_str, usucod_limpo, desc_limpa))
                self._conn.commit()
                return True
            except Exception as exc:
                if tabela == "USER_geoapolo_logatividades":
                    continue
                logger.warning("Falha ao registrar log de atividade: %s", exc)
                return False
        return False

    def obter_todas_chaves_filtro(self, filtro: EntidadeFiltro) -> List[Dict[str, Any]]:
        """
        Retorna todos os registros correspondentes ao filtro ativo sem limite de paginação,
        para fins de exportação em lote (Exporta Filtro para o Alvo).
        """
        import copy
        filtro_completo = copy.copy(filtro)
        filtro_completo.offset = 0
        filtro_completo.limite = 50000
        return self.consultar_lista(filtro_completo)

    def obter_ocorrencia_codigo(self, geoentcod: str) -> Optional[str]:
        sql = "SELECT ocorcod FROM user_geoapolo_entidade  WHERE geoentcod = ?"
        try:
            cursor = self._get_cursor()
            cursor.execute(sql, (geoentcod,))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as exc:
            self._registrar_log_erro_sql("obter_ocorrencia_codigo", sql, (geoentcod,), exc)
            return None

    def registrar_ocorrencia_ignorada(self, cod_empresa: str, ocor_cod: str, cod_usuario: str):
        """
        Executa a Stored Procedure nativa T-SQL de ocorrência com bind parameters seguros.
        """
        sql = """
            EXEC dbo.User_geraocorrencia_projetosv2
                @p_empcod        = ?,
                @p_tipo          = ?,
                @p_modo          = ?,
                @p_compl1        = ?,
                @p_compl2        = ?,
                @p_ocorcod       = ?,
                @p_compl3        = ?,
                @p_usucod        = ?,
                @p_descricao     = ?,
                @p_codmotivo     = ?,
                @p_compl4        = ?,
                @p_data1         = NULL,
                @p_data2         = NULL,
                @p_compl5        = ?
        """
        params = (
            cod_empresa,
            "F",
            "INDIVIDUAL",
            "",
            "",
            ocor_cod or "",
            "",
            cod_usuario,
            "FOI IGNORADA A ATUALIZAÇÃO DE CADASTRO POR ESTAR ATUALIZADO",
            "0000012",
            "",
            "",
        )
        try:
            cursor = self._get_cursor()
            cursor.execute(sql, params)
        except Exception as exc:
            self._registrar_log_erro_sql("registrar_ocorrencia_ignorada", sql, params, exc)
            raise

    def ignorar_atualizacao_alvo(self, geoentcod: str, usucod_apolo: str, cod_empresa: str, cod_usuario: str) -> bool:
        """
        Atualiza a flag atualizou_apolo para 'S' e gera a ocorrência interna em transação.
        """
        cursor = self._get_cursor()
        try:
            sql_upd = """
                UPDATE USER_geoapolo_Entidade
                   SET atualizou_apolo = 'S', 
                       usucod_atualizou_apolo = ?
                 WHERE geoentcod = ?
            """
            cursor.execute(sql_upd, (usucod_apolo, geoentcod))

            ocor_cod = self.obter_ocorrencia_codigo(geoentcod)
            self.registrar_ocorrencia_ignorada(cod_empresa, ocor_cod or "", cod_usuario)

            self._conn.commit()
            return True
        except Exception as exc:
            self._conn.rollback()
            self._registrar_log_erro_sql("ignorar_atualizacao_alvo", "UPDATE USER_geoapolo_Entidade...", (usucod_apolo, geoentcod), exc)
            logger.exception("Erro ao ignorar atualização da entidade: %s", exc)
            raise

    def atualizar_entcod_alvo_via_cpf(self, geoentcod: str) -> Optional[str]:
        """
        Verifica se a entidade existe na base Alvo pelo CPF/CNPJ e vincula o entcod.
        """
        cursor = self._get_cursor()
        cpf, _ = self.obter_cpf_rg_documentos(geoentcod)
        if not cpf:
            return None

        digitos_cpf = re.sub(r"\D", "", cpf)
        sql_alvo = """
            SELECT TOP 1 entcod 
              FROM entidades_apolo WITH (NOLOCK) 
             WHERE EntCpfCgc = ? 
                OR REPLACE(REPLACE(REPLACE(ISNULL(EntCpfCgc,''), '.', ''), '-', ''), '/', '') = ?
        """
        try:
            cursor.execute(sql_alvo, (cpf, digitos_cpf))
            row_alvo = cursor.fetchone()
            if not row_alvo:
                sql_fb = """
                    SELECT TOP 1 entcod 
                      FROM entidade WITH (NOLOCK) 
                     WHERE EntCpfCgc = ? 
                        OR REPLACE(REPLACE(REPLACE(ISNULL(EntCpfCgc,''), '.', ''), '-', ''), '/', '') = ?
                """
                cursor.execute(sql_fb, (cpf, digitos_cpf))
                row_alvo = cursor.fetchone()

            if not row_alvo:
                return None

            entcod_alvo = str(row_alvo[0]).strip()
            if entcod_alvo:
                sql_upd = "UPDATE USER_geoapolo_entidade SET entcod = ? WHERE geoentcod = ?"
                cursor.execute(sql_upd, (entcod_alvo, geoentcod))
                self._conn.commit()
            return entcod_alvo
        except Exception as exc:
            self._conn.rollback()
            self._registrar_log_erro_sql("atualizar_entcod_alvo_via_cpf", sql_alvo, (cpf, digitos_cpf), exc)
            return None

    def vincular_entcod(self, geoentcod: str, entcod: str) -> bool:
        """
        Atualiza o campo entcod da entidade GeoApolo com o identificador oficial gerado ou vinculado no Alvo.
        Equivalente ao comando UPDATE USER_geoapolo_entidade SET entcod = :entcod WHERE geoentcod = :geoentcod do Delphi.
        """
        sql = "UPDATE USER_geoapolo_entidade SET entcod = ? WHERE geoentcod = ?"
        try:
            cursor = self._get_cursor()
            cursor.execute(sql, (str(entcod), str(geoentcod)))
            self._conn.commit()
            return True
        except Exception as exc:
            self._conn.rollback()
            self._registrar_log_erro_sql("vincular_entcod", sql, (entcod, geoentcod), exc)
            return False

    def carregar_dados_completos_entidade_geoapolo(self, geoentcod: str) -> Dict[str, Any]:
        """
        Carrega todos os dados brutos da entidade da base GeoApolo (USER_geoapolo_entidade)
        com LEFT JOIN em USER_geoapolo_tipologradouro para trazer as siglas e descrições do logradouro.
        """
        sql = """
            SELECT uge.*, 
                   ugtl.tipologradabrev AS tipologradabrev, 
                   ugtl.tipologradouro AS tipologradnome,
                   ugtl.tipologradabrev AS entlograd,
                   ugtl.tipologradabrev AS logradouro,
                   ugoe.geo_origcodestr,
                   ugoe.geo_origcodestr AS origcodestr,
                   ugo.geo_orignome,
                   ugo.geo_orignome AS orignome,
                   cid.ufsigla,
                   cid.cidnomecomp
              FROM USER_geoapolo_entidade uge WITH (NOLOCK)
              LEFT JOIN USER_geoapolo_tipologradouro ugtl WITH (NOLOCK) ON uge.tipolograd = ugtl.tipolograd
              LEFT JOIN USER_geoapolo_origens_entidade ugoe WITH (NOLOCK) ON uge.geoentcod = ugoe.geoentcod
              LEFT JOIN USER_geoapolo_origens ugo WITH (NOLOCK) ON ugoe.geo_origcodestr = ugo.geo_origcodestr
              LEFT JOIN user_geoapolo_cidades cid WITH (NOLOCK) ON uge.geocidcod = cid.geocidcod
             WHERE uge.geoentcod = ?
        """
        try:
            cursor = self._get_cursor()
            cursor.execute(sql, (str(geoentcod),))
            row = cursor.fetchone()
            if not row:
                return {}
            cols = [c[0] for c in cursor.description] if cursor.description else []
            return dict(zip(cols, row))
        except Exception as exc:
            self._registrar_log_erro_sql("carregar_dados_completos_entidade_geoapolo", sql, (geoentcod,), exc)
            return {}

    def obter_cpf_rg_documentos(self, geoentcod: str) -> Tuple[str, str]:
        """
        Obtém CPF/CNPJ e RG/IE cadastrados na tabela de documentos (USER_geoapolo_entidade_documentos).
        """
        sql = """
            SELECT geotipodocumento, geonumerodocumento
              FROM USER_geoapolo_entidade_documentos 
             WHERE geoentcod = ?
        """
        cpf, rg = "", ""
        try:
            cursor = self._get_cursor()
            cursor.execute(sql, (str(geoentcod),))
            for row in cursor.fetchall():
                tipo = str(row[0] or "").upper()
                num = str(row[1] or "").strip()
                if "CPF" in tipo or "CNPJ" in tipo:
                    if not cpf:
                        cpf = num
                elif "RG" in tipo or "IE" in tipo:
                    if not rg:
                        rg = num
            return cpf, rg
        except Exception as exc:
            self._registrar_log_erro_sql("obter_cpf_rg_documentos", sql, (geoentcod,), exc)
            return "", ""

    def carregar_contatos_entidade(self, geoentcod: str) -> List[Dict[str, Any]]:
        """
        Carrega os contatos vinculados à entidade (USER_geoapolo_entidade_contato).
        Equivalente à query de contatos do Delphi em unt_entidades.pas.
        """
        sql = """
            SELECT econt.EntCodContato, econt.entCod AS entcod_relacao, uge.entcod AS entcod_contato_alvo,
                   uge.geoentnome, uge.tipolograd, uge.geoentender,
                   uge.geoenderno, uge.geoentendercomp, uge.geoentbair, uge.geocidcod, uge.geoentcep,
                   uge.geotipofj, econt.EntContatoCelular, econt.EntContatoTelefone,
                   econt.CargoCodEstr, econt.data_vigencia_inicial, econt.data_vigencia_final,
                   COALESCE(ugc.geocargonome, econt.CargoCodEstr) AS geocargonome
              FROM USER_geoapolo_entidade_contato econt WITH (NOLOCK)
             INNER JOIN USER_geoapolo_entidade uge WITH (NOLOCK) ON econt.EntCodContato = uge.geoentcod
              LEFT JOIN USER_geoapolo_cargos ugc WITH (NOLOCK) ON econt.CargoCodEstr = ugc.geocargocodestr
             WHERE econt.geoentcod = ?
        """
        contatos = []
        try:
            cursor = self._get_cursor()
            cursor.execute(sql, (str(geoentcod),))
            cols = [c[0] for c in cursor.description] if cursor.description else []
            for row in cursor.fetchall():
                contatos.append(dict(zip(cols, row)))
            return contatos
        except Exception as exc:
            self._registrar_log_erro_sql("carregar_contatos_entidade", sql, (geoentcod,), exc)
            return []

    def obter_contatos_vinculados_geoentcod(self, geoentcod: str) -> List[Dict[str, Any]]:
        """Retorna lista de contatos vinculados à entidade em USER_geoapolo_entidade_contato."""
        sql = """
            SELECT econt.EntCodContato, econt.entCod AS entcod_relacao,
                   uge.geoentnome, uge.entcod AS entcod_contato_alvo
              FROM USER_geoapolo_entidade_contato econt WITH (NOLOCK)
             INNER JOIN USER_geoapolo_entidade uge WITH (NOLOCK) ON econt.EntCodContato = uge.geoentcod
             WHERE econt.geoentcod = ?
        """
        cursor = self._get_cursor()
        try:
            cursor.execute(sql, (str(geoentcod),))
            cols = [c[0] for c in cursor.description] if cursor.description else []
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as exc:
            self._registrar_log_erro_sql("obter_contatos_vinculados_geoentcod", sql, (geoentcod,), exc)
            return []

    def vincular_entcod_contato_relacao(self, geoentcod_pai: str, geoentcod_contato: str, entcod_alvo: str) -> bool:
        """Atualiza a coluna entCod na tabela USER_geoapolo_entidade_contato com o código do Alvo."""
        sql = """
            UPDATE USER_geoapolo_entidade_contato
               SET entCod = ?
             WHERE geoentcod = ? AND EntCodContato = ?
        """
        cursor = self._get_cursor()
        try:
            cursor.execute(sql, (str(entcod_alvo), str(geoentcod_pai), str(geoentcod_contato)))
            self._conn.commit()
            return True
        except Exception as exc:
            self._conn.rollback()
            self._registrar_log_erro_sql("vincular_entcod_contato_relacao", sql, (entcod_alvo, geoentcod_pai, geoentcod_contato), exc)
            return False

    def obter_entcod_entidade(self, geoentcod: str) -> Optional[str]:
        """Obtém o campo entcod da entidade no GeoApolo."""
        sql = "SELECT entcod FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE geoentcod = ?"
        cursor = self._get_cursor()
        try:
            cursor.execute(sql, (str(geoentcod),))
            row = cursor.fetchone()
            if row and row[0] and str(row[0]).strip():
                return str(row[0]).strip()
            return None
        except Exception as exc:
            self._registrar_log_erro_sql("obter_entcod_entidade", sql, (geoentcod,), exc)
            return None

    def _tabela_possui_coluna(self, nome_tabela: str, nome_coluna: str) -> bool:
        try:
            cursor = self._get_cursor()
            cursor.execute(f"SELECT * FROM {nome_tabela} WHERE 1=0")
            if cursor.description:
                cols = {desc[0].lower() for desc in cursor.description}
                return nome_coluna.lower() in cols
        except Exception:
            pass
        return False

    def obter_credenciais_alvo(self, cod_usuario: str) -> CredencialAlvo:
        if not self._tabela_possui_coluna("USER_geoapolo_usuarios", "senha_alvo"):
            return CredencialAlvo()

        sql = """
            SELECT usucod_apolo, senha_alvo 
              FROM USER_geoapolo_usuarios WITH (NOLOCK) 
             WHERE usucod = ?
        """
        try:
            cursor = self._get_cursor()
            cursor.execute(sql, (cod_usuario,))
            row = cursor.fetchone()
            if row:
                return CredencialAlvo(usuario_alvo=row[0] or "", senha_alvo_cripto=row[1] or "")
            return CredencialAlvo()
        except Exception as exc:
            self._registrar_log_erro_sql("obter_credenciais_alvo", sql, (cod_usuario,), exc)
            return CredencialAlvo()

    def salvar_credenciais_alvo(self, cod_usuario: str, usu_apolo: str, senha_cripto: str):
        if not self._tabela_possui_coluna("USER_geoapolo_usuarios", "senha_alvo"):
            logger.info("Tabela USER_geoapolo_usuarios sem coluna senha_alvo. Persistência ignorada.")
            return

        sql = """
            UPDATE USER_geoapolo_usuarios 
               SET usucod_apolo = ?, senha_alvo = ? 
             WHERE usucod = ?
        """
        try:
            cursor = self._get_cursor()
            cursor.execute(sql, (usu_apolo, senha_cripto, cod_usuario))
            self._conn.commit()
        except Exception as exc:
            self._conn.rollback()
            self._registrar_log_erro_sql("salvar_credenciais_alvo", sql, (usu_apolo, senha_cripto, cod_usuario), exc)
            raise

    def carregar_dados_comparacao(
        self, geoentcod: str, entcod: str = "", cpf: str = ""
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        cursor = self._get_cursor()
        
        # 1. SVE (GeoApolo)
        sve_dict = {}
        try:
            cursor.execute("SELECT * FROM entidades_geoapolo WITH (NOLOCK) WHERE geoentcod = ?", (geoentcod,))
            row_sve = cursor.fetchone()
            if row_sve:
                cols_sve = [c[0] for c in cursor.description] if cursor.description else []
                sve_dict = dict(zip(cols_sve, row_sve))
        except Exception as exc:
            self._registrar_log_erro_sql("carregar_dados_comparacao_sve", "SELECT * FROM entidades_geoapolo...", (geoentcod,), exc)
            sve_dict = {}

        if not sve_dict:
            try:
                cursor.execute("SELECT * FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE geoentcod = ?", (geoentcod,))
                row_sve = cursor.fetchone()
                if row_sve:
                    cols_sve = [c[0] for c in cursor.description] if cursor.description else []
                    sve_dict = dict(zip(cols_sve, row_sve))
            except Exception:
                pass

        # Garante CPF e RG na entidade SVE a partir da tabela de documentos
        cpf_doc, rg_doc = self.obter_cpf_rg_documentos(geoentcod)
        if cpf_doc:
            sve_dict["Documento"] = cpf_doc
            sve_dict["geonumerodocumento"] = cpf_doc
            sve_dict["EntCpfCgc"] = cpf_doc
            sve_dict["entcpfcgc"] = cpf_doc
            if not cpf:
                cpf = cpf_doc
        if rg_doc:
            sve_dict["EntRgIe"] = rg_doc
            sve_dict["geonumerorg"] = rg_doc

        if not entcod and sve_dict.get("entcod"):
            entcod = str(sve_dict.get("entcod") or "").strip()

        # 2. Alvo (entidades_apolo)
        alvo_dict = {}
        if entcod:
            try:
                cursor.execute("SELECT * FROM entidades_apolo WITH (NOLOCK) WHERE entcod = ?", (entcod,))
                row_alvo = cursor.fetchone()
                if not row_alvo:
                    cursor.execute("SELECT * FROM entidade WITH (NOLOCK) WHERE entcod = ?", (entcod,))
                    row_alvo = cursor.fetchone()
                if row_alvo:
                    cols_alvo = [c[0] for c in cursor.description] if cursor.description else []
                    alvo_dict = dict(zip(cols_alvo, row_alvo))
            except Exception as exc:
                self._registrar_log_erro_sql("carregar_dados_comparacao_alvo_entcod", "SELECT * FROM entidades_apolo...", (entcod,), exc)

        # Se não encontrou por entcod e temos CPF, busca por EntCpfCgc no Alvo
        if not alvo_dict and cpf:
            digitos_cpf = re.sub(r"\D", "", cpf)
            try:
                sql_cpf = """
                    SELECT TOP 1 * FROM entidades_apolo WITH (NOLOCK)
                     WHERE EntCpfCgc = ? 
                        OR REPLACE(REPLACE(REPLACE(ISNULL(EntCpfCgc,''), '.', ''), '-', ''), '/', '') = ?
                """
                cursor.execute(sql_cpf, (cpf, digitos_cpf))
                row_alvo = cursor.fetchone()
                if not row_alvo:
                    sql_cpf_fb = """
                        SELECT TOP 1 * FROM entidade WITH (NOLOCK)
                         WHERE EntCpfCgc = ? 
                            OR REPLACE(REPLACE(REPLACE(ISNULL(EntCpfCgc,''), '.', ''), '-', ''), '/', '') = ?
                    """
                    cursor.execute(sql_cpf_fb, (cpf, digitos_cpf))
                    row_alvo = cursor.fetchone()

                if row_alvo:
                    cols_alvo = [c[0] for c in cursor.description] if cursor.description else []
                    alvo_dict = dict(zip(cols_alvo, row_alvo))
                    novo_entcod = str(alvo_dict.get("entcod") or "").strip()
                    if novo_entcod and novo_entcod != entcod:
                        self.vincular_entcod(geoentcod, novo_entcod)
                        sve_dict["entcod"] = novo_entcod
            except Exception as exc:
                self._registrar_log_erro_sql("carregar_dados_comparacao_alvo_cpf", "SELECT * FROM entidades_apolo...", (cpf,), exc)

        return sve_dict, alvo_dict

    def gravar_entidade_geoapolo(self, dados: Dict[str, Any], modo_inclusao: bool = True) -> bool:
        """Persiste ou atualiza uma entidade na base GeoApolo."""
        try:
            cursor = self._get_cursor()
            if modo_inclusao:
                sql = """
                    INSERT INTO USER_geoapolo_entidade (
                        geoentcod, geotipotratcod, geoentnome, geoentnomefantasia, tipolograd,
                        geoentender, geoenderno, geoentendercomp, geoentbair, geoentdatacad,
                        geoentdesdedata, geoentcep, geocidcod, geoentcxapost, geoentgenero,
                        geolocalreferencia_ender, geotipofj, geofalecido, codigo_grauescolaridade,
                        geocargocodestr, geoentdataanivfund, geoentestcivil, entcod, cidcodapolo,
                        geoentrgie, geotipocobcod, geodia_contribuicao, geovalorcontribuicao,
                        geodioceseid, geobconum, geoagnum, geoconta,
                        geogerarcarne, georecebelembrete, geoentnomepai, geoentnomemae,
                        geoentmoracom, geoentpossuifilho, numerofilhos, geoentconceito,
                        georegcodestr, geoobservacoes
                    ) VALUES (
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?
                    )
                """
                params = (
                    _sanitizar_str(dados.get("geoentcod")),
                    _sanitizar_str(dados.get("geotipotratcod")),
                    _sanitizar_str(dados.get("geoentnome")),
                    _sanitizar_str(dados.get("geoentnomefantasia")),
                    _resolver_tipolograd(cursor, dados.get("tipolograd")),
                    _sanitizar_str(dados.get("geoentender")),
                    _sanitizar_str(dados.get("geoenderno")),
                    _sanitizar_str(dados.get("geoentendercomp")),
                    _sanitizar_str(dados.get("geoentbair")),
                    _sanitizar_data(dados.get("geoentdatacad")),
                    _sanitizar_data(dados.get("geoentdesdedata")),
                    _sanitizar_str(dados.get("geoentcep") or "")[:10] if (dados.get("geoentcep") or dados.get("entcep")) else None,
                    _sanitizar_str(dados.get("geocidcod")),
                    _sanitizar_str(dados.get("geoentcxapost")),
                    _sanitizar_str(dados.get("geoentgenero")),
                    _sanitizar_str(dados.get("geolocalreferencia_ender")),
                    _sanitizar_str(dados.get("geotipofj")),
                    "S" if str(dados.get("geofalecido", "N")).upper() in ("S", "SIM") else "N",
                    _resolver_grauescolaridade(cursor, dados.get("codigo_grauescolaridade") or dados.get("entgrauescol")),
                    _sanitizar_str(dados.get("geocargocodestr")),
                    _sanitizar_data(dados.get("geoentdataanivfund")),
                    _sanitizar_str(dados.get("geoentestcivil")),
                    _sanitizar_str(dados.get("entcod")),
                    _sanitizar_str(dados.get("cidcodapolo") or dados.get("geocidcod")),
                    _sanitizar_str(dados.get("geoentrgie") or dados.get("entrgie") or dados.get("EntRgIe")),
                    _sanitizar_str(dados.get("geotipocobcod") or dados.get("tipocobcod")),
                    _sanitizar_inteiro(dados.get("geodia_contribuicao") or dados.get("USERDia_Debito_CC")),
                    _sanitizar_float(dados.get("geovalorcontribuicao") or dados.get("USERValor_Contribuicao")),
                    _sanitizar_inteiro(dados.get("geodioceseid") or dados.get("USERDiocese_id")),
                    _sanitizar_str(dados.get("geobconum") or dados.get("bconum")),
                    _sanitizar_str(dados.get("geoagnum") or dados.get("agnum")),
                    _sanitizar_str(dados.get("geoconta") or dados.get("geoentcontacorrente") or dados.get("EntBcoAgCCorNum")),
                    "S" if str(dados.get("geogerarcarne")).upper() in ("SIM", "S") or str(dados.get("USERGeraCarne")).upper() in ("SIM", "S") else "N",
                    "S" if str(dados.get("georecebelembrete")).upper() in ("SIM", "S") or str(dados.get("USERRecebelembretedoacao")).upper() in ("SIM", "S") else "N",
                    _sanitizar_str(dados.get("geoentnomepai") or dados.get("entnomepai")),
                    _sanitizar_str(dados.get("geoentnomemae") or dados.get("entnomemae")),
                    _sanitizar_str(dados.get("geoentmoracom") or dados.get("entmoracom")),
                    _sanitizar_str(dados.get("geoentpossuifilho") or dados.get("entpossuifilho")),
                    _sanitizar_inteiro(dados.get("numerofilhos") or dados.get("quantosfilhos")),
                    _sanitizar_str(dados.get("geoentconceito") or dados.get("entconceito")),
                    _sanitizar_str(dados.get("georegcodestr") or dados.get("regcodestr")),
                    _sanitizar_obs(dados.get("geoobservacoes") or dados.get("Entobservacoes"), 200)
                )
            else:
                sql = """
                    UPDATE USER_geoapolo_entidade SET
                        geotipotratcod = ?, geoentnome = ?, geoentnomefantasia = ?,
                        tipolograd = ?, geoentender = ?, geoenderno = ?,
                        geoentendercomp = ?, geoentbair = ?, geoentdatacad = ?,
                        geoentcep = ?, geocidcod = ?, cidcodapolo = ?,
                        geoentcxapost = ?, geoentgenero = ?, geolocalreferencia_ender = ?,
                        geofalecido = ?, codigo_grauescolaridade = ?, geocargocodestr = ?,
                        geoentdataanivfund = ?, geoentestcivil = ?, entcod = ?,
                        geotipocobcod = ?, geodia_contribuicao = ?, geovalorcontribuicao = ?,
                        geodioceseid = ?, geobconum = ?, geoagnum = ?, geoconta = ?,
                        geogerarcarne = ?, georecebelembrete = ?, geoentrgie = ?,
                        geoentnomepai = ?, geoentnomemae = ?, geoentmoracom = ?,
                        geoentpossuifilho = ?, numerofilhos = ?, geoentconceito = ?,
                        georegcodestr = ?, geoobservacoes = ?
                    WHERE geoentcod = ?
                """
                params = (
                    _sanitizar_str(dados.get("geotipotratcod")),
                    _sanitizar_str(dados.get("geoentnome")),
                    _sanitizar_str(dados.get("geoentnomefantasia")),
                    _resolver_tipolograd(cursor, dados.get("tipolograd")),
                    _sanitizar_str(dados.get("geoentender")),
                    _sanitizar_str(dados.get("geoenderno")),
                    _sanitizar_str(dados.get("geoentendercomp")),
                    _sanitizar_str(dados.get("geoentbair")),
                    _sanitizar_data(dados.get("geoentdatacad")),
                    _sanitizar_str(dados.get("geoentcep") or "")[:10] if (dados.get("geoentcep") or dados.get("entcep")) else None,
                    _sanitizar_str(dados.get("geocidcod")),
                    _sanitizar_str(dados.get("cidcodapolo") or dados.get("geocidcod")),
                    _sanitizar_str(dados.get("geoentcxapost")),
                    _sanitizar_str(dados.get("geoentgenero")),
                    _sanitizar_str(dados.get("geolocalreferencia_ender")),
                    "S" if str(dados.get("geofalecido", "N")).upper() in ("S", "SIM") else "N",
                    _resolver_grauescolaridade(cursor, dados.get("codigo_grauescolaridade") or dados.get("entgrauescol")),
                    _sanitizar_str(dados.get("geocargocodestr")),
                    _sanitizar_data(dados.get("geoentdataanivfund")),
                    _sanitizar_str(dados.get("geoentestcivil")),
                    _sanitizar_str(dados.get("entcod")),
                    _sanitizar_str(dados.get("geotipocobcod") or dados.get("tipocobcod")),
                    _sanitizar_inteiro(dados.get("geodia_contribuicao") or dados.get("USERDia_Debito_CC")),
                    _sanitizar_float(dados.get("geovalorcontribuicao") or dados.get("USERValor_Contribuicao")),
                    _sanitizar_inteiro(dados.get("geodioceseid") or dados.get("USERDiocese_id")),
                    _sanitizar_str(dados.get("geobconum") or dados.get("bconum")),
                    _sanitizar_str(dados.get("geoagnum") or dados.get("agnum")),
                    _sanitizar_str(dados.get("geoconta") or dados.get("geoentcontacorrente") or dados.get("EntBcoAgCCorNum")),
                    "S" if str(dados.get("geogerarcarne")).upper() in ("SIM", "S") or str(dados.get("USERGeraCarne")).upper() in ("SIM", "S") else "N",
                    "S" if str(dados.get("georecebelembrete")).upper() in ("SIM", "S") or str(dados.get("USERRecebelembretedoacao")).upper() in ("SIM", "S") else "N",
                    _sanitizar_str(dados.get("geoentrgie") or dados.get("entrgie") or dados.get("EntRgIe")),
                    _sanitizar_str(dados.get("geoentnomepai") or dados.get("entnomepai")),
                    _sanitizar_str(dados.get("geoentnomemae") or dados.get("entnomemae")),
                    _sanitizar_str(dados.get("geoentmoracom") or dados.get("entmoracom")),
                    _sanitizar_str(dados.get("geoentpossuifilho") or dados.get("entpossuifilho")),
                    _sanitizar_inteiro(dados.get("numerofilhos") or dados.get("quantosfilhos")),
                    _sanitizar_str(dados.get("geoentconceito") or dados.get("entconceito")),
                    _sanitizar_str(dados.get("georegcodestr") or dados.get("regcodestr")),
                    _sanitizar_obs(dados.get("geoobservacoes") or dados.get("Entobservacoes"), 200),
                    _sanitizar_str(dados.get("geoentcod"))
                )
            cursor.execute(sql, params)

            # Persistência do Contato e Vigência (USER_geoapolo_entidade_contato)
            cod_ent = _sanitizar_str(dados.get("geoentcod"))
            contato_cod = _sanitizar_str(dados.get("geocontatocod") or dados.get("contatocod"))
            dt_ini = _sanitizar_data(dados.get("geodtiniciovigencia") or dados.get("dtiniciovigencia"))
            dt_fim = _sanitizar_data(dados.get("geodtfinalvigencia") or dados.get("dtfinalvigencia"))
            cargo = _sanitizar_str(dados.get("geocontatocargocod") or dados.get("contatocargocod") or dados.get("CargoCodEstr"))
            entcod_val = _sanitizar_str(dados.get("entcod"))

            if cod_ent and contato_cod:
                cursor.execute(
                    "SELECT 1 FROM USER_geoapolo_entidade_contato WITH (NOLOCK) WHERE geoentcod = ?",
                    (cod_ent,)
                )
                row_c = cursor.fetchone()
                if row_c:
                    cursor.execute("""
                        UPDATE USER_geoapolo_entidade_contato
                           SET EntCodContato = ?,
                               entCod = ?,
                               CargoCodEstr = ?,
                               data_vigencia_inicial = ?,
                               data_vigencia_final = ?
                         WHERE geoentcod = ?
                    """, (contato_cod, entcod_val, cargo, dt_ini, dt_fim, cod_ent))
                else:
                    cursor.execute("""
                        INSERT INTO USER_geoapolo_entidade_contato (
                            geoentcod, entCod, EntCodContato, CargoCodEstr,
                            data_vigencia_inicial, data_vigencia_final
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (cod_ent, entcod_val, contato_cod, cargo, dt_ini, dt_fim))
            elif cod_ent and (dt_ini or dt_fim):
                cursor.execute("""
                    UPDATE USER_geoapolo_entidade_contato
                       SET data_vigencia_inicial = ?,
                           data_vigencia_final = ?
                     WHERE geoentcod = ?
                """, (dt_ini, dt_fim, cod_ent))

            # Sincronização de Documentos (CPF e RG/IE em USER_geoapolo_entidade_documentos)
            rg_val = _sanitizar_str(dados.get("geoentrgie") or dados.get("entrgie") or dados.get("EntRgIe"))
            cpf_val = _sanitizar_str(dados.get("entcpfcgc") or dados.get("EntCpfCgc") or dados.get("Documento"))

            if cod_ent:
                if rg_val:
                    cursor.execute(
                        "SELECT 1 FROM USER_geoapolo_entidade_documentos WITH (NOLOCK) "
                        "WHERE geoentcod = ? AND (geotipodocumento = 'RG' OR geotipodocumento = 'RG/IE' OR geotipodocumento LIKE 'RG%')",
                        (cod_ent,)
                    )
                    if cursor.fetchone():
                        cursor.execute(
                            "UPDATE USER_geoapolo_entidade_documentos "
                            "   SET geonumerodocumento = ? "
                            " WHERE geoentcod = ? AND (geotipodocumento = 'RG' OR geotipodocumento = 'RG/IE' OR geotipodocumento LIKE 'RG%')",
                            (rg_val, cod_ent)
                        )
                    else:
                        cursor.execute(
                            "INSERT INTO USER_geoapolo_entidade_documentos (geoentcod, geotipodocumento, geonumerodocumento) "
                            "VALUES (?, 'RG/IE', ?)",
                            (cod_ent, rg_val)
                        )
                else:
                    cursor.execute(
                        "DELETE FROM USER_geoapolo_entidade_documentos "
                        " WHERE geoentcod = ? AND (geotipodocumento = 'RG' OR geotipodocumento = 'RG/IE' OR geotipodocumento LIKE 'RG%')",
                        (cod_ent,)
                    )

                if cpf_val:
                    cursor.execute(
                        "SELECT 1 FROM USER_geoapolo_entidade_documentos WITH (NOLOCK) "
                        "WHERE geoentcod = ? AND (geotipodocumento = 'CPF' OR geotipodocumento = 'CPF/CNPJ' OR geotipodocumento = 'CNPJ')",
                        (cod_ent,)
                    )
                    if cursor.fetchone():
                        cursor.execute(
                            "UPDATE USER_geoapolo_entidade_documentos "
                            "   SET geonumerodocumento = ? "
                            " WHERE geoentcod = ? AND (geotipodocumento = 'CPF' OR geotipodocumento = 'CPF/CNPJ' OR geotipodocumento = 'CNPJ')",
                            (cpf_val, cod_ent)
                        )
                    else:
                        cursor.execute(
                            "INSERT INTO USER_geoapolo_entidade_documentos (geoentcod, geotipodocumento, geonumerodocumento) "
                            "VALUES (?, 'CPF/CNPJ', ?)",
                            (cod_ent, cpf_val)
                        )

            # Sincronização de Origem (USER_geoapolo_origens_entidade)
            orig_cod = _sanitizar_str(dados.get("geo_origcodestr") or dados.get("origcodestr"))
            if cod_ent and orig_cod:
                cursor.execute("""
                    IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_origens_entidade WITH (NOLOCK) WHERE geoentcod = ?)
                    BEGIN
                        INSERT INTO USER_geoapolo_origens_entidade (geo_origcodestr, geoentcod)
                        VALUES (?, ?);
                    END
                    ELSE
                    BEGIN
                        UPDATE USER_geoapolo_origens_entidade
                        SET geo_origcodestr = ?
                        WHERE geoentcod = ?;
                    END;
                """, (cod_ent, orig_cod, cod_ent, orig_cod, cod_ent))
            elif cod_ent and ("geo_origcodestr" in dados or "origcodestr" in dados) and not orig_cod:
                cursor.execute("DELETE FROM USER_geoapolo_origens_entidade WHERE geoentcod = ?", (cod_ent,))

            # Sincronização de Telefones (USER_geoapolo_entidade_comunicacao)
            for tel in (dados.get("telefones") or []):
                if isinstance(tel, dict) and cod_ent and (tel.get("numero") or tel.get("geotelefonenumero")):
                    tel_dict = dict(tel)
                    if not tel_dict.get("numero") and tel_dict.get("geotelefonenumero"):
                        tel_dict["numero"] = tel_dict["geotelefonenumero"]
                    if not tel_dict.get("ddd") and tel_dict.get("geotelefoneddd"):
                        tel_dict["ddd"] = tel_dict["geotelefoneddd"]
                    try:
                        self.salvar_telefone_entidade(cod_ent, tel_dict, base_dados="GeoApolo")
                    except Exception as e_tel:
                        logger.warning("Falha ao sincronizar telefone %s: %s", tel_dict, e_tel)

            top_tel = dados.get("telefone") or dados.get("Telefone")
            if cod_ent and top_tel and not dados.get("telefones"):
                top_tel_limpo = re.sub(r"\D", "", str(top_tel))
                if len(top_tel_limpo) >= 8:
                    ddd = top_tel_limpo[:2] if len(top_tel_limpo) in (10, 11) else ""
                    num = top_tel_limpo[2:] if len(top_tel_limpo) in (10, 11) else top_tel_limpo
                    try:
                        self.salvar_telefone_entidade(cod_ent, {"numero": num, "ddd": ddd, "principal": "Sim"}, base_dados="GeoApolo")
                    except Exception as e_tel:
                        logger.warning("Falha ao sincronizar telefone principal %s: %s", top_tel, e_tel)

            # Sincronização de Webcontatos / E-mails (USER_geoapolo_entidade_webcontato)
            for web in (dados.get("webcontatos") or []):
                if isinstance(web, dict) and cod_ent and (web.get("email") or web.get("website")):
                    try:
                        self.salvar_webcontato_entidade(cod_ent, web, base_dados="GeoApolo")
                    except Exception as e_web:
                        logger.warning("Falha ao sincronizar webcontato %s: %s", web, e_web)

            top_email = dados.get("email") or dados.get("Email")
            if cod_ent and top_email and "@" in str(top_email) and not dados.get("webcontatos"):
                try:
                    self.salvar_webcontato_entidade(cod_ent, {"email": str(top_email).strip(), "principal": "Sim"}, base_dados="GeoApolo")
                except Exception as e_web:
                    logger.warning("Falha ao sincronizar email principal %s: %s", top_email, e_web)

            # Sincronização de Categorias (USER_geoapolo_entcateg)
            for cat in (dados.get("categorias") or []):
                cat_cod = cat.get("categcodestr") if isinstance(cat, dict) else str(cat)
                if cat_cod and cod_ent:
                    try:
                        self.adicionar_categoria_entidade(cod_ent, cat_cod, base_dados="GeoApolo")
                    except Exception as e_cat:
                        logger.warning("Falha ao associar categoria %s: %s", cat_cod, e_cat)

            # Endereço adicional de cobrança (se informado)
            if cod_ent and (dados.get("geocobender") or dados.get("cobender")):
                cob_ender = dados.get("geocobender") or dados.get("cobender")
                cob_no = dados.get("geocobenderno") or dados.get("cobenderno") or ""
                cob_comp = dados.get("geocobendercomp") or dados.get("cobendercomp") or ""
                cob_bair = dados.get("geocobbair") or dados.get("cobbair") or ""
                cob_cep = dados.get("geocobcep") or dados.get("cobcep") or ""
                cob_cid = dados.get("geocobcidcod") or dados.get("cobcidcod") or ""
                cob_log = dados.get("geocoblograd") or dados.get("coblograd") or ""
                try:
                    cursor.execute("""
                        IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_endereco_adicionais WITH (NOLOCK) WHERE geoentcod = ? AND tipo_endereco = 'Cobrança')
                        BEGIN
                            INSERT INTO USER_geoapolo_entidade_endereco_adicionais (geoentcod, tipo_endereco, tipologradabrev, endereco, numero, complemento, bairro, geocidcod, cep)
                            VALUES (?, 'Cobrança', ?, ?, ?, ?, ?, ?, ?);
                        END
                        ELSE
                        BEGIN
                            UPDATE USER_geoapolo_entidade_endereco_adicionais
                               SET tipologradabrev = ?, endereco = ?, numero = ?, complemento = ?, bairro = ?, geocidcod = ?, cep = ?
                             WHERE geoentcod = ? AND tipo_endereco = 'Cobrança';
                        END
                    """, (cod_ent, cod_ent, cob_log, cob_ender, cob_no, cob_comp, cob_bair, cob_cid, cob_cep,
                          cob_log, cob_ender, cob_no, cob_comp, cob_bair, cob_cid, cob_cep, cod_ent))
                except Exception as e_cob:
                    logger.warning("Falha ao salvar endereco de cobranca: %s", e_cob)

            # Endereço adicional de entrega (se informado)
            if cod_ent and (dados.get("geoentregaender") or dados.get("entregaender")):
                ent_ender = dados.get("geoentregaender") or dados.get("entregaender")
                ent_no = dados.get("geoentregaenderno") or dados.get("entregaenderno") or ""
                ent_comp = dados.get("geoentregaendercomp") or dados.get("entregaendercomp") or ""
                ent_bair = dados.get("geoentregabair") or dados.get("entregabair") or ""
                ent_cep = dados.get("geoentregacep") or dados.get("entregacep") or ""
                ent_cid = dados.get("geoentregacidcod") or dados.get("entregacidcod") or ""
                ent_log = dados.get("geoentregalograd") or dados.get("entregalograd") or ""
                try:
                    cursor.execute("""
                        IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_endereco_adicionais WITH (NOLOCK) WHERE geoentcod = ? AND tipo_endereco = 'Entrega')
                        BEGIN
                            INSERT INTO USER_geoapolo_entidade_endereco_adicionais (geoentcod, tipo_endereco, tipologradabrev, endereco, numero, complemento, bairro, geocidcod, cep)
                            VALUES (?, 'Entrega', ?, ?, ?, ?, ?, ?, ?);
                        END
                        ELSE
                        BEGIN
                            UPDATE USER_geoapolo_entidade_endereco_adicionais
                               SET tipologradabrev = ?, endereco = ?, numero = ?, complemento = ?, bairro = ?, geocidcod = ?, cep = ?
                             WHERE geoentcod = ? AND tipo_endereco = 'Entrega';
                        END
                    """, (cod_ent, cod_ent, ent_log, ent_ender, ent_no, ent_comp, ent_bair, ent_cid, ent_cep,
                          ent_log, ent_ender, ent_no, ent_comp, ent_bair, ent_cid, ent_cep, cod_ent))
                except Exception as e_ent:
                    logger.warning("Falha ao salvar endereco de entrega: %s", e_ent)

            self._conn.commit()
            return True
        except Exception as exc:
            self._conn.rollback()
            self._registrar_log_erro_sql("gravar_entidade_geoapolo", sql, params, exc)
            logger.exception("Erro ao salvar entidade no GeoApolo: %s", exc)
            raise

    def gravar_entidade_alvo(self, dados: Dict[str, Any]) -> bool:
        """Atualiza a entidade e tabelas de extensão na base Alvo."""
        cursor = self._get_cursor()
        try:
            sql = """
                UPDATE entidade SET
                    entnome = ?, tipotratcod = ?, entnomefant = ?,
                    entlograd = ?, entender = ?, entenderno = ?,
                    entendercomp = ?, entbair = ?, entcep = ?, cidcod = ?,
                    enttipofj = ?, entcxapost = ?, entgenero = ?,
                    cargocodestr = ?, entestcivil = ?, entgrauescol = ?,
                    entdataanivfund = ?, entdatacad = ?,
                    tipocobcod = ?, bconum = ?, agnum = ?, entbcoagccornum = ?,
                    entconceito = ?, regcodestr = ?, ativeconcodestr = ?, origcodestr = ?,
                    entnomepai = ?, entnomemae = ?, entmoracom = ?,
                    entpossuifilho = ?, quantosfilhos = ?, entobservacoes = ?,
                    entrgie = ?, EntCpfCgc = ?
                WHERE entcod = ?
            """
            params = (
                _sanitizar_str(dados.get("entnome")),
                _sanitizar_str(dados.get("tipotratcod")),
                _sanitizar_str(dados.get("entnomefant")),
                _sanitizar_str(dados.get("entlograd")),
                _sanitizar_str(dados.get("entender")),
                _sanitizar_str(dados.get("entenderno")),
                _sanitizar_str(dados.get("entendercomp")),
                _sanitizar_str(dados.get("entbair")),
                _sanitizar_str(dados.get("entcep")),
                _sanitizar_str(dados.get("cidcod")),
                _sanitizar_str(dados.get("enttipofj")),
                _sanitizar_str(dados.get("entcxapost")),
                _sanitizar_str(dados.get("entgenero")),
                _sanitizar_str(dados.get("cargocodestr")),
                _sanitizar_str(dados.get("entestcivil")),
                _sanitizar_str(dados.get("entgrauescol")),
                _sanitizar_data(dados.get("entdataanivfund")),
                _sanitizar_data(dados.get("entdatacad")),
                _sanitizar_str(dados.get("tipocobcod")),
                _sanitizar_str(dados.get("bconum")),
                _sanitizar_str(dados.get("agnum")),
                _sanitizar_str(dados.get("EntBcoAgCCorNum") or dados.get("geoentcontacorrente")),
                _sanitizar_str(dados.get("entconceito")),
                _sanitizar_str(dados.get("regcodestr")),
                _sanitizar_str(dados.get("ativeconcodestr")),
                _sanitizar_str(dados.get("origcodestr")),
                _sanitizar_str(dados.get("entnomepai")),
                _sanitizar_str(dados.get("entnomemae")),
                _sanitizar_str(dados.get("entmoracom")),
                _sanitizar_str(dados.get("entpossuifilho")),
                _sanitizar_inteiro(dados.get("quantosfilhos") or dados.get("numerofilhos")),
                _sanitizar_str(dados.get("Entobservacoes") or dados.get("geoobservacoes")),
                _sanitizar_str(dados.get("entrgie") or dados.get("EntRgIe") or dados.get("geoentrgie")),
                _sanitizar_str(dados.get("EntCpfCgc") or dados.get("entcpfcgc") or dados.get("Documento")),
                _sanitizar_str(dados.get("entcod"))
            )
            cursor.execute(sql, params)

            # Atualiza u_entidade
            sql_u = """
                UPDATE u_entidade SET
                    USERFalecido = ?,
                    USERDia_Debito_CC = ?,
                    USERDiocese_id = ?,
                    USERNomeDiocese = ?,
                    USERGeraCarne = ?,
                    USERrecebelembretedoacao = ?,
                    USERValor_Contribuicao = ?
                WHERE entcod = ?
            """
            params_u = (
                "Sim" if str(dados.get("USERFalecido", "Não")).upper() in ("S", "SIM") else "Não",
                _sanitizar_inteiro(dados.get("USERDia_Debito_CC") or dados.get("geodia_contribuicao")),
                _sanitizar_inteiro(dados.get("USERDiocese_id") or dados.get("geodioceseid")),
                _sanitizar_str(dados.get("USERNomeDiocese")),
                "Sim" if str(dados.get("USERGeraCarne", "Não")).upper() in ("SIM", "S") else "Não",
                "Sim" if str(dados.get("USERrecebelembretedoacao", "Não")).upper() in ("SIM", "S") else "Não",
                _sanitizar_float(dados.get("USERValor_Contribuicao") or dados.get("geovalorcontribuicao")),
                _sanitizar_str(dados.get("entcod"))
            )
            cursor.execute(sql_u, params_u)
            self.atualizar_log_entidade_apolo(dados.get("entcod"))
            self._conn.commit()
            return True
        except Exception as exc:
            self._conn.rollback()
            self._registrar_log_erro_sql("gravar_entidade_alvo", sql, params, exc)
            logger.exception("Erro ao salvar entidade no Alvo: %s", exc)
            raise

    def aplicar_sobreposicao_alvo_local(self, entcod: str, dados_sobreposicao: Dict[str, Any]) -> bool:
        """
        Aplica na tabela entidade (Alvo local) as decisões tomadas pelo operador na conferência/sobreposição.
        Garante que o banco de dados local reflita imediatamente os campos atualizados no Alvo.
        """
        if not entcod or not dados_sobreposicao:
            return False
        cursor = self._get_cursor()
        campos_upd = []
        params = []

        cod_cidade = dados_sobreposicao.get("CodigoCidade") or dados_sobreposicao.get("cidcod")
        if cod_cidade:
            campos_upd.append("cidcod = ?")
            params.append(str(cod_cidade).strip())

        if "Nome" in dados_sobreposicao and dados_sobreposicao["Nome"]:
            campos_upd.append("entnome = ?")
            params.append(str(dados_sobreposicao["Nome"]).strip())

        if "Endereco" in dados_sobreposicao and dados_sobreposicao["Endereco"]:
            campos_upd.append("entender = ?")
            params.append(str(dados_sobreposicao["Endereco"]).strip())

        if "NumeroEndereco" in dados_sobreposicao:
            campos_upd.append("entenderno = ?")
            params.append(str(dados_sobreposicao["NumeroEndereco"] or "").strip())

        if "ComplementoEndereco" in dados_sobreposicao:
            campos_upd.append("entendercomp = ?")
            params.append(str(dados_sobreposicao["ComplementoEndereco"] or "").strip())

        if "Bairro" in dados_sobreposicao and dados_sobreposicao["Bairro"]:
            campos_upd.append("entbair = ?")
            params.append(str(dados_sobreposicao["Bairro"]).strip())

        if "Cep" in dados_sobreposicao and dados_sobreposicao["Cep"]:
            campos_upd.append("entcep = ?")
            params.append(str(dados_sobreposicao["Cep"]).strip())

        if "CPFCNPJ" in dados_sobreposicao and dados_sobreposicao["CPFCNPJ"]:
            campos_upd.append("EntCpfCgc = ?")
            params.append(str(dados_sobreposicao["CPFCNPJ"]).strip())

        if "RGIE" in dados_sobreposicao and dados_sobreposicao["RGIE"]:
            campos_upd.append("entrgie = ?")
            params.append(str(dados_sobreposicao["RGIE"]).strip())

        if "DataFundacao" in dados_sobreposicao and dados_sobreposicao["DataFundacao"]:
            campos_upd.append("entdataanivfund = ?")
            params.append(str(dados_sobreposicao["DataFundacao"]).strip())

        if "Genero" in dados_sobreposicao and dados_sobreposicao["Genero"]:
            campos_upd.append("entgenero = ?")
            params.append("F" if str(dados_sobreposicao["Genero"]).upper().startswith("F") else "M")

        if "CodigoTipoLograd" in dados_sobreposicao and dados_sobreposicao["CodigoTipoLograd"]:
            campos_upd.append("entlograd = ?")
            params.append(str(dados_sobreposicao["CodigoTipoLograd"]).strip())

        if not campos_upd:
            return False

        try:
            sql = f"UPDATE entidade SET {', '.join(campos_upd)} WHERE entcod = ?"
            params.append(str(entcod).strip())
            cursor.execute(sql, tuple(params))
            self._conn.commit()
            logger.info("Sobreposição aplicada localmente na entidade %s: %s", entcod, campos_upd)
            return True
        except Exception as exc:
            self._conn.rollback()
            self._registrar_log_erro_sql("aplicar_sobreposicao_alvo_local", sql, tuple(params), exc)
            logger.warning("Falha ao aplicar sobreposição local na entidade %s: %s", entcod, exc)
            return False

    def atualizar_log_entidade_apolo(self, entcod: str):
        """Atualiza carimbo de alteração na base Alvo."""
        try:
            cursor = self._get_cursor()
            cursor.execute("UPDATE entidade SET EntDataAlt = GETDATE() WHERE entcod = ?", (entcod,))
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # Categorias
    # -------------------------------------------------------------------------
    def listar_categorias_entidade(self, entcod: str, base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        """Retorna lista de categorias vinculadas à entidade."""
        if not entcod:
            return []
        cursor = self._get_cursor()
        sql = ""
        try:
            if base_dados == "GeoApolo":
                sql = """
                    SELECT gc.geocategcodestr AS codigo, gc.geocategnome AS descricao
                      FROM USER_geoapolo_entidade ge 
                     INNER JOIN USER_geoapolo_entcateg gec  ON ge.geoentcod = gec.geoentcod
                     INNER JOIN USER_geoapolo_categoria gc  ON gc.geocategcodestr = gec.geocategcodestr
                     WHERE gec.geoentcod = ?
                """
            else:
                sql = """
                    SELECT cat.categcodestr AS codigo, cat.categnome AS descricao
                      FROM entidade e 
                     INNER JOIN ent_categ ec  ON e.entcod = ec.entcod
                     INNER JOIN categoria cat ON ec.categcodestr = cat.categcodestr
                     WHERE ec.entcod = ?
                """
            cursor.execute(sql, (entcod,))
            cols = [col[0].lower() for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as exc:
            self._registrar_log_erro_sql("listar_categorias_entidade", sql, (entcod,), exc)
            logger.warning("Falha ao listar categorias da entidade %s: %s", entcod, exc)
            return []

    def adicionar_categoria_entidade(self, entcod: str, categcodestr: str, base_dados: str = "GeoApolo") -> bool:
        """Vincula categoria à entidade."""
        if not entcod or not categcodestr:
            return False
        cursor = self._get_cursor()
        try:
            if base_dados == "GeoApolo":
                cursor.execute(
                    "SELECT 1 FROM USER_geoapolo_entcateg WHERE geoentcod = ? AND geocategcodestr = ?",
                    (entcod, categcodestr)
                )
                if cursor.fetchone():
                    return False
                cursor.execute(
                    "INSERT INTO USER_geoapolo_entcateg (geoentcod, geocategcodestr) VALUES (?, ?)",
                    (entcod, categcodestr)
                )
            else:
                cursor.execute(
                    "SELECT 1 FROM ent_categ WHERE entcod = ? AND categcodestr = ?",
                    (entcod, categcodestr)
                )
                if cursor.fetchone():
                    return False
                cursor.execute(
                    "INSERT INTO ent_categ (entcod, categcodestr, entcategativatabpv) VALUES (?, ?, 'Não')",
                    (entcod, categcodestr)
                )
            self._conn.commit()
            return True
        except Exception as exc:
            self._conn.rollback()
            self._registrar_log_erro_sql("adicionar_categoria_entidade", "INSERT entcateg...", (entcod, categcodestr), exc)
            logger.exception("Erro ao vincular categoria %s à entidade %s: %s", categcodestr, entcod, exc)
            raise

    def remover_categoria_entidade(self, entcod: str, categcodestr: str, base_dados: str = "GeoApolo") -> bool:
        """Desvincula categoria da entidade."""
        if not entcod or not categcodestr:
            return False
        cursor = self._get_cursor()
        try:
            if base_dados == "GeoApolo":
                cursor.execute(
                    "DELETE FROM USER_geoapolo_entcateg WHERE geoentcod = ? AND geocategcodestr = ?",
                    (entcod, categcodestr)
                )
            else:
                cursor.execute(
                    "DELETE FROM ent_categ WHERE entcod = ? AND categcodestr = ?",
                    (entcod, categcodestr)
                )
            self._conn.commit()
            return True
        except Exception as exc:
            self._conn.rollback()
            self._registrar_log_erro_sql("remover_categoria_entidade", "DELETE entcateg...", (entcod, categcodestr), exc)
            logger.exception("Erro ao remover categoria %s da entidade %s: %s", categcodestr, entcod, exc)
            raise

    # -------------------------------------------------------------------------
    # Telefones & Comunicação
    # -------------------------------------------------------------------------
    def listar_telefones_entidade(self, entcod: str, base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        """Retorna lista de telefones cadastrados para a entidade."""
        if not entcod:
            return []
        cursor = self._get_cursor()
        sql = ""
        try:
            if base_dados == "GeoApolo":
                sql = """
                    SELECT gec.geotelefoneddi AS ddi, gec.geotelefoneddd AS ddd, gec.geotelefonenumero AS numero,
                           gec.geotelefoneramal AS ramal, gec.geotipotelefone AS tipotelefone,
                           gec.flagtelprincipal AS principal
                      FROM USER_geoapolo_entidade_comunicacao gec 
                     WHERE gec.geoentcod = ?
                """
            else:
                sql = """
                    SELECT ef.entfoneddi AS ddi, ef.EntFoneDDD AS ddd, ef.EntFoneNum AS numero,
                           ef.EntFoneRamalBip AS ramal, ef.EntFoneTipo AS tipotelefone,
                           ef.EntFonePrinc AS principal
                      FROM ent_fone ef 
                     WHERE ef.entcod = ?
                """
            cursor.execute(sql, (entcod,))
            cols = [col[0].lower() for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as exc:
            self._registrar_log_erro_sql("listar_telefones_entidade", sql, (entcod,), exc)
            logger.warning("Falha ao listar telefones da entidade %s: %s", entcod, exc)
            return []

    def salvar_telefone_entidade(self, entcod: str, dados_tel: Dict[str, Any], base_dados: str = "GeoApolo") -> bool:
        """Insere ou atualiza um registro telefônico da entidade."""
        if not entcod or not dados_tel.get("numero"):
            return False
        cursor = self._get_cursor()
        numero = str(dados_tel.get("numero", "")).strip()
        ddd = str(dados_tel.get("ddd", "")).strip()
        ddi = str(dados_tel.get("ddi", "55")).strip()
        ramal = str(dados_tel.get("ramal", "")).strip()
        tipo = str(dados_tel.get("tipotelefone") or dados_tel.get("tipo", "Celular")).strip()
        princ = "Sim" if str(dados_tel.get("principal", "")).lower() in ("sim", "s", "true", "1") else "Não"

        try:
            if base_dados == "GeoApolo":
                cursor.execute(
                    "SELECT 1 FROM USER_geoapolo_entidade_comunicacao WHERE geoentcod = ? AND geotelefonenumero = ?",
                    (entcod, numero)
                )
                if cursor.fetchone():
                    cursor.execute("""
                        UPDATE USER_geoapolo_entidade_comunicacao
                           SET geotipotelefone = ?, geotelefoneddi = ?, geotelefoneddd = ?,
                               geotelefoneramal = ?, flagtelprincipal = ?
                         WHERE geoentcod = ? AND geotelefonenumero = ?
                    """, (tipo, ddi, ddd, ramal, princ, entcod, numero))
                else:
                    cursor.execute("""
                        INSERT INTO USER_geoapolo_entidade_comunicacao
                            (geoentcod, geotipotelefone, geotelefoneddi, geotelefoneddd, geotelefonenumero, geotelefoneramal, flagtelprincipal)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (entcod, tipo, ddi, ddd, numero, ramal, princ))
            else:
                cursor.execute("SELECT 1 FROM ent_fone WHERE entcod = ? AND entfonenum = ?", (entcod, numero))
                if cursor.fetchone():
                    cursor.execute("""
                        UPDATE ent_fone
                           SET entfonetipo = ?, entfoneddi = ?, entfoneddd = ?,
                               entfoneramalbipnum = ?, entfoneprinc = ?, entfonedthrcad = GETDATE()
                         WHERE entcod = ? AND entfonenum = ?
                    """, (tipo, ddi, ddd, ramal, princ, entcod, numero))
                else:
                    cursor.execute("SELECT COALESCE(MAX(entfoneseq), 0) + 1 FROM ent_fone  WHERE entcod = ?", (entcod,))
                    row_seq = cursor.fetchone()
                    seq = row_seq[0] if row_seq else 1
                    cursor.execute("""
                        INSERT INTO ent_fone
                            (entcod, entfoneseq, entfonetipo, entfoneddi, entfoneddd, entfonenum, entfoneramalbipnum, entfoneprinc, entfonedthrcad)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
                    """, (entcod, seq, tipo, ddi, ddd, numero, ramal, princ))
                self.atualizar_log_entidade_apolo(entcod)
            self._conn.commit()
            return True
        except Exception as exc:
            self._conn.rollback()
            self._registrar_log_erro_sql("salvar_telefone_entidade", "salvar_telefone", (entcod, dados_tel), exc)
            logger.exception("Erro ao salvar telefone para entidade %s: %s", entcod, exc)
            raise

    def remover_telefone_entidade(self, entcod: str, numero: str, base_dados: str = "GeoApolo") -> bool:
        """Exclui um telefone vinculado à entidade."""
        if not entcod or not numero:
            return False
        cursor = self._get_cursor()
        try:
            if base_dados == "GeoApolo":
                cursor.execute(
                    "DELETE FROM USER_geoapolo_entidade_comunicacao WHERE geoentcod = ? AND geotelefonenumero = ?",
                    (entcod, numero)
                )
            else:
                cursor.execute(
                    "DELETE FROM ent_fone WHERE entcod = ? AND entfonenum = ?",
                    (entcod, numero)
                )
                self.atualizar_log_entidade_apolo(entcod)
            self._conn.commit()
            return True
        except Exception as exc:
            self._conn.rollback()
            self._registrar_log_erro_sql("remover_telefone_entidade", "DELETE fone...", (entcod, numero), exc)
            logger.exception("Erro ao remover telefone %s da entidade %s: %s", numero, entcod, exc)
            raise

    # -------------------------------------------------------------------------
    # Comunicação Web & E-mails
    # -------------------------------------------------------------------------
    def listar_webcontatos_entidade(self, entcod: str, base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        """Retorna lista de e-mails / contatos web da entidade."""
        if not entcod:
            return []
        cursor = self._get_cursor()
        sql = ""
        try:
            if base_dados == "GeoApolo":
                sql = """
                    SELECT tipo_contato, email, website, comunicador_instantaneo,
                           endereco_comunicador, flagemailprincipal AS principal
                      FROM USER_geoapolo_entidade_webcontato 
                     WHERE geoentcod = ?
                """
            else:
                sql = """
                    SELECT ew.entwebtipo AS tipo_contato, ew.EntWebEMail AS email,
                           ew.entwebwww AS website, '' AS comunicador_instantaneo,
                           '' AS endereco_comunicador, ew.entwebemailprinc AS principal
                      FROM ent_web ew 
                     WHERE ew.entcod = ?
                """
            cursor.execute(sql, (entcod,))
            cols = [col[0].lower() for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as exc:
            self._registrar_log_erro_sql("listar_webcontatos_entidade", sql, (entcod,), exc)
            logger.warning("Falha ao listar contatos web da entidade %s: %s", entcod, exc)
            return []

    def salvar_webcontato_entidade(self, entcod: str, dados_web: Dict[str, Any], base_dados: str = "GeoApolo") -> bool:
        """Insere ou atualiza e-mail / contato web."""
        if not entcod or not dados_web.get("email"):
            return False
        cursor = self._get_cursor()
        email = str(dados_web.get("email", "")).strip()
        tipo = str(dados_web.get("tipo_contato", "Pessoal")).strip()
        website = str(dados_web.get("website", "")).strip()
        comunicador = str(dados_web.get("comunicador_instantaneo", "")).strip()
        end_comunicador = str(dados_web.get("endereco_comunicador", "")).strip()
        princ = "Sim" if str(dados_web.get("principal", "")).lower() in ("sim", "s", "true", "1") else "Não"

        try:
            if base_dados == "GeoApolo":
                cursor.execute(
                    "SELECT 1 FROM USER_geoapolo_entidade_webcontato  WHERE geoentcod = ? AND email = ?",
                    (entcod, email)
                )
                if cursor.fetchone():
                    cursor.execute("""
                        UPDATE USER_geoapolo_entidade_webcontato
                           SET tipo_contato = ?, website = ?, comunicador_instantaneo = ?,
                               endereco_comunicador = ?, flagemailprincipal = ?
                         WHERE geoentcod = ? AND email = ?
                    """, (tipo, website, comunicador, end_comunicador, princ, entcod, email))
                else:
                    cursor.execute("""
                        INSERT INTO USER_geoapolo_entidade_webcontato
                            (geoentcod, tipo_contato, website, email, flagemailprincipal, comunicador_instantaneo, endereco_comunicador)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (entcod, tipo, website, email, princ, comunicador, end_comunicador))
            else:
                cursor.execute("SELECT 1 FROM ent_web WHERE entcod = ? AND entwebemail = ?", (entcod, email))
                if cursor.fetchone():
                    cursor.execute("""
                        UPDATE ent_web
                           SET entwebtipo = ?, entwebwww = ?, entwebemailprinc = ?
                         WHERE entcod = ? AND entwebemail = ?
                    """, (tipo, website, princ, entcod, email))
                else:
                    cursor.execute("SELECT COALESCE(MAX(entwebseq), 0) + 1 FROM ent_web WHERE entcod = ?", (entcod,))
                    row_seq = cursor.fetchone()
                    seq = row_seq[0] if row_seq else 1
                    cursor.execute("""
                        INSERT INTO ent_web
                            (entcod, entwebseq, entwebtipo, entwebemail, entwebwww, entwebemailprinc)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (entcod, seq, tipo, email, website, princ))
                self.atualizar_log_entidade_apolo(entcod)
            self._conn.commit()
            return True
        except Exception as exc:
            self._conn.rollback()
            self._registrar_log_erro_sql("salvar_webcontato_entidade", "salvar_web", (entcod, dados_web), exc)
            logger.exception("Erro ao salvar contato web para entidade %s: %s", entcod, exc)
            raise

    def remover_webcontato_entidade(self, entcod: str, email: str, base_dados: str = "GeoApolo") -> bool:
        """Exclui contato web da entidade."""
        if not entcod or not email:
            return False
        cursor = self._get_cursor()
        try:
            if base_dados == "GeoApolo":
                cursor.execute(
                    "DELETE FROM USER_geoapolo_entidade_webcontato WHERE geoentcod = ? AND email = ?",
                    (entcod, email)
                )
            else:
                cursor.execute(
                    "DELETE FROM ent_web WHERE entcod = ? AND entwebemail = ?",
                    (entcod, email)
                )
                self.atualizar_log_entidade_apolo(entcod)
            self._conn.commit()
            return True
        except Exception as exc:
            self._conn.rollback()
            self._registrar_log_erro_sql("remover_webcontato_entidade", "DELETE web...", (entcod, email), exc)
            logger.exception("Erro ao remover contato web %s da entidade %s: %s", email, entcod, exc)
            raise

    # -------------------------------------------------------------------------
    # Documentos
    # -------------------------------------------------------------------------
    def listar_documentos_entidade(self, entcod: str, base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        """Retorna lista de documentos da entidade."""
        if not entcod:
            return []
        cursor = self._get_cursor()
        sql = ""
        try:
            if base_dados == "GeoApolo":
                sql = """
                    SELECT uged.geotipodocumento AS tipo, uged.geonumerodocumento AS documento,
                           uged.geoobservacoes AS observacoes
                      FROM USER_geoapolo_entidade_documentos uged WITH (NOLOCK)
                     WHERE uged.geoentcod = ?
                """
            else:
                sql = """
                    SELECT v.Tipo AS tipo, v.Documento AS documento, '' AS observacoes
                      FROM ENTIDADE e WITH (NOLOCK)
                     CROSS APPLY (VALUES (e.EntCpfCgc, 'CPF/CNPJ'), (e.entrgie, 'RG/IE')) v(Documento, Tipo)
                     WHERE e.entcod = ? AND v.Documento IS NOT NULL AND RTRIM(v.Documento) <> ''
                """
            cursor.execute(sql, (entcod,))
            cols = [col[0].lower() for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as exc:
            self._registrar_log_erro_sql("listar_documentos_entidade", sql, (entcod,), exc)
            logger.warning("Falha ao listar documentos da entidade %s: %s", entcod, exc)
            return []

    def salvar_documento_entidade(self, entcod: str, tipo: str, documento: str, observacoes: str = "", base_dados: str = "GeoApolo") -> bool:
        """Adiciona ou atualiza documento da entidade."""
        if not entcod or not documento or not tipo:
            return False
        cursor = self._get_cursor()
        try:
            if base_dados == "GeoApolo":
                cursor.execute("""
                    SELECT 1 FROM USER_geoapolo_entidade_documentos WITH (NOLOCK)
                     WHERE geoentcod = ? AND geonumerodocumento = ?
                """, (entcod, documento))
                if cursor.fetchone():
                    cursor.execute("""
                        UPDATE USER_geoapolo_entidade_documentos
                           SET geonumerodocumento = ?, geoobservacoes = ?
                         WHERE geoentcod = ? AND geotipodocumento = ?
                    """, (documento, observacoes, entcod, tipo))
                else:
                    cursor.execute("""
                        INSERT INTO USER_geoapolo_entidade_documentos
                            (geoentcod, geotipodocumento, geonumerodocumento, geoobservacoes)
                        VALUES (?, ?, ?, ?)
                    """, (entcod, tipo, documento, observacoes))
            else:
                if "CPF" in tipo.upper() or "CNPJ" in tipo.upper():
                    cursor.execute("UPDATE entidade SET EntCpfCgc = ? WHERE entcod = ?", (documento, entcod))
                elif "RG" in tipo.upper() or "IE" in tipo.upper():
                    cursor.execute("UPDATE entidade SET entrgie = ? WHERE entcod = ?", (documento, entcod))
                self.atualizar_log_entidade_apolo(entcod)
            self._conn.commit()
            return True
        except Exception as exc:
            self._conn.rollback()
            self._registrar_log_erro_sql("salvar_documento_entidade", "salvar_documento", (entcod, tipo, documento), exc)
            logger.exception("Erro ao salvar documento %s para entidade %s: %s", documento, entcod, exc)
            raise

    def remover_documento_entidade(self, entcod: str, tipo: str, documento: str, base_dados: str = "GeoApolo") -> bool:
        """Remove documento da entidade."""
        if not entcod or not documento:
            return False
        cursor = self._get_cursor()
        try:
            if base_dados == "GeoApolo":
                cursor.execute("""
                    DELETE FROM USER_geoapolo_entidade_documentos
                     WHERE geoentcod = ? AND geotipodocumento = ? AND geonumerodocumento = ?
                """, (entcod, tipo, documento))
            else:
                if "CPF" in tipo.upper() or "CNPJ" in tipo.upper():
                    cursor.execute("UPDATE entidade SET EntCpfCgc = NULL WHERE entcod = ?", (entcod,))
                elif "RG" in tipo.upper() or "IE" in tipo.upper():
                    cursor.execute("UPDATE entidade SET entrgie = NULL WHERE entcod = ?", (entcod,))
                self.atualizar_log_entidade_apolo(entcod)
            self._conn.commit()
            return True
        except Exception as exc:
            self._conn.rollback()
            self._registrar_log_erro_sql("remover_documento_entidade", "DELETE doc...", (entcod, tipo, documento), exc)
            logger.exception("Erro ao remover documento %s da entidade %s: %s", documento, entcod, exc)
            raise

    # -------------------------------------------------------------------------
    # Lookups / Consultas Auxiliares
    # -------------------------------------------------------------------------
    def listar_entidades_lookup(self, termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        """Retorna lista de entidades para seleção de contatos/responsáveis."""
        cursor = self._get_cursor()
        termo_limpo = (termo or "").strip()
        filtro = f"%{termo_limpo}%" if termo_limpo else "%"
        if base_dados == "Alvo":
            sql = """
                SELECT TOP 100 entcod AS codigo, entnome AS nome, ISNULL(EntCpfCgc, '') AS documento
                  FROM entidade WITH (NOLOCK)
                 WHERE (entnome LIKE ? OR entcod LIKE ? OR EntCpfCgc LIKE ?)
                 ORDER BY entnome ASC
            """
            params = (filtro, filtro, filtro)
        else:
            sql = """
                SELECT TOP 100 geoentcod AS codigo, geoentnome AS nome, ISNULL(geotipofj, 'Física') AS tipo
                  FROM USER_geoapolo_entidade WITH (NOLOCK)
                 WHERE (geoentnome LIKE ? OR geoentcod LIKE ?)
                 ORDER BY geoentnome ASC
            """
            params = (filtro, filtro)
        try:
            cursor.execute(sql, params)
            cols = [c[0] for c in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as exc:
            self._registrar_log_erro_sql("listar_entidades_lookup", sql, params, exc)
            return []

    def listar_cidades(self, termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        """Retorna lista de cidades para seleção em lookups."""
        cursor = self._get_cursor()
        filtro = f"%{termo.strip()}%"
        try:
            if base_dados == "GeoApolo":
                sql = """
                    SELECT geocidcod AS codigo, cidnomecomp AS nome, ufsigla AS uf
                      FROM USER_geoapolo_cidades WITH (NOLOCK)
                     WHERE geocidcod LIKE ? OR cidnomecomp LIKE ? OR ufsigla LIKE ?
                     ORDER BY cidnomecomp ASC
                """
            else:
                sql = """
                    SELECT cidcod AS codigo, cidnomecomp AS nome, ufsigla AS uf
                      FROM CIDADE WITH (NOLOCK)
                     WHERE cidcod LIKE ? OR cidnomecomp LIKE ? OR ufsigla LIKE ?
                     ORDER BY cidnomecomp ASC
                """
            cursor.execute(sql, (filtro, filtro, filtro))
            cols = [col[0].lower() for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as exc:
            self._registrar_log_erro_sql("listar_cidades", "SELECT cidades", (filtro,), exc)
            logger.warning("Falha ao listar cidades: %s", exc)
            return []

    def obter_cidade_por_codigo(self, cidcod: str, base_dados: str = "GeoApolo") -> Optional[Dict[str, Any]]:
        """Busca uma cidade pelo seu código."""
        if not cidcod:
            return None
        cursor = self._get_cursor()
        val = str(cidcod).strip()
        try:
            if base_dados == "GeoApolo":
                sql = """
                    SELECT geocidcod AS codigo, cidnomecomp AS nome, ufsigla AS uf
                      FROM USER_geoapolo_cidades WITH (NOLOCK)
                     WHERE geocidcod = ?
                """
            else:
                sql = """
                    SELECT cidcod AS codigo, cidnomecomp AS nome, ufsigla AS uf
                      FROM CIDADE WITH (NOLOCK)
                     WHERE cidcod = ?
                """
            cursor.execute(sql, (val,))
            row = cursor.fetchone()
            if not row and base_dados != "GeoApolo":
                try:
                    cursor.execute("SELECT geocidcod AS codigo, cidnomecomp AS nome, ufsigla AS uf FROM USER_geoapolo_cidades WITH (NOLOCK) WHERE geocidcod = ?", (val,))
                    row = cursor.fetchone()
                except Exception:
                    pass
            elif not row and base_dados == "GeoApolo":
                try:
                    cursor.execute("SELECT cidcod AS codigo, cidnomecomp AS nome, ufsigla AS uf FROM CIDADE WITH (NOLOCK) WHERE cidcod = ?", (val,))
                    row = cursor.fetchone()
                except Exception:
                    pass
            if row:
                return {"codigo": str(row[0]), "nome": str(row[1] or ""), "uf": str(row[2] or "")}
            return None
        except Exception as exc:
            self._registrar_log_erro_sql("obter_cidade_por_codigo", "SELECT cidade por codigo", (val,), exc)
            return None

    def obter_cidade_por_nome_uf(self, nome: str, uf: str, base_dados: str = "GeoApolo") -> Optional[Dict[str, Any]]:
        """Busca a cidade e seu código a partir do nome e UF."""
        if not nome or not uf:
            return None
        cursor = self._get_cursor()
        nm = str(nome).strip()
        u = str(uf).strip()
        try:
            sql = """
                SELECT TOP 1 geocidcod AS codigo, cidnomecomp AS nome, ufsigla AS uf
                  FROM USER_geoapolo_cidades WITH (NOLOCK)
                 WHERE (cidnomecomp = ? OR cidnomecomp LIKE ?) AND ufsigla = ?
            """
            cursor.execute(sql, (nm, f"%{nm}%", u))
            row = cursor.fetchone()
            if not row:
                try:
                    sql_alvo = "SELECT TOP 1 cidcod AS codigo, cidnomecomp AS nome, ufsigla AS uf FROM CIDADE WITH (NOLOCK) WHERE (cidnomecomp = ? OR cidnomecomp LIKE ?) AND ufsigla = ?"
                    cursor.execute(sql_alvo, (nm, f"%{nm}%", u))
                    row = cursor.fetchone()
                except Exception:
                    pass
            if row:
                return {"codigo": str(row[0]), "nome": str(row[1] or ""), "uf": str(row[2] or "")}
            return None
        except Exception as exc:
            self._registrar_log_erro_sql("obter_cidade_por_nome_uf", "SELECT cidade por nome e uf", (nm, u), exc)
            return None

    def listar_categorias_lookup(self, termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        """Retorna categorias disponíveis para seleção/associação."""
        cursor = self._get_cursor()
        filtro = f"%{termo.strip()}%"
        try:
            if base_dados == "GeoApolo":
                sql = """
                    SELECT gc.geocategcodestr AS codigo, gc.geocategnome AS descricao
                      FROM USER_geoapolo_categoria gc WITH (NOLOCK)
                     WHERE gc.geocategcodestr LIKE ? OR gc.geocategnome LIKE ?
                     GROUP BY gc.geocategcodestr, gc.geocategnome
                     ORDER BY gc.geocategcodestr ASC
                """
            else:
                sql = """
                    SELECT cat.categcodestr AS codigo, cat.categnome AS descricao
                      FROM CATEGORIA cat WITH (NOLOCK)
                     WHERE cat.categcodestr LIKE ? OR cat.categnome LIKE ?
                     ORDER BY cat.categcodestr ASC
                """
            cursor.execute(sql, (filtro, filtro))
            cols = [col[0].lower() for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as exc:
            self._registrar_log_erro_sql("listar_categorias_lookup", "SELECT categorias", (filtro,), exc)
            logger.warning("Falha ao listar categorias lookup: %s", exc)
            return []

    def listar_cargos_lookup(self, termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        """Retorna cargos/ocupações disponíveis."""
        cursor = self._get_cursor()
        filtro = f"%{termo.strip()}%"
        try:
            if base_dados == "GeoApolo":
                sql = """
                    SELECT geocargocodestr AS codigo, geocargonome AS descricao
                      FROM USER_geoapolo_cargos WITH (NOLOCK)
                     WHERE geocargocodestr LIKE ? OR geocargonome LIKE ?
                     ORDER BY geocargonome ASC
                """
            else:
                sql = """
                    SELECT cargocodestr AS codigo, cargonome AS descricao
                      FROM CARGO WITH (NOLOCK)
                     WHERE cargocodestr LIKE ? OR cargonome LIKE ?
                     ORDER BY cargocodestr ASC
                """
            cursor.execute(sql, (filtro, filtro))
            cols = [col[0].lower() for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as exc:
            self._registrar_log_erro_sql("listar_cargos_lookup", "SELECT cargos", (filtro,), exc)
            logger.warning("Falha ao listar cargos lookup: %s", exc)
            return []

    def listar_tipos_cobranca(self, termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        """Retorna tipos de cobrança."""
        cursor = self._get_cursor()
        filtro = f"%{termo.strip()}%"
        try:
            if base_dados == "GeoApolo":
                sql = """
                    SELECT geotipocobcod AS codigo, geotipocobnome AS descricao
                      FROM USER_geoapolo_tipo_cobranca WITH (NOLOCK)
                     WHERE geotipocobcod LIKE ? OR geotipocobnome LIKE ?
                     ORDER BY geotipocobcod ASC
                """
            else:
                sql = """
                    SELECT tipocobcod AS codigo, tipocobnome AS descricao
                      FROM TIPO_COBRANCA WITH (NOLOCK)
                     WHERE tipocobcod LIKE ? OR tipocobnome LIKE ?
                     ORDER BY tipocobcod ASC
                """
            cursor.execute(sql, (filtro, filtro))
            cols = [col[0].lower() for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as exc:
            self._registrar_log_erro_sql("listar_tipos_cobranca", "SELECT tipo_cobranca", (filtro,), exc)
            logger.warning("Falha ao listar tipos de cobrança: %s", exc)
            return []

    def buscar_tipo_cobranca_por_codigo(self, codigo: str, base_dados: str = "GeoApolo") -> Optional[Dict[str, Any]]:
        """Busca rápida de tipo de cobrança por código para preenchimento de descrição."""
        if not codigo:
            return None
        cursor = self._get_cursor()
        try:
            if base_dados == "GeoApolo":
                sql = "SELECT geotipocobcod AS codigo, geotipocobnome AS descricao FROM USER_geoapolo_tipo_cobranca WITH (NOLOCK) WHERE geotipocobcod = ?"
            else:
                sql = "SELECT tipocobcod AS codigo, tipocobnome AS descricao FROM TIPO_COBRANCA WITH (NOLOCK) WHERE tipocobcod = ?"
            cursor.execute(sql, (codigo.strip(),))
            row = cursor.fetchone()
            if row:
                return {"codigo": str(row[0]), "descricao": str(row[1])}
            return None
        except Exception as exc:
            logger.warning("Erro ao buscar tipo de cobrança %s: %s", codigo, exc)
            return None

    def listar_dioceses(self, termo: str = "") -> List[Dict[str, Any]]:
        """Retorna dioceses da tabela USERdioceses_CNBB."""
        cursor = self._get_cursor()
        filtro = f"%{termo.strip()}%"
        try:
            sql = """
                SELECT CAST(id AS VARCHAR(20)) AS codigo, nome AS descricao, observacoes
                  FROM USERdioceses_CNBB WITH (NOLOCK)
                 WHERE CAST(id AS VARCHAR(20)) LIKE ? OR nome LIKE ?
                 ORDER BY nome ASC
            """
            cursor.execute(sql, (filtro, filtro))
            cols = [col[0].lower() for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as exc:
            self._registrar_log_erro_sql("listar_dioceses", "SELECT USERdioceses_CNBB", (filtro,), exc)
            logger.warning("Falha ao listar dioceses: %s", exc)
            return []

    def listar_dioceses_por_cidade(self, cidade: str = "", uf: str = "", termo: str = "") -> List[Dict[str, Any]]:
        """
        Retorna dioceses vinculadas à cidade e UF informadas, conforme lógica do Delphi em unt_cadentidades.pas.
        Se não encontrar para a cidade específica, faz fallback para dioceses do Estado (UF) e depois geral.
        """
        cursor = self._get_cursor()
        cidade_limpa = (cidade or "").strip().upper()
        uf_limpa = (uf or "").strip().upper()

        # 1. Tenta buscar filtrando por cidade e UF conforme query nativa do Delphi
        if cidade_limpa and uf_limpa:
            try:
                sql = """
                    SELECT CAST(udcnbb.id AS VARCHAR(20)) AS codigo, udcnbb.nome AS descricao, udcnbb.observacoes
                      FROM USERdioceses_CNBB udcnbb WITH (NOLOCK)
                     INNER JOIN USEREstado_CNBB uecnbb WITH (NOLOCK) ON udcnbb.estado_id = uecnbb.USERiD
                     INNER JOIN USERcidades_CNBB uccnbb WITH (NOLOCK) ON udcnbb.id = uccnbb.diocese_id
                     WHERE uecnbb.USERsigla = ? AND (uccnbb.descricao = ? OR uccnbb.descricao LIKE ?)
                     ORDER BY udcnbb.nome ASC
                """
                cursor.execute(sql, (uf_limpa, cidade_limpa, f"{cidade_limpa}%"))
                cols = [col[0].lower() for col in cursor.description]
                res = [dict(zip(cols, row)) for row in cursor.fetchall()]
                if res:
                    return res
            except Exception as exc:
                logger.warning("Falha na consulta de diocese por cidade/UF: %s", exc)

        # 2. Fallback: dioceses do Estado (UF)
        if uf_limpa:
            try:
                sql_uf = """
                    SELECT CAST(udcnbb.id AS VARCHAR(20)) AS codigo, udcnbb.nome AS descricao, udcnbb.observacoes
                      FROM USERdioceses_CNBB udcnbb WITH (NOLOCK)
                     INNER JOIN USEREstado_CNBB uecnbb WITH (NOLOCK) ON udcnbb.estado_id = uecnbb.USERiD
                     WHERE uecnbb.USERsigla = ?
                     ORDER BY udcnbb.nome ASC
                """
                cursor.execute(sql_uf, (uf_limpa,))
                cols = [col[0].lower() for col in cursor.description]
                res_uf = [dict(zip(cols, row)) for row in cursor.fetchall()]
                if res_uf:
                    return res_uf
            except Exception as exc:
                logger.warning("Falha na consulta de diocese por UF: %s", exc)

        # 3. Fallback geral: lista todas ou filtra por termo
        return self.listar_dioceses(termo)

    def obter_nome_diocese(self, diocese_id: Any) -> str:
        """Retorna o nome da diocese pelo ID numérico."""
        if not diocese_id:
            return ""
        s_id = str(diocese_id).strip()
        if not s_id or not s_id.isdigit():
            return ""
        cursor = self._get_cursor()
        try:
            sql = "SELECT nome FROM USERdioceses_CNBB WITH (NOLOCK) WHERE id = ?"
            cursor.execute(sql, (int(s_id),))
            row = cursor.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
            return ""
        except Exception as exc:
            logger.warning("Falha ao obter nome da diocese %s: %s", diocese_id, exc)
            return ""

    def obter_nome_atividade_economica(self, cod: str, base_dados: str = "GeoApolo") -> str:
        """Busca o nome da atividade econômica pelo código."""
        if not cod:
            return ""
        c = str(cod).strip()
        cursor = self._get_cursor()
        try:
            if base_dados == "GeoApolo":
                sql = "SELECT ativeconnome FROM USER_geoapolo_atividade_economica WITH (NOLOCK) WHERE ativeconcodestr = ?"
            else:
                sql = "SELECT AtivEconNome FROM ATIV_ECONOMICA WITH (NOLOCK) WHERE AtivEconCodEstr = ?"
            cursor.execute(sql, (c,))
            row = cursor.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
            return ""
        except Exception as exc:
            logger.warning("Falha ao obter nome de atividade econômica %s: %s", cod, exc)
            return ""

    def obter_nome_origem(self, cod: str, base_dados: str = "GeoApolo") -> str:
        """Busca o nome da origem pelo código."""
        if not cod:
            return ""
        c = str(cod).strip()
        cursor = self._get_cursor()
        try:
            if base_dados == "GeoApolo":
                sql = "SELECT geo_orignome FROM USER_geoapolo_origens WITH (NOLOCK) WHERE geo_origcodestr = ?"
            else:
                sql = "SELECT OrigNome FROM ORIGEM WITH (NOLOCK) WHERE OrigCodEstr = ?"
            cursor.execute(sql, (c,))
            row = cursor.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
            return ""
        except Exception as exc:
            logger.warning("Falha ao obter nome de origem %s: %s", cod, exc)
            return ""

    def obter_nome_regiao(self, cod: str, base_dados: str = "GeoApolo") -> str:
        """Busca o nome da região pelo código."""
        if not cod:
            return ""
        c = str(cod).strip()
        cursor = self._get_cursor()
        try:
            if base_dados == "GeoApolo":
                sql = "SELECT geo_regnome FROM USER_geoapolo_regiao_pais WITH (NOLOCK) WHERE georegcodestr = ?"
            else:
                sql = "SELECT RegNome FROM REGIAO WITH (NOLOCK) WHERE RegCodEstr = ?"
            cursor.execute(sql, (c,))
            row = cursor.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
            return ""
        except Exception as exc:
            logger.warning("Falha ao obter nome de região %s: %s", cod, exc)
            return ""

    def obter_codigo_regiao_por_uf(self, uf: str) -> Optional[str]:
        """
        Busca no banco na tabela REGIAO o código correspondente à UF da entidade:
          - RS, SC, PR -> Região Sul ('REGIAO SUL', código '1')
          - SP, MG, RJ, ES -> Região Sudeste ('REGIAO SUDESTE', código '5')
          - MS, MT, GO, TO, DF -> Região Centro-Oeste ('REGIAO CENTRO OESTE', código '3')
          - AM, RO, PA, AC, AP, RR -> Região Norte ('REGIAO NORTE', código '4')
          - AL, BA, CE, MA, PB, PE, PI, RN, SE -> Região Nordeste ('REGIAO NORDESTE', código '2')
        """
        if not uf:
            return None
        u = uf.strip().upper()

        mapa_uf_regiao = {
            # Sul
            "RS": ("SUL", "1"), "SC": ("SUL", "1"), "PR": ("SUL", "1"),
            # Sudeste
            "SP": ("SUDESTE", "5"), "MG": ("SUDESTE", "5"), "RJ": ("SUDESTE", "5"), "ES": ("SUDESTE", "5"),
            # Centro-Oeste
            "MS": ("CENTRO", "3"), "MT": ("CENTRO", "3"), "GO": ("CENTRO", "3"), "TO": ("CENTRO", "3"), "DF": ("CENTRO", "3"),
            # Norte
            "AM": ("NORTE", "4"), "RO": ("NORTE", "4"), "PA": ("NORTE", "4"), "AC": ("NORTE", "4"), "AP": ("NORTE", "4"), "RR": ("NORTE", "4"),
            # Nordeste
            "AL": ("NORDESTE", "2"), "BA": ("NORDESTE", "2"), "CE": ("NORDESTE", "2"), "MA": ("NORDESTE", "2"),
            "PB": ("NORDESTE", "2"), "PE": ("NORDESTE", "2"), "PI": ("NORDESTE", "2"), "RN": ("NORDESTE", "2"), "SE": ("NORDESTE", "2"),
        }

        info = mapa_uf_regiao.get(u)
        if not info:
            return None

        nome_busca, fallback_cod = info
        cursor = self._get_cursor()
        try:
            if nome_busca == "NORTE":
                sql = "SELECT TOP 1 RegCodEstr FROM REGIAO WITH (NOLOCK) WHERE RegNome LIKE '%NORTE%' AND RegNome NOT LIKE '%NORDESTE%'"
            elif nome_busca == "CENTRO":
                sql = "SELECT TOP 1 RegCodEstr FROM REGIAO WITH (NOLOCK) WHERE RegNome LIKE '%CENTRO%'"
            else:
                sql = f"SELECT TOP 1 RegCodEstr FROM REGIAO WITH (NOLOCK) WHERE RegNome LIKE '%{nome_busca}%'"

            cursor.execute(sql)
            row = cursor.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
            return fallback_cod
        except Exception as exc:
            logger.warning("Falha ao buscar código de região para UF %s no banco: %s", uf, exc)
            return fallback_cod

    def obter_categoria_por_codigo(self, cod: str, base_dados: str = "GeoApolo") -> Dict[str, str]:
        """Busca código e descrição da categoria pelo código estruturado."""
        if not cod:
            return {"codigo": "", "descricao": ""}
        c = str(cod).strip()
        cursor = self._get_cursor()
        try:
            if base_dados == "GeoApolo":
                sql = """
                    SELECT geocategcodestr AS codigo, geocategnome AS descricao
                      FROM USER_geoapolo_categoria WITH (NOLOCK)
                     WHERE geocategcodestr = ?
                """
            else:
                sql = """
                    SELECT categcodestr AS codigo, categnome AS descricao
                      FROM categoria WITH (NOLOCK)
                     WHERE categcodestr = ?
                """
            cursor.execute(sql, (c,))
            row = cursor.fetchone()
            if row:
                return {"codigo": str(row[0]).strip(), "descricao": str(row[1]).strip()}
            return {"codigo": c, "descricao": ""}
        except Exception as exc:
            logger.warning("Falha ao obter categoria por código %s: %s", cod, exc)
            return {"codigo": c, "descricao": ""}


    def listar_atividades_economicas(self, termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        """Retorna atividades econômicas."""
        cursor = self._get_cursor()
        filtro = f"%{termo.strip()}%"
        try:
            if base_dados == "GeoApolo":
                sql = """
                    SELECT ativeconcodestr AS codigo, ativeconnome AS descricao
                      FROM USER_geoapolo_atividade_economica WITH (NOLOCK)
                     WHERE ativeconcodestr LIKE ? OR ativeconnome LIKE ?
                     ORDER BY ativeconnome ASC
                """
            else:
                sql = """
                    SELECT AtivEconCodEstr AS codigo, AtivEconNome AS descricao
                      FROM ATIV_ECONOMICA WITH (NOLOCK)
                     WHERE AtivEconCodEstr LIKE ? OR AtivEconNome LIKE ?
                     ORDER BY AtivEconCodEstr ASC
                """
            cursor.execute(sql, (filtro, filtro))
            cols = [col[0].lower() for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as exc:
            self._registrar_log_erro_sql("listar_atividades_economicas", "SELECT ativ_economica", (filtro,), exc)
            logger.warning("Falha ao listar atividades econômicas: %s", exc)
            return []

    def listar_origens(self, termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        """Retorna origens de cadastro."""
        cursor = self._get_cursor()
        filtro = f"%{termo.strip()}%"
        try:
            if base_dados == "GeoApolo":
                sql = """
                    SELECT geo_origcodestr AS codigo, geo_orignome AS descricao
                      FROM USER_geoapolo_origens WITH (NOLOCK)
                     WHERE geo_origcodestr LIKE ? OR geo_orignome LIKE ?
                     ORDER BY geo_orignome ASC
                """
            else:
                sql = """
                    SELECT OrigCodEstr AS codigo, OrigNome AS descricao
                      FROM ORIGEM WITH (NOLOCK)
                     WHERE OrigCodEstr LIKE ? OR OrigNome LIKE ?
                     ORDER BY OrigCodEstr ASC
                """
            cursor.execute(sql, (filtro, filtro))
            cols = [col[0].lower() for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as exc:
            self._registrar_log_erro_sql("listar_origens", "SELECT origens", (filtro,), exc)
            logger.warning("Falha ao listar origens: %s", exc)
            return []

    def listar_regioes(self, termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        """Retorna regiões."""
        cursor = self._get_cursor()
        filtro = f"%{termo.strip()}%"
        try:
            if base_dados == "GeoApolo":
                sql = """
                    SELECT georegcodestr AS codigo, geo_regnome AS descricao
                      FROM USER_geoapolo_regiao_pais WITH (NOLOCK)
                     WHERE georegcodestr LIKE ? OR geo_regnome LIKE ?
                     ORDER BY geo_regnome ASC
                """
            else:
                sql = """
                    SELECT RegCodEstr AS codigo, RegNome AS descricao
                      FROM REGIAO WITH (NOLOCK)
                     WHERE RegCodEstr LIKE ? OR RegNome LIKE ?
                     ORDER BY RegCodEstr ASC
                """
            cursor.execute(sql, (filtro, filtro))
            cols = [col[0].lower() for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as exc:
            self._registrar_log_erro_sql("listar_regioes", "SELECT regioes", (filtro,), exc)
            logger.warning("Falha ao listar regiões: %s", exc)
            return []

    def listar_tipos_tratamento(self, base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        """Retorna todos os tipos de tratamento disponíveis para preenchimento de combobox."""
        cursor = self._get_cursor()
        itens_map = {}

        # 1. Busca da base GeoApolo (USER_geoapolo_tipotratamento)
        try:
            sql_geo = """
                SELECT tipotratcod AS codigo, abreviatura, descricao_tratamento AS descricao
                  FROM USER_geoapolo_tipotratamento WITH (NOLOCK)
                 ORDER BY abreviatura ASC
            """
            cursor.execute(sql_geo)
            cols = [col[0].lower() for col in cursor.description]
            for row in cursor.fetchall():
                d = dict(zip(cols, row))
                key = str(d.get("abreviatura") or d.get("codigo") or "").strip().upper()
                if key and key not in itens_map:
                    itens_map[key] = d
        except Exception as exc:
            logger.debug("Tabela USER_geoapolo_tipotratamento: %s", exc)

        # 2. Busca da base Apolo (TIPO_TRATAMENTO) para compor catálogo integral
        try:
            sql_apolo = """
                SELECT TipoTratCod AS codigo, TipoTratCod AS abreviatura, TipoTratNome AS descricao
                  FROM TIPO_TRATAMENTO WITH (NOLOCK)
                 ORDER BY TipoTratCod ASC
            """
            cursor.execute(sql_apolo)
            cols = [col[0].lower() for col in cursor.description]
            for row in cursor.fetchall():
                d = dict(zip(cols, row))
                key = str(d.get("abreviatura") or d.get("codigo") or "").strip().upper()
                if key and key not in itens_map:
                    itens_map[key] = d
        except Exception as exc:
            logger.debug("Tabela TIPO_TRATAMENTO: %s", exc)

        if itens_map:
            return sorted(
                list(itens_map.values()),
                key=lambda x: str(x.get("abreviatura") or x.get("descricao") or "").upper()
            )

        # Fallback abrangente caso o banco esteja inacessível/vazio
        return [
            {"codigo": "01", "abreviatura": "SR", "descricao": "SR - SENHOR"},
            {"codigo": "02", "abreviatura": "SRA", "descricao": "SRA - SENHORA"},
            {"codigo": "03", "abreviatura": "SRTA", "descricao": "SRTA - SENHORITA"},
            {"codigo": "04", "abreviatura": "PADRE", "descricao": "PADRE - PADRE"},
            {"codigo": "05", "abreviatura": "DOM", "descricao": "DOM - DOM"},
            {"codigo": "06", "abreviatura": "IRMA", "descricao": "IRMA - IRMÃ"},
            {"codigo": "07", "abreviatura": "DIACONO", "descricao": "DIÁCONO - DIÁCONO"},
            {"codigo": "08", "abreviatura": "DR", "descricao": "DR - DOUTOR"},
            {"codigo": "09", "abreviatura": "DRA", "descricao": "DRA - DOUTORA"},
            {"codigo": "10", "abreviatura": "BISPO", "descricao": "BISPO - BISPO"},
            {"codigo": "11", "abreviatura": "ARCEBISPO", "descricao": "ARCEBISPO - ARCEBISPO"},
            {"codigo": "12", "abreviatura": "MONSENHOR", "descricao": "MONSENHOR - MONSENHOR"},
            {"codigo": "13", "abreviatura": "FREI", "descricao": "FREI - FREI"},
            {"codigo": "14", "abreviatura": "PASTOR", "descricao": "PASTOR - PASTOR"},
            {"codigo": "15", "abreviatura": "PASTORA", "descricao": "PASTORA - PASTORA"},
            {"codigo": "16", "abreviatura": "PROF", "descricao": "PROF - PROFESSOR"},
            {"codigo": "17", "abreviatura": "PROFA", "descricao": "PROFA - PROFESSORA"},
            {"codigo": "18", "abreviatura": "PAPA", "descricao": "PAPA - PAPA"},
            {"codigo": "19", "abreviatura": "CARDEAL", "descricao": "CARDEAL - CARDEAL"},
            {"codigo": "20", "abreviatura": "VEREADOR", "descricao": "VEREADOR - VEREADOR"},
            {"codigo": "21", "abreviatura": "DEPUTADO", "descricao": "DEPUTADO - DEPUTADO"},
            {"codigo": "22", "abreviatura": "SENADOR", "descricao": "SENADOR - SENADOR"},
            {"codigo": "23", "abreviatura": "ILMO", "descricao": "ILMO - ILUSTRÍSSIMO"},
            {"codigo": "24", "abreviatura": "EXMO", "descricao": "EXMO - EXCELENTÍSSIMO"},
        ]

    def listar_graus_escolaridade(self) -> List[Dict[str, Any]]:
        """Retorna graus de escolaridade para combobox."""
        cursor = self._get_cursor()
        try:
            sql = """
                SELECT CAST(codigo_grauescolaridade AS VARCHAR(10)) AS codigo, grau_escolaridade AS descricao
                  FROM USER_geoapolo_grauescolaridade WITH (NOLOCK)
                 ORDER BY codigo_grauescolaridade ASC
            """
            cursor.execute(sql)
            cols = [col[0].lower() for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as exc:
            logger.warning("Falha ao listar graus de escolaridade: %s", exc)
            return []

    def listar_tipos_logradouro(self) -> List[Dict[str, Any]]:
        """Retorna tipos de logradouro para combobox."""
        cursor = self._get_cursor()
        try:
            sql = """
                SELECT tipologradabrev AS abrev, tipologradouro AS descricao
                  FROM USER_geoapolo_tipologradouro WITH (NOLOCK)
                 ORDER BY tipologradabrev ASC
            """
            cursor.execute(sql)
            cols = [col[0].lower() for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as exc:
            logger.warning("Falha ao listar tipos de logradouro: %s", exc)
            return []

    def listar_conceitos(self) -> List[Dict[str, Any]]:
        """Retorna conceitos disponíveis."""
        cursor = self._get_cursor()
        itens = [
            {"codigo": "Nenhum", "descricao": "Nenhum"},
            {"codigo": "Excelente", "descricao": "Excelente"},
            {"codigo": "Bom", "descricao": "Bom"},
            {"codigo": "Razoável", "descricao": "Razoável"},
            {"codigo": "Regular", "descricao": "Regular"},
            {"codigo": "Insatisfatório", "descricao": "Insatisfatório"},
        ]
        try:
            sql = "SELECT ConcAvalIdent AS codigo, ConcAvalDescr AS descricao FROM CONCEITO_AVAL WITH (NOLOCK) ORDER BY ConcAvalIdent ASC"
            cursor.execute(sql)
            rows = cursor.fetchall()
            for r in rows:
                c = str(r[0] or "").strip()
                d = str(r[1] or "").strip()
                if c and not any(it["codigo"].upper() == c.upper() for it in itens):
                    itens.append({"codigo": c, "descricao": d or c})
        except Exception:
            pass
        return itens

    def obter_ultimas_doacoes(self, entcod: str, limite: int = 1000) -> List[Dict[str, Any]]:
        """Retorna todas as doações / contribuições e títulos da entidade na base Alvo (padrão até 1000 registros)."""
        if not entcod:
            return []
        cursor = self._get_cursor()
        # 1. Tenta parc_doc_fin + doc_fin
        try:
            sql = f"""
                SELECT TOP {limite}
                       pdf.ParcDocFinDataPag AS datapag,
                       pdf.ParcDocFinDataVenc AS datavenc,
                       pdf.ParcDocFinValOrig AS valor,
                       COALESCE(df.DocFinEspec, 'DOA') AS especie,
                       pdf.DocFinChv AS documento,
                       pdf.TipoCobCod AS tipocob,
                       pdf.SitCodEstr AS status
                  FROM parc_doc_fin pdf WITH (NOLOCK)
                  LEFT JOIN doc_fin df WITH (NOLOCK) ON pdf.EmpCod = df.EmpCod AND pdf.DocFinChv = df.DocFinChv
                 WHERE pdf.EntCod = ?
                 ORDER BY COALESCE(pdf.ParcDocFinDataPag, pdf.ParcDocFinDataVenc) DESC
            """
            cursor.execute(sql, (entcod,))
            cols = [col[0].lower() for col in cursor.description]
            linhas = cursor.fetchall()
            if linhas:
                return [dict(zip(cols, row)) for row in linhas]
        except Exception as exc:
            logger.debug("Tentativa via parc_doc_fin falhou ou sem registros (%s), tentando view USERVW_DOACOES", exc)

        # 2. Fallback via USERVW_DOACOES
        try:
            sql_view = f"""
                SELECT TOP {limite}
                       parcdocfindatapag AS datapag,
                       NULL AS datavenc,
                       parcdocfinvalorig AS valor,
                       'DOACAO' AS especie,
                       DocFinChv AS documento,
                       TipoCobCod AS tipocob,
                       'QUITADO' AS status
                  FROM USERVW_DOACOES WITH (NOLOCK)
                 WHERE entcod = ?
                 ORDER BY parcdocfindatapag DESC
            """
            cursor.execute(sql_view, (entcod,))
            cols = [col[0].lower() for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]
        except Exception as exc2:
            logger.warning("Falha ao obter últimas doações para entidade %s: %s", entcod, exc2)
            return []

    def listar_bancos(self, termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        """Retorna lista de bancos para lookup."""
        cursor = self._get_cursor()
        try:
            if base_dados == "GeoApolo":
                sql = "SELECT geobconum AS codigo, geobconome AS descricao FROM USER_geoapolo_bancos WITH (NOLOCK) ORDER BY geobconome ASC"
            else:
                sql = "SELECT bconum AS codigo, bconome AS descricao FROM banco WITH (NOLOCK) ORDER BY bconome ASC"
            cursor.execute(sql)
            cols = [col[0].lower() for col in cursor.description]
            linhas = [dict(zip(cols, row)) for row in cursor.fetchall()]
            if termo:
                t = termo.strip().lower()
                return [r for r in linhas if t in str(r.get("codigo", "")).lower() or t in str(r.get("descricao", "")).lower()]
            return linhas
        except Exception as exc:
            logger.warning("Falha ao listar bancos: %s", exc)
            return []

    def listar_agencias(self, bconum: str = "", termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        """Retorna lista de agências bancárias para lookup."""
        cursor = self._get_cursor()
        try:
            if base_dados == "GeoApolo":
                if bconum:
                    sql = "SELECT geoagnum AS codigo, geoagnome AS descricao FROM USER_geoapolo_agencia WITH (NOLOCK) WHERE geobconum = ? ORDER BY geoagnome ASC"
                    cursor.execute(sql, (bconum,))
                else:
                    sql = "SELECT geoagnum AS codigo, geoagnome AS descricao FROM USER_geoapolo_agencia WITH (NOLOCK) ORDER BY geoagnome ASC"
                    cursor.execute(sql)
            else:
                if bconum:
                    sql = "SELECT agnum AS codigo, agnome AS descricao FROM AG_BANCARIA WITH (NOLOCK) WHERE bconum = ? ORDER BY agnome ASC"
                    cursor.execute(sql, (bconum,))
                else:
                    sql = "SELECT agnum AS codigo, agnome AS descricao FROM AG_BANCARIA WITH (NOLOCK) ORDER BY agnome ASC"
                    cursor.execute(sql)
            cols = [col[0].lower() for col in cursor.description]
            linhas = [dict(zip(cols, row)) for row in cursor.fetchall()]
            if termo:
                t = termo.strip().lower()
                return [r for r in linhas if t in str(r.get("codigo", "")).lower() or t in str(r.get("descricao", "")).lower()]
            return linhas
        except Exception as exc:
            logger.warning("Falha ao listar agências: %s", exc)
            return []

    def salvar_historico_entidade(self, entcod: str, novo_texto: str, usuario: str = "SISTEMA", base_dados: str = "GeoApolo") -> bool:
        """Acrescenta um novo registro de histórico à entidade com carimbo de usuário e data/hora."""
        if not entcod or not novo_texto:
            return False
        cursor = self._get_cursor()
        from datetime import datetime
        carimbo = f"[{usuario.upper()}] - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - {novo_texto.strip()}"
        try:
            if base_dados == "GeoApolo":
                try:
                    cursor.execute("SELECT enthist FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE geoentcod = ?", (entcod,))
                    row = cursor.fetchone()
                    hist_atual = str(row[0] or "") if row else ""
                    hist_novo = (hist_atual + "\n" + carimbo).strip() if hist_atual else carimbo.strip()
                    cursor.execute("UPDATE USER_geoapolo_entidade SET enthist = ? WHERE geoentcod = ?", (hist_novo, entcod))
                except Exception:
                    cursor.execute("SELECT geoobservacoes FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE geoentcod = ?", (entcod,))
                    row = cursor.fetchone()
                    hist_atual = str(row[0] or "") if row else ""
                    hist_novo = (hist_atual + "\n" + carimbo).strip() if hist_atual else carimbo.strip()
                    cursor.execute("UPDATE USER_geoapolo_entidade SET geoobservacoes = ? WHERE geoentcod = ?", (hist_novo, entcod))
            else:
                try:
                    cursor.execute("SELECT enttextohist FROM entidade WITH (NOLOCK) WHERE entcod = ?", (entcod,))
                    row = cursor.fetchone()
                    hist_atual = str(row[0] or "") if row else ""
                    hist_novo = (hist_atual + "\n" + carimbo).strip() if hist_atual else carimbo.strip()
                    cursor.execute("UPDATE entidade SET enttextohist = ? WHERE entcod = ?", (hist_novo, entcod))
                except Exception:
                    cursor.execute("SELECT entobservacoes FROM entidade WITH (NOLOCK) WHERE entcod = ?", (entcod,))
                    row = cursor.fetchone()
                    hist_atual = str(row[0] or "") if row else ""
                    hist_novo = (hist_atual + "\n" + carimbo).strip() if hist_atual else carimbo.strip()
                    cursor.execute("UPDATE entidade SET entobservacoes = ? WHERE entcod = ?", (hist_novo, entcod))
            self._conn.commit()
            return True
        except Exception as exc:
            self._conn.rollback()
            logger.warning("Falha ao salvar histórico da entidade %s: %s", entcod, exc)
            return False



