unit unt_excluicontabil;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, Menus, StdCtrls, ComCtrls, Buttons, ExtCtrls, Grids, DBGrids, Data.DB,
  Vcl.Mask,
  unt_excluicontabil_types, unt_excluicontabil_repository, unt_excluicontabil_service;

type
  Tfrmexcluicontablanc = class(TForm)
    PopupMenu1: TPopupMenu;
    Gravaropes1: TMenuItem;
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spbdeletapormodulo: TSpeedButton;
    spbsair: TSpeedButton;
    spblimpar: TSpeedButton;
    lblsair: TLabel;
    spbajuste: TSpeedButton;
    StatusBar1: TStatusBar;
    GroupBox1: TGroupBox;
    lblcontabchv: TLabeledEdit;
    gridcontabil: TDBGrid;
    GroupBox7: TGroupBox;
    lblcampo: TLabel;
    lblordem: TLabel;
    lblprocurarpor: TLabeledEdit;
    cbocampo: TComboBox;
    cbordem: TComboBox;
    rdgcrescente: TRadioButton;
    rdgdecrescente: TRadioButton;
    Panel1: TPanel;
    GroupBox2: TGroupBox;
    datamodini: TDateTimePicker;
    datamodfim: TDateTimePicker;
    Label1: TLabel;
    cbomodulo: TComboBox;
    lblmodulo: TLabel;
    gridexcluimodulo: TDBGrid;
    spbpesquisar: TSpeedButton;
    spbexecutar: TSpeedButton;
    BitBtn1: TBitBtn;
    lbltotalreg: TLabel;
    lblnreg: TLabel;
    lblorignum: TLabeledEdit;
    lblmodulorig: TLabel;
    cborigem: TComboBox;
    lblsubmodulo: TLabel;
    cbosubmodulo: TComboBox;
    panelaviso: TPanel;
    lblaviso: TLabel;
    Memo1: TMemo;
    btnok: TButton;
    procedure spblimparClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure FormActivate(Sender: TObject);
    procedure gridcontabilDblClick(Sender: TObject);
    procedure spbsalvarClick(Sender: TObject);
    procedure spbsairClick(Sender: TObject);
    procedure lblprocurarporKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbpesquisarClick(Sender: TObject);
    procedure spbdeletapormoduloClick(Sender: TObject);
    procedure spbexecutarClick(Sender: TObject);
    procedure btnokClick(Sender: TObject);
    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
  private
    FService: TExcluiContabilService;
    procedure CarregarMovimentoContabil;
    procedure ConfigurarControles;
  public
    { Public declarations }
  end;

var
  frmexcluicontablanc: Tfrmexcluicontablanc;

implementation

uses funcoes, unt_dados, unt_logon, unt_selecionaempresa, unt_principal;

{$R *.dfm}

procedure Tfrmexcluicontablanc.FormCreate(Sender: TObject);
var
  vRepo: IExcluiContabilRepository;
begin
  vRepo := TExcluiContabilRepositoryFireDAC.Create(modulo_dados.fdbanco);
  FService := TExcluiContabilService.Create(vRepo);
end;

procedure Tfrmexcluicontablanc.FormDestroy(Sender: TObject);
begin
  FreeAndNil(FService);
end;

procedure Tfrmexcluicontablanc.spblimparClick(Sender: TObject);
begin
  lblcontabchv.Clear;
  lblorignum.Clear;
  lblprocurarpor.Clear;
  lblprocurarpor.SetFocus;
end;

procedure Tfrmexcluicontablanc.spbsairClick(Sender: TObject);
begin
  Close;
end;

procedure Tfrmexcluicontablanc.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
  action := cafree;
end;

procedure Tfrmexcluicontablanc.FormKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
  if key = vk_f10 then
    spbsair.Click;
end;

procedure Tfrmexcluicontablanc.btnokClick(Sender: TObject);
begin
  panelaviso.Visible := False;
end;

procedure Tfrmexcluicontablanc.ConfigurarControles;
begin
  cbocampo.Clear;
  cbocampo.Items.Add('contablancchv');
  cbocampo.Items.Add('contablancorignum');
  cbocampo.Items.Add('contablancmod');
  cbocampo.Items.Add('contablancctadeb');
  cbocampo.Items.Add('contablancctacred');
  cbocampo.ItemIndex := 0;

  cbordem.Clear;
  cbordem.Items.Add('contablancdata');
  cbordem.Items.Add('contablancchv');
  cbordem.ItemIndex := 0;
end;

procedure Tfrmexcluicontablanc.CarregarMovimentoContabil;
begin
  with modulo_dados do
  begin
    fdquerysql4.Close;
    fdquerysql4.SQL.Clear;
    fdquerysql4.SQL.Text :=
      'SELECT TOP 100 cl.* FROM contab_lancamento cl WITH (NOLOCK) ' +
      'WHERE cl.planoctaempcod = :pempresa ' +
      'ORDER BY cl.contablancdata DESC, cl.contablancchv DESC';
    fdquerysql4.ParamByName('pempresa').AsString := frmprincipal.codigo_empresa;
    fdquerysql4.Open;
    dtsfdquerysql4.DataSet := fdquerysql4;
    gridcontabil.DataSource := dtsfdquerysql4;
    gridcontabil.Refresh;
  end;
end;

