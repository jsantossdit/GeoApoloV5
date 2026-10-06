"""
Serviço de Regras de Negócio para Gestão de Estoque e Requisições de Materiais.
GeoApolo V5
Clean Architecture: Validações de estoque, atendimento, cancelamento, devolução e movimentações.
"""

import logging
from typing import List, Optional, Tuple
from .models import (
    RequisicaoDTO,
    ItemRequisicaoDTO,
    MovimentoEstoqueDTO,
    FichaEstoqueLinhaDTO,
    SaldoProdutoDTO,
    ResultadoEstoqueDTO,
)
from .repository import EstoqueRepository

logger = logging.getLogger(__name__)


class EstoqueService:
    """Camada de serviços para gestão de requisições e movimentações de estoque."""

    def __init__(self, repository: Optional[EstoqueRepository] = None):
        self._repo = repository or EstoqueRepository()

    @property
    def repo(self) -> EstoqueRepository:
        return self._repo

    def obter_proximo_numero_requisicao(self, empcod: str = "1.01") -> str:
        """Obtém a próxima numeração para emissão de requisição."""
        return self._repo.obter_proximo_numero_requisicao(empcod=empcod)

    def listar_centros_custo(self, empcod: str = "1.01"):
        """Lista centros de custo disponíveis para a requisição ou movimentação."""
        return self._repo.listar_centros_custo(empcod=empcod)

    def listar_fornecedores(self, termo: str = ""):
        """Lista fornecedores disponíveis para entrada de mercadorias."""
        return self._repo.listar_fornecedores(termo=termo)

    def criar_requisicao(self, requisicao: RequisicaoDTO) -> ResultadoEstoqueDTO:
        """Valida e grava uma nova requisição de material no estoque."""
        if not requisicao.requerente or not requisicao.requerente.strip():
            return ResultadoEstoqueDTO(sucesso=False, mensagem="O solicitante / requerente da requisição é obrigatório.")

        if not requisicao.centro_custo or not requisicao.centro_custo.strip():
            return ResultadoEstoqueDTO(sucesso=False, mensagem="O centro de custo / controle é obrigatório.")

        if not requisicao.itens:
            return ResultadoEstoqueDTO(sucesso=False, mensagem="Adicione ao menos um item à requisição.")

        for i, item in enumerate(requisicao.itens, start=1):
            if not item.prodcod_estr or not item.prodcod_estr.strip():
                return ResultadoEstoqueDTO(sucesso=False, mensagem=f"Código do produto não informado no item {i}.")
            if item.qtd_solicitada <= 0:
                return ResultadoEstoqueDTO(sucesso=False, mensagem=f"Quantidade do item {i} ({item.prodnome}) deve ser maior que zero.")

        sucesso, msg, doc = self._repo.criar_requisicao(requisicao)
        return ResultadoEstoqueDTO(sucesso=sucesso, mensagem=msg, documento=doc)

    def listar_requisicoes(
        self,
        empcod: str = "1.01",
        status_filtro: str = "TODOS",
        termo_busca: str = "",
        data_ini: str = "",
        data_fim: str = "",
    ) -> List[RequisicaoDTO]:
        """Lista requisições com os filtros informados."""
        return self._repo.listar_requisicoes(
            empcod=empcod,
            status_filtro=status_filtro,
            termo_busca=termo_busca.strip().upper(),
            data_ini=data_ini.strip(),
            data_fim=data_fim.strip(),
        )

    def obter_requisicao(self, req_num: str, empcod: str = "1.01") -> Optional[RequisicaoDTO]:
        """Obtém uma requisição detalhada por número."""
        if not req_num or not req_num.strip():
            return None
        return self._repo.obter_requisicao(req_num.strip(), empcod=empcod)

    def obter_itens_requisicao(self, req_num: str, empcod: str = "1.01") -> List[ItemRequisicaoDTO]:
        """Obtém lista de itens de uma requisição."""
        if not req_num or not req_num.strip():
            return []
        return self._repo.obter_itens_requisicao(req_num.strip(), empcod=empcod)

    def atender_item_requisicao(
        self,
        req_num: str,
        item_seq: int,
        qtd_atender: float,
        empcod: str = "1.01",
        observacao: str = "",
        numero_lote: str = "",
    ) -> ResultadoEstoqueDTO:
        """Valida e processa o atendimento de item de requisição."""
        req_num = str(req_num).strip()
        if not req_num:
            return ResultadoEstoqueDTO(sucesso=False, mensagem="Número da requisição é obrigatório.")

        if item_seq <= 0:
            return ResultadoEstoqueDTO(sucesso=False, mensagem="Sequência de item inválida.")

        try:
            qtd = float(qtd_atender)
        except (ValueError, TypeError):
            return ResultadoEstoqueDTO(sucesso=False, mensagem="Quantidade informada é inválida.")

        if qtd <= 0:
            return ResultadoEstoqueDTO(sucesso=False, mensagem="A quantidade a atender deve ser maior que zero.")

        obs = observacao.strip().upper() if observacao else ""
        lote_str = str(numero_lote or "").strip().upper()
        sucesso, msg, mov_chv = self._repo.atender_item_requisicao(
            req_num=req_num,
            item_seq=item_seq,
            qtd_atender=qtd,
            empcod=empcod,
            observacao=obs,
            numero_lote=lote_str,
        )
        return ResultadoEstoqueDTO(sucesso=sucesso, mensagem=msg, codigo=mov_chv, documento=req_num)

    def atender_requisicao_completa(
        self,
        req_num: str,
        empcod: str = "1.01",
        observacao: str = "",
        itens_lotes: Optional[dict] = None,
    ) -> ResultadoEstoqueDTO:
        """Valida e processa o atendimento total de todos os itens pendentes da requisição."""
        req_num = str(req_num).strip()
        if not req_num:
            return ResultadoEstoqueDTO(sucesso=False, mensagem="Número da requisição é obrigatório.")

        obs = observacao.strip().upper() if observacao else ""
        sucesso, msg, mov_chv = self._repo.atender_requisicao_completa(
            req_num=req_num,
            empcod=empcod,
            observacao=obs,
            itens_lotes=itens_lotes,
        )
        return ResultadoEstoqueDTO(sucesso=sucesso, mensagem=msg, codigo=mov_chv, documento=req_num)

    def obter_saldo_produto(
        self,
        prodcod_estr: str,
        empcod: str = "1.01",
    ) -> Tuple[float, float, float]:
        """Retorna (saldo_atual, quantidade_reservada, saldo_disponivel) para o produto."""
        return self._repo.obter_saldo_produto(empcod=empcod, prodcod=prodcod_estr)

    def permite_estoque_negativo(self, empcod: str = "1.01") -> bool:
        """Verifica se os parâmetros do sistema permitem estoque negativo para a empresa."""
        return self._repo.permite_estoque_negativo(empcod=empcod)

    def cancelar_requisicao(
        self,
        req_num: str,
        empcod: str = "1.01",
        motivo: str = "",
    ) -> ResultadoEstoqueDTO:
        """Valida e efetua o cancelamento de uma requisição de material."""
        req_num = str(req_num).strip()
        if not req_num:
            return ResultadoEstoqueDTO(sucesso=False, mensagem="Número da requisição é obrigatório.")

        motivo_limpo = motivo.strip().upper()
        if not motivo_limpo:
            return ResultadoEstoqueDTO(sucesso=False, mensagem="É necessário informar a justificativa do cancelamento.")

        sucesso, msg = self._repo.cancelar_requisicao(req_num=req_num, empcod=empcod, motivo=motivo_limpo)
        return ResultadoEstoqueDTO(sucesso=sucesso, mensagem=msg, documento=req_num)

    def devolver_item_requisicao(
        self,
        req_num: str,
        item_seq: int,
        qtd_devolver: float,
        empcod: str = "1.01",
        observacao: str = "",
    ) -> ResultadoEstoqueDTO:
        """Valida e processa a devolução/estorno de item atendido de volta ao estoque."""
        req_num = str(req_num).strip()
        if not req_num:
            return ResultadoEstoqueDTO(sucesso=False, mensagem="Número da requisição é obrigatório.")

        if item_seq <= 0:
            return ResultadoEstoqueDTO(sucesso=False, mensagem="Sequência de item inválida.")

        try:
            qtd = float(qtd_devolver)
        except (ValueError, TypeError):
            return ResultadoEstoqueDTO(sucesso=False, mensagem="Quantidade informada é inválida.")

        if qtd <= 0:
            return ResultadoEstoqueDTO(sucesso=False, mensagem="A quantidade a devolver deve ser maior que zero.")

        obs = observacao.strip().upper() if observacao else ""
        sucesso, msg, mov_chv = self._repo.devolver_item_requisicao(
            req_num=req_num,
            item_seq=item_seq,
            qtd_devolver=qtd,
            empcod=empcod,
            observacao=obs,
        )
        return ResultadoEstoqueDTO(sucesso=sucesso, mensagem=msg, codigo=mov_chv, documento=req_num)

    def cancelar_item_requisicao(
        self,
        req_num: str,
        item_seq: int,
        motivo: str,
        empcod: str = "1.01",
    ) -> ResultadoEstoqueDTO:
        """Valida e cancela o saldo pendente de um item de requisição (baixa o item/requisição)."""
        req_num = str(req_num).strip()
        if not req_num:
            return ResultadoEstoqueDTO(sucesso=False, mensagem="Número da requisição é obrigatório.")

        if item_seq <= 0:
            return ResultadoEstoqueDTO(sucesso=False, mensagem="Sequência de item inválida.")

        motivo_limpo = (motivo or "").strip().upper()
        if not motivo_limpo:
            return ResultadoEstoqueDTO(sucesso=False, mensagem="É necessário informar a justificativa do cancelamento do item.")

        sucesso, msg = self._repo.cancelar_item_requisicao(
            req_num=req_num,
            item_seq=item_seq,
            motivo=motivo_limpo,
            empcod=empcod,
        )
        return ResultadoEstoqueDTO(sucesso=sucesso, mensagem=msg, documento=req_num)

    # -------------------------------------------------------------------------
    # MOVIMENTAÇÕES DE ENTRADA E SAÍDA
    # -------------------------------------------------------------------------
    def registrar_entrada_compras(
        self,
        empcod: str,
        prodcod_estr: str,
        quantidade: float,
        valor_unitario: float = 0.0,
        num_doc: str = "",
        fornecedor_obs: str = "",
        centro_custo: str = "",
        fornecedor_cod: str = "",
        fornecedor_nome: str = "",
        data_vencimento: str = "",
        data_emissao: str = "",
        numero_lote: str = "",
    ) -> ResultadoEstoqueDTO:
        """Valida e registra entrada de mercadorias no estoque e gera título a pagar se houver valor."""
        prod = str(prodcod_estr).strip().upper()
        if not prod:
            return ResultadoEstoqueDTO(sucesso=False, mensagem="Código do produto é obrigatório.")

        try:
            qtd = float(quantidade)
        except (ValueError, TypeError):
            return ResultadoEstoqueDTO(sucesso=False, mensagem="Quantidade inválida.")

        if qtd <= 0:
            return ResultadoEstoqueDTO(sucesso=False, mensagem="A quantidade de entrada deve ser maior que zero.")

        try:
            val_unit = float(valor_unitario or 0.0)
        except (ValueError, TypeError):
            val_unit = 0.0

        doc_limpo = num_doc.strip().upper()
        obs_limpo = fornecedor_obs.strip().upper()
        lote_limpo = str(numero_lote or "").strip().upper()

        sucesso, msg, mov_chv = self._repo.registrar_movimentacao_entrada(
            empcod=empcod,
            prodcod_estr=prod,
            quantidade=qtd,
            valor_unitario=val_unit,
            num_doc=doc_limpo,
            fornecedor_obs=obs_limpo,
            centro_custo=centro_custo.strip().upper(),
            fornecedor_cod=fornecedor_cod.strip().upper(),
            fornecedor_nome=fornecedor_nome.strip().upper(),
            numero_lote=lote_limpo,
        )

        # Geração automática de Contas a Pagar ao lançar movimento de estoque de entrada
        if sucesso and mov_chv > 0 and val_unit > 0:
            try:
                from contas_a_pagar.service import ContasPagarService
                cp_service = ContasPagarService()
                val_total = qtd * val_unit
                ok_cp, msg_cp, id_cp = cp_service.gerar_titulo_por_entrada_estoque(
                    empcod=empcod,
                    doc_num=doc_limpo,
                    fornecedor_cod=fornecedor_cod,
                    fornecedor_nome=fornecedor_nome,
                    data_emissao=data_emissao,
                    data_vencimento=data_vencimento,
                    valor_total=val_total,
                    codigo_movimento_estoque=mov_chv,
                    centro_custo=centro_custo,
                    observacao=obs_limpo,
                )
                if ok_cp:
                    msg += f"\nTítulo Financeiro a Pagar Nº {id_cp} gerado com sucesso!"
                elif "não encontrada" in msg_cp or "ainda não existe" in msg_cp:
                    msg += "\n(Aviso: A tabela de Contas a Pagar ainda não foi criada. Aplique sql/criar_tabela_contas_a_pagar.sql)"
                else:
                    msg += f"\n(Aviso Financeiro: {msg_cp})"
            except Exception as e:
                logger.warning("Falha ao integrar entrada de estoque com Contas a Pagar: %s", e)

        return ResultadoEstoqueDTO(sucesso=sucesso, mensagem=msg, codigo=mov_chv, documento=doc_limpo)

    def registrar_saida_direta(
        self,
        empcod: str,
        prodcod_estr: str,
        quantidade: float,
        destino_obs: str = "",
        centro_custo: str = "",
        numero_lote: str = "",
    ) -> ResultadoEstoqueDTO:
        """Valida e registra saída direta sem requisição."""
        prod = str(prodcod_estr).strip().upper()
        if not prod:
            return ResultadoEstoqueDTO(sucesso=False, mensagem="Código do produto é obrigatório.")

        try:
            qtd = float(quantidade)
        except (ValueError, TypeError):
            return ResultadoEstoqueDTO(sucesso=False, mensagem="Quantidade inválida.")

        if qtd <= 0:
            return ResultadoEstoqueDTO(sucesso=False, mensagem="A quantidade de saída deve ser maior que zero.")

        obs_limpo = destino_obs.strip().upper()
        lote_limpo = str(numero_lote or "").strip().upper()
        sucesso, msg, mov_chv = self._repo.registrar_movimentacao_saida_direta(
            empcod=empcod,
            prodcod_estr=prod,
            quantidade=qtd,
            destino_obs=obs_limpo,
            centro_custo=centro_custo.strip().upper(),
            numero_lote=lote_limpo,
        )
        return ResultadoEstoqueDTO(sucesso=sucesso, mensagem=msg, codigo=mov_chv)

    def listar_movimentacoes(
        self,
        empcod: str = "1.01",
        data_ini: str = "",
        data_fim: str = "",
        tipo_filtro: str = "TODOS",
        termo_prod: str = "",
        limite: int = 200,
    ) -> List[MovimentoEstoqueDTO]:
        """Lista histórico de movimentações com filtros."""
        return self._repo.listar_movimentacoes(
            empcod=empcod,
            data_ini=data_ini.strip(),
            data_fim=data_fim.strip(),
            tipo_filtro=tipo_filtro.upper(),
            termo_prod=termo_prod.strip().upper(),
            limite=limite,
        )

    # -------------------------------------------------------------------------
    # CONSULTAS
    # -------------------------------------------------------------------------
    def consultar_ficha_estoque(
        self,
        prodcod_estr: str,
        empcod: str = "1.01",
        data_ini: str = "",
        data_fim: str = "",
    ) -> List[FichaEstoqueLinhaDTO]:
        """Retorna extrato de Ficha Estoque (Kardex) para o produto."""
        if not prodcod_estr or not prodcod_estr.strip():
            return []
        return self._repo.consultar_ficha_estoque(
            prodcod_estr=prodcod_estr.strip().upper(),
            empcod=empcod,
            data_ini=data_ini.strip(),
            data_fim=data_fim.strip(),
        )

    def consultar_saldos_produtos(
        self,
        empcod: str = "1.01",
        termo_busca: str = "",
        grupocod: Optional[int] = None,
    ) -> List[SaldoProdutoDTO]:
        """Retorna os saldos atuais e disponíveis de produtos."""
        return self._repo.consultar_saldos_produtos(
            empcod=empcod,
            termo_busca=termo_busca.strip().upper(),
            grupocod=grupocod,
        )

    def contar_total_produtos_catalogo(self) -> int:
        """Retorna a contagem total de produtos cadastrados no catálogo."""
        return self._repo.contar_total_produtos_catalogo()
