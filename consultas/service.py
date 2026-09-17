"""
Serviço de lógica de negócio e montagem de SQL para Consultas Dinâmicas.
GeoApolo V5
"""

import re
from typing import List, Optional
from consultas.models import (
    ConsultaConfigDTO,
    PermissaoConsultaDTO,
    FiltroConsultaDTO,
    ResultadoConsultaDTO,
)
from consultas.repository import ConsultasRepository


class ConsultasService:
    """Orquestrador do motor de consultas dinâmicas e controle de acesso a relatórios."""

    def __init__(self, repository: ConsultasRepository):
        if not repository:
            raise ValueError("ConsultasRepository é obrigatório.")
        self._repo = repository

    def _sanitizar_identificador(self, nome: str, padrao: str) -> str:
        """Permite apenas nomes de colunas alfanuméricos para evitar SQL Injection."""
        if not nome or not nome.strip():
            return padrao
        limpo = nome.strip()
        if re.match(r"^[a-zA-Z0-9_.]+$", limpo):
            return limpo
        return padrao

    def montar_sql_consulta(self, filtro: FiltroConsultaDTO) -> tuple[str, list]:
        """Gera a consulta SQL parametrizada de acordo com o controle escolhido."""
        controle = (filtro.controle or "").upper().strip()
        ordem_dir = "ASC" if filtro.ordem_asc else "DESC"
        termo = f"%{filtro.texto_busca.strip()}%" if filtro.texto_busca else "%"
        nolock = self._repo._nolock()

        if controle == "CIDADE_CIDADE":
            campo_busca = self._sanitizar_identificador(filtro.campo_busca, "cidnomecomp")
            campo_ordem = self._sanitizar_identificador(filtro.campo_ordem, "cidnomecomp")
            sql = f"""
                SELECT geocidcod AS cidcod, cidnomecomp, ufsigla
                FROM user_geoapolo_cidades {nolock}
                WHERE {campo_busca} LIKE ?
                ORDER BY {campo_ordem} {ordem_dir}
            """
            return sql, [termo]

        elif controle == "CONTA_FINANCEIRASALDO":
            campo_busca = self._sanitizar_identificador(filtro.campo_busca, "contafinnome")
            campo_ordem = self._sanitizar_identificador(filtro.campo_ordem, "contafinnome")
            sql = f"""
                SELECT contafincod, contafinnome
                FROM USER_geoapolo_contasfinanceiras {nolock}
                WHERE {campo_busca} LIKE ?
                ORDER BY {campo_ordem} {ordem_dir}
            """
            return sql, [termo]

        elif controle == "USUARIO_DEPARTAMENTO":
            campo_busca = self._sanitizar_identificador(filtro.campo_busca, "nome_departamento")
            campo_ordem = self._sanitizar_identificador(filtro.campo_ordem, "nome_departamento")
            sql = f"""
                SELECT codigo_departamento, nome_departamento
                FROM USER_geoapolo_departamentos {nolock}
                WHERE {campo_busca} LIKE ?
                ORDER BY {campo_ordem} {ordem_dir}
            """
            return sql, [termo]

        elif controle == "CATEGORIA_ENTIDADE":
            campo_busca = self._sanitizar_identificador(filtro.campo_busca, "geocategnome")
            campo_ordem = self._sanitizar_identificador(filtro.campo_ordem, "geocategnome")
            sql = f"""
                SELECT geocategcodestr, geocategnome
                FROM USER_geoapolo_categoria {nolock}
                WHERE {campo_busca} LIKE ?
                ORDER BY {campo_ordem} {ordem_dir}
            """
            return sql, [termo]

        elif controle == "TIPOLOGRADOURO":
            campo_busca = self._sanitizar_identificador(filtro.campo_busca, "tipolograd")
            campo_ordem = self._sanitizar_identificador(filtro.campo_ordem, "tipolograd")
            sql = f"""
                SELECT tipolograd, tipologradabrev
                FROM USER_geoapolo_tipologradouro {nolock}
                WHERE {campo_busca} LIKE ?
                ORDER BY {campo_ordem} {ordem_dir}
            """
            return sql, [termo]

        else:
            # Padrão: CLIENTES / Entidades
            campo_busca = self._sanitizar_identificador(filtro.campo_busca, "geoentnome")
            campo_ordem = self._sanitizar_identificador(filtro.campo_ordem, "geoentnome")
            sql = f"""
                SELECT geoentcod, geoentnome, geocidcod
                FROM USER_geoapolo_entidade {nolock}
                WHERE {campo_busca} LIKE ?
                ORDER BY {campo_ordem} {ordem_dir}
            """
            return sql, [termo]

    def executar_busca(self, filtro: FiltroConsultaDTO) -> ResultadoConsultaDTO:
        """Monta o SQL e executa a busca parametrizada."""
        sql, params = self.montar_sql_consulta(filtro)
        return self._repo.executar_sql_dinamico(sql, params)

    def listar_consultas(self) -> List[ConsultaConfigDTO]:
        return self._repo.listar_consultas()

    def obter_consulta(self, codigo_consulta: str) -> Optional[ConsultaConfigDTO]:
        if not codigo_consulta or not codigo_consulta.strip():
            return None
        return self._repo.obter_consulta(codigo_consulta.strip())

    def salvar_consulta(self, c: ConsultaConfigDTO) -> bool:
        if not c.codigo_consulta or not c.codigo_consulta.strip():
            raise ValueError("Código da consulta é obrigatório.")
        if not c.descricao_consulta or not c.descricao_consulta.strip():
            raise ValueError("Descrição da consulta é obrigatória.")
        if not c.sql_consulta or not c.sql_consulta.strip():
            raise ValueError("Instrução SQL da consulta é obrigatória.")

        c.codigo_consulta = c.codigo_consulta.strip().upper()
        c.descricao_consulta = c.descricao_consulta.strip()
        c.sql_consulta = c.sql_consulta.strip()
        return self._repo.salvar_consulta(c)

    def excluir_consulta(self, codigo_consulta: str) -> bool:
        if not codigo_consulta or not codigo_consulta.strip():
            raise ValueError("Código da consulta é obrigatório.")
        return self._repo.excluir_consulta(codigo_consulta.strip().upper())

    def listar_permissoes_consulta(self, codigo_consulta: str) -> List[PermissaoConsultaDTO]:
        if not codigo_consulta or not codigo_consulta.strip():
            return []
        return self._repo.listar_permissoes_consulta(codigo_consulta.strip().upper())

    def atualizar_permissao(self, usucod: str, codigo_consulta: str, autorizada: bool) -> bool:
        if not usucod or not codigo_consulta:
            return False
        status = "S" if autorizada else "N"
        return self._repo.atualizar_permissao_consulta(usucod.strip().upper(), codigo_consulta.strip().upper(), status)
