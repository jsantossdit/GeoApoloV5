"""
Repositório de Acesso a Dados para Relacionamento de Entidades e Dioceses da CNBB.
GeoApolo V5
"""

import logging
from typing import List, Optional
from entidades.database import obter_conexao_banco
from .models import EntidadeDioceseDTO, DioceseCNBBDTO, FiltroVinculoDioceseDTO

logger = logging.getLogger(__name__)


class DiocesesRepository:
    """Acesso ao banco de dados SQL Server / Apolo para gestão de Dioceses CNBB e vínculos."""

    def __init__(self, connection=None):
        self._conn = connection

    def _get_cursor(self):
        if self._conn is None:
            self._conn = obter_conexao_banco()
        return self._conn.cursor()

    def _is_sqlite(self) -> bool:
        if self._conn is None:
            return False
        return "sqlite" in type(self._conn).__module__.lower()

    def _adapt_sql(self, sql: str) -> str:
        """Adapta a instrução SQL caso o banco seja SQLite (para testes unitários)."""
        if self._is_sqlite():
            # Remove hints WITH (NOLOCK)
            sql = sql.replace("WITH (NOLOCK)", "")
            sql = sql.replace("with (nolock)", "")
            sql = sql.replace("WITH(NOLOCK)", "")
            sql = sql.replace("with(nolock)", "")
            # Ajusta funções específicas se houver
            sql = sql.replace("ISNULL", "COALESCE")
            sql = sql.replace("isnull", "coalesce")
            sql = sql.replace("SUBSTRING", "substr")
        return sql

    def commit(self):
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()

    def rollback(self):
        if self._conn and hasattr(self._conn, "rollback"):
            self._conn.rollback()

    def listar_entidades(self, filtro: FiltroVinculoDioceseDTO) -> List[EntidadeDioceseDTO]:
        """
        Retorna a lista de entidades pertencentes às categorias RCC
        cadastradas no período especificado.
        """
        cursor = self._get_cursor()

        # Categorias de membros/líderes RCC no sistema legado
        sql = """
            SELECT e.entcod, e.entnome, e.cidcod,
                   COALESCE(cid.cidnomecomp, ''),
                   COALESCE(cid.ufsigla, ''),
                   COALESCE(e1.USERDiocese_id, ''),
                   COALESCE(e1.USERNomeDiocese, ''),
                   COALESCE(e1.USERJanaSVE, '')
            FROM entidade e WITH (NOLOCK)
            INNER JOIN ent_categ ec WITH (NOLOCK) ON e.entcod = ec.entcod
            INNER JOIN cidade cid WITH (NOLOCK) ON e.cidcod = cid.cidcod
            LEFT JOIN u_entidade e1 WITH (NOLOCK) ON e.entcod = e1.entcod
            WHERE SUBSTRING(ec.categcodestr, 1, 6) IN ('02.001', '02.002', '03.001', '03.002', '03.003', '03.004', '03.005')
        """
        params = []

        if filtro.data_inicial and filtro.data_final:
            sql += " AND e.entdesdedata BETWEEN ? AND ?"
            dt_ini_str = filtro.data_inicial.isoformat() if hasattr(filtro.data_inicial, 'isoformat') else str(filtro.data_inicial)
            dt_fim_str = filtro.data_final.isoformat() if hasattr(filtro.data_final, 'isoformat') else str(filtro.data_final)
            params.extend([dt_ini_str, dt_fim_str])

        if filtro.apenas_sem_diocese:
            sql += " AND (e1.USERDiocese_id IS NULL OR RTRIM(e1.USERDiocese_id) = '')"

        if filtro.termo_busca and filtro.termo_busca.strip():
            termo = f"%{filtro.termo_busca.strip()}%"
            sql += " AND (e.entcod LIKE ? OR e.entnome LIKE ?)"
            params.extend([termo, termo])

        sql += " ORDER BY e.entcod ASC"

        cursor.execute(self._adapt_sql(sql), params)
        resultados: List[EntidadeDioceseDTO] = []
        for r in cursor.fetchall():
            resultados.append(
                EntidadeDioceseDTO(
                    entcod=str(r[0]).strip(),
                    entnome=str(r[1]).strip(),
                    cidcod=str(r[2]).strip() if r[2] else "",
                    cidnomecomp=str(r[3]).strip() if r[3] else "",
                    ufsigla=str(r[4]).strip() if r[4] else "",
                    user_diocese_id=str(r[5]).strip() if r[5] and str(r[5]).strip() else None,
                    user_nome_diocese=str(r[6]).strip() if r[6] and str(r[6]).strip() else None,
                    user_jana_sve=str(r[7]).strip().upper() if r[7] and str(r[7]).strip() else None,
                )
            )
        return resultados

    def obter_entidade(self, entcod: str) -> Optional[EntidadeDioceseDTO]:
        """Obtém detalhes cadastrais e associação de diocese de uma entidade específica."""
        if not entcod or not entcod.strip():
            return None

        cursor = self._get_cursor()
        sql = """
            SELECT e.entcod, e.entnome, e.cidcod,
                   COALESCE(cid.cidnomecomp, ''),
                   COALESCE(cid.ufsigla, ''),
                   COALESCE(e1.USERDiocese_id, ''),
                   COALESCE(e1.USERNomeDiocese, ''),
                   COALESCE(e1.USERJanaSVE, '')
            FROM entidade e WITH (NOLOCK)
            INNER JOIN cidade cid WITH (NOLOCK) ON e.cidcod = cid.cidcod
            LEFT JOIN u_entidade e1 WITH (NOLOCK) ON e.entcod = e1.entcod
            WHERE e.entcod = ?
        """
        cursor.execute(self._adapt_sql(sql), [entcod.strip()])
        r = cursor.fetchone()
        if not r:
            return None

        return EntidadeDioceseDTO(
            entcod=str(r[0]).strip(),
            entnome=str(r[1]).strip(),
            cidcod=str(r[2]).strip() if r[2] else "",
            cidnomecomp=str(r[3]).strip() if r[3] else "",
            ufsigla=str(r[4]).strip() if r[4] else "",
            user_diocese_id=str(r[5]).strip() if r[5] and str(r[5]).strip() else None,
            user_nome_diocese=str(r[6]).strip() if r[6] and str(r[6]).strip() else None,
            user_jana_sve=str(r[7]).strip().upper() if r[7] and str(r[7]).strip() else None,
        )

    def listar_dioceses(
        self,
        uf: Optional[str] = None,
        cidade: Optional[str] = None,
        termo: Optional[str] = None
    ) -> List[DioceseCNBBDTO]:
        """Consulta as dioceses cadastradas na base da CNBB."""
        cursor = self._get_cursor()
        sql = """
            SELECT DISTINCT dio.id, dio.estado_id, dio.nome,
                            COALESCE(uccnbb.descricao, ''),
                            COALESCE(estado.usersigla, ''),
                            COALESCE(estado.usernome_estado, '')
            FROM USERdioceses_CNBB dio WITH (NOLOCK)
            INNER JOIN USEREstado_CNBB estado WITH (NOLOCK) ON dio.estado_id = estado.USERid
            LEFT JOIN USERcidades_CNBB uccnbb WITH (NOLOCK) ON dio.id = uccnbb.diocese_id
            WHERE 1=1
        """
        params = []

        if uf and uf.strip():
            sql += " AND estado.usersigla = ?"
            params.append(uf.strip().upper())

        if cidade and cidade.strip():
            sql += " AND uccnbb.descricao LIKE ?"
            params.append(f"%{cidade.strip()}%")

        if termo and termo.strip():
            sql += " AND (dio.nome LIKE ? OR uccnbb.descricao LIKE ?)"
            termo_like = f"%{termo.strip()}%"
            params.extend([termo_like, termo_like])

        sql += " ORDER BY dio.nome ASC"

        cursor.execute(self._adapt_sql(sql), params)
        resultados: List[DioceseCNBBDTO] = []
        vistos = set()
        for r in cursor.fetchall():
            did = str(r[0]).strip()
            # Agrupar por ID da diocese para listagens limpas
            if did in vistos:
                continue
            vistos.add(did)

            resultados.append(
                DioceseCNBBDTO(
                    id=did,
                    estado_id=str(r[1]).strip() if r[1] else "",
                    nome=str(r[2]).strip() if r[2] else "",
                    cidade=str(r[3]).strip() if r[3] else "",
                    ufsigla=str(r[4]).strip() if r[4] else "",
                    nome_estado=str(r[5]).strip() if r[5] else "",
                )
            )
        return resultados

    def obter_diocese_por_id(self, diocese_id: str) -> Optional[DioceseCNBBDTO]:
        """Busca diocese pelo ID da CNBB."""
        if not diocese_id or not str(diocese_id).strip():
            return None

        cursor = self._get_cursor()
        sql = """
            SELECT dio.id, dio.estado_id, dio.nome,
                   COALESCE(uccnbb.descricao, ''),
                   COALESCE(estado.usersigla, ''),
                   COALESCE(estado.usernome_estado, '')
            FROM USERdioceses_CNBB dio WITH (NOLOCK)
            INNER JOIN USEREstado_CNBB estado WITH (NOLOCK) ON dio.estado_id = estado.USERid
            LEFT JOIN USERcidades_CNBB uccnbb WITH (NOLOCK) ON dio.id = uccnbb.diocese_id
            WHERE dio.id = ?
        """
        cursor.execute(self._adapt_sql(sql), [str(diocese_id).strip()])
        r = cursor.fetchone()
        if not r:
            return None

        return DioceseCNBBDTO(
            id=str(r[0]).strip(),
            estado_id=str(r[1]).strip() if r[1] else "",
            nome=str(r[2]).strip() if r[2] else "",
            cidade=str(r[3]).strip() if r[3] else "",
            ufsigla=str(r[4]).strip() if r[4] else "",
            nome_estado=str(r[5]).strip() if r[5] else "",
        )

    def sugerir_diocese_por_cidade(self, cidade: str, uf: str) -> Optional[DioceseCNBBDTO]:
        """Sugere a Diocese CNBB correspondente a partir do município e estado da entidade."""
        if not cidade or not cidade.strip():
            return None

        cursor = self._get_cursor()
        sql = """
            SELECT dio.id, dio.estado_id, dio.nome,
                   uccnbb.descricao, estado.usersigla, estado.usernome_estado
            FROM USERcidades_CNBB uccnbb WITH (NOLOCK)
            INNER JOIN USERdioceses_CNBB dio WITH (NOLOCK) ON uccnbb.diocese_id = dio.id
            INNER JOIN USEREstado_CNBB estado WITH (NOLOCK) ON dio.estado_id = estado.USERid
            WHERE UPPER(uccnbb.descricao) = UPPER(?)
        """
        params = [cidade.strip()]
        if uf and uf.strip():
            sql += " AND UPPER(estado.usersigla) = UPPER(?)"
            params.append(uf.strip())

        cursor.execute(self._adapt_sql(sql), params)
        r = cursor.fetchone()
        if not r:
            # Tentar correspondência parcial (LIKE)
            sql_parcial = """
                SELECT dio.id, dio.estado_id, dio.nome,
                       uccnbb.descricao, estado.usersigla, estado.usernome_estado
                FROM USERcidades_CNBB uccnbb WITH (NOLOCK)
                INNER JOIN USERdioceses_CNBB dio WITH (NOLOCK) ON uccnbb.diocese_id = dio.id
                INNER JOIN USEREstado_CNBB estado WITH (NOLOCK) ON dio.estado_id = estado.USERid
                WHERE uccnbb.descricao LIKE ?
            """
            params_parcial = [f"%{cidade.strip()}%"]
            if uf and uf.strip():
                sql_parcial += " AND UPPER(estado.usersigla) = UPPER(?)"
                params_parcial.append(uf.strip())

            cursor.execute(self._adapt_sql(sql_parcial), params_parcial)
            r = cursor.fetchone()

        if not r:
            return None

        return DioceseCNBBDTO(
            id=str(r[0]).strip(),
            estado_id=str(r[1]).strip() if r[1] else "",
            nome=str(r[2]).strip() if r[2] else "",
            cidade=str(r[3]).strip() if r[3] else "",
            ufsigla=str(r[4]).strip() if r[4] else "",
            nome_estado=str(r[5]).strip() if r[5] else "",
        )

    def vincular_diocese(self, entcod: str, diocese_id: Optional[str], nome_diocese: Optional[str]) -> bool:
        """Salva ou atualiza a diocese vinculada na tabela de extensão u_entidade."""
        if not entcod or not entcod.strip():
            return False

        entcod = entcod.strip()
        diocese_id = str(diocese_id).strip() if diocese_id else None
        nome_diocese = str(nome_diocese).strip() if nome_diocese else None

        cursor = self._get_cursor()
        try:
            # Verifica se já existe registro em u_entidade
            check_sql = "SELECT entcod FROM u_entidade WHERE entcod = ?"
            cursor.execute(self._adapt_sql(check_sql), [entcod])
            existe = cursor.fetchone() is not None

            if existe:
                update_sql = """
                    UPDATE u_entidade
                    SET USERDiocese_id = ?, USERNomeDiocese = ?
                    WHERE entcod = ?
                """
                cursor.execute(self._adapt_sql(update_sql), [diocese_id, nome_diocese, entcod])
            else:
                insert_sql = """
                    INSERT INTO u_entidade (entcod, USERDiocese_id, USERNomeDiocese)
                    VALUES (?, ?, ?)
                """
                cursor.execute(self._adapt_sql(insert_sql), [entcod, diocese_id, nome_diocese])

            self.commit()
            return True
        except Exception as e:
            logger.error(f"Erro ao vincular diocese para entidade {entcod}: {e}")
            self.rollback()
            raise

    def desvincular_diocese(self, entcod: str) -> bool:
        """Remove o vínculo da diocese com a entidade (define campos como NULL)."""
        return self.vincular_diocese(entcod, diocese_id=None, nome_diocese=None)
