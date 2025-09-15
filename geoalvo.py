import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import time
from config_banco import DatabaseConfigForm
from toolbar_geoalvo import ToolbarManager

def abrir_config_banco():
    """Abre o formulário de configuração do banco de dados"""
    try:
        config_form = DatabaseConfigForm()
        config_form.root.transient(root)
        config_form.root.update_idletasks()
        width, height = 600, 500
        x = (config_form.root.winfo_screenwidth() // 2) - (width // 2)
        y = (config_form.root.winfo_screenheight() // 2) - (height // 2)
        config_form.root.geometry(f'{width}x{height}+{x}+{y}')
        config_form.run()
    except Exception as e:
        print(f"Erro ao abrir configuração do banco: {e}")

def sair_aplicacao():
    """Função para sair da aplicação"""
    if messagebox.askokcancel("Sair", "Deseja realmente sair do sistema?"):
        root.quit()
        root.destroy()

def atualizar_relogio(label_relogio):
    """Atualiza o relógio da barra de status"""
    hora_atual = time.strftime("%H:%M:%S")
    label_relogio.config(text=hora_atual)
    label_relogio.after(1000, atualizar_relogio, label_relogio)

def main():
    global root
    root = tk.Tk()
    root.title("GeoAlvo - Sistema de Gestão Integrada v5.0")
    
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight() - 40
    root.geometry(f"{largura_tela}x{altura_tela}+0+0")

    # =============================================
    # Barra de menu (PRIMEIRO)
    # =============================================
    menu_bar = tk.Menu(root)

    # Menu Configurações
    config_menu = tk.Menu(menu_bar, tearoff=0)
    config_menu.add_command(label="Banco de Dados", command=abrir_config_banco)
    
    sistema_menu = tk.Menu(config_menu, tearoff=0)
    sistema_menu.add_command(label="Parâmetros GeoApolo/Alvo")
    sistema_menu.add_command(label="Manutenção de Versões do GeoApolo")
    sistema_menu.add_command(label="Manutenção de Códigos do Sistema")
    config_menu.add_cascade(label="Parâmetros do Sistema", menu=sistema_menu)
    
    permissoes_menu = tk.Menu(config_menu, tearoff=0)
    permissoes_menu.add_command(label="Administração de Usuários")
    permissoes_menu.add_command(label="Permissões de Grupos e Usuários")
    permissoes_menu.add_command(label="Permissões de Grupos")
    config_menu.add_cascade(label="Permissões de Acesso", menu=permissoes_menu)
    
    config_menu.add_command(label="Trocar de Empresa <F2>")
    menu_bar.add_cascade(label="Configurações", menu=config_menu)

    # Menu Cadastros
    cadastros_menu = tk.Menu(menu_bar, tearoff=0)
    cadastros_menu.add_command(label="Usuários GeoApolo")
    menu_bar.add_cascade(label="Cadastros", menu=cadastros_menu)

    # Menu GeoApolo
    geoapolo_menu = tk.Menu(menu_bar, tearoff=0)
    geoapolo_menu.add_command(label="Atualiza Inventário de TI")
    menu_bar.add_cascade(label="Geoapolo", menu=geoapolo_menu)

    # Menu Alvo
    alvo_menu = tk.Menu(menu_bar, tearoff=0)
    alvo_menu.add_command(label="Auditoria de Cupons Fiscais")
    menu_bar.add_cascade(label="Alvo", menu=alvo_menu)

    # Menu Utilitários
    utilitarios_menu = tk.Menu(menu_bar, tearoff=0)
    utilitarios_menu.add_command(label="Validação de Licenças")
    menu_bar.add_cascade(label="Utilitários", menu=utilitarios_menu)

    # Comando Sair no menu principal
    menu_bar.add_command(label="Sair", command=sair_aplicacao)
    
    # Configura o menu na janela
    root.config(menu=menu_bar)

    # Criar a toolbar
    toolbar_manager = ToolbarManager(root)
    
    toolbar_manager.disable_button('Config. BD')  # Desabilitar botão salvar
    toolbar_manager.enable_button('Config. BD')   # Habilitar botão salvar

    # =============================================
    # Barra de status (TERCEIRO - no bottom)
    # =============================================
    status_bar = tk.Frame(root, bd=1, relief=tk.SUNKEN)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    painel1 = tk.Label(status_bar, text="Banco Alvo", bd=1, relief=tk.SUNKEN, anchor='w')
    painel1.pack(side=tk.LEFT, padx=2, ipadx=10, fill=tk.Y)
    
    painel2 = tk.Label(status_bar, text="Nome do Banco Alvo", bd=1, relief=tk.SUNKEN, anchor='w')
    painel2.pack(side=tk.LEFT, padx=2, ipadx=10, fill=tk.Y)
    
    painel3 = tk.Label(status_bar, text="Banco GeoAlvo", bd=1, relief=tk.SUNKEN, anchor='w')
    painel3.pack(side=tk.LEFT, padx=2, ipadx=10, fill=tk.Y)
    
    painel4 = tk.Label(status_bar, text="Nome do Banco GeoAlvo", bd=1, relief=tk.SUNKEN, anchor='w')
    painel4.pack(side=tk.LEFT, padx=2, ipadx=10, fill=tk.Y)
    
    painel5 = tk.Label(status_bar, text="Hora Oficial", bd=1, relief=tk.SUNKEN, anchor='w')
    painel5.pack(side=tk.LEFT, padx=2, ipadx=10, fill=tk.Y)
    
    painel6 = tk.Label(status_bar, bd=1, relief=tk.SUNKEN, anchor='w')
    painel6.pack(side=tk.LEFT, padx=2, ipadx=10, fill=tk.Y)

    # Inicia o relógio
    atualizar_relogio(painel6)

    # =============================================
    # Canvas principal com imagem de fundo (QUARTO)
    # =============================================
    canvas = tk.Canvas(root, width=largura_tela, height=altura_tela)
    canvas.pack(fill=tk.BOTH, expand=True)

    # Carrega imagem de fundo
    caminho_imagem = r"E:\Julio\Projetos-Programas\Projetos-Python\GeoApoloV5\Imagens\fundo_gradiente.jpeg"
    try:
        imagem = Image.open(caminho_imagem)
        imagem = imagem.resize((largura_tela, altura_tela), Image.Resampling.LANCZOS)
        imagem_fundo = ImageTk.PhotoImage(imagem)
        canvas.create_image(0, 0, anchor="nw", image=imagem_fundo)
        # Manter referência da imagem
        canvas.imagem_fundo = imagem_fundo
    except Exception as e:
        print(f"Erro ao carregar imagem de fundo: {e}")

    # =============================================
    # Área principal sobre o canvas
    # =============================================
    main_frame = tk.Frame(root, bg="#ffffff", bd=0)
    canvas.create_window(largura_tela*0.05, altura_tela*0.05, anchor='nw',
                         window=main_frame, width=largura_tela*0.9, height=altura_tela*0.8)

    welcome_label = tk.Label(main_frame, 
                             text="Sistema GeoAlvo V5.0\nBem-vindo ao Sistema!", 
                             font=("Arial", 16, "bold"),
                             bg="#ffffff", fg='darkblue')
    welcome_label.pack(pady=50)

    root.mainloop()

if __name__ == "__main__":
    main()