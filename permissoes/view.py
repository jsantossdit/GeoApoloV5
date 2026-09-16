"""
Interface Gráfica (Tkinter / ttk) para Clonagem de Permissões de Usuários.
Layout corporativo profissional no padrão visual GeoAlvo (#1A365D).
"""

import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Any, Optional

from permissoes.models import OpcoesClonagemDTO, ResultadoClonagemDTO
from permissoes.repository import PermissoesRepository
from permissoes.service import PermissoesService
from entidades.database import obter_conexao_banco

logger = logging.getLogger(__name__)


class ClonarPermissoesView(tk.Toplevel):
    """Janela para Clonagem e Replicação de Direitos e Permissões entre Usuários."""

    def __init__(self, parent=None, connection=None):
        super().__init__(parent)
        self.title("Clonagem de Permissões de Usuários - GeoAlvo")
        self.geometry("820x620")
        self.minsize(700, 520)

        self._centralizar_janela(820, 620)
        self._aplicar_icone()

        self._conn = connection
        if self._conn is None:
            try:
                self._conn = obter_conexao_banco()
            except Exception as exc:
                logger.warning("Não foi possível obter conexão automática: %s", exc)

        self._repo = PermissoesRepository(self._conn) if self._conn else None
        self._service = PermissoesService(self._repo) if self._repo else None

        self._usuarios: List[Dict[str, str]] = []

        self._configurar_estilos()
        self._criar_interface()
        self._carregar_usuarios()

        self.bind("<Escape>", lambda e: self.destroy())

    def _centralizar_janela(self, largura: int, altura: int):
        self.update_idletasks()
        pos_x = (self.winfo_screenwidth() // 2) - (largura // 2)
        pos_y = (self.winfo_screenheight() // 2) - (altura // 2) - 20
        self.geometry(f"{largura}x{altura}+{max(pos_x, 0)}+{max(pos_y, 0)}")

    def _aplicar_icone(self):
        caminhos = [
            os.path.join(os.path.dirname(__file__), "..", "Imagens", "IconeRCC.png"),
            os.path.join(os.path.dirname(__file__), "..", "Imagens", "entidades.png"),
        ]
        for c in caminhos:
            if os.path.exists(c):
                try:
                    img = tk.PhotoImage(file=c)
                    self.iconphoto(False, img)
                    self._icon_ref = img
                    break
                except Exception:
                    pass

    def _configurar_estilos(self):
        style = ttk.Style()
        style.configure("Permissoes.TCheckbutton", font=("Segoe UI", 9))

    def _criar_interface(self):
        # 1. Header Banner Corporativo
        banner = tk.Frame(self, bg="#1A365D", height=58)
        banner.pack(side=tk.TOP, fill=tk.X)
        banner.pack_propagate(False)

        lbl_tit = tk.Label(
            banner,
            text="🛡️ Clonagem de Permissões e Perfis de Acesso",
            font=("Segoe UI", 12, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
            anchor="w",
        )
        lbl_tit.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(8, 0))

        lbl_sub = tk.Label(
            banner,
            text="Replicação completa e modular de acessos, relatórios, contas financeiras e categorias entre operadores",
            font=("Segoe UI", 8),
            bg="#1A365D",
            fg="#CBD5E0",
            anchor="w",
        )
        lbl_sub.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(1, 6))

        # 2. Painel de Usuários (Origem e Destino)
        f_users = ttk.LabelFrame(self, text="Seleção de Perfis", padding=12)
        f_users.pack(side=tk.TOP, fill=tk.X, padx=14, pady=10)

        ru1 = ttk.Frame(f_users)
        ru1.pack(fill=tk.X, pady=4)
        ttk.Label(ru1, text="Usuário de Origem (Modelo):*", width=25).pack(side=tk.LEFT)
        self.combo_origem = ttk.Combobox(ru1, state="readonly", width=42, font=("Segoe UI", 9))
        self.combo_origem.pack(side=tk.LEFT, padx=(5, 0))

        ru2 = ttk.Frame(f_users)
        ru2.pack(fill=tk.X, pady=4)
        ttk.Label(ru2, text="Usuário de Destino (Receberá):*", width=25).pack(side=tk.LEFT)
        self.combo_destino = ttk.Combobox(ru2, state="readonly", width=42, font=("Segoe UI", 9))
        self.combo_destino.pack(side=tk.LEFT, padx=(5, 0))

        # 3. Painel de Opções Modulares (Checkboxes)
        f_opts = ttk.LabelFrame(self, text="Módulos de Permissões a Replicar", padding=12)
        f_opts.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=14, pady=5)

        # Botões de marcação rápida
        f_quick = ttk.Frame(f_opts)
        f_quick.pack(fill=tk.X, pady=(0, 8))
        btn_all = ttk.Button(f_quick, text="✔ Marcar Todos", command=self._marcar_todos)
        btn_all.pack(side=tk.LEFT, padx=(0, 6))
        btn_none = ttk.Button(f_quick, text="✖ Desmarcar Todos", command=self._desmarcar_todos)
        btn_none.pack(side=tk.LEFT)

        # Grid de Checkboxes
        f_chk_grid = ttk.Frame(f_opts)
        f_chk_grid.pack(fill=tk.BOTH, expand=True)

        self.chk_direitos = tk.BooleanVar(value=True)
        self.chk_relatorios = tk.BooleanVar(value=True)
        self.chk_contas = tk.BooleanVar(value=True)
        self.chk_forms = tk.BooleanVar(value=True)
        self.chk_categs = tk.BooleanVar(value=True)
        self.chk_tipopag = tk.BooleanVar(value=True)
        self.chk_grupos = tk.BooleanVar(value=True)
        self.chk_favoritos = tk.BooleanVar(value=True)
        self.chk_tour = tk.BooleanVar(value=True)
        self.chk_empresas = tk.BooleanVar(value=True)

        col1 = ttk.Frame(f_chk_grid)
        col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        col2 = ttk.Frame(f_chk_grid)
        col2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        ttk.Checkbutton(col1, text="Direitos Gerais do Sistema (Telas/Ações)", variable=self.chk_direitos).pack(anchor="w", pady=3)
        ttk.Checkbutton(col1, text="Acesso a Relatórios Gerenciais", variable=self.chk_relatorios).pack(anchor="w", pady=3)
        ttk.Checkbutton(col1, text="Contas Financeiras Autorizadas", variable=self.chk_contas).pack(anchor="w", pady=3)
        ttk.Checkbutton(col1, text="Formulários e Menus do Sistema", variable=self.chk_forms).pack(anchor="w", pady=3)
        ttk.Checkbutton(col1, text="Categorias e Entidades Vinculadas", variable=self.chk_categs).pack(anchor="w", pady=3)

        ttk.Checkbutton(col2, text="Tipos de Contas a Pagar e Receber", variable=self.chk_tipopag).pack(anchor="w", pady=3)
        ttk.Checkbutton(col2, text="Grupos de Trabalho e Supervisão", variable=self.chk_grupos).pack(anchor="w", pady=3)
        ttk.Checkbutton(col2, text="Menus e Atalhos Favoritos", variable=self.chk_favoritos).pack(anchor="w", pady=3)
        ttk.Checkbutton(col2, text="Roteiro de Treinamento / Tour", variable=self.chk_tour).pack(anchor="w", pady=3)
        ttk.Checkbutton(col2, text="Empresas e Filiais Autorizadas", variable=self.chk_empresas).pack(anchor="w", pady=3)

        # 4. Painel de Status / Execução
        f_exec = ttk.Frame(self, padding=12)
        f_exec.pack(side=tk.BOTTOM, fill=tk.X, padx=14, pady=(0, 10))

        self.lbl_status = tk.Label(f_exec, text="Pronto para replicar permissões.", font=("Segoe UI", 9), fg="#4A5568")
        self.lbl_status.pack(side=tk.LEFT)

        btn_fechar = ttk.Button(f_exec, text="Fechar (Esc)", command=self.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=(6, 0))

        btn_clonar = ttk.Button(f_exec, text="🚀 Executar Clonagem", command=self._executar_clonagem)
        btn_clonar.pack(side=tk.RIGHT)

    def _marcar_todos(self):
        for var in (
            self.chk_direitos, self.chk_relatorios, self.chk_contas, self.chk_forms,
            self.chk_categs, self.chk_tipopag, self.chk_grupos, self.chk_favoritos,
            self.chk_tour, self.chk_empresas
        ):
            var.set(True)

    def _desmarcar_todos(self):
        for var in (
            self.chk_direitos, self.chk_relatorios, self.chk_contas, self.chk_forms,
            self.chk_categs, self.chk_tipopag, self.chk_grupos, self.chk_favoritos,
            self.chk_tour, self.chk_empresas
        ):
            var.set(False)

    def _carregar_usuarios(self):
        if not self._service:
            return

        try:
            self._usuarios = self._service.listar_usuarios()
            self._map_usuarios = {f"{u['codigo']} - {u['nome']}": u['codigo'] for u in self._usuarios}
            valores = list(self._map_usuarios.keys())
            self.combo_origem["values"] = valores
            self.combo_destino["values"] = valores
        except Exception as exc:
            logger.exception("Erro ao carregar lista de usuários: %s", exc)

    def _executar_clonagem(self):
        orig_key = self.combo_origem.get()
        dest_key = self.combo_destino.get()

        orig_cod = getattr(self, "_map_usuarios", {}).get(orig_key, "")
        dest_cod = getattr(self, "_map_usuarios", {}).get(dest_key, "")

        if not orig_cod or not dest_cod:
            messagebox.showwarning("Aviso", "Selecione o Usuário de Origem e o Usuário de Destino.")
            return

        if orig_cod == dest_cod:
            messagebox.showwarning("Aviso", "O usuário de origem e de destino não podem ser iguais.")
            return

        conf = messagebox.askyesno(
            "Confirmação de Clonagem",
            f"Confirma a replicação dos direitos selecionados do usuário:\n"
            f"ORIGEM: {orig_key}\n"
            f"PARA DESTINO: {dest_key}?"
        )
        if not conf:
            return

        opcoes = OpcoesClonagemDTO(
            direitos_sistema=self.chk_direitos.get(),
            relatorios=self.chk_relatorios.get(),
            contas_financeiras=self.chk_contas.get(),
            formularios=self.chk_forms.get(),
            categorias_entidades=self.chk_categs.get(),
            tipo_pagar_receber=self.chk_tipopag.get(),
            grupos_usuario=self.chk_grupos.get(),
            favoritos=self.chk_favoritos.get(),
            tour_usuario=self.chk_tour.get(),
            empresas_filiais=self.chk_empresas.get(),
        )

        self.lbl_status.config(text="Executando clonagem...", fg="#2B6CB0")
        self.update_idletasks()

        if self._service:
            res = self._service.clonar_permissoes(orig_cod, dest_cod, opcoes)
            if res.sucesso:
                self.lbl_status.config(text=f"Concluído: {res.total_itens} itens clonados.", fg="#22543D")
                messagebox.showinfo("Sucesso", res.mensagem)
            else:
                self.lbl_status.config(text="Erro durante a clonagem.", fg="#C53030")
                messagebox.showerror("Erro de Clonagem", res.mensagem)
