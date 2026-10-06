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
from core import (
    obter_caminho_recurso,
    centralizar_janela,
    aplicar_icone_janela,
    GestorPermissoes,
    aplicar_permissoes_toolbar,
)


root = None

# Mapeamento extensível de empresas com dashboards cadastrados
EMPRESAS_DASHBOARD = {
    "1.01": {
        "titulo": "📊 Painel & Dashboard de Doações",
        "descricao": (
            "Para garantir inicialização rápida e livre de travamentos,\n"
            "as rotinas do dashboard estão disponíveis sob demanda nos botões abaixo:"
        ),
        "btn_abrir_texto": "📊 Abrir Dashboard de Doações",
        "btn_sync_texto": "⚙️ Sincronizar com o Banco de Dados",
    }
}


def montar_painel_inicial_corporativo(janela_root):
    """Monta a tela inicial corporativa padrão, liberando o login sem travamentos."""
    if not hasattr(janela_root, "main_frame") or not janela_root.main_frame.winfo_exists():
        return

    # Limpar widgets atuais do main_frame
    for child in list(janela_root.main_frame.winfo_children()):
        try:
            child.destroy()
        except Exception:
            pass

    cod_emp = str(getattr(janela_root, "empresa_ativa", "") or "").strip()
    nome_emp = str(getattr(janela_root, "nome_empresa_ativa", "") or "").strip()

    container = tk.Frame(janela_root.main_frame, bg="#FFFFFF")
    container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

    # Header de boas vindas
    header_box = tk.Frame(container, bg="#FFFFFF")
    header_box.pack(pady=(10, 15))

    lbl_logo = tk.Label(
        header_box,
        text="🏛️ GeoAlvo V5.0",
        font=("Segoe UI", 24, "bold"),
        bg="#FFFFFF",
        fg="#1E3A8A"
    )
    lbl_logo.pack()

    txt_emp = f"Empresa Ativa: {cod_emp} - {nome_emp}" if (cod_emp and nome_emp) else (f"Empresa Ativa: {cod_emp}" if cod_emp else "Contexto Corporativo Ativo")
    lbl_emp = tk.Label(
        header_box,
        text=txt_emp,
        font=("Segoe UI", 12, "bold"),
        bg="#FFFFFF",
        fg="#0F766E"
    )
    lbl_emp.pack(pady=(4, 0))
    janela_root.welcome_label = lbl_emp

    lbl_sub = tk.Label(
        header_box,
        text="Sistema de Gestão Integrada & Inteligência de Arrecadação",
        font=("Segoe UI", 10),
        bg="#FFFFFF",
        fg="#64748B"
    )
    lbl_sub.pack(pady=(2, 0))

    # Verifica se há dashboard criado para a empresa ativa (ex: 1.01 Escritório Nacional)
    # Se houver, disponibiliza o painel; caso contrário, oculta a informação.
    config_dash = EMPRESAS_DASHBOARD.get(cod_emp)
    if config_dash:
        card = tk.Frame(container, bg="#F8FAFC", bd=1, relief=tk.SOLID, padx=30, pady=20)
        card.pack(pady=20, ipadx=10, ipady=5)

        lbl_card_tit = tk.Label(
            card,
            text=config_dash.get("titulo", "📊 Painel & Dashboard"),
            font=("Segoe UI", 13, "bold"),
            bg="#F8FAFC",
            fg="#1E293B"
        )
        lbl_card_tit.pack(pady=(0, 6))

        lbl_card_desc = tk.Label(
            card,
            text=config_dash.get("descricao", ""),
            font=("Segoe UI", 9),
            bg="#F8FAFC",
            fg="#475569",
            justify=tk.CENTER
        )
        lbl_card_desc.pack(pady=(0, 15))

        btn_box = tk.Frame(card, bg="#F8FAFC")
        btn_box.pack()

        btn_dash = tk.Button(
            btn_box,
            text=config_dash.get("btn_abrir_texto", "📊 Abrir Dashboard"),
            font=("Segoe UI", 10, "bold"),
            bg="#2563EB",
            fg="#FFFFFF",
            activebackground="#1D4ED8",
            activeforeground="#FFFFFF",
            cursor="hand2",
            padx=16,
            pady=8,
            relief=tk.FLAT,
            command=lambda: abrir_dashboard_doacoes_menu(janela_root, auto_carregar=True)
        )
        btn_dash.pack(side=tk.LEFT, padx=8)
        janela_root.btn_abrir_dashboard = btn_dash

        btn_sync = tk.Button(
            btn_box,
            text=config_dash.get("btn_sync_texto", "⚙️ Sincronizar com o Banco de Dados"),
            font=("Segoe UI", 10, "bold"),
            bg="#0D9488",
            fg="#FFFFFF",
            activebackground="#0F766E",
            activeforeground="#FFFFFF",
            cursor="hand2",
            padx=16,
            pady=8,
            relief=tk.FLAT,
            command=lambda: sincronizar_dashboard_banco_acao(janela_root)
        )
        btn_sync.pack(side=tk.LEFT, padx=8)
        janela_root.btn_sincronizar_banco = btn_sync
    else:
        janela_root.btn_abrir_dashboard = None
        janela_root.btn_sincronizar_banco = None

    lbl_info_rapida = tk.Label(
        container,
        text="Dica: Use as opções do menu superior ou atalhos F2 (Trocar Empresa) e F4 (Consultas Imediatas).",
        font=("Segoe UI", 9, "italic"),
        bg="#FFFFFF",
        fg="#94A3B8"
    )
    lbl_info_rapida.pack(side=tk.BOTTOM, pady=10)


def fechar_dashboard_se_aberto(parent=None):
    """
    Quando o usuário clica em alguma opção do sistema, fecha o dashboard ativo
    no menu principal e libera toda a memória e timers para deixar a máquina livre.
    """
    global root
    janela = parent or root
    if hasattr(janela, "winfo_toplevel"):
        try:
            janela = janela.winfo_toplevel()
        except Exception:
            pass

    dash = getattr(janela, "dashboard_ativo", None)
    if dash:
        try:
            if hasattr(dash, "destruir_ou_liberar"):
                dash.destruir_ou_liberar()
            else:
                dash.destroy()
        except Exception:
            pass
        janela.dashboard_ativo = None

    montar_painel_inicial_corporativo(janela)

    import gc
    gc.collect()

def abrir_config_banco(root):
    """Abre o formulário de configuração do banco de dados"""
    try:
        fechar_dashboard_se_aberto(root)
        abrir_config_banco_aba(root, "MSSQL")
    except Exception as e:
        print(f"Erro ao abrir configuração do banco: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir configuração do banco:\n{e}")

def abrir_entidades(parent):
    """Abre a janela de gestão de entidades"""
    try:
        fechar_dashboard_se_aberto(parent)
        from entidades import EntidadesView
        EntidadesView(parent)
    except Exception as e:
        print(f"Erro ao abrir módulo de entidades: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir módulo de entidades:\n{e}")

def abrir_relatorios(parent):
    """Abre a Central de Relatórios"""
    try:
        fechar_dashboard_se_aberto(parent)
        from relatorios import RelatoriosView
        RelatoriosView(parent)
    except Exception as e:
        print(f"Erro ao abrir relatórios: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir relatórios:\n{e}")

def abrir_estacoes(parent):
    """Abre o módulo de Gestão de Estações de Trabalho e Inventário de TI"""
    try:
        fechar_dashboard_se_aberto(parent)
        from estacoes import EstacoesView
        EstacoesView(parent)
    except Exception as e:
        print(f"Erro ao abrir estações: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir módulo de estações:\n{e}")

def abrir_configuracoes_sistema(parent, tab_index=0):
    """Abre a tela de Parâmetros e Configurações Gerais do Sistema"""
    try:
        fechar_dashboard_se_aberto(parent)
        from configuracoes import ConfiguracoesView
        ConfiguracoesView(parent, tab_index=tab_index)
    except Exception as e:
        print(f"Erro ao abrir configurações do sistema: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir configurações do sistema:\n{e}")

def abrir_config_banco_aba(parent, initial_tab="MSSQL"):
    """Abre o formulário de configuração do banco de dados na aba selecionada (GeoAlvo ou SAVIC)."""
    try:
        fechar_dashboard_se_aberto(parent)
        from config_banco import DatabaseConfigForm
        from core import centralizar_janela
        form = DatabaseConfigForm(parent=parent, initial_tab=initial_tab)
        centralizar_janela(form.root, parent, 640, 580)
        form.run()
    except Exception as e:
        print(f"Erro ao abrir configuração do banco: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir configuração do banco:\n{e}")


