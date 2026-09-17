"""
Interface Gráfica para Gestão de Empresas e Seleção de Contexto Corporativo (<F2>).
GeoApolo V5
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from empresas.models import EmpresaDTO, ResultadoEmpresaDTO
from empresas.service import EmpresasService


class EmpresasView(ttk.Frame):
    """View corporativa com abas para Seleção de Contexto Ativo e Cadastro de Empresas."""

    def __init__(self, parent=None, service: Optional[EmpresasService] = None, connection=None):
        super().__init__(parent)
        self.service = service
        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from empresas.repository import EmpresasRepository
                conn = connection or obter_conexao_banco()
                self.service = EmpresasService(EmpresasRepository(conn))
            except Exception:
                pass

        self._setup_ui()
        if self.service:
            self.carregar_empresas()

    def _setup_ui(self):
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        lbl_titulo = ttk.Label(
            header,
            text="Multi-Empresas e Contexto Corporativo",
            font=("Segoe UI", 13, "bold"),
            foreground="#1E3A8A"
        )
        lbl_titulo.pack(side=tk.LEFT)

        lbl_sub = ttk.Label(
            header,
            text="Seleção rápida de filial ativa (<F2>) e manutenção da estrutura corporativa",
            font=("Segoe UI", 9),
            foreground="#6B7280"
        )
        lbl_sub.pack(side=tk.LEFT, padx=15)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tab_selecao = ttk.Frame(self.notebook, padding=10)
        self.tab_cadastro = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_selecao, text="  Selecionar Empresa Ativa (<F2>)  ")
        self.notebook.add(self.tab_cadastro, text="  Cadastro de Empresas & Filiais  ")

        self._build_tab_selecao()
        self._build_tab_cadastro()

    def _build_tab_selecao(self):
        status_box = ttk.Frame(self.tab_selecao, padding=5)
        status_box.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(status_box, text="Empresa Ativa Atual:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        self.lbl_emp_ativa = ttk.Label(status_box, text="Nenhuma selecionada", font=("Segoe UI", 10), foreground="#2563EB")
        self.lbl_emp_ativa.pack(side=tk.LEFT)

        cols = ("cod", "nome")
        self.tree_selecao = ttk.Treeview(self.tab_selecao, columns=cols, show="headings", selectmode="browse")
        self.tree_selecao.heading("cod", text="Código")
        self.tree_selecao.heading("nome", text="Razão Social / Filial")
        self.tree_selecao.column("cod", width=90, anchor=tk.CENTER)
        self.tree_selecao.column("nome", width=400)
        self.tree_selecao.pack(fill=tk.BOTH, expand=True, pady=5)
        self.tree_selecao.bind("<Double-1>", lambda e: self._selecionar_ativa())

        btn_box = ttk.Frame(self.tab_selecao, padding=5)
        btn_box.pack(fill=tk.X, pady=5)

        ttk.Button(btn_box, text="Definir Selecionada como Empresa Ativa", command=self._selecionar_ativa).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_box, text="Atualizar Lista", command=self.carregar_empresas).pack(side=tk.LEFT)

    def _build_tab_cadastro(self):
        paned = ttk.PanedWindow(self.tab_cadastro, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(paned, padding=5)
        paned.add(left, weight=1)

        cols = ("cod", "nome")
        self.tree_cad = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        self.tree_cad.heading("cod", text="Código")
        self.tree_cad.heading("nome", text="Nome da Empresa")
        self.tree_cad.column("cod", width=80, anchor=tk.CENTER)
        self.tree_cad.column("nome", width=250)
        self.tree_cad.pack(fill=tk.BOTH, expand=True, pady=5)
        self.tree_cad.bind("<<TreeviewSelect>>", self._on_cad_select)

        right = ttk.Frame(paned, padding=10)
        paned.add(right, weight=1)

        ttk.Label(right, text="Ficha da Empresa", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))

        f_grid = ttk.Frame(right)
        f_grid.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(f_grid, text="Código:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.ent_cod = ttk.Entry(f_grid, width=12)
        self.ent_cod.grid(row=0, column=1, sticky=tk.W, padx=5, pady=3)

        ttk.Label(f_grid, text="Razão Social / Nome:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.ent_nome = ttk.Entry(f_grid, width=32)
        self.ent_nome.grid(row=1, column=1, sticky=tk.W, padx=5, pady=3)

        btn_box = ttk.Frame(right)
        btn_box.pack(fill=tk.X, pady=(0, 15))

        ttk.Button(btn_box, text="Nova", command=self._nova_empresa).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_box, text="Salvar Empresa", command=self._salvar_empresa).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_box, text="Excluir Empresa", command=self._excluir_empresa).pack(side=tk.LEFT)

        sep = ttk.Separator(right, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X, pady=10)

        ttk.Label(right, text="Integração Apolo ERP", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        ttk.Label(right, text="Sincroniza automaticamente as filiais cadastradas na tabela principal 'empresa_filial':").pack(anchor=tk.W, pady=(0, 5))

        ttk.Button(right, text="Sincronizar Filiais do Apolo", command=self._sincronizar_apolo).pack(anchor=tk.W)

    def carregar_empresas(self):
        for item in self.tree_selecao.get_children():
            self.tree_selecao.delete(item)
        for item in self.tree_cad.get_children():
            self.tree_cad.delete(item)

        if not self.service:
            return

        empresas = self.service.listar_empresas()
        for e in empresas:
            self.tree_selecao.insert("", tk.END, values=(e.empcod, e.empnome))
            self.tree_cad.insert("", tk.END, values=(e.empcod, e.empnome))

        ativa = self.service.obter_empresa_ativa()
        if ativa:
            self.lbl_emp_ativa.config(text=ativa.display_completo, foreground="#16A34A")
        else:
            self.lbl_emp_ativa.config(text="Nenhuma selecionada", foreground="#DC2626")

    def _selecionar_ativa(self):
        sel = self.tree_selecao.selection()
        if not sel or not self.service:
            messagebox.showwarning("Aviso", "Selecione uma empresa da lista.")
            return

        cod = self.tree_selecao.item(sel[0], "values")[0]
        res = self.service.selecionar_empresa_ativa(cod)
        if res.sucesso:
            messagebox.showinfo("Empresa Ativa", res.mensagem)
            self.carregar_empresas()
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _on_cad_select(self, event):
        sel = self.tree_cad.selection()
        if not sel:
            return
        vals = self.tree_cad.item(sel[0], "values")
        self.ent_cod.delete(0, tk.END)
        self.ent_cod.insert(0, vals[0])
        self.ent_nome.delete(0, tk.END)
        self.ent_nome.insert(0, vals[1])

    def _nova_empresa(self):
        self.ent_cod.delete(0, tk.END)
        self.ent_nome.delete(0, tk.END)

    def _salvar_empresa(self):
        if not self.service:
            return
        cod = self.ent_cod.get().strip()
        nome = self.ent_nome.get().strip()
        res = self.service.salvar_empresa(EmpresaDTO(empcod=cod, empnome=nome))
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.carregar_empresas()
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _excluir_empresa(self):
        if not self.service:
            return
        cod = self.ent_cod.get().strip()
        if not cod:
            messagebox.showwarning("Aviso", "Selecione uma empresa para exclusão.")
            return

        if not messagebox.askyesno("Confirmação", f"Excluir a empresa '{cod}'?"):
            return

        res = self.service.excluir_empresa(cod)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self._nova_empresa()
            self.carregar_empresas()
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _sincronizar_apolo(self):
        if not self.service:
            return
        res = self.service.sincronizar_empresas()
        if res.sucesso:
            messagebox.showinfo("Sincronização", res.mensagem)
            self.carregar_empresas()
        else:
            messagebox.showerror("Erro", res.mensagem)
