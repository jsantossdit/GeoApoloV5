unit unt_grupousuario_repository;

{
  GeoApolo - Repositório de Persistência para Grupos de Usuários e Vínculos
  Clean Architecture: Acesso desacoplado com queries parametrizadas e WITH (NOLOCK).
}

interface

uses
  System.SysUtils, System.Classes, FireDAC.Comp.Client, FireDAC.DApt, Data.DB,
  unt_grupousuario_types;

type

  TGrupoUsuarioRepository = class
  private
    FConexao: TFDConnection;
    function CriarQuery: TFDQuery;
  public
    constructor Create(AConexao: TFDConnection);

    function ListarGrupos(out ALista: TArray<TDadosGrupoUsuario>): Boolean;
    function ObterGrupo(const ACodigoGrupo: string; out ADados: TDadosGrupoUsuario): Boolean;
    function SalvarGrupo(const ADados: TDadosGrupoUsuario): Boolean;
    function ExcluirGrupo(const ACodigoGrupo: string): Boolean;

    function ListarUsuariosGrupo(const ACodigoGrupo: string;
      out ALista: TArray<TVinculoUsuarioGrupo>): Boolean;
    function VincularUsuarioGrupo(const ACodigoGrupo, AUsucod: string): Boolean;
    function DesvincularUsuarioGrupo(const ACodigoGrupo, AUsucod: string): Boolean;
    function ExisteVinculo(const ACodigoGrupo, AUsucod: string): Boolean;
    function ExisteDescricaoGrupo(const ADescricao, AExceptCodigo: string): Boolean;
    function TotalMembrosGrupo(const ACodigoGrupo: string): Integer;
  end;

implementation

{ TGrupoUsuarioRepository }

constructor TGrupoUsuarioRepository.Create(AConexao: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConexao) then
    raise EArgumentNilException.Create('TGrupoUsuarioRepository: Conexao nao pode ser nula.');
  FConexao := AConexao;
end;

function TGrupoUsuarioRepository.CriarQuery: TFDQuery;
begin
  Result := TFDQuery.Create(nil);
  Result.Connection := FConexao;
end;

function TGrupoUsuarioRepository.ListarGrupos(out ALista: TArray<TDadosGrupoUsuario>): Boolean;
var
  Q: TFDQuery;
  Idx: Integer;
begin
  Result := False;
  SetLength(ALista, 0);
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT g.codigo_grupo, g.descricao, COUNT(gu.usucod) AS total_usuarios ' +
      'FROM USER_geoapolo_grupo g WITH (NOLOCK) ' +
      'LEFT JOIN USER_geoapolo_grupousuario gu WITH (NOLOCK) ON g.codigo_grupo = gu.codigo_grupo ' +
      'GROUP BY g.codigo_grupo, g.descricao ' +
      'ORDER BY g.descricao ASC';
    Q.Open;

    SetLength(ALista, Q.RecordCount);
    Idx := 0;
    while not Q.Eof do
    begin
      ALista[Idx].CodigoGrupo   := Q.FieldByName('codigo_grupo').AsString;
      ALista[Idx].Descricao     := Q.FieldByName('descricao').AsString;
      ALista[Idx].TotalUsuarios := Q.FieldByName('total_usuarios').AsInteger;
      Inc(Idx);
      Q.Next;
    end;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TGrupoUsuarioRepository.ObterGrupo(const ACodigoGrupo: string;
  out ADados: TDadosGrupoUsuario): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  ADados := Default(TDadosGrupoUsuario);
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT codigo_grupo, descricao ' +
      'FROM USER_geoapolo_grupo WITH (NOLOCK) ' +
      'WHERE codigo_grupo = :codigogrupo';
    Q.ParamByName('codigogrupo').AsString := Trim(ACodigoGrupo);
    Q.Open;

    if not Q.IsEmpty then
    begin
      ADados.CodigoGrupo := Q.FieldByName('codigo_grupo').AsString;
      ADados.Descricao   := Q.FieldByName('descricao').AsString;
      Result := True;
    end;
  finally
    Q.Free;
  end;
end;

function TGrupoUsuarioRepository.ExisteDescricaoGrupo(const ADescricao,
  AExceptCodigo: string): Boolean;
var
  Q: TFDQuery;
  SqlText: string;
begin
  Q := CriarQuery;
  try
    SqlText :=
      'SELECT 1 FROM USER_geoapolo_grupo WITH (NOLOCK) ' +
      'WHERE UPPER(descricao) = UPPER(:descricao)';
    if Trim(AExceptCodigo) <> '' then
      SqlText := SqlText + ' AND codigo_grupo <> :exceptcodigo';

    Q.SQL.Text := SqlText;
    Q.ParamByName('descricao').AsString := Trim(ADescricao);
    if Trim(AExceptCodigo) <> '' then
      Q.ParamByName('exceptcodigo').AsString := Trim(AExceptCodigo);

    Q.Open;
    Result := not Q.IsEmpty;
  finally
    Q.Free;
  end;
end;

function TGrupoUsuarioRepository.SalvarGrupo(
  const ADados: TDadosGrupoUsuario): Boolean;
var
  Q: TFDQuery;
  Existe: Boolean;
