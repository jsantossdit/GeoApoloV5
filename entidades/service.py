"""
Camada de Negócio e Serviços para Entidades em Python.
Correspondente a unt_entidades_service.pas.

Totalmente isolada de interface visual (Tkinter/Web) e frameworks de tela.
"""

import json
import logging
from typing import List, Dict, Any, Tuple, Optional
from entidades.models import (
    ItemComparacao,
    DecisaoLinha,
    ResultadoOperacao,
    EntidadeEdicao,
)
from entidades.repository import EntidadeRepository

logger = logging.getLogger(__name__)

MAPA_CAMPOS = [
    {"label": "Nome", "sve": "geoentnome", "alvo": "entnome"},
    {"label": "CPF / CNPJ", "sve": "Documento", "alvo": "EntCpfCgc"},
    {"label": "RG / IE", "sve": "EntRgIe", "alvo": "EntRgIe"},
    {"label": "Logradouro", "sve": "tipolograd", "alvo": "EntLograd"},
    {"label": "Endereço", "sve": "geoentender", "alvo": "entender"},
    {"label": "Número", "sve": "geoenderno", "alvo": "entenderno"},
    {"label": "Complemento", "sve": "geoentendercomp", "alvo": "EntEnderComp"},
    {"label": "Bairro", "sve": "geoentbair", "alvo": "entbair"},
    {"label": "CEP", "sve": "geoentcep", "alvo": "entcep"},
    {"label": "Cidade", "sve": "cidnomecomp", "alvo": "cidnomecomp"},
    {"label": "Estado", "sve": "ufsigla", "alvo": "ufsigla"},
    {"label": "E-mail", "sve": "Email", "alvo": "Email"},
    {"label": "Telefone", "sve": "Telefone", "alvo": "Telefone"},
    {"label": "Data Aniversário", "sve": "geoentdataanivfund", "alvo": "EntDataAnivFund"},
]


