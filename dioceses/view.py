"""
Interface Gráfica Corporativa para Vínculo de Entidades com Dioceses da CNBB.
GeoApolo V5
"""

import logging
from datetime import date, datetime
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List

from .models import (
    EntidadeDioceseDTO,
    DioceseCNBBDTO,
    FiltroVinculoDioceseDTO,
    ResultadoOperacaoDiocese,
)
from .repository import DiocesesRepository
from .service import DiocesesService

logger = logging.getLogger(__name__)


class RelacionaDioceseEntidadeView:
    """Janela corporativa para vincular colaboradores/entidades às Dioceses CNBB."""

    def __init__(self, parent: Optional[tk.Tk] = None, service: Optional[DiocesesService] = None):
        self.parent = parent
        self.service = service or DiocesesService(DiocesesRepository())

        if parent is not None:
            self.window = tk.Toplevel(parent)
            self.window.title("GeoAlvo - Relacionamento de Entidades RCC x Dioceses CNBB")
            self.window.geometry("1100x720")
            self.window.minsize(980, 620)
            self.window.transient(parent)
            self.window.grab_set()
        else:
            self.window = None

        self._entidades_atuais: List[EntidadeDioceseDTO] = []
        self._entidade_selecionada: Optional[EntidadeDioceseDTO] = None

        if self.window is not None:
            self._setup_ui()
            self._pesquisar_entidades()

    def _setup_ui(self):
        # Header corporativo
        header = tk.Frame(self.window, bg="#1A365D", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        lbl_titulo = tk.Label(
            header,
            text="Relacionamento de Entidades RCC com Dioceses da CNBB",
            font=("Segoe UI", 13, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
        )
        lbl_titulo.pack(side=tk.LEFT, padx=15, pady=12)

        # Container Principal
        container = ttk.Frame(self.window, padding="12")
        container.pack(fill=tk.BOTH, expand=True)

        # 1. Painel de Filtros
        filtro_frame = ttk.LabelFrame(container, text=" Filtros de Pesquisa ", padding="10")
        filtro_frame.pack(fill=tk.X, pady=(0, 10))

        # Linha 1 de filtros: Datas e Checkbox
        hoje = date.today()
        primeiro_dia_ano = date(hoje.year, 1, 1)

        ttk.Label(filtro_frame, text="Data Inicial:").grid(row=0, column=0, padx=5, sticky="w")
        self.txt_dt_inicial = ttk.Entry(filtro_frame, width=12)
        self.txt_dt_inicial.insert(0, primeiro_dia_ano.strftime("%d/%m/%Y"))
        self.txt_dt_inicial.grid(row=0, column=1, padx=5, sticky="w")

        ttk.Label(filtro_frame, text="Data Final:").grid(row=0, column=2, padx=5, sticky="w")
        self.txt_dt_final = ttk.Entry(filtro_frame, width=12)
        self.txt_dt_final.insert(0, hoje.strftime("%d/%m/%Y"))
        self.txt_dt_final.grid(row=0, column=3, padx=5, sticky="w")

        self.var_apenas_sem_diocese = tk.BooleanVar(value=True)
        chk_sem_diocese = ttk.Checkbutton(
            filtro_frame,
            text="Apenas entidades sem Diocese vinculada",
            variable=self.var_apenas_sem_diocese,
            command=self._pesquisar_entidades,
        )
        chk_sem_diocese.grid(row=0, column=4, padx=15, sticky="w")

        # Linha 2 de filtros: Termo de busca e botões
        ttk.Label(filtro_frame, text="Filtrar Nome/Código:").grid(row=1, column=0, padx=5, pady=(8, 0), sticky="w")
        self.txt_termo = ttk.Entry(filtro_frame, width=28)
        self.txt_termo.grid(row=1, column=1, columnspan=2, padx=5, pady=(8, 0), sticky="w")
        self.txt_termo.bind("<Return>", lambda e: self._pesquisar_entidades())

        btn_pesquisar = ttk.Button(
            filtro_frame,
            text="🔍 Pesquisar",
            command=self._pesquisar_entidades,
        )
        btn_pesquisar.grid(row=1, column=3, padx=5, pady=(8, 0), sticky="w")

        btn_limpar = ttk.Button(
            filtro_frame,
            text="🧹 Limpar",
            command=self._limpar_campos,
        )
        btn_limpar.grid(row=1, column=4, padx=5, pady=(8, 0), sticky="w")

        # 2. Tabela de Entidades
        grid_frame = ttk.LabelFrame(container, text=" Entidades Encontradas ", padding="6")
        grid_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        colunas = ("entcod", "entnome", "cidnomecomp", "ufsigla", "diocese", "sve")
        self.grid_entidades = ttk.Treeview(
            grid_frame,
            columns=colunas,
            show="headings",
            selectmode="browse",
            height=12,
        )

        self.grid_entidades.heading("entcod", text="Código")
        self.grid_entidades.heading("entnome", text="Nome da Entidade / Colaborador")
        self.grid_entidades.heading("cidnomecomp", text="Cidade")
        self.grid_entidades.heading("ufsigla", text="UF")
        self.grid_entidades.heading("diocese", text="Diocese CNBB Vinculada")
        self.grid_entidades.heading("sve", text="Plataforma SVE")

        self.grid_entidades.column("entcod", width=80, anchor="center")
        self.grid_entidades.column("entnome", width=280, anchor="w")
        self.grid_entidades.column("cidnomecomp", width=160, anchor="w")
        self.grid_entidades.column("ufsigla", width=50, anchor="center")
        self.grid_entidades.column("diocese", width=220, anchor="w")
        self.grid_entidades.column("sve", width=140, anchor="center")

        scroll_y = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.grid_entidades.yview)
        scroll_x = ttk.Scrollbar(grid_frame, orient=tk.HORIZONTAL, command=self.grid_entidades.xview)
        self.grid_entidades.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.grid_entidades.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        grid_frame.rowconfigure(0, weight=1)
        grid_frame.columnconfigure(0, weight=1)

        self.grid_entidades.bind("<<TreeviewSelect>>", self._on_selecionar_entidade)
        self.grid_entidades.bind("<Double-1>", self._on_duplo_clique_entidade)

        # 3. Painel de Vínculo com Diocese
        vinculo_frame = ttk.LabelFrame(container, text=" Vínculo com Diocese da CNBB ", padding="10")
        vinculo_frame.pack(fill=tk.X, pady=(0, 5))

        # Subpainel: Detalhes da Entidade Selecionada
        lbl_ent_header = ttk.Label(vinculo_frame, text="Entidade Selecionada:", font=("Segoe UI", 9, "bold"))
        lbl_ent_header.grid(row=0, column=0, padx=5, sticky="w")

        self.lbl_ent_info = ttk.Label(vinculo_frame, text="Nenhuma entidade selecionada na lista acima.", foreground="#2B6CB0")
        self.lbl_ent_info.grid(row=0, column=1, columnspan=4, padx=5, sticky="w")

        self.lbl_sve_badge = ttk.Label(vinculo_frame, text="", font=("Segoe UI", 9, "bold"))
        self.lbl_sve_badge.grid(row=0, column=5, padx=10, sticky="e")

        # Subpainel: Diocese
        ttk.Separator(vinculo_frame, orient="horizontal").grid(row=1, column=0, columnspan=6, sticky="ew", pady=8)

        ttk.Label(vinculo_frame, text="ID Diocese:").grid(row=2, column=0, padx=5, sticky="w")
        self.txt_dio_id = ttk.Entry(vinculo_frame, width=10)
        self.txt_dio_id.grid(row=2, column=1, padx=5, sticky="w")
        self.txt_dio_id.bind("<Return>", lambda e: self._buscar_diocese_por_id_digitado())

        ttk.Label(vinculo_frame, text="Nome Diocese:").grid(row=2, column=2, padx=5, sticky="w")
        self.txt_dio_nome = ttk.Entry(vinculo_frame, width=32)
        self.txt_dio_nome.grid(row=2, column=3, padx=5, sticky="w")

        btn_buscar_dio = ttk.Button(
            vinculo_frame,
            text="🔎 Buscar CNBB...",
            command=self._abrir_modal_busca_dioceses,
        )
        btn_buscar_dio.grid(row=2, column=4, padx=5, sticky="w")

        btn_sugerir_dio = ttk.Button(
            vinculo_frame,
            text="✨ Sugerir p/ Cidade",
            command=self._sugerir_diocese_cidade,
        )
        btn_sugerir_dio.grid(row=2, column=5, padx=5, sticky="w")

        # Linha de botões de Ação de Vínculo
        btn_box = ttk.Frame(vinculo_frame, padding=(0, 10, 0, 0))
        btn_box.grid(row=3, column=0, columnspan=6, sticky="e")

        self.btn_desvincular = ttk.Button(
            btn_box,
            text="❌ Remover Vínculo",
            command=self._remover_vinculo,
            state="disabled",
        )
        self.btn_desvincular.pack(side=tk.RIGHT, padx=5)

        self.btn_salvar_vinculo = ttk.Button(
            btn_box,
            text="💾 Salvar Vínculo",
            command=self._salvar_vinculo,
            state="disabled",
        )
        self.btn_salvar_vinculo.pack(side=tk.RIGHT, padx=5)

        # 4. Barra de Status Inferior
        status_bar = tk.Frame(self.window, bd=1, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_status = tk.Label(status_bar, text="Pronto.", anchor=tk.W, font=("Segoe UI", 9))
        self.lbl_status.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=3)

        self.lbl_contadores = tk.Label(status_bar, text="Total: 0 | Sem Diocese: 0", font=("Segoe UI", 9, "bold"))
        self.lbl_contadores.pack(side=tk.RIGHT, padx=12, pady=3)

    def _parse_data(self, texto: str) -> Optional[date]:
        """Converte texto DD/MM/AAAA em date."""
        if not texto or not texto.strip():
            return None
        try:
            return datetime.strptime(texto.strip(), "%d/%m/%Y").date()
        except ValueError:
            return None

    def _pesquisar_entidades(self):
        """Consulta as entidades conforme os filtros preenchidos."""
        dt_ini = self._parse_data(self.txt_dt_inicial.get())
        dt_fim = self._parse_data(self.txt_dt_final.get())

        if dt_ini and dt_fim and dt_ini > dt_fim:
            messagebox.showerror("Período Inválido", "A Data Inicial não pode ser maior que a Data Final.")
            return

        filtro = FiltroVinculoDioceseDTO(
            data_inicial=dt_ini,
            data_final=dt_fim,
            apenas_sem_diocese=self.var_apenas_sem_diocese.get(),
            termo_busca=self.txt_termo.get().strip() or None,
        )

        try:
            self._entidades_atuais = self.service.listar_entidades(filtro)
            self._popular_grid_entidades(self._entidades_atuais)
            total = len(self._entidades_atuais)
            sem_dio = sum(1 for e in self._entidades_atuais if not e.tem_diocese)
            self.lbl_contadores.config(text=f"Total: {total} | Sem Diocese: {sem_dio}")
            self.lbl_status.config(text=f"Consulta concluída com sucesso. {total} entidades retornadas.")
        except Exception as e:
            logger.exception("Erro ao pesquisar entidades")
            messagebox.showerror("Erro", f"Erro ao realizar consulta de entidades:\n{e}")

    def _popular_grid_entidades(self, lista: List[EntidadeDioceseDTO]):
        """Carrega a Treeview com a lista de entidades."""
        for item in self.grid_entidades.get_children():
            self.grid_entidades.delete(item)

        for ent in lista:
            dio_desc = ent.user_nome_diocese if ent.tem_diocese else "(Sem Diocese)"
            sve_desc = ent.status_sve_formatado
            self.grid_entidades.insert(
                "",
                tk.END,
                iid=ent.entcod,
                values=(
                    ent.entcod,
                    ent.entnome,
                    ent.cidnomecomp,
                    ent.ufsigla,
                    dio_desc,
                    sve_desc,
                ),
            )

    def _on_selecionar_entidade(self, event=None):
        """Ação disparada ao selecionar uma linha na tabela."""
        sel = self.grid_entidades.selection()
        if not sel:
            return

        entcod = sel[0]
        self._entidade_selecionada = next((e for e in self._entidades_atuais if e.entcod == entcod), None)
        if not self._entidade_selecionada:
            return

        ent = self._entidade_selecionada
        self.lbl_ent_info.config(
            text=f"[{ent.entcod}] {ent.entnome}  •  {ent.cidnomecomp}/{ent.ufsigla}"
        )

        # Badge SVE
        if ent.user_jana_sve == "S":
            self.lbl_sve_badge.config(text="✓ PLATAFORMA SVE", foreground="#22543D")
        elif ent.user_jana_sve == "N":
            self.lbl_sve_badge.config(text="✗ NÃO INCLUÍDA NA SVE", foreground="#742A2A")
        else:
            self.lbl_sve_badge.config(text="", foreground="#000000")

        self.txt_dio_id.delete(0, tk.END)
        self.txt_dio_nome.delete(0, tk.END)

        if ent.tem_diocese:
            self.txt_dio_id.insert(0, str(ent.user_diocese_id or ""))
            self.txt_dio_nome.insert(0, str(ent.user_nome_diocese or ""))
            self.btn_desvincular.config(state="normal")
        else:
            self.btn_desvincular.config(state="disabled")

        self.btn_salvar_vinculo.config(state="normal")

    def _on_duplo_clique_entidade(self, event=None):
        """No duplo clique, se não tiver diocese, já tenta sugerir automaticamente."""
        self._on_selecionar_entidade()
        if self._entidade_selecionada and not self._entidade_selecionada.tem_diocese:
            self._sugerir_diocese_cidade()

    def _sugerir_diocese_cidade(self):
        """Busca automaticamente a diocese referente à cidade da entidade selecionada."""
        if not self._entidade_selecionada:
            messagebox.showwarning("Atenção", "Selecione uma entidade primeiro.")
            return

        cidade = self._entidade_selecionada.cidnomecomp
        uf = self._entidade_selecionada.ufsigla

        diocese = self.service.sugerir_diocese(cidade=cidade, uf=uf)
        if diocese:
            self.txt_dio_id.delete(0, tk.END)
            self.txt_dio_id.insert(0, diocese.id)
            self.txt_dio_nome.delete(0, tk.END)
            self.txt_dio_nome.insert(0, diocese.nome)
            self.lbl_status.config(text=f"Diocese '{diocese.nome}' sugerida para o município de {cidade}/{uf}.")
        else:
            messagebox.showinfo("Sugestão Automática", f"Nenhuma Diocese correspondente encontrada para '{cidade}/{uf}'.\nUtilize a busca manual.")

    def _buscar_diocese_por_id_digitado(self):
        """Busca detalhes da diocese quando o usuário pressiona Enter no ID."""
        dio_id = self.txt_dio_id.get().strip()
        if not dio_id:
            return

        dioceses = self.service.listar_dioceses(termo=dio_id)
        match = next((d for d in dioceses if d.id == dio_id), None)
        if match:
            self.txt_dio_nome.delete(0, tk.END)
            self.txt_dio_nome.insert(0, match.nome)
        else:
            self.lbl_status.config(text=f"Diocese com ID '{dio_id}' não localizada.")

    def _abrir_modal_busca_dioceses(self):
        """Abre janela de diálogo para pesquisar e selecionar Dioceses CNBB."""
        modal = tk.Toplevel(self.window)
        modal.title("Pesquisa de Dioceses da CNBB")
        modal.geometry("640x480")
        modal.transient(self.window)
        modal.grab_set()

        filtro_modal = ttk.Frame(modal, padding="10")
        filtro_modal.pack(fill=tk.X)

        ttk.Label(filtro_modal, text="Nome ou Município:").grid(row=0, column=0, padx=5, sticky="w")
        txt_busca = ttk.Entry(filtro_modal, width=25)
        txt_busca.grid(row=0, column=1, padx=5, sticky="w")

        ttk.Label(filtro_modal, text="UF:").grid(row=0, column=2, padx=5, sticky="w")
        txt_uf = ttk.Entry(filtro_modal, width=5)
        if self._entidade_selecionada and self._entidade_selecionada.ufsigla:
            txt_uf.insert(0, self._entidade_selecionada.ufsigla)
        txt_uf.grid(row=0, column=3, padx=5, sticky="w")

        grid_modal_frame = ttk.Frame(modal, padding="10")
        grid_modal_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "nome", "cidade", "uf")
        grid_dio = ttk.Treeview(grid_modal_frame, columns=cols, show="headings", selectmode="browse")
        grid_dio.heading("id", text="ID")
        grid_dio.heading("nome", text="Diocese")
        grid_dio.heading("cidade", text="Sede/Cidade")
        grid_dio.heading("uf", text="UF")

        grid_dio.column("id", width=60, anchor="center")
        grid_dio.column("nome", width=260, anchor="w")
        grid_dio.column("cidade", width=180, anchor="w")
        grid_dio.column("uf", width=50, anchor="center")

        scr = ttk.Scrollbar(grid_modal_frame, orient=tk.VERTICAL, command=grid_dio.yview)
        grid_dio.configure(yscrollcommand=scr.set)
        grid_dio.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scr.pack(side=tk.RIGHT, fill=tk.Y)

        def carregar_dioceses():
            for it in grid_dio.get_children():
                grid_dio.delete(it)
            termo = txt_busca.get().strip() or None
            uf_val = txt_uf.get().strip().upper() or None
            resultados = self.service.listar_dioceses(uf=uf_val, termo=termo)
            for d in resultados:
                grid_dio.insert("", tk.END, iid=d.id, values=(d.id, d.nome, d.cidade, d.ufsigla))

        btn_buscar = ttk.Button(filtro_modal, text="Filtrar", command=carregar_dioceses)
        btn_buscar.grid(row=0, column=4, padx=5, sticky="w")
        txt_busca.bind("<Return>", lambda e: carregar_dioceses())

        def confirmar_selecao():
            sel = grid_dio.selection()
            if not sel:
                return
            dio_id = sel[0]
            item = grid_dio.item(dio_id)
            vals = item["values"]
            self.txt_dio_id.delete(0, tk.END)
            self.txt_dio_id.insert(0, str(vals[0]))
            self.txt_dio_nome.delete(0, tk.END)
            self.txt_dio_nome.insert(0, str(vals[1]))
            modal.destroy()

        grid_dio.bind("<Double-1>", lambda e: confirmar_selecao())

        btn_sel = ttk.Button(modal, text="✓ Selecionar Diocese", command=confirmar_selecao)
        btn_sel.pack(side=tk.RIGHT, padx=15, pady=10)

        carregar_dioceses()

    def _salvar_vinculo(self):
        """Executa a vinculação da entidade com a diocese informada."""
        if not self._entidade_selecionada:
            messagebox.showwarning("Atenção", "Selecione uma entidade primeiro.")
            return

        entcod = self._entidade_selecionada.entcod
        dio_id = self.txt_dio_id.get().strip()
        dio_nome = self.txt_dio_nome.get().strip()

        if not dio_id:
            messagebox.showwarning("Atenção", "Informe ou selecione uma Diocese da CNBB antes de salvar.")
            return

        msg_confirma = (
            f"Deseja confirmar o vínculo da entidade:\n\n"
            f"[{entcod}] {self._entidade_selecionada.entnome}\n"
            f"com a Diocese:\n"
            f"[{dio_id}] {dio_nome}?"
        )
        if not messagebox.askyesno("Confirmar Vínculo", msg_confirma):
            return

        resultado: ResultadoOperacaoDiocese = self.service.vincular(
            entcod=entcod,
            diocese_id=dio_id,
            nome_diocese=dio_nome,
        )

        if resultado.sucesso:
            messagebox.showinfo("Sucesso", resultado.mensagem)
            self._pesquisar_entidades()
            # Tenta reselecionar
            if entcod in self.grid_entidades.get_children():
                self.grid_entidades.selection_set(entcod)
                self.grid_entidades.focus(entcod)
        else:
            messagebox.showerror("Falha", resultado.mensagem)

    def _remover_vinculo(self):
        """Remove o vínculo de diocese da entidade."""
        if not self._entidade_selecionada:
            return

        entcod = self._entidade_selecionada.entcod
        if not messagebox.askyesno(
            "Desvincular Diocese",
            f"Tem certeza que deseja remover o vínculo da diocese para a entidade [{entcod}] {self._entidade_selecionada.entnome}?"
        ):
            return

        resultado = self.service.desvincular(entcod=entcod)
        if resultado.sucesso:
            messagebox.showinfo("Sucesso", resultado.mensagem)
            self._pesquisar_entidades()
        else:
            messagebox.showerror("Falha", resultado.mensagem)

    def _limpar_campos(self):
        """Limpa campos de filtro e seleção."""
        hoje = date.today()
        primeiro_dia_ano = date(hoje.year, 1, 1)
        self.txt_dt_inicial.delete(0, tk.END)
        self.txt_dt_inicial.insert(0, primeiro_dia_ano.strftime("%d/%m/%Y"))
        self.txt_dt_final.delete(0, tk.END)
        self.txt_dt_final.insert(0, hoje.strftime("%d/%m/%Y"))
        self.txt_termo.delete(0, tk.END)
        self.var_apenas_sem_diocese.set(True)
        self.txt_dio_id.delete(0, tk.END)
        self.txt_dio_nome.delete(0, tk.END)
        self.lbl_ent_info.config(text="Nenhuma entidade selecionada na lista acima.")
        self.lbl_sve_badge.config(text="")
        self.btn_salvar_vinculo.config(state="disabled")
        self.btn_desvincular.config(state="disabled")
        self._entidade_selecionada = None
        self._pesquisar_entidades()
