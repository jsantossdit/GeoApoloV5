"""
Interface Gráfica para Cadastro de Marcas de Produtos (Estoque Auxiliar).
GeoApolo V5
Clean Architecture: View desacoplada com suporte a execução headless e testes unitários.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from core import centralizar_janela, vincular_maiusculo, configurar_navegacao_enter
from .models import MarcaDTO, ResultadoMarcaDTO
from .service import MarcasService


class MarcasView(ttk.Frame):
    """Tela de cadastro e manutenção de marcas de produtos."""

    def __init__(self, parent=None, service: Optional[MarcasService] = None, connection=None):
        super().__init__(parent)
        self.service = service

        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from .repository import MarcasRepository
                conn = connection or obter_conexao_banco()
                self.service = MarcasService(MarcasRepository(conn))
            except Exception:
                pass

        self._setup_ui()
        self._configurar_atalhos()
        if self.service:
            self.carregar_marcas()

    def _setup_ui(self):
        # Header
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        lbl_titulo = ttk.Label(
            header,
            text="Cadastro de Marcas de Produtos",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
        )
        lbl_titulo.pack(side=tk.LEFT)

        lbl_sub = ttk.Label(
            header,
            text="Tabela auxiliar de marcas de produtos para controle de estoque e catálogo",
            font=("Segoe UI", 9),
            foreground="#6B7280",
        )
        lbl_sub.pack(side=tk.LEFT, padx=15)

        # PanedWindow
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Painel Esquerdo: Grade de Marcas
        frame_grid = ttk.Frame(paned, padding=5)
        paned.add(frame_grid, weight=3)

        # Barra de Pesquisa rápida
        f_busca = ttk.Frame(frame_grid)
        f_busca.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(f_busca, text="Buscar:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.var_busca = tk.StringVar()
        vincular_maiusculo(self.var_busca)
        self.ent_busca = ttk.Entry(f_busca, textvariable=self.var_busca, width=20)
        self.ent_busca.pack(side=tk.LEFT, padx=(0, 6))
        self.ent_busca.bind("<Return>", lambda e: self.carregar_marcas())

        ttk.Button(f_busca, text="Filtrar", command=self.carregar_marcas, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(f_busca, text="Todas", command=self._limpar_busca, width=7).pack(side=tk.LEFT, padx=2)

        cols = ("cod", "desc")
        self.tree = ttk.Treeview(frame_grid, columns=cols, show="headings", height=15)
        self.tree.heading("cod", text="Código")
        self.tree.heading("desc", text="Descrição da Marca")

        self.tree.column("cod", width=80, anchor=tk.CENTER)
        self.tree.column("desc", width=260)

        scroll = ttk.Scrollbar(frame_grid, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self._ao_selecionar_marca)

        # Painel Direito: Formulário de Cadastro
        frame_form = ttk.LabelFrame(paned, text=" Dados da Marca ", padding=12)
        paned.add(frame_form, weight=2)

        ttk.Label(frame_form, text="Código Interno:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.ent_cod = ttk.Entry(frame_form, width=15)
        self.ent_cod.pack(anchor=tk.W, fill=tk.X, pady=(0, 10))

        ttk.Label(frame_form, text="Descrição da Marca (*):", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_desc = tk.StringVar()
        vincular_maiusculo(self.var_desc)
        self.ent_desc = ttk.Entry(frame_form, textvariable=self.var_desc, width=30)
        self.ent_desc.pack(anchor=tk.W, fill=tk.X, pady=(0, 15))

        # Configura navegação com a tecla Enter
        configurar_navegacao_enter([self.ent_cod, self.ent_desc])
        self.ent_desc.bind("<Return>", lambda e: self._salvar_marca())

        # Botões de Ação com atalhos padronizados
        bar_btns = ttk.Frame(frame_form)
        bar_btns.pack(fill=tk.X, pady=(5, 0))

        self.btn_novo = ttk.Button(bar_btns, text="Novo <F2>", command=self._novo_registro)
        self.btn_novo.pack(side=tk.LEFT, padx=2)

        self.btn_salvar = ttk.Button(bar_btns, text="Salvar <F3>", command=self._salvar_marca)
        self.btn_salvar.pack(side=tk.LEFT, padx=2)

        self.btn_excluir = ttk.Button(bar_btns, text="Excluir <F5>", command=self._excluir_marca)
        self.btn_excluir.pack(side=tk.LEFT, padx=2)

        self.btn_limpar = ttk.Button(bar_btns, text="Limpar <F6>", command=self._limpar_campos)
        self.btn_limpar.pack(side=tk.RIGHT, padx=2)

    def _configurar_atalhos(self):
        """Associa atalhos de teclado F2, F3, F5, F6 e Alt aos botões."""
        top = self.winfo_toplevel()
        top.bind("<F2>", lambda e: self._novo_registro())
        top.bind("<F3>", lambda e: self._salvar_marca())
        top.bind("<F5>", lambda e: self._excluir_marca())
        top.bind("<F6>", lambda e: self._limpar_campos())
        top.bind("<Alt-i>", lambda e: self._novo_registro())
        top.bind("<Alt-I>", lambda e: self._novo_registro())
        top.bind("<Alt-g>", lambda e: self._salvar_marca())
        top.bind("<Alt-G>", lambda e: self._salvar_marca())
        top.bind("<Alt-e>", lambda e: self._excluir_marca())
        top.bind("<Alt-E>", lambda e: self._excluir_marca())
        top.bind("<Alt-c>", lambda e: self._limpar_campos())
        top.bind("<Alt-C>", lambda e: self._limpar_campos())

    def carregar_marcas(self):
        if not self.service:
            return
        filtro = self.var_busca.get().strip().upper()
        marcas = self.service.listar_marcas()
        self.tree.delete(*self.tree.get_children())
        for m in marcas:
            if filtro and filtro not in m.descricao_marca.upper() and filtro != str(m.codigo_marca):
                continue
            self.tree.insert("", tk.END, values=(f"{m.codigo_marca:03d}", m.descricao_marca))

    def _limpar_busca(self):
        self.var_busca.set("")
        self.carregar_marcas()

    def _ao_selecionar_marca(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        self.ent_cod.delete(0, tk.END)
        self.ent_cod.insert(0, str(vals[0]))
        self.var_desc.set(str(vals[1]))

    def _limpar_campos(self):
        self.ent_cod.delete(0, tk.END)
        self.var_desc.set("")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())
        self.ent_desc.focus_set()

    def _novo_registro(self):
        self._limpar_campos()
        if self.service:
            prox = self.service.obter_proximo_codigo()
            self.ent_cod.insert(0, f"{prox:03d}")
        self.ent_desc.focus_set()

    def _salvar_marca(self):
        if not self.service:
            return
        try:
            cod_val = int(self.ent_cod.get().strip() or 0)
        except ValueError:
            cod_val = 0

        desc = self.var_desc.get().strip().upper()
        if not desc:
            messagebox.showwarning("Aviso", "A descrição da marca é obrigatória.", parent=self)
            self.ent_desc.focus_set()
            return

        dto = MarcaDTO(codigo_marca=cod_val, descricao_marca=desc)
        res = self.service.salvar_marca(dto)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem, parent=self)
            self.carregar_marcas()
            self._limpar_campos()
        else:
            messagebox.showerror("Erro ao Salvar", res.mensagem, parent=self)

    def _excluir_marca(self):
        if not self.service:
            return
        try:
            cod_val = int(self.ent_cod.get().strip())
        except ValueError:
            messagebox.showwarning("Aviso", "Selecione uma marca cadastrada para exclusão.", parent=self)
            return

        desc = self.var_desc.get().strip().upper()
        if not messagebox.askyesno(
            "Confirmação de Exclusão",
            f"Deseja realmente excluir a marca '{desc}' (Código: {cod_val})?",
            parent=self
        ):
            return

        res = self.service.excluir_marca(cod_val)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem, parent=self)
            self.carregar_marcas()
            self._limpar_campos()
        else:
            messagebox.showerror("Erro ao Excluir", res.mensagem, parent=self)


def abrir_janela_marcas(parent, connection=None):
    """Abre a tela de cadastro de marcas em janela TopLevel centralizada."""
    win = tk.Toplevel(parent)
    win.title("Marcas de Produtos - GeoAlvo")
    win.minsize(580, 340)
    centralizar_janela(win, parent, 720, 440)
    view = MarcasView(win, connection=connection)
    view.pack(fill=tk.BOTH, expand=True)
    return win
