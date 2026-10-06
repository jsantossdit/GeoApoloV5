"""
Formulário de Cadastro e Manutenção de Entidades (FrmCadEntidade).
GeoApolo V5 - Equivalente e evolução direta de unt_cadentidades.pas / unt_cadentidades.dfm (Delphi).
"""

import os
import sys
import logging
from pathlib import Path
import re
from datetime import datetime, date
from typing import Optional, Dict, Any, Callable, List, Tuple
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText

# Garante que o diretório raiz esteja no sys.path
_raiz_projeto = str(Path(__file__).resolve().parent.parent)
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

from core import obter_caminho_recurso, centralizar_janela
try:
    from core.viacep import consultar_cep
except (ImportError, ModuleNotFoundError):
    consultar_cep = None

logger = logging.getLogger(__name__)


def formatar_data_br(val: Any) -> str:
    """Converte datas do banco (datetime, date, YYYY-MM-DD) para o formato brasileiro DD/MM/AAAA."""
    if not val:
        return ""
    if isinstance(val, (datetime, date)):
        return val.strftime("%d/%m/%Y")
    s = str(val).strip()
    if not s or s.lower() in ("none", "null", "none/none/none"):
        return ""
    if " " in s:
        s = s.split(" ")[0]
    if "T" in s:
        s = s.split("T")[0]
    partes_br = s.split("/")
    if len(partes_br) == 3 and len(partes_br[2]) == 4:
        return s
    partes_iso = s.split("-")
    if len(partes_iso) == 3 and len(partes_iso[0]) == 4:
        ano, mes, dia = partes_iso[0], partes_iso[1], partes_iso[2]
        return f"{dia.zfill(2)}/{mes.zfill(2)}/{ano}"
    return s


def converter_data_para_db(val: Any) -> Optional[str]:
    """Converte data digitada (DD/MM/AAAA) para formato aceito no banco (YYYY-MM-DD)."""
    if not val:
        return None
    s = str(val).strip()
    if not s or s in ("None", "null") or not re.search(r"\d", s):
        return None
    partes = s.split("/")
    if len(partes) == 3:
        dia, mes, ano = partes[0].strip(), partes[1].strip(), partes[2].strip()
        if dia.isdigit() and mes.isdigit() and ano.isdigit() and len(ano) == 4:
            return f"{ano.zfill(4)}-{mes.zfill(2)}-{dia.zfill(2)}"
    partes_iso = s.split("-")
    if len(partes_iso) == 3 and len(partes_iso[0]) == 4:
        return s[:10]
    return s if s else None


def _aplicar_mascara_data(event, widget):
    """Aplica formatação automática DD/MM/AAAA enquanto o usuário digita."""
    if event.keysym in ("Left", "Right", "Tab", "Return", "ISO_Left_Tab", "Home", "End", "Escape"):
        return
    if event.keysym in ("BackSpace", "Delete"):
        return
    texto = widget.get()
    apenas_digitos = re.sub(r"\D", "", texto)[:8]
    if not apenas_digitos:
        return
    if len(apenas_digitos) < 2:
        formatado = apenas_digitos
    elif len(apenas_digitos) == 2:
        formatado = f"{apenas_digitos[:2]}/"
    elif len(apenas_digitos) < 4:
        formatado = f"{apenas_digitos[:2]}/{apenas_digitos[2:]}"
    elif len(apenas_digitos) == 4:
        formatado = f"{apenas_digitos[:2]}/{apenas_digitos[2:4]}/"
    else:
        formatado = f"{apenas_digitos[:2]}/{apenas_digitos[2:4]}/{apenas_digitos[4:]}"
    if texto != formatado:
        widget.delete(0, tk.END)
        widget.insert(0, formatado)
        widget.icursor(len(formatado))


def _calcular_idade(data_str: str) -> Optional[int]:
    """Calcula a idade em anos completos a partir de uma data DD/MM/AAAA."""
    if not data_str:
        return None
    try:
        partes = data_str.strip().split("/")
        if len(partes) == 3:
            d, m, a = int(partes[0]), int(partes[1]), int(partes[2])
            hoje = date.today()
            nasc = date(a, m, d)
            return hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
    except Exception:
        pass
    return None




class ToolTip:
    """Exibe tooltip flutuante sobre um widget Tkinter com visual limpo e consistente."""

    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        try:
            x = self.widget.winfo_rootx() + 15
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        except Exception:
            return
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        lbl = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#1E293B",
            foreground="#FFFFFF",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Segoe UI", 8),
            padx=6,
            pady=3,
        )
        lbl.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


class LookupLabel(ttk.Label):
    """ttk.Label com métodos get(), set(), insert() e delete() para compatibilidade plena com campos de lookup."""

    def __init__(self, master=None, **kwargs):
        self._var = tk.StringVar(value=kwargs.pop("text", ""))
        super().__init__(master, textvariable=self._var, **kwargs)

    def get(self) -> str:
        return self._var.get()

    def set(self, val: str):
        self._var.set(str(val) if val is not None else "")

    def insert(self, index, val: str):
        self._var.set(str(val) if val is not None else "")

    def delete(self, first, last=None):
        self._var.set("")


class VarAdapter:
    """Adaptador de tk.StringVar para compatibilidade com interface de Combobox/Entry (get/set)."""

    def __init__(self, var: tk.StringVar):
        self._var = var

    def get(self) -> str:
        return self._var.get()

    def set(self, val: str):
        self._var.set(str(val) if val is not None else "")


