unit unt_desligafunc_service;

interface

uses
  System.SysUtils, System.Classes, System.Generics.Collections,
  unt_desligafunc_types, unt_desligafunc_repository;

type
  TDesligaFuncService = class
  private
    FRepository: IDesligaFuncRepository;
    procedure ValidarUsuario(const AUsuCod: string);
  public
    constructor Create(ARepository: IDesligaFuncRepository);
    function ObterUsuariosPorStatus(const AStatus: string): TList<TUsuarioDesligamentoDTO>;
    function Pesquisar(const ACampo, AValor, AStatus: string): TList<TUsuarioDesligamentoDTO>;
    function ObterDetalhesUsuario(const AUsuCod: string; out AUsuario: TUsuarioDesligamentoDTO): Boolean;
    function Desligar(const AUsuCod: string): TResultadoDesligamentoDTO;
    function Reativar(const AUsuCod: string): Boolean;
  end;

implementation

{ TDesligaFuncService }

constructor TDesligaFuncService.Create(ARepository: IDesligaFuncRepository);
begin
  inherited Create;
  if ARepository = nil then
    raise EArgumentNilException.Create('Repositório não pode ser nulo.');
  FRepository := ARepository;
end;

procedure TDesligaFuncService.ValidarUsuario(const AUsuCod: string);
begin
  if Trim(AUsuCod) = '' then
    raise EArgumentException.Create('Selecione um usuário válido.');
end;

function TDesligaFuncService.ObterUsuariosPorStatus(const AStatus: string): TList<TUsuarioDesligamentoDTO>;
begin
  Result := FRepository.ListarUsuariosPorStatus(AStatus);
end;

function TDesligaFuncService.Pesquisar(const ACampo, AValor, AStatus: string): TList<TUsuarioDesligamentoDTO>;
begin
  Result := FRepository.PesquisarUsuarios(ACampo, AValor, AStatus);
end;

function TDesligaFuncService.ObterDetalhesUsuario(const AUsuCod: string; out AUsuario: TUsuarioDesligamentoDTO): Boolean;
begin
  ValidarUsuario(AUsuCod);
  Result := FRepository.ObterUsuario(AUsuCod, AUsuario);
end;

function TDesligaFuncService.Desligar(const AUsuCod: string): TResultadoDesligamentoDTO;
begin
  try
    ValidarUsuario(AUsuCod);
    Result := FRepository.ExecutarDesligamento(AUsuCod);
  except
    on E: Exception do
      Result := TResultadoDesligamentoDTO.CriarFalha(E.Message);
  end;
end;

function TDesligaFuncService.Reativar(const AUsuCod: string): Boolean;
begin
  ValidarUsuario(AUsuCod);
  Result := FRepository.ReativarUsuario(AUsuCod);
end;

end.
