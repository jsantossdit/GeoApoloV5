unit unt_manativoimobilizado_types;

{
  Tipos de Dados, DTOs e Estruturas para Gestão de Ativo Imobilizado e Depreciação.
  Isolado de VCL, forms e dependências visuais.
}

interface

uses
  System.SysUtils, System.Classes;

type
  TCalculoDepreciacaoDTO = record
    DataAquisicao       : TDateTime;
    ValorCompra         : Double;
    TaxaDepreciacaoAnual: Double;
    AnosEmUso           : Double;
    DepreciacaoAnual    : Double;
    DepreciacaoAcumulada: Double;
    ValorAtual          : Double;
    Valido              : Boolean;
    Mensagem            : string;
  end;

  TAtivoImobilizadoDTO = record
    NumeroDoBem                     : string;
    DescricaoDoBem                  : string;
    EmpCod                          : string;
    EmpNome                         : string;
    GeoCctrlCodEstr                 : string;
    GeoCctrlNome                    : string;
    CodigoBarrasAtivo               : string;
    NumeroDeSerie                   : string;
    CodigoCategoriaBem              : string;
    CategoriaBem                    : string;
    CodigoClassificacaoAtivo        : string;
    Classificacao                   : string;
    CodigoLocalizacao               : string;
    Localizacao                     : string;
    CodigoFuncResponsavel           : string;
    NomeFuncResponsavel             : string;
    CodigoDaMarca                   : string;
    Marca                           : string;
    CodigoStatusBem                 : string;
    DescricaoStatusBem              : string;
    DataAquisicao                   : TDateTime;
    TemDataAquisicao                : Boolean;
    ValorCompra                     : Double;
    TaxaDepreciacaoAnual            : Double;
    DataUltimaRevisao               : TDateTime;
    TemDataUltimaRevisao            : Boolean;
    CaminhoFoto                     : string;
    Observacoes                     : string;
    Depreciacao                     : TCalculoDepreciacaoDTO;
  end;

  TLookupItemDTO = record
    Codigo    : string;
    Descricao : string;
    Extra     : string;
  end;

  TOperacaoResultadoAtivo = record
    Sucesso  : Boolean;
    Mensagem : string;
    Codigo   : string;
  end;

implementation

end.
