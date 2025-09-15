import tkinter as tk
from tkinter import ttk, messagebox
import os
import keyring
from pathlib import Path
import json

class ConfigManager:
    def __init__(self, app_name="meuapp"):
        self.app_name = app_name
        self.config_dir = self._get_config_dir()
        
    def _get_config_dir(self):
        if os.name == 'nt':
            return Path(os.environ['APPDATA']) / self.app_name
        return Path.home() / f'.{self.app_name}'
    
    def save_db_credentials(self, user, password):
        keyring.set_password(self.app_name, "db_user", user)
        keyring.set_password(self.app_name, "db_password", password)
    
    def get_db_credentials(self):
        return {
            'user': keyring.get_password(self.app_name, "db_user"),
            'password': keyring.get_password(self.app_name, "db_password")
        }
    
    def save_settings(self, settings):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_dir / 'settings.json', 'w') as f:
            json.dump(settings, f, indent=2)
    
    def load_settings(self):
        settings_file = self.config_dir / 'settings.json'
        if settings_file.exists():
            with open(settings_file, 'r') as f:
                return json.load(f)
        return {}

class DatabaseConfigForm:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Configuração do Banco de Dados")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Mantém a janela sempre na frente e com foco
        self.root.attributes('-topmost', True)
        self.root.focus_force()
        
        # Configurações de porta padrão por banco
        self.default_ports = {
            "SQL Server": "1433",
            "MySQL": "3306",
            "PostgreSQL": "5432",
            "SQLite": ""
        }
        
        self.config_manager = ConfigManager()
        self.create_widgets()
        self.load_existing_config()
        
        # Remove o topmost após 500ms para não interferir com outras janelas
        self.root.after(500, lambda: self.root.attributes('-topmost', False))
        
    def centralizar_janela(self):
        """Centraliza a janela na tela usando o tamanho real atual."""
        # Atualiza para garantir medidas finais da janela
        self.root.update_idletasks()

        # Captura o tamanho real da janela
        largura_janela = self.root.winfo_width()
        altura_janela  = self.root.winfo_height()

        # Captura o tamanho da tela
        largura_tela = self.root.winfo_screenwidth()
        altura_tela  = self.root.winfo_screenheight()

        # Calcula coordenadas para centralizar
        x = (largura_tela - largura_janela) // 2
        y = (altura_tela - altura_janela) // 2

        # Aplica posição e tamanho
        self.root.geometry(f"{largura_janela}x{altura_janela}+{x}+{y}")

        # Garante que a janela fique em evidência
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(500, lambda: self.root.attributes("-topmost", False))

    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="CONFIGURAÇÃO DO BANCO DE DADOS", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Campo Banco de Dados
        ttk.Label(main_frame, text="Banco de Dados:").pack(anchor="w", pady=(10, 5))
        self.db_type_var = tk.StringVar()
        self.db_combo = ttk.Combobox(main_frame, textvariable=self.db_type_var, 
                                    values=["SQL Server", "MySQL", "PostgreSQL", "SQLite"],
                                    state="readonly", width=40)
        self.db_combo.pack(pady=(0, 10), fill="x")
        self.db_combo.bind('<Return>', self.on_db_enter)
        self.db_combo.bind('<Tab>', self.on_db_enter)
        
        # Campo Endereço
        ttk.Label(main_frame, text="Endereço do Banco de Dados:").pack(anchor="w", pady=(10, 5))
        self.endereco_var = tk.StringVar()
        self.endereco_entry = ttk.Entry(main_frame, textvariable=self.endereco_var, width=40)
        self.endereco_entry.pack(pady=(0, 10), fill="x")
        self.endereco_entry.bind('<Return>', self.on_endereco_enter)
        self.endereco_entry.bind('<Tab>', self.on_endereco_enter)
        
        # Campo Porta
        ttk.Label(main_frame, text="Porta:").pack(anchor="w", pady=(10, 5))
        self.porta_var = tk.StringVar()
        self.porta_combo = ttk.Combobox(main_frame, textvariable=self.porta_var, width=40)
        self.porta_combo.pack(pady=(0, 10), fill="x")
        self.porta_combo.bind('<FocusIn>', self.on_porta_focus)
        self.porta_combo.bind('<Return>', self.on_porta_enter)
        self.porta_combo.bind('<Tab>', self.on_porta_enter)
        
        # Campo Usuário
        ttk.Label(main_frame, text="Usuário SA do Banco:").pack(anchor="w", pady=(10, 5))
        self.usuario_var = tk.StringVar()
        self.usuario_entry = ttk.Entry(main_frame, textvariable=self.usuario_var, width=40)
        self.usuario_entry.pack(pady=(0, 10), fill="x")
        self.usuario_entry.bind('<Return>', self.on_usuario_enter)
        self.usuario_entry.bind('<Tab>', self.on_usuario_enter)
        
        # Campo Senha
        ttk.Label(main_frame, text="Senha do Banco de Dados:").pack(anchor="w", pady=(10, 5))
        self.senha_var = tk.StringVar()
        self.senha_entry = ttk.Entry(main_frame, textvariable=self.senha_var, 
                                   show="*", width=40)
        self.senha_entry.pack(pady=(0, 20), fill="x")
        self.senha_entry.bind('<Return>', self.on_senha_enter)
        self.senha_entry.bind('<Tab>', self.on_senha_enter)
        
        # Frame dos botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(20, 0))
        
        # Botão Salvar (com ícone simulado)
        self.btn_salvar = ttk.Button(button_frame, text="💾 Salvar", 
                                   command=self.salvar_config)
        self.btn_salvar.pack(side="left", padx=(0, 10))
        
        # Botão Cancelar
        self.btn_cancelar = ttk.Button(button_frame, text="❌ Cancelar", 
                                     command=self.cancelar)
        self.btn_cancelar.pack(side="left")
        
        # Definir foco inicial
        self.db_combo.focus()
    
    def on_db_enter(self, event=None):
        """Evento quando pressiona Enter/Tab no combo do banco"""
        self.endereco_entry.focus()
        return "break"
    
    def on_endereco_enter(self, event=None):
        """Evento quando pressiona Enter/Tab no campo endereço"""
        if not self.endereco_var.get().strip():
            messagebox.showwarning("Campo Obrigatório", 
                                 "O campo 'Endereço do Banco de Dados' é obrigatório!")
            self.endereco_entry.focus()
            return "break"
        
        self.porta_combo.focus()
        return "break"
    
    def on_porta_focus(self, event=None):
        """Evento quando o foco entra no combo da porta"""
        db_type = self.db_type_var.get()
        if db_type in self.default_ports:
            default_port = self.default_ports[db_type]
            if db_type == "SQLite":
                self.porta_combo.configure(state="disabled")
                self.porta_var.set("")
            else:
                self.porta_combo.configure(state="normal")
                if not self.porta_var.get():  # Se estiver vazio, define a porta padrão
                    self.porta_var.set(default_port)
                # Permite edição das portas conhecidas
                self.porta_combo.configure(values=[default_port, "1433", "3306", "5432"])
    
    def on_porta_enter(self, event=None):
        """Evento quando pressiona Enter/Tab no campo porta"""
        # Se for SQLite, pula validação de porta
        if self.db_type_var.get() == "SQLite":
            self.usuario_entry.focus()
            return "break"
            
        if not self.porta_var.get().strip():
            messagebox.showwarning("Campo Obrigatório", 
                                 "O campo 'Porta' é obrigatório!")
            self.porta_combo.focus()
            return "break"
        
        self.usuario_entry.focus()
        return "break"
    
    def on_usuario_enter(self, event=None):
        """Evento quando pressiona Enter/Tab no campo usuário"""
        if not self.usuario_var.get().strip():
            messagebox.showwarning("Campo Obrigatório", 
                                 "O campo 'Usuário SA do Banco' é obrigatório!")
            self.usuario_entry.focus()
            return "break"
        
        self.senha_entry.focus()
        return "break"
    
    def on_senha_enter(self, event=None):
        """Evento quando pressiona Enter/Tab no campo senha"""
        if not self.senha_var.get().strip():
            messagebox.showwarning("Campo Obrigatório", 
                                 "O campo 'Senha' é obrigatório!")
            self.senha_entry.focus()
            return "break"
        
        # Se chegou até aqui, simula click no botão salvar
        self.btn_salvar.focus()
        self.salvar_config()
        return "break"
    
    def salvar_config(self):
        """Salva as configurações"""
        # Validações finais
        if not self.db_type_var.get():
            messagebox.showwarning("Atenção", "Selecione um banco de dados!")
            self.db_combo.focus()
            return
            
        if not self.endereco_var.get().strip():
            messagebox.showwarning("Atenção", "O endereço do banco é obrigatório!")
            self.endereco_entry.focus()
            return
        
        if self.db_type_var.get() != "SQLite" and not self.porta_var.get().strip():
            messagebox.showwarning("Atenção", "A porta é obrigatória!")
            self.porta_combo.focus()
            return
            
        if not self.usuario_var.get().strip():
            messagebox.showwarning("Atenção", "O usuário é obrigatório!")
            self.usuario_entry.focus()
            return
            
        if not self.senha_var.get().strip():
            messagebox.showwarning("Atenção", "A senha é obrigatória!")
            self.senha_entry.focus()
            return
        
        try:
            # Salvar credenciais sensíveis no keyring
            self.config_manager.save_db_credentials(
                self.usuario_var.get(), 
                self.senha_var.get()
            )
            
            # Salvar configurações gerais em arquivo
            settings = {
                "db_type": self.db_type_var.get(),
                "endereco": self.endereco_var.get(),
                "porta": self.porta_var.get() if self.db_type_var.get() != "SQLite" else ""
            }
            
            self.config_manager.save_settings(settings)
            
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            self.root.destroy()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {str(e)}")
    
    def load_existing_config(self):
        """Carrega configurações existentes"""
        try:
            settings = self.config_manager.load_settings()
            if settings:
                self.db_type_var.set(settings.get("db_type", ""))
                self.endereco_var.set(settings.get("endereco", ""))
                self.porta_var.set(settings.get("porta", ""))
            
            credentials = self.config_manager.get_db_credentials()
            if credentials.get("user"):
                self.usuario_var.set(credentials["user"])
            if credentials.get("password"):
                self.senha_var.set(credentials["password"])
                
        except Exception as e:
            print(f"Aviso: Não foi possível carregar configurações existentes: {e}")
    
    def cancelar(self):
        """Fecha o programa"""
        self.root.destroy()
    
    def run(self):
        """Executa o formulário"""
        self.root.mainloop()

# Executar o formulário
if __name__ == "__main__":
    app = DatabaseConfigForm()
    app.run()