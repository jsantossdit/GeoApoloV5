/* =========================================================================
   GEOAPOLO V5 / GEOALVO - MÓDULO FINANCEIRO
   SCRIPT DE CRIAÇÃO: TABELA DE CONTAS A PAGAR / DOCUMENTOS FINANCEIROS
   ARQUIVO: sql/criar_tabela_contas_a_pagar.sql
   ========================================================================= */

USE [banco_apolo]; -- Ajuste para o nome do seu banco de dados se necessário
GO

SET ANSI_NULLS ON;
GO
SET QUOTED_IDENTIFIER ON;
GO

IF OBJECT_ID(N'dbo.USER_geoapolo_contas_a_pagar', N'U') IS NULL
BEGIN
    PRINT 'Iniciando criação da tabela dbo.USER_geoapolo_contas_a_pagar...';

    CREATE TABLE dbo.USER_geoapolo_contas_a_pagar (
        codigo_documento          INT IDENTITY(1,1) NOT NULL,
        codigo_empresa            VARCHAR(10) NOT NULL CONSTRAINT DF_ctaspagar_emp DEFAULT ('1.01'),
        numero_documento          VARCHAR(40) NOT NULL,
        serie_documento           VARCHAR(10) NULL CONSTRAINT DF_ctaspagar_serie DEFAULT ('1'),
        parcela                   INT NOT NULL CONSTRAINT DF_ctaspagar_parc DEFAULT (1),
        total_parcelas            INT NOT NULL CONSTRAINT DF_ctaspagar_totparc DEFAULT (1),
        entcod                    VARCHAR(20) NULL,
        fornecedor_nome           VARCHAR(200) NOT NULL,
        cnpj_cpf                  VARCHAR(20) NULL,
        data_emissao              DATE NOT NULL CONSTRAINT DF_ctaspagar_dtemis DEFAULT (CONVERT(DATE, GETDATE())),
        data_vencimento           DATE NOT NULL,
        data_pagamento            DATE NULL,
        valor_original            NUMERIC(15,2) NOT NULL,
        valor_desconto            NUMERIC(15,2) NOT NULL CONSTRAINT DF_ctaspagar_desc DEFAULT (0.00),
        valor_juros_multa         NUMERIC(15,2) NOT NULL CONSTRAINT DF_ctaspagar_jur DEFAULT (0.00),
        valor_pago                NUMERIC(15,2) NOT NULL CONSTRAINT DF_ctaspagar_pago DEFAULT (0.00),
        saldo_aberto              NUMERIC(15,2) NOT NULL,
        situacao                  VARCHAR(20) NOT NULL CONSTRAINT DF_ctaspagar_sit DEFAULT ('ABERTO'), -- ABERTO, QUITADO, CANCELADO
        tipo_documento            VARCHAR(30) NOT NULL CONSTRAINT DF_ctaspagar_tipo DEFAULT ('ENTRADA_ESTOQUE'),
        origem                    VARCHAR(50) NOT NULL CONSTRAINT DF_ctaspagar_origem DEFAULT ('COMPRA_ESTOQUE'),
        centro_custo              VARCHAR(50) NULL,
        codigo_movimento_estoque  INT NULL,
        observacoes               VARCHAR(500) NULL,
        data_inclusao             DATETIME NOT NULL CONSTRAINT DF_ctaspagar_dtinc DEFAULT (GETDATE()),
        usuario_inclusao          VARCHAR(50) NULL,

        CONSTRAINT PK_USER_geoapolo_contas_a_pagar PRIMARY KEY CLUSTERED (codigo_documento ASC)
    );

    -- Índices para otimização de consultas e relatórios
    CREATE NONCLUSTERED INDEX IX_ctaspagar_emp_venc_sit 
        ON dbo.USER_geoapolo_contas_a_pagar (codigo_empresa, data_vencimento, situacao);

    CREATE NONCLUSTERED INDEX IX_ctaspagar_fornecedor 
        ON dbo.USER_geoapolo_contas_a_pagar (entcod, fornecedor_nome);

    CREATE NONCLUSTERED INDEX IX_ctaspagar_movestq 
        ON dbo.USER_geoapolo_contas_a_pagar (codigo_movimento_estoque);

    PRINT 'Tabela dbo.USER_geoapolo_contas_a_pagar criada com sucesso!';
END
ELSE
BEGIN
    PRINT 'A tabela dbo.USER_geoapolo_contas_a_pagar já existe no banco de dados.';
END
GO
