unit unt_cadcores_repository;

{
  Repositório FireDAC para Cores de Produtos (USER_geoapolo_produto_cores).
  Consultas parametrizadas e hints WITH (NOLOCK).
}

interface

uses
  System.SysUtils, System.Classes, Data.DB,
  FireDAC.Comp.Client, FireDAC.Stan.Param, FireDAC.Stan.Option,
  unt_cadcores_types;

type
  ICorRepository = interface
    ['{3C4D5E6F-7A8B-9C0D-1E2F-3A4B5C6D7E8F}']
    function ListarCores: TArray<TCorDTO>;
    function ObterCor(const ACodigo: Integer): TCorDTO;
    function ExisteDescricao(const ADescricao: string; const ACodigoIgnorar: Integer = 0): Boolean;
    function ObterProximoCodigo: Integer;
    function SalvarCor(const ACor: TCorDTO): Boolean;
    function ExcluirCor(const ACodigo: Integer): Boolean;
  end;

  TCorRepository = class(TInterfacedObject, ICorRepository)
  private
    FConn: TFDConnection;
  public
    constructor Create(AConn: TFDConnection);
    function ListarCores: TArray<TCorDTO>;
    function ObterCor(const ACodigo: Integer): TCorDTO;
    function ExisteDescricao(const ADescricao: string; const ACodigoIgnorar: Integer = 0): Boolean;
    function ObterProximoCodigo: Integer;
    function SalvarCor(const ACor: TCorDTO): Boolean;
    function ExcluirCor(const ACodigo: Integer): Boolean;
  end;

implementation

constructor TCorRepository.Create(AConn: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConn) then
    raise Exception.Create('TCorRepository: TFDConnection e obrigatoria.');
  FConn := AConn;
end;

function TCorRepository.ObterProximoCodigo: Integer;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT COALESCE(MAX(codigo_cor), 0) + 1 AS proximo FROM USER_geoapolo_produto_cores WITH (NOLOCK)';
    Qry.Open;
    Result := Qry.FieldByName('proximo').AsInteger;
  finally
    Qry.Free;
  end;
end;

function TCorRepository.ListarCores: TArray<TCorDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TCorDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT codigo_cor, descricao_cor FROM USER_geoapolo_produto_cores WITH (NOLOCK) ORDER BY codigo_cor ASC';
    Qry.Open;
    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].CodigoCor    := Qry.FieldByName('codigo_cor').AsInteger;
      Res[Idx].DescricaoCor := Qry.FieldByName('descricao_cor').AsString;
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
  Result := Res;
end;

function TCorRepository.ObterCor(const ACodigo: Integer): TCorDTO;
var
  Qry: TFDQuery;
begin
  FillChar(Result, SizeOf(Result), 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT codigo_cor, descricao_cor FROM USER_geoapolo_produto_cores WITH (NOLOCK) WHERE codigo_cor = :pCod';
    Qry.ParamByName('pCod').AsInteger := ACodigo;
    Qry.Open;
    if not Qry.Eof then
    begin
      Result.CodigoCor    := Qry.FieldByName('codigo_cor').AsInteger;
      Result.DescricaoCor := Qry.FieldByName('descricao_cor').AsString;
    end;
  finally
    Qry.Free;
  end;
end;

function TCorRepository.ExisteDescricao(const ADescricao: string; const ACodigoIgnorar: Integer): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT COUNT(1) AS qtd FROM USER_geoapolo_produto_cores WITH (NOLOCK) ' +
      'WHERE UPPER(RTRIM(LTRIM(descricao_cor))) = UPPER(RTRIM(LTRIM(:pDesc))) ' +
      '  AND codigo_cor <> :pCodIgnorar';
    Qry.ParamByName('pDesc').AsString := ADescricao;
    Qry.ParamByName('pCodIgnorar').AsInteger := ACodigoIgnorar;
    Qry.Open;
    Result := Qry.FieldByName('qtd').AsInteger > 0;
  finally
    Qry.Free;
  end;
end;

function TCorRepository.SalvarCor(const ACor: TCorDTO): Boolean;
var
  Qry: TFDQuery;
  Existe: Boolean;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT COUNT(1) AS qtd FROM USER_geoapolo_produto_cores WITH (NOLOCK) WHERE codigo_cor = :pCod';
    Qry.ParamByName('pCod').AsInteger := ACor.CodigoCor;
    Qry.Open;
    Existe := Qry.FieldByName('qtd').AsInteger > 0;
    Qry.Close;

    FConn.StartTransaction;
    try
      if Existe then
      begin
        Qry.SQL.Text := 'UPDATE USER_geoapolo_produto_cores SET descricao_cor = :pDesc WHERE codigo_cor = :pCod';
        Qry.ParamByName('pDesc').AsString := ACor.DescricaoCor;
        Qry.ParamByName('pCod').AsInteger := ACor.CodigoCor;
        Qry.ExecSQL;
      end
      else
      begin
        Qry.SQL.Text := 'INSERT INTO USER_geoapolo_produto_cores (codigo_cor, descricao_cor) VALUES (:pCod, :pDesc)';
        Qry.ParamByName('pCod').AsInteger := ACor.CodigoCor;
        Qry.ParamByName('pDesc').AsString := ACor.DescricaoCor;
        Qry.ExecSQL;
      end;
      FConn.Commit;
      Result := True;
    except
      FConn.Rollback;
      raise;
    end;
  finally
    Qry.Free;
  end;
end;

function TCorRepository.ExcluirCor(const ACodigo: Integer): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    FConn.StartTransaction;
    try
      Qry.SQL.Text := 'DELETE FROM USER_geoapolo_produto_cores WHERE codigo_cor = :pCod';
      Qry.ParamByName('pCod').AsInteger := ACodigo;
      Qry.ExecSQL;
      FConn.Commit;
      Result := True;
    except
      FConn.Rollback;
      raise;
    end;
  finally
    Qry.Free;
  end;
end;

end.
