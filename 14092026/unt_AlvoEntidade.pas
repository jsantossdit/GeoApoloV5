unit unt_AlvoEntidade;

interface

uses
  System.SysUtils, System.Classes, System.JSON, System.IOUtils,
  REST.Client, REST.Types, REST.Json;

// ============================================================
//  RECORDS DE SUPORTE (sub-objetos do JSON)
// ============================================================

type
  TCategoria = record
    Operacao        : string; // 'I'=Inserir, 'A'=Alterar, 'E'=Excluir
    Codigo          : string;
    AtivaTabelaPreco: string; // 'S' ou 'N'
    function ToJSON: TJSONObject;
  end;

  TTelefone = record
    Operacao   : string;
    Sequencia  : Integer;
    Tipo       : string; // ex: 'CEL', 'COM', 'RES'
    DDI        : string;
    DDD        : string;
    NumeroRamal: string;
    Numero     : string;
    Principal  : string; // 'S' ou 'N'
    Descricao  : string;
    NFe        : string;
    NFSe       : string;
    function ToJSON: TJSONObject;
  end;

  TEndereco = record
    Operacao                  : string;
    Sequencia                 : Integer;
    CodigoEntidade            : string;
    CodigoEntidadeRelacionada : string;
    EnderecoEntrega           : string;
    EnderecoCobranca          : string;
    EnderecoFaturamento       : string;
    EnderecoColeta            : string;
    Nome                      : string;
    Logradouro                : string;
    Endereco                  : string;
    NumeroEndereco            : string;
    NumeroEnderecoParImpar    : string;
    ComplementoEndereco       : string;
    Bairro                    : string;
    CodigoCidade              : string;
    Cep                       : string;
    TipoFisicaJuridica        : string; // 'F' ou 'J'
    CPFCNPJ                   : string;
    RGIE                      : string;
    OrgaoExpedidor            : string;
    CaixaPostal               : string;
    Email                     : string;
    PaginaWeb                 : string;
    NomeContato               : string;
    TextoLivre                : string;
    DataValidadeInicial       : TDateTime;
    DataValidadeFinal         : TDateTime;
    EnderecoCertificado       : string;
    function ToJSON: TJSONObject;
  end;

  TTelefoneContato = record
    Operacao : string;
    Sequencia: Integer;
    Tipo     : string;
    DDI      : string;
    DDD      : string;
    Numero   : string;
    Principal: string;
    function ToJSON: TJSONObject;
  end;

  TContato = record
    Operacao           : string;
    Codigo             : string;
    Nome               : string;
    NomeFantasia       : string;
    Endereco           : string;
    NumeroEndereco     : string;
    ComplementoEndereco: string;
    Bairro             : string;
    CodigoCidade       : string;
    Cep                : string;
    TipoFisicaJuridica : string;
    CPFCNPJ            : string;
    RGIE               : string;
    CodigoStatus       : string;
    Principal          : string;
    Email              : string;
    Telefones          : array of TTelefoneContato;
    function ToJSON: TJSONObject;
  end;

  TEmail = record
    Operacao : string;
    Sequencia: Integer;
    Tipo     : string; // ex: 'COM', 'PES', 'NFE'
    Url      : string;
    Email    : string;
    Principal: string;
    NFe      : string;
    NFSe     : string;
    Descricao: string;
    function ToJSON: TJSONObject;
  end;

  TVendedor = record
    Operacao          : string;
    CodigoVendedor    : string;
    Principal         : string;
    CodigoCentroCtrl  : string;
    PercentualRateio  : Double;
    function ToJSON: TJSONObject;
  end;

  TDocumento = record
    Operacao      : string;
    Sequencia     : Integer;
    Arquivo       : string;
    ArquivoBase64 : string;
    Obervacao     : string; // mantido como na API (sem 's')
    function ToJSON: TJSONObject;
  end;

