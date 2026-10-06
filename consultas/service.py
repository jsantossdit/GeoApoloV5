"""
Serviço de lógica de negócio e montagem de SQL para Consultas Dinâmicas.
GeoApolo V5
Equivalente a ConsultaService.pas e unt_imediatas_service.pas do Delphi.
"""

import re
from typing import List, Optional, Tuple, Any
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

    def listar_consultas(self, tipo_consulta: Optional[str] = None, banco_consulta: Optional[str] = None) -> List[ConsultaConfigDTO]:
        return self._repo.listar_consultas(tipo_consulta=tipo_consulta, banco_consulta=banco_consulta)

    def listar_consultas_imediatas(self, usuario: str = "", banco: str = "") -> List[ConsultaConfigDTO]:
        return self._repo.listar_consultas_imediatas(usuario=usuario, banco=banco)

    def obter_consulta(self, codigo_consulta: str) -> Optional[ConsultaConfigDTO]:
        if not codigo_consulta or not str(codigo_consulta).strip():
            return None
        return self._repo.obter_consulta(str(codigo_consulta).strip())

    def obter_consulta_por_descricao(self, descricao: str) -> Optional[ConsultaConfigDTO]:
        if not descricao or not str(descricao).strip():
            return None
        return self._repo.obter_consulta_por_descricao(str(descricao).strip())

    def obter_proximo_codigo(self) -> str:
        return self._repo.obter_proximo_codigo()

    def salvar_consulta(self, c: ConsultaConfigDTO) -> bool:
        if not c.codigo_consulta or not str(c.codigo_consulta).strip():
            raise ValueError("Código da consulta é obrigatório.")
        if not c.descricao_consulta or not c.descricao_consulta.strip():
            raise ValueError("Descrição da consulta é obrigatória.")
        if not c.sql_consulta or not c.sql_consulta.strip():
            raise ValueError("Instrução SQL da consulta é obrigatória.")

        c.codigo_consulta = str(c.codigo_consulta).strip().upper()
        c.descricao_consulta = c.descricao_consulta.strip()
        c.sql_consulta = c.sql_consulta.strip()
        return self._repo.salvar_consulta(c)

    def excluir_consulta(self, codigo_consulta: str) -> bool:
        if not codigo_consulta or not str(codigo_consulta).strip():
            raise ValueError("Código da consulta é obrigatório.")
        return self._repo.excluir_consulta(str(codigo_consulta).strip().upper())

    def listar_permissoes_consulta(self, codigo_consulta: str) -> List[PermissaoConsultaDTO]:
        if not codigo_consulta or not str(codigo_consulta).strip():
            return []
        return self._repo.listar_permissoes_consulta(str(codigo_consulta).strip().upper())

    def atualizar_permissao(self, usucod: str, codigo_consulta: str, autorizada: bool) -> bool:
        if not usucod or not codigo_consulta:
            return False
        status = "A" if autorizada else "N"
        return self._repo.atualizar_permissao_consulta(usucod.strip().upper(), str(codigo_consulta).strip().upper(), status)

    def remover_permissao(self, usucod: str, codigo_consulta: str) -> bool:
        if not usucod or not codigo_consulta:
            return False
        return self._repo.remover_permissao_consulta(usucod.strip().upper(), str(codigo_consulta).strip().upper())

    def listar_grupos(self) -> List[Tuple[str, str]]:
        """Retorna lista de grupos (codigo_grupo, descricao)."""
        return self._repo.listar_grupos_usuarios()

    def listar_usuarios(self, grupo: Optional[str] = None) -> List[Tuple[str, str]]:
        """Retorna lista de usuários ativos, opcionalmente filtrados por grupo."""
        return self._repo.listar_usuarios_por_grupo(grupo=grupo)

    def listar_usuarios_sistema(self) -> List[Tuple[str, str]]:
        return self._repo.listar_usuarios_sistema()

    def aplicar_permissao(
        self,
        codigo_consulta: str,
        autorizada: bool,
        usucod: Optional[str] = None,
        grupo: Optional[str] = None,
    ) -> tuple[bool, str]:
        """
        Aplica permissão para um usuário específico ou para todos os usuários do grupo selecionado.
        Equivalente a spbaplicapermissaoClick do Delphi.
        """
        if not codigo_consulta or not str(codigo_consulta).strip():
            return False, "Selecione uma consulta para aplicar a permissão."
        if not (usucod and usucod.strip()) and not (grupo and grupo.strip() and grupo.upper() != "TODOS"):
            return False, "É obrigatório escolher um grupo ou um usuário para aplicar a permissão."

        status = "A" if autorizada else "N"
        qtd = self._repo.aplicar_permissao_grupo_ou_usuario(
            codigo_consulta=str(codigo_consulta).strip().upper(),
            autorizacao=status,
            usucod=usucod.strip().upper() if usucod else None,
            grupo=grupo.strip() if grupo else None,
        )
        if qtd > 0:
            msg = f"Permissão aplicada com sucesso para {qtd} usuário(s)."
            return True, msg
        return False, "Nenhum usuário encontrado para atualizar permissão."

    def clonar_permissoes(self, usucod_origem: str, usucod_destino: str) -> tuple[bool, str]:
        """Clona todas as permissões de consultas do usuário de origem para o usuário de destino."""
        if not usucod_origem or not usucod_destino:
            return False, "Selecione o usuário de origem e o usuário de destino."
        if usucod_origem.strip().upper() == usucod_destino.strip().upper():
            return False, "Usuário de origem e destino devem ser diferentes."

        qtd = self._repo.clonar_permissoes_consulta(
            usucod_origem.strip().upper(),
            usucod_destino.strip().upper(),
        )
        return True, f"Clonagem concluída! {qtd} permissão(ões) copiada(s) de {usucod_origem} para {usucod_destino}."

    def validar_seguranca_sql_leitura(self, sql: str) -> tuple[bool, str]:
        """
        Valida que a consulta não contenha instruções destrutivas.
        Conforme especificação: somente DELETE e UPDATE são considerados destrutivos e proibidos;
        as demais instruções (SELECT, WITH, DECLARE, INSERT, CREATE, DROP temporárias, EXEC, etc.) são liberadas.
        """
        if not sql or not sql.strip():
            return False, "A sentença SQL não pode ser vazia."

        sql_upper = sql.upper()

        comandos_proibidos = [
            (r"\bDELETE\b", "DELETE"),
            (r"\bUPDATE\b", "UPDATE"),
        ]
        for padrao, nome in comandos_proibidos:
            if re.search(padrao, sql_upper):
                return False, f"Instrução destrutiva proibida detectada na consulta: {nome}"

        return True, ""

    def analisar_e_substituir_parametros(self, sql: str, callback_input=None) -> tuple[str, bool]:
        """
        Analisa e substitui parâmetros da consulta conforme as regras do Delphi (unt_imediatas):
        - |parametro^ ou |parametro: Parâmetro variável numérico ou texto.
        - {data}: Parâmetro de data formatado como YYYY-MM-DD.
        - [fixo]: Parâmetro fixo.
        - &? ou &: Substituído por aspas vazias.
        Retorna (sql_processado, sucesso). Se o usuário cancelar algum input, retorna ("", False).
        """
        if not sql:
            return "", True

        sql_proc = sql

        # 1. Parâmetros de data {Nome_Data}
        padrao_data = re.compile(r"\{([^}]+)\}")
        while True:
            m = padrao_data.search(sql_proc)
            if not m:
                break
            tag = m.group(0)
            nome_param = m.group(1).strip()
            if callback_input:
                val = callback_input(nome_param, "data")
                if val is None:
                    return "", False
            else:
                val = "1900-01-01"

            # Formata data para yyyy-MM-dd se vier em DD/MM/AAAA
            val_limpo = str(val).strip()
            if "/" in val_limpo:
                partes = val_limpo.split("/")
                if len(partes) == 3:
                    d, m_mes, a = partes
                    val_limpo = f"{a.zfill(4)}-{m_mes.zfill(2)}-{d.zfill(2)}"

            val_quoted = f"'{val_limpo}'"
            sql_proc = sql_proc.replace(tag, val_quoted, 1)

        # 2. Parâmetros variáveis |Parametro^ ou |Parametro|
        padrao_var = re.compile(r"\|([^|^\r\n]+)[\^|]?")
        while True:
            m = padrao_var.search(sql_proc)
            if not m:
                break
            tag = m.group(0)
            nome_param = m.group(1).strip()
            if not nome_param:
                nome_param = "Parametro"
            if callback_input:
                val = callback_input(nome_param, "texto")
                if val is None:
                    return "", False
            else:
                val = ""
            val_quoted = f"'{str(val).strip()}'"
            sql_proc = sql_proc.replace(tag, val_quoted, 1)

        # 3. Parâmetros fixos [Valor]
        padrao_fixo = re.compile(r"\[([^\]\r\n]+)\]")
        while True:
            m = padrao_fixo.search(sql_proc)
            if not m:
                break
            tag = m.group(0)
            conteudo = m.group(1).strip()
            sql_proc = sql_proc.replace(tag, f"'{conteudo}' ", 1)

        # 4. Substituição de &? por ''
        sql_proc = sql_proc.replace("&?", "''")

        return sql_proc, True

    def executar_consulta_imediata(self, sql: str, banco: str = "") -> ResultadoConsultaDTO:
        """Executa instrução de consulta imediata sem parâmetros adicionais, roteando para o banco especificado."""
        return self._repo.executar_sql_dinamico(sql, banco=banco)

    def exportar_resultado_csv(
        self,
        resultado: ResultadoConsultaDTO,
        caminho_arquivo: str,
        delimitador: str = ";"
    ) -> int:
        """Exporta o resultado da consulta para arquivo CSV UTF-8 de forma desacoplada."""
        import csv

        if not resultado or not resultado.sucesso:
            raise ValueError("Resultado da consulta inválido para exportação.")

        total_linhas = 0
        with open(caminho_arquivo, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=delimitador, quoting=csv.QUOTE_MINIMAL)
            if resultado.colunas:
                writer.writerow(resultado.colunas)
            for linha in resultado.linhas:
                writer.writerow(linha)
                total_linhas += 1

        return total_linhas

    def exportar_resultado_excel(self, resultado: ResultadoConsultaDTO, caminho_arquivo: str) -> int:
        """Exporta o resultado da consulta para XLSX (via openpyxl se disponível) ou CSV."""
        if not resultado or not resultado.sucesso:
            raise ValueError("Resultado da consulta inválido para exportação.")

        if caminho_arquivo.lower().endswith(".xlsx"):
            try:
                import openpyxl
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Consultas Imediatas"
                if resultado.colunas:
                    ws.append(resultado.colunas)
                for linha in resultado.linhas:
                    ws.append([str(c) if c is not None else "" for c in linha])
                wb.save(caminho_arquivo)
                return len(resultado.linhas)
            except ImportError:
                caminho_csv = caminho_arquivo.rsplit(".", 1)[0] + ".csv"
                return self.exportar_resultado_csv(resultado, caminho_csv)
        else:
            return self.exportar_resultado_csv(resultado, caminho_arquivo)
