"""
Interface Visual (Tkinter) do Dashboard de Doações & Inteligência Analítica (Empresa 1.01).
Alimentado pelas regras, campos e métricas de Dashboard-menuprincipal.sql.
GeoApolo V5
"""

import csv
import threading
import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta

logger = logging.getLogger(__name__)

from dashboard.models import (
    FiltroDashboardDTO,
    ResumoDoacoesDTO,
    DoadorPerfilDTO,
    StatusDoadorMetricaDTO,
    DioceseMetricaDTO,
    TipoCobrancaMetricaDTO,
    EvolucaoMesDTO,
    EvolucaoAnoDTO,
    HistoricoAnoMetodoDTO,
    InsightIADTO,
)
from dashboard.service import DashboardService
from dashboard.gauge import DashboardGaugeWidget, GaugeOverlay


MESES_LISTA = [
    ("01 - Janeiro", 1),
    ("02 - Fevereiro", 2),
    ("03 - Março", 3),
    ("04 - Abril", 4),
    ("05 - Maio", 5),
    ("06 - Junho", 6),
    ("07 - Julho", 7),
    ("08 - Agosto", 8),
    ("09 - Setembro", 9),
    ("10 - Outubro", 10),
    ("11 - Novembro", 11),
    ("12 - Dezembro", 12),
]


