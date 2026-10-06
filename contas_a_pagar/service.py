"""
Camada de Serviços e Regras de Negócio de Contas a Pagar / Documentos Financeiros.
GeoApolo V5
"""

import logging
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from .models import DocumentoPagarDTO, FiltroContasPagarDTO, ResumoContasPagarDTO, BaixaDocumentoDTO
from .repository import ContasPagarRepository

logger = logging.getLogger(__name__)


class ContasPagarService:
    """Regras de negócio corporativas para Contas a Pagar."""

    def __init__(self, repository: Optional[ContasPagarRepository] = None):
        self._repo = repository or ContasPagarRepository()

    def tabela_disponivel(self) -> bool:
        """Verifica se a infraestrutura de banco de dados para contas a pagar está pronta."""
        return self._repo.tabela_existe()

    def criar_tabela_banco(self) -> Tuple[bool, str]:
        """Cria a tabela no banco caso o usuário solicite."""
        return self._repo.criar_tabela()

    def gerar_titulo_por_entrada_estoque(
        self,
        empcod: str,
        doc_num: str,
        fornecedor_cod: str,
        fornecedor_nome: str,
        data_emissao: str,
        data_vencimento: str,
        valor_total: float,
        codigo_movimento_estoque: int,
        centro_custo: str = "",
        observacao: str = "",
        usuario: str = "",
    ) -> Tuple[bool, str, int]:
        """
        Gera automaticamente um título a pagar associado a uma movimentação de estoque de entrada.
        """
        if not self._repo.tabela_existe():
            return False, "Tabela de Contas a Pagar (USER_geoapolo_contas_a_pagar) não encontrada no banco.", 0

        v_tot = round(float(valor_total or 0.0), 2)
        if v_tot <= 0:
            return False, "Valor total do documento deve ser maior que zero para gerar contas a pagar.", 0

        num_doc_limpo = doc_num.strip().upper() if doc_num else f"ENT_{codigo_movimento_estoque}"
        nome_forn = fornecedor_nome.strip().upper() if fornecedor_nome else "FORNECEDOR NÃO INFORMADO"

        # Se não informada a data de emissão, assume data atual
        dt_emis = data_emissao.strip() if data_emissao else datetime.now().strftime("%Y-%m-%d")
        
        # Se não informada data de vencimento válida, assume 30 dias após emissão
        dt_venc = data_vencimento.strip() if data_vencimento else (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        obs_completa = f"GERADO AUTOMATICAMENTE PELA ENTRADA DE ESTOQUE Nº {codigo_movimento_estoque}. {observacao}".strip()

        doc_dto = DocumentoPagarDTO(
            codigo_empresa=empcod or "1.01",
            numero_documento=num_doc_limpo,
            serie_documento="1",
            parcela=1,
            total_parcelas=1,
            entcod=fornecedor_cod.strip() if fornecedor_cod else "",
            fornecedor_nome=nome_forn,
            data_emissao=dt_emis,
            data_vencimento=dt_venc,
            valor_original=v_tot,
            valor_desconto=0.0,
            valor_juros_multa=0.0,
            valor_pago=0.0,
            saldo_aberto=v_tot,
            situacao="ABERTO",
            tipo_documento="ENTRADA_ESTOQUE",
            origem="COMPRA_ESTOQUE",
            centro_custo=centro_custo.strip().upper(),
            codigo_movimento_estoque=codigo_movimento_estoque,
            observacoes=obs_completa,
            usuario_inclusao=usuario or "",
        )

        return self._repo.inserir_documento_pagar(doc_dto)

    def gerar_titulo_por_servico_requisicao(
        self,
        empcod: str,
        req_num: str,
        item_seq: int,
        descricao_servico: str,
        valor_total: float,
        codigo_movimento_estoque: int,
        centro_custo: str = "",
        fornecedor_cod: str = "",
        fornecedor_nome: str = "",
        data_emissao: str = "",
        data_vencimento: str = "",
        observacao: str = "",
        usuario: str = "",
    ) -> Tuple[bool, str, int]:
        """
        Gera automaticamente um título a pagar associado a um atendimento de requisição do tipo SERVIÇO.
        """
        if not self._repo.tabela_existe():
            self._repo.criar_tabela()

        v_tot = round(float(valor_total or 0.0), 2)
        num_doc = f"SRV_{req_num}_{item_seq}".strip().upper()
        nome_forn = fornecedor_nome.strip().upper() if fornecedor_nome else "PRESTADOR A DEFINIR"
        dt_emis = data_emissao.strip() if data_emissao else datetime.now().strftime("%Y-%m-%d")
        dt_venc = data_vencimento.strip() if data_vencimento else (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        obs_completa = f"SERVIÇO DA REQUISIÇÃO Nº {req_num} ITEM {item_seq}: {descricao_servico}. {observacao}".strip()

        doc_dto = DocumentoPagarDTO(
            codigo_empresa=empcod or "1.01",
            numero_documento=num_doc,
            serie_documento="1",
            parcela=1,
            total_parcelas=1,
            entcod=fornecedor_cod.strip() if fornecedor_cod else "",
            fornecedor_nome=nome_forn,
            data_emissao=dt_emis,
            data_vencimento=dt_venc,
            valor_original=v_tot,
            valor_desconto=0.0,
            valor_juros_multa=0.0,
            valor_pago=0.0,
            saldo_aberto=v_tot,
            situacao="ABERTO",
            tipo_documento="SERVICO",
            origem="REQUISICAO_SERVICO",
            centro_custo=centro_custo.strip().upper(),
            codigo_movimento_estoque=codigo_movimento_estoque,
            observacoes=obs_completa,
            usuario_inclusao=usuario or "",
        )

        return self._repo.inserir_documento_pagar(doc_dto)

    def listar_titulos(self, filtro: FiltroContasPagarDTO) -> List[DocumentoPagarDTO]:
        """Obtém lista de títulos aplicando filtros."""
        return self._repo.listar_documentos(filtro)

    def obter_resumo(self, filtro: FiltroContasPagarDTO) -> ResumoContasPagarDTO:
        """Obtém totalizadores para exibição nos cards."""
        return self._repo.obter_resumo(filtro)

    def registrar_baixa(self, baixa: BaixaDocumentoDTO) -> Tuple[bool, str]:
        """Valida e processa baixa de documento financeiro."""
        if baixa.valor_pago <= 0:
            return False, "O valor de pagamento deve ser superior a zero."
        return self._repo.baixar_documento(baixa)
