"""
Repositório de Dados para Lotes de Produtos.
GeoApolo V5
Opera sobre a tabela user_geoapolo_produto_lote (SQL Server / SQLite).
"""

import logging
from typing import List, Optional, Tuple
from datetime import datetime

from .models import ProdutoLoteDTO

logger = logging.getLogger(__name__)


class LotesRepository:
    """Repositório de persistência de lotes de produtos."""

    def __init__(self, connection=None):
        self.conn = connection
        self._garantir_tabela()

    @property
    def _is_sql_server(self) -> bool:
        return self.conn is not None and not hasattr(self.conn, "isolation_level")

    def _get_cursor(self):
        if not self.conn:
            raise RuntimeError("Conexão com o banco de dados não estabelecida.")
        return self.conn.cursor()

    def commit(self):
        if self.conn:
            try:
                self.conn.commit()
            except Exception:
                pass

    def rollback(self):
        if self.conn:
            try:
                self.conn.rollback()
            except Exception:
                pass

    def _nolock(self) -> str:
        return "WITH (NOLOCK)" if self._is_sql_server else ""

    def _garantir_tabela(self):
        """Garante a existência da tabela user_geoapolo_produto_lote."""
        if not self.conn:
            return
        try:
            cur = self._get_cursor()
            if self._is_sql_server:
                cur.execute("""
                    IF OBJECT_ID('user_geoapolo_produto_lote', 'U') IS NULL
                    BEGIN
                        CREATE TABLE user_geoapolo_produto_lote
                        (
                            ID_PRODUTO_LOTE BIGINT IDENTITY(1,1) NOT NULL,
                            prodcod numeric(8,0) NOT NULL,
                            NUMERO_LOTE     VARCHAR(50) NOT NULL,
                            DATA_FABRICACAO DATE NULL,
                            DATA_VALIDADE   DATE NULL,
                            QUANTIDADE_INICIAL DECIMAL(18,6) NOT NULL DEFAULT 0,
                            QUANTIDADE_ATUAL   DECIMAL(18,6) NOT NULL DEFAULT 0,
                            DATA_ENTRADA DATETIME2(0) NOT NULL DEFAULT SYSDATETIME(),
                            entcod_fornecedor numeric(8,0) NULL,
                            STATUS CHAR(1) NOT NULL DEFAULT 'A',
                            OBSERVACAO VARCHAR(500) NULL,
                            DATA_CADASTRO DATETIME2(0) NOT NULL DEFAULT SYSDATETIME(),
                            usucod VARCHAR(20) NULL,

                            CONSTRAINT PK_PRODUTO_LOTE PRIMARY KEY (ID_PRODUTO_LOTE),
                            CONSTRAINT CK_PRODUTO_LOTE_STATUS CHECK (STATUS IN ('A','I')),
                            CONSTRAINT CK_PRODUTO_LOTE_QUANTIDADE CHECK (QUANTIDADE_INICIAL >= 0 AND QUANTIDADE_ATUAL >= 0)
                        );
                    END
                """)
            else:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_geoapolo_produto_lote (
                        ID_PRODUTO_LOTE INTEGER PRIMARY KEY AUTOINCREMENT,
                        prodcod INTEGER NOT NULL,
                        NUMERO_LOTE VARCHAR(50) NOT NULL,
                        DATA_FABRICACAO TEXT,
                        DATA_VALIDADE TEXT,
                        QUANTIDADE_INICIAL REAL NOT NULL DEFAULT 0,
                        QUANTIDADE_ATUAL REAL NOT NULL DEFAULT 0,
                        DATA_ENTRADA TEXT,
                        entcod_fornecedor INTEGER,
                        STATUS CHAR(1) NOT NULL DEFAULT 'A',
                        OBSERVACAO VARCHAR(500),
                        DATA_CADASTRO TEXT,
                        usucod VARCHAR(20)
                    )
                """)
            self.commit()
        except Exception as e:
            logger.warning("Aviso ao verificar tabela user_geoapolo_produto_lote: %s", e)

    def listar_lotes(
        self,
        prodcod: Optional[int] = None,
        termo: str = "",
        apenas_ativos: bool = False,
        limite: int = 300,
    ) -> List[ProdutoLoteDTO]:
        """Lista os lotes de produtos cadastrados com junção ao catálogo de produtos e fornecedores."""
        cur = self._get_cursor()
        nolock = self._nolock()
        where = []
        params = []

        if prodcod is not None and prodcod > 0:
            where.append("l.prodcod = ?")
            params.append(prodcod)

        if apenas_ativos:
            where.append("l.STATUS = 'A'")

        if termo and str(termo).strip():
            t = f"%{str(termo).strip().upper()}%"
            where.append("(UPPER(l.NUMERO_LOTE) LIKE ? OR UPPER(p.prodnome) LIKE ? OR CAST(l.prodcod AS VARCHAR) LIKE ?)")
            params.extend([t, t, t])

        where_str = f"WHERE {' AND '.join(where)}" if where else ""

    def _obter_join_fornecedor(self, cur):
        nolock = self._nolock()
        join_forn = ""
        col_forn = "'' AS nome_fornecedor"
        try:
            if self._is_sql_server:
                cur.execute("SELECT name FROM sysobjects WHERE name IN ('ENTIDADE', 'USER_geoapolo_entidades') AND xtype = 'U'")
                r = cur.fetchone()
                if r:
                    tab_ent = str(r[0]).strip()
                    join_forn = f"LEFT JOIN {tab_ent} f {nolock} ON l.entcod_fornecedor = f.entcod"
                    col_forn = "COALESCE(f.entnome, '') AS nome_fornecedor"
            else:
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('ENTIDADE', 'USER_geoapolo_entidades')")
                r = cur.fetchone()
                if r:
                    tab_ent = str(r[0]).strip()
                    join_forn = f"LEFT JOIN {tab_ent} f ON l.entcod_fornecedor = f.entcod"
                    col_forn = "COALESCE(f.entnome, '') AS nome_fornecedor"
        except Exception:
            pass
        return join_forn, col_forn

    def listar_lotes(
        self,
        prodcod: Optional[int] = None,
        termo: str = "",
        apenas_ativos: bool = False,
        limite: int = 500,
    ) -> List[ProdutoLoteDTO]:
        """Lista os lotes de produtos cadastrados com junção ao catálogo de produtos e fornecedores."""
        cur = self._get_cursor()
        nolock = self._nolock()
        where = []
        params = []

        if prodcod is not None and prodcod > 0:
            where.append("l.prodcod = ?")
            params.append(prodcod)

        if apenas_ativos:
            where.append("l.STATUS = 'A'")

        if termo and str(termo).strip():
            t = f"%{str(termo).strip().upper()}%"
            where.append("(UPPER(l.NUMERO_LOTE) LIKE ? OR UPPER(p.prodnome) LIKE ? OR CAST(l.prodcod AS VARCHAR) LIKE ?)")
            params.extend([t, t, t])

        where_str = f"WHERE {' AND '.join(where)}" if where else ""
        join_forn, col_forn = self._obter_join_fornecedor(cur)

        sql = f"""
            SELECT l.ID_PRODUTO_LOTE, l.prodcod,
                   COALESCE(p.prodnome, 'PRODUTO NÃO ENCONTRADO'),
                   l.NUMERO_LOTE, l.DATA_FABRICACAO, l.DATA_VALIDADE,
                   COALESCE(l.QUANTIDADE_INICIAL, 0),
                   COALESCE(l.QUANTIDADE_ATUAL, 0),
                   l.DATA_ENTRADA, l.entcod_fornecedor,
                   {col_forn},
                   COALESCE(l.STATUS, 'A'),
                   COALESCE(l.OBSERVACAO, ''),
                   l.DATA_CADASTRO,
                   COALESCE(l.usucod, '')
            FROM user_geoapolo_produto_lote l {nolock}
            LEFT JOIN USER_geoapolo_produtos p {nolock} ON l.prodcod = p.prodcod
            {join_forn}
            {where_str}
            ORDER BY l.DATA_CADASTRO DESC, l.ID_PRODUTO_LOTE DESC
        """
        cur.execute(sql, params)
        lotes = []
        for r in cur.fetchall()[:limite]:
            d_fab = str(r[4])[:10] if r[4] else ""
            d_val = str(r[5])[:10] if r[5] else ""
            d_ent = str(r[8])[:19] if r[8] else ""
            d_cad = str(r[13])[:19] if r[13] else ""
            forn_cod = int(r[9]) if r[9] is not None else None
            lotes.append(ProdutoLoteDTO(
                id_produto_lote=int(r[0]),
                prodcod=int(r[1]),
                prodnome=str(r[2] or "").strip(),
                numero_lote=str(r[3] or "").strip(),
                data_fabricacao=d_fab,
                data_validade=d_val,
                quantidade_inicial=float(r[6] or 0.0),
                quantidade_atual=float(r[7] or 0.0),
                data_entrada=d_ent,
                entcod_fornecedor=forn_cod,
                nome_fornecedor=str(r[10] or "").strip(),
                status=str(r[11] or "A").strip().upper(),
                observacao=str(r[12] or "").strip(),
                data_cadastro=d_cad,
                usucod=str(r[14] or "").strip(),
            ))
        return lotes

    def obter_lote_por_id(self, id_produto_lote: int) -> Optional[ProdutoLoteDTO]:
        """Obtém os dados completos de um lote pelo ID."""
        cur = self._get_cursor()
        nolock = self._nolock()
        join_forn, col_forn = self._obter_join_fornecedor(cur)
        sql = f"""
            SELECT l.ID_PRODUTO_LOTE, l.prodcod,
                   COALESCE(p.prodnome, ''),
                   l.NUMERO_LOTE, l.DATA_FABRICACAO, l.DATA_VALIDADE,
                   COALESCE(l.QUANTIDADE_INICIAL, 0),
                   COALESCE(l.QUANTIDADE_ATUAL, 0),
                   l.DATA_ENTRADA, l.entcod_fornecedor,
                   {col_forn},
                   COALESCE(l.STATUS, 'A'),
                   COALESCE(l.OBSERVACAO, ''),
                   l.DATA_CADASTRO,
                   COALESCE(l.usucod, '')
            FROM user_geoapolo_produto_lote l {nolock}
            LEFT JOIN USER_geoapolo_produtos p {nolock} ON l.prodcod = p.prodcod
            {join_forn}
            WHERE l.ID_PRODUTO_LOTE = ?
        """
        cur.execute(sql, [id_produto_lote])
        r = cur.fetchone()
        if not r:
            return None
        d_fab = str(r[4])[:10] if r[4] else ""
        d_val = str(r[5])[:10] if r[5] else ""
        d_ent = str(r[8])[:19] if r[8] else ""
        d_cad = str(r[13])[:19] if r[13] else ""
        forn_cod = int(r[9]) if r[9] is not None else None
        return ProdutoLoteDTO(
            id_produto_lote=int(r[0]),
            prodcod=int(r[1]),
            prodnome=str(r[2] or "").strip(),
            numero_lote=str(r[3] or "").strip(),
            data_fabricacao=d_fab,
            data_validade=d_val,
            quantidade_inicial=float(r[6] or 0.0),
            quantidade_atual=float(r[7] or 0.0),
            data_entrada=d_ent,
            entcod_fornecedor=forn_cod,
            nome_fornecedor=str(r[10] or "").strip(),
            status=str(r[11] or "A").strip().upper(),
            observacao=str(r[12] or "").strip(),
            data_cadastro=d_cad,
            usucod=str(r[14] or "").strip(),
        )

    def obter_lote_por_numero(self, prodcod: int, numero_lote: str) -> Optional[ProdutoLoteDTO]:
        """Obtém um lote específico dado o produto e número do lote."""
        if not numero_lote or not str(numero_lote).strip():
            return None
        cur = self._get_cursor()
        nolock = self._nolock()
        join_forn, col_forn = self._obter_join_fornecedor(cur)
        sql = f"""
            SELECT l.ID_PRODUTO_LOTE, l.prodcod,
                   COALESCE(p.prodnome, ''),
                   l.NUMERO_LOTE, l.DATA_FABRICACAO, l.DATA_VALIDADE,
                   COALESCE(l.QUANTIDADE_INICIAL, 0),
                   COALESCE(l.QUANTIDADE_ATUAL, 0),
                   l.DATA_ENTRADA, l.entcod_fornecedor,
                   {col_forn},
                   COALESCE(l.STATUS, 'A'),
                   COALESCE(l.OBSERVACAO, ''),
                   l.DATA_CADASTRO,
                   COALESCE(l.usucod, '')
            FROM user_geoapolo_produto_lote l {nolock}
            LEFT JOIN USER_geoapolo_produtos p {nolock} ON l.prodcod = p.prodcod
            {join_forn}
            WHERE l.prodcod = ? AND UPPER(l.NUMERO_LOTE) = ?
        """
        cur.execute(sql, [prodcod, str(numero_lote).strip().upper()])
        r = cur.fetchone()
        if not r:
            return None
        d_fab = str(r[4])[:10] if r[4] else ""
        d_val = str(r[5])[:10] if r[5] else ""
        d_ent = str(r[8])[:19] if r[8] else ""
        d_cad = str(r[13])[:19] if r[13] else ""
        forn_cod = int(r[9]) if r[9] is not None else None
        return ProdutoLoteDTO(
            id_produto_lote=int(r[0]),
            prodcod=int(r[1]),
            prodnome=str(r[2] or "").strip(),
            numero_lote=str(r[3] or "").strip(),
            data_fabricacao=d_fab,
            data_validade=d_val,
            quantidade_inicial=float(r[6] or 0.0),
            quantidade_atual=float(r[7] or 0.0),
            data_entrada=d_ent,
            entcod_fornecedor=forn_cod,
            nome_fornecedor=str(r[10] or "").strip(),
            status=str(r[11] or "A").strip().upper(),
            observacao=str(r[12] or "").strip(),
            data_cadastro=d_cad,
            usucod=str(r[14] or "").strip(),
        )

    def produto_controla_lote(self, prodcod: int) -> bool:
        """
        Verifica se o produto possui controle de lote:
        1. No catálogo do Alvo (PRODUTO.ProdCtrlEstqLote = 'Sim' ou começa com 'S')
        2. Na tabela de lotes (user_geoapolo_produto_lote com registros para o produto)
        3. No histórico de movimentações com lote informado (USER_geoapolo_movimentacoes_estoque)
        """
        if not prodcod or prodcod <= 0:
            return False
        cur = self._get_cursor()
        nolock = self._nolock()

        # 1. Checa PRODUTO (Alvo)
        try:
            if self._is_sql_server:
                cur.execute("SELECT 1 FROM sysobjects WHERE name = 'PRODUTO' AND xtype = 'U'")
            else:
                cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name = 'PRODUTO'")
            if cur.fetchone():
                cur.execute(f"SELECT ProdCtrlEstqLote FROM PRODUTO {nolock} WHERE ProdCodEstr = ? OR ProdCodEstr = CAST(? AS VARCHAR)", [str(prodcod), prodcod])
                r = cur.fetchone()
                if r and r[0] and str(r[0]).strip().upper().startswith("S"):
                    return True
        except Exception:
            pass

        # 2. Checa retrocompatibilidade com USER_geoapolo_produtos (se existir codigo_lote legado preenchido)
        try:
            cur.execute(f"SELECT codigo_lote FROM USER_geoapolo_produtos {nolock} WHERE prodcod = ?", [prodcod])
            r = cur.fetchone()
            if r and r[0] and str(r[0]).strip():
                return True
        except Exception:
            pass

        # 3. Checa se já existem lotes cadastrados na tabela user_geoapolo_produto_lote
        try:
            cur.execute(f"SELECT COUNT(1) FROM user_geoapolo_produto_lote {nolock} WHERE prodcod = ?", [prodcod])
            r = cur.fetchone()
            if r and r[0] > 0:
                return True
        except Exception:
            pass

        # 3. Checa histórico de movimentações com lote
        try:
            cur.execute(
                f"SELECT TOP 1 1 FROM USER_geoapolo_movimentacoes_estoque {nolock} WHERE prodcod = ? AND numero_lote IS NOT NULL AND RTRIM(LTRIM(numero_lote)) <> ''" if self._is_sql_server else
                f"SELECT 1 FROM USER_geoapolo_movimentacoes_estoque WHERE prodcod = ? AND numero_lote IS NOT NULL AND TRIM(numero_lote) <> '' LIMIT 1",
                [prodcod]
            )
            if cur.fetchone():
                return True
        except Exception:
            pass

        return False

    def lote_existe(self, prodcod: int, numero_lote: str) -> bool:
        """Verifica se determinado número de lote já existe para o produto informado."""
        if not numero_lote or not str(numero_lote).strip():
            return False
        cur = self._get_cursor()
        nolock = self._nolock()
        sql = f"SELECT 1 FROM user_geoapolo_produto_lote {nolock} WHERE prodcod = ? AND UPPER(NUMERO_LOTE) = ?"
        cur.execute(sql, [prodcod, str(numero_lote).strip().upper()])
        return cur.fetchone() is not None

    def salvar_lote(self, dto: ProdutoLoteDTO) -> int:
        """Insere ou atualiza um lote de produto e retorna o ID gerado/alterado."""
        cur = self._get_cursor()
        data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        d_fab = dto.data_fabricacao if dto.data_fabricacao and str(dto.data_fabricacao).strip() else None
        d_val = dto.data_validade if dto.data_validade and str(dto.data_validade).strip() else None

        if dto.id_produto_lote and dto.id_produto_lote > 0:
            sql = """
                UPDATE user_geoapolo_produto_lote
                SET prodcod = ?,
                    NUMERO_LOTE = ?,
                    DATA_FABRICACAO = ?,
                    DATA_VALIDADE = ?,
                    QUANTIDADE_INICIAL = ?,
                    QUANTIDADE_ATUAL = ?,
                    entcod_fornecedor = ?,
                    STATUS = ?,
                    OBSERVACAO = ?,
                    usucod = ?
                WHERE ID_PRODUTO_LOTE = ?
            """
            cur.execute(sql, [
                dto.prodcod,
                dto.numero_lote.strip().upper(),
                d_fab,
                d_val,
                dto.quantidade_inicial,
                dto.quantidade_atual,
                dto.entcod_fornecedor,
                dto.status.strip().upper() or "A",
                (dto.observacao or "").strip(),
                dto.usucod or "",
                dto.id_produto_lote,
            ])
            self.commit()
            return dto.id_produto_lote
        else:
            if self._is_sql_server:
                sql = """
                    INSERT INTO user_geoapolo_produto_lote (
                        prodcod, NUMERO_LOTE, DATA_FABRICACAO, DATA_VALIDADE,
                        QUANTIDADE_INICIAL, QUANTIDADE_ATUAL, DATA_ENTRADA,
                        entcod_fornecedor, STATUS, OBSERVACAO, DATA_CADASTRO, usucod
                    )
                    OUTPUT INSERTED.ID_PRODUTO_LOTE
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cur.execute(sql, [
                    dto.prodcod,
                    dto.numero_lote.strip().upper(),
                    d_fab,
                    d_val,
                    dto.quantidade_inicial,
                    dto.quantidade_atual,
                    dto.data_entrada or data_agora,
                    dto.entcod_fornecedor,
                    dto.status.strip().upper() or "A",
                    (dto.observacao or "").strip(),
                    data_agora,
                    dto.usucod or "",
                ])
                row = cur.fetchone()
                novo_id = int(row[0]) if row else 0
            else:
                sql = """
                    INSERT INTO user_geoapolo_produto_lote (
                        prodcod, NUMERO_LOTE, DATA_FABRICACAO, DATA_VALIDADE,
                        QUANTIDADE_INICIAL, QUANTIDADE_ATUAL, DATA_ENTRADA,
                        entcod_fornecedor, STATUS, OBSERVACAO, DATA_CADASTRO, usucod
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cur.execute(sql, [
                    dto.prodcod,
                    dto.numero_lote.strip().upper(),
                    d_fab,
                    d_val,
                    dto.quantidade_inicial,
                    dto.quantidade_atual,
                    dto.data_entrada or data_agora,
                    dto.entcod_fornecedor,
                    dto.status.strip().upper() or "A",
                    (dto.observacao or "").strip(),
                    data_agora,
                    dto.usucod or "",
                ])
                novo_id = cur.lastrowid or 0
            self.commit()
            return novo_id

    def inativar_lote(self, id_produto_lote: int) -> bool:
        """Altera o status do lote para Inativo ('I')."""
        cur = self._get_cursor()
        cur.execute("UPDATE user_geoapolo_produto_lote SET STATUS = 'I' WHERE ID_PRODUTO_LOTE = ?", [id_produto_lote])
        self.commit()
        return True

    def excluir_lote(self, id_produto_lote: int) -> bool:
        """Exclui o lote da base de dados."""
        cur = self._get_cursor()
        cur.execute("DELETE FROM user_geoapolo_produto_lote WHERE ID_PRODUTO_LOTE = ?", [id_produto_lote])
        self.commit()
        return True

    def atualizar_saldo_lote(self, id_produto_lote: int, delta_qtd: float) -> bool:
        """Atualiza a quantidade atual de um lote."""
        cur = self._get_cursor()
        cur.execute("SELECT QUANTIDADE_ATUAL FROM user_geoapolo_produto_lote WHERE ID_PRODUTO_LOTE = ?", [id_produto_lote])
        row = cur.fetchone()
        if not row:
            return False
        novo_saldo = max(0.0, float(row[0] or 0.0) + delta_qtd)
        cur.execute("UPDATE user_geoapolo_produto_lote SET QUANTIDADE_ATUAL = ? WHERE ID_PRODUTO_LOTE = ?", [novo_saldo, id_produto_lote])
        self.commit()
        return True
