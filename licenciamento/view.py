"""
Interfaces Gráficas para Licenciamento, Manutenção de Versões e Novidades.
GeoApolo V5
Clean Architecture: Views desacopladas em Tkinter/ttk com suporte a execução headless.
"""

from datetime import date
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from .models import LicencaDTO, VersaoSistemaDTO
from .service import LicenciamentoService

logger = logging.getLogger(__name__)


class ValidacaoLicencaView(ttk.Frame):
    """Tela de Validação e Ativação de Licenças do GeoApolo/GeoAlvo."""

    def __init__(self, parent=None, service: Optional[LicenciamentoService] = None, connection=None, usuario: str = ""):
        super().__init__(parent)
        self.service = service
        self.connection = connection
        self.usuario_logado = usuario

        if not self.usuario_logado:
            try:
                from logon import sessao_usuario_atual
                self.usuario_logado = (
                    sessao_usuario_atual.get("login")
                    or sessao_usuario_atual.get("usucod_apolo")
                    or sessao_usuario_atual.get("codigo_usuario")
                    or ""
                )
            except Exception:
                self.usuario_logado = ""

        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from .repository import LicenciamentoRepository
                conn = connection or obter_conexao_banco()
                self.service = LicenciamentoService(LicenciamentoRepository(conn))
            except Exception:
                pass

        self._setup_ui()
        if self.service:
            self.verificar_status_licenca()

    def _setup_ui(self):
        # Cabeçalho
        header = ttk.Frame(self, padding=(15, 12))
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Validação de Licença & Segurança",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
        ).pack(side=tk.LEFT)

        ttk.Label(
            header,
            text="Verificação de autenticidade, vigência e ativação de módulos",
            font=("Segoe UI", 9),
            foreground="#6B7280",
        ).pack(side=tk.LEFT, padx=15)

        # Container Principal
        container = ttk.Frame(self, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Status Card
        card_status = ttk.LabelFrame(container, text=" Situação da Licença ", padding=12)
        card_status.pack(fill=tk.X, pady=(0, 15))

        grid_card = ttk.Frame(card_status)
        grid_card.pack(fill=tk.X)

        ttk.Label(grid_card, text="Identificador / Palavra-Chave:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=3)
        self.lbl_id_palavra = ttk.Label(grid_card, text="-", font=("Segoe UI", 9))
        self.lbl_id_palavra.grid(row=0, column=1, sticky=tk.W, padx=10, pady=3)

        ttk.Label(grid_card, text="Vigência da Licença:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=3)
        self.lbl_vigencia = ttk.Label(grid_card, text="-", font=("Segoe UI", 9))
        self.lbl_vigencia.grid(row=1, column=1, sticky=tk.W, padx=10, pady=3)

        ttk.Label(grid_card, text="Dias Restantes:", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=3)
        self.lbl_dias = ttk.Label(grid_card, text="-", font=("Segoe UI", 9, "bold"))
        self.lbl_dias.grid(row=2, column=1, sticky=tk.W, padx=10, pady=3)

        ttk.Label(grid_card, text="Status Atual:", font=("Segoe UI", 9, "bold")).grid(row=3, column=0, sticky=tk.W, pady=3)
        self.lbl_status = ttk.Label(grid_card, text="Não verificado", font=("Segoe UI", 10, "bold"), foreground="#6B7280")
        self.lbl_status.grid(row=3, column=1, sticky=tk.W, padx=10, pady=3)

        btn_verificar = ttk.Button(card_status, text="🔄 Verificar Licença Agora", command=self.verificar_status_licenca)
        btn_verificar.pack(anchor=tk.E, pady=(8, 0))

        # Ativação Card
        card_ativacao = ttk.LabelFrame(container, text=" Ativação / Desbloqueio de Módulos ", padding=12)
        card_ativacao.pack(fill=tk.X)

        ttk.Label(
            card_ativacao,
            text="Caso sua licença esteja vencida ou próxima da expiração, insira a chave fornecida pelo suporte:",
            font=("Segoe UI", 9),
        ).pack(anchor=tk.W, pady=(0, 8))

        box_chave = ttk.Frame(card_ativacao)
        box_chave.pack(fill=tk.X)

        ttk.Label(box_chave, text="Chave de Ativação:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        self.ent_chave = ttk.Entry(box_chave, width=35, font=("Consolas", 10))
        self.ent_chave.pack(side=tk.LEFT, padx=10)

        btn_ativar = ttk.Button(box_chave, text="🔑 Ativar Licença", command=self.ativar_licenca)
        btn_ativar.pack(side=tk.LEFT)

        # Rotina herdada do Delphi (Tfrmabout): visível para o usuário JULIO / ADMIN / cód 3
        usr = str(self.usuario_logado).strip().upper()
        if usr in ("JULIO", "ADMIN", "3", "003"):
            self._montar_painel_admin_julio(container)

    def _montar_painel_admin_julio(self, container):
        """Painel exclusivo do usuário JULIO para consulta e descriptografia de senhas de usuários ativos."""
        card_julio = ttk.LabelFrame(
            container,
            text=" 🔒 Administração de Senhas de Usuários (Acesso Restrito: JULIO) ",
            padding=12
        )
        card_julio.pack(fill=tk.X, pady=(15, 0))

        ttk.Label(
            card_julio,
            text="Selecione um usuário ativo para visualizar a senha cifrada e executar a descriptografia:",
            font=("Segoe UI", 9),
            foreground="#334155"
        ).pack(anchor=tk.W, pady=(0, 8))

        grid = ttk.Frame(card_julio)
        grid.pack(fill=tk.X, pady=2)

        ttk.Label(grid, text="Usuário Ativo:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=4)
        self.cbo_julio_usuarios = ttk.Combobox(
            grid,
            state="readonly",
            width=30,
            font=("Segoe UI", 9),
            postcommand=self._on_julio_cbo_postcommand
        )
        self.cbo_julio_usuarios.grid(row=0, column=1, sticky=tk.W, padx=10, pady=4)
        self.cbo_julio_usuarios.bind("<<ComboboxSelected>>", self._on_julio_usuario_selected)

        ttk.Label(grid, text="Senha Criptografada:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=4)
        self.ent_julio_senha_cripto = ttk.Entry(grid, width=32, font=("Consolas", 10))
        self.ent_julio_senha_cripto.grid(row=1, column=1, sticky=tk.W, padx=10, pady=4)

        self.btn_julio_decript = ttk.Button(
            grid,
            text="🔓 Descriptografar",
            command=self._executar_decriptografia_julio
        )
        self.btn_julio_decript.grid(row=1, column=2, sticky=tk.W, padx=6, pady=4)

        ttk.Label(grid, text="Senha Descriptografada:", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=4)
        self.lbl_julio_senha_plana = ttk.Label(grid, text="", font=("Consolas", 10, "bold"), foreground="#1D4ED8")
        self.lbl_julio_senha_plana.grid(row=2, column=1, sticky=tk.W, padx=10, pady=4)

        self._senha_descriptografada_cache = None
        self._map_usuarios_julio = {}
        self._carregar_usuarios_ativos_julio()

    def _on_julio_cbo_postcommand(self):
        """Recarrega os usuários se o combobox estiver vazio ao abrir o dropdown."""
        if not self.cbo_julio_usuarios.get() and not self.cbo_julio_usuarios["values"]:
            self._carregar_usuarios_ativos_julio()

    def _carregar_usuarios_ativos_julio(self):
        """Carrega a lista de usuários ativos no combobox do usuário JULIO."""
        try:
            from entidades.database import obter_conexao_banco
            conn = self.connection or getattr(getattr(self.service, "_repo", None), "_conn", None) or obter_conexao_banco()
            cur = conn.cursor()
            rows = []
            has_senha_alvo = True
            try:
                cur.execute(
                    "SELECT login, senha, senha_alvo FROM USER_geoapolo_usuarios "
                    "WHERE (UPPER(flagativo) IN ('A', 'S') OR flagativo IS NULL OR flagativo = '') "
                    "ORDER BY login ASC"
                )
                rows = cur.fetchall()
            except Exception:
                has_senha_alvo = False
                cur.execute(
                    "SELECT login, senha FROM USER_geoapolo_usuarios "
                    "WHERE (UPPER(flagativo) IN ('A', 'S') OR flagativo IS NULL OR flagativo = '') "
                    "ORDER BY login ASC"
                )
                rows = cur.fetchall()

            self._map_usuarios_julio = {}
            for r in rows:
                if not r or not r[0]:
                    continue
                login = str(r[0]).strip()
                senha_geo = str(r[1] or "").strip()
                senha_alvo = str(r[2] or "").strip() if has_senha_alvo and len(r) > 2 else ""
                self._map_usuarios_julio[login] = (senha_geo, senha_alvo)

            logins = sorted(list(self._map_usuarios_julio.keys()))
            self.cbo_julio_usuarios["values"] = logins
            if logins:
                curr = self.cbo_julio_usuarios.get().strip()
                if curr in logins:
                    self.cbo_julio_usuarios.set(curr)
                else:
                    self.cbo_julio_usuarios.current(0)
                self._on_julio_usuario_selected()
        except Exception as exc:
            logger.error("Erro ao carregar usuários para rotina do JULIO: %s", exc)
            print(f"Erro ao carregar usuários para rotina do JULIO: {exc}")

    def _on_julio_usuario_selected(self, event=None):
        """Atualiza o campo com a senha criptografada do usuário selecionado."""
        self._senha_descriptografada_cache = None
        login = self.cbo_julio_usuarios.get().strip()
        par_senhas = self._map_usuarios_julio.get(login, ("", ""))
        if isinstance(par_senhas, tuple):
            senha_geo, senha_alvo = par_senhas
        else:
            senha_geo, senha_alvo = str(par_senhas or ""), ""

        # Prioriza senha Geo; se vazia, exibe senha Alvo
        senha_exibicao = senha_geo if senha_geo else senha_alvo
        self.ent_julio_senha_cripto.delete(0, tk.END)
        self.ent_julio_senha_cripto.insert(0, senha_exibicao)
        self.lbl_julio_senha_plana.config(text="")

    def _executar_decriptografia_julio(self):
        """Descriptografa a senha do usuário selecionado ou o texto cifrado no campo sem comparações."""
        login = self.cbo_julio_usuarios.get().strip()
        texto_campo = self.ent_julio_senha_cripto.get().strip()

        # Se já foi descriptografada e o campo já possui o valor plano do cache
        cache = getattr(self, "_senha_descriptografada_cache", None)
        if cache is not None and texto_campo == cache:
            self.lbl_julio_senha_plana.config(text=f"👉 {cache}")
            return

        # Obter senhas cadastradas para o usuário selecionado
        par_senhas = self._map_usuarios_julio.get(login, ("", ""))
        if isinstance(par_senhas, tuple):
            senha_geo_db, senha_alvo_db = par_senhas
        else:
            senha_geo_db, senha_alvo_db = str(par_senhas or ""), ""

        # Se o usuário não estiver no mapa ou se o banco não tiver sido consultado previamente
        if not senha_geo_db and not senha_alvo_db and login:
            try:
                from entidades.database import obter_conexao_banco
                conn = self.connection or getattr(getattr(self.service, "_repo", None), "_conn", None) or obter_conexao_banco()
                cur = conn.cursor()
                try:
                    cur.execute("SELECT senha, senha_alvo FROM USER_geoapolo_usuarios WHERE login = ?", (login,))
                    row = cur.fetchone()
                    if row:
                        senha_geo_db = str(row[0] or "").strip()
                        senha_alvo_db = str(row[1] or "").strip() if len(row) > 1 else ""
                except Exception:
                    cur.execute("SELECT senha FROM USER_geoapolo_usuarios WHERE login = ?", (login,))
                    row = cur.fetchone()
                    if row:
                        senha_geo_db = str(row[0] or "").strip()
            except Exception as exc:
                logger.warning("Falha ao consultar senha pontual de %s: %s", login, exc)

        from core.criptografia import decriptografia

        # Se o texto do campo foi alterado manualmente ou informado avulso
        if texto_campo and texto_campo not in (senha_geo_db, senha_alvo_db):
            try:
                senha_dec = decriptografia(32, texto_campo)
                self.ent_julio_senha_cripto.delete(0, tk.END)
                self.ent_julio_senha_cripto.insert(0, senha_dec)
                self._senha_descriptografada_cache = senha_dec
                self.lbl_julio_senha_plana.config(text=f"👉 {senha_dec}")
            except Exception as exc:
                messagebox.showerror("Erro", f"Não foi possível descriptografar a senha: {exc}", parent=self)
            return

        try:
            senha_dec = ""
            if senha_geo_db:
                senha_dec = decriptografia(32, senha_geo_db)
            elif senha_alvo_db:
                senha_dec = decriptografia(35, senha_alvo_db)
            elif texto_campo:
                senha_dec = decriptografia(32, texto_campo)

            if senha_dec:
                self.ent_julio_senha_cripto.delete(0, tk.END)
                self.ent_julio_senha_cripto.insert(0, senha_dec)
                self._senha_descriptografada_cache = senha_dec
                self.lbl_julio_senha_plana.config(text=f"👉 {senha_dec}")
            else:
                self._senha_descriptografada_cache = None
                if login:
                    messagebox.showinfo("Senha", f"O usuário '{login}' não possui senha cadastrada ou está vazia.", parent=self)
                    self.lbl_julio_senha_plana.config(text="(sem senha cadastrada)")
                else:
                    messagebox.showinfo("Senha", "Selecione um usuário para decriptografar a senha.", parent=self)
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível descriptografar a senha: {exc}", parent=self)

    def verificar_status_licenca(self):
        if not self.service:
            return

        try:
            res = self.service.validar_licenca_atual()
            if res.licenca:
                self.lbl_id_palavra.config(text=res.licenca.id_palavra or "(Padrão)")
                dt_ini_str = res.licenca.data_inicial.strftime("%d/%m/%Y") if res.licenca.data_inicial else "?"
                dt_fim_str = res.licenca.data_final.strftime("%d/%m/%Y") if res.licenca.data_final else "?"
                self.lbl_vigencia.config(text=f"{dt_ini_str} até {dt_fim_str}")
            else:
                self.lbl_id_palavra.config(text="-")
                self.lbl_vigencia.config(text="-")

            self.lbl_dias.config(text=f"{res.dias_restantes} dia(s)")

            if res.status == "OK":
                self.lbl_status.config(text="✅ Licença Ativa e Regular", foreground="#059669")
            elif res.status == "AVISO_EXPIRACAO":
                self.lbl_status.config(text=f"⚠️ Licença Próxima do Vencimento ({res.dias_restantes} dias)", foreground="#D97706")
            elif res.status == "BLOQUEADA":
                self.lbl_status.config(text="❌ Licença Bloqueada / Vencida", foreground="#DC2626")
            elif res.status == "NAO_ATIVADA":
                self.lbl_status.config(text="⚠️ Chave do Período Não Ativada", foreground="#D97706")
            else:
                self.lbl_status.config(text=f"⚠️ {res.mensagem}", foreground="#6B7280")
        except Exception as exc:
            if hasattr(self, "lbl_status") and self.lbl_status:
                self.lbl_status.config(text=f"⚠️ {exc}", foreground="#DC2626")

    def ativar_licenca(self):
        if not self.service:
            return
        chave = self.ent_chave.get().strip()
        if not chave:
            messagebox.showwarning("Aviso", "Por favor, digite a chave de ativação fornecida.")
            return

        hoje = date.today()
        # Obtém a palavra da licença atual ou padrão
        res_check = self.service.validar_licenca_atual()
        id_palavra = res_check.licenca.id_palavra if res_check.licenca else "LICENCA"

        res = self.service.ativar_licenca_com_chave(id_palavra, chave, hoje.month, hoje.year)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.ent_chave.delete(0, tk.END)
            self.verificar_status_licenca()
        else:
            messagebox.showerror("Falha na Ativação", res.mensagem)


class ManutencaoVersoesView(ttk.Frame):
    """Tela de Manutenção e Cadastro de Novas Versões do GeoApolo."""

    def __init__(self, parent=None, service: Optional[LicenciamentoService] = None, connection=None):
        super().__init__(parent)
        self.service = service

        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from .repository import LicenciamentoRepository
                conn = connection or obter_conexao_banco()
                self.service = LicenciamentoService(LicenciamentoRepository(conn))
            except Exception:
                pass

        self._setup_ui()
        if self.service:
            self.carregar_versoes()

    def _setup_ui(self):
        # Header
        header = ttk.Frame(self, padding=(12, 10))
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Manutenção de Versões do GeoApolo",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
        ).pack(side=tk.LEFT)

        ttk.Label(
            header,
            text="Registro de releases, notas de atualização e controle de liberação",
            font=("Segoe UI", 9),
            foreground="#6B7280",
        ).pack(side=tk.LEFT, padx=15)

        # PanedWindow
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Grid Versões
        frame_grid = ttk.Frame(paned, padding=5)
        paned.add(frame_grid, weight=3)

        cols = ("versao", "data", "status")
        self.tree = ttk.Treeview(frame_grid, columns=cols, show="headings", height=15)
        self.tree.heading("versao", text="Versão")
        self.tree.heading("data", text="Data Lançamento")
        self.tree.heading("status", text="Status")

        self.tree.column("versao", width=90, anchor=tk.CENTER)
        self.tree.column("data", width=110, anchor=tk.CENTER)
        self.tree.column("status", width=110, anchor=tk.CENTER)

        scroll = ttk.Scrollbar(frame_grid, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self._ao_selecionar_versao)

        # Formulário Lateral
        frame_form = ttk.LabelFrame(paned, text=" Dados da Versão ", padding=12)
        paned.add(frame_form, weight=4)

        grid_top = ttk.Frame(frame_form)
        grid_top.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(grid_top, text="Versão (Ex: 5.0.1):", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ent_versao = ttk.Entry(grid_top, width=15)
        self.ent_versao.grid(row=0, column=1, sticky=tk.W, padx=8, pady=2)

        ttk.Label(grid_top, text="Data Lançamento:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.ent_data = ttk.Entry(grid_top, width=15)
        self.ent_data.grid(row=1, column=1, sticky=tk.W, padx=8, pady=2)

        ttk.Label(grid_top, text="Status da Versão:", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.cbo_status = ttk.Combobox(grid_top, values=["Liberada", "Não Liberada"], state="readonly", width=13)
        self.cbo_status.grid(row=2, column=1, sticky=tk.W, padx=8, pady=2)
        self.cbo_status.set("Não Liberada")

        ttk.Label(frame_form, text="Novidades e Notas da Versão (Release Notes):", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(8, 2))
        self.txt_novidades = tk.Text(frame_form, height=10, wrap=tk.WORD, font=("Segoe UI", 9))
        self.txt_novidades.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Botões
        bar_btns = ttk.Frame(frame_form)
        bar_btns.pack(fill=tk.X)

        ttk.Button(bar_btns, text="Novo", command=self._novo_registro).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar_btns, text="Salvar", command=self._salvar_versao).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar_btns, text="Excluir", command=self._excluir_versao).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar_btns, text="Limpar", command=self._limpar_campos).pack(side=tk.RIGHT, padx=2)

    def carregar_versoes(self):
        if not self.service:
            return
        versoes = self.service.listar_versoes()
        self.tree.delete(*self.tree.get_children())
        for v in versoes:
            status_desc = "Liberada" if v.is_liberada else "Não Liberada"
            self.tree.insert("", tk.END, values=(v.idversao, v.data_lancamento, status_desc))

    def _ao_selecionar_versao(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0])["values"]
        idversao = str(vals[0])

        if self.service:
            v = self.service.obter_versao(idversao)
            if v:
                self.ent_versao.delete(0, tk.END)
                self.ent_versao.insert(0, v.idversao)
                self.ent_data.delete(0, tk.END)
                self.ent_data.insert(0, v.data_lancamento)
                self.cbo_status.set("Liberada" if v.is_liberada else "Não Liberada")
                self.txt_novidades.delete("1.0", tk.END)
                self.txt_novidades.insert("1.0", v.textonovaversao)

    def _limpar_campos(self):
        self.ent_versao.delete(0, tk.END)
        self.ent_data.delete(0, tk.END)
        self.cbo_status.set("Não Liberada")
        self.txt_novidades.delete("1.0", tk.END)
        self.ent_versao.focus_set()

    def _novo_registro(self):
        self._limpar_campos()
        self.ent_data.insert(0, date.today().strftime("%d/%m/%Y"))
        self.ent_versao.focus_set()

    def _salvar_versao(self):
        if not self.service:
            return
        v_id = self.ent_versao.get().strip()
        v_data = self.ent_data.get().strip()
        v_status = "S" if self.cbo_status.get() == "Liberada" else "N"
        v_texto = self.txt_novidades.get("1.0", tk.END).strip()

        dto = VersaoSistemaDTO(
            idversao=v_id,
            data_lancamento=v_data,
            textonovaversao=v_texto,
            statusversao=v_status,
        )

        res = self.service.salvar_versao(dto)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.carregar_versoes()
        else:
            messagebox.showerror("Erro", res.mensagem)

    def _excluir_versao(self):
        if not self.service:
            return
        v_id = self.ent_versao.get().strip()
        if not v_id:
            messagebox.showwarning("Aviso", "Selecione uma versão válida para exclusão.")
            return

        if not messagebox.askyesno("Confirmação", f"Deseja realmente excluir o registro da versão {v_id}?"):
            return

        res = self.service.excluir_versao(v_id)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.carregar_versoes()
            self._limpar_campos()
        else:
            messagebox.showerror("Erro", res.mensagem)


class NovidadesVersaoDialog(tk.Toplevel):
    """Janela modal para exibição de novidades da versão ao usuário."""

    def __init__(self, parent, idversao: str, usucod: str, texto_novidades: str, service: LicenciamentoService):
        super().__init__(parent)
        self.idversao = idversao
        self.usucod = usucod
        self.service = service

        self.title(f"Novidades da Versão {idversao} - GeoApolo")
        self.geometry("640x480")
        self.minsize(500, 360)
        self.transient(parent)
        self.grab_set()

        self._setup_ui(texto_novidades)

    def _setup_ui(self, texto: str):
        header = ttk.Frame(self, padding=12)
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text=f"Novidades e Atualizações da Versão {self.idversao}",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A",
        ).pack(anchor=tk.W)

        ttk.Label(
            header,
            text="Confira abaixo as principais melhorias e correções implementadas nesta release:",
            font=("Segoe UI", 9),
            foreground="#4B5563",
        ).pack(anchor=tk.W, pady=(4, 0))

        frame_txt = ttk.Frame(self, padding=12)
        frame_txt.pack(fill=tk.BOTH, expand=True)

        txt = tk.Text(frame_txt, wrap=tk.WORD, font=("Segoe UI", 10), padx=8, pady=8)
        scroll = ttk.Scrollbar(frame_txt, orient=tk.VERTICAL, command=txt.yview)
        txt.configure(yscrollcommand=scroll.set)

        txt.insert("1.0", texto)
        txt.configure(state=tk.DISABLED)

        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        footer = ttk.Frame(self, padding=12)
        footer.pack(fill=tk.X)

        btn_ok = ttk.Button(footer, text="Entendi / Continuar", command=self._confirmar)
        btn_ok.pack(side=tk.RIGHT)

    def _confirmar(self):
        if self.service:
            self.service.confirmar_leitura_versao(self.idversao, self.usucod)
        self.destroy()


def abrir_validacao_licenca(parent, connection=None, usuario: str = ""):
    """Abre a tela de Validação de Licenças em janela TopLevel."""
    from core import centralizar_janela
    win = tk.Toplevel(parent)
    win.title("Validação de Licenças - GeoAlvo")
    win.minsize(560, 360)
    centralizar_janela(win, parent, 680, 520)
    view = ValidacaoLicencaView(win, connection=connection, usuario=usuario)
    view.pack(fill=tk.BOTH, expand=True)
    return win


def abrir_manutencao_versoes(parent, connection=None):
    """Abre a tela de Manutenção de Versões em janela TopLevel."""
    from core import centralizar_janela
    win = tk.Toplevel(parent)
    win.title("Manutenção de Versões do GeoApolo - GeoAlvo")
    win.minsize(700, 400)
    centralizar_janela(win, parent, 860, 520)
    view = ManutencaoVersoesView(win, connection=connection)
    view.pack(fill=tk.BOTH, expand=True)
    return win


def verificar_novidades_ao_iniciar(parent, versao_atual: str, usucod: str, connection=None):
    """Verifica e exibe novidades pendentes da versão para o usuário."""
    try:
        from entidades.database import obter_conexao_banco
        from .repository import LicenciamentoRepository
        conn = connection or obter_conexao_banco()
        srv = LicenciamentoService(LicenciamentoRepository(conn))
        texto = srv.obter_novidades_pendentes(versao_atual, usucod)
        if texto:
            NovidadesVersaoDialog(parent, versao_atual, usucod, texto, srv)
    except Exception:
        pass
