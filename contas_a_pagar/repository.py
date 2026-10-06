"""
Repositório de Dados de Contas a Pagar / Documentos Financeiros.
Tabela: USER_geoapolo_contas_a_pagar (SQL Server).
GeoApolo V5
"""

import logging
from typing import List, Optional, Tuple
from datetime import datetime
from entidades.database import obter_conexao_banco
from .models import DocumentoPagarDTO, FiltroContasPagarDTO, ResumoContasPagarDTO, BaixaDocumentoDTO

logger = logging.getLogger(__name__)


class ContasPagarRepository:
    """Acesso ao banco de dados para gestão de títulos a pagar."""

    def __init__(self, connection=None):
        self._conn = connection

    def _get_cursor(self):
        if self._conn is None:
            self._conn = obter_conexao_banco()
        return self._conn.cursor()

    def commit(self):
        if self._conn:
            self._conn.commit()

    def rollback(self):
        if self._conn:
            try:
                self._conn.rollback()
            except Exception:
                pass

    def tabela_existe(self) -> bool:
        """Verifica se a tabela USER_geoapolo_contas_a_pagar existe no banco SQL Server ou SQLite."""
        try:
            cur = self._get_cursor()
            is_sqlite = "sqlite" in type(self._conn).__module__.lower() if self._conn else False
            if is_sqlite:
                cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='USER_geoapolo_contas_a_pagar'")
            else:
                cur.execute("SELECT OBJECT_ID(N'dbo.USER_geoapolo_contas_a_pagar', N'U')")
            row = cur.fetchone()
            return bool(row and row[0] is not None)
        except Exception as e:
            logger.warning("Falha ao checar existência da tabela USER_geoapolo_contas_a_pagar: %s", e)
            return False

    def criar_tabela(self) -> Tuple[bool, str]:
        """Executa a criação da tabela USER_geoapolo_contas_a_pagar caso ainda não exista."""
        is_sqlite = "sqlite" in type(self._conn).__module__.lower() if self._conn else False
        if is_sqlite:
            sql = """
            CREATE TABLE IF NOT EXISTS USER_geoapolo_contas_a_pagar (
                codigo_documento          INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_empresa            VARCHAR(10) DEFAULT '1.01',
                numero_documento          VARCHAR(40) NOT NULL,
                serie_documento           VARCHAR(10) DEFAULT '1',
                parcela                   INT DEFAULT 1,
                total_parcelas            INT DEFAULT 1,
                entcod                    VARCHAR(20),
                fornecedor_nome           VARCHAR(200) NOT NULL,
                cnpj_cpf                  VARCHAR(20),
                data_emissao              DATE,
                data_vencimento           DATE NOT NULL,
                data_pagamento            DATE,
                valor_original            NUMERIC(15,2) NOT NULL,
                valor_desconto            NUMERIC(15,2) DEFAULT 0.00,
                valor_juros_multa         NUMERIC(15,2) DEFAULT 0.00,
                valor_pago                NUMERIC(15,2) DEFAULT 0.00,
                saldo_aberto              NUMERIC(15,2) NOT NULL,
                situacao                  VARCHAR(20) DEFAULT 'ABERTO',
                tipo_documento            VARCHAR(30) DEFAULT 'ENTRADA_ESTOQUE',
                origem                    VARCHAR(50) DEFAULT 'COMPRA_ESTOQUE',
                centro_custo              VARCHAR(50),
                codigo_movimento_estoque  INT,
                observacoes               VARCHAR(500),
                data_inclusao             DATETIME,
                usuario_inclusao          VARCHAR(50)
            );
            """
        else:
            sql = """
            IF OBJECT_ID(N'dbo.USER_geoapolo_contas_a_pagar', N'U') IS NULL
            BEGIN
                CREATE TABLE dbo.USER_geoapolo_contas_a_pagar (
                    codigo_documento          INT IDENTITY(1,1) NOT NULL,
                    codigo_empresa            VARCHAR(10) NOT NULL CONSTRAINT DF_ctaspagar_emp DEFAULT ('1.01'),
                    numero_documento          VARCHAR(40) NOT NULL,
                    serie_documento           VARCHAR(10) NULL CONSTRAINT DF_ctaspagar_serie DEFAULT ('1'),
                    parcela                   INT NOT NULL CONSTRAINT DF_ctaspagar_parc DEFAULT (1),
                    total_parcelas            INT NOT NULL CONSTRAINT DF_ctaspagar_totparc DEFAULT (1),
                    entcod                    VARCHAR(20) NULL,
                    fornecedor_nome           VARCHAR(200) NOT NULL,
                    cnpj_cpf                  VARCHAR(20) NULL,
                    data_emissao              DATE NOT NULL CONSTRAINT DF_ctaspagar_dtemis DEFAULT (CONVERT(DATE, GETDATE())),
                    data_vencimento           DATE NOT NULL,
                    data_pagamento            DATE NULL,
                    valor_original            NUMERIC(15,2) NOT NULL,
                    valor_desconto            NUMERIC(15,2) NOT NULL CONSTRAINT DF_ctaspagar_desc DEFAULT (0.00),
                    valor_juros_multa         NUMERIC(15,2) NOT NULL CONSTRAINT DF_ctaspagar_jur DEFAULT (0.00),
                    valor_pago                NUMERIC(15,2) NOT NULL CONSTRAINT DF_ctaspagar_pago DEFAULT (0.00),
                    saldo_aberto              NUMERIC(15,2) NOT NULL,
                    situacao                  VARCHAR(20) NOT NULL CONSTRAINT DF_ctaspagar_sit DEFAULT ('ABERTO'),
                    tipo_documento            VARCHAR(30) NOT NULL CONSTRAINT DF_ctaspagar_tipo DEFAULT ('ENTRADA_ESTOQUE'),
                    origem                    VARCHAR(50) NOT NULL CONSTRAINT DF_ctaspagar_origem DEFAULT ('COMPRA_ESTOQUE'),
                    centro_custo              VARCHAR(50) NULL,
                    codigo_movimento_estoque  INT NULL,
                    observacoes               VARCHAR(500) NULL,
                    data_inclusao             DATETIME NOT NULL CONSTRAINT DF_ctaspagar_dtinc DEFAULT (GETDATE()),
                    usuario_inclusao          VARCHAR(50) NULL,
                    CONSTRAINT PK_USER_geoapolo_contas_a_pagar PRIMARY KEY CLUSTERED (codigo_documento ASC)
                );
                CREATE NONCLUSTERED INDEX IX_ctaspagar_emp_venc_sit ON dbo.USER_geoapolo_contas_a_pagar (codigo_empresa, data_vencimento, situacao);
                CREATE NONCLUSTERED INDEX IX_ctaspagar_fornecedor ON dbo.USER_geoapolo_contas_a_pagar (entcod, fornecedor_nome);
                CREATE NONCLUSTERED INDEX IX_ctaspagar_movestq ON dbo.USER_geoapolo_contas_a_pagar (codigo_movimento_estoque);
            END
            """
        try:
            cur = self._get_cursor()
            cur.execute(sql)
            self.commit()
            return True, "Tabela USER_geoapolo_contas_a_pagar criada com sucesso!"
        except Exception as e:
            self.rollback()
            return False, f"Erro ao criar tabela de contas a pagar: {e}"

    def inserir_documento_pagar(self, doc: DocumentoPagarDTO) -> Tuple[bool, str, int]:
        """Insere um novo documento/título a pagar."""
        if not self.tabela_existe():
            return False, "A tabela USER_geoapolo_contas_a_pagar ainda não existe no banco de dados.", 0

        cur = self._get_cursor()
        is_sqlite = "sqlite" in type(self._conn).__module__.lower() if self._conn else False
        sql = """
            INSERT INTO USER_geoapolo_contas_a_pagar (
                codigo_empresa, numero_documento, serie_documento, parcela, total_parcelas,
                entcod, fornecedor_nome, cnpj_cpf, data_emissao, data_vencimento,
                valor_original, valor_desconto, valor_juros_multa, valor_pago,
                saldo_aberto, situacao, tipo_documento, origem, centro_custo,
                codigo_movimento_estoque, observacoes, usuario_inclusao
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?
            );
        """
        if not is_sqlite:
            sql = "SET NOCOUNT ON;\n" + sql + "\nSELECT SCOPE_IDENTITY();"
        try:
            v_orig = round(float(doc.valor_original or 0.0), 2)
            v_desc = round(float(doc.valor_desconto or 0.0), 2)
            v_jur = round(float(doc.valor_juros_multa or 0.0), 2)
            v_pago = round(float(doc.valor_pago or 0.0), 2)
            saldo = round(float(doc.saldo_aberto if doc.saldo_aberto is not None else (v_orig - v_desc + v_jur - v_pago)), 2)
            sit = doc.situacao.upper() if doc.situacao else ("QUITADO" if saldo <= 0 else "ABERTO")

            params = [
                doc.codigo_empresa or "1.01",
                doc.numero_documento.strip().upper(),
                doc.serie_documento or "1",
                doc.parcela or 1,
                doc.total_parcelas or 1,
                doc.entcod.strip() if doc.entcod else None,
                doc.fornecedor_nome.strip().upper() or "FORNECEDOR NÃO INFORMADO",
                doc.cnpj_cpf.strip() if doc.cnpj_cpf else None,
                doc.data_emissao or datetime.now().strftime("%Y-%m-%d"),
                doc.data_vencimento or datetime.now().strftime("%Y-%m-%d"),
                v_orig,
                v_desc,
                v_jur,
                v_pago,
                saldo,
                sit,
                doc.tipo_documento or "ENTRADA_ESTOQUE",
                doc.origem or "COMPRA_ESTOQUE",
                (doc.centro_custo or "").strip().upper(),
                doc.codigo_movimento_estoque,
                (doc.observacoes or "").strip().upper(),
                doc.usuario_inclusao or "",
            ]
            cur.execute(sql, params)
            if is_sqlite:
                novo_id = int(cur.lastrowid or 1)
            else:
                try:
                    row = cur.fetchone()
                    novo_id = int(row[0]) if row and row[0] is not None else 0
                except Exception:
                    novo_id = 1
            self.commit()
            return True, f"Título financeiro Nº {novo_id} gerado com sucesso!", novo_id
        except Exception as e:
            self.rollback()
            logger.error("Erro ao inserir título a pagar: %s", e)
            return False, f"Erro ao inserir título financeiro: {e}", 0

    def listar_documentos(self, filtro: FiltroContasPagarDTO) -> List[DocumentoPagarDTO]:
        """Consulta documentos a pagar conforme filtros aplicados."""
        if not self.tabela_existe():
            return []

        cur = self._get_cursor()
        where_clauses = ["codigo_empresa = ?"]
        params = [filtro.codigo_empresa or "1.01"]

        if filtro.situacao and filtro.situacao != "TODAS":
            where_clauses.append("situacao = ?")
            params.append(filtro.situacao.upper())

        if filtro.data_ini:
            where_clauses.append("data_vencimento >= ?")
            params.append(filtro.data_ini)

        if filtro.data_fim:
            where_clauses.append("data_vencimento <= ?")
            params.append(filtro.data_fim)

        if filtro.termo_busca:
            termo = f"%{filtro.termo_busca.strip().upper()}%"
            where_clauses.append("(numero_documento LIKE ? OR fornecedor_nome LIKE ? OR entcod LIKE ?)")
            params.extend([termo, termo, termo])

        if filtro.centro_custo:
            where_clauses.append("centro_custo = ?")
            params.append(filtro.centro_custo.strip().upper())

        sql = f"""
            SELECT
                codigo_documento, codigo_empresa, numero_documento, serie_documento,
                parcela, total_parcelas, ISNULL(entcod, ''), fornecedor_nome,
                ISNULL(cnpj_cpf, ''),
                CONVERT(VARCHAR(10), data_emissao, 120),
                CONVERT(VARCHAR(10), data_vencimento, 120),
                CONVERT(VARCHAR(10), data_pagamento, 120),
                valor_original, valor_desconto, valor_juros_multa, valor_pago,
                saldo_aberto, situacao, tipo_documento, origem,
                ISNULL(centro_custo, ''), codigo_movimento_estoque,
                ISNULL(observacoes, ''),
                CONVERT(VARCHAR(19), data_inclusao, 120),
                ISNULL(usuario_inclusao, '')
            FROM USER_geoapolo_contas_a_pagar WITH (NOLOCK)
            WHERE {" AND ".join(where_clauses)}
            ORDER BY data_vencimento ASC, codigo_documento DESC
        """
        cur.execute(sql, params)
        rows = cur.fetchall()
        resultado = []
        for r in rows:
            dto = DocumentoPagarDTO(
                codigo_documento=r[0],
                codigo_empresa=r[1],
                numero_documento=r[2],
                serie_documento=r[3],
                parcela=r[4],
                total_parcelas=r[5],
                entcod=r[6],
                fornecedor_nome=r[7],
                cnpj_cpf=r[8],
                data_emissao=r[9] or "",
                data_vencimento=r[10] or "",
                data_pagamento=r[11] if r[11] else None,
                valor_original=float(r[12] or 0.0),
                valor_desconto=float(r[13] or 0.0),
                valor_juros_multa=float(r[14] or 0.0),
                valor_pago=float(r[15] or 0.0),
                saldo_aberto=float(r[16] or 0.0),
                situacao=r[17] or "ABERTO",
                tipo_documento=r[18] or "",
                origem=r[19] or "",
                centro_custo=r[20] or "",
                codigo_movimento_estoque=r[21],
                observacoes=r[22] or "",
                data_inclusao=r[23] or "",
                usuario_inclusao=r[24] or "",
            )
            resultado.append(dto)
        return resultado

    def obter_resumo(self, filtro: FiltroContasPagarDTO) -> ResumoContasPagarDTO:
        """Calcula totais consolidados para os cards de resumo da tela."""
        if not self.tabela_existe():
            return ResumoContasPagarDTO()

        cur = self._get_cursor()
        where_clauses = ["codigo_empresa = ?"]
        params = [filtro.codigo_empresa or "1.01"]

        if filtro.data_ini:
            where_clauses.append("data_vencimento >= ?")
            params.append(filtro.data_ini)

        if filtro.data_fim:
            where_clauses.append("data_vencimento <= ?")
            params.append(filtro.data_fim)

        sql = f"""
            SELECT
                COUNT(codigo_documento) AS total_titulos,
                ISNULL(SUM(valor_original), 0.0) AS total_original,
                ISNULL(SUM(saldo_aberto), 0.0) AS total_aberto,
                ISNULL(SUM(valor_pago), 0.0) AS total_pago,
                SUM(CASE WHEN situacao = 'ABERTO' THEN 1 ELSE 0 END) AS qtd_abertos,
                SUM(CASE WHEN situacao = 'QUITADO' THEN 1 ELSE 0 END) AS qtd_quitados
            FROM USER_geoapolo_contas_a_pagar WITH (NOLOCK)
            WHERE {" AND ".join(where_clauses)}
        """
        cur.execute(sql, params)
        row = cur.fetchone()
        if row:
            return ResumoContasPagarDTO(
                total_titulos=row[0] or 0,
                total_original=float(row[1] or 0.0),
                total_aberto=float(row[2] or 0.0),
                total_pago=float(row[3] or 0.0),
                qtd_abertos=row[4] or 0,
                qtd_quitados=row[5] or 0,
            )
        return ResumoContasPagarDTO()

    def baixar_documento(self, baixa: BaixaDocumentoDTO) -> Tuple[bool, str]:
        """Registra a liquidação ou pagamento de um título a pagar."""
        if not self.tabela_existe():
            return False, "Tabela USER_geoapolo_contas_a_pagar não encontrada."

        cur = self._get_cursor()
        try:
            cur.execute("""
                SELECT valor_original, valor_pago, saldo_aberto, situacao
                FROM USER_geoapolo_contas_a_pagar
                WHERE codigo_documento = ?
            """, [baixa.codigo_documento])
            row = cur.fetchone()
            if not row:
                return False, "Documento financeiro não encontrado."

            v_orig = float(row[0] or 0.0)
            pago_atual = float(row[1] or 0.0)
            novo_pago = round(pago_atual + baixa.valor_pago, 2)
            novo_saldo = round(max(0.0, v_orig - novo_pago - baixa.valor_desconto + baixa.valor_juros_multa), 2)
            nova_situacao = "QUITADO" if novo_saldo <= 0.001 else "ABERTO"

            obs_add = f" BAIXA EM {baixa.data_pagamento}: R$ {baixa.valor_pago:.2f}. {baixa.observacao_baixa}".strip()

            cur.execute("""
                UPDATE USER_geoapolo_contas_a_pagar
                SET valor_pago = ?,
                    saldo_aberto = ?,
                    valor_desconto = valor_desconto + ?,
                    valor_juros_multa = valor_juros_multa + ?,
                    data_pagamento = ?,
                    situacao = ?,
                    observacoes = ISNULL(observacoes, '') + ?
                WHERE codigo_documento = ?
            """, [
                novo_pago, novo_saldo, baixa.valor_desconto, baixa.valor_juros_multa,
                baixa.data_pagamento, nova_situacao, obs_add, baixa.codigo_documento
            ])
            self.commit()
            return True, f"Documento Nº {baixa.codigo_documento} baixado com sucesso! (Situação: {nova_situacao})"
        except Exception as e:
            self.rollback()
            logger.error("Erro ao baixar título financeiro: %s", e)
            return False, f"Erro ao baixar documento: {e}"
