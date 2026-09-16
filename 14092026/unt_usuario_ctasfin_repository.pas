unit unt_usuario_ctasfin_repository;

interface

uses
  System.SysUtils, System.Classes, System.Generics.Collections,
  FireDAC.Comp.Client, FireDAC.Stan.Param, Data.DB,
  unt_usuario_ctasfin_types;

type
  /// <summary>
  /// Interface para abstração de persistência das permissões de contas financeiras.
  /// </summary>
  IUsuarioCtasFinRepository = interface
    ['{B8A1D394-399F-4D21-8608-D2D49DF798B1}']
    function ListarUsuariosAtivos: TList<string>;
    function ListarContasDisponiveis: TList<TContaFinanceiraDTO>;
    function ListarContasPorUsuario(const AUsuCod: string): TList<TContaFinanceiraDTO>;
    function SalvarPermissoesUsuario(const AUsuCod: string; const AContas: TArray<string>): TResultadoOperacaoContasFin;
    function RevogarTodasPermissoes(const AUsuCod: string): TResultadoOperacaoContasFin;
  end;

  /// <summary>
  /// Implementação concreta do repositório utilizando FireDAC e otimizações SQL Server.
  /// </summary>
  TUsuarioCtasFinRepositoryFireDAC = class(TInterfacedObject, IUsuarioCtasFinRepository)
  private
    FConexao: TFDConnection;
  public
    constructor Create(AConexao: TFDConnection);
    function ListarUsuariosAtivos: TList<string>;
    function ListarContasDisponiveis: TList<TContaFinanceiraDTO>;
    function ListarContasPorUsuario(const AUsuCod: string): TList<TContaFinanceiraDTO>;
    function SalvarPermissoesUsuario(const AUsuCod: string; const AContas: TArray<string>): TResultadoOperacaoContasFin;
    function RevogarTodasPermissoes(const AUsuCod: string): TResultadoOperacaoContasFin;
  end;

implementation

{ TUsuarioCtasFinRepositoryFireDAC }

constructor TUsuarioCtasFinRepositoryFireDAC.Create(AConexao: TFDConnection);
begin
  inherited Create;
  FConexao := AConexao;
end;

function TUsuarioCtasFinRepositoryFireDAC.ListarUsuariosAtivos: TList<string>;
var
  Qry: TFDQuery;
begin
  Result := TList<string>.Create;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    // TODO: Python SQLAlchemy -> session.query(Usuario.usucod).filter(Usuario.usustat == 'Ativo').order_by(Usuario.usucod)
    Qry.SQL.Text :=
      'SELECT usucod FROM usuario WITH (NOLOCK) ' +
      'WHERE usustat = :pstatus ' +
      'ORDER BY usucod ASC';
    Qry.ParamByName('pstatus').AsString := 'Ativo';
    Qry.Open;

    while not Qry.Eof do
    begin
      Result.Add(Trim(Qry.FieldByName('usucod').AsString));
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
end;

function TUsuarioCtasFinRepositoryFireDAC.ListarContasDisponiveis: TList<TContaFinanceiraDTO>;
var
  Qry: TFDQuery;
  Item: TContaFinanceiraDTO;
begin
  Result := TList<TContaFinanceiraDTO>.Create;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    // TODO: Python SQLAlchemy -> session.query(ContaFin).order_by(ContaFin.contafincod.asc())
    Qry.SQL.Text :=
      'SELECT contafincod, contafinnome, contafinccornum ' +
      'FROM conta_fin WITH (NOLOCK) ' +
      'ORDER BY contafincod ASC';
    Qry.Open;

    while not Qry.Eof do
    begin
      Item.ContaFinCod := Trim(Qry.FieldByName('contafincod').AsString);
      Item.ContaFinNome := Trim(Qry.FieldByName('contafinnome').AsString);
      Item.ContaFinCcorNum := Trim(Qry.FieldByName('contafinccornum').AsString);
      Result.Add(Item);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
end;

function TUsuarioCtasFinRepositoryFireDAC.ListarContasPorUsuario(const AUsuCod: string): TList<TContaFinanceiraDTO>;
var
  Qry: TFDQuery;
  Item: TContaFinanceiraDTO;
