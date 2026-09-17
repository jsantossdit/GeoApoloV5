unit unt_configcod_repository;

{
  GeoApolo - Repositório de Manutenção de Códigos e Sequenciais do Sistema
  Clean Architecture: Acesso desacoplado com queries parametrizadas e WITH (NOLOCK).
}

interface

uses
  System.SysUtils, System.Classes, FireDAC.Comp.Client, FireDAC.DApt, Data.DB,
  unt_configcod_types;

type

  TConfigCodRepository = class
  private
    FConexao: TFDConnection;
    function CriarQuery: TFDQuery;
  public
    constructor Create(AConexao: TFDConnection);

    function ListarTabelas(const AFiltro: string; out ALista: TArray<TDadosConfigCod>): Boolean;
    function ObterConfigCod(const AGeoTabela: string; out ADados: TDadosConfigCod): Boolean;
    function AtualizarProximoCodigo(const AGeoTabela: string; AProximoCodigo: Integer;
      const ATabelaAtiva: string): Boolean;
    function SalvarConfigCod(const ADados: TDadosConfigCod): Boolean;
  end;

implementation

{ TConfigCodRepository }

constructor TConfigCodRepository.Create(AConexao: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConexao) then
    raise EArgumentNilException.Create('TConfigCodRepository: Conexao nao pode ser nula.');
  FConexao := AConexao;
end;

function TConfigCodRepository.CriarQuery: TFDQuery;
begin
  Result := TFDQuery.Create(nil);
  Result.Connection := FConexao;
end;

function TConfigCodRepository.ListarTabelas(const AFiltro: string;
  out ALista: TArray<TDadosConfigCod>): Boolean;
var
  Q: TFDQuery;
  Idx: Integer;
  FiltroLimpo: string;
begin
  Result := False;
  SetLength(ALista, 0);
  Q := CriarQuery;
  try
    FiltroLimpo := Trim(AFiltro);
    if FiltroLimpo = '' then
    begin
      Q.SQL.Text :=
        'SELECT ugcc.geotabela, ugcc.proximo_codigo, ugcc.tabela_ativa, ' +
        '       ugcc.empcod, ISNULL(uge.empnome, '''') AS empnome ' +
        'FROM USER_geoapolo_configcod ugcc WITH (NOLOCK) ' +
        'LEFT JOIN USER_geoapolo_empresas uge WITH (NOLOCK) ON ugcc.empcod = uge.empcod ' +
        'ORDER BY ugcc.geotabela ASC';
    end
    else
    begin
      Q.SQL.Text :=
        'SELECT ugcc.geotabela, ugcc.proximo_codigo, ugcc.tabela_ativa, ' +
        '       ugcc.empcod, ISNULL(uge.empnome, '''') AS empnome ' +
        'FROM USER_geoapolo_configcod ugcc WITH (NOLOCK) ' +
        'LEFT JOIN USER_geoapolo_empresas uge WITH (NOLOCK) ON ugcc.empcod = uge.empcod ' +
        'WHERE ugcc.geotabela LIKE :filtro ' +
        'ORDER BY ugcc.geotabela ASC';
      Q.ParamByName('filtro').AsString := '%' + FiltroLimpo + '%';
    end;

    Q.Open;
    SetLength(ALista, Q.RecordCount);
    Idx := 0;
    while not Q.Eof do
    begin
      ALista[Idx].GeoTabela     := Q.FieldByName('geotabela').AsString;
      ALista[Idx].ProximoCodigo := Q.FieldByName('proximo_codigo').AsInteger;
      ALista[Idx].TabelaAtiva   := Q.FieldByName('tabela_ativa').AsString;
      ALista[Idx].EmpCod        := Q.FieldByName('empcod').AsString;
      ALista[Idx].EmpNome       := Q.FieldByName('empnome').AsString;
      Inc(Idx);
      Q.Next;
    end;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TConfigCodRepository.ObterConfigCod(const AGeoTabela: string;
  out ADados: TDadosConfigCod): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  ADados := Default(TDadosConfigCod);
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'SELECT ugcc.geotabela, ugcc.proximo_codigo, ugcc.tabela_ativa, ' +
      '       ugcc.empcod, ISNULL(uge.empnome, '''') AS empnome ' +
      'FROM USER_geoapolo_configcod ugcc WITH (NOLOCK) ' +
      'LEFT JOIN USER_geoapolo_empresas uge WITH (NOLOCK) ON ugcc.empcod = uge.empcod ' +
      'WHERE ugcc.geotabela = :geotabela';
    Q.ParamByName('geotabela').AsString := Trim(AGeoTabela);
    Q.Open;

    if not Q.IsEmpty then
    begin
      ADados.GeoTabela     := Q.FieldByName('geotabela').AsString;
      ADados.ProximoCodigo := Q.FieldByName('proximo_codigo').AsInteger;
      ADados.TabelaAtiva   := Q.FieldByName('tabela_ativa').AsString;
      ADados.EmpCod        := Q.FieldByName('empcod').AsString;
      ADados.EmpNome       := Q.FieldByName('empnome').AsString;
      Result := True;
    end;
  finally
    Q.Free;
  end;
end;

function TConfigCodRepository.AtualizarProximoCodigo(const AGeoTabela: string;
  AProximoCodigo: Integer; const ATabelaAtiva: string): Boolean;
var
  Q: TFDQuery;
begin
  Result := False;
  Q := CriarQuery;
  try
    Q.SQL.Text :=
      'UPDATE USER_geoapolo_configcod ' +
      'SET proximo_codigo = :proximocodigo, ' +
      '    tabela_ativa   = :tabelaativa ' +
      'WHERE geotabela = :geotabela';
    Q.ParamByName('proximocodigo').AsInteger := AProximoCodigo;
    Q.ParamByName('tabelaativa').AsString    := Trim(ATabelaAtiva);
    Q.ParamByName('geotabela').AsString      := Trim(AGeoTabela);
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

function TConfigCodRepository.SalvarConfigCod(
  const ADados: TDadosConfigCod): Boolean;
var
  Q: TFDQuery;
  Existe: Boolean;
begin
  Result := False;
  Q := CriarQuery;
  try
    Q.SQL.Text := 'SELECT 1 FROM USER_geoapolo_configcod WHERE geotabela = :geotabela';
    Q.ParamByName('geotabela').AsString := Trim(ADados.GeoTabela);
    Q.Open;
    Existe := not Q.IsEmpty;
    Q.Close;

    if Existe then
    begin
      Q.SQL.Text :=
        'UPDATE USER_geoapolo_configcod ' +
        'SET proximo_codigo = :proximocodigo, ' +
        '    tabela_ativa   = :tabelaativa, ' +
        '    empcod         = :empcod ' +
        'WHERE geotabela = :geotabela';
    end
    else
    begin
      Q.SQL.Text :=
        'INSERT INTO USER_geoapolo_configcod (geotabela, proximo_codigo, tabela_ativa, empcod) ' +
        'VALUES (:geotabela, :proximocodigo, :tabelaativa, :empcod)';
    end;

    Q.ParamByName('geotabela').AsString      := Trim(ADados.GeoTabela);
    Q.ParamByName('proximocodigo').AsInteger := ADados.ProximoCodigo;
    Q.ParamByName('tabelaativa').AsString    := Trim(ADados.TabelaAtiva);
    Q.ParamByName('empcod').AsString         := Trim(ADados.EmpCod);
    Q.ExecSQL;
    Result := True;
  finally
    Q.Free;
  end;
end;

end.
