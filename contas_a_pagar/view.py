"""
Interface Gráfica (Tkinter) do Módulo de Contas a Pagar / Documentos Financeiros.
GeoApolo V5
"""

import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List
from datetime import datetime, timedelta

from core import (
    centralizar_janela,
    vincular_mascara_data,
    converter_data_br_para_iso,
    formatar_data_br,
    obter_empresa_ativa,
)
from .models import DocumentoPagarDTO, FiltroContasPagarDTO, BaixaDocumentoDTO
from .service import ContasPagarService


class DocumentosPagarView(ttk.Frame):
    """Tela de Consulta, Gestão e Baixa de Documentos Financeiros a Pagar."""

    def __init__(self, parent=None, service: Optional[ContasPagarService] = None):
        super().__init__(parent)
        self.service = service or ContasPagarService()
        self._documentos: List[DocumentoPagarDTO] = []

        self._setup_ui()
        self._configurar_atalhos()
        self.carregar_documentos()

    def _setup_ui(self):
        # 1. Header Superior
        header = ttk.Frame(self, padding=(14, 10))
        header.pack(fill=tk.X)

        lbl_tit = ttk.Label(
            header,
            text="Documentos Financeiros a Pagar (Contas a Pagar)",
            font=("Segoe UI", 13, "bold"),
            foreground="#1E3A8A",
        )
        lbl_tit.pack(side=tk.LEFT)

        self.badge_status = tk.Label(
            header,
            text="CARREGANDO...",
            bg="#EFF6FF",
            fg="#1D4ED8",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=2,
            relief=tk.RIDGE,
        )
        self.badge_status.pack(side=tk.RIGHT)

        # 2. Painel de Filtros
        frame_filtros = ttk.LabelFrame(self, text=" Filtros de Pesquisa ", padding=(10, 8))
        frame_filtros.pack(fill=tk.X, padx=14, pady=(0, 8))

        row1 = ttk.Frame(frame_filtros)
        row1.pack(fill=tk.X)

        ttk.Label(row1, text="Empresa:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_emp = tk.StringVar(value=obter_empresa_ativa())
        ent_emp = ttk.Entry(row1, textvariable=self.var_emp, width=7)
        ent_emp.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row1, text="Situação:").pack(side=tk.LEFT, padx=(0, 4))
        self.cbo_sit = ttk.Combobox(row1, values=["TODAS", "ABERTO", "QUITADO"], state="readonly", width=11)
        self.cbo_sit.set("TODAS")
        self.cbo_sit.pack(side=tk.LEFT, padx=(0, 14))
        self.cbo_sit.bind("<<ComboboxSelected>>", lambda e: self.carregar_documentos())

        ttk.Label(row1, text="Vencimento De:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_dt_ini = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y"))
        ent_ini = ttk.Entry(row1, textvariable=self.var_dt_ini, width=11)
        ent_ini.pack(side=tk.LEFT, padx=(0, 8))
        vincular_mascara_data(ent_ini)

        ttk.Label(row1, text="Até:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_dt_fim = tk.StringVar(value=(datetime.now() + timedelta(days=90)).strftime("%d/%m/%Y"))
        ent_fim = ttk.Entry(row1, textvariable=self.var_dt_fim, width=11)
        ent_fim.pack(side=tk.LEFT, padx=(0, 14))
        vincular_mascara_data(ent_fim)

        ttk.Label(row1, text="Buscar:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_busca = tk.StringVar()
        ent_busca = ttk.Entry(row1, textvariable=self.var_busca, width=20)
        ent_busca.pack(side=tk.LEFT, padx=(0, 10))
        ent_busca.bind("<Return>", lambda e: self.carregar_documentos())

        btn_filtrar = ttk.Button(row1, text="🔍 Filtrar (F5)", command=self.carregar_documentos)
        btn_filtrar.pack(side=tk.LEFT, padx=(4, 0))

        # 3. Cards de Resumo
        cards_bar = ttk.Frame(self, padding=(14, 0))
        cards_bar.pack(fill=tk.X, pady=(0, 8))

        self.card_qtd = tk.Label(cards_bar, text="Títulos: 0", bg="#F1F5F9", fg="#334155", font=("Segoe UI", 9, "bold"), padx=12, pady=6, relief=tk.RIDGE)
        self.card_qtd.pack(side=tk.LEFT, padx=(0, 8))

        self.card_orig = tk.Label(cards_bar, text="Total R$: 0,00", bg="#EFF6FF", fg="#1E40AF", font=("Segoe UI", 9, "bold"), padx=12, pady=6, relief=tk.RIDGE)
        self.card_orig.pack(side=tk.LEFT, padx=(0, 8))

        self.card_aberto = tk.Label(cards_bar, text="Em Aberto: R$ 0,00", bg="#FEF2F2", fg="#B91C1C", font=("Segoe UI", 9, "bold"), padx=12, pady=6, relief=tk.RIDGE)
        self.card_aberto.pack(side=tk.LEFT, padx=(0, 8))

        self.card_pago = tk.Label(cards_bar, text="Quitado: R$ 0,00", bg="#F0FDF4", fg="#15803D", font=("Segoe UI", 9, "bold"), padx=12, pady=6, relief=tk.RIDGE)
        self.card_pago.pack(side=tk.LEFT)

        # 4. Tabela de Documentos a Pagar
        grid_frame = ttk.Frame(self, padding=(14, 0))
        grid_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("cod", "doc", "forn", "emis", "venc", "val_orig", "saldo", "sit", "cctrl", "mov")
        self.tree = ttk.Treeview(grid_frame, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("cod", text="Cód")
        self.tree.heading("doc", text="Nº Documento / NF")
        self.tree.heading("forn", text="Fornecedor / Razão Social")
        self.tree.heading("emis", text="Emissão")
        self.tree.heading("venc", text="Vencimento")
        self.tree.heading("val_orig", text="Valor Total (R$)")
        self.tree.heading("saldo", text="Saldo Aberto (R$)")
        self.tree.heading("sit", text="Situação")
        self.tree.heading("cctrl", text="Centro de Custo")
        self.tree.heading("mov", text="Mov. Estoque")

        self.tree.column("cod", width=65, anchor=tk.CENTER)
        self.tree.column("doc", width=125, anchor=tk.W)
        self.tree.column("forn", width=220, anchor=tk.W)
        self.tree.column("emis", width=90, anchor=tk.CENTER)
        self.tree.column("venc", width=95, anchor=tk.CENTER)
        self.tree.column("val_orig", width=110, anchor=tk.E)
        self.tree.column("saldo", width=110, anchor=tk.E)
        self.tree.column("sit", width=95, anchor=tk.CENTER)
        self.tree.column("cctrl", width=120, anchor=tk.W)
        self.tree.column("mov", width=90, anchor=tk.CENTER)

        scroll_y = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scroll_x = ttk.Scrollbar(grid_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.tag_configure("ABERTO", foreground="#B91C1C")
        self.tree.tag_configure("QUITADO", foreground="#15803D")

        # 5. Barra Inferior de Ações
        footer = ttk.Frame(self, padding=(14, 10))
        footer.pack(fill=tk.X)

        lbl_atalhos = ttk.Label(
            footer,
            text="[F5] Atualizar | [F8] Baixar Título | [F4] Detalhes | [F10] Exportar CSV | [Esc] Fechar",
            font=("Segoe UI", 8),
            foreground="#64748B",
        )
        lbl_atalhos.pack(side=tk.LEFT)

        btn_fechar = ttk.Button(footer, text="✕ Fechar (Esc)", command=self._fechar)
        btn_fechar.pack(side=tk.RIGHT, padx=(6, 0))

        btn_csv = ttk.Button(footer, text="📥 Exportar CSV (F10)", command=self._exportar_csv)
        btn_csv.pack(side=tk.RIGHT, padx=(6, 0))

        btn_detalhe = ttk.Button(footer, text="🔍 Detalhes (F4)", command=self._ver_detalhes)
        btn_detalhe.pack(side=tk.RIGHT, padx=(6, 0))

        self.btn_baixa = tk.Button(
            footer,
            text="💰 Baixar Título (F8)",
            bg="#16A34A",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=10,
            pady=4,
            command=self._abrir_modal_baixa,
        )
        self.btn_baixa.pack(side=tk.RIGHT)

    def _configurar_atalhos(self):
        root = self.winfo_toplevel()
        root.bind("<F5>", lambda e: self.carregar_documentos())
        root.bind("<F8>", lambda e: self._abrir_modal_baixa())
        root.bind("<F4>", lambda e: self._ver_detalhes())
        root.bind("<F10>", lambda e: self._exportar_csv())
        root.bind("<Escape>", lambda e: self._fechar())

    def _fechar(self):
        top = self.winfo_toplevel()
        if top != self:
            top.destroy()

    def carregar_documentos(self):
        """Carrega e exibe os documentos a pagar na Treeview."""
        if not self.service.tabela_disponivel():
            self.badge_status.config(text="TABELA INEXISTENTE NO BANCO", bg="#FEF2F2", fg="#B91C1C")
            for item in self.tree.get_children():
                self.tree.delete(item)
            msg = (
                "Aviso: A tabela USER_geoapolo_contas_a_pagar ainda não foi criada no banco SQL Server.\n\n"
                "Para ativar este módulo, aplique o script localizado em:\n"
                "sql/criar_tabela_contas_a_pagar.sql\n\n"
                "Deseja criar a tabela agora automaticamente?"
            )
            if messagebox.askyesno("Tabela Pendente", msg, parent=self):
                sucesso, res_msg = self.service.criar_tabela_banco()
                if sucesso:
                    messagebox.showinfo("Sucesso", res_msg, parent=self)
                else:
                    messagebox.showerror("Erro ao Criar Tabela", res_msg, parent=self)
                    return
            else:
                return

        # Monta filtro
        d_ini = converter_data_br_para_iso(self.var_dt_ini.get().strip()[:10]) if self.var_dt_ini.get().strip() else None
        d_fim = converter_data_br_para_iso(self.var_dt_fim.get().strip()[:10]) if self.var_dt_fim.get().strip() else None

        filtro = FiltroContasPagarDTO(
            codigo_empresa=self.var_emp.get().strip() or obter_empresa_ativa(),
            data_ini=d_ini,
            data_fim=d_fim,
            situacao=self.cbo_sit.get(),
            termo_busca=self.var_busca.get().strip(),
        )

        self._documentos = self.service.listar_titulos(filtro)
        resumo = self.service.obter_resumo(filtro)

        # Atualiza cards
        self.card_qtd.config(text=f"Títulos: {resumo.total_titulos}")
        self.card_orig.config(text=f"Total R$: {resumo.total_original:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        self.card_aberto.config(text=f"Em Aberto: R$ {resumo.total_aberto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        self.card_pago.config(text=f"Quitado: R$ {resumo.total_pago:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        self.badge_status.config(
            text=f"STATUS: ATIVO ({len(self._documentos)} REGISTROS)",
            bg="#EFF6FF",
            fg="#1D4ED8",
        )

        # Limpa e preenche Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        for d in self._documentos:
            d_emis_br = formatar_data_br(d.data_emissao) if d.data_emissao else ""
            d_venc_br = formatar_data_br(d.data_vencimento) if d.data_vencimento else ""
            mov_str = str(d.codigo_movimento_estoque) if d.codigo_movimento_estoque else "-"

            self.tree.insert(
                "",
                tk.END,
                iid=str(d.codigo_documento),
                values=(
                    d.codigo_documento,
                    d.numero_documento,
                    d.fornecedor_nome,
                    d_emis_br,
                    d_venc_br,
                    f"{d.valor_original:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    f"{d.saldo_aberto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    d.situacao,
                    d.centro_custo or "-",
                    mov_str,
                ),
                tags=(d.situacao.upper(),),
            )

    def _obter_selecionado(self) -> Optional[DocumentoPagarDTO]:
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um título na lista primeiro.", parent=self)
            return None
        cod = int(sel[0])
        for d in self._documentos:
            if d.codigo_documento == cod:
                return d
        return None

    def _ver_detalhes(self):
        doc = self._obter_selecionado()
        if not doc:
            return

        modal = tk.Toplevel(self)
        modal.title(f"Detalhes do Título a Pagar Nº {doc.codigo_documento}")
        centralizar_janela(modal, self, 560, 480)
        modal.transient(self)

        f_cont = ttk.Frame(modal, padding=16)
        f_cont.pack(fill=tk.BOTH, expand=True)

        ttk.Label(f_cont, text=f"Título Financeiro Nº {doc.codigo_documento}", font=("Segoe UI", 12, "bold"), foreground="#1E3A8A").pack(anchor=tk.W, pady=(0, 10))

        campos = [
            ("Empresa:", doc.codigo_empresa),
            ("Número Documento:", doc.numero_documento),
            ("Fornecedor / Razão:", doc.fornecedor_nome),
            ("Código Fornecedor (Entidade):", doc.entcod or "-"),
            ("Data de Emissão:", formatar_data_br(doc.data_emissao)),
            ("Data de Vencimento:", formatar_data_br(doc.data_vencimento)),
            ("Data de Pagamento:", formatar_data_br(doc.data_pagamento) if doc.data_pagamento else "Pendente"),
            ("Valor Original:", doc.display_valor),
            ("Valor Pago:", f"R$ {doc.valor_pago:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
            ("Saldo em Aberto:", doc.display_saldo),
            ("Situação Atual:", doc.situacao),
            ("Origem:", doc.origem),
            ("Movimento de Estoque Nº:", str(doc.codigo_movimento_estoque) if doc.codigo_movimento_estoque else "Não vinculado"),
            ("Centro de Custo:", doc.centro_custo or "-"),
            ("Observações:", doc.observacoes or "-"),
        ]

        grid = ttk.Frame(f_cont)
        grid.pack(fill=tk.BOTH, expand=True)

        for i, (rotulo, valor) in enumerate(campos):
            ttk.Label(grid, text=rotulo, font=("Segoe UI", 9, "bold")).grid(row=i, column=0, sticky=tk.W, pady=2, padx=(0, 8))
            ttk.Label(grid, text=valor, font=("Segoe UI", 9)).grid(row=i, column=1, sticky=tk.W, pady=2)

        ttk.Button(f_cont, text="Fechar", command=modal.destroy).pack(side=tk.RIGHT, pady=(12, 0))

    def _abrir_modal_baixa(self):
        doc = self._obter_selecionado()
        if not doc:
            return

        if doc.situacao.upper() == "QUITADO" or doc.saldo_aberto <= 0:
            messagebox.showinfo("Título Quitado", "Este título já se encontra totalmente quitado.", parent=self)
            return

        modal = tk.Toplevel(self)
        modal.title(f"Baixa / Pagamento de Título Nº {doc.codigo_documento}")
        centralizar_janela(modal, self, 460, 360)
        modal.transient(self)
        modal.grab_set()

        f = ttk.Frame(modal, padding=16)
        f.pack(fill=tk.BOTH, expand=True)

        ttk.Label(f, text="Liquidação de Documento a Pagar", font=("Segoe UI", 11, "bold"), foreground="#16A34A").pack(anchor=tk.W, pady=(0, 10))

        info_box = tk.Label(
            f,
            text=f"Documento: {doc.numero_documento} | Fornecedor: {doc.fornecedor_nome}\nSaldo em Aberto: {doc.display_saldo}",
            bg="#F8FAFC",
            fg="#1E293B",
            font=("Segoe UI", 9),
            padx=10,
            pady=8,
            relief=tk.GROOVE,
            justify=tk.LEFT,
        )
        info_box.pack(fill=tk.X, pady=(0, 12))

        grid = ttk.Frame(f)
        grid.pack(fill=tk.X)

        ttk.Label(grid, text="Data Pagamento:").grid(row=0, column=0, sticky=tk.W, pady=4)
        var_dt_pag = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))
        ent_dt_pag = ttk.Entry(grid, textvariable=var_dt_pag, width=12)
        ent_dt_pag.grid(row=0, column=1, sticky=tk.W, pady=4)
        vincular_mascara_data(ent_dt_pag)

        ttk.Label(grid, text="Valor Pago (R$): *").grid(row=1, column=0, sticky=tk.W, pady=4)
        var_val_pag = tk.StringVar(value=f"{doc.saldo_aberto:.2f}")
        ent_val_pag = ttk.Entry(grid, textvariable=var_val_pag, width=12)
        ent_val_pag.grid(row=1, column=1, sticky=tk.W, pady=4)

        ttk.Label(grid, text="Desconto (R$):").grid(row=2, column=0, sticky=tk.W, pady=4)
        var_desc = tk.StringVar(value="0.00")
        ent_desc = ttk.Entry(grid, textvariable=var_desc, width=12)
        ent_desc.grid(row=2, column=1, sticky=tk.W, pady=4)

        ttk.Label(grid, text="Juros / Multa (R$):").grid(row=3, column=0, sticky=tk.W, pady=4)
        var_jur = tk.StringVar(value="0.00")
        ent_jur = ttk.Entry(grid, textvariable=var_jur, width=12)
        ent_jur.grid(row=3, column=1, sticky=tk.W, pady=4)

        ttk.Label(grid, text="Observação Baixa:").grid(row=4, column=0, sticky=tk.W, pady=4)
        var_obs_bxa = tk.StringVar(value="PAGAMENTO EFETUADO")
        ent_obs_bxa = ttk.Entry(grid, textvariable=var_obs_bxa, width=28)
        ent_obs_bxa.grid(row=4, column=1, sticky=tk.W, pady=4)

        def _confirmar():
            try:
                v_pago = float(var_val_pag.get().replace(",", "."))
            except ValueError:
                messagebox.showerror("Erro", "Valor pago inválido.", parent=modal)
                return

            try:
                v_desc = float(var_desc.get().replace(",", ".")) if var_desc.get() else 0.0
                v_jur = float(var_jur.get().replace(",", ".")) if var_jur.get() else 0.0
            except ValueError:
                v_desc, v_jur = 0.0, 0.0

            d_iso = converter_data_br_para_iso(var_dt_pag.get().strip()[:10])

            baixa_dto = BaixaDocumentoDTO(
                codigo_documento=doc.codigo_documento,
                data_pagamento=d_iso,
                valor_pago=v_pago,
                valor_desconto=v_desc,
                valor_juros_multa=v_jur,
                observacao_baixa=var_obs_bxa.get().strip().upper(),
            )
            sucesso, msg = self.service.registrar_baixa(baixa_dto)
            if sucesso:
                messagebox.showinfo("Sucesso", msg, parent=modal)
                modal.destroy()
                self.carregar_documentos()
            else:
                messagebox.showerror("Erro na Baixa", msg, parent=modal)

        b_box = ttk.Frame(f)
        b_box.pack(fill=tk.X, pady=(16, 0))

        ttk.Button(b_box, text="Cancelar", command=modal.destroy).pack(side=tk.RIGHT, padx=(6, 0))
        btn_conf = tk.Button(b_box, text="✔ Confirmar Baixa", bg="#16A34A", fg="white", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=3, command=_confirmar)
        btn_conf.pack(side=tk.RIGHT)

    def _exportar_csv(self):
        if not self._documentos:
            messagebox.showwarning("Aviso", "Não há registros para exportar.", parent=self)
            return

        caminho = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".csv",
            filetypes=[("Arquivo CSV", "*.csv")],
            initialfile=f"contas_a_pagar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        )
        if not caminho:
            return

        try:
            with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([
                    "Código", "Empresa", "Nº Documento", "Fornecedor",
                    "Emissão", "Vencimento", "Valor Original", "Saldo Aberto",
                    "Valor Pago", "Situação", "Centro de Custo", "Movimento Estoque", "Observações"
                ])
                for d in self._documentos:
                    writer.writerow([
                        d.codigo_documento,
                        d.codigo_empresa,
                        d.numero_documento,
                        d.fornecedor_nome,
                        formatar_data_br(d.data_emissao),
                        formatar_data_br(d.data_vencimento),
                        f"{d.valor_original:.2f}",
                        f"{d.saldo_aberto:.2f}",
                        f"{d.valor_pago:.2f}",
                        d.situacao,
                        d.centro_custo,
                        d.codigo_movimento_estoque or "",
                        d.observacoes,
                    ])
            messagebox.showinfo("Sucesso", f"Relatório CSV exportado com sucesso!\n{caminho}", parent=self)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar CSV: {e}", parent=self)


def abrir_documentos_pagar(parent=None):
    """Abre a tela de Documentos Financeiros a Pagar em janela TopLevel centralizada."""
    win = tk.Toplevel(parent)
    win.title("Contas a Pagar - Documentos Financeiros - GeoAlvo")
    win.minsize(1050, 640)
    centralizar_janela(win, parent, 1140, 700)
    view = DocumentosPagarView(win)
    view.pack(fill=tk.BOTH, expand=True)
    return win
