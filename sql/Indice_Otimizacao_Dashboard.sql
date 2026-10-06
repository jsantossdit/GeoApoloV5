-- ==============================================================================
-- SCRIPT DE OTIMIZAÇÃO DE PERFORMANCE - DASHBOARD MENU PRINCIPAL (GEOAPOLO V5)
-- Objetivo: Acelerar a execução das consultas sobre USERPerfilFinanceiro_de_Doador
-- Redução estimada de tempo: de ~1.50s para menos de 0.05s (< 50ms)
-- ==============================================================================

USE [APOLO]; -- Substitua pelo nome do banco caso diferente
GO

-- 1. Criação do índice de cobertura composto para USERPerfilFinanceiro_de_Doador
-- Abrange os filtros primários: ano_doacao, mes_doacao e categcodestr
-- Inclui todas as colunas de retorno para evitar Lookups de tabela (Index Scan -> Index Seek)

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes 
    WHERE name = 'IX_USERPerfilFinanceiro_Dashboard_Otimizado' 
      AND object_id = OBJECT_ID('USERPerfilFinanceiro_de_Doador')
)
BEGIN
    PRINT 'Criando índice IX_USERPerfilFinanceiro_Dashboard_Otimizado...';
    
    CREATE NONCLUSTERED INDEX [IX_USERPerfilFinanceiro_Dashboard_Otimizado]
    ON [dbo].[USERPerfilFinanceiro_de_Doador] (
        [ano_doacao] ASC,
        [mes_doacao] ASC
    )
    INCLUDE (
        [entcod],
        [categcodestr],
        [tipocobcod],
        [docfinespec],
        [data_doacao_mescorrente],
        [valor_doado],
        [data_doacao_anterior],
        [valor_doado_mesanterior],
        [docfinchv]
    )
    WITH (
        PAD_INDEX = OFF, 
        STATISTICS_NORECOMPUTE = OFF, 
        SORT_IN_TEMPDB = OFF, 
        DROP_EXISTING = OFF, 
        ONLINE = OFF, 
        ALLOW_ROW_LOCKS = ON, 
        ALLOW_PAGE_LOCKS = ON
    );
    
    PRINT 'Índice IX_USERPerfilFinanceiro_Dashboard_Otimizado criado com sucesso!';
END
ELSE
BEGIN
    PRINT 'O índice IX_USERPerfilFinanceiro_Dashboard_Otimizado já existe no banco.';
END
GO

-- 2. Criação do índice focado em Intervalos de Datas Recentes (Últimos 10, 15, 30 dias)
IF NOT EXISTS (
    SELECT 1 FROM sys.indexes 
    WHERE name = 'IX_USERPerfilFinanceiro_DataDoacao' 
      AND object_id = OBJECT_ID('USERPerfilFinanceiro_de_Doador')
)
BEGIN
    PRINT 'Criando índice IX_USERPerfilFinanceiro_DataDoacao...';
    
    CREATE NONCLUSTERED INDEX [IX_USERPerfilFinanceiro_DataDoacao]
    ON [dbo].[USERPerfilFinanceiro_de_Doador] (
        [data_doacao_mescorrente] DESC
    )
    INCLUDE (
        [ano_doacao],
        [mes_doacao],
        [entcod],
        [categcodestr],
        [tipocobcod],
        [docfinespec],
        [valor_doado],
        [data_doacao_anterior],
        [valor_doado_mesanterior],
        [docfinchv]
    )
    WITH (
        PAD_INDEX = OFF, 
        STATISTICS_NORECOMPUTE = OFF, 
        SORT_IN_TEMPDB = OFF, 
        DROP_EXISTING = OFF, 
        ONLINE = OFF, 
        ALLOW_ROW_LOCKS = ON, 
        ALLOW_PAGE_LOCKS = ON
    );
    
    PRINT 'Índice IX_USERPerfilFinanceiro_DataDoacao criado com sucesso!';
END
ELSE
BEGIN
    PRINT 'O índice IX_USERPerfilFinanceiro_DataDoacao já existe no banco.';
END
GO

-- 3. Atualização das Estatísticas da Tabela
PRINT 'Atualizando estatísticas de USERPerfilFinanceiro_de_Doador...';
UPDATE STATISTICS [dbo].[USERPerfilFinanceiro_de_Doador] WITH FULLSCAN;
PRINT 'Estatísticas atualizadas com sucesso!';
GO
