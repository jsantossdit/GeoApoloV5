"""
Interface Gráfica (Tkinter / ttk) para Importação e Atualização de Grupos de Oração SAVIC -> GeoAlvo.
Equivalente direto a unt_importa_atualiza_go_savic_apolo.pas / .dfm do Delphi.
"""

import os
import sys
import logging
import threading
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any, List

from core import obter_caminho_recurso, centralizar_janela, aplicar_icone_janela
from savic.models import SavicFiltroDTO
from savic.service import SavicService

logger = logging.getLogger(__name__)


class MaskedDateEntry(ttk.Entry):
    """Entry com máscara brasileira de data (DD/MM/AAAA) permitindo digitação contínua sem apagar as barras."""

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._var = tk.StringVar(value="")
        self.config(textvariable=self._var)
        self.bind("<KeyRelease>", self._ao_digitar)
        self.bind("<FocusOut>", self._ao_perder_foco)

    def _ao_digitar(self, event):
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab", "Return", "Escape"):
            return
        texto = "".join([c for c in self._var.get() if c.isdigit()])[:8]
        fmt = ""
        if len(texto) > 4:
            fmt = f"{texto[:2]}/{texto[2:4]}/{texto[4:]}"
        elif len(texto) > 2:
            fmt = f"{texto[:2]}/{texto[2:]}"
        elif len(texto) > 0:
            fmt = texto
        self._var.set(fmt)
        self.icursor(len(fmt))

    def _ao_perder_foco(self, event):
        val = self.get().strip()
        if not val:
            return
        # Se usuário digitou 8 dígitos sem barras
        d = "".join([c for c in val if c.isdigit()])
        if len(d) == 8:
            self._var.set(f"{d[:2]}/{d[2:4]}/{d[4:]}")

    def obter_data(self) -> Optional[date]:
        val = self.get().strip()
        partes = val.split("/")
        if len(partes) == 3 and len(partes[2]) == 4:
            try:
                return date(int(partes[2]), int(partes[1]), int(partes[0]))
            except ValueError:
                return None
        return None

    def definir_data(self, d: date):
        if isinstance(d, (date, datetime)):
            self._var.set(d.strftime("%d/%m/%Y"))


