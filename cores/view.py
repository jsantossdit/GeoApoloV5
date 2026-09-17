"""
Interface Gráfica para Cadastro de Cores de Produtos (Estoque Auxiliar).
GeoApolo V5
Clean Architecture: View desacoplada com suporte a execução headless e testes unitários.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from .models import CorDTO, ResultadoCorDTO
from .service import CoresService


class CoresView(ttk.Frame):
    """Tela de cadastro e manutenção de cores de produtos."""

    def __init__(self, parent=None, service: Optional[CoresService] = None, connection=None):
        super().__init__(parent)
        self.service = service

        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from .repository import CoresRepository
                conn = connection or obter_conexao_banco()
                self.service = CoresService(CoresRepository(conn))
            except Exception:
                pass

        self._setup_ui()
        if self.service:
            self.carregar_cores()

    def _setup_ui(self):
        # Header
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        lbl_titulo = ttk.Label(
            header,
            text="Cadastro de Cores de Produtos",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
        )
        lbl_titulo.pack(side=tk.LEFT)

        lbl_sub = ttk.Label(
            header,
            text="Tabela auxiliar de cores para o controle de estoque e produtos",
            font=("Segoe UI", 9),
            foreground="#6B7280",
        )
        lbl_sub.pack(side=tk.LEFT, padx=15)

        # PanedWindow
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Grade de Cores
        frame_grid = ttk.Frame(paned, padding=5)
        paned.add(frame_grid, weight=3)

        cols = ("cod", "desc")
        self.tree = ttk.Treeview(frame_grid, columns=cols, show="headings", height=15)
        self.tree.heading("cod", text="Código")
        self.tree.heading("desc", text="Descrição da Cor")

        self.tree.column("cod", width=80, anchor=tk.CENTER)
        self.tree.column("desc", width=250)

        scroll = ttk.Scrollbar(frame_grid, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self._ao_selecionar_cor)

        # Formulário Lateral
        frame_form = ttk.LabelFrame(paned, text=" Dados da Cor ", padding=12)
        paned.add(frame_form, weight=2)

        ttk.Label(frame_form, text="Código:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.ent_cod = ttk.Entry(frame_form, width=15)
        self.ent_cod.pack(anchor=tk.W, fill=tk.X, pady=(0, 10))

        ttk.Label(frame_form, text="Descrição da Cor:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.ent_desc = ttk.Entry(frame_form, width=30)
        self.ent_desc.pack(anchor=tk.W, fill=tk.X, pady=(0, 15))
        self.ent_desc.bind("<Return>", lambda e: self._salvar_cor())

        # Botões
        bar_btns = ttk.Frame(frame_form)
        bar_btns.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(bar_btns, text="Novo", command=self._novo_registro).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar_btns, text="Salvar", command=self._salvar_cor).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar_btns, text="Excluir", command=self._excluir_cor).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar_btns, text="Limpar", command=self._limpar_campos).pack(side=tk.RIGHT, padx=2)

    def carregar_cores(self):
        if not self.service:
            return
        cores = self.service.listar_cores()
        self.tree.delete(*self.tree.get_children())
        for c in cores:
            self.tree.insert("", tk.END, values=(f"{c.codigo_cor:03d}", c.descricao_cor))

    def _ao_selecionar_cor(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        self.ent_cod.delete(0, tk.END)
        self.ent_cod.insert(0, str(vals[0]))
        self.ent_desc.delete(0, tk.END)
        self.ent_desc.insert(0, str(vals[1]))

    def _limpar_campos(self):
        self.ent_cod.delete(0, tk.END)
        self.ent_desc.delete(0, tk.END)
        self.ent_desc.focus_set()

    def _novo_registro(self):
        self._limpar_campos()
        if self.service:
            prox = self.service.obter_proximo_codigo()
            self.ent_cod.insert(0, f"{prox:03d}")
        self.ent_desc.focus_set()

    def _salvar_cor(self):
        if not self.service:
            return
        try:
            cod_val = int(self.ent_cod.get().strip() or 0)
        except ValueError:
            cod_val = 0

        dto = CorDTO(codigo_cor=cod_val, descricao_cor=self.ent_desc.get().strip())
        res = self.service.salvar_cor(dto)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.carregar_cores()
            self._limpar_campos()
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _excluir_cor(self):
        if not self.service:
            return
        try:
            cod_val = int(self.ent_cod.get().strip())
        except ValueError:
            messagebox.showwarning("Aviso", "Selecione uma cor válida para exclusão.")
            return

        desc = self.ent_desc.get().strip()
        if not messagebox.askyesno("Confirmação", f"Deseja realmente excluir a cor '{desc}' (Cód: {cod_val})?"):
            return

        res = self.service.excluir_cor(cod_val)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.carregar_cores()
            self._limpar_campos()
        else:
            messagebox.showerror("Erro", res.mensagem)


def abrir_janela_cores(parent, connection=None):
    """Abre a tela de cadastro de cores em janela TopLevel."""
    win = tk.Toplevel(parent)
    win.title("Cores de Produtos - GeoAlvo")
    win.geometry("680x420")
    win.minsize(560, 320)
    view = CoresView(win, connection=connection)
    view.pack(fill=tk.BOTH, expand=True)
    return win
