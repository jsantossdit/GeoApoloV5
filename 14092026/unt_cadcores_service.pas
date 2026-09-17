unit unt_cadcores_service;

{
  Serviço de Regras de Negócio para Cores de Produtos.
  Validação de preenchimento e unicidade de descrição.
}

interface

uses
  System.SysUtils, System.Classes,
  unt_cadcores_types, unt_cadcores_repository;

type
  ICorService = interface
    ['{4D5E6F7A-8B9C-0D1E-2F3A-4B5C6D7E8F9A}']
    function ListarCores: TArray<TCorDTO>;
    function ObterCor(const ACodigo: Integer): TCorDTO;
    function ObterProximoCodigo: Integer;
    function SalvarCor(var ACor: TCorDTO): TResultadoCor;
    function ExcluirCor(const ACodigo: Integer): TResultadoCor;
  end;

  TCorService = class(TInterfacedObject, ICorService)
  private
    FRepo: ICorRepository;
  public
    constructor Create(ARepository: ICorRepository);
    function ListarCores: TArray<TCorDTO>;
    function ObterCor(const ACodigo: Integer): TCorDTO;
    function ObterProximoCodigo: Integer;
    function SalvarCor(var ACor: TCorDTO): TResultadoCor;
    function ExcluirCor(const ACodigo: Integer): TResultadoCor;
  end;

implementation

constructor TCorService.Create(ARepository: ICorRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise Exception.Create('TCorService: Repositorio e obrigatorio.');
  FRepo := ARepository;
end;

function TCorService.ListarCores: TArray<TCorDTO>;
begin
  Result := FRepo.ListarCores;
end;

function TCorService.ObterCor(const ACodigo: Integer): TCorDTO;
begin
  if ACodigo <= 0 then
    raise Exception.Create('Codigo da cor invalido.');
  Result := FRepo.ObterCor(ACodigo);
end;

function TCorService.ObterProximoCodigo: Integer;
begin
  Result := FRepo.ObterProximoCodigo;
end;

function TCorService.SalvarCor(var ACor: TCorDTO): TResultadoCor;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';
  Result.Codigo   := ACor.CodigoCor;

  if Trim(ACor.DescricaoCor) = '' then
  begin
    Result.Mensagem := 'Descricao da cor e obrigatoria.';
    Exit;
  end;

  if ACor.CodigoCor <= 0 then
  begin
    ACor.CodigoCor := FRepo.ObterProximoCodigo;
    Result.Codigo  := ACor.CodigoCor;
  end;

  if FRepo.ExisteDescricao(Trim(ACor.DescricaoCor), ACor.CodigoCor) then
  begin
    Result.Mensagem := 'A cor informada ja esta cadastrada.';
    Exit;
  end;

  try
    if FRepo.SalvarCor(ACor) then
    begin
      Result.Sucesso  := True;
      Result.Mensagem := 'Cor gravada com sucesso.';
    end
    else
    begin
      Result.Mensagem := 'Falha ao gravar cor no banco de dados.';
    end;
  except
    on E: Exception do
    begin
      Result.Sucesso  := False;
      Result.Mensagem := 'Erro ao salvar cor: ' + E.Message;
    end;
  end;
end;

function TCorService.ExcluirCor(const ACodigo: Integer): TResultadoCor;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';
  Result.Codigo   := ACodigo;

  if ACodigo <= 0 then
  begin
    Result.Mensagem := 'Codigo da cor e obrigatorio para exclusao.';
    Exit;
  end;

  try
    if FRepo.ExcluirCor(ACodigo) then
    begin
      Result.Sucesso  := True;
      Result.Mensagem := 'Cor excluida com sucesso.';
    end
    else
    begin
      Result.Mensagem := 'Falha ao excluir cor do banco de dados.';
    end;
  except
    on E: Exception do
    begin
      Result.Sucesso  := False;
      Result.Mensagem := 'Erro ao excluir cor: ' + E.Message;
    end;
  end;
end;

end.
