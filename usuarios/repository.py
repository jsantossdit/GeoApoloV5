"""
Repositório de dados para Gestão de Usuários, Grupos e Perfis de Acesso.
GeoApolo V5
Compatível com SQL Server nativo (WITH NOLOCK) e SQLite em memória.
"""

from typing import List, Optional
from usuarios.models import (
    UsuarioDTO,
    DepartamentoDTO,
    SistemaDTO,
    GrupoUsuarioDTO,
    VinculoGrupoUsuarioDTO,
    ObjetoAcessoDTO,
    PerfilAcessoItemDTO,
)


class UsuariosRepository:
    """Repositório de persistência e consultas para Usuários e Perfis de Acesso."""

    def __init__(self, connection):
        self.conn = connection
        self._is_sql_server = not hasattr(connection, "isolation_level")

    def _nolock(self) -> str:
        return "WITH (NOLOCK)" if self._is_sql_server else ""

    def listar_usuarios(self, filtro_nome: str = "", apenas_ativos: bool = True) -> List[UsuarioDTO]:
        """Lista usuários cadastrados com suporte a filtro e status."""
        cur = self.conn.cursor()
        nolock = self._nolock()

        sql = f"""
            SELECT u.codigo_usuario, u.usucod, u.nome_completo, u.flagativo, u.login, u.email,
                   u.data_nascimento, u.codigo_departamento, d.nome_departamento, u.usucod_apolo,
                   u.senha_alvo, u.senha
            FROM USER_geoapolo_usuarios u {nolock}
            LEFT JOIN USER_geoapolo_departamentos d {nolock} ON u.codigo_departamento = d.codigo_departamento
            WHERE 1=1
        """
        params = []
        if apenas_ativos:
            sql += " AND u.flagativo IN ('A', 'S')"
        if filtro_nome.strip():
            sql += " AND (u.nome_completo LIKE ? OR u.login LIKE ?)"
            termo = f"%{filtro_nome.strip()}%"
            params.extend([termo, termo])

        sql += " ORDER BY u.nome_completo ASC"

        cur.execute(sql, params)
        rows = cur.fetchall()
        usuarios = []
        for r in rows:
            usuarios.append(UsuarioDTO(
                codigo_usuario=str(r[0] or ""),
                usucod=str(r[1] or ""),
                nome_completo=str(r[2] or ""),
                flagativo=str(r[3] or "A"),
                login=str(r[4] or ""),
                email=str(r[5] or ""),
                data_nascimento=str(r[6]) if r[6] else None,
                codigo_departamento=str(r[7] or ""),
                nome_departamento=str(r[8] or ""),
                usucod_apolo=str(r[9] or ""),
                senha_alvo=str(r[10] or ""),
                senha=str(r[11] or ""),
            ))
        return usuarios

    def obter_usuario_por_usucod(self, usucod: str) -> Optional[UsuarioDTO]:
        """Localiza usuário pelo código identificador (usucod)."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT u.codigo_usuario, u.usucod, u.nome_completo, u.flagativo, u.login, u.email,
                   u.data_nascimento, u.codigo_departamento, d.nome_departamento, u.usucod_apolo,
                   u.senha_alvo, u.senha
            FROM USER_geoapolo_usuarios u {nolock}
            LEFT JOIN USER_geoapolo_departamentos d {nolock} ON u.codigo_departamento = d.codigo_departamento
            WHERE u.usucod = ?
        """
        cur.execute(sql, [usucod])
        r = cur.fetchone()
        if not r:
            return None
        return UsuarioDTO(
            codigo_usuario=str(r[0] or ""),
            usucod=str(r[1] or ""),
            nome_completo=str(r[2] or ""),
            flagativo=str(r[3] or "A"),
            login=str(r[4] or ""),
            email=str(r[5] or ""),
            data_nascimento=str(r[6]) if r[6] else None,
            codigo_departamento=str(r[7] or ""),
            nome_departamento=str(r[8] or ""),
            usucod_apolo=str(r[9] or ""),
            senha_alvo=str(r[10] or ""),
            senha=str(r[11] or ""),
        )

    def obter_usuario_por_login(self, login: str) -> Optional[UsuarioDTO]:
        """Localiza usuário pelo login único de acesso."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT u.codigo_usuario, u.usucod, u.nome_completo, u.flagativo, u.login, u.email,
                   u.data_nascimento, u.codigo_departamento, d.nome_departamento, u.usucod_apolo,
                   u.senha_alvo, u.senha
            FROM USER_geoapolo_usuarios u {nolock}
            LEFT JOIN USER_geoapolo_departamentos d {nolock} ON u.codigo_departamento = d.codigo_departamento
            WHERE u.login = ?
        """
        cur.execute(sql, [login])
        r = cur.fetchone()
        if not r:
            return None
        return UsuarioDTO(
            codigo_usuario=str(r[0] or ""),
            usucod=str(r[1] or ""),
            nome_completo=str(r[2] or ""),
            flagativo=str(r[3] or "A"),
            login=str(r[4] or ""),
            email=str(r[5] or ""),
            data_nascimento=str(r[6]) if r[6] else None,
            codigo_departamento=str(r[7] or ""),
            nome_departamento=str(r[8] or ""),
            usucod_apolo=str(r[9] or ""),
            senha_alvo=str(r[10] or ""),
            senha=str(r[11] or ""),
        )

    def salvar_usuario(self, u: UsuarioDTO) -> bool:
        """Insere ou atualiza os dados de um usuário."""
        cur = self.conn.cursor()
        existente = self.obter_usuario_por_usucod(u.usucod)

        if existente:
            sql = """
                UPDATE USER_geoapolo_usuarios
                SET nome_completo = ?, flagativo = ?, login = ?, email = ?,
                    data_nascimento = ?, codigo_departamento = ?, usucod_apolo = ?,
                    senha_alvo = ?, senha = ?
                WHERE usucod = ?
            """
            cur.execute(sql, [
                u.nome_completo, u.flagativo, u.login, u.email,
                u.data_nascimento, u.codigo_departamento, u.usucod_apolo,
                u.senha_alvo, u.senha, u.usucod
            ])
        else:
            sql = """
                INSERT INTO USER_geoapolo_usuarios (
                    codigo_usuario, usucod, nome_completo, flagativo, login, email,
                    data_nascimento, codigo_departamento, usucod_apolo, senha_alvo, senha
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cur.execute(sql, [
                u.codigo_usuario or u.usucod, u.usucod, u.nome_completo, u.flagativo,
                u.login, u.email, u.data_nascimento, u.codigo_departamento,
                u.usucod_apolo, u.senha_alvo, u.senha
            ])
        self.conn.commit()
        return True

    def excluir_usuario(self, usucod: str) -> bool:
        """Remove o usuário e seus vínculos de sistemas e grupos."""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM USER_geoapolo_usuariossistemas WHERE usucod = ?", [usucod])
        cur.execute("DELETE FROM USER_geoapolo_grupousuario WHERE usucod = ?", [usucod])
        cur.execute("DELETE FROM USER_geoapolo_usuarios WHERE usucod = ?", [usucod])
        self.conn.commit()
        return True

    def listar_departamentos(self, empcod: str = "") -> List[DepartamentoDTO]:
        """Lista departamentos ativos cadastrados."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT ugd.codigo_departamento, ugd.nome_departamento, ugd.empcod,
                   COALESCE(uge.empnome, '') AS empnome, ugd.flagativo
            FROM USER_geoapolo_departamentos ugd {nolock}
            LEFT JOIN USER_geoapolo_empresas uge {nolock} ON ugd.empcod = uge.empcod
            WHERE ugd.flagativo = 'S'
        """
        params = []
        if empcod.strip():
            sql += " AND ugd.empcod = ?"
            params.append(empcod.strip())
        sql += " ORDER BY ugd.nome_departamento ASC"

        cur.execute(sql, params)
        return [
            DepartamentoDTO(
                codigo_departamento=str(r[0]),
                nome_departamento=str(r[1]),
                empcod=str(r[2] or ""),
                empnome=str(r[3] or ""),
                flagativo=str(r[4] or "S"),
            )
            for r in cur.fetchall()
        ]

    def listar_sistemas(self) -> List[SistemaDTO]:
        """Lista todos os sistemas corporativos disponíveis."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"SELECT codigo_sistema, descricao, COALESCE(sigla, '') FROM USER_geoapolo_sistemas {nolock} ORDER BY descricao ASC"
        cur.execute(sql)
        return [
            SistemaDTO(
                codigo_sistema=str(r[0]),
                descricao=str(r[1]),
                sigla=str(r[2] or ""),
            )
            for r in cur.fetchall()
        ]

    def listar_sistemas_usuario(self, usucod: str) -> List[SistemaDTO]:
        """Lista sistemas vinculados a um usuário específico."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT s.codigo_sistema, s.descricao, COALESCE(s.sigla, '')
            FROM USER_geoapolo_usuariossistemas us {nolock}
            INNER JOIN USER_geoapolo_sistemas s {nolock} ON us.codigo_sistema = s.codigo_sistema
            WHERE us.usucod = ?
            ORDER BY s.descricao ASC
        """
        cur.execute(sql, [usucod])
        return [
            SistemaDTO(
                codigo_sistema=str(r[0]),
                descricao=str(r[1]),
                sigla=str(r[2] or ""),
            )
            for r in cur.fetchall()
        ]

    def vincular_sistema_usuario(self, usucod: str, codigo_sistema: str) -> bool:
        """Associa um sistema ao usuário."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT 1 FROM USER_geoapolo_usuariossistemas WHERE usucod = ? AND codigo_sistema = ?",
            [usucod, codigo_sistema],
        )
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO USER_geoapolo_usuariossistemas (usucod, codigo_sistema) VALUES (?, ?)",
                [usucod, codigo_sistema],
            )
            self.conn.commit()
        return True

    def desvincular_sistema_usuario(self, usucod: str, codigo_sistema: str) -> bool:
        """Remove associação entre usuário e sistema."""
        cur = self.conn.cursor()
        cur.execute(
            "DELETE FROM USER_geoapolo_usuariossistemas WHERE usucod = ? AND codigo_sistema = ?",
            [usucod, codigo_sistema],
        )
        self.conn.commit()
        return True

    def listar_grupos(self) -> List[GrupoUsuarioDTO]:
        """Lista todos os grupos e quantidade de usuários participantes."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT g.codigo_grupo, g.descricao, COUNT(gu.usucod) AS total_usuarios
            FROM USER_geoapolo_grupo g {nolock}
            LEFT JOIN USER_geoapolo_grupousuario gu {nolock} ON g.codigo_grupo = gu.codigo_grupo
            GROUP BY g.codigo_grupo, g.descricao
            ORDER BY g.descricao ASC
        """
        cur.execute(sql)
        return [
            GrupoUsuarioDTO(
                codigo_grupo=str(r[0]),
                descricao=str(r[1]),
                total_usuarios=int(r[2] or 0),
            )
            for r in cur.fetchall()
        ]

    def salvar_grupo(self, codigo_grupo: str, descricao: str) -> bool:
        """Cria ou atualiza grupo de usuários."""
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM USER_geoapolo_grupo WHERE codigo_grupo = ?", [codigo_grupo])
        if cur.fetchone():
            cur.execute(
                "UPDATE USER_geoapolo_grupo SET descricao = ? WHERE codigo_grupo = ?",
                [descricao, codigo_grupo],
            )
        else:
            cur.execute(
                "INSERT INTO USER_geoapolo_grupo (codigo_grupo, descricao) VALUES (?, ?)",
                [codigo_grupo, descricao],
            )
        self.conn.commit()
        return True

    def excluir_grupo(self, codigo_grupo: str) -> bool:
        """Remove grupo e todos os seus vínculos de objetos e usuários."""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM USER_geoapolo_grupobjetos WHERE codigo_grupo = ?", [codigo_grupo])
        cur.execute("DELETE FROM USER_geoapolo_grupousuario WHERE codigo_grupo = ?", [codigo_grupo])
        cur.execute("DELETE FROM USER_geoapolo_grupo WHERE codigo_grupo = ?", [codigo_grupo])
        self.conn.commit()
        return True

    def listar_usuarios_grupo(self, codigo_grupo: str) -> List[VinculoGrupoUsuarioDTO]:
        """Lista usuários pertencentes a um grupo de segurança."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT gu.codigo_grupo, g.descricao, u.usucod, u.login, u.nome_completo
            FROM USER_geoapolo_grupousuario gu {nolock}
            INNER JOIN USER_geoapolo_grupo g {nolock} ON gu.codigo_grupo = g.codigo_grupo
            INNER JOIN USER_geoapolo_usuarios u {nolock} ON gu.usucod = u.usucod
            WHERE gu.codigo_grupo = ?
            ORDER BY u.nome_completo ASC
        """
        cur.execute(sql, [codigo_grupo])
        return [
            VinculoGrupoUsuarioDTO(
                codigo_grupo=str(r[0]),
                nome_grupo=str(r[1]),
                usucod=str(r[2]),
                login=str(r[3]),
                nome_completo=str(r[4]),
            )
            for r in cur.fetchall()
        ]

    def vincular_usuario_grupo(self, codigo_grupo: str, usucod: str) -> bool:
        """Insere usuário no grupo de segurança."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT 1 FROM USER_geoapolo_grupousuario WHERE codigo_grupo = ? AND usucod = ?",
            [codigo_grupo, usucod],
        )
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO USER_geoapolo_grupousuario (codigo_grupo, usucod) VALUES (?, ?)",
                [codigo_grupo, usucod],
            )
            self.conn.commit()
        return True

    def desvincular_usuario_grupo(self, codigo_grupo: str, usucod: str) -> bool:
        """Remove usuário do grupo."""
        cur = self.conn.cursor()
        cur.execute(
            "DELETE FROM USER_geoapolo_grupousuario WHERE codigo_grupo = ? AND usucod = ?",
            [codigo_grupo, usucod],
        )
        self.conn.commit()
        return True

    def listar_objetos_perfil(self, codigo_grupo: str, categoria: str = "") -> List[PerfilAcessoItemDTO]:
        """Lista status de acesso a telas e recursos para um grupo."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"""
            SELECT o.codigo_objeto, o.nome_objeto, COALESCE(o.nome_amigavel, o.nome_objeto),
                   COALESCE(o.categoria, 'Geral'), COALESCE(go.statusacesso, 'N')
            FROM USER_geoapolo_objetos o {nolock}
            LEFT JOIN USER_geoapolo_grupobjetos go {nolock}
              ON o.codigo_objeto = go.codigo_objeto AND go.codigo_grupo = ?
            WHERE 1=1
        """
        params = [codigo_grupo]
        if categoria.strip():
            sql += " AND o.categoria = ?"
            params.append(categoria.strip())

        sql += " ORDER BY o.categoria, o.nome_amigavel"
        cur.execute(sql, params)
        return [
            PerfilAcessoItemDTO(
                codigo_objeto=str(r[0]),
                nome_objeto=str(r[1]),
                nome_amigavel=str(r[2]),
                categoria=str(r[3]),
                codigo_grupo=codigo_grupo,
                statusacesso=str(r[4]),
            )
            for r in cur.fetchall()
        ]

    def listar_categorias_objetos(self) -> List[str]:
        """Lista categorias distintas de objetos/menus."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        sql = f"SELECT DISTINCT categoria FROM USER_geoapolo_objetos {nolock} WHERE categoria IS NOT NULL ORDER BY categoria"
        cur.execute(sql)
        return [str(r[0]) for r in cur.fetchall() if r[0]]

    def atualizar_status_acesso(self, codigo_grupo: str, codigo_objeto: str, statusacesso: str) -> bool:
        """Atualiza a permissão de acesso (A = Liberado, N = Bloqueado)."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT 1 FROM USER_geoapolo_grupobjetos WHERE codigo_grupo = ? AND codigo_objeto = ?",
            [codigo_grupo, codigo_objeto],
        )
        if cur.fetchone():
            cur.execute(
                "UPDATE USER_geoapolo_grupobjetos SET statusacesso = ? WHERE codigo_grupo = ? AND codigo_objeto = ?",
                [statusacesso, codigo_grupo, codigo_objeto],
            )
        else:
            cur.execute(
                "INSERT INTO USER_geoapolo_grupobjetos (codigo_grupo, codigo_objeto, statusacesso) VALUES (?, ?, ?)",
                [codigo_grupo, codigo_objeto, statusacesso],
            )
        self.conn.commit()
        return True
