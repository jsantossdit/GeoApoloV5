"""
Interface Gráfica (Tkinter / ttk) para Manutenção de Ativo Imobilizado e Depreciação.
Layout corporativo profissional no padrão visual GeoAlvo (#1A365D).
"""

import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from typing import List, Dict, Any, Optional

from core import (
    centralizar_janela,
    vincular_maiusculo,
    configurar_navegacao_enter,
    habilitar_filtro_dinamico_combobox,
)
from ativo_imobilizado.models import ResultadoOperacaoAtivo
from ativo_imobilizado.repository import AtivoImobilizadoRepository
from ativo_imobilizado.service import AtivoImobilizadoService
from entidades.database import obter_conexao_banco

logger = logging.getLogger(__name__)


class AtivoImobilizadoView(tk.Toplevel):
    """Janela de Gestão de Bens de Ativo Fixo Imobilizado e Depreciação."""

    def __init__(self, parent=None, connection=None, empresa_codigo="001"):
        super().__init__(parent)
        self.title("Gestão de Ativo Imobilizado & Depreciação Contábil - GeoAlvo")
        self.geometry("1120x720")
        self.minsize(940, 620)

        self._centralizar_janela(1120, 720)
        self._aplicar_icone()

        self._empresa_codigo = empresa_codigo
        self._modo_inclusao = True

        self._conn = connection
        if self._conn is None:
            try:
                self._conn = obter_conexao_banco()
            except Exception as exc:
                logger.warning("Falha ao obter conexão padrão com banco: %s", exc)

        self._repo = AtivoImobilizadoRepository(self._conn) if self._conn else None
        self._service = AtivoImobilizadoService(self._repo) if self._repo else None

        self._bens_cache: List[Dict[str, Any]] = []

        self._parent = parent
        if parent:
            try:
                self.transient(parent)
            except Exception:
                pass
        try:
            self.grab_set()
        except Exception:
            pass

        self._configurar_estilos()
        self._criar_interface()
        self._carregar_combos()
        self._novo_registro()
        self._carregar_grid()

        self.protocol("WM_DELETE_WINDOW", self._fechar)
        self.bind("<Escape>", lambda e: self._fechar())
        self.bind("<F5>", lambda e: self._carregar_grid())

    def _fechar(self):
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()

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
        style.configure(
            "Ativo.Treeview",
            font=("Segoe UI", 9),
            rowheight=26,
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
        )
        style.configure(
            "Ativo.Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            foreground="#1A365D",
            padding=5,
        )

    def _criar_interface(self):
        # 1. Banner Superior
        banner = tk.Frame(self, bg="#1A365D", height=58)
        banner.pack(side=tk.TOP, fill=tk.X)
        banner.pack_propagate(False)

        lbl_tit = tk.Label(
            banner,
            text="🏢 Gestão de Ativo Imobilizado & Depreciação",
            font=("Segoe UI", 12, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
            anchor="w",
        )
        lbl_tit.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(8, 0))

        lbl_sub = tk.Label(
            banner,
            text="Manutenção de patrimônio, classificação contábil, localização física e cálculo em linha reta",
            font=("Segoe UI", 8),
            bg="#1A365D",
            fg="#CBD5E0",
            anchor="w",
        )
        lbl_sub.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(1, 6))

        # 2. Barra de Ferramentas / Ações
        tb = tk.Frame(self, bg="#F0F4F8", height=42, relief=tk.RAISED, bd=1)
        tb.pack(side=tk.TOP, fill=tk.X)

        btn_salvar = ttk.Button(tb, text="💾 Salvar (F2)", command=self._salvar)
        btn_salvar.pack(side=tk.LEFT, padx=6, pady=6)

        btn_limpar = ttk.Button(tb, text="📄 Novo / Limpar", command=self._novo_registro)
        btn_limpar.pack(side=tk.LEFT, padx=4, pady=6)

        btn_excluir = ttk.Button(tb, text="🗑 Excluir", command=self._excluir)
        btn_excluir.pack(side=tk.LEFT, padx=4, pady=6)

        btn_deprec = ttk.Button(tb, text="⚡ Calcular Depreciação", command=self._calcular_depreciacao_form)
        btn_deprec.pack(side=tk.LEFT, padx=4, pady=6)

        btn_refresh = ttk.Button(tb, text="🔄 Atualizar (F5)", command=self._carregar_grid)
        btn_refresh.pack(side=tk.LEFT, padx=4, pady=6)

        btn_fechar = ttk.Button(tb, text="🚪 Fechar", command=self._fechar)
        btn_fechar.pack(side=tk.LEFT, padx=4, pady=6)

        self.lbl_modo = tk.Label(tb, text="MODO: INCLUSÃO", font=("Segoe UI", 9, "bold"), fg="#2B6CB0", bg="#F0F4F8")
        self.lbl_modo.pack(side=tk.RIGHT, padx=16)

        # 3. Notebook / Abas de Dados
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=False, padx=12, pady=8)

        tab_cad = ttk.Frame(self.notebook, padding=10)
        tab_dep = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(tab_cad, text="📋 Identificação & Cadastro")
        self.notebook.add(tab_dep, text="📈 Depreciação & Valores Contábeis")

        # ── ABA 1: Identificação & Cadastro ──
        f_id = ttk.LabelFrame(tab_cad, text="Identificação Patrimonial", padding=8)
        f_id.pack(side=tk.TOP, fill=tk.X, pady=(0, 6))

        # Linha 1: Código do Bem, Empresa, Plaqueta / Barras, Nº de Série
        r1 = ttk.Frame(f_id)
        r1.pack(fill=tk.X, pady=3)

        ttk.Label(r1, text="Nº do Bem:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_cod_bem = tk.StringVar()
        vincular_maiusculo(self.var_cod_bem)
        self.txt_cod_bem = ttk.Entry(r1, textvariable=self.var_cod_bem, width=12, font=("Segoe UI", 9, "bold"))
        self.txt_cod_bem.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(r1, text="Empresa:").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_empresa = ttk.Combobox(r1, state="readonly", width=22)
        self.combo_empresa.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(r1, text="Plaqueta / Cód. Barras:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_plaqueta = tk.StringVar()
        vincular_maiusculo(self.var_plaqueta)
        self.txt_plaqueta = ttk.Entry(r1, textvariable=self.var_plaqueta, width=16)
        self.txt_plaqueta.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(r1, text="Nº de Série:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_serie = tk.StringVar()
        vincular_maiusculo(self.var_serie)
        self.txt_serie = ttk.Entry(r1, textvariable=self.var_serie, width=16)
        self.txt_serie.pack(side=tk.LEFT)

        # Linha 2: Descrição do Bem
        r2 = ttk.Frame(f_id)
        r2.pack(fill=tk.X, pady=3)

        ttk.Label(r2, text="Descrição do Bem:*").pack(side=tk.LEFT, padx=(0, 4))
        self.var_descricao = tk.StringVar()
        vincular_maiusculo(self.var_descricao)
        self.txt_descricao = ttk.Entry(r2, textvariable=self.var_descricao, font=("Segoe UI", 9))
        self.txt_descricao.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Classificação e Estrutura Organizacional
        f_org = ttk.LabelFrame(tab_cad, text="Classificação, Localização & Dados de Entrada", padding=10)
        f_org.pack(side=tk.TOP, fill=tk.X, pady=4)

        r3 = ttk.Frame(f_org)
        r3.pack(fill=tk.X, pady=3)

        ttk.Label(r3, text="Centro de Custo:*").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_cctrl = ttk.Combobox(r3, state="readonly", width=30)
        self.combo_cctrl.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(r3, text="Categoria do Bem:*").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_categoria = ttk.Combobox(r3, state="readonly", width=28)
        self.combo_categoria.pack(side=tk.LEFT, padx=(0, 15))
        self.combo_categoria.bind("<<ComboboxSelected>>", lambda e: self._on_categoria_alterada())

        ttk.Label(r3, text="Classificação:*").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_classif = ttk.Combobox(
            r3,
            state="readonly",
            width=25,
            postcommand=self._garantir_classificacoes_carregadas,
        )
        self.combo_classif.pack(side=tk.LEFT)
        self.combo_classif.bind("<F4>", lambda e: self._abrir_cadastro_classificacao())
        self.combo_classif.bind("<Button-1>", lambda e: self._garantir_classificacoes_carregadas(), add="+")
        self.combo_classif.bind("<FocusIn>", lambda e: self._garantir_classificacoes_carregadas(), add="+")

        btn_add_classif = ttk.Button(
            r3,
            text="+",
            width=3,
            command=self._abrir_cadastro_classificacao,
        )
        btn_add_classif.pack(side=tk.LEFT, padx=(3, 0))

        r4 = ttk.Frame(f_org)
        r4.pack(fill=tk.X, pady=3)

        ttk.Label(r4, text="Localização Física:*").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_local = ttk.Combobox(r4, state="readonly", width=30)
        self.combo_local.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(r4, text="Responsável:").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_func = ttk.Combobox(r4, state="readonly", width=28)
        self.combo_func.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(r4, text="Marca do Produto:").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_marca = ttk.Combobox(r4, state="normal", width=22)
        self.combo_marca.pack(side=tk.LEFT)
        self.combo_marca.bind("<F4>", lambda e: self._cadastrar_marca_manual())
        self.combo_marca.bind("<FocusOut>", self._ao_confirmar_marca, add="+")

        btn_add_marca = ttk.Button(
            r4,
            text="+",
            width=3,
            command=self._cadastrar_marca_manual,
        )
        btn_add_marca.pack(side=tk.LEFT, padx=(3, 0))

        # Linha 5: Status à esquerda, Quantidade, Vl. Compra Unitário, Vl. Total e Data de Aquisição
        r5 = ttk.Frame(f_org)
        r5.pack(fill=tk.X, pady=(6, 3))

        ttk.Label(r5, text="Status do Bem:*").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_status = ttk.Combobox(r5, state="readonly", width=14)
        self.combo_status.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(r5, text="Quantidade:*").pack(side=tk.LEFT, padx=(0, 4))
        self.var_quantidade = tk.StringVar(value="1,00")
        self.txt_quantidade = ttk.Entry(r5, textvariable=self.var_quantidade, width=8)
        self.txt_quantidade.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(r5, text="Vl. Compra Unit. (R$):*").pack(side=tk.LEFT, padx=(0, 4))
        self.var_val_compra = tk.StringVar(value="0,00")
        self.txt_val_compra = ttk.Entry(r5, textvariable=self.var_val_compra, width=13)
        self.txt_val_compra.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(r5, text="Vl. Total (R$):").pack(side=tk.LEFT, padx=(0, 4))
        self.var_val_total = tk.StringVar(value="0,00")
        self.txt_val_total = ttk.Entry(r5, textvariable=self.var_val_total, width=13)
        self.txt_val_total.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(r5, text="Data Aquisição:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_dt_aquisicao = tk.StringVar()
        self.txt_dt_aquisicao = ttk.Entry(r5, textvariable=self.var_dt_aquisicao, width=12)
        self.txt_dt_aquisicao.pack(side=tk.LEFT)

        # Traces para cálculo em tempo real: Vl. Total = Quantidade * Vl. Compra
        self.var_quantidade.trace_add("write", self._ao_alterar_valores)
        self.var_val_compra.trace_add("write", self._ao_alterar_valores)
        self.var_val_total.trace_add("write", self._ao_alterar_val_total)

        # ── ABA 2: Depreciação & Valores Contábeis ──
        f_dep_vals = ttk.LabelFrame(tab_dep, text="Taxas e Histórico de Revisão", padding=8)
        f_dep_vals.pack(side=tk.TOP, fill=tk.X, pady=(0, 6))

        rd1 = ttk.Frame(f_dep_vals)
        rd1.pack(fill=tk.X, pady=3)

        ttk.Label(rd1, text="Taxa Dep. Anual (%):*").pack(side=tk.LEFT, padx=(0, 4))
        self.var_taxa_dep = tk.StringVar(value="10,00")
        self.txt_taxa_dep = ttk.Entry(rd1, textvariable=self.var_taxa_dep, width=10)
        self.txt_taxa_dep.pack(side=tk.LEFT, padx=(0, 20))
        self.txt_taxa_dep.bind("<KeyRelease>", lambda e: self._calcular_depreciacao_form(silencioso=True))

        ttk.Label(rd1, text="Última Revisão (DD/MM/AAAA):").pack(side=tk.LEFT, padx=(0, 4))
        self.var_dt_revisao = tk.StringVar()
        self.txt_dt_revisao = ttk.Entry(rd1, textvariable=self.var_dt_revisao, width=14)
        self.txt_dt_revisao.pack(side=tk.LEFT, padx=(0, 20))

        btn_recalc = ttk.Button(rd1, text="📊 Recalcular Valores", command=lambda: self._calcular_depreciacao_form(silencioso=False))
        btn_recalc.pack(side=tk.LEFT)

        # Painel Informativo de Depreciação Calculada (Cards)
        f_card = tk.Frame(tab_dep, bg="#EBF8FF", bd=1, relief=tk.SOLID, padx=12, pady=10)
        f_card.pack(side=tk.TOP, fill=tk.X, pady=6)

        self.lbl_anos_uso = tk.Label(
            f_card, text="Tempo em Uso: - anos", font=("Segoe UI", 10, "bold"), bg="#EBF8FF", fg="#2C5282"
        )
        self.lbl_anos_uso.pack(side=tk.LEFT, padx=15)

        self.lbl_dep_acumulada = tk.Label(
            f_card, text="Dep. Acumulada: R$ 0,00", font=("Segoe UI", 10, "bold"), bg="#EBF8FF", fg="#C53030"
        )
        self.lbl_dep_acumulada.pack(side=tk.LEFT, padx=25)

        self.lbl_val_atual = tk.Label(
            f_card, text="Valor Atual Estimado: R$ 0,00", font=("Segoe UI", 10, "bold"), bg="#EBF8FF", fg="#22543D"
        )
        self.lbl_val_atual.pack(side=tk.LEFT, padx=25)

        # Foto e Observações
        f_obs = ttk.LabelFrame(tab_dep, text="Complementos e Imagem", padding=8)
        f_obs.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=4)

        ro1 = ttk.Frame(f_obs)
        ro1.pack(fill=tk.X, pady=3)

        ttk.Label(ro1, text="Caminho da Foto:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_foto = tk.StringVar()
        vincular_maiusculo(self.var_foto)
        self.txt_foto = ttk.Entry(ro1, textvariable=self.var_foto)
        self.txt_foto.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        btn_foto = ttk.Button(ro1, text="📂 Procurar...", command=self._procurar_foto)
        btn_foto.pack(side=tk.LEFT)

        ttk.Label(f_obs, text="Observações Gerais:").pack(anchor="w", pady=(4, 2))
        self.txt_obs = tk.Text(f_obs, height=3, font=("Segoe UI", 9))
        self.txt_obs.pack(fill=tk.BOTH, expand=True)

        # 4. Grid de Bens Cadastrados
        f_grid = ttk.LabelFrame(self, text="Bens de Ativo Imobilizado Cadastrados", padding=8)
        f_grid.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))

        f_busca = ttk.Frame(f_grid)
        f_busca.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(f_busca, text="🔍 Filtrar por Descrição / Código:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_busca = tk.StringVar()
        vincular_maiusculo(self.var_busca)
        self.txt_busca = ttk.Entry(f_busca, textvariable=self.var_busca, width=32)
        self.txt_busca.pack(side=tk.LEFT, padx=(0, 8))
        self.txt_busca.bind("<KeyRelease>", lambda e: self._filtrar_grid())

        cols = ("bem", "descricao", "categoria", "classificacao", "local", "resp", "marca", "qtd", "compra", "total", "atual", "status")
        scroll_y = ttk.Scrollbar(f_grid, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(f_grid, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(
            f_grid,
            columns=cols,
            show="headings",
            selectmode="browse",
            style="Ativo.Treeview",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
        )
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        self.tree.heading("bem", text="Nº Bem")
        self.tree.heading("descricao", text="Descrição do Bem")
        self.tree.heading("categoria", text="Categoria")
        self.tree.heading("classificacao", text="Classificação")
        self.tree.heading("local", text="Localização")
        self.tree.heading("resp", text="Responsável")
        self.tree.heading("marca", text="Marca")
        self.tree.heading("qtd", text="Qtd")
        self.tree.heading("compra", text="Vl. Unit (R$)")
        self.tree.heading("total", text="Vl. Total (R$)")
        self.tree.heading("atual", text="Vl. Atual (R$)")
        self.tree.heading("status", text="Status")

        self.tree.column("bem", width=65, anchor=tk.CENTER)
        self.tree.column("descricao", width=190, anchor=tk.W)
        self.tree.column("categoria", width=110, anchor=tk.W)
        self.tree.column("classificacao", width=110, anchor=tk.W)
        self.tree.column("local", width=110, anchor=tk.W)
        self.tree.column("resp", width=100, anchor=tk.W)
        self.tree.column("marca", width=90, anchor=tk.W)
        self.tree.column("qtd", width=55, anchor=tk.E)
        self.tree.column("compra", width=90, anchor=tk.E)
        self.tree.column("total", width=95, anchor=tk.E)
        self.tree.column("atual", width=95, anchor=tk.E)
        self.tree.column("status", width=80, anchor=tk.CENTER)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.bind("<Double-1>", lambda e: self._carregar_registro_selecionado())
        self.tree.bind("<Delete>", lambda e: self._excluir())

        # Padronização de campos em caixa alta (maiúsculo)
        for w in (
            self.txt_cod_bem,
            self.txt_plaqueta,
            self.txt_serie,
            self.txt_descricao,
            self.txt_dt_aquisicao,
            self.txt_val_compra,
            self.txt_val_total,
            self.txt_taxa_dep,
            self.txt_dt_revisao,
            self.txt_foto,
            self.txt_busca,
            self.combo_marca,
        ):
            vincular_maiusculo(w)

        # Configurar navegação contínua com a tecla Enter (estilo ERP)
        ordem_campos = [
            self.txt_cod_bem,
            self.combo_empresa,
            self.txt_plaqueta,
            self.txt_serie,
            self.txt_descricao,
            self.combo_cctrl,
            self.combo_categoria,
            self.combo_classif,
            self.combo_local,
            self.combo_func,
            self.combo_marca,
            self.combo_status,
            self.txt_quantidade,
            self.txt_val_compra,
            self.txt_val_total,
            self.txt_dt_aquisicao,
            self.txt_taxa_dep,
            self.txt_dt_revisao,
            self.txt_foto,
        ]
        configurar_navegacao_enter(ordem_campos)

        # Ao dar Enter na combo de marcas: resolve o código imediatamente para a tela e avança
        def _ao_enter_marca(event=None):
            self._ao_confirmar_marca()
            try:
                self.combo_status.focus_set()
            except Exception:
                pass
            return "break"

        self.combo_marca.bind("<Return>", _ao_enter_marca)
        self.combo_marca.bind("<KP_Enter>", _ao_enter_marca)

        # Transição suave entre abas via Enter: ao sair de txt_dt_aquisicao avança para aba de Depreciação
        def _ao_enter_dt_aquisicao(event=None):
            try:
                self.notebook.select(1)
                self.txt_taxa_dep.focus_set()
            except Exception:
                pass
            return "break"

        self.txt_dt_aquisicao.bind("<Return>", _ao_enter_dt_aquisicao)
        self.txt_dt_aquisicao.bind("<KP_Enter>", _ao_enter_dt_aquisicao)

        # Enter no campo de busca dispara filtragem do grid
        self.txt_busca.bind("<Return>", lambda e: self._filtrar_grid())
        self.txt_busca.bind("<KP_Enter>", lambda e: self._filtrar_grid())

    # ── Métodos de Carregamento ──────────────────────────────────────────

    def _carregar_combos(self):
        if not self._service:
            return

        try:
            # Preserva seleções atuais se houver
            sel_emp = self.combo_empresa.get()
            sel_cctrl = self.combo_cctrl.get()
            sel_cat = self.combo_categoria.get()
            sel_classif = self.combo_classif.get()
            sel_loc = self.combo_local.get()
            sel_func = self.combo_func.get()
            sel_marca = self.combo_marca.get()
            sel_status = self.combo_status.get()

            # 1. Empresas
            emps = self._service.obter_empresas()
            self._map_emp = {f"{e['codigo']} - {e['descricao']}": e['codigo'] for e in emps}
            self.combo_empresa["values"] = list(self._map_emp.keys())
            if sel_emp in self.combo_empresa["values"]:
                self.combo_empresa.set(sel_emp)
            elif self.combo_empresa["values"]:
                self.combo_empresa.current(0)

            # 2. Centros de Custo
            cctrls = self._service.obter_centros_controle()
            self._map_cctrl = {f"{c['codigo']} - {c['descricao']}": c['codigo'] for c in cctrls}
            self.combo_cctrl["values"] = list(self._map_cctrl.keys())
            if sel_cctrl in self.combo_cctrl["values"]:
                self.combo_cctrl.set(sel_cctrl)

            # 3. Categorias
            categs = self._service.obter_categorias()
            self._map_categ = {f"{c['codigo']} - {c['descricao']}": c['codigo'] for c in categs}
            self.combo_categoria["values"] = list(self._map_categ.keys())
            if sel_cat in self.combo_categoria["values"]:
                self.combo_categoria.set(sel_cat)

            # 3.1 Classificações (Carrega filtrado pela categoria atual, ou todas se vazio)
            cat_cod = self._map_categ.get(self.combo_categoria.get(), "")
            self._recarregar_combo_classificacoes(cat_cod)
            if sel_classif in self.combo_classif["values"]:
                self.combo_classif.set(sel_classif)

            # 4. Localizações
            locs = self._service.obter_localizacoes()
            self._map_local = {f"{l['codigo']} - {l['descricao']}": l['codigo'] for l in locs}
            self.combo_local["values"] = list(self._map_local.keys())
            if sel_loc in self.combo_local["values"]:
                self.combo_local.set(sel_loc)

            # 5. Funcionários
            funcs = self._service.obter_funcionarios()
            self._map_func = {f"{f['codigo']} - {f['descricao']}": f['codigo'] for f in funcs}
            self.combo_func["values"] = list(self._map_func.keys())
            if sel_func in self.combo_func["values"]:
                self.combo_func.set(sel_func)

            # 6. Marcas
            self._recarregar_combo_marcas()
            if sel_marca in self.combo_marca["values"]:
                self.combo_marca.set(sel_marca)

            # 7. Status
            status_list = self._service.obter_status()
            self._map_status = {f"{s['codigo']} - {s['descricao']}": str(s['codigo']) for s in status_list}
            if not self._map_status:
                self._map_status = {"1 - ATIVO": "1", "2 - BAIXADO": "2"}
            self.combo_status["values"] = list(self._map_status.keys())
            if sel_status in self.combo_status["values"]:
                self.combo_status.set(sel_status)
            elif "1 - ATIVO" in self.combo_status["values"]:
                self.combo_status.set("1 - ATIVO")
        except Exception as exc:
            logger.exception("Erro ao carregar combos de ativo imobilizado: %s", exc)

    def _recarregar_combo_marcas(self, codigo_selecionar: Optional[str] = None):
        if not self._service:
            return
        try:
            marcas = self._service.obter_marcas()
            self._map_marca = {f"{m['codigo']} - {m['descricao']}": str(m['codigo']) for m in marcas}
            opcoes = list(self._map_marca.keys())
            if hasattr(self.combo_marca, "atualizar_valores_filtro"):
                self.combo_marca.atualizar_valores_filtro(opcoes)
            else:
                habilitar_filtro_dinamico_combobox(self.combo_marca, opcoes)

            if codigo_selecionar is not None:
                self._selecionar_combo_por_codigo(self.combo_marca, self._map_marca, str(codigo_selecionar))
        except Exception as exc:
            logger.exception("Erro ao recarregar marcas: %s", exc)

    def _cadastrar_marca_manual(self):
        sugestao = self.combo_marca.get().strip()
        if " - " in sugestao:
            sugestao = ""
        descricao = simpledialog.askstring(
            "Cadastrar Nova Marca",
            "Informe a descrição da nova marca:",
            initialvalue=sugestao,
            parent=self,
        )
        if not descricao or not descricao.strip():
            return
        try:
            novo_cod, desc_salva, criada = self._service.obter_ou_criar_marca(descricao)
            self._recarregar_combo_marcas(codigo_selecionar=str(novo_cod))
            msg = (
                f"Marca '{desc_salva}' cadastrada com sucesso sob o código {novo_cod}!"
                if criada
                else f"Marca '{desc_salva}' já existia com o código {novo_cod}."
            )
            messagebox.showinfo("Marca de Produto", msg, parent=self)
        except Exception as exc:
            logger.exception("Erro ao cadastrar marca: %s", exc)
            messagebox.showerror("Erro ao Cadastrar Marca", f"Falha ao cadastrar marca:\n{exc}", parent=self)

    def _resolver_marca_digitada(self) -> Optional[str]:
        """
        Analisa o conteúdo digitado ou selecionado no combo de marcas.
        - Se vazio: retorna "".
        - Se for opção existente ("COD - NOME"), retorna o COD.
        - Se for apenas o código numérico, localiza e seleciona a marca.
        - Se corresponder à descrição de marca existente, seleciona e retorna o código.
        - Se for nova marca inexistente: pergunta ao usuário se deseja cadastrá-la.
          Em caso afirmativo, cadastra no banco, atualiza o combo e retorna o novo código.
          Em caso negativo, retorna None para abortar a gravação.
        """
        texto = self.combo_marca.get().strip().upper()
        if not texto:
            return ""

        mapa = getattr(self, "_map_marca", {})
        # 1. Match direto no mapa de rótulos
        if texto in mapa:
            return str(mapa[texto])

        # 2. Match por formato "COD - DESC" ou código/descrição exata
        for rotulo, cod in mapa.items():
            if " - " in rotulo:
                parte_cod, parte_desc = rotulo.split(" - ", 1)
                if texto == parte_cod.strip() or texto == parte_desc.strip().upper():
                    self.combo_marca.set(rotulo)
                    return str(cod)
            if str(cod).strip() == texto:
                self.combo_marca.set(rotulo)
                return str(cod)

        # 3. Marca não cadastrada: perguntar ao usuário
        confirmar = messagebox.askyesno(
            "Cadastrar Nova Marca",
            f"A marca '{texto}' não consta no cadastro de marcas.\n\nDeseja cadastrá-la agora no sistema?",
            parent=self,
        )
        if not confirmar:
            return None

        try:
            novo_cod, desc_salva, _ = self._service.obter_ou_criar_marca(texto)
            self._recarregar_combo_marcas(codigo_selecionar=str(novo_cod))
            return str(novo_cod)
        except Exception as exc:
            logger.exception("Erro ao cadastrar marca automaticamente: %s", exc)
            messagebox.showerror("Erro ao Cadastrar Marca", f"Não foi possível cadastrar a nova marca:\n{exc}", parent=self)
            return None

    def _ao_confirmar_marca(self, event=None):
        """Ao digitar código da marca, localiza imediatamente no mapa e preenche o rótulo formatado na tela."""
        texto = self.combo_marca.get().strip().upper()
        if not texto:
            return
        mapa = getattr(self, "_map_marca", {})
        if texto in mapa:
            return

        # 1. Match por código numérico exato
        for rotulo, cod in mapa.items():
            if str(cod).strip() == texto or (texto.isdigit() and str(cod).strip().isdigit() and int(str(cod)) == int(texto)):
                self.combo_marca.set(rotulo)
                return

        # 2. Match por descrição exata
        for rotulo, cod in mapa.items():
            if " - " in rotulo:
                _, desc = rotulo.split(" - ", 1)
                if desc.strip().upper() == texto:
                    self.combo_marca.set(rotulo)
                    return

        # 3. Se houver apenas 1 resultado parcial no mapa, seleciona
        candidatos = [rotulo for rotulo in mapa.keys() if texto in rotulo.upper()]
        if len(candidatos) == 1:
            self.combo_marca.set(candidatos[0])

    def _garantir_classificacoes_carregadas(self, event=None):
        """Assegura que a combo de classificação esteja populada com registros ao ser clicada."""
        cat_key = self.combo_categoria.get()
        cat_cod = getattr(self, "_map_categ", {}).get(cat_key, "")
        self._recarregar_combo_classificacoes(cat_cod)
        if not self.combo_classif["values"]:
            self._recarregar_combo_classificacoes("")

    def _ao_alterar_valores(self, *args):
        """Calcula automaticamente: Vl. Total = Quantidade * Vl. Compra Unitário."""
        try:
            qtd_str = self.var_quantidade.get().strip().replace("R$", "").replace(" ", "")
            if "," in qtd_str:
                qtd_str = qtd_str.replace(".", "").replace(",", ".")
            qtd = float(qtd_str) if qtd_str else 0.0
        except Exception:
            qtd = 0.0

        try:
            val_str = self.var_val_compra.get().strip().replace("R$", "").replace(" ", "")
            if "," in val_str:
                val_str = val_str.replace(".", "").replace(",", ".")
            val_unit = float(val_str) if val_str else 0.0
        except Exception:
            val_unit = 0.0

        val_tot = round(qtd * val_unit, 2)
        str_tot = f"{val_tot:.2f}".replace(".", ",")
        if self.var_val_total.get() != str_tot and not getattr(self, "_calculando_valores", False):
            self._calculando_valores = True
            try:
                self.var_val_total.set(str_tot)
            finally:
                self._calculando_valores = False

        self._calcular_depreciacao_form(silencioso=True)

    def _ao_alterar_val_total(self, *args):
        """Ao digitar Vl. Total, ajusta o Vl. Compra Unitário se quantidade for informada."""
        if getattr(self, "_calculando_valores", False):
            return
        try:
            tot_str = self.var_val_total.get().strip().replace("R$", "").replace(" ", "")
            if "," in tot_str:
                tot_str = tot_str.replace(".", "").replace(",", ".")
            val_tot = float(tot_str) if tot_str else 0.0
        except Exception:
            val_tot = 0.0

        try:
            qtd_str = self.var_quantidade.get().strip().replace("R$", "").replace(" ", "")
            if "," in qtd_str:
                qtd_str = qtd_str.replace(".", "").replace(",", ".")
            qtd = float(qtd_str) if qtd_str else 1.0
        except Exception:
            qtd = 1.0

        if qtd > 0 and val_tot > 0:
            val_unit = round(val_tot / qtd, 2)
            str_unit = f"{val_unit:.2f}".replace(".", ",")
            if self.var_val_compra.get() != str_unit:
                self._calculando_valores = True
                try:
                    self.var_val_compra.set(str_unit)
                finally:
                    self._calculando_valores = False

        self._calcular_depreciacao_form(silencioso=True)

    def _recarregar_combo_classificacoes(self, cat_cod: str = ""):
        if not self._service:
            return
        valor_atual = self.combo_classif.get()
        try:
            classifs = self._service.obter_classificacoes(cat_cod)
            self._map_classif = {f"{c['codigo']} - {c['descricao']}": c['codigo'] for c in classifs}
            novos_valores = list(self._map_classif.keys())
            self.combo_classif["values"] = novos_valores
            if valor_atual in novos_valores:
                self.combo_classif.set(valor_atual)
        except Exception as exc:
            logger.exception("Erro ao recarregar classificações: %s", exc)

    def _abrir_cadastro_classificacao(self):
        try:
            from ativo_imobilizado.classificacao_bens_view import abrir_classificacao_bens_sistema
            win = abrir_classificacao_bens_sistema(self, connection=self._conn)

            def _ao_fechar():
                try:
                    cat_key = self.combo_categoria.get()
                    cat_cod = getattr(self, "_map_categ", {}).get(cat_key, "")
                    self._recarregar_combo_classificacoes(cat_cod)
                except Exception:
                    pass
                win.destroy()

            win.protocol("WM_DELETE_WINDOW", _ao_fechar)
        except Exception as exc:
            logger.exception("Erro ao abrir tela de classificações: %s", exc)
            messagebox.showerror("Erro", f"Não foi possível abrir o cadastro de classificações:\n{exc}", parent=self)

    def _on_categoria_alterada(self):
        if not self._service:
            return
        cat_key = self.combo_categoria.get()
        cat_cod = self._map_categ.get(cat_key, "")
        self._recarregar_combo_classificacoes(cat_cod)
        if self.combo_classif["values"]:
            self.combo_classif.current(0)
        else:
            self.combo_classif.set("")

    def _carregar_grid(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self._service:
            return

        try:
            emp_cod = self._obter_empresa_selecionada()
            self._bens_cache = self._service.listar_bens(emp_cod)
            for b in self._bens_cache:
                qtd = float(b.get("quantidade") or 1.0)
                v_compra = float(b.get("valor_compra") or 0.0)
                v_total = float(b.get("valor_total") or (qtd * v_compra))
                dep = b.get("depreciacao")
                vl_atual = dep.valor_atual if (dep and dep.valido) else v_total

                qtd_fmt = f"{qtd:.2f}".replace(".", ",")
                compra_fmt = f"R$ {v_compra:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                total_fmt = f"R$ {v_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                atual_fmt = f"R$ {vl_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                self.tree.insert(
                    "",
                    tk.END,
                    iid=str(b["numero_do_bem"]),
                    values=(
                        b["numero_do_bem"],
                        b["descricao_do_bem"],
                        b.get("categoria_bem", ""),
                        b.get("classificacao", ""),
                        b.get("localizacao", ""),
                        b.get("nome_func_responsavel", ""),
                        b.get("marca", ""),
                        qtd_fmt,
                        compra_fmt,
                        total_fmt,
                        atual_fmt,
                        b.get("descricao_status_bem") or "ATIVO",
                    ),
                )
        except Exception as exc:
            logger.exception("Erro ao listar bens: %s", exc)

    def _filtrar_grid(self):
        filtro = self.txt_busca.get().strip().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)

        for b in self._bens_cache:
            num = str(b.get("numero_do_bem", "")).lower()
            descr = str(b.get("descricao_do_bem", "")).lower()
            marca = str(b.get("marca", "")).lower()
            if not filtro or filtro in num or filtro in descr or filtro in marca:
                qtd = float(b.get("quantidade") or 1.0)
                v_compra = float(b.get("valor_compra") or 0.0)
                v_total = float(b.get("valor_total") or (qtd * v_compra))
                dep = b.get("depreciacao")
                vl_atual = dep.valor_atual if (dep and dep.valido) else v_total

                qtd_fmt = f"{qtd:.2f}".replace(".", ",")
                compra_fmt = f"R$ {v_compra:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                total_fmt = f"R$ {v_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                atual_fmt = f"R$ {vl_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                self.tree.insert(
                    "",
                    tk.END,
                    iid=str(b["numero_do_bem"]),
                    values=(
                        b["numero_do_bem"],
                        b["descricao_do_bem"],
                        b.get("categoria_bem", ""),
                        b.get("classificacao", ""),
                        b.get("localizacao", ""),
                        b.get("nome_func_responsavel", ""),
                        b.get("marca", ""),
                        qtd_fmt,
                        compra_fmt,
                        total_fmt,
                        atual_fmt,
                        b.get("descricao_status_bem") or "ATIVO",
                    ),
                )

    def _carregar_registro_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            return
        cod_bem = sel[0]
        emp_cod = self._obter_empresa_selecionada()

        bem = None
        if self._service:
            bem = self._service.obter_bem(cod_bem, emp_cod)

        if not bem:
            for b in self._bens_cache:
                if str(b.get("numero_do_bem")) == str(cod_bem):
                    bem = b
                    break

        if not bem:
            return

        self._modo_inclusao = False
        self.lbl_modo.config(text="MODO: ALTERAÇÃO", fg="#C53030")

        self.txt_cod_bem.delete(0, tk.END)
        self.txt_cod_bem.insert(0, str(bem.get("numero_do_bem", "")))

        self.txt_descricao.delete(0, tk.END)
        self.txt_descricao.insert(0, bem.get("descricao_do_bem", ""))

        self.txt_plaqueta.delete(0, tk.END)
        self.txt_plaqueta.insert(0, bem.get("codigo_barrasativo", ""))

        self.txt_serie.delete(0, tk.END)
        self.txt_serie.insert(0, bem.get("numero_de_serie", ""))

        self._selecionar_combo_por_codigo(self.combo_cctrl, getattr(self, "_map_cctrl", {}), bem.get("geocctrlcodestr"))
        self._selecionar_combo_por_codigo(self.combo_categoria, getattr(self, "_map_categ", {}), bem.get("codigo_categoria_bem"))
        self._on_categoria_alterada()
        cod_classif = bem.get("codigo_classificacaoativoimobilizado")
        if cod_classif and cod_classif not in getattr(self, "_map_classif", {}).values():
            self._recarregar_combo_classificacoes("")
        self._selecionar_combo_por_codigo(self.combo_classif, getattr(self, "_map_classif", {}), cod_classif)
        self._selecionar_combo_por_codigo(self.combo_local, getattr(self, "_map_local", {}), bem.get("codigo_localizacao"))
        self._selecionar_combo_por_codigo(self.combo_func, getattr(self, "_map_func", {}), bem.get("codigo_func_responsavel"))
        self._selecionar_combo_por_codigo(self.combo_marca, getattr(self, "_map_marca", {}), bem.get("codigo_da_marca"))
        self._selecionar_combo_por_codigo(self.combo_status, getattr(self, "_map_status", {}), bem.get("codigo_status_bem"))

        # Valores e Entrada
        qtd = float(bem.get("quantidade") or 1.0)
        v_compra = float(bem.get("valor_compra") or 0.0)
        v_total = float(bem.get("valor_total") or (qtd * v_compra))

        self.var_quantidade.set(f"{qtd:.2f}".replace(".", ","))
        self.var_val_compra.set(f"{v_compra:.2f}".replace(".", ","))
        self.var_val_total.set(f"{v_total:.2f}".replace(".", ","))
        self.var_dt_aquisicao.set(bem.get("data_aquisicao") or "")

        self.var_taxa_dep.set(f"{float(bem.get('taxa_depreciacao_anual') or 10.0):.2f}".replace(".", ","))
        self.var_dt_revisao.set(bem.get("data_ultima_revisao") or "")
        self.var_foto.set(bem.get("caminho_foto") or "")
        self.txt_obs.delete("1.0", tk.END)
        self.txt_obs.insert("1.0", bem.get("observacoes") or "")

        # Atualiza badge de cálculo
        self._calcular_depreciacao_form(silencioso=True)

    def _novo_registro(self):
        self._modo_inclusao = True
        self.lbl_modo.config(text="MODO: INCLUSÃO", fg="#2B6CB0")

        proximo = "1"
        if self._service:
            try:
                emp_cod = self._obter_empresa_selecionada()
                proximo = self._service.proximo_codigo(emp_cod)
            except Exception:
                proximo = "1"

        self.txt_cod_bem.delete(0, tk.END)
        self.txt_cod_bem.insert(0, proximo)

        self.txt_descricao.delete(0, tk.END)
        self.txt_plaqueta.delete(0, tk.END)
        self.txt_serie.delete(0, tk.END)

        self.combo_cctrl.set("")
        self.combo_categoria.set("")
        self._recarregar_combo_classificacoes("")
        self.combo_classif.set("")
        self.combo_local.set("")
        if self.combo_func["values"]:
            self.combo_func.current(0)
        self.combo_marca.set("")
        if "1 - ATIVO" in self.combo_status["values"]:
            self.combo_status.set("1 - ATIVO")
        elif self.combo_status["values"]:
            self.combo_status.current(0)

        self.var_quantidade.set("1,00")
        self.var_val_compra.set("0,00")
        self.var_val_total.set("0,00")
        self.var_dt_aquisicao.set("")
        self.var_taxa_dep.set("10,00")
        self.var_dt_revisao.set("")
        self.var_foto.set("")
        self.txt_obs.delete("1.0", tk.END)

        self.lbl_anos_uso.config(text="Tempo em Uso: - anos")
        self.lbl_dep_acumulada.config(text="Dep. Acumulada: R$ 0,00")
        self.lbl_val_atual.config(text="Valor Atual Estimado: R$ 0,00")
        self.txt_descricao.focus_set()

    def _calcular_depreciacao_form(self, silencioso=False):
        dt_aq = self.var_dt_aquisicao.get().strip()
        val_compra = self.var_val_compra.get().strip()
        taxa = self.var_taxa_dep.get().strip()

        val_compra_limpo = val_compra.replace("R$", "").replace(" ", "")
        if "," in val_compra_limpo:
            val_compra_limpo = val_compra_limpo.replace(".", "").replace(",", ".")

        taxa_limpa = taxa.replace("%", "").replace(" ", "")
        if "," in taxa_limpa:
            taxa_limpa = taxa_limpa.replace(".", "").replace(",", ".")

        if not dt_aq or not val_compra_limpo or not taxa_limpa:
            if not silencioso:
                messagebox.showwarning(
                    "Dados Insuficientes",
                    "Informe Data de Aquisição, Valor de Compra e Taxa Anual (%) para calcular a depreciação.",
                    parent=self,
                )
            return

        if not self._service:
            return

        calc = self._service.calcular_depreciacao(dt_aq, val_compra_limpo, taxa_limpa)
        if calc.valido:
            self.lbl_anos_uso.config(text=f"Tempo em Uso: {calc.anos_em_uso:.2f} anos")
            self.lbl_dep_acumulada.config(text=f"Dep. Acumulada: R$ {calc.depreciacao_acumulada:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            self.lbl_val_atual.config(text=f"Valor Atual Estimado: R$ {calc.valor_atual:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        else:
            if not silencioso:
                messagebox.showerror("Erro no Cálculo", calc.mensagem, parent=self)

    def _salvar(self):
        if not self._service:
            messagebox.showerror("Erro", "Serviço de Ativo Imobilizado indisponível.", parent=self)
            return

        marca_cod = self._resolver_marca_digitada()
        if marca_cod is None:
            return

        status_sel = self.combo_status.get().strip()
        status_cod = self._map_status.get(status_sel)
        if not status_cod:
            for rotulo, cod in getattr(self, "_map_status", {}).items():
                if status_sel.upper() in rotulo.upper() or status_sel == str(cod):
                    status_cod = cod
                    break
        if not status_cod:
            status_cod = "1"

        def _parse_campo_float(val: str, default: float = 0.0) -> float:
            s = str(val or "").strip().replace("R$", "").replace(" ", "")
            if not s:
                return default
            if "," in s:
                s = s.replace(".", "").replace(",", ".")
            try:
                return float(s)
            except (ValueError, TypeError):
                return default

        qtd = _parse_campo_float(self.var_quantidade.get(), default=1.0)
        if qtd <= 0:
            qtd = 1.0
        v_compra = _parse_campo_float(self.var_val_compra.get(), default=0.0)
        v_total = _parse_campo_float(self.var_val_total.get(), default=round(qtd * v_compra, 2))
        if v_total <= 0 and v_compra > 0:
            v_total = round(qtd * v_compra, 2)
        taxa = _parse_campo_float(self.var_taxa_dep.get(), default=10.0)

        cctrl_cod = self._map_cctrl.get(self.combo_cctrl.get(), "")
        categ_cod = self._map_categ.get(self.combo_categoria.get(), "")
        classif_cod = self._map_classif.get(self.combo_classif.get(), "")
        local_cod = self._map_local.get(self.combo_local.get(), "")
        func_cod = self._map_func.get(self.combo_func.get(), "")
        emp_cod = self._obter_empresa_selecionada()

        dados = {
            "numero_do_bem": self.txt_cod_bem.get().strip(),
            "descricao_do_bem": self.txt_descricao.get().strip(),
            "empcod": emp_cod,
            "geocctrlcodestr": cctrl_cod,
            "codigo_categoria_bem": categ_cod,
            "codigo_classificacaoativoimobilizado": classif_cod,
            "codigo_barrasativo": self.txt_plaqueta.get().strip(),
            "numero_de_serie": self.txt_serie.get().strip(),
            "codigo_localizacao": local_cod,
            "codigo_func_responsavel": func_cod,
            "codigo_da_marca": marca_cod,
            "codigo_status_bem": status_cod,
            "quantidade": qtd,
            "valor_compra": v_compra,
            "valor_total": v_total,
            "data_aquisicao": self.var_dt_aquisicao.get().strip(),
            "taxa_depreciacao_anual": taxa,
            "data_ultima_revisao": self.var_dt_revisao.get().strip(),
            "caminho_foto": self.var_foto.get().strip(),
            "observacoes": self.txt_obs.get("1.0", tk.END).strip(),
        }

        res = self._service.salvar_bem(dados, modo_inclusao=self._modo_inclusao)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem, parent=self)
            self._carregar_grid()
            self._novo_registro()
        else:
            messagebox.showerror("Erro de Validação/Gravação", res.mensagem, parent=self)

    def _excluir(self):
        cod_bem = self.txt_cod_bem.get().strip()
        if not cod_bem:
            messagebox.showwarning("Aviso", "Nenhum bem selecionado para exclusão.", parent=self)
            return

        if not messagebox.askyesno("Confirmação", f"Deseja realmente excluir o bem de código {cod_bem}?", parent=self):
            return

        if self._service:
            res = self._service.excluir_bem(cod_bem)
            if res.sucesso:
                messagebox.showinfo("Sucesso", res.mensagem, parent=self)
                self._carregar_grid()
                self._novo_registro()
            else:
                messagebox.showerror("Erro", res.mensagem, parent=self)

    def _procurar_foto(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar Foto do Bem",
            filetypes=[("Imagens", "*.jpg;*.jpeg;*.png;*.bmp"), ("Todos os Arquivos", "*.*")]
        )
        if caminho:
            self.txt_foto.delete(0, tk.END)
            self.txt_foto.insert(0, caminho)

    # ── Helpers de Seleção ───────────────────────────────────────────────

    def _obter_empresa_selecionada(self) -> str:
        sel = self.combo_empresa.get()
        return getattr(self, "_map_emp", {}).get(sel, self._empresa_codigo or "001")

    def _selecionar_combo_por_codigo(self, combo: ttk.Combobox, mapa: Dict[str, str], codigo: Optional[str]):
        if not codigo:
            combo.set("")
            return
        cod_str = str(codigo).strip()
        for rotulo, cod in mapa.items():
            if str(cod).strip() == cod_str:
                combo.set(rotulo)
                return
        combo.set("")
