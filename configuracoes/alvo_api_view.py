"""
Interface Gráfica (Tkinter / ttk) para Configuração da Integração API Alvo.
Permite ao operador configurar o Token de Acesso, Período de Vigência (Data Inicial/Final),
URL Base do Web Service, testar a conectividade em tempo real e salvar de forma persistente.
"""

import os
import re
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable

from core import centralizar_janela, obter_caminho_recurso
from configuracoes.alvo_api_config import (
    AlvoAPIConfig,
    carregar_configuracao_alvo,
    salvar_configuracao_alvo,
    validar_status_token,
    testar_comunicacao_alvo,
    parse_data_br,
)


def _aplicar_mascara_data(event, widget):
    """Aplica formatação automática DD/MM/AAAA enquanto o usuário digita."""
    if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab", "Return", "ISO_Left_Tab"):
        return
    texto = widget.get()
    apenas_digitos = re.sub(r"\D", "", texto)[:8]
    if not apenas_digitos:
        return
    if len(apenas_digitos) <= 2:
        formatado = apenas_digitos
    elif len(apenas_digitos) <= 4:
        formatado = f"{apenas_digitos[:2]}/{apenas_digitos[2:]}"
    else:
        formatado = f"{apenas_digitos[:2]}/{apenas_digitos[2:4]}/{apenas_digitos[4:]}"
    if texto != formatado:
        widget.delete(0, tk.END)
        widget.insert(0, formatado)


