unit unt_nomesamigaveis_repository;

{
  GeoApolo - Repositório de Persistência para Nomes Amigáveis de Objetos
  Clean Architecture: Acesso desacoplado com queries parametrizadas e WITH (NOLOCK).
}

interface

uses
  System.SysUtils, System.Classes, FireDAC.Comp.Client, FireDAC.DApt, Data.DB,
  unt_nomesamigaveis_types;

type

  TNomesAmigaveisRepository = class
  private
    FConexao: TFDConnection;
    function CriarQuery: TFDQuery;
  public
    constructor Create(AConexao: TFDConnection);

    function ListarObjetos(const ACategoria, AFiltro: string;
      out ALista: TArray<TDadosObjetoAmigavel>): Boolean;
    function ObterObjeto(const ANomeObjeto: string;
      out ADados: TDadosObjetoAmigavel): Boolean;
    function SalvarObjeto(const ADados: TDadosObjetoAmigavel): Boolean;
    function AtualizarNomeAmigavel(const ANomeObjeto, ANomeAmigavel,
      ACategoria: string): Boolean;
  end;

implementation

{ TNomesAmigaveisRepository }

constructor TNomesAmigaveisRepository.Create(AConexao: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConexao) then
    raise EArgumentNilException.Create('TNomesAmigaveisRepository: Conexao nao pode ser nula.');
  FConexao := AConexao;
end;

function TNomesAmigaveisRepository.CriarQuery: TFDQuery;
begin
  Result := TFDQuery.Create(nil);
  Result.Connection := FConexao;
end;

function TNomesAmigaveisRepository.ListarObjetos(const ACategoria,
  AFiltro: string; out ALista: TArray<TDadosObjetoAmigavel>): Boolean;
var
  Q: TFDQuery;
  Idx: Integer;
  SqlText: string;
  HasCat, HasFiltro: Boolean;
begin
  Result := False;
  SetLength(ALista, 0);
  Q := CriarQuery;
  try
    HasCat := Trim(ACategoria) <> '';
    HasFiltro := Trim(AFiltro) <> '';

    SqlText :=
      'SELECT nome_objeto, nome_amigavel, ISNULL(categoria, ''Geral'') AS categoria ' +
      'FROM USER_geoapolo_objetos WITH (NOLOCK) ' +
      'WHERE 1=1 ';

    if HasCat then
      SqlText := SqlText + 'AND UPPER(ISNULL(categoria, ''Geral'')) = UPPER(:categoria) ';

    if HasFiltro then
      SqlText := SqlText + 'AND (UPPER(nome_objeto) LIKE UPPER(:filtro) OR UPPER(nome_amigavel) LIKE UPPER(:filtro)) ';

    SqlText := SqlText + 'ORDER BY categoria ASC, nome_amigavel ASC, nome_objeto ASC';

    Q.SQL.Text := SqlText;

    if HasCat then
      Q.ParamByName('categoria').AsString := Trim(ACategoria);

    if HasFiltro then
      Q.ParamByName('filtro').AsString := '%' + Trim(AFiltro) + '%';

    Q.Open;
    SetLength(ALista, Q.RecordCount);
    Idx := 0;
    while not Q.Eof do
    begin
      ALista[Idx].NomeObjeto   := Q.FieldByName('nome_objeto').AsString;
      ALista[Idx].NomeAmigavel := Q.FieldByName('nome_amigavel').AsString;
      ALista[Idx].Categoria    := Q.FieldByName('categoria').AsString;
      Inc(Idx);
      Q.Next;
    end;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TNomesAmigaveisRepository.ObterObjeto(const ANomeObjeto: string;
  out ADados: TDadosObjetoAmigavel): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  ADados := Default(TDadosObjetoAmigavel);
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT nome_objeto, nome_amigavel, ISNULL(categoria, ''Geral'') AS categoria ' +
      'FROM USER_geoapolo_objetos WITH (NOLOCK) ' +
      'WHERE nome_objeto = :nomeobjeto';
    Q.ParamByName('nomeobjeto').AsString := Trim(ANomeObjeto);
    Q.Open;

    if not Q.IsEmpty then
    begin
      ADados.NomeObjeto   := Q.FieldByName('nome_objeto').AsString;
      ADados.NomeAmigavel := Q.FieldByName('nome_amigavel').AsString;
      ADados.Categoria    := Q.FieldByName('categoria').AsString;
      Result := True;
    end;
  finally
    Q.Free;
  end;
end;

function TNomesAmigaveisRepository.AtualizarNomeAmigavel(const ANomeObjeto,
  ANomeAmigavel, ACategoria: string): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'UPDATE USER_geoapolo_objetos ' +
      'SET nome_amigavel = :nomeamigavel, ' +
      '    categoria     = :categoria ' +
      'WHERE nome_objeto = :nomeobjeto';
    Q.ParamByName('nomeamigavel').AsString := Trim(ANomeAmigavel);
    Q.ParamByName('categoria').AsString    := Trim(ACategoria);
    Q.ParamByName('nomeobjeto').AsString   := Trim(ANomeObjeto);
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TNomesAmigaveisRepository.SalvarObjeto(
  const ADados: TDadosObjetoAmigavel): Boolean;
var
  Q: TFDQuery;
  Existe: Boolean;
begin
  Result := False;
  Q := CriarQuery;
  try
    Q.SQL.Text := 'SELECT 1 FROM USER_geoapolo_objetos WHERE nome_objeto = :nomeobjeto';
    Q.ParamByName('nomeobjeto').AsString := Trim(ADados.NomeObjeto);
    Q.Open;
    Existe := not Q.IsEmpty;
    Q.Close;

    if Existe then
    begin
      Q.SQL.Text :=
        'UPDATE USER_geoapolo_objetos ' +
        'SET nome_amigavel = :nomeamigavel, ' +
        '    categoria     = :categoria ' +
        'WHERE nome_objeto = :nomeobjeto';
    end
    else
    begin
      Q.SQL.Text :=
        'INSERT INTO USER_geoapolo_objetos (nome_objeto, nome_amigavel, categoria) ' +
        'VALUES (:nomeobjeto, :nomeamigavel, :categoria)';
    end;

    Q.ParamByName('nomeobjeto').AsString   := Trim(ADados.NomeObjeto);
    Q.ParamByName('nomeamigavel').AsString := Trim(ADados.NomeAmigavel);
    Q.ParamByName('categoria').AsString    := Trim(ADados.Categoria);
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

end.
