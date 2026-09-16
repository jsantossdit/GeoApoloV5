"""
Interface Gráfica para Exclusão e Auditoria de Lançamentos Contábeis.
GeoApolo V5
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from datetime import date, datetime
from .models import FiltroExclusaoModuloDTO
from .repository import ContabilidadeRepository
from .service import ContabilidadeService


class ExclusaoContabilView:
    """Janela corporativa para auditoria e exclusão controlada de lançamentos contábeis."""

    def __init__(self, parent: tk.Tk, service: Optional[ContabilidadeService] = None):
        self.parent = parent
        self.service = service or ContabilidadeService(ContabilidadeRepository())

        self.window = tk.Toplevel(parent)
        self.window.title("GeoAlvo - Exclusão de Lançamentos Contábeis")
        self.window.geometry("980x680")
        self.window.minsize(850, 580)
        self.window.transient(parent)
        self.window.grab_set()

        self._setup_ui()
        self._pesquisar_geral()

    def _setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg="#1A365D", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        lbl_titulo = tk.Label(
            header,
            text="Exclusão e Auditoria de Lançamentos Contábeis",
            font=("Segoe UI", 13, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
        )
        lbl_titulo.pack(side=tk.LEFT, padx=15, pady=12)

        # Notebook com Abas (Exclusão Individual vs Exclusão por Lote)
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Aba 1: Individual / Pesquisa Geral
        self.tab_individual = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_individual, text=" Consulta e Exclusão Individual ")
        self._setup_tab_individual()

        # Aba 2: Exclusão em Lote por Módulo
        self.tab_modulo = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_modulo, text=" Exclusão em Lote por Módulo ")
        self._setup_tab_modulo()

    def _setup_tab_individual(self):
        # Filtros
        filtros_frame = ttk.LabelFrame(self.tab_individual, text=" Filtros de Pesquisa ", padding="8")
        filtros_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(filtros_frame, text="Campo:").grid(row=0, column=0, padx=4, sticky="w")
        self.cbo_campo = ttk.Combobox(
            filtros_frame,
            values=["contablancchv", "contablancorignum", "contablancmod", "contablancctadeb", "contablancctacred"],
            state="readonly",
            width=18,
        )
        self.cbo_campo.current(0)
        self.cbo_campo.grid(row=0, column=1, padx=4, sticky="w")

        ttk.Label(filtros_frame, text="Procurar por:").grid(row=0, column=2, padx=4, sticky="w")
        self.txt_procurar = ttk.Entry(filtros_frame, width=22)
        self.txt_procurar.grid(row=0, column=3, padx=4, sticky="w")
        self.txt_procurar.bind("<Return>", lambda e: self._pesquisar_geral())

        ttk.Label(filtros_frame, text="Módulo:").grid(row=0, column=4, padx=4, sticky="w")
        self.cbo_origem = ttk.Combobox(
            filtros_frame,
            values=["", "Financeiro", "Contabilidade", "Estoque", "Vendas", "Compras", "Folha"],
            state="readonly",
            width=14,
        )
        self.cbo_origem.current(0)
        self.cbo_origem.grid(row=0, column=5, padx=4, sticky="w")

        btn_buscar = ttk.Button(filtros_frame, text="🔍 Pesquisar", command=self._pesquisar_geral)
        btn_buscar.grid(row=0, column=6, padx=6, sticky="w")

        btn_limpar = ttk.Button(filtros_frame, text="Limpar", command=self._limpar_pesquisa_individual)
        btn_limpar.grid(row=0, column=7, padx=4, sticky="w")

        # Grid
        grid_frame = ttk.Frame(self.tab_individual)
        grid_frame.pack(fill=tk.BOTH, expand=True)

        colunas = ("chave", "data", "modulo", "submodulo", "orignum", "val", "deb", "cred", "hist")
        self.tree_indiv = ttk.Treeview(grid_frame, columns=colunas, show="headings", selectmode="browse")

        self.tree_indiv.heading("chave", text="Chave")
        self.tree_indiv.heading("data", text="Data")
        self.tree_indiv.heading("modulo", text="Módulo")
        self.tree_indiv.heading("submodulo", text="SubMódulo")
        self.tree_indiv.heading("orignum", text="Nº Origem")
        self.tree_indiv.heading("val", text="Valor (R$)")
        self.tree_indiv.heading("deb", text="Cta Débito")
        self.tree_indiv.heading("cred", text="Cta Crédito")
        self.tree_indiv.heading("hist", text="Histórico")

        self.tree_indiv.column("chave", width=90, anchor="w")
        self.tree_indiv.column("data", width=85, anchor="center")
        self.tree_indiv.column("modulo", width=95, anchor="w")
        self.tree_indiv.column("submodulo", width=95, anchor="w")
        self.tree_indiv.column("orignum", width=90, anchor="w")
        self.tree_indiv.column("val", width=95, anchor="e")
        self.tree_indiv.column("deb", width=80, anchor="w")
        self.tree_indiv.column("cred", width=80, anchor="w")
        self.tree_indiv.column("hist", width=220, anchor="w")

        scroll_y = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.tree_indiv.yview)
        self.tree_indiv.configure(yscrollcommand=scroll_y.set)

        self.tree_indiv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_indiv.bind("<<TreeviewSelect>>", self._ao_selecionar_individual)

        # Painel Inferior de Ação Individual
        acao_frame = ttk.LabelFrame(self.tab_individual, text=" Lançamento Selecionado ", padding="8")
        acao_frame.pack(fill=tk.X, pady=(8, 0))

        ttk.Label(acao_frame, text="Chave:").grid(row=0, column=0, padx=5, sticky="w")
        self.txt_chave_sel = ttk.Entry(acao_frame, width=15)
        self.txt_chave_sel.grid(row=0, column=1, padx=5, sticky="w")

        ttk.Label(acao_frame, text="Nº Origem:").grid(row=0, column=2, padx=5, sticky="w")
        self.txt_orig_sel = ttk.Entry(acao_frame, width=15)
        self.txt_orig_sel.grid(row=0, column=3, padx=5, sticky="w")

        self.lbl_info_detalhe = ttk.Label(acao_frame, text="", font=("Segoe UI", 9, "italic"))
        self.lbl_info_detalhe.grid(row=0, column=4, padx=10, sticky="w")

        btn_box = ttk.Frame(acao_frame)
        btn_box.grid(row=0, column=5, sticky="e")
        acao_frame.columnconfigure(5, weight=1)

        self.btn_excluir_indiv = tk.Button(
            btn_box,
            text="🗑 Excluir Lançamento",
            font=("Segoe UI", 9, "bold"),
            bg="#C53030",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            command=self._excluir_lancamento_selecionado,
            cursor="hand2",
        )
        self.btn_excluir_indiv.pack(side=tk.RIGHT, padx=5)

    def _setup_tab_modulo(self):
        param_frame = ttk.LabelFrame(self.tab_modulo, text=" Critérios para Exclusão em Lote ", padding="10")
        param_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(param_frame, text="Data Inicial (AAAA-MM-DD):").grid(row=0, column=0, padx=5, sticky="w")
        self.txt_dt_ini = ttk.Entry(param_frame, width=14)
        hoje = date.today().strftime("%Y-%m-%d")
        self.txt_dt_ini.insert(0, hoje)
        self.txt_dt_ini.grid(row=0, column=1, padx=5, sticky="w")

        ttk.Label(param_frame, text="Data Final (AAAA-MM-DD):").grid(row=0, column=2, padx=5, sticky="w")
        self.txt_dt_fim = ttk.Entry(param_frame, width=14)
        self.txt_dt_fim.insert(0, hoje)
        self.txt_dt_fim.grid(row=0, column=3, padx=5, sticky="w")

        ttk.Label(param_frame, text="Módulo:").grid(row=0, column=4, padx=5, sticky="w")
        self.cbo_mod_lote = ttk.Combobox(
            param_frame,
            values=["Financeiro", "Contabilidade", "Estoque", "Vendas", "Compras", "Folha"],
            state="readonly",
            width=14,
        )
        self.cbo_mod_lote.current(0)
        self.cbo_mod_lote.grid(row=0, column=5, padx=5, sticky="w")

        ttk.Label(param_frame, text="Submódulo:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.txt_submod_lote = ttk.Entry(param_frame, width=14)
        self.txt_submod_lote.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        btn_pesq_mod = ttk.Button(param_frame, text="🔍 Filtrar Lote", command=self._pesquisar_lote_modulo)
        btn_pesq_mod.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Grid Lote
        grid_lote_frame = ttk.Frame(self.tab_modulo)
        grid_lote_frame.pack(fill=tk.BOTH, expand=True)

        colunas = ("chave", "data", "modulo", "submodulo", "orignum", "val", "hist")
        self.tree_lote = ttk.Treeview(grid_lote_frame, columns=colunas, show="headings")

        self.tree_lote.heading("chave", text="Chave")
        self.tree_lote.heading("data", text="Data")
        self.tree_lote.heading("modulo", text="Módulo")
        self.tree_lote.heading("submodulo", text="SubMódulo")
        self.tree_lote.heading("orignum", text="Nº Origem")
        self.tree_lote.heading("val", text="Valor (R$)")
        self.tree_lote.heading("hist", text="Histórico")

        self.tree_lote.column("chave", width=90, anchor="w")
        self.tree_lote.column("data", width=85, anchor="center")
        self.tree_lote.column("modulo", width=100, anchor="w")
        self.tree_lote.column("submodulo", width=100, anchor="w")
        self.tree_lote.column("orignum", width=100, anchor="w")
        self.tree_lote.column("val", width=100, anchor="e")
        self.tree_lote.column("hist", width=280, anchor="w")

        scroll_lote = ttk.Scrollbar(grid_lote_frame, orient=tk.VERTICAL, command=self.tree_lote.yview)
        self.tree_lote.configure(yscrollcommand=scroll_lote.set)

        self.tree_lote.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_lote.pack(side=tk.RIGHT, fill=tk.Y)

        # Rodapé Lote
        bottom_lote = ttk.Frame(self.tab_modulo, padding="8")
        bottom_lote.pack(fill=tk.X)

        self.lbl_status_lote = ttk.Label(bottom_lote, text="Informe os critérios e clique em 'Filtrar Lote'.")
        self.lbl_status_lote.pack(side=tk.LEFT)

        btn_excluir_lote = tk.Button(
            bottom_lote,
            text="⚠ Excluir TODOS os Lançamentos do Período",
            font=("Segoe UI", 9, "bold"),
            bg="#9B2C2C",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self._executar_exclusao_lote,
            cursor="hand2",
        )
        btn_excluir_lote.pack(side=tk.RIGHT)

    def _pesquisar_geral(self):
        for it in self.tree_indiv.get_children():
            self.tree_indiv.delete(it)

        campo = self.cbo_campo.get()
        valor = self.txt_procurar.get().strip()
        origem = self.cbo_origem.get().strip()

        try:
            itens = self.service.pesquisar_lancamentos(campo=campo, valor=valor, origem=origem)
            for lanc in itens:
                dt_str = lanc.data.strftime("%d/%m/%Y") if lanc.data else ""
                val_str = f"{lanc.valor:,.2f}"
                self.tree_indiv.insert(
                    "",
                    tk.END,
                    values=(
                        lanc.chave,
                        dt_str,
                        lanc.modulo,
                        lanc.submodulo,
                        lanc.numero_origem,
                        val_str,
                        lanc.conta_debito,
                        lanc.conta_credito,
                        lanc.historico,
                    ),
                )
        except Exception as e:
            messagebox.showerror("Erro na Pesquisa", f"Falha ao pesquisar lançamentos:\n{e}")

    def _limpar_pesquisa_individual(self):
        self.txt_procurar.delete(0, tk.END)
        self.cbo_origem.current(0)
        self.txt_chave_sel.delete(0, tk.END)
        self.txt_orig_sel.delete(0, tk.END)
        self.lbl_info_detalhe.config(text="")
        self._pesquisar_geral()

    def _ao_selecionar_individual(self, event=None):
        sel = self.tree_indiv.selection()
        if not sel:
            return
        vals = self.tree_indiv.item(sel[0])["values"]
        if vals:
            self.txt_chave_sel.delete(0, tk.END)
            self.txt_chave_sel.insert(0, str(vals[0]))
            self.txt_orig_sel.delete(0, tk.END)
            self.txt_orig_sel.insert(0, str(vals[4]))
            self.lbl_info_detalhe.config(text=f"Módulo: {vals[2]} | Valor: R$ {vals[5]}")

    def _excluir_lancamento_selecionado(self):
        chave = self.txt_chave_sel.get().strip()
        if not chave:
            messagebox.showwarning("Aviso", "Selecione ou informe a chave do lançamento a excluir.")
            return

        # Checagem prévia de integridade
        val = self.service.validar_exclusao(chave)
        if not val.permitido:
            messagebox.showerror("Exclusão Bloqueada", val.mensagem)
            return

        if not messagebox.askyesno(
            "Confirmação de Exclusão",
            f"Deseja realmente EXCLUIR o lançamento contábil chave '{chave}'?",
        ):
            return

        res = self.service.excluir_lancamento(chave)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self._pesquisar_geral()
            self.txt_chave_sel.delete(0, tk.END)
            self.txt_orig_sel.delete(0, tk.END)
        else:
            messagebox.showerror("Erro ao Excluir", res.mensagem)

    def _pesquisar_lote_modulo(self):
        for it in self.tree_lote.get_children():
            self.tree_lote.delete(it)

        try:
            dt_ini = datetime.strptime(self.txt_dt_ini.get().strip(), "%Y-%m-%d").date()
            dt_fim = datetime.strptime(self.txt_dt_fim.get().strip(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Data Inválida", "Formato de data inválido. Use AAAA-MM-DD.")
            return

        filtro = FiltroExclusaoModuloDTO(
            data_inicial=dt_ini,
            data_final=dt_fim,
            modulo=self.cbo_mod_lote.get().strip(),
            submodulo=self.txt_submod_lote.get().strip(),
        )

        try:
            itens = self.service.pesquisar_por_modulo(filtro)
            for lanc in itens:
                dt_str = lanc.data.strftime("%d/%m/%Y") if lanc.data else ""
                val_str = f"{lanc.valor:,.2f}"
                self.tree_lote.insert(
                    "",
                    tk.END,
                    values=(
                        lanc.chave,
                        dt_str,
                        lanc.modulo,
                        lanc.submodulo,
                        lanc.numero_origem,
                        val_str,
                        lanc.historico,
                    ),
                )
            self.lbl_status_lote.config(text=f"Total de {len(itens)} lançamento(s) localizado(s) no período.")
        except Exception as e:
            messagebox.showerror("Erro ao Pesquisar Lote", str(e))

    def _executar_exclusao_lote(self):
        try:
            dt_ini = datetime.strptime(self.txt_dt_ini.get().strip(), "%Y-%m-%d").date()
            dt_fim = datetime.strptime(self.txt_dt_fim.get().strip(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Data Inválida", "Formato de data inválido. Use AAAA-MM-DD.")
            return

        filtro = FiltroExclusaoModuloDTO(
            data_inicial=dt_ini,
            data_final=dt_fim,
            modulo=self.cbo_mod_lote.get().strip(),
            submodulo=self.txt_submod_lote.get().strip(),
        )

        if not messagebox.askyesno(
            "ALERTA DE SEGURANÇA",
            f"ATENÇÃO: Deseja realmente excluir em LOTE todos os lançamentos do módulo '{filtro.modulo}' "
            f"no período de {dt_ini} até {dt_fim}?\n\nEsta operação é definitiva!",
        ):
            return

        res = self.service.excluir_em_lote_por_modulo(filtro)
        if res.sucesso:
            messagebox.showinfo("Exclusão Concluída", res.mensagem)
            self._pesquisar_lote_modulo()
            self._pesquisar_geral()
        else:
            messagebox.showerror("Erro ao Excluir em Lote", res.mensagem)
