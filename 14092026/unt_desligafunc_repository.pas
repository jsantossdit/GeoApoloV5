unit unt_desligafunc_repository;

interface

uses
  System.SysUtils, System.Classes, System.Generics.Collections,
  FireDAC.Comp.Client, FireDAC.Stan.Param, Data.DB,
  unt_desligafunc_types;

type
  IDesligaFuncRepository = interface
    ['{E430B2F1-92D0-4F8A-963F-5FE6D7D31289}']
    function ListarUsuariosPorStatus(const AStatus: string): TList<TUsuarioDesligamentoDTO>;
    function PesquisarUsuarios(const ACampo, AValor, AStatus: string): TList<TUsuarioDesligamentoDTO>;
    function ObterUsuario(const AUsuCod: string; out AUsuario: TUsuarioDesligamentoDTO): Boolean;
    function ExecutarDesligamento(const AUsuCod: string): TResultadoDesligamentoDTO;
    function ReativarUsuario(const AUsuCod: string): Boolean;
  end;

  TDesligaFuncRepositoryFireDAC = class(TInterfacedObject, IDesligaFuncRepository)
  private
    FConexao: TFDConnection;
  public
    constructor Create(AConexao: TFDConnection);
    function ListarUsuariosPorStatus(const AStatus: string): TList<TUsuarioDesligamentoDTO>;
    function PesquisarUsuarios(const ACampo, AValor, AStatus: string): TList<TUsuarioDesligamentoDTO>;
    function ObterUsuario(const AUsuCod: string; out AUsuario: TUsuarioDesligamentoDTO): Boolean;
    function ExecutarDesligamento(const AUsuCod: string): TResultadoDesligamentoDTO;
    function ReativarUsuario(const AUsuCod: string): Boolean;
  end;

implementation

{ TDesligaFuncRepositoryFireDAC }

constructor TDesligaFuncRepositoryFireDAC.Create(AConexao: TFDConnection);
begin
  inherited Create;
  FConexao := AConexao;
end;

function TDesligaFuncRepositoryFireDAC.ListarUsuariosPorStatus(const AStatus: string): TList<TUsuarioDesligamentoDTO>;
var
  Qry: TFDQuery;
  Item: TUsuarioDesligamentoDTO;
begin
  Result := TList<TUsuarioDesligamentoDTO>.Create;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    // TODO: Python SQLAlchemy -> session.query(Usuario).filter(Usuario.usustat == status).order_by(Usuario.usucod)
    Qry.SQL.Text :=
      'SELECT usucod, usunome, usudepto, usustat ' +
      'FROM usuario WITH (NOLOCK) ' +
      'WHERE usustat = :pstatus ' +
      'ORDER BY usucod ASC';
    Qry.ParamByName('pstatus').AsString := Trim(AStatus);
    Qry.Open;

    while not Qry.Eof do
    begin
      Item.UsuCod := Trim(Qry.FieldByName('usucod').AsString);
      Item.UsuNome := Trim(Qry.FieldByName('usunome').AsString);
      Item.UsuDepto := Trim(Qry.FieldByName('usudepto').AsString);
      Item.UsuStat := Trim(Qry.FieldByName('usustat').AsString);
      Result.Add(Item);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
end;

function TDesligaFuncRepositoryFireDAC.PesquisarUsuarios(const ACampo, AValor, AStatus: string): TList<TUsuarioDesligamentoDTO>;
var
  Qry: TFDQuery;
  Item: TUsuarioDesligamentoDTO;
  CampoValido: string;
begin
  Result := TList<TUsuarioDesligamentoDTO>.Create;
  // Sanitização de campo para prevenir injeção
  if SameText(ACampo, 'usunome') then
    CampoValido := 'usunome'
  else if SameText(ACampo, 'usudepto') then
    CampoValido := 'usudepto'
  else
    CampoValido := 'usucod';

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    Qry.SQL.Text :=
      'SELECT usucod, usunome, usudepto, usustat ' +
      'FROM usuario WITH (NOLOCK) ' +
      Format('WHERE %s LIKE :pvalor ', [CampoValido]);

    if Trim(AStatus) <> '' then
      Qry.SQL.Add('AND usustat = :pstatus ');

    Qry.SQL.Add('ORDER BY ' + CampoValido + ' ASC');

    Qry.ParamByName('pvalor').AsString := '%' + Trim(AValor) + '%';
    if Trim(AStatus) <> '' then
      Qry.ParamByName('pstatus').AsString := Trim(AStatus);

    Qry.Open;
    while not Qry.Eof do
    begin
      Item.UsuCod := Trim(Qry.FieldByName('usucod').AsString);
      Item.UsuNome := Trim(Qry.FieldByName('usunome').AsString);
      Item.UsuDepto := Trim(Qry.FieldByName('usudepto').AsString);
      Item.UsuStat := Trim(Qry.FieldByName('usustat').AsString);
      Result.Add(Item);
      Qry.Next;
    end;
  finally
    Qry.Free;
  end;
