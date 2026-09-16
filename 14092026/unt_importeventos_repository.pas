unit unt_importeventos_repository;

interface

uses
  System.SysUtils, System.StrUtils, Data.DB, FireDAC.Comp.Client, FireDAC.Stan.Param,
  unt_importeventos_model;

type
  /// <summary>Acesso a dados da importação de inscritos em eventos. Depende só de
  /// TFDConnection (injetada), não de nenhum form/módulo de dados específico —
  /// pode ser testada isoladamente ou trocada por um fake em teste unitário.</summary>
  IRepositorioCongressoRcc = interface
    ['{9B6E4C3E-1F2A-4E4D-9E36-8D6D6A9C4E11}']
    function BuscarEntidadePorDocumento(const ADocumento: string): TInfoEntidade;
    function BuscarCategoriaProjeto(const AEntCod: string): string;
    function BuscarCategoriasProjeto(const AEntCod: string): string;
    function BuscarUltimaContribuicao(const AEntCod: string): string;
    function ExisteImportacao(const AIdEvento: string): Boolean;
    procedure ExcluirImportacao(const AIdEvento: string);
    procedure InserirRegistroCompleto(const AIdEvento: string; const AVinculo: TInfoVinculoApolo;
      const ADados: TDadosInscricaoCompleta);
    procedure InserirRegistroReduzido(const AIdEvento: string; const AVinculo: TInfoVinculoApolo;
      const ADados: TDadosInscricaoReduzida; const ATipoDocumento: string);
    function ListarEventos: TFDQuery;
  end;

  TRepositorioCongressoRccFireDAC = class(TInterfacedObject, IRepositorioCongressoRcc)
  private
    FConexao: TFDConnection;
    function NovaQuery: TFDQuery;
  public
    constructor Create(AConexao: TFDConnection);
    function BuscarEntidadePorDocumento(const ADocumento: string): TInfoEntidade;
    function BuscarCategoriaProjeto(const AEntCod: string): string;
    function BuscarCategoriasProjeto(const AEntCod: string): string;
    function BuscarUltimaContribuicao(const AEntCod: string): string;
    function ExisteImportacao(const AIdEvento: string): Boolean;
    procedure ExcluirImportacao(const AIdEvento: string);
    procedure InserirRegistroCompleto(const AIdEvento: string; const AVinculo: TInfoVinculoApolo;
      const ADados: TDadosInscricaoCompleta);
    procedure InserirRegistroReduzido(const AIdEvento: string; const AVinculo: TInfoVinculoApolo;
      const ADados: TDadosInscricaoReduzida; const ATipoDocumento: string);
    function ListarEventos: TFDQuery;
  end;

implementation

{ TRepositorioCongressoRccFireDAC }

constructor TRepositorioCongressoRccFireDAC.Create(AConexao: TFDConnection);
begin
  inherited Create;
  FConexao := AConexao;
end;

function TRepositorioCongressoRccFireDAC.NovaQuery: TFDQuery;
begin
  Result := TFDQuery.Create(nil);
  Result.Connection := FConexao;
end;

function TRepositorioCongressoRccFireDAC.BuscarEntidadePorDocumento(const ADocumento: string): TInfoEntidade;
var
  vQuery: TFDQuery;
begin
  Result := Default (TInfoEntidade);
  if ADocumento = '' then
    Exit;
  vQuery := NovaQuery;
  try
    vQuery.SQL.Text := 'SELECT entcod, entnome FROM entidade WITH (NOLOCK) WHERE entcpfcgc = :pDocumento';
    vQuery.ParamByName('pDocumento').AsString := ADocumento;
    vQuery.Open;
    Result.Encontrado := not vQuery.IsEmpty;
    if Result.Encontrado then
    begin
      Result.EntCod := vQuery.FieldByName('entcod').AsString;
      Result.EntNome := vQuery.FieldByName('entnome').AsString;
    end;
  finally
    vQuery.Free;
  end;
end;

function TRepositorioCongressoRccFireDAC.BuscarCategoriaProjeto(const AEntCod: string): string;
var
  vQuery: TFDQuery;
begin
  Result := '';
  if AEntCod = '' then
    Exit;
  vQuery := NovaQuery;
  try
    vQuery.SQL.Text :=
      'SELECT TOP 1 categcodestr FROM ent_categ WHERE entcod = :pEntCod ORDER BY categcodestr DESC';
    vQuery.ParamByName('pEntCod').AsString := AEntCod;
    vQuery.Open;
    if not vQuery.IsEmpty then
      Result := vQuery.FieldByName('categcodestr').AsString;
  finally
    vQuery.Free;
  end;
