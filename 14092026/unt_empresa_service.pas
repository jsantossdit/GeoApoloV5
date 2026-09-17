unit unt_empresa_service;

interface

uses
  System.SysUtils, System.Classes, unt_empresa_types, unt_empresa_repository;

type
  IEmpresaService = interface
    ['{6B7D9E0A-2C3D-4E5F-8A9B-1C2D3E4F5A6B}']
    function ListarEmpresas: TArray<TEmpresaDTO>;
    function ObterEmpresa(const AEmpCod: string): TEmpresaDTO;
    function SalvarEmpresa(const AEmpresa: TEmpresaDTO): TResultadoEmpresa;
    function ExcluirEmpresa(const AEmpCod: string): TResultadoEmpresa;
    function SincronizarEmpresasApolo: TResultadoEmpresa;
  end;

  TEmpresaService = class(TInterfacedObject, IEmpresaService)
  private
    FRepo: IEmpresaRepository;
  public
    constructor Create(ARepository: IEmpresaRepository);
    function ListarEmpresas: TArray<TEmpresaDTO>;
    function ObterEmpresa(const AEmpCod: string): TEmpresaDTO;
    function SalvarEmpresa(const AEmpresa: TEmpresaDTO): TResultadoEmpresa;
    function ExcluirEmpresa(const AEmpCod: string): TResultadoEmpresa;
    function SincronizarEmpresasApolo: TResultadoEmpresa;
  end;

implementation

constructor TEmpresaService.Create(ARepository: IEmpresaRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise Exception.Create('TEmpresaService: Repositório é obrigatório.');
  FRepo := ARepository;
end;

function TEmpresaService.ListarEmpresas: TArray<TEmpresaDTO>;
begin
  Result := FRepo.ListarEmpresas;
end;

function TEmpresaService.ObterEmpresa(const AEmpCod: string): TEmpresaDTO;
begin
  if Trim(AEmpCod) = '' then
    raise Exception.Create('Código da empresa é obrigatório.');
  Result := FRepo.ObterEmpresa(Trim(AEmpCod));
end;

function TEmpresaService.SalvarEmpresa(const AEmpresa: TEmpresaDTO): TResultadoEmpresa;
begin
  Result.Sucesso := False;
  Result.Mensagem := '';

  if Trim(AEmpresa.EmpCod) = '' then
  begin
    Result.Mensagem := 'O código da empresa é obrigatório.';
    Exit;
  end;

  if Trim(AEmpresa.EmpNome) = '' then
  begin
    Result.Mensagem := 'A razão social/nome da empresa não pode estar vazia.';
    Exit;
  end;

  try
    if FRepo.SalvarEmpresa(AEmpresa) then
    begin
      Result.Sucesso := True;
      Result.Mensagem := 'Empresa salva com sucesso.';
    end
    else
      Result.Mensagem := 'Falha ao salvar dados da empresa.';
  except
    on E: Exception do
      Result.Mensagem := 'Erro ao salvar empresa: ' + E.Message;
  end;
end;

function TEmpresaService.ExcluirEmpresa(const AEmpCod: string): TResultadoEmpresa;
begin
  Result.Sucesso := False;
  Result.Mensagem := '';

  if Trim(AEmpCod) = '' then
  begin
    Result.Mensagem := 'Código da empresa deve ser fornecido.';
    Exit;
  end;

  try
    if FRepo.ExcluirEmpresa(Trim(AEmpCod)) then
    begin
      Result.Sucesso := True;
      Result.Mensagem := 'Empresa excluída com sucesso.';
    end
    else
      Result.Mensagem := 'Falha ao excluir empresa.';
  except
    on E: Exception do
      Result.Mensagem := 'Erro ao excluir empresa: ' + E.Message;
  end;
end;

function TEmpresaService.SincronizarEmpresasApolo: TResultadoEmpresa;
var
  Qtd: Integer;
begin
  Result.Sucesso := False;
  Result.Mensagem := '';
  try
    Qtd := FRepo.SincronizarEmpresasApolo;
    Result.Sucesso := True;
    Result.Mensagem := Format('Sincronização concluída: %d nova(s) empresa(s) importada(s).', [Qtd]);
  except
    on E: Exception do
      Result.Mensagem := 'Erro na sincronização de empresas: ' + E.Message;
  end;
end;

end.
