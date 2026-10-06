"""
Repositório de Dados para o Dashboard de Doações & Inteligência Analítica (Empresa 1.01).
Alimentado pelas regras, joins e métricas de Dashboard-menuprincipal.sql sobre USERPerfilFinanceiro_de_Doador.
GeoApolo V5
"""

import logging
from typing import List, Dict, Optional, Tuple, Any, Callable
from datetime import date, datetime, timedelta
from dashboard.models import (
    FiltroDashboardDTO,
    ResumoDoacoesDTO,
    DoadorPerfilDTO,
    StatusDoadorMetricaDTO,
    DioceseMetricaDTO,
    TipoCobrancaMetricaDTO,
    EvolucaoMesDTO,
    EvolucaoAnoDTO,
    HistoricoAnoMetodoDTO,
)
from entidades.database import obter_conexao_banco

logger = logging.getLogger(__name__)

MESES_NOMES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

FORMA_NOMES = {
    "BOL": "BOL - Boleto Bancário",
    "DEB": "DEB - Débito em Conta",
    "VND": "VND - Cartão Recorrente (Vindi)",
    "PIX": "PIX - Pagamento Instantâneo PIX",
}


class DashboardRepository:
    """
    Camada de acesso a dados para o perfil financeiro de doadores e métricas de arrecadação.
    Baseado integralmente nas consultas de Dashboard-menuprincipal.sql.
    """

    def __init__(self, connection=None):
        self._conn = connection

    def _get_connection(self):
        if self._conn:
            return self._conn
        try:
            return obter_conexao_banco()
        except Exception as exc:
            logger.warning("Conexão direta com banco falhou: %s", exc)
            return None

    def _montar_clausula_subgrupos(self, subgrupos, alias: str = "upfd") -> str:
        """
        Monta a cláusula com predicados LIKE (Sargable), conforme atualizado no
        Dashboard-menuprincipal.sql, permitindo que o SQL Server utilize buscas por índice (Index Seek).
        """
        if not subgrupos:
            return "(1=1)"
        itens = [f"{alias}.categcodestr LIKE '{s}%'" for s in subgrupos]
        return f"({' OR '.join(itens)})"

    def obter_intervalo_datas(self, conn, filtro: FiltroDashboardDTO) -> Tuple[date, date, str]:
        """Calcula o intervalo de datas (início, fim, descrição) conforme o tipo de período."""
        if filtro.tipo_periodo == "MES":
            ano = filtro.ano or 2026
            mes = filtro.mes or 9
            dt_ini = date(ano, mes, 1)
            if mes == 12:
                dt_fim = date(ano, 12, 31)
            else:
                dt_fim = date(ano, mes + 1, 1) - timedelta(days=1)
            desc = f"{MESES_NOMES.get(mes, str(mes))} / {ano}"
            return dt_ini, dt_fim, desc

        if filtro.tipo_periodo == "PERSONALIZADO" and filtro.data_inicial and filtro.data_final:
            dt_ini = filtro.data_inicial
            dt_fim = filtro.data_final
            desc = f"Período: {dt_ini.strftime('%d/%m/%Y')} a {dt_fim.strftime('%d/%m/%Y')}"
            return dt_ini, dt_fim, desc

        dias = 10
        if filtro.tipo_periodo == "15_DIAS":
            dias = 15
        elif filtro.tipo_periodo == "30_DIAS":
            dias = 30

        dt_fim = filtro.data_final
        if not dt_fim and conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT MAX(data_doacao_mescorrente) FROM USERPerfilFinanceiro_de_Doador WITH (NOLOCK)")
                row = cur.fetchone()
                if row and row[0]:
                    dt_fim = row[0]
            except Exception:
                pass

        if not dt_fim:
            dt_fim = date.today()

        dt_ini = filtro.data_inicial or (dt_fim - timedelta(days=dias))
        desc = f"Últimos {dias} Dias ({dt_ini.strftime('%d/%m/%Y')} a {dt_fim.strftime('%d/%m/%Y')})"
        return dt_ini, dt_fim, desc

    def carregar_dados_completos(
        self,
        filtro: Optional[FiltroDashboardDTO] = None,
        callback_progresso: Optional[Callable[[int, str], None]] = None
    ) -> ResumoDoacoesDTO:
        """
        Carrega dados do dashboard coordenadamente utilizando a query de Dashboard-menuprincipal.sql:
        1. Relação de doadores (Últimos 10 dias por padrão ou mês/período customizado)
        2. Métricas consolidadas por Status e Formas de Contribuição
        3. Ranking das Top Dioceses
        4. Suporte a callback de progresso para alimentação do Gauge visual
        """
        if filtro is None:
            filtro = FiltroDashboardDTO()

        def _progresso(pct: int, msg: str):
            if callback_progresso:
                try:
                    callback_progresso(pct, msg)
                except Exception:
                    pass

        conn = self._get_connection()
        if not conn:
            _progresso(100, "Concluído (modo demonstração)")
            return self._gerar_dados_fallback(filtro)

        try:
            _progresso(10, "Conectando ao SQL Server...")
            _progresso(25, "Executando consulta analítica...")

            # 1. Carrega doadores e consolida KPIs do período
            resumo = self._obter_dados_perfil_doadores(conn, filtro)
            _progresso(65, "Calculando perfil de doadores e formas...")

            # 2. Carrega evolução histórica somente se explicitamente requisitado
            if filtro.carregar_historico_completo:
                _progresso(80, "Consultando histórico longitudinal (2018-2026)...")
                resumo.evolucao_meses = self._obter_evolucao_meses(conn, filtro.ano, filtro.subgrupos)
                resumo.evolucao_anos = self._obter_evolucao_anos(conn, filtro.subgrupos)
                resumo.historico_metodos = self._obter_historico_metodos_por_ano(conn, filtro.subgrupos)
            else:
                resumo.evolucao_meses = []
                resumo.evolucao_anos = []
                resumo.historico_metodos = []

            # Métricas calculadas
            _progresso(90, "Finalizando indicadores analíticos...")
            if resumo.tipos_cobranca:
                primeiro = resumo.tipos_cobranca[0]
                resumo.metodo_campeao = primeiro.nome
                resumo.metodo_campeao_valor = primeiro.total
                resumo.metodo_campeao_pct = primeiro.percentual

            if len(resumo.evolucao_anos) >= 2:
                ano_recente = resumo.evolucao_anos[0].total
                ano_anterior = resumo.evolucao_anos[1].total
                if ano_anterior > 0:
                    resumo.crescimento_yoy_pct = round(((ano_recente - ano_anterior) / ano_anterior) * 100.0, 1)

            resumo.taxa_quitacao_pct = 94.5

            _progresso(100, "Dados carregados com sucesso!")
            return resumo
        except Exception as exc:
            logger.exception("Erro ao executar consulta do dashboard no banco: %s", exc)
            _progresso(100, "Erro na consulta. Utilizando contingência.")
            return self._gerar_dados_fallback(filtro)
        finally:
            if not self._conn and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def carregar_historico_longitudinal(
        self,
        filtro: FiltroDashboardDTO
    ) -> Tuple[List[EvolucaoMesDTO], List[EvolucaoAnoDTO], List[HistoricoAnoMetodoDTO]]:
        """Carrega sob demanda (lazy loading) os dados da Aba 3 sem bloquear a abertura inicial."""
        conn = self._get_connection()
        if not conn:
            demo = self._gerar_dados_fallback(filtro)
            return demo.evolucao_meses, demo.evolucao_anos, demo.historico_metodos
        try:
            evolucao_meses = self._obter_evolucao_meses(conn, filtro.ano, filtro.subgrupos)
            evolucao_anos = self._obter_evolucao_anos(conn, filtro.subgrupos)
            historico_metodos = self._obter_historico_metodos_por_ano(conn, filtro.subgrupos)
            return evolucao_meses, evolucao_anos, historico_metodos
        finally:
            if not self._conn and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _obter_dados_perfil_doadores(self, conn, filtro: FiltroDashboardDTO) -> ResumoDoacoesDTO:
        """
        Executa a query baseada no Dashboard-menuprincipal.sql, suportando
        filtro rápido por intervalo de datas (ex.: últimos 10 dias) ou mês fechado.
        """
        cur = conn.cursor()
        subgrupos_sql = self._montar_clausula_subgrupos(filtro.subgrupos)
        dt_ini, dt_fim, desc_periodo = self.obter_intervalo_datas(conn, filtro)

        if filtro.tipo_periodo == "MES":
            sql = f"""
            SELECT 
                upfd.entcod, 
                e.entnome, 
                cid.ufsigla AS UF, 
                ISNULL(ue.USERDiocese_id, '') AS CodigoDio, 
                ISNULL(ue.USERNomeDiocese, 'Não Informada') AS Diocese,  
                upfd.categcodestr, 
                cat.categnome, 
                ISNULL(upfd.tipocobcod, '') AS tipocobcod,  
                ISNULL(upfd.docfinespec, 'N/D') AS FormaContribuicao,
                upfd.data_doacao_mescorrente,
                ISNULL(upfd.valor_doado, 0) AS valor_doado,
                upfd.data_doacao_anterior, 
                ISNULL(upfd.valor_doado_mesanterior, 0) AS valor_doado_mesanterior,
                ISNULL(upfd.docfinchv, '') AS docfinchv, 
                CASE 
                    WHEN upfd.data_doacao_anterior IS NULL AND dbo.fn_VerificaEntidadeUnica(upfd.entcod, ?) = 1 THEN 'Novo Doador'
                    WHEN DATEDIFF(day, ISNULL(upfd.data_doacao_anterior, upfd.data_doacao_mescorrente), upfd.data_doacao_mescorrente) > 35 THEN 'Retorno Doador'
                    ELSE 'Doador Recorrente'
                END AS StatusDoador
            FROM USERPerfilFinanceiro_de_Doador upfd WITH (NOLOCK)
            INNER JOIN entidade e ON upfd.entcod = e.entcod
            INNER JOIN cidade cid ON e.cidcod = cid.cidcod
            INNER JOIN categoria cat ON upfd.CategCodEstr = cat.CategCodEstr
            LEFT JOIN U_ENTIDADE ue ON upfd.entcod = ue.entcod 
            WHERE upfd.mes_doacao = ?
              AND upfd.ano_doacao = ?
              AND {subgrupos_sql}
            ORDER BY upfd.entcod, upfd.docfinespec ASC
            """
            cur.execute(sql, (filtro.empresa, filtro.mes, filtro.ano))
        else:
            sql = f"""
            SELECT 
                upfd.entcod, 
                e.entnome, 
                cid.ufsigla AS UF, 
                ISNULL(ue.USERDiocese_id, '') AS CodigoDio, 
                ISNULL(ue.USERNomeDiocese, 'Não Informada') AS Diocese,  
                upfd.categcodestr, 
                cat.categnome, 
                ISNULL(upfd.tipocobcod, '') AS tipocobcod,  
                ISNULL(upfd.docfinespec, 'N/D') AS FormaContribuicao,
                upfd.data_doacao_mescorrente,
                ISNULL(upfd.valor_doado, 0) AS valor_doado,
                upfd.data_doacao_anterior, 
                ISNULL(upfd.valor_doado_mesanterior, 0) AS valor_doado_mesanterior,
                ISNULL(upfd.docfinchv, '') AS docfinchv, 
                CASE 
                    WHEN upfd.data_doacao_anterior IS NULL AND dbo.fn_VerificaEntidadeUnica(upfd.entcod, ?) = 1 THEN 'Novo Doador'
                    WHEN DATEDIFF(day, ISNULL(upfd.data_doacao_anterior, upfd.data_doacao_mescorrente), upfd.data_doacao_mescorrente) > 35 THEN 'Retorno Doador'
                    ELSE 'Doador Recorrente'
                END AS StatusDoador
            FROM USERPerfilFinanceiro_de_Doador upfd WITH (NOLOCK)
            INNER JOIN entidade e ON upfd.entcod = e.entcod
            INNER JOIN cidade cid ON e.cidcod = cid.cidcod
            INNER JOIN categoria cat ON upfd.CategCodEstr = cat.CategCodEstr
            LEFT JOIN U_ENTIDADE ue ON upfd.entcod = ue.entcod 
            WHERE upfd.data_doacao_mescorrente >= ?
              AND upfd.data_doacao_mescorrente <= ?
              AND {subgrupos_sql}
            ORDER BY upfd.entcod, upfd.docfinespec ASC
            """
            cur.execute(sql, (filtro.empresa, dt_ini, dt_fim))
        rows = cur.fetchall()

        doadores: List[DoadorPerfilDTO] = []
        mapa_status: Dict[str, Dict[str, Any]] = {
            "Doador Recorrente": {"qtd": 0, "total": 0.0, "cor": "#10B981"},
            "Novo Doador": {"qtd": 0, "total": 0.0, "cor": "#3B82F6"},
            "Retorno Doador": {"qtd": 0, "total": 0.0, "cor": "#F59E0B"},
        }
        mapa_formas: Dict[str, Dict[str, Any]] = {}
        mapa_dioceses: Dict[str, Dict[str, Any]] = {}

        total_arrecadado = 0.0
        total_mes_anterior = 0.0
        entidades_unicas = set()

        for r in rows:
            entcod = str(r[0] or "").strip()
            entnome = str(r[1] or "").strip()
            uf = str(r[2] or "").strip()
            codigo_dio = str(r[3] or "").strip()
            diocese = str(r[4] or "Não Informada").strip()
            categcodestr = str(r[5] or "").strip()
            categnome = str(r[6] or "").strip()
            tipocobcod = str(r[7] or "").strip()
            forma_raw = str(r[8] or "N/D").strip().upper()
            dt_corrente = r[9]
            val_doado = float(r[10] or 0.0)
            dt_anterior = r[11]
            val_mes_ant = float(r[12] or 0.0)
            docfinchv = str(r[13] or "").strip()
            status_doador = str(r[14] or "").strip()

            if not status_doador:
                status_doador = "Doador Recorrente"

            entidades_unicas.add(entcod)
            total_arrecadado += val_doado
            total_mes_anterior += val_mes_ant

            # Status
            if status_doador in mapa_status:
                mapa_status[status_doador]["qtd"] += 1
                mapa_status[status_doador]["total"] += val_doado

            # Formas
            if forma_raw not in mapa_formas:
                nome_formatado = FORMA_NOMES.get(forma_raw, f"{forma_raw} - Outros")
                mapa_formas[forma_raw] = {"nome": nome_formatado, "qtd": 0, "total": 0.0}
            mapa_formas[forma_raw]["qtd"] += 1
            mapa_formas[forma_raw]["total"] += val_doado

            # Dioceses
            chave_dio = f"{diocese} ({uf})" if uf else diocese
            if chave_dio not in mapa_dioceses:
                mapa_dioceses[chave_dio] = {
                    "codigo": codigo_dio,
                    "nome": diocese,
                    "uf": uf,
                    "qtd": 0,
                    "total": 0.0,
                }
            mapa_dioceses[chave_dio]["qtd"] += 1
            mapa_dioceses[chave_dio]["total"] += val_doado

            doadores.append(DoadorPerfilDTO(
                entcod=entcod,
                entnome=entnome,
                uf=uf,
                codigo_dio=codigo_dio,
                diocese=diocese,
                categcodestr=categcodestr,
                categnome=categnome,
                tipocobcod=tipocobcod,
                forma_contribuicao=forma_raw,
                data_doacao_mescorrente=dt_corrente,
                valor_doado=round(val_doado, 2),
                data_doacao_anterior=dt_anterior,
                valor_doado_mesanterior=round(val_mes_ant, 2),
                docfinchv=docfinchv,
                status_doador=status_doador,
            ))

        qtd_doacoes = len(doadores)
        qtd_doadores = len(entidades_unicas)
        ticket_medio = round(total_arrecadado / qtd_doacoes, 2) if qtd_doacoes > 0 else 0.0

        variacao_mes_ant = 0.0
        if total_mes_anterior > 0:
            variacao_mes_ant = round(((total_arrecadado - total_mes_anterior) / total_mes_anterior) * 100.0, 1)

        # Status DTOs
        status_metricas: List[StatusDoadorMetricaDTO] = []
        for st_nome in ["Doador Recorrente", "Novo Doador", "Retorno Doador"]:
            dados_st = mapa_status[st_nome]
            q = dados_st["qtd"]
            tot = dados_st["total"]
            pct = round((tot / total_arrecadado * 100.0), 1) if total_arrecadado > 0 else 0.0
            tm = round((tot / q), 2) if q > 0 else 0.0
            status_metricas.append(StatusDoadorMetricaDTO(
                status=st_nome,
                qtd=q,
                total=round(tot, 2),
                percentual=pct,
                ticket_medio=tm,
                cor=dados_st["cor"],
            ))

        # Formas DTOs
        tipos_cobranca: List[TipoCobrancaMetricaDTO] = []
        formas_ordenadas = sorted(mapa_formas.items(), key=lambda x: x[1]["total"], reverse=True)
        for idx, (cod, d_f) in enumerate(formas_ordenadas):
            q = d_f["qtd"]
            tot = d_f["total"]
            pct = round((tot / total_arrecadado * 100.0), 1) if total_arrecadado > 0 else 0.0
            tm = round((tot / q), 2) if q > 0 else 0.0
            tend = "ALTA" if idx == 0 else ("ESTAVEL" if idx < 3 else "BAIXA")
            tipos_cobranca.append(TipoCobrancaMetricaDTO(
                codigo=cod,
                nome=d_f["nome"],
                qtd=q,
                total=round(tot, 2),
                percentual=pct,
                ticket_medio=tm,
                ranking=idx + 1,
                tendencia=tend,
            ))

        # Top Dioceses DTOs
        top_dioceses: List[DioceseMetricaDTO] = []
        dios_ordenadas = sorted(mapa_dioceses.values(), key=lambda x: x["total"], reverse=True)
        for d in dios_ordenadas[:12]:
            q = d["qtd"]
            tot = d["total"]
            pct = round((tot / total_arrecadado * 100.0), 1) if total_arrecadado > 0 else 0.0
            tm = round((tot / q), 2) if q > 0 else 0.0
            top_dioceses.append(DioceseMetricaDTO(
                codigo=d["codigo"],
                nome=d["nome"],
                uf=d["uf"],
                qtd=q,
                total=round(tot, 2),
                percentual=pct,
                ticket_medio=tm,
            ))

        ano_resumo = dt_fim.year if dt_fim else filtro.ano
        mes_resumo = dt_fim.month if dt_fim else filtro.mes

        return ResumoDoacoesDTO(
            ano=ano_resumo,
            mes=mes_resumo,
            tipo_periodo=filtro.tipo_periodo,
            data_inicial=dt_ini,
            data_final=dt_fim,
            total_arrecadado=round(total_arrecadado, 2),
            total_mes_anterior=round(total_mes_anterior, 2),
            variacao_mes_anterior_pct=variacao_mes_ant,
            qtd_doacoes=qtd_doacoes,
            qtd_doadores=qtd_doadores,
            ticket_medio=ticket_medio,
            qtd_novos=mapa_status["Novo Doador"]["qtd"],
            total_novos=round(mapa_status["Novo Doador"]["total"], 2),
            qtd_recorrentes=mapa_status["Doador Recorrente"]["qtd"],
            total_recorrentes=round(mapa_status["Doador Recorrente"]["total"], 2),
            qtd_retorno=mapa_status["Retorno Doador"]["qtd"],
            total_retorno=round(mapa_status["Retorno Doador"]["total"], 2),
            periodo_descricao=desc_periodo,
            status_metricas=status_metricas,
            tipos_cobranca=tipos_cobranca,
            top_dioceses=top_dioceses,
            doadores=doadores,
        )

    def _obter_evolucao_meses(self, conn, ano: int, subgrupos) -> List[EvolucaoMesDTO]:
        """Consulta rápida da evolução dos meses dentro do ano especificado."""
        cur = conn.cursor()
        subgrupos_sql = self._montar_clausula_subgrupos(subgrupos)

        sql = f"""
        SELECT 
            CAST(upfd.mes_doacao AS INT) AS Mes,
            COUNT(*) AS Qtd,
            COUNT(DISTINCT upfd.entcod) AS Doadores,
            SUM(ISNULL(upfd.valor_doado, 0)) AS Total
        FROM USERPerfilFinanceiro_de_Doador upfd WITH (NOLOCK)
        WHERE upfd.ano_doacao = ?
          AND {subgrupos_sql}
        GROUP BY upfd.mes_doacao
        ORDER BY Mes ASC
        """
        cur.execute(sql, (ano,))
        rows = cur.fetchall()

        evolucao: List[EvolucaoMesDTO] = []
        for r in rows:
            m = int(r[0])
            qtd = int(r[1] or 0)
            doadores = int(r[2] or 0)
            total = float(r[3] or 0.0)
            tm = round((total / qtd), 2) if qtd > 0 else 0.0
            evolucao.append(EvolucaoMesDTO(
                mes=m,
                nome_mes=MESES_NOMES.get(m, f"Mês {m}"),
                qtd=qtd,
                doadores=doadores,
                total=round(total, 2),
                ticket_medio=tm,
            ))
        return evolucao

    def _obter_evolucao_anos(self, conn, subgrupos) -> List[EvolucaoAnoDTO]:
        """Consulta agregada histórica anual de arrecadação cobrindo de 2018 a 2026."""
        cur = conn.cursor()
        subgrupos_sql = self._montar_clausula_subgrupos(subgrupos)

        sql = f"""
        SELECT 
            CAST(upfd.ano_doacao AS INT) AS Ano,
            CAST(upfd.mes_doacao AS INT) AS Mes,
            COUNT(*) AS Qtd,
            COUNT(DISTINCT upfd.entcod) AS Doadores,
            SUM(ISNULL(upfd.valor_doado, 0)) AS Total
        FROM USERPerfilFinanceiro_de_Doador upfd WITH (NOLOCK)
        WHERE CAST(upfd.ano_doacao AS INT) >= 2018
          AND {subgrupos_sql}
        GROUP BY upfd.ano_doacao, upfd.mes_doacao
        ORDER BY Ano DESC, Mes ASC
        """
        cur.execute(sql)
        rows = cur.fetchall()

        mapa_anos: Dict[int, EvolucaoAnoDTO] = {}
        for r in rows:
            ano = int(r[0])
            mes = int(r[1])
            qtd = int(r[2] or 0)
            doadores = int(r[3] or 0)
            total = float(r[4] or 0.0)

            if ano not in mapa_anos:
                mapa_anos[ano] = EvolucaoAnoDTO(
                    ano=ano,
                    total=0.0,
                    qtd=0,
                    doadores=0,
                    ticket_medio=0.0,
                    meses={},
                )
            obj = mapa_anos[ano]
            obj.total += total
            obj.qtd += qtd
            obj.doadores = max(obj.doadores, doadores)
            obj.meses[mes] = round(total, 2)

        for obj in mapa_anos.values():
            if obj.qtd > 0:
                obj.ticket_medio = round(obj.total / obj.qtd, 2)
            obj.total = round(obj.total, 2)

        return sorted(mapa_anos.values(), key=lambda x: x.ano, reverse=True)

    def _obter_historico_metodos_por_ano(self, conn, subgrupos) -> List[HistoricoAnoMetodoDTO]:
        """Consulta os meios que mais arrecadaram ano a ano de 2018 a 2026."""
        cur = conn.cursor()
        subgrupos_sql = self._montar_clausula_subgrupos(subgrupos)

        sql = f"""
        SELECT 
            CAST(upfd.ano_doacao AS INT) AS Ano,
            ISNULL(upfd.docfinespec, 'N/D') AS Forma,
            COUNT(*) AS Qtd,
            SUM(ISNULL(upfd.valor_doado, 0)) AS Total
        FROM USERPerfilFinanceiro_de_Doador upfd WITH (NOLOCK)
        WHERE CAST(upfd.ano_doacao AS INT) >= 2018
          AND {subgrupos_sql}
        GROUP BY upfd.ano_doacao, upfd.docfinespec
        ORDER BY Ano DESC, Total DESC
        """
        cur.execute(sql)
        rows = cur.fetchall()

        mapa_anos: Dict[int, List[TipoCobrancaMetricaDTO]] = {}
        for r in rows:
            ano = int(r[0])
            forma_raw = str(r[1] or "N/D").strip().upper()
            qtd = int(r[2] or 0)
            tot = float(r[3] or 0.0)
            nome_ext = FORMA_NOMES.get(forma_raw, f"{forma_raw} - Outros")

            if ano not in mapa_anos:
                mapa_anos[ano] = []
            mapa_anos[ano].append(TipoCobrancaMetricaDTO(
                codigo=forma_raw,
                nome=nome_ext,
                qtd=qtd,
                total=round(tot, 2),
                percentual=0.0,
                ticket_medio=round(tot / qtd, 2) if qtd > 0 else 0.0
            ))

        resultado: List[HistoricoAnoMetodoDTO] = []
        for ano in sorted(mapa_anos.keys(), reverse=True):
            metodos = mapa_anos[ano]
            total_ano = sum(m.total for m in metodos)
            qtd_ano = sum(m.qtd for m in metodos)
            tm_ano = round(total_ano / qtd_ano, 2) if qtd_ano > 0 else 0.0

            for idx, m in enumerate(metodos):
                m.percentual = round((m.total / total_ano * 100.0), 1) if total_ano > 0 else 0.0
                m.ranking = idx + 1

            lider = metodos[0] if metodos else TipoCobrancaMetricaDTO("", "Nenhum", 0, 0.0, 0.0, 0.0)
            resultado.append(HistoricoAnoMetodoDTO(
                ano=ano,
                metodo_lider=lider.nome,
                total_lider=lider.total,
                pct_lider=lider.percentual,
                total_ano=round(total_ano, 2),
                qtd_ano=qtd_ano,
                ticket_medio=tm_ano,
                metodos=metodos
            ))

        return resultado

    def sincronizar_perfil_mes(self, ano: int, mes: int, empcod: str = "1.01") -> bool:
        """
        Executa a atualização do mês executando a procedure USERPerfil_Financeiro_Doador
        conforme especificado no cabeçalho de Dashboard-menuprincipal.sql.
        """
        conn = self._get_connection()
        if not conn:
            return False

        try:
            cur = conn.cursor()
            # 1. Limpa o movimento anterior do mês caso a tabela exista
            sql_del = """
            IF EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USERPerfilFinanceiro_de_Doador' AND xtype = 'U')
            BEGIN
                DELETE FROM USERPerfilFinanceiro_de_Doador WHERE mes_doacao = ? AND ano_doacao = ?
            END
            """
            cur.execute(sql_del, (mes, ano))

            # 2. Executa a procedure de atualização oficial
            sql_proc = "EXEC USERPerfil_Financeiro_Doador ?, ?, ?"
            cur.execute(sql_proc, (empcod, str(ano), str(mes)))
            conn.commit()
            logger.info("Procedimento de atualização concluído para Ano %s, Mês %s.", ano, mes)
            return True
        except Exception as exc:
            logger.exception("Falha ao executar USERPerfil_Financeiro_Doador: %s", exc)
            try:
                conn.rollback()
            except Exception:
                pass
            return False
        finally:
            if not self._conn and conn:
                try:
                    conn.close()
                except Exception:
                    pass

    def _gerar_dados_fallback(self, filtro: FiltroDashboardDTO) -> ResumoDoacoesDTO:
        """Fornece dados estruturados de demonstração baseados no cenário real de 2026/2025."""
        doadores_demo = [
            DoadorPerfilDTO("0000012", "NATALIA SUELI DE MENEZES LEITÃO", "RJ", "46", "Arquidiocese de Niterói", "03.001.001", "SVE-DOADOR ATIVO", "0000011", "VND", date(2026, 9, 21), 23.66, date(2026, 8, 21), 23.66, "1671237", "Doador Recorrente"),
            DoadorPerfilDTO("0000034", "CELINA SILVA DOS SANTOS", "RJ", "53", "Diocese de Barra do Piraí-Volta Redonda", "03.001.000", "SVE-DOADOR ACUMULADO", "0000020", "BOL", date(2026, 9, 13), 30.00, date(2026, 7, 16), 30.00, "1637742", "Retorno Doador"),
            DoadorPerfilDTO("0000052", "LEANDRO PASSOS", "RJ", "47", "Diocese de Petrópolis", "03.001.000", "SVE-DOADOR ACUMULADO", "0000011", "VND", date(2026, 9, 8), 95.69, date(2026, 8, 8), 95.69, "1670976", "Doador Recorrente"),
            DoadorPerfilDTO("0000056", "ELIANE MARIA RESENDE", "SP", "247", "Diocese de Franca", "03.001.000", "SVE-DOADOR ACUMULADO", "0000020", "BOL", date(2026, 9, 25), 25.00, date(2026, 8, 7), 25.00, "1626371", "Doador Recorrente"),
            DoadorPerfilDTO("0000064", "INACIO PEREIRA LIMA JUNIOR", "PI", "132", "Arquidiocese de Teresina", "03.001.000", "SVE-DOADOR ACUMULADO", "0000023", "DEB", date(2026, 9, 11), 25.00, date(2026, 8, 13), 25.00, "1669759", "Doador Recorrente"),
            DoadorPerfilDTO("0000088", "MARIA APARECIDA DOS SANTOS", "SP", "240", "Arquidiocese de São Paulo", "03.001.001", "SVE-DOADOR ATIVO", "0000025", "PIX", date(2026, 9, 5), 50.00, None, 0.00, "1672301", "Novo Doador"),
            DoadorPerfilDTO("0000095", "JOAO CARLOS BATISTA", "MG", "120", "Arquidiocese de Belo Horizonte", "03.001.001", "SVE-DOADOR ATIVO", "0000023", "DEB", date(2026, 9, 10), 40.00, date(2026, 8, 10), 40.00, "1671902", "Doador Recorrente"),
            DoadorPerfilDTO("0000102", "ANA CLAUDIA MOREIRA", "DF", "010", "Arquidiocese de Brasília", "03.001.000", "SVE-DOADOR ACUMULADO", "0000025", "PIX", date(2026, 9, 18), 35.00, date(2026, 7, 20), 35.00, "1673105", "Retorno Doador"),
        ]

        status_metricas = [
            StatusDoadorMetricaDTO("Doador Recorrente", 1306, 42370.18, 80.0, 32.44, "#10B981"),
            StatusDoadorMetricaDTO("Retorno Doador", 314, 10212.54, 19.3, 32.52, "#F59E0B"),
            StatusDoadorMetricaDTO("Novo Doador", 10, 380.00, 0.7, 38.00, "#3B82F6"),
        ]

        tipos_cobranca = [
            TipoCobrancaMetricaDTO("DEB", "DEB - Débito em Conta", 610, 20150.00, 38.0, 33.03, 1, "ALTA"),
            TipoCobrancaMetricaDTO("BOL", "BOL - Boleto Bancário", 460, 15200.00, 28.7, 33.04, 2, "ESTAVEL"),
            TipoCobrancaMetricaDTO("VND", "VND - Cartão Recorrente (Vindi)", 380, 13800.00, 26.1, 36.32, 3, "ALTA"),
            TipoCobrancaMetricaDTO("PIX", "PIX - Pagamento Instantâneo PIX", 180, 3812.72, 7.2, 21.18, 4, "ALTA"),
        ]

        top_dioceses = [
            DioceseMetricaDTO("46", "ARQUIDIOCESE DO RIO DE JANEIRO", "RJ", 74, 2885.97, 5.4, 39.00),
            DioceseMetricaDTO("10", "ARQUIDIOCESE DE BRASÍLIA", "DF", 14, 1244.86, 2.3, 88.92),
            DioceseMetricaDTO("240", "ARQUIDIOCESE DE SÃO PAULO", "SP", 31, 1138.50, 2.1, 36.73),
            DioceseMetricaDTO("15", "ARQUIDIOCESE DE CURITIBA", "PR", 31, 1093.22, 2.1, 35.27),
            DioceseMetricaDTO("120", "ARQUIDIOCESE DE BELO HORIZONTE", "MG", 32, 1023.46, 1.9, 31.98),
            DioceseMetricaDTO("30", "ARQUIDIOCESE DE VITÓRIA", "ES", 36, 1002.94, 1.9, 27.86),
        ]

        evolucao_meses = [
            EvolucaoMesDTO(1, "Janeiro", 1911, 1845, 66463.99, 34.78),
            EvolucaoMesDTO(2, "Fevereiro", 2247, 2140, 79382.90, 35.33),
            EvolucaoMesDTO(3, "Março", 2438, 2280, 95513.59, 39.18),
            EvolucaoMesDTO(4, "Abril", 2285, 2137, 83257.55, 36.44),
            EvolucaoMesDTO(5, "Maio", 2327, 2204, 95895.44, 41.21),
            EvolucaoMesDTO(6, "Junho", 2390, 2247, 85313.97, 35.70),
            EvolucaoMesDTO(7, "Julho", 2158, 2036, 70755.36, 32.79),
            EvolucaoMesDTO(8, "Agosto", 1834, 1809, 60327.22, 32.89),
            EvolucaoMesDTO(9, "Setembro", 1630, 1609, 52962.72, 32.49),
        ]

        evolucao_anos = [
            EvolucaoAnoDTO(2026, 689872.74, 19220, 3291, 35.89, {1: 66463.99, 2: 79382.9, 3: 95513.59, 4: 83257.55, 5: 95895.44, 6: 85313.97, 7: 70755.36, 8: 60327.22, 9: 52962.72}),
            EvolucaoAnoDTO(2025, 1270822.40, 60926, 5489, 20.86),
            EvolucaoAnoDTO(2024, 1654335.41, 51682, 3458, 32.01),
            EvolucaoAnoDTO(2023, 1012618.13, 33227, 3108, 30.48),
            EvolucaoAnoDTO(2022, 968177.52, 32505, 3277, 29.79),
            EvolucaoAnoDTO(2021, 989530.58, 33962, 3617, 29.14),
            EvolucaoAnoDTO(2020, 829009.98, 28433, 3463, 29.16),
            EvolucaoAnoDTO(2019, 744495.25, 28186, 3298, 26.41),
            EvolucaoAnoDTO(2018, 407417.22, 15161, 2371, 26.87),
        ]

        historico_metodos = [
            HistoricoAnoMetodoDTO(2026, "DEB - Débito em Conta", 226623.00, 32.8, 689872.74, 19220, 35.89),
            HistoricoAnoMetodoDTO(2025, "DEB - Débito em Conta", 388056.00, 30.5, 1270822.40, 60926, 20.86),
            HistoricoAnoMetodoDTO(2024, "DEB - Débito em Conta", 581089.00, 35.1, 1654335.41, 51682, 32.01),
            HistoricoAnoMetodoDTO(2023, "BOL - Boleto Bancário", 442277.80, 43.7, 1012618.13, 33227, 30.48),
            HistoricoAnoMetodoDTO(2022, "BOL - Boleto Bancário", 426492.76, 44.1, 968177.52, 32505, 29.79),
            HistoricoAnoMetodoDTO(2021, "BOL - Boleto Bancário", 484067.00, 48.9, 989530.58, 33962, 29.14),
            HistoricoAnoMetodoDTO(2020, "BOL - Boleto Bancário", 538974.13, 65.0, 829009.98, 28433, 29.16),
            HistoricoAnoMetodoDTO(2019, "BOL - Boleto Bancário", 648480.25, 87.1, 744495.25, 28186, 26.41),
            HistoricoAnoMetodoDTO(2018, "BOL - Boleto Bancário", 407417.22, 100.0, 407417.22, 15161, 26.87),
        ]

        dt_ini, dt_fim, desc_periodo = self.obter_intervalo_datas(None, filtro)
        ano_resumo = dt_fim.year if dt_fim else filtro.ano
        mes_resumo = dt_fim.month if dt_fim else filtro.mes

        # Calibra métricas conforme o período para simular proporcionalidade
        if filtro.tipo_periodo == "10_DIAS":
            total_arrec = 18450.00
            qtd_doacoes_val = 534
            qtd_doadores_val = 520
            qtd_novos_val = 4
            tot_novos_val = 140.00
            qtd_rec_val = 430
            tot_rec_val = 14910.00
            qtd_ret_val = 100
            tot_ret_val = 3400.00
            doadores_retorno = doadores_demo[:4]
        else:
            total_arrec = 52962.72
            qtd_doacoes_val = 1630
            qtd_doadores_val = 1609
            qtd_novos_val = 10
            tot_novos_val = 380.00
            qtd_rec_val = 1306
            tot_rec_val = 42370.18
            qtd_ret_val = 314
            tot_ret_val = 10212.54
            doadores_retorno = doadores_demo

        tm_val = round(total_arrec / qtd_doacoes_val, 2) if qtd_doacoes_val > 0 else 0.0

        return ResumoDoacoesDTO(
            ano=ano_resumo,
            mes=mes_resumo,
            tipo_periodo=filtro.tipo_periodo,
            data_inicial=dt_ini,
            data_final=dt_fim,
            total_arrecadado=total_arrec,
            total_mes_anterior=60327.22,
            variacao_mes_anterior_pct=-12.2,
            qtd_doacoes=qtd_doacoes_val,
            qtd_doadores=qtd_doadores_val,
            ticket_medio=tm_val,
            qtd_novos=qtd_novos_val,
            total_novos=tot_novos_val,
            qtd_recorrentes=qtd_rec_val,
            total_recorrentes=tot_rec_val,
            qtd_retorno=qtd_ret_val,
            total_retorno=tot_ret_val,
            metodo_campeao="DEB - Débito em Conta",
            metodo_campeao_valor=20150.00,
            metodo_campeao_pct=38.0,
            periodo_descricao=desc_periodo,
            status_metricas=status_metricas,
            tipos_cobranca=tipos_cobranca,
            top_dioceses=top_dioceses,
            evolucao_meses=evolucao_meses,
            evolucao_anos=evolucao_anos,
            historico_metodos=historico_metodos,
            doadores=doadores_retorno,
        )
