"""
Utilitário para Resolução de Recursos, Imagens e Posicionamento de Janelas.
GeoApolo V5
Compatível com desenvolvimento e execução empacotada com PyInstaller (sys._MEIPASS).
"""

import os
import sys
from typing import Optional


def obter_caminho_recurso(caminho_relativo: str) -> str:
    """Retorna o caminho absoluto de um recurso/imagem, tanto em desenvolvimento
    quanto em executáveis empacotados pelo PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        base_dir = getattr(sys, "_MEIPASS")
    else:
        # Diretório raiz do projeto GeoApoloV5
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    caminho_normalizado = os.path.join(base_dir, caminho_relativo.replace("/", os.sep).replace("\\", os.sep))
    return caminho_normalizado


def aplicar_icone_janela(janela) -> bool:
    """Configura o ícone oficial da aplicação (faviconrcc.ico) na janela informada."""
    candidatos = [
        obter_caminho_recurso("faviconrcc.ico"),
        obter_caminho_recurso(os.path.join("Imagens", "faviconrcc.ico")),
        obter_caminho_recurso(os.path.join("Imagens", "GeoApolo_Icon.ico")),
    ]
    for c in candidatos:
        if os.path.exists(c):
            try:
                janela.iconbitmap(c)
                return True
            except Exception:
                try:
                    from PIL import Image, ImageTk
                    img = ImageTk.PhotoImage(Image.open(c))
                    janela.iconphoto(True, img)
                    janela._icon_ref_global = img
                    return True
                except Exception:
                    pass
    return False


def centralizar_janela(janela, parent=None, largura: int = 1000, altura: int = 650):
    """
    Centraliza uma janela (Toplevel/Tk) em relação à janela principal (menu principal)
    ou em relação à tela caso o parent não esteja visível/disponível.
    Equivalente a poMainFormCenter do Delphi.
    """
    try:
        janela.update_idletasks()
    except Exception:
        pass

    if parent is None:
        parent = getattr(janela, "master", None)

    pos_x = None
    pos_y = None

    if parent is not None:
        try:
            parent.update_idletasks()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            if pw > 100 and ph > 100:
                pos_x = px + (pw - largura) // 2
                pos_y = py + (ph - altura) // 2
        except Exception:
            pass

    try:
        sw = janela.winfo_screenwidth()
        sh = janela.winfo_screenheight()
    except Exception:
        sw, sh = 1920, 1080

    if pos_x is None or pos_y is None:
        pos_x = (sw - largura) // 2
        pos_y = (sh - altura) // 2 - 20

    # Garante que a janela permaneça dentro da área visível do monitor
    pos_x = max(10, min(pos_x, sw - largura - 10))
    pos_y = max(10, min(pos_y, sh - altura - 40))

    try:
        janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
    except Exception:
        pass


def geoapolo_configcod(empresa: str = "1.01", tabela: str = "USER_geoapolo_produtos", atualiza: str = "Sim", connection=None) -> str:
    """
    Função clássica do Delphi (funcoes.pas) para geração e incremento de código sequencial
    na tabela USER_geoapolo_configcod.
    """
    from entidades.database import obter_conexao_banco
    conn = connection or obter_conexao_banco()
    cur = conn.cursor()
    emp = (empresa or "1.01").strip()
    tab = tabela.strip()

    is_sql_server = not hasattr(conn, "isolation_level")
    nolock = "WITH (NOLOCK)" if is_sql_server else ""

    deve_atualizar = str(atualiza).strip().lower() in ("sim", "s", "true", "1")

    # Verifica se já existe registro para a tabela e empresa
    try:
        cur.execute(
            f"""
            SELECT proximo_codigo, ultimo_numero_utilizado, empcod
            FROM USER_geoapolo_configcod {nolock}
            WHERE (empcod = ? OR empcod = '1') AND UPPER(geotabela) = UPPER(?)
            ORDER BY CASE WHEN empcod = ? THEN 0 ELSE 1 END
            """,
            [emp, tab, emp]
        )
        row = cur.fetchone()
    except Exception:
        row = None

    if row and row[0] is not None:
        cod_atual = int(row[0])
        matched_emp = str(row[2])
        if deve_atualizar:
            novo_proximo = cod_atual + 1
            cur.execute(
                "UPDATE USER_geoapolo_configcod SET proximo_codigo = ?, ultimo_numero_utilizado = ?, tabela_ativa = 'S' WHERE empcod = ? AND UPPER(geotabela) = UPPER(?)",
                [novo_proximo, cod_atual, matched_emp, tab]
            )
            conn.commit()
        return str(cod_atual)
    else:
        # Se não existe registro, busca o maior código já existente na tabela de destino
        tab_lower = tab.lower()
        if "grupo" in tab_lower:
            candidatos = ["codigo_grupo", "grupocod", "cod_grupo"]
        elif "objeto" in tab_lower:
            candidatos = ["codigo_objeto", "objetocod", "cod_objeto"]
        elif "usuario" in tab_lower:
            candidatos = ["codigo_usuario", "usucod", "usuariocod"]
        elif "categoria" in tab_lower:
            candidatos = ["codigo_categoria", "categcod"]
        elif "entidade" in tab_lower:
            candidatos = ["geoentcod", "entcod", "codigo_entidade", "enticod"]
        else:
            candidatos = ["prodcod", "codigo", "cod", "id"]

        maior_cod = 0
        for campo in candidatos:
            try:
                cur.execute(f"SELECT COALESCE(MAX(CAST({campo} AS INT)), 0) FROM {tab} {nolock}")
                r_max = cur.fetchone()
                if r_max and r_max[0] is not None:
                    maior_cod = int(r_max[0])
                    break
            except Exception:
                continue

        cod_a_gerar = max(1, maior_cod + 1)
        novo_proximo = cod_a_gerar + 1 if deve_atualizar else cod_a_gerar
        ultimo_utilizado = cod_a_gerar if deve_atualizar else 0
        emp_gravar = emp if emp else "1"
        try:
            cur.execute(
                "INSERT INTO USER_geoapolo_configcod (empcod, geotabela, tabela_ativa, proximo_codigo, ultimo_numero_utilizado) VALUES (?, ?, 'S', ?, ?)",
                [emp_gravar, tab, novo_proximo, ultimo_utilizado]
            )
            conn.commit()
        except Exception:
            pass
        return str(cod_a_gerar)


def configurar_navegacao_enter(widgets: list):
    """
    Configura navegação em cadeia com a tecla Enter (<Return> e <KP_Enter>) para uma lista de widgets.
    Quando o usuário pressiona Enter em um widget, o foco salta imediatamente para o próximo widget da lista,
    padronizando a digitação rápida estilo ERP (semelhante à tecla Tab).
    """
    if not widgets or len(widgets) < 2:
        return

    for i in range(len(widgets) - 1):
        w_atual = widgets[i]
        w_prox = widgets[i + 1]

        def _criar_salto(destino):
            def _salto(event=None):
                try:
                    destino.focus_set()
                except Exception:
                    pass
                return "break"
            return _salto

        fn_salto = _criar_salto(w_prox)
        try:
            w_atual.bind("<Return>", fn_salto)
            w_atual.bind("<KP_Enter>", fn_salto)
        except Exception:
            pass


def vincular_maiusculo(var_ou_widget):
    """
    Assegura que qualquer valor digitado em uma StringVar ou Entry seja convertido
    automaticamente em letras maiúsculas.
    """
    try:
        import tkinter as tk
        if isinstance(var_ou_widget, tk.StringVar):
            def _upper_trace(*args):
                val = var_ou_widget.get()
                if val != val.upper():
                    var_ou_widget.set(val.upper())
            var_ou_widget.trace_add("write", _upper_trace)
        elif hasattr(var_ou_widget, "bind"):
            def _upper_entry(event=None):
                try:
                    texto = var_ou_widget.get()
                    if texto != texto.upper():
                        pos = var_ou_widget.index(tk.INSERT)
                        var_ou_widget.delete(0, tk.END)
                        var_ou_widget.insert(0, texto.upper())
                        var_ou_widget.icursor(pos)
                except Exception:
                    pass
            var_ou_widget.bind("<KeyRelease>", _upper_entry)
    except Exception:
        pass


def habilitar_filtro_dinamico_combobox(
    combobox,
    lista_completa: list,
    callback_selecao=None,
    callback_ao_nao_encontrar=None,
    maiusculo: bool = True,
):
    """
    Permite digitar texto diretamente no combobox e filtra interativamente os itens listados
    em tempo real, replicando o comportamento ágil de combos de busca do Delphi / Windows.
    Suporta busca inteligente por código (ex: '7', '01.01'), prefixo e substring,
    além de resolução e autocompletion automático em <Return>, <Tab> e <FocusOut>.
    """
    import unicodedata
    import tkinter as tk

    def normalizar(s: str) -> str:
        return unicodedata.normalize("NFKD", s or "").encode("ASCII", "ignore").decode("ASCII").lower().strip()

    def filtrar_itens(termo: str, itens: list) -> list:
        t = normalizar(termo)
        if not t:
            return list(itens)

        # 1. Match exato por código (ex: "7" em "ADOBE (007)", "01.01" em "01.01 - ADM", ou item "7")
        match_cod = []
        for it in itens:
            s_it = str(it).strip()
            # Padrão "cod - desc"
            if " - " in s_it:
                parte_cod = s_it.split(" - ")[0].strip()
                if normalizar(parte_cod) == t:
                    match_cod.append(it)
                    continue
            # Padrão "desc (cod)"
            if "(" in s_it and s_it.endswith(")"):
                parte_cod = s_it[s_it.rfind("(") + 1 : -1].strip()
                if normalizar(parte_cod) == t or (t.isdigit() and parte_cod.isdigit() and int(t) == int(parte_cod)):
                    match_cod.append(it)
                    continue
            # Item puramente numérico
            if t.isdigit() and s_it.isdigit() and int(t) == int(s_it):
                match_cod.append(it)
                continue

        if match_cod:
            return match_cod

        # 2. Match exato por descrição
        match_exato = [it for it in itens if normalizar(str(it)) == t]
        if match_exato:
            return match_exato

        # 3. Match por prefixo (inicia com o termo)
        iniciam = []
        for it in itens:
            s_it = str(it).strip()
            s_norm = normalizar(s_it)
            if s_norm.startswith(t):
                iniciam.append(it)
            elif " - " in s_it:
                parte_desc = normalizar(s_it.split(" - ")[1].strip())
                if parte_desc.startswith(t) and it not in iniciam:
                    iniciam.append(it)

        # 4. Match por substring (contém o termo)
        contem = [it for it in itens if t in normalizar(str(it)) and it not in iniciam]

        return iniciam + contem

    combobox._lista_completa_original = list(lista_completa)
    combobox["values"] = list(lista_completa)
    try:
        combobox["state"] = "normal"
    except Exception:
        pass

    def _resolver_selecao(event=None):
        termo = combobox.get().strip()
        originais = getattr(combobox, "_lista_completa_original", [])
        if not termo:
            combobox["values"] = originais
            return

        resultados = filtrar_itens(termo, originais)
        if resultados:
            escolhido = resultados[0]
            combobox.set(escolhido)
            combobox["values"] = originais
            if callback_selecao:
                try:
                    callback_selecao(escolhido)
                except Exception:
                    pass
        else:
            combobox["values"] = originais
            if callback_ao_nao_encontrar:
                try:
                    callback_ao_nao_encontrar(termo)
                except Exception:
                    pass

    def _on_key_release(event):
        # Teclas de confirmação e resolução
        if event.keysym in ("Return", "KP_Enter"):
            _resolver_selecao(event)
            return

        # Teclas de navegação pura (ignorar)
        if event.keysym in ("Up", "Down", "Escape", "Tab", "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Left", "Right", "Home", "End"):
            return

        # Forçar maiúsculas sem perder a posição do cursor
        if maiusculo:
            try:
                texto_raw = combobox.get()
                if texto_raw != texto_raw.upper():
                    pos = combobox.index(tk.INSERT)
                    combobox.delete(0, tk.END)
                    combobox.insert(0, texto_raw.upper())
                    combobox.icursor(pos)
            except Exception:
                pass

        termo = combobox.get().strip()
        originais = getattr(combobox, "_lista_completa_original", [])
        if not termo:
            combobox["values"] = originais
        else:
            filtrados = filtrar_itens(termo, originais)
            combobox["values"] = filtrados if filtrados else originais

    def _on_focus_out(event):
        _resolver_selecao(event)

    def _on_combobox_selected(event):
        originais = getattr(combobox, "_lista_completa_original", [])
        combobox["values"] = originais
        if callback_selecao:
            try:
                callback_selecao(combobox.get())
            except Exception:
                pass

    combobox.bind("<KeyRelease>", _on_key_release, add="+")
    combobox.bind("<FocusOut>", _on_focus_out, add="+")
    combobox.bind("<<ComboboxSelected>>", _on_combobox_selected, add="+")

    def _atualizar_lista(nova_lista: list):
        combobox._lista_completa_original = list(nova_lista)
        combobox["values"] = list(nova_lista)

    combobox.atualizar_valores_filtro = _atualizar_lista
    combobox.resolver_selecao_atual = _resolver_selecao


