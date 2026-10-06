"""
Componente Visual de Medidor (Gauge) Analítico para o Dashboard de Doações.
Desenha um medidor em arco (estilo velocímetro / tacômetro moderno)
com agulha indicadora, percentual em destaque e mensagens de status.
GeoApolo V5
"""

import math
import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable


class DashboardGaugeWidget(tk.Canvas):
    """
    Widget de velocímetro / gauge customizado em Tkinter Canvas.
    Renderiza um arco de 180 graus (semicírculo superior), trilha de fundo,
    arco colorido proporcional ao percentual, agulha móvel e texto de status.
    """

    def __init__(
        self,
        parent,
        width: int = 240,
        height: int = 150,
        bg: str = "#FFFFFF",
        titulo: str = "Progresso da Consulta",
        cor_arco: str = "#2563EB",
        cor_trilha: str = "#E2E8F0",
        **kwargs
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=bg,
            highlightthickness=0,
            **kwargs
        )
        self.w = width
        self.h = height
        self.titulo = titulo
        self.cor_arco = cor_arco
        self.cor_trilha = cor_trilha
        self.percentual: float = 0.0
        self.texto_status: str = "Aguardando..."

        # Dimensões geométricas do gauge
        self.cx = self.w / 2
        self.cy = self.h - 32
        self.raio = min(self.cx - 20, self.cy - 18)
        self.largura_arco = 14

        self.desenhar()

    def desenhar(self):
        """Redesenha todos os elementos visuais do gauge."""
        self.delete("all")

        # 1. Rótulo superior / Título
        if self.titulo:
            self.create_text(
                self.cx,
                14,
                text=self.titulo,
                font=("Segoe UI", 9, "bold"),
                fill="#1E293B"
            )

        # 2. Caixa delimitadora do arco (Bounding Box)
        x0 = self.cx - self.raio
        y0 = self.cy - self.raio
        x1 = self.cx + self.raio
        y1 = self.cy + self.raio

        # 3. Trilha de fundo (Semicírculo 180 graus de 180° a 0°)
        self.create_arc(
            x0, y0, x1, y1,
            start=0,
            extent=180,
            style=tk.ARC,
            outline=self.cor_trilha,
            width=self.largura_arco
        )

        # 4. Arco ativo de progresso (Proporcional de 180° no sentido horário)
        pct_clamped = max(0.0, min(100.0, self.percentual))
        if pct_clamped > 0:
            # Em Tkinter: start=180 (esquerda), extent negativo varre no sentido horário
            extensao = -1.8 * pct_clamped
            # Cor dinâmica: azul no início, verde petróleo em 100%
            if pct_clamped >= 100:
                cor_progresso = "#059669"  # Verde esmeralda
            elif pct_clamped >= 70:
                cor_progresso = "#0284C7"  # Azul ciano
            else:
                cor_progresso = self.cor_arco

            self.create_arc(
                x0, y0, x1, y1,
                start=180,
                extent=extensao,
                style=tk.ARC,
                outline=cor_progresso,
                width=self.largura_arco
            )

        # 5. Agulha indicadora
        # Ângulo em graus: 0% = 180° (esquerda), 50% = 90° (topo), 100% = 0° (direita)
        ang_graus = 180.0 - (1.8 * pct_clamped)
        ang_rad = math.radians(ang_graus)

        # Ponta da agulha
        comprimento_agulha = self.raio - 4
        nx = self.cx + comprimento_agulha * math.cos(ang_rad)
        ny = self.cy - comprimento_agulha * math.sin(ang_rad)

        # Desenho da agulha (linha sólida estilizada)
        self.create_line(
            self.cx, self.cy,
            nx, ny,
            fill="#0F172A",
            width=3,
            capstyle=tk.ROUND
        )

        # Cubo central da agulha
        r_hub = 7
        self.create_oval(
            self.cx - r_hub, self.cy - r_hub,
            self.cx + r_hub, self.cy + r_hub,
            fill="#1E293B",
            outline="#94A3B8",
            width=2
        )

        # 6. Texto do percentual numérico no centro do medidor
        texto_pct = f"{int(round(pct_clamped))}%"
        self.create_text(
            self.cx,
            self.cy - 24,
            text=texto_pct,
            font=("Segoe UI", 16, "bold"),
            fill="#0F172A"
        )

        # 7. Marcadores de extremos (0% e 100%)
        self.create_text(
            self.cx - self.raio - 2,
            self.cy + 10,
            text="0%",
            font=("Segoe UI", 7, "bold"),
            fill="#94A3B8"
        )
        self.create_text(
            self.cx + self.raio + 2,
            self.cy + 10,
            text="100%",
            font=("Segoe UI", 7, "bold"),
            fill="#94A3B8"
        )

        # 8. Texto da etapa atual / status
        if self.texto_status:
            self.create_text(
                self.cx,
                self.cy + 16,
                text=self.texto_status,
                font=("Segoe UI", 8),
                fill="#475569"
            )

    def definir_progresso(self, pct: float, texto: str = ""):
        """Atualiza imediatamente o valor e texto do gauge."""
        self.percentual = max(0.0, min(100.0, float(pct)))
        if texto:
            self.texto_status = texto
        self.desenhar()

    def resetar(self):
        """Reinicia o gauge para 0%."""
        self.percentual = 0.0
        self.texto_status = "Pronto para filtrar"
        self.desenhar()


class GaugeOverlay(tk.Frame):
    """
    Painel flutuante / Modal embutido com Gauge para exibir o progresso
    em tempo real enquanto consultas pesadas ou filtros são executados.
    """

    def __init__(self, parent, titulo: str = "Filtrando Dados de Doações...", **kwargs):
        super().__init__(
            parent,
            bg="#FFFFFF",
            bd=2,
            relief=tk.RAISED,
            padx=16,
            pady=12,
            **kwargs
        )
        self.parent = parent

        # Barra de título do card
        header = tk.Frame(self, bg="#FFFFFF")
        header.pack(fill=tk.X, pady=(0, 4))

        tk.Label(
            header,
            text="⚙️ PROCESSANDO FILTRO",
            font=("Segoe UI", 8, "bold"),
            fg="#2563EB",
            bg="#FFFFFF"
        ).pack(side=tk.LEFT)

        # Gauge central
        self.gauge = DashboardGaugeWidget(
            self,
            width=260,
            height=160,
            bg="#FFFFFF",
            titulo=titulo,
            cor_arco="#2563EB"
        )
        self.gauge.pack(pady=4)

        # Barra de progresso linear complementar
        self.prog_bar = ttk.Progressbar(self, orient="horizontal", length=240, mode="determinate")
        self.prog_bar.pack(pady=(4, 6))

        # Detalhe textual da operação
        self.lbl_detalhes = tk.Label(
            self,
            text="Iniciando consulta ao SQL Server...",
            font=("Segoe UI", 8),
            fg="#64748B",
            bg="#FFFFFF"
        )
        self.lbl_detalhes.pack()

    def atualizar(self, pct: float, status: str = ""):
        """Atualiza tanto o gauge analítico quanto a barra linear."""
        self.gauge.definir_progresso(pct, status)
        self.prog_bar["value"] = pct
        if status:
            self.lbl_detalhes.config(text=status)

    def exibir(self):
        """Posiciona o card de forma centralizada sobre o elemento pai."""
        try:
            self.lift()
            self.place(relx=0.5, rely=0.45, anchor=tk.CENTER)
            self.atualizar(5, "Iniciando consulta...")
        except Exception:
            pass

    def ocultar(self):
        """Remove o card do overlay."""
        try:
            self.place_forget()
        except Exception:
            pass
