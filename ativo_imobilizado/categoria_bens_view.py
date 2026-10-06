"""
Interface Gráfica para Cadastro e Manutenção de Categorias de Bens (Ativo Fixo).
GeoApolo V5
Equivalente funcional à gestão de categorias de bens do módulo SATFI em Delphi.
Tabela: USER_geoapolo_satfi_categorias
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from core import centralizar_janela, vincular_maiusculo, configurar_navegacao_enter
from ativo_imobilizado.repository import AtivoImobilizadoRepository


class CategoriaBensView(ttk.Frame):
    """Tela de manutenção de categorias de bens patrimoniais."""

    def __init__(self, parent=None, repo: Optional[AtivoImobilizadoRepository] = None, connection=None):
        super().__init__(parent)
        self.repo = repo or AtivoImobilizadoRepository(connection)
        self._setup_ui()
        self._configurar_atalhos()
        self.carregar_categorias()
        self._novo_registro()

    def _setup_ui(self):
        # Header superior
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Cadastro de Categoria de Bens (Ativo Fixo)",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
        ).pack(side=tk.LEFT)

        self.lbl_total = ttk.Label(
            header,
            text="0 categoria(s)",
            font=("Segoe UI", 9, "bold"),
            foreground="#475569",
        )
        self.lbl_total.pack(side=tk.RIGHT)

        # Divisão em duas colunas (Esquerda: Lista / Direita: Formulário)
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # -------------------------------------------------------------
        # Painel Esquerdo: Lista de Categorias
        # -------------------------------------------------------------
        f_left = ttk.Frame(paned, padding=6)
        paned.add(f_left, weight=3)

        f_busca = ttk.Frame(f_left)
        f_busca.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(f_busca, text="Buscar:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_busca = tk.StringVar()
        vincular_maiusculo(self.var_busca)
        ent_b = ttk.Entry(f_busca, textvariable=self.var_busca, width=22)
        ent_b.pack(side=tk.LEFT, padx=(0, 6), fill=tk.X, expand=True)
        ent_b.bind("<Return>", lambda e: self.carregar_categorias())

        btn_filtrar = ttk.Button(f_busca, text="Filtrar", command=self.carregar_categorias, width=8)
        btn_filtrar.pack(side=tk.LEFT, padx=2)

        btn_todos = ttk.Button(f_busca, text="Todos", command=self._limpar_filtro, width=7)
        btn_todos.pack(side=tk.LEFT, padx=2)

        cols = ("cod", "descricao")
        self.tree = ttk.Treeview(f_left, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("cod", text="Código")
        self.tree.heading("descricao", text="Descrição da Categoria")
        self.tree.column("cod", width=80, anchor=tk.CENTER)
        self.tree.column("descricao", width=260, anchor=tk.W)

        sb_y = ttk.Scrollbar(f_left, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb_y.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self._ao_selecionar)

        # -------------------------------------------------------------
        # Painel Direito: Edição / Cadastro
        # -------------------------------------------------------------
        f_right = ttk.Frame(paned, padding=8)
        paned.add(f_right, weight=2)

        box_form = ttk.LabelFrame(f_right, text=" Detalhes da Categoria ", padding=12)
        box_form.pack(fill=tk.BOTH, expand=True)

        ttk.Label(box_form, text="Código da Categoria: *", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_codigo = tk.StringVar()
        self.ent_codigo = ttk.Entry(box_form, textvariable=self.var_codigo, width=12, font=("Segoe UI", 9, "bold"))
        self.ent_codigo.pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(box_form, text="Descrição da Categoria: *", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_descricao = tk.StringVar()
        vincular_maiusculo(self.var_descricao)
        self.ent_descricao = ttk.Entry(box_form, textvariable=self.var_descricao, width=38)
        self.ent_descricao.pack(fill=tk.X, pady=(0, 16))

        # Barra de Botões de Ação
        f_botoes = ttk.Frame(box_form)
        f_botoes.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

        self.btn_novo = ttk.Button(f_botoes, text="Novo (F5)", command=self._novo_registro, width=10)
        self.btn_novo.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_gravar = tk.Button(
            f_botoes,
            text="Gravar (F10)",
            bg="#16A34A",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            relief=tk.FLAT,
            command=self._gravar,
        )
        self.btn_gravar.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_excluir = ttk.Button(f_botoes, text="Excluir", command=self._excluir, width=10)
        self.btn_excluir.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_fechar = ttk.Button(f_botoes, text="Fechar (Esc)", command=self._fechar, width=11)
        self.btn_fechar.pack(side=tk.RIGHT)

        configurar_navegacao_enter([self.ent_codigo, self.ent_descricao])

    def _configurar_atalhos(self):
        root = self.winfo_toplevel()
        root.bind("<F5>", lambda e: self._novo_registro())
        root.bind("<F10>", lambda e: self._gravar())
        root.bind("<Escape>", lambda e: self._fechar())

    def _fechar(self):
        top = self.winfo_toplevel()
        if top != self:
            top.destroy()

    def _limpar_filtro(self):
        self.var_busca.set("")
        self.carregar_categorias()

    def carregar_categorias(self):
        for it in self.tree.get_children():
            self.tree.delete(it)

        filtro = self.var_busca.get().strip().upper()
        try:
            lista = self.repo.listar_categorias()
            total = 0
            for item in lista:
                cod = str(item.get("codigo", ""))
                desc = str(item.get("descricao", ""))
                if not filtro or filtro in cod.upper() or filtro in desc.upper():
                    self.tree.insert("", tk.END, iid=cod, values=(cod, desc))
                    total += 1
            self.lbl_total.config(text=f"{total} categoria(s)")
        except Exception as ex:
            messagebox.showerror("Erro", f"Falha ao listar categorias: {ex}", parent=self)

    def _ao_selecionar(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        cod = sel[0]
        vals = self.tree.item(cod, "values")
        self.var_codigo.set(vals[0])
        self.var_descricao.set(vals[1])
        self.ent_codigo.config(state="readonly")
        self.ent_descricao.focus_set()

    def _novo_registro(self):
        self.tree.selection_remove(self.tree.selection())
        try:
            prox = self.repo.obter_proximo_codigo_categoria()
        except Exception:
            prox = 1
        self.ent_codigo.config(state="normal")
        self.var_codigo.set(str(prox))
        self.var_descricao.set("")
        self.ent_descricao.focus_set()

    def _gravar(self):
        cod_raw = self.var_codigo.get().strip()
        desc = self.var_descricao.get().strip().upper()

        if not cod_raw:
            messagebox.showerror("Erro", "Código da categoria é obrigatório.", parent=self)
            self.ent_codigo.focus_set()
            return

        try:
            cod = int(cod_raw)
        except ValueError:
            messagebox.showerror("Erro", "Código deve ser um valor numérico.", parent=self)
            self.ent_codigo.focus_set()
            return

        if not desc:
            messagebox.showerror("Erro", "Descrição da categoria é obrigatória.", parent=self)
            self.ent_descricao.focus_set()
            return

        try:
            self.repo.salvar_categoria(cod, desc)
            messagebox.showinfo("Sucesso", f"Categoria {cod} - {desc} salva com sucesso!", parent=self)
            self.carregar_categorias()
            self._novo_registro()
        except Exception as ex:
            messagebox.showerror("Erro", f"Falha ao gravar categoria: {ex}", parent=self)

    def _excluir(self):
        cod_raw = self.var_codigo.get().strip()
        if not cod_raw:
            messagebox.showwarning("Aviso", "Selecione uma categoria para excluir.", parent=self)
            return

        try:
            cod = int(cod_raw)
        except ValueError:
            return

        desc = self.var_descricao.get().strip()
        if messagebox.askyesno("Excluir", f"Confirma a exclusão da categoria {cod} - {desc}?", parent=self):
            try:
                self.repo.excluir_categoria(cod)
                messagebox.showinfo("Sucesso", "Categoria excluída com sucesso!", parent=self)
                self.carregar_categorias()
                self._novo_registro()
            except Exception as ex:
                messagebox.showerror("Erro ao Excluir", f"Não foi possível excluir a categoria: {ex}", parent=self)


def abrir_categorias_bens_sistema(parent=None, connection=None):
    """Abre a tela de cadastro de categorias de bens em janela TopLevel."""
    win = tk.Toplevel(parent)
    win.title("Categoria de Bens - Ativo Fixo - GeoAlvo")
    win.minsize(780, 480)
    centralizar_janela(win, parent, 840, 520)
    view = CategoriaBensView(win, connection=connection)
    view.pack(fill=tk.BOTH, expand=True)
    return win
