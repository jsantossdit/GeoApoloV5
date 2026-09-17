unit unt_cadtipotratamento_service;

interface

uses
  System.SysUtils, System.Classes, unt_cadtipotratamento_types, unt_cadtipotratamento_repository;

type
  ICadTipoTratamentoService = interface
    ['{9F3C4D5E-6A7B-8C9D-0E1F-2A3B4C5D6E7F}']
    function ListarTiposTratamento: TArray<TTipoTratamentoDTO>;
    function ObterTipoTratamento(const ACodigo: string): TTipoTratamentoDTO;
    function SalvarTipoTratamento(const ADTO: TTipoTratamentoDTO): TResultadoTipoTratamento;
    function ExcluirTipoTratamento(const ACodigo: string): TResultadoTipoTratamento;
  end;

  TCadTipoTratamentoService = class(TInterfacedObject, ICadTipoTratamentoService)
  private
    FRepo: ICadTipoTratamentoRepository;
  public
    constructor Create(ARepository: ICadTipoTratamentoRepository);
    function ListarTiposTratamento: TArray<TTipoTratamentoDTO>;
    function ObterTipoTratamento(const ACodigo: string): TTipoTratamentoDTO;
    function SalvarTipoTratamento(const ADTO: TTipoTratamentoDTO): TResultadoTipoTratamento;
    function ExcluirTipoTratamento(const ACodigo: string): TResultadoTipoTratamento;
  end;

implementation

constructor TCadTipoTratamentoService.Create(ARepository: ICadTipoTratamentoRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise Exception.Create('TCadTipoTratamentoService: Repositório é obrigatório.');
  FRepo := ARepository;
end;

function TCadTipoTratamentoService.ListarTiposTratamento: TArray<TTipoTratamentoDTO>;
begin
  Result := FRepo.ListarTiposTratamento;
end;

function TCadTipoTratamentoService.ObterTipoTratamento(const ACodigo: string): TTipoTratamentoDTO;
begin
  if Trim(ACodigo) = '' then
    raise Exception.Create('Código do tipo de tratamento deve ser informado.');
  Result := FRepo.ObterTipoTratamento(Trim(ACodigo));
end;

function TCadTipoTratamentoService.SalvarTipoTratamento(const ADTO: TTipoTratamentoDTO): TResultadoTipoTratamento;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';
  Result.IdGerado := ADTO.TipoTratCod;

  if Trim(ADTO.TipoTratCod) = '' then
  begin
    Result.Mensagem := 'O código do tipo de tratamento é obrigatório.';
    Exit;
  end;

  if Trim(ADTO.Abreviatura) = '' then
  begin
    Result.Mensagem := 'A abreviatura (ex: Sr., Pe., Dom) é obrigatória.';
    Exit;
  end;

  try
    if FRepo.SalvarTipoTratamento(ADTO) then
    begin
      Result.Sucesso  := True;
      Result.Mensagem := 'Tipo de tratamento salvo com sucesso.';
    end
    else
      Result.Mensagem := 'Falha ao salvar tipo de tratamento.';
  except
    on E: Exception do
      Result.Mensagem := 'Erro ao salvar tipo de tratamento: ' + E.Message;
  end;
end;

function TCadTipoTratamentoService.ExcluirTipoTratamento(const ACodigo: string): TResultadoTipoTratamento;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';
  Result.IdGerado := ACodigo;

  if Trim(ACodigo) = '' then
  begin
    Result.Mensagem := 'Código do tipo de tratamento deve ser fornecido.';
    Exit;
  end;

  try
    if FRepo.ExcluirTipoTratamento(Trim(ACodigo)) then
    begin
      Result.Sucesso  := True;
      Result.Mensagem := 'Tipo de tratamento excluído com sucesso.';
    end
    else
      Result.Mensagem := 'Falha ao excluir tipo de tratamento.';
  except
    on E: Exception do
      Result.Mensagem := 'Erro ao excluir tipo de tratamento: ' + E.Message;
  end;
end;

end.
