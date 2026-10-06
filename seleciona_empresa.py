"""
Módulo de Seleção de Empresa do GeoAlvo / GeoApolo V5.
Equivalente direto ao formulário Delphi Tfrmempresa (unt_selecionaempresa.pas / unt_selecionaempresa.dfm).
Responsabilidade:
  - Exibir a lista de empresas/filiais cadastradas na base de dados (USER_geoapolo_empresas).
  - Permitir a seleção da empresa ativa para o contexto da sessão corporativa.
  - Atalhos idênticos ao Delphi:
      * Duplo clique / <Return> / <F3>: Seleciona a empresa e abre o menu principal.
      * <F10> / <Escape>: Retorna ao formulário anterior (Logon).
"""

import os
import sys
import logging
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, List, Tuple

# Garante que o diretório raiz esteja no sys.path
_raiz_projeto = str(Path(__file__).resolve().parent)
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

from core import obter_caminho_recurso, aplicar_icone_janela

logger = logging.getLogger(__name__)


class TelaSelecaoEmpresa:
    """
    Formulário de Seleção de Empresa (Tfrmempresa).
    Apresentado imediatamente após o logon com sucesso para definir o contexto da filial ativa.
    """

    def __init__(
        self,
        parent=None,
        on_confirmar: Optional[Callable[[str, str], None]] = None,
        on_cancelar: Optional[Callable[[], None]] = None,
    ):
        self.parent = parent
        self.on_confirmar = on_confirmar
        self.on_cancelar = on_cancelar
        self.empresa_selecionada: Optional[Tuple[str, str]] = None

        if self.parent is not None:
            self.root = tk.Toplevel(self.parent)
        else:
            self.root = tk.Tk()

        self.root.title("Selecione a Empresa")
        self.root.geometry("680x420")
        self.root.minsize(580, 360)

        # Configura ícone da janela
        aplicar_icone_janela(self.root)

        self._criar_interface()
        self._configurar_eventos()
        self._centralizar_janela()
        self.carregar_empresas()

    def _centralizar_janela(self):
        """Centraliza o formulário na tela ou em relação à janela mãe."""
        try:
            from core import centralizar_janela
            centralizar_janela(self.root, self.parent, 680, 420)
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            self.root.attributes("-topmost", True)
            self.root.after(300, lambda: self._remover_topmost())
        except Exception:
            pass

    def _remover_topmost(self):
        try:
            self.root.attributes("-topmost", False)
        except Exception:
            pass

    def _criar_interface(self):
        """Monta os componentes visuais correspondentes ao Tfrmempresa do Delphi."""
        # Painel Superior de Cabeçalho
        panel_top = tk.Frame(self.root, bg="#1E3A8A", padx=16, pady=12)
        panel_top.pack(fill=tk.X)

        lbl_titulo = tk.Label(
            panel_top,
            text="SELEÇÃO DE EMPRESA",
            font=("Segoe UI", 12, "bold"),
            fg="white",
            bg="#1E3A8A",
        )
        lbl_titulo.pack(anchor="w")

        lbl_sub = tk.Label(
            panel_top,
            text="Selecione a empresa / filial desejada para acessar o sistema:",
            font=("Segoe UI", 9),
            fg="#BFDBFE",
            bg="#1E3A8A",
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # Container Principal
        container = tk.Frame(self.root, bg="#F3F4F6", padx=14, pady=10)
        container.pack(fill=tk.BOTH, expand=True)

        # Grade / Grid de Empresas (equivalente ao gridempresas: TDBGrid)
        frame_grid = tk.Frame(container, bg="#FFFFFF", bd=1, relief="solid")
        frame_grid.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        colunas = ("codigo", "nome")
        self.tree_empresas = ttk.Treeview(
            frame_grid,
            columns=colunas,
            show="headings",
            selectmode="browse",
        )

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            font=("Segoe UI", 10),
            rowheight=26,
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#E5E7EB",
            foreground="#1F2937",
        )
        style.map("Treeview", background=[("selected", "#2563EB")], foreground=[("selected", "#FFFFFF")])

        self.tree_empresas.heading("codigo", text="Código", anchor="center")
        self.tree_empresas.heading("nome", text="Razão Social / Filial", anchor="w")

        self.tree_empresas.column("codigo", width=100, minwidth=80, anchor="center")
        self.tree_empresas.column("nome", width=520, minwidth=300, anchor="w")

        scroll_y = ttk.Scrollbar(frame_grid, orient="vertical", command=self.tree_empresas.yview)
        self.tree_empresas.configure(yscrollcommand=scroll_y.set)

        self.tree_empresas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Barra de Botões
        frame_botoes = tk.Frame(container, bg="#F3F4F6")
        frame_botoes.pack(fill=tk.X, pady=(0, 5))

        self.btn_confirmar = tk.Button(
            frame_botoes,
            text="✔ Confirmar Seleção (F3 / Enter)",
            font=("Segoe UI", 10, "bold"),
            bg="#2563EB",
            fg="white",
            height=2,
            padx=15,
            relief="flat",
            cursor="hand2",
            command=self.confirmar_selecao,
        )
        self.btn_confirmar.pack(side=tk.LEFT)

        self.btn_retornar = tk.Button(
            frame_botoes,
            text="✖ Retornar (F10)",
            font=("Segoe UI", 10, "bold"),
            bg="#DC2626",
            fg="white",
            height=2,
            padx=15,
            relief="flat",
            cursor="hand2",
            command=self.cancelar,
        )
        self.btn_retornar.pack(side=tk.RIGHT)

        # Barra de Status Inferior (StatusBar1)
        self.status_bar = tk.Label(
            self.root,
            text="Carregando empresas cadastradas...",
            font=("Segoe UI", 8),
            bd=1,
            relief="sunken",
            anchor="w",
            padx=8,
            pady=3,
            bg="#E5E7EB",
            fg="#374151",
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _configurar_eventos(self):
        """Atalhos de teclado idênticos ao Delphi unt_selecionaempresa.pas."""
        self.tree_empresas.bind("<Double-1>", self._on_tree_double_click)
        self.tree_empresas.bind("<Return>", self._ao_teclar_enter)
        self.root.bind("<Return>", self._ao_teclar_enter)

        # Atalho F3 (idêntico ao Delphi: if key = vk_f3 then gridempresas.OnDblClick)
        self.root.bind("<F3>", self._ao_pressionar_f3)
        self.tree_empresas.bind("<F3>", self._ao_pressionar_f3)

        # Atalho F10 e Esc para retornar (idêntico ao Delphi: if key = vk_f10 then spbretornar.click)
        self.root.bind("<F10>", self._ao_cancelar_evento)
        self.root.bind("<Escape>", self._ao_cancelar_evento)

        self.root.protocol("WM_DELETE_WINDOW", self.cancelar)

    def _ao_teclar_enter(self, event=None):
        self.confirmar_selecao()
        return "break"

    def _ao_pressionar_f3(self, event=None):
        self.confirmar_selecao()
        return "break"

    def _ao_cancelar_evento(self, event=None):
        self.cancelar()
        return "break"

    def _on_tree_double_click(self, event=None):
        """Garante que a linha clicada com duplo clique seja selecionada antes de confirmar."""
        if event:
            row_id = self.tree_empresas.identify_row(event.y)
            if row_id:
                self.tree_empresas.selection_set(row_id)
                self.tree_empresas.focus(row_id)
        self.confirmar_selecao()
        return "break"

    def carregar_empresas(self):
        """Consulta as empresas na tabela USER_geoapolo_empresas do banco ativo."""
        for item in self.tree_empresas.get_children():
            self.tree_empresas.delete(item)

        try:
            from entidades.database import obter_conexao_banco
            conn = obter_conexao_banco()
            cursor = conn.cursor()
            sql = "SELECT empcod, empnome FROM USER_geoapolo_empresas ORDER BY empcod ASC"
            cursor.execute(sql)
            linhas = cursor.fetchall()
            conn.close()

            if not linhas:
                self.status_bar.config(text="Nenhuma empresa cadastrada na base. Empresa padrão (1.01) selecionada.")
                # Insere empresa padrão de contingência para permitir o acesso administrativo inicial
                self.tree_empresas.insert("", tk.END, values=("1.01", "1.01 - RCC BRASIL (Padrão)"))
                primeiro = self.tree_empresas.get_children()
                if primeiro:
                    self.tree_empresas.selection_set(primeiro[0])
                    self.tree_empresas.focus(primeiro[0])
                    self.tree_empresas.focus_set()
                return

            for r in linhas:
                cod = str(r[0] or "").strip()
                nome = str(r[1] or "").strip()
                self.tree_empresas.insert("", tk.END, values=(cod, nome))

            # Seleciona preferencialmente a empresa 1.01 ou a primeira da lista
            filhos = self.tree_empresas.get_children()
            item_selecionado = filhos[0] if filhos else None
            for item in filhos:
                val = self.tree_empresas.item(item, "values")
                if val and str(val[0]).strip() == "1.01":
                    item_selecionado = item
                    break
            if item_selecionado:
                self.tree_empresas.selection_set(item_selecionado)
                self.tree_empresas.focus(item_selecionado)
                self.tree_empresas.focus_set()

            self.status_bar.config(
                text=f"{len(linhas)} empresa(s) disponível(is). Dê duplo clique ou tecle <Enter> para acessar."
            )
        except Exception as exc:
            logger.error("Falha ao consultar empresas no banco: %s", exc)
            self.status_bar.config(text=f"Erro de conexão com o banco. Pressione Enter para modo de contingência.")
            # Insere opção de contingência corporativa para que o usuário não fique bloqueado
            self.tree_empresas.insert("", tk.END, values=("1.01", "1.01 - RCC BRASIL"))
            primeiro = self.tree_empresas.get_children()
            if primeiro:
                self.tree_empresas.selection_set(primeiro[0])
                self.tree_empresas.focus(primeiro[0])
                self.tree_empresas.focus_set()

    def confirmar_selecao(self):
        """Confirma a empresa selecionada e prossegue para a aplicação principal."""
        selecionados = self.tree_empresas.selection()
        if not selecionados:
            messagebox.showwarning("Atenção", "Por favor, selecione uma empresa na grade para prosseguir.")
            return

        item = self.tree_empresas.item(selecionados[0])
        valores = item.get("values", [])
        if not valores or len(valores) < 2:
            messagebox.showwarning("Atenção", "Registro de empresa inválido.")
            return

        cod = str(valores[0]).strip()
        nome = str(valores[1]).strip()
        self.empresa_selecionada = (cod, nome)

        # Atualiza a empresa ativa globalmente na sessão e no contexto corporativo
        try:
            from core.sessao import definir_empresa_ativa
            definir_empresa_ativa(cod, nome)
        except Exception:
            try:
                from logon import sessao_usuario_atual
                sessao_usuario_atual["codigo_empresa"] = cod
                sessao_usuario_atual["empcod"] = cod
                sessao_usuario_atual["nome_empresa"] = nome
            except Exception:
                pass
            try:
                from entidades.database import obter_conexao_banco
                from empresas.repository import EmpresasRepository
                from empresas.service import EmpresasService
                conn = obter_conexao_banco()
                service = EmpresasService(EmpresasRepository(conn))
                service.selecionar_empresa_ativa(cod)
                conn.close()
            except Exception:
                pass


        # Atualiza status de integração com Alvo para a empresa selecionada
        try:
            from logon import sessao_usuario_atual
            from entidades.database import obter_conexao_banco
            conn_cfg = obter_conexao_banco()
            cur_cfg = conn_cfg.cursor()
            cur_cfg.execute("SELECT integra_base_apolomix, integra_entidades_apolo FROM USER_geoapolo_configuracoes WHERE empcod = ?", [cod])
            cfg_row = cur_cfg.fetchone()
            if cfg_row:
                integra_base = str(cfg_row[0] or "").strip().upper()
                integra_ent = str(cfg_row[1] or "").strip().lower()
                if integra_base == "N" or integra_ent in ("não integra", "nao integra"):
                    sessao_usuario_atual["integra_alvo"] = False
            conn_cfg.close()
        except Exception:
            pass

        try:
            self.root.destroy()
        except Exception:
            pass

        if self.on_confirmar:
            self.on_confirmar(cod, nome)

        return "break"

    def cancelar(self):
        """Cancela a seleção de empresa e retorna para a tela de logon."""
        try:
            self.root.destroy()
        except Exception:
            pass

        if self.on_cancelar:
            self.on_cancelar()

        return "break"

    def executar(self):
        """Inicia o loop da interface gráfica."""
        if isinstance(self.root, tk.Tk):
            self.root.mainloop()
        else:
            try:
                self.root.grab_set()
                self.root.wait_window()
            except Exception:
                pass


if __name__ == "__main__":
    app = TelaSelecaoEmpresa()
    app.executar()
