"""
Interface Gráfica para Cadastro e Manutenção de Localização Física (Ativo Fixo).
GeoApolo V5
Equivalente funcional à gestão de localizações físicas do módulo SATFI em Delphi.
Tabela: USER_geoapolo_satfi_localizacao_fisica
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from core import (
    centralizar_janela,
    vincular_maiusculo,
    configurar_navegacao_enter,
    habilitar_filtro_dinamico_combobox,
)
from ativo_imobilizado.repository import AtivoImobilizadoRepository


class LocalizacaoFisicaView(ttk.Frame):
    """Tela de manutenção de localizações físicas patrimoniais."""

    def __init__(self, parent=None, repo: Optional[AtivoImobilizadoRepository] = None, connection=None):
        super().__init__(parent)
        self.repo = repo or AtivoImobilizadoRepository(connection)
        self._map_departamentos = {}
        self._setup_ui()
        self._configurar_atalhos()
        self._carregar_departamentos()
        self.carregar_localizacoes()
        self._novo_registro()

    def _setup_ui(self):
        # Header superior
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Cadastro de Localização Física (Ativo Fixo)",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
        ).pack(side=tk.LEFT)

        self.lbl_total = ttk.Label(
            header,
            text="0 localização(ões)",
            font=("Segoe UI", 9, "bold"),
            foreground="#475569",
        )
        self.lbl_total.pack(side=tk.RIGHT)

        # Divisão em duas colunas (Esquerda: Lista / Direita: Formulário)
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # -------------------------------------------------------------
        # Painel Esquerdo: Lista de Localizações
        # -------------------------------------------------------------
        f_left = ttk.Frame(paned, padding=6)
        paned.add(f_left, weight=3)

        f_busca = ttk.Frame(f_left)
        f_busca.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(f_busca, text="Buscar:").pack(side=tk.LEFT, padx=(0, 4))
        self.var_busca = tk.StringVar()
        vincular_maiusculo(self.var_busca)
        ent_b = ttk.Entry(f_busca, textvariable=self.var_busca, width=22)
        ent_b.pack(side=tk.LEFT, padx=(0, 6), fill=tk.X, expand=True)
        ent_b.bind("<Return>", lambda e: self.carregar_localizacoes())

        btn_filtrar = ttk.Button(f_busca, text="Filtrar", command=self.carregar_localizacoes, width=8)
        btn_filtrar.pack(side=tk.LEFT, padx=2)

        btn_todos = ttk.Button(f_busca, text="Todos", command=self._limpar_filtro, width=7)
        btn_todos.pack(side=tk.LEFT, padx=2)

        cols = ("cod", "descricao", "depto", "tipo")
        self.tree = ttk.Treeview(f_left, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("cod", text="Código")
        self.tree.heading("descricao", text="Localização Física")
        self.tree.heading("depto", text="Departamento")
        self.tree.heading("tipo", text="Tipo")

        self.tree.column("cod", width=90, anchor=tk.CENTER)
        self.tree.column("descricao", width=220, anchor=tk.W)
        self.tree.column("depto", width=160, anchor=tk.W)
        self.tree.column("tipo", width=70, anchor=tk.CENTER)

        sb_y = ttk.Scrollbar(f_left, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb_y.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self._ao_selecionar)

        # -------------------------------------------------------------
        # Painel Direito: Edição / Cadastro
        # -------------------------------------------------------------
        f_right = ttk.Frame(paned, padding=8)
        paned.add(f_right, weight=2)

        box_form = ttk.LabelFrame(f_right, text=" Detalhes da Localização Física ", padding=12)
        box_form.pack(fill=tk.BOTH, expand=True)

        ttk.Label(box_form, text="Código da Localização: *", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_codigo = tk.StringVar()
        vincular_maiusculo(self.var_codigo)
        self.ent_codigo = ttk.Entry(box_form, textvariable=self.var_codigo, width=16, font=("Segoe UI", 9, "bold"))
        self.ent_codigo.pack(anchor=tk.W, pady=(0, 8))

        ttk.Label(box_form, text="Descrição / Localização: *", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_descricao = tk.StringVar()
        vincular_maiusculo(self.var_descricao)
        self.ent_descricao = ttk.Entry(box_form, textvariable=self.var_descricao, width=38)
        self.ent_descricao.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(box_form, text="Departamento Vinculado:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_depto = tk.StringVar()
        self.cbo_depto = ttk.Combobox(box_form, textvariable=self.var_depto, width=36)
        self.cbo_depto.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(box_form, text="Tipo da Localização:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_tipo = tk.StringVar(value="A - ANALÍTICO")
        self.cbo_tipo = ttk.Combobox(
            box_form,
            textvariable=self.var_tipo,
            values=["A - ANALÍTICO", "G - GRUPO"],
            state="readonly",
            width=20,
        )
        self.cbo_tipo.pack(anchor=tk.W, pady=(0, 16))

        # Barra de Botões de Ação
        f_botoes = ttk.Frame(box_form)
        f_botoes.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

        self.btn_novo = ttk.Button(f_botoes, text="Novo (F5)", command=self._novo_registro, width=10)
        self.btn_novo.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_gravar = tk.Button(
            f_botoes,
            text="Gravar (F10)",
            bg="#16A34A",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=10,
            pady=4,
            relief=tk.FLAT,
            command=self._gravar,
        )
        self.btn_gravar.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_excluir = ttk.Button(f_botoes, text="Excluir", command=self._excluir, width=10)
        self.btn_excluir.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_fechar = ttk.Button(f_botoes, text="Fechar (Esc)", command=self._fechar, width=11)
        self.btn_fechar.pack(side=tk.RIGHT)

        configurar_navegacao_enter([self.ent_codigo, self.ent_descricao, self.cbo_depto, self.cbo_tipo])

    def _configurar_atalhos(self):
        root = self.winfo_toplevel()
        root.bind("<F5>", lambda e: self._novo_registro())
        root.bind("<F10>", lambda e: self._gravar())
        root.bind("<Escape>", lambda e: self._fechar())

    def _fechar(self):
        top = self.winfo_toplevel()
        if top != self:
            top.destroy()

    def _limpar_filtro(self):
        self.var_busca.set("")
        self.carregar_localizacoes()

    def _carregar_departamentos(self):
        try:
            deptos = self.repo.listar_departamentos()
            self._map_departamentos = {d["codigo"]: d["nome"] for d in deptos}
            opcoes = [f"{d['codigo']} - {d['nome']}" for d in deptos]
            habilitar_filtro_dinamico_combobox(self.cbo_depto, opcoes)
        except Exception:
            pass

    def carregar_localizacoes(self):
        for it in self.tree.get_children():
            self.tree.delete(it)

        filtro = self.var_busca.get().strip().upper()
        try:
            lista = self.repo.listar_todas_localizacoes()
            total = 0
            for item in lista:
                cod = str(item.get("codigo_localizacao", ""))
                desc = str(item.get("localizacao", ""))
                depto = str(item.get("departamento", ""))
                tipo_raw = str(item.get("grupo", "A")).upper()
                tipo_lbl = "GRUPO" if tipo_raw == "G" else "ANALÍTICO"

                if not filtro or filtro in cod.upper() or filtro in desc.upper() or filtro in depto.upper():
                    self.tree.insert("", tk.END, iid=cod, values=(cod, desc, depto, tipo_lbl))
                    total += 1
            self.lbl_total.config(text=f"{total} localização(ões)")
        except Exception as ex:
            messagebox.showerror("Erro", f"Falha ao listar localizações: {ex}", parent=self)

    def _ao_selecionar(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        cod = sel[0]
        vals = self.tree.item(cod, "values")
        self.var_codigo.set(vals[0])
        self.var_descricao.set(vals[1])

        # Encontrar departamento
        depto_nome = vals[2]
        self.var_depto.set("")
        for k, v in self._map_departamentos.items():
            if v == depto_nome:
                self.var_depto.set(f"{k} - {v}")
                break

        tipo_lbl = vals[3]
        if tipo_lbl == "GRUPO":
            self.var_tipo.set("G - GRUPO")
        else:
            self.var_tipo.set("A - ANALÍTICO")

        self.ent_codigo.config(state="readonly")
        self.ent_descricao.focus_set()

    def _novo_registro(self):
        self.tree.selection_remove(self.tree.selection())
        self.ent_codigo.config(state="normal")
        self.var_codigo.set("")
        self.var_descricao.set("")
        self.var_depto.set("")
        self.var_tipo.set("A - ANALÍTICO")
        self.ent_codigo.focus_set()

    def _gravar(self):
        cod = self.var_codigo.get().strip().upper()
        desc = self.var_descricao.get().strip().upper()
        depto_raw = self.var_depto.get().strip()
        tipo_raw = self.var_tipo.get().strip().upper()

        if not cod:
            messagebox.showerror("Erro", "Código da localização física é obrigatório.", parent=self)
            self.ent_codigo.focus_set()
            return

        if not desc:
            messagebox.showerror("Erro", "Descrição da localização é obrigatória.", parent=self)
            self.ent_descricao.focus_set()
            return

        codigo_depto = None
        if depto_raw:
            try:
                codigo_depto = int(depto_raw.split(" - ")[0].strip())
            except Exception:
                codigo_depto = None

        grupo_char = "G" if tipo_raw.startswith("G") else "A"

        try:
            self.repo.salvar_localizacao(cod, desc, codigo_depto, grupo_char)
            messagebox.showinfo("Sucesso", f"Localização {cod} - {desc} salva com sucesso!", parent=self)
            self.carregar_localizacoes()
            self._novo_registro()
        except Exception as ex:
            messagebox.showerror("Erro", f"Falha ao gravar localização: {ex}", parent=self)

    def _excluir(self):
        cod = self.var_codigo.get().strip().upper()
        if not cod:
            messagebox.showwarning("Aviso", "Selecione uma localização para excluir.", parent=self)
            return

        desc = self.var_descricao.get().strip()
        if messagebox.askyesno("Excluir", f"Confirma a exclusão da localização {cod} - {desc}?", parent=self):
            try:
                self.repo.excluir_localizacao(cod)
                messagebox.showinfo("Sucesso", "Localização excluída com sucesso!", parent=self)
                self.carregar_localizacoes()
                self._novo_registro()
            except Exception as ex:
                messagebox.showerror("Erro ao Excluir", f"Não foi possível excluir a localização: {ex}", parent=self)


def abrir_localizacoes_fisicas_sistema(parent=None, connection=None):
    """Abre a tela de cadastro de localizações físicas em janela TopLevel."""
    win = tk.Toplevel(parent)
    win.title("Localização Física - Ativo Fixo - GeoAlvo")
    win.minsize(860, 500)
    centralizar_janela(win, parent, 920, 540)
    view = LocalizacaoFisicaView(win, connection=connection)
    view.pack(fill=tk.BOTH, expand=True)
    return win
