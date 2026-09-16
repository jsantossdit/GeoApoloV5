unit unt_validador_licenca;

{
  GeoApolo - TValidadorLicenca
  Implementa IValidadorLicenca.
  Responsabilidade: verificar se a licenca do periodo atual esta valida,
  usando a data obtida via NTP (quando disponivel) ou a data local.
}

interface

uses
  SysUtils,
  unt_logon_interfaces;

type

  TValidadorLicenca = class(TInterfacedObject, IValidadorLicenca)
  private
    FRepositorio    : IRepositorioLicenca;
    FServicoNTP     : IServicoNTP;      // pode ser nil => usa data local
    FHostNTP        : string;
    FPortaNTP       : Integer;
    const DIAS_TOLERANCIA_PADRAO = 15;

    function ObterDataAtual: TDateTime;
    function DiferencaDias(const ADataFinal: TDateTime;
                           const ADataAtual: TDateTime): Integer;
  public
    constructor Create(ARepositorio: IRepositorioLicenca;
                       AServicoNTP : IServicoNTP;
                       const AHostNTP: string;
                       APortaNTP: Integer);

    { IValidadorLicenca }
    function ValidarLicencaAtual(out AResultado: TResultadoLicenca;
      out AMensagem: string): Boolean;
  end;

implementation

uses
  DateUtils, Math;

{ TValidadorLicenca }

constructor TValidadorLicenca.Create(ARepositorio: IRepositorioLicenca;
  AServicoNTP: IServicoNTP; const AHostNTP: string; APortaNTP: Integer);
begin
  inherited Create;
  if not Assigned(ARepositorio) then
    raise EArgumentNilException.Create('TValidadorLicenca: repositorio nao pode ser nil');

  FRepositorio := ARepositorio;
  FServicoNTP  := AServicoNTP;
  FHostNTP     := AHostNTP;
  FPortaNTP    := APortaNTP;
end;

function TValidadorLicenca.ObterDataAtual: TDateTime;
var
  DataNTP: TDateTime;
begin
  if Assigned(FServicoNTP) and (FHostNTP <> '') then
  begin
    if FServicoNTP.ObterDataHora(FHostNTP, FPortaNTP, DataNTP) then
    begin
      Result := DataNTP;
      Exit;
    end;
  end;
  Result := Now;
end;

function TValidadorLicenca.DiferencaDias(const ADataFinal: TDateTime;
  const ADataAtual: TDateTime): Integer;
begin
  Result := DaysBetween(Trunc(ADataFinal), Trunc(ADataAtual));
end;

function TValidadorLicenca.ValidarLicencaAtual(out AResultado: TResultadoLicenca;
  out AMensagem: string): Boolean;
var
  Licenca    : TDadosLicenca;
  DataAtual  : TDateTime;
  Diferenca  : Integer;
begin
  Result    := True;
  AResultado := rlLicencaOk;
  AMensagem  := '';

  DataAtual := ObterDataAtual;

  if not FRepositorio.BuscarLicencaMesAtual(
           MonthOf(DataAtual), YearOf(DataAtual), Licenca) then
  begin
    AResultado := rlErroConsulta;
    AMensagem  := 'Nao foi possivel consultar a licenca do periodo.';
    Result     := False;
    Exit;
  end;

  { Licenca explicitamente bloqueada }
  if Licenca.Bloqueia then
  begin
    AResultado := rlLicencaBloqueada;
    AMensagem  := 'Licenca do sistema esta vencida. Solicite a chave de liberacao.';
    Result     := False;
    Exit;
  end;

  { Chave ainda nao ativada }
  if not Licenca.FlagAtivo then
  begin
    AResultado := rlChaveNaoAtivada;
    AMensagem  := 'A chave do periodo ainda nao foi ativada.';
    Result     := False;
    Exit;
  end;

  { Chave ativada — verifica se passou da data final }
  if (MonthOf(Licenca.DataFinal) = MonthOf(DataAtual)) and
     (YearOf(Licenca.DataFinal)  = YearOf(DataAtual)) then
  begin
    Diferenca := DiferencaDias(DataAtual, Licenca.DataFinal);

    if (Diferenca <= DIAS_TOLERANCIA_PADRAO) and not Licenca.Bloqueia then
    begin
      { Dentro da tolerancia: bloqueia no banco para proxima vez }
      FRepositorio.BloquearLicenca(Licenca.IDPalavra);
      AResultado := rlDentroToleranciaBloqueando;
      AMensagem  := 'Sua chave de ativacao esta proxima do vencimento (' +
                    IntToStr(Diferenca) + ' dias restantes).';
      { nao impede o acesso, apenas avisa }
    end;
  end;
end;

end.
