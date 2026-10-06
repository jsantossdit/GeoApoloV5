DECLARE @Schema SYSNAME = 'dbo';
DECLARE @Tabela SYSNAME = 'user_geoapolo_produtos';

DECLARE @ObjectId INT;
DECLARE @SQL NVARCHAR(MAX) = N'';
DECLARE @Colunas NVARCHAR(MAX);
DECLARE @PK UNIQUEIDENTIFIER = NULL;

------------------------------------------------------------
-- LOCALIZA A TABELA
------------------------------------------------------------

SELECT @ObjectId = t.object_id
FROM sys.tables t
INNER JOIN sys.schemas s
    ON s.schema_id = t.schema_id
WHERE t.name = @Tabela
  AND s.name = @Schema;

IF @ObjectId IS NULL
BEGIN
    RAISERROR('Tabela não encontrada.', 16, 1);
    RETURN;
END;


------------------------------------------------------------
-- CABEÇALHO
------------------------------------------------------------

SET @SQL =
N'/* =========================================================
   SCRIPT DE CRIAÇÃO
   TABELA: ' + QUOTENAME(@Schema) + N'.' + QUOTENAME(@Tabela) + N'
   GERADO EM: ' + CONVERT(VARCHAR(19), GETDATE(), 120) + N'
   ========================================================= */

IF OBJECT_ID(N''' +
    @Schema + N'.' + @Tabela +
    N''', N''U'') IS NULL
BEGIN
';


------------------------------------------------------------
-- COLUNAS
------------------------------------------------------------

SELECT @Colunas =
STRING_AGG(
    CAST(
        N'    ' +
        QUOTENAME(c.name) + N' ' +

        CASE

            ------------------------------------------------
            -- COMPUTED
            ------------------------------------------------
            WHEN c.is_computed = 1 THEN
                N'AS ' + cc.definition

            ------------------------------------------------
            -- NORMAL
            ------------------------------------------------
            ELSE

                UPPER(t.name)

                +
                CASE

                    WHEN t.name IN
                        ('varchar','char','varbinary','binary')
                    THEN
                        N'(' +
                        CASE
                            WHEN c.max_length = -1
                                THEN N'MAX'
                            ELSE
                                CAST(c.max_length AS NVARCHAR(10))
                        END +
                        N')'

                    WHEN t.name IN ('nvarchar','nchar')
                    THEN
                        N'(' +
                        CASE
                            WHEN c.max_length = -1
                                THEN N'MAX'
                            ELSE
                                CAST(c.max_length / 2 AS NVARCHAR(10))
                        END +
                        N')'

                    WHEN t.name IN ('decimal','numeric')
                    THEN
                        N'(' +
                        CAST(c.precision AS NVARCHAR(10)) +
                        N',' +
                        CAST(c.scale AS NVARCHAR(10)) +
                        N')'

                    WHEN t.name IN
                        ('datetime2','datetimeoffset','time')
                    THEN
                        N'(' +
                        CAST(c.scale AS NVARCHAR(10)) +
                        N')'

                    ELSE N''

                END

                ------------------------------------------------
                -- COLLATION
                ------------------------------------------------
                +
                CASE
                    WHEN c.collation_name IS NOT NULL
                         AND t.name IN
                         ('varchar','char','nvarchar','nchar')
                    THEN
                        N' COLLATE ' + c.collation_name
                    ELSE N''
                END

                ------------------------------------------------
                -- IDENTITY
                ------------------------------------------------
                +
                CASE
                    WHEN c.is_identity = 1
                    THEN
                        N' IDENTITY(' +
                        CAST(ic.seed_value AS NVARCHAR(50)) +
                        N',' +
                        CAST(ic.increment_value AS NVARCHAR(50)) +
                        N')'
                    ELSE N''
                END

                ------------------------------------------------
                -- NULL
                ------------------------------------------------
                +
                CASE
                    WHEN c.is_nullable = 1
                        THEN N' NULL'
                    ELSE N' NOT NULL'
                END

        END

        --------------------------------------------------------
        -- DEFAULT
        --------------------------------------------------------
        +
        CASE
            WHEN dc.object_id IS NOT NULL
            THEN
                N' CONSTRAINT ' +
                QUOTENAME(dc.name) +
                N' DEFAULT ' +
                dc.definition
            ELSE N''
        END

    AS NVARCHAR(MAX)),
    N',' + CHAR(13) + CHAR(10)
)
WITHIN GROUP (ORDER BY c.column_id)

