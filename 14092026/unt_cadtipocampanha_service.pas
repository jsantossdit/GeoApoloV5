unit unt_cadtipocampanha_service;

interface

uses
  System.SysUtils, System.Classes, unt_cadtipocampanha_types, unt_cadtipocampanha_repository;

type
  ICadTipoCampanhaService = interface
    ['{7C1B2C3D-4E5F-6A7B-8C9D-0E1F2A3B4C5E}']
    function ListarTiposCampanha: TArray<TTipoCampanhaDTO>;
    function ObterTipoCampanha(const ACodigo: string): TTipoCampanhaDTO;
    function SalvarTipoCampanha(const ADTO: TTipoCampanhaDTO): TResultadoTipoCampanha;
    function ExcluirTipoCampanha(const ACodigo: string): TResultadoTipoCampanha;
  end;

  TCadTipoCampanhaService = class(TInterfacedObject, ICadTipoCampanhaService)
  private
    FRepo: ICadTipoCampanhaRepository;
  public
    constructor Create(ARepository: ICadTipoCampanhaRepository);
    function ListarTiposCampanha: TArray<TTipoCampanhaDTO>;
    function ObterTipoCampanha(const ACodigo: string): TTipoCampanhaDTO;
    function SalvarTipoCampanha(const ADTO: TTipoCampanhaDTO): TResultadoTipoCampanha;
    function ExcluirTipoCampanha(const ACodigo: string): TResultadoTipoCampanha;
  end;

implementation

constructor TCadTipoCampanhaService.Create(ARepository: ICadTipoCampanhaRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise Exception.Create('TCadTipoCampanhaService: Repositório é obrigatório.');
  FRepo := ARepository;
end;

function TCadTipoCampanhaService.ListarTiposCampanha: TArray<TTipoCampanhaDTO>;
begin
  Result := FRepo.ListarTiposCampanha;
end;

function TCadTipoCampanhaService.ObterTipoCampanha(const ACodigo: string): TTipoCampanhaDTO;
begin
  if Trim(ACodigo) = '' then
    raise Exception.Create('Código do tipo de campanha deve ser informado.');
  Result := FRepo.ObterTipoCampanha(Trim(ACodigo));
end;

function TCadTipoCampanhaService.SalvarTipoCampanha(const ADTO: TTipoCampanhaDTO): TResultadoTipoCampanha;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';
  Result.IdGerado := ADTO.CodigoTipoCampanha;

  if Trim(ADTO.CodigoTipoCampanha) = '' then
  begin
    Result.Mensagem := 'O código do tipo de campanha é obrigatório.';
    Exit;
  end;

  if Trim(ADTO.DescricaoTipoCamp) = '' then
  begin
    Result.Mensagem := 'A descrição do tipo de campanha não pode estar vazia.';
    Exit;
  end;

  try
    if FRepo.SalvarTipoCampanha(ADTO) then
    begin
      Result.Sucesso  := True;
      Result.Mensagem := 'Tipo de campanha gravado com sucesso.';
    end
    else
      Result.Mensagem := 'Falha ao salvar tipo de campanha.';
  except
    on E: Exception do
      Result.Mensagem := 'Erro ao salvar tipo de campanha: ' + E.Message;
  end;
end;

function TCadTipoCampanhaService.ExcluirTipoCampanha(const ACodigo: string): TResultadoTipoCampanha;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';
  Result.IdGerado := ACodigo;

  if Trim(ACodigo) = '' then
  begin
    Result.Mensagem := 'Código do tipo de campanha deve ser informado.';
    Exit;
  end;

  try
    if FRepo.ExcluirTipoCampanha(Trim(ACodigo)) then
    begin
      Result.Sucesso  := True;
      Result.Mensagem := 'Tipo de campanha excluído com sucesso.';
    end
    else
      Result.Mensagem := 'Falha ao excluir tipo de campanha.';
  except
    on E: Exception do
      Result.Mensagem := 'Erro ao excluir tipo de campanha: ' + E.Message;
  end;
end;

end.
