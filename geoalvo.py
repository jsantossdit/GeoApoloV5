import os
import sys
from pathlib import Path

# Garante que o diretório raiz do projeto esteja no sys.path
_raiz_projeto = str(Path(__file__).resolve().parent)
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import time
from config_banco import DatabaseConfigForm
from toolbar_geoalvo import ToolbarManager
from core import obter_caminho_recurso


root = None
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

def abrir_entidades(parent):
    """Abre a janela de gestão de entidades"""
    try:
        from entidades import EntidadesView
        EntidadesView(parent)
    except Exception as e:
        print(f"Erro ao abrir módulo de entidades: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir módulo de entidades:\n{e}")

def abrir_relatorios(parent):
    """Abre a Central de Relatórios"""
    try:
        from relatorios import RelatoriosView
        RelatoriosView(parent)
    except Exception as e:
        print(f"Erro ao abrir relatórios: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir relatórios:\n{e}")

def abrir_estacoes(parent):
    """Abre o módulo de Gestão de Estações de Trabalho e Inventário de TI"""
    try:
        from estacoes import EstacoesView
        EstacoesView(parent)
    except Exception as e:
        print(f"Erro ao abrir estações: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir módulo de estações:\n{e}")

def abrir_configuracoes_sistema(parent, tab_index=0):
    """Abre a tela de Parâmetros e Configurações Gerais do Sistema"""
    try:
        from configuracoes import ConfiguracoesView
        ConfiguracoesView(parent, tab_index=tab_index)
    except Exception as e:
        print(f"Erro ao abrir configurações do sistema: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir configurações do sistema:\n{e}")

def abrir_categorias(parent):
    """Abre a tela de Gestão e Associação de Categorias de Entidades"""
    try:
        from categorias import CategoriasEntidadeView
        CategoriasEntidadeView(parent)
    except Exception as e:
        print(f"Erro ao abrir categorias: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir categorias:\n{e}")

def abrir_cores(parent):
    """Abre a tela de Cadastro de Cores de Produtos e Estoque Auxiliar"""
    try:
        from cores import abrir_janela_cores
        abrir_janela_cores(parent)
    except Exception as e:
        print(f"Erro ao abrir cadastro de cores: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir cadastro de cores:\n{e}")


def abrir_ativo_imobilizado(parent):
    """Abre a tela de Gestão de Ativo Imobilizado & Depreciação"""
    try:
        from ativo_imobilizado import AtivoImobilizadoView
        AtivoImobilizadoView(parent)
    except Exception as e:
        print(f"Erro ao abrir ativo imobilizado: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir ativo imobilizado:\n{e}")

def abrir_clonar_permissoes(parent):
    """Abre a tela de Clonagem e Replicação de Permissões de Usuários"""
    try:
        from permissoes import ClonarPermissoesView
        ClonarPermissoesView(parent)
    except Exception as e:
        print(f"Erro ao abrir clonagem de permissões: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir clonagem de permissões:\n{e}")

def abrir_contas_financeiras_usuario(parent):
    """Abre a tela de Permissão de Usuários em Contas Financeiras"""
    try:
        from permissoes import UsuarioContasFinView
        UsuarioContasFinView(parent)
    except Exception as e:
        print(f"Erro ao abrir permissões de contas financeiras: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir permissões de contas financeiras:\n{e}")

def abrir_desligamento_usuarios(parent):
    """Abre a tela de Desativação e Desligamento de Usuários"""
    try:
        from permissoes import DesligamentoUsuarioView
        DesligamentoUsuarioView(parent)
    except Exception as e:
        print(f"Erro ao abrir desligamento de usuários: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir desligamento de usuários:\n{e}")

def abrir_exclusao_contabil(parent):
    """Abre a tela de Exclusão e Auditoria de Lançamentos Contábeis"""
    try:
        from contabilidade import ExclusaoContabilView
        ExclusaoContabilView(parent)
    except Exception as e:
        print(f"Erro ao abrir exclusão contábil: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir exclusão contábil:\n{e}")

def abrir_debxcred(parent):
    """Abre a tela de Conciliação Débito x Crédito"""
    try:
        from contabilidade import DebxCredView
        DebxCredView(parent)
    except Exception as e:
        print(f"Erro ao abrir conciliação débito x crédito: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir conciliação débito x crédito:\n{e}")

