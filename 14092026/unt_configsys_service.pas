unit unt_configsys_service;

{
  Camada de Serviços e Regras de Negócio para Parâmetros do Sistema.
  Normalização de diretórios, validação de integridade e isolamento de VCL.
}

interface

uses
  System.SysUtils, System.Classes, System.IOUtils,
  unt_configsys_types, unt_configsys_repository;

type
  TConfiguracoesService = class
  private
    FRepo: TConfiguracoesRepository;
  public
    constructor Create(ARepository: TConfiguracoesRepository);

    // Utilitários de Diretório
    class function NormalizarCaminho(const ACaminho: string): string; static;
    class function ValidarDiretorio(const ACaminho: string; const ACriarSeNaoExistir: Boolean = False): Boolean; static;

    // Regras de Negócio
    function ValidarConfiguracao(const AConfig: TConfiguracoesSistemaDTO; out AMsgErro: string): Boolean;
    function SalvarParametros(const AConfig: TConfiguracoesSistemaDTO): TOperacaoResultado;
    function ObterParametros(const AEmpresaCodigo: string): TConfiguracoesSistemaDTO;
  end;

implementation

constructor TConfiguracoesService.Create(ARepository: TConfiguracoesRepository);
begin
  inherited Create;
  FRepo := ARepository;
end;

class function TConfiguracoesService.NormalizarCaminho(const ACaminho: string): string;
var
  S: string;
begin
  S := Trim(ACaminho);
  // Substitui delimitadores legados do sistema ($ ou #) por barras invertidas padronizadas
  S := StringReplace(S, '$', '\', [rfReplaceAll]);
  S := StringReplace(S, '#', '-', [rfReplaceAll]);
  S := StringReplace(S, '/', '\', [rfReplaceAll]);

  if (S <> '') and (S[Length(S)] = '\') then
    Delete(S, Length(S), 1);

  Result := S;
end;

class function TConfiguracoesService.ValidarDiretorio(const ACaminho: string; const ACriarSeNaoExistir: Boolean = False): Boolean;
var
  CaminhoLimpo: string;
begin
  CaminhoLimpo := NormalizarCaminho(ACaminho);
  if CaminhoLimpo = '' then
    Exit(True); // Caminho vazio é aceito se não for obrigatório

  if DirectoryExists(CaminhoLimpo) then
    Exit(True);

  if ACriarSeNaoExistir then
  begin
    try
      ForceDirectories(CaminhoLimpo);
      Exit(DirectoryExists(CaminhoLimpo));
    except
      Exit(False);
    end;
  end;

  Result := False;
end;

function TConfiguracoesService.ValidarConfiguracao(const AConfig: TConfiguracoesSistemaDTO; out AMsgErro: string): Boolean;
begin
  AMsgErro := '';

  if Trim(AConfig.EmpresaCodigo) = '' then
  begin
    AMsgErro := 'O código da empresa é obrigatório para as configurações.';
    Exit(False);
  end;

  Result := True;
end;

function TConfiguracoesService.SalvarParametros(const AConfig: TConfiguracoesSistemaDTO): TOperacaoResultado;
var
  MsgErro: string;
  ConfigNormalizada: TConfiguracoesSistemaDTO;
begin
  if not ValidarConfiguracao(AConfig, MsgErro) then
  begin
    Result.Sucesso  := False;
    Result.Mensagem := MsgErro;
    Exit;
  end;

  ConfigNormalizada := AConfig;
  ConfigNormalizada.CaminhoBackupSistema    := NormalizarCaminho(AConfig.CaminhoBackupSistema);
  ConfigNormalizada.InstalacaoLocal         := NormalizarCaminho(AConfig.InstalacaoLocal);
  ConfigNormalizada.LocalNovasVersoes       := NormalizarCaminho(AConfig.LocalNovasVersoes);
  ConfigNormalizada.LocalInstaladorVersoes  := NormalizarCaminho(AConfig.LocalInstaladorVersoes);
  ConfigNormalizada.CaminhoArquivoConvenio  := NormalizarCaminho(AConfig.CaminhoArquivoConvenio);
  ConfigNormalizada.CaminhoInventario       := NormalizarCaminho(AConfig.CaminhoInventario);
  ConfigNormalizada.CaminhoDocTI            := NormalizarCaminho(AConfig.CaminhoDocTI);
  ConfigNormalizada.CaminhoDocMissaoPopular := NormalizarCaminho(AConfig.CaminhoDocMissaoPopular);
  ConfigNormalizada.CaminhoBaseAlvoLoja     := NormalizarCaminho(AConfig.CaminhoBaseAlvoLoja);

  Result := FRepo.SalvarConfiguracoes(ConfigNormalizada);
end;

function TConfiguracoesService.ObterParametros(const AEmpresaCodigo: string): TConfiguracoesSistemaDTO;
begin
  Result := FRepo.ObterConfiguracoes(AEmpresaCodigo);
end;

end.
