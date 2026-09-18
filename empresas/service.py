"""
Serviço de lógica de negócio e contexto de Multi-Empresas.
GeoApolo V5
"""

import sys
from pathlib import Path

# Garante que o diretório raiz esteja no sys.path
_raiz_projeto = str(Path(__file__).resolve().parent.parent)
if _raiz_projeto not in sys.path:
    sys.path.insert(0, _raiz_projeto)

from typing import List, Optional
try:
    from empresas.models import EmpresaDTO, ResultadoEmpresaDTO
    from empresas.repository import EmpresasRepository
except (ImportError, ModuleNotFoundError):
    from models import EmpresaDTO, ResultadoEmpresaDTO
    from repository import EmpresasRepository


class EmpresasService:
    """Gerencia regras de negócio cadastrais e o contexto corporativo da empresa ativa."""

    _empresa_ativa_contexto: Optional[EmpresaDTO] = None

    def __init__(self, repository: EmpresasRepository):
        if not repository:
            raise ValueError("EmpresasRepository é obrigatório.")
        self._repo = repository

    def listar_empresas(self) -> List[EmpresaDTO]:
        return self._repo.listar_empresas()

    def obter_empresa(self, empcod: str) -> Optional[EmpresaDTO]:
        if not empcod or not empcod.strip():
            raise ValueError("Código da empresa deve ser fornecido.")
        return self._repo.obter_empresa(empcod.strip().upper())

    def salvar_empresa(self, e: EmpresaDTO) -> ResultadoEmpresaDTO:
        if not e.empcod or not e.empcod.strip():
            return ResultadoEmpresaDTO(False, "O código da empresa é obrigatório.")

        if not e.empnome or not e.empnome.strip():
            return ResultadoEmpresaDTO(False, "A razão social/nome da empresa não pode estar vazia.")

        e.empcod = e.empcod.strip().upper()
        e.empnome = e.empnome.strip().upper()

        try:
            self._repo.salvar_empresa(e)
            return ResultadoEmpresaDTO(True, f"Empresa '{e.empcod}' salva com sucesso.", total_afetado=1)
        except Exception as exc:
            return ResultadoEmpresaDTO(False, f"Erro ao salvar empresa: {str(exc)}")

    def excluir_empresa(self, empcod: str) -> ResultadoEmpresaDTO:
        if not empcod or not empcod.strip():
            return ResultadoEmpresaDTO(False, "Código da empresa deve ser informado.")

        cod = empcod.strip().upper()
        if self._empresa_ativa_contexto and self._empresa_ativa_contexto.empcod == cod:
            return ResultadoEmpresaDTO(False, "Não é permitido excluir a empresa atualmente selecionada como ativa.")

        try:
            self._repo.excluir_empresa(cod)
            return ResultadoEmpresaDTO(True, f"Empresa '{cod}' excluída com sucesso.", total_afetado=1)
        except Exception as exc:
            return ResultadoEmpresaDTO(False, f"Erro ao excluir empresa: {str(exc)}")

    def sincronizar_empresas(self) -> ResultadoEmpresaDTO:
        try:
            total = self._repo.sincronizar_empresas_apolo()
            return ResultadoEmpresaDTO(
                True,
                f"Sincronização concluída: {total} filial(is) importada(s) do Apolo.",
                total_afetado=total,
            )
        except Exception as exc:
            return ResultadoEmpresaDTO(False, f"Erro na sincronização de filiais: {str(exc)}")

    def selecionar_empresa_ativa(self, empcod: str) -> ResultadoEmpresaDTO:
        """Define a empresa ativa na sessão corporativa."""
        if not empcod or not empcod.strip():
            return ResultadoEmpresaDTO(False, "Código da empresa inválido.")

        emp = self.obter_empresa(empcod)
        if not emp:
            return ResultadoEmpresaDTO(False, f"Empresa '{empcod}' não localizada para seleção.")

        EmpresasService._empresa_ativa_contexto = emp
        return ResultadoEmpresaDTO(True, f"Empresa ativa alterada para: {emp.display_completo}")

    @classmethod
    def obter_empresa_ativa(cls) -> Optional[EmpresaDTO]:
        return cls._empresa_ativa_contexto
