"""
Módulo de Verificação de Sanidade e Diagnóstico de Esquema do Banco de Dados.
Especializado nas tabelas de Produtos, Cores, Marcas e Estoque do GeoApolo / GeoAlvo.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import tkinter as tk
from tkinter import ttk, messagebox
from core.recursos import centralizar_janela, aplicar_icone_janela

logger = logging.getLogger(__name__)

# Lista canônica das 15 tabelas que compõem o módulo de Produtos e Estoque
TABELAS_ESTOQUE_PRODUTOS = [
    {
        "nome": "USER_geoapolo_produtos",
        "aliases": ["USER_geoapolo_produtos"],
        "obrigatoria": True,
        "descricao": "Catálogo principal de produtos do GeoApolo",
        "ddl": """
            IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USER_geoapolo_produtos' AND xtype = 'U')
            BEGIN
                CREATE TABLE USER_geoapolo_produtos (
                    prodcod NUMERIC(10, 0) NOT NULL PRIMARY KEY,
                    prodcodestr VARCHAR(31) NULL,
                    prodnome VARCHAR(100) NOT NULL,
                    descricao_alternativa VARCHAR(100) NULL,
                    grupo VARCHAR(10) NULL,
                    grupocod NUMERIC(10, 0) NULL,
                    unidmedcod NUMERIC(10, 0) NULL,
                    observacoes TEXT NULL,
                    unidademedida VARCHAR(10) NULL,
                    codigo_inmetro VARCHAR(50) NULL,
                    codigo_lote VARCHAR(50) NULL,
                    unidade_medida VARCHAR(20) NULL
                );
            END
        """
    },
    {
        "nome": "USER_geoapolo_produto_grupo",
        "aliases": ["USER_geoapolo_produto_grupo", "user_geoapolo_produto_grupo"],
        "obrigatoria": True,
        "descricao": "Grupos de produtos",
        "ddl": """
            IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USER_geoapolo_produto_grupo' AND xtype = 'U')
            BEGIN
                CREATE TABLE USER_geoapolo_produto_grupo (
                    grupocod NUMERIC(10, 0) NOT NULL PRIMARY KEY,
                    codigo_estruturado VARCHAR(30) NULL,
                    nome_grupo VARCHAR(80) NOT NULL
                );
            END
        """
    },
    {
        "nome": "USER_geoapolo_produto_marcas",
        "aliases": ["USER_geoapolo_produto_marcas", "USER_geoapolo_marcas"],
        "obrigatoria": True,
        "descricao": "Catálogo de marcas de produtos",
        "ddl": """
            IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USER_geoapolo_produto_marcas' AND xtype = 'U')
            BEGIN
                CREATE TABLE USER_geoapolo_produto_marcas (
                    codigo_marca NUMERIC(10, 0) NOT NULL PRIMARY KEY,
                    descricao_marca VARCHAR(80) NOT NULL
                );
            END
        """
    },
    {
        "nome": "USER_geoapolo_marca_produtos",
        "aliases": ["USER_geoapolo_marca_produtos"],
        "obrigatoria": True,
        "descricao": "Vínculo N:N entre Produto e Marca",
        "ddl": """
            IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USER_geoapolo_marca_produtos' AND xtype = 'U')
            BEGIN
                CREATE TABLE USER_geoapolo_marca_produtos (
                    codigo_marca NUMERIC(10, 0) NOT NULL,
                    prodcod NUMERIC(10, 0) NOT NULL,
                    CONSTRAINT pk_marcaprod PRIMARY KEY (codigo_marca, prodcod)
                );
                CREATE INDEX idx_marcaprod_prodcod ON USER_geoapolo_marca_produtos (prodcod);
            END
        """
    },
    {
        "nome": "USER_geoapolo_produto_cores",
        "aliases": ["USER_geoapolo_produto_cores", "user_geoapolo_produto_cores", "user_produto_cores"],
        "obrigatoria": True,
        "descricao": "Catálogo de cores de produtos",
        "ddl": """
            IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USER_geoapolo_produto_cores' AND xtype = 'U')
            BEGIN
                CREATE TABLE USER_geoapolo_produto_cores (
                    codigo_cor INT NOT NULL PRIMARY KEY,
                    descricao_cor VARCHAR(50) NOT NULL
                );
            END
        """
    },
    {
        "nome": "USER_geoapolo_produto_cor",
        "aliases": ["USER_geoapolo_produto_cor"],
        "obrigatoria": True,
        "descricao": "Vínculo N:N entre Produto e Cores",
        "ddl": """
            IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USER_geoapolo_produto_cor' AND xtype = 'U')
            BEGIN
                CREATE TABLE USER_geoapolo_produto_cor (
                    codigo_cor NUMERIC(10, 0) NOT NULL,
                    prodcod NUMERIC(10, 0) NOT NULL,
                    CONSTRAINT pk_codprodcor PRIMARY KEY (codigo_cor, prodcod)
                );
                CREATE INDEX idx_codprodcor_prodcod ON USER_geoapolo_produto_cor (prodcod);
            END
        """
    },
    {
        "nome": "USER_geoapolo_produto_foto",
        "aliases": ["USER_geoapolo_produto_foto"],
        "obrigatoria": False,
        "descricao": "Fotos dos produtos",
        "ddl": """
            IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USER_geoapolo_produto_foto' AND xtype = 'U')
            BEGIN
                CREATE TABLE USER_geoapolo_produto_foto (
                    prodcod NUMERIC(10, 0) NOT NULL PRIMARY KEY,
                    foto_produto VARBINARY(MAX) NULL
                );
            END
        """
    },
    {
        "nome": "user_geoapolo_produto_lote",
        "aliases": ["user_geoapolo_produto_lote", "USER_geoapolo_produto_lote"],
        "obrigatoria": True,
        "descricao": "Controle de lotes e validade de produtos",
        "ddl": """
            IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'user_geoapolo_produto_lote' AND xtype = 'U')
            BEGIN
                CREATE TABLE user_geoapolo_produto_lote (
                    ID_PRODUTO_LOTE INT IDENTITY(1,1) PRIMARY KEY,
                    prodcod NUMERIC(10, 0) NOT NULL,
                    NUMERO_LOTE VARCHAR(50) NOT NULL,
                    DATA_FABRICACAO DATE NULL,
                    DATA_VALIDADE DATE NULL,
                    QUANTIDADE_INICIAL NUMERIC(15, 4) DEFAULT 0,
                    QUANTIDADE_ATUAL NUMERIC(15, 4) DEFAULT 0,
                    ATIVO CHAR(1) DEFAULT 'S',
                    OBSERVACOES VARCHAR(255) NULL
                );
            END
        """
    },
    {
        "nome": "USER_geoapolo_estoque",
        "aliases": ["USER_geoapolo_estoque"],
        "obrigatoria": True,
        "descricao": "Saldos e quantidades em estoque por empresa",
        "ddl": """
            IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USER_geoapolo_estoque' AND xtype = 'U')
            BEGIN
                CREATE TABLE USER_geoapolo_estoque (
                    codigo_empresa VARCHAR(10) NOT NULL,
                    prodcod NUMERIC(10, 0) NOT NULL,
                    saldo_atual NUMERIC(15, 4) DEFAULT 0.0 NOT NULL,
                    quantidade_reservada NUMERIC(15, 4) DEFAULT 0.0 NOT NULL,
                    saldo_disponivel NUMERIC(15, 4) DEFAULT 0.0 NOT NULL,
                    data_ultima_movimentacao DATETIME NULL,
                    CONSTRAINT pk_geoapolo_estoque PRIMARY KEY (codigo_empresa, prodcod)
                );
            END
        """
    },
    {
        "nome": "USER_geoapolo_movimentacoes_estoque",
        "aliases": ["USER_geoapolo_movimentacoes_estoque"],
        "obrigatoria": True,
        "descricao": "Histórico de movimentações de estoque (Kardex)",
        "ddl": """
            IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USER_geoapolo_movimentacoes_estoque' AND xtype = 'U')
            BEGIN
                CREATE TABLE USER_geoapolo_movimentacoes_estoque (
                    codigo_movimento INT NOT NULL PRIMARY KEY,
                    codigo_empresa VARCHAR(10) NOT NULL,
                    tipo_movimento VARCHAR(1) NOT NULL,
                    data_movimento DATETIME NOT NULL,
                    prodcod NUMERIC(10, 0) NOT NULL,
                    quantidade NUMERIC(15, 4) NOT NULL,
                    saldo_anterior NUMERIC(15, 4) DEFAULT 0.0 NOT NULL,
                    saldo_posterior NUMERIC(15, 4) DEFAULT 0.0 NOT NULL,
                    documento_origem VARCHAR(50) NULL,
                    numero_requisicao VARCHAR(20) NULL,
                    centro_custo VARCHAR(30) NULL,
                    numero_lote VARCHAR(50) NULL,
                    usuario VARCHAR(50) NULL,
                    observacao VARCHAR(255) NULL
                );
            END
        """
    },
    {
        "nome": "user_geoapolo_almoxarifados",
        "aliases": ["user_geoapolo_almoxarifados"],
        "obrigatoria": True,
        "descricao": "Cadastro de Almoxarifados físicos",
        "ddl": """
            IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'user_geoapolo_almoxarifados' AND xtype = 'U')
            BEGIN
                CREATE TABLE user_geoapolo_almoxarifados (
                    codigo_almoxarifado INT NOT NULL PRIMARY KEY,
                    nome_almoxarifado VARCHAR(100) NOT NULL,
                    localizacao VARCHAR(150) NULL,
                    responsavel VARCHAR(80) NULL,
                    ativo CHAR(1) DEFAULT 'S'
                );
            END
        """
    },
    {
        "nome": "user_geoapolo_produtos_almoxarifados",
        "aliases": ["user_geoapolo_produtos_almoxarifados"],
        "obrigatoria": True,
        "descricao": "Saldos de produtos por almoxarifado",
        "ddl": """
            IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'user_geoapolo_produtos_almoxarifados' AND xtype = 'U')
            BEGIN
                CREATE TABLE user_geoapolo_produtos_almoxarifados (
                    id_produto_almoxarifado INT IDENTITY(1,1) PRIMARY KEY,
                    codigo_almoxarifado INT NOT NULL,
                    prodcod NUMERIC(10, 0) NOT NULL,
                    saldo_atual NUMERIC(15, 4) DEFAULT 0.0,
                    estoque_minimo NUMERIC(15, 4) DEFAULT 0.0,
                    estoque_maximo NUMERIC(15, 4) DEFAULT 0.0,
                    ponto_reposicao NUMERIC(15, 4) DEFAULT 0.0,
                    localizacao_corredor VARCHAR(50) NULL,
                    localizacao_prateleira VARCHAR(50) NULL,
                    data_ultima_movimentacao DATETIME NULL
                );
            END
        """
    },
    {
        "nome": "USER_geoapolo_requisicoes",
        "aliases": ["USER_geoapolo_requisicoes"],
        "obrigatoria": True,
        "descricao": "Cabeçalho de Requisições de Material",
        "ddl": """
            IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USER_geoapolo_requisicoes' AND xtype = 'U')
            BEGIN
                CREATE TABLE USER_geoapolo_requisicoes (
                    numero_requisicao VARCHAR(20) NOT NULL,
                    codigo_empresa VARCHAR(10) NOT NULL,
                    data_requisicao DATE NOT NULL,
                    solicitante VARCHAR(100) NOT NULL,
                    departamento VARCHAR(100) NULL,
                    centro_custo VARCHAR(30) NULL,
                    status VARCHAR(20) DEFAULT 'Pendente' NOT NULL,
                    tipo_requisicao VARCHAR(30) DEFAULT 'Normal' NOT NULL,
                    observacao VARCHAR(255) NULL,
                    CONSTRAINT pk_geoapolo_requisicoes PRIMARY KEY (numero_requisicao, codigo_empresa)
                );
            END
        """
    },
    {
        "nome": "USER_geoapolo_requisicao_itens",
        "aliases": ["USER_geoapolo_requisicao_itens"],
        "obrigatoria": True,
        "descricao": "Itens das Requisições de Material",
        "ddl": """
            IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USER_geoapolo_requisicao_itens' AND xtype = 'U')
            BEGIN
                CREATE TABLE USER_geoapolo_requisicao_itens (
                    numero_requisicao VARCHAR(20) NOT NULL,
                    codigo_empresa VARCHAR(10) NOT NULL,
                    item INT NOT NULL,
                    prodcod NUMERIC(10, 0) NOT NULL,
                    quantidade_solicitada NUMERIC(15, 4) NOT NULL,
                    quantidade_atendida NUMERIC(15, 4) DEFAULT 0.0 NOT NULL,
                    saldo_pendente NUMERIC(15, 4) NOT NULL,
                    observacao_item VARCHAR(255) NULL,
                    CONSTRAINT pk_geoapolo_req_itens PRIMARY KEY (numero_requisicao, codigo_empresa, item)
                );
            END
        """
    },
    {
        "nome": "USER_geoapolo_centrocontrole",
        "aliases": ["USER_geoapolo_centrocontrole", "USER_geoapolo_centro_controle"],
        "obrigatoria": True,
        "descricao": "Centros de Controle / Custo do GeoApolo",
        "ddl": """
            IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USER_geoapolo_centrocontrole' AND xtype = 'U')
            BEGIN
                CREATE TABLE USER_geoapolo_centrocontrole (
                    geocctrlcodestr VARCHAR(30) NOT NULL PRIMARY KEY,
                    geocctrlcodreduzido VARCHAR(30) NULL,
                    geocctrlnome VARCHAR(100) NOT NULL,
                    geocctrlcodestrniv VARCHAR(30) NULL,
                    geocctrlgrupo CHAR(1) NULL,
                    geocctrlcusto VARCHAR(30) NULL,
                    geodatavalidadeinicial DATETIME NULL,
                    geodatavalidadefinal DATETIME NULL,
                    empcod VARCHAR(10) NULL
                );
            END
        """
    },
]


def verificar_sanidade_estoque_produtos(connection=None) -> Dict[str, Any]:
    """
    Executa verificação completa de sanidade e diagnóstico no banco de dados ativo.
    Retorna dicionário estruturado com diagnóstico e lista de pendências.
    """
    if connection is None:
        try:
            from entidades.database import obter_conexao_banco
            connection = obter_conexao_banco()
        except Exception as e:
            return {
                "todas_ok": False,
                "erro_conexao": str(e),
                "tabelas_ok": [],
                "tabelas_faltando": [t["nome"] for t in TABELAS_ESTOQUE_PRODUTOS],
                "avisos": [f"Falha de conexão com o banco de dados: {e}"],
                "total_produtos": 0,
                "banco": "DESCONHECIDO",
            }

    is_sql_server = not hasattr(connection, "isolation_level")
    cur = connection.cursor()

    nome_banco = "DESCONHECIDO"
    try:
        cur.execute("SELECT DB_NAME()" if is_sql_server else "PRAGMA database_list")
        row = cur.fetchone()
        nome_banco = str(row[0]) if row else "DESCONHECIDO"
    except Exception:
        pass

    # Consulta todas as tabelas existentes no banco
    tabelas_existentes = set()
    try:
        if is_sql_server:
            cur.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
            """)
            for r in cur.fetchall():
                tabelas_existentes.add(str(r[0]).strip().upper())
        else:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            for r in cur.fetchall():
                tabelas_existentes.add(str(r[0]).strip().upper())
    except Exception as e:
        logger.warning(f"Erro ao listar tabelas: {e}")

    tabelas_ok = []
    tabelas_faltando = []
    avisos = []
    total_produtos = 0

    for def_tab in TABELAS_ESTOQUE_PRODUTOS:
        nome_oficial = def_tab["nome"]
        aliases = [a.upper() for a in def_tab["aliases"]]

        encontrada_nome = None
        for a in aliases:
            if a in tabelas_existentes:
                encontrada_nome = a
                break

        if encontrada_nome:
            qtd = 0
            try:
                cur.execute(f"SELECT COUNT(1) FROM [{encontrada_nome}]")
                row_c = cur.fetchone()
                qtd = int(row_c[0]) if row_c and row_c[0] is not None else 0
            except Exception:
                qtd = 0

            tabelas_ok.append({
                "nome": nome_oficial,
                "nome_real": encontrada_nome,
                "descricao": def_tab["descricao"],
                "linhas": qtd,
                "obrigatoria": def_tab["obrigatoria"],
            })

            if "USER_GEOAPOLO_PRODUTOS" in aliases:
                total_produtos = qtd
        else:
            tabelas_faltando.append({
                "nome": nome_oficial,
                "descricao": def_tab["descricao"],
                "obrigatoria": def_tab["obrigatoria"],
                "ddl": def_tab["ddl"],
            })

    if total_produtos == 0:
        avisos.append("O catálogo de produtos (USER_geoapolo_produtos) está vazio (0 registros cadastrados).")

    todas_ok = len(tabelas_faltando) == 0

    return {
        "todas_ok": todas_ok,
        "banco": nome_banco,
        "tabelas_ok": tabelas_ok,
        "tabelas_faltando": tabelas_faltando,
        "avisos": avisos,
        "total_produtos": total_produtos,
        "is_sql_server": is_sql_server,
    }


