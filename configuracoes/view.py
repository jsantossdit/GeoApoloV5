"""
Interface Gráfica (Tkinter / ttk) para Parâmetros e Configurações Gerais do Sistema.
Layout corporativo profissional no padrão visual GeoAlvo.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import logging
from typing import Optional, Dict, Any

from configuracoes.models import ResultadoOperacao
from configuracoes.repository import ConfiguracoesRepository
from configuracoes.service import ConfiguracoesService
from entidades.database import obter_conexao_banco

logger = logging.getLogger(__name__)


class ConfiguracoesView(tk.Toplevel):
    """Janela de Configurações Gerais e Parâmetros do GeoAlvo."""

    def __init__(self, parent=None, connection=None, empresa_codigo: str = "001"):
        super().__init__(parent)
        self.title("Parâmetros e Configurações Gerais - GeoAlvo")
        self.geometry("1080x660")
        self.minsize(900, 520)

        self._empresa_codigo = empresa_codigo
        self._centralizar_janela(1080, 660)
        self._aplicar_icone()

        self._conn = connection
        if self._conn is None:
            try:
                self._conn = obter_conexao_banco()
            except Exception as exc:
                messagebox.showwarning(
                    "Aviso de Conexão",
                    f"Não foi possível conectar automaticamente ao banco:\n{exc}\n\nConfigure o banco no menu Configurações."
                )

        self._repo = ConfiguracoesRepository(self._conn) if self._conn else None
        self._service = ConfiguracoesService(self._repo) if self._repo else None

        self._config_atual: Dict[str, Any] = {}

        self._configurar_estilos()
        self._criar_interface()
        self._carregar_configuracoes()

        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<F2>", lambda e: self._salvar_configuracoes())

    def _centralizar_janela(self, largura: int, altura: int):
        self.update_idletasks()
        pos_x = (self.winfo_screenwidth() // 2) - (largura // 2)
        pos_y = (self.winfo_screenheight() // 2) - (altura // 2) - 20
        self.geometry(f"{largura}x{altura}+{max(pos_x, 0)}+{max(pos_y, 0)}")

    def _aplicar_icone(self):
        caminhos = [
            os.path.join(os.path.dirname(__file__), "..", "Imagens", "IconeRCC.png"),
            os.path.join(os.path.dirname(__file__), "..", "Imagens", "entidades.png"),
        ]
        for c in caminhos:
            if os.path.exists(c):
                try:
                    img = tk.PhotoImage(file=c)
                    self.iconphoto(False, img)
                    self._icon_ref = img
                    break
                except Exception:
                    pass

    def _configurar_estilos(self):
        style = ttk.Style()
        style.configure("Config.TLabel", font=("Segoe UI", 9))
        style.configure("ConfigHeader.TLabel", font=("Segoe UI", 9, "bold"), foreground="#1A365D")

    def _criar_interface(self):
        # 1. Header Banner Corporativo
        banner = tk.Frame(self, bg="#1A365D", height=58)
        banner.pack(side=tk.TOP, fill=tk.X)
        banner.pack_propagate(False)

        lbl_tit = tk.Label(
            banner,
            text="⚙ Parâmetros e Configurações do Sistema",
            font=("Segoe UI", 12, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
            anchor="w",
        )
        lbl_tit.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(8, 0))

        lbl_sub = tk.Label(
            banner,
            text="Diretórios do sistema, parâmetros de integração GeoApolo ↔ Alvo e configurações de rede",
            font=("Segoe UI", 8),
            bg="#1A365D",
            fg="#CBD5E0",
            anchor="w",
        )
        lbl_sub.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(1, 6))

        # 2. Notebook de Abas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=12, pady=8)

        # Aba 1: Caminhos
        self.tab_caminhos = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.tab_caminhos, text="📁 Pastas e Diretórios do Sistema")
        self._criar_aba_caminhos()

        # Aba 2: Integrações
        self.tab_integracoes = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.tab_integracoes, text="🔄 Regras de Integração & Entidades")
        self._criar_aba_integracoes()

        # Aba 3: E-mails
        self.tab_email = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.tab_email, text="✉ Servidores de E-mail & Alertas")
        self._criar_aba_email()

        # 3. Rodapé
        bottom_frame = tk.Frame(self, bg="#E2E8F0", height=46, bd=1, relief=tk.GROOVE)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        bottom_frame.pack_propagate(False)

        btn_box = tk.Frame(bottom_frame, bg="#E2E8F0")
        btn_box.pack(side=tk.LEFT, padx=10, pady=7)

        ttk.Button(btn_box, text="💾 Salvar Configurações (F2)", command=self._salvar_configuracoes).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_box, text="🔄 Recarregar", command=self._carregar_configuracoes).pack(side=tk.LEFT, padx=4)

        btn_fechar = ttk.Button(bottom_frame, text="🚪 Fechar (Esc)", command=self.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=12, pady=7)

        self.lbl_status = tk.Label(
            bottom_frame,
            text=f"Empresa ativa: {self._empresa_codigo}",
            font=("Segoe UI", 9, "italic"),
            bg="#E2E8F0",
            fg="#4A5568",
        )
        self.lbl_status.pack(side=tk.RIGHT, padx=16)

    def _criar_campo_diretorio(self, parent, label_text: str, row: int):
        ttk.Label(parent, text=label_text, style="Config.TLabel").grid(row=row, column=0, sticky=tk.W, pady=6)
        entry = ttk.Entry(parent, width=65, font=("Segoe UI", 9))
        entry.grid(row=row, column=1, sticky=tk.W, padx=8, pady=6)
        btn = ttk.Button(parent, text="📂 Procurar", command=lambda e=entry: self._selecionar_pasta(e))
        btn.grid(row=row, column=2, padx=4, pady=6)
        return entry

    def _selecionar_pasta(self, entry: ttk.Entry):
        pasta = filedialog.askdirectory(title="Selecione a Pasta")
        if pasta:
            entry.delete(0, tk.END)
            entry.insert(0, os.path.normpath(pasta))

    def _criar_aba_caminhos(self):
        f = self.tab_caminhos
        self.edt_backup = self._criar_campo_diretorio(f, "Pasta de Backup do Sistema:", 0)
        self.edt_instalacao = self._criar_campo_diretorio(f, "Pasta de Instalação Local:", 1)
        self.edt_novas_versoes = self._criar_campo_diretorio(f, "Local de Novas Versões:", 2)
        self.edt_instalador = self._criar_campo_diretorio(f, "Local do Instalador de Versões:", 3)
        self.edt_docti = self._criar_campo_diretorio(f, "Documentação de TI:", 4)
        self.edt_inventario = self._criar_campo_diretorio(f, "Pasta de Inventário de TI:", 5)
        self.edt_convenio = self._criar_campo_diretorio(f, "Arquivos de Convênios:", 6)
        self.edt_alvo_loja = self._criar_campo_diretorio(f, "Base Alvo Loja:", 7)

    def _criar_aba_integracoes(self):
        f = self.tab_integracoes

        ttk.Label(f, text="Integração de Entidades com Alvo:", style="Config.TLabel").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.combo_integra = ttk.Combobox(f, values=["Integra", "Mescla", "Não Integra"], state="readonly", width=20)
        self.combo_integra.set("Integra")
        self.combo_integra.grid(row=0, column=1, sticky=tk.W, padx=8, pady=8)

        ttk.Label(f, text="Código Consumidor Final:", style="Config.TLabel").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.edt_consumidor_final = ttk.Entry(f, width=22, font=("Segoe UI", 9))
        self.edt_consumidor_final.grid(row=1, column=1, sticky=tk.W, padx=8, pady=8)

        ttk.Label(f, text="Código Origem Padrão:", style="Config.TLabel").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.edt_origem_padrao = ttk.Entry(f, width=22, font=("Segoe UI", 9))
        self.edt_origem_padrao.grid(row=2, column=1, sticky=tk.W, padx=8, pady=8)

        ttk.Label(f, text="Código Motivo de Ocorrência Padrão:", style="Config.TLabel").grid(row=3, column=0, sticky=tk.W, pady=8)
        self.edt_motivo_ocorrencia = ttk.Entry(f, width=22, font=("Segoe UI", 9))
        self.edt_motivo_ocorrencia.grid(row=3, column=1, sticky=tk.W, padx=8, pady=8)

        ttk.Label(f, text="Categoria Parceira Padrão:", style="Config.TLabel").grid(row=4, column=0, sticky=tk.W, pady=8)
        self.edt_parceira = ttk.Entry(f, width=22, font=("Segoe UI", 9))
        self.edt_parceira.grid(row=4, column=1, sticky=tk.W, padx=8, pady=8)

    def _criar_aba_email(self):
        f = self.tab_email

        ttk.Label(f, text="Servidor SMTP de Envio:", style="Config.TLabel").grid(row=0, column=0, sticky=tk.W, pady=6)
        self.edt_smtp_server = ttk.Entry(f, width=35, font=("Segoe UI", 9))
        self.edt_smtp_server.insert(0, "smtp.office365.com")
        self.edt_smtp_server.grid(row=0, column=1, sticky=tk.W, padx=8, pady=6)

        ttk.Label(f, text="Porta SMTP Envio:", style="Config.TLabel").grid(row=1, column=0, sticky=tk.W, pady=6)
        self.edt_smtp_porta = ttk.Entry(f, width=10, font=("Segoe UI", 9))
        self.edt_smtp_porta.insert(0, "587")
        self.edt_smtp_porta.grid(row=1, column=1, sticky=tk.W, padx=8, pady=6)

        ttk.Label(f, text="Servidor IMAP Recebimento:", style="Config.TLabel").grid(row=2, column=0, sticky=tk.W, pady=6)
        self.edt_imap_server = ttk.Entry(f, width=35, font=("Segoe UI", 9))
        self.edt_imap_server.insert(0, "outlook.office365.com")
        self.edt_imap_server.grid(row=2, column=1, sticky=tk.W, padx=8, pady=6)

        ttk.Label(f, text="Porta IMAP Recebimento:", style="Config.TLabel").grid(row=3, column=0, sticky=tk.W, pady=6)
        self.edt_imap_porta = ttk.Entry(f, width=10, font=("Segoe UI", 9))
        self.edt_imap_porta.insert(0, "993")
        self.edt_imap_porta.grid(row=3, column=1, sticky=tk.W, padx=8, pady=6)

        ttk.Label(
            f,
            text="Nota: As senhas e credenciais devem ser mantidas em segurança no Credential Manager do Windows.",
            font=("Segoe UI", 8, "italic"),
            foreground="#718096",
        ).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(15, 0))

    def _carregar_configuracoes(self):
        if not self._service:
            return
        try:
            self._config_atual = self._service.obter_parametros(self._empresa_codigo)

            def set_entry(entry, val):
                entry.delete(0, tk.END)
                entry.insert(0, str(val or ""))

            set_entry(self.edt_backup, self._config_atual.get("caminhobackupsistema"))
            set_entry(self.edt_instalacao, self._config_atual.get("instalacaolocal"))
            set_entry(self.edt_novas_versoes, self._config_atual.get("localnovasversoes"))
            set_entry(self.edt_instalador, self._config_atual.get("localinstaladorversoes"))
            set_entry(self.edt_docti, self._config_atual.get("caminhodocti"))
            set_entry(self.edt_inventario, self._config_atual.get("caminhoinventario"))
            set_entry(self.edt_convenio, self._config_atual.get("caminhoarquivoconvenio"))
            set_entry(self.edt_alvo_loja, self._config_atual.get("caminhobasealvoloja"))

            integra_val = self._config_atual.get("integra_entidades_apolo", "Integra")
            if integra_val in ["Integra", "Mescla", "Não Integra"]:
                self.combo_integra.set(integra_val)

            set_entry(self.edt_consumidor_final, self._config_atual.get("entcod_consumidorfinal"))
            set_entry(self.edt_origem_padrao, self._config_atual.get("origcodestr"))
            set_entry(self.edt_motivo_ocorrencia, self._config_atual.get("motocorcodestr"))
            set_entry(self.edt_parceira, self._config_atual.get("entcategparceira"))

            self.lbl_status.config(text=f"Configurações carregadas da empresa {self._empresa_codigo}.")
        except Exception as exc:
            logger.exception("Erro ao carregar configurações: %s", exc)
            messagebox.showerror("Erro", f"Erro ao carregar configurações:\n{exc}")

    def _salvar_configuracoes(self):
        if not self._service:
            return

        dados = {
            "caminhobackupsistema": self.edt_backup.get().strip(),
            "instalacaolocal": self.edt_instalacao.get().strip(),
            "localnovasversoes": self.edt_novas_versoes.get().strip(),
            "localinstaladorversoes": self.edt_instalador.get().strip(),
            "caminhodocti": self.edt_docti.get().strip(),
            "caminhoinventario": self.edt_inventario.get().strip(),
            "caminhoarquivoconvenio": self.edt_convenio.get().strip(),
            "caminhobasealvoloja": self.edt_alvo_loja.get().strip(),
            "integra_entidades_apolo": self.combo_integra.get(),
            "entcod_consumidorfinal": self.edt_consumidor_final.get().strip(),
            "origcodestr": self.edt_origem_padrao.get().strip(),
            "motocorcodestr": self.edt_motivo_ocorrencia.get().strip(),
            "entcategparceira": self.edt_parceira.get().strip(),
        }

        res: ResultadoOperacao = self._service.salvar_parametros(dados, self._empresa_codigo)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self._carregar_configuracoes()
        else:
            messagebox.showerror("Erro ao Salvar", res.mensagem)
