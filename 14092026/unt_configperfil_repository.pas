unit unt_configperfil_repository;

{
  GeoApolo - Repositório de Persistência para Configuração de Perfis e Permissões de Objetos
  Clean Architecture: Acesso desacoplado com queries parametrizadas e WITH (NOLOCK).
}

interface

uses
  System.SysUtils, System.Classes, FireDAC.Comp.Client, FireDAC.DApt, Data.DB,
  unt_configperfil_types;

type

  TConfigPerfilRepository = class
  private
    FConexao: TFDConnection;
    function CriarQuery: TFDQuery;
  public
    constructor Create(AConexao: TFDConnection);

    function ListarCategorias(out ALista: TArray<string>): Boolean;
    function ListarPermissoes(const ACodigoGrupo: Integer; const ACategoria: string;
      out ALista: TArray<TDadosObjetoPerfil>): Boolean;
    function BuscarCodigoObjeto(const ANomeTecnico: string): Integer;
    function ObterStatusAcesso(const ACodigoObjeto, ACodigoGrupo: Integer): string;
    function AlterarPermissao(const ACodigoObjeto, ACodigoGrupo: Integer;
      const AStatus: string): Boolean;
    function AlterarPermissaoLote(const ACodigosObjetos: TArray<Integer>;
      const ACodigoGrupo: Integer; const AStatus: string): Integer;
    function SincronizarObjeto(const ANomeTecnico, ANomeAmigavel,
      ACategoria: string): Integer;
    function LimparObjetosObsoletos(const ANomesValidos: TArray<string>): Integer;
  end;

implementation

{ TConfigPerfilRepository }

constructor TConfigPerfilRepository.Create(AConexao: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConexao) then
    raise EArgumentNilException.Create('TConfigPerfilRepository: Conexao nao pode ser nula.');
  FConexao := AConexao;
end;

function TConfigPerfilRepository.CriarQuery: TFDQuery;
begin
  Result := TFDQuery.Create(nil);
  Result.Connection := FConexao;
end;

function TConfigPerfilRepository.ListarCategorias(
  out ALista: TArray<string>): Boolean;
var
  Q: TFDQuery;
  Idx: Integer;
