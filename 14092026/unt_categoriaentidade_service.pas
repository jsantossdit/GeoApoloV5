unit unt_categoriaentidade_service;

{
  Serviço de Negócio para Relacionamento de Usuário/Grupo com Categorias de Entidades.
  Totalmente desacoplado de VCL, Grids e Gauges.
}

interface

uses
  System.SysUtils, System.Classes,
  unt_categoriaentidade_types, unt_categoriaentidade_repository;

type
  TCategoriaEntidadeService = class
  private
    FRepo: TCategoriaEntidadeRepository;
  public
    constructor Create(ARepository: TCategoriaEntidadeRepository);

    function ObterCategorias(const AModo: TModoRelacionamento; const AId: string): TArray<TCategoriaResumoDTO>;
    function VincularCategoria(const AModo: TModoRelacionamento; const AId, ACategoria: string): TOperacaoResultado;
    function RelacionarEntidades(const AModo: TModoRelacionamento; const AId, ACategoria: string): TOperacaoResultado;
    function RemoverRelacionamento(const AModo: TModoRelacionamento; const AId, ACategoria: string): TOperacaoResultado;
  end;

implementation

constructor TCategoriaEntidadeService.Create(ARepository: TCategoriaEntidadeRepository);
begin
  inherited Create;
  FRepo := ARepository;
end;

function TCategoriaEntidadeService.ObterCategorias(const AModo: TModoRelacionamento; const AId: string): TArray<TCategoriaResumoDTO>;
begin
  if Trim(AId) = '' then
  begin
    SetLength(Result, 0);
    Exit;
  end;

  if AModo = mrUsuario then
    Result := FRepo.ListarCategoriasDoUsuario(AId)
  else
    Result := FRepo.ListarCategoriasDoGrupo(AId);
end;

function TCategoriaEntidadeService.VincularCategoria(const AModo: TModoRelacionamento; const AId, ACategoria: string): TOperacaoResultado;
var
  Usuarios: TArray<string>;
  Usu: string;
begin
  if Trim(AId) = '' then
  begin
    Result.Sucesso := False;
    Result.Mensagem := 'Identificador de usuário ou grupo não informado.';
    Exit;
  end;

  if Trim(ACategoria) = '' then
  begin
    Result.Sucesso := False;
    Result.Mensagem := 'Código de categoria não informado.';
    Exit;
  end;

  if AModo = mrUsuario then
    Result := FRepo.VincularCategoriaUsuario(AId, ACategoria)
  else
  begin
    Usuarios := FRepo.ListarUsuariosDoGrupo(AId);
    for Usu in Usuarios do
      FRepo.VincularCategoriaUsuario(Usu, ACategoria);

    Result.Sucesso := True;
    Result.Mensagem := Format('Categoria vinculada a %d usuário(s) do grupo com sucesso!', [Length(Usuarios)]);
    Result.Codigo := ACategoria;
  end;
end;

function TCategoriaEntidadeService.RelacionarEntidades(const AModo: TModoRelacionamento; const AId, ACategoria: string): TOperacaoResultado;
var
  Usuarios: TArray<string>;
  Usu: string;
begin
  if (Trim(AId) = '') or (Trim(ACategoria) = '') then
  begin
    Result.Sucesso := False;
    Result.Mensagem := 'Parâmetros incompletos para relacionar entidades.';
    Exit;
  end;

  if AModo = mrUsuario then
    Result := FRepo.RelacionarEntidadesCategoriaUsuario(AId, ACategoria)
  else
  begin
    Usuarios := FRepo.ListarUsuariosDoGrupo(AId);
    for Usu in Usuarios do
      FRepo.RelacionarEntidadesCategoriaUsuario(Usu, ACategoria);

    Result.Sucesso := True;
    Result.Mensagem := Format('Entidades da categoria relacionadas para %d usuário(s) do grupo com sucesso!', [Length(Usuarios)]);
    Result.Codigo := ACategoria;
  end;
end;

function TCategoriaEntidadeService.RemoverRelacionamento(const AModo: TModoRelacionamento; const AId, ACategoria: string): TOperacaoResultado;
var
  Usuarios: TArray<string>;
  Usu: string;
begin
  if (Trim(AId) = '') or (Trim(ACategoria) = '') then
  begin
    Result.Sucesso := False;
    Result.Mensagem := 'Parâmetros incompletos para remoção.';
    Exit;
  end;

  if AModo = mrUsuario then
    Result := FRepo.RemoverCategoriaUsuario(AId, ACategoria)
  else
  begin
    Usuarios := FRepo.ListarUsuariosDoGrupo(AId);
    for Usu in Usuarios do
      FRepo.RemoverCategoriaUsuario(Usu, ACategoria);

    Result.Sucesso := True;
    Result.Mensagem := Format('Relacionamento removido para %d usuário(s) do grupo com sucesso!', [Length(Usuarios)]);
    Result.Codigo := ACategoria;
  end;
end;

end.