end;

function TRepositorioCongressoRccFireDAC.BuscarCategoriasProjeto(const AEntCod: string): string;
var
  vQuery: TFDQuery;
begin
  Result := '';
  if AEntCod = '' then
    Exit;
  vQuery := NovaQuery;
  try
    vQuery.SQL.Text := 'SELECT categcodestr FROM ent_categ WHERE entcod = :pEntCod ORDER BY categcodestr DESC';
    vQuery.ParamByName('pEntCod').AsString := AEntCod;
    vQuery.Open;
    while not vQuery.Eof do
    begin
      Result := Result + ',' + vQuery.FieldByName('categcodestr').AsString;
      vQuery.Next;
    end;
  finally
    vQuery.Free;
  end;
end;

function TRepositorioCongressoRccFireDAC.BuscarUltimaContribuicao(const AEntCod: string): string;
var
  vQuery: TFDQuery;
  vMes: string;
begin
  Result := '';
  if AEntCod = '' then
    Exit;
  vQuery := NovaQuery;
  try
    vQuery.SQL.Text :=
      'SELECT TOP 1 MONTH(pdf.parcdocfindatapag) AS mes, YEAR(pdf.parcdocfindatapag) AS ano ' +
      'FROM parc_doc_fin pdf WITH (NOLOCK) ' +
      'INNER JOIN doc_fin df WITH (NOLOCK) ON pdf.empcod = df.empcod AND pdf.docfinchv = df.docfinchv ' +
      'WHERE pdf.entcod = :pEntCod AND df.docfinespec IN (''BOL'', ''DEB'') ' +
      'GROUP BY MONTH(pdf.parcdocfindatapag), YEAR(pdf.parcdocfindatapag), pdf.parcdocfindatapag ' +
      'ORDER BY pdf.parcdocfindatapag DESC';
    vQuery.ParamByName('pEntCod').AsString := AEntCod;
    vQuery.Open;
    if not vQuery.IsEmpty then
    begin
      vMes := vQuery.FieldByName('mes').AsString;
      if Length(vMes) < 2 then
        vMes := '0' + vMes;
      Result := vQuery.FieldByName('ano').AsString + vMes;
    end;
  finally
    vQuery.Free;
  end;
end;

function TRepositorioCongressoRccFireDAC.ExisteImportacao(const AIdEvento: string): Boolean;
var
  vQuery: TFDQuery;
begin
  vQuery := NovaQuery;
  try
    vQuery.SQL.Text := 'SELECT TOP 1 id_evento FROM USER_geoapolo_congressos_rcc WHERE id_evento = :pIdEvento';
    vQuery.ParamByName('pIdEvento').AsString := AIdEvento;
    vQuery.Open;
    Result := not vQuery.IsEmpty;
  finally
    vQuery.Free;
  end;
end;

procedure TRepositorioCongressoRccFireDAC.ExcluirImportacao(const AIdEvento: string);
var
  vQuery: TFDQuery;
begin
  vQuery := NovaQuery;
  try
    vQuery.SQL.Text := 'DELETE FROM USER_geoapolo_congressos_rcc WHERE id_evento = :pIdEvento';
    vQuery.ParamByName('pIdEvento').AsString := AIdEvento;
    vQuery.ExecSQL;
  finally
    vQuery.Free;
  end;
end;

procedure TRepositorioCongressoRccFireDAC.InserirRegistroCompleto(const AIdEvento: string;
  const AVinculo: TInfoVinculoApolo; const ADados: TDadosInscricaoCompleta);
var
  vQuery: TFDQuery;
