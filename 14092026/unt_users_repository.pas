unit unt_users_repository;

interface

uses
  System.SysUtils, System.Classes, Data.DB, FireDAC.Comp.Client,
  FireDAC.Stan.Param, FireDAC.Stan.Option, unt_users_types;

type
  IUsuariosRepository = interface
    ['{8F4E6D2B-5B2C-4A8E-9801-1C34A981245B}']
    function ListarUsuarios(const AFiltroNome: string = ''; AApenasAtivos: Boolean = True): TArray<TUsuarioDTO>;
    function ObterUsuarioPorUsucod(const AUsucod: string): TUsuarioDTO;
    function ObterUsuarioPorLogin(const ALogin: string): TUsuarioDTO;
    function SalvarUsuario(const AUsuario: TUsuarioDTO): Boolean;
    function ExcluirUsuario(const AUsucod: string): Boolean;

    function ListarDepartamentos(const AEmpCod: string = ''): TArray<TDepartamentoDTO>;
    function ListarSistemas: TArray<TSistemaDTO>;
    function ListarSistemasDoUsuario(const AUsucod: string): TArray<TSistemaDTO>;
    function VincularSistema(const AUsucod, ACodigoSistema: string): Boolean;
    function DesvincularSistema(const AUsucod, ACodigoSistema: string): Boolean;

    function ListarGrupos: TArray<TGrupoUsuarioDTO>;
    function SalvarGrupo(const ACodigoGrupo, ADescricao: string): Boolean;
    function ExcluirGrupo(const ACodigoGrupo: string): Boolean;
    function ListarUsuariosDoGrupo(const ACodigoGrupo: string): TArray<TVinculoGrupoUsuarioDTO>;
    function VincularUsuarioGrupo(const ACodigoGrupo, AUsucod: string): Boolean;
    function DesvincularUsuarioGrupo(const ACodigoGrupo, AUsucod: string): Boolean;

    function ListarObjetosPerfil(const ACodigoGrupo: string; const ACategoria: string = ''): TArray<TPerfilItemDTO>;
    function ListarCategoriasObjetos: TArray<string>;
    function AtualizarStatusAcesso(const ACodigoGrupo, ACodigoObjeto, AStatus: string): Boolean;
  end;

  TUsuariosRepository = class(TInterfacedObject, IUsuariosRepository)
  private
    FConn: TFDConnection;
  public
    constructor Create(AConnection: TFDConnection);

    function ListarUsuarios(const AFiltroNome: string = ''; AApenasAtivos: Boolean = True): TArray<TUsuarioDTO>;
    function ObterUsuarioPorUsucod(const AUsucod: string): TUsuarioDTO;
    function ObterUsuarioPorLogin(const ALogin: string): TUsuarioDTO;
    function SalvarUsuario(const AUsuario: TUsuarioDTO): Boolean;
    function ExcluirUsuario(const AUsucod: string): Boolean;

    function ListarDepartamentos(const AEmpCod: string = ''): TArray<TDepartamentoDTO>;
    function ListarSistemas: TArray<TSistemaDTO>;
    function ListarSistemasDoUsuario(const AUsucod: string): TArray<TSistemaDTO>;
    function VincularSistema(const AUsucod, ACodigoSistema: string): Boolean;
    function DesvincularSistema(const AUsucod, ACodigoSistema: string): Boolean;

    function ListarGrupos: TArray<TGrupoUsuarioDTO>;
    function SalvarGrupo(const ACodigoGrupo, ADescricao: string): Boolean;
    function ExcluirGrupo(const ACodigoGrupo: string): Boolean;
    function ListarUsuariosDoGrupo(const ACodigoGrupo: string): TArray<TVinculoGrupoUsuarioDTO>;
    function VincularUsuarioGrupo(const ACodigoGrupo, AUsucod: string): Boolean;
    function DesvincularUsuarioGrupo(const ACodigoGrupo, AUsucod: string): Boolean;

    function ListarObjetosPerfil(const ACodigoGrupo: string; const ACategoria: string = ''): TArray<TPerfilItemDTO>;
    function ListarCategoriasObjetos: TArray<string>;
    function AtualizarStatusAcesso(const ACodigoGrupo, ACodigoObjeto, AStatus: string): Boolean;
  end;

