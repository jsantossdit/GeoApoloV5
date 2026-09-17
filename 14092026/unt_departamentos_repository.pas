unit unt_departamentos_repository;

{
  GeoApolo - Repositório de Persistência de Departamentos e Seções
  Clean Architecture: Acesso desacoplado com queries parametrizadas e WITH (NOLOCK).
}

interface

uses
  System.SysUtils, System.Classes, FireDAC.Comp.Client, FireDAC.DApt, Data.DB,
  unt_departamentos_types;

type

  TDepartamentosRepository = class
  private
    FConexao: TFDConnection;
    function CriarQuery: TFDQuery;
  public
    constructor Create(AConexao: TFDConnection);

    function ListarDepartamentos(const AEmpCod, AFiltro: string;
      out ALista: TArray<TDadosDepartamento>): Boolean;
    function ObterDepartamento(ACodigo: Integer;
      out ADados: TDadosDepartamento): Boolean;
    function ObterProximoCodigo: Integer;
    function SalvarDepartamento(const ADados: TDadosDepartamento): Boolean;
    function ExcluirDepartamento(ACodigo: Integer): Boolean;
    function VincularCentroControle(ACodigo: Integer; const ACCtrlCodEstr: string): Boolean;
    function RemoverVinculoCentroControle(ACodigo: Integer): Boolean;
  end;

implementation

{ TDepartamentosRepository }

constructor TDepartamentosRepository.Create(AConexao: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConexao) then
    raise EArgumentNilException.Create('TDepartamentosRepository: Conexao nao pode ser nula.');
  FConexao := AConexao;
end;

function TDepartamentosRepository.CriarQuery: TFDQuery;
begin
  Result := TFDQuery.Create(nil);
  Result.Connection := FConexao;
end;

function TDepartamentosRepository.ObterProximoCodigo: Integer;
var
  Q: TFDQuery;
begin
  Result := 1;
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT COALESCE(MAX(codigo_departamento), 0) + 1 AS proximo ' +
      'FROM USER_geoapolo_departamentos WITH (NOLOCK)';
    Q.Open;
    if not Q.IsEmpty then
      Result := Q.FieldByName('proximo').AsInteger;
  finally
    Q.Free;
  end;
end;

function TDepartamentosRepository.ListarDepartamentos(const AEmpCod,
  AFiltro: string; out ALista: TArray<TDadosDepartamento>): Boolean;
var
  Q: TFDQuery;
  Idx: Integer;
  SqlText: string;
  HasEmp, HasFiltro: Boolean;
begin
  Result := False;
  SetLength(ALista, 0);
  Q := CriarQuery;
  try
    HasEmp := Trim(AEmpCod) <> '';
    HasFiltro := Trim(AFiltro) <> '';

    SqlText :=
      'SELECT d.codigo_departamento, d.nome_departamento, d.empcod, ' +
      '       COALESCE(e.empnome, '''') AS empnome, COALESCE(d.flagativo, ''A'') AS flagativo, ' +
      '       COALESCE(v.cctrlcodestr, '''') AS cctrlcodestr, ' +
      '       COALESCE(cc.cctrlnome, '''') AS cctrlnome ' +
      'FROM USER_geoapolo_departamentos d WITH (NOLOCK) ' +
      'LEFT JOIN USER_geoapolo_empresas e WITH (NOLOCK) ON d.empcod = e.empcod ' +
      'LEFT JOIN geoapolo_secoescctrlapolo v WITH (NOLOCK) ON d.codigo_departamento = v.codigo_secao ' +
      'LEFT JOIN centro_ctrl cc WITH (NOLOCK) ON v.cctrlcodestr = cc.cctrlcodestr ' +
      'WHERE 1=1 ';

    if HasEmp then
      SqlText := SqlText + 'AND d.empcod = :empcod ';

    if HasFiltro then
      SqlText := SqlText + 'AND UPPER(d.nome_departamento) LIKE UPPER(:filtro) ';

    SqlText := SqlText + 'ORDER BY d.codigo_departamento ASC';

    Q.SQL.Text := SqlText;

    if HasEmp then
      Q.ParamByName('empcod').AsString := Trim(AEmpCod);

    if HasFiltro then
      Q.ParamByName('filtro').AsString := '%' + Trim(AFiltro) + '%';

    Q.Open;
    SetLength(ALista, Q.RecordCount);
    Idx := 0;
    while not Q.Eof do
    begin
      ALista[Idx].CodigoDepartamento := Q.FieldByName('codigo_departamento').AsInteger;
      ALista[Idx].NomeDepartamento   := Q.FieldByName('nome_departamento').AsString;
      ALista[Idx].EmpCod             := Q.FieldByName('empcod').AsString;
      ALista[Idx].EmpNome            := Q.FieldByName('empnome').AsString;
      ALista[Idx].FlagAtivo          := Q.FieldByName('flagativo').AsString;
      ALista[Idx].CCtrlCodEstr       := Q.FieldByName('cctrlcodestr').AsString;
      ALista[Idx].CCtrlNome          := Q.FieldByName('cctrlnome').AsString;
      Inc(Idx);
      Q.Next;
    end;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TDepartamentosRepository.ObterDepartamento(ACodigo: Integer;
  out ADados: TDadosDepartamento): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  ADados := Default(TDadosDepartamento);
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT d.codigo_departamento, d.nome_departamento, d.empcod, ' +
      '       COALESCE(e.empnome, '''') AS empnome, COALESCE(d.flagativo, ''A'') AS flagativo, ' +
      '       COALESCE(v.cctrlcodestr, '''') AS cctrlcodestr, ' +
      '       COALESCE(cc.cctrlnome, '''') AS cctrlnome ' +
      'FROM USER_geoapolo_departamentos d WITH (NOLOCK) ' +
      'LEFT JOIN USER_geoapolo_empresas e WITH (NOLOCK) ON d.empcod = e.empcod ' +
      'LEFT JOIN geoapolo_secoescctrlapolo v WITH (NOLOCK) ON d.codigo_departamento = v.codigo_secao ' +
      'LEFT JOIN centro_ctrl cc WITH (NOLOCK) ON v.cctrlcodestr = cc.cctrlcodestr ' +
      'WHERE d.codigo_departamento = :codigo';
    Q.ParamByName('codigo').AsInteger := ACodigo;
    Q.Open;

    if not Q.IsEmpty then
    begin
      ADados.CodigoDepartamento := Q.FieldByName('codigo_departamento').AsInteger;
      ADados.NomeDepartamento   := Q.FieldByName('nome_departamento').AsString;
      ADados.EmpCod             := Q.FieldByName('empcod').AsString;
      ADados.EmpNome            := Q.FieldByName('empnome').AsString;
      ADados.FlagAtivo          := Q.FieldByName('flagativo').AsString;
      ADados.CCtrlCodEstr       := Q.FieldByName('cctrlcodestr').AsString;
      ADados.CCtrlNome          := Q.FieldByName('cctrlnome').AsString;
      Result := True;
    end;
  finally
    Q.Free;
  end;
