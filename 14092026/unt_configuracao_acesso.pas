unit unt_configuracao_acesso;
{
  GeoApolo - TConfiguracaoAcessoRegistry
  Implementa IConfiguracaoAcesso lendo HKEY_CURRENT_USER\sdit\configuracoes\DataBase.
  Encapsula toda dependencia com TRegistry neste unico lugar.
}
interface
uses
  SysUtils,
  Registry, unt_logon_interfaces,unt_criptografia_adapter, unt_autenticador, windows;
type
  TConfiguracaoAcessoRegistry = class(TInterfacedObject, IConfiguracaoAcesso)
  private
    FCriptografia: ICriptografia; // <-- Declaramos a variável PRIMEIRO
    const CHAVE_REGISTRO = 'sdit\configuracoes\DataBase'; // <-- Constante DEPOIS
  public
    constructor Create(ACriptografia: ICriptografia);
    { IConfiguracaoAcesso }
    function ConfiguracaoBancoExiste: Boolean;
    function LerDadosBanco(out ADados: TDadosBanco): Boolean;
  end;
implementation
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
    Reg.RootKey := HKEY_CURRENT_USER; // <-- Correção aqui (adicionado os dois pontos)
    Result := Reg.KeyExists(CHAVE_REGISTRO);
  finally
    Reg.Free;
  end;
end;
function TConfiguracaoAcessoRegistry.LerDadosBanco(out ADados: TDadosBanco): Boolean;
var
  Reg: TRegistry;
begin
  Result := False;
  ADados := Default(TDadosBanco);

  Reg := TRegistry.Create;
  try
    Reg.RootKey := HKEY_CURRENT_USER; // <-- Correção aqui: removidas as aspas
    if not Reg.OpenKey(CHAVE_REGISTRO, False) then
      Exit;

    ADados.NomeServidor := Reg.ReadString('Nome do ServidorSQL');
    ADados.NomeBanco    := Reg.ReadString('NomeBancoSQL');
    ADados.IPServidor   := Reg.ReadString('IP do ServidorSQL');
    ADados.Usuario      := Reg.ReadString('Usuario MSSQL');
    ADados.Protocolo    := Reg.ReadString('ProtocoloADO');

    // senha vem criptografada no registry, decriptografa aqui
    ADados.Senha := FCriptografia.Decriptografar(
                      Reg.ReadString('Senha do Banco SQL'));
    Result := True;
  finally
    Reg.Free;
  end;
end;

end.
