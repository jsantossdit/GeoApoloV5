unit unt_DAOEstacoes;

interface

uses FireDAC.Comp.Client, System.SysUtils, unt_model_estacao ;

type
  TEstacaoDAO = class
  private
    FConnection: TFDConnection;
  public
    constructor Create(AConnection: TFDConnection);
    procedure Inserir(AEstacao: TEstacao);
  end;

implementation

constructor TEstacaoDAO.Create(AConnection: TFDConnection);
begin
  FConnection := AConnection;
end;

procedure TEstacaoDAO.Inserir(AEstacao: TEstacao);
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConnection;
    Qry.SQL.Text := 'INSERT INTO USER_geoapolo_satfi_estacao (codigo_estacao, descricao, data_cadastro, enderecoip) ' +
                    'VALUES (:cod, :desc, :data, :ip)';

    Qry.ParamByName('cod').AsString := AEstacao.Codigo;
    Qry.ParamByName('desc').AsString := AEstacao.Descricao;

    if AEstacao.DataCadastro > 0 then
      Qry.ParamByName('data').AsDateTime := AEstacao.DataCadastro
    else
      Qry.ParamByName('data').Clear; // Grava NULL no banco

    Qry.ParamByName('ip').AsString := AEstacao.EnderecoIP;

    Qry.ExecSQL;
  finally
    Qry.Free;
  end;
end;

end.

interface

implementation

end.