implementation

constructor TUsuariosRepository.Create(AConnection: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConnection) then
    raise Exception.Create('TUsuariosRepository: TFDConnection é obrigatória.');
  FConn := AConnection;
end;

function TUsuariosRepository.ListarUsuarios(const AFiltroNome: string; AApenasAtivos: Boolean): TArray<TUsuarioDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TUsuarioDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT u.codigo_usuario, u.usucod, u.nome_completo, u.flagativo, u.login, u.email, ' +
      '       CONVERT(VARCHAR(10), u.data_nascimento, 120) AS data_nasc_str, ' +
      '       u.codigo_departamento, d.nome_departamento, u.usucod_apolo, u.senha_alvo ' +
      'FROM USER_geoapolo_usuarios u WITH (NOLOCK) ' +
      'LEFT JOIN USER_geoapolo_departamentos d WITH (NOLOCK) ON u.codigo_departamento = d.codigo_departamento ' +
      'WHERE 1=1 ';

    if AApenasAtivos then
      Qry.SQL.Text := Qry.SQL.Text + 'AND u.flagativo IN (''A'', ''S'') ';

    if Trim(AFiltroNome) <> '' then
    begin
      Qry.SQL.Text := Qry.SQL.Text + 'AND (u.nome_completo LIKE :pNome OR u.login LIKE :pNome) ';
      Qry.ParamByName('pNome').AsString := '%' + Trim(AFiltroNome) + '%';
    end;

    Qry.SQL.Text := Qry.SQL.Text + 'ORDER BY u.nome_completo ASC';
    Qry.Open;

    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].CodigoUsuario      := Qry.FieldByName('codigo_usuario').AsString;
      Res[Idx].Usucod             := Qry.FieldByName('usucod').AsString;
      Res[Idx].NomeCompleto       := Qry.FieldByName('nome_completo').AsString;
      Res[Idx].FlagAtivo          := Qry.FieldByName('flagativo').AsString;
      Res[Idx].Login              := Qry.FieldByName('login').AsString;
      Res[Idx].Email              := Qry.FieldByName('email').AsString;
      Res[Idx].DataNascimento     := Qry.FieldByName('data_nasc_str').AsString;
      Res[Idx].CodigoDepartamento := Qry.FieldByName('codigo_departamento').AsString;
      Res[Idx].NomeDepartamento   := Qry.FieldByName('nome_departamento').AsString;
      Res[Idx].UsucodApolo        := Qry.FieldByName('usucod_apolo').AsString;
      Res[Idx].SenhaAlvo          := Qry.FieldByName('senha_alvo').AsString;
      Qry.Next;
    end;
    Result := Res;
  finally
    Qry.Free;
  end;
end;

function TUsuariosRepository.ObterUsuarioPorUsucod(const AUsucod: string): TUsuarioDTO;
var
  Qry: TFDQuery;
