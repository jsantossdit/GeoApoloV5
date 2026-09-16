unit uDebxCredMemTableHelper;

interface

uses
  FireDAC.Comp.Client, Data.DB;

type
  TDebxCredMemTableHelper = class
  public
    class procedure Configurar(AMemTable: TFDMemTable);
  end;

implementation

class procedure TDebxCredMemTableHelper.Configurar(AMemTable: TFDMemTable);
begin
  if AMemTable.Active then
    AMemTable.Close;

  AMemTable.FieldDefs.Clear;

  AMemTable.FieldDefs.Add('DATA', ftDate);
  AMemTable.FieldDefs.Add('DEBITO', ftCurrency);
  AMemTable.FieldDefs.Add('CREDITO', ftCurrency);
  AMemTable.FieldDefs.Add('DIFERENCA', ftCurrency);

  AMemTable.CreateDataSet;
end;

end.