// ============================================================
//  RECORD PRINCIPAL — Entidade
// ============================================================

  TEntidade = record
    // Controle
    Operacao              : string; // 'I'=Inserir, 'A'=Alterar
    Codigo                : string;
    CodigoAlternativo     : string;
    // Dados principais
    CodigoTipoTratamento  : string;
    Nome                  : string;
    NomeFantasia          : string;
    Natureza              : string;
    CodigoAtivEconomica   : string;
    CodigoOrigem          : string;
    EntidadeDesde         : string;
    DataCadastro          : string;
    // Endereço principal
    CodigoTipoLograd      : string;
    Endereco              : string;
    NumeroEndereco        : string;
    NumeroEnderecoParImpar: string;
    ComplementoEndereco   : string;
    Bairro                : string;
    CodigoCidade          : string;
    Cep                   : string;
    // Fiscal
    Tipo                  : string; // 'Física' ou 'Jurídica'
    CPFCNPJ               : string;
    RGIE                  : string;
    OrgaoExpedidor        : string;
    Agropecuarista        : string;
    InscricaoAgropecuarista:string;
    // Região / Status
    CaixaPostal           : string;
    CodigoRegiao          : string;
    Conceito              : string;
    CodigoCondPag         : string;
    AlteraCondicaoPagamento:string;
    CodigoTipoCobranca    : string;
    DataFundacao          : string;
    CodigoStatus          : string;
    CaracteristicaImovel  : Integer;
    CodigoCargo           : string;
    Genero                : string; // 'M', 'F', etc.
    // Fiscal complementar
    //InscricaoSuframa      : string;
    //CodigoExcPISCOFINS    : string;
    //MotivoDesoneracaoICMS : string;
    // Comunicação
    ComunicacaoEtiqueta     : string;
    ComunicacaoMalaDireta   : string;
    ComunicacaoEmail        : string;
    ComunicacaoFaxmarketing : string;
    ComunicacaoTelemarketing: string;
    StringDesconto          : string;
    PercentualDesconto      : integer;
    DataValidadeDesconto    : Tdatetime;
    StringAcrescimo         : string;
    PercentualAcrescimo     : integer;
    DataValidadeAcrescimo   : TDateTime;
    ContatoAposData         : string;
    // Banco
    NumeroBanco           : string;
    NumeroAgBancaria      : string;
    BancoAgenciaCamaraCompensacao:string;
    NumeroContaCorrente   : string;
    ValorLimiteCredito    : Double;
    ValorLimiteDebito     : Double;
    ValorContribuicao     : Double;

    // Arrays de sub-objetos
    Categorias : array of TCategoria;
    Telefones  : array of TTelefone;
    Enderecos  : array of TEndereco;
    Contatos   : array of TContato;
    Emails     : array of TEmail;
    Vendedores : array of TVendedor;
    Documentos : array of TDocumento;
    function ToJSON: TJSONObject;
  end;

// ============================================================
//  CLASSE DE ACESSO À API
// ============================================================

  TAlvoAPI = class
  private
    FBaseURL : string;
    FToken   : string;
    procedure ConfigurarRequest(ARequest: TRESTRequest);
  public
    constructor Create(const ABaseURL: string);
    // Login para obter token
    function Login(const AUsuario, ASenha: string): Boolean;
    // Inserir ou Alterar Entidade
    function InserirAlterarEntidade(const AEntidade: TEntidade;
                                    out AMensagem: string): Boolean;
    property Token: string read FToken write FToken;
  end;

// ============================================================
//  FUNÇÕES AUXILIARES
// ============================================================
function DateTimeToISO8601(const ADateTime: TDateTime): string;

implementation

uses
  System.DateUtils;

// ------------------------------------------------------------
//  AUXILIAR
// ------------------------------------------------------------

function DateTimeToISO8601(const ADateTime: TDateTime): string;
begin
  Result := FormatDateTime('yyyy-mm-dd"T"hh:nn:ss".000Z"', ADateTime);
end;

// ------------------------------------------------------------
//  TCategoria
// ------------------------------------------------------------

function TCategoria.ToJSON: TJSONObject;
begin
  Result := TJSONObject.Create;
  Result.AddPair('Operacao',         Operacao);
  Result.AddPair('Codigo',           Codigo);
  Result.AddPair('AtivaTabelaPreco', AtivaTabelaPreco);