class FrmConfiguracaoAPIAlvo(tk.Toplevel):
    """
    Formulário corporativo para Configuração do Token e Parâmetros da API Alvo (Riosoft).
    Garante controle de instância única e integração com o menu de configurações.
    """
    _instancia_ativa = None

    def __new__(cls, *args, **kwargs):
        if cls._instancia_ativa is not None and cls._instancia_ativa.winfo_exists():
            try:
                cls._instancia_ativa.deiconify()
                cls._instancia_ativa.lift()
                cls._instancia_ativa.focus_force()
            except Exception:
                pass
            return cls._instancia_ativa
        return super().__new__(cls)

    def __init__(
        self,
        parent=None,
        on_salvar_callback: Optional[Callable[[AlvoAPIConfig], None]] = None,
    ):
        if getattr(self, "_ja_inicializada", False):
            return
        super().__init__(parent)
        self._ja_inicializada = True
        FrmConfiguracaoAPIAlvo._instancia_ativa = self

        self.parent = parent
        self.on_salvar_callback = on_salvar_callback
        self.config_atual = carregar_configuracao_alvo()

        self.title("Configuração da Integração API Alvo - GeoAlvo")
        self.geometry("820x640")
        self.minsize(740, 560)
        centralizar_janela(self, parent, 820, 640)
        self._aplicar_icone()

        if parent:
            try:
                self.transient(parent)
                self.grab_set()
            except Exception:
                pass

        self._criar_interface()
        self._carregar_valores_na_tela()
        self._atualizar_badge_status()

        # Atalhos
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind("<Escape>", lambda e: self.destroy())
        self.bind("<F2>", lambda e: self.salvar())

    def _aplicar_icone(self):
        caminhos = [
            obter_caminho_recurso(os.path.join("Imagens", "IconeRCC.png")),
            obter_caminho_recurso(os.path.join("Imagens", "GeoApolo_Icon.ico")),
        ]
        for c in caminhos:
            if os.path.exists(c):
                try:
                    if c.endswith(".ico"):
                        self.iconbitmap(c)
                    else:
                        img = tk.PhotoImage(file=c)
                        self.iconphoto(False, img)
                        self._icon_ref = img
                    break
                except Exception:
                    pass

    def _criar_interface(self):
        # 1. Header Banner Corporativo
        banner = tk.Frame(self, bg="#1A365D", height=60)
        banner.pack(side=tk.TOP, fill=tk.X)
        banner.pack_propagate(False)

        lbl_tit = tk.Label(
            banner,
            text="🌐 Integração Web Service - API Alvo (Riosoft)",
            font=("Segoe UI", 12, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
            anchor="w",
        )
        lbl_tit.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(8, 0))

        lbl_sub = tk.Label(
            banner,
            text="Gerenciamento do token de autenticação, período de vigência e parâmetros do Web Service",
            font=("Segoe UI", 8),
            bg="#1A365D",
            fg="#CBD5E0",
            anchor="w",
        )
        lbl_sub.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(1, 6))

        # 2. Container Principal
        container = ttk.Frame(self, padding=(16, 12, 16, 12))
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Painel Status do Token (Badge dinâmico)
        self.frame_status = tk.Frame(container, bg="#F1F5F9", bd=1, relief=tk.SOLID, padx=12, pady=8)
        self.frame_status.pack(fill=tk.X, pady=(0, 10))

        self.lbl_status_badge = tk.Label(
            self.frame_status,
            text="⚪ Verificando status do token...",
            font=("Segoe UI", 10, "bold"),
            bg="#F1F5F9",
            fg="#334155",
            anchor="w",
        )
        self.lbl_status_badge.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Grupo 1: Token de Integração
        grp_token = ttk.LabelFrame(container, text=" Chave de Acesso / Token de Integração (Bearer / Riosoft-Token) ", padding=10)
        grp_token.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        lbl_token_dica = ttk.Label(
            grp_token,
            text="Cole abaixo o token de integração completo fornecido pelo administrador do Alvo:",
            font=("Segoe UI", 8, "italic"),
        )
        lbl_token_dica.pack(anchor=tk.W, pady=(0, 4))

        frame_txt = ttk.Frame(grp_token)
        frame_txt.pack(fill=tk.BOTH, expand=True)

        self.txt_token = tk.Text(
            frame_txt,
            height=4,
            wrap=tk.CHAR,
            font=("Consolas", 9),
            bg="#FFFFFF",
            fg="#0F172A",
            relief=tk.SOLID,
            bd=1,
        )
        scroll_txt = ttk.Scrollbar(frame_txt, orient=tk.VERTICAL, command=self.txt_token.yview)
        self.txt_token.config(yscrollcommand=scroll_txt.set)
        self.txt_token.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_txt.pack(side=tk.RIGHT, fill=tk.Y)

        self.txt_token.bind("<KeyRelease>", self._on_token_text_changed)

        # Barra de Ações do Token
        bar_token = ttk.Frame(grp_token)
        bar_token.pack(fill=tk.X, pady=(6, 0))

        ttk.Button(bar_token, text="📋 Colar da Área de Transferência", command=self._colar_token).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(bar_token, text="📄 Copiar Token", command=self._copiar_token).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(bar_token, text="🗑 Limpar", command=self._limpar_token).pack(side=tk.LEFT)

        self.lbl_tamanho_token = ttk.Label(bar_token, text="0 caracteres", font=("Segoe UI", 8))
        self.lbl_tamanho_token.pack(side=tk.RIGHT)

        # Grupo 2: Período de Vigência
        grp_validade = ttk.LabelFrame(container, text=" Período de Vigência e Validade do Token ", padding=10)
        grp_validade.pack(fill=tk.X, pady=(0, 10))

        row_val = ttk.Frame(grp_validade)
        row_val.pack(fill=tk.X)

        ttk.Label(row_val, text="Data Inicial de Validade:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.txt_dt_inicial = ttk.Entry(row_val, width=14, font=("Segoe UI", 9))
        self.txt_dt_inicial.pack(side=tk.LEFT, padx=(0, 20))
        self.txt_dt_inicial.bind("<KeyRelease>", lambda e: self._on_data_changed(e, self.txt_dt_inicial))

        ttk.Label(row_val, text="Data Final de Validade (Expiração):", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.txt_dt_final = ttk.Entry(row_val, width=14, font=("Segoe UI", 9))
        self.txt_dt_final.pack(side=tk.LEFT, padx=(0, 12))
        self.txt_dt_final.bind("<KeyRelease>", lambda e: self._on_data_changed(e, self.txt_dt_final))

        ttk.Label(
            grp_validade,
            text="* Formato: DD/MM/AAAA. O sistema emitirá avisos quando a data limite se aproximar.",
            font=("Segoe UI", 8, "italic"),
            foreground="#64748B",
        ).pack(anchor=tk.W, pady=(6, 0))

        # Grupo 3: Parâmetros de Conexão e Ambiente
        grp_params = ttk.LabelFrame(container, text=" Parâmetros de Conexão com o Web Service ", padding=10)
        grp_params.pack(fill=tk.X, pady=(0, 10))

        row_amb = ttk.Frame(grp_params)
        row_amb.pack(fill=tk.X, pady=3)

        ttk.Label(row_amb, text="Ambiente:", width=18, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.cbo_ambiente = ttk.Combobox(
            row_amb,
            values=[
                "Produção (https://alvo.rccbrasil.org.br/api)",
                "Homologação / Personalizado",
            ],
            state="readonly",
            width=46,
        )
        self.cbo_ambiente.pack(side=tk.LEFT, padx=(0, 12))
        self.cbo_ambiente.bind("<<ComboboxSelected>>", self._on_ambiente_changed)

        self.var_ativo = tk.BooleanVar(value=True)
        chk_ativo = ttk.Checkbutton(row_amb, text="Habilitar Integração Ativa", variable=self.var_ativo)
        chk_ativo.pack(side=tk.LEFT)

        row_url = ttk.Frame(grp_params)
        row_url.pack(fill=tk.X, pady=3)

        ttk.Label(row_url, text="URL Base da API:", width=18, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.txt_url = ttk.Entry(row_url, font=("Segoe UI", 9))
        self.txt_url.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))

        ttk.Label(row_url, text="Timeout (s):", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
        self.txt_timeout = ttk.Spinbox(row_url, from_=10, to=300, width=5)
        self.txt_timeout.pack(side=tk.LEFT)

        # 3. Rodapé de Ações
        bottom_frame = tk.Frame(self, bg="#E2E8F0", height=48, bd=1, relief=tk.GROOVE)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        bottom_frame.pack_propagate(False)

        btn_box = tk.Frame(bottom_frame, bg="#E2E8F0")
        btn_box.pack(side=tk.LEFT, padx=12, pady=7)

        self.btn_testar = ttk.Button(btn_box, text="🔌 Testar Conexão / Token", command=self.testar_conexao)
        self.btn_testar.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_salvar = ttk.Button(btn_box, text="💾 Salvar Configurações (F2)", command=self.salvar)
        self.btn_salvar.pack(side=tk.LEFT, padx=(0, 6))

        btn_fechar = ttk.Button(bottom_frame, text="🚪 Fechar (Esc)", command=self.destroy)
        btn_fechar.pack(side=tk.RIGHT, padx=12, pady=7)

        self.lbl_rodape_status = tk.Label(
            bottom_frame,
            text="Pronto.",
            font=("Segoe UI", 9, "italic"),
            bg="#E2E8F0",
            fg="#475569",
        )
        self.lbl_rodape_status.pack(side=tk.RIGHT, padx=16)

    def _carregar_valores_na_tela(self):
        cfg = self.config_atual
        self.txt_token.delete("1.0", tk.END)
        if cfg.token:
            self.txt_token.insert("1.0", cfg.token)

        self.txt_dt_inicial.delete(0, tk.END)
        self.txt_dt_inicial.insert(0, cfg.data_inicial or "")

        self.txt_dt_final.delete(0, tk.END)
        self.txt_dt_final.insert(0, cfg.data_final or "")

        self.txt_url.delete(0, tk.END)
        self.txt_url.insert(0, cfg.base_url or "https://alvo.rccbrasil.org.br/api")

        self.txt_timeout.delete(0, tk.END)
        self.txt_timeout.insert(0, str(cfg.timeout or 45))

        self.var_ativo.set(cfg.ativo)

        if "homolog" in (cfg.ambiente or "").lower() or "custom" in (cfg.ambiente or "").lower():
            self.cbo_ambiente.set("Homologação / Personalizado")
        else:
            self.cbo_ambiente.set("Produção (https://alvo.rccbrasil.org.br/api)")

        self._atualizar_contador_token()

    def _atualizar_contador_token(self):
        tam = len(self.txt_token.get("1.0", tk.END).strip())
        self.lbl_tamanho_token.config(text=f"{tam} caractere(s)")

    def _on_token_text_changed(self, event=None):
        self._atualizar_contador_token()
        self._atualizar_badge_status()

    def _on_data_changed(self, event, widget):
        _aplicar_mascara_data(event, widget)
        self._atualizar_badge_status()

    def _on_ambiente_changed(self, event=None):
        amb = self.cbo_ambiente.get()
        if "Produção" in amb:
            self.txt_url.delete(0, tk.END)
            self.txt_url.insert(0, "https://alvo.rccbrasil.org.br/api")

    def _colar_token(self):
        try:
            conteudo = self.clipboard_get().strip()
            if conteudo:
                self.txt_token.delete("1.0", tk.END)
                self.txt_token.insert("1.0", conteudo)
                self._atualizar_contador_token()
                self._atualizar_badge_status()
                self.lbl_rodape_status.config(text="Token colado da área de transferência com sucesso.")
        except Exception:
            messagebox.showwarning("Atenção", "Área de transferência não contém texto válido.", parent=self)

    def _copiar_token(self):
        tok = self.txt_token.get("1.0", tk.END).strip()
        if not tok:
            messagebox.showinfo("Aviso", "Nenhum token para copiar.", parent=self)
            return
        self.clipboard_clear()
        self.clipboard_append(tok)
        self.lbl_rodape_status.config(text="Token copiado para a área de transferência.")

    def _limpar_token(self):
        if messagebox.askyesno("Confirmação", "Deseja realmente limpar o campo de token?", parent=self):
            self.txt_token.delete("1.0", tk.END)
            self._atualizar_contador_token()
            self._atualizar_badge_status()

    def _obter_dados_tela(self) -> AlvoAPIConfig:
        return AlvoAPIConfig(
            token=self.txt_token.get("1.0", tk.END).strip(),
            data_inicial=self.txt_dt_inicial.get().strip(),
            data_final=self.txt_dt_final.get().strip(),
            base_url=self.txt_url.get().strip() or "https://alvo.rccbrasil.org.br/api",
            timeout=int(self.txt_timeout.get().strip() or 45),
            ativo=self.var_ativo.get(),
            ambiente="Homologação" if "Homologação" in self.cbo_ambiente.get() else "Produção",
            usuario_padrao=self.config_atual.usuario_padrao,
        )

    def _atualizar_badge_status(self):
        cfg = self._obter_dados_tela()
        status_code, msg, is_valido = validar_status_token(cfg)

        if status_code == "ATIVO":
            bg_cor, fg_cor = "#DCFCE7", "#166534"
            icone = "🟢 "
        elif status_code == "EXPIRANDO":
            bg_cor, fg_cor = "#FEF9C3", "#854D0E"
            icone = "🟡 "
        elif status_code == "EXPIRADO":
            bg_cor, fg_cor = "#FEE2E2", "#991B1B"
            icone = "🔴 "
        elif status_code == "FUTURO":
            bg_cor, fg_cor = "#E0E7FF", "#3730A3"
            icone = "⏳ "
        elif status_code == "DESATIVADO":
            bg_cor, fg_cor = "#F1F5F9", "#64748B"
            icone = "⚪ "
        else:
            bg_cor, fg_cor = "#F1F5F9", "#475569"
            icone = "⚪ "

        self.frame_status.config(bg=bg_cor)
        self.lbl_status_badge.config(text=f"{icone}{msg}", bg=bg_cor, fg=fg_cor)

    def testar_conexao(self):
        cfg = self._obter_dados_tela()
        if not cfg.token:
            messagebox.showwarning("Atenção", "Informe o Token de integração para realizar o teste.", parent=self)
            self.txt_token.focus_set()
            return

        self.btn_testar.config(state="disabled")
        self.lbl_rodape_status.config(text="Testando comunicação com a API Alvo...")
        self.update_idletasks()

        try:
            sucesso, msg, status_http = testar_comunicacao_alvo(cfg)
            if sucesso:
                messagebox.showinfo("Sucesso na Conexão", f"✔ Teste de Conexão Concluído com Sucesso!\n\n{msg}", parent=self)
                self.lbl_rodape_status.config(text="Comunicação com o Alvo OK.")
            else:
                messagebox.showerror("Falha na Comunicação", f"✖ Falha ao comunicar com a API Alvo:\n\n{msg}", parent=self)
                self.lbl_rodape_status.config(text="Falha no teste com o Alvo.")
        except Exception as exc:
            messagebox.showerror("Erro no Teste", f"Erro inesperado: {exc}", parent=self)
            self.lbl_rodape_status.config(text=f"Erro: {exc}")
        finally:
            self.btn_testar.config(state="normal")

    def salvar(self):
        cfg = self._obter_dados_tela()

        # Validação de datas se fornecidas
        if cfg.data_inicial:
            dt_ini = parse_data_br(cfg.data_inicial)
            if not dt_ini:
                messagebox.showwarning("Data Inválida", "Data Inicial de validade inválida. Use o formato DD/MM/AAAA.", parent=self)
                self.txt_dt_inicial.focus_set()
                return

        if cfg.data_final:
            dt_fim = parse_data_br(cfg.data_final)
            if not dt_fim:
                messagebox.showwarning("Data Inválida", "Data Final de validade inválida. Use o formato DD/MM/AAAA.", parent=self)
                self.txt_dt_final.focus_set()
                return

        if cfg.data_inicial and cfg.data_final:
            if parse_data_br(cfg.data_inicial) > parse_data_br(cfg.data_final):
                messagebox.showwarning("Período Inválido", "A Data Inicial não pode ser posterior à Data Final de validade.", parent=self)
                self.txt_dt_inicial.focus_set()
                return

        sucesso = salvar_configuracao_alvo(cfg)
        if sucesso:
            self.config_atual = cfg
            self._atualizar_badge_status()
            messagebox.showinfo("Configurações Salvas", "Parâmetros e Token da API Alvo gravados com sucesso!", parent=self)
            self.lbl_rodape_status.config(text="Configurações gravadas com sucesso.")

            if self.on_salvar_callback:
                try:
                    self.on_salvar_callback(cfg)
                except Exception:
                    pass

            self.destroy()
        else:
            messagebox.showerror("Erro ao Salvar", "Não foi possível persistir as configurações da API Alvo em disco.", parent=self)

    def destroy(self):
        try:
            self.grab_release()
        except Exception:
            pass
        FrmConfiguracaoAPIAlvo._instancia_ativa = None
        super().destroy()


def abrir_configuracao_api_alvo(parent=None, on_salvar_callback=None):
    """Função facilitadora para abrir o formulário de configuração da API Alvo."""
    return FrmConfiguracaoAPIAlvo(parent=parent, on_salvar_callback=on_salvar_callback)
