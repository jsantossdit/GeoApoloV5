"""
Interface Gráfica (Tkinter / ttk) para Relacionamento de Categorias de Entidades com Usuários e Grupos.
Layout corporativo profissional no padrão visual GeoAlvo.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import logging
from typing import List, Dict, Any, Optional

from categorias.models import ResultadoOperacao
from categorias.repository import CategoriaEntidadeRepository
from categorias.service import CategoriaEntidadeService
from entidades.database import obter_conexao_banco

logger = logging.getLogger(__name__)


class CategoriasEntidadeView(tk.Toplevel):
    """Janela de Gerenciamento de Categorias e Vínculos de Entidades."""

    def __init__(self, parent=None, connection=None):
        super().__init__(parent)
        self.title("Relacionamento de Categorias de Entidades - GeoAlvo")
        self.geometry("1000x620")
        self.minsize(820, 500)

        self._centralizar_janela(1000, 620)
        self._aplicar_icone()

        self._conn = connection
        if self._conn is None:
            try:
                self._conn = obter_conexao_banco()
            except Exception as exc:
                messagebox.showwarning(
                    "Aviso de Conexão",
                    f"Não foi possível conectar automaticamente ao banco:\n{exc}\n\nConfigure o banco no menu Configurações."
                )

        self._repo = CategoriaEntidadeRepository(self._conn) if self._conn else None
        self._service = CategoriaEntidadeService(self._repo) if self._repo else None

        self._usuarios: List[Dict[str, str]] = []
        self._grupos: List[Dict[str, str]] = []
        self._categorias_atuais: List[Dict[str, Any]] = []

        self._configurar_estilos()
        self._criar_interface()
        self._carregar_seletores()

        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<F5>", lambda e: self._carregar_categorias())

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
        style.configure(
            "Categorias.Treeview",
            font=("Segoe UI", 9),
            rowheight=26,
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
        )
        style.configure(
            "Categorias.Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            foreground="#1A365D",
            padding=5,
        )

    def _criar_interface(self):
        # 1. Header Banner Corporativo
        banner = tk.Frame(self, bg="#1A365D", height=58)
        banner.pack(side=tk.TOP, fill=tk.X)
        banner.pack_propagate(False)

        lbl_tit = tk.Label(
            banner,
            text="🏷 Relacionamento de Categorias de Entidades",
            font=("Segoe UI", 12, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
            anchor="w",
        )
        lbl_tit.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(8, 0))

        lbl_sub = tk.Label(
            banner,
            text="Associação e controle de acesso de categorias e entidades para usuários e grupos de trabalho",
            font=("Segoe UI", 8),
            bg="#1A365D",
            fg="#CBD5E0",
            anchor="w",
        )
        lbl_sub.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(1, 6))

        # 2. Painel de Seleção (Modo e Usuário/Grupo)
        ctrl_box = ttk.LabelFrame(self, text="Seleção de Operação", padding=10)
        ctrl_box.pack(side=tk.TOP, fill=tk.X, padx=12, pady=(10, 5))

        r_row = ttk.Frame(ctrl_box)
        r_row.pack(fill=tk.X)

        self.var_modo = tk.StringVar(value="Usuario")
        rb_usu = ttk.Radiobutton(
            r_row,
            text="Por Usuário",
            variable=self.var_modo,
            value="Usuario",
            command=self._on_modo_alterado,
        )
        rb_usu.pack(side=tk.LEFT, padx=(0, 15))

        rb_grp = ttk.Radiobutton(
            r_row,
            text="Por Grupo de Trabalho",
            variable=self.var_modo,
            value="Grupo",
            command=self._on_modo_alterado,
        )
        rb_grp.pack(side=tk.LEFT, padx=(0, 20))

        self.lbl_seletor = ttk.Label(r_row, text="Usuário:")
        self.lbl_seletor.pack(side=tk.LEFT, padx=(0, 5))

        self.combo_alvo = ttk.Combobox(r_row, state="readonly", width=38, font=("Segoe UI", 9))
        self.combo_alvo.pack(side=tk.LEFT, padx=(0, 15))
        self.combo_alvo.bind("<<ComboboxSelected>>", lambda e: self._carregar_categorias())

        btn_atualizar = ttk.Button(r_row, text="🔄 Atualizar (F5)", command=self._carregar_categorias)
        btn_atualizar.pack(side=tk.LEFT, padx=4)

        # 3. Grid Central de Categorias
        grid_container = ttk.LabelFrame(self, text="Categorias Disponíveis", padding=8)
        grid_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=12, pady=5)

        colunas = ("codigo", "descricao", "total_entidades", "status")
        scroll_y = ttk.Scrollbar(grid_container, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(grid_container, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(
            grid_container,
            columns=colunas,
            show="headings",
            selectmode="browse",
            style="Categorias.Treeview",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
        )
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        self.tree.heading("codigo", text="Código Categoria")
        self.tree.heading("descricao", text="Descrição da Categoria")
        self.tree.heading("total_entidades", text="Total de Entidades Vinculadas")
        self.tree.heading("status", text="Status do Vínculo")

        self.tree.column("codigo", width=140, anchor=tk.CENTER)
        self.tree.column("descricao", width=380, anchor=tk.W)
        self.tree.column("total_entidades", width=180, anchor=tk.CENTER)
        self.tree.column("status", width=180, anchor=tk.CENTER)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.tag_configure("par", background="#FFFFFF")
        self.tree.tag_configure("impar", background="#F7FAFC")
        self.tree.tag_configure("vinculada", foreground="#2B6CB0")
        self.tree.tag_configure("nao_vinculada", foreground="#718096")

        self.tree.bind("<Double-1>", lambda e: self._acao_vincular_categoria())

        # 4. Rodapé e Ações
        bottom_frame = tk.Frame(self, bg="#E2E8F0", height=46, bd=1, relief=tk.GROOVE)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        bottom_frame.pack_propagate(False)

        btn_box = tk.Frame(bottom_frame, bg="#E2E8F0")
        btn_box.pack(side=tk.LEFT, padx=10, pady=7)

        ttk.Button(btn_box, text="✔ Vincular Categoria", command=self._acao_vincular_categoria).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_box, text="🔗 Relacionar Entidades da Categoria", command=self._acao_relacionar_entidades).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_box, text="🗑 Remover Relacionamento", command=self._acao_remover_relacionamento).pack(side=tk.LEFT, padx=4)

        btn_fechar = ttk.Button(bottom_frame, text="🚪 Fechar (Esc)", command=self.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=12, pady=7)

        self.lbl_status = tk.Label(
            bottom_frame,
            text="0 categorias listadas.",
            font=("Segoe UI", 9, "italic"),
            bg="#E2E8F0",
            fg="#4A5568",
        )
        self.lbl_status.pack(side=tk.RIGHT, padx=16)

    def _carregar_seletores(self):
        if not self._service:
            return
        try:
            self._usuarios = self._service.obter_usuarios()
            self._grupos = self._service.obter_grupos()
            self._on_modo_alterado()
        except Exception as exc:
            logger.exception("Erro ao carregar seletores: %s", exc)

    def _on_modo_alterado(self):
        modo = self.var_modo.get()
        if modo == "Usuario":
            self.lbl_seletor.config(text="Usuário Ativo:")
            valores = [f"{u['codigo']} - {u['nome']}" for u in self._usuarios]
            self.combo_alvo.config(values=valores)
            if valores:
                self.combo_alvo.set(valores[0])
        else:
            self.lbl_seletor.config(text="Grupo de Usuários:")
            valores = [f"{g['codigo']} - {g['descricao']}" for g in self._grupos]
            self.combo_alvo.config(values=valores)
            if valores:
                self.combo_alvo.set(valores[0])

        self._carregar_categorias()

    def _obter_id_selecionado(self) -> str:
        txt = self.combo_alvo.get().strip()
        if " - " in txt:
            return txt.split(" - ")[0].strip()
        return txt

    def _carregar_categorias(self):
        alvo_id = self._obter_id_selecionado()
        if not self._service or not alvo_id:
            return

        try:
            modo = self.var_modo.get()
            self._categorias_atuais = self._service.obter_categorias(modo, alvo_id)

            for item in self.tree.get_children():
                self.tree.delete(item)

            total_vinculadas = 0
            for idx, reg in enumerate(self._categorias_atuais):
                vinculada = reg.get("vinculada", False)
                if vinculada:
                    total_vinculadas += 1

                tag_zebra = "par" if idx % 2 == 0 else "impar"
                tag_status = "vinculada" if vinculada else "nao_vinculada"
                txt_status = "✔ Vinculada" if vinculada else "— Não Vinculada —"

                self.tree.insert(
                    "",
                    tk.END,
                    text=reg.get("codigo_categoria", ""),
                    values=(
                        reg.get("codigo_categoria", ""),
                        reg.get("descricao", ""),
                        reg.get("total_entidades", 0),
                        txt_status,
                    ),
                    tags=(tag_zebra, tag_status),
                )

            self.lbl_status.config(
                text=f"Total: {len(self._categorias_atuais)} categorias ({total_vinculadas} vinculadas)."
            )
        except Exception as exc:
            logger.exception("Erro ao carregar categorias: %s", exc)
            messagebox.showerror("Erro", f"Falha ao carregar categorias:\n{exc}")

    def _obter_categoria_selecionada(self) -> Optional[str]:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma categoria na lista primeiro.")
            return None
        return self.tree.item(sel[0], "text")

    def _acao_vincular_categoria(self):
        cat = self._obter_categoria_selecionada()
        if not cat:
            return
        modo = self.var_modo.get()
        alvo_id = self._obter_id_selecionado()
        res: ResultadoOperacao = self._service.vincular_categoria(modo, alvo_id, cat)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self._carregar_categorias()
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _acao_relacionar_entidades(self):
        cat = self._obter_categoria_selecionada()
        if not cat:
            return
        modo = self.var_modo.get()
        alvo_id = self._obter_id_selecionado()
        if not messagebox.askyesno(
            "Confirmação",
            f"Deseja relacionar todas as entidades da categoria '{cat}' para {modo.lower()} '{alvo_id}'?"
        ):
            return

        res: ResultadoOperacao = self._service.relacionar_entidades(modo, alvo_id, cat)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self._carregar_categorias()
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _acao_remover_relacionamento(self):
        cat = self._obter_categoria_selecionada()
        if not cat:
            return
        modo = self.var_modo.get()
        alvo_id = self._obter_id_selecionado()
        if not messagebox.askyesno(
            "Confirmação",
            f"Confirma a remoção do relacionamento da categoria '{cat}' para {modo.lower()} '{alvo_id}'?"
        ):
            return

        res: ResultadoOperacao = self._service.remover_relacionamento(modo, alvo_id, cat)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self._carregar_categorias()
        else:
            messagebox.showerror("Erro", res.mensagem)
