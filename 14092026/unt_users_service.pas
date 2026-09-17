unit unt_users_service;

interface

uses
  System.SysUtils, System.Classes, unt_users_types, unt_users_repository;

type
  IUsuariosService = interface
    ['{3A912BC4-72D9-48A6-A23F-8519B9123490}']
    function ListarUsuarios(const AFiltroNome: string = ''; AApenasAtivos: Boolean = True): TArray<TUsuarioDTO>;
    function ObterUsuario(const AUsucod: string): TUsuarioDTO;
    function SalvarUsuario(const AUsuario: TUsuarioDTO): TResultadoOperacaoUsuario;
    function ExcluirUsuario(const AUsucod: string): TResultadoOperacaoUsuario;

    function ListarDepartamentos(const AEmpCod: string = ''): TArray<TDepartamentoDTO>;
    function ListarSistemas: TArray<TSistemaDTO>;
    function ListarSistemasDoUsuario(const AUsucod: string): TArray<TSistemaDTO>;
    function VincularSistema(const AUsucod, ACodigoSistema: string): TResultadoOperacaoUsuario;
    function DesvincularSistema(const AUsucod, ACodigoSistema: string): TResultadoOperacaoUsuario;

    function ListarGrupos: TArray<TGrupoUsuarioDTO>;
    function SalvarGrupo(const ACodigoGrupo, ADescricao: string): TResultadoOperacaoUsuario;
    function ExcluirGrupo(const ACodigoGrupo: string): TResultadoOperacaoUsuario;
    function ListarUsuariosDoGrupo(const ACodigoGrupo: string): TArray<TVinculoGrupoUsuarioDTO>;
    function VincularUsuarioGrupo(const ACodigoGrupo, AUsucod: string): TResultadoOperacaoUsuario;
    function DesvincularUsuarioGrupo(const ACodigoGrupo, AUsucod: string): TResultadoOperacaoUsuario;

    function ListarObjetosPerfil(const ACodigoGrupo: string; const ACategoria: string = ''): TArray<TPerfilItemDTO>;
    function ListarCategoriasObjetos: TArray<string>;
    function AtualizarAcesso(const ACodigoGrupo, ACodigoObjeto: string; ALiberado: Boolean): TResultadoOperacaoUsuario;
  end;

  TUsuariosService = class(TInterfacedObject, IUsuariosService)
  private
    FRepo: IUsuariosRepository;
  public
    constructor Create(ARepository: IUsuariosRepository);

    function ListarUsuarios(const AFiltroNome: string = ''; AApenasAtivos: Boolean = True): TArray<TUsuarioDTO>;
    function ObterUsuario(const AUsucod: string): TUsuarioDTO;
    function SalvarUsuario(const AUsuario: TUsuarioDTO): TResultadoOperacaoUsuario;
    function ExcluirUsuario(const AUsucod: string): TResultadoOperacaoUsuario;

    function ListarDepartamentos(const AEmpCod: string = ''): TArray<TDepartamentoDTO>;
    function ListarSistemas: TArray<TSistemaDTO>;
    function ListarSistemasDoUsuario(const AUsucod: string): TArray<TSistemaDTO>;
    function VincularSistema(const AUsucod, ACodigoSistema: string): TResultadoOperacaoUsuario;
    function DesvincularSistema(const AUsucod, ACodigoSistema: string): TResultadoOperacaoUsuario;

    function ListarGrupos: TArray<TGrupoUsuarioDTO>;
    function SalvarGrupo(const ACodigoGrupo, ADescricao: string): TResultadoOperacaoUsuario;
    function ExcluirGrupo(const ACodigoGrupo: string): TResultadoOperacaoUsuario;
    function ListarUsuariosDoGrupo(const ACodigoGrupo: string): TArray<TVinculoGrupoUsuarioDTO>;
    function VincularUsuarioGrupo(const ACodigoGrupo, AUsucod: string): TResultadoOperacaoUsuario;
    function DesvincularUsuarioGrupo(const ACodigoGrupo, AUsucod: string): TResultadoOperacaoUsuario;

    function ListarObjetosPerfil(const ACodigoGrupo: string; const ACategoria: string = ''): TArray<TPerfilItemDTO>;
    function ListarCategoriasObjetos: TArray<string>;
    function AtualizarAcesso(const ACodigoGrupo, ACodigoObjeto: string; ALiberado: Boolean): TResultadoOperacaoUsuario;
  end;

implementation

