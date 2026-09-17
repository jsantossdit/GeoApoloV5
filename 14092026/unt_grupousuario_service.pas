unit unt_grupousuario_service;

{
  GeoApolo - Serviço de Regras de Negócio para Grupos de Usuários e Vínculos
  Clean Architecture: Regras de negócio desacopladas da interface de usuário.
}

interface

uses
  System.SysUtils, unt_grupousuario_types, unt_grupousuario_repository;

type

  TGrupoUsuarioService = class
  private
    FRepository: TGrupoUsuarioRepository;
  public
    constructor Create(ARepository: TGrupoUsuarioRepository);

    function ListarGrupos(out ALista: TArray<TDadosGrupoUsuario>): Boolean;
    function ObterGrupo(const ACodigoGrupo: string; out ADados: TDadosGrupoUsuario): Boolean;
    function SalvarGrupo(const ADados: TDadosGrupoUsuario): TResultadoGrupoUsuario;
    function ExcluirGrupo(const ACodigoGrupo: string;
      const AForcarCascata: Boolean = False): TResultadoGrupoUsuario;

    function ListarUsuariosGrupo(const ACodigoGrupo: string;
      out ALista: TArray<TVinculoUsuarioGrupo>): Boolean;
    function VincularUsuario(const ACodigoGrupo, AUsucod: string): TResultadoGrupoUsuario;
    function DesvincularUsuario(const ACodigoGrupo, AUsucod: string): TResultadoGrupoUsuario;
  end;

implementation

{ TGrupoUsuarioService }