def abrir_importa_eventos(parent):
    """Abre a tela de Importação de Inscrições de Eventos e Congressos"""
    try:
        from eventos import ImportarInscritosEventosView
        ImportarInscritosEventosView(parent)
    except Exception as e:
        print(f"Erro ao abrir importação de eventos: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir importação de eventos:\n{e}")

def abrir_auditoria_cupons(parent):
    """Abre a tela de Auditoria e Conciliação de Cupons Fiscais (NFC-e)"""
    try:
        from fiscal import AuditoriaCuponsView
        AuditoriaCuponsView(parent)
    except Exception as e:
        print(f"Erro ao abrir auditoria de cupons: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir auditoria de cupons:\n{e}")

def abrir_concilia_vindi(parent):
    """Abre a tela de Conciliação Vindi e Crédito Recorrente RCC"""
    try:
        from vindi import ConciliacaoVindiView
        ConciliacaoVindiView(parent)
    except Exception as e:
        print(f"Erro ao abrir conciliação vindi: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir conciliação vindi:\n{e}")

def abrir_corrigecidadedistrito(parent):
    """Abre a tela de Correção de Distritos Cadastrados como Cidades"""
    try:
        from localidades import CorrecaoCidadesDistritosView
        CorrecaoCidadesDistritosView(parent)
    except Exception as e:
        print(f"Erro ao abrir correção de cidades/distritos: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir correção de cidades/distritos:\n{e}")

def abrir_relaciona_diocese_entidade(parent):
    """Abre a tela de Relacionamento de Entidades RCC com Dioceses da CNBB"""
    try:
        from dioceses import RelacionaDioceseEntidadeView
        RelacionaDioceseEntidadeView(parent)
    except Exception as e:
        print(f"Erro ao abrir relacionamento de diocese e entidade: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir relacionamento de diocese e entidade:\n{e}")

def abrir_usuarios_sistema(parent, tab_index=0):
    """Abre a tela unificada de Gestão de Usuários, Grupos e Perfis de Acesso"""
    try:
        from usuarios import UsuariosView
        top = tk.Toplevel(parent)
        top.title("Gestão de Usuários, Grupos e Perfis de Acesso - GeoAlvo")
        top.geometry("1050x660")
        top.minsize(850, 520)
        view = UsuariosView(top)
        view.pack(fill=tk.BOTH, expand=True)
        if tab_index > 0:
            view.notebook.select(tab_index)
    except Exception as e:
        print(f"Erro ao abrir gestão de usuários: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir gestão de usuários:\n{e}")

def abrir_consultas_sistema(parent, tab_index=0):
    """Abre o Motor de Consultas Dinâmicas & Permissões SQL"""
    try:
        from consultas import ConsultasView
        top = tk.Toplevel(parent)
        top.title("Motor de Consultas Dinâmicas & Permissões SQL - GeoAlvo")
        top.geometry("1050x640")
        top.minsize(850, 500)
        view = ConsultasView(top)
        view.pack(fill=tk.BOTH, expand=True)
        if tab_index > 0:
            view.notebook.select(tab_index)
    except Exception as e:
        print(f"Erro ao abrir consultas dinâmicas: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir consultas dinâmicas:\n{e}")

def abrir_matchcode_sistema(parent, tab_index=0):
    """Abre a Unificação de Cadastros e Duplicidades (MatchCode)"""
    try:
        from matchcode import MatchCodeView
        top = tk.Toplevel(parent)
        top.title("Unificação de Cadastros Duplicados (MatchCode) - GeoAlvo")
        top.geometry("850x520")
        top.minsize(700, 420)
        view = MatchCodeView(top)
        view.pack(fill=tk.BOTH, expand=True)
        if tab_index > 0:
            view.notebook.select(tab_index)
    except Exception as e:
        print(f"Erro ao abrir MatchCode: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir MatchCode:\n{e}")

def abrir_empresas_sistema(parent, tab_index=0):
    """Abre a tela de Multi-Empresas e Seleção de Contexto Corporativo (<F2>)"""
    try:
        from empresas import EmpresasView
        top = tk.Toplevel(parent)
        top.title("Multi-Empresas & Contexto Corporativo - GeoAlvo")
        top.geometry("880x560")
        top.minsize(720, 440)
        view = EmpresasView(top)
        view.pack(fill=tk.BOTH, expand=True)
        if tab_index > 0:
            view.notebook.select(tab_index)
    except Exception as e:
        print(f"Erro ao abrir empresas: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir empresas:\n{e}")

