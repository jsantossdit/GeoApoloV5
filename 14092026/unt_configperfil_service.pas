unit unt_configperfil_service;

{
  GeoApolo - Serviço de Regras de Negócio para Configuração de Perfis e Permissões
  Clean Architecture: Regras de negócio desacopladas da interface de usuário.
}

interface

uses
  System.SysUtils, unt_configperfil_types, unt_configperfil_repository;

type

  TConfigPerfilService = class
  private
    FRepository: TConfigPerfilRepository;
  public
    constructor Create(ARepository: TConfigPerfilRepository);

    function ListarCategorias(out ALista: TArray<string>): Boolean;
    function ListarPermissoes(const ACodigoGrupo: Integer; const ACategoria: string;
      out ALista: TArray<TDadosObjetoPerfil>): Boolean;

    function LiberarAcesso(const ACodigoObjeto, ACodigoGrupo: Integer): TResultadoConfigPerfil;
    function RevogarAcesso(const ACodigoObjeto, ACodigoGrupo: Integer): TResultadoConfigPerfil;

    function LiberarTodos(const ACodigosObjetos: TArray<Integer>;
      const ACodigoGrupo: Integer): TResultadoConfigPerfil;
    function RevogarTodos(const ACodigosObjetos: TArray<Integer>;
      const ACodigoGrupo: Integer): TResultadoConfigPerfil;

    function SincronizarComponente(const ANomeTecnico, ANomeAmigavel,
      ACategoria: string): Integer;
    function LimparComponentesObsoletos(const ANomesValidos: TArray<string>): Integer;
  end;

implementation

{ TConfigPerfilService }

constructor TConfigPerfilService.Create(ARepository: TConfigPerfilRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise EArgumentNilException.Create('TConfigPerfilService: Repositorio nao pode ser nulo.');
  FRepository := ARepository;
end;

function TConfigPerfilService.ListarCategorias(
  out ALista: TArray<string>): Boolean;
begin
  Result := FRepository.ListarCategorias(ALista);
end;

function TConfigPerfilService.ListarPermissoes(const ACodigoGrupo: Integer;
  const ACategoria: string; out ALista: TArray<TDadosObjetoPerfil>): Boolean;
begin
  if ACodigoGrupo <= 0 then
  begin
    SetLength(ALista, 0);
    Exit(False);
  end;
  Result := FRepository.ListarPermissoes(ACodigoGrupo, ACategoria, ALista);
end;

function TConfigPerfilService.LiberarAcesso(const ACodigoObjeto,
  ACodigoGrupo: Integer): TResultadoConfigPerfil;
begin
  Result.Sucesso       := False;
  Result.Mensagem      := '';
  Result.TotalAfetados := 0;

  if ACodigoGrupo <= 0 then
  begin
    Result.Mensagem := 'Selecione um grupo de usuarios antes de alterar permissoes.';
    Exit;
  end;

  if ACodigoObjeto <= 0 then
  begin
    Result.Mensagem := 'Identificador de objeto invalido.';
    Exit;
  end;

  if FRepository.AlterarPermissao(ACodigoObjeto, ACodigoGrupo, 'A') then
  begin
    Result.Sucesso       := True;
    Result.Mensagem      := 'Permissao concedida com sucesso (Liberado).';
    Result.TotalAfetados := 1;
  end
  else
    Result.Mensagem := 'Falha ao conceder permissao ao objeto.';
end;

function TConfigPerfilService.RevogarAcesso(const ACodigoObjeto,
  ACodigoGrupo: Integer): TResultadoConfigPerfil;
begin
  Result.Sucesso       := False;
  Result.Mensagem      := '';
  Result.TotalAfetados := 0;

  if ACodigoGrupo <= 0 then
  begin
    Result.Mensagem := 'Selecione um grupo de usuarios antes de alterar permissoes.';
    Exit;
  end;

  if ACodigoObjeto <= 0 then
  begin
    Result.Mensagem := 'Identificador de objeto invalido.';
    Exit;
  end;

  if FRepository.AlterarPermissao(ACodigoObjeto, ACodigoGrupo, 'N') then
  begin
    Result.Sucesso       := True;
    Result.Mensagem      := 'Permissao revogada com sucesso (Bloqueado).';
    Result.TotalAfetados := 1;
  end
  else
    Result.Mensagem := 'Falha ao revogar permissao do objeto.';
end;

function TConfigPerfilService.LiberarTodos(
  const ACodigosObjetos: TArray<Integer>;
  const ACodigoGrupo: Integer): TResultadoConfigPerfil;
var
  Total: Integer;
begin
  Result.Sucesso       := False;
  Result.Mensagem      := '';
  Result.TotalAfetados := 0;

  if ACodigoGrupo <= 0 then
  begin
    Result.Mensagem := 'Selecione um grupo de usuarios antes de liberar permissoes.';
    Exit;
  end;

  if Length(ACodigosObjetos) = 0 then
  begin
    Result.Sucesso  := True;
    Result.Mensagem := 'Nenhum objeto para liberar.';
    Exit;
  end;

  Total := FRepository.AlterarPermissaoLote(ACodigosObjetos, ACodigoGrupo, 'A');
  Result.Sucesso       := True;
  Result.TotalAfetados := Total;
  Result.Mensagem      := Format('%d permissao(oes) liberada(s) com sucesso.', [Total]);
end;

function TConfigPerfilService.RevogarTodos(
  const ACodigosObjetos: TArray<Integer>;
  const ACodigoGrupo: Integer): TResultadoConfigPerfil;
var
  Total: Integer;
begin
  Result.Sucesso       := False;
  Result.Mensagem      := '';
  Result.TotalAfetados := 0;

  if ACodigoGrupo <= 0 then
  begin
    Result.Mensagem := 'Selecione um grupo de usuarios antes de revogar permissoes.';
    Exit;
  end;

  if Length(ACodigosObjetos) = 0 then
  begin
    Result.Sucesso  := True;
    Result.Mensagem := 'Nenhum objeto para revogar.';
    Exit;
  end;

  Total := FRepository.AlterarPermissaoLote(ACodigosObjetos, ACodigoGrupo, 'N');
  Result.Sucesso       := True;
  Result.TotalAfetados := Total;
  Result.Mensagem      := Format('%d permissao(oes) revogada(s) com sucesso.', [Total]);
end;

function TConfigPerfilService.SincronizarComponente(const ANomeTecnico,
  ANomeAmigavel, ACategoria: string): Integer;
begin
  if Trim(ANomeTecnico) = '' then
    Exit(0);
  Result := FRepository.SincronizarObjeto(ANomeTecnico, ANomeAmigavel, ACategoria);
end;

function TConfigPerfilService.LimparComponentesObsoletos(
  const ANomesValidos: TArray<string>): Integer;
begin
  Result := FRepository.LimparObjetosObsoletos(ANomesValidos);
end;

end.