procedure Tfrmexcluicontablanc.FormActivate(Sender: TObject);
begin
  StatusBar1.Panels[1].Text := configura_statusbar('');
  StatusBar1.Panels[3].Text := configura_statusbar('');
  StatusBar1.Panels[5].Text := frmprincipal.nomeserversql;

  ConfigurarControles;
  CarregarMovimentoContabil;

  panelaviso.Visible := False;
end;

procedure Tfrmexcluicontablanc.gridcontabilDblClick(Sender: TObject);
begin
  with modulo_dados do
  begin
    if not fdquerysql4.IsEmpty then
    begin
      lblcontabchv.Text := Trim(fdquerysql4.FieldByName('contablancchv').AsString);
      lblorignum.Text := Trim(fdquerysql4.FieldByName('contablancorignum').AsString);
    end;
  end;
end;

procedure Tfrmexcluicontablanc.lblprocurarporKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
var
  Campo: string;
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then
  begin
    Campo := cbocampo.Text;
    if Trim(Campo) = '' then
      Campo := 'contablancchv';

    with modulo_dados do
    begin
      fdquerysql4.Close;
      fdquerysql4.SQL.Clear;
      fdquerysql4.SQL.Text :=
        'SELECT TOP 200 cl.* FROM contab_lancamento cl WITH (NOLOCK) ' +
        'WHERE cl.planoctaempcod = :pempresa ' +
        '  AND cl.' + Campo + ' LIKE :pvalor ' +
        'ORDER BY cl.contablancdata DESC, cl.contablancchv DESC';
      fdquerysql4.ParamByName('pempresa').AsString := frmprincipal.codigo_empresa;
      fdquerysql4.ParamByName('pvalor').AsString := '%' + Trim(lblprocurarpor.Text) + '%';
      fdquerysql4.Open;
      dtsfdquerysql4.DataSet := fdquerysql4;
      gridcontabil.DataSource := dtsfdquerysql4;
      gridcontabil.Refresh;
    end;
  end;
end;

procedure Tfrmexcluicontablanc.spbsalvarClick(Sender: TObject);
var
  Chave: string;
  ResDTO: TResultadoExclusaoContabil;
begin
  Chave := Trim(lblcontabchv.Text);
  if Chave = '' then
  begin
    MessageDlg('Informe o numero de chave do lancamento que deseja excluir.', mtError, [mbOK], 0);
    lblcontabchv.SetFocus;
    Exit;
  end;

  if MessageDlg('Confirma a Exclusao deste Lancamento Contabil? (Y/N)', mtConfirmation, [mbYes, mbNo], 0) <> IDYES then
    Exit;

  ResDTO := FService.ExcluirLancamento(Chave, frmlogon.nomeusuario);
  if ResDTO.Sucesso then
  begin
    MessageDlg(ResDTO.Mensagem, mtInformation, [mbOK], 0);
    CarregarMovimentoContabil;
    spblimpar.Click;
  end
  else
    MessageDlg(ResDTO.Mensagem, mtError, [mbOK], 0);
end;

procedure Tfrmexcluicontablanc.spbpesquisarClick(Sender: TObject);
begin
  with modulo_dados do
  begin
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text :=
      'SELECT cl.* FROM contab_lancamento cl WITH (NOLOCK) ' +
      'WHERE cl.contablancdata >= :pini AND cl.contablancdata <= :pfim ' +
      '  AND cl.planoctaempcod = :pempresa ' +
      '  AND cl.contablancmod = :pmodulo ' +
      'ORDER BY cl.contablancdata ASC';
    fdquerysql.ParamByName('pini').AsDate := datamodini.Date;
    fdquerysql.ParamByName('pfim').AsDate := datamodfim.Date;
    fdquerysql.ParamByName('pempresa').AsString := frmprincipal.codigo_empresa;
    fdquerysql.ParamByName('pmodulo').AsString := cbomodulo.Text;
    fdquerysql.Open;

    dtsfdquerysql.DataSet := fdquerysql;
    gridexcluimodulo.DataSource := dtsfdquerysql;
    gridexcluimodulo.Refresh;

    lblnreg.Caption := IntToStr(fdquerysql.RecordCount);
  end;
end;

procedure Tfrmexcluicontablanc.spbdeletapormoduloClick(Sender: TObject);
begin
  Panel1.Visible := not Panel1.Visible;
end;

procedure Tfrmexcluicontablanc.spbexecutarClick(Sender: TObject);
var
  Filtro: TFiltroExclusaoModuloDTO;
  ResDTO: TResultadoExclusaoContabil;
begin
  if MessageDlg('ATENCAO: Deseja realmente excluir todos os lancamentos do periodo selecionado?',
    mtConfirmation, [mbYes, mbNo], 0) <> IDYES then
    Exit;

  Filtro.DataInicial := datamodini.Date;
  Filtro.DataFinal := datamodfim.Date;
  Filtro.Modulo := cbomodulo.Text;
  Filtro.SubModulo := cbosubmodulo.Text;
  Filtro.EmpresaCod := frmprincipal.codigo_empresa;

  ResDTO := FService.ExcluirModuloLote(Filtro, frmlogon.nomeusuario);
  if ResDTO.Sucesso then
  begin
    MessageDlg(ResDTO.Mensagem, mtInformation, [mbOK], 0);
    spbpesquisar.Click;
    CarregarMovimentoContabil;
  end
  else
    MessageDlg(ResDTO.Mensagem, mtError, [mbOK], 0);
end;

end.
