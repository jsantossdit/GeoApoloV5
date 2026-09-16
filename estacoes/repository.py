"""
Repositório de Dados para Estações de Trabalho, Hardware, Software e Usuários.
Preserva as otimizações SQL Server e hints WITH (NOLOCK).
"""

import logging
from typing import List, Dict, Any, Optional
from estacoes.models import EstacaoFiltro
from entidades.database import obter_conexao_banco

logger = logging.getLogger(__name__)


class EstacoesRepository:
    """Repositório de persistência para o módulo de inventário e estações de trabalho."""

    def __init__(self, connection=None):
        self._conn = connection

    def _get_cursor(self):
        if self._conn is None:
            self._conn = obter_conexao_banco()
        return self._conn.cursor()

    def listar_estacoes(self, filtro: EstacaoFiltro) -> List[Dict[str, Any]]:
        cursor = self._get_cursor()

        sql = """
            SELECT TOP (?)
                e.codigo_estacao,
                e.descricao,
                e.codigo_departamento,
                ISNULL(d.nome_departamento, '') AS nome_departamento,
                CONVERT(VARCHAR(10), e.data_cadastro, 103) AS data_cadastro,
                ISNULL(e.codigo_usuario, '') AS codigo_usuario,
                ISNULL(e.usuario_responsavel, '') AS usuario_responsavel,
                ISNULL(e.tag_servico, '') AS tag_servico,
                ISNULL(e.geoentcod, '') AS geoentcod,
                ISNULL(ent.geoentnome, '') AS nome_entidade,
                ISNULL(e.modelo_estacao, '') AS modelo_estacao,
                ISNULL(e.codigo_localizacao, '') AS codigo_localizacao,
                ISNULL(loc.localizacao, '') AS nome_localizacao,
                ISNULL(e.enderecoip, '') AS enderecoip,
                ISNULL(e.observacoes, '') AS observacoes
            FROM USER_geoapolo_satfi_estacao e WITH (NOLOCK)
            LEFT JOIN USER_geoapolo_departamentos d WITH (NOLOCK) ON e.codigo_departamento = d.codigo_departamento
            LEFT JOIN USER_geoapolo_entidade ent WITH (NOLOCK) ON e.geoentcod = ent.geoentcod
            LEFT JOIN USER_geoapolo_satfi_localizacao_fisica loc WITH (NOLOCK) ON e.codigo_localizacao = loc.codigo_localizacao
            WHERE 1=1
        """
        params = [filtro.limite]

        if filtro.texto_busca.strip():
            if filtro.campo_busca == "codigo_estacao":
                sql += " AND e.codigo_estacao LIKE ? "
            elif filtro.campo_busca == "tag_servico":
                sql += " AND e.tag_servico LIKE ? "
            else:
                sql += " AND e.descricao LIKE ? "
            params.append(f"%{filtro.texto_busca.strip()}%")

        if filtro.departamento.strip():
            sql += " AND e.codigo_departamento = ? "
            params.append(filtro.departamento.strip())

        ordem_col = "e.codigo_estacao" if filtro.campo_ordem == "codigo_estacao" else "e.descricao"
        direcao = "ASC" if filtro.ordem_asc else "DESC"
        sql += f" ORDER BY {ordem_col} {direcao}"

        cursor.execute(sql, params)
        cols = [c[0] for c in cursor.description]
        registros = []
        for row in cursor.fetchall():
            registros.append(dict(zip(cols, row)))
        return registros

    def obter_estacao(self, codigo: str) -> Optional[Dict[str, Any]]:
        cursor = self._get_cursor()
        sql = """
            SELECT TOP (1)
                e.codigo_estacao,
                e.descricao,
                e.codigo_departamento,
                ISNULL(d.nome_departamento, '') AS nome_departamento,
                CONVERT(VARCHAR(10), e.data_cadastro, 103) AS data_cadastro,
                ISNULL(e.codigo_usuario, '') AS codigo_usuario,
                ISNULL(e.usuario_responsavel, '') AS usuario_responsavel,
                ISNULL(e.tag_servico, '') AS tag_servico,
                ISNULL(e.geoentcod, '') AS geoentcod,
                ISNULL(ent.geoentnome, '') AS nome_entidade,
                ISNULL(e.modelo_estacao, '') AS modelo_estacao,
                ISNULL(e.codigo_localizacao, '') AS codigo_localizacao,
                ISNULL(loc.localizacao, '') AS nome_localizacao,
                ISNULL(e.enderecoip, '') AS enderecoip,
                ISNULL(e.observacoes, '') AS observacoes
            FROM USER_geoapolo_satfi_estacao e WITH (NOLOCK)
            LEFT JOIN USER_geoapolo_departamentos d WITH (NOLOCK) ON e.codigo_departamento = d.codigo_departamento
            LEFT JOIN USER_geoapolo_entidade ent WITH (NOLOCK) ON e.geoentcod = ent.geoentcod
            LEFT JOIN USER_geoapolo_satfi_localizacao_fisica loc WITH (NOLOCK) ON e.codigo_localizacao = loc.codigo_localizacao
            WHERE e.codigo_estacao = ?
        """
        cursor.execute(sql, [codigo])
        row = cursor.fetchone()
        if not row:
            return None
        cols = [c[0] for c in cursor.description]
        return dict(zip(cols, row))

    def salvar_estacao(self, dados: Dict[str, Any], modo_inclusao: bool = True) -> bool:
        cursor = self._get_cursor()
        if modo_inclusao:
            sql = """
                INSERT INTO USER_geoapolo_satfi_estacao (
                    codigo_estacao, descricao, codigo_departamento, data_cadastro,
                    codigo_usuario, usuario_responsavel, tag_servico, geoentcod,
                    modelo_estacao, codigo_localizacao, enderecoip, observacoes
                ) VALUES (?, ?, ?, GETDATE(), ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = [
                dados.get("codigo_estacao", ""),
                dados.get("descricao", ""),
                dados.get("codigo_departamento", ""),
                dados.get("codigo_usuario", ""),
                dados.get("usuario_responsavel", ""),
                dados.get("tag_servico", ""),
                dados.get("geoentcod", ""),
                dados.get("modelo_estacao", ""),
                dados.get("codigo_localizacao", ""),
                dados.get("enderecoip", ""),
                dados.get("observacoes", ""),
            ]
        else:
            sql = """
                UPDATE USER_geoapolo_satfi_estacao SET
                    descricao = ?,
                    codigo_departamento = ?,
                    codigo_usuario = ?,
                    usuario_responsavel = ?,
                    tag_servico = ?,
                    geoentcod = ?,
                    modelo_estacao = ?,
                    codigo_localizacao = ?,
                    enderecoip = ?,
                    observacoes = ?
                WHERE codigo_estacao = ?
            """
            params = [
                dados.get("descricao", ""),
                dados.get("codigo_departamento", ""),
                dados.get("codigo_usuario", ""),
                dados.get("usuario_responsavel", ""),
                dados.get("tag_servico", ""),
                dados.get("geoentcod", ""),
                dados.get("modelo_estacao", ""),
                dados.get("codigo_localizacao", ""),
                dados.get("enderecoip", ""),
                dados.get("observacoes", ""),
                dados.get("codigo_estacao", ""),
            ]

        cursor.execute(sql, params)
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def excluir_estacao(self, codigo: str) -> bool:
        cursor = self._get_cursor()
        # Remove vínculos com usuários
        cursor.execute("DELETE FROM USER_geoapolo_usuario_estacao WHERE codigo_estacao = ?", [codigo])
        # Remove estação
        cursor.execute("DELETE FROM USER_geoapolo_satfi_estacao WHERE codigo_estacao = ?", [codigo])
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def listar_hardware(self, codigo_estacao: str) -> List[Dict[str, Any]]:
        cursor = self._get_cursor()
        sql = """
            SELECT
                h.codigo_hardware,
                h.descricao,
                h.valor,
                CONVERT(VARCHAR(10), h.data_compra, 103) AS data_compra,
                CONVERT(VARCHAR(10), h.data_ativacao, 103) AS data_ativacao,
                ISNULL(h.tempo_garantia, 0) AS tempo_garantia,
                ISNULL(h.codigo_status_h, 1) AS codigo_status,
                h.codigo_estacao,
                ISNULL(h.codigoclasse, 0) AS codigo_classe,
                ISNULL(h.observacoes, '') AS observacoes,
                ISNULL(h.nf, '') AS nf,
                ISNULL(h.ip, '') AS ip,
                ISNULL(h.rack, '') AS rack,
                ISNULL(h.patchpanel, '') AS patchpanel
            FROM USER_geoapolo_satfi_hardware h WITH (NOLOCK)
            WHERE h.codigo_estacao = ?
            ORDER BY h.codigo_hardware ASC
        """
        cursor.execute(sql, [codigo_estacao])
        cols = [c[0] for c in cursor.description]
        registros = []
        for row in cursor.fetchall():
            registros.append(dict(zip(cols, row)))
        return registros

    def salvar_hardware(self, dados: Dict[str, Any], modo_inclusao: bool = True) -> bool:
        cursor = self._get_cursor()
        if modo_inclusao:
            sql = """
                INSERT INTO USER_geoapolo_satfi_hardware (
                    codigo_hardware, descricao, valor, tempo_garantia,
                    codigo_status_h, codigo_estacao, codigoclasse,
                    observacoes, nf, ip, rack, patchpanel
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = [
                dados.get("codigo_hardware", ""),
                dados.get("descricao", ""),
                float(dados.get("valor", 0.0) or 0.0),
                int(dados.get("tempo_garantia", 365) or 365),
                int(dados.get("codigo_status", 1) or 1),
                dados.get("codigo_estacao", ""),
                int(dados.get("codigo_classe", 0) or 0),
                dados.get("observacoes", ""),
                dados.get("nf", ""),
                dados.get("ip", ""),
                dados.get("rack", ""),
                dados.get("patchpanel", ""),
            ]
        else:
            sql = """
                UPDATE USER_geoapolo_satfi_hardware SET
                    descricao = ?, valor = ?, tempo_garantia = ?,
                    codigo_status_h = ?, codigoclasse = ?, observacoes = ?,
                    nf = ?, ip = ?, rack = ?, patchpanel = ?
                WHERE codigo_hardware = ?
            """
            params = [
                dados.get("descricao", ""),
                float(dados.get("valor", 0.0) or 0.0),
                int(dados.get("tempo_garantia", 365) or 365),
                int(dados.get("codigo_status", 1) or 1),
                int(dados.get("codigo_classe", 0) or 0),
                dados.get("observacoes", ""),
                dados.get("nf", ""),
                dados.get("ip", ""),
                dados.get("rack", ""),
                dados.get("patchpanel", ""),
                dados.get("codigo_hardware", ""),
            ]

        cursor.execute(sql, params)
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def excluir_hardware(self, codigo_hardware: str) -> bool:
        cursor = self._get_cursor()
        cursor.execute("DELETE FROM USER_geoapolo_satfi_hardware WHERE codigo_hardware = ?", [codigo_hardware])
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def listar_software(self, codigo_estacao: str) -> List[Dict[str, Any]]:
        cursor = self._get_cursor()
        sql = """
            SELECT
                s.codigo_software,
                s.descricao,
                ISNULL(s.nfsoft, '') AS nf,
                ISNULL(s.valor, 0) AS valor,
                CONVERT(VARCHAR(10), s.data_compra, 103) AS data_compra,
                CONVERT(VARCHAR(10), s.data_vencimento, 103) AS data_vencimento,
                ISNULL(s.tipo_licenca, '') AS tipo_licenca,
                s.codigo_estacao,
                ISNULL(s.codigoclasse, 0) AS codigo_classe,
                ISNULL(s.observacoes, '') AS observacoes
            FROM USER_geoapolo_satfi_software s WITH (NOLOCK)
            WHERE s.codigo_estacao = ?
            ORDER BY s.codigo_software ASC
        """
        cursor.execute(sql, [codigo_estacao])
        cols = [c[0] for c in cursor.description]
        registros = []
        for row in cursor.fetchall():
            registros.append(dict(zip(cols, row)))
        return registros

    def salvar_software(self, dados: Dict[str, Any], modo_inclusao: bool = True) -> bool:
        cursor = self._get_cursor()
        if modo_inclusao:
            sql = """
                INSERT INTO USER_geoapolo_satfi_software (
                    codigo_software, descricao, nfsoft, valor,
                    tipo_licenca, codigo_estacao, codigoclasse, observacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = [
                dados.get("codigo_software", ""),
                dados.get("descricao", ""),
                dados.get("nf", ""),
                float(dados.get("valor", 0.0) or 0.0),
                dados.get("tipo_licenca", ""),
                dados.get("codigo_estacao", ""),
                int(dados.get("codigo_classe", 0) or 0),
                dados.get("observacoes", ""),
            ]
        else:
            sql = """
                UPDATE USER_geoapolo_satfi_software SET
                    descricao = ?, nfsoft = ?, valor = ?,
                    tipo_licenca = ?, codigoclasse = ?, observacoes = ?
                WHERE codigo_software = ?
            """
            params = [
                dados.get("descricao", ""),
                dados.get("nf", ""),
                float(dados.get("valor", 0.0) or 0.0),
                dados.get("tipo_licenca", ""),
                int(dados.get("codigo_classe", 0) or 0),
                dados.get("observacoes", ""),
                dados.get("codigo_software", ""),
            ]

        cursor.execute(sql, params)
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def excluir_software(self, codigo_software: str) -> bool:
        cursor = self._get_cursor()
        cursor.execute("DELETE FROM USER_geoapolo_satfi_software WHERE codigo_software = ?", [codigo_software])
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def listar_usuarios(self, codigo_estacao: str) -> List[Dict[str, Any]]:
        cursor = self._get_cursor()
        sql = """
            SELECT
                ue.codigo_usuario,
                ISNULL(u.usunome, '') AS nome_usuario,
                ue.codigo_estacao,
                CONVERT(VARCHAR(10), ue.data_vinculo, 103) AS data_vinculo,
                ISNULL(ue.responsavel, 'Não') AS responsavel
            FROM USER_geoapolo_usuario_estacao ue WITH (NOLOCK)
            LEFT JOIN USER_geoapolo_usuarios u WITH (NOLOCK) ON ue.codigo_usuario = u.usucod
            WHERE ue.codigo_estacao = ?
            ORDER BY u.usunome ASC
        """
        cursor.execute(sql, [codigo_estacao])
        cols = [c[0] for c in cursor.description]
        registros = []
        for row in cursor.fetchall():
            registros.append(dict(zip(cols, row)))
        return registros

    def vincular_usuario(self, codigo_usuario: str, codigo_estacao: str, responsavel: str = "Não") -> bool:
        cursor = self._get_cursor()
        sql = """
            INSERT INTO USER_geoapolo_usuario_estacao (codigo_usuario, codigo_estacao, data_vinculo, responsavel)
            VALUES (?, ?, GETDATE(), ?)
        """
        cursor.execute(sql, [codigo_usuario, codigo_estacao, responsavel])
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def desvincular_usuario(self, codigo_usuario: str, codigo_estacao: str) -> bool:
        cursor = self._get_cursor()
        cursor.execute(
            "DELETE FROM USER_geoapolo_usuario_estacao WHERE codigo_usuario = ? AND codigo_estacao = ?",
            [codigo_usuario, codigo_estacao],
        )
        if self._conn and hasattr(self._conn, "commit"):
            self._conn.commit()
        return True

    def listar_departamentos(self) -> List[Dict[str, str]]:
        try:
            cursor = self._get_cursor()
            sql = "SELECT codigo_departamento, nome_departamento FROM USER_geoapolo_departamentos WITH (NOLOCK) ORDER BY nome_departamento"
            cursor.execute(sql)
            return [{"codigo": str(r[0]), "nome": str(r[1])} for r in cursor.fetchall()]
        except Exception:
            return []

    def listar_localizacoes(self) -> List[Dict[str, str]]:
        try:
            cursor = self._get_cursor()
            sql = "SELECT codigo_localizacao, localizacao FROM USER_geoapolo_satfi_localizacao_fisica WITH (NOLOCK) ORDER BY localizacao"
            cursor.execute(sql)
            return [{"codigo": str(r[0]), "nome": str(r[1])} for r in cursor.fetchall()]
        except Exception:
            return []
