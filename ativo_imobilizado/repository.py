"""
Repositório de Dados para Gestão de Ativo Imobilizado.
Preserva as otimizações SQL Server e hints WITH (NOLOCK).
"""

import logging
from typing import List, Dict, Any, Optional
from entidades.database import obter_conexao_banco

logger = logging.getLogger(__name__)


class AtivoImobilizadoRepository:
    """Acesso ao banco de dados para operações com Ativo Fixo Imobilizado."""

    def __init__(self, connection=None):
        self._conn = connection

    def _get_cursor(self):
        if self._conn is None:
            self._conn = obter_conexao_banco()
        return self._conn.cursor()

    def listar_bens(self, empcod: str) -> List[Dict[str, Any]]:
        cursor = self._get_cursor()
        sql = """
            SELECT
                ugsa.numero_do_bem,
                ugsa.descricao_do_bem,
                ugsa.geocctrlcodestr,
                ISNULL(ugcc.geocctrlnome, '') AS geocctrlnome,
                ISNULL(ugsa.codigo_barrasativo, '') AS codigo_barrasativo,
                ugsa.codigo_categoria_bem,
                ISNULL(ugsc.descricao, '') AS categoria_bem,
                ugsa.codigo_classificacaoativoimobilizado,
                ISNULL(ugsca.descricao, '') AS classificacao,
                ugsa.codigo_localizacao,
                ISNULL(ugslf.localizacao, '') AS localizacao,
                ISNULL(ugsa.codigo_func_responsavel, '') AS codigo_func_responsavel,
                ISNULL(ugu.nome_completo, '') AS nome_func_responsavel,
                ISNULL(ugsa.codigo_da_marca, '') AS codigo_da_marca,
                ISNULL(ugpm.descricao_marca, '') AS marca,
                ISNULL(ugsa.codigo_status_bem, '') AS codigo_status_bem,
                ISNULL(ugssi.descricao_status_bem, '') AS descricao_status_bem,
                ugsa.empcod,
                CONVERT(VARCHAR(10), ugsa.data_aquisicao, 103) AS data_aquisicao,
                ISNULL(ugsa.valor_compra, 0.0) AS valor_compra,
                ISNULL(ugsa.taxa_depreciacao_anual, 0.0) AS taxa_depreciacao_anual,
                CONVERT(VARCHAR(10), ugsa.data_ultima_revisao, 103) AS data_ultima_revisao,
                ISNULL(ugsa.caminho_foto, '') AS caminho_foto,
                ISNULL(ugsa.observacoes, '') AS observacoes
            FROM USER_geoapolo_satfi_ativoimobilizado ugsa WITH (NOLOCK)
            INNER JOIN USER_geoapolo_centrocontrole ugcc WITH (NOLOCK)
                    ON ugsa.geocctrlcodestr = ugcc.geocctrlcodestr
            INNER JOIN USER_geoapolo_satfi_categorias ugsc WITH (NOLOCK)
                    ON ugsa.codigo_categoria_bem = ugsc.codigo_categoria
            INNER JOIN USER_geoapolo_satfi_classificacaoativo ugsca WITH (NOLOCK)
                    ON ugsa.codigo_classificacaoativoimobilizado = ugsca.codigoclasse
            INNER JOIN USER_geoapolo_satfi_localizacao_fisica ugslf WITH (NOLOCK)
                    ON ugsa.codigo_localizacao = ugslf.codigo_localizacao
            LEFT JOIN USER_geoapolo_usuarios ugu WITH (NOLOCK)
                   ON ugsa.codigo_func_responsavel = ugu.usucod
            LEFT JOIN USER_geoapolo_produto_marcas ugpm WITH (NOLOCK)
                   ON ugsa.codigo_da_marca = ugpm.codigo_marca
            LEFT JOIN USER_geoapolo_satfi_status_imobilizado ugssi WITH (NOLOCK)
                   ON ugsa.codigo_status_bem = ugssi.codigo_status_bem
            WHERE ugsa.empcod = ?
            ORDER BY CAST(ugsa.numero_do_bem AS INTEGER) ASC
        """
        cursor.execute(sql, [empcod])
        cols = [c[0].lower() for c in cursor.description]
        registros = []
        for row in cursor.fetchall():
            registros.append(dict(zip(cols, row)))
        return registros

    def obter_bem(self, numero_do_bem: str, empcod: str) -> Optional[Dict[str, Any]]:
        cursor = self._get_cursor()
        sql = """
            SELECT
                ugsa.numero_do_bem,
                ugsa.descricao_do_bem,
                ugsa.geocctrlcodestr,
                ISNULL(ugcc.geocctrlnome, '') AS geocctrlnome,
                ISNULL(ugsa.codigo_barrasativo, '') AS codigo_barrasativo,
                ugsa.codigo_categoria_bem,
                ISNULL(ugsc.descricao, '') AS categoria_bem,
                ugsa.codigo_classificacaoativoimobilizado,
                ISNULL(ugsca.descricao, '') AS classificacao,
                ugsa.codigo_localizacao,
                ISNULL(ugslf.localizacao, '') AS localizacao,
                ISNULL(ugsa.codigo_func_responsavel, '') AS codigo_func_responsavel,
                ISNULL(ugu.nome_completo, '') AS nome_func_responsavel,
                ISNULL(ugsa.codigo_da_marca, '') AS codigo_da_marca,
                ISNULL(ugpm.descricao_marca, '') AS marca,
                ISNULL(ugsa.codigo_status_bem, '') AS codigo_status_bem,
                ISNULL(ugssi.descricao_status_bem, '') AS descricao_status_bem,
                ugsa.empcod,
                CONVERT(VARCHAR(10), ugsa.data_aquisicao, 103) AS data_aquisicao,
                ISNULL(ugsa.valor_compra, 0.0) AS valor_compra,
                ISNULL(ugsa.taxa_depreciacao_anual, 0.0) AS taxa_depreciacao_anual,
                CONVERT(VARCHAR(10), ugsa.data_ultima_revisao, 103) AS data_ultima_revisao,
                ISNULL(ugsa.caminho_foto, '') AS caminho_foto,
                ISNULL(ugsa.observacoes, '') AS observacoes
            FROM USER_geoapolo_satfi_ativoimobilizado ugsa WITH (NOLOCK)
            INNER JOIN USER_geoapolo_centrocontrole ugcc WITH (NOLOCK)
                    ON ugsa.geocctrlcodestr = ugcc.geocctrlcodestr
            INNER JOIN USER_geoapolo_satfi_categorias ugsc WITH (NOLOCK)
                    ON ugsa.codigo_categoria_bem = ugsc.codigo_categoria
            INNER JOIN USER_geoapolo_satfi_classificacaoativo ugsca WITH (NOLOCK)
                    ON ugsa.codigo_classificacaoativoimobilizado = ugsca.codigoclasse
            INNER JOIN USER_geoapolo_satfi_localizacao_fisica ugslf WITH (NOLOCK)
                    ON ugsa.codigo_localizacao = ugslf.codigo_localizacao
            LEFT JOIN USER_geoapolo_usuarios ugu WITH (NOLOCK)
                   ON ugsa.codigo_func_responsavel = ugu.usucod
            LEFT JOIN USER_geoapolo_produto_marcas ugpm WITH (NOLOCK)
                   ON ugsa.codigo_da_marca = ugpm.codigo_marca
            LEFT JOIN USER_geoapolo_satfi_status_imobilizado ugssi WITH (NOLOCK)
                   ON ugsa.codigo_status_bem = ugssi.codigo_status_bem
            WHERE ugsa.numero_do_bem = ? AND ugsa.empcod = ?
        """
        cursor.execute(sql, [numero_do_bem, empcod])
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
                data_aquisicao, valor_compra, taxa_depreciacao_anual,
                data_ultima_revisao, caminho_foto, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        data_aquisicao = dados.get("data_aquisicao") or None
        data_revisao = dados.get("data_ultima_revisao") or None
        func_resp = dados.get("codigo_func_responsavel") or None
        marca = dados.get("codigo_da_marca") or None
        status_bem = dados.get("codigo_status_bem") or None

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
            float(dados.get("valor_compra") or 0.0),
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
                valor_compra                         = ?,
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
            float(dados.get("valor_compra") or 0.0),
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
        sql = """
            SELECT ISNULL(MAX(CAST(numero_do_bem AS INTEGER)), 0) + 1
            FROM USER_geoapolo_satfi_ativoimobilizado WITH (NOLOCK)
            WHERE ISNUMERIC(numero_do_bem) = 1
        """
        cursor.execute(sql)
        row = cursor.fetchone()
        return str(row[0]) if row else "1"

    # ── Lookups ──────────────────────────────────────────────────────────

    def listar_centros_controle(self) -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        sql = """
            SELECT geocctrlcodestr, geocctrlnome
            FROM USER_geoapolo_centrocontrole WITH (NOLOCK)
            ORDER BY geocctrlcodestr ASC
        """
        cursor.execute(sql)
        return [{"codigo": str(r[0]), "descricao": str(r[1])} for r in cursor.fetchall()]

    def listar_categorias(self) -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        sql = """
            SELECT codigo_categoria, descricao
            FROM USER_geoapolo_satfi_categorias WITH (NOLOCK)
            ORDER BY codigo_categoria ASC
        """
        cursor.execute(sql)
        return [{"codigo": str(r[0]), "descricao": str(r[1])} for r in cursor.fetchall()]

    def listar_classificacoes(self, categoria_cod: str = "") -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        if categoria_cod:
            sql = """
                SELECT ugsca.codigoclasse, ugsca.descricao, ISNULL(ugsc.descricao, '') AS categoria
                FROM USER_geoapolo_satfi_classificacaoativo ugsca WITH (NOLOCK)
                INNER JOIN USER_geoapolo_satfi_categorias ugsc WITH (NOLOCK)
                        ON ugsca.codigo_categoria = ugsc.codigo_categoria
                WHERE ugsca.codigo_categoria = ?
                ORDER BY ugsca.codigoclasse ASC
            """
            cursor.execute(sql, [categoria_cod])
        else:
            sql = """
                SELECT ugsca.codigoclasse, ugsca.descricao, ISNULL(ugsc.descricao, '') AS categoria
                FROM USER_geoapolo_satfi_classificacaoativo ugsca WITH (NOLOCK)
                INNER JOIN USER_geoapolo_satfi_categorias ugsc WITH (NOLOCK)
                        ON ugsca.codigo_categoria = ugsc.codigo_categoria
                ORDER BY ugsca.codigoclasse ASC
            """
            cursor.execute(sql)
        return [{"codigo": str(r[0]), "descricao": str(r[1]), "extra": str(r[2])} for r in cursor.fetchall()]

    def listar_localizacoes(self) -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        sql = """
            SELECT ugslf.codigo_localizacao, ugslf.localizacao, ISNULL(ugd.nome_departamento, '') AS departamento
            FROM USER_geoapolo_satfi_localizacao_fisica ugslf WITH (NOLOCK)
            INNER JOIN USER_geoapolo_departamentos ugd WITH (NOLOCK)
                    ON ugslf.codigo_departamento = ugd.codigo_departamento
                   AND ugd.flagativo = 'A'
            WHERE ugslf.grupo <> 'G'
            ORDER BY ugslf.codigo_localizacao ASC
        """
        cursor.execute(sql)
        return [{"codigo": str(r[0]), "descricao": str(r[1]), "extra": str(r[2])} for r in cursor.fetchall()]

    def listar_funcionarios(self) -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        sql = """
            SELECT ugu.usucod, ugu.nome_completo, ISNULL(ugd.nome_departamento, '') AS departamento
            FROM USER_geoapolo_usuarios ugu WITH (NOLOCK)
            INNER JOIN USER_geoapolo_departamentos ugd WITH (NOLOCK)
                    ON ugu.codigo_departamento = ugd.codigo_departamento
                   AND ugd.flagativo = 'A'
            WHERE ugu.flagativo = 'A'
            ORDER BY ugu.nome_completo ASC
        """
        cursor.execute(sql)
        return [{"codigo": str(r[0]), "descricao": str(r[1]), "extra": str(r[2])} for r in cursor.fetchall()]

    def listar_marcas(self) -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        sql = """
            SELECT codigo_marca, descricao_marca
            FROM USER_geoapolo_produto_marcas WITH (NOLOCK)
            ORDER BY codigo_marca ASC
        """
        cursor.execute(sql)
        return [{"codigo": str(r[0]), "descricao": str(r[1])} for r in cursor.fetchall()]

    def listar_status(self) -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        sql = """
            SELECT codigo_status_bem, descricao_status_bem
            FROM USER_geoapolo_satfi_status_imobilizado WITH (NOLOCK)
            ORDER BY codigo_status_bem ASC
        """
        cursor.execute(sql)
        return [{"codigo": str(r[0]), "descricao": str(r[1])} for r in cursor.fetchall()]

    def listar_empresas(self) -> List[Dict[str, str]]:
        cursor = self._get_cursor()
        sql = """
            SELECT empcod, empnome
            FROM USER_geoapolo_empresas WITH (NOLOCK)
            ORDER BY empcod ASC
        """
        cursor.execute(sql)
        return [{"codigo": str(r[0]), "descricao": str(r[1])} for r in cursor.fetchall()]
