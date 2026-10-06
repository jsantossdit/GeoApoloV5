unit unt_cadmarcas;

interface

uses
  Winapi.Windows, Winapi.Messages,
  System.SysUtils, System.Classes, System.Generics.Collections,
  Vcl.Graphics, Vcl.Controls, Vcl.Forms, Vcl.Dialogs,
  Vcl.StdCtrls, Vcl.ExtCtrls, Vcl.Buttons, Vcl.ComCtrls, Vcl.Grids,
  FireDAC.Comp.Client, FireDAC.Stan.Param, Vcl.Mask,
  unt_cadmarcas_types, unt_cadmarcas_repository, unt_cadmarcas_service;

type
  TModoEdicao = (moInclusao, moAlteracao);

  Tfrmcadmarcas = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spbsair: TSpeedButton;
    spblimpar: TSpeedButton;
    spbexcluir: TSpeedButton;
    lblsair: TLabel;
    GroupBox1: TGroupBox;
    lblcodmarca: TLabeledEdit;
    lbldescricao: TLabeledEdit;
    gridmarcas: TStringGrid;
    StatusBar1: TStatusBar;
    procedure FormActivate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormDestroy(Sender: TObject);
    procedure spbsairClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure spbsalvarClick(Sender: TObject);
    procedure spbexcluirClick(Sender: TObject);
    procedure gridmarcasDblClick(Sender: TObject);
    procedure gridmarcasKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lbldescricaoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
  private
    FService: IMarcaService;
    FRepo: IMarcaRepository;
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
  frmcadmarcas: Tfrmcadmarcas;

implementation

{$R *.dfm}

uses unt_dados;

procedure Tfrmcadmarcas.FormActivate(Sender: TObject);
begin
  if not Assigned(FService) then
  begin
    if Assigned(modulo_dados) and Assigned(modulo_dados.fdbanco) then
    begin
      FRepo    := TMarcaRepository.Create(modulo_dados.fdbanco);
      FService := TMarcaService.Create(FRepo);
    end
    else
      raise Exception.Create('Banco de dados nao inicializado em modulo_dados.');
  end;
  ConfigurarGrid;
  CarregarGrid;
  LimparCampos;
end;

procedure Tfrmcadmarcas.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Action := caFree;
end;

procedure Tfrmcadmarcas.FormDestroy(Sender: TObject);
begin
  frmcadmarcas := nil;
end;

procedure Tfrmcadmarcas.ConfigurarGrid;
begin
  gridmarcas.ColCount := 2;
  gridmarcas.RowCount := 2;
  gridmarcas.FixedRows := 1;
  gridmarcas.Cells[0, 0] := 'Código';
  gridmarcas.Cells[1, 0] := 'Descrição da Marca';
  gridmarcas.ColWidths[0] := 90;
  gridmarcas.ColWidths[1] := 600;
end;

procedure Tfrmcadmarcas.CarregarGrid;
var
  Lista: TArray<TMarcaDTO>;
  I: Integer;
begin
  ConfigurarGrid;
  if not Assigned(FService) then
    Exit;

  Lista := FService.ListarMarcas;
  if Length(Lista) = 0 then
  begin
    gridmarcas.RowCount := 2;
    gridmarcas.Cells[0, 1] := '';
    gridmarcas.Cells[1, 1] := '';
    Exit;
  end;

  gridmarcas.RowCount := Length(Lista) + 1;
  for I := 0 to High(Lista) do
  begin
    gridmarcas.Cells[0, I + 1] := Format('%.3d', [Lista[I].CodigoMarca]);
    gridmarcas.Cells[1, I + 1] := Lista[I].DescricaoMarca;
  end;
end;

procedure Tfrmcadmarcas.LimparCampos;
begin
  FModo := moInclusao;
  lblcodmarca.Text := '';
  lbldescricao.Text := '';
  NovoRegistro;
end;

procedure Tfrmcadmarcas.NovoRegistro;
begin
  FModo := moInclusao;
  lblcodmarca.Text := '';
  lbldescricao.Text := '';
  if Assigned(FService) then
    lblcodmarca.Text := Format('%.3d', [FService.ObterProximoCodigo]);
  lbldescricao.SetFocus;
end;

function Tfrmcadmarcas.CodigoAtual: Integer;
begin
  Result := StrToIntDef(Trim(lblcodmarca.Text), 0);
end;

function Tfrmcadmarcas.DescricaoAtual: string;
begin
  Result := UpperCase(Trim(lbldescricao.Text));
end;

procedure Tfrmcadmarcas.CarregarRegistroGrid;
var
  Linha: Integer;
begin
  Linha := gridmarcas.Row;
  if (Linha < 1) or (Trim(gridmarcas.Cells[0, Linha]) = '') then
    Exit;

  lblcodmarca.Text := gridmarcas.Cells[0, Linha];
  lbldescricao.Text := gridmarcas.Cells[1, Linha];
  FModo := moAlteracao;
  lbldescricao.SetFocus;
end;

procedure Tfrmcadmarcas.spbsalvarClick(Sender: TObject);
var
  Marca: TMarcaDTO;
  Res: TResultadoMarca;
begin
  if DescricaoAtual = '' then
  begin
    MessageDlg('Informe a descrição da marca.', mtWarning, [mbOK], 0);
    lbldescricao.SetFocus;
    Exit;
  end;

  Marca.CodigoMarca    := CodigoAtual;
  Marca.DescricaoMarca := DescricaoAtual;

  Res := FService.SalvarMarca(Marca);
  if Res.Sucesso then
  begin
    ShowMessage(Res.Mensagem);
    CarregarGrid;
    LimparCampos;
  end
  else
    MessageDlg(Res.Mensagem, mtError, [mbOK], 0);
end;

procedure Tfrmcadmarcas.spbexcluirClick(Sender: TObject);
var
  Cod: Integer;
  Res: TResultadoMarca;
begin
  Cod := CodigoAtual;
  if Cod <= 0 then
  begin
    MessageDlg('Selecione uma marca para exclusão.', mtWarning, [mbOK], 0);
    Exit;
  end;

  if MessageDlg(Format('Confirma a exclusão da marca "%s" (Cód: %d)?', [DescricaoAtual, Cod]),
                mtConfirmation, [mbYes, mbNo], 0) = mrYes then
  begin
    Res := FService.ExcluirMarca(Cod);
    if Res.Sucesso then
    begin
      ShowMessage(Res.Mensagem);
      CarregarGrid;
      LimparCampos;
    end
    else
      MessageDlg(Res.Mensagem, mtError, [mbOK], 0);
  end;
end;

procedure Tfrmcadmarcas.spblimparClick(Sender: TObject);
begin
  LimparCampos;
end;

procedure Tfrmcadmarcas.spbsairClick(Sender: TObject);
begin
  Close;
end;

procedure Tfrmcadmarcas.gridmarcasDblClick(Sender: TObject);
begin
  CarregarRegistroGrid;
end;

procedure Tfrmcadmarcas.gridmarcasKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_SPACE) then
    CarregarRegistroGrid;
end;

procedure Tfrmcadmarcas.lbldescricaoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_RETURN then
    spbsalvarClick(Sender);
end;

procedure Tfrmcadmarcas.FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  case Key of
    VK_ESCAPE: spbsairClick(Sender);
    VK_F2: spblimparClick(Sender);
    VK_F3: spbsalvarClick(Sender);
    VK_F5: spbexcluirClick(Sender);
    VK_F9: spbsairClick(Sender);
  end;
end;

end.
