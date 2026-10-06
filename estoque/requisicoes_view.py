"""
Interface Gráfica para Gestão de Requisições de Materiais.
GeoApolo V5
Clean Architecture: Atendimento, Cancelamento e Devolução de Requisições de Materiais.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List

from core import (
    centralizar_janela,
    vincular_maiusculo,
    configurar_navegacao_enter,
    formatar_data_br,
    obter_empresa_ativa,
)
from .models import RequisicaoDTO, ItemRequisicaoDTO
from .service import EstoqueService


class RequisicoesView(ttk.Frame):
    """Tela de Atendimento, Cancelamento e Devolução de Requisições de Materiais."""

    def __init__(self, parent=None, service: Optional[EstoqueService] = None, modo_inicial: str = "TODOS"):
        super().__init__(parent)
        self.service = service
        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from .repository import EstoqueRepository
                conn = obter_conexao_banco()
                self.service = EstoqueService(EstoqueRepository(conn))
            except Exception:
                pass

        self._modo_inicial = modo_inicial
        self._requisicao_selecionada: Optional[RequisicaoDTO] = None
        self._setup_ui()
        self._configurar_atalhos()
        self.carregar_requisicoes()

    def _setup_ui(self):
        # Header superior moderno
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        titulo_texto = "Gestão de Requisições de Materiais"
        if self._modo_inicial == "ATENDIMENTO":
            titulo_texto = "Atendimento de Requisições de Materiais"
        elif self._modo_inicial == "CANCELAMENTO":
            titulo_texto = "Cancelamento de Requisições de Materiais"
        elif self._modo_inicial == "DEVOLUCAO":
            titulo_texto = "Devolução de Requisições de Materiais"

        lbl_titulo = ttk.Label(
            header,
            text=titulo_texto,
            font=("Segoe UI", 13, "bold"),
            foreground="#1E3A8A",
        )
        lbl_titulo.pack(side=tk.LEFT)

        # Contador
        self.lbl_contador = ttk.Label(
            header,
            text="0 requisição(ões)",
            font=("Segoe UI", 9, "bold"),
            foreground="#475569",
        )
        self.lbl_contador.pack(side=tk.RIGHT, padx=5)

        # Barra de Filtros
        filtro_box = ttk.LabelFrame(self, text=" Filtros de Pesquisa ", padding=(10, 8))
        filtro_box.pack(fill=tk.X, padx=12, pady=(0, 6))

        # Linha 1 de filtros
        f_row = ttk.Frame(filtro_box)
        f_row.pack(fill=tk.X)

        ttk.Label(f_row, text="Status:").pack(side=tk.LEFT, padx=(0, 4))
        status_padrao = "TODOS"
        if self._modo_inicial in ("ATENDIMENTO", "CANCELAMENTO"):
            status_padrao = "PENDENTES"
        self.var_status = tk.StringVar(value=status_padrao)
        self.cb_status = ttk.Combobox(
            f_row,
            textvariable=self.var_status,
            values=["TODOS", "PENDENTES", "ABERTA", "ATENDIDA PARCIAL", "ATENDIDA TOTAL", "CANCELADA"],
            state="readonly",
            width=18,
        )
        self.cb_status.pack(side=tk.LEFT, padx=(0, 15))
        self.cb_status.bind("<<ComboboxSelected>>", lambda e: self.carregar_requisicoes())

        ttk.Label(f_row, text="Buscar:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_busca = tk.StringVar()
        vincular_maiusculo(self.var_busca)
        self.ent_busca = ttk.Entry(f_row, textvariable=self.var_busca, width=28)
        self.ent_busca.pack(side=tk.LEFT, padx=(0, 15))
        self.ent_busca.bind("<Return>", lambda e: self.carregar_requisicoes())

        ttk.Label(f_row, text="Empresa:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_empcod = tk.StringVar(value=obter_empresa_ativa())
        self.ent_empcod = ttk.Entry(f_row, textvariable=self.var_empcod, width=8)
        self.ent_empcod.pack(side=tk.LEFT, padx=(0, 15))

        btn_filtrar = ttk.Button(f_row, text="🔍 Filtrar (F5)", command=self.carregar_requisicoes)
        btn_filtrar.pack(side=tk.LEFT, padx=(0, 6))

        btn_limpar = ttk.Button(f_row, text="Limpar", command=self._limpar_filtros)
        btn_limpar.pack(side=tk.LEFT)

        # PanedWindow vertical para Mestre (Requisições) e Detalhe (Itens)
        paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        # Frame superior: Requisições
        frame_reqs = ttk.LabelFrame(paned, text=" Requisições de Materiais ", padding=6)
        paned.add(frame_reqs, weight=3)

        cols_req = ("num", "tipo", "data", "requerente", "centro_custo", "status", "tot_sol", "tot_atend", "tot_pend")
        self.tree_req = ttk.Treeview(frame_reqs, columns=cols_req, show="headings", height=8, selectmode="browse")
        self.tree_req.heading("num", text="Nº Requisição")
        self.tree_req.heading("tipo", text="Tipo")
        self.tree_req.heading("data", text="Data")
        self.tree_req.heading("requerente", text="Requerente")
        self.tree_req.heading("centro_custo", text="Centro Custo")
        self.tree_req.heading("status", text="Status")
        self.tree_req.heading("tot_sol", text="Qtd Solicitada")
        self.tree_req.heading("tot_atend", text="Qtd Atendida")
        self.tree_req.heading("tot_pend", text="Saldo Pendente")

        self.tree_req.column("num", width=110, anchor=tk.CENTER)
        self.tree_req.column("tipo", width=80, anchor=tk.CENTER)
        self.tree_req.column("data", width=95, anchor=tk.CENTER)
        self.tree_req.column("requerente", width=200, anchor=tk.W)
        self.tree_req.column("centro_custo", width=110, anchor=tk.W)
        self.tree_req.column("status", width=120, anchor=tk.CENTER)
        self.tree_req.column("tot_sol", width=90, anchor=tk.E)
        self.tree_req.column("tot_atend", width=90, anchor=tk.E)
        self.tree_req.column("tot_pend", width=90, anchor=tk.E)

        sb_req_y = ttk.Scrollbar(frame_reqs, orient=tk.VERTICAL, command=self.tree_req.yview)
        self.tree_req.configure(yscrollcommand=sb_req_y.set)
        self.tree_req.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_req_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_req.bind("<<TreeviewSelect>>", self._ao_selecionar_requisicao)
        self.tree_req.bind("<Double-1>", lambda e: self._abrir_atendimento_selecionado())

        # Tags de cores para status
        self.tree_req.tag_configure("Aberta", foreground="#0369A1", background="#F0F9FF")
        self.tree_req.tag_configure("Atendida Parcial", foreground="#B45309", background="#FFFBEB")
        self.tree_req.tag_configure("Atendida Total", foreground="#15803D", background="#F0FDF4")
        self.tree_req.tag_configure("Cancelada", foreground="#B91C1C", background="#FEF2F2")

        # Frame inferior: Itens da Requisição
        frame_itens = ttk.LabelFrame(paned, text=" Itens da Requisição Selecionada ", padding=6)
        paned.add(frame_itens, weight=3)

        cols_it = ("seq", "prodcod", "prodnome", "unid", "qtd_sol", "qtd_atend", "saldo", "status", "obs")
        self.tree_itens = ttk.Treeview(frame_itens, columns=cols_it, show="headings", height=6, selectmode="browse")
        self.tree_itens.heading("seq", text="Item")
        self.tree_itens.heading("prodcod", text="Código")
        self.tree_itens.heading("prodnome", text="Descrição do Produto")
        self.tree_itens.heading("unid", text="Unid")
        self.tree_itens.heading("qtd_sol", text="Qtd Solicitada")
        self.tree_itens.heading("qtd_atend", text="Qtd Atendida")
        self.tree_itens.heading("saldo", text="Saldo a Atender")
        self.tree_itens.heading("status", text="Status Item")
        self.tree_itens.heading("obs", text="Observação / Motivo")

        self.tree_itens.column("seq", width=50, anchor=tk.CENTER)
        self.tree_itens.column("prodcod", width=110, anchor=tk.W)
        self.tree_itens.column("prodnome", width=250, anchor=tk.W)
        self.tree_itens.column("unid", width=55, anchor=tk.CENTER)
        self.tree_itens.column("qtd_sol", width=100, anchor=tk.E)
        self.tree_itens.column("qtd_atend", width=100, anchor=tk.E)
        self.tree_itens.column("saldo", width=100, anchor=tk.E)
        self.tree_itens.column("status", width=115, anchor=tk.CENTER)
        self.tree_itens.column("obs", width=220, anchor=tk.W)

        sb_it_y = ttk.Scrollbar(frame_itens, orient=tk.VERTICAL, command=self.tree_itens.yview)
        self.tree_itens.configure(yscrollcommand=sb_it_y.set)
        self.tree_itens.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_it_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_itens.bind("<Double-1>", lambda e: self._abrir_atendimento_selecionado())

        self.tree_itens.tag_configure("Pendente", foreground="#0369A1")
        self.tree_itens.tag_configure("Atendido Parcial", foreground="#B45309")
        self.tree_itens.tag_configure("Atendido", foreground="#15803D")
        self.tree_itens.tag_configure("Cancelado", foreground="#B91C1C", background="#FEF2F2")

        # Barra inferior de Ações
        bar_acoes = ttk.Frame(self, padding=(12, 10))
        bar_acoes.pack(fill=tk.X)

        self.btn_nova_req = tk.Button(
            bar_acoes,
            text="➕ Nova Requisição (F2)",
            bg="#2563EB",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=4,
            relief=tk.FLAT,
            command=self._abrir_nova_requisicao,
        )
        self.btn_nova_req.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_atender = tk.Button(
            bar_acoes,
            text="✔ Atender Item (F3)",
            bg="#16A34A",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=4,
            relief=tk.FLAT,
            command=self._abrir_atendimento_selecionado,
        )
        self.btn_atender.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_atender_tudo = tk.Button(
            bar_acoes,
            text="⚡ Atender Tudo (F7)",
            bg="#059669",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=4,
            relief=tk.FLAT,
            command=self._atender_requisicao_completa,
        )
        self.btn_atender_tudo.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_devolver = tk.Button(
            bar_acoes,
            text="↩ Devolver Item (F8)",
            bg="#0284C7",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=4,
            relief=tk.FLAT,
            command=self._abrir_devolucao_selecionada,
        )
        self.btn_devolver.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_cancelar = tk.Button(
            bar_acoes,
            text="✖ Cancelar Requisição (F6)",
            bg="#DC2626",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=4,
            relief=tk.FLAT,
            command=self._abrir_cancelamento_selecionado,
        )
        self.btn_cancelar.pack(side=tk.LEFT, padx=(0, 8))

        btn_atualizar = ttk.Button(bar_acoes, text="🔄 Atualizar (F5)", command=self.carregar_requisicoes)
        btn_atualizar.pack(side=tk.LEFT, padx=(0, 8))

        btn_fechar = ttk.Button(bar_acoes, text="Fechar (Esc)", command=self._fechar_janela)
        btn_fechar.pack(side=tk.RIGHT)

        bar_bottom_hint = ttk.Frame(self, padding=(12, 0, 12, 8))
        bar_bottom_hint.pack(fill=tk.X)
        lbl_hint = ttk.Label(
            bar_bottom_hint,
            text="Atalhos: [F2] Nova | [F3] Atender Item | [F7] Atender Tudo | [F8] Devolver | [F6] Cancelar | [F4] Buscar | [F5] Atualizar | [Esc] Fechar",
            font=("Segoe UI", 8),
            foreground="#64748B",
        )
        lbl_hint.pack(side=tk.LEFT)

        configurar_navegacao_enter([self.cb_status, self.ent_busca, self.ent_empcod, btn_filtrar])

    def _configurar_atalhos(self):
        root = self.winfo_toplevel()
        root.bind("<F2>", lambda e: self._abrir_nova_requisicao())
        root.bind("<F3>", lambda e: self._abrir_atendimento_selecionado())
        root.bind("<F8>", lambda e: self._abrir_devolucao_selecionada())
        root.bind("<F5>", lambda e: self.carregar_requisicoes())
        root.bind("<F6>", lambda e: self._abrir_cancelamento_selecionado())
        root.bind("<F7>", lambda e: self._atender_requisicao_completa())
        root.bind("<F4>", lambda e: (self.ent_busca.focus_set(), self.ent_busca.select_range(0, tk.END)))
        root.bind("<Escape>", lambda e: self._fechar_janela())

    def _abrir_nova_requisicao(self):
        from .nova_requisicao_view import abrir_nova_requisicao_material
        abrir_nova_requisicao_material(parent=self.winfo_toplevel(), on_gravada_callback=self.carregar_requisicoes)

    def _fechar_janela(self):
        toplevel = self.winfo_toplevel()
        if toplevel != self:
            toplevel.destroy()

    def _limpar_filtros(self):
        self.var_status.set("TODOS")
        self.var_busca.set("")
        self.carregar_requisicoes()

    def carregar_requisicoes(self):
        if not self.service:
            return

        for it in self.tree_req.get_children():
            self.tree_req.delete(it)
        for it in self.tree_itens.get_children():
            self.tree_itens.delete(it)
        self._requisicao_selecionada = None

        empcod = self.var_empcod.get().strip() or "1.01"
        status_f = self.var_status.get().strip()
        busca = self.var_busca.get().strip()

        requisicoes = self.service.listar_requisicoes(
            empcod=empcod,
            status_filtro=status_f,
            termo_busca=busca,
        )

        for r in requisicoes:
            # Buscar itens para calcular totais
            det = self.service.obter_requisicao(r.req_num, empcod=empcod)
            tot_sol = det.total_solicitado if det else 0.0
            tot_atend = det.total_atendido if det else 0.0
            tot_pend = det.total_pendente if det else 0.0

            tag = r.status if r.status in ("Aberta", "Atendida Parcial", "Atendida Total", "Cancelada") else "Aberta"
            self.tree_req.insert(
                "",
                tk.END,
                iid=r.req_num,
                values=(
                    r.req_num,
                    getattr(r, "tipo_requisicao", "Produto") or "Produto",
                    formatar_data_br(r.data_req),
                    r.requerente,
                    r.centro_custo,
                    r.status,
                    f"{tot_sol:.2f}",
                    f"{tot_atend:.2f}",
                    f"{tot_pend:.2f}",
                ),
                tags=(tag,),
            )

        self.lbl_contador.config(text=f"{len(requisicoes)} requisição(ões) encontrada(s)")

    def _ao_selecionar_requisicao(self, event=None):
        sel = self.tree_req.selection()
        if not sel:
            return

        req_num = sel[0]
        empcod = self.var_empcod.get().strip() or "1.01"
        self._requisicao_selecionada = self.service.obter_requisicao(req_num, empcod=empcod)

        for it in self.tree_itens.get_children():
            self.tree_itens.delete(it)

        if not self._requisicao_selecionada:
            return

        for item in self._requisicao_selecionada.itens:
            tag = item.status_item
            self.tree_itens.insert(
                "",
                tk.END,
                iid=f"{item.req_num}_{item.item_seq}",
                values=(
                    item.item_seq,
                    item.prodcod_estr,
                    item.prodnome,
                    item.unidade,
                    f"{item.qtd_solicitada:.2f}",
                    f"{item.qtd_atendida:.2f}",
                    f"{item.saldo_pendente:.2f}",
                    item.status_item,
                    getattr(item, "observacao", "") or "",
                ),
                tags=(tag,),
            )

    def _obter_item_selecionado(self) -> Optional[ItemRequisicaoDTO]:
        if not self._requisicao_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma requisição primeiro.", parent=self)
            return None

        sel_it = self.tree_itens.selection()
        if not sel_it:
            if not self._requisicao_selecionada.itens:
                messagebox.showwarning("Aviso", "A requisição selecionada não possui itens.", parent=self)
                return None
            pendentes = [it for it in self._requisicao_selecionada.itens if it.saldo_pendente > 0.0001]
            item_alvo = pendentes[0] if pendentes else self._requisicao_selecionada.itens[0]
            iid_alvo = f"item_{item_alvo.item_seq}"
            if self.tree_itens.exists(iid_alvo):
                self.tree_itens.selection_set(iid_alvo)
                self.tree_itens.focus(iid_alvo)
            return item_alvo

        iid = sel_it[0]
        try:
            seq = int(iid.split("_")[-1])
        except Exception:
            return None
        for it in self._requisicao_selecionada.itens:
            if it.item_seq == seq:
                return it
        return None

    # -------------------------------------------------------------------------
    # ATENDIMENTO COMPLETO (EM LOTE) E INDIVIDUAL DE REQUISIÇÕES
    # -------------------------------------------------------------------------
    def _atender_requisicao_completa(self):
        sel = self.tree_req.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma requisição para realizar o atendimento completo.", parent=self)
            return

        req_num = sel[0]
        empcod = self.var_empcod.get().strip() or "1.01"
        req = self.service.obter_requisicao(req_num, empcod=empcod)
        if not req:
            messagebox.showerror("Erro", f"Requisição {req_num} não encontrada.", parent=self)
            return

        if req.status == "Cancelada":
            messagebox.showerror("Erro", "Requisições canceladas não podem ser atendidas.", parent=self)
            return

        itens_pendentes = [it for it in req.itens if it.saldo_pendente > 0.0001]
        if not itens_pendentes:
            messagebox.showinfo("Aviso", f"A requisição {req_num} já está totalmente atendida!", parent=self)
            return

        tot_itens = len(itens_pendentes)
        tot_qtd = sum(it.saldo_pendente for it in itens_pendentes)
        tipo_req = getattr(req, "tipo_requisicao", "Produto") or "Produto"
        is_servico = tipo_req.lower().startswith("serv")

        lote_svc = None
        if self.service and hasattr(self.service, "_repo") and self.service._repo and self.service._repo.conn:
            try:
                from lotes.repository import LotesRepository
                from lotes.service import LotesService
                lote_svc = LotesService(LotesRepository(self.service._repo.conn))
            except Exception:
                pass

        # Checar saldos e necessidade de lote para cada item
        itens_info = []
        itens_sem_saldo = []
        for it in itens_pendentes:
            s_atual, s_reserv, s_disp = self.service.obter_saldo_produto(it.prodcod_estr, empcod=empcod)
            p_int = None
            try:
                p_int = int(it.prodcod_estr)
            except Exception:
                pass

            ctrl_lote = False
            if not is_servico and lote_svc and p_int:
                try:
                    ctrl_lote = lote_svc.produto_controla_lote(p_int)
                except Exception:
                    ctrl_lote = False

            if not is_servico and it.saldo_pendente > (s_disp + 0.0001):
                itens_sem_saldo.append((it, s_disp))

            itens_info.append({
                "item": it,
                "s_atual": s_atual,
                "s_reserv": s_reserv,
                "s_disp": s_disp,
                "controla_lote": ctrl_lote,
                "p_int": p_int,
            })

        permite_neg = self.service.permite_estoque_negativo(empcod) if self.service else False
        if itens_sem_saldo and not permite_neg:
            detalhes = "\n".join([f"• Item {it.item_seq} - {it.prodnome} (Sol: {it.saldo_pendente:.2f} | Disp: {disp:.2f})" for it, disp in itens_sem_saldo])
            messagebox.showwarning(
                "Atenção: Saldo Insuficiente",
                f"O sistema não permite estoque negativo, este produto não tem em estoque e não permite movimentação:\n\n{detalhes}",
                parent=self,
            )
            return

        # Abre modal para conferência, preenchimento de lote e validação de validade
        modal_f7 = tk.Toplevel(self)
        modal_f7.title(f"Atendimento Total (F7) - Requisição Nº {req_num}")
        modal_f7.transient(self)
        modal_f7.grab_set()
        centralizar_janela(modal_f7, self, 700, 520)
        modal_f7.minsize(620, 440)

        f_cont = ttk.Frame(modal_f7, padding=16)
        f_cont.pack(fill=tk.BOTH, expand=True)

        lbl_top = ttk.Label(
            f_cont,
            text=f"Atendimento Completo de Requisição Nº {req_num}",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
        )
        lbl_top.pack(anchor=tk.W, pady=(0, 4))

        sub_txt = f"Solicitante: {req.requerente} | C. Custo: {req.centro_custo} | Total Itens: {tot_itens} ({tot_qtd:.2f} un)"
        lbl_sub = ttk.Label(f_cont, text=sub_txt, font=("Segoe UI", 9), foreground="#475569")
        lbl_sub.pack(anchor=tk.W, pady=(0, 10))

        # Canvas com barra de rolagem vertical
        f_scroll_cont = ttk.Frame(f_cont)
        f_scroll_cont.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        canvas = tk.Canvas(f_scroll_cont, borderwidth=0, highlightthickness=0, bg="#F8FAFC")
        scrollbar = ttk.Scrollbar(f_scroll_cont, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas_win = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def _on_canvas_configure(e):
            canvas.itemconfig(canvas_win, width=e.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def _ao_rolar_mouse(event):
            try:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass
        canvas.bind("<MouseWheel>", _ao_rolar_mouse)
        scrollable_frame.bind("<MouseWheel>", _ao_rolar_mouse)

        # Monta os cards de cada item
        for info in itens_info:
            it = info["item"]
            s_disp = info["s_disp"]
            ctrl = info["controla_lote"]
            p_int = info["p_int"]

            card = ttk.LabelFrame(
                scrollable_frame,
                text=f" Item {it.item_seq}: {it.prodcod_estr} - {it.prodnome} ",
                padding=8,
            )
            card.pack(fill=tk.X, padx=4, pady=4)
            card.bind("<MouseWheel>", _ao_rolar_mouse)

            f_linha_info = ttk.Frame(card)
            f_linha_info.pack(fill=tk.X, pady=(0, 4))
            f_linha_info.bind("<MouseWheel>", _ao_rolar_mouse)

            badge_bg = "#DCFCE7" if s_disp >= it.saldo_pendente else ("#FEF3C7" if s_disp > 0 else "#FEE2E2")
            badge_fg = "#15803D" if s_disp >= it.saldo_pendente else ("#B45309" if s_disp > 0 else "#B91C1C")

            lbl_qtd_info = ttk.Label(
                f_linha_info,
                text=f"Qtd a Atender: {it.saldo_pendente:.2f} {it.unidade}   |   Disp. Estoque: ",
                font=("Segoe UI", 9),
            )
            lbl_qtd_info.pack(side=tk.LEFT)
            lbl_qtd_info.bind("<MouseWheel>", _ao_rolar_mouse)

            lbl_badge_disp = tk.Label(
                f_linha_info,
                text=f"{s_disp:.2f} {it.unidade}",
                bg=badge_bg,
                fg=badge_fg,
                font=("Segoe UI", 9, "bold"),
                padx=4,
                pady=0,
                relief=tk.RIDGE,
            )
            lbl_badge_disp.pack(side=tk.LEFT)
            lbl_badge_disp.bind("<MouseWheel>", _ao_rolar_mouse)

            var_lote = tk.StringVar()
            vincular_maiusculo(var_lote)
            info["var_lote"] = var_lote

            if not is_servico:
                f_linha_lote = ttk.Frame(card)
                f_linha_lote.pack(fill=tk.X, pady=(2, 0))
                f_linha_lote.bind("<MouseWheel>", _ao_rolar_mouse)

                lbl_lote_txt = "Lote Obrigatório: *" if ctrl else "Lote (Opcional):"
                lbl_cor = "#B45309" if ctrl else "#334155"
                lbl_lote = tk.Label(
                    f_linha_lote,
                    text=lbl_lote_txt,
                    font=("Segoe UI", 9, "bold" if ctrl else "normal"),
                    fg=lbl_cor,
                )
                lbl_lote.pack(side=tk.LEFT, padx=(0, 6))
                lbl_lote.bind("<MouseWheel>", _ao_rolar_mouse)

                # Sugere lote com saldo se houver
                if lote_svc and p_int:
                    try:
                        lotes_prod = lote_svc.obter_lotes(p_int)
                        lote_com_saldo = next((l for l in lotes_prod if (l.saldo_atual or 0) > 0), None)
                        if lote_com_saldo:
                            var_lote.set(lote_com_saldo.numero_lote)
                    except Exception:
                        pass

                ent_lote = ttk.Entry(f_linha_lote, textvariable=var_lote, width=16, font=("Segoe UI", 9, "bold"))
                ent_lote.pack(side=tk.LEFT, padx=(0, 6))
                info["ent_lote"] = ent_lote

                def _criar_consultar_cb(prod_id, v_lote):
                    def _consultar():
                        from lotes import abrir_janela_lotes
                        abrir_janela_lotes(modal_f7, prodcod=prod_id, callback=lambda num: v_lote.set(num))
                    return _consultar

                btn_lote = ttk.Button(f_linha_lote, text="🔍 Lotes (F4)", command=_criar_consultar_cb(p_int, var_lote))
                btn_lote.pack(side=tk.LEFT)

        # Frame de Observação
        f_obs = ttk.Frame(f_cont)
        f_obs.pack(fill=tk.X, pady=(4, 10))
        ttk.Label(f_obs, text="Observação:").pack(side=tk.LEFT, padx=(0, 6))
        var_obs = tk.StringVar(value=f"BAIXA TOTAL REQUISICAO {req_num} VIA ATENDIMENTO RAPIDO")
        vincular_maiusculo(var_obs)
        ent_obs = ttk.Entry(f_obs, textvariable=var_obs)
        ent_obs.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Botões
        b_box = ttk.Frame(f_cont)
        b_box.pack(fill=tk.X, pady=(4, 0))

        def confirmar_f7():
            mapa_lotes_final = {}
            for info in itens_info:
                it = info["item"]
                p_int = info["p_int"]
                ctrl = info["controla_lote"]
                var_l = info.get("var_lote")
                lote_val = var_l.get().strip().upper() if var_l else ""
                mapa_lotes_final[it.item_seq] = lote_val

                if not is_servico:
                    if ctrl:
                        if not lote_val:
                            messagebox.showwarning(
                                "Lote Obrigatório",
                                f"O item {it.item_seq} ('{it.prodnome}') possui CONTROLE DE LOTE ativado.\n\n"
                                "Por favor, informe ou selecione o Lote do material (clique em 🔍 Lotes ou tecle F4).",
                                parent=modal_f7,
                            )
                            ent_l = info.get("ent_lote")
                            if ent_l:
                                ent_l.focus_set()
                            return

                        if lote_svc and p_int:
                            if not lote_svc.lote_existe(p_int, lote_val):
                                resp = messagebox.askyesno(
                                    "Lote Não Encontrado",
                                    f"O lote '{lote_val}' não existe para o produto '{it.prodnome}'.\n\nDeseja abrir o cadastro de lotes?",
                                    parent=modal_f7,
                                )
                                if resp:
                                    from lotes import abrir_janela_lotes
                                    abrir_janela_lotes(
                                        modal_f7,
                                        prodcod=p_int,
                                        numero_lote=lote_val,
                                        callback=lambda novo_lote, v=var_l: v.set(novo_lote),
                                    )
                                return

                            # Validação de Vencimento do Lote
                            from lotes.alerta_vencimento_view import exibir_alerta_vencimento_lote
                            nivel, dias, dt_val_fmt = lote_svc.verificar_vencimento_lote(p_int, lote_val)

                            if nivel == "ROXO":
                                # BLOQUEIO ABSOLUTO (0 a 5 dias ou vencido)
                                exibir_alerta_vencimento_lote(
                                    modal_f7,
                                    nivel="ROXO",
                                    numero_lote=lote_val,
                                    prodnome=it.prodnome,
                                    data_validade=dt_val_fmt,
                                    dias_restantes=dias,
                                )
                                return
                            elif nivel in ("VERMELHO", "AMARELO"):
                                prosseguir = exibir_alerta_vencimento_lote(
                                    modal_f7,
                                    nivel=nivel,
                                    numero_lote=lote_val,
                                    prodnome=it.prodnome,
                                    data_validade=dt_val_fmt,
                                    dias_restantes=dias,
                                )
                                if not prosseguir:
                                    return
                    else:
                        # Se não controla lote obrigatoriamente, mas lote existente foi digitado, valida vencimento
                        if lote_val and lote_svc and p_int and lote_svc.lote_existe(p_int, lote_val):
                            from lotes.alerta_vencimento_view import exibir_alerta_vencimento_lote
                            nivel, dias, dt_val_fmt = lote_svc.verificar_vencimento_lote(p_int, lote_val)
                            if nivel == "ROXO":
                                exibir_alerta_vencimento_lote(
                                    modal_f7,
                                    nivel="ROXO",
                                    numero_lote=lote_val,
                                    prodnome=it.prodnome,
                                    data_validade=dt_val_fmt,
                                    dias_restantes=dias,
                                )
                                return
                            elif nivel in ("VERMELHO", "AMARELO"):
                                if not exibir_alerta_vencimento_lote(modal_f7, nivel, lote_val, it.prodnome, dt_val_fmt, dias):
                                    return

            # Efetua o atendimento total
            res = self.service.atender_requisicao_completa(
                req_num=req_num,
                empcod=empcod,
                observacao=var_obs.get(),
                itens_lotes=mapa_lotes_final,
            )
            if res.sucesso:
                if is_servico:
                    try:
                        from contas_a_pagar.service import ContasPagarService
                        from logon import sessao_usuario_atual
                        user_login = sessao_usuario_atual.get("login", "")
                        cp_service = ContasPagarService()
                        for it in itens_pendentes:
                            cp_service.gerar_titulo_por_servico_requisicao(
                                empcod=empcod,
                                req_num=req_num,
                                item_seq=it.item_seq,
                                descricao_servico=it.prodnome,
                                valor_total=0.0,
                                codigo_movimento_estoque=res.codigo or 0,
                                centro_custo=req.centro_custo,
                                observacao="ATENDIMENTO TOTAL DE REQUISICAO DE SERVICO",
                                usuario=user_login,
                            )
                    except Exception:
                        pass
                messagebox.showinfo("Sucesso", res.mensagem, parent=self)
                modal_f7.destroy()
                self.carregar_requisicoes()
                self.tree_req.selection_set(req_num)
                self._ao_selecionar_requisicao()
            else:
                messagebox.showerror("Erro ao Atender", res.mensagem, parent=modal_f7)

        btn_conf = tk.Button(
            b_box,
            text="✔ Confirmar Atendimento Total (Enter)",
            bg="#16A34A",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=4,
            relief=tk.FLAT,
            command=confirmar_f7,
        )
        btn_conf.pack(side=tk.RIGHT, padx=(6, 0))

        btn_canc = ttk.Button(b_box, text="Cancelar (Esc)", command=modal_f7.destroy)
        btn_canc.pack(side=tk.RIGHT)

        modal_f7.bind("<Return>", lambda e: confirmar_f7())
        modal_f7.bind("<Escape>", lambda e: modal_f7.destroy())

    def _abrir_atendimento_selecionado(self):
        item = self._obter_item_selecionado()
        if not item:
            return

        if self._requisicao_selecionada.status == "Cancelada":
            messagebox.showerror("Erro", "Requisições canceladas não podem ser atendidas.", parent=self)
            return

        if item.saldo_pendente <= 0.0001:
            messagebox.showinfo("Aviso", f"O item {item.item_seq} já está totalmente atendido!", parent=self)
            return

        empcod = item.empcod or self.var_empcod.get().strip() or "1.01"
        s_atual, s_reserv, s_disp = self.service.obter_saldo_produto(item.prodcod_estr, empcod=empcod)

        # Abre modal moderno de atendimento
        modal = tk.Toplevel(self)
        try:
            modal.title(f"Atender Item {item.item_seq} - Req {item.req_num}")
            modal.transient(self)
            modal.grab_set()
            centralizar_janela(modal, self, 560, 480)

            p_int = None
            try:
                p_int = int(item.prodcod_estr)
            except Exception:
                pass

            lote_svc = None
            controla_lote = False
            if self.service and hasattr(self.service, "_repo") and self.service._repo and self.service._repo.conn:
                try:
                    from lotes.repository import LotesRepository
                    from lotes.service import LotesService
                    lote_svc = LotesService(LotesRepository(self.service._repo.conn))
                    if p_int:
                        controla_lote = lote_svc.produto_controla_lote(p_int)
                except Exception:
                    pass

            f_cont = ttk.Frame(modal, padding=16)
            f_cont.pack(fill=tk.BOTH, expand=True)

            lbl_top = ttk.Label(
                f_cont,
                text=f"Atendimento de Requisição Nº {item.req_num}",
                font=("Segoe UI", 12, "bold"),
                foreground="#1E3A8A",
            )
            lbl_top.pack(anchor=tk.W, pady=(0, 10))

            # Detalhes do item
            grid_info = ttk.LabelFrame(f_cont, text=" Dados do Material e Saldo em Estoque ", padding=10)
            grid_info.pack(fill=tk.X, pady=(0, 12))

            ttk.Label(grid_info, text="Produto:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
            ttk.Label(grid_info, text=f"{item.prodcod_estr} - {item.prodnome}").grid(row=0, column=1, sticky=tk.W, pady=2)

            ttk.Label(grid_info, text="Unidade:").grid(row=1, column=0, sticky=tk.W, pady=2)
            ttk.Label(grid_info, text=item.unidade).grid(row=1, column=1, sticky=tk.W, pady=2)

            ttk.Label(grid_info, text="Qtd Solicitada:").grid(row=2, column=0, sticky=tk.W, pady=2)
            ttk.Label(grid_info, text=f"{item.qtd_solicitada:.2f}").grid(row=2, column=1, sticky=tk.W, pady=2)

            ttk.Label(grid_info, text="Qtd Já Atendida:").grid(row=3, column=0, sticky=tk.W, pady=2)
            ttk.Label(grid_info, text=f"{item.qtd_atendida:.2f}").grid(row=3, column=1, sticky=tk.W, pady=2)

            ttk.Label(grid_info, text="Saldo Pendente:", font=("Segoe UI", 9, "bold"), foreground="#B45309").grid(row=4, column=0, sticky=tk.W, pady=2)
            ttk.Label(grid_info, text=f"{item.saldo_pendente:.2f}", font=("Segoe UI", 9, "bold"), foreground="#B45309").grid(row=4, column=1, sticky=tk.W, pady=2)

            # Saldo Físico / Disponível
            badge_bg = "#DCFCE7" if s_disp >= item.saldo_pendente else ("#FEF3C7" if s_disp > 0 else "#FEE2E2")
            badge_fg = "#15803D" if s_disp >= item.saldo_pendente else ("#B45309" if s_disp > 0 else "#B91C1C")
            texto_saldo = f"{s_disp:.2f} {item.unidade} (Disponível: {s_disp:.2f} | Físico: {s_atual:.2f})"
            if s_disp <= 0:
                texto_saldo += " [SEM SALDO]"
            elif s_disp < item.saldo_pendente:
                texto_saldo += " [SALDO PARCIAL]"

            ttk.Label(grid_info, text="Saldo em Estoque:", font=("Segoe UI", 9, "bold")).grid(row=5, column=0, sticky=tk.W, pady=2)
            lbl_saldo_estq = tk.Label(
                grid_info,
                text=texto_saldo,
                bg=badge_bg,
                fg=badge_fg,
                font=("Segoe UI", 9, "bold"),
                padx=6,
                pady=1,
                relief=tk.RIDGE,
            )
            lbl_saldo_estq.grid(row=5, column=1, sticky=tk.W, pady=2)

            tipo_req = getattr(self._requisicao_selecionada, "tipo_requisicao", "Produto") or "Produto"
            is_servico = tipo_req.lower().startswith("serv")

            ttk.Label(grid_info, text="Tipo da Requisição:", font=("Segoe UI", 9, "bold")).grid(row=6, column=0, sticky=tk.W, pady=2)
            lbl_tipo_req = tk.Label(
                grid_info,
                text=f"{tipo_req.upper()} (Gera Contas a Pagar Automático)" if is_servico else f"{tipo_req.upper()} (Material/Estoque)",
                bg="#EFF6FF" if is_servico else "#F8FAFC",
                fg="#1D4ED8" if is_servico else "#334155",
                font=("Segoe UI", 9, "bold"),
                padx=6,
                pady=1,
                relief=tk.RIDGE,
            )
            lbl_tipo_req.grid(row=6, column=1, sticky=tk.W, pady=2)

            # Campos de atendimento
            grid_form = ttk.Frame(f_cont)
            grid_form.pack(fill=tk.X, pady=(0, 15))

            ttk.Label(grid_form, text="Quantidade a Atender: *", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=4)
            var_qtd = tk.StringVar(value=f"{item.saldo_pendente:.2f}")
            ent_qtd = ttk.Entry(grid_form, textvariable=var_qtd, width=15, font=("Segoe UI", 10, "bold"))
            ent_qtd.grid(row=0, column=1, sticky=tk.W, padx=6, pady=4)
            ent_qtd.select_range(0, tk.END)
            ent_qtd.focus_set()

            var_val_servico = tk.StringVar(value="0,00")
            if is_servico:
                ttk.Label(grid_form, text="Valor Total Serviço (R$):", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=4)
                ent_val_s = ttk.Entry(grid_form, textvariable=var_val_servico, width=15, font=("Segoe UI", 10, "bold"))
                ent_val_s.grid(row=1, column=1, sticky=tk.W, padx=6, pady=4)

            # Campo Lote (se não for serviço)
            var_lote = tk.StringVar()
            vincular_maiusculo(var_lote)
            if not is_servico and lote_svc and p_int:
                try:
                    lotes_cad = lote_svc.obter_lotes(p_int)
                    lote_sugestao = next((l for l in lotes_cad if (l.saldo_atual or 0) > 0), None)
                    if lote_sugestao:
                        var_lote.set(lote_sugestao.numero_lote)
                except Exception:
                    pass
            ent_lote = None
            if not is_servico:
                lbl_lote_txt = "Lote do Material: *" if controla_lote else "Lote do Material:"
                ttk.Label(grid_form, text=lbl_lote_txt, font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=4)
                f_lote_box = ttk.Frame(grid_form)
                f_lote_box.grid(row=1, column=1, sticky=tk.W, padx=6, pady=4)

                ent_lote = ttk.Entry(f_lote_box, textvariable=var_lote, width=16, font=("Segoe UI", 9, "bold"))
                ent_lote.pack(side=tk.LEFT, padx=(0, 6))

                def _consultar_lotes_atend():
                    from lotes import abrir_janela_lotes
                    abrir_janela_lotes(modal, prodcod=p_int, callback=lambda num: var_lote.set(num))

                btn_lote = ttk.Button(f_lote_box, text="🔍 Lotes (F4)", command=_consultar_lotes_atend)
                btn_lote.pack(side=tk.LEFT)

            row_obs_idx = 2
            ttk.Label(grid_form, text="Observação:").grid(row=row_obs_idx, column=0, sticky=tk.W, pady=4)
            var_obs = tk.StringVar()
            vincular_maiusculo(var_obs)
            ent_obs = ttk.Entry(grid_form, textvariable=var_obs, width=32)
            ent_obs.grid(row=row_obs_idx, column=1, sticky=tk.W, padx=6, pady=4)

            # Botões
            b_box = ttk.Frame(f_cont)
            b_box.pack(fill=tk.X, pady=(5, 0))

            def confirmar():
                try:
                    qtd_val = float(var_qtd.get().replace(",", "."))
                except ValueError:
                    messagebox.showerror("Erro", "Quantidade inválida.", parent=modal)
                    ent_qtd.focus_set()
                    return

                if qtd_val <= 0:
                    messagebox.showerror("Erro", "A quantidade a atender deve ser maior que zero.", parent=modal)
                    ent_qtd.focus_set()
                    return

                if qtd_val > (item.saldo_pendente + 0.0001):
                    messagebox.showerror(
                        "Erro",
                        f"A quantidade a atender ({qtd_val}) não pode ser maior que o saldo pendente ({item.saldo_pendente:.2f}).",
                        parent=modal,
                    )
                    ent_qtd.focus_set()
                    return

                if qtd_val > (s_disp + 0.0001):
                    permite_neg = self.service.permite_estoque_negativo(item.empcod) if self.service else False
                    if not permite_neg:
                        messagebox.showwarning(
                            "Atenção: Saldo Insuficiente",
                            "O sistema não permite estoque negativo, este produto não tem em estoque e não permite movimentação",
                            parent=modal,
                        )
                        return
                    elif not messagebox.askyesno(
                        "Atenção: Saldo Insuficiente",
                        f"A quantidade a atender ({qtd_val:.2f}) é maior que o saldo disponível em estoque ({s_disp:.2f}).\n\n"
                        f"Esta operação resultará em saldo negativo para o produto.\n\n"
                        f"Deseja confirmar o atendimento mesmo assim?",
                        parent=modal,
                    ):
                        return

                # Validação de Controle de Lote e Vencimento
                lote_val = var_lote.get().strip().upper() if not is_servico else ""
                if not is_servico:
                    if controla_lote:
                        if not lote_val:
                            messagebox.showwarning(
                                "Lote Obrigatório",
                                f"O produto '{item.prodnome}' possui CONTROLE DE LOTE ativado.\n\n"
                                "Por favor, informe ou selecione o Lote do material (tecle F4).",
                                parent=modal,
                            )
                            if ent_lote:
                                ent_lote.focus_set()
                            return

                        if lote_svc and p_int:
                            if not lote_svc.lote_existe(p_int, lote_val):
                                resp = messagebox.askyesno(
                                    "Lote Não Encontrado",
                                    f"O número de lote '{lote_val}' não existe para este produto.\n\nDeseja abrir o cadastro de lotes?",
                                    parent=modal,
                                )
                                if resp:
                                    from lotes import abrir_janela_lotes
                                    abrir_janela_lotes(
                                        modal,
                                        prodcod=p_int,
                                        numero_lote=lote_val,
                                        callback=lambda novo_lote: var_lote.set(novo_lote),
                                    )
                                return

                            # Validação de Vencimento do Lote
                            from lotes.alerta_vencimento_view import exibir_alerta_vencimento_lote
                            nivel, dias, dt_val_fmt = lote_svc.verificar_vencimento_lote(p_int, lote_val)

                            if nivel == "ROXO":
                                # BLOQUEIO ABSOLUTO (0 a 5 dias ou vencido)
                                exibir_alerta_vencimento_lote(
                                    modal,
                                    nivel="ROXO",
                                    numero_lote=lote_val,
                                    prodnome=item.prodnome,
                                    data_validade=dt_val_fmt,
                                    dias_restantes=dias,
                                )
                                if messagebox.askyesno(
                                    "Cancelar / Baixar Item por Lote Vencido",
                                    f"O lote '{lote_val}' possui vencimento crítico ou vencido ({dt_val_fmt}) e o atendimento está bloqueado.\n\n"
                                    f"Deseja cancelar o item {item.item_seq} agora para dar baixa na requisição?",
                                    parent=modal,
                                ):
                                    modal.destroy()
                                    self._executar_cancelamento_item_direto(item, f"LOTE VENCIDO: {lote_val} (VALIDADE: {dt_val_fmt})")
                                    return
                                return
                            elif nivel in ("VERMELHO", "AMARELO"):
                                prosseguir = exibir_alerta_vencimento_lote(
                                    modal,
                                    nivel=nivel,
                                    numero_lote=lote_val,
                                    prodnome=item.prodnome,
                                    data_validade=dt_val_fmt,
                                    dias_restantes=dias,
                                )
                                if not prosseguir:
                                    return
                    else:
                        # Se não controla lote obrigatoriamente, mas lote existente foi digitado, valida vencimento
                        if lote_val and lote_svc and p_int and lote_svc.lote_existe(p_int, lote_val):
                            from lotes.alerta_vencimento_view import exibir_alerta_vencimento_lote
                            nivel, dias, dt_val_fmt = lote_svc.verificar_vencimento_lote(p_int, lote_val)
                            if nivel == "ROXO":
                                exibir_alerta_vencimento_lote(
                                    modal,
                                    nivel="ROXO",
                                    numero_lote=lote_val,
                                    prodnome=item.prodnome,
                                    data_validade=dt_val_fmt,
                                    dias_restantes=dias,
                                )
                                if messagebox.askyesno(
                                    "Cancelar / Baixar Item por Lote Vencido",
                                    f"O lote '{lote_val}' possui vencimento crítico ou vencido ({dt_val_fmt}) e o atendimento está bloqueado.\n\n"
                                    f"Deseja cancelar o item {item.item_seq} agora para dar baixa na requisição?",
                                    parent=modal,
                                ):
                                    modal.destroy()
                                    self._executar_cancelamento_item_direto(item, f"LOTE VENCIDO: {lote_val} (VALIDADE: {dt_val_fmt})")
                                    return
                                return
                            elif nivel in ("VERMELHO", "AMARELO"):
                                if not exibir_alerta_vencimento_lote(modal, nivel, lote_val, item.prodnome, dt_val_fmt, dias):
                                    return

                res = self.service.atender_item_requisicao(
                    req_num=item.req_num,
                    item_seq=item.item_seq,
                    qtd_atender=qtd_val,
                    empcod=item.empcod,
                    observacao=var_obs.get(),
                    numero_lote=lote_val,
                )
                if res.sucesso:
                    if is_servico:
                        try:
                            from contas_a_pagar.service import ContasPagarService
                            from logon import sessao_usuario_atual
                            user_login = sessao_usuario_atual.get("login", "")
                            cp_service = ContasPagarService()
                            v_str = var_val_servico.get().replace(".", "").replace(",", ".").strip()
                            v_val = float(v_str) if v_str else 0.0
                            cctrl = getattr(self._requisicao_selecionada, "centro_custo", "")
                            sucesso_cp, msg_cp, doc_id = cp_service.gerar_titulo_por_servico_requisicao(
                                empcod=item.empcod,
                                req_num=item.req_num,
                                item_seq=item.item_seq,
                                descricao_servico=item.prodnome,
                                valor_total=v_val,
                                codigo_movimento_estoque=res.codigo or 0,
                                centro_custo=cctrl,
                                observacao=var_obs.get(),
                                usuario=user_login,
                            )
                            if sucesso_cp and doc_id > 0:
                                res.mensagem += f"\n\nContas a Pagar gerado com sucesso (Título Nº {doc_id})."
                        except Exception as e_cp:
                            pass
                    messagebox.showinfo("Sucesso", res.mensagem, parent=self)
                    modal.destroy()
                    self.carregar_requisicoes()
                    self.tree_req.selection_set(item.req_num)
                    self._ao_selecionar_requisicao()
                else:
                    messagebox.showerror("Erro ao Atender", res.mensagem, parent=modal)

            btn_conf = tk.Button(
                b_box,
                text="✔ Confirmar Atendimento (Enter)",
                bg="#16A34A",
                fg="white",
                font=("Segoe UI", 9, "bold"),
                padx=10,
                pady=4,
                relief=tk.FLAT,
                command=confirmar,
            )
            btn_conf.pack(side=tk.RIGHT, padx=(6, 0))

            btn_canc = ttk.Button(b_box, text="Cancelar (Esc)", command=modal.destroy)
            btn_canc.pack(side=tk.RIGHT)

            def _cancelar_item_pelo_atendimento():
                modal.destroy()
                self._abrir_modal_cancelamento_item(item)

            btn_canc_item = tk.Button(
                b_box,
                text="✖ Cancelar/Baixar Item (F8)",
                bg="#DC2626",
                fg="white",
                font=("Segoe UI", 9, "bold"),
                padx=10,
                pady=4,
                relief=tk.FLAT,
                command=_cancelar_item_pelo_atendimento,
            )
            btn_canc_item.pack(side=tk.LEFT)
            modal.bind("<F8>", lambda e: _cancelar_item_pelo_atendimento())

            nav_widgets = [ent_qtd]
            if not is_servico and ent_lote:
                nav_widgets.append(ent_lote)
            elif is_servico:
                nav_widgets.append(ent_val_s)
            nav_widgets.extend([ent_obs, btn_conf])

            configurar_navegacao_enter(nav_widgets)
            modal.bind("<Return>", lambda e: confirmar())
            modal.bind("<Escape>", lambda e: modal.destroy())
            if not is_servico:
                modal.bind("<F4>", lambda e: _consultar_lotes_atend())
        except Exception as e:
            try:
                modal.destroy()
            except Exception:
                pass
            messagebox.showerror("Erro ao Abrir Atendimento", f"Falha ao carregar tela de atendimento do item:\n{e}", parent=self)

    def _executar_cancelamento_item_direto(self, item: ItemRequisicaoDTO, motivo: str):
        res = self.service.cancelar_item_requisicao(
            req_num=item.req_num,
            item_seq=item.item_seq,
            motivo=motivo,
            empcod=item.empcod,
        )
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem, parent=self)
            self.carregar_requisicoes()
            self.tree_req.selection_set(item.req_num)
            self._ao_selecionar_requisicao()
        else:
            messagebox.showerror("Erro ao Cancelar Item", res.mensagem, parent=self)

    # -------------------------------------------------------------------------
    # MODAL DE DEVOLUÇÃO E CANCELAMENTO/BAIXA DE ITENS (F8)
    # -------------------------------------------------------------------------
    def _abrir_devolucao_selecionada(self):
        item = self._obter_item_selecionado()
        if not item:
            return

        if str(item.status_item).strip() == "Cancelado":
            messagebox.showinfo("Aviso", f"O item {item.item_seq} já está cancelado.", parent=self)
            return

        if self._requisicao_selecionada and self._requisicao_selecionada.status == "Cancelada":
            messagebox.showinfo("Aviso", "Esta requisição já está cancelada.", parent=self)
            return

        # Caso 1: Item possui apenas saldo pendente (ainda não foi atendido)
        # Ex: lote vencido, material em falta, desistência -> Cancela e baixa o item da requisição
        if item.qtd_atendida <= 0.0001:
            self._abrir_modal_cancelamento_item(item)
            return

        # Caso 2: Atendimento parcial com saldo pendente restante
        if item.saldo_pendente > 0.0001:
            self._abrir_modal_devolucao_mista(item)
            return

        # Caso 3: Item totalmente atendido -> Devolução de estoque
        self._abrir_modal_devolucao_estoque(item)

    def _abrir_modal_cancelamento_item(self, item: ItemRequisicaoDTO):
        modal = tk.Toplevel(self)
        modal.title(f"Cancelar / Baixar Item {item.item_seq} - Req {item.req_num}")
        modal.transient(self)
        modal.grab_set()
        centralizar_janela(modal, self, 560, 390)

        f_cont = ttk.Frame(modal, padding=16)
        f_cont.pack(fill=tk.BOTH, expand=True)

        lbl_top = ttk.Label(
            f_cont,
            text=f"Cancelar e Baixar Item {item.item_seq} da Requisição Nº {item.req_num}",
            font=("Segoe UI", 12, "bold"),
            foreground="#DC2626",
        )
        lbl_top.pack(anchor=tk.W, pady=(0, 10))

        grid_info = ttk.LabelFrame(f_cont, text=" Dados do Material a Cancelar / Baixar ", padding=10)
        grid_info.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(grid_info, text="Produto:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(grid_info, text=f"{item.prodcod_estr} - {item.prodnome}").grid(row=0, column=1, sticky=tk.W, pady=2)

        ttk.Label(grid_info, text="Qtd Pendente a Baixar:", font=("Segoe UI", 9, "bold"), foreground="#DC2626").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(grid_info, text=f"{item.saldo_pendente:.2f} {item.unidade}", font=("Segoe UI", 9, "bold"), foreground="#DC2626").grid(row=1, column=1, sticky=tk.W, pady=2)

        grid_form = ttk.Frame(f_cont)
        grid_form.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(grid_form, text="Motivo da Baixa/Cancelamento: *", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=4)
        var_motivo = tk.StringVar(value="LOTE VENCIDO")
        cb_motivo = ttk.Combobox(
            grid_form,
            textvariable=var_motivo,
            values=[
                "LOTE VENCIDO",
                "LOTE PRÓXIMO AO VENCIMENTO",
                "MATERIAL SEM ESTOQUE DISPONÍVEL",
                "DESISTÊNCIA / CANCELAMENTO PELO REQUISITANTE",
                "MATERIAL AVARIADO OU NÃO CONFORME",
                "OUTRO MOTIVO",
            ],
            width=32,
        )
        cb_motivo.grid(row=0, column=1, sticky=tk.W, padx=6, pady=4)

        ttk.Label(grid_form, text="Detalhes / Observação:").grid(row=1, column=0, sticky=tk.W, pady=4)
        var_obs = tk.StringVar()
        vincular_maiusculo(var_obs)
        ent_obs = ttk.Entry(grid_form, textvariable=var_obs, width=34)
        ent_obs.grid(row=1, column=1, sticky=tk.W, padx=6, pady=4)
        ent_obs.focus_set()

        b_box = ttk.Frame(f_cont)
        b_box.pack(fill=tk.X, pady=(5, 0))

        def confirmar_canc():
            m_base = var_motivo.get().strip().upper() or "CANCELADO PELO USUÁRIO"
            m_det = var_obs.get().strip().upper()
            motivo_final = f"{m_base}: {m_det}" if m_det else m_base

            res = self.service.cancelar_item_requisicao(
                req_num=item.req_num,
                item_seq=item.item_seq,
                motivo=motivo_final,
                empcod=item.empcod,
            )
            if res.sucesso:
                messagebox.showinfo("Sucesso", res.mensagem, parent=self)
                modal.destroy()
                self.carregar_requisicoes()
                self.tree_req.selection_set(item.req_num)
                self._ao_selecionar_requisicao()
            else:
                messagebox.showerror("Erro ao Cancelar Item", res.mensagem, parent=modal)

        btn_conf = tk.Button(
            b_box,
            text="✔ Confirmar Cancelamento / Baixa (Enter)",
            bg="#DC2626",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            relief=tk.FLAT,
            command=confirmar_canc,
        )
        btn_conf.pack(side=tk.RIGHT, padx=(6, 0))

        btn_canc = ttk.Button(b_box, text="Voltar (Esc)", command=modal.destroy)
        btn_canc.pack(side=tk.RIGHT)

        configurar_navegacao_enter([cb_motivo, ent_obs, btn_conf])
        modal.bind("<Return>", lambda e: confirmar_canc())
        modal.bind("<Escape>", lambda e: modal.destroy())

    def _abrir_modal_devolucao_mista(self, item: ItemRequisicaoDTO):
        modal = tk.Toplevel(self)
        modal.title(f"Devolver / Cancelar Item {item.item_seq} - Req {item.req_num}")
        modal.transient(self)
        modal.grab_set()
        centralizar_janela(modal, self, 580, 460)

        f_cont = ttk.Frame(modal, padding=16)
        f_cont.pack(fill=tk.BOTH, expand=True)

        lbl_top = ttk.Label(
            f_cont,
            text=f"Ajuste do Item {item.item_seq} - Req Nº {item.req_num}",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
        )
        lbl_top.pack(anchor=tk.W, pady=(0, 10))

        grid_info = ttk.LabelFrame(f_cont, text=" Dados do Material ", padding=10)
        grid_info.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(grid_info, text="Produto:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(grid_info, text=f"{item.prodcod_estr} - {item.prodnome}").grid(row=0, column=1, sticky=tk.W, pady=2)

        ttk.Label(grid_info, text="Qtd Atendida Anteriormente:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(grid_info, text=f"{item.qtd_atendida:.2f} {item.unidade}", font=("Segoe UI", 9, "bold"), foreground="#0284C7").grid(row=1, column=1, sticky=tk.W, pady=2)

        ttk.Label(grid_info, text="Saldo Pendente Atual:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(grid_info, text=f"{item.saldo_pendente:.2f} {item.unidade}", font=("Segoe UI", 9, "bold"), foreground="#DC2626").grid(row=2, column=1, sticky=tk.W, pady=2)

        f_acao = ttk.LabelFrame(f_cont, text=" Selecione a Operação ", padding=10)
        f_acao.pack(fill=tk.X, pady=(0, 12))

        var_tipo_op = tk.StringVar(value="CANCELAR_PENDENTE")
        rb_canc = ttk.Radiobutton(
            f_acao,
            text=f"Cancelar Saldo Pendente Restante ({item.saldo_pendente:.2f} {item.unidade}) e Baixar o Item",
            variable=var_tipo_op,
            value="CANCELAR_PENDENTE",
        )
        rb_canc.pack(anchor=tk.W, pady=2)

        rb_dev = ttk.Radiobutton(
            f_acao,
            text=f"Devolver Material Atendido ({item.qtd_atendida:.2f} {item.unidade}) de volta ao Estoque",
            variable=var_tipo_op,
            value="DEVOLVER_ESTOQUE",
        )
        rb_dev.pack(anchor=tk.W, pady=2)

        grid_form = ttk.Frame(f_cont)
        grid_form.pack(fill=tk.X, pady=(0, 15))

        lbl_campo1 = ttk.Label(grid_form, text="Motivo da Baixa: *", font=("Segoe UI", 9, "bold"))
        lbl_campo1.grid(row=0, column=0, sticky=tk.W, pady=4)

        var_motivo = tk.StringVar(value="LOTE VENCIDO")
        cb_motivo = ttk.Combobox(
            grid_form,
            textvariable=var_motivo,
            values=[
                "LOTE VENCIDO",
                "LOTE PRÓXIMO AO VENCIMENTO",
                "MATERIAL SEM ESTOQUE DISPONÍVEL",
                "DESISTÊNCIA / CANCELAMENTO PELO REQUISITANTE",
                "MATERIAL AVARIADO OU NÃO CONFORME",
                "OUTRO MOTIVO",
            ],
            width=32,
        )
        cb_motivo.grid(row=0, column=1, sticky=tk.W, padx=6, pady=4)

        var_qtd_dev = tk.StringVar(value=f"{item.qtd_atendida:.2f}")
        ent_qtd_dev = ttk.Entry(grid_form, textvariable=var_qtd_dev, width=15, font=("Segoe UI", 9, "bold"))

        ttk.Label(grid_form, text="Justificativa / Detalhes:").grid(row=1, column=0, sticky=tk.W, pady=4)
        var_obs = tk.StringVar()
        vincular_maiusculo(var_obs)
        ent_obs = ttk.Entry(grid_form, textvariable=var_obs, width=34)
        ent_obs.grid(row=1, column=1, sticky=tk.W, padx=6, pady=4)

        def _ajustar_campos_op():
            if var_tipo_op.get() == "CANCELAR_PENDENTE":
                lbl_campo1.config(text="Motivo da Baixa: *")
                ent_qtd_dev.grid_forget()
                cb_motivo.grid(row=0, column=1, sticky=tk.W, padx=6, pady=4)
                btn_exec.config(text="✔ Confirmar Cancelamento / Baixa", bg="#DC2626")
            else:
                lbl_campo1.config(text="Quantidade a Devolver: *")
                cb_motivo.grid_forget()
                ent_qtd_dev.grid(row=0, column=1, sticky=tk.W, padx=6, pady=4)
                btn_exec.config(text="✔ Confirmar Devolução ao Estoque", bg="#0284C7")

        rb_canc.config(command=_ajustar_campos_op)
        rb_dev.config(command=_ajustar_campos_op)

        b_box = ttk.Frame(f_cont)
        b_box.pack(fill=tk.X, pady=(5, 0))

        def executar_op():
            if var_tipo_op.get() == "CANCELAR_PENDENTE":
                m_base = var_motivo.get().strip().upper() or "CANCELADO PELO USUÁRIO"
                m_det = var_obs.get().strip().upper()
                motivo_final = f"{m_base}: {m_det}" if m_det else m_base
                res = self.service.cancelar_item_requisicao(
                    req_num=item.req_num,
                    item_seq=item.item_seq,
                    motivo=motivo_final,
                    empcod=item.empcod,
                )
            else:
                try:
                    q_val = float(var_qtd_dev.get().replace(",", "."))
                except ValueError:
                    messagebox.showerror("Erro", "Quantidade inválida.", parent=modal)
                    return
                if q_val <= 0 or q_val > (item.qtd_atendida + 0.0001):
                    messagebox.showerror("Erro", f"Quantidade deve ser entre 0 e {item.qtd_atendida:.2f}.", parent=modal)
                    return
                res = self.service.devolver_item_requisicao(
                    req_num=item.req_num,
                    item_seq=item.item_seq,
                    qtd_devolver=q_val,
                    empcod=item.empcod,
                    observacao=var_obs.get(),
                )

            if res.sucesso:
                messagebox.showinfo("Sucesso", res.mensagem, parent=self)
                modal.destroy()
                self.carregar_requisicoes()
                self.tree_req.selection_set(item.req_num)
                self._ao_selecionar_requisicao()
            else:
                messagebox.showerror("Erro na Operação", res.mensagem, parent=modal)

        btn_exec = tk.Button(
            b_box,
            text="✔ Confirmar Cancelamento / Baixa",
            bg="#DC2626",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            relief=tk.FLAT,
            command=executar_op,
        )
        btn_exec.pack(side=tk.RIGHT, padx=(6, 0))

        btn_canc = ttk.Button(b_box, text="Voltar (Esc)", command=modal.destroy)
        btn_canc.pack(side=tk.RIGHT)

        modal.bind("<Return>", lambda e: executar_op())
        modal.bind("<Escape>", lambda e: modal.destroy())

    def _abrir_modal_devolucao_estoque(self, item: ItemRequisicaoDTO):
        modal = tk.Toplevel(self)
        modal.title(f"Devolver Item {item.item_seq} - Req {item.req_num}")
        modal.transient(self)
        modal.grab_set()
        centralizar_janela(modal, self, 500, 360)

        f_cont = ttk.Frame(modal, padding=16)
        f_cont.pack(fill=tk.BOTH, expand=True)

        lbl_top = ttk.Label(
            f_cont,
            text=f"Devolução de Material ao Estoque - Req Nº {item.req_num}",
            font=("Segoe UI", 12, "bold"),
            foreground="#0284C7",
        )
        lbl_top.pack(anchor=tk.W, pady=(0, 10))

        grid_info = ttk.LabelFrame(f_cont, text=" Dados do Material ", padding=10)
        grid_info.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(grid_info, text="Produto:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(grid_info, text=f"{item.prodcod_estr} - {item.prodnome}").grid(row=0, column=1, sticky=tk.W, pady=2)

        ttk.Label(grid_info, text="Qtd Atendida Anteriormente:", font=("Segoe UI", 9, "bold"), foreground="#0284C7").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(grid_info, text=f"{item.qtd_atendida:.2f} {item.unidade}", font=("Segoe UI", 9, "bold"), foreground="#0284C7").grid(row=1, column=1, sticky=tk.W, pady=2)

        grid_form = ttk.Frame(f_cont)
        grid_form.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(grid_form, text="Quantidade a Devolver: *", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=4)
        var_qtd = tk.StringVar(value=f"{item.qtd_atendida:.2f}")
        ent_qtd = ttk.Entry(grid_form, textvariable=var_qtd, width=15, font=("Segoe UI", 10, "bold"))
        ent_qtd.grid(row=0, column=1, sticky=tk.W, padx=6, pady=4)
        ent_qtd.select_range(0, tk.END)
        ent_qtd.focus_set()

        ttk.Label(grid_form, text="Motivo da Devolução:").grid(row=1, column=0, sticky=tk.W, pady=4)
        var_obs = tk.StringVar()
        vincular_maiusculo(var_obs)
        ent_obs = ttk.Entry(grid_form, textvariable=var_obs, width=32)
        ent_obs.grid(row=1, column=1, sticky=tk.W, padx=6, pady=4)

        b_box = ttk.Frame(f_cont)
        b_box.pack(fill=tk.X, pady=(5, 0))

        def confirmar_dev():
            try:
                qtd_val = float(var_qtd.get().replace(",", "."))
            except ValueError:
                messagebox.showerror("Erro", "Quantidade inválida.", parent=modal)
                ent_qtd.focus_set()
                return

            if qtd_val <= 0:
                messagebox.showerror("Erro", "Quantidade a devolver deve ser maior que zero.", parent=modal)
                ent_qtd.focus_set()
                return

            if qtd_val > (item.qtd_atendida + 0.0001):
                messagebox.showerror("Erro", f"Quantidade a devolver não pode superar o total atendido ({item.qtd_atendida:.2f}).", parent=modal)
                ent_qtd.focus_set()
                return

            res = self.service.devolver_item_requisicao(
                req_num=item.req_num,
                item_seq=item.item_seq,
                qtd_devolver=qtd_val,
                empcod=item.empcod,
                observacao=var_obs.get(),
            )
            if res.sucesso:
                messagebox.showinfo("Sucesso", res.mensagem, parent=self)
                modal.destroy()
                self.carregar_requisicoes()
                self.tree_req.selection_set(item.req_num)
                self._ao_selecionar_requisicao()
            else:
                messagebox.showerror("Erro ao Devolver", res.mensagem, parent=modal)

        btn_conf = tk.Button(
            b_box,
            text="✔ Confirmar Devolução (Enter)",
            bg="#0284C7",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            relief=tk.FLAT,
            command=confirmar_dev,
        )
        btn_conf.pack(side=tk.RIGHT, padx=(6, 0))

        btn_canc = ttk.Button(b_box, text="Cancelar (Esc)", command=modal.destroy)
        btn_canc.pack(side=tk.RIGHT)

        configurar_navegacao_enter([ent_qtd, ent_obs, btn_conf])
        modal.bind("<Return>", lambda e: confirmar_dev())
        modal.bind("<Escape>", lambda e: modal.destroy())


    # -------------------------------------------------------------------------
    # MODAL DE CANCELAMENTO
    # -------------------------------------------------------------------------
    def _abrir_cancelamento_selecionado(self):
        if not self._requisicao_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma requisição para cancelar.", parent=self)
            return

        req = self._requisicao_selecionada
        if req.status == "Cancelada":
            messagebox.showinfo("Aviso", "Esta requisição já está cancelada.", parent=self)
            return

        if req.status == "Atendida Total":
            messagebox.showwarning(
                "Aviso",
                f"A requisição {req.req_num} já foi totalmente atendida e não pode ser cancelada diretamente.\n\n"
                "Para retornar materiais ao estoque, utilize a rotina de Devolução de Materiais (F8).",
                parent=self,
            )
            return

        modal = tk.Toplevel(self)
        modal.title(f"Cancelar Requisição {req.req_num}")
        modal.transient(self)
        modal.grab_set()
        centralizar_janela(modal, self, 520, 310)

        f_cont = ttk.Frame(modal, padding=16)
        f_cont.pack(fill=tk.BOTH, expand=True)

        lbl_top = ttk.Label(
            f_cont,
            text=f"Cancelamento da Requisição Nº {req.req_num}",
            font=("Segoe UI", 12, "bold"),
            foreground="#DC2626",
        )
        lbl_top.pack(anchor=tk.W, pady=(0, 6))

        ttk.Label(f_cont, text=f"Requerente: {req.requerente} | Data: {req.data_req} | Centro: {req.centro_custo}").pack(anchor=tk.W, pady=(0, 6))

        if req.status == "Atendida Parcial":
            lbl_aviso_parc = tk.Label(
                f_cont,
                text="Atenção: Requisição com atendimento parcial. As baixas de estoque já efetuadas serão preservadas e apenas os saldos pendentes serão cancelados.",
                bg="#FEF3C7",
                fg="#92400E",
                font=("Segoe UI", 8, "italic"),
                padx=6,
                pady=4,
                wraplength=480,
                justify=tk.LEFT,
                relief=tk.RIDGE,
            )
            lbl_aviso_parc.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(f_cont, text="Justificativa do Cancelamento: *", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 4))
        var_motivo = tk.StringVar()
        vincular_maiusculo(var_motivo)
        ent_motivo = ttk.Entry(f_cont, textvariable=var_motivo, width=45)
        ent_motivo.pack(fill=tk.X, pady=(0, 15))
        ent_motivo.focus_set()

        b_box = ttk.Frame(f_cont)
        b_box.pack(fill=tk.X, pady=(10, 0))

        def confirmar_canc():
            motivo = var_motivo.get().strip()
            if not motivo:
                messagebox.showerror("Erro", "É obrigatório informar a justificativa do cancelamento.", parent=modal)
                ent_motivo.focus_set()
                return

            if not messagebox.askyesno(
                "Confirmar Cancelamento",
                f"Confirma o cancelamento da requisição {req.req_num}?\n\nEsta operação cancelará a solicitação.",
                parent=modal,
            ):
                return

            empcod = self.var_empcod.get().strip() or "1.01"
            res = self.service.cancelar_requisicao(req_num=req.req_num, empcod=empcod, motivo=motivo)
            if res.sucesso:
                messagebox.showinfo("Sucesso", res.mensagem, parent=self)
                modal.destroy()
                self.carregar_requisicoes()
            else:
                messagebox.showerror("Erro ao Cancelar", res.mensagem, parent=modal)

        btn_conf = tk.Button(
            b_box,
            text="✖ Confirmar Cancelamento (Enter)",
            bg="#DC2626",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            relief=tk.FLAT,
            command=confirmar_canc,
        )
        btn_conf.pack(side=tk.RIGHT, padx=(6, 0))

        btn_canc = ttk.Button(b_box, text="Voltar (Esc)", command=modal.destroy)
        btn_canc.pack(side=tk.RIGHT)

        configurar_navegacao_enter([ent_motivo, btn_conf])
        modal.bind("<Return>", lambda e: confirmar_canc())
        modal.bind("<Escape>", lambda e: modal.destroy())


def abrir_atendimento_requisicoes(parent=None, connection=None):
    win = tk.Toplevel(parent)
    win.title("Atendimento de Requisições de Materiais - GeoAlvo")
    win.minsize(980, 560)
    centralizar_janela(win, parent, 1100, 640)
    view = RequisicoesView(win, modo_inicial="ATENDIMENTO")
    view.pack(fill=tk.BOTH, expand=True)
    return win


def abrir_cancelamento_requisicoes(parent=None, connection=None):
    win = tk.Toplevel(parent)
    win.title("Cancelamento de Requisições de Materiais - GeoAlvo")
    win.minsize(980, 560)
    centralizar_janela(win, parent, 1100, 640)
    view = RequisicoesView(win, modo_inicial="CANCELAMENTO")
    view.pack(fill=tk.BOTH, expand=True)
    return win


def abrir_devolucao_requisicoes(parent=None, connection=None):
    win = tk.Toplevel(parent)
    win.title("Devolução de Requisições de Materiais - GeoAlvo")
    win.minsize(980, 560)
    centralizar_janela(win, parent, 1100, 640)
    view = RequisicoesView(win, modo_inicial="DEVOLUCAO")
    view.pack(fill=tk.BOTH, expand=True)
    return win
