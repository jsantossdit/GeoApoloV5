unit unt_cadcategorias_service;

{
  GeoApolo - Serviço de Regras de Negócio para Cadastro de Categorias e Vínculos
  Clean Architecture: Regras de negócio desacopladas da interface de usuário.
}

interface

uses
  System.SysUtils, unt_cadcategorias_types, unt_cadcategorias_repository;

type

  TCadCategoriasService = class
  private
    FRepository: TCadCategoriasRepository;
  public
    constructor Create(ARepository: TCadCategoriasRepository);

    function ListarCategorias(out ALista: TArray<TDadosCadCategoria>): Boolean;
    function ObterCategoria(const ACodigoEstrutural: string;
      out ADados: TDadosCadCategoria): Boolean;
    function SalvarCategoria(const ADados: TDadosCadCategoria): TResultadoCadCategoria;
    function ExcluirCategoria(const ACodigoEstrutural: string;
      const AForcar: Boolean = False): TResultadoCadCategoria;

    function ListarUsuariosDisponiveis(const ACodigoEstrutural: string;
      out ALista: TArray<TVinculoUsuarioCategoria>): Boolean;
    function ListarUsuariosVinculados(const ACodigoEstrutural: string;
      out ALista: TArray<TVinculoUsuarioCategoria>): Boolean;

    function VincularUsuario(const ACodigoEstrutural, AUsucod: string): TResultadoCadCategoria;
    function DesvincularUsuario(const ACodigoEstrutural, AUsucod: string): TResultadoCadCategoria;
    function VincularTodos(const ACodigoEstrutural: string): TResultadoCadCategoria;
    function DesvincularTodos(const ACodigoEstrutural: string): TResultadoCadCategoria;
  end;

implementation

{ TCadCategoriasService }

