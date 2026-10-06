"""
Camada de Negócio e Serviços para Entidades em Python.
Correspondente a unt_entidades_service.pas.

Totalmente isolada de interface visual (Tkinter/Web) e frameworks de tela.
"""

import sys
from pathlib import Path

# Garante que o diretório raiz esteja no sys.path
_raiz_projeto = str(Path(__file__).resolve().parent.parent)
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

import json
import logging
import re
from typing import List, Dict, Any, Tuple, Optional

try:
    from entidades.models import (
        ItemComparacao,
        DecisaoLinha,
        ResultadoOperacao,
        EntidadeEdicao,
    )
    from entidades.repository import EntidadeRepository
except (ImportError, ModuleNotFoundError):
    from models import (
        ItemComparacao,
        DecisaoLinha,
        ResultadoOperacao,
        EntidadeEdicao,
    )
    from repository import EntidadeRepository

logger = logging.getLogger(__name__)

MAPA_CAMPOS = [
    {"label": "Código Alvo (entcod)", "sve": "entcod", "alvo": "entcod"},
    {"label": "Código Geo (geoentcod)", "sve": "geoentcod", "alvo": "geoentcod"},
    {"label": "Nome", "sve": "geoentnome", "alvo": "entnome"},
    {"label": "CPF / CNPJ", "sve": "Documento", "alvo": "EntCpfCgc"},
    {"label": "RG / IE", "sve": "EntRgIe", "alvo": "EntRgIe"},
    {"label": "Logradouro", "sve": "logradouro", "alvo": "EntLograd"},
    {"label": "Endereço", "sve": "geoentender", "alvo": "entender"},
    {"label": "Número", "sve": "geoenderno", "alvo": "entenderno"},
    {"label": "Complemento", "sve": "geoentendercomp", "alvo": "EntEnderComp"},
    {"label": "Bairro", "sve": "geoentbair", "alvo": "entbair"},
    {"label": "CEP", "sve": "geoentcep", "alvo": "entcep"},
    {"label": "Cidade", "sve": "cidnomecomp", "alvo": "cidnomecomp"},
    {"label": "Estado", "sve": "ufsigla", "alvo": "ufsigla"},
    {"label": "Gênero", "sve": "geoentgenero", "alvo": "EntGenero"},
    {"label": "E-mail", "sve": "Email", "alvo": "Email"},
    {"label": "Telefone", "sve": "Telefone", "alvo": "Telefone"},
    {"label": "Data Aniversário", "sve": "geoentdataanivfund", "alvo": "EntDataAnivFund"},
]


def _formatar_data_br(dt_val: Any) -> str:
    """Formata datas no padrão DD/MM/AAAA conforme padrão do sistema operacional."""
    if not dt_val:
        return ""
    if hasattr(dt_val, "strftime"):
        return dt_val.strftime("%d/%m/%Y")
    s = str(dt_val).strip()
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return f"{s[8:10]}/{s[5:7]}/{s[0:4]}"
    if len(s) >= 10 and s[2] == "/" and s[5] == "/":
        return s[:10]
    return s


def _formatar_documento(doc: Any) -> str:
    """Aplica máscara padrão de CPF (000.000.000-00) ou CNPJ (00.000.000/0000-00)."""
    s = re.sub(r"\D", "", str(doc or ""))
    if len(s) == 11:
        return f"{s[:3]}.{s[3:6]}.{s[6:9]}-{s[9:]}"
    elif len(s) == 14:
        return f"{s[:2]}.{s[2:5]}.{s[5:8]}/{s[8:12]}-{s[12:]}"
    return str(doc or "").strip()



def _par_ou_impar(val: Any) -> str:
    """Calcula se o número de endereço é par ou ímpar, conforme Delphi unt_entidades.pas."""
    try:
        import re
        numeros = re.findall(r"\d+", str(val or ""))
        if numeros:
            n = int(numeros[-1])
            return "Par" if n % 2 == 0 else "Impar"
    except Exception:
        pass
    return ""


def _formatar_iso8601(dt_val: Any) -> Optional[str]:
    """Converte datas para o formato ISO 8601 exigido pela API Alvo (ex: 2026-09-21T00:00:00.000Z)."""
    if not dt_val:
        return None
    try:
        from datetime import datetime
        if isinstance(dt_val, str):
            dt_str = dt_val.strip()
            if not dt_str or dt_str.lower() in ("none", "null"):
                return None
            if "T" in dt_str:
                return dt_str
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S"):
                try:
                    d = datetime.strptime(dt_str, fmt)
                    return d.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                except ValueError:
                    pass
            return dt_str
        elif hasattr(dt_val, "strftime"):
            return dt_val.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    except Exception:
        pass
    return str(dt_val)


def _normalizar_genero_alvo(valor: Any) -> Optional[str]:
    """
    Normaliza o campo Genero para o padrão exigido pela API Alvo (Riosoft.BusinessObjects.Apolo).
    A regra corporativa do Apolo WebApi (BrokenRulesException) impõe: 'Genero can not exceed 1 characters'.
    Valores válidos retornados:
      - 'M' para Masculino
      - 'F' para Feminino
      - 'N' para Nenhum / Não informado
      - 1º caractere maiúsculo se outro código
      - None se vazio ou nulo
    """
    if not valor:
        return None
    val_str = str(valor).strip().upper()
    if not val_str:
        return None
    if val_str.startswith("M") or val_str in ("1", "HOMEM", "MALE"):
        return "M"
    if val_str.startswith("F") or val_str in ("2", "MULHER", "FEMALE"):
        return "F"
    if val_str.startswith("N") or val_str in ("0", "OUTRO", "INDEFINIDO", "NÃO INFORMADO", "NAO INFORMADO"):
        return "N"
    return val_str[0]


def _normalizar_tipo_telefone_alvo(valor: Any) -> str:
    """
    Normaliza o tipo de telefone para o padrão aceito pela API Alvo e dbo.ENT_FONE (CK_ENTFONE_001).
    Regra: sempre que não tiver o entfonetipo (vazio, nulo ou sigla legada 'CEL'), define como 'Pessoal'.
    """
    if not valor:
        return "Pessoal"
    v = str(valor).strip()
    if not v or v.upper() in ("CEL", "NONE", "NULL"):
        return "Pessoal"
    v_upper = v.upper()
    if v_upper in ("PESSOAL", "PES"):
        return "Pessoal"
    if v_upper.startswith("COM"):
        return "Comercial"
    if v_upper.startswith("RES"):
        return "Residencial"
    if v_upper.startswith("CEL"):
        return "Celular"
    if v_upper.startswith("REC"):
        return "Recado"
    if v_upper.startswith("FAX"):
        return "Fax"
    if v_upper.startswith("GRAT"):
        return "Gratuito"
    return v.capitalize()


