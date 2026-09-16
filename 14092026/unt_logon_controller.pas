unit unt_logon_controller;

{
  GeoApolo - TLogonController
  Implementa ILogonController.
  Orquestra autenticacao, licenca e configuracao de banco.
  Nao conhece formularios, Application nem mensagens de dialogo.
  A camada de apresentacao (Tfrmlogon) usa este controller e decide
  o que exibir com base nos TEventoLogon retornados.
}

interface

uses
  SysUtils,
  unt_logon_interfaces;

type

  TLogonController = class(TInterfacedObject, ILogonController)
  private
    FAutenticador   : IAutenticador;
    FValidadorLic   : IValidadorLicenca;
    FConfigAcesso   : IConfiguracaoAcesso;
  public
    constructor Create(AAutenticador : IAutenticador;
                       AValidadorLic : IValidadorLicenca;
                       AConfigAcesso : IConfiguracaoAcesso);

    { ILogonController }
    function ExecutarLogon(const ACred: TCredenciais;
      out AEvento: TEventoLogon;
      out AResultado: TResultadoAutenticacao): Boolean;

    function ValidarLicenca(out AEvento: TEventoLogon;
      out AMensagem: string): Boolean;

    function ConfirmarPrimeiraSenha(const ALogin, ASenha: string): Boolean;

    function CarregarConfiguracoesBanco(out ADados: TDadosBanco): Boolean;

    function DefinirCredenciaisAlvo(const ALogin, ACodApoloLink,
      ASenhaAlvoPlano: string; out AMensagemErro: string): Boolean;
  end;

implementation

{ TLogonController }

constructor TLogonController.Create(AAutenticador: IAutenticador;
  AValidadorLic: IValidadorLicenca; AConfigAcesso: IConfiguracaoAcesso);
begin
  inherited Create;
  if not Assigned(AAutenticador) then
    raise EArgumentNilException.Create('TLogonController: autenticador nao pode ser nil');
  if not Assigned(AValidadorLic) then
    raise EArgumentNilException.Create('TLogonController: validador de licenca nao pode ser nil');
  if not Assigned(AConfigAcesso) then
    raise EArgumentNilException.Create('TLogonController: configuracao de acesso nao pode ser nil');

  FAutenticador := AAutenticador;
  FValidadorLic := AValidadorLic;
  FConfigAcesso := AConfigAcesso;
end;

function TLogonController.ExecutarLogon(const ACred: TCredenciais;
  out AEvento: TEventoLogon; out AResultado: TResultadoAutenticacao): Boolean;
begin
  Result    := False;
  AEvento   := elCredenciaisVazias;
  AResultado := Default(TResultadoAutenticacao);

  { Credenciais vazias }
  if (Trim(ACred.Login) = '') or (Trim(ACred.Senha) = '') then
  begin
    AEvento := elCredenciaisVazias;
    Exit;
  end;

  { Delega autenticacao }
  if not FAutenticador.Autenticar(ACred, AResultado) then
  begin
    { Identifica o motivo da falha pelo campo MensagemErro }
    if AResultado.MensagemErro = 'SENHA_BRANCO' then
      AEvento := elSenhaNaoCadastrada
    else if Pos('nao encontrado', LowerCase(AResultado.MensagemErro)) > 0 then
      AEvento := elUsuarioInativo
    else if Pos('permissao', LowerCase(AResultado.MensagemErro)) > 0 then
      AEvento := elPermissaoNegada
    else
      AEvento := elSenhaInvalida;
    Exit;
  end;

  AEvento := elLogonSucesso;
  Result  := True;
end;

function TLogonController.ValidarLicenca(out AEvento: TEventoLogon;
  out AMensagem: string): Boolean;
var
  ResultadoLic: TResultadoLicenca;
begin
  AMensagem := '';
  AEvento   := elLogonSucesso;

  Result := FValidadorLic.ValidarLicencaAtual(ResultadoLic, AMensagem);

  if not Result then
    AEvento := elLicencaInvalida
  else if ResultadoLic = rlDentroToleranciaBloqueando then
    AEvento := elLicencaInvalida;  // aviso, mas nao bloqueia (Result = True)
end;

function TLogonController.ConfirmarPrimeiraSenha(const ALogin,
  ASenha: string): Boolean;
begin
  Result := FAutenticador.DefinirPrimeiraSenha(ALogin, ASenha);
end;

function TLogonController.CarregarConfiguracoesBanco(out ADados: TDadosBanco): Boolean;
begin
  ADados := Default(TDadosBanco);

  if not FConfigAcesso.ConfiguracaoBancoExiste then
  begin
    Result := False;
    Exit;
  end;

  Result := FConfigAcesso.LerDadosBanco(ADados);
end;

function TLogonController.DefinirCredenciaisAlvo(const ALogin, ACodApoloLink,
  ASenhaAlvoPlano: string; out AMensagemErro: string): Boolean;
begin
  AMensagemErro := '';
  try
    if Trim(ACodApoloLink) = '' then
    begin
      AMensagemErro := 'Usuario alvo nao informado.';
      Exit(False);
    end;
    if Trim(ASenhaAlvoPlano) = '' then
    begin
      AMensagemErro := 'Senha alvo nao informada.';
      Exit(False);
    end;

    { A criptografia (chave 35) e feita dentro do autenticador, que e quem
      conhece a implementacao de ICriptografia usada para o sistema alvo. }
    Result := FAutenticador.DefinirDadosAlvo(ALogin, ACodApoloLink, ASenhaAlvoPlano);

    if not Result then
      AMensagemErro := 'Nao foi possivel gravar os dados do usuario alvo.';
  except
    on E: Exception do
    begin
      Result := False;
      AMensagemErro := E.Message;
    end;
  end;
end;

end.
