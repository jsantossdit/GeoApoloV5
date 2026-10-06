"""
Módulo de Configuração de Banco de Dados do GeoAlvo & SAVIC.
Suporta SQL Server (GeoAlvo / Alvo) e MySQL (SAVIC legado).
Persistência híbrida: settings.json, keyring e Registro do Windows (HKEY_CURRENT_USER\\sdit\\configuracoes\\DataBase).
"""

import os
import sys
import json
import logging
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import keyring

logger = logging.getLogger(__name__)

# Tenta importar winreg para interoperabilidade com o Delphi
try:
    import winreg
except ImportError:
    winreg = None

try:
    from core import aplicar_icone_janela, centralizar_janela
except ImportError:
    def aplicar_icone_janela(w): return False
    def centralizar_janela(w, parent=None, largura=640, altura=580): pass


class ConfigManager:
    """Gerencia leitura e gravação de credenciais e parâmetros de conexão."""

    def __init__(self, app_name="meuapp"):
        self.app_name = app_name
        self.config_dir = self._get_config_dir()

    def _get_config_dir(self):
        if os.name == 'nt':
            return Path(os.environ.get('APPDATA', Path.home())) / self.app_name
        return Path.home() / f'.{self.app_name}'

    # -------------------------------------------------------------
    # GeoAlvo / Alvo (SQL Server)
    # -------------------------------------------------------------
    def save_db_credentials(self, user, password):
        try:
            keyring.set_password(self.app_name, "db_user", user or "")
            keyring.set_password(self.app_name, "db_password", password or "")
        except Exception as e:
            logger.warning(f"Keyring indisponível para GeoAlvo: {e}")
        self._sincronizar_registro_geoalvo(user=user, password=password)

    def get_db_credentials(self):
        user = ""
        password = ""
        try:
            user = keyring.get_password(self.app_name, "db_user") or ""
            password = keyring.get_password(self.app_name, "db_password") or ""
        except Exception:
            pass

        # Fallback para o Registro do Windows
        if not user or not password:
            reg_data = self._ler_registro_geoalvo()
            if not user and reg_data.get("usuario"):
                user = reg_data["usuario"]
            if not password and reg_data.get("senha"):
                password = reg_data["senha"]

        return {'user': user, 'password': password}

    def save_settings(self, settings):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        settings_file = self.config_dir / 'settings.json'
        atuais = self.load_settings()
        atuais.update(settings)
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(atuais, f, indent=2)
        self._sincronizar_registro_geoalvo(settings=settings)

    def load_settings(self):
        settings_file = self.config_dir / 'settings.json'
        dados = {}
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
            except Exception:
                dados = {}

        # Fallback / enriquecimento via Registro do Windows se estiver vazio
        if not dados.get("endereco"):
            reg_data = self._ler_registro_geoalvo()
            if reg_data.get("servidor"):
                dados.setdefault("db_type", "SQL Server")
                dados.setdefault("endereco", reg_data.get("servidor", "localhost"))
                dados.setdefault("banco", reg_data.get("banco", "RCC"))
                dados.setdefault("porta", "1433")

        if not dados.get("timeout"):
            reg_data = self._ler_registro_geoalvo()
            if reg_data.get("timeout"):
                try:
                    dados["timeout"] = int(reg_data["timeout"])
                except (ValueError, TypeError):
                    pass
            else:
                dados["timeout"] = 60

        return dados

    # -------------------------------------------------------------
    # SAVIC (MySQL Legado)
    # -------------------------------------------------------------
    def save_savic_credentials(self, user, password):
        try:
            keyring.set_password(self.app_name, "savic_user", user or "")
            keyring.set_password(self.app_name, "savic_password", password or "")
        except Exception as e:
            logger.warning(f"Keyring indisponível para SAVIC: {e}")
        self._sincronizar_registro_savic(user=user, password=password)

    def get_savic_credentials(self):
        user = ""
        password = ""
        try:
            user = keyring.get_password(self.app_name, "savic_user") or ""
            password = keyring.get_password(self.app_name, "savic_password") or ""
        except Exception:
            pass

        # Fallback para Registro do Windows
        if not user or not password:
            reg = self._ler_registro_savic()
            if not user and reg.get("usuario"):
                user = reg["usuario"]
            if not password and reg.get("senha"):
                password = reg["senha"]

        # Valores padrão históricos do SAVIC se ainda não configurados
        if not user:
            user = "rccbrasilsavic"
        if not password:
            password = "b2J4earCJuNcM7"

        return {'user': user, 'password': password}

    def save_savic_settings(self, settings):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        settings_file = self.config_dir / 'settings.json'
        atuais = self.load_settings()
        for k, v in settings.items():
            atuais[f"savic_{k}"] = v
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(atuais, f, indent=2)
        self._sincronizar_registro_savic(settings=settings)

    def load_savic_settings(self):
        atuais = self.load_settings()
        savic_dict = {
            "host": atuais.get("savic_host", ""),
            "port": atuais.get("savic_port", "3306"),
            "database": atuais.get("savic_database", "")
        }

        # Fallback para o Registro do Windows
        if not savic_dict["host"]:
            reg = self._ler_registro_savic()
            if reg.get("servidor"):
                savic_dict["host"] = reg["servidor"]
                savic_dict["port"] = str(reg.get("porta", "3306") or "3306")
                savic_dict["database"] = reg.get("banco", "rccbrasilsavic")

        # Padrões do SAVIC se não configurado ainda
        if not savic_dict["host"]:
            savic_dict["host"] = "167.71.28.209"
        if not savic_dict["port"]:
            savic_dict["port"] = "3333"
        if not savic_dict["database"]:
            savic_dict["database"] = "rccbrasilsavic"

        return savic_dict

    # -------------------------------------------------------------
    # Aplicativo RCC (MySQL)
    # -------------------------------------------------------------
    def save_app_rcc_credentials(self, user, password):
        try:
            keyring.set_password(self.app_name, "app_rcc_user", user or "")
            keyring.set_password(self.app_name, "app_rcc_password", password or "")
        except Exception as e:
            logger.warning(f"Keyring indisponível para Aplicativo RCC: {e}")
        self._sincronizar_registro_app_rcc(user=user, password=password)

    def get_app_rcc_credentials(self):
        user = ""
        password = ""
        try:
            user = keyring.get_password(self.app_name, "app_rcc_user") or ""
            password = keyring.get_password(self.app_name, "app_rcc_password") or ""
        except Exception:
            pass

        # Fallback para Registro do Windows
        if not user or not password:
            reg = self._ler_registro_app_rcc()
            if not user and reg.get("usuario"):
                user = reg["usuario"]
            if not password and reg.get("senha"):
                password = reg["senha"]

        return {'user': user, 'password': password}

    def save_app_rcc_settings(self, settings):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        settings_file = self.config_dir / 'settings.json'
        atuais = self.load_settings()
        for k, v in settings.items():
            atuais[f"app_rcc_{k}"] = v
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(atuais, f, indent=2)
        self._sincronizar_registro_app_rcc(settings=settings)

    def load_app_rcc_settings(self):
        atuais = self.load_settings()
        app_dict = {
            "host": atuais.get("app_rcc_host", ""),
            "port": atuais.get("app_rcc_port", "3306"),
            "database": atuais.get("app_rcc_database", "")
        }

        # Fallback para o Registro do Windows
        if not app_dict["host"]:
            reg = self._ler_registro_app_rcc()
            if reg.get("servidor"):
                app_dict["host"] = reg["servidor"]
                app_dict["port"] = str(reg.get("porta", "3306") or "3306")
                app_dict["database"] = reg.get("banco", "")

        return app_dict

    def _sincronizar_registro_app_rcc(self, user=None, password=None, settings=None):
        if not winreg:
            return
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"sdit\configuracoes\DataBase")
            if settings:
                if "host" in settings:
                    winreg.SetValueEx(key, "Nome do Servidor APP RCC", 0, winreg.REG_SZ, str(settings["host"]))
                    winreg.SetValueEx(key, "IP do Servidor APP RCC", 0, winreg.REG_SZ, str(settings["host"]))
                if "database" in settings:
                    winreg.SetValueEx(key, "NomeBancoAPP RCC", 0, winreg.REG_SZ, str(settings["database"]))
                if "port" in settings:
                    winreg.SetValueEx(key, "Porta Comunicacao APP RCC", 0, winreg.REG_SZ, str(settings["port"]))
            if user:
                winreg.SetValueEx(key, "Usuario admin APP RCC", 0, winreg.REG_SZ, str(user))
            if password:
                winreg.SetValueEx(key, "Senha APP RCC", 0, winreg.REG_SZ, str(password))
            winreg.SetValueEx(key, "Protocolo APP RCC", 0, winreg.REG_SZ, "MySQL")
            winreg.CloseKey(key)
        except Exception as e:
            logger.debug(f"Não foi possível sincronizar Registro do Windows para Aplicativo RCC: {e}")

    def _ler_registro_app_rcc(self):
        res = {}
        if not winreg:
            return res
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"sdit\configuracoes\DataBase")
            mapeamento = [
                ("servidor", ["Nome do Servidor APP RCC", "Nome do Servidor APP"]),
                ("banco", ["NomeBancoAPP RCC", "NomeBancoAPP"]),
                ("usuario", ["Usuario admin APP RCC", "Usuario admin APP"]),
                ("senha", ["Senha APP RCC", "Senha APP"]),
                ("porta", ["Porta Comunicacao APP RCC", "Porta Comunicacao APP"]),
            ]
            for field, reg_names in mapeamento:
                for reg_name in reg_names:
                    try:
                        val, _ = winreg.QueryValueEx(key, reg_name)
                        if str(val).strip():
                            res[field] = str(val).strip()
                            break
                    except OSError:
                        pass
            winreg.CloseKey(key)
        except Exception:
            pass
        return res

    # -------------------------------------------------------------
    # Sincronização com Windows Registry (sdit\configuracoes\DataBase)
    # -------------------------------------------------------------
    def _sincronizar_registro_geoalvo(self, user=None, password=None, settings=None):
        if not winreg:
            return
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"sdit\configuracoes\DataBase")
            if settings:
                if "endereco" in settings:
                    srv = str(settings["endereco"]).strip()
                    while srv.startswith("\\") or srv.startswith("/"):
                        srv = srv[1:]
                    srv = srv.replace("/", "\\")
                    while "\\\\" in srv:
                        srv = srv.replace("\\\\", "\\")
                    srv = srv.strip()
                    winreg.SetValueEx(key, "Nome do ServidorSQL", 0, winreg.REG_SZ, srv)
                    winreg.SetValueEx(key, "IP do ServidorSQL", 0, winreg.REG_SZ, srv)
                if "banco" in settings:
                    winreg.SetValueEx(key, "NomeBancoSQL", 0, winreg.REG_SZ, str(settings["banco"]).strip())
                if "porta" in settings:
                    winreg.SetValueEx(key, "ProtocoloSQL", 0, winreg.REG_SZ, "TCPIP")
                if "timeout" in settings:
                    winreg.SetValueEx(key, "TimeoutConexaoSQL", 0, winreg.REG_SZ, str(settings["timeout"]))
            if user:
                winreg.SetValueEx(key, "Usuario MSSQL", 0, winreg.REG_SZ, str(user).strip())
            if password:
                try:
                    from core.criptografia import criptografia
                    pwd_enc = criptografia(40, str(password))
                except Exception:
                    pwd_enc = str(password)
                winreg.SetValueEx(key, "Senha do Banco SQL", 0, winreg.REG_SZ, pwd_enc)
            winreg.CloseKey(key)
        except Exception as e:
            logger.debug(f"Não foi possível sincronizar Registro do Windows para GeoAlvo: {e}")

    def _ler_registro_geoalvo(self):
        res = {}
        if not winreg:
            return res
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"sdit\configuracoes\DataBase")
            for field, reg_name in [
                ("servidor", "Nome do ServidorSQL"),
                ("banco", "NomeBancoSQL"),
                ("usuario", "Usuario MSSQL"),
                ("senha", "Senha do Banco SQL"),
                ("timeout", "TimeoutConexaoSQL"),
            ]:
                try:
                    val, _ = winreg.QueryValueEx(key, reg_name)
                    res[field] = str(val)
                except OSError:
                    pass
            winreg.CloseKey(key)

            if res.get("servidor"):
                srv = res["servidor"].strip()
                while srv.startswith("\\") or srv.startswith("/"):
                    srv = srv[1:]
                srv = srv.replace("/", "\\")
                while "\\\\" in srv:
                    srv = srv.replace("\\\\", "\\")
                res["servidor"] = srv.strip()

            if res.get("senha"):
                try:
                    from core.criptografia import decriptografia
                    dec = decriptografia(40, res["senha"])
                    if dec and res["senha"] != "semsenha":
                        res["senha"] = dec
                except Exception:
                    pass
        except Exception:
            pass
        return res

    def _sincronizar_registro_savic(self, user=None, password=None, settings=None):
        if not winreg:
            return
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"sdit\configuracoes\DataBase")
            if settings:
                if "host" in settings:
                    winreg.SetValueEx(key, "Nome do Servidor APP", 0, winreg.REG_SZ, str(settings["host"]))
                    winreg.SetValueEx(key, "IP do Servidor APP", 0, winreg.REG_SZ, str(settings["host"]))
                if "database" in settings:
                    winreg.SetValueEx(key, "NomeBancoAPP", 0, winreg.REG_SZ, str(settings["database"]))
                if "port" in settings:
                    winreg.SetValueEx(key, "Porta Comunicacao APP", 0, winreg.REG_SZ, str(settings["port"]))
            if user:
                winreg.SetValueEx(key, "Usuario admin APP", 0, winreg.REG_SZ, str(user))
            if password:
                winreg.SetValueEx(key, "Senha APP", 0, winreg.REG_SZ, str(password))
            winreg.SetValueEx(key, "Protocolo APP", 0, winreg.REG_SZ, "MySQL")
            winreg.CloseKey(key)
        except Exception as e:
            logger.debug(f"Não foi possível sincronizar Registro do Windows para SAVIC: {e}")

    def _ler_registro_savic(self):
        res = {}
        if not winreg:
            return res
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"sdit\configuracoes\DataBase")
            for field, reg_name in [("servidor", "Nome do Servidor APP"), ("banco", "NomeBancoAPP"), ("usuario", "Usuario admin APP"), ("senha", "Senha APP"), ("porta", "Porta Comunicacao APP")]:
                try:
                    val, _ = winreg.QueryValueEx(key, reg_name)
                    res[field] = str(val)
                except OSError:
                    pass
            winreg.CloseKey(key)
        except Exception:
            pass
        return res