end;

// ------------------------------------------------------------
//  TTelefone
// ------------------------------------------------------------

function TTelefone.ToJSON: TJSONObject;
begin
  Result := TJSONObject.Create;
  Result.AddPair('Operacao',    Operacao);
  Result.AddPair('Sequencia',   TJSONNumber.Create(Sequencia));
  Result.AddPair('Tipo',        Tipo);
  Result.AddPair('DDI',         DDI);
  Result.AddPair('DDD',         DDD);
  Result.AddPair('NumeroRamal', NumeroRamal);
  Result.AddPair('Numero',      Numero);
  Result.AddPair('Principal',   Principal);
  Result.AddPair('Descricao',   Descricao);
  Result.AddPair('NFe',         NFe);
  Result.AddPair('NFSe',        NFSe);
end;

// ------------------------------------------------------------
//  TEndereco
// ------------------------------------------------------------

function TEndereco.ToJSON: TJSONObject;
begin
  Result := TJSONObject.Create;
  Result.AddPair('Operacao',                   Operacao);
  Result.AddPair('Sequencia',                  TJSONNumber.Create(Sequencia));
  Result.AddPair('CodigoEntidade',             CodigoEntidade);
  Result.AddPair('CodigoEntidadeRelacionada',  CodigoEntidadeRelacionada);
  Result.AddPair('EnderecoEntrega',            EnderecoEntrega);
  Result.AddPair('EnderecoCobranca',           EnderecoCobranca);
  Result.AddPair('EnderecoFaturamento',        EnderecoFaturamento);
  Result.AddPair('EnderecoColeta',             EnderecoColeta);
  Result.AddPair('Nome',                       Nome);
  Result.AddPair('Logradouro',                 Logradouro);
  Result.AddPair('Endereco',                   Endereco);
  Result.AddPair('NumeroEndereco',             NumeroEndereco);
  Result.AddPair('NumeroEnderecoParImpar',     NumeroEnderecoParImpar);
  Result.AddPair('ComplementoEndereco',        ComplementoEndereco);
  Result.AddPair('Bairro',                     Bairro);
  Result.AddPair('CodigoCidade',               CodigoCidade);
  Result.AddPair('Cep',                        Cep);
  Result.AddPair('TipoFisicaJuridica',         TipoFisicaJuridica);
  Result.AddPair('CPFCNPJ',                    CPFCNPJ);
  Result.AddPair('RGIE',                       RGIE);
  Result.AddPair('OrgaoExpedidor',             OrgaoExpedidor);
  Result.AddPair('CaixaPostal',                CaixaPostal);
  Result.AddPair('Email',                      Email);
  Result.AddPair('PaginaWeb',                  PaginaWeb);
  Result.AddPair('NomeContato',                NomeContato);
  Result.AddPair('TextoLivre',                 TextoLivre);
  Result.AddPair('DataValidadeInicial',        DateToISO8601(DataValidadeInicial));
  Result.AddPair('DataValidadeFinal',          DateToISO8601(DataValidadeFinal));
  Result.AddPair('EnderecoCertificado',        EnderecoCertificado);
end;

// ------------------------------------------------------------
//  TTelefoneContato
// ------------------------------------------------------------

function TTelefoneContato.ToJSON: TJSONObject;
begin
  Result := TJSONObject.Create;
  Result.AddPair('Operacao',  Operacao);
  Result.AddPair('Sequencia', TJSONNumber.Create(Sequencia));
  Result.AddPair('Tipo',      Tipo);
  Result.AddPair('DDI',       DDI);
  Result.AddPair('DDD',       DDD);
  Result.AddPair('Numero',    Numero);
  Result.AddPair('Principal', Principal);
end;

// ------------------------------------------------------------
//  TContato
// ------------------------------------------------------------

function TContato.ToJSON: TJSONObject;
var
  jTels: TJSONArray;
  i: Integer;
