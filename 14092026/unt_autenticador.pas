unit unt_autenticador;

{
  GeoApolo - TAutenticadorDB
  Implementa IAutenticador.
  Responsabilidade unica: validar credenciais contra o banco.
  Nao conhece formularios, Application nem Registry.
}

interface

uses
  SysUtils,
  unt_logon_interfaces;

type

  TAutenticadorDB = class(TInterfacedObject, IAutenticador)
  private
    FRepositorio  : IRepositorioUsuario;
    FCriptografia : ICriptografia;
    const NOME_SISTEMA = 'GeoApolo';
  public
    constructor Create(ARepositorio: IRepositorioUsuario;
                       ACriptografia: ICriptografia);

    { IAutenticador }
    function Autenticar(const ACred: TCredenciais;
      out AResultado: TResultadoAutenticacao): Boolean;
    function SenhaCadastradaEmBranco(const ALogin: string): Boolean;
    function DefinirPrimeiraSenha(const ALogin, ASenha: string): Boolean;
    function DefinirDadosAlvo(const ALogin, ACodApoloLink,
      ASenhaAlvoPlano: string): Boolean;
  end;

implementation

uses
  funcoes; // funcao global criptografia(const Texto: string; Chave: Integer): string

{ TAutenticadorDB }

constructor TAutenticadorDB.Create(ARepositorio: IRepositorioUsuario;
  ACriptografia: ICriptografia);
begin
  inherited Create;
  if not Assigned(ARepositorio) then
    raise EArgumentNilException.Create('TAutenticadorDB: repositorio nao pode ser nil');
  if not Assigned(ACriptografia) then
    raise EArgumentNilException.Create('TAutenticadorDB: criptografia nao pode ser nil');

  FRepositorio  := ARepositorio;
  FCriptografia := ACriptografia;
end;

function TAutenticadorDB.Autenticar(const ACred: TCredenciais;
  out AResultado: TResultadoAutenticacao): Boolean;
var
  Usuario      : TDadosUsuario;
  CodigoSistema: Integer;
  SenhaDecript : string;
begin
  Result    := False;
  AResultado := Default(TResultadoAutenticacao);

  { 1. Credenciais em branco }
  if (Trim(ACred.Login) = '') or (Trim(ACred.Senha) = '') then
  begin
    AResultado.MensagemErro := 'Login e senha sao obrigatorios.';
    Exit;
  end;

  { 2. Usuario existe e esta ativo? }
  if not FRepositorio.BuscarPorLogin(ACred.Login, Usuario) then
  begin
    AResultado.MensagemErro := 'Usuario nao encontrado ou inativo.';
    Exit;
  end;

  AResultado.DadosUsuario := Usuario;

  { 3. Senha em branco no banco — fluxo especial (primeira senha) }
  if Trim(Usuario.SenhaHash) = '' then
  begin
    AResultado.MensagemErro := 'SENHA_BRANCO';  // sinal para o controller
    Exit;
  end;

  { 4. Confere senha }
  SenhaDecript := FCriptografia.Decriptografar(Usuario.SenhaHash);
  if ACred.Senha <> SenhaDecript then
  begin
    AResultado.MensagemErro := 'Senha errada ou invalida.';
    Exit;
  end;

  { 5. Verifica permissao no sistema }
  if not FRepositorio.BuscarCodigoSistema(NOME_SISTEMA, CodigoSistema) then
  begin
    AResultado.MensagemErro := 'Sistema "' + NOME_SISTEMA + '" nao encontrado na base.';
    Exit;
  end;

  AResultado.CodigoSistema := CodigoSistema;

  if not FRepositorio.UsuarioPossuiPermissaoSistema(Usuario.CodUsuario, CodigoSistema) then
  begin
    AResultado.MensagemErro := 'Usuario sem permissao para acessar este sistema.';
    Exit;
  end;

  { Sucesso }
  AResultado.Sucesso := True;
  Result := True;
end;

function TAutenticadorDB.SenhaCadastradaEmBranco(const ALogin: string): Boolean;
var
  Usuario: TDadosUsuario;
begin
  Result := FRepositorio.BuscarPorLogin(ALogin, Usuario) and
            (Trim(Usuario.SenhaHash) = '');
end;

function TAutenticadorDB.DefinirPrimeiraSenha(const ALogin, ASenha: string): Boolean;
var
  Hash: string;
begin
  if Trim(ASenha) = '' then
    raise EArgumentException.Create('TAutenticadorDB.DefinirPrimeiraSenha: senha nao pode ser vazia');

  Hash   := FCriptografia.Criptografar(ASenha);
  Result := FRepositorio.AtualizarSenha(ALogin, Hash);
end;

function TAutenticadorDB.DefinirDadosAlvo(const ALogin, ACodApoloLink,
  ASenhaAlvoPlano: string): Boolean;
var
  SenhaAlvoCriptografada: string;
begin
  if Trim(ACodApoloLink) = '' then
    raise EArgumentException.Create('TAutenticadorDB.DefinirDadosAlvo: usuario alvo nao pode ser vazio');
  if Trim(ASenhaAlvoPlano) = '' then
    raise EArgumentException.Create('TAutenticadorDB.DefinirDadosAlvo: senha alvo nao pode ser vazia');

  { Criptografia especifica do usuario alvo, chave fixa 35 }
  SenhaAlvoCriptografada := criptografia(35, ASenhaAlvoPlano);

  Result := FRepositorio.AtualizarDadosAlvo(ALogin, ACodApoloLink, SenhaAlvoCriptografada);
end;

end.