def abrir_configuracao_api_alvo_menu(parent):
    """Abre o formulário de Configuração do Token e Parâmetros da API Alvo (Riosoft)"""
    try:
        fechar_dashboard_se_aberto(parent)
        from configuracoes import abrir_configuracao_api_alvo
        abrir_configuracao_api_alvo(parent)
    except Exception as e:
        print(f"Erro ao abrir configurações da API Alvo: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir configurações da API Alvo:\n{e}")

def abrir_importa_go_savic_menu(parent):
    """Abre o formulário de integração SAVIC x Apolo de Grupos de Oração"""
    try:
        fechar_dashboard_se_aberto(parent)
        from savic import abrir_importa_go_savic
        abrir_importa_go_savic(parent=parent)
    except Exception as e:
        print(f"Erro ao abrir integração SAVIC x Apolo: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir integração SAVIC x Apolo:\n{e}")

def abrir_moderacao_go_savic_menu(parent):
    """Abre o formulário de Moderação de Grupos de Oração SAVIC x Apolo"""
    try:
        fechar_dashboard_se_aberto(parent)
        from savic import abrir_moderacao_go_savic
        abrir_moderacao_go_savic(parent=parent)
    except Exception as e:
        print(f"Erro ao abrir moderação SAVIC x Apolo: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir moderação SAVIC x Apolo:\n{e}")


def abrir_cargos(parent):
    """Abre a tela de Cadastro e Manutenção de Cargos"""
    try:
        fechar_dashboard_se_aberto(parent)
        from cargos import abrir_cargos as abrir_tela_cargos
        abrir_tela_cargos(parent)
    except Exception as e:
        print(f"Erro ao abrir cargos: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir cargos:\n{e}")

def abrir_categorias(parent):
    """Abre a tela de Gestão e Associação de Categorias de Entidades"""
    try:
        fechar_dashboard_se_aberto(parent)
        from categorias import CategoriasEntidadeView
        CategoriasEntidadeView(parent)
    except Exception as e:
        print(f"Erro ao abrir categorias: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir categorias:\n{e}")

def abrir_cores(parent):
    """Abre a tela de Cadastro de Cores de Produtos e Estoque Auxiliar"""
    try:
        fechar_dashboard_se_aberto(parent)
        from cores import abrir_janela_cores
        abrir_janela_cores(parent)
    except Exception as e:
        print(f"Erro ao abrir cadastro de cores: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir cadastro de cores:\n{e}")


def abrir_ativo_imobilizado(parent):
    """Abre a tela de Gestão de Ativo Imobilizado & Depreciação"""
    try:
        fechar_dashboard_se_aberto(parent)
        from ativo_imobilizado import AtivoImobilizadoView
        AtivoImobilizadoView(parent)
    except Exception as e:
        print(f"Erro ao abrir ativo imobilizado: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir ativo imobilizado:\n{e}")

def abrir_categorias_bens(parent):
    """Abre a tela de Categoria de Bens do Ativo Fixo"""
    try:
        fechar_dashboard_se_aberto(parent)
        from ativo_imobilizado.categoria_bens_view import abrir_categorias_bens_sistema
        abrir_categorias_bens_sistema(parent)
    except Exception as e:
        print(f"Erro ao abrir categorias de bens: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir categorias de bens:\n{e}")

def abrir_localizacoes_fisicas(parent):
    """Abre a tela de Localização Física do Ativo Fixo"""
    try:
        fechar_dashboard_se_aberto(parent)
        from ativo_imobilizado.localizacao_fisica_view import abrir_localizacoes_fisicas_sistema
        abrir_localizacoes_fisicas_sistema(parent)
    except Exception as e:
        print(f"Erro ao abrir localizações físicas: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir localizações físicas:\n{e}")

def abrir_classificacao_bens(parent):
    """Abre a tela de Classificação de Bens do Ativo Fixo"""
    try:
        fechar_dashboard_se_aberto(parent)
        from ativo_imobilizado.classificacao_bens_view import abrir_classificacao_bens_sistema
        abrir_classificacao_bens_sistema(parent)
    except Exception as e:
        print(f"Erro ao abrir classificação de bens: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir classificação de bens:\n{e}")


def abrir_almoxarifados_menu(parent):
    """Abre a tela de Cadastro e Manutenção de Almoxarifados"""
    try:
        fechar_dashboard_se_aberto(parent)
        from estoque.almoxarifados_view import abrir_almoxarifados_sistema
        abrir_almoxarifados_sistema(parent)
    except Exception as e:
        print(f"Erro ao abrir almoxarifados: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir almoxarifados:\n{e}")

def abrir_relatorios_almoxarifados_menu(parent):
    """Abre a tela de Relatórios Gerenciais de Almoxarifados e Recentes Aquisições"""
    try:
        fechar_dashboard_se_aberto(parent)
        from estoque.relatorios_almoxarifado_view import abrir_relatorios_almoxarifados_sistema
        abrir_relatorios_almoxarifados_sistema(parent)
    except Exception as e:
        print(f"Erro ao abrir relatórios de almoxarifados: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir relatórios de almoxarifados:\n{e}")

def abrir_clonar_permissoes(parent):
    """Abre a tela de Clonagem e Replicação de Permissões de Usuários"""
    try:
        fechar_dashboard_se_aberto(parent)
        from permissoes import ClonarPermissoesView
        ClonarPermissoesView(parent)
    except Exception as e:
        print(f"Erro ao abrir clonagem de permissões: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir clonagem de permissões:\n{e}")

def abrir_contas_financeiras_usuario(parent):
    """Abre a tela de Permissão de Usuários em Contas Financeiras"""
    try:
        fechar_dashboard_se_aberto(parent)
        from permissoes import UsuarioContasFinView
        UsuarioContasFinView(parent)
    except Exception as e:
        print(f"Erro ao abrir permissões de contas financeiras: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir permissões de contas financeiras:\n{e}")

def abrir_desligamento_usuarios(parent):
    """Abre a tela de Desativação e Desligamento de Usuários"""
    try:
        fechar_dashboard_se_aberto(parent)
        from permissoes import DesligamentoUsuarioView
        DesligamentoUsuarioView(parent)
    except Exception as e:
        print(f"Erro ao abrir desligamento de usuários: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir desligamento de usuários:\n{e}")

def abrir_exclusao_contabil(parent):
    """Abre a tela de Exclusão e Auditoria de Lançamentos Contábeis"""
    try:
        fechar_dashboard_se_aberto(parent)
        from contabilidade import ExclusaoContabilView
        ExclusaoContabilView(parent)
    except Exception as e:
        print(f"Erro ao abrir exclusão contábil: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir exclusão contábil:\n{e}")

def abrir_debxcred(parent):
    """Abre a tela de Conciliação Débito x Crédito"""
    try:
        fechar_dashboard_se_aberto(parent)
        from contabilidade import DebxCredView
        DebxCredView(parent)
    except Exception as e:
        print(f"Erro ao abrir conciliação débito x crédito: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir conciliação débito x crédito:\n{e}")

def abrir_importa_eventos(parent):
    """Abre a tela de Importação de Inscrições de Eventos e Congressos"""
    try:
        fechar_dashboard_se_aberto(parent)
        from eventos import ImportarInscritosEventosView
        ImportarInscritosEventosView(parent)
    except Exception as e:
        print(f"Erro ao abrir importação de eventos: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir importação de eventos:\n{e}")

def abrir_auditoria_cupons(parent):
    """Abre a tela de Auditoria e Conciliação de Cupons Fiscais (NFC-e)"""
    try:
        fechar_dashboard_se_aberto(parent)
        from fiscal import AuditoriaCuponsView
        AuditoriaCuponsView(parent)
    except Exception as e:
        print(f"Erro ao abrir auditoria de cupons: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir auditoria de cupons:\n{e}")

def abrir_concilia_vindi(parent):
    """Abre a tela de Conciliação Vindi e Crédito Recorrente RCC"""
    try:
        fechar_dashboard_se_aberto(parent)
        from vindi import ConciliacaoVindiView
        ConciliacaoVindiView(parent)
    except Exception as e:
        print(f"Erro ao abrir conciliação vindi: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir conciliação vindi:\n{e}")

def abrir_dashboard_doacoes_menu(parent, auto_carregar: bool = True, sincronizar_procedure: bool = False):
    """Abre o Dashboard Executivo de Doações & Inteligência Analítica (Empresa 1.01) sob demanda."""
    try:
        global root
        janela = parent or root
        if hasattr(janela, "winfo_toplevel"):
            try:
                janela = janela.winfo_toplevel()
            except Exception:
                pass
        # Se for a janela principal com main_frame, remonta o dashboard nela
        if hasattr(janela, "main_frame") and janela.main_frame.winfo_exists():
            for child in list(janela.main_frame.winfo_children()):
                try:
                    child.destroy()
                except Exception:
                    pass
            from dashboard import DashboardDoacoesFrame
            dash = DashboardDoacoesFrame(janela.main_frame, empresa="1.01", auto_carregar=auto_carregar)
            dash.pack(fill=tk.BOTH, expand=True)
            janela.dashboard_ativo = dash
            if sincronizar_procedure:
                janela.after(100, dash._sincronizar_procedure)
            return
        from dashboard import abrir_dashboard_doacoes
        abrir_dashboard_doacoes(parent)
    except Exception as e:
        print(f"Erro ao abrir Dashboard de Doações: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir Dashboard de Doações:\n{e}")