begin
  Result := TJSONObject.Create;
  Result.AddPair('Operacao',            Operacao);
  Result.AddPair('Codigo',              Codigo);
  Result.AddPair('Nome',                Nome);
  Result.AddPair('NomeFantasia',        NomeFantasia);
  Result.AddPair('Endereco',            Endereco);
  Result.AddPair('NumeroEndereco',      NumeroEndereco);
  Result.AddPair('ComplementoEndereco', ComplementoEndereco);
  Result.AddPair('Bairro',              Bairro);
  Result.AddPair('CodigoCidade',        CodigoCidade);
  Result.AddPair('Cep',                 Cep);
  Result.AddPair('TipoFisicaJuridica',  TipoFisicaJuridica);
  Result.AddPair('CPFCNPJ',             CPFCNPJ);
  Result.AddPair('RGIE',                RGIE);
  Result.AddPair('CodigoStatus',        CodigoStatus);
  Result.AddPair('Principal',           Principal);
  Result.AddPair('Email',               Email);

  jTels := TJSONArray.Create;
  for i := 0 to High(Telefones) do
    jTels.AddElement(Telefones[i].ToJSON);
  Result.AddPair('Telefones', jTels);
end;

// ------------------------------------------------------------
//  TEmail
// ------------------------------------------------------------

function TEmail.ToJSON: TJSONObject;
begin
  Result := TJSONObject.Create;
  Result.AddPair('Operacao',  Operacao);
  Result.AddPair('Sequencia', TJSONNumber.Create(Sequencia));
  Result.AddPair('Tipo',      Tipo);
  Result.AddPair('Url',       Url);
  Result.AddPair('Email',     Email);
  Result.AddPair('Principal', Principal);
  Result.AddPair('NFe',       NFe);
  Result.AddPair('NFSe',      NFSe);
  Result.AddPair('Descricao', Descricao);
end;

// ------------------------------------------------------------
//  TVendedor
// ------------------------------------------------------------

function TVendedor.ToJSON: TJSONObject;
begin
  Result := TJSONObject.Create;
  Result.AddPair('Operacao',         Operacao);
  Result.AddPair('CodigoVendedor',   CodigoVendedor);
  Result.AddPair('Principal',        Principal);
  Result.AddPair('CodigoCentroCtrl', CodigoCentroCtrl);
  Result.AddPair('PercentualRateio', TJSONNumber.Create(PercentualRateio));
end;

// ------------------------------------------------------------
//  TDocumento
// ------------------------------------------------------------

function TDocumento.ToJSON: TJSONObject;
begin
  Result := TJSONObject.Create;
  Result.AddPair('Operacao',      Operacao);
  Result.AddPair('Sequencia',     TJSONNumber.Create(Sequencia));
  Result.AddPair('Arquivo',       Arquivo);
  Result.AddPair('ArquivoBase64', ArquivoBase64);
  Result.AddPair('Obervacao',     Obervacao); // sem 's' - igual à API
end;

// ------------------------------------------------------------
//  TEntidade.ToJSON — monta o JSON completo
// ------------------------------------------------------------

function TEntidade.ToJSON: TJSONObject;
var
  jArr: TJSONArray;
  i: Integer;
