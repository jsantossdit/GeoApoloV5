"""
Interface Gráfica para Auditoria de Cupons Fiscais (NFC-e / PDV).
GeoApolo V5
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List
from datetime import date, datetime
from .models import AuditoriaCupomDTO
from .repository import FiscalRepository
from .service import FiscalService


class AuditoriaCuponsView:
    """Janela corporativa para auditoria de NFC-e e conciliação Caixa x Apolo."""

    def __init__(self, parent: tk.Tk, service: Optional[FiscalService] = None):
        self.parent = parent
        self.service = service or FiscalService(FiscalRepository())

        self.window = tk.Toplevel(parent)
        self.window.title("GeoAlvo - Auditoria de Cupons Fiscais (NFC-e)")
        self.window.geometry("1020x660")
        self.window.minsize(880, 560)
        self.window.transient(parent)
        self.window.grab_set()

        self._cupons_atuais: List[AuditoriaCupomDTO] = []
        self._setup_ui()

    def _setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg="#1A365D", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        lbl_titulo = tk.Label(
            header,
            text="Auditoria e Conciliação de Cupons Fiscais (NFC-e Caixa x Retaguarda)",
            font=("Segoe UI", 13, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
        )
        lbl_titulo.pack(side=tk.LEFT, padx=15, pady=12)

        # Container Principal
        container = ttk.Frame(self.window, padding="15")
        container.pack(fill=tk.BOTH, expand=True)

        # Painel de Parâmetros
        param_frame = ttk.LabelFrame(container, text=" Configuração da Auditoria ", padding="10")
        param_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(param_frame, text="Base SQLite do Caixa:").grid(row=0, column=0, padx=5, sticky="w")
        self.txt_caminho_sqlite = ttk.Entry(param_frame, width=50)
        self.txt_caminho_sqlite.grid(row=0, column=1, padx=5, sticky="we")

        btn_procurar = ttk.Button(param_frame, text="📂 Procurar...", command=self._selecionar_sqlite)
        btn_procurar.grid(row=0, column=2, padx=5, sticky="w")

        # Linha 2 de datas
        hoje = date.today().strftime("%Y-%m-%d")
        ttk.Label(param_frame, text="Data Inicial:").grid(row=1, column=0, padx=5, pady=(8, 0), sticky="w")
        self.txt_dt_ini = ttk.Entry(param_frame, width=12)
        self.txt_dt_ini.insert(0, hoje)
        self.txt_dt_ini.grid(row=1, column=1, padx=5, pady=(8, 0), sticky="w")

        ttk.Label(param_frame, text="Data Final:").grid(row=1, column=1, padx=(140, 5), pady=(8, 0), sticky="w")
        self.txt_dt_fim = ttk.Entry(param_frame, width=12)
        self.txt_dt_fim.insert(0, hoje)
        self.txt_dt_fim.grid(row=1, column=1, padx=(220, 5), pady=(8, 0), sticky="w")

        btn_auditar = tk.Button(
            param_frame,
            text="⚡ Executar Auditoria",
            font=("Segoe UI", 9, "bold"),
            bg="#2B6CB0",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=14,
            pady=4,
            command=self._executar_auditoria,
            cursor="hand2",
        )
        btn_auditar.grid(row=1, column=2, padx=5, pady=(8, 0), sticky="w")

        param_frame.columnconfigure(1, weight=1)

        # Grid Treeview
        grid_frame = ttk.Frame(container)
        grid_frame.pack(fill=tk.BOTH, expand=True)

        colunas = ("nf", "serie", "cliente", "valor", "sefaz", "alvo", "fin", "fisc", "estq")
        self.tree = ttk.Treeview(grid_frame, columns=colunas, show="headings")

        self.tree.heading("nf", text="NFC-e Nº")
        self.tree.heading("serie", text="Série")
        self.tree.heading("cliente", text="Cliente / Destinatário")
        self.tree.heading("valor", text="Valor Total (R$)")
        self.tree.heading("sefaz", text="Status SEFAZ")
        self.tree.heading("alvo", text="Integ. Alvo?")
        self.tree.heading("fin", text="Financeiro?")
        self.tree.heading("fisc", text="Fiscal?")
        self.tree.heading("estq", text="Baixou Estoque?")

        self.tree.column("nf", width=90, anchor="center")
        self.tree.column("serie", width=60, anchor="center")
        self.tree.column("cliente", width=250, anchor="w")
        self.tree.column("valor", width=105, anchor="e")
        self.tree.column("sefaz", width=120, anchor="center")
        self.tree.column("alvo", width=90, anchor="center")
        self.tree.column("fin", width=90, anchor="center")
        self.tree.column("fisc", width=90, anchor="center")
        self.tree.column("estq", width=110, anchor="center")

        scroll_y = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Rodapé de Totais
        totais_frame = tk.Frame(container, bg="#EDF2F7", bd=1, relief=tk.SOLID, padx=12, pady=10)
        totais_frame.pack(fill=tk.X, pady=(10, 0))

        self.lbl_tot = tk.Label(totais_frame, text="Total Cupons: 0", font=("Segoe UI", 9, "bold"), bg="#EDF2F7", fg="#2D3748")
        self.lbl_tot.pack(side=tk.LEFT, padx=10)

        self.lbl_sefaz = tk.Label(totais_frame, text="Transmitidos: 0", font=("Segoe UI", 9, "bold"), bg="#EDF2F7", fg="#2F855A")
        self.lbl_sefaz.pack(side=tk.LEFT, padx=10)

        self.lbl_integ = tk.Label(totais_frame, text="Integrados Alvo: 0", font=("Segoe UI", 9, "bold"), bg="#EDF2F7", fg="#2B6CB0")
        self.lbl_integ.pack(side=tk.LEFT, padx=10)

        self.lbl_pend = tk.Label(totais_frame, text="Pendências: 0", font=("Segoe UI", 9, "bold"), bg="#EDF2F7", fg="#C53030")
        self.lbl_pend.pack(side=tk.LEFT, padx=10)

        self.btn_sinc = tk.Button(
            totais_frame,
            text="🔄 Sincronizar Flags com Apolo",
            font=("Segoe UI", 9, "bold"),
            bg="#2F855A",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=14,
            pady=4,
            command=self._sincronizar_flags,
            state=tk.DISABLED,
            cursor="hand2",
        )
        self.btn_sinc.pack(side=tk.RIGHT, padx=5)

    def _selecionar_sqlite(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar Base SQLite do Caixa",
            filetypes=[
                ("Bancos SQLite", "*.db;*.sqlite;*.sqlite3"),
                ("Todos os arquivos", "*.*"),
            ],
        )
        if caminho:
            self.txt_caminho_sqlite.delete(0, tk.END)
            self.txt_caminho_sqlite.insert(0, caminho)
            self.service._repo.caminho_sqlite = caminho

    def _executar_auditoria(self):
        caminho = self.txt_caminho_sqlite.get().strip()
        if not caminho:
            messagebox.showwarning("Aviso", "Selecione o arquivo da base SQLite do caixa.")
            return
        self.service._repo.caminho_sqlite = caminho

        try:
            dt_ini = datetime.strptime(self.txt_dt_ini.get().strip(), "%Y-%m-%d").date()
            dt_fim = datetime.strptime(self.txt_dt_fim.get().strip(), "%Y-%m-%d").date()
        except ValueError:
            messagebox.showwarning("Data Inválida", "Informe as datas no formato AAAA-MM-DD.")
            return

        for it in self.tree.get_children():
            self.tree.delete(it)

        try:
            cupons, resumo = self.service.executar_auditoria(dt_ini, dt_fim)
            self._cupons_atuais = cupons

            for c in cupons:
                val_str = f"{c.valor_total:,.2f}"
                alvo_str = "SIM" if c.integrado_alvo else "NÃO"
                fin_str = "SIM" if c.integrado_financ else "NÃO"
                fisc_str = "SIM" if c.integrado_fiscal else "NÃO"
                estq_str = "SIM" if c.baixou_estoque else "NÃO"

                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        c.numero,
                        c.serie,
                        c.entidade_nome,
                        val_str,
                        c.status_sefaz,
                        alvo_str,
                        fin_str,
                        fisc_str,
                        estq_str,
                    ),
                )

            self.lbl_tot.config(text=f"Total Cupons: {resumo.total_cupons}")
            self.lbl_sefaz.config(text=f"Transmitidos: {resumo.total_transmitidos}")
            self.lbl_integ.config(text=f"Integrados Alvo: {resumo.total_integrados}")
            self.lbl_pend.config(text=f"Pendências: {resumo.total_pendentes}")

            self.btn_sinc.config(state=tk.NORMAL if cupons else tk.DISABLED)
            messagebox.showinfo("Auditoria Concluída", f"Foram auditados {resumo.total_cupons} cupons fiscais.")
        except Exception as e:
            messagebox.showerror("Erro de Auditoria", f"Falha ao executar auditoria:\n{e}")

    def _sincronizar_flags(self):
        if not self._cupons_atuais:
            return

        if not messagebox.askyesno(
            "Confirmação",
            "Deseja checar a retaguarda Apolo e atualizar as flags de integração na base do PDV?",
        ):
            return

        res = self.service.sincronizar_flags_com_apolo(self._cupons_atuais)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self._executar_auditoria()
        else:
            messagebox.showerror("Erro", res.mensagem)
