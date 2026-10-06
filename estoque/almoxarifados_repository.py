"""
Repositório de Dados para Gestão de Almoxarifados e Multi-Almoxarifado.
GeoApolo V5
Clean Architecture & Suporte a SQL Server com Hints WITH (NOLOCK).
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from entidades.database import obter_conexao_banco

logger = logging.getLogger(__name__)


class AlmoxarifadosRepository:
    """Gerencia a persistência de Almoxarifados e Saldos de Produtos por Almoxarifado."""

    def __init__(self, connection=None):
        self._conn = connection
        if self._conn is not None:
            self.garantir_tabelas()

    @property
    def _is_sql_server(self) -> bool:
        if self._conn is None:
            return True
        return "sqlite" not in getattr(type(self._conn), "__module__", "").lower()

    def _nolock(self) -> str:
        return "WITH (NOLOCK)" if self._is_sql_server else ""

    def _get_cursor(self):
        if self._conn is None:
            self._conn = obter_conexao_banco()
            self.garantir_tabelas()
        return self._conn.cursor()

    def garantir_tabelas(self):
        """Garante que as tabelas de almoxarifados existam no banco de dados."""
        if not self._is_sql_server:
            # Em SQLite (testes unitários), tabelas são criadas pelo setUp do teste
            return
        try:
            cursor = self._get_cursor()
            # 1. user_geoapolo_almoxarifados
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[user_geoapolo_almoxarifados]') AND type in (N'U'))
                BEGIN
                    CREATE TABLE [dbo].[user_geoapolo_almoxarifados] (
                        [codigo_almoxarifado] VARCHAR(20) NOT NULL,
                        [descricao]           VARCHAR(100) NOT NULL,
                        [centro_custo]        VARCHAR(30) NULL,
                        [data_criacao]        DATETIME2(0) NOT NULL DEFAULT SYSDATETIME(),
                        [finalidade]          VARCHAR(500) NULL,
                        [status]              CHAR(1) NOT NULL DEFAULT 'A',
                        CONSTRAINT [PK_user_geoapolo_almoxarifados] PRIMARY KEY CLUSTERED ([codigo_almoxarifado] ASC)
                    );
                    INSERT INTO [dbo].[user_geoapolo_almoxarifados] 
                        ([codigo_almoxarifado], [descricao], [centro_custo], [data_criacao], [finalidade], [status])
                    VALUES 
                        ('01', 'ALMOXARIFADO CENTRAL / GERAL', '1.01', SYSDATETIME(), 'Almoxarifado geral principal', 'A');
                END
            """)
            # 2. user_geoapolo_produtos_almoxarifados
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[user_geoapolo_produtos_almoxarifados]') AND type in (N'U'))
                BEGIN
                    CREATE TABLE [dbo].[user_geoapolo_produtos_almoxarifados] (
                        [id_produto_almoxarifado]  BIGINT IDENTITY(1,1) NOT NULL,
                        [codigo_almoxarifado]      VARCHAR(20) NOT NULL,
                        [prodcod]                  NUMERIC(8,0) NOT NULL,
                        [saldo_atual]              DECIMAL(18,6) NOT NULL DEFAULT 0,
                        [data_ultima_movimentacao] DATETIME2(0) NULL,
                        [data_vinculo]             DATETIME2(0) NOT NULL DEFAULT SYSDATETIME(),
                        [status]                   CHAR(1) NOT NULL DEFAULT 'A',
                        CONSTRAINT [PK_user_geoapolo_prod_almox] PRIMARY KEY CLUSTERED ([id_produto_almoxarifado] ASC),
                        CONSTRAINT [UQ_user_geoapolo_prod_almox] UNIQUE NONCLUSTERED ([codigo_almoxarifado], [prodcod])
                    );
                END
            """)
            if hasattr(self._conn, "commit"):
                self._conn.commit()
        except Exception as ex:
            logger.warning("Verificação de tabelas de almoxarifado: %s", ex)

    def listar_almoxarifados(self, apenas_ativos: bool = False) -> List[Dict[str, Any]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        date_expr = "CONVERT(VARCHAR(19), a.data_criacao, 120)" if self._is_sql_server else "a.data_criacao"
        sql = f"""
            SELECT
                a.codigo_almoxarifado,
                a.descricao,
                a.centro_custo,
                {date_expr} AS data_criacao,
                COALESCE(a.finalidade, '') AS finalidade,
                a.status,
                COALESCE(cc.geocctrlnome, '') AS nome_centro_custo
            FROM user_geoapolo_almoxarifados a {nolock}
            LEFT JOIN USER_geoapolo_centrocontrole cc {nolock}
                   ON a.centro_custo = cc.geocctrlcodestr
        """
        if apenas_ativos:
            sql += " WHERE a.status = 'A'"
        sql += " ORDER BY a.codigo_almoxarifado ASC"

        cursor.execute(sql)
        cols = [c[0].lower() for c in cursor.description]
        return [dict(zip(cols, r)) for r in cursor.fetchall()]

    def obter_almoxarifado(self, codigo: str) -> Optional[Dict[str, Any]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        date_expr = "CONVERT(VARCHAR(19), data_criacao, 120)" if self._is_sql_server else "data_criacao"
        sql = f"""
            SELECT
                codigo_almoxarifado,
                descricao,
                centro_custo,
                {date_expr} AS data_criacao,
                COALESCE(finalidade, '') AS finalidade,
                status
            FROM user_geoapolo_almoxarifados {nolock}
            WHERE codigo_almoxarifado = ?
        """
        cursor.execute(sql, [codigo])
        row = cursor.fetchone()
        if not row:
            return None
        cols = [c[0].lower() for c in cursor.description]
        return dict(zip(cols, row))

    def salvar_almoxarifado(
        self,
        codigo: str,
        descricao: str,
        centro_custo: str,
        finalidade: str,
        status: str = "A",
    ) -> bool:
        cursor = self._get_cursor()
        cursor.execute("SELECT 1 FROM user_geoapolo_almoxarifados WHERE codigo_almoxarifado = ?", [codigo])
        existe = cursor.fetchone() is not None

        if existe:
            sql = """
                UPDATE user_geoapolo_almoxarifados
                SET descricao = ?, centro_custo = ?, finalidade = ?, status = ?
                WHERE codigo_almoxarifado = ?
            """
            cursor.execute(sql, [descricao, centro_custo, finalidade, status, codigo])
        else:
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = """
                INSERT INTO user_geoapolo_almoxarifados
                (codigo_almoxarifado, descricao, centro_custo, finalidade, status, data_criacao)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(sql, [codigo, descricao, centro_custo, finalidade, status, agora])

        if hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def excluir_almoxarifado(self, codigo: str) -> bool:
        cursor = self._get_cursor()
        # Não permite excluir se houver produtos com saldo
        cursor.execute("""
            SELECT COUNT(1) FROM user_geoapolo_produtos_almoxarifados
            WHERE codigo_almoxarifado = ? AND saldo_atual <> 0
        """, [codigo])
        row = cursor.fetchone()
        if row and row[0] > 0:
            raise ValueError(f"Não é possível excluir o almoxarifado {codigo} pois existem produtos com saldo estocado nele.")

        cursor.execute("DELETE FROM user_geoapolo_produtos_almoxarifados WHERE codigo_almoxarifado = ?", [codigo])
        cursor.execute("DELETE FROM user_geoapolo_almoxarifados WHERE codigo_almoxarifado = ?", [codigo])
        if hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    # -------------------------------------------------------------------------
    # VÍNCULO MULTI-ALMOXARIFADO DE PRODUTOS
    # -------------------------------------------------------------------------
    def listar_almoxarifados_produto(self, prodcod: int) -> List[Dict[str, Any]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT
                pa.id_produto_almoxarifado,
                pa.codigo_almoxarifado,
                a.descricao AS nome_almoxarifado,
                pa.prodcod,
                COALESCE(p.prodnome, '') AS prodnome,
                pa.saldo_atual,
                pa.data_ultima_movimentacao,
                pa.data_vinculo,
                pa.status
            FROM user_geoapolo_produtos_almoxarifados pa {nolock}
            INNER JOIN user_geoapolo_almoxarifados a {nolock}
                    ON pa.codigo_almoxarifado = a.codigo_almoxarifado
            LEFT JOIN USER_geoapolo_produtos p {nolock}
                   ON pa.prodcod = p.prodcod
            WHERE pa.prodcod = ?
            ORDER BY pa.codigo_almoxarifado ASC
        """
        cursor.execute(sql, [prodcod])
        cols = [c[0].lower() for c in cursor.description]
        return [dict(zip(cols, r)) for r in cursor.fetchall()]

    def vincular_produto(self, codigo_almoxarifado: str, prodcod: int, saldo_inicial: float = 0.0) -> bool:
        cursor = self._get_cursor()
        cursor.execute("""
            SELECT id_produto_almoxarifado FROM user_geoapolo_produtos_almoxarifados
            WHERE codigo_almoxarifado = ? AND prodcod = ?
        """, [codigo_almoxarifado, prodcod])
        row = cursor.fetchone()
        if row:
            cursor.execute("""
                UPDATE user_geoapolo_produtos_almoxarifados
                SET status = 'A'
                WHERE id_produto_almoxarifado = ?
            """, [row[0]])
        else:
            agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO user_geoapolo_produtos_almoxarifados
                (codigo_almoxarifado, prodcod, saldo_atual, data_ultima_movimentacao, data_vinculo, status)
                VALUES (?, ?, ?, ?, ?, 'A')
            """, [codigo_almoxarifado, prodcod, saldo_inicial, agora, agora])

        if hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def desvincular_produto(self, codigo_almoxarifado: str, prodcod: int) -> bool:
        cursor = self._get_cursor()
        cursor.execute("""
            SELECT saldo_atual FROM user_geoapolo_produtos_almoxarifados
            WHERE codigo_almoxarifado = ? AND prodcod = ?
        """, [codigo_almoxarifado, prodcod])
        row = cursor.fetchone()
        if row and float(row[0]) != 0:
            raise ValueError("Não é possível desvincular o produto com saldo diferente de zero neste almoxarifado.")

        cursor.execute("""
            DELETE FROM user_geoapolo_produtos_almoxarifados
            WHERE codigo_almoxarifado = ? AND prodcod = ?
        """, [codigo_almoxarifado, prodcod])
        if hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def obter_saldo_produto(self, codigo_almoxarifado: str, prodcod: int) -> float:
        cursor = self._get_cursor()
        nolock = self._nolock()
        cursor.execute(f"""
            SELECT saldo_atual FROM user_geoapolo_produtos_almoxarifados {nolock}
            WHERE codigo_almoxarifado = ? AND prodcod = ?
        """, [codigo_almoxarifado, prodcod])
        row = cursor.fetchone()
        return float(row[0]) if row and row[0] is not None else 0.0

    def atualizar_saldo(self, codigo_almoxarifado: str, prodcod: int, delta_qtd: float, data_mov: Optional[str] = None) -> float:
        cursor = self._get_cursor()
        # Garante vínculo
        cursor.execute("""
            SELECT id_produto_almoxarifado, saldo_atual
            FROM user_geoapolo_produtos_almoxarifados
            WHERE codigo_almoxarifado = ? AND prodcod = ?
        """, [codigo_almoxarifado, prodcod])
        row = cursor.fetchone()
        agora = data_mov or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if row:
            id_pa = row[0]
            novo_saldo = float(row[1]) + delta_qtd
            cursor.execute("""
                UPDATE user_geoapolo_produtos_almoxarifados
                SET saldo_atual = ?, data_ultima_movimentacao = ?
                WHERE id_produto_almoxarifado = ?
            """, [novo_saldo, agora, id_pa])
        else:
            novo_saldo = max(0.0, delta_qtd)
            cursor.execute("""
                INSERT INTO user_geoapolo_produtos_almoxarifados
                (codigo_almoxarifado, prodcod, saldo_atual, data_ultima_movimentacao, data_vinculo, status)
                VALUES (?, ?, ?, ?, ?, 'A')
            """, [codigo_almoxarifado, prodcod, novo_saldo, agora, agora])

        if hasattr(self._conn, "commit"):
            self._conn.commit()
        return novo_saldo

    # -------------------------------------------------------------------------
    # RELATÓRIOS DO ALMOXARIFADO
    # -------------------------------------------------------------------------
    def obter_relatorio_saldos(self, codigo_almoxarifado: str = "") -> List[Dict[str, Any]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        date_expr = "CONVERT(VARCHAR(10), pa.data_ultima_movimentacao, 103)" if self._is_sql_server else "pa.data_ultima_movimentacao"
        sql = f"""
            SELECT
                a.codigo_almoxarifado,
                a.descricao AS nome_almoxarifado,
                p.prodcod,
                p.prodnome,
                COALESCE(p.unidademedida, COALESCE(p.tamanho, 'UN')) AS unidade,
                pa.saldo_atual,
                {date_expr} AS data_ult_mov,
                COALESCE(m.descricao_marca, '') AS marca
            FROM user_geoapolo_produtos_almoxarifados pa {nolock}
            INNER JOIN user_geoapolo_almoxarifados a {nolock}
                    ON pa.codigo_almoxarifado = a.codigo_almoxarifado
            INNER JOIN USER_geoapolo_produtos p {nolock}
                    ON pa.prodcod = p.prodcod
            LEFT JOIN USER_geoapolo_produto_marcas m {nolock}
                   ON p.codigo_marca = m.codigo_marca
        """
        params = []
        if codigo_almoxarifado:
            sql += " WHERE a.codigo_almoxarifado = ?"
            params.append(codigo_almoxarifado)
        sql += " ORDER BY a.codigo_almoxarifado, p.prodnome"

        cursor.execute(sql, params)
        cols = [c[0].lower() for c in cursor.description]
        return [dict(zip(cols, r)) for r in cursor.fetchall()]

    def obter_relatorio_aquisicoes_recentes(self, codigo_almoxarifado: str = "", dias: int = 60) -> List[Dict[str, Any]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        date_expr = "CONVERT(VARCHAR(10), me.data_movimento, 103)" if self._is_sql_server else "me.data_movimento"
        date_filter = "DATEADD(DAY, -?, GETDATE())" if self._is_sql_server else "date('now', '-' || ? || ' days')"
        sql = f"""
            SELECT
                COALESCE(me.codigo_almoxarifado, '01') AS codigo_almoxarifado,
                COALESCE(a.descricao, 'GERAL') AS nome_almoxarifado,
                {date_expr} AS data_mov,
                p.prodcod,
                p.prodnome,
                COALESCE(p.unidademedida, COALESCE(p.tamanho, 'UN')) AS unidade,
                me.quantidade,
                me.valor_unitario,
                me.valor_total,
                COALESCE(me.numero_lote, '') AS numero_lote,
                COALESCE(me.doc_origem, '') AS doc_origem,
                COALESCE(f.nome_razaosocial, me.codigo_fornecedor) AS fornecedor
            FROM USER_geoapolo_mov_estq me {nolock}
            INNER JOIN USER_geoapolo_produtos p {nolock}
                    ON me.prodcod = p.prodcod
            LEFT JOIN user_geoapolo_almoxarifados a {nolock}
                   ON me.codigo_almoxarifado = a.codigo_almoxarifado
            LEFT JOIN USER_geoapolo_entidade f {nolock}
                   ON CAST(me.codigo_fornecedor AS VARCHAR) = CAST(f.entcod AS VARCHAR)
            WHERE me.tipo_movimento = 'E'
              AND me.data_movimento >= {date_filter}
        """
        params = [dias]
        if codigo_almoxarifado:
            sql += " AND me.codigo_almoxarifado = ?"
            params.append(codigo_almoxarifado)
        sql += " ORDER BY me.data_movimento DESC"

        try:
            cursor.execute(sql, params)
            cols = [c[0].lower() for c in cursor.description]
            return [dict(zip(cols, r)) for r in cursor.fetchall()]
        except Exception:
            # Fallback se colunas extras não existirem na tabela histórica de movimentos
            return []
