unit unt_categoriaentidade_repository;

{
  Repositório FireDAC para Relacionamento de Usuários, Grupos, Categorias e Entidades.
  Garante persistência segura, queries parametrizadas e hints WITH (NOLOCK).
}

interface

uses
  System.SysUtils, System.Classes, Data.DB,
  FireDAC.Comp.Client, FireDAC.Stan.Param,
  unt_categoriaentidade_types;

type
  TCategoriaEntidadeRepository = class
  private
    FConn: TFDConnection;
  public
    constructor Create(AConnection: TFDConnection);

    // Listagens auxiliares
    function ListarUsuariosAtivos: TArray<TUsuarioItemDTO>;
    function ListarGrupos: TArray<TGrupoItemDTO>;
    function ListarUsuariosDoGrupo(const AGrupoID: string): TArray<string>;

    // Consultas de Categorias e Vínculos
    function ListarCategoriasDoUsuario(const AUsuarioID: string): TArray<TCategoriaResumoDTO>;
    function ListarCategoriasDoGrupo(const AGrupoID: string): TArray<TCategoriaResumoDTO>;

    // Operações de Vínculo e Desvínculo
    function VincularCategoriaUsuario(const AUsuarioID, ACategCod: string): TOperacaoResultado;
    function RelacionarEntidadesCategoriaUsuario(const AUsuarioID, ACategCod: string): TOperacaoResultado;
    function RemoverCategoriaUsuario(const AUsuarioID, ACategCod: string): TOperacaoResultado;
  end;

implementation

constructor TCategoriaEntidadeRepository.Create(AConnection: TFDConnection);
begin
  inherited Create;
  FConn := AConnection;
end;

function TCategoriaEntidadeRepository.ListarUsuariosAtivos: TArray<TUsuarioItemDTO>;
var
  Qry: TFDQuery;
  Lista: TArray<TUsuarioItemDTO>;
  Item: TUsuarioItemDTO;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT usucod, ISNULL(usunome, usucod) AS usunome ' +
                    'FROM usuario WITH (NOLOCK) ' +
                    'WHERE UsuStat = ''Ativo'' ' +
                    'ORDER BY usucod ASC';
    Qry.Open;
    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Item.Codigo := Qry.FieldByName('usucod').AsString;
      Item.Nome   := Qry.FieldByName('usunome').AsString;
      Lista[Count] := Item;
      Inc(Count);
      Qry.Next;
    end;
    Result := Lista;
  finally
    Qry.Free;
  end;
end;

function TCategoriaEntidadeRepository.ListarGrupos: TArray<TGrupoItemDTO>;
var
  Qry: TFDQuery;
  Lista: TArray<TGrupoItemDTO>;
  Item: TGrupoItemDTO;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT GrpUsuCod, ISNULL(GrpUsuNome, GrpUsuCod) AS GrpUsuNome ' +
                    'FROM grp_usuario WITH (NOLOCK) ' +
                    'ORDER BY GrpUsuCod ASC';
    Qry.Open;
    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Item.Codigo    := Qry.FieldByName('GrpUsuCod').AsString;
      Item.Descricao := Qry.FieldByName('GrpUsuNome').AsString;
      Lista[Count] := Item;
      Inc(Count);
      Qry.Next;
    end;
    Result := Lista;
  finally
    Qry.Free;
  end;
end;

function TCategoriaEntidadeRepository.ListarUsuariosDoGrupo(const AGrupoID: string): TArray<string>;
var
  Qry: TFDQuery;
  Lista: TArray<string>;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT gu.usucod ' +
                    'FROM grp_x_usuario gu WITH (NOLOCK) ' +
                    'INNER JOIN usuario u WITH (NOLOCK) ON gu.usucod = u.usucod ' +
                    'WHERE gu.grpusucod = :grupo ' +
                    'ORDER BY gu.usucod ASC';
    Qry.ParamByName('grupo').AsString := AGrupoID;
    Qry.Open;
    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Lista[Count] := Qry.FieldByName('usucod').AsString;
      Inc(Count);
      Qry.Next;
    end;
    Result := Lista;
  finally
    Qry.Free;
  end;
end;

function TCategoriaEntidadeRepository.ListarCategoriasDoUsuario(const AUsuarioID: string): TArray<TCategoriaResumoDTO>;
var
  Qry: TFDQuery;
  Lista: TArray<TCategoriaResumoDTO>;
  Item: TCategoriaResumoDTO;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    // Lista todas as categorias e marca quais estão vinculadas ao usuário
    Qry.SQL.Text := 'SELECT ' +
                    '  c.categcodestr, ' +
                    '  ISNULL(c.categnome, c.categcodestr) AS categnome, ' +
                    '  (SELECT COUNT(ec.entcod) FROM entidade_categ ec WITH (NOLOCK) WHERE ec.categcodestr = c.categcodestr) AS total_entidades, ' +
                    '  CASE WHEN uc.categcodestr IS NOT NULL THEN 1 ELSE 0 END AS vinculada ' +
                    'FROM categoria c WITH (NOLOCK) ' +
                    'LEFT JOIN usuario_categ uc WITH (NOLOCK) ' +
                    '       ON c.categcodestr = uc.categcodestr AND uc.usucod = :usu ' +
                    'ORDER BY c.categcodestr ASC';
    Qry.ParamByName('usu').AsString := AUsuarioID;
    Qry.Open;
    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Item.CodigoCategoria := Qry.FieldByName('categcodestr').AsString;
      Item.Descricao       := Qry.FieldByName('categnome').AsString;
      Item.TotalEntidades  := Qry.FieldByName('total_entidades').AsInteger;
      Item.Vinculada       := Qry.FieldByName('vinculada').AsInteger = 1;
      Lista[Count] := Item;
      Inc(Count);
      Qry.Next;
    end;
    Result := Lista;
  finally
    Qry.Free;
  end;
