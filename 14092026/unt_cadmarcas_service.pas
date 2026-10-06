unit unt_cadmarcas_service;

{
  Servico de Regras de Negocio para Marcas de Produtos.
  Validacoes de unicidade, codigo automatico e integridade.
}

interface

uses
  System.SysUtils, System.Classes,
  unt_cadmarcas_types, unt_cadmarcas_repository;

type
  IMarcaService = interface
    ['{5C6D7E8F-9A0B-1C2D-3E4F-5A6B7C8D9E0F}']
    function ListarMarcas: TArray<TMarcaDTO>;
    function ObterMarca(const ACodigo: Integer): TMarcaDTO;
    function ObterProximoCodigo: Integer;
    function SalvarMarca(var AMarca: TMarcaDTO): TResultadoMarca;
    function ExcluirMarca(const ACodigo: Integer): TResultadoMarca;
  end;

  TMarcaService = class(TInterfacedObject, IMarcaService)
  private
    FRepo: IMarcaRepository;
  public
    constructor Create(ARepo: IMarcaRepository);
    function ListarMarcas: TArray<TMarcaDTO>;
    function ObterMarca(const ACodigo: Integer): TMarcaDTO;
    function ObterProximoCodigo: Integer;
    function SalvarMarca(var AMarca: TMarcaDTO): TResultadoMarca;
    function ExcluirMarca(const ACodigo: Integer): TResultadoMarca;
  end;

implementation

constructor TMarcaService.Create(ARepo: IMarcaRepository);
begin
  inherited Create;
  if not Assigned(ARepo) then
    raise Exception.Create('TMarcaService: IMarcaRepository e obrigatorio.');
  FRepo := ARepo;
end;

function TMarcaService.ListarMarcas: TArray<TMarcaDTO>;
begin
  Result := FRepo.ListarMarcas;
end;

function TMarcaService.ObterMarca(const ACodigo: Integer): TMarcaDTO;
begin
  if ACodigo <= 0 then
  begin
    FillChar(Result, SizeOf(Result), 0);
    Exit;
  end;
  Result := FRepo.ObterMarca(ACodigo);
end;

function TMarcaService.ObterProximoCodigo: Integer;
begin
  Result := FRepo.ObterProximoCodigo;
end;

function TMarcaService.SalvarMarca(var AMarca: TMarcaDTO): TResultadoMarca;
var
  Desc: string;
begin
  Desc := UpperCase(Trim(AMarca.DescricaoMarca));
  if Desc = '' then
  begin
    Result.Sucesso  := False;
    Result.Mensagem := 'Descricao da marca e obrigatoria.';
    Result.Codigo   := AMarca.CodigoMarca;
    Exit;
  end;

  if AMarca.CodigoMarca <= 0 then
    AMarca.CodigoMarca := FRepo.ObterProximoCodigo;

  AMarca.DescricaoMarca := Desc;

  if FRepo.ExisteDescricao(Desc, AMarca.CodigoMarca) then
  begin
    Result.Sucesso  := False;
    Result.Mensagem := Format('A marca "%s" ja esta cadastrada no sistema.', [Desc]);
    Result.Codigo   := AMarca.CodigoMarca;
    Exit;
  end;

  try
    FRepo.SalvarMarca(AMarca);
    Result.Sucesso  := True;
    Result.Mensagem := Format('Marca "%s" gravada com sucesso!', [Desc]);
    Result.Codigo   := AMarca.CodigoMarca;
  except
    on E: Exception do
    begin
      Result.Sucesso  := False;
      Result.Mensagem := 'Erro ao salvar marca: ' + E.Message;
      Result.Codigo   := AMarca.CodigoMarca;
    end;
  end;
end;

function TMarcaService.ExcluirMarca(const ACodigo: Integer): TResultadoMarca;
begin
  if ACodigo <= 0 then
  begin
    Result.Sucesso  := False;
    Result.Mensagem := 'Codigo da marca invalido para exclusao.';
    Result.Codigo   := ACodigo;
    Exit;
  end;

  try
    FRepo.ExcluirMarca(ACodigo);
    Result.Sucesso  := True;
    Result.Mensagem := 'Marca excluida com sucesso.';
    Result.Codigo   := ACodigo;
  except
    on E: Exception do
    begin
      Result.Sucesso  := False;
      Result.Mensagem := 'Erro ao excluir marca: ' + E.Message;
      Result.Codigo   := ACodigo;
    end;
  end;
end;

end.