begin
  FillChar(Result, SizeOf(Result), 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT u.codigo_usuario, u.usucod, u.nome_completo, u.flagativo, u.login, u.email, ' +
      '       CONVERT(VARCHAR(10), u.data_nascimento, 120) AS data_nasc_str, ' +
      '       u.codigo_departamento, d.nome_departamento, u.usucod_apolo, u.senha_alvo ' +
      'FROM USER_geoapolo_usuarios u WITH (NOLOCK) ' +
      'LEFT JOIN USER_geoapolo_departamentos d WITH (NOLOCK) ON u.codigo_departamento = d.codigo_departamento ' +
      'WHERE u.usucod = :pUsucod';
    Qry.ParamByName('pUsucod').AsString := AUsucod;
    Qry.Open;
    if not Qry.IsEmpty then
    begin
      Result.CodigoUsuario      := Qry.FieldByName('codigo_usuario').AsString;
      Result.Usucod             := Qry.FieldByName('usucod').AsString;
      Result.NomeCompleto       := Qry.FieldByName('nome_completo').AsString;
      Result.FlagAtivo          := Qry.FieldByName('flagativo').AsString;
      Result.Login              := Qry.FieldByName('login').AsString;
      Result.Email              := Qry.FieldByName('email').AsString;
      Result.DataNascimento     := Qry.FieldByName('data_nasc_str').AsString;
      Result.CodigoDepartamento := Qry.FieldByName('codigo_departamento').AsString;
      Result.NomeDepartamento   := Qry.FieldByName('nome_departamento').AsString;
      Result.UsucodApolo        := Qry.FieldByName('usucod_apolo').AsString;
      Result.SenhaAlvo          := Qry.FieldByName('senha_alvo').AsString;
    end;
  finally
    Qry.Free;
  end;
end;

function TUsuariosRepository.ObterUsuarioPorLogin(const ALogin: string): TUsuarioDTO;
var
  Qry: TFDQuery;
begin
  FillChar(Result, SizeOf(Result), 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT u.codigo_usuario, u.usucod, u.nome_completo, u.flagativo, u.login, u.email, ' +
      '       CONVERT(VARCHAR(10), u.data_nascimento, 120) AS data_nasc_str, ' +
      '       u.codigo_departamento, d.nome_departamento, u.usucod_apolo, u.senha_alvo ' +
      'FROM USER_geoapolo_usuarios u WITH (NOLOCK) ' +
      'LEFT JOIN USER_geoapolo_departamentos d WITH (NOLOCK) ON u.codigo_departamento = d.codigo_departamento ' +
      'WHERE u.login = :pLogin';
    Qry.ParamByName('pLogin').AsString := ALogin;
    Qry.Open;
    if not Qry.IsEmpty then
    begin
      Result.CodigoUsuario      := Qry.FieldByName('codigo_usuario').AsString;
      Result.Usucod             := Qry.FieldByName('usucod').AsString;
      Result.NomeCompleto       := Qry.FieldByName('nome_completo').AsString;
      Result.FlagAtivo          := Qry.FieldByName('flagativo').AsString;
      Result.Login              := Qry.FieldByName('login').AsString;
      Result.Email              := Qry.FieldByName('email').AsString;
      Result.DataNascimento     := Qry.FieldByName('data_nasc_str').AsString;
      Result.CodigoDepartamento := Qry.FieldByName('codigo_departamento').AsString;
      Result.NomeDepartamento   := Qry.FieldByName('nome_departamento').AsString;
      Result.UsucodApolo        := Qry.FieldByName('usucod_apolo').AsString;
      Result.SenhaAlvo          := Qry.FieldByName('senha_alvo').AsString;
    end;
  finally
    Qry.Free;
  end;
end;

function TUsuariosRepository.SalvarUsuario(const AUsuario: TUsuarioDTO): Boolean;
var
  Qry: TFDQuery;
  Existe: Boolean;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    FConn.StartTransaction;
    try
      Qry.SQL.Text := 'SELECT COUNT(*) FROM USER_geoapolo_usuarios WHERE usucod = :pUsucod';
      Qry.ParamByName('pUsucod').AsString := AUsuario.Usucod;
      Qry.Open;
      Existe := Qry.Fields[0].AsInteger > 0;
      Qry.Close;

      if Existe then
      begin
        Qry.SQL.Text :=
          'UPDATE USER_geoapolo_usuarios SET ' +
          '  nome_completo = :pNome, flagativo = :pAtivo, login = :pLogin, email = :pEmail, ' +
          '  codigo_departamento = :pDepto, usucod_apolo = :pApolo, senha_alvo = :pSenhaAlvo ' +
          'WHERE usucod = :pUsucod';
      end
      else
      begin
        Qry.SQL.Text :=
          'INSERT INTO USER_geoapolo_usuarios (codigo_usuario, usucod, nome_completo, flagativo, login, email, codigo_departamento, usucod_apolo, senha_alvo) ' +
          'VALUES (:pCod, :pUsucod, :pNome, :pAtivo, :pLogin, :pEmail, :pDepto, :pApolo, :pSenhaAlvo)';
        Qry.ParamByName('pCod').AsString := AUsuario.CodigoUsuario;
      end;

      Qry.ParamByName('pUsucod').AsString    := AUsuario.Usucod;
      Qry.ParamByName('pNome').AsString      := AUsuario.NomeCompleto;
      Qry.ParamByName('pAtivo').AsString     := AUsuario.FlagAtivo;
      Qry.ParamByName('pLogin').AsString     := AUsuario.Login;
      Qry.ParamByName('pEmail').AsString     := AUsuario.Email;
      Qry.ParamByName('pDepto').AsString     := AUsuario.CodigoDepartamento;
      Qry.ParamByName('pApolo').AsString     := AUsuario.UsucodApolo;
      Qry.ParamByName('pSenhaAlvo').AsString := AUsuario.SenhaAlvo;
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

function TUsuariosRepository.ExcluirUsuario(const AUsucod: string): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    FConn.StartTransaction;
    try
      // Remove vínculos antes
      Qry.SQL.Text := 'DELETE FROM USER_geoapolo_usuariossistemas WHERE usucod = :pUsucod';
      Qry.ParamByName('pUsucod').AsString := AUsucod;
      Qry.ExecSQL;

      Qry.SQL.Text := 'DELETE FROM USER_geoapolo_grupousuario WHERE usucod = :pUsucod';
      Qry.ParamByName('pUsucod').AsString := AUsucod;
      Qry.ExecSQL;

      Qry.SQL.Text := 'DELETE FROM USER_geoapolo_usuarios WHERE usucod = :pUsucod';
      Qry.ParamByName('pUsucod').AsString := AUsucod;
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

function TUsuariosRepository.ListarDepartamentos(const AEmpCod: string): TArray<TDepartamentoDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TDepartamentoDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT ugd.codigo_departamento, ugd.nome_departamento, ugd.empcod, uge.empnome, ugd.flagativo ' +
      'FROM USER_geoapolo_departamentos ugd WITH (NOLOCK) ' +
      'LEFT JOIN USER_geoapolo_empresas uge WITH (NOLOCK) ON ugd.empcod = uge.empcod ' +
      'WHERE ugd.flagativo = ''S'' ';

    if Trim(AEmpCod) <> '' then
    begin
      Qry.SQL.Text := Qry.SQL.Text + 'AND ugd.empcod = :pEmpCod ';
      Qry.ParamByName('pEmpCod').AsString := AEmpCod;
    end;

    Qry.SQL.Text := Qry.SQL.Text + 'ORDER BY ugd.nome_departamento ASC';
    Qry.Open;

    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].CodigoDepartamento := Qry.FieldByName('codigo_departamento').AsString;
      Res[Idx].NomeDepartamento   := Qry.FieldByName('nome_departamento').AsString;
      Res[Idx].EmpCod             := Qry.FieldByName('empcod').AsString;
      Res[Idx].EmpNome            := Qry.FieldByName('empnome').AsString;
      Res[Idx].FlagAtivo          := Qry.FieldByName('flagativo').AsString;
      Qry.Next;
    end;
    Result := Res;
  finally
    Qry.Free;
  end;
end;

function TUsuariosRepository.ListarSistemas: TArray<TSistemaDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TSistemaDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT codigo_sistema, descricao, ISNULL(sigla, '''') AS sigla FROM USER_geoapolo_sistemas WITH (NOLOCK) ORDER BY descricao ASC';
    Qry.Open;
    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].CodigoSistema := Qry.FieldByName('codigo_sistema').AsString;
      Res[Idx].Descricao     := Qry.FieldByName('descricao').AsString;
      Res[Idx].Sigla         := Qry.FieldByName('sigla').AsString;
      Qry.Next;
    end;
    Result := Res;
  finally
    Qry.Free;
  end;
end;

function TUsuariosRepository.ListarSistemasDoUsuario(const AUsucod: string): TArray<TSistemaDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TSistemaDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT s.codigo_sistema, s.descricao, ISNULL(s.sigla, '''') AS sigla ' +
      'FROM USER_geoapolo_usuariossistemas us WITH (NOLOCK) ' +
      'INNER JOIN USER_geoapolo_sistemas s WITH (NOLOCK) ON us.codigo_sistema = s.codigo_sistema ' +
      'WHERE us.usucod = :pUsucod ORDER BY s.descricao ASC';
    Qry.ParamByName('pUsucod').AsString := AUsucod;
    Qry.Open;
    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].CodigoSistema := Qry.FieldByName('codigo_sistema').AsString;
      Res[Idx].Descricao     := Qry.FieldByName('descricao').AsString;
      Res[Idx].Sigla         := Qry.FieldByName('sigla').AsString;
      Qry.Next;
    end;
    Result := Res;
  finally
    Qry.Free;
  end;
end;

function TUsuariosRepository.VincularSistema(const AUsucod, ACodigoSistema: string): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_usuariossistemas WHERE usucod = :pUsucod AND codigo_sistema = :pCod) ' +
      'BEGIN ' +
      '  INSERT INTO USER_geoapolo_usuariossistemas (usucod, codigo_sistema) VALUES (:pUsucod, :pCod); ' +
      'END';
    Qry.ParamByName('pUsucod').AsString := AUsucod;
    Qry.ParamByName('pCod').AsString    := ACodigoSistema;
    Qry.ExecSQL;
    Result := True;
  finally
    Qry.Free;
  end;