end;

function TCategoriaEntidadeRepository.ListarCategoriasDoGrupo(const AGrupoID: string): TArray<TCategoriaResumoDTO>;
var
  Usuarios: TArray<string>;
begin
  // Para grupos, lista categorias baseando-se nos usuários membros do grupo
  Usuarios := ListarUsuariosDoGrupo(AGrupoID);
  if Length(Usuarios) > 0 then
    Result := ListarCategoriasDoUsuario(Usuarios[0])
  else
    Result := ListarCategoriasDoUsuario('');
end;

function TCategoriaEntidadeRepository.VincularCategoriaUsuario(const AUsuarioID, ACategCod: string): TOperacaoResultado;
var
  Qry: TFDQuery;
  Existe: Boolean;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;

    Qry.SQL.Text := 'SELECT COUNT(*) FROM usuario_categ WITH (NOLOCK) WHERE usucod = :usu AND categcodestr = :cat';
    Qry.ParamByName('usu').AsString := AUsuarioID;
    Qry.ParamByName('cat').AsString := ACategCod;
    Qry.Open;
    Existe := Qry.Fields[0].AsInteger > 0;
    Qry.Close;

    if not Existe then
    begin
      Qry.SQL.Text := 'INSERT INTO usuario_categ (usucod, categcodestr, UsuCategTodasEnt) VALUES (:usu, :cat, ''N'')';
      Qry.ParamByName('usu').AsString := AUsuarioID;
      Qry.ParamByName('cat').AsString := ACategCod;
      Qry.ExecSQL;
    end;

    Result.Sucesso  := True;
    Result.Mensagem := 'Categoria vinculada ao usuário com sucesso!';
    Result.Codigo   := ACategCod;
  except
    on E: Exception do
    begin
      Result.Sucesso  := False;
      Result.Mensagem := 'Falha ao vincular categoria: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TCategoriaEntidadeRepository.RelacionarEntidadesCategoriaUsuario(const AUsuarioID, ACategCod: string): TOperacaoResultado;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;

    // Garante primeiro o vínculo da categoria
    VincularCategoriaUsuario(AUsuarioID, ACategCod);

    // Insere no relacionamento usuário x entidade todas as entidades da categoria que ainda não estejam vinculadas
    Qry.SQL.Text := 'INSERT INTO usuario_ent (UsuCod, EntCod, UsuEntRelacAvulso) ' +
                    'SELECT :usu, ec.entcod, ''N'' ' +
                    'FROM entidade_categ ec WITH (NOLOCK) ' +
                    'WHERE ec.categcodestr = :cat ' +
                    '  AND NOT EXISTS ( ' +
                    '      SELECT 1 FROM usuario_ent ue WITH (NOLOCK) ' +
                    '      WHERE ue.usucod = :usu AND ue.entcod = ec.entcod ' +
                    '  )';
    Qry.ParamByName('usu').AsString := AUsuarioID;
    Qry.ParamByName('cat').AsString := ACategCod;
    Qry.ExecSQL;

    Result.Sucesso  := True;
    Result.Mensagem := 'Todas as entidades da categoria foram vinculadas ao usuário com sucesso!';
    Result.Codigo   := ACategCod;
  except
    on E: Exception do
    begin
      Result.Sucesso  := False;
      Result.Mensagem := 'Falha ao relacionar entidades: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TCategoriaEntidadeRepository.RemoverCategoriaUsuario(const AUsuarioID, ACategCod: string): TOperacaoResultado;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;

    // Remove entidades vinculadas via essa categoria
    Qry.SQL.Text := 'DELETE FROM usuario_ent ' +
                    'WHERE usucod = :usu ' +
                    '  AND entcod IN (SELECT ec.entcod FROM entidade_categ ec WITH (NOLOCK) WHERE ec.categcodestr = :cat)';
    Qry.ParamByName('usu').AsString := AUsuarioID;
    Qry.ParamByName('cat').AsString := ACategCod;
    Qry.ExecSQL;

    // Remove categoria do usuário
    Qry.SQL.Text := 'DELETE FROM usuario_categ WHERE usucod = :usu AND categcodestr = :cat';
    Qry.ParamByName('usu').AsString := AUsuarioID;
    Qry.ParamByName('cat').AsString := ACategCod;
    Qry.ExecSQL;

    Result.Sucesso  := True;
    Result.Mensagem := 'Relacionamento da categoria removido com sucesso!';
    Result.Codigo   := ACategCod;
  except
    on E: Exception do
    begin
      Result.Sucesso  := False;
      Result.Mensagem := 'Falha ao remover relacionamento: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

end.
