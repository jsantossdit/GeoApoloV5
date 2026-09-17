"""
Interface Gráfica para Manutenção de Códigos e Sequenciais do Sistema.
GeoApolo V5
Clean Architecture: View desacoplada em Tkinter/ttk com suporte a execução headless.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from .models import ConfigCodDTO, ResultadoConfigCodDTO
from .service import ConfigCodService


class ManutencaoCodigosView(ttk.Frame):
    """Tela de Manutenção de Sequenciais e Códigos de Tabelas do Sistema."""

    def __init__(self, parent=None, service: Optional[ConfigCodService] = None, connection=None):
        super().__init__(parent)
        self.service = service

        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from .repository import ConfigCodRepository
                conn = connection or obter_conexao_banco()
                self.service = ConfigCodService(ConfigCodRepository(conn))
            except Exception:
                pass

        self._setup_ui()
        if self.service:
            self.carregar_tabelas()

    def _setup_ui(self):
        # Header
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Manutenção de Códigos do Sistema",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
        ).pack(side=tk.LEFT)

        ttk.Label(
            header,
            text="Controle e ajuste de sequenciais numéricos (auto-incremento) das tabelas",
            font=("Segoe UI", 9),
            foreground="#6B7280",
        ).pack(side=tk.LEFT, padx=15)

        # Barra de Filtro
        frame_busca = ttk.Frame(self, padding=(10, 5))
        frame_busca.pack(fill=tk.X)

        ttk.Label(frame_busca, text="Filtrar Tabela:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        self.ent_busca = ttk.Entry(frame_busca, width=30)
        self.ent_busca.pack(side=tk.LEFT, padx=8)
        self.ent_busca.bind("<Return>", lambda e: self.carregar_tabelas())
        self.ent_busca.bind("<KeyRelease>", lambda e: self.carregar_tabelas())

        ttk.Button(frame_busca, text="🔍 Buscar", command=self.carregar_tabelas).pack(side=tk.LEFT, padx=4)
        ttk.Button(frame_busca, text="🔄 Recarregar", command=self._recarregar).pack(side=tk.LEFT)

        # PanedWindow
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Grid de Tabelas
        frame_grid = ttk.Frame(paned, padding=5)
        paned.add(frame_grid, weight=3)

        cols = ("tabela", "proximo", "status", "empresa")
        self.tree = ttk.Treeview(frame_grid, columns=cols, show="headings", height=15)
        self.tree.heading("tabela", text="Tabela do GeoApolo")
        self.tree.heading("proximo", text="Próximo Código")
        self.tree.heading("status", text="Status")
        self.tree.heading("empresa", text="Empresa")

        self.tree.column("tabela", width=220)
        self.tree.column("proximo", width=110, anchor=tk.CENTER)
        self.tree.column("status", width=90, anchor=tk.CENTER)
        self.tree.column("empresa", width=130)

        scroll = ttk.Scrollbar(frame_grid, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self._ao_selecionar_tabela)

        # Formulário Lateral
        frame_form = ttk.LabelFrame(paned, text=" Dados da Tabela ", padding=12)
        paned.add(frame_form, weight=2)

        ttk.Label(frame_form, text="Nome da Tabela:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.ent_tabela = ttk.Entry(frame_form, width=30)
        self.ent_tabela.pack(anchor=tk.W, fill=tk.X, pady=(0, 10))

        ttk.Label(frame_form, text="Próximo Código Sequencial:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.ent_proximo = ttk.Entry(frame_form, width=15)
        self.ent_proximo.pack(anchor=tk.W, fill=tk.X, pady=(0, 10))

        self.var_ativa = tk.BooleanVar(value=True)
        self.chk_ativa = ttk.Checkbutton(frame_form, text="Tabela Ativa no Sistema", variable=self.var_ativa)
        self.chk_ativa.pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(frame_form, text="Empresa Associada:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.lbl_empresa = ttk.Label(frame_form, text="(Todas as empresas / Padrão)", foreground="#4B5563")
        self.lbl_empresa.pack(anchor=tk.W, pady=(0, 15))

        # Botões
        bar_btns = ttk.Frame(frame_form)
        bar_btns.pack(fill=tk.X)

        ttk.Button(bar_btns, text="Salvar", command=self._salvar_alteracoes).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar_btns, text="Limpar", command=self._limpar_campos).pack(side=tk.RIGHT, padx=2)

    def carregar_tabelas(self):
        if not self.service:
            return
        filtro = self.ent_busca.get().strip()
        tabelas = self.service.listar_tabelas(filtro)

        self.tree.delete(*self.tree.get_children())
        for t in tabelas:
            status_desc = "Ativa" if t.is_ativa else "Inativa"
            emp_desc = f"{t.empcod} - {t.empnome}" if t.empcod else "(Geral)"
            self.tree.insert("", tk.END, values=(t.geotabela, t.proximo_codigo, status_desc, emp_desc))

    def _ao_selecionar_tabela(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        nome_tab = str(vals[0])

        if self.service:
            cfg = self.service.obter_config_cod(nome_tab)
            if cfg:
                self.ent_tabela.delete(0, tk.END)
                self.ent_tabela.insert(0, cfg.geotabela)
                self.ent_proximo.delete(0, tk.END)
                self.ent_proximo.insert(0, str(cfg.proximo_codigo))
                self.var_ativa.set(cfg.is_ativa)
                emp_str = f"{cfg.empcod} - {cfg.empnome}" if cfg.empcod else "(Geral)"
                self.lbl_empresa.config(text=emp_str)

    def _recarregar(self):
        self.ent_busca.delete(0, tk.END)
        self.carregar_tabelas()
        self._limpar_campos()

    def _limpar_campos(self):
        self.ent_tabela.delete(0, tk.END)
        self.ent_proximo.delete(0, tk.END)
        self.var_ativa.set(True)
        self.lbl_empresa.config(text="(Geral)")
        self.ent_tabela.focus_set()

    def _salvar_alteracoes(self):
        if not self.service:
            return

        tabela = self.ent_tabela.get().strip()
        if not tabela:
            messagebox.showwarning("Aviso", "Selecione ou informe a tabela a ser configurada.")
            return

        try:
            prox_cod = int(self.ent_proximo.get().strip())
        except ValueError:
            messagebox.showerror("Erro", "O próximo código deve ser um número inteiro válido.")
            return

        status = "S" if self.var_ativa.get() else "N"
        res = self.service.atualizar_config_cod(tabela, prox_cod, status)

        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.carregar_tabelas()
        else:
            messagebox.showerror("Erro", res.mensagem)


def abrir_manutencao_codigos_sistema(parent, connection=None):
    """Abre a tela de Manutenção de Códigos do Sistema em janela TopLevel."""
    win = tk.Toplevel(parent)
    win.title("Manutenção de Códigos do Sistema - GeoAlvo")
    win.geometry("820x480")
    win.minsize(680, 360)
    view = ManutencaoCodigosView(win, connection=connection)
    view.pack(fill=tk.BOTH, expand=True)
    return win