constructor TGrupoUsuarioService.Create(ARepository: TGrupoUsuarioRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise EArgumentNilException.Create('TGrupoUsuarioService: Repositorio nao pode ser nulo.');
  FRepository := ARepository;
end;

function TGrupoUsuarioService.ListarGrupos(
  out ALista: TArray<TDadosGrupoUsuario>): Boolean;
begin
  Result := FRepository.ListarGrupos(ALista);
end;

function TGrupoUsuarioService.ObterGrupo(const ACodigoGrupo: string;
  out ADados: TDadosGrupoUsuario): Boolean;
begin
  if Trim(ACodigoGrupo) = '' then
    Exit(False);
  Result := FRepository.ObterGrupo(ACodigoGrupo, ADados);
end;

function TGrupoUsuarioService.SalvarGrupo(
  const ADados: TDadosGrupoUsuario): TResultadoGrupoUsuario;
var
  DadosLimpos: TDadosGrupoUsuario;
begin
  Result.Sucesso       := False;
  Result.Mensagem      := '';
  Result.IdGerado      := '';
  Result.TotalAfetados := 0;

  DadosLimpos := ADados;
  DadosLimpos.CodigoGrupo := Trim(DadosLimpos.CodigoGrupo);
  DadosLimpos.Descricao   := Trim(DadosLimpos.Descricao);

  if DadosLimpos.CodigoGrupo = '' then
  begin
    Result.Mensagem := 'O codigo do grupo de usuarios e obrigatorio.';
    Exit;
  end;

  if DadosLimpos.Descricao = '' then
  begin
    Result.Mensagem := 'A descricao do grupo nao pode ser vazia.';
    Exit;
  end;

  if FRepository.ExisteDescricaoGrupo(DadosLimpos.Descricao, DadosLimpos.CodigoGrupo) then
  begin
    Result.Mensagem := 'Ja existe um grupo cadastrado com esta mesma descricao: ' + DadosLimpos.Descricao;
    Exit;
  end;

  if FRepository.SalvarGrupo(DadosLimpos) then
  begin
    Result.Sucesso       := True;
    Result.Mensagem      := 'Grupo salvo com sucesso.';
    Result.IdGerado      := DadosLimpos.CodigoGrupo;
    Result.TotalAfetados := 1;
  end
  else
    Result.Mensagem := 'Erro ao persistir dados do grupo.';
end;

function TGrupoUsuarioService.ExcluirGrupo(const ACodigoGrupo: string;
  const AForcarCascata: Boolean): TResultadoGrupoUsuario;
var
  CodLimpo: string;
  TotalMembros: Integer;
begin
  Result.Sucesso       := False;
  Result.Mensagem      := '';
  Result.IdGerado      := '';
  Result.TotalAfetados := 0;

  CodLimpo := Trim(ACodigoGrupo);
  if CodLimpo = '' then
  begin
    Result.Mensagem := 'Codigo do grupo deve ser informado para exclusao.';
    Exit;
  end;

  TotalMembros := FRepository.TotalMembrosGrupo(CodLimpo);
  if (TotalMembros > 0) and (not AForcarCascata) then
  begin
    Result.Mensagem := Format('Nao e permitido excluir o grupo pois ha %d usuario(s) vinculado(s) a ele.', [TotalMembros]);
    Exit;
  end;

  if FRepository.ExcluirGrupo(CodLimpo) then
  begin
    Result.Sucesso       := True;
    Result.Mensagem      := 'Grupo e suas permissoes associadas excluidos com sucesso.';
    Result.IdGerado      := CodLimpo;
    Result.TotalAfetados := 1;
  end
  else
    Result.Mensagem := 'Falha ao excluir o grupo na base de dados.';
end;

function TGrupoUsuarioService.ListarUsuariosGrupo(const ACodigoGrupo: string;
  out ALista: TArray<TVinculoUsuarioGrupo>): Boolean;
begin
  if Trim(ACodigoGrupo) = '' then
  begin
    SetLength(ALista, 0);
    Exit(False);
  end;
  Result := FRepository.ListarUsuariosGrupo(ACodigoGrupo, ALista);
end;

function TGrupoUsuarioService.VincularUsuario(const ACodigoGrupo,
  AUsucod: string): TResultadoGrupoUsuario;
var
  CodGrupo, CodUsu: string;
begin
  Result.Sucesso       := False;
  Result.Mensagem      := '';
  Result.IdGerado      := '';
  Result.TotalAfetados := 0;

  CodGrupo := Trim(ACodigoGrupo);
  CodUsu   := Trim(AUsucod);

  if (CodGrupo = '') or (CodUsu = '') then
  begin
    Result.Mensagem := 'Grupo e Usuario devem ser selecionados para criar o vinculo.';
    Exit;
  end;

  if FRepository.ExisteVinculo(CodGrupo, CodUsu) then
  begin
    Result.Sucesso  := True;
    Result.Mensagem := 'O usuario ja esta vinculado a este grupo.';
    Exit;
  end;

  if FRepository.VincularUsuarioGrupo(CodGrupo, CodUsu) then
  begin
    Result.Sucesso       := True;
    Result.Mensagem      := 'Usuario vinculado ao grupo com sucesso.';
    Result.TotalAfetados := 1;
  end
  else
    Result.Mensagem := 'Falha ao vincular usuario ao grupo.';
end;

function TGrupoUsuarioService.DesvincularUsuario(const ACodigoGrupo,
  AUsucod: string): TResultadoGrupoUsuario;
var
  CodGrupo, CodUsu: string;
begin
  Result.Sucesso       := False;
  Result.Mensagem      := '';
  Result.IdGerado      := '';
  Result.TotalAfetados := 0;

  CodGrupo := Trim(ACodigoGrupo);
  CodUsu   := Trim(AUsucod);

  if (CodGrupo = '') or (CodUsu = '') then
  begin
    Result.Mensagem := 'Grupo e Usuario devem ser informados para desvincular.';
    Exit;
  end;

  if FRepository.DesvincularUsuarioGrupo(CodGrupo, CodUsu) then
  begin
    Result.Sucesso       := True;
    Result.Mensagem      := 'Usuario desvinculado do grupo com sucesso.';
    Result.TotalAfetados := 1;
  end
  else
    Result.Mensagem := 'Falha ao desvincular usuario do grupo.';
end;

end.
