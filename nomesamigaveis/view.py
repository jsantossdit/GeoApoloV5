"""
Interface Gráfica para Dicionário de Nomes Amigáveis de Objetos e Controles.
GeoApolo V5
Clean Architecture: View desacoplada em Tkinter/ttk com suporte a execução headless.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from .models import ObjetoSistemaDTO, ResultadoNomesAmigaveisDTO
from .service import NomesAmigaveisService


class NomesAmigaveisView(ttk.Frame):
    """Tela para consulta, edição e sugestão de nomes amigáveis de telas e componentes."""

    def __init__(self, parent=None, service: Optional[NomesAmigaveisService] = None, connection=None):
        super().__init__(parent)
        self.service = service

        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from .repository import NomesAmigaveisRepository
                conn = connection or obter_conexao_banco()
                self.service = NomesAmigaveisService(NomesAmigaveisRepository(conn))
            except Exception:
                pass

        self._setup_ui()
        if self.service:
            self._carregar_categorias()
            self.carregar_objetos()

    def _setup_ui(self):
        # Header
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Dicionário de Nomes Amigáveis",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
        ).pack(side=tk.LEFT)

        ttk.Label(
            header,
            text="Tradução e humanização de nomes de telas, menus e botões para usuários finais",
            font=("Segoe UI", 9),
            foreground="#6B7280",
        ).pack(side=tk.LEFT, padx=15)

        # Barra de Filtros
        bar_filtro = ttk.Frame(self, padding=(10, 5))
        bar_filtro.pack(fill=tk.X)

        ttk.Label(bar_filtro, text="Categoria:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        self.cbo_filtro_cat = ttk.Combobox(bar_filtro, state="readonly", width=18)
        self.cbo_filtro_cat.pack(side=tk.LEFT, padx=5)
        self.cbo_filtro_cat.bind("<<ComboboxSelected>>", lambda e: self.carregar_objetos())

        ttk.Label(bar_filtro, text="Buscar:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(10, 0))
        self.ent_busca = ttk.Entry(bar_filtro, width=25)
        self.ent_busca.pack(side=tk.LEFT, padx=5)
        self.ent_busca.bind("<Return>", lambda e: self.carregar_objetos())
        self.ent_busca.bind("<KeyRelease>", lambda e: self.carregar_objetos())

        ttk.Button(bar_filtro, text="🔍 Buscar", command=self.carregar_objetos).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar_filtro, text="🔄 Recarregar", command=self._recarregar).pack(side=tk.LEFT, padx=3)

        # PanedWindow
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Grid de Objetos
        frame_grid = ttk.Frame(paned, padding=5)
        paned.add(frame_grid, weight=3)

        cols = ("objeto", "amigavel", "categoria")
        self.tree = ttk.Treeview(frame_grid, columns=cols, show="headings", height=16)
        self.tree.heading("objeto", text="Objeto Técnico (Componente)")
        self.tree.heading("amigavel", text="Nome Amigável")
        self.tree.heading("categoria", text="Categoria")

        self.tree.column("objeto", width=220)
        self.tree.column("amigavel", width=220)
        self.tree.column("categoria", width=120, anchor=tk.CENTER)

        scroll = ttk.Scrollbar(frame_grid, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self._ao_selecionar_objeto)

        # Formulário Lateral
        frame_form = ttk.LabelFrame(paned, text=" Edição do Objeto ", padding=12)
        paned.add(frame_form, weight=2)

        ttk.Label(frame_form, text="Objeto Técnico:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.ent_objeto = ttk.Entry(frame_form, width=35)
        self.ent_objeto.pack(anchor=tk.W, fill=tk.X, pady=(0, 10))

        ttk.Label(frame_form, text="Nome Amigável:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.ent_amigavel = ttk.Entry(frame_form, width=35)
        self.ent_amigavel.pack(anchor=tk.W, fill=tk.X, pady=(0, 5))

        btn_sugerir_um = ttk.Button(frame_form, text="✨ Sugerir Nome para este Item", command=self._sugerir_nome_atual)
        btn_sugerir_um.pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(frame_form, text="Categoria:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.ent_categoria = ttk.Entry(frame_form, width=25)
        self.ent_categoria.pack(anchor=tk.W, fill=tk.X, pady=(0, 15))

        # Botões de Ação
        bar_btns = ttk.Frame(frame_form)
        bar_btns.pack(fill=tk.X, pady=(0, 15))

        ttk.Button(bar_btns, text="Salvar", command=self._salvar_alteracao).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar_btns, text="Limpar", command=self._limpar_campos).pack(side=tk.RIGHT, padx=2)

        ttk.Separator(frame_form, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Automação de Lote
        ttk.Label(frame_form, text="Ações em Lote:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 5))
        btn_sugerir_todos = ttk.Button(
            frame_form,
            text="⚡ Gerar Sugestões para Itens Não Editados",
            command=self._gerar_sugestoes_lote,
        )
        btn_sugerir_todos.pack(fill=tk.X)

    def _carregar_categorias(self):
        if not self.service:
            return
        cats = self.service.listar_categorias()
        opcoes = ["Todas as Categorias"] + cats
        self.cbo_filtro_cat["values"] = opcoes
        self.cbo_filtro_cat.set("Todas as Categorias")

    def carregar_objetos(self):
        if not self.service:
            return

        cat = self.cbo_filtro_cat.get().strip()
        if cat == "Todas as Categorias":
            cat = ""
        filtro = self.ent_busca.get().strip()

        objetos = self.service.listar_objetos(categoria=cat, filtro=filtro)
        self.tree.delete(*self.tree.get_children())
        for obj in objetos:
            self.tree.insert("", tk.END, values=(obj.nome_objeto, obj.nome_amigavel, obj.categoria))

    def _ao_selecionar_objeto(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        self.ent_objeto.delete(0, tk.END)
        self.ent_objeto.insert(0, str(vals[0]))
        self.ent_amigavel.delete(0, tk.END)
        self.ent_amigavel.insert(0, str(vals[1]))
        self.ent_categoria.delete(0, tk.END)
        self.ent_categoria.insert(0, str(vals[2]))

    def _sugerir_nome_atual(self):
        if not self.service:
            return
        nome_tec = self.ent_objeto.get().strip()
        if not nome_tec:
            messagebox.showwarning("Aviso", "Informe ou selecione um objeto técnico.")
            return
        sugestao = self.service.sugerir_nome_amigavel(nome_tec)
        self.ent_amigavel.delete(0, tk.END)
        self.ent_amigavel.insert(0, sugestao)

    def _limpar_campos(self):
        self.ent_objeto.delete(0, tk.END)
        self.ent_amigavel.delete(0, tk.END)
        self.ent_categoria.delete(0, tk.END)
        self.ent_objeto.focus_set()

    def _recarregar(self):
        self.ent_busca.delete(0, tk.END)
        self.cbo_filtro_cat.set("Todas as Categorias")
        self._carregar_categorias()
        self.carregar_objetos()
        self._limpar_campos()

    def _salvar_alteracao(self):
        if not self.service:
            return

        nome_tec = self.ent_objeto.get().strip()
        nome_ami = self.ent_amigavel.get().strip()
        categ = self.ent_categoria.get().strip() or "Geral"

        if not nome_tec:
            messagebox.showwarning("Aviso", "Nome técnico do objeto é obrigatório.")
            return

        dto = ObjetoSistemaDTO(nome_objeto=nome_tec, nome_amigavel=nome_ami, categoria=categ)
        res = self.service.salvar_objeto(dto)

        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.carregar_objetos()
            self._carregar_categorias()
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _gerar_sugestoes_lote(self):
        if not self.service:
            return

        if not messagebox.askyesno(
            "Confirmação",
            "Deseja gerar sugestões automáticas de nomes amigáveis para todos os objetos que ainda não foram personalizados?",
        ):
            return

        res = self.service.gerar_sugestoes_automaticas(apenas_nao_editados=True)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.carregar_objetos()
        else:
            messagebox.showerror("Erro", res.mensagem)


def abrir_janela_nomes_amigaveis(parent, connection=None):
    """Abre a tela de Dicionário de Nomes Amigáveis em janela TopLevel."""
    win = tk.Toplevel(parent)
    win.title("Dicionário de Nomes Amigáveis - GeoAlvo")
    win.geometry("900x540")
    win.minsize(720, 400)
    view = NomesAmigaveisView(win, connection=connection)
    view.pack(fill=tk.BOTH, expand=True)
    return win
