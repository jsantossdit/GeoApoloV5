"""
Leitor e normalizador de planilhas de inscrições de eventos (CSV/Excel).
GeoApolo V5
"""

import csv
import re
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from .models import InscricaoEventoDTO


def somente_digitos(valor: Any) -> str:
    """Extrai somente caracteres numéricos de um texto."""
    if not valor:
        return ""
    return re.sub(r"\D", "", str(valor))


class PlanilhaInscricoesReader:
    """Carrega e normaliza planilhas tabulares de inscrições de eventos."""

    ALIASES = {
        "documento": ["documento", "cpf", "cnpj", "doc", "cliente_documento", "clientedocumento", "cpf_cnpj"],
        "nome": ["nome", "cliente_nome", "clientenome", "participante", "comprador", "inscrito"],
        "email": ["email", "e-mail", "cliente_email", "clienteemail"],
        "telefone": ["telefone", "celular", "fone", "cliente_fones", "clientefones", "whatsapp"],
        "cidade": ["cidade", "municipio"],
        "uf": ["uf", "estado"],
        "cep": ["cep", "codigo_postal"],
        "endereco": ["endereco", "logradouro", "rua"],
        "valor": ["valor", "valor_venda", "valorvenda", "preco", "total"],
        "status": ["status", "status_inscricao", "statusinscricao", "situacao"],
        "fatura": ["fatura", "codigo_pedido", "transacao", "pedido"],
    }

    @classmethod
    def _normalizar_header(cls, cabecalhos: List[str]) -> Dict[str, int]:
        mapa = {}
        for idx, col in enumerate(cabecalhos):
            col_norm = col.strip().lower().replace(" ", "_").replace("-", "_")
            for campo_alvo, aliases in cls.ALIASES.items():
                if col_norm in aliases:
                    mapa[campo_alvo] = idx
                    break
        return mapa

    @classmethod
    def ler_arquivo(cls, caminho_arquivo: str, evento_id: str = "") -> List[InscricaoEventoDTO]:
        caminho = str(caminho_arquivo).lower()
        if caminho.endswith(".xlsx") or caminho.endswith(".xls"):
            return cls._ler_excel(caminho_arquivo, evento_id)
        return cls._ler_csv(caminho_arquivo, evento_id)

    @classmethod
    def _ler_csv(cls, caminho_arquivo: str, evento_id: str) -> List[InscricaoEventoDTO]:
        inscricoes = []
        # Tenta detectar encoding comum em planilhas brasileiras (utf-8, latin-1)
        for enc in ["utf-8-sig", "latin-1", "cp1252"]:
            try:
                with open(caminho_arquivo, mode="r", encoding=enc) as f:
                    amostra = f.read(4096)
                    f.seek(0)
                    dialect = csv.Sniffer().sniff(amostra, delimiters=";,|\t,")
                    reader = csv.reader(f, dialect)
                    cabecalho = next(reader, None)
                    if not cabecalho:
                        return []

                    mapa = cls._normalizar_header(cabecalho)
                    for linha in reader:
                        if not linha or not any(linha):
                            continue
                        inscricoes.append(cls._converter_linha(linha, mapa, evento_id))
                break
            except Exception:
                continue
        return inscricoes

    @classmethod
    def _ler_excel(cls, caminho_arquivo: str, evento_id: str) -> List[InscricaoEventoDTO]:
        try:
            import openpyxl

            wb = openpyxl.load_workbook(caminho_arquivo, data_only=True)
            sheet = wb.active
            rows = list(sheet.iter_rows(values_only=True))
            if not rows:
                return []

            cabecalho = [str(c or "") for c in rows[0]]
            mapa = cls._normalizar_header(cabecalho)

            inscricoes = []
            for r in rows[1:]:
                if not r or not any(r):
                    continue
                inscricoes.append(cls._converter_linha(r, mapa, evento_id))
            return inscricoes
        except ImportError:
            # Fallback para leitura como CSV se openpyxl não estiver instalado
            return cls._ler_csv(caminho_arquivo, evento_id)

    @classmethod
    def _converter_linha(cls, linha: Any, mapa: Dict[str, int], evento_id: str) -> InscricaoEventoDTO:
        def get_val(campo: str, padrao: str = "") -> str:
            if campo in mapa and mapa[campo] < len(linha):
                v = linha[mapa[campo]]
                return str(v).strip() if v is not None else padrao
            return padrao

        def get_float(campo: str) -> float:
            txt = get_val(campo, "0")
            txt = txt.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
            try:
                return float(txt)
            except ValueError:
                return 0.0

        doc = somente_digitos(get_val("documento"))
        nome = get_val("nome", "PARTICIPANTE")
        email = get_val("email")
        fone = get_val("telefone")
        cidade = get_val("cidade")
        uf = get_val("uf")
        cep = somente_digitos(get_val("cep"))
        endereco = get_val("endereco")
        val = get_float("valor")
        status = get_val("status", "Aprovado")
        fatura = get_val("fatura")

        return InscricaoEventoDTO(
            evento_id=evento_id,
            documento=doc,
            nome=nome,
            email=email,
            telefone=fone,
            fatura=fatura,
            status_inscricao=status,
            valor_venda=val,
            endereco=endereco,
            cidade=cidade,
            uf=uf,
            cep=cep,
        )
