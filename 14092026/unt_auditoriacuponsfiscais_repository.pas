unit unt_auditoriacuponsfiscais_repository;

interface

uses
  System.SysUtils, System.Classes, System.Generics.Collections,
  FireDAC.Comp.Client, FireDAC.Stan.Param, Data.DB,
  unt_auditoriacuponsfiscais_types;

type
  IAuditoriaCuponsRepository = interface
    ['{F4159D7E-243B-49E8-BF83-E1AC10298B03}']
    function ListarCuponsPDV(const ADataIni, ADataFim: TDateTime): TList<TAuditoriaCupomDTO>;
    function VerificarIntegracaoApolo(const ANFNum, ASerie: string): Boolean;
    function AtualizarFlagsIntegracao(const ANFNum: string; const AInteg, AFin, AFisc, AEstq: string): Boolean;
  end;

  TAuditoriaCuponsRepositoryFireDAC = class(TInterfacedObject, IAuditoriaCuponsRepository)
  private
    FConexaoSQLite: TFDConnection;
    FConexaoApolo: TFDConnection;
  public
    constructor Create(AConexaoSQLite, AConexaoApolo: TFDConnection);
    function ListarCuponsPDV(const ADataIni, ADataFim: TDateTime): TList<TAuditoriaCupomDTO>;
    function VerificarIntegracaoApolo(const ANFNum, ASerie: string): Boolean;
    function AtualizarFlagsIntegracao(const ANFNum: string; const AInteg, AFin, AFisc, AEstq: string): Boolean;
  end;

implementation

{ TAuditoriaCuponsRepositoryFireDAC }

constructor TAuditoriaCuponsRepositoryFireDAC.Create(AConexaoSQLite, AConexaoApolo: TFDConnection);
begin
  inherited Create;
  FConexaoSQLite := AConexaoSQLite;
  FConexaoApolo := AConexaoApolo;
end;

function TAuditoriaCuponsRepositoryFireDAC.ListarCuponsPDV(const ADataIni, ADataFim: TDateTime): TList<TAuditoriaCupomDTO>;
var
  Qry: TFDQuery;
  Item: TAuditoriaCupomDTO;
begin
  Result := TList<TAuditoriaCupomDTO>.Create;
  if FConexaoSQLite = nil then
    Exit;

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexaoSQLite;
    Qry.SQL.Text :=
      'SELECT nf.empcod, nf.entcod, substr(e.entnome, 1, 45) as entnome, ' +
      '       nf.ctrldfserie, nf.nfnum, nf.nfvaltotnota, ' +
      '       (CASE WHEN (SELECT count(1) FROM nota_fiscal_eletronica_trans WHERE nfnum = nf.nfnum) > 0 ' +
      '             THEN ''Transmitiu'' ELSE ''Não Transmitiu'' END) AS sefaz, ' +
      '       nf.nfinteg, nf.nfintegfin, nf.nfintegfisc, nf.nfbxaestq ' +
      'FROM nota_fiscal nf ' +
      'INNER JOIN entidade e ON nf.entcod = e.entcod ' +
      'WHERE nf.nfdataemis BETWEEN :pini AND :pfim ' +
      'ORDER BY nf.nfnum ASC';
    Qry.ParamByName('pini').AsDate := ADataIni;
    Qry.ParamByName('pfim').AsDate := ADataFim;
    Qry.Open;

    while not Qry.Eof do
    begin
      Item.EmpCod := Trim(Qry.FieldByName('empcod').AsString);
      Item.EntCod := Trim(Qry.FieldByName('entcod').AsString);
      Item.EntNome := Trim(Qry.FieldByName('entnome').AsString);
      Item.Serie := Trim(Qry.FieldByName('ctrldfserie').AsString);
      Item.NFNum := Trim(Qry.FieldByName('nfnum').AsString);
      Item.ValorTotal := Qry.FieldByName('nfvaltotnota').AsCurrency;
      Item.StatusSefaz := Trim(Qry.FieldByName('sefaz').AsString);
      Item.IntegradoAlvo := SameText(Trim(Qry.FieldByName('nfinteg').AsString), 'Sim');
      Item.IntegradoFinanc := SameText(Trim(Qry.FieldByName('nfintegfin').AsString), 'Sim');
      Item.IntegradoFiscal := SameText(Trim(Qry.FieldByName('nfintegfisc').AsString), 'Sim');
      Item.BaixouEstoque := SameText(Trim(Qry.FieldByName('nfbxaestq').AsString), 'Sim');
      Result.Add(Item);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
end;

function TAuditoriaCuponsRepositoryFireDAC.VerificarIntegracaoApolo(const ANFNum, ASerie: string): Boolean;
var
  Qry: TFDQuery;
begin
  Result := False;
  if FConexaoApolo = nil then
    Exit;

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexaoApolo;
    Qry.SQL.Text :=
      'SELECT TOP 1 1 FROM nota_fiscal WITH (NOLOCK) ' +
      'WHERE nfnum = :pnfnum AND ctrldfserie = :pserie';
    Qry.ParamByName('pnfnum').AsString := Trim(ANFNum);
    Qry.ParamByName('pserie').AsString := Trim(ASerie);
    Qry.Open;
    Result := not Qry.Eof;
  finally
    Qry.Free;
  end;
end;

function TAuditoriaCuponsRepositoryFireDAC.AtualizarFlagsIntegracao(
  const ANFNum: string; const AInteg, AFin, AFisc, AEstq: string): Boolean;
var
  Qry: TFDQuery;
begin
  Result := False;
  if FConexaoSQLite = nil then
    Exit;

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexaoSQLite;
    Qry.SQL.Text :=
      'UPDATE nota_fiscal SET nfinteg = :pinteg, nfintegfin = :pfin, ' +
      '       nfintegfisc = :pfisc, nfbxaestq = :pestq ' +
      'WHERE nfnum = :pnfnum';
    Qry.ParamByName('pinteg').AsString := AInteg;
    Qry.ParamByName('pfin').AsString := AFin;
    Qry.ParamByName('pfisc').AsString := AFisc;
    Qry.ParamByName('pestq').AsString := AEstq;
    Qry.ParamByName('pnfnum').AsString := Trim(ANFNum);
    Qry.ExecSQL;
    Result := Qry.RowsAffected > 0;
  finally
    Qry.Free;
  end;
end;

end.
