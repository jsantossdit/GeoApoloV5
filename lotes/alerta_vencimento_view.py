"""
Modal Gráfico para Alertas e Bloqueios por Vencimento de Lote.
GeoApolo V5
Alerta Amarelo (10 a 30 dias), Alerta Vermelho (5 a 10 dias) e Bloqueio Roxo (0 a 5 dias ou vencido).
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from core import centralizar_janela, aplicar_icone_janela


def exibir_alerta_vencimento_lote(
    parent,
    nivel: str,
    numero_lote: str,
    prodnome: str = "",
    data_validade: str = "",
    dias_restantes: int = 0,
) -> bool:
    """
    Exibe modal corporativo com os alertas visuais definidos:
    - 'AMARELO': Retorna True se o usuário confirmar o uso do lote, False se cancelar.
    - 'VERMELHO': Retorna True se o usuário confirmar o risco do lote, False se cancelar.
    - 'ROXO': Exibe mensagem de bloqueio total e retorna SEMPRE False (impede a operação).
    """
    modal = tk.Toplevel(parent)
    modal.transient(parent)
    modal.grab_set()

    # Variável de resultado
    resultado = {"confirmou": False}

    # Definição de cores e textos de acordo com o nível
    if nivel == "ROXO":
        cor_header_bg = "#F3E8FF"
        cor_header_fg = "#581C87"
        cor_borda = "#9333EA"
        cor_badge_bg = "#581C87"
        cor_badge_fg = "#FFFFFF"
        icone_titulo = "⛔ BLOQUEIO ROXO: LOTE IMPEDIDO DE SAÍDA"
        subtitulo = "OPERAÇÃO BLOQUEADA PELO SISTEMA (0 A 5 DIAS / VENCIDO)"
        titulo_janela = "Bloqueio de Movimentação por Vencimento de Lote"
    elif nivel == "VERMELHO":
        cor_header_bg = "#FEE2E2"
        cor_header_fg = "#991B1B"
        cor_borda = "#EF4444"
        cor_badge_bg = "#DC2626"
        cor_badge_fg = "#FFFFFF"
        icone_titulo = "🚨 ALERTA VERMELHO: LOTE MUITO PERTO DO VENCIMENTO"
        subtitulo = "ATENÇÃO CRÍTICA: VALIDADE ENTRE 5 E 10 DIAS"
        titulo_janela = "Alerta Crítico: Lote Muito Perto do Vencimento"
    else:  # AMARELO
        cor_header_bg = "#FEF9C3"
        cor_header_fg = "#854D0E"
        cor_borda = "#EAB308"
        cor_badge_bg = "#CA8A04"
        cor_badge_fg = "#FFFFFF"
        icone_titulo = "⚠️ ALERTA AMARELO: LOTE PERTO DO VENCIMENTO"
        subtitulo = "AVISO DE VENCIMENTO: VALIDADE ENTRE 10 E 30 DIAS"
        titulo_janela = "Alerta: Lote Perto do Vencimento"

    modal.title(titulo_janela)
    modal.geometry("560x380")
    modal.minsize(520, 360)
    centralizar_janela(modal, parent, 560, 380)
    aplicar_icone_janela(modal)

    modal.configure(bg="#F8FAFC")

    # Header Colorido
    header = tk.Frame(modal, bg=cor_header_bg, bd=2, relief=tk.SOLID, padx=16, pady=12)
    header.pack(fill=tk.X, padx=12, pady=(12, 8))

    lbl_badge = tk.Label(
        header,
        text=icone_titulo,
        bg=cor_badge_bg,
        fg=cor_badge_fg,
        font=("Segoe UI", 10, "bold"),
        padx=10,
        pady=3,
    )
    lbl_badge.pack(anchor=tk.W, pady=(0, 4))

    lbl_sub = tk.Label(
        header,
        text=subtitulo,
        bg=cor_header_bg,
        fg=cor_header_fg,
        font=("Segoe UI", 8, "bold"),
    )
    lbl_sub.pack(anchor=tk.W)

    # Card com detalhes do Material e do Lote
    card = tk.LabelFrame(
        modal,
        text=" Informações do Lote Selecionado ",
        font=("Segoe UI", 9, "bold"),
        bg="#FFFFFF",
        fg="#1E293B",
        padx=14,
        pady=10,
    )
    card.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

    # Produto
    f_p = tk.Frame(card, bg="#FFFFFF")
    f_p.pack(fill=tk.X, pady=2)
    tk.Label(f_p, text="Material / Produto:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569", width=18, anchor=tk.W).pack(side=tk.LEFT)
    tk.Label(f_p, text=prodnome or "(Não informado)", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#0F172A", wraplength=340, justify=tk.LEFT).pack(side=tk.LEFT, fill=tk.X, expand=True)

    # Número do Lote
    f_l = tk.Frame(card, bg="#FFFFFF")
    f_l.pack(fill=tk.X, pady=2)
    tk.Label(f_l, text="Número do Lote:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569", width=18, anchor=tk.W).pack(side=tk.LEFT)
    tk.Label(f_l, text=numero_lote, font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg="#1E3A8A").pack(side=tk.LEFT)

    # Data de Validade
    f_v = tk.Frame(card, bg="#FFFFFF")
    f_v.pack(fill=tk.X, pady=2)
    tk.Label(f_v, text="Data de Validade:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569", width=18, anchor=tk.W).pack(side=tk.LEFT)
    tk.Label(f_v, text=data_validade or "(Sem data)", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#0F172A").pack(side=tk.LEFT)

    # Prazo Restante
    f_d = tk.Frame(card, bg="#FFFFFF")
    f_d.pack(fill=tk.X, pady=2)
    tk.Label(f_d, text="Situação do Prazo:", font=("Segoe UI", 9, "bold"), bg="#FFFFFF", fg="#475569", width=18, anchor=tk.W).pack(side=tk.LEFT)

    if dias_restantes < 0:
        texto_prazo = f"VENCIDO HÁ {abs(dias_restantes)} DIA(S)!"
        cor_prazo = "#DC2626"
    elif dias_restantes == 0:
        texto_prazo = "VENCE HOJE!"
        cor_prazo = "#DC2626"
    else:
        texto_prazo = f"Restam {dias_restantes} dia(s) para o vencimento"
        cor_prazo = cor_badge_bg

    lbl_prazo = tk.Label(f_d, text=texto_prazo, font=("Segoe UI", 10, "bold"), bg="#FFFFFF", fg=cor_prazo)
    lbl_prazo.pack(side=tk.LEFT)

    # Mensagem de ação
    f_msg = tk.Frame(card, bg="#FFFFFF", pady=6)
    f_msg.pack(fill=tk.X)

    if nivel == "ROXO":
        texto_orientacao = (
            "⛔ IMPEDIMENTO: Conforme a política de controle de estoque, materiais com lote a 5 dias ou menos "
            "do vencimento (ou vencidos) estão com saída e atendimento BLOQUEADOS."
        )
        cor_txt_orient = "#581C87"
    elif nivel == "VERMELHO":
        texto_orientacao = (
            "🚨 ATENÇÃO: O lote está em período crítico. Deseja realmente confirmar e liberar "
            "a saída deste material por sua conta e risco?"
        )
        cor_txt_orient = "#991B1B"
    else:
        texto_orientacao = (
            "⚠️ AVISO: O lote informado está perto do vencimento. Deseja confirmar e prosseguir com a movimentação?"
        )
        cor_txt_orient = "#854D0E"

    lbl_orient = tk.Label(
        f_msg,
        text=texto_orientacao,
        font=("Segoe UI", 9, "bold"),
        bg="#F1F5F9",
        fg=cor_txt_orient,
        wraplength=500,
        justify=tk.LEFT,
        padx=10,
        pady=6,
        bd=1,
        relief=tk.GROOVE,
    )
    lbl_orient.pack(fill=tk.X)

    # Painel de Botões Inferior
    b_box = tk.Frame(modal, bg="#F8FAFC", padx=12, pady=10)
    b_box.pack(fill=tk.X, side=tk.BOTTOM)

    def fechar_bloqueio():
        resultado["confirmou"] = False
        modal.destroy()

    def confirmar_operacao():
        resultado["confirmou"] = True
        modal.destroy()

    if nivel == "ROXO":
        btn_bloqueado = tk.Button(
            b_box,
            text="Entendido / Cancelar Operação (Esc)",
            bg="#581C87",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=16,
            pady=6,
            cursor="hand2",
            command=fechar_bloqueio,
        )
        btn_bloqueado.pack(side=tk.RIGHT)
        modal.bind("<Escape>", lambda e: fechar_bloqueio())
        modal.bind("<Return>", lambda e: fechar_bloqueio())
        btn_bloqueado.focus_set()
    elif nivel == "VERMELHO":
        btn_conf = tk.Button(
            b_box,
            text="⚠ Confirmar Saída com Risco",
            bg="#DC2626",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            command=confirmar_operacao,
        )
        btn_conf.pack(side=tk.RIGHT, padx=(8, 0))

        btn_canc = tk.Button(
            b_box,
            text="Cancelar Operação (Esc)",
            bg="#64748B",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            command=fechar_bloqueio,
        )
        btn_canc.pack(side=tk.RIGHT)
        modal.bind("<Escape>", lambda e: fechar_bloqueio())
        btn_canc.focus_set()
    else:  # AMARELO
        btn_conf = tk.Button(
            b_box,
            text="✔ Prosseguir com o Lote",
            bg="#CA8A04",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            command=confirmar_operacao,
        )
        btn_conf.pack(side=tk.RIGHT, padx=(8, 0))

        btn_canc = tk.Button(
            b_box,
            text="Cancelar (Esc)",
            bg="#64748B",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            command=fechar_bloqueio,
        )
        btn_canc.pack(side=tk.RIGHT)
        modal.bind("<Escape>", lambda e: fechar_bloqueio())
        btn_conf.focus_set()

    # Aguarda o fechamento do modal
    modal.wait_window()
    return resultado["confirmou"]
