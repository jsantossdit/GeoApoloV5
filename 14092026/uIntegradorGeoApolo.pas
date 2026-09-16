unit uIntegradorGeoApolo;

interface

uses
  System.SysUtils, FireDAC.Comp.Client, Vcl.Forms;

type
  TIntegradorGeoApolo = class
  private
    FFDQuerySrc: TFDQuery;
    FFDQueryDst: TFDQuery;
    FFDQueryAux: TFDQuery;
    procedure ExecutaAcao(const ASQL: string; AQuery: TFDQuery);
    function FormataData(const AData: string): string;
  public
    constructor Create(ASrc, ADst, AAux: TFDQuery);
    procedure SincronizaOrigens(const ABanco: string; const AModoIntegracao: string);
  end;

implementation

{ TIntegradorGeoApolo }

constructor TIntegradorGeoApolo.Create(ASrc, ADst, AAux: TFDQuery);
begin
  FFDQuerySrc := ASrc;
  FFDQueryDst := ADst;
  FFDQueryAux := AAux;
end;

procedure TIntegradorGeoApolo.ExecutaAcao(const ASQL: string; AQuery: TFDQuery);
begin
  AQuery.Close;
  AQuery.SQL.Text := ASQL;
  AQuery.OpenOrExecute;
end;

function TIntegradorGeoApolo.FormataData(const AData: string): string;
begin
  Result := AData;
  if Length(AData) = 10 then
    Result := Copy(AData, 4, 2) + '/' + Copy(AData, 1, 2) + '/' + Copy(AData, 7, 4);
end;

procedure TIntegradorGeoApolo.SincronizaOrigens(const ABanco: string; const AModoIntegracao: string);
var
  sql, datainicial, datafinal: string;
begin
  if ABanco = 'GeoApolo' then
    sql := 'SELECT * FROM USER_geoapolo_origens'
  else
    sql := 'SELECT * FROM origem';

  ExecutaAcao(sql, FFDQuerySrc);

  if FFDQuerySrc.RecordCount <= 0 then
  begin
    if ((AModoIntegracao = 'Integra') or (AModoIntegracao = 'Mescla')) and (ABanco = 'Alvo') then
    begin
      sql := 'SELECT o.OrigCodEstr, o.OrigNome, o.OrigDataInic, o.OrigDataFim, o.OrigAtiva FROM ORIGEM o WITH (NOLOCK)';
      ExecutaAcao(sql, FFDQueryDst);

      if FFDQueryDst.RecordCount > 0 then
      begin
        FFDQueryDst.First;
        while not FFDQueryDst.Eof do
        begin
          datainicial := FormataData(FFDQueryDst.FieldByName('OrigDataInic').AsString);
          if datainicial = '' then datainicial := '01/01/2000';

          datafinal := FormataData(FFDQueryDst.FieldByName('OrigDataFim').AsString);
          if datafinal = '' then datafinal := '31/12/2050';

          sql :=
            'INSERT INTO USER_geoapolo_origens (geo_origcodestr, geo_orignome, geo_origdatainicial, geo_origdatafinal, geo_origativa) ' +
            'VALUES (' +
            QuotedStr(FFDQueryDst.FieldByName('OrigCodEstr').AsString) + ', ' +
            QuotedStr(FFDQueryDst.FieldByName('OrigNome').AsString) + ', ' +
            QuotedStr(datainicial) + ', ' +
            QuotedStr(datafinal) + ', ' +
            QuotedStr(FFDQueryDst.FieldByName('OrigAtiva').AsString) + ')';

          ExecutaAcao(sql, FFDQueryAux);
          FFDQueryDst.Next;
        end;
      end;
    end;
  end;
end;

end.

