unit unt_usuario_categoria_entidade;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.ComCtrls, Vcl.StdCtrls, Vcl.Buttons,
  Vcl.ExtCtrls, Vcl.Grids, unt_usuario_categoria_service;

type
  Tfrmusuario_categ_entidade = class(TForm)
    cbousuarios: TComboBox;
    arvore: TTreeView;
    gridrelacionamento: TStringGrid;
    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure spbsairClick(Sender: TObject);
    procedure arvoreDblClick(Sender: TObject);
    procedure btnaplicarClick(Sender: TObject);  // <- mantenha só se implementar
  private
    FService: TUsuarioCategoriaService;
    procedure LimparGrid;
  public
  end;

var
  frmusuario_categ_entidade: Tfrmusuario_categ_entidade;

implementation

{$R *.dfm}

procedure Tfrmusuario_categ_entidade.FormCreate(Sender: TObject);
begin
  FService := TUsuarioCategoriaService.Create;
  LimparGrid;
end;

procedure Tfrmusuario_categ_entidade.FormDestroy(Sender: TObject);
begin
  FService.Free;
end;

procedure Tfrmusuario_categ_entidade.FormActivate(Sender: TObject);
begin
  try
    FService.ListarUsuariosAtivos(cbousuarios.Items);
    FService.ListarCategoriasParaTree(arvore);
  except
    on E: Exception do
      MessageDlg('Erro ao carregar dados: ' + E.Message, mtError, [mbOK], 0);
  end;
end;

procedure Tfrmusuario_categ_entidade.arvoreDblClick(Sender: TObject);
var
  S, Codigo: string;
begin
  if cbousuarios.Text = '' then
  begin
    MessageDlg('Selecione um usuário primeiro!', mtWarning, [mbOK], 0);
    Exit;
  end;
  S := arvore.Selected.Text;
  Codigo := Trim(Copy(S, 1, Pos('-', S) - 1));
  gridrelacionamento.RowCount := gridrelacionamento.RowCount + 1;
  gridrelacionamento.Cells[0, gridrelacionamento.RowCount - 1] := cbousuarios.Text;
  gridrelacionamento.Cells[1, gridrelacionamento.RowCount - 1] := Codigo;
end;

procedure Tfrmusuario_categ_entidade.btnaplicarClick(Sender: TObject);
var
  Categorias: TStringList;
  i: Integer;
begin
  Categorias := TStringList.Create;
  try
    for i := 1 to gridrelacionamento.RowCount - 1 do
      if gridrelacionamento.Cells[1, i] <> '' then
        Categorias.Add(gridrelacionamento.Cells[1, i]);
    FService.AplicarVinculos(cbousuarios.Text, Categorias);
    MessageDlg('Dados sincronizados com sucesso!', mtInformation, [mbOK], 0);
  finally
    Categorias.Free;
  end;
end;

procedure Tfrmusuario_categ_entidade.LimparGrid;
var
  i: Integer;
begin
  for i := 0 to gridrelacionamento.ColCount - 1 do
    gridrelacionamento.Cols[i].Clear;
  gridrelacionamento.RowCount := 2;
  gridrelacionamento.Cells[0, 0] := 'Usuário';   // coluna 0, linha 0
  gridrelacionamento.Cells[1, 0] := 'Categoria'; // coluna 1, linha 0
end;

procedure Tfrmusuario_categ_entidade.spbsairClick(Sender: TObject);
begin
  Close;
end;

end.
