unit unt_importeventos_model;

interface

uses
  System.SysUtils, System.Classes, System.Generics.Collections, System.DateUtils;

type
  /// <summary>Resultado de uma busca de entidade (cliente/fornecedor) no Apolo.</summary>
  TInfoEntidade = record
    EntCod: string;
    EntNome: string;
    Encontrado: Boolean;
  end;

  /// <summary>Vínculo do documento (CPF/CNPJ) com a base Apolo: categoria de projetos e
  /// se colabora (tem categoria E contribuição registrada).</summary>
  TInfoVinculoApolo = record
    EntCod: string;
    CategCodEstr: string;
    AnoMesUltimaContribuicao: string;
    ColaboraProjetos: Boolean;
    function Encontrado: Boolean;
  end;

  /// <summary>Layout completo (planilha com todas as colunas financeiras/comerciais).</summary>
  TDadosInscricaoCompleta = record
    Fatura, StatusInscricao, FormaPagamento, NParcelas, Moeda, Contrato: string;
    DataCriacao, DataPagamento, DataCredito, DataReembolso: TDate;
    TipoReembolso, SKU, Produto, Quantidade, AfiliadoPrincipal, Cupom: string;
    ValorCupom, ValorVenda, ValorVendaComJuros, ValorItem, ValorReembolsado,
      ValorFrete, Taxa, Outros, Antecipacao, Comissao, Parceiro, GanhoLiquido: Currency;
    ClienteNome, ClienteEmail, ClienteFones, ClienteTipoDocumento, ClienteDocumento: string;
    Endereco, Numero, Complemento, Bairro, CEP, Cidade, IBGE, UF: string;
    UTMSource, UTMCampaign, UTMMedium, UTMContent, URLBoleto: string;
  end;

  /// <summary>Layout reduzido (planilha simplificada, só cadastro/endereço).</summary>
  TDadosInscricaoReduzida = record
    StatusInscricao, Produto, ClienteNome, ClienteEmail, DocumentoCliente: string;
    Endereco, Numero, Complemento, Bairro, CEP, Cidade, UF: string;
  end;

  TResultadoImportacao = record
    TotalLinhas: Integer;
    TotalComDocumento: Integer;
    TotalVinculadosApolo: Integer;
  end;

  /// <summary>Uma linha da planilha, com valores acessíveis por nome de coluna
  /// (o cabeçalho da 1a linha do arquivo), evitando índices mágicos.</summary>
  TLinhaPlanilha = class
  private
    FValores: TDictionary<string, string>;
    function Chave(const ACampo: string): string; inline;
  public
    constructor Create;
    destructor Destroy; override;
    procedure DefinirValor(const ACampo, AValor: string);
    function TemCampo(const ACampo: string): Boolean;
    function ValorTexto(const ACampo: string; const ADefault: string = ''): string;
    function ValorMoeda(const ACampo: string; const ADefault: Currency = 0;
      ARemoverSinal: Boolean = False): Currency;
    function ValorData(const ACampo: string; const ADefault: TDate): TDate;
  end;

  TPlanilhaImportada = class
  private
    FLinhas: TObjectList<TLinhaPlanilha>;
  public
    constructor Create;
    destructor Destroy; override;
    property Linhas: TObjectList<TLinhaPlanilha> read FLinhas;
    function Count: Integer;
  end;

/// <summary>Mantém apenas dígitos (uso em CPF/CNPJ, CEP).</summary>
function SomenteDigitos(const AValor: string): string;

implementation

{ TInfoVinculoApolo }

function TInfoVinculoApolo.Encontrado: Boolean;
begin
  Result := EntCod <> '';
end;

{ TLinhaPlanilha }

constructor TLinhaPlanilha.Create;
begin
  inherited Create;
  FValores := TDictionary<string, string>.Create;
end;

destructor TLinhaPlanilha.Destroy;
begin
  FValores.Free;
  inherited Destroy;
end;

function TLinhaPlanilha.Chave(const ACampo: string): string;
begin
  Result := UpperCase(Trim(ACampo));
end;

procedure TLinhaPlanilha.DefinirValor(const ACampo, AValor: string);
begin
  FValores.AddOrSetValue(Chave(ACampo), AValor);
end;

function TLinhaPlanilha.TemCampo(const ACampo: string): Boolean;
begin
  Result := FValores.ContainsKey(Chave(ACampo));
end;

function TLinhaPlanilha.ValorTexto(const ACampo: string; const ADefault: string): string;
begin
  if not FValores.TryGetValue(Chave(ACampo), Result) then
    Result := ADefault;
end;

function TLinhaPlanilha.ValorMoeda(const ACampo: string; const ADefault: Currency;
  ARemoverSinal: Boolean): Currency;
var
  vTexto: string;
begin
  vTexto := Trim(ValorTexto(ACampo, ''));
  if vTexto = '' then
    Exit(ADefault);
  if ARemoverSinal then
    vTexto := StringReplace(vTexto, '-', '', [rfReplaceAll]);
  vTexto := StringReplace(vTexto, '.', '', [rfReplaceAll]);   // separador de milhar
  vTexto := StringReplace(vTexto, ',', '.', [rfReplaceAll]);  // separador decimal BR -> US
  if not TryStrToCurr(vTexto, Result, TFormatSettings.Invariant) then
    Result := ADefault;
end;

function TLinhaPlanilha.ValorData(const ACampo: string; const ADefault: TDate): TDate;
var
  vTexto: string;
  vFmt: TFormatSettings;
  vDataHora: TDateTime;
begin
vTexto := Copy(vTexto, 1, 10);
vFmt := TFormatSettings.Invariant;
vFmt.DateSeparator := '/';
vFmt.ShortDateFormat := 'dd/mm/yyyy';
if TryStrToDate(vTexto, vDataHora, vFmt) or TryStrToDate(vTexto, vDataHora) then
  Result := TDate(vDataHora)
else
  Result := ADefault;
end;

{ TPlanilhaImportada }

constructor TPlanilhaImportada.Create;
begin
  inherited Create;
  FLinhas := TObjectList<TLinhaPlanilha>.Create(True);
end;

destructor TPlanilhaImportada.Destroy;
begin
  FLinhas.Free;
  inherited Destroy;
end;

function TPlanilhaImportada.Count: Integer;
begin
  Result := FLinhas.Count;
end;

function SomenteDigitos(const AValor: string): string;
var
  vChar: Char;
begin
  Result := '';
  for vChar in AValor do
    if CharInSet(vChar, ['0'..'9']) then
      Result := Result + vChar;
end;

end.