FROM sys.columns c

INNER JOIN sys.types t
    ON t.user_type_id = c.user_type_id

LEFT JOIN sys.identity_columns ic
    ON ic.object_id = c.object_id
    AND ic.column_id = c.column_id

LEFT JOIN sys.default_constraints dc
    ON dc.parent_object_id = c.object_id
    AND dc.parent_column_id = c.column_id

LEFT JOIN sys.computed_columns cc
    ON cc.object_id = c.object_id
    AND cc.column_id = c.column_id

WHERE c.object_id = @ObjectId;


------------------------------------------------------------
-- CREATE TABLE
------------------------------------------------------------

SET @SQL =
    @SQL +
    @Colunas +
    CHAR(13) + CHAR(10) +
    N');' +
    CHAR(13) + CHAR(10) +
    N'END' +
    CHAR(13) + CHAR(10) +
    N'GO' +
    CHAR(13) + CHAR(10);


------------------------------------------------------------
-- PRIMARY KEY
------------------------------------------------------------

DECLARE @PKSQL NVARCHAR(MAX);

SELECT @PKSQL =
(
    SELECT TOP 1

        N'/* PRIMARY KEY */' +
        CHAR(13) + CHAR(10) +

        N'ALTER TABLE ' +
        QUOTENAME(@Schema) + N'.' +
        QUOTENAME(@Tabela) +
        N' ADD CONSTRAINT ' +
        QUOTENAME(i.name) +
        N' PRIMARY KEY ' +

        CASE
            WHEN i.type = 1
                THEN N'CLUSTERED '
            ELSE N'NONCLUSTERED '
        END +

        N'(' +

        STUFF(
            (
                SELECT
                    N', ' + QUOTENAME(c.name)

                FROM sys.index_columns ic

                INNER JOIN sys.columns c
                    ON c.object_id = ic.object_id
                    AND c.column_id = ic.column_id

                WHERE ic.object_id = i.object_id
                  AND ic.index_id = i.index_id
                  AND ic.key_ordinal > 0

                ORDER BY ic.key_ordinal

                FOR XML PATH(''), TYPE
            ).value('.', 'NVARCHAR(MAX)'),
            1, 2, N''
        )

        + N');' +
        CHAR(13) + CHAR(10) +
        N'GO' +
        CHAR(13) + CHAR(10)

    FROM sys.indexes i

    WHERE i.object_id = @ObjectId
      AND i.is_primary_key = 1
);


IF @PKSQL IS NOT NULL
    SET @SQL = @SQL + @PKSQL;


------------------------------------------------------------
-- UNIQUE CONSTRAINTS
------------------------------------------------------------