def gerar_script_sql_tabelas_faltantes(tabelas_faltando: List[Dict[str, Any]]) -> str:
    """Gera script SQL pronto para execução para criar as tabelas ausentes."""
    linhas = [
        "-- ============================================================================",
        "-- SCRIPT AUTOMÁTICO DE CRIAÇÃO DE TABELAS AUSENTES DO ESTOQUE E PRODUTOS",
        "-- GeoApolo V5",
        "-- ============================================================================",
        ""
    ]
    for t in tabelas_faltando:
        linhas.append(f"-- Criação de {t['nome']} ({t['descricao']})")
        linhas.append(t["ddl"].strip())
        linhas.append("GO\n")
    return "\n".join(linhas)


def aplicar_correcao_tabelas_faltantes(connection, tabelas_faltando: Optional[List[Dict[str, Any]]] = None) -> Tuple[bool, str]:
    """Aplica os comandos DDL para criar as tabelas ausentes no banco ativo."""
    if not connection:
        return False, "Sem conexão com o banco de dados."

    if tabelas_faltando is None:
        diag = verificar_sanidade_estoque_produtos(connection)
        tabelas_faltando = diag.get("tabelas_faltando", [])

    if not tabelas_faltando:
        return True, "Nenhuma tabela pendente para criar."

    cur = connection.cursor()
    criadas = []
    erros = []

    for t in tabelas_faltando:
        ddl = t.get("ddl", "").strip()
        if not ddl:
            continue
        try:
            cur.execute(ddl)
            criadas.append(t["nome"])
        except Exception as exc:
            erros.append(f"{t['nome']}: {exc}")

    try:
        connection.commit()
    except Exception:
        pass

    if erros:
        return False, f"Criadas: {', '.join(criadas)}. Erros: {'; '.join(erros)}"
    return True, f"Tabelas criadas com sucesso: {', '.join(criadas)}"