end;

function TDepartamentosRepository.SalvarDepartamento(
  const ADados: TDadosDepartamento): Boolean;
var
  Q: TFDQuery;
  Existe: Boolean;
begin
  Result := False;
  Q := CriarQuery;
  try
    Q.SQL.Text := 'SELECT 1 FROM USER_geoapolo_departamentos WHERE codigo_departamento = :codigo';
    Q.ParamByName('codigo').AsInteger := ADados.CodigoDepartamento;
    Q.Open;
    Existe := not Q.IsEmpty;
    Q.Close;

    if Existe then
    begin
      Q.SQL.Text :=
        'UPDATE USER_geoapolo_departamentos ' +
        'SET nome_departamento = :nome, ' +
        '    empcod            = :empcod, ' +
        '    flagativo         = :flagativo ' +
        'WHERE codigo_departamento = :codigo';
    end
    else
    begin
      Q.SQL.Text :=
        'INSERT INTO USER_geoapolo_departamentos ' +
        '(codigo_departamento, nome_departamento, empcod, flagativo) ' +
        'VALUES (:codigo, :nome, :empcod, :flagativo)';
    end;

    Q.ParamByName('codigo').AsInteger  := ADados.CodigoDepartamento;
    Q.ParamByName('nome').AsString     := Trim(ADados.NomeDepartamento);
    Q.ParamByName('empcod').AsString   := Trim(ADados.EmpCod);
    Q.ParamByName('flagativo').AsString := Trim(ADados.FlagAtivo);
    Q.ExecSQL;

    // Atualiza vínculo com centro de controle se informado
    if Trim(ADados.CCtrlCodEstr) <> '' then
      VincularCentroControle(ADados.CodigoDepartamento, ADados.CCtrlCodEstr)
    else
      RemoverVinculoCentroControle(ADados.CodigoDepartamento);

    Result := True;
  finally
    Q.Free;
  end;
end;

function TDepartamentosRepository.ExcluirDepartamento(
  ACodigo: Integer): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  RemoverVinculoCentroControle(ACodigo);
  Q := CriarQuery;
  try
    Q.SQL.Text := 'DELETE FROM USER_geoapolo_departamentos WHERE codigo_departamento = :codigo';
    Q.ParamByName('codigo').AsInteger := ACodigo;
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TDepartamentosRepository.VincularCentroControle(ACodigo: Integer;
  const ACCtrlCodEstr: string): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  RemoverVinculoCentroControle(ACodigo);
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'INSERT INTO geoapolo_secoescctrlapolo (codigo_secao, cctrlcodestr) ' +
      'VALUES (:codigo, :cctrl)';
    Q.ParamByName('codigo').AsInteger := ACodigo;
    Q.ParamByName('cctrl').AsString   := Trim(ACCtrlCodEstr);
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TDepartamentosRepository.RemoverVinculoCentroControle(
  ACodigo: Integer): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  Q := CriarQuery;
  try
    Q.SQL.Text := 'DELETE FROM geoapolo_secoescctrlapolo WHERE codigo_secao = :codigo';
    Q.ParamByName('codigo').AsInteger := ACodigo;
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

end.
