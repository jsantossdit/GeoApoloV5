unit unt_clonarpermissao_service;

{
  Camada de Serviços e Regras de Negócio para Clonagem de Permissões de Usuários.
  Totalmente desacoplado de VCL, forms e componentes visuais.
}

interface

uses
  System.SysUtils, System.Classes,
  unt_clonarpermissao_types,
  unt_clonarpermissao_repository;

type
  TClonarPermissaoService = class
  private
    FRepo: TClonarPermissaoRepository;
  public
    constructor Create(ARepository: TClonarPermissaoRepository);

    function ListarUsuarios: TArray<TUsuarioResumoDTO>;
    function ValidarClonagem(const AOrigem, ADestino: string): TOperacaoResultadoClonagem;
    function ClonarPermissoes(
      const AOrigem, ADestino: string;
      const AOpcoes: TOpcoesClonagemDTO
    ): TOperacaoResultadoClonagem;
  end;

implementation

constructor TClonarPermissaoService.Create(ARepository: TClonarPermissaoRepository);
begin
  inherited Create;
  FRepo := ARepository;
end;

function TClonarPermissaoService.ListarUsuarios: TArray<TUsuarioResumoDTO>;
begin
  Result := FRepo.ListarUsuariosAtivos;
end;

function TClonarPermissaoService.ValidarClonagem(const AOrigem, ADestino: string): TOperacaoResultadoClonagem;
begin
  FillChar(Result, SizeOf(Result), 0);
  Result.Sucesso := False;

  if Trim(AOrigem) = '' then
  begin
    Result.Mensagem := 'Selecione o usuário de origem que servirá de modelo.';
    Exit;
  end;

  if Trim(ADestino) = '' then
  begin
    Result.Mensagem := 'Selecione o usuário de destino que receberá as permissões.';
    Exit;
  end;

  if SameText(Trim(AOrigem), Trim(ADestino)) then
  begin
    Result.Mensagem := 'O usuário de origem e o de destino não podem ser os mesmos.';
    Exit;
  end;

  if not FRepo.UsuarioTemDireitos(Trim(AOrigem)) then
  begin
    Result.Mensagem := Format('O usuário de origem "%s" não possui direitos cadastrados no sistema.', [AOrigem]);
    Exit;
  end;

  Result.Sucesso := True;
  Result.Mensagem := 'Validação de clonagem aprovada.';
end;

function TClonarPermissaoService.ClonarPermissoes(
  const AOrigem, ADestino: string;
  const AOpcoes: TOpcoesClonagemDTO
): TOperacaoResultadoClonagem;
var
  Val: TOperacaoResultadoClonagem;
  Rel: TRelatorioClonagemDTO;
begin
  Val := ValidarClonagem(AOrigem, ADestino);
  if not Val.Sucesso then
    Exit(Val);

  FillChar(Rel, SizeOf(Rel), 0);
  try
    if AOpcoes.DireitosSistema then
      Rel.TotalDireitosSistema := FRepo.ClonarDireitosSistema(AOrigem, ADestino);

    if AOpcoes.Relatorios then
      Rel.TotalRelatorios := FRepo.ClonarRelatorios(AOrigem, ADestino);

    if AOpcoes.ContasFinanceiras then
      Rel.TotalContasFinanceiras := FRepo.ClonarContasFinanceiras(AOrigem, ADestino);

    if AOpcoes.Formularios then
      Rel.TotalFormularios := FRepo.ClonarFormularios(AOrigem, ADestino);

    if AOpcoes.CategoriasEntidades then
      Rel.TotalCategoriasEntidades := FRepo.ClonarCategoriasEntidades(AOrigem, ADestino);

    if AOpcoes.TipoPagarReceber then
      Rel.TotalTipoPagarReceber := FRepo.ClonarTipoPagarReceber(AOrigem, ADestino);

    if AOpcoes.GruposUsuario then
      Rel.TotalGruposUsuario := FRepo.ClonarGruposUsuario(AOrigem, ADestino);

    if AOpcoes.Favoritos then
      Rel.TotalFavoritos := FRepo.ClonarFavoritos(AOrigem, ADestino);

    if AOpcoes.TourUsuario then
      Rel.TotalTourUsuario := FRepo.ClonarTourUsuario(AOrigem, ADestino);

    if AOpcoes.EmpresasFiliais then
      Rel.TotalEmpresasFiliais := FRepo.ClonarEmpresasFiliais(AOrigem, ADestino);

    Rel.TotalGeral :=
      Rel.TotalDireitosSistema +
      Rel.TotalRelatorios +
      Rel.TotalContasFinanceiras +
      Rel.TotalFormularios +
      Rel.TotalCategoriasEntidades +
      Rel.TotalTipoPagarReceber +
      Rel.TotalGruposUsuario +
      Rel.TotalFavoritos +
      Rel.TotalTourUsuario +
      Rel.TotalEmpresasFiliais;

    Result.Sucesso := True;
    Result.Mensagem := Format('Clonagem concluída com sucesso! Total de %d permissões concedidas.', [Rel.TotalGeral]);
    Result.TotalItens := Rel.TotalGeral;
    Result.Relatorio := Rel;
  except
    on E: Exception do
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Falha durante a replicação de permissões: ' + E.Message;
      Result.TotalItens := 0;
    end;
  end;
end;

end.