def sincronizar_dashboard_banco_acao(parent=None):
    """Abre o dashboard e dispara a rotina de sincronização / carga dos dados com o banco sob demanda."""
    abrir_dashboard_doacoes_menu(parent, auto_carregar=True, sincronizar_procedure=True)

def abrir_documentos_pagar_menu(parent):
    """Abre a tela de Contas a Pagar - Documentos Financeiros."""
    try:
        fechar_dashboard_se_aberto(parent)
        from contas_a_pagar import abrir_documentos_pagar
        abrir_documentos_pagar(parent)
    except Exception as e:
        print(f"Erro ao abrir Contas a Pagar - Documentos: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir Contas a Pagar - Documentos:\n{e}")

def abrir_corrigecidadedistrito(parent):
    """Abre a tela de Correção de Distritos Cadastrados como Cidades"""
    try:
        fechar_dashboard_se_aberto(parent)
        from localidades import CorrecaoCidadesDistritosView
        CorrecaoCidadesDistritosView(parent)
    except Exception as e:
        print(f"Erro ao abrir correção de cidades/distritos: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir correção de cidades/distritos:\n{e}")

def abrir_relaciona_diocese_entidade(parent):
    """Abre a tela de Relacionamento de Entidades RCC com Dioceses da CNBB"""
    try:
        fechar_dashboard_se_aberto(parent)
        from dioceses import RelacionaDioceseEntidadeView
        RelacionaDioceseEntidadeView(parent)
    except Exception as e:
        print(f"Erro ao abrir relacionamento de diocese e entidade: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir relacionamento de diocese e entidade:\n{e}")

_janela_usuarios_ativa = None


def abrir_usuarios_sistema(parent, tab_index=0):
    """Abre a tela unificada de Gestão de Usuários, Grupos e Perfis de Acesso com controle modal e instância única"""
    global _janela_usuarios_ativa
    try:
        fechar_dashboard_se_aberto(parent)
        if _janela_usuarios_ativa is not None and _janela_usuarios_ativa.winfo_exists():
            _janela_usuarios_ativa.deiconify()
            _janela_usuarios_ativa.lift()
            _janela_usuarios_ativa.focus_force()
            if hasattr(_janela_usuarios_ativa, "_view") and hasattr(_janela_usuarios_ativa._view, "notebook") and tab_index > 0:
                _janela_usuarios_ativa._view.notebook.select(tab_index)
            return

        from usuarios import UsuariosView
        top = tk.Toplevel(parent)
        _janela_usuarios_ativa = top
        top.title("Gestão de Usuários, Grupos e Perfis de Acesso - GeoAlvo")
        top.minsize(850, 520)
        centralizar_janela(top, parent, 1050, 660)

        # Configura comportamento modal e vínculo com a janela principal
        top.transient(parent)
        try:
            top.grab_set()
        except Exception:
            pass

        def _ao_fechar():
            global _janela_usuarios_ativa
            try:
                top.grab_release()
            except Exception:
                pass
            _janela_usuarios_ativa = None
            top.destroy()

        top.protocol("WM_DELETE_WINDOW", _ao_fechar)

        view = UsuariosView(top)
        top._view = view
        view.pack(fill=tk.BOTH, expand=True)
        if tab_index > 0:
            view.notebook.select(tab_index)
    except Exception as e:
        print(f"Erro ao abrir gestão de usuários: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir gestão de usuários:\n{e}", parent=parent)

def abrir_consultas_sistema(parent, tab_index=0):
    """Abre o Cadastro e Manutenção de Consultas (unt_cadconsulta)"""
    try:
        fechar_dashboard_se_aberto(parent)
        from consultas import ConsultasView
        top = tk.Toplevel(parent)
        top.title("Cadastro e Manutenção de Consultas - GeoAlvo")
        top.minsize(850, 500)
        centralizar_janela(top, parent, 1050, 640)
        view = ConsultasView(top)
        view.pack(fill=tk.BOTH, expand=True)
        if tab_index > 0:
            view.notebook.select(tab_index)
    except Exception as e:
        print(f"Erro ao abrir cadastro de consultas: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir cadastro de consultas:\n{e}")

def abrir_consultas_imediatas_menu(parent):
    """Abre a tela de Execução de Consultas Imediatas (unt_imediatas / Funil <F4>)"""
    gestor = getattr(parent, "gestor_permissoes", None)
    if gestor and not gestor.pode_acessar("btn_consultas_imediatas"):
        messagebox.showwarning("Acesso Bloqueado", "Seu usuário não possui permissão para acessar Consultas Imediatas.", parent=parent)
        return
    try:
        fechar_dashboard_se_aberto(parent)
        from consultas import abrir_consultas_imediatas
        abrir_consultas_imediatas(parent)
    except Exception as e:
        print(f"Erro ao abrir consultas imediatas: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir consultas imediatas:\n{e}")

def abrir_matchcode_sistema(parent, tab_index=0):
    """Abre a Unificação de Cadastros e Duplicidades (MatchCode)"""
    try:
        fechar_dashboard_se_aberto(parent)
        from matchcode import MatchCodeView
        top = tk.Toplevel(parent)
        top.title("Unificação de Cadastros Duplicados (MatchCode) - GeoAlvo")
        top.minsize(700, 420)
        centralizar_janela(top, parent, 850, 520)
        view = MatchCodeView(top)
        view.pack(fill=tk.BOTH, expand=True)
        if tab_index > 0:
            view.notebook.select(tab_index)
    except Exception as e:
        print(f"Erro ao abrir MatchCode: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir MatchCode:\n{e}")

def definir_empresa_ativa(janela_root, cod: str, nome: str):
    """Atualiza a empresa ativa na janela principal, sessão de usuário e banco de dados."""
    cod_str = str(cod or "").strip()
    nome_str = str(nome or "").strip()
    if not cod_str:
        return

    janela_root.empresa_ativa = cod_str
    janela_root.nome_empresa_ativa = nome_str

    titulo = f"GeoAlvo V5.0 - {cod_str} - {nome_str}" if (cod_str and nome_str) else (f"GeoAlvo V5.0 - Empresa {cod_str}" if cod_str else "GeoAlvo - Sistema de Gestão Integrada v5.0")
    try:
        janela_root.title(titulo)
    except Exception:
        pass

    # Atualiza painel na status bar e mensagem principal
    try:
        if hasattr(janela_root, "painel_empresa") and janela_root.painel_empresa.winfo_exists():
            janela_root.painel_empresa.config(text=f"Empresa: {cod_str} - {nome_str}")
    except Exception:
        pass

    try:
        if hasattr(janela_root, "welcome_label") and janela_root.welcome_label.winfo_exists():
            janela_root.welcome_label.config(text=f"Sistema GeoAlvo V5.0\nEmpresa: {cod_str} - {nome_str}\nBem-vindo ao Sistema!")
    except Exception:
        pass

    # Atualiza a sessão global de logon do usuário
    try:
        from logon import sessao_usuario_atual
        sessao_usuario_atual["codigo_empresa"] = cod_str
        sessao_usuario_atual["nome_empresa"] = nome_str
    except Exception:
        pass

    # Atualiza no banco de dados através do EmpresasService
    try:
        from entidades.database import obter_conexao_banco
        from empresas.repository import EmpresasRepository
        from empresas.service import EmpresasService
        conn = obter_conexao_banco()
        service = EmpresasService(EmpresasRepository(conn))
        service.selecionar_empresa_ativa(cod_str)
        conn.close()
    except Exception:
        pass

    # Atualiza a área principal (Dashboard de Doações para empresa 1.01 ou tela padrão)
    atualizar_painel_principal(janela_root)


def atualizar_painel_principal(janela_root):
    """Monta a tela inicial corporativa padrão sem bloquear o login com consultas pesadas."""
    montar_painel_inicial_corporativo(janela_root)


