unit unt_ocorrencia_repository;

interface

uses
  System.SysUtils, System.Classes, Data.DB, FireDAC.Comp.Client,
  FireDAC.Stan.Param, FireDAC.Stan.Option, unt_ocorrencia_types;

type
  IOcorrenciaRepository = interface
    ['{7A8B9C0D-1E2F-3A4B-5C6D-7E8F9A0B1C2D}']
    function ListarOcorrencias(const AStatus: string = ''; const AEmpCod: string = ''): TArray<TOcorrenciaDTO>;
    function ObterOcorrencia(const AOcorCod: string): TOcorrenciaDTO;
    function SalvarOcorrencia(const ADTO: TOcorrenciaDTO): Boolean;
    function CancelarOcorrencia(const AOcorCod, ADataCanc, ARespCanc, AMotCanc: string): Boolean;
    function AtualizarSolucao(const AOcorCod, ARespTexto, AStatus, ARespSol: string): Boolean;
    function ListarAreasDisponiveis: TArray<TMotivoOcorDTO>;
    function ListarMotivosPorArea(const APrefixoArea: string): TArray<TMotivoOcorDTO>;
    function ListarOrigens: TArray<TOrigemDTO>;
    function ListarSolicitantes(const AFiltro: string = ''): TArray<TSolicitanteDTO>;
  end;

  TOcorrenciaRepository = class(TInterfacedObject, IOcorrenciaRepository)
  private
    FConn: TFDConnection;
  public
    constructor Create(AConnection: TFDConnection);
    function ListarOcorrencias(const AStatus: string = ''; const AEmpCod: string = ''): TArray<TOcorrenciaDTO>;
    function ObterOcorrencia(const AOcorCod: string): TOcorrenciaDTO;
    function SalvarOcorrencia(const ADTO: TOcorrenciaDTO): Boolean;
    function CancelarOcorrencia(const AOcorCod, ADataCanc, ARespCanc, AMotCanc: string): Boolean;
    function AtualizarSolucao(const AOcorCod, ARespTexto, AStatus, ARespSol: string): Boolean;
    function ListarAreasDisponiveis: TArray<TMotivoOcorDTO>;
    function ListarMotivosPorArea(const APrefixoArea: string): TArray<TMotivoOcorDTO>;
    function ListarOrigens: TArray<TOrigemDTO>;
    function ListarSolicitantes(const AFiltro: string = ''): TArray<TSolicitanteDTO>;
  end;

implementation

constructor TOcorrenciaRepository.Create(AConnection: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConnection) then
    raise Exception.Create('TOcorrenciaRepository: TFDConnection e obrigatoria.');
  FConn := AConnection;
end;

