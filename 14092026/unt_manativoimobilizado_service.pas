unit unt_manativoimobilizado_service;

{
  Camada de Serviços e Regras de Negócio para Gestão de Ativo Imobilizado.
  Totalmente desacoplado de VCL, forms e componentes de tela.
  Contém cálculos de depreciação contábil em linha reta e validações cadastrais.
}

interface

uses
  System.SysUtils, System.Classes, System.DateUtils,
  unt_manativoimobilizado_types,
  unt_manativoimobilizado_repository;

type
  TAtivoImobilizadoService = class
  private
    FRepo: TAtivoImobilizadoRepository;
  public
    constructor Create(ARepository: TAtivoImobilizadoRepository);

    // Motor de Depreciação Contábil (Linha Reta)
    function CalcularDepreciacao(
      const ADataAquisicao: TDateTime;
      const AValorCompra, ATaxaAnual: Double;
      const ADataReferencia: TDateTime = 0
    ): TCalculoDepreciacaoDTO;

    // Regras de Validação Cadastral
    function ValidarBem(const ABem: TAtivoImobilizadoDTO): TOperacaoResultadoAtivo;

    // Orquestração de Negócio
    function SalvarBem(var ABem: TAtivoImobilizadoDTO; const AModoInclusao: Boolean): TOperacaoResultadoAtivo;
    function ExcluirBem(const ANumeroDoBem: string): TOperacaoResultadoAtivo;
    function ObterBem(const ANumeroDoBem, AEmpCod: string; out ABem: TAtivoImobilizadoDTO): Boolean;
    function ListarBens(const AEmpCod: string): TArray<TAtivoImobilizadoDTO>;
  end;

implementation

constructor TAtivoImobilizadoService.Create(ARepository: TAtivoImobilizadoRepository);
begin
  inherited Create;
  FRepo := ARepository;
end;

function TAtivoImobilizadoService.CalcularDepreciacao(
  const ADataAquisicao: TDateTime;
  const AValorCompra, ATaxaAnual: Double;
  const ADataReferencia: TDateTime = 0
): TCalculoDepreciacaoDTO;
var
  DataRef: TDateTime;
  DiasUso: Double;
begin
  FillChar(Result, SizeOf(Result), 0);
  Result.DataAquisicao        := ADataAquisicao;
  Result.ValorCompra          := AValorCompra;
  Result.TaxaDepreciacaoAnual := ATaxaAnual;

  if ADataAquisicao <= 0 then
  begin
    Result.Valido := False;
    Result.Mensagem := 'Data de aquisição não informada ou inválida.';
    Exit;
  end;

  if AValorCompra <= 0 then
  begin
    Result.Valido := False;
    Result.Mensagem := 'Valor de compra deve ser maior que zero.';
    Exit;
  end;

  if ATaxaAnual <= 0 then
  begin
    Result.Valido := False;
    Result.Mensagem := 'Taxa de depreciação anual (%) deve ser superior a zero.';
    Exit;
  end;

  if ADataReferencia > 0 then
    DataRef := ADataReferencia
  else
    DataRef := Date;

  if DataRef < ADataAquisicao then
  begin
    Result.Valido := False;
    Result.Mensagem := 'Data de referência anterior à data de aquisição.';
    Exit;
  end;

  DiasUso := DataRef - ADataAquisicao;
  Result.AnosEmUso := DiasUso / 365.25;

  // Fórmula Linha Reta:
  // DepreciacaoAnual  = ValorCompra * (TaxaAnual / 100)
  // DepAcumulada      = DepreciacaoAnual * AnosEmUso
  // ValorAtual        = MAX(ValorCompra - DepAcumulada, 0)
  Result.DepreciacaoAnual := AValorCompra * (ATaxaAnual / 100.0);
  Result.DepreciacaoAcumulada := Result.DepreciacaoAnual * Result.AnosEmUso;
  Result.ValorAtual := AValorCompra - Result.DepreciacaoAcumulada;

  if Result.ValorAtual < 0 then
    Result.ValorAtual := 0; // Ativo totalmente depreciado

  Result.Valido := True;
  Result.Mensagem := 'Cálculo de depreciação realizado com sucesso.';
end;

