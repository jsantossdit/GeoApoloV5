-- ============================================================================
-- SCRIPT DE CRIAÇÃO E ADEQUAÇÃO DE TABELAS DO MÓDULO DE PRODUTOS E ESTOQUE
-- GeoApolo V5 / GeoAlvo
-- Banco de Dados: Microsoft SQL Server
-- ============================================================================

-- 1. TABELA ASSOCIATIVA PRODUTO X MARCA (USER_geoapolo_marca_produtos)
IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USER_geoapolo_marca_produtos' AND xtype = 'U')
BEGIN
    PRINT 'Criando tabela USER_geoapolo_marca_produtos...';
    CREATE TABLE USER_geoapolo_marca_produtos (
        codigo_marca NUMERIC(10, 0) NOT NULL,
        prodcod NUMERIC(10, 0) NOT NULL,
        CONSTRAINT pk_marcaprod PRIMARY KEY (codigo_marca, prodcod)
    );
    CREATE INDEX idx_marcaprod_prodcod ON USER_geoapolo_marca_produtos (prodcod);
    PRINT 'Tabela USER_geoapolo_marca_produtos criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela USER_geoapolo_marca_produtos já existe.';
END
GO

-- 2. TABELA ASSOCIATIVA PRODUTO X COR (USER_geoapolo_produto_cor)
IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USER_geoapolo_produto_cor' AND xtype = 'U')
BEGIN
    PRINT 'Criando tabela USER_geoapolo_produto_cor...';
    CREATE TABLE USER_geoapolo_produto_cor (
        codigo_cor NUMERIC(10, 0) NOT NULL,
        prodcod NUMERIC(10, 0) NOT NULL,
        CONSTRAINT pk_codprodcor PRIMARY KEY (codigo_cor, prodcod)
    );
    CREATE INDEX idx_codprodcor_prodcod ON USER_geoapolo_produto_cor (prodcod);
    PRINT 'Tabela USER_geoapolo_produto_cor criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela USER_geoapolo_produto_cor já existe.';
END
GO

-- 3. TABELA DE FOTOS DE PRODUTOS (USER_geoapolo_produto_foto)
IF NOT EXISTS (SELECT 1 FROM sysobjects WHERE name = 'USER_geoapolo_produto_foto' AND xtype = 'U')
BEGIN
    PRINT 'Criando tabela USER_geoapolo_produto_foto...';
    CREATE TABLE USER_geoapolo_produto_foto (
        prodcod NUMERIC(10, 0) NOT NULL,
        foto_produto VARBINARY(MAX) NULL,
        CONSTRAINT pk_fotocodigoproduto PRIMARY KEY (prodcod)
    );
    PRINT 'Tabela USER_geoapolo_produto_foto criada com sucesso.';
END
ELSE
BEGIN
    PRINT 'Tabela USER_geoapolo_produto_foto já existe.';
END
GO

-- 4. GARANTIR COLUNAS COMPLEMENTARES EM USER_geoapolo_produtos
IF OBJECT_ID('USER_geoapolo_produtos', 'U') IS NOT NULL
BEGIN
    IF NOT EXISTS (SELECT 1 FROM syscolumns WHERE id = OBJECT_ID('USER_geoapolo_produtos') AND name = 'codigo_inmetro')
    BEGIN
        ALTER TABLE USER_geoapolo_produtos ADD codigo_inmetro VARCHAR(50) NULL;
        PRINT 'Coluna codigo_inmetro adicionada em USER_geoapolo_produtos.';
    END

    IF NOT EXISTS (SELECT 1 FROM syscolumns WHERE id = OBJECT_ID('USER_geoapolo_produtos') AND name = 'codigo_lote')
    BEGIN
        ALTER TABLE USER_geoapolo_produtos ADD codigo_lote VARCHAR(50) NULL;
        PRINT 'Coluna codigo_lote adicionada em USER_geoapolo_produtos.';
    END

    IF NOT EXISTS (SELECT 1 FROM syscolumns WHERE id = OBJECT_ID('USER_geoapolo_produtos') AND name = 'unidade_medida')
    BEGIN
        ALTER TABLE USER_geoapolo_produtos ADD unidade_medida VARCHAR(20) NULL;
        PRINT 'Coluna unidade_medida adicionada em USER_geoapolo_produtos.';
    END
END
GO
