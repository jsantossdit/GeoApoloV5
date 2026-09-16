unit ConsultaService;

interface

uses
  System.SysUtils,
  System.Classes,
  // Adicione aqui as unidades onde estão TConsultaRepository, TConsultaModel e EConsultaValidation
  ConsultaModel, ConsultaRepository;

type
  // Declaração de uma exceção personalizada (caso não esteja em outra unit)
  EConsultaValidation = class(Exception);

  TConsultaService = class
  private
    FRepository: TConsultaRepository;
    procedure ValidarSQL(ASQL: string);
    procedure ValidarConsulta(AConsulta: TConsultaModel);
  public
    constructor Create(ARepository: TConsultaRepository);
    function BuscarPorCodigo(ACodigo: Integer): TConsultaModel;
    procedure Salvar(AConsulta: TConsultaModel; ANovaConsulta: Boolean);
    procedure Excluir(ACodigo: Integer);
  end;

implementation

{ TConsultaService }

constructor TConsultaService.Create(ARepository: TConsultaRepository);
begin
  FRepository := ARepository;
end;

procedure TConsultaService.ValidarSQL(ASQL: string);
var
  Prefixo: string;
begin
  // Aumentei para 10 para garantir o "DECLARE" e "DELETE"
  Prefixo := UpperCase(Trim(ASQL));

  if not (
    Prefixo.StartsWith('SELECT') or
    Prefixo.StartsWith('INSERT') or
    Prefixo.StartsWith('UPDATE') or
    Prefixo.StartsWith('DELETE') or
    Prefixo.StartsWith('DECLARE') or
    Prefixo.StartsWith('CREATE')
  ) then
    raise EConsultaValidation.Create(
      'O conteúdo informado não é uma sentença SQL válida.'
    );
end;

procedure TConsultaService.ValidarConsulta(AConsulta: TConsultaModel);
begin
  if Trim(AConsulta.Descricao) = '' then
    raise EConsultaValidation.Create('Descrição da consulta é obrigatória.');

  if Trim(AConsulta.BancoConsulta) = '' then
    raise EConsultaValidation.Create('Banco da consulta é obrigatório.');

  if Trim(AConsulta.SentencaSQL) = '' then
    raise EConsultaValidation.Create('Sentença SQL é obrigatória.');

  ValidarSQL(AConsulta.SentencaSQL);
end;

function TConsultaService.BuscarPorCodigo(ACodigo: Integer): TConsultaModel;
begin
  Result := FRepository.BuscarPorCodigo(ACodigo);
end;

procedure TConsultaService.Salvar(AConsulta: TConsultaModel; ANovaConsulta: Boolean);
begin
  ValidarConsulta(AConsulta);

  if ANovaConsulta then
    FRepository.Inserir(AConsulta)
  else
    FRepository.Atualizar(AConsulta);
end;

procedure TConsultaService.Excluir(ACodigo: Integer);
begin
  if ACodigo <= 0 then
    raise EConsultaValidation.Create('Código inválido para exclusão.');

  FRepository.Excluir(ACodigo);
end;

end.
