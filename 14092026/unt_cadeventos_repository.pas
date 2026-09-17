unit unt_cadeventos_repository;

interface

uses
  System.SysUtils, System.Classes, Data.DB, FireDAC.Comp.Client,
  FireDAC.Stan.Param, FireDAC.Stan.Option, unt_cadeventos_types;

type
  ICadEventosRepository = interface
    ['{3B8F1A2C-4E5D-6F7A-8B9C-0D1E2F3A4B5C}']
    function ListarEventos(const AFiltroTema: string = ''): TArray<TEventoDTO>;
    function ObterEvento(const AIdEvento: string): TEventoDTO;
    function SalvarEvento(const AEvento: TEventoDTO): Boolean;
    function ExcluirEvento(const AIdEvento: string): Boolean;
    function ListarTiposEvento: TArray<TTipoEventoDTO>;
  end;

  TCadEventosRepository = class(TInterfacedObject, ICadEventosRepository)
  private
    FConn: TFDConnection;
  public
    constructor Create(AConnection: TFDConnection);
    function ListarEventos(const AFiltroTema: string = ''): TArray<TEventoDTO>;
    function ObterEvento(const AIdEvento: string): TEventoDTO;
    function SalvarEvento(const AEvento: TEventoDTO): Boolean;
    function ExcluirEvento(const AIdEvento: string): Boolean;
    function ListarTiposEvento: TArray<TTipoEventoDTO>;
  end;

implementation

constructor TCadEventosRepository.Create(AConnection: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConnection) then
    raise Exception.Create('TCadEventosRepository: TFDConnection é obrigatória.');
  FConn := AConnection;
end;

function TCadEventosRepository.ListarEventos(const AFiltroTema: string): TArray<TEventoDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TEventoDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT uge.idevento, uge.descricao, ' +
      '       CONVERT(VARCHAR(10), uge.data_inicial, 120) AS dt_ini_str, ' +
      '       CONVERT(VARCHAR(10), uge.data_final, 120) AS dt_fim_str, ' +
      '       uge.tema_principal, uge.tipoeventcod, ' +
      '       COALESCE(te.descricao_tipoevento, '''') AS desc_tipo ' +
      'FROM USER_geoapolo_eventos uge WITH (NOLOCK) ' +
      'LEFT JOIN USER_geoapolo_tipo_eventos te WITH (NOLOCK) ON uge.tipoeventcod = te.tipoeventcod ' +
      'WHERE 1=1 ';

    if Trim(AFiltroTema) <> '' then
    begin
      Qry.SQL.Text := Qry.SQL.Text + 'AND (uge.tema_principal LIKE :pTema OR uge.descricao LIKE :pTema) ';
      Qry.ParamByName('pTema').AsString := '%' + Trim(AFiltroTema) + '%';
    end;

    Qry.SQL.Text := Qry.SQL.Text + 'ORDER BY uge.data_inicial DESC';
    Qry.Open;

    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].IdEvento            := Qry.FieldByName('idevento').AsString;
      Res[Idx].Descricao           := Qry.FieldByName('descricao').AsString;
      Res[Idx].DataInicial         := Qry.FieldByName('dt_ini_str').AsString;
      Res[Idx].DataFinal           := Qry.FieldByName('dt_fim_str').AsString;
      Res[Idx].TemaPrincipal       := Qry.FieldByName('tema_principal').AsString;
      Res[Idx].TipoEventCod        := Qry.FieldByName('tipoeventcod').AsString;
      Res[Idx].DescricaoTipoEvento := Qry.FieldByName('desc_tipo').AsString;
      Qry.Next;
    end;
    Result := Res;
  finally
    Qry.Free;
  end;
end;

function TCadEventosRepository.ObterEvento(const AIdEvento: string): TEventoDTO;
var
  Qry: TFDQuery;
begin
  FillChar(Result, SizeOf(Result), 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT uge.idevento, uge.descricao, ' +
      '       CONVERT(VARCHAR(10), uge.data_inicial, 120) AS dt_ini_str, ' +
      '       CONVERT(VARCHAR(10), uge.data_final, 120) AS dt_fim_str, ' +
      '       uge.tema_principal, uge.tipoeventcod, ' +
      '       COALESCE(te.descricao_tipoevento, '''') AS desc_tipo ' +
      'FROM USER_geoapolo_eventos uge WITH (NOLOCK) ' +
      'LEFT JOIN USER_geoapolo_tipo_eventos te WITH (NOLOCK) ON uge.tipoeventcod = te.tipoeventcod ' +
      'WHERE uge.idevento = :pId';
    Qry.ParamByName('pId').AsString := AIdEvento;
    Qry.Open;
    if not Qry.IsEmpty then
    begin
      Result.IdEvento            := Qry.FieldByName('idevento').AsString;
      Result.Descricao           := Qry.FieldByName('descricao').AsString;
      Result.DataInicial         := Qry.FieldByName('dt_ini_str').AsString;
      Result.DataFinal           := Qry.FieldByName('dt_fim_str').AsString;
      Result.TemaPrincipal       := Qry.FieldByName('tema_principal').AsString;
      Result.TipoEventCod        := Qry.FieldByName('tipoeventcod').AsString;
      Result.DescricaoTipoEvento := Qry.FieldByName('desc_tipo').AsString;
    end;
  finally
    Qry.Free;
  end;
