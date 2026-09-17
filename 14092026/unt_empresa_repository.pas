unit unt_empresa_repository;

interface

uses
  System.SysUtils, System.Classes, Data.DB, FireDAC.Comp.Client,
  FireDAC.Stan.Param, FireDAC.Stan.Option, unt_empresa_types;

type
  IEmpresaRepository = interface
    ['{4C5E8A9B-1A2B-4C3D-8E9F-0A1B2C3D4E5F}']
    function ListarEmpresas: TArray<TEmpresaDTO>;
    function ObterEmpresa(const AEmpCod: string): TEmpresaDTO;
    function SalvarEmpresa(const AEmpresa: TEmpresaDTO): Boolean;
    function ExcluirEmpresa(const AEmpCod: string): Boolean;
    function SincronizarEmpresasApolo: Integer;
  end;

  TEmpresaRepository = class(TInterfacedObject, IEmpresaRepository)
  private
    FConn: TFDConnection;
  public
    constructor Create(AConnection: TFDConnection);
    function ListarEmpresas: TArray<TEmpresaDTO>;
    function ObterEmpresa(const AEmpCod: string): TEmpresaDTO;
    function SalvarEmpresa(const AEmpresa: TEmpresaDTO): Boolean;
    function ExcluirEmpresa(const AEmpCod: string): Boolean;
    function SincronizarEmpresasApolo: Integer;
  end;

implementation

constructor TEmpresaRepository.Create(AConnection: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConnection) then
    raise Exception.Create('TEmpresaRepository: TFDConnection é obrigatória.');
  FConn := AConnection;
end;

function TEmpresaRepository.ListarEmpresas: TArray<TEmpresaDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TEmpresaDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT empcod, empnome FROM USER_geoapolo_empresas WITH (NOLOCK) ORDER BY empcod ASC';
    Qry.Open;
    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].EmpCod  := Qry.FieldByName('empcod').AsString;
      Res[Idx].EmpNome := Qry.FieldByName('empnome').AsString;
      Res[Idx].Ativa   := True;
      Qry.Next;
    end;
    Result := Res;
  finally
    Qry.Free;
  end;
end;

function TEmpresaRepository.ObterEmpresa(const AEmpCod: string): TEmpresaDTO;
var
  Qry: TFDQuery;
begin
  FillChar(Result, SizeOf(Result), 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT empcod, empnome FROM USER_geoapolo_empresas WITH (NOLOCK) WHERE empcod = :pEmpCod';
    Qry.ParamByName('pEmpCod').AsString := AEmpCod;
    Qry.Open;
    if not Qry.IsEmpty then
    begin
      Result.EmpCod  := Qry.FieldByName('empcod').AsString;
      Result.EmpNome := Qry.FieldByName('empnome').AsString;
      Result.Ativa   := True;
    end;
  finally
    Qry.Free;
  end;
end;

function TEmpresaRepository.SalvarEmpresa(const AEmpresa: TEmpresaDTO): Boolean;
var
  Qry: TFDQuery;
  Existe: Boolean;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT COUNT(*) FROM USER_geoapolo_empresas WHERE empcod = :pEmpCod';
    Qry.ParamByName('pEmpCod').AsString := AEmpresa.EmpCod;
    Qry.Open;
    Existe := Qry.Fields[0].AsInteger > 0;
    Qry.Close;

    if Existe then
    begin
      Qry.SQL.Text := 'UPDATE USER_geoapolo_empresas SET empnome = :pEmpNome WHERE empcod = :pEmpCod';
    end
    else
    begin
      Qry.SQL.Text := 'INSERT INTO USER_geoapolo_empresas (empcod, empnome) VALUES (:pEmpCod, :pEmpNome)';
    end;
    Qry.ParamByName('pEmpCod').AsString  := AEmpresa.EmpCod;
    Qry.ParamByName('pEmpNome').AsString := AEmpresa.EmpNome;
    Qry.ExecSQL;
    Result := True;
  finally
    Qry.Free;
  end;
end;

function TEmpresaRepository.ExcluirEmpresa(const AEmpCod: string): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'DELETE FROM USER_geoapolo_empresas WHERE empcod = :pEmpCod';
    Qry.ParamByName('pEmpCod').AsString := AEmpCod;
    Qry.ExecSQL;
    Result := True;
  finally
    Qry.Free;
  end;
end;

function TEmpresaRepository.SincronizarEmpresasApolo: Integer;
var
  Qry: TFDQuery;
begin
  Result := 0;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'INSERT INTO USER_geoapolo_empresas (empcod, empnome) ' +
      'SELECT f.empcod, f.empnome FROM empresa_filial f WITH (NOLOCK) ' +
      'WHERE NOT EXISTS (SELECT 1 FROM USER_geoapolo_empresas g WHERE g.empcod = f.empcod)';
    Qry.ExecSQL;
    Result := Qry.RowsAffected;
  finally
    Qry.Free;
  end;
end;

end.