function TOcorrenciaRepository.ListarOcorrencias(const AStatus, AEmpCod: string): TArray<TOcorrenciaDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TOcorrenciaDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT o.OcorCod, o.OcorStat, o.EntCod, o.ocorentnome, o.OcorRespSol, ' +
      '       CONVERT(VARCHAR(10), o.OcorData, 120) AS ocordata_str, ' +
      '       o.MotOcorCodEstr, COALESCE(mo.MotOcorDescr, '''') AS MotOcorDescr, ' +
      '       COALESCE(o.ocortexto, '''') AS ocortexto, ' +
      '       COALESCE(o.ocorresptexto, '''') AS ocorresptexto, ' +
      '       COALESCE(o.origcodestr, '''') AS origcodestr, ' +
      '       COALESCE(o.empcod, '''') AS empcod, ' +
      '       CONVERT(VARCHAR(10), o.ocordatacanc, 120) AS ocordatacanc_str, ' +
      '       COALESCE(o.ocorrespcanc, '''') AS ocorrespcanc, ' +
      '       COALESCE(o.ocormotcanc, '''') AS ocormotcanc ' +
      'FROM OCORRENCIA o WITH (NOLOCK) ' +
      'LEFT JOIN MOTIVO_OCOR mo WITH (NOLOCK) ON o.MotOcorCodEstr = mo.MotOcorCodEstr ' +
      'WHERE (:pStatus = '''' OR o.OcorStat = :pStatus2) ' +
      '  AND (:pEmpCod = '''' OR o.empcod = :pEmpCod2) ' +
      'ORDER BY o.OcorData DESC';
    Qry.ParamByName('pStatus').AsString := AStatus;
    Qry.ParamByName('pStatus2').AsString := AStatus;
    Qry.ParamByName('pEmpCod').AsString := AEmpCod;
    Qry.ParamByName('pEmpCod2').AsString := AEmpCod;
    Qry.Open;
    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].OcorCod        := Qry.FieldByName('OcorCod').AsString;
      Res[Idx].OcorStat       := Qry.FieldByName('OcorStat').AsString;
      Res[Idx].EntCod         := Qry.FieldByName('EntCod').AsString;
      Res[Idx].OcorEntNome    := Qry.FieldByName('ocorentnome').AsString;
      Res[Idx].OcorRespSol    := Qry.FieldByName('OcorRespSol').AsString;
      Res[Idx].OcorData       := Qry.FieldByName('ocordata_str').AsString;
      Res[Idx].MotOcorCodEstr := Qry.FieldByName('MotOcorCodEstr').AsString;
      Res[Idx].MotOcorDescr   := Qry.FieldByName('MotOcorDescr').AsString;
      Res[Idx].OcorTexto      := Qry.FieldByName('ocortexto').AsString;
      Res[Idx].OcorRespTexto  := Qry.FieldByName('ocorresptexto').AsString;
      Res[Idx].OrigCodEstr    := Qry.FieldByName('origcodestr').AsString;
      Res[Idx].EmpCod         := Qry.FieldByName('empcod').AsString;
      Res[Idx].OcorDataCanc   := Qry.FieldByName('ocordatacanc_str').AsString;
      Res[Idx].OcorRespCanc   := Qry.FieldByName('ocorrespcanc').AsString;
      Res[Idx].OcorMotCanc    := Qry.FieldByName('ocormotcanc').AsString;
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
  Result := Res;
end;

function TOcorrenciaRepository.ObterOcorrencia(const AOcorCod: string): TOcorrenciaDTO;
var
  Qry: TFDQuery;
begin
  FillChar(Result, SizeOf(Result), 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT o.OcorCod, o.OcorStat, o.EntCod, o.ocorentnome, o.OcorRespSol, ' +
      '       CONVERT(VARCHAR(10), o.OcorData, 120) AS ocordata_str, ' +
      '       o.MotOcorCodEstr, COALESCE(mo.MotOcorDescr, '''') AS MotOcorDescr, ' +
      '       COALESCE(o.ocortexto, '''') AS ocortexto, ' +
      '       COALESCE(o.ocorresptexto, '''') AS ocorresptexto, ' +
      '       COALESCE(o.origcodestr, '''') AS origcodestr, ' +
      '       COALESCE(o.empcod, '''') AS empcod, ' +
      '       CONVERT(VARCHAR(10), o.ocordatacanc, 120) AS ocordatacanc_str, ' +
      '       COALESCE(o.ocorrespcanc, '''') AS ocorrespcanc, ' +
      '       COALESCE(o.ocormotcanc, '''') AS ocormotcanc ' +
      'FROM OCORRENCIA o WITH (NOLOCK) ' +
      'LEFT JOIN MOTIVO_OCOR mo WITH (NOLOCK) ON o.MotOcorCodEstr = mo.MotOcorCodEstr ' +
      'WHERE o.OcorCod = :pCod';
    Qry.ParamByName('pCod').AsString := AOcorCod;
    Qry.Open;
    if not Qry.Eof then
    begin
      Result.OcorCod        := Qry.FieldByName('OcorCod').AsString;
      Result.OcorStat       := Qry.FieldByName('OcorStat').AsString;
      Result.EntCod         := Qry.FieldByName('EntCod').AsString;
      Result.OcorEntNome    := Qry.FieldByName('ocorentnome').AsString;
      Result.OcorRespSol    := Qry.FieldByName('OcorRespSol').AsString;
      Result.OcorData       := Qry.FieldByName('ocordata_str').AsString;
      Result.MotOcorCodEstr := Qry.FieldByName('MotOcorCodEstr').AsString;
      Result.MotOcorDescr   := Qry.FieldByName('MotOcorDescr').AsString;
      Result.OcorTexto      := Qry.FieldByName('ocortexto').AsString;
      Result.OcorRespTexto  := Qry.FieldByName('ocorresptexto').AsString;
      Result.OrigCodEstr    := Qry.FieldByName('origcodestr').AsString;
      Result.EmpCod         := Qry.FieldByName('empcod').AsString;
      Result.OcorDataCanc   := Qry.FieldByName('ocordatacanc_str').AsString;
      Result.OcorRespCanc   := Qry.FieldByName('ocorrespcanc').AsString;
      Result.OcorMotCanc    := Qry.FieldByName('ocormotcanc').AsString;
    end;
  finally
    Qry.Free;
  end;
end;