constructor TUsuariosService.Create(ARepository: IUsuariosRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise Exception.Create('TUsuariosService: IUsuariosRepository é obrigatório.');
  FRepo := ARepository;
end;

function TUsuariosService.ListarUsuarios(const AFiltroNome: string; AApenasAtivos: Boolean): TArray<TUsuarioDTO>;
begin
  Result := FRepo.ListarUsuarios(AFiltroNome, AApenasAtivos);
end;

function TUsuariosService.ObterUsuario(const AUsucod: string): TUsuarioDTO;
begin
  if Trim(AUsucod) = '' then
    raise Exception.Create('Código do usuário não informado.');
  Result := FRepo.ObterUsuarioPorUsucod(AUsucod);
end;

function TUsuariosService.SalvarUsuario(const AUsuario: TUsuarioDTO): TResultadoOperacaoUsuario;
var
  Existente: TUsuarioDTO;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';
  Result.IdGerado := '';

  if Trim(AUsuario.Usucod) = '' then
  begin
    Result.Mensagem := 'O identificador (usucod) do usuário é obrigatório.';
    Exit;
  end;

  if Trim(AUsuario.Login) = '' then
  begin
    Result.Mensagem := 'O login de acesso é obrigatório.';
    Exit;
  end;

  if Trim(AUsuario.NomeCompleto) = '' then
  begin
    Result.Mensagem := 'O nome completo do usuário é obrigatório.';
    Exit;
  end;

  // Verifica se login já existe para outro usucod
  Existente := FRepo.ObterUsuarioPorLogin(Trim(AUsuario.Login));
  if (Trim(Existente.Usucod) <> '') and (Trim(Existente.Usucod) <> Trim(AUsuario.Usucod)) then
  begin
    Result.Mensagem := Format('O login "%s" já está em uso por outro usuário (%s).', [AUsuario.Login, Existente.NomeCompleto]);
    Exit;
  end;

  try
    if FRepo.SalvarUsuario(AUsuario) then
    begin
      Result.Sucesso  := True;
      Result.Mensagem := 'Usuário gravado com sucesso.';
      Result.IdGerado := AUsuario.Usucod;
    end
    else
      Result.Mensagem := 'Falha ao persistir dados do usuário.';
  except
    on E: Exception do
      Result.Mensagem := 'Erro ao salvar usuário: ' + E.Message;
  end;
end;

function TUsuariosService.ExcluirUsuario(const AUsucod: string): TResultadoOperacaoUsuario;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';
  Result.IdGerado := AUsucod;

  if Trim(AUsucod) = '' then
  begin
    Result.Mensagem := 'Código do usuário deve ser informado para exclusão.';
    Exit;
  end;

  try
    if FRepo.ExcluirUsuario(AUsucod) then
    begin
      Result.Sucesso  := True;
      Result.Mensagem := 'Usuário excluído com sucesso.';
    end
    else
      Result.Mensagem := 'Não foi possível excluir o usuário.';
  except
    on E: Exception do
      Result.Mensagem := 'Erro ao excluir usuário: ' + E.Message;
  end;
end;

function TUsuariosService.ListarDepartamentos(const AEmpCod: string): TArray<TDepartamentoDTO>;
begin
  Result := FRepo.ListarDepartamentos(AEmpCod);
end;

function TUsuariosService.ListarSistemas: TArray<TSistemaDTO>;
begin
  Result := FRepo.ListarSistemas;
end;

function TUsuariosService.ListarSistemasDoUsuario(const AUsucod: string): TArray<TSistemaDTO>;
begin
  if Trim(AUsucod) = '' then
  begin
    SetLength(Result, 0);
    Exit;
  end;
  Result := FRepo.ListarSistemasDoUsuario(AUsucod);
end;

function TUsuariosService.VincularSistema(const AUsucod, ACodigoSistema: string): TResultadoOperacaoUsuario;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';
  Result.IdGerado := ACodigoSistema;

  if (Trim(AUsucod) = '') or (Trim(ACodigoSistema) = '') then
  begin
    Result.Mensagem := 'Usuário e Sistema devem ser selecionados.';
    Exit;
  end;

  try
    if FRepo.VincularSistema(AUsucod, ACodigoSistema) then
    begin
      Result.Sucesso  := True;
      Result.Mensagem := 'Sistema vinculado com sucesso.';
    end;
  except
    on E: Exception do
      Result.Mensagem := 'Erro ao vincular sistema: ' + E.Message;
  end;
end;

function TUsuariosService.DesvincularSistema(const AUsucod, ACodigoSistema: string): TResultadoOperacaoUsuario;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';
  Result.IdGerado := ACodigoSistema;

  if (Trim(AUsucod) = '') or (Trim(ACodigoSistema) = '') then
  begin
    Result.Mensagem := 'Identificadores inválidos para desvinculação.';
    Exit;
  end;

  try
    if FRepo.DesvincularSistema(AUsucod, ACodigoSistema) then
    begin
      Result.Sucesso  := True;
      Result.Mensagem := 'Vínculo com sistema removido com sucesso.';
    end;
  except
    on E: Exception do
      Result.Mensagem := 'Erro ao desvincular sistema: ' + E.Message;
  end;
end;

function TUsuariosService.ListarGrupos: TArray<TGrupoUsuarioDTO>;
begin
  Result := FRepo.ListarGrupos;
end;

function TUsuariosService.SalvarGrupo(const ACodigoGrupo, ADescricao: string): TResultadoOperacaoUsuario;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';
  Result.IdGerado := ACodigoGrupo;

  if Trim(ACodigoGrupo) = '' then
  begin
    Result.Mensagem := 'O código do grupo é obrigatório.';
    Exit;
  end;

  if Trim(ADescricao) = '' then
  begin
    Result.Mensagem := 'A descrição do grupo não pode ser vazia.';
    Exit;
  end;

  try
    if FRepo.SalvarGrupo(ACodigoGrupo, ADescricao) then
    begin
      Result.Sucesso  := True;
      Result.Mensagem := 'Grupo salvo com sucesso.';
    end;
  except
    on E: Exception do
      Result.Mensagem := 'Erro ao salvar grupo: ' + E.Message;
  end;
end;

function TUsuariosService.ExcluirGrupo(const ACodigoGrupo: string): TResultadoOperacaoUsuario;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';
  Result.IdGerado := ACodigoGrupo;

  if Trim(ACodigoGrupo) = '' then
  begin
    Result.Mensagem := 'Código do grupo deve ser fornecido.';
    Exit;
  end;

  try
    if FRepo.ExcluirGrupo(ACodigoGrupo) then
    begin
      Result.Sucesso  := True;
      Result.Mensagem := 'Grupo e permissões associadas excluídos com sucesso.';
    end;
  except
    on E: Exception do
      Result.Mensagem := 'Erro ao excluir grupo: ' + E.Message;
  end;
end;

function TUsuariosService.ListarUsuariosDoGrupo(const ACodigoGrupo: string): TArray<TVinculoGrupoUsuarioDTO>;
begin
  if Trim(ACodigoGrupo) = '' then
  begin
    SetLength(Result, 0);
    Exit;
  end;
  Result := FRepo.ListarUsuariosDoGrupo(ACodigoGrupo);
end;

function TUsuariosService.VincularUsuarioGrupo(const ACodigoGrupo, AUsucod: string): TResultadoOperacaoUsuario;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';

  if (Trim(ACodigoGrupo) = '') or (Trim(AUsucod) = '') then
  begin
    Result.Mensagem := 'Grupo e usuário são obrigatórios.';
    Exit;
  end;

  try
    if FRepo.VincularUsuarioGrupo(ACodigoGrupo, AUsucod) then
    begin
      Result.Sucesso  := True;
      Result.Mensagem := 'Usuário adicionado ao grupo.';
    end;
  except
    on E: Exception do
      Result.Mensagem := 'Erro ao vincular usuário ao grupo: ' + E.Message;
  end;
end;

function TUsuariosService.DesvincularUsuarioGrupo(const ACodigoGrupo, AUsucod: string): TResultadoOperacaoUsuario;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';

  if (Trim(ACodigoGrupo) = '') or (Trim(AUsucod) = '') then
  begin
    Result.Mensagem := 'Identificadores inválidos.';
    Exit;
  end;

  try
    if FRepo.DesvincularUsuarioGrupo(ACodigoGrupo, AUsucod) then
    begin
      Result.Sucesso  := True;
      Result.Mensagem := 'Usuário removido do grupo.';
    end;
  except
    on E: Exception do
      Result.Mensagem := 'Erro ao desvincular usuário do grupo: ' + E.Message;
  end;
end;

function TUsuariosService.ListarObjetosPerfil(const ACodigoGrupo: string; const ACategoria: string): TArray<TPerfilItemDTO>;
begin
  if Trim(ACodigoGrupo) = '' then
  begin
    SetLength(Result, 0);
    Exit;
  end;
  Result := FRepo.ListarObjetosPerfil(ACodigoGrupo, ACategoria);
end;

function TUsuariosService.ListarCategoriasObjetos: TArray<string>;
begin
  Result := FRepo.ListarCategoriasObjetos;
end;

function TUsuariosService.AtualizarAcesso(const ACodigoGrupo, ACodigoObjeto: string; ALiberado: Boolean): TResultadoOperacaoUsuario;
var
  StatusStr: string;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';

  if (Trim(ACodigoGrupo) = '') or (Trim(ACodigoObjeto) = '') then
  begin
    Result.Mensagem := 'Grupo e objeto são obrigatórios.';
    Exit;
  end;

  if ALiberado then
    StatusStr := 'A'
  else
    StatusStr := 'N';

  try
    if FRepo.AtualizarStatusAcesso(ACodigoGrupo, ACodigoObjeto, StatusStr) then
    begin
      Result.Sucesso  := True;
      if ALiberado then
        Result.Mensagem := 'Acesso liberado com sucesso.'
      else
        Result.Mensagem := 'Acesso revogado/bloqueado.';
    end;
  except
    on E: Exception do
      Result.Mensagem := 'Erro ao atualizar permissão: ' + E.Message;
  end;
end;

end.
