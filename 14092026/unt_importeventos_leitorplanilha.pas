unit unt_importeventos_leitorplanilha;

interface

uses
  System.SysUtils, System.Variants, Winapi.ActiveX, System.Win.ComObj,
  unt_importeventos_model;

type
  /// <summary>Contrato para leitura de uma planilha de importação. Permite trocar a
  /// implementação (OLE, ODBC, biblioteca de terceiros) sem alterar o Controller,
  /// e permite criar um mock/fake em teste unitário.</summary>
  IImportadorPlanilha = interface
    ['{5A8B6E1E-6B0E-4B7B-9B7C-2B7B8E7F2C31}']
    function Carregar(const AArquivo: string): TPlanilhaImportada;
  end;

  /// <summary>Implementação via automação OLE do Excel (mesma técnica do código
  /// legado, encapsulada). Lê a 1a linha como cabeçalho e monta uma
  /// TPlanilhaImportada com acesso por nome de coluna.</summary>
  TImportadorPlanilhaExcelOLE = class(TInterfacedObject, IImportadorPlanilha)
  public
    function Carregar(const AArquivo: string): TPlanilhaImportada;
  end;

implementation

const
  xlCellTypeLastCell = $0000000B;

function TImportadorPlanilhaExcelOLE.Carregar(const AArquivo: string): TPlanilhaImportada;
var
  vExcel, vPlanilha: OleVariant;
  vMatriz: Variant;
  vUltimaLinha, vUltimaColuna, vLinha, vColuna: Integer;
  vCabecalhos: TArray<string>;
  vLinhaObj: TLinhaPlanilha;
begin
  if not FileExists(AArquivo) then
    raise Exception.CreateFmt('Arquivo não encontrado: %s', [AArquivo]);

  Result := TPlanilhaImportada.Create;
  try
    vExcel := CreateOleObject('Excel.Application');
    try
      vExcel.Visible := False;
      vExcel.DisplayAlerts := False;
      vExcel.Workbooks.Open(AArquivo);
      vPlanilha := vExcel.Workbooks[ExtractFileName(AArquivo)].WorkSheets[1];
      vPlanilha.Activate;

      vPlanilha.Cells.SpecialCells(xlCellTypeLastCell, EmptyParam).Activate;
      vUltimaLinha := vExcel.ActiveCell.Row;
      vUltimaColuna := vExcel.ActiveCell.Column;

      if vUltimaLinha < 2 then
        Exit; // só cabeçalho ou planilha vazia

      vMatriz := vPlanilha.Range['A1', vPlanilha.Cells.Item[vUltimaLinha, vUltimaColuna]].Value;

      SetLength(vCabecalhos, vUltimaColuna);
      for vColuna := 1 to vUltimaColuna do
        vCabecalhos[vColuna - 1] := Trim(VarToStr(vMatriz[1, vColuna]));

      for vLinha := 2 to vUltimaLinha do
      begin
        vLinhaObj := TLinhaPlanilha.Create;
        for vColuna := 1 to vUltimaColuna do
          if vCabecalhos[vColuna - 1] <> '' then
            vLinhaObj.DefinirValor(vCabecalhos[vColuna - 1], VarToStr(vMatriz[vLinha, vColuna]));
        Result.Linhas.Add(vLinhaObj);
      end;
    finally
      if not VarIsEmpty(vExcel) then
      begin
        vExcel.Quit;
        vExcel := Unassigned;
        vPlanilha := Unassigned;
      end;
    end;
  except
    Result.Free;
    raise;
  end;
end;

end.