function TAtivoImobilizadoService.ValidarBem(const ABem: TAtivoImobilizadoDTO): TOperacaoResultadoAtivo;
begin
  Result.Sucesso := False;
  Result.Codigo  := ABem.NumeroDoBem;

  if Trim(ABem.NumeroDoBem) = '' then
  begin
    Result.Mensagem := 'O número/código do bem é obrigatório.';
    Exit;
  end;

  if Trim(ABem.EmpCod) = '' then
  begin
    Result.Mensagem := 'A empresa proprietária do bem é obrigatória.';
    Exit;
  end;

  if Trim(ABem.GeoCctrlCodEstr) = '' then
  begin
    Result.Mensagem := 'O centro de controle/custo é obrigatório.';
    Exit;
  end;

  if Trim(ABem.CodigoCategoriaBem) = '' then
  begin
    Result.Mensagem := 'A categoria do bem é obrigatória.';
    Exit;
  end;

  if Trim(ABem.DescricaoDoBem) = '' then
  begin
    Result.Mensagem := 'A descrição do bem é obrigatória.';
    Exit;
  end;

  if Trim(ABem.CodigoClassificacaoAtivo) = '' then
  begin
    Result.Mensagem := 'A classificação do ativo imobilizado é obrigatória.';
    Exit;
  end;

  if Trim(ABem.CodigoLocalizacao) = '' then
  begin
    Result.Mensagem := 'A localização física do bem é obrigatória.';
    Exit;
  end;

  Result.Sucesso := True;
  Result.Mensagem := 'Validação concluída com sucesso.';
end;

function TAtivoImobilizadoService.SalvarBem(
  var ABem: TAtivoImobilizadoDTO;
  const AModoInclusao: Boolean
): TOperacaoResultadoAtivo;
var
  Val: TOperacaoResultadoAtivo;
begin
  Val := ValidarBem(ABem);
  if not Val.Sucesso then
    Exit(Val);

  // Se houver parâmetros de depreciação, calcular
  if ABem.TemDataAquisicao and (ABem.ValorCompra > 0) and (ABem.TaxaDepreciacaoAnual > 0) then
  begin
    ABem.Depreciacao := CalcularDepreciacao(
      ABem.DataAquisicao,
      ABem.ValorCompra,
      ABem.TaxaDepreciacaoAnual
    );
  end;

  if AModoInclusao then
    Result := FRepo.InserirBem(ABem)
  else
    Result := FRepo.AtualizarBem(ABem);
end;

function TAtivoImobilizadoService.ExcluirBem(const ANumeroDoBem: string): TOperacaoResultadoAtivo;
begin
  if Trim(ANumeroDoBem) = '' then
  begin
    Result.Sucesso := False;
    Result.Mensagem := 'Código do bem inválido para exclusão.';
    Result.Codigo := '';
    Exit;
  end;

  Result := FRepo.ExcluirBem(ANumeroDoBem);
end;

function TAtivoImobilizadoService.ObterBem(
  const ANumeroDoBem, AEmpCod: string;
  out ABem: TAtivoImobilizadoDTO
): Boolean;
begin
  Result := FRepo.ObterBem(ANumeroDoBem, AEmpCod, ABem);
  if Result and ABem.TemDataAquisicao and (ABem.ValorCompra > 0) and (ABem.TaxaDepreciacaoAnual > 0) then
  begin
    ABem.Depreciacao := CalcularDepreciacao(
      ABem.DataAquisicao,
      ABem.ValorCompra,
      ABem.TaxaDepreciacaoAnual
    );
  end;
end;

function TAtivoImobilizadoService.ListarBens(const AEmpCod: string): TArray<TAtivoImobilizadoDTO>;
var
  Bens: TArray<TAtivoImobilizadoDTO>;
  I: Integer;
begin
  Bens := FRepo.ListarBens(AEmpCod);
  for I := 0 to High(Bens) do
  begin
    if Bens[I].TemDataAquisicao and (Bens[I].ValorCompra > 0) and (Bens[I].TaxaDepreciacaoAnual > 0) then
    begin
      Bens[I].Depreciacao := CalcularDepreciacao(
        Bens[I].DataAquisicao,
        Bens[I].ValorCompra,
        Bens[I].TaxaDepreciacaoAnual
      );
    end;
  end;
  Result := Bens;
end;

end.
