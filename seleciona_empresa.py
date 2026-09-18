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

from core import obter_caminho_recurso

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
        caminho_icone = obter_caminho_recurso(os.path.join("Imagens", "GeoApolo_Icon.ico"))
        if os.path.exists(caminho_icone):
            try:
                self.root.iconbitmap(caminho_icone)
            except Exception:
                pass

        self._criar_interface()
        self._configurar_eventos()
        self._centralizar_janela()
        self.carregar_empresas()

    def _centralizar_janela(self):
        """Centraliza o formulário na tela."""
        try:
            self.root.update_idletasks()
            largura = 680
            altura = 420
            largura_tela = self.root.winfo_screenwidth()
            altura_tela = self.root.winfo_screenheight()
            x = max(0, (largura_tela - largura) // 2)
            y = max(0, (altura_tela - altura) // 2)
            self.root.geometry(f"{largura}x{altura}+{x}+{y}")
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
        self.tree_empresas.bind("<Double-1>", lambda e: self.confirmar_selecao())
        self.tree_empresas.bind("<Return>", lambda e: self.confirmar_selecao())
        self.root.bind("<Return>", lambda e: self.confirmar_selecao())

        # Atalho F3 (idêntico ao Delphi: if key = vk_f3 then gridempresas.OnDblClick)
        self.root.bind("<F3>", lambda e: self.confirmar_selecao())
        self.tree_empresas.bind("<F3>", lambda e: self.confirmar_selecao())

        # Atalho F10 e Esc para retornar (idêntico ao Delphi: if key = vk_f10 then spbretornar.click)
        self.root.bind("<F10>", lambda e: self.cancelar())
        self.root.bind("<Escape>", lambda e: self.cancelar())

        self.root.protocol("WM_DELETE_WINDOW", self.cancelar)

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
                self.status_bar.config(text="Nenhuma empresa cadastrada na tabela USER_geoapolo_empresas.")
                return

            for r in linhas:
                cod = str(r[0] or "").strip()
                nome = str(r[1] or "").strip()
                self.tree_empresas.insert("", tk.END, values=(cod, nome))

            # Seleciona o primeiro registro por padrão
            primeiro = self.tree_empresas.get_children()
            if primeiro:
                self.tree_empresas.selection_set(primeiro[0])
                self.tree_empresas.focus(primeiro[0])
                self.tree_empresas.focus_set()

            self.status_bar.config(
                text=f"{len(linhas)} empresa(s) disponível(is). Dê duplo clique ou tecle <Enter> para acessar."
            )
        except Exception as exc:
            logger.error("Falha ao consultar empresas no banco: %s", exc)
            self.status_bar.config(text=f"Erro ao carregar empresas: {exc}")
            messagebox.showerror("Erro de Banco", f"Não foi possível listar as empresas:\n{exc}")

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

        # Atualiza o contexto ativo através do EmpresasService se disponível
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

        if self.on_confirmar:
            self.on_confirmar(cod, nome)
        else:
            try:
                self.root.destroy()
            except Exception:
                pass

    def cancelar(self):
        """Cancela a seleção de empresa e retorna para a tela de logon."""
        if self.on_cancelar:
            self.on_cancelar()
        else:
            try:
                self.root.destroy()
            except Exception:
                pass

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
