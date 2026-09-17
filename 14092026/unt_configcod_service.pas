unit unt_configcod_service;

{
  GeoApolo - Serviço de Regras de Negócio para Manutenção de Códigos do Sistema
  Clean Architecture: Validações de integridade cadastral e sequencial numérico.
}

interface

uses
  System.SysUtils, System.Classes,
  unt_configcod_types, unt_configcod_repository;

type

  TConfigCodService = class
  private
    FRepository: TConfigCodRepository;
  public
    constructor Create(ARepository: TConfigCodRepository);

    function ListarTabelas(const AFiltro: string; out ALista: TArray<TDadosConfigCod>): Boolean;
    function ObterConfigCod(const AGeoTabela: string; out ADados: TDadosConfigCod): Boolean;
    function AtualizarConfigCod(const AGeoTabela: string; AProximoCodigo: Integer;
      const ATabelaAtiva: string; out AResultado: TResultadoConfigCod): Boolean;
    function SalvarConfigCod(const ADados: TDadosConfigCod;
      out AResultado: TResultadoConfigCod): Boolean;
  end;

implementation

{ TConfigCodService }

constructor TConfigCodService.Create(ARepository: TConfigCodRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise EArgumentNilException.Create('TConfigCodService: Repositorio nao pode ser nulo.');
  FRepository := ARepository;
end;

function TConfigCodService.ListarTabelas(const AFiltro: string;
  out ALista: TArray<TDadosConfigCod>): Boolean;
begin
  Result := FRepository.ListarTabelas(Trim(AFiltro), ALista);
end;

function TConfigCodService.ObterConfigCod(const AGeoTabela: string;
  out ADados: TDadosConfigCod): Boolean;
begin
  if Trim(AGeoTabela) = '' then
  begin
    ADados := Default(TDadosConfigCod);
    Result := False;
    Exit;
  end;
  Result := FRepository.ObterConfigCod(Trim(AGeoTabela), ADados);
end;

function TConfigCodService.AtualizarConfigCod(const AGeoTabela: string;
  AProximoCodigo: Integer; const ATabelaAtiva: string;
  out AResultado: TResultadoConfigCod): Boolean;
var
  TabelaLimpa: string;
  StatusAtiva: string;
begin
  Result := False;
  AResultado.Sucesso := False;
  AResultado.GeoTabela := Trim(AGeoTabela);
  AResultado.ProximoCodigo := AProximoCodigo;

  TabelaLimpa := Trim(AGeoTabela);
  if TabelaLimpa = '' then
  begin
    AResultado.Mensagem := 'Nome da tabela nao pode ser em branco.';
    Exit;
  end;

  if AProximoCodigo < 0 then
  begin
    AResultado.Mensagem := 'O proximo codigo sequencial nao pode ser negativo.';
    Exit;
  end;

  if (UpperCase(Trim(ATabelaAtiva)) = 'S') or (UpperCase(Trim(ATabelaAtiva)) = 'TRUE') then
    StatusAtiva := 'S'
  else
    StatusAtiva := 'N';

  try
    if FRepository.AtualizarProximoCodigo(TabelaLimpa, AProximoCodigo, StatusAtiva) then
    begin
      AResultado.Sucesso := True;
      AResultado.Mensagem := 'Configuracao da tabela ' + TabelaLimpa + ' atualizada com sucesso!';
      Result := True;
    end
    else
    begin
      AResultado.Mensagem := 'Falha ao atualizar configuracao no banco de dados.';
    end;
  except
    on E: Exception do
      AResultado.Mensagem := 'Erro ao atualizar configuracao: ' + E.Message;
  end;
end;

function TConfigCodService.SalvarConfigCod(const ADados: TDadosConfigCod;
  out AResultado: TResultadoConfigCod): Boolean;
var
  DadosLimpos: TDadosConfigCod;
begin
  Result := False;
  AResultado.Sucesso := False;
  AResultado.GeoTabela := Trim(ADados.GeoTabela);
  AResultado.ProximoCodigo := ADados.ProximoCodigo;

  if Trim(ADados.GeoTabela) = '' then
  begin
    AResultado.Mensagem := 'Nome da tabela e obrigatorio.';
    Exit;
  end;

  if ADados.ProximoCodigo < 0 then
  begin
    AResultado.Mensagem := 'Proximo codigo nao pode ser negativo.';
    Exit;
  end;

  DadosLimpos := ADados;
  DadosLimpos.GeoTabela := Trim(ADados.GeoTabela);
  if (UpperCase(Trim(ADados.TabelaAtiva)) = 'S') or (UpperCase(Trim(ADados.TabelaAtiva)) = 'TRUE') then
    DadosLimpos.TabelaAtiva := 'S'
  else
    DadosLimpos.TabelaAtiva := 'N';

  try
    if FRepository.SalvarConfigCod(DadosLimpos) then
    begin
      AResultado.Sucesso := True;
      AResultado.Mensagem := 'Configuracao de codigo gravada com sucesso!';
      Result := True;
    end
    else
    begin
      AResultado.Mensagem := 'Falha ao gravar configuracao no banco.';
    end;
  except
    on E: Exception do
      AResultado.Mensagem := 'Erro ao gravar configuracao: ' + E.Message;
  end;
end;

end.
