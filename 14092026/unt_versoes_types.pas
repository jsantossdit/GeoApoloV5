unit unt_versoes_types;

{
  GeoApolo - Tipos e Contratos para Manutenção de Novas Versões
  Clean Architecture: Tipos desacoplados sem dependência de VCL ou DataSets.
}

interface

uses
  System.SysUtils;

type

  TDadosVersao = record
    IDVersao         : string;
    DataLancamento   : string;
    TextoNovaVersao  : string;
    StatusVersao     : string; // 'S' = Liberada, 'N' = Não Liberada
  end;

  TResultadoVersao = record
    Sucesso   : Boolean;
    Mensagem  : string;
    IDVersao  : string;
  end;

implementation

end.
