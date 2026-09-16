"""
Camada de Serviços e Regras de Negócio para Relacionamento de Categorias de Entidades.
"""

import logging
from typing import List, Dict, Any
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
