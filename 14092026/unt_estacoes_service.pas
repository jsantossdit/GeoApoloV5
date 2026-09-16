unit unt_estacoes_service;

{
  Camada de Regras de Negócio e Serviços para o Módulo de Estações de Trabalho.
  Totalmente desacoplada de formulários e componentes VCL.
}

interface

uses
  System.SysUtils, System.Classes, System.DateUtils, System.RegularExpressions,
  unt_estacoes_types, unt_estacoes_repository;

type
  TEstacoesService = class
  private
    FRepo: TEstacoesRepository;
  public
    constructor Create(ARepository: TEstacoesRepository);

    // Validações
    function ValidarEstacao(const AEstacao: TEstacaoDTO; out AMsgErro: string): Boolean;
    function ValidarHardware(const AHardware: THardwareDTO; out AMsgErro: string): Boolean;
    function ValidarSoftware(const ASoftware: TSoftwareDTO; out AMsgErro: string): Boolean;
    function ValidarEnderecoIP(const AIP: string): Boolean;

    // Regras de Garantia e Status
    function CalcularDiasGarantiaRestante(const ADataCompra: TDateTime; const ATempoGarantiaDias: Integer): Integer;
    function ObterDescricaoGarantia(const ADataCompra: TDateTime; const ATempoGarantiaDias: Integer): string;

    // Orquestração de Persistência
    function SalvarEstacao(const AEstacao: TEstacaoDTO; const AModoInclusao: Boolean): TOperacaoResultado;
    function SalvarHardware(const AHardware: THardwareDTO; const AModoInclusao: Boolean): TOperacaoResultado;
    function SalvarSoftware(const ASoftware: TSoftwareDTO; const AModoInclusao: Boolean): TOperacaoResultado;
    function ExcluirEstacao(const ACodigo: string): TOperacaoResultado;
  end;

implementation

constructor TEstacoesService.Create(ARepository: TEstacoesRepository);
begin
  inherited Create;
  FRepo := ARepository;
end;

function TEstacoesService.ValidarEnderecoIP(const AIP: string): Boolean;
var
  RegEx: TRegEx;
begin
  if Trim(AIP) = '' then
    Exit(True); // IP é opcional, mas se informado deve ser válido

  RegEx := TRegEx.Create('^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$');
  Result := RegEx.IsMatch(Trim(AIP));
end;

function TEstacoesService.ValidarEstacao(const AEstacao: TEstacaoDTO; out AMsgErro: string): Boolean;
begin
  AMsgErro := '';

  if Trim(AEstacao.CodigoEstacao) = '' then
  begin
    AMsgErro := 'O código da estação é obrigatório.';
    Exit(False);
  end;

  if Trim(AEstacao.Descricao) = '' then
  begin
    AMsgErro := 'A descrição da estação é obrigatória.';
    Exit(False);
  end;

  if (Trim(AEstacao.EnderecoIP) <> '') and (not ValidarEnderecoIP(AEstacao.EnderecoIP)) then
  begin
    AMsgErro := 'O endereço IP informado (' + AEstacao.EnderecoIP + ') possui formato inválido.';
    Exit(False);
  end;

  Result := True;
end;

function TEstacoesService.ValidarHardware(const AHardware: THardwareDTO; out AMsgErro: string): Boolean;
begin
  AMsgErro := '';

  if Trim(AHardware.CodigoHardware) = '' then
  begin
    AMsgErro := 'O código do hardware é obrigatório.';
    Exit(False);
  end;

  if Trim(AHardware.Descricao) = '' then
  begin
    AMsgErro := 'A descrição do hardware é obrigatória.';
    Exit(False);
  end;

  if Trim(AHardware.CodigoEstacao) = '' then
  begin
    AMsgErro := 'O hardware deve estar vinculado a uma estação de trabalho.';
    Exit(False);
  end;

  if AHardware.Valor < 0 then
  begin
    AMsgErro := 'O valor do hardware não pode ser negativo.';
    Exit(False);
  end;

  if (Trim(AHardware.EnderecoIP) <> '') and (not ValidarEnderecoIP(AHardware.EnderecoIP)) then
  begin
    AMsgErro := 'O IP do hardware possui formato inválido.';
    Exit(False);
  end;

  Result := True;
