unit unt_importeventos_controller;

interface

uses
  System.SysUtils, System.Classes, FireDAC.Comp.Client,
  unt_importeventos_model, unt_importeventos_repository,
  unt_importeventos_servico, unt_importeventos_leitorplanilha;

const
  STATUS_INSCRICAO_VALIDOS: array [0..3] of string = ('Paga', 'Aberta', 'Cancelada', 'Reembolsado');

type
  TProgressoImportacaoEvent = reference to procedure(AAtual, ATotal: Integer);

  /// <summary>Orquestra o caso de uso "importar inscritos de evento", layout
  /// completo ou reduzido. Não conhece TForm nem TStringGrid — depende só das
  /// interfaces de repositório, serviço e leitor de planilha (injeção de
  /// dependência), o que permite testar a lógica sem UI e sem banco real.</summary>
  TControllerImportacaoEventos = class
  private
    FRepositorio: IRepositorioCongressoRcc;
    FServicoVinculo: IServicoVinculoApolo;
    FLeitor: IImportadorPlanilha;
    FOnProgresso: TProgressoImportacaoEvent;
    function MapearLinhaCompleta(ALinha: TLinhaPlanilha): TDadosInscricaoCompleta;
    function MapearLinhaReduzida(ALinha: TLinhaPlanilha): TDadosInscricaoReduzida;
    function StatusValido(const AStatus: string): Boolean;
  public
    constructor Create(ARepositorio: IRepositorioCongressoRcc; AServicoVinculo: IServicoVinculoApolo;
      ALeitor: IImportadorPlanilha);
    property OnProgresso: TProgressoImportacaoEvent read FOnProgresso write FOnProgresso;

    function EventoJaImportado(const AIdEvento: string): Boolean;
    procedure RemoverImportacaoAnterior(const AIdEvento: string);

    function ImportarLayoutCompleto(const AIdEvento, AArquivo: string): TResultadoImportacao;
    function ImportarLayoutReduzido(const AIdEvento, AArquivo: string): TResultadoImportacao;

    /// <summary>Dataset (aberto) com os eventos disponíveis para importação.
    /// O chamador é responsável por liberar o TFDQuery retornado.</summary>
    function ListarEventosDisponiveis: TFDQuery;
  end;

implementation

{ TControllerImportacaoEventos }

constructor TControllerImportacaoEventos.Create(ARepositorio: IRepositorioCongressoRcc;
  AServicoVinculo: IServicoVinculoApolo; ALeitor: IImportadorPlanilha);
begin
  inherited Create;
  FRepositorio := ARepositorio;
  FServicoVinculo := AServicoVinculo;
  FLeitor := ALeitor;
end;

function TControllerImportacaoEventos.EventoJaImportado(const AIdEvento: string): Boolean;
begin
  Result := FRepositorio.ExisteImportacao(AIdEvento);
end;

function TControllerImportacaoEventos.ListarEventosDisponiveis: TFDQuery;
begin
  Result := FRepositorio.ListarEventos;
end;

procedure TControllerImportacaoEventos.RemoverImportacaoAnterior(const AIdEvento: string);
begin
  FRepositorio.ExcluirImportacao(AIdEvento);
end;

function TControllerImportacaoEventos.StatusValido(const AStatus: string): Boolean;
var
  vStatus: string;
begin
  for vStatus in STATUS_INSCRICAO_VALIDOS do
    if SameText(vStatus, AStatus) then
      Exit(True);
  Result := False;
end;

function TControllerImportacaoEventos.MapearLinhaCompleta(ALinha: TLinhaPlanilha): TDadosInscricaoCompleta;
const
  DATA_PADRAO: TDate = 36526; // 01/01/2000