function TOcorrenciaRepository.SalvarOcorrencia(const ADTO: TOcorrenciaDTO): Boolean;
var
  Qry: TFDQuery;
  Existe: Boolean;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Existe := False;
    if Trim(ADTO.OcorCod) <> '' then
    begin
      Qry.SQL.Text := 'SELECT COUNT(1) AS qtd FROM OCORRENCIA WITH (NOLOCK) WHERE OcorCod = :pCod';
      Qry.ParamByName('pCod').AsString := ADTO.OcorCod;
      Qry.Open;
      Existe := Qry.FieldByName('qtd').AsInteger > 0;
      Qry.Close;
    end;

    FConn.StartTransaction;
    try
      if Existe then
      begin
        Qry.SQL.Text :=
          'UPDATE OCORRENCIA SET ' +
          '  EntCod = :pEntCod, ocorentnome = :pEntNome, OcorRespSol = :pRespSol, ' +
          '  MotOcorCodEstr = :pMotCod, ocortexto = :pTexto, ocorresptexto = :pRespTexto, ' +
          '  origcodestr = :pOrigCod, ocorstat = :pStat, empcod = :pEmpCod ' +
          'WHERE OcorCod = :pCod';
        Qry.ParamByName('pEntCod').AsString    := ADTO.EntCod;
        Qry.ParamByName('pEntNome').AsString   := ADTO.OcorEntNome;
        Qry.ParamByName('pRespSol').AsString   := ADTO.OcorRespSol;
        Qry.ParamByName('pMotCod').AsString    := ADTO.MotOcorCodEstr;
        Qry.ParamByName('pTexto').AsString     := ADTO.OcorTexto;
        Qry.ParamByName('pRespTexto').AsString := ADTO.OcorRespTexto;
        Qry.ParamByName('pOrigCod').AsString   := ADTO.OrigCodEstr;
        Qry.ParamByName('pStat').AsString      := ADTO.OcorStat;
        Qry.ParamByName('pEmpCod').AsString    := ADTO.EmpCod;
        Qry.ParamByName('pCod').AsString       := ADTO.OcorCod;
        Qry.ExecSQL;
      end
      else
      begin
        Qry.SQL.Text :=
          'INSERT INTO OCORRENCIA (OcorCod, OcorStat, EntCod, ocorentnome, OcorRespSol, ' +
          '                        OcorData, MotOcorCodEstr, ocortexto, ocorresptexto, ' +
          '                        origcodestr, empcod) ' +
          'VALUES (:pCod, :pStat, :pEntCod, :pEntNome, :pRespSol, ' +
          '        GETDATE(), :pMotCod, :pTexto, :pRespTexto, :pOrigCod, :pEmpCod)';
        Qry.ParamByName('pCod').AsString       := ADTO.OcorCod;
        Qry.ParamByName('pStat').AsString      := ADTO.OcorStat;
        Qry.ParamByName('pEntCod').AsString    := ADTO.EntCod;
        Qry.ParamByName('pEntNome').AsString   := ADTO.OcorEntNome;
        Qry.ParamByName('pRespSol').AsString   := ADTO.OcorRespSol;
        Qry.ParamByName('pMotCod').AsString    := ADTO.MotOcorCodEstr;
        Qry.ParamByName('pTexto').AsString     := ADTO.OcorTexto;
        Qry.ParamByName('pRespTexto').AsString := ADTO.OcorRespTexto;
        Qry.ParamByName('pOrigCod').AsString   := ADTO.OrigCodEstr;
        Qry.ParamByName('pEmpCod').AsString    := ADTO.EmpCod;
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

function TOcorrenciaRepository.CancelarOcorrencia(const AOcorCod, ADataCanc, ARespCanc, AMotCanc: string): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    FConn.StartTransaction;
    try
      Qry.SQL.Text :=
        'UPDATE OCORRENCIA SET ' +
        '  ocordatacanc = :pDtCanc, ' +
        '  ocorrespcanc = :pRespCanc, ' +
        '  ocormotcanc = :pMotCanc, ' +
        '  ocorstat = ''Cancelado'' ' +
        'WHERE OcorCod = :pCod';
      Qry.ParamByName('pDtCanc').AsString   := ADataCanc;
      Qry.ParamByName('pRespCanc').AsString := ARespCanc;
      Qry.ParamByName('pMotCanc').AsString  := AMotCanc;
      Qry.ParamByName('pCod').AsString      := AOcorCod;
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

