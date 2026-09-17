unit unt_configbanco_service;

{
  Serviço de Validação e Regras de Conexão de Bancos de Dados e Rede.
  Isolado de VCL e componentes visuais.
}

interface

uses
  System.SysUtils, System.Classes,
  unt_configbanco_types, unt_configbanco_repository;

type
  IConfigBancoService = interface
    ['{2B3C4D5E-6F7A-8B9C-0D1E-2F3A4B5C6D7E}']
    function CarregarConfiguracao(const ATipo: string = 'MSSQL'): TConfigBancoDTO;
    function SalvarConfiguracao(const AConfig: TConfigBancoDTO): TResultadoConfigBanco;
    function TestarConexao(const AConfig: TConfigBancoDTO): TResultadoTesteConexao;
    function ValidarParametros(const AConfig: TConfigBancoDTO): TResultadoConfigBanco;
  end;

  TConfigBancoService = class(TInterfacedObject, IConfigBancoService)
  private
    FRepo: IConfigBancoRepository;
  public
    constructor Create(ARepository: IConfigBancoRepository);
    function CarregarConfiguracao(const ATipo: string = 'MSSQL'): TConfigBancoDTO;
    function SalvarConfiguracao(const AConfig: TConfigBancoDTO): TResultadoConfigBanco;
    function TestarConexao(const AConfig: TConfigBancoDTO): TResultadoTesteConexao;
    function ValidarParametros(const AConfig: TConfigBancoDTO): TResultadoConfigBanco;
  end;

implementation

constructor TConfigBancoService.Create(ARepository: IConfigBancoRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise Exception.Create('TConfigBancoService: Repositorio e obrigatorio.');
  FRepo := ARepository;
end;

function TConfigBancoService.CarregarConfiguracao(const ATipo: string): TConfigBancoDTO;
begin
  Result := FRepo.CarregarConfiguracao(ATipo);
end;

function TConfigBancoService.ValidarParametros(const AConfig: TConfigBancoDTO): TResultadoConfigBanco;
begin
  Result.Sucesso  := False;
  Result.Mensagem := '';

  if Trim(AConfig.Servidor) = '' then
  begin
    Result.Mensagem := 'Nome ou IP do servidor e obrigatorio.';
    Exit;
  end;

  if Trim(AConfig.NomeBanco) = '' then
  begin
    Result.Mensagem := 'Nome da base de dados e obrigatorio.';
    Exit;
  end;

  if (AConfig.Porta < 1) or (AConfig.Porta > 65535) then
  begin
    Result.Mensagem := 'Porta TCP invalida (deve estar entre 1 e 65535).';
    Exit;
  end;

  if Trim(AConfig.Usuario) = '' then
  begin
    Result.Mensagem := 'Usuario de autenticacao e obrigatorio.';
    Exit;
  end;

  Result.Sucesso  := True;
  Result.Mensagem := 'Parametros validos.';
end;

function TConfigBancoService.SalvarConfiguracao(const AConfig: TConfigBancoDTO): TResultadoConfigBanco;
begin
  Result := ValidarParametros(AConfig);
  if not Result.Sucesso then
    Exit;

  try
    if FRepo.SalvarConfiguracao(AConfig) then
    begin
      Result.Sucesso  := True;
      Result.Mensagem := 'Configuracoes gravadas com sucesso no Registro.';
    end
    else
    begin
      Result.Sucesso  := False;
      Result.Mensagem := 'Falha ao gravar configuracoes no Registro.';
    end;
  except
    on E: Exception do
    begin
      Result.Sucesso  := False;
      Result.Mensagem := 'Erro ao salvar configuracoes: ' + E.Message;
    end;
  end;
end;

function TConfigBancoService.TestarConexao(const AConfig: TConfigBancoDTO): TResultadoTesteConexao;
var
  Val: TResultadoConfigBanco;
begin
  Val := ValidarParametros(AConfig);
  if not Val.Sucesso then
  begin
    Result.Sucesso := False;
    Result.Mensagem := Val.Mensagem;
    Result.TempoRespostaMs := 0;
    Exit;
  end;

  Result := FRepo.TestarConexao(AConfig);
end;

end.
