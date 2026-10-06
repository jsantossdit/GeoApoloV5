"""
Repositório de persistência de Produtos e Grupos de Produtos.
GeoApolo V5
Equivalente a unt_cadprodutos do Delphi.
"""

from typing import List, Optional, Tuple
from produtos.models import ProdutoDTO, GrupoProdutoDTO


class ProdutosRepository:
    """Repositório para manipulação de USER_geoapolo_produtos e USER_geoapolo_produto_grupo."""

    def __init__(self, connection):
        self.conn = connection
        self._is_sql_server = not hasattr(connection, "isolation_level")
        self._garantir_schema_produtos()

    def _garantir_schema_produtos(self):
        """Garante a existência das colunas unidade_medida, codigo_inmetro e codigo_lote."""
        if not self.conn:
            return
        try:
            cur = self.conn.cursor()
            if self._is_sql_server:
                cur.execute("""
                    IF OBJECT_ID('USER_geoapolo_produtos', 'U') IS NOT NULL
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM syscolumns WHERE id = OBJECT_ID('USER_geoapolo_produtos') AND name = 'codigo_inmetro')
                            ALTER TABLE USER_geoapolo_produtos ADD codigo_inmetro VARCHAR(50) NULL;

                        IF NOT EXISTS (SELECT 1 FROM syscolumns WHERE id = OBJECT_ID('USER_geoapolo_produtos') AND name = 'codigo_lote')
                            ALTER TABLE USER_geoapolo_produtos ADD codigo_lote VARCHAR(50) NULL;

                        IF NOT EXISTS (SELECT 1 FROM syscolumns WHERE id = OBJECT_ID('USER_geoapolo_produtos') AND name = 'unidade_medida')
                        BEGIN
                            ALTER TABLE USER_geoapolo_produtos ADD unidade_medida VARCHAR(20) NULL;
                            IF EXISTS (SELECT 1 FROM syscolumns WHERE id = OBJECT_ID('USER_geoapolo_produtos') AND name = 'tamanho')
                                EXEC('UPDATE USER_geoapolo_produtos SET unidade_medida = tamanho WHERE (unidade_medida IS NULL OR unidade_medida = '''') AND tamanho IS NOT NULL AND tamanho <> ''''');
                        END
                    END

                    -- Tabela associativa de Marcas do Produto
                    IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USER_geoapolo_marca_produtos' AND xtype = 'U')
                    BEGIN
                        CREATE TABLE USER_geoapolo_marca_produtos (
                            codigo_marca NUMERIC(10, 0) NOT NULL,
                            prodcod NUMERIC(10, 0) NOT NULL,
                            CONSTRAINT pk_marcaprod PRIMARY KEY (codigo_marca, prodcod)
                        );
                        CREATE INDEX idx_marcaprod_prodcod ON USER_geoapolo_marca_produtos (prodcod);
                    END

                    -- Tabela associativa de Cores do Produto
                    IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USER_geoapolo_produto_cor' AND xtype = 'U')
                    BEGIN
                        CREATE TABLE USER_geoapolo_produto_cor (
                            codigo_cor NUMERIC(10, 0) NOT NULL,
                            prodcod NUMERIC(10, 0) NOT NULL,
                            CONSTRAINT pk_codprodcor PRIMARY KEY (codigo_cor, prodcod)
                        );
                        CREATE INDEX idx_codprodcor_prodcod ON USER_geoapolo_produto_cor (prodcod);
                    END

                    -- Tabela de Fotos do Produto
                    IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USER_geoapolo_produto_foto' AND xtype = 'U')
                    BEGIN
                        CREATE TABLE USER_geoapolo_produto_foto (
                            prodcod NUMERIC(10, 0) NOT NULL,
                            foto_produto VARBINARY(MAX) NULL,
                            CONSTRAINT pk_fotocodigoproduto PRIMARY KEY (prodcod)
                        );
                    END
                """)
            else:
                cur.execute("PRAGMA table_info(USER_geoapolo_produtos)")
                colunas = [r[1] for r in cur.fetchall()]
                if colunas:
                    if "codigo_inmetro" not in colunas:
                        cur.execute("ALTER TABLE USER_geoapolo_produtos ADD COLUMN codigo_inmetro TEXT")
                    if "codigo_lote" not in colunas:
                        cur.execute("ALTER TABLE USER_geoapolo_produtos ADD COLUMN codigo_lote TEXT")
                    if "unidade_medida" not in colunas:
                        cur.execute("ALTER TABLE USER_geoapolo_produtos ADD COLUMN unidade_medida TEXT")
                        if "tamanho" in colunas:
                            cur.execute("UPDATE USER_geoapolo_produtos SET unidade_medida = tamanho WHERE (unidade_medida IS NULL OR unidade_medida = '') AND tamanho IS NOT NULL AND tamanho != ''")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS USER_geoapolo_marca_produtos (
                        codigo_marca INTEGER NOT NULL,
                        prodcod INTEGER NOT NULL,
                        PRIMARY KEY (codigo_marca, prodcod)
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS USER_geoapolo_produto_cor (
                        codigo_cor INTEGER NOT NULL,
                        prodcod INTEGER NOT NULL,
                        PRIMARY KEY (codigo_cor, prodcod)
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS USER_geoapolo_produto_foto (
                        prodcod INTEGER NOT NULL PRIMARY KEY,
                        foto_produto BLOB
                    )
                """)
            self.conn.commit()
        except Exception:
            pass

    def _nolock(self) -> str:
        return "WITH (NOLOCK)" if self._is_sql_server else ""

    @property
    def _tem_coluna_tamanho(self) -> bool:
        if not hasattr(self, "_cached_tem_tamanho"):
            try:
                cur = self.conn.cursor()
                if self._is_sql_server:
                    cur.execute("""
                        SELECT 1 FROM syscolumns 
                        WHERE id = OBJECT_ID('USER_geoapolo_produtos') AND name = 'tamanho'
                    """)
                    self._cached_tem_tamanho = cur.fetchone() is not None
                else:
                    cur.execute("PRAGMA table_info(USER_geoapolo_produtos)")
                    cols = [r[1] for r in cur.fetchall()]
                    self._cached_tem_tamanho = "tamanho" in cols
            except Exception:
                self._cached_tem_tamanho = False
        return self._cached_tem_tamanho

    @property
    def _coluna_unidade_sql(self) -> str:
        if self._tem_coluna_tamanho:
            return "COALESCE(p.unidade_medida, p.tamanho, '')"
        return "COALESCE(p.unidade_medida, '')"


    def contar_produtos(self) -> int:
        """Retorna o número total de produtos cadastrados (FormActivate do Delphi)."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        try:
            cur.execute(f"SELECT COUNT(1) FROM USER_geoapolo_produtos {nolock}")
            row = cur.fetchone()
            return int(row[0]) if row and row[0] is not None else 0
        except Exception:
            return 0

    def obter_proximo_codigo(self) -> int:
        """Gera o próximo código sequencial de produto."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        try:
            cur.execute(f"SELECT COALESCE(MAX(CAST(prodcod AS INT)), 0) + 1 FROM USER_geoapolo_produtos {nolock}")
            row = cur.fetchone()
            return int(row[0]) if row and row[0] is not None else 1
        except Exception:
            return 1

    def listar_grupos(self) -> List[GrupoProdutoDTO]:
        """Lista grupos de produtos cadastrados."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        try:
            sql = f"""
                SELECT grupocod, codigo_estruturado, nome_grupo
                FROM USER_geoapolo_produto_grupo {nolock}
                ORDER BY codigo_estruturado ASC, nome_grupo ASC
            """
            cur.execute(sql)
            return [
                GrupoProdutoDTO(
                    grupocod=int(r[0]),
                    codigo_estruturado=str(r[1] or ""),
                    nome_grupo=str(r[2] or ""),
                )
                for r in cur.fetchall()
            ]
        except Exception:
            return []

    def obter_grupo(self, grupocod: int) -> Optional[GrupoProdutoDTO]:
        """Obtém um grupo de produto pelo código."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        cur.execute(
            f"SELECT grupocod, codigo_estruturado, nome_grupo FROM USER_geoapolo_produto_grupo {nolock} WHERE grupocod = ?",
            [grupocod]
        )
        r = cur.fetchone()
        if not r:
            return None
        return GrupoProdutoDTO(
            grupocod=int(r[0]),
            codigo_estruturado=str(r[1] or ""),
            nome_grupo=str(r[2] or ""),
        )

    def salvar_grupo(self, g: GrupoProdutoDTO) -> bool:
        """Insere ou atualiza um grupo de produtos."""
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM USER_geoapolo_produto_grupo WHERE grupocod = ?", [g.grupocod])
        if cur.fetchone():
            sql = """
                UPDATE USER_geoapolo_produto_grupo
                SET codigo_estruturado = ?, nome_grupo = ?
                WHERE grupocod = ?
            """
            cur.execute(sql, [g.codigo_estruturado, g.nome_grupo, g.grupocod])
        else:
            sql = """
                INSERT INTO USER_geoapolo_produto_grupo (grupocod, codigo_estruturado, nome_grupo)
                VALUES (?, ?, ?)
            """
            cur.execute(sql, [g.grupocod, g.codigo_estruturado, g.nome_grupo])
        self.conn.commit()
        return True

    def excluir_grupo(self, grupocod: int) -> bool:
        """Remove um grupo de produto."""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM USER_geoapolo_produto_grupo WHERE grupocod = ?", [grupocod])
        self.conn.commit()
        return True

    def gerar_codigo_configcod(self, tabela: str = "USER_geoapolo_produtos", empresa: str = "1.01") -> int:
        """Gera e atualiza código via geoapolo_configcod."""
        from core.recursos import geoapolo_configcod
        cod_str = geoapolo_configcod(empresa=empresa, tabela=tabela, atualiza="Sim", connection=self.conn)
        try:
            return int(cod_str)
        except ValueError:
            return self.obter_proximo_codigo()

    @property
    def _tabela_marcas(self) -> str:
        """Determina dinamicamente a tabela de marcas com a coluna descricao_marca."""
        if not hasattr(self, "_cached_tabela_marcas"):
            cur = self.conn.cursor()
            tab = "USER_geoapolo_marcas"
            for t in ("USER_geoapolo_marcas", "USER_geoapolo_produto_marcas"):
                try:
                    cur.execute(f"SELECT descricao_marca FROM {t} WHERE 1 = 0")
                    tab = t
                    break
                except Exception:
                    pass
            self._cached_tabela_marcas = tab
        return self._cached_tabela_marcas

    def listar_marcas(self) -> List[Tuple[int, str]]:
        """Lista todas as marcas cadastradas."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        tab = self._tabela_marcas
        try:
            cur.execute(f"SELECT codigo_marca, descricao_marca FROM {tab} {nolock} ORDER BY descricao_marca ASC")
            return [(int(r[0]), str(r[1] or "").strip()) for r in cur.fetchall()]
        except Exception:
            return []

    def listar_cores(self) -> List[Tuple[int, str]]:
        """Lista todas as cores cadastradas em USER_geoapolo_produto_cores."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        try:
            cur.execute(f"SELECT codigo_cor, descricao_cor FROM USER_geoapolo_produto_cores {nolock} ORDER BY descricao_cor ASC")
            return [(int(r[0]), str(r[1] or "").strip()) for r in cur.fetchall()]
        except Exception:
            return []

    def obter_ou_criar_marca(self, descricao: str) -> Tuple[int, str]:
        """
        Localiza a marca pela descrição (case-insensitive). Se não existir,
        insere na tabela de marcas atribuindo o próximo código sequencial.
        Retorna (codigo_marca, descricao_marca).
        """
        desc = str(descricao or "").strip().upper()
        if not desc:
            return 0, ""

        cur = self.conn.cursor()
        nolock = self._nolock()
        tab = self._tabela_marcas
        try:
            cur.execute(
                f"SELECT codigo_marca, descricao_marca FROM {tab} {nolock} WHERE UPPER(RTRIM(LTRIM(descricao_marca))) = ?",
                [desc]
            )
            r = cur.fetchone()
            if r:
                return int(r[0]), str(r[1] or "").strip()

            cur.execute(f"SELECT COALESCE(MAX(codigo_marca), 0) + 1 FROM {tab} {nolock}")
            row_cod = cur.fetchone()
            novo_cod = int(row_cod[0]) if row_cod and row_cod[0] is not None else 1

            cur.execute(
                f"INSERT INTO {tab} (codigo_marca, descricao_marca) VALUES (?, ?)",
                [novo_cod, desc]
            )
            self.conn.commit()
            return novo_cod, desc
        except Exception:
            return 0, desc

    def obter_marca_do_produto(self, prodcod: int) -> Tuple[Optional[int], str]:
        """Recupera o código e nome da marca associada a um produto."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        tab = self._tabela_marcas
        try:
            sql = f"""
                SELECT mp.codigo_marca, pm.descricao_marca
                FROM USER_geoapolo_marca_produtos mp {nolock}
                INNER JOIN {tab} pm {nolock} ON mp.codigo_marca = pm.codigo_marca
                WHERE mp.prodcod = ?
            """
            cur.execute(sql, [prodcod])
            r = cur.fetchone()
            if r:
                return int(r[0]), str(r[1] or "").strip()
        except Exception:
            pass
        return None, ""

    def obter_cores_do_produto(self, prodcod: int) -> Tuple[List[int], List[str]]:
        """Recupera os códigos e descrições das cores vinculadas a um produto."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        cods = []
        nomes = []
        try:
            sql = f"""
                SELECT pc.codigo_cor, c.descricao_cor
                FROM USER_geoapolo_produto_cor pc {nolock}
                INNER JOIN USER_geoapolo_produto_cores c {nolock} ON pc.codigo_cor = c.codigo_cor
                WHERE pc.prodcod = ?
                ORDER BY c.descricao_cor ASC
            """
            cur.execute(sql, [prodcod])
            for r in cur.fetchall():
                cods.append(int(r[0]))
                nomes.append(str(r[1] or "").strip())
        except Exception:
            pass
        return cods, nomes

    def listar_produtos(self, filtro: str = "", grupocod: Optional[int] = None) -> List[ProdutoDTO]:
        """Lista produtos com filtro opcional por código/nome e por grupo, incluindo Marca."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        where_clauses = []
        params = []

        if filtro and filtro.strip():
            f = f"%{filtro.strip().upper()}%"
            where_clauses.append("(UPPER(p.prodnome) LIKE ? OR CAST(p.prodcod AS VARCHAR) LIKE ? OR UPPER(pm.descricao_marca) LIKE ?)")
            params.extend([f, f, f])

        if grupocod is not None and grupocod > 0:
            where_clauses.append("p.grupocod = ?")
            params.append(grupocod)

        where_str = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        col_unid = self._coluna_unidade_sql
        tab_marca = self._tabela_marcas
        sql = f"""
            SELECT p.prodcod, p.prodnome, p.descricao_alternativa, p.grupocod,
                   COALESCE(g.nome_grupo, ''),
                   {col_unid},
                   p.observacoes,
                   mp.codigo_marca, COALESCE(pm.descricao_marca, ''),
                   COALESCE(p.codigo_inmetro, ''), COALESCE(p.codigo_lote, '')
            FROM USER_geoapolo_produtos p {nolock}
            LEFT JOIN USER_geoapolo_produto_grupo g {nolock} ON p.grupocod = g.grupocod
            LEFT JOIN USER_geoapolo_marca_produtos mp {nolock} ON p.prodcod = mp.prodcod
            LEFT JOIN {tab_marca} pm {nolock} ON mp.codigo_marca = pm.codigo_marca
            {where_str}
            ORDER BY p.prodcod ASC
        """
        try:
            cur.execute(sql, params)
            produtos = []
            for r in cur.fetchall():
                unid_val = str(r[5] or "")
                produtos.append(ProdutoDTO(
                    prodcod=int(r[0]),
                    prodnome=str(r[1] or ""),
                    descricao_alternativa=str(r[2] or ""),
                    grupocod=int(r[3]) if r[3] is not None else None,
                    nome_grupo=str(r[4] or ""),
                    unidade_medida=unid_val,
                    tamanho=unid_val,
                    observacoes=str(r[6] or ""),
                    codigo_marca=int(r[7]) if r[7] is not None else None,
                    nome_marca=str(r[8] or "").strip(),
                    codigo_inmetro=str(r[9] or ""),
                    codigo_lote=str(r[10] or ""),
                ))
            return produtos
        except Exception:
            # Fallback sem a tabela USER_geoapolo_marca_produtos ou sem novas colunas
            fallback_where = []
            fallback_params = []
            if filtro and filtro.strip():
                f = f"%{filtro.strip().upper()}%"
                fallback_where.append("(UPPER(p.prodnome) LIKE ? OR CAST(p.prodcod AS VARCHAR) LIKE ?)")
                fallback_params.extend([f, f])
            if grupocod is not None and grupocod > 0:
                fallback_where.append("p.grupocod = ?")
                fallback_params.append(grupocod)
            where_fb_str = f"WHERE {' AND '.join(fallback_where)}" if fallback_where else ""
            sql_fb = f"""
                SELECT p.prodcod, p.prodnome, p.descricao_alternativa, p.grupocod,
                       COALESCE(g.nome_grupo, ''), {col_unid}, p.observacoes
                FROM USER_geoapolo_produtos p {nolock}
                LEFT JOIN USER_geoapolo_produto_grupo g {nolock} ON p.grupocod = g.grupocod
                {where_fb_str}
                ORDER BY p.prodcod ASC
            """
            cur.execute(sql_fb, fallback_params)
            return [
                ProdutoDTO(
                    prodcod=int(r[0]),
                    prodnome=str(r[1] or ""),
                    descricao_alternativa=str(r[2] or ""),
                    grupocod=int(r[3]) if r[3] is not None else None,
                    nome_grupo=str(r[4] or ""),
                    unidade_medida=str(r[5] or ""),
                    tamanho=str(r[5] or ""),
                    observacoes=str(r[6] or ""),
                )
                for r in cur.fetchall()
            ]

    def obter_produto(self, prodcod: int) -> Optional[ProdutoDTO]:
        """Busca um produto específico pelo código, com suas marcas e cores vinculadas."""
        cur = self.conn.cursor()
        nolock = self._nolock()
        col_unid = self._coluna_unidade_sql
        try:
            sql = f"""
                SELECT p.prodcod, p.prodnome, p.descricao_alternativa, p.grupocod,
                       COALESCE(g.nome_grupo, ''),
                       {col_unid},
                       p.observacoes,
                       COALESCE(p.codigo_inmetro, ''), COALESCE(p.codigo_lote, '')
                FROM USER_geoapolo_produtos p {nolock}
                LEFT JOIN USER_geoapolo_produto_grupo g {nolock} ON p.grupocod = g.grupocod
                WHERE p.prodcod = ?
            """
            cur.execute(sql, [prodcod])
            r = cur.fetchone()
            if not r:
                return None
            unid = str(r[5] or "")
            inmetro = str(r[7] or "")
            lote = str(r[8] or "")
        except Exception:
            sql_fb = f"""
                SELECT p.prodcod, p.prodnome, p.descricao_alternativa, p.grupocod,
                       COALESCE(g.nome_grupo, ''), {col_unid}, p.observacoes
                FROM USER_geoapolo_produtos p {nolock}
                LEFT JOIN USER_geoapolo_produto_grupo g {nolock} ON p.grupocod = g.grupocod
                WHERE p.prodcod = ?
            """
            cur.execute(sql_fb, [prodcod])
            r = cur.fetchone()
            if not r:
                return None
            unid = str(r[5] or "")
            inmetro = ""
            lote = ""

        cod_marca, nome_marca = self.obter_marca_do_produto(prodcod)
        cores_cods, cores_nomes = self.obter_cores_do_produto(prodcod)

        return ProdutoDTO(
            prodcod=int(r[0]),
            prodnome=str(r[1] or ""),
            descricao_alternativa=str(r[2] or ""),
            grupocod=int(r[3]) if r[3] is not None else None,
            nome_grupo=str(r[4] or ""),
            codigo_marca=cod_marca,
            nome_marca=nome_marca,
            cores_codigos=cores_cods,
            cores_nomes=cores_nomes,
            unidade_medida=unid,
            tamanho=unid,
            codigo_inmetro=inmetro,
            codigo_lote=lote,
            observacoes=str(r[6] or ""),
        )

    def salvar_produto(self, p: ProdutoDTO) -> bool:
        """Insere ou atualiza um produto no banco com seus vínculos de marca e cores."""
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM USER_geoapolo_produtos WHERE prodcod = ?", [p.prodcod])
        unid = p.unidade_medida or p.tamanho or ""
        inmetro = p.codigo_inmetro or ""
        lote = p.codigo_lote or ""
        tem_tam = self._tem_coluna_tamanho

        if cur.fetchone():
            try:
                if tem_tam:
                    sql = """
                        UPDATE USER_geoapolo_produtos
                        SET prodnome = ?, descricao_alternativa = ?, grupocod = ?, tamanho = ?, observacoes = ?,
                            codigo_inmetro = ?, codigo_lote = ?, unidade_medida = ?
                        WHERE prodcod = ?
                    """
                    cur.execute(sql, [
                        p.prodnome,
                        p.descricao_alternativa,
                        p.grupocod,
                        unid,
                        p.observacoes,
                        inmetro,
                        lote,
                        unid,
                        p.prodcod,
                    ])
                else:
                    sql = """
                        UPDATE USER_geoapolo_produtos
                        SET prodnome = ?, descricao_alternativa = ?, grupocod = ?, observacoes = ?,
                            codigo_inmetro = ?, codigo_lote = ?, unidade_medida = ?
                        WHERE prodcod = ?
                    """
                    cur.execute(sql, [
                        p.prodnome,
                        p.descricao_alternativa,
                        p.grupocod,
                        p.observacoes,
                        inmetro,
                        lote,
                        unid,
                        p.prodcod,
                    ])
            except Exception:
                if tem_tam:
                    sql = """
                        UPDATE USER_geoapolo_produtos
                        SET prodnome = ?, descricao_alternativa = ?, grupocod = ?, tamanho = ?, observacoes = ?
                        WHERE prodcod = ?
                    """
                    cur.execute(sql, [
                        p.prodnome,
                        p.descricao_alternativa,
                        p.grupocod,
                        unid,
                        p.observacoes,
                        p.prodcod,
                    ])
                else:
                    sql = """
                        UPDATE USER_geoapolo_produtos
                        SET prodnome = ?, descricao_alternativa = ?, grupocod = ?, observacoes = ?
                        WHERE prodcod = ?
                    """
                    cur.execute(sql, [
                        p.prodnome,
                        p.descricao_alternativa,
                        p.grupocod,
                        p.observacoes,
                        p.prodcod,
                    ])
        else:
            try:
                if tem_tam:
                    sql = """
                        INSERT INTO USER_geoapolo_produtos (prodcod, prodnome, descricao_alternativa, grupocod, tamanho, observacoes, codigo_inmetro, codigo_lote, unidade_medida)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    cur.execute(sql, [
                        p.prodcod,
                        p.prodnome,
                        p.descricao_alternativa,
                        p.grupocod,
                        unid,
                        p.observacoes,
                        inmetro,
                        lote,
                        unid,
                    ])
                else:
                    sql = """
                        INSERT INTO USER_geoapolo_produtos (prodcod, prodnome, descricao_alternativa, grupocod, observacoes, codigo_inmetro, codigo_lote, unidade_medida)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    cur.execute(sql, [
                        p.prodcod,
                        p.prodnome,
                        p.descricao_alternativa,
                        p.grupocod,
                        p.observacoes,
                        inmetro,
                        lote,
                        unid,
                    ])
            except Exception:
                if tem_tam:
                    sql = """
                        INSERT INTO USER_geoapolo_produtos (prodcod, prodnome, descricao_alternativa, grupocod, tamanho, observacoes)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """
                    cur.execute(sql, [
                        p.prodcod,
                        p.prodnome,
                        p.descricao_alternativa,
                        p.grupocod,
                        unid,
                        p.observacoes,
                    ])
                else:
                    sql = """
                        INSERT INTO USER_geoapolo_produtos (prodcod, prodnome, descricao_alternativa, grupocod, observacoes)
                        VALUES (?, ?, ?, ?, ?)
                    """
                    cur.execute(sql, [
                        p.prodcod,
                        p.prodnome,
                        p.descricao_alternativa,
                        p.grupocod,
                        p.observacoes,
                    ])

        # Persistência do vínculo de Marca
        try:
            cur.execute("DELETE FROM USER_geoapolo_marca_produtos WHERE prodcod = ?", [p.prodcod])
            if p.codigo_marca and p.codigo_marca > 0:
                cur.execute(
                    "INSERT INTO USER_geoapolo_marca_produtos (codigo_marca, prodcod) VALUES (?, ?)",
                    [p.codigo_marca, p.prodcod]
                )
        except Exception:
            pass

        # Persistência dos vínculos de Cores
        try:
            cur.execute("DELETE FROM USER_geoapolo_produto_cor WHERE prodcod = ?", [p.prodcod])
            for c_cod in p.cores_codigos:
                if c_cod and c_cod > 0:
                    cur.execute(
                        "INSERT INTO USER_geoapolo_produto_cor (codigo_cor, prodcod) VALUES (?, ?)",
                        [c_cod, p.prodcod]
                    )
        except Exception:
            pass

        self.conn.commit()
        return True

    def excluir_produto(self, prodcod: int) -> bool:
        """Exclui um produto pelo código e seus vínculos."""
        cur = self.conn.cursor()
        try:
            cur.execute("DELETE FROM USER_geoapolo_marca_produtos WHERE prodcod = ?", [prodcod])
            cur.execute("DELETE FROM USER_geoapolo_produto_cor WHERE prodcod = ?", [prodcod])
        except Exception:
            pass
        cur.execute("DELETE FROM USER_geoapolo_produtos WHERE prodcod = ?", [prodcod])
        self.conn.commit()
        return True
