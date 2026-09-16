"""
Interface Gráfica Moderna para Gestão de Permissões de Contas Financeiras por Usuário.
GeoApolo V5
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from permissoes.models import ContaFinanceiraDTO
from permissoes.repository import PermissoesRepository
from permissoes.service import PermissoesService


class UsuarioContasFinView:
    """Janela corporativa para vincular contas financeiras a usuários."""

    def __init__(self, parent: tk.Tk, service: Optional[PermissoesService] = None):
        self.parent = parent
        self.service = service or PermissoesService(PermissoesRepository())

        self.window = tk.Toplevel(parent)
        self.window.title("GeoAlvo - Permissão em Contas Financeiras")
        self.window.geometry("820x620")
        self.window.minsize(750, 550)
        self.window.transient(parent)
        self.window.grab_set()

        self._todas_contas: List[ContaFinanceiraDTO] = []
        self._setup_ui()
        self._carregar_dados_iniciais()

    def _setup_ui(self):
        # Header corporativo
        header = tk.Frame(self.window, bg="#1A365D", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        lbl_titulo = tk.Label(
            header,
            text="Permissão de Usuários em Contas Financeiras",
            font=("Segoe UI", 13, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
        )
        lbl_titulo.pack(side=tk.LEFT, padx=15, pady=12)

        # Container Principal
        container = ttk.Frame(self.window, padding="15")
        container.pack(fill=tk.BOTH, expand=True)

        # Seletor de Usuário
        user_frame = ttk.LabelFrame(container, text=" Seleção do Usuário ", padding="10")
        user_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(user_frame, text="Usuário:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(5, 10))

        self.cbo_usuario = ttk.Combobox(user_frame, state="readonly", width=35, font=("Segoe UI", 10))
        self.cbo_usuario.pack(side=tk.LEFT, padx=5)
        self.cbo_usuario.bind("<<ComboboxSelected>>", self._ao_selecionar_usuario)

        btn_recarregar = ttk.Button(user_frame, text="Recarregar", command=self._carregar_dados_iniciais)
        btn_recarregar.pack(side=tk.LEFT, padx=10)

        # Painel Central com Duas Listas e Botões de Transferência
        lists_frame = ttk.Frame(container)
        lists_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Coluna 1: Contas Disponíveis
        frame_disp = ttk.LabelFrame(lists_frame, text=" Contas Disponíveis no Apolo ", padding="8")
        frame_disp.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.lst_disponiveis = tk.Listbox(
            frame_disp,
            selectmode=tk.EXTENDED,
            font=("Consolas", 10),
            activestyle="none",
            exportselection=False,
        )
        scroll_disp = ttk.Scrollbar(frame_disp, orient=tk.VERTICAL, command=self.lst_disponiveis.yview)
        self.lst_disponiveis.configure(yscrollcommand=scroll_disp.set)
        self.lst_disponiveis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_disp.pack(side=tk.RIGHT, fill=tk.Y)

        # Coluna Central: Ações de Transferência
        btn_box = ttk.Frame(lists_frame, padding="10")
        btn_box.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=20)

        ttk.Button(btn_box, text=" > ", width=5, command=self._mover_um_para_relacionadas).pack(pady=4)
        ttk.Button(btn_box, text=" >> ", width=5, command=self._mover_todos_para_relacionadas).pack(pady=4)
        ttk.Button(btn_box, text=" < ", width=5, command=self._remover_um_de_relacionadas).pack(pady=4)
        ttk.Button(btn_box, text=" << ", width=5, command=self._remover_todos_de_relacionadas).pack(pady=4)

        # Coluna 2: Contas Já Relacionadas
        frame_rel = ttk.LabelFrame(lists_frame, text=" Contas Autorizadas para o Usuário ", padding="8")
        frame_rel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.lst_relacionadas = tk.Listbox(
            frame_rel,
            selectmode=tk.EXTENDED,
            font=("Consolas", 10),
            activestyle="none",
            exportselection=False,
        )
        scroll_rel = ttk.Scrollbar(frame_rel, orient=tk.VERTICAL, command=self.lst_relacionadas.yview)
        self.lst_relacionadas.configure(yscrollcommand=scroll_rel.set)
        self.lst_relacionadas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_rel.pack(side=tk.RIGHT, fill=tk.Y)

        # Barra de Ações Inferior
        bottom_frame = ttk.Frame(container)
        bottom_frame.pack(fill=tk.X, pady=(15, 0))

        self.lbl_status = ttk.Label(bottom_frame, text="Selecione um usuário para visualizar as permissões.", font=("Segoe UI", 9))
        self.lbl_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

        btn_salvar = tk.Button(
            bottom_frame,
            text="💾 Salvar Permissões",
            font=("Segoe UI", 10, "bold"),
            bg="#2B6CB0",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self._salvar_permissoes,
            cursor="hand2",
        )
        btn_salvar.pack(side=tk.RIGHT, padx=5)

        btn_fechar = ttk.Button(bottom_frame, text="Fechar", command=self.window.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=5)

    def _carregar_dados_iniciais(self):
        try:
            usuarios = self.service.listar_usuarios()
            codigos = [u["codigo"] for u in usuarios]
            self.cbo_usuario["values"] = codigos
            if codigos:
                self.cbo_usuario.current(0)

            self._todas_contas = self.service.obter_contas_disponiveis()
            self._atualizar_lista_disponiveis()

            if codigos:
                self._carregar_contas_usuario(codigos[0])
        except Exception as e:
            messagebox.showerror("Erro de Inicialização", f"Erro ao carregar dados do banco:\n{e}")

    def _atualizar_lista_disponiveis(self):
        self.lst_disponiveis.delete(0, tk.END)
        for conta in self._todas_contas:
            self.lst_disponiveis.insert(tk.END, conta.texto_formatado)

    def _carregar_contas_usuario(self, usucod: str):
        self.lst_relacionadas.delete(0, tk.END)
        try:
            contas_usu = self.service.obter_contas_usuario(usucod)
            for c in contas_usu:
                self.lst_relacionadas.insert(tk.END, c.texto_formatado)
            self.lbl_status.config(
                text=f"Usuário '{usucod}': {len(contas_usu)} conta(s) autorizada(s)."
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar contas do usuário:\n{e}")

    def _ao_selecionar_usuario(self, event=None):
        usucod = self.cbo_usuario.get()
        if usucod:
            self._carregar_contas_usuario(usucod)

    def _mover_um_para_relacionadas(self):
        indices = self.lst_disponiveis.curselection()
        if not indices:
            return
        itens_atuais = set(self.lst_relacionadas.get(0, tk.END))
        for idx in indices:
            item = self.lst_disponiveis.get(idx)
            if item not in itens_atuais:
                self.lst_relacionadas.insert(tk.END, item)
                itens_atuais.add(item)

    def _mover_todos_para_relacionadas(self):
        itens_atuais = set(self.lst_relacionadas.get(0, tk.END))
        for item in self.lst_disponiveis.get(0, tk.END):
            if item not in itens_atuais:
                self.lst_relacionadas.insert(tk.END, item)
                itens_atuais.add(item)

    def _remover_um_de_relacionadas(self):
        indices = list(self.lst_relacionadas.curselection())
        for idx in reversed(indices):
            self.lst_relacionadas.delete(idx)

    def _remover_todos_de_relacionadas(self):
        self.lst_relacionadas.delete(0, tk.END)

    def _salvar_permissoes(self):
        usucod = self.cbo_usuario.get().strip()
        if not usucod:
            messagebox.showwarning("Aviso", "Selecione um usuário antes de prosseguir.")
            return

        itens = self.lst_relacionadas.get(0, tk.END)
        codigos = []
        for it in itens:
            if "->" in it:
                codigos.append(it.split("->")[0].strip())
            else:
                codigos.append(it.strip())

        if not messagebox.askyesno(
            "Confirmação",
            f"Confirma a autorização de {len(codigos)} conta(s) para o usuário '{usucod}'?",
        ):
            return

        res = self.service.salvar_contas_usuario(usucod, codigos)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self._carregar_contas_usuario(usucod)
        else:
            messagebox.showerror("Erro ao Salvar", res.mensagem)
