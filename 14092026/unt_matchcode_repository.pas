unit unt_matchcode_repository;

interface

uses
  System.SysUtils, System.Classes, Data.DB, FireDAC.Comp.Client,
  FireDAC.Stan.Param, FireDAC.Stan.Option, unt_matchcode_types;

type
  IMatchCodeRepository = interface
    ['{7B4C8A91-2E3D-4F15-9923-3D4E5F6A7B8C}']
    function ObterNomeUsuario(const AUsucod: string): string;
    function ObterNomeEntidade(const AEntcod: string): string;
    function UnificarUsuarios(const AOrigem, ADestino: string): TResultadoMatchCode;
    function UnificarEntidades(const AOrigem, ADestino: string): TResultadoMatchCode;
  end;

  TMatchCodeRepository = class(TInterfacedObject, IMatchCodeRepository)
  private
    FConn: TFDConnection;
  public
    constructor Create(AConnection: TFDConnection);
    function ObterNomeUsuario(const AUsucod: string): string;
    function ObterNomeEntidade(const AEntcod: string): string;
    function UnificarUsuarios(const AOrigem, ADestino: string): TResultadoMatchCode;
    function UnificarEntidades(const AOrigem, ADestino: string): TResultadoMatchCode;
  end;

implementation

constructor TMatchCodeRepository.Create(AConnection: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConnection) then
    raise Exception.Create('TMatchCodeRepository: TFDConnection é obrigatória.');
  FConn := AConnection;
end;

function TMatchCodeRepository.ObterNomeUsuario(const AUsucod: string): string;
var
  Qry: TFDQuery;
begin
  Result := '';
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT nome_completo FROM USER_geoapolo_usuarios WITH (NOLOCK) WHERE usucod = :pUsucod';
    Qry.ParamByName('pUsucod').AsString := AUsucod;
    Qry.Open;
    if not Qry.IsEmpty then
      Result := Qry.Fields[0].AsString;
  finally
    Qry.Free;
  end;
end;

function TMatchCodeRepository.ObterNomeEntidade(const AEntcod: string): string;
var
  Qry: TFDQuery;
begin
  Result := '';
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT entnome FROM entidade WITH (NOLOCK) WHERE entcod = :pEntcod';
    Qry.ParamByName('pEntcod').AsString := AEntcod;
    Qry.Open;
    if not Qry.IsEmpty then
      Result := Qry.Fields[0].AsString;
  finally
    Qry.Free;
  end;
end;

function TMatchCodeRepository.UnificarUsuarios(const AOrigem, ADestino: string): TResultadoMatchCode;
var
  Qry: TFDQuery;
  Total: Integer;