class DlgConsultaGenerica(tk.Toplevel):
    """
    Janela modal de consulta e seleção de lookups (cidades, categorias, cargos, cobrança, dioceses, etc.).
    Possui filtro em tempo real, grid com scroll e seleção via duplo clique ou Enter.
    """

    def __init__(
        self,
        parent,
        titulo: str,
        colunas: List[Tuple[str, str, int]],
        dados: List[Dict[str, Any]],
        on_selecionar: Callable[[Dict[str, Any]], None],
    ):
        super().__init__(parent)
        self.title(titulo)
        self.geometry("700x460")
        self.minsize(520, 340)
        centralizar_janela(self, parent, 700, 460)
        self.transient(parent)
        self.grab_set()

        self._colunas = colunas
        self._dados_originais = dados or []
        self._on_selecionar = on_selecionar

        self._criar_ui()
        self._popular_grid(self._dados_originais)

        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<Return>", lambda e: self._confirmar_selecao())
        self.txt_busca.focus_set()

    def _criar_ui(self):
        # Barra de Pesquisa
        top = ttk.Frame(self, padding=10)
        top.pack(fill=tk.X)

        ttk.Label(top, text="🔍 Filtrar:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self.txt_busca = ttk.Entry(top)
        self.txt_busca.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.txt_busca.bind("<KeyRelease>", self._filtrar)

        self.lbl_contagem = ttk.Label(top, text=f"{len(self._dados_originais)} registro(s)", font=("Segoe UI", 8))
        self.lbl_contagem.pack(side=tk.RIGHT)

        # Grid
        mid = ttk.Frame(self, padding=(10, 0, 10, 0))
        mid.pack(fill=tk.BOTH, expand=True)

        col_ids = [c[0] for c in self._colunas]
        self.tree = ttk.Treeview(mid, columns=col_ids, show="headings", height=13)
        for cid, ctit, clarg in self._colunas:
            self.tree.heading(cid, text=ctit)
            self.tree.column(cid, width=clarg, anchor="w")

        sc_y = ttk.Scrollbar(mid, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sc_y.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", lambda e: (self._confirmar_selecao(), "break")[1])
        self.tree.bind("<Return>", lambda e: (self._confirmar_selecao(), "break")[1])

        # Rodapé
        bottom = ttk.Frame(self, padding=10)
        bottom.pack(fill=tk.X)

        btn_sel = ttk.Button(bottom, text="✔ Selecionar (Enter)", command=self._confirmar_selecao)
        btn_sel.pack(side=tk.RIGHT, padx=(8, 0))

        btn_canc = ttk.Button(bottom, text="Fechar (Esc)", command=self.destroy)
        btn_canc.pack(side=tk.RIGHT)

    def _popular_grid(self, lista: List[Dict[str, Any]]):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for reg in lista:
            valores = [str(reg.get(cid, "") or "") for cid, _, _ in self._colunas]
            self.tree.insert("", tk.END, values=valores)
        self.lbl_contagem.config(text=f"{len(lista)} registro(s)")
        itens = self.tree.get_children()
        if itens:
            self.tree.selection_set(itens[0])
            self.tree.focus(itens[0])

    def _filtrar(self, event=None):
        termo = self.txt_busca.get().strip().lower()
        if not termo:
            self._popular_grid(self._dados_originais)
            return
        filtrados = []
        for reg in self._dados_originais:
            match = False
            for cid, _, _ in self._colunas:
                val = str(reg.get(cid, "") or "").lower()
                if termo in val:
                    match = True
                    break
            if match:
                filtrados.append(reg)
        self._popular_grid(filtrados)

    def _confirmar_selecao(self):
        sel = self.tree.selection()
        if not sel:
            return "break"
        vals = self.tree.item(sel[0], "values")
        if not vals:
            return "break"
        d = {}
        for i, (cid, _, _) in enumerate(self._colunas):
            d[cid] = vals[i] if i < len(vals) else ""
        try:
            self.destroy()
        except Exception:
            pass
        self._on_selecionar(d)
        return "break"


class FrmCadEntidade(tk.Toplevel):
    """
    Formulário para edição e manutenção cadastral de entidades.
    Corresponde ao Tfrmcadentidade do Delphi.
    """
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

    def __init__(
        self,
        parent=None,
        registro: Optional[Dict[str, Any]] = None,
        base_dados: str = "GeoApolo",
        on_salvar: Optional[Callable[[], None]] = None,
        connection=None,
        modo_inclusao: bool = False,
    ):
        if getattr(self, "_ja_inicializada", False):
            return
        super().__init__(parent)
        self._ja_inicializada = True
        FrmCadEntidade._instancia_ativa = self
        self.parent = parent
        self.registro = registro or {}
        self.base_dados = base_dados
        self.on_salvar = on_salvar
        self._conn = connection
        self.modo_inclusao = modo_inclusao or not bool(registro and (registro.get("geoentcod") or registro.get("entcod")))

        self.title("Manutenção de Entidades - GeoAlvo" if not self.modo_inclusao else "Nova Entidade - Inclusão - GeoAlvo")
        self.geometry("1040x650")
        self.minsize(880, 520)

        # Centraliza a janela em relação ao parent/principal
        centralizar_janela(self, parent, 1040, 650)
        self._aplicar_icone()

        if parent:
            try:
                self.transient(parent)
                self.grab_set()
            except Exception:
                pass

        # Dependências de serviço e repositório
        self._service = None
        self._repo = None
        self._inicializar_dependencias()

        # Constrói UI e popula dados
        self._criar_interface()
        self._preencher_dados(self.registro)
        if self.modo_inclusao:
            self._configurar_novo_registro()

        self._configurar_maiusculas_e_enter()

        # Atalhos e fechamento
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<F3>", lambda e: self.salvar())

    def _aplicar_icone(self):
        caminhos = [
            obter_caminho_recurso(os.path.join("Imagens", "entidades.png")),
            obter_caminho_recurso(os.path.join("Imagens", "GeoApolo_Icon.ico")),
        ]
        for c in caminhos:
            if os.path.exists(c):
                try:
                    if c.endswith(".ico"):
                        self.iconbitmap(c)
                    else:
                        img = tk.PhotoImage(file=c)
                        self.iconphoto(False, img)
                        self._icon_ref = img
                    break
                except Exception:
                    pass

    def _configurar_novo_registro(self):
        """Prepara os campos do formulário para inclusão de novo registro."""
        from core.recursos import geoapolo_configcod
        try:
            novo_cod = geoapolo_configcod("1.01", "USER_geoapolo_entidade", "Sim", connection=self._conn)
            if hasattr(self, "txt_geoentcod") and self.txt_geoentcod.winfo_exists():
                orig_state = str(self.txt_geoentcod.cget("state"))
                if orig_state == "readonly":
                    self.txt_geoentcod.config(state="normal")
                self.txt_geoentcod.delete(0, tk.END)
                self.txt_geoentcod.insert(0, str(novo_cod).strip())
                if orig_state == "readonly":
                    self.txt_geoentcod.config(state="readonly")
        except Exception as exc:
            logger.warning("Falha ao gerar próximo código sequencial: %s", exc)

        hoje_br = datetime.now().strftime("%d/%m/%Y")
        if hasattr(self, "txt_data_cad") and self.txt_data_cad.winfo_exists():
            orig_state = str(self.txt_data_cad.cget("state"))
            if orig_state == "readonly":
                self.txt_data_cad.config(state="normal")
            self.txt_data_cad.delete(0, tk.END)
            self.txt_data_cad.insert(0, hoje_br)
            if orig_state == "readonly":
                self.txt_data_cad.config(state="readonly")

        if hasattr(self, "cbo_tipofj") and not self.cbo_tipofj.get():
            self.cbo_tipofj.set("F - Física")
        if hasattr(self, "cbo_falecido") and not self.cbo_falecido.get():
            self.cbo_falecido.set("Não")
        if hasattr(self, "cbo_estadocivil") and not self.cbo_estadocivil.get():
            self.cbo_estadocivil.set("SOLTEIRO(A)")
        if hasattr(self, "cbo_sexo") and not self.cbo_sexo.get():
            self.cbo_sexo.set("MASCULINO")
        if hasattr(self, "cbo_geracarne") and not self.cbo_geracarne.get():
            self.cbo_geracarne.set("Sim")
        if hasattr(self, "cbo_recebelembrete") and not self.cbo_recebelembrete.get():
            self.cbo_recebelembrete.set("Sim")
        if hasattr(self, "cbo_escolaridade") and not self.cbo_escolaridade.get():
            self.cbo_escolaridade.set("Nenhum")
        if hasattr(self, "txt_cargo_cod") and not self.txt_cargo_cod.get().strip():
            self.txt_cargo_cod.delete(0, tk.END)
            self.txt_cargo_cod.insert(0, "04")
            if hasattr(self, "lbl_cargo_nome"):
                self.lbl_cargo_nome.config(text="OUTROS")

        if hasattr(self, "notebook") and hasattr(self, "tab_principal"):
            self.notebook.select(self.tab_principal)
        if hasattr(self, "txt_nome"):
            self.txt_nome.focus_set()

    def _inicializar_dependencias(self):
        try:
            from entidades.database import obter_conexao_banco
            from entidades.repository import EntidadeRepository
            from entidades.service import EntidadeService

            if self._conn is None:
                self._conn = obter_conexao_banco()
            self._repo = EntidadeRepository(self._conn)
            self._service = EntidadeService(self._repo)
        except Exception as exc:
            logger.warning("Falha ao inicializar serviço de entidades em FrmCadEntidade: %s", exc)
            self._repo = None
            self._service = None

    def _criar_interface(self):
        # 1. Header Superior
        header = tk.Frame(self, bg="#1E3A8A", height=54)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)

        cod_geo = str(self.registro.get("geoentcod") or "").strip()
        cod_alvo = str(self.registro.get("entcod") or "").strip()
        nome = self.registro.get("geoentnome") or self.registro.get("entnome") or ""

        if cod_geo and cod_alvo:
            tag_cod = f"Geo: {cod_geo} | Alvo: {cod_alvo}"
        elif cod_alvo:
            tag_cod = f"Alvo: {cod_alvo}"
        elif cod_geo:
            tag_cod = f"Geo: {cod_geo}"
        else:
            tag_cod = "NOVO"

        self.lbl_tit = tk.Label(
            header,
            text=f"📋 Manutenção de Entidade: [{tag_cod}] {nome}",
            font=("Segoe UI", 12, "bold"),
            bg="#1E3A8A",
            fg="white",
            anchor="w",
        )
        self.lbl_tit.pack(side=tk.LEFT, padx=16, pady=8)

        lbl_base = tk.Label(
            header,
            text=f"Base: {self.base_dados}",
            font=("Segoe UI", 9, "bold"),
            bg="#2563EB",
            fg="white",
            padx=8,
            pady=2,
        )
        lbl_base.pack(side=tk.RIGHT, padx=16, pady=12)

        # 2. Barra de Ferramentas / Ações
        toolbar = tk.Frame(self, bg="#E2E8F0", height=42, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        toolbar.pack_propagate(False)

        btn_salvar = ttk.Button(toolbar, text="💾 Salvar (F3)", command=self.salvar)
        btn_salvar.pack(side=tk.LEFT, padx=8, pady=6)

        btn_sair = ttk.Button(toolbar, text="🚪 Fechar (Esc)", command=self.destroy)
        btn_sair.pack(side=tk.RIGHT, padx=12, pady=6)

        # 3. Notebook com Abas do Cadastro
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=8)

        self.tab_principal = ttk.Frame(self.notebook, padding=8)
        self.tab_complementar = ttk.Frame(self.notebook, padding=6)
        self.tab_categorias = ttk.Frame(self.notebook, padding=8)
        self.tab_contatos = ttk.Frame(self.notebook, padding=6)
        self.tab_historico = ttk.Frame(self.notebook, padding=8)
        self.tab_documentos = ttk.Frame(self.notebook, padding=8)
        self.tab_observacoes = ttk.Frame(self.notebook, padding=8)

        self.notebook.add(self.tab_principal, text="  Identificação / Principal  ")
        self.notebook.add(self.tab_complementar, text="  Complementar  ")
        self.notebook.add(self.tab_categorias, text="  Categorias  ")
        self.notebook.add(self.tab_contatos, text="  Contatos & Comunicação  ")
        self.notebook.add(self.tab_historico, text="  Histórico Entidade  ")
        self.notebook.add(self.tab_documentos, text="  Documentos  ")
        self.notebook.add(self.tab_observacoes, text="  Observações  ")

        self._build_tab_principal()
        self._build_tab_complementar()
        self._build_tab_categorias()
        self._build_tab_contatos()
        self._build_tab_historico()
        self._build_tab_documentos()
        self._build_tab_observacoes()

        # 4. Status Bar Inferior
        self.statusbar = tk.Label(
            self,
            text=f"Entidade carregada da base {self.base_dados}. Pronto para edição.",
            font=("Segoe UI", 9),
            bd=1,
            relief=tk.SUNKEN,
            anchor="w",
            bg="#F1F5F9",
            fg="#475569",
            padx=10,
            pady=3,
        )
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Habilita busca/digitação dinâmica em todos os combos com conteúdo
        self._aplicar_autocomplete_todos_combos()
        self._configurar_maiusculas_e_enter()


    # -------------------------------------------------------------
    # Construção das Abas
    # -------------------------------------------------------------
    def _build_tab_principal(self):
        f_container = self.tab_principal
        self.tab_endereco = self.tab_principal  # Alias de compatibilidade retroativa

        canvas = tk.Canvas(f_container, highlightthickness=0)
        sc_y = ttk.Scrollbar(f_container, orient=tk.VERTICAL, command=canvas.yview)
        f = ttk.Frame(canvas, padding=6)

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        f.bind("<Configure>", _on_frame_configure)
        win_id = canvas.create_window((0, 0), window=f, anchor="nw")

        def _on_canvas_configure(event):
            canvas.itemconfig(win_id, width=event.width)

        canvas.bind("<Configure>", _on_canvas_configure)
        canvas.configure(yscrollcommand=sc_y.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Suporte ao scroll do mouse
        def _on_mousewheel(event):
            try:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass
        canvas.bind("<MouseWheel>", _on_mousewheel)

        # Linha 0: Códigos, Tratamento, Pessoa (F/J) e Falecido
        row0 = ttk.Frame(f)
        row0.pack(fill=tk.X, pady=3)

        ttk.Label(row0, text="Cód. Geo:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_geoentcod = ttk.Entry(row0, width=10, state="readonly")
        self.txt_geoentcod.pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(row0, text="Cód. Alvo:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_entcod = ttk.Entry(row0, width=10, state="readonly")
        self.txt_entcod.pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(row0, text="Tratamento:").pack(side=tk.LEFT, padx=(0, 4))
        self.cbo_tipotrat = ttk.Combobox(row0, width=14, state="readonly")
        self.cbo_tipotrat.pack(side=tk.LEFT, padx=(0, 12))
        self.txt_tipotrat = self.cbo_tipotrat

        ttk.Label(row0, text="Pessoa:").pack(side=tk.LEFT, padx=(0, 4))
        self.cbo_tipofj = ttk.Combobox(row0, values=["F", "J"], width=5, state="readonly")
        self.cbo_tipofj.set("F")
        self.cbo_tipofj.pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(row0, text="Falecido:").pack(side=tk.LEFT, padx=(0, 4))
        self.cbo_falecido = ttk.Combobox(row0, values=["Não", "Sim"], width=6, state="readonly")
        self.cbo_falecido.set("Não")
        self.cbo_falecido.pack(side=tk.LEFT)

        # Linha 1: Nome e Nome Fantasia
        row1 = ttk.Frame(f)
        row1.pack(fill=tk.X, pady=3)

        ttk.Label(row1, text="Nome / Razão Social:*").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_nome = ttk.Entry(row1, width=44)
        self.txt_nome.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row1, text="Nome Fantasia:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_nomefantasia = ttk.Entry(row1, width=38)
        self.txt_nomefantasia.pack(side=tk.LEFT)

        # Linha 2: Documentos e Gênero
        row2 = ttk.Frame(f)
        row2.pack(fill=tk.X, pady=3)

        ttk.Label(row2, text="CPF / CNPJ:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_cpf_cnpj = ttk.Entry(row2, width=18)
        self.txt_cpf_cnpj.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row2, text="RG / Inscrição Estadual:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_rg_ie = ttk.Entry(row2, width=18)
        self.txt_rg_ie.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row2, text="Gênero (Sexo):").pack(side=tk.LEFT, padx=(0, 4))
        self.cbo_sexo = ttk.Combobox(row2, values=["MASCULINO", "FEMININO", "NENHUM"], width=13, state="readonly")
        self.cbo_sexo.set("MASCULINO")
        self.cbo_sexo.pack(side=tk.LEFT)

        # Linha 3: Endereço (CEP, Logradouro, Endereço, Número)
        row3 = ttk.Frame(f)
        row3.pack(fill=tk.X, pady=3)

        ttk.Label(row3, text="CEP:*").pack(side=tk.LEFT, padx=(0, 4))
        vcmd_cep = (self.register(lambda p: len(p) <= 10), "%P")
        self.txt_cep = ttk.Entry(row3, width=12, validate="key", validatecommand=vcmd_cep)
        self.txt_cep.pack(side=tk.LEFT, padx=(0, 14))
        self.txt_cep.bind("<Return>", self._consultar_viacep)
        self.txt_cep.bind("<FocusOut>", self._consultar_viacep)

        ttk.Label(row3, text="Tipo:").pack(side=tk.LEFT, padx=(0, 4))
        self.cbo_tipolograd = ttk.Combobox(row3, width=8)
        self.cbo_tipolograd.pack(side=tk.LEFT, padx=(0, 14))
        self.txt_tipolograd = self.cbo_tipolograd

        ttk.Label(row3, text="Endereço / Logradouro:*").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_ender = ttk.Entry(row3, width=38)
        self.txt_ender.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row3, text="Número:*").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_enderno = ttk.Entry(row3, width=8)
        self.txt_enderno.pack(side=tk.LEFT)

        # Linha 4: Complemento, Bairro e Local de Referência
        row4 = ttk.Frame(f)
        row4.pack(fill=tk.X, pady=3)

        ttk.Label(row4, text="Complemento:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_endercomp = ttk.Entry(row4, width=24)
        self.txt_endercomp.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row4, text="Bairro:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_bair = ttk.Entry(row4, width=26)
        self.txt_bair.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row4, text="Local Referência:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_referencia = ttk.Entry(row4, width=32)
        self.txt_referencia.pack(side=tk.LEFT)

        # Linha 5: Cidade, UF e Caixa Postal
        row5 = ttk.Frame(f)
        row5.pack(fill=tk.X, pady=3)

        ttk.Label(row5, text="Cód. Cidade:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_cidcod = ttk.Entry(row5, width=8)
        self.txt_cidcod.pack(side=tk.LEFT, padx=(0, 2))
        self.txt_cidcod.bind("<Return>", self._on_cidcod_action)
        self.txt_cidcod.bind("<FocusOut>", self._on_cidcod_focus_out)
        self.btn_busca_cid = ttk.Button(row5, text="🔍", width=3, command=self._abrir_consulta_cidade)
        self.btn_busca_cid.pack(side=tk.LEFT, padx=(0, 10))
        ToolTip(self.btn_busca_cid, "Pesquisar Cidade")

        ttk.Label(row5, text="Cidade:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_cidade = ttk.Entry(row5, width=30)
        self.txt_cidade.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row5, text="UF:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_uf = ttk.Entry(row5, width=5)
        self.txt_uf.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row5, text="Caixa Postal:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_cxapost = ttk.Entry(row5, width=12)
        self.txt_cxapost.pack(side=tk.LEFT)

        # Linha 6: Estado Civil, Datas (Nascimento e Cadastro), Escolaridade
        row6 = ttk.Frame(f)
        row6.pack(fill=tk.X, pady=3)

        ttk.Label(row6, text="Estado Civil:").pack(side=tk.LEFT, padx=(0, 4))
        self.cbo_estadocivil = ttk.Combobox(
            row6,
            values=['CASADO(A)', 'DESQUITADO(A)', 'DIVORCIADO(A)', 'OUTRO', 'SEPARADO(A)', 'SOLTEIRO(A)', 'VIÚVO(A)'],
            width=15,
            state="readonly"
        )
        self.cbo_estadocivil.set("SOLTEIRO(A)")
        self.cbo_estadocivil.pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(row6, text="Data Nascimento:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_dtnasc = ttk.Entry(row6, width=12)
        self.txt_dtnasc.pack(side=tk.LEFT, padx=(0, 12))
        self.txt_dtnasc.bind("<KeyRelease>", lambda e: (_aplicar_mascara_data(e, self.txt_dtnasc), self._verificar_alerta_menor()))
        self.txt_dtnasc.bind("<FocusOut>", self._verificar_alerta_menor)

        ttk.Label(row6, text="Data Cadastro:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_dtcad = ttk.Entry(row6, width=12)
        self.txt_dtcad.pack(side=tk.LEFT, padx=(0, 12))
        self.txt_dtcad.bind("<KeyRelease>", lambda e: _aplicar_mascara_data(e, self.txt_dtcad))

        ttk.Label(row6, text="Escolaridade:").pack(side=tk.LEFT, padx=(0, 4))
        self.cbo_escolaridade = ttk.Combobox(
            row6,
            values=[
                'Superior Incompleto', 'Superior Completo', 'Segundo Grau Incompleto',
                'Segundo Grau Completo', 'Primeiro Grau Incompleto', 'Primeiro Grau Completo',
                'Pós-Graduado', 'Mestrado', 'Doutorado', 'Analfabeto', 'Nenhum'
            ],
            width=22
        )
        self.cbo_escolaridade.pack(side=tk.LEFT)
        self.txt_escolaridade = self.cbo_escolaridade

        # Linha 7: Ocupação / Cargo
        row7 = ttk.Frame(f)
        row7.pack(fill=tk.X, pady=3)

        ttk.Label(row7, text="Ocupação / Cargo (Cód):").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_cargo_cod = ttk.Entry(row7, width=8)
        self.txt_cargo_cod.pack(side=tk.LEFT, padx=(0, 2))
        self.btn_busca_cargo = ttk.Button(row7, text="🔍", width=3, command=self._abrir_consulta_cargo)
        self.btn_busca_cargo.pack(side=tk.LEFT, padx=(0, 10))
        ToolTip(self.btn_busca_cargo, "Pesquisar Cargo / Ocupação")

        ttk.Label(row7, text="Nome Cargo:").pack(side=tk.LEFT, padx=(0, 4))
        self.lbl_cargo_nome = LookupLabel(row7, text="", font=("Segoe UI", 9, "bold"), foreground="#1E3A8A")
        self.lbl_cargo_nome.pack(side=tk.LEFT, padx=(0, 10))
        self.txt_cargo_nome = self.lbl_cargo_nome
        self.txt_cargo = self.txt_cargo_cod

        self._carregar_combos_principal()
        self._carregar_combos_endereco()

    def _build_tab_endereco(self):
        """Método de compatibilidade retroativa; campos de endereço foram unificados na aba principal."""
        pass

    def _carregar_combos_principal(self):
        # 1. Tipo de Tratamento (todos os registros disponíveis)
        tratamentos = []
        if self._service:
            try:
                tratamentos = self._service.listar_tipos_tratamento(base_dados=self.base_dados)
            except Exception:
                pass
        if not tratamentos and self._repo:
            try:
                tratamentos = self._repo.listar_tipos_tratamento(base_dados=self.base_dados)
            except Exception:
                pass
        if not tratamentos:
            tratamentos = [
                {"codigo": "01", "abreviatura": "SR", "descricao": "SR - SENHOR"},
                {"codigo": "02", "abreviatura": "SRA", "descricao": "SRA - SENHORA"},
                {"codigo": "03", "abreviatura": "SRTA", "descricao": "SRTA - SENHORITA"},
                {"codigo": "04", "abreviatura": "DR", "descricao": "DR - DOUTOR"},
                {"codigo": "05", "abreviatura": "DRA", "descricao": "DRA - DOUTORA"},
                {"codigo": "06", "abreviatura": "PROF", "descricao": "PROF - PROFESSOR"},
                {"codigo": "07", "abreviatura": "PROFA", "descricao": "PROFA - PROFESSORA"},
                {"codigo": "08", "abreviatura": "PADRE", "descricao": "PADRE - PADRE"},
                {"codigo": "09", "abreviatura": "DOM", "descricao": "DOM - DOM"},
                {"codigo": "10", "abreviatura": "IRMA", "descricao": "IRMA - IRMÃ"},
                {"codigo": "11", "abreviatura": "FREI", "descricao": "FREI - FREI"},
                {"codigo": "12", "abreviatura": "DIACONO", "descricao": "DIÁCONO - DIÁCONO"},
                {"codigo": "13", "abreviatura": "PASTOR", "descricao": "PASTOR - PASTOR"},
                {"codigo": "14", "abreviatura": "PASTORA", "descricao": "PASTORA - PASTORA"},
                {"codigo": "15", "abreviatura": "BISPO", "descricao": "BISPO - BISPO"},
                {"codigo": "16", "abreviatura": "ARCEBISPO", "descricao": "ARCEBISPO - ARCEBISPO"},
                {"codigo": "17", "abreviatura": "MONSENHOR", "descricao": "MONSENHOR - MONSENHOR"},
                {"codigo": "18", "abreviatura": "CARDEAL", "descricao": "CARDEAL - CARDEAL"},
                {"codigo": "19", "abreviatura": "PAPA", "descricao": "PAPA - PAPA"},
                {"codigo": "20", "abreviatura": "MINISTRO", "descricao": "MINISTRO - MINISTRO"},
                {"codigo": "21", "abreviatura": "JUIZ", "descricao": "JUIZ - JUIZ"},
                {"codigo": "22", "abreviatura": "DEPUTADO", "descricao": "DEPUTADO - DEPUTADO"},
                {"codigo": "23", "abreviatura": "SENADOR", "descricao": "SENADOR - SENADOR"},
                {"codigo": "24", "abreviatura": "PREFEITO", "descricao": "PREFEITO - PREFEITO"},
            ]
        vals_trat = []
        for t in tratamentos:
            v = str(t.get("abreviatura") or t.get("descricao") or t.get("codigo") or "").strip()
            if v and v not in vals_trat:
                vals_trat.append(v)
        self.cbo_tipotrat["values"] = sorted(vals_trat)

        # 2. Escolaridade
        escolaridades_delphi = [
            'Superior Incompleto', 'Superior Completo', 'Segundo Grau Incompleto',
            'Segundo Grau Completo', 'Primeiro Grau Incompleto', 'Primeiro Grau Completo',
            'Pós-Graduado', 'Mestrado', 'Doutorado', 'Analfabeto', 'Nenhum'
        ]
        self.cbo_escolaridade["values"] = escolaridades_delphi

    def _carregar_combos_endereco(self):
        logradouros = []
        if self._service:
            try:
                logradouros = self._service.listar_tipos_logradouro()
            except Exception:
                pass
        if not logradouros:
            logradouros = [
                {"abrev": "RUA"}, {"abrev": "AV"}, {"abrev": "AL"}, {"abrev": "PCA"},
                {"abrev": "ROD"}, {"abrev": "TRV"}, {"abrev": "EST"}, {"abrev": "CHAC"},
                {"abrev": "LOT"}, {"abrev": "RES"}, {"abrev": "VIA"}, {"abrev": "VL"},
                {"abrev": "OUT"},
            ]
        vals = [l.get("abrev") for l in logradouros if l.get("abrev")]
        self.cbo_tipolograd["values"] = vals
        self._configurar_autocomplete_logradouro()

    def _build_tab_categorias(self):
        f = self.tab_categorias

        # Painel superior de ações e busca de categorias
        top_frame = ttk.LabelFrame(f, text=" Associar Nova Categoria ", padding=8)
        top_frame.pack(fill=tk.X, padx=4, pady=4)

        ttk.Label(top_frame, text="Código Categoria:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_categ_cod = ttk.Entry(top_frame, width=12)
        self.txt_categ_cod.pack(side=tk.LEFT, padx=(0, 2))
        self.txt_categ_cod.bind("<FocusOut>", self._on_categ_focusout)
        self.txt_categ_cod.bind("<Return>", self._on_categ_focusout)

        self.btn_busca_categ = ttk.Button(top_frame, text="🔍", width=3, command=self._abrir_consulta_categoria)
        self.btn_busca_categ.pack(side=tk.LEFT, padx=(0, 12))
        ToolTip(self.btn_busca_categ, "Pesquisar Categorias")

        ttk.Label(top_frame, text="Descrição da Categoria:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_categ_nome = ttk.Entry(top_frame, width=32)
        self.txt_categ_nome.pack(side=tk.LEFT, padx=(0, 16))

        self.btn_add_categ = ttk.Button(top_frame, text="➕", width=4, command=self._adicionar_categoria)
        self.btn_add_categ.pack(side=tk.LEFT, padx=(0, 8))
        ToolTip(self.btn_add_categ, "Inserir/Atualizar a informação")

        self.btn_del_categ = ttk.Button(top_frame, text="❌", width=4, command=self._remover_categoria)
        self.btn_del_categ.pack(side=tk.LEFT)
        ToolTip(self.btn_del_categ, "Remover Categoria")

        # Grid / Treeview com categorias vinculadas
        grid_frame = ttk.LabelFrame(f, text=" Categorias Vinculadas à Entidade ", padding=8)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        cols = ("codigo", "descricao")
        self.tree_categorias = ttk.Treeview(grid_frame, columns=cols, show="headings", height=12)
        self.tree_categorias.heading("codigo", text="Código Categoria")
        self.tree_categorias.heading("descricao", text="Descrição da Categoria")
        self.tree_categorias.column("codigo", width=180, anchor="w")
        self.tree_categorias.column("descricao", width=540, anchor="w")

        sc_y = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.tree_categorias.yview)
        self.tree_categorias.configure(yscrollcommand=sc_y.set)

        self.tree_categorias.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_categorias.bind("<Delete>", lambda e: self._remover_categoria())
        self.tree_categorias.bind("<Double-1>", self._on_categ_double_click)

    def _build_tab_complementar(self):
        f = self.tab_complementar
        self.sub_notebook = ttk.Notebook(f)
        self.sub_notebook.pack(fill=tk.BOTH, expand=True)

        self.subtab_pessoal = ttk.Frame(self.sub_notebook, padding=8)
        self.subtab_financeiro = ttk.Frame(self.sub_notebook, padding=8)
        self.subtab_infocompl = ttk.Frame(self.sub_notebook, padding=8)
        self.subtab_endcobranca = ttk.Frame(self.sub_notebook, padding=8)
        self.subtab_endentrega = ttk.Frame(self.sub_notebook, padding=8)

        # Aliases para compatibilidade retroativa
        self.tab_pessoal = self.subtab_pessoal
        self.tab_financeiro = self.subtab_financeiro

        self.sub_notebook.add(self.subtab_pessoal, text="  Dados Pessoais  ")
        self.sub_notebook.add(self.subtab_financeiro, text="  Financeiro  ")
        self.sub_notebook.add(self.subtab_infocompl, text="  Informações Complementares  ")

        self._build_subtab_dados_pessoais()
        self._build_subtab_financeiro()
        self._build_subtab_infocompl()
        self._build_subtab_endcobranca()
        self._build_subtab_endentrega()

    def _build_subtab_dados_pessoais(self):
        f = self.subtab_pessoal

        row0 = ttk.Frame(f)
        row0.pack(fill=tk.X, pady=4)

        ttk.Label(row0, text="Nome do Pai:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_nomepai = ttk.Entry(row0, width=42)
        self.txt_nomepai.pack(side=tk.LEFT, padx=(0, 20))
        self.txt_nomepai.bind("<KeyRelease>", lambda e: self._forcar_maiusculo(self.txt_nomepai))

        ttk.Label(row0, text="Nome da Mãe:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_nomemae = ttk.Entry(row0, width=42)
        self.txt_nomemae.pack(side=tk.LEFT)
        self.txt_nomemae.bind("<KeyRelease>", lambda e: self._forcar_maiusculo(self.txt_nomemae))

        row1 = ttk.Frame(f)
        row1.pack(fill=tk.X, pady=6)

        ttk.Label(row1, text="Reside com:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_residecom = ttk.Entry(row1, width=35)
        self.txt_residecom.pack(side=tk.LEFT, padx=(0, 20))
        self.txt_residecom.bind("<KeyRelease>", lambda e: self._forcar_maiusculo(self.txt_residecom))

        # Radio button para Possui Filhos (Sim ou Não)
        grp_filhos = ttk.LabelFrame(row1, text=" Possui Filhos? ", padding=4)
        grp_filhos.pack(side=tk.LEFT, padx=(0, 20))
        self.var_filhos = tk.StringVar(value="Não")
        self.rdg_filhos_nao = ttk.Radiobutton(grp_filhos, text="Não", value="Não", variable=self.var_filhos)
        self.rdg_filhos_nao.pack(side=tk.LEFT, padx=4)
        self.rdg_filhos_sim = ttk.Radiobutton(grp_filhos, text="Sim", value="Sim", variable=self.var_filhos)
        self.rdg_filhos_sim.pack(side=tk.LEFT, padx=4)
        self.cbo_filhos = VarAdapter(self.var_filhos)

        vcmd_num = (self.register(lambda p: p == "" or p.isdigit()), "%P")
        ttk.Label(row1, text="Quantos filhos:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_quantosfilhos = ttk.Entry(row1, width=8, validate="key", validatecommand=vcmd_num)
        self.txt_quantosfilhos.pack(side=tk.LEFT)

    def _build_tab_pessoal(self):
        """Método de compatibilidade retroativa."""
        pass

    def _build_subtab_financeiro(self):
        f = self.subtab_financeiro

        # Linha 0: Tipo de Cobrança, Carnê e Lembrete
        row0 = ttk.Frame(f)
        row0.pack(fill=tk.X, pady=3)

        ttk.Label(row0, text="Tipo Cobrança (Cód):").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_tipocobcod = ttk.Entry(row0, width=8)
        self.txt_tipocobcod.pack(side=tk.LEFT, padx=(0, 2))
        self.btn_busca_tipocob = ttk.Button(row0, text="🔍", width=3, command=self._abrir_consulta_tipocob)
        self.btn_busca_tipocob.pack(side=tk.LEFT, padx=(0, 6))
        ToolTip(self.btn_busca_tipocob, "Pesquisar Tipo de Cobrança")
        self.txt_tipocobcod.bind("<FocusOut>", self._validar_codigo_tipocob)
        self.txt_tipocobcod.bind("<Return>", self._validar_codigo_tipocob)

        ttk.Label(row0, text="Descrição:").pack(side=tk.LEFT, padx=(0, 4))
        self.lbl_tipocobnome = LookupLabel(row0, text="", font=("Segoe UI", 9, "bold"), foreground="#1E3A8A")
        self.lbl_tipocobnome.pack(side=tk.LEFT, padx=(0, 16))
        self.txt_tipocobnome = self.lbl_tipocobnome

        ttk.Label(row0, text="Gerar Carnê:").pack(side=tk.LEFT, padx=(0, 4))
        self.cbo_geracarne = ttk.Combobox(row0, values=["Não", "Sim"], width=6, state="readonly")
        self.cbo_geracarne.set("Não")
        self.cbo_geracarne.pack(side=tk.LEFT, padx=(0, 16))

        ttk.Label(row0, text="Recebe Lembrete?:").pack(side=tk.LEFT, padx=(0, 4))
        self.cbo_recebelembrete = ttk.Combobox(row0, values=["Não", "Sim"], width=6, state="readonly")
        self.cbo_recebelembrete.set("Não")
        self.cbo_recebelembrete.pack(side=tk.LEFT)

        # Linha 1: Banco, Agência e Conta Corrente
        row1 = ttk.Frame(f)
        row1.pack(fill=tk.X, pady=3)

        ttk.Label(row1, text="Banco (Cód):").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_bconum = ttk.Entry(row1, width=8)
        self.txt_bconum.pack(side=tk.LEFT, padx=(0, 2))
        self.btn_busca_bco = ttk.Button(row1, text="🔍", width=3, command=self._abrir_consulta_banco)
        self.btn_busca_bco.pack(side=tk.LEFT, padx=(0, 6))
        ToolTip(self.btn_busca_bco, "Pesquisar Banco")

        self.lbl_bconome = LookupLabel(row1, text="", font=("Segoe UI", 9, "bold"), foreground="#1E3A8A")
        self.lbl_bconome.pack(side=tk.LEFT, padx=(0, 16))
        self.txt_bconome = self.lbl_bconome

        ttk.Label(row1, text="Agência:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_agnum = ttk.Entry(row1, width=8)
        self.txt_agnum.pack(side=tk.LEFT, padx=(0, 2))
        self.btn_busca_ag = ttk.Button(row1, text="🔍", width=3, command=self._abrir_consulta_agencia)
        self.btn_busca_ag.pack(side=tk.LEFT, padx=(0, 6))
        ToolTip(self.btn_busca_ag, "Pesquisar Agência")

        self.lbl_agnome = LookupLabel(row1, text="", font=("Segoe UI", 9, "bold"), foreground="#1E3A8A")
        self.lbl_agnome.pack(side=tk.LEFT, padx=(0, 16))
        self.txt_agnome = self.lbl_agnome

        ttk.Label(row1, text="Conta Corrente:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_cc = ttk.Entry(row1, width=16)
        self.txt_cc.pack(side=tk.LEFT)

        # Linha 2: Dia Débito, Valor Contribuição (com botões 🇧🇷 e 🇺🇸) e Diocese
        row2 = ttk.Frame(f)
        row2.pack(fill=tk.X, pady=3)

        ttk.Label(row2, text="Dia Deb. Automático:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_diadebito = ttk.Entry(row2, width=8)
        self.txt_diadebito.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row2, text="Valor Contribuição:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_valorcontrib = ttk.Entry(row2, width=12)
        self.txt_valorcontrib.pack(side=tk.LEFT, padx=(0, 2))
        self.txt_valorcontrib.bind("<FocusOut>", lambda e: self._formatar_valor_real())

        self.btn_moeda_br = ttk.Button(row2, text="🇧🇷 R$", width=6, command=self._formatar_valor_real)
        self.btn_moeda_br.pack(side=tk.LEFT, padx=(0, 2))
        ToolTip(self.btn_moeda_br, "Formatar como Moeda Brasileira (R$)")

        self.btn_moeda_us = ttk.Button(row2, text="🇺🇸 US$", width=7, command=self._formatar_valor_dolar)
        self.btn_moeda_us.pack(side=tk.LEFT, padx=(0, 14))
        ToolTip(self.btn_moeda_us, "Formatar como Moeda Norte-Americana (US$)")

        ttk.Label(row2, text="Diocese (ID):").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_dioceseid = ttk.Entry(row2, width=8)
        self.txt_dioceseid.pack(side=tk.LEFT, padx=(0, 2))
        self.txt_dioceseid.bind("<FocusOut>", self._on_diocese_focusout)
        self.btn_busca_diocese = ttk.Button(row2, text="🔍", width=3, command=self._abrir_consulta_diocese)
        self.btn_busca_diocese.pack(side=tk.LEFT, padx=(0, 6))
        ToolTip(self.btn_busca_diocese, "Pesquisar Diocese")

        self.lbl_diocesenome = LookupLabel(row2, text="", font=("Segoe UI", 9, "bold"), foreground="#1E3A8A")
        self.lbl_diocesenome.pack(side=tk.LEFT)
        self.txt_diocesenome = self.lbl_diocesenome

        # Grid inferior: últimas 36 doações da respectiva entidade na base Alvo
        frame_doacoes = ttk.LabelFrame(f, text=" Histórico das Últimas 36 Doações / Títulos na Base Alvo ", padding=6)
        frame_doacoes.pack(fill=tk.BOTH, expand=True, padx=2, pady=(8, 2))

        cols_doa = ("datapag", "datavenc", "valor", "especie", "documento", "tipocob", "status")
        self.tree_doacoes = ttk.Treeview(frame_doacoes, columns=cols_doa, show="headings", height=6)
        self.tree_doacoes.heading("datapag", text="Data Pagto")
        self.tree_doacoes.heading("datavenc", text="Data Venc.")
        self.tree_doacoes.heading("valor", text="Valor R$")
        self.tree_doacoes.heading("especie", text="Espécie")
        self.tree_doacoes.heading("documento", text="Nº Documento")
        self.tree_doacoes.heading("tipocob", text="Tipo Cobr.")
        self.tree_doacoes.heading("status", text="Status")

        self.tree_doacoes.column("datapag", width=100, anchor="center")
        self.tree_doacoes.column("datavenc", width=100, anchor="center")
        self.tree_doacoes.column("valor", width=90, anchor="e")
        self.tree_doacoes.column("especie", width=80, anchor="center")
        self.tree_doacoes.column("documento", width=110, anchor="w")
        self.tree_doacoes.column("tipocob", width=90, anchor="w")
        self.tree_doacoes.column("status", width=90, anchor="center")

        sc_doa_y = ttk.Scrollbar(frame_doacoes, orient=tk.VERTICAL, command=self.tree_doacoes.yview)
        self.tree_doacoes.configure(yscrollcommand=sc_doa_y.set)
        self.tree_doacoes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc_doa_y.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_tab_financeiro(self):
        """Método de compatibilidade retroativa."""
        pass

    def _build_subtab_infocompl(self):
        f = self.subtab_infocompl

        # Linha 0: Atividade Econômica e Origem da Entidade
        row0 = ttk.Frame(f)
        row0.pack(fill=tk.X, pady=4)

        ttk.Label(row0, text="Ativ. Econômica:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_ativecon_cod = ttk.Entry(row0, width=8)
        self.txt_ativecon_cod.pack(side=tk.LEFT, padx=(0, 2))
        self.txt_ativecon_cod.bind("<FocusOut>", self._on_ativecon_focusout)
        self.txt_ativecon_cod.bind("<Return>", self._on_ativecon_focusout)
        self.btn_busca_ativecon = ttk.Button(row0, text="🔍", width=3, command=self._abrir_consulta_ativecon)
        self.btn_busca_ativecon.pack(side=tk.LEFT, padx=(0, 6))
        ToolTip(self.btn_busca_ativecon, "Pesquisar Atividade Econômica")

        self.lbl_ativecon_nome = LookupLabel(row0, text="", font=("Segoe UI", 9, "bold"), foreground="#1E3A8A")
        self.lbl_ativecon_nome.pack(side=tk.LEFT, padx=(0, 16))
        self.txt_ativecon = self.txt_ativecon_cod
        self.txt_ativecon_nome = self.lbl_ativecon_nome

        ttk.Label(row0, text="Origem da Entidade:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_origem_cod = ttk.Entry(row0, width=8)
        self.txt_origem_cod.pack(side=tk.LEFT, padx=(0, 2))
        self.txt_origem_cod.bind("<FocusOut>", self._on_origem_focusout)
        self.txt_origem_cod.bind("<Return>", self._on_origem_focusout)
        self.btn_busca_origem = ttk.Button(row0, text="🔍", width=3, command=self._abrir_consulta_origem)
        self.btn_busca_origem.pack(side=tk.LEFT, padx=(0, 6))
        ToolTip(self.btn_busca_origem, "Pesquisar Origem")

        self.lbl_origem_nome = LookupLabel(row0, text="", font=("Segoe UI", 9, "bold"), foreground="#1E3A8A")
        self.lbl_origem_nome.pack(side=tk.LEFT)
        self.txt_origem = self.txt_origem_cod
        self.txt_origem_nome = self.lbl_origem_nome

        # Linha 1: Região e Conceito da Entidade
        row1 = ttk.Frame(f)
        row1.pack(fill=tk.X, pady=4)

        ttk.Label(row1, text="Região:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_regiao_cod = ttk.Entry(row1, width=8)
        self.txt_regiao_cod.pack(side=tk.LEFT, padx=(0, 2))
        self.txt_regiao_cod.bind("<FocusOut>", self._on_regiao_focusout)
        self.txt_regiao_cod.bind("<Return>", self._on_regiao_focusout)
        self.btn_busca_regiao = ttk.Button(row1, text="🔍", width=3, command=self._abrir_consulta_regiao)
        self.btn_busca_regiao.pack(side=tk.LEFT, padx=(0, 6))
        ToolTip(self.btn_busca_regiao, "Pesquisar Região")

        self.lbl_regiao_nome = LookupLabel(row1, text="", font=("Segoe UI", 9, "bold"), foreground="#1E3A8A")
        self.lbl_regiao_nome.pack(side=tk.LEFT, padx=(0, 16))
        self.txt_regiao = self.txt_regiao_cod
        self.txt_regiao_nome = self.lbl_regiao_nome

        ttk.Label(row1, text="Conceito da Entidade:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_conceito = ttk.Entry(row1, width=32)
        self.txt_conceito.pack(side=tk.LEFT)
        self.txt_conceito_cod = self.txt_conceito
        self.txt_conceito_nome = self.txt_conceito

        # Linha 2: Groupboxes para Endereço de Cobrança e Entrega o mesmo
        row2 = ttk.Frame(f)
        row2.pack(fill=tk.X, pady=10)

        grp_cob = ttk.LabelFrame(row2, text=" Endereço de cobrança o mesmo? ", padding=8)
        grp_cob.pack(side=tk.LEFT, padx=(0, 20))
        self.var_end_cob_mesmo = tk.StringVar(value="Sim")
        ttk.Radiobutton(grp_cob, text="Sim", value="Sim", variable=self.var_end_cob_mesmo, command=self._toggle_subtab_endcobranca).pack(side=tk.LEFT, padx=6)
        ttk.Radiobutton(grp_cob, text="Não", value="Não", variable=self.var_end_cob_mesmo, command=self._toggle_subtab_endcobranca).pack(side=tk.LEFT, padx=6)

        grp_ent = ttk.LabelFrame(row2, text=" Endereço de entrega o mesmo? ", padding=8)
        grp_ent.pack(side=tk.LEFT)
        self.var_end_ent_mesmo = tk.StringVar(value="Sim")
        ttk.Radiobutton(grp_ent, text="Sim", value="Sim", variable=self.var_end_ent_mesmo, command=self._toggle_subtab_endentrega).pack(side=tk.LEFT, padx=6)
        ttk.Radiobutton(grp_ent, text="Não", value="Não", variable=self.var_end_ent_mesmo, command=self._toggle_subtab_endentrega).pack(side=tk.LEFT, padx=6)

    def _build_subtab_endcobranca(self):
        f = self.subtab_endcobranca

        row0 = ttk.Frame(f)
        row0.pack(fill=tk.X, pady=4)

        ttk.Label(row0, text="CEP:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_cob_cep = ttk.Entry(row0, width=12)
        self.txt_cob_cep.pack(side=tk.LEFT, padx=(0, 14))
        self.txt_cob_cep.bind("<Return>", self._consultar_viacep_cobranca)
        self.txt_cob_cep.bind("<FocusOut>", self._consultar_viacep_cobranca)

        ttk.Label(row0, text="Tipo:").pack(side=tk.LEFT, padx=(0, 4))
        self.cbo_cob_tipolograd = ttk.Combobox(row0, width=8)
        self.cbo_cob_tipolograd.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row0, text="Endereço / Logradouro:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_cob_ender = ttk.Entry(row0, width=38)
        self.txt_cob_ender.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row0, text="Número:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_cob_enderno = ttk.Entry(row0, width=8)
        self.txt_cob_enderno.pack(side=tk.LEFT)

        row1 = ttk.Frame(f)
        row1.pack(fill=tk.X, pady=4)

        ttk.Label(row1, text="Complemento:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_cob_endercomp = ttk.Entry(row1, width=24)
        self.txt_cob_endercomp.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row1, text="Bairro:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_cob_bair = ttk.Entry(row1, width=28)
        self.txt_cob_bair.pack(side=tk.LEFT)

        row2 = ttk.Frame(f)
        row2.pack(fill=tk.X, pady=4)

        ttk.Label(row2, text="Cód. Cidade:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_cob_cidcod = ttk.Entry(row2, width=8)
        self.txt_cob_cidcod.pack(side=tk.LEFT, padx=(0, 2))
        self.btn_busca_cob_cid = ttk.Button(row2, text="🔍", width=3, command=self._abrir_consulta_cidade_cob)
        self.btn_busca_cob_cid.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(row2, text="Cidade:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_cob_cidade = ttk.Entry(row2, width=30)
        self.txt_cob_cidade.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row2, text="UF:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_cob_uf = ttk.Entry(row2, width=5)
        self.txt_cob_uf.pack(side=tk.LEFT)

    def _build_subtab_endentrega(self):
        f = self.subtab_endentrega

        row0 = ttk.Frame(f)
        row0.pack(fill=tk.X, pady=4)

        ttk.Label(row0, text="CEP:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_ent_cep = ttk.Entry(row0, width=12)
        self.txt_ent_cep.pack(side=tk.LEFT, padx=(0, 14))
        self.txt_ent_cep.bind("<Return>", self._consultar_viacep_entrega)
        self.txt_ent_cep.bind("<FocusOut>", self._consultar_viacep_entrega)

        ttk.Label(row0, text="Tipo:").pack(side=tk.LEFT, padx=(0, 4))
        self.cbo_ent_tipolograd = ttk.Combobox(row0, width=8)
        self.cbo_ent_tipolograd.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row0, text="Endereço / Logradouro:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_ent_ender = ttk.Entry(row0, width=38)
        self.txt_ent_ender.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row0, text="Número:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_ent_enderno = ttk.Entry(row0, width=8)
        self.txt_ent_enderno.pack(side=tk.LEFT)

        row1 = ttk.Frame(f)
        row1.pack(fill=tk.X, pady=4)

        ttk.Label(row1, text="Complemento:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_ent_endercomp = ttk.Entry(row1, width=24)
        self.txt_ent_endercomp.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row1, text="Bairro:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_ent_bair = ttk.Entry(row1, width=28)
        self.txt_ent_bair.pack(side=tk.LEFT)

        row2 = ttk.Frame(f)
        row2.pack(fill=tk.X, pady=4)

        ttk.Label(row2, text="Cód. Cidade:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_ent_cidcod = ttk.Entry(row2, width=8)
        self.txt_ent_cidcod.pack(side=tk.LEFT, padx=(0, 2))
        self.btn_busca_ent_cid = ttk.Button(row2, text="🔍", width=3, command=self._abrir_consulta_cidade_ent)
        self.btn_busca_ent_cid.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(row2, text="Cidade:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_ent_cidade = ttk.Entry(row2, width=30)
        self.txt_ent_cidade.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(row2, text="UF:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_ent_uf = ttk.Entry(row2, width=5)
        self.txt_ent_uf.pack(side=tk.LEFT)

    def _build_tab_contatos(self):
        f = self.tab_contatos

        # Banner de alerta para menor de 18 anos
        self.frame_alerta_menor = tk.Frame(f, bg="#FEF3C7", bd=1, relief=tk.SOLID)
        self.lbl_alerta_menor = tk.Label(
            self.frame_alerta_menor,
            text="",
            font=("Segoe UI", 9, "bold"),
            bg="#FEF3C7",
            fg="#B45309",
            padx=8,
            pady=4,
        )
        self.lbl_alerta_menor.pack(fill=tk.X, pady=(0, 4))

        # Sub-notebook com duas sub-abas: "Contatos" e "Comunicação"
        self.sub_notebook_contatos = ttk.Notebook(f)
        self.sub_notebook_contatos.pack(fill=tk.BOTH, expand=True)

        self.subtab_contatos = ttk.Frame(self.sub_notebook_contatos, padding=10)
        self.subtab_comunicacao = ttk.Frame(self.sub_notebook_contatos, padding=8)

        self.sub_notebook_contatos.add(self.subtab_contatos, text="  Contatos  ")
        self.sub_notebook_contatos.add(self.subtab_comunicacao, text="  Comunicação  ")

        # -----------------------------------------------------------------
        # SUB-ABA 1: DADOS DOS CONTATOS
        # -----------------------------------------------------------------
        frame_resp = ttk.LabelFrame(
            self.subtab_contatos,
            text=" Dados do Contato / Responsável Legal / Grupo de Oração ",
            padding=12
        )
        frame_resp.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Linha 1: Tipo / Grupo de Oração
        row_go = ttk.Frame(frame_resp)
        row_go.pack(fill=tk.X, pady=(0, 8))

        self.var_grupooracao = tk.BooleanVar(value=False)
        self.chk_grupooracao = ttk.Checkbutton(
            row_go,
            text="O Contato é um Grupo de Oração ?",
            variable=self.var_grupooracao,
            command=self._on_grupooracao_toggle
        )
        self.chk_grupooracao.pack(side=tk.LEFT, padx=(0, 16))

        # Linha 2: Datas de Vigência (destacadas e sempre editáveis)
        row_vigencia = ttk.Frame(frame_resp)
        row_vigencia.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(row_vigencia, text="Data Início da Vigência:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self.txt_dtiniciovigencia = ttk.Entry(row_vigencia, width=14, font=("Segoe UI", 9))
        self.txt_dtiniciovigencia.pack(side=tk.LEFT, padx=(0, 24))
        self.txt_dtiniciovigencia.bind("<KeyRelease>", lambda e: _aplicar_mascara_data(e, self.txt_dtiniciovigencia))

        ttk.Label(row_vigencia, text="Data Término da Vigência:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self.txt_dtfinalvigencia = ttk.Entry(row_vigencia, width=14, font=("Segoe UI", 9))
        self.txt_dtfinalvigencia.pack(side=tk.LEFT, padx=(0, 10))
        self.txt_dtfinalvigencia.bind("<KeyRelease>", lambda e: _aplicar_mascara_data(e, self.txt_dtfinalvigencia))

        # Linha 3: Identificação do Contato (Código, Lupa de Entidades, Nome)
        row_resp_campos = ttk.Frame(frame_resp)
        row_resp_campos.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(row_resp_campos, text="Cód. Contato:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.txt_contato_cod = ttk.Entry(row_resp_campos, width=10, font=("Segoe UI", 9))
        self.txt_contato_cod.pack(side=tk.LEFT, padx=(0, 4))
        self.btn_busca_contato = ttk.Button(row_resp_campos, text="🔍", width=3, command=self._abrir_consulta_contato)
        self.btn_busca_contato.pack(side=tk.LEFT, padx=(0, 8))
        ToolTip(self.btn_busca_contato, "Pesquisar Entidades para Contato")

        self.lbl_contato_nome = LookupLabel(row_resp_campos, text="", font=("Segoe UI", 10, "bold"), foreground="#1E3A8A")
        self.lbl_contato_nome.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Linha 4: Cargo / Ocupação
        row_cargo = ttk.Frame(frame_resp)
        row_cargo.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(row_cargo, text="Cargo / Ocupação:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.txt_contato_cargo_cod = ttk.Entry(row_cargo, width=8, font=("Segoe UI", 9))
        self.txt_contato_cargo_cod.pack(side=tk.LEFT, padx=(0, 4))
        self.btn_busca_contato_cargo = ttk.Button(row_cargo, text="🔍", width=3, command=self._abrir_consulta_contato_cargo)
        self.btn_busca_contato_cargo.pack(side=tk.LEFT, padx=(0, 8))
        ToolTip(self.btn_busca_contato_cargo, "Pesquisar Cargos / Funções")

        self.lbl_contato_cargo_nome = LookupLabel(row_cargo, text="", font=("Segoe UI", 9), foreground="#475569")
        self.lbl_contato_cargo_nome.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Linha 5: Atributos adicionais
        row_attr = ttk.Frame(frame_resp)
        row_attr.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(row_attr, text="Contato Principal:").pack(side=tk.LEFT, padx=(0, 4))
        self.cbo_contato_princ = ttk.Combobox(row_attr, values=["Sim", "Não"], width=6, state="readonly")
        self.cbo_contato_princ.set("Sim")
        self.cbo_contato_princ.pack(side=tk.LEFT, padx=(0, 18))

        ttk.Label(row_attr, text="Status do Contato:").pack(side=tk.LEFT, padx=(0, 4))
        self.cbo_contato_status = ttk.Combobox(row_attr, values=["Ativo", "Inativo"], width=8, state="readonly")
        self.cbo_contato_status.set("Ativo")
        self.cbo_contato_status.pack(side=tk.LEFT, padx=(0, 18))

        ttk.Label(row_attr, text="Grau de Decisão:").pack(side=tk.LEFT, padx=(0, 4))
        self.cbo_contato_graudecisao = ttk.Combobox(row_attr, values=["Alto", "Médio", "Baixo"], width=8, state="readonly")
        self.cbo_contato_graudecisao.set("Médio")
        self.cbo_contato_graudecisao.pack(side=tk.LEFT)

        # -----------------------------------------------------------------
        # SUB-ABA 2: COMUNICAÇÃO (Telefones e E-mails/Web)
        # -----------------------------------------------------------------
        # 1. Seção Telefones
        frame_tel = ttk.LabelFrame(self.subtab_comunicacao, text=" Telefones & Contatos Telefônicos ", padding=8)
        frame_tel.pack(fill=tk.BOTH, expand=True, padx=2, pady=4)

        row_tel_top = ttk.Frame(frame_tel)
        row_tel_top.pack(fill=tk.X, pady=(0, 6))

        vcmd_tel = (self.register(lambda s: all(c in "0123456789+-() *#" for c in s)), "%S")
        vcmd_dig = (self.register(lambda s: s.isdigit()), "%S")

        ttk.Label(row_tel_top, text="DDI:").pack(side=tk.LEFT, padx=(0, 2))
        self.txt_ddi = ttk.Entry(row_tel_top, width=4, validate="key", validatecommand=vcmd_dig)
        self.txt_ddi.insert(0, "55")
        self.txt_ddi.pack(side=tk.LEFT, padx=(0, 6))
        self.txt_ddi.bind("<Return>", lambda e: self.txt_ddd.focus_set())

        ttk.Label(row_tel_top, text="DDD:").pack(side=tk.LEFT, padx=(0, 2))
        self.txt_ddd = ttk.Entry(row_tel_top, width=4, validate="key", validatecommand=vcmd_dig)
        self.txt_ddd.pack(side=tk.LEFT, padx=(0, 6))
        self.txt_ddd.bind("<Return>", lambda e: self.txt_tel_num.focus_set())

        ttk.Label(row_tel_top, text="Número:*").pack(side=tk.LEFT, padx=(0, 2))
        self.txt_tel_num = ttk.Entry(row_tel_top, width=14, validate="key", validatecommand=vcmd_tel)
        self.txt_tel_num.pack(side=tk.LEFT, padx=(0, 6))
        self.txt_tel_num.bind("<Return>", lambda e: self.txt_tel_ramal.focus_set())

        ttk.Label(row_tel_top, text="Ramal:").pack(side=tk.LEFT, padx=(0, 2))
        self.txt_tel_ramal = ttk.Entry(row_tel_top, width=6, validate="key", validatecommand=vcmd_dig)
        self.txt_tel_ramal.pack(side=tk.LEFT, padx=(0, 6))
        self.txt_tel_ramal.bind("<Return>", lambda e: self.cbo_tel_tipo.focus_set())

        ttk.Label(row_tel_top, text="Tipo:").pack(side=tk.LEFT, padx=(0, 2))
        self.cbo_tel_tipo = ttk.Combobox(
            row_tel_top,
            values=["Pessoal", "Celular", "Comercial", "Residencial", "WhatsApp", "Recado", "Fax", "Gratuito"],
            width=10,
            state="readonly"
        )
        self.cbo_tel_tipo.set("Celular")
        self.cbo_tel_tipo.pack(side=tk.LEFT, padx=(0, 6))
        self.cbo_tel_tipo.bind("<Return>", lambda e: self._adicionar_telefone())

        self.var_tel_princ = tk.BooleanVar(value=True)
        self.chk_tel_princ = ttk.Checkbutton(row_tel_top, text="Princ.", variable=self.var_tel_princ)
        self.chk_tel_princ.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_add_tel = ttk.Button(row_tel_top, text="➕", width=3, command=self._adicionar_telefone)
        self.btn_add_tel.pack(side=tk.LEFT, padx=(0, 4))
        ToolTip(self.btn_add_tel, "Inserir Telefone")

        self.btn_del_tel = ttk.Button(row_tel_top, text="❌", width=3, command=self._remover_telefone)
        self.btn_del_tel.pack(side=tk.LEFT)
        ToolTip(self.btn_del_tel, "Excluir Telefone")

        cols_tel = ("tipo", "ddi", "ddd", "numero", "ramal", "principal")
        self.tree_telefones = ttk.Treeview(frame_tel, columns=cols_tel, show="headings", height=5)
        self.tree_telefones.heading("tipo", text="Tipo")
        self.tree_telefones.heading("ddi", text="DDI")
        self.tree_telefones.heading("ddd", text="DDD")
        self.tree_telefones.heading("numero", text="Número")
        self.tree_telefones.heading("ramal", text="Ramal")
        self.tree_telefones.heading("principal", text="Principal")

        self.tree_telefones.column("tipo", width=100, anchor="w")
        self.tree_telefones.column("ddi", width=45, anchor="center")
        self.tree_telefones.column("ddd", width=45, anchor="center")
        self.tree_telefones.column("numero", width=130, anchor="w")
        self.tree_telefones.column("ramal", width=60, anchor="center")
        self.tree_telefones.column("principal", width=70, anchor="center")

        sc_tel = ttk.Scrollbar(frame_tel, orient=tk.VERTICAL, command=self.tree_telefones.yview)
        self.tree_telefones.configure(yscrollcommand=sc_tel.set)
        self.tree_telefones.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc_tel.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_telefones.bind("<Delete>", self._remover_telefone)
        self.tree_telefones.bind("<Double-1>", self._on_tel_double_click)

        # 2. Seção Comunicação WEB / E-mails
        frame_web = ttk.LabelFrame(self.subtab_comunicacao, text=" Comunicação WEB & E-mails ", padding=8)
        frame_web.pack(fill=tk.BOTH, expand=True, padx=2, pady=4)

        row_web_top = ttk.Frame(frame_web)
        row_web_top.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(row_web_top, text="Tipo:").pack(side=tk.LEFT, padx=(0, 2))
        self.cbo_web_tipo = ttk.Combobox(
            row_web_top,
            values=["Pessoal", "Comercial", "Profissional", "Recado"],
            width=10,
            state="readonly"
        )
        self.cbo_web_tipo.set("Pessoal")
        self.cbo_web_tipo.pack(side=tk.LEFT, padx=(0, 6))

        ttk.Label(row_web_top, text="E-mail:*").pack(side=tk.LEFT, padx=(0, 2))
        self.txt_web_email = ttk.Entry(row_web_top, width=22)
        self.txt_web_email.pack(side=tk.LEFT, padx=(0, 6))
        self.txt_web_email.bind("<KeyRelease>", self._forcar_email_minusculo)

        ttk.Label(row_web_top, text="Website:").pack(side=tk.LEFT, padx=(0, 2))
        self.txt_web_site = ttk.Entry(row_web_top, width=18)
        self.txt_web_site.pack(side=tk.LEFT, padx=(0, 6))

        ttk.Label(row_web_top, text="Comunicador:").pack(side=tk.LEFT, padx=(0, 2))
        self.txt_web_comunicador = ttk.Entry(row_web_top, width=12)
        self.txt_web_comunicador.pack(side=tk.LEFT, padx=(0, 6))

        self.var_web_princ = tk.BooleanVar(value=True)
        self.chk_web_princ = ttk.Checkbutton(row_web_top, text="Princ.", variable=self.var_web_princ)
        self.chk_web_princ.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_add_web = ttk.Button(row_web_top, text="➕", width=3, command=self._adicionar_webcontato)
        self.btn_add_web.pack(side=tk.LEFT, padx=(0, 4))
        ToolTip(self.btn_add_web, "Inserir E-mail/Web")

        self.btn_del_web = ttk.Button(row_web_top, text="❌", width=3, command=self._remover_webcontato)
        self.btn_del_web.pack(side=tk.LEFT)
        ToolTip(self.btn_del_web, "Excluir Web")

        cols_web = ("tipo", "email", "website", "comunicador", "principal")
        self.tree_webcontatos = ttk.Treeview(frame_web, columns=cols_web, show="headings", height=5)
        self.tree_webcontatos.heading("tipo", text="Tipo")
        self.tree_webcontatos.heading("email", text="E-Mail")
        self.tree_webcontatos.heading("website", text="Website")
        self.tree_webcontatos.heading("comunicador", text="Comunicador Instantâneo")
        self.tree_webcontatos.heading("principal", text="Principal")

        self.tree_webcontatos.column("tipo", width=90, anchor="w")
        self.tree_webcontatos.column("email", width=200, anchor="w")
        self.tree_webcontatos.column("website", width=160, anchor="w")
        self.tree_webcontatos.column("comunicador", width=120, anchor="w")
        self.tree_webcontatos.column("principal", width=65, anchor="center")

        sc_web = ttk.Scrollbar(frame_web, orient=tk.VERTICAL, command=self.tree_webcontatos.yview)
        self.tree_webcontatos.configure(yscrollcommand=sc_web.set)
        self.tree_webcontatos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc_web.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_webcontatos.bind("<Delete>", self._remover_webcontato)
        self.tree_webcontatos.bind("<Double-1>", self._on_web_double_click)

    def _build_tab_historico(self):
        f = self.tab_historico

        ttk.Label(f, text="HISTÓRICO:", font=("Segoe UI", 10, "bold"), foreground="#475569").pack(anchor="w", pady=(0, 3))
        self.txt_historico = ScrolledText(
            f,
            height=10,
            bg="#E2E8F0",
            fg="#1E293B",
            font=("Consolas", 9),
            state="disabled",
            wrap=tk.WORD,
            relief=tk.SOLID,
            borderwidth=1,
        )
        self.txt_historico.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        ttk.Label(f, text="NOVO REGISTRO DE HISTÓRICO:", font=("Segoe UI", 10, "bold"), foreground="#1E3A8A").pack(anchor="w", pady=(0, 3))
        self.txt_novohistorico = ScrolledText(
            f,
            height=5,
            bg="#FFFFFF",
            fg="#0F172A",
            font=("Segoe UI", 10),
            wrap=tk.WORD,
            relief=tk.SOLID,
            borderwidth=1,
        )
        self.txt_novohistorico.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        row_botoes = ttk.Frame(f)
        row_botoes.pack(fill=tk.X)

        self.btn_gravar_historico = ttk.Button(row_botoes, text="💾 Gravar Registro no Histórico", command=self._gravar_novo_historico)
        self.btn_gravar_historico.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_limpar_novohistorico = ttk.Button(row_botoes, text="🧹 Limpar", command=lambda: self.txt_novohistorico.delete("1.0", tk.END))
        self.btn_limpar_novohistorico.pack(side=tk.LEFT)

    def _build_tab_documentos(self):
        f = self.tab_documentos

        top_frame = ttk.LabelFrame(f, text=" Manutenção de Documentos Adicionais da Entidade ", padding=8)
        top_frame.pack(fill=tk.X, padx=4, pady=4)

        row0 = ttk.Frame(top_frame)
        row0.pack(fill=tk.X, pady=2)

        ttk.Label(row0, text="Tipo de Documento:*").pack(side=tk.LEFT, padx=(0, 4))
        self.cbo_doc_tipo = ttk.Combobox(
            row0,
            values=["C.N.H.", "IM", "PASSAPORTE", "CERTIDAO", "TITULO DE ELEITOR", "OUTROS"],
            width=16,
            state="readonly"
        )
        self.cbo_doc_tipo.set("C.N.H.")
        self.cbo_doc_tipo.pack(side=tk.LEFT, padx=(0, 16))

        ttk.Label(row0, text="Número do Documento:*").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_doc_num = ttk.Entry(row0, width=22)
        self.txt_doc_num.pack(side=tk.LEFT, padx=(0, 16))

        ttk.Label(row0, text="Observações / Órgão:").pack(side=tk.LEFT, padx=(0, 4))
        self.txt_doc_obs = ttk.Entry(row0, width=32)
        self.txt_doc_obs.pack(side=tk.LEFT, padx=(0, 16))

        self.btn_add_doc = ttk.Button(row0, text="➕", width=4, command=self._adicionar_documento)
        self.btn_add_doc.pack(side=tk.LEFT, padx=(0, 6))
        ToolTip(self.btn_add_doc, "Inserir Documento")

        self.btn_del_doc = ttk.Button(row0, text="❌", width=4, command=self._remover_documento)
        self.btn_del_doc.pack(side=tk.LEFT)
        ToolTip(self.btn_del_doc, "Remover Documento")

        grid_frame = ttk.LabelFrame(f, text=" Documentos Registrados ", padding=8)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        cols = ("tipo", "documento", "observacoes")
        self.tree_documentos = ttk.Treeview(grid_frame, columns=cols, show="headings", height=12)
        self.tree_documentos.heading("tipo", text="Tipo de Documento")
        self.tree_documentos.heading("documento", text="Número / Identificação")
        self.tree_documentos.heading("observacoes", text="Observações / Detalhes")

        self.tree_documentos.column("tipo", width=180, anchor="w")
        self.tree_documentos.column("documento", width=250, anchor="w")
        self.tree_documentos.column("observacoes", width=380, anchor="w")

        sc_doc = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.tree_documentos.yview)
        self.tree_documentos.configure(yscrollcommand=sc_doc.set)
        self.tree_documentos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sc_doc.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_documentos.bind("<Delete>", lambda e: self._remover_documento())
        self.tree_documentos.bind("<Double-1>", self._on_doc_double_click)

    def _build_tab_observacoes(self):
        f = self.tab_observacoes

        lbl_obs = ttk.Label(
            f,
            text="Pendências / Observações Cadastrais (Impedimentos para envio ao Alvo):",
            font=("Segoe UI", 10, "bold"),
            foreground="#B91C1C",
        )
        lbl_obs.pack(anchor="w", pady=(8, 4))

        self.txt_observacoes = ScrolledText(f, height=14, font=("Segoe UI", 10), wrap=tk.WORD)
        self.txt_observacoes.pack(fill=tk.BOTH, expand=True)
        self.txt_observacoes.bind("<F3>", lambda e: (self.salvar(), "break")[1])

    # -------------------------------------------------------------
    # Handlers e Abertura de Consultas (Lookups)
    # -------------------------------------------------------------
    def _forcar_maiusculo(self, widget: ttk.Entry):
        try:
            pos = widget.index(tk.INSERT)
            texto = widget.get().upper()
            orig_state = str(widget.cget("state"))
            if orig_state == "readonly":
                widget.config(state="normal")
            widget.delete(0, tk.END)
            widget.insert(0, texto)
            if orig_state == "readonly":
                widget.config(state="readonly")
            widget.icursor(pos)
        except Exception:
            pass

    def _forcar_email_minusculo(self, event=None):
        try:
            pos = self.txt_web_email.index(tk.INSERT)
            val = self.txt_web_email.get().lower()
            self.txt_web_email.delete(0, tk.END)
            self.txt_web_email.insert(0, val)
            self.txt_web_email.icursor(pos)
        except Exception:
            pass

    def _abrir_consulta_cidade(self):
        dados = []
        if self._service:
            try:
                dados = self._service.listar_cidades(base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro na Consulta", f"Falha ao carregar cidades: {exc}", parent=self)
                return

        def _selecionou(item):
            self.txt_cidcod.delete(0, tk.END)
            self.txt_cidcod.insert(0, str(item.get("codigo", "")))
            self.txt_cidade.delete(0, tk.END)
            self.txt_cidade.insert(0, str(item.get("nome", "")))
            self.txt_uf.delete(0, tk.END)
            self.txt_uf.insert(0, str(item.get("uf", "")))
            self.statusbar.config(text=f"Cidade selecionada: {item.get('nome')} / {item.get('uf')}")

        cols = [("codigo", "Código", 100), ("nome", "Nome da Cidade", 380), ("uf", "UF", 70)]
        DlgConsultaGenerica(self, "Pesquisa de Cidades", cols, dados, _selecionou)

    def _abrir_consulta_categoria(self):
        dados = []
        if not self._service:
            self._inicializar_dependencias()
        if self._service:
            try:
                dados = self._service.listar_categorias_lookup(base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro na Consulta", f"Falha ao carregar categorias: {exc}", parent=self)
                return

        def _selecionou(item):
            self.txt_categ_cod.delete(0, tk.END)
            self.txt_categ_cod.insert(0, str(item.get("codigo", "")))
            self.txt_categ_nome.delete(0, tk.END)
            self.txt_categ_nome.insert(0, str(item.get("descricao", "")))
            self.statusbar.config(text=f"Categoria selecionada: [{item.get('codigo')}] {item.get('descricao')}")

        cols = [("codigo", "Código Categoria", 160), ("descricao", "Descrição da Categoria", 480)]
        DlgConsultaGenerica(self, "Pesquisa de Categorias", cols, dados, _selecionou)

    def _on_categ_focusout(self, event=None):
        cod = self.txt_categ_cod.get().strip()
        if not cod:
            self.txt_categ_nome.delete(0, tk.END)
            return
        if not self._service:
            self._inicializar_dependencias()
        if self._service:
            try:
                cat = self._service.obter_categoria_por_codigo(cod, base_dados=self.base_dados)
                if cat and cat.get("descricao"):
                    self.txt_categ_nome.delete(0, tk.END)
                    self.txt_categ_nome.insert(0, cat["descricao"])
            except Exception as exc:
                logger.warning("Falha ao resolver categoria no FocusOut: %s", exc)


    def _abrir_consulta_cargo(self):
        dados = []
        if self._service:
            try:
                dados = self._service.listar_cargos_lookup(base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro na Consulta", f"Falha ao carregar cargos: {exc}", parent=self)
                return

        def _selecionou(item):
            self.txt_cargo_cod.delete(0, tk.END)
            self.txt_cargo_cod.insert(0, str(item.get("codigo", "")))
            self.lbl_cargo_nome.set(str(item.get("descricao", "")))
            self.statusbar.config(text=f"Cargo selecionado: [{item.get('codigo')}] {item.get('descricao')}")

        cols = [("codigo", "Código Cargo", 140), ("descricao", "Nome / Descrição do Cargo", 480)]
        DlgConsultaGenerica(self, "Pesquisa de Cargos / Ocupações", cols, dados, _selecionou)

    def _abrir_consulta_tipocob(self):
        dados = []
        if self._service:
            try:
                dados = self._service.listar_tipos_cobranca(base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro na Consulta", f"Falha ao carregar tipos de cobrança: {exc}", parent=self)
                return

        def _selecionou(item):
            self.txt_tipocobcod.delete(0, tk.END)
            self.txt_tipocobcod.insert(0, str(item.get("codigo", "")))
            desc = str(item.get("descricao", ""))
            self.lbl_tipocobnome.set(desc)
            if "DEB" in desc.upper() or "DÉB" in desc.upper():
                if not self.txt_diadebito.get().strip():
                    self.txt_diadebito.delete(0, tk.END)
                    self.txt_diadebito.insert(0, "10")
            self.statusbar.config(text=f"Tipo de cobrança selecionado: [{item.get('codigo')}] {desc}")

        cols = [("codigo", "Código", 120), ("descricao", "Descrição Tipo Cobrança", 500)]
        DlgConsultaGenerica(self, "Pesquisa de Tipos de Cobrança", cols, dados, _selecionou)

    def _validar_codigo_tipocob(self, event=None):
        cod = self.txt_tipocobcod.get().strip()
        if not cod:
            return
        if self._service:
            try:
                tc = self._service.buscar_tipo_cobranca_por_codigo(cod, base_dados=self.base_dados)
                if tc:
                    desc = str(tc.get("descricao", ""))
                    self.lbl_tipocobnome.set(desc)
                    if "DEB" in desc.upper() or "DÉB" in desc.upper():
                        if not self.txt_diadebito.get().strip():
                            self.txt_diadebito.delete(0, tk.END)
                            self.txt_diadebito.insert(0, "10")
            except Exception:
                pass

    def _abrir_consulta_banco(self):
        dados = []
        if self._service:
            try:
                dados = self._service.listar_bancos(base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro na Consulta", f"Falha ao carregar bancos: {exc}", parent=self)
                return

        def _selecionou(item):
            self.txt_bconum.delete(0, tk.END)
            self.txt_bconum.insert(0, str(item.get("numero", "")))
            self.lbl_bconome.set(str(item.get("nome", "")))
            self.statusbar.config(text=f"Banco selecionado: [{item.get('numero')}] {item.get('nome')}")

        cols = [("numero", "Nº Banco", 90), ("nome", "Nome do Banco", 420), ("abreviatura", "Abrev.", 120)]
        DlgConsultaGenerica(self, "Pesquisa de Bancos", cols, dados, _selecionou)

    def _abrir_consulta_agencia(self):
        bconum = self.txt_bconum.get().strip()
        dados = []
        if self._service:
            try:
                dados = self._service.listar_agencias(bconum=bconum, base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro na Consulta", f"Falha ao carregar agências: {exc}", parent=self)
                return

        def _selecionou(item):
            self.txt_agnum.delete(0, tk.END)
            self.txt_agnum.insert(0, str(item.get("numero", "")))
            self.lbl_agnome.set(str(item.get("nome", "")))
            self.statusbar.config(text=f"Agência selecionada: [{item.get('numero')}] {item.get('nome')}")

        cols = [("numero", "Nº Agência", 100), ("nome", "Nome da Agência", 380), ("cidade", "Cidade", 140)]
        DlgConsultaGenerica(self, "Pesquisa de Agências", cols, dados, _selecionou)

    def _abrir_consulta_diocese(self):
        dados = []
        if not self._service:
            self._inicializar_dependencias()
        if self._service:
            try:
                cidade = self.txt_cidade.get().strip() if hasattr(self, "txt_cidade") else ""
                uf = self.txt_uf.get().strip() if hasattr(self, "txt_uf") else ""
                dados = self._service.listar_dioceses_por_cidade(cidade=cidade, uf=uf)
            except Exception as exc:
                messagebox.showerror("Erro na Consulta", f"Falha ao carregar dioceses: {exc}", parent=self)
                return

        def _selecionou(item):
            self.txt_dioceseid.delete(0, tk.END)
            self.txt_dioceseid.insert(0, str(item.get("codigo", "")))
            self.lbl_diocesenome.set(str(item.get("descricao", "")))
            self.statusbar.config(text=f"Diocese selecionada: [{item.get('codigo')}] {item.get('descricao')}")

        cols = [("codigo", "ID", 80), ("descricao", "Nome da Diocese", 420), ("observacoes", "Observações", 160)]
        DlgConsultaGenerica(self, "Pesquisa de Dioceses (CNBB)", cols, dados, _selecionou)

    def _on_diocese_focusout(self, event=None):
        cod = self.txt_dioceseid.get().strip()
        if not cod:
            self.lbl_diocesenome.set("")
            return
        if not self._service:
            self._inicializar_dependencias()
        if self._service:
            try:
                nome = self._service.obter_nome_diocese(cod)
                self.lbl_diocesenome.set(nome)
            except Exception as exc:
                logger.warning("Falha ao resolver diocese no FocusOut: %s", exc)

    def _abrir_consulta_ativecon(self):
        dados = []
        if not self._service:
            self._inicializar_dependencias()
        if self._service:
            try:
                dados = self._service.listar_atividades_economicas(base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro na Consulta", f"Falha ao carregar atividades econômicas: {exc}", parent=self)
                return

        def _selecionou(item):
            self.txt_ativecon_cod.delete(0, tk.END)
            self.txt_ativecon_cod.insert(0, str(item.get("codigo", "")))
            self.lbl_ativecon_nome.set(str(item.get("descricao", "")))
            self.statusbar.config(text=f"Atividade econômica selecionada: {item.get('descricao')}")

        cols = [("codigo", "Código", 140), ("descricao", "Nome da Atividade Econômica", 500)]
        DlgConsultaGenerica(self, "Pesquisa de Atividade Econômica", cols, dados, _selecionou)

    def _on_ativecon_focusout(self, event=None):
        cod = self.txt_ativecon_cod.get().strip()
        if not cod:
            self.lbl_ativecon_nome.set("")
            return
        if not self._service:
            self._inicializar_dependencias()
        if self._service:
            try:
                nome = self._service.obter_nome_atividade_economica(cod, base_dados=self.base_dados)
                self.lbl_ativecon_nome.set(nome)
            except Exception as exc:
                logger.warning("Falha ao resolver atividade econômica no FocusOut: %s", exc)

    def _abrir_consulta_origem(self):
        dados = []
        if not self._service:
            self._inicializar_dependencias()
        if self._service:
            try:
                dados = self._service.listar_origens(base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro na Consulta", f"Falha ao carregar origens: {exc}", parent=self)
                return

        def _selecionou(item):
            self.txt_origem_cod.delete(0, tk.END)
            self.txt_origem_cod.insert(0, str(item.get("codigo", "")))
            self.lbl_origem_nome.set(str(item.get("descricao", "")))
            self.statusbar.config(text=f"Origem selecionada: {item.get('descricao')}")

        cols = [("codigo", "Código", 140), ("descricao", "Nome da Origem", 500)]
        DlgConsultaGenerica(self, "Pesquisa de Origem", cols, dados, _selecionou)

    def _on_origem_focusout(self, event=None):
        cod = self.txt_origem_cod.get().strip()
        if not cod:
            self.lbl_origem_nome.set("")
            return
        if not self._service:
            self._inicializar_dependencias()
        if self._service:
            try:
                nome = self._service.obter_nome_origem(cod, base_dados=self.base_dados)
                self.lbl_origem_nome.set(nome)
            except Exception as exc:
                logger.warning("Falha ao resolver origem no FocusOut: %s", exc)

    def _abrir_consulta_regiao(self):
        dados = []
        if not self._service:
            self._inicializar_dependencias()
        if self._service:
            try:
                dados = self._service.listar_regioes(base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro na Consulta", f"Falha ao carregar regiões: {exc}", parent=self)
                return

        def _selecionou(item):
            self.txt_regiao_cod.delete(0, tk.END)
            self.txt_regiao_cod.insert(0, str(item.get("codigo", "")))
            self.lbl_regiao_nome.set(str(item.get("descricao", "")))
            self.statusbar.config(text=f"Região selecionada: {item.get('descricao')}")

        cols = [("codigo", "Código", 140), ("descricao", "Nome da Região", 500)]
        DlgConsultaGenerica(self, "Pesquisa de Regiões", cols, dados, _selecionou)

    def _on_regiao_focusout(self, event=None):
        cod = self.txt_regiao_cod.get().strip()
        if not cod:
            self.lbl_regiao_nome.set("")
            return
        if not self._service:
            self._inicializar_dependencias()
        if self._service:
            try:
                nome = self._service.obter_nome_regiao(cod, base_dados=self.base_dados)
                self.lbl_regiao_nome.set(nome)
            except Exception as exc:
                logger.warning("Falha ao resolver região no FocusOut: %s", exc)


    def _abrir_consulta_conceito(self):
        dados = []
        if self._service:
            try:
                dados = self._service.listar_conceitos()
            except Exception as exc:
                messagebox.showerror("Erro na Consulta", f"Falha ao carregar conceitos: {exc}", parent=self)
                return

        def _selecionou(item):
            self.txt_conceito.delete(0, tk.END)
            self.txt_conceito.insert(0, str(item.get("descricao", "")))
            self.statusbar.config(text=f"Conceito selecionado: {item.get('descricao')}")

        cols = [("codigo", "Código", 140), ("descricao", "Descrição do Conceito", 500)]
        DlgConsultaGenerica(self, "Pesquisa de Conceitos", cols, dados, _selecionou)

    def _abrir_consulta_cidade_cob(self):
        dados = []
        if self._service:
            try:
                dados = self._service.listar_cidades(base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro na Consulta", f"Falha ao carregar cidades: {exc}", parent=self)
                return

        def _selecionou(item):
            self.txt_cob_cidcod.delete(0, tk.END)
            self.txt_cob_cidcod.insert(0, str(item.get("codigo", "")))
            self.txt_cob_cidade.delete(0, tk.END)
            self.txt_cob_cidade.insert(0, str(item.get("nome", "")))
            self.txt_cob_uf.delete(0, tk.END)
            self.txt_cob_uf.insert(0, str(item.get("uf", "")))

        cols = [("codigo", "Código", 100), ("nome", "Nome da Cidade", 380), ("uf", "UF", 70)]
        DlgConsultaGenerica(self, "Pesquisa de Cidades - Cobrança", cols, dados, _selecionou)

    def _abrir_consulta_cidade_ent(self):
        dados = []
        if self._service:
            try:
                dados = self._service.listar_cidades(base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro na Consulta", f"Falha ao carregar cidades: {exc}", parent=self)
                return

        def _selecionou(item):
            self.txt_ent_cidcod.delete(0, tk.END)
            self.txt_ent_cidcod.insert(0, str(item.get("codigo", "")))
            self.txt_ent_cidade.delete(0, tk.END)
            self.txt_ent_cidade.insert(0, str(item.get("nome", "")))
            self.txt_ent_uf.delete(0, tk.END)
            self.txt_ent_uf.insert(0, str(item.get("uf", "")))

        cols = [("codigo", "Código", 100), ("nome", "Nome da Cidade", 380), ("uf", "UF", 70)]
        DlgConsultaGenerica(self, "Pesquisa de Cidades - Entrega", cols, dados, _selecionou)

    def _abrir_consulta_contato(self):
        dados = []
        if self._service:
            try:
                dados = self._service.listar_entidades_lookup(termo="", base_dados=self.base_dados)
            except Exception:
                pass
        elif self._repo:
            try:
                dados = self._repo.listar_entidades_lookup(termo="", base_dados=self.base_dados)
            except Exception:
                pass

        def _selecionou(item):
            self.txt_contato_cod.delete(0, tk.END)
            self.txt_contato_cod.insert(0, str(item.get("codigo", "")))
            self.lbl_contato_nome.set(str(item.get("nome", "")))

        cols = [("codigo", "Código", 100), ("nome", "Nome / Razão Social da Entidade", 450), ("tipo", "Tipo", 80)]
        DlgConsultaGenerica(self, "Pesquisa de Entidades (Contato / Responsável)", cols, dados, _selecionou)

    def _abrir_consulta_contato_cargo(self):
        dados = []
        if self._service:
            try:
                dados = self._service.listar_cargos_lookup(base_dados=self.base_dados)
            except Exception:
                pass

        def _selecionou(item):
            self.txt_contato_cargo_cod.delete(0, tk.END)
            self.txt_contato_cargo_cod.insert(0, str(item.get("codigo", "")))
            self.lbl_contato_cargo_nome.set(str(item.get("descricao", "")))

        cols = [("codigo", "Código", 120), ("descricao", "Nome / Cargo", 480)]
        DlgConsultaGenerica(self, "Pesquisa de Cargo do Contato", cols, dados, _selecionou)

    def _formatar_valor_real(self):
        val = self.txt_valorcontrib.get().strip()
        num_str = "".join(c for c in val if c.isdigit() or c in ",.")
        if "," in num_str and "." in num_str:
            num_str = num_str.replace(".", "").replace(",", ".")
        elif "," in num_str:
            num_str = num_str.replace(",", ".")
        try:
            f_val = float(num_str) if num_str else 0.0
            formatado = f"R$ {f_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            self.txt_valorcontrib.delete(0, tk.END)
            self.txt_valorcontrib.insert(0, formatado)
        except Exception:
            pass

    def _formatar_valor_dolar(self):
        val = self.txt_valorcontrib.get().strip()
        num_str = "".join(c for c in val if c.isdigit() or c in ",.")
        if "," in num_str and "." in num_str:
            num_str = num_str.replace(".", "").replace(",", ".")
        elif "," in num_str:
            num_str = num_str.replace(",", ".")
        try:
            f_val = float(num_str) if num_str else 0.0
            self.txt_valorcontrib.delete(0, tk.END)
            self.txt_valorcontrib.insert(0, f"US$ {f_val:,.2f}")
        except Exception:
            pass

    def _verificar_alerta_menor(self, event=None):
        if not hasattr(self, "txt_dtnasc") or not self.txt_dtnasc.winfo_exists():
            return
        data_str = self.txt_dtnasc.get().strip()
        idade = _calcular_idade(data_str)
        is_packed = bool(hasattr(self, "frame_alerta_menor") and self.frame_alerta_menor.winfo_manager() == "pack")
        if idade is not None and idade < 18:
            msg = f"⚠️ ATENÇÃO: Entidade menor de 18 anos ({idade} anos). Obrigatório cadastrar responsável legal na aba Contatos para emissão de doações por boleto."
            self.lbl_alerta_menor.config(text=msg)
            if hasattr(self, "frame_alerta_menor") and not is_packed:
                target_before = getattr(self, "sub_notebook_contatos", None) or getattr(self, "frame_contatos_body", None)
                if target_before:
                    self.frame_alerta_menor.pack(side=tk.TOP, fill=tk.X, padx=4, pady=4, before=target_before)
                else:
                    self.frame_alerta_menor.pack(side=tk.TOP, fill=tk.X, padx=4, pady=4)
        else:
            self.lbl_alerta_menor.config(text="")
            if hasattr(self, "frame_alerta_menor") and is_packed:
                self.frame_alerta_menor.pack_forget()

    def _on_grupooracao_toggle(self):
        # As datas de vigência permanecem sempre habilitadas para edição
        if hasattr(self, "txt_dtiniciovigencia") and self.txt_dtiniciovigencia.winfo_exists():
            self.txt_dtiniciovigencia.config(state="normal")
        if hasattr(self, "txt_dtfinalvigencia") and self.txt_dtfinalvigencia.winfo_exists():
            self.txt_dtfinalvigencia.config(state="normal")

    def _toggle_subtab_endcobranca(self):
        val = self.var_end_cob_mesmo.get()
        subabas = [self.sub_notebook.tab(i, "text").strip() for i in range(self.sub_notebook.index("end"))]
        if val == "Não":
            if "End. Cobrança" not in subabas:
                self.sub_notebook.add(self.subtab_endcobranca, text="  End. Cobrança  ")
                self.sub_notebook.select(self.subtab_endcobranca)
        else:
            if "End. Cobrança" in subabas:
                idx = subabas.index("End. Cobrança")
                self.sub_notebook.forget(idx)

    def _toggle_subtab_endentrega(self):
        val = self.var_end_ent_mesmo.get()
        subabas = [self.sub_notebook.tab(i, "text").strip() for i in range(self.sub_notebook.index("end"))]
        if val == "Não":
            if "End. Entrega" not in subabas:
                self.sub_notebook.add(self.subtab_endentrega, text="  End. Entrega  ")
                self.sub_notebook.select(self.subtab_endentrega)
        else:
            if "End. Entrega" in subabas:
                idx = subabas.index("End. Entrega")
                self.sub_notebook.forget(idx)

    def _consultar_viacep_cobranca(self, event=None):
        cep = self.txt_cob_cep.get().strip()
        if not cep or len(cep.replace("-", "").replace(".", "")) < 8:
            return
        dados_cep = None
        if self._service:
            try:
                dados_cep = self._service.consultar_cep(cep)
            except Exception:
                pass
        if not dados_cep:
            return
        rua = dados_cep.get("logradouro", "")
        bairro = dados_cep.get("bairro", "")
        cid = dados_cep.get("cidade", "")
        uf = dados_cep.get("uf", "")
        if rua:
            self.txt_cob_ender.delete(0, tk.END)
            self.txt_cob_ender.insert(0, rua)
        if bairro:
            self.txt_cob_bair.delete(0, tk.END)
            self.txt_cob_bair.insert(0, bairro)
        if cid:
            self.txt_cob_cidade.delete(0, tk.END)
            self.txt_cob_cidade.insert(0, cid)
        if uf:
            self.txt_cob_uf.delete(0, tk.END)
            self.txt_cob_uf.insert(0, uf)
        if cid and uf:
            cid_info = self._buscar_cidade_por_nome_uf(cid, uf)
            if cid_info:
                self.txt_cob_cidcod.delete(0, tk.END)
                self.txt_cob_cidcod.insert(0, str(cid_info.get("codigo", "")))
        self.txt_cob_enderno.focus_set()

    def _consultar_viacep_entrega(self, event=None):
        cep = self.txt_ent_cep.get().strip()
        if not cep or len(cep.replace("-", "").replace(".", "")) < 8:
            return
        dados_cep = None
        if self._service:
            try:
                dados_cep = self._service.consultar_cep(cep)
            except Exception:
                pass
        if not dados_cep:
            return
        rua = dados_cep.get("logradouro", "")
        bairro = dados_cep.get("bairro", "")
        cid = dados_cep.get("cidade", "")
        uf = dados_cep.get("uf", "")
        if rua:
            self.txt_ent_ender.delete(0, tk.END)
            self.txt_ent_ender.insert(0, rua)
        if bairro:
            self.txt_ent_bair.delete(0, tk.END)
            self.txt_ent_bair.insert(0, bairro)
        if cid:
            self.txt_ent_cidade.delete(0, tk.END)
            self.txt_ent_cidade.insert(0, cid)
        if uf:
            self.txt_ent_uf.delete(0, tk.END)
            self.txt_ent_uf.insert(0, uf)
        if cid and uf:
            cid_info = self._buscar_cidade_por_nome_uf(cid, uf)
            if cid_info:
                self.txt_ent_cidcod.delete(0, tk.END)
                self.txt_ent_cidcod.insert(0, str(cid_info.get("codigo", "")))
        self.txt_ent_enderno.focus_set()

    def _obter_usuario_atual(self) -> str:
        try:
            from logon import sessao_usuario_atual
            if sessao_usuario_atual and sessao_usuario_atual.get("usuario"):
                return str(sessao_usuario_atual.get("usuario")).upper()
        except Exception:
            pass
        return "SISTEMA"

    def _gravar_novo_historico(self):
        novo = self.txt_novohistorico.get("1.0", tk.END).strip()
        if not novo:
            messagebox.showwarning("Atenção", "Digite o texto do novo registro de histórico antes de salvar.", parent=self)
            self.txt_novohistorico.focus_set()
            return

        usuario = self._obter_usuario_atual()
        carimbo = f"[{usuario}] - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} - {novo}"

        # Atualiza memo cinza
        self.txt_historico.config(state="normal")
        hist_atual = self.txt_historico.get("1.0", tk.END).strip()
        if hist_atual:
            conteudo_total = carimbo + "\n" + ("-" * 60) + "\n" + hist_atual
        else:
            conteudo_total = carimbo
        self.txt_historico.delete("1.0", tk.END)
        self.txt_historico.insert("1.0", conteudo_total)
        self.txt_historico.config(state="disabled")

        self.txt_novohistorico.delete("1.0", tk.END)

        cod = self._obter_entcod_ativo()
        if cod and cod != "NOVO" and self._service:
            try:
                self._service.salvar_historico(cod, novo, usuario=usuario, base_dados=self.base_dados)
                self.statusbar.config(text=f"Histórico registrado no banco para entidade {cod}.")
            except Exception as exc:
                logger.warning("Falha ao gravar histórico no banco: %s", exc)
                self.statusbar.config(text="Histórico incluído em tela. Clique em Salvar para persistir.")
        else:
            self.statusbar.config(text="Histórico incluído em tela. Clique em Salvar para persistir.")

    # -------------------------------------------------------------
    # Autocomplete Dinâmico em Comboboxes, ViaCEP e Busca de Cidade
    # -------------------------------------------------------------
    def _configurar_autocomplete_combobox(self, combo: ttk.Combobox):
        """
        Permite digitar em qualquer combobox com busca e autocompletion dinâmico em tempo real,
        facilitando a seleção rápida e a correção de cadastros.
        """
        if not combo:
            return

        # Guarda valores originais
        if not hasattr(combo, "_valores_originais") or not combo._valores_originais:
            combo._valores_originais = list(combo["values"] or [])
        else:
            if combo["values"]:
                combo._valores_originais = list(combo["values"])

        # Muda para normal para permitir digitação direta pelo teclado
        try:
            combo.config(state="normal")
        except Exception:
            pass

        def _on_key_release(event):
            if event.keysym in ("Up", "Down", "Left", "Right", "Return", "Escape", "Tab",
                                "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R"):
                return

            texto = combo.get()
            originais = getattr(combo, "_valores_originais", None) or list(combo["values"] or [])
            if not texto:
                combo["values"] = originais
                return

            t_upper = texto.strip().upper()
            iniciam = [v for v in originais if str(v).strip().upper().startswith(t_upper)]
            contem = [v for v in originais if t_upper in str(v).strip().upper() and v not in iniciam]
            filtrados = iniciam + contem

            if filtrados:
                combo["values"] = filtrados
            else:
                combo["values"] = originais

        def _on_focus_out(event):
            val = combo.get().strip().upper()
            originais = getattr(combo, "_valores_originais", None) or list(combo["values"] or [])
            combo["values"] = originais
            if not val:
                return
            for v in originais:
                if str(v).strip().upper() == val:
                    combo.set(v)
                    return
            for v in originais:
                if str(v).strip().upper().startswith(val):
                    combo.set(v)
                    return

        combo.bind("<KeyRelease>", _on_key_release, add="+")
        combo.bind("<FocusOut>", _on_focus_out, add="+")

    def _configurar_autocomplete_logradouro(self):
        """Alias para manter compatibilidade com chamadas existentes."""
        if hasattr(self, "cbo_tipolograd"):
            self._configurar_autocomplete_combobox(self.cbo_tipolograd)

    def _aplicar_autocomplete_todos_combos(self):
        """Aplica autocomplete dinâmico a todos os comboboxes com conteúdo do formulário."""
        combos = [
            getattr(self, "cbo_tipotrat", None),
            getattr(self, "cbo_tipofj", None),
            getattr(self, "cbo_falecido", None),
            getattr(self, "cbo_sexo", None),
            getattr(self, "cbo_tipolograd", None),
            getattr(self, "cbo_estadocivil", None),
            getattr(self, "cbo_escolaridade", None),
            getattr(self, "cbo_geracarne", None),
            getattr(self, "cbo_recebelembrete", None),
            getattr(self, "cbo_cob_tipolograd", None),
            getattr(self, "cbo_ent_tipolograd", None),
            getattr(self, "cbo_contato_princ", None),
            getattr(self, "cbo_contato_status", None),
            getattr(self, "cbo_contato_graudecisao", None),
            getattr(self, "cbo_tel_tipo", None),
            getattr(self, "cbo_web_tipo", None),
            getattr(self, "cbo_doc_tipo", None),
        ]
        for c in combos:
            if c is not None and isinstance(c, ttk.Combobox):
                self._configurar_autocomplete_combobox(c)

    def _configurar_maiusculas_e_enter(self):
        """
        Padroniza todos os campos de texto como maiúsculos (exceto e-mails)
        e habilita navegação de um campo para o outro teclando <Enter>.
        """
        def _on_key_release_upper(event):
            widget = event.widget
            if event.keysym in (
                "Left", "Right", "Up", "Down", "Home", "End", "Tab", "Return",
                "Escape", "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Caps_Lock"
            ):
                return
            try:
                pos = widget.index(tk.INSERT)
                val = widget.get()
                val_u = val.upper()
                if val != val_u:
                    widget.delete(0, tk.END)
                    widget.insert(0, val_u)
                    widget.icursor(pos)
            except Exception:
                pass

        def _on_enter_navegar(event):
            widget = event.widget
            prox = widget.tk_focusNext()
            if prox:
                prox.focus_set()
                if hasattr(prox, "selection_range"):
                    try:
                        prox.selection_range(0, tk.END)
                    except Exception:
                        pass
            return "break"

        # Widgets que NÃO devem ser forçados para maiúsculo (ex: e-mails, URLs)
        widgets_ignorar_upper = set()
        for nome_attr in ("txt_web_email", "txt_web_site"):
            w = getattr(self, nome_attr, None)
            if w is not None:
                widgets_ignorar_upper.add(w)

        # Widgets com manipulador próprio de Return (consultas dinâmicas)
        widgets_ignorar_enter = set()
        for nome_attr in ("txt_cep", "txt_cidcod"):
            w = getattr(self, nome_attr, None)
            if w is not None:
                widgets_ignorar_enter.add(w)

        def _processar_container(container):
            for child in container.winfo_children():
                # Caixas multilinhas (observações e históricos) não interceptam Enter para permitir quebra de linha
                if isinstance(child, (tk.Text, ScrolledText)):
                    continue

                if isinstance(child, (ttk.Entry, tk.Entry)):
                    if child not in widgets_ignorar_upper:
                        child.bind("<KeyRelease>", _on_key_release_upper, add="+")
                    if child not in widgets_ignorar_enter:
                        child.bind("<Return>", _on_enter_navegar, add="+")

                elif isinstance(child, ttk.Combobox):
                    if child not in widgets_ignorar_enter:
                        child.bind("<Return>", _on_enter_navegar, add="+")

                if child.winfo_children():
                    _processar_container(child)

        _processar_container(self)



    def _on_cidcod_action(self, event=None):
        cidcod = self.txt_cidcod.get().strip()
        if not cidcod:
            return "break" if event else None
        res = self._buscar_cidade_por_codigo(cidcod, silencioso=False)
        if res and event and getattr(event, "keysym", "") == "Return":
            if hasattr(self, "txt_cxapost") and self.txt_cxapost.winfo_exists():
                self.txt_cxapost.focus_set()
            return "break"
        return "break" if event and getattr(event, "keysym", "") == "Return" else None

    def _on_cidcod_focus_out(self, event=None):
        cidcod = self.txt_cidcod.get().strip()
        if not cidcod:
            return
        if not self.txt_cidade.get().strip() or not self.txt_uf.get().strip():
            self._buscar_cidade_por_codigo(cidcod, silencioso=True)

    def _buscar_cidade_por_codigo(self, cidcod: str, silencioso: bool = False) -> Optional[Dict[str, Any]]:
        cidcod = str(cidcod).strip()
        if not cidcod:
            return None
        cidade_info = None
        if self._service:
            try:
                cidade_info = self._service.obter_cidade_por_codigo(cidcod, base_dados=self.base_dados)
            except Exception as exc:
                logger.warning("Falha ao buscar cidade por código via serviço: %s", exc)
        if not cidade_info and self._repo:
            try:
                cidade_info = self._repo.obter_cidade_por_codigo(cidcod, base_dados=self.base_dados)
            except Exception:
                pass

        if cidade_info:
            nome = cidade_info.get("nome", "")
            uf = cidade_info.get("uf", "")
            self.txt_cidade.delete(0, tk.END)
            self.txt_cidade.insert(0, nome)
            self.txt_uf.delete(0, tk.END)
            self.txt_uf.insert(0, uf)
            self.statusbar.config(text=f"Cidade localizada: {nome} - {uf}")
            return cidade_info
        else:
            if not silencioso:
                messagebox.showwarning("Cidade não encontrada", f"Código de cidade '{cidcod}' não encontrado no cadastro.", parent=self)
            return None

    def _buscar_cidade_por_nome_uf(self, nome: str, uf: str) -> Optional[Dict[str, Any]]:
        if not nome or not uf:
            return None
        cidade_info = None
        if self._service:
            try:
                cidade_info = self._service.obter_cidade_por_nome_uf(nome, uf, base_dados=self.base_dados)
            except Exception as exc:
                logger.warning("Falha ao buscar cidade por nome/uf: %s", exc)
        if not cidade_info and self._repo:
            try:
                cidade_info = self._repo.obter_cidade_por_nome_uf(nome, uf, base_dados=self.base_dados)
            except Exception:
                pass
        return cidade_info

    def _consultar_viacep(self, event=None):
        cep_raw = self.txt_cep.get().strip()
        cep_limpo = re.sub(r"\D", "", cep_raw)
        if len(cep_limpo) != 8:
            return

        self.statusbar.config(text=f"Consultando CEP {cep_limpo} no ViaCEP...")
        self.update_idletasks()

        dados_cep = None
        try:
            from core.viacep import consultar_cep
            dados_cep = consultar_cep(cep_limpo)
        except Exception as exc:
            logger.warning("Erro ao consultar ViaCEP: %s", exc)

        if not dados_cep:
            self.statusbar.config(text=f"CEP {cep_limpo} não encontrado no ViaCEP.")
            return

        logradouro_completo = dados_cep.get("logradouro", "").strip()
        bairro = dados_cep.get("bairro", "").strip()
        cidade = dados_cep.get("cidade", "").strip()
        uf = dados_cep.get("uf", "").strip()

        tipo_lograd = ""
        nome_rua = logradouro_completo
        if " " in logradouro_completo:
            primeira_palavra, resto = logradouro_completo.split(" ", 1)
            p_upper = primeira_palavra.upper()
            valores_combo = list(self.cbo_tipolograd["values"] or [])
            for val in valores_combo:
                v_u = str(val).upper()
                if v_u == p_upper or p_upper.startswith(v_u) or (p_upper == "AVENIDA" and v_u == "AV") or (p_upper == "PRAÇA" and v_u == "PCA") or (p_upper == "TRAVESSA" and v_u == "TRV") or (p_upper == "ALAMEDA" and v_u == "AL") or (p_upper == "RODOVIA" and v_u == "ROD"):
                    tipo_lograd = val
                    nome_rua = resto.strip()
                    break

        if tipo_lograd:
            self.cbo_tipolograd.set(tipo_lograd)
        if nome_rua:
            self.txt_ender.delete(0, tk.END)
            self.txt_ender.insert(0, nome_rua)
        if bairro:
            self.txt_bair.delete(0, tk.END)
            self.txt_bair.insert(0, bairro)
        if cidade:
            self.txt_cidade.delete(0, tk.END)
            self.txt_cidade.insert(0, cidade)
        if uf:
            self.txt_uf.delete(0, tk.END)
            self.txt_uf.insert(0, uf)

        if cidade and uf:
            cid_info = self._buscar_cidade_por_nome_uf(cidade, uf)
            if cid_info:
                self.txt_cidcod.delete(0, tk.END)
                self.txt_cidcod.insert(0, str(cid_info.get("codigo", "")))

        self.txt_enderno.focus_set()
        self.txt_enderno.select_range(0, tk.END)
        self.statusbar.config(text=f"Endereço preenchido via ViaCEP: {logradouro_completo}, {cidade}-{uf}.")

    # -------------------------------------------------------------
    # Mapeamento e Preenchimento
    # -------------------------------------------------------------
    def _preencher_dados(self, r: Dict[str, Any]):
        def s(k, default=""):
            v = r.get(k)
            return str(v).strip() if v is not None else default

        def _set_entry(widget, text):
            if widget is None:
                return
            orig_state = str(widget.cget("state")) if hasattr(widget, "cget") else ""
            if orig_state == "readonly":
                widget.config(state="normal")
            if hasattr(widget, "delete") and hasattr(widget, "insert"):
                widget.delete(0, tk.END)
                widget.insert(0, str(text or ""))
            elif hasattr(widget, "set"):
                widget.set(str(text or ""))
            elif hasattr(widget, "config"):
                widget.config(text=str(text or ""))
            if orig_state == "readonly":
                widget.config(state="readonly")

        # 1. Principal
        _set_entry(self.txt_geoentcod, s("geoentcod"))
        _set_entry(self.txt_entcod, s("entcod"))

        # Tipo Tratamento
        trat = s("tipotratcod") or s("geotipotratcod")
        if trat:
            for v in self.cbo_tipotrat["values"]:
                if trat.upper() == str(v).upper() or trat.upper() == str(v).split(" - ")[0].upper():
                    trat = v
                    break
        self.cbo_tipotrat.set(trat)

        _set_entry(self.txt_nome, s("entnome") or s("geoentnome"))
        _set_entry(self.txt_nomefantasia, s("entnomefant") or s("geoentnomefantasia"))

        # CPF / CNPJ e RG / IE (se não preenchidos na entidade, consulta documentos)
        cpf = s("EntCpfCgc") or s("entcpfcgc") or s("Documento")
        rg = s("geoentrgie") or s("EntRgIe") or s("entrgie")
        cod_ativo = s("geoentcod") or s("entcod")
        if (not cpf or not rg) and self._service and cod_ativo and cod_ativo != "NOVO":
            try:
                docs_existentes = self._service.listar_documentos(cod_ativo, base_dados=self.base_dados)
                for d in docs_existentes:
                    tp = str(d.get("tipo") or "").upper()
                    doc_val = str(d.get("documento") or "").strip()
                    if not cpf and ("CPF" in tp or "CNPJ" in tp):
                        cpf = doc_val
                    if not rg and ("RG" in tp or "IE" in tp):
                        rg = doc_val
            except Exception:
                pass
        _set_entry(self.txt_cpf_cnpj, cpf)
        _set_entry(self.txt_rg_ie, rg)

        fj = (s("enttipofj") or s("geotipofj") or "F").upper()
        self.cbo_tipofj.set("J" if fj == "J" else "F")

        fal = (s("USERFalecido") or s("geofalecido") or "N").upper()
        self.cbo_falecido.set("Sim" if fal in ("S", "SIM") else "Não")

        sexo = (s("entgenero") or s("geoentgenero") or "M").upper()
        if sexo.startswith("M"):
            self.cbo_sexo.set("MASCULINO")
        elif sexo.startswith("F"):
            self.cbo_sexo.set("FEMININO")
        else:
            self.cbo_sexo.set("NENHUM")

        ec = s("entestcivil") or s("geoentestcivil") or "SOLTEIRO(A)"
        self.cbo_estadocivil.set(ec.upper())

        _set_entry(self.txt_dtnasc, formatar_data_br(s("entdataanivfund") or s("geoentdataanivfund")))
        self._verificar_alerta_menor()

        # Data de Cadastro: se inclusão ou nova entidade, preenche com a data do dia; senão traz do banco
        dt_cad_db = s("entdesdedata") or s("entdatacad") or s("geoentdatacad")
        cod_ent = s("geoentcod") or s("entcod")
        if not dt_cad_db or not cod_ent or cod_ent == "NOVO":
            _set_entry(self.txt_dtcad, date.today().strftime("%d/%m/%Y"))
        else:
            _set_entry(self.txt_dtcad, formatar_data_br(dt_cad_db))

        # Escolaridade
        esc = s("EntGrauEscol") or s("codigo_grauescolaridade") or s("entgrauescol")
        if esc:
            for v in self.cbo_escolaridade["values"]:
                if str(esc).strip() == str(v).split(" - ")[0].strip() or str(esc).strip().upper() in str(v).upper():
                    esc = v
                    break
        self.cbo_escolaridade.set(esc)

        # Cargo / Ocupação
        _set_entry(self.txt_cargo_cod, s("cargocodestr") or s("geocargocodestr"))
        _set_entry(self.txt_cargo_nome, s("cargonome") or s("geocargonome"))

        # 2. Endereço Principal
        _set_entry(self.txt_cep, s("entcep") or s("geoentcep"))
        lograd_carregado = s("tipologradabrev") or s("logradouro") or s("entlograd")
        if not lograd_carregado or str(lograd_carregado).isdigit():
            mapa_rev = {"1": "R", "115": "Av", "2": "Av", "3": "Al", "4": "Pç", "472": "Rod", "583": "Trv", "251": "Est"}
            lograd_carregado = mapa_rev.get(str(s("tipolograd")), s("tipolograd") or "")
        self.cbo_tipolograd.set(lograd_carregado)
        _set_entry(self.txt_ender, s("entender") or s("geoentender"))
        _set_entry(self.txt_enderno, s("entenderno") or s("geoenderno"))
        _set_entry(self.txt_endercomp, s("entendercomp") or s("geoentendercomp"))
        _set_entry(self.txt_bair, s("entbair") or s("geoentbair"))

        cid_cod = s("cidcod") or s("geocidcod") or s("cidcodapolo") or s("geocidcodapolo")
        cidade_nome = s("cidnomecomp") or s("cidnome") or s("cidade") or s("cidadenome")
        uf_sigla = s("ufsigla") or s("uf") or s("siglauf") or s("estado")

        if not uf_sigla and "/" in cidade_nome:
            partes_cid = cidade_nome.split("/")
            cidade_nome = partes_cid[0].strip()
            uf_sigla = partes_cid[1].strip()
        elif not uf_sigla and " - " in cidade_nome:
            partes_cid = cidade_nome.split(" - ")
            cidade_nome = partes_cid[0].strip()
            uf_sigla = partes_cid[1].strip()

        if cid_cod:
            _set_entry(self.txt_cidcod, cid_cod)
            if not cidade_nome or not uf_sigla:
                cid_info = self._buscar_cidade_por_codigo(cid_cod, silencioso=True)
                if cid_info:
                    cidade_nome = cid_info.get("nome") or cidade_nome
                    uf_sigla = cid_info.get("uf") or uf_sigla
        elif cidade_nome and uf_sigla:
            cid_info = self._buscar_cidade_por_nome_uf(cidade_nome, uf_sigla)
            if cid_info:
                cid_cod = cid_info.get("codigo") or ""
                _set_entry(self.txt_cidcod, cid_cod)

        _set_entry(self.txt_cidade, cidade_nome)
        _set_entry(self.txt_uf, uf_sigla)

        _set_entry(self.txt_cxapost, s("EntCxaPost") or s("geoentcxapost"))
        _set_entry(self.txt_referencia, s("geolocalreferencia_ender"))

        # 3. Pessoal
        _set_entry(self.txt_nomepai, s("entnomepai") or s("geoentnomepai"))
        _set_entry(self.txt_nomemae, s("entnomemae") or s("geoentnomemae"))
        _set_entry(self.txt_residecom, s("entmoracom") or s("geoentmoracom"))
        filhos = s("entpossuifilho") or s("geoentpossuifilho")
        self.cbo_filhos.set("Sim" if filhos.lower() in ("sim", "s") else "Não")
        _set_entry(self.txt_quantosfilhos, s("quantosfilhos") or s("numerofilhos"))

        # 4. Financeiro
        _set_entry(self.txt_tipocobcod, s("tipocobcod") or s("geotipocobcod"))
        _set_entry(self.txt_tipocobnome, s("tipocobnome") or s("geotipocobnome"))
        if self.txt_tipocobcod.get().strip() and not self.txt_tipocobnome.get().strip():
            self._validar_codigo_tipocob()
        carne = s("USERGeraCarne") or s("geogeracarne") or s("geogerarcarne")
        self.cbo_geracarne.set("Sim" if carne.lower() in ("s", "sim") else "Não")

        _set_entry(self.txt_bconum, s("bconum") or s("geobconum"))
        _set_entry(self.txt_bconome, s("bconome"))
        _set_entry(self.txt_agnum, s("agnum") or s("geoagnum"))
        _set_entry(self.txt_agnome, s("agnome"))
        _set_entry(self.txt_cc, s("EntBcoAgCCorNum") or s("geoentcontacorrente") or s("geoconta"))
        
        dia_deb = s("USERDia_Debito_CC") or s("dia_debito") or s("geodia_contribuicao")
        tcob_nome = s("tipocobnome") or s("geotipocobnome")
        if not dia_deb and ("DEB" in tcob_nome.upper() or "DÉB" in tcob_nome.upper()):
            dia_deb = "10"
        _set_entry(self.txt_diadebito, dia_deb)
        
        _set_entry(self.txt_valorcontrib, s("USERValor_Contribuicao") or s("geovalorcontribuicao") or "25.00")
        self._formatar_valor_real()

        id_dioc = s("USERDiocese_id") or s("geodioceseid")
        _set_entry(self.txt_dioceseid, id_dioc)
        nome_dioc = s("USERNomeDiocese") or s("Diocese") or s("diocesenome")
        if not nome_dioc and id_dioc and self._service:
            try:
                nome_dioc = self._service.obter_nome_diocese(id_dioc)
            except Exception:
                pass
        self.lbl_diocesenome.set(nome_dioc or "")

        lembr = s("USERRecebelembretedoacao") or s("georecebelembrete")
        self.cbo_recebelembrete.set("Sim" if lembr.lower() in ("s", "sim") else "Não")

        # 5. Complementares / Observações
        cod_ativ = s("ativeconcodestr") or s("geoativeconcodestr")
        _set_entry(self.txt_ativecon_cod, cod_ativ)
        nome_ativ = s("ativeconnome")
        if not nome_ativ and cod_ativ and self._service:
            try:
                nome_ativ = self._service.obter_nome_atividade_economica(cod_ativ, base_dados=self.base_dados)
            except Exception:
                pass
        self.lbl_ativecon_nome.set(nome_ativ or "")

        cod_orig = s("origcodestr") or s("geo_origcodestr")
        _set_entry(self.txt_origem_cod, cod_orig)
        nome_orig = s("orignome") or s("geo_orignome")
        if not nome_orig and cod_orig and self._service:
            try:
                nome_orig = self._service.obter_nome_origem(cod_orig, base_dados=self.base_dados)
            except Exception:
                pass
        self.lbl_origem_nome.set(nome_orig or "")

        cod_reg = s("regcodestr") or s("georegcodestr")
        _set_entry(self.txt_regiao_cod, cod_reg)
        nome_reg = s("regnome") or s("geo_regnome")
        if not nome_reg and cod_reg and self._service:
            try:
                nome_reg = self._service.obter_nome_regiao(cod_reg, base_dados=self.base_dados)
            except Exception:
                pass
        self.lbl_regiao_nome.set(nome_reg or "")

        _set_entry(self.txt_conceito_cod, s("entconceito") or s("geoentconceito"))
        _set_entry(self.txt_conceito_nome, s("entconceito") or s("geoentconceito"))

        # Endereço de Cobrança Secundário
        cob_cep = s("geocobcep") or s("cobcep") or s("EndCobrancaCep")
        cob_ender = s("geocobender") or s("cobender") or s("EndCobrancaEnder")
        if cob_cep or cob_ender:
            self.var_end_cob_mesmo.set("Não")
            self._toggle_subtab_endcobranca()
            _set_entry(self.txt_cob_cep, cob_cep)
            self.cbo_cob_tipolograd.set(s("geocoblograd") or s("coblograd") or s("EndCobrancaLograd"))
            _set_entry(self.txt_cob_ender, cob_ender)
            _set_entry(self.txt_cob_enderno, s("geocobenderno") or s("cobenderno") or s("EndCobrancaEnderNo"))
            _set_entry(self.txt_cob_endercomp, s("geocobendercomp") or s("cobendercomp") or s("EndCobrancaEnderComp"))
            _set_entry(self.txt_cob_bair, s("geocobbair") or s("cobbair") or s("EndCobrancaBair"))
            _set_entry(self.txt_cob_cidcod, s("geocobcidcod") or s("cobcidcod") or s("EndCobrancaCidCod"))
            _set_entry(self.txt_cob_cidade, s("geocobcidade") or s("cobcidade") or s("EndCobrancaCidade"))
            _set_entry(self.txt_cob_uf, s("geocobuf") or s("cobuf") or s("EndCobrancaUF"))
        else:
            self.var_end_cob_mesmo.set("Sim")
            self._toggle_subtab_endcobranca()

        # Endereço de Entrega Secundário
        ent_cep = s("geoentregacep") or s("entregacep") or s("EndEntregaCep")
        ent_ender = s("geoentregaender") or s("entregaender") or s("EndEntregaEnder")
        if ent_cep or ent_ender:
            self.var_end_ent_mesmo.set("Não")
            self._toggle_subtab_endentrega()
            _set_entry(self.txt_ent_cep, ent_cep)
            self.cbo_ent_tipolograd.set(s("geoentregalograd") or s("entregalograd") or s("EndEntregaLograd"))
            _set_entry(self.txt_ent_ender, ent_ender)
            _set_entry(self.txt_ent_enderno, s("geoentregaenderno") or s("entregaenderno") or s("EndEntregaEnderNo"))
            _set_entry(self.txt_ent_endercomp, s("geoentregaendercomp") or s("entregaendercomp") or s("EndEntregaEnderComp"))
            _set_entry(self.txt_ent_bair, s("geoentregabair") or s("entregabair") or s("EndEntregaBair"))
            _set_entry(self.txt_ent_cidcod, s("geoentregacidcod") or s("entregacidcod") or s("EndEntregaCidCod"))
            _set_entry(self.txt_ent_cidade, s("geoentregacidade") or s("entregacidade") or s("EndEntregaCidade"))
            _set_entry(self.txt_ent_uf, s("geoentregauf") or s("entregauf") or s("EndEntregaUF"))
        else:
            self.var_end_ent_mesmo.set("Sim")
            self._toggle_subtab_endentrega()

        # Observações
        self.txt_observacoes.delete("1.0", tk.END)
        texto_obs = s("Entobservacoes") or s("geoobservacoes")
        texto_obs = re.sub(
            r"(Última Atualização do G\.O\.:\s*)(\d{4})-(\d{2})-(\d{2})",
            r"\1\4/\3/\2",
            texto_obs,
            flags=re.IGNORECASE
        )
        self.txt_observacoes.insert("1.0", texto_obs)

        # Histórico da Entidade (enthist no memo cinza desabilitado)
        hist_val = s("enthist") or s("geoenthist") or s("enttextohist") or s("geoenttextohist")
        if hasattr(self, "txt_historico"):
            self.txt_historico.config(state="normal")
            self.txt_historico.delete("1.0", tk.END)
            self.txt_historico.insert("1.0", hist_val)
            self.txt_historico.config(state="disabled")

        # Grupo de Oração, Vigência de Mandato e Coordenador
        is_go = (s("chkgrupooracao").upper() in ("S", "SIM", "TRUE", "1") or
                 "GRUPO DE ORAÇÃO" in s("geocategnome").upper() or
                 "GRUPO DE ORAÇÃO" in s("categnome").upper())
        self.var_grupooracao.set(is_go)
        self._on_grupooracao_toggle()
        _set_entry(self.txt_dtiniciovigencia, formatar_data_br(s("dtiniciovigencia") or s("geodtiniciovigencia")))
        _set_entry(self.txt_dtfinalvigencia, formatar_data_br(s("dtfinalvigencia") or s("geodtfinalvigencia")))
        _set_entry(self.txt_contato_cod, s("contatocod") or s("geocontatocod"))
        _set_entry(self.lbl_contato_nome, s("contatonome") or s("geocontatonome"))
        _set_entry(self.txt_contato_cargo_cod, s("contatocargocod") or s("geocontatocargocod"))
        _set_entry(self.lbl_contato_cargo_nome, s("contatocargonome") or s("geocontatocargonome"))
        if s("contatoprinc"):
            self.cbo_contato_princ.set(s("contatoprinc"))
        if s("contatostatus"):
            self.cbo_contato_status.set(s("contatostatus"))
        if s("contatograudecisao"):
            self.cbo_contato_graudecisao.set(s("contatograudecisao"))

        # Se os campos de contato ou vigência não vieram do registro principal, busca na tabela USER_geoapolo_entidade_contato
        if (not self.txt_contato_cod.get().strip() or not self.txt_dtiniciovigencia.get().strip()) and self._repo and cod_ent and cod_ent != "NOVO":
            try:
                contatos_vinculados = self._repo.carregar_contatos_entidade(cod_ent)
                if contatos_vinculados:
                    c_princ = contatos_vinculados[0]
                    if not self.txt_contato_cod.get().strip():
                        _set_entry(self.txt_contato_cod, c_princ.get("EntCodContato") or "")
                        _set_entry(self.lbl_contato_nome, c_princ.get("geoentnome") or "")
                    if not self.txt_contato_cargo_cod.get().strip():
                        _set_entry(self.txt_contato_cargo_cod, c_princ.get("CargoCodEstr") or "")
                        _set_entry(self.lbl_contato_cargo_nome, c_princ.get("geocargonome") or c_princ.get("CargoCodEstr") or "")
                    if not self.txt_dtiniciovigencia.get().strip():
                        _set_entry(self.txt_dtiniciovigencia, formatar_data_br(c_princ.get("data_vigencia_inicial")))
                    if not self.txt_dtfinalvigencia.get().strip():
                        _set_entry(self.txt_dtfinalvigencia, formatar_data_br(c_princ.get("data_vigencia_final")))
            except Exception as exc:
                logger.warning("Erro ao carregar contato vinculado para %s: %s", cod_ent, exc)

        # 6. Categorias, Contatos, Documentos e Doações
        self._carregar_categorias(r)
        self._carregar_contatos(r)
        self._carregar_documentos(r)
        self._carregar_doacoes()


    def _carregar_doacoes(self):
        if not hasattr(self, "tree_doacoes"):
            return
        for item in self.tree_doacoes.get_children():
            self.tree_doacoes.delete(item)

        # Prioriza o código do Alvo (entcod), pois títulos/contribuições no Alvo usam entcod
        cod_alvo = ""
        if hasattr(self, "txt_entcod") and self.txt_entcod.winfo_exists():
            cod_alvo = self.txt_entcod.get().strip()
        if not cod_alvo:
            cod_alvo = str(self.registro.get("entcod") or "").strip()

        cod = cod_alvo or self._obter_entcod_ativo()
        if not cod or cod == "NOVO" or not self._service:
            return

        try:
            doacoes = self._service.obter_ultimas_doacoes(cod, limite=1000)
            for d in doacoes:
                dt_pag = formatar_data_br(d.get("datapag"))
                dt_venc = formatar_data_br(d.get("datavenc"))
                val_num = d.get("valor")
                val_str = f"{float(val_num):.2f}" if val_num is not None else "0.00"
                self.tree_doacoes.insert(
                    "",
                    tk.END,
                    values=(
                        dt_pag or "-",
                        dt_venc or "-",
                        val_str,
                        str(d.get("especie") or ""),
                        str(d.get("documento") or ""),
                        str(d.get("tipocob") or ""),
                        str(d.get("status") or ""),
                    )
                )
        except Exception as exc:
            logger.warning("Falha ao carregar doações para entidade %s: %s", cod, exc)


    def _obter_entcod_ativo(self) -> str:
        cod = ""
        if hasattr(self, "txt_geoentcod") and self.txt_geoentcod.winfo_exists():
            cod = self.txt_geoentcod.get().strip()
        if not cod and hasattr(self, "txt_entcod") and self.txt_entcod.winfo_exists():
            cod = self.txt_entcod.get().strip()
        if not cod or cod == "NOVO":
            cod = str(self.registro.get("geoentcod") or self.registro.get("entcod") or "").strip()
        return cod

    # -------------------------------------------------------------------------
    # Gerenciamento de Categorias
    # -------------------------------------------------------------------------
    def _carregar_categorias(self, r: Optional[Dict[str, Any]] = None):
        if not hasattr(self, "tree_categorias"):
            return
        for item in self.tree_categorias.get_children():
            self.tree_categorias.delete(item)

        cod = self._obter_entcod_ativo()
        lista = []
        if self._service and cod and cod != "NOVO":
            try:
                lista = self._service.listar_categorias(cod, base_dados=self.base_dados)
            except Exception as exc:
                logger.warning("Falha ao carregar categorias via serviço: %s", exc)

        if not lista and r:
            categ_cod = r.get("geocategcodestr") or r.get("categcodestr")
            categ_nome = r.get("geocategnome") or r.get("categnome")
            if categ_cod:
                lista.append({"codigo": str(categ_cod), "descricao": str(categ_nome or "")})
            if "categorias" in r and isinstance(r["categorias"], list):
                lista.extend(r["categorias"])

        codigos_adicionados = set()
        for it in lista:
            c = str(it.get("codigo") or it.get("geocategcodestr") or it.get("categcodestr") or "").strip()
            d = str(it.get("descricao") or it.get("geocategnome") or it.get("categnome") or "").strip()
            if c and c.upper() not in codigos_adicionados:
                codigos_adicionados.add(c.upper())
                self.tree_categorias.insert("", tk.END, values=(c, d))

    def _adicionar_categoria(self):
        cod = self._obter_entcod_ativo()
        cat_cod = self.txt_categ_cod.get().strip()
        cat_nome = self.txt_categ_nome.get().strip()
        if not cat_cod:
            messagebox.showwarning("Atenção", "Informe o código da categoria a ser vinculada.", parent=self)
            self.txt_categ_cod.focus_set()
            return

        for item in self.tree_categorias.get_children():
            vals = self.tree_categorias.item(item, "values")
            if vals and vals[0].upper() == cat_cod.upper():
                messagebox.showwarning("Atenção", "Esta categoria já está associada à entidade.", parent=self)
                self.tree_categorias.focus_set()
                return

        if self._service and cod and cod != "NOVO":
            try:
                self._service.adicionar_categoria(cod, cat_cod, base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro ao Vincular Categoria", f"Erro no banco: {exc}", parent=self)
                return

        self.tree_categorias.insert("", tk.END, values=(cat_cod, cat_nome))
        self.txt_categ_cod.delete(0, tk.END)
        self.txt_categ_nome.delete(0, tk.END)
        self.statusbar.config(text=f"Categoria '{cat_cod}' vinculada com sucesso.")
        self.tree_categorias.focus_set()

    def _remover_categoria(self):
        sel = self.tree_categorias.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione uma categoria na lista para remover.", parent=self)
            self.tree_categorias.focus_set()
            self.focus_force()
            return

        vals = self.tree_categorias.item(sel[0], "values")
        cat_cod = vals[0] if vals else ""
        if not cat_cod:
            return

        if not messagebox.askyesno("Confirmação", f"Deseja realmente desvincular a categoria '{cat_cod}'?", parent=self):
            self.tree_categorias.focus_set()
            self.focus_force()
            return

        cod = self._obter_entcod_ativo()
        if self._service and cod and cod != "NOVO":
            try:
                self._service.remover_categoria(cod, cat_cod, base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro ao Remover Categoria", f"Erro no banco: {exc}", parent=self)
                self.tree_categorias.focus_set()
                self.focus_force()
                return

        self.tree_categorias.delete(sel[0])
        self.statusbar.config(text=f"Categoria '{cat_cod}' removida com sucesso.")
        restantes = self.tree_categorias.get_children()
        if restantes:
            self.tree_categorias.selection_set(restantes[0])
            self.tree_categorias.focus(restantes[0])
        self.tree_categorias.focus_set()
        self.focus_force()

    def _on_categ_double_click(self, event=None):
        sel = self.tree_categorias.selection()
        if not sel:
            return
        vals = self.tree_categorias.item(sel[0], "values")
        if vals and len(vals) >= 2:
            self.txt_categ_cod.delete(0, tk.END)
            self.txt_categ_cod.insert(0, vals[0])
            self.txt_categ_nome.delete(0, tk.END)
            self.txt_categ_nome.insert(0, vals[1])

    # -------------------------------------------------------------------------
    # Gerenciamento de Contatos (Telefones e Web)
    # -------------------------------------------------------------------------
    def _carregar_contatos(self, r: Optional[Dict[str, Any]] = None):
        if not hasattr(self, "tree_telefones") or not hasattr(self, "tree_webcontatos"):
            return
        for item in self.tree_telefones.get_children():
            self.tree_telefones.delete(item)
        for item in self.tree_webcontatos.get_children():
            self.tree_webcontatos.delete(item)

        cod = self._obter_entcod_ativo()
        tels = []
        webs = []
        if self._service and cod and cod != "NOVO":
            try:
                tels = self._service.listar_telefones(cod, base_dados=self.base_dados)
                webs = self._service.listar_webcontatos(cod, base_dados=self.base_dados)
            except Exception as exc:
                logger.warning("Falha ao carregar contatos via serviço: %s", exc)

        if not tels and r:
            fone = r.get("Telefone") or r.get("entfonenum") or r.get("geotelefonenumero")
            if fone:
                ddd = r.get("EntFoneDDD") or r.get("geotelefoneddd") or ""
                tels.append({
                    "tipotelefone": "Celular",
                    "ddi": "55",
                    "ddd": str(ddd),
                    "numero": str(fone),
                    "ramal": "",
                    "principal": "Sim"
                })
            if "telefones" in r and isinstance(r["telefones"], list):
                tels.extend(r["telefones"])

        for t in tels:
            self.tree_telefones.insert(
                "",
                tk.END,
                values=(
                    t.get("tipotelefone") or t.get("tipo") or "Celular",
                    t.get("ddi") or "55",
                    t.get("ddd") or "",
                    t.get("numero") or "",
                    t.get("ramal") or "",
                    t.get("principal") or "Sim",
                )
            )

        if not webs and r:
            email = r.get("Email") or r.get("email") or r.get("entwebemail")
            if email:
                webs.append({
                    "tipo_contato": "Pessoal",
                    "email": str(email),
                    "website": str(r.get("website") or ""),
                    "comunicador_instantaneo": "",
                    "principal": "Sim"
                })
            if "webcontatos" in r and isinstance(r["webcontatos"], list):
                webs.extend(r["webcontatos"])

        for w in webs:
            self.tree_webcontatos.insert(
                "",
                tk.END,
                values=(
                    w.get("tipo_contato") or w.get("tipo") or "Pessoal",
                    w.get("email") or "",
                    w.get("website") or "",
                    w.get("comunicador_instantaneo") or w.get("comunicador") or "",
                    w.get("principal") or "Sim",
                )
            )

    def _adicionar_telefone(self):
        cod = self._obter_entcod_ativo()
        num = self.txt_tel_num.get().strip()
        if not num:
            messagebox.showwarning("Atenção", "Informe o número do telefone.", parent=self)
            self.txt_tel_num.focus_set()
            return

        dados_tel = {
            "ddi": self.txt_ddi.get().strip() or "55",
            "ddd": self.txt_ddd.get().strip(),
            "numero": num,
            "ramal": self.txt_tel_ramal.get().strip(),
            "tipotelefone": self.cbo_tel_tipo.get().strip(),
            "principal": "Sim" if self.var_tel_princ.get() else "Não"
        }

        if self._service and cod and cod != "NOVO":
            try:
                self._service.salvar_telefone(cod, dados_tel, base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro ao Salvar Telefone", f"Erro no banco: {exc}", parent=self)
                return

        item_existente = None
        for item in self.tree_telefones.get_children():
            vals = self.tree_telefones.item(item, "values")
            if vals and vals[3] == num:
                item_existente = item
                break

        val_tuple = (
            dados_tel["tipotelefone"],
            dados_tel["ddi"],
            dados_tel["ddd"],
            dados_tel["numero"],
            dados_tel["ramal"],
            dados_tel["principal"],
        )
        if item_existente:
            self.tree_telefones.item(item_existente, values=val_tuple)
        else:
            self.tree_telefones.insert("", tk.END, values=val_tuple)

        self.txt_tel_num.delete(0, tk.END)
        self.txt_tel_ramal.delete(0, tk.END)
        self.statusbar.config(text=f"Telefone '{num}' registrado com sucesso.")

    def _on_tel_select(self, event=None):
        sel = self.tree_telefones.selection()
        if sel:
            self._ultimo_tel_sel = sel

    def _remover_telefone(self, event=None):
        sel = self.tree_telefones.selection() or getattr(self, "_ultimo_tel_sel", ())
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um telefone na lista para remover.", parent=self)
            return "break"

        vals = self.tree_telefones.item(sel[0], "values")
        num = vals[3] if vals and len(vals) > 3 else ""
        if not num:
            return "break"

        if not messagebox.askyesno("Confirmação", f"Deseja realmente remover o telefone '{num}'?", parent=self):
            return "break"

        cod = self._obter_entcod_ativo()
        if self._service and cod and cod != "NOVO":
            try:
                self._service.remover_telefone(cod, num, base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro ao Remover Telefone", f"Erro no banco: {exc}", parent=self)
                return "break"

        idx = self.tree_telefones.index(sel[0]) if sel else 0
        self.tree_telefones.delete(sel[0])
        self._ultimo_tel_sel = ()
        restantes = self.tree_telefones.get_children()
        if restantes:
            novo_idx = min(idx, len(restantes) - 1)
            self.tree_telefones.selection_set(restantes[novo_idx])
            self.tree_telefones.focus(restantes[novo_idx])
            self.tree_telefones.see(restantes[novo_idx])
            self._ultimo_tel_sel = (restantes[novo_idx],)
        self.tree_telefones.focus_force()
        self.statusbar.config(text=f"Telefone '{num}' excluído.")
        return "break"

    def _on_tel_double_click(self, event=None):
        sel = self.tree_telefones.selection()
        if not sel:
            return
        vals = self.tree_telefones.item(sel[0], "values")
        if vals and len(vals) >= 6:
            self.cbo_tel_tipo.set(vals[0])
            self.txt_ddi.delete(0, tk.END)
            self.txt_ddi.insert(0, vals[1])
            self.txt_ddd.delete(0, tk.END)
            self.txt_ddd.insert(0, vals[2])
            self.txt_tel_num.delete(0, tk.END)
            self.txt_tel_num.insert(0, vals[3])
            self.txt_tel_ramal.delete(0, tk.END)
            self.txt_tel_ramal.insert(0, vals[4])
            self.var_tel_princ.set(vals[5].lower() in ("sim", "s", "true"))
            self.txt_tel_num.focus_set()

    def _adicionar_webcontato(self):
        cod = self._obter_entcod_ativo()
        email = self.txt_web_email.get().strip().lower()
        if not email:
            messagebox.showwarning("Atenção", "Informe o endereço de e-mail.", parent=self)
            self.txt_web_email.focus_set()
            return

        padrao_email = r"^[\w\.-]+@([\w-]+\.)+[a-zA-Z]{2,}$"
        if not re.match(padrao_email, email):
            messagebox.showwarning(
                "E-mail Inválido",
                f"O e-mail informado '{email}' não é válido.\nInforme um endereço no formato xxxx@xxxx.com ou xxxx@xxxx.com.br.",
                parent=self,
            )
            self.txt_web_email.focus_set()
            return

        dados_web = {
            "tipo_contato": self.cbo_web_tipo.get().strip(),
            "email": email,
            "website": self.txt_web_site.get().strip(),
            "comunicador_instantaneo": self.txt_web_comunicador.get().strip(),
            "principal": "Sim" if self.var_web_princ.get() else "Não"
        }

        if self._service and cod and cod != "NOVO":
            try:
                self._service.salvar_webcontato(cod, dados_web, base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro ao Salvar Contato Web", f"Erro no banco: {exc}", parent=self)
                return

        item_existente = None
        for item in self.tree_webcontatos.get_children():
            vals = self.tree_webcontatos.item(item, "values")
            if vals and vals[1].lower() == email.lower():
                item_existente = item
                break

        val_tuple = (
            dados_web["tipo_contato"],
            dados_web["email"],
            dados_web["website"],
            dados_web["comunicador_instantaneo"],
            dados_web["principal"],
        )
        if item_existente:
            self.tree_webcontatos.item(item_existente, values=val_tuple)
        else:
            self.tree_webcontatos.insert("", tk.END, values=val_tuple)

        self.txt_web_email.delete(0, tk.END)
        self.txt_web_site.delete(0, tk.END)
        self.txt_web_comunicador.delete(0, tk.END)
        self.statusbar.config(text=f"Contato web '{email}' salvo com sucesso.")

    def _on_web_select(self, event=None):
        sel = self.tree_webcontatos.selection()
        if sel:
            self._ultimo_web_sel = sel

    def _remover_webcontato(self, event=None):
        sel = self.tree_webcontatos.selection() or getattr(self, "_ultimo_web_sel", ())
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um contato web na lista para remover.", parent=self)
            return "break"

        vals = self.tree_webcontatos.item(sel[0], "values")
        email = vals[1] if vals and len(vals) > 1 else ""
        if not email:
            return "break"

        if not messagebox.askyesno("Confirmação", f"Deseja realmente remover o e-mail/contato '{email}'?", parent=self):
            return "break"

        cod = self._obter_entcod_ativo()
        if self._service and cod and cod != "NOVO":
            try:
                self._service.remover_webcontato(cod, email, base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro ao Remover Contato Web", f"Erro no banco: {exc}", parent=self)
                return "break"

        idx = self.tree_webcontatos.index(sel[0]) if sel else 0
        self.tree_webcontatos.delete(sel[0])
        self._ultimo_web_sel = ()
        restantes = self.tree_webcontatos.get_children()
        if restantes:
            novo_idx = min(idx, len(restantes) - 1)
            self.tree_webcontatos.selection_set(restantes[novo_idx])
            self.tree_webcontatos.focus(restantes[novo_idx])
            self.tree_webcontatos.see(restantes[novo_idx])
            self._ultimo_web_sel = (restantes[novo_idx],)
        self.tree_webcontatos.focus_force()
        self.statusbar.config(text=f"Contato web '{email}' excluído.")
        return "break"

    def _on_web_double_click(self, event=None):
        sel = self.tree_webcontatos.selection()
        if not sel:
            return
        vals = self.tree_webcontatos.item(sel[0], "values")
        if vals and len(vals) >= 5:
            self.cbo_web_tipo.set(vals[0])
            self.txt_web_email.delete(0, tk.END)
            self.txt_web_email.insert(0, vals[1])
            self.txt_web_site.delete(0, tk.END)
            self.txt_web_site.insert(0, vals[2])
            self.txt_web_comunicador.delete(0, tk.END)
            self.txt_web_comunicador.insert(0, vals[3])
            self.var_web_princ.set(vals[4].lower() in ("sim", "s", "true"))
            self.txt_web_email.focus_set()

    # -------------------------------------------------------------------------
    # Gerenciamento de Documentos
    # -------------------------------------------------------------------------
    def _carregar_documentos(self, r: Optional[Dict[str, Any]] = None):
        if not hasattr(self, "tree_documentos"):
            return
        for item in self.tree_documentos.get_children():
            self.tree_documentos.delete(item)

        cod = self._obter_entcod_ativo()
        docs = []
        if self._service and cod and cod != "NOVO":
            try:
                docs = self._service.listar_documentos(cod, base_dados=self.base_dados)
            except Exception as exc:
                logger.warning("Falha ao carregar documentos via serviço: %s", exc)

        if not docs and r:
            cpf_cnpj = r.get("EntCpfCgc") or r.get("entcpfcgc") or r.get("Documento")
            rg_ie = r.get("geoentrgie") or r.get("EntRgIe") or r.get("entrgie")
            if cpf_cnpj:
                docs.append({"tipo": "CPF/CNPJ", "documento": str(cpf_cnpj), "observacoes": "Principal"})
            if rg_ie:
                docs.append({"tipo": "RG/IE", "documento": str(rg_ie), "observacoes": ""})
            if "documentos" in r and isinstance(r["documentos"], list):
                docs.extend(r["documentos"])

        for d in docs:
            self.tree_documentos.insert(
                "",
                tk.END,
                values=(
                    d.get("tipo") or "OUTROS",
                    d.get("documento") or "",
                    d.get("observacoes") or "",
                )
            )

    def _adicionar_documento(self):
        cod = self._obter_entcod_ativo()
        tipo = self.cbo_doc_tipo.get().strip()
        doc = self.txt_doc_num.get().strip()
        obs = self.txt_doc_obs.get().strip()

        if not doc:
            messagebox.showwarning("Atenção", "Informe a numeração / identificação do documento.", parent=self)
            self.txt_doc_num.focus_set()
            return

        if self._service and cod and cod != "NOVO":
            try:
                self._service.salvar_documento(cod, tipo, doc, observacoes=obs, base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro ao Salvar Documento", f"Erro no banco: {exc}", parent=self)
                return

        item_existente = None
        for item in self.tree_documentos.get_children():
            vals = self.tree_documentos.item(item, "values")
            if vals and vals[0] == tipo and vals[1] == doc:
                item_existente = item
                break

        if item_existente:
            self.tree_documentos.item(item_existente, values=(tipo, doc, obs))
        else:
            self.tree_documentos.insert("", tk.END, values=(tipo, doc, obs))

        # Sincroniza com o campo correspondente na aba principal
        if "CPF" in tipo.upper() or "CNPJ" in tipo.upper():
            self.txt_cpf_cnpj.delete(0, tk.END)
            self.txt_cpf_cnpj.insert(0, doc)
        elif "RG" in tipo.upper() or "IE" in tipo.upper():
            self.txt_rg_ie.delete(0, tk.END)
            self.txt_rg_ie.insert(0, doc)

        self.txt_doc_num.delete(0, tk.END)
        self.txt_doc_obs.delete(0, tk.END)
        self.statusbar.config(text=f"Documento '{tipo} - {doc}' salvo com sucesso.")

    def _remover_documento(self):
        sel = self.tree_documentos.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um documento na lista para remover.", parent=self)
            return

        vals = self.tree_documentos.item(sel[0], "values")
        tipo = vals[0] if vals and len(vals) > 0 else ""
        doc = vals[1] if vals and len(vals) > 1 else ""
        if not doc:
            return

        if not messagebox.askyesno("Confirmação", f"Deseja realmente remover o documento '{tipo}: {doc}'?", parent=self):
            return

        cod = self._obter_entcod_ativo()
        if self._service and cod and cod != "NOVO":
            try:
                self._service.remover_documento(cod, tipo, doc, base_dados=self.base_dados)
            except Exception as exc:
                messagebox.showerror("Erro ao Remover Documento", f"Erro no banco: {exc}", parent=self)
                return

        idx = self.tree_documentos.index(sel[0]) if sel else 0
        self.tree_documentos.delete(sel[0])
        restantes = self.tree_documentos.get_children()
        if restantes:
            novo_idx = min(idx, len(restantes) - 1)
            self.tree_documentos.selection_set(restantes[novo_idx])
            self.tree_documentos.focus(restantes[novo_idx])
            self.tree_documentos.see(restantes[novo_idx])
        self.tree_documentos.focus_force()
        self.statusbar.config(text=f"Documento '{doc}' excluído.")

    def _on_doc_double_click(self, event=None):
        sel = self.tree_documentos.selection()
        if not sel:
            return
        vals = self.tree_documentos.item(sel[0], "values")
        if vals and len(vals) >= 2:
            self.cbo_doc_tipo.set(vals[0])
            self.txt_doc_num.delete(0, tk.END)
            self.txt_doc_num.insert(0, vals[1])
            self.txt_doc_obs.delete(0, tk.END)
            if len(vals) >= 3:
                self.txt_doc_obs.insert(0, vals[2])
            self.txt_doc_num.focus_set()

    # -------------------------------------------------------------------------
    # Extratores de Dados para Coleta e Persistência
    # -------------------------------------------------------------------------
    def _obter_categorias(self) -> List[Dict[str, str]]:
        itens = []
        if hasattr(self, "tree_categorias"):
            for item in self.tree_categorias.get_children():
                vals = self.tree_categorias.item(item, "values")
                if vals:
                    itens.append({"codigo": vals[0], "descricao": vals[1] if len(vals) > 1 else ""})
        return itens

    def _obter_telefones(self) -> List[Dict[str, str]]:
        itens = []
        if hasattr(self, "tree_telefones"):
            for item in self.tree_telefones.get_children():
                vals = self.tree_telefones.item(item, "values")
                if vals and len(vals) >= 6:
                    itens.append({
                        "tipo": vals[0],
                        "ddi": vals[1],
                        "ddd": vals[2],
                        "numero": vals[3],
                        "ramal": vals[4],
                        "principal": vals[5],
                    })
        return itens

    def _obter_webcontatos(self) -> List[Dict[str, str]]:
        itens = []
        if hasattr(self, "tree_webcontatos"):
            for item in self.tree_webcontatos.get_children():
                vals = self.tree_webcontatos.item(item, "values")
                if vals and len(vals) >= 5:
                    itens.append({
                        "tipo": vals[0],
                        "email": vals[1],
                        "website": vals[2],
                        "comunicador": vals[3],
                        "principal": vals[4],
                    })
        return itens

    def _obter_documentos(self) -> List[Dict[str, str]]:
        itens = []
        if hasattr(self, "tree_documentos"):
            for item in self.tree_documentos.get_children():
                vals = self.tree_documentos.item(item, "values")
                if vals and len(vals) >= 2:
                    itens.append({
                        "tipo": str(vals[0]),
                        "documento": str(vals[1]),
                        "observacoes": str(vals[2]) if len(vals) > 2 else "",
                    })

        # Sincroniza CPF/CNPJ e RG/IE das entradas da tela principal com a lista de documentos
        cpf_atual = self.txt_cpf_cnpj.get().strip() if hasattr(self, "txt_cpf_cnpj") else ""
        rg_atual = self.txt_rg_ie.get().strip() if hasattr(self, "txt_rg_ie") else ""

        if cpf_atual:
            idx_cpf = next((i for i, d in enumerate(itens) if "CPF" in str(d.get("tipo", "")).upper() or "CNPJ" in str(d.get("tipo", "")).upper()), None)
            if idx_cpf is not None:
                itens[idx_cpf]["documento"] = cpf_atual
            else:
                itens.append({"tipo": "CPF/CNPJ", "documento": cpf_atual, "observacoes": "Principal"})

        if rg_atual:
            idx_rg = next((i for i, d in enumerate(itens) if "RG" in str(d.get("tipo", "")).upper() or "IE" in str(d.get("tipo", "")).upper()), None)
            if idx_rg is not None:
                itens[idx_rg]["documento"] = rg_atual
            else:
                itens.append({"tipo": "RG/IE", "documento": rg_atual, "observacoes": ""})

        return itens

    def _coletar_dados(self) -> Dict[str, Any]:
        """Extrai todos os campos editáveis para um dicionário compatível com o Repositório."""
        trat_val = self.cbo_tipotrat.get().strip().split(" - ")[0].strip()
        esc_raw = self.cbo_escolaridade.get().strip()
        esc_val = esc_raw.split(" - ")[0].strip() if esc_raw else ""

        # Limpeza e sanitização da contribuição
        val_contrib_raw = self.txt_valorcontrib.get().strip()
        num_str = "".join(c for c in val_contrib_raw if c.isdigit() or c in ",.")
        if "," in num_str and "." in num_str:
            num_str = num_str.replace(".", "").replace(",", ".")
        elif "," in num_str:
            num_str = num_str.replace(",", ".")
        try:
            val_contrib_limpo = f"{float(num_str):.2f}" if num_str else "0.00"
        except Exception:
            val_contrib_limpo = "0.00"

        hist_val = self.txt_historico.get("1.0", tk.END).strip()

        dados = {
            # Códigos
            "geoentcod": self.txt_geoentcod.get().strip(),
            "entcod": self.txt_entcod.get().strip(),
            "geotipotratcod": trat_val,
            "tipotratcod": trat_val,
            # Nomes
            "geoentnome": self.txt_nome.get().strip().upper(),
            "entnome": self.txt_nome.get().strip().upper(),
            "geoentnomefantasia": self.txt_nomefantasia.get().strip().upper(),
            "entnomefant": self.txt_nomefantasia.get().strip().upper(),
            # Documentos & Pessoa
            "entcpfcgc": self.txt_cpf_cnpj.get().strip().upper(),
            "EntCpfCgc": self.txt_cpf_cnpj.get().strip().upper(),
            "Documento": self.txt_cpf_cnpj.get().strip().upper(),
            "entrgie": self.txt_rg_ie.get().strip().upper(),
            "EntRgIe": self.txt_rg_ie.get().strip().upper(),
            "geoentrgie": self.txt_rg_ie.get().strip().upper(),
            "geotipofj": self.cbo_tipofj.get().strip(),
            "enttipofj": self.cbo_tipofj.get().strip(),
            "geofalecido": "S" if self.cbo_falecido.get() == "Sim" else "N",
            "USERFalecido": self.cbo_falecido.get(),
            "geoentgenero": "M" if "MASC" in self.cbo_sexo.get() else ("F" if "FEM" in self.cbo_sexo.get() else "N"),
            "entgenero": "M" if "MASC" in self.cbo_sexo.get() else ("F" if "FEM" in self.cbo_sexo.get() else "N"),
            "geoentestcivil": self.cbo_estadocivil.get().upper(),
            "entestcivil": self.cbo_estadocivil.get().upper(),
            "geoentdataanivfund": converter_data_para_db(self.txt_dtnasc.get().strip()),
            "entdataanivfund": converter_data_para_db(self.txt_dtnasc.get().strip()),
            "geoentdatacad": converter_data_para_db(self.txt_dtcad.get().strip()),
            "entdatacad": converter_data_para_db(self.txt_dtcad.get().strip()),
            "codigo_grauescolaridade": esc_val,
            "entgrauescol": esc_val,
            "geocargocodestr": self.txt_cargo_cod.get().strip().upper(),
            "cargocodestr": self.txt_cargo_cod.get().strip().upper(),
            "geocargonome": self.txt_cargo_nome.get().strip().upper(),
            "cargonome": self.txt_cargo_nome.get().strip().upper(),
            # Endereço Principal
            "geoentcep": self.txt_cep.get().strip()[:10],
            "entcep": self.txt_cep.get().strip()[:10],
            "tipolograd": self.cbo_tipolograd.get().strip().upper(),
            "entlograd": self.cbo_tipolograd.get().strip().upper(),
            "tipologradabrev": self.cbo_tipolograd.get().strip().upper(),
            "geoentender": self.txt_ender.get().strip().upper(),
            "entender": self.txt_ender.get().strip().upper(),
            "geoenderno": self.txt_enderno.get().strip().upper(),
            "entenderno": self.txt_enderno.get().strip().upper(),
            "geoentendercomp": self.txt_endercomp.get().strip().upper(),
            "entendercomp": self.txt_endercomp.get().strip().upper(),
            "geoentbair": self.txt_bair.get().strip().upper(),
            "entbair": self.txt_bair.get().strip().upper(),
            "geocidcod": self.txt_cidcod.get().strip().upper(),
            "cidcod": self.txt_cidcod.get().strip().upper(),
            "cidcodapolo": self.txt_cidcod.get().strip().upper(),
            "cidnomecomp": self.txt_cidade.get().strip().upper(),
            "ufsigla": self.txt_uf.get().strip().upper(),
            "geoentcxapost": self.txt_cxapost.get().strip().upper(),
            "EntCxaPost": self.txt_cxapost.get().strip().upper(),
            "geolocalreferencia_ender": self.txt_referencia.get().strip().upper(),
            # Pessoais (com conversão para maiúsculo)
            "entnomepai": self.txt_nomepai.get().strip().upper(),
            "geoentnomepai": self.txt_nomepai.get().strip().upper(),
            "entnomemae": self.txt_nomemae.get().strip().upper(),
            "geoentnomemae": self.txt_nomemae.get().strip().upper(),
            "entmoracom": self.txt_residecom.get().strip().upper(),
            "geoentmoracom": self.txt_residecom.get().strip().upper(),
            "entpossuifilho": self.cbo_filhos.get(),
            "geoentpossuifilho": self.cbo_filhos.get(),
            "quantosfilhos": self.txt_quantosfilhos.get().strip(),
            "numerofilhos": self.txt_quantosfilhos.get().strip(),
            # Financeiro
            "tipocobcod": self.txt_tipocobcod.get().strip(),
            "geotipocobcod": self.txt_tipocobcod.get().strip(),
            "tipocobnome": self.txt_tipocobnome.get().strip(),
            "geotipocobnome": self.txt_tipocobnome.get().strip(),
            "USERGeraCarne": self.cbo_geracarne.get(),
            "geogeracarne": "S" if self.cbo_geracarne.get() == "Sim" else "N",
            "bconum": self.txt_bconum.get().strip(),
            "geobconum": self.txt_bconum.get().strip(),
            "bconome": self.txt_bconome.get().strip(),
            "agnum": self.txt_agnum.get().strip(),
            "geoagnum": self.txt_agnum.get().strip(),
            "EntBcoAgCCorNum": self.txt_cc.get().strip(),
            "geoentcontacorrente": self.txt_cc.get().strip(),
            "geoconta": self.txt_cc.get().strip(),
            "USERDia_Debito_CC": self.txt_diadebito.get().strip(),
            "geodia_contribuicao": self.txt_diadebito.get().strip(),
            "USERValor_Contribuicao": val_contrib_limpo,
            "geovalorcontribuicao": val_contrib_limpo,
            "geomoedacontribuicao": "USD" if "US$" in val_contrib_raw else "BRL",
            "USERDiocese_id": self.txt_dioceseid.get().strip(),
            "geodioceseid": self.txt_dioceseid.get().strip(),
            "USERNomeDiocese": self.txt_diocesenome.get().strip(),
            "USERRecebelembretedoacao": self.cbo_recebelembrete.get(),
            "georecebelembrete": "S" if self.cbo_recebelembrete.get() == "Sim" else "N",
            # Complementares
            "ativeconcodestr": self.txt_ativecon_cod.get().strip(),
            "geoativeconcodestr": self.txt_ativecon_cod.get().strip(),
            "ativeconnome": self.txt_ativecon_nome.get().strip(),
            "origcodestr": self.txt_origem_cod.get().strip(),
            "geo_origcodestr": self.txt_origem_cod.get().strip(),
            "orignome": self.txt_origem_nome.get().strip(),
            "regcodestr": self.txt_regiao_cod.get().strip(),
            "georegcodestr": self.txt_regiao_cod.get().strip(),
            "regnome": self.txt_regiao_nome.get().strip(),
            "entconceito": self.txt_conceito_cod.get().strip(),
            "geoentconceito": self.txt_conceito_cod.get().strip(),
            "end_cob_mesmo": self.var_end_cob_mesmo.get(),
            "end_ent_mesmo": self.var_end_ent_mesmo.get(),
            # Observações e Histórico
            "Entobservacoes": self.txt_observacoes.get("1.0", tk.END).strip()[:200],
            "geoobservacoes": self.txt_observacoes.get("1.0", tk.END).strip()[:200],
            "enthist": hist_val,
            "geoenthist": hist_val,
            "enttextohist": hist_val,
            # Grupo de Oração, Vigência de Mandato e Coordenador
            "chkgrupooracao": "S" if self.var_grupooracao.get() else "N",
            "geochkgrupooracao": "S" if self.var_grupooracao.get() else "N",
            "dtiniciovigencia": converter_data_para_db(self.txt_dtiniciovigencia.get().strip()),
            "geodtiniciovigencia": converter_data_para_db(self.txt_dtiniciovigencia.get().strip()),
            "dtfinalvigencia": converter_data_para_db(self.txt_dtfinalvigencia.get().strip()),
            "geodtfinalvigencia": converter_data_para_db(self.txt_dtfinalvigencia.get().strip()),
            "contatocod": self.txt_contato_cod.get().strip(),
            "geocontatocod": self.txt_contato_cod.get().strip(),
            "contatonome": self.lbl_contato_nome.get().strip(),
            "geocontatonome": self.lbl_contato_nome.get().strip(),
            "contatocargocod": self.txt_contato_cargo_cod.get().strip(),
            "geocontatocargocod": self.txt_contato_cargo_cod.get().strip(),
            "contatocargonome": self.lbl_contato_cargo_nome.get().strip(),
            "geocontatocargonome": self.lbl_contato_cargo_nome.get().strip(),
            "contatoprinc": self.cbo_contato_princ.get().strip(),
            "contatostatus": self.cbo_contato_status.get().strip(),
            "contatograudecisao": self.cbo_contato_graudecisao.get().strip(),
            # Categorias, Contatos e Documentos
            "categorias": self._obter_categorias(),
            "telefones": self._obter_telefones(),
            "webcontatos": self._obter_webcontatos(),
            "documentos": self._obter_documentos(),
        }

        # Endereço de cobrança se diferente do principal
        if self.var_end_cob_mesmo.get() == "Não":
            dados.update({
                "geocobcep": self.txt_cob_cep.get().strip()[:10],
                "cobcep": self.txt_cob_cep.get().strip()[:10],
                "geocoblograd": self.cbo_cob_tipolograd.get().strip(),
                "coblograd": self.cbo_cob_tipolograd.get().strip(),
                "geocobender": self.txt_cob_ender.get().strip(),
                "cobender": self.txt_cob_ender.get().strip(),
                "geocobenderno": self.txt_cob_enderno.get().strip(),
                "cobenderno": self.txt_cob_enderno.get().strip(),
                "geocobendercomp": self.txt_cob_endercomp.get().strip(),
                "cobendercomp": self.txt_cob_endercomp.get().strip(),
                "geocobbair": self.txt_cob_bair.get().strip(),
                "cobbair": self.txt_cob_bair.get().strip(),
                "geocobcidcod": self.txt_cob_cidcod.get().strip(),
                "cobcidcod": self.txt_cob_cidcod.get().strip(),
                "geocobcidade": self.txt_cob_cidade.get().strip(),
                "cobcidade": self.txt_cob_cidade.get().strip(),
                "geocobuf": self.txt_cob_uf.get().strip(),
                "cobuf": self.txt_cob_uf.get().strip(),
            })

        # Endereço de entrega se diferente do principal
        if self.var_end_ent_mesmo.get() == "Não":
            dados.update({
                "geoentregacep": self.txt_ent_cep.get().strip()[:10],
                "entregacep": self.txt_ent_cep.get().strip()[:10],
                "geoentregalograd": self.cbo_ent_tipolograd.get().strip(),
                "entregalograd": self.cbo_ent_tipolograd.get().strip(),
                "geoentregaender": self.txt_ent_ender.get().strip(),
                "entregaender": self.txt_ent_ender.get().strip(),
                "geoentregaenderno": self.txt_ent_enderno.get().strip(),
                "entregaenderno": self.txt_ent_enderno.get().strip(),
                "geoentregaendercomp": self.txt_ent_endercomp.get().strip(),
                "entregaendercomp": self.txt_ent_endercomp.get().strip(),
                "geoentregabair": self.txt_ent_bair.get().strip(),
                "entregabair": self.txt_ent_bair.get().strip(),
                "geoentregacidcod": self.txt_ent_cidcod.get().strip(),
                "entregacidcod": self.txt_ent_cidcod.get().strip(),
                "geoentregacidade": self.txt_ent_cidade.get().strip(),
                "entregacidade": self.txt_ent_cidade.get().strip(),
                "geoentregauf": self.txt_ent_uf.get().strip(),
                "entregauf": self.txt_ent_uf.get().strip(),
            })

        return dados


    def salvar(self, event=None):
        """Valida e persiste as alterações realizadas na entidade."""
        dados = self._coletar_dados()

        # Validação essencial
        nome = dados.get("entnome") or dados.get("geoentnome")
        if not nome:
            messagebox.showwarning("Atenção", "O campo 'Nome / Razão Social' é de preenchimento obrigatório.", parent=self)
            self.notebook.select(self.tab_principal)
            self.txt_nome.focus_set()
            return

        try:
            modo_inc = getattr(self, "modo_inclusao", False) or not bool(self.registro.get("geoentcod"))
            if self._service:
                res = self._service.salvar_entidade(dados, base_dados=self.base_dados, modo_inclusao=modo_inc)
                if not res.sucesso:
                    messagebox.showerror("Erro ao Salvar", res.mensagem, parent=self)
                    return
            elif self._repo:
                if self.base_dados == "GeoApolo":
                    self._repo.gravar_entidade_geoapolo(dados, modo_inclusao=modo_inc)
                else:
                    self._repo.gravar_entidade_alvo(dados)
            else:
                messagebox.showerror("Erro", "Conexão com o banco de dados não disponível para gravação.", parent=self)
                return

            messagebox.showinfo("Sucesso", f"Entidade '{nome}' gravada com sucesso!", parent=self)
            self.statusbar.config(text=f"Entidade '{nome}' atualizada com sucesso às {self._hora_atual()}.")

            # Notifica tela pai para recarregar lista
            if self.on_salvar:
                self.on_salvar()

            self.destroy()
        except Exception as exc:
            logger.exception("Erro ao salvar entidade no formulário: %s", exc)
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar a entidade:\n{exc}", parent=self)

    def atualizar_codigo_alvo(self, novo_entcod: str):
        """Atualiza dinamicamente o código do Alvo nos campos de tela e no título."""
        if not novo_entcod:
            return
        novo_entcod = str(novo_entcod).strip()
        self.registro["entcod"] = novo_entcod
        if hasattr(self, "txt_entcod") and self.txt_entcod.winfo_exists():
            orig_state = str(self.txt_entcod.cget("state"))
            if orig_state == "readonly":
                self.txt_entcod.config(state="normal")
            self.txt_entcod.delete(0, tk.END)
            self.txt_entcod.insert(0, novo_entcod)
            if orig_state == "readonly":
                self.txt_entcod.config(state="readonly")

        cod_geo = str(self.registro.get("geoentcod") or "—").strip()
        nome = self.registro.get("geoentnome") or self.registro.get("entnome") or ""
        if hasattr(self, "lbl_tit") and self.lbl_tit.winfo_exists():
            self.lbl_tit.config(text=f"📋 Manutenção de Entidade: [Geo: {cod_geo} | Alvo: {novo_entcod}] {nome}")
        if hasattr(self, "statusbar") and self.statusbar.winfo_exists():
            self.statusbar.config(text=f"Código do Alvo vinculado com sucesso: {novo_entcod} às {self._hora_atual()}.")
        try:
            self._carregar_doacoes()
        except Exception:
            pass

    def atualizar_documento(self, novo_doc: str):
        """Atualiza dinamicamente o CPF/CNPJ nos campos de tela."""
        if not novo_doc:
            return
        novo_doc = str(novo_doc).strip()
        self.registro["entcpfcgc"] = novo_doc
        self.registro["EntCpfCgc"] = novo_doc
        self.registro["Documento"] = novo_doc
        if hasattr(self, "txt_cpf_cnpj") and self.txt_cpf_cnpj.winfo_exists():
            orig_state = str(self.txt_cpf_cnpj.cget("state"))
            if orig_state == "readonly":
                self.txt_cpf_cnpj.config(state="normal")
            self.txt_cpf_cnpj.delete(0, tk.END)
            self.txt_cpf_cnpj.insert(0, novo_doc)
            if orig_state == "readonly":
                self.txt_cpf_cnpj.config(state="readonly")
        if hasattr(self, "_carregar_documentos"):
            try:
                self._carregar_documentos()
            except Exception:
                pass

    def destroy(self):
        """Garante a liberação de foco modal e limpeza de instância única."""
        try:
            self.grab_release()
        except Exception:
            pass
        FrmCadEntidade._instancia_ativa = None
        super().destroy()

    def _hora_atual(self) -> str:
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")


# Alias para compatibilidade
CadEntidadeView = FrmCadEntidade
