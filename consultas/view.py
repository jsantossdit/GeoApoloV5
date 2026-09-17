"""
Interface Gráfica para o Motor de Consultas Dinâmicas e Gestão de Permissões.
GeoApolo V5
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List

from consultas.models import (
    ConsultaConfigDTO,
    PermissaoConsultaDTO,
    FiltroConsultaDTO,
    ResultadoConsultaDTO,
)
from consultas.service import ConsultasService


class ConsultasView(ttk.Frame):
    """View unificada com abas para Execução de Consultas Dinâmicas e Gerenciamento de Permissões."""

    def __init__(self, parent=None, service: Optional[ConsultasService] = None, connection=None):
        super().__init__(parent)
        self.service = service
        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from consultas.repository import ConsultasRepository
                conn = connection or obter_conexao_banco()
                self.service = ConsultasService(ConsultasRepository(conn))
            except Exception:
                pass

        self._setup_ui()
        if self.service:
            self._carregar_dados_iniciais()

    def _setup_ui(self):
        # Header
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        lbl_titulo = ttk.Label(
            header,
            text="Motor de Consultas Dinâmicas & Permissões SQL",
            font=("Segoe UI", 13, "bold"),
            foreground="#1E3A8A"
        )
        lbl_titulo.pack(side=tk.LEFT)

        lbl_sub = ttk.Label(
            header,
            text="Pesquisa flexível e controle de acesso a relatórios e visões do banco",
            font=("Segoe UI", 9),
            foreground="#6B7280"
        )
        lbl_sub.pack(side=tk.LEFT, padx=15)

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tab_busca = ttk.Frame(self.notebook, padding=10)
        self.tab_gerenciador = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_busca, text="  Pesquisa Dinâmica  ")
        self.notebook.add(self.tab_gerenciador, text="  Cadastro de Consultas & Permissões  ")

        self._build_tab_busca()
        self._build_tab_gerenciador()

    # -------------------------------------------------------------------------
    # ABA 1: EXECUÇÃO DE CONSULTAS DINÂMICAS
    # -------------------------------------------------------------------------
    def _build_tab_busca(self):
        bar = ttk.Frame(self.tab_busca, padding=5)
        bar.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(bar, text="Módulo / Visão:").pack(side=tk.LEFT, padx=(0, 5))
        self.cbo_controle = ttk.Combobox(
            bar,
            values=[
                "CLIENTES",
                "CIDADE_CIDADE",
                "CONTA_FINANCEIRASALDO",
                "USUARIO_DEPARTAMENTO",
                "CATEGORIA_ENTIDADE",
                "TIPOLOGRADOURO",
            ],
            state="readonly",
            width=22,
        )
        self.cbo_controle.set("CLIENTES")
        self.cbo_controle.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(bar, text="Termo:").pack(side=tk.LEFT, padx=(0, 5))
        self.ent_busca = ttk.Entry(bar, width=25)
        self.ent_busca.pack(side=tk.LEFT, padx=(0, 10))
        self.ent_busca.bind("<Return>", lambda e: self.executar_pesquisa())

        self.var_asc = tk.BooleanVar(value=True)
        chk_asc = ttk.Checkbutton(bar, text="Ordem Crescente", variable=self.var_asc)
        chk_asc.pack(side=tk.LEFT, padx=(0, 10))

        btn_buscar = ttk.Button(bar, text="Executar Pesquisa", command=self.executar_pesquisa)
        btn_buscar.pack(side=tk.LEFT)

        # Container do Grid
        self.grid_container = ttk.Frame(self.tab_busca)
        self.grid_container.pack(fill=tk.BOTH, expand=True, pady=5)

        self.tree_resultados = ttk.Treeview(self.grid_container, show="headings", selectmode="browse")
        self.scroll_y = ttk.Scrollbar(self.grid_container, orient=tk.VERTICAL, command=self.tree_resultados.yview)
        self.scroll_x = ttk.Scrollbar(self.grid_container, orient=tk.HORIZONTAL, command=self.tree_resultados.xview)
        self.tree_resultados.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        self.tree_resultados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_status_busca = ttk.Label(self.tab_busca, text="Aguardando parâmetros para consulta...")
        self.lbl_status_busca.pack(anchor=tk.W, pady=5)

    # -------------------------------------------------------------------------
    # ABA 2: CADASTRO DE CONSULTAS & PERMISSÕES
    # -------------------------------------------------------------------------
    def _build_tab_gerenciador(self):
        paned = ttk.PanedWindow(self.tab_gerenciador, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Painel Esquerdo: Lista de Consultas Cadastradas
        left = ttk.Frame(paned, padding=5)
        paned.add(left, weight=1)

        ttk.Label(left, text="Consultas Cadastradas", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        cols = ("cod", "desc", "banco")
        self.tree_consultas = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        self.tree_consultas.heading("cod", text="Código")
        self.tree_consultas.heading("desc", text="Descrição")
        self.tree_consultas.heading("banco", text="Banco")
        self.tree_consultas.column("cod", width=80, anchor=tk.CENTER)
        self.tree_consultas.column("desc", width=220)
        self.tree_consultas.column("banco", width=90, anchor=tk.CENTER)
        self.tree_consultas.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.tree_consultas.bind("<<TreeviewSelect>>", self._on_consulta_select)

        # Painel Direito: Formulário e Permissões
        right = ttk.Frame(paned, padding=5)
        paned.add(right, weight=1)

        ttk.Label(right, text="Definição da Consulta", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        f_grid = ttk.Frame(right)
        f_grid.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(f_grid, text="Código:").grid(row=0, column=0, sticky=tk.W)
        self.ent_cad_cod = ttk.Entry(f_grid, width=12)
        self.ent_cad_cod.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(f_grid, text="Banco:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        self.ent_cad_banco = ttk.Entry(f_grid, width=15)
        self.ent_cad_banco.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        self.ent_cad_banco.insert(0, "Apolo")

        ttk.Label(f_grid, text="Descrição:").grid(row=1, column=0, sticky=tk.W)
        self.ent_cad_desc = ttk.Entry(f_grid, width=40)
        self.ent_cad_desc.grid(row=1, column=1, columnspan=3, sticky=tk.W, padx=5, pady=2)

        ttk.Label(right, text="Instrução SQL:").pack(anchor=tk.W, pady=(5, 2))
        self.txt_sql = tk.Text(right, height=6, font=("Consolas", 9))
        self.txt_sql.pack(fill=tk.X, pady=(0, 5))

        btn_box = ttk.Frame(right)
        btn_box.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(btn_box, text="Nova", command=self._nova_consulta).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_box, text="Salvar Consulta", command=self._salvar_consulta).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_box, text="Excluir Consulta", command=self._excluir_consulta).pack(side=tk.LEFT)

        # Seção de Permissões
        sep = ttk.Separator(right, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X, pady=5)

        ttk.Label(right, text="Permissões de Usuários na Consulta", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(5, 2))

        cols_p = ("usuario", "autorizacao")
        self.tree_perm_consultas = ttk.Treeview(right, columns=cols_p, show="headings", height=4)
        self.tree_perm_consultas.heading("usuario", text="Usuário (Login)")
        self.tree_perm_consultas.heading("autorizacao", text="Status Autorização")
        self.tree_perm_consultas.column("usuario", width=160)
        self.tree_perm_consultas.column("autorizacao", width=140, anchor=tk.CENTER)
        self.tree_perm_consultas.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        p_btns = ttk.Frame(right)
        p_btns.pack(fill=tk.X)

        ttk.Button(p_btns, text="Autorizar Selecionado (S)", command=lambda: self._set_permissao(True)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(p_btns, text="Bloquear Selecionado (N)", command=lambda: self._set_permissao(False)).pack(side=tk.LEFT)

    # -------------------------------------------------------------------------
    # DADOS E EVENTOS
    # -------------------------------------------------------------------------
    def _carregar_dados_iniciais(self):
        try:
            self.carregar_consultas_cadastradas()
        except Exception:
            pass

    def executar_pesquisa(self):
        if not self.service:
            return

        controle = self.cbo_controle.get()
        termo = self.ent_busca.get()
        ordem_asc = self.var_asc.get()

        filtro = FiltroConsultaDTO(
            controle=controle,
            texto_busca=termo,
            ordem_asc=ordem_asc,
        )

        res: ResultadoConsultaDTO = self.service.executar_busca(filtro)
        if not res.sucesso:
            self.lbl_status_busca.config(text=res.mensagem, foreground="#DC2626")
            return

        # Reconstrói colunas dinâmicas no Treeview
        self.tree_resultados.delete(*self.tree_resultados.get_children())
        self.tree_resultados["columns"] = res.colunas
        for col in res.colunas:
            self.tree_resultados.heading(col, text=col)
            self.tree_resultados.column(col, width=140)

        for row in res.linhas:
            self.tree_resultados.insert("", tk.END, values=row)

        self.lbl_status_busca.config(
            text=f"Total de {res.total_registros} registro(s) encontrado(s).",
            foreground="#16A34A"
        )

    def carregar_consultas_cadastradas(self):
        for item in self.tree_consultas.get_children():
            self.tree_consultas.delete(item)

        if not self.service:
            return

        consultas = self.service.listar_consultas()
        for c in consultas:
            self.tree_consultas.insert("", tk.END, values=(c.codigo_consulta, c.descricao_consulta, c.banco_consulta))

    def _on_consulta_select(self, event):
        sel = self.tree_consultas.selection()
        if not sel or not self.service:
            return
        cod = self.tree_consultas.item(sel[0], "values")[0]
        c = self.service.obter_consulta(cod)
        if not c:
            return

        self.ent_cad_cod.delete(0, tk.END)
        self.ent_cad_cod.insert(0, c.codigo_consulta)

        self.ent_cad_desc.delete(0, tk.END)
        self.ent_cad_desc.insert(0, c.descricao_consulta)

        self.ent_cad_banco.delete(0, tk.END)
        self.ent_cad_banco.insert(0, c.banco_consulta)

        self.txt_sql.delete("1.0", tk.END)
        self.txt_sql.insert("1.0", c.sql_consulta)

        self._carregar_permissoes_consulta(c.codigo_consulta)

    def _carregar_permissoes_consulta(self, cod_consulta: str):
        for item in self.tree_perm_consultas.get_children():
            self.tree_perm_consultas.delete(item)

        if not self.service:
            return

        perms = self.service.listar_permissoes_consulta(cod_consulta)
        for p in perms:
            self.tree_perm_consultas.insert("", tk.END, values=(p.usucod, p.status_display))

    def _nova_consulta(self):
        self.ent_cad_cod.delete(0, tk.END)
        self.ent_cad_desc.delete(0, tk.END)
        self.ent_cad_banco.delete(0, tk.END)
        self.ent_cad_banco.insert(0, "Apolo")
        self.txt_sql.delete("1.0", tk.END)
        for item in self.tree_perm_consultas.get_children():
            self.tree_perm_consultas.delete(item)

    def _salvar_consulta(self):
        if not self.service:
            return
        cod = self.ent_cad_cod.get().strip()
        desc = self.ent_cad_desc.get().strip()
        banco = self.ent_cad_banco.get().strip()
        sql = self.txt_sql.get("1.0", tk.END).strip()

        try:
            dto = ConsultaConfigDTO(
                codigo_consulta=cod,
                descricao_consulta=desc,
                sql_consulta=sql,
                banco_consulta=banco,
            )
            self.service.salvar_consulta(dto)
            messagebox.showinfo("Sucesso", "Consulta cadastrada com sucesso.")
            self.carregar_consultas_cadastradas()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _excluir_consulta(self):
        if not self.service:
            return
        cod = self.ent_cad_cod.get().strip()
        if not cod:
            messagebox.showwarning("Aviso", "Selecione uma consulta para excluir.")
            return

        if not messagebox.askyesno("Confirmação", f"Excluir consulta '{cod}'?"):
            return

        try:
            self.service.excluir_consulta(cod)
            messagebox.showinfo("Sucesso", "Consulta excluída.")
            self._nova_consulta()
            self.carregar_consultas_cadastradas()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _set_permissao(self, autorizada: bool):
        if not self.service:
            return
        cod_consulta = self.ent_cad_cod.get().strip()
        sel = self.tree_perm_consultas.selection()
        if not cod_consulta or not sel:
            messagebox.showwarning("Aviso", "Selecione uma permissão de usuário.")
            return

        usucod = self.tree_perm_consultas.item(sel[0], "values")[0]
        self.service.atualizar_permissao(usucod, cod_consulta, autorizada)
        self._carregar_permissoes_consulta(cod_consulta)