end;

function TUsuariosRepository.DesvincularSistema(const AUsucod, ACodigoSistema: string): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'DELETE FROM USER_geoapolo_usuariossistemas WHERE usucod = :pUsucod AND codigo_sistema = :pCod';
    Qry.ParamByName('pUsucod').AsString := AUsucod;
    Qry.ParamByName('pCod').AsString    := ACodigoSistema;
    Qry.ExecSQL;
    Result := True;
  finally
    Qry.Free;
  end;
end;

function TUsuariosRepository.ListarGrupos: TArray<TGrupoUsuarioDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TGrupoUsuarioDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT g.codigo_grupo, g.descricao, COUNT(gu.usucod) AS total_usuarios ' +
      'FROM USER_geoapolo_grupo g WITH (NOLOCK) ' +
      'LEFT JOIN USER_geoapolo_grupousuario gu WITH (NOLOCK) ON g.codigo_grupo = gu.codigo_grupo ' +
      'GROUP BY g.codigo_grupo, g.descricao ' +
      'ORDER BY g.descricao ASC';
    Qry.Open;
    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].CodigoGrupo   := Qry.FieldByName('codigo_grupo').AsString;
      Res[Idx].Descricao     := Qry.FieldByName('descricao').AsString;
      Res[Idx].TotalUsuarios := Qry.FieldByName('total_usuarios').AsInteger;
      Qry.Next;
    end;
    Result := Res;
  finally
    Qry.Free;
  end;
