unit unt_relacionadioceseentidade_repository;

interface

uses
  System.SysUtils, System.Classes, System.Generics.Collections,
  FireDAC.Comp.Client, FireDAC.Stan.Param, Data.DB,
  unt_relacionadioceseentidade_types;

type
  IRelacionaDioceseEntidadeRepository = interface
    ['{E3C2B814-6F29-4A73-98D1-C78C9E74A532}']
    function ListarEntidades(const AFiltro: TFiltroEntidadeDioceseDTO): TList<TEntidadeDioceseDTO>;
    function BuscarEntidadePorCodigo(const AEntCod: string; out AEntidade: TEntidadeDioceseDTO): Boolean;
    function BuscarDiocesePorCidade(const ADioceseId, ACidade: string): string;
    function ListarDiocesesPorEstadoECidade(const AUFSigla, ACidade: string): TList<TDioceseCNBBDTO>;
    function ObterEstadoCNBBId(const AUFSigla: string): string;
    function VincularDiocese(const AEntCod, ADioceseId, ANomeDiocese: string): Boolean;
    function DesvincularDiocese(const AEntCod: string): Boolean;
  end;

  TRelacionaDioceseEntidadeRepositoryFireDAC = class(TInterfacedObject, IRelacionaDioceseEntidadeRepository)
  private
    FConexao: TFDConnection;
    function ExisteUEntidade(const AEntCod: string): Boolean;
  public
    constructor Create(AConexao: TFDConnection);
    function ListarEntidades(const AFiltro: TFiltroEntidadeDioceseDTO): TList<TEntidadeDioceseDTO>;
    function BuscarEntidadePorCodigo(const AEntCod: string; out AEntidade: TEntidadeDioceseDTO): Boolean;
    function BuscarDiocesePorCidade(const ADioceseId, ACidade: string): string;
    function ListarDiocesesPorEstadoECidade(const AUFSigla, ACidade: string): TList<TDioceseCNBBDTO>;
    function ObterEstadoCNBBId(const AUFSigla: string): string;
    function VincularDiocese(const AEntCod, ADioceseId, ANomeDiocese: string): Boolean;
    function DesvincularDiocese(const AEntCod: string): Boolean;
  end;

implementation

{ TRelacionaDioceseEntidadeRepositoryFireDAC }

constructor TRelacionaDioceseEntidadeRepositoryFireDAC.Create(AConexao: TFDConnection);
begin
  inherited Create;
  FConexao := AConexao;
end;

function TRelacionaDioceseEntidadeRepositoryFireDAC.ExisteUEntidade(const AEntCod: string): Boolean;
var
  Qry: TFDQuery;
begin
  Result := False;
  if (FConexao = nil) or (Trim(AEntCod) = '') then
    Exit;

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    Qry.SQL.Text := 'SELECT entcod FROM u_entidade WITH(NOLOCK) WHERE entcod = :entcod';
    Qry.ParamByName('entcod').AsString := AEntCod;
    Qry.Open;
    Result := not Qry.IsEmpty;
  finally
    Qry.Free;
  end;
end;

function TRelacionaDioceseEntidadeRepositoryFireDAC.ListarEntidades(
  const AFiltro: TFiltroEntidadeDioceseDTO): TList<TEntidadeDioceseDTO>;
var
  Qry: TFDQuery;
  SQLText: string;
  Item: TEntidadeDioceseDTO;
