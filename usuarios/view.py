"""
Interface Gráfica para Gestão de Usuários, Grupos e Perfis de Acesso.
GeoApolo V5
Desenvolvido em Tkinter / ttk com suporte a execução headless em testes unitários.
"""

import sys
from pathlib import Path

# Garante que o diretório raiz esteja no sys.path
_raiz_projeto = str(Path(__file__).resolve().parent.parent)
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from PIL import Image, ImageTk

from core.recursos import (
    obter_caminho_recurso,
    configurar_navegacao_enter,
    vincular_maiusculo,
    geoapolo_configcod,
)
from core.criptografia import criptografia, decriptografia

try:
    from usuarios.models import (
        UsuarioDTO,
        DepartamentoDTO,
        SistemaDTO,
        GrupoUsuarioDTO,
        VinculoGrupoUsuarioDTO,
        PerfilAcessoItemDTO,
    )
    from usuarios.service import UsuariosService
except (ImportError, ModuleNotFoundError):
    from models import (
        UsuarioDTO,
        DepartamentoDTO,
        SistemaDTO,
        GrupoUsuarioDTO,
        VinculoGrupoUsuarioDTO,
        PerfilAcessoItemDTO,
    )
    from service import UsuariosService


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
        self._icones_cache = []
        self._senha_cifrada_cache = ""
        self._codigo_usuario_atual = ""

        self._setup_ui()
        if self.service:
            self._carregar_dados_iniciais()

    def _obter_empresa_atual(self) -> str:
        try:
            from variaveis_globais import sessao_usuario_atual
            return str(sessao_usuario_atual.get("codigo_empresa") or "1")
        except Exception:
            return "1"

    def _garantir_foco(self):
        try:
            top = self.winfo_toplevel()
            top.lift()
            top.focus_force()
        except Exception:
            pass

    def _msg_info(self, titulo: str, mensagem: str):
        messagebox.showinfo(titulo, mensagem, parent=self)
        self._garantir_foco()

    def _msg_warning(self, titulo: str, mensagem: str):
        messagebox.showwarning(titulo, mensagem, parent=self)
        self._garantir_foco()

    def _msg_error(self, titulo: str, mensagem: str):
        messagebox.showerror(titulo, mensagem, parent=self)
        self._garantir_foco()

    def _msg_askyesno(self, titulo: str, mensagem: str) -> bool:
        res = messagebox.askyesno(titulo, mensagem, parent=self)
        self._garantir_foco()
        return res

    def _carregar_icone(self, nome_arquivo: str, tamanho=(22, 22)) -> Optional[ImageTk.PhotoImage]:
        """Carrega ícone da pasta Imagens com tratamento seguro e redimensionamento."""
        try:
            caminho_base = obter_caminho_recurso("Imagens")
            caminho_completo = os.path.join(caminho_base, nome_arquivo)
            if os.path.exists(caminho_completo):
                img = Image.open(caminho_completo).convert("RGBA")
                img = img.resize(tamanho, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img, master=self)
                self._icones_cache.append(photo)
                return photo
        except Exception:
            pass
        return None

    def _criar_tooltip(self, widget: tk.Widget, texto: str):
        """Associa uma tooltip descritiva a um componente visual."""
        def show_tooltip(event):
            if hasattr(widget, "tooltip_win") and widget.tooltip_win:
                try:
                    widget.tooltip_win.destroy()
                except Exception:
                    pass

            tip = tk.Toplevel()
            tip.wm_overrideredirect(True)
            tip.configure(bg="#FFFFE0", relief="solid", bd=1)

            lbl = tk.Label(
                tip,
                text=texto,
                bg="#FFFFE0",
                fg="#1A202C",
                font=("Segoe UI", 9),
                padx=6,
                pady=3,
            )
            lbl.pack()

            x = event.x_root + 10
            y = event.y_root + 18
            tip.geometry(f"+{x}+{y}")

            widget.tooltip_win = tip
            tip.after(3500, lambda: hide_tooltip(None))

        def hide_tooltip(event=None):
            if hasattr(widget, "tooltip_win") and widget.tooltip_win:
                try:
                    widget.tooltip_win.destroy()
                except Exception:
                    pass
                delattr(widget, "tooltip_win")

        widget.bind("<Enter>", show_tooltip, add="+")
        widget.bind("<Leave>", hide_tooltip, add="+")

    def _alternar_decriptografia_senha(self):
        """Decriptografa a senha para o usuário 'julio'."""
        senha_atual = self.ent_senha.get().strip()
        if not senha_atual:
            self._msg_info("Senha", "Nenhuma senha cadastrada para este usuário.")
            return

        if self.ent_senha.cget("show") == "*":
            # Está oculto/cifrado: decriptografa e revela
            senha_dec = decriptografia(32, senha_atual)
            self._senha_cifrada_cache = senha_atual
            self.ent_senha.delete(0, tk.END)
            self.ent_senha.insert(0, senha_dec)
            self.ent_senha.configure(show="")
            self._msg_info(
                "Senha Decriptografada",
                f"Usuário: {self.ent_login.get()}\n\nSenha Decriptografada: {senha_dec}"
            )
        else:
            # Está exibindo texto claro: re-cifra e oculta com *
            if self._senha_cifrada_cache and senha_atual == decriptografia(32, self._senha_cifrada_cache):
                senha_cifrada = self._senha_cifrada_cache
            else:
                senha_cifrada = criptografia(32, senha_atual)
            self.ent_senha.delete(0, tk.END)
            self.ent_senha.insert(0, senha_cifrada)
            self.ent_senha.configure(show="*")

    def _atualizar_visibilidade_btn_decript(self):
        """Exibe o botão de decriptografia exclusivamente quando o usuário for 'julio'."""
        if not hasattr(self, "btn_decript_senha"):
            return
        login = self.ent_login.get().strip().lower()
        usucod = self.ent_usucod.get().strip().lower()
        if login == "julio" or usucod == "julio":
            if self.btn_decript_senha.winfo_manager() != "pack":
                self.btn_decript_senha.pack(side=tk.LEFT, padx=(5, 0))
        else:
            if self.btn_decript_senha.winfo_manager() == "pack":
                self.btn_decript_senha.pack_forget()
            if self.ent_senha.cget("show") != "*":
                self.ent_senha.configure(show="*")

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
        self.ent_usucod.bind("<KeyRelease>", lambda e: self._atualizar_visibilidade_btn_decript())

        self.var_user_ativo = tk.BooleanVar(value=True)
        chk_status = ttk.Checkbutton(form_grid, text="Usuário Ativo", variable=self.var_user_ativo)
        chk_status.grid(row=0, column=2, sticky=tk.W, padx=10, pady=3)

        ttk.Label(form_grid, text="Login de Acesso:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.ent_login = ttk.Entry(form_grid, width=25)
        self.ent_login.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=3)
        self.ent_login.bind("<KeyRelease>", lambda e: self._atualizar_visibilidade_btn_decript())

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
        senha_box = ttk.Frame(form_grid)
        senha_box.grid(row=5, column=1, columnspan=2, sticky=tk.W, padx=5, pady=3)

        self.ent_senha = ttk.Entry(senha_box, width=25, show="*")
        self.ent_senha.pack(side=tk.LEFT)

        # Botão de decriptografia de senha visível exclusivamente para o usuário 'julio'
        ico_key = self._carregar_icone("key.png", (20, 20))
        self.btn_decript_senha = ttk.Button(
            senha_box,
            image=ico_key,
            text="",
            command=self._alternar_decriptografia_senha
        )
        self._criar_tooltip(self.btn_decript_senha, "Decriptografar senha do usuário 'julio'")
        # Permanece oculto inicialmente até seleção/digitação do usuário 'julio'

        # Navegação com Enter encadeada
        configurar_navegacao_enter([
            self.ent_usucod,
            self.ent_login,
            self.ent_nome,
            self.ent_email,
            self.cbo_departamento,
            self.ent_senha,
        ])

        # Botões de Ação do Usuário
        btn_box = ttk.Frame(right_frame)
        btn_box.pack(fill=tk.X, pady=(0, 15))

        ico_novo = self._carregar_icone("user_add.png", (22, 22))
        self.btn_novo = ttk.Button(btn_box, image=ico_novo, text="", command=self._novo_usuario)
        self.btn_novo.pack(side=tk.LEFT, padx=(0, 5))
        self._criar_tooltip(self.btn_novo, "Novo Usuário")

        ico_salvar = self._carregar_icone("salvar.png", (22, 22))
        self.btn_salvar = ttk.Button(btn_box, image=ico_salvar, text="", command=self._salvar_usuario)
        self.btn_salvar.pack(side=tk.LEFT, padx=(0, 5))
        self._criar_tooltip(self.btn_salvar, "Salva o Usuário")

        ico_excluir = self._carregar_icone("user_delete.png", (22, 22))
        self.btn_excluir = ttk.Button(btn_box, image=ico_excluir, text="", command=self._excluir_usuario)
        self.btn_excluir.pack(side=tk.LEFT, padx=(0, 5))
        self._criar_tooltip(self.btn_excluir, "Exclui usuário sem histórico")

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

        # Linha 1: Seleção do Sistema
        sis_sel_row = ttk.Frame(sis_actions)
        sis_sel_row.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(sis_sel_row, text="Adicionar Sistema:").pack(side=tk.LEFT, padx=(0, 5))
        self.cbo_novo_sistema = ttk.Combobox(sis_sel_row, state="readonly", width=25)
        self.cbo_novo_sistema.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Linha 2: Botões Vincular e Remover na linha de baixo (evita ficar oculto)
        sis_btn_row = ttk.Frame(sis_actions)
        sis_btn_row.pack(fill=tk.X, pady=(2, 0))

        ico_vincular = self._carregar_icone("vincular_sistema.png", (22, 22))
        self.btn_add_sis = ttk.Button(
            sis_btn_row,
            image=ico_vincular,
            text="",
            command=self._vincular_sistema
        )
        self.btn_add_sis.pack(side=tk.LEFT, padx=(0, 5))
        self._criar_tooltip(self.btn_add_sis, "Vincula o usuário ao sistema")

        ico_desvincular = self._carregar_icone("desvincular_sistema.png", (22, 22))
        self.btn_rem_sis = ttk.Button(
            sis_btn_row,
            image=ico_desvincular,
            text="",
            command=self._desvincular_sistema
        )
        self.btn_rem_sis.pack(side=tk.LEFT)
        self._criar_tooltip(self.btn_rem_sis, "Remove vinculo entre usuário e sistema")

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

        # Padronização em Caixa Alta e Navegação Enter
        vincular_maiusculo(self.ent_grp_cod)
        vincular_maiusculo(self.ent_grp_desc)
        configurar_navegacao_enter([self.ent_grp_cod, self.ent_grp_desc])

        grp_btns = ttk.Frame(left)
        grp_btns.pack(fill=tk.X, pady=5)

        ico_novo_grp = self._carregar_icone("group_add.png", (22, 22))
        self.btn_novo_grupo = ttk.Button(
            grp_btns,
            image=ico_novo_grp,
            text="",
            command=self._novo_grupo
        )
        self.btn_novo_grupo.pack(side=tk.LEFT, padx=(0, 5))
        self._criar_tooltip(self.btn_novo_grupo, "Novo Grupo de Usuários")

        ico_salvar_grp = self._carregar_icone("salvar.png", (22, 22))
        self.btn_salvar_grupo = ttk.Button(
            grp_btns,
            image=ico_salvar_grp,
            text="",
            command=self._salvar_grupo
        )
        self.btn_salvar_grupo.pack(side=tk.LEFT, padx=(0, 5))
        self._criar_tooltip(self.btn_salvar_grupo, "Salva o Grupo de Usuários")

        ico_excluir_grp = self._carregar_icone("user_delete.png", (22, 22))
        self.btn_excluir_grupo = ttk.Button(
            grp_btns,
            image=ico_excluir_grp,
            text="",
            command=self._excluir_grupo
        )
        self.btn_excluir_grupo.pack(side=tk.LEFT)
        self._criar_tooltip(self.btn_excluir_grupo, "Remove o Grupo de usuário se não houver vinculos no sistema")

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

        # Linha 1: Seleção do Colaborador
        membros_sel_row = ttk.Frame(membros_actions)
        membros_sel_row.pack(fill=tk.X, pady=(0, 4))

        ttk.Label(membros_sel_row, text="Adicionar Colaborador:").pack(side=tk.LEFT, padx=(0, 5))
        self.cbo_add_usuario_grupo = ttk.Combobox(membros_sel_row, state="readonly", width=25)
        self.cbo_add_usuario_grupo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Linha 2: Botões Adicionar e Remover Membro na linha de baixo
        membros_btn_row = ttk.Frame(membros_actions)
        membros_btn_row.pack(fill=tk.X, pady=(2, 0))

        ico_add_membro = self._carregar_icone("user_add.png", (22, 22))
        self.btn_add_usuario_grupo = ttk.Button(
            membros_btn_row,
            image=ico_add_membro,
            text="",
            command=self._adicionar_membro_grupo
        )
        self.btn_add_usuario_grupo.pack(side=tk.LEFT, padx=(0, 5))
        self._criar_tooltip(self.btn_add_usuario_grupo, "Adicionar usuários ao grupo")

        ico_rem_membro = self._carregar_icone("user_delete.png", (22, 22))
        self.btn_rem_usuario_grupo = ttk.Button(
            membros_btn_row,
            image=ico_rem_membro,
            text="",
            command=self._remover_membro_grupo
        )
        self.btn_rem_usuario_grupo.pack(side=tk.LEFT)
        self._criar_tooltip(self.btn_rem_usuario_grupo, "Remove uusuários do grupo")

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

        ttk.Button(top_bar, text="Atualizar Lista", command=self._atualizar_lista_com_varredura).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(top_bar, text="🔄 Sincronizar Catálogo Completo", command=self._atualizar_lista_com_varredura).pack(side=tk.LEFT)

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
            self.service.sincronizar_catalogo_completo(empresa=self.empresa)
        except Exception:
            pass
        try:
            self.carregar_departamentos()
            self.carregar_sistemas()
            self.pesquisar_usuarios()
            self.carregar_grupos()
            self.carregar_categorias_perfil()
            if hasattr(self, "cbo_perfil_grupo") and self.cbo_perfil_grupo["values"] and not self.cbo_perfil_grupo.get():
                self.cbo_perfil_grupo.current(0)
                self.carregar_perfil_objetos()
        except Exception as e:
            # Em modo headless / testes, erros silenciosos de banco são tolerados
            pass

    def carregar_departamentos(self):
        """Carrega os departamentos cadastrados na tabela USER_geoapolo_departamentos."""
        if not self.service:
            return
        try:
            self.departamentos = self.service.listar_departamentos()
            dept_values = [f"{d.codigo_departamento} - {d.nome_departamento}" for d in self.departamentos]
            self.cbo_departamento["values"] = dept_values
        except Exception:
            pass

    def carregar_sistemas(self):
        """Carrega os sistemas corporativos disponíveis."""
        if not self.service:
            return
        try:
            self.sistemas_disponiveis = self.service.listar_sistemas()
            sis_values = [f"{s.codigo_sistema} - {s.descricao}" for s in self.sistemas_disponiveis]
            self.cbo_novo_sistema["values"] = sis_values
        except Exception:
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

        self._codigo_usuario_atual = str(usuario.codigo_usuario or "")

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
        self.ent_senha.configure(show="*")
        self._senha_cifrada_cache = usuario.senha_alvo

        self.var_user_ativo.set(usuario.ativo)

        # Seleciona depto na combo por código ou por nome
        cod_depto = str(usuario.codigo_departamento or "").strip()
        nome_depto = str(usuario.nome_departamento or "").strip().upper()
        depto_encontrado = False
        for v in self.cbo_departamento["values"]:
            partes = v.split(" - ", 1)
            v_cod = partes[0].strip()
            v_nome = partes[1].strip().upper() if len(partes) > 1 else ""
            if (cod_depto and v_cod == cod_depto) or (nome_depto and v_nome == nome_depto):
                self.cbo_departamento.set(v)
                depto_encontrado = True
                break
        if not depto_encontrado:
            self.cbo_departamento.set("")

        self._carregar_sistemas_usuario(usuario.usucod)
        self._atualizar_visibilidade_btn_decript()

    def _carregar_sistemas_usuario(self, usucod: str):
        for item in self.tree_sistemas_user.get_children():
            self.tree_sistemas_user.delete(item)

        sistemas = self.service.listar_sistemas_usuario(usucod)
        for s in sistemas:
            self.tree_sistemas_user.insert("", tk.END, values=(s.codigo_sistema, s.descricao, s.sigla))

    def _novo_usuario(self):
        self._codigo_usuario_atual = ""
        if self.tree_users.selection():
            try:
                self.tree_users.selection_remove(self.tree_users.selection())
            except Exception:
                pass
        self.ent_usucod.delete(0, tk.END)
        self.ent_login.delete(0, tk.END)
        self.ent_nome.delete(0, tk.END)
        self.ent_email.delete(0, tk.END)
        self.ent_senha.delete(0, tk.END)
        self.ent_senha.configure(show="*")
        self._senha_cifrada_cache = ""
        self.cbo_departamento.set("")
        self.var_user_ativo.set(True)
        for item in self.tree_sistemas_user.get_children():
            self.tree_sistemas_user.delete(item)
        self._atualizar_visibilidade_btn_decript()
        self.ent_usucod.focus_set()

    def _salvar_usuario(self):
        usucod = self.ent_usucod.get().strip()
        login = self.ent_login.get().strip()
        nome = self.ent_nome.get().strip()
        email = self.ent_email.get().strip()
        senha = self.ent_senha.get().strip()
        ativo = "A" if self.var_user_ativo.get() else "I"

        if not usucod:
            self._msg_warning("Aviso", "O código (usucod) do usuário é obrigatório.")
            self.ent_usucod.focus_set()
            return

        if not login:
            self._msg_warning("Aviso", "O login de acesso é obrigatório.")
            self.ent_login.focus_set()
            return

        if not nome:
            self._msg_warning("Aviso", "O nome completo do usuário é obrigatório.")
            self.ent_nome.focus_set()
            return

        depto_sel = self.cbo_departamento.get().strip()
        cod_depto = depto_sel.split(" - ")[0].strip() if " - " in depto_sel else depto_sel

        # Pergunta de confirmação da operação (Inclusão vs Alteração)
        usuario_existente = self.service.obter_usuario(usucod) if self.service else None
        if usuario_existente:
            confirmar = self._msg_askyesno(
                "Confirmação de Alteração",
                f"Deseja realmente confirmar a alteração dos dados do usuário '{usucod}' ({nome})?",
            )
        else:
            confirmar = self._msg_askyesno(
                "Confirmação de Inclusão",
                f"Deseja realmente confirmar a inclusão do novo usuário '{usucod}' ({nome})?",
            )

        if not confirmar:
            return

        # Se a senha estava em modo revelado/descriptografado, re-criptografa antes de gravar
        if self.ent_senha.cget("show") == "":
            senha_salvar = criptografia(32, senha)
            self.ent_senha.configure(show="*")
            self.ent_senha.delete(0, tk.END)
            self.ent_senha.insert(0, senha_salvar)
            self._senha_cifrada_cache = senha_salvar
        else:
            senha_salvar = senha

        u = UsuarioDTO(
            usucod=usucod,
            login=login,
            nome_completo=nome,
            email=email,
            codigo_usuario=getattr(self, "_codigo_usuario_atual", ""),
            codigo_departamento=cod_depto,
            flagativo=ativo,
            senha_alvo=senha_salvar,
        )

        res = self.service.salvar_usuario(u)
        if res.sucesso:
            self._msg_info("Sucesso", res.mensagem)
            self.pesquisar_usuarios()
            self._atualizar_visibilidade_btn_decript()
            self.ent_usucod.focus_set()
        else:
            self._msg_error("Atenção", res.mensagem)
        self._garantir_foco()

    def _excluir_usuario(self):
        usucod = self.ent_usucod.get().strip()
        if not usucod:
            self._msg_warning("Aviso", "Selecione um usuário para excluir.")
            return

        confirmar = self._msg_askyesno(
            "Confirmação de Exclusão",
            f"Deseja realmente confirmar a exclusão do usuário '{usucod}'?\n\n"
            "Aviso: Caso o usuário possua histórico de movimentação no sistema, não será permitida a exclusão do mesmo.",
        )
        if not confirmar:
            return

        res = self.service.excluir_usuario(usucod)
        if res.sucesso:
            self._msg_info("Sucesso", res.mensagem)
            self._novo_usuario()
            self.pesquisar_usuarios()
        else:
            self._msg_error(
                "Atenção - Exclusão Não Permitida",
                f"Não foi possível excluir o usuário '{usucod}'.\n\n"
                f"{res.mensagem}\n\n"
                "Caso o usuário possua histórico de movimentação no sistema, "
                "não será permitida a exclusão do mesmo. Sugere-se inativar o cadastro."
            )
        self._garantir_foco()

    def _vincular_sistema(self):
        usucod = self.ent_usucod.get().strip()
        sel = self.cbo_novo_sistema.get()
        if not usucod or not sel:
            self._msg_warning("Aviso", "Selecione um usuário e um sistema para vincular.")
            return
        cod_sis = sel.split(" - ")[0].strip()

        confirmar = self._msg_askyesno(
            "Confirmação de Inclusão",
            f"Deseja realmente confirmar a inclusão do vínculo com o sistema '{sel}' para o usuário '{usucod}'?",
        )
        if not confirmar:
            return

        res = self.service.vincular_sistema(usucod, cod_sis)
        if res.sucesso:
            self._carregar_sistemas_usuario(usucod)
        else:
            self._msg_error("Erro", res.mensagem)
        self._garantir_foco()

    def _desvincular_sistema(self):
        usucod = self.ent_usucod.get().strip()
        sel = self.tree_sistemas_user.selection()
        if not usucod or not sel:
            self._msg_warning("Aviso", "Selecione um sistema da lista para desvincular.")
            return
        item_vals = self.tree_sistemas_user.item(sel[0], "values")
        cod_sis = item_vals[0]
        desc_sis = item_vals[1] if len(item_vals) > 1 else cod_sis

        confirmar = self._msg_askyesno(
            "Confirmação de Exclusão",
            f"Deseja realmente confirmar a exclusão do vínculo com o sistema '{cod_sis} - {desc_sis}' do usuário '{usucod}'?",
        )
        if not confirmar:
            return

        res = self.service.desvincular_sistema(usucod, cod_sis)
        if res.sucesso:
            self._carregar_sistemas_usuario(usucod)
        else:
            self._msg_error("Erro", res.mensagem)
        self._garantir_foco()

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
        cod = str(vals[0] or "").strip().upper()
        desc = str(vals[1] or "").strip().upper()

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

        empresa = self._obter_empresa_atual()
        try:
            prox_cod = geoapolo_configcod(empresa, "USER_geoapolo_grupo", "Sim")
            self.ent_grp_cod.insert(0, str(prox_cod).upper())
        except Exception:
            pass
        self.ent_grp_desc.focus_set()

    def _salvar_grupo(self):
        cod = self.ent_grp_cod.get().strip().upper()
        desc = self.ent_grp_desc.get().strip().upper()
        empresa = self._obter_empresa_atual()

        if not cod:
            try:
                cod = str(geoapolo_configcod(empresa, "USER_geoapolo_grupo", "Sim")).upper()
                self.ent_grp_cod.delete(0, tk.END)
                self.ent_grp_cod.insert(0, cod)
            except Exception:
                pass

        if not cod:
            self._msg_warning("Aviso", "O código do grupo é obrigatório.")
            self.ent_grp_cod.focus_set()
            return
        if not desc:
            self._msg_warning("Aviso", "A descrição do grupo é obrigatória.")
            self.ent_grp_desc.focus_set()
            return

        grupo_existente = self.service.obter_grupo(cod) if self.service else None
        if grupo_existente:
            confirmar = self._msg_askyesno(
                "Confirmação de Alteração",
                f"Deseja realmente confirmar a alteração do grupo '{cod}' ({desc})?",
            )
        else:
            confirmar = self._msg_askyesno(
                "Confirmação de Inclusão",
                f"Deseja realmente confirmar a inclusão do novo grupo '{cod}' ({desc})?",
            )
        if not confirmar:
            return

        res = self.service.salvar_grupo(cod, desc)
        if res.sucesso:
            self._msg_info("Sucesso", res.mensagem)
            self.carregar_grupos()
        else:
            self._msg_error("Erro", res.mensagem)
        self._garantir_foco()

    def _excluir_grupo(self):
        cod = self.ent_grp_cod.get().strip().upper()
        if not cod:
            self._msg_warning("Aviso", "Informe o grupo para exclusão.")
            return

        confirmar = self._msg_askyesno(
            "Confirmação de Exclusão",
            f"Deseja realmente confirmar a exclusão do grupo '{cod}'?\n\n"
            "Aviso: Remove o Grupo de usuário se não houver vinculos no sistema.",
        )
        if not confirmar:
            return

        res = self.service.excluir_grupo(cod)
        if res.sucesso:
            self._msg_info("Sucesso", res.mensagem)
            self._novo_grupo()
            self.carregar_grupos()
        else:
            self._msg_error(
                "Atenção - Exclusão Não Permitida",
                f"Não foi possível excluir o grupo '{cod}'.\n\n"
                f"{res.mensagem}\n\n"
                "Caso o grupo possua usuários vinculados ou vínculos no sistema, "
                "não será permitida a exclusão do mesmo."
            )
        self._garantir_foco()

    def _adicionar_membro_grupo(self):
        cod_grupo = self.ent_grp_cod.get().strip().upper()
        user_sel = self.cbo_add_usuario_grupo.get()
        if not cod_grupo or not user_sel:
            self._msg_warning("Aviso", "Selecione um grupo e um colaborador.")
            return
        usucod = user_sel.split(" - ")[0].strip()

        if not self._msg_askyesno("Confirmação de Inclusão", f"Deseja realmente confirmar a inclusão do usuário '{user_sel}' no grupo '{cod_grupo}'?"):
            return

        res = self.service.vincular_usuario_grupo(cod_grupo, usucod)
        if res.sucesso:
            self._msg_info("Sucesso", res.mensagem)
            self._carregar_membros_grupo(cod_grupo)
            self.carregar_grupos()
        else:
            self._msg_error("Erro", res.mensagem)
        self._garantir_foco()

    def _remover_membro_grupo(self):
        cod_grupo = self.ent_grp_cod.get().strip().upper()
        sel = self.tree_membros_grupo.selection()
        if not cod_grupo or not sel:
            self._msg_warning("Aviso", "Selecione um membro para remover.")
            return
        item_vals = self.tree_membros_grupo.item(sel[0], "values")
        usucod = item_vals[0]
        nome = item_vals[2] if len(item_vals) > 2 else usucod

        if not self._msg_askyesno("Confirmação de Exclusão", f"Deseja realmente confirmar a exclusão do usuário '{usucod} - {nome}' do grupo '{cod_grupo}'?"):
            return

        res = self.service.desvincular_usuario_grupo(cod_grupo, usucod)
        if res.sucesso:
            self._msg_info("Sucesso", res.mensagem)
            self._carregar_membros_grupo(cod_grupo)
            self.carregar_grupos()
        else:
            self._msg_error("Erro", res.mensagem)
        self._garantir_foco()

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

    def _atualizar_lista_com_varredura(self):
        """Faz a varredura completa dos objetos do sistema, sincroniza novos itens e atualiza as permissões."""
        try:
            res = self.service.sincronizar_catalogo_completo(empresa=self.empresa)
            self.carregar_categorias_perfil()
            self.carregar_perfil_objetos()
            if res.sucesso:
                self._msg_info("Atualizar Lista de Objetos", f"Varredura concluída com sucesso!\n\n{res.mensagem}")
            else:
                self._msg_error("Erro de Varredura", res.mensagem)
        except Exception as e:
            self._msg_error("Erro", f"Falha ao realizar varredura de catálogo: {str(e)}")
        self._garantir_foco()

    def _sincronizar_catalogo_completo(self):
        self._atualizar_lista_com_varredura()

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
            self._msg_warning("Aviso", "Selecione um recurso da lista.")
            return
        item_vals = self.tree_perfis.item(sel[0], "values")
        cod_obj = item_vals[0]
        nome_tela = item_vals[2] if len(item_vals) > 2 else cod_obj
        acao = "liberação" if liberado else "bloqueio"
        if not self._msg_askyesno("Confirmação de Alteração", f"Deseja realmente confirmar o {acao} de acesso ao recurso '{nome_tela}'?"):
            return
        self._atualizar_permissao_objeto(cod_obj, liberado)

    def _set_permissao_todos(self, liberado: bool):
        grp_sel = self.cbo_perfil_grupo.get()
        if not grp_sel:
            self._msg_warning("Aviso", "Selecione um grupo de segurança primeiro.")
            return
        cod_grupo = grp_sel.split(" - ")[0]
        acao = "liberação" if liberado else "bloqueio"
        if not self._msg_askyesno("Confirmação de Alteração", f"Deseja realmente confirmar o {acao} em lote para todos os recursos listados do grupo '{grp_sel}'?"):
            return

        for item in self.tree_perfis.get_children():
            vals = self.tree_perfis.item(item, "values")
            cod_obj = vals[0]
            self.service.atualizar_acesso(cod_grupo, cod_obj, liberado)

        self.carregar_perfil_objetos()
        self._garantir_foco()

    def _atualizar_permissao_objeto(self, cod_objeto: str, liberado: bool):
        grp_sel = self.cbo_perfil_grupo.get()
        if not grp_sel:
            return
        cod_grupo = grp_sel.split(" - ")[0]
        res = self.service.atualizar_acesso(cod_grupo, cod_objeto, liberado)
        if res.sucesso:
            self.carregar_perfil_objetos()
        else:
            self._msg_error("Erro", res.mensagem)
        self._garantir_foco()
