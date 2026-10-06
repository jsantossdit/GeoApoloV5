"""
Interface Gráfica para Gestão e Histórico de Movimentações de Estoque.
GeoApolo V5
Clean Architecture: Grade alimentada por atendimento de requisições, entradas de compras e saídas diretas.
Padrões de mercado: Pesquisa rápida F3, visualização de saldos, totais e atalhos operacionais.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from datetime import datetime, timedelta

from core import (
    centralizar_janela,
    vincular_maiusculo,
    configurar_navegacao_enter,
    vincular_mascara_data,
    formatar_data_br,
    habilitar_filtro_dinamico_combobox,
    converter_data_br_para_iso,
    validar_data_br,
    obter_empresa_ativa,
)
from .models import MovimentoEstoqueDTO
from .service import EstoqueService


def formatar_moeda_br(valor: float) -> str:
    """Retorna valor monetário formatado no padrão brasileiro (ex: R$ 1.250,50)."""
    try:
        val = float(valor)
        negativo = val < 0
        val_abs = abs(val)
        fmt = f"{val_abs:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"-R$ {fmt}" if negativo else f"R$ {fmt}"
    except Exception:
        return "R$ 0,00"


def formatar_numero_br(valor: float, decimais: int = 2) -> str:
    """Retorna número formatado no padrão brasileiro (ex: 1.500,00)."""
    try:
        val = float(valor)
        negativo = val < 0
        val_abs = abs(val)
        fmt_spec = f"{{:,.{decimais}f}}"
        fmt = fmt_spec.format(val_abs).replace(",", "X").replace(".", ",").replace("X", ".")
        return f"-{fmt}" if negativo else fmt
    except Exception:
        return "0,00"


class MovimentacaoView(ttk.Frame):
    """Tela de Histórico e Registro de Movimentações de Estoque."""

    def __init__(self, parent=None, service: Optional[EstoqueService] = None):
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

        self._setup_ui()
        self._configurar_atalhos()
        self.carregar_movimentacoes()

    def _setup_ui(self):
        # Header superior
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        lbl_titulo = ttk.Label(
            header,
            text="Movimentação de Estoque",
            font=("Segoe UI", 13, "bold"),
            foreground="#1E3A8A",
        )
        lbl_titulo.pack(side=tk.LEFT)

        self.lbl_contador = ttk.Label(
            header,
            text="0 movimentação(ões)",
            font=("Segoe UI", 9, "bold"),
            foreground="#475569",
        )
        self.lbl_contador.pack(side=tk.RIGHT, padx=5)

        # Barra de Ações Rápidas (Toolbar)
        bar_toolbar = ttk.Frame(self, padding=(12, 4))
        bar_toolbar.pack(fill=tk.X)

        btn_entrada = tk.Button(
            bar_toolbar,
            text="➕ Nova Entrada de Compras (F8)",
            bg="#16A34A",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=5,
            relief=tk.FLAT,
            command=self._abrir_modal_entrada,
        )
        btn_entrada.pack(side=tk.LEFT, padx=(0, 8))

        btn_saida = tk.Button(
            bar_toolbar,
            text="➖ Nova Saída Direta (F3)",
            bg="#D97706",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=5,
            relief=tk.FLAT,
            command=self._abrir_modal_saida_direta,
        )
        btn_saida.pack(side=tk.LEFT, padx=(0, 8))

        btn_atender = tk.Button(
            bar_toolbar,
            text="📋 Atender Requisições",
            bg="#2563EB",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=5,
            relief=tk.FLAT,
            command=self._abrir_atendimento_requisicoes,
        )
        btn_atender.pack(side=tk.LEFT, padx=(0, 8))

        btn_kardex = ttk.Button(
            bar_toolbar,
            text="📊 Ver Kardex do Item (F6)",
            command=self._ver_kardex_selecionado,
        )
        btn_kardex.pack(side=tk.LEFT, padx=(0, 8))

        btn_atualizar = ttk.Button(
            bar_toolbar,
            text="🔄 Atualizar (F5)",
            command=self.carregar_movimentacoes,
        )
        btn_atualizar.pack(side=tk.LEFT, padx=(0, 8))

        # Cards de Resumo no topo
        f_cards = ttk.Frame(self, padding=(12, 4))
        f_cards.pack(fill=tk.X)

        self.card_tot_reg = tk.Label(
            f_cards,
            text="Registros: 0",
            bg="#EFF6FF",
            fg="#1D4ED8",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            relief=tk.RIDGE,
        )
        self.card_tot_reg.pack(side=tk.LEFT, padx=(0, 8))

        self.card_tot_ent = tk.Label(
            f_cards,
            text="Entradas: 0.00 un (R$ 0,00)",
            bg="#F0FDF4",
            fg="#15803D",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            relief=tk.RIDGE,
        )
        self.card_tot_ent.pack(side=tk.LEFT, padx=(0, 8))

        self.card_tot_sai = tk.Label(
            f_cards,
            text="Saídas: 0.00 un (R$ 0,00)",
            bg="#FEF2F2",
            fg="#B91C1C",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            relief=tk.RIDGE,
        )
        self.card_tot_sai.pack(side=tk.LEFT, padx=(0, 8))

        self.card_tot_saldo = tk.Label(
            f_cards,
            text="Saldo Período: 0.00 un (R$ 0,00)",
            bg="#F8FAFC",
            fg="#0F172A",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            relief=tk.RIDGE,
        )
        self.card_tot_saldo.pack(side=tk.LEFT, padx=(0, 8))

        # Barra de Filtros
        filtro_box = ttk.LabelFrame(self, text=" Filtros de Movimentações ", padding=(10, 8))
        filtro_box.pack(fill=tk.X, padx=12, pady=(4, 6))

        f_row = ttk.Frame(filtro_box)
        f_row.pack(fill=tk.X)

        ttk.Label(f_row, text="Tipo:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_tipo = tk.StringVar(value="TODOS")
        self.cb_tipo = ttk.Combobox(
            f_row,
            textvariable=self.var_tipo,
            values=["TODOS", "ENTRADA", "SAIDA"],
            state="readonly",
            width=12,
        )
        self.cb_tipo.pack(side=tk.LEFT, padx=(0, 12))
        self.cb_tipo.bind("<<ComboboxSelected>>", lambda e: self.carregar_movimentacoes())

        ttk.Label(f_row, text="Produto:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_busca = tk.StringVar()
        vincular_maiusculo(self.var_busca)
        self.ent_busca = ttk.Entry(f_row, textvariable=self.var_busca, width=20)
        self.ent_busca.pack(side=tk.LEFT, padx=(0, 4))
        self.ent_busca.bind("<Return>", lambda e: self.carregar_movimentacoes())

        btn_busca_p = ttk.Button(
            f_row,
            text="🔍 (F4)",
            width=6,
            command=self._abrir_busca_filtro_produto,
        )
        btn_busca_p.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(f_row, text="De:").pack(side=tk.LEFT, padx=(0, 4))
        dt_ini_padrao = (datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y")
        self.var_data_ini = tk.StringVar(value=dt_ini_padrao)
        self.ent_data_ini = ttk.Entry(f_row, textvariable=self.var_data_ini, width=12)
        self.ent_data_ini.pack(side=tk.LEFT, padx=(0, 8))
        vincular_mascara_data(self.ent_data_ini)

        ttk.Label(f_row, text="Até:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_data_fim = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        self.ent_data_fim = ttk.Entry(f_row, textvariable=self.var_data_fim, width=12)
        self.ent_data_fim.pack(side=tk.LEFT, padx=(0, 12))
        vincular_mascara_data(self.ent_data_fim)

        ttk.Label(f_row, text="Empresa:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_empcod = tk.StringVar(value=obter_empresa_ativa())
        self.ent_empcod = ttk.Entry(f_row, textvariable=self.var_empcod, width=7)
        self.ent_empcod.pack(side=tk.LEFT, padx=(0, 12))

        btn_filtrar = ttk.Button(f_row, text="🔍 Filtrar (F5)", command=self.carregar_movimentacoes)
        btn_filtrar.pack(side=tk.LEFT, padx=(0, 6))

        btn_limpar = ttk.Button(f_row, text="Limpar", command=self._limpar_filtros)
        btn_limpar.pack(side=tk.LEFT)

        # Grade de Movimentações
        frame_grid = ttk.LabelFrame(self, text=" Histórico de Entradas e Saídas (Duplo clique para detalhes) ", padding=6)
        frame_grid.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        cols = ("chv", "data", "tipo", "origem", "prodcod", "prodnome", "unid", "lote", "qtd", "val_unit", "val_tot", "doc", "ccusto", "obs")
        self.tree = ttk.Treeview(frame_grid, columns=cols, show="headings", height=14, selectmode="browse")

        self.tree.heading("chv", text="Nº Lcto")
        self.tree.heading("data", text="Data/Hora")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("origem", text="Origem")
        self.tree.heading("prodcod", text="Código")
        self.tree.heading("prodnome", text="Descrição do Produto")
        self.tree.heading("unid", text="Unid")
        self.tree.heading("lote", text="Lote")
        self.tree.heading("qtd", text="Quantidade")
        self.tree.heading("val_unit", text="Vlr Unit (R$)")
        self.tree.heading("val_tot", text="Vlr Total (R$)")
        self.tree.heading("doc", text="Doc / NF")
        self.tree.heading("ccusto", text="Centro de Custo")
        self.tree.heading("obs", text="Observação / Destino")

        self.tree.column("chv", width=75, anchor=tk.CENTER)
        self.tree.column("data", width=135, anchor=tk.CENTER)
        self.tree.column("tipo", width=55, anchor=tk.CENTER)
        self.tree.column("origem", width=120, anchor=tk.CENTER)
        self.tree.column("prodcod", width=110, anchor=tk.W)
        self.tree.column("prodnome", width=240, anchor=tk.W)
        self.tree.column("unid", width=55, anchor=tk.CENTER)
        self.tree.column("lote", width=95, anchor=tk.W)
        self.tree.column("qtd", width=95, anchor=tk.E)
        self.tree.column("val_unit", width=95, anchor=tk.E)
        self.tree.column("val_tot", width=105, anchor=tk.E)
        self.tree.column("doc", width=110, anchor=tk.W)
        self.tree.column("ccusto", width=140, anchor=tk.W)
        self.tree.column("obs", width=220, anchor=tk.W)

        sb_y = ttk.Scrollbar(frame_grid, orient=tk.VERTICAL, command=self.tree.yview)
        sb_x = ttk.Scrollbar(frame_grid, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        sb_y.grid(row=0, column=1, sticky="ns")
        sb_x.grid(row=1, column=0, sticky="ew")

        frame_grid.rowconfigure(0, weight=1)
        frame_grid.columnconfigure(0, weight=1)

        self.tree.tag_configure("E", foreground="#15803D", background="#F0FDF4")
        self.tree.tag_configure("S", foreground="#B91C1C", background="#FEF2F2")

        self.tree.bind("<Double-1>", lambda e: self._abrir_detalhes_movimento())

        # Barra inferior
        bar_bottom = ttk.Frame(self, padding=(12, 8))
        bar_bottom.pack(fill=tk.X)

        lbl_dicas = ttk.Label(
            bar_bottom,
            text="Atalhos: [F8] Nova Entrada | [F3] Nova Saída | [F6] Kardex | [F5] Atualizar | [F4] Buscar | [Duplo Clique] Detalhes | [Esc] Fechar",
            font=("Segoe UI", 8),
            foreground="#475569",
        )
        lbl_dicas.pack(side=tk.LEFT)

        btn_fechar = ttk.Button(bar_bottom, text="Fechar (Esc)", command=self._fechar_janela)
        btn_fechar.pack(side=tk.RIGHT)

        configurar_navegacao_enter([self.cb_tipo, self.ent_busca, self.ent_data_ini, self.ent_data_fim, self.ent_empcod, btn_filtrar])

    def _configurar_atalhos(self):
        root = self.winfo_toplevel()
        root.bind("<F8>", lambda e: self._abrir_modal_entrada())
        root.bind("<F3>", lambda e: self._abrir_modal_saida_direta())
        root.bind("<F6>", lambda e: self._ver_kardex_selecionado())
        root.bind("<F5>", lambda e: self.carregar_movimentacoes())
        root.bind("<F4>", lambda e: self._abrir_busca_filtro_produto())
        root.bind("<Escape>", lambda e: self._fechar_janela())

    def _abrir_busca_filtro_produto(self):
        def _definir_busca(cod, nome, unid, saldo):
            self.var_busca.set(cod)
            self.carregar_movimentacoes()
        self._abrir_modal_busca_produtos(_definir_busca, self.var_busca.get().strip())

    def _fechar_janela(self):
        toplevel = self.winfo_toplevel()
        if toplevel != self:
            toplevel.destroy()

    def _abrir_atendimento_requisicoes(self):
        try:
            from .requisicoes_view import abrir_atendimento_requisicoes
            conn = getattr(self.service._repo, "_conn", None) if self.service and hasattr(self.service, "_repo") else None
            top = self.winfo_toplevel()
            win = abrir_atendimento_requisicoes(top, connection=conn)
            if win:
                win.bind("<Destroy>", lambda e: self.after(200, self.carregar_movimentacoes) if e.widget == win else None)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir Atendimento de Requisições:\n{e}", parent=self)

    def _limpar_filtros(self):
        self.var_tipo.set("TODOS")
        self.var_busca.set("")
        self.var_data_ini.set((datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y"))
        self.var_data_fim.set(datetime.now().strftime("%d/%m/%Y"))
        self.carregar_movimentacoes()

    def carregar_movimentacoes(self):
        if not self.service:
            return

        for it in self.tree.get_children():
            self.tree.delete(it)

        empcod = self.var_empcod.get().strip() or "1.01"
        tipo_f = self.var_tipo.get().strip()
        busca = self.var_busca.get().strip()
        dt_ini = self.var_data_ini.get().strip()
        dt_fim = self.var_data_fim.get().strip()

        movs = self.service.listar_movimentacoes(
            empcod=empcod,
            tipo_filtro=tipo_f,
            termo_prod=busca,
            data_ini=dt_ini,
            data_fim=dt_fim,
            limite=300,
        )

        tot_ent_qtd = 0.0
        tot_ent_val = 0.0
        tot_sai_qtd = 0.0
        tot_sai_val = 0.0

        for m in movs:
            tag = "E" if m.tipo_movimento == "E" else "S"
            if m.tipo_movimento == "E":
                tot_ent_qtd += m.quantidade
                tot_ent_val += m.valor_total
            else:
                tot_sai_qtd += m.quantidade
                tot_sai_val += m.valor_total

            dt_br = formatar_data_br(m.data_movimento, incluir_hora=True)
            self.tree.insert(
                "",
                tk.END,
                iid=str(m.mov_chv),
                values=(
                    m.mov_chv,
                    dt_br,
                    m.tipo_movimento,
                    m.origem_movimento,
                    m.prodcod_estr,
                    m.prodnome,
                    m.unidade,
                    m.numero_lote or "-",
                    formatar_numero_br(m.quantidade),
                    formatar_moeda_br(m.valor_unitario),
                    formatar_moeda_br(m.valor_total),
                    m.doc_origem,
                    m.centro_custo,
                    m.observacao,
                ),
                tags=(tag,),
            )

        saldo_qtd = tot_ent_qtd - tot_sai_qtd
        saldo_val = tot_ent_val - tot_sai_val

        self.lbl_contador.config(text=f"{len(movs)} movimentação(ões) listada(s)")
        self.card_tot_reg.config(text=f"Registros: {len(movs)}")
        self.card_tot_ent.config(text=f"Entradas: {formatar_numero_br(tot_ent_qtd)} un ({formatar_moeda_br(tot_ent_val)})")
        self.card_tot_sai.config(text=f"Saídas: {formatar_numero_br(tot_sai_qtd)} un ({formatar_moeda_br(tot_sai_val)})")

        cor_saldo_bg = "#F0FDF4" if saldo_qtd >= 0 else "#FEF2F2"
        cor_saldo_fg = "#15803D" if saldo_qtd >= 0 else "#B91C1C"
        sinal = "+" if saldo_qtd > 0 else ""
        self.card_tot_saldo.config(
            text=f"Saldo Período: {sinal}{formatar_numero_br(saldo_qtd)} un ({formatar_moeda_br(saldo_val)})",
            bg=cor_saldo_bg,
            fg=cor_saldo_fg,
        )

    def _ver_kardex_selecionado(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione uma movimentação para visualizar a ficha do produto.", parent=self)
            return

        vals = self.tree.item(sel[0], "values")
        prodcod = vals[4]
        from .consultas_view import abrir_consulta_ficha_estoque
        abrir_consulta_ficha_estoque(parent=self.winfo_toplevel(), prodcod_inicial=prodcod)

    def _abrir_detalhes_movimento(self):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        modal = tk.Toplevel(self)
        modal.title(f"Detalhes do Lançamento de Estoque Nº {vals[0]}")
        modal.transient(self)
        modal.grab_set()
        centralizar_janela(modal, self, 520, 420)

        f_cont = ttk.Frame(modal, padding=16)
        f_cont.pack(fill=tk.BOTH, expand=True)

        lbl_top = ttk.Label(f_cont, text=f"Movimentação de Estoque Nº {vals[0]}", font=("Segoe UI", 12, "bold"), foreground="#1E3A8A")
        lbl_top.pack(anchor=tk.W, pady=(0, 10))

        grid = ttk.LabelFrame(f_cont, text=" Ficha do Lançamento ", padding=10)
        grid.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        tipo_desc = "ENTRADA" if vals[2] == "E" else "SAÍDA"
        campos = [
            ("Data / Hora:", vals[1]),
            ("Tipo de Operação:", f"{vals[2]} - {tipo_desc}"),
            ("Origem:", vals[3]),
            ("Código Produto:", vals[4]),
            ("Descrição:", vals[5]),
            ("Unidade:", vals[6]),
            ("Lote:", vals[7] or "-"),
            ("Quantidade:", vals[8]),
            ("Valor Unitário:", vals[9] if "R$" in str(vals[9]) else f"R$ {vals[9]}"),
            ("Valor Total:", vals[10] if "R$" in str(vals[10]) else f"R$ {vals[10]}"),
            ("Documento / NF:", vals[11] or "-"),
            ("Centro de Custo:", vals[12] or "-"),
            ("Observação / Destino:", vals[13] or "-"),
        ]
        for r_idx, (rotulo, valor) in enumerate(campos):
            ttk.Label(grid, text=rotulo, font=("Segoe UI", 9, "bold")).grid(row=r_idx, column=0, sticky=tk.W, pady=2)
            ttk.Label(grid, text=valor).grid(row=r_idx, column=1, sticky=tk.W, padx=8, pady=2)

        btn_ok = ttk.Button(f_cont, text="Fechar (Esc)", command=modal.destroy)
        btn_ok.pack(side=tk.RIGHT)
        modal.bind("<Escape>", lambda e: modal.destroy())

    def _abrir_modal_busca_produtos(self, callback, termo_inicial: str = ""):
        modal = tk.Toplevel(self)
        modal.title("Pesquisa de Produtos")
        modal.transient(self)
        modal.grab_set()
        modal.minsize(820, 480)
        centralizar_janela(modal, self, 880, 520)

        f_cont = ttk.Frame(modal, padding=12)
        f_cont.pack(fill=tk.BOTH, expand=True)

        ttk.Label(f_cont, text="Localizar Produto no Catálogo", font=("Segoe UI", 11, "bold"), foreground="#1E3A8A").pack(anchor=tk.W, pady=(0, 6))

        f_b = ttk.Frame(f_cont)
        f_b.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(f_b, text="Buscar:").pack(side=tk.LEFT, padx=(0, 4))
        var_b = tk.StringVar(value=termo_inicial)
        vincular_maiusculo(var_b)
        ent_b = ttk.Entry(f_b, textvariable=var_b, width=32)
        ent_b.pack(side=tk.LEFT, padx=(0, 8))

        btn_pesq = ttk.Button(f_b, text="🔍 Buscar (F4)", command=lambda: recarregar())
        btn_pesq.pack(side=tk.LEFT)

        f_tree_box = ttk.Frame(f_cont)
        f_tree_box.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        cols_b = ("cod", "nome", "unid", "saldo")
        tree_b = ttk.Treeview(f_tree_box, columns=cols_b, show="headings", height=11, selectmode="browse")
        tree_b.heading("cod", text="Código")
        tree_b.heading("nome", text="Descrição do Produto")
        tree_b.heading("unid", text="Unid")
        tree_b.heading("saldo", text="Saldo Atual")
        tree_b.column("cod", width=110, anchor=tk.W)
        tree_b.column("nome", width=460, anchor=tk.W)
        tree_b.column("unid", width=70, anchor=tk.CENTER)
        tree_b.column("saldo", width=120, anchor=tk.E)

        sb_b = ttk.Scrollbar(f_tree_box, orient=tk.VERTICAL, command=tree_b.yview)
        tree_b.configure(yscrollcommand=sb_b.set)
        tree_b.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_b.pack(side=tk.RIGHT, fill=tk.Y)

        def recarregar():
            for it in tree_b.get_children():
                tree_b.delete(it)
            emp = self.var_empcod.get().strip() or "1.01"
            termo = var_b.get().strip()
            saldos = self.service.consultar_saldos_produtos(empcod=emp, termo_busca=termo)
            for p in saldos:
                tree_b.insert("", tk.END, iid=p.prodcod_estr, values=(p.prodcod_estr, p.prodnome, p.unidade, f"{p.saldo_atual:.2f}"))

        def selecionar():
            sel = tree_b.selection()
            if not sel:
                return "break"
            vals = tree_b.item(sel[0], "values")
            callback(vals[0], vals[1], vals[2], float(vals[3]))
            try:
                modal.destroy()
            except Exception:
                pass
            return "break"

        ent_b.bind("<Return>", lambda e: (recarregar(), "break")[1])
        tree_b.bind("<Double-1>", lambda e: (selecionar(), "break")[1])
        tree_b.bind("<Return>", lambda e: (selecionar(), "break")[1])
        modal.bind("<F4>", lambda e: (recarregar(), "break")[1])
        modal.bind("<F3>", lambda e: (selecionar(), "break")[1])
        modal.bind("<Escape>", lambda e: (modal.destroy(), "break")[1])

        f_bottom = ttk.Frame(f_cont)
        f_bottom.pack(fill=tk.X, side=tk.BOTTOM, pady=(6, 0))

        btn_sel = tk.Button(
            f_bottom,
            text="✔ Selecionar (Enter)",
            bg="#1D4ED8",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=6,
            relief=tk.FLAT,
            command=selecionar,
        )
        btn_sel.pack(side=tk.RIGHT, padx=4)

        btn_canc = tk.Button(
            f_bottom,
            text="Cancelar (Esc)",
            bg="#E2E8F0",
            fg="#1E293B",
            font=("Segoe UI", 9),
            padx=12,
            pady=6,
            relief=tk.GROOVE,
            command=modal.destroy,
        )
        btn_canc.pack(side=tk.RIGHT, padx=4)

        recarregar()
        ent_b.focus_set()

    def _abrir_modal_busca_fornecedores(self, callback, termo_inicial: str = ""):
        modal = tk.Toplevel(self)
        modal.title("Pesquisa de Fornecedores / Entidades")
        modal.transient(self)
        modal.grab_set()
        modal.minsize(800, 480)
        centralizar_janela(modal, self, 860, 520)

        f_cont = ttk.Frame(modal, padding=12)
        f_cont.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            f_cont,
            text="Localizar Fornecedor / Entidade no Catálogo (F4)",
            font=("Segoe UI", 11, "bold"),
            foreground="#1E3A8A",
        ).pack(anchor=tk.W, pady=(0, 6))

        f_b = ttk.Frame(f_cont)
        f_b.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(f_b, text="Buscar:").pack(side=tk.LEFT, padx=(0, 4))
        var_b = tk.StringVar(value=termo_inicial)
        vincular_maiusculo(var_b)
        ent_b = ttk.Entry(f_b, textvariable=var_b, width=32)
        ent_b.pack(side=tk.LEFT, padx=(0, 8))

        btn_pesq = ttk.Button(f_b, text="🔍 Filtrar (F4)", command=lambda: recarregar())
        btn_pesq.pack(side=tk.LEFT)

        f_tree_box = ttk.Frame(f_cont)
        f_tree_box.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        cols_f = ("cod", "nome", "doc")
        tree_f = ttk.Treeview(f_tree_box, columns=cols_f, show="headings", height=11, selectmode="browse")
        tree_f.heading("cod", text="Código")
        tree_f.heading("nome", text="Razão Social / Nome do Fornecedor")
        tree_f.heading("doc", text="CNPJ / CPF")
        tree_f.column("cod", width=110, anchor=tk.W)
        tree_f.column("nome", width=460, anchor=tk.W)
        tree_f.column("doc", width=160, anchor=tk.CENTER)

        sb_f = ttk.Scrollbar(f_tree_box, orient=tk.VERTICAL, command=tree_f.yview)
        tree_f.configure(yscrollcommand=sb_f.set)
        tree_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_f.pack(side=tk.RIGHT, fill=tk.Y)

        def recarregar():
            for it in tree_f.get_children():
                tree_f.delete(it)
            termo = var_b.get().strip()
            forns = self.service.listar_fornecedores(termo=termo) if self.service else []
            for f in forns:
                tree_f.insert("", tk.END, iid=f[0], values=(f[0], f[1], f[2]))

        def selecionar():
            sel = tree_f.selection()
            if not sel:
                return "break"
            vals = tree_f.item(sel[0], "values")
            callback(vals[0], vals[1])
            try:
                modal.destroy()
            except Exception:
                pass
            return "break"

        ent_b.bind("<Return>", lambda e: (recarregar(), "break")[1])
        tree_f.bind("<Double-1>", lambda e: (selecionar(), "break")[1])
        tree_f.bind("<Return>", lambda e: (selecionar(), "break")[1])
        modal.bind("<F4>", lambda e: (recarregar(), "break")[1])
        modal.bind("<F3>", lambda e: (selecionar(), "break")[1])
        modal.bind("<Escape>", lambda e: (modal.destroy(), "break")[1])

        f_bottom = ttk.Frame(f_cont)
        f_bottom.pack(fill=tk.X, side=tk.BOTTOM, pady=(6, 0))

        btn_sel = tk.Button(
            f_bottom,
            text="✔ Selecionar (Enter)",
            bg="#1D4ED8",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=16,
            pady=6,
            relief=tk.FLAT,
            command=selecionar,
        )
        btn_sel.pack(side=tk.RIGHT, padx=4)

        btn_canc = tk.Button(
            f_bottom,
            text="Cancelar (Esc)",
            bg="#E2E8F0",
            fg="#1E293B",
            font=("Segoe UI", 9),
            padx=12,
            pady=6,
            relief=tk.GROOVE,
            command=modal.destroy,
        )
        btn_canc.pack(side=tk.RIGHT, padx=4)

        recarregar()
        ent_b.focus_set()

    def _abrir_modal_busca_almoxarifados(self, callback, termo_inicial: str = ""):
        modal = tk.Toplevel(self)
        modal.title("Pesquisa de Almoxarifados")
        modal.transient(self)
        modal.grab_set()
        modal.minsize(680, 420)
        centralizar_janela(modal, self, 720, 440)

        f_cont = ttk.Frame(modal, padding=12)
        f_cont.pack(fill=tk.BOTH, expand=True)

        lbl_top = ttk.Label(
            f_cont,
            text="Selecionar Almoxarifado de Estoque",
            font=("Segoe UI", 11, "bold"),
            foreground="#1E3A8A",
        )
        lbl_top.pack(anchor=tk.W, pady=(0, 8))

        f_busca = ttk.Frame(f_cont)
        f_busca.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(f_busca, text="Buscar:").pack(side=tk.LEFT, padx=(0, 4))
        var_b = tk.StringVar(value=termo_inicial)
        vincular_maiusculo(var_b)
        ent_b = ttk.Entry(f_busca, textvariable=var_b, width=30)
        ent_b.pack(side=tk.LEFT, padx=(0, 8))

        cols_b = ("cod", "nome", "cc", "status")
        tree_b = ttk.Treeview(f_cont, columns=cols_b, show="headings", height=10, selectmode="browse")
        tree_b.heading("cod", text="Código")
        tree_b.heading("nome", text="Descrição do Almoxarifado")
        tree_b.heading("cc", text="Centro de Custo")
        tree_b.heading("status", text="Status")

        tree_b.column("cod", width=80, anchor=tk.CENTER)
        tree_b.column("nome", width=300, anchor=tk.W)
        tree_b.column("cc", width=140, anchor=tk.W)
        tree_b.column("status", width=70, anchor=tk.CENTER)

        sb_b = ttk.Scrollbar(f_cont, orient=tk.VERTICAL, command=tree_b.yview)
        tree_b.configure(yscrollcommand=sb_b.set)
        tree_b.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_b.pack(side=tk.RIGHT, fill=tk.Y)

        from estoque.almoxarifados_repository import AlmoxarifadosRepository
        repo_almox = AlmoxarifadosRepository()

        def recarregar():
            termo = var_b.get().strip().upper()
            for it in tree_b.get_children():
                tree_b.delete(it)
            try:
                todos = repo_almox.listar_almoxarifados()
                for a in todos:
                    cod = str(a.get("codigo_almoxarifado", ""))
                    desc = str(a.get("descricao", ""))
                    cc = str(a.get("centro_custo", "") or "")
                    cc_nome = str(a.get("nome_centro_custo", "") or "")
                    cc_disp = f"{cc} - {cc_nome}" if cc_nome else cc
                    st = "ATIVO" if a.get("status", "A") == "A" else "INATIVO"
                    if not termo or termo in cod.upper() or termo in desc.upper() or termo in cc_disp.upper():
                        tree_b.insert("", tk.END, iid=cod, values=(cod, desc, cc_disp, st))
            except Exception:
                pass

        def selecionar():
            sel = tree_b.selection()
            if not sel:
                return "break"
            vals = tree_b.item(sel[0], "values")
            callback(vals[0], vals[1])
            try:
                modal.destroy()
            except Exception:
                pass
            return "break"

        ent_b.bind("<Return>", lambda e: (recarregar(), "break")[1])
        tree_b.bind("<Double-1>", lambda e: (selecionar(), "break")[1])
        tree_b.bind("<Return>", lambda e: (selecionar(), "break")[1])
        modal.bind("<Escape>", lambda e: (modal.destroy(), "break")[1])

        btn_b = ttk.Button(f_busca, text="Filtrar", command=recarregar)
        btn_b.pack(side=tk.LEFT)

        recarregar()
        ent_b.focus_set()

    # -------------------------------------------------------------------------
    # MODAL DE ENTRADA DE COMPRAS
    # -------------------------------------------------------------------------
    def _abrir_modal_entrada(self):
        modal = tk.Toplevel(self)
        modal.title("Nova Movimentação de Entrada - Chegada de Compras")
        modal.transient(self)
        modal.grab_set()
        modal.minsize(700, 560)
        centralizar_janela(modal, self, 760, 600)

        f_cont = ttk.Frame(modal, padding=16)
        f_cont.pack(fill=tk.BOTH, expand=True)

        lbl_top = ttk.Label(
            f_cont,
            text="Entrada de Estoque por Compra",
            font=("Segoe UI", 12, "bold"),
            foreground="#16A34A",
        )
        lbl_top.pack(anchor=tk.W, pady=(0, 10))

        grid = ttk.Frame(f_cont)
        grid.pack(fill=tk.BOTH, expand=True)

        # Empresa
        ttk.Label(grid, text="Empresa:").grid(row=0, column=0, sticky=tk.W, pady=4)
        var_emp = tk.StringVar(value=self.var_empcod.get().strip() or obter_empresa_ativa())
        ent_emp = ttk.Entry(grid, textvariable=var_emp, width=10)
        ent_emp.grid(row=0, column=1, sticky=tk.W, pady=4)

        # Almoxarifado com Busca
        ttk.Label(grid, text="Almoxarifado: *", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=4)
        f_almox_box = ttk.Frame(grid)
        f_almox_box.grid(row=1, column=1, sticky=tk.W, pady=4)

        var_almox = tk.StringVar(value="01")
        vincular_maiusculo(var_almox)
        ent_almox = ttk.Entry(f_almox_box, textvariable=var_almox, width=8, font=("Segoe UI", 9, "bold"))
        ent_almox.pack(side=tk.LEFT, padx=(0, 6))

        lbl_almox_nome = tk.Label(
            f_almox_box,
            text="ALMOXARIFADO CENTRAL / GERAL",
            font=("Segoe UI", 9, "bold"),
            bg="#DCFCE7",
            fg="#15803D",
            padx=6,
            pady=2,
            relief=tk.RIDGE,
        )

        def _definir_almox(cod, desc):
            var_almox.set(cod)
            lbl_almox_nome.config(text=desc, bg="#DCFCE7", fg="#15803D")

        def _buscar_almox_click():
            self._abrir_modal_busca_almoxarifados(_definir_almox, var_almox.get().strip())

        btn_busca_almox = ttk.Button(f_almox_box, text="🔍 Buscar", command=_buscar_almox_click)
        btn_busca_almox.pack(side=tk.LEFT, padx=(0, 6))
        lbl_almox_nome.pack(side=tk.LEFT, padx=(0, 4))

        def _ao_sair_almox(event=None):
            c_almox = var_almox.get().strip().upper()
            if not c_almox:
                lbl_almox_nome.config(text="⚠️ Almoxarifado obrigatório", bg="#FEE2E2", fg="#B91C1C")
                return
            try:
                from estoque.almoxarifados_repository import AlmoxarifadosRepository
                repo_a = AlmoxarifadosRepository()
                a_obj = repo_a.obter_almoxarifado(c_almox)
                if a_obj:
                    _definir_almox(a_obj["codigo_almoxarifado"], a_obj["descricao"])
                else:
                    lbl_almox_nome.config(text="⚠️ Não cadastrado", bg="#FEE2E2", fg="#B91C1C")
            except Exception:
                pass

        ent_almox.bind("<FocusOut>", _ao_sair_almox)
        ent_almox.bind("<Return>", lambda e: _ao_sair_almox())

        # Produto com Busca F4
        ttk.Label(grid, text="Produto: *", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=4)
        f_prod_box = ttk.Frame(grid)
        f_prod_box.grid(row=2, column=1, sticky=tk.W, pady=4)

        var_prod = tk.StringVar()
        vincular_maiusculo(var_prod)
        ent_prod = ttk.Entry(f_prod_box, textvariable=var_prod, width=14, font=("Segoe UI", 9, "bold"))
        ent_prod.pack(side=tk.LEFT, padx=(0, 6))

        lbl_prod_nome = tk.Label(
            f_prod_box,
            text="",
            font=("Segoe UI", 9, "bold"),
            bg="#F1F5F9",
            fg="#15803D",
            padx=6,
            pady=2,
            relief=tk.RIDGE,
        )

        def _definir_prod(cod, nome, unid, saldo):
            var_prod.set(cod)
            lbl_prod_nome.config(
                text=f"{nome} ({unid}) | Saldo: {saldo:.2f}",
                bg="#DCFCE7",
                fg="#15803D",
            )

        def _buscar_prod_click():
            self._abrir_modal_busca_produtos(_definir_prod, var_prod.get().strip())

        btn_busca_p = ttk.Button(f_prod_box, text="🔍 Buscar (F4)", command=_buscar_prod_click)
        btn_busca_p.pack(side=tk.LEFT, padx=(0, 6))
        lbl_prod_nome.pack(side=tk.LEFT, padx=(0, 4))

        def _ao_sair_prod(event=None):
            cod = var_prod.get().strip()
            if not cod:
                lbl_prod_nome.config(text="", bg="#F1F5F9", fg="#475569")
                return
            saldos = self.service.consultar_saldos_produtos(empcod=var_emp.get().strip() or "1.01", termo_busca=cod)
            encontrado = False
            for p in saldos:
                if str(p.prodcod_estr).strip().upper() == cod.upper():
                    _definir_prod(p.prodcod_estr, p.prodnome, p.unidade, p.saldo_atual)
                    encontrado = True
                    break
            if not encontrado:
                try:
                    cur = self.service.repo._get_cursor()
                    nolock = self.service.repo._nolock()
                    cur.execute(f"SELECT prodcod, prodnome FROM USER_geoapolo_produtos {nolock} WHERE CAST(prodcod AS VARCHAR) = ?", [cod])
                    r = cur.fetchone()
                    if r:
                        _definir_prod(str(r[0]), str(r[1] or ""), "UN", 0.0)
                        encontrado = True
                except Exception:
                    pass
            if not encontrado:
                lbl_prod_nome.config(text="⚠️ Produto não localizado", bg="#FEE2E2", fg="#B91C1C")

        ent_prod.bind("<FocusOut>", _ao_sair_prod)
        ent_prod.bind("<Return>", lambda e: _ao_sair_prod())

        # Centro de Custo
        ttk.Label(grid, text="Centro de Custo: *", font=("Segoe UI", 9, "bold")).grid(row=3, column=0, sticky=tk.W, pady=4)
        var_cctrl = tk.StringVar()
        cb_cctrl = ttk.Combobox(grid, textvariable=var_cctrl, width=38)
        cb_cctrl.grid(row=3, column=1, sticky=tk.W, pady=4)
        centros = self.service.listar_centros_custo(var_emp.get().strip() or obter_empresa_ativa()) if self.service else []
        lista_centros = [f"{c[0]} - {c[1]}" for c in centros]
        habilitar_filtro_dinamico_combobox(cb_cctrl, lista_centros)
        if lista_centros:
            cb_cctrl.current(0)

        # Fornecedor com Busca F4
        ttk.Label(grid, text="Fornecedor:").grid(row=4, column=0, sticky=tk.W, pady=4)
        f_forn_box = ttk.Frame(grid)
        f_forn_box.grid(row=4, column=1, sticky=tk.W, pady=4)

        var_forn_cod = tk.StringVar()
        vincular_maiusculo(var_forn_cod)
        ent_forn_cod = ttk.Entry(f_forn_box, textvariable=var_forn_cod, width=14, font=("Segoe UI", 9, "bold"))
        ent_forn_cod.pack(side=tk.LEFT, padx=(0, 6))

        var_forn_nome = tk.StringVar()
        lbl_forn_nome = tk.Label(
            f_forn_box,
            text="",
            font=("Segoe UI", 9, "bold"),
            bg="#F1F5F9",
            fg="#1E3A8A",
            padx=6,
            pady=2,
            relief=tk.RIDGE,
        )

        def _definir_forn(cod, nome):
            var_forn_cod.set(cod)
            var_forn_nome.set(nome)
            lbl_forn_nome.config(text=f"{nome}", bg="#DBEAFE", fg="#1E40AF")

        def _buscar_forn_click():
            self._abrir_modal_busca_fornecedores(_definir_forn, var_forn_cod.get().strip())

        btn_busca_forn = ttk.Button(f_forn_box, text="🔍 Buscar (F4)", command=_buscar_forn_click)
        btn_busca_forn.pack(side=tk.LEFT, padx=(0, 6))
        lbl_forn_nome.pack(side=tk.LEFT, padx=(0, 4))

        def _ao_sair_forn(event=None):
            cod = var_forn_cod.get().strip()
            if not cod:
                lbl_forn_nome.config(text="", bg="#F1F5F9", fg="#475569")
                return
            forns = self.service.listar_fornecedores(cod) if self.service else []
            for f in forns:
                if f[0].upper() == cod.upper() or cod.upper() in f[1].upper():
                    _definir_forn(f[0], f[1])
                    return

        ent_forn_cod.bind("<FocusOut>", _ao_sair_forn)
        ent_forn_cod.bind("<Return>", lambda e: _ao_sair_forn())

        # Número do Lote com Busca F4
        ttk.Label(grid, text="Número do Lote:").grid(row=5, column=0, sticky=tk.W, pady=4)
        f_lote_box = ttk.Frame(grid)
        f_lote_box.grid(row=5, column=1, sticky=tk.W, pady=4)

        var_lote = tk.StringVar()
        vincular_maiusculo(var_lote)
        ent_lote = ttk.Entry(f_lote_box, textvariable=var_lote, width=20, font=("Segoe UI", 9, "bold"))
        ent_lote.pack(side=tk.LEFT, padx=(0, 6))

        def _consultar_lotes_click():
            p_val = var_prod.get().strip()
            if not p_val:
                messagebox.showwarning("Aviso", "Selecione o produto primeiro.", parent=modal)
                ent_prod.focus_set()
                return
            try:
                p_int = int(p_val)
            except ValueError:
                p_int = None
            from lotes import abrir_janela_lotes
            abrir_janela_lotes(modal, prodcod=p_int, callback=lambda num: var_lote.set(num))

        btn_ver_lotes = ttk.Button(f_lote_box, text="🏷 Lotes (F4)", command=_consultar_lotes_click)
        btn_ver_lotes.pack(side=tk.LEFT)

        # Quantidade
        ttk.Label(grid, text="Quantidade: *", font=("Segoe UI", 9, "bold")).grid(row=6, column=0, sticky=tk.W, pady=4)
        var_qtd = tk.StringVar()
        ent_qtd = ttk.Entry(grid, textvariable=var_qtd, width=15, font=("Segoe UI", 9, "bold"))
        ent_qtd.grid(row=6, column=1, sticky=tk.W, pady=4)

        # Valor Unitário
        ttk.Label(grid, text="Valor Unitário (R$):").grid(row=7, column=0, sticky=tk.W, pady=4)
        var_val = tk.StringVar(value="0,00")
        ent_val = ttk.Entry(grid, textvariable=var_val, width=15)
        ent_val.grid(row=7, column=1, sticky=tk.W, pady=4)

        # Total Calculado
        ttk.Label(grid, text="Valor Total:").grid(row=8, column=0, sticky=tk.W, pady=4)
        lbl_total_calc = ttk.Label(grid, text="R$ 0,00", font=("Segoe UI", 10, "bold"), foreground="#15803D")
        lbl_total_calc.grid(row=8, column=1, sticky=tk.W, pady=4)

        def _recalcular_total(*args):
            try:
                q = float(var_qtd.get().replace(",", "."))
                v = float(var_val.get().replace(",", "."))
                lbl_total_calc.config(text=f"R$ {q * v:,.2f}")
            except Exception:
                lbl_total_calc.config(text="R$ 0,00")

        var_qtd.trace_add("write", _recalcular_total)
        var_val.trace_add("write", _recalcular_total)

        # Número Doc / NF
        ttk.Label(grid, text="Nº Doc / NF:").grid(row=9, column=0, sticky=tk.W, pady=4)
        var_doc = tk.StringVar()
        vincular_maiusculo(var_doc)
        ent_doc = ttk.Entry(grid, textvariable=var_doc, width=22)
        ent_doc.grid(row=9, column=1, sticky=tk.W, pady=4)

        # Data de Vencimento (Contas a Pagar)
        ttk.Label(grid, text="Vencimento (Financeiro):").grid(row=10, column=0, sticky=tk.W, pady=4)
        var_venc = tk.StringVar(value=(datetime.now() + timedelta(days=30)).strftime("%d/%m/%Y"))
        ent_venc = ttk.Entry(grid, textvariable=var_venc, width=15)
        ent_venc.grid(row=10, column=1, sticky=tk.W, pady=4)
        vincular_mascara_data(ent_venc)

        # Observações / Obs
        ttk.Label(grid, text="Observações / Obs:").grid(row=11, column=0, sticky=tk.W, pady=4)
        var_obs = tk.StringVar()
        vincular_maiusculo(var_obs)
        ent_obs = ttk.Entry(grid, textvariable=var_obs, width=38)
        ent_obs.grid(row=11, column=1, sticky=tk.W, pady=4)


        # Botões
        b_box = ttk.Frame(f_cont)
        b_box.pack(fill=tk.X, pady=(15, 0))

        def confirmar_entrada():
            try:
                prod = var_prod.get().strip()
                if not prod:
                    messagebox.showerror("Erro", "Código do produto é obrigatório.", parent=modal)
                    ent_prod.focus_set()
                    return

                try:
                    qtd_val = float(var_qtd.get().replace(",", "."))
                except ValueError:
                    messagebox.showerror("Erro", "Quantidade inválida.", parent=modal)
                    ent_qtd.focus_set()
                    return

                if qtd_val <= 0:
                    messagebox.showerror("Erro", "A quantidade de entrada deve ser maior que zero.", parent=modal)
                    ent_qtd.focus_set()
                    return

                cctrl_val = var_cctrl.get().strip()
                if not cctrl_val:
                    messagebox.showerror("Erro", "O Centro de Custo é obrigatório.", parent=modal)
                    cb_cctrl.focus_set()
                    return
                cctrl_cod = cctrl_val.split(" - ")[0].strip()
                for c in centros:
                    if c[0].upper() == cctrl_val.upper() or cctrl_val.upper() in c[1].upper():
                        cctrl_cod = c[0]
                        break

                try:
                    val_unit = float(var_val.get().replace(",", "."))
                except ValueError:
                    val_unit = 0.0

                d_venc_raw = var_venc.get().strip()
                if d_venc_raw and "/" in d_venc_raw and not validar_data_br(d_venc_raw[:10]):
                    messagebox.showerror("Erro", "Data de vencimento inválida. Utilize o formato DD/MM/AAAA.", parent=modal)
                    ent_venc.focus_set()
                    return
                d_venc_iso = converter_data_br_para_iso(d_venc_raw[:10]) if d_venc_raw else ""

                # Verificação de Lote
                lote_val = var_lote.get().strip().upper()

                cod_almox = var_almox.get().strip().upper()
                if not cod_almox:
                    messagebox.showerror("Erro", "O Almoxarifado é obrigatório.", parent=modal)
                    ent_almox.focus_set()
                    return

                res = self.service.registrar_entrada_compras(
                    empcod=var_emp.get().strip() or "1.01",
                    prodcod_estr=prod,
                    quantidade=qtd_val,
                    valor_unitario=val_unit,
                    num_doc=var_doc.get().strip(),
                    fornecedor_obs=var_obs.get().strip(),
                    centro_custo=cctrl_cod,
                    fornecedor_cod=var_forn_cod.get().strip(),
                    fornecedor_nome=var_forn_nome.get().strip(),
                    data_vencimento=d_venc_iso,
                    numero_lote=lote_val,
                )
                if res.sucesso:
                    try:
                        from estoque.almoxarifados_repository import AlmoxarifadosRepository
                        conn_a = self.service._repo.conn if self.service and hasattr(self.service, "_repo") and self.service._repo else None
                        repo_almox = AlmoxarifadosRepository(conn_a)
                        repo_almox.atualizar_saldo(cod_almox, int(prod), qtd_val)
                    except Exception:
                        pass
                    messagebox.showinfo("Sucesso", res.mensagem, parent=modal)
                    modal.destroy()
                    self.carregar_movimentacoes()
                else:
                    messagebox.showerror("Erro ao Registrar Entrada", res.mensagem, parent=modal)
            except Exception as e:
                messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao registrar a entrada:\n{e}", parent=modal)

        lbl_dica_modal = ttk.Label(b_box, text="Atalhos: [F4] Buscar | [F10/Enter] Confirmar | [Esc] Cancelar", font=("Segoe UI", 8), foreground="#64748B")
        lbl_dica_modal.pack(side=tk.LEFT)

        btn_conf = tk.Button(
            b_box,
            text="✔ Confirmar Entrada (F10 / Enter)",
            bg="#16A34A",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            relief=tk.FLAT,
            command=confirmar_entrada,
        )
        btn_conf.pack(side=tk.RIGHT, padx=(6, 0))

        btn_canc = ttk.Button(b_box, text="Cancelar (Esc)", command=modal.destroy)
        btn_canc.pack(side=tk.RIGHT)

        def _on_modal_f4(event=None):
            fw = modal.focus_get()
            if fw in (ent_almox, btn_busca_almox):
                _buscar_almox_click()
            elif fw in (ent_forn_cod, btn_busca_forn):
                _buscar_forn_click()
            elif fw in (ent_lote, btn_ver_lotes):
                _consultar_lotes_click()
            else:
                _buscar_prod_click()

        modal.bind("<F4>", _on_modal_f4)
        modal.bind("<F10>", lambda e: confirmar_entrada())
        modal.bind("<Return>", lambda e: confirmar_entrada())
        modal.bind("<Escape>", lambda e: modal.destroy())

        configurar_navegacao_enter([ent_emp, ent_almox, ent_prod, cb_cctrl, ent_forn_cod, ent_lote, ent_qtd, ent_val, ent_doc, ent_venc, ent_obs, btn_conf])
        ent_almox.focus_set()

    # -------------------------------------------------------------------------
    # MODAL DE SAÍDA DIRETA
    # -------------------------------------------------------------------------
    def _abrir_modal_saida_direta(self):
        modal = tk.Toplevel(self)
        modal.title("Nova Movimentação de Saída Direta - Sem Requisição")
        modal.transient(self)
        modal.grab_set()
        modal.minsize(720, 500)
        centralizar_janela(modal, self, 780, 520)

        f_cont = ttk.Frame(modal, padding=16)
        f_cont.pack(fill=tk.BOTH, expand=True)

        lbl_top = ttk.Label(
            f_cont,
            text="Saída Direta de Estoque (Consumo Direto)",
            font=("Segoe UI", 12, "bold"),
            foreground="#D97706",
        )
        lbl_top.pack(anchor=tk.W, pady=(0, 12))

        grid = ttk.Frame(f_cont)
        grid.pack(fill=tk.BOTH, expand=True)

        # Empresa
        ttk.Label(grid, text="Empresa:").grid(row=0, column=0, sticky=tk.W, pady=4)
        var_emp = tk.StringVar(value=self.var_empcod.get().strip() or obter_empresa_ativa())
        ent_emp = ttk.Entry(grid, textvariable=var_emp, width=10)
        ent_emp.grid(row=0, column=1, sticky=tk.W, pady=4)

        # Almoxarifado com Busca
        ttk.Label(grid, text="Almoxarifado: *", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=4)
        f_almox_box_s = ttk.Frame(grid)
        f_almox_box_s.grid(row=1, column=1, sticky=tk.W, pady=4)

        var_almox_s = tk.StringVar(value="01")
        vincular_maiusculo(var_almox_s)
        ent_almox_s = ttk.Entry(f_almox_box_s, textvariable=var_almox_s, width=8, font=("Segoe UI", 9, "bold"))
        ent_almox_s.pack(side=tk.LEFT, padx=(0, 6))

        lbl_almox_nome_s = tk.Label(
            f_almox_box_s,
            text="ALMOXARIFADO CENTRAL / GERAL",
            font=("Segoe UI", 9, "bold"),
            bg="#DCFCE7",
            fg="#15803D",
            padx=6,
            pady=2,
            relief=tk.RIDGE,
        )

        def _definir_almox_s(cod, desc):
            var_almox_s.set(cod)
            lbl_almox_nome_s.config(text=desc, bg="#DCFCE7", fg="#15803D")

        def _buscar_almox_s_click():
            self._abrir_modal_busca_almoxarifados(_definir_almox_s, var_almox_s.get().strip())

        btn_busca_almox_s = ttk.Button(f_almox_box_s, text="🔍 Buscar", command=_buscar_almox_s_click)
        btn_busca_almox_s.pack(side=tk.LEFT, padx=(0, 6))
        lbl_almox_nome_s.pack(side=tk.LEFT, padx=(0, 4))

        def _ao_sair_almox_s(event=None):
            c_almox = var_almox_s.get().strip().upper()
            if not c_almox:
                lbl_almox_nome_s.config(text="⚠️ Almoxarifado obrigatório", bg="#FEE2E2", fg="#B91C1C")
                return
            try:
                from estoque.almoxarifados_repository import AlmoxarifadosRepository
                repo_a = AlmoxarifadosRepository()
                a_obj = repo_a.obter_almoxarifado(c_almox)
                if a_obj:
                    _definir_almox_s(a_obj["codigo_almoxarifado"], a_obj["descricao"])
                else:
                    lbl_almox_nome_s.config(text="⚠️ Não cadastrado", bg="#FEE2E2", fg="#B91C1C")
            except Exception:
                pass

        ent_almox_s.bind("<FocusOut>", _ao_sair_almox_s)
        ent_almox_s.bind("<Return>", lambda e: _ao_sair_almox_s())

        # Produto com Busca F4
        ttk.Label(grid, text="Produto: *", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=4)
        f_prod_box = ttk.Frame(grid)
        f_prod_box.grid(row=2, column=1, sticky=tk.W, pady=4)

        var_prod = tk.StringVar()
        vincular_maiusculo(var_prod)
        ent_prod = ttk.Entry(f_prod_box, textvariable=var_prod, width=14, font=("Segoe UI", 9, "bold"))
        ent_prod.pack(side=tk.LEFT, padx=(0, 6))

        lbl_prod_nome = tk.Label(
            f_prod_box,
            text="",
            font=("Segoe UI", 9, "bold"),
            bg="#F1F5F9",
            fg="#475569",
            padx=6,
            pady=2,
            relief=tk.RIDGE,
        )

        saldo_info = {"saldo": 0.0}

        def _definir_prod_saida(cod, nome, unid, saldo):
            var_prod.set(cod)
            saldo_info["saldo"] = saldo
            cor_bg = "#DCFCE7" if saldo > 0 else "#FEE2E2"
            cor_fg = "#15803D" if saldo > 0 else "#B91C1C"
            lbl_prod_nome.config(
                text=f"{nome} ({unid}) | Saldo: {saldo:.2f}",
                bg=cor_bg,
                fg=cor_fg,
            )

        def _buscar_prod_click():
            self._abrir_modal_busca_produtos(_definir_prod_saida, var_prod.get().strip())

        btn_busca_p = ttk.Button(f_prod_box, text="🔍 Buscar (F4)", command=_buscar_prod_click)
        btn_busca_p.pack(side=tk.LEFT, padx=(0, 6))
        lbl_prod_nome.pack(side=tk.LEFT, padx=(0, 4))

        def _ao_sair_prod_saida(event=None):
            cod = var_prod.get().strip()
            if not cod:
                lbl_prod_nome.config(text="", bg="#F1F5F9", fg="#475569")
                return
            saldos = self.service.consultar_saldos_produtos(empcod=var_emp.get().strip() or "1.01", termo_busca=cod)
            encontrado = False
            for p in saldos:
                if str(p.prodcod_estr).strip().upper() == cod.upper():
                    _definir_prod_saida(p.prodcod_estr, p.prodnome, p.unidade, p.saldo_atual)
                    encontrado = True
                    break
            if not encontrado:
                try:
                    cur = self.service.repo._get_cursor()
                    nolock = self.service.repo._nolock()
                    cur.execute(f"SELECT prodcod, prodnome FROM USER_geoapolo_produtos {nolock} WHERE CAST(prodcod AS VARCHAR) = ?", [cod])
                    r = cur.fetchone()
                    if r:
                        _definir_prod_saida(str(r[0]), str(r[1] or ""), "UN", 0.0)
                        encontrado = True
                except Exception:
                    pass
            if not encontrado:
                lbl_prod_nome.config(text="⚠️ Produto não localizado", bg="#FEE2E2", fg="#B91C1C")

        ent_prod.bind("<FocusOut>", _ao_sair_prod_saida)
        ent_prod.bind("<Return>", lambda e: _ao_sair_prod_saida())

        # Centro de Custo
        ttk.Label(grid, text="Centro de Custo: *", font=("Segoe UI", 9, "bold")).grid(row=3, column=0, sticky=tk.W, pady=4)
        var_cctrl_s = tk.StringVar()
        cb_cctrl_s = ttk.Combobox(grid, textvariable=var_cctrl_s, width=38)
        cb_cctrl_s.grid(row=3, column=1, sticky=tk.W, pady=4)
        centros_s = self.service.listar_centros_custo(var_emp.get().strip() or obter_empresa_ativa()) if self.service else []
        lista_centros_s = [f"{c[0]} - {c[1]}" for c in centros_s]
        habilitar_filtro_dinamico_combobox(cb_cctrl_s, lista_centros_s)
        if lista_centros_s:
            cb_cctrl_s.current(0)

        # Número do Lote com Busca F4
        ttk.Label(grid, text="Número do Lote:").grid(row=4, column=0, sticky=tk.W, pady=4)
        f_lote_box = ttk.Frame(grid)
        f_lote_box.grid(row=4, column=1, sticky=tk.W, pady=4)

        var_lote = tk.StringVar()
        vincular_maiusculo(var_lote)
        ent_lote = ttk.Entry(f_lote_box, textvariable=var_lote, width=20, font=("Segoe UI", 9, "bold"))
        ent_lote.pack(side=tk.LEFT, padx=(0, 6))

        def _consultar_lotes_click():
            p_val = var_prod.get().strip()
            if not p_val:
                messagebox.showwarning("Aviso", "Selecione o produto primeiro.", parent=modal)
                ent_prod.focus_set()
                return
            try:
                p_int = int(p_val)
            except ValueError:
                p_int = None
            from lotes import abrir_janela_lotes
            abrir_janela_lotes(modal, prodcod=p_int, callback=lambda num: var_lote.set(num))

        btn_ver_lotes = ttk.Button(f_lote_box, text="🏷 Lotes (F4)", command=_consultar_lotes_click)
        btn_ver_lotes.pack(side=tk.LEFT)

        # Quantidade
        ttk.Label(grid, text="Quantidade: *", font=("Segoe UI", 9, "bold")).grid(row=5, column=0, sticky=tk.W, pady=4)
        f_qtd_box = ttk.Frame(grid)
        f_qtd_box.grid(row=5, column=1, sticky=tk.W, pady=4)
        var_qtd = tk.StringVar()
        ent_qtd = ttk.Entry(f_qtd_box, textvariable=var_qtd, width=15, font=("Segoe UI", 9, "bold"))
        ent_qtd.pack(side=tk.LEFT, padx=(0, 8))

        lbl_aviso_saldo = tk.Label(f_qtd_box, text="", font=("Segoe UI", 8, "bold"), fg="#DC2626")
        lbl_aviso_saldo.pack(side=tk.LEFT)

        def _verificar_saldo_ao_digitar(*args):
            try:
                v = float(var_qtd.get().replace(",", "."))
                if v > saldo_info["saldo"] and saldo_info["saldo"] >= 0:
                    lbl_aviso_saldo.config(text=f"⚠️ Excede saldo ({saldo_info['saldo']:.2f})")
                else:
                    lbl_aviso_saldo.config(text="")
            except Exception:
                lbl_aviso_saldo.config(text="")

        var_qtd.trace_add("write", _verificar_saldo_ao_digitar)

        # Destino / Observação
        ttk.Label(grid, text="Destino / Motivo:").grid(row=6, column=0, sticky=tk.W, pady=4)
        var_obs = tk.StringVar()
        vincular_maiusculo(var_obs)
        ent_obs = ttk.Entry(grid, textvariable=var_obs, width=38)
        ent_obs.grid(row=6, column=1, sticky=tk.W, pady=4)


        # Botões
        b_box = ttk.Frame(f_cont)
        b_box.pack(fill=tk.X, pady=(15, 0))

        def confirmar_saida():
            try:
                prod = var_prod.get().strip()
                if not prod:
                    messagebox.showerror("Erro", "Código do produto é obrigatório.", parent=modal)
                    ent_prod.focus_set()
                    return

                try:
                    qtd_val = float(var_qtd.get().replace(",", "."))
                except ValueError:
                    messagebox.showerror("Erro", "Quantidade inválida.", parent=modal)
                    ent_qtd.focus_set()
                    return

                if qtd_val <= 0:
                    messagebox.showerror("Erro", "A quantidade de saída deve ser maior que zero.", parent=modal)
                    ent_qtd.focus_set()
                    return

                cctrl_val = var_cctrl_s.get().strip()
                if not cctrl_val:
                    messagebox.showerror("Erro", "O Centro de Custo é obrigatório.", parent=modal)
                    cb_cctrl_s.focus_set()
                    return
                cctrl_cod = cctrl_val.split(" - ")[0].strip()
                for c in centros_s:
                    if c[0].upper() == cctrl_val.upper() or cctrl_val.upper() in c[1].upper():
                        cctrl_cod = c[0]
                        break

                if qtd_val > saldo_info["saldo"]:
                    emp_val = var_emp.get().strip() or "1.01"
                    permite_neg = self.service.permite_estoque_negativo(emp_val) if self.service else False
                    if not permite_neg:
                        messagebox.showwarning(
                            "Atenção: Saldo Insuficiente",
                            "O sistema não permite estoque negativo, este produto não tem em estoque e não permite movimentação",
                            parent=modal,
                        )
                        return
                    elif not messagebox.askyesno(
                        "Atenção: Saldo Insuficiente",
                        f"A quantidade a baixar ({qtd_val:.2f}) é maior que o saldo atual ({saldo_info['saldo']:.2f}).\n\n"
                        f"Deseja confirmar a saída direta mesmo com saldo insuficiente?",
                        parent=modal,
                    ):
                        return

                # Verificação de Controle de Lote e Validade
                lote_val = var_lote.get().strip().upper()
                p_nome = lbl_prod_nome.cget("text") or f"Produto {prod}"
                if prod:
                    try:
                        p_int = int(prod)
                        from lotes.service import LotesService
                        from lotes.repository import LotesRepository
                        from lotes.alerta_vencimento_view import exibir_alerta_vencimento_lote

                        lote_repo = LotesRepository(self.service._repo.conn)
                        lote_svc = LotesService(lote_repo)

                        controla_lote = lote_svc.produto_controla_lote(p_int)

                        if controla_lote:
                            if not lote_val:
                                messagebox.showwarning(
                                    "Lote Obrigatório",
                                    f"O produto '{p_nome}' possui CONTROLE DE LOTE ativado.\n\n"
                                    "Por favor, informe ou selecione o Lote do material (tecle F4).",
                                    parent=modal,
                                )
                                ent_lote.focus_set()
                                return

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
                            nivel, dias, dt_val_fmt = lote_svc.verificar_vencimento_lote(p_int, lote_val)

                            if nivel == "ROXO":
                                # BLOQUEIO ABSOLUTO (0 a 5 dias ou vencido)
                                exibir_alerta_vencimento_lote(
                                    modal,
                                    nivel="ROXO",
                                    numero_lote=lote_val,
                                    prodnome=p_nome,
                                    data_validade=dt_val_fmt,
                                    dias_restantes=dias,
                                )
                                return
                            elif nivel in ("VERMELHO", "AMARELO"):
                                prosseguir = exibir_alerta_vencimento_lote(
                                    modal,
                                    nivel=nivel,
                                    numero_lote=lote_val,
                                    prodnome=p_nome,
                                    data_validade=dt_val_fmt,
                                    dias_restantes=dias,
                                )
                                if not prosseguir:
                                    return
                        else:
                            # Caso o produto não controle lote, mas o usuário preencheu um lote existente
                            if lote_val and lote_svc.lote_existe(p_int, lote_val):
                                nivel, dias, dt_val_fmt = lote_svc.verificar_vencimento_lote(p_int, lote_val)
                                if nivel == "ROXO":
                                    exibir_alerta_vencimento_lote(
                                        modal,
                                        nivel="ROXO",
                                        numero_lote=lote_val,
                                        prodnome=p_nome,
                                        data_validade=dt_val_fmt,
                                        dias_restantes=dias,
                                    )
                                    return
                                elif nivel in ("VERMELHO", "AMARELO"):
                                    if not exibir_alerta_vencimento_lote(modal, nivel, lote_val, p_nome, dt_val_fmt, dias):
                                        return
                    except Exception as ex_lote:
                        logger.warning("Erro na validação de lote da saída direta: %s", ex_lote)

                cod_almox = var_almox_s.get().strip().upper()
                if not cod_almox:
                    messagebox.showerror("Erro", "O Almoxarifado é obrigatório.", parent=modal)
                    ent_almox_s.focus_set()
                    return

                res = self.service.registrar_saida_direta(
                    empcod=var_emp.get().strip() or "1.01",
                    prodcod_estr=prod,
                    quantidade=qtd_val,
                    destino_obs=var_obs.get().strip(),
                    centro_custo=cctrl_cod,
                    numero_lote=lote_val,
                )
                if res.sucesso:
                    try:
                        from estoque.almoxarifados_repository import AlmoxarifadosRepository
                        repo_almox = AlmoxarifadosRepository()
                        repo_almox.atualizar_saldo(cod_almox, int(prod), -qtd_val)
                    except Exception:
                        pass
                    messagebox.showinfo("Sucesso", res.mensagem, parent=modal)
                    modal.destroy()
                    self.carregar_movimentacoes()
                else:
                    messagebox.showerror("Erro ao Registrar Saída", res.mensagem, parent=modal)
            except Exception as e:
                messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao registrar a saída:\n{e}", parent=modal)

        lbl_dica_modal = ttk.Label(b_box, text="Atalhos: [F4] Buscar | [F10/Enter] Confirmar | [Esc] Cancelar", font=("Segoe UI", 8), foreground="#64748B")
        lbl_dica_modal.pack(side=tk.LEFT)

        btn_conf = tk.Button(
            b_box,
            text="✔ Confirmar Saída Direta (F10 / Enter)",
            bg="#D97706",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            relief=tk.FLAT,
            command=confirmar_saida,
        )
        btn_conf.pack(side=tk.RIGHT, padx=(6, 0))

        btn_canc = ttk.Button(b_box, text="Cancelar (Esc)", command=modal.destroy)
        btn_canc.pack(side=tk.RIGHT)

        def _on_modal_f4(event=None):
            fw = modal.focus_get()
            if fw in (ent_almox_s, btn_busca_almox_s):
                _buscar_almox_s_click()
            elif fw in (ent_lote, btn_ver_lotes):
                _consultar_lotes_click()
            else:
                _buscar_prod_click()

        modal.bind("<F4>", _on_modal_f4)
        modal.bind("<F10>", lambda e: confirmar_saida())
        modal.bind("<Return>", lambda e: confirmar_saida())
        modal.bind("<Escape>", lambda e: modal.destroy())

        configurar_navegacao_enter([ent_emp, ent_almox_s, ent_prod, cb_cctrl_s, ent_lote, ent_qtd, ent_obs, btn_conf])
        ent_almox_s.focus_set()


def abrir_movimentacao_estoque(parent=None, connection=None):
    win = tk.Toplevel(parent)
    win.title("Movimentação de Estoque - GeoAlvo")
    win.minsize(1050, 580)
    centralizar_janela(win, parent, 1180, 680)
    view = MovimentacaoView(win)
    view.pack(fill=tk.BOTH, expand=True)
    return win
