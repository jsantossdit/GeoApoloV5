"""
Interface Gráfica para Cadastro de Grupos de Produtos.
GeoApolo V5
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from core import vincular_maiusculo, configurar_navegacao_enter
from produtos.models import GrupoProdutoDTO
from produtos.service import ProdutosService


class GruposProdutosView(ttk.Frame):
    """Tela de cadastro e manutenção de grupos de produtos."""

    def __init__(self, parent=None, service: Optional[ProdutosService] = None, connection=None):
        super().__init__(parent)
        self.service = service
        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from produtos.repository import ProdutosRepository
                conn = connection or obter_conexao_banco()
                self.service = ProdutosService(ProdutosRepository(conn))
            except Exception:
                pass

        self._setup_ui()
        self._configurar_atalhos()
        if self.service:
            self._carregar_dados_iniciais()

    def _setup_ui(self):
        # Header
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        lbl_titulo = ttk.Label(
            header,
            text="Cadastro de Grupos de Produtos",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
        )
        lbl_titulo.pack(side=tk.LEFT)

        lbl_sub = ttk.Label(
            header,
            text="Classificação e estruturação de grupos para produtos e estoque",
            font=("Segoe UI", 9),
            foreground="#6B7280",
        )
        lbl_sub.pack(side=tk.LEFT, padx=15)

        # PanedWindow
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Painel Esquerdo: Grade de Grupos
        left = ttk.Frame(paned, padding=5)
        paned.add(left, weight=3)

        f_busca = ttk.Frame(left)
        f_busca.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(f_busca, text="Buscar:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.var_busca = tk.StringVar()
        self.var_busca.trace_add("write", lambda *a: self._forcar_maiusculo(self.var_busca))
        self.ent_busca = ttk.Entry(f_busca, textvariable=self.var_busca, width=20)
        self.ent_busca.pack(side=tk.LEFT, padx=(0, 6))
        self.ent_busca.bind("<Return>", lambda e: self.carregar_grupos())

        ttk.Button(f_busca, text="Filtrar", command=self.carregar_grupos, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(f_busca, text="Todos", command=self._limpar_busca, width=7).pack(side=tk.LEFT, padx=2)

        cols = ("cod", "est", "nome")
        self.tree_grupos = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        self.tree_grupos.heading("cod", text="Código")
        self.tree_grupos.heading("est", text="Código Estruturado (Árvore)")
        self.tree_grupos.heading("nome", text="Descrição do Grupo")

        self.tree_grupos.column("cod", width=60, anchor=tk.CENTER)
        self.tree_grupos.column("est", width=150, anchor=tk.W)
        self.tree_grupos.column("nome", width=220)

        scroll_y = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.tree_grupos.yview)
        self.tree_grupos.configure(yscrollcommand=scroll_y.set)

        self.tree_grupos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_grupos.bind("<<TreeviewSelect>>", self._ao_selecionar_grupo)

        # Painel Direito: Formulário
        right = ttk.Frame(paned, padding=8)
        paned.add(right, weight=2)

        form_box = ttk.LabelFrame(right, text=" Dados do Grupo de Produtos ", padding=10)
        form_box.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        ttk.Label(form_box, text="Código Interno:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(2, 2))
        self.ent_grupocod = ttk.Entry(form_box, width=12)
        self.ent_grupocod.pack(anchor=tk.W, pady=(0, 8))
        self.ent_grupocod.bind("<Return>", lambda e: self._focar(self.ent_cod_estruturado))

        ttk.Label(form_box, text="Código Estruturado (Ex: 01.01):", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(2, 2))
        self.var_cod_est = tk.StringVar()
        self.var_cod_est.trace_add("write", lambda *a: self._forcar_maiusculo(self.var_cod_est))
        self.ent_cod_estruturado = ttk.Entry(form_box, textvariable=self.var_cod_est, width=20)
        self.ent_cod_estruturado.pack(anchor=tk.W, pady=(0, 8))
        self.ent_cod_estruturado.bind("<Return>", lambda e: self._focar(self.ent_nome_grupo))

        ttk.Label(form_box, text="Nome do Grupo (*):", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(2, 2))
        self.var_nome_grupo = tk.StringVar()
        self.var_nome_grupo.trace_add("write", lambda *a: self._forcar_maiusculo(self.var_nome_grupo))
        self.ent_nome_grupo = ttk.Entry(form_box, textvariable=self.var_nome_grupo)
        self.ent_nome_grupo.pack(fill=tk.X, pady=(0, 15))
        self.ent_nome_grupo.bind("<Return>", lambda e: self._salvar_grupo())

        configurar_navegacao_enter([self.ent_grupocod, self.ent_cod_estruturado, self.ent_nome_grupo])

        # Botões com atalhos padronizados
        bar_btns = ttk.Frame(right)
        bar_btns.pack(fill=tk.X, pady=(4, 0))

        self.btn_inclui = ttk.Button(bar_btns, text="Inclui <F2>", command=self._novo_grupo)
        self.btn_inclui.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_grava = ttk.Button(bar_btns, text="Grava <F3>", command=self._salvar_grupo)
        self.btn_grava.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_exclui = ttk.Button(bar_btns, text="Exclui <F5>", command=self._excluir_grupo)
        self.btn_exclui.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_cancela = ttk.Button(bar_btns, text="Cancela/Limpar <F6>", command=self._limpar_campos)
        self.btn_cancela.pack(side=tk.RIGHT)

    def _configurar_atalhos(self):
        """Associa atalhos de teclado F2, F3, F5, F6 e Alt aos botões."""
        top = self.winfo_toplevel()
        top.bind("<F2>", lambda e: self._novo_grupo())
        top.bind("<F3>", lambda e: self._salvar_grupo())
        top.bind("<F5>", lambda e: self._excluir_grupo())
        top.bind("<F6>", lambda e: self._limpar_campos())
        top.bind("<Alt-i>", lambda e: self._novo_grupo())
        top.bind("<Alt-I>", lambda e: self._novo_grupo())
        top.bind("<Alt-g>", lambda e: self._salvar_grupo())
        top.bind("<Alt-G>", lambda e: self._salvar_grupo())
        top.bind("<Alt-e>", lambda e: self._excluir_grupo())
        top.bind("<Alt-E>", lambda e: self._excluir_grupo())
        top.bind("<Alt-c>", lambda e: self._limpar_campos())
        top.bind("<Alt-C>", lambda e: self._limpar_campos())

    def _forcar_maiusculo(self, var: tk.StringVar):
        val = var.get()
        if val != val.upper():
            var.set(val.upper())

    def _focar(self, widget):
        widget.focus_set()
        return "break"

    def _carregar_dados_iniciais(self):
        self.carregar_grupos()
        self._limpar_campos()

    def carregar_grupos(self):
        for item in self.tree_grupos.get_children():
            self.tree_grupos.delete(item)

        if not self.service:
            return

        filtro = self.var_busca.get().strip().upper()
        grupos = self.service.listar_grupos()
        for g in grupos:
            if filtro:
                if filtro not in g.nome_grupo.upper() and filtro not in g.codigo_estruturado.upper() and filtro != str(g.grupocod):
                    continue
            # Visão em árvore hierárquica alinhada à esquerda
            nivel = g.codigo_estruturado.count(".") if g.codigo_estruturado else 0
            recuo = ("    " * nivel) + ("└─ " if nivel > 0 else "")
            display_estruturado = f"{recuo}{g.codigo_estruturado}" if g.codigo_estruturado else "-"
            self.tree_grupos.insert(
                "",
                tk.END,
                values=(g.grupocod, display_estruturado, g.nome_grupo)
            )

    def _limpar_busca(self):
        self.var_busca.set("")
        self.carregar_grupos()

    def _ao_selecionar_grupo(self, event=None):
        sel = self.tree_grupos.selection()
        if not sel or not self.service:
            return
        cod_val = self.tree_grupos.item(sel[0], "values")[0]
        try:
            cod_int = int(cod_val)
        except ValueError:
            return

        g = self.service.obter_grupo(cod_int)
        if not g:
            return

        self.ent_grupocod.delete(0, tk.END)
        self.ent_grupocod.insert(0, str(g.grupocod))
        self.var_cod_est.set(g.codigo_estruturado)
        self.var_nome_grupo.set(g.nome_grupo)

    def _limpar_campos(self):
        self.ent_grupocod.delete(0, tk.END)
        self.var_cod_est.set("")
        self.var_nome_grupo.set("")
        if self.tree_grupos.selection():
            self.tree_grupos.selection_remove(self.tree_grupos.selection())
        self.ent_nome_grupo.focus_set()

    def _novo_grupo(self):
        """Inicia inclusão de grupo solicitando confirmação e gerando código via geoapolo_configcod."""
        if not messagebox.askyesno("Confirmação", "Confirma a inclusão do grupo de produtos?", parent=self):
            return

        self._limpar_campos()
        if self.service:
            empresa = getattr(self.winfo_toplevel(), "empresa_ativa", "1.01")
            prox = self.service.gerar_codigo_configcod(tabela="USER_geoapolo_produto_grupo", empresa=empresa)
            self.ent_grupocod.insert(0, str(prox))
        self.ent_nome_grupo.focus_set()

    def _salvar_grupo(self):
        """Grava os dados do grupo de produtos com confirmação Sim/Não."""
        if not self.service:
            return

        try:
            cod_val = int(self.ent_grupocod.get().strip() or 0)
        except ValueError:
            cod_val = 0

        nome = self.var_nome_grupo.get().strip().upper()
        if not nome:
            messagebox.showwarning("Aviso", "O nome do grupo de produtos é obrigatório.", parent=self)
            self.ent_nome_grupo.focus_set()
            return

        if not messagebox.askyesno("Confirmação", "Confirma a gravação dos dados do grupo de produtos?", parent=self):
            return

        dto = GrupoProdutoDTO(
            grupocod=cod_val,
            codigo_estruturado=self.var_cod_est.get().strip().upper(),
            nome_grupo=nome,
        )

        empresa = getattr(self.winfo_toplevel(), "empresa_ativa", "1.01")
        res = self.service.salvar_grupo(dto, empresa=empresa)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem, parent=self)
            self.carregar_grupos()
            # Seleciona o grupo salvo
            for item in self.tree_grupos.get_children():
                if str(self.tree_grupos.item(item, "values")[0]) == str(res.codigo):
                    self.tree_grupos.selection_set(item)
                    self.tree_grupos.see(item)
                    break
        else:
            messagebox.showerror("Erro ao Gravar", res.mensagem, parent=self)

    def _excluir_grupo(self):
        """Exclui o grupo de produtos selecionado com confirmação Sim/Não."""
        if not self.service:
            return

        try:
            cod_val = int(self.ent_grupocod.get().strip() or 0)
        except ValueError:
            cod_val = 0

        if cod_val <= 0:
            messagebox.showwarning("Aviso", "Selecione um grupo de produtos cadastrado para exclusão.", parent=self)
            return

        nome = self.var_nome_grupo.get().strip()
        if not messagebox.askyesno(
            "Confirmação de Exclusão",
            f"Confirma a remoção do grupo de produtos?\n\nCódigo: {cod_val}\nNome: {nome}\n\nEsta operação não poderá ser desfeita.",
            parent=self
        ):
            return

        res = self.service.excluir_grupo(cod_val)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem, parent=self)
            self.carregar_grupos()
            self._limpar_campos()
        else:
            messagebox.showerror("Erro ao Excluir", res.mensagem, parent=self)


def abrir_janela_grupos_produtos(parent, connection=None):
    """Abre a tela de cadastro de grupos de produtos em TopLevel centralizada."""
    from core import centralizar_janela
    win = tk.Toplevel(parent)
    win.title("Cadastro de Grupos de Produtos - GeoAlvo")
    win.minsize(700, 420)
    centralizar_janela(win, parent, 820, 480)
    view = GruposProdutosView(win, connection=connection)
    view.pack(fill=tk.BOTH, expand=True)
    return win