class DatabaseConfigForm:
    """Formulário de Configuração de Banco de Dados com suporte a GeoAlvo (MSSQL) e SAVIC (MySQL)."""

    def __init__(self, parent=None, initial_tab: str = "MSSQL"):
        if parent is None and getattr(tk, "_default_root", None) is not None:
            parent = tk._default_root

        self.parent = parent
        if parent is not None:
            self.root = tk.Toplevel(parent)
            try:
                self.root.transient(parent)
            except Exception:
                pass
        else:
            self.root = tk.Tk()

        self.root.title("Configurador de Banco de Dados - GeoAlvo, SAVIC & Aplicativo RCC")
        self.root.geometry("640x580")
        self.root.minsize(580, 520)

        aplicar_icone_janela(self.root)

        self.salvo = False
        self.config_manager = ConfigManager()

        self._criar_interface()
        self._carregar_configuracoes()

        # Seleciona a aba solicitada
        tab_key = str(initial_tab or "").upper().strip()
        if tab_key in ("APLICATIVO", "APLICATIVO_RCC", "APP_RCC", "APP", "APLICATIVO RCC"):
            self.notebook.select(self.tab_app_rcc)
        elif tab_key in ("MYSQL", "SAVIC"):
            self.notebook.select(self.tab_savic)
        else:
            self.notebook.select(self.tab_geoalvo)

        centralizar_janela(self.root, parent, 640, 580)
        self.root.protocol("WM_DELETE_WINDOW", self.fechar)

    def _criar_interface(self):
        container = ttk.Frame(self.root, padding="15")
        container.pack(fill=tk.BOTH, expand=True)

        lbl_header = ttk.Label(
            container,
            text="CONFIGURAÇÃO DE ACESSO A BANCOS DE DADOS",
            font=("Segoe UI", 12, "bold"),
            foreground="#1E3A8A"
        )
        lbl_header.pack(pady=(0, 12))

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_geoalvo = ttk.Frame(self.notebook, padding="15")
        self.tab_savic = ttk.Frame(self.notebook, padding="15")
        self.tab_app_rcc = ttk.Frame(self.notebook, padding="15")

        self.notebook.add(self.tab_geoalvo, text=" Banco Dados GeoAlvo/Alvo (SQL Server) ")
        self.notebook.add(self.tab_savic, text=" Banco Dados SAVIC (MySQL Legado) ")
        self.notebook.add(self.tab_app_rcc, text=" Banco Dados Aplicativo RCC (MySQL) ")

        self._montar_aba_geoalvo()
        self._montar_aba_savic()
        self._montar_aba_app_rcc()

        # Barra inferior com botão fechar
        bottom_bar = ttk.Frame(container)
        bottom_bar.pack(fill=tk.X, pady=(12, 0))
        btn_sair = ttk.Button(bottom_bar, text="✖ Fechar", command=self.fechar)
        btn_sair.pack(side=tk.RIGHT)

    def _montar_aba_geoalvo(self):
        f = self.tab_geoalvo

        lbl_info = ttk.Label(
            f,
            text="Configurações de conexão para o banco principal GeoAlvo e Alvo ERP (Microsoft SQL Server):",
            wraplength=540,
            foreground="#475569"
        )
        lbl_info.pack(anchor="w", pady=(0, 15))

        grid_frame = ttk.Frame(f)
        grid_frame.pack(fill=tk.X, expand=False)

        ttk.Label(grid_frame, text="Servidor / IP:").grid(row=0, column=0, sticky="w", pady=6)
        self.geo_endereco_var = tk.StringVar(value="localhost")
        self.geo_endereco_entry = ttk.Entry(grid_frame, textvariable=self.geo_endereco_var, width=35)
        self.geo_endereco_entry.grid(row=0, column=1, sticky="w", padx=10, pady=6)

        ttk.Label(grid_frame, text="Porta TCP:").grid(row=1, column=0, sticky="w", pady=6)
        self.geo_porta_var = tk.StringVar(value="1433")
        self.geo_porta_entry = ttk.Entry(grid_frame, textvariable=self.geo_porta_var, width=15)
        self.geo_porta_entry.grid(row=1, column=1, sticky="w", padx=10, pady=6)

        ttk.Label(grid_frame, text="Catálogo / Banco:").grid(row=2, column=0, sticky="w", pady=6)
        self.geo_banco_var = tk.StringVar(value="RCC")
        self.geo_banco_entry = ttk.Entry(grid_frame, textvariable=self.geo_banco_var, width=35)
        self.geo_banco_entry.grid(row=2, column=1, sticky="w", padx=10, pady=6)

        ttk.Label(grid_frame, text="Usuário:").grid(row=3, column=0, sticky="w", pady=6)
        self.geo_usuario_var = tk.StringVar(value="sa")
        self.geo_usuario_entry = ttk.Entry(grid_frame, textvariable=self.geo_usuario_var, width=35)
        self.geo_usuario_entry.grid(row=3, column=1, sticky="w", padx=10, pady=6)

        ttk.Label(grid_frame, text="Senha:").grid(row=4, column=0, sticky="w", pady=6)
        self.geo_senha_var = tk.StringVar()
        self.geo_senha_entry = ttk.Entry(grid_frame, textvariable=self.geo_senha_var, show="*", width=35)
        self.geo_senha_entry.grid(row=4, column=1, sticky="w", padx=10, pady=6)

        ttk.Label(grid_frame, text="Timeout Conexão (seg):").grid(row=5, column=0, sticky="w", pady=6)
        self.geo_timeout_var = tk.StringVar(value="60")
        self.geo_timeout_entry = ttk.Entry(grid_frame, textvariable=self.geo_timeout_var, width=15)
        self.geo_timeout_entry.grid(row=5, column=1, sticky="w", padx=10, pady=6)

        ttk.Label(
            grid_frame,
            text="(Recomendado: 60s ou mais para bases locais)",
            font=("Segoe UI", 8),
            foreground="#6B7280"
        ).grid(row=5, column=2, sticky="w", pady=6)

        self.lbl_status_geo = ttk.Label(f, text="", foreground="#2563EB", wraplength=540)
        self.lbl_status_geo.pack(anchor="w", pady=(15, 10))

        btn_bar = ttk.Frame(f)
        btn_bar.pack(anchor="w", pady=(5, 0))

        btn_testar = ttk.Button(btn_bar, text="⚡ Testar Conexão GeoAlvo", command=self.testar_conexao_geoalvo)
        btn_testar.pack(side=tk.LEFT, padx=(0, 10))

        btn_salvar = ttk.Button(btn_bar, text="💾 Salvar Configuração GeoAlvo", command=self.salvar_config_geoalvo)
        btn_salvar.pack(side=tk.LEFT)

    def _montar_aba_savic(self):
        f = self.tab_savic

        lbl_info = ttk.Label(
            f,
            text="Configurações de conexão para o banco do sistema legado SAVIC RCC (MySQL):",
            wraplength=540,
            foreground="#475569"
        )
        lbl_info.pack(anchor="w", pady=(0, 15))

        grid_frame = ttk.Frame(f)
        grid_frame.pack(fill=tk.X, expand=False)

        ttk.Label(grid_frame, text="Servidor MySQL / IP:").grid(row=0, column=0, sticky="w", pady=6)
        self.savic_host_var = tk.StringVar(value="191.252.53.94")
        self.savic_host_entry = ttk.Entry(grid_frame, textvariable=self.savic_host_var, width=35)
        self.savic_host_entry.grid(row=0, column=1, sticky="w", padx=10, pady=6)

        ttk.Label(grid_frame, text="Porta MySQL:").grid(row=1, column=0, sticky="w", pady=6)
        self.savic_porta_var = tk.StringVar(value="3306")
        self.savic_porta_entry = ttk.Entry(grid_frame, textvariable=self.savic_porta_var, width=15)
        self.savic_porta_entry.grid(row=1, column=1, sticky="w", padx=10, pady=6)

        ttk.Label(grid_frame, text="Nome do Banco:").grid(row=2, column=0, sticky="w", pady=6)
        self.savic_banco_var = tk.StringVar(value="rccbrasilsavic")
        self.savic_banco_entry = ttk.Entry(grid_frame, textvariable=self.savic_banco_var, width=35)
        self.savic_banco_entry.grid(row=2, column=1, sticky="w", padx=10, pady=6)

        ttk.Label(grid_frame, text="Usuário Admin:").grid(row=3, column=0, sticky="w", pady=6)
        self.savic_usuario_var = tk.StringVar(value="rccbrasilsavic")
        self.savic_usuario_entry = ttk.Entry(grid_frame, textvariable=self.savic_usuario_var, width=35)
        self.savic_usuario_entry.grid(row=3, column=1, sticky="w", padx=10, pady=6)

        ttk.Label(grid_frame, text="Senha:").grid(row=4, column=0, sticky="w", pady=6)
        self.savic_senha_var = tk.StringVar(value="b2J4earCJuNcM7")
        self.savic_senha_entry = ttk.Entry(grid_frame, textvariable=self.savic_senha_var, show="*", width=35)
        self.savic_senha_entry.grid(row=4, column=1, sticky="w", padx=10, pady=6)

        self.lbl_status_savic = ttk.Label(f, text="", foreground="#2563EB", wraplength=540)
        self.lbl_status_savic.pack(anchor="w", pady=(15, 10))

        btn_bar = ttk.Frame(f)
        btn_bar.pack(anchor="w", pady=(5, 0))

        btn_testar = ttk.Button(btn_bar, text="⚡ Testar Conexão SAVIC", command=self.testar_conexao_savic)
        btn_testar.pack(side=tk.LEFT, padx=(0, 10))

        btn_salvar = ttk.Button(btn_bar, text="💾 Salvar Configuração SAVIC", command=self.salvar_config_savic)
        btn_salvar.pack(side=tk.LEFT)

    def _montar_aba_app_rcc(self):
        f = self.tab_app_rcc

        lbl_info = ttk.Label(
            f,
            text="Configurações de conexão para o banco do Aplicativo RCC (MySQL):",
            wraplength=540,
            foreground="#475569"
        )
        lbl_info.pack(anchor="w", pady=(0, 15))

        grid_frame = ttk.Frame(f)
        grid_frame.pack(fill=tk.X, expand=False)

        ttk.Label(grid_frame, text="Servidor MySQL / IP:").grid(row=0, column=0, sticky="w", pady=6)
        self.app_rcc_host_var = tk.StringVar(value="")
        self.app_rcc_host_entry = ttk.Entry(grid_frame, textvariable=self.app_rcc_host_var, width=35)
        self.app_rcc_host_entry.grid(row=0, column=1, sticky="w", padx=10, pady=6)

        ttk.Label(grid_frame, text="Porta MySQL:").grid(row=1, column=0, sticky="w", pady=6)
        self.app_rcc_porta_var = tk.StringVar(value="3306")
        self.app_rcc_porta_entry = ttk.Entry(grid_frame, textvariable=self.app_rcc_porta_var, width=15)
        self.app_rcc_porta_entry.grid(row=1, column=1, sticky="w", padx=10, pady=6)

        ttk.Label(grid_frame, text="Nome do Banco:").grid(row=2, column=0, sticky="w", pady=6)
        self.app_rcc_banco_var = tk.StringVar(value="")
        self.app_rcc_banco_entry = ttk.Entry(grid_frame, textvariable=self.app_rcc_banco_var, width=35)
        self.app_rcc_banco_entry.grid(row=2, column=1, sticky="w", padx=10, pady=6)

        ttk.Label(grid_frame, text="Usuário Admin:").grid(row=3, column=0, sticky="w", pady=6)
        self.app_rcc_usuario_var = tk.StringVar(value="")
        self.app_rcc_usuario_entry = ttk.Entry(grid_frame, textvariable=self.app_rcc_usuario_var, width=35)
        self.app_rcc_usuario_entry.grid(row=3, column=1, sticky="w", padx=10, pady=6)

        ttk.Label(grid_frame, text="Senha:").grid(row=4, column=0, sticky="w", pady=6)
        self.app_rcc_senha_var = tk.StringVar(value="")
        self.app_rcc_senha_entry = ttk.Entry(grid_frame, textvariable=self.app_rcc_senha_var, show="*", width=35)
        self.app_rcc_senha_entry.grid(row=4, column=1, sticky="w", padx=10, pady=6)

        self.lbl_status_app_rcc = ttk.Label(f, text="", foreground="#2563EB", wraplength=540)
        self.lbl_status_app_rcc.pack(anchor="w", pady=(15, 10))

        btn_bar = ttk.Frame(f)
        btn_bar.pack(anchor="w", pady=(5, 0))

        btn_testar = ttk.Button(btn_bar, text="⚡ Testar Conexão Aplicativo RCC", command=self.testar_conexao_app_rcc)
        btn_testar.pack(side=tk.LEFT, padx=(0, 10))

        btn_salvar = ttk.Button(btn_bar, text="💾 Salvar Configuração Aplicativo RCC", command=self.salvar_config_app_rcc)
        btn_salvar.pack(side=tk.LEFT)

    def _carregar_configuracoes(self):
        # Carrega GeoAlvo
        geo_settings = self.config_manager.load_settings()
        geo_creds = self.config_manager.get_db_credentials()
        if geo_settings.get("endereco"):
            self.geo_endereco_var.set(geo_settings["endereco"])
        if geo_settings.get("porta"):
            self.geo_porta_var.set(geo_settings["porta"])
        if geo_settings.get("banco"):
            self.geo_banco_var.set(geo_settings["banco"])
        if geo_creds.get("user"):
            self.geo_usuario_var.set(geo_creds["user"])
        if geo_creds.get("password"):
            self.geo_senha_var.set(geo_creds["password"])
        # Carrega Timeout do GeoAlvo
        timeout_val = geo_settings.get("timeout")
        if not timeout_val:
            reg_geo = self.config_manager._ler_registro_geoalvo()
            timeout_val = reg_geo.get("timeout")
        self.geo_timeout_var.set(str(timeout_val or "60"))

        # Carrega SAVIC
        savic_settings = self.config_manager.load_savic_settings()
        savic_creds = self.config_manager.get_savic_credentials()
        if savic_settings.get("host"):
            self.savic_host_var.set(savic_settings["host"])
        if savic_settings.get("port"):
            self.savic_porta_var.set(str(savic_settings["port"]))
        if savic_settings.get("database"):
            self.savic_banco_var.set(savic_settings["database"])
        if savic_creds.get("user"):
            self.savic_usuario_var.set(savic_creds["user"])
        if savic_creds.get("password"):
            self.savic_senha_var.set(savic_creds["password"])

        # Carrega Aplicativo RCC
        app_settings = self.config_manager.load_app_rcc_settings()
        app_creds = self.config_manager.get_app_rcc_credentials()
        if app_settings.get("host"):
            self.app_rcc_host_var.set(app_settings["host"])
        if app_settings.get("port"):
            self.app_rcc_porta_var.set(str(app_settings["port"]))
        if app_settings.get("database"):
            self.app_rcc_banco_var.set(app_settings["database"])
        if app_creds.get("user"):
            self.app_rcc_usuario_var.set(app_creds["user"])
        if app_creds.get("password"):
            self.app_rcc_senha_var.set(app_creds["password"])

    def testar_conexao_geoalvo(self):
        """Testa conexão com o SQL Server (GeoAlvo)."""
        import time
        self.lbl_status_geo.config(text="Tentando conectar ao SQL Server...", foreground="#D97706")
        self.root.update_idletasks()

        server = self.geo_endereco_var.get().strip()
        while server.startswith("\\") or server.startswith("/"):
            server = server[1:]
        server = server.replace("/", "\\")
        while "\\\\" in server:
            server = server.replace("\\\\", "\\")
        server = server.strip()
        self.geo_endereco_var.set(server)

        port = self.geo_porta_var.get().strip()
        db = self.geo_banco_var.get().strip()
        user = self.geo_usuario_var.get().strip()
        pwd = self.geo_senha_var.get()

        timeout_str = self.geo_timeout_var.get().strip()
        try:
            timeout_seg = int(timeout_str) if timeout_str else 60
            if timeout_seg <= 0:
                timeout_seg = 60
        except ValueError:
            timeout_seg = 60

        if port and port != "1433" and "," not in server:
            server_str = f"{server},{port}"
        else:
            server_str = server

        try:
            import pyodbc
            drivers = pyodbc.drivers()
            driver = "ODBC Driver 17 for SQL Server"
            if "ODBC Driver 18 for SQL Server" in drivers:
                driver = "ODBC Driver 18 for SQL Server"
            elif "ODBC Driver 17 for SQL Server" in drivers:
                driver = "ODBC Driver 17 for SQL Server"
            elif "SQL Server" in drivers:
                driver = "SQL Server"

            conn_str = f"DRIVER={{{driver}}};SERVER={server_str};DATABASE={db};UID={user};PWD={pwd};Connection Timeout={timeout_seg};TrustServerCertificate=yes;"
            t0 = time.time()
            conn = pyodbc.connect(conn_str, timeout=timeout_seg)
            conn.close()
            ms = int((time.time() - t0) * 1000)
            msg = f"✔ Conexão com GeoAlvo (SQL Server) estabelecida com sucesso! ({ms} ms)"
            self.lbl_status_geo.config(text=msg, foreground="#16A34A")
            messagebox.showinfo("Sucesso", msg, parent=self.root)
        except Exception as exc:
            msg = f"✖ Falha na conexão com GeoAlvo: {exc}"
            self.lbl_status_geo.config(text=msg, foreground="#DC2626")
            messagebox.showerror("Erro de Conexão", msg, parent=self.root)

    def salvar_config_geoalvo(self):
        """Salva parâmetros do SQL Server no settings.json, keyring e registro."""
        server = self.geo_endereco_var.get().strip()
        while server.startswith("\\") or server.startswith("/"):
            server = server[1:]
        server = server.replace("/", "\\")
        while "\\\\" in server:
            server = server.replace("\\\\", "\\")
        server = server.strip()
        self.geo_endereco_var.set(server)

        port = self.geo_porta_var.get().strip()
        db = self.geo_banco_var.get().strip()
        user = self.geo_usuario_var.get().strip()
        pwd = self.geo_senha_var.get()

        if not server or not db or not user:
            messagebox.showwarning("Atenção", "Preencha Servidor, Banco e Usuário.", parent=self.root)
            return

        timeout_str = self.geo_timeout_var.get().strip()
        try:
            timeout_val = int(timeout_str)
            if timeout_val <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Atenção", "O timeout de conexão deve ser um número inteiro positivo (em segundos).", parent=self.root)
            self.geo_timeout_entry.focus_set()
            return

        self.config_manager.save_db_credentials(user, pwd)
        self.config_manager.save_settings({
            "db_type": "SQL Server",
            "endereco": server,
            "porta": port,
            "banco": db,
            "timeout": timeout_val
        })
        self.salvo = True
        msg = f"Configurações do GeoAlvo (SQL Server) salvas com sucesso! (Timeout: {timeout_val}s)"
        self.lbl_status_geo.config(text="✔ " + msg, foreground="#16A34A")
        messagebox.showinfo("Sucesso", msg, parent=self.root)

    def testar_conexao_savic(self):
        """Testa conexão com o MySQL (SAVIC)."""
        import time
        self.lbl_status_savic.config(text="Tentando conectar ao MySQL SAVIC...", foreground="#D97706")
        self.root.update_idletasks()

        host = self.savic_host_var.get().strip()
        try:
            port = int(self.savic_porta_var.get().strip() or 3306)
        except ValueError:
            port = 3306
        db = self.savic_banco_var.get().strip()
        user = self.savic_usuario_var.get().strip()
        pwd = self.savic_senha_var.get()

        try:
            import pymysql
            t0 = time.time()
            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=pwd,
                database=db,
                connect_timeout=10
            )
            conn.close()
            ms = int((time.time() - t0) * 1000)
            msg = f"✔ Conexão com SAVIC (MySQL) estabelecida com sucesso! ({ms} ms)"
            self.lbl_status_savic.config(text=msg, foreground="#16A34A")
            messagebox.showinfo("Sucesso", msg, parent=self.root)
        except Exception as exc:
            msg = f"✖ Falha na conexão com SAVIC (MySQL): {exc}"
            self.lbl_status_savic.config(text=msg, foreground="#DC2626")
            messagebox.showerror("Erro de Conexão", msg, parent=self.root)

    def salvar_config_savic(self):
        """Salva parâmetros do SAVIC no settings.json, keyring e registro."""
        host = self.savic_host_var.get().strip()
        port = self.savic_porta_var.get().strip() or "3306"
        db = self.savic_banco_var.get().strip()
        user = self.savic_usuario_var.get().strip()
        pwd = self.savic_senha_var.get()

        if not host or not db or not user:
            messagebox.showwarning("Atenção", "Preencha Servidor, Banco e Usuário do SAVIC.", parent=self.root)
            return

        self.config_manager.save_savic_credentials(user, pwd)
        self.config_manager.save_savic_settings({
            "host": host,
            "port": port,
            "database": db
        })
        self.salvo = True
        msg = "Configurações do SAVIC (MySQL) salvas com sucesso!"
        self.lbl_status_savic.config(text="✔ " + msg, foreground="#16A34A")
        messagebox.showinfo("Sucesso", msg, parent=self.root)

    def testar_conexao_app_rcc(self):
        """Testa conexão com o MySQL do Aplicativo RCC."""
        import time
        self.lbl_status_app_rcc.config(text="Tentando conectar ao MySQL do Aplicativo RCC...", foreground="#D97706")
        self.root.update_idletasks()

        host = self.app_rcc_host_var.get().strip()
        try:
            port = int(self.app_rcc_porta_var.get().strip() or 3306)
        except ValueError:
            port = 3306
        db = self.app_rcc_banco_var.get().strip()
        user = self.app_rcc_usuario_var.get().strip()
        pwd = self.app_rcc_senha_var.get()

        try:
            import pymysql
            t0 = time.time()
            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=pwd,
                database=db,
                connect_timeout=10
            )
            conn.close()
            ms = int((time.time() - t0) * 1000)
            msg = f"✔ Conexão com Aplicativo RCC (MySQL) estabelecida com sucesso! ({ms} ms)"
            self.lbl_status_app_rcc.config(text=msg, foreground="#16A34A")
            messagebox.showinfo("Sucesso", msg, parent=self.root)
        except Exception as exc:
            msg = f"✖ Falha na conexão com Aplicativo RCC (MySQL): {exc}"
            self.lbl_status_app_rcc.config(text=msg, foreground="#DC2626")
            messagebox.showerror("Erro de Conexão", msg, parent=self.root)

    def salvar_config_app_rcc(self):
        """Salva parâmetros do Aplicativo RCC no settings.json, keyring e registro."""
        host = self.app_rcc_host_var.get().strip()
        port = self.app_rcc_porta_var.get().strip() or "3306"
        db = self.app_rcc_banco_var.get().strip()
        user = self.app_rcc_usuario_var.get().strip()
        pwd = self.app_rcc_senha_var.get()

        if not host or not db or not user:
            messagebox.showwarning("Atenção", "Preencha Servidor, Banco e Usuário do Aplicativo RCC.", parent=self.root)
            return

        self.config_manager.save_app_rcc_credentials(user, pwd)
        self.config_manager.save_app_rcc_settings({
            "host": host,
            "port": port,
            "database": db
        })
        self.salvo = True
        msg = "Configurações do Aplicativo RCC (MySQL) salvas com sucesso!"
        self.lbl_status_app_rcc.config(text="✔ " + msg, foreground="#16A34A")
        messagebox.showinfo("Sucesso", msg, parent=self.root)

    def fechar(self):
        try:
            self.root.grab_release()
        except Exception:
            pass
        self.root.destroy()

    def run(self):
        if isinstance(self.root, tk.Tk):
            self.root.mainloop()
        else:
            try:
                self.root.focus_set()
                self.root.grab_set()
                self.root.wait_window(self.root)
            except Exception:
                pass


if __name__ == "__main__":
    app = DatabaseConfigForm()
    app.run()