begin
  Result.Sucesso := False;
  Result.Mensagem := '';
  Result.RegistrosMigrados := 0;
  Total := 0;

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    FConn.StartTransaction;
    try
      // 1. Grupos
      Qry.SQL.Text :=
        'DELETE FROM USER_geoapolo_grupousuario WHERE usucod = :pOrig AND codigo_grupo IN ' +
        '(SELECT codigo_grupo FROM USER_geoapolo_grupousuario WHERE usucod = :pDest)';
      Qry.ParamByName('pOrig').AsString := AOrigem;
      Qry.ParamByName('pDest').AsString := ADestino;
      Qry.ExecSQL;

      Qry.SQL.Text := 'UPDATE USER_geoapolo_grupousuario SET usucod = :pDest WHERE usucod = :pOrig';
      Qry.ParamByName('pOrig').AsString := AOrigem;
      Qry.ParamByName('pDest').AsString := ADestino;
      Qry.ExecSQL;
      Inc(Total, Qry.RowsAffected);

      // 2. Sistemas
      Qry.SQL.Text :=
        'DELETE FROM USER_geoapolo_usuariossistemas WHERE usucod = :pOrig AND codigo_sistema IN ' +
        '(SELECT codigo_sistema FROM USER_geoapolo_usuariossistemas WHERE usucod = :pDest)';
      Qry.ParamByName('pOrig').AsString := AOrigem;
      Qry.ParamByName('pDest').AsString := ADestino;
      Qry.ExecSQL;

      Qry.SQL.Text := 'UPDATE USER_geoapolo_usuariossistemas SET usucod = :pDest WHERE usucod = :pOrig';
      Qry.ParamByName('pOrig').AsString := AOrigem;
      Qry.ParamByName('pDest').AsString := ADestino;
      Qry.ExecSQL;
      Inc(Total, Qry.RowsAffected);

      // 3. Consultas
      Qry.SQL.Text :=
        'DELETE FROM USER_geoapolo_permissaoconsulta WHERE usucod = :pOrig AND codigo_consulta IN ' +
        '(SELECT codigo_consulta FROM USER_geoapolo_permissaoconsulta WHERE usucod = :pDest)';
      Qry.ParamByName('pOrig').AsString := AOrigem;
      Qry.ParamByName('pDest').AsString := ADestino;
      Qry.ExecSQL;

      Qry.SQL.Text := 'UPDATE USER_geoapolo_permissaoconsulta SET usucod = :pDest WHERE usucod = :pOrig';
      Qry.ParamByName('pOrig').AsString := AOrigem;
      Qry.ParamByName('pDest').AsString := ADestino;
      Qry.ExecSQL;
      Inc(Total, Qry.RowsAffected);

      // 4. Remove origem
      Qry.SQL.Text := 'DELETE FROM USER_geoapolo_usuarios WHERE usucod = :pOrig';
      Qry.ParamByName('pOrig').AsString := AOrigem;
      Qry.ExecSQL;

      FConn.Commit;
      Result.Sucesso := True;
      Result.RegistrosMigrados := Total;
      Result.Mensagem := Format('Usuário "%s" mesclado com sucesso no usuário "%s".', [AOrigem, ADestino]);
    except
      on E: Exception do
      begin
        FConn.Rollback;
        Result.Sucesso := False;
        Result.Mensagem := 'Falha na unificação: ' + E.Message;
      end;
    end;
  finally
    Qry.Free;
  end;
end;

function TMatchCodeRepository.UnificarEntidades(const AOrigem, ADestino: string): TResultadoMatchCode;
var
  Qry: TFDQuery;
  Total: Integer;
begin
  Result.Sucesso := False;
  Result.Mensagem := '';
  Result.RegistrosMigrados := 0;
  Total := 0;

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    FConn.StartTransaction;
    try
      // Categorias da entidade
      Qry.SQL.Text :=
        'DELETE FROM ent_categ WHERE entcod = :pOrig AND categcodestr IN ' +
        '(SELECT categcodestr FROM ent_categ WHERE entcod = :pDest)';
      Qry.ParamByName('pOrig').AsString := AOrigem;
      Qry.ParamByName('pDest').AsString := ADestino;
      Qry.ExecSQL;

      Qry.SQL.Text := 'UPDATE ent_categ SET entcod = :pDest WHERE entcod = :pOrig';
      Qry.ParamByName('pOrig').AsString := AOrigem;
      Qry.ParamByName('pDest').AsString := ADestino;
      Qry.ExecSQL;
      Inc(Total, Qry.RowsAffected);

      // Remove u_entidade origem
      Qry.SQL.Text := 'DELETE FROM u_entidade WHERE entcod = :pOrig';
      Qry.ParamByName('pOrig').AsString := AOrigem;
      Qry.ExecSQL;

      // Remove entidade origem
      Qry.SQL.Text := 'DELETE FROM entidade WHERE entcod = :pOrig';
      Qry.ParamByName('pOrig').AsString := AOrigem;
      Qry.ExecSQL;

      FConn.Commit;
      Result.Sucesso := True;
      Result.RegistrosMigrados := Total;
      Result.Mensagem := Format('Entidade "%s" mesclada com sucesso em "%s".', [AOrigem, ADestino]);
    except
      on E: Exception do
      begin
        FConn.Rollback;
        Result.Sucesso := False;
        Result.Mensagem := 'Falha na unificação: ' + E.Message;
      end;
    end;
  finally
    Qry.Free;
  end;
end;

end.
