"""
Interface Gráfica para Cadastro e Controle de Lotes de Produtos.
GeoApolo V5
Integração com catálogo de produtos e tela de movimentação de estoque.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Callable
from datetime import datetime

from core import (
    centralizar_janela,
    vincular_maiusculo,
    configurar_navegacao_enter,
    vincular_mascara_data,
    formatar_data_br,
    converter_data_br_para_iso,
    validar_data_br,
)
from .models import ProdutoLoteDTO, ResultadoLoteDTO
from .service import LotesService


class LotesView(ttk.Frame):
    """Tela de Cadastro e Controle de Lotes de Produtos."""

    def __init__(
        self,
        parent=None,
        service: Optional[LotesService] = None,
        connection=None,
        prodcod_inicial: Optional[int] = None,
        numero_lote_inicial: str = "",
        ao_salvar_callback: Optional[Callable[[str], None]] = None,
    ):
        super().__init__(parent)
        self.service = service
        self.ao_salvar_callback = ao_salvar_callback
        self._prodcod_inicial = prodcod_inicial
        self._numero_lote_inicial = numero_lote_inicial

        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from .repository import LotesRepository
                conn = connection or obter_conexao_banco()
                self.service = LotesService(LotesRepository(conn))
            except Exception:
                pass

        self._id_lote_edicao = 0
        self._setup_ui()
        self._configurar_atalhos()

        if self.service:
            self.carregar_lotes()

        # Se veio pré-preenchido (chamado da movimentação)
        if self._prodcod_inicial or self._numero_lote_inicial:
            self._preencher_dados_iniciais()

    def _setup_ui(self):
        # Header Superior
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        lbl_titulo = ttk.Label(
            header,
            text="Cadastro e Controle de Lotes de Produtos",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
        )
        lbl_titulo.pack(side=tk.LEFT)

        self.lbl_contador = ttk.Label(
            header,
            text="0 lote(s)",
            font=("Segoe UI", 9, "bold"),
            foreground="#475569",
        )
        self.lbl_contador.pack(side=tk.RIGHT, padx=5)

        # Barra de Pesquisa e Filtros
        bar_filtro = ttk.Frame(self, padding=(10, 4))
        bar_filtro.pack(fill=tk.X)

        ttk.Label(bar_filtro, text="Buscar:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.var_busca = tk.StringVar()
        vincular_maiusculo(self.var_busca)
        self.ent_busca = ttk.Entry(bar_filtro, textvariable=self.var_busca, width=24)
        self.ent_busca.pack(side=tk.LEFT, padx=(0, 6))
        self.ent_busca.bind("<Return>", lambda e: self.carregar_lotes())

        ttk.Label(bar_filtro, text="Status:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(8, 4))
        self.var_filtro_status = tk.StringVar(value="TODOS")
        cb_status = ttk.Combobox(bar_filtro, textvariable=self.var_filtro_status, values=["TODOS", "ATIVOS", "INATIVOS"], width=10, state="readonly")
        cb_status.pack(side=tk.LEFT, padx=(0, 8))
        cb_status.bind("<<ComboboxSelected>>", lambda e: self.carregar_lotes())

        ttk.Button(bar_filtro, text="🔍 Filtrar (F5)", command=self.carregar_lotes).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar_filtro, text="🔄 Todos", command=self._limpar_filtros).pack(side=tk.LEFT, padx=3)

        if self.ao_salvar_callback:
            btn_sel = tk.Button(
                bar_filtro,
                text="✔ Selecionar Lote (F3)",
                bg="#1D4ED8",
                fg="white",
                font=("Segoe UI", 9, "bold"),
                padx=10,
                pady=2,
                relief=tk.FLAT,
                command=self._confirmar_selecao_e_fechar,
            )
            btn_sel.pack(side=tk.RIGHT, padx=4)

        # Painel Dividido (Grade à esquerda, Formulário à direita)
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Painel Esquerdo: Grade de Lotes
        frame_grid = ttk.Frame(paned, padding=5)
        paned.add(frame_grid, weight=3)

        cols = ("id", "prodcod", "prodnome", "lote", "validade", "qtd_ini", "qtd_atu", "status", "forn")
        self.tree = ttk.Treeview(frame_grid, columns=cols, show="headings", height=16, selectmode="browse")
        self.tree.heading("id", text="ID")
        self.tree.heading("prodcod", text="Cód.")
        self.tree.heading("prodnome", text="Descrição do Produto")
        self.tree.heading("lote", text="Nº do Lote")
        self.tree.heading("validade", text="Validade")
        self.tree.heading("qtd_ini", text="Qtd. Inicial")
        self.tree.heading("qtd_atu", text="Saldo Atual")
        self.tree.heading("status", text="Status")
        self.tree.heading("forn", text="Fornecedor")

        self.tree.column("id", width=45, anchor=tk.CENTER)
        self.tree.column("prodcod", width=55, anchor=tk.CENTER)
        self.tree.column("prodnome", width=200, anchor=tk.W)
        self.tree.column("lote", width=120, anchor=tk.W)
        self.tree.column("validade", width=85, anchor=tk.CENTER)
        self.tree.column("qtd_ini", width=80, anchor=tk.E)
        self.tree.column("qtd_atu", width=85, anchor=tk.E)
        self.tree.column("status", width=65, anchor=tk.CENTER)
        self.tree.column("forn", width=140, anchor=tk.W)

        scroll_y = ttk.Scrollbar(frame_grid, orient=tk.VERTICAL, command=self.tree.yview)
        scroll_x = ttk.Scrollbar(frame_grid, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.bind("<<TreeviewSelect>>", self._ao_selecionar_lote)
        self.tree.bind("<Double-1>", self._ao_duplo_clique_grade)


        # Painel Direito: Formulário de Lotes
        frame_form = ttk.LabelFrame(paned, text=" Dados do Lote ", padding=12)
        paned.add(frame_form, weight=2)

        # 1. Produto com Busca F4
        ttk.Label(frame_form, text="Produto: *", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        f_prod = ttk.Frame(frame_form)
        f_prod.pack(fill=tk.X, pady=(0, 2))

        self.var_prodcod = tk.StringVar()
        self.ent_prodcod = ttk.Entry(f_prod, textvariable=self.var_prodcod, width=12, font=("Segoe UI", 9, "bold"))
        self.ent_prodcod.pack(side=tk.LEFT, padx=(0, 6))

        btn_busca_prod = ttk.Button(f_prod, text="🔍 Buscar (F4)", command=self._abrir_busca_produto)
        btn_busca_prod.pack(side=tk.LEFT)

        self.lbl_prod_nome = ttk.Label(
            frame_form,
            text="Informe o código ou clique em Buscar (F4)",
            font=("Segoe UI", 8, "italic"),
            foreground="#475569",
        )
        self.lbl_prod_nome.pack(anchor=tk.W, pady=(0, 8))

        self.ent_prodcod.bind("<FocusOut>", lambda e: self._ao_sair_prodcod())
        self.ent_prodcod.bind("<Return>", lambda e: self._ao_sair_prodcod())

        # 2. Número do Lote
        ttk.Label(frame_form, text="Número do Lote: *", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_numero_lote = tk.StringVar()
        vincular_maiusculo(self.var_numero_lote)
        self.ent_numero_lote = ttk.Entry(frame_form, textvariable=self.var_numero_lote, width=28, font=("Segoe UI", 9, "bold"))
        self.ent_numero_lote.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))

        # 3. Datas (Fabricação e Validade)
        f_datas = ttk.Frame(frame_form)
        f_datas.pack(fill=tk.X, pady=(0, 8))

        f_fab = ttk.Frame(f_datas)
        f_fab.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Label(f_fab, text="Data Fabricação:", font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(0, 2))
        self.var_dt_fab = tk.StringVar()
        self.ent_dt_fab = ttk.Entry(f_fab, textvariable=self.var_dt_fab, width=12)
        self.ent_dt_fab.pack(fill=tk.X)
        vincular_mascara_data(self.ent_dt_fab)

        f_val = ttk.Frame(f_datas)
        f_val.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
        ttk.Label(f_val, text="Data Validade:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_dt_val = tk.StringVar()
        self.ent_dt_val = ttk.Entry(f_val, textvariable=self.var_dt_val, width=12)
        self.ent_dt_val.pack(fill=tk.X)
        vincular_mascara_data(self.ent_dt_val)

        # 4. Quantidades (Inicial e Atual)
        f_qtds = ttk.Frame(frame_form)
        f_qtds.pack(fill=tk.X, pady=(0, 8))

        f_qini = ttk.Frame(f_qtds)
        f_qini.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Label(f_qini, text="Qtd. Inicial: *", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_qtd_ini = tk.StringVar(value="0,00")
        self.ent_qtd_ini = ttk.Entry(f_qini, textvariable=self.var_qtd_ini, width=12)
        self.ent_qtd_ini.pack(fill=tk.X)

        f_qatu = ttk.Frame(f_qtds)
        f_qatu.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
        ttk.Label(f_qatu, text="Saldo Atual: *", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_qtd_atu = tk.StringVar(value="0,00")
        self.ent_qtd_atu = ttk.Entry(f_qatu, textvariable=self.var_qtd_atu, width=12)
        self.ent_qtd_atu.pack(fill=tk.X)

        # 5. Fornecedor com Busca F4
        ttk.Label(frame_form, text="Fornecedor:", font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(0, 2))
        f_forn = ttk.Frame(frame_form)
        f_forn.pack(fill=tk.X, pady=(0, 2))

        self.var_forncod = tk.StringVar()
        self.ent_forncod = ttk.Entry(f_forn, textvariable=self.var_forncod, width=12)
        self.ent_forncod.pack(side=tk.LEFT, padx=(0, 6))

        btn_busca_forn = ttk.Button(f_forn, text="🔍 Buscar (F4)", command=self._abrir_busca_fornecedor)
        btn_busca_forn.pack(side=tk.LEFT)

        self.lbl_forn_nome = ttk.Label(
            frame_form,
            text="Informe o código do fornecedor ou F4",
            font=("Segoe UI", 8, "italic"),
            foreground="#475569",
        )
        self.lbl_forn_nome.pack(anchor=tk.W, pady=(0, 8))

        self.ent_forncod.bind("<FocusOut>", lambda e: self._ao_sair_forncod())
        self.ent_forncod.bind("<Return>", lambda e: self._ao_sair_forncod())

        # 6. Status
        ttk.Label(frame_form, text="Status do Lote:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_status = tk.StringVar(value="A")
        f_st = ttk.Frame(frame_form)
        f_st.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))
        ttk.Radiobutton(f_st, text="Ativo (Permite movimentações)", variable=self.var_status, value="A").pack(anchor=tk.W)
        ttk.Radiobutton(f_st, text="Inativo (Bloqueado)", variable=self.var_status, value="I").pack(anchor=tk.W)

        # 7. Observações
        ttk.Label(frame_form, text="Observações:", font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(0, 2))
        self.var_obs = tk.StringVar()
        vincular_maiusculo(self.var_obs)
        self.ent_obs = ttk.Entry(frame_form, textvariable=self.var_obs, width=32)
        self.ent_obs.pack(anchor=tk.W, fill=tk.X, pady=(0, 15))

        # Barra de Botões
        bar_btns = ttk.Frame(frame_form)
        bar_btns.pack(fill=tk.X, pady=(5, 0))

        btn_novo = tk.Button(
            bar_btns,
            text="➕ Novo",
            bg="#2563EB",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            relief=tk.FLAT,
            command=self._novo_registro,
        )
        btn_novo.pack(side=tk.LEFT, padx=2)

        btn_salvar = tk.Button(
            bar_btns,
            text="✔ Salvar (F10)",
            bg="#16A34A",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            relief=tk.FLAT,
            command=self._salvar_lote,
        )
        btn_salvar.pack(side=tk.LEFT, padx=2)

        btn_excluir = tk.Button(
            bar_btns,
            text="🗑 Excluir",
            bg="#DC2626",
            fg="white",
            font=("Segoe UI", 9),
            padx=8,
            pady=4,
            relief=tk.FLAT,
            command=self._excluir_lote,
        )
        btn_excluir.pack(side=tk.LEFT, padx=2)

        ttk.Button(bar_btns, text="Limpar", command=self._limpar_campos).pack(side=tk.RIGHT, padx=2)

    def _configurar_atalhos(self):
        self.bind_all("<F5>", lambda e: self.carregar_lotes())
        self.bind_all("<F10>", lambda e: self._salvar_lote())
        self.bind_all("<F3>", lambda e: self._confirmar_selecao_e_fechar(e))
        configurar_navegacao_enter([
            self.ent_prodcod,
            self.ent_numero_lote,
            self.ent_dt_fab,
            self.ent_dt_val,
            self.ent_qtd_ini,
            self.ent_qtd_atu,
            self.ent_forncod,
            self.ent_obs,
        ])

    def _ao_duplo_clique_grade(self, event=None):
        """No duplo clique na grade de lotes, se houver callback, seleciona e fecha."""
        if self.ao_salvar_callback:
            self._confirmar_selecao_e_fechar(event)

    def _confirmar_selecao_e_fechar(self, event=None):
        """Seleciona o lote da linha clicada/selecionada e retorna para o formulário chamador."""
        num_lote = ""
        sel = self.tree.selection()
        if sel:
            vals = self.tree.item(sel[0], "values")
            # cols = ("id", "prodcod", "prodnome", "lote", "validade", "qtd_ini", "qtd_atu", "status", "forn")
            if len(vals) >= 4:
                num_lote = str(vals[3]).strip()
        if not num_lote:
            num_lote = self.var_numero_lote.get().strip()

        if not num_lote:
            messagebox.showwarning("Aviso", "Selecione um lote na lista primeiro.", parent=self)
            return

        if self.ao_salvar_callback:
            try:
                self.ao_salvar_callback(num_lote)
            except Exception:
                pass
            parent_win = self.winfo_toplevel()
            if isinstance(parent_win, tk.Toplevel):
                parent_win.destroy()
        else:
            messagebox.showinfo("Lote Selecionado", f"Lote: {num_lote}", parent=self)


    def _preencher_dados_iniciais(self):
        """Preenche dados pré-configurados passados por outra tela."""
        if self._prodcod_inicial:
            self.var_prodcod.set(str(self._prodcod_inicial))
            self._ao_sair_prodcod()
        if self._numero_lote_inicial:
            self.var_numero_lote.set(str(self._numero_lote_inicial).strip().upper())
            self.ent_dt_val.focus_set()
        else:
            self.ent_numero_lote.focus_set()

    def carregar_lotes(self):
        """Carrega a grade com lotes filtrados."""
        if not self.service:
            return

        termo = self.var_busca.get().strip()
        filtro_st = self.var_filtro_status.get()
        apenas_atv = filtro_st == "ATIVOS"

        lotes = self.service.listar_lotes(termo=termo, apenas_ativos=apenas_atv)
        if filtro_st == "INATIVOS":
            lotes = [l for l in lotes if l.status == "I"]

        for item in self.tree.get_children():
            self.tree.delete(item)

        for l in lotes:
            dt_val_br = formatar_data_br(l.data_validade) if l.data_validade else "-"
            self.tree.insert("", tk.END, iid=str(l.id_produto_lote), values=(
                l.id_produto_lote,
                l.prodcod,
                l.prodnome,
                l.numero_lote,
                dt_val_br,
                f"{l.quantidade_inicial:.2f}",
                f"{l.quantidade_atual:.2f}",
                l.display_status,
                l.nome_fornecedor or (str(l.entcod_fornecedor) if l.entcod_fornecedor else "-"),
            ))

        total = len(lotes)
        self.lbl_contador.config(text=f"{total} lote(s) encontrado(s)")

    def _ao_selecionar_lote(self, event=None):
        """Carrega os dados do lote selecionado na grade para os campos do formulário."""
        sel = self.tree.selection()
        if not sel:
            return
        id_lote = int(self.tree.item(sel[0])["values"][0])
        if not self.service:
            return
        lote = self.service.obter_lote(id_lote)
        if lote:
            self._id_lote_edicao = lote.id_produto_lote
            self.var_prodcod.set(str(lote.prodcod))
            self.lbl_prod_nome.config(text=f"{lote.prodnome}")
            self.var_numero_lote.set(lote.numero_lote)
            self.var_dt_fab.set(formatar_data_br(lote.data_fabricacao) if lote.data_fabricacao else "")
            self.var_dt_val.set(formatar_data_br(lote.data_validade) if lote.data_validade else "")
            self.var_qtd_ini.set(f"{lote.quantidade_inicial:.2f}")
            self.var_qtd_atu.set(f"{lote.quantidade_atual:.2f}")
            self.var_forncod.set(str(lote.entcod_fornecedor) if lote.entcod_fornecedor else "")
            self.lbl_forn_nome.config(text=lote.nome_fornecedor or "")
            self.var_status.set(lote.status)
            self.var_obs.set(lote.observacao)

    def _limpar_campos(self):
        """Limpa todos os campos do formulário."""
        self._id_lote_edicao = 0
        self.var_prodcod.set("")
        self.lbl_prod_nome.config(text="Informe o código ou clique em Buscar (F4)")
        self.var_numero_lote.set("")
        self.var_dt_fab.set("")
        self.var_dt_val.set("")
        self.var_qtd_ini.set("0,00")
        self.var_qtd_atu.set("0,00")
        self.var_forncod.set("")
        self.lbl_forn_nome.config(text="Informe o código do fornecedor ou F4")
        self.var_status.set("A")
        self.var_obs.set("")
        self.ent_prodcod.focus_set()

    def _novo_registro(self):
        self._limpar_campos()

    def _limpar_filtros(self):
        self.var_busca.set("")
        self.var_filtro_status.set("TODOS")
        self.carregar_lotes()
        self._limpar_campos()

    def _ao_sair_prodcod(self):
        cod_raw = self.var_prodcod.get().strip()
        if not cod_raw:
            return
        try:
            prod_int = int(cod_raw)
        except ValueError:
            return
        if self.service and self.service._repo.conn:
            try:
                cur = self.service._repo.conn.cursor()
                nolock = self.service._repo._nolock()
                cur.execute(f"SELECT prodnome FROM USER_geoapolo_produtos {nolock} WHERE prodcod = ?", [prod_int])
                r = cur.fetchone()
                if r:
                    self.lbl_prod_nome.config(text=f"{r[0]}")
                else:
                    self.lbl_prod_nome.config(text="Produto não cadastrado no sistema")
            except Exception:
                pass

    def _ao_sair_forncod(self):
        cod_raw = self.var_forncod.get().strip()
        if not cod_raw:
            self.lbl_forn_nome.config(text="")
            return
        try:
            forn_int = int(cod_raw)
        except ValueError:
            return
        if self.service and self.service._repo.conn:
            try:
                cur = self.service._repo.conn.cursor()
                nolock = self.service._repo._nolock()
                nome_forn = None
                try:
                    cur.execute(f"SELECT geoentnome FROM USER_geoapolo_entidade {nolock} WHERE geoentcod = ?", [str(forn_int)])
                    r = cur.fetchone()
                    if r and r[0]:
                        nome_forn = str(r[0]).strip()
                except Exception:
                    pass
                if not nome_forn:
                    try:
                        cur.execute(f"SELECT entnome FROM ENTIDADE {nolock} WHERE entcod = ?", [forn_int])
                        r = cur.fetchone()
                        if r and r[0]:
                            nome_forn = str(r[0]).strip()
                    except Exception:
                        pass

                if nome_forn:
                    self.lbl_forn_nome.config(text=nome_forn)
                else:
                    self.lbl_forn_nome.config(text="Fornecedor não encontrado")
            except Exception:
                pass

    def _abrir_busca_produto(self):
        """Abre modal F4 para seleção de produtos."""
        modal = tk.Toplevel(self)
        modal.title("Pesquisa de Produtos")
        modal.transient(self)
        modal.grab_set()
        centralizar_janela(modal, self, 640, 420)

        f_cont = ttk.Frame(modal, padding=10)
        f_cont.pack(fill=tk.BOTH, expand=True)

        f_b = ttk.Frame(f_cont)
        f_b.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(f_b, text="Buscar:").pack(side=tk.LEFT)
        var_b = tk.StringVar()
        vincular_maiusculo(var_b)
        ent_b = ttk.Entry(f_b, textvariable=var_b, width=30)
        ent_b.pack(side=tk.LEFT, padx=6)

        cols_p = ("cod", "nome")
        tree_p = ttk.Treeview(f_cont, columns=cols_p, show="headings", height=12)
        tree_p.heading("cod", text="Código")
        tree_p.heading("nome", text="Descrição do Produto")
        tree_p.column("cod", width=90, anchor=tk.CENTER)
        tree_p.column("nome", width=450, anchor=tk.W)
        tree_p.pack(fill=tk.BOTH, expand=True)

        def recarregar():
            tree_p.delete(*tree_p.get_children())
            t = f"%{var_b.get().strip().upper()}%"
            try:
                cur = self.service._repo.conn.cursor()
                nolock = self.service._repo._nolock()
                cur.execute(
                    f"SELECT prodcod, prodnome FROM USER_geoapolo_produtos {nolock} WHERE UPPER(prodnome) LIKE ? OR CAST(prodcod AS VARCHAR) LIKE ? ORDER BY prodnome ASC",
                    [t, t]
                )
                for r in cur.fetchall()[:100]:
                    tree_p.insert("", tk.END, values=(r[0], r[1]))
            except Exception:
                pass

        def selecionar():
            sel = tree_p.selection()
            if sel:
                vals = tree_p.item(sel[0])["values"]
                self.var_prodcod.set(str(vals[0]))
                self.lbl_prod_nome.config(text=f"{vals[1]}")
                try:
                    modal.destroy()
                except Exception:
                    pass
                self.ent_numero_lote.focus_set()
            return "break"

        ent_b.bind("<Return>", lambda e: (recarregar(), "break")[1])
        tree_p.bind("<Double-1>", lambda e: (selecionar(), "break")[1])
        tree_p.bind("<Return>", lambda e: (selecionar(), "break")[1])
        modal.bind("<Escape>", lambda e: (modal.destroy(), "break")[1])

        recarregar()
        ent_b.focus_set()

    def _abrir_busca_fornecedor(self):
        """Abre modal F4 para seleção de fornecedores."""
        modal = tk.Toplevel(self)
        modal.title("Pesquisa de Fornecedores / Entidades")
        modal.transient(self)
        modal.grab_set()
        centralizar_janela(modal, self, 640, 440)

        f_cont = ttk.Frame(modal, padding=10)
        f_cont.pack(fill=tk.BOTH, expand=True)

        f_b = ttk.Frame(f_cont)
        f_b.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(f_b, text="Buscar:").pack(side=tk.LEFT)
        var_b = tk.StringVar()
        vincular_maiusculo(var_b)
        ent_b = ttk.Entry(f_b, textvariable=var_b, width=30)
        ent_b.pack(side=tk.LEFT, padx=6)

        btn_pesq = ttk.Button(f_b, text="🔍 Buscar", command=lambda: recarregar())
        btn_pesq.pack(side=tk.LEFT, padx=4)

        lbl_status_busca = tk.Label(f_cont, text="", font=("Segoe UI", 9, "bold"), anchor="w")
        lbl_status_busca.pack(fill=tk.X, pady=(0, 4))

        cols_f = ("cod", "nome")
        tree_f = ttk.Treeview(f_cont, columns=cols_f, show="headings", height=12)
        tree_f.heading("cod", text="Código")
        tree_f.heading("nome", text="Razão Social / Nome")
        tree_f.column("cod", width=90, anchor=tk.CENTER)
        tree_f.column("nome", width=450, anchor=tk.W)
        tree_f.pack(fill=tk.BOTH, expand=True)

        def _buscar_fornecedores_banco(termo: str = ""):
            if not self.service or not self.service._repo.conn:
                return []
            cur = self.service._repo.conn.cursor()
            nolock = self.service._repo._nolock()
            t = f"%{termo.strip().upper()}%"
            # 1. Tenta USER_geoapolo_entidade (base local ativa)
            try:
                cur.execute(
                    f"SELECT geoentcod, geoentnome FROM USER_geoapolo_entidade {nolock} "
                    f"WHERE UPPER(geoentnome) LIKE ? OR CAST(geoentcod AS VARCHAR) LIKE ? "
                    f"ORDER BY geoentnome ASC",
                    [t, t]
                )
                linhas = cur.fetchall()
                if linhas:
                    return [(str(r[0]), str(r[1] or "").strip()) for r in linhas[:100]]
            except Exception:
                pass

            # 2. Fallback para ENTIDADE
            try:
                cur.execute(
                    f"SELECT entcod, entnome FROM ENTIDADE {nolock} "
                    f"WHERE UPPER(entnome) LIKE ? OR CAST(entcod AS VARCHAR) LIKE ? "
                    f"ORDER BY entnome ASC",
                    [t, t]
                )
                linhas = cur.fetchall()
                if linhas:
                    return [(str(r[0]), str(r[1] or "").strip()) for r in linhas[:100]]
            except Exception:
                pass
            return []

        def recarregar(primeira_vez: bool = False):
            tree_f.delete(*tree_f.get_children())
            termo = var_b.get().strip()
            registros = _buscar_fornecedores_banco(termo)
            if not registros:
                lbl_status_busca.config(
                    text="⚠️ Não há registros na tabela de fornecedores/entidades.",
                    fg="#DC2626",
                    bg="#FEE2E2",
                )
                if primeira_vez:
                    messagebox.showinfo(
                        "Fornecedores",
                        "Não há registros na tabela de fornecedores/entidades.",
                        parent=modal,
                    )
            else:
                lbl_status_busca.config(
                    text=f"✔ {len(registros)} entidade(s) localizada(s). Duplo clique para selecionar.",
                    fg="#15803D",
                    bg="#DCFCE7",
                )
                for r in registros:
                    tree_f.insert("", tk.END, values=(r[0], r[1]))

        def selecionar():
            sel = tree_f.selection()
            if sel:
                vals = tree_f.item(sel[0])["values"]
                self.var_forncod.set(str(vals[0]))
                self.lbl_forn_nome.config(text=f"{vals[1]}")
                try:
                    modal.destroy()
                except Exception:
                    pass
                self.ent_obs.focus_set()
            return "break"

        ent_b.bind("<Return>", lambda e: (recarregar(), "break")[1])
        tree_f.bind("<Double-1>", lambda e: (selecionar(), "break")[1])
        tree_f.bind("<Return>", lambda e: (selecionar(), "break")[1])
        modal.bind("<Escape>", lambda e: (modal.destroy(), "break")[1])

        recarregar(primeira_vez=True)
        ent_b.focus_set()


    def _salvar_lote(self):
        """Valida e persiste os dados do lote."""
        if not self.service:
            return

        cod_raw = self.var_prodcod.get().strip()
        if not cod_raw:
            messagebox.showerror("Aviso", "O Código do Produto é obrigatório.", parent=self)
            self.ent_prodcod.focus_set()
            return

        try:
            prod_int = int(cod_raw)
        except ValueError:
            messagebox.showerror("Aviso", "Código do Produto inválido.", parent=self)
            self.ent_prodcod.focus_set()
            return

        num_lote = self.var_numero_lote.get().strip().upper()
        if not num_lote:
            messagebox.showerror("Aviso", "O Número do Lote é obrigatório.", parent=self)
            self.ent_numero_lote.focus_set()
            return

        # Datas
        d_fab_br = self.var_dt_fab.get().strip()
        if d_fab_br and not validar_data_br(d_fab_br):
            messagebox.showerror("Aviso", "Data de fabricação inválida. Utilize DD/MM/AAAA.", parent=self)
            self.ent_dt_fab.focus_set()
            return
        d_fab_iso = converter_data_br_para_iso(d_fab_br) if d_fab_br else None

        d_val_br = self.var_dt_val.get().strip()
        if d_val_br and not validar_data_br(d_val_br):
            messagebox.showerror("Aviso", "Data de validade inválida. Utilize DD/MM/AAAA.", parent=self)
            self.ent_dt_val.focus_set()
            return
        d_val_iso = converter_data_br_para_iso(d_val_br) if d_val_br else None

        # Quantidades
        try:
            q_ini = float(self.var_qtd_ini.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Aviso", "Quantidade inicial inválida.", parent=self)
            self.ent_qtd_ini.focus_set()
            return

        try:
            q_atu = float(self.var_qtd_atu.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Aviso", "Quantidade atual inválida.", parent=self)
            self.ent_qtd_atu.focus_set()
            return

        # Fornecedor
        forn_raw = self.var_forncod.get().strip()
        forn_int = None
        if forn_raw:
            try:
                forn_int = int(forn_raw)
            except ValueError:
                pass

        # Usuário da Sessão
        usucod_atual = ""
        try:
            from logon import sessao_usuario_atual
            usucod_atual = sessao_usuario_atual.get("usucod_apolo") or sessao_usuario_atual.get("login") or ""
        except Exception:
            pass

        dto = ProdutoLoteDTO(
            id_produto_lote=self._id_lote_edicao,
            prodcod=prod_int,
            numero_lote=num_lote,
            data_fabricacao=d_fab_iso,
            data_validade=d_val_iso,
            quantidade_inicial=q_ini,
            quantidade_atual=q_atu,
            entcod_fornecedor=forn_int,
            status=self.var_status.get().strip().upper() or "A",
            observacao=self.var_obs.get().strip(),
            usucod=str(usucod_atual),
        )

        res = self.service.salvar_lote(dto)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem, parent=self)
            self.carregar_lotes()

            # Executa callback de retorno se informado
            if self.ao_salvar_callback:
                try:
                    self.ao_salvar_callback(num_lote)
                except Exception:
                    pass

            self._limpar_campos()
        else:
            messagebox.showerror("Erro ao Salvar Lote", res.mensagem, parent=self)

    def _excluir_lote(self):
        """Exclui ou inativa o lote selecionado."""
        if not self.service or not self._id_lote_edicao:
            messagebox.showwarning("Aviso", "Selecione um lote na tabela para excluir.", parent=self)
            return

        num_lote = self.var_numero_lote.get().strip()
        if not messagebox.askyesno(
            "Confirmação de Exclusão",
            f"Deseja realmente excluir o lote '{num_lote}' (ID: {self._id_lote_edicao})?",
            parent=self,
        ):
            return

        res = self.service.excluir_lote(self._id_lote_edicao)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem, parent=self)
            self.carregar_lotes()
            self._limpar_campos()
        else:
            messagebox.showerror("Erro ao Excluir", res.mensagem, parent=self)


def abrir_janela_lotes(
    parent,
    prodcod: Optional[int] = None,
    numero_lote: str = "",
    callback: Optional[Callable[[str], None]] = None,
    connection=None,
    service: Optional[LotesService] = None,
):
    """Abre a tela de Cadastro e Controle de Lotes em janela TopLevel."""
    win = tk.Toplevel(parent)
    win.title("Cadastro e Controle de Lotes de Produtos - GeoAlvo")
    win.minsize(860, 520)
    centralizar_janela(win, parent, 980, 620)
    view = LotesView(
        win,
        service=service,
        connection=connection,
        prodcod_inicial=prodcod,
        numero_lote_inicial=numero_lote,
        ao_salvar_callback=callback,
    )
    view.pack(fill=tk.BOTH, expand=True)
    return win