def trocar_empresa_menu(parent):
    """Abre o formulário de seleção de empresa e atualiza a empresa ativa na janela principal."""
    gestor = getattr(parent, "gestor_permissoes", None)
    if gestor and not gestor.pode_acessar("spbtrocaempresa"):
        messagebox.showwarning("Acesso Bloqueado", "Seu usuário não possui permissão para trocar de empresa.", parent=parent)
        return
    try:
        fechar_dashboard_se_aberto(parent)
        from seleciona_empresa import TelaSelecaoEmpresa

        def _on_confirmar(cod, nome):
            definir_empresa_ativa(parent, cod, nome)
            messagebox.showinfo(
                "Troca de Empresa",
                f"Empresa ativa alterada com sucesso:\n{cod} - {nome}"
            )

        form_empresa = TelaSelecaoEmpresa(parent, on_confirmar=_on_confirmar)
        form_empresa.executar()
    except Exception as e:
        print(f"Erro ao trocar empresa: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir seleção de empresa:\n{e}")


def abrir_empresas_sistema(parent, tab_index=0):
    """Abre a tela de Multi-Empresas e Seleção de Contexto Corporativo (<F2>)"""
    try:
        fechar_dashboard_se_aberto(parent)
        from empresas import EmpresasView
        top = tk.Toplevel(parent)
        top.title("Multi-Empresas & Contexto Corporativo - GeoAlvo")
        top.minsize(720, 440)
        centralizar_janela(top, parent, 880, 560)
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
        fechar_dashboard_se_aberto(parent)
        from crm import CRMView
        top = tk.Toplevel(parent)
        top.title("Gestão de CRM, Campanhas & Ocorrências - GeoAlvo")
        top.minsize(850, 520)
        centralizar_janela(top, parent, 1020, 680)
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
        fechar_dashboard_se_aberto(parent)
        from licenciamento import abrir_manutencao_versoes
        abrir_manutencao_versoes(parent)
    except Exception as e:
        print(f"Erro ao abrir manutenção de versões: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir manutenção de versões:\n{e}")

def abrir_validacao_licenca_sistema(parent):
    """Abre a tela de Validação e Ativação de Licenças do Sistema"""
    try:
        fechar_dashboard_se_aberto(parent)
        from licenciamento import abrir_validacao_licenca
        from logon import sessao_usuario_atual
        login_atual = str(sessao_usuario_atual.get("login", "") or getattr(parent, "usuario_logado", "")).strip()
        abrir_validacao_licenca(parent, usuario=login_atual)
    except Exception as e:
        print(f"Erro ao abrir validação de licenças: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir validação de licenças:\n{e}")

def abrir_manutencao_codigos_sistema_menu(parent):
    """Abre a tela de Manutenção de Códigos e Sequenciais do Sistema"""
    try:
        fechar_dashboard_se_aberto(parent)
        from configcod import abrir_manutencao_codigos_sistema
        abrir_manutencao_codigos_sistema(parent)
    except Exception as e:
        print(f"Erro ao abrir manutenção de códigos: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir manutenção de códigos:\n{e}")

def abrir_nomes_amigaveis_sistema(parent):
    """Abre a tela do Dicionário de Nomes Amigáveis de Telas e Controles"""
    try:
        fechar_dashboard_se_aberto(parent)
        from nomesamigaveis import abrir_janela_nomes_amigaveis
        abrir_janela_nomes_amigaveis(parent)
    except Exception as e:
        print(f"Erro ao abrir dicionário de nomes amigáveis: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir dicionário de nomes amigáveis:\n{e}")

def abrir_departamentos_sistema(parent):
    """Abre a tela de Gestão de Departamentos e Seções"""
    try:
        fechar_dashboard_se_aberto(parent)
        from departamentos import abrir_janela_departamentos
        abrir_janela_departamentos(parent)
    except Exception as e:
        print(f"Erro ao abrir departamentos: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir departamentos:\n{e}")

def abrir_sobre_sistema_menu(parent):
    """Abre a janela com informações técnicas e Sobre o GeoAlvo"""
    try:
        fechar_dashboard_se_aberto(parent)
        from autenticacao import abrir_sobre_sistema
        abrir_sobre_sistema(parent)
    except Exception as e:
        print(f"Erro ao abrir Sobre o Sistema: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir Sobre o Sistema:\n{e}")

def abrir_cores_sistema(parent):
    """Abre a tela de cadastro e manutenção de cores de produtos (unt_cadcores / unt_geoapolo_cores)."""
    try:
        fechar_dashboard_se_aberto(parent)
        from cores.view import abrir_janela_cores
        abrir_janela_cores(parent)
    except Exception as e:
        print(f"Erro ao abrir cadastro de cores: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir cadastro de cores:\n{e}")

def abrir_produtos_sistema(parent):
    """Abre a tela de cadastro e manutenção de produtos (unt_cadprodutos)."""
    try:
        fechar_dashboard_se_aberto(parent)
        from produtos.view import abrir_janela_produtos
        abrir_janela_produtos(parent)
    except Exception as e:
        print(f"Erro ao abrir cadastro de produtos: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir cadastro de produtos:\n{e}")

def abrir_grupos_produtos_sistema(parent):
    """Abre a tela de cadastro e manutenção de grupos de produtos (unt_geoapolo_grupoprodutos)."""
    try:
        fechar_dashboard_se_aberto(parent)
        from produtos.grupos_view import abrir_janela_grupos_produtos
        abrir_janela_grupos_produtos(parent)
    except Exception as e:
        print(f"Erro ao abrir cadastro de grupos de produtos: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir cadastro de grupos de produtos:\n{e}")

def abrir_marcas_sistema(parent):
    """Abre a tela de cadastro e manutenção de marcas (unt_cadmarcas)."""
    try:
        fechar_dashboard_se_aberto(parent)
        from marcas.view import abrir_janela_marcas
        abrir_janela_marcas(parent)
    except Exception as e:
        print(f"Erro ao abrir cadastro de marcas: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir cadastro de marcas:\n{e}")

def abrir_centros_controle_sistema(parent):
    """Abre a tela de cadastro e manutenção de centros de controle/custo (USER_geoapolo_centrocontrole)."""
    try:
        fechar_dashboard_se_aberto(parent)
        from centro_controle import abrir_janela_centros_controle
        abrir_janela_centros_controle(parent)
    except Exception as e:
        print(f"Erro ao abrir cadastro de centros de controle: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir cadastro de centros de controle:\n{e}")

def abrir_lotes_sistema(parent):
    """Abre a tela de cadastro e controle de lotes de produtos (user_geoapolo_produto_lote)."""
    try:
        fechar_dashboard_se_aberto(parent)
        from lotes import abrir_janela_lotes
        abrir_janela_lotes(parent)
    except Exception as e:
        print(f"Erro ao abrir controle de lotes: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir controle de lotes:\n{e}")

def abrir_nova_requisicao_material_menu(parent):
    """Abre o formulário de Emissão de Requisição de Materiais."""
    try:
        fechar_dashboard_se_aberto(parent)
        from estoque import abrir_nova_requisicao_material
        abrir_nova_requisicao_material(parent)
    except Exception as e:
        print(f"Erro ao abrir emissão de requisição de materiais: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir emissão de requisição de materiais:\n{e}")

def abrir_atendimento_requisicoes_menu(parent):
    """Abre a tela de Atendimento de Requisições de Materiais."""
    try:
        fechar_dashboard_se_aberto(parent)
        from estoque import abrir_atendimento_requisicoes
        abrir_atendimento_requisicoes(parent)
    except Exception as e:
        print(f"Erro ao abrir atendimento de requisições: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir atendimento de requisições:\n{e}")

def abrir_cancelamento_requisicoes_menu(parent):
    """Abre a tela de Cancelamento de Requisições de Materiais."""
    try:
        fechar_dashboard_se_aberto(parent)
        from estoque import abrir_cancelamento_requisicoes
        abrir_cancelamento_requisicoes(parent)
    except Exception as e:
        print(f"Erro ao abrir cancelamento de requisições: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir cancelamento de requisições:\n{e}")

def abrir_devolucao_requisicoes_menu(parent):
    """Abre a tela de Devolução de Requisições de Materiais."""
    try:
        fechar_dashboard_se_aberto(parent)
        from estoque import abrir_devolucao_requisicoes
        abrir_devolucao_requisicoes(parent)
    except Exception as e:
        print(f"Erro ao abrir devolução de requisições: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir devolução de requisições:\n{e}")

def abrir_movimentacao_estoque_menu(parent):
    """Abre a tela de Movimentação de Estoque (entradas e saídas)."""
    try:
        fechar_dashboard_se_aberto(parent)
        from estoque import abrir_movimentacao_estoque
        abrir_movimentacao_estoque(parent)
    except Exception as e:
        print(f"Erro ao abrir movimentação de estoque: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir movimentação de estoque:\n{e}")

