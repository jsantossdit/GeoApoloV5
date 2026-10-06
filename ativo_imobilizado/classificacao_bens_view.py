"""
Interface Gráfica para Cadastro e Manutenção de Classificação de Bens (Ativo Fixo).
GeoApolo V5
Equivalente funcional à gestão de classificação de bens/ativos do módulo SATFI em Delphi.
Tabela: USER_geoapolo_satfi_classificacaoativo
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict

from core import (
    centralizar_janela,
    vincular_maiusculo,
    configurar_navegacao_enter,
    habilitar_filtro_dinamico_combobox,
)
from ativo_imobilizado.repository import AtivoImobilizadoRepository


class ClassificacaoBensView(ttk.Frame):
    """Tela de manutenção de classificações de bens patrimoniais."""

    def __init__(self, parent=None, repo: Optional[AtivoImobilizadoRepository] = None, connection=None):
        super().__init__(parent)
        self.repo = repo or AtivoImobilizadoRepository(connection)
        self._map_categorias: Dict[str, str] = {}
        self._setup_ui()
        self._configurar_atalhos()
        self._carregar_categorias_combo()
        self.carregar_classificacoes()
        self._novo_registro()

    def _setup_ui(self):
        # Header superior
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Cadastro de Classificação de Bens (Ativo Fixo)",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
        ).pack(side=tk.LEFT)

        self.lbl_total = ttk.Label(
            header,
            text="0 classificação(ões)",
            font=("Segoe UI", 9, "bold"),
            foreground="#475569",
        )
        self.lbl_total.pack(side=tk.RIGHT)

        # Divisão em duas colunas (Esquerda: Lista / Direita: Formulário)
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # -------------------------------------------------------------
        # Painel Esquerdo: Lista de Classificações
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
        ent_b.bind("<Return>", lambda e: self.carregar_classificacoes())

        btn_filtrar = ttk.Button(f_busca, text="Filtrar", command=self.carregar_classificacoes, width=8)
        btn_filtrar.pack(side=tk.LEFT, padx=2)

        btn_todos = ttk.Button(f_busca, text="Todos", command=self._limpar_filtro, width=7)
        btn_todos.pack(side=tk.LEFT, padx=2)

        cols = ("cod", "descricao", "categoria")
        self.tree = ttk.Treeview(f_left, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("cod", text="Código")
        self.tree.heading("descricao", text="Descrição da Classificação")
        self.tree.heading("categoria", text="Categoria do Bem")

        self.tree.column("cod", width=80, anchor=tk.CENTER)
        self.tree.column("descricao", width=240, anchor=tk.W)
        self.tree.column("categoria", width=180, anchor=tk.W)

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

        box_form = ttk.LabelFrame(f_right, text=" Detalhes da Classificação ", padding=12)
        box_form.pack(fill=tk.BOTH, expand=True)

        ttk.Label(box_form, text="Código da Classificação: *", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_codigo = tk.StringVar()
        vincular_maiusculo(self.var_codigo)
        self.ent_codigo = ttk.Entry(box_form, textvariable=self.var_codigo, width=12, font=("Segoe UI", 9, "bold"))
        self.ent_codigo.pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(box_form, text="Descrição da Classificação: *", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_descricao = tk.StringVar()
        vincular_maiusculo(self.var_descricao)
        self.ent_descricao = ttk.Entry(box_form, textvariable=self.var_descricao, width=38)
        self.ent_descricao.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(box_form, text="Categoria do Bem Vinculada:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_categoria = tk.StringVar()
        self.cbo_categoria = ttk.Combobox(box_form, textvariable=self.var_categoria, width=36)
        self.cbo_categoria.pack(fill=tk.X, pady=(0, 16))

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

        configurar_navegacao_enter([self.ent_codigo, self.ent_descricao, self.cbo_categoria])

    def _configurar_atalhos(self):
        root = self.winfo_toplevel()
        root.bind("<F5>", lambda e: self._novo_registro())
        root.bind("<F10>", lambda e: self._gravar())
        root.bind("<Escape>", lambda e: self._fechar())

    def _fechar(self):
        top = self.winfo_toplevel()
        if top != self:
            top.destroy()

    def _carregar_categorias_combo(self):
        try:
            categorias = self.repo.listar_categorias()
            self._map_categorias = {
                f"{c['codigo']} - {c['descricao']}": str(c['codigo'])
                for c in categorias
            }
            opcoes = list(self._map_categorias.keys())
            self.cbo_categoria["values"] = opcoes
            habilitar_filtro_dinamico_combobox(self.cbo_categoria, opcoes)
        except Exception as ex:
            print(f"Erro ao carregar categorias para combo: {ex}")

    def _limpar_filtro(self):
        self.var_busca.set("")
        self.carregar_classificacoes()

    def carregar_classificacoes(self):
        for it in self.tree.get_children():
            self.tree.delete(it)

        filtro = self.var_busca.get().strip().upper()
        try:
            lista = self.repo.listar_todas_classificacoes(filtro)
            total = 0
            for item in lista:
                cod = str(item.get("codigoclasse", ""))
                desc = str(item.get("descricao", ""))
                cat = str(item.get("categoria", "") or "")
                self.tree.insert("", tk.END, iid=cod, values=(cod, desc, cat))
                total += 1
            self.lbl_total.config(text=f"{total} classificação(ões)")
        except Exception as ex:
            messagebox.showerror("Erro", f"Falha ao listar classificações: {ex}", parent=self)

    def _ao_selecionar(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        cod = sel[0]
        try:
            reg = self.repo.obter_classificacao(int(cod))
        except Exception:
            reg = None

        if reg:
            self.var_codigo.set(str(reg.get("codigoclasse", "")))
            self.var_descricao.set(str(reg.get("descricao", "")))
            cod_cat = str(reg.get("codigo_categoria") or "").strip()
            # Seleciona no combo correspondente
            achou = False
            for rotulo, val_cod in self._map_categorias.items():
                if val_cod == cod_cat:
                    self.var_categoria.set(rotulo)
                    achou = True
                    break
            if not achou:
                self.var_categoria.set("")
        else:
            vals = self.tree.item(cod, "values")
            self.var_codigo.set(vals[0])
            self.var_descricao.set(vals[1])
            self.var_categoria.set(vals[2] if len(vals) > 2 else "")

        self.ent_codigo.config(state="readonly")
        self.ent_descricao.focus_set()

    def _novo_registro(self):
        self.tree.selection_remove(self.tree.selection())
        try:
            prox = self.repo.obter_proximo_codigo_classificacao()
        except Exception:
            prox = 1
        self.ent_codigo.config(state="normal")
        self.var_codigo.set(str(prox))
        self.var_descricao.set("")
        self.var_categoria.set("")
        self.ent_descricao.focus_set()

    def _gravar(self):
        cod_raw = self.var_codigo.get().strip()
        desc = self.var_descricao.get().strip().upper()

        if not cod_raw:
            messagebox.showerror("Erro", "Código da classificação é obrigatório.", parent=self)
            self.ent_codigo.focus_set()
            return

        try:
            cod = int(cod_raw)
        except ValueError:
            messagebox.showerror("Erro", "Código deve ser um valor numérico.", parent=self)
            self.ent_codigo.focus_set()
            return

        if not desc:
            messagebox.showerror("Erro", "Descrição da classificação é obrigatória.", parent=self)
            self.ent_descricao.focus_set()
            return

        cat_selecionada = self.var_categoria.get().strip()
        cod_categoria = self._map_categorias.get(cat_selecionada)
        cod_cat_int = int(cod_categoria) if cod_categoria else None

        try:
            self.repo.salvar_classificacao(cod, desc, cod_cat_int)
            messagebox.showinfo("Sucesso", f"Classificação {cod} - {desc} salva com sucesso!", parent=self)
            self.carregar_classificacoes()
            self._novo_registro()
        except Exception as ex:
            messagebox.showerror("Erro", f"Falha ao gravar classificação: {ex}", parent=self)

    def _excluir(self):
        cod_raw = self.var_codigo.get().strip()
        if not cod_raw:
            messagebox.showwarning("Aviso", "Selecione uma classificação para excluir.", parent=self)
            return

        try:
            cod = int(cod_raw)
        except ValueError:
            return

        desc = self.var_descricao.get().strip()
        if messagebox.askyesno("Excluir", f"Confirma a exclusão da classificação {cod} - {desc}?", parent=self):
            try:
                self.repo.excluir_classificacao(cod)
                messagebox.showinfo("Sucesso", "Classificação excluída com sucesso!", parent=self)
                self.carregar_classificacoes()
                self._novo_registro()
            except Exception as ex:
                messagebox.showerror("Erro ao Excluir", f"Não foi possível excluir a classificação: {ex}", parent=self)


def abrir_classificacao_bens_sistema(parent=None, connection=None):
    """Abre a tela de cadastro de classificações de bens em janela TopLevel."""
    win = tk.Toplevel(parent)
    win.title("Classificação de Bens / Ativos - Ativo Fixo - GeoAlvo")
    win.minsize(800, 500)
    centralizar_janela(win, parent, 860, 540)
    view = ClassificacaoBensView(win, connection=connection)
    view.pack(fill=tk.BOTH, expand=True)
    return win
