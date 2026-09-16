"""
Repositório de Dados para Gestão e Clonagem de Permissões de Usuários.
Preserva as otimizações SQL Server e hints WITH (NOLOCK).
"""

import logging
from typing import List, Dict, Any, Optional
from entidades.database import obter_conexao_banco
from .models import (
    ContaFinanceiraDTO,
    UsuarioDesligamentoDTO,
    ResultadoDesligamentoDTO,
)

logger = logging.getLogger(__name__)


class PermissoesRepository:
    """Acesso ao banco para operações de segurança, controle de acesso e replicação de perfis."""

    def __init__(self, connection=None):
        self._conn = connection

    def _get_cursor(self):
        if self._conn is None:
            self._conn = obter_conexao_banco()
        return self._conn.cursor()

    def commit(self):
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()

    def rollback(self):
        if self._conn and hasattr(self._conn, "rollback"):
            self._conn.rollback()

    def listar_usuarios_ativos(self) -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        sql = """
            SELECT usucod, ISNULL(usunome, usucod) AS usunome
            FROM usuario WITH (NOLOCK)
            WHERE UsuStat = 'Ativo'
            ORDER BY usucod ASC
        """
        cursor.execute(sql)
        return [{"codigo": str(r[0]), "nome": str(r[1])} for r in cursor.fetchall()]

    def usuario_tem_direitos(self, usucod: str) -> bool:
        cursor = self._get_cursor()
        sql = "SELECT TOP 1 1 FROM dir_usuario WITH (NOLOCK) WHERE usucod = ?"
        cursor.execute(sql, [usucod])
        return cursor.fetchone() is not None

    def clonar_direitos_sistema(self, origem: str, destino: str) -> int:
        cursor = self._get_cursor()
        sql = """
            INSERT INTO dir_usuario (tabsistcod, usucod, dirusuacesso, dirusuinclui, dirusuexclui, dirusualtera, dirusuconsulta, dirusuvisualfront)
            SELECT d.tabsistcod, ?, d.dirusuacesso, d.dirusuinclui, d.dirusuexclui, d.dirusualtera, d.dirusuconsulta, d.dirusuvisualfront
            FROM dir_usuario d WITH (NOLOCK)
            WHERE d.usucod = ?
              AND NOT EXISTS (
                  SELECT 1 FROM dir_usuario dest WITH (NOLOCK)
                  WHERE dest.usucod = ? AND dest.tabsistcod = d.tabsistcod
              )
        """
        cursor.execute(sql, [destino, origem, destino])
        return cursor.rowcount if cursor.rowcount > 0 else 0

    def clonar_relatorios(self, origem: str, destino: str) -> int:
        cursor = self._get_cursor()
        sql = """
            INSERT INTO dir_rel_usuario (relcod, usucod)
            SELECT d.relcod, ?
            FROM dir_rel_usuario d WITH (NOLOCK)
            WHERE d.usucod = ?
              AND NOT EXISTS (
                  SELECT 1 FROM dir_rel_usuario dest WITH (NOLOCK)
                  WHERE dest.usucod = ? AND dest.relcod = d.relcod
              )
        """
        cursor.execute(sql, [destino, origem, destino])
        return cursor.rowcount if cursor.rowcount > 0 else 0

    def clonar_contas_financeiras(self, origem: str, destino: str) -> int:
        cursor = self._get_cursor()
        sql = """
            INSERT INTO relac_ctasfin_usuario (ctasfincod, usucod)
            SELECT r.ctasfincod, ?
            FROM relac_ctasfin_usuario r WITH (NOLOCK)
            WHERE r.usucod = ?
              AND NOT EXISTS (
                  SELECT 1 FROM relac_ctasfin_usuario dest WITH (NOLOCK)
                  WHERE dest.usucod = ? AND dest.ctasfincod = r.ctasfincod
              )
        """
        cursor.execute(sql, [destino, origem, destino])
        return cursor.rowcount if cursor.rowcount > 0 else 0

    def clonar_formularios(self, origem: str, destino: str) -> int:
        cursor = self._get_cursor()
        sql = """
            INSERT INTO ctrl_forms (empcod, tabsistcod, usucod, ctrlformsnome)
            SELECT f.empcod, f.tabsistcod, ?, f.ctrlformsnome
            FROM ctrl_forms f WITH (NOLOCK)
            WHERE f.usucod = ?
              AND NOT EXISTS (
                  SELECT 1 FROM ctrl_forms dest WITH (NOLOCK)
                  WHERE dest.usucod = ? AND dest.empcod = f.empcod AND dest.tabsistcod = f.tabsistcod
              )
        """
        cursor.execute(sql, [destino, origem, destino])
        return cursor.rowcount if cursor.rowcount > 0 else 0

    def clonar_categorias_entidades(self, origem: str, destino: str) -> int:
        cursor = self._get_cursor()
        total = 0

        # 1. Categorias
        sql_cat = """
            INSERT INTO usuario_categ (usucod, categcodestr, usucategtodasent)
            SELECT ?, uc.categcodestr, uc.usucategtodasent
            FROM usuario_categ uc WITH (NOLOCK)
            WHERE uc.usucod = ?
              AND NOT EXISTS (
                  SELECT 1 FROM usuario_categ dest WITH (NOLOCK)
                  WHERE dest.usucod = ? AND dest.categcodestr = uc.categcodestr
              )
        """
        cursor.execute(sql_cat, [destino, origem, destino])
        if cursor.rowcount > 0:
            total += cursor.rowcount

        # 2. Entidades associadas às categorias
        sql_ent = """
            INSERT INTO usuario_ent (usucod, entcod, usuentrelacavulso)
            SELECT ?, ec.entcod, 'N'
            FROM usuario_categ uc WITH (NOLOCK)
            INNER JOIN entidade_categ ec WITH (NOLOCK)
                    ON ec.categcodestr = uc.categcodestr
            WHERE uc.usucod = ?
              AND NOT EXISTS (
                  SELECT 1 FROM usuario_ent ue WITH (NOLOCK)
                  WHERE ue.usucod = ? AND ue.entcod = ec.entcod
              )
        """
        cursor.execute(sql_ent, [destino, origem, destino])
        if cursor.rowcount > 0:
            total += cursor.rowcount

        return total

    def clonar_tipo_pagar_receber(self, origem: str, destino: str) -> int:
        cursor = self._get_cursor()
        sql = """
            INSERT INTO tipo_pag_rec_usuario (tipopagreccod, usucod)
            SELECT t.tipopagreccod, ?
            FROM tipo_pag_rec_usuario t WITH (NOLOCK)
            WHERE t.usucod = ?
              AND NOT EXISTS (
                  SELECT 1 FROM tipo_pag_rec_usuario dest WITH (NOLOCK)
                  WHERE dest.usucod = ? AND dest.tipopagreccod = t.tipopagreccod
              )
        """
        cursor.execute(sql, [destino, origem, destino])
        return cursor.rowcount if cursor.rowcount > 0 else 0

    def clonar_grupos_usuario(self, origem: str, destino: str) -> int:
        cursor = self._get_cursor()
        sql = """
            INSERT INTO grp_x_usuario (grpusucod, usucod, grpususuperv)
            SELECT g.grpusucod, ?, g.grpususuperv
            FROM grp_x_usuario g WITH (NOLOCK)
            WHERE g.usucod = ?
              AND NOT EXISTS (
                  SELECT 1 FROM grp_x_usuario dest WITH (NOLOCK)
                  WHERE dest.usucod = ? AND dest.grpusucod = g.grpusucod
              )
        """
        cursor.execute(sql, [destino, origem, destino])
        return cursor.rowcount if cursor.rowcount > 0 else 0

    def clonar_favoritos(self, origem: str, destino: str) -> int:
        cursor = self._get_cursor()
        sql = """
            INSERT INTO ctrl_favoritos_usu (empcod, tabsistcod, usucod, ctrlfavususistema)
            SELECT f.empcod, f.tabsistcod, ?, f.ctrlfavususistema
            FROM ctrl_favoritos_usu f WITH (NOLOCK)
            WHERE f.usucod = ?
              AND NOT EXISTS (
                  SELECT 1 FROM ctrl_favoritos_usu dest WITH (NOLOCK)
                  WHERE dest.usucod = ? AND dest.empcod = f.empcod AND dest.tabsistcod = f.tabsistcod
              )
        """
        cursor.execute(sql, [destino, origem, destino])
        return cursor.rowcount if cursor.rowcount > 0 else 0

    def clonar_tour_usuario(self, origem: str, destino: str) -> int:
        cursor = self._get_cursor()
        sql = """
            INSERT INTO tour_usuario (idtour, usucod)
            SELECT t.idtour, ?
            FROM tour_usuario t WITH (NOLOCK)
            WHERE t.usucod = ?
              AND NOT EXISTS (
                  SELECT 1 FROM tour_usuario dest WITH (NOLOCK)
                  WHERE dest.usucod = ? AND dest.idtour = t.idtour
              )
        """
        cursor.execute(sql, [destino, origem, destino])
        return cursor.rowcount if cursor.rowcount > 0 else 0

    def clonar_empresas_filiais(self, origem: str, destino: str) -> int:
        cursor = self._get_cursor()
        sql = """
            INSERT INTO emp_fil_usuario (empcod, usucod, empfilusupermacessist, empfilusupermverdet)
            SELECT ef.empcod, ?, ef.empfilusupermacessist, ef.empfilusupermverdet
            FROM emp_fil_usuario ef WITH (NOLOCK)
            WHERE ef.usucod = ?
              AND NOT EXISTS (
                  SELECT 1 FROM emp_fil_usuario dest WITH (NOLOCK)
                  WHERE dest.usucod = ? AND dest.empcod = ef.empcod
              )
        """
        cursor.execute(sql, [destino, origem, destino])
        return cursor.rowcount if cursor.rowcount > 0 else 0

    # =========================================================================
    # Permissões em Contas Financeiras
    # =========================================================================

    def listar_contas_disponiveis(self) -> List[ContaFinanceiraDTO]:
        cursor = self._get_cursor()
        sql = """
            SELECT contafincod, contafinnome, ISNULL(contafinccornum, '')
            FROM conta_fin WITH (NOLOCK)
            ORDER BY contafincod ASC
        """
        cursor.execute(sql)
        return [
            ContaFinanceiraDTO(
                codigo=str(r[0]).strip(),
                nome=str(r[1]).strip(),
                conta_corrente=str(r[2]).strip(),
            )
            for r in cursor.fetchall()
        ]

    def listar_contas_usuario(self, usucod: str) -> List[ContaFinanceiraDTO]:
        cursor = self._get_cursor()
        sql = """
            SELECT ucf.contafincod, cf.contafinnome, ISNULL(cf.contafinccornum, '')
            FROM usuario_conta_fin ucf WITH (NOLOCK)
            INNER JOIN conta_fin cf WITH (NOLOCK) ON cf.contafincod = ucf.contafincod
            WHERE ucf.usucod = ?
            ORDER BY ucf.contafincod ASC
        """
        cursor.execute(sql, [usucod])
        return [
            ContaFinanceiraDTO(
                codigo=str(r[0]).strip(),
                nome=str(r[1]).strip(),
                conta_corrente=str(r[2]).strip(),
            )
            for r in cursor.fetchall()
        ]

    def salvar_contas_usuario(self, usucod: str, contas_codigos: List[str]) -> int:
        cursor = self._get_cursor()
        # Revoga permissões existentes para substituir pelo conjunto atualizado
        sql_del = "DELETE FROM usuario_conta_fin WHERE usucod = ?"
        cursor.execute(sql_del, [usucod])

        inseridos = 0
        if contas_codigos:
            sql_ins = "INSERT INTO usuario_conta_fin (contafincod, usucod) VALUES (?, ?)"
            for cod in contas_codigos:
                if cod and cod.strip():
                    cursor.execute(sql_ins, [cod.strip(), usucod.strip()])
                    inseridos += 1
        self.commit()
        return inseridos

    def revogar_contas_usuario(self, usucod: str) -> int:
        cursor = self._get_cursor()
        sql = "DELETE FROM usuario_conta_fin WHERE usucod = ?"
        cursor.execute(sql, [usucod])
        afetados = cursor.rowcount if cursor.rowcount > 0 else 0
        self.commit()
        return afetados

    # =========================================================================
    # Desligamento e Desativação de Usuários
    # =========================================================================

    def listar_usuarios_por_status(self, status: str = "Ativo") -> List[UsuarioDesligamentoDTO]:
        cursor = self._get_cursor()
        sql = """
            SELECT usucod, ISNULL(usunome, usucod), ISNULL(usudepto, ''), ISNULL(usustat, 'Ativo')
            FROM usuario WITH (NOLOCK)
            WHERE usustat = ?
            ORDER BY usucod ASC
        """
        cursor.execute(sql, [status])
        return [
            UsuarioDesligamentoDTO(
                codigo=str(r[0]).strip(),
                nome=str(r[1]).strip(),
                departamento=str(r[2]).strip(),
                status=str(r[3]).strip(),
            )
            for r in cursor.fetchall()
        ]

    def pesquisar_usuarios(
        self, campo: str, valor: str, status: Optional[str] = None
    ) -> List[UsuarioDesligamentoDTO]:
        campo_map = {
            "usucod": "usucod",
            "usunome": "usunome",
            "usudepto": "usudepto",
        }
        coluna = campo_map.get(campo.lower(), "usucod")
        cursor = self._get_cursor()

        sql = f"""
            SELECT usucod, ISNULL(usunome, usucod), ISNULL(usudepto, ''), ISNULL(usustat, 'Ativo')
            FROM usuario WITH (NOLOCK)
            WHERE {coluna} LIKE ?
        """
        params = [f"%{valor.strip()}%"]
        if status:
            sql += " AND usustat = ?"
            params.append(status)

        sql += f" ORDER BY {coluna} ASC"
        cursor.execute(sql, params)
        return [
            UsuarioDesligamentoDTO(
                codigo=str(r[0]).strip(),
                nome=str(r[1]).strip(),
                departamento=str(r[2]).strip(),
                status=str(r[3]).strip(),
            )
            for r in cursor.fetchall()
        ]

    def obter_usuario(self, usucod: str) -> Optional[UsuarioDesligamentoDTO]:
        cursor = self._get_cursor()
        sql = """
            SELECT usucod, ISNULL(usunome, usucod), ISNULL(usudepto, ''), ISNULL(usustat, 'Ativo')
            FROM usuario WITH (NOLOCK)
            WHERE usucod = ?
        """
        cursor.execute(sql, [usucod])
        r = cursor.fetchone()
        if r:
            return UsuarioDesligamentoDTO(
                codigo=str(r[0]).strip(),
                nome=str(r[1]).strip(),
                departamento=str(r[2]).strip(),
                status=str(r[3]).strip(),
            )
        return None

    def executar_desligamento(self, usucod: str) -> ResultadoDesligamentoDTO:
        cursor = self._get_cursor()
        res = ResultadoDesligamentoDTO(sucesso=True, mensagem="")
        try:
            # 1. Remove vinculos com Entidades
            cursor.execute("DELETE FROM usuario_ent WHERE usucod = ?", [usucod])
            res.vinculos_entidades = cursor.rowcount if cursor.rowcount > 0 else 0

            # 2. Remove vinculos com Categorias
            cursor.execute("DELETE FROM usuario_categ WHERE usucod = ?", [usucod])
            res.vinculos_categorias = cursor.rowcount if cursor.rowcount > 0 else 0

            # 3. Remove relatórios autorizados
            cursor.execute("DELETE FROM dir_rel_usuario WHERE usucod = ?", [usucod])
            res.permissoes_relatorios = cursor.rowcount if cursor.rowcount > 0 else 0

            # 4. Remove contas financeiras autorizadas
            cursor.execute("DELETE FROM usuario_conta_fin WHERE usucod = ?", [usucod])
            res.permissoes_contas_fin = cursor.rowcount if cursor.rowcount > 0 else 0

            # 5. Atualiza status para 'Desligado'
            cursor.execute("UPDATE usuario SET usustat = 'Desligado' WHERE usucod = ?", [usucod])

            self.commit()
            res.mensagem = f"Usuário {usucod} desligado com sucesso. Todos os vínculos foram revogados."
            return res
        except Exception as e:
            self.rollback()
            logger.error(f"Erro ao desligar usuário {usucod}: {e}")
            res.sucesso = False
            res.mensagem = f"Erro ao executar desligamento: {e}"
            return res

    def reativar_usuario(self, usucod: str) -> bool:
        cursor = self._get_cursor()
        try:
            cursor.execute("UPDATE usuario SET usustat = 'Ativo' WHERE usucod = ?", [usucod])
            self.commit()
            return True
        except Exception as e:
            self.rollback()
            logger.error(f"Erro ao reativar usuário {usucod}: {e}")
            return False

