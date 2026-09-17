unit unt_cadcores;

interface

uses
  Winapi.Windows, Winapi.Messages,
  System.SysUtils, System.Classes, System.Generics.Collections,
  Vcl.Graphics, Vcl.Controls, Vcl.Forms, Vcl.Dialogs,
  Vcl.StdCtrls, Vcl.ExtCtrls, Vcl.Buttons, Vcl.ComCtrls, Vcl.Grids,
  FireDAC.Comp.Client, FireDAC.Stan.Param, Vcl.Mask,
  unt_cadcores_types, unt_cadcores_repository, unt_cadcores_service;
type
  TModoEdicao = (moInclusao, moAlteracao);

  { MODEL }
  TCor = class
  private
    FCodigo: Integer;
    FDescricao: string;
  public
    property Codigo: Integer read FCodigo write FCodigo;
    property Descricao: string read FDescricao write FDescricao;
  end;

  { REPOSITORY }
  TCorRepository = class
  private
    FConn: TFDConnection;
    function CriarQuery: TFDQuery;
  public
    constructor Create(AConn: TFDConnection);
    function Listar: TFDQuery;
    function ExisteDescricao(const ADescricao: string; ACodigoIgnorar: Integer = 0): Boolean;
    function ObterProximoCodigo: Integer; // Movido para o repositório
    procedure Inserir(ACor: TCor);
    procedure Alterar(ACor: TCor);
    procedure Excluir(ACodigo: Integer);
  end;

  Tfrmcadcores = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spbsair: TSpeedButton;
    spblimpar: TSpeedButton;
    spbexcluir: TSpeedButton;
    GroupBox1: TGroupBox;
    lblcodcor: TLabeledEdit;
    lbldescricao: TLabeledEdit;
    gridcores: TStringGrid;
    StatusBar1: TStatusBar;
    lblsair: TLabel;
    procedure FormDestroy(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure spbsairClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure spbsalvarClick(Sender: TObject);
    procedure spbexcluirClick(Sender: TObject);
    procedure gridcoresDblClick(Sender: TObject);
    procedure gridcoresKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lbldescricaoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
  private
    FRepositorio: TCorRepository;
    FModo: TModoEdicao;
    procedure ConfigurarGrid;
    procedure CarregarGrid;
    procedure LimparCampos;
    procedure NovoRegistro;
    procedure CarregarRegistroGrid;
    function CodigoAtual: Integer;
    function DescricaoAtual: string;
  public
  end;

var
  frmcadcores: Tfrmcadcores;

implementation

{$R *.dfm}

uses unt_dados; // Removi unt_principal se não for usada aqui para evitar circularidade

{ TCorRepository }

constructor TCorRepository.Create(AConn: TFDConnection);
begin
  inherited Create;
  FConn := AConn;
end;

function TCorRepository.CriarQuery: TFDQuery;
begin
  Result := TFDQuery.Create(nil);
  if Assigned(FConn) then
    Result.Connection := FConn
  else
    raise Exception.Create('Conexão com o banco de dados não informada no Repositório.');
end;

function TCorRepository.ObterProximoCodigo: Integer;
var
  Qry: TFDQuery;
begin
  Qry := CriarQuery;
  try
    Qry.SQL.Text := 'SELECT ISNULL(MAX(codigo_cor),0) + 1 AS proximo FROM USER_geoapolo_produto_cores';
    Qry.Open;
    Result := Qry.FieldByName('proximo').AsInteger;
  finally
    Qry.Free;
  end;
end;

function TCorRepository.Listar: TFDQuery;
begin
  Result := CriarQuery;
  Result.SQL.Text := 'SELECT codigo_cor, descricao_cor FROM USER_geoapolo_produto_cores ORDER BY codigo_cor';
  Result.Open;
end;

function TCorRepository.ExisteDescricao(const ADescricao: string; ACodigoIgnorar: Integer): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := CriarQuery;
  try
    Qry.SQL.Text := 'SELECT 1 FROM USER_geoapolo_produto_cores ' +
                    'WHERE descricao_cor = :descricao AND codigo_cor <> :codigo';
    Qry.ParamByName('descricao').AsString := Trim(ADescricao);
    Qry.ParamByName('codigo').AsInteger := ACodigoIgnorar;
    Qry.Open;
    Result := not Qry.IsEmpty;
  finally
    Qry.Free;
  end;
end;

procedure TCorRepository.Inserir(ACor: TCor);
var
  Qry: TFDQuery;
begin
  Qry := CriarQuery;
  try
    Qry.SQL.Text := 'INSERT INTO USER_geoapolo_produto_cores (codigo_cor, descricao_cor) VALUES (:codigo, :descricao)';
    Qry.ParamByName('codigo').AsInteger := ACor.Codigo;
    Qry.ParamByName('descricao').AsString := ACor.Descricao;
    Qry.ExecSQL;
  finally
    Qry.Free;
  end;
end;

procedure TCorRepository.Alterar(ACor: TCor);
var
  Qry: TFDQuery;
begin
  Qry := CriarQuery;
  try
    Qry.SQL.Text := 'UPDATE USER_geoapolo_produto_cores SET descricao_cor = :descricao WHERE codigo_cor = :codigo';
    Qry.ParamByName('codigo').AsInteger := ACor.Codigo;
    Qry.ParamByName('descricao').AsString := ACor.Descricao;
    Qry.ExecSQL;
  finally
    Qry.Free;
  end;
end;

procedure TCorRepository.Excluir(ACodigo: Integer);
var
  Qry: TFDQuery;
begin
  Qry := CriarQuery;
  try
    Qry.SQL.Text := 'DELETE FROM USER_geoapolo_produto_cores WHERE codigo_cor = :codigo';
    Qry.ParamByName('codigo').AsInteger := ACodigo;
    Qry.ExecSQL;
  finally
    Qry.Free;
  end;
end;

{ Tfrmcadcores }

procedure Tfrmcadcores.FormDestroy(Sender: TObject);
begin
  if Assigned(FRepositorio) then
    FRepositorio.Free;
end;

procedure Tfrmcadcores.FormActivate(Sender: TObject);
begin
  // Verificação de segurança para evitar AV caso o modulo_dados não exista
  if Assigned(modulo_dados) and Assigned(modulo_dados.fdbanco) then
    FRepositorio := TCorRepository.Create(modulo_dados.fdbanco)
  else
    raise Exception.Create('Banco de dados não inicializado em modulo_dados.');

  ConfigurarGrid;
  CarregarGrid;
  NovoRegistro;
end;

procedure Tfrmcadcores.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Action := caFree;
end;

procedure Tfrmcadcores.ConfigurarGrid;
begin
  gridcores.ColCount := 2;
  gridcores.FixedRows := 1;
  gridcores.Cells[0,0] := 'Código';
  gridcores.Cells[1,0] := 'Descrição';
  gridcores.ColWidths[0] := 60;
  gridcores.ColWidths[1] := 300;
end;

procedure Tfrmcadcores.CarregarGrid;
var
  Qry: TFDQuery;
  Linha: Integer;
begin
  gridcores.RowCount := 2; // Reseta o grid
  gridcores.Cells[0, 1] := '';
  gridcores.Cells[1, 1] := '';

  Qry := FRepositorio.Listar;
  try
    Linha := 1;
    while not Qry.Eof do
    begin
      if Linha >= gridcores.RowCount then
        gridcores.RowCount := Linha + 1;

      gridcores.Cells[0, Linha] := Qry.FieldByName('codigo_cor').AsString;
      gridcores.Cells[1, Linha] := Qry.FieldByName('descricao_cor').AsString;

      Inc(Linha);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
end;

procedure Tfrmcadcores.NovoRegistro;
begin
  FModo := moInclusao;
  LimparCampos;
  lblcodcor.Text := IntToStr(FRepositorio.ObterProximoCodigo);
  lbldescricao.SetFocus;
end;

procedure Tfrmcadcores.LimparCampos;
begin
  lblcodcor.Clear;
  lbldescricao.Clear;
end;

function Tfrmcadcores.CodigoAtual: Integer;
begin
  Result := StrToIntDef(lblcodcor.Text, 0);
end;

function Tfrmcadcores.DescricaoAtual: string;
begin
  Result := Trim(lbldescricao.Text);
end;

procedure Tfrmcadcores.spbsalvarClick(Sender: TObject);
var
  Cor: TCor;
begin
  if DescricaoAtual = '' then
  begin
    MessageDlg('Informe a descrição.', mtWarning, [mbOK], 0);
    lbldescricao.SetFocus;
    Exit;
  end;

  if FRepositorio.ExisteDescricao(DescricaoAtual, CodigoAtual) then
  begin
    MessageDlg('Descrição já cadastrada.', mtWarning, [mbOK], 0);
    lbldescricao.SetFocus;
    Exit;
  end;

  Cor := TCor.Create;
  try
    Cor.Codigo := CodigoAtual;
    Cor.Descricao := DescricaoAtual;

    if FModo = moInclusao then
      FRepositorio.Inserir(Cor)
    else
      FRepositorio.Alterar(Cor);

    CarregarGrid;
    NovoRegistro;
  finally
    Cor.Free;
  end;
end;

procedure Tfrmcadcores.spbexcluirClick(Sender: TObject);
begin
  if (CodigoAtual > 0) and (MessageDlg('Excluir registro?', mtConfirmation, [mbYes, mbNo], 0) = mrYes) then
  begin
    FRepositorio.Excluir(CodigoAtual);
    CarregarGrid;
    NovoRegistro;
  end;
end;

procedure Tfrmcadcores.CarregarRegistroGrid;
begin
  if (gridcores.Row > 0) and (gridcores.Cells[0, gridcores.Row] <> '') then
  begin
    lblcodcor.Text := gridcores.Cells[0, gridcores.Row];
    lbldescricao.Text := gridcores.Cells[1, gridcores.Row];
    FModo := moAlteracao;
    lbldescricao.SetFocus;
  end;
end;

procedure Tfrmcadcores.gridcoresDblClick(Sender: TObject);
begin
  CarregarRegistroGrid;
end;

procedure Tfrmcadcores.gridcoresKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_RETURN then CarregarRegistroGrid;
  if Key = VK_DELETE then begin frmcadcores.lblcodcor.text := frmcadcores.gridcores.cells[0,gridcores.row]; spbexcluirClick(Sender); end;
end;

procedure Tfrmcadcores.lbldescricaoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_RETURN then spbsalvarClick(Sender);
end;

procedure Tfrmcadcores.spbsairClick(Sender: TObject);
begin
  Close;
end;

procedure Tfrmcadcores.spblimparClick(Sender: TObject);
begin
  NovoRegistro;
end;

procedure Tfrmcadcores.FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F10 then Close;
  if Key = VK_INSERT then NovoRegistro;
end;

end.
