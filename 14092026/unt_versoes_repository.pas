unit unt_versoes_repository;

{
  GeoApolo - Repositório de Persistência de Versões do Sistema
  Clean Architecture: Acesso desacoplado com queries parametrizadas e WITH (NOLOCK).
}

interface

uses
  System.SysUtils, System.Classes, FireDAC.Comp.Client, FireDAC.DApt, Data.DB,
  unt_versoes_types;

type

  TVersoesRepository = class
  private
    FConexao: TFDConnection;
    function CriarQuery: TFDQuery;
  public
    constructor Create(AConexao: TFDConnection);

    function ListarVersoes(out ALista: TArray<TDadosVersao>): Boolean;
    function ObterVersao(const AIDVersao: string; out ADados: TDadosVersao): Boolean;
    function SalvarVersao(const ADados: TDadosVersao; AIsAlteracao: Boolean): Boolean;
    function ExcluirVersao(const AIDVersao: string): Boolean;
    function UsuarioJaViuVersao(const AIDVersao, AUsuCod: string): Boolean;
    function RegistrarLeituraVersao(const AIDVersao, AUsuCod: string): Boolean;
  end;

implementation

{ TVersoesRepository }

constructor TVersoesRepository.Create(AConexao: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConexao) then
    raise EArgumentNilException.Create('TVersoesRepository: Conexao nao pode ser nula.');
  FConexao := AConexao;
end;

function TVersoesRepository.CriarQuery: TFDQuery;
begin
  Result := TFDQuery.Create(nil);
  Result.Connection := FConexao;
end;

function TVersoesRepository.ListarVersoes(out ALista: TArray<TDadosVersao>): Boolean;
var
  Q: TFDQuery;
  Idx: Integer;
begin
  Result := False;
  SetLength(ALista, 0);
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT idversao, data_lancamento, textonovaversao, statusversao ' +
      'FROM USER_geoapolo_novversao WITH (NOLOCK) ' +
      'ORDER BY data_lancamento DESC, idversao DESC';
    Q.Open;

    SetLength(ALista, Q.RecordCount);
    Idx := 0;
    while not Q.Eof do
    begin
      ALista[Idx].IDVersao        := Q.FieldByName('idversao').AsString;
      ALista[Idx].DataLancamento  := Q.FieldByName('data_lancamento').AsString;
      ALista[Idx].TextoNovaVersao := Q.FieldByName('textonovaversao').AsString;
      ALista[Idx].StatusVersao    := Q.FieldByName('statusversao').AsString;
      Inc(Idx);
      Q.Next;
    end;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TVersoesRepository.ObterVersao(const AIDVersao: string;
  out ADados: TDadosVersao): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  ADados := Default(TDadosVersao);
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT idversao, data_lancamento, textonovaversao, statusversao ' +
      'FROM USER_geoapolo_novversao WITH (NOLOCK) ' +
      'WHERE idversao = :idversao';
    Q.ParamByName('idversao').AsString := AIDVersao;
    Q.Open;

    if not Q.IsEmpty then
    begin
      ADados.IDVersao        := Q.FieldByName('idversao').AsString;
      ADados.DataLancamento  := Q.FieldByName('data_lancamento').AsString;
      ADados.TextoNovaVersao := Q.FieldByName('textonovaversao').AsString;
      ADados.StatusVersao    := Q.FieldByName('statusversao').AsString;
      Result := True;
    end;
  finally
    Q.Free;
  end;
end;

function TVersoesRepository.SalvarVersao(const ADados: TDadosVersao;
  AIsAlteracao: Boolean): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  Q := CriarQuery;
  try
    if AIsAlteracao then
    begin
      Q.SQL.Text :=
        'UPDATE USER_geoapolo_novversao ' +
        'SET data_lancamento = :dataliberacao, ' +
        '    textonovaversao = :novidades, ' +
        '    statusversao    = :statusversao ' +
        'WHERE idversao = :idversao';
    end
    else
    begin
      Q.SQL.Text :=
        'INSERT INTO USER_geoapolo_novversao ' +
        '(idversao, data_lancamento, textonovaversao, statusversao) ' +
        'VALUES (:idversao, :dataliberacao, :novidades, :statusversao)';
    end;

    Q.ParamByName('idversao').AsString        := Trim(ADados.IDVersao);
    Q.ParamByName('dataliberacao').AsString    := Trim(ADados.DataLancamento);
    Q.ParamByName('novidades').AsString        := ADados.TextoNovaVersao;
    Q.ParamByName('statusversao').AsString     := Trim(ADados.StatusVersao);

    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TVersoesRepository.ExcluirVersao(const AIDVersao: string): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  Q := CriarQuery;
  try
    Q.SQL.Text := 'DELETE FROM USER_geoapolo_novversao WHERE idversao = :idversao';
    Q.ParamByName('idversao').AsString := AIDVersao;
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TVersoesRepository.UsuarioJaViuVersao(const AIDVersao,
  AUsuCod: string): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT COUNT(1) FROM USER_geoapolo_userversao WITH (NOLOCK) ' +
      'WHERE idversao = :idversao AND usucod = :usucod';
    Q.ParamByName('idversao').AsString := AIDVersao;
    Q.ParamByName('usucod').AsString   := AUsuCod;
    Q.Open;

    if not Q.IsEmpty then
      Result := Q.Fields[0].AsInteger > 0;
  finally
    Q.Free;
  end;
end;

function TVersoesRepository.RegistrarLeituraVersao(const AIDVersao,
  AUsuCod: string): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  if UsuarioJaViuVersao(AIDVersao, AUsuCod) then
  begin
    Result := True;
    Exit;
  end;

  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'INSERT INTO USER_geoapolo_userversao (idversao, usucod) ' +
      'VALUES (:idversao, :usucod)';
    Q.ParamByName('idversao').AsString := AIDVersao;
    Q.ParamByName('usucod').AsString   := AUsuCod;
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

end.
