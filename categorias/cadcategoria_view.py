"""
Formulário de Cadastro e Manutenção de Categorias (FrmCadCategoria).
GeoApolo V5 - Equivalente e evolução direta de unt_cadcategorias.pas / unt_cadcategorias.dfm (Delphi).
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List
import tkinter as tk
from tkinter import ttk, messagebox

# Garante que o diretório raiz esteja no sys.path
_raiz_projeto = str(Path(__file__).resolve().parent.parent)
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

from core import obter_caminho_recurso, centralizar_janela
from categorias.models import ResultadoOperacao
from categorias.repository import CategoriaEntidadeRepository
from categorias.service import CategoriaEntidadeService
from entidades.database import obter_conexao_banco

logger = logging.getLogger(__name__)


class FrmCadCategoria(tk.Toplevel):
    """
    Formulário para inclusão e manutenção de categorias de entidades.
    Corresponde ao Tfrmcadcategoria do Delphi (unt_cadcategorias.pas).
    """
    _instancia_ativa = None

    def __new__(cls, *args, **kwargs):
        if cls._instancia_ativa is not None and cls._instancia_ativa.winfo_exists():
            try:
                cls._instancia_ativa.deiconify()
                cls._instancia_ativa.lift()
                cls._instancia_ativa.focus_force()
            except Exception:
                pass
            return cls._instancia_ativa
        return super().__new__(cls)

    def __init__(
        self,
        parent=None,
        connection=None,
        on_salvar: Optional[Callable[[], None]] = None,
        categoria_inicial: Optional[Dict[str, Any]] = None,
    ):
        if getattr(self, "_ja_inicializada", False):
            return
        super().__init__(parent)
        self._ja_inicializada = True
        FrmCadCategoria._instancia_ativa = self

        self.parent = parent
        self._conn = connection
        self.on_salvar = on_salvar
        self._modo_inclusao = True
        self._codigo_antigo = ""

        if self._conn is None:
            try:
                self._conn = obter_conexao_banco()
            except Exception as exc:
                logger.warning("Falha ao obter conexão: %s", exc)

        self._repo = CategoriaEntidadeRepository(self._conn) if self._conn else None
        self._service = CategoriaEntidadeService(self._repo) if self._repo else None

        self.title("Manutenção de Categorias - GeoAlvo")
        self.geometry("780x520")
        self.minsize(640, 420)

        centralizar_janela(self, parent, 780, 520)
        self._aplicar_icone()

        if parent:
            try:
                self.transient(parent)
            except Exception:
                pass

        self._criar_interface()
        self._carregar_grid_categorias()

        if categoria_inicial:
            self._carregar_dados_categoria(categoria_inicial)
        else:
            self.novo_registro()

        self._configurar_maiusculas_e_enter()

        # Atalhos globais da janela
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Insert>", lambda e: self.novo_registro())
        self.bind("<F3>", lambda e: self.salvar())

    def _aplicar_icone(self):
        caminhos = [
            obter_caminho_recurso(os.path.join("Imagens", "entidades.png")),
            obter_caminho_recurso(os.path.join("Imagens", "GeoApolo_Icon.ico")),
            obter_caminho_recurso(os.path.join("Imagens", "IconeRCC.png")),
        ]
        for c in caminhos:
            if os.path.exists(c):
                try:
                    if c.endswith(".ico"):
                        self.iconbitmap(c)
                    else:
                        img = tk.PhotoImage(file=c)
                        self.iconphoto(False, img)
                        self._icon_ref = img
                    break
                except Exception:
                    pass

    def _criar_interface(self):
        # 1. Top Banner
        banner = tk.Frame(self, bg="#1E3A8A", height=48)
        banner.pack(side=tk.TOP, fill=tk.X)
        banner.pack_propagate(False)

        lbl_tit = tk.Label(
            banner,
            text="🏷 Cadastro e Manutenção de Categorias",
            font=("Segoe UI", 11, "bold"),
            bg="#1E3A8A",
            fg="#FFFFFF",
            anchor="w",
        )
        lbl_tit.pack(side=tk.LEFT, padx=14, pady=10)

        self.lbl_modo = tk.Label(
            banner,
            text="MODO: INCLUSÃO",
            font=("Segoe UI", 9, "bold"),
            bg="#1E3A8A",
            fg="#FDE047",
            anchor="e",
        )
        self.lbl_modo.pack(side=tk.RIGHT, padx=14, pady=10)

        # 2. Toolbar
        toolbar = tk.Frame(self, bg="#E2E8F0", height=42, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        toolbar.pack_propagate(False)

        btn_novo = ttk.Button(toolbar, text="➕ Novo (Ins)", command=self.novo_registro)
        btn_novo.pack(side=tk.LEFT, padx=(10, 4), pady=6)

        btn_salvar = ttk.Button(toolbar, text="💾 Salvar (F3)", command=self.salvar)
        btn_salvar.pack(side=tk.LEFT, padx=4, pady=6)

        btn_limpar = ttk.Button(toolbar, text="✖ Limpar", command=self.limpar_campos)
        btn_limpar.pack(side=tk.LEFT, padx=4, pady=6)

        btn_excluir = ttk.Button(toolbar, text="🗑 Excluir", command=self.excluir)
        btn_excluir.pack(side=tk.LEFT, padx=4, pady=6)

        btn_fechar = ttk.Button(toolbar, text="🚪 Fechar (Esc)", command=self.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=12, pady=6)

        # 3. Painel de Dados da Categoria
        pnl_campos = ttk.LabelFrame(self, text=" Dados da Categoria ", padding=10)
        pnl_campos.pack(side=tk.TOP, fill=tk.X, padx=10, pady=8)

        # Linha 1: Código Estruturado, Código Alternativo e Checkbox Grupo
        row1 = ttk.Frame(pnl_campos)
        row1.pack(fill=tk.X, pady=4)

        ttk.Label(row1, text="Código Categoria:*").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_codigo_estrutural = ttk.Entry(row1, width=16)
        self.txt_codigo_estrutural.pack(side=tk.LEFT, padx=(0, 16))

        ttk.Label(row1, text="Código Alternativo:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_codigo_alternativo = ttk.Entry(row1, width=14)
        self.txt_codigo_alternativo.pack(side=tk.LEFT, padx=(0, 16))

        self.var_grupo = tk.BooleanVar(value=False)
        self.chk_grupo = ttk.Checkbutton(row1, text="Categoria Agrupadora (Grupo)", variable=self.var_grupo)
        self.chk_grupo.pack(side=tk.LEFT, padx=8)

        # Linha 2: Nome da Categoria
        row2 = ttk.Frame(pnl_campos)
        row2.pack(fill=tk.X, pady=4)

        ttk.Label(row2, text="Nome da Categoria:*").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_nome = ttk.Entry(row2, width=64)
        self.txt_nome.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 4. Grid de Categorias Cadastradas
        pnl_grid = ttk.LabelFrame(self, text=" Categorias Cadastradas ", padding=8)
        pnl_grid.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        colunas = ("codigo", "nome", "grupo", "codalt")
        self.tree = ttk.Treeview(pnl_grid, columns=colunas, show="headings", height=8, selectmode="browse")

        self.tree.heading("codigo", text="Código Estruturado")
        self.tree.heading("nome", text="Nome da Categoria")
        self.tree.heading("grupo", text="Grupo")
        self.tree.heading("codalt", text="Cód. Alternativo")

        self.tree.column("codigo", width=140, anchor="w")
        self.tree.column("nome", width=360, anchor="w")
        self.tree.column("grupo", width=80, anchor="center")
        self.tree.column("codalt", width=120, anchor="center")

        sc_y = ttk.Scrollbar(pnl_grid, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sc_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self._on_tree_double_click)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Delete>", lambda e: self.excluir())

        # 5. Status Bar
        self.statusbar = tk.Label(
            self,
            text="Pronto para inclusão ou edição de categorias.",
            font=("Segoe UI", 9),
            bd=1,
            relief=tk.SUNKEN,
            anchor="w",
            bg="#F1F5F9",
            fg="#475569",
            padx=10,
            pady=3,
        )
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def _configurar_maiusculas_e_enter(self):
        """Padroniza campos texto como maiúsculos e permite passar de um campo para outro com Enter."""
        def _on_key_release_upper(event):
            widget = event.widget
            if event.keysym in (
                "Left", "Right", "Up", "Down", "Home", "End", "Tab", "Return",
                "Escape", "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Caps_Lock"
            ):
                return
            try:
                pos = widget.index(tk.INSERT)
                val = widget.get()
                val_u = val.upper()
                if val != val_u:
                    widget.delete(0, tk.END)
                    widget.insert(0, val_u)
                    widget.icursor(pos)
            except Exception:
                pass

        def _on_enter_navegar(event):
            widget = event.widget
            prox = widget.tk_focusNext()
            if prox:
                prox.focus_set()
                if hasattr(prox, "selection_range"):
                    try:
                        prox.selection_range(0, tk.END)
                    except Exception:
                        pass
            return "break"

        for entry in (self.txt_codigo_estrutural, self.txt_codigo_alternativo, self.txt_nome):
            entry.bind("<KeyRelease>", _on_key_release_upper, add="+")
            entry.bind("<Return>", _on_enter_navegar, add="+")

    def _carregar_grid_categorias(self):
        """Preenche o grid com todas as categorias cadastradas."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self._service:
            return

        try:
            categorias = self._service.listar_todas_categorias()
            for cat in categorias:
                cod = str(cat.get("codigo", "")).strip()
                nome = str(cat.get("descricao", "")).strip()
                grupo = "Sim" if str(cat.get("grupo", "")).strip().upper() == "S" else "Não"
                codalt = str(cat.get("codigo_alternativo", "")).strip()
                self.tree.insert("", tk.END, values=(cod, nome, grupo, codalt))
            self.statusbar.config(text=f"{len(categorias)} categoria(s) cadastrada(s).")
        except Exception as exc:
            logger.exception("Falha ao listar categorias no formulário: %s", exc)
            self.statusbar.config(text=f"Erro ao carregar categorias: {exc}")

    def novo_registro(self):
        """Prepara o formulário para um novo registro de categoria (equivalente a teclar Insert ou clicar Novo)."""
        self._modo_inclusao = True
        self._codigo_antigo = ""
        self.lbl_modo.config(text="MODO: INCLUSÃO", fg="#FDE047")

        self.txt_codigo_estrutural.delete(0, tk.END)
        self.txt_nome.delete(0, tk.END)
        self.var_grupo.set(False)

        prox_alt = ""
        if self._service:
            try:
                prox_alt = self._service.obter_proximo_codigo_alternativo()
            except Exception:
                pass

        self.txt_codigo_alternativo.delete(0, tk.END)
        if prox_alt:
            self.txt_codigo_alternativo.insert(0, prox_alt)

        self.txt_codigo_estrutural.focus_set()
        self.statusbar.config(text="Modo de Inclusão: Digite o código e nome da nova categoria.")

    def limpar_campos(self):
        """Limpa todos os campos de edição."""
        self.txt_codigo_estrutural.delete(0, tk.END)
        self.txt_codigo_alternativo.delete(0, tk.END)
        self.txt_nome.delete(0, tk.END)
        self.var_grupo.set(False)
        self.txt_codigo_estrutural.focus_set()

    def _carregar_dados_categoria(self, dados: Dict[str, Any]):
        """Carrega os dados de uma categoria para o formulário no modo alteração."""
        self._modo_inclusao = False
        cod = str(dados.get("codigo") or dados.get("geocategcodestr") or "").strip()
        nome = str(dados.get("descricao") or dados.get("geocategnome") or "").strip()
        codalt = str(dados.get("codigo_alternativo") or dados.get("geocategcodalt") or "").strip()
        grupo = str(dados.get("grupo") or dados.get("geocateggrupo") or "").strip().upper() == "S"

        self._codigo_antigo = cod
        self.lbl_modo.config(text=f"MODO: ALTERAÇÃO ({cod})", fg="#6EE7B7")

        self.txt_codigo_estrutural.delete(0, tk.END)
        self.txt_codigo_estrutural.insert(0, cod)

        self.txt_codigo_alternativo.delete(0, tk.END)
        self.txt_codigo_alternativo.insert(0, codalt)

        self.txt_nome.delete(0, tk.END)
        self.txt_nome.insert(0, nome)

        self.var_grupo.set(grupo)
        self.txt_nome.focus_set()
        self.statusbar.config(text=f"Categoria '{cod}' carregada para alteração.")

    def _on_tree_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        if vals:
            d = {
                "codigo": vals[0],
                "descricao": vals[1],
                "grupo": "S" if vals[2] == "Sim" else "N",
                "codigo_alternativo": vals[3],
            }
            self._carregar_dados_categoria(d)

    def _on_tree_double_click(self, event=None):
        self._on_tree_select()

    def salvar(self, event=None):
        """Valida e persiste a categoria na base USER_geoapolo_categoria."""
        cod_estr = self.txt_codigo_estrutural.get().strip().upper()
        nome = self.txt_nome.get().strip().upper()
        cod_alt = self.txt_codigo_alternativo.get().strip()
        grupo = "S" if self.var_grupo.get() else "N"

        if not cod_estr:
            messagebox.showwarning("Atenção", "O campo 'Código Categoria' é de preenchimento obrigatório.", parent=self)
            self.txt_codigo_estrutural.focus_set()
            return

        if not nome:
            messagebox.showwarning("Atenção", "O campo 'Nome da Categoria' é de preenchimento obrigatório.", parent=self)
            self.txt_nome.focus_set()
            return

        dados = {
            "codigo": cod_estr,
            "descricao": nome,
            "codigo_alternativo": cod_alt,
            "grupo": grupo,
            "codigo_antigo": self._codigo_antigo if not self._modo_inclusao else cod_estr,
        }

        if not self._service:
            messagebox.showerror("Erro", "Conexão com o banco de dados não disponível.", parent=self)
            return

        op = "Inclusão" if self._modo_inclusao else "Alteração"
        resp = messagebox.askyesno("Confirmação", f"Confirma a {op} desta categoria de entidade?", parent=self)
        if not resp:
            return

        res = self._service.salvar_categoria(dados, modo_inclusao=self._modo_inclusao)
        if not res.sucesso:
            messagebox.showerror("Erro ao Salvar Categoria", res.mensagem, parent=self)
            self.txt_codigo_estrutural.focus_set()
            return

        messagebox.showinfo("Sucesso", res.mensagem, parent=self)
        self._carregar_grid_categorias()

        if self.on_salvar:
            try:
                self.on_salvar()
            except Exception:
                pass

        self.novo_registro()

    def excluir(self):
        """Remove a categoria selecionada após confirmação."""
        cod_estr = self.txt_codigo_estrutural.get().strip().upper()
        if not cod_estr:
            sel = self.tree.selection()
            if sel:
                vals = self.tree.item(sel[0], "values")
                if vals:
                    cod_estr = vals[0]

        if not cod_estr:
            messagebox.showwarning("Atenção", "Selecione uma categoria para excluir.", parent=self)
            return

        resp = messagebox.askyesno("Exclusão de Categoria", f"Confirma a exclusão da categoria '{cod_estr}'?", parent=self)
        if not resp:
            return

        if not self._service:
            messagebox.showerror("Erro", "Conexão com o banco não disponível.", parent=self)
            return

        res = self._service.excluir_categoria(cod_estr)
        if not res.sucesso:
            messagebox.showerror("Erro ao Excluir Categoria", res.mensagem, parent=self)
            return

        messagebox.showinfo("Sucesso", res.mensagem, parent=self)
        self._carregar_grid_categorias()

        if self.on_salvar:
            try:
                self.on_salvar()
            except Exception:
                pass

        self.novo_registro()
