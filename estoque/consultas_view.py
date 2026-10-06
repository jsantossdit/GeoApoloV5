"""
Interface Gráfica para Consultas de Estoque:
1. Consulta Ficha Estoque (Kardex)
2. Consulta Saldo Produto
3. Consulta Requisições de Materiais
GeoApolo V5
Clean Architecture: Visual moderno com cards estatísticos, extrato cronológico e badges.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from datetime import datetime, timedelta

from core import (
    centralizar_janela,
    vincular_maiusculo,
    configurar_navegacao_enter,
    vincular_mascara_data,
    formatar_data_br,
    obter_empresa_ativa,
)
from .models import FichaEstoqueLinhaDTO, SaldoProdutoDTO, RequisicaoDTO
from .service import EstoqueService


class ConsultasEstoqueView(ttk.Frame):
    """Tela consolidada de Consultas de Estoque com Notebook multi-abas."""

    def __init__(self, parent=None, service: Optional[EstoqueService] = None, aba_inicial: int = 0, prodcod_inicial: str = ""):
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

        self._prodcod_inicial = prodcod_inicial
        self._setup_ui()
        self._configurar_atalhos()

        # Seleciona aba desejada
        if 0 <= aba_inicial < 3:
            self.notebook.select(aba_inicial)

        if self._prodcod_inicial:
            self.var_kardex_prod.set(self._prodcod_inicial)
            self.carregar_ficha_estoque()

        # Cargas iniciais
        if aba_inicial == 1:
            self.carregar_saldos_produtos()
        elif aba_inicial == 2:
            self.carregar_requisicoes_consulta()

    def _setup_ui(self):
        # Header superior
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        lbl_titulo = ttk.Label(
            header,
            text="Central de Consultas de Estoque",
            font=("Segoe UI", 13, "bold"),
            foreground="#1E3A8A",
        )
        lbl_titulo.pack(side=tk.LEFT)

        # Notebook com 3 abas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        # 1. Aba Ficha Estoque (Kardex)
        self.tab_kardex = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(self.tab_kardex, text="  📊 Ficha de Estoque (Kardex)  ")
        self._setup_tab_kardex()

        # 2. Aba Saldo de Produtos
        self.tab_saldos = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(self.tab_saldos, text="  📦 Saldo de Produtos  ")
        self._setup_tab_saldos()

        # 3. Aba Requisições de Materiais
        self.tab_reqs = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(self.tab_reqs, text="  📑 Requisições de Materiais  ")
        self._setup_tab_reqs()

        self.notebook.bind("<<NotebookTabChanged>>", self._ao_mudar_aba)

        # Barra inferior
        bar_bottom = ttk.Frame(self, padding=(12, 8))
        bar_bottom.pack(fill=tk.X)

        lbl_atalhos = ttk.Label(
            bar_bottom,
            text="Atalhos: [F4] Buscar Produto | [F5] Atualizar Consulta | [Duplo Clique] Abrir Kardex | [Esc] Fechar",
            font=("Segoe UI", 8),
            foreground="#475569",
        )
        lbl_atalhos.pack(side=tk.LEFT)

        btn_fechar = ttk.Button(bar_bottom, text="Fechar (Esc)", command=self._fechar_janela)
        btn_fechar.pack(side=tk.RIGHT)

    def _configurar_atalhos(self):
        root = self.winfo_toplevel()
        root.bind("<F5>", lambda e: self._atualizar_aba_atual())
        root.bind("<F4>", lambda e: self._ao_pressionar_f4())
        root.bind("<Escape>", lambda e: self._fechar_janela())

    def _ao_pressionar_f4(self):
        aba_idx = self.notebook.index(self.notebook.select())
        if aba_idx == 0:
            self._abrir_modal_busca_kardex()
        elif aba_idx == 1:
            self.ent_saldo_busca.focus_set()
            self.ent_saldo_busca.select_range(0, tk.END)
        elif aba_idx == 2:
            self.ent_req_busca.focus_set()
            self.ent_req_busca.select_range(0, tk.END)

    def _abrir_modal_busca_kardex(self):
        modal = tk.Toplevel(self)
        modal.title("Pesquisa de Produtos para Kardex")
        modal.transient(self)
        modal.grab_set()
        centralizar_janela(modal, self, 700, 460)

        f_cont = ttk.Frame(modal, padding=12)
        f_cont.pack(fill=tk.BOTH, expand=True)

        ttk.Label(f_cont, text="Localizar Produto para Ficha de Estoque (Kardex)", font=("Segoe UI", 11, "bold"), foreground="#1E3A8A").pack(anchor=tk.W, pady=(0, 8))

        f_b = ttk.Frame(f_cont)
        f_b.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(f_b, text="Buscar:").pack(side=tk.LEFT, padx=(0, 4))
        var_b = tk.StringVar(value=self.var_kardex_prod.get().strip())
        vincular_maiusculo(var_b)
        ent_b = ttk.Entry(f_b, textvariable=var_b, width=32)
        ent_b.pack(side=tk.LEFT, padx=(0, 8))

        cols_b = ("cod", "nome", "unid", "saldo")
        tree_b = ttk.Treeview(f_cont, columns=cols_b, show="headings", height=11, selectmode="browse")
        tree_b.heading("cod", text="Código")
        tree_b.heading("nome", text="Descrição do Produto")
        tree_b.heading("unid", text="Unid")
        tree_b.heading("saldo", text="Saldo Atual")
        tree_b.column("cod", width=110, anchor=tk.W)
        tree_b.column("nome", width=340, anchor=tk.W)
        tree_b.column("unid", width=60, anchor=tk.CENTER)
        tree_b.column("saldo", width=100, anchor=tk.E)

        sb_b = ttk.Scrollbar(f_cont, orient=tk.VERTICAL, command=tree_b.yview)
        tree_b.configure(yscrollcommand=sb_b.set)
        tree_b.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_b.pack(side=tk.RIGHT, fill=tk.Y)

        def recarregar():
            for it in tree_b.get_children():
                tree_b.delete(it)
            emp = self.var_kardex_emp.get().strip() or "1.01"
            termo = var_b.get().strip()
            saldos = self.service.consultar_saldos_produtos(empcod=emp, termo_busca=termo) if self.service else []
            for p in saldos:
                tree_b.insert("", tk.END, iid=p.prodcod_estr, values=(p.prodcod_estr, p.prodnome, p.unidade, f"{p.saldo_atual:.2f}"))

        def selecionar():
            sel = tree_b.selection()
            if not sel:
                return "break"
            vals = tree_b.item(sel[0], "values")
            self.var_kardex_prod.set(vals[0])
            try:
                modal.destroy()
            except Exception:
                pass
            self.carregar_ficha_estoque()
            return "break"

        ent_b.bind("<Return>", lambda e: (recarregar(), "break")[1])
        tree_b.bind("<Double-1>", lambda e: (selecionar(), "break")[1])
        tree_b.bind("<Return>", lambda e: (selecionar(), "break")[1])
        modal.bind("<Escape>", lambda e: (modal.destroy(), "break")[1])

        btn_sel = tk.Button(f_cont, text="✔ Selecionar (Enter)", bg="#1D4ED8", fg="white", font=("Segoe UI", 9, "bold"), padx=10, pady=4, relief=tk.FLAT, command=selecionar)
        btn_sel.pack(side=tk.RIGHT, pady=(6, 0))

        recarregar()
        ent_b.focus_set()

    def _fechar_janela(self):
        toplevel = self.winfo_toplevel()
        if toplevel != self:
            toplevel.destroy()

    def _ao_mudar_aba(self, event=None):
        aba_idx = self.notebook.index(self.notebook.select())
        if aba_idx == 1 and not self.tree_saldos.get_children():
            self.carregar_saldos_produtos()
        elif aba_idx == 2 and not self.tree_reqs_cons.get_children():
            self.carregar_requisicoes_consulta()

    def _atualizar_aba_atual(self):
        aba_idx = self.notebook.index(self.notebook.select())
        if aba_idx == 0:
            self.carregar_ficha_estoque()
        elif aba_idx == 1:
            self.carregar_saldos_produtos()
        elif aba_idx == 2:
            self.carregar_requisicoes_consulta()

    # =========================================================================
    # 1. ABA FICHA DE ESTOQUE (KARDEX)
    # =========================================================================
    def _setup_tab_kardex(self):
        # Filtros Kardex
        f_box = ttk.LabelFrame(self.tab_kardex, text=" Parâmetros da Ficha de Estoque ", padding=8)
        f_box.pack(fill=tk.X, pady=(0, 6))

        f_row = ttk.Frame(f_box)
        f_row.pack(fill=tk.X)

        ttk.Label(f_row, text="Código do Produto: *", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.var_kardex_prod = tk.StringVar()
        vincular_maiusculo(self.var_kardex_prod)
        self.ent_kardex_prod = ttk.Entry(f_row, textvariable=self.var_kardex_prod, width=16)
        self.ent_kardex_prod.pack(side=tk.LEFT, padx=(0, 4))
        self.ent_kardex_prod.bind("<Return>", lambda e: self.carregar_ficha_estoque())

        btn_busca_kardex = ttk.Button(
            f_row,
            text="🔍 (F4)",
            width=6,
            command=self._abrir_modal_busca_kardex,
        )
        btn_busca_kardex.pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(f_row, text="De:").pack(side=tk.LEFT, padx=(0, 4))
        dt_ini_padrao = (datetime.now() - timedelta(days=90)).strftime("%d/%m/%Y")
        self.var_kardex_ini = tk.StringVar(value=dt_ini_padrao)
        self.ent_kardex_ini = ttk.Entry(f_row, textvariable=self.var_kardex_ini, width=12)
        self.ent_kardex_ini.pack(side=tk.LEFT, padx=(0, 8))
        vincular_mascara_data(self.ent_kardex_ini)

        ttk.Label(f_row, text="Até:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_kardex_fim = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.ent_kardex_fim = ttk.Entry(f_row, textvariable=self.var_kardex_fim, width=12)
        self.ent_kardex_fim.pack(side=tk.LEFT, padx=(0, 12))
        vincular_mascara_data(self.ent_kardex_fim)

        ttk.Label(f_row, text="Empresa:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_kardex_emp = tk.StringVar(value=obter_empresa_ativa())
        self.ent_kardex_emp = ttk.Entry(f_row, textvariable=self.var_kardex_emp, width=7)
        self.ent_kardex_emp.pack(side=tk.LEFT, padx=(0, 15))

        btn_cons = ttk.Button(f_row, text="🔍 Consultar Kardex (F5)", command=self.carregar_ficha_estoque)
        btn_cons.pack(side=tk.LEFT)

        # Cards com Totais / Indicadores
        f_cards = ttk.Frame(self.tab_kardex, padding=(0, 4))
        f_cards.pack(fill=tk.X, pady=(0, 6))

        # Card Entradas
        card_e = tk.Frame(f_cards, bg="#F0FDF4", highlightbackground="#86EFAC", highlightthickness=1, padx=12, pady=6)
        card_e.pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(card_e, text="Total Entradas", bg="#F0FDF4", fg="#15803D", font=("Segoe UI", 8)).pack(anchor=tk.W)
        self.lbl_card_tot_e = tk.Label(card_e, text="0.00", bg="#F0FDF4", fg="#15803D", font=("Segoe UI", 12, "bold"))
        self.lbl_card_tot_e.pack(anchor=tk.W)

        # Card Saídas
        card_s = tk.Frame(f_cards, bg="#FEF2F2", highlightbackground="#FCA5A5", highlightthickness=1, padx=12, pady=6)
        card_s.pack(side=tk.LEFT, padx=(0, 10))
        tk.Label(card_s, text="Total Saídas", bg="#FEF2F2", fg="#B91C1C", font=("Segoe UI", 8)).pack(anchor=tk.W)
        self.lbl_card_tot_s = tk.Label(card_s, text="0.00", bg="#FEF2F2", fg="#B91C1C", font=("Segoe UI", 12, "bold"))
        self.lbl_card_tot_s.pack(anchor=tk.W)

        # Card Saldo Atual
        card_saldo = tk.Frame(f_cards, bg="#F0F9FF", highlightbackground="#7DD3FC", highlightthickness=1, padx=14, pady=6)
        card_saldo.pack(side=tk.LEFT)
        tk.Label(card_saldo, text="Saldo Acumulado", bg="#F0F9FF", fg="#0369A1", font=("Segoe UI", 8)).pack(anchor=tk.W)
        self.lbl_card_saldo = tk.Label(card_saldo, text="0.00", bg="#F0F9FF", fg="#0369A1", font=("Segoe UI", 13, "bold"))
        self.lbl_card_saldo.pack(anchor=tk.W)

        # Grade do Extrato Kardex
        frame_kardex = ttk.LabelFrame(self.tab_kardex, text=" Extrato Cronológico de Movimentações ", padding=6)
        frame_kardex.pack(fill=tk.BOTH, expand=True)

        cols_k = ("data", "doc", "tipo", "origem", "entrada", "saida", "saldo", "obs")
        self.tree_kardex = ttk.Treeview(frame_kardex, columns=cols_k, show="headings", height=10, selectmode="browse")

        self.tree_kardex.heading("data", text="Data/Hora")
        self.tree_kardex.heading("doc", text="Documento / Lcto")
        self.tree_kardex.heading("tipo", text="Tipo")
        self.tree_kardex.heading("origem", text="Origem / Histórico")
        self.tree_kardex.heading("entrada", text="Entrada (+)")
        self.tree_kardex.heading("saida", text="Saída (-)")
        self.tree_kardex.heading("saldo", text="Saldo Acumulado")
        self.tree_kardex.heading("obs", text="Observações")

        self.tree_kardex.column("data", width=140, anchor=tk.CENTER)
        self.tree_kardex.column("doc", width=120, anchor=tk.CENTER)
        self.tree_kardex.column("tipo", width=50, anchor=tk.CENTER)
        self.tree_kardex.column("origem", width=150, anchor=tk.W)
        self.tree_kardex.column("entrada", width=100, anchor=tk.E)
        self.tree_kardex.column("saida", width=100, anchor=tk.E)
        self.tree_kardex.column("saldo", width=120, anchor=tk.E)
        self.tree_kardex.column("obs", width=250, anchor=tk.W)

        sb_k_y = ttk.Scrollbar(frame_kardex, orient=tk.VERTICAL, command=self.tree_kardex.yview)
        self.tree_kardex.configure(yscrollcommand=sb_k_y.set)
        self.tree_kardex.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_k_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_kardex.tag_configure("E", foreground="#15803D")
        self.tree_kardex.tag_configure("S", foreground="#B91C1C")

        configurar_navegacao_enter([self.ent_kardex_prod, self.ent_kardex_ini, self.ent_kardex_fim, self.ent_kardex_emp, btn_cons])

    def carregar_ficha_estoque(self):
        if not self.service:
            return

        for it in self.tree_kardex.get_children():
            self.tree_kardex.delete(it)

        prod = self.var_kardex_prod.get().strip()
        if not prod:
            messagebox.showinfo("Aviso", "Informe o código do produto para consultar a ficha.", parent=self)
            self.ent_kardex_prod.focus_set()
            return

        empcod = self.var_kardex_emp.get().strip() or "1.01"
        dt_ini = self.var_kardex_ini.get().strip()
        dt_fim = self.var_kardex_fim.get().strip()

        extrato = self.service.consultar_ficha_estoque(
            prodcod_estr=prod,
            empcod=empcod,
            data_ini=dt_ini,
            data_fim=dt_fim,
        )

        tot_e = sum(lin.qtd_entrada for lin in extrato)
        tot_s = sum(lin.qtd_saida for lin in extrato)
        saldo_final = extrato[-1].saldo_acumulado if extrato else 0.0

        self.lbl_card_tot_e.config(text=f"{tot_e:.2f}")
        self.lbl_card_tot_s.config(text=f"{tot_s:.2f}")
        self.lbl_card_saldo.config(text=f"{saldo_final:.2f}")

        for i, lin in enumerate(extrato):
            tag = "E" if lin.tipo_mov == "E" else "S"
            e_str = f"{lin.qtd_entrada:.2f}" if lin.qtd_entrada > 0 else "-"
            s_str = f"{lin.qtd_saida:.2f}" if lin.qtd_saida > 0 else "-"
            self.tree_kardex.insert(
                "",
                tk.END,
                iid=str(i),
                values=(
                    formatar_data_br(lin.data, incluir_hora=True),
                    lin.doc_num,
                    lin.tipo_mov,
                    lin.origem,
                    e_str,
                    s_str,
                    f"{lin.saldo_acumulado:.2f}",
                    lin.observacao,
                ),
                tags=(tag,),
            )

    # =========================================================================
    # 2. ABA SALDO DE PRODUTOS
    # =========================================================================
    def _setup_tab_saldos(self):
        f_box = ttk.LabelFrame(self.tab_saldos, text=" Filtro de Produtos ", padding=8)
        f_box.pack(fill=tk.X, pady=(0, 6))

        f_row = ttk.Frame(f_box)
        f_row.pack(fill=tk.X)

        ttk.Label(f_row, text="Buscar Produto:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_saldo_busca = tk.StringVar()
        vincular_maiusculo(self.var_saldo_busca)
        self.ent_saldo_busca = ttk.Entry(f_row, textvariable=self.var_saldo_busca, width=30)
        self.ent_saldo_busca.pack(side=tk.LEFT, padx=(0, 15))
        self.ent_saldo_busca.bind("<Return>", lambda e: self.carregar_saldos_produtos())

        ttk.Label(f_row, text="Empresa:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_saldo_emp = tk.StringVar(value=obter_empresa_ativa())
        self.ent_saldo_emp = ttk.Entry(f_row, textvariable=self.var_saldo_emp, width=8)
        self.ent_saldo_emp.pack(side=tk.LEFT, padx=(0, 15))

        btn_filtrar = ttk.Button(f_row, text="🔍 Buscar (F5)", command=self.carregar_saldos_produtos)
        btn_filtrar.pack(side=tk.LEFT, padx=(0, 8))

        btn_ver_k = ttk.Button(f_row, text="📊 Ver Kardex do Selecionado", command=self._ver_kardex_do_saldo)
        btn_ver_k.pack(side=tk.LEFT)

        # Grade de Saldos
        frame_saldos = ttk.LabelFrame(self.tab_saldos, text=" Posição de Estoque Físico e Disponível ", padding=6)
        frame_saldos.pack(fill=tk.BOTH, expand=True)

        cols_s = ("prodcod", "prodnome", "unid", "saldo_atual", "qtd_reservada", "saldo_disp")
        self.tree_saldos = ttk.Treeview(frame_saldos, columns=cols_s, show="headings", height=12, selectmode="browse")

        self.tree_saldos.heading("prodcod", text="Código")
        self.tree_saldos.heading("prodnome", text="Descrição do Produto")
        self.tree_saldos.heading("unid", text="Unid")
        self.tree_saldos.heading("saldo_atual", text="Saldo Físico/Atual")
        self.tree_saldos.heading("qtd_reservada", text="Reservado")
        self.tree_saldos.heading("saldo_disp", text="Saldo Disponível")

        self.tree_saldos.column("prodcod", width=140, anchor=tk.W)
        self.tree_saldos.column("prodnome", width=340, anchor=tk.W)
        self.tree_saldos.column("unid", width=70, anchor=tk.CENTER)
        self.tree_saldos.column("saldo_atual", width=130, anchor=tk.E)
        self.tree_saldos.column("qtd_reservada", width=120, anchor=tk.E)
        self.tree_saldos.column("saldo_disp", width=130, anchor=tk.E)

        sb_s_y = ttk.Scrollbar(frame_saldos, orient=tk.VERTICAL, command=self.tree_saldos.yview)
        self.tree_saldos.configure(yscrollcommand=sb_s_y.set)
        self.tree_saldos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_s_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_saldos.bind("<Double-1>", lambda e: self._ver_kardex_do_saldo())

        self.tree_saldos.tag_configure("disponivel", foreground="#15803D")
        self.tree_saldos.tag_configure("zerado", foreground="#B91C1C")

        configurar_navegacao_enter([self.ent_saldo_busca, self.ent_saldo_emp, btn_filtrar])

    def carregar_saldos_produtos(self):
        if not self.service:
            return

        for it in self.tree_saldos.get_children():
            self.tree_saldos.delete(it)

        empcod = self.var_saldo_emp.get().strip() or "1.01"
        busca = self.var_saldo_busca.get().strip()

        saldos = self.service.consultar_saldos_produtos(empcod=empcod, termo_busca=busca)
        for s in saldos:
            tag = "disponivel" if s.saldo_disponivel > 0.0001 else "zerado"
            self.tree_saldos.insert(
                "",
                tk.END,
                iid=s.prodcod_estr,
                values=(
                    s.prodcod_estr,
                    s.prodnome,
                    s.unidade,
                    f"{s.saldo_atual:.2f}",
                    f"{s.quantidade_reservada:.2f}",
                    f"{s.saldo_disp_str if hasattr(s, 'saldo_disp_str') else s.saldo_disponivel:.2f}",
                ),
                tags=(tag,),
            )

    def _ver_kardex_do_saldo(self):
        sel = self.tree_saldos.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um produto da lista de saldos.", parent=self)
            return

        prodcod = sel[0]
        self.var_kardex_prod.set(prodcod)
        self.notebook.select(0)
        self.carregar_ficha_estoque()

    # =========================================================================
    # 3. ABA REQUISIÇÕES DE MATERIAIS
    # =========================================================================
    def _setup_tab_reqs(self):
        f_box = ttk.LabelFrame(self.tab_reqs, text=" Filtros de Requisições ", padding=8)
        f_box.pack(fill=tk.X, pady=(0, 6))

        f_row = ttk.Frame(f_box)
        f_row.pack(fill=tk.X)

        ttk.Label(f_row, text="Status:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_req_status = tk.StringVar(value="TODOS")
        self.cb_req_status = ttk.Combobox(
            f_row,
            textvariable=self.var_req_status,
            values=["TODOS", "ABERTA", "ATENDIDA PARCIAL", "ATENDIDA TOTAL", "CANCELADA"],
            state="readonly",
            width=18,
        )
        self.cb_req_status.pack(side=tk.LEFT, padx=(0, 15))
        self.cb_req_status.bind("<<ComboboxSelected>>", lambda e: self.carregar_requisicoes_consulta())

        ttk.Label(f_row, text="Buscar:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_req_busca = tk.StringVar()
        vincular_maiusculo(self.var_req_busca)
        self.ent_req_busca = ttk.Entry(f_row, textvariable=self.var_req_busca, width=25)
        self.ent_req_busca.pack(side=tk.LEFT, padx=(0, 15))
        self.ent_req_busca.bind("<Return>", lambda e: self.carregar_requisicoes_consulta())

        ttk.Label(f_row, text="Empresa:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_req_emp = tk.StringVar(value=obter_empresa_ativa())
        self.ent_req_emp = ttk.Entry(f_row, textvariable=self.var_req_emp, width=8)
        self.ent_req_emp.pack(side=tk.LEFT, padx=(0, 15))

        btn_filtrar = ttk.Button(f_row, text="🔍 Buscar (F5)", command=self.carregar_requisicoes_consulta)
        btn_filtrar.pack(side=tk.LEFT)

        # PanedWindow para Mestre (Requisições) e Detalhe (Itens)
        paned = ttk.PanedWindow(self.tab_reqs, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=6)

        frame_r = ttk.LabelFrame(paned, text=" Requisições ", padding=6)
        paned.add(frame_r, weight=3)

        cols_r = ("num", "data", "requerente", "centro_custo", "status", "tot_sol", "tot_atend", "tot_pend")
        self.tree_reqs_cons = ttk.Treeview(frame_r, columns=cols_r, show="headings", height=6, selectmode="browse")

        self.tree_reqs_cons.heading("num", text="Nº Requisição")
        self.tree_reqs_cons.heading("data", text="Data")
        self.tree_reqs_cons.heading("requerente", text="Requerente")
        self.tree_reqs_cons.heading("centro_custo", text="Centro Custo")
        self.tree_reqs_cons.heading("status", text="Status")
        self.tree_reqs_cons.heading("tot_sol", text="Qtd Solicitada")
        self.tree_reqs_cons.heading("tot_atend", text="Qtd Atendida")
        self.tree_reqs_cons.heading("tot_pend", text="Saldo Pendente")

        self.tree_reqs_cons.column("num", width=120, anchor=tk.CENTER)
        self.tree_reqs_cons.column("data", width=100, anchor=tk.CENTER)
        self.tree_reqs_cons.column("requerente", width=220, anchor=tk.W)
        self.tree_reqs_cons.column("centro_custo", width=120, anchor=tk.W)
        self.tree_reqs_cons.column("status", width=130, anchor=tk.CENTER)
        self.tree_reqs_cons.column("tot_sol", width=100, anchor=tk.E)
        self.tree_reqs_cons.column("tot_atend", width=100, anchor=tk.E)
        self.tree_reqs_cons.column("tot_pend", width=100, anchor=tk.E)

        sb_r_y = ttk.Scrollbar(frame_r, orient=tk.VERTICAL, command=self.tree_reqs_cons.yview)
        self.tree_reqs_cons.configure(yscrollcommand=sb_r_y.set)
        self.tree_reqs_cons.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_r_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_reqs_cons.bind("<<TreeviewSelect>>", self._ao_selecionar_req_cons)

        self.tree_reqs_cons.tag_configure("Aberta", foreground="#0369A1", background="#F0F9FF")
        self.tree_reqs_cons.tag_configure("Atendida Parcial", foreground="#B45309", background="#FFFBEB")
        self.tree_reqs_cons.tag_configure("Atendida Total", foreground="#15803D", background="#F0FDF4")
        self.tree_reqs_cons.tag_configure("Cancelada", foreground="#B91C1C", background="#FEF2F2")

        # Detalhe Itens
        frame_it = ttk.LabelFrame(paned, text=" Itens da Requisição ", padding=6)
        paned.add(frame_it, weight=3)

        cols_it = ("seq", "prodcod", "prodnome", "unid", "qtd_sol", "qtd_atend", "saldo", "status")
        self.tree_it_cons = ttk.Treeview(frame_it, columns=cols_it, show="headings", height=5, selectmode="browse")

        self.tree_it_cons.heading("seq", text="Item")
        self.tree_it_cons.heading("prodcod", text="Código")
        self.tree_it_cons.heading("prodnome", text="Descrição do Produto")
        self.tree_it_cons.heading("unid", text="Unid")
        self.tree_it_cons.heading("qtd_sol", text="Qtd Solicitada")
        self.tree_it_cons.heading("qtd_atend", text="Qtd Atendida")
        self.tree_it_cons.heading("saldo", text="Saldo Pendente")
        self.tree_it_cons.heading("status", text="Status Item")

        self.tree_it_cons.column("seq", width=50, anchor=tk.CENTER)
        self.tree_it_cons.column("prodcod", width=120, anchor=tk.W)
        self.tree_it_cons.column("prodnome", width=280, anchor=tk.W)
        self.tree_it_cons.column("unid", width=60, anchor=tk.CENTER)
        self.tree_it_cons.column("qtd_sol", width=110, anchor=tk.E)
        self.tree_it_cons.column("qtd_atend", width=110, anchor=tk.E)
        self.tree_it_cons.column("saldo", width=110, anchor=tk.E)
        self.tree_it_cons.column("status", width=120, anchor=tk.CENTER)

        sb_it_y = ttk.Scrollbar(frame_it, orient=tk.VERTICAL, command=self.tree_it_cons.yview)
        self.tree_it_cons.configure(yscrollcommand=sb_it_y.set)
        self.tree_it_cons.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_it_y.pack(side=tk.RIGHT, fill=tk.Y)

        configurar_navegacao_enter([self.cb_req_status, self.ent_req_busca, self.ent_req_emp, btn_filtrar])

    def carregar_requisicoes_consulta(self):
        if not self.service:
            return

        for it in self.tree_reqs_cons.get_children():
            self.tree_reqs_cons.delete(it)
        for it in self.tree_it_cons.get_children():
            self.tree_it_cons.delete(it)

        empcod = self.var_req_emp.get().strip() or "1.01"
        status_f = self.var_req_status.get().strip()
        busca = self.var_req_busca.get().strip()

        requisicoes = self.service.listar_requisicoes(
            empcod=empcod,
            status_filtro=status_f,
            termo_busca=busca,
        )

        for r in requisicoes:
            det = self.service.obter_requisicao(r.req_num, empcod=empcod)
            tot_sol = det.total_solicitado if det else 0.0
            tot_atend = det.total_atendido if det else 0.0
            tot_pend = det.total_pendente if det else 0.0

            tag = r.status if r.status in ("Aberta", "Atendida Parcial", "Atendida Total", "Cancelada") else "Aberta"
            self.tree_reqs_cons.insert(
                "",
                tk.END,
                iid=r.req_num,
                values=(
                    r.req_num,
                    formatar_data_br(r.data_req),
                    r.requerente,
                    r.centro_custo,
                    r.status,
                    f"{tot_sol:.2f}",
                    f"{tot_atend:.2f}",
                    f"{tot_pend:.2f}",
                ),
                tags=(tag,),
            )

    def _ao_selecionar_req_cons(self, event=None):
        sel = self.tree_reqs_cons.selection()
        if not sel:
            return

        req_num = sel[0]
        empcod = self.var_req_emp.get().strip() or "1.01"
        req = self.service.obter_requisicao(req_num, empcod=empcod)

        for it in self.tree_it_cons.get_children():
            self.tree_it_cons.delete(it)

        if not req:
            return

        for item in req.itens:
            self.tree_it_cons.insert(
                "",
                tk.END,
                iid=f"{item.req_num}_{item.item_seq}",
                values=(
                    item.item_seq,
                    item.prodcod_estr,
                    item.prodnome,
                    item.unidade,
                    f"{item.qtd_solicitada:.2f}",
                    f"{item.qtd_atendida:.2f}",
                    f"{item.saldo_pendente:.2f}",
                    item.status_item,
                ),
            )


def abrir_consulta_ficha_estoque(parent=None, connection=None, prodcod_inicial: str = ""):
    win = tk.Toplevel(parent)
    win.title("Consulta Ficha de Estoque (Kardex) - GeoAlvo")
    win.minsize(1050, 580)
    centralizar_janela(win, parent, 1150, 660)
    view = ConsultasEstoqueView(win, aba_inicial=0, prodcod_inicial=prodcod_inicial)
    view.pack(fill=tk.BOTH, expand=True)
    return win


def abrir_consulta_saldo_produto(parent=None, connection=None):
    win = tk.Toplevel(parent)
    win.title("Consulta Saldo de Produtos - GeoAlvo")
    win.minsize(1050, 580)
    centralizar_janela(win, parent, 1150, 660)
    view = ConsultasEstoqueView(win, aba_inicial=1)
    view.pack(fill=tk.BOTH, expand=True)
    return win


def abrir_consulta_requisicoes(parent=None, connection=None):
    win = tk.Toplevel(parent)
    win.title("Consulta Requisições de Materiais - GeoAlvo")
    win.minsize(1050, 580)
    centralizar_janela(win, parent, 1150, 660)
    view = ConsultasEstoqueView(win, aba_inicial=2)
    view.pack(fill=tk.BOTH, expand=True)
    return win
