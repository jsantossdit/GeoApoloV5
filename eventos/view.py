"""
Interface Gráfica para Importação de Inscrições em Eventos e Congressos.
GeoApolo V5
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List
from .models import InscricaoEventoDTO
from .repository import EventosRepository
from .service import EventosService


class ImportarInscritosEventosView:
    """Janela corporativa para processar e vincular planilhas de congressistas à base Apolo."""

    def __init__(self, parent: tk.Tk, service: Optional[EventosService] = None):
        self.parent = parent
        self.service = service or EventosService(EventosRepository())

        self.window = tk.Toplevel(parent)
        self.window.title("GeoAlvo - Importação de Cadastros de Eventos")
        self.window.geometry("1040x680")
        self.window.minsize(900, 580)
        self.window.transient(parent)
        self.window.grab_set()

        self._inscricoes: List[InscricaoEventoDTO] = []
        self._setup_ui()

    def _setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg="#1A365D", height=60)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        lbl_titulo = tk.Label(
            header,
            text="Importação de Inscrições de Eventos / Congressos (Apolo x Web)",
            font=("Segoe UI", 13, "bold"),
            bg="#1A365D",
            fg="#FFFFFF",
        )
        lbl_titulo.pack(side=tk.LEFT, padx=15, pady=12)

        # Container Principal
        container = ttk.Frame(self.window, padding="15")
        container.pack(fill=tk.BOTH, expand=True)

        # Painel de Seleção de Arquivo e Evento
        file_frame = ttk.LabelFrame(container, text=" Origem dos Dados ", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))

        # Linha 1: Arquivo
        ttk.Label(file_frame, text="Arquivo da Planilha:").grid(row=0, column=0, padx=5, sticky="w")
        self.txt_arquivo = ttk.Entry(file_frame, width=60)
        self.txt_arquivo.grid(row=0, column=1, padx=5, sticky="we")

        btn_procurar = ttk.Button(file_frame, text="📂 Procurar...", command=self._selecionar_arquivo)
        btn_procurar.grid(row=0, column=2, padx=5, sticky="w")

        # Linha 2: ID Evento
        ttk.Label(file_frame, text="Identificador do Evento:").grid(row=1, column=0, padx=5, pady=(8, 0), sticky="w")
        self.txt_evento_id = ttk.Entry(file_frame, width=20)
        self.txt_evento_id.grid(row=1, column=1, padx=5, pady=(8, 0), sticky="w")

        btn_processar = tk.Button(
            file_frame,
            text="⚡ Carregar e Cruzar com Apolo",
            font=("Segoe UI", 9, "bold"),
            bg="#2B6CB0",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=12,
            pady=4,
            command=self._processar_planilha,
            cursor="hand2",
        )
        btn_processar.grid(row=1, column=2, padx=5, pady=(8, 0), sticky="w")

        file_frame.columnconfigure(1, weight=1)

        # Barra de Progresso
        self.progress_bar = ttk.Progressbar(container, orient=tk.HORIZONTAL, mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        # Grid Treeview
        grid_frame = ttk.Frame(container)
        grid_frame.pack(fill=tk.BOTH, expand=True)

        colunas = ("doc", "nome", "email", "fone", "cidade_uf", "valor", "entcod", "colabora", "anomes")
        self.tree = ttk.Treeview(grid_frame, columns=colunas, show="headings")

        self.tree.heading("doc", text="CPF / CNPJ")
        self.tree.heading("nome", text="Nome do Participante")
        self.tree.heading("email", text="E-mail")
        self.tree.heading("fone", text="Telefone")
        self.tree.heading("cidade_uf", text="Cidade / UF")
        self.tree.heading("valor", text="Valor (R$)")
        self.tree.heading("entcod", text="Entidade Apolo")
        self.tree.heading("colabora", text="Colabora Projetos?")
        self.tree.heading("anomes", text="Última Contribuição")

        self.tree.column("doc", width=120, anchor="center")
        self.tree.column("nome", width=220, anchor="w")
        self.tree.column("email", width=180, anchor="w")
        self.tree.column("fone", width=110, anchor="w")
        self.tree.column("cidade_uf", width=130, anchor="w")
        self.tree.column("valor", width=85, anchor="e")
        self.tree.column("entcod", width=100, anchor="center")
        self.tree.column("colabora", width=120, anchor="center")
        self.tree.column("anomes", width=120, anchor="center")

        scroll_y = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Rodapé Estatístico e Gravação
        totais_frame = tk.Frame(container, bg="#EDF2F7", bd=1, relief=tk.SOLID, padx=12, pady=10)
        totais_frame.pack(fill=tk.X, pady=(10, 0))

        self.lbl_tot_linhas = tk.Label(totais_frame, text="Total Registros: 0", font=("Segoe UI", 9, "bold"), bg="#EDF2F7", fg="#2D3748")
        self.lbl_tot_linhas.pack(side=tk.LEFT, padx=10)

        self.lbl_tot_doc = tk.Label(totais_frame, text="Com Documento: 0", font=("Segoe UI", 9, "bold"), bg="#EDF2F7", fg="#2B6CB0")
        self.lbl_tot_doc.pack(side=tk.LEFT, padx=10)

        self.lbl_tot_apolo = tk.Label(totais_frame, text="Vinculados no Apolo: 0", font=("Segoe UI", 9, "bold"), bg="#EDF2F7", fg="#2F855A")
        self.lbl_tot_apolo.pack(side=tk.LEFT, padx=10)

        self.lbl_tot_colab = tk.Label(totais_frame, text="Colaboradores: 0", font=("Segoe UI", 9, "bold"), bg="#EDF2F7", fg="#7B341E")
        self.lbl_tot_colab.pack(side=tk.LEFT, padx=10)

        self.btn_gravar = tk.Button(
            totais_frame,
            text="💾 Gravar no Banco Apolo",
            font=("Segoe UI", 9, "bold"),
            bg="#2F855A",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=15,
            pady=4,
            command=self._gravar_inscricoes,
            state=tk.DISABLED,
            cursor="hand2",
        )
        self.btn_gravar.pack(side=tk.RIGHT, padx=5)

    def _selecionar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Selecionar Planilha de Inscrições",
            filetypes=[
                ("Planilhas e CSV", "*.csv;*.xlsx;*.xls"),
                ("Arquivos CSV", "*.csv"),
                ("Planilhas Excel", "*.xlsx;*.xls"),
                ("Todos os arquivos", "*.*"),
            ],
        )
        if caminho:
            self.txt_arquivo.delete(0, tk.END)
            self.txt_arquivo.insert(0, caminho)

    def _processar_planilha(self):
        caminho = self.txt_arquivo.get().strip()
        evento_id = self.txt_evento_id.get().strip()

        if not caminho:
            messagebox.showwarning("Aviso", "Selecione o arquivo da planilha a importar.")
            return

        if not evento_id:
            messagebox.showwarning("Aviso", "Informe o identificador do evento (Ex: RCC2025).")
            return

        for it in self.tree.get_children():
            self.tree.delete(it)

        try:
            self._inscricoes = self.service.carregar_planilha(caminho, evento_id)
            if not self._inscricoes:
                messagebox.showinfo("Vazio", "Nenhum registro encontrado no arquivo informado.")
                return

            self.progress_bar["maximum"] = len(self._inscricoes)
            self.progress_bar["value"] = 0

            def atualiza_progresso(atual, total):
                self.progress_bar["value"] = atual
                self.window.update_idletasks()

            res = self.service.cruzar_com_apolo(self._inscricoes, callback_progresso=atualiza_progresso)

            colaboradores = 0
            for item in self._inscricoes:
                cidade_uf = f"{item.cidade}/{item.uf}".strip("/")
                val_str = f"{item.valor_venda:,.2f}"
                ent_str = item.ent_cod or "-"
                colab_str = "SIM" if item.colabora_projetos else "NÃO"
                if item.colabora_projetos:
                    colaboradores += 1

                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        item.documento or "-",
                        item.nome,
                        item.email,
                        item.telefone,
                        cidade_uf,
                        val_str,
                        ent_str,
                        colab_str,
                        item.ano_mes_ultima_contribuicao or "-",
                    ),
                )

            self.lbl_tot_linhas.config(text=f"Total Registros: {res.total_linhas}")
            self.lbl_tot_doc.config(text=f"Com Documento: {res.total_com_documento}")
            self.lbl_tot_apolo.config(text=f"Vinculados no Apolo: {res.total_vinculados_apolo}")
            self.lbl_tot_colab.config(text=f"Colaboradores: {colaboradores}")

            self.btn_gravar.config(state=tk.NORMAL)
            messagebox.showinfo(
                "Leitura Concluída",
                f"Foram lidos {res.total_linhas} inscritos.\n"
                f"{res.total_vinculados_apolo} já constam cadastrados na base Apolo.",
            )
        except Exception as e:
            messagebox.showerror("Erro ao Processar", f"Falha na leitura da planilha:\n{e}")

    def _gravar_inscricoes(self):
        evento_id = self.txt_evento_id.get().strip()
        if not evento_id or not self._inscricoes:
            return

        if self.service.evento_ja_importado(evento_id):
            if messagebox.askyesno(
                "Reimportação",
                f"Já existem registros cadastrados para o evento '{evento_id}'.\n"
                "Deseja substituir os dados existentes por esta nova importação?",
            ):
                self.service.remover_importacao_anterior(evento_id)
            else:
                return

        res = self.service.salvar_inscricoes(evento_id, self._inscricoes)
        if res.sucesso:
            messagebox.showinfo("Sucesso", res.mensagem)
            self.btn_gravar.config(state=tk.DISABLED)
        else:
            messagebox.showerror("Erro ao Gravar", res.mensagem)
