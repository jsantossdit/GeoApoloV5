unit unt_usuario_ctasfin;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, ComCtrls, Buttons, ExtCtrls, DBCtrls,
  unt_usuario_ctasfin_types, unt_usuario_ctasfin_repository, unt_usuario_ctasfin_service;

type
  TfrmRelacContasFin_usuario = class(TForm)
    Panel1: TPanel;
    spbsalvar: TSpeedButton;
    spblimpar: TSpeedButton;
    spblocalizar: TSpeedButton;
    spbexcluir: TSpeedButton;
    spbretornar: TSpeedButton;
    lblmsg1: TLabel;
    StatusBar1: TStatusBar;
    GroupBox1: TGroupBox;
    lblusuarios: TLabel;
    cbousuario: TComboBox;
    lstctasdisponiveis: TListBox;
    lstjarelac: TListBox;
    lblcontasdisponiveis: TLabel;
    lblctasjarelacionadas: TLabel;
    Panel2: TPanel;
    btntodosvolta: TBitBtn;
    btnvaium: TBitBtn;
    btnvaitodos: TBitBtn;
    btnvoltaum: TBitBtn;
    procedure FormKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbretornarClick(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure btnvaiumClick(Sender: TObject);
    procedure lstjarelacEnter(Sender: TObject);
    procedure cbousuarioKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure lstctasdisponiveisKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure btnvoltaumClick(Sender: TObject);
    procedure btntodosvoltaClick(Sender: TObject);
    procedure spbsalvarClick(Sender: TObject);
    procedure btnvaitodosClick(Sender: TObject);
    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
  private
    FService: TUsuarioCtasFinService;
    procedure CarregarUsuarios;
    procedure CarregarContasDisponiveis;
    procedure CarregarContasUsuario(const AUsuCod: string);
  public
    { Public declarations }
  end;

var
  frmRelacContasFin_usuario: TfrmRelacContasFin_usuario;

implementation

uses funcoes, unt_dados, unt_principal;

{$R *.dfm}

procedure TfrmRelacContasFin_usuario.FormCreate(Sender: TObject);
var
  vRepo: IUsuarioCtasFinRepository;
begin
  vRepo := TUsuarioCtasFinRepositoryFireDAC.Create(modulo_dados.fdbanco);
  FService := TUsuarioCtasFinService.Create(vRepo);
end;

procedure TfrmRelacContasFin_usuario.FormDestroy(Sender: TObject);
begin
  FreeAndNil(FService);
end;

procedure TfrmRelacContasFin_usuario.FormKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
  if key = vk_f10 then
    spbretornar.Click;
end;

procedure TfrmRelacContasFin_usuario.spbretornarClick(Sender: TObject);
begin
  Close;
end;

procedure TfrmRelacContasFin_usuario.FormClose(Sender: TObject;
  var Action: TCloseAction);
begin
  action := cafree;
end;

procedure TfrmRelacContasFin_usuario.FormActivate(Sender: TObject);
begin
  CarregarUsuarios;
  CarregarContasDisponiveis;

  StatusBar1.Panels[1].Text := configura_statusbar('1');
  StatusBar1.Panels[3].Text := configura_statusbar('1');
  StatusBar1.Panels[5].Text := frmprincipal.nomeserversql;
end;

procedure TfrmRelacContasFin_usuario.CarregarUsuarios;
var
  Lista: TList<string>;
  Usu: string;
begin
  cbousuario.Items.Clear;
  Lista := FService.ObterUsuariosAtivos;
  try
    if Lista.Count = 0 then
    begin
      MessageDlg('NAO HA USUARIOS CADASTRADOS NA BASE APOLO !!!', mtError, [mbOK], 0);
      Exit;
    end;

    for Usu in Lista do
      cbousuario.Items.Add(Usu);

    if cbousuario.Items.Count > 0 then
      cbousuario.ItemIndex := 0;
  finally
    Lista.Free;
  end;
end;

procedure TfrmRelacContasFin_usuario.CarregarContasDisponiveis;
var
  Lista: TList<TContaFinanceiraDTO>;
  Conta: TContaFinanceiraDTO;
begin
  lstctasdisponiveis.Clear;
  Lista := FService.ObterContasDisponiveis;
  try
    if Lista.Count = 0 then
    begin
      MessageDlg('NAO HA CONTAS FINANCEIRAS DISPONIVEIS NA BASE APOLO !!!', mtError, [mbOK], 0);
      cbousuario.SetFocus;
      Exit;
    end;

    for Conta in Lista do
      lstctasdisponiveis.Items.Add(Conta.ToStringFormatado);
  finally
    Lista.Free;
  end;
end;

procedure TfrmRelacContasFin_usuario.CarregarContasUsuario(const AUsuCod: string);
var
  Lista: TList<TContaFinanceiraDTO>;
  Conta: TContaFinanceiraDTO;
  Formatado: string;
begin
  lstjarelac.Clear;
  if Trim(AUsuCod) = '' then
    Exit;

  Lista := FService.ObterContasDoUsuario(AUsuCod);
  try
    for Conta in Lista do
    begin
      Formatado := Conta.ToStringFormatado;
      lstjarelac.Items.Add(Formatado);
    end;
  finally
    Lista.Free;
  end;
  lstjarelac.Refresh;
end;

procedure TfrmRelacContasFin_usuario.btnvaiumClick(Sender: TObject);
var
  Idx: Integer;
  Item: string;
begin
  Idx := lstctasdisponiveis.ItemIndex;
  if Idx >= 0 then
  begin
    Item := lstctasdisponiveis.Items[Idx];
    if lstjarelac.Items.IndexOf(Item) < 0 then
      lstjarelac.Items.Add(Item);
    lstjarelac.Refresh;
  end;
end;

procedure TfrmRelacContasFin_usuario.btnvaitodosClick(Sender: TObject);
var
  i: Integer;
  Item: string;
begin
  for i := 0 to lstctasdisponiveis.Items.Count - 1 do
  begin
    Item := lstctasdisponiveis.Items[i];
    if lstjarelac.Items.IndexOf(Item) < 0 then
      lstjarelac.Items.Add(Item);
  end;
  lstjarelac.Refresh;
end;

procedure TfrmRelacContasFin_usuario.btnvoltaumClick(Sender: TObject);
begin
  if lstjarelac.ItemIndex >= 0 then
  begin
    lstjarelac.Items.Delete(lstjarelac.ItemIndex);
    lstjarelac.Refresh;
  end;
end;

procedure TfrmRelacContasFin_usuario.btntodosvoltaClick(Sender: TObject);
begin
  lstjarelac.Items.Clear;
  lstjarelac.Refresh;
end;

procedure TfrmRelacContasFin_usuario.lstjarelacEnter(Sender: TObject);
begin
  if Trim(cbousuario.Text) = '' then
  begin
    MessageDlg('INFORME UM USUARIO PARA O RELACIONAMENTO COM AS CONTAS FINANCEIRAS DO APOLO !!!', mtWarning, [mbOK], 0);
    cbousuario.SetFocus;
    Exit;
  end;
  CarregarContasUsuario(cbousuario.Text);
end;

procedure TfrmRelacContasFin_usuario.cbousuarioKeyUp(Sender: TObject;
  var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then
  begin
    CarregarContasUsuario(cbousuario.Text);
    lstctasdisponiveis.SetFocus;
  end;
end;

procedure TfrmRelacContasFin_usuario.lstctasdisponiveisKeyUp(
  Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then
    lstjarelac.SetFocus;
end;

procedure TfrmRelacContasFin_usuario.spbsalvarClick(Sender: TObject);
var
  ContasArray: TArray<string>;
  i: Integer;
  Resultado: TResultadoOperacaoContasFin;
begin
  if Trim(cbousuario.Text) = '' then
  begin
    MessageDlg('Selecione um usuario antes de salvar.', mtWarning, [mbOK], 0);
    cbousuario.SetFocus;
    Exit;
  end;

  if MessageDlg('Confirma a Permissao para as Contas Listadas?', mtConfirmation, [mbYes, mbNo], 0) <> IDYES then
  begin
    cbousuario.SetFocus;
    Exit;
  end;

  SetLength(ContasArray, lstjarelac.Items.Count);
  for i := 0 to lstjarelac.Items.Count - 1 do
    ContasArray[i] := TUsuarioCtasFinService.ExtrairCodigoConta(lstjarelac.Items[i]);

  Resultado := FService.SalvarPermissoes(cbousuario.Text, ContasArray);
  if Resultado.Sucesso then
  begin
    MessageDlg(Resultado.Mensagem, mtInformation, [mbOK], 0);
    CarregarContasDisponiveis;
    CarregarContasUsuario(cbousuario.Text);
  end
  else
    MessageDlg('Erro ao salvar permissoes: ' + Resultado.Mensagem, mtError, [mbOK], 0);
end;

end.
