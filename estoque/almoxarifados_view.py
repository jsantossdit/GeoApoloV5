"""
Interface Gráfica para Cadastro e Manutenção de Almoxarifados.
GeoApolo V5
Clean Architecture & Suporte a Multi-Almoxarifado.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from datetime import datetime

from core import (
    centralizar_janela,
    vincular_maiusculo,
    configurar_navegacao_enter,
    habilitar_filtro_dinamico_combobox,
)
from estoque.almoxarifados_repository import AlmoxarifadosRepository


class AlmoxarifadosView(ttk.Frame):
    """Tela de manutenção do cadastro de Almoxarifados."""

    def __init__(self, parent=None, repo: Optional[AlmoxarifadosRepository] = None, connection=None):
        super().__init__(parent)
        self.repo = repo or AlmoxarifadosRepository(connection)
        self._map_centros_custo = {}
        self._setup_ui()
        self._configurar_atalhos()
        self._carregar_centros_custo()
        self.carregar_almoxarifados()
        self._novo_registro()

    def _setup_ui(self):
        # Header superior
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Cadastro e Manutenção de Almoxarifados",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
        ).pack(side=tk.LEFT)

        self.lbl_total = ttk.Label(
            header,
            text="0 almoxarifado(s)",
            font=("Segoe UI", 9, "bold"),
            foreground="#475569",
        )
        self.lbl_total.pack(side=tk.RIGHT)

        # Divisão PanedWindow
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # -------------------------------------------------------------
        # Painel Esquerdo: Lista de Almoxarifados
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
        ent_b.bind("<Return>", lambda e: self.carregar_almoxarifados())

        btn_filtrar = ttk.Button(f_busca, text="Filtrar", command=self.carregar_almoxarifados, width=8)
        btn_filtrar.pack(side=tk.LEFT, padx=2)

        btn_todos = ttk.Button(f_busca, text="Todos", command=self._limpar_filtro, width=7)
        btn_todos.pack(side=tk.LEFT, padx=2)

        cols = ("cod", "descricao", "cctrl", "dt_criacao", "status")
        self.tree = ttk.Treeview(f_left, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("cod", text="Código")
        self.tree.heading("descricao", text="Descrição do Almoxarifado")
        self.tree.heading("cctrl", text="Centro de Custo")
        self.tree.heading("dt_criacao", text="Data Criação")
        self.tree.heading("status", text="Status")

        self.tree.column("cod", width=80, anchor=tk.CENTER)
        self.tree.column("descricao", width=220, anchor=tk.W)
        self.tree.column("cctrl", width=140, anchor=tk.W)
        self.tree.column("dt_criacao", width=120, anchor=tk.CENTER)
        self.tree.column("status", width=60, anchor=tk.CENTER)

        sb_y = ttk.Scrollbar(f_left, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb_y.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self._ao_selecionar)

        # -------------------------------------------------------------
        # Painel Direito: Formulário
        # -------------------------------------------------------------
        f_right = ttk.Frame(paned, padding=8)
        paned.add(f_right, weight=2)

        box_form = ttk.LabelFrame(f_right, text=" Detalhes do Almoxarifado ", padding=12)
        box_form.pack(fill=tk.BOTH, expand=True)

        # Código & Status
        r1 = ttk.Frame(box_form)
        r1.pack(fill=tk.X, pady=(0, 6))

        c_cod = ttk.Frame(r1)
        c_cod.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        ttk.Label(c_cod, text="Código do Almoxarifado: *", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_codigo = tk.StringVar()
        vincular_maiusculo(self.var_codigo)
        self.ent_codigo = ttk.Entry(c_cod, textvariable=self.var_codigo, width=14, font=("Segoe UI", 9, "bold"))
        self.ent_codigo.pack(fill=tk.X)

        c_stat = ttk.Frame(r1)
        c_stat.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        ttk.Label(c_stat, text="Situação / Status:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_status = tk.StringVar(value="A - ATIVO")
        self.cbo_status = ttk.Combobox(
            c_stat,
            textvariable=self.var_status,
            values=["A - ATIVO", "I - INATIVO"],
            state="readonly",
            width=12,
        )
        self.cbo_status.pack(fill=tk.X)

        # Descrição
        ttk.Label(box_form, text="Descrição do Almoxarifado: *", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(4, 2))
        self.var_descricao = tk.StringVar()
        vincular_maiusculo(self.var_descricao)
        self.ent_descricao = ttk.Entry(box_form, textvariable=self.var_descricao, width=42)
        self.ent_descricao.pack(fill=tk.X, pady=(0, 6))

        # Centro de Custo a que pertence
        ttk.Label(box_form, text="Centro de Custo Vinculado:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(4, 2))
        self.var_cctrl = tk.StringVar()
        self.cbo_cctrl = ttk.Combobox(box_form, textvariable=self.var_cctrl, width=42)
        self.cbo_cctrl.pack(fill=tk.X, pady=(0, 6))

        # Data de Criação
        ttk.Label(box_form, text="Data de Criação:", font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(4, 2))
        self.var_dt_criacao = tk.StringVar()
        self.ent_dt_criacao = ttk.Entry(box_form, textvariable=self.var_dt_criacao, state="readonly", width=22)
        self.ent_dt_criacao.pack(anchor=tk.W, pady=(0, 6))

        # Campo Text para Finalidade a que se destina
        ttk.Label(box_form, text="Finalidade / Destinação do Almoxarifado:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(4, 2))
        f_txt = ttk.Frame(box_form)
        f_txt.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.txt_finalidade = tk.Text(f_txt, height=5, font=("Segoe UI", 9), wrap=tk.WORD)
        sb_txt = ttk.Scrollbar(f_txt, orient=tk.VERTICAL, command=self.txt_finalidade.yview)
        self.txt_finalidade.configure(yscrollcommand=sb_txt.set)
        self.txt_finalidade.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb_txt.pack(side=tk.RIGHT, fill=tk.Y)

        # Botões de Ação
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

        configurar_navegacao_enter([self.ent_codigo, self.cbo_status, self.ent_descricao, self.cbo_cctrl])

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
        self.carregar_almoxarifados()

    def _carregar_centros_custo(self):
        try:
            cur = self.repo._get_cursor()
            cur.execute("""
                SELECT geocctrlcodestr, geocctrlnome
                FROM USER_geoapolo_centrocontrole WITH (NOLOCK)
                ORDER BY geocctrlcodestr
            """)
            rows = cur.fetchall()
            opcoes = [f"{r[0]} - {r[1]}" for r in rows]
            self._map_centros_custo = {r[0]: r[1] for r in rows}
            habilitar_filtro_dinamico_combobox(self.cbo_cctrl, opcoes)
        except Exception:
            pass

    def carregar_almoxarifados(self):
        for it in self.tree.get_children():
            self.tree.delete(it)

        filtro = self.var_busca.get().strip().upper()
        try:
            lista = self.repo.listar_almoxarifados()
            total = 0
            for item in lista:
                cod = str(item.get("codigo_almoxarifado", ""))
                desc = str(item.get("descricao", ""))
                cc = str(item.get("centro_custo", "") or "")
                cc_nome = str(item.get("nome_centro_custo", ""))
                cc_disp = f"{cc} - {cc_nome}" if cc_nome else cc
                dt = str(item.get("data_criacao", "") or "")[:10]
                st = "ATIVO" if str(item.get("status", "A")).upper() == "A" else "INATIVO"

                if not filtro or filtro in cod.upper() or filtro in desc.upper() or filtro in cc_disp.upper():
                    self.tree.insert("", tk.END, iid=cod, values=(cod, desc, cc_disp, dt, st))
                    total += 1
            self.lbl_total.config(text=f"{total} almoxarifado(s)")
        except Exception as ex:
            messagebox.showerror("Erro", f"Falha ao listar almoxarifados: {ex}", parent=self)

    def _ao_selecionar(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        cod = sel[0]
        almox = self.repo.obter_almoxarifado(cod)
        if not almox:
            return

        self.var_codigo.set(almox.get("codigo_almoxarifado", ""))
        self.var_descricao.set(almox.get("descricao", ""))
        cc = almox.get("centro_custo", "") or ""
        if cc in self._map_centros_custo:
            self.var_cctrl.set(f"{cc} - {self._map_centros_custo[cc]}")
        else:
            self.var_cctrl.set(cc)

        self.var_dt_criacao.set(almox.get("data_criacao", "") or "")
        st = almox.get("status", "A")
        self.var_status.set("A - ATIVO" if st == "A" else "I - INATIVO")

        self.txt_finalidade.delete("1.0", tk.END)
        self.txt_finalidade.insert("1.0", almox.get("finalidade", "") or "")

        self.ent_codigo.config(state="readonly")
        self.ent_descricao.focus_set()

    def _novo_registro(self):
        self.tree.selection_remove(self.tree.selection())
        self.ent_codigo.config(state="normal")
        self.var_codigo.set("")
        self.var_descricao.set("")
        self.var_cctrl.set("")
        self.var_dt_criacao.set(datetime.now().strftime("%d/%m/%Y %H:%M"))
        self.var_status.set("A - ATIVO")
        self.txt_finalidade.delete("1.0", tk.END)
        self.ent_codigo.focus_set()

    def _gravar(self):
        cod = self.var_codigo.get().strip().upper()
        desc = self.var_descricao.get().strip().upper()
        cc_raw = self.var_cctrl.get().strip()
        cc = cc_raw.split(" - ")[0].strip() if cc_raw else ""
        finalidade = self.txt_finalidade.get("1.0", tk.END).strip()
        st_raw = self.var_status.get().strip().upper()
        status = "I" if st_raw.startswith("I") else "A"

        if not cod:
            messagebox.showerror("Erro", "Código do almoxarifado é obrigatório.", parent=self)
            self.ent_codigo.focus_set()
            return

        if not desc:
            messagebox.showerror("Erro", "Descrição do almoxarifado é obrigatória.", parent=self)
            self.ent_descricao.focus_set()
            return

        try:
            self.repo.salvar_almoxarifado(cod, desc, cc, finalidade, status)
            messagebox.showinfo("Sucesso", f"Almoxarifado {cod} - {desc} salvo com sucesso!", parent=self)
            self.carregar_almoxarifados()
            self._novo_registro()
        except Exception as ex:
            messagebox.showerror("Erro", f"Falha ao salvar almoxarifado: {ex}", parent=self)

    def _excluir(self):
        cod = self.var_codigo.get().strip().upper()
        if not cod:
            messagebox.showwarning("Aviso", "Selecione um almoxarifado para excluir.", parent=self)
            return

        desc = self.var_descricao.get().strip()
        if messagebox.askyesno("Excluir", f"Confirma a exclusão do almoxarifado {cod} - {desc}?", parent=self):
            try:
                self.repo.excluir_almoxarifado(cod)
                messagebox.showinfo("Sucesso", "Almoxarifado excluído com sucesso!", parent=self)
                self.carregar_almoxarifados()
                self._novo_registro()
            except Exception as ex:
                messagebox.showerror("Erro ao Excluir", f"Não foi possível excluir o almoxarifado: {ex}", parent=self)


def abrir_almoxarifados_sistema(parent=None, connection=None):
    """Abre a janela de cadastro de almoxarifados."""
    win = tk.Toplevel(parent)
    win.title("Cadastro de Almoxarifados - GeoAlvo")
    win.minsize(860, 520)
    centralizar_janela(win, parent, 940, 560)
    view = AlmoxarifadosView(win, connection=connection)
    view.pack(fill=tk.BOTH, expand=True)
    return win
