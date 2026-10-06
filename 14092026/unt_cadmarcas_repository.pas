unit unt_cadmarcas_repository;

{
  Repositório FireDAC para Marcas de Produtos (USER_geoapolo_produto_marcas).
  Consultas parametrizadas e hints WITH (NOLOCK).
}

interface

uses
  System.SysUtils, System.Classes, Data.DB,
  FireDAC.Comp.Client, FireDAC.Stan.Param, FireDAC.Stan.Option,
  unt_cadmarcas_types;

type
  IMarcaRepository = interface
    ['{4B5C6D7E-8F9A-0B1C-2D3E-4F5A6B7C8D9E}']
    function ListarMarcas: TArray<TMarcaDTO>;
    function ObterMarca(const ACodigo: Integer): TMarcaDTO;
    function ExisteDescricao(const ADescricao: string; const ACodigoIgnorar: Integer = 0): Boolean;
    function ObterProximoCodigo: Integer;
    function SalvarMarca(const AMarca: TMarcaDTO): Boolean;
    function ExcluirMarca(const ACodigo: Integer): Boolean;
  end;

  TMarcaRepository = class(TInterfacedObject, IMarcaRepository)
  private
    FConn: TFDConnection;
  public
    constructor Create(AConn: TFDConnection);
    function ListarMarcas: TArray<TMarcaDTO>;
    function ObterMarca(const ACodigo: Integer): TMarcaDTO;
    function ExisteDescricao(const ADescricao: string; const ACodigoIgnorar: Integer = 0): Boolean;
    function ObterProximoCodigo: Integer;
    function SalvarMarca(const AMarca: TMarcaDTO): Boolean;
    function ExcluirMarca(const ACodigo: Integer): Boolean;
  end;

implementation

constructor TMarcaRepository.Create(AConn: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConn) then
    raise Exception.Create('TMarcaRepository: TFDConnection e obrigatoria.');
  FConn := AConn;
end;

function TMarcaRepository.ObterProximoCodigo: Integer;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT COALESCE(MAX(codigo_marca), 0) + 1 AS proximo FROM USER_geoapolo_produto_marcas WITH (NOLOCK)';
    Qry.Open;
    Result := Qry.FieldByName('proximo').AsInteger;
  finally
    Qry.Free;
  end;
end;

function TMarcaRepository.ListarMarcas: TArray<TMarcaDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TMarcaDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT codigo_marca, descricao_marca FROM USER_geoapolo_produto_marcas WITH (NOLOCK) ORDER BY codigo_marca ASC';
    Qry.Open;
    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].CodigoMarca    := Qry.FieldByName('codigo_marca').AsInteger;
      Res[Idx].DescricaoMarca := Qry.FieldByName('descricao_marca').AsString;
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
  Result := Res;
end;

function TMarcaRepository.ObterMarca(const ACodigo: Integer): TMarcaDTO;
var
  Qry: TFDQuery;
begin
  FillChar(Result, SizeOf(Result), 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT codigo_marca, descricao_marca FROM USER_geoapolo_produto_marcas WITH (NOLOCK) WHERE codigo_marca = :pCod';
    Qry.ParamByName('pCod').AsInteger := ACodigo;
    Qry.Open;
    if not Qry.Eof then
    begin
      Result.CodigoMarca    := Qry.FieldByName('codigo_marca').AsInteger;
      Result.DescricaoMarca := Qry.FieldByName('descricao_marca').AsString;
    end;
  finally
    Qry.Free;
  end;
end;

function TMarcaRepository.ExisteDescricao(const ADescricao: string; const ACodigoIgnorar: Integer): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT COUNT(1) AS qtd FROM USER_geoapolo_produto_marcas WITH (NOLOCK) ' +
      'WHERE UPPER(RTRIM(LTRIM(descricao_marca))) = UPPER(RTRIM(LTRIM(:pDesc))) ' +
      '  AND codigo_marca <> :pCodIgnorar';
    Qry.ParamByName('pDesc').AsString := ADescricao;
    Qry.ParamByName('pCodIgnorar').AsInteger := ACodigoIgnorar;
    Qry.Open;
    Result := Qry.FieldByName('qtd').AsInteger > 0;
  finally
    Qry.Free;
  end;
end;

function TMarcaRepository.SalvarMarca(const AMarca: TMarcaDTO): Boolean;
var
  Qry: TFDQuery;
  Existe: Boolean;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT COUNT(1) AS qtd FROM USER_geoapolo_produto_marcas WITH (NOLOCK) WHERE codigo_marca = :pCod';
    Qry.ParamByName('pCod').AsInteger := AMarca.CodigoMarca;
    Qry.Open;
    Existe := Qry.FieldByName('qtd').AsInteger > 0;
    Qry.Close;

    FConn.StartTransaction;
    try
      if Existe then
      begin
        Qry.SQL.Text := 'UPDATE USER_geoapolo_produto_marcas SET descricao_marca = :pDesc WHERE codigo_marca = :pCod';
        Qry.ParamByName('pDesc').AsString := AMarca.DescricaoMarca;
        Qry.ParamByName('pCod').AsInteger := AMarca.CodigoMarca;
        Qry.ExecSQL;
      end
      else
      begin
        Qry.SQL.Text := 'INSERT INTO USER_geoapolo_produto_marcas (codigo_marca, descricao_marca) VALUES (:pCod, :pDesc)';
        Qry.ParamByName('pCod').AsInteger := AMarca.CodigoMarca;
        Qry.ParamByName('pDesc').AsString := AMarca.DescricaoMarca;
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

function TMarcaRepository.ExcluirMarca(const ACodigo: Integer): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    FConn.StartTransaction;
    try
      Qry.SQL.Text := 'DELETE FROM USER_geoapolo_produto_marcas WHERE codigo_marca = :pCod';
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
