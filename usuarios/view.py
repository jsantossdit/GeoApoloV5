"""
Interface Gráfica para Gestão de Usuários, Grupos e Perfis de Acesso.
GeoApolo V5
Desenvolvido em Tkinter / ttk com suporte a execução headless em testes unitários.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List

from usuarios.models import (
    UsuarioDTO,
    DepartamentoDTO,
    SistemaDTO,
    GrupoUsuarioDTO,
    VinculoGrupoUsuarioDTO,
    PerfilAcessoItemDTO,
)
from usuarios.service import UsuariosService


class UsuariosView(ttk.Frame):
    """View corporativa com 3 abas: Usuários, Grupos de Usuários e Perfis de Acesso."""

    def __init__(self, parent=None, service: Optional[UsuariosService] = None, connection=None):
        super().__init__(parent)
        self.service = service
        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from usuarios.repository import UsuariosRepository
                conn = connection or obter_conexao_banco()
                self.service = UsuariosService(UsuariosRepository(conn))
            except Exception:
                pass

        self.departamentos: List[DepartamentoDTO] = []
        self.sistemas_disponiveis: List[SistemaDTO] = []
        self.todos_usuarios: List[UsuarioDTO] = []

        self._setup_ui()
        if self.service:
            self._carregar_dados_iniciais()

    def _setup_ui(self):
        # Header Superior
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        lbl_titulo = ttk.Label(
            header,
            text="Gestão de Usuários, Grupos e Perfis de Acesso",
            font=("Segoe UI", 13, "bold"),
            foreground="#1E3A8A"
        )
        lbl_titulo.pack(side=tk.LEFT)

        lbl_sub = ttk.Label(
            header,
            text="Controle unificado de credenciais, vínculos corporativos e permissões de segurança",
            font=("Segoe UI", 9),
            foreground="#6B7280"
        )
        lbl_sub.pack(side=tk.LEFT, padx=15)

        # Notebook com 3 Abas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tab_usuarios = ttk.Frame(self.notebook, padding=10)
        self.tab_grupos = ttk.Frame(self.notebook, padding=10)
        self.tab_perfis = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_usuarios, text="  Usuários do Sistema  ")
        self.notebook.add(self.tab_grupos, text="  Grupos de Usuários  ")
        self.notebook.add(self.tab_perfis, text="  Perfis de Acesso (Telas & Recursos)  ")

        self._build_tab_usuarios()
        self._build_tab_grupos()
        self._build_tab_perfis()

    # =========================================================================
    # ABA 1: USUÁRIOS & SISTEMAS
    # =========================================================================
    def _build_tab_usuarios(self):
        paned = ttk.PanedWindow(self.tab_usuarios, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Painel Esquerdo: Lista e Filtros
        left_frame = ttk.Frame(paned, padding=5)
        paned.add(left_frame, weight=1)

        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(filter_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        self.ent_busca_user = ttk.Entry(filter_frame, width=20)
        self.ent_busca_user.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.ent_busca_user.bind("<Return>", lambda e: self.pesquisar_usuarios())

        self.var_apenas_ativos = tk.BooleanVar(value=True)
        chk_ativos = ttk.Checkbutton(
            filter_frame, text="Apenas Ativos", variable=self.var_apenas_ativos,
            command=self.pesquisar_usuarios
        )
        chk_ativos.pack(side=tk.LEFT, padx=(0, 5))

        btn_busca = ttk.Button(filter_frame, text="Pesquisar", command=self.pesquisar_usuarios)
        btn_busca.pack(side=tk.LEFT)

        # Grid de Usuários
        cols = ("usucod", "login", "nome", "depto", "status")
        self.tree_users = ttk.Treeview(left_frame, columns=cols, show="headings", selectmode="browse")
        self.tree_users.heading("usucod", text="Código")
        self.tree_users.heading("login", text="Login")
        self.tree_users.heading("nome", text="Nome Completo")
        self.tree_users.heading("depto", text="Departamento")
        self.tree_users.heading("status", text="Status")

        self.tree_users.column("usucod", width=70, anchor=tk.CENTER)
        self.tree_users.column("login", width=100)
        self.tree_users.column("nome", width=180)
        self.tree_users.column("depto", width=140)
        self.tree_users.column("status", width=70, anchor=tk.CENTER)

        scroll_users = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree_users.yview)
        self.tree_users.configure(yscrollcommand=scroll_users.set)
        self.tree_users.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_users.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_users.bind("<<TreeviewSelect>>", self._on_user_select)

        # Painel Direito: Formulário e Vínculo de Sistemas
        right_frame = ttk.Frame(paned, padding=10)
        paned.add(right_frame, weight=1)

        lbl_form = ttk.Label(right_frame, text="Ficha Cadastral do Usuário", font=("Segoe UI", 10, "bold"))
        lbl_form.pack(anchor=tk.W, pady=(0, 10))

        form_grid = ttk.Frame(right_frame)
        form_grid.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(form_grid, text="Código (Usucod):").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.ent_usucod = ttk.Entry(form_grid, width=15)
        self.ent_usucod.grid(row=0, column=1, sticky=tk.W, padx=5, pady=3)

        self.var_user_ativo = tk.BooleanVar(value=True)
        chk_status = ttk.Checkbutton(form_grid, text="Usuário Ativo", variable=self.var_user_ativo)
        chk_status.grid(row=0, column=2, sticky=tk.W, padx=10, pady=3)

        ttk.Label(form_grid, text="Login de Acesso:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.ent_login = ttk.Entry(form_grid, width=25)
        self.ent_login.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=3)

        ttk.Label(form_grid, text="Nome Completo:").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.ent_nome = ttk.Entry(form_grid, width=35)
        self.ent_nome.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=5, pady=3)

        ttk.Label(form_grid, text="E-mail:").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.ent_email = ttk.Entry(form_grid, width=35)
        self.ent_email.grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=5, pady=3)

        ttk.Label(form_grid, text="Departamento:").grid(row=4, column=0, sticky=tk.W, pady=3)
        self.cbo_departamento = ttk.Combobox(form_grid, state="readonly", width=32)
        self.cbo_departamento.grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=5, pady=3)

        ttk.Label(form_grid, text="Senha Alvo / Hash:").grid(row=5, column=0, sticky=tk.W, pady=3)
        self.ent_senha = ttk.Entry(form_grid, width=25, show="*")
        self.ent_senha.grid(row=5, column=1, columnspan=2, sticky=tk.W, padx=5, pady=3)

        # Botões de Ação do Usuário
        btn_box = ttk.Frame(right_frame)
        btn_box.pack(fill=tk.X, pady=(0, 15))

        btn_novo = ttk.Button(btn_box, text="Novo", command=self._novo_usuario)
        btn_novo.pack(side=tk.LEFT, padx=(0, 5))

        btn_salvar = ttk.Button(btn_box, text="Salvar Usuário", command=self._salvar_usuario)
        btn_salvar.pack(side=tk.LEFT, padx=(0, 5))

        btn_excluir = ttk.Button(btn_box, text="Excluir Usuário", command=self._excluir_usuario)
        btn_excluir.pack(side=tk.LEFT, padx=(0, 5))

        # Seção Sistemas Vinculados
        sep = ttk.Separator(right_frame, orient=tk.HORIZONTAL)
        sep.pack(fill=tk.X, pady=5)

        ttk.Label(right_frame, text="Sistemas Vinculados", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(5, 5))

        sis_frame = ttk.Frame(right_frame)
        sis_frame.pack(fill=tk.BOTH, expand=True)

        cols_sis = ("cod", "descricao", "sigla")
        self.tree_sistemas_user = ttk.Treeview(sis_frame, columns=cols_sis, show="headings", height=4)
        self.tree_sistemas_user.heading("cod", text="Cód.")
        self.tree_sistemas_user.heading("descricao", text="Sistema")
        self.tree_sistemas_user.heading("sigla", text="Sigla")
        self.tree_sistemas_user.column("cod", width=50, anchor=tk.CENTER)
        self.tree_sistemas_user.column("descricao", width=180)
        self.tree_sistemas_user.column("sigla", width=80, anchor=tk.CENTER)
        self.tree_sistemas_user.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sis_actions = ttk.Frame(right_frame)
        sis_actions.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(sis_actions, text="Adicionar Sistema:").pack(side=tk.LEFT, padx=(0, 5))
        self.cbo_novo_sistema = ttk.Combobox(sis_actions, state="readonly", width=20)
        self.cbo_novo_sistema.pack(side=tk.LEFT, padx=(0, 5))

        btn_add_sis = ttk.Button(sis_actions, text="Vincular", command=self._vincular_sistema)
        btn_add_sis.pack(side=tk.LEFT, padx=(0, 5))

        btn_rem_sis = ttk.Button(sis_actions, text="Remover", command=self._desvincular_sistema)
        btn_rem_sis.pack(side=tk.LEFT)

    # =========================================================================
    # ABA 2: GRUPOS DE USUÁRIOS
    # =========================================================================
    def _build_tab_grupos(self):
        paned = ttk.PanedWindow(self.tab_grupos, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Painel Esquerdo: Lista de Grupos
        left = ttk.Frame(paned, padding=5)
        paned.add(left, weight=1)

        ttk.Label(left, text="Grupos de Usuários", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        cols_grp = ("cod", "descricao", "qtd")
        self.tree_grupos = ttk.Treeview(left, columns=cols_grp, show="headings", selectmode="browse")
        self.tree_grupos.heading("cod", text="Código")
        self.tree_grupos.heading("descricao", text="Descrição do Grupo")
        self.tree_grupos.heading("qtd", text="Qtd. Usuários")
        self.tree_grupos.column("cod", width=80, anchor=tk.CENTER)
        self.tree_grupos.column("descricao", width=200)
        self.tree_grupos.column("qtd", width=100, anchor=tk.CENTER)
        self.tree_grupos.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.tree_grupos.bind("<<TreeviewSelect>>", self._on_grupo_select)

        form_grp = ttk.Frame(left)
        form_grp.pack(fill=tk.X, pady=5)

        ttk.Label(form_grp, text="Cód:").grid(row=0, column=0, sticky=tk.W)
        self.ent_grp_cod = ttk.Entry(form_grp, width=10)
        self.ent_grp_cod.grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(form_grp, text="Descrição:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        self.ent_grp_desc = ttk.Entry(form_grp, width=22)
        self.ent_grp_desc.grid(row=0, column=3, sticky=tk.W, padx=5)

        grp_btns = ttk.Frame(left)
        grp_btns.pack(fill=tk.X, pady=5)

        ttk.Button(grp_btns, text="Novo Grupo", command=self._novo_grupo).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(grp_btns, text="Salvar Grupo", command=self._salvar_grupo).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(grp_btns, text="Excluir Grupo", command=self._excluir_grupo).pack(side=tk.LEFT)

        # Painel Direito: Usuários do Grupo
        right = ttk.Frame(paned, padding=5)
        paned.add(right, weight=1)

        ttk.Label(right, text="Membros do Grupo Selecionado", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        cols_membros = ("usucod", "login", "nome")
        self.tree_membros_grupo = ttk.Treeview(right, columns=cols_membros, show="headings", selectmode="browse")
        self.tree_membros_grupo.heading("usucod", text="Código")
        self.tree_membros_grupo.heading("login", text="Login")
        self.tree_membros_grupo.heading("nome", text="Nome do Usuário")
        self.tree_membros_grupo.column("usucod", width=70, anchor=tk.CENTER)
        self.tree_membros_grupo.column("login", width=100)
        self.tree_membros_grupo.column("nome", width=200)
        self.tree_membros_grupo.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        membros_actions = ttk.Frame(right)
        membros_actions.pack(fill=tk.X, pady=5)

        ttk.Label(membros_actions, text="Adicionar Colaborador:").pack(side=tk.LEFT, padx=(0, 5))
        self.cbo_add_usuario_grupo = ttk.Combobox(membros_actions, state="readonly", width=25)
        self.cbo_add_usuario_grupo.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(membros_actions, text="Adicionar", command=self._adicionar_membro_grupo).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(membros_actions, text="Remover Membro", command=self._remover_membro_grupo).pack(side=tk.LEFT)

    # =========================================================================
    # ABA 3: PERFIS DE ACESSO / TELAS
    # =========================================================================
    def _build_tab_perfis(self):
        top_bar = ttk.Frame(self.tab_perfis, padding=5)
        top_bar.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(top_bar, text="Grupo de Segurança:").pack(side=tk.LEFT, padx=(0, 5))
        self.cbo_perfil_grupo = ttk.Combobox(top_bar, state="readonly", width=25)
        self.cbo_perfil_grupo.pack(side=tk.LEFT, padx=(0, 15))
        self.cbo_perfil_grupo.bind("<<ComboboxSelected>>", lambda e: self.carregar_perfil_objetos())

        ttk.Label(top_bar, text="Categoria:").pack(side=tk.LEFT, padx=(0, 5))
        self.cbo_perfil_cat = ttk.Combobox(top_bar, state="readonly", width=20)
        self.cbo_perfil_cat.pack(side=tk.LEFT, padx=(0, 10))
        self.cbo_perfil_cat.bind("<<ComboboxSelected>>", lambda e: self.carregar_perfil_objetos())

        ttk.Button(top_bar, text="Atualizar Lista", command=self.carregar_perfil_objetos).pack(side=tk.LEFT)

        # Grid de Permissões
        grid_frame = ttk.Frame(self.tab_perfis)
        grid_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        cols_obj = ("cod", "nome_tecnico", "nome_amigavel", "categoria", "status")
        self.tree_perfis = ttk.Treeview(grid_frame, columns=cols_obj, show="headings", selectmode="browse")
        self.tree_perfis.heading("cod", text="Código")
        self.tree_perfis.heading("nome_tecnico", text="Objeto / Classe")
        self.tree_perfis.heading("nome_amigavel", text="Título / Tela Amigável")
        self.tree_perfis.heading("categoria", text="Categoria")
        self.tree_perfis.heading("status", text="Permissão")

        self.tree_perfis.column("cod", width=60, anchor=tk.CENTER)
        self.tree_perfis.column("nome_tecnico", width=180)
        self.tree_perfis.column("nome_amigavel", width=240)
        self.tree_perfis.column("categoria", width=120)
        self.tree_perfis.column("status", width=90, anchor=tk.CENTER)

        scroll_perf = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.tree_perfis.yview)
        self.tree_perfis.configure(yscrollcommand=scroll_perf.set)
        self.tree_perfis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_perf.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_perfis.bind("<Double-1>", lambda e: self._toggle_permissao_selecionada())

        # Ações de Permissão
        action_bar = ttk.Frame(self.tab_perfis, padding=5)
        action_bar.pack(fill=tk.X, pady=5)

        ttk.Button(action_bar, text="Liberar Selecionado (A)", command=lambda: self._set_permissao_selecionada(True)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_bar, text="Bloquear Selecionado (N)", command=lambda: self._set_permissao_selecionada(False)).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Button(action_bar, text="Liberar Todos da Lista", command=lambda: self._set_permissao_todos(True)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_bar, text="Bloquear Todos da Lista", command=lambda: self._set_permissao_todos(False)).pack(side=tk.LEFT)

    # =========================================================================
    # MÉTODOS DE DADOS & CONTROLLER
    # =========================================================================
    def _carregar_dados_iniciais(self):
        try:
            self.departamentos = self.service.listar_departamentos()
            dept_values = [f"{d.codigo_departamento} - {d.nome_departamento}" for d in self.departamentos]
            self.cbo_departamento["values"] = dept_values

            self.sistemas_disponiveis = self.service.listar_sistemas()
            sis_values = [f"{s.codigo_sistema} - {s.descricao}" for s in self.sistemas_disponiveis]
            self.cbo_novo_sistema["values"] = sis_values

            self.pesquisar_usuarios()
            self.carregar_grupos()
            self.carregar_categorias_perfil()
        except Exception as e:
            # Em modo headless / testes, erros silenciosos de banco são tolerados
            pass

    def pesquisar_usuarios(self):
        filtro = self.ent_busca_user.get()
        apenas_ativos = self.var_apenas_ativos.get()

        for item in self.tree_users.get_children():
            self.tree_users.delete(item)

        self.todos_usuarios = self.service.listar_usuarios(filtro, apenas_ativos)
        user_cbo_values = []
        for u in self.todos_usuarios:
            user_cbo_values.append(f"{u.usucod} - {u.nome_completo}")
            self.tree_users.insert("", tk.END, values=(
                u.usucod, u.login, u.nome_completo, u.nome_departamento, u.status_display
            ))

        self.cbo_add_usuario_grupo["values"] = user_cbo_values

    def _on_user_select(self, event):
        sel = self.tree_users.selection()
        if not sel:
            return
        vals = self.tree_users.item(sel[0], "values")
        if not vals:
            return
        usucod = vals[0]
        usuario = self.service.obter_usuario(usucod)
        if not usuario:
            return

        self.ent_usucod.delete(0, tk.END)
        self.ent_usucod.insert(0, usuario.usucod)

        self.ent_login.delete(0, tk.END)
        self.ent_login.insert(0, usuario.login)

        self.ent_nome.delete(0, tk.END)
        self.ent_nome.insert(0, usuario.nome_completo)

        self.ent_email.delete(0, tk.END)
        self.ent_email.insert(0, usuario.email)

        self.ent_senha.delete(0, tk.END)
        self.ent_senha.insert(0, usuario.senha_alvo)

        self.var_user_ativo.set(usuario.ativo)

        # Seleciona depto na combo
        for v in self.cbo_departamento["values"]:
            if v.startswith(f"{usuario.codigo_departamento} -"):
                self.cbo_departamento.set(v)
                break
        else:
            self.cbo_departamento.set("")

        self._carregar_sistemas_usuario(usuario.usucod)

    def _carregar_sistemas_usuario(self, usucod: str):
        for item in self.tree_sistemas_user.get_children():
            self.tree_sistemas_user.delete(item)

        sistemas = self.service.listar_sistemas_usuario(usucod)
        for s in sistemas:
            self.tree_sistemas_user.insert("", tk.END, values=(s.codigo_sistema, s.descricao, s.sigla))

    def _novo_usuario(self):
        self.ent_usucod.delete(0, tk.END)
        self.ent_login.delete(0, tk.END)
        self.ent_nome.delete(0, tk.END)
        self.ent_email.delete(0, tk.END)
        self.ent_senha.delete(0, tk.END)
        self.cbo_departamento.set("")
        self.var_user_ativo.set(True)
        for item in self.tree_sistemas_user.get_children():
            self.tree_sistemas_user.delete(item)

    def _salvar_usuario(self):
        usucod = self.ent_usucod.get().strip()
        login = self.ent_login.get().strip()
        nome = self.ent_nome.get().strip()
        email = self.ent_email.get().strip()
        senha = self.ent_senha.get().strip()
        ativo = "A" if self.var_user_ativo.get() else "I"

        depto_sel = self.cbo_departamento.get()
        cod_depto = depto_sel.split(" - ")[0] if " - " in depto_sel else ""

        u = UsuarioDTO(
            usucod=usucod,
            login=login,
            nome_completo=nome,
            email=email,
            codigo_departamento=cod_depto,
            flagativo=ativo,
            senha_alvo=senha,
        )

        res = self.service.salvar_usuario(u)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.pesquisar_usuarios()
        else:
            messagebox.showerror("Atenção", res.mensagem)

    def _excluir_usuario(self):
        usucod = self.ent_usucod.get().strip()
        if not usucod:
            messagebox.showwarning("Aviso", "Selecione um usuário para excluir.")
            return

        if not messagebox.askyesno("Confirmação", f"Deseja realmente excluir o usuário '{usucod}'?"):
            return

        res = self.service.excluir_usuario(usucod)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self._novo_usuario()
            self.pesquisar_usuarios()
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _vincular_sistema(self):
        usucod = self.ent_usucod.get().strip()
        sel = self.cbo_novo_sistema.get()
        if not usucod or not sel:
            messagebox.showwarning("Aviso", "Selecione um usuário e um sistema para vincular.")
            return
        cod_sis = sel.split(" - ")[0]
        res = self.service.vincular_sistema(usucod, cod_sis)
        if res.sucesso:
            self._carregar_sistemas_usuario(usucod)
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _desvincular_sistema(self):
        usucod = self.ent_usucod.get().strip()
        sel = self.tree_sistemas_user.selection()
        if not usucod or not sel:
            messagebox.showwarning("Aviso", "Selecione um sistema da lista para desvincular.")
            return
        cod_sis = self.tree_sistemas_user.item(sel[0], "values")[0]
        res = self.service.desvincular_sistema(usucod, cod_sis)
        if res.sucesso:
            self._carregar_sistemas_usuario(usucod)
        else:
            messagebox.showerror("Erro", res.mensagem)

    # -------------------------------------------------------------------------
    # MÉTODOS GRUPOS
    # -------------------------------------------------------------------------
    def carregar_grupos(self):
        for item in self.tree_grupos.get_children():
            self.tree_grupos.delete(item)

        grupos = self.service.listar_grupos()
        grp_cbo = []
        for g in grupos:
            grp_cbo.append(f"{g.codigo_grupo} - {g.descricao}")
            self.tree_grupos.insert("", tk.END, values=(g.codigo_grupo, g.descricao, g.total_usuarios))

        self.cbo_perfil_grupo["values"] = grp_cbo

    def _on_grupo_select(self, event):
        sel = self.tree_grupos.selection()
        if not sel:
            return
        vals = self.tree_grupos.item(sel[0], "values")
        cod = vals[0]
        desc = vals[1]

        self.ent_grp_cod.delete(0, tk.END)
        self.ent_grp_cod.insert(0, cod)

        self.ent_grp_desc.delete(0, tk.END)
        self.ent_grp_desc.insert(0, desc)

        self._carregar_membros_grupo(cod)

    def _carregar_membros_grupo(self, cod_grupo: str):
        for item in self.tree_membros_grupo.get_children():
            self.tree_membros_grupo.delete(item)

        membros = self.service.listar_usuarios_grupo(cod_grupo)
        for m in membros:
            self.tree_membros_grupo.insert("", tk.END, values=(m.usucod, m.login, m.nome_completo))

    def _novo_grupo(self):
        self.ent_grp_cod.delete(0, tk.END)
        self.ent_grp_desc.delete(0, tk.END)
        for item in self.tree_membros_grupo.get_children():
            self.tree_membros_grupo.delete(item)

    def _salvar_grupo(self):
        cod = self.ent_grp_cod.get().strip()
        desc = self.ent_grp_desc.get().strip()
        res = self.service.salvar_grupo(cod, desc)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.carregar_grupos()
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _excluir_grupo(self):
        cod = self.ent_grp_cod.get().strip()
        if not cod:
            messagebox.showwarning("Aviso", "Informe o grupo para exclusão.")
            return

        if not messagebox.askyesno("Confirmação", f"Excluir grupo '{cod}' e todos os seus vínculos?"):
            return

        res = self.service.excluir_grupo(cod)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self._novo_grupo()
            self.carregar_grupos()
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _adicionar_membro_grupo(self):
        cod_grupo = self.ent_grp_cod.get().strip()
        user_sel = self.cbo_add_usuario_grupo.get()
        if not cod_grupo or not user_sel:
            messagebox.showwarning("Aviso", "Selecione um grupo e um colaborador.")
            return
        usucod = user_sel.split(" - ")[0]
        res = self.service.vincular_usuario_grupo(cod_grupo, usucod)
        if res.sucesso:
            self._carregar_membros_grupo(cod_grupo)
            self.carregar_grupos()
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _remover_membro_grupo(self):
        cod_grupo = self.ent_grp_cod.get().strip()
        sel = self.tree_membros_grupo.selection()
        if not cod_grupo or not sel:
            messagebox.showwarning("Aviso", "Selecione um membro para remover.")
            return
        usucod = self.tree_membros_grupo.item(sel[0], "values")[0]
        res = self.service.desvincular_usuario_grupo(cod_grupo, usucod)
        if res.sucesso:
            self._carregar_membros_grupo(cod_grupo)
            self.carregar_grupos()
        else:
            messagebox.showerror("Erro", res.mensagem)

    # -------------------------------------------------------------------------
    # MÉTODOS PERFIS DE ACESSO
    # -------------------------------------------------------------------------
    def carregar_categorias_perfil(self):
        cats = self.service.listar_categorias_objetos()
        self.cbo_perfil_cat["values"] = ["Todas"] + cats
        self.cbo_perfil_cat.set("Todas")

    def carregar_perfil_objetos(self):
        for item in self.tree_perfis.get_children():
            self.tree_perfis.delete(item)

        grp_sel = self.cbo_perfil_grupo.get()
        if not grp_sel:
            return
        cod_grupo = grp_sel.split(" - ")[0]

        cat_sel = self.cbo_perfil_cat.get()
        cat = "" if cat_sel in ("", "Todas") else cat_sel

        itens = self.service.listar_objetos_perfil(cod_grupo, cat)
        for it in itens:
            self.tree_perfis.insert("", tk.END, values=(
                it.codigo_objeto, it.nome_objeto, it.nome_amigavel, it.categoria, it.status_display
            ))

    def _toggle_permissao_selecionada(self):
        sel = self.tree_perfis.selection()
        if not sel:
            return
        vals = self.tree_perfis.item(sel[0], "values")
        cod_obj = vals[0]
        atual_liberado = (vals[4] == "Liberado")
        self._atualizar_permissao_objeto(cod_obj, not atual_liberado)

    def _set_permissao_selecionada(self, liberado: bool):
        sel = self.tree_perfis.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um recurso da lista.")
            return
        cod_obj = self.tree_perfis.item(sel[0], "values")[0]
        self._atualizar_permissao_objeto(cod_obj, liberado)

    def _set_permissao_todos(self, liberado: bool):
        grp_sel = self.cbo_perfil_grupo.get()
        if not grp_sel:
            messagebox.showwarning("Aviso", "Selecione um grupo de segurança primeiro.")
            return
        cod_grupo = grp_sel.split(" - ")[0]

        for item in self.tree_perfis.get_children():
            vals = self.tree_perfis.item(item, "values")
            cod_obj = vals[0]
            self.service.atualizar_acesso(cod_grupo, cod_obj, liberado)

        self.carregar_perfil_objetos()

    def _atualizar_permissao_objeto(self, cod_objeto: str, liberado: bool):
        grp_sel = self.cbo_perfil_grupo.get()
        if not grp_sel:
            return
        cod_grupo = grp_sel.split(" - ")[0]
        res = self.service.atualizar_acesso(cod_grupo, cod_objeto, liberado)
        if res.sucesso:
            self.carregar_perfil_objetos()
        else:
            messagebox.showerror("Erro", res.mensagem)
