"""
Módulo de Utilitários de Data e Hora Corporativos do GeoAlvo.
Padroniza a manipulação, formatação e digitação de datas no padrão DD/MM/AAAA (pt-BR / SO).
"""

import re
from datetime import datetime, date
from typing import Optional, Any
import tkinter as tk


def aplicar_mascara_data(event, widget) -> None:
    """
    Aplica formatação progressiva DD/MM/AAAA dinamicamente enquanto o usuário digita.
    Ignora teclas de navegação e comandos para não atrapalhar a experiência do operador.
    """
    if event and getattr(event, "keysym", "") in (
        "BackSpace", "Delete", "Left", "Right", "Up", "Down",
        "Home", "End", "Tab", "Return", "ISO_Left_Tab",
        "Control_L", "Control_R", "Shift_L", "Shift_R", "Alt_L", "Alt_R",
        "Escape"
    ):
        return

    try:
        texto = widget.get()
    except Exception:
        return

    apenas_digitos = re.sub(r"\D", "", texto)[:8]
    if not apenas_digitos:
        return

    if len(apenas_digitos) <= 2:
        formatado = apenas_digitos
    elif len(apenas_digitos) <= 4:
        formatado = f"{apenas_digitos[:2]}/{apenas_digitos[2:]}"
    else:
        formatado = f"{apenas_digitos[:2]}/{apenas_digitos[2:4]}/{apenas_digitos[4:]}"

    if texto != formatado:
        try:
            widget.delete(0, tk.END)
            widget.insert(0, formatado)
        except Exception:
            pass


def vincular_mascara_data(widget) -> None:
    """
    Atalho corporativo para vincular a máscara DD/MM/AAAA ao evento KeyRelease de um Entry.
    """
    try:
        widget.bind("<KeyRelease>", lambda e: aplicar_mascara_data(e, widget), add="+")
    except Exception:
        pass


def parse_data_flexivel(texto: Any) -> Optional[date]:
    """
    Realiza o parse tolerante de uma data a partir de string ou objeto date/datetime.
    Suporta formatos DD/MM/AAAA, AAAA-MM-DD, DD-MM-AAAA, ISO com hora etc.
    """
    if not texto:
        return None

    if isinstance(texto, datetime):
        return texto.date()
    if isinstance(texto, date):
        return texto

    s = str(texto).strip()
    if not s:
        return None

    # Se contiver hora, isola os primeiros 10 caracteres
    parte_data = s[:10]

    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%y"):
        try:
            return datetime.strptime(parte_data, fmt).date()
        except ValueError:
            continue

    return None


def formatar_data_br(valor: Any, incluir_hora: bool = False, incluir_segundos: bool = False) -> str:
    """
    Converte qualquer valor de data/hora para o padrão corporativo brasileiro:
    - Se incluir_hora=False: DD/MM/AAAA (ex: '27/09/2026')
    - Se incluir_hora=True: DD/MM/AAAA HH:MM (ex: '27/09/2026 14:30')
    - Se incluir_segundos=True: DD/MM/AAAA HH:MM:SS (ex: '27/09/2026 14:30:15')
    """
    if valor is None:
        return ""

    if isinstance(valor, datetime):
        if incluir_segundos:
            return valor.strftime("%d/%m/%Y %H:%M:%S")
        if incluir_hora:
            return valor.strftime("%d/%m/%Y %H:%M")
        return valor.strftime("%d/%m/%Y")

    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")

    s = str(valor).strip()
    if not s:
        return ""

    # Se já estiver com barra (formato brasileiro DD/MM/AAAA)
    if "/" in s:
        partes = s.split(" ")
        dt_parte = partes[0]
        hora_parte = partes[1] if len(partes) > 1 else ""
        if not incluir_hora or not hora_parte:
            return dt_parte
        if incluir_segundos:
            return f"{dt_parte} {hora_parte[:8]}"
        return f"{dt_parte} {hora_parte[:5]}"

    # Se estiver no padrão ISO com hífen (AAAA-MM-DD...)
    if "-" in s:
        # Tenta parsear com hora
        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d",
        ):
            try:
                dt = datetime.strptime(s[:19], fmt[: len(s[:19])])
                if incluir_segundos and dt.hour + dt.minute + dt.second > 0:
                    return dt.strftime("%d/%m/%Y %H:%M:%S")
                if incluir_hora and (dt.hour + dt.minute > 0 or len(s) > 10):
                    return dt.strftime("%d/%m/%Y %H:%M")
                return dt.strftime("%d/%m/%Y")
            except (ValueError, TypeError):
                continue

        # Fallback simples por split
        partes = s.split(" ")
        dt_iso = partes[0].split("-")
        if len(dt_iso) == 3 and len(dt_iso[0]) == 4:
            br_data = f"{dt_iso[2]}/{dt_iso[1]}/{dt_iso[0]}"
            if incluir_hora and len(partes) > 1:
                return f"{br_data} {partes[1][:5]}"
            return br_data

    return s


def converter_data_br_para_iso(texto: Any, fim_do_dia: bool = False) -> str:
    """
    Converte com segurança uma data em formato DD/MM/AAAA (ou qualquer formato flexível)
    para o formato aceito por bancos SQL (YYYY-MM-DD ou YYYY-MM-DD 23:59:59).
    """
    if not texto:
        return ""

    d = parse_data_flexivel(texto)
    if not d:
        s = str(texto).strip()
        return s

    iso = d.strftime("%Y-%m-%d")
    if fim_do_dia:
        return f"{iso} 23:59:59"
    return iso


def validar_data_br(texto: str) -> bool:
    """Verifica se a string é uma data válida no calendário no formato DD/MM/AAAA."""
    if not texto or not isinstance(texto, str):
        return False
    t = texto.strip()
    if len(t) != 10:
        return False
    try:
        datetime.strptime(t, "%d/%m/%Y")
        return True
    except ValueError:
        return False
