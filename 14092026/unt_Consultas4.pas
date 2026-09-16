unit unt_consultas4;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Classes, Data.DB,
  FireDAC.Comp.Client, FireDAC.Stan.Param, FireDAC.Stan.Error,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.StdCtrls,
  Vcl.ExtCtrls, Vcl.DBGrids, Vcl.Grids, System.UITypes;

type
  TFrmConsulta4 = class(TForm)
    pnlTopo: TPanel;
    lblTitulo: TLabel;
    lblFiltro: TLabel;
    edtFiltro: TEdit;
    DBGrid1: TDBGrid;
    DataSource1: TDataSource;
    pnlRodape: TPanel;
    btnOK: TButton;
    btnCancelar: TButton;

    procedure FormCreate(Sender: TObject);
    procedure FormKeyDown(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure btnCancelarClick(Sender: TObject);
    procedure btnOKClick(Sender: TObject);
    procedure DBGrid1DblClick(Sender: TObject);
    procedure edtFiltroChange(Sender: TObject);
    procedure FormShow(Sender: TObject);

  private
    FMemTable       : TFDMemTable;
    FCampoCodigo    : string;
    FCampoDescricao : string;
    FCodigoSel      : string;
    FDescricaoSel   : string;
    FCamposExtras   : TStringList;

    procedure FMemTableFilterRecord(DataSet: TDataSet; var Accept: Boolean); // <-- adicionar
    procedure CriarDatasets;
    procedure AplicarFiltro(const ATexto: string);
    procedure CapturarSelecao;
    procedure ConfigurarColunasGrid;

    function  GetTitulo: string;
    procedure SetTitulo(const Value: string);

  public
    constructor Create(AOwner: TComponent); override;
    destructor  Destroy; override;

    procedure PopularGrid(
      ASource         : TDataSet;
      const ACampoCodigo    : string;
      const ACampoDescricao : string
    );

    function GetCampoExtra(const ANomeCampo: string): string;

    property CodigoSelecionado   : string read FCodigoSel;
    property DescricaoSelecionada: string read FDescricaoSel;
    property Titulo              : string read GetTitulo write SetTitulo;
  end;

implementation

{$R *.dfm}

{ ========================= CONSTRUCTOR/DESTRUCTOR ========================= }

constructor TFrmConsulta4.Create(AOwner: TComponent);
begin
  inherited Create(AOwner);
  FCamposExtras := TStringList.Create;
end;

destructor TFrmConsulta4.Destroy;
begin
  FCamposExtras.Free;
  inherited Destroy;
end;

{ ========================= FORM ========================= }

procedure TFrmConsulta4.FormCreate(Sender: TObject);
begin
  KeyPreview    := True;
  FCodigoSel    := '';
  FDescricaoSel := '';
  CriarDatasets;
end;

procedure TFrmConsulta4.FormShow(Sender: TObject);
begin
  edtFiltro.SetFocus;
end;

procedure TFrmConsulta4.FormKeyDown(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  case Key of
    VK_RETURN : btnOKClick(Sender);
    VK_ESCAPE : btnCancelarClick(Sender);
    VK_UP, VK_DOWN:
      if ActiveControl <> DBGrid1 then
      begin
        DBGrid1.SetFocus;
        SendMessage(DBGrid1.Handle, WM_KEYDOWN, Key, 0);
      end;
  end;
end;

{ ========================= DATASETS ========================= }

procedure TFrmConsulta4.CriarDatasets;
begin
  FMemTable                    := TFDMemTable.Create(Self);
  FMemTable.OnFilterRecord     := FMemTableFilterRecord; // <-- vincula aqui
  FMemTable.FetchOptions.Unidirectional := False;
  DataSource1.DataSet          := FMemTable;
  DBGrid1.DataSource           := DataSource1;
end;

{ ========================= POPULAR GRID ========================= }

procedure TFrmConsulta4.PopularGrid(ASource: TDataSet; const ACampoCodigo, ACampoDescricao: string);
begin
  FCampoCodigo    := ACampoCodigo;
  FCampoDescricao := ACampoDescricao;

  FMemTable.Close;
  FMemTable.FieldDefs.Clear;
  FMemTable.FieldDefs.Assign(ASource.FieldDefs);
  FMemTable.CreateDataSet;

  ASource.First;
  FMemTable.DisableControls;
  try
    while not ASource.Eof do
    begin
      FMemTable.Append;
      // Copia campo a campo para evitar incompatibilidade de estrutura
      var i: Integer;
      for i := 0 to ASource.FieldCount - 1 do
      begin
        if not FMemTable.Fields[i].ReadOnly then
          FMemTable.Fields[i].Value := ASource.Fields[i].Value;
      end;
      FMemTable.Post;
      ASource.Next;
    end;
  finally
    FMemTable.EnableControls;
  end;

  FMemTable.First;
  ConfigurarColunasGrid;
end;

procedure TFrmConsulta4.ConfigurarColunasGrid;
begin
  DBGrid1.Columns.Clear;

  with DBGrid1.Columns.Add do
  begin
    FieldName     := FCampoCodigo;
    Title.Caption := 'Código';
    Width         := 80;
  end;

  with DBGrid1.Columns.Add do
  begin
    FieldName     := FCampoDescricao;
    Title.Caption := 'Descrição';
    Width         := 400;
  end;

  DBGrid1.ReadOnly := True;
end;


{ ========================= FILTRO ========================= }
procedure TFrmConsulta4.AplicarFiltro(const ATexto: string);
begin
  FMemTable.Filtered       := False;
  FMemTable.OnFilterRecord := nil;

  if Trim(ATexto) = '' then
    Exit;

  FMemTable.First;
  FMemTable.Filtered := True;
end; // <-- fecha AplicarFiltro

procedure TFrmConsulta4.FMemTableFilterRecord(DataSet: TDataSet; var Accept: Boolean);
var
  i   : Integer;
  txt : string;
begin
  txt    := UpperCase(Trim(edtFiltro.Text)); // lê direto do campo
  Accept := False;
  for i := 0 to DataSet.FieldCount - 1 do
  begin
    try
      if Pos(txt, UpperCase(DataSet.Fields[i].AsString)) > 0 then
      begin
        Accept := True;
        Break;
      end;
    except
      // campo não conversível — ignora
    end;
  end;
end;

procedure TFrmConsulta4.edtFiltroChange(Sender: TObject);
begin
  AplicarFiltro(edtFiltro.Text);
end;

{ ========================= SELEÇÃO ========================= }
procedure TFrmConsulta4.CapturarSelecao;
var
  i   : Integer;
  fld : TField;
begin
  FMemTable.Filtered := False;
  FCamposExtras.Clear;
  FCodigoSel    := '';
  FDescricaoSel := '';

  if FMemTable.IsEmpty then
    Exit;

  FCodigoSel    := FMemTable.FieldByName(FCampoCodigo).AsString;
  FDescricaoSel := FMemTable.FieldByName(FCampoDescricao).AsString;

  for i := 0 to FMemTable.FieldCount - 1 do
  begin
    fld := FMemTable.Fields[i];
    FCamposExtras.Values[fld.FieldName] := fld.AsString;
  end;
end;

{ ========================= GET CAMPO EXTRA ========================= }

function TFrmConsulta4.GetCampoExtra(const ANomeCampo: string): string;
begin
  Result := FCamposExtras.Values[ANomeCampo];
end;

{ ========================= BOTÕES ========================= }

procedure TFrmConsulta4.btnOKClick(Sender: TObject);
begin
  CapturarSelecao;

  if FCodigoSel = '' then
  begin
    MessageDlg('Por favor, selecione um registro.', mtInformation, [mbOK], 0);
    Exit;
  end;

  ModalResult := mrOK;
end;

procedure TFrmConsulta4.btnCancelarClick(Sender: TObject);
begin
  ModalResult := mrCancel;
end;

procedure TFrmConsulta4.DBGrid1DblClick(Sender: TObject);
begin
  btnOKClick(Sender);
end;

{ ========================= TÍTULO ========================= }

function TFrmConsulta4.GetTitulo: string;
begin
  Result := lblTitulo.Caption;
end;

procedure TFrmConsulta4.SetTitulo(const Value: string);
begin
  lblTitulo.Caption := Value;
  Self.Caption      := Value;
end;

end.
