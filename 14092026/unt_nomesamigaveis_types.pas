unit unt_nomesamigaveis_types;

{
  GeoApolo - Tipos e Contratos para Nomes Amigáveis de Objetos e Controles
  Clean Architecture: Tipos desacoplados sem dependência de VCL ou DataSets.
}

interface

uses
  System.SysUtils;

type

  TDadosObjetoAmigavel = record
    NomeObjeto   : string;
    NomeAmigavel : string;
    Categoria    : string;
  end;

  TResultadoNomesAmigaveis = record
    Sucesso       : Boolean;
    Mensagem      : string;
    TotalAfetados : Integer;
  end;

implementation

end.
