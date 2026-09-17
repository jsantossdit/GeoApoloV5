"""
Interface Gráfica para Cadastro e Gestão de Departamentos e Seções.
GeoApolo V5
Clean Architecture: View desacoplada em Tkinter/ttk com suporte a execução headless.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from .models import DepartamentoDTO, ResultadoDepartamentoDTO
from .service import DepartamentosService


class DepartamentosView(ttk.Frame):
    """Tela de Cadastro e Manutenção de Departamentos e Seções da Empresa."""

    def __init__(self, parent=None, service: Optional[DepartamentosService] = None, connection=None):
        super().__init__(parent)
        self.service = service

        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from .repository import DepartamentosRepository
                conn = connection or obter_conexao_banco()
                self.service = DepartamentosService(DepartamentosRepository(conn))
            except Exception:
                pass

        self._setup_ui()
        if self.service:
            self.carregar_departamentos()

    def _setup_ui(self):
        # Header
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Cadastro de Departamentos e Seções",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
        ).pack(side=tk.LEFT)

        ttk.Label(
            header,
            text="Estrutura organizacional da empresa e vínculo com centros de controle Apolo",
            font=("Segoe UI", 9),
            foreground="#6B7280",
        ).pack(side=tk.LEFT, padx=15)

        # Barra de Filtros
        bar_filtro = ttk.Frame(self, padding=(10, 5))
        bar_filtro.pack(fill=tk.X)

        ttk.Label(bar_filtro, text="Buscar:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        self.ent_busca = ttk.Entry(bar_filtro, width=28)
        self.ent_busca.pack(side=tk.LEFT, padx=6)
        self.ent_busca.bind("<Return>", lambda e: self.carregar_departamentos())
        self.ent_busca.bind("<KeyRelease>", lambda e: self.carregar_departamentos())

        ttk.Button(bar_filtro, text="🔍 Buscar", command=self.carregar_departamentos).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar_filtro, text="🔄 Recarregar", command=self._recarregar).pack(side=tk.LEFT, padx=3)

        # PanedWindow
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Grid
        frame_grid = ttk.Frame(paned, padding=5)
        paned.add(frame_grid, weight=3)

        cols = ("cod", "nome", "empresa", "status", "cc")
        self.tree = ttk.Treeview(frame_grid, columns=cols, show="headings", height=15)
        self.tree.heading("cod", text="Código")
        self.tree.heading("nome", text="Nome do Departamento")
        self.tree.heading("empresa", text="Empresa")
        self.tree.heading("status", text="Status")
        self.tree.heading("cc", text="Centro de Custo")

        self.tree.column("cod", width=70, anchor=tk.CENTER)
        self.tree.column("nome", width=200)
        self.tree.column("empresa", width=120)
        self.tree.column("status", width=80, anchor=tk.CENTER)
        self.tree.column("cc", width=120)

        scroll = ttk.Scrollbar(frame_grid, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self._ao_selecionar_depto)

        # Formulário Lateral
        frame_form = ttk.LabelFrame(paned, text=" Dados do Departamento ", padding=12)
        paned.add(frame_form, weight=2)

        ttk.Label(frame_form, text="Código:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.ent_cod = ttk.Entry(frame_form, width=15)
        self.ent_cod.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))

        ttk.Label(frame_form, text="Nome do Departamento:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.ent_nome = ttk.Entry(frame_form, width=30)
        self.ent_nome.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))

        ttk.Label(frame_form, text="Código da Empresa:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.ent_empresa = ttk.Entry(frame_form, width=15)
        self.ent_empresa.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))
        self.ent_empresa.insert(0, "01")

        ttk.Label(frame_form, text="Centro de Custo/Controle (Apolo):", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.ent_cc = ttk.Entry(frame_form, width=20)
        self.ent_cc.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))

        self.var_ativo = tk.BooleanVar(value=True)
        self.chk_ativo = ttk.Checkbutton(frame_form, text="Departamento Ativo", variable=self.var_ativo)
        self.chk_ativo.pack(anchor=tk.W, pady=(0, 15))

        # Botões
        bar_btns = ttk.Frame(frame_form)
        bar_btns.pack(fill=tk.X)

        ttk.Button(bar_btns, text="Novo", command=self._novo_registro).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar_btns, text="Salvar", command=self._salvar_depto).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar_btns, text="Excluir", command=self._excluir_depto).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar_btns, text="Limpar", command=self._limpar_campos).pack(side=tk.RIGHT, padx=2)

    def carregar_departamentos(self):
        if not self.service:
            return
        filtro = self.ent_busca.get().strip()
        deptos = self.service.listar_departamentos(filtro=filtro)

        self.tree.delete(*self.tree.get_children())
        for d in deptos:
            status_desc = "Ativo" if d.is_ativo else "Inativo"
            emp_desc = f"{d.empcod} - {d.empnome}" if d.empnome else d.empcod
            cc_desc = f"{d.cctrlcodestr} - {d.cctrlnome}" if d.cctrlnome else d.cctrlcodestr
            self.tree.insert("", tk.END, values=(f"{d.codigo_departamento:03d}", d.nome_departamento, emp_desc, status_desc, cc_desc))

    def _ao_selecionar_depto(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        try:
            cod_val = int(vals[0])
        except ValueError:
            return

        if self.service:
            d = self.service.obter_departamento(cod_val)
            if d:
                self.ent_cod.delete(0, tk.END)
                self.ent_cod.insert(0, f"{d.codigo_departamento:03d}")
                self.ent_nome.delete(0, tk.END)
                self.ent_nome.insert(0, d.nome_departamento)
                self.ent_empresa.delete(0, tk.END)
                self.ent_empresa.insert(0, d.empcod or "01")
                self.ent_cc.delete(0, tk.END)
                self.ent_cc.insert(0, d.cctrlcodestr)
                self.var_ativo.set(d.is_ativo)

    def _limpar_campos(self):
        self.ent_cod.delete(0, tk.END)
        self.ent_nome.delete(0, tk.END)
        self.ent_empresa.delete(0, tk.END)
        self.ent_empresa.insert(0, "01")
        self.ent_cc.delete(0, tk.END)
        self.var_ativo.set(True)
        self.ent_nome.focus_set()

    def _novo_registro(self):
        self._limpar_campos()
        if self.service:
            prox = self.service.obter_proximo_codigo()
            self.ent_cod.insert(0, f"{prox:03d}")
        self.ent_nome.focus_set()

    def _recarregar(self):
        self.ent_busca.delete(0, tk.END)
        self.carregar_departamentos()
        self._limpar_campos()

    def _salvar_depto(self):
        if not self.service:
            return

        try:
            cod_val = int(self.ent_cod.get().strip() or 0)
        except ValueError:
            cod_val = 0

        nome = self.ent_nome.get().strip()
        emp = self.ent_empresa.get().strip() or "01"
        cc = self.ent_cc.get().strip()
        status = "A" if self.var_ativo.get() else "I"

        dto = DepartamentoDTO(
            codigo_departamento=cod_val,
            nome_departamento=nome,
            empcod=emp,
            flagativo=status,
            cctrlcodestr=cc,
        )

        res = self.service.salvar_departamento(dto)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.carregar_departamentos()
            self._limpar_campos()
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _excluir_depto(self):
        if not self.service:
            return

        try:
            cod_val = int(self.ent_cod.get().strip())
        except ValueError:
            messagebox.showwarning("Aviso", "Selecione um departamento válido para exclusão.")
            return

        nome = self.ent_nome.get().strip()
        if not messagebox.askyesno("Confirmação", f"Deseja realmente excluir o departamento '{nome}' (Cód: {cod_val})?"):
            return

        res = self.service.excluir_departamento(cod_val)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.carregar_departamentos()
            self._limpar_campos()
        else:
            messagebox.showerror("Erro", res.mensagem)


def abrir_janela_departamentos(parent, connection=None):
    """Abre a tela de Departamentos em janela TopLevel."""
    win = tk.Toplevel(parent)
    win.title("Gestão de Departamentos & Seções - GeoAlvo")
    win.geometry("860x500")
    win.minsize(700, 380)
    view = DepartamentosView(win, connection=connection)
    view.pack(fill=tk.BOTH, expand=True)
    return win
