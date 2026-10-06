-- ========================================================================
-- Script DDL: Criação das Tabelas de Almoxarifados e Vínculo com Produtos
-- GeoApolo V5 / Apolo ERP
-- ========================================================================

-- 1. Tabela de Almoxarifados
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[user_geoapolo_almoxarifados]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[user_geoapolo_almoxarifados] (
        [codigo_almoxarifado] VARCHAR(20) NOT NULL,
        [descricao]           VARCHAR(100) NOT NULL,
        [centro_custo]        VARCHAR(30) NULL,
        [data_criacao]        DATETIME2(0) NOT NULL DEFAULT SYSDATETIME(),
        [finalidade]          VARCHAR(500) NULL,
        [status]              CHAR(1) NOT NULL DEFAULT 'A',
        
        CONSTRAINT [PK_user_geoapolo_almoxarifados] PRIMARY KEY CLUSTERED ([codigo_almoxarifado] ASC),
        CONSTRAINT [CK_user_geoapolo_almoxarifados_status] CHECK ([status] IN ('A', 'I'))
    );

    PRINT 'Tabela user_geoapolo_almoxarifados criada com sucesso.';
END
GO

-- 2. Tabela de Vínculo de Produtos com Almoxarifados (Multi-Almoxarifado & Saldos por Data)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[user_geoapolo_produtos_almoxarifados]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[user_geoapolo_produtos_almoxarifados] (
        [id_produto_almoxarifado]  BIGINT IDENTITY(1,1) NOT NULL,
        [codigo_almoxarifado]      VARCHAR(20) NOT NULL,
        [prodcod]                  NUMERIC(8,0) NOT NULL,
        [saldo_atual]              DECIMAL(18,6) NOT NULL DEFAULT 0,
        [data_ultima_movimentacao] DATETIME2(0) NULL,
        [data_vinculo]             DATETIME2(0) NOT NULL DEFAULT SYSDATETIME(),
        [status]                   CHAR(1) NOT NULL DEFAULT 'A',
        
        CONSTRAINT [PK_user_geoapolo_prod_almox] PRIMARY KEY CLUSTERED ([id_produto_almoxarifado] ASC),
        CONSTRAINT [UQ_user_geoapolo_prod_almox] UNIQUE NONCLUSTERED ([codigo_almoxarifado], [prodcod]),
        CONSTRAINT [CK_user_geoapolo_prod_almox_status] CHECK ([status] IN ('A', 'I'))
    );

    CREATE NONCLUSTERED INDEX [IX_prod_almox_prodcod] ON [dbo].[user_geoapolo_produtos_almoxarifados] ([prodcod]);
    CREATE NONCLUSTERED INDEX [IX_prod_almox_almox] ON [dbo].[user_geoapolo_produtos_almoxarifados] ([codigo_almoxarifado]);

    PRINT 'Tabela user_geoapolo_produtos_almoxarifados criada com sucesso.';
END
GO

-- 3. Almoxarifado Geral Padrão (Carga Inicial caso a tabela esteja vazia)
IF NOT EXISTS (SELECT 1 FROM [dbo].[user_geoapolo_almoxarifados] WHERE [codigo_almoxarifado] = '01')
BEGIN
    INSERT INTO [dbo].[user_geoapolo_almoxarifados] 
        ([codigo_almoxarifado], [descricao], [centro_custo], [data_criacao], [finalidade], [status])
    VALUES 
        ('01', 'ALMOXARIFADO CENTRAL / GERAL', '1.01', SYSDATETIME(), 'Almoxarifado principal para armazenamento e controle geral de mercadorias e insumos.', 'A');

    PRINT 'Almoxarifado Central (01) inserido como inicial.';
END
GO
