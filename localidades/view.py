"""
Interface Gráfica para Correção de Distritos Cadastrados como Cidades.
GeoApolo V5
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from .models import CidadeDistritoDTO, EntidadeLocalidadeDTO
from .repository import LocalidadesRepository
from .service import LocalidadesService


class CorrecaoCidadesDistritosView:
    """Janela corporativa para saneamento geográfico e unificação de distritos em cidades mães."""

    def __init__(self, parent: tk.Tk, service: Optional[LocalidadesService] = None):
        self.parent = parent
        self.service = service or LocalidadesService(LocalidadesRepository())

        self.window = tk.Toplevel(parent)
        self.window.title("GeoAlvo - Correção de Distritos Cadastrados como Cidades")
        self.window.geometry("1040x680")
        self.window.minsize(900, 580)
        self.window.transient(parent)
        self.window.grab_set()

        self._cidades_atuais: List[CidadeDistritoDTO] = []
        self._setup_ui()
        self._buscar_cidades()

    def _setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg="#1A365D", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        lbl_titulo = tk.Label(
            header,
            text="Saneamento de Localidades - Correção de Distritos x Cidades Mães",
            font=("Segoe UI", 13, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
        )
        lbl_titulo.pack(side=tk.LEFT, padx=15, pady=12)

        # Container Principal
        container = ttk.Frame(self.window, padding="15")
        container.pack(fill=tk.BOTH, expand=True)

        # Filtros
        filtro_frame = ttk.LabelFrame(container, text=" Pesquisa de Localidades ", padding="10")
        filtro_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filtro_frame, text="Nome da Cidade/Distrito:").grid(row=0, column=0, padx=5, sticky="w")
        self.txt_busca = ttk.Entry(filtro_frame, width=30)
        self.txt_busca.grid(row=0, column=1, padx=5, sticky="w")
        self.txt_busca.bind("<Return>", lambda e: self._buscar_cidades())

        ttk.Label(filtro_frame, text="UF:").grid(row=0, column=2, padx=5, sticky="w")
        self.txt_uf = ttk.Entry(filtro_frame, width=6)
        self.txt_uf.grid(row=0, column=3, padx=5, sticky="w")

        btn_buscar = ttk.Button(filtro_frame, text="🔍 Buscar", command=self._buscar_cidades)
        btn_buscar.grid(row=0, column=4, padx=8, sticky="w")

        # PanedWindow para dividir Grid de Cidades e Grid de Entidades
        paned = ttk.PanedWindow(container, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Grid Superior: Cidades / Distritos
        grid_cid_frame = ttk.LabelFrame(paned, text=" Cidades e Distritos Cadastrados ", padding="5")
        paned.add(grid_cid_frame, weight=2)

        colunas_cid = ("codigo", "nome", "uf", "ibge", "total_ent")
        self.tree_cid = ttk.Treeview(grid_cid_frame, columns=colunas_cid, show="headings", selectmode="browse")

        self.tree_cid.heading("codigo", text="Código")
        self.tree_cid.heading("nome", text="Nome da Localidade")
        self.tree_cid.heading("uf", text="UF")
        self.tree_cid.heading("ibge", text="Cód. IBGE")
        self.tree_cid.heading("total_ent", text="Entidades Vinculadas")

        self.tree_cid.column("codigo", width=100, anchor="center")
        self.tree_cid.column("nome", width=320, anchor="w")
        self.tree_cid.column("uf", width=60, anchor="center")
        self.tree_cid.column("ibge", width=110, anchor="center")
        self.tree_cid.column("total_ent", width=140, anchor="center")

        scroll_cid = ttk.Scrollbar(grid_cid_frame, orient=tk.VERTICAL, command=self.tree_cid.yview)
        self.tree_cid.configure(yscrollcommand=scroll_cid.set)

        self.tree_cid.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_cid.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_cid.bind("<<TreeviewSelect>>", self._ao_selecionar_cidade)

        # Grid Inferior: Entidades Vinculadas
        grid_ent_frame = ttk.LabelFrame(paned, text=" Entidades Vinculadas à Localidade Selecionada ", padding="5")
        paned.add(grid_ent_frame, weight=2)

        colunas_ent = ("cod", "nome", "doc", "cep", "endereco", "bairro")
        self.tree_ent = ttk.Treeview(grid_ent_frame, columns=colunas_ent, show="headings")

        self.tree_ent.heading("cod", text="Código")
        self.tree_ent.heading("nome", text="Razão Social / Nome")
        self.tree_ent.heading("doc", text="CPF / CNPJ")
        self.tree_ent.heading("cep", text="CEP")
        self.tree_ent.heading("endereco", text="Endereço")
        self.tree_ent.heading("bairro", text="Bairro")

        self.tree_ent.column("cod", width=85, anchor="center")
        self.tree_ent.column("nome", width=250, anchor="w")
        self.tree_ent.column("doc", width=120, anchor="center")
        self.tree_ent.column("cep", width=90, anchor="center")
        self.tree_ent.column("endereco", width=220, anchor="w")
        self.tree_ent.column("bairro", width=140, anchor="w")

        scroll_ent = ttk.Scrollbar(grid_ent_frame, orient=tk.VERTICAL, command=self.tree_ent.yview)
        self.tree_ent.configure(yscrollcommand=scroll_ent.set)

        self.tree_ent.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_ent.pack(side=tk.RIGHT, fill=tk.Y)

        # Painel Inferior de Correção e Migração
        acao_frame = ttk.LabelFrame(container, text=" Painel de Correção / Reatribuição de Distrito ", padding="10")
        acao_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(acao_frame, text="Distrito Selecionado:").grid(row=0, column=0, padx=5, sticky="w")
        self.lbl_distrito_sel = ttk.Label(acao_frame, text="-", font=("Segoe UI", 9, "bold"))
        self.lbl_distrito_sel.grid(row=0, column=1, padx=5, sticky="w")

        ttk.Label(acao_frame, text="Código Cidade Mãe (Destino):").grid(row=0, column=2, padx=(20, 5), sticky="w")
        self.txt_cid_destino = ttk.Entry(acao_frame, width=12)
        self.txt_cid_destino.grid(row=0, column=3, padx=5, sticky="w")

        btn_consultar_viacep = ttk.Button(acao_frame, text="🌐 Consultar ViaCEP", command=self._consultar_viacep_entidade)
        btn_consultar_viacep.grid(row=0, column=4, padx=8, sticky="w")

        self.btn_migrar = tk.Button(
            acao_frame,
            text="🔄 Reatribuir Entidades para Cidade Mãe",
            font=("Segoe UI", 9, "bold"),
            bg="#2F855A",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=14,
            pady=4,
            command=self._migrar_entidades,
            cursor="hand2",
        )
        self.btn_migrar.grid(row=0, column=5, padx=10, sticky="e")
        acao_frame.columnconfigure(5, weight=1)

    def _buscar_cidades(self):
        termo = self.txt_busca.get().strip()
        uf = self.txt_uf.get().strip()

        for it in self.tree_cid.get_children():
            self.tree_cid.delete(it)
        for it in self.tree_ent.get_children():
            self.tree_ent.delete(it)

        self.lbl_distrito_sel.config(text="-")

        try:
            self._cidades_atuais = self.service.buscar_cidades(termo, uf)
            for c in self._cidades_atuais:
                self.tree_cid.insert(
                    "",
                    tk.END,
                    values=(c.cid_cod, c.nome, c.uf, c.ibge, c.total_entidades),
                )
        except Exception as e:
            messagebox.showerror("Erro de Busca", f"Falha ao pesquisar localidades:\n{e}")

    def _ao_selecionar_cidade(self, event=None):
        sel = self.tree_cid.selection()
        if not sel:
            return
        vals = self.tree_cid.item(sel[0])["values"]
        if not vals:
            return

        cid_cod = str(vals[0])
        nome = str(vals[1])
        uf = str(vals[2])

        self.lbl_distrito_sel.config(text=f"{cid_cod} - {nome}/{uf}")

        for it in self.tree_ent.get_children():
            self.tree_ent.delete(it)

        try:
            entidades = self.service.obter_entidades_localidade(cid_cod)
            for ent in entidades:
                self.tree_ent.insert(
                    "",
                    tk.END,
                    values=(ent.ent_cod, ent.nome, ent.documento, ent.cep, ent.endereco, ent.bairro),
                )
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao listar entidades da localidade:\n{e}")

    def _consultar_viacep_entidade(self):
        sel = self.tree_ent.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione uma entidade na tabela inferior para consultar o CEP.")
            return

        cep = str(self.tree_ent.item(sel[0])["values"][3]).replace("-", "").strip()
        if not cep:
            messagebox.showwarning("Aviso", "A entidade selecionada não possui CEP cadastrado.")
            return

        try:
            info = self.service.consultar_cep(cep)
            if info:
                msg = (
                    f"Consulta ViaCEP Oficial:\n\n"
                    f"Cidade: {info.get('localidade')}/{info.get('uf')}\n"
                    f"Bairro: {info.get('bairro')}\n"
                    f"Logradouro: {info.get('logradouro')}\n"
                    f"Código IBGE: {info.get('ibge')}\n"
                )
                messagebox.showinfo("ViaCEP Oficial", msg)
            else:
                messagebox.showwarning("ViaCEP", "CEP não localizado nos Correios.")
        except Exception as e:
            messagebox.showerror("Erro ViaCEP", f"Falha ao consultar CEP:\n{e}")

    def _migrar_entidades(self):
        sel = self.tree_cid.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione o distrito de origem na tabela superior.")
            return

        cid_origem = str(self.tree_cid.item(sel[0])["values"][0])
        cid_destino = self.txt_cid_destino.get().strip()

        if not cid_destino:
            messagebox.showwarning("Aviso", "Informe o código da cidade mãe de destino.")
            return

        if not messagebox.askyesno(
            "Confirmação de Migração",
            f"Confirma a reatribuição de todas as entidades do distrito '{cid_origem}' para a cidade mãe '{cid_destino}'?",
        ):
            return

        res = self.service.corrigir_distrito_para_cidade(cid_origem, cid_destino)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self._buscar_cidades()
        else:
            messagebox.showerror("Erro", res.mensagem)