begin
  Result := Default (TDadosInscricaoCompleta);
  Result.Fatura := ALinha.ValorTexto('Fatura');
  Result.StatusInscricao := ALinha.ValorTexto('Status');
  Result.FormaPagamento := ALinha.ValorTexto('Forma de Pagamento');
  Result.NParcelas := ALinha.ValorTexto('Nº Parcelas');
  Result.Moeda := ALinha.ValorTexto('Moeda');
  Result.Contrato := ALinha.ValorTexto('Contrato');
  Result.DataCriacao := ALinha.ValorData('Data de Criação', DATA_PADRAO);
  Result.DataPagamento := ALinha.ValorData('Data de Pagamento', DATA_PADRAO);
  Result.DataCredito := ALinha.ValorData('Data de Crédito', DATA_PADRAO);
  Result.DataReembolso := ALinha.ValorData('Data de Reembolso', DATA_PADRAO);
  Result.TipoReembolso := ALinha.ValorTexto('Tipo de Reembolso');
  Result.SKU := ALinha.ValorTexto('SKU');
  Result.Produto := ALinha.ValorTexto('Produto');
  Result.Quantidade := ALinha.ValorTexto('Quantidade');
  Result.AfiliadoPrincipal := ALinha.ValorTexto('Afiliado Principal');
  Result.Cupom := ALinha.ValorTexto('Cupom');
  Result.ValorCupom := ALinha.ValorMoeda('Valor do Cupom');
  Result.ValorVenda := ALinha.ValorMoeda('Valor da Venda');
  Result.ValorVendaComJuros := ALinha.ValorMoeda('Valor da Venda com Juros');
  Result.ValorItem := ALinha.ValorMoeda('Valor do Item');
  Result.ValorReembolsado := ALinha.ValorMoeda('Valor Reembolsado');
  Result.ValorFrete := ALinha.ValorMoeda('Valor de Frete');
  Result.Taxa := ALinha.ValorMoeda('Taxa', 0, True); // legado removia o sinal negativo da taxa
  Result.Outros := ALinha.ValorMoeda('Outros');
  Result.Antecipacao := ALinha.ValorMoeda('Antecipação');
  Result.Comissao := ALinha.ValorMoeda('Comissão');
  Result.Parceiro := ALinha.ValorMoeda('Parceiro');
  Result.GanhoLiquido := ALinha.ValorMoeda('Ganho Liquido');
  Result.ClienteNome := UpperCase(ALinha.ValorTexto('Cliente / Nome'));
  Result.ClienteEmail := ALinha.ValorTexto('Cliente / E-mail');
  Result.ClienteFones := ALinha.ValorTexto('Cliente / Fones');
  Result.ClienteTipoDocumento := ALinha.ValorTexto('Cliente / Tipo Documento');
  Result.ClienteDocumento := SomenteDigitos(ALinha.ValorTexto('Cliente / Documento'));
  Result.Endereco := UpperCase(ALinha.ValorTexto('Endereço'));
  Result.Numero := UpperCase(ALinha.ValorTexto('Numero'));
  Result.Complemento := UpperCase(ALinha.ValorTexto('Complemento'));
  Result.Bairro := UpperCase(ALinha.ValorTexto('Bairro'));
  Result.CEP := StringReplace(ALinha.ValorTexto('CEP'), '-', '', [rfReplaceAll]);
  Result.Cidade := UpperCase(ALinha.ValorTexto('Cidade'));
  Result.IBGE := UpperCase(ALinha.ValorTexto('IBGE'));
  Result.UF := UpperCase(ALinha.ValorTexto('UF'));
  Result.UTMSource := UpperCase(ALinha.ValorTexto('UTM Source'));
  Result.UTMCampaign := UpperCase(ALinha.ValorTexto('UTM Campaign'));
  Result.UTMMedium := UpperCase(ALinha.ValorTexto('UTM Medium'));
  Result.UTMContent := UpperCase(ALinha.ValorTexto('UTM Content'));
  Result.URLBoleto := UpperCase(ALinha.ValorTexto('URL Boleto'));
end;

