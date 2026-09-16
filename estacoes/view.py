"""
Interface Gráfica (Tkinter / ttk) para Gestão de Estações de Trabalho e Inventário de TI.
Layout corporativo profissional no padrão GeoAlvo.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import logging
from typing import Optional, List, Dict, Any

from estacoes.models import EstacaoFiltro, ResultadoOperacao
from estacoes.repository import EstacoesRepository
from estacoes.service import EstacoesService
from entidades.database import obter_conexao_banco
from relatorios.generator import RelatorioGenerator

logger = logging.getLogger(__name__)


class EstacoesView(tk.Toplevel):
    """Janela principal de Gestão de Estações de Trabalho do GeoAlvo."""

    def __init__(self, parent=None, connection=None):
        super().__init__(parent)
        self.title("Gestão de Estações de Trabalho e Inventário de TI - GeoAlvo")
        self.geometry("1180x700")
        self.minsize(980, 580)

        self._centralizar_janela(1180, 700)
        self._aplicar_icone()

        self._conn = connection
        if self._conn is None:
            try:
                self._conn = obter_conexao_banco()
            except Exception as exc:
                messagebox.showwarning(
                    "Aviso de Conexão",
                    f"Não foi possível conectar automaticamente ao banco:\n{exc}\n\nConfigure o banco de dados no menu Configurações."
                )

        self._repo = EstacoesRepository(self._conn) if self._conn else None
        self._service = EstacoesService(self._repo) if self._repo else None

        self._estacoes_atuais: List[Dict[str, Any]] = []
        self._estacao_selecionada: Optional[Dict[str, Any]] = None

        self._configurar_estilos()
        self._criar_interface()
        self._carregar_estacoes()

        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<F5>", lambda e: self._carregar_estacoes())

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
        style.configure(
            "Estacoes.Treeview",
            font=("Segoe UI", 9),
            rowheight=26,
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
        )
        style.configure(
            "Estacoes.Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            foreground="#1A365D",
            padding=5,
        )

    def _criar_interface(self):
        # 1. Header Banner Corporativo
        banner = tk.Frame(self, bg="#1A365D", height=58)
        banner.pack(side=tk.TOP, fill=tk.X)
        banner.pack_propagate(False)

        lbl_tit = tk.Label(
            banner,
            text="🖥 Gestão de Estações de Trabalho e Inventário de TI",
            font=("Segoe UI", 12, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
            anchor="w",
        )
        lbl_tit.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(8, 0))

        lbl_sub = tk.Label(
            banner,
            text="Inventário de hardware, softwares instalados, licenças, service tags e localização física",
            font=("Segoe UI", 8),
            bg="#1A365D",
            fg="#CBD5E0",
            anchor="w",
        )
        lbl_sub.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(1, 6))

        # 2. Barra Superior de Filtros
        filtro_box = ttk.LabelFrame(self, text="Pesquisa e Filtros Rápidos", padding=8)
        filtro_box.pack(side=tk.TOP, fill=tk.X, padx=12, pady=(8, 4))

        f_row = ttk.Frame(filtro_box)
        f_row.pack(fill=tk.X)

        ttk.Label(f_row, text="Buscar por:").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_campo_busca = ttk.Combobox(
            f_row,
            values=["descricao", "codigo_estacao", "tag_servico"],
            state="readonly",
            width=15,
            font=("Segoe UI", 9),
        )
        self.combo_campo_busca.set("descricao")
        self.combo_campo_busca.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(f_row, text="Termo:").pack(side=tk.LEFT, padx=(0, 4))
        self.entry_busca = ttk.Entry(f_row, width=28, font=("Segoe UI", 9))
        self.entry_busca.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_busca.bind("<Return>", lambda e: self._carregar_estacoes())

        btn_buscar = ttk.Button(f_row, text="🔍 Buscar", command=self._carregar_estacoes)
        btn_buscar.pack(side=tk.LEFT, padx=3)

        btn_limpar = ttk.Button(f_row, text="✖ Limpar", command=self._limpar_filtro)
        btn_limpar.pack(side=tk.LEFT, padx=3)

        btn_atualizar = ttk.Button(f_row, text="🔄 Atualizar (F5)", command=self._carregar_estacoes)
        btn_atualizar.pack(side=tk.LEFT, padx=8)

        # 3. Painel Principal: Notebook de Abas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=12, pady=5)

        # Aba 1: Lista de Estações
        self.tab_lista = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(self.tab_lista, text="🖥 Estações de Trabalho")
        self._criar_aba_lista()

        # Aba 2: Detalhes e Edição
        self.tab_detalhes = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.tab_detalhes, text="📝 Detalhes / Edição")
        self._criar_aba_detalhes()

        # Aba 3: Hardware
        self.tab_hardware = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(self.tab_hardware, text="🔧 Hardware Vinculado")
        self._criar_aba_hardware()

        # Aba 4: Software
        self.tab_software = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(self.tab_software, text="💾 Software & Licenças")
        self._criar_aba_software()

        # Aba 5: Usuários
        self.tab_usuarios = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(self.tab_usuarios, text="👤 Usuários Vinculados")
        self._criar_aba_usuarios()

        # 4. Rodapé e Status
        bottom_frame = tk.Frame(self, bg="#E2E8F0", height=46, bd=1, relief=tk.GROOVE)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        bottom_frame.pack_propagate(False)

        btn_box = tk.Frame(bottom_frame, bg="#E2E8F0")
        btn_box.pack(side=tk.LEFT, padx=10, pady=7)

        ttk.Button(btn_box, text="📊 Exportar Excel", command=self._exportar_excel).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_box, text="🖨 Imprimir / PDF", command=self._exportar_html).pack(side=tk.LEFT, padx=4)

        btn_fechar = ttk.Button(bottom_frame, text="🚪 Fechar (Esc)", command=self.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=12, pady=7)

        self.lbl_status = tk.Label(
            bottom_frame,
            text="0 estações listadas.",
            font=("Segoe UI", 9, "italic"),
            bg="#E2E8F0",
            fg="#4A5568",
        )
        self.lbl_status.pack(side=tk.RIGHT, padx=16)

    def _criar_aba_lista(self):
        colunas = ("cod", "desc", "dep", "servicetag", "ip", "modelo", "resp", "datacad")
        scroll_y = ttk.Scrollbar(self.tab_lista, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(self.tab_lista, orient=tk.HORIZONTAL)

        self.tree_estacoes = ttk.Treeview(
            self.tab_lista,
            columns=colunas,
            show="headings",
            selectmode="browse",
            style="Estacoes.Treeview",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
        )
        scroll_y.config(command=self.tree_estacoes.yview)
        scroll_x.config(command=self.tree_estacoes.xview)

        self.tree_estacoes.heading("cod", text="Código")
        self.tree_estacoes.heading("desc", text="Descrição da Estação")
        self.tree_estacoes.heading("dep", text="Departamento")
        self.tree_estacoes.heading("servicetag", text="Service Tag")
        self.tree_estacoes.heading("ip", text="Endereço IP")
        self.tree_estacoes.heading("modelo", text="Modelo")
        self.tree_estacoes.heading("resp", text="Responsável")
        self.tree_estacoes.heading("datacad", text="Data Cadastro")

        self.tree_estacoes.column("cod", width=80, anchor=tk.CENTER)
        self.tree_estacoes.column("desc", width=230, anchor=tk.W)
        self.tree_estacoes.column("dep", width=160, anchor=tk.W)
        self.tree_estacoes.column("servicetag", width=120, anchor=tk.CENTER)
        self.tree_estacoes.column("ip", width=120, anchor=tk.CENTER)
        self.tree_estacoes.column("modelo", width=130, anchor=tk.W)
        self.tree_estacoes.column("resp", width=150, anchor=tk.W)
        self.tree_estacoes.column("datacad", width=100, anchor=tk.CENTER)

        self.tree_estacoes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree_estacoes.tag_configure("par", background="#FFFFFF")
        self.tree_estacoes.tag_configure("impar", background="#F7FAFC")

        self.tree_estacoes.bind("<Double-1>", self._on_double_click_estacao)

    def _criar_aba_detalhes(self):
        form_frame = ttk.Frame(self.tab_detalhes)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Linha 1: Código e Descrição
        r1 = ttk.Frame(form_frame)
        r1.pack(fill=tk.X, pady=6)

        ttk.Label(r1, text="Código Estação:", width=16).pack(side=tk.LEFT)
        self.edt_codigo = ttk.Entry(r1, width=14, font=("Segoe UI", 9))
        self.edt_codigo.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(r1, text="Descrição:", width=10).pack(side=tk.LEFT)
        self.edt_descricao = ttk.Entry(r1, width=45, font=("Segoe UI", 9))
        self.edt_descricao.pack(side=tk.LEFT, padx=(0, 20), fill=tk.X, expand=True)

        # Linha 2: Departamento e Localização
        r2 = ttk.Frame(form_frame)
        r2.pack(fill=tk.X, pady=6)

        ttk.Label(r2, text="Departamento:", width=16).pack(side=tk.LEFT)
        self.edt_departamento = ttk.Entry(r2, width=28, font=("Segoe UI", 9))
        self.edt_departamento.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(r2, text="Localização:", width=10).pack(side=tk.LEFT)
        self.edt_localizacao = ttk.Entry(r2, width=30, font=("Segoe UI", 9))
        self.edt_localizacao.pack(side=tk.LEFT, padx=(0, 20), fill=tk.X, expand=True)

        # Linha 3: Service Tag, Modelo e IP
        r3 = ttk.Frame(form_frame)
        r3.pack(fill=tk.X, pady=6)

        ttk.Label(r3, text="Service Tag:", width=16).pack(side=tk.LEFT)
        self.edt_servicetag = ttk.Entry(r3, width=20, font=("Segoe UI", 9))
        self.edt_servicetag.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(r3, text="Modelo:", width=8).pack(side=tk.LEFT)
        self.edt_modelo = ttk.Entry(r3, width=22, font=("Segoe UI", 9))
        self.edt_modelo.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(r3, text="Endereço IP:").pack(side=tk.LEFT, padx=(0, 4))
        self.edt_ip = ttk.Entry(r3, width=18, font=("Segoe UI", 9))
        self.edt_ip.pack(side=tk.LEFT)

        # Linha 4: Responsável
        r4 = ttk.Frame(form_frame)
        r4.pack(fill=tk.X, pady=6)

        ttk.Label(r4, text="Usuário Responsável:", width=16).pack(side=tk.LEFT)
        self.edt_responsavel = ttk.Entry(r4, width=40, font=("Segoe UI", 9))
        self.edt_responsavel.pack(side=tk.LEFT, padx=(0, 20))

        # Linha 5: Observações
        r5 = ttk.Frame(form_frame)
        r5.pack(fill=tk.BOTH, expand=True, pady=6)

        ttk.Label(r5, text="Observações:", width=16).pack(side=tk.LEFT, anchor=tk.N)
        self.txt_observacoes = tk.Text(r5, height=5, font=("Segoe UI", 9))
        self.txt_observacoes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Barra de Botões do Formulário
        b_bar = ttk.Frame(self.tab_detalhes)
        b_bar.pack(fill=tk.X, pady=10)

        ttk.Button(b_bar, text="➕ Nova Estação", command=self._limpar_formulario).pack(side=tk.LEFT, padx=4)
        ttk.Button(b_bar, text="💾 Salvar Estação", command=self._salvar_estacao).pack(side=tk.LEFT, padx=4)
        ttk.Button(b_bar, text="🗑 Excluir Estação", command=self._excluir_estacao).pack(side=tk.LEFT, padx=4)

    def _criar_aba_hardware(self):
        colunas = ("cod", "desc", "valor", "nf", "compra", "garantia", "status", "ip", "rack")
        self.tree_hardware = ttk.Treeview(
            self.tab_hardware,
            columns=colunas,
            show="headings",
            selectmode="browse",
            style="Estacoes.Treeview",
        )
        self.tree_hardware.heading("cod", text="Cód.")
        self.tree_hardware.heading("desc", text="Descrição do Hardware")
        self.tree_hardware.heading("valor", text="Valor (R$)")
        self.tree_hardware.heading("nf", text="Nota Fiscal")
        self.tree_hardware.heading("compra", text="Data Compra")
        self.tree_hardware.heading("garantia", text="Garantia (Dias)")
        self.tree_hardware.heading("status", text="Status")
        self.tree_hardware.heading("ip", text="IP")
        self.tree_hardware.heading("rack", text="Rack")

        self.tree_hardware.column("cod", width=60, anchor=tk.CENTER)
        self.tree_hardware.column("desc", width=220, anchor=tk.W)
        self.tree_hardware.column("valor", width=90, anchor=tk.E)
        self.tree_hardware.column("nf", width=100, anchor=tk.CENTER)
        self.tree_hardware.column("compra", width=95, anchor=tk.CENTER)
        self.tree_hardware.column("garantia", width=100, anchor=tk.CENTER)
        self.tree_hardware.column("status", width=85, anchor=tk.CENTER)
        self.tree_hardware.column("ip", width=110, anchor=tk.CENTER)
        self.tree_hardware.column("rack", width=90, anchor=tk.CENTER)

        self.tree_hardware.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        h_bar = ttk.Frame(self.tab_hardware)
        h_bar.pack(fill=tk.X)
        ttk.Button(h_bar, text="➕ Adicionar Hardware", command=self._adicionar_hardware).pack(side=tk.LEFT, padx=4)
        ttk.Button(h_bar, text="🗑 Excluir Hardware", command=self._excluir_hardware).pack(side=tk.LEFT, padx=4)

    def _criar_aba_software(self):
        colunas = ("cod", "desc", "nf", "valor", "licenca", "vencimento")
        self.tree_software = ttk.Treeview(
            self.tab_software,
            columns=colunas,
            show="headings",
            selectmode="browse",
            style="Estacoes.Treeview",
        )
        self.tree_software.heading("cod", text="Cód.")
        self.tree_software.heading("desc", text="Software")
        self.tree_software.heading("nf", text="Nota Fiscal")
        self.tree_software.heading("valor", text="Valor (R$)")
        self.tree_software.heading("licenca", text="Tipo Licença")
        self.tree_software.heading("vencimento", text="Vencimento")

        self.tree_software.column("cod", width=70, anchor=tk.CENTER)
        self.tree_software.column("desc", width=260, anchor=tk.W)
        self.tree_software.column("nf", width=110, anchor=tk.CENTER)
        self.tree_software.column("valor", width=95, anchor=tk.E)
        self.tree_software.column("licenca", width=150, anchor=tk.W)
        self.tree_software.column("vencimento", width=110, anchor=tk.CENTER)

        self.tree_software.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        s_bar = ttk.Frame(self.tab_software)
        s_bar.pack(fill=tk.X)
        ttk.Button(s_bar, text="➕ Adicionar Software", command=self._adicionar_software).pack(side=tk.LEFT, padx=4)
        ttk.Button(s_bar, text="🗑 Excluir Software", command=self._excluir_software).pack(side=tk.LEFT, padx=4)

    def _criar_aba_usuarios(self):
        colunas = ("cod", "nome", "data", "responsavel")
        self.tree_usuarios = ttk.Treeview(
            self.tab_usuarios,
            columns=colunas,
            show="headings",
            selectmode="browse",
            style="Estacoes.Treeview",
        )
        self.tree_usuarios.heading("cod", text="Cód. Usuário")
        self.tree_usuarios.heading("nome", text="Nome do Usuário")
        self.tree_usuarios.heading("data", text="Data Vínculo")
        self.tree_usuarios.heading("responsavel", text="Responsável")

        self.tree_usuarios.column("cod", width=100, anchor=tk.CENTER)
        self.tree_usuarios.column("nome", width=280, anchor=tk.W)
        self.tree_usuarios.column("data", width=120, anchor=tk.CENTER)
        self.tree_usuarios.column("responsavel", width=110, anchor=tk.CENTER)

        self.tree_usuarios.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        u_bar = ttk.Frame(self.tab_usuarios)
        u_bar.pack(fill=tk.X)
        ttk.Button(u_bar, text="➕ Vincular Usuário", command=self._vincular_usuario).pack(side=tk.LEFT, padx=4)
        ttk.Button(u_bar, text="🗑 Desvincular Usuário", command=self._desvincular_usuario).pack(side=tk.LEFT, padx=4)

    def _carregar_estacoes(self):
        if not self._repo:
            return

        filtro = EstacaoFiltro(
            campo_busca=self.combo_campo_busca.get(),
            texto_busca=self.entry_busca.get().strip(),
            limite=200,
        )

        try:
            self._estacoes_atuais = self._repo.listar_estacoes(filtro)

            for item in self.tree_estacoes.get_children():
                self.tree_estacoes.delete(item)

            for idx, reg in enumerate(self._estacoes_atuais):
                tag = "par" if idx % 2 == 0 else "impar"
                self.tree_estacoes.insert(
                    "",
                    tk.END,
                    text=str(idx),
                    values=(
                        reg.get("codigo_estacao", ""),
                        reg.get("descricao", ""),
                        reg.get("nome_departamento", ""),
                        reg.get("tag_servico", ""),
                        reg.get("enderecoip", ""),
                        reg.get("modelo_estacao", ""),
                        reg.get("usuario_responsavel", ""),
                        reg.get("data_cadastro", ""),
                    ),
                    tags=(tag,),
                )

            self.lbl_status.config(text=f"Total: {len(self._estacoes_atuais)} estação(ões) cadastrada(s).")
        except Exception as exc:
            logger.exception("Erro ao listar estações: %s", exc)
            messagebox.showerror("Erro", f"Erro ao listar estações de trabalho:\n{exc}")

    def _limpar_filtro(self):
        self.entry_busca.delete(0, tk.END)
        self._carregar_estacoes()

    def _on_double_click_estacao(self, event):
        selected = self.tree_estacoes.selection()
        if not selected:
            return
        idx = int(self.tree_estacoes.item(selected[0], "text"))
        if 0 <= idx < len(self._estacoes_atuais):
            self._carregar_detalhes_estacao(self._estacoes_atuais[idx])

    def _carregar_detalhes_estacao(self, reg: Dict[str, Any]):
        self._estacao_selecionada = reg

        # Preenche formulário da Aba 2
        self.edt_codigo.delete(0, tk.END)
        self.edt_codigo.insert(0, reg.get("codigo_estacao", ""))

        self.edt_descricao.delete(0, tk.END)
        self.edt_descricao.insert(0, reg.get("descricao", ""))

        self.edt_departamento.delete(0, tk.END)
        self.edt_departamento.insert(0, reg.get("nome_departamento", ""))

        self.edt_localizacao.delete(0, tk.END)
        self.edt_localizacao.insert(0, reg.get("nome_localizacao", ""))

        self.edt_servicetag.delete(0, tk.END)
        self.edt_servicetag.insert(0, reg.get("tag_servico", ""))

        self.edt_modelo.delete(0, tk.END)
        self.edt_modelo.insert(0, reg.get("modelo_estacao", ""))

        self.edt_ip.delete(0, tk.END)
        self.edt_ip.insert(0, reg.get("enderecoip", ""))

        self.edt_responsavel.delete(0, tk.END)
        self.edt_responsavel.insert(0, reg.get("usuario_responsavel", ""))

        self.txt_observacoes.delete("1.0", tk.END)
        self.txt_observacoes.insert("1.0", reg.get("observacoes", ""))

        # Carrega Hardware, Software e Usuários vinculados
        cod = reg.get("codigo_estacao", "")
        self._carregar_hardware_estacao(cod)
        self._carregar_software_estacao(cod)
        self._carregar_usuarios_estacao(cod)

        # Alterna para a aba de detalhes
        self.notebook.select(self.tab_detalhes)

    def _carregar_hardware_estacao(self, cod_estacao: str):
        for item in self.tree_hardware.get_children():
            self.tree_hardware.delete(item)

        if not self._repo or not cod_estacao:
            return

        try:
            hardwares = self._repo.listar_hardware(cod_estacao)
            for reg in hardwares:
                val = f"R$ {float(reg.get('valor', 0.0) or 0.0):,.2f}"
                self.tree_hardware.insert(
                    "",
                    tk.END,
                    text=reg.get("codigo_hardware", ""),
                    values=(
                        reg.get("codigo_hardware", ""),
                        reg.get("descricao", ""),
                        val,
                        reg.get("nf", ""),
                        reg.get("data_compra", ""),
                        reg.get("tempo_garantia", ""),
                        "Ativo" if reg.get("codigo_status", 1) == 1 else "Inativo",
                        reg.get("ip", ""),
                        reg.get("rack", ""),
                    ),
                )
        except Exception as exc:
            logger.exception("Erro ao carregar hardware: %s", exc)

    def _carregar_software_estacao(self, cod_estacao: str):
        for item in self.tree_software.get_children():
            self.tree_software.delete(item)

        if not self._repo or not cod_estacao:
            return

        try:
            softwares = self._repo.listar_software(cod_estacao)
            for reg in softwares:
                val = f"R$ {float(reg.get('valor', 0.0) or 0.0):,.2f}"
                self.tree_software.insert(
                    "",
                    tk.END,
                    text=reg.get("codigo_software", ""),
                    values=(
                        reg.get("codigo_software", ""),
                        reg.get("descricao", ""),
                        reg.get("nf", ""),
                        val,
                        reg.get("tipo_licenca", ""),
                        reg.get("data_vencimento", ""),
                    ),
                )
        except Exception as exc:
            logger.exception("Erro ao carregar software: %s", exc)

    def _carregar_usuarios_estacao(self, cod_estacao: str):
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)

        if not self._repo or not cod_estacao:
            return

        try:
            usuarios = self._repo.listar_usuarios(cod_estacao)
            for reg in usuarios:
                self.tree_usuarios.insert(
                    "",
                    tk.END,
                    text=reg.get("codigo_usuario", ""),
                    values=(
                        reg.get("codigo_usuario", ""),
                        reg.get("nome_usuario", ""),
                        reg.get("data_vinculo", ""),
                        reg.get("responsavel", ""),
                    ),
                )
        except Exception as exc:
            logger.exception("Erro ao carregar usuários da estação: %s", exc)

    def _limpar_formulario(self):
        self._estacao_selecionada = None
        self.edt_codigo.delete(0, tk.END)
        self.edt_descricao.delete(0, tk.END)
        self.edt_departamento.delete(0, tk.END)
        self.edt_localizacao.delete(0, tk.END)
        self.edt_servicetag.delete(0, tk.END)
        self.edt_modelo.delete(0, tk.END)
        self.edt_ip.delete(0, tk.END)
        self.edt_responsavel.delete(0, tk.END)
        self.txt_observacoes.delete("1.0", tk.END)

        for t in (self.tree_hardware, self.tree_software, self.tree_usuarios):
            for item in t.get_children():
                t.delete(item)

        self.edt_codigo.focus_set()

    def _salvar_estacao(self):
        if not self._service:
            return

        dados = {
            "codigo_estacao": self.edt_codigo.get().strip(),
            "descricao": self.edt_descricao.get().strip(),
            "codigo_departamento": self.edt_departamento.get().strip(),
            "tag_servico": self.edt_servicetag.get().strip(),
            "modelo_estacao": self.edt_modelo.get().strip(),
            "codigo_localizacao": self.edt_localizacao.get().strip(),
            "enderecoip": self.edt_ip.get().strip(),
            "usuario_responsavel": self.edt_responsavel.get().strip(),
            "observacoes": self.txt_observacoes.get("1.0", tk.END).strip(),
        }

        modo_inclusao = self._estacao_selecionada is None
        res: ResultadoOperacao = self._service.salvar_estacao(dados, modo_inclusao=modo_inclusao)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self._carregar_estacoes()
        else:
            messagebox.showerror("Erro ao Salvar", res.mensagem)

    def _excluir_estacao(self):
        cod = self.edt_codigo.get().strip()
        if not cod:
            messagebox.showwarning("Aviso", "Nenhuma estação selecionada para exclusão.")
            return

        if not messagebox.askyesno("Confirmação", f"Tem certeza que deseja excluir a estação '{cod}'?"):
            return

        res: ResultadoOperacao = self._service.excluir_estacao(cod)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self._limpar_formulario()
            self._carregar_estacoes()
            self.notebook.select(self.tab_lista)
        else:
            messagebox.showerror("Erro ao Excluir", res.mensagem)

    def _adicionar_hardware(self):
        cod_est = self.edt_codigo.get().strip()
        if not cod_est:
            messagebox.showwarning("Aviso", "Selecione ou grave a estação primeiro.")
            return

        win = tk.Toplevel(self)
        win.title("Adicionar Hardware à Estação")
        win.geometry("450x320")
        win.transient(self)
        win.grab_set()

        r1 = ttk.Frame(win, padding=10)
        r1.pack(fill=tk.BOTH, expand=True)

        ttk.Label(r1, text="Código Hardware:").grid(row=0, column=0, sticky=tk.W, pady=4)
        e_cod = ttk.Entry(r1, width=15)
        e_cod.grid(row=0, column=1, sticky=tk.W, pady=4)

        ttk.Label(r1, text="Descrição:").grid(row=1, column=0, sticky=tk.W, pady=4)
        e_desc = ttk.Entry(r1, width=30)
        e_desc.grid(row=1, column=1, sticky=tk.W, pady=4)

        ttk.Label(r1, text="Valor (R$):").grid(row=2, column=0, sticky=tk.W, pady=4)
        e_val = ttk.Entry(r1, width=15)
        e_val.insert(0, "0.00")
        e_val.grid(row=2, column=1, sticky=tk.W, pady=4)

        ttk.Label(r1, text="Nota Fiscal:").grid(row=3, column=0, sticky=tk.W, pady=4)
        e_nf = ttk.Entry(r1, width=15)
        e_nf.grid(row=3, column=1, sticky=tk.W, pady=4)

        ttk.Label(r1, text="Tempo Garantia (Dias):").grid(row=4, column=0, sticky=tk.W, pady=4)
        e_gar = ttk.Entry(r1, width=10)
        e_gar.insert(0, "365")
        e_gar.grid(row=4, column=1, sticky=tk.W, pady=4)

        def salvar():
            dados = {
                "codigo_hardware": e_cod.get().strip(),
                "descricao": e_desc.get().strip(),
                "valor": float(e_val.get().strip() or 0.0),
                "nf": e_nf.get().strip(),
                "tempo_garantia": int(e_gar.get().strip() or 365),
                "codigo_estacao": cod_est,
            }
            res = self._service.salvar_hardware(dados, modo_inclusao=True)
            if res.sucesso:
                messagebox.showinfo("Sucesso", res.mensagem)
                win.destroy()
                self._carregar_hardware_estacao(cod_est)
            else:
                messagebox.showerror("Erro", res.mensagem)

        ttk.Button(r1, text="✔ Salvar Hardware", command=salvar).grid(row=5, column=1, sticky=tk.E, pady=15)

    def _excluir_hardware(self):
        sel = self.tree_hardware.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um hardware na lista para excluir.")
            return

        cod_hard = self.tree_hardware.item(sel[0], "text")
        if messagebox.askyesno("Confirmação", f"Excluir hardware '{cod_hard}'?"):
            res = self._service.excluir_hardware(cod_hard)
            if res.sucesso:
                messagebox.showinfo("Sucesso", res.mensagem)
                self._carregar_hardware_estacao(self.edt_codigo.get().strip())
            else:
                messagebox.showerror("Erro", res.mensagem)

    def _adicionar_software(self):
        cod_est = self.edt_codigo.get().strip()
        if not cod_est:
            messagebox.showwarning("Aviso", "Selecione ou grave a estação primeiro.")
            return

        win = tk.Toplevel(self)
        win.title("Adicionar Software / Licença")
        win.geometry("450x260")
        win.transient(self)
        win.grab_set()

        r = ttk.Frame(win, padding=10)
        r.pack(fill=tk.BOTH, expand=True)

        ttk.Label(r, text="Código Software:").grid(row=0, column=0, sticky=tk.W, pady=4)
        e_cod = ttk.Entry(r, width=15)
        e_cod.grid(row=0, column=1, sticky=tk.W, pady=4)

        ttk.Label(r, text="Descrição Software:").grid(row=1, column=0, sticky=tk.W, pady=4)
        e_desc = ttk.Entry(r, width=30)
        e_desc.grid(row=1, column=1, sticky=tk.W, pady=4)

        ttk.Label(r, text="Tipo Licença:").grid(row=2, column=0, sticky=tk.W, pady=4)
        e_lic = ttk.Entry(r, width=20)
        e_lic.grid(row=2, column=1, sticky=tk.W, pady=4)

        def salvar():
            dados = {
                "codigo_software": e_cod.get().strip(),
                "descricao": e_desc.get().strip(),
                "tipo_licenca": e_lic.get().strip(),
                "codigo_estacao": cod_est,
            }
            if self._repo.salvar_software(dados, modo_inclusao=True):
                messagebox.showinfo("Sucesso", "Software registrado com sucesso!")
                win.destroy()
                self._carregar_software_estacao(cod_est)
            else:
                messagebox.showerror("Erro", "Falha ao registrar software.")

        ttk.Button(r, text="✔ Salvar Software", command=salvar).grid(row=4, column=1, sticky=tk.E, pady=15)

    def _excluir_software(self):
        sel = self.tree_software.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um software na lista.")
            return

        cod_soft = self.tree_software.item(sel[0], "text")
        if messagebox.askyesno("Confirmação", f"Excluir software '{cod_soft}'?"):
            if self._repo.excluir_software(cod_soft):
                messagebox.showinfo("Sucesso", "Software excluído com sucesso!")
                self._carregar_software_estacao(self.edt_codigo.get().strip())
            else:
                messagebox.showerror("Erro", "Falha ao excluir software.")

    def _vincular_usuario(self):
        cod_est = self.edt_codigo.get().strip()
        if not cod_est:
            messagebox.showwarning("Aviso", "Selecione uma estação primeiro.")
            return

        win = tk.Toplevel(self)
        win.title("Vincular Usuário à Estação")
        win.geometry("400x180")
        win.transient(self)
        win.grab_set()

        r = ttk.Frame(win, padding=15)
        r.pack(fill=tk.BOTH, expand=True)

        ttk.Label(r, text="Código do Usuário:").grid(row=0, column=0, sticky=tk.W, pady=5)
        e_usu = ttk.Entry(r, width=18)
        e_usu.grid(row=0, column=1, sticky=tk.W, pady=5)

        ttk.Label(r, text="É o Responsável?:").grid(row=1, column=0, sticky=tk.W, pady=5)
        cb_resp = ttk.Combobox(r, values=["Sim", "Não"], state="readonly", width=8)
        cb_resp.set("Sim")
        cb_resp.grid(row=1, column=1, sticky=tk.W, pady=5)

        def salvar():
            cod_u = e_usu.get().strip()
            if not cod_u:
                messagebox.showwarning("Aviso", "Informe o código do usuário.")
                return
            if self._repo.vincular_usuario(cod_u, cod_est, cb_resp.get()):
                messagebox.showinfo("Sucesso", "Usuário vinculado com sucesso!")
                win.destroy()
                self._carregar_usuarios_estacao(cod_est)
            else:
                messagebox.showerror("Erro", "Falha ao vincular usuário.")

        ttk.Button(r, text="✔ Vincular", command=salvar).grid(row=2, column=1, sticky=tk.E, pady=15)

    def _desvincular_usuario(self):
        sel = self.tree_usuarios.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um usuário na lista.")
            return
        cod_usu = self.tree_usuarios.item(sel[0], "text")
        cod_est = self.edt_codigo.get().strip()
        if messagebox.askyesno("Confirmação", f"Desvincular usuário '{cod_usu}' desta estação?"):
            if self._repo.desvincular_usuario(cod_usu, cod_est):
                messagebox.showinfo("Sucesso", "Usuário desvinculado com sucesso!")
                self._carregar_usuarios_estacao(cod_est)
            else:
                messagebox.showerror("Erro", "Falha ao desvincular usuário.")

    def _exportar_excel(self):
        if not self._estacoes_atuais:
            messagebox.showwarning("Aviso", "Nenhum dado disponível para exportação.")
            return

        caminho = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Planilha Excel", "*.xlsx")],
            title="Salvar Inventário em Excel",
            initialfile="Inventario_Estacoes_GeoAlvo.xlsx",
        )
        if not caminho:
            return

        try:
            RelatorioGenerator.gerar_excel(self._estacoes_atuais, "Inventário de Estações de Trabalho", caminho)
            messagebox.showinfo("Sucesso", f"Planilha exportada com sucesso em:\n{caminho}")
        except Exception as exc:
            messagebox.showerror("Erro", f"Falha ao gerar Excel:\n{exc}")

    def _exportar_html(self):
        if not self._estacoes_atuais:
            messagebox.showwarning("Aviso", "Nenhum dado para impressão.")
            return
        try:
            RelatorioGenerator.gerar_html_imprimivel(self._estacoes_atuais, "Inventário de Estações de Trabalho")
        except Exception as exc:
            messagebox.showerror("Erro", f"Falha ao abrir relatório de impressão:\n{exc}")