function TOcorrenciaRepository.AtualizarSolucao(const AOcorCod, ARespTexto, AStatus, ARespSol: string): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    FConn.StartTransaction;
    try
      Qry.SQL.Text :=
        'UPDATE OCORRENCIA SET ' +
        '  ocorresptexto = :pRespTexto, ' +
        '  ocorstat = :pStatus, ' +
        '  OcorRespSol = :pRespSol ' +
        'WHERE OcorCod = :pCod';
      Qry.ParamByName('pRespTexto').AsString := ARespTexto;
      Qry.ParamByName('pStatus').AsString    := AStatus;
      Qry.ParamByName('pRespSol').AsString   := ARespSol;
      Qry.ParamByName('pCod').AsString       := AOcorCod;
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

function TOcorrenciaRepository.ListarAreasDisponiveis: TArray<TMotivoOcorDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TMotivoOcorDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT MotOcorCodEstr, MotOcorDescr FROM motivo_ocor WITH (NOLOCK) ' +
      'WHERE MotOcorGrupo = ''T'' ORDER BY MotOcorDescr ASC';
    Qry.Open;
    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].MotOcorCodEstr := Qry.FieldByName('MotOcorCodEstr').AsString;
      Res[Idx].MotOcorDescr   := Qry.FieldByName('MotOcorDescr').AsString;
      Res[Idx].MotOcorGrupo   := 'T';
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
  Result := Res;
end;

function TOcorrenciaRepository.ListarMotivosPorArea(const APrefixoArea: string): TArray<TMotivoOcorDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TMotivoOcorDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT MotOcorCodEstr, MotOcorDescr, ' +
      '       COALESCE(MotOcorResp1, '''') AS MotOcorResp1, ' +
      '       COALESCE(MotOcorResp2, '''') AS MotOcorResp2, ' +
      '       COALESCE(MotOcorResp3, '''') AS MotOcorResp3 ' +
      'FROM motivo_ocor WITH (NOLOCK) ' +
      'WHERE MotOcorGrupo = ''F'' AND MotOcorCodEstr LIKE :pPrefixo + ''%'' ' +
      'ORDER BY MotOcorDescr ASC';
    Qry.ParamByName('pPrefixo').AsString := APrefixoArea;
    Qry.Open;
    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].MotOcorCodEstr := Qry.FieldByName('MotOcorCodEstr').AsString;
      Res[Idx].MotOcorDescr   := Qry.FieldByName('MotOcorDescr').AsString;
      Res[Idx].MotOcorGrupo   := 'F';
      Res[Idx].MotOcorResp1   := Qry.FieldByName('MotOcorResp1').AsString;
      Res[Idx].MotOcorResp2   := Qry.FieldByName('MotOcorResp2').AsString;
      Res[Idx].MotOcorResp3   := Qry.FieldByName('MotOcorResp3').AsString;
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
  Result := Res;
end;

function TOcorrenciaRepository.ListarOrigens: TArray<TOrigemDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TOrigemDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT OrigCodEstr, OrigNome FROM ORIGEM WITH (NOLOCK) ORDER BY OrigCodEstr ASC';
    Qry.Open;
    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].OrigCodEstr := Qry.FieldByName('OrigCodEstr').AsString;
      Res[Idx].OrigNome    := Qry.FieldByName('OrigNome').AsString;
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
  Result := Res;
end;

function TOcorrenciaRepository.ListarSolicitantes(const AFiltro: string): TArray<TSolicitanteDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TSolicitanteDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT e.entcod, e.entnome, ec.categcodestr, COALESCE(e.entstatdescr, '''') AS entstatdescr ' +
      'FROM ENTIDADE e WITH (NOLOCK) ' +
      'INNER JOIN ENT_CATEG ec WITH (NOLOCK) ON e.EntCod = ec.EntCod ' +
      'WHERE (:pFiltro = '''' OR e.entnome LIKE ''%'' + :pFiltro2 + ''%'') ' +
      'GROUP BY e.entcod, e.EntNome, ec.categcodestr, e.EntStatDescr ' +
      'ORDER BY e.EntNome ASC';
    Qry.ParamByName('pFiltro').AsString := AFiltro;
    Qry.ParamByName('pFiltro2').AsString := AFiltro;
    Qry.Open;
    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].EntCod       := Qry.FieldByName('entcod').AsString;
      Res[Idx].EntNome      := Qry.FieldByName('entnome').AsString;
      Res[Idx].CategCodEstr := Qry.FieldByName('categcodestr').AsString;
      Res[Idx].EntStatDescr := Qry.FieldByName('entstatdescr').AsString;
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
  Result := Res;
end;

end.