function TControllerImportacaoEventos.MapearLinhaReduzida(ALinha: TLinhaPlanilha): TDadosInscricaoReduzida;
begin
  Result := Default (TDadosInscricaoReduzida);
  Result.StatusInscricao := ALinha.ValorTexto('Status');
  Result.Produto := ALinha.ValorTexto('Produto');
  Result.ClienteNome := UpperCase(ALinha.ValorTexto('Nome'));
  Result.ClienteEmail := LowerCase(ALinha.ValorTexto('E-mail'));
  Result.DocumentoCliente := SomenteDigitos(ALinha.ValorTexto('Documento'));
  Result.Endereco := ALinha.ValorTexto('Endereco');
  Result.Numero := ALinha.ValorTexto('Numero');
  Result.Complemento := ALinha.ValorTexto('Complemento');
  Result.Bairro := UpperCase(ALinha.ValorTexto('Bairro'));
  Result.CEP := ALinha.ValorTexto('CEP');
  Result.Cidade := UpperCase(ALinha.ValorTexto('Cidade'));
  Result.UF := ALinha.ValorTexto('UF');
end;

function TControllerImportacaoEventos.ImportarLayoutCompleto(const AIdEvento, AArquivo: string): TResultadoImportacao;
var
  vPlanilha: TPlanilhaImportada;
  vLinha: TLinhaPlanilha;
  vDados: TDadosInscricaoCompleta;
  vVinculo: TInfoVinculoApolo;
  vIndice: Integer;
begin
  Result := Default (TResultadoImportacao);
  vPlanilha := FLeitor.Carregar(AArquivo);
  try
    Result.TotalLinhas := vPlanilha.Count;
    for vIndice := 0 to vPlanilha.Count - 1 do
    begin
      vLinha := vPlanilha.Linhas[vIndice];
      vDados := MapearLinhaCompleta(vLinha);

      // Vínculo é recalculado a cada linha (registro "zerado" por padrão),
      // corrigindo o bug do código original em que entcod/categoria/colaboração
      // de uma linha "vazavam" para a próxima linha sem documento.
      vVinculo := FServicoVinculo.ObterVinculo(vDados.ClienteDocumento, False);
      if vVinculo.Encontrado then
        Inc(Result.TotalVinculadosApolo);
      if vDados.ClienteDocumento <> '' then
        Inc(Result.TotalComDocumento);

      FRepositorio.InserirRegistroCompleto(AIdEvento, vVinculo, vDados);

      if Assigned(FOnProgresso) then
        FOnProgresso(vIndice + 1, vPlanilha.Count);
    end;
  finally
    vPlanilha.Free;
  end;
end;

function TControllerImportacaoEventos.ImportarLayoutReduzido(const AIdEvento, AArquivo: string): TResultadoImportacao;
var
  vPlanilha: TPlanilhaImportada;
  vLinha: TLinhaPlanilha;
  vDados: TDadosInscricaoReduzida;
  vVinculo: TInfoVinculoApolo;
  vTipoDocumento: string;
  vIndice: Integer;
begin
  Result := Default (TResultadoImportacao);
  vPlanilha := FLeitor.Carregar(AArquivo);
  try
    Result.TotalLinhas := vPlanilha.Count;
    for vIndice := 0 to vPlanilha.Count - 1 do
    begin
      vLinha := vPlanilha.Linhas[vIndice];
      vDados := MapearLinhaReduzida(vLinha);

      if not StatusValido(vDados.StatusInscricao) then
        Continue;

      vVinculo := FServicoVinculo.ObterVinculo(vDados.DocumentoCliente, True);

      if vDados.DocumentoCliente = '' then
        vTipoDocumento := ''
      else if Length(vDados.DocumentoCliente) = 11 then
        vTipoDocumento := 'F'
      else
        vTipoDocumento := 'J';

      FRepositorio.InserirRegistroReduzido(AIdEvento, vVinculo, vDados, vTipoDocumento);

      if vDados.DocumentoCliente <> '' then
        Inc(Result.TotalComDocumento);
      if vVinculo.Encontrado then
        Inc(Result.TotalVinculadosApolo);

      if Assigned(FOnProgresso) then
        FOnProgresso(vIndice + 1, vPlanilha.Count);
    end;
  finally
    vPlanilha.Free;
  end;
end;

end.
