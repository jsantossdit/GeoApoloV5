unit unt_cadtipocampanha_repository;

interface

uses
  System.SysUtils, System.Classes, Data.DB, FireDAC.Comp.Client,
  FireDAC.Stan.Param, FireDAC.Stan.Option, unt_cadtipocampanha_types;

type
  ICadTipoCampanhaRepository = interface
    ['{5A1B2C3D-4E5F-6A7B-8C9D-0E1F2A3B4C5D}']
    function ListarTiposCampanha: TArray<TTipoCampanhaDTO>;
    function ObterTipoCampanha(const ACodigo: string): TTipoCampanhaDTO;
    function SalvarTipoCampanha(const ADTO: TTipoCampanhaDTO): Boolean;
    function ExcluirTipoCampanha(const ACodigo: string): Boolean;
  end;

  TCadTipoCampanhaRepository = class(TInterfacedObject, ICadTipoCampanhaRepository)
  private
    FConn: TFDConnection;
  public
    constructor Create(AConnection: TFDConnection);
    function ListarTiposCampanha: TArray<TTipoCampanhaDTO>;
    function ObterTipoCampanha(const ACodigo: string): TTipoCampanhaDTO;
    function SalvarTipoCampanha(const ADTO: TTipoCampanhaDTO): Boolean;
    function ExcluirTipoCampanha(const ACodigo: string): Boolean;
  end;

implementation

constructor TCadTipoCampanhaRepository.Create(AConnection: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConnection) then
    raise Exception.Create('TCadTipoCampanhaRepository: TFDConnection é obrigatória.');
  FConn := AConnection;
end;

function TCadTipoCampanhaRepository.ListarTiposCampanha: TArray<TTipoCampanhaDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TTipoCampanhaDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT codigo_tipocampanha, descricaotipocamp, ativo, geracampanha FROM USER_geoapolo_tipocampanha WITH (NOLOCK) ORDER BY codigo_tipocampanha ASC';
    Qry.Open;
    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].CodigoTipoCampanha := Qry.FieldByName('codigo_tipocampanha').AsString;
      Res[Idx].DescricaoTipoCamp  := Qry.FieldByName('descricaotipocamp').AsString;
      Res[Idx].Ativo              := Qry.FieldByName('ativo').AsString;
      Res[Idx].GeraCampanha       := Qry.FieldByName('geracampanha').AsString;
      Qry.Next;
    end;
    Result := Res;
  finally
    Qry.Free;
  end;
end;

function TCadTipoCampanhaRepository.ObterTipoCampanha(const ACodigo: string): TTipoCampanhaDTO;
var
  Qry: TFDQuery;
begin
  FillChar(Result, SizeOf(Result), 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT codigo_tipocampanha, descricaotipocamp, ativo, geracampanha FROM USER_geoapolo_tipocampanha WITH (NOLOCK) WHERE codigo_tipocampanha = :pCod';
    Qry.ParamByName('pCod').AsString := ACodigo;
    Qry.Open;
    if not Qry.IsEmpty then
    begin
      Result.CodigoTipoCampanha := Qry.FieldByName('codigo_tipocampanha').AsString;
      Result.DescricaoTipoCamp  := Qry.FieldByName('descricaotipocamp').AsString;
      Result.Ativo              := Qry.FieldByName('ativo').AsString;
      Result.GeraCampanha       := Qry.FieldByName('geracampanha').AsString;
    end;
  finally
    Qry.Free;
  end;
end;

function TCadTipoCampanhaRepository.SalvarTipoCampanha(const ADTO: TTipoCampanhaDTO): Boolean;
var
  Qry: TFDQuery;
  Existe: Boolean;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    FConn.StartTransaction;
    try
      Qry.SQL.Text := 'SELECT COUNT(*) FROM USER_geoapolo_tipocampanha WHERE codigo_tipocampanha = :pCod';
      Qry.ParamByName('pCod').AsString := ADTO.CodigoTipoCampanha;
      Qry.Open;
      Existe := Qry.Fields[0].AsInteger > 0;
      Qry.Close;

      if Existe then
      begin
        Qry.SQL.Text :=
          'UPDATE USER_geoapolo_tipocampanha SET descricaotipocamp = :pDesc, ativo = :pAtivo, geracampanha = :pGera ' +
          'WHERE codigo_tipocampanha = :pCod';
      end
      else
      begin
        Qry.SQL.Text :=
          'INSERT INTO USER_geoapolo_tipocampanha (codigo_tipocampanha, descricaotipocamp, ativo, geracampanha) ' +
          'VALUES (:pCod, :pDesc, :pAtivo, :pGera)';
      end;
      Qry.ParamByName('pCod').AsString   := ADTO.CodigoTipoCampanha;
      Qry.ParamByName('pDesc').AsString  := ADTO.DescricaoTipoCamp;
      Qry.ParamByName('pAtivo').AsString := ADTO.Ativo;
      Qry.ParamByName('pGera').AsString  := ADTO.GeraCampanha;
      Qry.ExecSQL;

      // Sincroniza também com base Apolo tipo_campanha
      Qry.SQL.Text :=
        'IF NOT EXISTS (SELECT 1 FROM tipo_campanha WHERE tipocampcod = :pCod) ' +
        '  INSERT INTO tipo_campanha (tipocampcod, tipocampnome) VALUES (:pCod, :pDesc) ' +
        'ELSE ' +
        '  UPDATE tipo_campanha SET tipocampnome = :pDesc WHERE tipocampcod = :pCod';
      Qry.ParamByName('pCod').AsString  := ADTO.CodigoTipoCampanha;
      Qry.ParamByName('pDesc').AsString := ADTO.DescricaoTipoCamp;
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

function TCadTipoCampanhaRepository.ExcluirTipoCampanha(const ACodigo: string): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    FConn.StartTransaction;
    try
      Qry.SQL.Text := 'DELETE FROM USER_geoapolo_tipocampanha WHERE codigo_tipocampanha = :pCod';
      Qry.ParamByName('pCod').AsString := ACodigo;
      Qry.ExecSQL;

      Qry.SQL.Text := 'DELETE FROM tipo_campanha WHERE tipocampcod = :pCod';
      Qry.ParamByName('pCod').AsString := ACodigo;
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
