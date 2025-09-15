import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk


import os

class ToolbarManager:
    """Classe para gerenciar a barra de ferramentas"""
    
    def __init__(self, parent):
        self.parent = parent
        self.buttons = {}
        self.icons = {}
        self.create_toolbar()
        
    def create_toolbar(self):
        """Cria a estrutura da toolbar"""
        # Frame principal da toolbar
        self.toolbar = tk.Frame(self.parent, bd=1, relief=tk.RAISED, bg='#f0f0f0')
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Configuração dos botões da toolbar
        self.toolbar_config = [            
            # Seção: Banco de Dados
            {'name': 'config_bd', 'icon': 'database.png', 'text': 'Configura', 'command': 'abrir_config_banco', 'tooltip': 'Configurar Acesso ao Banco de dados (Ctrl+B+D)'},
            {'type': 'separator'},

            # Seção: Arquivo
            # {'name': 'novo', 'icon': 'new.png', 'text': 'Config BD', 'command': self.novo_banco, 'tooltip': 'ajustar'},
            {'name': 'troca_empresa', 'icon': 'company.png', 'text': 'Troca Emporesa', 'command': 'self.change_company', 'tooltip': 'Troca de empresa no sistema'},
            {'name': 'salvar', 'icon': 'save.png', 'text': 'Salvar', 'command': self.salvar_arquivo, 'tooltip': 'Salvar arquivo (Ctrl+S)'},
            {'type': 'separator'},
            
            # Seção: Relatórios
            {'name': 'relatorio', 'icon': 'report.png', 'text': 'Relatório', 'command': self.gerar_relatorio, 'tooltip': 'Gerar relatório'},
            {'name': 'imprimir', 'icon': 'print.png', 'text': 'Imprimir', 'command': self.imprimir, 'tooltip': 'Imprimir documento (Ctrl+P)'},
            {'type': 'separator'},
            
            # Seção: Sistema
            {'name': 'usuarios', 'icon': 'users.png', 'text': 'Usuários', 'command': self.gerenciar_usuarios, 'tooltip': 'Gerenciar usuários'},
            {'name': 'config', 'icon': 'settings.png', 'text': 'Config', 'command': self.configuracoes, 'tooltip': 'Configurações do sistema'},
            {'type': 'separator'},
            
            # Seção: Sair
            {'name': 'sair', 'icon': 'dooropen.jpeg', 'text': 'Sair', 'command': self.sair_aplicacao, 'tooltip': 'Sair do sistema'}
        ]
        
        self.create_buttons()
    
    def create_buttons(self):
        """Cria os botões baseado na configuração"""
        for item in self.toolbar_config:
            if item.get('type') == 'separator':
                self.add_separator()
            else:
                self.add_button(item)
    
    def add_button(self, config):
        """Adiciona um botão à toolbar"""
        name = config['name']
        icon_path = config['icon']
        text = config['text']
        command = config['command']
        tooltip = config.get('tooltip', '')
        
        # Carrega o ícone
        icon = self.load_icon(icon_path, size=(24, 24))
        
        if icon:
            btn = tk.Button(
                self.toolbar, 
                image=icon, 
                command=command,
                relief=tk.FLAT,
                bd=1,
                padx=5,
                pady=2,
                bg='#f0f0f0',
                activebackground='#e0e0e0',
                cursor='hand2'
            )
            # Manter referência da imagem
            btn.image = icon
        else:
            # Fallback para texto se não carregar o ícone
            btn = tk.Button(
                self.toolbar, 
                text=text, 
                command=command,
                relief=tk.FLAT,
                bd=1,
                padx=8,
                pady=4,
                bg='#f0f0f0',
                activebackground='#e0e0e0',
                cursor='hand2'
            )
        
        btn.pack(side=tk.LEFT, padx=1, pady=2)
        
        # Adicionar tooltip
        if tooltip:
            self.create_tooltip(btn, tooltip)
        
        # Efeitos hover
        btn.bind("<Enter>", lambda e, b=btn: self.on_enter(b))
        btn.bind("<Leave>", lambda e, b=btn: self.on_leave(b))
        
        # Salvar referência
        self.buttons[name] = btn
    
    def add_separator(self):
        """Adiciona um separador vertical"""
        separator = tk.Frame(self.toolbar, width=2, height=30, bg='#d0d0d0', relief=tk.SUNKEN, bd=1)
        separator.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
    
    def load_icon(self, filename, size=(24, 24)):
        """Carrega um ícone com tratamento de erro"""
        base_path = r"E:\Julio\Projetos-Programas\Projetos-Python\GeoApoloV5\Imagens"
        full_path = os.path.join(base_path, filename)
        
        try:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                # Usar PIL para redimensionar
                image = Image.open(full_path)
                image = image.resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(image)
            else:
                # Para arquivos .gif nativos do tkinter
                return tk.PhotoImage(file=full_path)
        except Exception as e:
            print(f"Erro ao carregar ícone {filename}: {e}")
            return None
    
    def create_tooltip(self, widget, text):
        """Cria tooltip para um widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.configure(bg='#ffffe0', relief='solid', bd=1)
            
            label = tk.Label(tooltip, text=text, bg='#ffffe0', fg='black', 
                           font=('Arial', 8), padx=4, pady=2)
            label.pack()
            
            x = event.x_root + 10
            y = event.y_root + 10
            tooltip.geometry(f"+{x}+{y}")
            
            # Remove tooltip após 3 segundos
            widget.tooltip = tooltip
            tooltip.after(3000, tooltip.destroy)
        
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
    
    def on_enter(self, button):
        """Efeito hover - entrada"""
        button.config(relief=tk.RAISED, bg='#e6f3ff')
    
    def on_leave(self, button):
        """Efeito hover - saída"""
        button.config(relief=tk.FLAT, bg='#f0f0f0')
    
    def enable_button(self, name):
        """Habilita um botão específico"""
        if name in self.buttons:
            self.buttons[name].config(state=tk.NORMAL)
    
    def disable_button(self, name):
        """Desabilita um botão específico"""
        if name in self.buttons:
            self.buttons[name].config(state=tk.DISABLED)
    
    def update_button_state(self, name, enabled=True):
        """Atualiza estado de um botão"""
        if enabled:
            self.enable_button(name)
        else:
            self.disable_button(name)
    
    # ==========================================
    # MÉTODOS DE COMANDO DOS BOTÕES
    # ==========================================
    
    def novo_arquivo(self):
        messagebox.showinfo("","Config. BD")
    
    def abrir_arquivo(self):
        messagebox.showinfo("Abrir", "Abrir arquivo")
    
    def salvar_arquivo(self):
        messagebox.showinfo("Salvar", "Salvar arquivo")
    
    def config_banco(self):
        messagebox.showinfo("", "Configurar Banco de Dados")
    
    def conectar_banco(self):
        messagebox.showinfo("Conectar", "Conectar ao banco")
    
    def gerar_relatorio(self):
        messagebox.showinfo("Relatório", "Gerar relatório")
    
    def imprimir(self):
        messagebox.showinfo("Imprimir", "Imprimir documento")
    
    def gerenciar_usuarios(self):
        messagebox.showinfo("Usuários", "Gerenciar usuários")
    
    def configuracoes(self):
        messagebox.showinfo("Configurações", "Configurações do sistema")
    
    def sair_aplicacao(self):
        if messagebox.askokcancel("Sair", "Deseja realmente sair do sistema?"):
            self.parent.quit()
            self.parent.destroy()

# # ==========================================
# # EXEMPLO DE USO
# # ==========================================

# def main():
#     root = tk.Tk()
#     root.title("Sistema GeoAlvo - Toolbar Profissional")
#     root.geometry("800x600")
    
#     # Criar a toolbar
#     toolbar_manager = ToolbarManager(root)
    
#     # Exemplo de como controlar botões
#     # toolbar_manager.disable_button('salvar')  # Desabilitar botão salvar
#     # toolbar_manager.enable_button('salvar')   # Habilitar botão salvar
    
#     # Área principal
#     main_frame = tk.Frame(root, bg='white')
#     main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
#     label = tk.Label(main_frame, text="Área principal do sistema", 
#                     font=('Arial', 14), bg='white')
#     label.pack(pady=50)
    
#     root.mainloop()

# if __name__ == "__main__":
#     main()