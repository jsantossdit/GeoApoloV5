unit unt_relacionadioceseentidade_service;

interface

uses
  System.SysUtils, System.Classes, System.Generics.Collections,
  unt_relacionadioceseentidade_types,
  unt_relacionadioceseentidade_repository;

type
  IRelacionaDioceseEntidadeService = interface
    ['{B592CD6A-12E0-4BCF-959F-3B97A0A9C1D1}']
    function ObterEntidades(const AFiltro: TFiltroEntidadeDioceseDTO): TList<TEntidadeDioceseDTO>;
    function BuscarEntidade(const AEntCod: string; out AEntidade: TEntidadeDioceseDTO): Boolean;
    function VincularEntidadeDiocese(const AEntCod, ADioceseId, ANomeDiocese: string): TResultadoVinculoDiocese;
    function DesvincularEntidadeDiocese(const AEntCod: string): TResultadoVinculoDiocese;
    function ListarDioceses(const AUFSigla, ACidade: string): TList<TDioceseCNBBDTO>;
    function ObterNomeDiocese(const ADioceseId, ACidade: string): string;
  end;

  TRelacionaDioceseEntidadeService = class(TInterfacedObject, IRelacionaDioceseEntidadeService)
  private
    FRepository: IRelacionaDioceseEntidadeRepository;
  public
    constructor Create(ARepository: IRelacionaDioceseEntidadeRepository);
    function ObterEntidades(const AFiltro: TFiltroEntidadeDioceseDTO): TList<TEntidadeDioceseDTO>;
    function BuscarEntidade(const AEntCod: string; out AEntidade: TEntidadeDioceseDTO): Boolean;
    function VincularEntidadeDiocese(const AEntCod, ADioceseId, ANomeDiocese: string): TResultadoVinculoDiocese;
    function DesvincularEntidadeDiocese(const AEntCod: string): TResultadoVinculoDiocese;
    function ListarDioceses(const AUFSigla, ACidade: string): TList<TDioceseCNBBDTO>;
    function ObterNomeDiocese(const ADioceseId, ACidade: string): string;
  end;

implementation

{ TRelacionaDioceseEntidadeService }

constructor TRelacionaDioceseEntidadeService.Create(ARepository: IRelacionaDioceseEntidadeRepository);
begin
  inherited Create;
  FRepository := ARepository;
end;

function TRelacionaDioceseEntidadeService.ObterEntidades(
  const AFiltro: TFiltroEntidadeDioceseDTO): TList<TEntidadeDioceseDTO>;
begin
  if FRepository = nil then
    Exit(TList<TEntidadeDioceseDTO>.Create);

  if AFiltro.DataInicial > AFiltro.DataFinal then
    raise Exception.Create('A Data Inicial não pode ser maior que a Data Final.');

  Result := FRepository.ListarEntidades(AFiltro);
end;

function TRelacionaDioceseEntidadeService.BuscarEntidade(
  const AEntCod: string; out AEntidade: TEntidadeDioceseDTO): Boolean;
begin
  if (FRepository = nil) or (Trim(AEntCod) = '') then
  begin
    AEntidade := Default(TEntidadeDioceseDTO);
    Exit(False);
  end;
  Result := FRepository.BuscarEntidadePorCodigo(Trim(AEntCod), AEntidade);
end;

function TRelacionaDioceseEntidadeService.VincularEntidadeDiocese(
  const AEntCod, ADioceseId, ANomeDiocese: string): TResultadoVinculoDiocese;
var
  CodLimpo, DioIdLimpo, DioNomeLimpo: string;
begin
  CodLimpo := Trim(AEntCod);
  DioIdLimpo := Trim(ADioceseId);
  DioNomeLimpo := Trim(ANomeDiocese);

  if CodLimpo = '' then
    Exit(TResultadoVinculoDiocese.CriarFalha('Código da Entidade deve ser informado.'));

  if FRepository = nil then
    Exit(TResultadoVinculoDiocese.CriarFalha('Repositório de dados não configurado.'));

  // Se o ID da diocese for vazio, trata como desvinculação
  if DioIdLimpo = '' then
  begin
    if FRepository.DesvincularDiocese(CodLimpo) then
      Result := TResultadoVinculoDiocese.CriarSucesso('Diocese desvinculada com sucesso!')
    else
      Result := TResultadoVinculoDiocese.CriarFalha('Erro ao desvincular diocese da entidade.');
    Exit;
  end;

  if FRepository.VincularDiocese(CodLimpo, DioIdLimpo, DioNomeLimpo) then
    Result := TResultadoVinculoDiocese.CriarSucesso('Diocese vinculada com sucesso!')
  else
    Result := TResultadoVinculoDiocese.CriarFalha('Erro ao salvar vínculo da diocese no banco de dados.');
end;

function TRelacionaDioceseEntidadeService.DesvincularEntidadeDiocese(
  const AEntCod: string): TResultadoVinculoDiocese;
var
  CodLimpo: string;
begin
  CodLimpo := Trim(AEntCod);
  if CodLimpo = '' then
    Exit(TResultadoVinculoDiocese.CriarFalha('Código da Entidade deve ser informado.'));

  if FRepository = nil then
    Exit(TResultadoVinculoDiocese.CriarFalha('Repositório de dados não configurado.'));

  if FRepository.DesvincularDiocese(CodLimpo) then
    Result := TResultadoVinculoDiocese.CriarSucesso('Diocese desvinculada com sucesso!')
  else
    Result := TResultadoVinculoDiocese.CriarFalha('Erro ao desvincular diocese da entidade.');
end;

function TRelacionaDioceseEntidadeService.ListarDioceses(
  const AUFSigla, ACidade: string): TList<TDioceseCNBBDTO>;
begin
  if FRepository = nil then
    Exit(TList<TDioceseCNBBDTO>.Create);
  Result := FRepository.ListarDiocesesPorEstadoECidade(Trim(AUFSigla), Trim(ACidade));
end;

function TRelacionaDioceseEntidadeService.ObterNomeDiocese(
  const ADioceseId, ACidade: string): string;
begin
  if (FRepository = nil) or (Trim(ADioceseId) = '') then
    Exit('NÃO ENCONTRADO');
  Result := FRepository.BuscarDiocesePorCidade(Trim(ADioceseId), Trim(ACidade));
end;

end.
