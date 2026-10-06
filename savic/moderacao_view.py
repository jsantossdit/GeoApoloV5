"""
Interface Gráfica (Tkinter / ttk) para Moderação de Grupos de Oração SAVIC x Apolo.
Refatoração moderna de unt_moderagrupodeoracao.pas / .dfm do Delphi.
"""

import os
import sys
import logging
import threading
from datetime import datetime, date
from decimal import Decimal
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any, List

from core import (
    obter_caminho_recurso,
    centralizar_janela,
    aplicar_icone_janela,
    salvar_log_erro_executavel,
)
from savic.moderacao_models import (
    FiltroModeracaoDTO,
    CoordenadorModeracaoDTO,
    GrupoOracaoModeracaoDTO,
    FichaFinanceiraDTO,
    EntidadeApoloComparativoDTO,
)
from savic.moderacao_service import SavicModeracaoService

logger = logging.getLogger(__name__)


class SavicModeracaoGOView(tk.Toplevel):
    """
    Formulário de Moderação de Grupos de Oração SAVIC x Apolo.
    Equivalente a Tfrmmoderacaogrupodeoracao.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.title("Moderação de Grupos de Oração Savic x Apolo")
        self.geometry("1100x720")
        self.minsize(980, 600)

        centralizar_janela(self, parent, 1100, 720)
        aplicar_icone_janela(self)

        self._service = SavicModeracaoService()

        # Dados em memória
        self._estados: List[Any] = []
        self._dioceses: List[Any] = []
        self._cidades: List[Any] = []
        self._coordenadores: List[CoordenadorModeracaoDTO] = []
        self._grupos: List[GrupoOracaoModeracaoDTO] = []
        self._geocidcod_atual: Optional[str] = None
        self._coordenador_selecionado: Optional[CoordenadorModeracaoDTO] = None
        self._grupo_selecionado: Optional[GrupoOracaoModeracaoDTO] = None

        self._criar_interface()
        self._vincular_atalhos()

        # Carrega estados iniciais em thread de background
        self._carregar_estados_inicial()

    def _vincular_atalhos(self):
        """Associa atalhos de teclado F5, F6, F10 e Escape."""
        self.bind("<F5>", lambda e: self._abrir_ficha_financeira())
        self.bind("<F6>", lambda e: self._abrir_comparativo_apolo())
        self.bind("<F10>", lambda e: self.destroy())
        self.bind("<Escape>", lambda e: self.destroy())

    def _criar_interface(self):
        # -------------------------------------------------------------
        # Barra Superior / Título e Ações Principais
        # -------------------------------------------------------------
        top_frame = ttk.Frame(self, padding="6 6 6 2")
        top_frame.pack(fill=tk.X, side=tk.TOP)

        lbl_titulo = ttk.Label(
            top_frame,
            text="Moderação e Confronto de Grupos de Oração SAVIC x Apolo",
            font=("Arial", 12, "bold")
        )
        lbl_titulo.pack(side=tk.LEFT, padx=6)

        btn_fechar = ttk.Button(
            top_frame, text="Retornar (F10)", command=self.destroy
        )
        btn_fechar.pack(side=tk.RIGHT, padx=4)

        btn_exportar_ent = ttk.Button(
            top_frame, text="Exportar para Entidades", command=self._exportar_para_entidades
        )
        btn_exportar_ent.pack(side=tk.RIGHT, padx=4)

        btn_exportar_csv = ttk.Button(
            top_frame, text="Exportar CSV", command=self._exportar_dados
        )
        btn_exportar_csv.pack(side=tk.RIGHT, padx=4)

        btn_limpar = ttk.Button(
            top_frame, text="Limpar", command=self._limpar_campos
        )
        btn_limpar.pack(side=tk.RIGHT, padx=4)

        # -------------------------------------------------------------
        # Painel de Filtros em Cascata (UF -> Diocese -> Cidade -> Situação)
        # -------------------------------------------------------------
        filtro_frame = ttk.LabelFrame(self, text=" Filtros de Pesquisa e Localização ", padding="8")
        filtro_frame.pack(fill=tk.X, padx=10, pady=4)

        # Linha 1: UF, Diocese, Cidade
        row1 = ttk.Frame(filtro_frame)
        row1.pack(fill=tk.X, pady=2)

        ttk.Label(row1, text="Estado (UF):", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=(4, 2))
        self.cbo_uf = ttk.Combobox(row1, width=5, state="readonly")
        self.cbo_uf.pack(side=tk.LEFT, padx=(0, 10))
        self.cbo_uf.bind("<<ComboboxSelected>>", self._ao_mudar_uf)
        self.cbo_uf.bind("<KeyPress>", self._ao_teclar_uf)

        ttk.Label(row1, text="Diocese:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=(4, 2))
        self.cbo_diocese = ttk.Combobox(row1, width=32, state="readonly")
        self.cbo_diocese.pack(side=tk.LEFT, padx=(0, 10))
        self.cbo_diocese.bind("<<ComboboxSelected>>", self._ao_mudar_diocese)

        ttk.Label(row1, text="Cidade:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=(4, 2))
        self.cbo_cidade = ttk.Combobox(row1, width=28, state="readonly")
        self.cbo_cidade.pack(side=tk.LEFT, padx=(0, 10))
        self.cbo_cidade.bind("<<ComboboxSelected>>", lambda e: self.cbo_situacao.focus())

        # Linha 2: Situação do Grupo, Categoria Apolo, Botão Filtrar
        row2 = ttk.Frame(filtro_frame)
        row2.pack(fill=tk.X, pady=(4, 2))

        ttk.Label(row2, text="Situação:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=(4, 2))
        self.cbo_situacao = ttk.Combobox(
            row2,
            width=16,
            values=["HOMOLOGADO", "EM ANDAMENTO", "NÃO HOMOLOGADO", "TODOS"],
            state="readonly"
        )
        self.cbo_situacao.set("HOMOLOGADO")
        self.cbo_situacao.pack(side=tk.LEFT, padx=(0, 10))
        self.cbo_situacao.bind("<Return>", lambda e: self._executar_filtro())

        ttk.Label(row2, text="Categoria Apolo:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(4, 2))
        self.txt_categoria = ttk.Entry(row2, width=10)
        self.txt_categoria.insert(0, "02.001")
        self.txt_categoria.pack(side=tk.LEFT, padx=(0, 4))

        btn_buscar_categ = ttk.Button(row2, text="F4 Categoria", command=self._selecionar_categoria, width=12)
        btn_buscar_categ.pack(side=tk.LEFT, padx=(0, 15))

        self.btn_filtrar = ttk.Button(
            row2,
            text="🔍 Filtrar Grupos e Coordenadores",
            command=self._executar_filtro
        )
        self.btn_filtrar.pack(side=tk.LEFT, padx=6)

        # -------------------------------------------------------------
        # Divisor / Splitter com as duas Grids (Mestre-Detalhe)
        # -------------------------------------------------------------
        paned = ttk.Panedwindow(self, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        # === PAINEL 1: Coordenadores ===
        frame_coord = ttk.LabelFrame(
            paned,
            text=" Coordenadores de Grupos de Oração (SAVIC)  |  Atalho: [F5] Ficha Financeira ",
            padding="4"
        )
        paned.add(frame_coord, weight=3)

        colunas_coord = (
            "exportado", "id_savic", "cod_apolo", "coordenador", "cpf", "inicio", "fim",
            "indet", "telefones", "celular", "email", "bairro", "cep", "cidade", "uf"
        )
        self.grid_coord = ttk.Treeview(
            frame_coord,
            columns=colunas_coord,
            show="headings",
            selectmode="browse"
        )

        headers_coord = [
            ("exportado", "Exportado", 75, "center"),
            ("id_savic", "ID Savic", 65, "center"),
            ("cod_apolo", "Cód. Apolo", 75, "center"),
            ("coordenador", "Nome do Coordenador", 220, "w"),
            ("cpf", "CPF", 100, "center"),
            ("inicio", "Início", 75, "center"),
            ("fim", "Fim", 75, "center"),
            ("indet", "Indet.", 50, "center"),
            ("telefones", "Telefones", 100, "w"),
            ("celular", "Celular", 100, "w"),
            ("email", "E-mail", 160, "w"),
            ("bairro", "Bairro", 110, "w"),
            ("cep", "CEP", 80, "center"),
            ("cidade", "Cidade", 120, "w"),
            ("uf", "UF", 40, "center"),
        ]
        for col_id, titulo, larg, alin in headers_coord:
            self.grid_coord.heading(col_id, text=titulo)
            self.grid_coord.column(col_id, width=larg, anchor=alin)

        self.grid_coord.tag_configure("exportado", background="#FFF59D", foreground="#000000")

        scroll_y_coord = ttk.Scrollbar(frame_coord, orient=tk.VERTICAL, command=self.grid_coord.yview)
        scroll_x_coord = ttk.Scrollbar(frame_coord, orient=tk.HORIZONTAL, command=self.grid_coord.xview)
        self.grid_coord.configure(yscrollcommand=scroll_y_coord.set, xscrollcommand=scroll_x_coord.set)

        self.grid_coord.grid(row=0, column=0, sticky="nsew")
        scroll_y_coord.grid(row=0, column=1, sticky="ns")
        scroll_x_coord.grid(row=1, column=0, sticky="ew")

        frame_coord.rowconfigure(0, weight=1)
        frame_coord.columnconfigure(0, weight=1)

        self.grid_coord.bind("<<TreeviewSelect>>", self._ao_selecionar_coordenador)
        self.grid_coord.bind("<Double-1>", lambda e: self._abrir_ficha_financeira())

        # === PAINEL 2: Grupos de Oração do Coordenador ===
        frame_go = ttk.LabelFrame(
            paned,
            text=" Grupo de Oração Vinculado ao Coordenador  |  Atalhos: [F5] Ficha Fin.  |  [F6] Comparativo Apolo na Cidade ",
            padding="4"
        )
        paned.add(frame_go, weight=2)

        colunas_go = (
            "exportado", "gocodigo", "codigoapolo", "grupo", "local", "tipo_local",
            "dias", "horario", "situacao", "caracteristica", "dt_inclusao", "dt_atualizacao"
        )
        self.grid_go = ttk.Treeview(
            frame_go,
            columns=colunas_go,
            show="headings",
            selectmode="browse"
        )

        headers_go = [
            ("exportado", "Exportado", 75, "center"),
            ("gocodigo", "Cód. G.O.", 70, "center"),
            ("codigoapolo", "Cód. Apolo", 75, "center"),
            ("grupo", "Nome do Grupo de Oração", 240, "w"),
            ("local", "Local da Reunião", 180, "w"),
            ("tipo_local", "Tipo de Local", 110, "w"),
            ("dias", "Dias da Reunião", 110, "w"),
            ("horario", "Horário", 70, "center"),
            ("situacao", "Situação", 110, "center"),
            ("caracteristica", "Característica", 120, "w"),
            ("dt_inclusao", "Data Inclusão", 90, "center"),
            ("dt_atualizacao", "Últ. Atualização", 90, "center"),
        ]
        for col_id, titulo, larg, alin in headers_go:
            self.grid_go.heading(col_id, text=titulo)
            self.grid_go.column(col_id, width=larg, anchor=alin)

        self.grid_go.tag_configure("exportado", background="#FFF59D", foreground="#000000")

        scroll_y_go = ttk.Scrollbar(frame_go, orient=tk.VERTICAL, command=self.grid_go.yview)
        scroll_x_go = ttk.Scrollbar(frame_go, orient=tk.HORIZONTAL, command=self.grid_go.xview)
        self.grid_go.configure(yscrollcommand=scroll_y_go.set, xscrollcommand=scroll_x_go.set)

        self.grid_go.grid(row=0, column=0, sticky="nsew")
        scroll_y_go.grid(row=0, column=1, sticky="ns")
        scroll_x_go.grid(row=1, column=0, sticky="ew")

        frame_go.rowconfigure(0, weight=1)
        frame_go.columnconfigure(0, weight=1)

        self.grid_go.bind("<<TreeviewSelect>>", self._ao_selecionar_grupo)
        self.grid_go.bind("<Double-1>", lambda e: self._abrir_ficha_financeira())

        # -------------------------------------------------------------
        # Barra de Status Inferior
        # -------------------------------------------------------------
        self.status_bar = ttk.Frame(self, relief=tk.SUNKEN, padding="3")
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_status = ttk.Label(self.status_bar, text="Pronto para consulta. Selecione Estado, Diocese e Cidade.", font=("Arial", 8))
        self.lbl_status.pack(side=tk.LEFT, padx=6)

        self.lbl_totais = ttk.Label(self.status_bar, text="Coordenadores: 0 | Grupos: 0", font=("Arial", 8, "bold"))
        self.lbl_totais.pack(side=tk.RIGHT, padx=8)

    # -------------------------------------------------------------------------
    # Operações em Background e Carregamento de Combos
    # -------------------------------------------------------------------------
    def _carregar_estados_inicial(self):
        """Carrega lista de estados do banco em segundo plano."""
        def tarefa():
            try:
                estados = self._service.obter_estados()
                if self.winfo_exists():
                    self.after(0, lambda: self._atualizar_combo_estados(estados))
            except Exception as e:
                logger.error(f"Erro ao carregar estados: {e}")
                try:
                    if self.winfo_exists():
                        self.after(0, lambda: self._definir_status(f"Erro ao carregar estados: {e}"))
                except Exception:
                    pass

        threading.Thread(target=tarefa, daemon=True).start()

    def _atualizar_combo_estados(self, estados):
        self._estados = estados
        siglas = [""] + [e.sigla for e in estados]
        self.cbo_uf["values"] = siglas
        self.cbo_uf.set("")

    def _ao_teclar_uf(self, event):
        """Posiciona a combo no primeiro estado que inicia com a letra digitada."""
        char = (event.char or "").strip().upper()
        if not char or not char.isalpha():
            return
        vals = list(self.cbo_uf["values"])
        for idx, val in enumerate(vals):
            if val and str(val).strip().upper().startswith(char):
                self.cbo_uf.current(idx)
                self._ao_mudar_uf()
                return "break"

    def _ao_mudar_uf(self, event=None):
        """Disparado quando o usuário escolhe uma UF: limpa diocese e cidade e busca dioceses."""
        uf = self.cbo_uf.get().strip().upper()
        self.cbo_diocese.set("")
        self.cbo_diocese["values"] = []
        self.cbo_cidade.set("")
        self.cbo_cidade["values"] = []

        if not uf:
            self._definir_status("Filtro de Estado limpo.")
            return

        self._definir_status(f"Carregando dioceses do estado {uf}...")

        def tarefa():
            try:
                dioceses = self._service.obter_dioceses(uf)
                self.after(0, lambda: self._atualizar_combo_dioceses(dioceses))
            except Exception as e:
                logger.error(f"Erro ao carregar dioceses: {e}")
                self.after(0, lambda: self._definir_status(f"Erro ao carregar dioceses: {e}"))

        threading.Thread(target=tarefa, daemon=True).start()

    def _atualizar_combo_dioceses(self, dioceses):
        self._dioceses = dioceses
        nomes = [""] + [d.nome for d in dioceses]
        self.cbo_diocese["values"] = nomes
        self.cbo_diocese.set("")
        self._definir_status(f"{len(dioceses)} diocese(s) encontrada(s).")

    def _ao_mudar_diocese(self, event=None):
        """Disparado quando a diocese é selecionada: busca cidades vinculadas."""
        diocese_nome = self.cbo_diocese.get().strip()
        self.cbo_cidade.set("")
        self.cbo_cidade["values"] = []

        if not diocese_nome:
            return

        self._definir_status(f"Carregando cidades da diocese '{diocese_nome}'...")

        def tarefa():
            try:
                cidades = self._service.obter_cidades_diocese(diocese_nome)
                self.after(0, lambda: self._atualizar_combo_cidades(cidades))
            except Exception as e:
                logger.error(f"Erro ao carregar cidades: {e}")
                self.after(0, lambda: self._definir_status(f"Erro ao carregar cidades: {e}"))

        threading.Thread(target=tarefa, daemon=True).start()

    def _atualizar_combo_cidades(self, cidades):
        self._cidades = cidades
        descricoes = [""] + [c.descricao for c in cidades]
        self.cbo_cidade["values"] = descricoes
        self.cbo_cidade.set("")
        self._definir_status(f"{len(cidades)} cidade(s) na diocese.")

    # -------------------------------------------------------------------------
    # Filtro e Consulta Principal
    # -------------------------------------------------------------------------
    def _executar_filtro(self):
        """Valida campos (opcionais) e pesquisa os coordenadores e grupos de oração."""
        uf = self.cbo_uf.get().strip()
        diocese = self.cbo_diocese.get().strip()
        cidade = self.cbo_cidade.get().strip()
        situacao = self.cbo_situacao.get().strip()
        categoria = self.txt_categoria.get().strip() or "02.001"

        filtro = FiltroModeracaoDTO(
            uf=uf,
            diocese_nome=diocese,
            cidade_nome=cidade,
            situacao_grupo=situacao,
            categoria_apolo=categoria,
        )

        msg_filtro = "Filtrando registros"
        if cidade:
            msg_filtro += f" em {cidade}"
        if uf:
            msg_filtro += f" ({uf})"
        if situacao and situacao != "TODOS":
            msg_filtro += f" [Situação: {situacao}]"
        self._definir_status(f"{msg_filtro}...")
        self.btn_filtrar.config(state="disabled")

        def tarefa():
            try:
                geocidcod, lista_coords, msg = self._service.filtrar_coordenadores(filtro)
                self.after(0, lambda: self._exibir_resultado_coordenadores(geocidcod, lista_coords, msg))
            except Exception as e:
                logger.error(f"Erro ao filtrar coordenadores: {e}")
                self.after(0, lambda: self._exibir_erro_filtro(str(e)))

        threading.Thread(target=tarefa, daemon=True).start()

    def _exibir_resultado_coordenadores(self, geocidcod, lista_coords, msg):
        self.btn_filtrar.config(state="normal")
        self._geocidcod_atual = geocidcod
        self._coordenadores = lista_coords

        # Limpa grids
        for item in self.grid_coord.get_children():
            self.grid_coord.delete(item)
        for item in self.grid_go.get_children():
            self.grid_go.delete(item)

        self._coordenador_selecionado = None
        self._grupo_selecionado = None

        for c in lista_coords:
            dt_ini_str = c.data_inicio.strftime("%d/%m/%Y") if c.data_inicio else ""
            dt_fim_str = c.data_fim.strftime("%d/%m/%Y") if c.data_fim else ""
            tels = f"{c.telefone_fixo} {c.telefone_comercial}".strip()

            tags = ("exportado",) if (c.flagexportado or "").strip().upper() == "SIM" else ()

            self.grid_coord.insert(
                "",
                tk.END,
                iid=c.id_savic,
                values=(
                    c.flagexportado,
                    c.id_savic,
                    c.codigo_apolo,
                    c.coordenador,
                    c.cpf,
                    dt_ini_str,
                    dt_fim_str,
                    c.mandato_indeterminado,
                    tels,
                    c.celular,
                    c.email,
                    c.bairro,
                    c.cep,
                    c.cidade,
                    c.uf,
                ),
                tags=tags
            )

        self._definir_status(msg)
        self.lbl_totais.config(text=f"Coordenadores: {len(lista_coords)} | Grupos: 0")

        # Seleciona o primeiro coordenador se houver
        if lista_coords:
            primeiro_id = lista_coords[0].id_savic
            self.grid_coord.selection_set(primeiro_id)
            self.grid_coord.focus(primeiro_id)
            self._ao_selecionar_coordenador()

    def _exibir_erro_filtro(self, erro_msg):
        self.btn_filtrar.config(state="normal")
        messagebox.showerror("Erro no Filtro", erro_msg, parent=self)
        self._definir_status(f"Falha: {erro_msg}")

    # -------------------------------------------------------------------------
    # Seleção Mestre-Detalhe (Coordenador -> Grupos de Oração)
    # -------------------------------------------------------------------------
    def _ao_selecionar_coordenador(self, event=None):
        """Ao clicar em um coordenador, pesquisa seus grupos de oração."""
        sel = self.grid_coord.selection()
        if not sel:
            return

        id_savic = sel[0]
        self._coordenador_selecionado = next((c for c in self._coordenadores if c.id_savic == id_savic), None)

        def tarefa():
            try:
                grupos = self._service.obter_grupos_do_coordenador(id_savic)
                self.after(0, lambda: self._exibir_grupos_do_coordenador(grupos))
            except Exception as e:
                logger.error(f"Erro ao buscar grupos do coordenador {id_savic}: {e}")

        threading.Thread(target=tarefa, daemon=True).start()

    def _exibir_grupos_do_coordenador(self, grupos):
        self._grupos = grupos
        for item in self.grid_go.get_children():
            self.grid_go.delete(item)

        self._grupo_selecionado = None

        for g in grupos:
            dt_inc_str = g.data_inclusao_savic.strftime("%d/%m/%Y") if g.data_inclusao_savic else ""
            dt_atu_str = g.ultima_atualizacao.strftime("%d/%m/%Y") if g.ultima_atualizacao else ""

            tags = ("exportado",) if (g.flagexportado or "").strip().upper() == "SIM" else ()

            self.grid_go.insert(
                "",
                tk.END,
                iid=g.gocodigo,
                values=(
                    g.flagexportado,
                    g.gocodigo,
                    g.codigo_apolo,
                    g.nome_grupo,
                    g.local_reuniao,
                    g.tipo_local,
                    g.dias_reuniao,
                    g.horario,
                    g.situacao_grupo,
                    g.caracteristica_grupo,
                    dt_inc_str,
                    dt_atu_str,
                ),
                tags=tags
            )

        total_coords = len(self._coordenadores)
        total_grupos = len(grupos)
        self.lbl_totais.config(text=f"Coordenadores: {total_coords} | Grupos: {total_grupos}")

        if grupos:
            self.grid_go.selection_set(grupos[0].gocodigo)
            self._grupo_selecionado = grupos[0]

    def _ao_selecionar_grupo(self, event=None):
        sel = self.grid_go.selection()
        if not sel:
            return
        gocodigo = sel[0]
        self._grupo_selecionado = next((g for g in self._grupos if g.gocodigo == gocodigo), None)

    # -------------------------------------------------------------------------
    # Atalho F5: Ficha Financeira (Histórico de Doações)
    # -------------------------------------------------------------------------
    def _abrir_ficha_financeira(self):
        """
        Abre a Ficha Financeira para a entidade selecionada (coordenador ou grupo de oração).
        """
        codigo_apolo = ""
        nome_entidade = ""

        # Prioriza o grupo selecionado se houver foco na grid de grupos, senão o coordenador
        foco = self.focus_get()
        if foco == self.grid_go and self._grupo_selecionado:
            codigo_apolo = self._grupo_selecionado.codigo_apolo
            nome_entidade = self._grupo_selecionado.nome_grupo
        elif self._coordenador_selecionado:
            codigo_apolo = self._coordenador_selecionado.codigo_apolo
            nome_entidade = self._coordenador_selecionado.coordenador
        elif self._grupo_selecionado:
            codigo_apolo = self._grupo_selecionado.codigo_apolo
            nome_entidade = self._grupo_selecionado.nome_grupo

        if not codigo_apolo or codigo_apolo.strip() in ("", "0"):
            messagebox.showinfo(
                "Ficha Financeira",
                "O registro selecionado ainda não possui código de entidade vinculado no Apolo.",
                parent=self
            )
            return

        # Abre modal com os lançamentos de parc_doc_fin
        self._exibir_modal_ficha_financeira(codigo_apolo.strip(), nome_entidade)

    def _exibir_modal_ficha_financeira(self, entcod: str, nome: str):
        modal = tk.Toplevel(self)
        modal.title(f"Ficha Financeira da Entidade - Cód: {entcod}")
        modal.geometry("750x420")
        centralizar_janela(modal, self, 750, 420)
        aplicar_icone_janela(modal)
        modal.grab_set()

        top_info = ttk.Frame(modal, padding="10")
        top_info.pack(fill=tk.X)

        ttk.Label(top_info, text=f"Entidade: {entcod} - {nome}", font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Label(top_info, text="Histórico de Contribuições e Doações (parc_doc_fin)", font=("Arial", 9)).pack(anchor="w")

        # Treeview de dados financeiros
        cols = ("empresa", "tipocob_cod", "tipocob_nome", "primeiro", "ultimo", "total")
        grid_fin = ttk.Treeview(modal, columns=cols, show="headings")

        grid_fin.heading("empresa", text="Empresa")
        grid_fin.heading("tipocob_cod", text="Cód. Cobr.")
        grid_fin.heading("tipocob_nome", text="Tipo de Cobrança")
        grid_fin.heading("primeiro", text="Primeira Doação")
        grid_fin.heading("ultimo", text="Última Doação")
        grid_fin.heading("total", text="Valor Total Doado (R$)")

        grid_fin.column("empresa", width=70, anchor="center")
        grid_fin.column("tipocob_cod", width=80, anchor="center")
        grid_fin.column("tipocob_nome", width=180, anchor="w")
        grid_fin.column("primeiro", width=110, anchor="center")
        grid_fin.column("ultimo", width=110, anchor="center")
        grid_fin.column("total", width=130, anchor="e")

        grid_fin.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        lbl_total_geral = ttk.Label(modal, text="Total Geral Doado: R$ 0,00", font=("Arial", 10, "bold"), padding="8")
        lbl_total_geral.pack(side=tk.LEFT)

        btn_fechar = ttk.Button(modal, text="Fechar (Esc)", command=modal.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=10, pady=8)

        modal.bind("<Escape>", lambda e: modal.destroy())

        def carregar():
            try:
                dados = self._service.obter_ficha_financeira(entcod)
                total_geral = Decimal("0.00")
                for d in dados:
                    p_str = d.primeiro_registro.strftime("%d/%m/%Y") if d.primeiro_registro else ""
                    u_str = d.ultimo_registro.strftime("%d/%m/%Y") if d.ultimo_registro else ""
                    vr_str = f"R$ {d.vr_total_doado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                    total_geral += d.vr_total_doado
                    grid_fin.insert("", tk.END, values=(
                        d.empresa, d.tipo_cobranca_cod, d.tipo_cobranca_nome, p_str, u_str, vr_str
                    ))
                tot_fmt = f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                lbl_total_geral.config(text=f"Total Geral Doado: {tot_fmt}")
            except Exception as exc:
                logger.error(f"Erro ao carregar ficha financeira: {exc}")

        threading.Thread(target=carregar, daemon=True).start()

    # -------------------------------------------------------------------------
    # Atalho F6: Comparativo de Grupos na Cidade (Apolo x Savic)
    # -------------------------------------------------------------------------
    def _abrir_comparativo_apolo(self):
        """
        Abre o comparativo com as entidades cadastradas no Apolo na mesma cidade (categoria 02.001%).
        """
        cidcod = self._geocidcod_atual
        if not cidcod:
            # Tenta resolver pelo grupo selecionado
            if self._grupo_selecionado and self._grupo_selecionado.geocidcod:
                cidcod = self._grupo_selecionado.geocidcod

        if not cidcod:
            messagebox.showwarning(
                "Comparativo Apolo",
                "É necessário filtrar uma cidade antes de consultar o comparativo do Apolo.",
                parent=self
            )
            return

        cidade_nome = self.cbo_cidade.get().strip()
        categoria = self.txt_categoria.get().strip() or "02.001"

        modal = tk.Toplevel(self)
        modal.title(f"Comparativo de Grupos no Apolo - {cidade_nome} (Cód: {cidcod})")
        modal.geometry("920x540")
        centralizar_janela(modal, self, 920, 540)
        aplicar_icone_janela(modal)
        modal.grab_set()

        top_info = ttk.Frame(modal, padding="10")
        top_info.pack(fill=tk.X)

        ttk.Label(
            top_info,
            text=f"Entidades Apolo na Cidade '{cidade_nome}' (Categoria: {categoria}%)",
            font=("Arial", 10, "bold")
        ).pack(anchor="w")

        # Split: Superior Grid Apolo, Inferior Detalhes Lado a Lado
        paned = ttk.Panedwindow(modal, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        cols = ("entcod", "trat", "entnome", "lograd", "endereco", "numero", "bairro", "cep")
        grid_apolo = ttk.Treeview(paned, columns=cols, show="headings", selectmode="browse")

        grid_apolo.heading("entcod", text="Cód. Apolo")
        grid_apolo.heading("trat", text="Trat.")
        grid_apolo.heading("entnome", text="Nome da Entidade no Apolo")
        grid_apolo.heading("lograd", text="Logradouro")
        grid_apolo.heading("endereco", text="Endereço")
        grid_apolo.heading("numero", text="Nº")
        grid_apolo.heading("bairro", text="Bairro")
        grid_apolo.heading("cep", text="CEP")

        grid_apolo.column("entcod", width=80, anchor="center")
        grid_apolo.column("trat", width=50, anchor="center")
        grid_apolo.column("entnome", width=220, anchor="w")
        grid_apolo.column("lograd", width=70, anchor="w")
        grid_apolo.column("endereco", width=180, anchor="w")
        grid_apolo.column("numero", width=50, anchor="center")
        grid_apolo.column("bairro", width=120, anchor="w")
        grid_apolo.column("cep", width=80, anchor="center")

        paned.add(grid_apolo, weight=3)

        # Painel Inferior: Detalhes Lado a Lado (SAVIC x APOLO)
        frame_detalhes = ttk.Frame(paned, padding="4")
        paned.add(frame_detalhes, weight=2)

        lbl_savic = ttk.Label(frame_detalhes, text="[ Dados SAVIC Selecionado ]", font=("Arial", 9, "bold"))
        lbl_savic.grid(row=0, column=0, sticky="w", padx=4)

        lbl_apolo = ttk.Label(frame_detalhes, text="[ Dados APOLO Selecionado ]", font=("Arial", 9, "bold"))
        lbl_apolo.grid(row=0, column=1, sticky="w", padx=4)

        txt_savic = tk.Text(frame_detalhes, height=7, width=48, font=("Consolas", 8))
        txt_savic.grid(row=1, column=0, sticky="nsew", padx=4, pady=2)

        txt_apolo = tk.Text(frame_detalhes, height=7, width=48, font=("Consolas", 8))
        txt_apolo.grid(row=1, column=1, sticky="nsew", padx=4, pady=2)

        frame_detalhes.columnconfigure(0, weight=1)
        frame_detalhes.columnconfigure(1, weight=1)
        frame_detalhes.rowconfigure(1, weight=1)

        # Preenche dados do SAVIC atual
        if self._grupo_selecionado:
            g = self._grupo_selecionado
            texto_s = (
                f"Código G.O. SAVIC: {g.gocodigo}\n"
                f"Código Apolo: {g.codigo_apolo}\n"
                f"Nome Grupo: {g.nome_grupo}\n"
                f"Local Reunião: {g.local_reuniao} ({g.tipo_local})\n"
                f"Endereço: {g.endereco}, Nº {g.numero} - {g.bairro}\n"
                f"CEP: {g.cep} | Cidade: {g.cidade} - {g.uf}\n"
                f"Situação: {g.situacao_grupo} | Dias: {g.dias_reuniao} às {g.horario}"
            )
            txt_savic.insert(tk.END, texto_s)
            txt_savic.config(state="disabled")

        entidades_apolo: List[EntidadeApoloComparativoDTO] = []

        def ao_selecionar_apolo(ev=None):
            sel = grid_apolo.selection()
            if not sel:
                return
            entcod_sel = sel[0]
            ent = next((e for e in entidades_apolo if e.entcod == entcod_sel), None)
            if ent:
                txt_apolo.config(state="normal")
                txt_apolo.delete("1.0", tk.END)
                texto_a = (
                    f"Código Apolo: {ent.entcod}\n"
                    f"Tratamento: {ent.tipotratcod}\n"
                    f"Nome Entidade: {ent.entnome}\n"
                    f"Endereço: {ent.entlograd} {ent.entender}, Nº {ent.entenderno}\n"
                    f"Complemento: {ent.entendercomp} | Bairro: {ent.entbair}\n"
                    f"CEP: {ent.entcep}\n"
                    f"Cidade: {ent.cidade} - {ent.uf}"
                )
                txt_apolo.insert(tk.END, texto_a)
                txt_apolo.config(state="disabled")

        grid_apolo.bind("<<TreeviewSelect>>", ao_selecionar_apolo)

        btn_box = ttk.Frame(modal, padding="6")
        btn_box.pack(fill=tk.X)
        btn_fechar = ttk.Button(btn_box, text="Fechar (Esc)", command=modal.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=6)

        modal.bind("<Escape>", lambda e: modal.destroy())

        def carregar():
            nonlocal entidades_apolo
            try:
                entidades_apolo = self._service.obter_comparativo_apolo(cidcod, categoria)
                for e in entidades_apolo:
                    grid_apolo.insert("", tk.END, iid=e.entcod, values=(
                        e.entcod, e.tipotratcod, e.entnome, e.entlograd, e.entender, e.entenderno, e.entbair, e.entcep
                    ))
            except Exception as exc:
                logger.error(f"Erro ao carregar comparativo Apolo: {exc}")

        threading.Thread(target=carregar, daemon=True).start()

    # -------------------------------------------------------------------------
    # Seleção de Categoria (F4)
    # -------------------------------------------------------------------------
    def _selecionar_categoria(self):
        """Abre janela para escolha de categoria de grupos de oração (F4)."""
        modal = tk.Toplevel(self)
        modal.title("Selecionar Categoria de Entidade")
        modal.geometry("450x320")
        centralizar_janela(modal, self, 450, 320)
        aplicar_icone_janela(modal)
        modal.grab_set()

        ttk.Label(modal, text="Categorias Disponíveis:", font=("Arial", 9, "bold"), padding="6").pack(anchor="w")

        cols = ("codigo", "nome")
        grid_cat = ttk.Treeview(modal, columns=cols, show="headings", selectmode="browse")
        grid_cat.heading("codigo", text="Código Estruturado")
        grid_cat.heading("nome", text="Descrição da Categoria")
        grid_cat.column("codigo", width=120, anchor="center")
        grid_cat.column("nome", width=280, anchor="w")
        grid_cat.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        try:
            cats = self._service.obter_categorias_elegiveis()
            for c in cats:
                grid_cat.insert("", tk.END, iid=c["codigo"], values=(c["codigo"], c["nome"]))
        except Exception as e:
            logger.error(f"Erro ao listar categorias: {e}")

        def selecionar():
            sel = grid_cat.selection()
            if sel:
                self.txt_categoria.delete(0, tk.END)
                self.txt_categoria.insert(0, sel[0])
                modal.destroy()

        btn_box = ttk.Frame(modal, padding="6")
        btn_box.pack(fill=tk.X)
        ttk.Button(btn_box, text="Confirmar", command=selecionar).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_box, text="Cancelar", command=modal.destroy).pack(side=tk.RIGHT, padx=4)
        grid_cat.bind("<Double-1>", lambda e: selecionar())

    # -------------------------------------------------------------------------
    # Exportação de Dados e Limpeza
    # -------------------------------------------------------------------------
    def _exportar_para_entidades(self):
        """Exporta os registros filtrados para a tabela USER_geoapolo_entidade."""
        if not self._coordenadores:
            messagebox.showinfo("Exportar", "Não há registros filtrados para exportação.", parent=self)
            return

        confirma = messagebox.askyesno(
            "Exportação para Entidades",
            f"Deseja realizar a exportação dos {len(self._coordenadores)} coordenador(es) "
            f"e seus grupos de oração para a tabela de Entidades do GeoAlvo/Apolo?\n\n"
            f"• Coordenadores serão gravados com Categoria: 02.001.0006\n"
            f"• Grupos de Oração serão gravados com Categoria: 02.001\n"
            f"• Os registros exportados serão marcados como 'Sim' e destacados em amarelo.",
            parent=self
        )
        if not confirma:
            return

        self._definir_status("Iniciando exportação para Entidades...")

        def tarefa():
            conn_thread = None
            try:
                def progresso(passo, total, texto):
                    self.after(0, lambda: self._definir_status(texto))

                try:
                    from entidades.database import obter_conexao_banco
                    conn_thread = obter_conexao_banco()
                except Exception as ex_conn:
                    logger.warning("Não foi possível abrir conexão dedicada para a exportação, usando conexão padrão: %s", ex_conn)
                    conn_thread = None

                resultado = self._service.exportar_entidades_selecionadas(
                    coordenadores=self._coordenadores,
                    grupos=None,
                    empresa_codigo="1.01",
                    callback_progresso=progresso,
                    connection=conn_thread,
                )
                self.after(0, lambda: self._pos_exportacao_entidades(resultado))
            except Exception as e:
                logger.exception("Erro durante exportação: %s", e)
                caminho_log = salvar_log_erro_executavel(
                    nome_arquivo="exportacao_erro.log",
                    titulo="Moderação SAVIC - Exportação para Entidades",
                    erro=e,
                    contexto=f"Total de coordenadores na lista: {len(self._coordenadores)}"
                )
                msg_erro = (
                    f"Ocorreu um erro durante a exportação:\n{e}\n\n"
                    f"Os detalhes técnicos e o histórico de execução foram salvos em:\n"
                    f"{caminho_log}"
                )
                self.after(0, lambda m=msg_erro: self._tratar_falha_exportacao(m))
            finally:
                if conn_thread is not None:
                    try:
                        conn_thread.close()
                    except Exception:
                        pass

        threading.Thread(target=tarefa, daemon=True).start()

    def _tratar_falha_exportacao(self, msg_erro: str):
        self._definir_status("Falha na exportação para Entidades.")
        messagebox.showerror("Erro na Exportação", msg_erro, parent=self)

    def _pos_exportacao_entidades(self, resultado):
        self._definir_status(resultado.mensagem)
        if resultado.sucesso:
            messagebox.showinfo("Sucesso na Exportação", resultado.mensagem, parent=self)
        else:
            if resultado.erros:
                caminho_log = salvar_log_erro_executavel(
                    nome_arquivo="exportacao_erro.log",
                    titulo="Moderação SAVIC - Erros em Lote na Exportação",
                    erro=RuntimeError(f"{len(resultado.erros)} erro(s) encontrados durante o processamento em lote."),
                    contexto="\n".join(resultado.erros)
                )
            else:
                caminho_log = ""

            erros_str = "\n".join(resultado.erros[:5])
            complemento_log = f"\n\nLog completo registrado em:\n{caminho_log}" if caminho_log else ""
            messagebox.showwarning(
                "Exportação com Pendências",
                f"{resultado.mensagem}\n\nPrincipais pendências:\n{erros_str}{complemento_log}",
                parent=self
            )
        # Recarrega a consulta atual para refletir o status amarelo de 'Sim'
        self._executar_filtro()

    def _exportar_dados(self):
        """Exporta os coordenadores exibidos para arquivo CSV ou Excel."""
        if not self._coordenadores:
            messagebox.showinfo("Exportar", "Não há registros filtrados para exportação.", parent=self)
            return

        caminho = filedialog.asksaveasfilename(
            parent=self,
            title="Salvar Relação de Coordenadores e Grupos",
            defaultextension=".csv",
            filetypes=[("Arquivo CSV", "*.csv"), ("Todos os Arquivos", "*.*")]
        )
        if not caminho:
            return

        try:
            import csv
            with open(caminho, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([
                    "ID Savic", "Código Apolo", "Coordenador", "CPF", "Início Mandato",
                    "Fim Mandato", "Mandato Indeterminado", "Telefones", "Celular",
                    "E-mail", "Bairro", "CEP", "Cidade", "UF"
                ])
                for c in self._coordenadores:
                    dt_ini = c.data_inicio.strftime("%d/%m/%Y") if c.data_inicio else ""
                    dt_fim = c.data_fim.strftime("%d/%m/%Y") if c.data_fim else ""
                    tels = f"{c.telefone_fixo} {c.telefone_comercial}".strip()
                    writer.writerow([
                        c.id_savic, c.codigo_apolo, c.coordenador, c.cpf, dt_ini, dt_fim,
                        c.mandato_indeterminado, tels, c.celular, c.email, c.bairro,
                        c.cep, c.cidade, c.uf
                    ])
            messagebox.showinfo("Sucesso", f"Dados exportados com sucesso para:\n{caminho}", parent=self)
        except Exception as exc:
            logger.error(f"Erro ao exportar dados: {exc}")
            messagebox.showerror("Erro de Exportação", f"Falha ao exportar arquivo:\n{exc}", parent=self)

    def _limpar_campos(self):
        """Reseta filtros e limpa tabelas."""
        for item in self.grid_coord.get_children():
            self.grid_coord.delete(item)
        for item in self.grid_go.get_children():
            self.grid_go.delete(item)
        self._coordenadores.clear()
        self._grupos.clear()
        self._geocidcod_atual = None
        self._coordenador_selecionado = None
        self._grupo_selecionado = None
        self.lbl_totais.config(text="Coordenadores: 0 | Grupos: 0")
        self._definir_status("Campos e consultas resetados.")

    def _definir_status(self, texto: str):
        self.lbl_status.config(text=texto)


def abrir_moderacao_go_savic(parent=None):
    """Função utilitária para abrir a janela de Moderação a partir de menus."""
    janela = SavicModeracaoGOView(parent=parent)
    return janela
