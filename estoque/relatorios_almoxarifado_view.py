"""
Módulo de Relatórios e Consultas Gerenciais de Almoxarifados.
GeoApolo V5
Relatórios:
1. Saldos e Posição Físico-Financeira por Almoxarifado
2. Recentes Aquisições e Entradas de Compras por Almoxarifado
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from core import centralizar_janela
from estoque.almoxarifados_repository import AlmoxarifadosRepository


class RelatoriosAlmoxarifadoView(ttk.Frame):
    """Central de Relatórios Gerenciais de Almoxarifados e Recentes Aquisições."""

    def __init__(self, parent=None, repo: Optional[AlmoxarifadosRepository] = None, connection=None):
        super().__init__(parent)
        self.repo = repo or AlmoxarifadosRepository(connection)
        self._setup_ui()
        self._carregar_combos()
        self.carregar_relatorio_saldos()
        self.carregar_relatorio_aquisicoes()

    def _setup_ui(self):
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Relatórios Gerenciais: Saldos & Recentes Aquisições por Almoxarifado",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
        ).pack(side=tk.LEFT)

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Aba 1: Saldos por Almoxarifado
        self.tab_saldos = ttk.Frame(notebook, padding=8)
        notebook.add(self.tab_saldos, text="📦 Saldos por Almoxarifado")
        self._setup_tab_saldos()

        # Aba 2: Recentes Aquisições
        self.tab_aquisicoes = ttk.Frame(notebook, padding=8)
        notebook.add(self.tab_aquisicoes, text="🛒 Recentes Aquisições & Entradas")
        self._setup_tab_aquisicoes()

    # -------------------------------------------------------------------------
    # ABA 1: SALDOS POR ALMOXARIFADO
    # -------------------------------------------------------------------------
    def _setup_tab_saldos(self):
        f_top = ttk.Frame(self.tab_saldos)
        f_top.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(f_top, text="Almoxarifado:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_almox_saldo = tk.StringVar(value="TODOS")
        self.cbo_almox_saldo = ttk.Combobox(f_top, textvariable=self.var_almox_saldo, state="readonly", width=32)
        self.cbo_almox_saldo.pack(side=tk.LEFT, padx=(0, 8))
        self.cbo_almox_saldo.bind("<<ComboboxSelected>>", lambda e: self.carregar_relatorio_saldos())

        btn_atualizar = ttk.Button(f_top, text="Atualizar", command=self.carregar_relatorio_saldos, width=10)
        btn_atualizar.pack(side=tk.LEFT, padx=2)

        self.lbl_tot_saldos = ttk.Label(f_top, text="Total: 0 produtos | Saldo Total: 0.00", font=("Segoe UI", 9, "bold"), foreground="#15803D")
        self.lbl_tot_saldos.pack(side=tk.RIGHT, padx=6)

        cols = ("almox", "cod", "nome", "unid", "saldo", "ult_mov", "marca")
        self.tree_saldos = ttk.Treeview(self.tab_saldos, columns=cols, show="headings", selectmode="browse")
        self.tree_saldos.heading("almox", text="Almoxarifado")
        self.tree_saldos.heading("cod", text="Cód.")
        self.tree_saldos.heading("nome", text="Descrição do Produto")
        self.tree_saldos.heading("unid", text="Unid.")
        self.tree_saldos.heading("saldo", text="Saldo Atual")
        self.tree_saldos.heading("ult_mov", text="Últ. Movimento")
        self.tree_saldos.heading("marca", text="Marca")

        self.tree_saldos.column("almox", width=180, anchor=tk.W)
        self.tree_saldos.column("cod", width=60, anchor=tk.CENTER)
        self.tree_saldos.column("nome", width=320, anchor=tk.W)
        self.tree_saldos.column("unid", width=50, anchor=tk.CENTER)
        self.tree_saldos.column("saldo", width=100, anchor=tk.E)
        self.tree_saldos.column("ult_mov", width=100, anchor=tk.CENTER)
        self.tree_saldos.column("marca", width=120, anchor=tk.W)

        sb_y = ttk.Scrollbar(self.tab_saldos, orient=tk.VERTICAL, command=self.tree_saldos.yview)
        self.tree_saldos.configure(yscrollcommand=sb_y.set)
        self.tree_saldos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_y.pack(side=tk.RIGHT, fill=tk.Y)

    # -------------------------------------------------------------------------
    # ABA 2: RECENTES AQUISIÇÕES & ENTRADAS
    # -------------------------------------------------------------------------
    def _setup_tab_aquisicoes(self):
        f_top = ttk.Frame(self.tab_aquisicoes)
        f_top.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(f_top, text="Almoxarifado:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_almox_aquis = tk.StringVar(value="TODOS")
        self.cbo_almox_aquis = ttk.Combobox(f_top, textvariable=self.var_almox_aquis, state="readonly", width=28)
        self.cbo_almox_aquis.pack(side=tk.LEFT, padx=(0, 8))
        self.cbo_almox_aquis.bind("<<ComboboxSelected>>", lambda e: self.carregar_relatorio_aquisicoes())

        ttk.Label(f_top, text="Período:").pack(side=tk.LEFT, padx=(4, 4))
        self.var_periodo = tk.StringVar(value="60 dias")
        self.cbo_periodo = ttk.Combobox(
            f_top,
            textvariable=self.var_periodo,
            values=["15 dias", "30 dias", "60 dias", "90 dias", "180 dias", "365 dias"],
            state="readonly",
            width=10,
        )
        self.cbo_periodo.pack(side=tk.LEFT, padx=(0, 8))
        self.cbo_periodo.bind("<<ComboboxSelected>>", lambda e: self.carregar_relatorio_aquisicoes())

        btn_atualizar = ttk.Button(f_top, text="Atualizar", command=self.carregar_relatorio_aquisicoes, width=10)
        btn_atualizar.pack(side=tk.LEFT, padx=2)

        self.lbl_tot_aquis = ttk.Label(f_top, text="Total Compras: R$ 0,00", font=("Segoe UI", 9, "bold"), foreground="#1D4ED8")
        self.lbl_tot_aquis.pack(side=tk.RIGHT, padx=6)

        cols = ("data", "almox", "cod", "nome", "unid", "qtd", "unit", "total", "lote", "forn")
        self.tree_aquis = ttk.Treeview(self.tab_aquisicoes, columns=cols, show="headings", selectmode="browse")
        self.tree_aquis.heading("data", text="Data")
        self.tree_aquis.heading("almox", text="Almoxarifado")
        self.tree_aquis.heading("cod", text="Cód.")
        self.tree_aquis.heading("nome", text="Descrição do Produto")
        self.tree_aquis.heading("unid", text="Unid.")
        self.tree_aquis.heading("qtd", text="Qtd.")
        self.tree_aquis.heading("unit", text="Vl. Unitário")
        self.tree_aquis.heading("total", text="Total (R$)")
        self.tree_aquis.heading("lote", text="Nº Lote")
        self.tree_aquis.heading("forn", text="Fornecedor / Origem")

        self.tree_aquis.column("data", width=80, anchor=tk.CENTER)
        self.tree_aquis.column("almox", width=140, anchor=tk.W)
        self.tree_aquis.column("cod", width=55, anchor=tk.CENTER)
        self.tree_aquis.column("nome", width=220, anchor=tk.W)
        self.tree_aquis.column("unid", width=45, anchor=tk.CENTER)
        self.tree_aquis.column("qtd", width=70, anchor=tk.E)
        self.tree_aquis.column("unit", width=80, anchor=tk.E)
        self.tree_aquis.column("total", width=95, anchor=tk.E)
        self.tree_aquis.column("lote", width=90, anchor=tk.CENTER)
        self.tree_aquis.column("forn", width=180, anchor=tk.W)

        sb_y = ttk.Scrollbar(self.tab_aquisicoes, orient=tk.VERTICAL, command=self.tree_aquis.yview)
        self.tree_aquis.configure(yscrollcommand=sb_y.set)
        self.tree_aquis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_y.pack(side=tk.RIGHT, fill=tk.Y)

    def _carregar_combos(self):
        try:
            almoxs = self.repo.listar_almoxarifados()
            vals = ["TODOS"] + [f"{a['codigo_almoxarifado']} - {a['descricao']}" for a in almoxs]
            self.cbo_almox_saldo["values"] = vals
            self.cbo_almox_aquis["values"] = vals
        except Exception:
            pass

    def carregar_relatorio_saldos(self):
        for it in self.tree_saldos.get_children():
            self.tree_saldos.delete(it)

        raw = self.var_almox_saldo.get().strip()
        cod_almox = "" if raw == "TODOS" else raw.split(" - ")[0].strip()

        try:
            dados = self.repo.obter_relatorio_saldos(cod_almox)
            tot_itens = len(dados)
            tot_qtd = 0.0
            for r in dados:
                s = float(r.get("saldo_atual") or 0.0)
                tot_qtd += s
                almox_desc = f"{r.get('codigo_almoxarifado')} - {r.get('nome_almoxarifado')}"
                self.tree_saldos.insert(
                    "",
                    tk.END,
                    values=(
                        almox_desc,
                        r.get("prodcod"),
                        r.get("prodnome"),
                        r.get("unidade"),
                        f"{s:.2f}",
                        r.get("data_ult_mov") or "-",
                        r.get("marca") or "-",
                    ),
                )
            self.lbl_tot_saldos.config(text=f"Total: {tot_itens} item(ns) | Saldo Total: {tot_qtd:.2f}")
        except Exception as ex:
            messagebox.showerror("Erro", f"Falha ao carregar saldos: {ex}", parent=self)

    def carregar_relatorio_aquisicoes(self):
        for it in self.tree_aquis.get_children():
            self.tree_aquis.delete(it)

        raw_almox = self.var_almox_aquis.get().strip()
        cod_almox = "" if raw_almox == "TODOS" else raw_almox.split(" - ")[0].strip()

        raw_p = self.var_periodo.get().split()[0]
        try:
            dias = int(raw_p)
        except Exception:
            dias = 60

        try:
            dados = self.repo.obter_relatorio_aquisicoes_recentes(cod_almox, dias=dias)
            tot_valor = 0.0
            for r in dados:
                qtd = float(r.get("quantidade") or 0.0)
                unit = float(r.get("valor_unitario") or 0.0)
                tot = float(r.get("valor_total") or (qtd * unit))
                tot_valor += tot
                almox_desc = f"{r.get('codigo_almoxarifado')} - {r.get('nome_almoxarifado')}"
                self.tree_aquis.insert(
                    "",
                    tk.END,
                    values=(
                        r.get("data_mov"),
                        almox_desc,
                        r.get("prodcod"),
                        r.get("prodnome"),
                        r.get("unidade"),
                        f"{qtd:.2f}",
                        f"R$ {unit:.2f}",
                        f"R$ {tot:.2f}",
                        r.get("numero_lote") or "-",
                        r.get("fornecedor") or "-",
                    ),
                )
            self.lbl_tot_aquis.config(text=f"Total Compras: R$ {tot_valor:,.2f} ({len(dados)} lançamentos)")
        except Exception as ex:
            messagebox.showerror("Erro", f"Falha ao carregar aquisições: {ex}", parent=self)


def abrir_relatorios_almoxarifados_sistema(parent=None, connection=None):
    """Abre a janela de relatórios de almoxarifados."""
    win = tk.Toplevel(parent)
    win.title("Relatórios de Estoque e Recentes Aquisições por Almoxarifado - GeoAlvo")
    win.minsize(980, 560)
    centralizar_janela(win, parent, 1080, 620)
    view = RelatoriosAlmoxarifadoView(win, connection=connection)
    view.pack(fill=tk.BOTH, expand=True)
    return win
