unit unt_repositorio_licenca;

{
  GeoApolo - TRepositorioLicencaDB
  Implementa IRepositorioLicenca via FireDAC.
}

interface

uses
  SysUtils,
  FireDAC.Comp.Client,
  unt_logon_interfaces;

type

  TRepositorioLicencaDB = class(TInterfacedObject, IRepositorioLicenca)
  private
    FConexao: TFDConnection;
    function CriarQuery: TFDQuery;
  public
    constructor Create(AConexao: TFDConnection);

    { IRepositorioLicenca }
    function BuscarLicencaMesAtual(AMes, AAno: Integer;
      out ALicenca: TDadosLicenca): Boolean;
    function BloquearLicenca(const AIDPalavra: string): Boolean;
  end;

implementation

uses
  DateUtils;

{ TRepositorioLicencaDB }

constructor TRepositorioLicencaDB.Create(AConexao: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConexao) then
    raise EArgumentNilException.Create('TRepositorioLicencaDB: conexao nao pode ser nil');
  FConexao := AConexao;
end;

function TRepositorioLicencaDB.CriarQuery: TFDQuery;
begin
  Result := TFDQuery.Create(nil);
  Result.Connection := FConexao;
end;

function TRepositorioLicencaDB.BuscarLicencaMesAtual(AMes, AAno: Integer;
  out ALicenca: TDadosLicenca): Boolean;
var
  Q: TFDQuery;
begin
  Result  := False;
  ALicenca := Default(TDadosLicenca);

  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT id_palavra, flag_bloqueia, tempo_bloqueio_dias, ' +
      '       flag_ativar, data_final ' +
      'FROM user_geoapolo_dicionario ' +
      'WHERE MONTH(data_inicial) = :mes AND YEAR(data_inicial) = :ano';
    Q.ParamByName('mes').AsString := IntToStr(AMes);
    Q.ParamByName('ano').AsString := IntToStr(AAno);
    Q.Open;

    if not Q.IsEmpty then
    begin
      ALicenca.IDPalavra      := Q.FieldByName('id_palavra').AsString;
      ALicenca.Bloqueia       := Q.FieldByName('flag_bloqueia').AsString = 'S';
      ALicenca.DiasTolerancia := Q.FieldByName('tempo_bloqueio_dias').AsInteger;
      ALicenca.FlagAtivo      := Q.FieldByName('flag_ativar').AsString = 'S';
      ALicenca.DataFinal      := Q.FieldByName('data_final').AsDateTime;
      ALicenca.MesReferencia  := AMes;
      ALicenca.AnoReferencia  := AAno;
      Result := True;
    end;
  finally
    Q.Free;
  end;
end;

function TRepositorioLicencaDB.BloquearLicenca(const AIDPalavra: string): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;

  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'UPDATE user_geoapolo_dicionario SET flag_bloqueia = ' + QuotedStr('S') +
      ' WHERE id_palavra = :id_palavra';
    Q.ParamByName('id_palavra').AsString := AIDPalavra;
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

end.