end;

function TUsuariosRepository.SalvarGrupo(const ACodigoGrupo, ADescricao: string): Boolean;
var
  Qry: TFDQuery;
  Existe: Boolean;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT COUNT(*) FROM USER_geoapolo_grupo WHERE codigo_grupo = :pCod';
    Qry.ParamByName('pCod').AsString := ACodigoGrupo;
    Qry.Open;
    Existe := Qry.Fields[0].AsInteger > 0;
    Qry.Close;

    if Existe then
    begin
      Qry.SQL.Text := 'UPDATE USER_geoapolo_grupo SET descricao = :pDesc WHERE codigo_grupo = :pCod';
    end
    else
    begin
      Qry.SQL.Text := 'INSERT INTO USER_geoapolo_grupo (codigo_grupo, descricao) VALUES (:pCod, :pDesc)';
    end;
    Qry.ParamByName('pCod').AsString  := ACodigoGrupo;
    Qry.ParamByName('pDesc').AsString := ADescricao;
    Qry.ExecSQL;
    Result := True;
  finally
    Qry.Free;
  end;
end;

function TUsuariosRepository.ExcluirGrupo(const ACodigoGrupo: string): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    FConn.StartTransaction;
    try
      Qry.SQL.Text := 'DELETE FROM USER_geoapolo_grupobjetos WHERE codigo_grupo = :pCod';
      Qry.ParamByName('pCod').AsString := ACodigoGrupo;
      Qry.ExecSQL;

      Qry.SQL.Text := 'DELETE FROM USER_geoapolo_grupousuario WHERE codigo_grupo = :pCod';
      Qry.ParamByName('pCod').AsString := ACodigoGrupo;
      Qry.ExecSQL;

      Qry.SQL.Text := 'DELETE FROM USER_geoapolo_grupo WHERE codigo_grupo = :pCod';
      Qry.ParamByName('pCod').AsString := ACodigoGrupo;
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

