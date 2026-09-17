unit unt_cadcategorias_repository;

{
  GeoApolo - Repositório de Persistência para Cadastro de Categorias e Operadores
  Clean Architecture: Acesso desacoplado com queries parametrizadas e WITH (NOLOCK).
}

interface

uses
  System.SysUtils, System.Classes, FireDAC.Comp.Client, FireDAC.DApt, Data.DB,
  unt_cadcategorias_types;

type

  TCadCategoriasRepository = class
  private
    FConexao: TFDConnection;
    function CriarQuery: TFDQuery;
  public
    constructor Create(AConexao: TFDConnection);

    function ListarCategorias(out ALista: TArray<TDadosCadCategoria>): Boolean;
    function ObterCategoria(const ACodigoEstrutural: string;
      out ADados: TDadosCadCategoria): Boolean;
    function SalvarCategoria(const ADados: TDadosCadCategoria): Boolean;
    function ExcluirCategoria(const ACodigoEstrutural: string): Boolean;

    function ListarUsuariosDisponiveis(const ACodigoEstrutural: string;
      out ALista: TArray<TVinculoUsuarioCategoria>): Boolean;
    function ListarUsuariosVinculados(const ACodigoEstrutural: string;
      out ALista: TArray<TVinculoUsuarioCategoria>): Boolean;

    function VincularUsuario(const ACodigoEstrutural, AUsucod: string): Boolean;
    function DesvincularUsuario(const ACodigoEstrutural, AUsucod: string): Boolean;
    function VincularTodosUsuarios(const ACodigoEstrutural: string): Integer;
    function DesvincularTodosUsuarios(const ACodigoEstrutural: string): Integer;
    function TotalEntidadesVinculadas(const ACodigoEstrutural: string): Integer;
  end;

implementation

{ TCadCategoriasRepository }

constructor TCadCategoriasRepository.Create(AConexao: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConexao) then
    raise EArgumentNilException.Create('TCadCategoriasRepository: Conexao nao pode ser nula.');
  FConexao := AConexao;
end;

function TCadCategoriasRepository.CriarQuery: TFDQuery;
begin
  Result := TFDQuery.Create(nil);
  Result.Connection := FConexao;
end;

function TCadCategoriasRepository.ListarCategorias(
  out ALista: TArray<TDadosCadCategoria>): Boolean;
var
  Q: TFDQuery;
  Idx: Integer;
