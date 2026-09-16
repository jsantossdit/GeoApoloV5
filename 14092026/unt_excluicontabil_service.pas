unit unt_excluicontabil_service;

interface

uses
  System.SysUtils, System.Classes, System.Generics.Collections,
  unt_excluicontabil_types, unt_excluicontabil_repository;

type
  TExcluiContabilService = class
  private
    FRepository: IExcluiContabilRepository;
  public
    constructor Create(ARepository: IExcluiContabilRepository);
    function Pesquisar(const ACampo, AValor, AEmpresaCod, AOrigem: string): TList<TLancamentoContabilDTO>;
    function ObterDetalhes(const AChave: string; out ALancamento: TLancamentoContabilDTO): Boolean;
    function ValidarExclusao(const AChave: string): TValidacaoExclusaoDTO;
    function ExcluirLancamento(const AChave, AUsuario: string; const AForcar: Boolean = False): TResultadoExclusaoContabil;
    function PesquisarModulo(const AFiltro: TFiltroExclusaoModuloDTO): TList<TLancamentoContabilDTO>;
    function ExcluirModuloLote(const AFiltro: TFiltroExclusaoModuloDTO; const AUsuario: string): TResultadoExclusaoContabil;
  end;

implementation

{ TExcluiContabilService }

constructor TExcluiContabilService.Create(ARepository: IExcluiContabilRepository);
begin
  inherited Create;
  if ARepository = nil then
    raise EArgumentNilException.Create('Repositório contábil não pode ser nulo.');
  FRepository := ARepository;
end;

function TExcluiContabilService.Pesquisar(
  const ACampo, AValor, AEmpresaCod, AOrigem: string): TList<TLancamentoContabilDTO>;
begin
  Result := FRepository.PesquisarLancamentos(ACampo, AValor, AEmpresaCod, AOrigem);
end;

function TExcluiContabilService.ObterDetalhes(
  const AChave: string; out ALancamento: TLancamentoContabilDTO): Boolean;
begin
  if Trim(AChave) = '' then
    Exit(False);
  Result := FRepository.ObterLancamento(AChave, ALancamento);
end;

function TExcluiContabilService.ValidarExclusao(const AChave: string): TValidacaoExclusaoDTO;
var
  Lanc: TLancamentoContabilDTO;
begin
  if Trim(AChave) = '' then
    Exit(TValidacaoExclusaoDTO.Bloqueado('Informe o número de chave do lançamento.', ''));

  if not FRepository.ObterLancamento(AChave, Lanc) then
    Exit(TValidacaoExclusaoDTO.Bloqueado('Lançamento contábil não localizado na base de dados.', ''));

  Result := FRepository.ValidarIntegridadeOrigem(Lanc);
end;

function TExcluiContabilService.ExcluirLancamento(
  const AChave, AUsuario: string; const AForcar: Boolean): TResultadoExclusaoContabil;
var
  Val: TValidacaoExclusaoDTO;
begin
  if Trim(AChave) = '' then
    Exit(TResultadoExclusaoContabil.CriarFalha('Chave do lançamento obrigatória.'));

  if not AForcar then
  begin
    Val := ValidarExclusao(AChave);
    if not Val.Permitido then
      Exit(TResultadoExclusaoContabil.CriarFalha(Val.Mensagem));
  end;

  Result := FRepository.ExcluirLancamento(AChave, AUsuario);
end;

function TExcluiContabilService.PesquisarModulo(
  const AFiltro: TFiltroExclusaoModuloDTO): TList<TLancamentoContabilDTO>;
begin
  if AFiltro.DataInicial > AFiltro.DataFinal then
    raise EArgumentException.Create('Data inicial não pode ser superior à data final.');

  Result := FRepository.PesquisarPorModulo(AFiltro);
end;

function TExcluiContabilService.ExcluirModuloLote(
  const AFiltro: TFiltroExclusaoModuloDTO; const AUsuario: string): TResultadoExclusaoContabil;
begin
  if AFiltro.DataInicial > AFiltro.DataFinal then
    Exit(TResultadoExclusaoContabil.CriarFalha('Data inicial superior à data final.'));

  Result := FRepository.ExcluirEmLotePorModulo(AFiltro, AUsuario);
end;

end.