begin
  Result := False;
  SetLength(ALista, 0);
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT DISTINCT categoria ' +
      'FROM USER_geoapolo_objetos WITH (NOLOCK) ' +
      'WHERE categoria IS NOT NULL AND LTRIM(RTRIM(categoria)) <> '''' ' +
      'ORDER BY categoria ASC';
    Q.Open;

    SetLength(ALista, Q.RecordCount);
    Idx := 0;
    while not Q.Eof do
    begin
      ALista[Idx] := Q.FieldByName('categoria').AsString;
      Inc(Idx);
      Q.Next;
    end;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TConfigPerfilRepository.ListarPermissoes(const ACodigoGrupo: Integer;
  const ACategoria: string; out ALista: TArray<TDadosObjetoPerfil>): Boolean;
var
  Q: TFDQuery;
  SqlText: string;
  Idx: Integer;
  HasCat: Boolean;
begin
  Result := False;
  SetLength(ALista, 0);
  if ACodigoGrupo <= 0 then
    Exit;

  Q := CriarQuery;
  try
    HasCat := (Trim(ACategoria) <> '') and (Trim(ACategoria) <> '(Todas)');

    SqlText :=
      'SELECT o.codigo_objeto, o.nome_objeto, ' +
      '       COALESCE(o.nome_amigavel, o.nome_objeto) AS nome_amigavel, ' +
      '       COALESCE(o.categoria, ''Geral'') AS categoria, ' +
      '       COALESCE(g.statusacesso, ''N'') AS statusacesso ' +
      'FROM USER_geoapolo_objetos o WITH (NOLOCK) ' +
      'LEFT JOIN USER_geoapolo_grupobjetos g WITH (NOLOCK) ' +
      '  ON g.codigo_objeto = o.codigo_objeto ' +
      ' AND g.codigo_grupo  = :codigogrupo ' +
      'WHERE 1=1 ';

    if HasCat then
      SqlText := SqlText + 'AND o.categoria = :categoria ';

    SqlText := SqlText + 'ORDER BY o.categoria ASC, nome_amigavel ASC';

    Q.SQL.Text := SqlText;
    Q.ParamByName('codigogrupo').AsInteger := ACodigoGrupo;
    if HasCat then
      Q.ParamByName('categoria').AsString := Trim(ACategoria);

    Q.Open;
    SetLength(ALista, Q.RecordCount);
    Idx := 0;
    while not Q.Eof do
    begin
      ALista[Idx].CodigoObjeto := Q.FieldByName('codigo_objeto').AsInteger;
      ALista[Idx].NomeObjeto   := Q.FieldByName('nome_objeto').AsString;
      ALista[Idx].NomeAmigavel := Q.FieldByName('nome_amigavel').AsString;
      ALista[Idx].Categoria    := Q.FieldByName('categoria').AsString;
      ALista[Idx].CodigoGrupo  := ACodigoGrupo;
      ALista[Idx].StatusAcesso := Q.FieldByName('statusacesso').AsString;
      Inc(Idx);
      Q.Next;
    end;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TConfigPerfilRepository.BuscarCodigoObjeto(
  const ANomeTecnico: string): Integer;
var
  Q: TFDQuery;
begin
  Result := 0;
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT codigo_objeto FROM USER_geoapolo_objetos WITH (NOLOCK) ' +
      'WHERE nome_objeto = :nomeobjeto';
    Q.ParamByName('nomeobjeto').AsString := Trim(ANomeTecnico);
    Q.Open;
    if not Q.IsEmpty then
      Result := Q.FieldByName('codigo_objeto').AsInteger;
  finally
    Q.Free;
  end;
end;

function TConfigPerfilRepository.ObterStatusAcesso(const ACodigoObjeto,
  ACodigoGrupo: Integer): string;
var
  Q: TFDQuery;
begin
  Result := 'N';
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT statusacesso FROM USER_geoapolo_grupobjetos WITH (NOLOCK) ' +
      'WHERE codigo_objeto = :codigobj AND codigo_grupo = :codigogrupo';
    Q.ParamByName('codigobj').AsInteger    := ACodigoObjeto;
    Q.ParamByName('codigogrupo').AsInteger := ACodigoGrupo;
    Q.Open;
    if not Q.IsEmpty then
      Result := Q.FieldByName('statusacesso').AsString;
  finally
    Q.Free;
  end;
end;

function TConfigPerfilRepository.AlterarPermissao(const ACodigoObjeto,
  ACodigoGrupo: Integer; const AStatus: string): Boolean;
var
  Q: TFDQuery;
  Existe: Boolean;
  StatusLimpo: string;
begin
  Result := False;
  if (ACodigoObjeto <= 0) or (ACodigoGrupo <= 0) then
    Exit;

  StatusLimpo := UpperCase(Trim(AStatus));
  if (StatusLimpo <> 'A') and (StatusLimpo <> 'N') then
    StatusLimpo := 'N';

  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT 1 FROM USER_geoapolo_grupobjetos ' +
      'WHERE codigo_objeto = :codigobj AND codigo_grupo = :codigogrupo';
    Q.ParamByName('codigobj').AsInteger    := ACodigoObjeto;
    Q.ParamByName('codigogrupo').AsInteger := ACodigoGrupo;
    Q.Open;
    Existe := not Q.IsEmpty;
    Q.Close;

    if Existe then
    begin
      Q.SQL.Text :=
        'UPDATE USER_geoapolo_grupobjetos ' +
        'SET statusacesso = :statusacesso ' +
        'WHERE codigo_objeto = :codigobj AND codigo_grupo = :codigogrupo';
    end
    else
    begin
      Q.SQL.Text :=
        'INSERT INTO USER_geoapolo_grupobjetos (codigo_objeto, codigo_grupo, statusacesso) ' +
        'VALUES (:codigobj, :codigogrupo, :statusacesso)';
    end;

    Q.ParamByName('codigobj').AsInteger    := ACodigoObjeto;
    Q.ParamByName('codigogrupo').AsInteger := ACodigoGrupo;
    Q.ParamByName('statusacesso').AsString := StatusLimpo;
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TConfigPerfilRepository.AlterarPermissaoLote(
  const ACodigosObjetos: TArray<Integer>; const ACodigoGrupo: Integer;
  const AStatus: string): Integer;
var
  I: Integer;
begin
  Result := 0;
  for I := Low(ACodigosObjetos) to High(ACodigosObjetos) do
  begin
    if AlterarPermissao(ACodigosObjetos[I], ACodigoGrupo, AStatus) then
      Inc(Result);
  end;
end;

function TConfigPerfilRepository.SincronizarObjeto(const ANomeTecnico,
  ANomeAmigavel, ACategoria: string): Integer;
var
  Q: TFDQuery;
  Cod: Integer;
begin
  Cod := BuscarCodigoObjeto(ANomeTecnico);
  Q := CriarQuery;
  try
    if Cod > 0 then
    begin
      Q.SQL.Text :=
        'UPDATE USER_geoapolo_objetos ' +
        'SET nome_amigavel = COALESCE(nome_amigavel, :nomeamigavel), ' +
        '    categoria     = COALESCE(categoria, :categoria) ' +
        'WHERE codigo_objeto = :codigo';
      Q.ParamByName('nomeamigavel').AsString := Trim(ANomeAmigavel);
      Q.ParamByName('categoria').AsString    := Trim(ACategoria);
      Q.ParamByName('codigo').AsInteger      := Cod;
      Q.ExecSQL;
      Result := Cod;
    end
    else
    begin
      Q.SQL.Text :=
        'INSERT INTO USER_geoapolo_objetos (nome_objeto, nome_amigavel, categoria) ' +
        'VALUES (:nomeobjeto, :nomeamigavel, :categoria)';
      Q.ParamByName('nomeobjeto').AsString   := Trim(ANomeTecnico);
      Q.ParamByName('nomeamigavel').AsString := Trim(ANomeAmigavel);
      Q.ParamByName('categoria').AsString    := Trim(ACategoria);
      Q.ExecSQL;
      Result := BuscarCodigoObjeto(ANomeTecnico);
    end;
  finally
    Q.Free;
  end;
end;

function TConfigPerfilRepository.LimparObjetosObsoletos(
  const ANomesValidos: TArray<string>): Integer;
var
  Q: TFDQuery;
  SqlText: string;
  Idx: Integer;
begin
  Result := 0;
  if Length(ANomesValidos) = 0 then
    Exit;

  Q := CriarQuery;
  try
    // Busca objetos que não estejam na lista válida
    SqlText :=
      'SELECT codigo_objeto FROM USER_geoapolo_objetos WITH (NOLOCK) ' +
      'WHERE nome_objeto NOT IN (';
    for Idx := Low(ANomesValidos) to High(ANomesValidos) do
    begin
      if Idx > Low(ANomesValidos) then
        SqlText := SqlText + ', ';
      SqlText := SqlText + QuotedStr(ANomesValidos[Idx]);
    end;
    SqlText := SqlText + ')';

    Q.SQL.Text := SqlText;
    Q.Open;

    while not Q.Eof do
    begin
      var Cod := Q.FieldByName('codigo_objeto').AsInteger;
      var DelQ := CriarQuery;
      try
        DelQ.SQL.Text := 'DELETE FROM USER_geoapolo_grupobjetos WHERE codigo_objeto = :cod';
        DelQ.ParamByName('cod').AsInteger := Cod;
        DelQ.ExecSQL;

        DelQ.SQL.Text := 'DELETE FROM USER_geoapolo_objetos WHERE codigo_objeto = :cod';
        DelQ.ParamByName('cod').AsInteger := Cod;
        DelQ.ExecSQL;
        Inc(Result);
      finally
        DelQ.Free;
      end;
      Q.Next;
    end;
  finally
    Q.Free;
  end;
end;

end.
