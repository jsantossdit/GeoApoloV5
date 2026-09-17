"""
Regras de Negócio e Serviços para Nomes Amigáveis de Objetos do Sistema.
GeoApolo V5
Clean Architecture: Parser heurístico de nomenclatura técnica para nomes legíveis aos usuários.
"""

import logging
import re
from typing import List, Optional

from .models import ObjetoSistemaDTO, ResultadoNomesAmigaveisDTO
from .repository import NomesAmigaveisRepository

logger = logging.getLogger(__name__)

PREFIXOS_CONTROLE = [
    "tbsheet",
    "btn",
    "mnu",
    "tbs",
    "pnl",
    "lbl",
    "cbo",
    "edt",
    "chk",
    "rbtn",
    "frm",
]

SUBSTITUICOES_COMUNS = {
    "Nfe": "NF-e",
    "Nfce": "NFC-e",
    "Cte": "CT-e",
    "Mdf": "MDF-e",
    "Cpf": "CPF",
    "Cnpj": "CNPJ",
    "Cep": "CEP",
    "Rcc": "RCC",
    "Ti": "TI",
    "Sql": "SQL",
    "Crm": "CRM",
    "Go": "Grupo de Oração (GO)",
}


class NomesAmigaveisService:
    """Regras de negócio e sugestões inteligentes de nomes legíveis de objetos."""

    def __init__(self, repository: NomesAmigaveisRepository):
        self._repo = repository

    def sugerir_nome_amigavel(self, nome_tecnico: str) -> str:
        """
        Gera uma sugestão de nome amigável a partir do nome técnico do componente.
        Ex: 'frmprincipal.btnEmitirNFe' -> 'Emitir NF-e'
            'frmprincipal.mnuCadastros' -> 'Cadastros'
        """
        raw = (nome_tecnico or "").strip()
        if not raw:
            return ""

        # Remove prefixo de form/container
        if "." in raw:
            raw = raw.split(".")[-1]

        # Remove prefixo de tipo de controle (btn, mnu, edt, etc)
        lower_raw = raw.lower()
        for pref in PREFIXOS_CONTROLE:
            if lower_raw.startswith(pref) and len(raw) > len(pref):
                raw = raw[len(pref):]
                break

        # Preserva siglas com hífen antes da quebra de maiúsculas
        siglas_especiais = [
            ("NFe", "NF-e"),
            ("NFCe", "NFC-e"),
            ("CTe", "CT-e"),
            ("MDFe", "MDF-e"),
        ]
        for sigla, formatada in siglas_especiais:
            raw = re.sub(re.escape(sigla), f" {formatada} ", raw, flags=re.IGNORECASE)

        # Separa palavras em CamelCase
        raw = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", raw)
        raw = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", raw)
        raw = raw.replace("_", " ").strip()

        # Capitalização inteligente de palavras
        partes = []
        for p in raw.split():
            if "-" in p:
                partes.append(p)
                continue
            cap = p.capitalize()
            partes.append(SUBSTITUICOES_COMUNS.get(cap, cap))

        sugestao = " ".join(partes).strip()
        return sugestao or nome_tecnico


    def listar_objetos(self, categoria: str = "", filtro: str = "") -> List[ObjetoSistemaDTO]:
        return self._repo.listar_objetos(categoria, filtro)

    def obter_objeto(self, nome_objeto: str) -> Optional[ObjetoSistemaDTO]:
        if not nome_objeto.strip():
            return None
        return self._repo.obter_objeto(nome_objeto)

    def salvar_objeto(self, dto: ObjetoSistemaDTO) -> ResultadoNomesAmigaveisDTO:
        obj_limpo = dto.nome_objeto.strip()
        if not obj_limpo:
            return ResultadoNomesAmigaveisDTO(sucesso=False, mensagem="Nome técnico do objeto é obrigatório.")

        dto.nome_objeto = obj_limpo
        dto.nome_amigavel = dto.nome_amigavel.strip() or self.sugerir_nome_amigavel(obj_limpo)
        dto.categoria = dto.categoria.strip() or "Geral"

        try:
            self._repo.salvar_objeto(dto)
            return ResultadoNomesAmigaveisDTO(
                sucesso=True,
                mensagem=f"Objeto '{obj_limpo}' salvo com sucesso!",
                total_afetados=1,
                nome_objeto=obj_limpo,
            )
        except Exception as exc:
            logger.exception("Erro ao salvar objeto %s: %s", obj_limpo, exc)
            return ResultadoNomesAmigaveisDTO(sucesso=False, mensagem=f"Erro ao salvar objeto:\n{exc}")

    def gerar_sugestoes_automaticas(self, apenas_nao_editados: bool = True) -> ResultadoNomesAmigaveisDTO:
        """
        Percorre todos os objetos e gera nomes amigáveis para registros
        que ainda não tenham sido personalizados.
        """
        try:
            todos = self._repo.listar_objetos()
            total_atualizados = 0

            for obj in todos:
                nome_tec = obj.nome_objeto.strip()
                nome_ami = obj.nome_amigavel.strip()

                deve_sugerir = False
                if not nome_ami:
                    deve_sugerir = True
                elif apenas_nao_editados and (nome_ami.upper() == nome_tec.upper()):
                    deve_sugerir = True

                if deve_sugerir:
                    nova_sugestao = self.sugerir_nome_amigavel(nome_tec)
                    if nova_sugestao and nova_sugestao != nome_ami:
                        self._repo.atualizar_nome_amigavel(nome_tec, nova_sugestao, obj.categoria)
                        total_atualizados += 1

            return ResultadoNomesAmigaveisDTO(
                sucesso=True,
                mensagem=f"Sugestões automáticas geradas para {total_atualizados} objeto(s) com sucesso!",
                total_afetados=total_atualizados,
            )
        except Exception as exc:
            logger.exception("Erro ao gerar sugestões automáticas: %s", exc)
            return ResultadoNomesAmigaveisDTO(
                sucesso=False,
                mensagem=f"Erro ao gerar sugestões automáticas:\n{exc}",
                total_afetados=0,
            )

    def listar_categorias(self) -> List[str]:
        return self._repo.listar_categorias()
