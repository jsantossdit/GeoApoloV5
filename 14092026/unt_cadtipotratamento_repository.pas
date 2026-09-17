unit unt_cadtipotratamento_repository;

interface

uses
  System.SysUtils, System.Classes, Data.DB, FireDAC.Comp.Client,
  FireDAC.Stan.Param, FireDAC.Stan.Option, unt_cadtipotratamento_types;

type
  ICadTipoTratamentoRepository = interface
    ['{8E2B3C4D-5F6A-7B8C-9D0E-1F2A3B4C5D6E}']
    function ListarTiposTratamento: TArray<TTipoTratamentoDTO>;
    function ObterTipoTratamento(const ACodigo: string): TTipoTratamentoDTO;
    function SalvarTipoTratamento(const ADTO: TTipoTratamentoDTO): Boolean;
    function ExcluirTipoTratamento(const ACodigo: string): Boolean;
  end;

  TCadTipoTratamentoRepository = class(TInterfacedObject, ICadTipoTratamentoRepository)
  private
    FConn: TFDConnection;
  public
    constructor Create(AConnection: TFDConnection);
    function ListarTiposTratamento: TArray<TTipoTratamentoDTO>;
    function ObterTipoTratamento(const ACodigo: string): TTipoTratamentoDTO;
    function SalvarTipoTratamento(const ADTO: TTipoTratamentoDTO): Boolean;
    function ExcluirTipoTratamento(const ACodigo: string): Boolean;
  end;

implementation

constructor TCadTipoTratamentoRepository.Create(AConnection: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConnection) then
    raise Exception.Create('TCadTipoTratamentoRepository: TFDConnection é obrigatória.');
  FConn := AConnection;
end;

function TCadTipoTratamentoRepository.ListarTiposTratamento: TArray<TTipoTratamentoDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TTipoTratamentoDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT tipotratcod, abreviatura, descricao_tratamento FROM USER_geoapolo_tipotratamento WITH (NOLOCK) ORDER BY abreviatura ASC';
    Qry.Open;
    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].TipoTratCod         := Qry.FieldByName('tipotratcod').AsString;
      Res[Idx].Abreviatura         := Qry.FieldByName('abreviatura').AsString;
      Res[Idx].DescricaoTratamento := Qry.FieldByName('descricao_tratamento').AsString;
      Qry.Next;
    end;
    Result := Res;
  finally
    Qry.Free;
  end;
end;

function TCadTipoTratamentoRepository.ObterTipoTratamento(const ACodigo: string): TTipoTratamentoDTO;
var
  Qry: TFDQuery;
begin
  FillChar(Result, SizeOf(Result), 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT tipotratcod, abreviatura, descricao_tratamento FROM USER_geoapolo_tipotratamento WITH (NOLOCK) WHERE tipotratcod = :pCod';
    Qry.ParamByName('pCod').AsString := ACodigo;
    Qry.Open;
    if not Qry.IsEmpty then
    begin
      Result.TipoTratCod         := Qry.FieldByName('tipotratcod').AsString;
      Result.Abreviatura         := Qry.FieldByName('abreviatura').AsString;
      Result.DescricaoTratamento := Qry.FieldByName('descricao_tratamento').AsString;
    end;
  finally
    Qry.Free;
  end;
end;

function TCadTipoTratamentoRepository.SalvarTipoTratamento(const ADTO: TTipoTratamentoDTO): Boolean;
var
  Qry: TFDQuery;
  Existe: Boolean;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT COUNT(*) FROM USER_geoapolo_tipotratamento WHERE tipotratcod = :pCod';
    Qry.ParamByName('pCod').AsString := ADTO.TipoTratCod;
    Qry.Open;
    Existe := Qry.Fields[0].AsInteger > 0;
    Qry.Close;

    if Existe then
    begin
      Qry.SQL.Text :=
        'UPDATE USER_geoapolo_tipotratamento SET abreviatura = :pAbrev, descricao_tratamento = :pDesc ' +
        'WHERE tipotratcod = :pCod';
    end
    else
    begin
      Qry.SQL.Text :=
        'INSERT INTO USER_geoapolo_tipotratamento (tipotratcod, abreviatura, descricao_tratamento) ' +
        'VALUES (:pCod, :pAbrev, :pDesc)';
    end;
    Qry.ParamByName('pCod').AsString   := ADTO.TipoTratCod;
    Qry.ParamByName('pAbrev').AsString := ADTO.Abreviatura;
    Qry.ParamByName('pDesc').AsString  := ADTO.DescricaoTratamento;
    Qry.ExecSQL;
    Result := True;
  finally
    Qry.Free;
  end;
end;

function TCadTipoTratamentoRepository.ExcluirTipoTratamento(const ACodigo: string): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'DELETE FROM USER_geoapolo_tipotratamento WHERE tipotratcod = :pCod';
    Qry.ParamByName('pCod').AsString := ACodigo;
    Qry.ExecSQL;
    Result := True;
  finally
    Qry.Free;
  end;
end;

end.