class EntidadeService:
    """
    Regras de Negócio, orquestração e sanitização de dados para o módulo de Entidades.
    """

    def __init__(self, repository: EntidadeRepository):
        self._repo = repository

    def pode_exportar_para_alvo(self, base_dados: str, observacoes: Optional[str]) -> Tuple[bool, str]:
        """
        Valida se o registro atual está apto a ser exportado para a API Alvo.
        """
        if base_dados == "Alvo":
            return False, "Você já está na base Alvo; a exportação só é permitida da base GeoApolo."

        if observacoes and observacoes.strip():
            return False, "Existem observações que precisam de moderação manual antes da exportação."

        return True, ""

    def executar_acao_ignorar(
        self, geoentcod: str, usucod_apolo: str, cod_empresa: str, cod_usuario: str
    ) -> ResultadoOperacao:
        """
        Marca o registro como ignorado para não travar a fila de sincronização.
        """
        try:
            sucesso = self._repo.ignorar_atualizacao_alvo(
                geoentcod, usucod_apolo, cod_empresa, cod_usuario
            )
            if sucesso:
                return ResultadoOperacao(
                    sucesso=True,
                    mensagem="Registro marcado como ignorado no Alvo com sucesso.",
                    codigo=geoentcod,
                )
            return ResultadoOperacao(
                sucesso=False,
                mensagem="Não foi possível atualizar o status do registro.",
            )
        except Exception as exc:
            logger.exception("Falha ao ignorar entidade: %s", exc)
            return ResultadoOperacao(
                sucesso=False,
                mensagem=f"Erro interno ao processar operação: {str(exc)}",
            )

    def obter_ou_resolver_entcod_alvo(self, geoentcod: str, entcod_atual: Optional[str]) -> Optional[str]:
        """
        Obtém o entcod ou tenta correlacionar automaticamente buscando pelo CPF/CNPJ.
        """
        if entcod_atual and str(entcod_atual).strip():
            return str(entcod_atual).strip()

        return self._repo.atualizar_entcod_alvo_via_cpf(geoentcod)

    def comparar_cadastros(
        self, sve_data: Dict[str, Any], alvo_data: Dict[str, Any]
    ) -> List[ItemComparacao]:
        """
        Compara lado a lado os campos dos cadastros GeoApolo e Alvo.
        Retorna apenas as linhas com divergências.
        """
        diferencas: List[ItemComparacao] = []

        for idx, mapa in enumerate(MAPA_CAMPOS):
            val_sve = str(sve_data.get(mapa["sve"]) or "").strip()
            val_alvo = str(alvo_data.get(mapa["alvo"]) or "").strip()

            item = ItemComparacao(
                indice_mapa=idx,
                rotulo=mapa["label"],
                campo_sve=mapa["sve"],
                campo_alvo=mapa["alvo"],
                valor_sve=val_sve,
                valor_alvo=val_alvo,
                decisao=DecisaoLinha.NENHUMA,
            )

            if item.eh_diferente:
                diferencas.append(item)

        return diferencas

    def gerar_payload_sobreposicao(self, itens: List[ItemComparacao]) -> Dict[str, Any]:
        """
        Gera o dicionário JSON estruturado para enviar ao endpoint de alteração da API Alvo.
        """
        dados_entidade: Dict[str, Any] = {
            "Operacao": "A",
            "Natureza": "Consumidor",
        }

        for item in itens:
            if item.decisao == DecisaoLinha.MANTER_SVE:
                valor_final = item.valor_sve
            elif item.decisao == DecisaoLinha.MANTER_ALVO:
                valor_final = item.valor_alvo
            else:
                continue

            rotulo = item.rotulo.upper()
            if rotulo == "NOME":
                dados_entidade["Nome"] = valor_final
            elif rotulo == "CPF / CNPJ":
                dados_entidade["CPFCNPJ"] = valor_final
            elif rotulo == "RG / IE":
                dados_entidade["RGIE"] = valor_final
            elif rotulo == "LOGRADOURO":
                dados_entidade["CodigoTipoLograd"] = valor_final
            elif rotulo == "ENDEREÇO":
                dados_entidade["Endereco"] = valor_final
            elif rotulo == "NÚMERO":
                dados_entidade["NumeroEndereco"] = valor_final
            elif rotulo == "COMPLEMENTO":
                dados_entidade["ComplementoEndereco"] = valor_final
            elif rotulo == "BAIRRO":
                dados_entidade["Bairro"] = valor_final
            elif rotulo == "CEP":
                dados_entidade["Cep"] = valor_final
            elif rotulo == "CIDADE":
                dados_entidade["Cidade"] = valor_final
            elif rotulo == "ESTADO":
                dados_entidade["UF"] = valor_final
            elif rotulo == "DATA ANIVERSÁRIO":
                dados_entidade["DataFundacao"] = valor_final

        return {"Operacao": "A", "Entidade": dados_entidade}

    def mapear_para_edicao(self, registro: Dict[str, Any], modo_integracao: str) -> EntidadeEdicao:
        """
        Converte o dicionário bruto da query para o modelo EntidadeEdicao (DTO).
        """
        return EntidadeEdicao(
            codigo=str(registro.get("entcod") or ""),
            codigo_alternativo=str(registro.get("geoentcod") or ""),
            tipo_tratamento=str(registro.get("tipotratcod") or ""),
            nome=str(registro.get("entnome") or ""),
            nome_fantasia=str(registro.get("entnomefant") or ""),
            cpf_cnpj=str(registro.get("entcpfcgc") or ""),
            rg_ie=str(registro.get("entrgie") or ""),
            cep=str(registro.get("entcep") or ""),
            logradouro=str(registro.get("entlograd") or ""),
            endereco=str(registro.get("entender") or ""),
            numero=str(registro.get("entenderno") or ""),
            complemento=str(registro.get("entendercomp") or ""),
            bairro=str(registro.get("entbair") or ""),
            codigo_cidade=str(registro.get("cidcod") or ""),
            nome_cidade=str(registro.get("cidnomecomp") or ""),
            uf=str(registro.get("ufsigla") or ""),
            genero=str(registro.get("entgenero") or ""),
            estado_civil=str(registro.get("entestcivil") or ""),
            data_nascimento=str(registro.get("entdataanivfund") or ""),
            data_cadastro=str(registro.get("entdesdedata") or ""),
            nome_pai=str(registro.get("entnomepai") or ""),
            nome_mae=str(registro.get("entnomemae") or ""),
            possui_filhos=str(registro.get("entpossuifilho") or "").strip().lower() == "sim",
            valor_contribuicao=float(registro.get("USERValor_Contribuicao") or 25.0),
            diocese_id=str(registro.get("USERDiocese_id") or ""),
            nome_diocese=str(registro.get("USERNomeDiocese") or ""),
            observacoes=str(registro.get("Entobservacoes") or ""),
            atualizou_apolo=str(registro.get("atualizou_apolo") or "N"),
            modo_integracao=modo_integracao,
        )

    def validar_dados(self, dados: Dict[str, Any]) -> Tuple[bool, str]:
        """Valida campos obrigatórios da entidade."""
        if not dados.get("geoentcod") and not dados.get("entcod"):
            return False, "O código da entidade é obrigatório."
        if not dados.get("geoentnome") and not dados.get("entnome"):
            return False, "O nome da entidade é obrigatório."
        if not dados.get("geoentender") and not dados.get("entender"):
            return False, "O endereço é obrigatório."
        if not dados.get("geoenderno") and not dados.get("entenderno"):
            return False, "O número do endereço é obrigatório."
        if not dados.get("geoentcep") and not dados.get("entcep"):
            return False, "O CEP é obrigatório."
        if not dados.get("geocidcod") and not dados.get("cidcod"):
            return False, "A cidade é obrigatória."
        return True, ""

    def salvar_entidade(self, dados: Dict[str, Any], base_dados: str = "GeoApolo", modo_inclusao: bool = True) -> ResultadoOperacao:
        """Valida e persiste a entidade no banco de dados correspondente."""
        valido, msg_erro = self.validar_dados(dados)
        if not valido:
            return ResultadoOperacao(sucesso=False, mensagem=msg_erro)

        try:
            if base_dados == "GeoApolo":
                self._repo.gravar_entidade_geoapolo(dados, modo_inclusao=modo_inclusao)
            else:
                self._repo.gravar_entidade_alvo(dados)

            cod = dados.get("geoentcod") or dados.get("entcod")
            return ResultadoOperacao(sucesso=True, mensagem="Entidade gravada com sucesso!", codigo=str(cod))
        except Exception as exc:
            logger.exception("Falha ao salvar entidade no banco: %s", exc)
            return ResultadoOperacao(sucesso=False, mensagem=f"Erro ao salvar no banco: {str(exc)}")

