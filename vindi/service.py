"""
Camada de Serviços e Regras de Negócio para Conciliação Vindi.
GeoApolo V5
"""

import logging
from typing import List, Tuple, Optional
from datetime import date
from .models import (
    TransacaoVindiDTO,
    ResumoConciliacaoVindiDTO,
    ResultadoIntegracaoVindiDTO,
)
from .repository import VindiRepository

logger = logging.getLogger(__name__)


class VindiService:
    """Regras de validação de integridade, cálculo de taxas e conciliação Vindi."""

    # Subgrupos permitidos para categorias do setor de arrecadação (conforme substrings oficiais)
    SUBGRUPOS_ARRECADACAO = (
        "02.001",
        "02.002",
        "03.001",
        "03.002",
        "03.003",
        "03.004",
        "03.005",
        "03.006",
    )

    def __init__(self, repository: VindiRepository):
        self._repo = repository

    def validar_categoria_arrecadacao(self, categoria: str) -> bool:
        """Verifica se a categoria pertence aos subgrupos permitidos de arrecadação por substring."""
        cat = str(categoria or "").strip()
        return any(sub in cat for sub in self.SUBGRUPOS_ARRECADACAO)

    def obter_subgrupos_duplicados(self, categorias: List[str]) -> List[Tuple[str, List[str]]]:
        """
        Identifica se há mais de uma categoria associada ao mesmo subgrupo de arrecadação.
        Retorna lista de tuplas (subgrupo, [categorias_duplicadas]).
        """
        duplicados = []
        for sub in self.SUBGRUPOS_ARRECADACAO:
            cats = [c for c in categorias if sub in c]
            if len(cats) > 1:
                duplicados.append((sub, cats))
        return duplicados

    def checar_integridade(self, transacao: TransacaoVindiDTO) -> List[str]:
        erros = []
        if not transacao.cpf_cnpj:
            erros.append("CPF/CNPJ do cliente não informado na transação.")
        else:
            ent = self._repo.buscar_entidade_por_cpf(transacao.cpf_cnpj)
            if not ent:
                erros.append(f"Documento '{transacao.cpf_cnpj}' não localizado no cadastro de Entidades do Alvo.")
            else:
                transacao.ent_cod = ent[0]
                categs = self._repo.buscar_categorias_entidade(ent[0])
                if not categs:
                    erros.append(f"Entidade {ent[0]} não possui categoria de doador associada no Alvo.")
                else:
                    # Identifica categorias do setor de arrecadação
                    categs_arrecadacao = [c for c in categs if self.validar_categoria_arrecadacao(c)]
                    transacao.categoria_cod = ", ".join(categs_arrecadacao) if categs_arrecadacao else ", ".join(categs)

                    if not categs_arrecadacao:
                        erros.append(
                            f"Entidade {ent[0]} não possui categoria no setor de arrecadação do Alvo "
                            f"({', '.join(self.SUBGRUPOS_ARRECADACAO)}). Categorias encontradas: {', '.join(categs)}."
                        )
                    else:
                        # Regra: não pode haver mais de uma categoria do mesmo subgrupo.
                        # Caso haja categorias de outros grupos, a entidade pode pertencer a eles sem problemas.
                        duplicados = self.obter_subgrupos_duplicados(categs_arrecadacao)
                        if duplicados:
                            detalhes = [f"subgrupo '{sub}' ({', '.join(cats)})" for sub, cats in duplicados]
                            erros.append(
                                f"Entidade {ent[0]} possui mais de uma categoria no mesmo subgrupo de arrecadação: "
                                f"{'; '.join(detalhes)}."
                            )

        if transacao.valor_bruto <= 0:
            erros.append("Valor bruto da transação deve ser superior a zero.")

        status_norm = transacao.status_vindi.lower().strip()
        if status_norm in ("inactive", "inativa", "cancelada", "recusada", "estornada"):
            erros.append(f"Status da transação/entidade na Vindi é inativo/inválido ('{transacao.status_vindi}').")
        elif status_norm not in ("active", "ativa", "paga", "paid", "aprovada", "confirmada", "sucesso"):
            erros.append(f"Status da transação na Vindi não é de aprovação ('{transacao.status_vindi}').")

        transacao.erros = erros
        return erros

    def filtrar_transacoes(
        self, data_ini: date, data_fim: date, apenas_nao_integradas: bool = False
    ) -> Tuple[List[TransacaoVindiDTO], ResumoConciliacaoVindiDTO]:
        """Filtra transações no período sem disparar a rotina de consistência/integridade."""
        if data_ini > data_fim:
            raise ValueError("A data inicial não pode ser superior à data final.")

        transacoes = self._repo.listar_transacoes(data_ini, data_fim, apenas_nao_integradas)

        total_bruto = sum(t.valor_bruto for t in transacoes)
        total_tarifas = sum(t.valor_tarifa for t in transacoes)
        total_liquido = sum(t.valor_liquido for t in transacoes)
        total_integradas = sum(1 for t in transacoes if t.integrada_apolo)

        resumo = ResumoConciliacaoVindiDTO(
            total_transacoes=len(transacoes),
            total_bruto=round(total_bruto, 2),
            total_tarifas=round(total_tarifas, 2),
            total_liquido=round(total_liquido, 2),
            total_integradas=total_integradas,
            total_com_inconsistencias=0,
        )
        return transacoes, resumo

    def executar_checagem_integridade(
        self, transacoes: List[TransacaoVindiDTO]
    ) -> ResumoConciliacaoVindiDTO:
        """Executa a rotina de integridade para as transações carregadas."""
        total_bruto = sum(t.valor_bruto for t in transacoes)
        total_tarifas = sum(t.valor_tarifa for t in transacoes)
        total_liquido = sum(t.valor_liquido for t in transacoes)
        total_integradas = sum(1 for t in transacoes if t.integrada_apolo)

        com_erros = 0
        for t in transacoes:
            erros = self.checar_integridade(t)
            if erros:
                com_erros += 1

        return ResumoConciliacaoVindiDTO(
            total_transacoes=len(transacoes),
            total_bruto=round(total_bruto, 2),
            total_tarifas=round(total_tarifas, 2),
            total_liquido=round(total_liquido, 2),
            total_integradas=total_integradas,
            total_com_inconsistencias=com_erros,
        )

    def conciliar_periodo(
        self, data_ini: date, data_fim: date, apenas_nao_integradas: bool = False
    ) -> Tuple[List[TransacaoVindiDTO], ResumoConciliacaoVindiDTO]:
        transacoes, _ = self.filtrar_transacoes(data_ini, data_fim, apenas_nao_integradas)
        resumo = self.executar_checagem_integridade(transacoes)
        return transacoes, resumo

    def integrar_transacao(self, pedido_id: str) -> bool:
        p = str(pedido_id or "").strip()
        if not p:
            return False
        return self._repo.marcar_transacao_integrada(p)
