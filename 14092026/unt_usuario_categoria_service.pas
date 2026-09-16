unit unt_usuario_categoria_service;

interface

uses
  System.SysUtils, System.Classes, FireDAC.Comp.Client, FireDAC.DApt,
  Data.DB, Vcl.Grids, Vcl.ComCtrls, unt_dados; // Certifique-se que unt_dados tem a conexão FD

type
  TUsuarioCategoriaService = class
  private
    FQuery: TFDQuery;
  public
    constructor Create;
    destructor Destroy; override;

    procedure ListarCategoriasParaTree(ATree: TTreeView);
    procedure ListarUsuariosAtivos(AItems: TStrings);
    procedure CarregarGridVinculos(AUsuCod: string; AGrid: TObject);
    procedure AplicarVinculos(AUsuCod: string; ACategorias: TStringList);
    procedure RemoverVinculo(AUsuCod, ACategCod: string);
  end;

implementation

constructor TUsuarioCategoriaService.Create;
begin
  FQuery := TFDQuery.Create(nil);
  FQuery.Connection := modulo_dados.fdbanco; // Nome da sua FDConnection
end;

destructor TUsuarioCategoriaService.Destroy;
begin
  FQuery.Free;
  inherited;
end;


procedure TUsuarioCategoriaService.CarregarGridVinculos(AUsuCod: string; AGrid: TObject);
var
  Grid: TStringGrid;
  L: Integer;
begin
  Grid := TStringGrid(AGrid);
  // Limpa o Grid mantendo o cabeçalho
  Grid.RowCount := 2;
  Grid.Rows[0].Clear;

  FQuery.Close;
  FQuery.SQL.Text := 'SELECT usucod, categcodestr FROM usuario_categ WHERE usucod = :usu';
  FQuery.ParamByName('usu').AsString := AUsuCod;
  FQuery.Open;

  L := 1;
  while not FQuery.Eof do
  begin
    if L > 1 then Grid.RowCount := Grid.RowCount + 1;

    Grid.Cells[0, L] := FQuery.FieldByName('usucod').AsString;
    Grid.Cells[1, L] := FQuery.FieldByName('categcodestr').AsString;

    Inc(L);
    FQuery.Next;
  end;
end;

procedure TUsuarioCategoriaService.ListarUsuariosAtivos(AItems: TStrings);
begin
  AItems.BeginUpdate;
  try
    AItems.Clear;
    AItems.Add('');
    FQuery.Open('SELECT UsuCod FROM usuario WHERE UsuStat = ''Ativo'' ORDER BY UsuCod ASC');
    while not FQuery.Eof do
    begin
      AItems.Add(FQuery.FieldByName('UsuCod').AsString);
      FQuery.Next;
    end;
  finally
    AItems.EndUpdate;
  end;
end;

procedure TUsuarioCategoriaService.ListarCategoriasParaTree(ATree: TTreeView);
var
  Node: TTreeNode;
begin
  ATree.Items.BeginUpdate;
  try
    ATree.Items.Clear;
    FQuery.Open('SELECT CategCodEstr, CategNome, CategCodEstrNiv FROM categoria ORDER BY CategCodEstr ASC');

    while not FQuery.Eof do
    begin
      if FQuery.FieldByName('CategCodEstrNiv').AsString = '' then
        Node := ATree.Items.Add(nil, FQuery.FieldByName('CategCodEstr').AsString + ' - ' + FQuery.FieldByName('CategNome').AsString)
      else
        ATree.Items.AddChild(Node, FQuery.FieldByName('CategCodEstr').AsString + ' - ' + FQuery.FieldByName('CategNome').AsString);

      FQuery.Next;
    end;
  finally
    ATree.Items.EndUpdate;
  end;
end;

procedure TUsuarioCategoriaService.AplicarVinculos(AUsuCod: string; ACategorias: TStringList);
var
  i: Integer;
begin
  FQuery.Connection.StartTransaction;
  try
    for i := 0 to ACategorias.Count - 1 do
    begin
      // 1. Inserir/Atualizar Categoria do Usuário
      FQuery.SQL.Text := 'IF NOT EXISTS (SELECT 1 FROM usuario_categ WHERE usucod = :usu AND categcodestr = :cat) ' +
                         'INSERT INTO usuario_categ (usucod, categcodestr, UsuCategTodasEnt) VALUES (:usu, :cat, ''Sim'')';
      FQuery.Params.ParamByName('usu').AsString := AUsuCod;
      FQuery.Params.ParamByName('cat').AsString := ACategorias[i];
      FQuery.ExecSQL;

      // 2. Sincronizar Entidades da Categoria para o Usuário
      FQuery.SQL.Text := 'INSERT INTO usuario_ent (usucod, entcod, UsuEntRelacAvulso) ' +
                         'SELECT :usu, entcod, ''Não'' FROM ent_categ ' +
                         'WHERE categcodestr = :cat ' +
                         'AND entcod NOT IN (SELECT entcod FROM usuario_ent WHERE usucod = :usu)';
      FQuery.ExecSQL;
    end;
    FQuery.Connection.Commit;
  except
    FQuery.Connection.Rollback;
    raise;
  end;
end;

procedure TUsuarioCategoriaService.RemoverVinculo(AUsuCod, ACategCod: string);
begin
  FQuery.SQL.Text := 'DELETE FROM usuario_categ WHERE usucod = :usu AND categcodestr = :cat';
  FQuery.Params.ParamByName('usu').AsString := AUsuCod;
  FQuery.Params.ParamByName('cat').AsString := ACategCod;
  FQuery.ExecSQL;
end;

end.