def abrir_consulta_ficha_estoque_menu(parent):
    """Abre a tela de Consulta de Ficha de Estoque (Kardex)."""
    try:
        fechar_dashboard_se_aberto(parent)
        from estoque import abrir_consulta_ficha_estoque
        abrir_consulta_ficha_estoque(parent)
    except Exception as e:
        print(f"Erro ao abrir consulta ficha de estoque: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir consulta ficha de estoque:\n{e}")

def abrir_consulta_saldo_produto_menu(parent):
    """Abre a tela de Consulta de Saldo de Produtos."""
    try:
        fechar_dashboard_se_aberto(parent)
        from estoque import abrir_consulta_saldo_produto
        abrir_consulta_saldo_produto(parent)
    except Exception as e:
        print(f"Erro ao abrir consulta saldo de produto: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir consulta saldo de produto:\n{e}")

def abrir_consulta_requisicoes_menu(parent):
    """Abre a tela de Consulta de Requisições de Materiais."""
    try:
        fechar_dashboard_se_aberto(parent)
        from estoque import abrir_consulta_requisicoes
        abrir_consulta_requisicoes(parent)
    except Exception as e:
        print(f"Erro ao abrir consulta de requisições: {e}")
        messagebox.showerror("Erro", f"Erro ao abrir consulta de requisições:\n{e}")


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

