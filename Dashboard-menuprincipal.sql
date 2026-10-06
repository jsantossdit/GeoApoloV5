DECLARE @vdatainicial date, @vdatafinal date, @ventcod varchar(7), @ventnome varchar(200), @vcategcodestr varchar(31), @vcategnome varchar(200),
@vtipocobcod varchar(7), @vtipocobnome varchar(100), @vdatainimesanterior date, @vdatafimmesanterior date, @vstatusdoacao varchar(60), 
@vdiaentredoacoes int, @vvalidaprimeiradoacao int,
@vdatadoacaomesanterior date,
@vformacontribtitulomesanterior varchar(50), 
@vvalordoacaomesanterior numeric(14,2),
-------------------------------------------------------------
@vdatadoacaomescorrente date,
@vformacontribtitulomescorrente varchar(50), 
@vvalordoacaomescorrente numeric(14,2),
@vdiferencadata integer

DECLARE @Mes INT  -- Substitua pelo mês desejado
DECLARE @Ano INT -- Substitua pelo ano desejado^

SELECT @Mes = MONTH(getdate());
SELECT @Ano = YEAR(getdate());
-- DELETA O MOVIMENTO DO MÊS E ATUALIZA QUANDO ELA RODAR A CONSULTA
-- DELETE FROM USERPerfilFinanceiro_de_Doador WHERE mes_doacao = @Mes AND ano_doacao = @Ano
if exists(SELECT 1 FROM SYSOBJECTS WHERE NAME ='USERPerfilFinanceiro_de_Doador' and xtype = 'U')        
begin         
DELETE FROM USERPerfilFinanceiro_de_Doador WHERE mes_doacao = @Mes AND ano_doacao = @Ano
     --DROP TABLE USERPerfilFinanceiro_de_Doador
end

-- RODA A PROCEDURE DE ATUALIZAÇÃO
SET STATISTICS TIME ON;
exec USERPerfil_Financeiro_Doador  '1.01', @Ano,@Mes  
SET STATISTICS TIME OFF;

-- Primeiro dia do mês
DECLARE @PrimeiroDia DATE = DATEFROMPARTS(@Ano, @Mes, 1);
-- Último dia do mês
DECLARE @UltimoDia DATE = EOMONTH(@PrimeiroDia);
SELECT @vdatainicial = @PrimeiroDia 
SELECT @vdatafinal = @UltimoDia
--
SELECT @vdatainimesanterior = DATEADD(MONTH, -120, @vdatainicial);
SELECT @vdatafimmesanterior= DATEADD(MONTH, -1, @vdatafinal);

SELECT upfd.entcod, e.entnome, cid.ufsigla as UF, ue.USERDiocese_id as CodigoDio, ue.USERNomeDiocese as Diocese,  upfd.categcodestr, cat.categnome, 
	upfd.tipocobcod,  upfd.docfinespec as FormaContribuicao,upfd.data_doacao_mescorrente,upfd.valor_doado,
	upfd.data_doacao_anterior, upfd.valor_doado_mesanterior,upfd.docfinchv, 
	iif(dbo.fn_VerificaEntidadeUnica(upfd.entcod,'1.01') = 1,'Novo Doador',iif((datediff(day,isnull(upfd.data_doacao_anterior,upfd.data_doacao_mescorrente),upfd.data_doacao_mescorrente))>35,'Retorno Doador',iif(datediff(day,isnull(upfd.data_doacao_anterior,upfd.data_doacao_mescorrente),upfd.data_doacao_mescorrente)<=35,'Doador Recorrente',''))) as StatusDoador
	FROM USERPerfilFinanceiro_de_Doador upfd with(nolock)
INNER JOIN entidade e  ON upfd.entcod = e.entcod
INNER JOIN cidade cid  ON e.cidcod = cid.cidcod
INNER JOIN categoria cat  ON upfd.CategCodEstr = cat.CategCodEstr
LEFT JOIN U_ENTIDADE ue  ON upfd.entcod = ue.entcod 
WHERE upfd.mes_doacao = @Mes
AND     upfd.ano_doacao = @Ano
AND (
    upfd.categcodestr LIKE '02.001%' OR
    upfd.categcodestr LIKE '02.002%' OR
    upfd.categcodestr LIKE '03.001%' OR
    upfd.categcodestr LIKE '03.002%' OR
    upfd.categcodestr LIKE '03.003%' OR
    upfd.categcodestr LIKE '03.004%' OR
    upfd.categcodestr LIKE '03.005%'
)  
ORDER BY upfd.entcod, upfd.docfinespec ASC
