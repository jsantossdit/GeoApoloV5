"""
Interface Gráfica para Emissão / Cadastro de Requisições de Materiais.
GeoApolo V5
Clean Architecture: Padrões de mercado para controle de estoque, requisições de almoxarifado,
consulta de saldo em tempo real, validações corporativas e atalhos.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Tuple
from datetime import datetime

from core import (
    centralizar_janela,
    vincular_maiusculo,
    configurar_navegacao_enter,
    vincular_mascara_data,
    converter_data_br_para_iso,
    validar_data_br,
    habilitar_filtro_dinamico_combobox,
    obter_empresa_ativa,
)
from .models import RequisicaoDTO, ItemRequisicaoDTO
from .service import EstoqueService


class NovaRequisicaoView(ttk.Frame):
    """Formulário de Emissão de Requisição de Materiais com Padrões de Mercado."""

    def __init__(self, parent=None, service: Optional[EstoqueService] = None, on_gravada_callback=None):
        super().__init__(parent)
        self.service = service
        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from .repository import EstoqueRepository
                conn = obter_conexao_banco()
                self.service = EstoqueService(EstoqueRepository(conn))
            except Exception:
                pass

        self._on_gravada_callback = on_gravada_callback
        self._itens_requisicao: List[ItemRequisicaoDTO] = []
        self._produto_selecionado = {"codigo": "", "nome": "", "unidade": "UN", "saldo": 0.0}

        self._setup_ui()
        self._configurar_atalhos()
        self._carregar_dados_iniciais()

    def _setup_ui(self):
        # ---------------------------------------------------------------------
        # Header Superior
        # ---------------------------------------------------------------------
        header = ttk.Frame(self, padding=(14, 10))
        header.pack(fill=tk.X)

        lbl_titulo = ttk.Label(
            header,
            text="Emissão de Requisição de Materiais",
            font=("Segoe UI", 13, "bold"),
            foreground="#1E3A8A",
        )
        lbl_titulo.pack(side=tk.LEFT)

        badge_status = tk.Label(
            header,
            text="STATUS: NOVA / ABERTA",
            bg="#EFF6FF",
            fg="#1D4ED8",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=2,
            relief=tk.RIDGE,
        )
        badge_status.pack(side=tk.RIGHT)

        # ---------------------------------------------------------------------
        # Seção 1: Cabeçalho da Requisição (Header)
        # ---------------------------------------------------------------------
        frame_cab = ttk.LabelFrame(self, text=" Dados Principais da Requisição ", padding=(12, 10))
        frame_cab.pack(fill=tk.X, padx=14, pady=(0, 8))

        # Linha 1: Nº Requisição, Empresa, Data Emissão
        row1 = ttk.Frame(frame_cab)
        row1.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(row1, text="Nº Requisição: *", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.var_req_num = tk.StringVar()
        self.ent_req_num = ttk.Entry(row1, textvariable=self.var_req_num, width=12, font=("Segoe UI", 9, "bold"))
        self.ent_req_num.pack(side=tk.LEFT, padx=(0, 16))

        ttk.Label(row1, text="Empresa: *").pack(side=tk.LEFT, padx=(0, 4))
        self.var_empcod = tk.StringVar(value=obter_empresa_ativa())
        self.ent_empcod = ttk.Entry(row1, textvariable=self.var_empcod, width=8)
        self.ent_empcod.pack(side=tk.LEFT, padx=(0, 16))

        ttk.Label(row1, text="Data Emissão:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_data = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.ent_data = ttk.Entry(row1, textvariable=self.var_data, width=12)
        self.ent_data.pack(side=tk.LEFT, padx=(0, 16))
        vincular_mascara_data(self.ent_data)

        ttk.Label(row1, text="Tipo: *", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.var_tipo_requisicao = tk.StringVar(value="Produto")
        self.cb_tipo_requisicao = ttk.Combobox(
            row1,
            textvariable=self.var_tipo_requisicao,
            values=["Produto", "Serviço"],
            state="readonly",
            width=12,
        )
        self.cb_tipo_requisicao.pack(side=tk.LEFT)

        # Linha 2: Solicitante (Código + Busca + Nome) e Centro de Custo
        row2 = ttk.Frame(frame_cab)
        row2.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(row2, text="Cód. Solicitante: *", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.var_solicitante_cod = tk.StringVar()
        vincular_maiusculo(self.var_solicitante_cod)
        self.ent_solicitante_cod = ttk.Entry(row2, textvariable=self.var_solicitante_cod, width=8, font=("Segoe UI", 9, "bold"))
        self.ent_solicitante_cod.pack(side=tk.LEFT, padx=(0, 4))
        self.ent_solicitante_cod.bind("<Return>", lambda e: self._ao_mudar_solicitante_cod())
        self.ent_solicitante_cod.bind("<FocusOut>", lambda e: self._ao_mudar_solicitante_cod())
        self.ent_solicitante_cod.bind("<F4>", lambda e: (self._abrir_modal_busca_usuarios(), "break")[1])

        self.btn_busca_solic = ttk.Button(
            row2,
            text="🔍 Buscar (F4)",
            width=11,
            command=self._abrir_modal_busca_usuarios,
        )
        self.btn_busca_solic.pack(side=tk.LEFT, padx=(0, 6))

        self.var_requerente = tk.StringVar()
        self.lbl_solicitante_nome = tk.Label(
            row2,
            textvariable=self.var_requerente,
            font=("Segoe UI", 9, "bold"),
            bg="#F1F5F9",
            fg="#1E3A8A",
            padx=8,
            pady=2,
            relief=tk.RIDGE,
            width=28,
            anchor=tk.W,
        )
        self.lbl_solicitante_nome.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row2, text="Centro de Custo / Controle: *", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.var_cctrl = tk.StringVar()
        self.cb_cctrl = ttk.Combobox(row2, textvariable=self.var_cctrl, width=32)
        self.cb_cctrl.pack(side=tk.LEFT)

        # Linha 3: Finalidade / Aplicação / Justificativa
        row3 = ttk.Frame(frame_cab)
        row3.pack(fill=tk.X)

        ttk.Label(row3, text="Finalidade / Aplicação:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_obs = tk.StringVar()
        vincular_maiusculo(self.var_obs)
        self.ent_obs = ttk.Entry(row3, textvariable=self.var_obs, width=78)
        self.ent_obs.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ---------------------------------------------------------------------
        # Seção 2: Inclusão Rápida de Itens (Item Entry)
        # ---------------------------------------------------------------------
        frame_add = ttk.LabelFrame(self, text=" Adicionar Item de Material ", padding=(12, 10))
        frame_add.pack(fill=tk.X, padx=14, pady=(0, 8))

        # Linha 1 de item: Cód. Produto, Botão Busca, Descrição, Unidade, Saldo Atual
        r_item1 = ttk.Frame(frame_add)
        r_item1.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(r_item1, text="Cód. Produto: *", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.var_prod_cod = tk.StringVar()
        vincular_maiusculo(self.var_prod_cod)
        self.ent_prod_cod = ttk.Entry(r_item1, textvariable=self.var_prod_cod, width=16)
        self.ent_prod_cod.pack(side=tk.LEFT, padx=(0, 4))
        self.ent_prod_cod.bind("<Return>", lambda e: self._ao_digitar_codigo_produto())
        self.ent_prod_cod.bind("<F4>", lambda e: (self._abrir_modal_busca_produtos(), "break")[1])

        btn_buscar_p = ttk.Button(r_item1, text="🔍 Buscar (F4)", command=self._abrir_modal_busca_produtos)
        btn_buscar_p.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(r_item1, text="Descrição:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_prod_nome = tk.StringVar()
        self.ent_prod_nome = ttk.Entry(r_item1, textvariable=self.var_prod_nome, state="readonly", width=34)
        self.ent_prod_nome.pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(r_item1, text="Unid:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_prod_unid = tk.StringVar(value="UN")
        self.ent_prod_unid = ttk.Entry(r_item1, textvariable=self.var_prod_unid, state="readonly", width=5)
        self.ent_prod_unid.pack(side=tk.LEFT, padx=(0, 14))

        # Badge de Saldo em Estoque
        ttk.Label(r_item1, text="Estoque Atual:").pack(side=tk.LEFT, padx=(0, 4))
        self.lbl_saldo_badge = tk.Label(
            r_item1,
            text="0.00",
            bg="#F3F4F6",
            fg="#4B5563",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=2,
            relief=tk.GROOVE,
        )
        self.lbl_saldo_badge.pack(side=tk.LEFT)

        # Linha 2 de item: Quantidade Solicitada, Observação do Item e Botão Adicionar
        r_item2 = ttk.Frame(frame_add)
        r_item2.pack(fill=tk.X)

        ttk.Label(r_item2, text="Quantidade Solicitada: *", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.var_qtd_solic = tk.StringVar()
        self.ent_qtd_solic = ttk.Entry(r_item2, textvariable=self.var_qtd_solic, width=12, font=("Segoe UI", 10, "bold"))
        self.ent_qtd_solic.pack(side=tk.LEFT, padx=(0, 16))
        self.ent_qtd_solic.bind("<Return>", lambda e: self._adicionar_item_grade())

        ttk.Label(r_item2, text="Observação do Item:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_item_obs = tk.StringVar()
        vincular_maiusculo(self.var_item_obs)
        self.ent_item_obs = ttk.Entry(r_item2, textvariable=self.var_item_obs, width=32)
        self.ent_item_obs.pack(side=tk.LEFT, padx=(0, 16))
        self.ent_item_obs.bind("<Return>", lambda e: self._adicionar_item_grade())

        self.btn_add_item = tk.Button(
            r_item2,
            text="➕ Adicionar Item (Enter)",
            bg="#16A34A",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=3,
            relief=tk.FLAT,
            command=self._adicionar_item_grade,
        )
        self.btn_add_item.pack(side=tk.LEFT)

        # ---------------------------------------------------------------------
        # Seção 3: Grade de Itens da Requisição
        # ---------------------------------------------------------------------
        frame_grid = ttk.LabelFrame(self, text=" Itens Solicitados nesta Requisição ", padding=6)
        frame_grid.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 8))

        cols = ("seq", "prodcod", "prodnome", "unid", "saldo_est", "qtd_solic", "obs")
        self.tree = ttk.Treeview(frame_grid, columns=cols, show="headings", height=8, selectmode="browse")

        self.tree.heading("seq", text="Item")
        self.tree.heading("prodcod", text="Código")
        self.tree.heading("prodnome", text="Descrição do Produto")
        self.tree.heading("unid", text="Unid")
        self.tree.heading("saldo_est", text="Saldo Estoque")
        self.tree.heading("qtd_solic", text="Qtd Solicitada")
        self.tree.heading("obs", text="Observação / Aplicação")

        self.tree.column("seq", width=50, anchor=tk.CENTER)
        self.tree.column("prodcod", width=120, anchor=tk.W)
        self.tree.column("prodnome", width=280, anchor=tk.W)
        self.tree.column("unid", width=60, anchor=tk.CENTER)
        self.tree.column("saldo_est", width=110, anchor=tk.E)
        self.tree.column("qtd_solic", width=110, anchor=tk.E)
        self.tree.column("obs", width=220, anchor=tk.W)

        sb_y = ttk.Scrollbar(frame_grid, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb_y.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Toolbar abaixo da grade
        bar_grid = ttk.Frame(self, padding=(14, 0))
        bar_grid.pack(fill=tk.X, pady=(0, 6))

        btn_rem = ttk.Button(bar_grid, text="🗑️ Remover Item (Del / F8)", command=self._remover_item_selecionado)
        btn_rem.pack(side=tk.LEFT, padx=(0, 8))

        btn_clr = ttk.Button(bar_grid, text="Limpar Itens", command=self._limpar_grade_itens)
        btn_clr.pack(side=tk.LEFT)

        # ---------------------------------------------------------------------
        # Seção 4: Totais e Botões de Ação
        # ---------------------------------------------------------------------
        bar_footer = ttk.Frame(self, padding=(14, 8))
        bar_footer.pack(fill=tk.X)

        # Cards de Totais
        f_tot = ttk.Frame(bar_footer)
        f_tot.pack(side=tk.LEFT)

        card_itens = tk.Frame(f_tot, bg="#F0F9FF", highlightbackground="#BAE6FD", highlightthickness=1, padx=12, pady=4)
        card_itens.pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(card_itens, text="Total de Itens", bg="#F0F9FF", fg="#0369A1", font=("Segoe UI", 8)).pack(anchor=tk.W)
        self.lbl_tot_itens = tk.Label(card_itens, text="0 item(ns)", bg="#F0F9FF", fg="#0369A1", font=("Segoe UI", 11, "bold"))
        self.lbl_tot_itens.pack(anchor=tk.W)

        card_qtd = tk.Frame(f_tot, bg="#F0FDF4", highlightbackground="#BBF7D0", highlightthickness=1, padx=12, pady=4)
        card_qtd.pack(side=tk.LEFT)
        tk.Label(card_qtd, text="Volume Solicitado", bg="#F0FDF4", fg="#15803D", font=("Segoe UI", 8)).pack(anchor=tk.W)
        self.lbl_tot_qtd = tk.Label(card_qtd, text="0.00", bg="#F0FDF4", fg="#15803D", font=("Segoe UI", 11, "bold"))
        self.lbl_tot_qtd.pack(anchor=tk.W)

        lbl_atalhos_req = ttk.Label(
            bar_footer,
            text="Atalhos: [F4] Buscar Produto | [Del / F8] Remover Item | [F5] Nova | [F10] Gravar",
            font=("Segoe UI", 8),
            foreground="#475569",
        )
        lbl_atalhos_req.pack(side=tk.LEFT, padx=(16, 0))

        # Botões de Gravação e Saída
        btn_fechar = ttk.Button(bar_footer, text="Fechar (Esc)", command=self._fechar_janela)
        btn_fechar.pack(side=tk.RIGHT, padx=(6, 0))

        btn_nova = ttk.Button(bar_footer, text="📄 Nova (F5)", command=self._limpar_formulario_completo)
        btn_nova.pack(side=tk.RIGHT, padx=(6, 0))

        self.btn_gravar = tk.Button(
            bar_footer,
            text="💾 Gravar Requisição (F10)",
            bg="#16A34A",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=5,
            relief=tk.FLAT,
            command=self._gravar_requisicao,
        )
        self.btn_gravar.pack(side=tk.RIGHT)

        # Navegação Enter no cabeçalho
        configurar_navegacao_enter([
            self.ent_req_num,
            self.ent_empcod,
            self.ent_data,
            self.ent_solicitante_cod,
            self.cb_cctrl,
            self.ent_obs,
            self.ent_prod_cod,
        ])

    def _configurar_atalhos(self):
        root = self.winfo_toplevel()
        root.bind("<F4>", lambda e: self._tratar_f4_contextual())
        root.bind("<F8>", lambda e: self._remover_item_selecionado())
        root.bind("<Delete>", lambda e: self._remover_item_selecionado())
        root.bind("<F5>", lambda e: self._limpar_formulario_completo())
        root.bind("<F10>", lambda e: self._gravar_requisicao())
        root.bind("<Escape>", lambda e: self._fechar_janela())

    def _tratar_f4_contextual(self):
        focus = self.focus_get()
        if focus == self.ent_solicitante_cod:
            self._abrir_modal_busca_usuarios()
        else:
            self._abrir_modal_busca_produtos()

    def _fechar_janela(self):
        toplevel = self.winfo_toplevel()
        if toplevel != self:
            toplevel.destroy()

    def _carregar_dados_iniciais(self):
        # Usuário logado na sessão corporativa
        try:
            from logon import sessao_usuario_atual
            emp = sessao_usuario_atual.get("codigo_empresa", "1.01")
            user = sessao_usuario_atual.get("nome_usuario", "")
            nome_compl = sessao_usuario_atual.get("nome_completo", "")
            usucod = sessao_usuario_atual.get("codigo_usuario") or sessao_usuario_atual.get("usucod_apolo") or ""
            if emp:
                self.var_empcod.set(emp)
            if usucod:
                self.var_solicitante_cod.set(str(usucod))
            if nome_compl or user:
                self.var_requerente.set((nome_compl or user).upper())
        except Exception:
            pass

        # Próximo número sequencial
        if self.service:
            emp = self.var_empcod.get().strip() or "1.01"
            prox_num = self.service.obter_proximo_numero_requisicao(emp)
            self.var_req_num.set(prox_num)

            # Centros de Custo
            centros = self.service.listar_centros_custo(emp)
            self._lista_centros_custo = list(centros)
            opcoes_cc = [f"{c[0]} - {c[1]}" for c in centros]
            habilitar_filtro_dinamico_combobox(self.cb_cctrl, opcoes_cc)
            if opcoes_cc:
                self.cb_cctrl.current(0)

        self.ent_solicitante_cod.focus_set()

    def _buscar_usuario_por_codigo(self, cod: str):
        if not cod:
            return None
        try:
            from entidades.database import obter_conexao_banco
            conn = obter_conexao_banco()
            cur = conn.cursor()
            cur.execute("""
                SELECT usucod, login, ISNULL(nome_completo, '') AS nome_completo
                FROM USER_geoapolo_usuarios WITH (NOLOCK)
                WHERE CAST(usucod AS VARCHAR) = ? OR UPPER(login) = UPPER(?)
            """, [cod, cod])
            row = cur.fetchone()
            if row:
                return {"usucod": row[0], "login": row[1], "nome_completo": row[2]}
        except Exception:
            pass
        return None

    def _ao_mudar_solicitante_cod(self, event=None):
        cod = self.var_solicitante_cod.get().strip()
        if not cod:
            self.var_requerente.set("")
            return
        u = self._buscar_usuario_por_codigo(cod)
        if u:
            self.var_solicitante_cod.set(str(u["usucod"]))
            nome = u["nome_completo"] or u["login"] or str(u["usucod"])
            self.var_requerente.set(nome.upper())
        else:
            self.var_requerente.set("USUÁRIO NÃO LOCALIZADO")

    def _abrir_modal_busca_usuarios(self):
        modal = tk.Toplevel(self)
        modal.title("Pesquisa de Solicitante / Usuários do Sistema")
        modal.transient(self)
        modal.grab_set()
        centralizar_janela(modal, self, 720, 480)

        f_cont = ttk.Frame(modal, padding=12)
        f_cont.pack(fill=tk.BOTH, expand=True)

        lbl_top = ttk.Label(
            f_cont,
            text="Selecionar Usuário Solicitante da Requisição",
            font=("Segoe UI", 11, "bold"),
            foreground="#1E3A8A",
        )
        lbl_top.pack(anchor=tk.W, pady=(0, 8))

        f_busca = ttk.Frame(f_cont)
        f_busca.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(f_busca, text="Buscar Solicitante:").pack(side=tk.LEFT, padx=(0, 4))
        var_b = tk.StringVar(value=self.var_solicitante_cod.get().strip())
        vincular_maiusculo(var_b)
        ent_b = ttk.Entry(f_busca, textvariable=var_b, width=32)
        ent_b.pack(side=tk.LEFT, padx=(0, 8))

        cols_b = ("cod", "login", "nome")
        tree_b = ttk.Treeview(f_cont, columns=cols_b, show="headings", height=11, selectmode="browse")
        tree_b.heading("cod", text="Cód. Usuário")
        tree_b.heading("login", text="Login")
        tree_b.heading("nome", text="Nome Completo do Solicitante")

        tree_b.column("cod", width=90, anchor=tk.CENTER)
        tree_b.column("login", width=140, anchor=tk.W)
        tree_b.column("nome", width=420, anchor=tk.W)

        sb_b = ttk.Scrollbar(f_cont, orient=tk.VERTICAL, command=tree_b.yview)
        tree_b.configure(yscrollcommand=sb_b.set)
        tree_b.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_b.pack(side=tk.RIGHT, fill=tk.Y)

        def recarregar_usuarios():
            termo = var_b.get().strip().upper()
            for it in tree_b.get_children():
                tree_b.delete(it)
            try:
                from entidades.database import obter_conexao_banco
                conn = obter_conexao_banco()
                cur = conn.cursor()
                if termo:
                    cur.execute("""
                        SELECT usucod, login, ISNULL(nome_completo, '') AS nome_completo
                        FROM USER_geoapolo_usuarios WITH (NOLOCK)
                        WHERE (CAST(usucod AS VARCHAR) LIKE ? OR UPPER(login) LIKE ? OR UPPER(nome_completo) LIKE ?)
                        ORDER BY nome_completo, login
                    """, [f"%{termo}%", f"%{termo}%", f"%{termo}%"])
                else:
                    cur.execute("""
                        SELECT TOP 200 usucod, login, ISNULL(nome_completo, '') AS nome_completo
                        FROM USER_geoapolo_usuarios WITH (NOLOCK)
                        ORDER BY nome_completo, login
                    """)
                for r in cur.fetchall():
                    tree_b.insert("", tk.END, values=(r[0], r[1], r[2] or r[1]))
            except Exception:
                pass

        def selecionar():
            sel = tree_b.selection()
            if not sel:
                return "break"
            vals = tree_b.item(sel[0], "values")
            self.var_solicitante_cod.set(str(vals[0]))
            self.var_requerente.set(vals[2] or vals[1])
            try:
                modal.destroy()
            except Exception:
                pass
            self.cb_cctrl.focus_set()
            return "break"

        ent_b.bind("<Return>", lambda e: (recarregar_usuarios(), "break")[1])
        tree_b.bind("<Double-1>", lambda e: (selecionar(), "break")[1])
        tree_b.bind("<Return>", lambda e: (selecionar(), "break")[1])
        modal.bind("<Escape>", lambda e: (modal.destroy(), "break")[1])

        btn_b = ttk.Button(f_busca, text="Filtrar", command=recarregar_usuarios)
        btn_b.pack(side=tk.LEFT)

        recarregar_usuarios()
        ent_b.focus_set()

    # -------------------------------------------------------------------------
    # BUSCA DE PRODUTOS E SALDO EM TEMPO REAL
    # -------------------------------------------------------------------------
    def _ao_digitar_codigo_produto(self):
        cod = self.var_prod_cod.get().strip().upper()
        if not cod:
            self._abrir_modal_busca_produtos()
            return

        if not self.service:
            return

        emp = self.var_empcod.get().strip() or "1.01"
        saldos = self.service.consultar_saldos_produtos(empcod=emp, termo_busca=cod)
        prod_encontrado = None
        for p in saldos:
            if p.prodcod_estr.upper() == cod:
                prod_encontrado = p
                break

        if prod_encontrado:
            self._definir_produto_selecionado(
                prod_encontrado.prodcod_estr,
                prod_encontrado.prodnome,
                prod_encontrado.unidade,
                prod_encontrado.saldo_atual,
            )
            self.ent_qtd_solic.focus_set()
        else:
            self._abrir_modal_busca_produtos(termo_inicial=cod)

    def _definir_produto_selecionado(self, codigo: str, nome: str, unidade: str, saldo: float):
        self._produto_selecionado = {
            "codigo": codigo,
            "nome": nome,
            "unidade": unidade or "UN",
            "saldo": saldo,
        }
        self.var_prod_cod.set(codigo)
        self.var_prod_nome.set(nome)
        self.var_prod_unid.set(unidade or "UN")

        # Atualiza badge de saldo
        if saldo > 0:
            self.lbl_saldo_badge.config(
                text=f"{saldo:.2f} {unidade} (Disponível)",
                bg="#DCFCE7",
                fg="#15803D",
            )
        else:
            self.lbl_saldo_badge.config(
                text=f"{saldo:.2f} {unidade} (Sem Saldo)",
                bg="#FEE2E2",
                fg="#B91C1C",
            )

    def _abrir_modal_busca_produtos(self, termo_inicial: str = ""):
        modal = tk.Toplevel(self)
        modal.title("Pesquisa Rápida de Produtos e Saldo em Estoque")
        modal.transient(self)
        modal.grab_set()
        centralizar_janela(modal, self, 720, 480)

        f_cont = ttk.Frame(modal, padding=12)
        f_cont.pack(fill=tk.BOTH, expand=True)

        lbl_top = ttk.Label(
            f_cont,
            text="Localizar Produto no Catálogo",
            font=("Segoe UI", 11, "bold"),
            foreground="#1E3A8A",
        )
        lbl_top.pack(anchor=tk.W, pady=(0, 8))

        f_busca = ttk.Frame(f_cont)
        f_busca.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(f_busca, text="Buscar:").pack(side=tk.LEFT, padx=(0, 4))
        var_b = tk.StringVar(value=termo_inicial)
        vincular_maiusculo(var_b)
        ent_b = ttk.Entry(f_busca, textvariable=var_b, width=32)
        ent_b.pack(side=tk.LEFT, padx=(0, 8))

        cols_b = ("cod", "nome", "unid", "saldo")
        tree_b = ttk.Treeview(f_cont, columns=cols_b, show="headings", height=12, selectmode="browse")
        tree_b.heading("cod", text="Código")
        tree_b.heading("nome", text="Descrição do Produto")
        tree_b.heading("unid", text="Unid")
        tree_b.heading("saldo", text="Saldo Atual")

        tree_b.column("cod", width=120, anchor=tk.W)
        tree_b.column("nome", width=340, anchor=tk.W)
        tree_b.column("unid", width=60, anchor=tk.CENTER)
        tree_b.column("saldo", width=100, anchor=tk.E)

        sb_b = ttk.Scrollbar(f_cont, orient=tk.VERTICAL, command=tree_b.yview)
        tree_b.configure(yscrollcommand=sb_b.set)
        tree_b.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_b.pack(side=tk.RIGHT, fill=tk.Y)

        tree_b.tag_configure("disp", foreground="#15803D")
        tree_b.tag_configure("zero", foreground="#B91C1C")

        lbl_status_produtos = tk.Label(
            f_cont,
            text="",
            font=("Segoe UI", 9),
            anchor=tk.W,
            justify=tk.LEFT,
        )
        lbl_status_produtos.pack(fill=tk.X, pady=(4, 0))

        b_modal = ttk.Frame(f_cont)
        b_modal.pack(fill=tk.X, pady=(8, 0))

        def abrir_cadastro_produtos():
            from produtos import abrir_janela_produtos
            w = abrir_janela_produtos(modal)
            modal.wait_window(w)
            filtrar()

        btn_novo_p = tk.Button(
            b_modal,
            text="➕ Cadastrar Produto",
            bg="#2563EB",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=3,
            relief=tk.FLAT,
            command=abrir_cadastro_produtos,
        )
        btn_novo_p.pack(side=tk.LEFT)

        emp = self.var_empcod.get().strip() or "1.01"

        def filtrar():
            for it in tree_b.get_children():
                tree_b.delete(it)
            t = var_b.get().strip().upper()
            try:
                prods = self.service.consultar_saldos_produtos(empcod=emp, termo_busca=t) if self.service else []
            except Exception as exc:
                lbl_status_produtos.config(
                    text=f"❌ Erro ao consultar produtos: {exc}",
                    fg="#DC2626",
                    bg="#FEF2F2",
                )
                return

            if not prods:
                total_cat = 0
                try:
                    total_cat = self.service.contar_total_produtos_catalogo() if (self.service and hasattr(self.service, "contar_total_produtos_catalogo")) else 0
                except Exception:
                    pass

                if total_cat == 0:
                    lbl_status_produtos.config(
                        text="⚠️ Catálogo Vazio: Nenhum produto cadastrado no banco (USER_geoapolo_produtos está vazia).\nUtilize o botão '➕ Cadastrar Produto' para inserir novos itens.",
                        fg="#B91C1C",
                        bg="#FEF2F2",
                    )
                else:
                    lbl_status_produtos.config(
                        text=f"Nenhum produto localizado para '{t}'. (Total no catálogo: {total_cat})",
                        fg="#6B7280",
                        bg="#F9FAFB",
                    )
            else:
                lbl_status_produtos.config(
                    text=f"✔ {len(prods)} produto(s) encontrado(s). Pressione Enter para selecionar o item.",
                    fg="#15803D",
                    bg="#F0FDF4",
                )
                for p in prods:
                    tag = "disp" if p.saldo_atual > 0 else "zero"
                    tree_b.insert(
                        "",
                        tk.END,
                        iid=p.prodcod_estr,
                        values=(p.prodcod_estr, p.prodnome, p.unidade, f"{p.saldo_atual:.2f}"),
                        tags=(tag,),
                    )
                filhos = tree_b.get_children()
                if filhos:
                    tree_b.selection_set(filhos[0])
                    tree_b.focus(filhos[0])

        btn_f = ttk.Button(f_busca, text="Filtrar", command=filtrar)
        btn_f.pack(side=tk.LEFT)
        ent_b.bind("<Return>", lambda e: filtrar())

        def selecionar():
            sel = tree_b.selection()
            if not sel:
                return "break"
            vals = tree_b.item(sel[0], "values")
            try:
                s_val = float(vals[3])
            except ValueError:
                s_val = 0.0
            self._definir_produto_selecionado(vals[0], vals[1], vals[2], s_val)
            try:
                modal.destroy()
            except Exception:
                pass
            self.ent_qtd_solic.focus_set()
            return "break"

        tree_b.bind("<Double-1>", lambda e: (selecionar(), "break")[1])
        tree_b.bind("<Return>", lambda e: (selecionar(), "break")[1])

        btn_ok = tk.Button(
            b_modal,
            text="✔ Selecionar Produto (Enter)",
            bg="#16A34A",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=3,
            relief=tk.FLAT,
            command=selecionar,
        )
        btn_ok.pack(side=tk.RIGHT, padx=(6, 0))

        btn_cancel = ttk.Button(b_modal, text="Cancelar (Esc)", command=modal.destroy)
        btn_cancel.pack(side=tk.RIGHT)
        modal.bind("<Escape>", lambda e: modal.destroy())
        modal.bind("<F4>", lambda e: (ent_b.focus_set(), ent_b.select_range(0, tk.END)))

        filtrar()
        ent_b.focus_set()
        ent_b.select_range(0, tk.END)

    # -------------------------------------------------------------------------
    # OPERAÇÕES DA GRADE DE ITENS
    # -------------------------------------------------------------------------
    def _adicionar_item_grade(self):
        cod = self.var_prod_cod.get().strip().upper()
        if not cod:
            messagebox.showwarning("Aviso", "Informe o código do produto ou use F4 para pesquisar.", parent=self)
            self.ent_prod_cod.focus_set()
            return

        nome = self.var_prod_nome.get().strip().upper() or cod
        unid = self.var_prod_unid.get().strip().upper() or "UN"

        try:
            qtd_val = float(self.var_qtd_solic.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida.", parent=self)
            self.ent_qtd_solic.focus_set()
            return

        if qtd_val <= 0:
            messagebox.showerror("Erro", "A quantidade solicitada deve ser maior que zero.", parent=self)
            self.ent_qtd_solic.focus_set()
            return

        obs_item = self.var_item_obs.get().strip().upper()
        saldo_est = self._produto_selecionado.get("saldo", 0.0)

        # Verifica se o produto já existe na lista
        item_existente = None
        for it in self._itens_requisicao:
            if it.prodcod_estr == cod:
                item_existente = it
                break

        if item_existente:
            item_existente.qtd_solicitada += qtd_val
            item_existente.saldo_pendente = item_existente.qtd_solicitada
            if obs_item:
                item_existente.observacao = obs_item
        else:
            novo_item = ItemRequisicaoDTO(
                req_num=self.var_req_num.get().strip(),
                item_seq=len(self._itens_requisicao) + 1,
                empcod=self.var_empcod.get().strip() or "1.01",
                prodcod_estr=cod,
                prodnome=nome,
                unidade=unid,
                qtd_solicitada=qtd_val,
                qtd_atendida=0.0,
                saldo_pendente=qtd_val,
                status_item="Pendente",
            )
            # Guardamos saldo físico como atributo dinâmico para exibição
            setattr(novo_item, "saldo_estoque_ref", saldo_est)
            setattr(novo_item, "observacao", obs_item)
            self._itens_requisicao.append(novo_item)

        self._atualizar_visual_grade()

        # Limpa campos de inserção para o próximo item
        self.var_prod_cod.set("")
        self.var_prod_nome.set("")
        self.var_prod_unid.set("UN")
        self.lbl_saldo_badge.config(text="0.00", bg="#F3F4F6", fg="#4B5563")
        self.var_qtd_solic.set("")
        self.var_item_obs.set("")
        self._produto_selecionado = {"codigo": "", "nome": "", "unidade": "UN", "saldo": 0.0}
        self.ent_prod_cod.focus_set()

    def _remover_item_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um item da grade para remover.", parent=self)
            return

        seq = int(self.tree.item(sel[0], "values")[0])
        self._itens_requisicao = [it for it in self._itens_requisicao if it.item_seq != seq]
        # Re-indexa sequencial
        for idx, it in enumerate(self._itens_requisicao, start=1):
            it.item_seq = idx
        self._atualizar_visual_grade()

    def _limpar_grade_itens(self):
        if not self._itens_requisicao:
            return
        if messagebox.askyesno("Confirmar", "Deseja remover todos os itens da requisição?", parent=self):
            self._itens_requisicao.clear()
            self._atualizar_visual_grade()

    def _atualizar_visual_grade(self):
        for it in self.tree.get_children():
            self.tree.delete(it)

        tot_vol = 0.0
        for it in self._itens_requisicao:
            tot_vol += it.qtd_solicitada
            s_ref = getattr(it, "saldo_estoque_ref", 0.0)
            obs_it = getattr(it, "observacao", "")
            self.tree.insert(
                "",
                tk.END,
                iid=str(it.item_seq),
                values=(
                    it.item_seq,
                    it.prodcod_estr,
                    it.prodnome,
                    it.unidade,
                    f"{s_ref:.2f}",
                    f"{it.qtd_solicitada:.2f}",
                    obs_it,
                ),
            )

        self.lbl_tot_itens.config(text=f"{len(self._itens_requisicao)} item(ns)")
        self.lbl_tot_qtd.config(text=f"{tot_vol:.2f}")

    def _limpar_formulario_completo(self):
        self._itens_requisicao.clear()
        self._atualizar_visual_grade()
        self._carregar_dados_iniciais()
        self.var_tipo_requisicao.set("Produto")
        self.var_data.set(datetime.now().strftime("%d/%m/%Y"))
        self.var_obs.set("")
        self.var_prod_cod.set("")
        self.var_prod_nome.set("")
        self.var_qtd_solic.set("")
        self.var_item_obs.set("")
        self.lbl_saldo_badge.config(text="0.00", bg="#F3F4F6", fg="#4B5563")

    # -------------------------------------------------------------------------
    # GRAVAÇÃO DA REQUISIÇÃO
    # -------------------------------------------------------------------------
    def _gravar_requisicao(self):
        req_num = self.var_req_num.get().strip()
        if not req_num:
            messagebox.showerror("Erro", "O número da requisição é obrigatório.", parent=self)
            self.ent_req_num.focus_set()
            return

        solic_cod = self.var_solicitante_cod.get().strip()
        if not solic_cod:
            messagebox.showerror("Erro", "O código do solicitante é obrigatório.", parent=self)
            self.ent_solicitante_cod.focus_set()
            return

        requerente = self.var_requerente.get().strip().upper()
        if not requerente or requerente == "USUÁRIO NÃO LOCALIZADO":
            messagebox.showerror("Erro", "Informe um solicitante / requerente válido cadastrado no sistema.", parent=self)
            self.ent_solicitante_cod.focus_set()
            return

        cctrl_raw = self.var_cctrl.get().strip().upper()
        if not cctrl_raw:
            messagebox.showerror("Erro", "O Centro de Custo / Controle é obrigatório.", parent=self)
            self.cb_cctrl.focus_set()
            return

        cctrl_cod = cctrl_raw.split(" - ")[0].strip()
        for c in getattr(self, "_lista_centros_custo", []):
            if c[0].upper() == cctrl_raw or cctrl_raw in c[1].upper():
                cctrl_cod = c[0]
                break

        dt_input = self.var_data.get().strip()
        if not dt_input:
            messagebox.showerror("Erro", "Informe a data de emissão da requisição.", parent=self)
            self.ent_data.focus_set()
            return

        if "/" in dt_input and not validar_data_br(dt_input[:10]):
            messagebox.showerror("Erro", "Data de emissão inválida. Utilize o formato DD/MM/AAAA.", parent=self)
            self.ent_data.focus_set()
            return

        if not self._itens_requisicao:
            messagebox.showerror("Erro", "Adicione ao menos um item de material à requisição antes de gravar.", parent=self)
            self.ent_prod_cod.focus_set()
            return

        if not messagebox.askyesno(
            "Confirmação de Emissão",
            f"Confirma a emissão da Requisição Nº {req_num} com {len(self._itens_requisicao)} item(ns)?",
            parent=self,
        ):
            return

        d_iso = converter_data_br_para_iso(dt_input[:10])
        dt_str = f"{d_iso} {datetime.now().strftime('%H:%M:%S')}"

        req_dto = RequisicaoDTO(
            req_num=req_num,
            empcod=self.var_empcod.get().strip() or "1.01",
            data_req=dt_str,
            tipo_requisicao=self.var_tipo_requisicao.get().strip() or "Produto",
            solicitante_cod=solic_cod,
            requerente=requerente,
            centro_custo=cctrl_cod,
            status="Aberta",
            observacao=self.var_obs.get().strip().upper(),
            itens=self._itens_requisicao,
        )

        res = self.service.criar_requisicao(req_dto)
        if res.sucesso:
            messagebox.showinfo("Sucesso", f"{res.mensagem}\n\nO formulário foi preparado para uma nova requisição.", parent=self)
            if self._on_gravada_callback:
                try:
                    self._on_gravada_callback()
                except Exception:
                    pass
            self._limpar_formulario_completo()
            self.ent_req_num.focus_set()
        else:
            messagebox.showerror("Erro ao Gravar", res.mensagem, parent=self)


def abrir_nova_requisicao_material(parent=None, connection=None, on_gravada_callback=None):
    """Abre a tela de emissão de requisição de material em janela TopLevel centralizada."""
    win = tk.Toplevel(parent)
    win.title("Nova Requisição de Material - GeoAlvo")
    win.minsize(980, 620)
    centralizar_janela(win, parent, 1080, 680)
    view = NovaRequisicaoView(win, on_gravada_callback=on_gravada_callback)
    view.pack(fill=tk.BOTH, expand=True)
    return win