def abrir_crm_sistema(parent, tab_index=0):
    """Abre a Central de CRM (Ocorrências, Campanhas, Tratamentos)."""
    try:
        from crm import CRMView
        top = tk.Toplevel(parent)
        top.title("Gestão de CRM, Campanhas & Ocorrências - GeoAlvo")
        top.geometry("1020x680")
        top.minsize(850, 520)
        view = CRMView(top, codigo_empresa=getattr(parent, "empresa_ativa", "01"))
        view.pack(fill=tk.BOTH, expand=True)
        if tab_index > 0:
            view.notebook.select(tab_index)
    except Exception as e:
        print(f"Erro ao abrir CRM: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir CRM:\n{e}")

def abrir_manutencao_versoes_sistema(parent):
    """Abre a tela de Manutenção de Versões e Release Notes do GeoApolo"""
    try:
        from licenciamento import abrir_manutencao_versoes
        abrir_manutencao_versoes(parent)
    except Exception as e:
        print(f"Erro ao abrir manutenção de versões: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir manutenção de versões:\n{e}")

def abrir_validacao_licenca_sistema(parent):
    """Abre a tela de Validação e Ativação de Licenças do Sistema"""
    try:
        from licenciamento import abrir_validacao_licenca
        abrir_validacao_licenca(parent)
    except Exception as e:
        print(f"Erro ao abrir validação de licenças: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir validação de licenças:\n{e}")

def abrir_manutencao_codigos_sistema_menu(parent):
    """Abre a tela de Manutenção de Códigos e Sequenciais do Sistema"""
    try:
        from configcod import abrir_manutencao_codigos_sistema
        abrir_manutencao_codigos_sistema(parent)
    except Exception as e:
        print(f"Erro ao abrir manutenção de códigos: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir manutenção de códigos:\n{e}")

def abrir_nomes_amigaveis_sistema(parent):
    """Abre a tela do Dicionário de Nomes Amigáveis de Telas e Controles"""
    try:
        from nomesamigaveis import abrir_janela_nomes_amigaveis
        abrir_janela_nomes_amigaveis(parent)
    except Exception as e:
        print(f"Erro ao abrir dicionário de nomes amigáveis: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir dicionário de nomes amigáveis:\n{e}")

def abrir_departamentos_sistema(parent):
    """Abre a tela de Gestão de Departamentos e Seções"""
    try:
        from departamentos import abrir_janela_departamentos
        abrir_janela_departamentos(parent)
    except Exception as e:
        print(f"Erro ao abrir departamentos: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir departamentos:\n{e}")

