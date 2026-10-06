"""
Serviço de Negócio para Integração SAVIC x GeoAlvo/Apolo.
Executa regras de conferência, apuração, normalização de dados cadastrais
e sincronização de Coordenadores e Grupos de Oração.
"""

import os
import sys
import re
import logging
from pathlib import Path
from datetime import date, datetime
from typing import Optional, List, Dict, Any, Callable

from savic.models import (
    SavicResumoStatusDTO,
    SavicFiltroDTO,
    SavicGrupoOracaoDTO,
    SavicCoordenadorDTO,
    ResultadoImportacaoSavicDTO,
)
from savic.repository import SavicRepository
from core import geoapolo_configcod
from core.validators import limpar_formatacao, formatar_cpf
from entidades.database import obter_conexao_banco

logger = logging.getLogger(__name__)


def eh_mandato_vencido(mandato_indeterminado: Any, data_fim: Any) -> bool:
    """
    Retorna True se o mandato do coordenador não for indeterminado e a data final for anterior à data atual.
    """
    if str(mandato_indeterminado or "").strip().lower() in ("sim", "s", "1", "true"):
        return False
    if not data_fim:
        return False
    dt_fim = None
    if isinstance(data_fim, datetime):
        dt_fim = data_fim.date()
    elif isinstance(data_fim, date):
        dt_fim = data_fim
    elif isinstance(data_fim, str):
        s = data_fim.strip()[:10]
        try:
            if "-" in s:
                dt_fim = datetime.strptime(s, "%Y-%m-%d").date()
            elif "/" in s:
                dt_fim = datetime.strptime(s, "%d/%m/%Y").date()
        except Exception:
            pass
    if dt_fim and dt_fim < date.today():
        return True
    return False


def aplicar_pendencia_mandato_vencido(obs_texto: str) -> str:
    """
    Insere na tag [PENDÊNCIAS] o aviso de que o mandato do coordenador está vencido.
    """
    aviso = "mandato do coordenador está vencido, checar na diocese"
    texto = (obs_texto or "").strip()
    if aviso.lower() in texto.lower():
        return texto
    if "[PENDÊNCIAS]" in texto:
        return texto.replace("[PENDÊNCIAS]", f"[PENDÊNCIAS]\n{aviso}")
    elif "[PENDENCIAS]" in texto:
        return texto.replace("[PENDENCIAS]", f"[PENDÊNCIAS]\n{aviso}")
    elif "[PEND" in texto.upper():
        idx = texto.upper().find("[PEND")
        fim_colchete = texto.find("]", idx)
        if fim_colchete != -1:
            tag = texto[idx:fim_colchete + 1]
            return texto.replace(tag, f"{tag}\n{aviso}")
        return f"[PENDÊNCIAS]\n{aviso}\n\n{texto}"
    else:
        if texto:
            return f"[PENDÊNCIAS]\n{aviso}\n\n{texto}"
        return f"[PENDÊNCIAS]\n{aviso}"


