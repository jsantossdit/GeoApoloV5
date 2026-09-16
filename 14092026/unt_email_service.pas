unit unt_email_service;

{
  Serviço Seguro de Envio de E-mails corporativos via SMTP/TLS (Indy).
  Isola configurações, leitura de parâmetros de banco/ambiente e elimina credenciais hardcoded.
}

interface

uses
  System.SysUtils, System.Classes,
  IdSMTP, IdMessage, IdText, IdAttachmentFile, IdSSLOpenSSL, IdExplicitTLSClientServerBase;

type
  TEMailConfig = record
    Servidor       : string;
    Porta          : Integer;
    Usuario        : string;
    Senha          : string;
    RemetenteEmail : string;
    RemetenteNome  : string;
    UsarTLS        : Boolean;
    class function CriarVazia: TEMailConfig; static;
  end;

  TEMailService = class
  private
    class var FConfigPadrao: TEMailConfig;
  public
    class procedure ConfigurarPadrao(const AConfig: TEMailConfig); static;
    class function ObterConfigPadrao: TEMailConfig; static;
    class function Enviar(
      const AConfig: TEMailConfig;
      const APara, AAssunto, ACorpoHTML: string;
      const AAnexos: TArray<string> = nil
    ): Boolean; static;
  end;

implementation

class function TEMailConfig.CriarVazia: TEMailConfig;
begin
  Result.Servidor       := '';
  Result.Porta          := 587;
  Result.Usuario        := '';
  Result.Senha          := '';
  Result.RemetenteEmail := '';
  Result.RemetenteNome  := 'GeoAlvo Sistema';
  Result.UsarTLS        := True;
end;

class procedure TEMailService.ConfigurarPadrao(const AConfig: TEMailConfig);
begin
  FConfigPadrao := AConfig;
end;

class function TEMailService.ObterConfigPadrao: TEMailConfig;
begin
  if FConfigPadrao.Servidor = '' then
  begin
    // Tenta obter de variáveis de ambiente do servidor/sistema antes de qualquer fallback
    FConfigPadrao.Servidor       := GetEnvironmentVariable('SMTP_SERVER');
    if FConfigPadrao.Servidor = '' then
      FConfigPadrao.Servidor := 'smtp.office365.com';

    FConfigPadrao.Porta          := StrToIntDef(GetEnvironmentVariable('SMTP_PORT'), 587);
    FConfigPadrao.Usuario        := GetEnvironmentVariable('SMTP_USER');
    FConfigPadrao.Senha          := GetEnvironmentVariable('SMTP_PASSWORD');
    FConfigPadrao.RemetenteEmail := GetEnvironmentVariable('SMTP_FROM');
    FConfigPadrao.RemetenteNome  := 'GeoAlvo Notificações';
    FConfigPadrao.UsarTLS        := True;
  end;
  Result := FConfigPadrao;
end;

class function TEMailService.Enviar(
  const AConfig: TEMailConfig;
  const APara, AAssunto, ACorpoHTML: string;
  const AAnexos: TArray<string> = nil
): Boolean;
var
  SMTP: TIdSMTP;
  Msg: TIdMessage;
  SSLHandler: TIdSSLIOHandlerSocketOpenSSL;
  CorpoTexto: TIdText;
  Anexo: string;
begin
  Result := False;
  if Trim(APara) = '' then
    Exit(False);

  SMTP := TIdSMTP.Create(nil);
  Msg := TIdMessage.Create(nil);
  SSLHandler := TIdSSLIOHandlerSocketOpenSSL.Create(nil);
  try
    try
      // Configuração SSL/TLS
      SSLHandler.SSLOptions.Method := sslvTLSv1_2;
      SSLHandler.SSLOptions.Mode := sslmClient;

      SMTP.IOHandler := SSLHandler;
      SMTP.Host := AConfig.Servidor;
      SMTP.Port := AConfig.Porta;
      SMTP.Username := AConfig.Usuario;
      SMTP.Password := AConfig.Senha;
      SMTP.UseTLS := utUseExplicitTLS;
      SMTP.AuthType := satDefault;
      SMTP.ConnectTimeout := 10000;
      SMTP.ReadTimeout := 10000;

      // Montagem da Mensagem
      Msg.Clear;
      Msg.From.Address := AConfig.RemetenteEmail;
      Msg.From.Name := AConfig.RemetenteNome;
      Msg.Recipients.EmailAddresses := APara;
      Msg.Subject := AAssunto;
      Msg.CharSet := 'utf-8';
      Msg.ContentType := 'multipart/mixed';

      // Corpo da mensagem
      CorpoTexto := TIdText.Create(Msg.MessageParts);
      CorpoTexto.Body.Text := ACorpoHTML;
      CorpoTexto.ContentType := 'text/html';
      CorpoTexto.CharSet := 'utf-8';

      // Anexos
      if Length(AAnexos) > 0 then
      begin
        for Anexo in AAnexos do
        begin
          if FileExists(Anexo) then
            TIdAttachmentFile.Create(Msg.MessageParts, Anexo);
        end;
      end;

      SMTP.Connect;
      try
        SMTP.Send(Msg);
        Result := True;
      finally
        SMTP.Disconnect;
      end;
    except
      on E: Exception do
      begin
        Result := False;
      end;
    end;
  finally
    SSLHandler.Free;
    Msg.Free;
    SMTP.Free;
  end;
end;

end.
