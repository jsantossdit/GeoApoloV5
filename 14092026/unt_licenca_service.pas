unit unt_licenca_service;

{
  GeoApolo - Serviço de Validação e Manutenção de Licenças
  Clean Architecture: Fachada para IValidadorLicenca e IRepositorioLicenca.
}

interface

uses
  System.SysUtils, System.Classes, FireDAC.Comp.Client,
  unt_logon_interfaces, unt_repositorio_licenca, unt_validador_licenca;

type

  TLicencaService = class
  private
    FConexao      : TFDConnection;
    FRepositorio  : IRepositorioLicenca;
    FValidador    : IValidadorLicenca;
    FServicoNTP   : IServicoNTP;
    FHostNTP      : string;
    FPortaNTP     : Integer;
  public
    constructor Create(AConexao: TFDConnection;
                       AServicoNTP: IServicoNTP = nil;
                       const AHostNTP: string = 'a.st1.ntp.br';
                       APortaNTP: Integer = 123);

    function ValidarLicenca(out AResultado: TResultadoLicenca;
      out AMensagem: string): Boolean;
    function ObterLicencaMes(AMes, AAno: Integer;
      out ALicenca: TDadosLicenca): Boolean;
    function BloquearLicenca(const AIDPalavra: string): Boolean;
  end;

implementation

{ TLicencaService }

constructor TLicencaService.Create(AConexao: TFDConnection;
  AServicoNTP: IServicoNTP; const AHostNTP: string; APortaNTP: Integer);
begin
  inherited Create;
  if not Assigned(AConexao) then
    raise EArgumentNilException.Create('TLicencaService: Conexao nao pode ser nula.');

  FConexao     := AConexao;
  FServicoNTP  := AServicoNTP;
  FHostNTP     := AHostNTP;
  FPortaNTP    := APortaNTP;

  FRepositorio := TRepositorioLicencaDB.Create(FConexao);
  FValidador   := TValidadorLicenca.Create(FRepositorio, FServicoNTP, FHostNTP, FPortaNTP);
end;

function TLicencaService.ValidarLicenca(out AResultado: TResultadoLicenca;
  out AMensagem: string): Boolean;
begin
  Result := FValidador.ValidarLicencaAtual(AResultado, AMensagem);
end;

function TLicencaService.ObterLicencaMes(AMes, AAno: Integer;
  out ALicenca: TDadosLicenca): Boolean;
begin
  Result := FRepositorio.BuscarLicencaMesAtual(AMes, AAno, ALicenca);
end;

function TLicencaService.BloquearLicenca(const AIDPalavra: string): Boolean;
begin
  Result := FRepositorio.BloquearLicenca(AIDPalavra);
end;

end.
