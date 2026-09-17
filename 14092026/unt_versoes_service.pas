unit unt_versoes_service;

{
  GeoApolo - Serviço de Regras de Negócio para Manutenção e Novidades de Versões
  Clean Architecture: Validações de integridade e publicação de versões.
}

interface

uses
  System.SysUtils, System.Classes,
  unt_versoes_types, unt_versoes_repository;

type

  TVersoesService = class
  private
    FRepository: TVersoesRepository;
  public
    constructor Create(ARepository: TVersoesRepository);

    function ListarVersoes(out ALista: TArray<TDadosVersao>): Boolean;
    function ObterVersao(const AIDVersao: string; out ADados: TDadosVersao): Boolean;
    function SalvarVersao(const ADados: TDadosVersao; AIsAlteracao: Boolean;
      out AResultado: TResultadoVersao): Boolean;
    function ExcluirVersao(const AIDVersao: string;
      out AResultado: TResultadoVersao): Boolean;
    function ObterNovidadesPendentes(const AIDVersao, AUsuCod: string;
      out ATextoNovidades: string): Boolean;
    function ConfirmarLeitura(const AIDVersao, AUsuCod: string): Boolean;
  end;

implementation

{ TVersoesService }

constructor TVersoesService.Create(ARepository: TVersoesRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise EArgumentNilException.Create('TVersoesService: Repositorio nao pode ser nulo.');
  FRepository := ARepository;
end;

function TVersoesService.ListarVersoes(out ALista: TArray<TDadosVersao>): Boolean;
begin
  Result := FRepository.ListarVersoes(ALista);
end;

function TVersoesService.ObterVersao(const AIDVersao: string;
  out ADados: TDadosVersao): Boolean;
begin
  if Trim(AIDVersao) = '' then
  begin
    ADados := Default(TDadosVersao);
    Result := False;
    Exit;
  end;
  Result := FRepository.ObterVersao(Trim(AIDVersao), ADados);
end;

function TVersoesService.SalvarVersao(const ADados: TDadosVersao;
  AIsAlteracao: Boolean; out AResultado: TResultadoVersao): Boolean;
var
  DadosNormalizados: TDadosVersao;
begin
  Result := False;
  AResultado.Sucesso := False;
  AResultado.IDVersao := Trim(ADados.IDVersao);

  if Trim(ADados.IDVersao) = '' then
  begin
    AResultado.Mensagem := 'Identificador da versao e obrigatorio.';
    Exit;
  end;

  if (Trim(ADados.DataLancamento) = '') or (ADados.DataLancamento = '  /  /    ') then
  begin
    AResultado.Mensagem := 'Data de liberacao da versao e obrigatoria.';
    Exit;
  end;

  DadosNormalizados := ADados;
  DadosNormalizados.IDVersao := Trim(ADados.IDVersao);
  DadosNormalizados.DataLancamento := Trim(ADados.DataLancamento);

  if (UpperCase(Trim(ADados.StatusVersao)) = 'S') or (UpperCase(Trim(ADados.StatusVersao)) = 'LIBERADA') then
    DadosNormalizados.StatusVersao := 'S'
  else
    DadosNormalizados.StatusVersao := 'N';

  try
    if FRepository.SalvarVersao(DadosNormalizados, AIsAlteracao) then
    begin
      AResultado.Sucesso := True;
      AResultado.Mensagem := 'Versao salva com sucesso!';
      Result := True;
    end
    else
    begin
      AResultado.Mensagem := 'Falha ao persistir versao no banco de dados.';
    end;
  except
    on E: Exception do
      AResultado.Mensagem := 'Erro ao salvar versao: ' + E.Message;
  end;
end;

function TVersoesService.ExcluirVersao(const AIDVersao: string;
  out AResultado: TResultadoVersao): Boolean;
var
  VersaoExistente: TDadosVersao;
begin
  Result := False;
  AResultado.Sucesso := False;
  AResultado.IDVersao := Trim(AIDVersao);

  if Trim(AIDVersao) = '' then
  begin
    AResultado.Mensagem := 'Identificador da versao invalido para exclusao.';
    Exit;
  end;

  if not FRepository.ObterVersao(Trim(AIDVersao), VersaoExistente) then
  begin
    AResultado.Mensagem := 'Versao informada nao encontrada.';
    Exit;
  end;

  if VersaoExistente.StatusVersao = 'S' then
  begin
    AResultado.Mensagem := 'Nao e permitido excluir uma versao ja liberada e homologada.';
    Exit;
  end;

  try
    if FRepository.ExcluirVersao(Trim(AIDVersao)) then
    begin
      AResultado.Sucesso := True;
      AResultado.Mensagem := 'Versao excluida com sucesso.';
      Result := True;
    end
    else
    begin
      AResultado.Mensagem := 'Falha ao excluir versao no banco de dados.';
    end;
  except
    on E: Exception do
      AResultado.Mensagem := 'Erro ao excluir versao: ' + E.Message;
  end;
end;

function TVersoesService.ObterNovidadesPendentes(const AIDVersao,
  AUsuCod: string; out ATextoNovidades: string): Boolean;
var
  Versao: TDadosVersao;
begin
  Result := False;
  ATextoNovidades := '';

  if (Trim(AIDVersao) = '') or (Trim(AUsuCod) = '') then
    Exit;

  if FRepository.UsuarioJaViuVersao(Trim(AIDVersao), Trim(AUsuCod)) then
    Exit; // Ja visualizou

  if FRepository.ObterVersao(Trim(AIDVersao), Versao) then
  begin
    if Versao.StatusVersao = 'S' then
    begin
      ATextoNovidades := Versao.TextoNovaVersao;
      Result := True;
    end;
  end;
end;

function TVersoesService.ConfirmarLeitura(const AIDVersao,
  AUsuCod: string): Boolean;
begin
  if (Trim(AIDVersao) = '') or (Trim(AUsuCod) = '') then
  begin
    Result := False;
    Exit;
  end;
  Result := FRepository.RegistrarLeituraVersao(Trim(AIDVersao), Trim(AUsuCod));
end;

end.
