"""
Gerenciamento centralizado de sessão corporativa e contexto multi-empresa.
GeoApolo V5
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def obter_empresa_ativa(padrao: str = "1.01") -> str:
    """
    Retorna o código da empresa ativa no momento, priorizando a empresa selecionada
    no login corporativo (sessao_usuario_atual).
    """
    # 1. Tenta obter da sessão do logon (selecionada no login)
    try:
        from logon import sessao_usuario_atual
        emp = sessao_usuario_atual.get("codigo_empresa") or sessao_usuario_atual.get("empcod")
        if emp and str(emp).strip():
            return str(emp).strip()
    except Exception:
        pass

    # 2. Tenta obter do contexto em memória do EmpresasService
    try:
        from empresas.service import EmpresasService
        emp_obj = EmpresasService.obter_empresa_ativa()
        if emp_obj and emp_obj.empcod:
            return emp_obj.empcod.strip()
    except Exception:
        pass

    return padrao


def obter_nome_empresa_ativa() -> str:
    """Retorna a razão social / nome da empresa ativa."""
    try:
        from logon import sessao_usuario_atual
        nome = sessao_usuario_atual.get("nome_empresa")
        if nome and str(nome).strip():
            return str(nome).strip()
    except Exception:
        pass

    try:
        from empresas.service import EmpresasService
        emp_obj = EmpresasService.obter_empresa_ativa()
        if emp_obj and emp_obj.empnome:
            return emp_obj.empnome.strip()
    except Exception:
        pass

    cod = obter_empresa_ativa()
    try:
        from entidades.database import obter_conexao_banco
        conn = obter_conexao_banco()
        cur = conn.cursor()
        cur.execute("SELECT empnome FROM USER_geoapolo_empresas WHERE empcod = ?", [cod])
        row = cur.fetchone()
        conn.close()
        if row and row[0]:
            return str(row[0]).strip()
    except Exception:
        pass

    return f"EMPRESA {cod}"


def definir_empresa_ativa(cod: str, nome: str = "") -> None:
    """Atualiza a empresa ativa tanto na sessão de logon quanto no EmpresasService."""
    cod_limpo = str(cod or "").strip()
    if not cod_limpo:
        return

    # Atualiza sessão
    try:
        from logon import sessao_usuario_atual
        sessao_usuario_atual["codigo_empresa"] = cod_limpo
        sessao_usuario_atual["empcod"] = cod_limpo
        if nome:
            sessao_usuario_atual["nome_empresa"] = str(nome).strip()
    except Exception:
        pass

    # Atualiza serviço de empresas
    try:
        from entidades.database import obter_conexao_banco
        from empresas.repository import EmpresasRepository
        from empresas.service import EmpresasService
        conn = obter_conexao_banco()
        svc = EmpresasService(EmpresasRepository(conn))
        svc.selecionar_empresa_ativa(cod_limpo)
        conn.close()
    except Exception:
        pass
