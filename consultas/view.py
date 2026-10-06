"""
Interface Gráfica para o Motor de Consultas Dinâmicas, Cadastro e Gestão de Permissões.
GeoApolo V5
Equivalente a unt_cadconsulta.pas (Tfrmcadconsulta) do Delphi.
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
    """View unificada para Cadastro e Gestão de Consultas Imediatas e Permissões SQL."""

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

        self._map_consultas = {}
        self._map_usuarios = {}
        self._setup_ui()
        if self.service:
            self._carregar_dados_iniciais()

    def _setup_ui(self):
        # Header
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        lbl_titulo = ttk.Label(
            header,
            text="Cadastro e Manutenção de Consultas no Banco de Dados",
            font=("Segoe UI", 13, "bold"),
            foreground="#1E3A8A"
        )
        lbl_titulo.pack(side=tk.LEFT)

        # Notebook com abas padronizadas conforme unt_cadconsulta.dfm
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tab_gerenciador = ttk.Frame(self.notebook, padding=10)
        self.tab_permissoes = ttk.Frame(self.notebook, padding=10)
        self.tab_busca = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_gerenciador, text="  Manutenção de Consultas  ")
        self.notebook.add(self.tab_permissoes, text="  Permissões de Consultas  ")
        self.notebook.add(self.tab_busca, text="  Pesquisa Dinâmica por Entidades  ")

        self._build_tab_gerenciador()
        self._build_tab_permissoes()
        self._build_tab_busca()

    # -------------------------------------------------------------------------
    # ABA 1: CADASTRO DE CONSULTAS (unt_cadconsulta - tblmanutencao)
    # -------------------------------------------------------------------------
    def _build_tab_gerenciador(self):
        paned = ttk.PanedWindow(self.tab_gerenciador, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Painel Esquerdo: Lista de Consultas Cadastradas
        left = ttk.Frame(paned, padding=5)
        paned.add(left, weight=1)

        f_left_top = ttk.Frame(left)
        f_left_top.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(f_left_top, text="Consultas Cadastradas", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        # Filtro rápido por tipo no painel esquerdo
        self.cbo_filtro_tipo = ttk.Combobox(
            f_left_top,
            values=["TODOS", "I - IMEDIATAS", "C - CAMPANHAS"],
            state="readonly",
            width=15,
            font=("Segoe UI", 8)
        )
        self.cbo_filtro_tipo.set("TODOS")
        self.cbo_filtro_tipo.pack(side=tk.RIGHT)
        self.cbo_filtro_tipo.bind("<<ComboboxSelected>>", lambda e: self.carregar_consultas_cadastradas())

        cols = ("cod", "desc", "tipo", "banco")
        self.tree_consultas = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        self.tree_consultas.heading("cod", text="Código")
        self.tree_consultas.heading("desc", text="Descrição")
        self.tree_consultas.heading("tipo", text="Tipo")
        self.tree_consultas.heading("banco", text="Banco")
        self.tree_consultas.column("cod", width=60, anchor=tk.CENTER)
        self.tree_consultas.column("desc", width=230)
        self.tree_consultas.column("tipo", width=50, anchor=tk.CENTER)
        self.tree_consultas.column("banco", width=80, anchor=tk.CENTER)

        scroll_tree_y = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.tree_consultas.yview)
        self.tree_consultas.configure(yscrollcommand=scroll_tree_y.set)

        self.tree_consultas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_tree_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_consultas.bind("<<TreeviewSelect>>", self._on_consulta_select)

        # Painel Direito: Formulário e Instrução SQL
        right = ttk.Frame(paned, padding=8)
        paned.add(right, weight=2)

        ttk.Label(right, text="Definição da Consulta", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        f_grid = ttk.Frame(right)
        f_grid.pack(fill=tk.X, pady=(0, 5))

        # Linha 0: Código, Tipo de Consulta, Banco
        ttk.Label(f_grid, text="Código:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ent_cad_cod = ttk.Entry(f_grid, width=10)
        self.ent_cad_cod.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(f_grid, text="Tipo:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0), pady=2)
        self.cbo_tipo_consulta = ttk.Combobox(
            f_grid,
            values=["I - IMEDIATA", "C - CAMPANHA", "M - MIX"],
            state="readonly",
            width=14,
        )
        self.cbo_tipo_consulta.set("I - IMEDIATA")
        self.cbo_tipo_consulta.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)

        ttk.Label(f_grid, text="Banco:").grid(row=0, column=4, sticky=tk.W, padx=(10, 0), pady=2)
        self.cbo_cad_banco = ttk.Combobox(
            f_grid,
            values=["ALVO", "GEOAPOLO", "SAVIC", "APLICATIVO RCC", "Apolo"],
            state="normal",
            width=16,
        )
        self.cbo_cad_banco.set("ALVO")
        self.cbo_cad_banco.grid(row=0, column=5, sticky=tk.W, padx=5, pady=2)
        self.cbo_cad_banco.bind("<<ComboboxSelected>>", self._on_cad_banco_selected)

        # Linha 1: Descrição da consulta
        ttk.Label(f_grid, text="Descrição:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.ent_cad_desc = ttk.Entry(f_grid)
        self.ent_cad_desc.grid(row=1, column=1, columnspan=5, sticky="ew", padx=5, pady=2)
        f_grid.columnconfigure(1, weight=1)

        # Instrução SQL (memosql do Delphi)
        ttk.Label(right, text="Instrução SQL (sentenca_sql):", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(4, 2))
        f_sql = ttk.Frame(right)
        f_sql.pack(fill=tk.BOTH, expand=True, pady=(0, 4))

        self.txt_sql = tk.Text(f_sql, height=10, font=("Consolas", 9), wrap=tk.NONE)
        sql_sy = ttk.Scrollbar(f_sql, orient=tk.VERTICAL, command=self.txt_sql.yview)
        sql_sx = ttk.Scrollbar(f_sql, orient=tk.HORIZONTAL, command=self.txt_sql.xview)
        self.txt_sql.configure(yscrollcommand=sql_sy.set, xscrollcommand=sql_sx.set)

        self.txt_sql.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sql_sy.pack(side=tk.RIGHT, fill=tk.Y)
        sql_sx.pack(side=tk.BOTTOM, fill=tk.X)

        # Box explicativo de parâmetros (GroupBox2 de unt_cadconsulta.dfm do Delphi)
        box_help = ttk.LabelFrame(right, text=" Definição de Parâmetros para Consulta ", padding=6)
        box_help.pack(fill=tk.X, pady=(0, 6))

        h1 = "• Parâmetros Numéricos ou Caracteres variáveis: coloque no início '|' e no final '^' (Ex: |Ano^)"
        h2 = "• Parâmetros de Data: coloque no início '{' e no final '}' (Ex: {Data_Inicial})"
        h3 = "• Parâmetros Numéricos ou Caracteres fixos: coloque no início '[' e no final ']' (Ex: [01.001])"
        h4 = "• Parâmetro de vazio: utilize '&?' onde desejar passar como vazio"

        for h in [h1, h2, h3, h4]:
            lbl_h = tk.Label(box_help, text=h, font=("Segoe UI", 8), fg="#0d47a1", anchor=tk.W)
            lbl_h.pack(fill=tk.X, pady=1)

        # Botões de Ação do Cadastro
        btn_box = ttk.Frame(right)
        btn_box.pack(fill=tk.X, pady=(2, 2))

        ttk.Button(btn_box, text="Novo", command=self._nova_consulta).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_box, text="Salvar Consulta", command=self._salvar_consulta).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_box, text="Excluir Consulta", command=self._excluir_consulta).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(
            btn_box,
            text="Permissões da Consulta ->",
            command=lambda: self.notebook.select(self.tab_permissoes)
        ).pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(btn_box, text="Executar Imediatas (Funil)", command=self._abrir_imediatas_funil).pack(side=tk.RIGHT)

    # -------------------------------------------------------------------------
    # ABA 2: PERMISSÕES DE CONSULTAS (unt_cadconsulta - tblpermissao)
    # -------------------------------------------------------------------------
    def _build_tab_permissoes(self):
        # Banner superior informando a consulta selecionada
        f_top = ttk.Frame(self.tab_permissoes, padding=(4, 4))
        f_top.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(
            f_top,
            text="Consulta Selecionada:",
            font=("Segoe UI", 10, "bold"),
            foreground="#1E3A8A",
        ).pack(side=tk.LEFT, padx=(0, 6))

        self.lbl_perm_consulta_info = ttk.Label(
            f_top,
            text="Nenhuma consulta selecionada",
            font=("Segoe UI", 10, "bold"),
            foreground="#B91C1C",
        )
        self.lbl_perm_consulta_info.pack(side=tk.LEFT, padx=(0, 15))

        # Seletor rápido de consulta diretamente nesta aba
        ttk.Label(f_top, text="Alternar Consulta:").pack(side=tk.LEFT, padx=(10, 4))
        self.cbo_perm_consulta_sel = ttk.Combobox(f_top, state="readonly", width=35)
        self.cbo_perm_consulta_sel.pack(side=tk.LEFT)
        self.cbo_perm_consulta_sel.bind("<<ComboboxSelected>>", self._on_perm_consulta_combo_select)

        # 1. Definição da Permissão (GroupBox3 de unt_cadconsulta)
        box_aplicar = ttk.LabelFrame(
            self.tab_permissoes,
            text=" Grupos de Usuários & Usuários (unt_cadconsulta - GroupBox3) ",
            padding=10
        )
        box_aplicar.pack(fill=tk.X, pady=(0, 8))

        f_grid_perm = ttk.Frame(box_aplicar)
        f_grid_perm.pack(fill=tk.X)

        # Linha 0: Grupo de Usuários e Usuário
        ttk.Label(f_grid_perm, text="Grupo de Usuários:", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 8), pady=4
        )
        self.cbo_perm_grupo = ttk.Combobox(f_grid_perm, state="readonly", width=30)
        self.cbo_perm_grupo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20), pady=4)
        self.cbo_perm_grupo.bind("<<ComboboxSelected>>", self._on_perm_grupo_changed)

        ttk.Label(f_grid_perm, text="Usuários:", font=("Segoe UI", 9, "bold")).grid(
            row=0, column=2, sticky=tk.W, padx=(0, 8), pady=4
        )
        self.cbo_perm_usuario = ttk.Combobox(f_grid_perm, state="readonly", width=35)
        self.cbo_perm_usuario.grid(row=0, column=3, sticky=tk.W, padx=(0, 10), pady=4)

        # Alias para compatibilidade com testes anteriores
        self.cbo_user_perm = self.cbo_perm_usuario

        # Linha 1: Status de Permissão (Radiobuttons como rdgpermissaoconsulta do Delphi)
        ttk.Label(f_grid_perm, text="Permissão:", font=("Segoe UI", 9, "bold")).grid(
            row=1, column=0, sticky=tk.W, padx=(0, 8), pady=8
        )

        f_radios = ttk.Frame(f_grid_perm)
        f_radios.grid(row=1, column=1, sticky=tk.W, pady=8)

        self.var_perm_status = tk.StringVar(value="A")
        rb_aut = ttk.Radiobutton(
            f_radios,
            text="Autorizado (A)",
            value="A",
            variable=self.var_perm_status
        )
        rb_aut.pack(side=tk.LEFT, padx=(0, 15))

        rb_neg = ttk.Radiobutton(
            f_radios,
            text="Negado (N)",
            value="N",
            variable=self.var_perm_status
        )
        rb_neg.pack(side=tk.LEFT)

        # Botões de Ação na barra de permissão (estilizados e padronizados)
        f_perm_actions = ttk.Frame(f_grid_perm)
        f_perm_actions.grid(row=1, column=2, columnspan=2, sticky=tk.W, pady=8)

        self.btn_aplicar_perm = ttk.Button(
            f_perm_actions,
            text="Aplicar Permissão",
            command=self._aplicar_permissao_click,
            width=20
        )
        self.btn_aplicar_perm.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_remover_perm = ttk.Button(
            f_perm_actions,
            text="Remover Permissão",
            command=self._remover_permissao_click,
            width=20
        )
        self.btn_remover_perm.pack(side=tk.LEFT)

        # 2. Grade de Permissões Concedidas para a Consulta
        box_grid = ttk.LabelFrame(
            self.tab_permissoes,
            text=" Permissões Registradas para a Consulta Selecionada ",
            padding=8
        )
        box_grid.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        cols_p = ("usuario", "autorizacao")
        self.tree_perm_consultas = ttk.Treeview(
            box_grid,
            columns=cols_p,
            show="headings",
            height=7,
            selectmode="browse"
        )
        self.tree_perm_consultas.heading("usuario", text="Usuário (Login / usucod)")
        self.tree_perm_consultas.heading("autorizacao", text="Status Autorização")
        self.tree_perm_consultas.column("usuario", width=250)
        self.tree_perm_consultas.column("autorizacao", width=160, anchor=tk.CENTER)

        perm_sy = ttk.Scrollbar(box_grid, orient=tk.VERTICAL, command=self.tree_perm_consultas.yview)
        self.tree_perm_consultas.configure(yscrollcommand=perm_sy.set)

        self.tree_perm_consultas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        perm_sy.pack(side=tk.RIGHT, fill=tk.Y)

        # 3. Clonagem de Permissão de Consultas (GroupBox4 de unt_cadconsulta.dfm)
        box_clone = ttk.LabelFrame(
            self.tab_permissoes,
            text=" Clonagem de Permissão de Consultas (unt_cadconsulta - GroupBox4) ",
            padding=8
        )
        box_clone.pack(fill=tk.X, pady=(0, 4))

        f_grid_clone = ttk.Frame(box_clone)
        f_grid_clone.pack(fill=tk.X)

        ttk.Label(f_grid_clone, text="Usuário de Origem:").grid(row=0, column=0, sticky=tk.W, padx=(0, 6), pady=2)
        self.cbo_clone_origem = ttk.Combobox(f_grid_clone, state="readonly", width=28)
        self.cbo_clone_origem.grid(row=0, column=1, sticky=tk.W, padx=(0, 15), pady=2)

        ttk.Label(f_grid_clone, text="Usuário de Destino:").grid(row=0, column=2, sticky=tk.W, padx=(0, 6), pady=2)
        self.cbo_clone_destino = ttk.Combobox(f_grid_clone, state="readonly", width=28)
        self.cbo_clone_destino.grid(row=0, column=3, sticky=tk.W, padx=(0, 15), pady=2)

        self.btn_clonar_perm = ttk.Button(
            f_grid_clone,
            text="Clonar Permissões",
            command=self._clonar_permissoes_click,
            width=20
        )
        self.btn_clonar_perm.grid(row=0, column=4, sticky=tk.W, pady=2)

    # -------------------------------------------------------------------------
    # ABA 3: PESQUISA DINÂMICA (unt_consultas4)
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
    # DADOS E EVENTOS
    # -------------------------------------------------------------------------
    def _carregar_dados_iniciais(self):
        try:
            self.carregar_consultas_cadastradas()
            self._carregar_grupos_sistema()
            self._carregar_usuarios_sistema()
            self._nova_consulta()
        except Exception as e:
            print(f"Erro ao carregar dados iniciais de consultas: {e}")

    def _carregar_grupos_sistema(self):
        """Carrega grupos de usuários para o combo de permissão (unt_cadconsulta - CarregarGrupos)."""
        if not self.service:
            return
        try:
            grupos = self.service.listar_grupos()
            vals = ["TODOS OS GRUPOS"] + [g[1] for g in grupos if g[1]]
            self.cbo_perm_grupo["values"] = vals
            self.cbo_perm_grupo.set("TODOS OS GRUPOS")
        except Exception as e:
            print(f"Erro ao carregar grupos: {e}")

    def _carregar_usuarios_sistema(self, grupo: Optional[str] = None):
        """Carrega usuários ativos no combo de permissão e clonagem."""
        if not self.service:
            return
        try:
            filtro_grupo = None if not grupo or grupo == "TODOS OS GRUPOS" else grupo
            usuarios = self.service.listar_usuarios(grupo=filtro_grupo)
            self._map_usuarios = {u[0]: u[1] for u in usuarios}

            users_list = [f"{u[0]} - {u[1]}" if u[1] and u[1] != u[0] else u[0] for u in usuarios]
            combo_users = ["(Todos os usuários do grupo)"] + users_list if filtro_grupo else users_list

            self.cbo_perm_usuario["values"] = combo_users
            if combo_users:
                self.cbo_perm_usuario.current(0)

            # Combos de clonagem recebem a lista completa de usuários
            if not filtro_grupo:
                self.cbo_clone_origem["values"] = users_list
                self.cbo_clone_destino["values"] = users_list
                if users_list:
                    self.cbo_clone_origem.current(0)
                    if len(users_list) > 1:
                        self.cbo_clone_destino.current(1)
        except Exception as e:
            print(f"Erro ao carregar usuários de consulta: {e}")

    def _on_perm_grupo_changed(self, event=None):
        """Atualiza a lista de usuários quando o grupo é alterado (unt_cadconsulta - cbogruposChange)."""
        grupo = self.cbo_perm_grupo.get().strip()
        self._carregar_usuarios_sistema(grupo=grupo)

    def carregar_consultas_cadastradas(self):
        for item in self.tree_consultas.get_children():
            self.tree_consultas.delete(item)

        if not self.service:
            return

        filtro = self.cbo_filtro_tipo.get()
        tipo = None
        if "IMEDIATA" in filtro:
            tipo = "I"
        elif "CAMPANHA" in filtro:
            tipo = "C"

        consultas = self.service.listar_consultas(tipo_consulta=tipo)
        self._map_consultas = {}
        cbo_items = []
        for c in consultas:
            self.tree_consultas.insert(
                "",
                tk.END,
                values=(c.codigo_consulta, c.descricao_consulta, c.tipo_consulta, c.banco_consulta)
            )
            item_display = f"{c.codigo_consulta} - {c.descricao_consulta}"
            self._map_consultas[c.codigo_consulta] = c
            cbo_items.append(item_display)

        self.cbo_perm_consulta_sel["values"] = cbo_items

    def _on_consulta_select(self, event=None):
        sel = self.tree_consultas.selection()
        if not sel or not self.service:
            return
        cod = str(self.tree_consultas.item(sel[0], "values")[0])
        c = self.service.obter_consulta(cod)
        if not c:
            return

        self.ent_cad_cod.delete(0, tk.END)
        self.ent_cad_cod.insert(0, c.codigo_consulta)

        self.ent_cad_desc.delete(0, tk.END)
        self.ent_cad_desc.insert(0, c.descricao_consulta)

        # Tipo de consulta
        if c.tipo_consulta == "C":
            self.cbo_tipo_consulta.set("C - CAMPANHA")
        elif c.tipo_consulta == "M":
            self.cbo_tipo_consulta.set("M - MIX")
        else:
            self.cbo_tipo_consulta.set("I - IMEDIATA")

        self.cbo_cad_banco.set(c.banco_consulta or "ALVO")

        self.txt_sql.delete("1.0", tk.END)
        self.txt_sql.insert("1.0", c.sql_consulta)

        # Atualiza o banner de permissões e sincroniza combo
        info = f"{c.codigo_consulta} - {c.descricao_consulta}"
        self.lbl_perm_consulta_info.config(text=info, foreground="#1E3A8A")
        self.cbo_perm_consulta_sel.set(info)

        self._carregar_permissoes_consulta(c.codigo_consulta)

    def _on_cad_banco_selected(self, event=None):
        """Ao selecionar o banco como Aplicativo RCC ou SAVIC, valida conexão e configurações."""
        banco = (self.cbo_cad_banco.get() or "").strip().upper()
        if banco in ("APLICATIVO RCC", "APLICATIVO"):
            try:
                from entidades.database import obter_conexao_aplicativo_rcc
                conn = obter_conexao_aplicativo_rcc(timeout_seg=5)
                conn.close()
            except Exception as exc:
                messagebox.showwarning(
                    "Conexão - Banco do Aplicativo RCC",
                    f"Atenção ao selecionar o banco do Aplicativo RCC:\n\n{str(exc)}",
                    parent=self
                )
        elif banco == "SAVIC":
            try:
                from config_banco import ConfigManager
                config_mgr = ConfigManager()
                settings = config_mgr.load_savic_settings()
                credentials = config_mgr.get_savic_credentials()
                host = str(settings.get("host") or "").strip()
                db = str(settings.get("database") or "").strip()
                user = str(credentials.get("user") or "").strip()
                if not host or not db or not user:
                    messagebox.showwarning(
                        "Banco de Dados SAVIC",
                        "Solicite ao Administrador a configuração de acesso aos dados do SAVIC",
                        parent=self
                    )
            except Exception:
                messagebox.showwarning(
                    "Banco de Dados SAVIC",
                    "Solicite ao Administrador a configuração de acesso aos dados do SAVIC",
                    parent=self
                )

    def _on_perm_consulta_combo_select(self, event=None):
        sel_text = self.cbo_perm_consulta_sel.get().strip()
        if not sel_text:
            return
        cod = sel_text.split(" - ")[0].strip()
        # Seleciona na árvore de consultas
        for item in self.tree_consultas.get_children():
            if str(self.tree_consultas.item(item, "values")[0]) == cod:
                self.tree_consultas.selection_set(item)
                self.tree_consultas.see(item)
                break
        self._carregar_permissoes_consulta(cod)
        c = self.service.obter_consulta(cod)
        if c:
            info = f"{c.codigo_consulta} - {c.descricao_consulta}"
            self.lbl_perm_consulta_info.config(text=info, foreground="#1E3A8A")

    def _carregar_permissoes_consulta(self, cod_consulta: str):
        for item in self.tree_perm_consultas.get_children():
            self.tree_perm_consultas.delete(item)

        if not self.service or not cod_consulta:
            return

        perms = self.service.listar_permissoes_consulta(cod_consulta)
        for p in perms:
            self.tree_perm_consultas.insert("", tk.END, values=(p.usucod, p.status_display))

    def _nova_consulta(self):
        """Prepara os campos para uma nova consulta e sugere o próximo código sequencial."""
        prox_cod = self.service.obter_proximo_codigo() if self.service else ""
        self.ent_cad_cod.delete(0, tk.END)
        self.ent_cad_cod.insert(0, prox_cod)
        self.ent_cad_desc.delete(0, tk.END)
        self.cbo_tipo_consulta.set("I - IMEDIATA")
        self.cbo_cad_banco.set("ALVO")
        self.txt_sql.delete("1.0", tk.END)
        self.lbl_perm_consulta_info.config(text="Nova Consulta (Não Salva)", foreground="#6B7280")
        for item in self.tree_perm_consultas.get_children():
            self.tree_perm_consultas.delete(item)

    def _salvar_consulta(self):
        """Salva a consulta com confirmação do usuário (Sim/Não)."""
        if not self.service:
            return

        cod = self.ent_cad_cod.get().strip()
        desc = self.ent_cad_desc.get().strip()
        banco = self.cbo_cad_banco.get().strip()
        sql = self.txt_sql.get("1.0", tk.END).strip()

        tipo_raw = self.cbo_tipo_consulta.get().strip()
        tipo = tipo_raw[0] if tipo_raw else "I"

        if not desc:
            messagebox.showwarning("Aviso", "A descrição da consulta é obrigatória.", parent=self)
            return

        if not sql:
            messagebox.showwarning("Aviso", "A instrução SQL é obrigatória.", parent=self)
            return

        if not messagebox.askyesno("Confirmação", "Confirma a gravação dos dados da consulta?", parent=self):
            return

        try:
            dto = ConsultaConfigDTO(
                codigo_consulta=cod,
                descricao_consulta=desc,
                sql_consulta=sql,
                tipo_consulta=tipo,
                banco_consulta=banco,
            )
            self.service.salvar_consulta(dto)
            messagebox.showinfo("Sucesso", "Consulta gravada com sucesso no banco de dados.", parent=self)
            self.carregar_consultas_cadastradas()
            # Seleciona a consulta salva
            for item in self.tree_consultas.get_children():
                if str(self.tree_consultas.item(item, "values")[0]) == cod:
                    self.tree_consultas.selection_set(item)
                    self.tree_consultas.see(item)
                    self._on_consulta_select()
                    break
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", str(e), parent=self)

    def _excluir_consulta(self):
        """Exclui a consulta selecionada com confirmação do usuário (Sim/Não)."""
        if not self.service:
            return
        cod = self.ent_cad_cod.get().strip()
        desc = self.ent_cad_desc.get().strip()

        if not cod:
            messagebox.showwarning("Aviso", "Selecione uma consulta para excluir.", parent=self)
            return

        if not messagebox.askyesno(
            "Confirmação de Exclusão",
            f"Deseja realmente excluir a consulta '{desc or cod}'?\n\nEsta operação não poderá ser desfeita.",
            parent=self
        ):
            return

        try:
            self.service.excluir_consulta(cod)
            messagebox.showinfo("Sucesso", "Consulta excluída com sucesso.", parent=self)
            self._nova_consulta()
            self.carregar_consultas_cadastradas()
        except Exception as e:
            messagebox.showerror("Erro ao Excluir", str(e), parent=self)

    def _aplicar_permissao_click(self):
        """Aplica permissão para o usuário ou grupo selecionado (unt_cadconsulta - spbaplicapermissaoClick)."""
        if not self.service:
            return
        cod_consulta = self.ent_cad_cod.get().strip()
        if not cod_consulta:
            messagebox.showwarning("Aviso", "Selecione uma consulta antes de definir permissões.", parent=self)
            return

        grupo_sel = self.cbo_perm_grupo.get().strip()
        user_raw = self.cbo_perm_usuario.get().strip()
        status = self.var_perm_status.get() == "A"

        # Extrai usucod se houver seleção de usuário
        usucod = ""
        if user_raw and not user_raw.startswith("("):
            usucod = user_raw.split(" - ")[0].strip()

        if not usucod and (not grupo_sel or grupo_sel == "TODOS OS GRUPOS"):
            messagebox.showwarning(
                "Aviso",
                "É OBRIGATÓRIO ESCOLHER UM GRUPO OU UM USUÁRIO PARA APLICAR A PERMISSÃO !!!",
                parent=self
            )
            return

        alvo_str = f"ao usuário '{usucod}'" if usucod else f"a todos os usuários do grupo '{grupo_sel}'"
        tipo_str = "AUTORIZAR" if status else "NEGAR"

        if not messagebox.askyesno(
            "Confirmação",
            f"Confirma esta permissão ({tipo_str}) para a consulta selecionada {alvo_str}?",
            parent=self
        ):
            return

        sucesso, msg = self.service.aplicar_permissao(
            codigo_consulta=cod_consulta,
            autorizada=status,
            usucod=usucod if usucod else None,
            grupo=grupo_sel if (not usucod and grupo_sel != "TODOS OS GRUPOS") else None,
        )

        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self._carregar_permissoes_consulta(cod_consulta)
        else:
            messagebox.showerror("Erro", msg, parent=self)

    def _remover_permissao_click(self):
        """Remove a permissão do usuário selecionado na grade."""
        if not self.service:
            return
        cod_consulta = self.ent_cad_cod.get().strip()
        sel = self.tree_perm_consultas.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um usuário na grade para remover a permissão.", parent=self)
            return

        usucod = str(self.tree_perm_consultas.item(sel[0], "values")[0])
        if not messagebox.askyesno("Confirmação", f"Deseja remover a permissão do usuário '{usucod}' desta consulta?", parent=self):
            return

        sucesso = self.service.remover_permissao(usucod, cod_consulta)
        if sucesso:
            messagebox.showinfo("Sucesso", f"Permissão do usuário '{usucod}' removida com sucesso.", parent=self)
            self._carregar_permissoes_consulta(cod_consulta)
        else:
            messagebox.showerror("Erro", "Erro ao remover permissão.", parent=self)

    def _clonar_permissoes_click(self):
        """Clona todas as permissões de consultas de um usuário para outro (unt_cadconsulta - GroupBox4)."""
        if not self.service:
            return

        raw_orig = self.cbo_clone_origem.get().strip()
        raw_dest = self.cbo_clone_destino.get().strip()

        u_orig = raw_orig.split(" - ")[0].strip() if raw_orig else ""
        u_dest = raw_dest.split(" - ")[0].strip() if raw_dest else ""

        if not u_orig or not u_dest:
            messagebox.showwarning("Aviso", "Selecione os usuários de origem e destino para clonar.", parent=self)
            return

        if u_orig == u_dest:
            messagebox.showwarning("Aviso", "O usuário de origem e de destino devem ser diferentes.", parent=self)
            return

        if not messagebox.askyesno(
            "Confirmação de Clonagem",
            f"Deseja realmente copiar todas as permissões de consultas do usuário '{u_orig}' para o usuário '{u_dest}'?",
            parent=self
        ):
            return

        sucesso, msg = self.service.clonar_permissoes(u_orig, u_dest)
        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            cod_atual = self.ent_cad_cod.get().strip()
            if cod_atual:
                self._carregar_permissoes_consulta(cod_atual)
        else:
            messagebox.showerror("Erro", msg, parent=self)

    def _set_permissao(self, autorizada: bool):
        """Método legado de permissão mantido para compatibilidade."""
        self.var_perm_status.set("A" if autorizada else "N")
        self._aplicar_permissao_click()

    def _abrir_imediatas_funil(self):
        from consultas.imediatas_view import abrir_consultas_imediatas
        abrir_consultas_imediatas(self.winfo_toplevel())

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
