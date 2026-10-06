"""
Repositório de Dados para Gestão de Estoque e Requisições do GeoApolo.
GeoApolo V5
Clean Architecture: Operação 100% dedicada sobre o catálogo do GeoApolo (USER_geoapolo_produtos)
e tabelas dedicadas de estoque (USER_geoapolo_estoque, USER_geoapolo_requisicoes,
USER_geoapolo_requisicao_itens, USER_geoapolo_movimentacoes_estoque).
SEM interação com tabelas legadas do ERP Alvo (REQ_MAT, ITEM_REQ_MAT, MOV_ESTQ, PRODUTO).
"""

import logging
from typing import List, Optional, Tuple, Any
from datetime import datetime
from core import converter_data_br_para_iso
from entidades.database import obter_conexao_banco
from .models import (
    RequisicaoDTO,
    ItemRequisicaoDTO,
    MovimentoEstoqueDTO,
    FichaEstoqueLinhaDTO,
    SaldoProdutoDTO,
)

logger = logging.getLogger(__name__)


class EstoqueRepository:
    """Repositório dedicado do GeoApolo para estoques, requisições e movimentações."""

    def __init__(self, connection=None):
        self._conn = connection
        self._tabelas_inicializadas = False

    def _get_cursor(self):
        if self._conn is None:
            self._conn = obter_conexao_banco()
        if not self._tabelas_inicializadas:
            self._garantir_tabelas_geoapolo()
        return self._conn.cursor()

    @property
    def conn(self):
        if self._conn is None:
            self._conn = obter_conexao_banco()
        return self._conn

    @property
    def _is_sql_server(self) -> bool:
        return self._conn is not None and not hasattr(self._conn, "isolation_level")

    def _nolock(self) -> str:
        return "WITH (NOLOCK)" if self._is_sql_server else ""

    def commit(self):
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()

    def rollback(self):
        if self._conn and hasattr(self._conn, "rollback"):
            self._conn.rollback()

    # -------------------------------------------------------------------------
    # AUTO-CRIAÇÃO DAS TABELAS PRÓPRIAS DO GEOAPOLO
    # -------------------------------------------------------------------------
    def _garantir_tabelas_geoapolo(self):
        """Garante a existência das 4 tabelas dedicadas do subsistema de estoque GeoApolo."""
        if self._tabelas_inicializadas:
            return

        cur = self._conn.cursor()
        is_sql = self._is_sql_server

        try:
            if is_sql:
                # SQL Server
                cur.execute("""
                    IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name='USER_geoapolo_estoque' AND xtype='U')
                    CREATE TABLE USER_geoapolo_estoque (
                        codigo_empresa VARCHAR(10) NOT NULL,
                        prodcod INT NOT NULL,
                        saldo_atual FLOAT DEFAULT 0.0,
                        quantidade_reservada FLOAT DEFAULT 0.0,
                        saldo_disponivel FLOAT DEFAULT 0.0,
                        data_ultima_movimentacao VARCHAR(30),
                        PRIMARY KEY (codigo_empresa, prodcod)
                    );
                """)
                cur.execute("""
                    IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name='USER_geoapolo_requisicoes' AND xtype='U')
                    CREATE TABLE USER_geoapolo_requisicoes (
                        codigo_empresa VARCHAR(10) NOT NULL,
                        numero_requisicao VARCHAR(30) NOT NULL,
                        data_requisicao VARCHAR(30) NOT NULL,
                        solicitante VARCHAR(100) NOT NULL,
                        centro_custo VARCHAR(50) NOT NULL,
                        status VARCHAR(30) DEFAULT 'Aberta',
                        observacao VARCHAR(500),
                        tipo_requisicao VARCHAR(20) DEFAULT 'Produto',
                        PRIMARY KEY (codigo_empresa, numero_requisicao)
                    );
                """)
                cur.execute("""
                    IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name='USER_geoapolo_requisicao_itens' AND xtype='U')
                    CREATE TABLE USER_geoapolo_requisicao_itens (
                        codigo_empresa VARCHAR(10) NOT NULL,
                        numero_requisicao VARCHAR(30) NOT NULL,
                        item_seq INT NOT NULL,
                        prodcod INT NOT NULL,
                        unidade VARCHAR(10) DEFAULT 'UN',
                        quantidade_solicitada FLOAT NOT NULL,
                        quantidade_atendida FLOAT DEFAULT 0.0,
                        saldo_pendente FLOAT NOT NULL,
                        status_item VARCHAR(30) DEFAULT 'Pendente',
                        observacao VARCHAR(255),
                        PRIMARY KEY (codigo_empresa, numero_requisicao, item_seq)
                    );
                """)
                cur.execute("""
                    IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name='USER_geoapolo_movimentacoes_estoque' AND xtype='U')
                    CREATE TABLE USER_geoapolo_movimentacoes_estoque (
                        codigo_movimento INT NOT NULL,
                        codigo_empresa VARCHAR(10) NOT NULL,
                        data_movimento VARCHAR(30) NOT NULL,
                        tipo_movimento VARCHAR(1) NOT NULL,
                        origem_movimento VARCHAR(30) NOT NULL,
                        prodcod INT NOT NULL,
                        unidade VARCHAR(10) DEFAULT 'UN',
                        quantidade FLOAT NOT NULL,
                        valor_unitario FLOAT DEFAULT 0.0,
                        valor_total FLOAT DEFAULT 0.0,
                        documento_origem VARCHAR(50),
                        numero_requisicao VARCHAR(30),
                        item_requisicao_seq INT,
                        centro_custo VARCHAR(50),
                        observacao VARCHAR(500),
                        PRIMARY KEY (codigo_movimento)
                    );
                """)
                cur.execute("""
                    IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name='user_geoapolo_saldoestqdata' AND xtype='U')
                    CREATE TABLE user_geoapolo_saldoestqdata (
                        prodcod numeric(8,0) NOT NULL,
                        data_saldo date NOT NULL,
                        saldo_do_dia numeric(14,6) NOT NULL DEFAULT 0,
                        CONSTRAINT pk_prodssaldoestqdata PRIMARY KEY (prodcod, data_saldo)
                    );
                """)
            else:
                # SQLite
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS USER_geoapolo_estoque (
                        codigo_empresa VARCHAR(10) NOT NULL,
                        prodcod INT NOT NULL,
                        saldo_atual FLOAT DEFAULT 0.0,
                        quantidade_reservada FLOAT DEFAULT 0.0,
                        saldo_disponivel FLOAT DEFAULT 0.0,
                        data_ultima_movimentacao VARCHAR(30),
                        PRIMARY KEY (codigo_empresa, prodcod)
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS USER_geoapolo_requisicoes (
                        codigo_empresa VARCHAR(10) NOT NULL,
                        numero_requisicao VARCHAR(30) NOT NULL,
                        data_requisicao VARCHAR(30) NOT NULL,
                        solicitante VARCHAR(100) NOT NULL,
                        centro_custo VARCHAR(50) NOT NULL,
                        status VARCHAR(30) DEFAULT 'Aberta',
                        observacao VARCHAR(500),
                        tipo_requisicao VARCHAR(20) DEFAULT 'Produto',
                        PRIMARY KEY (codigo_empresa, numero_requisicao)
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS USER_geoapolo_requisicao_itens (
                        codigo_empresa VARCHAR(10) NOT NULL,
                        numero_requisicao VARCHAR(30) NOT NULL,
                        item_seq INT NOT NULL,
                        prodcod INT NOT NULL,
                        unidade VARCHAR(10) DEFAULT 'UN',
                        quantidade_solicitada FLOAT NOT NULL,
                        quantidade_atendida FLOAT DEFAULT 0.0,
                        saldo_pendente FLOAT NOT NULL,
                        status_item VARCHAR(30) DEFAULT 'Pendente',
                        observacao VARCHAR(255),
                        PRIMARY KEY (codigo_empresa, numero_requisicao, item_seq)
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS USER_geoapolo_movimentacoes_estoque (
                        codigo_movimento INTEGER PRIMARY KEY,
                        codigo_empresa VARCHAR(10) NOT NULL,
                        data_movimento VARCHAR(30) NOT NULL,
                        tipo_movimento VARCHAR(1) NOT NULL,
                        origem_movimento VARCHAR(30) NOT NULL,
                        prodcod INT NOT NULL,
                        unidade VARCHAR(10) DEFAULT 'UN',
                        quantidade FLOAT NOT NULL,
                        valor_unitario FLOAT DEFAULT 0.0,
                        valor_total FLOAT DEFAULT 0.0,
                        documento_origem VARCHAR(50),
                        numero_requisicao VARCHAR(30),
                        item_requisicao_seq INT,
                        centro_custo VARCHAR(50),
                        observacao VARCHAR(500)
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_geoapolo_saldoestqdata (
                        prodcod INTEGER NOT NULL,
                        data_saldo TEXT NOT NULL,
                        saldo_do_dia REAL NOT NULL DEFAULT 0,
                        PRIMARY KEY (prodcod, data_saldo)
                    );
                """)

            # Garante coluna centro_custo caso a tabela já tenha sido criada anteriormente
            try:
                if is_sql:
                    cur.execute("""
                        IF NOT EXISTS (SELECT 1 FROM syscolumns WHERE id = OBJECT_ID('USER_geoapolo_movimentacoes_estoque') AND name = 'centro_custo')
                        ALTER TABLE USER_geoapolo_movimentacoes_estoque ADD centro_custo VARCHAR(50) NULL;
                    """)
                else:
                    cur.execute("ALTER TABLE USER_geoapolo_movimentacoes_estoque ADD COLUMN centro_custo VARCHAR(50)")
            except Exception:
                pass

            # Garante coluna numero_lote caso a tabela já tenha sido criada anteriormente
            try:
                if is_sql:
                    cur.execute("""
                        IF NOT EXISTS (SELECT 1 FROM syscolumns WHERE id = OBJECT_ID('USER_geoapolo_movimentacoes_estoque') AND name = 'numero_lote')
                        ALTER TABLE USER_geoapolo_movimentacoes_estoque ADD numero_lote VARCHAR(50) NULL;
                    """)
                else:
                    cur.execute("ALTER TABLE USER_geoapolo_movimentacoes_estoque ADD COLUMN numero_lote VARCHAR(50)")
            except Exception:
                pass

            # Garante coluna tipo_requisicao caso a tabela já tenha sido criada anteriormente
            try:
                if is_sql:
                    cur.execute("""
                        IF NOT EXISTS (SELECT 1 FROM syscolumns WHERE id = OBJECT_ID('USER_geoapolo_requisicoes') AND name = 'tipo_requisicao')
                        ALTER TABLE USER_geoapolo_requisicoes ADD tipo_requisicao VARCHAR(20) DEFAULT 'Produto';
                    """)
                else:
                    cur.execute("ALTER TABLE USER_geoapolo_requisicoes ADD COLUMN tipo_requisicao VARCHAR(20) DEFAULT 'Produto'")
            except Exception:
                pass

            self.commit()
            self._tabelas_inicializadas = True
        except Exception as e:
            logger.warning("Aviso na inicialização das tabelas de estoque GeoApolo: %s", e)
            self._tabelas_inicializadas = True

    # -------------------------------------------------------------------------
    # AUXILIARES
    # -------------------------------------------------------------------------
    def _coluna_unidade_sql(self, alias_prod: str = "p") -> str:
        """Retorna a expressão SQL segura para obter a unidade de medida do produto."""
        try:
            cur = self._get_cursor()
            p = f"{alias_prod}." if alias_prod else ""
            if self._is_sql_server:
                cur.execute("""
                    SELECT 1 FROM syscolumns 
                    WHERE id = OBJECT_ID('USER_geoapolo_produtos') AND name = 'tamanho'
                """)
                tem_tam = cur.fetchone() is not None
                cur.execute("""
                    SELECT 1 FROM syscolumns 
                    WHERE id = OBJECT_ID('USER_geoapolo_produtos') AND name = 'unidade_medida'
                """)
                tem_unid = cur.fetchone() is not None
            else:
                cur.execute("PRAGMA table_info(USER_geoapolo_produtos)")
                cols = [c[1].lower() for c in cur.fetchall()]
                tem_tam = "tamanho" in cols
                tem_unid = "unidade_medida" in cols

            if tem_unid and tem_tam:
                return f"COALESCE({p}unidade_medida, {p}tamanho, 'UN')"
            elif tem_unid:
                return f"COALESCE({p}unidade_medida, 'UN')"
            elif tem_tam:
                return f"COALESCE({p}tamanho, 'UN')"
        except Exception:
            pass
        return "'UN'"

    def obter_unidade_produto(self, prodcod: int) -> str:
        """Obtém a unidade de medida do produto cadastrada em USER_geoapolo_produtos."""
        try:
            cur = self._get_cursor()
            nolock = self._nolock()
            col_unid = self._coluna_unidade_sql(alias_prod="")
            cur.execute(
                f"SELECT {col_unid} FROM USER_geoapolo_produtos {nolock} WHERE prodcod = ?",
                [prodcod],
            )
            r = cur.fetchone()
            if r and r[0]:
                return str(r[0]).strip().upper()
        except Exception:
            pass
        return "UN"


    def _atualizar_saldo_lote(self, prodcod: int, numero_lote: str, delta_qtd: float):
        """Atualiza a quantidade atual do lote em user_geoapolo_produto_lote ou cria se for entrada."""
        if not numero_lote or not str(numero_lote).strip() or not prodcod or prodcod <= 0:
            return
        try:
            cur = self._get_cursor()
            lote_str = str(numero_lote).strip().upper()
            cur.execute(
                "SELECT ID_PRODUTO_LOTE, QUANTIDADE_ATUAL FROM user_geoapolo_produto_lote WHERE prodcod = ? AND UPPER(NUMERO_LOTE) = ?",
                [prodcod, lote_str],
            )
            r = cur.fetchone()
            if r:
                id_lote = r[0]
                nova_qtd = max(0.0, float(r[1] or 0.0) + delta_qtd)
                cur.execute(
                    "UPDATE user_geoapolo_produto_lote SET QUANTIDADE_ATUAL = ? WHERE ID_PRODUTO_LOTE = ?",
                    [nova_qtd, id_lote],
                )
            elif delta_qtd > 0:
                # Cria e mantém o lote na movimentação de entrada se ainda não existir
                cur.execute(
                    """
                    INSERT INTO user_geoapolo_produto_lote (
                        prodcod, NUMERO_LOTE, QUANTIDADE_INICIAL, QUANTIDADE_ATUAL, STATUS, OBSERVACAO
                    ) VALUES (?, ?, ?, ?, 'A', 'CRIADO NA MOVIMENTACAO DE ESTOQUE')
                    """,
                    [prodcod, lote_str, delta_qtd, delta_qtd],
                )
        except Exception as e:
            logger.debug("Aviso ao atualizar saldo do lote %s: %s", numero_lote, e)

    def _atualizar_saldo_estq_data(self, prodcod: int, data_mov: str, delta_qtd: float):
        """
        Atualiza a tabela user_geoapolo_saldoestqdata:
        Entrada (+delta_qtd) adiciona ao saldo_do_dia.
        Saída (-delta_qtd) reduz do saldo_do_dia conforme a data do movimento.
        """
        if not prodcod or prodcod <= 0:
            return
        try:
            cur = self._get_cursor()
            nolock = self._nolock()
            dt_raw = str(data_mov or "").strip()
            if "/" in dt_raw:
                p_dt = dt_raw.split(" ")[0].split("/")
                if len(p_dt) == 3:
                    dt_iso = f"{p_dt[2]}-{p_dt[1].zfill(2)}-{p_dt[0].zfill(2)}"
                else:
                    dt_iso = datetime.now().strftime("%Y-%m-%d")
            elif "-" in dt_raw:
                dt_iso = dt_raw.split(" ")[0]
            else:
                dt_iso = datetime.now().strftime("%Y-%m-%d")

            cur.execute(
                f"SELECT saldo_do_dia FROM user_geoapolo_saldoestqdata {nolock} WHERE prodcod = ? AND data_saldo = ?",
                [prodcod, dt_iso],
            )
            r = cur.fetchone()
            if r:
                novo_saldo = float(r[0] or 0.0) + delta_qtd
                cur.execute(
                    "UPDATE user_geoapolo_saldoestqdata SET saldo_do_dia = ? WHERE prodcod = ? AND data_saldo = ?",
                    [novo_saldo, prodcod, dt_iso],
                )
            else:
                cur.execute(
                    "INSERT INTO user_geoapolo_saldoestqdata (prodcod, data_saldo, saldo_do_dia) VALUES (?, ?, ?)",
                    [prodcod, dt_iso, delta_qtd],
                )
        except Exception as e:
            logger.error("Erro ao atualizar user_geoapolo_saldoestqdata: %s", e)

    def _parse_prodcod(self, prod_val) -> int:
        """Converte com segurança o identificador do produto para int de USER_geoapolo_produtos."""
        try:
            return int(str(prod_val).strip())
        except (ValueError, TypeError):
            # Se for formato pontuado como '01.001.0001', extrai os dígitos ou retorna hash
            digs = "".join(c for c in str(prod_val) if c.isdigit())
            return int(digs) if digs else 0

    def _montar_filtro_empresa(self, alias: str, empcod: str) -> Tuple[str, List[Any]]:
        """
        Gera cláusula SQL e parâmetros compatíveis para códigos de empresa (ex: '1' vs '1.01').
        Suporta 'TODOS', 'TODAS', '*' e vazio para ignorar filtro de empresa.
        """
        if not empcod or str(empcod).strip().upper() in ("TODAS", "TODOS", "*"):
            return "", []
        emp_val = str(empcod).strip()
        emp_base = emp_val.split(".")[0]
        col = f"{alias}.codigo_empresa" if alias else "codigo_empresa"
        if emp_base != emp_val:
            return f"({col} = ? OR {col} = ?)", [emp_val, emp_base]
        else:
            return f"({col} = ? OR {col} LIKE ?)", [emp_val, f"{emp_val}.%"]

    def _atualizar_saldo_produto(self, empcod: str, prodcod: int, delta_qtd: float):
        """Atualiza saldo_atual e saldo_disponivel em USER_geoapolo_estoque."""
        cur = self._get_cursor()
        nolock = self._nolock()
        data_agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        emp_val = str(empcod).strip()
        emp_base = emp_val.split(".")[0]

        cur.execute(
            f"SELECT saldo_atual, quantidade_reservada, codigo_empresa FROM USER_geoapolo_estoque {nolock} WHERE (codigo_empresa = ? OR codigo_empresa = ?) AND prodcod = ?",
            [emp_val, emp_base, prodcod],
        )
        row = cur.fetchone()
        if row:
            emp_gravar = str(row[2])
            s_atual = float(row[0] or 0.0) + delta_qtd
            reserv = float(row[1] or 0.0)
            disp = s_atual - reserv
            sql_upd = """
                UPDATE USER_geoapolo_estoque
                SET saldo_atual = ?, saldo_disponivel = ?, data_ultima_movimentacao = ?
                WHERE codigo_empresa = ? AND prodcod = ?
            """
            cur.execute(sql_upd, [s_atual, disp, data_agora, emp_gravar, prodcod])
        else:
            s_atual = delta_qtd
            disp = delta_qtd
            sql_ins = """
                INSERT INTO USER_geoapolo_estoque (codigo_empresa, prodcod, saldo_atual, quantidade_reservada, saldo_disponivel, data_ultima_movimentacao)
                VALUES (?, ?, ?, 0.0, ?, ?)
            """
            cur.execute(sql_ins, [empcod, prodcod, s_atual, disp, data_agora])

    def obter_saldo_produto(self, empcod: str, prodcod) -> Tuple[float, float, float]:
        """Retorna (saldo_atual, quantidade_reservada, saldo_disponivel) para o produto."""
        cur = self._get_cursor()
        nolock = self._nolock()
        p_cod = self._parse_prodcod(prodcod)
        emp_val = str(empcod).strip()
        emp_base = emp_val.split(".")[0]
        sql = f"SELECT saldo_atual, quantidade_reservada, saldo_disponivel FROM USER_geoapolo_estoque {nolock} WHERE (codigo_empresa = ? OR codigo_empresa = ?) AND prodcod = ?"
        cur.execute(sql, [emp_val, emp_base, p_cod])
        row = cur.fetchone()
        if row:
            s_atual = float(row[0] or 0.0)
            reserv = float(row[1] or 0.0)
            disp = float(row[2] if row[2] is not None else (s_atual - reserv))
            return s_atual, reserv, disp
        return 0.0, 0.0, 0.0

    def obter_proxima_chave_movimento(self) -> int:
        cur = self._get_cursor()
        nolock = self._nolock()
        sql = f"SELECT COALESCE(MAX(codigo_movimento), 0) + 1 FROM USER_geoapolo_movimentacoes_estoque {nolock}"
        cur.execute(sql)
        row = cur.fetchone()
        return int(row[0]) if row and row[0] is not None else 1

    def obter_proximo_numero_requisicao(self, empcod: str = "1.01") -> str:
        """Gera o próximo número sequencial de requisição."""
        cur = self._get_cursor()
        nolock = self._nolock()
        try:
            sql = f"SELECT numero_requisicao FROM USER_geoapolo_requisicoes {nolock} WHERE codigo_empresa = ?"
            cur.execute(sql, [empcod])
            numeros = []
            for r in cur.fetchall():
                val = str(r[0] or "").strip()
                digs = "".join(c for c in val if c.isdigit())
                if digs:
                    try:
                        numeros.append(int(digs))
                    except ValueError:
                        pass
            if numeros:
                prox = max(numeros) + 1
                return f"{prox:06d}"
        except Exception:
            pass
        return "000001"

    def listar_centros_custo(self, empcod: str = "1.01") -> List[Tuple[str, str]]:
        """Lista centros de custo disponíveis (USER_geoapolo_centrocontrole ou USER_geoapolo_centro_controle)."""
        cur = self._get_cursor()
        nolock = self._nolock()
        for tab_nome in ("USER_geoapolo_centrocontrole", "USER_geoapolo_centro_controle"):
            try:
                sql = f"SELECT geocctrlcodestr, COALESCE(geocctrlnome, '') FROM {tab_nome} {nolock} ORDER BY geocctrlcodestr ASC"
                cur.execute(sql)
                rows = cur.fetchall()
                if rows:
                    return [(str(r[0] or "").strip(), str(r[1] or "").strip()) for r in rows if r[0]]
            except Exception:
                pass

        return [
            ("01.01", "ADMINISTRATIVO / GERAL"),
            ("01.02", "OPERACIONAL / LOGÍSTICA"),
            ("01.03", "MANUTENÇÃO / INFRAESTRUTURA"),
            ("01.04", "TECNOLOGIA DA INFORMAÇÃO"),
            ("01.05", "ATENDIMENTO / SUPORTE"),
        ]

    def listar_fornecedores(self, termo: str = "") -> List[Tuple[str, str, str]]:
        """Lista fornecedores disponíveis no catálogo de entidades (código, descrição/nome, documento)."""
        cur = self._get_cursor()
        nolock = self._nolock()
        t_limpo = (termo or "").strip()
        filtro = f"%{t_limpo}%" if t_limpo else "%"

        # 1. Tenta buscar na tabela entidade (Alvo / Apolo ERP)
        try:
            sql = f"""
                SELECT entcod, COALESCE(entnome, ''), COALESCE(EntCpfCgc, '')
                FROM entidade {nolock}
                WHERE (entnome LIKE ? OR entcod LIKE ? OR EntCpfCgc LIKE ?)
                ORDER BY entnome ASC
            """
            cur.execute(sql, [filtro, filtro, filtro])
            rows = cur.fetchall()
            if rows:
                return [(str(r[0] or "").strip(), str(r[1] or "").strip(), str(r[2] or "").strip()) for r in rows[:100] if r[0]]
        except Exception:
            pass

        # 2. Tenta buscar na tabela USER_geoapolo_entidade (GeoApolo)
        try:
            sql = f"""
                SELECT geoentcod, COALESCE(geoentnome, ''), COALESCE(geocpfcnpj, '')
                FROM USER_geoapolo_entidade {nolock}
                WHERE (geoentnome LIKE ? OR geoentcod LIKE ? OR geocpfcnpj LIKE ?)
                ORDER BY geoentnome ASC
            """
            cur.execute(sql, [filtro, filtro, filtro])
            rows = cur.fetchall()
            if rows:
                return [(str(r[0] or "").strip(), str(r[1] or "").strip(), str(r[2] or "").strip()) for r in rows[:100] if r[0]]
        except Exception:
            pass

        # 3. Fallback inteligente / dados mock em SQLite caso nenhuma tabela exista ainda
        padrao = [
            ("FORN001", "DISTRIBUIDORA DE MATERIAIS ELETRICOS LTDA", "12.345.678/0001-90"),
            ("FORN002", "FIBRA BRASIL TELECOMUNICACOES E CABOS", "98.765.432/0001-10"),
            ("FORN003", "COMERCIAL DE EQUIPAMENTOS DE REDE S/A", "45.123.789/0001-55"),
            ("FORN004", "SUPRIMENTOS DE INFORMATICA E ESCRITORIO", "33.222.111/0001-44"),
            ("FORN005", "FERRAGENS E FERRAMENTAS INDUSTRIAIS", "55.666.777/0001-88"),
        ]
        if t_limpo:
            termo_u = t_limpo.upper()
            return [f for f in padrao if termo_u in f[0].upper() or termo_u in f[1].upper() or termo_u in f[2].upper()]
        return padrao

    # -------------------------------------------------------------------------
    # REQUISIÇÕES DE MATERIAIS
    # -------------------------------------------------------------------------
    def listar_requisicoes(
        self,
        empcod: str = "1.01",
        status_filtro: str = "TODOS",
        termo_busca: str = "",
        data_ini: str = "",
        data_fim: str = "",
    ) -> List[RequisicaoDTO]:
        """Lista requisições da tabela USER_geoapolo_requisicoes com filtros."""
        cur = self._get_cursor()
        nolock = self._nolock()
        where = []
        params = []

        cl_emp, p_emp = self._montar_filtro_empresa("r", empcod)
        if cl_emp:
            where.append(cl_emp)
            params.extend(p_emp)

        if status_filtro and status_filtro != "TODOS":
            if status_filtro.upper() == "PENDENTES":
                where.append("UPPER(r.status) IN ('ABERTA', 'ATENDIDA PARCIAL', 'PENDENTE', 'PENDENTES')")
            else:
                where.append("UPPER(r.status) = ?")
                params.append(status_filtro.upper())

        if termo_busca and termo_busca.strip():
            t = f"%{termo_busca.strip().upper()}%"
            where.append("(UPPER(r.numero_requisicao) LIKE ? OR UPPER(r.solicitante) LIKE ?)")
            params.extend([t, t])

        if data_ini and data_ini.strip():
            where.append("r.data_requisicao >= ?")
            params.append(data_ini.strip())

        if data_fim and data_fim.strip():
            where.append("r.data_requisicao <= ?")
            params.append(data_fim.strip() + " 23:59:59" if len(data_fim.strip()) == 10 else data_fim.strip())

        where_str = f"WHERE {' AND '.join(where)}" if where else ""
        sql = f"""
            SELECT r.numero_requisicao, r.codigo_empresa, r.data_requisicao,
                   COALESCE(r.solicitante, ''), COALESCE(r.centro_custo, ''),
                   COALESCE(r.status, 'Aberta'), COALESCE(r.observacao, ''),
                   COALESCE(r.tipo_requisicao, 'Produto')
            FROM USER_geoapolo_requisicoes r {nolock}
            {where_str}
            ORDER BY r.data_requisicao DESC, r.numero_requisicao DESC
        """
        cur.execute(sql, params)
        requisicoes = []
        for row in cur.fetchall():
            dt_str = str(row[2])[:10] if row[2] else ""
            req = RequisicaoDTO(
                req_num=str(row[0] or "").strip(),
                empcod=str(row[1] or "").strip(),
                data_req=dt_str,
                requerente=str(row[3] or "").strip(),
                centro_custo=str(row[4] or "").strip(),
                status=str(row[5] or "Aberta").strip(),
                observacao=str(row[6] or "").strip(),
                tipo_requisicao=str(row[7] or "Produto").strip(),
            )
            requisicoes.append(req)
        return requisicoes

    def obter_itens_requisicao(self, req_num: str, empcod: str = "1.01") -> List[ItemRequisicaoDTO]:
        """Obtém itens de USER_geoapolo_requisicao_itens com produtos de USER_geoapolo_produtos."""
        cur = self._get_cursor()
        nolock = self._nolock()
        where_it = ["i.numero_requisicao = ?"]
        params_it = [req_num]
        cl_emp, p_emp = self._montar_filtro_empresa("i", empcod)
        if cl_emp:
            where_it.append(cl_emp)
            params_it.extend(p_emp)

        where_it_str = f"WHERE {' AND '.join(where_it)}"
        sql = f"""
            SELECT i.numero_requisicao, i.item_seq, i.codigo_empresa, i.prodcod,
                   p.prodnome,
                   COALESCE(i.unidade, 'UN'),
                   COALESCE(i.quantidade_solicitada, 0),
                   COALESCE(i.quantidade_atendida, 0),
                   COALESCE(i.saldo_pendente, i.quantidade_solicitada),
                   COALESCE(i.status_item, 'Pendente'),
                   COALESCE(i.observacao, '')
            FROM USER_geoapolo_requisicao_itens i {nolock}
            LEFT JOIN USER_geoapolo_produtos p {nolock} ON i.prodcod = p.prodcod
            {where_it_str}
            ORDER BY i.item_seq ASC
        """
        cur.execute(sql, params_it)
        itens = []
        for r in cur.fetchall():
            qtd_sol = float(r[6] or 0)
            qtd_atend = float(r[7] or 0)
            saldo = float(r[8] if r[8] is not None else (qtd_sol - qtd_atend))
            p_nome = str(r[4] or f"PRODUTO {r[3]}").strip()
            itens.append(ItemRequisicaoDTO(
                req_num=str(r[0] or "").strip(),
                item_seq=int(r[1]),
                empcod=str(r[2] or "").strip(),
                prodcod_estr=str(r[3] or "").strip(),
                prodnome=p_nome,
                unidade=str(r[5] or "UN").strip(),
                qtd_solicitada=qtd_sol,
                qtd_atendida=qtd_atend,
                saldo_pendente=max(0.0, saldo),
                status_item=str(r[9] or "Pendente").strip(),
                observacao=str(r[10] or "").strip(),
            ))
        return itens

    def obter_requisicao(self, req_num: str, empcod: str = "1.01") -> Optional[RequisicaoDTO]:
        lista = self.listar_requisicoes(empcod=empcod, termo_busca=req_num)
        for r in lista:
            if r.req_num == req_num:
                r.itens = self.obter_itens_requisicao(req_num, empcod=r.empcod or empcod)
                return r
        # Fallback sem restrição de empresa
        lista_geral = self.listar_requisicoes(empcod="", termo_busca=req_num)
        for r in lista_geral:
            if r.req_num == req_num:
                r.itens = self.obter_itens_requisicao(req_num, empcod=r.empcod)
                return r
        return None

    def criar_requisicao(self, requisicao: RequisicaoDTO) -> Tuple[bool, str, str]:
        """Grava uma nova requisição em USER_geoapolo_requisicoes e USER_geoapolo_requisicao_itens."""
        cur = self._get_cursor()
        nolock = self._nolock()

        empcod = requisicao.empcod.strip() or "1.01"
        req_num = requisicao.req_num.strip()
        if not req_num:
            req_num = self.obter_proximo_numero_requisicao(empcod)
            requisicao.req_num = req_num

        cur.execute(
            f"SELECT COUNT(1) FROM USER_geoapolo_requisicoes {nolock} WHERE numero_requisicao = ? AND codigo_empresa = ?",
            [req_num, empcod],
        )
        r_chk = cur.fetchone()
        if r_chk and r_chk[0] > 0:
            return False, f"Já existe uma requisição com o Nº {req_num}.", req_num

        if not requisicao.itens:
            return False, "A requisição precisa conter pelo menos um item.", req_num

        raw_dt = requisicao.data_req.strip() if requisicao.data_req else ""
        if "/" in raw_dt:
            partes = raw_dt.split(" ")
            d_iso = converter_data_br_para_iso(partes[0])
            hora = partes[1] if len(partes) > 1 else datetime.now().strftime("%H:%M:%S")
            data_req = f"{d_iso} {hora}".strip()
        else:
            data_req = raw_dt or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        requerente = requisicao.requerente.strip().upper()
        cctrl = requisicao.centro_custo.strip().upper()
        status_req = "Aberta"
        obs = requisicao.observacao.strip().upper()
        tipo_req = getattr(requisicao, "tipo_requisicao", "Produto") or "Produto"

        try:
            sql_cab = """
                INSERT INTO USER_geoapolo_requisicoes (
                    codigo_empresa, numero_requisicao, data_requisicao,
                    solicitante, centro_custo, status, observacao, tipo_requisicao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            cur.execute(sql_cab, [empcod, req_num, data_req, requerente, cctrl, status_req, obs, tipo_req])

            sql_it = """
                INSERT INTO USER_geoapolo_requisicao_itens (
                    codigo_empresa, numero_requisicao, item_seq, prodcod,
                    unidade, quantidade_solicitada, quantidade_atendida,
                    saldo_pendente, status_item, observacao
                ) VALUES (?, ?, ?, ?, ?, ?, 0.0, ?, 'Pendente', ?)
            """
            for idx, item in enumerate(requisicao.itens, start=1):
                p_cod = self._parse_prodcod(item.prodcod_estr)
                item.req_num = req_num
                item.item_seq = idx
                item.empcod = empcod
                item.qtd_atendida = 0.0
                item.saldo_pendente = item.qtd_solicitada
                cur.execute(sql_it, [
                    empcod,
                    req_num,
                    idx,
                    p_cod,
                    item.unidade.strip().upper() or "UN",
                    item.qtd_solicitada,
                    item.qtd_solicitada,
                    getattr(item, "observacao", "").strip().upper(),
                ])

            self.commit()
            return True, f"Requisição de Material Nº {req_num} emitida com sucesso com {len(requisicao.itens)} item(ns)!", req_num
        except Exception as e:
            self.rollback()
            logger.error("Erro ao gravar requisicao %s: %s", req_num, e)
            return False, f"Erro ao gravar requisição no banco: {e}", req_num

    def permite_estoque_negativo(self, empcod: str = "1.01") -> bool:
        """Verifica se os parâmetros do sistema permitem estoque negativo para a empresa especificada."""
        emp = str(empcod).strip() or "1.01"
        try:
            cur = self._get_cursor()
            nolock = self._nolock()
            sql = f"SELECT COALESCE(permite_estoque_negativo, 'Nao') FROM USER_geoapolo_configuracoes {nolock} WHERE empcod = ?"
            cur.execute(sql, [emp])
            row = cur.fetchone()
            if row and row[0]:
                val = str(row[0]).strip().upper()
                if val in ("SIM", "S", "1", "TRUE"):
                    return True
            return False
        except Exception as e:
            logger.debug("Aviso ao verificar parâmetro permite_estoque_negativo: %s", e)
            return False

    def atender_item_requisicao(
        self,
        req_num: str,
        item_seq: int,
        qtd_atender: float,
        empcod: str = "1.01",
        observacao: str = "",
        numero_lote: str = "",
    ) -> Tuple[bool, str, int]:
        """
        Atendimento parcial ou total de item de requisição:
        1. Valida política de estoque negativo.
        2. Atualiza USER_geoapolo_requisicao_itens.
        3. Insere saída em USER_geoapolo_movimentacoes_estoque ('S', 'REQUISICAO').
        4. Debita saldo em USER_geoapolo_estoque.
        5. Atualiza status em USER_geoapolo_requisicoes.
        """
        cur = self._get_cursor()
        nolock = self._nolock()

        sql_item = f"""
            SELECT prodcod, quantidade_solicitada, quantidade_atendida, saldo_pendente, unidade
            FROM USER_geoapolo_requisicao_itens {nolock}
            WHERE numero_requisicao = ? AND item_seq = ? AND codigo_empresa = ?
        """
        cur.execute(sql_item, [req_num, item_seq, empcod])
        row_item = cur.fetchone()
        if not row_item:
            return False, f"Item {item_seq} da requisição {req_num} não encontrado.", 0

        prodcod = int(row_item[0])
        qtd_sol = float(row_item[1] or 0)
        qtd_ja_atend = float(row_item[2] or 0)
        saldo_atual = float(row_item[3] if row_item[3] is not None else (qtd_sol - qtd_ja_atend))
        unid = str(row_item[4] or "UN").strip()

        if qtd_atender <= 0:
            return False, "A quantidade a atender deve ser maior que zero.", 0

        if qtd_atender > (saldo_atual + 0.0001):
            return False, f"Quantidade informada ({qtd_atender}) ultrapassa o saldo pendente ({saldo_atual:.2f}).", 0

        # Validação de Estoque Negativo
        if not self.permite_estoque_negativo(empcod):
            saldo_estq, _, _ = self.obter_saldo_produto(empcod=empcod, prodcod=prodcod)
            if qtd_atender > (saldo_estq + 0.0001):
                return False, "O sistema não permite estoque negativo, este produto não tem em estoque e não permite movimentação", 0

        nova_qtd_atendida = qtd_ja_atend + qtd_atender
        novo_saldo = max(0.0, qtd_sol - nova_qtd_atendida)
        status_item = "Atendido" if novo_saldo <= 0.0001 else "Atendido Parcial"

        try:
            # 1. Atualiza USER_geoapolo_requisicao_itens
            sql_upd = """
                UPDATE USER_geoapolo_requisicao_itens
                SET quantidade_atendida = ?, saldo_pendente = ?, status_item = ?
                WHERE numero_requisicao = ? AND item_seq = ? AND codigo_empresa = ?
            """
            cur.execute(sql_upd, [nova_qtd_atendida, novo_saldo, status_item, req_num, item_seq, empcod])

            # 2. Insere saída em USER_geoapolo_movimentacoes_estoque
            mov_chv = self.obter_proxima_chave_movimento()
            data_hoje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            obs_saida = observacao.strip().upper() or f"BAIXA REQUISICAO {req_num} ITEM {item_seq}"
            lote_str = str(numero_lote or "").strip().upper()

            sql_mov = """
                INSERT INTO USER_geoapolo_movimentacoes_estoque (
                    codigo_movimento, codigo_empresa, data_movimento, tipo_movimento,
                    origem_movimento, prodcod, unidade, quantidade, valor_unitario, valor_total,
                    documento_origem, numero_requisicao, item_requisicao_seq, numero_lote, observacao
                ) VALUES (?, ?, ?, 'S', 'REQUISICAO', ?, ?, ?, 0.0, 0.0, ?, ?, ?, ?, ?)
            """
            cur.execute(sql_mov, [
                mov_chv, empcod, data_hoje, prodcod, unid, qtd_atender,
                req_num, req_num, item_seq, lote_str, obs_saida
            ])

            # 3. Debita saldo em USER_geoapolo_estoque
            self._atualizar_saldo_produto(empcod, prodcod, -qtd_atender)
            if lote_str:
                self._atualizar_saldo_lote(prodcod, lote_str, -qtd_atender)
            self._atualizar_saldo_estq_data(prodcod, data_hoje, -qtd_atender)

            # 4. Atualiza status da requisição
            cur.execute(
                f"SELECT COUNT(1) FROM USER_geoapolo_requisicao_itens {nolock} WHERE numero_requisicao = ? AND codigo_empresa = ? AND saldo_pendente > 0.0001",
                [req_num, empcod],
            )
            r_pend = cur.fetchone()
            pendentes = int(r_pend[0]) if r_pend else 0
            novo_status = "Atendida Total" if pendentes == 0 else "Atendida Parcial"

            cur.execute(
                "UPDATE USER_geoapolo_requisicoes SET status = ? WHERE numero_requisicao = ? AND codigo_empresa = ?",
                [novo_status, req_num, empcod],
            )

            self.commit()
            return True, f"Item atendido com sucesso! Gerada movimentação Nº {mov_chv}.", mov_chv
        except Exception as e:
            self.rollback()
            logger.error("Erro ao atender item requisicao: %s", e)
            return False, f"Erro ao atender requisição: {e}", 0

    def atender_requisicao_completa(
        self,
        req_num: str,
        empcod: str = "1.01",
        observacao: str = "",
        itens_lotes: Optional[dict] = None,
    ) -> Tuple[bool, str, int]:
        """Efetua o atendimento total de todos os itens pendentes da requisição com seus respectivos lotes."""
        itens = self.obter_itens_requisicao(req_num, empcod=empcod)
        if not itens:
            return False, f"Nenhum item encontrado na requisição {req_num}.", 0

        itens_pendentes = [it for it in itens if it.saldo_pendente > 0.0001]
        if not itens_pendentes:
            return False, f"Todos os itens da requisição {req_num} já estão atendidos.", 0

        # Pré-validação de estoque negativo para todos os itens
        if not self.permite_estoque_negativo(empcod):
            for it in itens_pendentes:
                saldo_estq, _, _ = self.obter_saldo_produto(empcod=empcod, prodcod=it.prodcod_estr)
                if it.saldo_pendente > (saldo_estq + 0.0001):
                    return False, "O sistema não permite estoque negativo, este produto não tem em estoque e não permite movimentação", 0

        atendidos = 0
        ultima_mov = 0
        obs = observacao.strip().upper() or f"ATENDIMENTO TOTAL REQUISICAO {req_num}"
        for it in itens_pendentes:
            lote_item = ""
            if itens_lotes:
                lote_item = str(itens_lotes.get(it.item_seq) or itens_lotes.get(it.prodcod_estr) or "").strip().upper()
            sucesso, msg, mov_chv = self.atender_item_requisicao(
                req_num=req_num,
                item_seq=it.item_seq,
                qtd_atender=it.saldo_pendente,
                empcod=empcod,
                observacao=obs,
                numero_lote=lote_item,
            )
            if sucesso:
                atendidos += 1
                ultima_mov = mov_chv
            else:
                return False, msg, 0

        if atendidos > 0:
            return True, f"{atendidos} item(ns) atendido(s) com sucesso na requisição {req_num}!", ultima_mov
        else:
            return False, f"Não foi possível atender os itens da requisição {req_num}.", 0

    def cancelar_requisicao(self, req_num: str, empcod: str = "1.01", motivo: str = "") -> Tuple[bool, str]:
        """Cancela uma requisição marcando seu status como 'Cancelada'."""
        cur = self._get_cursor()
        nolock = self._nolock()

        cur.execute(
            f"SELECT status FROM USER_geoapolo_requisicoes {nolock} WHERE numero_requisicao = ? AND codigo_empresa = ?",
            [req_num, empcod],
        )
        r = cur.fetchone()
        if not r:
            return False, f"Requisição {req_num} não encontrada."

        if str(r[0] or "").strip() == "Cancelada":
            return False, "Esta requisição já está cancelada."

        obs_canc = f"Cancelada em {datetime.now().strftime('%d/%m/%Y %H:%M')}. Motivo: {motivo}".strip().upper()
        sql = "UPDATE USER_geoapolo_requisicoes SET status = 'Cancelada', observacao = ? WHERE numero_requisicao = ? AND codigo_empresa = ?"
        cur.execute(sql, [obs_canc, req_num, empcod])
        self.commit()
        return True, f"Requisição {req_num} cancelada com sucesso."

    def devolver_item_requisicao(
        self,
        req_num: str,
        item_seq: int,
        qtd_devolver: float,
        empcod: str = "1.01",
        observacao: str = "",
    ) -> Tuple[bool, str, int]:
        """Estorna material atendido: devolve quantidade ao estoque e restaura saldo."""
        cur = self._get_cursor()
        nolock = self._nolock()

        sql_item = f"""
            SELECT prodcod, quantidade_solicitada, quantidade_atendida, unidade
            FROM USER_geoapolo_requisicao_itens {nolock}
            WHERE numero_requisicao = ? AND item_seq = ? AND codigo_empresa = ?
        """
        cur.execute(sql_item, [req_num, item_seq, empcod])
        row_item = cur.fetchone()
        if not row_item:
            return False, f"Item {item_seq} da requisição {req_num} não encontrado.", 0

        prodcod = int(row_item[0])
        qtd_sol = float(row_item[1] or 0)
        qtd_atendida = float(row_item[2] or 0)
        unid = str(row_item[3] or "UN").strip()

        if qtd_devolver <= 0:
            return False, "Quantidade a devolver deve ser maior que zero.", 0

        if qtd_devolver > (qtd_atendida + 0.0001):
            return False, f"Quantidade a devolver ({qtd_devolver}) não pode ultrapassar o total atendido ({qtd_atendida:.2f}).", 0

        nova_qtd_atendida = max(0.0, qtd_atendida - qtd_devolver)
        novo_saldo = min(qtd_sol, qtd_sol - nova_qtd_atendida)
        status_item = "Pendente" if nova_qtd_atendida <= 0.0001 else "Atendido Parcial"

        try:
            # 1. Atualiza USER_geoapolo_requisicao_itens
            sql_upd = """
                UPDATE USER_geoapolo_requisicao_itens
                SET quantidade_atendida = ?, saldo_pendente = ?, status_item = ?
                WHERE numero_requisicao = ? AND item_seq = ? AND codigo_empresa = ?
            """
            cur.execute(sql_upd, [nova_qtd_atendida, novo_saldo, status_item, req_num, item_seq, empcod])

            # 2. Gera movimento de Entrada/Estorno no estoque
            mov_chv = self.obter_proxima_chave_movimento()
            data_hoje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            obs_dev = observacao.strip().upper() or f"DEVOLUCAO/ESTORNO REQUISICAO {req_num} ITEM {item_seq}"

            sql_mov = """
                INSERT INTO USER_geoapolo_movimentacoes_estoque (
                    codigo_movimento, codigo_empresa, data_movimento, tipo_movimento,
                    origem_movimento, prodcod, unidade, quantidade, valor_unitario, valor_total,
                    documento_origem, numero_requisicao, item_requisicao_seq, observacao
                ) VALUES (?, ?, ?, 'E', 'DEVOLUCAO', ?, ?, ?, 0.0, 0.0, ?, ?, ?, ?)
            """
            cur.execute(sql_mov, [
                mov_chv, empcod, data_hoje, prodcod, unid, qtd_devolver,
                req_num, req_num, item_seq, obs_dev
            ])

            # 3. Credita saldo em USER_geoapolo_estoque
            self._atualizar_saldo_produto(empcod, prodcod, +qtd_devolver)
            self._atualizar_saldo_estq_data(prodcod, data_hoje, +qtd_devolver)

            # 4. Atualiza cabeçalho
            cur.execute(
                f"SELECT quantidade_atendida, saldo_pendente, status_item FROM USER_geoapolo_requisicao_itens {nolock} WHERE numero_requisicao = ? AND (codigo_empresa = ? OR codigo_empresa = ?)",
                [req_num, empcod, str(empcod).split(".")[0]],
            )
            rows_ch = cur.fetchall()
            tot_atend = sum(float(r[0] or 0) for r in rows_ch)
            tot_pend = sum(float(r[1] or 0) for r in rows_ch)
            if tot_pend <= 0.0001:
                novo_status = "Atendida Total" if tot_atend > 0.0001 else "Cancelada"
            else:
                novo_status = "Atendida Parcial" if tot_atend > 0.0001 else "Aberta"

            cur.execute(
                "UPDATE USER_geoapolo_requisicoes SET status = ? WHERE numero_requisicao = ? AND (codigo_empresa = ? OR codigo_empresa = ?)",
                [novo_status, req_num, empcod, str(empcod).split(".")[0]],
            )

            self.commit()
            return True, f"Devolução processada com sucesso! Gerada entrada Nº {mov_chv}.", mov_chv
        except Exception as e:
            self.rollback()
            logger.error("Erro ao devolver item de requisicao: %s", e)
            return False, f"Erro ao devolver item: {e}", 0

    def cancelar_item_requisicao(
        self,
        req_num: str,
        item_seq: int,
        motivo: str,
        empcod: str = "1.01",
    ) -> Tuple[bool, str]:
        """
        Cancela o saldo pendente de um item da requisição e baixa a requisição se não houver mais pendências.
        Utilizado principalmente quando um item não pode ser atendido (ex: lote vencido ou com validade crítica).
        """
        cur = self._get_cursor()
        nolock = self._nolock()

        emp_val = str(empcod).strip()
        emp_base = emp_val.split(".")[0]

        sql_item = f"""
            SELECT prodcod, quantidade_solicitada, quantidade_atendida, saldo_pendente, status_item, observacao, codigo_empresa
            FROM USER_geoapolo_requisicao_itens {nolock}
            WHERE numero_requisicao = ? AND item_seq = ? AND (codigo_empresa = ? OR codigo_empresa = ?)
        """
        cur.execute(sql_item, [req_num, item_seq, emp_val, emp_base])
        row_item = cur.fetchone()
        if not row_item:
            return False, f"Item {item_seq} da requisição {req_num} não encontrado."

        prodcod = int(row_item[0])
        qtd_sol = float(row_item[1] or 0)
        qtd_atendida = float(row_item[2] or 0)
        saldo_pendente = float(row_item[3] if row_item[3] is not None else (qtd_sol - qtd_atendida))
        status_atual = str(row_item[4] or "Pendente").strip()
        obs_atual = str(row_item[5] or "").strip()
        emp_real = str(row_item[6] or emp_val).strip()

        if status_atual == "Cancelado" and saldo_pendente <= 0.0001:
            return False, f"O item {item_seq} da requisição {req_num} já está cancelado."

        try:
            novo_status_item = "Cancelado" if qtd_atendida <= 0.0001 else "Atendido Parcial"
            data_hoje_br = datetime.now().strftime("%d/%m/%Y %H:%M")
            motivo_limpo = motivo.strip().upper() or "CANCELADO PELO USUÁRIO"
            nota_canc = f"[CANCELADO em {data_hoje_br}: {motivo_limpo}]"
            nova_obs = f"{obs_atual} | {nota_canc}".strip(" | ")[:250]

            sql_upd = """
                UPDATE USER_geoapolo_requisicao_itens
                SET saldo_pendente = 0.0, status_item = ?, observacao = ?
                WHERE numero_requisicao = ? AND item_seq = ? AND (codigo_empresa = ? OR codigo_empresa = ?)
            """
            cur.execute(sql_upd, [novo_status_item, nova_obs, req_num, item_seq, emp_real, emp_base])

            # Recalcula o status da requisição consultando todos os itens
            sql_itens_req = f"""
                SELECT quantidade_solicitada, quantidade_atendida, saldo_pendente, status_item
                FROM USER_geoapolo_requisicao_itens {nolock}
                WHERE numero_requisicao = ? AND (codigo_empresa = ? OR codigo_empresa = ?)
            """
            cur.execute(sql_itens_req, [req_num, emp_real, emp_base])
            rows_req = cur.fetchall()

            tot_sol = sum(float(r[0] or 0) for r in rows_req)
            tot_atend = sum(float(r[1] or 0) for r in rows_req)
            tot_pend = sum(float(r[2] or 0) for r in rows_req)

            if tot_pend <= 0.0001:
                # Não resta nenhuma pendência: requisição é baixada!
                if tot_atend > 0.0001:
                    novo_status_req = "Atendida Total"
                    msg_sucesso = f"Item {item_seq} cancelado ({motivo_limpo}). Requisição {req_num} baixada e concluída!"
                else:
                    novo_status_req = "Cancelada"
                    msg_sucesso = f"Item {item_seq} cancelado ({motivo_limpo}). Todos os itens cancelados, requisição {req_num} baixada como Cancelada."
            else:
                if tot_atend > 0.0001:
                    novo_status_req = "Atendida Parcial"
                else:
                    novo_status_req = "Aberta"
                msg_sucesso = f"Item {item_seq} cancelado ({motivo_limpo}). Requisição {req_num} atualizada (restam {tot_pend:.2f} pendentes)."

            sql_upd_req = """
                UPDATE USER_geoapolo_requisicoes
                SET status = ?
                WHERE numero_requisicao = ? AND (codigo_empresa = ? OR codigo_empresa = ?)
            """
            cur.execute(sql_upd_req, [novo_status_req, req_num, emp_real, emp_base])

            self.commit()
            return True, msg_sucesso
        except Exception as e:
            self.rollback()
            logger.error("Erro ao cancelar item de requisicao: %s", e)
            return False, f"Erro ao cancelar item: {e}"

    # -------------------------------------------------------------------------
    # MOVIMENTAÇÕES DE ENTRADA E SAÍDA DIRETA
    # -------------------------------------------------------------------------
    def registrar_movimentacao_entrada(
        self,
        empcod: str,
        prodcod_estr: str,
        quantidade: float,
        valor_unitario: float = 0.0,
        num_doc: str = "",
        fornecedor_obs: str = "",
        centro_custo: str = "",
        fornecedor_cod: str = "",
        fornecedor_nome: str = "",
        numero_lote: str = "",
    ) -> Tuple[bool, str, int]:
        """Registra entrada de compras em USER_geoapolo_movimentacoes_estoque e credita saldo."""
        if quantidade <= 0:
            return False, "Quantidade de entrada deve ser maior que zero.", 0

        prodcod = self._parse_prodcod(prodcod_estr)
        cur = self._get_cursor()
        mov_chv = self.obter_proxima_chave_movimento()
        data_hoje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        doc_str = num_doc.strip().upper() or f"NF_{mov_chv}"
        lote_str = str(numero_lote or "").strip().upper()

        partes = [f"ENTRADA POR COMPRA. DOC/NF: {doc_str}"]
        if lote_str:
            partes.append(f"LOTE: {lote_str}")
        if fornecedor_cod or fornecedor_nome:
            f_txt = f"{fornecedor_cod} - {fornecedor_nome}".strip(" - ")
            partes.append(f"FORNECEDOR: {f_txt}")
        if centro_custo and centro_custo.strip():
            partes.append(f"CENTRO DE CUSTO: {centro_custo.strip()}")
        if fornecedor_obs and fornecedor_obs.strip():
            partes.append(fornecedor_obs.strip())
        obs_texto = ". ".join(partes).upper()
        val_tot = quantidade * valor_unitario
        unid_prod = self.obter_unidade_produto(prodcod)

        try:
            sql_mov = """
                INSERT INTO USER_geoapolo_movimentacoes_estoque (
                    codigo_movimento, codigo_empresa, data_movimento, tipo_movimento,
                    origem_movimento, prodcod, unidade, quantidade, valor_unitario, valor_total,
                    documento_origem, centro_custo, numero_lote, observacao
                ) VALUES (?, ?, ?, 'E', 'COMPRA', ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cur.execute(sql_mov, [
                mov_chv, empcod, data_hoje, prodcod, unid_prod, quantidade,
                valor_unitario, val_tot, doc_str, (centro_custo or "").strip(), lote_str, obs_texto
            ])

            self._atualizar_saldo_produto(empcod, prodcod, +quantidade)
            if lote_str:
                self._atualizar_saldo_lote(prodcod, lote_str, +quantidade)
            self._atualizar_saldo_estq_data(prodcod, data_hoje, +quantidade)
            self.commit()
            return True, f"Movimentação de Entrada Nº {mov_chv} registrada com sucesso!", mov_chv
        except Exception as e:
            self.rollback()
            logger.error("Erro ao registrar entrada de compras: %s", e)
            return False, f"Erro ao registrar entrada: {e}", 0

    def registrar_movimentacao_saida_direta(
        self,
        empcod: str,
        prodcod_estr: str,
        quantidade: float,
        destino_obs: str = "",
        centro_custo: str = "",
        numero_lote: str = "",
    ) -> Tuple[bool, str, int]:
        """Registra saída direta sem requisição e debita saldo de USER_geoapolo_estoque."""
        if quantidade <= 0:
            return False, "Quantidade de saída deve ser maior que zero.", 0

        prodcod = self._parse_prodcod(prodcod_estr)

        # Validação de Estoque Negativo
        if not self.permite_estoque_negativo(empcod):
            saldo_estq, _, _ = self.obter_saldo_produto(empcod=empcod, prodcod=prodcod)
            if quantidade > (saldo_estq + 0.0001):
                return False, "O sistema não permite estoque negativo, este produto não tem em estoque e não permite movimentação", 0

        cur = self._get_cursor()
        mov_chv = self.obter_proxima_chave_movimento()
        data_hoje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lote_str = str(numero_lote or "").strip().upper()
        partes = ["SAÍDA DIRETA SEM REQUISIÇÃO"]
        if lote_str:
            partes.append(f"LOTE: {lote_str}")
        if centro_custo and centro_custo.strip():
            partes.append(f"CENTRO DE CUSTO: {centro_custo.strip()}")
        if destino_obs and destino_obs.strip():
            partes.append(destino_obs.strip())
        obs_texto = ". ".join(partes).upper()
        unid_prod = self.obter_unidade_produto(prodcod)

        try:
            sql_mov = """
                INSERT INTO USER_geoapolo_movimentacoes_estoque (
                    codigo_movimento, codigo_empresa, data_movimento, tipo_movimento,
                    origem_movimento, prodcod, unidade, quantidade, valor_unitario, valor_total,
                    centro_custo, numero_lote, observacao
                ) VALUES (?, ?, ?, 'S', 'SAIDA_DIRETA', ?, ?, ?, 0.0, 0.0, ?, ?, ?)
            """
            cur.execute(sql_mov, [
                mov_chv, empcod, data_hoje, prodcod, unid_prod, quantidade,
                (centro_custo or "").strip(), lote_str, obs_texto
            ])

            self._atualizar_saldo_produto(empcod, prodcod, -quantidade)
            if lote_str:
                self._atualizar_saldo_lote(prodcod, lote_str, -quantidade)
            self._atualizar_saldo_estq_data(prodcod, data_hoje, -quantidade)
            self.commit()
            return True, f"Saída direta Nº {mov_chv} registrada com sucesso!", mov_chv
        except Exception as e:
            self.rollback()
            logger.error("Erro ao registrar saída direta: %s", e)
            return False, f"Erro ao registrar saída direta: {e}", 0

    def listar_movimentacoes(
        self,
        empcod: str = "1.01",
        data_ini: str = "",
        data_fim: str = "",
        tipo_filtro: str = "TODOS",
        termo_prod: str = "",
        limite: int = 200,
    ) -> List[MovimentoEstoqueDTO]:
        """Lista histórico de movimentações com JOIN em USER_geoapolo_produtos."""
        cur = self._get_cursor()
        nolock = self._nolock()
        where = []
        params = []
        cl_emp, p_emp = self._montar_filtro_empresa("m", empcod)
        if cl_emp:
            where.append(cl_emp)
            params.extend(p_emp)

        if tipo_filtro == "ENTRADA":
            where.append("m.tipo_movimento = 'E'")
        elif tipo_filtro == "SAIDA":
            where.append("m.tipo_movimento = 'S'")

        if data_ini and str(data_ini).strip():
            where.append("m.data_movimento >= ?")
            params.append(converter_data_br_para_iso(data_ini))

        if data_fim and str(data_fim).strip():
            where.append("m.data_movimento <= ?")
            params.append(converter_data_br_para_iso(data_fim, fim_do_dia=True))

        if termo_prod and termo_prod.strip():
            tp = f"%{termo_prod.strip().upper()}%"
            where.append("(CAST(m.prodcod AS VARCHAR(30)) LIKE ? OR UPPER(p.prodnome) LIKE ?)")
            params.extend([tp, tp])

        where_str = f"WHERE {' AND '.join(where)}" if where else ""
        sql = f"""
            SELECT m.codigo_movimento, m.codigo_empresa, m.data_movimento,
                   m.tipo_movimento, m.prodcod,
                   p.prodnome,
                   COALESCE(m.unidade, 'UN'),
                   COALESCE(m.quantidade, 0),
                   COALESCE(m.valor_unitario, 0),
                   COALESCE(m.valor_total, 0),
                   COALESCE(m.documento_origem, ''),
                   COALESCE(m.observacao, ''),
                   m.origem_movimento,
                   COALESCE(m.centro_custo, ''),
                   COALESCE(m.numero_lote, '')
            FROM USER_geoapolo_movimentacoes_estoque m {nolock}
            LEFT JOIN USER_geoapolo_produtos p {nolock} ON m.prodcod = p.prodcod
            {where_str}
            ORDER BY m.data_movimento DESC, m.codigo_movimento DESC
        """
        cur.execute(sql, params)
        movimentos = []
        for r in cur.fetchall()[:limite]:
            dt_str = str(r[2])[:19] if r[2] else ""
            qtd = float(r[7] or 0)
            v_tot = float(r[9] or 0)
            v_unit = float(r[8] or 0)
            p_nome = str(r[5] or f"PRODUTO {r[4]}").strip()
            cc_val = str(r[13] or "").strip()
            lote_val = str(r[14] or "").strip()
            movimentos.append(MovimentoEstoqueDTO(
                mov_chv=int(r[0]),
                empcod=str(r[1] or "").strip(),
                data_movimento=dt_str,
                tipo_movimento=str(r[3] or "S"),
                prodcod_estr=str(r[4] or "").strip(),
                prodnome=p_nome,
                unidade=str(r[6] or "UN").strip(),
                quantidade=qtd,
                valor_unitario=v_unit,
                valor_total=v_tot,
                doc_origem=str(r[10] or "").strip(),
                observacao=str(r[11] or "").strip(),
                origem_movimento=str(r[12] or "REQUISICAO").strip(),
                centro_custo=cc_val,
                numero_lote=lote_val,
            ))
        return movimentos

    # -------------------------------------------------------------------------
    # CONSULTAS (KARDEX & SALDOS DE PRODUTOS DO GEOAPOLO)
    # -------------------------------------------------------------------------
    def consultar_ficha_estoque(
        self,
        prodcod_estr: str,
        empcod: str = "1.01",
        data_ini: str = "",
        data_fim: str = "",
    ) -> List[FichaEstoqueLinhaDTO]:
        """Extrato cronológico (Kardex) do produto em USER_geoapolo_movimentacoes_estoque."""
        prodcod = self._parse_prodcod(prodcod_estr)
        cur = self._get_cursor()
        nolock = self._nolock()
        where = ["m.prodcod = ?"]
        params = [prodcod]
        cl_emp, p_emp = self._montar_filtro_empresa("m", empcod)
        if cl_emp:
            where.append(cl_emp)
            params.extend(p_emp)

        if data_ini and str(data_ini).strip():
            where.append("m.data_movimento >= ?")
            params.append(converter_data_br_para_iso(data_ini))

        if data_fim and str(data_fim).strip():
            where.append("m.data_movimento <= ?")
            params.append(converter_data_br_para_iso(data_fim, fim_do_dia=True))

        where_str = f"WHERE {' AND '.join(where)}"
        sql = f"""
            SELECT m.data_movimento,
                   COALESCE(m.documento_origem, CAST(m.codigo_movimento AS VARCHAR)),
                   m.tipo_movimento,
                   COALESCE(m.quantidade, 0),
                   COALESCE(m.observacao, ''),
                   m.origem_movimento
            FROM USER_geoapolo_movimentacoes_estoque m {nolock}
            {where_str}
            ORDER BY m.data_movimento ASC, m.codigo_movimento ASC
        """
        cur.execute(sql, params)
        extrato = []
        saldo_acumulado = 0.0

        for r in cur.fetchall():
            dt_str = str(r[0])[:19] if r[0] else ""
            doc = str(r[1] or "").strip()
            tipo = str(r[2] or "S")
            qtd = float(r[3] or 0)
            obs = str(r[4] or "").strip()
            orig = str(r[5] or "").strip()

            if tipo == "E":
                qtd_e = qtd
                qtd_s = 0.0
                saldo_acumulado += qtd
            else:
                qtd_e = 0.0
                qtd_s = qtd
                saldo_acumulado -= qtd

            extrato.append(FichaEstoqueLinhaDTO(
                data=dt_str,
                doc_num=doc,
                tipo_mov=tipo,
                origem=orig,
                qtd_entrada=qtd_e,
                qtd_saida=qtd_s,
                saldo_acumulado=saldo_acumulado,
                observacao=obs,
            ))
        return extrato

    def consultar_saldos_produtos(
        self,
        empcod: str = "1.01",
        termo_busca: str = "",
        grupocod: Optional[int] = None,
    ) -> List[SaldoProdutoDTO]:
        """Consulta os saldos de USER_geoapolo_produtos com LEFT JOIN em USER_geoapolo_estoque."""
        cur = self._get_cursor()
        nolock = self._nolock()

        cl_emp, p_emp = self._montar_filtro_empresa("e", empcod)
        join_emp = f"AND {cl_emp}" if cl_emp else ""
        params = list(p_emp)

        where = []
        if termo_busca and termo_busca.strip():
            t = f"%{termo_busca.strip().upper()}%"
            where.append("(CAST(p.prodcod AS VARCHAR(30)) LIKE ? OR UPPER(p.prodnome) LIKE ?)")
            params.extend([t, t])

        if grupocod is not None and grupocod > 0:
            where.append("p.grupocod = ?")
            params.append(grupocod)

        where_str = f"WHERE {' AND '.join(where)}" if where else ""

        sel_unid = self._coluna_unidade_sql(alias_prod="p")

        sql = f"""
            SELECT p.prodcod, p.prodnome,
                   COALESCE(e.saldo_atual, 0.0),
                   COALESCE(e.quantidade_reservada, 0.0),
                   COALESCE(e.saldo_disponivel, 0.0),
                   {sel_unid} AS unidade_medida
            FROM USER_geoapolo_produtos p {nolock}
            LEFT JOIN USER_geoapolo_estoque e {nolock}
                   ON p.prodcod = e.prodcod {join_emp}
            {where_str}
            ORDER BY p.prodnome ASC
        """
        cur.execute(sql, params)
        saldos = []
        for r in cur.fetchall():
            s_atual = float(r[2] or 0.0)
            reserv = float(r[3] or 0.0)
            disp = float(r[4] if r[4] is not None else (s_atual - reserv))
            unid_val = str(r[5] or "UN").strip().upper()
            saldos.append(SaldoProdutoDTO(
                prodcod_estr=str(r[0]),
                prodnome=str(r[1] or "").strip(),
                unidade=unid_val,
                saldo_atual=s_atual,
                quantidade_reservada=reserv,
                saldo_disponivel=disp,
            ))
        return saldos

    def contar_total_produtos_catalogo(self) -> int:
        """Retorna o total de produtos cadastrados em USER_geoapolo_produtos."""
        cur = self._get_cursor()
        nolock = self._nolock()
        try:
            cur.execute(f"SELECT COUNT(1) FROM USER_geoapolo_produtos {nolock}")
            row = cur.fetchone()
            return int(row[0]) if row and row[0] is not None else 0
        except Exception:
            return 0

