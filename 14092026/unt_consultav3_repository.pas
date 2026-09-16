unit unt_consultav3_repository;

interface

uses
  System.SysUtils, System.Classes, Data.DB, FireDAC.Comp.Client,
  FireDAC.Stan.Param, FireDAC.Stan.Option, unt_consultav3_types;

type
  IConsultaRepository = interface
    ['{8E1A3402-2B47-4C0A-A2E4-E5BD3C11D923}']
    function ExecutarConsulta(const ASql: string; const AParamValor: string; ATargetQuery: TFDQuery): Boolean;
    function ObterParametroEmpresa(const AEmpCod, ACampo: string): string;
  end;

  TConsultaRepository = class(TInterfacedObject, IConsultaRepository)
  private
    FConn: TFDConnection;
  public
    constructor Create(AConnection: TFDConnection);
    function ExecutarConsulta(const ASql: string; const AParamValor: string; ATargetQuery: TFDQuery): Boolean;
    function ObterParametroEmpresa(const AEmpCod, ACampo: string): string;
  end;

implementation

constructor TConsultaRepository.Create(AConnection: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConnection) then
    raise Exception.Create('TConsultaRepository: TFDConnection é obrigatória.');
  FConn := AConnection;
end;

function TConsultaRepository.ExecutarConsulta(
  const ASql: string; const AParamValor: string; ATargetQuery: TFDQuery
): Boolean;
begin
  ATargetQuery.Close;
  ATargetQuery.Connection := FConn;
  ATargetQuery.FetchOptions.Mode := fmOnDemand;
  ATargetQuery.FetchOptions.RowsetSize := 50;
  ATargetQuery.FetchOptions.RecsMax := -1;

  // TODO: [SQLAlchemy Migration]
  // session.execute(text(sql).with_hint(Table, 'WITH (NOLOCK)', 'mssql'), {"termo": f"%{valor}%"})
  ATargetQuery.SQL.Text := ASql;
  if ATargetQuery.Params.FindParam('termo') <> nil then
    ATargetQuery.ParamByName('termo').AsString := '%' + AParamValor + '%';

  ATargetQuery.Open;
  Result := ATargetQuery.Active;
end;

function TConsultaRepository.ObterParametroEmpresa(const AEmpCod, ACampo: string): string;
var
  Qry: TFDQuery;
begin
  Result := '';
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    // Sanitiza nome de campo
    Qry.SQL.Text := Format('SELECT %s FROM USER_geoapolo_configuracoes WITH (NOLOCK) WHERE empcod = :empcod', [ACampo]);
    Qry.ParamByName('empcod').AsString := AEmpCod;
    Qry.Open;
    if not Qry.IsEmpty then
      Result := Qry.Fields[0].AsString;
  finally
    Qry.Free;
  end;
end;

end.
