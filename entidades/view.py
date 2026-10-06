"""
Interface Gráfica em Python (Tkinter / ttk) para Gestão e Integração de Entidades.
Layout corporativo e profissional alinhado aos padrões visuais do sistema GeoAlvo.
Correspondente e evolução de unt_entidades.pas (Tfrmentidades).
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from pathlib import Path

# Garante que o diretório raiz esteja no sys.path
_raiz_projeto = str(Path(__file__).resolve().parent.parent)
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

import logging
from typing import Optional, List, Dict, Any, Tuple


class DlgCredenciaisAlvo(tk.Toplevel):
    """
    Diálogo modal para captura do Usuário e Senha de acesso ao sistema Alvo.
    Equivalente a InputBox e SolicitarSenhaMascarada em unt_entidades.pas do Delphi.
    """

    def __init__(self, parent, usuario_padrao: str = ""):
        super().__init__(parent)
        self.title("Credenciais do Usuário Alvo")
        self.geometry("380x210")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.resultado: Optional[Tuple[str, str]] = None

        container = ttk.Frame(self, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            container,
            text="Informe as credenciais de acesso ao Alvo:",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(container, text="Usuário Alvo:").pack(anchor=tk.W)
        self.ent_usuario = ttk.Entry(container)
        self.ent_usuario.pack(fill=tk.X, pady=(2, 8))
        if usuario_padrao:
            self.ent_usuario.insert(0, usuario_padrao)

        ttk.Label(container, text="Senha Alvo:").pack(anchor=tk.W)
        self.ent_senha = ttk.Entry(container, show="*")
        self.ent_senha.pack(fill=tk.X, pady=(2, 14))

        btn_box = ttk.Frame(container)
        btn_box.pack(fill=tk.X)

        ttk.Button(btn_box, text="Confirmar", command=self._confirmar).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_box, text="Cancelar", command=self.destroy).pack(side=tk.RIGHT, padx=4)

        self.bind("<Return>", lambda e: self._confirmar())
        self.bind("<Escape>", lambda e: self.destroy())

        self.update_idletasks()
        try:
            px = parent.winfo_rootx() + (parent.winfo_width() // 2) - 190
            py = parent.winfo_rooty() + (parent.winfo_height() // 2) - 105
            self.geometry(f"+{max(0, px)}+{max(0, py)}")
        except Exception:
            pass

        if usuario_padrao:
            self.ent_senha.focus_set()
        else:
            self.ent_usuario.focus_set()

        self.wait_window()

    def _confirmar(self):
        usu = self.ent_usuario.get().strip().upper()
        pwd = self.ent_senha.get().strip()
        if not usu or not pwd:
            messagebox.showwarning("Aviso", "Informe usuário e senha para continuar.", parent=self)
            return
        self.resultado = (usu, pwd)
        self.destroy()


try:
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
except (ImportError, ModuleNotFoundError):
    from models import (
        EntidadeFiltro,
        ItemComparacao,
        DecisaoLinha,
        ResultadoOperacao,
    )
    from repository import EntidadeRepository
    from service import EntidadeService
    from api_client import AlvoAPIClient
    from database import obter_conexao_banco

logger = logging.getLogger(__name__)

from core.error_logger import salvar_log_erro_executavel

MAPA_CAMPOS_BUSCA_UI = {
    "Razão Social / Nome": "entnome",
    "Nome Fantasia": "entnomefant",
    "CPF / CNPJ": "EntCpfCgc",
    "RG / Inscrição Estadual": "EntRgIe",
    "Endereço / Logradouro": "entender",
    "Número": "entenderno",
    "Complemento": "entendercomp",
    "Bairro": "entbair",
    "Cidade": "cidnomecomp",
    "UF / Estado": "ufsigla",
    "CEP": "entcep",
    "Código GeoApolo": "geoentcod",
    "entcod": "entcod",
    "Código Alvo": "entcod",
    "Tipo Pessoa (F/J)": "enttipofj",
    "Gênero": "entgenero",
    "Estado Civil": "EntEstCivil",
    "Cargo": "cargonome",
    "Escolaridade": "EntGrauEscol",
    "Diocese": "USERNomeDiocese",
    "Categoria(s)": "categnome",
    "Origem": "OrigNome",
    "Observações": "Entobservacoes",
}

MAPA_ORDEM_UI = {
    "Razão Social / Nome": "entnome",
    "Código GeoApolo": "geoentcod",
    "entcod": "entcod",
    "Código Alvo": "entcod",
    "Data de Cadastro": "entdatacad",
    "Cidade": "cidnomecomp",
    "Bairro": "entbair",
    "CPF / CNPJ": "EntCpfCgc",
    "Categoria": "categnome",
}


class EntidadesView(tk.Toplevel):
    """Janela principal de Gestão de Entidades do GeoAlvo."""
    _instancia_ativa = None

    def __new__(cls, *args, **kwargs):
        if cls._instancia_ativa is not None and cls._instancia_ativa.winfo_exists():
            try:
                cls._instancia_ativa.deiconify()
                cls._instancia_ativa.lift()
                cls._instancia_ativa.focus_force()
            except Exception:
                pass
            return cls._instancia_ativa
        return super().__new__(cls)

    def __init__(self, parent=None, connection=None):
        if getattr(self, "_ja_inicializada", False):
            return
        super().__init__(parent)
        self._ja_inicializada = True
        EntidadesView._instancia_ativa = self
        self.title("Gestão e Integração de Entidades - GeoAlvo")
        self.geometry("1160x680")
        self.minsize(950, 560)

        # Centraliza a janela
        self._centralizar_janela(1160, 680)

        # Ícone da aplicação
        self._aplicar_icone()

        # Inicializa dependências
        self._conn = connection
        self._criou_conexao = False
        if self._conn is None:
            try:
                self._conn = obter_conexao_banco()
                self._criou_conexao = True
                if self._conn:
                    self._conn.timeout = 0
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
        self._carregando_mais = False
        self._fim_dos_registros = False
        self._ultima_pesquisa_especifica = False

        self._configurar_estilos()
        self._criar_interface()
        # Carrega dados após renderizar a janela (não congela abertura)
        self._after_id = self.after(50, self._executar_carga_inicial)

        # Atalhos de Teclado
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<F5>", lambda e: self._carregar_dados())
        self.bind("<Insert>", lambda e: self._novo_registro())

    def _executar_carga_inicial(self):
        self._after_id = None
        try:
            if self.winfo_exists():
                self._carregar_dados()
        except Exception:
            pass

    def _centralizar_janela(self, largura: int, altura: int):
        from core import centralizar_janela
        centralizar_janela(self, getattr(self, "master", None), largura, altura)

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
        self.combo_base.bind("<<ComboboxSelected>>", self._on_mudar_base)

        ttk.Label(row1, text="Campo de Busca:").pack(side=tk.LEFT, padx=(0, 5))
        self.combo_campo = ttk.Combobox(
            row1,
            values=[k for k in MAPA_CAMPOS_BUSCA_UI.keys() if k != "Código Alvo"],
            state="readonly",
            width=23,
        )
        self.combo_campo.set("Razão Social / Nome")
        self.combo_campo.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(row1, text="Procurar por:").pack(side=tk.LEFT, padx=(0, 5))
        self.entry_busca = ttk.Entry(row1, width=28, font=("Segoe UI", 9))
        self.entry_busca.pack(side=tk.LEFT, padx=(0, 8))
        self.entry_busca.bind("<Return>", lambda e: self._carregar_dados(especifica=True))

        def _forcar_upper_busca(event):
            if event.keysym in ("Left", "Right", "Up", "Down", "Home", "End", "Tab", "Return", "Escape", "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Caps_Lock"):
                return
            try:
                pos = self.entry_busca.index(tk.INSERT)
                txt = self.entry_busca.get()
                txt_u = txt.upper()
                if txt != txt_u:
                    self.entry_busca.delete(0, tk.END)
                    self.entry_busca.insert(0, txt_u)
                    self.entry_busca.icursor(pos)
            except Exception:
                pass
        self.entry_busca.bind("<KeyRelease>", _forcar_upper_busca, add="+")

        btn_buscar = ttk.Button(row1, text="🔍 Buscar", command=lambda: self._carregar_dados(especifica=True))
        btn_buscar.pack(side=tk.LEFT, padx=3)

        btn_limpar = ttk.Button(row1, text="✖ Limpar", command=self._limpar_busca)
        btn_limpar.pack(side=tk.LEFT, padx=3)

        btn_novo = ttk.Button(row1, text="➕ Novo (Ins)", command=self._novo_registro)
        btn_novo.pack(side=tk.LEFT, padx=(12, 3))

        # Linha 2: Categoria, Ordenação e Filtros Especiais
        row2 = ttk.Frame(filtro_container)
        row2.pack(fill=tk.X, pady=(6, 2))

        ttk.Label(row2, text="Categoria:").pack(side=tk.LEFT, padx=(0, 5))
        self.combo_categoria = ttk.Combobox(row2, state="readonly", width=22)
        self.combo_categoria.pack(side=tk.LEFT, padx=(0, 15))
        self.combo_categoria.bind("<<ComboboxSelected>>", lambda e: self._carregar_dados())
        self._atualizar_lookup_categorias()

        ttk.Label(row2, text="Ordenar por:").pack(side=tk.LEFT, padx=(0, 5))
        self.combo_ordem = ttk.Combobox(
            row2,
            values=[k for k in MAPA_ORDEM_UI.keys() if k != "Código Alvo"],
            state="readonly",
            width=21,
        )
        self.combo_ordem.set("Razão Social / Nome")
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
            "cod_geo",
            "entcod",
            "nome",
            "nome_fantasia",
            "documento",
            "tipo_doc",
            "rg_ie",
            "tipo_fj",
            "tratamento",
            "desde_data",
            "data_cad",
            "logradouro",
            "endereco",
            "numero",
            "complemento",
            "bairro",
            "cidade_cod",
            "cidade",
            "uf",
            "cep",
            "cx_postal",
            "ref_ender",
            "regiao",
            "conceito",
            "data_nasc",
            "cargo_cod",
            "cargo",
            "genero",
            "estado_civil",
            "nome_pai",
            "nome_mae",
            "possui_filho",
            "num_filhos",
            "mora_com",
            "cod_escolaridade",
            "escolaridade",
            "falecido",
            "ativ_econ",
            "orig_cod",
            "origem",
            "categ_cod",
            "categoria",
            "tipo_cob_cod",
            "tipo_cob_nome",
            "bco_num",
            "bco_nome",
            "ag_num",
            "ag_nome",
            "conta",
            "dia_contrib",
            "gerar_carne",
            "diocese_id",
            "diocese",
            "recebe_lembrete",
            "val_contrib",
            "cid_apolo",
            "loc_cobranca",
            "loc_entrega",
            "transporte",
            "atualizou",
            "usu_atualizou",
            "observacoes",
        )
        tree_scroll_y = ttk.Scrollbar(grid_container, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(grid_container, orient=tk.HORIZONTAL)

        def _on_tree_yscroll(*args):
            tree_scroll_y.set(*args)
            try:
                if len(args) >= 2:
                    bottom = float(args[1])
                    if bottom >= 0.88:
                        self.after_idle(self._checar_carregar_mais)
            except Exception:
                pass

        self.tree = ttk.Treeview(
            grid_container,
            columns=colunas,
            show="headings",
            selectmode="browse",
            style="Entidades.Treeview",
            yscrollcommand=_on_tree_yscroll,
            xscrollcommand=tree_scroll_x.set,
        )
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        # Cabeçalhos do Treeview
        self.tree.heading("cod_geo", text="Cód. Geo", command=lambda: self._ordenar_coluna("cod_geo"))
        self.tree.heading("entcod", text="entcod", command=lambda: self._ordenar_coluna("entcod"))
        self.tree.heading("nome", text="Razão Social / Nome", command=lambda: self._ordenar_coluna("nome"))
        self.tree.heading("nome_fantasia", text="Nome Fantasia", command=lambda: self._ordenar_coluna("nome_fantasia"))
        self.tree.heading("documento", text="CPF / CNPJ", command=lambda: self._ordenar_coluna("documento"))
        self.tree.heading("tipo_doc", text="Tipo Doc.", command=lambda: self._ordenar_coluna("tipo_doc"))
        self.tree.heading("rg_ie", text="RG / IE", command=lambda: self._ordenar_coluna("rg_ie"))
        self.tree.heading("tipo_fj", text="F/J", command=lambda: self._ordenar_coluna("tipo_fj"))
        self.tree.heading("tratamento", text="Tratamento", command=lambda: self._ordenar_coluna("tratamento"))
        self.tree.heading("desde_data", text="Desde Data", command=lambda: self._ordenar_coluna("desde_data"))
        self.tree.heading("data_cad", text="Data Cadastro", command=lambda: self._ordenar_coluna("data_cad"))
        self.tree.heading("logradouro", text="Tipo Logradouro", command=lambda: self._ordenar_coluna("logradouro"))
        self.tree.heading("endereco", text="Endereço", command=lambda: self._ordenar_coluna("endereco"))
        self.tree.heading("numero", text="Nº", command=lambda: self._ordenar_coluna("numero"))
        self.tree.heading("complemento", text="Compl.", command=lambda: self._ordenar_coluna("complemento"))
        self.tree.heading("bairro", text="Bairro", command=lambda: self._ordenar_coluna("bairro"))
        self.tree.heading("cidade_cod", text="Cód. Cidade", command=lambda: self._ordenar_coluna("cidade_cod"))
        self.tree.heading("cidade", text="Cidade", command=lambda: self._ordenar_coluna("cidade"))
        self.tree.heading("uf", text="UF", command=lambda: self._ordenar_coluna("uf"))
        self.tree.heading("cep", text="CEP", command=lambda: self._ordenar_coluna("cep"))
        self.tree.heading("cx_postal", text="Cx. Postal", command=lambda: self._ordenar_coluna("cx_postal"))
        self.tree.heading("ref_ender", text="Ref. Endereço", command=lambda: self._ordenar_coluna("ref_ender"))
        self.tree.heading("regiao", text="Região", command=lambda: self._ordenar_coluna("regiao"))
        self.tree.heading("conceito", text="Conceito", command=lambda: self._ordenar_coluna("conceito"))
        self.tree.heading("data_nasc", text="Data Nasc./Fund.", command=lambda: self._ordenar_coluna("data_nasc"))
        self.tree.heading("cargo_cod", text="Cód. Cargo", command=lambda: self._ordenar_coluna("cargo_cod"))
        self.tree.heading("cargo", text="Cargo", command=lambda: self._ordenar_coluna("cargo"))
        self.tree.heading("genero", text="Gênero", command=lambda: self._ordenar_coluna("genero"))
        self.tree.heading("estado_civil", text="Estado Civil", command=lambda: self._ordenar_coluna("estado_civil"))
        self.tree.heading("nome_pai", text="Nome do Pai", command=lambda: self._ordenar_coluna("nome_pai"))
        self.tree.heading("nome_mae", text="Nome da Mãe", command=lambda: self._ordenar_coluna("nome_mae"))
        self.tree.heading("possui_filho", text="Filhos?", command=lambda: self._ordenar_coluna("possui_filho"))
        self.tree.heading("num_filhos", text="Qtd. Filhos", command=lambda: self._ordenar_coluna("num_filhos"))
        self.tree.heading("mora_com", text="Mora Com", command=lambda: self._ordenar_coluna("mora_com"))
        self.tree.heading("cod_escolaridade", text="Cód. Escol.", command=lambda: self._ordenar_coluna("cod_escolaridade"))
        self.tree.heading("escolaridade", text="Escolaridade", command=lambda: self._ordenar_coluna("escolaridade"))
        self.tree.heading("falecido", text="Falecido", command=lambda: self._ordenar_coluna("falecido"))
        self.tree.heading("ativ_econ", text="Atividade Econômica", command=lambda: self._ordenar_coluna("ativ_econ"))
        self.tree.heading("orig_cod", text="Cód. Origem", command=lambda: self._ordenar_coluna("orig_cod"))
        self.tree.heading("origem", text="Origem", command=lambda: self._ordenar_coluna("origem"))
        self.tree.heading("categ_cod", text="Cód. Categorias", command=lambda: self._ordenar_coluna("categ_cod"))
        self.tree.heading("categoria", text="Categoria(s)", command=lambda: self._ordenar_coluna("categoria"))
        self.tree.heading("tipo_cob_cod", text="Cód. Cobrança", command=lambda: self._ordenar_coluna("tipo_cob_cod"))
        self.tree.heading("tipo_cob_nome", text="Tipo Cobrança", command=lambda: self._ordenar_coluna("tipo_cob_nome"))
        self.tree.heading("bco_num", text="Nº Banco", command=lambda: self._ordenar_coluna("bco_num"))
        self.tree.heading("bco_nome", text="Banco", command=lambda: self._ordenar_coluna("bco_nome"))
        self.tree.heading("ag_num", text="Nº Agência", command=lambda: self._ordenar_coluna("ag_num"))
        self.tree.heading("ag_nome", text="Agência", command=lambda: self._ordenar_coluna("ag_nome"))
        self.tree.heading("conta", text="Conta Corrente", command=lambda: self._ordenar_coluna("conta"))
        self.tree.heading("dia_contrib", text="Dia Débito", command=lambda: self._ordenar_coluna("dia_contrib"))
        self.tree.heading("gerar_carne", text="Gerar Carnê", command=lambda: self._ordenar_coluna("gerar_carne"))
        self.tree.heading("diocese_id", text="ID Diocese", command=lambda: self._ordenar_coluna("diocese_id"))
        self.tree.heading("diocese", text="Diocese", command=lambda: self._ordenar_coluna("diocese"))
        self.tree.heading("recebe_lembrete", text="Recebe Lembrete", command=lambda: self._ordenar_coluna("recebe_lembrete"))
        self.tree.heading("val_contrib", text="Valor Contribuição", command=lambda: self._ordenar_coluna("val_contrib"))
        self.tree.heading("cid_apolo", text="Cód. Cid Apolo", command=lambda: self._ordenar_coluna("cid_apolo"))
        self.tree.heading("loc_cobranca", text="Cobr. Mesmo End.", command=lambda: self._ordenar_coluna("loc_cobranca"))
        self.tree.heading("loc_entrega", text="Entr. Mesmo End.", command=lambda: self._ordenar_coluna("loc_entrega"))
        self.tree.heading("transporte", text="Transp. Mesmo", command=lambda: self._ordenar_coluna("transporte"))
        self.tree.heading("atualizou", text="Sincronizado", command=lambda: self._ordenar_coluna("atualizou"))
        self.tree.heading("usu_atualizou", text="Usuário Sinc.", command=lambda: self._ordenar_coluna("usu_atualizou"))
        self.tree.heading("observacoes", text="Observações / Motivo", command=lambda: self._ordenar_coluna("observacoes"))

        # Larguras e alinhamentos das colunas
        self.tree.column("cod_geo", width=75, anchor=tk.CENTER)
        self.tree.column("entcod", width=75, anchor=tk.CENTER)
        self.tree.column("nome", width=220, anchor=tk.W)
        self.tree.column("nome_fantasia", width=180, anchor=tk.W)
        self.tree.column("documento", width=120, anchor=tk.CENTER)
        self.tree.column("tipo_doc", width=80, anchor=tk.CENTER)
        self.tree.column("rg_ie", width=100, anchor=tk.CENTER)
        self.tree.column("tipo_fj", width=45, anchor=tk.CENTER)
        self.tree.column("tratamento", width=85, anchor=tk.CENTER)
        self.tree.column("desde_data", width=90, anchor=tk.CENTER)
        self.tree.column("data_cad", width=95, anchor=tk.CENTER)
        self.tree.column("logradouro", width=80, anchor=tk.W)
        self.tree.column("endereco", width=190, anchor=tk.W)
        self.tree.column("numero", width=60, anchor=tk.CENTER)
        self.tree.column("complemento", width=90, anchor=tk.W)
        self.tree.column("bairro", width=120, anchor=tk.W)
        self.tree.column("cidade_cod", width=70, anchor=tk.CENTER)
        self.tree.column("cidade", width=130, anchor=tk.W)
        self.tree.column("uf", width=45, anchor=tk.CENTER)
        self.tree.column("cep", width=85, anchor=tk.CENTER)
        self.tree.column("cx_postal", width=80, anchor=tk.CENTER)
        self.tree.column("ref_ender", width=120, anchor=tk.W)
        self.tree.column("regiao", width=100, anchor=tk.W)
        self.tree.column("conceito", width=80, anchor=tk.CENTER)
        self.tree.column("data_nasc", width=95, anchor=tk.CENTER)
        self.tree.column("cargo_cod", width=80, anchor=tk.CENTER)
        self.tree.column("cargo", width=120, anchor=tk.W)
        self.tree.column("genero", width=60, anchor=tk.CENTER)
        self.tree.column("estado_civil", width=90, anchor=tk.W)
        self.tree.column("nome_pai", width=150, anchor=tk.W)
        self.tree.column("nome_mae", width=150, anchor=tk.W)
        self.tree.column("possui_filho", width=60, anchor=tk.CENTER)
        self.tree.column("num_filhos", width=65, anchor=tk.CENTER)
        self.tree.column("mora_com", width=80, anchor=tk.W)
        self.tree.column("cod_escolaridade", width=75, anchor=tk.CENTER)
        self.tree.column("escolaridade", width=120, anchor=tk.W)
        self.tree.column("falecido", width=60, anchor=tk.CENTER)
        self.tree.column("ativ_econ", width=130, anchor=tk.W)
        self.tree.column("orig_cod", width=80, anchor=tk.CENTER)
        self.tree.column("origem", width=120, anchor=tk.W)
        self.tree.column("categ_cod", width=110, anchor=tk.W)
        self.tree.column("categoria", width=160, anchor=tk.W)
        self.tree.column("tipo_cob_cod", width=80, anchor=tk.CENTER)
        self.tree.column("tipo_cob_nome", width=130, anchor=tk.W)
        self.tree.column("bco_num", width=65, anchor=tk.CENTER)
        self.tree.column("bco_nome", width=100, anchor=tk.W)
        self.tree.column("ag_num", width=70, anchor=tk.CENTER)
        self.tree.column("ag_nome", width=100, anchor=tk.W)
        self.tree.column("conta", width=90, anchor=tk.CENTER)
        self.tree.column("dia_contrib", width=75, anchor=tk.CENTER)
        self.tree.column("gerar_carne", width=60, anchor=tk.CENTER)
        self.tree.column("diocese_id", width=75, anchor=tk.CENTER)
        self.tree.column("diocese", width=140, anchor=tk.W)
        self.tree.column("recebe_lembrete", width=70, anchor=tk.CENTER)
        self.tree.column("val_contrib", width=95, anchor=tk.E)
        self.tree.column("cid_apolo", width=80, anchor=tk.CENTER)
        self.tree.column("loc_cobranca", width=80, anchor=tk.CENTER)
        self.tree.column("loc_entrega", width=80, anchor=tk.CENTER)
        self.tree.column("transporte", width=80, anchor=tk.CENTER)
        self.tree.column("atualizou", width=100, anchor=tk.CENTER)
        self.tree.column("usu_atualizou", width=100, anchor=tk.W)
        self.tree.column("observacoes", width=180, anchor=tk.W)

        # Layout com grid para manter as barras de rolagem sempre visíveis
        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_y.grid(row=0, column=1, sticky="ns")
        tree_scroll_x.grid(row=1, column=0, sticky="ew")

        grid_container.rowconfigure(0, weight=1)
        grid_container.columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Insert>", lambda e: self._novo_registro())
        self.tree.bind("<KeyRelease>", self._on_tree_key_release, add="+")
        self.tree.bind("<MouseWheel>", self._on_tree_mousewheel, add="+")

        # Tags visuais
        self.tree.tag_configure("par", background="#FFFFFF")
        self.tree.tag_configure("impar", background="#F7FAFC")
        self.tree.tag_configure("sincronizado", foreground="#1D4ED8")
        self.tree.tag_configure("pendente_geoapolo", foreground="#DC2626", background="#FEE2E2")
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

        self.btn_exportar_filtro = ttk.Button(
            btn_box, text="⚡ Exporta Filtro para o Alvo", command=self._acao_exportar_filtro
        )
        self.btn_exportar_filtro.pack(side=tk.LEFT, padx=4)

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
        self.combo_campo.set("Razão Social / Nome")
        self.combo_ordem.set("Razão Social / Nome")
        if hasattr(self, "combo_categoria"):
            self.combo_categoria.set("[Todas as Categorias]")
        self.var_ordem_asc.set(True)
        self.var_filtro_exportada.set("PENDENTES")
        self._carregar_dados(especifica=False)
        self.entry_busca.focus_set()

    def _on_mudar_base(self, event=None):
        self._atualizar_lookup_categorias()
        self._carregar_dados()

    def _atualizar_lookup_categorias(self):
        if not self._repo or not hasattr(self, "combo_categoria"):
            return
        base_atual = self.combo_base.get() if hasattr(self, "combo_base") else "GeoApolo"
        try:
            cats = self._repo.listar_categorias_lookup("", base_dados=base_atual)
            opcoes = ["[Todas as Categorias]"] + [f"{c['codigo']} - {c['descricao']}" for c in cats]
            self.combo_categoria["values"] = opcoes
            if not self.combo_categoria.get() or self.combo_categoria.get() not in opcoes:
                self.combo_categoria.set("[Todas as Categorias]")
        except Exception as exc:
            logger.warning("Erro ao carregar combo categorias: %s", exc)

    def _abrir_relatorios_integrados(self):
        try:
            from relatorios import RelatoriosView
            RelatoriosView(self, connection=self._conn)
        except Exception as exc:
            logger.exception("Erro ao abrir relatórios: %s", exc)
            messagebox.showerror("Erro", f"Não foi possível abrir os relatórios:\n{exc}", parent=self)

    def _ordenar_coluna(self, col: str):
        """Permite ordenar os itens da tabela clicando nos cabeçalhos."""
        asc = not self._ordem_colunas_asc.get(col, False)
        self._ordem_colunas_asc[col] = asc

        itens = [(self.tree.set(item, col), item) for item in self.tree.get_children("")]
        itens.sort(reverse=not asc)

        for index, (_, item) in enumerate(itens):
            self.tree.move(item, "", index)
            tags_atuais = list(self.tree.item(item, "tags"))
            if "pendente_geoapolo" in tags_atuais:
                self.tree.item(item, tags=("pendente_geoapolo",))
            else:
                tag_zebra = "par" if index % 2 == 0 else "impar"
                tags_restantes = [t for t in tags_atuais if t not in ("par", "impar")]
                self.tree.item(item, tags=[tag_zebra] + tags_restantes)

    def _obter_registro_selecionado(self) -> Optional[Dict[str, Any]]:
        selected = self.tree.selection()
        if not selected:
            return None
        item_text = self.tree.item(selected[0], "text")
        if item_text is not None and str(item_text).strip().isdigit():
            idx = int(str(item_text).strip())
            if 0 <= idx < len(self._registros_atuais):
                return self._registros_atuais[idx]
        try:
            idx = self.tree.index(selected[0])
            if 0 <= idx < len(self._registros_atuais):
                return self._registros_atuais[idx]
        except Exception:
            pass
        return None

    def _on_tree_key_release(self, event):
        if event.keysym in ("Down", "Next", "End", "Page_Down"):
            self.after(50, self._checar_carregar_mais)

    def _on_tree_mousewheel(self, event):
        if getattr(event, "delta", 0) < 0:
            self.after(50, self._checar_carregar_mais)

    def _checar_carregar_mais(self):
        if self._carregando_mais or self._fim_dos_registros or not self._repo:
            return

        deve_carregar = False
        try:
            yview = self.tree.yview()
            if yview and len(yview) == 2 and float(yview[1]) >= 0.85:
                deve_carregar = True
        except Exception:
            pass

        if not deve_carregar:
            selected = self.tree.selection()
            if selected:
                try:
                    total_itens = len(self._registros_atuais)
                    idx = self.tree.index(selected[0])
                    if total_itens > 0 and (total_itens - idx) <= 15:
                        deve_carregar = True
                except Exception:
                    pass

        if deve_carregar:
            self._carregar_dados(append=True)

    def _carregar_dados(self, especifica: bool = False, append: bool = False):
        if not self._repo:
            return

        if append:
            if self._carregando_mais or self._fim_dos_registros:
                return
            especifica = getattr(self, "_ultima_pesquisa_especifica", False)
            offset = len(self._registros_atuais)
        else:
            self._fim_dos_registros = False
            self._ultima_pesquisa_especifica = especifica or bool(self.entry_busca.get().strip())
            offset = 0

        self._carregando_mais = True

        campo_busca_ui = self.combo_campo.get()
        campo_busca = MAPA_CAMPOS_BUSCA_UI.get(campo_busca_ui, campo_busca_ui)

        campo_ordem_ui = self.combo_ordem.get()
        campo_ordem = MAPA_ORDEM_UI.get(campo_ordem_ui, campo_ordem_ui)

        cat_filtro = ""
        if hasattr(self, "combo_categoria"):
            val_cat = self.combo_categoria.get().strip()
            if val_cat and val_cat != "[Todas as Categorias]":
                cat_filtro = val_cat

        filtro = EntidadeFiltro(
            base_dados=self.combo_base.get(),
            tipo_pesquisa="Especifica" if especifica else "Consulta",
            filtro_especial=self.var_filtro_exportada.get(),
            campo_busca=campo_busca,
            texto_busca=self.entry_busca.get().strip(),
            categoria_busca=cat_filtro,
            campo_ordenacao=campo_ordem,
            ordem_asc=self.var_ordem_asc.get(),
            limite=100,
            offset=offset,
        )

        try:
            novos_registros = self._repo.consultar_lista(filtro)
            if not novos_registros or len(novos_registros) < 100:
                self._fim_dos_registros = True

            if not append:
                # Limpa grid e lista
                for item in self.tree.get_children():
                    self.tree.delete(item)
                self._registros_atuais = []

            base_atual = self.combo_base.get()

            def _fmt_data(dt_val):
                if not dt_val:
                    return ""
                if hasattr(dt_val, "strftime"):
                    return dt_val.strftime("%d/%m/%Y")
                s = str(dt_val)[:10]
                if len(s) == 10 and s[4] == "-" and s[7] == "-":
                    return f"{s[8:10]}/{s[5:7]}/{s[0:4]}"
                return s

            start_idx = len(self._registros_atuais)
            self._registros_atuais.extend(novos_registros)

            for i, reg in enumerate(novos_registros):
                idx = start_idx + i
                cod_geo = str(reg.get("geoentcod") or "").strip()
                entcod = str(reg.get("entcod") or "").strip()
                nome = str(reg.get("entnome") or reg.get("geoentnome") or "").strip()
                nome_fantasia = str(reg.get("entnomefant") or reg.get("geoentnomefantasia") or "").strip()

                doc = str(reg.get("EntCpfCgc") or reg.get("entcpfcgc") or reg.get("geonumerodocumento") or reg.get("Documento") or "").strip()
                tipo_doc = str(reg.get("geotipodocumento") or "").strip()
                rg_ie = str(reg.get("EntRgIe") or reg.get("entrgie") or reg.get("geonumerorg") or "").strip()
                if not doc and cod_geo and self._repo:
                    try:
                        cpf_doc, rg_doc = self._repo.obter_cpf_rg_documentos(cod_geo)
                        doc = cpf_doc or ""
                        if rg_doc and not rg_ie:
                            rg_ie = rg_doc
                    except Exception:
                        pass

                tipo_fj = str(reg.get("enttipofj") or reg.get("geotipofj") or "").strip()
                tratamento = str(reg.get("tipotratcod") or reg.get("geotipotratcod") or "").strip()
                desde_data = _fmt_data(reg.get("EntDesdeData") or reg.get("geoentdesdedata"))
                data_cad = _fmt_data(reg.get("entdatacad") or reg.get("geoentdatacad"))

                lograd = str(reg.get("logradouro") or reg.get("entlograd") or reg.get("tipologradabrev") or "").strip()
                ender = str(reg.get("entender") or reg.get("geoentender") or "").strip()
                if lograd and not ender.startswith(lograd):
                    ender_completo = f"{lograd} {ender}".strip()
                else:
                    ender_completo = ender

                numero = str(reg.get("entenderno") or reg.get("geoenderno") or "").strip()
                compl = str(reg.get("entendercomp") or reg.get("geoentendercomp") or "").strip()
                bairro = str(reg.get("entbair") or reg.get("geoentbair") or "").strip()
                cidade_cod = str(reg.get("cidcod") or reg.get("geocidcod") or "").strip()
                cidade = str(reg.get("cidnomecomp") or "").strip()
                uf = str(reg.get("ufsigla") or "").strip()
                cep = str(reg.get("entcep") or reg.get("geoentcep") or "").strip()
                cx_postal = str(reg.get("entcxapost") or reg.get("geoentcxapost") or "").strip()
                ref_ender = str(reg.get("geolocalreferencia_ender") or "").strip()

                regiao = str(reg.get("regnome") or reg.get("regcodestr") or reg.get("georegcodestr") or "").strip()
                conceito = str(reg.get("entconceito") or reg.get("geoentconceito") or "").strip()
                data_nasc = _fmt_data(reg.get("entdataanivfund") or reg.get("geoentdataanivfund"))

                cargo_cod = str(reg.get("cargocodestr") or reg.get("geocargocodestr") or "").strip()
                cargo = str(reg.get("cargonome") or reg.get("geocargonome") or "").strip()
                genero = str(reg.get("entgenero") or reg.get("geoentgenero") or "").strip()
                estado_civil = str(reg.get("EntEstCivil") or reg.get("geoentestcivil") or "").strip()

                nome_pai = str(reg.get("EntNomePai") or reg.get("geoentnomepai") or "").strip()
                nome_mae = str(reg.get("EntNomeMae") or reg.get("geoentnomemae") or "").strip()
                possui_filho = str(reg.get("EntPossuiFilho") or reg.get("geoentpossuifilho") or "").strip()
                num_filhos = str(reg.get("numerofilhos") if reg.get("numerofilhos") is not None else "0").strip()
                mora_com = str(reg.get("EntMoraCom") or reg.get("geoentmoracom") or "").strip()

                cod_escolaridade = str(reg.get("codigo_grauescolaridade") or "").strip()
                escolaridade = str(reg.get("EntGrauEscol") or reg.get("grau_escolaridade") or "").strip()
                falecido = str(reg.get("USERFalecido") or reg.get("geofalecido") or "").strip()
                ativ_econ = str(reg.get("ativeconnome") or "").strip()

                orig_cod = str(reg.get("OrigCodEstr") or reg.get("geo_origcodestr") or "").strip()
                origem = str(reg.get("OrigNome") or reg.get("geo_orignome") or "").strip()
                categ_cod = str(reg.get("Categcodestr") or reg.get("geocategcodestr") or "").strip()
                categoria = str(reg.get("categnome") or reg.get("geocategnome") or "").strip()

                tipo_cob_cod = str(reg.get("TipoCobCod") or reg.get("geotipocobcod") or "").strip()
                tipo_cob_nome = str(reg.get("TipoCobNome") or reg.get("geotipocobnome") or "").strip()
                bco_num = str(reg.get("bconum") or reg.get("geobconum") or "").strip()
                bco_nome = str(reg.get("bconome") or reg.get("geobconome") or "").strip()
                ag_num = str(reg.get("agnum") or reg.get("geoagnum") or "").strip()
                ag_nome = str(reg.get("AgNome") or reg.get("geoagnome") or "").strip()
                conta = str(reg.get("EntBcoAgCCorNum") or reg.get("geoconta") or "").strip()
                dia_contrib = str(reg.get("USERDia_Debito_CC") or reg.get("geodia_contribuicao") or "").strip()
                gerar_carne = str(reg.get("USERgeraCarne") or reg.get("geogerarcarne") or "").strip()
                diocese_id = str(reg.get("UserDiocese_id") or reg.get("geodioceseid") or "").strip()
                diocese = str(reg.get("USERNomeDiocese") or reg.get("Diocese") or "").strip()
                recebe_lembrete = str(reg.get("USERrecebelembretedoacao") or reg.get("georecebelembrete") or "").strip()

                val_raw = reg.get("USERValor_Contribuicao") or reg.get("geovalorcontribuicao") or 0
                try:
                    val_contrib = f"R$ {float(val_raw):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                except Exception:
                    val_contrib = str(val_raw)

                cid_apolo = str(reg.get("cidcodapolo") or "").strip()
                loc_cobranca = str(reg.get("entloccobrancaomesmo") or reg.get("geoentloccobrancaomesmo") or "").strip()
                loc_entrega = str(reg.get("EntLocEntregaOMesmo") or reg.get("geoentlocentregaomesmo") or "").strip()
                transporte = str(reg.get("EntTransporteOMesmo") or reg.get("geoenttransporteomesmo") or "").strip()

                atualizou = reg.get("status_sincronizacao") or reg.get("atualizou_apolo", "N")
                usu_atualizou = str(reg.get("usucod_atualizou_apolo") or "").strip()
                obs = str(reg.get("Entobservacoes") or reg.get("geoobservacoes") or "").strip()

                tag_zebra = "par" if idx % 2 == 0 else "impar"
                is_pendente = (str(atualizou).strip().upper() != "S")

                # Se a base selecionada for GeoApolo, destaca em vermelho os registros pendentes
                if base_atual == "GeoApolo" and is_pendente:
                    tags_item = ("pendente_geoapolo",)
                elif atualizou == "S":
                    tags_item = (tag_zebra, "sincronizado")
                else:
                    tags_item = (tag_zebra, "pendente")

                status_formatado = "✔ Sim (Sincronizado)" if atualizou == "S" else "⏳ Não (Pendente)"

                self.tree.insert(
                    "",
                    tk.END,
                    text=str(idx),
                    values=(
                        cod_geo,
                        entcod,
                        nome,
                        nome_fantasia,
                        doc,
                        tipo_doc,
                        rg_ie,
                        tipo_fj,
                        tratamento,
                        desde_data,
                        data_cad,
                        lograd,
                        ender_completo,
                        numero,
                        compl,
                        bairro,
                        cidade_cod,
                        cidade,
                        uf,
                        cep,
                        cx_postal,
                        ref_ender,
                        regiao,
                        conceito,
                        data_nasc,
                        cargo_cod,
                        cargo,
                        genero,
                        estado_civil,
                        nome_pai,
                        nome_mae,
                        possui_filho,
                        num_filhos,
                        mora_com,
                        cod_escolaridade,
                        escolaridade,
                        falecido,
                        ativ_econ,
                        orig_cod,
                        origem,
                        categ_cod,
                        categoria,
                        tipo_cob_cod,
                        tipo_cob_nome,
                        bco_num,
                        bco_nome,
                        ag_num,
                        ag_nome,
                        conta,
                        dia_contrib,
                        gerar_carne,
                        diocese_id,
                        diocese,
                        recebe_lembrete,
                        val_contrib,
                        cid_apolo,
                        loc_cobranca,
                        loc_entrega,
                        transporte,
                        status_formatado,
                        usu_atualizou,
                        obs,
                    ),
                    tags=tags_item,
                )

            if self._fim_dos_registros:
                self.lbl_status.config(text=f"Total: {len(self._registros_atuais)} entidade(s) listada(s).")
            else:
                self.lbl_status.config(text=f"Total: {len(self._registros_atuais)} entidade(s) listada(s) (Role para carregar mais)...")
        except Exception as exc:
            logger.exception("Erro ao carregar lista de entidades: %s", exc)
            messagebox.showerror("Erro", f"Erro ao consultar entidades:\n{exc}", parent=self)
        finally:
            self._carregando_mais = False

    def _on_double_click(self, event):
        """Ao dar duplo clique em uma entidade, abre o FrmCadEntidade (unt_cadentidades do Delphi) para visualização e edição."""
        reg = self._obter_registro_selecionado()
        if not reg:
            return

        try:
            from entidades.cadentidade_view import FrmCadEntidade
            form_cad = FrmCadEntidade(
                parent=self,
                registro=reg,
                base_dados=self.combo_base.get(),
                on_salvar=self._carregar_dados,
                connection=self._conn,
            )
            form_cad.focus_set()
        except Exception as exc:
            logger.exception("Erro ao abrir formulário de cadastro de entidade: %s", exc)
            messagebox.showerror("Erro", f"Não foi possível abrir o formulário de cadastro de entidade:\n{exc}", parent=self)

    def _novo_registro(self):
        """Abre o formulário de cadastro de entidades para a inclusão de um novo registro."""
        try:
            from entidades.cadentidade_view import FrmCadEntidade
            form_cad = FrmCadEntidade(
                parent=self,
                registro=None,
                base_dados=self.combo_base.get(),
                on_salvar=self._carregar_dados,
                connection=self._conn,
                modo_inclusao=True,
            )
            form_cad.focus_set()
        except Exception as exc:
            logger.exception("Erro ao abrir formulário de cadastro de entidade para inclusão: %s", exc)
            messagebox.showerror("Erro", f"Não foi possível abrir o formulário de cadastro de entidade:\n{exc}", parent=self)

    def _abrir_tela_comparacao(
        self,
        diferencas: List[ItemComparacao],
        geoentcod: str = "",
        entcod: str = "",
        nome_entidade: str = "",
        sve_data: Optional[Dict[str, Any]] = None,
        alvo_data: Optional[Dict[str, Any]] = None,
    ):
        """Janela modal para comparação de campos SVE x Alvo centralizada em relação ao formulário principal."""
        if not diferencas:
            messagebox.showinfo("Comparação de Cadastros", "✔ Cadastros idênticos! Nenhuma divergência encontrada entre o GeoApolo e o Alvo.", parent=self)
            return

        comp_win = tk.Toplevel(self)
        comp_win.title("Comparador de Divergências: GeoApolo (SVE) x Alvo")
        largura, altura = 960, 560
        from core import centralizar_janela
        centralizar_janela(comp_win, self, largura, altura)
        comp_win.minsize(820, 440)
        comp_win.transient(self)
        comp_win.grab_set()

        # Banner Superior do Comparador
        banner_comp = tk.Frame(comp_win, bg="#1A365D", height=60)
        banner_comp.pack(side=tk.TOP, fill=tk.X)
        banner_comp.pack_propagate(False)

        num_difs = len([d for d in diferencas if d.eh_diferente])
        titulo_banner = f"⚖ Conferência Lado a Lado: {nome_entidade or 'Entidade'}"
        sub_banner = f"Cód. GeoApolo: {geoentcod} | Cód. Alvo: {entcod or 'Não vinculado'} | {num_difs} campo(s) divergente(s) em moderação"

        tk.Label(
            banner_comp,
            text=titulo_banner,
            font=("Segoe UI", 11, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
            anchor="w",
        ).pack(side=tk.TOP, fill=tk.X, padx=15, pady=(8, 0))

        tk.Label(
            banner_comp,
            text=sub_banner,
            font=("Segoe UI", 8),
            bg="#1A365D",
            fg="#CBD5E0",
            anchor="w",
        ).pack(side=tk.TOP, fill=tk.X, padx=15, pady=(1, 6))

        # Barra de Ações Rápidas em Lote
        batch_bar = ttk.Frame(comp_win, padding=6)
        batch_bar.pack(side=tk.TOP, fill=tk.X, padx=10, pady=4)

        cols = ("campo", "sve", "alvo", "decisao")
        tree_comp = ttk.Treeview(comp_win, columns=cols, show="headings", selectmode="browse")
        tree_comp.heading("campo", text="Campo")
        tree_comp.heading("sve", text="GeoApolo (SVE) - Clique p/ Usar")
        tree_comp.heading("alvo", text="Alvo - Clique p/ Manter")
        tree_comp.heading("decisao", text="Decisão Tomada")

        tree_comp.column("campo", width=180)
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
                    if not item.eh_diferente:
                        status = "✔ Idêntico (Manter)"
                    else:
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
                if item.eh_diferente:
                    item.decisao = DecisaoLinha.MANTER_SVE
            atualizar_tabela_comp()

        def selecionar_todos_alvo():
            for item in diferencas:
                if item.eh_diferente:
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
            pendentes = [d for d in diferencas if d.decisao == DecisaoLinha.NENHUMA and d.eh_diferente]
            if pendentes:
                if not messagebox.askyesno(
                    "Decisões Pendentes",
                    f"Ainda restam {len(pendentes)} campo(s) sem decisão explícita.\nDeseja aplicar as decisões atuais e ignorar os demais?",
                    parent=comp_win,
                ):
                    return

            from configuracoes.alvo_api_config import carregar_configuracao_alvo, validar_status_token
            cfg_alvo = carregar_configuracao_alvo()
            status_token, msg_token, is_valido = validar_status_token(cfg_alvo)

            if is_valido and cfg_alvo.token.strip():
                self._api_client.token = cfg_alvo.token.strip()
                if cfg_alvo.base_url:
                    self._api_client.base_url = cfg_alvo.base_url.rstrip("/")
            elif not self._api_client.token:
                cred = self._obter_credenciais_alvo_operador()
                if not cred:
                    return
                usu, pwd = cred
                if not self._api_client.garantir_autenticacao(usu, pwd):
                    messagebox.showerror("Erro de Autenticação", "Falha ao autenticar no Alvo com o usuário/senha informados.", parent=comp_win)
                    return

            comp_win.config(cursor="wait")
            comp_win.update_idletasks()
            try:
                if geoentcod and self._service:
                    sucesso_c, msg_c, _ = self._service.garantir_contato_integrado_alvo(
                        geoentcod_pai=geoentcod,
                        api_client=self._api_client
                    )
                    if not sucesso_c:
                        messagebox.showerror("Erro de Integração do Contato", msg_c, parent=comp_win)
                        return

                payload = self._service.gerar_payload_sobreposicao(
                    diferencas,
                    entcod=entcod,
                    geoentcod=geoentcod,
                    sve_data=sve_data,
                    alvo_data=alvo_data,
                )
                sucesso, msg, dados_resp = self._api_client.inserir_alterar_entidade(payload)
            except Exception as exc_sb:
                logger.exception("Erro ao aplicar sobreposição no Alvo: %s", exc_sb)
                caminho_log = salvar_log_erro_executavel(
                    nome_arquivo="exportacao_erro.log",
                    titulo="Gestão de Entidades - Sobreposição de Campos",
                    erro=exc_sb,
                    contexto=f"geoentcod={geoentcod}, entcod={entcod}"
                )
                messagebox.showerror(
                    "Erro ao Sobrepor",
                    f"Ocorreu um erro ao enviar decisões para o Alvo:\n{exc_sb}\n\nDetalhes gravados em:\n{caminho_log}",
                    parent=comp_win,
                )
                return
            finally:
                if comp_win.winfo_exists():
                    comp_win.config(cursor="")

            if sucesso:
                novo_cod = self._api_client.extrair_entcod_resposta(msg, dados_resp) or entcod
                if novo_cod and geoentcod and self._service:
                    self._service.vincular_entcod(geoentcod, novo_cod)
                    try:
                        from entidades.cadentidade_view import FrmCadEntidade
                        if FrmCadEntidade._instancia_ativa and FrmCadEntidade._instancia_ativa.winfo_exists():
                            inst = FrmCadEntidade._instancia_ativa
                            if str(inst.registro.get("geoentcod") or "") == str(geoentcod):
                                inst.atualizar_codigo_alvo(novo_cod)
                    except Exception:
                        pass

                # Aplica as decisões de sobreposição na tabela entidade do banco local
                if self._repo and (novo_cod or entcod):
                    try:
                        dados_sobrep = payload.get("Entidade", payload)
                        self._repo.aplicar_sobreposicao_alvo_local(str(novo_cod or entcod), dados_sobrep)
                    except Exception as ex_loc:
                        logger.warning("Falha ao atualizar entidade local no banco: %s", ex_loc)

                messagebox.showinfo("Sucesso", f"Decisões de sobreposição aplicadas no Alvo com sucesso!\n{msg}", parent=comp_win)
                comp_win.destroy()
                self._carregar_dados()
            else:
                caminho_log = salvar_log_erro_executavel(
                    nome_arquivo="exportacao_erro.log",
                    titulo="Gestão de Entidades - Falha na Sobreposição API Alvo",
                    erro=RuntimeError(msg),
                    contexto=f"geoentcod={geoentcod}, entcod={entcod}"
                )
                messagebox.showerror(
                    "Falha ao Sobrepor",
                    f"Erro retornado pela API Alvo:\n{msg}\n\nDetalhes registrados em:\n{caminho_log}",
                    parent=comp_win,
                )

        ttk.Button(btn_frame, text="✔ Aplicar Decisões no Alvo", command=salvar_sobreposicao).pack(side=tk.LEFT, padx=10, pady=7)
        ttk.Button(btn_frame, text="Cancelar (Esc)", command=comp_win.destroy).pack(side=tk.RIGHT, padx=10, pady=7)
        comp_win.bind("<Escape>", lambda e: comp_win.destroy())

    def _obter_credenciais_alvo_operador(self) -> Optional[Tuple[str, str]]:
        """
        Obtém as credenciais do Alvo (usuario_alvo, senha_alvo_plana).
        1. Consulta na sessão atual em memória.
        2. Consulta no banco de dados (USER_geoapolo_usuarios) pelo usuário logado, decriptografando com chave 35.
        3. Se não houver, solicita ao operador via diálogo modal DlgCredenciaisAlvo e salva no banco cifrada com chave 35.
        Equivalente à rotina de credenciais do Delphi em unt_entidades.pas.
        """
        from logon import sessao_usuario_atual
        from core.criptografia import criptografia, decriptografia

        usu_alvo = str(sessao_usuario_atual.get("usucod_apolo") or "").strip()
        senha_alvo_db = str(sessao_usuario_atual.get("senha_alvo") or "").strip()
        cod_usuario = str(sessao_usuario_atual.get("codigo_usuario") or "").strip()

        if (not usu_alvo or not senha_alvo_db) and cod_usuario and self._repo:
            try:
                cred = self._repo.obter_credenciais_alvo(cod_usuario)
                if cred.usuario_alvo and cred.senha_alvo_cripto:
                    usu_alvo = cred.usuario_alvo
                    senha_alvo_db = cred.senha_alvo_cripto
                    sessao_usuario_atual["usucod_apolo"] = usu_alvo
                    sessao_usuario_atual["senha_alvo"] = senha_alvo_db
            except Exception as ex:
                logger.warning("Erro ao consultar credenciais do Alvo no banco: %s", ex)

        if usu_alvo and senha_alvo_db:
            senha_plana = decriptografia(35, senha_alvo_db)
            if senha_plana:
                return usu_alvo, senha_plana

        dlg = DlgCredenciaisAlvo(self, usuario_padrao=usu_alvo)
        if not dlg.resultado:
            return None

        novo_usu, nova_senha_plana = dlg.resultado
        nova_senha_cripto = criptografia(35, nova_senha_plana)

        sessao_usuario_atual["usucod_apolo"] = novo_usu
        sessao_usuario_atual["senha_alvo"] = nova_senha_cripto

        if cod_usuario and self._repo:
            try:
                self._repo.salvar_credenciais_alvo(cod_usuario, novo_usu, nova_senha_cripto)
            except Exception as ex:
                logger.warning("Falha ao persistir credenciais do Alvo no banco: %s", ex)

        return novo_usu, nova_senha_plana

    def _acao_exportar(self):
        """
        Dispara a rotina de exportação para a API Alvo conforme regras do Delphi (unt_entidades.pas):
        - Bloqueia caso esteja na base Alvo.
        - Bloqueia caso haja observações não moderadas.
        - Se a entidade já possui entcod (cadastrada no Alvo): abre a conferência de divergências lado a lado.
        - Se a entidade for nova (sem entcod): solicita confirmação do operador, obtém credenciais e envia para a API.
        """
        reg = self._obter_registro_selecionado()
        if not reg:
            messagebox.showwarning("Aviso", "Selecione uma entidade na lista primeiro.", parent=self)
            return

        base = self.combo_base.get()
        if base == "Alvo":
            messagebox.showerror(
                "Aviso",
                "VOCÊ ESTÁ NA BASE ALVO E NÃO SERÁ PERMITIDA A EXPORTAÇÃO DA ENTIDADE !!!",
                parent=self,
            )
            return

        obs = str(reg.get("entobservacoes") or reg.get("Entobservacoes") or reg.get("geoobservacoes") or "").strip()
        obs_upper = obs.upper()
        if "[PEND" in obs_upper:
            messagebox.showerror(
                "Aviso - Pendências Registradas",
                "A exportação para o Alvo foi interrompida pois esta entidade possui [PENDÊNCIAS] registradas no campo de observações!\n\n"
                "Dê duplo clique na entidade e modere as pendências antes de exportar.",
                parent=self,
            )
            return

        geoentcod = str(reg.get("geoentcod") or "")

        # Validação obrigatória de CPF / CNPJ válido antes de tentar exportar
        doc_entidade = str(reg.get("entcpfcgc") or reg.get("cpf") or "").strip()
        if not doc_entidade and self._repo:
            try:
                cpf_doc, _ = self._repo.obter_cpf_rg_documentos(geoentcod)
                doc_entidade = (cpf_doc or "").strip()
            except Exception:
                pass

        import re
        from core.validators import validar_cpf, validar_cnpj
        from entidades.documentos_teste import (
            eh_grupo_de_oracao,
            obter_proximo_documento_teste,
            consumir_documento_teste,
            verificar_alerta_poucos_documentos,
        )
        digitos_doc = re.sub(r"\D", "", doc_entidade)
        tipo_fj = str(reg.get("enttipofj") or reg.get("geotipofj") or "F").upper()
        is_juridica = tipo_fj in ("J", "JURIDICA", "JURÍDICA") or len(digitos_doc) > 11
        is_grupo_oracao = eh_grupo_de_oracao(geoentcod, reg, self._repo)

        # Alerta se a lista de documentos de teste estiver com 5 ou menos registros
        if is_grupo_oracao and not digitos_doc:
            alerta_lista = verificar_alerta_poucos_documentos(tipo_fj, limite=5)
            if alerta_lista:
                messagebox.showwarning("Aviso - Lista de Documentos Quase no Fim", alerta_lista, parent=self)

        if is_juridica:
            if not validar_cnpj(digitos_doc):
                if not (not digitos_doc and is_grupo_oracao):
                    messagebox.showerror(
                        "Aviso - CNPJ Inválido",
                        f"O CNPJ '{doc_entidade or 'não informado'}' da entidade é inválido!\n\n"
                        f"Não é permitida a exportação para o Alvo com documento inválido.\n"
                        f"Favor corrigir o CNPJ antes de tentar exportar.",
                        parent=self,
                    )
                    return
        else:
            if not validar_cpf(digitos_doc):
                if not (not digitos_doc and is_grupo_oracao):
                    messagebox.showerror(
                        "Aviso - CPF Inválido",
                        f"O CPF '{doc_entidade or 'não informado'}' da entidade é inválido!\n\n"
                        f"Não é permitida a exportação para o Alvo com CPF inválido.\n"
                        f"Favor corrigir o CPF antes de tentar exportar.",
                        parent=self,
                    )
                    return

        entcod = self._service.obter_ou_resolver_entcod_alvo(geoentcod, reg.get("entcod")) if self._service else reg.get("entcod")

        sve_data = {}
        alvo_data = {}
        if self._repo:
            try:
                ret_comp = self._repo.carregar_dados_comparacao(
                    geoentcod, str(entcod or ""), cpf=doc_entidade
                )
                if isinstance(ret_comp, (tuple, list)) and len(ret_comp) == 2:
                    sve_data, alvo_data = ret_comp
            except Exception as ex:
                logger.warning("Erro ao carregar dados de comparação: %s", ex)

        # Se encontrou entcod pelo carregar_dados_comparacao (via CPF no Alvo)
        if not entcod and alvo_data.get("entcod"):
            entcod = str(alvo_data.get("entcod") or "").strip()

        nome_ent = str(sve_data.get("geoentnome") or sve_data.get("entnome") or reg.get("entnome") or reg.get("geoentnome") or geoentcod).strip()

        # Caso a entidade já possua código no Alvo, trata-se de uma ATUALIZAÇÃO:
        # Exibe OBRIGATORIAMENTE a tela de conferência/comparação antes de qualquer atualização!
        if entcod and self._service:
            if not sve_data:
                sve_data = reg

            # Se for Grupo de Oração e o documento estiver vazio, aloca da lista de teste, consome e insere na grid
            doc_sve = str(sve_data.get("Documento") or sve_data.get("geonumerodocumento") or sve_data.get("EntCpfCgc") or sve_data.get("entcpfcgc") or doc_entidade or "").strip()
            digitos_sve = re.sub(r"\D", "", doc_sve)
            if is_grupo_oracao and not digitos_sve:
                try:
                    novo_doc, caminho_csv = obter_proximo_documento_teste(tipo_fj)
                    consumir_documento_teste(caminho_csv, novo_doc)
                    if self._repo:
                        self._repo.salvar_documento_entidade(
                            geoentcod, tipo="CPF/CNPJ", documento=novo_doc, observacoes="TESTE AUTO"
                        )
                    doc_entidade = novo_doc
                    digitos_doc = re.sub(r"\D", "", novo_doc)
                    reg["entcpfcgc"] = novo_doc
                    reg["Documento"] = novo_doc
                    reg["geonumerodocumento"] = novo_doc
                    sve_data["Documento"] = novo_doc
                    sve_data["EntCpfCgc"] = novo_doc
                    sve_data["entcpfcgc"] = novo_doc
                    sve_data["geonumerodocumento"] = novo_doc

                    # Atualiza imediatamente a grid principal
                    selected = self.tree.selection()
                    if selected:
                        self.tree.set(selected[0], "documento", novo_doc)

                    # Se a tela de manutenção estiver aberta, atualiza o campo em tela
                    try:
                        from entidades.cadentidade_view import FrmCadEntidade
                        if FrmCadEntidade._instancia_ativa and FrmCadEntidade._instancia_ativa.winfo_exists():
                            inst = FrmCadEntidade._instancia_ativa
                            if str(inst.registro.get("geoentcod") or "") == str(geoentcod):
                                if hasattr(inst, "atualizar_documento"):
                                    inst.atualizar_documento(novo_doc)
                    except Exception:
                        pass
                except Exception as e_doc_exist:
                    logger.warning("Falha ao alocar documento de teste para entidade existente %s: %s", geoentcod, e_doc_exist)
            if not alvo_data:
                # Preenche com dados disponíveis para viabilizar conferência em tela
                alvo_data = {
                    "entcod": entcod,
                    "entnome": nome_ent,
                    "EntCpfCgc": reg.get("EntCpfCgc") or reg.get("entcpfcgc") or doc_entidade,
                    "EntRgIe": reg.get("EntRgIe") or reg.get("entrgie") or "",
                    "EntLograd": reg.get("EntLograd") or reg.get("entlograd") or "",
                    "entender": reg.get("entender") or reg.get("geoentender") or "",
                    "entenderno": reg.get("entenderno") or reg.get("geoenderno") or "",
                    "EntEnderComp": reg.get("EntEnderComp") or reg.get("geoentendercomp") or "",
                    "entbair": reg.get("entbair") or reg.get("geoentbair") or "",
                    "entcep": reg.get("entcep") or reg.get("geoentcep") or "",
                    "cidnomecomp": reg.get("cidnomecomp") or "",
                    "ufsigla": reg.get("ufsigla") or "",
                }

            difs = self._service.comparar_cadastros(sve_data, alvo_data, incluir_referencias=True)
            num_difs = len([d for d in difs if d.eh_diferente])

            if num_difs == 0:
                if not messagebox.askyesno(
                    "Cadastros Idênticos",
                    f"A entidade '{nome_ent}' já possui código no Alvo ({entcod}) e todos os campos analisados estão idênticos!\n\n"
                    f"Deseja abrir a tela de conferência para revisar ou forçar a atualização mesmo assim?",
                    parent=self,
                ):
                    return

            self._abrir_tela_comparacao(
                difs,
                geoentcod=geoentcod,
                entcod=str(entcod),
                nome_entidade=nome_ent,
                sve_data=sve_data,
                alvo_data=alvo_data,
            )
            return

        # Registro novo no Alvo (sem entcod): confirma exportação direta via API
        nome_ent = reg.get("entnome") or reg.get("geoentnome") or geoentcod

        # Alerta se o valor de contribuição for igual a zero para conferência de quem está exportando
        val_contrib = float(reg.get("USERValor_Contribuicao") or reg.get("uservalor_contribuicao") or reg.get("geovalorcontribuicao") or 0.0)
        if val_contrib == 0.0:
            if not messagebox.askyesno(
                "Atenção - Valor de Contribuição Zerado",
                f"Atenção: O Valor de Contribuição desta entidade está igual a zero (R$ 0,00)!\n\n"
                f"Entidade: {nome_ent} (Cód. Geo: {geoentcod})\n\n"
                f"Deseja prosseguir com a exportação para o Alvo para conferência?",
                parent=self,
            ):
                return

        if not messagebox.askyesno(
            "Confirmação",
            f"Confirma a exportação desta entidade ({nome_ent}) para o Alvo?",
            parent=self,
        ):
            return

        usuario_alvo = ""
        senha_alvo_plana = ""

        # Prioriza o token permanente da integração API Alvo configurado no sistema
        from configuracoes.alvo_api_config import carregar_configuracao_alvo, validar_status_token
        cfg_alvo = carregar_configuracao_alvo()
        status_token, msg_token, is_valido = validar_status_token(cfg_alvo)

        if not is_valido:
            # Sem token válido configurado: solicita login ao operador como fallback
            cred = self._obter_credenciais_alvo_operador()
            if not cred:
                return
            usuario_alvo, senha_alvo_plana = cred

        if not self._service:
            messagebox.showerror("Erro", "Serviço de entidades indisponível.", parent=self)
            return

        self.config(cursor="wait")
        self.update_idletasks()
        try:
            res = self._service.exportar_entidade_para_alvo(
                geoentcod=geoentcod,
                usuario_alvo=usuario_alvo,
                senha_alvo_plana=senha_alvo_plana,
                api_client=self._api_client,
            )
        except Exception as exc:
            logger.exception("Erro durante exportação da entidade para o Alvo: %s", exc)
            caminho_log = salvar_log_erro_executavel(
                nome_arquivo="exportacao_erro.log",
                titulo="Gestão de Entidades - Exportação para o Alvo",
                erro=exc,
                contexto=f"Entidade geoentcod={geoentcod}, nome={nome_ent}"
            )
            messagebox.showerror(
                "Erro na Exportação",
                f"Ocorreu um erro durante a exportação da entidade para o Alvo:\n{exc}\n\n"
                f"Os detalhes técnicos foram registrados no arquivo de log:\n{caminho_log}",
                parent=self,
            )
            return
        finally:
            self.config(cursor="")

        if res.sucesso:
            novo_codigo = res.codigo
            if novo_codigo:
                reg["entcod"] = str(novo_codigo).strip()
                try:
                    from entidades.cadentidade_view import FrmCadEntidade
                    if FrmCadEntidade._instancia_ativa and FrmCadEntidade._instancia_ativa.winfo_exists():
                        inst = FrmCadEntidade._instancia_ativa
                        if str(inst.registro.get("geoentcod") or "") == str(geoentcod):
                            inst.atualizar_codigo_alvo(str(novo_codigo).strip())
                            if self._repo:
                                cpf_atualizado, _ = self._repo.obter_cpf_rg_documentos(geoentcod)
                                if cpf_atualizado and hasattr(inst, "atualizar_documento"):
                                    inst.atualizar_documento(cpf_atualizado)
                except Exception:
                    pass
            if self._repo:
                try:
                    from logon import sessao_usuario_atual
                    usucod_op = sessao_usuario_atual.get("usucod") or sessao_usuario_atual.get("login") or sessao_usuario_atual.get("usucod_apolo") or "JULIO"
                    self._repo.registrar_log_atividade(
                        usucod=usucod_op,
                        descricao=f"Exportou a Entidade: {geoentcod} e {nome_ent} para o alvo usando o geoapolo",
                    )
                except Exception as e_log:
                    logger.warning("Falha ao registrar log de atividade: %s", e_log)
            messagebox.showinfo("Sucesso", res.mensagem, parent=self)
            self._carregar_dados()
        else:
            caminho_log = salvar_log_erro_executavel(
                nome_arquivo="exportacao_erro.log",
                titulo="Gestão de Entidades - Falha na Resposta do Alvo",
                erro=RuntimeError(res.mensagem),
                contexto=f"Entidade geoentcod={geoentcod}, nome={nome_ent}"
            )
            messagebox.showerror(
                "Falha na Exportação",
                f"{res.mensagem}\n\nDetalhes registrados em:\n{caminho_log}",
                parent=self,
            )

    def _acao_exportar_filtro(self):
        """
        Executa a exportação em lote de todas as entidades correspondentes ao filtro ativo para o Alvo:
        - Valida a base selecionada (somente GeoApolo).
        - Obtém todos os registros filtrados sem limite de paginação.
        - Solicita confirmação ao operador com a quantidade total.
        - Valida credenciais/token API Alvo.
        - Loop com janela modal de progresso e botão de cancelamento.
        - Ignora registros com [PENDÊNCIAS].
        - Aloca CPF/CNPJ de teste para Grupos de Oração sem documento e consome do CSV ao ter sucesso.
        - Salva log de atividade para cada entidade exportada:
          "Exportou a Entidade: <código> e <nome> para o alvo usando o geoapolo" na tabela USER_geoapolo_logatividades.
        - Exibe resumo final e atualiza a grid.
        """
        base = self.combo_base.get()
        if base == "Alvo":
            messagebox.showerror(
                "Aviso",
                "VOCÊ ESTÁ NA BASE ALVO E NÃO SERÁ PERMITIDA A EXPORTAÇÃO DA ENTIDADE !!!",
                parent=self,
            )
            return

        if not self._repo or not self._service:
            messagebox.showerror("Erro", "Serviço de banco de dados ou integração indisponível.", parent=self)
            return

        campo_busca_ui = self.combo_campo.get()
        campo_busca = MAPA_CAMPOS_BUSCA_UI.get(campo_busca_ui, campo_busca_ui)

        campo_ordem_ui = self.combo_ordem.get()
        campo_ordem = MAPA_ORDEM_UI.get(campo_ordem_ui, campo_ordem_ui)

        cat_filtro = ""
        if hasattr(self, "combo_categoria"):
            val_cat = self.combo_categoria.get().strip()
            if val_cat and val_cat != "[Todas as Categorias]":
                cat_filtro = val_cat

        filtro = EntidadeFiltro(
            base_dados="GeoApolo",
            tipo_pesquisa="Especifica" if bool(self.entry_busca.get().strip()) else "Consulta",
            filtro_especial=self.var_filtro_exportada.get(),
            campo_busca=campo_busca,
            texto_busca=self.entry_busca.get().strip(),
            categoria_busca=cat_filtro,
            campo_ordenacao=campo_ordem,
            ordem_asc=self.var_ordem_asc.get(),
            limite=50000,
            offset=0,
        )

        try:
            self.config(cursor="wait")
            self.update_idletasks()
            registros = self._repo.obter_todas_chaves_filtro(filtro)
        except Exception as exc_busca:
            logger.exception("Erro ao obter lista de entidades do filtro: %s", exc_busca)
            messagebox.showerror("Erro", f"Falha ao consultar entidades do filtro:\n{exc_busca}", parent=self)
            return
        finally:
            self.config(cursor="")

        if not registros:
            messagebox.showinfo("Aviso", "Nenhuma entidade encontrada para o filtro atual.", parent=self)
            return

        total_entidades = len(registros)
        desc_cat = f" com categoria '{cat_filtro}'" if cat_filtro else ""

        # Alerta se houver entidades com valor de contribuição zerado para conferência
        zerados = [r for r in registros if float(r.get("USERValor_Contribuicao") or r.get("uservalor_contribuicao") or r.get("geovalorcontribuicao") or 0.0) == 0.0]
        aviso_zerados = f"\n\n⚠️ ATENÇÃO: {len(zerados)} entidade(s) possuem Valor de Contribuição igual a zero (R$ 0,00) para conferência!" if zerados else ""

        if not messagebox.askyesno(
            "Confirmação de Exportação em Lote",
            f"Foram encontradas {total_entidades} entidade(s){desc_cat} no filtro atual.{aviso_zerados}\n\n"
            f"Deseja iniciar a exportação em lote para o Alvo?",
            parent=self,
        ):
            return

        # Validação do Token Alvo ou credenciais
        usuario_alvo = ""
        senha_alvo_plana = ""
        from configuracoes.alvo_api_config import carregar_configuracao_alvo, validar_status_token
        cfg_alvo = carregar_configuracao_alvo()
        status_token, msg_token, is_valido = validar_status_token(cfg_alvo)

        if not is_valido:
            cred = self._obter_credenciais_alvo_operador()
            if not cred:
                return
            usuario_alvo, senha_alvo_plana = cred

        from entidades.documentos_teste import verificar_alerta_poucos_documentos
        alerta_cpf = verificar_alerta_poucos_documentos("F", limite=5)
        if alerta_cpf:
            messagebox.showwarning("Aviso - Lista de CPFs Quase no Fim", alerta_cpf, parent=self)
        alerta_cnpj = verificar_alerta_poucos_documentos("J", limite=5)
        if alerta_cnpj:
            messagebox.showwarning("Aviso - Lista de CNPJs Quase no Fim", alerta_cnpj, parent=self)

        from logon import sessao_usuario_atual
        usucod = sessao_usuario_atual.get("usucod") or sessao_usuario_atual.get("login") or sessao_usuario_atual.get("usucod_apolo") or "JULIO"

        # Modal de Progresso
        prog_win = tk.Toplevel(self)
        prog_win.title("Exportação de Filtro para o Alvo")
        largura_p, altura_p = 560, 240
        from core import centralizar_janela
        centralizar_janela(prog_win, self, largura_p, altura_p)
        prog_win.resizable(False, False)
        prog_win.transient(self)
        prog_win.grab_set()

        banner = tk.Frame(prog_win, bg="#1A365D", height=50)
        banner.pack(side=tk.TOP, fill=tk.X)
        banner.pack_propagate(False)

        tk.Label(
            banner,
            text="⚡ Exportação em Lote para o Alvo",
            font=("Segoe UI", 11, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
        ).pack(side=tk.TOP, anchor="w", padx=16, pady=(6, 0))

        tk.Label(
            banner,
            text=f"Processando {total_entidades} registro(s) do filtro ativo...",
            font=("Segoe UI", 8),
            bg="#1A365D",
            fg="#CBD5E0",
        ).pack(side=tk.TOP, anchor="w", padx=16, pady=(1, 4))

        corpo = ttk.Frame(prog_win, padding=12)
        corpo.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        lbl_item = ttk.Label(corpo, text="Iniciando processamento...", font=("Segoe UI", 9))
        lbl_item.pack(side=tk.TOP, fill=tk.X, pady=(0, 6))

        pbar = ttk.Progressbar(corpo, orient=tk.HORIZONTAL, mode="determinate", maximum=total_entidades)
        pbar.pack(side=tk.TOP, fill=tk.X, pady=(0, 8))

        lbl_stats = ttk.Label(
            corpo,
            text="Sucesso: 0 | Pendências: 0 | Erros: 0",
            font=("Segoe UI", 9, "bold"),
            foreground="#1A365D",
        )
        lbl_stats.pack(side=tk.TOP, anchor="w", pady=(0, 8))

        cancelado = [False]

        def _cancelar():
            cancelado[0] = True
            lbl_item.config(text="Cancelando... Aguarde o término do item atual.")

        btn_cancelar = ttk.Button(corpo, text="✖ Cancelar Operação", command=_cancelar)
        btn_cancelar.pack(side=tk.BOTTOM, anchor="e")

        qtd_sucesso = 0
        qtd_pendencias = 0
        qtd_erros = 0
        erros_detalhes = []

        for idx, reg in enumerate(registros, start=1):
            if cancelado[0]:
                break

            geoentcod = str(reg.get("geoentcod") or "")
            nome_ent = str(reg.get("geoentnome") or reg.get("entnome") or geoentcod).strip()

            lbl_item.config(text=f"[{idx}/{total_entidades}] Cód: {geoentcod} - {nome_ent[:40]}")
            pbar["value"] = idx
            prog_win.update()

            obs = str(reg.get("entobservacoes") or reg.get("Entobservacoes") or reg.get("geoobservacoes") or "").strip().upper()
            if "[PEND" in obs:
                qtd_pendencias += 1
                erros_detalhes.append(f"{geoentcod} - {nome_ent}: Bloqueado por [PENDÊNCIAS]")
                lbl_stats.config(text=f"Sucesso: {qtd_sucesso} | Pendências: {qtd_pendencias} | Erros: {qtd_erros}")
                continue

            try:
                res = self._service.exportar_entidade_para_alvo(
                    geoentcod=geoentcod,
                    usuario_alvo=usuario_alvo,
                    senha_alvo_plana=senha_alvo_plana,
                    api_client=self._api_client,
                )
                if res.sucesso:
                    qtd_sucesso += 1
                    # Registra log de atividade oficial
                    self._repo.registrar_log_atividade(
                        usucod=usucod,
                        descricao=f"Exportou a Entidade: {geoentcod} e {nome_ent} para o alvo usando o geoapolo",
                    )
                else:
                    if "[PEND" in (res.mensagem or "").upper():
                        qtd_pendencias += 1
                        erros_detalhes.append(f"{geoentcod} - {nome_ent}: Bloqueado por [PENDÊNCIAS]")
                    else:
                        qtd_erros += 1
                        erros_detalhes.append(f"{geoentcod} - {nome_ent}: {res.mensagem}")
            except Exception as exc_loop:
                qtd_erros += 1
                erros_detalhes.append(f"{geoentcod} - {nome_ent}: {exc_loop}")

            lbl_stats.config(text=f"Sucesso: {qtd_sucesso} | Pendências: {qtd_pendencias} | Erros: {qtd_erros}")
            prog_win.update()

        try:
            prog_win.grab_release()
            prog_win.destroy()
        except Exception:
            pass

        total_proc = qtd_sucesso + qtd_pendencias + qtd_erros
        msg_resumo = (
            f"Processamento de exportação em lote finalizado!\n\n"
            f"• Total processado: {total_proc} de {total_entidades}\n"
            f"• Exportados com sucesso: {qtd_sucesso}\n"
            f"• Ignorados por [PENDÊNCIAS]: {qtd_pendencias}\n"
            f"• Erros ou falhas: {qtd_erros}"
        )
        if cancelado[0]:
            msg_resumo += "\n\n(Aviso: A operação foi cancelada antes de processar todos os itens.)"

        if qtd_erros > 0:
            try:
                caminho_log = salvar_log_erro_executavel(
                    nome_arquivo="exportacao_filtro_erros.log",
                    titulo="Gestão de Entidades - Erros na Exportação em Lote",
                    erro=RuntimeError("\n".join(erros_detalhes[:50])),
                    contexto=f"Exportação em lote com filtro: total={total_entidades}, erros={qtd_erros}"
                )
                msg_resumo += f"\n\nOs detalhes dos erros foram registrados em:\n{caminho_log}"
            except Exception:
                pass

        messagebox.showinfo("Exportação em Lote Concluída", msg_resumo, parent=self)
        self._carregar_dados()


    def _acao_ignorar(self):
        reg = self._obter_registro_selecionado()
        if not reg:
            messagebox.showwarning("Aviso", "Selecione uma entidade na lista primeiro.", parent=self)
            return

        if not messagebox.askyesno("Confirmação", "Confirma a não atualização deste registro no Alvo?", parent=self):
            return

        geoentcod = str(reg.get("geoentcod") or "")
        resultado: ResultadoOperacao = self._service.executar_acao_ignorar(
            geoentcod=geoentcod,
            usucod_apolo="APOLO_SYS",
            cod_empresa="001",
            cod_usuario="ADMIN",
        )

        if resultado.sucesso:
            messagebox.showinfo("Sucesso", resultado.mensagem, parent=self)
            self._carregar_dados()
        else:
            messagebox.showerror("Erro", resultado.mensagem, parent=self)

    def destroy(self):
        EntidadesView._instancia_ativa = None
        if hasattr(self, "_after_id") and self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        if hasattr(self, "_criou_conexao") and self._criou_conexao and self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None
        super().destroy()