begin
  Result := TList<TEntidadeDioceseDTO>.Create;
  if FConexao = nil then
    Exit;

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    SQLText :=
      'SELECT e.entcod, e.entnome, e.cidcod, cid.cidnomecomp, cid.ufsigla, ' +
      '       e1.USERDiocese_id, e1.USERNomeDiocese, e1.USERJanaSVE ' +
      'FROM entidade e WITH(NOLOCK) ' +
      'INNER JOIN ent_categ ec WITH(NOLOCK) ON e.entcod = ec.entcod ' +
      'INNER JOIN cidade cid WITH(NOLOCK) ON e.cidcod = cid.cidcod ' +
      'LEFT JOIN u_entidade e1 WITH(NOLOCK) ON e.entcod = e1.entcod ' +
      'WHERE SUBSTRING(ec.categcodestr, 1, 6) IN (''02.001'', ''02.002'', ''03.001'', ''03.002'', ''03.003'', ''03.004'', ''03.005'') ' +
      '  AND e.entdesdedata BETWEEN :dt_ini AND :dt_fim ';

    if AFiltro.ApenasSemDiocese then
    begin
      SQLText := SQLText + '  AND (e1.USERDiocese_id IS NULL OR RTRIM(e1.USERDiocese_id) = '''') ';
    end;

    SQLText := SQLText + 'ORDER BY e.entcod ASC';

    Qry.SQL.Text := SQLText;
    Qry.ParamByName('dt_ini').AsDateTime := AFiltro.DataInicial;
    Qry.ParamByName('dt_fim').AsDateTime := AFiltro.DataFinal;
    Qry.Open;

    while not Qry.Eof do
    begin
      Item.EntCod := Qry.FieldByName('entcod').AsString;
      Item.EntNome := Qry.FieldByName('entnome').AsString;
      Item.CidCod := Qry.FieldByName('cidcod').AsString;
      Item.CidNomeComp := Qry.FieldByName('cidnomecomp').AsString;
      Item.UFSigla := Qry.FieldByName('ufsigla').AsString;
      Item.USERDioceseId := Qry.FieldByName('USERDiocese_id').AsString;
      Item.USERNomeDiocese := Qry.FieldByName('USERNomeDiocese').AsString;
      Item.USERJanaSVE := Qry.FieldByName('USERJanaSVE').AsString;
      Result.Add(Item);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
end;

function TRelacionaDioceseEntidadeRepositoryFireDAC.BuscarEntidadePorCodigo(
  const AEntCod: string; out AEntidade: TEntidadeDioceseDTO): Boolean;
var
  Qry: TFDQuery;
begin
  Result := False;
  AEntidade := Default(TEntidadeDioceseDTO);
  if (FConexao = nil) or (Trim(AEntCod) = '') then
    Exit;

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    Qry.SQL.Text :=
      'SELECT e.entcod, e.entnome, e.cidcod, cid.cidnomecomp, cid.ufsigla, ' +
      '       e1.USERDiocese_id, e1.USERNomeDiocese, e1.USERJanaSVE ' +
      'FROM entidade e WITH(NOLOCK) ' +
      'INNER JOIN cidade cid WITH(NOLOCK) ON e.cidcod = cid.cidcod ' +
      'LEFT JOIN u_entidade e1 WITH(NOLOCK) ON e.entcod = e1.entcod ' +
      'WHERE e.entcod = :entcod';
    Qry.ParamByName('entcod').AsString := AEntCod;
    Qry.Open;

    if not Qry.IsEmpty then
    begin
      AEntidade.EntCod := Qry.FieldByName('entcod').AsString;
      AEntidade.EntNome := Qry.FieldByName('entnome').AsString;
      AEntidade.CidCod := Qry.FieldByName('cidcod').AsString;
      AEntidade.CidNomeComp := Qry.FieldByName('cidnomecomp').AsString;
      AEntidade.UFSigla := Qry.FieldByName('ufsigla').AsString;
      AEntidade.USERDioceseId := Qry.FieldByName('USERDiocese_id').AsString;
      AEntidade.USERNomeDiocese := Qry.FieldByName('USERNomeDiocese').AsString;
      AEntidade.USERJanaSVE := Qry.FieldByName('USERJanaSVE').AsString;
      Result := True;
    end;
  finally
    Qry.Free;
  end;
end;

function TRelacionaDioceseEntidadeRepositoryFireDAC.BuscarDiocesePorCidade(
  const ADioceseId, ACidade: string): string;
var
  Qry: TFDQuery;
begin
  Result := 'NÃO ENCONTRADO';
  if FConexao = nil then
    Exit;

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    Qry.SQL.Text :=
      'SELECT dio.id, dio.nome, cidcnbb.descricao, estcnbb.usersigla ' +
      'FROM USERdioceses_CNBB dio WITH(NOLOCK) ' +
      'INNER JOIN USERcidades_CNBB cidcnbb WITH(NOLOCK) ON dio.id = cidcnbb.diocese_id ' +
      'INNER JOIN USEREstado_CNBB estcnbb WITH(NOLOCK) ON cidcnbb.estado_id = estcnbb.USERiD ' +
      'WHERE dio.id = :dioceseid AND cidcnbb.descricao = :cidadecnbb';
    Qry.ParamByName('dioceseid').AsString := ADioceseId;
    Qry.ParamByName('cidadecnbb').AsString := ACidade;
    Qry.Open;

    if not Qry.IsEmpty then
      Result := Qry.FieldByName('descricao').AsString + '/' + Qry.FieldByName('usersigla').AsString;
  finally
    Qry.Free;
  end;
end;

function TRelacionaDioceseEntidadeRepositoryFireDAC.ObterEstadoCNBBId(const AUFSigla: string): string;
var
  Qry: TFDQuery;
begin
  Result := '';
  if FConexao = nil then
    Exit;

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    Qry.SQL.Text := 'SELECT USERid FROM USEREstado_CNBB WITH(NOLOCK) WHERE usersigla = :uf';
    Qry.ParamByName('uf').AsString := AUFSigla;
    Qry.Open;
    if not Qry.IsEmpty then
      Result := Qry.FieldByName('USERid').AsString;
  finally
    Qry.Free;
  end;
end;

function TRelacionaDioceseEntidadeRepositoryFireDAC.ListarDiocesesPorEstadoECidade(
  const AUFSigla, ACidade: string): TList<TDioceseCNBBDTO>;
var
  Qry: TFDQuery;
  Item: TDioceseCNBBDTO;
  EstadoId: string;
begin
  Result := TList<TDioceseCNBBDTO>.Create;
  if FConexao = nil then
    Exit;

  EstadoId := ObterEstadoCNBBId(AUFSigla);

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    Qry.SQL.Text :=
      'SELECT DISTINCT dio.id, dio.estado_id, dio.nome, estado.usersigla, estado.usernome_estado, uccnbb.descricao ' +
      'FROM USERdioceses_CNBB dio WITH(NOLOCK) ' +
      'INNER JOIN USEREstado_CNBB estado WITH(NOLOCK) ON dio.estado_id = estado.USERid ' +
      'INNER JOIN USERcidades_CNBB uccnbb WITH(NOLOCK) ON dio.id = uccnbb.diocese_id ' +
      'WHERE (estado.usersigla = :uf OR :uf = '''') ' +
      '  AND (uccnbb.descricao LIKE :cidade OR :cidade = '''') ' +
      'ORDER BY dio.nome, uccnbb.descricao';
    Qry.ParamByName('uf').AsString := AUFSigla;
    if Trim(ACidade) <> '' then
      Qry.ParamByName('cidade').AsString := '%' + ACidade + '%'
    else
      Qry.ParamByName('cidade').AsString := '';
    Qry.Open;

    while not Qry.Eof do
    begin
      Item.Id := Qry.FieldByName('id').AsString;
      Item.EstadoId := Qry.FieldByName('estado_id').AsString;
      Item.Nome := Qry.FieldByName('nome').AsString;
      Item.DescricaoCidade := Qry.FieldByName('descricao').AsString;
      Item.UFSigla := Qry.FieldByName('usersigla').AsString;
      Item.NomeEstado := Qry.FieldByName('usernome_estado').AsString;
      Result.Add(Item);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
end;

function TRelacionaDioceseEntidadeRepositoryFireDAC.VincularDiocese(
  const AEntCod, ADioceseId, ANomeDiocese: string): Boolean;
var
  Qry: TFDQuery;
begin
  Result := False;
  if (FConexao = nil) or (Trim(AEntCod) = '') then
    Exit;

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    if ExisteUEntidade(AEntCod) then
    begin
      Qry.SQL.Text :=
        'UPDATE u_entidade SET USERDiocese_id = :dioceseid, USERNomeDiocese = :nomediocese ' +
        'WHERE entcod = :entcod';
    end
    else
    begin
      Qry.SQL.Text :=
        'INSERT INTO u_entidade (entcod, USERDiocese_id, USERNomeDiocese) ' +
        'VALUES (:entcod, :dioceseid, :nomediocese)';
    end;

    Qry.ParamByName('entcod').AsString := AEntCod;
    Qry.ParamByName('dioceseid').AsString := ADioceseId;
    Qry.ParamByName('nomediocese').AsString := ANomeDiocese;
    Qry.ExecSQL;
    Result := True;
  except
    Result := False;
  end;
  Qry.Free;
end;

function TRelacionaDioceseEntidadeRepositoryFireDAC.DesvincularDiocese(const AEntCod: string): Boolean;
var
  Qry: TFDQuery;
begin
  Result := False;
  if (FConexao = nil) or (Trim(AEntCod) = '') then
    Exit;

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    if ExisteUEntidade(AEntCod) then
    begin
      Qry.SQL.Text :=
        'UPDATE u_entidade SET USERDiocese_id = NULL, USERNomeDiocese = NULL ' +
        'WHERE entcod = :entcod';
      Qry.ParamByName('entcod').AsString := AEntCod;
      Qry.ExecSQL;
    end;
    Result := True;
  except
    Result := False;
  end;
  Qry.Free;
end;

end.
