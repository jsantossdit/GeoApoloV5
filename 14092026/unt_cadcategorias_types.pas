unit unt_cadcategorias_types;

{
  GeoApolo - Tipos e Contratos para Cadastro de Categorias de Entidades e Vínculos
  Clean Architecture: Tipos desacoplados sem dependência de VCL ou DataSets.
}

interface

uses
  System.SysUtils;

type

  TDadosCadCategoria = record
    CodigoEstrutural  : string;
    Nome              : string;
    CodigoAlternativo : string;
    IsGrupo           : Boolean;
  end;

  TVinculoUsuarioCategoria = record
    CodigoCategoria : string;
    Usucod          : string;
    Login           : string;
    Nome            : string;
  end;

  TResultadoCadCategoria = record
    Sucesso       : Boolean;
    Mensagem      : string;
    IdGerado      : string;
    TotalAfetados : Integer;
  end;

implementation

end.
