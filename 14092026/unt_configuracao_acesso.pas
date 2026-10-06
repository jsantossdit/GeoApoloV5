unit unt_configuracao_acesso;
{
  GeoApolo - TConfiguracaoAcessoRegistry
  Implementa IConfiguracaoAcesso lendo HKEY_CURRENT_USER\sdit\configuracoes\DataBase.
  Encapsula toda dependencia com TRegistry neste unico lugar.
}
interface
uses
  SysUtils,
  Registry, unt_logon_interfaces, unt_criptografia_adapter, unt_autenticador, windows;
type
  TConfiguracaoAcessoRegistry = class(TInterfacedObject, IConfiguracaoAcesso)
  private
    FCriptografia: ICriptografia;
    const CHAVE_REGISTRO = 'sdit\configuracoes\DataBase';
  public
    constructor Create(ACriptografia: ICriptografia);
    { IConfiguracaoAcesso }
    function ConfiguracaoBancoExiste: Boolean;
    function LerDadosBanco(out ADados: TDadosBanco): Boolean;
  end;
implementation

uses funcoes;

{ TConfiguracaoAcessoRegistry }

constructor TConfiguracaoAcessoRegistry.Create(ACriptografia: ICriptografia);
begin
  inherited Create;
  if not Assigned(ACriptografia) then
    raise EArgumentNilException.Create('TConfiguracaoAcessoRegistry: criptografia nao pode ser nil');
  FCriptografia := ACriptografia;
end;

function TConfiguracaoAcessoRegistry.ConfiguracaoBancoExiste: Boolean;
var
  Reg: TRegistry;
begin
  Reg := TRegistry.Create;
  try
    Reg.RootKey := HKEY_CURRENT_USER;
    Result := Reg.KeyExists(CHAVE_REGISTRO);
  finally
    Reg.Free;
  end;
end;

function TConfiguracaoAcessoRegistry.LerDadosBanco(out ADados: TDadosBanco): Boolean;
var
  Reg: TRegistry;
  SenhaCrua, SenhaDecriptada: string;
begin
  Result := False;
  ADados := Default(TDadosBanco);

  Reg := TRegistry.Create;
  try
    Reg.RootKey := HKEY_CURRENT_USER;
    if not Reg.OpenKey(CHAVE_REGISTRO, False) then
      Exit;

    ADados.NomeServidor := SanitizarNomeServidor(Reg.ReadString('Nome do ServidorSQL'));
    ADados.NomeBanco    := Trim(Reg.ReadString('NomeBancoSQL'));
    ADados.IPServidor   := SanitizarNomeServidor(Reg.ReadString('IP do ServidorSQL'));
    ADados.Usuario      := Trim(Reg.ReadString('Usuario MSSQL'));
    ADados.Protocolo    := Trim(Reg.ReadString('ProtocoloSQL'));
    if ADados.Protocolo = '' then
      ADados.Protocolo  := Trim(Reg.ReadString('ProtocoloADO'));

    SenhaCrua := Reg.ReadString('Senha do Banco SQL');
    try
      SenhaDecriptada := FCriptografia.Decriptografar(SenhaCrua);
    except
      SenhaDecriptada := SenhaCrua;
    end;

    if (Trim(SenhaDecriptada) = '') and (Trim(SenhaCrua) <> '') then
      ADados.Senha := SenhaCrua
    else if SenhaCrua = 'semsenha' then
      ADados.Senha := 'semsenha'
    else
      ADados.Senha := SenhaDecriptada;

    Result := (ADados.NomeServidor <> '') and (ADados.NomeBanco <> '');
  finally
    Reg.Free;
  end;
end;

end.