function TUsuariosRepository.ListarUsuariosDoGrupo(const ACodigoGrupo: string): TArray<TVinculoGrupoUsuarioDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TVinculoGrupoUsuarioDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT gu.codigo_grupo, g.descricao AS nome_grupo, u.usucod, u.login, u.nome_completo ' +
      'FROM USER_geoapolo_grupousuario gu WITH (NOLOCK) ' +
      'INNER JOIN USER_geoapolo_grupo g WITH (NOLOCK) ON gu.codigo_grupo = g.codigo_grupo ' +
      'INNER JOIN USER_geoapolo_usuarios u WITH (NOLOCK) ON gu.usucod = u.usucod ' +
      'WHERE gu.codigo_grupo = :pCod ' +
      'ORDER BY u.nome_completo ASC';
    Qry.ParamByName('pCod').AsString := ACodigoGrupo;
    Qry.Open;
    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].CodigoGrupo  := Qry.FieldByName('codigo_grupo').AsString;
      Res[Idx].NomeGrupo    := Qry.FieldByName('nome_grupo').AsString;
      Res[Idx].Usucod       := Qry.FieldByName('usucod').AsString;
      Res[Idx].Login        := Qry.FieldByName('login').AsString;
      Res[Idx].NomeCompleto := Qry.FieldByName('nome_completo').AsString;
      Qry.Next;
    end;
    Result := Res;
  finally
    Qry.Free;
  end;
end;

function TUsuariosRepository.VincularUsuarioGrupo(const ACodigoGrupo, AUsucod: string): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_grupousuario WHERE codigo_grupo = :pCod AND usucod = :pUsucod) ' +
      'BEGIN ' +
      '  INSERT INTO USER_geoapolo_grupousuario (codigo_grupo, usucod) VALUES (:pCod, :pUsucod); ' +
      'END';
    Qry.ParamByName('pCod').AsString    := ACodigoGrupo;
    Qry.ParamByName('pUsucod').AsString := AUsucod;
    Qry.ExecSQL;
    Result := True;
  finally
    Qry.Free;
  end;
end;

function TUsuariosRepository.DesvincularUsuarioGrupo(const ACodigoGrupo, AUsucod: string): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'DELETE FROM USER_geoapolo_grupousuario WHERE codigo_grupo = :pCod AND usucod = :pUsucod';
    Qry.ParamByName('pCod').AsString    := ACodigoGrupo;
    Qry.ParamByName('pUsucod').AsString := AUsucod;
    Qry.ExecSQL;
    Result := True;
  finally
    Qry.Free;
  end;