begin
  vQuery := NovaQuery;
  try
    vQuery.SQL.Text :=
      'INSERT INTO USER_geoapolo_congressos_rcc (' +
      'id_evento, entcod_apolo, categoria_apolo, colabora_projetos, ano_mes_ultima_contribuicao, ' +
      'Fatura, Status_Inscricao, Forma_de_Pagamento, N_Parcelas, Moeda, Contrato, ' +
      'Data_de_Criacao, Data_de_Pagamento, Data_de_Crédito, Data_de_Reembolso, Tipo_de_Reembolso, ' +
      'SKU, Produto, Quantidade, Afiliado_Principal, Cupom, Valor_do_Cupom, Valor_da_Venda, ' +
      'Valor_da_Venda_com_Juros, Valor_do_Item, Valor_Reembolsado, Valor_de_Frete, Taxa, Outros, ' +
      'Antecipacao, Comissao, Parceiro, Ganho_Liquido, Cliente_Nome, Cliente_Email, Cliente_Fones, ' +
      'Cliente_TipoDocumento, Cliente_Documento, Endereco, Numero, Complemento, Bairro, CEP, Cidade, ' +
      'IBGE, UF, UTM_Source, UTM_Campaign, UTM_Medium, UTM_Content, URL_Boleto' +
      ') VALUES (' +
      ':pIdEvento, :pEntCod, :pCategCod, :pColabora, :pAnoMes, ' +
      ':pFatura, :pStatus, :pFormaPagto, :pNParcelas, :pMoeda, :pContrato, ' +
      ':pDataCriacao, :pDataPagamento, :pDataCredito, :pDataReembolso, :pTipoReembolso, ' +
      ':pSKU, :pProduto, :pQuantidade, :pAfiliado, :pCupom, :pValorCupom, :pValorVenda, ' +
      ':pValorVendaJuros, :pValorItem, :pValorReembolsado, :pValorFrete, :pTaxa, :pOutros, ' +
      ':pAntecipacao, :pComissao, :pParceiro, :pGanhoLiquido, :pClienteNome, :pClienteEmail, :pClienteFones, ' +
      ':pClienteTipoDoc, :pClienteDoc, :pEndereco, :pNumero, :pComplemento, :pBairro, :pCEP, :pCidade, ' +
      ':pIBGE, :pUF, :pUTMSource, :pUTMCampaign, :pUTMMedium, :pUTMContent, :pURLBoleto' +
      ')';

    vQuery.ParamByName('pIdEvento').AsString := AIdEvento;
    vQuery.ParamByName('pEntCod').AsString := AVinculo.EntCod;
    vQuery.ParamByName('pCategCod').AsString := AVinculo.CategCodEstr;
    vQuery.ParamByName('pColabora').AsString := IfThen(AVinculo.ColaboraProjetos, 'S', 'N');
    vQuery.ParamByName('pAnoMes').AsString := AVinculo.AnoMesUltimaContribuicao;

    vQuery.ParamByName('pFatura').AsString := ADados.Fatura;
    vQuery.ParamByName('pStatus').AsString := ADados.StatusInscricao;
    vQuery.ParamByName('pFormaPagto').AsString := ADados.FormaPagamento;
    vQuery.ParamByName('pNParcelas').AsString := ADados.NParcelas;
    vQuery.ParamByName('pMoeda').AsString := ADados.Moeda;
    vQuery.ParamByName('pContrato').AsString := ADados.Contrato;
    vQuery.ParamByName('pDataCriacao').AsDate := ADados.DataCriacao;
    vQuery.ParamByName('pDataPagamento').AsDate := ADados.DataPagamento;
    vQuery.ParamByName('pDataCredito').AsDate := ADados.DataCredito;
    vQuery.ParamByName('pDataReembolso').AsDate := ADados.DataReembolso;
    vQuery.ParamByName('pTipoReembolso').AsString := ADados.TipoReembolso;
    vQuery.ParamByName('pSKU').AsString := ADados.SKU;
    vQuery.ParamByName('pProduto').AsString := ADados.Produto;
    vQuery.ParamByName('pQuantidade').AsString := ADados.Quantidade;
    vQuery.ParamByName('pAfiliado').AsString := ADados.AfiliadoPrincipal;
    vQuery.ParamByName('pCupom').AsString := ADados.Cupom;
    vQuery.ParamByName('pValorCupom').AsCurrency := ADados.ValorCupom;
    vQuery.ParamByName('pValorVenda').AsCurrency := ADados.ValorVenda;
    vQuery.ParamByName('pValorVendaJuros').AsCurrency := ADados.ValorVendaComJuros;
    vQuery.ParamByName('pValorItem').AsCurrency := ADados.ValorItem;
    vQuery.ParamByName('pValorReembolsado').AsCurrency := ADados.ValorReembolsado;
    vQuery.ParamByName('pValorFrete').AsCurrency := ADados.ValorFrete;
    vQuery.ParamByName('pTaxa').AsCurrency := ADados.Taxa;
    vQuery.ParamByName('pOutros').AsCurrency := ADados.Outros;
    vQuery.ParamByName('pAntecipacao').AsCurrency := ADados.Antecipacao;
    vQuery.ParamByName('pComissao').AsCurrency := ADados.Comissao;
    vQuery.ParamByName('pParceiro').AsCurrency := ADados.Parceiro;
    vQuery.ParamByName('pGanhoLiquido').AsCurrency := ADados.GanhoLiquido;
    vQuery.ParamByName('pClienteNome').AsString := ADados.ClienteNome;
    vQuery.ParamByName('pClienteEmail').AsString := ADados.ClienteEmail;
    vQuery.ParamByName('pClienteFones').AsString := ADados.ClienteFones;
    vQuery.ParamByName('pClienteTipoDoc').AsString := ADados.ClienteTipoDocumento;
    vQuery.ParamByName('pClienteDoc').AsString := ADados.ClienteDocumento;
    vQuery.ParamByName('pEndereco').AsString := ADados.Endereco;
    vQuery.ParamByName('pNumero').AsString := ADados.Numero;
    vQuery.ParamByName('pComplemento').AsString := ADados.Complemento;
    vQuery.ParamByName('pBairro').AsString := ADados.Bairro;
    vQuery.ParamByName('pCEP').AsString := ADados.CEP;
    vQuery.ParamByName('pCidade').AsString := ADados.Cidade;
    vQuery.ParamByName('pIBGE').AsString := ADados.IBGE;
    vQuery.ParamByName('pUF').AsString := ADados.UF;
    vQuery.ParamByName('pUTMSource').AsString := ADados.UTMSource;
    vQuery.ParamByName('pUTMCampaign').AsString := ADados.UTMCampaign;
    vQuery.ParamByName('pUTMMedium').AsString := ADados.UTMMedium;
    vQuery.ParamByName('pUTMContent').AsString := ADados.UTMContent;
    vQuery.ParamByName('pURLBoleto').AsString := ADados.URLBoleto;

    vQuery.ExecSQL;
  finally
    vQuery.Free;
  end;
