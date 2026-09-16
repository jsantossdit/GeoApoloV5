unit unt_repositorio_usuario;

{
  GeoApolo - TRepositorioUsuarioDB
  Implementa IRepositorioUsuario usando FireDAC (TFDConnection + TFDQuery).
  Nao conhece formularios nem Application.
}

interface

uses
  SysUtils,
  FireDAC.Comp.Client,
  unt_logon_interfaces;

type

  TRepositorioUsuarioDB = class(TInterfacedObject, IRepositorioUsuario)
  private
    FConexao: TFDConnection;
    function CriarQuery: TFDQuery;
  public
    constructor Create(AConexao: TFDConnection);

    { IRepositorioUsuario }
    function BuscarPorLogin(const ALogin: string;
      out AUsuario: TDadosUsuario): Boolean;
    function BuscarCodigoSistema(const ASigla: string;
      out ACodigo: Integer): Boolean;
    function UsuarioPossuiPermissaoSistema(const ACodUsuario: string;
      ACodigoSistema: Integer): Boolean;
    function AtualizarSenha(const ALogin, ASenhaHash: string): Boolean;
    function AtualizarDadosAlvo(const ALogin, ACodApoloLink,
      ASenhaAlvoHash: string): Boolean;
  end;

implementation

{ TRepositorioUsuarioDB }

constructor TRepositorioUsuarioDB.Create(AConexao: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConexao) then
    raise EArgumentNilException.Create('TRepositorioUsuarioDB: conexao nao pode ser nil');
  FConexao := AConexao;
end;

function TRepositorioUsuarioDB.CriarQuery: TFDQuery;
begin
  Result := TFDQuery.Create(nil);
  Result.Connection := FConexao;
end;

function TRepositorioUsuarioDB.BuscarPorLogin(const ALogin: string;
  out AUsuario: TDadosUsuario): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  AUsuario := Default(TDadosUsuario);

  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT usucod, login, nome_completo, usucod_apolo, senha, senha_alvo, flagativo ' +
      'FROM USER_geoapolo_usuarios ' +
      'WHERE login = :login AND flagativo = :flagativo';
    Q.ParamByName('login').AsString    := ALogin;
    Q.ParamByName('flagativo').AsString := 'A';
    Q.Open;

    if not Q.IsEmpty then
    begin
      AUsuario.CodUsuario   := Q.FieldByName('usucod').AsString;
      AUsuario.Login        := Q.FieldByName('login').AsString;
      AUsuario.NomeCompleto := Q.FieldByName('nome_completo').AsString;
      AUsuario.CodApoloLink := Q.FieldByName('usucod_apolo').AsString;
      AUsuario.SenhaHash    := Q.FieldByName('senha').AsString;
      AUsuario.SenhaAlvo    := Q.FieldByName('senha_alvo').AsString;
      AUsuario.Ativo        := Q.FieldByName('flagativo').AsString = 'A';
      Result := True;
    end;
  finally
    Q.Free;
  end;
end;

function TRepositorioUsuarioDB.BuscarCodigoSistema(const ASigla: string;
  out ACodigo: Integer): Boolean;
var
  Q: TFDQuery;
begin
  Result  := False;
  ACodigo := 0;

  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT codigo_sistema FROM USER_geoapolo_sistemas ' +
      'WHERE sigla = :sigla';
    Q.ParamByName('sigla').AsString := ASigla;
    Q.Open;

    if not Q.IsEmpty then
    begin
      ACodigo := Q.FieldByName('codigo_sistema').AsInteger;
      Result  := True;
    end;
  finally
    Q.Free;
  end;
end;

function TRepositorioUsuarioDB.UsuarioPossuiPermissaoSistema(
  const ACodUsuario: string; ACodigoSistema: Integer): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;

  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT usucod FROM USER_geoapolo_usuariossistemas ' +
      'WHERE usucod = :usucod AND codigo_sistema = :codsistema';
    Q.ParamByName('usucod').AsString     := ACodUsuario;
    Q.ParamByName('codsistema').AsInteger := ACodigoSistema;
    Q.Open;

    // usucod = '0' significa acesso negado na regra original
    Result := (not Q.IsEmpty) and
              (Q.FieldByName('usucod').AsString <> '0');
  finally
    Q.Free;
  end;
end;

function TRepositorioUsuarioDB.AtualizarSenha(const ALogin,
  ASenhaHash: string): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;

  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'UPDATE USER_geoapolo_usuarios SET senha = :senha ' +
      'WHERE login = :login';
    Q.ParamByName('senha').AsString := ASenhaHash;
    Q.ParamByName('login').AsString := ALogin;
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TRepositorioUsuarioDB.AtualizarDadosAlvo(const ALogin, ACodApoloLink,
  ASenhaAlvoHash: string): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;

  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'UPDATE USER_geoapolo_usuarios SET usucod_apolo = :usucodapolo, ' +
      'senha_alvo = :senhaalvo WHERE login = :login';
    Q.ParamByName('usucodapolo').AsString := ACodApoloLink;
    Q.ParamByName('senhaalvo').AsString   := ASenhaAlvoHash;
    Q.ParamByName('login').AsString       := ALogin;
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

end.
