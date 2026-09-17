unit unt_configcod_types;

{
  GeoApolo - Tipos e Contratos para Manutenção de Códigos e Sequenciais do Sistema
  Clean Architecture: Tipos desacoplados sem dependência de VCL ou DataSets.
}

interface

uses
  System.SysUtils;

type

  TDadosConfigCod = record
    GeoTabela     : string;
    ProximoCodigo : Integer;
    TabelaAtiva   : string; // 'S' ou 'N'
    EmpCod        : string;
    EmpNome       : string;
  end;

  TResultadoConfigCod = record
    Sucesso       : Boolean;
    Mensagem      : string;
    GeoTabela     : string;
    ProximoCodigo : Integer;
  end;

implementation

end.
