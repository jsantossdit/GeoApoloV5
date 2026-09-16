unit unt_debxcredctafin_service;

interface

uses
  System.SysUtils, System.Classes, System.Variants,
  FireDAC.Comp.Client, FireDAC.Stan.Param,  Data.DB;
type
  TRegistroMovimento = record
    Data       : TDate;
    Debito     : Currency;
    Credito    : Currency;
    Diferenca  : Currency;
  end;
  TResultadoMovimento = record
    Registros     : TArray<TRegistroMovimento>;
    TotalDebito   : Currency;
    TotalCredito  : Currency;
    Saldo         : Currency;
  end;
  TContaFinanceiraItem = record
    Codigo : string;
    Nome   : string;
  end;
  // Array de contas — sem problema de ownership de TFDQuery
  TListaContasFinanceiras = TArray<TContaFinanceiraItem>;
  IDebXCredService = interface
    ['{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}']
    function BuscarNomeContaFinanceira(const ACodigo: string): string;
    function ListarContasFinanceiras(const ACodGrupoUsuario: string): TListaContasFinanceiras;
    function BuscarGrupoUsuario(const ALoginUsuario: string): string;
    function ConsultarMovimentos(const AContaCod: string;
      ADataInicial, ADataFinal: TDate): TResultadoMovimento;
  end;
  TDebXCredService = class(TInterfacedObject, IDebXCredService)
  private
    FConexao: TFDConnection;
    function ExecutarQueryScalar(const ASQL: string;
      const AParams: array of Variant): Variant;
    function ExecutarQueryDebito(const AContaCod: string; AData: TDate): Currency;
    function ExecutarQueryCredito(const AContaCod: string; AData: TDate): Currency;
  public
    constructor Create(AConexao: TFDConnection);
    function BuscarNomeContaFinanceira(const ACodigo: string): string;
    function ListarContasFinanceiras(const ACodGrupoUsuario: string): TListaContasFinanceiras;
    function BuscarGrupoUsuario(const ALoginUsuario: string): string;
    function ConsultarMovimentos(const AContaCod: string;
      ADataInicial, ADataFinal: TDate): TResultadoMovimento;
  end;
implementation
{ TDebXCredService }

uses unt_dados;

constructor TDebXCredService.Create(AConexao: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConexao) then
    raise EArgumentNilException.Create('Conexão FireDAC não pode ser nula.');
  FConexao := AConexao;
end;

function TDebXCredService.ExecutarQueryScalar(const ASQL: string; const AParams: array of Variant): Variant;
var
  LQuery : TFDQuery;
  i      : Integer;
begin
  Result := Null;
  LQuery := TFDQuery.Create(nil);
  try
    LQuery.Connection := FConexao;
    LQuery.SQL.Text   := ASQL;
    for i := 0 to High(AParams) do
      LQuery.Params[i].Value := AParams[i];
    LQuery.Open;
    if not LQuery.IsEmpty then
      Result := LQuery.Fields[0].Value;
  finally
    LQuery.Free;
  end;
end;

function TDebXCredService.BuscarGrupoUsuario(const ALoginUsuario: string): string;
const
  SQL_GRUPO =
    'SELECT GrpUsuCod FROM grp_x_usuario WHERE usucod = :pUsuario';
var
  Valor: Variant;
begin
  Valor := ExecutarQueryScalar(SQL_GRUPO, [ALoginUsuario]);
  if VarIsNull(Valor) or VarIsEmpty(Valor) then
    Result := ''
  else
    Result := VarToStr(Valor);
end;

function TDebXCredService.BuscarNomeContaFinanceira(const ACodigo: string): string;
const
  SQL_NOME =
    'SELECT contafinnome FROM conta_fin WITH (NOLOCK) WHERE contafincod = :pCodigo';
var
  Valor: Variant;
begin
  Valor := ExecutarQueryScalar(SQL_NOME, [ACodigo]);
  if VarIsNull(Valor) or VarIsEmpty(Valor) then
    Result := ''
  else
    Result := VarToStr(Valor);
end;

function TDebXCredService.ListarContasFinanceiras(const ACodGrupoUsuario: string): TListaContasFinanceiras;
const
  SQL_CONTAS =
    'SELECT DISTINCT cf.contafincod, cf.contafinnome ' +
    'FROM conta_fin cf WITH (NOLOCK) ' +
    'INNER JOIN usuario_conta_fin ucf WITH (NOLOCK) ON cf.contafincod = ucf.contafincod ' +
    'INNER JOIN grp_x_usuario gu WITH (NOLOCK) ON ucf.usucod = gu.usucod ' +
    'WHERE gu.GrpUsuCod = :pGrupo ' +
    'ORDER BY cf.contafincod';
var
  LQuery : TFDQuery;
  LIdx   : Integer;
