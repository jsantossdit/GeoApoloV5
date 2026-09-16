"""
Interface Gráfica (Tkinter / ttk) para a Central de Relatórios do GeoAlvo.
Layout profissional alinhado aos padrões visuais corporativos do sistema GeoAlvo.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import logging
from typing import List, Dict, Any

from relatorios.models import TipoRelatorio, FiltroRelatorio
from relatorios.service import RelatorioService
from relatorios.generator import RelatorioGenerator

logger = logging.getLogger(__name__)


class RelatoriosView(tk.Toplevel):
    """Janela da Central de Relatórios e Auditoria do GeoAlvo."""

    def __init__(self, parent=None, connection=None):
        super().__init__(parent)
        self.title("Central de Relatórios e Auditoria - GeoAlvo")
        self.geometry("1020x640")
        self.minsize(850, 520)

        # Centraliza a janela na tela
        self._centralizar_janela(1020, 640)

        # Configura ícone da janela
        self._aplicar_icone()

        self._service = RelatorioService(connection)
        self._dados_originais: List[Dict[str, Any]] = []
        self._dados_filtrados: List[Dict[str, Any]] = []

        self._configurar_estilos()
        self._criar_interface()
        self._carregar_dados_previa()

        # Atalhos de teclado
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<F5>", lambda e: self._carregar_dados_previa())

    def _centralizar_janela(self, largura: int, altura: int):
        self.update_idletasks()
        pos_x = (self.winfo_screenwidth() // 2) - (largura // 2)
        pos_y = (self.winfo_screenheight() // 2) - (altura // 2) - 20
        self.geometry(f"{largura}x{altura}+{max(pos_x, 0)}+{max(pos_y, 0)}")

    def _aplicar_icone(self):
        caminhos = [
            os.path.join(os.path.dirname(__file__), "..", "Imagens", "IconeRCC.png"),
            os.path.join(os.path.dirname(__file__), "..", "Imagens", "entidades.png"),
        ]
        for c in caminhos:
            if os.path.exists(c):
                try:
                    img = tk.PhotoImage(file=c)
                    self.iconphoto(False, img)
                    self._icon_ref = img
                    break
                except Exception:
                    pass

    def _configurar_estilos(self):
        style = ttk.Style()
        # Treeview profissional
        style.configure(
            "Relatorio.Treeview",
            font=("Segoe UI", 9),
            rowheight=26,
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
        )
        style.configure(
            "Relatorio.Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            foreground="#1A365D",
            padding=5,
        )

    def _criar_interface(self):
        # 1. Header Banner Corporativo (Azul Marinho GeoAlvo)
        banner_frame = tk.Frame(self, bg="#1A365D", height=58)
        banner_frame.pack(side=tk.TOP, fill=tk.X)
        banner_frame.pack_propagate(False)

        lbl_titulo = tk.Label(
            banner_frame,
            text="📊 Central de Relatórios e Auditoria",
            font=("Segoe UI", 12, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
            anchor="w",
        )
        lbl_titulo.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(8, 0))

        lbl_subtitulo = tk.Label(
            banner_frame,
            text="Visualização prévia, auditoria de dados e exportação profissional para Excel, PDF e CSV",
            font=("Segoe UI", 8),
            bg="#1A365D",
            fg="#CBD5E0",
            anchor="w",
        )
        lbl_subtitulo.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(1, 6))

        # 2. Painel de Filtros e Seleção
        filtro_container = ttk.LabelFrame(self, text="Seleção e Filtros de Pesquisa", padding=10)
        filtro_container.pack(side=tk.TOP, fill=tk.X, padx=12, pady=(10, 5))

        f_row = ttk.Frame(filtro_container)
        f_row.pack(fill=tk.X)

        ttk.Label(f_row, text="Tipo de Relatório:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self.combo_tipo = ttk.Combobox(
            f_row,
            values=[t.value for t in TipoRelatorio],
            state="readonly",
            width=36,
            font=("Segoe UI", 9),
        )
        self.combo_tipo.set(TipoRelatorio.ENTIDADES_GERAL.value)
        self.combo_tipo.pack(side=tk.LEFT, padx=(0, 15))
        self.combo_tipo.bind("<<ComboboxSelected>>", lambda e: self._carregar_dados_previa())

        ttk.Label(f_row, text="Filtrar Resultados:").pack(side=tk.LEFT, padx=(5, 4))
        self.entry_filtro = ttk.Entry(f_row, width=24, font=("Segoe UI", 9))
        self.entry_filtro.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_filtro.bind("<KeyRelease>", lambda e: self._aplicar_filtro_local())

        btn_atualizar = ttk.Button(
            f_row, text="🔄 Atualizar (F5)", command=self._carregar_dados_previa
        )
        btn_atualizar.pack(side=tk.LEFT, padx=4)

        # 3. Painel Central: Grid de Visualização Prévia
        preview_frame = ttk.LabelFrame(self, text="Pré-visualização dos Registros", padding=8)
        preview_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=12, pady=5)

        tree_scroll_y = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(
            preview_frame,
            style="Relatorio.Treeview",
            show="headings",
            selectmode="browse",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
        )
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Configuração de cores alternadas
        self.tree.tag_configure("par", background="#FFFFFF")
        self.tree.tag_configure("impar", background="#F7FAFC")

        # 4. Painel Inferior: Ações de Exportação e Barra de Status
        bottom_frame = tk.Frame(self, bg="#E2E8F0", height=46, bd=1, relief=tk.GROOVE)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        bottom_frame.pack_propagate(False)

        # Botões de Exportação
        btn_box = tk.Frame(bottom_frame, bg="#E2E8F0")
        btn_box.pack(side=tk.LEFT, padx=10, pady=7)

        self.btn_excel = ttk.Button(
            btn_box, text="📊 Exportar Excel (.xlsx)", command=self._exportar_excel
        )
        self.btn_excel.pack(side=tk.LEFT, padx=4)

        self.btn_html = ttk.Button(
            btn_box, text="🖨 Visualizar / Imprimir (PDF)", command=self._exportar_html
        )
        self.btn_html.pack(side=tk.LEFT, padx=4)

        self.btn_csv = ttk.Button(
            btn_box, text="📄 Exportar CSV", command=self._exportar_csv
        )
        self.btn_csv.pack(side=tk.LEFT, padx=4)

        # Botão Fechar no canto direito
        btn_fechar = ttk.Button(bottom_frame, text="🚪 Fechar (Esc)", command=self.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=12, pady=7)

        # Status
        self.lbl_status = tk.Label(
            bottom_frame,
            text="0 registros carregados.",
            font=("Segoe UI", 9, "italic"),
            bg="#E2E8F0",
            fg="#4A5568",
        )
        self.lbl_status.pack(side=tk.RIGHT, padx=16)

    def _obter_tipo_selecionado(self) -> TipoRelatorio:
        val = self.combo_tipo.get()
        for t in TipoRelatorio:
            if t.value == val:
                return t
        return TipoRelatorio.ENTIDADES_GERAL

    def _carregar_dados_previa(self):
        tipo = self._obter_tipo_selecionado()
        filtro = FiltroRelatorio(tipo_relatorio=tipo)

        try:
            self._dados_originais = self._service.obter_dados_relatorio(filtro)
            self._dados_filtrados = list(self._dados_originais)
            self._renderizar_tabela()
        except Exception as exc:
            logger.exception("Erro ao gerar prévia de relatório: %s", exc)
            messagebox.showerror("Erro de Relatório", f"Erro ao consultar dados:\n{exc}")

    def _aplicar_filtro_local(self):
        termo = self.entry_filtro.get().strip().lower()
        if not termo:
            self._dados_filtrados = list(self._dados_originais)
        else:
            self._dados_filtrados = [
                reg
                for reg in self._dados_originais
                if any(termo in str(v).lower() for v in reg.values())
            ]
        self._renderizar_tabela()

    def _renderizar_tabela(self):
        # Limpa itens existentes
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self._dados_filtrados:
            self.lbl_status.config(
                text=f"Nenhum registro encontrado (Total base: {len(self._dados_originais)})."
            )
            return

        colunas = list(self._dados_filtrados[0].keys())
        self.tree["columns"] = colunas

        for col in colunas:
            self.tree.heading(col, text=col, anchor=tk.W)
            # Calcula largura baseada no nome da coluna
            largura = max(len(col) * 11, 100)
            self.tree.column(col, width=min(largura, 280), anchor=tk.W)

        for idx, reg in enumerate(self._dados_filtrados[:250]):
            valores = [reg.get(c, "") for c in colunas]
            tag = "par" if idx % 2 == 0 else "impar"
            self.tree.insert("", tk.END, values=valores, tags=(tag,))

        total_filtrados = len(self._dados_filtrados)
        total_orig = len(self._dados_originais)
        if total_filtrados == total_orig:
            self.lbl_status.config(text=f"Total: {total_orig} registro(s) carregado(s).")
        else:
            self.lbl_status.config(
                text=f"Exibindo: {total_filtrados} de {total_orig} registros."
            )

    def _exportar_excel(self):
        dados_para_exportar = self._dados_filtrados if self._dados_filtrados else self._dados_originais
        if not dados_para_exportar:
            messagebox.showwarning("Atenção", "Nenhum dado disponível para exportação.")
            return

        caminho = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Planilha Excel", "*.xlsx")],
            title="Salvar Relatório em Excel",
            initialfile=f"Relatorio_{self._obter_tipo_selecionado().name}.xlsx",
        )
        if not caminho:
            return

        try:
            RelatorioGenerator.gerar_excel(dados_para_exportar, self.combo_tipo.get(), caminho)
            messagebox.showinfo("Sucesso", f"Relatório Excel exportado com sucesso em:\n{caminho}")
        except Exception as exc:
            messagebox.showerror("Erro ao Exportar", f"Falha ao gerar planilha Excel:\n{exc}")

    def _exportar_html(self):
        dados_para_exportar = self._dados_filtrados if self._dados_filtrados else self._dados_originais
        if not dados_para_exportar:
            messagebox.showwarning("Atenção", "Nenhum dado disponível para impressão.")
            return

        try:
            caminho = RelatorioGenerator.gerar_html_imprimivel(
                dados_para_exportar, self.combo_tipo.get()
            )
            logger.info("Relatório HTML aberto no navegador: %s", caminho)
        except Exception as exc:
            messagebox.showerror(
                "Erro ao Gerar Impressão", f"Falha ao abrir relatório para impressão:\n{exc}"
            )

    def _exportar_csv(self):
        dados_para_exportar = self._dados_filtrados if self._dados_filtrados else self._dados_originais
        if not dados_para_exportar:
            messagebox.showwarning("Atenção", "Nenhum dado disponível para exportação.")
            return

        caminho = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Arquivo CSV", "*.csv")],
            title="Salvar Relatório em CSV",
            initialfile=f"Relatorio_{self._obter_tipo_selecionado().name}.csv",
        )
        if not caminho:
            return

        try:
            RelatorioGenerator.gerar_csv(dados_para_exportar, caminho)
            messagebox.showinfo("Sucesso", f"Relatório CSV exportado com sucesso em:\n{caminho}")
        except Exception as exc:
            messagebox.showerror("Erro ao Exportar", f"Falha ao gerar arquivo CSV:\n{exc}")