end;

function TEstacoesService.ValidarSoftware(const ASoftware: TSoftwareDTO; out AMsgErro: string): Boolean;
begin
  AMsgErro := '';

  if Trim(ASoftware.CodigoSoftware) = '' then
  begin
    AMsgErro := 'O código do software é obrigatório.';
    Exit(False);
  end;

  if Trim(ASoftware.Descricao) = '' then
  begin
    AMsgErro := 'A descrição do software é obrigatória.';
    Exit(False);
  end;

  if Trim(ASoftware.CodigoEstacao) = '' then
  begin
    AMsgErro := 'O software deve estar vinculado a uma estação de trabalho.';
    Exit(False);
  end;

  if (ASoftware.DataCompra > 0) and (ASoftware.DataVencimento > 0) and (ASoftware.DataVencimento < ASoftware.DataCompra) then
  begin
    AMsgErro := 'A data de vencimento da licença não pode ser anterior à data de aquisição.';
    Exit(False);
  end;

  Result := True;
end;

function TEstacoesService.CalcularDiasGarantiaRestante(const ADataCompra: TDateTime; const ATempoGarantiaDias: Integer): Integer;
var
  DataLimite: TDateTime;
  Dias: Integer;
begin
  if (ADataCompra <= 0) or (ATempoGarantiaDias <= 0) then
    Exit(0);

  DataLimite := IncDay(ADataCompra, ATempoGarantiaDias);
  Dias := DaysBetween(DataLimite, Date);

  if Date > DataLimite then
    Result := -Dias // Garantia expirada há X dias
  else
    Result := Dias;  // Restam X dias
end;

function TEstacoesService.ObterDescricaoGarantia(const ADataCompra: TDateTime; const ATempoGarantiaDias: Integer): string;
var
  Dias: Integer;
begin
  if (ADataCompra <= 0) or (ATempoGarantiaDias <= 0) then
    Exit('Sem garantia informada');

  Dias := CalcularDiasGarantiaRestante(ADataCompra, ATempoGarantiaDias);
  if Dias < 0 then
    Result := Format('Garantia EXPIRADA há %d dias', [Abs(Dias)])
  else if Dias = 0 then
    Result := 'Garantia EXPIRA HOJE'
  else
    Result := Format('Em garantia (%d dias restantes)', [Dias]);
end;

function TEstacoesService.SalvarEstacao(const AEstacao: TEstacaoDTO; const AModoInclusao: Boolean): TOperacaoResultado;
var
  MsgErro: string;
begin
  if not ValidarEstacao(AEstacao, MsgErro) then
  begin
    Result.Sucesso := False;
    Result.Mensagem := MsgErro;
    Exit;
  end;

  if AModoInclusao then
    Result := FRepo.InserirEstacao(AEstacao)
  else
    Result := FRepo.AtualizarEstacao(AEstacao);
end;

function TEstacoesService.SalvarHardware(const AHardware: THardwareDTO; const AModoInclusao: Boolean): TOperacaoResultado;
var
  MsgErro: string;
begin
  if not ValidarHardware(AHardware, MsgErro) then
  begin
    Result.Sucesso := False;
    Result.Mensagem := MsgErro;
    Exit;
  end;

  if AModoInclusao then
    Result := FRepo.InserirHardware(AHardware)
  else
    Result := FRepo.AtualizarHardware(AHardware);
end;

function TEstacoesService.SalvarSoftware(const ASoftware: TSoftwareDTO; const AModoInclusao: Boolean): TOperacaoResultado;
var
  MsgErro: string;
begin
  if not ValidarSoftware(ASoftware, MsgErro) then
  begin
    Result.Sucesso := False;
    Result.Mensagem := MsgErro;
    Exit;
  end;

  if AModoInclusao then
    Result := FRepo.InserirSoftware(ASoftware)
  else
    Result := FRepo.AtualizarSoftware(ASoftware);
end;

function TEstacoesService.ExcluirEstacao(const ACodigo: string): TOperacaoResultado;
begin
  if Trim(ACodigo) = '' then
  begin
    Result.Sucesso := False;
    Result.Mensagem := 'Código de estação não informado.';
    Exit;
  end;

  Result := FRepo.ExcluirEstacao(ACodigo);
end;

end.