begin
  SetLength(Result, 0);
  LQuery := TFDQuery.Create(nil);
  try
    LQuery.Connection := FConexao;
    LQuery.SQL.Text   := SQL_CONTAS;
    LQuery.ParamByName('pGrupo').AsString := ACodGrupoUsuario;
    LQuery.Open;  // Se falhar aqui, o finally garante o Free sem AV
    LIdx := 0;
    while not LQuery.Eof do
    begin
      SetLength(Result, LIdx + 1);
      Result[LIdx].Codigo := LQuery.FieldByName('contafincod').AsString;
      Result[LIdx].Nome   := LQuery.FieldByName('contafinnome').AsString;
      Inc(LIdx);
      LQuery.Next;
    end;
  finally
    LQuery.Free;  // Sempre destruído aqui — nunca vaza para fora
  end;
end;

function TDebXCredService.ExecutarQueryDebito(const AContaCod: string;
  AData: TDate): Currency;
const
  SQL_DEBITO =
    'SELECT COALESCE(SUM(l.lancmovctrlbancval), 0) AS valordebito ' +
    'FROM lanc_mov_ctrl_banc l WITH (NOLOCK) ' +
    'INNER JOIN tipo_lanc tl WITH (NOLOCK) ON l.tipolanccod = tl.tipolanccod ' +
    'WHERE tl.tipolancoper = :pOper ' +
    'AND l.contafincod = :pConta ' +
    'AND l.lancmovctrlbancdataconc = :pData';
var
  LQuery: TFDQuery;
begin
  Result := 0;
  LQuery := TFDQuery.Create(nil);
  try
    LQuery.Connection := modulo_dados.fdbanco;
    LQuery.SQL.Text   := SQL_DEBITO;
    LQuery.ParamByName('pOper').AsString  := 'Débito';
    LQuery.ParamByName('pConta').AsString := AContaCod;
    LQuery.ParamByName('pData').AsDate    := AData;
    LQuery.Open;
    if not LQuery.IsEmpty then
      Result := LQuery.FieldByName('valordebito').AsCurrency;
  finally
    LQuery.Free;
  end;
end;
function TDebXCredService.ExecutarQueryCredito(const AContaCod: string;
  AData: TDate): Currency;
const
  SQL_CREDITO =
    'SELECT COALESCE(SUM(l.lancmovctrlbancval), 0) AS valorcredito ' +
    'FROM lanc_mov_ctrl_banc l WITH (NOLOCK) ' +
    'INNER JOIN tipo_lanc tl WITH (NOLOCK) ON l.tipolanccod = tl.tipolanccod ' +
    'WHERE tl.tipolancoper = :pOper ' +
    'AND l.contafincod = :pConta ' +
    'AND l.lancmovctrlbancdataconc = :pData';
var
  LQuery: TFDQuery;
begin
  Result := 0;
  LQuery := TFDQuery.Create(nil);
  try
    LQuery.Connection := modulo_dados.fdbanco;
    LQuery.SQL.Text   := SQL_CREDITO;
    LQuery.ParamByName('pOper').AsString  := 'Crédito';
    LQuery.ParamByName('pConta').AsString := AContaCod;
    LQuery.ParamByName('pData').AsDate    := AData;
    LQuery.Open;
    if not LQuery.IsEmpty then
      Result := LQuery.FieldByName('valorcredito').AsCurrency;
  finally
    LQuery.Free;
  end;
end;
function TDebXCredService.ConsultarMovimentos(const AContaCod: string;
  ADataInicial, ADataFinal: TDate): TResultadoMovimento;
var
  LData    : TDate;
  LReg     : TRegistroMovimento;
  LDebito  : Currency;
  LCredito : Currency;
  LIdx     : Integer;
begin
  Result.TotalDebito  := 0;
  Result.TotalCredito := 0;
  Result.Saldo        := 0;
  SetLength(Result.Registros, 0);
  LData := ADataInicial;
  LIdx  := 0;
  while LData <= ADataFinal do
  begin
    LDebito  := ExecutarQueryDebito(AContaCod, LData);
    LCredito := ExecutarQueryCredito(AContaCod, LData);
    LReg.Data      := LData;
    LReg.Debito    := LDebito;
    LReg.Credito   := LCredito;
    if (LDebito = 0) and (LCredito = 0) then
      LReg.Diferenca := 0
    else
      LReg.Diferenca := LDebito - LCredito;
    SetLength(Result.Registros, LIdx + 1);
    Result.Registros[LIdx] := LReg;
    Result.TotalDebito  := Result.TotalDebito  + LDebito;
    Result.TotalCredito := Result.TotalCredito + LCredito;
    LData := LData + 1;
    Inc(LIdx);
  end;
  Result.Saldo := Result.TotalDebito - Result.TotalCredito;
end;
end.