def criar_barra_menu_principal(root, gestor: GestorPermissoes = None) -> tk.Menu:
    """Cria a barra de menu principal aplicando o controle de permissoes e visibilidade.
    - Se o usuario for ADMIN, exibe todas as opcoes normalmente.
    - Se for usuario com perfil restrito, apenas opcoes liberadas no perfil sao exibidas.
    - Submenus sem itens validos sao automaticamente ocultados."""
    from logon import sessao_usuario_atual

    if gestor is None:
        gestor = getattr(root, "gestor_permissoes", None)
        if gestor is None:
            gestor = GestorPermissoes("ADMIN", is_admin=True)

    integra_alvo = bool(sessao_usuario_atual.get("integra_alvo", True))
    cmd_api_alvo_state = "normal" if integra_alvo else "disabled"

    menu_bar = tk.Menu(root)

    def _add_cmd(menu, label, command=None, obj_name=None, **kwargs):
        identificador = obj_name or label
        if gestor.pode_acessar(identificador):
            menu.add_command(label=label, command=command, **kwargs)
            return True
        return False

    def _add_sep(menu):
        if menu.index("end") is not None:
            menu.add_separator()

    def _add_casc(parent_menu, label, submenu, obj_name=None, **kwargs):
        identificador = obj_name or label
        if hasattr(gestor, "esta_bloqueado_explicitamente") and gestor.esta_bloqueado_explicitamente(identificador):
            return False
        end_idx = submenu.index("end")
        if end_idx is None:
            return False
        tem_visivel = False
        for idx in range(end_idx + 1):
            if submenu.type(idx) != "separator":
                tem_visivel = True
                break
        if not tem_visivel:
            return False
        parent_menu.add_cascade(label=label, menu=submenu, **kwargs)
        return True

    # 1. Menu Configuracoes
    config_menu = tk.Menu(menu_bar, tearoff=0)
    
    # Submenu Banco de Dados
    banco_menu = tk.Menu(config_menu, tearoff=0)
    _add_cmd(banco_menu, "Banco Dados GeoAlvo/Alvo", command=lambda: abrir_config_banco_aba(root, "MSSQL"), obj_name="mnuconfigbdgeoalvo")
    _add_cmd(banco_menu, "Banco Dados Savic", command=lambda: abrir_config_banco_aba(root, "MYSQL"), obj_name="mnuconfigbdsavic")
    _add_cmd(banco_menu, "Banco Dados Aplicativo RCC", command=lambda: abrir_config_banco_aba(root, "APLICATIVO"), obj_name="mnuconfigbdapp")
    _add_casc(config_menu, "Banco de Dados", banco_menu, obj_name="mnuconfigdatabase")

    if integra_alvo:
        _add_cmd(config_menu, "Integração API Alvo (Token & Validade)", command=lambda: abrir_configuracao_api_alvo_menu(root), obj_name="mnucfgtokenalvo", state=cmd_api_alvo_state)
    
    sistema_menu = tk.Menu(config_menu, tearoff=0)
    _add_cmd(sistema_menu, "Parâmetros GeoApolo/Alvo", command=lambda: abrir_configuracoes_sistema(root), obj_name="mnucfgparsisgeoapolo")
    if integra_alvo:
        _add_cmd(sistema_menu, "Integração API Alvo (Token & Validade)", command=lambda: abrir_configuracao_api_alvo_menu(root), obj_name="mnucfgtokenalvo", state=cmd_api_alvo_state)
    _add_cmd(sistema_menu, "Manutenção de Versões do GeoApolo", command=lambda: abrir_manutencao_versoes_sistema(root), obj_name="mnuparversaogeoapolo")
    _add_cmd(sistema_menu, "Manutenção de Códigos do Sistema", command=lambda: abrir_manutencao_codigos_sistema_menu(root), obj_name="mnuparamcodsistema")
    _add_casc(config_menu, "Parâmetros do Sistema", sistema_menu, obj_name="mnuconfigparametros")
    
    permissoes_menu = tk.Menu(config_menu, tearoff=0)
    _add_cmd(permissoes_menu, "Administração de Usuários", command=lambda: abrir_usuarios_sistema(root, 0), obj_name="mnuconfigadmusuario")
    _add_cmd(permissoes_menu, "Permissões de Grupos e Usuários", command=lambda: abrir_usuarios_sistema(root, 1), obj_name="mnupermissoesgrupousuarios")
    _add_cmd(permissoes_menu, "Permissões de Grupos", command=lambda: abrir_usuarios_sistema(root, 2), obj_name="mnupermissoesgrupo")
    _add_cmd(permissoes_menu, "Clonar Permissões de Usuários", command=lambda: abrir_clonar_permissoes(root), obj_name="mnuclonarpermissoes")
    _add_cmd(permissoes_menu, "Permissão em Contas Financeiras", command=lambda: abrir_contas_financeiras_usuario(root), obj_name="mnucontasfinanceiras")
    _add_cmd(permissoes_menu, "Desativação / Desligamento de Usuários", command=lambda: abrir_desligamento_usuarios(root), obj_name="mnudesligamentousuario")
    _add_cmd(permissoes_menu, "Mesclagem / MatchCode de Usuários", command=lambda: abrir_matchcode_sistema(root, 0), obj_name="mnumatchcodeusuario")
    _add_cmd(permissoes_menu, "Dicionário de Nomes Amigáveis", command=lambda: abrir_nomes_amigaveis_sistema(root), obj_name="mnunomesamigaveis")
    _add_casc(config_menu, "Permissões de Acesso", permissoes_menu, obj_name="mnupermissoesacesso")
    
    _add_cmd(config_menu, "Trocar de Empresa <F2>", command=lambda: trocar_empresa_menu(root), obj_name="mnuconfigtrocaempresa")
    _add_casc(menu_bar, "Configurações", config_menu, obj_name="mnuconfig")

    # 2. Menu Cadastros
    cadastros_menu = tk.Menu(menu_bar, tearoff=0)
    cadatfmenu = tk.Menu(cadastros_menu, tearoff=0)    
    _add_cmd(cadatfmenu, "Ativo Imobilizado", command=lambda: abrir_ativo_imobilizado(root), obj_name="mnucadativoimobilizado")
    _add_cmd(cadatfmenu, "Categoria de Bens", command=lambda: abrir_categorias_bens(root), obj_name="mnucadcategbens")
    _add_cmd(cadatfmenu, "Classificação de Ativos", command=lambda: abrir_classificacao_bens(root), obj_name="mnucadclassificacaoativo")
    _add_cmd(cadatfmenu, "Estações de Trabalho", command=lambda: abrir_estacoes(root), obj_name="mnucadestacoes")
    _add_cmd(cadatfmenu, "Localização Física", command=lambda: abrir_localizacoes_fisicas(root), obj_name="mnucadlocalizacaofisica")
    _add_cmd(cadatfmenu, "Status de Hardware/Software", obj_name="mnucadstatushardsoft")
    _add_cmd(cadatfmenu, "Tipos de Licenças de Software", obj_name="mnucadtipolicsoftware")
    _add_casc(cadastros_menu, "Ativo Fixo", cadatfmenu, obj_name="mnucadativofixoti")

    cadcctrlmenu = tk.Menu(cadastros_menu, tearoff=0)
    _add_cmd(cadcctrlmenu, "Centro de Custos/Controle", command=lambda: abrir_centros_controle_sistema(root), obj_name="mnucad_centrocontrole")
    _add_casc(cadastros_menu, "Manutenção Centro de controle", cadcctrlmenu, obj_name="mnucad_mancentrocontrole")

    cadcrm = tk.Menu(cadastros_menu, tearoff=0)
    _add_cmd(cadcrm, "Ocorrências & Chamados", command=lambda: abrir_crm_sistema(root, 0), obj_name="mnucad_crm_ocorrencias")
    _add_cmd(cadcrm, "Cadastros de Eventos", command=lambda: abrir_crm_sistema(root, 0), obj_name="mnucad_crm_eventos")
    _add_cmd(cadcrm, "Importar Inscritos de Eventos", command=lambda: abrir_importa_eventos(root), obj_name="mnucad_crm_importa")
    _add_cmd(cadcrm, "Cadastros de Tipos de Campanhas", command=lambda: abrir_crm_sistema(root, 1), obj_name="mnucad_crm_campanhas")
    _add_cmd(cadcrm, "Cadastros de Tipos de Tratamento", command=lambda: abrir_crm_sistema(root, 2), obj_name="mnucad_crm_tratamentos")
    _add_casc(cadastros_menu, "CRM", cadcrm, obj_name="mnucad_crm")

    cadentidades = tk.Menu(cadastros_menu, tearoff=0)
    _add_cmd(cadentidades, "Cargos", command=lambda: abrir_cargos(root), obj_name="mnucadcargos")
    _add_cmd(cadentidades, "Categorias", command=lambda: abrir_categorias(root), obj_name="mnucadentcategorias")
    _add_cmd(cadentidades, "Entidades", command=lambda: abrir_entidades(root), obj_name="mnuentidades")
    _add_cmd(cadentidades, "Importa Entidades", obj_name="mnuimportaentidades")
    _add_cmd(cadentidades, "Tipos de Tratamento", command=lambda: abrir_crm_sistema(root, 2), obj_name="mnucadtipotratamento")
    _add_casc(cadastros_menu, "Entidades", cadentidades, obj_name="mnucadentidades")

    cadfinanc = tk.Menu(cadastros_menu, tearoff=0)
    _add_cmd(cadfinanc, "Plano de Classes de Receitas/Despesas", obj_name="mnucadfinclasserecdesp")
    _add_cmd(cadfinanc, "Manutenção de Cartões de Crédito", obj_name="mnugacadcartoescredito")
    _add_cmd(cadfinanc, "Situação Financeira de Documentos", obj_name="mnucadfinsitcod")
    _add_cmd(cadfinanc, "tipos de Cobrança", obj_name="mnucadfintipocob")
    _add_casc(cadastros_menu, "Financeiro", cadfinanc, obj_name="mnucadfinanceiro")

    cadestoque = tk.Menu(cadastros_menu, tearoff=0)
    _add_cmd(cadestoque, "Almoxarifados", command=lambda: abrir_almoxarifados_menu(root), obj_name="mnucadalmoxarifados")
    _add_cmd(cadestoque, "Cores", command=lambda: abrir_cores_sistema(root), obj_name="mnucadcores")
    _add_cmd(cadestoque, "Grupos de Produtos", command=lambda: abrir_grupos_produtos_sistema(root), obj_name="mnucadprodutos")
    _add_cmd(cadestoque, "Marcas", command=lambda: abrir_marcas_sistema(root), obj_name="mnucadmarcas")
    _add_cmd(cadestoque, "Produtos", command=lambda: abrir_produtos_sistema(root), obj_name="mnucadprodutos")
    _add_cmd(cadestoque, "Controle de Lotes de Produtos", command=lambda: abrir_lotes_sistema(root), obj_name="mnucadlotes")
    _add_casc(cadastros_menu, "Estoque", cadestoque, obj_name="mnucadestoque")

    cadgeral = tk.Menu(cadastros_menu, tearoff=0)
    _add_cmd(cadgeral, "Departamentos", command=lambda: abrir_departamentos_sistema(root), obj_name="mnucadepartamentos")
    _add_cmd(cadgeral, "Empresas", command=lambda: abrir_empresas_sistema(root, 1), obj_name="mnucadempresas")
    _add_casc(cadastros_menu, "Geral", cadgeral, obj_name="mnucadgeral")

    _add_cmd(cadastros_menu, "Usuários GeoApolo", command=lambda: abrir_usuarios_sistema(root, 0), obj_name="mnucadusuarios")
    _add_casc(menu_bar, "Cadastros", cadastros_menu, obj_name="mnucadastro")

    # 3. Menu GeoAlvo
    geoapolo_menu = tk.Menu(menu_bar, tearoff=0)
    gamenuativofixo = tk.Menu(geoapolo_menu, tearoff=0)
    _add_cmd(gamenuativofixo, "Atualiza Inventário de TI", command=lambda: abrir_estacoes(root), obj_name="gamenuativofixo")
    _add_casc(geoapolo_menu, "Ativo Fixo", gamenuativofixo, obj_name="gamenuativofixo")

    gamenufinancapagar = tk.Menu(geoapolo_menu, tearoff=0)
    gamenu_doc_fin_pagar = tk.Menu(gamenufinancapagar, tearoff=0)
    _add_cmd(gamenu_doc_fin_pagar, "Documentos", command=lambda: abrir_documentos_pagar_menu(root), obj_name="mnudocfinanceiropagar")
    _add_casc(gamenufinancapagar, "Documento Financeiro", gamenu_doc_fin_pagar, obj_name="gamenu_doc_fin_pagar")
    _add_sep(gamenufinancapagar)
    _add_cmd(gamenufinancapagar, "Controle de Cartões de Crédito", obj_name="mnugafinctaspagarcartaocredito")
    _add_casc(geoapolo_menu, "Contas a Pagar", gamenufinancapagar, obj_name="mnugafinctaspagar")

    gamenufinancareceber = tk.Menu(geoapolo_menu, tearoff=0)
    _add_cmd(gamenufinancareceber, "Documentos a Receber", obj_name="mnugafincprecdocfin")
    _add_casc(geoapolo_menu, "Contas a Receber", gamenufinancareceber, obj_name="mnugactasareceber")

    gamenuintegrasavic = tk.Menu(geoapolo_menu, tearoff=0)
    _add_cmd(gamenuintegrasavic, "Importar Grupos de Oração do SAVIC", command=lambda: abrir_importa_go_savic_menu(root), obj_name="mnugaintegrasavicgo")
    _add_cmd(gamenuintegrasavic, "Moderação de Grupos de Oração Savic x Alvo", command=lambda: abrir_moderacao_go_savic_menu(root), obj_name="mnugaintegrasavic_moderago")
    _add_cmd(gamenuintegrasavic, "Valida Entidades Alvo x Savic", obj_name="mnugeosavicvalidaorigem")
    _add_cmd(gamenuintegrasavic, "Importa entidades Savic -> GeoAlvo", obj_name="mnuimportaentidadesavicgeoapolo")
    if integra_alvo:
        _add_casc(geoapolo_menu, "Integrar SAVIC x Alvo", gamenuintegrasavic, obj_name="mnugeosavic")

    gamenuestoque = tk.Menu(geoapolo_menu, tearoff=0)
    gamenureqs = tk.Menu(gamenuestoque, tearoff=0)
    _add_cmd(gamenureqs, "Nova Requisição de Material", command=lambda: abrir_nova_requisicao_material_menu(root), obj_name="mnunovarequisicao")
    _add_cmd(gamenureqs, "Atendimento", command=lambda: abrir_atendimento_requisicoes_menu(root), obj_name="mnuatendimentoreqs")
    _add_cmd(gamenureqs, "Cancelamento", command=lambda: abrir_cancelamento_requisicoes_menu(root), obj_name="mnucancelamentoreqs")
    _add_cmd(gamenureqs, "Devolução", command=lambda: abrir_devolucao_requisicoes_menu(root), obj_name="mnudevolucaoreqs")
    _add_casc(gamenuestoque, "Requisições de Materiais", gamenureqs, obj_name="gamenureqs")

    _add_cmd(gamenuestoque, "Movimentação de Estoque", command=lambda: abrir_movimentacao_estoque_menu(root), obj_name="mnumovimentacaoestoque")

    gamenuconsultas = tk.Menu(gamenuestoque, tearoff=0)
    _add_cmd(gamenuconsultas, "Consulta Ficha Estoque", command=lambda: abrir_consulta_ficha_estoque_menu(root), obj_name="mnuconsfichaestoque")
    _add_cmd(gamenuconsultas, "Consulta Saldo Produto", command=lambda: abrir_consulta_saldo_produto_menu(root), obj_name="mnuconssaldoproduto")
    _add_cmd(gamenuconsultas, "Consulta Requisições de Materiais", command=lambda: abrir_consulta_requisicoes_menu(root), obj_name="mnuconsrequisicoes")
    _add_cmd(gamenuconsultas, "Relatórios por Almoxarifado", command=lambda: abrir_relatorios_almoxarifados_menu(root), obj_name="mnurelalmoxarifados")
    _add_casc(gamenuestoque, "Consultas", gamenuconsultas, obj_name="gamenuconsultas")

    _add_casc(geoapolo_menu, "Estoque", gamenuestoque, obj_name="gamenuestoque")
    _add_casc(menu_bar, "GeoAlvo", geoapolo_menu, obj_name="mnugeoapolo")

    # 4. Menu Alvo
    alvo_menu = tk.Menu(menu_bar, tearoff=0)
    alvoloja = tk.Menu(alvo_menu, tearoff=0)
    _add_cmd(alvoloja, "Auditoria de Cupons Fiscais", command=lambda: abrir_auditoria_cupons(root), obj_name="mnuapoauditoriacupons")
    _add_cmd(alvoloja, "Troca Cupom Fiscal nomeado por Consumidor Final", obj_name="mnuapoalojatrocacncf")
    _add_casc(alvo_menu, "Alvo Loja", alvoloja, obj_name="mnuapoalojatrocacncf")

    alvocontabilidade = tk.Menu(alvo_menu, tearoff=0)
    _add_cmd(alvocontabilidade, "Débito x Crédito", command=lambda: abrir_debxcred(root), obj_name="mnuapolodebcredcontafin")
    _add_cmd(alvocontabilidade, "Débito x Crédito Detalhado", command=lambda: abrir_debxcred(root), obj_name="mnuapolodebcredcontafin")
    _add_cmd(alvocontabilidade, "Exclui Lançamentos Contábeis", command=lambda: abrir_exclusao_contabil(root), obj_name="mnuapoexcluilanccontabil")
    _add_cmd(alvocontabilidade, "Corrige Lançamentos de Cupom Fiscal", obj_name="mnuapocorrigecupomfiscal")
    _add_casc(alvo_menu, "Contabilidade", alvocontabilidade, obj_name="mnuapocontabilidade")

    alvocrm = tk.Menu(alvo_menu, tearoff=0)
    _add_cmd(alvocrm, "Administração de Campanhas", command=lambda: abrir_crm_sistema(root, 1), obj_name="mnucad_crm_campanhas")
    _add_cmd(alvocrm, "Atualiza Valores de Campanhas", obj_name="mnucad_crm_campanhas")
    _add_cmd(alvocrm, "E-Mail Marketing de Campanhas", obj_name="mnucad_crm_campanhas")
    _add_cmd(alvocrm, "TeleMarketing de Campanhas", obj_name="mnucad_crm_campanhas")
    _add_cmd(alvocrm, "Soluções de Ocorrências", command=lambda: abrir_crm_sistema(root, 0), obj_name="mnucad_crm_ocorrencias")
    _add_cmd(alvocrm, "Mesclagem de Entidades", command=lambda: abrir_matchcode_sistema(root, 1), obj_name="mnumatchcodeusuario")
    alvocrmrcc = tk.Menu(alvocrm, tearoff=0)
    _add_cmd(alvocrmrcc, "Importar Inscrições de Eventos/Congressos", command=lambda: abrir_importa_eventos(root), obj_name="mnucad_crm_importa")
    _add_cmd(alvocrmrcc, "Importa Monitoramento Lembrete de Doações", obj_name="mnucad_crm_eventos")
    _add_cmd(alvocrmrcc, "Integração Congressos ONLINE x Alvo x RdStation", obj_name="mnucad_crm_eventos")
    _add_cmd(alvocrmrcc, "Vincula Entidade a Diocese", command=lambda: abrir_relaciona_diocese_entidade(root), obj_name="mnurelacionadiocese")
    _add_casc(alvocrm, "RCC", alvocrmrcc, obj_name="mnuapo_fin_rcc")
    _add_casc(alvo_menu, "CRM", alvocrm, obj_name="mnucad_crm")

    alvoentidade = tk.Menu(alvo_menu, tearoff=0)
    _add_cmd(alvoentidade, "Relaciona Usuário com Categoria", command=lambda: abrir_categorias(root), obj_name="mnucadentcategorias")
    _add_cmd(alvoentidade, "Relaciona Usuários, Categorias e Entidades", command=lambda: abrir_categorias(root), obj_name="mnucadentcategorias")
    _add_cmd(alvoentidade, "Relaciona Entidade com Diocese", command=lambda: abrir_relaciona_diocese_entidade(root), obj_name="mnurelacionadiocese")
    _add_casc(alvo_menu, "Entidades", alvoentidade, obj_name="mnucadentidades")

    alvofinanceiro = tk.Menu(alvo_menu, tearoff=0)
    _add_cmd(alvofinanceiro, "Gera Títulos a Receber no Alvo", obj_name="mnuapologeratitulorecapolo")
    _add_cmd(alvofinanceiro, "Gera Remessa para Bancos", obj_name="mnuapolofingerarecbanco")
    _add_cmd(alvofinanceiro, "Débito x Crédito de Conta Financeira", obj_name="mnuapolodebcredcontafin")
    _add_cmd(alvofinanceiro, "Atualiza Situação de Títulos", obj_name="mnuapolofinacertasituacaotitulo")
    _add_cmd(alvofinanceiro, "Conciliação Vindi Crédito Recorrente(RCC)", command=lambda: abrir_concilia_vindi(root), obj_name="mnuapoloconciliavindi")
    _add_sep(alvofinanceiro)
    _add_cmd(alvofinanceiro, "📊 Dashboard de Doações & IA (1.01)", command=lambda: abrir_dashboard_doacoes_menu(root), obj_name="mnudashboarddoacoes")
    _add_cmd(alvofinanceiro, "⚙️ Sincronizar Dashboard com o Banco", command=lambda: sincronizar_dashboard_banco_acao(root), obj_name="mnusincronizardashboard")
    _add_casc(alvo_menu, "Financeiro", alvofinanceiro, obj_name="mnuapolofinanceiro")

    alvolocalidade = tk.Menu(alvo_menu, tearoff=0)
    _add_cmd(alvolocalidade, "Correção de Distritos cadastrados como Cidades", command=lambda: abrir_corrigecidadedistrito(root), obj_name="mnucorrigecidades")
    _add_casc(alvo_menu, "Localidades", alvolocalidade, obj_name="mnucorrigecidades")

    alvogeral = tk.Menu(alvo_menu, tearoff=0)
    _add_cmd(alvogeral, "Departamentos", command=lambda: abrir_departamentos_sistema(root), obj_name="mnucadepartamentos")
    _add_cmd(alvogeral, "Empresas", command=lambda: abrir_empresas_sistema(root, 1), obj_name="mnucadempresas")
    _add_casc(alvo_menu, "Geral", alvogeral, obj_name="mnucadgeral")

    alvousersalvo = tk.Menu(alvo_menu, tearoff=0)
    _add_cmd(alvousersalvo, "Desativa Usuários do Alvo", command=lambda: abrir_desligamento_usuarios(root), obj_name="mnuapolodesativausuario")
    _add_cmd(alvousersalvo, "Clonar Permissão de Usuários", command=lambda: abrir_clonar_permissoes(root), obj_name="mnuapoloclonarpermissao")
    _add_cmd(alvousersalvo, "Permissão em Contas Financeiras", command=lambda: abrir_contas_financeiras_usuario(root), obj_name="mnuapolopermsctafin")
    _add_casc(alvo_menu, "Usuários do Alvo", alvousersalvo, obj_name="mnuapolousuarios")

    if integra_alvo:
        _add_casc(menu_bar, "Alvo", alvo_menu, obj_name="mnuapolo")
    else:
        if gestor.pode_acessar("mnuapolo") and gestor.is_admin:
            menu_bar.add_cascade(label="Alvo (Não Integrado)", menu=alvo_menu, state="disabled")

    # 5. Menu Utilitários
    utilitarios_menu = tk.Menu(menu_bar, tearoff=0)
    _add_cmd(utilitarios_menu, "Cadastro de Consultas Imediatas", command=lambda: abrir_consultas_sistema(root, 0), obj_name="mnucadconsultas")
    _add_cmd(utilitarios_menu, "Consultas Imediatas <F4>", command=lambda: abrir_consultas_imediatas_menu(root), obj_name="mnuconsultasimediatas")
    _add_sep(utilitarios_menu)
    _add_cmd(utilitarios_menu, "Validação de Licenças", command=lambda: abrir_validacao_licenca_sistema(root), obj_name="mnutlvalidalicenca")
    _add_cmd(utilitarios_menu, "Enviar E-Mail via GeoAlvo F8", obj_name="mnuutlenviaemail")
    _add_casc(menu_bar, "Utilitários", utilitarios_menu, obj_name="mnutilitarios")

    # 6. Menu Relatórios
    relatorios_menu = tk.Menu(menu_bar, tearoff=0)
    _add_cmd(relatorios_menu, "📊 Dashboard de Doações & IA (1.01)", command=lambda: abrir_dashboard_doacoes_menu(root), obj_name="mnudashboarddoacoes")
    _add_cmd(relatorios_menu, "⚙️ Sincronizar Dashboard com o Banco", command=lambda: sincronizar_dashboard_banco_acao(root), obj_name="mnusincronizardashboard")
    _add_sep(relatorios_menu)
    _add_cmd(relatorios_menu, "Central de Relatórios", command=lambda: abrir_relatorios(root), obj_name="mnurelcentral")
    _add_cmd(relatorios_menu, "Listagem Geral de Entidades", command=lambda: abrir_relatorios(root), obj_name="mnurellistagemgeral")
    _add_cmd(relatorios_menu, "Entidades Sincronizadas", command=lambda: abrir_relatorios(root), obj_name="mnurelentidadessinc")
    _add_cmd(relatorios_menu, "Entidades Pendentes de Sincronização", command=lambda: abrir_relatorios(root), obj_name="mnurelentidadespend")
    _add_cmd(relatorios_menu, "Auditoria e Ocorrências", command=lambda: abrir_relatorios(root), obj_name="mnurelauditoria")
    _add_casc(menu_bar, "Relatórios", relatorios_menu, obj_name="mnurelatórios")

    # 7. Menu Ajuda
    ajuda_menu = tk.Menu(menu_bar, tearoff=0)
    _add_cmd(ajuda_menu, "Sobre o GeoAlvo", command=lambda: abrir_sobre_sistema_menu(root), obj_name="ajuda")
    _add_casc(menu_bar, "Ajuda", ajuda_menu, obj_name="ajuda")

    # 8. Sair
    if gestor.pode_acessar("sair") or gestor.pode_acessar("mnusair") or gestor.pode_acessar("btn_sair"):
        menu_bar.add_command(label="Sair", command=sair_aplicacao)

    return menu_bar


