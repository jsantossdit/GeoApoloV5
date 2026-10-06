"""
Interface Gráfica para Cadastro e Manutenção de Centros de Controle / Custos.
GeoApolo V5
Equivalente a unt_principal (mnucad_mancentrocontrole) e unt_consultav3 do Delphi.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
from datetime import datetime

from core import (
    centralizar_janela,
    vincular_maiusculo,
    configurar_navegacao_enter,
    vincular_mascara_data,
    formatar_data_br,
    converter_data_br_para_iso,
    validar_data_br,
    obter_empresa_ativa,
)
from .models import CentroControleDTO, ResultadoCentroControleDTO
from .service import CentroControleService


class CentrosControleView(ttk.Frame):
    """Tela de Cadastro e Manutenção de Centros de Controle / Custos."""

    def __init__(self, parent=None, service: Optional[CentroControleService] = None, connection=None):
        super().__init__(parent)
        self.service = service

        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from .repository import CentroControleRepository
                conn = connection or obter_conexao_banco()
                self.service = CentroControleService(CentroControleRepository(conn))
            except Exception:
                pass

        self._modo_edicao = False
        self._setup_ui()
        self._configurar_atalhos()
        if self.service:
            self.carregar_centros()
            self._carregar_niveis_pai()

    def _setup_ui(self):
        # Header Superior
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        lbl_titulo = ttk.Label(
            header,
            text="Manutenção de Centros de Controle / Custos",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
        )
        lbl_titulo.pack(side=tk.LEFT)

        self.lbl_contador = ttk.Label(
            header,
            text="0 centro(s) cadastrado(s)",
            font=("Segoe UI", 9, "bold"),
            foreground="#475569",
        )
        self.lbl_contador.pack(side=tk.RIGHT, padx=5)

        # Barra de Pesquisa e Filtros
        bar_filtro = ttk.Frame(self, padding=(10, 4))
        bar_filtro.pack(fill=tk.X)

        ttk.Label(bar_filtro, text="Buscar:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.var_busca = tk.StringVar()
        vincular_maiusculo(self.var_busca)
        self.ent_busca = ttk.Entry(bar_filtro, textvariable=self.var_busca, width=28)
        self.ent_busca.pack(side=tk.LEFT, padx=(0, 6))
        self.ent_busca.bind("<Return>", lambda e: self.carregar_centros())
        self.ent_busca.bind("<KeyRelease>", lambda e: self.carregar_centros())

        ttk.Label(bar_filtro, text="Empresa:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(10, 4))
        self.var_filtro_emp = tk.StringVar(value="")
        self.ent_filtro_emp = ttk.Entry(bar_filtro, textvariable=self.var_filtro_emp, width=8)
        self.ent_filtro_emp.pack(side=tk.LEFT, padx=(0, 8))
        self.ent_filtro_emp.bind("<Return>", lambda e: self.carregar_centros())

        ttk.Button(bar_filtro, text="🔍 Filtrar (F5)", command=self.carregar_centros).pack(side=tk.LEFT, padx=3)
        ttk.Button(bar_filtro, text="🔄 Recarregar", command=self._recarregar).pack(side=tk.LEFT, padx=3)

        # Painel Dividido (Grid à esquerda, Formulário à direita)
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Painel Esquerdo: Grade de Centros de Controle
        frame_grid = ttk.Frame(paned, padding=5)
        paned.add(frame_grid, weight=3)

        cols = ("codestr", "codred", "nome", "nivel", "tipo", "empresa")
        self.tree = ttk.Treeview(frame_grid, columns=cols, show="headings", height=16, selectmode="browse")
        self.tree.heading("codestr", text="Cód. Estruturado")
        self.tree.heading("codred", text="Reduzido")
        self.tree.heading("nome", text="Descrição do Centro de Controle")
        self.tree.heading("nivel", text="Nível Pai")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("empresa", text="Empresa")

        self.tree.column("codestr", width=120, anchor=tk.W)
        self.tree.column("codred", width=65, anchor=tk.CENTER)
        self.tree.column("nome", width=240, anchor=tk.W)
        self.tree.column("nivel", width=100, anchor=tk.W)
        self.tree.column("tipo", width=95, anchor=tk.CENTER)
        self.tree.column("empresa", width=70, anchor=tk.CENTER)

        scroll_y = ttk.Scrollbar(frame_grid, orient=tk.VERTICAL, command=self.tree.yview)
        scroll_x = ttk.Scrollbar(frame_grid, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.bind("<<TreeviewSelect>>", self._ao_selecionar_centro)

        # Painel Direito: Formulário de Cadastro e Manutenção
        frame_form = ttk.LabelFrame(paned, text=" Dados do Centro de Controle ", padding=12)
        paned.add(frame_form, weight=2)

        # 1. Código Estruturado
        ttk.Label(frame_form, text="Código Estruturado: *", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_codestr = tk.StringVar()
        vincular_maiusculo(self.var_codestr)
        self.ent_codestr = ttk.Entry(frame_form, textvariable=self.var_codestr, width=24, font=("Segoe UI", 9, "bold"))
        self.ent_codestr.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))

        # 2. Código Reduzido
        ttk.Label(frame_form, text="Código Reduzido: *", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_codred = tk.StringVar()
        vincular_maiusculo(self.var_codred)
        self.ent_codred = ttk.Entry(frame_form, textvariable=self.var_codred, width=12)
        self.ent_codred.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))

        # 3. Nome / Descrição
        ttk.Label(frame_form, text="Nome / Descrição: *", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_nome = tk.StringVar()
        vincular_maiusculo(self.var_nome)
        self.ent_nome = ttk.Entry(frame_form, textvariable=self.var_nome, width=32)
        self.ent_nome.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))

        # 4. Nível Superior (Pai)
        ttk.Label(frame_form, text="Nível Superior (Pai):", font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(0, 2))
        self.var_nivpai = tk.StringVar()
        self.cb_nivpai = ttk.Combobox(frame_form, textvariable=self.var_nivpai, width=28)
        self.cb_nivpai.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))

        # 5. Tipo (Sintético / Analítico)
        ttk.Label(frame_form, text="Tipo de Centro:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        f_tipo = ttk.Frame(frame_form)
        f_tipo.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))
        self.var_tipo = tk.StringVar(value="A")
        rb_ana = ttk.Radiobutton(f_tipo, text="Analítico (Aceita lançamentos)", variable=self.var_tipo, value="A")
        rb_ana.pack(anchor=tk.W)
        rb_sin = ttk.Radiobutton(f_tipo, text="Sintético / Grupo (Totalizador)", variable=self.var_tipo, value="T")
        rb_sin.pack(anchor=tk.W)

        # 6. Custo Auxiliar e Empresa
        f_linha_custo_emp = ttk.Frame(frame_form)
        f_linha_custo_emp.pack(fill=tk.X, pady=(0, 8))

        f_custo = ttk.Frame(f_linha_custo_emp)
        f_custo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Label(f_custo, text="Centro de Custo Aux:", font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(0, 2))
        self.var_custo = tk.StringVar()
        vincular_maiusculo(self.var_custo)
        self.ent_custo = ttk.Entry(f_custo, textvariable=self.var_custo, width=12)
        self.ent_custo.pack(fill=tk.X)

        f_emp = ttk.Frame(f_linha_custo_emp)
        f_emp.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
        ttk.Label(f_emp, text="Empresa: *", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.var_emp = tk.StringVar(value=obter_empresa_ativa())
        self.ent_emp = ttk.Entry(f_emp, textvariable=self.var_emp, width=8)
        self.ent_emp.pack(fill=tk.X)

        # 7. Datas de Validade (Inicial e Final)
        f_datas = ttk.Frame(frame_form)
        f_datas.pack(fill=tk.X, pady=(0, 15))

        f_dt_ini = ttk.Frame(f_datas)
        f_dt_ini.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        ttk.Label(f_dt_ini, text="Validade Inicial:", font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(0, 2))
        self.var_dt_ini = tk.StringVar()
        self.ent_dt_ini = ttk.Entry(f_dt_ini, textvariable=self.var_dt_ini, width=12)
        self.ent_dt_ini.pack(fill=tk.X)
        vincular_mascara_data(self.ent_dt_ini)

        f_dt_fim = ttk.Frame(f_datas)
        f_dt_fim.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
        ttk.Label(f_dt_fim, text="Validade Final:", font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(0, 2))
        self.var_dt_fim = tk.StringVar()
        self.ent_dt_fim = ttk.Entry(f_dt_fim, textvariable=self.var_dt_fim, width=12)
        self.ent_dt_fim.pack(fill=tk.X)
        vincular_mascara_data(self.ent_dt_fim)

        # Barra de Botões
        bar_btns = ttk.Frame(frame_form)
        bar_btns.pack(fill=tk.X, pady=(10, 0))

        btn_novo = tk.Button(
            bar_btns,
            text="➕ Novo",
            bg="#2563EB",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=4,
            relief=tk.FLAT,
            command=self._novo_registro,
        )
        btn_novo.pack(side=tk.LEFT, padx=2)

        btn_salvar = tk.Button(
            bar_btns,
            text="✔ Salvar (F10)",
            bg="#16A34A",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=4,
            relief=tk.FLAT,
            command=self._salvar_centro,
        )
        btn_salvar.pack(side=tk.LEFT, padx=2)

        btn_excluir = tk.Button(
            bar_btns,
            text="🗑 Excluir",
            bg="#DC2626",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=4,
            relief=tk.FLAT,
            command=self._excluir_centro,
        )
        btn_excluir.pack(side=tk.LEFT, padx=2)

        btn_limpar = tk.Button(
            bar_btns,
            text="Limpar",
            bg="#F3F4F6",
            fg="#1F2937",
            font=("Segoe UI", 9),
            padx=8,
            pady=4,
            relief=tk.GROOVE,
            command=self._limpar_campos,
        )
        btn_limpar.pack(side=tk.LEFT, padx=2)


    def _configurar_atalhos(self):
        self.bind_all("<F5>", lambda e: self.carregar_centros())
        self.bind_all("<F10>", lambda e: self._salvar_centro())
        configurar_navegacao_enter([
            self.ent_codestr,
            self.ent_codred,
            self.ent_nome,
            self.cb_nivpai,
            self.ent_custo,
            self.ent_emp,
            self.ent_dt_ini,
            self.ent_dt_fim,
        ])

    def carregar_centros(self):
        """Carrega a grade com a lista de centros de controle."""
        if not self.service:
            return
        termo = self.var_busca.get().strip()
        emp = self.var_filtro_emp.get().strip()
        centros = self.service.listar_centros(termo=termo, empcod=emp)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for c in centros:
            self.tree.insert("", tk.END, iid=c.geocctrlcodestr, values=(
                c.geocctrlcodestr,
                c.geocctrlcodreduzido,
                c.geocctrlnome,
                c.geocctrlcodestrniv or "-",
                c.display_tipo,
                c.empcod,
            ))

        total = len(centros)
        self.lbl_contador.config(text=f"{total} centro(s) cadastrado(s)")

    def _carregar_niveis_pai(self):
        """Carrega as opções de níveis sintéticos disponíveis para vínculo hierárquico."""
        if not self.service:
            return
        niveis = self.service.listar_niveis_superiores()
        opcoes = [""] + [f"{n.geocctrlcodestr} - {n.geocctrlnome}" for n in niveis]
        self.cb_nivpai["values"] = opcoes

    def _ao_selecionar_centro(self, event=None):
        """Carrega os dados do centro de controle selecionado na grade para os campos do formulário."""
        sel = self.tree.selection()
        if not sel:
            return
        cod = str(sel[0])
        if not self.service:
            return
        c = self.service.obter_centro(str(cod))
        if c:
            self._modo_edicao = True
            self.var_codestr.set(c.geocctrlcodestr)
            self.ent_codestr.config(state="readonly")
            self.var_codred.set(c.geocctrlcodreduzido)
            self.var_nome.set(c.geocctrlnome)

            # Localiza nível pai na combo
            val_pai = c.geocctrlcodestrniv
            for op in self.cb_nivpai["values"]:
                if op.startswith(f"{val_pai} -") or op == val_pai:
                    self.var_nivpai.set(op)
                    break
            else:
                self.var_nivpai.set(val_pai or "")

            self.var_tipo.set(c.geocctrlgrupo or "A")
            self.var_custo.set(c.geocctrlcusto or "")
            self.var_emp.set(c.empcod or obter_empresa_ativa())
            self.var_dt_ini.set(formatar_data_br(c.geodatavalidadeinicial) if c.geodatavalidadeinicial else "")
            self.var_dt_fim.set(formatar_data_br(c.geodatavalidadefinal) if c.geodatavalidadefinal else "")

    def _limpar_campos(self):
        """Limpa o formulário e destrava o campo de código para novo cadastro."""
        self._modo_edicao = False
        self.ent_codestr.config(state="normal")
        self.var_codestr.set("")
        self.var_codred.set("")
        self.var_nome.set("")
        self.var_nivpai.set("")
        self.var_tipo.set("A")
        self.var_custo.set("")
        self.var_emp.set(obter_empresa_ativa())
        self.var_dt_ini.set("")
        self.var_dt_fim.set("")
        self.ent_codestr.focus_set()

    def _novo_registro(self):
        """Inicia um novo registro com código reduzido sugerido."""
        self._limpar_campos()
        if self.service:
            prox_red = self.service.obter_sugestao_codigo_reduzido()
            self.var_codred.set(prox_red)
        self.ent_codestr.focus_set()

    def _recarregar(self):
        self.var_busca.set("")
        self.var_filtro_emp.set("")
        self.carregar_centros()
        self._carregar_niveis_pai()
        self._limpar_campos()

    def _salvar_centro(self):
        """Valida e envia o DTO do centro de controle para a camada de serviço."""
        if not self.service:
            return

        cod_estr = self.var_codestr.get().strip().upper()
        if not cod_estr:
            messagebox.showerror("Aviso", "O Código Estruturado é obrigatório.", parent=self)
            self.ent_codestr.focus_set()
            return

        nome = self.var_nome.get().strip().upper()
        if not nome:
            messagebox.showerror("Aviso", "A Descrição do Centro de Controle é obrigatória.", parent=self)
            self.ent_nome.focus_set()
            return

        # Nível Pai (extrai apenas o código estruturado se selecionado com descrição)
        niv_raw = self.var_nivpai.get().strip()
        niv_cod = niv_raw.split(" - ")[0].strip() if " - " in niv_raw else niv_raw

        # Datas
        d_ini_br = self.var_dt_ini.get().strip()
        if d_ini_br and not validar_data_br(d_ini_br):
            messagebox.showerror("Aviso", "Data de validade inicial inválida. Utilize DD/MM/AAAA.", parent=self)
            self.ent_dt_ini.focus_set()
            return
        d_ini_iso = converter_data_br_para_iso(d_ini_br) if d_ini_br else None

        d_fim_br = self.var_dt_fim.get().strip()
        if d_fim_br and not validar_data_br(d_fim_br):
            messagebox.showerror("Aviso", "Data de validade final inválida. Utilize DD/MM/AAAA.", parent=self)
            self.ent_dt_fim.focus_set()
            return
        d_fim_iso = converter_data_br_para_iso(d_fim_br) if d_fim_br else None

        dto = CentroControleDTO(
            geocctrlcodestr=cod_estr,
            geocctrlcodreduzido=self.var_codred.get().strip() or "01",
            geocctrlnome=nome,
            geocctrlcodestrniv=niv_cod,
            geocctrlgrupo=self.var_tipo.get().strip().upper() or "A",
            geocctrlcusto=self.var_custo.get().strip(),
            geodatavalidadeinicial=d_ini_iso,
            geodatavalidadefinal=d_fim_iso,
            empcod=self.var_emp.get().strip() or obter_empresa_ativa(),
        )

        res = self.service.salvar_centro(dto)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem, parent=self)
            self.carregar_centros()
            self._carregar_niveis_pai()
            self._limpar_campos()
        else:
            messagebox.showerror("Erro ao Salvar", res.mensagem, parent=self)

    def _excluir_centro(self):
        """Exclui o centro de controle selecionado."""
        if not self.service:
            return

        cod_estr = self.var_codestr.get().strip().upper()
        if not cod_estr:
            messagebox.showwarning("Aviso", "Selecione um Centro de Controle na lista para excluir.", parent=self)
            return

        nome = self.var_nome.get().strip()
        if not messagebox.askyesno(
            "Confirmação de Exclusão",
            f"Deseja realmente excluir o Centro de Controle '{cod_estr} - {nome}'?",
            parent=self,
        ):
            return

        res = self.service.excluir_centro(cod_estr)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem, parent=self)
            self.carregar_centros()
            self._carregar_niveis_pai()
            self._limpar_campos()
        else:
            messagebox.showerror("Erro ao Excluir", res.mensagem, parent=self)


def abrir_janela_centros_controle(parent, connection=None):
    """Abre a tela de Manutenção de Centros de Controle em janela TopLevel."""
    win = tk.Toplevel(parent)
    win.title("Manutenção de Centros de Controle / Custos - GeoAlvo")
    win.minsize(1050, 560)
    centralizar_janela(win, parent, 1180, 620)
    view = CentrosControleView(win, connection=connection)
    view.pack(fill=tk.BOTH, expand=True)
    return win