end;

function TUsuariosRepository.ListarObjetosPerfil(const ACodigoGrupo: string; const ACategoria: string): TArray<TPerfilItemDTO>;
var
  Qry: TFDQuery;
  Res: TArray<TPerfilItemDTO>;
  Idx: Integer;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT o.codigo_objeto, o.nome_objeto, ISNULL(o.nome_amigavel, o.nome_objeto) AS nome_amigavel, ' +
      '       ISNULL(o.categoria, ''Geral'') AS categoria, ' +
      '       ISNULL(go.statusacesso, ''N'') AS statusacesso ' +
      'FROM USER_geoapolo_objetos o WITH (NOLOCK) ' +
      'LEFT JOIN USER_geoapolo_grupobjetos go WITH (NOLOCK) ON o.codigo_objeto = go.codigo_objeto AND go.codigo_grupo = :pCodGrupo ' +
      'WHERE 1=1 ';

    if Trim(ACategoria) <> '' then
    begin
      Qry.SQL.Text := Qry.SQL.Text + 'AND o.categoria = :pCat ';
      Qry.ParamByName('pCat').AsString := ACategoria;
    end;

    Qry.SQL.Text := Qry.SQL.Text + 'ORDER BY o.categoria, o.nome_amigavel';
    Qry.ParamByName('pCodGrupo').AsString := ACodigoGrupo;
    Qry.Open;

    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Idx := High(Res);
      Res[Idx].CodigoObjeto := Qry.FieldByName('codigo_objeto').AsString;
      Res[Idx].NomeObjeto   := Qry.FieldByName('nome_objeto').AsString;
      Res[Idx].NomeAmigavel := Qry.FieldByName('nome_amigavel').AsString;
      Res[Idx].Categoria    := Qry.FieldByName('categoria').AsString;
      Res[Idx].CodigoGrupo  := ACodigoGrupo;
      Res[Idx].StatusAcesso := Qry.FieldByName('statusacesso').AsString;
      Qry.Next;
    end;
    Result := Res;
  finally
    Qry.Free;
  end;
end;

function TUsuariosRepository.ListarCategoriasObjetos: TArray<string>;
var
  Qry: TFDQuery;
  Res: TArray<string>;
begin
  SetLength(Res, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT DISTINCT categoria FROM USER_geoapolo_objetos WITH (NOLOCK) WHERE categoria IS NOT NULL ORDER BY categoria';
    Qry.Open;
    while not Qry.Eof do
    begin
      SetLength(Res, Length(Res) + 1);
      Res[High(Res)] := Qry.FieldByName('categoria').AsString;
      Qry.Next;
    end;
    Result := Res;
  finally
    Qry.Free;
  end;
end;

function TUsuariosRepository.AtualizarStatusAcesso(const ACodigoGrupo, ACodigoObjeto, AStatus: string): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'IF EXISTS (SELECT 1 FROM USER_geoapolo_grupobjetos WHERE codigo_grupo = :pGrupo AND codigo_objeto = :pObj) ' +
      'BEGIN ' +
      '  UPDATE USER_geoapolo_grupobjetos SET statusacesso = :pStatus WHERE codigo_grupo = :pGrupo AND codigo_objeto = :pObj; ' +
      'END ' +
      'ELSE ' +
      'BEGIN ' +
      '  INSERT INTO USER_geoapolo_grupobjetos (codigo_grupo, codigo_objeto, statusacesso) VALUES (:pGrupo, :pObj, :pStatus); ' +
      'END';
    Qry.ParamByName('pGrupo').AsString  := ACodigoGrupo;
    Qry.ParamByName('pObj').AsString    := ACodigoObjeto;
    Qry.ParamByName('pStatus').AsString := AStatus;
    Qry.ExecSQL;
    Result := True;
  finally
    Qry.Free;
  end;
end;

end.