begin
  Result := TList<TContaFinanceiraDTO>.Create;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    // TODO: Python SQLAlchemy -> Join between UsuarioContaFin and ContaFin filtered by usucod
    Qry.SQL.Text :=
      'SELECT ucf.contafincod, cf.contafinnome, cf.contafinccornum ' +
      'FROM usuario_conta_fin ucf WITH (NOLOCK) ' +
      'INNER JOIN conta_fin cf WITH (NOLOCK) ON cf.contafincod = ucf.contafincod ' +
      'WHERE ucf.usucod = :pusucod ' +
      'ORDER BY ucf.contafincod ASC';
    Qry.ParamByName('pusucod').AsString := Trim(AUsuCod);
    Qry.Open;

    while not Qry.Eof do
    begin
      Item.ContaFinCod := Trim(Qry.FieldByName('contafincod').AsString);
      Item.ContaFinNome := Trim(Qry.FieldByName('contafinnome').AsString);
      Item.ContaFinCcorNum := Trim(Qry.FieldByName('contafinccornum').AsString);
      Result.Add(Item);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
end;

function TUsuarioCtasFinRepositoryFireDAC.RevogarTodasPermissoes(const AUsuCod: string): TResultadoOperacaoContasFin;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    // TODO: Python SQLAlchemy -> session.query(UsuarioContaFin).filter_by(usucod=usucod).delete()
    Qry.SQL.Text := 'DELETE FROM usuario_conta_fin WHERE usucod = :pusucod';
    Qry.ParamByName('pusucod').AsString := Trim(AUsuCod);
    Qry.ExecSQL;
    Result := TResultadoOperacaoContasFin.CriarSucesso('Permissões revogadas com sucesso.', Qry.RowsAffected);
  except
    on E: Exception do
      Result := TResultadoOperacaoContasFin.CriarFalha('Erro ao revogar permissões: ' + E.Message);
  end;
  Qry.Free;
end;

function TUsuarioCtasFinRepositoryFireDAC.SalvarPermissoesUsuario(const AUsuCod: string; const AContas: TArray<string>): TResultadoOperacaoContasFin;
var
  QryDelete, QryInsert: TFDQuery;
  ContaCod: string;
  Inseridos: Integer;
begin
  Inseridos := 0;
  if (FConexao = nil) or (not FConexao.Connected) then
    Exit(TResultadoOperacaoContasFin.CriarFalha('Conexão com o banco de dados indisponível.'));

  FConexao.StartTransaction;
  QryDelete := TFDQuery.Create(nil);
  QryInsert := TFDQuery.Create(nil);
  try
    try
      QryDelete.Connection := FConexao;
      QryDelete.SQL.Text := 'DELETE FROM usuario_conta_fin WHERE usucod = :pusucod';
      QryDelete.ParamByName('pusucod').AsString := Trim(AUsuCod);
      QryDelete.ExecSQL;

      if Length(AContas) > 0 then
      begin
        QryInsert.Connection := FConexao;
        // Inserção idempotente parametrizada
        QryInsert.SQL.Text :=
          'INSERT INTO usuario_conta_fin (contafincod, usucod) ' +
          'VALUES (:pcontafincod, :pusucod)';

        for ContaCod in AContas do
        begin
          if Trim(ContaCod) = '' then
            Continue;
          QryInsert.ParamByName('pcontafincod').AsString := Trim(ContaCod);
          QryInsert.ParamByName('pusucod').AsString := Trim(AUsuCod);
          QryInsert.ExecSQL;
          Inc(Inseridos);
        end;
      end;

      FConexao.Commit;
      Result := TResultadoOperacaoContasFin.CriarSucesso(
        Format('Permissões atualizadas com sucesso (%d contas vinculadas).', [Inseridos]), Inseridos);
    except
      on E: Exception do
      begin
        if FConexao.InTransaction then
          FConexao.Rollback;
        Result := TResultadoOperacaoContasFin.CriarFalha('Falha na transação de permissões: ' + E.Message);
      end;
    end;
  finally
    QryDelete.Free;
    QryInsert.Free;
  end;
end;

end.
