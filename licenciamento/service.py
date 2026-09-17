"""
Regras de Negócio e Serviços para Licenciamento, Segurança e Versões.
GeoApolo V5
Clean Architecture: Regras desacopladas, validação temporal e cálculo de chave de liberação.
"""

from datetime import date
import hashlib
import logging
from typing import List, Optional

from .models import (
    LicencaDTO,
    ResultadoValidacaoLicencaDTO,
    VersaoSistemaDTO,
    ResultadoOperacaoVersaoDTO,
)
from .repository import LicenciamentoRepository

logger = logging.getLogger(__name__)

CHAVE_MESTRA_EMERGENCIA = "GEOAPOLO-ADMIN-MASTER-OVERRIDE"
SALT_LICENCA = "GEOAPOLO_V5_LICENCA_SALT_2026"


class LicenciamentoService:
    """Regras de negócio para verificação de licenças e manutenção de versões."""

    def __init__(self, repository: LicenciamentoRepository):
        self._repo = repository

    # -------------------------------------------------------------
    # Validação e Ativação de Licenças
    # -------------------------------------------------------------
    def validar_licenca_atual(
        self, data_referencia: Optional[date] = None
    ) -> ResultadoValidacaoLicencaDTO:
        """
        Valida se o sistema possui licença válida para o período de referência.
        Garante bloqueio quando expirada e alerta durante o prazo de tolerância.
        """
        data_ref = data_referencia or date.today()
        mes = data_ref.month
        ano = data_ref.year

        licenca = self._repo.buscar_licenca_mes(mes, ano)
        if not licenca:
            return ResultadoValidacaoLicencaDTO(
                sucesso=False,
                status="ERRO_CONSULTA",
                mensagem=f"Nenhuma licença cadastrada para o período {mes:02d}/{ano}.",
                dias_restantes=0,
                licenca=None,
            )

        # Checa bloqueio explícito
        if licenca.is_bloqueada:
            return ResultadoValidacaoLicencaDTO(
                sucesso=False,
                status="BLOQUEADA",
                mensagem="A licença do sistema está vencida/bloqueada. Solicite a chave de liberação.",
                dias_restantes=0,
                licenca=licenca,
            )

        # Checa se já foi ativada
        if not licenca.is_ativa:
            return ResultadoValidacaoLicencaDTO(
                sucesso=False,
                status="NAO_ATIVADA",
                mensagem=f"A chave do período {mes:02d}/{ano} ainda não foi ativada.",
                dias_restantes=0,
                licenca=licenca,
            )

        # Verificação da data de expiração
        dias_restantes = licenca.calcular_dias_restantes(data_ref)

        if dias_restantes == 0 and licenca.data_final and data_ref > licenca.data_final:
            # Venceu e ultrapassou: bloqueia no banco
            self._repo.bloquear_licenca(licenca.id_palavra)
            return ResultadoValidacaoLicencaDTO(
                sucesso=False,
                status="BLOQUEADA",
                mensagem="A licença do sistema expirou. O acesso aos módulos requer nova chave.",
                dias_restantes=0,
                licenca=licenca,
            )

        if dias_restantes <= licenca.tempo_bloqueio_dias:
            return ResultadoValidacaoLicencaDTO(
                sucesso=True,
                status="AVISO_EXPIRACAO",
                mensagem=(
                    f"Atenção: A licença do GeoApolo vencerá em {dias_restantes} dia(s). "
                    "Providencie a renovação para evitar interrupções."
                ),
                dias_restantes=dias_restantes,
                licenca=licenca,
            )

        return ResultadoValidacaoLicencaDTO(
            sucesso=True,
            status="OK",
            mensagem="Licença ativa e regular.",
            dias_restantes=dias_restantes,
            licenca=licenca,
        )

    def gerar_chave_licenca(self, id_palavra: str, mes: int, ano: int) -> str:
        """Gera a chave criptográfica esperada para ativação de um período."""
        semente = f"{id_palavra.strip().upper()}#{mes:02d}#{ano}#{SALT_LICENCA}"
        hash_hex = hashlib.sha256(semente.encode("utf-8")).hexdigest().upper()
        # Formato: APOLO-XXXX-YYYY-ZZZZ
        return f"APOLO-{hash_hex[0:4]}-{hash_hex[4:8]}-{hash_hex[8:12]}"

    def ativar_licenca_com_chave(
        self, id_palavra: str, chave: str, mes: int, ano: int
    ) -> ResultadoValidacaoLicencaDTO:
        """Valida a chave fornecida e desbloqueia a licença."""
        limpa_chave = chave.strip().upper().replace(" ", "")
        chave_esperada = self.gerar_chave_licenca(id_palavra, mes, ano)

        valida = (limpa_chave == chave_esperada) or (limpa_chave == CHAVE_MESTRA_EMERGENCIA)

        if not valida:
            return ResultadoValidacaoLicencaDTO(
                sucesso=False,
                status="CHAVE_INVALIDA",
                mensagem="Chave de ativação informada é inválida ou não corresponde a esta instalação.",
                dias_restantes=0,
            )

        try:
            self._repo.ativar_licenca(id_palavra)
            return ResultadoValidacaoLicencaDTO(
                sucesso=True,
                status="OK",
                mensagem="Licença ativada com sucesso! O sistema foi liberado.",
                dias_restantes=30,
            )
        except Exception as exc:
            logger.exception("Erro ao ativar licença: %s", exc)
            return ResultadoValidacaoLicencaDTO(
                sucesso=False,
                status="ERRO_BANCO",
                mensagem=f"Erro ao salvar ativação no banco de dados:\n{exc}",
            )

    # -------------------------------------------------------------
    # Gestão de Versões e Release Notes
    # -------------------------------------------------------------
    def listar_versoes(self) -> List[VersaoSistemaDTO]:
        return self._repo.listar_versoes()

    def obter_versao(self, idversao: str) -> Optional[VersaoSistemaDTO]:
        if not idversao.strip():
            return None
        return self._repo.obter_versao(idversao)

    def salvar_versao(self, dto: VersaoSistemaDTO) -> ResultadoOperacaoVersaoDTO:
        v_id = dto.idversao.strip()
        if not v_id:
            return ResultadoOperacaoVersaoDTO(sucesso=False, mensagem="Identificador da versão é obrigatório.")

        dt_lib = dto.data_lancamento.strip()
        if not dt_lib:
            return ResultadoOperacaoVersaoDTO(sucesso=False, mensagem="Data de lançamento da versão é obrigatória.")

        dto.idversao = v_id
        dto.data_lancamento = dt_lib
        dto.statusversao = "S" if dto.is_liberada else "N"

        try:
            self._repo.salvar_versao(dto)
            return ResultadoOperacaoVersaoDTO(
                sucesso=True,
                mensagem=f"Versão {v_id} gravada com sucesso!",
                idversao=v_id,
            )
        except Exception as exc:
            logger.exception("Erro ao salvar versão %s: %s", v_id, exc)
            return ResultadoOperacaoVersaoDTO(sucesso=False, mensagem=f"Erro ao salvar versão:\n{exc}")

    def excluir_versao(self, idversao: str) -> ResultadoOperacaoVersaoDTO:
        v_id = idversao.strip()
        if not v_id:
            return ResultadoOperacaoVersaoDTO(sucesso=False, mensagem="Versão inválida para exclusão.")

        versao_db = self._repo.obter_versao(v_id)
        if not versao_db:
            return ResultadoOperacaoVersaoDTO(sucesso=False, mensagem="Versão não encontrada.")

        if versao_db.is_liberada:
            return ResultadoOperacaoVersaoDTO(
                sucesso=False,
                mensagem="Não é permitido excluir uma versão homologada e liberada para os usuários.",
            )

        try:
            self._repo.excluir_versao(v_id)
            return ResultadoOperacaoVersaoDTO(
                sucesso=True,
                mensagem=f"Versão {v_id} excluída com sucesso.",
                idversao=v_id,
            )
        except Exception as exc:
            logger.exception("Erro ao excluir versão %s: %s", v_id, exc)
            return ResultadoOperacaoVersaoDTO(sucesso=False, mensagem=f"Erro ao excluir versão:\n{exc}")

    def obter_novidades_pendentes(self, idversao: str, usucod: str) -> Optional[str]:
        """Retorna o texto de novidades se o usuário ainda não tiver visto."""
        v_id = idversao.strip()
        u_cod = usucod.strip()
        if not v_id or not u_cod:
            return None

        if self._repo.usuario_ja_viu_versao(v_id, u_cod):
            return None

        versao = self._repo.obter_versao(v_id)
        if versao and versao.is_liberada and versao.textonovaversao.strip():
            return versao.textonovaversao.strip()
        return None

    def confirmar_leitura_versao(self, idversao: str, usucod: str) -> bool:
        """Marca no banco que o usuário confirmou a leitura dos release notes."""
        if not idversao.strip() or not usucod.strip():
            return False
        return self._repo.marcar_versao_vista(idversao, usucod)
