unit unt_logon_interfaces;

{
  GeoApolo - Interfaces do subsistema de Logon
  Responsabilidade: contratos (interfaces) que desacoplam implementacao de consumidores.
  Nenhuma dependencia de VCL, FireDAC ou formularios.
}

interface

uses
  SysUtils;

type

  { ------------------------------------------------------------------ }
  { Dados transferidos entre camadas (Value Objects)                     }
  { ------------------------------------------------------------------ }

  TCredenciais = record
    Login: string;
    Senha: string;
  end;

  TDadosUsuario = record
    CodUsuario   : string;
    Login        : string;
    NomeCompleto : string;
    CodApoloLink : string;   // usucod_apolo
    SenhaHash    : string;   // armazenada criptografada
    SenhaAlvo    : string;   // senha_alvo, armazenada criptografada (chave 35)
    Ativo        : Boolean;
  end;

  TDadosBanco = record
    NomeServidor : string;
    NomeBanco    : string;
    IPServidor   : string;
    Usuario      : string;
    Senha        : string;   // ja decriptografada
    Protocolo    : string;
  end;

  TDadosLicenca = record
    IDPalavra        : string;
    Bloqueia         : Boolean;
    DiasTolerancia   : Integer;
    FlagAtivo        : Boolean;
    DataFinal        : TDateTime;
    MesReferencia    : Integer;
    AnoReferencia    : Integer;
  end;

  TResultadoAutenticacao = record
    Sucesso        : Boolean;
    MensagemErro   : string;
    DadosUsuario   : TDadosUsuario;
    CodigoSistema  : Integer;
  end;

  { ------------------------------------------------------------------ }
  { IRepositorioUsuario                                                  }
  { ------------------------------------------------------------------ }
  IRepositorioUsuario = interface
    ['{A1B2C3D4-0001-0001-0001-000000000001}']
    { Busca usuario por login retornando True se encontrado e ativo }
    function BuscarPorLogin(const ALogin: string; out AUsuario: TDadosUsuario): Boolean;
    { Busca codigo do sistema pela sigla }
    function BuscarCodigoSistema(const ASigla: string; out ACodigo: Integer): Boolean;
    { Verifica se usuario tem permissao no sistema }
    function UsuarioPossuiPermissaoSistema(const ACodUsuario: string;
      ACodigoSistema: Integer): Boolean;
    { Atualiza a senha do usuario }
    function AtualizarSenha(const ALogin, ASenhaHash: string): Boolean;
    { Grava usucod_apolo e senha_alvo (ja criptografada) do usuario }
    function AtualizarDadosAlvo(const ALogin, ACodApoloLink,
      ASenhaAlvoHash: string): Boolean;
  end;

  { ------------------------------------------------------------------ }
  { IRepositorioLicenca                                                  }
  { ------------------------------------------------------------------ }
  IRepositorioLicenca = interface
    ['{A1B2C3D4-0002-0001-0001-000000000002}']
    function BuscarLicencaMesAtual(AMes, AAno: Integer;
      out ALicenca: TDadosLicenca): Boolean;
    function BloquearLicenca(const AIDPalavra: string): Boolean;
  end;

  { ------------------------------------------------------------------ }
  { IConfiguracaoAcesso                                                  }
  { Abstrai leitura do Registry (ou outra fonte)                         }
  { ------------------------------------------------------------------ }
  IConfiguracaoAcesso = interface
    ['{A1B2C3D4-0003-0001-0001-000000000003}']
    function ConfiguracaoBancoExiste: Boolean;
    function LerDadosBanco(out ADados: TDadosBanco): Boolean;
  end;

  { ------------------------------------------------------------------ }
  { ICriptografia                                                        }
  { ------------------------------------------------------------------ }
  ICriptografia = interface
    ['{A1B2C3D4-0004-0001-0001-000000000004}']
    function Criptografar(const ATexto: string): string;
    function Decriptografar(const AHash: string): string;
  end;

  { ------------------------------------------------------------------ }
  { IServicoNTP                                                          }
  { ------------------------------------------------------------------ }
  IServicoNTP = interface
    ['{A1B2C3D4-0005-0001-0001-000000000005}']
    function ObterDataHora(const AHost: string; APorta: Integer;
      out ADataHora: TDateTime): Boolean;
  end;

  { ------------------------------------------------------------------ }
  { IAutenticador                                                        }
  { Orquestra a autenticacao de um usuario                               }
  { ------------------------------------------------------------------ }
  IAutenticador = interface
    ['{A1B2C3D4-0006-0001-0001-000000000006}']
    function Autenticar(const ACred: TCredenciais;
      out AResultado: TResultadoAutenticacao): Boolean;
    { Retorna True se o campo senha do usuario esta em branco no banco }
    function SenhaCadastradaEmBranco(const ALogin: string): Boolean;
    { Grava nova senha quando usuario nao tinha senha }
    function DefinirPrimeiraSenha(const ALogin, ASenha: string): Boolean;
    { Grava usucod_apolo e senha_alvo (criptografando a senha em texto puro com a chave 35) }
    function DefinirDadosAlvo(const ALogin, ACodApoloLink,
      ASenhaAlvoPlano: string): Boolean;
  end;

  { ------------------------------------------------------------------ }
  { IValidadorLicenca                                                    }
  { ------------------------------------------------------------------ }
  TResultadoLicenca = (
    rlLicencaOk,
    rlLicencaBloqueada,
    rlChaveNaoAtivada,
    rlDentroToleranciaBloqueando,
    rlErroConsulta
  );

  IValidadorLicenca = interface
    ['{A1B2C3D4-0007-0001-0001-000000000007}']
    function ValidarLicencaAtual(out AResultado: TResultadoLicenca;
      out AMensagem: string): Boolean;
  end;

  { ------------------------------------------------------------------ }
  { ILogonController                                                     }
  { Ponto de entrada principal para a camada de apresentacao             }
  { ------------------------------------------------------------------ }
  TEventoLogon = (
    elNecessarioConfigurarBanco,
    elBancoNaoConfigurado,
    elCredenciaisVazias,
    elUsuarioInativo,
    elSenhaInvalida,
    elSenhaNaoCadastrada,
    elPermissaoNegada,
    elAtualizacaoDisponivel,
    elLogonSucesso,
    elLicencaInvalida
  );

  ILogonController = interface
    ['{A1B2C3D4-0008-0001-0001-000000000008}']
    function ExecutarLogon(const ACred: TCredenciais;
      out AEvento: TEventoLogon;
      out AResultado: TResultadoAutenticacao): Boolean;
    function ValidarLicenca(out AEvento: TEventoLogon;
      out AMensagem: string): Boolean;
    function ConfirmarPrimeiraSenha(const ALogin, ASenha: string): Boolean;
    function CarregarConfiguracoesBanco(out ADados: TDadosBanco): Boolean;
    { Grava usuario/senha do sistema alvo quando usucod_apolo ainda nao esta configurado }
    function DefinirCredenciaisAlvo(const ALogin, ACodApoloLink,
      ASenhaAlvoPlano: string; out AMensagemErro: string): Boolean;
  end;

implementation

end.