class DialogoSanidadeSchema(tk.Toplevel):
    """Diálogo visual moderno de alarme e diagnóstico de esquema para o usuário."""

    def __init__(self, parent, connection=None, diag_info: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.parent = parent
        self.connection = connection
        self.diag_info = diag_info or verificar_sanidade_estoque_produtos(connection)

        self.title("Diagnóstico de Sanidade do Banco de Dados - Produtos & Estoque")
        self.geometry("740x520")
        self.minsize(680, 460)
        self.transient(parent)
        self.grab_set()

        aplicar_icone_janela(self)
        self._criar_interface()
        centralizar_janela(self, parent, 740, 520)

    def _criar_interface(self):
        f_top = ttk.Frame(self, padding=12)
        f_top.pack(fill=tk.BOTH, expand=True)

        # Cabeçalho com status
        tem_faltando = len(self.diag_info.get("tabelas_faltando", [])) > 0
        banco = self.diag_info.get("banco", "DESCONHECIDO")

        cor_bg = "#FEF2F2" if tem_faltando else "#F0FDF4"
        cor_fg = "#B91C1C" if tem_faltando else "#15803D"
        titulo_txt = "🚨 ALARME: Tabelas Ausentes Detectadas no Banco de Dados" if tem_faltando else "✔ Esquema de Produtos e Estoque Verificado com Sucesso"

        f_banner = tk.Frame(f_top, bg=cor_bg, highlightbackground=cor_fg, highlightthickness=1, padx=12, pady=10)
        f_banner.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            f_banner,
            text=titulo_txt,
            font=("Segoe UI", 11, "bold"),
            bg=cor_bg,
            fg=cor_fg,
        ).pack(anchor=tk.W)

        sub_msg = f"Banco Conectado: [{banco}] | Total de Produtos no Catálogo: {self.diag_info.get('total_produtos', 0)}"
        tk.Label(
            f_banner,
            text=sub_msg,
            font=("Segoe UI", 9),
            bg=cor_bg,
            fg="#4B5563",
        ).pack(anchor=tk.W, pady=(2, 0))

        # Grade com todas as tabelas checadas
        f_grade = ttk.LabelFrame(f_top, text=" Diagnóstico Detalhado das Tabelas ", padding=8)
        f_grade.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        cols = ("status", "tabela", "linhas", "desc")
        self.tree = ttk.Treeview(f_grade, columns=cols, show="headings", height=11, selectmode="browse")
        self.tree.heading("status", text="Status")
        self.tree.heading("tabela", text="Nome da Tabela")
        self.tree.heading("linhas", text="Registros")
        self.tree.heading("desc", text="Descrição / Função")

        self.tree.column("status", width=90, anchor=tk.CENTER)
        self.tree.column("tabela", width=220, anchor=tk.W)
        self.tree.column("linhas", width=80, anchor=tk.E)
        self.tree.column("desc", width=300, anchor=tk.W)

        sb = ttk.Scrollbar(f_grade, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.tag_configure("ok", foreground="#15803D")
        self.tree.tag_configure("erro", foreground="#B91C1C", font=("Segoe UI", 9, "bold"))
        self.tree.tag_configure("vazio", foreground="#D97706")

        self._popular_grade()

        # Avisos adicionais
        if self.diag_info.get("avisos"):
            f_av = ttk.Frame(f_top)
            f_av.pack(fill=tk.X, pady=(0, 8))
            for av in self.diag_info["avisos"]:
                lbl = ttk.Label(f_av, text=f"• {av}", foreground="#B45309", font=("Segoe UI", 9, "italic"))
                lbl.pack(anchor=tk.W)

        # Barra de Ações
        f_botoes = ttk.Frame(f_top)
        f_botoes.pack(fill=tk.X)

        if tem_faltando:
            btn_corrigir = tk.Button(
                f_botoes,
                text="⚡ Criar Tabelas Faltantes Automaticamente",
                bg="#16A34A",
                fg="white",
                font=("Segoe UI", 9, "bold"),
                padx=12,
                pady=4,
                relief=tk.FLAT,
                command=self._executar_autocorrecao,
            )
            btn_corrigir.pack(side=tk.LEFT, padx=(0, 8))

            btn_sql = ttk.Button(
                f_botoes,
                text="📋 Copiar Script SQL",
                command=self._copiar_script_sql,
            )
            btn_sql.pack(side=tk.LEFT, padx=(0, 8))

        btn_fechar = ttk.Button(f_botoes, text="Fechar", command=self.destroy)
        btn_fechar.pack(side=tk.RIGHT)

    def _popular_grade(self):
        for it in self.tree.get_children():
            self.tree.delete(it)

        # Tabelas OK
        for t in self.diag_info.get("tabelas_ok", []):
            linhas = t["linhas"]
            status = "✅ Presente"
            tag = "ok" if linhas > 0 else "vazio"
            self.tree.insert(
                "",
                tk.END,
                values=(status, t["nome"], f"{linhas:,}".replace(",", "."), t["descricao"]),
                tags=(tag,),
            )

        # Tabelas Ausentes
        for t in self.diag_info.get("tabelas_faltando", []):
            self.tree.insert(
                "",
                tk.END,
                values=("❌ AUSENTE", t["nome"], "0", t["descricao"]),
                tags=("erro",),
            )

    def _executar_autocorrecao(self):
        if not self.connection:
            try:
                from entidades.database import obter_conexao_banco
                self.connection = obter_conexao_banco()
            except Exception as e:
                messagebox.showerror("Erro de Conexão", f"Não foi possível obter conexão: {e}", parent=self)
                return

        sucesso, msg = aplicar_correcao_tabelas_faltantes(
            self.connection,
            self.diag_info.get("tabelas_faltando", []),
        )

        if sucesso:
            messagebox.showinfo("Sucesso", f"{msg}\nO banco agora está com todas as tabelas em conformidade.", parent=self)
            self.diag_info = verificar_sanidade_estoque_produtos(self.connection)
            self._popular_grade()
        else:
            messagebox.showerror("Erro ao Criar Tabelas", msg, parent=self)

    def _copiar_script_sql(self):
        sql = gerar_script_sql_tabelas_faltantes(self.diag_info.get("tabelas_faltando", []))
        self.clipboard_clear()
        self.clipboard_append(sql)
        messagebox.showinfo("Copiado", "Script SQL copiado para a área de transferência!", parent=self)


def exibir_dialogo_sanidade_schema(parent, connection=None, apenas_se_houver_erro: bool = True) -> Optional[DialogoSanidadeSchema]:
    """Exibe o diálogo de sanidade se houver erro ou se for forçado."""
    diag = verificar_sanidade_estoque_produtos(connection)
    tem_problema = not diag.get("todas_ok", False)

    if apenas_se_houver_erro and not tem_problema:
        return None

    return DialogoSanidadeSchema(parent, connection=connection, diag_info=diag)
