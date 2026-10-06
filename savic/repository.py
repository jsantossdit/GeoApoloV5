"""
Repositório de Dados do Módulo SAVIC.
Acessa a base legado SAVIC (MySQL) e consulta tabelas de apoio do GeoAlvo (SQL Server).
"""

import logging
from datetime import date, datetime
from typing import Optional, List, Dict, Any

from savic.models import (
    SavicResumoStatusDTO,
    SavicFiltroDTO,
    SavicGrupoOracaoDTO,
    SavicCoordenadorDTO,
)
from entidades.database import obter_conexao_savic, obter_conexao_banco

logger = logging.getLogger(__name__)


class SavicRepository:
    """Encapsula operações SQL na base SAVIC (MySQL) e consultas de apoio no GeoAlvo."""

    def __init__(self, conn_savic=None, conn_geo=None):
        self._conn_savic = conn_savic
        self._conn_geo = conn_geo

    def _get_savic_conn(self):
        if self._conn_savic is not None:
            return self._conn_savic
        return obter_conexao_savic()

    def _get_geo_conn(self):
        if self._conn_geo is not None:
            return self._conn_geo
        return obter_conexao_banco()

    def obter_resumo_status(self) -> SavicResumoStatusDTO:
        """
        Executa as 4 consultas estatísticas de grupos de oração no SAVIC (MySQL).
        Equivalente a estatistica_go_savic do Delphi.
        """
        conn = self._get_savic_conn()
        resumo = SavicResumoStatusDTO()
        deve_fechar = (self._conn_savic is None)

        try:
            with conn.cursor() as cur:
                # 1. Total de GO
                cur.execute("SELECT COUNT(1) AS TotalGo FROM go")
                row = cur.fetchone()
                if row:
                    val = row.get("TotalGo") if isinstance(row, dict) else row[0]
                    resumo.total_go = int(val or 0)

                # 2. Total Homologados
                sql_homolog = (
                    "SELECT COUNT(1) AS TotalGoHomologado FROM go "
                    "INNER JOIN go_situacao gs ON go.go_situacaoid = gs.go_situacaoId "
                    "WHERE UPPER(TRIM(gs.descricao)) = 'HOMOLOGADO'"
                )
                cur.execute(sql_homolog)
                row = cur.fetchone()
                if row:
                    val = row.get("TotalGoHomologado") if isinstance(row, dict) else row[0]
                    resumo.total_homologados = int(val or 0)

                # 3. Total Não Homologados
                sql_nao_homolog = (
                    "SELECT COUNT(1) AS TotalGoNaoHomologado FROM go "
                    "INNER JOIN go_situacao gs ON go.go_situacaoid = gs.go_situacaoId "
                    "WHERE UPPER(TRIM(gs.descricao)) IN ('NÃO HOMOLOGADO', 'NAO HOMOLOGADO')"
                )
                cur.execute(sql_nao_homolog)
                row = cur.fetchone()
                if row:
                    val = row.get("TotalGoNaoHomologado") if isinstance(row, dict) else row[0]
                    resumo.total_nao_homologados = int(val or 0)

                # 4. Total Em Andamento
                sql_andamento = (
                    "SELECT COUNT(1) AS TotalGoEmAndamento FROM go "
                    "INNER JOIN go_situacao gs ON go.go_situacaoid = gs.go_situacaoId "
                    "WHERE UPPER(TRIM(gs.descricao)) = 'EM ANDAMENTO'"
                )
                cur.execute(sql_andamento)
                row = cur.fetchone()
                if row:
                    val = row.get("TotalGoEmAndamento") if isinstance(row, dict) else row[0]
                    resumo.total_em_andamento = int(val or 0)

            return resumo
        finally:
            if deve_fechar:
                try:
                    conn.close()
                except Exception:
                    pass

    def contar_registros_apurados(self, filtro: SavicFiltroDTO) -> int:
        """
        Calcula o total de registros apurados no SAVIC baseado no período de datas
        e na regra de mandato indeterminado ou período vigente.
        """
        conn = self._get_savic_conn()
        deve_fechar = (self._conn_savic is None)

        dt_ini_str = filtro.data_inicial.strftime("%Y-%m-%d") if filtro.data_inicial else "1900-01-01"
        dt_fim_str = filtro.data_final.strftime("%Y-%m-%d") if filtro.data_final else "2099-12-31"

        clausula_mandato = ""
        if filtro.apenas_vigentes_ou_indeterminados:
            clausula_mandato = (
                "AND ("
                "  (UPPER(COALESCE(vga.indeterminado, '')) IN ('SIM', 'S', '1', 'TRUE')) "
                "  OR (vga.datafim_coordenacao IS NULL OR vga.datafim_coordenacao >= CURRENT_DATE())"
                ")"
            )

        sql = f"""
            SELECT COUNT(1) AS TotalApurado
            FROM view_go_ativosv2 vga
            WHERE (vga.DataAtualizacao_go BETWEEN %s AND %s)
            {clausula_mandato}
        """

        try:
            with conn.cursor() as cur:
                cur.execute(sql, (dt_ini_str, dt_fim_str))
                row = cur.fetchone()
                if row:
                    val = row.get("TotalApurado") if isinstance(row, dict) else row[0]
                    return int(val or 0)
                return 0
        finally:
            if deve_fechar:
                try:
                    conn.close()
                except Exception:
                    pass

    def buscar_grupos_para_importacao(self, filtro: SavicFiltroDTO) -> List[SavicGrupoOracaoDTO]:
        """
        Consulta todos os registros de view_go_ativosv2 correspondentes ao filtro de período e vigência.
        """
        conn = self._get_savic_conn()
        deve_fechar = (self._conn_savic is None)

        dt_ini_str = filtro.data_inicial.strftime("%Y-%m-%d") if filtro.data_inicial else "1900-01-01"
        dt_fim_str = filtro.data_final.strftime("%Y-%m-%d") if filtro.data_final else "2099-12-31"

        clausula_mandato = ""
        if filtro.apenas_vigentes_ou_indeterminados:
            clausula_mandato = (
                "AND ("
                "  (UPPER(COALESCE(vga.indeterminado, '')) IN ('SIM', 'S', '1', 'TRUE')) "
                "  OR (vga.datafim_coordenacao IS NULL OR vga.datafim_coordenacao >= CURRENT_DATE())"
                ")"
            )

        sql = f"""
            SELECT
                vga.goid, UPPER(COALESCE(vga.go, '')) AS GrupodeOracao,
                UPPER(COALESCE(vga.cidade, '')) AS Cidade, UPPER(COALESCE(vga.estado, '')) AS Estado,
                COALESCE(vga.dias_semana, '') AS dias_semana, COALESCE(vga.horario, '') AS horario,
                UPPER(COALESCE(vga.situacao, '')) AS Situacao, UPPER(COALESCE(vga.caracteristica, '')) AS CaracteristicaGrupo,
                UPPER(COALESCE(vga.local, '')) AS LocalReuniao, UPPER(COALESCE(vga.tipo_local, '')) AS TipoLocalReuniao,
                vga.datainclusao_go, vga.dataatualizacao_go,
                COALESCE(vga.cadastroid_coord, '') AS cadastroid_coord,
                UPPER(COALESCE(vga.coordenador, '')) AS Coordenador,
                COALESCE(vga.genero_coord, 'M') AS genero_coord,
                COALESCE(vga.ender_coord, '') AS EnderecoCoordenador,
                COALESCE(vga.Numero_CasaCoord, '') AS Numero_CasaCoord,
                COALESCE(vga.Compl_coord, '') AS Compl_coord,
                UPPER(COALESCE(vga.bairrocoord, '')) AS Bairro,
                COALESCE(vga.CepCoord, '') AS CepCoord,
                COALESCE(vga.cpf_coordenador, '') AS cpf_coordenador,
                COALESCE(vga.rgcoord, '') AS rgcoord,
                COALESCE(vga.rgcoordemissor, '') AS rgcoordemissor,
                COALESCE(vga.CaixaPostal_Coord, '') AS CaixaPostal_Coord,
                COALESCE(vga.Telefone_Coord, '') AS Telefone_Coord,
                COALESCE(vga.TelCom_Coord, '') AS TelCom_Coord,
                COALESCE(vga.CelularCoord1, '') AS CelularCoord1,
                COALESCE(vga.celularcoord2, '') AS celularcoord2,
                COALESCE(vga.dioceseId, '') AS dioceseId,
                COALESCE(vga.diocesecoordenador, '') AS diocesecoordenador,
                COALESCE(vga.email, '') AS email,
                COALESCE(vga.indeterminado, 'Não') AS MandatoIndeterminado,
                vga.Dataini_coordenacao, vga.datafim_coordenacao,
                COALESCE(vga.useratualizacao, '') AS useratualizacao,
                COALESCE(vga.ultimaalteracaofeitapor, '') AS ultimaalteracaofeitapor
            FROM view_go_ativosv2 vga
            WHERE (vga.DataAtualizacao_go BETWEEN %s AND %s)
            {clausula_mandato}
            ORDER BY vga.goid ASC
        """

        lista: List[SavicGrupoOracaoDTO] = []
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (dt_ini_str, dt_fim_str))
                rows = cur.fetchall()
                for r in rows:
                    coord = SavicCoordenadorDTO(
                        cadastroid_coord=str(r.get("cadastroid_coord") or ""),
                        coordenador=str(r.get("Coordenador") or ""),
                        genero_coord=str(r.get("genero_coord") or "M"),
                        cpf_coordenador=str(r.get("cpf_coordenador") or ""),
                        rgcoord=str(r.get("rgcoord") or ""),
                        rgcoordemissor=str(r.get("rgcoordemissor") or ""),
                        endereco_coordenador=str(r.get("EnderecoCoordenador") or ""),
                        numero_casa_coord=str(r.get("Numero_CasaCoord") or ""),
                        compl_coord=str(r.get("Compl_coord") or ""),
                        bairro_coord=str(r.get("Bairro") or ""),
                        cep_coord=str(r.get("CepCoord") or ""),
                        cidade=str(r.get("Cidade") or ""),
                        estado=str(r.get("Estado") or ""),
                        caixa_postal=str(r.get("CaixaPostal_Coord") or ""),
                        telefone_coord=str(r.get("Telefone_Coord") or ""),
                        tel_com_coord=str(r.get("TelCom_Coord") or ""),
                        celular_coord1=str(r.get("CelularCoord1") or ""),
                        celular_coord2=str(r.get("celularcoord2") or ""),
                        email=str(r.get("email") or ""),
                        diocese_id=str(r.get("dioceseId") or ""),
                        diocese_coordenador=str(r.get("diocesecoordenador") or ""),
                        mandato_indeterminado=str(r.get("MandatoIndeterminado") or "Não"),
                        dataini_coordenacao=r.get("Dataini_coordenacao"),
                        datafim_coordenacao=r.get("datafim_coordenacao"),
                        user_atualizacao=str(r.get("useratualizacao") or ""),
                        ultima_alteracao_feita_por=str(r.get("ultimaalteracaofeitapor") or "")
                    )

                    go = SavicGrupoOracaoDTO(
                        goid=str(r.get("goid") or ""),
                        grupo_de_oracao=str(r.get("GrupodeOracao") or ""),
                        cidade=str(r.get("Cidade") or ""),
                        estado=str(r.get("Estado") or ""),
                        dias_semana=str(r.get("dias_semana") or ""),
                        horario=str(r.get("horario") or ""),
                        situacao=str(r.get("Situacao") or ""),
                        caracteristica_grupo=str(r.get("CaracteristicaGrupo") or ""),
                        local_reuniao=str(r.get("LocalReuniao") or ""),
                        tipo_local_reuniao=str(r.get("TipoLocalReuniao") or ""),
                        datainclusao_go=r.get("datainclusao_go"),
                        dataatualizacao_go=r.get("dataatualizacao_go"),
                        coordenador=coord
                    )
                    lista.append(go)
            return lista
        finally:
            if deve_fechar:
                try:
                    conn.close()
                except Exception:
                    pass

    # -------------------------------------------------------------
    # Métodos de Apoio no GeoAlvo (SQL Server)
    # -------------------------------------------------------------
    def buscar_geoentcod_por_cpf(self, cpf: str) -> Optional[str]:
        """
        Busca uma entidade no GeoAlvo pelo CPF na tabela USER_geoapolo_entidade_documentos.
        Testa variações do CPF (original, sem máscara, e com máscara 000.000.000-00).
        Retorna geoentcod se encontrado, ou None se não encontrado.
        """
        if not cpf or not cpf.strip():
            return None

        cpf_original = cpf.strip()
        cpf_limpo = "".join([c for c in cpf_original if c.isdigit()])
        cpf_fmt = ""
        if len(cpf_limpo) == 11:
            cpf_fmt = f"{cpf_limpo[0:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:11]}"

        conn = self._get_geo_conn()
        cur = conn.cursor()
        sql = """
            SELECT TOP 1 geoentcod
            FROM USER_geoapolo_entidade_documentos WITH (NOLOCK)
            WHERE (geotipodocumento = 'CPF/CNPJ' OR geotipodocumento LIKE '%CPF%')
              AND (geonumerodocumento = ? OR geonumerodocumento = ? OR geonumerodocumento = ?)
        """
        try:
            cur.execute(sql, [cpf_original, cpf_limpo, cpf_fmt or cpf_original])
            row = cur.fetchone()
            if row and row[0]:
                return str(row[0]).strip()
            return None
        except Exception as exc:
            logger.error(f"Erro ao buscar CPF {cpf} em USER_geoapolo_entidade_documentos: {exc}")
            return None

    def listar_grupos_ja_importados(self) -> List[Dict[str, Any]]:
        """Retorna os grupos de oração cadastrados na base GeoAlvo para exibição na grid."""
        conn = self._get_geo_conn()
        cur = conn.cursor()
        sql = """
            SELECT gocodigo, gonome_grupodeoracao, go_local_grupo, go_tipo_de_local,
                   situacao_grupo, dias_semana, horario, datainclusao_go, datatualizacao_go
            FROM USER_geoapolo_gruposdeoracao WITH (NOLOCK)
            ORDER BY gocodigo ASC
        """
        resultado = []
        try:
            cur.execute(sql)
            colunas = [column[0].lower() for column in cur.description]
            for row in cur.fetchall():
                resultado.append(dict(zip(colunas, row)))
        except Exception as exc:
            logger.error(f"Erro ao listar grupos já importados no GeoAlvo: {exc}")
        return resultado

    def listar_categorias_geoalvo(self) -> List[Dict[str, str]]:
        """Retorna as categorias cadastradas em USER_geoapolo_categoria para pesquisa."""
        conn = self._get_geo_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT geocategcodestr, geocategnome FROM USER_geoapolo_categoria WITH (NOLOCK) ORDER BY geocategcodestr ASC")
            return [{"codigo": str(r[0]), "descricao": str(r[1])} for r in cur.fetchall()]
        except Exception as exc:
            logger.warning("Erro ao listar categorias GeoAlvo: %s", exc)
            return []

    def obter_nome_categoria(self, codigo: str) -> str:
        """Busca o nome da categoria pelo código estruturado."""
        if not codigo or not str(codigo).strip():
            return ""
        conn = self._get_geo_conn()
        try:
            cur = conn.cursor()
            cur.execute("SELECT TOP 1 geocategnome FROM USER_geoapolo_categoria WITH (NOLOCK) WHERE geocategcodestr = ?", [str(codigo).strip()])
            row = cur.fetchone()
            if row and row[0]:
                return str(row[0])
            return "(Categoria não localizada)"
        except Exception:
            return ""

