"""
Interface Gráfica para Unificação e Mesclagem de Cadastros (MatchCode).
GeoApolo V5
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from matchcode.models import ResultadoMatchCodeDTO
from matchcode.service import MatchCodeService


class MatchCodeView(ttk.Frame):
    """Tela corporativa para mesclagem de usuários e entidades duplicadas."""

    def __init__(self, parent=None, service: Optional[MatchCodeService] = None, connection=None):
        super().__init__(parent)
        self.service = service
        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from matchcode.repository import MatchCodeRepository
                conn = connection or obter_conexao_banco()
                self.service = MatchCodeService(MatchCodeRepository(conn))
            except Exception:
                pass

        self._setup_ui()

    def _setup_ui(self):
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        lbl_titulo = ttk.Label(
            header,
            text="Unificação de Cadastros Duplicados (MatchCode)",
            font=("Segoe UI", 13, "bold"),
            foreground="#1E3A8A"
        )
        lbl_titulo.pack(side=tk.LEFT)

        lbl_sub = ttk.Label(
            header,
            text="Mesclagem segura de históricos e expurgo de duplicidades com garantia transacional",
            font=("Segoe UI", 9),
            foreground="#6B7280"
        )
        lbl_sub.pack(side=tk.LEFT, padx=15)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tab_usuarios = ttk.Frame(self.notebook, padding=15)
        self.tab_entidades = ttk.Frame(self.notebook, padding=15)

        self.notebook.add(self.tab_usuarios, text="  MatchCode Usuários  ")
        self.notebook.add(self.tab_entidades, text="  MatchCode Entidades & Contatos  ")

        self._build_tab_usuarios()
        self._build_tab_entidades()

    def _build_tab_usuarios(self):
        box_orig = ttk.LabelFrame(self.tab_usuarios, text=" Usuário de Origem (A ser mesclado e excluído) ", padding=10)
        box_orig.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(box_orig, text="Código / Usucod:").grid(row=0, column=0, sticky=tk.W)
        self.ent_user_orig = ttk.Entry(box_orig, width=15)
        self.ent_user_orig.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.ent_user_orig.bind("<FocusOut>", lambda e: self._validar_user_origem())

        ttk.Button(box_orig, text="Verificar", command=self._validar_user_origem).grid(row=0, column=2, padx=5)
        self.lbl_user_orig_desc = ttk.Label(box_orig, text="---", font=("Segoe UI", 9, "italic"))
        self.lbl_user_orig_desc.grid(row=0, column=3, sticky=tk.W, padx=10)

        box_dest = ttk.LabelFrame(self.tab_usuarios, text=" Usuário de Destino (Cadastro definitivo a ser mantido) ", padding=10)
        box_dest.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(box_dest, text="Código / Usucod:").grid(row=0, column=0, sticky=tk.W)
        self.ent_user_dest = ttk.Entry(box_dest, width=15)
        self.ent_user_dest.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.ent_user_dest.bind("<FocusOut>", lambda e: self._validar_user_destino())

        ttk.Button(box_dest, text="Verificar", command=self._validar_user_destino).grid(row=0, column=2, padx=5)
        self.lbl_user_dest_desc = ttk.Label(box_dest, text="---", font=("Segoe UI", 9, "italic"))
        self.lbl_user_dest_desc.grid(row=0, column=3, sticky=tk.W, padx=10)

        btn_unif = ttk.Button(self.tab_usuarios, text="Executar Unificação de Usuários", command=self._unificar_usuarios)
        btn_unif.pack(anchor=tk.W, pady=5)

        self.lbl_user_status = ttk.Label(self.tab_usuarios, text="", font=("Segoe UI", 9, "bold"))
        self.lbl_user_status.pack(anchor=tk.W, pady=5)

    def _build_tab_entidades(self):
        box_orig = ttk.LabelFrame(self.tab_entidades, text=" Entidade de Origem (A ser mesclada e inativada) ", padding=10)
        box_orig.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(box_orig, text="Código da Entidade:").grid(row=0, column=0, sticky=tk.W)
        self.ent_ent_orig = ttk.Entry(box_orig, width=15)
        self.ent_ent_orig.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.ent_ent_orig.bind("<FocusOut>", lambda e: self._validar_ent_origem())

        ttk.Button(box_orig, text="Verificar", command=self._validar_ent_origem).grid(row=0, column=2, padx=5)
        self.lbl_ent_orig_desc = ttk.Label(box_orig, text="---", font=("Segoe UI", 9, "italic"))
        self.lbl_ent_orig_desc.grid(row=0, column=3, sticky=tk.W, padx=10)

        box_dest = ttk.LabelFrame(self.tab_entidades, text=" Entidade de Destino (Cadastro definitivo a ser mantido) ", padding=10)
        box_dest.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(box_dest, text="Código da Entidade:").grid(row=0, column=0, sticky=tk.W)
        self.ent_ent_dest = ttk.Entry(box_dest, width=15)
        self.ent_ent_dest.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.ent_ent_dest.bind("<FocusOut>", lambda e: self._validar_ent_destino())

        ttk.Button(box_dest, text="Verificar", command=self._validar_ent_destino).grid(row=0, column=2, padx=5)
        self.lbl_ent_dest_desc = ttk.Label(box_dest, text="---", font=("Segoe UI", 9, "italic"))
        self.lbl_ent_dest_desc.grid(row=0, column=3, sticky=tk.W, padx=10)

        btn_unif = ttk.Button(self.tab_entidades, text="Executar Unificação de Entidades", command=self._unificar_entidades)
        btn_unif.pack(anchor=tk.W, pady=5)

        self.lbl_ent_status = ttk.Label(self.tab_entidades, text="", font=("Segoe UI", 9, "bold"))
        self.lbl_ent_status.pack(anchor=tk.W, pady=5)

    def _validar_user_origem(self):
        if not self.service:
            return
        cod = self.ent_user_orig.get().strip()
        u = self.service.obter_usuario(cod)
        if u:
            self.lbl_user_orig_desc.config(text=f"{u[1]} (Status: {u[2]})", foreground="#16A34A")
        else:
            self.lbl_user_orig_desc.config(text="Não localizado", foreground="#DC2626")

    def _validar_user_destino(self):
        if not self.service:
            return
        cod = self.ent_user_dest.get().strip()
        u = self.service.obter_usuario(cod)
        if u:
            self.lbl_user_dest_desc.config(text=f"{u[1]} (Status: {u[2]})", foreground="#16A34A")
        else:
            self.lbl_user_dest_desc.config(text="Não localizado", foreground="#DC2626")

    def _unificar_usuarios(self):
        if not self.service:
            return
        orig = self.ent_user_orig.get().strip()
        dest = self.ent_user_dest.get().strip()

        if not messagebox.askyesno(
            "Confirmação Irreversível",
            f"Deseja realmente migrar todos os dados do usuário '{orig}' para '{dest}'?\nO usuário de origem será removido permanentemente."
        ):
            return

        res = self.service.unificar_usuarios(orig, dest)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.lbl_user_status.config(text=res.mensagem, foreground="#16A34A")
            self.ent_user_orig.delete(0, tk.END)
            self.lbl_user_orig_desc.config(text="---")
        else:
            messagebox.showerror("Erro", res.mensagem)
            self.lbl_user_status.config(text=res.mensagem, foreground="#DC2626")

    def _validar_ent_origem(self):
        if not self.service:
            return
        cod = self.ent_ent_orig.get().strip()
        e = self.service.obter_entidade(cod)
        if e:
            self.lbl_ent_orig_desc.config(text=e[1], foreground="#16A34A")
        else:
            self.lbl_ent_orig_desc.config(text="Não localizada", foreground="#DC2626")

    def _validar_ent_destino(self):
        if not self.service:
            return
        cod = self.ent_ent_dest.get().strip()
        e = self.service.obter_entidade(cod)
        if e:
            self.lbl_ent_dest_desc.config(text=e[1], foreground="#16A34A")
        else:
            self.lbl_ent_dest_desc.config(text="Não localizada", foreground="#DC2626")

    def _unificar_entidades(self):
        if not self.service:
            return
        orig = self.ent_ent_orig.get().strip()
        dest = self.ent_ent_dest.get().strip()

        if not messagebox.askyesno(
            "Confirmação Irreversível",
            f"Deseja transferir todos os títulos e cadastros da entidade '{orig}' para '{dest}'?\nA entidade de origem será removida."
        ):
            return

        res = self.service.unificar_entidades(orig, dest)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.lbl_ent_status.config(text=res.mensagem, foreground="#16A34A")
            self.ent_ent_orig.delete(0, tk.END)
            self.lbl_ent_orig_desc.config(text="---")
        else:
            messagebox.showerror("Erro", res.mensagem)
            self.lbl_ent_status.config(text=res.mensagem, foreground="#DC2626")
