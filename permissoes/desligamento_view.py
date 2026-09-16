"""
Interface Gráfica Moderna para Desativação e Desligamento de Usuários do Sistema.
GeoApolo V5
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from permissoes.models import UsuarioDesligamentoDTO
from permissoes.repository import PermissoesRepository
from permissoes.service import PermissoesService


class DesligamentoUsuarioView:
    """Janela corporativa para desligamento e revogação em lote de acessos de operadores."""

    def __init__(self, parent: tk.Tk, service: Optional[PermissoesService] = None):
        self.parent = parent
        self.service = service or PermissoesService(PermissoesRepository())

        self.window = tk.Toplevel(parent)
        self.window.title("GeoAlvo - Desativação / Desligamento de Usuários")
        self.window.geometry("860x600")
        self.window.minsize(780, 520)
        self.window.transient(parent)
        self.window.grab_set()

        self._setup_ui()
        self._pesquisar()

    def _setup_ui(self):
        # Header corporativo
        header = tk.Frame(self.window, bg="#1A365D", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        lbl_titulo = tk.Label(
            header,
            text="Desativação e Desligamento de Usuários (Alvo / Apolo)",
            font=("Segoe UI", 13, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
        )
        lbl_titulo.pack(side=tk.LEFT, padx=15, pady=12)

        # Container Principal
        container = ttk.Frame(self.window, padding="15")
        container.pack(fill=tk.BOTH, expand=True)

        # Painel de Filtros e Busca
        filter_frame = ttk.LabelFrame(container, text=" Filtros de Pesquisa ", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filter_frame, text="Campo:", font=("Segoe UI", 9)).grid(row=0, column=0, padx=5, sticky="w")
        self.cbo_campo = ttk.Combobox(
            filter_frame,
            values=["usucod", "usunome", "usudepto"],
            state="readonly",
            width=12,
        )
        self.cbo_campo.current(0)
        self.cbo_campo.grid(row=0, column=1, padx=5, sticky="w")

        ttk.Label(filter_frame, text="Pesquisar por:", font=("Segoe UI", 9)).grid(row=0, column=2, padx=5, sticky="w")
        self.txt_busca = ttk.Entry(filter_frame, width=25)
        self.txt_busca.grid(row=0, column=3, padx=5, sticky="w")
        self.txt_busca.bind("<Return>", lambda e: self._pesquisar())

        ttk.Label(filter_frame, text="Status:", font=("Segoe UI", 9)).grid(row=0, column=4, padx=5, sticky="w")
        self.cbo_status = ttk.Combobox(
            filter_frame,
            values=["Ativo", "Desligado", "Todos"],
            state="readonly",
            width=10,
        )
        self.cbo_status.current(0)
        self.cbo_status.grid(row=0, column=5, padx=5, sticky="w")

        btn_buscar = ttk.Button(filter_frame, text="🔍 Buscar", command=self._pesquisar)
        btn_buscar.grid(row=0, column=6, padx=8, sticky="w")

        btn_limpar = ttk.Button(filter_frame, text="Limpar", command=self._limpar_filtro)
        btn_limpar.grid(row=0, column=7, padx=4, sticky="w")

        # Tabela Treeview
        grid_frame = ttk.Frame(container)
        grid_frame.pack(fill=tk.BOTH, expand=True)

        colunas = ("codigo", "nome", "departamento", "status")
        self.tree = ttk.Treeview(grid_frame, columns=colunas, show="headings", selectmode="browse")

        self.tree.heading("codigo", text="Código do Usuário")
        self.tree.heading("nome", text="Nome do Funcionário")
        self.tree.heading("departamento", text="Departamento")
        self.tree.heading("status", text="Status Atual")

        self.tree.column("codigo", width=140, anchor="w")
        self.tree.column("nome", width=280, anchor="w")
        self.tree.column("departamento", width=180, anchor="w")
        self.tree.column("status", width=100, anchor="center")

        scroll_y = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._ao_selecionar_grid)

        # Painel do Usuário Selecionado
        detalhe_frame = ttk.LabelFrame(container, text=" Detalhes da Seleção ", padding="10")
        detalhe_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(detalhe_frame, text="Usuário Selecionado:").grid(row=0, column=0, padx=5, sticky="w")
        self.lbl_detalhe_usuario = ttk.Label(detalhe_frame, text="-", font=("Segoe UI", 10, "bold"))
        self.lbl_detalhe_usuario.grid(row=0, column=1, padx=5, sticky="w")

        # Botões de Ação
        btn_box = ttk.Frame(detalhe_frame)
        btn_box.grid(row=0, column=2, sticky="e", padx=10)
        detalhe_frame.columnconfigure(2, weight=1)

        self.btn_desligar = tk.Button(
            btn_box,
            text="🚫 Desligar Usuário",
            font=("Segoe UI", 9, "bold"),
            bg="#C53030",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            command=self._executar_desligamento,
            cursor="hand2",
        )
        self.btn_desligar.pack(side=tk.LEFT, padx=5)

        self.btn_reativar = tk.Button(
            btn_box,
            text="✅ Reativar Usuário",
            font=("Segoe UI", 9, "bold"),
            bg="#2F855A",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            command=self._executar_reativacao,
            cursor="hand2",
        )
        self.btn_reativar.pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_box, text="Fechar", command=self.window.destroy).pack(side=tk.LEFT, padx=5)

        # Barra de status inferior
        self.lbl_status_bar = ttk.Label(container, text="", font=("Segoe UI", 8))
        self.lbl_status_bar.pack(fill=tk.X, pady=(5, 0))

    def _pesquisar(self):
        campo = self.cbo_campo.get()
        valor = self.txt_busca.get().strip()
        status_sel = self.cbo_status.get()
        status_param = None if status_sel == "Todos" else status_sel

        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            if valor:
                usuarios = self.service.pesquisar_usuarios_desligamento(campo, valor, status_param)
            else:
                if status_param:
                    usuarios = self.service.listar_usuarios_desligamento(status_param)
                else:
                    usuarios = self.service.pesquisar_usuarios_desligamento("usucod", "")

            for u in usuarios:
                self.tree.insert(
                    "",
                    tk.END,
                    values=(u.codigo, u.nome, u.departamento, u.status),
                )

            self.lbl_status_bar.config(text=f"Total de {len(usuarios)} usuário(s) encontrado(s).")
            self._limpar_selecao()
        except Exception as e:
            messagebox.showerror("Erro de Pesquisa", f"Falha ao pesquisar usuários:\n{e}")

    def _limpar_filtro(self):
        self.txt_busca.delete(0, tk.END)
        self.cbo_status.current(0)
        self._pesquisar()

    def _limpar_selecao(self):
        self.lbl_detalhe_usuario.config(text="-")
        self.btn_desligar.config(state=tk.DISABLED)
        self.btn_reativar.config(state=tk.DISABLED)

    def _ao_selecionar_grid(self, event=None):
        sel = self.tree.selection()
        if not sel:
            self._limpar_selecao()
            return
        item = self.tree.item(sel[0])
        vals = item["values"]
        if vals:
            cod, nome, depto, status = vals[0], vals[1], vals[2], vals[3]
            self.lbl_detalhe_usuario.config(text=f"{cod} - {nome} ({status})")
            if str(status).upper() == "ATIVO":
                self.btn_desligar.config(state=tk.NORMAL)
                self.btn_reativar.config(state=tk.DISABLED)
            else:
                self.btn_desligar.config(state=tk.DISABLED)
                self.btn_reativar.config(state=tk.NORMAL)

    def _executar_desligamento(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um usuário na tabela.")
            return

        vals = self.tree.item(sel[0])["values"]
        cod, nome = vals[0], vals[1]

        if not messagebox.askyesno(
            "Confirmação de Desligamento",
            f"Deseja realmente DESLIGAR o usuário '{cod}' ({nome})?\n\n"
            "ATENÇÃO: Todos os vínculos de Entidades, Categorias, Relatórios e Contas Financeiras serão revogados!",
        ):
            return

        res = self.service.desligar_usuario(cod)
        if res.sucesso:
            messagebox.showinfo("Desligamento Concluído", res.mensagem)
            self._pesquisar()
        else:
            messagebox.showerror("Falha no Desligamento", res.mensagem)

    def _executar_reativacao(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um usuário na tabela.")
            return

        vals = self.tree.item(sel[0])["values"]
        cod, nome = vals[0], vals[1]

        if not messagebox.askyesno(
            "Reativação",
            f"Deseja reativar o status do usuário '{cod}' ({nome}) para Ativo?",
        ):
            return

        if self.service.reativar_usuario(cod):
            messagebox.showinfo("Sucesso", f"Usuário '{cod}' reativado com sucesso!")
            self._pesquisar()
        else:
            messagebox.showerror("Erro", f"Não foi possível reativar o usuário '{cod}'.")
