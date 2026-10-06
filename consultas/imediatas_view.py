"""
Interface Gráfica para Execução Rápida de Consultas Imediatas.
GeoApolo V5
Equivalente a unt_imediatas.pas (Tfrmimediatas) do Delphi.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from typing import Optional, List, Any

from consultas.models import ConsultaConfigDTO, ResultadoConsultaDTO
from consultas.repository import ConsultasRepository
from consultas.service import ConsultasService
from core import obter_caminho_recurso, centralizar_janela


class ConsultasImediatasView(ttk.Frame):
    """
    Tela de Execução de Consultas Imediatas equivalente ao Tfrmimediatas do Delphi.
    Permite selecionar banco, consulta autorizada, preencher parâmetros dinâmicos e exportar para Excel.
    """

    def __init__(self, parent=None, service: Optional[ConsultasService] = None, connection=None, usuario: str = ""):
        super().__init__(parent)
        self.parent = parent
        self.connection = connection
        self.service = service
        self.usuario_atual = usuario

        if not self.usuario_atual:
            try:
                from logon import sessao_usuario_atual
                self.usuario_atual = (
                    sessao_usuario_atual.get("usucod_apolo")
                    or sessao_usuario_atual.get("login")
                    or sessao_usuario_atual.get("codigo_usuario")
                    or ""
                )
            except Exception:
                self.usuario_atual = ""

        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                conn = self.connection or obter_conexao_banco()
                self.service = ConsultasService(ConsultasRepository(conn))
            except Exception as e:
                print(f"Erro ao conectar serviço de consultas: {e}")

        self._consultas_map = {}  # {descricao: ConsultaConfigDTO}
        self._resultado_atual: Optional[ResultadoConsultaDTO] = None

        self._setup_ui()
        self._carregar_consultas_permitidas()

    def _setup_ui(self):
        # Frame Superior - Barra de Ferramentas / Ações
        top_bar = tk.Frame(self, bg="#f0f0f0", bd=1, relief=tk.RAISED, height=45)
        top_bar.pack(side=tk.TOP, fill=tk.X)

        # Botão Executar Consulta
        btn_executar = tk.Button(
            top_bar,
            text="▶ Executar Consulta",
            font=("Segoe UI", 9, "bold"),
            bg="#2e7d32",
            fg="white",
            activebackground="#1b5e20",
            activeforeground="white",
            relief=tk.RAISED,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self.executar_consulta,
        )
        btn_executar.pack(side=tk.LEFT, padx=6, pady=5)

        # Botão Limpar
        btn_limpar = tk.Button(
            top_bar,
            text="Limpar",
            font=("Segoe UI", 9),
            bg="#f5f5f5",
            relief=tk.RAISED,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.limpar,
        )
        btn_limpar.pack(side=tk.LEFT, padx=4, pady=5)

        # Botão Exportar para Excel
        btn_exportar = tk.Button(
            top_bar,
            text="📊 Exportar para Excel",
            font=("Segoe UI", 9),
            bg="#1976d2",
            fg="white",
            activebackground="#0d47a1",
            activeforeground="white",
            relief=tk.RAISED,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.exportar_excel,
        )
        btn_exportar.pack(side=tk.LEFT, padx=4, pady=5)

        # Botão Exportar para PDF
        btn_pdf = tk.Button(
            top_bar,
            text="📕 Exportar para PDF",
            font=("Segoe UI", 9),
            bg="#b91c1c",
            fg="white",
            activebackground="#991b1b",
            activeforeground="white",
            relief=tk.RAISED,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.exportar_pdf,
        )
        btn_pdf.pack(side=tk.LEFT, padx=4, pady=5)

        # Botão Retornar / Fechar
        btn_fechar = tk.Button(
            top_bar,
            text="Retornar",
            font=("Segoe UI", 9),
            bg="#f5f5f5",
            relief=tk.RAISED,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.retornar,
        )
        btn_fechar.pack(side=tk.RIGHT, padx=8, pady=5)

        # Painel de Seleção e Filtros (equivalente ao GroupBox do Delphi)
        filter_box = ttk.LabelFrame(self, text=" Seleção de Consulta Imediata ", padding=(10, 8))
        filter_box.pack(fill=tk.X, padx=10, pady=6)

        # Linha 1 do painel: Banco de Dados e Consulta
        row1 = ttk.Frame(filter_box)
        row1.pack(fill=tk.X, pady=2)

        ttk.Label(row1, text="Banco de Dados:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self.cbo_banco = ttk.Combobox(
            row1,
            values=["ALVO", "GEOAPOLO", "SAVIC", "APLICATIVO RCC", "TODOS"],
            state="readonly",
            width=16,
            font=("Segoe UI", 9),
        )
        self.cbo_banco.set("ALVO")
        self.cbo_banco.pack(side=tk.LEFT, padx=(0, 15))
        self.cbo_banco.bind("<<ComboboxSelected>>", self._on_banco_selecionado)

        ttk.Label(row1, text="Consulta:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self.cbo_consulta = ttk.Combobox(
            row1,
            state="normal",
            font=("Segoe UI", 9),
        )
        self.cbo_consulta.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.cbo_consulta.bind("<Return>", lambda e: self.executar_consulta())

        # Linha 2 do painel: Contador de registros e mensagens
        row2 = ttk.Frame(filter_box)
        row2.pack(fill=tk.X, pady=(6, 2))

        lbl_tit_reg = tk.Label(
            row2,
            text="Número de Registros Coletados:",
            font=("Segoe UI", 10, "bold"),
            fg="#1565c0",
        )
        lbl_tit_reg.pack(side=tk.LEFT)

        self.lbl_num_reg = tk.Label(
            row2,
            text="0",
            font=("Segoe UI", 11, "bold"),
            fg="#0d47a1",
            padx=8,
        )
        self.lbl_num_reg.pack(side=tk.LEFT)

        self.lbl_status = ttk.Label(
            row2,
            text="Selecione uma consulta e clique em 'Executar Consulta'.",
            font=("Segoe UI", 9, "italic"),
            foreground="#555555",
        )
        self.lbl_status.pack(side=tk.RIGHT, padx=5)

        # Grade de Resultados (DBGrid do Delphi)
        grid_frame = ttk.Frame(self)
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        self.tree_resultados = ttk.Treeview(grid_frame, show="headings", selectmode="extended")
        scroll_y = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.tree_resultados.yview)
        scroll_x = ttk.Scrollbar(grid_frame, orient=tk.HORIZONTAL, command=self.tree_resultados.xview)
        self.tree_resultados.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree_resultados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Barra de status no rodapé
        self.status_bar = ttk.Frame(self, relief=tk.SUNKEN, padding=(6, 2))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        user_info = f"Usuário: {self.usuario_atual or 'PADRÃO'}"
        self.lbl_user_info = ttk.Label(self.status_bar, text=user_info, font=("Segoe UI", 8))
        self.lbl_user_info.pack(side=tk.LEFT)

        self.lbl_footer = ttk.Label(self.status_bar, text="Pronto", font=("Segoe UI", 8))
        self.lbl_footer.pack(side=tk.RIGHT)

    def _on_banco_selecionado(self, event=None):
        """Ao alternar o banco de dados, se for Aplicativo RCC ou SAVIC, valida configurações e conectividade."""
        banco = (self.cbo_banco.get() or "").strip().upper()
        if banco in ("APLICATIVO RCC", "APLICATIVO"):
            try:
                from entidades.database import obter_conexao_aplicativo_rcc
                conn = obter_conexao_aplicativo_rcc(timeout_seg=5)
                conn.close()
                self.lbl_status.config(
                    text="Conexão com Banco do Aplicativo RCC (MySQL) ativa e pronta.",
                    foreground="#16A34A"
                )
            except Exception as exc:
                self.lbl_status.config(
                    text="Atenção: Falha de conexão com o Banco do Aplicativo RCC.",
                    foreground="#DC2626"
                )
                messagebox.showwarning(
                    "Banco do Aplicativo RCC",
                    f"Atenção ao selecionar o Banco do Aplicativo RCC:\n\n{str(exc)}",
                    parent=self
                )
        elif banco == "SAVIC":
            try:
                from config_banco import ConfigManager
                config_mgr = ConfigManager()
                settings = config_mgr.load_savic_settings()
                credentials = config_mgr.get_savic_credentials()
                host = str(settings.get("host") or "").strip()
                db = str(settings.get("database") or "").strip()
                user = str(credentials.get("user") or "").strip()
                if not host or not db or not user:
                    self.lbl_status.config(
                        text="Solicite ao Administrador a configuração de acesso aos dados do SAVIC",
                        foreground="#DC2626"
                    )
                    messagebox.showwarning(
                        "Banco de Dados SAVIC",
                        "Solicite ao Administrador a configuração de acesso aos dados do SAVIC",
                        parent=self
                    )
                else:
                    self.lbl_status.config(
                        text="Conexão com Banco SAVIC configurada e pronta.",
                        foreground="#16A34A"
                    )
            except Exception:
                self.lbl_status.config(
                    text="Solicite ao Administrador a configuração de acesso aos dados do SAVIC",
                    foreground="#DC2626"
                )
        self._carregar_consultas_permitidas()

    def _carregar_consultas_permitidas(self):
        """Carrega a lista de consultas imediatas autorizadas no combobox."""
        if not self.service:
            return

        banco = self.cbo_banco.get()
        try:
            consultas = self.service.listar_consultas_imediatas(usuario=self.usuario_atual, banco=banco)
            self._consultas_map = {c.descricao_consulta: c for c in consultas}
            descricoes = sorted(list(self._consultas_map.keys()))
            from core import habilitar_filtro_dinamico_combobox
            habilitar_filtro_dinamico_combobox(self.cbo_consulta, descricoes)
            if descricoes:
                self.cbo_consulta.set(descricoes[0])
            else:
                self.cbo_consulta.set("")
            self.lbl_status.config(
                text=f"{len(descricoes)} consulta(s) disponível(is) para o banco '{banco}'.",
                foreground="#333333"
            )
        except Exception as e:
            print(f"Erro ao carregar consultas imediatas: {e}")
            self.lbl_status.config(text=f"Erro: {e}", foreground="#d32f2f")

    def _obter_input_parametro(self, nome_param: str, tipo: str) -> Optional[str]:
        """Exibe diálogo modal para solicitar valores de parâmetros (equivalente ao InputBox do Delphi)."""
        if tipo == "data":
            prompt = f"Informe a data para '{nome_param}' (formato DD/MM/AAAA):"
            valor = simpledialog.askstring("GEOAPOLO - Entrada de Data", prompt, parent=self)
            return valor
        else:
            prompt = f"Informe o parâmetro '{nome_param}':"
            valor = simpledialog.askstring("GEOAPOLO - Entrada de Parâmetro", prompt, parent=self)
            return valor

    def executar_consulta(self):
        """Executa a consulta selecionada, solicitando parâmetros dinâmicos se necessário."""
        desc = self.cbo_consulta.get().strip()
        if not desc:
            messagebox.showwarning(
                "Aviso",
                "Para executar uma consulta, primeiro selecione qual consulta deseja!",
                parent=self
            )
            return

        consulta_dto = self._consultas_map.get(desc)
        if not consulta_dto:
            # Tenta buscar pelo repositório se não estiver no mapa
            if self.service:
                consulta_dto = self.service.obter_consulta_por_descricao(desc)

        if not consulta_dto:
            messagebox.showerror("Erro", f"Consulta '{desc}' não encontrada no sistema.", parent=self)
            return

        sql_bruto = consulta_dto.sql_consulta
        if not sql_bruto or not sql_bruto.strip():
            messagebox.showwarning("Aviso", "Esta consulta não possui instrução SQL cadastrada.", parent=self)
            return

        # Validação de segurança
        valido, msg_val = self.service.validar_seguranca_sql_leitura(sql_bruto)
        if not valido:
            messagebox.showerror("Segurança", msg_val, parent=self)
            return

        # Análise e substituição de parâmetros dinâmicos (|Parametro^, {Data}, [Fixo], &?)
        sql_final, sucesso_params = self.service.analisar_e_substituir_parametros(
            sql_bruto,
            callback_input=self._obter_input_parametro
        )

        if not sucesso_params:
            self.lbl_status.config(text="Execução cancelada pelo usuário.", foreground="#d32f2f")
            return

        # Determina o banco de dados de destino da consulta
        banco_destino = (consulta_dto.banco_consulta or self.cbo_banco.get() or "ALVO").strip().upper()
        if banco_destino == "TODOS":
            banco_destino = (consulta_dto.banco_consulta or "ALVO").strip().upper()

        if banco_destino == "SAVIC":
            try:
                from config_banco import ConfigManager
                cm = ConfigManager()
                s_sett = cm.load_savic_settings()
                s_cred = cm.get_savic_credentials()
                h = str(s_sett.get("host") or "").strip()
                d = str(s_sett.get("database") or "").strip()
                u = str(s_cred.get("user") or "").strip()
                if not h or not d or not u:
                    self.lbl_status.config(
                        text="Solicite ao Administrador a configuração de acesso aos dados do SAVIC",
                        foreground="#d32f2f"
                    )
                    messagebox.showwarning(
                        "Configuração SAVIC",
                        "Solicite ao Administrador a configuração de acesso aos dados do SAVIC",
                        parent=self
                    )
                    return
            except Exception:
                self.lbl_status.config(
                    text="Solicite ao Administrador a configuração de acesso aos dados do SAVIC",
                    foreground="#d32f2f"
                )
                messagebox.showwarning(
                    "Configuração SAVIC",
                    "Solicite ao Administrador a configuração de acesso aos dados do SAVIC",
                    parent=self
                )
                return

        # Execução no banco em segundo plano
        import threading
        self.lbl_status.config(text=f"Conectando e executando consulta no banco {banco_destino} em segundo plano...", foreground="#1565c0")
        try:
            self.config(cursor="wait")
        except Exception:
            pass

        def _task():
            res = self.service.executar_consulta_imediata(sql_final, banco=banco_destino)
            self.after(0, lambda: self._pos_execucao_consulta(res, desc))

        threading.Thread(target=_task, daemon=True).start()

    def _pos_execucao_consulta(self, res: ResultadoConsultaDTO, desc: str):
        """Callback invocado na thread principal após término da execução da consulta."""
        try:
            if self.winfo_exists():
                self.config(cursor="")
        except Exception:
            pass

        self._resultado_atual = res

        if not res.sucesso:
            self.lbl_status.config(text="Erro na execução.", foreground="#d32f2f")
            if "Solicite ao Administrador a configuração de acesso aos dados do SAVIC" in (res.mensagem or ""):
                messagebox.showwarning(
                    "Configuração SAVIC",
                    "Solicite ao Administrador a configuração de acesso aos dados do SAVIC",
                    parent=self
                )
            else:
                messagebox.showerror("Erro na Execução da Consulta", f"Não foi possível executar a consulta:\n\n{res.mensagem}", parent=self)
            return

        # Atualiza grade de dados
        self._preencher_grade(res)
        self.lbl_num_reg.config(text=str(res.total_registros))
        self.lbl_status.config(
            text=f"Consulta concluída com sucesso! {res.total_registros} registro(s) obtido(s).",
            foreground="#2e7d32"
        )
        self.lbl_footer.config(text=f"Última execução: {desc} ({res.total_registros} regs)")

    def _preencher_grade(self, res: ResultadoConsultaDTO):
        """Limpa e preenche o Treeview com as colunas e linhas do resultado."""
        # Limpa dados e colunas antigas
        for item in self.tree_resultados.get_children():
            self.tree_resultados.delete(item)

        self.tree_resultados["columns"] = res.colunas
        for col in res.colunas:
            self.tree_resultados.heading(col, text=col, anchor=tk.W)
            # Largura dinâmica com limite mínimo e razoável
            self.tree_resultados.column(col, width=150, minwidth=80, anchor=tk.W)

        # Insere linhas
        for linha in res.linhas:
            linha_formatada = [str(val) if val is not None else "" for val in linha]
            self.tree_resultados.insert("", tk.END, values=linha_formatada)

    def limpar(self):
        """Limpa a grade de dados e reinicia os contadores."""
        for item in self.tree_resultados.get_children():
            self.tree_resultados.delete(item)
        self._resultado_atual = None
        self.lbl_num_reg.config(text="0")
        self.lbl_status.config(text="Grade limpa. Pronto para nova consulta.", foreground="#555555")

    def exportar_excel(self):
        """Exporta os registros da consulta para arquivo XLSX ou CSV."""
        if not self._resultado_atual or not self._resultado_atual.linhas:
            messagebox.showwarning(
                "Aviso",
                "Nenhum resultado disponível para exportação.\nExecute uma consulta primeiro.",
                parent=self
            )
            return

        caminho = filedialog.asksaveasfilename(
            title="Exportar Dados da Consulta",
            defaultextension=".xlsx",
            filetypes=[
                ("Planilha Excel (*.xlsx)", "*.xlsx"),
                ("Arquivo CSV (*.csv)", "*.csv"),
                ("Todos os Arquivos", "*.*")
            ],
            parent=self,
        )

        if not caminho:
            return

        try:
            total = self.service.exportar_resultado_excel(self._resultado_atual, caminho)
            messagebox.showinfo(
                "Exportação Concluída",
                f"Exportação realizada com sucesso!\n\n"
                f"Total de registros exportados: {total}\n"
                f"Arquivo: {os.path.basename(caminho)}",
                parent=self
            )
            self.lbl_status.config(text=f"Exportado com sucesso para {os.path.basename(caminho)}.", foreground="#2e7d32")
        except Exception as exc:
            messagebox.showerror("Erro de Exportação", f"Falha ao exportar dados:\n{exc}", parent=self)

    def exportar_pdf(self):
        """Exporta os resultados da consulta para documento PDF profissional via fpdf2."""
        if not self._resultado_atual or not self._resultado_atual.linhas:
            messagebox.showwarning(
                "Aviso",
                "Nenhum resultado disponível para exportação em PDF.\nExecute uma consulta primeiro.",
                parent=self
            )
            return

        caminho = filedialog.asksaveasfilename(
            title="Exportar Dados da Consulta para PDF",
            defaultextension=".pdf",
            filetypes=[
                ("Documento PDF (*.pdf)", "*.pdf"),
                ("Todos os Arquivos", "*.*")
            ],
            parent=self,
        )

        if not caminho:
            return

        try:
            from relatorios.generator import RelatorioGenerator
            colunas = self._resultado_atual.colunas
            dados = [dict(zip(colunas, linha)) for linha in self._resultado_atual.linhas]
            titulo = self._resultado_atual.titulo or (self.cbo_consulta.get() or "Consulta Imediata")
            RelatorioGenerator.gerar_pdf(dados, titulo, caminho)
            messagebox.showinfo(
                "Exportação Concluída",
                f"Exportação em PDF realizada com sucesso!\n\n"
                f"Total de registros exportados: {len(dados)}\n"
                f"Arquivo: {os.path.basename(caminho)}",
                parent=self
            )
            self.lbl_status.config(text=f"Exportado com sucesso para {os.path.basename(caminho)}.", foreground="#2e7d32")
        except Exception as exc:
            messagebox.showerror("Erro de Exportação PDF", f"Falha ao exportar PDF:\n{exc}", parent=self)

    def retornar(self):
        """Fecha a janela ou frame atual."""
        top = self.winfo_toplevel()
        if top != self:
            top.destroy()


def abrir_consultas_imediatas(parent, usuario: str = ""):
    """
    Função auxiliar para abrir a janela de Consultas Imediatas vinculada ao ícone do funil (<F4>).
    """
    top = tk.Toplevel(parent)
    top.title("Utilitário de Execução de Consultas Imediatas - GeoAlvo")
    top.minsize(800, 500)
    centralizar_janela(top, parent, 1100, 680)

    # Configura ícone oficial da aplicação
    caminho_icone = obter_caminho_recurso(os.path.join("Imagens", "GeoApolo_Icon.ico"))
    if os.path.exists(caminho_icone):
        try:
            top.iconbitmap(caminho_icone)
        except Exception:
            pass

    view = ConsultasImediatasView(top, usuario=usuario)
    view.pack(fill=tk.BOTH, expand=True)

    # Teclas de atalho locais
    top.bind("<F5>", lambda e: view.executar_consulta())
    top.bind("<Escape>", lambda e: view.retornar())
    return view