end;

function TCadEventosRepository.SalvarEvento(const AEvento: TEventoDTO): Boolean;
var
  Qry: TFDQuery;
  Existe: Boolean;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT COUNT(*) FROM USER_geoapolo_eventos WHERE idevento = :pId';
    Qry.ParamByName('pId').AsString := AEvento.IdEvento;
    Qry.Open;
    Existe := Qry.Fields[0].AsInteger > 0;
    Qry.Close;

    if Existe then
    begin
      Qry.SQL.Text :=
        'UPDATE USER_geoapolo_eventos SET ' +
        '  descricao = :pDesc, data_inicial = :pIni, data_final = :pFim, ' +
        '  tema_principal = :pTema, tipoeventcod = :pTipo ' +
        'WHERE idevento = :pId';
    end
    else
    begin
      Qry.SQL.Text :=
        'INSERT INTO USER_geoapolo_eventos (idevento, descricao, data_inicial, data_final, tema_principal, tipoeventcod) ' +
        'VALUES (:pId, :pDesc, :pIni, :pFim, :pTema, :pTipo)';
    end;

    Qry.ParamByName('pId').AsString   := AEvento.IdEvento;
    Qry.ParamByName('pDesc').AsString := AEvento.Descricao;
    Qry.ParamByName('pIni').AsString  := AEvento.DataInicial;
    Qry.ParamByName('pFim').AsString  := AEvento.DataFinal;
    Qry.ParamByName('pTema').AsString := AEvento.TemaPrincipal;
    Qry.ParamByName('pTipo').AsString := AEvento.TipoEventCod;
    Qry.ExecSQL;
    Result := True;
  finally
    Qry.Free;
  end;
end;

function TCadEventosRepository.ExcluirEvento(const AIdEvento: string): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'DELETE FROM USER_geoapolo_eventos WHERE idevento = :pId';
    Qry.ParamByName('pId').AsString := AIdEvento;
    Qry.ExecSQL;
    Result := True;
  finally
    Qry.Free;
  end;
end;

function TCadEventosRepository.ListarTiposEvento: TArray<TTipoEventoDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TTipoEventoDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT tipoeventcod, descricao_tipoevento FROM USER_geoapolo_tipo_eventos WITH (NOLOCK) ORDER BY descricao_tipoevento ASC';
    Qry.Open;
    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].TipoEventCod        := Qry.FieldByName('tipoeventcod').AsString;
      Res[Idx].DescricaoTipoEvento := Qry.FieldByName('descricao_tipoevento').AsString;
      Qry.Next;
    end;
    Result := Res;
  finally
    Qry.Free;
  end;
end;

end.