class EntidadeService:
    """
    Regras de Negócio, orquestração e sanitização de dados para o módulo de Entidades.
    """

    def __init__(self, repository: EntidadeRepository):
        self._repo = repository

    def vincular_entcod(self, geoentcod: str, entcod: str) -> bool:
        """Vincula o entcod oficial gerado pelo Alvo à entidade local."""
        return self._repo.vincular_entcod(geoentcod, entcod)

    def pode_exportar_para_alvo(self, base_dados: str, observacoes: Optional[str]) -> Tuple[bool, str]:
        """
        Valida se o registro atual está apto a ser exportado para a API Alvo.
        Regra:
        - Bloqueia se a base selecionada for Alvo (exportação ocorre de GeoApolo/GeoAlvo para Alvo).
        - Se contiver [PENDÊNCIAS] (ou variação [PEND), bloqueia a exportação.
        - Se contiver [INFORMAÇÕES] sem pendências, a exportação é permitida normalmente.
        """
        if base_dados == "Alvo":
            return False, "Você já está na base Alvo; a exportação só é permitida da base GeoApolo."

        obs_upper = (observacoes or "").upper()
        if "[PEND" in obs_upper:
            return False, "A exportação para o Alvo foi interrompida pois esta entidade possui [PENDÊNCIAS] registradas!"

        return True, ""

    def montar_payload_entidade_alvo(
        self, geoentcod: str, operacao: str = "I", entcod: str = "", modo: str = "php"
    ) -> Dict[str, Any]:
        """
        Monta o payload para a API Alvo (https://alvo.rccbrasil.org.br/api).
        Modos:
          - 'php' (padrão): Baseado no esquema funcional IntegracaoPHP.php (DTO de 21 propriedades,
            endereço e dados bancários diretamente na raiz, filtrando nulos e sem arrays 'dummy'
            com datas de 100 anos, contatos vazios ou strings literais 'null').
          - 'delphi': Baseado na serialização legada do Delphi unt_AlvoEntidade.pas.
        """
        dados = self._repo.carregar_dados_completos_entidade_geoapolo(geoentcod)
        if not dados:
            dados = self._repo.obter_entidade_geoapolo(geoentcod) if hasattr(self._repo, "obter_entidade_geoapolo") else {}

        cpf_doc, rg_doc = self._repo.obter_cpf_rg_documentos(geoentcod)
        cpf_final = cpf_doc or str(dados.get("entcpfcgc") or "")
        rg_final = rg_doc or str(dados.get("entrgie") or "")

        num_end = str(dados.get("entenderno") or dados.get("geoenderno") or "")
        par_impar = _par_ou_impar(num_end)

        # Categorias
        cats_raw = self._repo.listar_categorias_entidade(geoentcod, base_dados="GeoApolo")
        categorias_payload = []
        for c in cats_raw:
            cat_cod = str(c.get("categcodestr") or c.get("Codigo") or c.get("codigo") or "")
            if cat_cod:
                categorias_payload.append({
                    "Operacao": "I",
                    "Codigo": cat_cod,
                    "AtivaTabelaPreco": "Sim"
                })
        if not categorias_payload:
            cat_str = str(dados.get("categcodestr") or dados.get("geocategcodestr") or "").strip()
            if cat_str:
                for cat_part in cat_str.replace(";", ",").split(","):
                    cp = cat_part.strip()
                    if cp:
                        categorias_payload.append({
                            "Operacao": "I",
                            "Codigo": cp,
                            "AtivaTabelaPreco": "Sim"
                        })
        if not categorias_payload:
            # Garante que a entidade nunca fique sem categoria (exigência obrigatória da API Alvo)
            categorias_payload.append({
                "Operacao": "I",
                "Codigo": "03.001.001",
                "AtivaTabelaPreco": "Sim"
            })

        # Adiciona categoria 08.009 para grupos de oração e coordenadores (uso pela Loja)
        codigos_cats = [str(c.get("Codigo") or "").strip() for c in categorias_payload]
        if any(c.startswith("02.001") for c in codigos_cats) and "08.009" not in codigos_cats:
            categorias_payload.append({
                "Operacao": "I",
                "Codigo": "08.009",
                "AtivaTabelaPreco": "Sim"
            })

        # Telefones
        tels_raw = self._repo.listar_telefones_entidade(geoentcod, base_dados="GeoApolo")
        telefones_payload = []
        for i, tel in enumerate(tels_raw):
            num = str(tel.get("geotelefonenumero") or tel.get("numero") or "").strip()
            if num:
                raw_tipo_tel = tel.get("tipotelefone") or tel.get("entfonetipo") or tel.get("geotipotelefone") or tel.get("tipo")
                tipo_tel = _normalizar_tipo_telefone_alvo(raw_tipo_tel)
                telefones_payload.append({
                    "Operacao": "I",
                    "Sequencia": i + 1,
                    "Tipo": tipo_tel,
                    "entfonetipo": tipo_tel,
                    "DDI": str(tel.get("geotelefoneddi") or tel.get("ddi") or "55"),
                    "DDD": str(tel.get("geotelefoneddd") or tel.get("ddd") or ""),
                    "NumeroRamal": str(tel.get("geotelefoneramal") or tel.get("ramal") or ""),
                    "Numero": num,
                    "Principal": "Sim" if i == 0 else "Não",
                    "Descricao": "",
                    "NFe": "Não",
                    "NFSe": "Não"
                })

        # Emails / Web
        emails_raw = self._repo.listar_webcontatos_entidade(geoentcod, base_dados="GeoApolo")
        emails_payload = []
        for i, em in enumerate(emails_raw):
            email_val = str(em.get("email") or em.get("geoentwebcontatourl") or "").strip()
            if email_val and "@" in email_val:
                raw_tipo = str(em.get("tipo_contato") or em.get("entwebtipo") or "").strip().upper()
                if raw_tipo in ("COMERCIAL", "COM") or raw_tipo.startswith("COM"):
                    tipo_web = "Comercial"
                elif raw_tipo in ("FINANCEIRO", "FIN") or raw_tipo.startswith("FIN"):
                    tipo_web = "Financeiro"
                else:
                    tipo_web = "Pessoal"

                emails_payload.append({
                    "Operacao": "I",
                    "Sequencia": i + 1,
                    "Tipo": tipo_web,
                    "entwebtipo": tipo_web,
                    "Url": str(em.get("website") or "").strip(),
                    "Email": email_val,
                    "Principal": "Sim",
                    "entwebemailprinc": "Sim",
                    "NFe": "Não",
                    "NFSe": "Não",
                    "Descricao": ""
                })

        raw_dt = dados.get("geoentdataanivfund") or dados.get("entdataanivfund") or dados.get("DataFundacao")
        data_fund = _formatar_iso8601(raw_dt) or None
        tipo_fj = "Jurídica" if (str(dados.get("enttipofj") or "").upper() in ("J", "JURIDICA", "JURÍDICA") or len(re.sub(r"\D", "", cpf_final)) > 11) else "Física"
        comp_end = str(dados.get("entendercomp") or dados.get("geoentendercomp") or "").strip() or None

        # Dados bancários
        num_banco = str(dados.get("bancocod") or dados.get("NumeroBanco") or "").strip() or None
        ag_banco = str(dados.get("agenciacod") or dados.get("NumeroAgBancaria") or "").strip() or None
        cc_banco = str(dados.get("contacorrente") or dados.get("NumeroContaCorrente") or "").strip() or None
        val_contrib = float(dados.get("USERValor_Contribuicao") or dados.get("uservalor_contribuicao") or dados.get("geovalorcontribuicao") or 0.0)

        # Tipo de cobrança: obrigatório segundo regra de negócio (não pode ir nulo/vazio, padrão '0000027')
        raw_cobranca = str(dados.get("geotipocobcod") or dados.get("tipocobcod") or dados.get("CodigoTipoCobranca") or "").strip()
        if not raw_cobranca or raw_cobranca.lower() in ("none", "null", ""):
            cod_cobranca = "0000027"
        else:
            cod_cobranca = raw_cobranca

        # Região: busca no banco na tabela REGIAO conforme a UF da entidade
        uf_sigla = str(dados.get("ufsigla") or dados.get("geoufsigla") or "").strip()
        cod_regiao_resolvido = None
        if uf_sigla:
            cod_regiao_resolvido = self._repo.obter_codigo_regiao_por_uf(uf_sigla)
        if not cod_regiao_resolvido:
            cod_regiao_resolvido = str(dados.get("georegcodestr") or dados.get("regcodestr") or "").strip() or None

        codigo_val = str(entcod or dados.get("entcod") or "").strip() or None if operacao != "I" else None
        
        # Obter Gênero preenchido no GeoAlvo ou Alvo (garantindo no máx 1 caractere: 'M', 'F', 'N')
        raw_genero = str(dados.get("geoentgenero") or dados.get("entgenero") or dados.get("genero") or "").strip()
        genero_val = _normalizar_genero_alvo(raw_genero)

        lograd_val = str(dados.get("entlograd") or dados.get("tipologradabrev") or dados.get("logradouro") or dados.get("tipolograd") or "").strip() or None

        if modo == "php":
            payload_php = {
                "Operacao": operacao,
                "Codigo": codigo_val,
                "TipoFisicaJuridica": tipo_fj,
                "CPFCNPJ": cpf_final,
                "Nome": str(dados.get("geoentnome") or dados.get("entnome") or "").strip(),
                "DataFundacao": data_fund,
                "Genero": genero_val,
                "Logradouro": lograd_val,
                "CodigoTipoLograd": lograd_val,
                "Endereco": str(dados.get("geoentender") or dados.get("entender") or "").strip(),
                "NumeroEndereco": num_end or None,
                "ComplementoEndereco": comp_end,
                "Bairro": str(dados.get("entbair") or dados.get("geoentbair") or "").strip() or None,
                "Cep": str(dados.get("entcep") or dados.get("geoentcep") or "").strip() or None,
                "CodigoCidade": str(dados.get("cidcodapolo") or dados.get("cidcod") or dados.get("geocidcod") or "").strip() or None,
                "CodigoRegiao": cod_regiao_resolvido,
                "ValorContribuicao": val_contrib,
                "NumeroBanco": num_banco,
                "NumeroAgBancaria": ag_banco,
                "NumeroContaCorrente": cc_banco,
                "ComunicacaoEmail": "Sim",
                "Telefones": telefones_payload,
                "Emails": emails_payload,
                "CodigoTipoCobranca": cod_cobranca,
                "Categorias": categorias_payload,
            }
            # Remove valores None (equivalente a array_filter em IntegracaoPHP.php)
            return {k: v for k, v in payload_php.items() if v is not None}

        # Modo Delphi (compatibilidade legada)
        from datetime import datetime, timedelta
        dt_ini = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
        dt_fim = (datetime.now() + timedelta(days=36500)).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        enderecos_payload = [{
            "Operacao": "I",
            "Sequencia": 1,
            "CodigoEntidade": str(geoentcod),
            "CodigoEntidadeRelacionada": "",
            "EnderecoEntrega": "Sim",
            "EnderecoCobranca": "Não",
            "EnderecoFaturamento": "Não",
            "EnderecoColeta": "Não",
            "Nome": str(dados.get("geoentnome") or dados.get("entnome") or ""),
            "Logradouro": str(dados.get("entlograd") or dados.get("tipolograd") or ""),
            "Endereco": str(dados.get("geoentender") or dados.get("entender") or ""),
            "NumeroEndereco": num_end,
            "NumeroEnderecoParImpar": "",
            "ComplementoEndereco": str(dados.get("entendercomp") or dados.get("geoentendercomp") or ""),
            "Bairro": str(dados.get("entbair") or dados.get("geoentbair") or ""),
            "CodigoCidade": str(dados.get("cidcod") or dados.get("geocidcod") or ""),
            "Cep": str(dados.get("entcep") or dados.get("geoentcep") or ""),
            "TipoFisicaJuridica": str(dados.get("enttipofj") or dados.get("geotipofj") or "F"),
            "CPFCNPJ": cpf_final,
            "RGIE": rg_final,
            "OrgaoExpedidor": "",
            "CaixaPostal": "",
            "Email": "",
            "PaginaWeb": "",
            "NomeContato": "",
            "TextoLivre": "",
            "DataValidadeInicial": dt_ini,
            "DataValidadeFinal": dt_fim,
            "EnderecoCertificado": "Não"
        }]

        contatos_raw = self._repo.carregar_contatos_entidade(geoentcod)
        contatos_payload = []
        for i, cont in enumerate(contatos_raw):
            cod_contato_final = (
                str(cont.get("entCod") or "").strip()
                or str(cont.get("entcod_relacao") or "").strip()
                or str(cont.get("entcod_contato_alvo") or "").strip()
                or str(cont.get("EntCodContato") or "").strip()
            )
            contatos_payload.append({
                "Operacao": "I",
                "Codigo": cod_contato_final,
                "Nome": str(cont.get("geoentnome") or ""),
                "NomeFantasia": "",
                "Endereco": str(cont.get("geoentender") or ""),
                "NumeroEndereco": str(cont.get("geoenderno") or ""),
                "ComplementoEndereco": str(cont.get("geoentendercomp") or ""),
                "Bairro": str(cont.get("geoentbair") or ""),
                "CodigoCidade": str(cont.get("geocidcod") or ""),
                "Cep": str(cont.get("geoentcep") or ""),
                "TipoFisicaJuridica": str(cont.get("geotipofj") or "F"),
                "CPFCNPJ": "",
                "RGIE": "",
                "CodigoStatus": "Ativo",
                "Principal": "Sim" if i == 0 else "Não",
                "Email": "",
                "Telefones": [{
                    "Operacao": "I",
                    "Sequencia": 1,
                    "Tipo": _normalizar_tipo_telefone_alvo(cont.get("tipotelefone") or cont.get("entfonetipo")),
                    "entfonetipo": _normalizar_tipo_telefone_alvo(cont.get("tipotelefone") or cont.get("entfonetipo")),
                    "DDI": "55",
                    "DDD": "",
                    "Numero": str(cont.get("EntContatoCelular") or cont.get("EntContatoTelefone") or ""),
                    "Principal": "Sim"
                }] if (cont.get("EntContatoCelular") or cont.get("EntContatoTelefone")) else []
            })

        payload = {
            "Operacao": operacao,
            "Codigo": str(entcod or dados.get("entcod") or ""),
            "CodigoAlternativo": str(geoentcod),
            "CodigoTipoTratamento": str(dados.get("tipotratcod") or ""),
            "Nome": str(dados.get("geoentnome") or dados.get("entnome") or ""),
            "NomeFantasia": str(dados.get("geoentnomefantasia") or dados.get("entnomefant") or ""),
            "Natureza": "Consumidor",
            "CodigoAtivEconomica": "null",
            "CodigoOrigem": str(dados.get("origcodestr") or dados.get("geo_origcodestr") or ""),
            "EntidadeDesde": str(dados.get("entdesdedata") or ""),
            "DataCadastro": str(dados.get("entdatacad") or ""),
            "CodigoTipoLograd": str(dados.get("entlograd") or dados.get("tipolograd") or ""),
            "Endereco": str(dados.get("geoentender") or dados.get("entender") or ""),
            "NumeroEndereco": num_end,
            "NumeroEnderecoParImpar": par_impar,
            "ComplementoEndereco": str(dados.get("entendercomp") or dados.get("geoentendercomp") or ""),
            "Bairro": str(dados.get("entbair") or dados.get("geoentbair") or ""),
            "CodigoCidade": str(dados.get("cidcod") or dados.get("geocidcod") or ""),
            "Cep": str(dados.get("entcep") or dados.get("geoentcep") or ""),
            "Tipo": str(dados.get("enttipofj") or dados.get("geotipofj") or "Física"),
            "CPFCNPJ": cpf_final,
            "RGIE": rg_final,
            "OrgaoExpedidor": "",
            "Agropecuarista": "Não",
            "InscricaoAgropecuarista": "null",
            "CaixaPostal": str(dados.get("entcxapost") or ""),
            "CodigoRegiao": str(cod_regiao_resolvido or ""),
            "Conceito": str(dados.get("entconceito") or ""),
            "CodigoCondPag": "null",
            "AlteraCondicaoPagamento": "Sim",
            "CodigoTipoCobranca": str(cod_cobranca or "0000027"),
            "DataFundacao": data_fund,
            "CodigoCargo": str(dados.get("cargocodestr") or ""),
            "Genero": _normalizar_genero_alvo(dados.get("entgenero") or dados.get("geoentgenero")) or "",
            "CodigoStatus": "Ativo",
            "CaracteristicaImovel": 0,
            "ComunicacaoEtiqueta": "Sim",
            "ComunicacaoMalaDireta": "Não",
            "ComunicacaoEmail": "Sim",
            "ComunicacaoTelemarketing": "Não",
            "StringDesconto": "",
            "PercentualDesconto": 0,
            "DataValidadeDesconto": None,
            "StringAcrescimo": "",
            "PercentualAcrescimo": 0,
            "DataValidadeAcrescimo": None,
            "ContatoAposData": "",
            "NumeroBanco": "",
            "NumeroAgBancaria": "",
            "NumeroContaCorrente": "",
            "ValorContribuicao": val_contrib,
            "Categorias": categorias_payload,
            "Telefones": telefones_payload,
            "Enderecos": enderecos_payload,
            "Contatos": contatos_payload,
            "Emails": emails_payload,
            "Vendedores": [],
            "Documentos": []
        }
        return payload

    def garantir_contato_integrado_alvo(
        self,
        geoentcod_pai: str,
        usuario_alvo: str = "",
        senha_alvo_plana: str = "",
        api_client: Optional[Any] = None,
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Verifica se a entidade pai tem contato vinculado em USER_geoapolo_entidade_contato.
        Se tiver:
          1. Busca dados do contato no GeoAlvo.
          2. Pelo CPF, verifica se já existe no Alvo (via banco de dados ou entcod local).
          3. Se já existir, traz o entcod do Alvo e vincula.
          4. Se não encontrar, faz primeiro a integração do contato no Alvo e vincula o entcod gerado.
        Retorna (sucesso, mensagem, entcod_contato_alvo).
        """
        if not self._repo:
            return True, "Sem repositório", None
        contatos_vinculados = self._repo.obter_contatos_vinculados_geoentcod(geoentcod_pai) if hasattr(self._repo, "obter_contatos_vinculados_geoentcod") else []
        if not contatos_vinculados:
            return True, "Entidade sem contato vinculado", None

        for cont in contatos_vinculados:
            geo_contato = str(cont.get("EntCodContato") or "").strip()
            if not geo_contato:
                continue

            # 1. Verifica se o contato já possui entcod no Alvo registrado no cadastro local
            entcod_alvo = str(cont.get("entcod_relacao") or "").strip() or str(cont.get("entcod_contato_alvo") or "").strip()
            if not entcod_alvo:
                entcod_alvo = self._repo.obter_entcod_entidade(geo_contato) or ""

            # 2. Se não tem entcod local, busca no Alvo pelo CPF
            if not entcod_alvo:
                entcod_alvo = self._repo.atualizar_entcod_alvo_via_cpf(geo_contato) or ""

            if entcod_alvo:
                # Contato já existe no Alvo: vincula nas tabelas locais
                self._repo.vincular_entcod(geo_contato, entcod_alvo)
                self._repo.vincular_entcod_contato_relacao(geoentcod_pai, geo_contato, entcod_alvo)
                logger.info("Contato %s da entidade %s já existe no Alvo com entcod=%s. Vínculo atualizado.", geo_contato, geoentcod_pai, entcod_alvo)
                return True, f"Contato existente {entcod_alvo} vinculado com sucesso", entcod_alvo

            # 3. Não encontrou no Alvo: faz primeiro a integração do contato no Alvo
            logger.info("Contato %s da entidade %s não encontrado no Alvo. Iniciando integração prévia do contato...", geo_contato, geoentcod_pai)
            res_cont = self.exportar_entidade_para_alvo(
                geoentcod=geo_contato,
                usuario_alvo=usuario_alvo,
                senha_alvo_plana=senha_alvo_plana,
                api_client=api_client,
                _integrando_contato_filho=True,
            )

            if not res_cont.sucesso and not res_cont.codigo:
                logger.error("Falha ao integrar previamente o contato %s no Alvo: %s", geo_contato, res_cont.mensagem)
                return False, f"Falha na integração prévia do contato vinculado ({geo_contato}):\n{res_cont.mensagem}", None

            novo_entcod_contato = str(res_cont.codigo or "").strip()
            if novo_entcod_contato:
                self._repo.vincular_entcod(geo_contato, novo_entcod_contato)
                self._repo.vincular_entcod_contato_relacao(geoentcod_pai, geo_contato, novo_entcod_contato)
                logger.info("Contato %s integrado previamente no Alvo com entcod=%s. Vínculo atualizado.", geo_contato, novo_entcod_contato)
                return True, f"Contato integrado previamente com entcod={novo_entcod_contato}", novo_entcod_contato

        return True, "Contatos processados", None

    def exportar_entidade_para_alvo(
        self,
        geoentcod: str,
        usuario_alvo: str = "",
        senha_alvo_plana: str = "",
        api_client: Optional[Any] = None,
        modo_payload: str = "php",
        _integrando_contato_filho: bool = False,
    ) -> ResultadoOperacao:
        """
        Orquestra a exportação/sincronização de uma entidade GeoApolo para a API Alvo.
        1. Validação de pré-requisitos (observações pendentes, base de dados).
        2. Obtenção/Validação do Token de integração (configurado previamente ou login).
        3. Construção do payload segundo o esquema funcional do IntegracaoPHP.php (modo="php").
        4. Envio para Entidade/InserirAlterarEntidade.
        5. Atualização do entcod no banco GeoApolo em caso de sucesso.
        """
        dados = self._repo.carregar_dados_completos_entidade_geoapolo(geoentcod)
        pode, msg = self.pode_exportar_para_alvo("GeoApolo", dados.get("entobservacoes"))
        if not pode:
            return ResultadoOperacao(sucesso=False, mensagem=msg, codigo=geoentcod)

        # Validação obrigatória de CPF / CNPJ válido antes da exportação
        cpf_doc, rg_doc = self._repo.obter_cpf_rg_documentos(geoentcod)
        documento = cpf_doc or str(dados.get("entcpfcgc") or "").strip()
        digitos_doc = re.sub(r"\D", "", documento)
        tipo_fj = str(dados.get("enttipofj") or dados.get("geotipofj") or "F").upper()
        is_juridica = tipo_fj in ("J", "JURIDICA", "JURÍDICA") or len(digitos_doc) > 11

        doc_teste_pendente = None
        from entidades.documentos_teste import (
            eh_grupo_de_oracao,
            obter_proximo_documento_teste,
            consumir_documento_teste,
        )

        if not digitos_doc and eh_grupo_de_oracao(geoentcod, dados, self._repo):
            try:
                novo_doc, caminho_csv = obter_proximo_documento_teste(tipo_fj)
                self._repo.salvar_documento_entidade(
                    geoentcod, tipo="CPF/CNPJ", documento=novo_doc, observacoes="TESTE AUTO"
                )
                documento = novo_doc
                digitos_doc = re.sub(r"\D", "", documento)
                dados["entcpfcgc"] = novo_doc
                doc_teste_pendente = (caminho_csv, novo_doc)
                logger.info(
                    "Grupo de Oração %s sem documento: atribuído documento de teste %s de %s",
                    geoentcod, novo_doc, caminho_csv.name
                )
            except Exception as e_doc:
                return ResultadoOperacao(
                    sucesso=False,
                    mensagem=f"Falha ao obter documento de teste para o Grupo de Oração: {e_doc}",
                    codigo=geoentcod,
                )

        from core.validators import validar_cpf, validar_cnpj
        if is_juridica:
            if not validar_cnpj(digitos_doc):
                return ResultadoOperacao(
                    sucesso=False,
                    mensagem=f"Atenção: O CNPJ '{documento or 'não informado'}' é inválido! A entidade não pode ser exportada para o Alvo.",
                    codigo=geoentcod,
                )
        else:
            if not validar_cpf(digitos_doc):
                return ResultadoOperacao(
                    sucesso=False,
                    mensagem=f"Atenção: O CPF '{documento or 'não informado'}' é inválido! A entidade não pode ser exportada para o Alvo.",
                    codigo=geoentcod,
                )

        if api_client is None:
            from entidades.api_client import AlvoAPIClient
            api_client = AlvoAPIClient()

        # Prioriza o token permanente da integração configurado
        from configuracoes.alvo_api_config import carregar_configuracao_alvo, validar_status_token
        cfg = carregar_configuracao_alvo()
        status_token, msg_token, is_valido = validar_status_token(cfg)

        if is_valido and cfg.token.strip():
            api_client.token = cfg.token.strip()
            if cfg.base_url:
                api_client.base_url = cfg.base_url.rstrip("/")
        elif not api_client.token:
            if usuario_alvo and senha_alvo_plana:
                if not api_client.garantir_autenticacao(usuario_alvo, senha_alvo_plana):
                    return ResultadoOperacao(
                        sucesso=False,
                        mensagem="Falha ao autenticar na API Alvo. Verifique o usuário e a senha.",
                        codigo=geoentcod,
                    )
            else:
                return ResultadoOperacao(
                    sucesso=False,
                    mensagem=f"Integração API Alvo sem token válido ({msg_token}). Configure o token no menu de Configurações.",
                    codigo=geoentcod,
                )

        if not _integrando_contato_filho:
            sucesso_cont, msg_cont, cod_cont = self.garantir_contato_integrado_alvo(
                geoentcod_pai=geoentcod,
                usuario_alvo=usuario_alvo,
                senha_alvo_plana=senha_alvo_plana,
                api_client=api_client,
            )
            if not sucesso_cont:
                return ResultadoOperacao(
                    sucesso=False,
                    mensagem=msg_cont,
                    codigo=geoentcod,
                )

        try:
            operacao_envio = "A" if str(dados.get("entcod") or "").strip() else "I"
            payload = self.montar_payload_entidade_alvo(geoentcod, operacao=operacao_envio, modo=modo_payload)
            sucesso, msg_retorno, dados_json = api_client.inserir_alterar_entidade(payload)

            entcod_identificado = api_client.extrair_entcod_resposta(msg_retorno, dados_json)

            if not sucesso:
                if entcod_identificado:
                    # Entidade já existe no Alvo: armazena em variável e atualiza na tabela user_geoapolo_entidade, campo entcod
                    codigo_existente = entcod_identificado
                    self.vincular_entcod(geoentcod, codigo_existente)
                    logger.info("Entidade %s já existente no Alvo identificada com entcod=%s. Campo entcod atualizado.", geoentcod, codigo_existente)
                    if doc_teste_pendente:
                        try:
                            consumir_documento_teste(doc_teste_pendente[0], doc_teste_pendente[1])
                        except Exception as e_cons:
                            logger.warning("Falha ao consumir documento de teste: %s", e_cons)
                    return ResultadoOperacao(
                        sucesso=True,
                        mensagem=(
                            f"A entidade já existe no Alvo com o código: {codigo_existente}.\n"
                            f"O campo 'entcod' da tabela user_geoapolo_entidade foi atualizado com sucesso para '{codigo_existente}'!\n"
                            f"Detalhes: {msg_retorno}"
                        ),
                        codigo=codigo_existente,
                    )

                return ResultadoOperacao(
                    sucesso=False,
                    mensagem=f"Erro ao exportar para a API Alvo:\n{msg_retorno}",
                    codigo=geoentcod,
                )

            codigo_gerado = entcod_identificado
            if codigo_gerado:
                self.vincular_entcod(geoentcod, codigo_gerado)

            if doc_teste_pendente:
                try:
                    consumir_documento_teste(doc_teste_pendente[0], doc_teste_pendente[1])
                except Exception as e_cons:
                    logger.warning("Falha ao consumir documento de teste: %s", e_cons)

            return ResultadoOperacao(
                sucesso=True,
                mensagem=f"Entidade exportada com sucesso!\n{msg_retorno}",
                codigo=codigo_gerado or geoentcod,
            )
        except Exception as exc:
            logger.exception("Falha durante exportação da entidade %s: %s", geoentcod, exc)
            return ResultadoOperacao(
                sucesso=False,
                mensagem=f"Exceção durante exportação: {str(exc)}",
                codigo=geoentcod,
            )

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
        self,
        sve_data: Dict[str, Any],
        alvo_data: Dict[str, Any],
        incluir_referencias: bool = False,
    ) -> List[ItemComparacao]:
        """
        Compara lado a lado os campos dos cadastros GeoApolo e Alvo.
        Se incluir_referencias=True, inclui campos essenciais de identificação
        (Código Alvo, Código Geo, Nome, CPF / CNPJ) no topo mesmo que idênticos.
        """
        diferencas: List[ItemComparacao] = []
        referencias: List[ItemComparacao] = []

        CAMPOS_REFERENCIA = (
            "Código Alvo (entcod)",
            "Código Geo (geoentcod)",
            "Nome",
            "CPF / CNPJ",
        )

        for idx, mapa in enumerate(MAPA_CAMPOS):
            rotulo = mapa["label"]
            if rotulo == "Código Alvo (entcod)":
                val_sve = str(sve_data.get("entcod") or "").strip()
                val_alvo = str(alvo_data.get("entcod") or "").strip()
            elif rotulo == "Código Geo (geoentcod)":
                val_sve = str(sve_data.get("geoentcod") or "").strip()
                val_alvo = str(alvo_data.get("geoentcod") or alvo_data.get("entcod_alternativo") or val_sve).strip()
            elif rotulo == "CPF / CNPJ":
                raw_sve = str(sve_data.get("Documento") or sve_data.get("geonumerodocumento") or sve_data.get("EntCpfCgc") or sve_data.get("entcpfcgc") or sve_data.get("cpf") or "").strip()
                raw_alvo = str(alvo_data.get("EntCpfCgc") or alvo_data.get("entcpfcgc") or alvo_data.get("Documento") or alvo_data.get("cpf") or "").strip()
                val_sve = _formatar_documento(raw_sve)
                val_alvo = _formatar_documento(raw_alvo)
            elif rotulo == "Data Aniversário":
                raw_sve = sve_data.get("geoentdataanivfund") or sve_data.get("EntDataAnivFund") or sve_data.get("data_aniversario") or sve_data.get("data_nascimento")
                raw_alvo = alvo_data.get("EntDataAnivFund") or alvo_data.get("geoentdataanivfund") or alvo_data.get("data_aniversario")
                val_sve = _formatar_data_br(raw_sve)
                val_alvo = _formatar_data_br(raw_alvo)
            elif rotulo == "Logradouro":
                val_sve = str(sve_data.get("logradouro") or sve_data.get("tipolograd") or sve_data.get("entlograd") or sve_data.get("tipologradabrev") or "").strip()
                val_alvo = str(alvo_data.get("EntLograd") or alvo_data.get("entlograd") or alvo_data.get("logradouro") or "").strip()
            elif rotulo == "Gênero":
                val_sve = str(sve_data.get("geoentgenero") or sve_data.get("entgenero") or sve_data.get("genero") or "").strip()
                val_alvo = str(alvo_data.get("EntGenero") or alvo_data.get("entgenero") or alvo_data.get("genero") or "").strip()
            else:
                val_sve = str(sve_data.get(mapa["sve"]) or "").strip()
                val_alvo = str(alvo_data.get(mapa["alvo"]) or "").strip()

            item = ItemComparacao(
                indice_mapa=idx,
                rotulo=rotulo,
                campo_sve=mapa["sve"],
                campo_alvo=mapa["alvo"],
                valor_sve=val_sve,
                valor_alvo=val_alvo,
                decisao=DecisaoLinha.NENHUMA,
            )

            if item.eh_diferente:
                if rotulo == "CPF / CNPJ" and item.valor_sve and not item.valor_alvo:
                    item.decisao = DecisaoLinha.MANTER_SVE
                diferencas.append(item)
            elif incluir_referencias and rotulo in CAMPOS_REFERENCIA:
                item.decisao = DecisaoLinha.MANTER_ALVO
                referencias.append(item)

        if incluir_referencias:
            return referencias + diferencas

        return diferencas

    def gerar_payload_sobreposicao(
        self,
        itens: List[ItemComparacao],
        entcod: str = "",
        geoentcod: str = "",
        sve_data: Optional[Dict[str, Any]] = None,
        alvo_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Gera o dicionário JSON estruturado para enviar ao endpoint de alteração da API Alvo.
        Garante o envio de 'CodigoCidade' esperado pelo DTO da API Alvo ao mudar de cidade.
        """
        dados_entidade: Dict[str, Any] = {
            "Operacao": "A",
            "Natureza": "Consumidor",
        }
        if entcod:
            dados_entidade["Codigo"] = str(entcod).strip()
        if geoentcod:
            dados_entidade["CodigoAlternativo"] = str(geoentcod).strip()

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
                dados_entidade["Logradouro"] = valor_final
            elif rotulo in ("GÊNERO", "GENERO", "SEXO"):
                dados_entidade["Genero"] = _normalizar_genero_alvo(valor_final) or ""
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
                cod_cidade = ""
                if item.decisao == DecisaoLinha.MANTER_SVE and sve_data:
                    cod_cidade = str(sve_data.get("cidcodapolo") or sve_data.get("geocidcod") or sve_data.get("cidcod") or "").strip()
                elif item.decisao == DecisaoLinha.MANTER_ALVO and alvo_data:
                    cod_cidade = str(alvo_data.get("cidcod") or "").strip()

                if not cod_cidade and self._repo:
                    try:
                        uf_busca = ""
                        if item.decisao == DecisaoLinha.MANTER_SVE and sve_data:
                            uf_busca = str(sve_data.get("ufsigla") or "").strip()
                        elif alvo_data:
                            uf_busca = str(alvo_data.get("ufsigla") or "").strip()

                        cid_row = self._repo.obter_cidade_por_nome_uf(valor_final, uf_busca) if uf_busca else None
                        if not cid_row:
                            lista_c = self._repo.listar_cidades(termo=valor_final)
                            if lista_c:
                                cid_row = lista_c[0]
                        if cid_row:
                            cod_cidade = str(cid_row.get("codigo") or cid_row.get("geocidcod") or cid_row.get("cidcod") or "").strip()
                    except Exception as ex_cid:
                        logger.warning("Falha ao resolver código da cidade %s: %s", valor_final, ex_cid)

                if cod_cidade:
                    dados_entidade["CodigoCidade"] = cod_cidade
            elif rotulo in ("ESTADO", "UF"):
                dados_entidade["UF"] = valor_final
                dados_entidade["Estado"] = valor_final
            elif rotulo == "DATA ANIVERSÁRIO":
                s_dt = str(valor_final or "").strip()
                if len(s_dt) == 10 and s_dt[2] == "/" and s_dt[5] == "/":
                    dados_entidade["DataFundacao"] = f"{s_dt[6:]}-{s_dt[3:5]}-{s_dt[:2]}"
                else:
                    dados_entidade["DataFundacao"] = s_dt

        if geoentcod and self._repo and hasattr(self._repo, "carregar_contatos_entidade"):
            contatos_raw = self._repo.carregar_contatos_entidade(geoentcod)
            if contatos_raw:
                contatos_payload = []
                for i, cont in enumerate(contatos_raw):
                    cod_contato_final = (
                        str(cont.get("entCod") or "").strip()
                        or str(cont.get("entcod_relacao") or "").strip()
                        or str(cont.get("entcod_contato_alvo") or "").strip()
                        or str(cont.get("EntCodContato") or "").strip()
                    )
                    contatos_payload.append({
                        "Operacao": "I",
                        "Codigo": cod_contato_final,
                        "Nome": str(cont.get("geoentnome") or ""),
                        "NomeFantasia": "",
                        "Endereco": str(cont.get("geoentender") or ""),
                        "NumeroEndereco": str(cont.get("geoenderno") or ""),
                        "ComplementoEndereco": str(cont.get("geoentendercomp") or ""),
                        "Bairro": str(cont.get("geoentbair") or ""),
                        "CodigoCidade": str(cont.get("geocidcod") or ""),
                        "Cep": str(cont.get("geoentcep") or ""),
                        "TipoFisicaJuridica": str(cont.get("geotipofj") or "F"),
                        "CPFCNPJ": "",
                        "RGIE": "",
                        "CodigoStatus": "Ativo",
                        "Principal": "Sim" if i == 0 else "Não",
                        "Email": "",
                        "Telefones": [{
                            "Operacao": "I",
                            "Sequencia": 1,
                            "Tipo": _normalizar_tipo_telefone_alvo(cont.get("tipotelefone") or cont.get("entfonetipo")),
                            "entfonetipo": _normalizar_tipo_telefone_alvo(cont.get("tipotelefone") or cont.get("entfonetipo")),
                            "DDI": "55",
                            "DDD": "",
                            "Numero": str(cont.get("EntContatoCelular") or cont.get("EntContatoTelefone") or ""),
                            "Principal": "Sim"
                        }] if (cont.get("EntContatoCelular") or cont.get("EntContatoTelefone")) else []
                    })
                dados_entidade["Contatos"] = contatos_payload

        payload = {"Operacao": "A", "Entidade": dados_entidade}
        # Injeta chaves na raiz para suporte a ambos os esquemas de chamada da API
        if entcod:
            payload["Codigo"] = str(entcod).strip()
        if geoentcod:
            payload["CodigoAlternativo"] = str(geoentcod).strip()
        for k, v in dados_entidade.items():
            if k not in payload:
                payload[k] = v
        return payload

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

    # -------------------------------------------------------------------------
    # Categorias
    # -------------------------------------------------------------------------
    def listar_categorias(self, entcod: str, base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        return self._repo.listar_categorias_entidade(entcod, base_dados=base_dados)

    def adicionar_categoria(self, entcod: str, categcodestr: str, base_dados: str = "GeoApolo") -> bool:
        return self._repo.adicionar_categoria_entidade(entcod, categcodestr, base_dados=base_dados)

    def remover_categoria(self, entcod: str, categcodestr: str, base_dados: str = "GeoApolo") -> bool:
        return self._repo.remover_categoria_entidade(entcod, categcodestr, base_dados=base_dados)

    # -------------------------------------------------------------------------
    # Telefones & Contatos
    # -------------------------------------------------------------------------
    def listar_telefones(self, entcod: str, base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        return self._repo.listar_telefones_entidade(entcod, base_dados=base_dados)

    def salvar_telefone(self, entcod: str, dados_tel: Dict[str, Any], base_dados: str = "GeoApolo") -> bool:
        return self._repo.salvar_telefone_entidade(entcod, dados_tel, base_dados=base_dados)

    def remover_telefone(self, entcod: str, numero: str, base_dados: str = "GeoApolo") -> bool:
        return self._repo.remover_telefone_entidade(entcod, numero, base_dados=base_dados)

    # -------------------------------------------------------------------------
    # Contatos Web / E-mails
    # -------------------------------------------------------------------------
    def listar_webcontatos(self, entcod: str, base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        return self._repo.listar_webcontatos_entidade(entcod, base_dados=base_dados)

    def salvar_webcontato(self, entcod: str, dados_web: Dict[str, Any], base_dados: str = "GeoApolo") -> bool:
        return self._repo.salvar_webcontato_entidade(entcod, dados_web, base_dados=base_dados)

    def remover_webcontato(self, entcod: str, email: str, base_dados: str = "GeoApolo") -> bool:
        return self._repo.remover_webcontato_entidade(entcod, email, base_dados=base_dados)

    # -------------------------------------------------------------------------
    # Documentos
    # -------------------------------------------------------------------------
    def listar_documentos(self, entcod: str, base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        return self._repo.listar_documentos_entidade(entcod, base_dados=base_dados)

    def salvar_documento(self, entcod: str, tipo: str, documento: str, observacoes: str = "", base_dados: str = "GeoApolo") -> bool:
        return self._repo.salvar_documento_entidade(entcod, tipo, documento, observacoes=observacoes, base_dados=base_dados)

    def remover_documento(self, entcod: str, tipo: str, documento: str, base_dados: str = "GeoApolo") -> bool:
        return self._repo.remover_documento_entidade(entcod, tipo, documento, base_dados=base_dados)

    # -------------------------------------------------------------------------
    # Lookups / Consultas Auxiliares
    # -------------------------------------------------------------------------
    def listar_entidades_lookup(self, termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        return self._repo.listar_entidades_lookup(termo=termo, base_dados=base_dados)

    def listar_cidades(self, termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        return self._repo.listar_cidades(termo=termo, base_dados=base_dados)

    def obter_cidade_por_codigo(self, cidcod: str, base_dados: str = "GeoApolo") -> Optional[Dict[str, Any]]:
        return self._repo.obter_cidade_por_codigo(cidcod=cidcod, base_dados=base_dados)

    def obter_cidade_por_nome_uf(self, nome: str, uf: str, base_dados: str = "GeoApolo") -> Optional[Dict[str, Any]]:
        return self._repo.obter_cidade_por_nome_uf(nome=nome, uf=uf, base_dados=base_dados)

    def listar_categorias_lookup(self, termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        return self._repo.listar_categorias_lookup(termo=termo, base_dados=base_dados)

    def listar_cargos_lookup(self, termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        return self._repo.listar_cargos_lookup(termo=termo, base_dados=base_dados)

    def listar_tipos_cobranca(self, termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        return self._repo.listar_tipos_cobranca(termo=termo, base_dados=base_dados)

    def buscar_tipo_cobranca_por_codigo(self, codigo: str, base_dados: str = "GeoApolo") -> Optional[Dict[str, Any]]:
        return self._repo.buscar_tipo_cobranca_por_codigo(codigo, base_dados=base_dados)

    def listar_dioceses(self, termo: str = "") -> List[Dict[str, Any]]:
        return self._repo.listar_dioceses(termo=termo)

    def listar_dioceses_por_cidade(self, cidade: str = "", uf: str = "", termo: str = "") -> List[Dict[str, Any]]:
        return self._repo.listar_dioceses_por_cidade(cidade=cidade, uf=uf, termo=termo)

    def obter_nome_diocese(self, diocese_id: Any) -> str:
        return self._repo.obter_nome_diocese(diocese_id=diocese_id)

    def obter_nome_atividade_economica(self, cod: str, base_dados: str = "GeoApolo") -> str:
        return self._repo.obter_nome_atividade_economica(cod=cod, base_dados=base_dados)

    def obter_nome_origem(self, cod: str, base_dados: str = "GeoApolo") -> str:
        return self._repo.obter_nome_origem(cod=cod, base_dados=base_dados)

    def obter_nome_regiao(self, cod: str, base_dados: str = "GeoApolo") -> str:
        return self._repo.obter_nome_regiao(cod=cod, base_dados=base_dados)

    def obter_categoria_por_codigo(self, cod: str, base_dados: str = "GeoApolo") -> Dict[str, str]:
        return self._repo.obter_categoria_por_codigo(cod=cod, base_dados=base_dados)

    def listar_atividades_economicas(self, termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        return self._repo.listar_atividades_economicas(termo=termo, base_dados=base_dados)

    def listar_origens(self, termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        return self._repo.listar_origens(termo=termo, base_dados=base_dados)

    def listar_regioes(self, termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        return self._repo.listar_regioes(termo=termo, base_dados=base_dados)

    def listar_tipos_tratamento(self, base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        return self._repo.listar_tipos_tratamento(base_dados=base_dados)

    def listar_graus_escolaridade(self) -> List[Dict[str, Any]]:
        return self._repo.listar_graus_escolaridade()

    def listar_tipos_logradouro(self) -> List[Dict[str, Any]]:
        return self._repo.listar_tipos_logradouro()

    def listar_conceitos(self) -> List[Dict[str, Any]]:
        return self._repo.listar_conceitos()

    def obter_ultimas_doacoes(self, entcod: str, limite: int = 1000) -> List[Dict[str, Any]]:
        return self._repo.obter_ultimas_doacoes(entcod, limite=limite)

    def listar_bancos(self, termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        return self._repo.listar_bancos(termo=termo, base_dados=base_dados)

    def listar_agencias(self, bconum: str = "", termo: str = "", base_dados: str = "GeoApolo") -> List[Dict[str, Any]]:
        return self._repo.listar_agencias(bconum=bconum, termo=termo, base_dados=base_dados)

    def salvar_historico(self, entcod: str, novo_texto: str, usuario: str = "SISTEMA", base_dados: str = "GeoApolo") -> bool:
        return self._repo.salvar_historico_entidade(entcod=entcod, novo_texto=novo_texto, usuario=usuario, base_dados=base_dados)




