import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sys
import os

class TelaLogon:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login - GeoAlvo V5.0.0.1")
        self.root.resizable(False, False)

        self.caminho_logo = r"E:\Julio\Projetos-Programas\Projetos-Python\GeoApoloV5\Imagens\Assinatura_SDIT.jpg"
        
        # Criar interface
        self.criar_interface()
        
        # Configurar eventos
        self.configurar_eventos()
        
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

    
    def criar_interface(self):
        """Cria a interface da tela de logon"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0', padx=50, pady=30)
        main_frame.pack(fill='both', expand=True)
        
        # Título
        titulo_frame = tk.Frame(main_frame, bg='#f0f0f0')
        titulo_frame.pack(pady=(0, 30))
        
        # Logo (se existir)
        self.carregar_logo(titulo_frame)
        
        titulo = tk.Label(titulo_frame, 
                         text="GeoAlvo V5", 
                         font=("Times New Roman", 24, "bold"), 
                         fg='#2c3e50',
                         bg='#f0f0f0')
        titulo.pack(pady=(10, 0))
        
        subtitulo = tk.Label(titulo_frame, 
                           text="Sistema de Gestão Empresarial", 
                           font=("Arial", 10), 
                           fg='#7f8c8d',
                           bg='#f0f0f0')
        subtitulo.pack()
        
        # Frame dos campos
        campos_frame = tk.Frame(main_frame, bg='#f0f0f0')
        campos_frame.pack(pady=20, fill='x')
        
        # Campo Usuário
        tk.Label(campos_frame, text="Usuário:", 
                font=("Arial", 12, "bold"), 
                bg='#f0f0f0', 
                fg='#2c3e50').pack(anchor='w')
        
        self.entry_usuario = tk.Entry(campos_frame, 
                                     font=("Arial", 11), 
                                     relief='solid',
                                     bd=1)
        self.entry_usuario.pack(pady=(5, 15), fill='x')
        
        # Campo Senha
        tk.Label(campos_frame, text="Senha:", 
                font=("Arial", 12, "bold"), 
                bg='#f0f0f0', 
                fg='#2c3e50').pack(anchor='w')
        
        self.entry_senha = tk.Entry(campos_frame, 
                                   show="*", 
                                   font=("Arial", 11), 
                                   relief='solid',
                                   bd=1)
        self.entry_senha.pack(pady=(5, 20), fill='x')
        
        # Frame dos botões
        botoes_frame = tk.Frame(main_frame, bg='#f0f0f0')
        botoes_frame.pack(pady=20)
        
        # Botão Entrar
        self.btn_entrar = tk.Button(botoes_frame, 
                                   text="Entrar", 
                                   font=("Arial", 11, "bold"),
                                   bg='#3498db',
                                   fg='white',
                                   width=12,
                                   height=2,
                                   relief='flat',
                                   command=self.fazer_login)
        self.btn_entrar.pack(side='left', padx=10)
        
        # Botão Sair
        btn_sair = tk.Button(botoes_frame, 
                            text="Sair", 
                            font=("Arial", 11, "bold"),
                            bg='#e74c3c',
                            fg='white',
                            width=12,
                            height=2,
                            relief='flat',
                            command=self.sair_aplicacao)
        btn_sair.pack(side='left', padx=10)
        
        # Versão no rodapé
        versao_label = tk.Label(main_frame, 
                               text="Versão 5.0.0.1", 
                               font=("Arial", 9), 
                               fg='#95a5a6',
                               bg='#f0f0f0')
        versao_label.pack(side='bottom', pady=(30, 0))
        
    def carregar_logo(self, parent_frame):
        """Carrega e exibe o logo"""
        try:
            if os.path.exists(self.caminho_logo):
                # Carregar e redimensionar logo
                img = Image.open(self.caminho_logo)
                
                # Redimensionar logo para ficar proporcional na tela de login
                largura_max = 350
                altura_max = 80
                
                img.thumbnail((largura_max, altura_max), Image.Resampling.LANCZOS)
                
                self.logo_photo = ImageTk.PhotoImage(img)
                
                logo_label = tk.Label(parent_frame, 
                                    image=self.logo_photo, 
                                    bg='#f0f0f0')
                logo_label.pack(pady=(0, 10))
                
            else:
                # Se não encontrar o logo, criar um placeholder
                logo_placeholder = tk.Label(parent_frame,
                                          text="[LOGO SDIT]",
                                          font=("Arial", 10),
                                          fg='#bdc3c7',
                                          bg='#f0f0f0')
                logo_placeholder.pack(pady=(0, 10))
                
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")
            # Placeholder em caso de erro
            logo_placeholder = tk.Label(parent_frame,
                                      text="[LOGO SDIT]",
                                      font=("Arial", 10),
                                      fg='#bdc3c7',
                                      bg='#f0f0f0')
            logo_placeholder.pack(pady=(0, 10))
        
    def configurar_eventos(self):
        """Configura eventos da interface"""
        # Enter no campo usuário vai para senha
        self.entry_usuario.bind('<Return>', lambda e: self.entry_senha.focus_set())
        
        # Enter no campo senha faz login
        self.entry_senha.bind('<Return>', lambda e: self.fazer_login())
        
        # Focar no campo usuário
        self.entry_usuario.focus_set()
        
        # Evento de fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.sair_aplicacao)
    
    def fazer_login(self):
        """Processa o login do usuário"""
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get().strip()
        
        # Validações básicas
        if not usuario:
            messagebox.showwarning("Atenção", "Por favor, digite o usuário!")
            self.entry_usuario.focus_set()
            return
            
        if not senha:
            messagebox.showwarning("Atenção", "Por favor, digite a senha!")
            self.entry_senha.focus_set()
            return
        
        # Aqui você implementaria a validação real contra banco de dados
        if self.validar_usuario(usuario, senha):
            messagebox.showinfo("Sucesso", f"Bem-vindo, {usuario}!")
            self.root.destroy()
            self.abrir_sistema_principal()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos!")
            self.entry_senha.delete(0, 'end')
            self.entry_usuario.focus_set()
    
    def validar_usuario(self, usuario, senha):
        """Valida usuário e senha (implementar com banco de dados real)"""
        # Validação temporária para testes
        usuarios_validos = {
            'admin': 'admin',
            'user': '123',
            'julio': 'julio'
        }
        
        return usuarios_validos.get(usuario.lower()) == senha
    
    def abrir_sistema_principal(self):
        """Abre o sistema principal"""
        try:
            # Tentar abrir o geoalvo.py
            caminho_geoalvo = os.path.join(os.path.dirname(__file__), 'geoalvo.py')
            
            if os.path.exists(caminho_geoalvo):
                import subprocess
                subprocess.run([sys.executable, caminho_geoalvo])
            else:
                # Se não encontrar geoalvo.py, tentar main.py
                caminho_main = os.path.join(os.path.dirname(__file__), 'main.py')
                
                if os.path.exists(caminho_main):
                    import subprocess
                    subprocess.run([sys.executable, caminho_main])
                else:
                    # Se não encontrar nenhum, mostrar mensagem
                    messagebox.showinfo("Sistema", "Sistema principal carregado com sucesso!\n(Criar arquivo geoalvo.py)")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir sistema principal: {e}")
    
    def sair_aplicacao(self):
        """Sai da aplicação"""
        if messagebox.askokcancel("Sair", "Deseja realmente sair do sistema?"):
            self.root.destroy()
            sys.exit()
    
    def executar(self):
        """Executa a tela de logon"""
        self.root.mainloop()

if __name__ == "__main__":
    logon = TelaLogon()
    logon.executar()