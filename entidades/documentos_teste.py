"""
Módulo para gerenciamento de documentos de teste (CPF/CNPJ) para Grupos de Oração.
Lê e remove documentos consumidos dos arquivos:
- cpfs_teste_200.csv (Pessoa Física)
- cnpjs_teste_200.csv (Pessoa Jurídica)
"""

import os
import sys
import logging
import re
from pathlib import Path
from typing import Optional, Tuple, Any

logger = logging.getLogger(__name__)


def obter_caminho_arquivo_teste(nome_arquivo: str) -> Optional[Path]:
    """
    Localiza o arquivo CSV de teste na ordem:
    1. Diretório do executável (sys.executable)
    2. Diretório de trabalho atual (Path.cwd())
    3. Diretório raiz do projeto (onde está geoalvo.py)
    """
    candidatos = [
        Path(sys.executable).parent / nome_arquivo,
        Path.cwd() / nome_arquivo,
        Path(__file__).resolve().parent.parent / nome_arquivo,
        Path(__file__).resolve().parent / nome_arquivo,
    ]
    for p in candidatos:
        if p.is_file():
            return p
    return None


def eh_grupo_de_oracao(geoentcod: str, dados_entidade: dict, repo: Any = None) -> bool:
    """
    Verifica se a entidade em questão é um Grupo de Oração através de:
    - Categoria 02.001 (ou subcategorias de GO 02.001.0000 a 02.001.0005)
    - Tabela USER_geoapolo_gruposdeoracao
    - Nome da entidade contendo menção a Grupo de Oração
    """
    if not dados_entidade and not geoentcod:
        return False

    dados = dados_entidade or {}

    # 1. Checa categorias nas propriedades do dicionário
    cats = str(dados.get("geocategcodestr") or dados.get("categcodestr") or "")
    if "02.001" in cats:
        partes = [p.strip() for p in cats.replace(";", ",").split(",") if p.strip()]
        for p in partes:
            if p == "02.001" or (p.startswith("02.001.") and not p.startswith("02.001.0006")):
                return True

    # 2. Se temos repo, consulta categorias no banco
    if repo and geoentcod:
        try:
            lista_cats = repo.listar_categorias_entidade(geoentcod)
            for c in lista_cats:
                cod = str(c.get("codigo") or c.get("categcodestr") or "").strip()
                if cod == "02.001" or (cod.startswith("02.001.") and not cod.startswith("02.001.0006")):
                    return True
        except Exception:
            pass

    # 3. Checa na tabela USER_geoapolo_gruposdeoracao
    if repo and geoentcod:
        try:
            cur = repo._get_cursor()
            cur.execute(
                "SELECT 1 FROM USER_geoapolo_gruposdeoracao WITH (NOLOCK) WHERE codigoapolo = ? OR gocodigo = ?",
                (str(geoentcod), str(geoentcod))
            )
            if cur.fetchone():
                return True
        except Exception:
            pass

    # 4. Checa no nome da entidade
    nome = str(dados.get("geoentnome") or dados.get("entnome") or "").upper()
    if "GRUPO DE ORA" in nome or "G.O." in nome or "GRUPO DE ORAÇÃO" in nome:
        return True

    return False


def obter_proximo_documento_teste(tipo_fj: str) -> Tuple[str, Path]:
    """
    Retorna o próximo documento disponível da lista correspondente:
    - tipo_fj Jurídica -> cnpjs_teste_200.csv
    - tipo_fj Física/outro -> cpfs_teste_200.csv
    Retorna (documento_limpo, caminho_arquivo) sem remover ainda.
    """
    is_juridica = str(tipo_fj or "").upper() in ("J", "JURIDICA", "JURÍDICA", "CNPJ")
    nome_arquivo = "cnpjs_teste_200.csv" if is_juridica else "cpfs_teste_200.csv"
    caminho = obter_caminho_arquivo_teste(nome_arquivo)

    if not caminho or not caminho.is_file():
        raise FileNotFoundError(f"Arquivo de documentos de teste '{nome_arquivo}' não foi encontrado.")

    with open(caminho, "r", encoding="utf-8-sig") as f:
        linhas = [linha.strip() for linha in f if linha.strip()]

    # A primeira linha é o cabeçalho ("CPF" ou "CNPJ")
    documentos = [l for l in linhas[1:] if l and not l.startswith("#")]
    if not documentos:
        tipo_nome = "CNPJs" if is_juridica else "CPFs"
        raise RuntimeError(f"O arquivo '{nome_arquivo}' não possui mais {tipo_nome} disponíveis na lista.")

    proximo_doc = re.sub(r"\D", "", documentos[0])
    return proximo_doc, caminho


