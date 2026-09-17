unit unt_ocorrencia_service;

interface

uses
  System.SysUtils, System.Classes, unt_ocorrencia_types, unt_ocorrencia_repository;

type
  IOcorrenciaService = interface
    ['{9A0B1C2D-3E4F-5A6B-7C8D-9E0F1A2B3C4D}']
    function ListarOcorrencias(const AStatus: string = ''; const AEmpCod: string = ''): TArray<TOcorrenciaDTO>;
    function ObterOcorrencia(const AOcorCod: string): TOcorrenciaDTO;
    function SalvarOcorrencia(const ADTO: TOcorrenciaDTO): TResultadoOcorrencia;
    function CancelarOcorrencia(const AOcorCod, ADataCanc, ARespCanc, AMotCanc: string): TResultadoOcorrencia;
    function AtualizarSolucao(const AOcorCod, ARespTexto, AStatus, ARespSol: string): TResultadoOcorrencia;
    function ListarAreasDisponiveis: TArray<TMotivoOcorDTO>;
    function ListarMotivosPorArea(const APrefixoArea: string): TArray<TMotivoOcorDTO>;
    function ListarOrigens: TArray<TOrigemDTO>;
    function ListarSolicitantes(const AFiltro: string = ''): TArray<TSolicitanteDTO>;
  end;

  TOcorrenciaService = class(TInterfacedObject, IOcorrenciaService)
  private
    FRepo: IOcorrenciaRepository;
  public
    constructor Create(ARepository: IOcorrenciaRepository);
    function ListarOcorrencias(const AStatus: string = ''; const AEmpCod: string = ''): TArray<TOcorrenciaDTO>;
    function ObterOcorrencia(const AOcorCod: string): TOcorrenciaDTO;
    function SalvarOcorrencia(const ADTO: TOcorrenciaDTO): TResultadoOcorrencia;
    function CancelarOcorrencia(const AOcorCod, ADataCanc, ARespCanc, AMotCanc: string): TResultadoOcorrencia;
    function AtualizarSolucao(const AOcorCod, ARespTexto, AStatus, ARespSol: string): TResultadoOcorrencia;
    function ListarAreasDisponiveis: TArray<TMotivoOcorDTO>;
    function ListarMotivosPorArea(const APrefixoArea: string): TArray<TMotivoOcorDTO>;
    function ListarOrigens: TArray<TOrigemDTO>;
    function ListarSolicitantes(const AFiltro: string = ''): TArray<TSolicitanteDTO>;
  end;

implementation

constructor TOcorrenciaService.Create(ARepository: IOcorrenciaRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise Exception.Create('TOcorrenciaService: Repositorio e obrigatorio.');
  FRepo := ARepository;
end;

function TOcorrenciaService.ListarOcorrencias(const AStatus, AEmpCod: string): TArray<TOcorrenciaDTO>;
begin
  Result := FRepo.ListarOcorrencias(AStatus, AEmpCod);
end;

function TOcorrenciaService.ObterOcorrencia(const AOcorCod: string): TOcorrenciaDTO;
begin
  if Trim(AOcorCod) = '' then
    raise Exception.Create('Codigo da ocorrencia deve ser informado.');
  Result := FRepo.ObterOcorrencia(Trim(AOcorCod));
end;

function TOcorrenciaService.SalvarOcorrencia(const ADTO: TOcorrenciaDTO): TResultadoOcorrencia;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';
  Result.IdGerado := ADTO.OcorCod;

  if Trim(ADTO.EntCod) = '' then
  begin
    Result.Mensagem := 'Solicitante e obrigatorio.';
    Exit;
  end;

  if Trim(ADTO.MotOcorCodEstr) = '' then
  begin
    Result.Mensagem := 'Motivo da ocorrencia e obrigatorio.';
    Exit;
  end;

  if Trim(ADTO.OcorTexto) = '' then
  begin
    Result.Mensagem := 'Descricao da solicitacao e obrigatoria.';
    Exit;
  end;

  try
    if FRepo.SalvarOcorrencia(ADTO) then
    begin
      Result.Sucesso := True;
      Result.Mensagem := 'Ocorrencia gravada com sucesso.';
    end
    else
    begin
      Result.Mensagem := 'Falha ao gravar ocorrencia no banco de dados.';
    end;
  except
    on E: Exception do
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Erro ao salvar ocorrencia: ' + E.Message;
    end;
  end;
end;

function TOcorrenciaService.CancelarOcorrencia(const AOcorCod, ADataCanc, ARespCanc, AMotCanc: string): TResultadoOcorrencia;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';
  Result.IdGerado := AOcorCod;

  if Trim(AOcorCod) = '' then
  begin
    Result.Mensagem := 'Codigo da ocorrencia e obrigatorio para cancelamento.';
    Exit;
  end;

  if Trim(AMotCanc) = '' then
  begin
    Result.Mensagem := 'Motivo de cancelamento e obrigatorio.';
    Exit;
  end;

  if Trim(ADataCanc) = '' then
  begin
    Result.Mensagem := 'Data de cancelamento e obrigatoria.';
    Exit;
  end;

  try
    if FRepo.CancelarOcorrencia(AOcorCod, ADataCanc, ARespCanc, AMotCanc) then
    begin
      Result.Sucesso := True;
      Result.Mensagem := 'Ocorrencia cancelada com sucesso.';
    end
    else
    begin
      Result.Mensagem := 'Falha ao cancelar ocorrencia no banco de dados.';
    end;
  except
    on E: Exception do
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Erro ao cancelar ocorrencia: ' + E.Message;
    end;
  end;
end;

function TOcorrenciaService.AtualizarSolucao(const AOcorCod, ARespTexto, AStatus, ARespSol: string): TResultadoOcorrencia;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';
  Result.IdGerado := AOcorCod;

  if Trim(AOcorCod) = '' then
  begin
    Result.Mensagem := 'Codigo da ocorrencia e obrigatorio.';
    Exit;
  end;

  try
    if FRepo.AtualizarSolucao(AOcorCod, ARespTexto, AStatus, ARespSol) then
    begin
      Result.Sucesso := True;
      Result.Mensagem := 'Solucao da ocorrencia atualizada com sucesso.';
    end
    else
    begin
      Result.Mensagem := 'Falha ao atualizar solucao no banco de dados.';
    end;
  except
    on E: Exception do
    begin
      Result.Sucesso := False;
      Result.Mensagem := 'Erro ao atualizar solucao: ' + E.Message;
    end;
  end;
end;

function TOcorrenciaService.ListarAreasDisponiveis: TArray<TMotivoOcorDTO>;
begin
  Result := FRepo.ListarAreasDisponiveis;
end;

function TOcorrenciaService.ListarMotivosPorArea(const APrefixoArea: string): TArray<TMotivoOcorDTO>;
begin
  Result := FRepo.ListarMotivosPorArea(Trim(APrefixoArea));
end;

function TOcorrenciaService.ListarOrigens: TArray<TOrigemDTO>;
begin
  Result := FRepo.ListarOrigens;
end;

function TOcorrenciaService.ListarSolicitantes(const AFiltro: string): TArray<TSolicitanteDTO>;
begin
  Result := FRepo.ListarSolicitantes(Trim(AFiltro));
end;

end.
