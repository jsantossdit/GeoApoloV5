"""
Interface Gráfica para Conciliação de Transações Vindi.
GeoApolo V5
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from datetime import date, datetime
from PIL import Image, ImageTk

from core import obter_caminho_recurso, centralizar_janela
from .models import TransacaoVindiDTO, ResumoConciliacaoVindiDTO
from .repository import VindiRepository
from .service import VindiService


class ConciliacaoVindiView:
    """Janela corporativa para conciliação financeira de doações e assinaturas Vindi."""

    def __init__(self, parent: tk.Widget, service: Optional[VindiService] = None):
        self.parent = parent
        self.service = service or VindiService(VindiRepository())

        self.window = tk.Toplevel(parent)
        self.window.title("GeoAlvo - Conciliação Vindi Crédito Recorrente (RCC)")
        self.window.minsize(960, 600)
        self.window.transient(parent)
        self.window.grab_set()
        centralizar_janela(self.window, parent, 1100, 700)

        self._transacoes_atuais: List[TransacaoVindiDTO] = []
        self._icones_cache = []
        self._setup_ui()

    def _parse_data(self, texto: str) -> date:
        """Converte texto de data suportando formato DD/MM/AAAA e variações."""
        t = (texto or "").strip()
        if not t:
            raise ValueError("Data não informada.")
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%Y-%m-%d", "%Y/%m/%d"):
            try:
                return datetime.strptime(t, fmt).date()
            except ValueError:
                pass
        raise ValueError(f"Formato inválido: {t}")

    def _carregar_icone(self, nome_arquivo: str, tamanho=(20, 20)) -> Optional[ImageTk.PhotoImage]:
        """Carrega ícone da pasta Imagens com tratamento seguro e redimensionamento."""
        try:
            caminho_base = obter_caminho_recurso("Imagens")
            caminho_completo = os.path.join(caminho_base, nome_arquivo)
            if os.path.exists(caminho_completo):
                img = Image.open(caminho_completo).convert("RGBA")
                img = img.resize(tamanho, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img, master=self.window)
                self._icones_cache.append(photo)
                return photo
        except Exception as e:
            print(f"Aviso ao carregar ícone {nome_arquivo}: {e}")
        return None

    def _criar_tooltip(self, widget: tk.Widget, texto: str):
        """Associa uma tooltip descritiva a um componente visual."""
        def show_tooltip(event):
            if hasattr(widget, "tooltip_win") and widget.tooltip_win:
                try:
                    widget.tooltip_win.destroy()
                except Exception:
                    pass

            tip = tk.Toplevel()
            tip.wm_overrideredirect(True)
            tip.configure(bg="#FFFFE0", relief="solid", bd=1)

            lbl = tk.Label(
                tip,
                text=texto,
                bg="#FFFFE0",
                fg="#1A202C",
                font=("Segoe UI", 9),
                padx=6,
                pady=3,
            )
            lbl.pack()

            x = event.x_root + 10
            y = event.y_root + 18
            tip.geometry(f"+{x}+{y}")

            widget.tooltip_win = tip
            tip.after(3500, lambda: hide_tooltip(None))

        def hide_tooltip(event=None):
            if hasattr(widget, "tooltip_win") and widget.tooltip_win:
                try:
                    widget.tooltip_win.destroy()
                except Exception:
                    pass
                delattr(widget, "tooltip_win")

        widget.bind("<Enter>", show_tooltip, add="+")
        widget.bind("<Leave>", hide_tooltip, add="+")

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

        # Datas Padrão
        hoje = date.today().strftime("%d/%m/%Y")
        primeiro_dia = date(date.today().year, date.today().month, 1).strftime("%d/%m/%Y")

        ttk.Label(filtro_frame, text="Data Inicial:").grid(row=0, column=0, padx=4, sticky="w")
        self.txt_dt_ini = ttk.Entry(filtro_frame, width=12)
        self.txt_dt_ini.insert(0, primeiro_dia)
        self.txt_dt_ini.grid(row=0, column=1, padx=4, sticky="w")
        self.txt_dt_ini.bind("<Return>", lambda e: self.txt_dt_fim.focus_set())

        ttk.Label(filtro_frame, text="Data Final:").grid(row=0, column=2, padx=4, sticky="w")
        self.txt_dt_fim = ttk.Entry(filtro_frame, width=12)
        self.txt_dt_fim.insert(0, hoje)
        self.txt_dt_fim.grid(row=0, column=3, padx=4, sticky="w")
        self.txt_dt_fim.bind("<Return>", lambda e: self._executar_filtro())

        self.var_nao_integ = tk.BooleanVar(value=True)
        chk_integ = ttk.Checkbutton(
            filtro_frame,
            text="Somente não importadas para o Alvo",
            variable=self.var_nao_integ,
        )
        chk_integ.grid(row=0, column=4, padx=10, sticky="w")

        # Container para os botões de ação do filtro
        btn_box = tk.Frame(filtro_frame)
        btn_box.grid(row=0, column=5, padx=8, sticky="w")

        # 1. Botão Filtrar Registros (com ícone de lupa)
        icon_lupa = self._carregar_icone("lupa.png", (18, 18))
        self.btn_filtrar = tk.Button(
            btn_box,
            text=" Filtrar Registros",
            image=icon_lupa,
            compound=tk.LEFT,
            font=("Segoe UI", 9, "bold"),
            bg="#2B6CB0",
            fg="#FFFFFF",
            activebackground="#1E4E8C",
            activeforeground="#FFFFFF",
            relief=tk.RAISED,
            bd=1,
            padx=10,
            pady=4,
            command=self._executar_filtro,
            cursor="hand2",
        )
        self.btn_filtrar.pack(side=tk.LEFT, padx=3)
        self._criar_tooltip(self.btn_filtrar, "Filtrar registros por período")

        # 2. Botão Checar a Integridade (com ícone de integridade)
        icon_integ = self._carregar_icone("integridade.png", (18, 18))
        self.btn_integridade = tk.Button(
            btn_box,
            text=" Checar a Integridade",
            image=icon_integ,
            compound=tk.LEFT,
            font=("Segoe UI", 9, "bold"),
            bg="#1E3A8A",
            fg="#FFFFFF",
            activebackground="#172554",
            activeforeground="#FFFFFF",
            relief=tk.RAISED,
            bd=1,
            padx=10,
            pady=4,
            command=self._executar_checagem_integridade,
            cursor="hand2",
        )
        self.btn_integridade.pack(side=tk.LEFT, padx=3)
        self._criar_tooltip(self.btn_integridade, "Checa a Integridade dos registros")

        # 3. Botão Dashboard (futuros insights de IA)
        icon_dash = self._carregar_icone("dashboard.png", (18, 18))
        self.btn_dashboard = tk.Button(
            btn_box,
            text=" Dashboard",
            image=icon_dash,
            compound=tk.LEFT,
            font=("Segoe UI", 9, "bold"),
            bg="#4F46E5",
            fg="#FFFFFF",
            activebackground="#3730A3",
            activeforeground="#FFFFFF",
            relief=tk.RAISED,
            bd=1,
            padx=10,
            pady=4,
            command=self._abrir_dashboard,
            cursor="hand2",
        )
        self.btn_dashboard.pack(side=tk.LEFT, padx=3)
        self._criar_tooltip(self.btn_dashboard, "Abrir Dashboard e Insights de IA")

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

        self.lbl_card_inconsist = tk.Label(cards_frame, text="Inconsistências: Não checado", font=("Segoe UI", 9, "bold"), bg="#F7FAFC", fg="#7B341E")
        self.lbl_card_inconsist.pack(side=tk.RIGHT, padx=12)

        # PanedWindow para dividir Grid e Log de Erros
        paned = ttk.PanedWindow(container, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Grid Superior
        grid_frame = ttk.Frame(paned)
        paned.add(grid_frame, weight=3)

        colunas = ("id", "data", "cpf", "cliente", "bruto", "tarifa", "liq", "status", "alvo", "erros")
        self.tree = ttk.Treeview(grid_frame, columns=colunas, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID Pedido")
        self.tree.heading("data", text="Data")
        self.tree.heading("cpf", text="CPF / CNPJ")
        self.tree.heading("cliente", text="Nome do Doador")
        self.tree.heading("bruto", text="Bruto (R$)")
        self.tree.heading("tarifa", text="Tarifa (R$)")
        self.tree.heading("liq", text="Líquido (R$)")
        self.tree.heading("status", text="Status Vindi")
        self.tree.heading("alvo", text="Integ. Alvo?")
        self.tree.heading("erros", text="Inconsistências")

        self.tree.column("id", width=85, anchor="center")
        self.tree.column("data", width=80, anchor="center")
        self.tree.column("cpf", width=110, anchor="center")
        self.tree.column("cliente", width=220, anchor="w")
        self.tree.column("bruto", width=85, anchor="e")
        self.tree.column("tarifa", width=80, anchor="e")
        self.tree.column("liq", width=85, anchor="e")
        self.tree.column("status", width=85, anchor="center")
        self.tree.column("alvo", width=85, anchor="center")
        self.tree.column("erros", width=240, anchor="w")

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



    def _executar_filtro(self):
        """
        Executa o filtro de registros conforme datas inicial e final.
        Não executa a rotina de consistência.
        Valida preenchimento obrigatório e retorna o foco para data inicial se vazio/inválido.
        """
        txt_ini = self.txt_dt_ini.get().strip()
        if not txt_ini:
            messagebox.showerror("Atenção", "A Data Inicial é obrigatória. Informe a data inicial.", parent=self.window)
            self.txt_dt_ini.focus_set()
            return

        txt_fim = self.txt_dt_fim.get().strip()
        if not txt_fim:
            messagebox.showerror("Atenção", "A Data Final é obrigatória. Informe a data final.", parent=self.window)
            self.txt_dt_ini.focus_set()
            return

        try:
            dt_ini = self._parse_data(txt_ini)
        except ValueError:
            messagebox.showerror("Data Inválida", "Informe a Data Inicial no formato DD/MM/AAAA.", parent=self.window)
            self.txt_dt_ini.focus_set()
            return

        try:
            dt_fim = self._parse_data(txt_fim)
        except ValueError:
            messagebox.showerror("Data Inválida", "Informe a Data Final no formato DD/MM/AAAA.", parent=self.window)
            self.txt_dt_ini.focus_set()
            return

        if dt_ini > dt_fim:
            messagebox.showerror("Aviso", "A Data Inicial não pode ser superior à Data Final.", parent=self.window)
            self.txt_dt_ini.focus_set()
            return

        for it in self.tree.get_children():
            self.tree.delete(it)
        self.txt_log_erros.delete("1.0", tk.END)

        try:
            apenas_nao_integ = self.var_nao_integ.get()
            transacoes, resumo = self.service.filtrar_transacoes(dt_ini, dt_fim, apenas_nao_integ)
            self._transacoes_atuais = transacoes

            for t in transacoes:
                dt_str = t.data_transacao.strftime("%d/%m/%Y") if t.data_transacao else ""
                alvo_str = "SIM" if t.integrada_apolo else "NÃO"
                erros_resumo = "Não checado (Clique em 'Checar a Integridade')"

                self.tree.insert(
                    "",
                    tk.END,
                    iid=t.pedido_id,
                    values=(
                        t.pedido_id,
                        dt_str,
                        t.cpf_cnpj,
                        t.nome_cliente,
                        f"{t.valor_bruto:,.2f}",
                        f"{t.valor_tarifa:,.2f}",
                        f"{t.valor_liquido:,.2f}",
                        t.status_vindi,
                        alvo_str,
                        erros_resumo,
                    ),
                )

            # Atualizar métricas (inconsistências ainda não checadas)
            self.lbl_card_trans.config(text=f"Transações: {resumo.total_transacoes}")
            self.lbl_card_bruto.config(text=f"Valor Bruto: R$ {resumo.total_bruto:,.2f}")
            self.lbl_card_tarifas.config(text=f"Tarifas: R$ {resumo.total_tarifas:,.2f}")
            self.lbl_card_liq.config(text=f"Líquido: R$ {resumo.total_liquido:,.2f}")
            self.lbl_card_inconsist.config(
                text="Inconsistências: Não checado",
                fg="#7B341E",
            )
            self.txt_log_erros.insert(
                tk.END,
                f"Filtro aplicado com sucesso: {len(transacoes)} transação(ões) carregada(s).\n"
                f"Clique em 'Checar a Integridade' para auditar cadastros e consistência com a base Alvo."
            )
        except Exception as e:
            messagebox.showerror("Erro de Filtro", f"Falha ao carregar transações Vindi:\n{e}", parent=self.window)

    def _executar_checagem_integridade(self):
        """
        Executa a rotina de checagem de integridade dos registros carregados.
        Ao término, atualiza todas as linhas da coluna 'Inconsistências' no Treeview.
        """
        if not self._transacoes_atuais:
            messagebox.showwarning(
                "Atenção",
                "Nenhum registro carregado na lista para verificação.\nExecute o filtro de registros primeiro.",
                parent=self.window
            )
            return

        resumo = self.service.executar_checagem_integridade(self._transacoes_atuais)

        # Atualiza cada linha do grid na coluna Inconsistências
        for t in self._transacoes_atuais:
            if self.tree.exists(t.pedido_id):
                dt_str = t.data_transacao.strftime("%d/%m/%Y") if t.data_transacao else ""
                alvo_str = "SIM" if t.integrada_apolo else "NÃO"
                erros_resumo = f"{len(t.erros)} inconsistência(s)" if t.erros else "OK - Sem Inconsistências"

                self.tree.item(
                    t.pedido_id,
                    values=(
                        t.pedido_id,
                        dt_str,
                        t.cpf_cnpj,
                        t.nome_cliente,
                        f"{t.valor_bruto:,.2f}",
                        f"{t.valor_tarifa:,.2f}",
                        f"{t.valor_liquido:,.2f}",
                        t.status_vindi,
                        alvo_str,
                        erros_resumo,
                    ),
                )

        # Atualiza métricas
        self.lbl_card_inconsist.config(
            text=f"Inconsistências: {resumo.total_com_inconsistencias}",
            fg="#C53030" if resumo.total_com_inconsistencias > 0 else "#2F855A",
        )

        # Log geral de inconsistências
        self.txt_log_erros.delete("1.0", tk.END)
        self.txt_log_erros.insert(
            tk.END,
            f"=== CHECAGEM DE INTEGRIDADE CONCLUÍDA ===\n"
            f"Total de Registros Analisados: {len(self._transacoes_atuais)}\n"
            f"Registros com Inconsistências: {resumo.total_com_inconsistencias}\n"
            f"Registros Íntegros (Aptos): {len(self._transacoes_atuais) - resumo.total_com_inconsistencias}\n\n"
        )

        for t in self._transacoes_atuais:
            if t.erros:
                self.txt_log_erros.insert(tk.END, f"• Pedido [{t.pedido_id}] {t.nome_cliente} ({t.cpf_cnpj}):\n")
                for err in t.erros:
                    self.txt_log_erros.insert(tk.END, f"   - {err}\n")

        # Se houver seleção ativa, atualiza o detalhe específico
        self._ao_selecionar_transacao()

        messagebox.showinfo(
            "Checagem de Integridade",
            f"Checagem de integridade finalizada com sucesso!\n\n"
            f"• Registros auditados: {len(self._transacoes_atuais)}\n"
            f"• Com inconsistências: {resumo.total_com_inconsistencias}\n"
            f"• Sem inconsistências: {len(self._transacoes_atuais) - resumo.total_com_inconsistencias}",
            parent=self.window
        )

    def _abrir_dashboard(self):
        """Abre o formulário de Dashboard e Insights de IA para Doações Recorrentes."""
        try:
            from .dashboard_view import DashboardVindiView
            DashboardVindiView(self.window, self.service)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o Dashboard:\n{e}", parent=self.window)

    def _ao_selecionar_transacao(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        if not vals:
            return

        pedido_id = str(vals[0])
        for t in self._transacoes_atuais:
            if t.pedido_id == pedido_id:
                self.txt_log_erros.delete("1.0", tk.END)
                if t.erros:
                    self.txt_log_erros.insert(tk.END, f"Inconsistências identificadas no Pedido {pedido_id}:\n")
                    for err in t.erros:
                        self.txt_log_erros.insert(tk.END, f" • {err}\n")
                else:
                    self.txt_log_erros.insert(
                        tk.END,
                        f"✔ Nenhuma inconsistência no Pedido {pedido_id}. Registro íntegro e validado."
                    )
                break
