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

    def __init__(self, repository: VindiRepository):
        self._repo = repository

    def checar_integridade(self, transacao: TransacaoVindiDTO) -> List[str]:
        erros = []
        if not transacao.cpf_cnpj:
            erros.append("CPF/CNPJ do cliente não informado na transação.")
        else:
            ent = self._repo.buscar_entidade_por_cpf(transacao.cpf_cnpj)
            if not ent:
                erros.append(f"Documento '{transacao.cpf_cnpj}' não localizado no cadastro de Entidades do Apolo.")
            else:
                transacao.ent_cod = ent[0]
                categs = self._repo.buscar_categorias_entidade(ent[0])
                if not categs:
                    erros.append(f"Entidade {ent[0]} não possui categoria de doador associada no Apolo.")
                elif len(categs) > 1:
                    erros.append(f"Entidade {ent[0]} possui duplicidade de categorias ({len(categs)} categorias cadastradas).")
                else:
                    transacao.categoria_cod = categs[0]

        if transacao.valor_bruto <= 0:
            erros.append("Valor bruto da transação deve ser superior a zero.")

        if transacao.status_vindi.lower() not in ("paga", "aprovada", "confirmada", "sucesso"):
            erros.append(f"Status da transação na Vindi não é de aprovação ('{transacao.status_vindi}').")

        transacao.erros = erros
        return erros

    def conciliar_periodo(
        self, data_ini: date, data_fim: date, apenas_nao_integradas: bool = False
    ) -> Tuple[List[TransacaoVindiDTO], ResumoConciliacaoVindiDTO]:
        if data_ini > data_fim:
            raise ValueError("A data inicial não pode ser superior à data final.")

        transacoes = self._repo.listar_transacoes(data_ini, data_fim, apenas_nao_integradas)

        total_bruto = sum(t.valor_bruto for t in transacoes)
        total_tarifas = sum(t.valor_tarifa for t in transacoes)
        total_liquido = sum(t.valor_liquido for t in transacoes)
        total_integradas = sum(1 for t in transacoes if t.integrada_apolo)

        com_erros = 0
        for t in transacoes:
            erros = self.checar_integridade(t)
            if erros:
                com_erros += 1

        resumo = ResumoConciliacaoVindiDTO(
            total_transacoes=len(transacoes),
            total_bruto=round(total_bruto, 2),
            total_tarifas=round(total_tarifas, 2),
            total_liquido=round(total_liquido, 2),
            total_integradas=total_integradas,
            total_com_inconsistencias=com_erros,
        )
        return transacoes, resumo

    def integrar_transacao(self, pedido_id: str) -> bool:
        p = str(pedido_id or "").strip()
        if not p:
            return False
        return self._repo.marcar_transacao_integrada(p)
