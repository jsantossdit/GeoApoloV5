"""
Camada de Serviços e Regras de Negócio para Relacionamento de Categorias de Entidades.
"""

import logging
from typing import List, Dict, Any, Optional
from categorias.models import ResultadoOperacao
from categorias.repository import CategoriaEntidadeRepository

logger = logging.getLogger(__name__)


class CategoriaEntidadeService:
    """Orquestração de regras de negócio para permissões e relacionamentos de categorias."""

    def __init__(self, repository: CategoriaEntidadeRepository):
        self._repo = repository

    def obter_usuarios(self) -> List[Dict[str, str]]:
        return self._repo.listar_usuarios_ativos()

    def obter_grupos(self) -> List[Dict[str, str]]:
        return self._repo.listar_grupos()

    def obter_categorias(self, modo: str, id_selecionado: str) -> List[Dict[str, Any]]:
        if not id_selecionado:
            return []
        if modo == "Usuario":
            return self._repo.listar_categorias_usuario(id_selecionado)
        else:
            usuarios = self._repo.listar_usuarios_do_grupo(id_selecionado)
            if usuarios:
                return self._repo.listar_categorias_usuario(usuarios[0])
            return []

    def vincular_categoria(self, modo: str, id_selecionado: str, categoria_codigo: str) -> ResultadoOperacao:
        if not id_selecionado or not categoria_codigo:
            return ResultadoOperacao(sucesso=False, mensagem="Identificador ou categoria não selecionada.")

        try:
            if modo == "Usuario":
                self._repo.vincular_categoria_usuario(id_selecionado, categoria_codigo)
            else:
                usuarios = self._repo.listar_usuarios_do_grupo(id_selecionado)
                for u in usuarios:
                    self._repo.vincular_categoria_usuario(u, categoria_codigo)

            return ResultadoOperacao(
                sucesso=True,
                mensagem="Categoria vinculada com sucesso!",
                codigo=categoria_codigo,
            )
        except Exception as exc:
            logger.exception("Erro ao vincular categoria: %s", exc)
            return ResultadoOperacao(sucesso=False, mensagem=f"Erro ao vincular:\n{exc}")

    def relacionar_entidades(self, modo: str, id_selecionado: str, categoria_codigo: str) -> ResultadoOperacao:
        if not id_selecionado or not categoria_codigo:
            return ResultadoOperacao(sucesso=False, mensagem="Identificador ou categoria não selecionada.")

        try:
            if modo == "Usuario":
                self._repo.relacionar_entidades_categoria_usuario(id_selecionado, categoria_codigo)
            else:
                usuarios = self._repo.listar_usuarios_do_grupo(id_selecionado)
                for u in usuarios:
                    self._repo.relacionar_entidades_categoria_usuario(u, categoria_codigo)

            return ResultadoOperacao(
                sucesso=True,
                mensagem="Todas as entidades desta categoria foram relacionadas com sucesso!",
                codigo=categoria_codigo,
            )
        except Exception as exc:
            logger.exception("Erro ao relacionar entidades: %s", exc)
            return ResultadoOperacao(sucesso=False, mensagem=f"Erro ao relacionar entidades:\n{exc}")

    def remover_relacionamento(self, modo: str, id_selecionado: str, categoria_codigo: str) -> ResultadoOperacao:
        if not id_selecionado or not categoria_codigo:
            return ResultadoOperacao(sucesso=False, mensagem="Identificador ou categoria não selecionada.")

        try:
            if modo == "Usuario":
                self._repo.remover_categoria_usuario(id_selecionado, categoria_codigo)
            else:
                usuarios = self._repo.listar_usuarios_do_grupo(id_selecionado)
                for u in usuarios:
                    self._repo.remover_categoria_usuario(u, categoria_codigo)

            return ResultadoOperacao(
                sucesso=True,
                mensagem="Relacionamento de categoria removido com sucesso!",
                codigo=categoria_codigo,
            )
        except Exception as exc:
            logger.exception("Erro ao remover relacionamento: %s", exc)
            return ResultadoOperacao(sucesso=False, mensagem=f"Erro ao remover:\n{exc}")

    def listar_todas_categorias(self) -> List[Dict[str, Any]]:
        """Retorna todas as categorias cadastradas."""
        return self._repo.listar_todas_categorias()

    def obter_categoria(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Busca detalhes de uma categoria específica."""
        if not codigo:
            return None
        return self._repo.obter_categoria(codigo)

    def obter_proximo_codigo_alternativo(self) -> str:
        """Gera ou obtém o próximo código sequencial de categoria."""
        return self._repo.obter_proximo_codigo_alternativo()

    def salvar_categoria(self, dados: Dict[str, Any], modo_inclusao: bool = True) -> ResultadoOperacao:
        """Valida e persiste a criação ou edição de categoria."""
        cod_estr = str(dados.get("codigo") or dados.get("geocategcodestr") or "").strip().upper()
        nome = str(dados.get("descricao") or dados.get("geocategnome") or "").strip().upper()

        if not cod_estr:
            return ResultadoOperacao(sucesso=False, mensagem="O campo 'Código Categoria' é de preenchimento obrigatório.")
        if not nome:
            return ResultadoOperacao(sucesso=False, mensagem="O campo 'Nome da Categoria' é de preenchimento obrigatório.")

        if modo_inclusao:
            existente = self._repo.obter_categoria(cod_estr)
            if existente:
                return ResultadoOperacao(
                    sucesso=False,
                    mensagem=f"Código de categoria '{cod_estr}' já está em uso!",
                    codigo=cod_estr,
                )

        try:
            self._repo.salvar_categoria(dados, modo_inclusao=modo_inclusao)
            return ResultadoOperacao(
                sucesso=True,
                mensagem=f"Categoria '{nome}' salva com sucesso!",
                codigo=cod_estr,
            )
        except Exception as exc:
            logger.exception("Erro ao salvar categoria: %s", exc)
            return ResultadoOperacao(sucesso=False, mensagem=f"Erro ao salvar categoria:\n{exc}")

    def excluir_categoria(self, codigo: str) -> ResultadoOperacao:
        """Remove a categoria após validações."""
        if not codigo:
            return ResultadoOperacao(sucesso=False, mensagem="Código de categoria não informado.")
        try:
            self._repo.excluir_categoria(codigo)
            return ResultadoOperacao(
                sucesso=True,
                mensagem=f"Categoria '{codigo}' excluída com sucesso!",
                codigo=codigo,
            )
        except Exception as exc:
            logger.exception("Erro ao excluir categoria: %s", exc)
            return ResultadoOperacao(sucesso=False, mensagem=f"Erro ao excluir categoria:\n{exc}")

