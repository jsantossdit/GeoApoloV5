unit unt_auditoriacuponsfiscais_service;

interface

uses
  System.SysUtils, System.Classes, System.Generics.Collections,
  unt_auditoriacuponsfiscais_types, unt_auditoriacuponsfiscais_repository;

type
  TAuditoriaCuponsService = class
  private
    FRepository: IAuditoriaCuponsRepository;
  public
    constructor Create(ARepository: IAuditoriaCuponsRepository);
    function ExecutarAuditoria(const ADataIni, ADataFim: TDateTime;
      out AResumo: TResumoAuditoriaCupomDTO): TList<TAuditoriaCupomDTO>;
    function SincronizarComApolo(const ACupons: TList<TAuditoriaCupomDTO>): TResultadoSincronizacaoCupom;
  end;

implementation

{ TAuditoriaCuponsService }

constructor TAuditoriaCuponsService.Create(ARepository: IAuditoriaCuponsRepository);
begin
  inherited Create;
  if ARepository = nil then
    raise EArgumentNilException.Create('Repositório de auditoria não pode ser nulo.');
  FRepository := ARepository;
end;

function TAuditoriaCuponsService.ExecutarAuditoria(
  const ADataIni, ADataFim: TDateTime;
  out AResumo: TResumoAuditoriaCupomDTO): TList<TAuditoriaCupomDTO>;
var
  Item: TAuditoriaCupomDTO;
begin
  FillChar(AResumo, SizeOf(AResumo), 0);
  Result := FRepository.ListarCuponsPDV(ADataIni, ADataFim);
  AResumo.TotalCupons := Result.Count;

  for Item in Result do
  begin
    if SameText(Item.StatusSefaz, 'Transmitiu') then
      Inc(AResumo.TotalTransmitidos)
    else
      Inc(AResumo.TotalNaoTransmitidos);

    if Item.IntegradoAlvo then
      Inc(AResumo.TotalIntegrados)
    else
      Inc(AResumo.TotalNaoIntegrados);

    if Item.IntegradoFinanc then Inc(AResumo.TotalIntegradosFinanc);
    if Item.IntegradoFiscal then Inc(AResumo.TotalIntegradosFiscal);
    if Item.BaixouEstoque then Inc(AResumo.TotalBaixouEstoque);
  end;
end;

function TAuditoriaCuponsService.SincronizarComApolo(
  const ACupons: TList<TAuditoriaCupomDTO>): TResultadoSincronizacaoCupom;
var
  Item: TAuditoriaCupomDTO;
  Atualizados: Integer;
begin
  Atualizados := 0;
  if (ACupons = nil) or (ACupons.Count = 0) then
    Exit(TResultadoSincronizacaoCupom.CriarSucesso('Nenhum cupom para sincronizar.', 0));

  for Item in ACupons do
  begin
    // Se o cupom consta no Apolo mas está marcado como não integrado no PDV, corrige a flag
    if FRepository.VerificarIntegracaoApolo(Item.NFNum, Item.Serie) then
    begin
      if not Item.IntegradoAlvo then
      begin
        FRepository.AtualizarFlagsIntegracao(Item.NFNum, 'Sim', 'Sim', 'Sim', 'Sim');
        Inc(Atualizados);
      end;
    end;
  end;

  Result := TResultadoSincronizacaoCupom.CriarSucesso(
    Format('Sincronização concluída com sucesso. %d cupons atualizados.', [Atualizados]), Atualizados);
end;

end.
