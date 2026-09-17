"""
Interface Gráfica para Gestão de CRM, Campanhas, Tratamentos e Ocorrências.
GeoApolo V5
Clean Architecture: View desacoplada baseada em Tkinter e ttk.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from .models import (
    TipoCampanhaDTO,
    TipoTratamentoDTO,
    OcorrenciaDTO,
    MotivoOcorrenciaDTO,
    OrigemDTO,
    SolicitanteDTO,
    ResultadoCRM,
)
from .service import CRMService


class CRMView(ttk.Frame):
    """View principal do CRM com abas para Ocorrências, Tipos de Campanha e Tratamento."""

    def __init__(
        self,
        parent=None,
        service: Optional[CRMService] = None,
        connection=None,
        codigo_empresa: str = "01",
        usuario_atual: str = "ADMIN",
    ):
        super().__init__(parent)
        self.service = service
        self.codigo_empresa = codigo_empresa
        self.usuario_atual = usuario_atual

        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from .repository import CRMRepository
                conn = connection or obter_conexao_banco()
                self.service = CRMService(CRMRepository(conn))
            except Exception:
                pass

        self._setup_ui()
        if self.service:
            self.recarregar_dados()

    def _setup_ui(self):
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        lbl_titulo = ttk.Label(
            header,
            text="Gestão de CRM & Ocorrências",
            font=("Segoe UI", 13, "bold"),
            foreground="#1E3A8A",
        )
        lbl_titulo.pack(side=tk.LEFT)

        lbl_sub = ttk.Label(
            header,
            text="Central de Ocorrências, Tipos de Campanha e Procedimentos de Atendimento",
            font=("Segoe UI", 9),
            foreground="#6B7280",
        )
        lbl_sub.pack(side=tk.LEFT, padx=15)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Abas
        self.tab_ocorrencias = ttk.Frame(self.notebook, padding=10)
        self.tab_campanhas = ttk.Frame(self.notebook, padding=10)
        self.tab_tratamentos = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_ocorrencias, text="  Ocorrências e Chamados  ")
        self.notebook.add(self.tab_campanhas, text="  Tipos de Campanha  ")
        self.notebook.add(self.tab_tratamentos, text="  Tipos de Tratamento  ")

        self._setup_aba_ocorrencias()
        self._setup_aba_campanhas()
        self._setup_aba_tratamentos()

    # =========================================================================
    # ABA 1: OCORRÊNCIAS
    # =========================================================================

    def _setup_aba_ocorrencias(self):
        # Filtros de status
        bar_filtro = ttk.Frame(self.tab_ocorrencias)
        bar_filtro.pack(fill=tk.X, pady=(0, 8))

        self.var_status_filtro = tk.StringVar(value="")
        lbl_st = ttk.Label(bar_filtro, text="Status:", font=("Segoe UI", 9, "bold"))
        lbl_st.pack(side=tk.LEFT, padx=(0, 5))

        for text, val in [
            ("Todas", ""),
            ("Pendente", "Pendente"),
            ("Em Andamento", "Em Andamento"),
            ("Resolvido", "Resolvido"),
            ("Cancelado", "Cancelado"),
        ]:
            rb = ttk.Radiobutton(
                bar_filtro,
                text=text,
                value=val,
                variable=self.var_status_filtro,
                command=self._ao_mudar_filtro_status,
            )
            rb.pack(side=tk.LEFT, padx=5)

        lbl_busca = ttk.Label(bar_filtro, text="Buscar:", font=("Segoe UI", 9))
        lbl_busca.pack(side=tk.LEFT, padx=(15, 5))
        self.ent_busca_ocor = ttk.Entry(bar_filtro, width=20)
        self.ent_busca_ocor.pack(side=tk.LEFT, padx=5)
        self.ent_busca_ocor.bind("<Return>", lambda e: self._ao_mudar_filtro_status())

        btn_filtrar = ttk.Button(bar_filtro, text="Filtrar", command=self._ao_mudar_filtro_status)
        btn_filtrar.pack(side=tk.LEFT, padx=5)

        # PanedWindow dividindo Grade e Detalhes
        paned = ttk.PanedWindow(self.tab_ocorrencias, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Treeview de Ocorrências
        frame_grid = ttk.Frame(paned)
        paned.add(frame_grid, weight=1)

        cols = ("cod", "status", "entcod", "entnome", "motivo", "respsol", "data")
        self.tree_ocor = ttk.Treeview(frame_grid, columns=cols, show="headings", height=8)
        self.tree_ocor.heading("cod", text="Cód.")
        self.tree_ocor.heading("status", text="Status")
        self.tree_ocor.heading("entcod", text="Solicitante")
        self.tree_ocor.heading("entnome", text="Nome")
        self.tree_ocor.heading("motivo", text="Motivo")
        self.tree_ocor.heading("respsol", text="Resp. Solução")
        self.tree_ocor.heading("data", text="Data")

        self.tree_ocor.column("cod", width=70, anchor=tk.CENTER)
        self.tree_ocor.column("status", width=95, anchor=tk.CENTER)
        self.tree_ocor.column("entcod", width=80)
        self.tree_ocor.column("entnome", width=220)
        self.tree_ocor.column("motivo", width=180)
        self.tree_ocor.column("respsol", width=120)
        self.tree_ocor.column("data", width=90, anchor=tk.CENTER)

        scroll_ocor = ttk.Scrollbar(frame_grid, orient=tk.VERTICAL, command=self.tree_ocor.yview)
        self.tree_ocor.configure(yscrollcommand=scroll_ocor.set)
        self.tree_ocor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_ocor.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_ocor.bind("<<TreeviewSelect>>", self._ao_selecionar_ocorrencia)

        # Formulário de Ocorrência
        frame_form = ttk.LabelFrame(paned, text=" Detalhes da Ocorrência ", padding=10)
        paned.add(frame_form, weight=2)

        # Linha 1: Cód, Solicitante Cód e Nome
        row1 = ttk.Frame(frame_form)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="Cód. Ocorrência:", width=15).pack(side=tk.LEFT)
        self.ent_ocor_cod = ttk.Entry(row1, width=12, state="readonly")
        self.ent_ocor_cod.pack(side=tk.LEFT, padx=5)

        ttk.Label(row1, text="Solicitante:").pack(side=tk.LEFT, padx=(15, 5))
        self.ent_ocor_entcod = ttk.Entry(row1, width=10)
        self.ent_ocor_entcod.pack(side=tk.LEFT, padx=5)
        self.ent_ocor_entnome = ttk.Entry(row1, width=35)
        self.ent_ocor_entnome.pack(side=tk.LEFT, padx=5)

        ttk.Label(row1, text="Data:").pack(side=tk.LEFT, padx=(15, 5))
        self.ent_ocor_data = ttk.Entry(row1, width=12)
        self.ent_ocor_data.pack(side=tk.LEFT, padx=5)

        # Linha 2: Área, Motivo, Origem, Resp. Solução
        row2 = ttk.Frame(frame_form)
        row2.pack(fill=tk.X, pady=4)
        ttk.Label(row2, text="Área:", width=15).pack(side=tk.LEFT)
        self.cbo_ocor_area = ttk.Combobox(row2, state="readonly", width=20)
        self.cbo_ocor_area.pack(side=tk.LEFT, padx=5)
        self.cbo_ocor_area.bind("<<ComboboxSelected>>", self._ao_mudar_area)

        ttk.Label(row2, text="Motivo:").pack(side=tk.LEFT, padx=(10, 5))
        self.cbo_ocor_motivo = ttk.Combobox(row2, state="readonly", width=25)
        self.cbo_ocor_motivo.pack(side=tk.LEFT, padx=5)

        ttk.Label(row2, text="Resp. Solução:").pack(side=tk.LEFT, padx=(10, 5))
        self.ent_ocor_respsol = ttk.Entry(row2, width=18)
        self.ent_ocor_respsol.pack(side=tk.LEFT, padx=5)

        # Linha 3: Textos Solicitação e Solução
        row3 = ttk.Frame(frame_form)
        row3.pack(fill=tk.BOTH, expand=True, pady=4)

        f_solic = ttk.LabelFrame(row3, text=" Solicitação / Reclamação ", padding=5)
        f_solic.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.txt_ocor_solic = tk.Text(f_solic, height=4, width=35, font=("Segoe UI", 9))
        self.txt_ocor_solic.pack(fill=tk.BOTH, expand=True)

        f_soluc = ttk.LabelFrame(row3, text=" Parecer / Solução ", padding=5)
        f_soluc.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        self.txt_ocor_soluc = tk.Text(f_soluc, height=4, width=35, font=("Segoe UI", 9))
        self.txt_ocor_soluc.pack(fill=tk.BOTH, expand=True)

        # Painel de Cancelamento (visível se cancelado ou para cancelar)
        self.frame_canc = ttk.LabelFrame(frame_form, text=" Cancelamento da Ocorrência ", padding=5)
        self.frame_canc.pack(fill=tk.X, pady=4)
        ttk.Label(self.frame_canc, text="Data Canc:").pack(side=tk.LEFT, padx=5)
        self.ent_canc_data = ttk.Entry(self.frame_canc, width=12)
        self.ent_canc_data.pack(side=tk.LEFT, padx=5)
        ttk.Label(self.frame_canc, text="Resp. Canc:").pack(side=tk.LEFT, padx=5)
        self.ent_canc_resp = ttk.Entry(self.frame_canc, width=15)
        self.ent_canc_resp.pack(side=tk.LEFT, padx=5)
        ttk.Label(self.frame_canc, text="Motivo:").pack(side=tk.LEFT, padx=5)
        self.ent_canc_motivo = ttk.Entry(self.frame_canc, width=35)
        self.ent_canc_motivo.pack(side=tk.LEFT, padx=5)

        # Botões de Ação
        bar_btns = ttk.Frame(frame_form)
        bar_btns.pack(fill=tk.X, pady=(6, 0))
        ttk.Button(bar_btns, text="Nova Ocorrência", command=self._nova_ocorrencia).pack(side=tk.LEFT, padx=5)
        ttk.Button(bar_btns, text="Salvar", command=self._salvar_ocorrencia).pack(side=tk.LEFT, padx=5)
        ttk.Button(bar_btns, text="Registrar Solução", command=self._resolver_ocorrencia).pack(side=tk.LEFT, padx=5)
        ttk.Button(bar_btns, text="Cancelar Ocorrência", command=self._cancelar_ocorrencia).pack(side=tk.LEFT, padx=5)
        ttk.Button(bar_btns, text="Limpar", command=self._limpar_form_ocorrencia).pack(side=tk.RIGHT, padx=5)

    # =========================================================================
    # ABA 2: TIPOS DE CAMPANHA
    # =========================================================================

    def _setup_aba_campanhas(self):
        paned = ttk.PanedWindow(self.tab_campanhas, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        frame_grid = ttk.Frame(paned)
        paned.add(frame_grid, weight=3)

        cols = ("cod", "desc", "ativo", "gera")
        self.tree_camp = ttk.Treeview(frame_grid, columns=cols, show="headings")
        self.tree_camp.heading("cod", text="Código")
        self.tree_camp.heading("desc", text="Descrição do Tipo de Campanha")
        self.tree_camp.heading("ativo", text="Ativo")
        self.tree_camp.heading("gera", text="Gera Campanha")

        self.tree_camp.column("cod", width=80, anchor=tk.CENTER)
        self.tree_camp.column("desc", width=250)
        self.tree_camp.column("ativo", width=60, anchor=tk.CENTER)
        self.tree_camp.column("gera", width=90, anchor=tk.CENTER)

        scroll_camp = ttk.Scrollbar(frame_grid, orient=tk.VERTICAL, command=self.tree_camp.yview)
        self.tree_camp.configure(yscrollcommand=scroll_camp.set)
        self.tree_camp.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_camp.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_camp.bind("<<TreeviewSelect>>", self._ao_selecionar_campanha)

        # Formulário Lateral
        frame_form = ttk.LabelFrame(paned, text=" Cadastro de Tipo de Campanha ", padding=10)
        paned.add(frame_form, weight=2)

        ttk.Label(frame_form, text="Código:").pack(anchor=tk.W, pady=(0, 2))
        self.ent_camp_cod = ttk.Entry(frame_form, width=15)
        self.ent_camp_cod.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))

        ttk.Label(frame_form, text="Descrição:").pack(anchor=tk.W, pady=(0, 2))
        self.ent_camp_desc = ttk.Entry(frame_form, width=30)
        self.ent_camp_desc.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))

        self.chk_camp_ativo_var = tk.BooleanVar(value=True)
        chk_ativo = ttk.Checkbutton(frame_form, text="Ativo", variable=self.chk_camp_ativo_var)
        chk_ativo.pack(anchor=tk.W, pady=4)

        self.chk_camp_gera_var = tk.BooleanVar(value=True)
        chk_gera = ttk.Checkbutton(frame_form, text="Gera Campanha", variable=self.chk_camp_gera_var)
        chk_gera.pack(anchor=tk.W, pady=4)

        bar_btns = ttk.Frame(frame_form)
        bar_btns.pack(fill=tk.X, pady=(15, 0))
        ttk.Button(bar_btns, text="Salvar", command=self._salvar_campanha).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar_btns, text="Excluir", command=self._excluir_campanha).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar_btns, text="Limpar", command=self._limpar_campanha).pack(side=tk.RIGHT, padx=2)

    # =========================================================================
    # ABA 3: TIPOS DE TRATAMENTO
    # =========================================================================

    def _setup_aba_tratamentos(self):
        paned = ttk.PanedWindow(self.tab_tratamentos, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        frame_grid = ttk.Frame(paned)
        paned.add(frame_grid, weight=3)

        cols = ("cod", "abrev", "desc")
        self.tree_trat = ttk.Treeview(frame_grid, columns=cols, show="headings")
        self.tree_trat.heading("cod", text="Código")
        self.tree_trat.heading("abrev", text="Abreviatura")
        self.tree_trat.heading("desc", text="Descrição do Tratamento")

        self.tree_trat.column("cod", width=80, anchor=tk.CENTER)
        self.tree_trat.column("abrev", width=100)
        self.tree_trat.column("desc", width=280)

        scroll_trat = ttk.Scrollbar(frame_grid, orient=tk.VERTICAL, command=self.tree_trat.yview)
        self.tree_trat.configure(yscrollcommand=scroll_trat.set)
        self.tree_trat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_trat.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_trat.bind("<<TreeviewSelect>>", self._ao_selecionar_tratamento)

        # Formulário Lateral
        frame_form = ttk.LabelFrame(paned, text=" Cadastro de Tipo de Tratamento ", padding=10)
        paned.add(frame_form, weight=2)

        ttk.Label(frame_form, text="Código:").pack(anchor=tk.W, pady=(0, 2))
        self.ent_trat_cod = ttk.Entry(frame_form, width=15)
        self.ent_trat_cod.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))

        ttk.Label(frame_form, text="Abreviatura:").pack(anchor=tk.W, pady=(0, 2))
        self.ent_trat_abrev = ttk.Entry(frame_form, width=15)
        self.ent_trat_abrev.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))

        ttk.Label(frame_form, text="Descrição:").pack(anchor=tk.W, pady=(0, 2))
        self.ent_trat_desc = ttk.Entry(frame_form, width=30)
        self.ent_trat_desc.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))

        bar_btns = ttk.Frame(frame_form)
        bar_btns.pack(fill=tk.X, pady=(15, 0))
        ttk.Button(bar_btns, text="Salvar", command=self._salvar_tratamento).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar_btns, text="Excluir", command=self._excluir_tratamento).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar_btns, text="Limpar", command=self._limpar_tratamento).pack(side=tk.RIGHT, padx=2)

    # =========================================================================
    # CARREGAMENTO E MANIPULAÇÃO DE DADOS
    # =========================================================================

    def recarregar_dados(self):
        self.carregar_ocorrencias()
        self.carregar_tipos_campanha()
        self.carregar_tipos_tratamento()
        self._carregar_combos_ocorrencia()

    def carregar_ocorrencias(self, status: str = "", filtro: str = ""):
        if not self.service:
            return
        st = status if status != "" else self.var_status_filtro.get()
        f = filtro if filtro != "" else self.ent_busca_ocor.get()
        ocorrencias = self.service.listar_ocorrencias(
            status=st, empcod=self.codigo_empresa, filtro=f
        )
        self.tree_ocor.delete(*self.tree_ocor.get_children())
        for o in ocorrencias:
            self.tree_ocor.insert(
                "",
                tk.END,
                values=(
                    o.ocorcod,
                    o.ocorstat,
                    o.entcod,
                    o.ocorentnome,
                    o.motocordescr,
                    o.ocorrespsol,
                    o.ocordata[:10] if o.ocordata else "",
                ),
            )

    def _ao_mudar_filtro_status(self):
        self.carregar_ocorrencias()

    def _carregar_combos_ocorrencia(self):
        if not self.service:
            return
        try:
            areas = self.service.listar_areas_disponiveis()
            self._mapa_areas = {a.motocordescr: a.motocorcodestr for a in areas}
            self.cbo_ocor_area["values"] = list(self._mapa_areas.keys())
        except Exception:
            pass

    def _ao_mudar_area(self, event=None):
        if not self.service:
            return
        area_nome = self.cbo_ocor_area.get()
        cod_area = getattr(self, "_mapa_areas", {}).get(area_nome, "")
        if cod_area:
            motivos = self.service.listar_motivos_por_area(cod_area)
            self._mapa_motivos = {m.motocordescr: m.motocorcodestr for m in motivos}
            self.cbo_ocor_motivo["values"] = list(self._mapa_motivos.keys())
            if motivos:
                self.cbo_ocor_motivo.current(0)

    def _ao_selecionar_ocorrencia(self, event=None):
        sel = self.tree_ocor.selection()
        if not sel or not self.service:
            return
        item = self.tree_ocor.item(sel[0])
        cod = str(item["values"][0])
        ocor = self.service.obter_ocorrencia(cod)
        if not ocor:
            return

        self._preencher_form_ocorrencia(ocor)

    def _preencher_form_ocorrencia(self, o: OcorrenciaDTO):
        self.ent_ocor_cod.configure(state="normal")
        self.ent_ocor_cod.delete(0, tk.END)
        self.ent_ocor_cod.insert(0, o.ocorcod)
        self.ent_ocor_cod.configure(state="readonly")

        self.ent_ocor_entcod.delete(0, tk.END)
        self.ent_ocor_entcod.insert(0, o.entcod)

        self.ent_ocor_entnome.delete(0, tk.END)
        self.ent_ocor_entnome.insert(0, o.ocorentnome)

        self.ent_ocor_data.delete(0, tk.END)
        self.ent_ocor_data.insert(0, o.ocordata[:10] if o.ocordata else "")

        self.ent_ocor_respsol.delete(0, tk.END)
        self.ent_ocor_respsol.insert(0, o.ocorrespsol)

        self.txt_ocor_solic.delete("1.0", tk.END)
        self.txt_ocor_solic.insert(tk.END, o.ocortexto)

        self.txt_ocor_soluc.delete("1.0", tk.END)
        self.txt_ocor_soluc.insert(tk.END, o.ocorresptexto)

        self.ent_canc_data.delete(0, tk.END)
        self.ent_canc_data.insert(0, o.ocordatacanc[:10] if o.ocordatacanc else "")

        self.ent_canc_resp.delete(0, tk.END)
        self.ent_canc_resp.insert(0, o.ocorrespcanc)

        self.ent_canc_motivo.delete(0, tk.END)
        self.ent_canc_motivo.insert(0, o.ocormotcanc)

    def _limpar_form_ocorrencia(self):
        self.ent_ocor_cod.configure(state="normal")
        self.ent_ocor_cod.delete(0, tk.END)
        self.ent_ocor_cod.configure(state="readonly")
        self.ent_ocor_entcod.delete(0, tk.END)
        self.ent_ocor_entnome.delete(0, tk.END)
        self.ent_ocor_data.delete(0, tk.END)
        self.ent_ocor_respsol.delete(0, tk.END)
        self.txt_ocor_solic.delete("1.0", tk.END)
        self.txt_ocor_soluc.delete("1.0", tk.END)
        self.ent_canc_data.delete(0, tk.END)
        self.ent_canc_resp.delete(0, tk.END)
        self.ent_canc_motivo.delete(0, tk.END)

    def _nova_ocorrencia(self):
        self._limpar_form_ocorrencia()
        self.ent_ocor_entcod.focus_set()

    def _salvar_ocorrencia(self):
        if not self.service:
            return

        mot_nome = self.cbo_ocor_motivo.get()
        mot_cod = getattr(self, "_mapa_motivos", {}).get(mot_nome, "")

        dto = OcorrenciaDTO(
            ocorcod=self.ent_ocor_cod.get().strip(),
            ocorstat="Pendente",
            entcod=self.ent_ocor_entcod.get().strip(),
            ocorentnome=self.ent_ocor_entnome.get().strip(),
            ocorrespsol=self.ent_ocor_respsol.get().strip(),
            ocordata=self.ent_ocor_data.get().strip(),
            motocorcodestr=mot_cod,
            ocortexto=self.txt_ocor_solic.get("1.0", tk.END).strip(),
            ocorresptexto=self.txt_ocor_soluc.get("1.0", tk.END).strip(),
            empcod=self.codigo_empresa,
        )

        res = self.service.salvar_ocorrencia(dto)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.carregar_ocorrencias()
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _resolver_ocorrencia(self):
        if not self.service:
            return
        cod = self.ent_ocor_cod.get().strip()
        soluc = self.txt_ocor_soluc.get("1.0", tk.END).strip()
        respsol = self.ent_ocor_respsol.get().strip()

        if not cod:
            messagebox.showwarning("Aviso", "Selecione uma ocorrência para registrar solução.")
            return

        res = self.service.atualizar_solucao(cod, soluc, status="Resolvido", resp_sol=respsol)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.carregar_ocorrencias()
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _cancelar_ocorrencia(self):
        if not self.service:
            return
        cod = self.ent_ocor_cod.get().strip()
        dt = self.ent_canc_data.get().strip()
        resp = self.ent_canc_resp.get().strip()
        mot = self.ent_canc_motivo.get().strip()

        if not cod:
            messagebox.showwarning("Aviso", "Selecione uma ocorrência para cancelamento.")
            return

        if not messagebox.askyesno(
            "Confirmação de Cancelamento",
            f"Atenção: o cancelamento da ocorrência {cod} é irreversível. Confirmar?",
        ):
            return

        res = self.service.cancelar_ocorrencia(cod, dt, resp, mot)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.carregar_ocorrencias()
        else:
            messagebox.showerror("Erro", res.mensagem)

    # Campanhas
    def carregar_tipos_campanha(self):
        if not self.service:
            return
        camps = self.service.listar_tipos_campanha()
        self.tree_camp.delete(*self.tree_camp.get_children())
        for c in camps:
            self.tree_camp.insert(
                "",
                tk.END,
                values=(c.codigo_tipocampanha, c.descricaotipocamp, c.ativo, c.geracampanha),
            )

    def _ao_selecionar_campanha(self, event=None):
        sel = self.tree_camp.selection()
        if not sel or not self.service:
            return
        vals = self.tree_camp.item(sel[0])["values"]
        self.ent_camp_cod.delete(0, tk.END)
        self.ent_camp_cod.insert(0, str(vals[0]))
        self.ent_camp_desc.delete(0, tk.END)
        self.ent_camp_desc.insert(0, str(vals[1]))
        self.chk_camp_ativo_var.set(str(vals[2]).upper() == "S")
        self.chk_camp_gera_var.set(str(vals[3]).upper() == "S")

    def _limpar_campanha(self):
        self.ent_camp_cod.delete(0, tk.END)
        self.ent_camp_desc.delete(0, tk.END)
        self.chk_camp_ativo_var.set(True)
        self.chk_camp_gera_var.set(True)

    def _salvar_campanha(self):
        if not self.service:
            return
        dto = TipoCampanhaDTO(
            codigo_tipocampanha=self.ent_camp_cod.get().strip(),
            descricaotipocamp=self.ent_camp_desc.get().strip(),
            ativo="S" if self.chk_camp_ativo_var.get() else "N",
            geracampanha="S" if self.chk_camp_gera_var.get() else "N",
        )
        res = self.service.salvar_tipo_campanha(dto)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.carregar_tipos_campanha()
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _excluir_campanha(self):
        if not self.service:
            return
        cod = self.ent_camp_cod.get().strip()
        if not cod:
            messagebox.showwarning("Aviso", "Selecione um tipo de campanha para exclusão.")
            return
        if not messagebox.askyesno("Confirmação", f"Excluir tipo de campanha '{cod}'?"):
            return
        res = self.service.excluir_tipo_campanha(cod)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self._limpar_campanha()
            self.carregar_tipos_campanha()
        else:
            messagebox.showerror("Erro", res.mensagem)

    # Tratamentos
    def carregar_tipos_tratamento(self):
        if not self.service:
            return
        trats = self.service.listar_tipos_tratamento()
        self.tree_trat.delete(*self.tree_trat.get_children())
        for t in trats:
            self.tree_trat.insert(
                "",
                tk.END,
                values=(t.tipotratcod, t.abreviatura, t.descricao_tratamento),
            )

    def _ao_selecionar_tratamento(self, event=None):
        sel = self.tree_trat.selection()
        if not sel or not self.service:
            return
        vals = self.tree_trat.item(sel[0])["values"]
        self.ent_trat_cod.delete(0, tk.END)
        self.ent_trat_cod.insert(0, str(vals[0]))
        self.ent_trat_abrev.delete(0, tk.END)
        self.ent_trat_abrev.insert(0, str(vals[1]))
        self.ent_trat_desc.delete(0, tk.END)
        self.ent_trat_desc.insert(0, str(vals[2]))

    def _limpar_tratamento(self):
        self.ent_trat_cod.delete(0, tk.END)
        self.ent_trat_abrev.delete(0, tk.END)
        self.ent_trat_desc.delete(0, tk.END)

    def _salvar_tratamento(self):
        if not self.service:
            return
        dto = TipoTratamentoDTO(
            tipotratcod=self.ent_trat_cod.get().strip(),
            abreviatura=self.ent_trat_abrev.get().strip(),
            descricao_tratamento=self.ent_trat_desc.get().strip(),
        )
        res = self.service.salvar_tipo_tratamento(dto)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.carregar_tipos_tratamento()
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _excluir_tratamento(self):
        if not self.service:
            return
        cod = self.ent_trat_cod.get().strip()
        if not cod:
            messagebox.showwarning("Aviso", "Selecione um tipo de tratamento para exclusão.")
            return
        if not messagebox.askyesno("Confirmação", f"Excluir tipo de tratamento '{cod}'?"):
            return
        res = self.service.excluir_tipo_tratamento(cod)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self._limpar_tratamento()
            self.carregar_tipos_tratamento()
        else:
            messagebox.showerror("Erro", res.mensagem)


def abrir_janela_crm(parent, connection=None, codigo_empresa="01", usuario_atual="ADMIN"):
    """Abre o módulo de CRM & Ocorrências em janela modal/toplevel."""
    win = tk.Toplevel(parent)
    win.title("Gestão de CRM, Campanhas e Ocorrências - GeoApolo V5")
    win.geometry("980x680")
    win.minsize(800, 500)

    view = CRMView(
        parent=win,
        connection=connection,
        codigo_empresa=codigo_empresa,
        usuario_atual=usuario_atual,
    )
    view.pack(fill=tk.BOTH, expand=True)
    return win