def main():
    global root
    from logon import sessao_usuario_atual, TelaLogon

    # Fluxo corporativo oficial:
    # 1. Abre o formulário de Login;
    # 2. Solicita usuário e senha e autentica;
    # 3. Abre a Seleção de Empresas;
    # 4. SÓ AÍ abre o sistema principal e executa o Dashboard (para empresa 1.01).
    if not sessao_usuario_atual.get("codigo_usuario") or not sessao_usuario_atual.get("codigo_empresa"):
        tela = TelaLogon()
        tela.executar()
        return

    root = tk.Tk()
    
    # Contexto corporativo herdado da seleção de empresas
    cod_emp = sessao_usuario_atual.get("codigo_empresa", "1.01")
    nome_emp = sessao_usuario_atual.get("nome_empresa", "")
    root.empresa_ativa = cod_emp
    root.nome_empresa_ativa = nome_emp
    if cod_emp and nome_emp:
        root.title(f"GeoAlvo V5.0 - {cod_emp} - {nome_emp}")
    else:
        root.title("GeoAlvo - Sistema de Gestão Integrada v5.0")
    
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight() - 40
    root.geometry(f"{largura_tela}x{altura_tela}+0+0")
    root.state('zoomed') # maximiza a janela

    # Configura ícone oficial da aplicação se disponível
    aplicar_icone_janela(root)

    # Identifica se a base/empresa ativa possui integração com o Alvo
    integra_alvo = bool(sessao_usuario_atual.get("integra_alvo", True))
    cmd_api_alvo_state = "normal" if integra_alvo else "disabled"

    # Carrega permissões corporativas do usuário autenticado
    usuario_ativo = (
        sessao_usuario_atual.get("usucod")
        or sessao_usuario_atual.get("codigo_usuario")
        or sessao_usuario_atual.get("login")
        or "ADMIN"
    )
    conn_perm = None
    try:
        from entidades.database import obter_conexao_banco
        conn_perm = obter_conexao_banco()
    except Exception as exc_conn:
        print(f"Aviso: Não foi possível obter conexão direta para permissões: {exc_conn}")

    gestor_permissoes = GestorPermissoes.carregar_do_banco(conn_perm, usuario_ativo)
    root.gestor_permissoes = gestor_permissoes

    # =============================================
    # Barra de menu (PRIMEIRO)
    # =============================================
    menu_bar = criar_barra_menu_principal(root, gestor_permissoes)
    root.config(menu=menu_bar)
    root.menu_bar = menu_bar

    root.bind("<F2>", lambda event=None: trocar_empresa_menu(root))
    root.bind("<F4>", lambda event=None: abrir_consultas_imediatas_menu(root))

    # Criar a toolbar e aplicar controle de acesso
    toolbar_manager = ToolbarManager(root)
    toolbar_manager.aplicar_permissoes(gestor_permissoes)
    root.toolbar_manager = toolbar_manager
    

    # =============================================
    # Barra de status (TERCEIRO - no bottom)
    # =============================================
    status_bar = tk.Frame(root, bd=1, relief=tk.SUNKEN)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # Painel da Empresa Ativa (idêntico ao Delphi TStatusBar.Panels[0])
    txt_emp = f"Empresa: {root.empresa_ativa} - {root.nome_empresa_ativa}" if (getattr(root, "empresa_ativa", None) and getattr(root, "nome_empresa_ativa", None)) else f"Empresa: {getattr(root, 'empresa_ativa', '1.01')}"
    painel_empresa = tk.Label(status_bar, text=txt_emp, bd=1, relief=tk.SUNKEN, anchor='w', font=("Segoe UI", 9, "bold"), fg="#1E3A8A")
    painel_empresa.pack(side=tk.LEFT, padx=2, ipadx=10, fill=tk.Y)
    root.painel_empresa = painel_empresa

    from logon import sessao_usuario_atual
    from config_banco import ConfigManager
    nome_banco_conectado = (
        sessao_usuario_atual.get("nome_banco")
        or ConfigManager().load_settings().get("banco")
        or "RCC"
    )

    painel1 = tk.Label(status_bar, text="Banco Alvo", bd=1, relief=tk.SUNKEN, anchor='w')
    painel1.pack(side=tk.LEFT, padx=2, ipadx=10, fill=tk.Y)
    
    texto_alvo_status = nome_banco_conectado if integra_alvo else "Não Integrado"
    cor_alvo_status = "#1E293B" if integra_alvo else "#64748B"
    painel2 = tk.Label(status_bar, text=texto_alvo_status, bd=1, relief=tk.SUNKEN, anchor='w', font=("Segoe UI", 9, "bold"), fg=cor_alvo_status)
    painel2.pack(side=tk.LEFT, padx=2, ipadx=10, fill=tk.Y)
    root.painel_banco_alvo = painel2
    
    painel3 = tk.Label(status_bar, text="Banco GeoAlvo", bd=1, relief=tk.SUNKEN, anchor='w')
    painel3.pack(side=tk.LEFT, padx=2, ipadx=10, fill=tk.Y)
    
    painel4 = tk.Label(status_bar, text=nome_banco_conectado, bd=1, relief=tk.SUNKEN, anchor='w', font=("Segoe UI", 9, "bold"), fg="#1E293B")
    painel4.pack(side=tk.LEFT, padx=2, ipadx=10, fill=tk.Y)
    root.painel_banco_geoalvo = painel4
    
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
    main_window_id = canvas.create_window(largura_tela*0.04, altura_tela*0.04, anchor='nw',
                         window=main_frame, width=largura_tela*0.92, height=altura_tela*0.84)
    root.main_frame = main_frame

    def _on_canvas_configure(event):
        try:
            w = max(int(event.width * 0.94), 400)
            h = max(int(event.height * 0.86), 300)
            pad_x = max(int((event.width - w) / 2), 10)
            pad_y = max(int((event.height - h) / 2), 10)
            canvas.coords(main_window_id, pad_x, pad_y)
            canvas.itemconfig(main_window_id, width=w, height=h)
        except Exception:
            pass
    canvas.bind("<Configure>", _on_canvas_configure)

    # Reconexão transparente em caso de perda de comunicação por inatividade
    _ultimo_check_conexao = [0.0]
    def _verificar_conexao_tecla(event=None):
        agora = time.time()
        # Throttle de 5 segundos para não sobrecarregar socket durante digitação contínua
        if agora - _ultimo_check_conexao[0] < 5.0:
            return
        _ultimo_check_conexao[0] = agora
        try:
            from entidades.database import obter_conexao_banco
            obter_conexao_banco()
        except Exception:
            pass
    root.bind_all("<Key>", _verificar_conexao_tecla, add="+")

    # Inicializa a área principal com o painel apropriado (Dashboard se Empresa 1.01)
    atualizar_painel_principal(root)

    root.mainloop()

if __name__ == "__main__":
    main()