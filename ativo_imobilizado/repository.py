"""
Repositório de Dados para Gestão de Ativo Imobilizado.
Preserva as otimizações SQL Server e hints WITH (NOLOCK).
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from entidades.database import obter_conexao_banco

logger = logging.getLogger(__name__)


class AtivoImobilizadoRepository:
    """Acesso ao banco de dados para operações com Ativo Fixo Imobilizado."""

    def __init__(self, connection=None):
        self._conn = connection

    @property
    def _is_sql_server(self) -> bool:
        if self._conn is None:
            return True
        return "sqlite" not in getattr(type(self._conn), "__module__", "").lower()

    def _nolock(self) -> str:
        return "WITH (NOLOCK)" if self._is_sql_server else ""

    def _get_cursor(self):
        if self._conn is None:
            self._conn = obter_conexao_banco()
        return self._conn.cursor()

    @property
    def _tabela_marcas(self) -> str:
        """Determina dinamicamente a tabela que armazena o catálogo de marcas com a coluna descricao_marca."""
        if not hasattr(self, "_cached_tabela_marcas"):
            cursor = self._get_cursor()
            tab = "USER_geoapolo_marcas"
            for t in ("USER_geoapolo_marcas", "USER_geoapolo_produto_marcas"):
                try:
                    cursor.execute(f"SELECT descricao_marca FROM {t} WHERE 1 = 0")
                    tab = t
                    break
                except Exception:
                    pass
            self._cached_tabela_marcas = tab
        return self._cached_tabela_marcas

    def listar_bens(self, empcod: str) -> List[Dict[str, Any]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        tab_marcas = self._tabela_marcas
        date_aquisicao = "CONVERT(VARCHAR(10), ugsa.data_aquisicao, 103)" if self._is_sql_server else "ugsa.data_aquisicao"
        date_revisao = "CONVERT(VARCHAR(10), ugsa.data_ultima_revisao, 103)" if self._is_sql_server else "ugsa.data_ultima_revisao"
        sql = f"""
            SELECT
                ugsa.numero_do_bem,
                ugsa.descricao_do_bem,
                ugsa.geocctrlcodestr,
                COALESCE(ugcc.geocctrlnome, '') AS geocctrlnome,
                COALESCE(ugsa.codigo_barrasativo, '') AS codigo_barrasativo,
                ugsa.codigo_categoria_bem,
                COALESCE(ugsc.descricao, '') AS categoria_bem,
                ugsa.codigo_classificacaoativoimobilizado,
                COALESCE(ugsca.descricao, '') AS classificacao,
                ugsa.codigo_localizacao,
                COALESCE(ugslf.localizacao, '') AS localizacao,
                COALESCE(ugsa.codigo_func_responsavel, '') AS codigo_func_responsavel,
                COALESCE(ugu.nome_completo, '') AS nome_func_responsavel,
                COALESCE(ugsa.codigo_da_marca, '') AS codigo_da_marca,
                COALESCE(ugpm.descricao_marca, '') AS marca,
                COALESCE(ugsa.codigo_status_bem, '1') AS codigo_status_bem,
                COALESCE(ugssi.descricao_status_bem, CASE WHEN ugsa.codigo_status_bem = '2' THEN 'BAIXADO' ELSE 'ATIVO' END) AS descricao_status_bem,
                ugsa.empcod,
                {date_aquisicao} AS data_aquisicao,
                COALESCE(ugsa.quantidade, 1.0) AS quantidade,
                COALESCE(ugsa.valor_compra, 0.0) AS valor_compra,
                COALESCE(ugsa.valor_total, ugsa.valor_compra, 0.0) AS valor_total,
                COALESCE(ugsa.taxa_depreciacao_anual, 0.0) AS taxa_depreciacao_anual,
                {date_revisao} AS data_ultima_revisao,
                COALESCE(ugsa.caminho_foto, '') AS caminho_foto,
                COALESCE(ugsa.observacoes, '') AS observacoes
            FROM USER_geoapolo_satfi_ativoimobilizado ugsa {nolock}
            LEFT JOIN USER_geoapolo_centrocontrole ugcc {nolock}
                    ON ugsa.geocctrlcodestr = ugcc.geocctrlcodestr
            LEFT JOIN USER_geoapolo_satfi_categorias ugsc {nolock}
                    ON ugsa.codigo_categoria_bem = ugsc.codigo_categoria
            LEFT JOIN USER_geoapolo_satfi_classificacaoativo ugsca {nolock}
                    ON ugsa.codigo_classificacaoativoimobilizado = ugsca.codigoclasse
            LEFT JOIN USER_geoapolo_satfi_localizacao_fisica ugslf {nolock}
                    ON ugsa.codigo_localizacao = ugslf.codigo_localizacao
            LEFT JOIN USER_geoapolo_usuarios ugu {nolock}
                   ON ugsa.codigo_func_responsavel = ugu.usucod
            LEFT JOIN {tab_marcas} ugpm {nolock}
                   ON ugsa.codigo_da_marca = ugpm.codigo_marca
            LEFT JOIN USER_geoapolo_satfi_status_imobilizado ugssi {nolock}
                   ON ugsa.codigo_status_bem = ugssi.codigo_status_bem
            WHERE (? IS NULL OR ? = '' OR ugsa.empcod = ?)
            ORDER BY CAST(ugsa.numero_do_bem AS INTEGER) ASC
        """
        cursor.execute(sql, [empcod, empcod, empcod])
        cols = [c[0].lower() for c in cursor.description]
        registros = []
        for row in cursor.fetchall():
            registros.append(dict(zip(cols, row)))
        return registros

    def obter_bem(self, numero_do_bem: str, empcod: str) -> Optional[Dict[str, Any]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        tab_marcas = self._tabela_marcas
        date_aquisicao = "CONVERT(VARCHAR(10), ugsa.data_aquisicao, 103)" if self._is_sql_server else "ugsa.data_aquisicao"
        date_revisao = "CONVERT(VARCHAR(10), ugsa.data_ultima_revisao, 103)" if self._is_sql_server else "ugsa.data_ultima_revisao"
        sql = f"""
            SELECT
                ugsa.numero_do_bem,
                ugsa.descricao_do_bem,
                ugsa.geocctrlcodestr,
                COALESCE(ugcc.geocctrlnome, '') AS geocctrlnome,
                COALESCE(ugsa.codigo_barrasativo, '') AS codigo_barrasativo,
                ugsa.codigo_categoria_bem,
                COALESCE(ugsc.descricao, '') AS categoria_bem,
                ugsa.codigo_classificacaoativoimobilizado,
                COALESCE(ugsca.descricao, '') AS classificacao,
                ugsa.codigo_localizacao,
                COALESCE(ugslf.localizacao, '') AS localizacao,
                COALESCE(ugsa.codigo_func_responsavel, '') AS codigo_func_responsavel,
                COALESCE(ugu.nome_completo, '') AS nome_func_responsavel,
                COALESCE(ugsa.codigo_da_marca, '') AS codigo_da_marca,
                COALESCE(ugpm.descricao_marca, '') AS marca,
                COALESCE(ugsa.codigo_status_bem, '1') AS codigo_status_bem,
                COALESCE(ugssi.descricao_status_bem, CASE WHEN ugsa.codigo_status_bem = '2' THEN 'BAIXADO' ELSE 'ATIVO' END) AS descricao_status_bem,
                ugsa.empcod,
                {date_aquisicao} AS data_aquisicao,
                COALESCE(ugsa.quantidade, 1.0) AS quantidade,
                COALESCE(ugsa.valor_compra, 0.0) AS valor_compra,
                COALESCE(ugsa.valor_total, ugsa.valor_compra, 0.0) AS valor_total,
                COALESCE(ugsa.taxa_depreciacao_anual, 0.0) AS taxa_depreciacao_anual,
                {date_revisao} AS data_ultima_revisao,
                COALESCE(ugsa.caminho_foto, '') AS caminho_foto,
                COALESCE(ugsa.observacoes, '') AS observacoes
            FROM USER_geoapolo_satfi_ativoimobilizado ugsa {nolock}
            LEFT JOIN USER_geoapolo_centrocontrole ugcc {nolock}
                    ON ugsa.geocctrlcodestr = ugcc.geocctrlcodestr
            LEFT JOIN USER_geoapolo_satfi_categorias ugsc {nolock}
                    ON ugsa.codigo_categoria_bem = ugsc.codigo_categoria
            LEFT JOIN USER_geoapolo_satfi_classificacaoativo ugsca {nolock}
                    ON ugsa.codigo_classificacaoativoimobilizado = ugsca.codigoclasse
            LEFT JOIN USER_geoapolo_satfi_localizacao_fisica ugslf {nolock}
                    ON ugsa.codigo_localizacao = ugslf.codigo_localizacao
            LEFT JOIN USER_geoapolo_usuarios ugu {nolock}
                   ON ugsa.codigo_func_responsavel = ugu.usucod
            LEFT JOIN {tab_marcas} ugpm {nolock}
                   ON ugsa.codigo_da_marca = ugpm.codigo_marca
            LEFT JOIN USER_geoapolo_satfi_status_imobilizado ugssi {nolock}
                   ON ugsa.codigo_status_bem = ugssi.codigo_status_bem
            WHERE ugsa.numero_do_bem = ? AND (? IS NULL OR ? = '' OR ugsa.empcod = ?)
        """
        cursor.execute(sql, [numero_do_bem, empcod, empcod, empcod])
        row = cursor.fetchone()
        if not row:
            return None
        cols = [c[0].lower() for c in cursor.description]
        return dict(zip(cols, row))

    def inserir_bem(self, dados: Dict[str, Any]) -> bool:
        cursor = self._get_cursor()
        sql = """
            INSERT INTO USER_geoapolo_satfi_ativoimobilizado (
                numero_do_bem, descricao_do_bem, geocctrlcodestr,
                codigo_barrasativo, codigo_categoria_bem,
                codigo_classificacaoativoimobilizado, codigo_localizacao,
                codigo_func_responsavel, codigo_da_marca, empcod, codigo_status_bem,
                data_aquisicao, quantidade, valor_compra, valor_total, taxa_depreciacao_anual,
                data_ultima_revisao, caminho_foto, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        data_aquisicao = dados.get("data_aquisicao") or None
        data_revisao = dados.get("data_ultima_revisao") or None
        func_resp = dados.get("codigo_func_responsavel") or None
        marca = dados.get("codigo_da_marca") or None
        status_bem = dados.get("codigo_status_bem") or None
        qtd = float(dados.get("quantidade") or 1.0)
        v_compra = float(dados.get("valor_compra") or 0.0)
        v_total = float(dados.get("valor_total") or (qtd * v_compra))

        cursor.execute(sql, [
            str(dados.get("numero_do_bem")),
            dados.get("descricao_do_bem"),
            dados.get("geocctrlcodestr"),
            dados.get("codigo_barrasativo", ""),
            dados.get("codigo_categoria_bem"),
            dados.get("codigo_classificacaoativoimobilizado"),
            dados.get("codigo_localizacao"),
            func_resp,
            marca,
            dados.get("empcod", "001"),
            status_bem,
            data_aquisicao,
            qtd,
            v_compra,
            v_total,
            float(dados.get("taxa_depreciacao_anual") or 0.0),
            data_revisao,
            dados.get("caminho_foto", ""),
            dados.get("observacoes", ""),
        ])
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def atualizar_bem(self, dados: Dict[str, Any]) -> bool:
        cursor = self._get_cursor()
        sql = """
            UPDATE USER_geoapolo_satfi_ativoimobilizado SET
                descricao_do_bem                     = ?,
                geocctrlcodestr                      = ?,
                codigo_barrasativo                   = ?,
                codigo_categoria_bem                 = ?,
                codigo_classificacaoativoimobilizado = ?,
                codigo_localizacao                   = ?,
                codigo_func_responsavel              = ?,
                codigo_da_marca                      = ?,
                empcod                               = ?,
                codigo_status_bem                    = ?,
                data_aquisicao                       = ?,
                quantidade                           = ?,
                valor_compra                         = ?,
                valor_total                          = ?,
                taxa_depreciacao_anual               = ?,
                data_ultima_revisao                  = ?,
                caminho_foto                         = ?,
                observacoes                          = ?
            WHERE numero_do_bem = ?
        """
        data_aquisicao = dados.get("data_aquisicao") or None
        data_revisao = dados.get("data_ultima_revisao") or None
        func_resp = dados.get("codigo_func_responsavel") or None
        marca = dados.get("codigo_da_marca") or None
        status_bem = dados.get("codigo_status_bem") or None
        qtd = float(dados.get("quantidade") or 1.0)
        v_compra = float(dados.get("valor_compra") or 0.0)
        v_total = float(dados.get("valor_total") or (qtd * v_compra))

        cursor.execute(sql, [
            dados.get("descricao_do_bem"),
            dados.get("geocctrlcodestr"),
            dados.get("codigo_barrasativo", ""),
            dados.get("codigo_categoria_bem"),
            dados.get("codigo_classificacaoativoimobilizado"),
            dados.get("codigo_localizacao"),
            func_resp,
            marca,
            dados.get("empcod", "001"),
            status_bem,
            data_aquisicao,
            qtd,
            v_compra,
            v_total,
            float(dados.get("taxa_depreciacao_anual") or 0.0),
            data_revisao,
            dados.get("caminho_foto", ""),
            dados.get("observacoes", ""),
            str(dados.get("numero_do_bem")),
        ])
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def excluir_bem(self, numero_do_bem: str) -> bool:
        cursor = self._get_cursor()
        sql = "DELETE FROM USER_geoapolo_satfi_ativoimobilizado WHERE numero_do_bem = ?"
        cursor.execute(sql, [str(numero_do_bem)])
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def obter_proximo_numero_bem(self, empcod: str) -> str:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT COALESCE(MAX(CAST(numero_do_bem AS INTEGER)), 0) + 1
            FROM USER_geoapolo_satfi_ativoimobilizado {nolock}
            WHERE ISNUMERIC(numero_do_bem) = 1
        """
        cursor.execute(sql)
        row = cursor.fetchone()
        return str(row[0]) if row else "1"

    # ── Lookups ──────────────────────────────────────────────────────────

    def listar_centros_controle(self) -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT geocctrlcodestr, geocctrlnome
            FROM USER_geoapolo_centrocontrole {nolock}
            ORDER BY geocctrlcodestr ASC
        """
        cursor.execute(sql)
        return [{"codigo": str(r[0]), "descricao": str(r[1])} for r in cursor.fetchall()]

    def listar_categorias(self) -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT codigo_categoria, descricao
            FROM USER_geoapolo_satfi_categorias {nolock}
            ORDER BY codigo_categoria ASC
        """
        cursor.execute(sql)
        return [{"codigo": str(r[0]), "descricao": str(r[1])} for r in cursor.fetchall()]

    def listar_classificacoes(self, categoria_cod: str = "") -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        if categoria_cod:
            sql = f"""
                SELECT ugsca.codigoclasse, ugsca.descricao, COALESCE(ugsc.descricao, '') AS categoria
                FROM USER_geoapolo_satfi_classificacaoativo ugsca {nolock}
                LEFT JOIN USER_geoapolo_satfi_categorias ugsc {nolock}
                       ON ugsca.codigo_categoria = ugsc.codigo_categoria
                WHERE CAST(ugsca.codigo_categoria AS VARCHAR) = ?
                ORDER BY ugsca.codigoclasse ASC
            """
            cursor.execute(sql, [str(categoria_cod)])
        else:
            sql = f"""
                SELECT ugsca.codigoclasse, ugsca.descricao, COALESCE(ugsc.descricao, '') AS categoria
                FROM USER_geoapolo_satfi_classificacaoativo ugsca {nolock}
                LEFT JOIN USER_geoapolo_satfi_categorias ugsc {nolock}
                       ON ugsca.codigo_categoria = ugsc.codigo_categoria
                ORDER BY ugsca.codigoclasse ASC
            """
            cursor.execute(sql)
        return [{"codigo": str(r[0]), "descricao": str(r[1]), "extra": str(r[2])} for r in cursor.fetchall()]

    def listar_localizacoes(self) -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT ugslf.codigo_localizacao, ugslf.localizacao, COALESCE(ugd.nome_departamento, '') AS departamento
            FROM USER_geoapolo_satfi_localizacao_fisica ugslf {nolock}
            INNER JOIN USER_geoapolo_departamentos ugd {nolock}
                    ON ugslf.codigo_departamento = ugd.codigo_departamento
                   AND ugd.flagativo = 'A'
            WHERE ugslf.grupo <> 'G'
            ORDER BY ugslf.codigo_localizacao ASC
        """
        cursor.execute(sql)
        return [{"codigo": str(r[0]), "descricao": str(r[1]), "extra": str(r[2])} for r in cursor.fetchall()]

    def listar_funcionarios(self) -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT ugu.usucod, ugu.nome_completo, COALESCE(ugd.nome_departamento, '') AS departamento
            FROM USER_geoapolo_usuarios ugu {nolock}
            INNER JOIN USER_geoapolo_departamentos ugd {nolock}
                    ON ugu.codigo_departamento = ugd.codigo_departamento
                   AND ugd.flagativo = 'A'
            WHERE ugu.flagativo = 'A'
            ORDER BY ugu.nome_completo ASC
        """
        cursor.execute(sql)
        return [{"codigo": str(r[0]), "descricao": str(r[1]), "extra": str(r[2])} for r in cursor.fetchall()]

    def listar_marcas(self) -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        tab = self._tabela_marcas
        sql = f"""
            SELECT codigo_marca, descricao_marca
            FROM {tab} {nolock}
            ORDER BY descricao_marca ASC
        """
        cursor.execute(sql)
        return [
            {"codigo": str(r[0]), "descricao": str(r[1] or "").strip()}
            for r in cursor.fetchall()
            if r[1] and str(r[1]).strip()
        ]

    def obter_ou_criar_marca(self, descricao: str) -> Tuple[int, str, bool]:
        """Obtém ou cria uma nova marca no catálogo utilizando o serviço unificado de marcas."""
        from marcas.repository import MarcasRepository
        from marcas.service import MarcasService

        repo_marcas = MarcasRepository(self._conn)
        service_marcas = MarcasService(repo_marcas)
        return service_marcas.obter_ou_criar_marca(descricao)

    def listar_status(self) -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        try:
            sql = f"""
                SELECT codigo_status_bem, descricao_status_bem
                FROM USER_geoapolo_satfi_status_imobilizado {nolock}
                ORDER BY codigo_status_bem ASC
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            if rows:
                return [{"codigo": str(r[0]).strip(), "descricao": str(r[1] or "").strip().upper()} for r in rows]
        except Exception as exc:
            logger.warning("Falha ao consultar tabela de status do imobilizado: %s", exc)

        return [
            {"codigo": "1", "descricao": "ATIVO"},
            {"codigo": "2", "descricao": "BAIXADO"},
        ]

    def listar_empresas(self) -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT empcod, empnome
            FROM USER_geoapolo_empresas {nolock}
            ORDER BY empcod ASC
        """
        cursor.execute(sql)
        return [{"codigo": str(r[0]), "descricao": str(r[1])} for r in cursor.fetchall()]

    def obter_proximo_codigo_categoria(self) -> int:
        cursor = self._get_cursor()
        cursor.execute("SELECT COALESCE(MAX(codigo_categoria), 0) + 1 FROM USER_geoapolo_satfi_categorias")
        row = cursor.fetchone()
        return int(row[0]) if row and row[0] else 1

    def salvar_categoria(self, codigo: int, descricao: str) -> bool:
        cursor = self._get_cursor()
        cursor.execute("SELECT 1 FROM USER_geoapolo_satfi_categorias WHERE codigo_categoria = ?", [codigo])
        existe = cursor.fetchone() is not None
        if existe:
            cursor.execute(
                "UPDATE USER_geoapolo_satfi_categorias SET descricao = ? WHERE codigo_categoria = ?",
                [descricao, codigo],
            )
        else:
            cursor.execute(
                "INSERT INTO USER_geoapolo_satfi_categorias (codigo_categoria, descricao) VALUES (?, ?)",
                [codigo, descricao],
            )
        if hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def excluir_categoria(self, codigo: int) -> bool:
        cursor = self._get_cursor()
        cursor.execute("DELETE FROM USER_geoapolo_satfi_categorias WHERE codigo_categoria = ?", [codigo])
        if hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def obter_proximo_codigo_classificacao(self) -> int:
        cursor = self._get_cursor()
        nolock = self._nolock()
        cursor.execute(f"SELECT COALESCE(MAX(CAST(codigoclasse AS INTEGER)), 0) + 1 FROM USER_geoapolo_satfi_classificacaoativo {nolock}")
        row = cursor.fetchone()
        return int(row[0]) if row and row[0] else 1

    def salvar_classificacao(self, codigo: int, descricao: str, codigo_categoria: Optional[int] = None) -> bool:
        cursor = self._get_cursor()
        cursor.execute("SELECT 1 FROM USER_geoapolo_satfi_classificacaoativo WHERE codigoclasse = ?", [codigo])
        existe = cursor.fetchone() is not None
        cod_cat = int(codigo_categoria) if codigo_categoria not in (None, "", 0, "0") else None
        if existe:
            cursor.execute(
                """
                UPDATE USER_geoapolo_satfi_classificacaoativo
                SET descricao = ?, codigo_categoria = ?
                WHERE codigoclasse = ?
                """,
                [str(descricao).strip().upper(), cod_cat, codigo],
            )
        else:
            cursor.execute(
                """
                INSERT INTO USER_geoapolo_satfi_classificacaoativo (codigoclasse, descricao, codigo_categoria)
                VALUES (?, ?, ?)
                """,
                [codigo, str(descricao).strip().upper(), cod_cat],
            )
        if hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def excluir_classificacao(self, codigo: int) -> bool:
        cursor = self._get_cursor()
        cursor.execute("DELETE FROM USER_geoapolo_satfi_classificacaoativo WHERE codigoclasse = ?", [codigo])
        if hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def obter_classificacao(self, codigo: int) -> Optional[Dict[str, Any]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT
                ugsca.codigoclasse,
                ugsca.descricao,
                ugsca.codigo_categoria,
                COALESCE(ugsc.descricao, '') AS categoria
            FROM USER_geoapolo_satfi_classificacaoativo ugsca {nolock}
            LEFT JOIN USER_geoapolo_satfi_categorias ugsc {nolock}
                   ON ugsca.codigo_categoria = ugsc.codigo_categoria
            WHERE ugsca.codigoclasse = ?
        """
        cursor.execute(sql, [codigo])
        row = cursor.fetchone()
        if not row:
            return None
        cols = [c[0].lower() for c in cursor.description]
        return dict(zip(cols, row))

    def listar_todas_classificacoes(self, busca: str = "") -> List[Dict[str, Any]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        filtro = f"%{busca.strip()}%" if busca.strip() else ""
        if filtro:
            sql = f"""
                SELECT
                    ugsca.codigoclasse,
                    ugsca.descricao,
                    ugsca.codigo_categoria,
                    COALESCE(ugsc.descricao, '') AS categoria
                FROM USER_geoapolo_satfi_classificacaoativo ugsca {nolock}
                LEFT JOIN USER_geoapolo_satfi_categorias ugsc {nolock}
                       ON ugsca.codigo_categoria = ugsc.codigo_categoria
                WHERE ugsca.descricao LIKE ? OR CAST(ugsca.codigoclasse AS VARCHAR) LIKE ?
                ORDER BY ugsca.codigoclasse ASC
            """
            cursor.execute(sql, [filtro, filtro])
        else:
            sql = f"""
                SELECT
                    ugsca.codigoclasse,
                    ugsca.descricao,
                    ugsca.codigo_categoria,
                    COALESCE(ugsc.descricao, '') AS categoria
                FROM USER_geoapolo_satfi_classificacaoativo ugsca {nolock}
                LEFT JOIN USER_geoapolo_satfi_categorias ugsc {nolock}
                       ON ugsca.codigo_categoria = ugsc.codigo_categoria
                ORDER BY ugsca.codigoclasse ASC
            """
            cursor.execute(sql)
        cols = [c[0].lower() for c in cursor.description]
        return [dict(zip(cols, r)) for r in cursor.fetchall()]


    def listar_todas_localizacoes(self) -> List[Dict[str, Any]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT
                ugslf.codigo_localizacao,
                ugslf.localizacao,
                ugslf.codigo_departamento,
                COALESCE(ugd.nome_departamento, '') AS departamento,
                COALESCE(ugslf.grupo, 'A') AS grupo
            FROM USER_geoapolo_satfi_localizacao_fisica ugslf {nolock}
            LEFT JOIN USER_geoapolo_departamentos ugd {nolock}
                   ON ugslf.codigo_departamento = ugd.codigo_departamento
            ORDER BY ugslf.codigo_localizacao ASC
        """
        cursor.execute(sql)
        cols = [c[0].lower() for c in cursor.description]
        return [dict(zip(cols, r)) for r in cursor.fetchall()]

    def salvar_localizacao(self, codigo: str, localizacao: str, codigo_departamento: Optional[int], grupo: str = "A") -> bool:
        cursor = self._get_cursor()
        cursor.execute("SELECT 1 FROM USER_geoapolo_satfi_localizacao_fisica WHERE codigo_localizacao = ?", [codigo])
        existe = cursor.fetchone() is not None
        if existe:
            cursor.execute(
                """
                UPDATE USER_geoapolo_satfi_localizacao_fisica
                SET localizacao = ?, codigo_departamento = ?, grupo = ?
                WHERE codigo_localizacao = ?
                """,
                [localizacao, codigo_departamento, grupo, codigo],
            )
        else:
            cursor.execute(
                """
                INSERT INTO USER_geoapolo_satfi_localizacao_fisica (codigo_localizacao, localizacao, codigo_departamento, grupo)
                VALUES (?, ?, ?, ?)
                """,
                [codigo, localizacao, codigo_departamento, grupo],
            )
        if hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def excluir_localizacao(self, codigo: str) -> bool:
        cursor = self._get_cursor()
        cursor.execute("DELETE FROM USER_geoapolo_satfi_localizacao_fisica WHERE codigo_localizacao = ?", [codigo])
        if hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def listar_departamentos(self) -> List[Dict[str, Any]]:
        cursor = self._get_cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT codigo_departamento, nome_departamento
            FROM USER_geoapolo_departamentos {nolock}
            ORDER BY nome_departamento ASC
        """
        cursor.execute(sql)
        return [{"codigo": r[0], "nome": r[1]} for r in cursor.fetchall()]