def consumir_documento_teste(caminho_arquivo: Path, documento: str) -> bool:
    """
    Remove a linha do documento utilizado do arquivo CSV correspondente e salva de forma segura.
    """
    if not caminho_arquivo or not caminho_arquivo.is_file():
        logger.warning(f"Arquivo de documentos de teste não encontrado para remoção: {caminho_arquivo}")
        return False

    doc_limpo = re.sub(r"\D", "", str(documento or ""))
    if not doc_limpo:
        return False

    try:
        with open(caminho_arquivo, "r", encoding="utf-8-sig") as f:
            linhas = [linha.strip() for linha in f if linha.strip()]

        if not linhas:
            return False

        cabecalho = linhas[0]
        novas_linhas = [cabecalho]
        removido = False

        for l in linhas[1:]:
            l_limpo = re.sub(r"\D", "", l)
            if not removido and l_limpo == doc_limpo:
                removido = True
                continue
            novas_linhas.append(l)

        if removido:
            conteudo = "\r\n".join(novas_linhas) + "\r\n"
            caminho_tmp = caminho_arquivo.with_suffix(".tmp")
            with open(caminho_tmp, "w", encoding="utf-8") as f_out:
                f_out.write(conteudo)
            caminho_tmp.replace(caminho_arquivo)
            logger.info(f"Documento de teste '{doc_limpo}' removido com sucesso de {caminho_arquivo.name}.")
            return True
        else:
            logger.warning(f"Documento de teste '{doc_limpo}' não encontrado em {caminho_arquivo.name} para remoção.")
            return False
    except Exception as exc:
        logger.error(f"Erro ao remover documento de teste de {caminho_arquivo}: {exc}")
        return False


def contar_documentos_restantes(tipo_fj: str) -> Tuple[int, Path, str]:
    """
    Retorna a quantidade de documentos restantes na lista CSV correspondente,
    o caminho do arquivo e a descrição do tipo ('CPFs' ou 'CNPJs').
    """
    is_juridica = str(tipo_fj or "").upper() in ("J", "JURIDICA", "JURÍDICA", "CNPJ")
    nome_arquivo = "cnpjs_teste_200.csv" if is_juridica else "cpfs_teste_200.csv"
    caminho = obter_caminho_arquivo_teste(nome_arquivo)
    tipo_desc = "CNPJs" if is_juridica else "CPFs"

    if not caminho or not caminho.is_file():
        return 0, Path(nome_arquivo), tipo_desc

    try:
        with open(caminho, "r", encoding="utf-8-sig") as f:
            linhas = [linha.strip() for linha in f if linha.strip()]
        docs = [l for l in linhas[1:] if l and not l.startswith("#")]
        return len(docs), caminho, tipo_desc
    except Exception as exc:
        logger.error(f"Erro ao contar documentos restantes em {caminho}: {exc}")
        return 0, caminho, tipo_desc


def verificar_alerta_poucos_documentos(tipo_fj: str, limite: int = 5) -> Optional[str]:
    """
    Verifica se a lista de documentos de teste possui limite ou menos registros restantes.
    Se estiver com <= limite, retorna uma mensagem de alerta formatada.
    Caso contrário, retorna None.
    """
    qtd, caminho, tipo_desc = contar_documentos_restantes(tipo_fj)
    if qtd <= limite:
        nome_arq = caminho.name if caminho else ("cnpjs_teste_200.csv" if "CNPJ" in tipo_desc else "cpfs_teste_200.csv")
        if qtd == 1:
            texto_qtd = "Resta apenas 1 registro disponível."
        else:
            texto_qtd = f"Restam apenas {qtd} registros disponíveis."
        return (
            f"Atenção: A lista de {tipo_desc} de teste ({nome_arq}) está quase no fim!\n\n"
            f"{texto_qtd}\n"
            f"Por favor, providencie a adição de novos {tipo_desc} no arquivo de teste."
        )
    return None