class SavicService:
    """Regras de negócio de apuração e importação da base SAVIC para o GeoAlvo."""

    def __init__(self, repository: Optional[SavicRepository] = None, conn_geo=None):
        self._repo = repository or SavicRepository(conn_geo=conn_geo)
        self._conn_geo = conn_geo

    def _get_geo_conn(self):
        if self._conn_geo is not None:
            return self._conn_geo
        return obter_conexao_banco()

    def obter_resumo_status(self) -> SavicResumoStatusDTO:
        """Obtém os 4 subtotais de Grupos de Oração no SAVIC."""
        return self._repo.obter_resumo_status()

    def contar_apurados(self, filtro: SavicFiltroDTO) -> int:
        """Calcula a quantidade de registros no SAVIC para o período informado."""
        return self._repo.contar_registros_apurados(filtro)

    def listar_grupos_ja_importados(self) -> List[Dict[str, Any]]:
        """Retorna grupos de oração cadastrados na base local do GeoAlvo."""
        return self._repo.listar_grupos_ja_importados()

    def listar_categorias_geoalvo(self) -> List[Dict[str, str]]:
        """Retorna categorias do GeoAlvo para pesquisa."""
        return self._repo.listar_categorias_geoalvo()

    def obter_nome_categoria(self, codigo: str) -> str:
        """Retorna nome da categoria pelo código."""
        return self._repo.obter_nome_categoria(codigo)

    # -------------------------------------------------------------
    # Normalizadores de Dados Cadastrais
    # -------------------------------------------------------------
    @staticmethod
    def normalizar_tipo_logradouro(endereco: str) -> str:
        """Extrai a sigla/tipo de logradouro do endereço (R., Av., etc.)."""
        if not endereco:
            return "R."
        e = endereco.strip().upper()
        if e.startswith("RUA ") or e.startswith("R.") or e.startswith("R "):
            return "R."
        elif e.startswith("AVENIDA ") or e.startswith("AV.") or e.startswith("AV "):
            return "Av."
        elif e.startswith("ALAMEDA ") or e.startswith("AL.") or e.startswith("AL "):
            return "Al."
        elif e.startswith("TRAVESSA ") or e.startswith("TV.") or e.startswith("TV "):
            return "Tv."
        elif e.startswith("PRAÇA ") or e.startswith("PRACA ") or e.startswith("PÇ."):
            return "Pç."
        elif e.startswith("RODOVIA ") or e.startswith("ROD."):
            return "Rod."
        return "R."

    @staticmethod
    def normalizar_tratamento(genero: str) -> str:
        """Retorna código de tratamento padrão baseado no gênero ('0001' Sr. / '0002' Sra.)."""
        g = str(genero or "M").strip().upper()
        if g.startswith("F"):
            return "0002"
        return "0001"

    def resolver_cidade_codigo(self, nome_cidade: str, ufsigla: str, conn_geo=None) -> str:
        """
        Localiza o código da cidade (geocidcod) na base GeoAlvo/Alvo.
        Possui equivalências históricas do SAVIC (Brasília, satélites, acentuação).
        Equivalente a retorna_cidade_estado do Delphi.
        """
        cidade = (nome_cidade or "").strip().upper()
        estado = (ufsigla or "").strip().upper()

        if not cidade:
            return "00000001"

        # Correções de nomes conhecidas do Delphi
        if cidade == "ALVORADA D OESTE":
            cidade = "ALVORADA DO OESTE"
        elif cidade == "PASSA-VINTE":
            cidade = "PASSA VINTE"
        elif cidade in ("ESTRUTURAL", "VICENTE PIRES", "ÁGUAS CLARAS", "AGUAS CLARAS",
                        "RIACHO FUNDO I", "RIACHO FUNDO II", "COLÔNIA AGRÍCOLA SAMAMBAIA",
                        "COLONIA AGRICOLA SAMAMBAIA", "ITAPUÃ", "ITAPUA", "NUCLEO BANDEIRANTES",
                        "NÚCLEO BANDEIRANTE", "NUCLEO BANDEIRANTE") and estado == "DF":
            cidade = "BRASILIA"
        elif cidade == "SANTA RITA DE IBITIPOCA":
            cidade = "SANTA RITA DO IBITIPOCA"
        elif cidade in ("ALTA FLORESTA DOESTE", "ALTA FLORESTA D OESTE"):
            cidade = "ALTA FLORESTA DO OESTE"
        elif cidade in ("MIRASSOL DOESTE", "MIRASSOL D OESTE") and estado == "MT":
            cidade = "MIRASSOL DO OESTE"
        elif cidade in ("DONA EUSÉBIA", "DONA EUSEBIA") and estado == "MG":
            cidade = "DONA EUZÉBIA"
        elif cidade == "CONQUISTA D OESTE" and estado == "MT":
            cidade = "CONQUISTA DO OESTE"
        elif cidade in ("PÉROLA D OESTE", "PEROLA D OESTE"):
            cidade = "PEROLA DO OESTE"
        elif cidade == "LAGOA DE ITAENGA" and estado == "PE":
            cidade = "LAGOA DO ITAENGA"
        elif cidade in ("JANUÁRIO CICCO", "JANUARIO CICCO") and estado == "RN":
            cidade = "BOA SAÚDE"
        elif cidade == "AUGUSTO SEVERO" and estado == "RN":
            cidade = "CAMPO GRANDE"

        conn = conn_geo or self._get_geo_conn()
        cur = conn.cursor()

        # 1. Busca em USER_geoapolo_cidades (exata com collation insensível a acento e caixa)
        sql1 = """
            SELECT TOP 1 geocidcod
            FROM USER_geoapolo_cidades WITH (NOLOCK)
            WHERE cidnomecomp COLLATE Latin1_General_CI_AI = ? COLLATE Latin1_General_CI_AI
              AND UPPER(ufsigla) = ?
        """
        try:
            cur.execute(sql1, [cidade, estado])
            row = cur.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
        except Exception:
            pass

        # 1.1 Busca em USER_geoapolo_cidades por prefixo LIKE com collation CI_AI
        sql1_like = """
            SELECT TOP 1 geocidcod
            FROM USER_geoapolo_cidades WITH (NOLOCK)
            WHERE cidnomecomp COLLATE Latin1_General_CI_AI LIKE (? + '%')
              AND UPPER(ufsigla) = ?
        """
        try:
            cur.execute(sql1_like, [cidade, estado])
            row = cur.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
        except Exception:
            pass

        # 2. Busca na tabela cidade do Alvo (exata com collation CI_AI)
        sql2 = """
            SELECT TOP 1 cidcod
            FROM cidade WITH (NOLOCK)
            WHERE cidnomecomp COLLATE Latin1_General_CI_AI = ? COLLATE Latin1_General_CI_AI
              AND UPPER(ufsigla) = ?
        """
        try:
            cur.execute(sql2, [cidade, estado])
            row = cur.fetchone()
            if row and row[0]:
                cidcod = str(row[0]).strip()
                # Insere em USER_geoapolo_cidades para agilizar futuras buscas
                try:
                    cur.execute(
                        "IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_cidades WHERE geocidcod = ?) "
                        "INSERT INTO USER_geoapolo_cidades (geocidcod, cidnomecomp, ufsigla) VALUES (?, ?, ?)",
                        [cidcod, cidcod, cidade, estado]
                    )
                    conn.commit()
                except Exception:
                    pass
                return cidcod
        except Exception:
            pass

        # 2.1 Busca na tabela cidade do Alvo por prefixo LIKE com collation CI_AI
        sql2_like = """
            SELECT TOP 1 cidcod
            FROM cidade WITH (NOLOCK)
            WHERE cidnomecomp COLLATE Latin1_General_CI_AI LIKE (? + '%')
              AND UPPER(ufsigla) = ?
        """
        try:
            cur.execute(sql2_like, [cidade, estado])
            row = cur.fetchone()
            if row and row[0]:
                cidcod = str(row[0]).strip()
                try:
                    cur.execute(
                        "IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_cidades WHERE geocidcod = ?) "
                        "INSERT INTO USER_geoapolo_cidades (geocidcod, cidnomecomp, ufsigla) VALUES (?, ?, ?)",
                        [cidcod, cidcod, cidade, estado]
                    )
                    conn.commit()
                except Exception:
                    pass
                return cidcod
        except Exception:
            pass

        return None

    # -------------------------------------------------------------
    # Fluxo Completo de Importação e Sincronização
    # -------------------------------------------------------------
    def importar_grupos_e_coordenadores(
        self,
        filtro: SavicFiltroDTO,
        empresa_codigo: str = "1.01",
        callback_progresso: Optional[Callable[[int, int, str], None]] = None,
        categoria_go: str = "02.001",
        categoria_coord: str = "02.001.0006",
    ) -> ResultadoImportacaoSavicDTO:
        """
        Executa a exportação do SAVIC e importação/sincronização no GeoAlvo (SQL Server):
        - Coordenadores com mandato indeterminado ou período vigente.
        - Busca CPF em USER_geoapolo_entidade_documentos.
        - Se existe: UPDATE em USER_geoapolo_entidade.
        - Se não existe: INSERT completo em USER_geoapolo_entidade + documentos + comunicação + webcontato.
        - Grava em USER_geoapolo_coordenadores_grupodeoracao (categoria 02.001.0006).
        - Grava em USER_geoapolo_gruposdeoracao (categoria padrão 02.001).
        """
        resultado = ResultadoImportacaoSavicDTO()
        lista_grupos = self._repo.buscar_grupos_para_importacao(filtro)
        resultado.total_registros_apurados = len(lista_grupos)

        if not lista_grupos:
            resultado.sucesso = True
            resultado.mensagem = "Nenhum registro apurado no SAVIC para o período e critérios informados."
            return resultado

        conn_geo = self._get_geo_conn()
        cur = conn_geo.cursor()
        hoje_str = date.today().strftime("%Y-%m-%d")

        total = len(lista_grupos)
        for idx, grupo in enumerate(lista_grupos, start=1):
            coord = grupo.coordenador
            cpf_raw = (coord.cpf_coordenador or "").strip()
            cpf_limpo = limpar_formatacao(cpf_raw)
            cpf_fmt = formatar_cpf(cpf_limpo) if len(cpf_limpo) == 11 else cpf_raw

            if callback_progresso:
                callback_progresso(idx, total, f"Processando G.O. {grupo.grupo_de_oracao} ({idx}/{total})...")

            geoentcod_existente = None
            if cpf_limpo:
                geoentcod_existente = self._repo.buscar_geoentcod_por_cpf(cpf_limpo)

            cidcod = self.resolver_cidade_codigo(coord.cidade or grupo.cidade, coord.estado or grupo.estado, conn_geo)
            tipo_lograd = self.normalizar_tipo_logradouro(coord.endereco_coordenador)
            tipo_trat = self.normalizar_tratamento(coord.genero_coord)
            genero_sigla = "F" if str(coord.genero_coord).upper().startswith("F") else "M"

            # ---------------------------------------------------------
            # 1. Entidade do Coordenador (UPDATE ou INSERT)
            # ---------------------------------------------------------
            try:
                if geoentcod_existente:
                    # Entidade já existe: UPDATE em USER_geoapolo_entidade
                    sql_upd = """
                        UPDATE USER_geoapolo_entidade SET
                            geoentnome = ?,
                            geoentender = ?,
                            geoenderno = ?,
                            geoentendercomp = ?,
                            geoentbair = ?,
                            geoentcep = ?,
                            geocidcod = ?,
                            cidcodapolo = ?,
                            geoentgenero = ?,
                            geotipofj = 'F',
                            geofalecido = 'N'
                        WHERE geoentcod = ?
                    """
                    cur.execute(sql_upd, [
                        coord.coordenador or "COORDENADOR SAVIC",
                        coord.endereco_coordenador,
                        coord.numero_casa_coord,
                        coord.compl_coord,
                        coord.bairro_coord,
                        limpar_formatacao(coord.cep_coord),
                        cidcod,
                        cidcod,
                        genero_sigla,
                        geoentcod_existente
                    ])
                    resultado.total_coordenadores_atualizados += 1
                    geoentcod_ativo = geoentcod_existente
                else:
                    # Entidade não existe: INSERT em USER_geoapolo_entidade
                    novo_geoentcod = geoapolo_configcod(empresa_codigo, "USER_geoapolo_entidade", "Sim", conn_geo)
                    geoentcod_ativo = novo_geoentcod

                    # Verifica se o CPF já existe na tabela entidade do Alvo para obter o entcod
                    entcod_alvo = ""
                    try:
                        cur.execute(
                            "SELECT TOP 1 entcod FROM entidade WITH (NOLOCK) WHERE entcpfcgc IN (?, ?, ?)",
                            [cpf_raw, cpf_limpo, cpf_fmt]
                        )
                        row_alvo = cur.fetchone()
                        if row_alvo and row_alvo[0]:
                            entcod_alvo = str(row_alvo[0]).strip()
                    except Exception:
                        pass

                    sql_ins_ent = """
                        INSERT INTO USER_geoapolo_entidade (
                            geoentcod, geotipotratcod, geoentnome, geoentnomefantasia, tipolograd,
                            geoentender, geoenderno, geoentendercomp, geoentbair, geoentdatacad,
                            geoentdesdedata, geoentcep, geocidcod, geoentcxapost, geoentgenero,
                            geotipofj, geofalecido, entcod, cidcodapolo
                        ) VALUES (
                            ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?,
                            'F', 'N', ?, ?
                        )
                    """
                    cur.execute(sql_ins_ent, [
                        novo_geoentcod,
                        tipo_trat,
                        coord.coordenador or "COORDENADOR SAVIC",
                        coord.coordenador or "COORDENADOR SAVIC",
                        tipo_lograd,
                        coord.endereco_coordenador,
                        coord.numero_casa_coord,
                        coord.compl_coord,
                        coord.bairro_coord,
                        hoje_str,
                        hoje_str,
                        limpar_formatacao(coord.cep_coord),
                        cidcod,
                        coord.caixa_postal,
                        genero_sigla,
                        entcod_alvo or None,
                        cidcod
                    ])

                    # Inserção do CPF em USER_geoapolo_entidade_documentos
                    if cpf_limpo or cpf_raw:
                        cur.execute(
                            "INSERT INTO USER_geoapolo_entidade_documentos (geoentcod, geotipodocumento, geonumerodocumento, geoobservacoes) VALUES (?, 'CPF/CNPJ', ?, 'SAVIC')",
                            [novo_geoentcod, cpf_raw or cpf_limpo]
                        )

                    # Inserção do RG em USER_geoapolo_entidade_documentos se informado
                    if coord.rgcoord:
                        cur.execute(
                            "INSERT INTO USER_geoapolo_entidade_documentos (geoentcod, geotipodocumento, geonumerodocumento, geoobservacoes) VALUES (?, 'RG/IE', ?, ?)",
                            [novo_geoentcod, coord.rgcoord, coord.rgcoordemissor]
                        )

                    # Telefones em USER_geoapolo_entidade_comunicacao
                    if coord.telefone_coord or coord.celular_coord1:
                        fone = coord.celular_coord1 or coord.telefone_coord
                        tipo_fone = "Celular" if coord.celular_coord1 else "Residencial"
                        try:
                            cur.execute(
                                "INSERT INTO USER_geoapolo_entidade_comunicacao (geoentcod, geotelefonetipo, geotelefonenumero) VALUES (?, ?, ?)",
                                [novo_geoentcod, tipo_fone, fone]
                            )
                        except Exception:
                            pass

                    # E-mail em USER_geoapolo_entidade_webcontato
                    if coord.email and "@" in coord.email:
                        try:
                            cur.execute(
                                "INSERT INTO USER_geoapolo_entidade_webcontato (geoentcod, email, flagemailprincipal) VALUES (?, ?, 'S')",
                                [novo_geoentcod, coord.email.strip()]
                            )
                        except Exception:
                            pass

                    resultado.total_coordenadores_inseridos += 1

                # Categoria do Coordenador
                cat_coord_str = (categoria_coord or "02.001.0006").strip()
                if geoentcod_ativo and cat_coord_str:
                    try:
                        cur.execute(
                            "IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_categoria WHERE geoentcod = ? AND geocategcodigo = ?) "
                            "INSERT INTO USER_geoapolo_entidade_categoria (geoentcod, geocategcodigo) VALUES (?, ?)",
                            [geoentcod_ativo, cat_coord_str, geoentcod_ativo, cat_coord_str]
                        )
                    except Exception:
                        pass
                    try:
                        cur.execute(
                            "IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entcateg WITH (NOLOCK) WHERE geoentcod = ? AND geocategcodestr = ?) "
                            "INSERT INTO USER_geoapolo_entcateg (geoentcod, geocategcodestr) VALUES (?, ?)",
                            [geoentcod_ativo, cat_coord_str, geoentcod_ativo, cat_coord_str]
                        )
                    except Exception:
                        pass
                    try:
                        cur.execute(
                            "IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entcateg WITH (NOLOCK) WHERE geoentcod = ? AND geocategcodestr = '08.009') "
                            "INSERT INTO USER_geoapolo_entcateg (geoentcod, geocategcodestr) VALUES (?, '08.009')",
                            [geoentcod_ativo, geoentcod_ativo]
                        )
                    except Exception:
                        pass

                # Vínculo da Origem '013.007' (SAVIC)
                if geoentcod_ativo:
                    try:
                        cur.execute("""
                            IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_origens_entidade WITH (NOLOCK) WHERE geoentcod = ?)
                                INSERT INTO USER_geoapolo_origens_entidade (geo_origcodestr, geoentcod) VALUES ('013.007', ?)
                            ELSE
                                UPDATE USER_geoapolo_origens_entidade SET geo_origcodestr = '013.007' WHERE geoentcod = ?
                        """, [geoentcod_ativo, geoentcod_ativo, geoentcod_ativo])
                        if entcod_alvo:
                            cur.execute(
                                "UPDATE entidade SET OrigCodEstr = '013.007' WHERE entcod = ? AND (OrigCodEstr IS NULL OR OrigCodEstr = '')",
                                [entcod_alvo]
                            )
                    except Exception:
                        pass

                # -----------------------------------------------------
                # 2. Coordenador de GO (USER_geoapolo_coordenadores_grupodeoracao)
                # -----------------------------------------------------
                cur.execute(
                    "SELECT TOP 1 cadastroid_coordenador FROM USER_geoapolo_coordenadores_grupodeoracao WITH (NOLOCK) WHERE cadastroid_coordenador = ? OR (cpfcoordenador = ? AND cpfcoordenador <> '')",
                    [coord.cadastroid_coord, cpf_raw or cpf_limpo]
                )
                row_coord = cur.fetchone()

                dt_ini_c = coord.dataini_coordenacao.strftime("%Y-%m-%d") if coord.dataini_coordenacao else None
                dt_fim_c = coord.datafim_coordenacao.strftime("%Y-%m-%d") if coord.datafim_coordenacao else None

                if row_coord:
                    # Update coordenador de GO
                    sql_upd_cgo = """
                        UPDATE USER_geoapolo_coordenadores_grupodeoracao SET
                            coordenador = ?,
                            generocoordenador = ?,
                            rgcoordenador = ?,
                            rgorgaoexpedidor = ?,
                            mandatoindeterminado = ?,
                            datainiciocoordenacao = ?,
                            datafimcoordenacao = ?,
                            endereco_coordenador = ?,
                            numero = ?,
                            complemento = ?,
                            bairrocoordenador = ?,
                            cepcoordenador = ?,
                            go_geocidcod = ?,
                            email = ?,
                            dioceseid = ?,
                            diocesecoordenador = ?
                        WHERE cadastroid_coordenador = ?
                    """
                    cur.execute(sql_upd_cgo, [
                        coord.coordenador,
                        genero_sigla,
                        coord.rgcoord,
                        coord.rgcoordemissor,
                        coord.mandato_indeterminado,
                        dt_ini_c,
                        dt_fim_c,
                        coord.endereco_coordenador,
                        coord.numero_casa_coord,
                        coord.compl_coord,
                        coord.bairro_coord,
                        limpar_formatacao(coord.cep_coord),
                        cidcod,
                        coord.email,
                        coord.diocese_id,
                        coord.diocese_coordenador,
                        coord.cadastroid_coord
                    ])
                else:
                    # Insert coordenador de GO (com categoria padrão 02.001.0006)
                    sql_ins_cgo = """
                        INSERT INTO USER_geoapolo_coordenadores_grupodeoracao (
                            cadastroid_coordenador, coordenador, generocoordenador, cpfcoordenador, rgcoordenador,
                            rgorgaoexpedidor, mandatoindeterminado, datainiciocoordenacao, datafimcoordenacao,
                            endereco_coordenador, numero, complemento, bairrocoordenador, cepcoordenador,
                            go_geocidcod, caixapostalcoordenador, telefonefixo_coordenador, telefonecomercial_coordenador,
                            celular_coordenador, celular2_coordenador, email, dioceseid, diocesecoordenador,
                            idultimoatualizador, ultimaalteracaofeitapor
                        ) VALUES (
                            ?, ?, ?, ?, ?,
                            ?, ?, ?, ?,
                            ?, ?, ?, ?, ?,
                            ?, ?, ?, ?,
                            ?, ?, ?, ?, ?,
                            ?, ?
                        )
                    """
                    cur.execute(sql_ins_cgo, [
                        coord.cadastroid_coord,
                        coord.coordenador,
                        genero_sigla,
                        cpf_raw or cpf_limpo,
                        coord.rgcoord,
                        coord.rgcoordemissor,
                        coord.mandato_indeterminado,
                        dt_ini_c,
                        dt_fim_c,
                        coord.endereco_coordenador,
                        coord.numero_casa_coord,
                        coord.compl_coord,
                        coord.bairro_coord,
                        limpar_formatacao(coord.cep_coord),
                        cidcod,
                        coord.caixa_postal,
                        coord.telefone_coord,
                        coord.tel_com_coord,
                        coord.celular_coord1,
                        coord.celular_coord2,
                        coord.email,
                        coord.diocese_id,
                        coord.diocese_coordenador,
                        coord.user_atualizacao,
                        coord.ultima_alteracao_feita_por
                    ])

                # -----------------------------------------------------
                # 3. Grupo de Oração (USER_geoapolo_gruposdeoracao)
                # -----------------------------------------------------
                cur.execute(
                    "SELECT TOP 1 gocodigo FROM USER_geoapolo_gruposdeoracao WITH (NOLOCK) WHERE gocodigo = ?",
                    [grupo.goid]
                )
                row_go = cur.fetchone()

                dt_inc_go = grupo.datainclusao_go.strftime("%Y-%m-%d") if grupo.datainclusao_go else None
                dt_at_go = grupo.dataatualizacao_go.strftime("%Y-%m-%d") if grupo.dataatualizacao_go else hoje_str

                if row_go:
                    sql_upd_go = """
                        UPDATE USER_geoapolo_gruposdeoracao SET
                            gonome_grupodeoracao = ?,
                            go_local_grupo = ?,
                            go_tipo_de_local = ?,
                            go_geocidcod = ?,
                            cadastroid_coordenador = ?,
                            dias_semana = ?,
                            horario = ?,
                            situacao_grupo = ?,
                            caracteristica_grupo = ?,
                            datatualizacao_go = ?
                        WHERE gocodigo = ?
                    """
                    cur.execute(sql_upd_go, [
                        grupo.grupo_de_oracao,
                        grupo.local_reuniao,
                        grupo.tipo_local_reuniao,
                        cidcod,
                        coord.cadastroid_coord,
                        grupo.dias_semana,
                        grupo.horario,
                        grupo.situacao,
                        grupo.caracteristica_grupo,
                        dt_at_go,
                        grupo.goid
                    ])
                    resultado.total_grupos_atualizados += 1
                else:
                    # Inclusão com categoria padrão 02.001
                    sql_ins_go = """
                        INSERT INTO USER_geoapolo_gruposdeoracao (
                            gocodigo, gonome_grupodeoracao, go_local_grupo, go_tipo_de_local,
                            go_geocidcod, cadastroid_coordenador, dias_semana, horario,
                            situacao_grupo, caracteristica_grupo, datainclusao_go, datatualizacao_go
                        ) VALUES (
                            ?, ?, ?, ?,
                            ?, ?, ?, ?,
                            ?, ?, ?, ?
                        )
                    """
                    cur.execute(sql_ins_go, [
                        grupo.goid,
                        grupo.grupo_de_oracao,
                        grupo.local_reuniao,
                        grupo.tipo_local_reuniao,
                        cidcod,
                        coord.cadastroid_coord,
                        grupo.dias_semana,
                        grupo.horario,
                        grupo.situacao,
                        grupo.caracteristica_grupo,
                        dt_inc_go,
                        dt_at_go
                    ])
                    resultado.total_grupos_inseridos += 1

                # -----------------------------------------------------
                # 4. Integração do Grupo de Oração no Cadastro de Entidades (USER_geoapolo_entidade)
                # -----------------------------------------------------
                goid_str = str(grupo.goid or "").strip()
                # geoentcod na tabela USER_geoapolo_entidade é VARCHAR(7)
                geoentcod_go = goid_str[:7]

                # Validação de cidade (Item 2.2)
                cidcod_validado = None
                nome_cid = (grupo.cidade or "").strip().upper()
                uf_cid = (grupo.estado or "").strip().upper()

                if cidcod and cidcod != "0" and "-" not in cidcod and cidcod != "00000001":
                    try:
                        cur.execute("SELECT TOP 1 geocidcod FROM USER_geoapolo_cidades WITH (NOLOCK) WHERE geocidcod = ?", [cidcod])
                        row_c = cur.fetchone()
                        if row_c and row_c[0]:
                            cidcod_validado = str(row_c[0]).strip()
                    except Exception:
                        pass

                if not cidcod_validado and nome_cid:
                    cidcod_validado = self.resolver_cidade_codigo(nome_cid, uf_cid, conn_geo)

                if not cidcod_validado:
                    # Inconsistência de cidade: não salva em entidades e registra motivo
                    motivo_inc = f"Cidade não encontrada em USER_geoapolo_cidades ou cidade ({nome_cid} - {uf_cid})"
                    cur.execute("UPDATE USER_geoapolo_gruposdeoracao SET flagexportado = 'Não' WHERE gocodigo = ?", [grupo.goid])
                    resultado.registros_apenas_grupos.append({
                        "goid": grupo.goid,
                        "nome": grupo.grupo_de_oracao,
                        "cidade": nome_cid,
                        "uf": uf_cid,
                        "motivo": motivo_inc,
                        "status": "Gravado apenas em USER_geoapolo_gruposdeoracao"
                    })
                else:
                    # Cidade validada: prossegue integração na USER_geoapolo_entidade
                    cur.execute(
                        "SELECT TOP 1 geoentcod, entcod, geoobservacoes FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE geoentcod = ?",
                        [geoentcod_go]
                    )
                    row_ent_go = cur.fetchone()
                    entidade_go_existe = (row_ent_go is not None)
                    obs_atual = str(row_ent_go[2] or "") if (row_ent_go and len(row_ent_go) > 2) else ""
                    entcod_go = str(row_ent_go[1] or "").strip() if (row_ent_go and len(row_ent_go) > 1 and row_ent_go[1]) else None

                    # Bloco [INFORMAÇÕES] preservando [PENDÊNCIAS]
                    dt_at_go_formatada = (
                        grupo.dataatualizacao_go.strftime("%d/%m/%Y")
                        if grupo.dataatualizacao_go
                        else date.today().strftime("%d/%m/%Y")
                    )
                    obs_info = f"[INFORMAÇÕES]\nDia da Semana: {grupo.dias_semana or ''}"
                    if grupo.horario:
                        obs_info += f" às {grupo.horario}"
                    obs_info += f"\nCaracteristicas do Grupo: {grupo.caracteristica_grupo or ''}\nÚltima Atualização do G.O.: {dt_at_go_formatada}"

                    pos_info = obs_atual.find("[INFORMAÇÕES]")
                    if pos_info == -1:
                        pos_info = obs_atual.find("[INFORMACOES]")

                    if pos_info != -1:
                        pendencias = obs_atual[:pos_info].strip()
                    else:
                        pendencias = obs_atual.strip()

                    coord_go = getattr(grupo, "coordenador", None) or coord
                    if coord_go and eh_mandato_vencido(
                        getattr(coord_go, "mandato_indeterminado", None),
                        getattr(coord_go, "datafim_coordenacao", None)
                    ):
                        pendencias = aplicar_pendencia_mandato_vencido(pendencias)

                    if pendencias:
                        obs_final = f"{pendencias}\n\n{obs_info}"
                    else:
                        obs_final = obs_info

                    # Ajuste rigoroso aos limites de colunas do SQL Server
                    nome_go = (grupo.grupo_de_oracao or "")[:100]
                    local_reuniao = (grupo.local_reuniao or grupo.grupo_de_oracao or "")[:60]
                    endereco_go = (grupo.local_reuniao or grupo.grupo_de_oracao or "S/N")[:100]
                    tipo_local = (grupo.tipo_local_reuniao or "")[:40]
                    situacao = (grupo.situacao or "")[:70]
                    obs_final_trunc = obs_final[:200]
                    entcod_go_sql = entcod_go[:7] if entcod_go else None
                    cid_validada_trunc = cidcod_validado[:10]
                    cid_apolo_trunc = cidcod_validado[:8]

                    if entidade_go_existe:
                        sql_upd_go_ent = """
                            UPDATE USER_geoapolo_entidade SET
                                geoentnome = ?,
                                geoentnomefantasia = ?,
                                tipolograd = ISNULL(NULLIF(tipolograd, 0), 1),
                                geotipotratcod = ISNULL(NULLIF(geotipotratcod, ''), '0001'),
                                geoentender = CASE WHEN ISNULL(NULLIF(?, ''), '') <> '' THEN ? ELSE ISNULL(geoentender, 'S/N') END,
                                geoenderno = ISNULL(NULLIF(geoenderno, ''), 'S/N'),
                                geolocalreferencia_ender = ?,
                                geoentendercomp = ?,
                                geoobservacoes = ?,
                                geocidcod = ?,
                                cidcodapolo = ?,
                                geotipofj = 'Jurídica',
                                geofalecido = 'N',
                                geoentloccobrancaomesmo = 'Sim',
                                geoentlocentregaomesmo = 'Sim',
                                geoenttransporteomesmo = 'Sim',
                                entcod = CASE WHEN ISNULL(entcod, '') = '' AND ? IS NOT NULL THEN ? ELSE entcod END
                            WHERE geoentcod = ?
                        """
                        cur.execute(sql_upd_go_ent, [
                            nome_go, local_reuniao, endereco_go, endereco_go,
                            tipo_local, situacao, obs_final_trunc,
                            cid_validada_trunc, cid_apolo_trunc,
                            entcod_go_sql, entcod_go_sql,
                            geoentcod_go
                        ])
                        resultado.total_entidades_go_atualizadas += 1
                        status_reg = "Atualizado em USER_geoapolo_entidade com sucesso"
                    else:
                        sql_ins_go_ent = """
                            INSERT INTO USER_geoapolo_entidade (
                                geoentcod, geotipotratcod, geoentnome, geoentnomefantasia, tipolograd,
                                geoentender, geoenderno, geolocalreferencia_ender, geoentendercomp, geoobservacoes,
                                geoentdatacad, geoentdesdedata, geocidcod, cidcodapolo, geoentgenero,
                                geotipofj, geofalecido, entcod,
                                geoentloccobrancaomesmo, geoentlocentregaomesmo, geoenttransporteomesmo
                            ) VALUES (
                                ?, '0001', ?, ?, 1,
                                ?, 'S/N', ?, ?, ?,
                                ?, ?, ?, ?, 'M',
                                'Jurídica', 'N', ?,
                                'Sim', 'Sim', 'Sim'
                            )
                        """
                        cur.execute(sql_ins_go_ent, [
                            geoentcod_go, nome_go, local_reuniao,
                            endereco_go, tipo_local, situacao, obs_final_trunc,
                            dt_inc_go or hoje_str, dt_inc_go or hoje_str,
                            cid_validada_trunc, cid_apolo_trunc, entcod_go_sql
                        ])
                        resultado.total_entidades_go_inseridas += 1
                        status_reg = "Inserido em USER_geoapolo_entidade com sucesso"

                    # Vínculo da Categoria na tabela oficial USER_geoapolo_entcateg
                    cat_go_str = (categoria_go or "02.001").strip()[:30]
                    try:
                        cur.execute(
                            "IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entcateg WITH (NOLOCK) WHERE geoentcod = ? AND geocategcodestr = ?) "
                            "INSERT INTO USER_geoapolo_entcateg (geoentcod, geocategcodestr) VALUES (?, ?)",
                            [geoentcod_go, cat_go_str, geoentcod_go, cat_go_str]
                        )
                    except Exception:
                        pass
                    try:
                        cur.execute(
                            "IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entcateg WITH (NOLOCK) WHERE geoentcod = ? AND geocategcodestr = '08.009') "
                            "INSERT INTO USER_geoapolo_entcateg (geoentcod, geocategcodestr) VALUES (?, '08.009')",
                            [geoentcod_go, geoentcod_go]
                        )
                    except Exception:
                        pass

                    # Vínculo com Atividade Econômica (se tabela existir)
                    try:
                        cur.execute(
                            "IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'USER_geoapolo_entidade_ativecon') "
                            "AND NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_ativecon WITH (NOLOCK) WHERE geoentcod = ?) "
                            "INSERT INTO USER_geoapolo_entidade_ativecon (ativeconcodestr, geoentcod) VALUES ('94.91-0', ?)",
                            [geoentcod_go, geoentcod_go]
                        )
                    except Exception:
                        pass

                    # Vínculo da Origem '013.007' (SAVIC)
                    try:
                        cur.execute("""
                            IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_origens_entidade WITH (NOLOCK) WHERE geoentcod = ?)
                                INSERT INTO USER_geoapolo_origens_entidade (geo_origcodestr, geoentcod) VALUES ('013.007', ?)
                            ELSE
                                UPDATE USER_geoapolo_origens_entidade SET geo_origcodestr = '013.007' WHERE geoentcod = ?
                        """, [geoentcod_go, geoentcod_go, geoentcod_go])
                        if entcod_go_sql:
                            cur.execute(
                                "UPDATE entidade SET OrigCodEstr = '013.007' WHERE entcod = ? AND (OrigCodEstr IS NULL OR OrigCodEstr = '')",
                                [entcod_go_sql]
                            )
                    except Exception:
                        pass

                    # Vínculo do Coordenador com Grupo em USER_geoapolo_entidade_contato (Item 2.3)
                    geoentcod_coord_contato = None
                    if cpf_limpo:
                        geoentcod_coord_contato = self._repo.buscar_geoentcod_por_cpf(cpf_limpo)
                    if not geoentcod_coord_contato and geoentcod_ativo:
                        geoentcod_coord_contato = geoentcod_ativo

                    if geoentcod_coord_contato:
                        tipo_trat_coord = "0001"
                        try:
                            cur.execute("SELECT TOP 1 geotipotratcod FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE geoentcod = ?", [geoentcod_coord_contato])
                            row_tc = cur.fetchone()
                            if row_tc and row_tc[0]:
                                tipo_trat_coord = str(row_tc[0]).strip() or "0001"
                        except Exception:
                            pass

                        try:
                            sql_contato = """
                                IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_contato WITH (NOLOCK) WHERE geoentcod = ? AND EntCodContato = ?)
                                INSERT INTO USER_geoapolo_entidade_contato (
                                    geoentcod, entCod, EntCodContato, TipoTratCod, CargoCodEstr, EntContatoCategPrinc,
                                    EntContatoEMail, EntContatoTelefone, EntContatoCelular, CidCod, data_vigencia_inicial, data_vigencia_final
                                ) VALUES (
                                    ?, ?, ?, ?, 'Coordenador', 'S',
                                    ?, ?, ?, ?, ?, ?
                                )
                                ELSE UPDATE USER_geoapolo_entidade_contato SET
                                    entCod = ?,
                                    TipoTratCod = ?, CargoCodEstr = 'Coordenador', EntContatoCategPrinc = 'S',
                                    EntContatoEMail = ?, EntContatoTelefone = ?, EntContatoCelular = ?,
                                    CidCod = ?, data_vigencia_inicial = ?, data_vigencia_final = ?
                                WHERE geoentcod = ? AND EntCodContato = ?
                            """
                            cur.execute(sql_contato, [
                                geoentcod_go, geoentcod_coord_contato,
                                geoentcod_go, entcod_go_sql, geoentcod_coord_contato, tipo_trat_coord[:6],
                                (coord.email or "")[:200], (coord.telefone_coord or "")[:31], (coord.celular_coord1 or "")[:31],
                                cid_validada_trunc, dt_ini_c, dt_fim_c,
                                entcod_go_sql, tipo_trat_coord[:6],
                                (coord.email or "")[:200], (coord.telefone_coord or "")[:31], (coord.celular_coord1 or "")[:31],
                                cid_validada_trunc, dt_ini_c, dt_fim_c,
                                geoentcod_go, geoentcod_coord_contato
                            ])
                        except Exception:
                            pass

                    # Marca o Grupo como exportado com sucesso
                    cur.execute(
                        "UPDATE USER_geoapolo_gruposdeoracao SET flagexportado = 'Sim', codigoapolo = ? WHERE gocodigo = ?",
                        [geoentcod_go[:7], grupo.goid]
                    )

                    resultado.registros_inseridos_entidades.append({
                        "goid": grupo.goid,
                        "nome": grupo.grupo_de_oracao,
                        "cidade": nome_cid,
                        "uf": uf_cid,
                        "geocidcod": cid_validada_trunc,
                        "geoentcod": geoentcod_go,
                        "status": status_reg
                    })

                conn_geo.commit()

            except Exception as exc:
                conn_geo.rollback()
                msg_err = f"Erro no G.O. {grupo.goid} ({grupo.grupo_de_oracao}): {exc}"
                logger.error(msg_err)
                resultado.erros.append(msg_err)
                resultado.registros_apenas_grupos.append({
                    "goid": grupo.goid,
                    "nome": grupo.grupo_de_oracao,
                    "cidade": (grupo.cidade or "").strip(),
                    "uf": (grupo.estado or "").strip(),
                    "motivo": f"Exceção ao gravar entidade: {exc}",
                    "status": "Não gravado em Entidades (Erro SQL/Execução)"
                })

        # -------------------------------------------------------------
        # 5. Geração do Arquivo de Ocorrências no Diretório do Executável
        # -------------------------------------------------------------
        if getattr(sys, "frozen", False):
            dir_exe = os.path.dirname(sys.executable)
        else:
            dir_exe = str(Path(__file__).resolve().parent.parent)

        caminho_ocorrencias = os.path.join(dir_exe, "ocorrencias_importacao_savic_alvo.txt")
        caminho_inconsistencias = os.path.join(dir_exe, "inconsistencias_integ_entidades.txt")
        dt_ini_fmt = filtro.data_inicial.strftime("%d/%m/%Y") if filtro.data_inicial else "Início"
        dt_fim_fmt = filtro.data_final.strftime("%d/%m/%Y") if filtro.data_final else "Fim"

        try:
            with open(caminho_ocorrencias, "w", encoding="utf-8") as f_out:
                f_out.write("=" * 100 + "\n")
                f_out.write("RELATÓRIO COMPLETO DE OCORRÊNCIAS DA INTEGRAÇÃO SAVIC x ALVO - GRUPOS DE ORAÇÃO\n")
                f_out.write(f"Data e Hora da Execução : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f_out.write(f"Período Apurado         : {dt_ini_fmt} a {dt_fim_fmt}\n")
                f_out.write(f"Total Registros Apurados: {resultado.total_registros_apurados}\n")
                f_out.write("=" * 100 + "\n\n")

                f_out.write(f"--- [1] REGISTROS INSERIDOS / ATUALIZADOS EM USER_GEOAPOLO_ENTIDADE (TOTAL: {len(resultado.registros_inseridos_entidades)}) ---\n")
                if resultado.registros_inseridos_entidades:
                    for idx_e, reg in enumerate(resultado.registros_inseridos_entidades, start=1):
                        f_out.write(
                            f"[{idx_e:04d}] GO ID: {reg['goid']} | Código Entidade (geoentcod): {reg['geoentcod']} | "
                            f"Nome: {reg['nome']} | Cidade/UF: {reg['cidade']} - {reg['uf']} (Cód: {reg.get('geocidcod', '')}) | "
                            f"Status: {reg['status']}\n"
                        )
                else:
                    f_out.write("Nenhum registro foi gravado na tabela USER_geoapolo_entidade.\n")

                f_out.write("\n" + "=" * 100 + "\n\n")

                f_out.write(f"--- [2] REGISTROS GRAVADOS APENAS EM USER_GEOAPOLO_GRUPOSDEORACAO (TOTAL: {len(resultado.registros_apenas_grupos)}) ---\n")
                if resultado.registros_apenas_grupos:
                    for idx_g, reg in enumerate(resultado.registros_apenas_grupos, start=1):
                        f_out.write(
                            f"[{idx_g:04d}] GO ID: {reg['goid']} | Nome: {reg['nome']} | "
                            f"Cidade/UF: {reg['cidade']} - {reg['uf']} | "
                            f"Motivo: {reg['motivo']} | Status: {reg['status']}\n"
                        )
                else:
                    f_out.write("Nenhum registro ficou restrito exclusivamente à tabela de grupos de oração.\n")

                f_out.write("\n" + "=" * 100 + "\n\n")

                f_out.write("--- [3] RESUMO GERAL E TOTALIZADORES ---\n")
                f_out.write(f"- Total de Registros Apurados no SAVIC: {resultado.total_registros_apurados}\n")
                f_out.write(f"- Grupos Inseridos em Grupos de Oração: {resultado.total_grupos_inseridos}\n")
                f_out.write(f"- Grupos Atualizados em Grupos de Oração: {resultado.total_grupos_atualizados}\n")
                f_out.write(f"- Entidades Inseridas em USER_geoapolo_entidade: {resultado.total_entidades_go_inseridas}\n")
                f_out.write(f"- Entidades Atualizadas em USER_geoapolo_entidade: {resultado.total_entidades_go_atualizadas}\n")
                f_out.write(f"- Registros Restritos a Grupos de Oração (Ocorrências): {len(resultado.registros_apenas_grupos)}\n")
                f_out.write(f"- Coordenadores Inseridos: {resultado.total_coordenadores_inseridos}\n")
                f_out.write(f"- Coordenadores Atualizados: {resultado.total_coordenadores_atualizados}\n")
                f_out.write(f"- Total de Erros / Exceções: {len(resultado.erros)}\n")
                f_out.write("=" * 100 + "\n")

            resultado.caminho_arquivo_ocorrencias = caminho_ocorrencias
        except Exception as exc_arq:
            logger.error(f"Erro ao gravar arquivo de ocorrências {caminho_ocorrencias}: {exc_arq}")

        # Mantém também arquivo legado inconsistencias_integ_entidades.txt atualizado na pasta do executável
        if resultado.registros_apenas_grupos:
            try:
                with open(caminho_inconsistencias, "a", encoding="utf-8") as f_inc:
                    agora_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    for reg_inc in resultado.registros_apenas_grupos:
                        f_inc.write(
                            f"{agora_str} | GOID: {reg_inc['goid']} | GO: {reg_inc['nome']} | "
                            f"Cidade: {reg_inc['cidade']} - {reg_inc['uf']} | Motivo: {reg_inc['motivo']}\n"
                        )
            except Exception:
                pass

        resultado.sucesso = (len(resultado.erros) == 0)
        resultado.mensagem = (
            f"Sincronização concluída com sucesso!\n"
            f"- Entidades alimentadas: {resultado.total_entidades_go_inseridas + resultado.total_entidades_go_atualizadas}\n"
            f"- Gravados apenas em Grupos de Oração: {len(resultado.registros_apenas_grupos)}\n"
            f"- Coordenadores integrados: {resultado.total_coordenadores_inseridos + resultado.total_coordenadores_atualizados}\n"
            f"- Relatório gerado em: {caminho_ocorrencias}"
        )
        return resultado

