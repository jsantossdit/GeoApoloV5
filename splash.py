import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import sys
import subprocess
from core import obter_caminho_recurso

class SplashScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GeoAlvo V5")
        self.root.overrideredirect(True)  # Remove bordas e botões da janela
        
        # Configurações da versão
        self.versao = "5.0.0.1"
        
        # Caminho da imagem
        self.caminho_imagem = obter_caminho_recurso(os.path.join("Imagens", "Assinatura_SDIT.jpg"))

        
        # Configurar e exibir splash
        self.criar_splash()
        self.centralizar_janela()
        
        # Permitir avanço imediato ao clicar ou pressionar tecla
        self.root.bind("<Button-1>", lambda e: self.fechar_splash())
        self.root.bind("<Key>", lambda e: self.fechar_splash())
        
        # Fechar splash após 4 segundos
        self._after_id = self.root.after(4000, self.fechar_splash)
        
    def criar_splash(self):
        try:
            # Tentar carregar a imagem
            if os.path.exists(self.caminho_imagem):
                # Abrir e redimensionar imagem se necessário
                img = Image.open(self.caminho_imagem)
                # Manter proporção original da imagem
                self.photo = ImageTk.PhotoImage(img)
                
                # Ajustar tamanho da janela baseado na imagem
                largura_img = img.width
                altura_img = img.height
                
            else:
                # Criar imagem placeholder se não encontrar a imagem
                largura_img = 600
                altura_img = 200
                img_placeholder = Image.new('RGB', (largura_img, altura_img), color='lightblue')
                self.photo = ImageTk.PhotoImage(img_placeholder)
                
            # Altura adicional para versão e margem
            altura_adicional = 80
            
            # Configurar tamanho da janela
            self.largura_janela = largura_img + 40  # Margem lateral
            self.altura_janela = altura_img + altura_adicional
            
            # Frame principal
            main_frame = tk.Frame(self.root, bg='white', relief='raised', bd=2)
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Label para imagem
            img_label = tk.Label(main_frame, image=self.photo, bg='white')
            img_label.pack(pady=10)
            
            # Label para versão
            versao_label = tk.Label(
                main_frame,
                text=f"Versão {self.versao}",
                font=("Arial", 12, "bold"),
                fg="darkblue",
                bg="white"
            )
            versao_label.pack(pady=5)
            
            # Barra de progresso (opcional - para dar feedback visual)
            self.progress = ttk.Progressbar(
                main_frame,
                mode='indeterminate',
                length=300
            )
            self.progress.pack(pady=10)
            self.progress.start(10)  # Animação da barra
            
        except Exception as e:
            print(f"Erro ao criar splash: {e}")
            # Criar splash simples em caso de erro
            self.criar_splash_simples()
    
    def criar_splash_simples(self):
        """Cria um splash simples caso haja problema com a imagem"""
        self.largura_janela = 400
        self.altura_janela = 300
        
        main_frame = tk.Frame(self.root, bg='lightblue', relief='raised', bd=2)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Título
        titulo_label = tk.Label(
            main_frame,
            text="GeoAlvo V5",
            font=("Arial", 24, "bold"),
            fg="darkblue",
            bg="lightblue"
        )
        titulo_label.pack(pady=30)
        
        # Versão
        versao_label = tk.Label(
            main_frame,
            text=f"Versão {self.versao}",
            font=("Arial", 12, "bold"),
            fg="darkblue",
            bg="lightblue"
        )
        versao_label.pack(pady=10)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=300
        )
        self.progress.pack(pady=20)
        self.progress.start(10)
        

    
    def centralizar_janela(self):
        """Centraliza a janela na tela"""
        # Atualizar para obter dimensões corretas        
        self.root.update_idletasks()  # garante medidas finais

        largura_janela = self.root.winfo_width()
        altura_janela  = self.root.winfo_height()

        largura_tela = self.root.winfo_screenwidth()
        altura_tela  = self.root.winfo_screenheight()

        x = (largura_tela - largura_janela) // 2
        y = (altura_tela - altura_janela) // 2
        self.root.geometry(f"{largura_janela}x{altura_janela}+{x}+{y}")
        
    
    def fechar_splash(self):
        """Fecha splash e abre logon oficial"""
        if hasattr(self, '_after_id') and self._after_id:
            try:
                self.root.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        try:
            if hasattr(self, 'progress'):
                self.progress.stop()
        except Exception:
            pass
        self.root.destroy()
        self.abrir_logon()
    
    def abrir_logon(self):
        """Abre a tela de logon oficial (logon.py) com validação real"""
        try:
            import logon
            app = logon.TelaLogon()
            app.root.mainloop()
        except Exception as e:
            import traceback
            traceback.print_exc()
            from tkinter import messagebox
            messagebox.showerror("Erro ao Iniciar", f"Não foi possível abrir o formulário de login:\n\n{e}")
            sys.exit(1)
    
    def executar(self):
        """Executa o splash screen"""
        self.root.mainloop()

if __name__ == "__main__":
    # Verificar se PIL está instalado
    try:
        from PIL import Image, ImageTk
    except ImportError:
        print("Pillow não está instalado. Instale com: pip install Pillow")
        sys.exit(1)
    
    splash = SplashScreen()
    splash.executar()