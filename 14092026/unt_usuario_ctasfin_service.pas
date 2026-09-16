unit unt_usuario_ctasfin_service;

interface

uses
  System.SysUtils, System.Classes, System.Generics.Collections,
  unt_usuario_ctasfin_types, unt_usuario_ctasfin_repository;

type
  /// <summary>
  /// Camada de serviço pura (sem VCL) com regras de negócio de permissões financeiras.
  /// </summary>
  TUsuarioCtasFinService = class
  private
    FRepository: IUsuarioCtasFinRepository;
    procedure ValidarUsuario(const AUsuCod: string);
  public
    constructor Create(ARepository: IUsuarioCtasFinRepository);
    function ObterUsuariosAtivos: TList<string>;
    function ObterContasDisponiveis: TList<TContaFinanceiraDTO>;
    function ObterContasDoUsuario(const AUsuCod: string): TList<TContaFinanceiraDTO>;
    function SalvarPermissoes(const AUsuCod: string; const AContas: TArray<string>): TResultadoOperacaoContasFin;
    function RevogarTodas(const AUsuCod: string): TResultadoOperacaoContasFin;
    class function ExtrairCodigoConta(const ATextoFormatado: string): string; static;
  end;

implementation

{ TUsuarioCtasFinService }

constructor TUsuarioCtasFinService.Create(ARepository: IUsuarioCtasFinRepository);
begin
  inherited Create;
  if ARepository = nil then
    raise EArgumentNilException.Create('Repositório não pode ser nulo.');
  FRepository := ARepository;
end;

procedure TUsuarioCtasFinService.ValidarUsuario(const AUsuCod: string);
begin
  if Trim(AUsuCod) = '' then
    raise EArgumentException.Create('Informe um usuário válido para realizar a operação.');
end;

function TUsuarioCtasFinService.ObterUsuariosAtivos: TList<string>;
begin
  Result := FRepository.ListarUsuariosAtivos;
end;

function TUsuarioCtasFinService.ObterContasDisponiveis: TList<TContaFinanceiraDTO>;
begin
  Result := FRepository.ListarContasDisponiveis;
end;

function TUsuarioCtasFinService.ObterContasDoUsuario(const AUsuCod: string): TList<TContaFinanceiraDTO>;
begin
  ValidarUsuario(AUsuCod);
  Result := FRepository.ListarContasPorUsuario(AUsuCod);
end;

function TUsuarioCtasFinService.SalvarPermissoes(const AUsuCod: string; const AContas: TArray<string>): TResultadoOperacaoContasFin;
begin
  try
    ValidarUsuario(AUsuCod);
    Result := FRepository.SalvarPermissoesUsuario(AUsuCod, AContas);
  except
    on E: Exception do
      Result := TResultadoOperacaoContasFin.CriarFalha(E.Message);
  end;
end;

function TUsuarioCtasFinService.RevogarTodas(const AUsuCod: string): TResultadoOperacaoContasFin;
begin
  try
    ValidarUsuario(AUsuCod);
    Result := FRepository.RevogarTodasPermissoes(AUsuCod);
  except
    on E: Exception do
      Result := TResultadoOperacaoContasFin.CriarFalha(E.Message);
  end;
end;

class function TUsuarioCtasFinService.ExtrairCodigoConta(const ATextoFormatado: string): string;
var
  PosSeta: Integer;
begin
  // Extrai com segurança qualquer formato "CODIGO -> NOME"
  PosSeta := Pos('->', ATextoFormatado);
  if PosSeta > 0 then
    Result := Trim(Copy(ATextoFormatado, 1, PosSeta - 1))
  else
    Result := Trim(ATextoFormatado);
end;

end.
