unit unt_ViaCEPUtils;

interface

uses
  System.SysUtils, System.JSON, System.Net.HttpClient, System.Net.URLClient;

type
  TEnderecoInfo = record
    Logradouro: string;
    Cidade: string;
    Bairro: string;
    UF: string;
    CEP: string;
    Erro: Boolean;
    MensagemErro: string;
  end;

function ConsultarCEP(const CEP: string): TEnderecoInfo;

implementation

function ConsultarCEP(const CEP: string): TEnderecoInfo;
var
  HttpClient: THTTPClient;
  Response: IHTTPResponse;
  JSONResponse: TJSONObject;
  CEPLimpo: string;
  URL: string;
begin
  // Inicializa o resultado
  Result.Logradouro := '';
  Result.Cidade := '';
  Result.Bairro := '';
  Result.UF := '';
  Result.CEP := '';
  Result.Erro := False;
  Result.MensagemErro := '';

  // Remove caracteres não numéricos do CEP
  CEPLimpo := CEP.Replace('-', '').Replace('.', '').Replace(' ', '');

  // Valida se o CEP tem 8 dígitos
  if (Length(CEPLimpo) <> 8) then
  begin
    Result.Erro := True;
    Result.MensagemErro := 'CEP deve conter exatamente 8 dígitos';
    Exit;
  end;

  // Valida se contém apenas números
  var TempInt64: Int64;
  if not TryStrToInt64(CEPLimpo, TempInt64) then
  begin
    Result.Erro := True;
    Result.MensagemErro := 'CEP deve conter apenas números';
    Exit;
  end;

  HttpClient := THTTPClient.Create;
  try
    try
      // Monta a URL da API do ViaCEP
      URL := Format('https://viacep.com.br/ws/%s/json/', [CEPLimpo]);

      // Faz a requisição HTTP
      Response := HttpClient.Get(URL);

      // Verifica se a requisição foi bem-sucedida
      if Response.StatusCode = 200 then
      begin
        // Parse do JSON de resposta
        JSONResponse := TJSONObject.ParseJSONValue(Response.ContentAsString) as TJSONObject;
        try
          // Verifica se retornou erro (CEP não encontrado)
          if JSONResponse.GetValue('erro') <> nil then
          begin
            Result.Erro := True;
            Result.MensagemErro := 'CEP não encontrado';
          end
          else
          begin
            // Extrai os dados do JSON
            Result.CEP := JSONResponse.GetValue('cep').Value;
            Result.Logradouro := JSONResponse.GetValue('logradouro').Value;
            Result.Bairro := JSONResponse.GetValue('bairro').Value;
            Result.Cidade := JSONResponse.GetValue('localidade').Value;
            Result.UF := JSONResponse.GetValue('uf').Value;
          end;
        finally
          JSONResponse.Free;
        end;
      end
      else
      begin
        Result.Erro := True;
        Result.MensagemErro := Format('Erro na requisição HTTP: %d - %s',
          [Response.StatusCode, Response.StatusText]);
      end;

    except
      on E: Exception do
      begin
        Result.Erro := True;
        Result.MensagemErro := 'Erro ao consultar CEP: ' + E.Message;
      end;
    end;
  finally
    HttpClient.Free;
  end;
end;

end.
