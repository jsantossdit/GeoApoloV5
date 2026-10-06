"""
Repositório de Dados para o Módulo de Moderação de Grupos de Oração SAVIC x Apolo.
Executa consultas no SQL Server (GeoAlvo/Apolo) para estados, dioceses, cidades, coordenadores,
grupos de oração, ficha financeira, comparação e exportação para a tabela de Entidades.
"""

import logging
import unicodedata
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any

from savic.moderacao_models import (
    EstadoDTO,
    DioceseDTO,
    CidadeDioceseDTO,
    CoordenadorModeracaoDTO,
    GrupoOracaoModeracaoDTO,
    FichaFinanceiraDTO,
    EntidadeApoloComparativoDTO,
)
from core import geoapolo_configcod, limpar_formatacao, formatar_cpf
from entidades.database import obter_conexao_banco

logger = logging.getLogger(__name__)


def remover_acentos(texto: str) -> str:
    """Remove acentuações e caracteres diacríticos mantendo letras maiúsculas."""
    if not texto:
        return ""
    texto_norm = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto_norm if not unicodedata.combining(c)).upper().strip()


class SavicModeracaoRepository:
    """Acesso a dados no SQL Server para a tela de Moderação de Grupos de Oração."""

    def __init__(self, conn=None):
        self._conn = conn

    def _get_conn(self):
        if self._conn is not None:
            return self._conn
        return obter_conexao_banco()

    # -------------------------------------------------------------------------
    # Migração / Garantia de Estrutura de Banco de Dados
    # -------------------------------------------------------------------------
    def assegurar_colunas_exportado(self):
        """
        Cria idempotentemente a coluna flagexportado nas tabelas
        USER_geoapolo_coordenadores_grupodeoracao e USER_geoapolo_gruposdeoracao.
        """
        conn = self._get_conn()
        cur = conn.cursor()
        ddl = """
            IF NOT EXISTS (
                SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'USER_geoapolo_coordenadores_grupodeoracao' AND COLUMN_NAME = 'flagexportado'
            )
            BEGIN
                ALTER TABLE USER_geoapolo_coordenadores_grupodeoracao
                ADD flagexportado VARCHAR(3) NULL CONSTRAINT DF_ugcg_flagexportado DEFAULT 'Não' WITH VALUES;
            END;

            IF NOT EXISTS (
                SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'USER_geoapolo_gruposdeoracao' AND COLUMN_NAME = 'flagexportado'
            )
            BEGIN
                ALTER TABLE USER_geoapolo_gruposdeoracao
                ADD flagexportado VARCHAR(3) NULL CONSTRAINT DF_uggo_flagexportado DEFAULT 'Não' WITH VALUES;
            END;
        """
        try:
            cur.execute(ddl)
            conn.commit()
        except Exception as exc:
            logger.error(f"Erro ao assegurar colunas flagexportado: {exc}")

    # -------------------------------------------------------------------------
    # Filtros e Localidades (CNBB)
    # -------------------------------------------------------------------------
    def listar_estados(self) -> List[EstadoDTO]:
        """Retorna todos os estados da tabela userestado_cnbb ordenados pela sigla."""
        conn = self._get_conn()
        cur = conn.cursor()
        sql = """
            SELECT USERiD, USERsigla, USERnome_estado
            FROM userestado_cnbb WITH (NOLOCK)
            ORDER BY USERsigla ASC
        """
        resultado = []
        try:
            cur.execute(sql)
            for row in cur.fetchall():
                resultado.append(EstadoDTO(
                    id=int(row[0] or 0),
                    sigla=str(row[1] or "").strip(),
                    nome=str(row[2] or "").strip()
                ))
        except Exception as exc:
            logger.error(f"Erro ao listar estados CNBB: {exc}")
        return resultado

    def listar_dioceses_por_estado(self, uf: Optional[str] = None) -> List[DioceseDTO]:
        """Retorna dioceses ativas de determinado estado (ou todas se UF for None/vazio)."""
        conn = self._get_conn()
        cur = conn.cursor()
        if uf and uf.strip():
            sql = """
                SELECT d.id, d.estado_id, d.nome, d.ativo
                FROM userdioceses_cnbb d WITH (NOLOCK)
                INNER JOIN userestado_cnbb e WITH (NOLOCK) ON d.estado_id = e.USERiD
                WHERE UPPER(e.USERsigla) = UPPER(?) AND d.ativo = 1
                ORDER BY d.nome ASC
            """
            params = [uf.strip().upper()]
        else:
            sql = """
                SELECT d.id, d.estado_id, d.nome, d.ativo
                FROM userdioceses_cnbb d WITH (NOLOCK)
                WHERE d.ativo = 1
                ORDER BY d.nome ASC
            """
            params = []

        resultado = []
        try:
            cur.execute(sql, params)
            for row in cur.fetchall():
                resultado.append(DioceseDTO(
                    id=int(row[0] or 0),
                    estado_id=int(row[1] or 0),
                    nome=str(row[2] or "").strip(),
                    ativo=int(row[3] or 1)
                ))
        except Exception as exc:
            logger.error(f"Erro ao listar dioceses: {exc}")
        return resultado

    def listar_cidades_por_diocese(self, diocese_nome_ou_id: Optional[str] = None) -> List[CidadeDioceseDTO]:
        """Retorna as cidades vinculadas a uma diocese (por ID ou nome, ou todas se vazio)."""
        conn = self._get_conn()
        cur = conn.cursor()
        if not diocese_nome_ou_id or not str(diocese_nome_ou_id).strip():
            sql = """
                SELECT TOP 500 c.id, c.estado_id, c.descricao, c.ibge, c.diocese_id
                FROM usercidades_cnbb c WITH (NOLOCK)
                ORDER BY c.descricao ASC
            """
            params = []
        elif str(diocese_nome_ou_id).strip().isdigit():
            sql = """
                SELECT c.id, c.estado_id, c.descricao, c.ibge, c.diocese_id
                FROM usercidades_cnbb c WITH (NOLOCK)
                WHERE c.diocese_id = ?
                ORDER BY c.descricao ASC
            """
            params = [int(diocese_nome_ou_id.strip())]
        else:
            sql = """
                SELECT c.id, c.estado_id, c.descricao, c.ibge, c.diocese_id
                FROM usercidades_cnbb c WITH (NOLOCK)
                INNER JOIN userdioceses_cnbb d WITH (NOLOCK) ON c.diocese_id = d.id
                WHERE UPPER(d.nome) = UPPER(?)
                ORDER BY c.descricao ASC
            """
            params = [str(diocese_nome_ou_id).strip()]

        resultado = []
        try:
            cur.execute(sql, params)
            for row in cur.fetchall():
                resultado.append(CidadeDioceseDTO(
                    id=int(row[0] or 0),
                    estado_id=int(row[1] or 0),
                    descricao=str(row[2] or "").strip(),
                    ibge=int(row[3]) if row[3] is not None else None,
                    diocese_id=int(row[4] or 0)
                ))
        except Exception as exc:
            logger.error(f"Erro ao listar cidades: {exc}")
        return resultado

    # -------------------------------------------------------------------------
    # Resolução de Cidade (Equivalente a retorna_cidade_estado do Delphi)
    # -------------------------------------------------------------------------
    def buscar_geocidcod(self, cidade: str, uf: str) -> Optional[str]:
        """
        Localiza o código da cidade (geocidcod) na tabela USER_geoapolo_cidades.
        Aplica correções conhecidas de nomes e, se necessário, sincroniza a partir
        da tabela principal 'cidade'.
        """
        if not cidade or not uf:
            return None

        nome = remover_acentos(cidade)
        sigla = uf.strip().upper()

        de_para = {
            "ALVORADA D OESTE": "ALVORADA DO OESTE",
            "PASSA-VINTE": "PASSA VINTE",
            "SANTA RITA DE IBITIPOCA": "SANTA RITA DO IBITIPOCA",
            "LAGOA DE ITAENGA": "LAGOA DO ITAENGA",
        }
        if nome in de_para:
            nome = de_para[nome]

        if sigla == "DF" and nome in ("ESTRUTURAL", "NUCLEO BANDEIRANTES", "VICENTE PIRES", "ITAPUA"):
            nome = "BRASILIA"
        elif sigla == "RN" and nome == "JANUARIO CICCO":
            nome = "BOA SAUDE"
        elif sigla == "RN" and nome == "AUGUSTO SEVERO":
            nome = "CAMPO GRANDE"

        conn = self._get_conn()
        cur = conn.cursor()

        # 1. Busca em USER_geoapolo_cidades
        sql1 = """
            SELECT geocidcod
            FROM USER_geoapolo_cidades WITH (NOLOCK)
            WHERE ufsigla = ?
              AND (
                dbo.TiraAcento(cidnomecomp) = ?
                OR UPPER(cidnomecomp) = ?
                OR dbo.TiraAcento(cidnomecomp) LIKE ?
              )
        """
        try:
            cur.execute(sql1, [sigla, nome, nome, f"{nome}%"])
            row = cur.fetchone()
            if row and row[0]:
                geocidcod = str(row[0]).strip()
                if geocidcod != "00000064":
                    return geocidcod
        except Exception:
            try:
                cur.execute(
                    "SELECT geocidcod FROM USER_geoapolo_cidades WITH (NOLOCK) WHERE ufsigla = ? AND UPPER(cidnomecomp) LIKE ?",
                    [sigla, f"{nome}%"]
                )
                row = cur.fetchone()
                if row and row[0]:
                    return str(row[0]).strip()
            except Exception as e2:
                logger.error(f"Erro na busca direta em USER_geoapolo_cidades: {e2}")

        # 2. Busca na tabela cidade do Apolo
        sql2 = """
            SELECT cidcod, cidnomecomp
            FROM cidade WITH (NOLOCK)
            WHERE ufsigla = ? AND UPPER(cidnomecomp) LIKE ?
        """
        try:
            cur.execute(sql2, [sigla, f"{nome}%"])
            row = cur.fetchone()
            if row and row[0]:
                cidcod = str(row[0]).strip()
                cidnome = str(row[1] or nome).strip()
                try:
                    cur.execute(
                        "INSERT INTO USER_geoapolo_cidades (geocidcod, cidnomecomp, ufsigla) VALUES (?, ?, ?)",
                        [cidcod, cidnome, sigla]
                    )
                    conn.commit()
                except Exception:
                    pass
                return cidcod
        except Exception as exc:
            logger.error(f"Erro ao buscar cidade no Apolo: {exc}")

        return None

    # -------------------------------------------------------------------------
    # Coordenadores e Grupos de Oração (Filtros Flexíveis)
    # -------------------------------------------------------------------------
    def listar_coordenadores(
        self,
        geocidcod: Optional[str] = None,
        uf: Optional[str] = None,
        diocese_nome_ou_id: Optional[str] = None,
        situacao_grupo: str = "HOMOLOGADO"
    ) -> List[CoordenadorModeracaoDTO]:
        """
        Lista coordenadores com base nos filtros informados.
        Permite que qualquer combinação de filtros (UF, Diocese, Cidade) fique em branco.
        Traz a coluna flagexportado ('Sim'/'Não').
        """
        self.assegurar_colunas_exportado()

        conn = self._get_conn()
        cur = conn.cursor()

        where_clauses = ["1=1"]
        params: List[Any] = []

        if geocidcod and str(geocidcod).strip():
            where_clauses.append("ugcg.go_geocidcod = ?")
            params.append(str(geocidcod).strip())
        elif uf and str(uf).strip():
            where_clauses.append("UPPER(ugc1.ufsigla) = ?")
            params.append(str(uf).strip().upper())

        if diocese_nome_ou_id and str(diocese_nome_ou_id).strip():
            d_val = str(diocese_nome_ou_id).strip()
            if d_val.isdigit():
                where_clauses.append("ugcg.dioceseid = ?")
                params.append(int(d_val))
            else:
                where_clauses.append(
                    "(UPPER(ugcg.diocesecoordenador) = UPPER(?) "
                    "OR ugcg.dioceseid IN (SELECT id FROM userdioceses_cnbb WITH (NOLOCK) WHERE UPPER(nome) = UPPER(?)))"
                )
                params.extend([d_val, d_val])

        situacao_limpa = situacao_grupo.strip().upper() if situacao_grupo else ""
        if situacao_limpa and situacao_limpa != "TODOS":
            where_clauses.append("UPPER(uggo.situacao_grupo) = ?")
            params.append(situacao_limpa)

        filtro_str = " AND ".join(where_clauses)

        sql = f"""
            SELECT DISTINCT
                ugcg.cadastroid_coordenador AS IdSavic,
                ugcg.entcod_apolo AS CodigoApolo,
                ugcg.coordenador,
                ugcg.cpfcoordenador,
                ugcg.datainiciocoordenacao,
                ugcg.datafimcoordenacao,
                ugcg.generocoordenador AS Genero,
                ugcg.telefonefixo_coordenador,
                ugcg.telefonecomercial_coordenador,
                ugcg.celular_coordenador,
                ugcg.celular2_coordenador,
                ugcg.email,
                ugcg.endereco_coordenador,
                ugcg.numero,
                ugcg.complemento,
                ugcg.bairrocoordenador,
                ugcg.cepcoordenador,
                ugc1.cidnomecomp AS CidadeCoordenador,
                ugc1.ufsigla AS EstadoCoordenador,
                ugcg.dioceseid,
                ugcg.diocesecoordenador,
                ugcg.mandatoindeterminado,
                ugcg.rgcoordenador,
                ugcg.rgorgaoexpedidor,
                ISNULL(ugcg.flagexportado, 'Não') AS flagexportado
            FROM USER_geoapolo_coordenadores_grupodeoracao ugcg WITH (NOLOCK)
            LEFT JOIN USER_geoapolo_cidades ugc1 WITH (NOLOCK) ON ugcg.go_geocidcod = ugc1.geocidcod
            INNER JOIN USER_geoapolo_gruposdeoracao uggo WITH (NOLOCK) ON ugcg.cadastroid_coordenador = uggo.cadastroid_coordenador
            WHERE {filtro_str}
            ORDER BY ugcg.coordenador ASC
        """
        resultado = []
        try:
            cur.execute(sql, params)
            for row in cur.fetchall():
                resultado.append(CoordenadorModeracaoDTO(
                    id_savic=str(row[0] or "").strip(),
                    codigo_apolo=str(row[1] or "").strip(),
                    coordenador=str(row[2] or "").strip(),
                    cpf=str(row[3] or "").strip(),
                    data_inicio=row[4] if isinstance(row[4], (date, datetime)) else None,
                    data_fim=row[5] if isinstance(row[5], (date, datetime)) else None,
                    genero=str(row[6] or "").strip(),
                    telefone_fixo=str(row[7] or "").strip(),
                    telefone_comercial=str(row[8] or "").strip(),
                    celular=str(row[9] or "").strip(),
                    celular2=str(row[10] or "").strip(),
                    email=str(row[11] or "").strip(),
                    endereco=str(row[12] or "").strip(),
                    numero=str(row[13] or "").strip(),
                    complemento=str(row[14] or "").strip(),
                    bairro=str(row[15] or "").strip(),
                    cep=str(row[16] or "").strip(),
                    cidade=str(row[17] or "").strip(),
                    uf=str(row[18] or "").strip(),
                    diocese_id=str(row[19] or "").strip(),
                    diocese_nome=str(row[20] or "").strip(),
                    mandato_indeterminado=str(row[21] or "Não").strip(),
                    rg=str(row[22] or "").strip(),
                    orgao_emissor=str(row[23] or "").strip(),
                    flagexportado=str(row[24] or "Não").strip(),
                ))
        except Exception as exc:
            logger.error(f"Erro ao listar coordenadores com filtros: {exc}")
        return resultado

    def buscar_grupos_por_coordenador(self, cadastroid_coordenador: str) -> List[GrupoOracaoModeracaoDTO]:
        """
        Retorna os grupos de oração vinculados ao coordenador (cadastroid_coordenador).
        Traz a coluna flagexportado ('Sim'/'Não').
        """
        if not cadastroid_coordenador:
            return []

        conn = self._get_conn()
        cur = conn.cursor()
        sql = """
            SELECT
                uggo.gocodigo,
                uggo.codigoapolo,
                uggo.gonome_grupodeoracao AS GrupodeOracao,
                uggo.go_local_grupo AS Local_Reuniao,
                uggo.go_tipo_de_local AS Tipo_Local,
                UPPER(ugcg.endereco_coordenador) AS Endereco,
                ugcg.numero,
                ugcg.complemento,
                ugcg.bairrocoordenador,
                ugcg.cepcoordenador AS cep,
                uggo.go_geocidcod,
                ugc.cidnomecomp,
                ugc.ufsigla,
                uggo.dias_semana AS Dias_Reuniao,
                uggo.horario,
                uggo.situacao_grupo,
                uggo.caracteristica_grupo,
                uggo.datainclusao_go AS Data_Inclusao_Savic,
                uggo.datatualizacao_go AS Ultima_Atualizacao,
                ISNULL(uggo.flagexportado, 'Não') AS flagexportado,
                uggo.cadastroid_coordenador
            FROM USER_geoapolo_gruposdeoracao uggo WITH (NOLOCK)
            LEFT JOIN USER_geoapolo_cidades ugc WITH (NOLOCK) ON uggo.go_geocidcod = ugc.geocidcod
            INNER JOIN USER_geoapolo_coordenadores_grupodeoracao ugcg WITH (NOLOCK) ON uggo.cadastroid_coordenador = ugcg.cadastroid_coordenador
            WHERE uggo.cadastroid_coordenador = ?
            ORDER BY uggo.gonome_grupodeoracao ASC
        """
        resultado = []
        try:
            cur.execute(sql, [str(cadastroid_coordenador).strip()])
            for row in cur.fetchall():
                resultado.append(GrupoOracaoModeracaoDTO(
                    gocodigo=str(row[0] or "").strip(),
                    codigo_apolo=str(row[1] or "").strip(),
                    nome_grupo=str(row[2] or "").strip(),
                    local_reuniao=str(row[3] or "").strip(),
                    tipo_local=str(row[4] or "").strip(),
                    endereco=str(row[5] or "").strip(),
                    numero=str(row[6] or "").strip(),
                    complemento=str(row[7] or "").strip(),
                    bairro=str(row[8] or "").strip(),
                    cep=str(row[9] or "").strip(),
                    geocidcod=str(row[10] or "").strip(),
                    cidade=str(row[11] or "").strip(),
                    uf=str(row[12] or "").strip(),
                    dias_reuniao=str(row[13] or "").strip(),
                    horario=str(row[14] or "").strip(),
                    situacao_grupo=str(row[15] or "").strip(),
                    caracteristica_grupo=str(row[16] or "").strip(),
                    data_inclusao_savic=row[17] if isinstance(row[17], datetime) else None,
                    ultima_atualizacao=row[18] if isinstance(row[18], datetime) else None,
                    flagexportado=str(row[19] or "Não").strip(),
                    cadastroid_coordenador=str(row[20] if len(row) > 20 and row[20] else cadastroid_coordenador).strip(),
                ))
        except Exception as exc:
            logger.error(f"Erro ao buscar grupos de oração para coordenador {cadastroid_coordenador}: {exc}")
        return resultado

    def buscar_grupos_por_ids_coordenadores(self, ids_coords: List[str]) -> List[GrupoOracaoModeracaoDTO]:
        """Busca em lote todos os grupos de oração associados a uma lista de IDs de coordenadores."""
        if not ids_coords:
            return []

        conn = self._get_conn()
        cur = conn.cursor()

        chunks = [ids_coords[i:i + 500] for i in range(0, len(ids_coords), 500)]
        resultado = []

        for chunk in chunks:
            placeholders = ",".join("?" for _ in chunk)
            sql = f"""
                SELECT
                    uggo.gocodigo,
                    uggo.codigoapolo,
                    uggo.gonome_grupodeoracao,
                    uggo.go_local_grupo,
                    uggo.go_tipo_de_local,
                    UPPER(ugcg.endereco_coordenador),
                    ugcg.numero,
                    ugcg.complemento,
                    ugcg.bairrocoordenador,
                    ugcg.cepcoordenador,
                    uggo.go_geocidcod,
                    ugc.cidnomecomp,
                    ugc.ufsigla,
                    uggo.dias_semana,
                    uggo.horario,
                    uggo.situacao_grupo,
                    uggo.caracteristica_grupo,
                    uggo.datainclusao_go,
                    uggo.datatualizacao_go,
                    ISNULL(uggo.flagexportado, 'Não') AS flagexportado,
                    uggo.cadastroid_coordenador
                FROM USER_geoapolo_gruposdeoracao uggo WITH (NOLOCK)
                LEFT JOIN USER_geoapolo_cidades ugc WITH (NOLOCK) ON uggo.go_geocidcod = ugc.geocidcod
                INNER JOIN USER_geoapolo_coordenadores_grupodeoracao ugcg WITH (NOLOCK) ON uggo.cadastroid_coordenador = ugcg.cadastroid_coordenador
                WHERE uggo.cadastroid_coordenador IN ({placeholders})
                ORDER BY uggo.gonome_grupodeoracao ASC
            """
            try:
                cur.execute(sql, chunk)
                for row in cur.fetchall():
                    resultado.append(GrupoOracaoModeracaoDTO(
                        gocodigo=str(row[0] or "").strip(),
                        codigo_apolo=str(row[1] or "").strip(),
                        nome_grupo=str(row[2] or "").strip(),
                        local_reuniao=str(row[3] or "").strip(),
                        tipo_local=str(row[4] or "").strip(),
                        endereco=str(row[5] or "").strip(),
                        numero=str(row[6] or "").strip(),
                        complemento=str(row[7] or "").strip(),
                        bairro=str(row[8] or "").strip(),
                        cep=str(row[9] or "").strip(),
                        geocidcod=str(row[10] or "").strip(),
                        cidade=str(row[11] or "").strip(),
                        uf=str(row[12] or "").strip(),
                        dias_reuniao=str(row[13] or "").strip(),
                        horario=str(row[14] or "").strip(),
                        situacao_grupo=str(row[15] or "").strip(),
                        caracteristica_grupo=str(row[16] or "").strip(),
                        data_inclusao_savic=row[17] if isinstance(row[17], datetime) else None,
                        ultima_atualizacao=row[18] if isinstance(row[18], datetime) else None,
                        flagexportado=str(row[19] or "Não").strip(),
                        cadastroid_coordenador=str(row[20] if len(row) > 20 and row[20] else "").strip(),
                    ))
            except Exception as exc:
                logger.error(f"Erro ao buscar grupos por lote: {exc}")

        return resultado

    # -------------------------------------------------------------------------
    # Operações de Exportação para Tabelas de Entidades GeoAlvo
    # -------------------------------------------------------------------------
    def buscar_geoentcod_por_cpf(self, cpf: str) -> Optional[str]:
        """Localiza geoentcod em USER_geoapolo_entidade_documentos pelo CPF."""
        if not cpf or not cpf.strip():
            return None
        cpf_orig = cpf.strip()
        cpf_limpo = limpar_formatacao(cpf_orig)
        cpf_fmt = formatar_cpf(cpf_limpo) if len(cpf_limpo) == 11 else cpf_orig

        conn = self._get_conn()
        cur = conn.cursor()
        sql = """
            SELECT TOP 1 geoentcod
            FROM USER_geoapolo_entidade_documentos WITH (NOLOCK)
            WHERE (geotipodocumento = 'CPF/CNPJ' OR geotipodocumento LIKE '%CPF%')
              AND (
                  geonumerodocumento IN (?, ?, ?)
                  OR REPLACE(REPLACE(REPLACE(geonumerodocumento, '.', ''), '-', ''), '/', '') = ?
              )
        """
        try:
            cur.execute(sql, [cpf_orig, cpf_limpo, cpf_fmt, cpf_limpo])
            row = cur.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
        except Exception as exc:
            logger.error(f"Erro ao buscar CPF {cpf}: {exc}")
        return None

    def buscar_geoentcod_por_nome_e_cidade(self, nome: str, geocidcod: str) -> Optional[str]:
        """Localiza geoentcod em USER_geoapolo_entidade pelo nome e código da cidade."""
        if not nome or not nome.strip():
            return None
        conn = self._get_conn()
        cur = conn.cursor()
        sql = """
            SELECT TOP 1 geoentcod
            FROM USER_geoapolo_entidade WITH (NOLOCK)
            WHERE UPPER(geoentnome) = UPPER(?) AND geocidcod = ?
        """
        try:
            cur.execute(sql, [nome.strip(), str(geocidcod).strip()])
            row = cur.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
        except Exception:
            pass
        return None

    def garantir_categoria_entidade(self, geoentcod: str, geocategcodestr: str):
        """Associa a categoria (ex: 02.001.0006 ou 02.001) na tabela USER_geoapolo_entcateg."""
        if not geoentcod or not geocategcodestr:
            return
        conn = self._get_conn()
        cur = conn.cursor()
        sql = """
            IF NOT EXISTS (
                SELECT 1 FROM USER_geoapolo_entcateg
                WHERE geoentcod = ? AND geocategcodestr = ?
            )
            BEGIN
                INSERT INTO USER_geoapolo_entcateg (geoentcod, geocategcodestr)
                VALUES (?, ?);
            END;
        """
        try:
            cur.execute(sql, [geoentcod, geocategcodestr, geoentcod, geocategcodestr])
        except Exception as exc:
            logger.error(f"Erro ao vincular categoria {geocategcodestr} para entidade {geoentcod}: {exc}")

    def marcar_coordenador_exportado(self, cadastroid_coordenador: str, geoentcod: str):
        """Atualiza flagexportado = 'Sim' e entcod_apolo na tabela de coordenadores."""
        conn = self._get_conn()
        cur = conn.cursor()
        sql = """
            UPDATE USER_geoapolo_coordenadores_grupodeoracao
            SET flagexportado = 'Sim', entcod_apolo = ?
            WHERE cadastroid_coordenador = ?
        """
        try:
            cur.execute(sql, [geoentcod, str(cadastroid_coordenador).strip()])
        except Exception as exc:
            logger.error(f"Erro ao marcar coordenador {cadastroid_coordenador} como exportado: {exc}")

    def marcar_grupo_exportado(self, gocodigo: str, geoentcod: str):
        """Atualiza flagexportado = 'Sim' e codigoapolo na tabela de grupos de oração."""
        conn = self._get_conn()
        cur = conn.cursor()
        sql = """
            UPDATE USER_geoapolo_gruposdeoracao
            SET flagexportado = 'Sim', codigoapolo = ?
            WHERE gocodigo = ?
        """
        try:
            cur.execute(sql, [geoentcod, str(gocodigo).strip()])
        except Exception as exc:
            logger.error(f"Erro ao marcar grupo {gocodigo} como exportado: {exc}")

    def garantir_origem_entidade(self, geoentcod: str, origcod: str = "013.007", conn=None) -> bool:
        """
        Associa ou atualiza a origem da entidade na tabela USER_geoapolo_origens_entidade.
        Por padrão, '013.007' (SAVIC).
        """
        if not geoentcod or not origcod:
            return False
        connection = conn if conn is not None else self._get_conn()
        cur = connection.cursor()
        sql = """
            IF NOT EXISTS (
                SELECT 1 FROM USER_geoapolo_origens_entidade WITH (NOLOCK)
                WHERE geoentcod = ?
            )
            BEGIN
                INSERT INTO USER_geoapolo_origens_entidade (geo_origcodestr, geoentcod)
                VALUES (?, ?);
            END
            ELSE
            BEGIN
                UPDATE USER_geoapolo_origens_entidade
                SET geo_origcodestr = ?
                WHERE geoentcod = ?;
            END;
        """
        try:
            cur.execute(sql, [geoentcod, origcod, geoentcod, origcod, geoentcod])
            return True
        except Exception as exc:
            logger.error(f"Erro ao vincular origem {origcod} para entidade {geoentcod}: {exc}")
            return False

    def assegurar_colunas_exportado(self):
        """Garante que as colunas flagexportado existam nas tabelas de coordenadores e grupos e reconcilia origens SAVIC."""
        conn = self._get_conn()
        cur = conn.cursor()
        try:
            cur.execute("""
                IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('USER_geoapolo_coordenadores_grupodeoracao') AND name = 'flagexportado')
                ALTER TABLE USER_geoapolo_coordenadores_grupodeoracao ADD flagexportado VARCHAR(3) NULL CONSTRAINT DF_ugcg_flagexportado DEFAULT 'Não' WITH VALUES;
            """)
            cur.execute("""
                IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('USER_geoapolo_gruposdeoracao') AND name = 'flagexportado')
                ALTER TABLE USER_geoapolo_gruposdeoracao ADD flagexportado VARCHAR(3) NULL CONSTRAINT DF_uggo_flagexportado DEFAULT 'Não' WITH VALUES;
            """)
            # Garante que a origem '013.007' exista em USER_geoapolo_origens
            cur.execute("""
                IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'USER_geoapolo_origens')
                AND NOT EXISTS (SELECT 1 FROM USER_geoapolo_origens WITH (NOLOCK) WHERE geo_origcodestr = '013.007')
                BEGIN
                    INSERT INTO USER_geoapolo_origens (geo_origcodestr, geo_orignome, geo_origdatainicial, geo_origdatafinal, geo_origativa)
                    VALUES ('013.007', 'SAVIC', '2000-01-01', '2050-12-31', 'Sim');
                END;
            """)
            # Reconciliação: vincula a origem '013.007' a registros exportados de grupos (02.001) e coordenadores (02.001.0006) sem origem
            cur.execute("""
                IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'USER_geoapolo_origens_entidade')
                BEGIN
                    INSERT INTO USER_geoapolo_origens_entidade (geo_origcodestr, geoentcod)
                    SELECT '013.007', e.geoentcod
                      FROM USER_geoapolo_entidade e WITH (NOLOCK)
                     INNER JOIN USER_geoapolo_entcateg c WITH (NOLOCK) ON e.geoentcod = c.geoentcod
                      LEFT JOIN USER_geoapolo_origens_entidade o WITH (NOLOCK) ON e.geoentcod = o.geoentcod
                     WHERE c.geocategcodestr IN ('02.001', '02.001.0006')
                       AND o.geo_origcodestr IS NULL;
                END;
            """)
            conn.commit()
        except Exception as exc:
            logger.error(f"Erro ao assegurar colunas flagexportado / origens: {exc}")

    # -------------------------------------------------------------------------
    # Ficha Financeira (Atalho F5)
    # -------------------------------------------------------------------------
    def buscar_ficha_financeira(self, entcod: str) -> List[FichaFinanceiraDTO]:
        """
        Consulta histórico de doações na tabela parc_doc_fin agrupado por tipo de cobrança e empresa.
        Equivalente ao comando F5 do Delphi (querysql6).
        """
        if not entcod or entcod in ("0", ""):
            return []

        conn = self._get_conn()
        cur = conn.cursor()
        sql = """
            SELECT
                pdf.empcod AS Empresa,
                pdf.tipocobcod AS Codigo_Tipo_Cobranca,
                tc.TipoCobNome AS TipoCobranca,
                MIN(pdf.parcdocfindataemissao) AS PrimeiroRegistro,
                MAX(pdf.parcdocfindataemissao) AS UltimoRegistro,
                SUM(pdf.parcdocfinvalpag) AS VrTotalDoado
            FROM parc_doc_fin pdf WITH (NOLOCK)
            INNER JOIN TIPO_COBRANCA tc WITH (NOLOCK) ON pdf.TipoCobCod = tc.TipoCobCod
            INNER JOIN entidade e WITH (NOLOCK) ON pdf.entcod = e.EntCod
            WHERE pdf.entcod = ?
              AND pdf.empcod IN ('1.01', '1.03')
              AND pdf.MovCtrlBancNum IS NOT NULL
            GROUP BY pdf.TipoCobCod, tc.TipoCobNome, pdf.empcod
            ORDER BY pdf.empcod ASC, tc.TipoCobNome ASC
        """
        resultado = []
        try:
            cur.execute(sql, [str(entcod).strip()])
            for row in cur.fetchall():
                vr = row[5]
                vr_decimal = Decimal(str(vr)) if vr is not None else Decimal("0.00")
                resultado.append(FichaFinanceiraDTO(
                    empresa=str(row[0] or "").strip(),
                    tipo_cobranca_cod=str(row[1] or "").strip(),
                    tipo_cobranca_nome=str(row[2] or "").strip(),
                    primeiro_registro=row[3] if isinstance(row[3], datetime) else None,
                    ultimo_registro=row[4] if isinstance(row[4], datetime) else None,
                    vr_total_doado=vr_decimal
                ))
        except Exception as exc:
            logger.error(f"Erro ao buscar ficha financeira para entcod {entcod}: {exc}")
        return resultado

    # -------------------------------------------------------------------------
    # Comparativo de Grupos Apolo na Cidade (Atalho F6)
    # -------------------------------------------------------------------------
    def listar_grupos_apolo_cidade(
        self, cidcod: str, categ_prefix: str = "02.001"
    ) -> List[EntidadeApoloComparativoDTO]:
        """
        Retorna as entidades cadastradas no Apolo da categoria de grupos de oração (ex: 02.001%)
        para a cidade especificada. Equivalente ao atalho F6 do Delphi (querysql8).
        """
        if not cidcod:
            return []

        conn = self._get_conn()
        cur = conn.cursor()
        sql = """
            SELECT DISTINCT
                e.entcod,
                e.tipotratcod,
                e.entnome,
                e.entlograd,
                e.entender,
                e.entenderno,
                e.entendercomp,
                e.entbair,
                e.entcep,
                cid.cidnomecomp,
                cid.ufsigla,
                e.cidcod
            FROM entidade e WITH (NOLOCK)
            INNER JOIN cidade cid WITH (NOLOCK) ON e.cidcod = cid.cidcod
            INNER JOIN ent_categ ec WITH (NOLOCK) ON e.entcod = ec.entcod
            WHERE e.cidcod = ?
              AND SUBSTRING(ec.categcodestr, 1, 6) = ?
            ORDER BY e.entnome ASC
        """
        resultado = []
        try:
            prefix = categ_prefix[:6] if len(categ_prefix) >= 6 else "02.001"
            cur.execute(sql, [str(cidcod).strip(), prefix])
            for row in cur.fetchall():
                resultado.append(EntidadeApoloComparativoDTO(
                    entcod=str(row[0] or "").strip(),
                    tipotratcod=str(row[1] or "").strip(),
                    entnome=str(row[2] or "").strip(),
                    entlograd=str(row[3] or "").strip(),
                    entender=str(row[4] or "").strip(),
                    entenderno=str(row[5] or "").strip(),
                    entendercomp=str(row[6] or "").strip(),
                    entbair=str(row[7] or "").strip(),
                    entcep=str(row[8] or "").strip(),
                    cidade=str(row[9] or "").strip(),
                    uf=str(row[10] or "").strip(),
                    cidcod=str(row[11] or "").strip(),
                ))
        except Exception as exc:
            logger.error(f"Erro ao listar grupos Apolo na cidade {cidcod}: {exc}")
        return resultado

    # -------------------------------------------------------------------------
    # Categorias Disponíveis
    # -------------------------------------------------------------------------
    def listar_categorias_go(self) -> List[Dict[str, str]]:
        """Retorna as categorias elegíveis para grupos de oração (02.001, etc.)."""
        conn = self._get_conn()
        cur = conn.cursor()
        sql = """
            SELECT cat.categcodestr, cat.categnome
            FROM categoria cat WITH (NOLOCK)
            WHERE SUBSTRING(cat.CategCodEstr, 1, 6) IN (
                '02.001', '02.002', '03.001', '03.002', '03.003', '03.004', '03.005', '03.006'
            )
            ORDER BY cat.CategCodEstr ASC
        """
        resultado = []
        try:
            cur.execute(sql)
            for row in cur.fetchall():
                resultado.append({
                    "codigo": str(row[0] or "").strip(),
                    "nome": str(row[1] or "").strip(),
                })
        except Exception as exc:
            logger.error(f"Erro ao listar categorias: {exc}")
        return resultado