class SavicImportaGOView(tk.Toplevel):
    """Formulário de Integração SAVIC x Apolo (unt_importa_atualiza_go_savic_apolo)."""

    def __init__(self, parent=None, empresa_codigo: str = "1.01"):
        super().__init__(parent)
        self.parent = parent
        self.empresa_codigo = empresa_codigo

        self.title("Integração SAVIC x Apolo - Importar Grupos de Oração do SAVIC")
        self.geometry("980x660")
        self.minsize(860, 560)

        centralizar_janela(self, parent, 980, 660)
        aplicar_icone_janela(self)

        self._service = SavicService()

        self._criar_interface()
        self._carregar_dados_locais()
        self._atualizar_nome_categ_go()
        self._atualizar_nome_categ_coord()

        # Atalhos
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<F10>", lambda e: self.destroy())

    def _criar_interface(self):
        # -------------------------------------------------------------
        # Barra de Ferramentas Superior
        # -------------------------------------------------------------
        toolbar = ttk.Frame(self, padding="8")
        toolbar.pack(fill=tk.X, side=tk.TOP)

        btn_conectar = ttk.Button(
            toolbar,
            text="⚡ Conectar ao Savic",
            command=self._conectar_savic_acao
        )
        btn_conectar.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_importar = ttk.Button(
            toolbar,
            text="📥 Importar/Atualizar",
            command=self._iniciar_importacao_acao
        )
        self.btn_importar.pack(side=tk.LEFT, padx=6)

        btn_limpar = ttk.Button(
            toolbar,
            text="🧹 Limpar",
            command=self._limpar_campos
        )
        btn_limpar.pack(side=tk.LEFT, padx=6)

        btn_fechar = ttk.Button(
            toolbar,
            text="✖ Retornar <F10>",
            command=self.destroy
        )
        btn_fechar.pack(side=tk.RIGHT, padx=6)

        # -------------------------------------------------------------
        # Painel Central Superior: Status SAVIC e Filtros
        # -------------------------------------------------------------
        top_frame = ttk.Frame(self, padding="10")
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        # Quadro da esquerda: Status no SAVIC
        lf_status = ttk.LabelFrame(top_frame, text=" Status dos Grupos de Oração no Savic ", padding="12")
        lf_status.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        ttk.Label(lf_status, text="Quantidade Total de G.O.:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=4)
        self.lbl_total_go = ttk.Label(lf_status, text="000", font=("Segoe UI", 10, "bold"), foreground="#1E3A8A")
        self.lbl_total_go.grid(row=0, column=1, sticky="e", padx=(20, 0), pady=4)

        ttk.Label(lf_status, text="Quantidade G.O. Homologados:").grid(row=1, column=0, sticky="w", pady=4)
        self.lbl_homologados = ttk.Label(lf_status, text="000", font=("Segoe UI", 10, "bold"), foreground="#16A34A")
        self.lbl_homologados.grid(row=1, column=1, sticky="e", padx=(20, 0), pady=4)

        ttk.Label(lf_status, text="Quantidade G.O. Não Homologados:").grid(row=2, column=0, sticky="w", pady=4)
        self.lbl_nao_homologados = ttk.Label(lf_status, text="000", font=("Segoe UI", 10, "bold"), foreground="#DC2626")
        self.lbl_nao_homologados.grid(row=2, column=1, sticky="e", padx=(20, 0), pady=4)

        ttk.Label(lf_status, text="Quantidade G.O. Em Andamento:").grid(row=3, column=0, sticky="w", pady=4)
        self.lbl_em_andamento = ttk.Label(lf_status, text="000", font=("Segoe UI", 10, "bold"), foreground="#D97706")
        self.lbl_em_andamento.grid(row=3, column=1, sticky="e", padx=(20, 0), pady=4)

        # Quadro da direita: Filtro por Data e Total Apurado
        lf_filtro = ttk.LabelFrame(top_frame, text=" Filtro de Apuração (SAVIC) ", padding="12")
        lf_filtro.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        f_datas = ttk.Frame(lf_filtro)
        f_datas.pack(anchor="w", pady=(0, 10))

        ttk.Label(f_datas, text="Período de Atualização G.O.:").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))

        ttk.Label(f_datas, text="De:").grid(row=1, column=0, sticky="w")
        self.edt_dt_ini = MaskedDateEntry(f_datas, width=12)
        self.edt_dt_ini.grid(row=1, column=1, sticky="w", padx=(4, 12))

        ttk.Label(f_datas, text="Até:").grid(row=1, column=2, sticky="w")
        self.edt_dt_fim = MaskedDateEntry(f_datas, width=12)
        self.edt_dt_fim.grid(row=1, column=3, sticky="w", padx=(4, 0))

        # Evento Enter e FocusOut na data final calcula registros apurados
        self.edt_dt_fim.bind("<Return>", lambda e: self._calcular_apuracao_acao())
        self.edt_dt_fim.bind("<FocusOut>", lambda e: self._calcular_apuracao_acao())

        # Total de Registros Apurados
        f_total = ttk.Frame(lf_filtro)
        f_total.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(
            f_total,
            text="Total de Registros Apurados:",
            font=("Segoe UI", 10, "bold")
        ).pack(side=tk.LEFT)

        self.lbl_apurados = ttk.Label(
            f_total,
            text="00000",
            font=("Segoe UI", 12, "bold"),
            foreground="#2563EB"
        )
        self.lbl_apurados.pack(side=tk.LEFT, padx=10)

        btn_apurar = ttk.Button(f_total, text="🔍 Apurar", command=self._calcular_apuracao_acao)
        btn_apurar.pack(side=tk.RIGHT)

        # -------------------------------------------------------------
        # Categorias para Integração no GeoAlvo
        # -------------------------------------------------------------
        lf_cat = ttk.LabelFrame(self, text=" Categorias para Integração no GeoAlvo ", padding="10")
        lf_cat.pack(fill=tk.X, padx=10, pady=(0, 6))

        f_cat_go = ttk.Frame(lf_cat)
        f_cat_go.pack(fill=tk.X, pady=2)
        ttk.Label(f_cat_go, text="Categoria Grupos de Oração:", width=32, anchor="w", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        self.var_categ_go = tk.StringVar(value="02.001")
        self.edt_categ_go = ttk.Entry(f_cat_go, textvariable=self.var_categ_go, width=15)
        self.edt_categ_go.pack(side=tk.LEFT, padx=(4, 6))
        self.edt_categ_go.bind("<FocusOut>", lambda e: self._atualizar_nome_categ_go())
        btn_busca_cat_go = ttk.Button(f_cat_go, text="🔍 Buscar", width=9, command=self._abrir_busca_categoria_go)
        btn_busca_cat_go.pack(side=tk.LEFT, padx=(0, 10))
        self.lbl_categ_nome_go = ttk.Label(f_cat_go, text="...", font=("Segoe UI", 9, "bold"), foreground="#1E3A8A")
        self.lbl_categ_nome_go.pack(side=tk.LEFT, fill=tk.X, expand=True)

        f_cat_coord = ttk.Frame(lf_cat)
        f_cat_coord.pack(fill=tk.X, pady=2)
        ttk.Label(f_cat_coord, text="Categoria Coordenadores de Grupo:", width=32, anchor="w", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        self.var_categ_coord = tk.StringVar(value="02.001.0006")
        self.edt_categ_coord = ttk.Entry(f_cat_coord, textvariable=self.var_categ_coord, width=15)
        self.edt_categ_coord.pack(side=tk.LEFT, padx=(4, 6))
        self.edt_categ_coord.bind("<FocusOut>", lambda e: self._atualizar_nome_categ_coord())
        btn_busca_cat_coord = ttk.Button(f_cat_coord, text="🔍 Buscar", width=9, command=self._abrir_busca_categoria_coord)
        btn_busca_cat_coord.pack(side=tk.LEFT, padx=(0, 10))
        self.lbl_categ_nome_coord = ttk.Label(f_cat_coord, text="...", font=("Segoe UI", 9, "bold"), foreground="#1E3A8A")
        self.lbl_categ_nome_coord.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # -------------------------------------------------------------
        # Barra de Progresso e Status
        # -------------------------------------------------------------
        prog_frame = ttk.Frame(self, padding="10")
        prog_frame.pack(fill=tk.X, padx=10)

        self.progress_bar = ttk.Progressbar(prog_frame, mode="determinate")
        self.progress_bar.pack(fill=tk.X)

        self.lbl_status_acao = ttk.Label(prog_frame, text="Pronto para conectar ou consultar.", foreground="#475569")
        self.lbl_status_acao.pack(anchor="w", pady=(4, 0))

        # -------------------------------------------------------------
        # Grid Inferior: Dados Atuais no GeoAlvo
        # -------------------------------------------------------------
        lf_grid = ttk.LabelFrame(self, text=" Grupos de Oração Cadastrados no GeoAlvo ", padding="10")
        lf_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        cols = ("gocodigo", "gonome_grupodeoracao", "go_local_grupo", "go_tipo_de_local", "situacao_grupo", "dias_semana", "horario")
        self.tree = ttk.Treeview(lf_grid, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("gocodigo", text="Código G.O.")
        self.tree.heading("gonome_grupodeoracao", text="Grupo de Oração")
        self.tree.heading("go_local_grupo", text="Local de Reunião")
        self.tree.heading("go_tipo_de_local", text="Tipo Local")
        self.tree.heading("situacao_grupo", text="Situação")
        self.tree.heading("dias_semana", text="Dia Semana")
        self.tree.heading("horario", text="Horário")

        self.tree.column("gocodigo", width=90, anchor="center")
        self.tree.column("gonome_grupodeoracao", width=240, anchor="w")
        self.tree.column("go_local_grupo", width=180, anchor="w")
        self.tree.column("go_tipo_de_local", width=110, anchor="center")
        self.tree.column("situacao_grupo", width=110, anchor="center")
        self.tree.column("dias_semana", width=100, anchor="center")
        self.tree.column("horario", width=80, anchor="center")

        scroll_y = ttk.Scrollbar(lf_grid, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    # -------------------------------------------------------------
    # Ações e Eventos
    # -------------------------------------------------------------
    def _conectar_savic_acao(self):
        """Conecta ao SAVIC MySQL e atualiza os 4 contadores estatísticos."""
        self.lbl_status_acao.config(text="Conectando à base SAVIC (MySQL)...", foreground="#D97706")
        self.update_idletasks()

        def _task():
            try:
                resumo = self._service.obter_resumo_status()
                self.after(0, lambda: self._atualizar_resumo_ui(resumo))
            except Exception as exc:
                self.after(0, lambda: self._tratar_erro_conexao(exc))

        threading.Thread(target=_task, daemon=True).start()

    def _atualizar_resumo_ui(self, resumo):
        self.lbl_total_go.config(text=str(resumo.total_go))
        self.lbl_homologados.config(text=str(resumo.total_homologados))
        self.lbl_nao_homologados.config(text=str(resumo.total_nao_homologados))
        self.lbl_em_andamento.config(text=str(resumo.total_em_andamento))
        self.lbl_status_acao.config(text="✔ Conectado ao SAVIC. Resumo de Grupos atualizado com sucesso.", foreground="#16A34A")

    def _tratar_erro_conexao(self, exc):
        msg = f"Falha ao conectar à base SAVIC:\n{exc}\n\nVerifique se o host, porta e credenciais estão configurados no menu Configurações -> Banco de Dados -> Banco Dados Savic."
        self.lbl_status_acao.config(text="✖ Erro de conexão com o SAVIC.", foreground="#DC2626")
        messagebox.showerror("Erro de Conexão SAVIC", msg, parent=self)

    def _calcular_apuracao_acao(self):
        """Executa apuração com base nas datas informadas."""
        d_ini = self.edt_dt_ini.obter_data()
        d_fim = self.edt_dt_fim.obter_data()

        if not d_ini or not d_fim:
            # Não faz nada se os campos ainda não foram preenchidos
            return

        if d_ini > d_fim:
            messagebox.showwarning("Atenção", "A Data Inicial não pode ser maior que a Data Final.", parent=self)
            return

        filtro = SavicFiltroDTO(data_inicial=d_ini, data_final=d_fim)
        self.lbl_status_acao.config(text="Calculando registros apurados no SAVIC...", foreground="#D97706")
        self.update_idletasks()

        def _task():
            try:
                qtd = self._service.contar_apurados(filtro)
                self.after(0, lambda: self._exibir_apuracao_ui(qtd))
            except Exception as exc:
                self.after(0, lambda: self._tratar_erro_apuracao(exc))

        threading.Thread(target=_task, daemon=True).start()

    def _exibir_apuracao_ui(self, qtd: int):
        self.lbl_apurados.config(text=str(qtd).zfill(5))
        self.lbl_status_acao.config(text=f"✔ Apuração concluída: {qtd} registros encontrados no período.", foreground="#16A34A")

    def _tratar_erro_apuracao(self, exc):
        self.lbl_status_acao.config(text=f"✖ Erro ao apurar registros: {exc}", foreground="#DC2626")
        messagebox.showerror("Erro na Apuração", str(exc), parent=self)

    def _iniciar_importacao_acao(self):
        """Inicia o processo de importação e sincronização dos coordenadores e grupos."""
        d_ini = self.edt_dt_ini.obter_data()
        d_fim = self.edt_dt_fim.obter_data()

        if not d_ini or not d_fim:
            messagebox.showwarning("Atenção", "Preencha a Data Inicial e a Data Final no formato DD/MM/AAAA para importar.", parent=self)
            return

        resp = messagebox.askyesno(
            "Confirmação",
            f"Deseja iniciar a importação/atualização dos Grupos de Oração e Coordenadores do período {d_ini.strftime('%d/%m/%Y')} a {d_fim.strftime('%d/%m/%Y')}?",
            parent=self
        )
        if not resp:
            return

        filtro = SavicFiltroDTO(data_inicial=d_ini, data_final=d_fim)
        self.btn_importar.config(state="disabled")
        self.progress_bar["value"] = 0
        self.lbl_status_acao.config(text="Iniciando sincronização...", foreground="#D97706")

        def _callback(atual, total, msg):
            self.after(0, lambda: self._atualizar_progresso_ui(atual, total, msg))

        def _task():
            try:
                res = self._service.importar_grupos_e_coordenadores(
                    filtro=filtro,
                    empresa_codigo=self.empresa_codigo,
                    callback_progresso=_callback,
                    categoria_go=self.var_categ_go.get().strip() or "02.001",
                    categoria_coord=self.var_categ_coord.get().strip() or "02.001.0006"
                )
                self.after(0, lambda: self._concluir_importacao_ui(res))
            except Exception as exc:
                self.after(0, lambda: self._tratar_erro_importacao(exc))

        threading.Thread(target=_task, daemon=True).start()

    def _atualizar_progresso_ui(self, atual: int, total: int, msg: str):
        if total > 0:
            porcentagem = int((atual / total) * 100)
            self.progress_bar["value"] = porcentagem
        self.lbl_status_acao.config(text=msg, foreground="#2563EB")

    def _concluir_importacao_ui(self, res):
        self.btn_importar.config(state="normal")
        self.progress_bar["value"] = 100
        self._carregar_dados_locais()

        msg = res.mensagem
        if res.caminho_arquivo_ocorrencias and os.path.exists(res.caminho_arquivo_ocorrencias):
            self.lbl_status_acao.config(
                text=f"✔ Concluído! Ocorrências em: {os.path.basename(res.caminho_arquivo_ocorrencias)}",
                foreground="#16A34A" if res.sucesso else "#D97706"
            )
            abrir_rel = messagebox.askyesno(
                "Sincronização SAVIC x Alvo Concluída",
                f"{msg}\n\nDeseja abrir o arquivo de ocorrências gerado no Bloco de Notas agora?",
                parent=self
            )
            if abrir_rel:
                try:
                    os.startfile(res.caminho_arquivo_ocorrencias)
                except Exception:
                    import subprocess
                    subprocess.Popen(["notepad.exe", res.caminho_arquivo_ocorrencias])
        else:
            if res.sucesso:
                self.lbl_status_acao.config(text="✔ Sincronização concluída com sucesso!", foreground="#16A34A")
                messagebox.showinfo("Sucesso", res.mensagem, parent=self)
            else:
                self.lbl_status_acao.config(text="⚠ Sincronização finalizada com advertências.", foreground="#D97706")
                detalhes = "\n".join(res.erros[:5])
                if len(res.erros) > 5:
                    detalhes += f"\n... e mais {len(res.erros) - 5} ocorrências."
                messagebox.showwarning("Concluído com Avisos", f"{res.mensagem}\n\nOcorrências:\n{detalhes}", parent=self)


    def _tratar_erro_importacao(self, exc):
        self.btn_importar.config(state="normal")
        self.lbl_status_acao.config(text=f"✖ Falha na importação: {exc}", foreground="#DC2626")
        messagebox.showerror("Erro de Importação", str(exc), parent=self)

    def _carregar_dados_locais(self):
        """Carrega e exibe grupos de oração cadastrados na base GeoAlvo."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        grupos = self._service.listar_grupos_ja_importados()
        for g in grupos:
            self.tree.insert("", tk.END, values=(
                g.get("gocodigo", ""),
                g.get("gonome_grupodeoracao", ""),
                g.get("go_local_grupo", ""),
                g.get("go_tipo_de_local", ""),
                g.get("situacao_grupo", ""),
                g.get("dias_semana", ""),
                g.get("horario", "")
            ))

    def _limpar_campos(self):
        self.edt_dt_ini.delete(0, tk.END)
        self.edt_dt_fim.delete(0, tk.END)
        self.lbl_apurados.config(text="00000")
        self.lbl_status_acao.config(text="Campos limpos.", foreground="#475569")
        self.progress_bar["value"] = 0

    def _atualizar_nome_categ_go(self):
        cod = self.var_categ_go.get().strip()
        nome = self._service.obter_nome_categoria(cod) if cod else ""
        self.lbl_categ_nome_go.config(text=nome or "...")

    def _atualizar_nome_categ_coord(self):
        cod = self.var_categ_coord.get().strip()
        nome = self._service.obter_nome_categoria(cod) if cod else ""
        self.lbl_categ_nome_coord.config(text=nome or "...")

    def _abrir_busca_categoria(self, titulo: str, on_selecionado):
        """Abre janela modal para busca e seleção de categoria em USER_geoapolo_categoria."""
        dlg = tk.Toplevel(self)
        dlg.title(titulo)
        dlg.geometry("540x420")
        dlg.transient(self)
        dlg.grab_set()
        centralizar_janela(dlg, self, 540, 420)

        f_busca = ttk.Frame(dlg, padding="10")
        f_busca.pack(fill=tk.X)

        ttk.Label(f_busca, text="Filtrar:").pack(side=tk.LEFT, padx=(0, 6))
        var_filtro = tk.StringVar()
        edt_filtro = ttk.Entry(f_busca, textvariable=var_filtro)
        edt_filtro.pack(side=tk.LEFT, fill=tk.X, expand=True)

        cols = ("codigo", "descricao")
        tree_cat = ttk.Treeview(dlg, columns=cols, show="headings", selectmode="browse")
        tree_cat.heading("codigo", text="Código Estruturado")
        tree_cat.heading("descricao", text="Descrição da Categoria")
        tree_cat.column("codigo", width=140, anchor="w")
        tree_cat.column("descricao", width=360, anchor="w")

        scroll = ttk.Scrollbar(dlg, orient=tk.VERTICAL, command=tree_cat.yview)
        tree_cat.configure(yscrollcommand=scroll.set)

        tree_cat.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=(0, 10))
        scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=(0, 10))

        todas_categorias = self._service.listar_categorias_geoalvo()

        def _preencher(termo=""):
            for item in tree_cat.get_children():
                tree_cat.delete(item)
            t = termo.strip().upper()
            for c in todas_categorias:
                cod = str(c.get("codigo") or "")
                desc = str(c.get("descricao") or "")
                if not t or (t in cod.upper()) or (t in desc.upper()):
                    tree_cat.insert("", tk.END, values=(cod, desc))

        _preencher()
        var_filtro.trace_add("write", lambda *args: _preencher(var_filtro.get()))

        def _confirmar():
            sel = tree_cat.selection()
            if sel:
                vals = tree_cat.item(sel[0], "values")
                if vals:
                    on_selecionado(vals[0], vals[1])
                    try:
                        dlg.destroy()
                    except Exception:
                        pass
            return "break"

        tree_cat.bind("<Double-1>", lambda e: (_confirmar(), "break")[1])
        tree_cat.bind("<Return>", lambda e: (_confirmar(), "break")[1])
        dlg.bind("<Escape>", lambda e: (dlg.destroy(), "break")[1])

    def _abrir_busca_categoria_go(self):
        def _sel(cod, desc):
            self.var_categ_go.set(cod)
            self.lbl_categ_nome_go.config(text=desc)
        self._abrir_busca_categoria("Selecionar Categoria do Grupo de Oração", _sel)

    def _abrir_busca_categoria_coord(self):
        def _sel(cod, desc):
            self.var_categ_coord.set(cod)
            self.lbl_categ_nome_coord.config(text=desc)
        self._abrir_busca_categoria("Selecionar Categoria do Coordenador", _sel)


def abrir_importa_go_savic(parent=None, empresa_codigo: str = "1.01") -> SavicImportaGOView:
    """Função de conveniência para abertura da janela de importação SAVIC."""
    view = SavicImportaGOView(parent=parent, empresa_codigo=empresa_codigo)
    return view
