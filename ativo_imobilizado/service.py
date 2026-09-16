"""
Camada de Serviços e Regras de Negócio para Ativo Imobilizado.
Implementa cálculos de depreciação (Linha Reta) e validações cadastrais.
"""

import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Union
from ativo_imobilizado.models import (
    AtivoImobilizadoDTO,
    CalculoDepreciacaoDTO,
    ResultadoOperacaoAtivo,
)
from ativo_imobilizado.repository import AtivoImobilizadoRepository

logger = logging.getLogger(__name__)


class AtivoImobilizadoService:
    """Regras de negócio, cálculos contábeis e orquestração de Ativo Imobilizado."""

    def __init__(self, repository: AtivoImobilizadoRepository):
        self._repo = repository

    def _parse_data(self, data_str: Optional[Union[str, date, datetime]]) -> Optional[date]:
        """Converte strings no formato DD/MM/YYYY ou YYYY-MM-DD em objeto date."""
        if not data_str:
            return None
        if isinstance(data_str, datetime):
            return data_str.date()
        if isinstance(data_str, date):
            return data_str

        data_limpa = str(data_str).strip()
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(data_limpa, fmt).date()
            except ValueError:
                continue
        return None

    def calcular_depreciacao(
        self,
        data_aquisicao: Optional[Union[str, date]],
        valor_compra: float,
        taxa_depreciacao_anual: float,
        data_referencia: Optional[Union[str, date]] = None,
    ) -> CalculoDepreciacaoDTO:
        """
        Calcula a depreciação contábil pelo método de Linha Reta:
            DepreciacaoAnual  = ValorCompra * (TaxaAnual / 100)
            AnosEmUso         = (Hoje - DataAquisicao) / 365.25
            DepAcumulada      = DepreciacaoAnual * AnosEmUso
            ValorAtual        = MAX(ValorCompra - DepAcumulada, 0)
        """
        dt_aquisicao = self._parse_data(data_aquisicao)
        if not dt_aquisicao:
            return CalculoDepreciacaoDTO(
                valido=False,
                mensagem="Data de aquisição não informada ou formato inválido.",
            )

        try:
            val_compra = float(valor_compra or 0.0)
        except (ValueError, TypeError):
            val_compra = 0.0

        if val_compra <= 0:
            return CalculoDepreciacaoDTO(
                valido=False,
                mensagem="Valor de compra deve ser maior que zero.",
            )

        try:
            taxa_anual = float(taxa_depreciacao_anual or 0.0)
        except (ValueError, TypeError):
            taxa_anual = 0.0

        if taxa_anual <= 0:
            return CalculoDepreciacaoDTO(
                valido=False,
                mensagem="Taxa de depreciação anual (%) deve ser superior a zero.",
            )

        dt_ref = self._parse_data(data_referencia) or date.today()
        if dt_ref < dt_aquisicao:
            return CalculoDepreciacaoDTO(
                valido=False,
                mensagem="Data de referência não pode ser anterior à data de aquisição.",
            )

        dias_uso = (dt_ref - dt_aquisicao).days
        anos_em_uso = round(dias_uso / 365.25, 2)

        dep_anual = round(val_compra * (taxa_anual / 100.0), 2)
        dep_acumulada = round(dep_anual * anos_em_uso, 2)
        valor_atual = max(round(val_compra - dep_acumulada, 2), 0.0)

        return CalculoDepreciacaoDTO(
            data_aquisicao=dt_aquisicao.strftime("%d/%m/%Y"),
            valor_compra=val_compra,
            taxa_depreciacao_anual=taxa_anual,
            anos_em_uso=anos_em_uso,
            depreciacao_anual=dep_anual,
            depreciacao_acumulada=dep_acumulada,
            valor_atual=valor_atual,
            valido=True,
            mensagem="Cálculo de depreciação realizado com sucesso.",
        )

    def validar_bem(self, dados: Dict[str, Any]) -> ResultadoOperacaoAtivo:
        """Valida campos obrigatórios cadastrais de acordo com as regras de negócio."""
        num_bem = str(dados.get("numero_do_bem") or "").strip()
        if not num_bem:
            return ResultadoOperacaoAtivo(False, "O número/código do bem é obrigatório.")

        empcod = str(dados.get("empcod") or "").strip()
        if not empcod:
            return ResultadoOperacaoAtivo(False, "A empresa é obrigatória.", codigo=num_bem)

        cctrl = str(dados.get("geocctrlcodestr") or "").strip()
        if not cctrl:
            return ResultadoOperacaoAtivo(False, "O centro de controle/custo é obrigatório.", codigo=num_bem)

        categ = str(dados.get("codigo_categoria_bem") or "").strip()
        if not categ:
            return ResultadoOperacaoAtivo(False, "A categoria do bem é obrigatória.", codigo=num_bem)

        descr = str(dados.get("descricao_do_bem") or "").strip()
        if not descr:
            return ResultadoOperacaoAtivo(False, "A descrição do bem é obrigatória.", codigo=num_bem)

        classif = str(dados.get("codigo_classificacaoativoimobilizado") or "").strip()
        if not classif:
            return ResultadoOperacaoAtivo(False, "A classificação do ativo imobilizado é obrigatória.", codigo=num_bem)

        loc = str(dados.get("codigo_localizacao") or "").strip()
        if not loc:
            return ResultadoOperacaoAtivo(False, "A localização física do bem é obrigatória.", codigo=num_bem)

        return ResultadoOperacaoAtivo(True, "Dados válidos.", codigo=num_bem)

    def salvar_bem(self, dados: Dict[str, Any], modo_inclusao: bool) -> ResultadoOperacaoAtivo:
        """Valida, calcula depreciação e persiste a inclusão ou alteração."""
        val = self.validar_bem(dados)
        if not val.sucesso:
            return val

        # Validação de data de aquisição se informada
        dt_aq = dados.get("data_aquisicao")
        if dt_aq:
            parsed_aq = self._parse_data(dt_aq)
            if not parsed_aq:
                return ResultadoOperacaoAtivo(False, "Data de aquisição inválida. Utilize o formato DD/MM/AAAA.")
            dados["data_aquisicao"] = parsed_aq.strftime("%Y-%m-%d")

        dt_rev = dados.get("data_ultima_revisao")
        if dt_rev:
            parsed_rev = self._parse_data(dt_rev)
            if not parsed_rev:
                return ResultadoOperacaoAtivo(False, "Data de revisão inválida. Utilize o formato DD/MM/AAAA.")
            dados["data_ultima_revisao"] = parsed_rev.strftime("%Y-%m-%d")

        try:
            if modo_inclusao:
                self._repo.inserir_bem(dados)
                return ResultadoOperacaoAtivo(True, "Bem de ativo imobilizado incluído com sucesso!", dados.get("numero_do_bem"))
            else:
                self._repo.atualizar_bem(dados)
                return ResultadoOperacaoAtivo(True, "Bem de ativo imobilizado atualizado com sucesso!", dados.get("numero_do_bem"))
        except Exception as exc:
            logger.exception("Erro ao salvar bem de ativo imobilizado: %s", exc)
            return ResultadoOperacaoAtivo(False, f"Erro ao salvar bem no banco:\n{exc}", dados.get("numero_do_bem"))

    def excluir_bem(self, numero_do_bem: str) -> ResultadoOperacaoAtivo:
        if not numero_do_bem:
            return ResultadoOperacaoAtivo(False, "Número do bem não informado.")
        try:
            self._repo.excluir_bem(numero_do_bem)
            return ResultadoOperacaoAtivo(True, f"Bem {numero_do_bem} excluído com sucesso!", numero_do_bem)
        except Exception as exc:
            logger.exception("Erro ao excluir bem: %s", exc)
            return ResultadoOperacaoAtivo(False, f"Erro ao excluir bem:\n{exc}", numero_do_bem)

    def obter_bem(self, numero_do_bem: str, empcod: str) -> Optional[Dict[str, Any]]:
        bem = self._repo.obter_bem(numero_do_bem, empcod)
        if bem and bem.get("data_aquisicao") and bem.get("valor_compra") and bem.get("taxa_depreciacao_anual"):
            calc = self.calcular_depreciacao(
                bem["data_aquisicao"],
                bem["valor_compra"],
                bem["taxa_depreciacao_anual"],
            )
            bem["depreciacao"] = calc
        return bem

    def listar_bens(self, empcod: str) -> List[Dict[str, Any]]:
        bens = self._repo.listar_bens(empcod)
        for b in bens:
            if b.get("data_aquisicao") and b.get("valor_compra") and b.get("taxa_depreciacao_anual"):
                calc = self.calcular_depreciacao(
                    b["data_aquisicao"],
                    b["valor_compra"],
                    b["taxa_depreciacao_anual"],
                )
                b["depreciacao"] = calc
        return bens

    def proximo_codigo(self, empcod: str) -> str:
        return self._repo.obter_proximo_numero_bem(empcod)

    # ── Métodos de Apoio aos Seletores / Lookups ──────────────────────────

    def obter_centros_controle(self) -> List[Dict[str, str]]:
        return self._repo.listar_centros_controle()

    def obter_categorias(self) -> List[Dict[str, str]]:
        return self._repo.listar_categorias()

    def obter_classificacoes(self, categoria_cod: str = "") -> List[Dict[str, str]]:
        return self._repo.listar_classificacoes(categoria_cod)

    def obter_localizacoes(self) -> List[Dict[str, str]]:
        return self._repo.listar_localizacoes()

    def obter_funcionarios(self) -> List[Dict[str, str]]:
        return self._repo.listar_funcionarios()

    def obter_marcas(self) -> List[Dict[str, str]]:
        return self._repo.listar_marcas()

    def obter_status(self) -> List[Dict[str, str]]:
        return self._repo.listar_status()

    def obter_empresas(self) -> List[Dict[str, str]]:
        return self._repo.listar_empresas()
