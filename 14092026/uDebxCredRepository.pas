unit uDebxCredRepository;

interface

uses
  System.SysUtils,
  System.Generics.Collections,
  FireDAC.Comp.Client,
  uDebxCredDTO;

type
  TDebxCredRepository = class
  private
    FConnection: TFDConnection;
  public
    constructor Create(AConnection: TFDConnection);

    function Consultar(
      const ADataInicial, ADataFinal: TDate;
      const ACodConta: string
    ): TObjectList<TDebxCredDTO>;
  end;

implementation

constructor TDebxCredRepository.Create(AConnection: TFDConnection);
begin
  inherited Create;
  FConnection := AConnection;
end;

function TDebxCredRepository.Consultar(
  const ADataInicial, ADataFinal: TDate;
  const ACodConta: string
): TObjectList<TDebxCredDTO>;
var
  Qry: TFDQuery;
  Item: TDebxCredDTO;
begin
  Result := TObjectList<TDebxCredDTO>.Create(True);

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConnection;

    Qry.SQL.Clear;
    Qry.SQL.Add('SELECT');
    Qry.SQL.Add('    ContabLancData AS DataLanc,');
    Qry.SQL.Add('    SUM(CASE');
    Qry.SQL.Add('        WHEN ContabLancValor < 0 THEN ABS(ContabLancValor)');
    Qry.SQL.Add('        ELSE 0');
    Qry.SQL.Add('    END) AS Debito,');
    Qry.SQL.Add('    SUM(CASE');
    Qry.SQL.Add('        WHEN ContabLancValor > 0 THEN ContabLancValor');
    Qry.SQL.Add('        ELSE 0');
    Qry.SQL.Add('    END) AS Credito');
    Qry.SQL.Add('FROM Contab_Lancamento');
    Qry.SQL.Add('WHERE ContabLancData BETWEEN :DATAINI AND :DATAFIM');

    if Trim(ACodConta) <> '' then
    begin
      Qry.SQL.Add('AND (');
      Qry.SQL.Add('    ContabLancCtaDeb LIKE :CONTA');
      Qry.SQL.Add('    OR');
      Qry.SQL.Add('    ContabLancCtaCred LIKE :CONTA');
      Qry.SQL.Add(')');
    end;

    Qry.SQL.Add('GROUP BY ContabLancData');
    Qry.SQL.Add('ORDER BY ContabLancData');

    Qry.ParamByName('DATAINI').AsDate := ADataInicial;
    Qry.ParamByName('DATAFIM').AsDate := ADataFinal;

    if Trim(ACodConta) <> '' then
      Qry.ParamByName('CONTA').AsString := '%' + Trim(ACodConta) + '%';

    Qry.Open;

    while not Qry.Eof do
    begin
      Item := TDebxCredDTO.Create;

      Item.Data      := Qry.FieldByName('DataLanc').AsDateTime;
      Item.Debito    := Qry.FieldByName('Debito').AsCurrency;
      Item.Credito   := Qry.FieldByName('Credito').AsCurrency;
      Item.Diferenca := Item.Debito - Item.Credito;

      Result.Add(Item);

      Qry.Next;
    end;

  finally
    Qry.Free;
  end;
end;

end.
