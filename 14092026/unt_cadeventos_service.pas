unit unt_cadeventos_service;

interface

uses
  System.SysUtils, System.Classes, unt_cadeventos_types, unt_cadeventos_repository;

type
  ICadEventosService = interface
    ['{8E1A2B3C-4D5E-6F7A-8B9C-0D1E2F3A4B5C}']
    function ListarEventos(const AFiltroTema: string = ''): TArray<TEventoDTO>;
    function ObterEvento(const AIdEvento: string): TEventoDTO;
    function SalvarEvento(const AEvento: TEventoDTO): TResultadoEvento;
    function ExcluirEvento(const AIdEvento: string): TResultadoEvento;
    function ListarTiposEvento: TArray<TTipoEventoDTO>;
  end;

  TCadEventosService = class(TInterfacedObject, ICadEventosService)
  private
    FRepo: ICadEventosRepository;
  public
    constructor Create(ARepository: ICadEventosRepository);
    function ListarEventos(const AFiltroTema: string = ''): TArray<TEventoDTO>;
    function ObterEvento(const AIdEvento: string): TEventoDTO;
    function SalvarEvento(const AEvento: TEventoDTO): TResultadoEvento;
    function ExcluirEvento(const AIdEvento: string): TResultadoEvento;
    function ListarTiposEvento: TArray<TTipoEventoDTO>;
  end;

implementation

constructor TCadEventosService.Create(ARepository: ICadEventosRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise Exception.Create('TCadEventosService: Repositório é obrigatório.');
  FRepo := ARepository;
end;

function TCadEventosService.ListarEventos(const AFiltroTema: string): TArray<TEventoDTO>;
begin
  Result := FRepo.ListarEventos(AFiltroTema);
end;

function TCadEventosService.ObterEvento(const AIdEvento: string): TEventoDTO;
begin
  if Trim(AIdEvento) = '' then
    raise Exception.Create('Identificador do evento deve ser informado.');
  Result := FRepo.ObterEvento(Trim(AIdEvento));
end;

function TCadEventosService.SalvarEvento(const AEvento: TEventoDTO): TResultadoEvento;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';
  Result.IdGerado := AEvento.IdEvento;

  if Trim(AEvento.IdEvento) = '' then
  begin
    Result.Mensagem := 'O código de identificação do evento é obrigatório.';
    Exit;
  end;

  if Trim(AEvento.Descricao) = '' then
  begin
    Result.Mensagem := 'A descrição / nome do evento é obrigatória.';
    Exit;
  end;

  try
    if FRepo.SalvarEvento(AEvento) then
    begin
      Result.Sucesso  := True;
      Result.Mensagem := 'Evento salvo com sucesso.';
    end
    else
      Result.Mensagem := 'Falha ao gravar evento.';
  except
    on E: Exception do
      Result.Mensagem := 'Erro ao salvar evento: ' + E.Message;
  end;
end;

function TCadEventosService.ExcluirEvento(const AIdEvento: string): TResultadoEvento;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';
  Result.IdGerado := AIdEvento;

  if Trim(AIdEvento) = '' then
  begin
    Result.Mensagem := 'Código do evento deve ser fornecido.';
    Exit;
  end;

  try
    if FRepo.ExcluirEvento(Trim(AIdEvento)) then
    begin
      Result.Sucesso  := True;
      Result.Mensagem := 'Evento excluído com sucesso.';
    end
    else
      Result.Mensagem := 'Falha ao excluir evento.';
  except
    on E: Exception do
      Result.Mensagem := 'Erro ao excluir evento: ' + E.Message;
  end;
end;

function TCadEventosService.ListarTiposEvento: TArray<TTipoEventoDTO>;
begin
  Result := FRepo.ListarTiposEvento;
end;

end.
