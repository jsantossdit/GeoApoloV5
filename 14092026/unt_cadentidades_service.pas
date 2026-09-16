unit unt_cadentidades_service;

interface

uses
  System.SysUtils, System.Classes, unt_cadentidades_types, unt_cadentidades_repository;

type
  TResultadoValidacao = record
    Valido  : Boolean;
    Mensagem: string;
    Campo   : string;
  end;

  TCadastroEntidadeService = class
  private
    FRepo: ICadastroEntidadeRepository;
  public
    constructor Create(ARepository: ICadastroEntidadeRepository);

    function ValidarDados(const ADados: TEntidadeCompletaDTO): TResultadoValidacao;
    function SalvarEntidade(const ADados: TEntidadeCompletaDTO): TResultadoValidacao;
    function FormatarDataISO(const ADataBR: string): string;
  end;

implementation

constructor TCadastroEntidadeService.Create(ARepository: ICadastroEntidadeRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise Exception.Create('TCadastroEntidadeService: Repositório é obrigatório.');
  FRepo := ARepository;
end;

function TCadastroEntidadeService.FormatarDataISO(const ADataBR: string): string;
var
  DataLimpa: string;
begin
  DataLimpa := StringReplace(ADataBR, '/', '', [rfReplaceAll]);
  DataLimpa := StringReplace(DataLimpa, '-', '', [rfReplaceAll]);
  DataLimpa := Trim(DataLimpa);
  if (DataLimpa = '') or (DataLimpa = '01011970') then
    Exit('');

  try
    Result := FormatDateTime('yyyy-mm-dd', StrToDate(ADataBR));
  except
    Result := '';
  end;
end;

function TCadastroEntidadeService.ValidarDados(const ADados: TEntidadeCompletaDTO): TResultadoValidacao;
begin
  Result.Valido := False;
  Result.Campo := '';

  if Trim(ADados.Pessoais.Codigo) = '' then
  begin
    Result.Mensagem := 'O Código da Entidade é obrigatório.';
    Result.Campo := 'Codigo';
    Exit;
  end;

  if Trim(ADados.Pessoais.Nome) = '' then
  begin
    Result.Mensagem := 'O Nome da Entidade é obrigatório.';
    Result.Campo := 'Nome';
    Exit;
  end;

  if Trim(ADados.Endereco.Endereco) = '' then
  begin
    Result.Mensagem := 'O Endereço é obrigatório.';
    Result.Campo := 'Endereco';
    Exit;
  end;

  if Trim(ADados.Endereco.Numero) = '' then
  begin
    Result.Mensagem := 'O Número do Endereço é obrigatório.';
    Result.Campo := 'Numero';
    Exit;
  end;

  if Trim(ADados.Endereco.CEP) = '' then
  begin
    Result.Mensagem := 'O CEP é obrigatório.';
    Result.Campo := 'CEP';
    Exit;
  end;

  if Trim(ADados.Endereco.CodigoCidade) = '' then
  begin
    Result.Mensagem := 'A Cidade é obrigatória.';
    Result.Campo := 'Cidade';
    Exit;
  end;

  Result.Valido := True;
  Result.Mensagem := 'Validação concluída com sucesso.';
end;

function TCadastroEntidadeService.SalvarEntidade(const ADados: TEntidadeCompletaDTO): TResultadoValidacao;
begin
  Result := ValidarDados(ADados);
  if not Result.Valido then
    Exit;

  try
    if ADados.BaseDestino = bdGeoApolo then
      FRepo.GravarGeoApolo(ADados)
    else
      FRepo.GravarAlvo(ADados);

    Result.Valido := True;
    Result.Mensagem := 'Entidade salva com sucesso!';
  except
    on E: Exception do
    begin
      Result.Valido := False;
      Result.Mensagem := 'Erro ao persistir entidade no banco: ' + E.Message;
    end;
  end;
end;

end.
