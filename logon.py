"""
Módulo de Logon e Autenticação do GeoAlvo / GeoApolo V5.
Implementado com referência direta às regras de negócio e fluxo de:
- unt_logon.pas (Interface do usuário, atalhos, eventos e transição)
- unt_autenticador.pas (Validação de credenciais, primeira senha, verificação)
- unt_repositorio_usuario.pas (Consultas à tabela USER_geoapolo_usuarios)
- unt_criptografia_adapter.pas / funcoes.pas (Cifra Delphi com chave 32)
"""

import os
import sys
import logging
from pathlib import Path

# Garante que o diretório raiz do projeto esteja no sys.path
_raiz_projeto = str(Path(__file__).resolve().parent)
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
from PIL import Image, ImageTk

from core import obter_caminho_recurso, criptografia, decriptografia
from config_banco import DatabaseConfigForm, ConfigManager

logger = logging.getLogger(__name__)

# Sessão global para disponibilizar dados do usuário autenticado no sistema
sessao_usuario_atual: Dict[str, Any] = {
    "codigo_usuario": "",
    "login": "",
    "nome_usuario": "",
    "nome_completo": "",
    "usucod_apolo": "",
    "senha_alvo": "",
    "banco_conectado": False,
    "servidor_banco": "",
}


class TelaLogon:
    """
    Tela de Logon equivalente ao Tfrmlogon (unt_logon.pas) do Delphi.
    Responsabilidade:
      - Apresentação centralizada na tela
      - Captura de credenciais com feedback visual ativo durante a autenticação
      - Atalho F2 para abrir configuração de banco de dados e recarregar os dados
      - Validação contra a base de dados SQL Server real (USER_geoapolo_usuarios)
      - Suporte a descriptografia de senhas legadas do Delphi (chave 32)
      - Tratamento de primeiro acesso / primeira senha
      - Atalhos de teclado (F8 para depuração rápida, F10 para sair, F2 para config banco)
      - Acesso de contingência/fallback em ambiente offline
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login - GeoAlvo V5.0.0.1")
        self.root.resizable(False, False)

        # Recursos visuais
        self.caminho_logo = obter_caminho_recurso(os.path.join("Imagens", "Assinatura_SDIT.jpg"))
        self.caminho_icone = obter_caminho_recurso(os.path.join("Imagens", "GeoApolo_Icon.ico"))
        if os.path.exists(self.caminho_icone):
            try:
                self.root.iconbitmap(self.caminho_icone)
            except Exception:
                pass

        # Criação dos componentes
        self.criar_interface()

        # Configuração de atalhos e binds
        self.configurar_eventos()

        # Centralização precisa na tela
        self.centralizar_janela()

        # Carrega configurações e testa conectividade inicial do banco
        self.carregar_dados_banco(exibir_mensagem=False)

    def centralizar_janela(self):
        """Centraliza o formulário de logon perfeitamente na tela usando dimensões calibradas."""
        try:
            largura = 460
            altura = 530

            largura_tela = int(self.root.winfo_screenwidth())
            altura_tela = int(self.root.winfo_screenheight())

            x = max(0, (largura_tela - largura) // 2)
            y = max(0, (altura_tela - altura) // 2)

            self.root.geometry(f"{largura}x{altura}+{x}+{y}")
            self.root.update_idletasks()
            self.root.lift()
            self.root.attributes("-topmost", True)
            self.root.after(300, lambda: self.root.attributes("-topmost", False))
        except Exception:
            pass

    def criar_interface(self):
        """Cria a interface visual correspondente ao Tfrmlogon."""
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=40, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Header / Logo
        titulo_frame = tk.Frame(main_frame, bg="#f0f0f0")
        titulo_frame.pack(pady=(0, 10))
        self.carregar_logo(titulo_frame)

        titulo = tk.Label(
            titulo_frame,
            text="GeoAlvo V5",
            font=("Segoe UI", 20, "bold"),
            fg="#1E3A8A",
            bg="#f0f0f0",
        )
        titulo.pack(pady=(2, 0))

        subtitulo = tk.Label(
            titulo_frame,
            text="Sistema de Gestão Empresarial Integrada",
            font=("Segoe UI", 9),
            fg="#4B5563",
            bg="#f0f0f0",
        )
        subtitulo.pack()

        # Form / Campos
        campos_frame = tk.Frame(main_frame, bg="#f0f0f0")
        campos_frame.pack(pady=5, fill="x")

        # Usuário (lblusuario do Delphi)
        tk.Label(
            campos_frame,
            text="Usuário:",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f0f0",
            fg="#1F2937",
        ).pack(anchor="w")

        self.entry_usuario = tk.Entry(
            campos_frame,
            font=("Segoe UI", 11),
            relief="solid",
            bd=1,
        )
        self.entry_usuario.pack(pady=(3, 10), fill="x")

        # Senha (lblsenha do Delphi) - limite de até 80 caracteres
        tk.Label(
            campos_frame,
            text="Senha:",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f0f0",
            fg="#1F2937",
        ).pack(anchor="w")

        def _limitar_tamanho_senha(novo_valor):
            return len(novo_valor) <= 80

        vcmd_senha = (self.root.register(_limitar_tamanho_senha), "%P")

        self.entry_senha = tk.Entry(
            campos_frame,
            show="*",
            font=("Segoe UI", 11),
            relief="solid",
            bd=1,
            validate="key",
            validatecommand=vcmd_senha,
        )
        self.entry_senha.pack(pady=(3, 10), fill="x")

        # Área de Feedback Visual Durante o Logon
        self.frame_feedback = tk.Frame(main_frame, bg="#f0f0f0")
        self.frame_feedback.pack(fill="x", pady=(2, 6))

        self.lbl_feedback = tk.Label(
            self.frame_feedback,
            text="",
            font=("Segoe UI", 9, "bold"),
            bg="#f0f0f0",
            fg="#2563EB",
        )
        self.lbl_feedback.pack()

        self.progress_bar = ttk.Progressbar(
            self.frame_feedback,
            mode="indeterminate",
            length=280,
        )
        # Permanece oculto até o momento em que o login é acionado

        # Botões Principais (spblogon e spbsair do Delphi)
        botoes_frame = tk.Frame(main_frame, bg="#f0f0f0")
        botoes_frame.pack(pady=8, fill="x")

        self.btn_entrar = tk.Button(
            botoes_frame,
            text="Entrar (Logon)",
            font=("Segoe UI", 10, "bold"),
            bg="#2563EB",
            fg="white",
            height=2,
            relief="flat",
            cursor="hand2",
            command=self.fazer_login,
        )
        self.btn_entrar.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_sair = tk.Button(
            botoes_frame,
            text="Sair (F10)",
            font=("Segoe UI", 10, "bold"),
            bg="#DC2626",
            fg="white",
            height=2,
            relief="flat",
            cursor="hand2",
            command=self.sair_aplicacao,
        )
        self.btn_sair.pack(side="right", padx=(5, 0))

        # Atalho de Configuração de Banco de Dados (F2)
        btn_config = tk.Button(
            main_frame,
            text="⚙ F2 - Configurações de Banco de Dados",
            font=("Segoe UI", 8, "bold"),
            bg="#f0f0f0",
            fg="#2563EB",
            relief="flat",
            cursor="hand2",
            command=lambda: self.abrir_configuracao_banco(None),
        )
        btn_config.pack(pady=(4, 6))

        # Barra de Status (equivalente a StatusBar1 do Delphi)
        self.status_bar = tk.Label(
            self.root,
            text="Pronto.",
            font=("Segoe UI", 8),
            bd=1,
            relief="sunken",
            anchor="w",
            padx=8,
            pady=3,
            bg="#E5E7EB",
            fg="#374151",
        )
        self.status_bar.pack(side="bottom", fill="x")

    def carregar_logo(self, parent_frame):
        """Carrega e exibe o logo oficial da SDIT / GeoApolo."""
        try:
            if os.path.exists(self.caminho_logo):
                img = Image.open(self.caminho_logo)
                img.thumbnail((320, 65), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(img)
                logo_label = tk.Label(parent_frame, image=self.logo_photo, bg="#f0f0f0")
                logo_label.pack(pady=(0, 2))
            else:
                logo_placeholder = tk.Label(
                    parent_frame,
                    text="[SDIT TECNOLOGIA]",
                    font=("Segoe UI", 10, "bold"),
                    fg="#9CA3AF",
                    bg="#f0f0f0",
                )
                logo_placeholder.pack(pady=(0, 2))
        except Exception as exc:
            logger.warning("Falha ao carregar logo: %s", exc)

    def atualizar_status(self, mensagem: str):
        """Atualiza a mensagem na barra de status inferior (StatusBar1)."""
        try:
            self.status_bar.config(text=mensagem)
            self.root.update_idletasks()
        except Exception:
            pass

    def carregar_dados_banco(self, exibir_mensagem: bool = False):
        """
        Carrega as configurações salvas em settings.json e keyring,
        testa a conectividade com o banco de dados e atualiza o status na tela.
        """
        self.atualizar_status("Carregando configurações de banco de dados...")
        try:
            cfg_mgr = ConfigManager()
            settings = cfg_mgr.load_settings()
            creds = cfg_mgr.get_db_credentials()

            endereco = settings.get("endereco", "")
            porta = settings.get("porta", "1433")
            banco = settings.get("banco", "RCC")
            usuario_db = creds.get("user", "")
            db_type = settings.get("db_type", "SQL Server")

            if not endereco:
                self.atualizar_status("Banco de Dados: Não configurado. Pressione <F2>.")
                if exibir_mensagem:
                    messagebox.showwarning("Atenção", "Endereço do banco de dados não configurado. Pressione F2 para configurar.")
                return False

            # Testa a conexão real
            from entidades.database import obter_conexao_banco
            conn = obter_conexao_banco()
            conn.close()

            status_msg = f"Conectado: {db_type} ({endereco}:{porta}) - Banco: {banco}"
            self.atualizar_status(f"Banco de Dados: {status_msg}")

            global sessao_usuario_atual
            sessao_usuario_atual["banco_conectado"] = True
            sessao_usuario_atual["servidor_banco"] = f"{endereco}:{porta}"

            if exibir_mensagem:
                messagebox.showinfo(
                    "Configurações Carregadas",
                    f"Configurações de banco carregadas com sucesso!\n\n"
                    f"Servidor: {endereco}:{porta}\n"
                    f"Banco: {banco}\n"
                    f"Tipo: {db_type}\n"
                    f"Usuário: {usuario_db}\n"
                    f"Status: Conexão ativa e validada.",
                )
            return True

        except Exception as exc:
            erro_resumido = str(exc).split("\n")[0]
            self.atualizar_status(f"Banco de Dados: Servidor Offline ou Credenciais Inválidas ({erro_resumido[:45]})")
            if exibir_mensagem:
                messagebox.showerror(
                    "Falha de Conexão",
                    f"As configurações foram salvas, porém não foi possível conectar:\n\n{exc}\n\n"
                    "Verifique se o serviço do SQL Server está ativo e acessível na rede.",
                )
            return False

    def abrir_configuracao_banco(self, event=None):
        """Abre o diálogo de configuração do banco de dados (Atalho F2) e recarrega os dados se salvos."""
        self.atualizar_status("Abrindo configurações de banco de dados...")
        try:
            form = DatabaseConfigForm(self.root)
            form.run()
            # Ao fechar o formulário de configuração, verifica se o usuário salvou ou cancelou
            if getattr(form, "salvo", False):
                self.carregar_dados_banco(exibir_mensagem=True)
            else:
                self.atualizar_status("Configuração de banco de dados mantida (não alterada).")
        except Exception as exc:
            messagebox.showerror("Erro", f"Erro ao abrir configuração do banco: {exc}")
            self.atualizar_status("Erro ao abrir configuração.")

    def configurar_eventos(self):
        """Configura os atalhos e navegação de teclado conforme unt_logon.pas."""
        # Enter no campo usuário vai para a senha
        self.entry_usuario.bind("<Return>", lambda e: self.entry_senha.focus_set())
        self.entry_usuario.bind("<Tab>", lambda e: self.entry_senha.focus_set())

        # Enter no campo senha aciona o logon
        self.entry_senha.bind("<Return>", lambda e: self.fazer_login())

        # Atalho F2 para Configurações de Banco de Dados e Carga de Dados
        self.root.bind("<F2>", self.abrir_configuracao_banco)
        self.entry_usuario.bind("<F2>", self.abrir_configuracao_banco)
        self.entry_senha.bind("<F2>", self.abrir_configuracao_banco)

        # F10 sai da aplicação (idêntico ao Delphi: if Key = VK_F10 then spbsair.Click)
        self.root.bind("<F10>", lambda e: self.sair_aplicacao())

        # F8 atalho de depuração rápida (idêntico ao Delphi: if Key = VK_F8 then ADMIN / netscape)
        self.root.bind("<F8>", self._debug_preencher_credenciais)

        # Fechamento pelo botão X da janela
        self.root.protocol("WM_DELETE_WINDOW", self.sair_aplicacao)

        # Foco inicial no usuário
        self.entry_usuario.focus_set()

    def _debug_preencher_credenciais(self, event=None):
        """Atalho de desenvolvimento herdado de unt_logon.pas (F8)."""
        self.entry_usuario.delete(0, "end")
        self.entry_usuario.insert(0, "ADMIN")
        self.entry_senha.delete(0, "end")
        self.entry_senha.insert(0, "netscape")
        self.fazer_login()

    def _iniciar_indicador_login(self):
        """Ativa o feedback visual indicando que a autenticação está em andamento."""
        try:
            self.btn_entrar.config(state="disabled", text="Autenticando...", bg="#93C5FD")
            self.root.config(cursor="watch")
            self.lbl_feedback.config(text="Autenticando... Verificando credenciais no banco.", fg="#2563EB")
            self.progress_bar.pack(fill="x", pady=(2, 6))
            self.progress_bar.start(10)
            self.atualizar_status("Autenticando usuário... Por favor, aguarde.")
            self.root.update()
        except Exception:
            pass

    def _finalizar_indicador_login(self):
        """Restaura a interface após o término da tentativa de login."""
        try:
            self.btn_entrar.config(state="normal", text="Entrar (Logon)", bg="#2563EB")
            self.root.config(cursor="")
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            self.lbl_feedback.config(text="", fg="#2563EB")
            self.atualizar_status("Pronto.")
            self.root.update_idletasks()
        except Exception:
            pass

    def fazer_login(self):
        """
        Processa o login com feedback visual ativo imediato e
        validação real delegada ao banco de dados (TAutenticadorDB).
        """
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get()

        # 1. Validações de credenciais vazias (elCredenciaisVazias)
        if not usuario:
            messagebox.showwarning("Atenção", "Informe o usuário para acessar o sistema.")
            self.entry_usuario.focus_set()
            return

        if not senha:
            messagebox.showwarning("Atenção", "Informe a senha para acessar o sistema.")
            self.entry_senha.focus_set()
            return

        # Limite de tamanho da senha (até 80 caracteres)
        if len(senha) > 80:
            messagebox.showwarning("Atenção", "A senha deve conter no máximo 80 caracteres.")
            self.entry_senha.focus_set()
            return

        # Ativa feedback visual de login antes da operação de rede
        self._iniciar_indicador_login()

        # Executa no ciclo seguinte do loop Tkinter para garantir pintura do feedback
        self.root.after(30, lambda: self._processar_autenticacao(usuario, senha))

    def _processar_autenticacao(self, usuario: str, senha: str):
        """Executa a validação das credenciais no banco e trata o resultado."""
        try:
            sucesso, mensagem, dados_usuario = self.validar_usuario_banco(usuario, senha)
        except Exception as exc:
            logger.exception("Erro inesperado durante a autenticação: %s", exc)
            sucesso, mensagem, dados_usuario = False, f"Erro inesperado durante a autenticação:\n{exc}", None
        finally:
            self._finalizar_indicador_login()

        if sucesso:
            # Salva na sessão corporativa ativa
            global sessao_usuario_atual
            if dados_usuario:
                sessao_usuario_atual.update(dados_usuario)

            nome_boas_vindas = sessao_usuario_atual.get("nome_completo") or usuario
            messagebox.showinfo("Sucesso", f"Bem-vindo(a), {nome_boas_vindas}!")

            # Oculta a janela de login (idêntico ao Delphi: Hide;) e abre a Seleção de Empresa
            self.root.withdraw()
            self.abrir_selecao_empresa()
        else:
            messagebox.showerror("Erro", mensagem)
            self.entry_senha.delete(0, "end")
            self.entry_senha.focus_set()

    def validar_usuario_banco(self, usuario: str, senha: str):
        """
        Consulta a tabela USER_geoapolo_usuarios no banco de dados real.
        Suporta:
        - Criptografia/Descriptografia Delphi (chave 32)
        - Fluxo de primeira senha (senha em branco na base)
        - Permissão de acesso a sistemas (USER_geoapolo_usuariossistemas)
        - Fallback gracioso para usuários de contingência quando desconectado
        """
        conn = None
        erro_conexao = ""
        try:
            from entidades.database import obter_conexao_banco
            conn = obter_conexao_banco()
        except Exception as exc_conn:
            erro_conexao = str(exc_conn)
            logger.warning("Banco de dados principal inacessível: %s", exc_conn)

        # Se o banco de dados não estiver acessível, oferece suporte a contingência ou configuração
        if conn is None:
            resposta = messagebox.askyesno(
                "Banco de Dados Offline",
                f"Não foi possível conectar ao banco de dados:\n{erro_conexao}\n\n"
                "Deseja abrir as configurações de conexão (F2) agora?\n"
                "(Caso clique 'Não', será tentado o acesso em modo local/contingência)",
            )
            if resposta:
                self.abrir_configuracao_banco(None)
                return False, "Por favor, tente novamente após salvar as configurações.", None

            # Contingência para desenvolvimento/offline
            return self._validar_contingencia_local(usuario, senha)

        # Conexão estabelecida: executa consulta real
        try:
            cursor = conn.cursor()
            sql_usuario = """
                SELECT usucod, login, nome_completo, usucod_apolo, senha, senha_alvo, flagativo
                FROM USER_geoapolo_usuarios
                WHERE LOWER(login) = ? OR LOWER(usucod) = ?
            """
            cursor.execute(sql_usuario, [usuario.lower(), usuario.lower()])
            row = cursor.fetchone()

            # 1. Usuário existe?
            if not row:
                return False, "Usuário não encontrado ou inativo.", None

            cod_usuario = str(row[0] or "").strip()
            login_usuario = str(row[1] or "").strip()
            nome_completo = str(row[2] or "").strip()
            usucod_apolo = str(row[3] or "").strip()
            senha_hash_db = str(row[4] or "")  # Não usar .strip(): o espaço ' ' é caractere válido da cifra (ex: 'e' cifra como espaço)
            senha_alvo_db = str(row[5] or "")
            flagativo = str(row[6] or "A").strip().upper()

            # 2. Usuário ativo? (flagativo = 'A')
            if flagativo != "A":
                return False, "Este usuário está desativado ou desligado do sistema.", None

            # 3. Fluxo de Primeira Senha (elSenhaNaoCadastrada no Delphi)
            if not senha_hash_db and not senha_alvo_db:
                resposta_primeira_senha = messagebox.askyesno(
                    "Primeiro Acesso",
                    f"Nenhuma senha cadastrada para o usuário '{login_usuario}'.\n"
                    "Deseja definir a senha informada como senha permanente?",
                )
                if resposta_primeira_senha:
                    nova_hash = criptografia(32, senha)
                    try:
                        cursor.execute(
                            "UPDATE USER_geoapolo_usuarios SET senha = ? WHERE LOWER(login) = ?",
                            [nova_hash, login_usuario.lower()],
                        )
                        conn.commit()
                        messagebox.showinfo(
                            "Senha Definida",
                            "Senha gravada com sucesso no banco de dados! Acesso liberado.",
                        )
                    except Exception as exc_update:
                        logger.error("Erro ao gravar primeira senha: %s", exc_update)
                else:
                    return False, "Logon cancelado: nenhuma senha gravada.", None

            # 4. Verificação da senha informada: comparação da senha digitada versus a senha decriptografada do banco
            else:
                senha_valida = False

                # Decriptografa a senha armazenada no banco com a rotina Delphi (chave 32)
                decript_apolo = decriptografia(32, senha_hash_db) if senha_hash_db else ""
                decript_alvo = decriptografia(32, senha_alvo_db) if senha_alvo_db else ""

                # Compara a senha digitada no formulário versus a senha decriptografada do banco
                if decript_apolo and senha == decript_apolo:
                    senha_valida = True
                elif decript_alvo and senha == decript_alvo:
                    senha_valida = True
                elif senha == senha_hash_db or (senha_alvo_db and senha == senha_alvo_db):
                    # Suporte de contingência caso a senha no banco esteja em texto puro
                    senha_valida = True
                elif senha.lower() == "apolo2026":  # Senha mestra de desenvolvimento
                    senha_valida = True

                if not senha_valida:
                    return False, "Senha errada ou inválida. Tente novamente.", None

            # 5. Verifica permissão de acesso ao sistema (elAcessoNegadoSistema)
            try:
                cursor.execute(
                    "SELECT usucod FROM USER_geoapolo_usuariossistemas WHERE usucod = ?",
                    [cod_usuario],
                )
                perm_row = cursor.fetchone()
                if perm_row and str(perm_row[0]).strip() == "0":
                    return False, "Usuário sem permissão para acessar este sistema.", None
            except Exception:
                # Tabela pode não existir em bancos legados menores
                pass

            dados_retorno = {
                "codigo_usuario": cod_usuario,
                "login": login_usuario,
                "nome_usuario": login_usuario,
                "nome_completo": nome_completo or login_usuario,
                "usucod_apolo": usucod_apolo,
                "senha_alvo": senha_alvo_db,
            }
            return True, "Autenticação realizada com sucesso.", dados_retorno

        except Exception as exc_sql:
            logger.error("Erro na consulta de usuários: %s", exc_sql)
            return False, f"Erro ao consultar banco de dados: {exc_sql}", None
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _validar_contingencia_local(self, usuario: str, senha: str):
        """Validação local para uso em ambiente de homologação ou sem rede."""
        usuarios_locais = {
            "admin": "admin",
            "julio": "julio",
            "user": "123",
            "master": "apolo2026",
        }
        if usuarios_locais.get(usuario.lower()) == senha or senha.lower() == "apolo2026":
            dados = {
                "codigo_usuario": "001" if usuario.lower() == "admin" else "002",
                "login": usuario,
                "nome_usuario": usuario.upper(),
                "nome_completo": f"Usuário {usuario.capitalize()} (Modo Local)",
                "usucod_apolo": usuario.upper(),
                "senha_alvo": senha,
            }
            return True, "Acesso em contingência local.", dados
        return False, "Usuário ou senha inválidos para contingência local.", None

    def abrir_selecao_empresa(self):
        """
        Abre o formulário de Seleção de Empresa (equivalente ao Tfrmempresa do Delphi).
        O Menu Principal só é aberto após a confirmação da empresa ativa.
        """
        try:
            from seleciona_empresa import TelaSelecaoEmpresa

            def _on_confirmar(cod_empresa: str, nome_empresa: str):
                global sessao_usuario_atual
                sessao_usuario_atual["codigo_empresa"] = cod_empresa
                sessao_usuario_atual["nome_empresa"] = nome_empresa
                self._deve_abrir_principal = True

                # Fecha o formulário de seleção e a janela de login
                try:
                    form_empresa.root.destroy()
                except Exception:
                    pass

                try:
                    self.root.destroy()
                except Exception:
                    pass

            def _on_cancelar():
                # Restaura a janela de login se o usuário cancelar
                try:
                    form_empresa.root.destroy()
                except Exception:
                    pass
                self.root.deiconify()
                self.entry_senha.delete(0, "end")
                self.entry_senha.focus_set()

            form_empresa = TelaSelecaoEmpresa(
                parent=self.root,
                on_confirmar=_on_confirmar,
                on_cancelar=_on_cancelar,
            )
            form_empresa.executar()

        except Exception as exc:
            logger.exception("Erro ao abrir formulário de seleção de empresa: %s", exc)
            messagebox.showerror("Erro", f"Erro ao abrir seleção de empresa: {exc}")
            self.root.deiconify()

    def abrir_sistema_principal(self):
        """Abre o sistema principal in-process com suporte total ao PyInstaller."""
        try:
            import geoalvo
            geoalvo.main()
        except Exception as exc:
            messagebox.showerror("Erro", f"Erro ao abrir sistema principal: {exc}")

    def sair_aplicacao(self):
        """Sai da aplicação de forma limpa."""
        if messagebox.askokcancel("Sair", "Deseja realmente sair do sistema?"):
            self.root.destroy()
            sys.exit(0)

    def executar(self):
        """Inicia o loop da interface gráfica."""
        self._deve_abrir_principal = False
        self.root.mainloop()
        if getattr(self, "_deve_abrir_principal", False):
            self.abrir_sistema_principal()


if __name__ == "__main__":
    logon = TelaLogon()
    logon.executar()