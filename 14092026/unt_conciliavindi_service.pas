unit unt_conciliavindi_service;

{
  GeoApolo - Serviço de Regras de Negócio e Integridade para Conciliação Vindi
  Clean Architecture: Validações de integridade desacopladas da tela.
}

interface

uses
  System.SysUtils, System.Classes, unt_conciliavindi_types, unt_conciliavindi_repository;

type

  TConciliaVindiService = class
  private
    FRepository: TConciliaVindiRepository;
    procedure AdicionarErro(var AResult: TIntegridadeVindiResult; const AMensagem: string);
    function  RemoverFormatacaoCpfCnpj(const AValor: string): string;
  public
    constructor Create(ARepository: TConciliaVindiRepository);

    function ChecarIntegridade(const APedidoId: string): TIntegridadeVindiResult;
    function ListarTransacoes(const ADataIni, ADataFim: TDateTime;
      out ALista: TArray<TDadosTransacaoVindi>): Boolean;
  end;

implementation

{ TConciliaVindiService }

constructor TConciliaVindiService.Create(ARepository: TConciliaVindiRepository);
begin
  inherited Create;
  if not Assigned(ARepository) then
    raise EArgumentNilException.Create('TConciliaVindiService: Repositorio nao pode ser nulo.');
  FRepository := ARepository;
end;

procedure TConciliaVindiService.AdicionarErro(
  var AResult: TIntegridadeVindiResult; const AMensagem: string);
var
  L: Integer;
begin
  L := Length(AResult.Erros);
  SetLength(AResult.Erros, L + 1);
  AResult.Erros[L] := AMensagem;
end;

function TConciliaVindiService.RemoverFormatacaoCpfCnpj(
  const AValor: string): string;
var
  C: Char;
begin
  Result := '';
  for C in AValor do
  begin
    if CharInSet(C, ['0'..'9']) then
      Result := Result + C;
  end;
end;

function TConciliaVindiService.ChecarIntegridade(
  const APedidoId: string): TIntegridadeVindiResult;
var
  ValorOrig: Double;
  EntIdVindi: string;
  CpfVindi: string;
  CpfLimpo: string;
  StatusVindi: string;
  EntCodApolo, EntNomeApolo: string;
  TotalCategorias: Integer;
begin
  Result.PedidoId := Trim(APedidoId);
  SetLength(Result.Erros, 0);

  if Result.PedidoId = '' then
  begin
    AdicionarErro(Result, 'Identificador do pedido Vindi nao informado.');
    Exit;
  end;

  // 1. Verifica existência da transação
  if not FRepository.BuscaValorOriginal(Result.PedidoId, ValorOrig) then
  begin
    AdicionarErro(Result, 'Transacao nao encontrada na tabela USER_VINDITRANSACOES.');
    Exit;
  end;

  // 2. Busca entidade vinculada na Vindi
  if not FRepository.BuscaEntidadeIdVindi(Result.PedidoId, EntIdVindi) or (Trim(EntIdVindi) = '') then
  begin
    AdicionarErro(Result, 'Pedido nao possui Entidade Vindi associada.');
    Exit;
  end;

  // 3. Busca CPF/CNPJ do cliente na Vindi
  if not FRepository.BuscaCpfPorEntidadeVindi(EntIdVindi, CpfVindi) or (Trim(CpfVindi) = '') then
  begin
    AdicionarErro(Result, 'Cliente Vindi nao possui CPF/CNPJ preenchido.');
    Exit;
  end;

  // 4. Checa status da entidade na Vindi
  if FRepository.BuscaStatusEntidadeVindi(EntIdVindi, StatusVindi) then
  begin
    if UpperCase(Trim(StatusVindi)) = 'INACTIVE' then
      AdicionarErro(Result, 'Cliente esta com status INATIVO na plataforma Vindi.');
  end;

  // 5. Cruzamento com cadastro de entidades do ERP Apolo
  CpfLimpo := RemoverFormatacaoCpfCnpj(CpfVindi);
  if not FRepository.BuscaDadosEntidadeApolo(CpfLimpo, EntCodApolo, EntNomeApolo, TotalCategorias) then
  begin
    AdicionarErro(Result, Format('Entidade com CPF/CNPJ %s nao localizada no banco do ERP Apolo.', [CpfVindi]));
    Exit;
  end;

  // 6. Checa consistência de categorias
  if TotalCategorias = 0 then
    AdicionarErro(Result, Format('Entidade %s (%s) nao possui categoria cadastrada no Apolo.', [EntNomeApolo, EntCodApolo]))
  else if TotalCategorias > 1 then
    AdicionarErro(Result, Format('Entidade %s (%s) possui duplicidade de categorias (%d encontradas).',
      [EntNomeApolo, EntCodApolo, TotalCategorias]));
end;

function TConciliaVindiService.ListarTransacoes(const ADataIni,
  ADataFim: TDateTime; out ALista: TArray<TDadosTransacaoVindi>): Boolean;
begin
  Result := FRepository.ListarTransacoesPeriodo(ADataIni, ADataFim, ALista);
end;

end.