SELECT @SQL = @SQL +

    N'/* UNIQUE */' +
    CHAR(13) + CHAR(10) +

    N'ALTER TABLE ' +
    QUOTENAME(@Schema) + N'.' +
    QUOTENAME(@Tabela) +
    N' ADD CONSTRAINT ' +
    QUOTENAME(i.name) +
    N' UNIQUE ' +

    CASE
        WHEN i.type = 1
            THEN N'CLUSTERED '
        ELSE N'NONCLUSTERED '
    END +

    N'(' +

    STUFF(
        (
            SELECT
                N', ' + QUOTENAME(c.name)

            FROM sys.index_columns ic

            INNER JOIN sys.columns c
                ON c.object_id = ic.object_id
                AND c.column_id = ic.column_id

            WHERE ic.object_id = i.object_id
              AND ic.index_id = i.index_id
              AND ic.key_ordinal > 0

            ORDER BY ic.key_ordinal

            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'),
        1, 2, N''
    )

    + N');' +
    CHAR(13) + CHAR(10) +
    N'GO' +
    CHAR(13) + CHAR(10)

FROM sys.indexes i

WHERE i.object_id = @ObjectId
  AND i.is_unique_constraint = 1;


------------------------------------------------------------
-- CHECK CONSTRAINTS
------------------------------------------------------------

SELECT @SQL = @SQL +

    N'/* CHECK */' +
    CHAR(13) + CHAR(10) +

    N'ALTER TABLE ' +
    QUOTENAME(@Schema) + N'.' +
    QUOTENAME(@Tabela) +
    N' ADD CONSTRAINT ' +
    QUOTENAME(cc.name) +
    N' CHECK ' +
    cc.definition +
    N';' +
    CHAR(13) + CHAR(10) +
    N'GO' +
    CHAR(13) + CHAR(10)

FROM sys.check_constraints cc

WHERE cc.parent_object_id = @ObjectId;


------------------------------------------------------------
-- ÍNDICES
------------------------------------------------------------

SELECT @SQL = @SQL +

    N'/* INDEX */' +
    CHAR(13) + CHAR(10) +

    N'CREATE ' +

    CASE
        WHEN i.is_unique = 1
            THEN N'UNIQUE '
        ELSE N''
    END +

    CASE
        WHEN i.type = 1
            THEN N'CLUSTERED '
        WHEN i.type = 2
            THEN N'NONCLUSTERED '
        ELSE N''
    END +

    N'INDEX ' +
    QUOTENAME(i.name) +
    N' ON ' +
    QUOTENAME(@Schema) + N'.' +
    QUOTENAME(@Tabela) +
    N' (' +

    STUFF(
        (
            SELECT
                N', ' +
                QUOTENAME(c.name) +

                CASE
                    WHEN ic.is_descending_key = 1
                        THEN N' DESC'
                    ELSE N' ASC'
                END

            FROM sys.index_columns ic

            INNER JOIN sys.columns c
                ON c.object_id = ic.object_id
                AND c.column_id = ic.column_id

            WHERE ic.object_id = i.object_id
              AND ic.index_id = i.index_id
              AND ic.key_ordinal > 0

            ORDER BY ic.key_ordinal

            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'),
        1, 2, N''
    )

    + N');' +
    CHAR(13) + CHAR(10) +
    N'GO' +
    CHAR(13) + CHAR(10)

FROM sys.indexes i

WHERE i.object_id = @ObjectId

  AND i.index_id > 0

  AND i.is_primary_key = 0

  AND i.is_unique_constraint = 0

  AND i.type IN (1,2);


------------------------------------------------------------
-- FOREIGN KEYS
------------------------------------------------------------

SELECT @SQL = @SQL +

    N'/* FOREIGN KEY */' +
    CHAR(13) + CHAR(10) +

    N'ALTER TABLE ' +
    QUOTENAME(@Schema) + N'.' +
    QUOTENAME(@Tabela) +

    N' ADD CONSTRAINT ' +
    QUOTENAME(fk.name) +

    N' FOREIGN KEY (' +

    STUFF(
        (
            SELECT
                N', ' + QUOTENAME(c.name)

            FROM sys.foreign_key_columns fkc

            INNER JOIN sys.columns c
                ON c.object_id = fkc.parent_object_id
                AND c.column_id = fkc.parent_column_id

            WHERE fkc.constraint_object_id = fk.object_id

            ORDER BY fkc.constraint_column_id

            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'),
        1, 2, N''
    )

    + N') REFERENCES ' +

    QUOTENAME(OBJECT_SCHEMA_NAME(fk.referenced_object_id)) +
    N'.' +
    QUOTENAME(OBJECT_NAME(fk.referenced_object_id)) +

    N' (' +

    STUFF(
        (
            SELECT
                N', ' + QUOTENAME(c.name)

            FROM sys.foreign_key_columns fkc

            INNER JOIN sys.columns c
                ON c.object_id = fkc.referenced_object_id
                AND c.column_id = fkc.referenced_column_id

            WHERE fkc.constraint_object_id = fk.object_id

            ORDER BY fkc.constraint_column_id

            FOR XML PATH(''), TYPE
        ).value('.', 'NVARCHAR(MAX)'),
        1, 2, N''
    )

    + N')' +

    CASE
        WHEN fk.delete_referential_action_desc <> 'NO_ACTION'
        THEN
            N' ON DELETE ' +
            REPLACE(
                fk.delete_referential_action_desc,
                N'_',
                N' '
            )
        ELSE N''
    END +

    CASE
        WHEN fk.update_referential_action_desc <> 'NO_ACTION'
        THEN
            N' ON UPDATE ' +
            REPLACE(
                fk.update_referential_action_desc,
                N'_',
                N' '
            )
        ELSE N''
    END +

    N';' +
    CHAR(13) + CHAR(10) +
    N'GO' +
    CHAR(13) + CHAR(10)

FROM sys.foreign_keys fk

WHERE fk.parent_object_id = @ObjectId;


------------------------------------------------------------
-- RESULTADO
------------------------------------------------------------

SELECT @SQL AS ScriptCriacao;