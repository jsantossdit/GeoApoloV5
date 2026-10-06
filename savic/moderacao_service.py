"""
Serviço de Negócios para o Módulo de Moderação de Grupos de Oração SAVIC x Apolo.
Valida parâmetros, orquestra consultas em cascata e formata dados para a interface de usuário.
"""

import logging
from datetime import date, datetime
from typing import Optional, List, Dict, Tuple, Any, Callable

from savic.moderacao_models import (
    EstadoDTO,
    DioceseDTO,
    CidadeDioceseDTO,
    FiltroModeracaoDTO,
    CoordenadorModeracaoDTO,
    GrupoOracaoModeracaoDTO,
    FichaFinanceiraDTO,
    EntidadeApoloComparativoDTO,
    ResultadoExportacaoEntidadeDTO,
)
from savic.moderacao_repository import SavicModeracaoRepository
from core import geoapolo_configcod
from core.validators import limpar_formatacao, formatar_cpf
from entidades.database import obter_conexao_banco
from savic.service import eh_mandato_vencido, aplicar_pendencia_mandato_vencido

logger = logging.getLogger(__name__)


class SavicModeracaoService:
    """Regras de negócio e operações de consulta da Moderação de Grupos de Oração."""

    def __init__(
        self,
        repo: Optional[SavicModeracaoRepository] = None,
        repository: Optional[SavicModeracaoRepository] = None,
    ):
        self._repo = repo or repository or SavicModeracaoRepository()

    def obter_estados(self) -> List[EstadoDTO]:
        """Retorna lista de UFs para o combo de estados."""
        return self._repo.listar_estados()

    def obter_dioceses(self, uf: str) -> List[DioceseDTO]:
        """Retorna as dioceses de uma UF selecionada."""
        if not uf:
            return []
        return self._repo.listar_dioceses_por_estado(uf)

    def obter_cidades_diocese(self, diocese_nome_ou_id: str) -> List[CidadeDioceseDTO]:
        """Retorna cidades vinculadas à diocese informada."""
        if not diocese_nome_ou_id:
            return []
        return self._repo.listar_cidades_por_diocese(diocese_nome_ou_id)

    def resolver_codigo_cidade(self, cidade_nome: str, uf: str) -> Optional[str]:
        """Localiza o geocidcod da cidade especificada."""
        return self._repo.buscar_geocidcod(cidade_nome, uf)

    def filtrar_coordenadores(
        self, filtro: FiltroModeracaoDTO
    ) -> Tuple[Optional[str], List[CoordenadorModeracaoDTO], str]:
        """
        Valida os filtros (agora opcionais) e busca os coordenadores correspondentes.
        Permite filtrar somente por Situação (ex: HOMOLOGADO) sem exigir Estado, Diocese ou Cidade.
        Retorna (geocidcod, lista_coordenadores, mensagem_status).
        """
        geocidcod = None
        uf_limpa = filtro.uf.strip().upper() if filtro.uf else ""
        cidade_limpa = filtro.cidade_nome.strip() if filtro.cidade_nome else ""
        diocese_limpa = filtro.diocese_nome.strip() if filtro.diocese_nome else ""

        if cidade_limpa and uf_limpa:
            geocidcod = self.resolver_codigo_cidade(cidade_limpa, uf_limpa)
            if not geocidcod:
                msg = f"Cidade '{cidade_limpa}' ({uf_limpa}) não foi localizada na base de dados do GeoAlvo/Apolo."
                return None, [], msg

        coordenadores = self._repo.listar_coordenadores(
            geocidcod=geocidcod,
            uf=uf_limpa if uf_limpa else None,
            diocese_nome_ou_id=diocese_limpa if diocese_limpa else None,
            situacao_grupo=filtro.situacao_grupo
        )

        msg = f"{len(coordenadores)} coordenador(es) encontrado(s)."
        return geocidcod, coordenadores, msg

    def obter_grupos_do_coordenador(
        self, cadastroid_coordenador: str
    ) -> List[GrupoOracaoModeracaoDTO]:
        """Retorna os grupos de oração cadastrados para o coordenador selecionado."""
        if not cadastroid_coordenador:
            return []
        return self._repo.buscar_grupos_por_coordenador(cadastroid_coordenador)

    def obter_ficha_financeira(self, entcod: str) -> List[FichaFinanceiraDTO]:
        """Retorna os dados financeiros históricos da entidade (F5)."""
        if not entcod or entcod in ("0", ""):
            return []
        return self._repo.buscar_ficha_financeira(entcod)

    def obter_comparativo_apolo(
        self, cidcod: str, categoria: str = "02.001"
    ) -> List[EntidadeApoloComparativoDTO]:
        """Retorna entidades cadastradas no Apolo na cidade para comparação (F6)."""
        if not cidcod:
            return []
        return self._repo.listar_grupos_apolo_cidade(cidcod, categ_prefix=categoria)

    def obter_categorias_elegiveis(self) -> List[Dict[str, str]]:
        """Retorna a lista de categorias padrão para grupo de oração."""
        return self._repo.listar_categorias_go()

    @staticmethod
    def _normalizar_tratamento(genero: str) -> str:
        g = str(genero or "M").strip().upper()
        if g.startswith("F"):
            return "0002"
        return "0001"

    @staticmethod
    def _extrair_ddd_e_numero(telefone: str) -> Tuple[str, str]:
        """Separa DDD e número de telefone."""
        digitos = "".join(ch for ch in str(telefone or "") if ch.isdigit())
        if len(digitos) >= 10:
            return digitos[:2], digitos[2:]
        return "", digitos

    @staticmethod
    def _extrair_numero_inteiro(numero_str: str) -> Optional[int]:
        """Extrai apenas os dígitos para colunas numéricas de endereço."""
        digitos = "".join(ch for ch in str(numero_str or "") if ch.isdigit())
        return int(digitos) if digitos else None

    @staticmethod
    def _obter_tipologradabrev_valido(cur) -> str:
        """Retorna uma abreviação de tipo de logradouro válida no banco para satisfazer a fk_geoentadicionais_geolograd."""
        try:
            cur.execute("SELECT tipologradabrev FROM USER_geoapolo_tipologradouro WITH (NOLOCK) WHERE tipologradabrev = 'R.'")
            row = cur.fetchone()
            if row and row[0]:
                return str(row[0]).strip()

            for cand in ('R', 'RUA', 'AV.', 'AV', 'PCA', 'PRACA', 'AL', 'ROD'):
                cur.execute("SELECT tipologradabrev FROM USER_geoapolo_tipologradouro WITH (NOLOCK) WHERE UPPER(tipologradabrev) = ?", [cand])
                r = cur.fetchone()
                if r and r[0]:
                    return str(r[0]).strip()

            cur.execute("SELECT TOP 1 tipologradabrev FROM USER_geoapolo_tipologradouro WITH (NOLOCK) WHERE tipologradabrev IS NOT NULL AND tipologradabrev <> ''")
            r_top = cur.fetchone()
            if r_top and r_top[0]:
                return str(r_top[0]).strip()
        except Exception as e:
            logger.warning("Falha ao consultar USER_geoapolo_tipologradouro: %s", e)
        return "R."

    def exportar_entidades_selecionadas(
        self,
        coordenadores: List[CoordenadorModeracaoDTO],
        grupos: Optional[List[GrupoOracaoModeracaoDTO]] = None,
        empresa_codigo: str = "1.01",
        callback_progresso: Optional[Callable[[int, int, str], None]] = None,
        connection: Optional[Any] = None,
    ) -> ResultadoExportacaoEntidadeDTO:
        """
        Exporta coordenadores e seus respectivos grupos de oração para o GeoAlvo alimentando
        integralmente as 8 tabelas do ecossistema GeoApolo:
          1. USER_geoapolo_entidade (tipolograd = 1 numérico, 'Física'/'Jurídica')
          2. USER_geoapolo_entcateg ('02.001.0006' para coord, '02.001' para grupo)
          3. USER_geoapolo_entidade_ativecon ('94.91-0' Atividades religiosas)
          4. USER_geoapolo_entidade_comunicacao (Celular e Residencial separados)
          5. USER_geoapolo_entidade_contato (Vínculo Grupo de Oração <-> Coordenador)
          6. USER_geoapolo_entidade_documentos (CPF e RG garantidos na inclusão e alteração)
          7. USER_geoapolo_entidade_endereco_adicionais (Endereços residencial e principal)
          8. USER_geoapolo_entidade_webcontato (E-mail principal)
        """
        resultado = ResultadoExportacaoEntidadeDTO()
        if not coordenadores:
            resultado.sucesso = True
            resultado.mensagem = "Nenhum coordenador informado para exportação."
            return resultado

        # Garante a existência das colunas flagexportado
        self._repo.assegurar_colunas_exportado()

        grupos_fornecidos_explicitamente = (grupos is not None)
        if grupos is None:
            ids_coords = [c.id_savic for c in coordenadores if c.id_savic]
            grupos = self._repo.buscar_grupos_por_ids_coordenadores(ids_coords)

        # Mapeia grupos por coordenador
        grupos_por_coord: Dict[str, List[GrupoOracaoModeracaoDTO]] = {}
        for g in grupos:
            grupos_por_coord.setdefault(str(g.cadastroid_coordenador).strip(), []).append(g)

        conn = connection if connection is not None else self._repo._get_conn()
        cur = conn.cursor()
        hoje_str = date.today().strftime("%Y-%m-%d")

        total_passos = len(coordenadores) + len(grupos)
        passo_atual = 0
        grupos_processados_set = set()

        # -------------------------------------------------------------
        # 1. Processamento de Coordenadores e seus Grupos de Oração
        # -------------------------------------------------------------
        for coord in coordenadores:
            passo_atual += 1
            if callback_progresso:
                callback_progresso(
                    passo_atual,
                    total_passos,
                    f"Exportando Coordenador: {coord.coordenador} ({passo_atual}/{total_passos})..."
                )

            cpf_raw = (coord.cpf or "").strip()
            cpf_limpo = limpar_formatacao(cpf_raw)
            cpf_fmt = formatar_cpf(cpf_limpo) if len(cpf_limpo) == 11 else cpf_raw
            rg_limpo = (coord.rg or "").strip()

            # Resolução do geoentcod do coordenador
            # 1.1 Busca PRIMÁRIA pelo CPF em USER_geoapolo_entidade_documentos
            geoentcod_existente = None
            if cpf_limpo or cpf_raw:
                geoentcod_existente = self._repo.buscar_geoentcod_por_cpf(cpf_raw)

            # 1.2 Fallback: se não encontrou por CPF na tabela de documentos, tenta por codigo_apolo pré-existente
            if not geoentcod_existente and coord.codigo_apolo and coord.codigo_apolo not in ("0", ""):
                try:
                    cur.execute("SELECT TOP 1 geoentcod FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE geoentcod = ?", [coord.codigo_apolo.strip()])
                    row_chk = cur.fetchone()
                    if row_chk and row_chk[0]:
                        geoentcod_existente = str(row_chk[0]).strip()
                except Exception:
                    pass

            # 1.3 Busca na tabela entidade do Apolo para reaproveitar entcod se existir
            entcod_alvo = None
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
            if not entcod_alvo and coord.codigo_apolo and coord.codigo_apolo not in ("0", ""):
                entcod_alvo = coord.codigo_apolo.strip()

            # 1.4 Verifica se a entidade realmente existe na tabela mestre USER_geoapolo_entidade
            entidade_mestre_existe = False
            if geoentcod_existente:
                try:
                    cur.execute("SELECT TOP 1 geoentcod FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE geoentcod = ?", [geoentcod_existente])
                    row_m = cur.fetchone()
                    if row_m and row_m[0]:
                        entidade_mestre_existe = True
                except Exception:
                    pass

            # Resolve geocidcod da cidade do coordenador
            cidcod = "00000001"
            if coord.cidade and coord.uf:
                c_cod = self.resolver_codigo_cidade(coord.cidade, coord.uf)
                if c_cod:
                    cidcod = c_cod

            tipo_trat = self._normalizar_tratamento(coord.genero)
            genero_sigla = "F" if str(coord.genero).upper().startswith("F") else "M"
            dt_ini_str = coord.data_inicio.strftime("%Y-%m-%d") if coord.data_inicio else None
            dt_fim_str = coord.data_fim.strftime("%Y-%m-%d") if coord.data_fim else None

            try:
                # ---------------------------------------------------------
                # 1.1 USER_geoapolo_entidade (Coordenador)
                # ---------------------------------------------------------
                if entidade_mestre_existe:
                    sql_upd = """
                        UPDATE USER_geoapolo_entidade SET
                            geoentnome = CASE WHEN ISNULL(NULLIF(?, ''), '') <> '' THEN ? ELSE geoentnome END,
                            geoentnomefantasia = ISNULL(NULLIF(geoentnomefantasia, ''), ISNULL(NULLIF(?, ''), geoentnome)),
                            tipolograd = ISNULL(NULLIF(tipolograd, 0), 1),
                            geotipotratcod = CASE WHEN ISNULL(geotipotratcod, '') IN ('', '0') THEN ? ELSE geotipotratcod END,
                            geoentender = CASE WHEN ISNULL(NULLIF(?, ''), '') <> '' THEN ? ELSE geoentender END,
                            geoenderno = CASE WHEN ISNULL(NULLIF(?, ''), '') <> '' THEN ? ELSE ISNULL(geoenderno, 'S/N') END,
                            geoentendercomp = CASE WHEN ISNULL(NULLIF(?, ''), '') <> '' THEN ? ELSE geoentendercomp END,
                            geoentbair = CASE WHEN ISNULL(NULLIF(?, ''), '') <> '' THEN ? ELSE geoentbair END,
                            geoentcep = CASE WHEN ISNULL(NULLIF(?, ''), '') <> '' THEN ? ELSE geoentcep END,
                            geocidcod = CASE WHEN ISNULL(NULLIF(?, ''), '') <> '' AND ? <> '00000001' THEN ? ELSE ISNULL(NULLIF(geocidcod, ''), ?) END,
                            cidcodapolo = CASE WHEN ISNULL(NULLIF(cidcodapolo, ''), '') IN ('', '0', '00000001') THEN ? ELSE cidcodapolo END,
                            geotipofj = ISNULL(NULLIF(geotipofj, ''), 'Física'),
                            geoentgenero = ISNULL(NULLIF(geoentgenero, ''), ?),
                            geofalecido = ISNULL(NULLIF(geofalecido, ''), 'N'),
                            geoentloccobrancaomesmo = ISNULL(NULLIF(geoentloccobrancaomesmo, ''), 'Sim'),
                            geoentlocentregaomesmo = ISNULL(NULLIF(geoentlocentregaomesmo, ''), 'Sim'),
                            geoenttransporteomesmo = ISNULL(NULLIF(geoenttransporteomesmo, ''), 'Sim'),
                            geoentdatacad = ISNULL(geoentdatacad, ?),
                            geoentdesdedata = ISNULL(geoentdesdedata, ?),
                            entcod = CASE WHEN ISNULL(entcod, '') = '' AND ? <> '' THEN ? ELSE entcod END
                        WHERE geoentcod = ?
                    """
                    cur.execute(sql_upd, [
                        coord.coordenador or "", coord.coordenador or "COORDENADOR SAVIC",
                        coord.coordenador or "COORDENADOR SAVIC",
                        tipo_trat,
                        coord.endereco or "", coord.endereco or "",
                        coord.numero or "", coord.numero or "",
                        coord.complemento or "", coord.complemento or "",
                        coord.bairro or "", coord.bairro or "",
                        limpar_formatacao(coord.cep), limpar_formatacao(coord.cep),
                        cidcod, cidcod, cidcod, cidcod,
                        cidcod,
                        genero_sigla,
                        hoje_str, hoje_str,
                        entcod_alvo or "", entcod_alvo or "",
                        geoentcod_existente
                    ])
                    geoentcod_coord_ativo = geoentcod_existente
                    resultado.total_coordenadores_atualizados += 1
                else:
                    if geoentcod_existente:
                        novo_geoentcod = geoentcod_existente
                    else:
                        novo_geoentcod = geoapolo_configcod(empresa_codigo, "USER_geoapolo_entidade", "Sim", conn)
                    geoentcod_coord_ativo = novo_geoentcod

                    sql_ins_ent = """
                        INSERT INTO USER_geoapolo_entidade (
                            geoentcod, geotipotratcod, geoentnome, geoentnomefantasia, tipolograd,
                            geoentender, geoenderno, geoentendercomp, geoentbair, geoentdatacad,
                            geoentdesdedata, geoentcep, geocidcod, geoentgenero, geotipofj,
                            geofalecido, entcod, cidcodapolo,
                            geoentloccobrancaomesmo, geoentlocentregaomesmo, geoenttransporteomesmo
                        ) VALUES (
                            ?, ?, ?, ?, 1,
                            ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, 'Física',
                            'N', ?, ?,
                            'Sim', 'Sim', 'Sim'
                        )
                    """
                    cur.execute(sql_ins_ent, [
                        novo_geoentcod,
                        tipo_trat,
                        coord.coordenador or "COORDENADOR SAVIC",
                        coord.coordenador or "COORDENADOR SAVIC",
                        coord.endereco,
                        coord.numero,
                        coord.complemento,
                        coord.bairro,
                        hoje_str,
                        hoje_str,
                        limpar_formatacao(coord.cep),
                        cidcod,
                        genero_sigla,
                        entcod_alvo,
                        cidcod
                    ])
                    resultado.total_coordenadores_inseridos += 1

                # 1.2 USER_geoapolo_entcateg: Categoria 02.001.0006 e 08.009 (Loja)
                self._repo.garantir_categoria_entidade(geoentcod_coord_ativo, "02.001.0006")
                self._repo.garantir_categoria_entidade(geoentcod_coord_ativo, "08.009")
                resultado.total_categorias_vinculadas += 2

                # USER_geoapolo_origens_entidade: Origem '013.007' (SAVIC)
                self._repo.garantir_origem_entidade(geoentcod_coord_ativo, "013.007", conn=conn)
                if entcod_alvo:
                    try:
                        cur.execute(
                            "UPDATE entidade SET OrigCodEstr = '013.007' WHERE entcod = ? AND (OrigCodEstr IS NULL OR OrigCodEstr = '')",
                            [entcod_alvo]
                        )
                    except Exception:
                        pass

                # ---------------------------------------------------------
                # 1.3 USER_geoapolo_entidade_documentos: CPF e RG garantidos
                # ---------------------------------------------------------
                if cpf_limpo or cpf_raw:
                    doc_cpf = cpf_limpo if cpf_limpo else cpf_raw
                    sql_doc_cpf = """
                        IF NOT EXISTS (
                            SELECT 1 FROM USER_geoapolo_entidade_documentos WITH (NOLOCK)
                            WHERE geoentcod = ? AND (geotipodocumento = 'CPF/CNPJ' OR geotipodocumento LIKE '%CPF%')
                        )
                        BEGIN
                            INSERT INTO USER_geoapolo_entidade_documentos (geoentcod, geotipodocumento, geonumerodocumento, geoobservacoes)
                            VALUES (?, 'CPF/CNPJ', ?, 'SAVIC');
                        END
                        ELSE
                        BEGIN
                            UPDATE USER_geoapolo_entidade_documentos
                            SET geonumerodocumento = ?, geoobservacoes = 'SAVIC'
                            WHERE geoentcod = ? AND (geotipodocumento = 'CPF/CNPJ' OR geotipodocumento LIKE '%CPF%');
                        END;
                    """
                    cur.execute(sql_doc_cpf, [geoentcod_coord_ativo, geoentcod_coord_ativo, doc_cpf, doc_cpf, geoentcod_coord_ativo])

                if rg_limpo:
                    sql_doc_rg = """
                        IF NOT EXISTS (
                            SELECT 1 FROM USER_geoapolo_entidade_documentos WITH (NOLOCK)
                            WHERE geoentcod = ? AND (geotipodocumento = 'RG/IE' OR geotipodocumento LIKE '%RG%')
                        )
                        BEGIN
                            INSERT INTO USER_geoapolo_entidade_documentos (geoentcod, geotipodocumento, geonumerodocumento, geoobservacoes)
                            VALUES (?, 'RG/IE', ?, ?);
                        END
                        ELSE
                        BEGIN
                            UPDATE USER_geoapolo_entidade_documentos
                            SET geonumerodocumento = ?, geoobservacoes = ?
                            WHERE geoentcod = ? AND (geotipodocumento = 'RG/IE' OR geotipodocumento LIKE '%RG%');
                        END;
                    """
                    cur.execute(sql_doc_rg, [
                        geoentcod_coord_ativo, geoentcod_coord_ativo, rg_limpo, coord.orgao_emissor or "SSP",
                        rg_limpo, coord.orgao_emissor or "SSP", geoentcod_coord_ativo
                    ])

                # ---------------------------------------------------------
                # 1.4 USER_geoapolo_entidade_comunicacao: Celular e Residencial
                # ---------------------------------------------------------
                celular_coord = coord.celular or coord.celular2
                if celular_coord:
                    ddd_cel, num_cel = self._extrair_ddd_e_numero(celular_coord)
                    if num_cel:
                        sql_com_cel = """
                            IF NOT EXISTS (
                                SELECT 1 FROM USER_geoapolo_entidade_comunicacao WITH (NOLOCK)
                                WHERE geoentcod = ? AND geotipotelefone = 'Celular'
                            )
                            BEGIN
                                INSERT INTO USER_geoapolo_entidade_comunicacao (geoentcod, geotipotelefone, geotelefoneddd, geotelefonenumero, flagtelprincipal)
                                VALUES (?, 'Celular', ?, ?, 'S');
                            END
                            ELSE
                            BEGIN
                                UPDATE USER_geoapolo_entidade_comunicacao
                                SET geotelefoneddd = ?, geotelefonenumero = ?
                                WHERE geoentcod = ? AND geotipotelefone = 'Celular';
                            END;
                        """
                        cur.execute(sql_com_cel, [geoentcod_coord_ativo, geoentcod_coord_ativo, ddd_cel, num_cel, ddd_cel, num_cel, geoentcod_coord_ativo])

                fixo_coord = coord.telefone_fixo or coord.telefone_comercial
                if fixo_coord:
                    ddd_fix, num_fix = self._extrair_ddd_e_numero(fixo_coord)
                    if num_fix:
                        sql_com_fix = """
                            IF NOT EXISTS (
                                SELECT 1 FROM USER_geoapolo_entidade_comunicacao WITH (NOLOCK)
                                WHERE geoentcod = ? AND geotipotelefone = 'Residencial'
                            )
                            BEGIN
                                INSERT INTO USER_geoapolo_entidade_comunicacao (geoentcod, geotipotelefone, geotelefoneddd, geotelefonenumero, flagtelprincipal)
                                VALUES (?, 'Residencial', ?, ?, 'N');
                            END
                            ELSE
                            BEGIN
                                UPDATE USER_geoapolo_entidade_comunicacao
                                SET geotelefoneddd = ?, geotelefonenumero = ?
                                WHERE geoentcod = ? AND geotipotelefone = 'Residencial';
                            END;
                        """
                        cur.execute(sql_com_fix, [geoentcod_coord_ativo, geoentcod_coord_ativo, ddd_fix, num_fix, ddd_fix, num_fix, geoentcod_coord_ativo])

                # ---------------------------------------------------------
                # 1.5 USER_geoapolo_entidade_webcontato: E-mail
                # ---------------------------------------------------------
                if coord.email and "@" in coord.email:
                    email_limpo = coord.email.strip()
                    sql_web = """
                        IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_webcontato WITH (NOLOCK) WHERE geoentcod = ?)
                        BEGIN
                            INSERT INTO USER_geoapolo_entidade_webcontato (
                                geoentcod, tipo_contato, website, email, flagemailprincipal, comunicador_instantaneo, endereco_comunicador
                            ) VALUES (?, 'E-mail', '', ?, 'S', '', '');
                        END
                        ELSE
                        BEGIN
                            UPDATE USER_geoapolo_entidade_webcontato
                            SET email = ?
                            WHERE geoentcod = ?;
                        END;
                    """
                    cur.execute(sql_web, [geoentcod_coord_ativo, geoentcod_coord_ativo, email_limpo, email_limpo, geoentcod_coord_ativo])

                # ---------------------------------------------------------
                # 1.6 USER_geoapolo_entidade_endereco_adicionais: Residencial
                # ---------------------------------------------------------
                if coord.endereco:
                    try:
                        tipo_lograd = self._obter_tipologradabrev_valido(cur)
                        num_coord_int = self._extrair_numero_inteiro(coord.numero)
                        sql_end_coord = """
                            IF NOT EXISTS (
                                SELECT 1 FROM USER_geoapolo_entidade_endereco_adicionais WITH (NOLOCK)
                                WHERE geoentcod = ? AND tipo_endereco = 'Residencial'
                            )
                            BEGIN
                                INSERT INTO USER_geoapolo_entidade_endereco_adicionais (
                                    geoentcod, tipo_endereco, tipologradabrev, endereco, numero, complemento, bairro, geocidcod
                                ) VALUES (?, 'Residencial', ?, ?, ?, ?, ?, ?);
                            END
                            ELSE
                            BEGIN
                                UPDATE USER_geoapolo_entidade_endereco_adicionais
                                SET tipologradabrev = ?, endereco = ?, numero = ?, complemento = ?, bairro = ?, geocidcod = ?
                                WHERE geoentcod = ? AND tipo_endereco = 'Residencial';
                            END;
                        """
                        cur.execute(sql_end_coord, [
                            geoentcod_coord_ativo, geoentcod_coord_ativo,
                            tipo_lograd,
                            (coord.endereco or "")[:60], num_coord_int,
                            (coord.complemento or "")[:45], (coord.bairro or "")[:45], cidcod,
                            tipo_lograd,
                            (coord.endereco or "")[:60], num_coord_int,
                            (coord.complemento or "")[:45], (coord.bairro or "")[:45], cidcod,
                            geoentcod_coord_ativo
                        ])
                    except Exception as exc_end_coord:
                        logger.warning("Aviso ao salvar endereço adicional do coordenador %s: %s", coord.coordenador, exc_end_coord)

                # ---------------------------------------------------------
                # 1.7 USER_geoapolo_entidade_ativecon: 94.91-0
                # ---------------------------------------------------------
                sql_ativecon = """
                    IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_ativecon WITH (NOLOCK) WHERE geoentcod = ?)
                    BEGIN
                        INSERT INTO USER_geoapolo_entidade_ativecon (ativeconcodestr, geoentcod)
                        VALUES ('94.91-0', ?);
                    END;
                """
                cur.execute(sql_ativecon, [geoentcod_coord_ativo, geoentcod_coord_ativo])

                # ---------------------------------------------------------
                # 1.8 Marca Coordenador como Exportado
                # ---------------------------------------------------------
                self._repo.marcar_coordenador_exportado(coord.id_savic, geoentcod_coord_ativo)
                coord.flagexportado = "Sim"
                coord.codigo_apolo = geoentcod_coord_ativo
                resultado.total_coordenadores_processados += 1

                # ---------------------------------------------------------
                # 2. Grupos de Oração vinculados a este Coordenador
                # ---------------------------------------------------------
                grupos_do_coord = grupos_por_coord.get(str(coord.id_savic).strip(), [])
                if not grupos_do_coord and not grupos_fornecidos_explicitamente:
                    grupos_do_coord = self._repo.buscar_grupos_por_coordenador(coord.id_savic)

                for grupo in grupos_do_coord:
                    if grupo.gocodigo and grupo.gocodigo in grupos_processados_set:
                        continue

                    passo_atual += 1
                    if callback_progresso:
                        callback_progresso(
                            passo_atual,
                            total_passos,
                            f"Exportando Grupo: {grupo.nome_grupo} ({passo_atual}/{total_passos})..."
                        )

                    nome_g = (grupo.nome_grupo or "").strip()
                    cidcod_g = grupo.geocidcod or cidcod
                    if (not cidcod_g or cidcod_g == "00000001") and grupo.cidade and grupo.uf:
                        c_cod = self.resolver_codigo_cidade(grupo.cidade, grupo.uf)
                        if c_cod:
                            cidcod_g = c_cod

                    geoentcod_grupo_existente = None
                    if grupo.codigo_apolo and grupo.codigo_apolo not in ("0", ""):
                        try:
                            cur.execute("SELECT TOP 1 geoentcod FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE geoentcod = ?", [grupo.codigo_apolo.strip()])
                            row_gchk = cur.fetchone()
                            if row_gchk and row_gchk[0]:
                                geoentcod_grupo_existente = str(row_gchk[0]).strip()
                        except Exception:
                            pass

                    if not geoentcod_grupo_existente:
                        geoentcod_grupo_existente = self._repo.buscar_geoentcod_por_nome_e_cidade(nome_g, cidcod_g)

                    end_local = grupo.local_reuniao or grupo.endereco or ""
                    comp_local = grupo.tipo_local or grupo.complemento or ""

                    # 2.1 USER_geoapolo_entidade (Grupo de Oração)
                    is_mandato_vencido = eh_mandato_vencido(coord.mandato_indeterminado, coord.data_fim)

                    if geoentcod_grupo_existente:
                        obs_g_upd = None
                        if is_mandato_vencido:
                            try:
                                cur.execute("SELECT TOP 1 geoobservacoes FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE geoentcod = ?", [geoentcod_grupo_existente])
                                row_obs = cur.fetchone()
                                obs_existente = str(row_obs[0] or "") if row_obs else ""
                                obs_g_upd = aplicar_pendencia_mandato_vencido(obs_existente)[:200]
                            except Exception:
                                obs_g_upd = aplicar_pendencia_mandato_vencido("")[:200]

                        sql_upd_g = """
                            UPDATE USER_geoapolo_entidade SET
                                geoentnome = CASE WHEN ISNULL(NULLIF(?, ''), '') <> '' THEN ? ELSE geoentnome END,
                                geoentnomefantasia = ISNULL(NULLIF(geoentnomefantasia, ''), ?),
                                tipolograd = ISNULL(NULLIF(tipolograd, 0), 1),
                                geotipotratcod = ISNULL(NULLIF(geotipotratcod, ''), '0001'),
                                geoentender = CASE WHEN ISNULL(NULLIF(?, ''), '') <> '' THEN ? ELSE geoentender END,
                                geoenderno = ISNULL(NULLIF(geoenderno, ''), 'S/N'),
                                geoentendercomp = CASE WHEN ISNULL(NULLIF(?, ''), '') <> '' THEN ? ELSE geoentendercomp END,
                                geocidcod = ?,
                                cidcodapolo = ?,
                                geotipofj = ISNULL(NULLIF(geotipofj, ''), 'Jurídica'),
                                geofalecido = ISNULL(NULLIF(geofalecido, ''), 'N'),
                                geoentloccobrancaomesmo = ISNULL(NULLIF(geoentloccobrancaomesmo, ''), 'Sim'),
                                geoentlocentregaomesmo = ISNULL(NULLIF(geoentlocentregaomesmo, ''), 'Sim'),
                                geoenttransporteomesmo = ISNULL(NULLIF(geoenttransporteomesmo, ''), 'Sim'),
                                geoobservacoes = CASE WHEN ? IS NOT NULL THEN ? ELSE geoobservacoes END,
                                geoentdatacad = ISNULL(geoentdatacad, ?),
                                geoentdesdedata = ISNULL(geoentdesdedata, ?)
                            WHERE geoentcod = ?
                        """
                        cur.execute(sql_upd_g, [
                            nome_g, nome_g,
                            nome_g,
                            end_local, end_local,
                            comp_local, comp_local,
                            cidcod_g,
                            cidcod_g,
                            obs_g_upd, obs_g_upd,
                            hoje_str,
                            hoje_str,
                            geoentcod_grupo_existente
                        ])
                        geoentcod_g_ativo = geoentcod_grupo_existente
                        resultado.total_grupos_atualizados += 1
                    else:
                        novo_geoentcod_g = geoapolo_configcod(empresa_codigo, "USER_geoapolo_entidade", "Sim", conn)
                        geoentcod_g_ativo = novo_geoentcod_g
                        obs_g_ins = aplicar_pendencia_mandato_vencido("")[:200] if is_mandato_vencido else None

                        sql_ins_g = """
                            INSERT INTO USER_geoapolo_entidade (
                                geoentcod, geotipotratcod, geoentnome, geoentnomefantasia, tipolograd,
                                geoentender, geoenderno, geoentendercomp, geoentbair, geoobservacoes, geoentdatacad,
                                geoentdesdedata, geoentcep, geocidcod, geoentgenero, geotipofj,
                                geofalecido, cidcodapolo,
                                geoentloccobrancaomesmo, geoentlocentregaomesmo, geoenttransporteomesmo
                            ) VALUES (
                                ?, '0001', ?, ?, 1,
                                ?, 'S/N', ?, '', ?, ?,
                                ?, ?, ?, 'M', 'Jurídica',
                                'N', ?,
                                'Sim', 'Sim', 'Sim'
                            )
                        """
                        cur.execute(sql_ins_g, [
                            novo_geoentcod_g,
                            nome_g,
                            nome_g,
                            end_local,
                            comp_local,
                            obs_g_ins,
                            hoje_str,
                            hoje_str,
                            limpar_formatacao(grupo.cep),
                            cidcod_g,
                            cidcod_g
                        ])
                        resultado.total_grupos_inseridos += 1

                    # 2.2 USER_geoapolo_entcateg: Categoria 02.001 e 08.009 (Loja)
                    self._repo.garantir_categoria_entidade(geoentcod_g_ativo, "02.001")
                    self._repo.garantir_categoria_entidade(geoentcod_g_ativo, "08.009")
                    resultado.total_categorias_vinculadas += 2

                    # USER_geoapolo_origens_entidade: Origem '013.007' (SAVIC)
                    self._repo.garantir_origem_entidade(geoentcod_g_ativo, "013.007", conn=conn)

                    # 2.3 USER_geoapolo_entidade_ativecon: 94.91-0
                    cur.execute(sql_ativecon, [geoentcod_g_ativo, geoentcod_g_ativo])

                    # 2.4 USER_geoapolo_entidade_endereco_adicionais: Principal
                    if end_local:
                        try:
                            tipo_lograd_g = self._obter_tipologradabrev_valido(cur)
                            sql_end_g = """
                                IF NOT EXISTS (
                                    SELECT 1 FROM USER_geoapolo_entidade_endereco_adicionais WITH (NOLOCK)
                                    WHERE geoentcod = ? AND tipo_endereco = 'Principal'
                                )
                                BEGIN
                                    INSERT INTO USER_geoapolo_entidade_endereco_adicionais (
                                        geoentcod, tipo_endereco, tipologradabrev, endereco, numero, complemento, bairro, geocidcod
                                    ) VALUES (?, 'Principal', ?, ?, NULL, ?, '', ?);
                                END
                                ELSE
                                BEGIN
                                    UPDATE USER_geoapolo_entidade_endereco_adicionais
                                    SET tipologradabrev = ?, endereco = ?, complemento = ?, geocidcod = ?
                                    WHERE geoentcod = ? AND tipo_endereco = 'Principal';
                                END;
                            """
                            cur.execute(sql_end_g, [
                                geoentcod_g_ativo, geoentcod_g_ativo,
                                tipo_lograd_g,
                                end_local[:60], comp_local[:45], cidcod_g,
                                tipo_lograd_g,
                                end_local[:60], comp_local[:45], cidcod_g,
                                geoentcod_g_ativo
                            ])
                        except Exception as exc_end_g:
                            logger.warning("Aviso ao salvar endereço principal do grupo %s: %s", grupo.gonome, exc_end_g)

                    # 2.5 USER_geoapolo_entidade_contato: Vínculo Grupo <-> Coordenador
                    sql_contato = """
                        IF NOT EXISTS (
                            SELECT 1 FROM USER_geoapolo_entidade_contato WITH (NOLOCK)
                            WHERE geoentcod = ? AND EntCodContato = ?
                        )
                        BEGIN
                            INSERT INTO USER_geoapolo_entidade_contato (
                                geoentcod, entCod, EntCodContato, TipoTratCod, CargoCodEstr, EntContatoCategPrinc,
                                EntContatoEMail, EntContatoTelefone, EntContatoCelular, CidCod, data_vigencia_inicial, data_vigencia_final
                            ) VALUES (
                                ?, NULL, ?, ?, 'Coordenador', 'S',
                                ?, ?, ?, ?, ?, ?
                            );
                        END
                        ELSE
                        BEGIN
                            UPDATE USER_geoapolo_entidade_contato SET
                                TipoTratCod = ?,
                                CargoCodEstr = 'Coordenador',
                                EntContatoCategPrinc = 'S',
                                EntContatoEMail = ?,
                                EntContatoTelefone = ?,
                                EntContatoCelular = ?,
                                CidCod = ?,
                                data_vigencia_inicial = ?,
                                data_vigencia_final = ?
                            WHERE geoentcod = ? AND EntCodContato = ?;
                        END;
                    """
                    cur.execute(sql_contato, [
                        geoentcod_g_ativo, geoentcod_coord_ativo,
                        geoentcod_g_ativo, geoentcod_coord_ativo, tipo_trat,
                        coord.email or "", coord.telefone_fixo or "", coord.celular or "", cidcod, dt_ini_str, dt_fim_str,
                        tipo_trat,
                        coord.email or "", coord.telefone_fixo or "", coord.celular or "", cidcod, dt_ini_str, dt_fim_str,
                        geoentcod_g_ativo, geoentcod_coord_ativo
                    ])

                    # 2.6 Marca Grupo como exportado no banco
                    self._repo.marcar_grupo_exportado(grupo.gocodigo, geoentcod_g_ativo)
                    grupo.flagexportado = "Sim"
                    grupo.codigo_apolo = geoentcod_g_ativo
                    resultado.total_grupos_processados += 1
                    grupos_processados_set.add(grupo.gocodigo)

                conn.commit()

            except Exception as exc:
                conn.rollback()
                err = f"Erro ao exportar Coordenador {coord.coordenador} (ID {coord.id_savic}): {exc}"
                logger.error(err)
                resultado.erros.append(err)

        # -------------------------------------------------------------
        # 3. Grupos restantes (caso tenham sido informados sem coordenador associado)
        # -------------------------------------------------------------
        for grupo in grupos:
            if grupo.gocodigo and grupo.gocodigo in grupos_processados_set:
                continue

            passo_atual += 1
            if callback_progresso:
                callback_progresso(
                    passo_atual,
                    total_passos,
                    f"Exportando Grupo de Oração: {grupo.nome_grupo} ({passo_atual}/{total_passos})..."
                )

            nome_g = (grupo.nome_grupo or "").strip()
            cidcod_g = grupo.geocidcod or "00000001"
            if (not cidcod_g or cidcod_g == "00000001") and grupo.cidade and grupo.uf:
                c_cod = self.resolver_codigo_cidade(grupo.cidade, grupo.uf)
                if c_cod:
                    cidcod_g = c_cod

            geoentcod_grupo_existente = self._repo.buscar_geoentcod_por_nome_e_cidade(nome_g, cidcod_g)
            end_local = grupo.local_reuniao or grupo.endereco or ""
            comp_local = grupo.tipo_local or grupo.complemento or ""

            try:
                is_mandato_vencido = False
                if grupo.cadastroid_coordenador:
                    try:
                        cur.execute("""
                            SELECT TOP 1 mandatoindeterminado, datafimcoordenacao
                              FROM USER_geoapolo_coordenadores_grupodeoracao WITH (NOLOCK)
                             WHERE cadastroid_coordenador = ?
                        """, [grupo.cadastroid_coordenador])
                        row_m = cur.fetchone()
                        if row_m:
                            is_mandato_vencido = eh_mandato_vencido(row_m[0], row_m[1])
                    except Exception:
                        pass

                if geoentcod_grupo_existente:
                    obs_g_upd = None
                    if is_mandato_vencido:
                        try:
                            cur.execute("SELECT TOP 1 geoobservacoes FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE geoentcod = ?", [geoentcod_grupo_existente])
                            row_obs = cur.fetchone()
                            obs_existente = str(row_obs[0] or "") if row_obs else ""
                            obs_g_upd = aplicar_pendencia_mandato_vencido(obs_existente)[:200]
                        except Exception:
                            obs_g_upd = aplicar_pendencia_mandato_vencido("")[:200]

                    sql_upd_g = """
                        UPDATE USER_geoapolo_entidade SET
                            geoentnome = CASE WHEN ISNULL(NULLIF(?, ''), '') <> '' THEN ? ELSE geoentnome END,
                            geoentnomefantasia = ISNULL(NULLIF(geoentnomefantasia, ''), ?),
                            tipolograd = ISNULL(NULLIF(tipolograd, 0), 1),
                            geotipotratcod = ISNULL(NULLIF(geotipotratcod, ''), '0001'),
                            geoentender = CASE WHEN ISNULL(NULLIF(?, ''), '') <> '' THEN ? ELSE geoentender END,
                            geoenderno = ISNULL(NULLIF(geoenderno, ''), 'S/N'),
                            geoentendercomp = CASE WHEN ISNULL(NULLIF(?, ''), '') <> '' THEN ? ELSE geoentendercomp END,
                            geocidcod = ?,
                            cidcodapolo = ?,
                            geotipofj = ISNULL(NULLIF(geotipofj, ''), 'Jurídica'),
                            geofalecido = ISNULL(NULLIF(geofalecido, ''), 'N'),
                            geoentloccobrancaomesmo = ISNULL(NULLIF(geoentloccobrancaomesmo, ''), 'Sim'),
                            geoentlocentregaomesmo = ISNULL(NULLIF(geoentlocentregaomesmo, ''), 'Sim'),
                            geoenttransporteomesmo = ISNULL(NULLIF(geoenttransporteomesmo, ''), 'Sim'),
                            geoobservacoes = CASE WHEN ? IS NOT NULL THEN ? ELSE geoobservacoes END,
                            geoentdatacad = ISNULL(geoentdatacad, ?),
                            geoentdesdedata = ISNULL(geoentdesdedata, ?)
                        WHERE geoentcod = ?
                    """
                    cur.execute(sql_upd_g, [
                        nome_g, nome_g,
                        nome_g,
                        end_local, end_local,
                        comp_local, comp_local,
                        cidcod_g,
                        cidcod_g,
                        obs_g_upd, obs_g_upd,
                        hoje_str,
                        hoje_str,
                        geoentcod_grupo_existente
                    ])
                    geoentcod_g_ativo = geoentcod_grupo_existente
                    resultado.total_grupos_atualizados += 1
                else:
                    novo_geoentcod_g = geoapolo_configcod(empresa_codigo, "USER_geoapolo_entidade", "Sim", conn)
                    geoentcod_g_ativo = novo_geoentcod_g
                    obs_g_ins = aplicar_pendencia_mandato_vencido("")[:200] if is_mandato_vencido else None

                    sql_ins_g = """
                        INSERT INTO USER_geoapolo_entidade (
                            geoentcod, geotipotratcod, geoentnome, geoentnomefantasia, tipolograd,
                            geoentender, geoenderno, geoentendercomp, geoentbair, geoobservacoes, geoentdatacad,
                            geoentdesdedata, geoentcep, geocidcod, geoentgenero, geotipofj,
                            geofalecido, cidcodapolo,
                            geoentloccobrancaomesmo, geoentlocentregaomesmo, geoenttransporteomesmo
                        ) VALUES (
                            ?, '0001', ?, ?, 1,
                            ?, 'S/N', ?, '', ?, ?,
                            ?, ?, ?, 'M', 'Jurídica',
                            'N', ?,
                            'Sim', 'Sim', 'Sim'
                        )
                    """
                    cur.execute(sql_ins_g, [
                        novo_geoentcod_g,
                        nome_g,
                        nome_g,
                        end_local,
                        comp_local,
                        obs_g_ins,
                        hoje_str,
                        hoje_str,
                        limpar_formatacao(grupo.cep),
                        cidcod_g,
                        cidcod_g
                    ])
                    resultado.total_grupos_inseridos += 1

                # Categoria de Grupo de Oração: 02.001 e 08.009 (Loja)
                self._repo.garantir_categoria_entidade(geoentcod_g_ativo, "02.001")
                self._repo.garantir_categoria_entidade(geoentcod_g_ativo, "08.009")
                resultado.total_categorias_vinculadas += 2

                # USER_geoapolo_origens_entidade: Origem '013.007' (SAVIC)
                self._repo.garantir_origem_entidade(geoentcod_g_ativo, "013.007", conn=conn)

                # Atividade econômica: 94.91-0
                cur.execute("""
                    IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_ativecon WITH (NOLOCK) WHERE geoentcod = ?)
                    BEGIN
                        INSERT INTO USER_geoapolo_entidade_ativecon (ativeconcodestr, geoentcod)
                        VALUES ('94.91-0', ?);
                    END;
                """, [geoentcod_g_ativo, geoentcod_g_ativo])

                # Endereço adicional: Principal
                if end_local:
                    try:
                        tipo_lograd_ge = self._obter_tipologradabrev_valido(cur)
                        cur.execute("""
                            IF NOT EXISTS (
                                SELECT 1 FROM USER_geoapolo_entidade_endereco_adicionais WITH (NOLOCK)
                                WHERE geoentcod = ? AND tipo_endereco = 'Principal'
                            )
                            BEGIN
                                INSERT INTO USER_geoapolo_entidade_endereco_adicionais (
                                    geoentcod, tipo_endereco, tipologradabrev, endereco, numero, complemento, bairro, geocidcod
                                ) VALUES (?, 'Principal', ?, ?, NULL, ?, '', ?);
                            END
                            ELSE
                            BEGIN
                                UPDATE USER_geoapolo_entidade_endereco_adicionais
                                SET tipologradabrev = ?, endereco = ?, complemento = ?, geocidcod = ?
                                WHERE geoentcod = ? AND tipo_endereco = 'Principal';
                            END;
                        """, [
                            geoentcod_g_ativo, geoentcod_g_ativo,
                            tipo_lograd_ge,
                            end_local[:60], comp_local[:45], cidcod_g,
                            tipo_lograd_ge,
                            end_local[:60], comp_local[:45], cidcod_g,
                            geoentcod_g_ativo
                        ])
                    except Exception as exc_end_ge:
                        logger.warning("Aviso ao salvar endereço principal do grupo existente %s: %s", grupo.gonome, exc_end_ge)

                # Marca grupo como exportado no banco
                self._repo.marcar_grupo_exportado(grupo.gocodigo, geoentcod_g_ativo)
                grupo.flagexportado = "Sim"
                grupo.codigo_apolo = geoentcod_g_ativo
                resultado.total_grupos_processados += 1
                conn.commit()

            except Exception as exc:
                conn.rollback()
                err = f"Erro ao exportar Grupo {grupo.nome_grupo} (Cód {grupo.gocodigo}): {exc}"
                logger.error(err)
                resultado.erros.append(err)

        resultado.sucesso = (len(resultado.erros) == 0)
        resultado.mensagem = (
            f"Exportação para Entidades concluída! "
            f"Coordenadores (02.001.0006): {resultado.total_coordenadores_inseridos} inseridos, "
            f"{resultado.total_coordenadores_atualizados} atualizados. "
            f"Grupos de Oração (02.001): {resultado.total_grupos_inseridos} inseridos, "
            f"{resultado.total_grupos_atualizados} atualizados. "
            f"Total categorias vinculadas: {resultado.total_categorias_vinculadas}."
        )
        return resultado