begin
  Result := TJSONObject.Create;

  // Campos principais
  Result.AddPair('Operacao',               Operacao);
  Result.AddPair('Codigo',                 Codigo);
  Result.AddPair('CodigoAlternativo',      CodigoAlternativo);
  Result.AddPair('CodigoTipoTratamento',   CodigoTipoTratamento);
  Result.AddPair('Nome',                   Nome);
  Result.AddPair('NomeFantasia',           NomeFantasia);
  Result.AddPair('Natureza',               Natureza);
  Result.AddPair('CodigoTipoLograd',       CodigoTipoLograd);
  Result.AddPair('Endereco',               Endereco);
  Result.AddPair('NumeroEndereco',         NumeroEndereco);
  Result.AddPair('NumeroEnderecoParImpar', NumeroEnderecoParImpar);
  Result.AddPair('ComplementoEndereco',    ComplementoEndereco);
  Result.AddPair('Bairro',                 Bairro);
  Result.AddPair('CodigoCidade',           CodigoCidade);
  Result.AddPair('Cep',                    Cep);
  Result.AddPair('Tipo',                   Tipo);
  Result.AddPair('CPFCNPJ',               CPFCNPJ);
  Result.AddPair('RGIE',                   RGIE);
  Result.AddPair('OrgaoExpedidor',         OrgaoExpedidor);
  Result.AddPair('Agropecuarista',         Agropecuarista);
  Result.AddPair('InscricaoAgropecuarista',InscricaoAgropecuarista);
  Result.AddPair('CaixaPostal',            CaixaPostal);
  Result.AddPair('CodigoRegiao',           CodigoRegiao);
  Result.AddPair('Conceito',               Conceito);
  Result.AddPair('CodigoCondPag',          CodigoCondPag);
  Result.AddPair('AlteraCondicaoPagamento', AlteraCondicaoPagamento);
  Result.AddPair('CodigoTipoCobranca',     CodigoTipoCobranca);
  Result.AddPair('CodigoCargo',            CodigoCargo);
  Result.AddPair('Genero',                 Genero);
  Result.AddPair('ComunicacaoEtiqueta',    ComunicacaoEtiqueta);
  Result.AddPair('ComunicacaoMalaDireta',  ComunicacaoMalaDireta);
  Result.AddPair('ComunicacaoEmail',       ComunicacaoEmail);
  Result.AddPair('ComunicacaoTelemarketing', ComunicacaoTelemarketing);
  Result.AddPair('StringDesconto',         StringDesconto);
  Result.AddPair('PercentualDesconto',     PercentualDesconto);
  Result.AddPair('DataValidadeDesconto',   TJsonNull.create);
  Result.AddPair('StringAcrescimo',        StringAcrescimo);
  Result.AddPair('PercentualAcrescimo',    PercentualAcrescimo);
  Result.AddPair('DataValidadeAcrescimo',  TJsonNull.create);
  Result.AddPair('ContatoAposData',        ContatoAposData);
  Result.AddPair('CodigoRegiao',           CodigoRegiao);
  Result.AddPair('CodigoStatus',           CodigoStatus);
  Result.AddPair('CaracteristicaImovel',   TJSONNumber.Create(CaracteristicaImovel));
  Result.AddPair('DataFundacao',           DataFundacao);
 // Result.AddPair('InscricaoSuframa',       InscricaoSuframa);
 // Result.AddPair('CodigoExcPISCOFINS',     CodigoExcPISCOFINS);
 // Result.AddPair('MotivoDesoneracaoICMS',  MotivoDesoneracaoICMS);
  Result.AddPair('NumeroBanco',            NumeroBanco);
  Result.AddPair('NumeroAgBancaria',       NumeroAgBancaria);
  Result.AddPair('NumeroContaCorrente',    NumeroContaCorrente);
  Result.AddPair('ValorContribuicao',      TJSONNumber.Create(ValorContribuicao));


  // Categorias
  jArr := TJSONArray.Create;
  for i := 0 to High(Categorias) do
    jArr.AddElement(Categorias[i].ToJSON);
  Result.AddPair('Categorias', jArr);

  // Telefones
  jArr := TJSONArray.Create;
  for i := 0 to High(Telefones) do
    jArr.AddElement(Telefones[i].ToJSON);
  Result.AddPair('Telefones', jArr);

  // Enderecos
  jArr := TJSONArray.Create;
  for i := 0 to High(Enderecos) do
    jArr.AddElement(Enderecos[i].ToJSON);
  Result.AddPair('Enderecos', jArr);

  // Contatos
  jArr := TJSONArray.Create;
  for i := 0 to High(Contatos) do
    jArr.AddElement(Contatos[i].ToJSON);
  Result.AddPair('Contatos', jArr);

  // Emails
  jArr := TJSONArray.Create;
  for i := 0 to High(Emails) do
    jArr.AddElement(Emails[i].ToJSON);
  Result.AddPair('Emails', jArr);

  // Vendedores
  jArr := TJSONArray.Create;
  for i := 0 to High(Vendedores) do
    jArr.AddElement(Vendedores[i].ToJSON);
  Result.AddPair('Vendedores', jArr);

  // Documentos
  jArr := TJSONArray.Create;
  for i := 0 to High(Documentos) do
    jArr.AddElement(Documentos[i].ToJSON);
  Result.AddPair('Documentos', jArr);