begin
  Result := False;
  SetLength(ALista, 0);
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT geocategcodestr, geocategnome, COALESCE(geocodcategalt, '''') AS geocodcategalt, ' +
      '       COALESCE(chkgrupo, ''N'') AS chkgrupo ' +
      'FROM USER_geoapolo_categoria WITH (NOLOCK) ' +
      'ORDER BY geocategcodestr ASC';
    Q.Open;

    SetLength(ALista, Q.RecordCount);
    Idx := 0;
    while not Q.Eof do
    begin
      ALista[Idx].CodigoEstrutural  := Q.FieldByName('geocategcodestr').AsString;
      ALista[Idx].Nome              := Q.FieldByName('geocategnome').AsString;
      ALista[Idx].CodigoAlternativo := Q.FieldByName('geocodcategalt').AsString;
      ALista[Idx].IsGrupo           := Q.FieldByName('chkgrupo').AsString.ToUpper.Equals('S') or
                                       Q.FieldByName('chkgrupo').AsString.ToUpper.Equals('T');
      Inc(Idx);
      Q.Next;
    end;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TCadCategoriasRepository.ObterCategoria(
  const ACodigoEstrutural: string; out ADados: TDadosCadCategoria): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  ADados := Default(TDadosCadCategoria);
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT geocategcodestr, geocategnome, COALESCE(geocodcategalt, '''') AS geocodcategalt, ' +
      '       COALESCE(chkgrupo, ''N'') AS chkgrupo ' +
      'FROM USER_geoapolo_categoria WITH (NOLOCK) ' +
      'WHERE geocategcodestr = :codestr';
    Q.ParamByName('codestr').AsString := Trim(ACodigoEstrutural);
    Q.Open;

    if not Q.IsEmpty then
    begin
      ADados.CodigoEstrutural  := Q.FieldByName('geocategcodestr').AsString;
      ADados.Nome              := Q.FieldByName('geocategnome').AsString;
      ADados.CodigoAlternativo := Q.FieldByName('geocodcategalt').AsString;
      ADados.IsGrupo           := Q.FieldByName('chkgrupo').AsString.ToUpper.Equals('S') or
                                  Q.FieldByName('chkgrupo').AsString.ToUpper.Equals('T');
      Result := True;
    end;
  finally
    Q.Free;
  end;
end;

function TCadCategoriasRepository.SalvarCategoria(
  const ADados: TDadosCadCategoria): Boolean;
var
  Q: TFDQuery;
  Existe: Boolean;
  StrGrupo: string;
begin
  Result := False;
  StrGrupo := 'N';
  if ADados.IsGrupo then
    StrGrupo := 'S';

  Q := CriarQuery;
  try
    Q.SQL.Text := 'SELECT 1 FROM USER_geoapolo_categoria WHERE geocategcodestr = :codestr';
    Q.ParamByName('codestr').AsString := Trim(ADados.CodigoEstrutural);
    Q.Open;
    Existe := not Q.IsEmpty;
    Q.Close;

    if Existe then
    begin
      Q.SQL.Text :=
        'UPDATE USER_geoapolo_categoria ' +
        'SET geocategnome   = :nome, ' +
        '    geocodcategalt = :alt, ' +
        '    chkgrupo       = :grupo ' +
        'WHERE geocategcodestr = :codestr';
    end
    else
    begin
      Q.SQL.Text :=
        'INSERT INTO USER_geoapolo_categoria (geocategcodestr, geocategnome, geocodcategalt, chkgrupo) ' +
        'VALUES (:codestr, :nome, :alt, :grupo)';
    end;

    Q.ParamByName('codestr').AsString := Trim(ADados.CodigoEstrutural);
    Q.ParamByName('nome').AsString    := Trim(ADados.Nome);
    Q.ParamByName('alt').AsString     := Trim(ADados.CodigoAlternativo);
    Q.ParamByName('grupo').AsString   := StrGrupo;
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TCadCategoriasRepository.ExcluirCategoria(
  const ACodigoEstrutural: string): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  Q := CriarQuery;
  try
    Q.SQL.Text := 'DELETE FROM USER_geoapolo_usuariocateg WHERE geocategcodestr = :codestr';
    Q.ParamByName('codestr').AsString := Trim(ACodigoEstrutural);
    Q.ExecSQL;

    Q.SQL.Text := 'DELETE FROM USER_geoapolo_categoria WHERE geocategcodestr = :codestr';
    Q.ParamByName('codestr').AsString := Trim(ACodigoEstrutural);
    Q.ExecSQL;

    Result := True;
  finally
    Q.Free;
  end;
end;

function TCadCategoriasRepository.ListarUsuariosDisponiveis(
  const ACodigoEstrutural: string;
  out ALista: TArray<TVinculoUsuarioCategoria>): Boolean;
var
  Q: TFDQuery;
  Idx: Integer;
begin
  Result := False;
  SetLength(ALista, 0);
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT u.usucod, u.login, COALESCE(u.nome_completo, u.login) AS nome ' +
      'FROM USER_geoapolo_usuarios u WITH (NOLOCK) ' +
      'WHERE u.flagativo IN (''A'', ''S'') ' +
      '  AND u.usucod NOT IN ( ' +
      '    SELECT uc.usucod FROM USER_geoapolo_usuariocateg uc WITH (NOLOCK) ' +
      '    WHERE uc.geocategcodestr = :codestr ' +
      '  ) ' +
      'ORDER BY nome ASC';
    Q.ParamByName('codestr').AsString := Trim(ACodigoEstrutural);
    Q.Open;

    SetLength(ALista, Q.RecordCount);
    Idx := 0;
    while not Q.Eof do
    begin
      ALista[Idx].CodigoCategoria := Trim(ACodigoEstrutural);
      ALista[Idx].Usucod          := Q.FieldByName('usucod').AsString;
      ALista[Idx].Login           := Q.FieldByName('login').AsString;
      ALista[Idx].Nome            := Q.FieldByName('nome').AsString;
      Inc(Idx);
      Q.Next;
    end;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TCadCategoriasRepository.ListarUsuariosVinculados(
  const ACodigoEstrutural: string;
  out ALista: TArray<TVinculoUsuarioCategoria>): Boolean;
var
  Q: TFDQuery;
  Idx: Integer;
begin
  Result := False;
  SetLength(ALista, 0);
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT uc.geocategcodestr, uc.usucod, u.login, ' +
      '       COALESCE(u.nome_completo, u.login) AS nome ' +
      'FROM USER_geoapolo_usuariocateg uc WITH (NOLOCK) ' +
      'INNER JOIN USER_geoapolo_usuarios u WITH (NOLOCK) ON uc.usucod = u.usucod ' +
      'WHERE uc.geocategcodestr = :codestr ' +
      'ORDER BY nome ASC';
    Q.ParamByName('codestr').AsString := Trim(ACodigoEstrutural);
    Q.Open;

    SetLength(ALista, Q.RecordCount);
    Idx := 0;
    while not Q.Eof do
    begin
      ALista[Idx].CodigoCategoria := Q.FieldByName('geocategcodestr').AsString;
      ALista[Idx].Usucod          := Q.FieldByName('usucod').AsString;
      ALista[Idx].Login           := Q.FieldByName('login').AsString;
      ALista[Idx].Nome            := Q.FieldByName('nome').AsString;
      Inc(Idx);
      Q.Next;
    end;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TCadCategoriasRepository.VincularUsuario(const ACodigoEstrutural,
  AUsucod: string): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT 1 FROM USER_geoapolo_usuariocateg WITH (NOLOCK) ' +
      'WHERE geocategcodestr = :codestr AND usucod = :usucod';
    Q.ParamByName('codestr').AsString := Trim(ACodigoEstrutural);
    Q.ParamByName('usucod').AsString  := Trim(AUsucod);
    Q.Open;
    if not Q.IsEmpty then
      Exit(True);
    Q.Close;

    Q.SQL.Text :=
      'INSERT INTO USER_geoapolo_usuariocateg (geocategcodestr, usucod) ' +
      'VALUES (:codestr, :usucod)';
    Q.ParamByName('codestr').AsString := Trim(ACodigoEstrutural);
    Q.ParamByName('usucod').AsString  := Trim(AUsucod);
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TCadCategoriasRepository.DesvincularUsuario(const ACodigoEstrutural,
  AUsucod: string): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'DELETE FROM USER_geoapolo_usuariocateg ' +
      'WHERE geocategcodestr = :codestr AND usucod = :usucod';
    Q.ParamByName('codestr').AsString := Trim(ACodigoEstrutural);
    Q.ParamByName('usucod').AsString  := Trim(AUsucod);
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TCadCategoriasRepository.VincularTodosUsuarios(
  const ACodigoEstrutural: string): Integer;
var
  Q: TFDQuery;
begin
  Result := 0;
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'INSERT INTO USER_geoapolo_usuariocateg (geocategcodestr, usucod) ' +
      'SELECT :codestr, u.usucod FROM USER_geoapolo_usuarios u WITH (NOLOCK) ' +
      'WHERE u.flagativo IN (''A'', ''S'') ' +
      '  AND u.usucod NOT IN ( ' +
      '    SELECT uc.usucod FROM USER_geoapolo_usuariocateg uc WITH (NOLOCK) ' +
      '    WHERE uc.geocategcodestr = :codestr2 ' +
      '  )';
    Q.ParamByName('codestr').AsString  := Trim(ACodigoEstrutural);
    Q.ParamByName('codestr2').AsString := Trim(ACodigoEstrutural);
    Q.ExecSQL;
    Result := Q.RowsAffected;
  finally
    Q.Free;
  end;
end;

function TCadCategoriasRepository.DesvincularTodosUsuarios(
  const ACodigoEstrutural: string): Integer;
var
  Q: TFDQuery;
begin
  Result := 0;
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'DELETE FROM USER_geoapolo_usuariocateg WHERE geocategcodestr = :codestr';
    Q.ParamByName('codestr').AsString := Trim(ACodigoEstrutural);
    Q.ExecSQL;
    Result := Q.RowsAffected;
  finally
    Q.Free;
  end;
end;

function TCadCategoriasRepository.TotalEntidadesVinculadas(
  const ACodigoEstrutural: string): Integer;
var
  Q: TFDQuery;
begin
  Result := 0;
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT COUNT(1) AS total FROM USER_geoapolo_entidade WITH (NOLOCK) ' +
      'WHERE geocategcodestr = :codestr';
    Q.ParamByName('codestr').AsString := Trim(ACodigoEstrutural);
    Q.Open;
    if not Q.IsEmpty then
      Result := Q.FieldByName('total').AsInteger;
  finally
    Q.Free;
  end;
end;

end.