end;

function TDesligaFuncRepositoryFireDAC.ObterUsuario(const AUsuCod: string; out AUsuario: TUsuarioDesligamentoDTO): Boolean;
var
  Qry: TFDQuery;
begin
  Result := False;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    Qry.SQL.Text :=
      'SELECT usucod, usunome, usudepto, usustat ' +
      'FROM usuario WITH (NOLOCK) ' +
      'WHERE usucod = :pusucod';
    Qry.ParamByName('pusucod').AsString := Trim(AUsuCod);
    Qry.Open;

    if not Qry.Eof then
    begin
      AUsuario.UsuCod := Trim(Qry.FieldByName('usucod').AsString);
      AUsuario.UsuNome := Trim(Qry.FieldByName('usunome').AsString);
      AUsuario.UsuDepto := Trim(Qry.FieldByName('usudepto').AsString);
      AUsuario.UsuStat := Trim(Qry.FieldByName('usustat').AsString);
      Result := True;
    end;
  finally
    Qry.Free;
  end;
end;

function TDesligaFuncRepositoryFireDAC.ExecutarDesligamento(const AUsuCod: string): TResultadoDesligamentoDTO;
var
  Qry: TFDQuery;
begin
  if (FConexao = nil) or (not FConexao.Connected) then
    Exit(TResultadoDesligamentoDTO.CriarFalha('Banco de dados desconectado.'));

  FConexao.StartTransaction;
  Qry := TFDQuery.Create(nil);
  try
    try
      Qry.Connection := FConexao;

      // 1. Remove vinculos com Entidades
      Qry.SQL.Text := 'DELETE FROM usuario_ent WHERE usucod = :pusucod';
      Qry.ParamByName('pusucod').AsString := Trim(AUsuCod);
      Qry.ExecSQL;
      Result.VinculosEntidadesRemovidos := Qry.RowsAffected;

      // 2. Remove vinculos com Categorias
      Qry.SQL.Text := 'DELETE FROM usuario_categ WHERE usucod = :pusucod';
      Qry.ParamByName('pusucod').AsString := Trim(AUsuCod);
      Qry.ExecSQL;
      Result.VinculosCategoriasRemovidos := Qry.RowsAffected;

      // 3. Remove permissões de Relatórios
      Qry.SQL.Text := 'DELETE FROM dir_rel_usuario WHERE usucod = :pusucod';
      Qry.ParamByName('pusucod').AsString := Trim(AUsuCod);
      Qry.ExecSQL;
      Result.PermissoesRelatoriosRemovidas := Qry.RowsAffected;

      // 4. Remove permissões em Contas Financeiras
      Qry.SQL.Text := 'DELETE FROM usuario_conta_fin WHERE usucod = :pusucod';
      Qry.ParamByName('pusucod').AsString := Trim(AUsuCod);
      Qry.ExecSQL;
      Result.PermissoesContasFinRemovidas := Qry.RowsAffected;

      // 5. Atualiza o status do Usuário para 'Desligado'
      Qry.SQL.Text := 'UPDATE usuario SET usustat = :pstatus WHERE usucod = :pusucod';
      Qry.ParamByName('pstatus').AsString := 'Desligado';
      Qry.ParamByName('pusucod').AsString := Trim(AUsuCod);
      Qry.ExecSQL;

      FConexao.Commit;
      Result.Sucesso := True;
      Result.Mensagem := Format('Usuário %s desligado com sucesso. Vínculos revogados.', [AUsuCod]);
    except
      on E: Exception do
      begin
        if FConexao.InTransaction then
          FConexao.Rollback;
        Result := TResultadoDesligamentoDTO.CriarFalha('Falha ao executar desligamento: ' + E.Message);
      end;
    end;
  finally
    Qry.Free;
  end;
end;

function TDesligaFuncRepositoryFireDAC.ReativarUsuario(const AUsuCod: string): Boolean;
var
  Qry: TFDQuery;
begin
  Result := False;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConexao;
    Qry.SQL.Text := 'UPDATE usuario SET usustat = :pstatus WHERE usucod = :pusucod';
    Qry.ParamByName('pstatus').AsString := 'Ativo';
    Qry.ParamByName('pusucod').AsString := Trim(AUsuCod);
    Qry.ExecSQL;
    Result := Qry.RowsAffected > 0;
  finally
    Qry.Free;
  end;
end;

end.
