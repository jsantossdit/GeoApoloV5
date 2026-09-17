"""
Interfaces Gráficas para Logon, Autenticação e Sobre o Sistema.
GeoApolo V5
Clean Architecture: View desacoplada em Tkinter/ttk com suporte a execução headless.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

from .models import CredenciaisDTO, UsuarioSessaoDTO
from .service import AutenticacaoService


class LoginView(ttk.Frame):
    """Tela de Logon para autenticação e escolha da empresa ativa."""

    def __init__(
        self,
        parent=None,
        service: Optional[AutenticacaoService] = None,
        on_success: Optional[Callable[[UsuarioSessaoDTO], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
        connection=None,
    ):
        super().__init__(parent)
        self.service = service
        self.on_success = on_success
        self.on_cancel = on_cancel

        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from .repository import AutenticacaoRepository
                from licenciamento import LicenciamentoService, LicenciamentoRepository
                conn = connection or obter_conexao_banco()
                lic_srv = LicenciamentoService(LicenciamentoRepository(conn))
                self.service = AutenticacaoService(AutenticacaoRepository(conn), licenciamento_service=lic_srv)
            except Exception:
                pass

        self._setup_ui()
        if self.service:
            self._carregar_empresas()

    def _setup_ui(self):
        # Header / Banner
        header = ttk.Frame(self, padding=15)
        header.pack(fill=tk.X)

        lbl_logo = ttk.Label(
            header,
            text="GeoAlvo ERP",
            font=("Segoe UI", 16, "bold"),
            foreground="#1E3A8A",
        )
        lbl_logo.pack(anchor=tk.CENTER)

        lbl_sub = ttk.Label(
            header,
            text="Sistema de Gestão Integrada & CRM - v5.0",
            font=("Segoe UI", 9),
            foreground="#6B7280",
        )
        lbl_sub.pack(anchor=tk.CENTER, pady=(2, 0))

        # Formulário Central
        frame_form = ttk.LabelFrame(self, text=" Autenticação de Usuário ", padding=15)
        frame_form.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        ttk.Label(frame_form, text="Usuário / Login:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.ent_login = ttk.Entry(frame_form, width=30)
        self.ent_login.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_form, text="Senha de Acesso:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.ent_senha = ttk.Entry(frame_form, width=30, show="*")
        self.ent_senha.pack(fill=tk.X, pady=(0, 10))
        self.ent_senha.bind("<Return>", lambda e: self._executar_login())

        ttk.Label(frame_form, text="Empresa Ativa:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        self.cbo_empresa = ttk.Combobox(frame_form, state="readonly", width=28)
        self.cbo_empresa.pack(fill=tk.X, pady=(0, 15))

        self.lbl_feedback = ttk.Label(frame_form, text="", font=("Segoe UI", 8), foreground="#DC2626")
        self.lbl_feedback.pack(anchor=tk.W, pady=(0, 10))

        # Botões
        bar_btns = ttk.Frame(frame_form)
        bar_btns.pack(fill=tk.X)

        btn_entrar = ttk.Button(bar_btns, text="Entrar no Sistema", command=self._executar_login)
        btn_entrar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        btn_cancelar = ttk.Button(bar_btns, text="Cancelar / Sair", command=self._cancelar)
        btn_cancelar.pack(side=tk.RIGHT, padx=(5, 0))

    def _carregar_empresas(self):
        if not self.service:
            return
        empresas = self.service.listar_empresas_disponiveis()
        opcoes = [f"{e['empcod']} - {e['empnome']}" for e in empresas]
        self.cbo_empresa["values"] = opcoes
        if opcoes:
            self.cbo_empresa.set(opcoes[0])

    def _executar_login(self):
        login = self.ent_login.get().strip()
        senha = self.ent_senha.get().strip()

        emp_sel = self.cbo_empresa.get().strip()
        empcod = emp_sel.split("-")[0].strip() if "-" in emp_sel else "01"

        cred = CredenciaisDTO(login=login, senha=senha, empcod=empcod)

        if self.service:
            res = self.service.autenticar(cred)
            if res.sucesso and res.sessao:
                self.lbl_feedback.config(text="")
                if self.on_success:
                    self.on_success(res.sessao)
            else:
                self.lbl_feedback.config(text=res.mensagem)
                messagebox.showerror("Falha na Autenticação", res.mensagem)
        else:
            # Fallback sem banco conectado
            sessao = UsuarioSessaoDTO(usucod="ADMIN", login=login, nome_usuario="Administrador", empcod=empcod)
            if self.on_success:
                self.on_success(sessao)

    def _cancelar(self):
        if self.on_cancel:
            self.on_cancel()


class SobreSistemaDialog(tk.Toplevel):
    """Janela 'Sobre o GeoAlvo / GeoApolo' com metadados do sistema e da estação."""

    def __init__(self, parent=None, service: Optional[AutenticacaoService] = None, connection=None):
        super().__init__(parent)
        self.title("Sobre o GeoAlvo")
        self.geometry("540x360")
        self.minsize(460, 300)
        self.transient(parent)
        self.service = service

        if self.service is None:
            try:
                from entidades.database import obter_conexao_banco
                from .repository import AutenticacaoRepository
                from licenciamento import LicenciamentoService, LicenciamentoRepository
                conn = connection or obter_conexao_banco()
                lic_srv = LicenciamentoService(LicenciamentoRepository(conn))
                self.service = AutenticacaoService(AutenticacaoRepository(conn), licenciamento_service=lic_srv)
            except Exception:
                pass

        self._setup_ui()

    def _setup_ui(self):
        info = self.service.obter_info_sistema() if self.service else {
            "sistema": "GeoAlvo / GeoApolo",
            "versao": "5.0.0",
            "build": "Build 2026.09.17",
            "estacao": "localhost",
            "ip": "127.0.0.1",
            "copyright": "© 2026 GeoApolo Tecnologia da Informação.",
            "suporte": "suporte@geoapolo.com.br",
        }

        header = ttk.Frame(self, padding=15)
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="GeoAlvo ERP & Gestão Integrada",
            font=("Segoe UI", 14, "bold"),
            foreground="#1E3A8A",
        ).pack(anchor=tk.W)

        ttk.Label(
            header,
            text=f"Versão {info.get('versao')} ({info.get('build')})",
            font=("Segoe UI", 9, "bold"),
            foreground="#4B5563",
        ).pack(anchor=tk.W, pady=(2, 0))

        content = ttk.LabelFrame(self, text=" Informações da Estação & Licença ", padding=12)
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        grid = ttk.Frame(content)
        grid.pack(fill=tk.BOTH, expand=True)

        ttk.Label(grid, text="Nome da Estação (Hostname):", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=3)
        ttk.Label(grid, text=info.get("estacao", "-")).grid(row=0, column=1, sticky=tk.W, padx=8, pady=3)

        ttk.Label(grid, text="Endereço IP da Máquina:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky=tk.W, pady=3)
        ttk.Label(grid, text=info.get("ip", "-")).grid(row=1, column=1, sticky=tk.W, padx=8, pady=3)

        ttk.Label(grid, text="Status da Licença:", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=3)
        status_lic = info.get("licenca_status", "Ativa")
        ttk.Label(grid, text=f"{status_lic} ({info.get('licenca_dias', 0)} dias restantes)").grid(row=2, column=1, sticky=tk.W, padx=8, pady=3)

        ttk.Label(grid, text="Suporte Técnico:", font=("Segoe UI", 9, "bold")).grid(row=3, column=0, sticky=tk.W, pady=3)
        ttk.Label(grid, text=info.get("suporte", "-")).grid(row=3, column=1, sticky=tk.W, padx=8, pady=3)

        footer = ttk.Frame(self, padding=12)
        footer.pack(fill=tk.X)

        ttk.Label(footer, text=info.get("copyright", ""), font=("Segoe UI", 8), foreground="#9CA3AF").pack(side=tk.LEFT)
        ttk.Button(footer, text="Fechar", command=self.destroy).pack(side=tk.RIGHT)


def abrir_sobre_sistema(parent, connection=None):
    """Abre a janela 'Sobre o GeoAlvo'."""
    dialog = SobreSistemaDialog(parent, connection=connection)
    dialog.grab_set()
    return dialog
