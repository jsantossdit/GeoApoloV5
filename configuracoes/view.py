"""
Interface Gráfica (Tkinter / ttk) para Parâmetros e Configurações Gerais do Sistema.
Layout corporativo profissional no padrão visual GeoAlvo.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import logging
from typing import Optional, Dict, Any

from configuracoes.models import (
    ResultadoOperacao,
    ConfiguracaoBancoDTO,
    ResultadoTesteConexaoDTO,
)

from configuracoes.repository import ConfiguracoesRepository
from configuracoes.service import ConfiguracoesService
from entidades.database import obter_conexao_banco
from core import centralizar_janela, vincular_maiusculo, configurar_navegacao_enter

logger = logging.getLogger(__name__)


class JanelaPesquisaParametro(tk.Toplevel):
    """Diálogo modal corporativo de pesquisa e seleção para parâmetros (F3/🔍)."""

    def __init__(self, parent, titulo: str, col_codigo_nome: str, col_descr_nome: str, buscar_func, callback_selecao, termo_inicial: str = ""):
        super().__init__(parent)
        self.title(titulo)
        self.transient(parent)
        self.grab_set()
        self._buscar_func = buscar_func
        self._callback = callback_selecao

        centralizar_janela(self, parent, 660, 480)

        # Header
        f_top = ttk.Frame(self, padding=(12, 10))
        f_top.pack(fill=tk.X)

        lbl_tit = ttk.Label(f_top, text=titulo, font=("Segoe UI", 11, "bold"), foreground="#1A365D")
        lbl_tit.pack(side=tk.LEFT)

        # Filtro
        f_busca = ttk.Frame(self, padding=(12, 4))
        f_busca.pack(fill=tk.X)

        ttk.Label(f_busca, text="Filtrar:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self.var_busca = tk.StringVar(value=termo_inicial)
        vincular_maiusculo(self.var_busca)
        self.ent_busca = ttk.Entry(f_busca, textvariable=self.var_busca, width=35, font=("Segoe UI", 9))
        self.ent_busca.pack(side=tk.LEFT, padx=(0, 6), fill=tk.X, expand=True)
        self.ent_busca.bind("<Return>", lambda e: self._filtrar())
        self.var_busca.trace_add("write", lambda *args: self._filtrar())

        btn_busca = ttk.Button(f_busca, text="Buscar", command=self._filtrar, width=10)
        btn_busca.pack(side=tk.LEFT)

        # Grid Treeview
        f_grid = ttk.Frame(self, padding=(12, 6))
        f_grid.pack(fill=tk.BOTH, expand=True)

        cols = ("codigo", "descricao")
        self.tree = ttk.Treeview(f_grid, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("codigo", text=col_codigo_nome)
        self.tree.heading("descricao", text=col_descr_nome)
        self.tree.column("codigo", width=140, anchor=tk.W)
        self.tree.column("descricao", width=460, anchor=tk.W)

        sb_y = ttk.Scrollbar(f_grid, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb_y.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", lambda e: (self._confirmar_selecao(), "break")[1])
        self.tree.bind("<Return>", lambda e: (self._confirmar_selecao(), "break")[1])

        # Rodapé com Botões
        f_bot = ttk.Frame(self, padding=(12, 10))
        f_bot.pack(fill=tk.X)

        self.lbl_cont = ttk.Label(f_bot, text="0 registro(s) encontrado(s)", font=("Segoe UI", 8, "italic"), foreground="#4A5568")
        self.lbl_cont.pack(side=tk.LEFT)

        btn_sel = tk.Button(
            f_bot,
            text="✔ Confirmar Seleção (Enter)",
            bg="#2563EB",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            relief=tk.FLAT,
            command=self._confirmar_selecao,
        )
        btn_sel.pack(side=tk.RIGHT, padx=(6, 0))

        btn_canc = ttk.Button(f_bot, text="Cancelar (Esc)", command=self.destroy)
        btn_canc.pack(side=tk.RIGHT)

        self.bind("<Escape>", lambda e: self.destroy())
        self.ent_busca.focus_set()
        self._after_id = self.after(50, self._filtrar)

    def destroy(self):
        if hasattr(self, "_after_id") and self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        super().destroy()

    def _filtrar(self):
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return
        termo = self.var_busca.get().strip()
        for it in self.tree.get_children():
            self.tree.delete(it)
        try:
            regs = self._buscar_func(termo)
            for r in regs:
                self.tree.insert("", tk.END, iid=r["codigo"], values=(r["codigo"], r["descricao"]))
            self.lbl_cont.config(text=f"{len(regs)} registro(s) encontrado(s)")
            children = self.tree.get_children()
            if children:
                self.tree.selection_set(children[0])
                self.tree.focus(children[0])
        except Exception as e:
            self.lbl_cont.config(text=f"Erro na pesquisa: {e}")

    def _confirmar_selecao(self):
        sel = self.tree.selection()
        if not sel:
            return "break"
        vals = self.tree.item(sel[0], "values")
        if vals and len(vals) >= 2:
            cod, desc = vals[0], vals[1]
            try:
                self.destroy()
            except Exception:
                pass
            self._callback(cod, desc)
        return "break"


class ConfiguracoesView(tk.Toplevel):
    """Janela de Configurações Gerais e Parâmetros do GeoAlvo."""

    def __init__(
        self,
        parent=None,
        connection=None,
        empresa_codigo: str = "001",
        tab_index: int = 0,
    ):
        super().__init__(parent)
        self.title("Parâmetros e Configurações Gerais - GeoAlvo")
        self.geometry("1080x660")
        self.minsize(900, 520)

        self._empresa_codigo = empresa_codigo
        self._centralizar_janela(1080, 660)
        self._aplicar_icone()

        self._conn = connection
        if self._conn is None:
            try:
                self._conn = obter_conexao_banco()
            except Exception as exc:
                pass

        self._repo = ConfiguracoesRepository(self._conn) if self._conn else None
        self._service = ConfiguracoesService(self._repo) if self._repo else None

        self._config_atual: Dict[str, Any] = {}

        self._configurar_estilos()
        self._criar_interface()
        self._carregar_configuracoes()

        if tab_index > 0 and hasattr(self, "notebook"):
            try:
                self.notebook.select(tab_index)
            except Exception:
                pass

        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<F2>", lambda e: self._salvar_configuracoes())

    def _centralizar_janela(self, largura: int, altura: int):
        from core import centralizar_janela
        centralizar_janela(self, getattr(self, "master", None), largura, altura)

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
        style.configure("Config.TLabel", font=("Segoe UI", 9))
        style.configure("ConfigHeader.TLabel", font=("Segoe UI", 9, "bold"), foreground="#1A365D")

    def _criar_interface(self):
        # 1. Header Banner Corporativo
        banner = tk.Frame(self, bg="#1A365D", height=58)
        banner.pack(side=tk.TOP, fill=tk.X)
        banner.pack_propagate(False)

        lbl_tit = tk.Label(
            banner,
            text="⚙ Parâmetros e Configurações do Sistema",
            font=("Segoe UI", 12, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
            anchor="w",
        )
        lbl_tit.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(8, 0))

        lbl_sub = tk.Label(
            banner,
            text="Diretórios do sistema, parâmetros de integração GeoApolo ↔ Alvo e configurações de rede",
            font=("Segoe UI", 8),
            bg="#1A365D",
            fg="#CBD5E0",
            anchor="w",
        )
        lbl_sub.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(1, 6))

        # 2. Notebook de Abas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=12, pady=8)

        # Aba 1: Caminhos
        self.tab_caminhos = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.tab_caminhos, text="📁 Pastas e Diretórios do Sistema")
        self._criar_aba_caminhos()

        # Aba 2: Integrações
        self.tab_integracoes = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.tab_integracoes, text="🔄 Regras de Integração & Entidades")
        self._criar_aba_integracoes()

        # Aba 3: Parâmetros de Estoque
        self.tab_estoque = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.tab_estoque, text="📦 Parâmetros de Estoque")
        self._criar_aba_estoque()

        # Aba 4: E-mails
        self.tab_email = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.tab_email, text="✉ Servidores de E-mail & Alertas")
        self._criar_aba_email()

        # Aba 5: Banco de Dados & Rede
        self.tab_banco = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.tab_banco, text="🗄 Servidores de Banco & Rede")
        self._criar_aba_banco()

        # Aba 6: API Alvo (Token & Validade)
        self.tab_alvo = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.tab_alvo, text="🌐 API Alvo (Token & Validade)")
        self._criar_aba_alvo()


        # 3. Rodapé
        bottom_frame = tk.Frame(self, bg="#E2E8F0", height=46, bd=1, relief=tk.GROOVE)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        bottom_frame.pack_propagate(False)

        btn_box = tk.Frame(bottom_frame, bg="#E2E8F0")
        btn_box.pack(side=tk.LEFT, padx=10, pady=7)

        ttk.Button(btn_box, text="💾 Salvar Configurações (F2)", command=self._salvar_configuracoes).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_box, text="🔄 Recarregar", command=self._carregar_configuracoes).pack(side=tk.LEFT, padx=4)

        btn_fechar = ttk.Button(bottom_frame, text="🚪 Fechar (Esc)", command=self.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=12, pady=7)

        self.lbl_status = tk.Label(
            bottom_frame,
            text=f"Empresa ativa: {self._empresa_codigo}",
            font=("Segoe UI", 9, "italic"),
            bg="#E2E8F0",
            fg="#4A5568",
        )
        self.lbl_status.pack(side=tk.RIGHT, padx=16)

    def _criar_campo_diretorio(self, parent, label_text: str, row: int):
        ttk.Label(parent, text=label_text, style="Config.TLabel").grid(row=row, column=0, sticky=tk.W, pady=6)
        entry = ttk.Entry(parent, width=65, font=("Segoe UI", 9))
        entry.grid(row=row, column=1, sticky=tk.W, padx=8, pady=6)
        btn = ttk.Button(parent, text="📂 Procurar", command=lambda e=entry: self._selecionar_pasta(e))
        btn.grid(row=row, column=2, padx=4, pady=6)
        return entry

    def _selecionar_pasta(self, entry: ttk.Entry):
        pasta = filedialog.askdirectory(title="Selecione a Pasta")
        if pasta:
            entry.delete(0, tk.END)
            entry.insert(0, os.path.normpath(pasta))

    def _criar_aba_caminhos(self):
        f = self.tab_caminhos
        self.edt_backup = self._criar_campo_diretorio(f, "Pasta de Backup do Sistema:", 0)
        self.edt_instalacao = self._criar_campo_diretorio(f, "Pasta de Instalação Local:", 1)
        self.edt_novas_versoes = self._criar_campo_diretorio(f, "Local de Novas Versões:", 2)
        self.edt_instalador = self._criar_campo_diretorio(f, "Local do Instalador de Versões:", 3)
        self.edt_docti = self._criar_campo_diretorio(f, "Documentação de TI:", 4)
        self.edt_inventario = self._criar_campo_diretorio(f, "Pasta de Inventário de TI:", 5)
        self.edt_convenio = self._criar_campo_diretorio(f, "Arquivos de Convênios:", 6)
        self.edt_alvo_loja = self._criar_campo_diretorio(f, "Base Alvo Loja:", 7)

    def _criar_aba_integracoes(self):
        f = self.tab_integracoes

        ttk.Label(f, text="Integração de Entidades com Alvo:", style="Config.TLabel").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.combo_integra = ttk.Combobox(f, values=["Integra", "Mescla", "Não Integra"], state="readonly", width=20)
        self.combo_integra.set("Integra")
        self.combo_integra.grid(row=0, column=1, sticky=tk.W, padx=8, pady=8)

        # 1. Consumidor Final
        ttk.Label(f, text="Código Consumidor Final:", style="Config.TLabel").grid(row=1, column=0, sticky=tk.W, pady=8)
        f_cf = ttk.Frame(f)
        f_cf.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=8, pady=8)

        self.edt_consumidor_final = ttk.Entry(f_cf, width=16, font=("Segoe UI", 9))
        self.edt_consumidor_final.pack(side=tk.LEFT)
        btn_busca_cf = ttk.Button(f_cf, text="🔍 Buscar", command=self._abrir_busca_consumidor_final, width=9)
        btn_busca_cf.pack(side=tk.LEFT, padx=(4, 8))
        self.lbl_consumidor_final_desc = ttk.Label(f_cf, text="", font=("Segoe UI", 9, "bold"), foreground="#1E3A8A")
        self.lbl_consumidor_final_desc.pack(side=tk.LEFT)

        # 2. Origem Padrão
        ttk.Label(f, text="Código Origem Padrão:", style="Config.TLabel").grid(row=2, column=0, sticky=tk.W, pady=8)
        f_orig = ttk.Frame(f)
        f_orig.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=8, pady=8)

        self.edt_origem_padrao = ttk.Entry(f_orig, width=16, font=("Segoe UI", 9))
        self.edt_origem_padrao.pack(side=tk.LEFT)
        btn_busca_orig = ttk.Button(f_orig, text="🔍 Buscar", command=self._abrir_busca_origem_padrao, width=9)
        btn_busca_orig.pack(side=tk.LEFT, padx=(4, 8))
        self.lbl_origem_padrao_desc = ttk.Label(f_orig, text="", font=("Segoe UI", 9, "bold"), foreground="#1E3A8A")
        self.lbl_origem_padrao_desc.pack(side=tk.LEFT)

        # 3. Motivo de Ocorrência Padrão
        ttk.Label(f, text="Código Motivo de Ocorrência Padrão:", style="Config.TLabel").grid(row=3, column=0, sticky=tk.W, pady=8)
        f_mot = ttk.Frame(f)
        f_mot.grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=8, pady=8)

        self.edt_motivo_ocorrencia = ttk.Entry(f_mot, width=16, font=("Segoe UI", 9))
        self.edt_motivo_ocorrencia.pack(side=tk.LEFT)
        btn_busca_mot = ttk.Button(f_mot, text="🔍 Buscar", command=self._abrir_busca_motivo_ocorrencia, width=9)
        btn_busca_mot.pack(side=tk.LEFT, padx=(4, 8))
        self.lbl_motivo_ocorrencia_desc = ttk.Label(f_mot, text="", font=("Segoe UI", 9, "bold"), foreground="#1E3A8A")
        self.lbl_motivo_ocorrencia_desc.pack(side=tk.LEFT)

        # 4. Categoria Parceira Padrão
        ttk.Label(f, text="Categoria Parceira Padrão:", style="Config.TLabel").grid(row=4, column=0, sticky=tk.W, pady=8)
        f_parc = ttk.Frame(f)
        f_parc.grid(row=4, column=1, columnspan=2, sticky=tk.W, padx=8, pady=8)

        self.edt_parceira = ttk.Entry(f_parc, width=16, font=("Segoe UI", 9))
        self.edt_parceira.pack(side=tk.LEFT)
        btn_busca_parc = ttk.Button(f_parc, text="🔍 Buscar", command=self._abrir_busca_categoria_parceira, width=9)
        btn_busca_parc.pack(side=tk.LEFT, padx=(4, 8))
        self.lbl_parceira_desc = ttk.Label(f_parc, text="", font=("Segoe UI", 9, "bold"), foreground="#1E3A8A")
        self.lbl_parceira_desc.pack(side=tk.LEFT)

        # Eventos para resolver nomes ao digitar código e sair
        self.edt_consumidor_final.bind("<FocusOut>", lambda e: self._atualizar_nome_consumidor_final())
        self.edt_consumidor_final.bind("<Return>", lambda e: self._atualizar_nome_consumidor_final())

        self.edt_origem_padrao.bind("<FocusOut>", lambda e: self._atualizar_nome_origem_padrao())
        self.edt_origem_padrao.bind("<Return>", lambda e: self._atualizar_nome_origem_padrao())

        self.edt_motivo_ocorrencia.bind("<FocusOut>", lambda e: self._atualizar_nome_motivo_ocorrencia())
        self.edt_motivo_ocorrencia.bind("<Return>", lambda e: self._atualizar_nome_motivo_ocorrencia())

        self.edt_parceira.bind("<FocusOut>", lambda e: self._atualizar_nome_categoria_parceira())
        self.edt_parceira.bind("<Return>", lambda e: self._atualizar_nome_categoria_parceira())

        # Seção de atalho para Token e Validade da API Alvo
        sep = ttk.Separator(f, orient=tk.HORIZONTAL)
        sep.grid(row=5, column=0, columnspan=3, sticky="ew", pady=15)

        ttk.Label(f, text="Web Service API Alvo (Token Permanente & Validade):", style="ConfigHeader.TLabel").grid(row=6, column=0, sticky=tk.W, pady=4)
        btn_alvo = ttk.Button(
            f,
            text="🔑 Configurar Token & Validade da API Alvo...",
            command=self._abrir_tela_token_alvo,
        )
        btn_alvo.grid(row=7, column=0, sticky=tk.W, pady=4)

    def _abrir_busca_consumidor_final(self):
        def _sel(cod, desc):
            self.edt_consumidor_final.delete(0, tk.END)
            self.edt_consumidor_final.insert(0, cod)
            self.lbl_consumidor_final_desc.config(text=desc)

        termo = self.edt_consumidor_final.get().strip()
        JanelaPesquisaParametro(
            self,
            titulo="Pesquisa de Entidade / Consumidor Final",
            col_codigo_nome="Código Entidade",
            col_descr_nome="Razão Social / Nome",
            buscar_func=lambda t: self._service.buscar_entidades(t) if self._service else [],
            callback_selecao=_sel,
            termo_inicial=termo,
        )

    def _atualizar_nome_consumidor_final(self):
        cod = self.edt_consumidor_final.get().strip()
        nome = self._service.obter_nome_entidade(cod) if (self._service and cod) else ""
        self.lbl_consumidor_final_desc.config(text=nome)

    def _abrir_busca_origem_padrao(self):
        def _sel(cod, desc):
            self.edt_origem_padrao.delete(0, tk.END)
            self.edt_origem_padrao.insert(0, cod)
            self.lbl_origem_padrao_desc.config(text=desc)

        modo = self.combo_integra.get()
        termo = self.edt_origem_padrao.get().strip()
        JanelaPesquisaParametro(
            self,
            titulo=f"Pesquisa de Origem Padrão ({modo})",
            col_codigo_nome="Código Estruturado",
            col_descr_nome="Nome da Origem",
            buscar_func=lambda t: self._service.buscar_origens(modo, t) if self._service else [],
            callback_selecao=_sel,
            termo_inicial=termo,
        )

    def _atualizar_nome_origem_padrao(self):
        cod = self.edt_origem_padrao.get().strip()
        modo = self.combo_integra.get()
        nome = self._service.obter_nome_origem(modo, cod) if (self._service and cod) else ""
        self.lbl_origem_padrao_desc.config(text=nome)

    def _abrir_busca_motivo_ocorrencia(self):
        def _sel(cod, desc):
            self.edt_motivo_ocorrencia.delete(0, tk.END)
            self.edt_motivo_ocorrencia.insert(0, cod)
            self.lbl_motivo_ocorrencia_desc.config(text=desc)

        modo = self.combo_integra.get()
        termo = self.edt_motivo_ocorrencia.get().strip()
        JanelaPesquisaParametro(
            self,
            titulo=f"Pesquisa de Motivo de Ocorrência ({modo})",
            col_codigo_nome="Código Motivo",
            col_descr_nome="Descrição da Ocorrência",
            buscar_func=lambda t: self._service.buscar_motivos_ocorrencia(modo, t) if self._service else [],
            callback_selecao=_sel,
            termo_inicial=termo,
        )

    def _atualizar_nome_motivo_ocorrencia(self):
        cod = self.edt_motivo_ocorrencia.get().strip()
        modo = self.combo_integra.get()
        nome = self._service.obter_nome_motivo_ocorrencia(modo, cod) if (self._service and cod) else ""
        self.lbl_motivo_ocorrencia_desc.config(text=nome)

    def _abrir_busca_categoria_parceira(self):
        def _sel(cod, desc):
            self.edt_parceira.delete(0, tk.END)
            self.edt_parceira.insert(0, cod)
            self.lbl_parceira_desc.config(text=desc)

        modo = self.combo_integra.get()
        termo = self.edt_parceira.get().strip()
        JanelaPesquisaParametro(
            self,
            titulo="Pesquisa de Categorias Parceiras",
            col_codigo_nome="Código Estruturado",
            col_descr_nome="Nome da Categoria",
            buscar_func=lambda t: self._service.buscar_categorias_parceiras(modo, t) if self._service else [],
            callback_selecao=_sel,
            termo_inicial=termo,
        )

    def _atualizar_nome_categoria_parceira(self):
        cod = self.edt_parceira.get().strip()
        modo = self.combo_integra.get()
        nome = self._service.obter_nome_categoria(modo, cod) if (self._service and cod) else ""
        self.lbl_parceira_desc.config(text=nome)

    def _criar_aba_estoque(self):
        """Aba de Configurações e Parâmetros do Módulo de Estoque."""
        f = ttk.LabelFrame(self.tab_estoque, text=" Políticas e Regras de Controle de Estoque ", padding=15)
        f.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(
            f,
            text="Parâmetros Gerais do Módulo de Estoque",
            font=("Segoe UI", 11, "bold"),
            foreground="#1A365D",
        ).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 15))

        # Permite Estoque Negativo
        ttk.Label(f, text="Permite Estoque Negativo:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=8)
        self.combo_permite_estq_negativo = ttk.Combobox(
            f,
            values=["Não", "Sim"],
            state="readonly",
            width=12,
            font=("Segoe UI", 9, "bold"),
        )
        self.combo_permite_estq_negativo.set("Não")
        self.combo_permite_estq_negativo.grid(row=1, column=1, sticky=tk.W, padx=8, pady=8)

        # Card informativo
        card = tk.Frame(f, bg="#EFF6FF", bd=1, relief=tk.SOLID, padx=12, pady=10)
        card.grid(row=2, column=0, columnspan=3, sticky="we", pady=(15, 10))

        ttk.Label(
            card,
            text="ℹ Regra de Negócio de Estoque Negativo:",
            font=("Segoe UI", 9, "bold"),
            foreground="#1E40AF",
            background="#EFF6FF",
        ).pack(anchor=tk.W, pady=(0, 4))

        msg_info = (
            "• Configurado como 'Não' (Padrão recomendado): O sistema impede e bloqueia o atendimento de requisições\n"
            "  e movimentações de saída direta caso o saldo disponível em estoque seja insuficiente ou nulo.\n"
            "• Configurado como 'Sim': Permite efetuar saídas e atendimentos mesmo que o saldo final do produto fique negativo."
        )
        ttk.Label(
            card,
            text=msg_info,
            font=("Segoe UI", 9),
            foreground="#1E3A8A",
            background="#EFF6FF",
            justify=tk.LEFT,
        ).pack(anchor=tk.W)


    def _criar_aba_email(self):
        f = self.tab_email

        ttk.Label(f, text="Servidor SMTP de Envio:", style="Config.TLabel").grid(row=0, column=0, sticky=tk.W, pady=6)
        self.edt_smtp_server = ttk.Entry(f, width=35, font=("Segoe UI", 9))
        self.edt_smtp_server.insert(0, "smtp.office365.com")
        self.edt_smtp_server.grid(row=0, column=1, sticky=tk.W, padx=8, pady=6)

        ttk.Label(f, text="Porta SMTP Envio:", style="Config.TLabel").grid(row=1, column=0, sticky=tk.W, pady=6)
        self.edt_smtp_porta = ttk.Entry(f, width=10, font=("Segoe UI", 9))
        self.edt_smtp_porta.insert(0, "587")
        self.edt_smtp_porta.grid(row=1, column=1, sticky=tk.W, padx=8, pady=6)

        ttk.Label(f, text="Servidor IMAP Recebimento:", style="Config.TLabel").grid(row=2, column=0, sticky=tk.W, pady=6)
        self.edt_imap_server = ttk.Entry(f, width=35, font=("Segoe UI", 9))
        self.edt_imap_server.insert(0, "outlook.office365.com")
        self.edt_imap_server.grid(row=2, column=1, sticky=tk.W, padx=8, pady=6)

        ttk.Label(f, text="Porta IMAP Recebimento:", style="Config.TLabel").grid(row=3, column=0, sticky=tk.W, pady=6)
        self.edt_imap_porta = ttk.Entry(f, width=10, font=("Segoe UI", 9))
        self.edt_imap_porta.insert(0, "993")
        self.edt_imap_porta.grid(row=3, column=1, sticky=tk.W, padx=8, pady=6)

        ttk.Label(
            f,
            text="Nota: As senhas e credenciais devem ser mantidas em segurança no Credential Manager do Windows.",
            font=("Segoe UI", 8, "italic"),
            foreground="#718096",
        ).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(15, 0))

    def _carregar_configuracoes(self):
        if not self._service:
            return
        try:
            self._config_atual = self._service.obter_parametros(self._empresa_codigo)

            def set_entry(entry, val):
                entry.delete(0, tk.END)
                entry.insert(0, str(val or ""))

            set_entry(self.edt_backup, self._config_atual.get("caminhobackupsistema"))
            set_entry(self.edt_instalacao, self._config_atual.get("instalacaolocal"))
            set_entry(self.edt_novas_versoes, self._config_atual.get("localnovasversoes"))
            set_entry(self.edt_instalador, self._config_atual.get("localinstaladorversoes"))
            set_entry(self.edt_docti, self._config_atual.get("caminhodocti"))
            set_entry(self.edt_inventario, self._config_atual.get("caminhoinventario"))
            set_entry(self.edt_convenio, self._config_atual.get("caminhoarquivoconvenio"))
            set_entry(self.edt_alvo_loja, self._config_atual.get("caminhobasealvoloja"))

            integra_val = self._config_atual.get("integra_entidades_apolo", "Integra")
            if integra_val in ["Integra", "Mescla", "Não Integra"]:
                self.combo_integra.set(integra_val)

            set_entry(self.edt_consumidor_final, self._config_atual.get("entcod_consumidorfinal"))
            set_entry(self.edt_origem_padrao, self._config_atual.get("origcodestr"))
            set_entry(self.edt_motivo_ocorrencia, self._config_atual.get("motocorcodestr"))
            set_entry(self.edt_parceira, self._config_atual.get("entcategparceira"))

            # Permite Estoque Negativo
            perm_neg = str(self._config_atual.get("permite_estoque_negativo", "Não")).strip()
            if perm_neg in ("Sim", "S", "1", "True", "true"):
                self.combo_permite_estq_negativo.set("Sim")
            else:
                self.combo_permite_estq_negativo.set("Não")

            # Atualiza descrições dos códigos carregados
            self._atualizar_nome_consumidor_final()
            self._atualizar_nome_origem_padrao()
            self._atualizar_nome_motivo_ocorrencia()
            self._atualizar_nome_categoria_parceira()

            # Carrega parâmetros de banco
            if self._service and hasattr(self, "edt_db_servidor"):
                db_cfg = self._service.obter_config_banco()
                self.combo_tipo_banco.set(db_cfg.tipo_banco)
                set_entry(self.edt_db_servidor, db_cfg.servidor)
                set_entry(self.edt_db_porta, str(db_cfg.porta))
                set_entry(self.edt_db_nome, db_cfg.banco)
                set_entry(self.edt_db_usuario, db_cfg.usuario)
                set_entry(self.edt_db_senha, db_cfg.senha)
                set_entry(self.edt_db_timeout, str(db_cfg.timeout))

            self.lbl_status.config(text=f"Configurações carregadas da empresa {self._empresa_codigo}.")
        except Exception as exc:
            logger.exception("Erro ao carregar configurações: %s", exc)
            messagebox.showerror("Erro", f"Erro ao carregar configurações:\n{exc}")

    def _criar_aba_banco(self):
        f = ttk.LabelFrame(self.tab_banco, text=" Servidor de Banco de Dados & Parâmetros de Rede ", padding=15)
        f.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(f, text="Tipo de Banco:", style="Config.TLabel").grid(row=0, column=0, sticky=tk.W, pady=6)
        self.combo_tipo_banco = ttk.Combobox(f, values=["MSSQL", "MySQL", "SQLite"], state="readonly", width=18)
        self.combo_tipo_banco.set("MSSQL")
        self.combo_tipo_banco.grid(row=0, column=1, sticky=tk.W, padx=8, pady=6)

        ttk.Label(f, text="Servidor / Host / IP:", style="Config.TLabel").grid(row=1, column=0, sticky=tk.W, pady=6)
        self.edt_db_servidor = ttk.Entry(f, width=32, font=("Segoe UI", 9))
        self.edt_db_servidor.insert(0, "localhost")
        self.edt_db_servidor.grid(row=1, column=1, sticky=tk.W, padx=8, pady=6)

        ttk.Label(f, text="Porta TCP:", style="Config.TLabel").grid(row=2, column=0, sticky=tk.W, pady=6)
        self.edt_db_porta = ttk.Entry(f, width=12, font=("Segoe UI", 9))
        self.edt_db_porta.insert(0, "1433")
        self.edt_db_porta.grid(row=2, column=1, sticky=tk.W, padx=8, pady=6)

        ttk.Label(f, text="Nome da Base (Database):", style="Config.TLabel").grid(row=3, column=0, sticky=tk.W, pady=6)
        self.edt_db_nome = ttk.Entry(f, width=32, font=("Segoe UI", 9))
        self.edt_db_nome.insert(0, "Apolo")
        self.edt_db_nome.grid(row=3, column=1, sticky=tk.W, padx=8, pady=6)

        ttk.Label(f, text="Usuário de Autenticação:", style="Config.TLabel").grid(row=4, column=0, sticky=tk.W, pady=6)
        self.edt_db_usuario = ttk.Entry(f, width=22, font=("Segoe UI", 9))
        self.edt_db_usuario.insert(0, "sa")
        self.edt_db_usuario.grid(row=4, column=1, sticky=tk.W, padx=8, pady=6)

        ttk.Label(f, text="Senha:", style="Config.TLabel").grid(row=5, column=0, sticky=tk.W, pady=6)
        self.edt_db_senha = ttk.Entry(f, width=22, font=("Segoe UI", 9), show="*")
        self.edt_db_senha.grid(row=5, column=1, sticky=tk.W, padx=8, pady=6)

        ttk.Label(f, text="Timeout (segundos):", style="Config.TLabel").grid(row=6, column=0, sticky=tk.W, pady=6)
        self.edt_db_timeout = ttk.Entry(f, width=10, font=("Segoe UI", 9))
        self.edt_db_timeout.insert(0, "15")
        self.edt_db_timeout.grid(row=6, column=1, sticky=tk.W, padx=8, pady=6)

        bar_banco = ttk.Frame(f)
        bar_banco.grid(row=7, column=0, columnspan=3, sticky=tk.W, pady=(16, 8))

        ttk.Button(bar_banco, text="⚡ Testar Conectividade", command=self._testar_conexao_banco).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(bar_banco, text="💾 Salvar Configurações de Banco", command=self._salvar_config_banco).pack(side=tk.LEFT, padx=8)

        self.lbl_db_resultado = ttk.Label(f, text="", font=("Segoe UI", 9, "bold"))
        self.lbl_db_resultado.grid(row=8, column=0, columnspan=3, sticky=tk.W, pady=6)

    def _testar_conexao_banco(self):
        if not self._service:
            return
        try:
            porta_val = int(self.edt_db_porta.get().strip() or 1433)
            timeout_val = int(self.edt_db_timeout.get().strip() or 15)
        except ValueError:
            messagebox.showerror("Erro", "Porta e Timeout devem ser números inteiros válidos.")
            return

        dto = ConfiguracaoBancoDTO(
            tipo_banco=self.combo_tipo_banco.get(),
            servidor=self.edt_db_servidor.get().strip(),
            porta=porta_val,
            banco=self.edt_db_nome.get().strip(),
            usuario=self.edt_db_usuario.get().strip(),
            senha=self.edt_db_senha.get().strip(),
            timeout=timeout_val,
        )

        res = self._service.testar_conexao_banco(dto)
        if res.sucesso:
            self.lbl_db_resultado.config(text=f"✔ {res.mensagem}", foreground="#2E7D32")
            messagebox.showinfo("Conexão Bem-Sucedida", res.mensagem)
        else:
            self.lbl_db_resultado.config(text=f"✖ {res.mensagem}", foreground="#C62828")
            messagebox.showerror("Falha na Conexão", res.mensagem)

    def _salvar_config_banco(self):
        if not self._service:
            return
        try:
            porta_val = int(self.edt_db_porta.get().strip() or 1433)
            timeout_val = int(self.edt_db_timeout.get().strip() or 15)
        except ValueError:
            messagebox.showerror("Erro", "Porta e Timeout devem ser números inteiros válidos.")
            return

        dto = ConfiguracaoBancoDTO(
            tipo_banco=self.combo_tipo_banco.get(),
            servidor=self.edt_db_servidor.get().strip(),
            porta=porta_val,
            banco=self.edt_db_nome.get().strip(),
            usuario=self.edt_db_usuario.get().strip(),
            senha=self.edt_db_senha.get().strip(),
            timeout=timeout_val,
        )

        res = self._service.salvar_config_banco(dto)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _salvar_configuracoes(self):
        if not self._service:
            return

        dados = {
            "caminhobackupsistema": self.edt_backup.get().strip(),
            "instalacaolocal": self.edt_instalacao.get().strip(),
            "localnovasversoes": self.edt_novas_versoes.get().strip(),
            "localinstaladorversoes": self.edt_instalador.get().strip(),
            "caminhodocti": self.edt_docti.get().strip(),
            "caminhoinventario": self.edt_inventario.get().strip(),
            "caminhoarquivoconvenio": self.edt_convenio.get().strip(),
            "caminhobasealvoloja": self.edt_alvo_loja.get().strip(),
            "integra_entidades_apolo": self.combo_integra.get(),
            "entcod_consumidorfinal": self.edt_consumidor_final.get().strip(),
            "origcodestr": self.edt_origem_padrao.get().strip(),
            "motocorcodestr": self.edt_motivo_ocorrencia.get().strip(),
            "entcategparceira": self.edt_parceira.get().strip(),
            "permite_estoque_negativo": self.combo_permite_estq_negativo.get().strip(),
        }

        res: ResultadoOperacao = self._service.salvar_parametros(dados, self._empresa_codigo)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self._carregar_configuracoes()
        else:
            messagebox.showerror("Erro ao Salvar", res.mensagem)

    def _abrir_tela_token_alvo(self):
        """Abre o formulário modal corporativo de configuração da API Alvo."""
        try:
            from configuracoes.alvo_api_view import abrir_configuracao_api_alvo
            abrir_configuracao_api_alvo(self, on_salvar_callback=self._atualizar_aba_alvo)
        except Exception as exc:
            messagebox.showerror("Erro", f"Erro ao abrir tela de configuração da API Alvo:\n{exc}", parent=self)

    def _criar_aba_alvo(self):
        """Constrói o painel de gerenciamento do Token e Vigência da API Alvo."""
        f = ttk.LabelFrame(self.tab_alvo, text=" Parâmetros de Autenticação Web Service Alvo (Riosoft) ", padding=15)
        f.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Status badge
        self.lbl_alvo_badge = tk.Label(
            f,
            text="...",
            font=("Segoe UI", 9, "bold"),
            relief=tk.RIDGE,
            padx=10,
            pady=4,
            bg="#EDF2F7",
            fg="#2D3748",
        )
        self.lbl_alvo_badge.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))

        # URL Base
        ttk.Label(f, text="URL Base Web Service:", style="Config.TLabel").grid(row=1, column=0, sticky=tk.W, pady=6)
        self.edt_alvo_url = ttk.Entry(f, width=50, font=("Segoe UI", 9))
        self.edt_alvo_url.grid(row=1, column=1, sticky=tk.W, padx=8, pady=6)

        # Período de Validade do Token
        ttk.Label(f, text="Validade Inicial (DD/MM/AAAA):", style="Config.TLabel").grid(row=2, column=0, sticky=tk.W, pady=6)
        self.edt_alvo_dt_ini = ttk.Entry(f, width=16, font=("Segoe UI", 9))
        self.edt_alvo_dt_ini.grid(row=2, column=1, sticky=tk.W, padx=8, pady=6)
        from configuracoes.alvo_api_view import _aplicar_mascara_data
        self.edt_alvo_dt_ini.bind("<KeyRelease>", lambda e: _aplicar_mascara_data(e, self.edt_alvo_dt_ini))

        ttk.Label(f, text="Validade Final (DD/MM/AAAA):", style="Config.TLabel").grid(row=3, column=0, sticky=tk.W, pady=6)
        self.edt_alvo_dt_fim = ttk.Entry(f, width=16, font=("Segoe UI", 9))
        self.edt_alvo_dt_fim.grid(row=3, column=1, sticky=tk.W, padx=8, pady=6)
        self.edt_alvo_dt_fim.bind("<KeyRelease>", lambda e: _aplicar_mascara_data(e, self.edt_alvo_dt_fim))

        # Token
        ttk.Label(f, text="Token de Integração:", style="Config.TLabel").grid(row=4, column=0, sticky=tk.NW, pady=6)
        self.txt_alvo_token = tk.Text(f, width=60, height=4, font=("Consolas", 8), wrap="char")
        self.txt_alvo_token.grid(row=4, column=1, sticky=tk.W, padx=8, pady=6)

        # Barra de Botões da Aba Alvo
        bar_alvo = ttk.Frame(f)
        bar_alvo.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(12, 8))

        ttk.Button(bar_alvo, text="⚡ Testar Comunicação & Token", command=self._testar_conexao_alvo_aba).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(bar_alvo, text="💾 Salvar Parâmetros Alvo", command=self._salvar_config_alvo_aba).pack(side=tk.LEFT, padx=8)
        ttk.Button(bar_alvo, text="🔍 Abrir Painel Completo do Token...", command=self._abrir_tela_token_alvo).pack(side=tk.LEFT, padx=8)

        self.lbl_alvo_resultado = ttk.Label(f, text="", font=("Segoe UI", 9, "bold"))
        self.lbl_alvo_resultado.grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=6)

        self._atualizar_aba_alvo()

    def _atualizar_aba_alvo(self, *args):
        """Recarrega os campos da aba Alvo a partir da configuração persistida."""
        try:
            from configuracoes.alvo_api_config import carregar_configuracao_alvo, validar_status_token
            cfg = carregar_configuracao_alvo()

            self.edt_alvo_url.delete(0, tk.END)
            self.edt_alvo_url.insert(0, cfg.base_url or "https://alvo.rccbrasil.org.br/api")

            self.edt_alvo_dt_ini.delete(0, tk.END)
            self.edt_alvo_dt_ini.insert(0, cfg.data_inicial or "")

            self.edt_alvo_dt_fim.delete(0, tk.END)
            self.edt_alvo_dt_fim.insert(0, cfg.data_final or "")

            self.txt_alvo_token.delete("1.0", tk.END)
            self.txt_alvo_token.insert("1.0", cfg.token or "")

            status, msg, valido = validar_status_token(cfg)
            if status == "ATIVO":
                self.lbl_alvo_badge.config(text=f"🟢 {msg}", bg="#DEF7EC", fg="#03543F")
            elif status == "EXPIRANDO":
                self.lbl_alvo_badge.config(text=f"🟡 {msg}", bg="#FEF08A", fg="#854D0E")
            elif status == "ATIVO_SEM_DATAS":
                self.lbl_alvo_badge.config(text=f"🟢 {msg}", bg="#DEF7EC", fg="#03543F")
            elif status == "EXPIRADO":
                self.lbl_alvo_badge.config(text=f"🔴 {msg}", bg="#FDE8E8", fg="#9B1C1C")
            elif status == "FUTURO":
                self.lbl_alvo_badge.config(text=f"🔵 {msg}", bg="#E1EFFE", fg="#1E429F")
            else:
                self.lbl_alvo_badge.config(text=f"⚪ {msg}", bg="#EDF2F7", fg="#4A5568")
        except Exception:
            pass

    def _salvar_config_alvo_aba(self):
        """Salva a configuração da API Alvo diretamente da aba."""
        try:
            from configuracoes.alvo_api_config import AlvoAPIConfig, salvar_configuracao_alvo, carregar_configuracao_alvo
            atual = carregar_configuracao_alvo()
            cfg = AlvoAPIConfig(
                token=self.txt_alvo_token.get("1.0", tk.END).strip(),
                data_inicial=self.edt_alvo_dt_ini.get().strip(),
                data_final=self.edt_alvo_dt_fim.get().strip(),
                base_url=self.edt_alvo_url.get().strip() or "https://alvo.rccbrasil.org.br/api",
                timeout=atual.timeout,
                ativo=atual.ativo,
                ambiente=atual.ambiente,
                usuario_padrao=atual.usuario_padrao,
            )
            salvar_configuracao_alvo(cfg)
            self._atualizar_aba_alvo()
            messagebox.showinfo("Sucesso", "Configurações da API Alvo salvas com sucesso!", parent=self)
        except Exception as exc:
            messagebox.showerror("Erro", f"Erro ao salvar configurações da API Alvo:\n{exc}", parent=self)

    def _testar_conexao_alvo_aba(self):
        """Executa teste de conexão e validação do token na aba."""
        try:
            from configuracoes.alvo_api_config import AlvoAPIConfig, testar_comunicacao_alvo
            cfg = AlvoAPIConfig(
                token=self.txt_alvo_token.get("1.0", tk.END).strip(),
                base_url=self.edt_alvo_url.get().strip() or "https://alvo.rccbrasil.org.br/api",
            )
            sucesso, msg, _ = testar_comunicacao_alvo(cfg)
            if sucesso:
                self.lbl_alvo_resultado.config(text="✔ Comunicação com a API Alvo bem-sucedida!", foreground="#2E7D32")
                messagebox.showinfo("Teste de Comunicação Alvo", msg, parent=self)
            else:
                self.lbl_alvo_resultado.config(text="✖ Falha na comunicação com a API Alvo", foreground="#C62828")
                messagebox.showerror("Teste de Comunicação Alvo", msg, parent=self)
        except Exception as exc:
            messagebox.showerror("Erro", f"Exceção durante teste:\n{exc}", parent=self)

