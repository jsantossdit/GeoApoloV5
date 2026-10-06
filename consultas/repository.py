"""
Repositório de dados para Consultas Dinâmicas e Gestão de Permissões de Consultas.
GeoApolo V5
Compatível com SQL Server nativo (WITH NOLOCK) e SQLite em memória.
Equivalente a ConsultaRepository.pas e unt_imediatas_repository.pas do Delphi.
"""

from typing import List, Optional, Tuple, Any
from consultas.models import ConsultaConfigDTO, PermissaoConsultaDTO, ResultadoConsultaDTO


class ConsultasRepository:
    """Repositório de persistência e execução de Consultas Dinâmicas e Imediatas."""

    def __init__(self, connection):
        self.conn = connection
        self._is_sql_server = not hasattr(connection, "isolation_level")
        self._cached_coluna_sql: Optional[str] = None

    def _nolock(self) -> str:
        return "WITH (NOLOCK)" if self._is_sql_server else ""

    def _coluna_sql(self) -> str:
        """Determina dinamicamente se a coluna de SQL é sentenca_sql (SQL Server) ou sql_consulta (SQLite)."""
        if self._cached_coluna_sql is None:
            try:
                cur = self.conn.cursor()
                if self._is_sql_server:
                    cur.execute(
                        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                        "WHERE TABLE_NAME = 'USER_geoapolo_consultas' AND COLUMN_NAME = 'sentenca_sql'"
                    )
                    self._cached_coluna_sql = "sentenca_sql" if cur.fetchone() else "sql_consulta"
                else:
                    cur.execute("PRAGMA table_info(USER_geoapolo_consultas)")
                    cols = [row[1] for row in cur.fetchall()]
                    self._cached_coluna_sql = "sentenca_sql" if "sentenca_sql" in cols else "sql_consulta"
            except Exception:
                self._cached_coluna_sql = "sentenca_sql" if self._is_sql_server else "sql_consulta"
        return self._cached_coluna_sql

    def obter_proximo_codigo(self) -> str:
        """Obtém o próximo código numérico para nova consulta (equivalente ao Delphi)."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        try:
            cur.execute(f"SELECT COALESCE(MAX(CAST(codigo_consulta AS INT)), 0) + 1 FROM USER_geoapolo_consultas {nolock}")
            row = cur.fetchone()
            return str(row[0]) if row and row[0] is not None else "1"
        except Exception:
            return "1"

    def listar_consultas(self, tipo_consulta: Optional[str] = None, banco_consulta: Optional[str] = None) -> List[ConsultaConfigDTO]:
        """Lista todas as consultas cadastradas, com filtros opcionais por tipo e banco."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        col_sql = self._coluna_sql()

        where_clauses = []
        params = []
        if tipo_consulta:
            where_clauses.append("tipo_consulta = ?")
            params.append(tipo_consulta)
        if banco_consulta and banco_consulta.upper() != "TODOS":
            where_clauses.append("(banco_consulta = ? OR banco_consulta IS NULL)")
            params.append(banco_consulta)

        where_str = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        sql = f"""
            SELECT codigo_consulta, descricao_consulta, {col_sql}, tipo_consulta, banco_consulta
            FROM USER_geoapolo_consultas {nolock}
            {where_str}
            ORDER BY descricao_consulta ASC
        """
        cur.execute(sql, params)
        return [
            ConsultaConfigDTO(
                codigo_consulta=str(r[0]),
                descricao_consulta=str(r[1] or ""),
                sql_consulta=str(r[2] or ""),
                tipo_consulta=str(r[3] or "I"),
                banco_consulta=str(r[4] or "ALVO"),
            )
            for r in cur.fetchall()
        ]

    def listar_consultas_imediatas(self, usuario: str = "", banco: str = "") -> List[ConsultaConfigDTO]:
        """
        Lista consultas imediatas (tipo_consulta = 'I') autorizadas para o usuário.
        Equivalente a carrega_consultaspermitidas em unt_imediatas.pas no Delphi.
        """
        cur = self.conn.cursor()
        nolock = self._nolock()
        col_sql = self._coluna_sql()

        usuario_limpo = (usuario or "").strip().upper()
        banco_filtro = (banco or "").strip().upper()

        # Se for ADMIN ou usuário vazio, lista todas as consultas imediatas do banco
        if not usuario_limpo or usuario_limpo == "ADMIN":
            if banco_filtro and banco_filtro != "TODOS":
                sql = f"""
                    SELECT codigo_consulta, descricao_consulta, {col_sql}, tipo_consulta, banco_consulta
                    FROM USER_geoapolo_consultas {nolock}
                    WHERE tipo_consulta = 'I' AND (UPPER(banco_consulta) = ? OR banco_consulta IS NULL)
                    ORDER BY descricao_consulta ASC
                """
                cur.execute(sql, [banco_filtro])
            else:
                sql = f"""
                    SELECT codigo_consulta, descricao_consulta, {col_sql}, tipo_consulta, banco_consulta
                    FROM USER_geoapolo_consultas {nolock}
                    WHERE tipo_consulta = 'I'
                    ORDER BY descricao_consulta ASC
                """
                cur.execute(sql)
            rows = cur.fetchall()
            return [
                ConsultaConfigDTO(
                    codigo_consulta=str(r[0]),
                    descricao_consulta=str(r[1] or ""),
                    sql_consulta=str(r[2] or ""),
                    tipo_consulta=str(r[3] or "I"),
                    banco_consulta=str(r[4] or "ALVO"),
                )
                for r in rows
            ]

        # Verifica consultas com permissão específica do usuário
        where_banco = "AND (UPPER(gac.banco_consulta) = ? OR gac.banco_consulta IS NULL)" if (banco_filtro and banco_filtro != "TODOS") else ""
        params = [usuario_limpo]
        if where_banco:
            params.append(banco_filtro)

        sql = f"""
            SELECT gac.codigo_consulta, gac.descricao_consulta, gac.{col_sql}, gac.tipo_consulta, gac.banco_consulta
            FROM USER_geoapolo_consultas gac {nolock}
            INNER JOIN USER_geoapolo_permissaoconsulta gpc {nolock} ON gac.codigo_consulta = gpc.codigo_consulta
            WHERE gpc.usucod = ?
              AND gac.tipo_consulta = 'I'
              AND gpc.autorizacao IN ('A', 'S')
              {where_banco}
            ORDER BY gac.descricao_consulta ASC
        """
        cur.execute(sql, params)
        rows = cur.fetchall()

        # Se o usuário não tiver registros individuais na tabela de permissões, fallback para todas as imediatas
        if not rows:
            cur.execute("SELECT 1 FROM USER_geoapolo_permissaoconsulta WHERE usucod = ?", [usuario_limpo])
            tem_registro = cur.fetchone() is not None
            if not tem_registro:
                return self.listar_consultas_imediatas(usuario="ADMIN", banco=banco)

        return [
            ConsultaConfigDTO(
                codigo_consulta=str(r[0]),
                descricao_consulta=str(r[1] or ""),
                sql_consulta=str(r[2] or ""),
                tipo_consulta=str(r[3] or "I"),
                banco_consulta=str(r[4] or "ALVO"),
            )
            for r in rows
        ]

    def obter_consulta(self, codigo_consulta: str) -> Optional[ConsultaConfigDTO]:
        """Localiza configuração de consulta pelo código."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        col_sql = self._coluna_sql()
        sql = f"""
            SELECT codigo_consulta, descricao_consulta, {col_sql}, tipo_consulta, banco_consulta
            FROM USER_geoapolo_consultas {nolock}
            WHERE codigo_consulta = ?
        """
        cur.execute(sql, [codigo_consulta])
        r = cur.fetchone()
        if not r:
            return None
        return ConsultaConfigDTO(
            codigo_consulta=str(r[0]),
            descricao_consulta=str(r[1] or ""),
            sql_consulta=str(r[2] or ""),
            tipo_consulta=str(r[3] or "I"),
            banco_consulta=str(r[4] or "ALVO"),
        )

    def obter_consulta_por_descricao(self, descricao: str) -> Optional[ConsultaConfigDTO]:
        """Localiza configuração de consulta pela descrição exata."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        col_sql = self._coluna_sql()
        sql = f"""
            SELECT codigo_consulta, descricao_consulta, {col_sql}, tipo_consulta, banco_consulta
            FROM USER_geoapolo_consultas {nolock}
            WHERE descricao_consulta = ?
        """
        cur.execute(sql, [descricao])
        r = cur.fetchone()
        if not r:
            return None
        return ConsultaConfigDTO(
            codigo_consulta=str(r[0]),
            descricao_consulta=str(r[1] or ""),
            sql_consulta=str(r[2] or ""),
            tipo_consulta=str(r[3] or "I"),
            banco_consulta=str(r[4] or "ALVO"),
        )

    def salvar_consulta(self, c: ConsultaConfigDTO) -> bool:
        """Cria ou atualiza uma consulta configurável."""
        cur = self.conn.cursor()
        col_sql = self._coluna_sql()

        if not c.codigo_consulta:
            c.codigo_consulta = self.obter_proximo_codigo()

        cur.execute("SELECT 1 FROM USER_geoapolo_consultas WHERE codigo_consulta = ?", [c.codigo_consulta])
        if cur.fetchone():
            sql = f"""
                UPDATE USER_geoapolo_consultas
                SET descricao_consulta = ?, {col_sql} = ?, tipo_consulta = ?, banco_consulta = ?
                WHERE codigo_consulta = ?
            """
            cur.execute(sql, [c.descricao_consulta, c.sql_consulta, c.tipo_consulta, c.banco_consulta, c.codigo_consulta])
        else:
            sql = f"""
                INSERT INTO USER_geoapolo_consultas (codigo_consulta, descricao_consulta, {col_sql}, tipo_consulta, banco_consulta)
                VALUES (?, ?, ?, ?, ?)
            """
            cur.execute(sql, [c.codigo_consulta, c.descricao_consulta, c.sql_consulta, c.tipo_consulta, c.banco_consulta])
        self.conn.commit()
        return True

    def excluir_consulta(self, codigo_consulta: str) -> bool:
        """Remove consulta e suas permissões associadas."""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM USER_geoapolo_permissaoconsulta WHERE codigo_consulta = ?", [codigo_consulta])
        cur.execute("DELETE FROM USER_geoapolo_consultas WHERE codigo_consulta = ?", [codigo_consulta])
        self.conn.commit()
        return True

    def listar_permissoes_consulta(self, codigo_consulta: str) -> List[PermissaoConsultaDTO]:
        """Lista permissões de usuários para determinada consulta."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT p.usucod, p.codigo_consulta, COALESCE(c.descricao_consulta, ''), p.autorizacao
            FROM USER_geoapolo_permissaoconsulta p {nolock}
            LEFT JOIN USER_geoapolo_consultas c {nolock} ON p.codigo_consulta = c.codigo_consulta
            WHERE p.codigo_consulta = ?
            ORDER BY p.usucod ASC
        """
        cur.execute(sql, [codigo_consulta])
        return [
            PermissaoConsultaDTO(
                usucod=str(r[0]),
                codigo_consulta=str(r[1]),
                descricao_consulta=str(r[2]),
                autorizacao=str(r[3] or "S"),
            )
            for r in cur.fetchall()
        ]

    def atualizar_permissao_consulta(self, usucod: str, codigo_consulta: str, autorizacao: str) -> bool:
        """Define se o usuário está autorizado a ver os dados da consulta (A/S = Autorizado, N/B = Bloqueado)."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT 1 FROM USER_geoapolo_permissaoconsulta WHERE usucod = ? AND codigo_consulta = ?",
            [usucod, codigo_consulta],
        )
        if cur.fetchone():
            cur.execute(
                "UPDATE USER_geoapolo_permissaoconsulta SET autorizacao = ? WHERE usucod = ? AND codigo_consulta = ?",
                [autorizacao, usucod, codigo_consulta],
            )
        else:
            cur.execute(
                "INSERT INTO USER_geoapolo_permissaoconsulta (usucod, codigo_consulta, autorizacao) VALUES (?, ?, ?)",
                [usucod, codigo_consulta, autorizacao],
            )
        self.conn.commit()
        return True

    def remover_permissao_consulta(self, usucod: str, codigo_consulta: str) -> bool:
        """Remove a permissão de um usuário para uma consulta."""
        cur = self.conn.cursor()
        cur.execute(
            "DELETE FROM USER_geoapolo_permissaoconsulta WHERE usucod = ? AND codigo_consulta = ?",
            [usucod, codigo_consulta],
        )
        self.conn.commit()
        return True

    def listar_grupos_usuarios(self) -> List[Tuple[str, str]]:
        """Lista grupos de usuários (codigo_grupo, descricao)."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        try:
            sql = f"SELECT codigo_grupo, descricao FROM USER_geoapolo_grupo {nolock} ORDER BY descricao ASC"
            cur.execute(sql)
            return [(str(r[0]), str(r[1] or "")) for r in cur.fetchall()]
        except Exception:
            return []

    def listar_usuarios_por_grupo(self, grupo: Optional[str] = None) -> List[Tuple[str, str]]:
        """Lista usuários ativos, opcionalmente filtrados pelo grupo (nome ou código). Retorna lista de (usucod, nome)."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        try:
            if grupo and grupo.strip() and grupo.upper() != "TODOS":
                # Tenta filtrar por grupo (JOIN USER_geoapolo_grupousuario)
                sql = f"""
                    SELECT u.usucod, COALESCE(u.nome_completo, u.usunome, u.login, u.usucod)
                    FROM USER_geoapolo_usuarios u {nolock}
                    INNER JOIN USER_geoapolo_grupousuario ggu {nolock} ON u.usucod = ggu.usucod
                    INNER JOIN USER_geoapolo_grupo gu {nolock} ON ggu.codigo_grupo = gu.codigo_grupo
                    WHERE (gu.descricao = ? OR CAST(gu.codigo_grupo AS VARCHAR) = ?)
                      AND (u.flagativo = 'A' OR u.flagativo IS NULL)
                    ORDER BY u.usucod ASC
                """
                cur.execute(sql, [grupo, grupo])
                rows = cur.fetchall()
                if rows:
                    return [(str(r[0]), str(r[1] or r[0])) for r in rows]
                # Fallback se não encontrou no join: retorna vazio ou tenta coluna grupo
            sql = f"""
                SELECT usucod, COALESCE(nome_completo, usunome, login, usucod)
                FROM USER_geoapolo_usuarios {nolock}
                WHERE (flagativo = 'A' OR flagativo IS NULL)
                ORDER BY usucod ASC
            """
            cur.execute(sql)
            return [(str(r[0]), str(r[1] or r[0])) for r in cur.fetchall()]
        except Exception:
            return self.listar_usuarios_sistema()

    def listar_usuarios_sistema(self) -> List[Tuple[str, str]]:
        """Lista usuários do sistema para vinculação de permissões."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        try:
            sql = f"""
                SELECT usucod, COALESCE(nome_completo, usunome, login, usucod)
                FROM USER_geoapolo_usuarios {nolock}
                ORDER BY usucod ASC
            """
            cur.execute(sql)
            return [(str(r[0]), str(r[1] or r[0])) for r in cur.fetchall()]
        except Exception:
            return []

    def aplicar_permissao_grupo_ou_usuario(
        self,
        codigo_consulta: str,
        autorizacao: str,
        usucod: Optional[str] = None,
        grupo: Optional[str] = None,
    ) -> int:
        """
        Aplica permissão para um usuário específico ou para todos os membros de um grupo.
        Retorna a quantidade de usuários atualizados.
        """
        if usucod and usucod.strip():
            self.atualizar_permissao_consulta(usucod.strip(), codigo_consulta, autorizacao)
            return 1
        elif grupo and grupo.strip():
            usuarios = self.listar_usuarios_por_grupo(grupo.strip())
            count = 0
            for u_cod, _ in usuarios:
                self.atualizar_permissao_consulta(u_cod, codigo_consulta, autorizacao)
                count += 1
            return count
        return 0

    def clonar_permissoes_consulta(self, usucod_origem: str, usucod_destino: str) -> int:
        """
        Copia todas as permissões de consultas de um usuário para outro (unt_cadconsulta - GroupBox4).
        Retorna o número de permissões clonadas.
        """
        cur = self.conn.cursor()
        nolock = self._nolock()
        cur.execute(
            f"SELECT codigo_consulta, autorizacao FROM USER_geoapolo_permissaoconsulta {nolock} WHERE usucod = ?",
            [usucod_origem],
        )
        rows = cur.fetchall()
        count = 0
        for cod_cons, aut in rows:
            self.atualizar_permissao_consulta(usucod_destino, str(cod_cons), str(aut))
            count += 1
        return count

    def executar_sql_dinamico(
        self,
        sql: str,
        params: Optional[List[Any]] = None,
        banco: Optional[str] = None
    ) -> ResultadoConsultaDTO:
        """Executa instrução SQL parametrizada retornando colunas e linhas, roteando para MySQL se banco for Aplicativo RCC ou SAVIC."""
        banco_upper = (banco or "").strip().upper()
        if banco_upper in ("APLICATIVO RCC", "APLICATIVO"):
            return self._executar_sql_aplicativo_rcc(sql, params)
        elif banco_upper == "SAVIC":
            return self._executar_sql_savic(sql, params)

        cur = self.conn.cursor()
        try:
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)

            # Para consultas SQL Server com DECLARE/SET múltiplos, avança até o conjunto de resultados
            if cur.description is None and hasattr(cur, "nextset"):
                while cur.nextset():
                    if cur.description:
                        break

            colunas = [d[0] for d in cur.description] if cur.description else []
            linhas = cur.fetchall() if cur.description else []
            return ResultadoConsultaDTO(
                colunas=colunas,
                linhas=[list(r) for r in linhas],
                total_registros=len(linhas),
                sucesso=True,
            )
        except Exception as exc:
            return ResultadoConsultaDTO(
                colunas=[],
                linhas=[],
                total_registros=0,
                sucesso=False,
                mensagem=f"Erro na execução da consulta: {str(exc)}",
            )

    def _executar_sql_aplicativo_rcc(self, sql: str, params: Optional[List[Any]] = None) -> ResultadoConsultaDTO:
        """Executa instrução SQL na base do Aplicativo RCC (MySQL via pymysql)."""
        try:
            from entidades.database import obter_conexao_aplicativo_rcc
            conn_app = obter_conexao_aplicativo_rcc()
        except Exception as exc:
            return ResultadoConsultaDTO(
                colunas=[],
                linhas=[],
                total_registros=0,
                sucesso=False,
                mensagem=str(exc)
            )

        try:
            with conn_app.cursor() as cur:
                sql_mysql = sql
                if params and "?" in sql_mysql:
                    sql_mysql = sql_mysql.replace("?", "%s")
                if params:
                    cur.execute(sql_mysql, params)
                else:
                    cur.execute(sql_mysql)

                rows = cur.fetchall()
                if cur.description:
                    colunas = [d[0] for d in cur.description]
                else:
                    colunas = []

                linhas_formatadas = []
                for row in rows:
                    if isinstance(row, dict):
                        linhas_formatadas.append([row.get(col) for col in colunas])
                    else:
                        linhas_formatadas.append(list(row))

                return ResultadoConsultaDTO(
                    colunas=colunas,
                    linhas=linhas_formatadas,
                    total_registros=len(linhas_formatadas),
                    sucesso=True
                )
        except Exception as exc:
            return ResultadoConsultaDTO(
                colunas=[],
                linhas=[],
                total_registros=0,
                sucesso=False,
                mensagem=f"Erro de sintaxe ou execução SQL no Aplicativo RCC:\n\n{str(exc)}"
            )
        finally:
            try:
                conn_app.close()
            except Exception:
                pass

    def _executar_sql_savic(self, sql: str, params: Optional[List[Any]] = None) -> ResultadoConsultaDTO:
        """Executa instrução SQL na base do SAVIC (MySQL via pymysql)."""
        try:
            from config_banco import ConfigManager
            config_mgr = ConfigManager()
            settings = config_mgr.load_savic_settings()
            credentials = config_mgr.get_savic_credentials()
            host = str(settings.get("host") or "").strip()
            db = str(settings.get("database") or "").strip()
            user = str(credentials.get("user") or "").strip()

            if not host or not db or not user:
                return ResultadoConsultaDTO(
                    colunas=[],
                    linhas=[],
                    total_registros=0,
                    sucesso=False,
                    mensagem="Solicite ao Administrador a configuração de acesso aos dados do SAVIC"
                )

            from entidades.database import obter_conexao_savic
            conn_savic = obter_conexao_savic()
        except Exception as exc:
            return ResultadoConsultaDTO(
                colunas=[],
                linhas=[],
                total_registros=0,
                sucesso=False,
                mensagem="Solicite ao Administrador a configuração de acesso aos dados do SAVIC"
            )

        try:
            with conn_savic.cursor() as cur:
                sql_mysql = sql
                if params and "?" in sql_mysql:
                    sql_mysql = sql_mysql.replace("?", "%s")
                if params:
                    cur.execute(sql_mysql, params)
                else:
                    cur.execute(sql_mysql)

                rows = cur.fetchall()
                if cur.description:
                    colunas = [d[0] for d in cur.description]
                else:
                    colunas = []

                linhas_formatadas = []
                for row in rows:
                    if isinstance(row, dict):
                        linhas_formatadas.append([row.get(col) for col in colunas])
                    else:
                        linhas_formatadas.append(list(row))

                return ResultadoConsultaDTO(
                    colunas=colunas,
                    linhas=linhas_formatadas,
                    total_registros=len(linhas_formatadas),
                    sucesso=True
                )
        except Exception as exc:
            return ResultadoConsultaDTO(
                colunas=[],
                linhas=[],
                total_registros=0,
                sucesso=False,
                mensagem=f"Erro de sintaxe ou execução SQL no SAVIC:\n\n{str(exc)}"
            )
        finally:
            try:
                conn_savic.close()
            except Exception:
                pass

