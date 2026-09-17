unit unt_imediatas_repository;

{
  GeoApolo - Repositório de Acesso a Consultas Imediatas
  Clean Architecture: Acesso desacoplado com queries parametrizadas e WITH (NOLOCK).
}

interface

uses
  System.SysUtils, System.Classes, FireDAC.Comp.Client, FireDAC.DApt, Data.DB,
  unt_imediatas_types;

type

  TImediatasRepository = class
  private
    FConexaoPadrao : TFDConnection;
    function CriarQuery(AConexao: TFDConnection = nil): TFDQuery;
  public
    constructor Create(AConexao: TFDConnection);

    function ListarConsultasPermitidas(const ABanco, AUsucod: string;
      out ALista: TArray<TDadosConsultaImediata>): Boolean;
    function ObterConsulta(const ACodigo: string;
      out ADados: TDadosConsultaImediata): Boolean;
    function ExecutarConsultaSQL(const ASentencaSQL: string;
      AQueryDestino: TFDQuery; AConexaoAlvo: TFDConnection = nil): Integer;
  end;

implementation

{ TImediatasRepository }

constructor TImediatasRepository.Create(AConexao: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConexao) then
    raise EArgumentNilException.Create('TImediatasRepository: Conexao padrao nao pode ser nula.');
  FConexaoPadrao := AConexao;
end;

function TImediatasRepository.CriarQuery(AConexao: TFDConnection): TFDQuery;
begin
  Result := TFDQuery.Create(nil);
  if Assigned(AConexao) then
    Result.Connection := AConexao
  else
    Result.Connection := FConexaoPadrao;
end;

function TImediatasRepository.ListarConsultasPermitidas(const ABanco,
  AUsucod: string; out ALista: TArray<TDadosConsultaImediata>): Boolean;
var
  Q: TFDQuery;
  SqlText: string;
  Idx: Integer;
  HasBanco, HasUsu: Boolean;
begin
  Result := False;
  SetLength(ALista, 0);
  Q := CriarQuery;
  try
    HasBanco := Trim(ABanco) <> '';
    HasUsu   := Trim(AUsucod) <> '';

    SqlText :=
      'SELECT DISTINCT c.cod_consulta, c.descricao, c.sql, ' +
      '       COALESCE(c.banco, ''Apolo'') AS banco, ' +
      '       COALESCE(c.tipo, ''I'') AS tipo ' +
      'FROM USER_geoapolo_consultas c WITH (NOLOCK) ';

    if HasUsu then
    begin
      SqlText := SqlText +
        'INNER JOIN USER_geoapolo_permissaoconsulta p WITH (NOLOCK) ' +
        '  ON c.cod_consulta = p.cod_consulta ' +
        'WHERE p.usucod = :usucod ';
      if HasBanco then
        SqlText := SqlText + 'AND UPPER(c.banco) = UPPER(:banco) ';
    end
    else
    begin
      SqlText := SqlText + 'WHERE 1=1 ';
      if HasBanco then
        SqlText := SqlText + 'AND UPPER(c.banco) = UPPER(:banco) ';
    end;

    SqlText := SqlText + 'ORDER BY c.descricao ASC';

    Q.SQL.Text := SqlText;
    if HasUsu then
      Q.ParamByName('usucod').AsString := Trim(AUsucod);
    if HasBanco then
      Q.ParamByName('banco').AsString := Trim(ABanco);

    Q.Open;
    SetLength(ALista, Q.RecordCount);
    Idx := 0;
    while not Q.Eof do
    begin
      ALista[Idx].CodigoConsulta := Q.FieldByName('cod_consulta').AsString;
      ALista[Idx].Descricao      := Q.FieldByName('descricao').AsString;
      ALista[Idx].SentencaSQL    := Q.FieldByName('sql').AsString;
      ALista[Idx].BancoConsulta  := Q.FieldByName('banco').AsString;
      ALista[Idx].TipoConsulta   := Q.FieldByName('tipo').AsString;
      Inc(Idx);
      Q.Next;
    end;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TImediatasRepository.ObterConsulta(const ACodigo: string;
  out ADados: TDadosConsultaImediata): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  ADados := Default(TDadosConsultaImediata);
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT cod_consulta, descricao, sql, ' +
      '       COALESCE(banco, ''Apolo'') AS banco, ' +
      '       COALESCE(tipo, ''I'') AS tipo ' +
      'FROM USER_geoapolo_consultas WITH (NOLOCK) ' +
      'WHERE cod_consulta = :codconsulta';
    Q.ParamByName('codconsulta').AsString := Trim(ACodigo);
    Q.Open;

    if not Q.IsEmpty then
    begin
      ADados.CodigoConsulta := Q.FieldByName('cod_consulta').AsString;
      ADados.Descricao      := Q.FieldByName('descricao').AsString;
      ADados.SentencaSQL    := Q.FieldByName('sql').AsString;
      ADados.BancoConsulta  := Q.FieldByName('banco').AsString;
      ADados.TipoConsulta   := Q.FieldByName('tipo').AsString;
      Result := True;
    end;
  finally
    Q.Free;
  end;
end;

function TImediatasRepository.ExecutarConsultaSQL(const ASentencaSQL: string;
  AQueryDestino: TFDQuery; AConexaoAlvo: TFDConnection): Integer;
begin
  if not Assigned(AQueryDestino) then
    raise EArgumentNilException.Create('Query de destino obrigatoria.');

  if Assigned(AConexaoAlvo) then
    AQueryDestino.Connection := AConexaoAlvo
  else if not Assigned(AQueryDestino.Connection) then
    AQueryDestino.Connection := FConexaoPadrao;

  AQueryDestino.Close;
  AQueryDestino.SQL.Text := ASentencaSQL;
  AQueryDestino.Open;
  Result := AQueryDestino.RecordCount;
end;

end.
