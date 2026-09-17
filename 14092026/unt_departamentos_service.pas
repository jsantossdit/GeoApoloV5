unit unt_departamentos_service;

{
  GeoApolo - Serviço de Regras de Negócio para Departamentos e Seções
  Clean Architecture: Validações de integridade, auto-numeração e vínculo contábil.
}

interface

uses
  System.SysUtils, System.Classes,
  unt_departamentos_types, unt_departamentos_repository;

type

  TDepartamentosService = class
  private
    FRepository: TDepartamentosRepository;
  public
    constructor Create(ARepository: TDepartamentosRepository);

    function ListarDepartamentos(const AEmpCod, AFiltro: string;
      out ALista: TArray<TDadosDepartamento>): Boolean;
    function ObterDepartamento(ACodigo: Integer;
      out ADados: TDadosDepartamento): Boolean;
    function ObterProximoCodigo: Integer;
    function SalvarDepartamento(var ADados: TDadosDepartamento;
      out AResultado: TResultadoDepartamento): Boolean;
    function ExcluirDepartamento(ACodigo: Integer;
      out AResultado: TResultadoDepartamento): Boolean;
  end;

implementation

{ TDepartamentosService }

constructor TDepartamentosService.Create(
  ARepository: TDepartamentosRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise EArgumentNilException.Create('TDepartamentosService: Repositorio nao pode ser nulo.');
  FRepository := ARepository;
end;

function TDepartamentosService.ObterProximoCodigo: Integer;
begin
  Result := FRepository.ObterProximoCodigo;
end;

function TDepartamentosService.ListarDepartamentos(const AEmpCod,
  AFiltro: string; out ALista: TArray<TDadosDepartamento>): Boolean;
begin
  Result := FRepository.ListarDepartamentos(Trim(AEmpCod), Trim(AFiltro), ALista);
end;

function TDepartamentosService.ObterDepartamento(ACodigo: Integer;
  out ADados: TDadosDepartamento): Boolean;
begin
  if ACodigo <= 0 then
  begin
    ADados := Default(TDadosDepartamento);
    Result := False;
    Exit;
  end;
  Result := FRepository.ObterDepartamento(ACodigo, ADados);
end;

function TDepartamentosService.SalvarDepartamento(
  var ADados: TDadosDepartamento;
  out AResultado: TResultadoDepartamento): Boolean;
var
  NomeLimpo, EmpLimpa: string;
begin
  Result := False;
  AResultado.Sucesso := False;
  AResultado.CodigoDepartamento := ADados.CodigoDepartamento;

  NomeLimpo := Trim(ADados.NomeDepartamento);
  if NomeLimpo = '' then
  begin
    AResultado.Mensagem := 'Nome do departamento e obrigatorio.';
    Exit;
  end;

  EmpLimpa := Trim(ADados.EmpCod);
  if EmpLimpa = '' then
  begin
    AResultado.Mensagem := 'Empresa associada ao departamento e obrigatoria.';
    Exit;
  end;

  if ADados.CodigoDepartamento <= 0 then
    ADados.CodigoDepartamento := FRepository.ObterProximoCodigo;

  ADados.NomeDepartamento := NomeLimpo;
  ADados.EmpCod := EmpLimpa;

  if (UpperCase(Trim(ADados.FlagAtivo)) = 'I') or (UpperCase(Trim(ADados.FlagAtivo)) = 'INATIVO') then
    ADados.FlagAtivo := 'I'
  else
    ADados.FlagAtivo := 'A';

  try
    if FRepository.SalvarDepartamento(ADados) then
    begin
      AResultado.Sucesso := True;
      AResultado.CodigoDepartamento := ADados.CodigoDepartamento;
      AResultado.Mensagem := 'Departamento ''' + NomeLimpo + ''' salvo com sucesso!';
      Result := True;
    end
    else
    begin
      AResultado.Mensagem := 'Falha ao gravar departamento no banco de dados.';
    end;
  except
    on E: Exception do
      AResultado.Mensagem := 'Erro ao salvar departamento: ' + E.Message;
  end;
end;

function TDepartamentosService.ExcluirDepartamento(ACodigo: Integer;
  out AResultado: TResultadoDepartamento): Boolean;
begin
  Result := False;
  AResultado.Sucesso := False;
  AResultado.CodigoDepartamento := ACodigo;

  if ACodigo <= 0 then
  begin
    AResultado.Mensagem := 'Codigo do departamento invalido para exclusao.';
    Exit;
  end;

  try
    if FRepository.ExcluirDepartamento(ACodigo) then
    begin
      AResultado.Sucesso := True;
      AResultado.Mensagem := 'Departamento excluido com sucesso.';
      Result := True;
    end
    else
    begin
      AResultado.Mensagem := 'Falha ao excluir departamento no banco.';
    end;
  except
    on E: Exception do
      AResultado.Mensagem := 'Erro ao excluir departamento: ' + E.Message;
  end;
end;

end.
