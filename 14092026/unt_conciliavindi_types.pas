unit unt_conciliavindi_types;

{
  GeoApolo - Tipos e Contratos para Conciliação Financeira Vindi
  Clean Architecture: Tipos desacoplados sem dependência de VCL ou DataSets.
}

interface

uses
  System.SysUtils;

type

  TDadosTransacaoVindi = record
    PedidoId        : string;
    DataTransacao   : TDateTime;
    Valor           : Double;
    Status          : string;
    MetodoPagamento : string;
    ClienteNome     : string;
    ClienteCpfCnpj  : string;
    EntidadeIdVindi : string;
    EntCodApolo     : string;
  end;

  TIntegridadeVindiResult = record
    PedidoId : string;
    Erros    : TArray<string>;
    function TemErros: Boolean;
  end;

  TResultadoConciliacao = record
    Sucesso       : Boolean;
    Mensagem      : string;
    TotalAfetados : Integer;
  end;

implementation

{ TIntegridadeVindiResult }

function TIntegridadeVindiResult.TemErros: Boolean;
begin
  Result := Length(Erros) > 0;
end;

end.
