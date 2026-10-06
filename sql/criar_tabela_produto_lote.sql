-- =========================================================================
-- Tabela de Cadastro e Controle de Lotes de Produtos
-- GeoApolo V5
-- =========================================================================

IF OBJECT_ID('user_geoapolo_produto_lote', 'U') IS NULL
BEGIN
    CREATE TABLE user_geoapolo_produto_lote
    (
        ID_PRODUTO_LOTE BIGINT IDENTITY(1,1) NOT NULL,
        prodcod numeric(8,0) NOT NULL,
        NUMERO_LOTE     VARCHAR(50) NOT NULL,
        DATA_FABRICACAO DATE NULL,
        DATA_VALIDADE   DATE NULL,
        QUANTIDADE_INICIAL DECIMAL(18,6) NOT NULL DEFAULT 0,
        QUANTIDADE_ATUAL   DECIMAL(18,6) NOT NULL DEFAULT 0,
        DATA_ENTRADA DATETIME2(0) NOT NULL DEFAULT SYSDATETIME(),
        entcod_fornecedor numeric(8,0) NULL,
        STATUS CHAR(1) NOT NULL DEFAULT 'A',
        OBSERVACAO VARCHAR(500) NULL,
        DATA_CADASTRO DATETIME2(0) NOT NULL DEFAULT SYSDATETIME(),
        usucod VARCHAR(20) NULL,

        CONSTRAINT PK_PRODUTO_LOTE PRIMARY KEY (ID_PRODUTO_LOTE),
        CONSTRAINT CK_PRODUTO_LOTE_STATUS CHECK (STATUS IN ('A','I')),
        CONSTRAINT CK_PRODUTO_LOTE_QUANTIDADE CHECK (QUANTIDADE_INICIAL >= 0 AND QUANTIDADE_ATUAL >= 0)
    );

    CREATE INDEX IX_PRODUTO_LOTE_PRODCOD ON user_geoapolo_produto_lote(prodcod);
    CREATE INDEX IX_PRODUTO_LOTE_NUMERO ON user_geoapolo_produto_lote(NUMERO_LOTE);
END
GO
