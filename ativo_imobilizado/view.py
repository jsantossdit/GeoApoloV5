"""
Interface Gráfica (Tkinter / ttk) para Manutenção de Ativo Imobilizado e Depreciação.
Layout corporativo profissional no padrão visual GeoAlvo (#1A365D).
"""

import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict, Any, Optional

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

        self._configurar_estilos()
        self._criar_interface()
        self._carregar_combos()
        self._novo_registro()
        self._carregar_grid()

        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<F5>", lambda e: self._carregar_grid())

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

        self.lbl_modo = tk.Label(tb, text="MODO: INCLUSÃO", font=("Segoe UI", 9, "bold"), fg="#2B6CB0", bg="#F0F4F8")
        self.lbl_modo.pack(side=tk.RIGHT, padx=16)

        # 3. Notebook / Abas de Dados
        notebook = ttk.Notebook(self)
        notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=False, padx=12, pady=8)

        tab_cad = ttk.Frame(notebook, padding=10)
        tab_dep = ttk.Frame(notebook, padding=10)

        notebook.add(tab_cad, text="📋 Identificação & Cadastro")
        notebook.add(tab_dep, text="📈 Depreciação & Valores Contábeis")

        # ── ABA 1: Identificação & Cadastro ──
        f_id = ttk.LabelFrame(tab_cad, text="Identificação Patrimonial", padding=8)
        f_id.pack(side=tk.TOP, fill=tk.X, pady=(0, 6))

        # Linha 1: Código do Bem, Empresa, Plaqueta / Barras, Nº de Série
        r1 = ttk.Frame(f_id)
        r1.pack(fill=tk.X, pady=3)

        ttk.Label(r1, text="Nº do Bem:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_cod_bem = ttk.Entry(r1, width=12, font=("Segoe UI", 9, "bold"))
        self.txt_cod_bem.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(r1, text="Empresa:").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_empresa = ttk.Combobox(r1, state="readonly", width=22)
        self.combo_empresa.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(r1, text="Plaqueta / Cód. Barras:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_plaqueta = ttk.Entry(r1, width=16)
        self.txt_plaqueta.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(r1, text="Nº de Série:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_serie = ttk.Entry(r1, width=16)
        self.txt_serie.pack(side=tk.LEFT)

        # Linha 2: Descrição do Bem
        r2 = ttk.Frame(f_id)
        r2.pack(fill=tk.X, pady=3)

        ttk.Label(r2, text="Descrição do Bem:*").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_descricao = ttk.Entry(r2, font=("Segoe UI", 9))
        self.txt_descricao.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Classificação e Estrutura Organizacional
        f_org = ttk.LabelFrame(tab_cad, text="Classificação & Localização Organizacional", padding=8)
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
        self.combo_classif = ttk.Combobox(r3, state="readonly", width=28)
        self.combo_classif.pack(side=tk.LEFT)

        r4 = ttk.Frame(f_org)
        r4.pack(fill=tk.X, pady=3)

        ttk.Label(r4, text="Localização Física:*").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_local = ttk.Combobox(r4, state="readonly", width=30)
        self.combo_local.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(r4, text="Responsável:").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_func = ttk.Combobox(r4, state="readonly", width=28)
        self.combo_func.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(r4, text="Marca do Produto:").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_marca = ttk.Combobox(r4, state="readonly", width=20)
        self.combo_marca.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(r4, text="Status do Bem:").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_status = ttk.Combobox(r4, state="readonly", width=16)
        self.combo_status.pack(side=tk.LEFT)

        # ── ABA 2: Depreciação & Valores Contábeis ──
        f_dep_vals = ttk.LabelFrame(tab_dep, text="Valores de Aquisição e Taxas", padding=8)
        f_dep_vals.pack(side=tk.TOP, fill=tk.X, pady=(0, 6))

        rd1 = ttk.Frame(f_dep_vals)
        rd1.pack(fill=tk.X, pady=3)

        ttk.Label(rd1, text="Data Aquisição (DD/MM/AAAA):").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_dt_aquisicao = ttk.Entry(rd1, width=14)
        self.txt_dt_aquisicao.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(rd1, text="Valor Compra (R$):").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_val_compra = ttk.Entry(rd1, width=14)
        self.txt_val_compra.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(rd1, text="Taxa Dep. Anual (%):").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_taxa_dep = ttk.Entry(rd1, width=10)
        self.txt_taxa_dep.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(rd1, text="Última Revisão:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_dt_revisao = ttk.Entry(rd1, width=14)
        self.txt_dt_revisao.pack(side=tk.LEFT)

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
        self.txt_foto = ttk.Entry(ro1)
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
        self.txt_busca = ttk.Entry(f_busca, width=32)
        self.txt_busca.pack(side=tk.LEFT, padx=(0, 8))
        self.txt_busca.bind("<KeyRelease>", lambda e: self._filtrar_grid())

        cols = ("bem", "descricao", "categoria", "classificacao", "local", "resp", "compra", "atual", "status")
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
        self.tree.heading("compra", text="Vl. Compra (R$)")
        self.tree.heading("atual", text="Vl. Atual (R$)")
        self.tree.heading("status", text="Status")

        self.tree.column("bem", width=80, anchor=tk.CENTER)
        self.tree.column("descricao", width=220, anchor=tk.W)
        self.tree.column("categoria", width=120, anchor=tk.W)
        self.tree.column("classificacao", width=140, anchor=tk.W)
        self.tree.column("local", width=140, anchor=tk.W)
        self.tree.column("resp", width=140, anchor=tk.W)
        self.tree.column("compra", width=100, anchor=tk.E)
        self.tree.column("atual", width=100, anchor=tk.E)
        self.tree.column("status", width=90, anchor=tk.CENTER)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.bind("<Double-1>", lambda e: self._carregar_registro_selecionado())
        self.tree.bind("<Delete>", lambda e: self._excluir())

    # ── Métodos de Carregamento ──────────────────────────────────────────

    def _carregar_combos(self):
        if not self._service:
            return

        try:
            # 1. Empresas
            emps = self._service.obter_empresas()
            self._map_emp = {f"{e['codigo']} - {e['descricao']}": e['codigo'] for e in emps}
            self.combo_empresa["values"] = list(self._map_emp.keys())
            if self.combo_empresa["values"]:
                self.combo_empresa.current(0)

            # 2. Centros de Custo
            cctrls = self._service.obter_centros_controle()
            self._map_cctrl = {f"{c['codigo']} - {c['descricao']}": c['codigo'] for c in cctrls}
            self.combo_cctrl["values"] = list(self._map_cctrl.keys())

            # 3. Categorias
            categs = self._service.obter_categorias()
            self._map_categ = {f"{c['codigo']} - {c['descricao']}": c['codigo'] for c in categs}
            self.combo_categoria["values"] = list(self._map_categ.keys())

            # 4. Localizações
            locs = self._service.obter_localizacoes()
            self._map_local = {f"{l['codigo']} - {l['descricao']}": l['codigo'] for l in locs}
            self.combo_local["values"] = list(self._map_local.keys())

            # 5. Funcionários
            funcs = self._service.obter_funcionarios()
            self._map_func = {f"{f['codigo']} - {f['descricao']}": f['codigo'] for f in funcs}
            self.combo_func["values"] = list(self._map_func.keys())

            # 6. Marcas
            marcas = self._service.obter_marcas()
            self._map_marca = {f"{m['codigo']} - {m['descricao']}": m['codigo'] for m in marcas}
            self.combo_marca["values"] = list(self._map_marca.keys())

            # 7. Status
            status_list = self._service.obter_status()
            self._map_status = {f"{s['codigo']} - {s['descricao']}": s['codigo'] for s in status_list}
            self.combo_status["values"] = list(self._map_status.keys())
        except Exception as exc:
            logger.exception("Erro ao carregar combos de ativo imobilizado: %s", exc)

    def _on_categoria_alterada(self):
        if not self._service:
            return
        cat_key = self.combo_categoria.get()
        cat_cod = self._map_categ.get(cat_key, "")
        try:
            classifs = self._service.obter_classificacoes(cat_cod)
            self._map_classif = {f"{c['codigo']} - {c['descricao']}": c['codigo'] for c in classifs}
            self.combo_classif["values"] = list(self._map_classif.keys())
            if self.combo_classif["values"]:
                self.combo_classif.current(0)
            else:
                self.combo_classif.set("")
        except Exception as exc:
            logger.exception("Erro ao atualizar classificações: %s", exc)

    def _carregar_grid(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self._service:
            return

        try:
            emp_cod = self._obter_empresa_selecionada()
            self._bens_cache = self._service.listar_bens(emp_cod)
            for b in self._bens_cache:
                vl_compra_str = f"R$ {float(b.get('valor_compra') or 0.0):,.2f}"
                dep = b.get("depreciacao")
                vl_atual_str = f"R$ {dep.valor_atual:,.2f}" if dep and dep.valido else f"R$ {float(b.get('valor_compra') or 0.0):,.2f}"

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
                        vl_compra_str,
                        vl_atual_str,
                        b.get("descricao_status_bem", ""),
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
            if not filtro or filtro in num or filtro in descr:
                vl_compra_str = f"R$ {float(b.get('valor_compra') or 0.0):,.2f}"
                dep = b.get("depreciacao")
                vl_atual_str = f"R$ {dep.valor_atual:,.2f}" if dep and dep.valido else f"R$ {float(b.get('valor_compra') or 0.0):,.2f}"

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
                        vl_compra_str,
                        vl_atual_str,
                        b.get("descricao_status_bem", ""),
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
            # Busca do cache
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
        self._selecionar_combo_por_codigo(self.combo_classif, getattr(self, "_map_classif", {}), bem.get("codigo_classificacaoativoimobilizado"))
        self._selecionar_combo_por_codigo(self.combo_local, getattr(self, "_map_local", {}), bem.get("codigo_localizacao"))
        self._selecionar_combo_por_codigo(self.combo_func, getattr(self, "_map_func", {}), bem.get("codigo_func_responsavel"))
        self._selecionar_combo_por_codigo(self.combo_marca, getattr(self, "_map_marca", {}), bem.get("codigo_da_marca"))
        self._selecionar_combo_por_codigo(self.combo_status, getattr(self, "_map_status", {}), bem.get("codigo_status_bem"))

        # Depreciação
        self.txt_dt_aquisicao.delete(0, tk.END)
        self.txt_dt_aquisicao.insert(0, bem.get("data_aquisicao") or "")

        self.txt_val_compra.delete(0, tk.END)
        self.txt_val_compra.insert(0, str(bem.get("valor_compra", "")))

        self.txt_taxa_dep.delete(0, tk.END)
        self.txt_taxa_dep.insert(0, str(bem.get("taxa_depreciacao_anual", "")))

        self.txt_dt_revisao.delete(0, tk.END)
        self.txt_dt_revisao.insert(0, bem.get("data_ultima_revisao") or "")

        self.txt_foto.delete(0, tk.END)
        self.txt_foto.insert(0, bem.get("caminho_foto", ""))

        self.txt_obs.delete("1.0", tk.END)
        self.txt_obs.insert("1.0", bem.get("observacoes", ""))

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

        if self.combo_cctrl["values"]:
            self.combo_cctrl.current(0)
        if self.combo_categoria["values"]:
            self.combo_categoria.current(0)
            self._on_categoria_alterada()
        if self.combo_local["values"]:
            self.combo_local.current(0)
        if self.combo_func["values"]:
            self.combo_func.current(0)
        if self.combo_marca["values"]:
            self.combo_marca.current(0)
        if self.combo_status["values"]:
            self.combo_status.current(0)

        self.txt_dt_aquisicao.delete(0, tk.END)
        self.txt_val_compra.delete(0, tk.END)
        self.txt_taxa_dep.delete(0, tk.END)
        self.txt_dt_revisao.delete(0, tk.END)
        self.txt_foto.delete(0, tk.END)
        self.txt_obs.delete("1.0", tk.END)

        self.lbl_anos_uso.config(text="Tempo em Uso: - anos")
        self.lbl_dep_acumulada.config(text="Dep. Acumulada: R$ 0,00")
        self.lbl_val_atual.config(text="Valor Atual Estimado: R$ 0,00")
        self.txt_descricao.focus_set()

    def _calcular_depreciacao_form(self, silencioso=False):
        dt_aq = self.txt_dt_aquisicao.get().strip()
        val_compra = self.txt_val_compra.get().strip()
        taxa = self.txt_taxa_dep.get().strip()

        if not dt_aq or not val_compra or not taxa:
            if not silencioso:
                messagebox.showwarning(
                    "Dados Insuficientes",
                    "Informe Data de Aquisição, Valor de Compra e Taxa Anual (%) para calcular a depreciação."
                )
            return

        if not self._service:
            return

        calc = self._service.calcular_depreciacao(dt_aq, val_compra, taxa)
        if calc.valido:
            self.lbl_anos_uso.config(text=f"Tempo em Uso: {calc.anos_em_uso:.2f} anos")
            self.lbl_dep_acumulada.config(text=f"Dep. Acumulada: R$ {calc.depreciacao_acumulada:,.2f}")
            self.lbl_val_atual.config(text=f"Valor Atual Estimado: R$ {calc.valor_atual:,.2f}")
        else:
            if not silencioso:
                messagebox.showerror("Erro no Cálculo", calc.mensagem)

    def _salvar(self):
        if not self._service:
            messagebox.showerror("Erro", "Serviço de Ativo Imobilizado indisponível.")
            return

        cctrl_cod = self._map_cctrl.get(self.combo_cctrl.get(), "")
        categ_cod = self._map_categ.get(self.combo_categoria.get(), "")
        classif_cod = self._map_classif.get(self.combo_classif.get(), "")
        local_cod = self._map_local.get(self.combo_local.get(), "")
        func_cod = self._map_func.get(self.combo_func.get(), "")
        marca_cod = self._map_marca.get(self.combo_marca.get(), "")
        status_cod = self._map_status.get(self.combo_status.get(), "")
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
            "data_aquisicao": self.txt_dt_aquisicao.get().strip(),
            "valor_compra": self.txt_val_compra.get().strip() or "0",
            "taxa_depreciacao_anual": self.txt_taxa_dep.get().strip() or "0",
            "data_ultima_revisao": self.txt_dt_revisao.get().strip(),
            "caminho_foto": self.txt_foto.get().strip(),
            "observacoes": self.txt_obs.get("1.0", tk.END).strip(),
        }

        res = self._service.salvar_bem(dados, modo_inclusao=self._modo_inclusao)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self._carregar_grid()
            self._novo_registro()
        else:
            messagebox.showerror("Erro de Validação/Gravação", res.mensagem)

    def _excluir(self):
        cod_bem = self.txt_cod_bem.get().strip()
        if not cod_bem:
            messagebox.showwarning("Aviso", "Nenhum bem selecionado para exclusão.")
            return

        if not messagebox.askyesno("Confirmação", f"Deseja realmente excluir o bem de código {cod_bem}?"):
            return

        if self._service:
            res = self._service.excluir_bem(cod_bem)
            if res.sucesso:
                messagebox.showinfo("Sucesso", res.mensagem)
                self._carregar_grid()
                self._novo_registro()
            else:
                messagebox.showerror("Erro", res.mensagem)

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