def abrir_sobre_sistema_menu(parent):
    """Abre a janela com informações técnicas e Sobre o GeoAlvo"""
    try:
        from autenticacao import abrir_sobre_sistema
        abrir_sobre_sistema(parent)
    except Exception as e:
        print(f"Erro ao abrir Sobre o Sistema: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir Sobre o Sistema:\n{e}")

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
    
    # Atualiza o contexto corporativo e o título da janela principal
    try:
        from logon import sessao_usuario_atual
        cod_emp = sessao_usuario_atual.get("codigo_empresa", "")
        nome_emp = sessao_usuario_atual.get("nome_empresa", "")
        root.empresa_ativa = cod_emp or "1.01"
        root.nome_empresa_ativa = nome_emp
        if cod_emp and nome_emp:
            root.title(f"GeoAlvo V5.0 - {cod_emp} - {nome_emp}")
        else:
            root.title("GeoAlvo - Sistema de Gestão Integrada v5.0")
    except Exception:
        root.title("GeoAlvo - Sistema de Gestão Integrada v5.0")
    
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight() - 40
    root.geometry(f"{largura_tela}x{altura_tela}+0+0")
    root.state('zoomed') # maximiza a janela

    # Configura ícone oficial da aplicação se disponível
    caminho_icone = obter_caminho_recurso(os.path.join("Imagens", "GeoApolo_Icon.ico"))
    if os.path.exists(caminho_icone):
        try:
            root.iconbitmap(caminho_icone)
        except Exception:
            pass

    # =============================================
    # Barra de menu (PRIMEIRO)
    # =============================================
    menu_bar = tk.Menu(root)

    # Menu Configurações
    config_menu = tk.Menu(menu_bar, tearoff=0)
    config_menu.add_command(label="Banco de Dados & Servidores", command=lambda: abrir_configuracoes_sistema(root, 3))

    
    sistema_menu = tk.Menu(config_menu, tearoff=0)
    sistema_menu.add_command(label="Parâmetros GeoApolo/Alvo", command=lambda: abrir_configuracoes_sistema(root))
    sistema_menu.add_command(label="Manutenção de Versões do GeoApolo", command=lambda: abrir_manutencao_versoes_sistema(root))
    sistema_menu.add_command(label="Manutenção de Códigos do Sistema", command=lambda: abrir_manutencao_codigos_sistema_menu(root))
    config_menu.add_cascade(label="Parâmetros do Sistema", menu=sistema_menu)
    
    permissoes_menu = tk.Menu(config_menu, tearoff=0)
    permissoes_menu.add_command(label="Administração de Usuários", command=lambda: abrir_usuarios_sistema(root, 0))
    permissoes_menu.add_command(label="Permissões de Grupos e Usuários", command=lambda: abrir_usuarios_sistema(root, 1))
    permissoes_menu.add_command(label="Permissões de Grupos", command=lambda: abrir_usuarios_sistema(root, 2))
    permissoes_menu.add_command(label="Clonar Permissões de Usuários", command=lambda: abrir_clonar_permissoes(root))
    permissoes_menu.add_command(label="Permissão em Contas Financeiras", command=lambda: abrir_contas_financeiras_usuario(root))
    permissoes_menu.add_command(label="Desativação / Desligamento de Usuários", command=lambda: abrir_desligamento_usuarios(root))
    permissoes_menu.add_command(label="Mesclagem / MatchCode de Usuários", command=lambda: abrir_matchcode_sistema(root, 0))
    permissoes_menu.add_command(label="Dicionário de Nomes Amigáveis", command=lambda: abrir_nomes_amigaveis_sistema(root))
    config_menu.add_cascade(label="Permissões de Acesso", menu=permissoes_menu)
    
    config_menu.add_command(label="Trocar de Empresa <F2>", command=lambda: abrir_empresas_sistema(root, 0))
    menu_bar.add_cascade(label="Configurações", menu=config_menu)

    # Menu Cadastros
    cadastros_menu = tk.Menu(menu_bar, tearoff=0)
    cadatfmenu = tk.Menu(cadastros_menu, tearoff=0)    
    cadatfmenu.add_command(label="Ativo Imobilizado", command=lambda: abrir_ativo_imobilizado(root))
    cadatfmenu.add_command(label="Categoria de Bens")
    cadatfmenu.add_command(label="Classificação de Ativos")
    cadatfmenu.add_command(label="Estações de Trabalho", command=lambda: abrir_estacoes(root))
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
    cadcrm.add_command(label="Ocorrências & Chamados", command=lambda: abrir_crm_sistema(root, 0))
    cadcrm.add_command(label="Cadastros de &Eventos", command=lambda: abrir_crm_sistema(root, 0))
    cadcrm.add_command(label="Importar Inscritos de Eventos", command=lambda: abrir_importa_eventos(root))
    cadcrm.add_command(label="Cadastros de Tipos de Campanhas", command=lambda: abrir_crm_sistema(root, 1))
    cadcrm.add_command(label="Cadastros de Tipos de Tratamento", command=lambda: abrir_crm_sistema(root, 2))
    cadastros_menu.add_cascade(label="CRM", menu=cadcrm)
    # 
    cadentidades = tk.Menu(cadastros_menu, tearoff=0)
    cadentidades.add_command(label="Categorias", command=lambda: abrir_categorias(root))
    cadentidades.add_command(label="Entidades", command=lambda: abrir_entidades(root))
    cadentidades.add_command(label="Importa Entidades")
    cadentidades.add_command(label="Tipos de Tratamento", command=lambda: abrir_crm_sistema(root, 2))
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
    cadestoque.add_command(label="Cores", command=lambda: abrir_cores(root))
    cadestoque.add_command(label="Marcas")
    cadestoque.add_command(label="Produtos")
    cadastros_menu.add_cascade(label="Estoque",menu=cadestoque)
    # 
    cadgeral = tk.Menu(cadastros_menu, tearoff=0)
    cadgeral.add_command(label="Departamentos", command=lambda: abrir_departamentos_sistema(root))
    cadgeral.add_command(label="Empresas", command=lambda: abrir_empresas_sistema(root, 1))
    cadastros_menu.add_cascade(label="Geral", menu=cadgeral)
    # 
    cadastros_menu.add_command(label="Usuários GeoApolo", command=lambda: abrir_usuarios_sistema(root, 0))   
    
    menu_bar.add_cascade(label="Cadastros", menu=cadastros_menu)

    # Menu GeoApolo
    geoapolo_menu = tk.Menu(menu_bar, tearoff=0)    
    gamenuativofixo = tk.Menu(geoapolo_menu, tearoff=0)
    gamenuativofixo.add_command(label="Atualiza Inventário de TI", command=lambda: abrir_estacoes(root))
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
    alvoloja.add_command(label="Auditoria de Cupons Fiscais", command=lambda: abrir_auditoria_cupons(root))
    alvoloja.add_command(label="Troca Cupom Fiscal nomeado por Consumidor Final")
    alvo_menu.add_cascade(label="Alvo Loja", menu=alvoloja)
    # 
    alvocontabilidade = tk.Menu(alvo_menu, tearoff=0)
    alvocontabilidade.add_command(label="Débito x Crédito", command=lambda: abrir_debxcred(root))
    alvocontabilidade.add_command(label="Débito x Crédito Detalhado", command=lambda: abrir_debxcred(root))
    alvocontabilidade.add_command(label="Exclui Lançamentos Contábeis", command=lambda: abrir_exclusao_contabil(root))
    alvocontabilidade.add_command(label="Corrige Lançamentos de Cupom Fiscal")
    alvo_menu.add_cascade(label="Contabilidade", menu=alvocontabilidade)
    # 
    alvocrm = tk.Menu(alvo_menu, tearoff=0)
    alvocrm.add_command(label="Administração de Campanhas", command=lambda: abrir_crm_sistema(root, 1))
    alvocrm.add_command(label="Atualiza Valores de Campanhas")
    alvocrm.add_command(label="E-Mail Marketing de Campanhas")
    alvocrm.add_command(label="TeleMarketing de Campanhas")
    alvocrm.add_command(label="Soluções de Ocorrências", command=lambda: abrir_crm_sistema(root, 0))
    alvocrm.add_command(label="Mesclagem de Entidades", command=lambda: abrir_matchcode_sistema(root, 1))
    alvocrmrcc = tk.Menu(alvocrm, tearoff=0)
    alvocrmrcc.add_command(label="Importar Inscrições de Eventos/Congressos", command=lambda: abrir_importa_eventos(root))
    alvocrmrcc.add_command(label="Importa Monitoramento Lembrete de Doações")
    alvocrmrcc.add_command(label="Integração Congressos ONLINE x Alvo x RdStation")
    alvocrmrcc.add_command(label="Vincula Entidade a Diocese", command=lambda: abrir_relaciona_diocese_entidade(root))
    alvocrm.add_cascade(label="RCC", menu=alvocrmrcc)
    alvo_menu.add_cascade(label="CRM", menu=alvocrm)
    # 
    alvoentidade = tk.Menu(alvo_menu, tearoff=0)
    alvoentidade.add_command(label="Relaciona Usuário com Categoria", command=lambda: abrir_categorias(root))
    alvoentidade.add_command(label="Relaciona Usuários, Categorias e Entidades", command=lambda: abrir_categorias(root))
    alvoentidade.add_command(label="Relaciona Entidade com Diocese", command=lambda: abrir_relaciona_diocese_entidade(root))
    alvo_menu.add_cascade(label="Entidades", menu=alvoentidade)
    # 
    alvofinanceiro = tk.Menu(alvo_menu, tearoff=0)
    alvofinanceiro.add_command(label="Gera Títulos a Receber no Alvo")
    alvofinanceiro.add_command(label="Gera Remessa para Bancos")
    alvofinanceiro.add_command(label="Débito x Crédito de Conta Financeira")
    alvofinanceiro.add_command(label="Atualiza Situação de Títulos")
    alvofinanceiro.add_command(label="Conciliação Vindi Crédito Recorrente(RCC)", command=lambda: abrir_concilia_vindi(root))
    alvo_menu.add_cascade(label="Financeiro", menu=alvofinanceiro)
    # 
    alvolocalidade = tk.Menu(alvo_menu, tearoff=0)
    alvolocalidade.add_command(label="Correção de Distritos cadastrados como Cidades", command=lambda: abrir_corrigecidadedistrito(root))
    alvo_menu.add_cascade(label="Localidades", menu=alvolocalidade)
    # 
    alvoestoque = tk.Menu(alvo_menu, tearoff=0)
    alvoestoque.add_command(label="Cores", command=lambda: abrir_cores(root))
    alvoestoque.add_command(label="Marcas")
    alvoestoque.add_command(label="Produtos")
    alvo_menu.add_cascade(label="Estoque", menu=alvoestoque)
    # 
    alvogeral = tk.Menu(alvo_menu, tearoff=0)
    alvogeral.add_command(label="Departamentos", command=lambda: abrir_departamentos_sistema(root))
    alvogeral.add_command(label="Empresas", command=lambda: abrir_empresas_sistema(root, 1))
    alvo_menu.add_cascade(label="Geral", menu=alvogeral)
    # 
    alvousersalvo = tk.Menu(alvo_menu, tearoff=0)
    alvousersalvo.add_command(label="Desativa Usuários do Alvo", command=lambda: abrir_desligamento_usuarios(root))
    alvousersalvo.add_command(label="Clonar Permissão de Usuários", command=lambda: abrir_clonar_permissoes(root))
    alvousersalvo.add_command(label="Permissão em Contas Financeiras", command=lambda: abrir_contas_financeiras_usuario(root))
    alvo_menu.add_cascade(label="Usuários do Alvo", menu=alvousersalvo)
    # 
    menu_bar.add_cascade(label="Alvo", menu=alvo_menu)
    # 
    # Menu Utilitários
    utilitarios_menu = tk.Menu(menu_bar, tearoff=0)
    utilmenuimediatas = tk.Menu(menu_bar, tearoff=0)        
    utilmenuimediatas.add_command(label="Cadastrar Consultas", command=lambda: abrir_consultas_sistema(root, 1))
    utilmenuimediatas.add_command(label="Executar Consultas", command=lambda: abrir_consultas_sistema(root, 0))
    # 
    utilitarios_menu.add_cascade(label="Consultas Imediatas", menu=utilmenuimediatas)    
    utilitarios_menu.add_command(label="Validação de Licenças", command=lambda: abrir_validacao_licenca_sistema(root))
    utilitarios_menu.add_command(label="Enviar E-Mail via GeoAlvo F8")
    # 
    # Menu Relatórios
    relatorios_menu = tk.Menu(menu_bar, tearoff=0)
    relatorios_menu.add_command(label="Central de Relatórios", command=lambda: abrir_relatorios(root))
    relatorios_menu.add_command(label="Listagem Geral de Entidades", command=lambda: abrir_relatorios(root))
    relatorios_menu.add_command(label="Entidades Sincronizadas", command=lambda: abrir_relatorios(root))
    relatorios_menu.add_command(label="Entidades Pendentes de Sincronização", command=lambda: abrir_relatorios(root))
    relatorios_menu.add_command(label="Auditoria e Ocorrências", command=lambda: abrir_relatorios(root))
    menu_bar.add_cascade(label="Relatórios", menu=relatorios_menu)

    # Menu Ajuda
    ajuda_menu = tk.Menu(menu_bar, tearoff=0)
    ajuda_menu.add_command(label="Sobre o GeoAlvo", command=lambda: abrir_sobre_sistema_menu(root))
    menu_bar.add_cascade(label="Ajuda", menu=ajuda_menu)

    # Comando Sair no menu principal
    menu_bar.add_command(label="Sair", command=sair_aplicacao)

    
    # Configura o menu na janela
    root.config(menu=menu_bar)
    root.bind("<F2>", lambda event=None: abrir_empresas_sistema(root, 0))

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
    caminho_imagem = obter_caminho_recurso(os.path.join("Imagens", "fundo_gradiente.jpeg"))
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