constructor TCadCategoriasService.Create(ARepository: TCadCategoriasRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise EArgumentNilException.Create('TCadCategoriasService: Repositorio nao pode ser nulo.');
  FRepository := ARepository;
end;

function TCadCategoriasService.ListarCategorias(
  out ALista: TArray<TDadosCadCategoria>): Boolean;
begin
  Result := FRepository.ListarCategorias(ALista);
end;

function TCadCategoriasService.ObterCategoria(const ACodigoEstrutural: string;
  out ADados: TDadosCadCategoria): Boolean;
begin
  if Trim(ACodigoEstrutural) = '' then
    Exit(False);
  Result := FRepository.ObterCategoria(ACodigoEstrutural, ADados);
end;

function TCadCategoriasService.SalvarCategoria(
  const ADados: TDadosCadCategoria): TResultadoCadCategoria;
var
  DadosLimpos: TDadosCadCategoria;
begin
  Result.Sucesso       := False;
  Result.Mensagem      := '';
  Result.IdGerado      := '';
  Result.TotalAfetados := 0;

  DadosLimpos := ADados;
  DadosLimpos.CodigoEstrutural := Trim(DadosLimpos.CodigoEstrutural);
  DadosLimpos.Nome             := Trim(DadosLimpos.Nome);

  if DadosLimpos.CodigoEstrutural = '' then
  begin
    Result.Mensagem := 'O codigo estrutural da categoria e obrigatorio.';
    Exit;
  end;

  if DadosLimpos.Nome = '' then
  begin
    Result.Mensagem := 'O nome da categoria e obrigatorio.';
    Exit;
  end;

  if FRepository.SalvarCategoria(DadosLimpos) then
  begin
    Result.Sucesso       := True;
    Result.Mensagem      := 'Categoria salva com sucesso.';
    Result.IdGerado      := DadosLimpos.CodigoEstrutural;
    Result.TotalAfetados := 1;
  end
  else
    Result.Mensagem := 'Erro ao persistir a categoria no banco de dados.';
end;

function TCadCategoriasService.ExcluirCategoria(
  const ACodigoEstrutural: string;
  const AForcar: Boolean): TResultadoCadCategoria;
var
  CodLimpo: string;
  TotalEnt: Integer;
begin
  Result.Sucesso       := False;
  Result.Mensagem      := '';
  Result.IdGerado      := '';
  Result.TotalAfetados := 0;

  CodLimpo := Trim(ACodigoEstrutural);
  if CodLimpo = '' then
  begin
    Result.Mensagem := 'Codigo da categoria deve ser informado para exclusao.';
    Exit;
  end;

  TotalEnt := FRepository.TotalEntidadesVinculadas(CodLimpo);
  if (TotalEnt > 0) and (not AForcar) then
  begin
    Result.Mensagem := Format('Nao e permitido excluir a categoria pois existem %d entidade(s) vinculada(s) a ela.', [TotalEnt]);
    Exit;
  end;

  if FRepository.ExcluirCategoria(CodLimpo) then
  begin
    Result.Sucesso       := True;
    Result.Mensagem      := 'Categoria excluida com sucesso.';
    Result.IdGerado      := CodLimpo;
    Result.TotalAfetados := 1;
  end
  else
    Result.Mensagem := 'Erro ao excluir a categoria na base de dados.';
end;

function TCadCategoriasService.ListarUsuariosDisponiveis(
  const ACodigoEstrutural: string;
  out ALista: TArray<TVinculoUsuarioCategoria>): Boolean;
begin
  Result := FRepository.ListarUsuariosDisponiveis(ACodigoEstrutural, ALista);
end;

function TCadCategoriasService.ListarUsuariosVinculados(
  const ACodigoEstrutural: string;
  out ALista: TArray<TVinculoUsuarioCategoria>): Boolean;
begin
  Result := FRepository.ListarUsuariosVinculados(ACodigoEstrutural, ALista);
end;

function TCadCategoriasService.VincularUsuario(const ACodigoEstrutural,
  AUsucod: string): TResultadoCadCategoria;
begin
  Result.Sucesso       := False;
  Result.Mensagem      := '';
  Result.TotalAfetados := 0;

  if (Trim(ACodigoEstrutural) = '') or (Trim(AUsucod) = '') then
  begin
    Result.Mensagem := 'Categoria e Usuario devem ser informados para criar o vinculo.';
    Exit;
  end;

  if FRepository.VincularUsuario(ACodigoEstrutural, AUsucod) then
  begin
    Result.Sucesso       := True;
    Result.Mensagem      := 'Usuario vinculado a categoria com sucesso.';
    Result.TotalAfetados := 1;
  end
  else
    Result.Mensagem := 'Falha ao vincular usuario a categoria.';
end;

function TCadCategoriasService.DesvincularUsuario(const ACodigoEstrutural,
  AUsucod: string): TResultadoCadCategoria;
begin
  Result.Sucesso       := False;
  Result.Mensagem      := '';
  Result.TotalAfetados := 0;

  if (Trim(ACodigoEstrutural) = '') or (Trim(AUsucod) = '') then
  begin
    Result.Mensagem := 'Categoria e Usuario devem ser informados para desvincular.';
    Exit;
  end;

  if FRepository.DesvincularUsuario(ACodigoEstrutural, AUsucod) then
  begin
    Result.Sucesso       := True;
    Result.Mensagem      := 'Usuario desvinculado da categoria com sucesso.';
    Result.TotalAfetados := 1;
  end
  else
    Result.Mensagem := 'Falha ao desvincular usuario da categoria.';
end;

function TCadCategoriasService.VincularTodos(
  const ACodigoEstrutural: string): TResultadoCadCategoria;
var
  Total: Integer;
begin
  Result.Sucesso       := False;
  Result.Mensagem      := '';
  Result.TotalAfetados := 0;

  if Trim(ACodigoEstrutural) = '' then
  begin
    Result.Mensagem := 'Selecione uma categoria antes de vincular todos os usuarios.';
    Exit;
  end;

  Total := FRepository.VincularTodosUsuarios(ACodigoEstrutural);
  Result.Sucesso       := True;
  Result.TotalAfetados := Total;
  Result.Mensagem      := Format('%d usuario(s) vinculado(s) a categoria com sucesso.', [Total]);
end;

function TCadCategoriasService.DesvincularTodos(
  const ACodigoEstrutural: string): TResultadoCadCategoria;
var
  Total: Integer;
begin
  Result.Sucesso       := False;
  Result.Mensagem      := '';
  Result.TotalAfetados := 0;

  if Trim(ACodigoEstrutural) = '' then
  begin
    Result.Mensagem := 'Selecione uma categoria antes de desvincular todos os usuarios.';
    Exit;
  end;

  Total := FRepository.DesvincularTodosUsuarios(ACodigoEstrutural);
  Result.Sucesso       := True;
  Result.TotalAfetados := Total;
  Result.Mensagem      := Format('%d usuario(s) desvinculado(s) da categoria com sucesso.', [Total]);
end;

end.