class DashboardDoacoesFrame(ttk.Frame):
    """
    Componente visual integrado ao menu principal do sistema GeoAlvo.
    Apresenta KPIs de doações, perfil dos doadores (Novo, Recorrente, Retorno),
    relação detalhada de doadores da query oficial, gráficos e diagnósticos de IA.
    Suporta carregamento assíncrono em segundo plano para inicialização instantânea.
    """

    def __init__(self, parent, service: Optional[DashboardService] = None, empresa: str = "1.01", assincrono_inicial: bool = True, auto_carregar: bool = False, **kwargs):
        super().__init__(parent, **kwargs)
        self.service = service or DashboardService()
        self.empresa_atual = empresa
        self.resumo_atual = ResumoDoacoesDTO()
        self._todos_doadores: List[DoadorPerfilDTO] = []
        self._carregando: bool = False
        self._carregando_historico: bool = False

        self._configurar_estilos()
        self._construir_interface()

        # O carregamento é sob demanda por padrão para liberar o login e não travar o sistema.
        # Se auto_carregar=True ou assincrono_inicial=False (execução direta/síncrona):
        if auto_carregar or not assincrono_inicial:
            if assincrono_inicial:
                self.after(50, lambda: self.carregar_dados(assincrono=True))
            else:
                self.carregar_dados(assincrono=False)
        else:
            self.lbl_status_carregamento.config(
                text="⚡ Modo sob demanda ativo. Clique em '⚙️ Sincronizar Banco' ou '⚡ Filtrar' para carregar."
            )

    def _configurar_estilos(self):
        style = ttk.Style()
        style.configure("DashHeader.TLabel", font=("Segoe UI", 11, "bold"), foreground="#1A365D")
        style.configure("DashSub.TLabel", font=("Segoe UI", 8), foreground="#64748B")
        style.configure("DashCardTitle.TLabel", font=("Segoe UI", 8, "bold"), foreground="#64748B")
        style.configure("DashCardVal.TLabel", font=("Segoe UI", 13, "bold"))
        style.configure("DashCardSub.TLabel", font=("Segoe UI", 7), foreground="#94A3B8")

    def destruir_ou_liberar(self):
        """
        Cancela operações assíncronas, limpa as listas e coleções pesadas da memória
        e destrói a hierarquia de widgets para liberar recursos da máquina.
        """
        try:
            self._carregando = False
            self._carregando_historico = False
            if hasattr(self, "_timer_gauge") and self._timer_gauge:
                try:
                    self.after_cancel(self._timer_gauge)
                except Exception:
                    pass
                self._timer_gauge = None
            if hasattr(self, "_todos_doadores") and self._todos_doadores:
                self._todos_doadores.clear()
            self.resumo_atual = None
            for child in list(self.winfo_children()):
                try:
                    child.destroy()
                except Exception:
                    pass
            self.destroy()
            import gc
            gc.collect()
        except Exception as exc:
            logger.debug("Erro ao liberar DashboardDoacoesFrame: %s", exc)

    def _construir_interface(self):
        # 1. Barra Superior com 2 Linhas: Título/Ações + Controles de Parâmetros
        top_bar = tk.Frame(self, bg="#1A365D", height=82)
        top_bar.pack(fill=tk.X, side=tk.TOP)
        top_bar.pack_propagate(False)

        # Linha Superior da Barra: Título, Status e Botões de Sincronização / Exportação
        row_sup = tk.Frame(top_bar, bg="#1A365D")
        row_sup.pack(fill=tk.X, padx=12, pady=(4, 2))

        lbl_tit = tk.Label(
            row_sup,
            text="📊 Dashboard de Doações & Inteligência Analítica (Empresa 1.01 - RCC)",
            font=("Segoe UI", 11, "bold"),
            bg="#1A365D",
            fg="#FFFFFF"
        )
        lbl_tit.pack(side=tk.LEFT)

        self.lbl_status_carregamento = tk.Label(
            row_sup,
            text="",
            font=("Segoe UI", 8, "italic"),
            bg="#1A365D",
            fg="#FDE047"
        )
        self.lbl_status_carregamento.pack(side=tk.LEFT, padx=15)

        box_acoes = tk.Frame(row_sup, bg="#1A365D")
        box_acoes.pack(side=tk.RIGHT)

        self.btn_sinc = tk.Button(
            box_acoes,
            text="⚙️ Sincronizar Banco",
            font=("Segoe UI", 8),
            bg="#0284C7",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=7,
            pady=2,
            cursor="hand2",
            command=self._sincronizar_procedure
        )
        self.btn_sinc.pack(side=tk.LEFT, padx=3)

        btn_exportar = tk.Button(
            box_acoes,
            text="📥 Exportar CSV",
            font=("Segoe UI", 8),
            bg="#059669",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=7,
            pady=2,
            cursor="hand2",
            command=self._exportar_relatorio_csv
        )
        btn_exportar.pack(side=tk.LEFT, padx=3)

        # Linha Inferior da Barra: Controles de Filtros e Parâmetros
        ctrl_box = tk.Frame(top_bar, bg="#1A365D")
        ctrl_box.pack(fill=tk.X, padx=12, pady=(2, 4))

        # Período
        tk.Label(ctrl_box, text="Período:", font=("Segoe UI", 8, "bold"), bg="#1A365D", fg="#F1F5F9").pack(side=tk.LEFT, padx=(0, 2))
        self.cbo_tipo_periodo = ttk.Combobox(
            ctrl_box,
            values=[
                "Últimos 10 Dias",
                "Últimos 15 Dias",
                "Últimos 30 Dias",
                "Mês Selecionado",
                "Período Personalizado"
            ],
            state="readonly",
            width=17,
            font=("Segoe UI", 8)
        )
        self.cbo_tipo_periodo.set("Últimos 10 Dias")
        self.cbo_tipo_periodo.pack(side=tk.LEFT, padx=(0, 8))
        self.cbo_tipo_periodo.bind("<<ComboboxSelected>>", self._on_tipo_periodo_changed)

        # Data Inicial
        tk.Label(ctrl_box, text="De:", font=("Segoe UI", 8, "bold"), bg="#1A365D", fg="#F1F5F9").pack(side=tk.LEFT, padx=(0, 2))
        self.txt_data_ini = ttk.Entry(ctrl_box, width=10, font=("Segoe UI", 8))
        self.txt_data_ini.insert(0, "10/09/2026")
        self.txt_data_ini.config(state="readonly")
        self.txt_data_ini.pack(side=tk.LEFT, padx=(0, 6))

        # Data Final
        tk.Label(ctrl_box, text="Até:", font=("Segoe UI", 8, "bold"), bg="#1A365D", fg="#F1F5F9").pack(side=tk.LEFT, padx=(0, 2))
        self.txt_data_fim = ttk.Entry(ctrl_box, width=10, font=("Segoe UI", 8))
        self.txt_data_fim.insert(0, "20/09/2026")
        self.txt_data_fim.config(state="readonly")
        self.txt_data_fim.pack(side=tk.LEFT, padx=(0, 8))

        # Ano
        tk.Label(ctrl_box, text="Ano:", font=("Segoe UI", 8, "bold"), bg="#1A365D", fg="#CBD5E1").pack(side=tk.LEFT, padx=(0, 2))
        self.cbo_ano = ttk.Combobox(
            ctrl_box,
            values=[str(a) for a in range(2026, 2017, -1)],
            state="disabled",
            width=5,
            font=("Segoe UI", 8)
        )
        self.cbo_ano.set("2026")
        self.cbo_ano.pack(side=tk.LEFT, padx=(0, 6))

        # Mês
        tk.Label(ctrl_box, text="Mês:", font=("Segoe UI", 8, "bold"), bg="#1A365D", fg="#CBD5E1").pack(side=tk.LEFT, padx=(0, 2))
        self.cbo_mes = ttk.Combobox(
            ctrl_box,
            values=[m[0] for m in MESES_LISTA],
            state="disabled",
            width=12,
            font=("Segoe UI", 8)
        )
        self.cbo_mes.set("09 - Setembro")
        self.cbo_mes.pack(side=tk.LEFT, padx=(0, 8))

        # Status do Doador
        tk.Label(ctrl_box, text="Status:", font=("Segoe UI", 8, "bold"), bg="#1A365D", fg="#F1F5F9").pack(side=tk.LEFT, padx=(0, 2))
        self.cbo_status = ttk.Combobox(
            ctrl_box,
            values=["Todos os Status", "Doador Recorrente", "Retorno Doador", "Novo Doador"],
            state="readonly",
            width=14,
            font=("Segoe UI", 8)
        )
        self.cbo_status.set("Todos os Status")
        self.cbo_status.pack(side=tk.LEFT, padx=(0, 6))
        self.cbo_status.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtros_tabela())

        # Forma de Contribuição
        tk.Label(ctrl_box, text="Forma:", font=("Segoe UI", 8, "bold"), bg="#1A365D", fg="#F1F5F9").pack(side=tk.LEFT, padx=(0, 2))
        self.cbo_forma = ttk.Combobox(
            ctrl_box,
            values=["Todas", "DEB", "BOL", "VND", "PIX"],
            state="readonly",
            width=5,
            font=("Segoe UI", 8)
        )
        self.cbo_forma.set("Todas")
        self.cbo_forma.pack(side=tk.LEFT, padx=(0, 10))
        self.cbo_forma.bind("<<ComboboxSelected>>", lambda e: self._aplicar_filtros_tabela())

        # Botão Filtrar Período (Destaque Principal com cor vibrante)
        self.btn_filtrar = tk.Button(
            ctrl_box,
            text="⚡ Filtrar",
            font=("Segoe UI", 8, "bold"),
            bg="#10B981",
            fg="#FFFFFF",
            activebackground="#059669",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=10,
            pady=2,
            cursor="hand2",
            command=lambda: self.carregar_dados(forcar=True)
        )
        self.btn_filtrar.pack(side=tk.LEFT, padx=3)

        # Botão Atualizar
        self.btn_atualizar = tk.Button(
            ctrl_box,
            text="🔄 Atualizar",
            font=("Segoe UI", 8, "bold"),
            bg="#2563EB",
            fg="#FFFFFF",
            activebackground="#1D4ED8",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=8,
            pady=2,
            cursor="hand2",
            command=lambda: self.carregar_dados(forcar=True)
        )
        self.btn_atualizar.pack(side=tk.LEFT, padx=3)

        # 2. Área com Rolagem e Notebook Principal
        canvas_container = tk.Canvas(self, bg="#F8FAFC", highlightthickness=0)
        v_scroll = ttk.Scrollbar(self, orient="vertical", command=canvas_container.yview)
        self.body_frame = tk.Frame(canvas_container, bg="#F8FAFC")

        self.body_frame.bind(
            "<Configure>",
            lambda e: canvas_container.configure(scrollregion=canvas_container.bbox("all"))
        )

        canvas_window = canvas_container.create_window((0, 0), window=self.body_frame, anchor="nw")
        canvas_container.configure(yscrollcommand=v_scroll.set)

        def _on_canvas_resize(event):
            canvas_container.itemconfig(canvas_window, width=event.width)
        canvas_container.bind("<Configure>", _on_canvas_resize)

        canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Componente de Gauge Analítico para feedback em tempo real das consultas
        self.gauge_overlay = GaugeOverlay(self, titulo="Processando Indicadores de Doações...")

        def _on_mousewheel(event):
            try:
                if canvas_container.winfo_exists():
                    canvas_container.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass

        canvas_container.bind("<Enter>", lambda e: canvas_container.bind_all("<MouseWheel>", _on_mousewheel))
        canvas_container.bind("<Leave>", lambda e: canvas_container.unbind_all("<MouseWheel>"))

        # Estrutura de Abas do Dashboard
        self.notebook = ttk.Notebook(self.body_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 10))

        # Aba 1: Visão Geral & Perfil dos Doadores
        self.tab_geral = tk.Frame(self.notebook, bg="#F8FAFC")
        self.notebook.add(self.tab_geral, text=" 📊 Visão Geral & Perfil dos Doadores ")

        # Aba 2: Relação Detalhada de Doadores (Query SQL Oficial)
        self.tab_doadores = tk.Frame(self.notebook, bg="#F8FAFC")
        self.notebook.add(self.tab_doadores, text=" 📋 Relação de Doadores (Query SQL) ")

        # Aba 3: Evolução Mensal & Histórico Longitudinal (2018 a 2026)
        self.tab_historico = tk.Frame(self.notebook, bg="#F8FAFC")
        self.notebook.add(self.tab_historico, text=" 📅 Evolução Mensal & Histórico (2018-2026) ")

        # Construção dos painéis
        self._construir_aba_geral(self.tab_geral)
        self._construir_aba_doadores(self.tab_doadores)
        self._construir_aba_historica(self.tab_historico)

        def _on_tab_changed(event):
            try:
                canvas_container.configure(scrollregion=canvas_container.bbox("all"))
                self._desenhar_grafico_status()
                self._desenhar_grafico_formas()
                self._desenhar_grafico_evolucao_meses()
                self._desenhar_grafico_historico_lider()

                # Lazy load: Se selecionou a Aba 3 e histórico longitudinal ainda não foi carregado
                idx = self.notebook.index(self.notebook.select())
                if idx == 2 and not self.resumo_atual.evolucao_anos:
                    self._carregar_historico_aba3()
            except Exception:
                pass
        self.notebook.bind("<<NotebookTabChanged>>", _on_tab_changed)

    # -------------------------------------------------------------
    # ABA 1: VISÃO GERAL & PERFIL DOS DOADORES
    # -------------------------------------------------------------
    def _construir_aba_geral(self, parent):
        # 1. Cards de KPI Executivos
        kpi_row = tk.Frame(parent, bg="#F8FAFC")
        kpi_row.pack(fill=tk.X, padx=10, pady=(8, 6))

        self.card_arrecadado = self._criar_card_kpi(kpi_row, 0, "ARRECADAÇÃO DO MÊS", "R$ 0,00", "#1E3A8A", "Total do mês")
        self.card_recorrentes = self._criar_card_kpi(kpi_row, 1, "DOADORES RECORRENTES", "0", "#059669", "Intervalo <= 35 dias")
        self.card_retorno = self._criar_card_kpi(kpi_row, 2, "RETORNO DE DOADORES", "0", "#D97706", "Intervalo > 35 dias")
        self.card_novos = self._criar_card_kpi(kpi_row, 3, "NOVOS DOADORES", "0", "#2563EB", "1ª doação histórica")
        self.card_ticket = self._criar_card_kpi(kpi_row, 4, "TICKET MÉDIO", "R$ 0,00", "#7C3AED", "Valor médio por doação")

        # 2. Linha de Gráficos (Status do Doador & Formas de Contribuição)
        graf_row = tk.Frame(parent, bg="#F8FAFC")
        graf_row.pack(fill=tk.X, padx=10, pady=4)

        # Gráfico 1: Status do Doador
        frame_g1 = tk.Frame(graf_row, bg="#FFFFFF", bd=1, relief=tk.SOLID, padx=10, pady=8)
        frame_g1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))

        tk.Label(
            frame_g1,
            text="👥 Composição da Base por Status do Doador",
            font=("Segoe UI", 9, "bold"),
            fg="#1E293B",
            bg="#FFFFFF"
        ).pack(anchor="w", pady=(0, 4))

        self.canvas_status = tk.Canvas(frame_g1, height=160, bg="#FFFFFF", highlightthickness=0)
        self.canvas_status.pack(fill=tk.BOTH, expand=True)
        self.canvas_status.bind("<Configure>", lambda e: self._desenhar_grafico_status())

        # Gráfico 2: Formas de Contribuição
        frame_g2 = tk.Frame(graf_row, bg="#FFFFFF", bd=1, relief=tk.SOLID, padx=10, pady=8)
        frame_g2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0))

        tk.Label(
            frame_g2,
            text="💳 Arrecadação por Forma de Contribuição (%)",
            font=("Segoe UI", 9, "bold"),
            fg="#1E293B",
            bg="#FFFFFF"
        ).pack(anchor="w", pady=(0, 4))

        self.canvas_formas = tk.Canvas(frame_g2, height=160, bg="#FFFFFF", highlightthickness=0)
        self.canvas_formas.pack(fill=tk.BOTH, expand=True)
        self.canvas_formas.bind("<Configure>", lambda e: self._desenhar_grafico_formas())

        # 3. Linha Inferior: Top Dioceses e Insights de IA
        bottom_row = tk.Frame(parent, bg="#F8FAFC")
        bottom_row.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4, 10))

        # Esquerda: Top Dioceses
        frame_dioceses = tk.Frame(bottom_row, bg="#FFFFFF", bd=1, relief=tk.SOLID, padx=10, pady=8)
        frame_dioceses.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))

        tk.Label(
            frame_dioceses,
            text="🏛️ Top Dioceses com Maior Arrecadação no Mês",
            font=("Segoe UI", 9, "bold"),
            fg="#1E293B",
            bg="#FFFFFF"
        ).pack(anchor="w", pady=(0, 4))

        cols_d = ("rank", "diocese", "uf", "qtd", "total", "pct", "ticket")
        self.tree_dioceses = ttk.Treeview(frame_dioceses, columns=cols_d, show="headings", height=7, selectmode="browse")
        self.tree_dioceses.heading("rank", text="#")
        self.tree_dioceses.heading("diocese", text="Nome da Diocese")
        self.tree_dioceses.heading("uf", text="UF")
        self.tree_dioceses.heading("qtd", text="Doações")
        self.tree_dioceses.heading("total", text="Total (R$)")
        self.tree_dioceses.heading("pct", text="%")
        self.tree_dioceses.heading("ticket", text="Ticket")

        self.tree_dioceses.column("rank", width=30, anchor=tk.CENTER)
        self.tree_dioceses.column("diocese", width=190, anchor=tk.W)
        self.tree_dioceses.column("uf", width=35, anchor=tk.CENTER)
        self.tree_dioceses.column("qtd", width=55, anchor=tk.E)
        self.tree_dioceses.column("total", width=85, anchor=tk.E)
        self.tree_dioceses.column("pct", width=45, anchor=tk.E)
        self.tree_dioceses.column("ticket", width=65, anchor=tk.E)

        scroll_dio = ttk.Scrollbar(frame_dioceses, orient=tk.VERTICAL, command=self.tree_dioceses.yview)
        self.tree_dioceses.configure(yscrollcommand=scroll_dio.set)

        self.tree_dioceses.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_dio.pack(side=tk.RIGHT, fill=tk.Y)

        # Direita: Diagnósticos e Insights de IA
        frame_ia = tk.Frame(bottom_row, bg="#FFFFFF", bd=1, relief=tk.SOLID, padx=10, pady=8)
        frame_ia.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0))

        header_ia = tk.Frame(frame_ia, bg="#FFFFFF")
        header_ia.pack(fill=tk.X, pady=(0, 4))

        tk.Label(
            header_ia,
            text="🧠 Diagnósticos Analíticos e Recomendações de IA",
            font=("Segoe UI", 9, "bold"),
            fg="#1A365D",
            bg="#FFFFFF"
        ).pack(side=tk.LEFT)

        btn_regerar = tk.Button(
            header_ia,
            text="⚡ Recalcular IA",
            font=("Segoe UI", 7, "bold"),
            bg="#E0E7FF",
            fg="#3730A3",
            relief=tk.FLAT,
            padx=6,
            pady=1,
            cursor="hand2",
            command=self._recalcular_ia
        )
        btn_regerar.pack(side=tk.RIGHT)

        self.ia_box = tk.Frame(frame_ia, bg="#FFFFFF")
        self.ia_box.pack(fill=tk.BOTH, expand=True)

    def _criar_card_kpi(self, parent, col, titulo, valor, cor, subtitulo):
        card = tk.Frame(parent, bg="#FFFFFF", bd=1, relief=tk.SOLID, padx=10, pady=8)
        card.grid(row=0, column=col, padx=3, sticky="nsew")
        parent.columnconfigure(col, weight=1)

        tk.Label(card, text=titulo, font=("Segoe UI", 7, "bold"), fg="#64748B", bg="#FFFFFF").pack(anchor="w")
        lbl_val = tk.Label(card, text=valor, font=("Segoe UI", 13, "bold"), fg=cor, bg="#FFFFFF")
        lbl_val.pack(anchor="w", pady=(2, 2))
        lbl_sub = tk.Label(card, text=subtitulo, font=("Segoe UI", 7), fg="#94A3B8", bg="#FFFFFF")
        lbl_sub.pack(anchor="w")

        return {"val": lbl_val, "sub": lbl_sub}

    # -------------------------------------------------------------
    # ABA 2: RELAÇÃO DETALHADA DE DOADORES (QUERY OFICIAL)
    # -------------------------------------------------------------
    def _construir_aba_doadores(self, parent):
        # Barra superior de busca e contadores
        bar_busca = tk.Frame(parent, bg="#F1F5F9", padx=10, pady=6)
        bar_busca.pack(fill=tk.X, padx=10, pady=(8, 4))

        tk.Label(bar_busca, text="🔍 Pesquisar:", font=("Segoe UI", 8, "bold"), bg="#F1F5F9", fg="#334155").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_busca = ttk.Entry(bar_busca, width=32, font=("Segoe UI", 8))
        self.txt_busca.pack(side=tk.LEFT, padx=(0, 10))
        self.txt_busca.bind("<KeyRelease>", lambda e: self._aplicar_filtros_tabela())

        btn_limpar_busca = tk.Button(
            bar_busca,
            text="Limpar",
            font=("Segoe UI", 7),
            bg="#E2E8F0",
            fg="#475569",
            relief=tk.FLAT,
            padx=6,
            command=lambda: [self.txt_busca.delete(0, tk.END), self._aplicar_filtros_tabela()]
        )
        btn_limpar_busca.pack(side=tk.LEFT, padx=(0, 15))

        self.lbl_contador_doadores = tk.Label(
            bar_busca,
            text="Exibindo 0 doadores | Total Listado: R$ 0,00",
            font=("Segoe UI", 8, "bold"),
            bg="#F1F5F9",
            fg="#1E3A8A"
        )
        self.lbl_contador_doadores.pack(side=tk.RIGHT)

        # Grade de Doadores
        frame_grid = tk.Frame(parent, bg="#FFFFFF", bd=1, relief=tk.SOLID)
        frame_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 10))

        cols = (
            "entcod", "entnome", "uf", "diocese", "categnome",
            "forma", "valor_doado", "dt_doacao", "valor_anterior", "dt_anterior", "status"
        )
        self.tree_doadores = ttk.Treeview(frame_grid, columns=cols, show="headings", height=15, selectmode="browse")

        self.tree_doadores.heading("entcod", text="Código")
        self.tree_doadores.heading("entnome", text="Nome do Doador")
        self.tree_doadores.heading("uf", text="UF")
        self.tree_doadores.heading("diocese", text="Diocese")
        self.tree_doadores.heading("categnome", text="Categoria")
        self.tree_doadores.heading("forma", text="Forma")
        self.tree_doadores.heading("valor_doado", text="Valor Doado (R$)")
        self.tree_doadores.heading("dt_doacao", text="Data Doação")
        self.tree_doadores.heading("valor_anterior", text="Mês Ant. (R$)")
        self.tree_doadores.heading("dt_anterior", text="Data Anterior")
        self.tree_doadores.heading("status", text="Status Doador")

        self.tree_doadores.column("entcod", width=65, anchor=tk.CENTER)
        self.tree_doadores.column("entnome", width=220, anchor=tk.W)
        self.tree_doadores.column("uf", width=35, anchor=tk.CENTER)
        self.tree_doadores.column("diocese", width=180, anchor=tk.W)
        self.tree_doadores.column("categnome", width=150, anchor=tk.W)
        self.tree_doadores.column("forma", width=55, anchor=tk.CENTER)
        self.tree_doadores.column("valor_doado", width=105, anchor=tk.E)
        self.tree_doadores.column("dt_doacao", width=85, anchor=tk.CENTER)
        self.tree_doadores.column("valor_anterior", width=105, anchor=tk.E)
        self.tree_doadores.column("dt_anterior", width=85, anchor=tk.CENTER)
        self.tree_doadores.column("status", width=130, anchor=tk.CENTER)

        scroll_y = ttk.Scrollbar(frame_grid, orient=tk.VERTICAL, command=self.tree_doadores.yview)
        scroll_x = ttk.Scrollbar(frame_grid, orient=tk.HORIZONTAL, command=self.tree_doadores.xview)
        self.tree_doadores.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree_doadores.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        frame_grid.rowconfigure(0, weight=1)
        frame_grid.columnconfigure(0, weight=1)

    # -------------------------------------------------------------
    # ABA 3: EVOLUÇÃO MENSAL & HISTÓRICO LONGITUDINAL (2018-2026)
    # -------------------------------------------------------------
    def _construir_aba_historica(self, parent):
        # 1. Painel Superior: Evolução dos meses do ano selecionado
        frame_meses = tk.Frame(parent, bg="#FFFFFF", bd=1, relief=tk.SOLID, padx=10, pady=8)
        frame_meses.pack(fill=tk.BOTH, expand=True, padx=10, pady=(8, 4))

        self.lbl_evolucao_meses_tit = tk.Label(
            frame_meses,
            text="📈 Evolução Mensal da Arrecadação no Ano Selecionado",
            font=("Segoe UI", 9, "bold"),
            fg="#1E293B",
            bg="#FFFFFF"
        )
        self.lbl_evolucao_meses_tit.pack(anchor="w", pady=(0, 4))

        self.canvas_evolucao_meses = tk.Canvas(frame_meses, height=150, bg="#FFFFFF", highlightthickness=0)
        self.canvas_evolucao_meses.pack(fill=tk.BOTH, expand=True)
        self.canvas_evolucao_meses.bind("<Configure>", lambda e: self._desenhar_grafico_evolucao_meses())

        # 2. Painel Inferior: Histórico Anual dos Meios Líderes (2018 a 2026)
        frame_hist = tk.Frame(parent, bg="#FFFFFF", bd=1, relief=tk.SOLID, padx=10, pady=8)
        frame_hist.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4, 10))

        tk.Label(
            frame_hist,
            text="🏆 Meios de Cobrança Líderes Ano a Ano (2018 - 2026)",
            font=("Segoe UI", 9, "bold"),
            fg="#1E293B",
            bg="#FFFFFF"
        ).pack(anchor="w", pady=(0, 2))

        tk.Label(
            frame_hist,
            text="Histórico consolidado longitudinal das doações processadas para o subgrupo da RCC.",
            font=("Segoe UI", 7),
            fg="#64748B",
            bg="#FFFFFF"
        ).pack(anchor="w", pady=(0, 4))

        cols_h = ("ano", "lider", "tot_lider", "pct_lider", "tot_ano", "qtd_ano", "tm_ano")
        self.tree_historico = ttk.Treeview(frame_hist, columns=cols_h, show="headings", height=6, selectmode="browse")
        self.tree_historico.heading("ano", text="Ano")
        self.tree_historico.heading("lider", text="Meio Líder no Ano")
        self.tree_historico.heading("tot_lider", text="Total Líder (R$)")
        self.tree_historico.heading("pct_lider", text="% no Ano")
        self.tree_historico.heading("tot_ano", text="Total Geral do Ano (R$)")
        self.tree_historico.heading("qtd_ano", text="Doações")
        self.tree_historico.heading("tm_ano", text="Ticket Médio")

        self.tree_historico.column("ano", width=55, anchor=tk.CENTER)
        self.tree_historico.column("lider", width=240, anchor=tk.W)
        self.tree_historico.column("tot_lider", width=120, anchor=tk.E)
        self.tree_historico.column("pct_lider", width=70, anchor=tk.E)
        self.tree_historico.column("tot_ano", width=130, anchor=tk.E)
        self.tree_historico.column("qtd_ano", width=75, anchor=tk.E)
        self.tree_historico.column("tm_ano", width=90, anchor=tk.E)

        scroll_h = ttk.Scrollbar(frame_hist, orient=tk.VERTICAL, command=self.tree_historico.yview)
        self.tree_historico.configure(yscrollcommand=scroll_h.set)

        self.tree_historico.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_h.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_tipo_periodo_changed(self, event=None):
        """Atualiza campos de data e habilitação conforme o período selecionado."""
        tipo_sel = self.cbo_tipo_periodo.get()
        ref_fim = date(2026, 9, 20)

        if "10" in tipo_sel:
            d_ini = ref_fim - timedelta(days=10)
            self._set_datas_entry(d_ini, ref_fim, editavel=False)
            self.cbo_ano.config(state="disabled")
            self.cbo_mes.config(state="disabled")
        elif "15" in tipo_sel:
            d_ini = ref_fim - timedelta(days=15)
            self._set_datas_entry(d_ini, ref_fim, editavel=False)
            self.cbo_ano.config(state="disabled")
            self.cbo_mes.config(state="disabled")
        elif "30" in tipo_sel:
            d_ini = ref_fim - timedelta(days=30)
            self._set_datas_entry(d_ini, ref_fim, editavel=False)
            self.cbo_ano.config(state="disabled")
            self.cbo_mes.config(state="disabled")
        elif "Mês" in tipo_sel:
            self.cbo_ano.config(state="readonly")
            self.cbo_mes.config(state="readonly")
            try:
                ano = int(self.cbo_ano.get())
                txt_mes = self.cbo_mes.get()
                mes = 9
                for item_txt, num in MESES_LISTA:
                    if str(num).zfill(2) in txt_mes:
                        mes = num
                        break
            except Exception:
                ano, mes = 2026, 9
            d_ini = date(ano, mes, 1)
            d_fim = date(ano, mes + 1, 1) - timedelta(days=1) if mes < 12 else date(ano, 12, 31)
            self._set_datas_entry(d_ini, d_fim, editavel=False)
        elif "Personalizado" in tipo_sel:
            self._set_datas_entry(None, None, editavel=True)
            self.cbo_ano.config(state="disabled")
            self.cbo_mes.config(state="disabled")

    def _set_datas_entry(self, d_ini: Optional[date], d_fim: Optional[date], editavel: bool = False):
        try:
            self.txt_data_ini.config(state="normal")
            self.txt_data_fim.config(state="normal")
            if d_ini:
                self.txt_data_ini.delete(0, tk.END)
                self.txt_data_ini.insert(0, d_ini.strftime("%d/%m/%Y"))
            if d_fim:
                self.txt_data_fim.delete(0, tk.END)
                self.txt_data_fim.insert(0, d_fim.strftime("%d/%m/%Y"))
            if not editavel:
                self.txt_data_ini.config(state="readonly")
                self.txt_data_fim.config(state="readonly")
        except Exception:
            pass

    def _parse_data(self, texto: str) -> Optional[date]:
        if not texto:
            return None
        try:
            partes = texto.strip().split("/")
            if len(partes) == 3:
                d, m, y = int(partes[0]), int(partes[1]), int(partes[2])
                return date(y, m, d)
        except Exception:
            pass
        return None

    def _atualizar_gauge_progresso(self, pct: int, msg: str):
        """Atualiza a agulha, percentual e mensagem do Gauge em tempo real."""
        if hasattr(self, "gauge_overlay"):
            self.gauge_overlay.atualizar(pct, msg)
        if hasattr(self, "lbl_status_carregamento"):
            self.lbl_status_carregamento.config(text=f"⚙️ {pct}% - {msg}")

    def _carregar_historico_aba3(self):
        """Carrega sob demanda as séries temporais (2018-2026) da Aba 3 com Gauge de progresso."""
        if getattr(self, "_carregando_historico", False):
            return
        self._carregando_historico = True

        if hasattr(self, "gauge_overlay"):
            self.gauge_overlay.exibir()
            self.gauge_overlay.atualizar(20, "Consultando histórico longitudinal (2018 a 2026)...")

        def _worker_hist():
            try:
                try:
                    ano = int(self.cbo_ano.get())
                except Exception:
                    ano = 2026
                filtro = FiltroDashboardDTO(empresa=self.empresa_atual, ano=ano)
                ev_meses, ev_anos, hist_met = self.service.carregar_historico(filtro)

                def _aplicar_hist():
                    self.resumo_atual.evolucao_meses = ev_meses
                    self.resumo_atual.evolucao_anos = ev_anos
                    self.resumo_atual.historico_metodos = hist_met
                    self._atualizar_aba_historica()
                    if hasattr(self, "gauge_overlay"):
                        self.gauge_overlay.atualizar(100, "Histórico carregado com sucesso!")
                        self.after(350, self.gauge_overlay.ocultar)
                    self._carregando_historico = False

                if self.winfo_exists():
                    self.after(0, _aplicar_hist)
            except Exception as exc:
                logger.exception("Erro ao carregar histórico da aba 3: %s", exc)
                self._carregando_historico = False
                if self.winfo_exists() and hasattr(self, "gauge_overlay"):
                    self.after(0, self.gauge_overlay.ocultar)

        threading.Thread(target=_worker_hist, daemon=True).start()

    # -------------------------------------------------------------
    # CARREGAMENTO E ATUALIZAÇÃO DE DADOS (ASSÍNCRONO / ALTA PERFORMANCE)
    # -------------------------------------------------------------
    def carregar_dados(self, forcar: bool = False, assincrono: bool = True):
        """
        Dispara a consulta do dashboard. Na abertura, roda automaticamente para os
        últimos 10 dias com retorno ultra-rápido, liberando a interface do GeoAlvo.
        Quando acionado pelo usuário, exibe o medidor Gauge marcando o progresso da carga.
        """
        if self._carregando:
            return

        tipo_sel = self.cbo_tipo_periodo.get() if hasattr(self, "cbo_tipo_periodo") else "Últimos 10 Dias"
        if "10" in tipo_sel:
            tipo_periodo = "10_DIAS"
        elif "15" in tipo_sel:
            tipo_periodo = "15_DIAS"
        elif "30" in tipo_sel:
            tipo_periodo = "30_DIAS"
        elif "Mês" in tipo_sel:
            tipo_periodo = "MES"
        elif "Personalizado" in tipo_sel:
            tipo_periodo = "PERSONALIZADO"
        else:
            tipo_periodo = "10_DIAS"

        try:
            ano = int(self.cbo_ano.get()) if hasattr(self, "cbo_ano") else 2026
        except Exception:
            ano = 2026

        mes = 9
        txt_mes = self.cbo_mes.get() if hasattr(self, "cbo_mes") else "09 - Setembro"
        for item_txt, num in MESES_LISTA:
            if str(num).zfill(2) in txt_mes or item_txt.split("-")[1].strip().lower() in txt_mes.lower():
                mes = num
                break

        dt_ini = self._parse_data(self.txt_data_ini.get()) if hasattr(self, "txt_data_ini") else None
        dt_fim = self._parse_data(self.txt_data_fim.get()) if hasattr(self, "txt_data_fim") else None

        filtro = FiltroDashboardDTO(
            empresa=self.empresa_atual,
            tipo_periodo=tipo_periodo,
            data_inicial=dt_ini,
            data_final=dt_fim,
            ano=ano,
            mes=mes,
            carregar_historico_completo=False
        )

        def _progresso_cb(pct: int, msg: str):
            try:
                if self.winfo_exists():
                    self.after(0, self._atualizar_gauge_progresso, pct, msg)
            except Exception:
                pass

        if not assincrono:
            self._carregando = True
            try:
                resumo = self.service.obter_dashboard(
                    filtro,
                    forcar_atualizacao=forcar,
                    callback_progresso=_progresso_cb
                )
                self._aplicar_dados_carregados(resumo)
            finally:
                self._carregando = False
            return

        self._carregando = True
        self._exibir_estado_carregando(tipo_sel)

        def _worker():
            try:
                resumo = self.service.obter_dashboard(
                    filtro,
                    forcar_atualizacao=forcar,
                    callback_progresso=_progresso_cb
                )
            except Exception as exc:
                logger.exception("Erro ao carregar dados do dashboard em segundo plano: %s", exc)
                resumo = ResumoDoacoesDTO(ano=ano, mes=mes)

            try:
                if self.winfo_exists():
                    self.after(0, self._aplicar_dados_carregados, resumo)
            except Exception:
                pass

        threading.Thread(target=_worker, daemon=True).start()

    def _exibir_estado_carregando(self, desc_periodo: str = ""):
        """Apresenta feedback visual imediato com o Gauge de progresso."""
        if hasattr(self, "lbl_status_carregamento"):
            self.lbl_status_carregamento.config(text=f"⏳ Filtrando {desc_periodo}...")
        if hasattr(self, "gauge_overlay"):
            self.gauge_overlay.exibir()
            self.gauge_overlay.atualizar(5, f"Iniciando consulta para {desc_periodo}...")
        if hasattr(self, "card_arrecadado"):
            self.card_arrecadado["val"].config(text="Carregando...")
            self.card_arrecadado["sub"].config(text="Calculando período...")
        if hasattr(self, "btn_atualizar"):
            self.btn_atualizar.config(state="disabled")
        if hasattr(self, "btn_filtrar"):
            self.btn_filtrar.config(state="disabled")
        if hasattr(self, "btn_sinc"):
            self.btn_sinc.config(state="disabled")

    def _aplicar_dados_carregados(self, resumo: ResumoDoacoesDTO):
        """Aplica os dados consolidados nos componentes visuais com thread safety."""
        self._carregando = False
        if hasattr(self, "lbl_status_carregamento"):
            self.lbl_status_carregamento.config(text=f"✅ {resumo.periodo_descricao} carregado com sucesso.")
        if hasattr(self, "btn_atualizar"):
            self.btn_atualizar.config(state="normal")
        if hasattr(self, "btn_filtrar"):
            self.btn_filtrar.config(state="normal")
        if hasattr(self, "btn_sinc"):
            self.btn_sinc.config(state="normal")

        self.resumo_atual = resumo
        self._todos_doadores = resumo.doadores

        self._atualizar_cards()
        self._desenhar_grafico_status()
        self._desenhar_grafico_formas()
        self._atualizar_tabela_dioceses()
        self._renderizar_insights_ia()
        self._aplicar_filtros_tabela()
        self._atualizar_aba_historica()

        # Conclusão e recolhimento do Gauge
        if hasattr(self, "gauge_overlay"):
            self.gauge_overlay.atualizar(100, "Dados carregados com sucesso!")
            self.after(350, self.gauge_overlay.ocultar)

    def _atualizar_cards(self):
        r = self.resumo_atual
        # Card Arrecadação
        self.card_arrecadado["val"].config(text=f"R$ {r.total_arrecadado:,.2f}")
        sinal = "+" if r.variacao_mes_anterior_pct >= 0 else ""
        sub_txt = f"{sinal}{r.variacao_mes_anterior_pct:.1f}% vs Mês Ant (R$ {r.total_mes_anterior:,.2f})" if r.total_mes_anterior > 0 else f"{r.periodo_descricao}"
        self.card_arrecadado["sub"].config(text=sub_txt)

        # Card Recorrentes
        self.card_recorrentes["val"].config(text=f"{r.qtd_recorrentes:,}")
        self.card_recorrentes["sub"].config(text=f"R$ {r.total_recorrentes:,.2f} ({((r.total_recorrentes / r.total_arrecadado)*100):.1f}%)" if r.total_arrecadado > 0 else "R$ 0,00")

        # Card Retorno
        self.card_retorno["val"].config(text=f"{r.qtd_retorno:,}")
        self.card_retorno["sub"].config(text=f"R$ {r.total_retorno:,.2f} ({((r.total_retorno / r.total_arrecadado)*100):.1f}%)" if r.total_arrecadado > 0 else "R$ 0,00")

        # Card Novos
        self.card_novos["val"].config(text=f"{r.qtd_novos:,}")
        self.card_novos["sub"].config(text=f"R$ {r.total_novos:,.2f} ({((r.total_novos / r.total_arrecadado)*100):.1f}%)" if r.total_arrecadado > 0 else "R$ 0,00")

        # Card Ticket Médio
        self.card_ticket["val"].config(text=f"R$ {r.ticket_medio:,.2f}")
        self.card_ticket["sub"].config(text=f"{r.qtd_doadores:,} doadores únicos no mês")

    def _desenhar_grafico_status(self):
        """Desenha barras verticais dos 3 status de doadores (Recorrente, Retorno, Novo)."""
        c = self.canvas_status
        c.delete("all")
        w = c.winfo_width() or 340
        h = c.winfo_height() or 160

        itens = self.resumo_atual.status_metricas
        if not itens:
            c.create_text(w / 2, h / 2, text="Sem dados de status", fill="#94A3B8", font=("Segoe UI", 9))
            return

        max_val = max((x.total for x in itens), default=1.0)
        if max_val <= 0:
            max_val = 1.0

        margem_esq = 45
        margem_dir = 20
        margem_sup = 20
        margem_inf = 32

        largura_util = w - margem_esq - margem_dir
        altura_util = h - margem_sup - margem_inf
        y_eixo = margem_sup + altura_util

        c.create_line(margem_esq, y_eixo, w - margem_dir, y_eixo, fill="#CBD5E1", width=1.5)

        espaco = largura_util / len(itens)
        largura_barra = min(espaco * 0.5, 42)

        for i, item in enumerate(itens):
            cx = margem_esq + (i * espaco) + (espaco / 2)
            x0 = cx - largura_barra / 2
            x1 = cx + largura_barra / 2
            alt = (item.total / max_val) * altura_util
            y0 = y_eixo - alt

            c.create_rectangle(x0, y0, x1, y_eixo, fill=item.cor, outline="#0F172A", width=1)

            # Rótulo de Valor
            val_txt = f"R${item.total/1000:.1f}k" if item.total >= 1000 else f"R${item.total:.0f}"
            c.create_text(cx, y0 - 8, text=f"{val_txt} ({item.percentual:.0f}%)", fill="#0F172A", font=("Segoe UI", 7, "bold"))

            # Rótulo do Status
            nome_curto = item.status.replace("Doador ", "")
            c.create_text(cx, y_eixo + 10, text=nome_curto, fill="#1E293B", font=("Segoe UI", 7, "bold"))
            c.create_text(cx, y_eixo + 21, text=f"{item.qtd} doações", fill="#64748B", font=("Segoe UI", 6))

    def _desenhar_grafico_formas(self):
        """Desenha barras horizontais com a participação das formas de contribuição."""
        c = self.canvas_formas
        c.delete("all")
        w = c.winfo_width() or 340
        h = c.winfo_height() or 160

        top_formas = self.resumo_atual.tipos_cobranca[:4]
        if not top_formas:
            c.create_text(w / 2, h / 2, text="Sem dados de formas de pagamento", fill="#94A3B8", font=("Segoe UI", 9))
            return

        margem_esq = 80
        margem_dir = 50
        margem_sup = 12
        espaco_y = (h - margem_sup * 2) / len(top_formas)
        altura_barra = min(espaco_y * 0.55, 18)

        cores = ["#1E40AF", "#059669", "#7C3AED", "#D97706"]

        for i, item in enumerate(top_formas):
            cy = margem_sup + i * espaco_y + espaco_y / 2
            y0 = cy - altura_barra / 2
            y1 = cy + altura_barra / 2

            # Código curto à esquerda
            cod_curto = item.codigo
            c.create_text(margem_esq - 6, cy, text=cod_curto, fill="#334155", font=("Segoe UI", 8, "bold"), anchor="e")

            largura_max = w - margem_esq - margem_dir
            largura_item = max((item.percentual / 100.0) * largura_max, 4)
            x0 = margem_esq
            x1 = margem_esq + largura_item

            cor = cores[i % len(cores)]
            c.create_rectangle(x0, y0, x1, y1, fill=cor, outline="", width=0)

            # Rótulo de % e R$ à direita
            c.create_text(x1 + 5, cy, text=f"{item.percentual:.1f}% (R$ {item.total/1000:.1f}k)", fill="#0F172A", font=("Segoe UI", 7, "bold"), anchor="w")

    def _atualizar_tabela_dioceses(self):
        for item in self.tree_dioceses.get_children():
            self.tree_dioceses.delete(item)

        for idx, d in enumerate(self.resumo_atual.top_dioceses):
            self.tree_dioceses.insert(
                "",
                tk.END,
                values=(
                    idx + 1,
                    d.nome,
                    d.uf,
                    f"{d.qtd:,}",
                    f"R$ {d.total:,.2f}",
                    f"{d.percentual:.1f}%",
                    f"R$ {d.ticket_medio:,.2f}",
                )
            )

    def _renderizar_insights_ia(self):
        for widget in self.ia_box.winfo_children():
            widget.destroy()

        if not self.resumo_atual.insights_ia:
            lbl = tk.Label(self.ia_box, text="Nenhum insight gerado no momento.", bg="#FFFFFF", fg="#94A3B8")
            lbl.pack(pady=10)
            return

        for ins in self.resumo_atual.insights_ia[:3]:
            card = tk.Frame(self.ia_box, bg="#F8FAFC", bd=1, relief=tk.SOLID, padx=8, pady=5)
            card.pack(fill=tk.X, pady=2)

            bar = tk.Frame(card, bg=ins.cor_destaque, width=4)
            bar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

            content = tk.Frame(card, bg="#F8FAFC")
            content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            top_line = tk.Frame(content, bg="#F8FAFC")
            top_line.pack(fill=tk.X)

            tk.Label(
                top_line,
                text=f"{ins.icone} {ins.titulo}",
                font=("Segoe UI", 8, "bold"),
                fg=ins.cor_destaque,
                bg="#F8FAFC"
            ).pack(side=tk.LEFT)

            tk.Label(
                top_line,
                text=ins.tipo,
                font=("Segoe UI", 6, "bold"),
                bg="#E2E8F0",
                fg="#475569",
                padx=4,
                pady=1
            ).pack(side=tk.RIGHT)

            tk.Label(
                content,
                text=ins.descricao,
                font=("Segoe UI", 7),
                fg="#334155",
                bg="#F8FAFC",
                justify=tk.LEFT,
                wraplength=460
            ).pack(anchor="w", pady=(2, 0))

    def _aplicar_filtros_tabela(self):
        """Filtra a Treeview de doadores da Aba 2 conforme Status, Forma e Termo de Busca."""
        st_sel = self.cbo_status.get()
        if st_sel == "Todos os Status":
            st_sel = "TODOS"

        fm_sel = self.cbo_forma.get()
        if fm_sel == "Todas":
            fm_sel = "TODAS"

        termo = self.txt_busca.get().strip().lower()

        filtrados = self.service._filtrar_doadores(
            self._todos_doadores,
            status_filtro=st_sel,
            forma_filtro=fm_sel,
            termo_busca=termo
        )

        for item in self.tree_doadores.get_children():
            self.tree_doadores.delete(item)

        total_filtrado = 0.0
        for d in filtrados:
            total_filtrado += d.valor_doado
            dt_c_str = d.data_doacao_mescorrente.strftime("%d/%m/%Y") if d.data_doacao_mescorrente else "-"
            dt_a_str = d.data_doacao_anterior.strftime("%d/%m/%Y") if d.data_doacao_anterior else "-"
            self.tree_doadores.insert(
                "",
                tk.END,
                values=(
                    d.entcod,
                    d.entnome,
                    d.uf,
                    d.diocese,
                    d.categnome,
                    d.forma_contribuicao,
                    f"R$ {d.valor_doado:,.2f}",
                    dt_c_str,
                    f"R$ {d.valor_doado_mesanterior:,.2f}",
                    dt_a_str,
                    d.status_doador,
                )
            )

        self.lbl_contador_doadores.config(
            text=f"Exibindo {len(filtrados):,} de {len(self._todos_doadores):,} doadores | Total Listado: R$ {total_filtrado:,.2f}"
        )

    def _atualizar_aba_historica(self):
        """Atualiza a tabela de histórico anual e desenha gráficos."""
        if hasattr(self, "lbl_evolucao_meses_tit"):
            self.lbl_evolucao_meses_tit.config(
                text=f"📈 Evolução Mensal da Arrecadação no Ano {self.resumo_atual.ano}"
            )

        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)

        for h in self.resumo_atual.historico_metodos:
            self.tree_historico.insert(
                "",
                tk.END,
                values=(
                    h.ano,
                    h.metodo_lider,
                    f"R$ {h.total_lider:,.2f}",
                    f"{h.pct_lider:.1f}%",
                    f"R$ {h.total_ano:,.2f}",
                    f"{h.qtd_ano:,}",
                    f"R$ {h.ticket_medio:,.2f}",
                )
            )

        self._desenhar_grafico_evolucao_meses()

    def _desenhar_grafico_evolucao_meses(self):
        """Desenha barras de evolução dos meses do ano selecionado."""
        if not hasattr(self, "canvas_evolucao_meses"):
            return
        c = self.canvas_evolucao_meses
        c.delete("all")
        w = c.winfo_width() or 340
        h = c.winfo_height() or 150

        dados = self.resumo_atual.evolucao_meses
        if not dados:
            c.create_text(w / 2, h / 2, text="Sem dados de evolução mensal", fill="#94A3B8", font=("Segoe UI", 9))
            return

        max_val = max((x.total for x in dados), default=1.0)
        if max_val <= 0:
            max_val = 1.0

        margem_esq = 55
        margem_dir = 20
        margem_sup = 20
        margem_inf = 30

        largura_util = w - margem_esq - margem_dir
        altura_util = h - margem_sup - margem_inf
        y_eixo = margem_sup + altura_util

        c.create_line(margem_esq, y_eixo, w - margem_dir, y_eixo, fill="#CBD5E1", width=1.5)

        qtd_meses = len(dados)
        espaco = largura_util / max(qtd_meses, 1)
        largura_barra = min(espaco * 0.55, 36)

        cores = [
            "#38BDF8", "#0EA5E9", "#0284C7", "#2563EB", "#1D4ED8",
            "#1E40AF", "#1E3A8A", "#059669", "#047857", "#D97706",
            "#B45309", "#7C3AED"
        ]

        for i, item in enumerate(dados):
            cx = margem_esq + (i * espaco) + (espaco / 2)
            x0 = cx - largura_barra / 2
            x1 = cx + largura_barra / 2
            alt = (item.total / max_val) * altura_util
            y0 = y_eixo - alt

            cor = cores[(item.mes - 1) % len(cores)]
            c.create_rectangle(x0, y0, x1, y_eixo, fill=cor, outline="#1E3A8A", width=1)

            # Rótulo de Valor
            val_txt = f"R${item.total/1000:.1f}k" if item.total >= 1000 else f"R${item.total:.0f}"
            c.create_text(cx, y0 - 8, text=val_txt, fill="#0F172A", font=("Segoe UI", 7, "bold"))

            # Rótulo do Mês
            nome_abrev = item.nome_mes[:3]
            c.create_text(cx, y_eixo + 10, text=nome_abrev, fill="#1E293B", font=("Segoe UI", 7, "bold"))
            c.create_text(cx, y_eixo + 20, text=f"{item.qtd} un", fill="#64748B", font=("Segoe UI", 6))

    def _desenhar_grafico_historico_lider(self):
        pass

    def _recalcular_ia(self):
        """Força o recálculo dos insights de IA."""
        self.resumo_atual.insights_ia = self.service.gerar_insights_ia(self.resumo_atual)
        self._renderizar_insights_ia()
        messagebox.showinfo("Inteligência Analítica", "Diagnósticos de IA recalculados com sucesso!", parent=self)

    def _sincronizar_procedure(self):
        """Executa a sincronização do perfil financeiro no banco via procedure oficial ou recarrega a consulta sob demanda."""
        ano = self.resumo_atual.ano
        mes = self.resumo_atual.mes

        resp = messagebox.askyesnocancel(
            "Sincronização com o Banco de Dados",
            f"Deseja executar a procedure de sincronização no banco ou apenas atualizar os dados do Dashboard?\n\n"
            f"• Sim: Executa a procedure USERPerfil_Financeiro_Doador no banco (Ano {ano}, Mês {mes}) e atualiza os dados.\n"
            f"• Não: Apenas recarrega/sincroniza a consulta do Dashboard diretamente do banco agora.\n"
            f"• Cancelar: Retorna sem realizar operações.",
            parent=self
        )
        if resp is None:
            return

        if resp:
            sucesso = self.service.sincronizar_perfil_mes(ano, mes, self.empresa_atual)
            if sucesso:
                messagebox.showinfo("Sucesso", f"Perfil financeiro do Ano {ano}, Mês {mes} sincronizado com sucesso no banco!", parent=self)
                self.carregar_dados(forcar=True, assincrono=True)
            else:
                messagebox.showerror("Erro", "Falha ao executar procedure de sincronização no banco de dados.", parent=self)
        else:
            self.carregar_dados(forcar=True, assincrono=True)

    def _exportar_relatorio_csv(self):
        """Exporta a relação completa de doadores e métricas para arquivo CSV."""
        if not self._todos_doadores:
            messagebox.showwarning("Aviso", "Não há registros de doadores para exportar.", parent=self)
            return

        caminho = filedialog.asksaveasfilename(
            title="Exportar Relação de Doadores (Dashboard)",
            defaultextension=".csv",
            filetypes=[("Arquivo CSV", "*.csv"), ("Todos os Arquivos", "*.*")],
            initialfile=f"dashboard_doadores_{self.resumo_atual.ano}_{self.resumo_atual.mes:02d}.csv"
        )
        if not caminho:
            return

        try:
            with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["--- RESUMO EXECUTIVO DO MÊS (RCC - EMPRESA 1.01) ---"])
                writer.writerow(["Período", self.resumo_atual.periodo_descricao])
                writer.writerow(["Arrecadação Total (R$)", f"{self.resumo_atual.total_arrecadado:.2f}".replace(".", ",")])
                writer.writerow(["Arrecadação Mês Anterior (R$)", f"{self.resumo_atual.total_mes_anterior:.2f}".replace(".", ",")])
                writer.writerow(["Variação vs Mês Anterior (%)", f"{self.resumo_atual.variacao_mes_anterior_pct:.1f}".replace(".", ",")])
                writer.writerow(["Total de Doações", self.resumo_atual.qtd_doacoes])
                writer.writerow(["Doadores Únicos", self.resumo_atual.qtd_doadores])
                writer.writerow(["Ticket Médio (R$)", f"{self.resumo_atual.ticket_medio:.2f}".replace(".", ",")])
                writer.writerow(["Doadores Recorrentes", self.resumo_atual.qtd_recorrentes, f"R$ {self.resumo_atual.total_recorrentes:.2f}".replace(".", ",")])
                writer.writerow(["Retorno de Doadores", self.resumo_atual.qtd_retorno, f"R$ {self.resumo_atual.total_retorno:.2f}".replace(".", ",")])
                writer.writerow(["Novos Doadores", self.resumo_atual.qtd_novos, f"R$ {self.resumo_atual.total_novos:.2f}".replace(".", ",")])
                writer.writerow([])

                writer.writerow(["--- RELAÇÃO DE DOADORES (Dashboard-menuprincipal.sql) ---"])
                writer.writerow([
                    "Código", "Nome Doador", "UF", "Cód Diocese", "Diocese",
                    "Cód Categoria", "Nome Categoria", "Cód Cobrança", "Forma Contribuição",
                    "Data Doação", "Valor Doado (R$)", "Data Anterior", "Valor Mês Anterior (R$)",
                    "Chave Doc", "Status Doador"
                ])
                for d in self._todos_doadores:
                    dt_c = d.data_doacao_mescorrente.strftime("%d/%m/%Y") if d.data_doacao_mescorrente else ""
                    dt_a = d.data_doacao_anterior.strftime("%d/%m/%Y") if d.data_doacao_anterior else ""
                    writer.writerow([
                        d.entcod,
                        d.entnome,
                        d.uf,
                        d.codigo_dio,
                        d.diocese,
                        d.categcodestr,
                        d.categnome,
                        d.tipocobcod,
                        d.forma_contribuicao,
                        dt_c,
                        f"{d.valor_doado:.2f}".replace(".", ","),
                        dt_a,
                        f"{d.valor_doado_mesanterior:.2f}".replace(".", ","),
                        d.docfinchv,
                        d.status_doador,
                    ])

            messagebox.showinfo("Exportação Concluída", f"Relatório exportado com sucesso em:\n{caminho}", parent=self)
        except Exception as exc:
            messagebox.showerror("Erro ao Exportar", f"Falha ao gravar arquivo CSV:\n{exc}", parent=self)


class DashboardDoacoesView(tk.Toplevel):
    """Janela independente e maximizada para visualização do Dashboard."""
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

    def __init__(self, parent=None, empresa: str = "1.01"):
        if getattr(self, "_ja_inicializada", False):
            return
        super().__init__(parent)
        self._ja_inicializada = True
        DashboardDoacoesView._instancia_ativa = self

        self.title("GeoAlvo - Dashboard de Doações & Inteligência Analítica (Empresa 1.01)")
        self.geometry("1180x740")
        self.minsize(980, 620)

        from core import centralizar_janela
        centralizar_janela(self, parent, 1180, 740)

        self.dash_frame = DashboardDoacoesFrame(self, empresa=empresa, auto_carregar=True)
        self.dash_frame.pack(fill=tk.BOTH, expand=True)

        self.bind("<Escape>", lambda e: self.destroy())

    def destroy(self):
        DashboardDoacoesView._instancia_ativa = None
        super().destroy()


def abrir_dashboard_doacoes(parent=None, empresa: str = "1.01"):
    """Abre a visualização do dashboard de doações."""
    return DashboardDoacoesView(parent=parent, empresa=empresa)
