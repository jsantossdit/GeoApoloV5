/* =========================================================
   STORED PROCEDURE: Atender Item de Requisição
   ========================================================= */
IF OBJECT_ID('dbo.sp_user_geoapolo_atender_req_item', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_user_geoapolo_atender_req_item;
GO

CREATE PROCEDURE [dbo].[sp_user_geoapolo_atender_req_item]
    @reqitemcod NUMERIC(8,0),
    @qtd_atender DECIMAL(18,4),
    @observacao VARCHAR(255) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @reqcod NUMERIC(8,0), @empcod NUMERIC(8,0), @prodcod NUMERIC(8,0);
    DECLARE @qtd_solicitada DECIMAL(18,4), @qtd_ja_atendida DECIMAL(18,4);
    DECLARE @novo_status_item VARCHAR(30);

    BEGIN TRY
        BEGIN TRANSACTION;

        -- 1. BUSCAR DADOS DO ITEM
        SELECT 
            @reqcod = reqcod, @empcod = empcod, @prodcod = prodcod,
            @qtd_solicitada = qtd_solicitada, @qtd_ja_atendida = qtd_atendida
        FROM [dbo].[user_geoapolo_estoque_req_itens]
        WHERE reqitemcod = @reqitemcod;

        IF @reqcod IS NULL
            RAISERROR ('Item da requisição não encontrado.', 16, 1);

        IF (@qtd_ja_atendida + @qtd_atender) > @qtd_solicitada
            RAISERROR ('A quantidade a atender ultrapassa o limite solicitado.', 16, 1);

        -- 2. ATUALIZAR STATUS DO ITEM E QUANTIDADE
        SET @novo_status_item = CASE 
            WHEN (@qtd_ja_atendida + @qtd_atender) >= @qtd_solicitada THEN 'Atendido'
            ELSE 'Atendido Parcial'
        END;

        UPDATE [dbo].[user_geoapolo_estoque_req_itens]
        SET qtd_atendida = qtd_atendida + @qtd_atender,
            status_item = @novo_status_item
        WHERE reqitemcod = @reqitemcod;

        -- 3. GERAR A MOVIMENTAÇÃO DE SAÍDA (Chamando a SP que já criamos!)
        DECLARE @obs_mov VARCHAR(255) = ISNULL(@observacao, 'Baixa de Requisição Item: ' + CAST(@reqitemcod AS VARCHAR));
        
        EXEC [dbo].[sp_user_geoapolo_registra_movimentacao]
            @empcod = @empcod,
            @prodcod = @prodcod,
            @tipo_movimento = 'S', -- Saída!
            @quantidade = @qtd_atender,
            @entcod = NULL,
            @origem_movimento = 'REQUISICAO',
            @doc_origem_cod = @reqcod, -- Amarra a saída ao código da Requisição
            @observacao = @obs_mov;

        -- 4. ATUALIZAR STATUS DO CABEÇALHO DA REQUISIÇÃO
        -- Verifica se ainda existem itens pendentes ou parciais nesta requisição
        DECLARE @itens_pendentes INT;
        SELECT @itens_pendentes = COUNT(*) 
        FROM [dbo].[user_geoapolo_estoque_req_itens] 
        WHERE reqcod = @reqcod AND status_item <> 'Atendido';

        UPDATE [dbo].[user_geoapolo_estoque_req_cab]
        SET status_requisicao = CASE 
            WHEN @itens_pendentes = 0 THEN 'Atendida'
            ELSE 'Atendida Parcial'
        END
        WHERE reqcod = @reqcod;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE();
        RAISERROR (@ErrorMessage, 16, 1);
    END CATCH
END
GO