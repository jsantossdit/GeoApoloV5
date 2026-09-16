"""
Interface Gráfica em Python (Tkinter / ttk) para Gestão e Integração de Entidades.
Layout corporativo e profissional alinhado aos padrões visuais do sistema GeoAlvo.
Correspondente e evolução de unt_entidades.pas (Tfrmentidades).
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import logging
from typing import Optional, List, Dict, Any

from entidades.models import (
    EntidadeFiltro,
    ItemComparacao,
    DecisaoLinha,
    ResultadoOperacao,
)
from entidades.repository import EntidadeRepository
from entidades.service import EntidadeService
from entidades.api_client import AlvoAPIClient
from entidades.database import obter_conexao_banco

logger = logging.getLogger(__name__)


class EntidadesView(tk.Toplevel):
    """Janela principal de Gestão de Entidades do GeoAlvo."""

    def __init__(self, parent=None, connection=None):
        super().__init__(parent)
        self.title("Gestão e Integração de Entidades - GeoAlvo")
        self.geometry("1160x680")
        self.minsize(950, 560)

        # Centraliza a janela
        self._centralizar_janela(1160, 680)

        # Ícone da aplicação
        self._aplicar_icone()

        # Inicializa dependências
        self._conn = connection
        if self._conn is None:
            try:
                self._conn = obter_conexao_banco()
            except Exception as exc:
                messagebox.showwarning(
                    "Aviso de Conexão",
                    f"Não foi possível conectar automaticamente ao banco:\n{exc}\n\nConfigure o banco de dados no menu Configurações."
                )

        self._repo = EntidadeRepository(self._conn) if self._conn else None
        self._service = EntidadeService(self._repo) if self._repo else None
        self._api_client = AlvoAPIClient()

        self._registros_atuais: List[Dict[str, Any]] = []
        self._ordem_colunas_asc = {}

        self._configurar_estilos()
        self._criar_interface()
        self._carregar_dados()

        # Atalhos de Teclado
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<F5>", lambda e: self._carregar_dados())

    def _centralizar_janela(self, largura: int, altura: int):
        self.update_idletasks()
        pos_x = (self.winfo_screenwidth() // 2) - (largura // 2)
        pos_y = (self.winfo_screenheight() // 2) - (altura // 2) - 20
        self.geometry(f"{largura}x{altura}+{max(pos_x, 0)}+{max(pos_y, 0)}")

    def _aplicar_icone(self):
        caminhos = [
            os.path.join(os.path.dirname(__file__), "..", "Imagens", "entidades.png"),
            os.path.join(os.path.dirname(__file__), "..", "Imagens", "IconeRCC.png"),
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
            "Entidades.Treeview",
            font=("Segoe UI", 9),
            rowheight=26,
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
        )
        style.configure(
            "Entidades.Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            foreground="#1A365D",
            padding=5,
        )

    def _criar_interface(self):
        # 1. Header Banner Corporativo
        banner_frame = tk.Frame(self, bg="#1A365D", height=58)
        banner_frame.pack(side=tk.TOP, fill=tk.X)
        banner_frame.pack_propagate(False)

        lbl_titulo = tk.Label(
            banner_frame,
            text="👥 Gestão e Integração de Entidades",
            font=("Segoe UI", 12, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
            anchor="w",
        )
        lbl_titulo.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(8, 0))

        lbl_subtitulo = tk.Label(
            banner_frame,
            text="Sincronização GeoApolo (SVE) ↔ Alvo | Moderação de cadastros e resolução de divergências",
            font=("Segoe UI", 8),
            bg="#1A365D",
            fg="#CBD5E0",
            anchor="w",
        )
        lbl_subtitulo.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(1, 6))

        # 2. Painel de Filtros e Pesquisa
        filtro_container = ttk.LabelFrame(self, text="Filtros e Parâmetros de Pesquisa", padding=10)
        filtro_container.pack(side=tk.TOP, fill=tk.X, padx=12, pady=(10, 5))

        # Linha 1: Base de dados e campos de busca
        row1 = ttk.Frame(filtro_container)
        row1.pack(fill=tk.X, pady=3)

        ttk.Label(row1, text="Base de Dados:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        self.combo_base = ttk.Combobox(row1, values=["GeoApolo", "Alvo"], state="readonly", width=12)
        self.combo_base.set("GeoApolo")
        self.combo_base.pack(side=tk.LEFT, padx=(0, 15))
        self.combo_base.bind("<<ComboboxSelected>>", lambda e: self._carregar_dados())

        ttk.Label(row1, text="Campo de Busca:").pack(side=tk.LEFT, padx=(0, 5))
        self.combo_campo = ttk.Combobox(
            row1,
            values=["entnome", "geoentnome", "Documento", "EntCpfCgc", "geoentender", "cidnomecomp"],
            state="readonly",
            width=15,
        )
        self.combo_campo.set("geoentnome")
        self.combo_campo.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(row1, text="Procurar por:").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_busca = ttk.Entry(row1, width=28, font=("Segoe UI", 9))
        self.entry_busca.pack(side=tk.LEFT, padx=(0, 8))
        self.entry_busca.bind("<Return>", lambda e: self._carregar_dados(especifica=True))

        btn_buscar = ttk.Button(row1, text="🔍 Buscar", command=lambda: self._carregar_dados(especifica=True))
        btn_buscar.pack(side=tk.LEFT, padx=3)

        btn_limpar = ttk.Button(row1, text="✖ Limpar", command=self._limpar_busca)
        btn_limpar.pack(side=tk.LEFT, padx=3)

        # Linha 2: Ordenação e Filtros Especiais
        row2 = ttk.Frame(filtro_container)
        row2.pack(fill=tk.X, pady=(6, 2))

        ttk.Label(row2, text="Ordenar por:").pack(side=tk.LEFT, padx=(0, 5))
        self.combo_ordem = ttk.Combobox(
            row2,
            values=["geoentnome", "entnome", "geoentcod", "entcod", "entdatacad"],
            state="readonly",
            width=15,
        )
        self.combo_ordem.set("geoentnome")
        self.combo_ordem.pack(side=tk.LEFT, padx=(0, 15))
        self.combo_ordem.bind("<<ComboboxSelected>>", lambda e: self._carregar_dados())

        self.var_ordem_asc = tk.BooleanVar(value=True)
        r_asc = ttk.Radiobutton(
            row2, text="Crescente (A-Z)", variable=self.var_ordem_asc, value=True, command=self._carregar_dados
        )
        r_asc.pack(side=tk.LEFT, padx=5)
        r_desc = ttk.Radiobutton(
            row2, text="Decrescente (Z-A)", variable=self.var_ordem_asc, value=False, command=self._carregar_dados
        )
        r_desc.pack(side=tk.LEFT, padx=5)

        self.var_filtro_exportada = tk.StringVar(value="PENDENTES")
        chk_exp = ttk.Checkbutton(
            row2,
            text="Somente Já Sincronizadas",
            variable=self.var_filtro_exportada,
            onvalue="JAEXPORTADA",
            offvalue="PENDENTES",
            command=self._carregar_dados,
        )
        chk_exp.pack(side=tk.LEFT, padx=20)

        # 3. Painel Central: Grid de Entidades
        grid_container = ttk.LabelFrame(self, text="Entidades Cadastradas (Duplo clique para conferir/editar)", padding=8)
        grid_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=12, pady=5)

        colunas = (
            "codigo",
            "nome",
            "documento",
            "endereco",
            "cidade",
            "atualizou",
            "observacoes",
        )
        tree_scroll_y = ttk.Scrollbar(grid_container, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(grid_container, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(
            grid_container,
            columns=colunas,
            show="headings",
            selectmode="browse",
            style="Entidades.Treeview",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
        )
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        self.tree.heading("codigo", text="Cód.", command=lambda: self._ordenar_coluna("codigo"))
        self.tree.heading("nome", text="Nome da Entidade", command=lambda: self._ordenar_coluna("nome"))
        self.tree.heading("documento", text="CPF / CNPJ", command=lambda: self._ordenar_coluna("documento"))
        self.tree.heading("endereco", text="Endereço Completo", command=lambda: self._ordenar_coluna("endereco"))
        self.tree.heading("cidade", text="Cidade / UF", command=lambda: self._ordenar_coluna("cidade"))
        self.tree.heading("atualizou", text="Sincronizado Alvo", command=lambda: self._ordenar_coluna("atualizou"))
        self.tree.heading("observacoes", text="Observações / Motivo", command=lambda: self._ordenar_coluna("observacoes"))

        self.tree.column("codigo", width=75, anchor=tk.CENTER)
        self.tree.column("nome", width=250, anchor=tk.W)
        self.tree.column("documento", width=130, anchor=tk.CENTER)
        self.tree.column("endereco", width=240, anchor=tk.W)
        self.tree.column("cidade", width=150, anchor=tk.W)
        self.tree.column("atualizou", width=115, anchor=tk.CENTER)
        self.tree.column("observacoes", width=190, anchor=tk.W)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.bind("<Double-1>", self._on_double_click)

        # Tags visuais
        self.tree.tag_configure("par", background="#FFFFFF")
        self.tree.tag_configure("impar", background="#F7FAFC")
        self.tree.tag_configure("sincronizado", foreground="#2B6CB0")
        self.tree.tag_configure("pendente", foreground="#C53030")

        # 4. Painel Inferior: Barra de Ações Corporativa
        bottom_frame = tk.Frame(self, bg="#E2E8F0", height=46, bd=1, relief=tk.GROOVE)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        bottom_frame.pack_propagate(False)

        btn_box = tk.Frame(bottom_frame, bg="#E2E8F0")
        btn_box.pack(side=tk.LEFT, padx=10, pady=7)

        self.btn_exportar = ttk.Button(
            btn_box, text="🚀 Exportar para Alvo", command=self._acao_exportar
        )
        self.btn_exportar.pack(side=tk.LEFT, padx=4)

        self.btn_ignorar = ttk.Button(
            btn_box, text="🚫 Ignorar Registro", command=self._acao_ignorar
        )
        self.btn_ignorar.pack(side=tk.LEFT, padx=4)

        self.btn_atualizar = ttk.Button(
            btn_box, text="🔄 Atualizar (F5)", command=self._carregar_dados
        )
        self.btn_atualizar.pack(side=tk.LEFT, padx=4)

        self.btn_relatorios = ttk.Button(
            btn_box, text="📊 Central de Relatórios", command=self._abrir_relatorios_integrados
        )
        self.btn_relatorios.pack(side=tk.LEFT, padx=4)

        btn_fechar = ttk.Button(bottom_frame, text="🚪 Fechar (Esc)", command=self.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=12, pady=7)

        self.lbl_status = tk.Label(
            bottom_frame,
            text="0 entidades listadas.",
            font=("Segoe UI", 9, "italic"),
            bg="#E2E8F0",
            fg="#4A5568",
        )
        self.lbl_status.pack(side=tk.RIGHT, padx=16)

    def _limpar_busca(self):
        self.entry_busca.delete(0, tk.END)
        self._carregar_dados()

    def _abrir_relatorios_integrados(self):
        try:
            from relatorios import RelatoriosView
            RelatoriosView(self, connection=self._conn)
        except Exception as exc:
            logger.exception("Erro ao abrir relatórios: %s", exc)
            messagebox.showerror("Erro", f"Não foi possível abrir os relatórios:\n{exc}")

    def _ordenar_coluna(self, col: str):
        """Permite ordenar os itens da tabela clicando nos cabeçalhos."""
        asc = not self._ordem_colunas_asc.get(col, False)
        self._ordem_colunas_asc[col] = asc

        itens = [(self.tree.set(item, col), item) for item in self.tree.get_children("")]
        itens.sort(reverse=not asc)

        for index, (_, item) in enumerate(itens):
            self.tree.move(item, "", index)
            tag_zebra = "par" if index % 2 == 0 else "impar"
            tags_atuais = [t for t in self.tree.item(item, "tags") if t not in ("par", "impar")]
            self.tree.item(item, tags=[tag_zebra] + tags_atuais)

    def _obter_registro_selecionado(self) -> Optional[Dict[str, Any]]:
        selected = self.tree.selection()
        if not selected:
            return None
        idx = int(self.tree.item(selected[0], "text"))
        if 0 <= idx < len(self._registros_atuais):
            return self._registros_atuais[idx]
        return None

    def _carregar_dados(self, especifica: bool = False):
        if not self._repo:
            return

        filtro = EntidadeFiltro(
            base_dados=self.combo_base.get(),
            tipo_pesquisa="Especifica" if especifica else "Consulta",
            filtro_especial=self.var_filtro_exportada.get(),
            campo_busca=self.combo_campo.get(),
            texto_busca=self.entry_busca.get().strip(),
            campo_ordenacao=self.combo_ordem.get(),
            ordem_asc=self.var_ordem_asc.get(),
            limite=100,
        )

        try:
            self._registros_atuais = self._repo.consultar_lista(filtro)

            # Limpa grid
            for item in self.tree.get_children():
                self.tree.delete(item)

            for idx, reg in enumerate(self._registros_atuais):
                cod = reg.get("geoentcod") or reg.get("entcod") or ""
                nome = reg.get("geoentnome") or reg.get("entnome") or ""
                doc = reg.get("EntCpfCgc") or reg.get("Documento") or ""
                ender = reg.get("geoentender") or reg.get("entender") or ""
                cid = f"{reg.get('cidnomecomp', '')} / {reg.get('ufsigla', '')}".strip(" /")
                atualizou = reg.get("atualizou_apolo", "N")
                obs = reg.get("Entobservacoes") or ""

                tag_zebra = "par" if idx % 2 == 0 else "impar"
                tag_status = "sincronizado" if atualizou == "S" else "pendente"

                status_formatado = "✔ Sim (Sincronizado)" if atualizou == "S" else "⏳ Não (Pendente)"

                self.tree.insert(
                    "",
                    tk.END,
                    text=str(idx),
                    values=(cod, nome, doc, ender, cid, status_formatado, obs),
                    tags=(tag_zebra, tag_status),
                )

            self.lbl_status.config(text=f"Total: {len(self._registros_atuais)} entidade(s) listada(s).")
        except Exception as exc:
            logger.exception("Erro ao carregar lista de entidades: %s", exc)
            messagebox.showerror("Erro", f"Erro ao consultar entidades:\n{exc}")

    def _on_double_click(self, event):
        reg = self._obter_registro_selecionado()
        if not reg:
            return

        entcod = reg.get("entcod")
        geoentcod = reg.get("geoentcod")

        # Se já existe no Alvo e no GeoApolo, abre comparador lado a lado
        if entcod and geoentcod and self._repo and self._service:
            sve_data, alvo_data = self._repo.carregar_dados_comparacao(str(geoentcod), str(entcod))
            difs = self._service.comparar_cadastros(sve_data, alvo_data)
            self._abrir_tela_comparacao(difs)
        else:
            messagebox.showinfo(
                "Detalhes da Entidade",
                f"Código: {reg.get('geoentcod') or reg.get('entcod')}\n"
                f"Nome: {reg.get('geoentnome') or reg.get('entnome')}\n"
                f"Documento: {reg.get('EntCpfCgc') or reg.get('Documento') or 'N/I'}\n"
                f"Status: {reg.get('atualizou_apolo', 'N')}",
            )

    def _abrir_tela_comparacao(self, diferencas: List[ItemComparacao]):
        """Janela modal para comparação de campos SVE x Alvo com decisões em lote e layout refinado."""
        if not diferencas:
            messagebox.showinfo("Comparação de Cadastros", "✔ Cadastros idênticos! Nenhuma divergência encontrada.")
            return

        comp_win = tk.Toplevel(self)
        comp_win.title("Comparador de Divergências: GeoApolo (SVE) x Alvo")
        comp_win.geometry("920x520")
        comp_win.minsize(800, 420)
        comp_win.transient(self)
        comp_win.grab_set()

        # Banner Superior do Comparador
        banner_comp = tk.Frame(comp_win, bg="#1A365D", height=50)
        banner_comp.pack(side=tk.TOP, fill=tk.X)
        banner_comp.pack_propagate(False)

        tk.Label(
            banner_comp,
            text=f"⚖ Conferência Lado a Lado: {len(diferencas)} divergência(s) encontrada(s)",
            font=("Segoe UI", 11, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
        ).pack(side=tk.LEFT, padx=15, pady=8)

        # Barra de Ações Rápidas em Lote
        batch_bar = ttk.Frame(comp_win, padding=6)
        batch_bar.pack(side=tk.TOP, fill=tk.X, padx=10, pady=4)

        cols = ("campo", "sve", "alvo", "decisao")
        tree_comp = ttk.Treeview(comp_win, columns=cols, show="headings", selectmode="browse")
        tree_comp.heading("campo", text="Campo Divergente")
        tree_comp.heading("sve", text="GeoApolo (SVE) - Clique p/ Usar")
        tree_comp.heading("alvo", text="Alvo - Clique p/ Manter")
        tree_comp.heading("decisao", text="Decisão Tomada")

        tree_comp.column("campo", width=160)
        tree_comp.column("sve", width=280)
        tree_comp.column("alvo", width=280)
        tree_comp.column("decisao", width=150, anchor=tk.CENTER)

        tree_scroll_y = ttk.Scrollbar(comp_win, orient=tk.VERTICAL, command=tree_comp.yview)
        tree_comp.configure(yscrollcommand=tree_scroll_y.set)

        tree_comp.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        def atualizar_tabela_comp():
            for idx, item in enumerate(diferencas):
                if item.decisao == DecisaoLinha.MANTER_SVE:
                    status = "✔ Usar GeoApolo (SVE)"
                elif item.decisao == DecisaoLinha.MANTER_ALVO:
                    status = "✔ Manter Alvo"
                else:
                    status = "— pendente —"

                if tree_comp.exists(str(idx)):
                    tree_comp.item(str(idx), values=(item.rotulo, item.valor_sve, item.valor_alvo, status))
                else:
                    tree_comp.insert(
                        "",
                        tk.END,
                        iid=str(idx),
                        values=(item.rotulo, item.valor_sve, item.valor_alvo, status),
                    )

        atualizar_tabela_comp()

        # Funções para botões em lote
        def selecionar_todos_sve():
            for item in diferencas:
                item.decisao = DecisaoLinha.MANTER_SVE
            atualizar_tabela_comp()

        def selecionar_todos_alvo():
            for item in diferencas:
                item.decisao = DecisaoLinha.MANTER_ALVO
            atualizar_tabela_comp()

        ttk.Button(batch_bar, text="⬅ Usar Todos do GeoApolo (SVE)", command=selecionar_todos_sve).pack(side=tk.LEFT, padx=4)
        ttk.Button(batch_bar, text="➡ Manter Todos do Alvo", command=selecionar_todos_alvo).pack(side=tk.LEFT, padx=4)
        ttk.Label(batch_bar, text="(Ou clique na célula desejada na tabela)", font=("Segoe UI", 9, "italic")).pack(side=tk.LEFT, padx=10)

        def on_click_cell(event):
            region = tree_comp.identify_region(event.x, event.y)
            if region != "cell":
                return
            col_id = tree_comp.identify_column(event.x)
            item_id = tree_comp.identify_row(event.y)
            if not item_id:
                return

            idx = int(item_id)
            if col_id == "#2":  # Clicou na coluna SVE
                diferencas[idx].decisao = DecisaoLinha.MANTER_SVE
            elif col_id == "#3":  # Clicou na coluna Alvo
                diferencas[idx].decisao = DecisaoLinha.MANTER_ALVO
            atualizar_tabela_comp()

        tree_comp.bind("<ButtonRelease-1>", on_click_cell)

        # Rodapé de ações do modal
        btn_frame = tk.Frame(comp_win, bg="#E2E8F0", height=46, bd=1, relief=tk.GROOVE)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
        btn_frame.pack_propagate(False)

        def salvar_sobreposicao():
            pendentes = [d for d in diferencas if d.decisao == DecisaoLinha.NENHUMA]
            if pendentes:
                if not messagebox.askyesno(
                    "Decisões Pendentes",
                    f"Ainda restam {len(pendentes)} campo(s) sem decisão explícita.\nDeseja aplicar as decisões atuais e ignorar os demais?"
                ):
                    return

            payload = self._service.gerar_payload_sobreposicao(diferencas)
            sucesso, msg = self._api_client.enviar_entidade(payload)
            if sucesso:
                messagebox.showinfo("Sucesso", "Decisões de sobreposição aplicadas no Alvo com sucesso!")
                comp_win.destroy()
                self._carregar_dados()
            else:
                messagebox.showerror("Falha ao Sobrepor", f"Erro retornado pela API Alvo:\n{msg}")

        ttk.Button(btn_frame, text="✔ Aplicar Decisões no Alvo", command=salvar_sobreposicao).pack(side=tk.LEFT, padx=10, pady=7)
        ttk.Button(btn_frame, text="Cancelar (Esc)", command=comp_win.destroy).pack(side=tk.RIGHT, padx=10, pady=7)
        comp_win.bind("<Escape>", lambda e: comp_win.destroy())

    def _acao_exportar(self):
        reg = self._obter_registro_selecionado()
        if not reg:
            messagebox.showwarning("Aviso", "Selecione uma entidade na lista primeiro.")
            return

        base = self.combo_base.get()
        obs = reg.get("Entobservacoes") or ""

        pode, motivo = self._service.pode_exportar_para_alvo(base, obs)
        if not pode:
            messagebox.showwarning("Exportação Impedida", motivo)
            return

        geoentcod = str(reg.get("geoentcod") or "")
        entcod = self._service.obter_ou_resolver_entcod_alvo(geoentcod, reg.get("entcod"))

        if entcod:
            # Já existe no Alvo -> dispara fluxo de conferência/comparação
            sve_data, alvo_data = self._repo.carregar_dados_comparacao(geoentcod, str(entcod))
            difs = self._service.comparar_cadastros(sve_data, alvo_data)
            self._abrir_tela_comparacao(difs)
        else:
            # Inclusão direta
            if messagebox.askyesno("Confirmação", "Confirma a exportação e inserção desta entidade para o Alvo?"):
                payload = {
                    "Operacao": "I",
                    "CodigoAlternativo": geoentcod,
                    "Nome": reg.get("geoentnome") or reg.get("entnome"),
                    "CPFCNPJ": reg.get("EntCpfCgc") or reg.get("Documento"),
                }
                sucesso, msg = self._api_client.enviar_entidade(payload)
                if sucesso:
                    messagebox.showinfo("Sucesso", f"Entidade exportada com sucesso!\n{msg}")
                    self._carregar_dados()
                else:
                    messagebox.showerror("Erro na Exportação", msg)

    def _acao_ignorar(self):
        reg = self._obter_registro_selecionado()
        if not reg:
            messagebox.showwarning("Aviso", "Selecione uma entidade na lista primeiro.")
            return

        if not messagebox.askyesno("Confirmação", "Confirma a não atualização deste registro no Alvo?"):
            return

        geoentcod = str(reg.get("geoentcod") or "")
        resultado: ResultadoOperacao = self._service.executar_acao_ignorar(
            geoentcod=geoentcod,
            usucod_apolo="APOLO_SYS",
            cod_empresa="001",
            cod_usuario="ADMIN",
        )

        if resultado.sucesso:
            messagebox.showinfo("Sucesso", resultado.mensagem)
            self._carregar_dados()
        else:
            messagebox.showerror("Erro", resultado.mensagem)
