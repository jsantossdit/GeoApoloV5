unit DAO.AtivoFixo;

interface

uses
  FireDAC.Comp.Client, FireDAC.Stan.Param, System.SysUtils, Model.AtivoFixo, Data.DB;

type
  TAtivoDAO = class
  private
    FConn: TFDConnection;
    FQuery: TFDQuery;
  public
    constructor Create(AConn: TFDConnection);
    destructor Destroy; override;
    function Salvar(AAtivo: TAtivoFixo; AOperacao: string): Boolean;
    function Deletar(ANumeroBem: string): Boolean;
    procedure Listar(ADataSet: TFDQuery; AEmpresa: string);
  end;

implementation

constructor TAtivoDAO.Create(AConn: TFDConnection);
begin
  FConn := AConn;
  FQuery := TFDQuery.Create(nil);
  FQuery.Connection := FConn;
end;

destructor TAtivoDAO.Destroy;
begin
  FQuery.Free;
  inherited;
end;

procedure TAtivoDAO.Listar(ADataSet: TFDQuery; AEmpresa: string);
begin
  ADataSet.Close;
  ADataSet.SQL.Text := 'SELECT * FROM USER_geoapolo_satfi_ativoimobilizado WHERE empcod = :emp ORDER BY numero_do_bem';
  ADataSet.ParamByName('emp').AsString := AEmpresa;
  ADataSet.Open;
end;

function TAtivoDAO.Salvar(AAtivo: TAtivoFixo; AOperacao: string): Boolean;
begin
  Result := False;
  FQuery.SQL.Clear;

  if AOperacao = 'INCLUSÃO' then
    FQuery.SQL.Add('INSERT INTO USER_geoapolo_satfi_ativoimobilizado (numero_do_bem, descricao_do_bem, geocctrlcodestr, ' +
                   'codigo_categoria_bem, empcod, data_aquisicao, valor_compra, taxa_depreciacao_anual) ' +
                   'VALUES (:num, :desc, :cc, :cat, :emp, :data, :valor, :taxa)')
  else
    FQuery.SQL.Add('UPDATE USER_geoapolo_satfi_ativoimobilizado SET descricao_do_bem = :desc, geocctrlcodestr = :cc, ' +
                   'codigo_categoria_bem = :cat, data_aquisicao = :data, valor_compra = :valor, ' +
                   'taxa_depreciacao_anual = :taxa WHERE numero_do_bem = :num AND empcod = :emp');

  FQuery.ParamByName('num').AsString   := AAtivo.NumeroBem;
  FQuery.ParamByName('desc').AsString  := AAtivo.Descricao;
  FQuery.ParamByName('cc').AsString    := AAtivo.CentroCusto;
  FQuery.ParamByName('cat').AsString   := AAtivo.Categoria;
  FQuery.ParamByName('emp').AsString   := AAtivo.Empresa;
  FQuery.ParamByName('data').AsDate    := AAtivo.DataAquisicao;
  FQuery.ParamByName('valor').AsCurrency := AAtivo.ValorCompra;
  FQuery.ParamByName('taxa').AsFloat   := AAtivo.TaxaDepreciacaoAnual;

  try
    FConn.StartTransaction;
    FQuery.ExecSQL;
    FConn.Commit;
    Result := True;
  except
    on E: Exception do
    begin
      FConn.Rollback;
      raise Exception.Create('Erro ao salvar Ativo: ' + E.Message);
    end;
  end;
end;

function TAtivoDAO.Deletar(ANumeroBem: string): Boolean;
begin
  FQuery.SQL.Text := 'DELETE FROM USER_geoapolo_satfi_ativoimobilizado WHERE numero_do_bem = :num';
  FQuery.ParamByName('num').AsString := ANumeroBem;
  FQuery.ExecSQL;
  Result := FQuery.RowsAffected > 0;
end;

end.
