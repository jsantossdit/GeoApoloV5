"""
Interface Gráfica Moderna para Conciliação Débito x Crédito.
GeoApolo V5
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from typing import Optional, List
from datetime import date, datetime
from core import centralizar_janela, vincular_mascara_data, parse_data_flexivel
from .models import DebxCredItemDTO, ResumoConciliacaoDTO
from .repository import ContabilidadeRepository
from .service import ContabilidadeService


class DebxCredView:
    """Janela corporativa para auditoria e conciliação contábil Débito x Crédito."""

    def __init__(self, parent: tk.Tk, service: Optional[ContabilidadeService] = None):
        self.parent = parent
        self.service = service or ContabilidadeService(ContabilidadeRepository())

        self.window = tk.Toplevel(parent)
        self.window.title("GeoAlvo - Conciliação Débito x Crédito")
        self.window.minsize(880, 560)
        self.window.transient(parent)
        self.window.grab_set()
        centralizar_janela(self.window, parent, 1020, 660)

        self._itens_atuais: List[DebxCredItemDTO] = []
        self._setup_ui()

    def _setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg="#1A365D", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        lbl_titulo = tk.Label(
            header,
            text="Conciliação Contábil Débito x Crédito",
            font=("Segoe UI", 13, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
        )
        lbl_titulo.pack(side=tk.LEFT, padx=15, pady=12)

        # Container Principal
        container = ttk.Frame(self.window, padding="15")
        container.pack(fill=tk.BOTH, expand=True)

        # Painel de Filtros
        filtro_frame = ttk.LabelFrame(container, text=" Critérios de Conciliação ", padding="10")
        filtro_frame.pack(fill=tk.X, pady=(0, 10))

        hoje = date.today().strftime("%d/%m/%Y")

        ttk.Label(filtro_frame, text="Data Inicial:").grid(row=0, column=0, padx=4, sticky="w")
        self.txt_dt_ini = ttk.Entry(filtro_frame, width=12)
        self.txt_dt_ini.insert(0, hoje)
        self.txt_dt_ini.grid(row=0, column=1, padx=4, sticky="w")
        vincular_mascara_data(self.txt_dt_ini)

        ttk.Label(filtro_frame, text="Data Final:").grid(row=0, column=2, padx=4, sticky="w")
        self.txt_dt_fim = ttk.Entry(filtro_frame, width=12)
        self.txt_dt_fim.insert(0, hoje)
        self.txt_dt_fim.grid(row=0, column=3, padx=4, sticky="w")
        vincular_mascara_data(self.txt_dt_fim)

        ttk.Label(filtro_frame, text="Cód. Reduzido Conta:").grid(row=0, column=4, padx=4, sticky="w")
        f_conta = ttk.Frame(filtro_frame)
        f_conta.grid(row=0, column=5, padx=4, sticky="w")

        self.txt_conta_red = ttk.Entry(f_conta, width=10)
        self.txt_conta_red.pack(side=tk.LEFT)
        self.txt_conta_red.bind("<FocusOut>", self._buscar_nome_conta)
        self.txt_conta_red.bind("<Return>", self._buscar_nome_conta)

        btn_busca_cta = ttk.Button(f_conta, text="🔍", width=3, command=self._abrir_pesquisa_conta)
        btn_busca_cta.pack(side=tk.LEFT, padx=(3, 0))

        self.lbl_nome_conta = ttk.Label(filtro_frame, text="[Todas as Contas]", font=("Segoe UI", 9, "italic"))
        self.lbl_nome_conta.grid(row=0, column=6, padx=6, sticky="w")

        # Linha 2 de filtros
        self.var_somente_diverg = tk.BooleanVar(value=False)
        chk_div = ttk.Checkbutton(
            filtro_frame,
            text="Exibir apenas lançamentos com divergência",
            variable=self.var_somente_diverg,
        )
        chk_div.grid(row=1, column=0, columnspan=4, padx=4, pady=(8, 0), sticky="w")

        btn_box = ttk.Frame(filtro_frame)
        btn_box.grid(row=1, column=4, columnspan=3, pady=(8, 0), sticky="e")

        btn_executar = tk.Button(
            btn_box,
            text="⚡ Conciliar",
            font=("Segoe UI", 9, "bold"),
            bg="#2B6CB0",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=12,
            pady=3,
            command=self._executar_conciliacao,
            cursor="hand2",
        )
        btn_executar.pack(side=tk.LEFT, padx=4)

        btn_exportar = ttk.Button(btn_box, text="📥 Exportar CSV", command=self._exportar_csv)
        btn_exportar.pack(side=tk.LEFT, padx=4)

        btn_limpar = ttk.Button(btn_box, text="Limpar", command=self._limpar_filtros)
        btn_limpar.pack(side=tk.LEFT, padx=4)

        # Grid Treeview
        grid_frame = ttk.Frame(container)
        grid_frame.pack(fill=tk.BOTH, expand=True)

        colunas = ("chave", "data", "deb", "cred", "val_deb", "val_cred", "dif", "hist", "doc", "mod")
        self.tree = ttk.Treeview(grid_frame, columns=colunas, show="headings")

        self.tree.heading("chave", text="Chave")
        self.tree.heading("data", text="Data")
        self.tree.heading("deb", text="Cta Débito")
        self.tree.heading("cred", text="Cta Crédito")
        self.tree.heading("val_deb", text="Valor Débito (R$)")
        self.tree.heading("val_cred", text="Valor Crédito (R$)")
        self.tree.heading("dif", text="Diferença (R$)")
        self.tree.heading("hist", text="Histórico")
        self.tree.heading("doc", text="Documento")
        self.tree.heading("mod", text="Módulo")

        self.tree.column("chave", width=80, anchor="w")
        self.tree.column("data", width=85, anchor="center")
        self.tree.column("deb", width=80, anchor="w")
        self.tree.column("cred", width=80, anchor="w")
        self.tree.column("val_deb", width=110, anchor="e")
        self.tree.column("val_cred", width=110, anchor="e")
        self.tree.column("dif", width=100, anchor="e")
        self.tree.column("hist", width=220, anchor="w")
        self.tree.column("doc", width=85, anchor="w")
        self.tree.column("mod", width=85, anchor="w")

        scroll_y = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Rodapé com Balanço / Totais
        totais_frame = tk.Frame(container, bg="#EDF2F7", bd=1, relief=tk.SOLID, padx=12, pady=8)
        totais_frame.pack(fill=tk.X, pady=(10, 0))

        self.lbl_tot_deb = tk.Label(totais_frame, text="Total Débito: R$ 0,00", font=("Segoe UI", 10, "bold"), bg="#EDF2F7", fg="#2C5282")
        self.lbl_tot_deb.pack(side=tk.LEFT, padx=10)

        self.lbl_tot_cred = tk.Label(totais_frame, text="Total Crédito: R$ 0,00", font=("Segoe UI", 10, "bold"), bg="#EDF2F7", fg="#2C5282")
        self.lbl_tot_cred.pack(side=tk.LEFT, padx=10)

        self.lbl_saldo = tk.Label(totais_frame, text="Saldo / Divergência: R$ 0,00", font=("Segoe UI", 10, "bold"), bg="#EDF2F7", fg="#285E61")
        self.lbl_saldo.pack(side=tk.LEFT, padx=15)

        self.lbl_registros = tk.Label(totais_frame, text="Registros: 0", font=("Segoe UI", 9), bg="#EDF2F7", fg="#4A5568")
        self.lbl_registros.pack(side=tk.RIGHT, padx=10)

    def _abrir_pesquisa_conta(self):
        """Abre janela de pesquisa de contas contábeis do Alvo (plano_cta) filtrando por empresa."""
        try:
            from logon import sessao_usuario_atual
            emp = sessao_usuario_atual.get("codigo_empresa") or getattr(self.parent, "empresa_ativa", "1.01")
        except Exception:
            emp = "1.01"

        modal = tk.Toplevel(self.window)
        modal.title(f"Pesquisa de Contas Contábeis (Empresa: {emp})")
        modal.geometry("720x460")
        modal.minsize(600, 380)
        modal.transient(self.window)
        modal.grab_set()
        centralizar_janela(modal, self.window, 720, 460)

        # Header de busca
        f_top = ttk.Frame(modal, padding="10")
        f_top.pack(fill=tk.X)

        ttk.Label(f_top, text="Buscar Conta / Código:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        var_termo = tk.StringVar()
        ent_termo = ttk.Entry(f_top, textvariable=var_termo, width=35)
        ent_termo.pack(side=tk.LEFT, padx=(0, 8))
        ent_termo.focus_set()

        tree_frame = ttk.Frame(modal, padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("cod_reduzido", "nome", "cod_estrutural", "tipo")
        tree_contas = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        tree_contas.heading("cod_reduzido", text="Cód. Reduzido")
        tree_contas.heading("nome", text="Nome da Conta Contábil")
        tree_contas.heading("cod_estrutural", text="Cód. Estrutural")
        tree_contas.heading("tipo", text="Tipo")

        tree_contas.column("cod_reduzido", width=110, anchor=tk.CENTER)
        tree_contas.column("nome", width=340, anchor=tk.W)
        tree_contas.column("cod_estrutural", width=140, anchor=tk.W)
        tree_contas.column("tipo", width=60, anchor=tk.CENTER)

        sb_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree_contas.yview)
        tree_contas.configure(yscrollcommand=sb_y.set)
        tree_contas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_y.pack(side=tk.RIGHT, fill=tk.Y)

        def _carregar_contas():
            tree_contas.delete(*tree_contas.get_children())
            termo = var_termo.get().strip()
            contas = self.service.pesquisar_plano_contas(empcod=emp, termo=termo)
            for c in contas:
                tree_contas.insert("", tk.END, values=(c["cod_reduzido"], c["nome"], c["cod_estrutural"], c["tipo"]))

        btn_pesq = ttk.Button(f_top, text="🔍 Buscar", command=_carregar_contas)
        btn_pesq.pack(side=tk.LEFT)
        ent_termo.bind("<Return>", lambda e: _carregar_contas())
        ent_termo.bind("<KeyRelease>", lambda e: _carregar_contas())

        def _confirmar():
            sel = tree_contas.selection()
            if not sel:
                messagebox.showwarning("Atenção", "Selecione uma conta na lista.", parent=modal)
                return
            valores = tree_contas.item(sel[0], "values")
            cod_red = valores[0]
            nome_cta = valores[1]
            self.txt_conta_red.delete(0, tk.END)
            self.txt_conta_red.insert(0, cod_red)
            self.lbl_nome_conta.config(text=f"Conta: {nome_cta}")
            try:
                modal.destroy()
            except Exception:
                pass
            return "break"

        tree_contas.bind("<Double-1>", lambda e: (_confirmar(), "break")[1])
        tree_contas.bind("<Return>", lambda e: (_confirmar(), "break")[1])
        modal.bind("<Return>", lambda e: (_confirmar(), "break")[1])
        modal.bind("<Escape>", lambda e: (modal.destroy(), "break")[1])

        f_bottom = ttk.Frame(modal, padding="10")
        f_bottom.pack(fill=tk.X)
        btn_conf = ttk.Button(f_bottom, text="✔️ Selecionar", command=_confirmar)
        btn_conf.pack(side=tk.RIGHT, padx=4)
        btn_canc = ttk.Button(f_bottom, text="Cancelar (Esc)", command=modal.destroy)
        btn_canc.pack(side=tk.RIGHT, padx=4)

        _carregar_contas()

    def _buscar_nome_conta(self, event=None):
        cod = self.txt_conta_red.get().strip()
        if not cod:
            self.lbl_nome_conta.config(text="[Todas as Contas]")
            return
        try:
            nome = self.service.obter_nome_conta_contabil(cod)
            if nome:
                self.lbl_nome_conta.config(text=f"Conta: {nome}")
            else:
                self.lbl_nome_conta.config(text="[Conta não encontrada]")
        except Exception:
            self.lbl_nome_conta.config(text="")

    def _executar_conciliacao(self):
        for it in self.tree.get_children():
            self.tree.delete(it)

        dt_ini = parse_data_flexivel(self.txt_dt_ini.get().strip())
        dt_fim = parse_data_flexivel(self.txt_dt_fim.get().strip())
        if not dt_ini or not dt_fim:
            messagebox.showwarning("Data Inválida", "Informe as datas no formato DD/MM/AAAA.")
            return

        cod_red = self.txt_conta_red.get().strip() or None
        somente_div = self.var_somente_diverg.get()

        try:
            itens, resumo = self.service.conciliar_debxcred(dt_ini, dt_fim, cod_red, somente_div)
            self._itens_atuais = itens

            for it in itens:
                dt_str = it.data.strftime("%d/%m/%Y") if it.data else ""
                val_deb_str = f"{it.valor_debito:,.2f}"
                val_cred_str = f"{it.valor_credito:,.2f}"
                dif = it.valor_debito - it.valor_credito
                dif_str = f"{dif:,.2f}"

                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        it.chave,
                        dt_str,
                        it.conta_debito,
                        it.conta_credito,
                        val_deb_str,
                        val_cred_str,
                        dif_str,
                        it.historico,
                        it.documento,
                        it.modulo_origem,
                    ),
                )

            # Atualizar totais
            self.lbl_tot_deb.config(text=f"Total Débito: R$ {resumo.total_debito:,.2f}")
            self.lbl_tot_cred.config(text=f"Total Crédito: R$ {resumo.total_credito:,.2f}")
            self.lbl_registros.config(
                text=f"Registros: {resumo.total_registros} ({resumo.total_divergentes} divergentes)"
            )

            if abs(resumo.saldo_divergencia) > 0.001:
                self.lbl_saldo.config(
                    text=f"Saldo / Divergência: R$ {resumo.saldo_divergencia:,.2f} ⚠",
                    fg="#C53030",
                )
            else:
                self.lbl_saldo.config(
                    text="Saldo Conciliado: R$ 0,00 ✔",
                    fg="#22543D",
                )

        except Exception as e:
            messagebox.showerror("Erro de Conciliação", f"Falha na conciliação contábil:\n{e}")

    def _exportar_csv(self):
        if not self._itens_atuais:
            messagebox.showwarning("Aviso", "Não há dados conciliados para exportar.")
            return

        caminho = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Arquivo CSV", "*.csv"), ("Todos os arquivos", "*.*")],
            title="Salvar Conciliação Contábil",
        )
        if not caminho:
            return

        try:
            with open(caminho, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([
                    "Chave",
                    "Data",
                    "Conta Débito",
                    "Conta Crédito",
                    "Valor Débito",
                    "Valor Crédito",
                    "Diferença",
                    "Histórico",
                    "Documento",
                    "Módulo",
                ])
                for it in self._itens_atuais:
                    dif = it.valor_debito - it.valor_credito
                    writer.writerow([
                        it.chave,
                        it.data.strftime("%d/%m/%Y") if it.data else "",
                        it.conta_debito,
                        it.conta_credito,
                        f"{it.valor_debito:.2f}".replace(".", ","),
                        f"{it.valor_credito:.2f}".replace(".", ","),
                        f"{dif:.2f}".replace(".", ","),
                        it.historico,
                        it.documento,
                        it.modulo_origem,
                    ])
            messagebox.showinfo("Exportação Concluída", f"Arquivo salvo com sucesso em:\n{caminho}")
        except Exception as e:
            messagebox.showerror("Erro ao Exportar", f"Não foi possível salvar o arquivo:\n{e}")

    def _limpar_filtros(self):
        hoje = date.today().strftime("%Y-%m-%d")
        self.txt_dt_ini.delete(0, tk.END)
        self.txt_dt_ini.insert(0, hoje)
        self.txt_dt_fim.delete(0, tk.END)
        self.txt_dt_fim.insert(0, hoje)
        self.txt_conta_red.delete(0, tk.END)
        self.lbl_nome_conta.config(text="[Todas as Contas]")
        self.var_somente_diverg.set(False)
        for it in self.tree.get_children():
            self.tree.delete(it)
        self._itens_atuais = []
        self.lbl_tot_deb.config(text="Total Débito: R$ 0,00")
        self.lbl_tot_cred.config(text="Total Crédito: R$ 0,00")
        self.lbl_saldo.config(text="Saldo / Divergência: R$ 0,00", fg="#285E61")
        self.lbl_registros.config(text="Registros: 0")
