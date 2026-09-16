unit unt_alvo_api_client;

interface

uses
  System.SysUtils, System.Classes, System.IOUtils, unt_entidades_types;

type
  IAlvoAPIClient = interface
    ['{E4399066-88F4-44DF-8724-4B2E5C9A6F4E}']
    function Autenticar(const AUsuario, ASenhaPlana: string): Boolean;
    function ObterTokenValido: string;
    function EnviarEntidade(const APayloadJSON: string; out AMensagemRetorno: string): Boolean;
  end;

  TAlvoAPIClient = class(TInterfacedObject, IAlvoAPIClient)
  private
    FBaseURL    : string;
    FTokenAtual : string;
    FUsuario    : string;
    FSenha      : string;
    procedure RegistrarLogDebug(const ANomeArquivo, AConteudo: string);
  public
    constructor Create(const ABaseURL: string);
    function Autenticar(const AUsuario, ASenhaPlana: string): Boolean;
    function ObterTokenValido: string;
    function EnviarEntidade(const APayloadJSON: string; out AMensagemRetorno: string): Boolean;
  end;

implementation

constructor TAlvoAPIClient.Create(const ABaseURL: string);
begin
  inherited Create;
  FBaseURL    := ABaseURL;
  FTokenAtual := '';
end;

procedure TAlvoAPIClient.RegistrarLogDebug(const ANomeArquivo, AConteudo: string);
var
  CaminhoLog: string;
begin
  {$IFDEF DEBUG}
  CaminhoLog := TPath.Combine(TPath.GetTempPath, ANomeArquivo);
  try
    TFile.WriteAllText(CaminhoLog, AConteudo);
  except
    // Falha em log de depuracao nao interrompe a operacao
  end;
  {$ENDIF}
end;

function TAlvoAPIClient.Autenticar(const AUsuario, ASenhaPlana: string): Boolean;
begin
  FUsuario := AUsuario;
  FSenha   := ASenhaPlana;
  // TODO: Emissao do POST /api/auth/login
  Result := (FTokenAtual <> '');
end;

function TAlvoAPIClient.ObterTokenValido: string;
begin
  if FTokenAtual = '' then
  begin
    if (FUsuario <> '') and (FSenha <> '') then
      Autenticar(FUsuario, FSenha)
    else
      raise Exception.Create('Credenciais do Alvo não configuradas para esta sessão.');
  end;
  Result := FTokenAtual;
end;

function TAlvoAPIClient.EnviarEntidade(const APayloadJSON: string; out AMensagemRetorno: string): Boolean;
begin
  RegistrarLogDebug('dump_entidade_enviada.json', APayloadJSON);
  Result := True;
  AMensagemRetorno := 'Sucesso';
end;

end.
