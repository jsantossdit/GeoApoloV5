"""
Módulo utilitário para registro de logs de erros diretamente no diretório do executável.
Garante que exceções de exportação e integração sejam persistidas em arquivo texto
ao lado do binário (.exe) e acessíveis ao usuário e suporte técnico.
"""

import os
import sys
import logging
import traceback
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


def obter_diretorio_executavel() -> str:
    """
    Retorna o diretório do executável em ambiente compilado (PyInstaller)
    ou a raiz do projeto em ambiente de desenvolvimento.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    # Se estiver em desenvolvimento, retorna a pasta raiz do projeto
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def salvar_log_erro_executavel(
    nome_arquivo: str = "exportacao_erro.log",
    titulo: str = "Erro de Operação",
    erro: Optional[Exception] = None,
    contexto: str = "",
) -> str:
    """
    Grava um erro formatado com data/hora e stack trace em arquivo de log
    na pasta do executável. Retorna o caminho absoluto do arquivo gravado.
    """
    pasta = obter_diretorio_executavel()
    caminho_arquivo = os.path.join(pasta, nome_arquivo)

    agora_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linhas = [
        f"\n{'=' * 75}",
        f"DATA/HORA: {agora_str}",
        f"MÓDULO / OPERAÇÃO: {titulo}",
    ]
    if contexto:
        linhas.append(f"CONTEXTO: {contexto}")
    if erro is not None:
        linhas.append(f"TIPO DO ERRO: {type(erro).__name__}")
        linhas.append(f"MENSAGEM: {erro}")
        linhas.append("STACK TRACE:")
        tb_str = "".join(traceback.format_exception(type(erro), erro, erro.__traceback__))
        linhas.append(tb_str.strip())
    linhas.append(f"{'=' * 75}\n")

    try:
        with open(caminho_arquivo, "a", encoding="utf-8") as f:
            f.write("\n".join(linhas))
        logger.error("Erro registrado no log do executável [%s]: %s", caminho_arquivo, erro)
    except Exception as ex_grava:
        logger.exception("Falha ao gravar arquivo de log no diretório do executável (%s): %s", caminho_arquivo, ex_grava)

    return caminho_arquivo
