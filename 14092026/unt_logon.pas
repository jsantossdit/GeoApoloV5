unit unt_logon;
{
  GeoApolo - Tfrmlogon (refatorado)
  Responsabilidade: SOMENTE apresentacao.
  Toda logica de negocio e delegada ao ILogonController.
  Este formulario:
    - Captura credenciais
    - Chama o controller
    - Interpreta o TEventoLogon retornado
    - Exibe mensagens ao usuario
    - Navega entre formularios
  Dependencias de negocio: ZERO (apenas via ILogonController).
}
interface
uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, StdCtrls, Buttons, ExtCtrls, ComCtrls, Vcl.Mask,    FireDAC.Comp.Client,
  IdBaseComponent, IdComponent, IdUDPBase, IdUDPClient, IdSNTP,unt_logon_controller,
  Vcl.Imaging.pngimage, unt_logon_interfaces;

type
  Tfrmlogon = class(TForm)
    GroupBox1   : TGroupBox;
    spblogon    : TSpeedButton;
    spbsair     : TSpeedButton;
    img1        : TImage;
    StatusBar1  : TStatusBar;
    lblusuario  : TLabeledEdit;
    lblsenha    : TLabeledEdit;
    procedure FormCreate(Sender: TObject);
    procedure FormDestroy(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spblogonClick(Sender: TObject);
    procedure spbsairClick(Sender: TObject);
    procedure lblusuarioKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblsenhaKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblsenhaEnter(Sender: TObject);
  private
    FController     : ILogonController;
    FConexao        : TFDConnection;   // gerenciada pelo modulo_dados
    { Inicializacao do controller com todas as dependencias }
    procedure InicializarController;
    { Interpretacao dos eventos retornados pelo controller }
    procedure TratarEventoLogon(AEvento: TEventoLogon;
      const AResultado: TResultadoAutenticacao;
      const AMensagem: string);
    { Fluxo de primeira senha }
    procedure TratarPrimeiraSenha(const ALogin: string);
    { Verifica se usucod_apolo esta vazio e, se estiver, solicita os dados do alvo }
    procedure SolicitarDadosAlvo(const ALogin: string);
    { Exibe um dialogo simples com campo de senha mascarado (PasswordChar) }
    function SolicitarSenhaMascarada(const ATitulo, APrompt: string;
      out ASenha: string): Boolean;
    { Configura banco via form externo e reinicia controller }
    procedure SolicitarConfiguracaoBanco;
    { Atualiza statusbar de forma segura }
    procedure AtualizarStatus(const AMensagem: string);
    { Verifica rede antes de tudo }
    function RedeDisponivel: Boolean;
  public
    { Dados publicos consumidos por frmprincipal apos logon bem-sucedido }
    CodigoUsuario      : string;
    LoginApolo         : string;
    NomeUsuario        : string;
    NomeCompletoUsuario: string;
  end;
var
  frmlogon: Tfrmlogon;
implementation

uses
  unt_dados, unt_principal,
  frmconfigbancos, unt_selecionaempresa, funcoes, unt_about,
  unt_criptografia_adapter, unt_configuracao_acesso, unt_repositorio_usuario,
  unt_repositorio_licenca, unt_autenticador, unt_validador_licenca;

{$R *.dfm}
{ ---------------------------------------------------------------------------- }
{ Ciclo de vida do formulario                                                   }
{ ---------------------------------------------------------------------------- }
procedure Tfrmlogon.FormCreate(Sender: TObject);
begin
  // controller sera criado em FormActivate, apos modulo_dados estar disponivel
end;

procedure Tfrmlogon.FormDestroy(Sender: TObject);
begin
  FController := nil;
end;

procedure Tfrmlogon.FormActivate(Sender: TObject);
var
  DadosBanco: TDadosBanco;
begin
  if not RedeDisponivel then
    begin
      MessageDlg('Rede de dados nao detectada. Impossivel acessar o sistema.', mtError, [mbOK], 0);
      Close;
      Exit;
    end;
  AtualizarStatus('Verificando configuracoes...');
  { Garante frmprincipal criado }
  if not FormEstaCriado(Tfrmprincipal) then
    Application.CreateForm(Tfrmprincipal, frmprincipal);
  { Inicializa controller (primeira vez) }
  InicializarController;
  { Verifica se banco esta configurado }
  if not FController.CarregarConfiguracoesBanco(DadosBanco) then
    begin
      SolicitarConfiguracaoBanco;
      InicializarController;  // recria apos configuracao
    end
  else
  begin
    { Propaga dados para frmprincipal (compatibilidade com codigo legado) }
    frmprincipal.nomeserversql    := DadosBanco.NomeServidor;
    frmprincipal.nomebancosql     := DadosBanco.NomeBanco;
    frmprincipal.ipserversql      := DadosBanco.IPServidor;
    frmprincipal.usuariobancosql  := DadosBanco.Usuario;
    frmprincipal.senhasql         := DadosBanco.Senha;
    frmprincipal.protocolo        := DadosBanco.Protocolo;
  end;
  AtualizarStatus('Pronto.');
  lblusuario.SetFocus;
end;

procedure Tfrmlogon.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Action := caHide;
end;
{ ---------------------------------------------------------------------------- }
{ Acoes dos botoes                                                              }
{ ---------------------------------------------------------------------------- }
procedure Tfrmlogon.spbsairClick(Sender: TObject);
begin
  Close;
end;

procedure Tfrmlogon.spblogonClick(Sender: TObject);
var
  Cred      : TCredenciais;
  Evento    : TEventoLogon;
  Resultado : TResultadoAutenticacao;
  MsgLic    : string;
begin
  if not Assigned(FController) then
  begin
    MessageDlg('Sistema nao inicializado. Tente novamente.', mtError, [mbOK], 0);
    Exit;
  end;
  { Valida campo senha vazio antes de chamar o controller }
  if Trim(lblsenha.Text) = '' then
  begin
    MessageDlg('Informe a senha para acessar o sistema.', mtError, [mbOK], 0);
    lblsenha.SetFocus;
    Exit;
  end;
  Cred.Login := Trim(lblusuario.Text);
  Cred.Senha := lblsenha.Text;
  AtualizarStatus('Autenticando...');
  { Valida licenca antes do logon }
{  if not FController.ValidarLicenca(Evento, MsgLic) then
  begin
    TratarEventoLogon(Evento, Default(TResultadoAutenticacao), MsgLic);
    AtualizarStatus('');
    Exit;
  end; }
  if Trim(lblusuario.Text) = '' then
  begin
    MessageDlg('Informe o usuario para acessar o sistema.', mtError, [mbOK], 0);
    lblusuario.SetFocus;
    Exit;
  end;
  { Executa logon }
  if FController.ExecutarLogon(Cred, Evento, Resultado) then
  begin
    { Propaga dados do usuario para uso externo }
    CodigoUsuario       := Resultado.DadosUsuario.CodUsuario;
    LoginApolo          := Resultado.DadosUsuario.CodApoloLink;
    NomeUsuario         := Resultado.DadosUsuario.Login;
    NomeCompletoUsuario := Resultado.DadosUsuario.NomeCompleto;
    { Propaga para frmprincipal (compatibilidade) }
    frmprincipal.usucod_apolo := Resultado.DadosUsuario.CodApoloLink;
    frmprincipal.senha_alvo   := Resultado.DadosUsuario.SenhaAlvo;
    { Se o usuario alvo (usucod_apolo) ainda nao estiver configurado, solicita agora }
    if Trim(Resultado.DadosUsuario.CodApoloLink) = '' then
      SolicitarDadosAlvo(Resultado.DadosUsuario.Login);
    TratarEventoLogon(elLogonSucesso, Resultado, '');
  end
  else
    TratarEventoLogon(Evento, Resultado, Resultado.MensagemErro);
  AtualizarStatus('');
end;

{ ---------------------------------------------------------------------------- }
{ Teclado                                                                       }
{ ---------------------------------------------------------------------------- }
procedure Tfrmlogon.FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F10 then
    spbsair.Click;
  { F8 - acesso rapido para debug (remover em producao) }
  if Key = VK_F8 then
  begin
   lblusuario.Text := 'ADMIN';
    lblsenha.Text   := 'netscape';
    spblogon.Click;
  end;
end;
procedure Tfrmlogon.lblusuarioKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then
    lblsenha.SetFocus;
end;
procedure Tfrmlogon.lblsenhaKeyUp(Sender: TObject; var Key: Word;
  Shift: TShiftState);
begin
  if (Key = VK_RETURN) then
    spblogon.Click;
end;
procedure Tfrmlogon.lblsenhaEnter(Sender: TObject);
begin
  if Trim(lblusuario.Text) = '' then
  begin
    MessageDlg('Informe o usuario antes de prosseguir.', mtInformation, [mbOK], 0);
    lblusuario.SetFocus;
  end;
end;
{ ---------------------------------------------------------------------------- }
{ Metodos privados                                                              }
{ ---------------------------------------------------------------------------- }
procedure Tfrmlogon.InicializarController;
var
  Cript          : ICriptografia;
  CriptBanco     : ICriptografia;
  RepoUsuario    : IRepositorioUsuario;
  RepoLicenca    : IRepositorioLicenca;
  ConfigAcesso   : IConfiguracaoAcesso;
  Autenticador   : IAutenticador;
  ValidadorLic   : IValidadorLicenca;
  HostNTP        : string;
  PortaNTP       : Integer;
begin
  Cript      := TCriptografiaAdapter.Create;
  CriptBanco := TCriptografiaBancoAdapter.Create;
  ConfigAcesso := TConfiguracaoAcessoRegistry.Create(CriptBanco);
  if not Assigned(modulo_dados) then
  modulo_dados := Tmodulo_dados.Create(Application);

  // Verificar se foi criado antes do uso:
  if not Assigned(modulo_dados.fdbanco) then
     modulo_dados.fdbanco := TFDConnection.Create(nil); // ou Self, dependendo do escopo

   if not Assigned(modulo_dados.fdbanco) then
      raise Exception.Create('Conexão não inicializada.');

FConexao := modulo_dados.fdbanco;

  { Conexao disponivel via modulo_dados se ja criado }
  if Assigned(modulo_dados.fdbanco) then
    FConexao := modulo_dados.fdbanco
  else
     FConexao:=nil;
  if Assigned(FConexao) then
  begin
    RepoUsuario := TRepositorioUsuarioDB.Create(FConexao);
    RepoLicenca := TRepositorioLicencaDB.Create(FConexao);
    Autenticador := TAutenticadorDB.Create(RepoUsuario, Cript);
    HostNTP  := frmprincipal.servidor_ntp;
    PortaNTP := StrToIntDef(frmprincipal.porta_servidor_ntp, 123);
    ValidadorLic := TValidadorLicenca.Create(RepoLicenca, nil, HostNTP, PortaNTP);
  end
  else
  begin
    { Antes de ter conexao, autenticador e validador ficam sem banco }
    Autenticador := nil;
    ValidadorLic := nil;
  end;
  if Assigned(Autenticador) and Assigned(ValidadorLic) then
    FController := TLogonController.Create(Autenticador, ValidadorLic, ConfigAcesso)
  else
    FController := nil;
end;

procedure Tfrmlogon.TratarEventoLogon(AEvento: TEventoLogon;
  const AResultado: TResultadoAutenticacao; const AMensagem: string);
begin
  case AEvento of
    elLogonSucesso:
      begin
        Hide;
        if not Assigned(frmempresa) then
          Application.CreateForm(Tfrmempresa, frmempresa);
        frmempresa.Show;
      end;
    elCredenciaisVazias:
      begin
        MessageDlg('Informe usuario e senha para acessar o sistema.',
          mtWarning, [mbOK], 0);
        lblusuario.SetFocus;
      end;
    elUsuarioInativo:
      begin
        MessageDlg('Usuario nao encontrado ou inativo.', mtError, [mbOK], 0);
        lblusuario.SetFocus;
      end;
    elSenhaInvalida:
      begin
        MessageDlg('Senha errada ou invalida. Tente novamente.',
          mtError, [mbOK], 0);
        lblsenha.Clear;
        lblsenha.SetFocus;
      end;
    elSenhaNaoCadastrada:
      TratarPrimeiraSenha(lblusuario.Text);
    elPermissaoNegada:
      begin
        MessageDlg('Acesso negado para este sistema.', mtError, [mbOK], 0);
        Application.Terminate;
      end;
    elLicencaInvalida:
      begin
        if MessageDlg(AMensagem + #13#10 +
          'Possui a contra-chave de ativacao?',
          mtConfirmation, [mbYes, mbNo], 0) = idYes then
        begin
          Application.CreateForm(Tfrmabout, frmabout);
          frmabout.flag := 'LOGON';
          frmabout.ShowModal;
        end
        else
          Application.Terminate;
      end;
    elNecessarioConfigurarBanco:
      SolicitarConfiguracaoBanco;
    elBancoNaoConfigurado:
      begin
        MessageDlg('Banco de dados nao configurado corretamente.',
          mtError, [mbOK], 0);
      end;
  end;
end;

procedure Tfrmlogon.TratarPrimeiraSenha(const ALogin: string);
var
  Resp: Integer;
begin
  Resp := MessageDlg(
    'Nenhuma senha cadastrada para este usuario.' + #13#10 +
    'Deseja definir a senha informada como senha permanente?',
    mtConfirmation, [mbYes, mbNo], 0);
  if Resp = idYes then
  begin
    if FController.ConfirmarPrimeiraSenha(ALogin, lblsenha.Text) then
      MessageDlg('Senha definida com sucesso. Tente fazer o logon novamente.',
        mtInformation, [mbOK], 0)
    else
      MessageDlg('Erro ao definir senha. Contate o suporte.',
        mtError, [mbOK], 0);
  end
  else
    MessageDlg('Acesso negado.', mtError, [mbOK], 0);
end;

procedure Tfrmlogon.SolicitarConfiguracaoBanco;
begin
  MessageDlg('Sistema sem configuracoes de banco de dados. Informe os dados de conexao.',
    mtWarning, [mbOK], 0);
  Application.CreateForm(Tfrmconfigbanco, frmconfigbanco);
  frmconfigbanco.ShowModal;
end;

procedure Tfrmlogon.AtualizarStatus(const AMensagem: string);
begin
  StatusBar1.Panels[0].Text := AMensagem;
  StatusBar1.Refresh;
end;

function Tfrmlogon.RedeDisponivel: Boolean;
begin
  Result := GetSystemMetrics(SM_NETWORK) and $01 = $01;
end;

procedure Tfrmlogon.SolicitarDadosAlvo(const ALogin: string);
var
  CodAlvo   : string;
  SenhaAlvo : string;
  MsgErro   : string;
begin
  CodAlvo := InputBox('Usuario alvo',
    'Usuario de acesso ao sistema alvo (usucod_apolo) nao configurado.' + #13#10 +
    'Informe o usuario alvo:', '');

  if Trim(CodAlvo) = '' then
  begin
    MessageDlg('Operacao cancelada. Usuario alvo nao foi configurado.',
      mtWarning, [mbOK], 0);
    Exit;
  end;

  if not SolicitarSenhaMascarada('Senha do usuario alvo',
       'Informe a senha do usuario alvo (' + CodAlvo + '):', SenhaAlvo) then
  begin
    MessageDlg('Operacao cancelada. Senha do usuario alvo nao foi configurada.',
      mtWarning, [mbOK], 0);
    Exit;
  end;

  if not FController.DefinirCredenciaisAlvo(ALogin, CodAlvo, SenhaAlvo, MsgErro) then
    MessageDlg('Erro ao salvar os dados do usuario alvo: ' + MsgErro,
      mtError, [mbOK], 0)
  else
  begin
    { Atualiza tambem em memoria para uso imediato pelo restante do sistema }
    frmprincipal.usucod_apolo := CodAlvo;
    MessageDlg('Dados do usuario alvo configurados com sucesso.',
      mtInformation, [mbOK], 0);
  end;
end;

function Tfrmlogon.SolicitarSenhaMascarada(const ATitulo, APrompt: string;
  out ASenha: string): Boolean;
var
  FormSenha : TForm;
  lblProm   : TLabel;
  edtSenha  : TEdit;
  btnOK     : TButton;
  btnCancel : TButton;
begin
  Result := False;
  ASenha := '';
  FormSenha := TForm.CreateNew(Application);
  try
    FormSenha.Caption     := ATitulo;
    FormSenha.ClientWidth  := 340;
    FormSenha.ClientHeight := 120;
    FormSenha.Position    := poScreenCenter;
    FormSenha.BorderStyle := bsDialog;
    FormSenha.BorderIcons := [biSystemMenu];
    FormSenha.KeyPreview  := True;

    lblProm := TLabel.Create(FormSenha);
    lblProm.Parent  := FormSenha;
    lblProm.Left    := 16;
    lblProm.Top     := 12;
    lblProm.Width   := 308;
    lblProm.WordWrap := True;
    lblProm.Caption := APrompt;

    edtSenha := TEdit.Create(FormSenha);
    edtSenha.Parent       := FormSenha;
    edtSenha.Left         := 16;
    edtSenha.Top          := 44;
    edtSenha.Width        := 308;
    edtSenha.PasswordChar := '*';

    btnOK := TButton.Create(FormSenha);
    btnOK.Parent      := FormSenha;
    btnOK.Caption     := 'OK';
    btnOK.Left        := 168;
    btnOK.Top         := 80;
    btnOK.Width       := 75;
    btnOK.ModalResult := mrOk;
    btnOK.Default     := True;

    btnCancel := TButton.Create(FormSenha);
    btnCancel.Parent      := FormSenha;
    btnCancel.Caption     := 'Cancelar';
    btnCancel.Left        := 249;
    btnCancel.Top         := 80;
    btnCancel.Width       := 75;
    btnCancel.ModalResult := mrCancel;
    btnCancel.Cancel      := True;

    FormSenha.ActiveControl := edtSenha;

    if FormSenha.ShowModal = mrOk then
    begin
      ASenha := edtSenha.Text;
      Result := Trim(ASenha) <> '';
    end;
  finally
    FormSenha.Free;
  end;
end;

end.
