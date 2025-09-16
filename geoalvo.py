import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import time
from config_banco import DatabaseConfigForm
from toolbar_geoalvo import ToolbarManager

root = tk.Tk()
def abrir_config_banco(root):
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
    root.state('zoomed') # maximiza a janela

    # =============================================
    # Barra de menu (PRIMEIRO)
    # =============================================
    menu_bar = tk.Menu(root)

    # Menu Configurações
    config_menu = tk.Menu(menu_bar, tearoff=0)
    config_menu.add_command(label="Banco de Dados", command=lambda: abrir_config_banco(root))
    
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
    cadatfmenu = tk.Menu(cadastros_menu, tearoff=0)    
    cadatfmenu.add_command(label="Ativo Imobilizado")
    cadatfmenu.add_command(label="Categoria de Bens")
    cadatfmenu.add_command(label="Classificação de Ativos")
    cadatfmenu.add_command(label="Estações de Trabalho")
    cadatfmenu.add_command(label="Localização Física")
    cadatfmenu.add_command(label="Status de Hardware/Software")
    cadatfmenu.add_command(label="Tipos de Licenças de Software")
    cadastros_menu.add_cascade(label="Ativo Fixo", menu=cadatfmenu)  
    # 
    cadcctrlmenu = tk.Menu(cadastros_menu,tearoff=0)
    cadcctrlmenu.add_command(label="Centro de Custos/Controle")
    cadastros_menu.add_cascade(label="Manutenção Centro de controle", menu=cadcctrlmenu)
    # 
    cadcrm = tk.Menu(cadastros_menu, tearoff=0)
    cadcrm.add_command(label="Cadastros de &Eventos")
    cadcrm.add_command(label="Cadastros de Tipos de Campanhas")
    cadastros_menu.add_cascade(label="CRM",menu=cadcrm)
    # 
    cadentidades = tk.Menu(cadastros_menu, tearoff=0)
    cadentidades.add_command(label="Categorias")
    cadentidades.add_command(label="Entidades")
    cadentidades.add_command(label="Importa Entidades")
    cadentidades.add_command(label="Tipos de Tratamento")
    cadastros_menu.add_cascade(label="Entidades", menu=cadentidades)
    # 
    cadfinanc = tk.Menu(cadastros_menu, tearoff=0)
    cadfinanc.add_command(label="Plano de Classes de Receitas/Despesas")
    cadfinanc.add_command(label="Manutenção de Cartões de Crédito")
    cadfinanc.add_command(label="Situação Financeira de Documentos")
    cadfinanc.add_command(label="tipos de Cobrança")
    cadastros_menu.add_cascade(label="Financeiro", menu=cadfinanc)
    # 
    cadestoque = tk.Menu(cadastros_menu, tearoff=0)
    cadestoque.add_command(label="Cores")
    cadestoque.add_command(label="Marcas")
    cadestoque.add_command(label="Produtos")
    cadastros_menu.add_cascade(label="Estoque",menu=cadestoque)
    # 
    cadgeral = tk.Menu(cadastros_menu, tearoff=0)
    cadgeral.add_command(label="Departamentos")
    cadgeral.add_command(label="Empresas")
    cadastros_menu.add_cascade(label="Geral", menu=cadgeral)
    # 
    cadastros_menu.add_command(label="Usuários GeoApolo")   
    
    menu_bar.add_cascade(label="Cadastros", menu=cadastros_menu)

    # Menu GeoApolo
    geoapolo_menu = tk.Menu(menu_bar, tearoff=0)    
    gamenuativofixo = tk.Menu(geoapolo_menu, tearoff=0)
    gamenuativofixo.add_command(label="Atualiza Inventário de TI")
    geoapolo_menu.add_cascade(label="Ativo Fixo", menu=gamenuativofixo)
    # 
    gamenufinanc = tk.Menu(menu_bar, tearoff=0)
    # 
    gamenufinancapagar = tk.Menu(gamenufinanc, tearoff=0)
    gamenufinancapagar.add_command(label="Controle de Cartões de Crédito")
    geoapolo_menu.add_cascade(label="Contas a Pagar", menu=gamenufinancapagar)
    # 
    gamenufinancareceber = tk.Menu(gamenufinanc, tearoff=0)
    gamenufinancareceber.add_command(label="Documentos a Receber")
    geoapolo_menu.add_cascade(label="Contas a Receber", menu=gamenufinancareceber)
    # 
    gamenuintegrasavic = tk.Menu(geoapolo_menu, tearoff=0)
    gamenuintegrasavic.add_command(label="Importa Grupos de Oração(GO) Savic")
    gamenuintegrasavic.add_command(label="Moderação de Grupos de Oração Savic x Alvo")
    gamenuintegrasavic.add_command(label="Valida Entidades Alvo x Savic")
    gamenuintegrasavic.add_command(label="Importa entidades Savic -> GeoAlvo")
    geoapolo_menu.add_cascade(label="Integração Savic x Alvo", menu=gamenuintegrasavic)
    menu_bar.add_cascade(label="Geoapolo", menu=geoapolo_menu)
    # 
    # Menu Alvo
    alvo_menu = tk.Menu(menu_bar, tearoff=0)
    alvoloja = tk.Menu(alvo_menu, tearoff=0)
    alvoloja.add_command(label="Auditoria de Cupons Fiscais")
    alvoloja.add_command(label="Troca Cupom Fiscal nomeado por Consumidor Final")
    alvo_menu.add_cascade(label="Alvo Loja", menu=alvoloja)
    # 
    alvocontabilidade = tk.Menu(alvo_menu, tearoff=0)
    alvocontabilidade.add_command(label="Débito x Crédito")
    alvocontabilidade.add_command(label="Débito x Crédito Detalhado")
    alvocontabilidade.add_command(label="Exclui Lançamentos Contábeis")
    alvocontabilidade.add_command(label="Corrige Lançamentos de Cupom Fiscal")
    alvo_menu.add_cascade(label="Contabilidade",menu=alvocontabilidade)
    # 
    alvocrm = tk.Menu(alvo_menu, tearoff=0)
    alvocrm.add_command(label="Administração de Campanhas")
    alvocrm.add_command(label="Atualiza Valores de Campanhas")
    alvocrm.add_command(label="E-Mail Marketing de Campanhas")
    alvocrm.add_command(label="TeleMarketing de Campanhas")
    alvocrm.add_command(label="Soluções de Ocorrências")
    alvocrm.add_command(label="Mesclagem de Entidades")
    alvocrmrcc= tk.Menu(alvocrm, tearoff=0)
    alvocrmrcc.add_command(label="Importa Monitoramento Lembrete de Doações")
    alvocrmrcc.add_command(label="Integração Congressos ONLINE x Alvo x RdStation")
    alvocrmrcc.add_command(label="Vincula Entidade a Diocese")
    alvocrm.add_cascade(label="RCC", menu=alvocrmrcc)
    alvo_menu.add_cascade(label="CRM", menu=alvocrm)
    # 
    alvoentidade = tk.Menu(alvo_menu, tearoff=0)
    alvoentidade.add_command(label="Relaciona Usuário com Categoria")
    alvoentidade.add_command(label="Relaciona Usuários, Categorias e Entidades")
    alvoentidade.add_command(label="Relaciona Entidade com Diocese")
    alvo_menu.add_cascade(label="Entidades", menu=alvoentidade)
    # 
    alvofinanceiro = tk.Menu(alvo_menu, tearoff=0)
    alvofinanceiro.add_command(label="Gera Títulos a Receber no Alvo")
    alvofinanceiro.add_command(label="Gera Remessa para Bancos")
    alvofinanceiro.add_command(label="Débito x Crédito de Conta Financeira")
    alvofinanceiro.add_command(label="Atualiza Situação de Títulos")
    alvofinanceiro.add_command(label="Conciliação Vindi Crédito Recorrente(RCC)")
    alvo_menu.add_cascade(label="Financeiro", menu=alvofinanceiro)
    # 
    alvolocalidade = tk.Menu(alvo_menu, tearoff=0)
    alvolocalidade.add_command(label="Correção de Distritos cadastrados como Cidades")
    alvo_menu.add_cascade(label="Localidades", menu=alvolocalidade)
    # 
    alvoestoque = tk.Menu(alvo_menu, tearoff=0)
    alvoestoque.add_command(label="Cores")
    alvoestoque.add_command(label="Marcas")
    alvoestoque.add_command(label="Produtos")
    alvo_menu.add_cascade(label="Estoque", menu=alvoestoque)
    # 
    alvogeral = tk.Menu(alvo_menu, tearoff=0)
    alvogeral.add_command(label="Departamentos")
    alvogeral.add_command(label="Empresas")
    alvo_menu.add_cascade(label="Geral", menu=alvogeral)
    # 
    alvousersalvo = tk.Menu(alvo_menu, tearoff=0)
    alvousersalvo.add_command(label="Desativa Usuários do Alvo")
    alvousersalvo.add_command(label="Clonar Permissão de Usuários")
    alvousersalvo.add_command(label="Permissão em Contas Financeiras")
    alvo_menu.add_cascade(label="Usuários do Alvo", menu=alvousersalvo)
    # 
    menu_bar.add_cascade(label="Alvo", menu=alvo_menu)
    # 
    # Menu Utilitários
    utilitarios_menu = tk.Menu(menu_bar, tearoff=0)
    utilmenuimediatas = tk.Menu(menu_bar, tearoff=0)        
    utilmenuimediatas.add_command(label="Cadastrar Consultas")
    utilmenuimediatas.add_command(label="Executar Consultas")
    # 
    utilitarios_menu.add_cascade(label="Consultas Imediatas", menu=utilmenuimediatas)    
    utilitarios_menu.add_command(label="Validação de Licenças")
    utilitarios_menu.add_command(label="Enviar E-Mail via GeoAlvo F8")
    # 
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