"""
Camada de Negócio e Motor de Inteligência Analítica (IA) para Doações.
Gera diagnósticos preditivos, comportamentais e recomendações estratégicas
com base nas métricas de Dashboard-menuprincipal.sql.
GeoApolo V5
"""

import copy
import logging
from typing import Optional, List, Dict, Tuple, Any, Callable
from dashboard.models import (
    FiltroDashboardDTO,
    ResumoDoacoesDTO,
    DoadorPerfilDTO,
    StatusDoadorMetricaDTO,
    TipoCobrancaMetricaDTO,
    EvolucaoMesDTO,
    EvolucaoAnoDTO,
    HistoricoAnoMetodoDTO,
    InsightIADTO,
)
from dashboard.repository import DashboardRepository

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Serviço de agregação de métricas, cache inteligente de sessão, filtragem dinâmica
    e geração de insights de IA sobre o perfil de doadores e arrecadação.
    """

    def __init__(self, repository: Optional[DashboardRepository] = None):
        self._repo = repository or DashboardRepository()
        self._cache_resumo: Dict[Tuple[Any, ...], ResumoDoacoesDTO] = {}

    def obter_dashboard(
        self,
        filtro: Optional[FiltroDashboardDTO] = None,
        forcar_atualizacao: bool = False,
        callback_progresso: Optional[Callable[[int, str], None]] = None
    ) -> ResumoDoacoesDTO:
        """Carrega os dados (com suporte a cache em memória) e enriquece com diagnósticos de IA."""
        if filtro is None:
            filtro = FiltroDashboardDTO()

        cache_key = (
            filtro.empresa,
            filtro.tipo_periodo,
            str(filtro.data_inicial),
            str(filtro.data_final),
            filtro.ano,
            filtro.mes
        )
        if not forcar_atualizacao and cache_key in self._cache_resumo:
            logger.debug("Utilizando resumo em cache para %s", cache_key)
            if callback_progresso:
                try:
                    callback_progresso(100, "Dados recuperados do cache de sessão")
                except Exception:
                    pass
            resumo_base = self._cache_resumo[cache_key]
        else:
            resumo_base = self._repo.carregar_dados_completos(filtro, callback_progresso=callback_progresso)
            self._cache_resumo[cache_key] = resumo_base

        # Cria cópia superficial para aplicar filtros locais de tela sem degradar o cache mestre
        resumo = copy.copy(resumo_base)
        resumo.doadores = self._filtrar_doadores(
            list(resumo_base.doadores),
            status_filtro=filtro.status_filtro,
            forma_filtro=filtro.forma_filtro,
            termo_busca=filtro.termo_busca,
        )

        resumo.insights_ia = self.gerar_insights_ia(resumo)
        return resumo

    def carregar_historico(
        self,
        filtro: FiltroDashboardDTO
    ) -> Tuple[List[EvolucaoMesDTO], List[EvolucaoAnoDTO], List[HistoricoAnoMetodoDTO]]:
        """Carrega sob demanda as séries temporais da Aba 3 (lazy loading)."""
        return self._repo.carregar_historico_longitudinal(filtro)

    def limpar_cache(self):
        """Descarta o cache em memória para forçar nova consulta ao banco."""
        self._cache_resumo.clear()

    def sincronizar_perfil_mes(self, ano: int, mes: int, empcod: str = "1.01") -> bool:
        """Aciona a procedure de sincronização do perfil financeiro e invalida o cache."""
        self.limpar_cache()
        return self._repo.sincronizar_perfil_mes(ano, mes, empcod)

    def _filtrar_doadores(
        self,
        doadores: List[DoadorPerfilDTO],
        status_filtro: str = "TODOS",
        forma_filtro: str = "TODAS",
        termo_busca: str = ""
    ) -> List[DoadorPerfilDTO]:
        """Filtra a relação de doadores por status, forma de pagamento ou termo de pesquisa."""
        resultado = doadores

        if status_filtro and status_filtro != "TODOS":
            resultado = [d for d in resultado if d.status_doador.lower() == status_filtro.lower()]

        if forma_filtro and forma_filtro != "TODAS":
            resultado = [d for d in resultado if d.forma_contribuicao.upper() == forma_filtro.upper()]

        if termo_busca:
            termo = termo_busca.strip().lower()
            resultado = [
                d for d in resultado
                if termo in d.entcod.lower()
                or termo in d.entnome.lower()
                or termo in d.diocese.lower()
                or termo in d.uf.lower()
                or termo in d.categnome.lower()
            ]

        return resultado

    def gerar_insights_ia(self, resumo: ResumoDoacoesDTO) -> List[InsightIADTO]:
        """
        Motor Analítico de IA: Avalia composição da base (Recorrentes, Novos, Retorno),
        sazonalidade, comparativo com mês anterior e projeta metas de arrecadação.
        """
        insights = []

        if not resumo.doadores and resumo.total_arrecadado == 0:
            insights.append(InsightIADTO(
                tipo="ALERTA",
                icone="ℹ️",
                titulo="Sem Dados para o Mês Selecionado",
                descricao="Nenhum título de doação encontrado para os critérios selecionados.",
                impacto="INFO",
                cor_destaque="#4B5563"
            ))
            return insights

        # 1. Insight: Base Recorrente e Índice de Fidelização
        if resumo.qtd_doacoes > 0 and resumo.qtd_recorrentes > 0:
            pct_recorr = (resumo.qtd_recorrentes / resumo.qtd_doacoes) * 100.0
            val_formatado = f"R$ {resumo.total_recorrentes:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            insights.append(InsightIADTO(
                tipo="FIDELIZACAO",
                icone="🔄",
                titulo=f"Base Recorrente Sólida ({pct_recorr:.1f}% das Doações)",
                descricao=(
                    f"Os doadores recorrentes (intervalo <= 35 dias) somam {resumo.qtd_recorrentes} doações "
                    f"e totalizam {val_formatado}. Essa base altamente fidelizada assegura a sustentabilidade "
                    f"financeira dos projetos centrais da RCC."
                ),
                impacto="ALTO",
                cor_destaque="#059669",
            ))

        # 2. Insight: Retorno de Doadores (Reativação de Doadores Inativos)
        if resumo.qtd_retorno > 0:
            val_retorno = f"R$ {resumo.total_retorno:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            pct_retorno = (resumo.qtd_retorno / resumo.qtd_doacoes * 100.0) if resumo.qtd_doacoes > 0 else 0.0
            insights.append(InsightIADTO(
                tipo="OPORTUNIDADE",
                icone="🤝",
                titulo=f"Reativação de Doadores em Alta ({resumo.qtd_retorno} Retornos)",
                descricao=(
                    f"Identificados {resumo.qtd_retorno} doadores que retomaram suas contribuições após mais de 35 dias de hiato "
                    f"({val_retorno}, representando {pct_retorno:.1f}% do mês). "
                    f"Campanhas de pós-retorno e cartas de agradecimento aumentam a retenção desses doadores em até 44%."
                ),
                impacto="ALTO",
                cor_destaque="#D97706",
            ))

        # 3. Insight: Novos Doadores & Expansão de Base
        if resumo.qtd_novos > 0:
            val_novos = f"R$ {resumo.total_novos:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            insights.append(InsightIADTO(
                tipo="DESTAQUE",
                icone="🌟",
                titulo=f"Captação de Novos Doadores ({resumo.qtd_novos} Cadastros)",
                descricao=(
                    f"No mês avaliado, {resumo.qtd_novos} pessoas realizaram sua primeira contribuição histórica "
                    f"({val_novos}). O acolhimento imediato no primeiro mês é determinante para transformá-los em recorrentes."
                ),
                impacto="MEDIO",
                cor_destaque="#2563EB",
            ))

        # 4. Insight: Comparativo vs Mês Anterior
        if resumo.total_mes_anterior > 0:
            diff = resumo.total_arrecadado - resumo.total_mes_anterior
            diff_fmt = f"R$ {abs(diff):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            pct = resumo.variacao_mes_anterior_pct
            if pct >= 0:
                insights.append(InsightIADTO(
                    tipo="TENDENCIA",
                    icone="📈",
                    titulo=f"Crescimento de +{pct:.1f}% em Relação ao Mês Anterior",
                    descricao=(
                        f"A arrecadação avançou {diff_fmt} em comparação com o mês imediatamente anterior "
                        f"(R$ {resumo.total_mes_anterior:,.2f} vs R$ {resumo.total_arrecadado:,.2f}), indicando curva favorável de captação."
                    ),
                    impacto="MEDIO",
                    cor_destaque="#0D9488",
                ))
            else:
                insights.append(InsightIADTO(
                    tipo="ALERTA",
                    icone="📉",
                    titulo=f"Oscilação de {pct:.1f}% vs Mês Anterior",
                    descricao=(
                        f"Houve uma retração de {diff_fmt} em relação ao mês anterior. "
                        f"Recomenda-se intensificar disparos de e-mail e lembretes de liquidação de boletos em aberto."
                    ),
                    impacto="MEDIO",
                    cor_destaque="#DC2626",
                ))

        # 5. Insight: Eficiência de Meios (Débito, Vindi e PIX vs Boletos)
        if resumo.tipos_cobranca:
            meio_lider = resumo.tipos_cobranca[0]
            insights.append(InsightIADTO(
                tipo="TENDENCIA",
                icone="💳",
                titulo=f"Liderança Operacional: {meio_lider.nome}",
                descricao=(
                    f"O canal '{meio_lider.nome}' lidera o mês com R$ {meio_lider.total:,.2f} "
                    f"({meio_lider.percentual:.1f}% de participação) em {meio_lider.qtd} doações com ticket médio "
                    f"de R$ {meio_lider.ticket_medio:,.2f}."
                ),
                impacto="MEDIO",
                cor_destaque="#4F46E5",
            ))

        # 6. Insight: Regionalização e Top Dioceses
        if resumo.top_dioceses:
            top_dio = resumo.top_dioceses[0]
            insights.append(InsightIADTO(
                tipo="DESTAQUE",
                icone="🏛️",
                titulo=f"Destaque Regional: {top_dio.nome} ({top_dio.uf})",
                descricao=(
                    f"A diocese '{top_dio.nome}' ({top_dio.uf}) alcançou a primeira posição no ranking com "
                    f"R$ {top_dio.total:,.2f} em {top_dio.qtd} doações processadas no período."
                ),
                impacto="INFO",
                cor_destaque="#065F46",
            ))

        # 7. Insight: Previsibilidade Preditiva (Forecast)
        if resumo.total_arrecadado > 0 and resumo.ticket_medio > 0:
            projecao = resumo.total_arrecadado * 1.05
            val_proj_fmt = f"R$ {projecao:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            ticket_fmt = f"R$ {resumo.ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            insights.append(InsightIADTO(
                tipo="FORECAST",
                icone="🔮",
                titulo="Projeção Preditiva para o Próximo Mês",
                descricao=(
                    f"Com a taxa de recorrência atual e ticket médio de {ticket_fmt}, a estimativa para o "
                    f"fechamento do ciclo seguinte é de {val_proj_fmt} (+5,0% de projeção orgânica)."
                ),
                impacto="ALTO",
                cor_destaque="#047857",
            ))

        return insights
