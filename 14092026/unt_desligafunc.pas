unit unt_desligafunc;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, ComCtrls, Buttons, ExtCtrls, Gauges, Grids, DBGrids,
  Menus, Data.DB, Vcl.Mask,
  unt_desligafunc_types, unt_desligafunc_repository, unt_desligafunc_service;

type
  Tfrmdesligafunc = class(TForm)
    Panel1: TPanel;
    spbdesligar: TSpeedButton;
    spblimpar: TSpeedButton;
    spblocalizar: TSpeedButton;
    spbexcluir: TSpeedButton;
    spbretornar: TSpeedButton;
    lblmsg1: TLabel;
    SpeedButton1: TSpeedButton;
    StatusBar1: TStatusBar;
    GroupBox1: TGroupBox;
    lblnomefunc: TLabeledEdit;
    lblusucod: TLabeledEdit;
    Label1: TLabel;
    cbostatus: TComboBox;
    GroupBox3: TGroupBox;
    gridesligamento: TDBGrid;
    GroupBox7: TGroupBox;
    lblcampo: TLabel;
    lblordem: TLabel;
    lblprocurarpor: TLabeledEdit;
    cbocampo: TComboBox;
    cbordem: TComboBox;
    rdgcrescente: TRadioButton;
    rdgdecrescente: TRadioButton;
    PopupMenu1: TPopupMenu;
    procedure FormKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure spbretornarClick(Sender: TObject);
    procedure lblusucodKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblnomefuncKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lblnomefuncEnter(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure lblprocurarporKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbdesligarClick(Sender: TObject);
    procedure gridesligamentoDblClick(Sender: TObject);
    procedure spblimparClick(Sender: TObject);
    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
  private
    FService: TDesligaFuncService;
    procedure CarregarUsuarios(const AStatus: string);
    procedure ConfigurarCamposBusca;
  public
    { Public declarations }
  end;

var
  frmdesligafunc: Tfrmdesligafunc;

implementation

uses funcoes, unt_dados, unt_principal, unt_logon;

{$R *.dfm}

procedure Tfrmdesligafunc.FormCreate(Sender: TObject);
var
  vRepo: IDesligaFuncRepository;
begin
  vRepo := TDesligaFuncRepositoryFireDAC.Create(modulo_dados.fdbanco);
  FService := TDesligaFuncService.Create(vRepo);
end;

procedure Tfrmdesligafunc.FormDestroy(Sender: TObject);
begin
  FreeAndNil(FService);
end;

procedure Tfrmdesligafunc.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
  if key = vk_f10 then
    spbretornar.Click;
end;

procedure Tfrmdesligafunc.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
  action := cafree;
end;

procedure Tfrmdesligafunc.spbretornarClick(Sender: TObject);
begin
  Close;
end;

procedure Tfrmdesligafunc.spblimparClick(Sender: TObject);
begin
  lblusucod.Clear;
  lblnomefunc.Clear;
  lblprocurarpor.Clear;
  lblusucod.SetFocus;
end;

procedure Tfrmdesligafunc.ConfigurarCamposBusca;
begin
  cbocampo.Clear;
  cbocampo.Items.Add('usucod');
  cbocampo.Items.Add('usunome');
  cbocampo.Items.Add('usudepto');
  cbocampo.ItemIndex := 0;

  cbordem.Clear;
  cbordem.Items.Add('usucod');
  cbordem.Items.Add('usunome');
  cbordem.ItemIndex := 0;
end;

procedure Tfrmdesligafunc.CarregarUsuarios(const AStatus: string);
begin
  // Usa a query padrão do formulário desacoplada via serviço se necessário
  with modulo_dados do
  begin
    fdquerysql4.Close;
    fdquerysql4.SQL.Clear;
    fdquerysql4.SQL.Text :=
      'SELECT usucod, usunome, usudepto, usustat ' +
      'FROM usuario WITH (NOLOCK) ' +
      'WHERE usustat = :pstatus ORDER BY usucod ASC';
    fdquerysql4.ParamByName('pstatus').AsString := AStatus;
    fdquerysql4.Open;
    dtsfdquerysql4.DataSet := fdquerysql4;
    gridesligamento.DataSource := dtsfdquerysql4;
    gridesligamento.Refresh;
  end;
end;

procedure Tfrmdesligafunc.FormActivate(Sender: TObject);
begin
  ConfigurarCamposBusca;
  CarregarUsuarios('Ativo');
  lblusucod.SetFocus;

  StatusBar1.Panels[0].Text := 'Banco Alvo';
  StatusBar1.Panels[1].Text := configura_statusbar('1');
  StatusBar1.Panels[2].Text := 'Banco GeoApolo';
  StatusBar1.Panels[3].Text := StatusBar1.Panels[1].Text;
end;

procedure Tfrmdesligafunc.lblusucodKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
var
  Usu: TUsuarioDesligamentoDTO;
begin
  if ((key = vk_return) or (key = vk_tab)) then
  begin
    if Trim(lblusucod.Text) <> '' then
    begin
      if FService.ObterDetalhesUsuario(lblusucod.Text, Usu) then
      begin
        lblnomefunc.Text := Usu.UsuNome;
        if SameText(Usu.UsuStat, 'Ativo') then
          cbostatus.ItemIndex := 0
        else
          cbostatus.ItemIndex := 1;
      end;
    end;
    lblnomefunc.SetFocus;
  end;
end;

procedure Tfrmdesligafunc.lblnomefuncKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
  if ((key = vk_return) or (key = vk_tab)) then
    cbostatus.SetFocus;
end;

procedure Tfrmdesligafunc.lblnomefuncEnter(Sender: TObject);
var
  Usu: TUsuarioDesligamentoDTO;
begin
  if Trim(lblusucod.Text) = '' then
  begin
    MessageDlg('ESCOLHA O USUARIO QUE SERA DESLIGADO DO SISTEMA ALVO !!!', mtWarning, [mbOK], 0);
    lblusucod.SetFocus;
    Exit;
  end;

  if FService.ObterDetalhesUsuario(lblusucod.Text, Usu) then
  begin
    lblnomefunc.Text := Usu.UsuNome;
    if SameText(Usu.UsuStat, 'Ativo') then
      cbostatus.ItemIndex := 0
    else
      cbostatus.ItemIndex := 1;
  end;
end;

procedure Tfrmdesligafunc.lblprocurarporKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
var
  Campo: string;
begin
  if (Trim(lblprocurarpor.Text) <> '') and ((key = vk_return) or (key = vk_tab)) then
  begin
    Campo := cbocampo.Text;
    if Trim(Campo) = '' then
      Campo := 'usucod';

    with modulo_dados do
    begin
      fdquerysql4.Close;
      fdquerysql4.SQL.Clear;
      fdquerysql4.SQL.Text :=
        'SELECT usucod, usunome, usudepto, usustat FROM usuario WITH (NOLOCK) ' +
        'WHERE ' + Campo + ' LIKE :pvalor ORDER BY usucod ASC';
      fdquerysql4.ParamByName('pvalor').AsString := '%' + Trim(lblprocurarpor.Text) + '%';
      fdquerysql4.Open;
      dtsfdquerysql4.DataSet := fdquerysql4;
      gridesligamento.DataSource := dtsfdquerysql4;
      gridesligamento.Refresh;
    end;
  end;
end;

procedure Tfrmdesligafunc.spbdesligarClick(Sender: TObject);
var
  ResDTO: TResultadoDesligamentoDTO;
begin
  if Trim(lblusucod.Text) = '' then
  begin
    MessageDlg('Selecione o usuario que sera desligado.', mtWarning, [mbOK], 0);
    lblusucod.SetFocus;
    Exit;
  end;

  if MessageDlg('Confirma o Desligamento deste Usuario? (Y/N)', mtConfirmation, [mbYes, mbNo], 0) <> IDYES then
  begin
    lblusucod.SetFocus;
    Exit;
  end;

  ResDTO := FService.Desligar(lblusucod.Text);
  if ResDTO.Sucesso then
  begin
    MessageDlg(ResDTO.Mensagem, mtInformation, [mbOK], 0);
    CarregarUsuarios('Ativo');
    spblimpar.Click;
  end
  else
    MessageDlg('Erro ao desligar usuario: ' + ResDTO.Mensagem, mtError, [mbOK], 0);
end;

procedure Tfrmdesligafunc.gridesligamentoDblClick(Sender: TObject);
begin
  with modulo_dados do
  begin
    if not fdquerysql4.IsEmpty then
    begin
      lblusucod.Text := Trim(fdquerysql4.FieldByName('usucod').AsString);
      lblnomefunc.Text := Trim(fdquerysql4.FieldByName('usunome').AsString);
      if SameText(fdquerysql4.FieldByName('usustat').AsString, 'Ativo') then
        cbostatus.ItemIndex := 0
      else
        cbostatus.ItemIndex := 1;
    end;
  end;
end;

end.