end;

// ============================================================
//  TAlvoAPI
// ============================================================

constructor TAlvoAPI.Create(const ABaseURL: string);
begin
  inherited Create;
  FBaseURL := ABaseURL;
  FToken   := '';
end;

procedure TAlvoAPI.ConfigurarRequest(ARequest: TRESTRequest);
begin
 { if FToken <> '' then
    ARequest.AddParameter(
      'Authorization',
      'Bearer ' + FToken,
      pkHTTPHEADER,
      [poDoNotEncode]
    );    }
  if FToken <> '' then
    ARequest.AddParameter(
      'Riosoft-Token',
      FToken,
      pkHTTPHEADER,
      [poDoNotEncode]
    );
end;

// ------------------------------------------------------------
//  Login — obtém o token JWT
// ------------------------------------------------------------
function TAlvoAPI.Login(const AUsuario, ASenha: string): Boolean;
var
  Client  : TRESTClient;
  Request : TRESTRequest;
  Response: TRESTResponse;
  jBody   : TJSONObject;
  jResp   : TJSONValue;
begin
  Result  := False;
  Client  := TRESTClient.Create(nil);
  Request := TRESTRequest.Create(nil);
  Response:= TRESTResponse.Create(nil);
  jBody   := TJSONObject.Create;
  try
    Client.BaseURL    := FBaseURL;
    Request.Client    := Client;
    Request.Response  := Response;
    Request.Method    := rmPOST;
    Request.Resource  := 'Auth/Login'; // ajuste se necessário

    jBody.AddPair('usuario', AUsuario);
    jBody.AddPair('senha',   ASenha);
    Request.AddBody(jBody.ToString, ctAPPLICATION_JSON);
    Request.Execute;

    if Response.StatusCode = 200 then
    begin
      jResp := TJSONObject.ParseJSONValue(Response.Content);
      try
        FToken := jResp.GetValue<string>('token');
        Result := FToken <> '';
      finally
        jResp.Free;
      end;
    end;
  finally
    jBody.Free;
    Response.Free;
    Request.Free;
    Client.Free;
  end;
end;

function TAlvoAPI.InserirAlterarEntidade(const AEntidade: TEntidade;
                                          out AMensagem: string): Boolean;
var
  Client  : TRESTClient;
  Request : TRESTRequest;
  Response: TRESTResponse;
  jBody   : TJSONObject;
begin
  Result   := False;
  AMensagem:= '';
  Client   := TRESTClient.Create(nil);
  Request  := TRESTRequest.Create(nil);
  Response := TRESTResponse.Create(nil);
  try
    Client.BaseURL   := FBaseURL;
    Request.Client   := Client;
    Request.Response := Response;
    Request.Method   := rmPOST;
    Request.Resource := 'Entidade/InserirAlterarEntidade';
    ConfigurarRequest(Request);
    jBody := AEntidade.ToJSON;
    try
      // ---- DUMP PARA ANÁLISE ----
      TFile.WriteAllText('c:\temp\dump_inserir_alterar_entidade.json', jBody.Format(2));
      {Clipboard.AsText := jBody.Format(2);
      ShellExecute(0, 'open', 'notepad.exe',
                   PChar('c:\temp\dump_inserir_alterar_entidade.json'), nil, SW_SHOWNORMAL);   }
      // ---------------------------

      Request.AddBody(jBody.ToString, ctAPPLICATION_JSON);
    finally
      jBody.Free;
    end;
    Request.Execute;
    AMensagem := Response.Content;
    Result    := Response.StatusCode in [200, 201];
    if not Result then
      AMensagem := Format('Erro HTTPS %d: %s',
                          [Response.StatusCode, Response.Content]);
  finally
    Response.Free;
    Request.Free;
    Client.Free;
  end;
end;

end.
