import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from config_banco import DatabaseConfigForm
import os
import sys
from core import obter_caminho_recurso, centralizar_janela


class ToolbarManager:
    """Classe para gerenciar a barra de ferramentas"""
    
    def __init__(self, parent):
        self.parent = parent
        self.buttons = {}
        self.items = []
        self.icons = []
        self.create_toolbar()
    
    def _fechar_dashboard_se_aberto(self):
        """Fecha o dashboard e limpa memória se estiver ativo no frame principal"""
        try:
            from geoalvo import fechar_dashboard_se_aberto
            fechar_dashboard_se_aberto(self.parent)
        except Exception:
            pass

    def abrir_config_bancob(self):
        """Abre o formulário de configuração do banco de dados"""
        try:
            self._fechar_dashboard_se_aberto()
            from geoalvo import abrir_config_banco_aba
            abrir_config_banco_aba(self.parent, "MSSQL")
        except Exception as e:
            print(f"Erro ao abrir configuração do banco: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir configuração do banco:\n{e}")

    def abrir_entidades(self):
        """Abre a janela de gestão de entidades"""
        try:
            self._fechar_dashboard_se_aberto()
            from entidades import EntidadesView
            EntidadesView(self.parent)
        except Exception as e:
            print(f"Erro ao abrir módulo de entidades: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir módulo de entidades:\n{e}")

    def abrir_consultas_imediatas(self):
        """Abre a janela de Consultas Imediatas (unt_imediatas do Delphi) com ícone de funil"""
        try:
            self._fechar_dashboard_se_aberto()
            from consultas import abrir_consultas_imediatas
            abrir_consultas_imediatas(self.parent)
        except Exception as e:
            print(f"Erro ao abrir Consultas Imediatas: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir Consultas Imediatas:\n{e}")

    def abrir_concilia_vindi(self):
        """Abre o formulário de Conciliação Vindi e Crédito Recorrente RCC"""
        try:
            self._fechar_dashboard_se_aberto()
            from vindi import ConciliacaoVindiView
            ConciliacaoVindiView(self.parent)
        except Exception as e:
            print(f"Erro ao abrir Conciliação Vindi: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir Conciliação Vindi:\n{e}")

    def abrir_nova_requisicao(self):
        """Abre o formulário de Nova Requisição de Materiais"""
        try:
            self._fechar_dashboard_se_aberto()
            from estoque import abrir_nova_requisicao_material
            abrir_nova_requisicao_material(self.parent)
        except Exception as e:
            print(f"Erro ao abrir Nova Requisição de Material: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir Nova Requisição de Material:\n{e}")

    def abrir_usuarios_geoapolo(self):
        """Abre o formulário de Gestão de Usuários GeoApolo"""
        try:
            self._fechar_dashboard_se_aberto()
            from usuarios import UsuariosView
            top = tk.Toplevel(self.parent)
            top.title("Gestão de Usuários, Grupos e Perfis de Acesso - GeoAlvo")
            top.minsize(800, 500)
            centralizar_janela(top, self.parent, 960, 620)
            view = UsuariosView(top)
            view.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            print(f"Erro ao abrir gestão de usuários: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir gestão de usuários:\n{e}")

    def create_toolbar(self):
        """Cria a estrutura da toolbar"""
        # Frame principal da toolbar
        self.toolbar = tk.Frame(self.parent, bd=1, relief=tk.RAISED, bg='#f0f0f0')
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Configuração dos botões da toolbar
        self.toolbar_config = [            
            # Seção: Principal (Configurações, Entidades, Conciliação Vindi, Nova Requisição de Material)
            {'name': 'config_bd', 'icon': 'database.png', 'text': 'Configurações', 'command': self.abrir_config_bancob, 'tooltip': 'Configurações'},
            {'name': 'entidades', 'icon': 'entidades.png', 'text': 'Entidades', 'command': self.abrir_entidades, 'tooltip': 'Entidades'},
            {'name': 'conciliacao_vindi', 'icon': 'cifrao.png', 'text': 'R$', 'command': self.abrir_concilia_vindi, 'tooltip': 'Conciliação Vindi'},
            {'name': 'nova_requisicao', 'icon': 'requisicao.png', 'text': 'Requisição', 'command': self.abrir_nova_requisicao, 'tooltip': 'Nova Requisição de Material'},
            {'type': 'separator'},

            # Seção: Arquivo (Troca de Empresa)
            {'name': 'troca_empresa', 'icon': 'company.png', 'text': 'Troca Empresa', 'command': self.change_company, 'tooltip': 'Troca de empresa no sistema'},
            {'type': 'separator'},
            
            # Seção: Usuários GeoApolo
            {'name': 'usuarios', 'icon': 'users.png', 'text': 'Usuários', 'command': self.abrir_usuarios_geoapolo, 'tooltip': 'Usuários GeoApolo'},
            {'type': 'separator'},

            # Seção: Impressão e Consultas Imediatas (Imprimir posicionado antes do funil de consultas)
            {'name': 'imprimir', 'icon': 'print.png', 'text': 'Imprimir', 'command': self.imprimir, 'tooltip': 'Imprimir documento (Ctrl+P)'},
            {'name': 'consultas_imediatas', 'icon': 'funil.png', 'text': 'Consultas', 'command': self.abrir_consultas_imediatas, 'tooltip': 'Consultas Imediatas'},
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
        
        # Efeitos hover
        btn.bind("<Enter>", lambda e, b=btn: self.on_enter(b), add="+")
        btn.bind("<Leave>", lambda e, b=btn: self.on_leave(b), add="+")

        # Adicionar tooltip
        if tooltip:
            self.create_tooltip(btn, tooltip)
        
        # Salvar referência
        self.buttons[name] = btn
        self.items.append({'type': 'button', 'name': name, 'widget': btn})
    
    def add_separator(self):
        """Adiciona um separador vertical"""
        separator = tk.Frame(self.toolbar, width=2, height=30, bg='#d0d0d0', relief=tk.SUNKEN, bd=1)
        separator.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
        self.items.append({'type': 'separator', 'widget': separator})
    
    def load_icon(self, filename, size=(24, 24)):
        """Carrega um ícone com tratamento de erro"""
        base_path = obter_caminho_recurso("Imagens")
        full_path = os.path.join(base_path, filename)
        
        try:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                # Usar PIL para redimensionar
                image = Image.open(full_path)
                image = image.resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(image, master=self.parent)
            else:
                # Para arquivos .gif nativos do tkinter
                return tk.PhotoImage(file=full_path)
        except Exception as e:
            print(f"Erro ao carregar ícone {filename}: {e}")
            return None
    
    def create_tooltip(self, widget, text):
        """Cria tooltip para um widget"""
        def show_tooltip(event):
            if hasattr(widget, 'tooltip') and widget.tooltip:
                try:
                    widget.tooltip.destroy()
                except Exception:
                    pass

            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.configure(bg='#ffffe0', relief='solid', bd=1)
            
            label = tk.Label(tooltip, text=text, bg='#ffffe0', fg='black', 
                           font=('Segoe UI', 9), padx=6, pady=3)
            label.pack()
            
            x = event.x_root + 10
            y = event.y_root + 18
            tooltip.geometry(f"+{x}+{y}")
            
            widget.tooltip = tooltip
            tooltip.after(3500, lambda: hide_tooltip(None))
        
        def hide_tooltip(event=None):
            if hasattr(widget, 'tooltip') and widget.tooltip:
                try:
                    widget.tooltip.destroy()
                except Exception:
                    pass
                delattr(widget, 'tooltip')
        
        widget.bind("<Enter>", show_tooltip, add="+")
        widget.bind("<Leave>", hide_tooltip, add="+")
    
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
    
    def show_button(self, name):
        """Exibe um botão específico na toolbar"""
        if name in self.buttons:
            self.buttons[name].pack(side=tk.LEFT, padx=1, pady=2)

    def hide_button(self, name):
        """Oculta um botão específico da toolbar"""
        if name in self.buttons:
            self.buttons[name].pack_forget()

    def aplicar_permissoes(self, gestor):
        """Aplica controle de acesso na barra de ferramentas:
        - Bloqueia e oculta a barra inteira se pnlmenuprincipal estiver desautorizado.
        - Para cada botão: se permitido, habilita e exibe; se bloqueado, desabilita e oculta.
        - Elimina separadores órfãos ou duplicados."""
        if not gestor:
            return

        # 1. Verifica bloqueio global da barra de ferramentas (pnlmenuprincipal)
        if not gestor.pode_acessar("pnlmenuprincipal"):
            self.toolbar.pack_forget()
            return
        else:
            self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # 2. Desempacota todos os itens para remontar em ordem precisa
        for item in self.items:
            try:
                item['widget'].pack_forget()
            except Exception:
                pass

        ultimo_item_foi_botao = False
        for item in self.items:
            if item['type'] == 'button':
                nome_btn = item['name']
                permitido = gestor.pode_acessar(nome_btn)
                btn = item['widget']
                if permitido:
                    btn.config(state=tk.NORMAL)
                    btn.pack(side=tk.LEFT, padx=1, pady=2)
                    ultimo_item_foi_botao = True
                else:
                    btn.config(state=tk.DISABLED)
                    # Não empacota o botão bloqueado -> permanece oculto
            elif item['type'] == 'separator':
                # Só exibe o separador se precedido por um botão visível
                if ultimo_item_foi_botao:
                    item['widget'].pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)
                    ultimo_item_foi_botao = False
    
    # ==========================================
    # MÉTODOS DE COMANDO DOS BOTÕES
    # ==========================================
    
    def change_company(self):
        """Abre o formulário de seleção de empresas para troca de contexto corporativo."""
        try:
            self._fechar_dashboard_se_aberto()
            from seleciona_empresa import TelaSelecaoEmpresa

            def _on_confirmar(cod, nome):
                try:
                    from geoalvo import definir_empresa_ativa
                    definir_empresa_ativa(self.parent, cod, nome)
                except Exception as ex:
                    print(f"Erro ao definir empresa ativa: {ex}")
                messagebox.showinfo("Troca de Empresa", f"Empresa ativa alterada com sucesso:\n{cod} - {nome}")

            form_empresa = TelaSelecaoEmpresa(self.parent, on_confirmar=_on_confirmar)
            form_empresa.executar()
        except Exception as e:
            print(f"Erro ao abrir seleção de empresa: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir seleção de empresa:\n{e}")
    
    def gerar_relatorio(self):
        """Abre a Central de Relatórios"""
        try:
            self._fechar_dashboard_se_aberto()
            from relatorios import RelatoriosView
            RelatoriosView(self.parent)
        except Exception as e:
            print(f"Erro ao abrir relatórios: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir relatórios:\n{e}")
    
    def imprimir(self):
        self.gerar_relatorio()
    
    def gerenciar_usuarios(self):
        self.abrir_usuarios_geoapolo()
    
    def configuracoes(self):
        self._fechar_dashboard_se_aberto()
        messagebox.showinfo("Configurações", "Configurações do sistema")
    
    def sair_aplicacao(self):
        if messagebox.askokcancel("Sair", "Deseja realmente sair do sistema?"):
            self.parent.quit()
            self.parent.destroy()