end;

procedure TRepositorioCongressoRccFireDAC.InserirRegistroReduzido(const AIdEvento: string;
  const AVinculo: TInfoVinculoApolo; const ADados: TDadosInscricaoReduzida; const ATipoDocumento: string);
var
  vQuery: TFDQuery;
begin
  vQuery := NovaQuery;
  try
    vQuery.SQL.Text :=
      'INSERT INTO USER_geoapolo_congressos_rcc (' +
      'id_evento, entcod_apolo, categoria_apolo, status_inscricao, produto, Cliente_Nome, ' +
      'Cliente_Email, Cliente_TipoDocumento, Cliente_Documento, Endereco, Numero, Complemento, Bairro, ' +
      'CEP, Cidade, UF, ano_mes_ultima_contribuicao' +
      ') VALUES (' +
      ':pIdEvento, :pEntCod, :pCategCod, :pStatus, :pProduto, :pClienteNome, ' +
      ':pClienteEmail, :pTipoDoc, :pDocumento, :pEndereco, :pNumero, :pComplemento, :pBairro, ' +
      ':pCEP, :pCidade, :pUF, :pAnoMes' +
      ')';

    vQuery.ParamByName('pIdEvento').AsString := AIdEvento;
    vQuery.ParamByName('pEntCod').AsString := AVinculo.EntCod;
    vQuery.ParamByName('pCategCod').AsString := AVinculo.CategCodEstr;
    vQuery.ParamByName('pStatus').AsString := ADados.StatusInscricao;
    vQuery.ParamByName('pProduto').AsString := ADados.Produto;
    vQuery.ParamByName('pClienteNome').AsString := ADados.ClienteNome;
    vQuery.ParamByName('pClienteEmail').AsString := ADados.ClienteEmail;
    vQuery.ParamByName('pTipoDoc').AsString := ATipoDocumento;
    vQuery.ParamByName('pDocumento').AsString := ADados.DocumentoCliente;
    vQuery.ParamByName('pEndereco').AsString := ADados.Endereco;
    vQuery.ParamByName('pNumero').AsString := ADados.Numero;
    vQuery.ParamByName('pComplemento').AsString := ADados.Complemento;
    vQuery.ParamByName('pBairro').AsString := ADados.Bairro;
    vQuery.ParamByName('pCEP').AsString := ADados.CEP;
    vQuery.ParamByName('pCidade').AsString := ADados.Cidade;
    vQuery.ParamByName('pUF').AsString := ADados.UF;
    vQuery.ParamByName('pAnoMes').AsString := AVinculo.AnoMesUltimaContribuicao;

    vQuery.ExecSQL;
  finally
    vQuery.Free;
  end;
end;

function TRepositorioCongressoRccFireDAC.ListarEventos: TFDQuery;
begin
  Result := NovaQuery;
  Result.SQL.Text := 'SELECT uge.idevento, uge.descricao FROM USER_geoapolo_eventos uge WITH (NOLOCK)';
  Result.Open;
end;

end.
