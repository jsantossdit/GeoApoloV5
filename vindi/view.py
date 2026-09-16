"""
Interface Gráfica para Conciliação de Transações Vindi.
GeoApolo V5
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from datetime import date, datetime
from .models import TransacaoVindiDTO
from .repository import VindiRepository
from .service import VindiService


class ConciliacaoVindiView:
    """Janela corporativa para conciliação financeira de doações e assinaturas Vindi."""

    def __init__(self, parent: tk.Tk, service: Optional[VindiService] = None):
        self.parent = parent
        self.service = service or VindiService(VindiRepository())

        self.window = tk.Toplevel(parent)
        self.window.title("GeoAlvo - Conciliação Vindi Crédito Recorrente (RCC)")
        self.window.geometry("1060x680")
        self.window.minsize(920, 580)
        self.window.transient(parent)
        self.window.grab_set()

        self._transacoes_atuais: List[TransacaoVindiDTO] = []
        self._setup_ui()

    def _setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg="#1A365D", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        lbl_titulo = tk.Label(
            header,
            text="Conciliação Financeira Vindi - Doações & Crédito Recorrente RCC",
            font=("Segoe UI", 13, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
        )
        lbl_titulo.pack(side=tk.LEFT, padx=15, pady=12)

        # Container Principal
        container = ttk.Frame(self.window, padding="15")
        container.pack(fill=tk.BOTH, expand=True)

        # Painel de Filtros
        filtro_frame = ttk.LabelFrame(container, text=" Parâmetros de Conciliação ", padding="10")
        filtro_frame.pack(fill=tk.X, pady=(0, 10))

        hoje = date.today().strftime("%Y-%m-%d")
        ttk.Label(filtro_frame, text="Data Inicial:").grid(row=0, column=0, padx=4, sticky="w")
        self.txt_dt_ini = ttk.Entry(filtro_frame, width=12)
        self.txt_dt_ini.insert(0, hoje)
        self.txt_dt_ini.grid(row=0, column=1, padx=4, sticky="w")

        ttk.Label(filtro_frame, text="Data Final:").grid(row=0, column=2, padx=4, sticky="w")
        self.txt_dt_fim = ttk.Entry(filtro_frame, width=12)
        self.txt_dt_fim.insert(0, hoje)
        self.txt_dt_fim.grid(row=0, column=3, padx=4, sticky="w")

        self.var_nao_integ = tk.BooleanVar(value=False)
        chk_integ = ttk.Checkbutton(
            filtro_frame,
            text="Apenas não integradas no Apolo",
            variable=self.var_nao_integ,
        )
        chk_integ.grid(row=0, column=4, padx=15, sticky="w")

        btn_conciliar = tk.Button(
            filtro_frame,
            text="⚡ Conciliar Período",
            font=("Segoe UI", 9, "bold"),
            bg="#2B6CB0",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=14,
            pady=4,
            command=self._executar_conciliacao,
            cursor="hand2",
        )
        btn_conciliar.grid(row=0, column=5, padx=8, sticky="w")

        # Cards com Métricas Financeiras
        cards_frame = tk.Frame(container, bg="#F7FAFC", bd=1, relief=tk.SOLID, padx=10, pady=8)
        cards_frame.pack(fill=tk.X, pady=(0, 10))

        self.lbl_card_trans = tk.Label(cards_frame, text="Transações: 0", font=("Segoe UI", 9, "bold"), bg="#F7FAFC", fg="#2D3748")
        self.lbl_card_trans.pack(side=tk.LEFT, padx=12)

        self.lbl_card_bruto = tk.Label(cards_frame, text="Valor Bruto: R$ 0,00", font=("Segoe UI", 9, "bold"), bg="#F7FAFC", fg="#2C5282")
        self.lbl_card_bruto.pack(side=tk.LEFT, padx=12)

        self.lbl_card_tarifas = tk.Label(cards_frame, text="Tarifas: R$ 0,00", font=("Segoe UI", 9, "bold"), bg="#F7FAFC", fg="#C53030")
        self.lbl_card_tarifas.pack(side=tk.LEFT, padx=12)

        self.lbl_card_liq = tk.Label(cards_frame, text="Líquido: R$ 0,00", font=("Segoe UI", 9, "bold"), bg="#F7FAFC", fg="#2F855A")
        self.lbl_card_liq.pack(side=tk.LEFT, padx=12)

        self.lbl_card_inconsist = tk.Label(cards_frame, text="Inconsistências: 0", font=("Segoe UI", 9, "bold"), bg="#F7FAFC", fg="#7B341E")
        self.lbl_card_inconsist.pack(side=tk.RIGHT, padx=12)

        # PanedWindow para dividir Grid e Log de Erros
        paned = ttk.PanedWindow(container, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Grid Superior
        grid_frame = ttk.Frame(paned)
        paned.add(grid_frame, weight=3)

        colunas = ("id", "data", "cpf", "cliente", "bruto", "tarifa", "liq", "status", "apolo", "erros")
        self.tree = ttk.Treeview(grid_frame, columns=colunas, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID Pedido")
        self.tree.heading("data", text="Data")
        self.tree.heading("cpf", text="CPF / CNPJ")
        self.tree.heading("cliente", text="Nome do Doador")
        self.tree.heading("bruto", text="Bruto (R$)")
        self.tree.heading("tarifa", text="Tarifa (R$)")
        self.tree.heading("liq", text="Líquido (R$)")
        self.tree.heading("status", text="Status Vindi")
        self.tree.heading("apolo", text="Integ. Apolo?")
        self.tree.heading("erros", text="Inconsistências")

        self.tree.column("id", width=85, anchor="center")
        self.tree.column("data", width=80, anchor="center")
        self.tree.column("cpf", width=110, anchor="center")
        self.tree.column("cliente", width=220, anchor="w")
        self.tree.column("bruto", width=85, anchor="e")
        self.tree.column("tarifa", width=80, anchor="e")
        self.tree.column("liq", width=85, anchor="e")
        self.tree.column("status", width=85, anchor="center")
        self.tree.column("apolo", width=85, anchor="center")
        self.tree.column("erros", width=180, anchor="w")

        scroll_y = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self._ao_selecionar_transacao)

        # Painel Inferior de Detalhes e Inconsistências
        bottom_frame = ttk.LabelFrame(paned, text=" Detalhamento de Inconsistências da Transação Selecionada ", padding="8")
        paned.add(bottom_frame, weight=1)

        self.txt_log_erros = tk.Text(bottom_frame, height=4, font=("Consolas", 9), wrap=tk.WORD)
        self.txt_log_erros.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_txt = ttk.Scrollbar(bottom_frame, orient=tk.VERTICAL, command=self.txt_log_erros.yview)
        self.txt_log_erros.configure(yscrollcommand=scroll_txt.set)
        scroll_txt.pack(side=tk.RIGHT, fill=tk.Y)

        # Barra de Ação
        action_bar = ttk.Frame(container)
        action_bar.pack(fill=tk.X, pady=(10, 0))

        self.btn_integrar = tk.Button(
            action_bar,
            text="✔ Integrar Transação Selecionada",
            font=("Segoe UI", 9, "bold"),
            bg="#2F855A",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=14,
            pady=4,
            command=self._integrar_selecionada,
            state=tk.DISABLED,
            cursor="hand2",
        )
        self.btn_integrar.pack(side=tk.RIGHT, padx=5)

    def _executar_conciliacao(self):
        try:
            dt_ini = datetime.strptime(self.txt_dt_ini.get().strip(), "%Y-%m-%d").date()
            dt_fim = datetime.strptime(self.txt_dt_fim.get().strip(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Data Inválida", "Informe as datas no formato AAAA-MM-DD.")
            return

        for it in self.tree.get_children():
            self.tree.delete(it)
        self.txt_log_erros.delete("1.0", tk.END)
        self.btn_integrar.config(state=tk.DISABLED)

        try:
            apenas_nao_integ = self.var_nao_integ.get()
            transacoes, resumo = self.service.conciliar_periodo(dt_ini, dt_fim, apenas_nao_integ)
            self._transacoes_atuais = transacoes

            for t in transacoes:
                dt_str = t.data_transacao.strftime("%d/%m/%Y") if t.data_transacao else ""
                apolo_str = "SIM" if t.integrada_apolo else "NÃO"
                erros_resumo = f"{len(t.erros)} inconsistência(s)" if t.erros else "OK"

                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        t.pedido_id,
                        dt_str,
                        t.cpf_cnpj,
                        t.nome_cliente,
                        f"{t.valor_bruto:,.2f}",
                        f"{t.valor_tarifa:,.2f}",
                        f"{t.valor_liquido:,.2f}",
                        t.status_vindi,
                        apolo_str,
                        erros_resumo,
                    ),
                )

            # Atualizar métricas
            self.lbl_card_trans.config(text=f"Transações: {resumo.total_transacoes}")
            self.lbl_card_bruto.config(text=f"Valor Bruto: R$ {resumo.total_bruto:,.2f}")
            self.lbl_card_tarifas.config(text=f"Tarifas: R$ {resumo.total_tarifas:,.2f}")
            self.lbl_card_liq.config(text=f"Líquido: R$ {resumo.total_liquido:,.2f}")
            self.lbl_card_inconsist.config(
                text=f"Inconsistências: {resumo.total_com_inconsistencias}",
                fg="#C53030" if resumo.total_com_inconsistencias > 0 else "#2F855A",
            )
        except Exception as e:
            messagebox.showerror("Erro de Conciliação", f"Falha ao conciliar transações Vindi:\n{e}")

    def _ao_selecionar_transacao(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        if not vals:
            return

        pedido_id = str(vals[0])
        self.txt_log_erros.delete("1.0", tk.END)

        for t in self._transacoes_atuais:
            if t.pedido_id == pedido_id:
                if t.erros:
                    self.txt_log_erros.insert(tk.END, "Inconsistências encontradas:\n")
                    for err in t.erros:
                        self.txt_log_erros.insert(tk.END, f" • {err}\n")
                    self.btn_integrar.config(state=tk.DISABLED)
                else:
                    self.txt_log_erros.insert(tk.END, "✔ Nenhuma inconsistência identificada. Transação apta para integração.")
                    self.btn_integrar.config(state=tk.NORMAL if not t.integrada_apolo else tk.DISABLED)
                break

    def _integrar_selecionada(self):
        sel = self.tree.selection()
        if not sel:
            return
        pedido_id = str(self.tree.item(sel[0])["values"][0])

        if self.service.integrar_transacao(pedido_id):
            messagebox.showinfo("Sucesso", f"Transação '{pedido_id}' integrada com sucesso na base Apolo!")
            self._executar_conciliacao()
        else:
            messagebox.showerror("Erro", f"Não foi possível integrar a transação '{pedido_id}'.")