begin
  Result := False;
  Q := CriarQuery;
  try
    Q.SQL.Text := 'SELECT 1 FROM USER_geoapolo_grupo WHERE codigo_grupo = :codigogrupo';
    Q.ParamByName('codigogrupo').AsString := Trim(ADados.CodigoGrupo);
    Q.Open;
    Existe := not Q.IsEmpty;
    Q.Close;

    if Existe then
    begin
      Q.SQL.Text :=
        'UPDATE USER_geoapolo_grupo ' +
        'SET descricao = :descricao ' +
        'WHERE codigo_grupo = :codigogrupo';
    end
    else
    begin
      Q.SQL.Text :=
        'INSERT INTO USER_geoapolo_grupo (codigo_grupo, descricao) ' +
        'VALUES (:codigogrupo, :descricao)';
    end;

    Q.ParamByName('codigogrupo').AsString := Trim(ADados.CodigoGrupo);
    Q.ParamByName('descricao').AsString   := Trim(ADados.Descricao);
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TGrupoUsuarioRepository.ExcluirGrupo(const ACodigoGrupo: string): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  Q := CriarQuery;
  try
    // Remove permissões e vínculos vinculados ao grupo
    Q.SQL.Text := 'DELETE FROM USER_geoapolo_grupobjetos WHERE codigo_grupo = :codigogrupo';
    Q.ParamByName('codigogrupo').AsString := Trim(ACodigoGrupo);
    Q.ExecSQL;

    Q.SQL.Text := 'DELETE FROM USER_geoapolo_grupousuario WHERE codigo_grupo = :codigogrupo';
    Q.ParamByName('codigogrupo').AsString := Trim(ACodigoGrupo);
    Q.ExecSQL;

    Q.SQL.Text := 'DELETE FROM USER_geoapolo_grupo WHERE codigo_grupo = :codigogrupo';
    Q.ParamByName('codigogrupo').AsString := Trim(ACodigoGrupo);
    Q.ExecSQL;

    Result := True;
  finally
    Q.Free;
  end;
end;

function TGrupoUsuarioRepository.ListarUsuariosGrupo(const ACodigoGrupo: string;
  out ALista: TArray<TVinculoUsuarioGrupo>): Boolean;
var
  Q: TFDQuery;
  Idx: Integer;
begin
  Result := False;
  SetLength(ALista, 0);
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT gu.codigo_grupo, g.descricao, u.usucod, u.login, ' +
      '       COALESCE(u.nome_completo, u.login) AS nome_completo ' +
      'FROM USER_geoapolo_grupousuario gu WITH (NOLOCK) ' +
      'INNER JOIN USER_geoapolo_grupo g WITH (NOLOCK) ON gu.codigo_grupo = g.codigo_grupo ' +
      'INNER JOIN USER_geoapolo_usuarios u WITH (NOLOCK) ON gu.usucod = u.usucod ' +
      'WHERE gu.codigo_grupo = :codigogrupo AND u.flagativo IN (''A'', ''S'') ' +
      'ORDER BY nome_completo ASC';
    Q.ParamByName('codigogrupo').AsString := Trim(ACodigoGrupo);
    Q.Open;

    SetLength(ALista, Q.RecordCount);
    Idx := 0;
    while not Q.Eof do
    begin
      ALista[Idx].CodigoGrupo  := Q.FieldByName('codigo_grupo').AsString;
      ALista[Idx].NomeGrupo    := Q.FieldByName('descricao').AsString;
      ALista[Idx].Usucod       := Q.FieldByName('usucod').AsString;
      ALista[Idx].Login        := Q.FieldByName('login').AsString;
      ALista[Idx].NomeCompleto := Q.FieldByName('nome_completo').AsString;
      Inc(Idx);
      Q.Next;
    end;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TGrupoUsuarioRepository.ExisteVinculo(const ACodigoGrupo,
  AUsucod: string): Boolean;
var
  Q: TFDQuery;
begin
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT 1 FROM USER_geoapolo_grupousuario WITH (NOLOCK) ' +
      'WHERE codigo_grupo = :codigogrupo AND usucod = :usucod';
    Q.ParamByName('codigogrupo').AsString := Trim(ACodigoGrupo);
    Q.ParamByName('usucod').AsString      := Trim(AUsucod);
    Q.Open;
    Result := not Q.IsEmpty;
  finally
    Q.Free;
  end;
end;

function TGrupoUsuarioRepository.VincularUsuarioGrupo(const ACodigoGrupo,
  AUsucod: string): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  if ExisteVinculo(ACodigoGrupo, AUsucod) then
    Exit(True);

  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'INSERT INTO USER_geoapolo_grupousuario (codigo_grupo, usucod) ' +
      'VALUES (:codigogrupo, :usucod)';
    Q.ParamByName('codigogrupo').AsString := Trim(ACodigoGrupo);
    Q.ParamByName('usucod').AsString      := Trim(AUsucod);
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TGrupoUsuarioRepository.DesvincularUsuarioGrupo(const ACodigoGrupo,
  AUsucod: string): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'DELETE FROM USER_geoapolo_grupousuario ' +
      'WHERE codigo_grupo = :codigogrupo AND usucod = :usucod';
    Q.ParamByName('codigogrupo').AsString := Trim(ACodigoGrupo);
    Q.ParamByName('usucod').AsString      := Trim(AUsucod);
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TGrupoUsuarioRepository.TotalMembrosGrupo(
  const ACodigoGrupo: string): Integer;
var
  Q: TFDQuery;
begin
  Result := 0;
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT COUNT(1) AS total FROM USER_geoapolo_grupousuario WITH (NOLOCK) ' +
      'WHERE codigo_grupo = :codigogrupo';
    Q.ParamByName('codigogrupo').AsString := Trim(ACodigoGrupo);
    Q.Open;
    if not Q.IsEmpty then
      Result := Q.FieldByName('total').AsInteger;
  finally
    Q.Free;
  end;
end;

end.
