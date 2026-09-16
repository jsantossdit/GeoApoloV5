"""
Camada de Serviços e Regras de Negócio para Clonagem de Permissões de Usuários.
GeoApolo V5
"""

import logging
from typing import List, Dict, Any, Optional
from permissoes.models import (
    OpcoesClonagemDTO,
    RelatorioClonagemDTO,
    ResultadoClonagemDTO,
    ContaFinanceiraDTO,
    ResultadoContasFinDTO,
    UsuarioDesligamentoDTO,
    ResultadoDesligamentoDTO,
)
from permissoes.repository import PermissoesRepository

logger = logging.getLogger(__name__)


class PermissoesService:
    """Regras de validação e coordenação de replicação de permissões e segurança."""

    def __init__(self, repository: PermissoesRepository):
        self._repo = repository

    def listar_usuarios(self) -> List[Dict[str, str]]:
        return self._repo.listar_usuarios_ativos()

    def validar_clonagem(self, origem: str, destino: str) -> ResultadoClonagemDTO:
        orig = str(origem or "").strip()
        dest = str(destino or "").strip()

        if not orig:
            return ResultadoClonagemDTO(False, "Selecione o usuário de origem que servirá de modelo.")

        if not dest:
            return ResultadoClonagemDTO(False, "Selecione o usuário de destino que receberá as permissões.")

        if orig.upper() == dest.upper():
            return ResultadoClonagemDTO(False, "O usuário de origem e o de destino não podem ser os mesmos.")

        if not self._repo.usuario_tem_direitos(orig):
            return ResultadoClonagemDTO(
                False,
                f'O usuário de origem "{orig}" não possui direitos cadastrados no sistema.',
            )

        return ResultadoClonagemDTO(True, "Validação de clonagem aprovada.")

    def clonar_permissoes(
        self,
        origem: str,
        destino: str,
        opcoes: Optional[OpcoesClonagemDTO] = None,
    ) -> ResultadoClonagemDTO:
        """
        Executa a replicação modular de acessos entre usuários de forma transacional.
        """
        val = self.validar_clonagem(origem, destino)
        if not val.sucesso:
            return val

        if opcoes is None:
            opcoes = OpcoesClonagemDTO()

        orig = str(origem).strip()
        dest = str(destino).strip()
        rel = RelatorioClonagemDTO()

        try:
            if opcoes.direitos_sistema:
                rel.total_direitos_sistema = self._repo.clonar_direitos_sistema(orig, dest)

            if opcoes.relatorios:
                rel.total_relatorios = self._repo.clonar_relatorios(orig, dest)

            if opcoes.contas_financeiras:
                rel.total_contas_financeiras = self._repo.clonar_contas_financeiras(orig, dest)

            if opcoes.formularios:
                rel.total_formularios = self._repo.clonar_formularios(orig, dest)

            if opcoes.categorias_entidades:
                rel.total_categorias_entidades = self._repo.clonar_categorias_entidades(orig, dest)

            if opcoes.tipo_pagar_receber:
                rel.total_tipo_pagar_receber = self._repo.clonar_tipo_pagar_receber(orig, dest)

            if opcoes.grupos_usuario:
                rel.total_grupos_usuario = self._repo.clonar_grupos_usuario(orig, dest)

            if opcoes.favoritos:
                rel.total_favoritos = self._repo.clonar_favoritos(orig, dest)

            if opcoes.tour_usuario:
                rel.total_tour_usuario = self._repo.clonar_tour_usuario(orig, dest)

            if opcoes.empresas_filiais:
                rel.total_empresas_filiais = self._repo.clonar_empresas_filiais(orig, dest)

            rel.total_geral = (
                rel.total_direitos_sistema
                + rel.total_relatorios
                + rel.total_contas_financeiras
                + rel.total_formularios
                + rel.total_categorias_entidades
                + rel.total_tipo_pagar_receber
                + rel.total_grupos_usuario
                + rel.total_favoritos
                + rel.total_tour_usuario
                + rel.total_empresas_filiais
            )

            self._repo.commit()

            return ResultadoClonagemDTO(
                sucesso=True,
                mensagem=f"Clonagem de permissões concluída com sucesso! Total de {rel.total_geral} itens replicados.",
                total_itens=rel.total_geral,
                relatorio=rel,
            )
        except Exception as exc:
            self._repo.rollback()
            logger.exception("Erro durante clonagem de permissões: %s", exc)
            return ResultadoClonagemDTO(
                sucesso=False,
                mensagem=f"Falha na replicação de acessos:\n{exc}",
                total_itens=0,
                relatorio=rel,
            )

    # =========================================================================
    # Regras de Negócio: Permissões em Contas Financeiras
    # =========================================================================

    def obter_contas_disponiveis(self) -> List[ContaFinanceiraDTO]:
        return self._repo.listar_contas_disponiveis()

    def obter_contas_usuario(self, usucod: str) -> List[ContaFinanceiraDTO]:
        u = str(usucod or "").strip()
        if not u:
            return []
        return self._repo.listar_contas_usuario(u)

    def salvar_contas_usuario(self, usucod: str, contas_codigos: List[str]) -> ResultadoContasFinDTO:
        u = str(usucod or "").strip()
        if not u:
            return ResultadoContasFinDTO(False, "Selecione um usuário para salvar as permissões.")

        try:
            total = self._repo.salvar_contas_usuario(u, contas_codigos)
            msg = f"Permissões atualizadas com sucesso! ({total} contas associadas ao usuário {u})."
            return ResultadoContasFinDTO(True, msg, total)
        except Exception as e:
            logger.exception("Erro ao salvar permissões de contas financeiras: %s", e)
            return ResultadoContasFinDTO(False, f"Erro ao atualizar permissões:\n{e}", 0)

    def revogar_contas_usuario(self, usucod: str) -> ResultadoContasFinDTO:
        u = str(usucod or "").strip()
        if not u:
            return ResultadoContasFinDTO(False, "Selecione um usuário para revogar as permissões.")

        try:
            total = self._repo.revogar_contas_usuario(u)
            return ResultadoContasFinDTO(True, f"Permissões revogadas com sucesso ({total} removidas).", total)
        except Exception as e:
            logger.exception("Erro ao revogar permissões de contas financeiras: %s", e)
            return ResultadoContasFinDTO(False, f"Erro ao revogar permissões:\n{e}", 0)

    # =========================================================================
    # Regras de Negócio: Desligamento de Usuários
    # =========================================================================

    def listar_usuarios_desligamento(self, status: str = "Ativo") -> List[UsuarioDesligamentoDTO]:
        return self._repo.listar_usuarios_por_status(status)

    def pesquisar_usuarios_desligamento(
        self, campo: str, valor: str, status: Optional[str] = None
    ) -> List[UsuarioDesligamentoDTO]:
        return self._repo.pesquisar_usuarios(campo, valor, status)

    def obter_detalhes_usuario(self, usucod: str) -> Optional[UsuarioDesligamentoDTO]:
        u = str(usucod or "").strip()
        if not u:
            return None
        return self._repo.obter_usuario(u)

    def desligar_usuario(self, usucod: str) -> ResultadoDesligamentoDTO:
        u = str(usucod or "").strip()
        if not u:
            return ResultadoDesligamentoDTO(False, "Selecione um usuário para desligamento.")
        return self._repo.executar_desligamento(u)

    def reativar_usuario(self, usucod: str) -> bool:
        u = str(usucod or "").strip()
        if not u:
            return False
        return self._repo.reativar_usuario(u)

