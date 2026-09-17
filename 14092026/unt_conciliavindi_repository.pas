unit unt_conciliavindi_repository;

{
  GeoApolo - Repositório de Acesso a Dados para Conciliação Vindi
  Clean Architecture: Acesso desacoplado com queries parametrizadas e WITH (NOLOCK).
}

interface

uses
  System.SysUtils, System.Classes, FireDAC.Comp.Client, FireDAC.DApt, Data.DB,
  unt_conciliavindi_types;

type

  TConciliaVindiRepository = class
  private
    FConexao: TFDConnection;
    function CriarQuery: TFDQuery;
  public
    constructor Create(AConexao: TFDConnection);

    function BuscaValorOriginal(const APedidoId: string; out AValor: Double): Boolean;
    function BuscaEntidadeIdVindi(const APedidoId: string; out AEntidadeId: string): Boolean;
    function BuscaCpfPorEntidadeVindi(const AEntidadeId: string; out ACpfCnpj: string): Boolean;
    function BuscaStatusEntidadeVindi(const AEntidadeId: string; out AStatus: string): Boolean;
    function BuscaDadosEntidadeApolo(const ACpfCnpjLimpo: string;
      out AEntCod, AEntNome: string; out ATotalCategorias: Integer): Boolean;
    function ListarTransacoesPeriodo(const ADataIni, ADataFim: TDateTime;
      out ALista: TArray<TDadosTransacaoVindi>): Boolean;
  end;

implementation

{ TConciliaVindiRepository }

constructor TConciliaVindiRepository.Create(AConexao: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConexao) then
    raise EArgumentNilException.Create('TConciliaVindiRepository: Conexao nao pode ser nula.');
  FConexao := AConexao;
end;

function TConciliaVindiRepository.CriarQuery: TFDQuery;
begin
  Result := TFDQuery.Create(nil);
  Result.Connection := FConexao;
end;

function TConciliaVindiRepository.BuscaValorOriginal(const APedidoId: string;
  out AValor: Double): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  AValor := 0.0;
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT valor FROM USER_VINDITRANSACOES WITH (NOLOCK) ' +
      'WHERE pedido_id = :pedidoid';
    Q.ParamByName('pedidoid').AsString := Trim(APedidoId);
    Q.Open;
    if not Q.IsEmpty then
    begin
      AValor := Q.FieldByName('valor').AsFloat;
      Result := True;
    end;
  finally
    Q.Free;
  end;
end;

function TConciliaVindiRepository.BuscaEntidadeIdVindi(const APedidoId: string;
  out AEntidadeId: string): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  AEntidadeId := '';
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT entidade_id FROM USER_VINDITRANSACOES WITH (NOLOCK) ' +
      'WHERE pedido_id = :pedidoid';
    Q.ParamByName('pedidoid').AsString := Trim(APedidoId);
    Q.Open;
    if not Q.IsEmpty then
    begin
      AEntidadeId := Q.FieldByName('entidade_id').AsString;
      Result := True;
    end;
  finally
    Q.Free;
  end;
end;

function TConciliaVindiRepository.BuscaCpfPorEntidadeVindi(
  const AEntidadeId: string; out ACpfCnpj: string): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  ACpfCnpj := '';
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT cpf_cnpj FROM USERVINDI_ENTIDADE WITH (NOLOCK) ' +
      'WHERE entidade_id = :entidadeid';
    Q.ParamByName('entidadeid').AsString := Trim(AEntidadeId);
    Q.Open;
    if not Q.IsEmpty then
    begin
      ACpfCnpj := Q.FieldByName('cpf_cnpj').AsString;
      Result := True;
    end;
  finally
    Q.Free;
  end;
end;

function TConciliaVindiRepository.BuscaStatusEntidadeVindi(
  const AEntidadeId: string; out AStatus: string): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  AStatus := '';
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT status FROM USERVINDI_ENTIDADE WITH (NOLOCK) ' +
      'WHERE entidade_id = :entidadeid';
    Q.ParamByName('entidadeid').AsString := Trim(AEntidadeId);
    Q.Open;
    if not Q.IsEmpty then
    begin
      AStatus := Q.FieldByName('status').AsString;
      Result := True;
    end;
  finally
    Q.Free;
  end;
end;

function TConciliaVindiRepository.BuscaDadosEntidadeApolo(
  const ACpfCnpjLimpo: string; out AEntCod, AEntNome: string;
  out ATotalCategorias: Integer): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  AEntCod := '';
  AEntNome := '';
  ATotalCategorias := 0;
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT e.entcod, e.entnome, COUNT(ec.categcod) AS total_categ ' +
      'FROM ENTIDADE e WITH (NOLOCK) ' +
      'LEFT JOIN ENT_CATEG ec WITH (NOLOCK) ON e.entcod = ec.entcod ' +
      'WHERE REPLACE(REPLACE(REPLACE(e.entcpf_cgc, ''.'', ''''), ''-'', ''''), ''/'', '''') = :cpf ' +
      'GROUP BY e.entcod, e.entnome';
    Q.ParamByName('cpf').AsString := Trim(ACpfCnpjLimpo);
    Q.Open;
    if not Q.IsEmpty then
    begin
      AEntCod          := Q.FieldByName('entcod').AsString;
      AEntNome         := Q.FieldByName('entnome').AsString;
      ATotalCategorias := Q.FieldByName('total_categ').AsInteger;
      Result := True;
    end;
  finally
    Q.Free;
  end;
end;

function TConciliaVindiRepository.ListarTransacoesPeriodo(const ADataIni,
  ADataFim: TDateTime; out ALista: TArray<TDadosTransacaoVindi>): Boolean;
var
  Q: TFDQuery;
  Idx: Integer;
begin
  Result := False;
  SetLength(ALista, 0);
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT pedido_id, data_transacao, valor, status, ' +
      '       COALESCE(metodo_pagamento, '''') AS metodo_pagamento, ' +
      '       COALESCE(cliente_nome, '''') AS cliente_nome, ' +
      '       COALESCE(cliente_cpf_cnpj, '''') AS cliente_cpf_cnpj, ' +
      '       COALESCE(entidade_id, '''') AS entidade_id ' +
      'FROM USER_VINDITRANSACOES WITH (NOLOCK) ' +
      'WHERE data_transacao BETWEEN :dtini AND :dtfim ' +
      'ORDER BY data_transacao DESC';
    Q.ParamByName('dtini').AsDateTime := ADataIni;
    Q.ParamByName('dtfim').AsDateTime := ADataFim;
    Q.Open;

    SetLength(ALista, Q.RecordCount);
    Idx := 0;
    while not Q.Eof do
    begin
      ALista[Idx].PedidoId        := Q.FieldByName('pedido_id').AsString;
      ALista[Idx].DataTransacao   := Q.FieldByName('data_transacao').AsDateTime;
      ALista[Idx].Valor           := Q.FieldByName('valor').AsFloat;
      ALista[Idx].Status          := Q.FieldByName('status').AsString;
      ALista[Idx].MetodoPagamento := Q.FieldByName('metodo_pagamento').AsString;
      ALista[Idx].ClienteNome     := Q.FieldByName('cliente_nome').AsString;
      ALista[Idx].ClienteCpfCnpj  := Q.FieldByName('cliente_cpf_cnpj').AsString;
      ALista[Idx].EntidadeIdVindi := Q.FieldByName('entidade_id').AsString;
      Inc(Idx);
      Q.Next;
    end;
    Result := True;
  finally
    Q.Free;
  end;
end;

end.
