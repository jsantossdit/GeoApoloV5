unit unt_viacep_service;

{
  Serviço REST para consulta de CEP via API ViaCEP.
  Utiliza System.Net.HttpClient e System.JSON (nativos, leves e thread-safe).
}

interface

uses
  System.SysUtils, System.Classes, System.Net.HttpClient, System.JSON,
  unt_document_validators;

type
  TViaCEPDTO = record
    CEP         : string;
    Logradouro  : string;
    Complemento : string;
    Bairro      : string;
    Cidade      : string;
    UF          : string;
    IBGE        : string;
    DDD         : string;
    Sucesso     : Boolean;
    Mensagem    : string;
  end;

  TViaCEPService = class
  public
    class function Consultar(const ACEP: string; out AResultado: TViaCEPDTO): Boolean; static;
  end;

implementation

class function TViaCEPService.Consultar(const ACEP: string; out AResultado: TViaCEPDTO): Boolean;
var
  HttpClient: THTTPClient;
  HttpResponse: IHTTPResponse;
  URL, CEPLimpo: string;
  JsonObj: TJSONObject;
begin
  FillChar(AResultado, SizeOf(AResultado), 0);
  CEPLimpo := TDocumentValidators.LimparFormatacao(ACEP);

  if Length(CEPLimpo) <> 8 then
  begin
    AResultado.Sucesso := False;
    AResultado.Mensagem := 'CEP informado deve conter exatamente 8 dígitos.';
    Exit(False);
  end;

  HttpClient := THTTPClient.Create;
  try
    HttpClient.ConnectionTimeout := 5000;
    HttpClient.ResponseTimeout := 7000;
    URL := Format('https://viacep.com.br/ws/%s/json/', [CEPLimpo]);

    try
      HttpResponse := HttpClient.Get(URL);
      if HttpResponse.StatusCode <> 200 then
      begin
        AResultado.Sucesso := False;
        AResultado.Mensagem := Format('Erro na consulta ViaCEP. Status: %d', [HttpResponse.StatusCode]);
        Exit(False);
      end;

      JsonObj := TJSONObject.ParseJSONValue(HttpResponse.ContentAsString(TEncoding.UTF8)) as TJSONObject;
      if not Assigned(JsonObj) then
      begin
        AResultado.Sucesso := False;
        AResultado.Mensagem := 'Resposta inválida do serviço ViaCEP.';
        Exit(False);
      end;

      try
        // ViaCEP retorna {"erro": "true"} quando o CEP não é localizado
        if JsonObj.GetValue('erro') <> nil then
        begin
          AResultado.Sucesso := False;
          AResultado.Mensagem := 'CEP não encontrado na base do ViaCEP.';
          Exit(False);
        end;

        AResultado.CEP         := JsonObj.GetValue<string>('cep', '');
        AResultado.Logradouro  := JsonObj.GetValue<string>('logradouro', '');
        AResultado.Complemento := JsonObj.GetValue<string>('complemento', '');
        AResultado.Bairro      := JsonObj.GetValue<string>('bairro', '');
        AResultado.Cidade      := JsonObj.GetValue<string>('localidade', '');
        AResultado.UF          := JsonObj.GetValue<string>('uf', '');
        AResultado.IBGE        := JsonObj.GetValue<string>('ibge', '');
        AResultado.DDD         := JsonObj.GetValue<string>('ddd', '');
        AResultado.Sucesso     := True;
        AResultado.Mensagem    := 'Consulta realizada com sucesso.';
        Result := True;
      finally
        JsonObj.Free;
      end;
    except
      on E: Exception do
      begin
        AResultado.Sucesso := False;
        AResultado.Mensagem := 'Falha na comunicação com ViaCEP: ' + E.Message;
        Result := False;
      end;
    end;
  finally
    HttpClient.Free;
  end;
end;

end.
