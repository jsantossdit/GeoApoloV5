"""
Repositório de dados para Entidades em Python / SQL Server.
Correspondente a unt_entidades_repository.pas.

Preserva rigorosamente:
- Hints de leitura T-SQL: WITH (NOLOCK)
- Parametrização segura contra SQL Injection
- Chamada de Stored Procedure nativa User_geraocorrencia_projetosv2 com parâmetros vinculados
"""

import logging
from typing import List, Dict, Any, Optional
from entidades.models import EntidadeFiltro, CredencialAlvo

logger = logging.getLogger(__name__)


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
        if self._conn is None:
            raise RuntimeError("Conexão com o banco de dados não foi inicializada no Repositório.")
        return self._conn.cursor()

    def obter_parametro_integracao(self, empcod: str) -> str:
        """
        Consulta se a empresa possui integração com o Alvo (Integra / Não Integra / Mescla).
        Preserva WITH (NOLOCK).
        """
        sql = """
            SELECT integra_entidades_apolo 
              FROM USER_geoapolo_configuracoes WITH (NOLOCK) 
             WHERE empcod = ?
        """
        cursor = self._get_cursor()
        cursor.execute(sql, (empcod,))
        row = cursor.fetchone()
        if row:
            return row[0] or ""
        return ""

    def view_existe(self, nome_view: str) -> bool:
        """Verifica a existência de view no catálogo de metadados do SQL Server."""
        sql = "SELECT 1 FROM sys.views WITH (NOLOCK) WHERE name = ?"
        cursor = self._get_cursor()
        cursor.execute(sql, (nome_view,))
        return cursor.fetchone() is not None

    def consultar_lista(self, filtro: EntidadeFiltro) -> List[Dict[str, Any]]:
        """
        Executa a busca otimizada de entidades na base selecionada (GeoApolo ou Alvo).
        Preserva os hints de índice e NOLOCK originais do Delphi.
        """
        direcao = "ASC" if filtro.ordem_asc else "DESC"
        campo_busca = filtro.campo_busca.strip() or ("entnome" if filtro.base_dados == "Alvo" else "geoentnome")
        
        # Sanitização simples de nome de coluna
        campo_busca = "".join(c for c in campo_busca if c.isalnum() or c == "_")
        ordem_col = "".join(c for c in (filtro.campo_ordenacao or campo_busca) if c.isalnum() or c == "_")

        cursor = self._get_cursor()

        if filtro.base_dados == "Alvo":
            if filtro.tipo_pesquisa == "Consulta":
                sql = f"""
                    SELECT TOP ({filtro.limite}) *
                      FROM entidades_apolo e WITH (NOLOCK)
                     WHERE e.{campo_busca} LIKE ?
                       AND SUBSTRING(e.categcodestr, 1, 2) IN ('02', '03')
                     ORDER BY e.entnome ASC
                """
                cursor.execute(sql, (f"%{filtro.texto_busca}%",))
            else:
                sql = f"""
                    SELECT *
                      FROM entidades_apolo e WITH (NOLOCK)
                     WHERE e.{campo_busca} LIKE ?
                       AND SUBSTRING(e.categcodestr, 1, 2) IN ('02', '03')
                     ORDER BY e.{ordem_col} {direcao}
                """
                cursor.execute(sql, (f"%{filtro.texto_busca}%",))
        else:
            # Base GeoApolo
            if filtro.tipo_pesquisa == "Consulta":
                status_atualizou = "S" if filtro.filtro_especial == "JAEXPORTADA" else "N"
                sql = f"""
                    SELECT TOP ({filtro.limite}) *
                      FROM entidades_geoapolo e WITH (NOLOCK)
                     INNER JOIN USER_geoapolo_entidade_documentos uged WITH (NOLOCK)
                        ON e.entcpfcgc = uged.geonumerodocumento 
                       AND uged.geotipodocumento = 'CPF/CNPJ'
                     INNER JOIN user_geoapolo_entidade ue WITH (NOLOCK)
                        ON e.geoentcod = ue.geoentcod
                     WHERE ue.atualizou_apolo = ?
                     ORDER BY CASE WHEN ue.atualizou_apolo = 'N' AND e.Entobservacoes IS NULL THEN 0 ELSE 1 END
                """
                cursor.execute(sql, (status_atualizou,))
            else:
                sql = f"""
                    SELECT *
                      FROM entidades_geoapolo e WITH (NOLOCK)
                     INNER JOIN user_geoapolo_entidade ue WITH (NOLOCK) 
                        ON e.geoentcod = ue.geoentcod
                     WHERE e.{campo_busca} LIKE ?
                     ORDER BY CASE WHEN ue.atualizou_apolo = 'N' AND e.Entobservacoes IS NULL THEN 0 ELSE 1 END
                """
                cursor.execute(sql, (f"%{filtro.texto_busca}%",))

        # Mapeia colunas para dicionários
        colunas = [column[0] for column in cursor.description]
        registros = []
        for row in cursor.fetchall():
            registros.append(dict(zip(colunas, row)))

        return registros

    def obter_ocorrencia_codigo(self, geoentcod: str) -> Optional[str]:
        sql = "SELECT ocorcod FROM user_geoapolo_entidade WITH (NOLOCK) WHERE geoentcod = ?"
        cursor = self._get_cursor()
        cursor.execute(sql, (geoentcod,))
        row = cursor.fetchone()
        return row[0] if row else None

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
        cursor = self._get_cursor()
        cursor.execute(sql, params)

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
            logger.exception("Erro ao ignorar atualização da entidade: %s", exc)
            raise

    def atualizar_entcod_alvo_via_cpf(self, geoentcod: str) -> Optional[str]:
        """
        Verifica se a entidade existe na base Alvo pelo CPF/CNPJ e vincula o entcod.
        """
        cursor = self._get_cursor()
        sql_doc = """
            SELECT geonumerodocumento 
              FROM USER_geoapolo_entidade_documentos WITH (NOLOCK)
             WHERE geoentcod = ? AND geotipodocumento = 'CPF/CNPJ'
        """
        cursor.execute(sql_doc, (geoentcod,))
        row_doc = cursor.fetchone()
        if not row_doc:
            return None

        cpf = row_doc[0]
        sql_alvo = "SELECT entcod FROM entidades_geoapolo WITH (NOLOCK) WHERE entcpfcgc = ?"
        cursor.execute(sql_alvo, (cpf,))
        row_alvo = cursor.fetchone()
        if not row_alvo:
            return None

        entcod_alvo = str(row_alvo[0])
        sql_upd = "UPDATE USER_geoapolo_entidade SET entcod = ? WHERE geoentcod = ?"
        cursor.execute(sql_upd, (entcod_alvo, geoentcod))
        self._conn.commit()
        return entcod_alvo

    def obter_credenciais_alvo(self, cod_usuario: str) -> CredencialAlvo:
        sql = """
            SELECT usucod_apolo, senha_alvo 
              FROM USER_geoapolo_usuarios WITH (NOLOCK) 
             WHERE usucod = ?
        """
        cursor = self._get_cursor()
        cursor.execute(sql, (cod_usuario,))
        row = cursor.fetchone()
        if row:
            return CredencialAlvo(usuario_alvo=row[0] or "", senha_alvo_cripto=row[1] or "")
        return CredencialAlvo()

    def salvar_credenciais_alvo(self, cod_usuario: str, usu_apolo: str, senha_cripto: str):
        sql = """
            UPDATE USER_geoapolo_usuarios 
               SET usucod_apolo = ?, senha_alvo = ? 
             WHERE usucod = ?
        """
        cursor = self._get_cursor()
        cursor.execute(sql, (usu_apolo, senha_cripto, cod_usuario))
        self._conn.commit()

    def carregar_dados_comparacao(self, geoentcod: str, entcod: str) -> tuple[Dict[str, Any], Dict[str, Any]]:
        cursor = self._get_cursor()
        
        # SVE (GeoApolo)
        cursor.execute("SELECT * FROM entidades_geoapolo WITH (NOLOCK) WHERE geoentcod = ?", (geoentcod,))
        row_sve = cursor.fetchone()
        cols_sve = [c[0] for c in cursor.description] if cursor.description else []
        sve_dict = dict(zip(cols_sve, row_sve)) if row_sve else {}

        # Alvo
        cursor.execute("SELECT * FROM entidades_apolo WITH (NOLOCK) WHERE entcod = ?", (entcod,))
        row_alvo = cursor.fetchone()
        cols_alvo = [c[0] for c in cursor.description] if cursor.description else []
        alvo_dict = dict(zip(cols_alvo, row_alvo)) if row_alvo else {}

        return sve_dict, alvo_dict

    def gravar_entidade_geoapolo(self, dados: Dict[str, Any], modo_inclusao: bool = True) -> bool:
        """Persiste ou atualiza uma entidade na base GeoApolo."""
        cursor = self._get_cursor()
        try:
            if modo_inclusao:
                sql = """
                    INSERT INTO USER_geoapolo_entidade (
                        geoentcod, geotipotratcod, geoentnome, geoentnomefantasia, tipolograd,
                        geoentender, geoenderno, geoentendercomp, geoentbair, geoentdatacad,
                        geoentdesdedata, geoentcep, geocidcod, geoentcxapost, geoentgenero,
                        geolocalreferencia_ender, geotipofj, geofalecido, codigo_grauescolaridade,
                        geocargocodestr, geoentdataanivfund, geoentestcivil, entcod, cidcodapolo
                    ) VALUES (
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?, ?, ?, ?
                    )
                """
                params = (
                    dados.get("geoentcod"), dados.get("geotipotratcod"), dados.get("geoentnome"),
                    dados.get("geoentnomefantasia"), dados.get("tipolograd"), dados.get("geoentender"),
                    dados.get("geoenderno"), dados.get("geoentendercomp"), dados.get("geoentbair"),
                    dados.get("geoentdatacad"), dados.get("geoentdesdedata"), dados.get("geoentcep"),
                    dados.get("geocidcod"), dados.get("geoentcxapost"), dados.get("geoentgenero"),
                    dados.get("geolocalreferencia_ender"), dados.get("geotipofj"), dados.get("geofalecido", "N"),
                    dados.get("codigo_grauescolaridade"), dados.get("geocargocodestr"), dados.get("geoentdataanivfund"),
                    dados.get("geoentestcivil"), dados.get("entcod"), dados.get("cidcodapolo")
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
                        geoentdataanivfund = ?, geoentestcivil = ?, entcod = ?
                    WHERE geoentcod = ?
                """
                params = (
                    dados.get("geotipotratcod"), dados.get("geoentnome"), dados.get("geoentnomefantasia"),
                    dados.get("tipolograd"), dados.get("geoentender"), dados.get("geoenderno"),
                    dados.get("geoentendercomp"), dados.get("geoentbair"), dados.get("geoentdatacad"),
                    dados.get("geoentcep"), dados.get("geocidcod"), dados.get("cidcodapolo"),
                    dados.get("geoentcxapost"), dados.get("geoentgenero"), dados.get("geolocalreferencia_ender"),
                    dados.get("geofalecido", "N"), dados.get("codigo_grauescolaridade"), dados.get("geocargocodestr"),
                    dados.get("geoentdataanivfund"), dados.get("geoentestcivil"), dados.get("entcod"),
                    dados.get("geoentcod")
                )
            cursor.execute(sql, params)
            self._conn.commit()
            return True
        except Exception as exc:
            self._conn.rollback()
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
                    entdataanivfund = ?, entdatacad = ?
                WHERE entcod = ?
            """
            params = (
                dados.get("entnome"), dados.get("tipotratcod"), dados.get("entnomefant"),
                dados.get("entlograd"), dados.get("entender"), dados.get("entenderno"),
                dados.get("entendercomp"), dados.get("entbair"), dados.get("entcep"), dados.get("cidcod"),
                dados.get("enttipofj"), dados.get("entcxapost"), dados.get("entgenero"),
                dados.get("cargocodestr"), dados.get("entestcivil"), dados.get("entgrauescol"),
                dados.get("entdataanivfund"), dados.get("entdatacad"), dados.get("entcod")
            )
            cursor.execute(sql, params)

            # Atualiza u_entidade
            cursor.execute("UPDATE u_entidade SET USERFalecido = ? WHERE entcod = ?", (dados.get("USERFalecido", "Não"), dados.get("entcod")))
            self.atualizar_log_entidade_apolo(dados.get("entcod"))
            self._conn.commit()
            return True
        except Exception as exc:
            self._conn.rollback()
            logger.exception("Erro ao salvar entidade no Alvo: %s", exc)
            raise
