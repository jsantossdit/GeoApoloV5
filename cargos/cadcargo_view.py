"""
Formulário de Cadastro e Manutenção de Cargos (FrmCadCargo).
GeoApolo V5 - Equivalente e evolução direta sob o padrão GeoAlvo.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import tkinter as tk
from tkinter import ttk, messagebox

# Garante que o diretório raiz esteja no sys.path
_raiz_projeto = str(Path(__file__).resolve().parent.parent)
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

from core import obter_caminho_recurso, centralizar_janela, vincular_maiusculo, configurar_navegacao_enter
from cargos.models import CargoDTO, ResultadoCargoDTO
from cargos.repository import CargoRepository
from cargos.service import CargoService
from entidades.database import obter_conexao_banco

logger = logging.getLogger(__name__)


class FrmCadCargo(tk.Toplevel):
    """
    Formulário para inclusão e manutenção de cargos.
    Padrão corporativo GeoAlvo / GeoApolo V5.
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
        cargo_inicial: Optional[Dict[str, Any]] = None,
    ):
        if getattr(self, "_ja_inicializada", False):
            return
        super().__init__(parent)
        self._ja_inicializada = True
        FrmCadCargo._instancia_ativa = self

        self.parent = parent
        self._conn = connection
        self.on_salvar = on_salvar
        self._modo_inclusao = True

        if self._conn is None:
            try:
                self._conn = obter_conexao_banco()
            except Exception as exc:
                logger.warning("Falha ao obter conexão: %s", exc)

        self._repo = CargoRepository(self._conn) if self._conn else None
        self._service = CargoService(self._repo) if self._repo else None

        self.title("Cadastro e Manutenção de Cargos - GeoAlvo")
        self.geometry("740x500")
        self.minsize(620, 420)

        centralizar_janela(self, parent, 740, 500)
        self._aplicar_icone()

        if parent:
            try:
                self.transient(parent)
            except Exception:
                pass

        self._criar_interface()
        self._carregar_grid_cargos()

        if cargo_inicial:
            self._carregar_dados_cargo(cargo_inicial)
        else:
            self.novo_registro()

        self._configurar_maiusculas_e_enter()

        # Atalhos de teclado
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Insert>", lambda e: self.novo_registro())
        self.bind("<F2>", lambda e: self.salvar_registro())

    def _aplicar_icone(self):
        try:
            ico = obter_caminho_recurso("GeoApolo_Icon.ico")
            if os.path.isfile(ico):
                self.iconbitmap(ico)
        except Exception:
            pass

    def _criar_interface(self):
        self.configure(bg="#F1F5F9")

        # 1. Header Superior
        header = tk.Frame(self, bg="#1E3A8A", height=50)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        lbl_tit = tk.Label(
            header,
            text="🏷 Cadastro e Manutenção de Cargos",
            font=("Segoe UI", 12, "bold"),
            bg="#1E3A8A",
            fg="white",
        )
        lbl_tit.pack(side=tk.LEFT, padx=16, pady=10)

        self.lbl_status_contador = tk.Label(
            header,
            text="0 cargo(s)",
            font=("Segoe UI", 9, "bold"),
            bg="#1E3A8A",
            fg="#93C5FD",
        )
        self.lbl_status_contador.pack(side=tk.RIGHT, padx=16, pady=10)

        # 2. Barra de Ferramentas / Pesquisa
        toolbar = tk.Frame(self, bg="#FFFFFF", bd=1, relief=tk.SOLID, padx=10, pady=8)
        toolbar.pack(fill=tk.X, padx=12, pady=(10, 6))

        btn_novo = tk.Button(
            toolbar,
            text="➕ Novo (Insert)",
            bg="#16A34A",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.novo_registro,
        )
        btn_novo.pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(toolbar, text="Pesquisar:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155").pack(side=tk.LEFT, padx=(0, 5))
        self.var_busca = tk.StringVar()
        vincular_maiusculo(self.var_busca)
        self.ent_busca = ttk.Entry(toolbar, textvariable=self.var_busca, width=32)
        self.ent_busca.pack(side=tk.LEFT, padx=(0, 8))
        self.ent_busca.bind("<KeyRelease>", lambda e: self._filtrar_cargos())
        self.ent_busca.bind("<Return>", lambda e: self._filtrar_cargos())

        btn_limpar = ttk.Button(toolbar, text="Limpar", command=self._limpar_busca)
        btn_limpar.pack(side=tk.LEFT)

        # 3. Painel Central: Grid de Listagem
        frame_grid = tk.Frame(self, bg="#F1F5F9")
        frame_grid.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        colunas = ("codigo", "nome", "faixa")
        self.tree = ttk.Treeview(frame_grid, columns=colunas, show="headings", selectmode="browse", height=8)

        self.tree.heading("codigo", text="Código")
        self.tree.heading("nome", text="Nome do Cargo")
        self.tree.heading("faixa", text="Faixa Salarial")

        self.tree.column("codigo", width=90, minwidth=70, anchor=tk.CENTER)
        self.tree.column("nome", width=380, minwidth=200, anchor=tk.W)
        self.tree.column("faixa", width=140, minwidth=100, anchor=tk.CENTER)

        scroll_y = ttk.Scrollbar(frame_grid, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._ao_selecionar_item)
        self.tree.bind("<Double-1>", lambda e: self.ent_nome.focus_set())

        # 4. Painel Inferior: Formulário de Edição
        self.frame_form = tk.LabelFrame(
            self,
            text=" Dados do Cargo ",
            font=("Segoe UI", 9, "bold"),
            bg="#FFFFFF",
            fg="#1E3A8A",
            padx=12,
            pady=10,
        )
        self.frame_form.pack(fill=tk.X, padx=12, pady=(6, 12))

        # Linha 1: Código, Nome, Faixa Salarial
        f_row1 = tk.Frame(self.frame_form, bg="#FFFFFF")
        f_row1.pack(fill=tk.X, pady=4)

        tk.Label(f_row1, text="Código:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155").pack(side=tk.LEFT, padx=(0, 4))
        self.var_codigo = tk.StringVar()
        self.ent_codigo = ttk.Entry(f_row1, textvariable=self.var_codigo, width=10, justify=tk.CENTER)
        self.ent_codigo.pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(f_row1, text="Nome do Cargo: *", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155").pack(side=tk.LEFT, padx=(0, 4))
        self.var_nome = tk.StringVar()
        self.ent_nome = ttk.Entry(f_row1, textvariable=self.var_nome, width=38)
        self.ent_nome.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))

        tk.Label(f_row1, text="Faixa Salarial:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#334155").pack(side=tk.LEFT, padx=(0, 4))
        self.var_faixa = tk.StringVar()
        self.ent_faixa = ttk.Entry(f_row1, textvariable=self.var_faixa, width=14, justify=tk.CENTER)
        self.ent_faixa.pack(side=tk.LEFT)

        # 5. Barra de Botões de Ação
        f_botoes = tk.Frame(self.frame_form, bg="#FFFFFF")
        f_botoes.pack(fill=tk.X, pady=(10, 0))

        self.btn_salvar = tk.Button(
            f_botoes,
            text="💾 Salvar Cargo (F2)",
            bg="#2563EB",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=14,
            pady=4,
            cursor="hand2",
            command=self.salvar_registro,
        )
        self.btn_salvar.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_excluir = tk.Button(
            f_botoes,
            text="🗑 Excluir",
            bg="#DC2626",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.excluir_registro,
        )
        self.btn_excluir.pack(side=tk.LEFT, padx=(0, 8))

        btn_fechar = ttk.Button(f_botoes, text="Fechar (Esc)", command=self.destroy)
        btn_fechar.pack(side=tk.RIGHT)

    def _configurar_maiusculas_e_enter(self):
        vincular_maiusculo(self.var_nome)
        vincular_maiusculo(self.var_faixa)
        configurar_navegacao_enter([self.ent_codigo, self.ent_nome, self.ent_faixa, self.btn_salvar])

    def _limpar_busca(self):
        self.var_busca.set("")
        self._carregar_grid_cargos()

    def _filtrar_cargos(self):
        termo = self.var_busca.get().strip()
        self._carregar_grid_cargos(termo=termo)

    def _carregar_grid_cargos(self, termo: str = ""):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self._service:
            return

        cargos = self._service.listar_cargos(termo=termo)
        for c in cargos:
            self.tree.insert(
                "",
                tk.END,
                iid=str(c.geocargocodestr),
                values=(c.geocargocodestr, c.geocargonome, c.geofaixasalarial or "-"),
            )

        total = len(cargos)
        self.lbl_status_contador.config(text=f"{total} cargo(s)")

    def _ao_selecionar_item(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        cod_str = sel[0]
        try:
            cod_int = int(cod_str)
            if self._service:
                cargo = self._service.obter_cargo(cod_int)
                if cargo:
                    self._carregar_dados_cargo({
                        "codigo": cargo.geocargocodestr,
                        "nome": cargo.geocargonome,
                        "faixa": cargo.geofaixasalarial,
                    })
        except Exception as e:
            logger.warning("Erro ao carregar cargo selecionado: %s", e)

    def _carregar_dados_cargo(self, dados: Dict[str, Any]):
        self._modo_inclusao = False
        self.var_codigo.set(str(dados.get("codigo", "") or ""))
        self.var_nome.set(str(dados.get("nome", "") or ""))
        self.var_faixa.set(str(dados.get("faixa", "") or ""))
        self.ent_codigo.config(state="readonly")
        self.btn_excluir.config(state=tk.NORMAL)

    def novo_registro(self):
        """Prepara o formulário para inclusão de um novo cargo."""
        self._modo_inclusao = True
        prox_cod = 1
        if self._service:
            prox_cod = self._service.obter_proximo_codigo()

        self.var_codigo.set(str(prox_cod))
        self.var_nome.set("")
        self.var_faixa.set("")
        self.ent_codigo.config(state=tk.NORMAL)
        self.btn_excluir.config(state=tk.DISABLED)

        # Remove seleção da tree
        sel = self.tree.selection()
        if sel:
            self.tree.selection_remove(sel)

        self.ent_nome.focus_set()

    def salvar_registro(self):
        """Valida e salva o registro de cargo."""
        if not self._service:
            messagebox.showerror("Erro", "Serviço de dados não inicializado.", parent=self)
            return

        cod_str = self.var_codigo.get().strip()
        try:
            cod_int = int(cod_str)
        except ValueError:
            messagebox.showerror("Código Inválido", "O código do cargo deve ser um número inteiro.", parent=self)
            self.ent_codigo.focus_set()
            return

        nome = self.var_nome.get().strip().upper()
        if not nome:
            messagebox.showwarning("Campo Obrigatório", "O Nome do Cargo é obrigatório.", parent=self)
            self.ent_nome.focus_set()
            return

        dto = CargoDTO(
            geocargocodestr=cod_int,
            geocargonome=nome,
            geofaixasalarial=self.var_faixa.get().strip().upper(),
        )

        res = self._service.salvar_cargo(dto)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem, parent=self)
            self._carregar_grid_cargos(termo=self.var_busca.get().strip())
            # Seleciona na treeview
            if str(res.codigo) in self.tree.get_children():
                self.tree.selection_set(str(res.codigo))
                self.tree.see(str(res.codigo))
            if callable(self.on_salvar):
                try:
                    self.on_salvar()
                except Exception:
                    pass
        else:
            messagebox.showerror("Erro ao Salvar", res.mensagem, parent=self)

    def excluir_registro(self):
        """Exclui o cargo selecionado com confirmação."""
        if self._modo_inclusao:
            return

        cod_str = self.var_codigo.get().strip()
        try:
            cod_int = int(cod_str)
        except ValueError:
            return

        nome = self.var_nome.get().strip()
        confirma = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o Cargo Nº {cod_int} - '{nome}'?",
            parent=self,
            default=messagebox.NO,
        )
        if not confirma:
            return

        res = self._service.excluir_cargo(cod_int)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem, parent=self)
            self._carregar_grid_cargos(termo=self.var_busca.get().strip())
            self.novo_registro()
            if callable(self.on_salvar):
                try:
                    self.on_salvar()
                except Exception:
                    pass
        else:
            messagebox.showerror("Erro ao Excluir", res.mensagem, parent=self)


def abrir_cargos(parent=None, connection=None, on_salvar=None) -> FrmCadCargo:
    """Função utilitária para instanciar e exibir a janela de Cargos."""
    return FrmCadCargo(parent=parent, connection=connection, on_salvar=on_salvar)
