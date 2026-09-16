unit ConsultaRepository;

interface

uses
  System.SysUtils,
  FireDAC.Comp.Client,
  ConsultaModel;

type
  TConsultaRepository = class
  private
    FConnection: TFDConnection;
    function TipoConsultaToDB(ATipo: TTipoConsulta): string;
    function DBToTipoConsulta(AValue: string): TTipoConsulta;
  public
    constructor Create(AConnection: TFDConnection);

    function BuscarPorCodigo(ACodigo: Integer): TConsultaModel;
    procedure Inserir(AConsulta: TConsultaModel);
    procedure Atualizar(AConsulta: TConsultaModel);
    procedure Excluir(ACodigo: Integer);
  end;

implementation

constructor TConsultaRepository.Create(AConnection: TFDConnection);
begin
  FConnection := AConnection;
end;

function TConsultaRepository.TipoConsultaToDB(ATipo: TTipoConsulta): string;
begin
  case ATipo of
    tcImediata: Result := 'I';
    tcCampanha: Result := 'I';
    //tcMix: Result := 'M';
  else
    Result := 'I';
  end;
end;

function TConsultaRepository.DBToTipoConsulta(AValue: string): TTipoConsulta;
begin
  if AValue = 'I' then
    Result := tcImediata
  else if AValue = 'C' then
    Result := tcCampanha
  else
    Result := tcMix;
end;

function TConsultaRepository.BuscarPorCodigo(ACodigo: Integer): TConsultaModel;
var
  Qry: TFDQuery;
begin
  Result := nil;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConnection;
    Qry.SQL.Text :=
      'SELECT codigo_consulta, descricao_consulta, sentenca_sql, tipo_consulta, banco_consulta ' +
      'FROM USER_geoapolo_consultas ' +
      'WHERE codigo_consulta = :codigo';

    Qry.ParamByName('codigo').AsInteger := ACodigo;
    Qry.Open;

    if not Qry.IsEmpty then
    begin
      Result := TConsultaModel.Create;
      Result.Codigo := Qry.FieldByName('codigo_consulta').AsInteger;
      Result.Descricao := Qry.FieldByName('descricao_consulta').AsString;
      Result.SentencaSQL := Qry.FieldByName('sentenca_sql').AsString;
      Result.TipoConsulta := DBToTipoConsulta(Qry.FieldByName('tipo_consulta').AsString);
      Result.BancoConsulta := Qry.FieldByName('banco_consulta').AsString;
    end;
  finally
    Qry.Free;
  end;
end;

procedure TConsultaRepository.Inserir(AConsulta: TConsultaModel);
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConnection;
    Qry.SQL.Text :=
      'INSERT INTO USER_geoapolo_consultas ' +
      '(codigo_consulta, descricao_consulta, sentenca_sql, tipo_consulta, banco_consulta) ' +
      'VALUES (:codigo, :descricao, :sql, :tipo, :banco)';

    Qry.ParamByName('codigo').AsInteger := AConsulta.Codigo;
    Qry.ParamByName('descricao').AsString := AConsulta.Descricao;
    Qry.ParamByName('sql').AsString := AConsulta.SentencaSQL;

    Qry.ParamByName('tipo').AsString := TipoConsultaToDB(AConsulta.TipoConsulta);
    Qry.ParamByName('banco').AsString := AConsulta.BancoConsulta;

    Qry.ExecSQL;
  finally
    Qry.Free;
  end;
end;

procedure TConsultaRepository.Atualizar(AConsulta: TConsultaModel);
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConnection;
    Qry.SQL.Text :=
      'UPDATE USER_geoapolo_consultas SET ' +
      'descricao_consulta = :descricao, ' +
      'sentenca_sql = :sql, ' +
      'tipo_consulta = :tipo, ' +
      'banco_consulta = :banco ' +
      'WHERE codigo_consulta = :codigo';

    Qry.ParamByName('codigo').AsInteger := AConsulta.Codigo;
    Qry.ParamByName('descricao').AsString := AConsulta.Descricao;
    Qry.ParamByName('sql').AsString := AConsulta.SentencaSQL;
    Qry.ParamByName('tipo').AsString := TipoConsultaToDB(AConsulta.TipoConsulta);
    Qry.ParamByName('banco').AsString := AConsulta.BancoConsulta;

    Qry.ExecSQL;
  finally
    Qry.Free;
  end;
end;

procedure TConsultaRepository.Excluir(ACodigo: Integer);
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConnection;
    Qry.SQL.Text :=
      'DELETE FROM USER_geoapolo_consultas ' +
      'WHERE codigo_consulta = :codigo';

    Qry.ParamByName('codigo').AsInteger := ACodigo;
    Qry.ExecSQL;
  finally
    Qry.Free;
  end;
end;

end.

