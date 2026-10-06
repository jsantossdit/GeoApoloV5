"""
Interface Gráfica para Cadastro e Manutenção de Produtos.
GeoApolo V5
Equivalente a unt_cadprodutos.pas do Delphi.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Tuple

from core import (
    centralizar_janela,
    vincular_maiusculo,
    configurar_navegacao_enter,
    habilitar_filtro_dinamico_combobox,
)
from produtos.models import ProdutoDTO
from produtos.service import ProdutosService
from produtos.grupos_view import abrir_janela_grupos_produtos
from marcas.view import abrir_janela_marcas
from cores.view import abrir_janela_cores


class ProdutosView(ttk.Frame):
    """Tela de cadastro e manutenção de produtos."""

    def __init__(self, parent=None, service: Optional[ProdutosService] = None, connection=None):
        super().__init__(parent)
        self.service = service
        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from produtos.repository import ProdutosRepository
                conn = connection or obter_conexao_banco()
                self.service = ProdutosService(ProdutosRepository(conn))
            except Exception:
                pass

        self._map_grupos = {}
        self._map_marcas = {}
        self._cores_selecionadas: List[Tuple[int, str]] = []  # lista de (codigo_cor, descricao_cor)
        self._almoxarifados_vinculados = []
        self._setup_ui()
        self._configurar_atalhos()
        if self.service:
            self._carregar_dados_iniciais()

    def _setup_ui(self):
        # Header superior
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        lbl_titulo = ttk.Label(
            header,
            text="Cadastro e Manutenção de Produtos",
            font=("Segoe UI", 13, "bold"),
            foreground="#1E3A8A",
        )
        lbl_titulo.pack(side=tk.LEFT)

        btn_diag = ttk.Button(
            header,
            text="🩺 Sanidade das Tabelas",
            command=self._abrir_diagnostico_schema,
        )
        btn_diag.pack(side=tk.LEFT, padx=(14, 0))

        # Contador de registros
        f_count = ttk.Frame(header)
        f_count.pack(side=tk.RIGHT, padx=10)

        ttk.Label(
            f_count,
            text="Nº de Registros:",
            font=("Segoe UI", 9, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 4))

        self.lbl_num_produtos = ttk.Label(
            f_count,
            text="0",
            font=("Segoe UI", 10, "bold"),
            foreground="#B91C1C",
        )
        self.lbl_num_produtos.pack(side=tk.LEFT)

        # Painel Dividido (Grade à esquerda, Formulário à direita)
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ---------------------------------------------------------------------
        # Painel Esquerdo: Lista de Produtos
        # ---------------------------------------------------------------------
        left = ttk.Frame(paned, padding=5)
        paned.add(left, weight=3)

        # Barra de Pesquisa e Filtro
        f_pesquisa = ttk.Frame(left)
        f_pesquisa.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(f_pesquisa, text="Buscar:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.var_filtro = tk.StringVar()
        vincular_maiusculo(self.var_filtro)
        self.ent_filtro = ttk.Entry(f_pesquisa, textvariable=self.var_filtro, width=18)
        self.ent_filtro.pack(side=tk.LEFT, padx=(0, 6))
        self.ent_filtro.bind("<Return>", lambda e: self.carregar_produtos())

        ttk.Label(f_pesquisa, text="Grupo:").pack(side=tk.LEFT, padx=(4, 4))
        self.cbo_filtro_grupo = ttk.Combobox(f_pesquisa, state="readonly", width=16)
        self.cbo_filtro_grupo.pack(side=tk.LEFT, padx=(0, 6))
        self.cbo_filtro_grupo.bind("<<ComboboxSelected>>", lambda e: self.carregar_produtos())

        btn_busca = ttk.Button(f_pesquisa, text="Filtrar", command=self.carregar_produtos, width=8)
        btn_busca.pack(side=tk.LEFT, padx=2)

        btn_limpar_busca = ttk.Button(f_pesquisa, text="Todos", command=self._limpar_filtro, width=7)
        btn_limpar_busca.pack(side=tk.LEFT, padx=2)

        # Treeview de Produtos com Marca e Cores
        cols = ("cod", "nome", "marca", "grupo", "tamanho", "inmetro", "cores", "alt")
        self.tree_produtos = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        self.tree_produtos.heading("cod", text="Código")
        self.tree_produtos.heading("nome", text="Descrição do Produto")
        self.tree_produtos.heading("marca", text="Marca")
        self.tree_produtos.heading("grupo", text="Grupo")
        self.tree_produtos.heading("tamanho", text="Unid.")
        self.tree_produtos.heading("inmetro", text="INMETRO")
        self.tree_produtos.heading("cores", text="Cores")
        self.tree_produtos.heading("alt", text="Descrição Alternativa")

        self.tree_produtos.column("cod", width=55, anchor=tk.CENTER)
        self.tree_produtos.column("nome", width=180)
        self.tree_produtos.column("marca", width=100)
        self.tree_produtos.column("grupo", width=100)
        self.tree_produtos.column("tamanho", width=50, anchor=tk.CENTER)
        self.tree_produtos.column("inmetro", width=80, anchor=tk.CENTER)
        self.tree_produtos.column("cores", width=100)
        self.tree_produtos.column("alt", width=110)

        scroll_y = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.tree_produtos.yview)
        scroll_x = ttk.Scrollbar(left, orient=tk.HORIZONTAL, command=self.tree_produtos.xview)
        self.tree_produtos.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_produtos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_produtos.bind("<<TreeviewSelect>>", self._ao_selecionar_produto)

        # ---------------------------------------------------------------------
        # Painel Direito: Formulário de Cadastro
        # ---------------------------------------------------------------------
        right = ttk.Frame(paned, padding=8)
        paned.add(right, weight=2)

        form_box = ttk.LabelFrame(right, text=" Dados do Produto ", padding=10)
        form_box.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        # 1. Código do Produto
        ttk.Label(form_box, text="Código Interno:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(2, 2))
        self.ent_prodcod = ttk.Entry(form_box, width=12)
        self.ent_prodcod.pack(anchor=tk.W, pady=(0, 6))

        # 2. Descrição do Produto (MAIÚSCULO)
        ttk.Label(form_box, text="Descrição do Produto (*):", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(2, 2))
        self.var_prodnome = tk.StringVar()
        vincular_maiusculo(self.var_prodnome)
        self.ent_prodnome = ttk.Entry(form_box, textvariable=self.var_prodnome)
        self.ent_prodnome.pack(fill=tk.X, pady=(0, 6))

        # 3. Marca do Produto (com auto-inclusão ao digitar marca nova)
        f_lbl_marca = ttk.Frame(form_box)
        f_lbl_marca.pack(fill=tk.X, pady=(2, 2))
        ttk.Label(f_lbl_marca, text="Marca do Produto:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)

        btn_marcas_link = ttk.Button(
            f_lbl_marca,
            text="+ Marcas",
            command=self._abrir_cadastro_marcas,
            width=12
        )
        btn_marcas_link.pack(side=tk.RIGHT)

        self.var_marca = tk.StringVar()
        self.cbo_marca = ttk.Combobox(form_box, textvariable=self.var_marca)
        self.cbo_marca.pack(fill=tk.X, pady=(0, 6))

        # 4. Grupo do Produto com atalho
        f_lbl_grupo = ttk.Frame(form_box)
        f_lbl_grupo.pack(fill=tk.X, pady=(2, 2))
        ttk.Label(f_lbl_grupo, text="Grupo de Produtos:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)

        btn_novo_grupo_link = ttk.Button(
            f_lbl_grupo,
            text="+ Novo Grupo <F4>",
            command=self._abrir_cadastro_grupos,
            width=16
        )
        btn_novo_grupo_link.pack(side=tk.RIGHT)

        self.cbo_grupo = ttk.Combobox(form_box)
        self.cbo_grupo.pack(fill=tk.X, pady=(0, 6))

        # 5. Unidade de Medida e Código INMETRO
        f_ctrl_box = ttk.Frame(form_box)
        f_ctrl_box.pack(fill=tk.X, pady=(2, 6))

        # Coluna 1: Unidade de Medida
        f_col_unid = ttk.Frame(f_ctrl_box)
        f_col_unid.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ttk.Label(f_col_unid, text="Unidade de Medida (*):", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_unidade = tk.StringVar(value="UN")
        vincular_maiusculo(self.var_unidade)
        self.var_tamanho = self.var_unidade  # Retrocompatibilidade
        self.cbo_unidade = ttk.Combobox(
            f_col_unid,
            textvariable=self.var_unidade,
            values=[
                "UN - UNIDADE",
                "CX - CAIXA",
                "PCT - PACOTE",
                "PC - PEÇA",
                "KG - QUILOGRAMA",
                "LT - LITRO",
                "MT - METRO",
                "PAR - PAR",
                "DZ - DÚZIA",
                "FD - FARDO",
                "CJ - CONJUNTO",
                "RL - ROLO",
                "M2 - METRO QUADRADO",
                "M3 - METRO CÚBICO",
            ],
            width=14
        )
        self.cbo_unidade.pack(fill=tk.X)
        self.ent_tamanho = self.cbo_unidade  # Retrocompatibilidade

        # Coluna 2: Código INMETRO
        f_col_inmetro = ttk.Frame(f_ctrl_box)
        f_col_inmetro.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(f_col_inmetro, text="Código INMETRO:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_codigo_inmetro = tk.StringVar()
        vincular_maiusculo(self.var_codigo_inmetro)
        self.ent_codigo_inmetro = ttk.Entry(f_col_inmetro, textvariable=self.var_codigo_inmetro, width=14)
        self.ent_codigo_inmetro.pack(fill=tk.X)

        # 6. Cores do Produto (Seleção Múltipla com Chips/Lista)
        f_lbl_cores = ttk.Frame(form_box)
        f_lbl_cores.pack(fill=tk.X, pady=(2, 2))
        ttk.Label(f_lbl_cores, text="Cores do Produto:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)

        btn_cores_link = ttk.Button(
            f_lbl_cores,
            text="+ Vincular Cores",
            command=self._abrir_seletor_cores,
            width=16
        )
        btn_cores_link.pack(side=tk.RIGHT)

        f_cores_box = ttk.Frame(form_box, relief=tk.SOLID, borderwidth=1, padding=4)
        f_cores_box.pack(fill=tk.X, pady=(0, 6))

        self.lbl_cores_display = ttk.Label(
            f_cores_box,
            text="(Nenhuma cor vinculada)",
            font=("Segoe UI", 9),
            foreground="#1E3A8A"
        )
        self.lbl_cores_display.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        btn_limpar_cores = ttk.Button(
            f_cores_box,
            text="Limpar",
            command=self._limpar_cores_selecionadas,
            width=8
        )
        btn_limpar_cores.pack(side=tk.RIGHT)

        # 6.1 Almoxarifados do Produto (Multi-Almoxarifado)
        f_lbl_almox = ttk.Frame(form_box)
        f_lbl_almox.pack(fill=tk.X, pady=(2, 2))
        ttk.Label(f_lbl_almox, text="Almoxarifados do Produto:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)

        btn_almox_link = ttk.Button(
            f_lbl_almox,
            text="🏢 Gerenciar Almoxarifados",
            command=self._abrir_seletor_almoxarifados,
            width=26
        )
        btn_almox_link.pack(side=tk.RIGHT)

        f_almox_box = ttk.Frame(form_box, relief=tk.SOLID, borderwidth=1, padding=4)
        f_almox_box.pack(fill=tk.X, pady=(0, 6))

        self.lbl_almox_display = ttk.Label(
            f_almox_box,
            text="(Nenhum almoxarifado vinculado - padrão Geral)",
            font=("Segoe UI", 9),
            foreground="#047857"
        )
        self.lbl_almox_display.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        # 7. Descrição Alternativa (MAIÚSCULO)
        ttk.Label(form_box, text="Descrição Alternativa:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(2, 2))
        self.var_desc_alt = tk.StringVar()
        vincular_maiusculo(self.var_desc_alt)
        self.ent_desc_alt = ttk.Entry(form_box, textvariable=self.var_desc_alt)
        self.ent_desc_alt.pack(fill=tk.X, pady=(0, 6))

        # 8. Observações
        f_obs_hdr = ttk.Frame(form_box)
        f_obs_hdr.pack(fill=tk.X, pady=(2, 2))
        ttk.Label(f_obs_hdr, text="Observações / Detalhes:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        ttk.Label(
            f_obs_hdr,
            text="(Tecle <ESC> para salvar e iniciar novo produto)",
            font=("Segoe UI", 8, "italic"),
            foreground="#0D47A1"
        ).pack(side=tk.RIGHT)

        f_obs = ttk.Frame(form_box)
        f_obs.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        self.txt_observacoes = tk.Text(f_obs, height=4, font=("Segoe UI", 9), wrap=tk.WORD)
        obs_sy = ttk.Scrollbar(f_obs, orient=tk.VERTICAL, command=self.txt_observacoes.yview)
        self.txt_observacoes.configure(yscrollcommand=obs_sy.set)
        self.txt_observacoes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        obs_sy.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_observacoes.bind("<Escape>", self._on_obs_escape)

        # Padronização de Navegação por ENTER
        configurar_navegacao_enter([
            self.ent_prodcod,
            self.ent_prodnome,
            self.cbo_marca,
            self.cbo_grupo,
            self.cbo_unidade,
            self.ent_codigo_inmetro,
            self.ent_desc_alt,
            self.txt_observacoes,
        ])

        # Botões de Ação com Atalhos padronizados
        bar_btns = ttk.Frame(right)
        bar_btns.pack(fill=tk.X, pady=(4, 0))

        self.btn_inclui = ttk.Button(bar_btns, text="Inclui <F2>", command=self._novo_produto)
        self.btn_inclui.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_grava = ttk.Button(bar_btns, text="Grava <F3>", command=self._salvar_produto)
        self.btn_grava.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_exclui = ttk.Button(bar_btns, text="Exclui <F5>", command=self._excluir_produto)
        self.btn_exclui.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_cancela = ttk.Button(bar_btns, text="Cancela/Limpar <F6>", command=self._limpar_campos)
        self.btn_cancela.pack(side=tk.RIGHT)

    def _configurar_atalhos(self):
        """Associa atalhos de teclado F2, F3, F4, F5, F6 e Alt aos botões."""
        top = self.winfo_toplevel()
        top.bind("<F2>", lambda e: self._novo_produto())
        top.bind("<F3>", lambda e: self._salvar_produto())
        top.bind("<F4>", lambda e: self._abrir_cadastro_grupos())
        top.bind("<F5>", lambda e: self._excluir_produto())
        top.bind("<F6>", lambda e: self._limpar_campos())
        top.bind("<Alt-i>", lambda e: self._novo_produto())
        top.bind("<Alt-I>", lambda e: self._novo_produto())
        top.bind("<Alt-g>", lambda e: self._salvar_produto())
        top.bind("<Alt-G>", lambda e: self._salvar_produto())
        top.bind("<Alt-e>", lambda e: self._excluir_produto())
        top.bind("<Alt-E>", lambda e: self._excluir_produto())
        top.bind("<Alt-c>", lambda e: self._limpar_campos())
        top.bind("<Alt-C>", lambda e: self._limpar_campos())

    def _on_obs_escape(self, event=None):
        sucesso = self._salvar_produto(pedir_confirmacao=True)
        if sucesso:
            self._novo_produto(pedir_confirmacao=True)
        return "break"

    def _abrir_cadastro_grupos(self):
        top = self.winfo_toplevel()
        win = abrir_janela_grupos_produtos(top)
        top.wait_window(win)
        self._carregar_grupos()

    def _abrir_cadastro_marcas(self):
        top = self.winfo_toplevel()
        win = abrir_janela_marcas(top)
        top.wait_window(win)
        self._carregar_marcas()

    def _abrir_seletor_cores(self):
        """Abre modal elegante para selecionar uma ou mais cores para o produto."""
        if not self.service:
            return

        todas_cores = self.service.listar_cores()
        if not todas_cores:
            if messagebox.askyesno("Cores", "Nenhuma cor cadastrada. Deseja abrir o cadastro de cores agora?"):
                top = self.winfo_toplevel()
                win = abrir_janela_cores(top)
                top.wait_window(win)
                todas_cores = self.service.listar_cores()
            if not todas_cores:
                return

        win_cor = tk.Toplevel(self)
        win_cor.title("Selecionar Cores do Produto")
        win_cor.transient(self.winfo_toplevel())
        win_cor.grab_set()
        centralizar_janela(win_cor, self, 420, 450)

        ttk.Label(
            win_cor,
            text="Selecione as Cores do Produto",
            font=("Segoe UI", 11, "bold"),
            foreground="#1E3A8A",
            padding=(10, 10, 10, 5)
        ).pack(anchor=tk.W)

        frame_scroll = ttk.Frame(win_cor, padding=10)
        frame_scroll.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(frame_scroll, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_scroll, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        cods_atuais = {c[0] for c in self._cores_selecionadas}
        checks = {}

        for cod, desc in todas_cores:
            var_chk = tk.BooleanVar(value=(cod in cods_atuais))
            chk = ttk.Checkbutton(
                scrollable_frame,
                text=f"{desc} (Cód: {cod:03d})",
                variable=var_chk
            )
            chk.pack(anchor=tk.W, pady=3, padx=5)
            checks[cod] = (desc, var_chk)

        def _confirmar():
            novas = []
            for cod, (desc, var_chk) in checks.items():
                if var_chk.get():
                    novas.append((cod, desc))
            self._cores_selecionadas = novas
            self._atualizar_display_cores()
            win_cor.destroy()

        f_botoes = ttk.Frame(win_cor, padding=10)
        f_botoes.pack(fill=tk.X)
        ttk.Button(f_botoes, text="Confirmar Seleção", command=_confirmar).pack(side=tk.RIGHT, padx=4)
        ttk.Button(f_botoes, text="Cancelar", command=win_cor.destroy).pack(side=tk.RIGHT, padx=4)

    def _limpar_cores_selecionadas(self):
        self._cores_selecionadas = []
        self._atualizar_display_cores()

    def _atualizar_display_cores(self):
        if not self._cores_selecionadas:
            self.lbl_cores_display.config(text="(Nenhuma cor vinculada)", foreground="#6B7280")
        else:
            nomes = [c[1] for c in self._cores_selecionadas]
            self.lbl_cores_display.config(text=", ".join(nomes), foreground="#1E3A8A")

    def _abrir_diagnostico_schema(self):
        from core.schema_checker import exibir_dialogo_sanidade_schema
        conn = self.service.repo.conn if (self.service and hasattr(self.service, "repo")) else None
        exibir_dialogo_sanidade_schema(self, connection=conn, apenas_se_houver_erro=False)

    # -------------------------------------------------------------------------
    # OPERAÇÕES DE CARGA E DADOS
    # -------------------------------------------------------------------------
    def _carregar_dados_iniciais(self):
        # Alerta preventivo se houver tabelas faltando
        try:
            from core.schema_checker import verificar_sanidade_estoque_produtos, exibir_dialogo_sanidade_schema
            conn = self.service.repo.conn if (self.service and hasattr(self.service, "repo")) else None
            diag = verificar_sanidade_estoque_produtos(conn)
            if not diag.get("todas_ok", True):
                self.after(300, lambda: exibir_dialogo_sanidade_schema(self, connection=conn, apenas_se_houver_erro=True))
        except Exception:
            pass

        self._carregar_grupos()
        self._carregar_marcas()
        self.carregar_produtos()
        self._limpar_campos()

    def _carregar_grupos(self):
        if not self.service:
            return
        grupos = self.service.listar_grupos()
        self._map_grupos = {}
        cbo_form_vals = ["(Nenhum grupo)"]
        cbo_filtro_vals = ["TODOS OS GRUPOS"]

        for g in grupos:
            d = g.display
            self._map_grupos[d] = g.grupocod
            self._map_grupos[str(g.grupocod)] = g.grupocod
            if g.codigo_estruturado:
                self._map_grupos[g.codigo_estruturado] = g.grupocod
            if g.nome_grupo:
                self._map_grupos[g.nome_grupo] = g.grupocod
            cbo_form_vals.append(d)
            cbo_filtro_vals.append(d)

        habilitar_filtro_dinamico_combobox(
            self.cbo_filtro_grupo,
            cbo_filtro_vals,
            callback_selecao=lambda v: self.carregar_produtos(),
        )
        self.cbo_filtro_grupo.set("TODOS OS GRUPOS")

        habilitar_filtro_dinamico_combobox(self.cbo_grupo, cbo_form_vals)
        if not self.cbo_grupo.get():
            self.cbo_grupo.set("(Nenhum grupo)")

    def _carregar_marcas(self):
        if not self.service:
            return
        marcas = self.service.listar_marcas()
        self._map_marcas = {}
        self._marcas_lista_pura = []
        vals = ["(Nenhuma marca)"]
        for cod, desc in marcas:
            desc_limpa = (desc or "").strip().upper()
            display = f"{desc_limpa} ({cod:03d})"
            self._map_marcas[display] = (cod, desc_limpa)
            self._map_marcas[desc_limpa] = (cod, desc_limpa)
            self._map_marcas[str(cod)] = (cod, desc_limpa)
            self._map_marcas[f"{cod:03d}"] = (cod, desc_limpa)
            self._marcas_lista_pura.append((cod, desc_limpa, display))
            vals.append(display)

        habilitar_filtro_dinamico_combobox(
            self.cbo_marca,
            vals,
            callback_ao_nao_encontrar=lambda t: self._verificar_marca_digitada(),
        )
        if not self.var_marca.get():
            self.var_marca.set("(Nenhuma marca)")

    def _resolver_marca_por_termo(self, termo: str) -> Optional[Tuple[int, str, str]]:
        """
        Localiza uma marca cadastrada por código, igualdade exata, prefixo ou substring.
        Retorna (codigo_marca, descricao_marca, display_formatado) ou None.
        """
        import unicodedata

        def norm(s: str) -> str:
            return unicodedata.normalize("NFKD", s or "").encode("ASCII", "ignore").decode("ASCII").lower().strip()

        t = norm(termo)
        if not t or t == norm("(Nenhuma marca)"):
            return None

        # 1. Match exato no mapa (display, descrição, código numérico)
        t_upper = termo.strip().upper()
        if t_upper in self._map_marcas:
            cod, desc = self._map_marcas[t_upper]
            return cod, desc, f"{desc} ({cod:03d})"

        # 2. Busca por código numérico
        if t.isdigit():
            c_int = int(t)
            for cod, desc, disp in getattr(self, "_marcas_lista_pura", []):
                if cod == c_int:
                    return cod, desc, disp

        # 3. Match por descrição exata normalizada
        for cod, desc, disp in getattr(self, "_marcas_lista_pura", []):
            if norm(desc) == t:
                return cod, desc, disp

        # 4. Match por prefixo (descrição inicia com o termo)
        for cod, desc, disp in getattr(self, "_marcas_lista_pura", []):
            if norm(desc).startswith(t):
                return cod, desc, disp

        # 5. Match por substring (termo contido na descrição)
        for cod, desc, disp in getattr(self, "_marcas_lista_pura", []):
            if t in norm(desc):
                return cod, desc, disp

        return None

    def _verificar_marca_digitada(self) -> Tuple[Optional[int], str]:
        """
        Ao digitar uma marca no cadastro de produto:
        1. Resolve se existir por código, nome exato, prefixo ou substring.
        2. Somente se realmente não existir em nenhuma forma, pergunta se deseja incluir.
        """
        texto = self.var_marca.get().strip().upper()
        if not texto or texto == "(NENHUMA MARCA)":
            return None, ""

        # Tenta resolver de forma inteligente
        encontrada = self._resolver_marca_por_termo(texto)
        if encontrada:
            cod, desc, disp = encontrada
            self.var_marca.set(disp)
            return cod, desc

        # Não está cadastrada de nenhuma forma: pergunta se deseja incluir e atribuir código
        if not self.service:
            return None, texto

        resposta = messagebox.askyesno(
            "Incluir Nova Marca",
            f"A marca '{texto}' ainda não existe no cadastro.\n\nDeseja incluí-la e atribuir um código automaticamente?",
            parent=self
        )
        if resposta:
            cod, desc = self.service.obter_ou_criar_marca(texto)
            self._carregar_marcas()
            disp = f"{desc} ({cod:03d})"
            self.var_marca.set(disp)
            return cod, desc
        else:
            self.var_marca.set("(Nenhuma marca)")
            return None, ""

    def carregar_produtos(self):
        """Carrega e atualiza a grade de produtos e o contador total."""
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)

        if not self.service:
            return

        filtro = self.var_filtro.get().strip().upper()
        grupo_sel = self.cbo_filtro_grupo.get().strip()
        grupocod = None
        if grupo_sel and grupo_sel != "TODOS OS GRUPOS":
            grupocod = self._map_grupos.get(grupo_sel)

        produtos = self.service.listar_produtos(filtro=filtro, grupocod=grupocod)
        for p in produtos:
            # Obtém cores se não carregadas
            cores_txt = p.display_cores
            unid_txt = p.unidade_medida or p.tamanho or "-"
            self.tree_produtos.insert(
                "",
                tk.END,
                values=(
                    p.prodcod,
                    p.prodnome,
                    p.nome_marca or "(Sem marca)",
                    p.nome_grupo or "(Sem grupo)",
                    unid_txt,
                    p.codigo_inmetro or "-",
                    cores_txt,
                    p.descricao_alternativa or "",
                )
            )

        total = self.service.contar_produtos()
        self.lbl_num_produtos.config(text=str(total))

    def _limpar_filtro(self):
        self.var_filtro.set("")
        self.cbo_filtro_grupo.set("TODOS OS GRUPOS")
        self.carregar_produtos()

    def _ao_selecionar_produto(self, event=None):
        sel = self.tree_produtos.selection()
        if not sel or not self.service:
            return
        cod_val = self.tree_produtos.item(sel[0], "values")[0]
        try:
            cod_int = int(cod_val)
        except ValueError:
            return

        p = self.service.obter_produto(cod_int)
        if not p:
            return

        self.ent_prodcod.delete(0, tk.END)
        self.ent_prodcod.insert(0, str(p.prodcod))

        self.var_prodnome.set(p.prodnome)

        # Unidade de Medida
        unid = p.unidade_medida or p.tamanho or "UN"
        unid_display = unid
        for opt in self.cbo_unidade["values"]:
            if opt.startswith(f"{unid} - ") or opt == unid:
                unid_display = opt
                break
        self.var_unidade.set(unid_display)

        self.var_codigo_inmetro.set(p.codigo_inmetro or "")
        self.var_desc_alt.set(p.descricao_alternativa)

        # Marca
        if p.nome_marca:
            display_marca = None
            if p.codigo_marca:
                display_marca = f"{p.nome_marca} ({p.codigo_marca:03d})"
            else:
                encontrada = self._resolver_marca_por_termo(p.nome_marca)
                if encontrada:
                    display_marca = encontrada[2]
            self.var_marca.set(display_marca or p.nome_marca)
        else:
            self.var_marca.set("(Nenhuma marca)")

        # Cores
        self._cores_selecionadas = list(zip(p.cores_codigos, p.cores_nomes))
        self._atualizar_display_cores()

        self.txt_observacoes.delete("1.0", tk.END)
        self.txt_observacoes.insert("1.0", p.observacoes.upper() if p.observacoes else "")

        # Grupo
        grupo_encontrado = False
        if p.grupocod:
            for display_nome, g_cod in self._map_grupos.items():
                if g_cod == p.grupocod:
                    self.cbo_grupo.set(display_nome)
                    grupo_encontrado = True
                    break
        if not grupo_encontrado:
            self.cbo_grupo.set("(Nenhum grupo)")

        self._carregar_almoxarifados_do_produto(p.prodcod)

    def _atualizar_display_almoxarifados(self):
        if not getattr(self, "_almoxarifados_vinculados", []):
            self.lbl_almox_display.config(text="(Nenhum almoxarifado vinculado - padrão Geral)", foreground="#6B7280")
            return
        itens_str = []
        for a in self._almoxarifados_vinculados:
            cod = a.get("codigo_almoxarifado", "")
            nome = a.get("nome_almoxarifado", "")
            saldo = float(a.get("saldo_atual") or 0.0)
            itens_str.append(f"{cod} - {nome} (Saldo: {saldo:.2f})")
        self.lbl_almox_display.config(text=" | ".join(itens_str), foreground="#047857")

    def _carregar_almoxarifados_do_produto(self, prodcod: int):
        try:
            from estoque.almoxarifados_repository import AlmoxarifadosRepository
            repo = AlmoxarifadosRepository()
            self._almoxarifados_vinculados = repo.listar_almoxarifados_produto(prodcod)
            self._atualizar_display_almoxarifados()
        except Exception:
            self._almoxarifados_vinculados = []
            self._atualizar_display_almoxarifados()

    def _abrir_seletor_almoxarifados(self):
        cod_str = self.ent_prodcod.get().strip()
        if not cod_str or not cod_str.isdigit():
            messagebox.showwarning("Aviso", "Selecione ou salve um produto antes de gerenciar seus almoxarifados.", parent=self)
            return

        prodcod = int(cod_str)
        nome_prod = self.var_prodnome.get().strip()

        modal = tk.Toplevel(self)
        modal.title(f"Almoxarifados do Produto: {prodcod} - {nome_prod}")
        modal.transient(self)
        modal.grab_set()
        centralizar_janela(modal, self, 780, 500)

        f_cont = ttk.Frame(modal, padding=12)
        f_cont.pack(fill=tk.BOTH, expand=True)

        lbl_top = ttk.Label(
            f_cont,
            text=f"Vínculo Multi-Almoxarifado & Saldos: {prodcod} - {nome_prod}",
            font=("Segoe UI", 11, "bold"),
            foreground="#1E3A8A",
        )
        lbl_top.pack(anchor=tk.W, pady=(0, 10))

        cols = ("cod", "nome", "vinculado", "saldo", "ult_mov")
        tree = ttk.Treeview(f_cont, columns=cols, show="headings", height=10, selectmode="browse")
        tree.heading("cod", text="Cód. Almoxarifado")
        tree.heading("nome", text="Descrição do Almoxarifado")
        tree.heading("vinculado", text="Status Vínculo")
        tree.heading("saldo", text="Saldo no Local")
        tree.heading("ult_mov", text="Última Movimentação")

        tree.column("cod", width=110, anchor=tk.CENTER)
        tree.column("nome", width=260, anchor=tk.W)
        tree.column("vinculado", width=110, anchor=tk.CENTER)
        tree.column("saldo", width=100, anchor=tk.E)
        tree.column("ult_mov", width=140, anchor=tk.CENTER)

        sb = ttk.Scrollbar(f_cont, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        from estoque.almoxarifados_repository import AlmoxarifadosRepository
        repo = AlmoxarifadosRepository()

        def recarregar_grade():
            for it in tree.get_children():
                tree.delete(it)
            todos_almox = repo.listar_almoxarifados()
            vinculados = {v["codigo_almoxarifado"]: v for v in repo.listar_almoxarifados_produto(prodcod)}
            for a in todos_almox:
                cod = a["codigo_almoxarifado"]
                desc = a["descricao"]
                if cod in vinculados:
                    v = vinculados[cod]
                    st = "✔ VINCULADO"
                    saldo = f"{float(v.get('saldo_atual') or 0.0):.2f}"
                    dt_mov = str(v.get("data_ultima_movimentacao") or "-")
                else:
                    st = "NÃO VINCULADO"
                    saldo = "0.00"
                    dt_mov = "-"
                tree.insert("", tk.END, iid=cod, values=(cod, desc, st, saldo, dt_mov))

        f_acoes = ttk.Frame(f_cont)
        f_acoes.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

        def vincular():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione um almoxarifado para vincular.", parent=modal)
                return
            cod_a = sel[0]
            try:
                repo.vincular_produto(cod_a, prodcod)
                recarregar_grade()
                self._carregar_almoxarifados_do_produto(prodcod)
            except Exception as ex:
                messagebox.showerror("Erro", f"Falha ao vincular almoxarifado: {ex}", parent=modal)

        def desvincular():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione um almoxarifado para desvincular.", parent=modal)
                return
            cod_a = sel[0]
            try:
                repo.desvincular_produto(cod_a, prodcod)
                recarregar_grade()
                self._carregar_almoxarifados_do_produto(prodcod)
            except Exception as ex:
                messagebox.showerror("Aviso", str(ex), parent=modal)

        btn_vinc = ttk.Button(f_acoes, text="✔ Vincular Almoxarifado", command=vincular)
        btn_vinc.pack(side=tk.LEFT, padx=(0, 6))

        btn_desv = ttk.Button(f_acoes, text="✖ Desvincular Almoxarifado", command=desvincular)
        btn_desv.pack(side=tk.LEFT, padx=(0, 6))

        btn_fechar = ttk.Button(f_acoes, text="Concluir / Fechar (Esc)", command=modal.destroy)
        btn_fechar.pack(side=tk.RIGHT)
        modal.bind("<Escape>", lambda e: modal.destroy())

        recarregar_grade()

    def _limpar_campos(self):
        """Limpa todos os campos para novo cadastro ou cancelamento."""
        self.ent_prodcod.delete(0, tk.END)
        self.var_prodnome.set("")
        self.var_marca.set("(Nenhuma marca)")
        self.var_unidade.set("UN - UNIDADE")
        self.var_codigo_inmetro.set("")
        self.var_desc_alt.set("")
        self._limpar_cores_selecionadas()
        self._almoxarifados_vinculados = []
        self._atualizar_display_almoxarifados()
        self.txt_observacoes.delete("1.0", tk.END)
        self.cbo_grupo.set("(Nenhum grupo)")
        if self.tree_produtos.selection():
            self.tree_produtos.selection_remove(self.tree_produtos.selection())
        self.ent_prodnome.focus_set()

    def _novo_produto(self, pedir_confirmacao=True):
        if pedir_confirmacao:
            if not messagebox.askyesno("Confirmação", "Confirma a inclusão do produto?", parent=self):
                return

        self._limpar_campos()
        if self.service:
            top = self.winfo_toplevel()
            empresa = getattr(top, "empresa_ativa", "1.01")
            prox = self.service.gerar_codigo_configcod(tabela="USER_geoapolo_produtos", empresa=empresa)
            self.ent_prodcod.insert(0, str(prox))
        self.ent_prodnome.focus_set()

    def _salvar_produto(self, pedir_confirmacao=True) -> bool:
        if not self.service:
            return False

        try:
            cod_val = int(self.ent_prodcod.get().strip() or 0)
        except ValueError:
            cod_val = 0

        nome = self.var_prodnome.get().strip().upper()
        if not nome:
            messagebox.showwarning("Aviso", "A descrição do produto é obrigatória.", parent=self)
            self.ent_prodnome.focus_set()
            return False

        # Valida/inclui marca caso digitada
        cod_marca, nome_marca = self._verificar_marca_digitada()

        if pedir_confirmacao:
            if not messagebox.askyesno(
                "Confirmação",
                "Confirma a gravação dos dados do produto?",
                parent=self
            ):
                return False

        grupo_sel = self.cbo_grupo.get().strip()
        grupocod = None
        if grupo_sel and grupo_sel != "(Nenhum grupo)":
            if grupo_sel in self._map_grupos:
                grupocod = self._map_grupos[grupo_sel]
            else:
                for k, v in self._map_grupos.items():
                    if k.startswith(grupo_sel) or grupo_sel in k:
                        grupocod = v
                        break

        obs_texto = self.txt_observacoes.get("1.0", tk.END).strip().upper()

        cores_codigos = [c[0] for c in self._cores_selecionadas]
        cores_nomes = [c[1] for c in self._cores_selecionadas]

        dto = ProdutoDTO(
            prodcod=cod_val,
            prodnome=nome,
            descricao_alternativa=self.var_desc_alt.get().strip().upper(),
            grupocod=grupocod,
            codigo_marca=cod_marca,
            nome_marca=nome_marca,
            cores_codigos=cores_codigos,
            cores_nomes=cores_nomes,
            unidade_medida=self.var_unidade.get().strip().upper(),
            tamanho=self.var_unidade.get().strip().upper(),
            codigo_inmetro=self.var_codigo_inmetro.get().strip().upper(),
            codigo_lote="",
            observacoes=obs_texto,
        )

        res = self.service.salvar_produto(dto)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem, parent=self)
            self.carregar_produtos()
            for item in self.tree_produtos.get_children():
                if str(self.tree_produtos.item(item, "values")[0]) == str(res.codigo):
                    self.tree_produtos.selection_set(item)
                    self.tree_produtos.see(item)
                    break
            return True
        else:
            messagebox.showerror("Erro ao Gravar", res.mensagem, parent=self)
            return False

    def _excluir_produto(self):
        if not self.service:
            return

        try:
            cod_val = int(self.ent_prodcod.get().strip() or 0)
        except ValueError:
            cod_val = 0

        if cod_val <= 0:
            messagebox.showwarning("Aviso", "Selecione um produto cadastrado para exclusão.", parent=self)
            return

        nome = self.var_prodnome.get().strip().upper()
        if not messagebox.askyesno(
            "Confirmação de Exclusão",
            f"Confirma a remoção do produto?\n\nCódigo: {cod_val}\nDescrição: {nome}\n\nEsta operação não poderá ser desfeita.",
            parent=self
        ):
            return

        res = self.service.excluir_produto(cod_val)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem, parent=self)
            self.carregar_produtos()
            self._limpar_campos()
        else:
            messagebox.showerror("Erro ao Excluir", res.mensagem, parent=self)


def abrir_janela_produtos(parent, connection=None):
    """Abre a tela de cadastro e manutenção de produtos em TopLevel centralizada."""
    win = tk.Toplevel(parent)
    win.title("Cadastro de Produtos - GeoAlvo")
    win.minsize(920, 520)
    centralizar_janela(win, parent, 1100, 660)
    view = ProdutosView(win, connection=connection)
    view.pack(fill=tk.BOTH, expand=True)
    return win
