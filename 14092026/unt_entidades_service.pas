unit unt_entidades_service;

interface

uses
  System.SysUtils, System.Classes, System.JSON, Data.DB, FireDAC.Comp.Client,
  unt_entidades_types, unt_entidades_repository;

type
  TEntidadeService = class
  private
    FRepo: IEntidadeRepository;
  public
    constructor Create(ARepository: IEntidadeRepository);

    function PodeExportarParaAlvo(const ABaseSelecionada, AObservacoes: string; out AMotivo: string): Boolean;
    function ExecutarAcaoIgnorar(const AGeoEntCod, AUsuCodApolo, ACodEmpresa, ACodUsuario: string): TResultadoOperacaoDTO;
    function ObterOuResolverEntCodAlvo(const AGeoEntCod, AEntCodAtual: string): string;
    function GerarPayloadSobreposicaoJSON(const AItens: TArray<TItemDiferencaComparacao>): string;
    function CompararBases(AQrySVE, AQryAlvo: TFDQuery): TArray<TItemDiferencaComparacao>;
    function MapearDatasetParaDTO(ADataset: TDataSet; const AModoIntegracao: string): TEntidadeEdicaoDTO;
  end;

implementation

{ TEntidadeService }

constructor TEntidadeService.Create(ARepository: IEntidadeRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise Exception.Create('TEntidadeService: Instância de IEntidadeRepository é necessária.');
  FRepo := ARepository;
end;

function TEntidadeService.PodeExportarParaAlvo(const ABaseSelecionada, AObservacoes: string; out AMotivo: string): Boolean;
begin
  Result := False;
  AMotivo := '';

  if ABaseSelecionada = 'Alvo' then
  begin
    AMotivo := 'Operação não permitida: Você está conectado diretamente à base Alvo.';
    Exit;
  end;

  if Trim(AObservacoes) <> '' then
  begin
    AMotivo := 'Existem observações que precisam ser moderadas antes de exportar.';
    Exit;
  end;

  Result := True;
end;

function TEntidadeService.ExecutarAcaoIgnorar(const AGeoEntCod, AUsuCodApolo, ACodEmpresa, ACodUsuario: string): TResultadoOperacaoDTO;
begin
  try
    if FRepo.IgnorarAtualizacaoAlvo(AGeoEntCod, AUsuCodApolo, ACodEmpresa, ACodUsuario) then
    begin
      Result.Sucesso  := True;
      Result.Mensagem := 'Atualização ignorada e ocorrência gerada no sistema.';
      Result.Codigo   := AGeoEntCod;
    end
    else
    begin
      Result.Sucesso  := False;
      Result.Mensagem := 'Falha ao registrar a desistência da atualização no banco.';
    end;
  except
    on E: Exception do
    begin
      Result.Sucesso  := False;
      Result.Mensagem := 'Erro interno ao processar operação: ' + E.Message;
    end;
  end;
end;

function TEntidadeService.ObterOuResolverEntCodAlvo(const AGeoEntCod, AEntCodAtual: string): string;
begin
  Result := Trim(AEntCodAtual);
  if Result = '' then
  begin
    Result := FRepo.AtualizarEntCodAlvoViaCPF(AGeoEntCod);
  end;
end;

function TEntidadeService.GerarPayloadSobreposicaoJSON(const AItens: TArray<TItemDiferencaComparacao>): string;
var
  JsonRoot, JsonEntidade, Entidade1Obj: TJSONObject;
  TelefonesArray, EnderecosArray, CategoriasArray: TJSONArray;
  TelefoneObj, EnderecoObj: TJSONObject;
  Item: TItemDiferencaComparacao;
  ValorFinal, CampoNorm: string;
begin
  JsonRoot        := TJSONObject.Create;
  JsonEntidade    := TJSONObject.Create;
  Entidade1Obj    := TJSONObject.Create;
  CategoriasArray := TJSONArray.Create;
  TelefonesArray  := TJSONArray.Create;
  EnderecosArray  := TJSONArray.Create;
  try
    JsonRoot.AddPair('Operacao', 'A');
    JsonEntidade.AddPair('Natureza', 'Consumidor');

    for Item in AItens do
    begin
      if Item.Decisao = dlManterSVE then
        ValorFinal := Item.ValorSVE
      else if Item.Decisao = dlManterAlvo then
        ValorFinal := Item.ValorAlvo
      else
        Continue;

      CampoNorm := UpperCase(Item.Rotulo);

      if (CampoNorm = 'NOME') or (CampoNorm = 'ENTNOME') then
        JsonEntidade.AddPair('Nome', ValorFinal)
      else if (CampoNorm = 'CPF / CNPJ') or (CampoNorm = 'DOCUMENTO') or (CampoNorm = 'ENTCPFCGC') then
        JsonEntidade.AddPair('CPFCNPJ', ValorFinal)
      else if (CampoNorm = 'RG / IE') or (CampoNorm = 'ENTRGIE') then
        JsonEntidade.AddPair('RGIE', ValorFinal)
      else if (CampoNorm = 'LOGRADOURO') or (CampoNorm = 'TIPOLOGRAD') then
        JsonEntidade.AddPair('CodigoTipoLograd', ValorFinal)
      else if (CampoNorm = 'ENDEREÇO') or (CampoNorm = 'GEOENTENDER') or (CampoNorm = 'ENTENDER') then
        JsonEntidade.AddPair('Endereco', ValorFinal)
      else if (CampoNorm = 'NÚMERO') or (CampoNorm = 'GEOENDERNO') or (CampoNorm = 'ENTENDERNO') then
        JsonEntidade.AddPair('NumeroEndereco', ValorFinal)
      else if (CampoNorm = 'COMPLEMENTO') or (CampoNorm = 'GEOENTENDERCOMP') then
        JsonEntidade.AddPair('ComplementoEndereco', ValorFinal)
      else if (CampoNorm = 'BAIRRO') or (CampoNorm = 'GEOENTBAIR') or (CampoNorm = 'ENTBAIR') then
        JsonEntidade.AddPair('Bairro', ValorFinal)
      else if (CampoNorm = 'CEP') or (CampoNorm = 'GEOENTCEP') or (CampoNorm = 'ENTCEP') then
        JsonEntidade.AddPair('Cep', ValorFinal)
      else if (CampoNorm = 'CIDADE') or (CampoNorm = 'CIDNOMECOMP') then
        JsonEntidade.AddPair('Cidade', ValorFinal)
      else if (CampoNorm = 'ESTADO') or (CampoNorm = 'UFSIGLA') then
        JsonEntidade.AddPair('UF', ValorFinal)
      else if (CampoNorm = 'DATA ANIVERSÁRIO') or (CampoNorm = 'GEOENTDATAANIVFUND') then
        JsonEntidade.AddPair('DataFundacao', ValorFinal);
    end;

    if TelefonesArray.Count > 0 then
      Entidade1Obj.AddPair('EntFoneChildList', TelefonesArray)
    else
      TelefonesArray.Free;

    if EnderecosArray.Count > 0 then
      Entidade1Obj.AddPair('EnderEntChildList', EnderecosArray)
    else
      EnderecosArray.Free;

    if CategoriasArray.Count > 0 then
      Entidade1Obj.AddPair('EntCategChildList', CategoriasArray)
    else
      CategoriasArray.Free;

    if Entidade1Obj.Count > 0 then
      JsonEntidade.AddPair('Entidade1Object', Entidade1Obj)
    else
      Entidade1Obj.Free;

    JsonRoot.AddPair('Entidade', JsonEntidade);
    Result := JsonRoot.Format(2);
  finally
    JsonRoot.Free;
  end;
end;

function TEntidadeService.CompararBases(AQrySVE, AQryAlvo: TFDQuery): TArray<TItemDiferencaComparacao>;
const
  TOTAL_MAPAS = 14;
  LabelsExibicao: array[0..TOTAL_MAPAS-1] of string = (
    'Nome', 'CPF / CNPJ', 'RG / IE', 'Logradouro', 'Endereço', 'Número',
    'Complemento', 'Bairro', 'CEP', 'Cidade', 'Estado', 'E-mail',
    'Telefone', 'Data Aniversário'
  );
  CamposSVE: array[0..TOTAL_MAPAS-1] of string = (
    'geoentnome', 'Documento', 'EntRgIe', 'tipolograd', 'geoentender', 'geoenderno',
    'geoentendercomp', 'geoentbair', 'geoentcep', 'cidnomecomp', 'ufsigla', 'Email',
    'Telefone', 'geoentdataanivfund'
  );
  CamposAlvo: array[0..TOTAL_MAPAS-1] of string = (
    'entnome', 'EntCpfCgc', 'EntRgIe', 'EntLograd', 'entender', 'entenderno',
    'EntEnderComp', 'entbair', 'entcep', 'cidnomecomp', 'ufsigla', 'Email',
    'Telefone', 'EntDataAnivFund'
  );
var
  i, TotalDiferencas: Integer;
  ValSVE, ValAlvo: string;
  Item: TItemDiferencaComparacao;
begin
  SetLength(Result, 0);
  TotalDiferencas := 0;

  for i := 0 to TOTAL_MAPAS - 1 do
  begin
    ValSVE  := '';
    ValAlvo := '';

    if (AQrySVE <> nil) and (AQrySVE.FindField(CamposSVE[i]) <> nil) then
      ValSVE := Trim(AQrySVE.FieldByName(CamposSVE[i]).AsString);

    if (AQryAlvo <> nil) and (AQryAlvo.FindField(CamposAlvo[i]) <> nil) then
      ValAlvo := Trim(AQryAlvo.FieldByName(CamposAlvo[i]).AsString);

    if not SameText(ValSVE, ValAlvo) then
    begin
      Inc(TotalDiferencas);
      SetLength(Result, TotalDiferencas);
      Item.IndiceMapa := i;
      Item.Rotulo     := LabelsExibicao[i];
      Item.ValorSVE   := ValSVE;
      Item.ValorAlvo  := ValAlvo;
      Item.Decisao    := dlNenhuma;
      Result[TotalDiferencas - 1] := Item;
    end;
  end;
end;

function TEntidadeService.MapearDatasetParaDTO(ADataset: TDataSet; const AModoIntegracao: string): TEntidadeEdicaoDTO;
begin
  Result := Default(TEntidadeEdicaoDTO);
  if (ADataset = nil) or (not ADataset.Active) or (ADataset.IsEmpty) then
    Exit;

  Result.Codigo            := ADataset.FieldByName('entcod').AsString;
  Result.CodigoAlternativo := ADataset.FieldByName('geoentcod').AsString;
  Result.TipoTratamento    := ADataset.FieldByName('tipotratcod').AsString;
  Result.Nome              := ADataset.FieldByName('entnome').AsString;
  Result.NomeFantasia      := ADataset.FieldByName('entnomefant').AsString;
  Result.CEP               := ADataset.FieldByName('entcep').AsString;
  Result.Logradouro        := ADataset.FieldByName('entlograd').AsString;
  Result.Endereco          := ADataset.FieldByName('entender').AsString;
  Result.Numero            := ADataset.FieldByName('entenderno').AsString;
  Result.Complemento       := ADataset.FieldByName('entendercomp').AsString;
  Result.Bairro            := ADataset.FieldByName('entbair').AsString;
  Result.CodigoCidade      := ADataset.FieldByName('cidcod').AsString;
  Result.NomeCidade        := ADataset.FieldByName('cidnomecomp').AsString;
  Result.UF                := ADataset.FieldByName('ufsigla').AsString;
  Result.Genero            := ADataset.FieldByName('entgenero').AsString;
  Result.EstadoCivil       := ADataset.FieldByName('entestcivil').AsString;
  Result.DataNascimento    := ADataset.FieldByName('entdataanivfund').AsString;
  Result.DataCadastro      := ADataset.FieldByName('entdesdedata').AsString;
  Result.NomePai           := ADataset.FieldByName('entnomepai').AsString;
  Result.NomeMae           := ADataset.FieldByName('entnomemae').AsString;
  Result.PossuiFilhos      := SameText(ADataset.FieldByName('entpossuifilho').AsString, 'Sim');
  Result.ValorContribuicao := ADataset.FieldByName('USERValor_Contribuicao').AsFloat;
  Result.DioceseId         := ADataset.FieldByName('USERDiocese_id').AsString;
  Result.NomeDiocese       := ADataset.FieldByName('USERNomeDiocese').AsString;
  Result.Observacoes       := ADataset.FieldByName('Entobservacoes').AsString;
  Result.ModoIntegracao    := AModoIntegracao;
end;

end.
