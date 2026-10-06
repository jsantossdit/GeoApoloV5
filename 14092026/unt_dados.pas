unit unt_dados;

interface

uses
	SysUtils, Classes, DB, Dialogs, Menus, Buttons, Windows,
	Messages, Controls, ExtCtrls, ComCtrls,	StdCtrls, Registry,
  Datasnap.DBClient, Datasnap.Provider,

  Data.FMTBcd,
  Data.SqlExpr, Data.DBXMySql, FireDAC.Stan.Intf, FireDAC.Stan.Option,
  FireDAC.Stan.Error, FireDAC.UI.Intf, FireDAC.Phys.Intf, FireDAC.Stan.Def,
  FireDAC.Stan.Pool, FireDAC.Stan.Async, FireDAC.Phys, FireDAC.Phys.MySQL,
  FireDAC.Phys.MySQLDef, FireDAC.VCLUI.Wait, FireDAC.Comp.UI,
  FireDAC.Comp.Client, FireDAC.Phys.MSSQL, FireDAC.Phys.MSSQLDef,
  FireDAC.Stan.Param, FireDAC.DatS, FireDAC.DApt.Intf, FireDAC.DApt,
  FireDAC.Comp.DataSet, FireDAC.Phys.SQLite, FireDAC.Phys.SQLiteDef,
  FireDAC.Stan.ExprFuncs, FireDAC.Phys.SQLiteWrapper.Stat;


type
	Tmodulo_dados = class(TDataModule)
    fdbanco: TFDConnection;
    fdquerysql: TFDQuery;
    dtsfdquerysql: TDataSource;
    dtsquerysve: TDataSource;
    dtsquerybanco: TDataSource;
    fdquerysql10: TFDQuery;
    dtsfdquerysql10: TDataSource;
    fdquerysql3: TFDQuery;
    dtsfdquerysql3: TDataSource;
    fdquerysql4: TFDQuery;
    dtsfdquerysql4: TDataSource;
    fdqueryentidade: TFDQuery;
    dtsfdqueryentidade: TDataSource;
    fdquerysql6: TFDQuery;
    dtsfdquerysql6: TDataSource;
    fdquerysql16: TFDQuery;
    dtsfdquerysql16: TDataSource;
    dtsfdquerysql14: TDataSource;
    fdquerysql14: TFDQuery;
    fdquerysql1: TFDQuery;
    dtsfdquerysql1: TDataSource;
    fdcomando: TFDCommand;
    dtsfdquerysql12: TDataSource;
    fdquerysql12: TFDQuery;
    fdquerysql7: TFDQuery;
    dtsfdquerysql7: TDataSource;
    fdquerysql22: TFDQuery;
    dtsfdquerysql22: TDataSource;
    dtsfdquerysql23: TDataSource;
    fdquerysql23: TFDQuery;
    dtsfdquerysql11: TDataSource;
    fdquerysql11: TFDQuery;
    dtsfdquerysql17: TDataSource;
    fdquerysql17: TFDQuery;
    fdquerysql18: TFDQuery;
    dtsfdquerysql18: TDataSource;
    fdquerysql8: TFDQuery;
    dtsfdquerysql8: TDataSource;
    fdquerysql2: TFDQuery;
    dtsfdquerysql2: TDataSource;

    fdquerysql19: TFDQuery;
    dtsfdquerysql19: TDataSource;
    fdquerysql20: TFDQuery;
    dtsfdquerysql20: TDataSource;
    fdquerysql15: TFDQuery;
    dtsfdquerysql15: TDataSource;
    fdquerysql9: TFDQuery;
    dtsfdquerysql9: TDataSource;
    fdquerysql13: TFDQuery;
    dtsfdquerysql13: TDataSource;
    dtsfdconsulta: TDataSource;
    fdquerysql5: TFDQuery;
    dtsfdquerysql5: TDataSource;
    fdbancosqlite: TFDConnection;
    fdbancosavic: TFDConnection;
    fdbancoapp: TFDConnection;
		procedure DataModuleCreate(Sender: TObject);
	private
		{ Private declarations }
	public
		{ Public declarations }
	end;

var
  modulo_dados: Tmodulo_dados;
  catalogo: string;

function conecta_banco(nome_banco: string): Boolean;
function conecta_banco_savic: Boolean;
function conecta_banco_app_rcc: Boolean;
function TratarErroConexaoMSSQL(const E: Exception; const AServidor, ABanco: string): string;
procedure TratarFalhaConexaoGeral(const AErro, AServidor, ABanco: string);

implementation

uses funcoes, unt_principal, frmconfigbancos, Vcl.Forms;

{$R *.dfm}

procedure Tmodulo_dados.DataModuleCreate(Sender: TObject);
begin
   // Conecta somente se configuracoes ja foram carregadas (evita erro prematuro)
   if Assigned(frmprincipal) and
      ((Trim(frmprincipal.nomeserversql) <> '') or (Trim(frmprincipal.nomebancosql) <> '')) then
     conecta_banco('FDALVO');
end;

function TratarErroConexaoMSSQL(const E: Exception; const AServidor, ABanco: string): string;
var
  Msg, Detalhes: string;
begin
  if Assigned(E) then
    Detalhes := E.Message
  else
    Detalhes := 'Erro desconhecido ao tentar conectar.';

  if (Pos('26', Detalhes) > 0) or (Pos('53', Detalhes) > 0) or
     (Pos('Named Pipes', Detalhes) > 0) or (Pos('Localizar Servidor', Detalhes) > 0) or
     (Pos('não foi encontrado', Detalhes) > 0) or (Pos('nao foi encontrado', Detalhes) > 0) or
     (Pos('server was not found', LowerCase(Detalhes)) > 0) then
  begin
    Msg := 'Não foi possível localizar o servidor ou a instância do SQL Server: "' + AServidor + '".' + sLineBreak + sLineBreak +
           'Possíveis causas e soluções:' + sLineBreak +
           '• Se for uma base local, verifique se o serviço do SQL Server está em execução no Windows (services.msc).' + sLineBreak +
           '• Se for uma instância nomeada (ex: SERVIDOR\INSTANCIA) via rede, certifique-se de que o serviço "SQL Server Browser" está ativo.' + sLineBreak +
           '• Verifique se o nome do computador ou endereço IP está correto e sem barras invertidas extras no início.' + sLineBreak +
           '• Verifique se o Firewall do Windows não está bloqueando as portas do SQL Server.';
  end
  else if (Pos('18456', Detalhes) > 0) or (Pos('Login failed', Detalhes) > 0) or (Pos('Falha de logon', Detalhes) > 0) then
  begin
    Msg := 'Falha de autenticação no SQL Server: "' + AServidor + '".' + sLineBreak + sLineBreak +
           'Possíveis causas e soluções:' + sLineBreak +
           '• O usuário ou a senha informados para o banco de dados estão incorretos.' + sLineBreak +
           '• O SQL Server pode estar configurado apenas para Autenticação do Windows (Modo Misto desativado).' + sLineBreak +
           '• Verifique a senha cadastrada na tela de Configurações de Banco.';
  end
  else if (Pos('4060', Detalhes) > 0) or (Pos('Cannot open database', Detalhes) > 0) or (Pos('Não é possível abrir o banco', Detalhes) > 0) then
  begin
    Msg := 'O banco de dados "' + ABanco + '" não foi encontrado no servidor "' + AServidor + '".' + sLineBreak + sLineBreak +
           'Possíveis causas e soluções:' + sLineBreak +
           '• O nome da base de dados (' + ABanco + ') pode estar digitado incorretamente.' + sLineBreak +
           '• A base de dados ainda não foi criada ou restaurada nesta instância do SQL Server.';
  end
  else if (Pos('certificate', LowerCase(Detalhes)) > 0) or (Pos('ssl', LowerCase(Detalhes)) > 0) or (Pos('cadeia de certificados', LowerCase(Detalhes)) > 0) then
  begin
    Msg := 'Falha na validação do certificado de segurança SSL/TLS ao conectar com "' + AServidor + '".' + sLineBreak + sLineBreak +
           'Possíveis causas e soluções:' + sLineBreak +
           '• O certificado do servidor não é confiável ou é autoassinado.' + sLineBreak +
           '• A opção TrustServerCertificate deve estar ativada.';
  end
  else
  begin
    Msg := 'Falha ao conectar no banco de dados "' + ABanco + '" no servidor "' + AServidor + '".' + sLineBreak + sLineBreak +
           'Detalhes técnicos: ' + Detalhes;
  end;

  Result := Msg;
end;

procedure TratarFalhaConexaoGeral(const AErro, AServidor, ABanco: string);
var
  MsgAmigavel: string;
  Ex: Exception;
  Resp: Integer;
begin
  Ex := Exception.Create(AErro);
  try
    MsgAmigavel := TratarErroConexaoMSSQL(Ex, AServidor, ABanco);
  finally
    Ex.Free;
  end;

  Resp := MessageDlg(MsgAmigavel + sLineBreak + sLineBreak +
                     'Deseja abrir a tela de Configurações de Banco agora para verificar os parâmetros?',
                     mtError, [mbYes, mbNo], 0);
  if Resp = mrYes then
  begin
    if not Assigned(frmconfigbanco) then
      Application.CreateForm(Tfrmconfigbanco, frmconfigbanco);
    frmconfigbanco.ShowModal;
  end;
end;

function TentarConexaoDireta(const AServidor, ABanco, AUsuario, ASenha, AProtocolo: string; out AErro: string): Boolean;
var
  SrvLimpo: string;
begin
  Result := False;
  AErro := '';
  if not Assigned(modulo_dados) or not Assigned(modulo_dados.fdbanco) then Exit;

  SrvLimpo := SanitizarNomeServidor(AServidor);
  if SrvLimpo = '' then
  begin
    AErro := 'Nome do servidor SQL não foi informado.';
    Exit;
  end;

  with modulo_dados.fdbanco do
  begin
    Connected := False;
    Params.Clear;
    Params.Values['DriverID']               := 'MSSQL';
    Params.Values['Server']                 := SrvLimpo;
    Params.Values['Database']               := Trim(ABanco);
    Params.Values['User_Name']              := Trim(AUsuario);
    Params.Values['Password']               := ASenha;
    Params.Values['Encrypt']                := 'No';
    Params.Values['TrustServerCertificate'] := 'Yes';
    Params.Values['MARS']                   := 'Yes';

    // Se o protocolo for especificado e nao for conexao local com instancia nomeada:
    if (Trim(AProtocolo) <> '') and not (ServidorEhLocal(SrvLimpo) and (Pos('\', SrvLimpo) > 0)) then
      Params.Values['Protocol'] := Trim(AProtocolo);

    LoginPrompt                   := False;
    ResourceOptions.AutoReconnect := True;
    ResourceOptions.SilentMode    := True;
    TxOptions.AutoCommit          := True;
    FetchOptions.Mode             := fmAll;
    FetchOptions.Items            := [];

    try
      Connected := True;
      Result := True;
    except
      on E: Exception do
      begin
        Result := False;
        AErro := E.Message;
      end;
    end;
  end;
end;

function conecta_banco(nome_banco: string): Boolean;
var
  Srv, Banco, Usu, Senha, Proto, Erro: string;
  Sucesso: Boolean;
  NomeInstancia: string;
  P: Integer;
begin
  Result := False;
  if not Assigned(modulo_dados) then Exit;
  if not Assigned(frmprincipal) then Exit;

  if nome_banco = 'FDALVO' then
  begin
    if not Assigned(modulo_dados.fdbanco) then Exit;

    Srv   := SanitizarNomeServidor(frmprincipal.nomeserversql);
    Banco := Trim(frmprincipal.nomebancosql);
    Usu   := Trim(frmprincipal.usuariobancosql);
    Senha := frmprincipal.senhasql;
    Proto := Trim(frmprincipal.protocolo);

    // Evita conexao prematura com parametros em branco
    if (Srv = '') and (Banco = '') then
      Exit(False);

    Sucesso := TentarConexaoDireta(Srv, Banco, Usu, Senha, Proto, Erro);

    // Fallback 1: se falhou por autenticacao e senha no registro puder ter sido 'semsenha' crua
    if not Sucesso and (Pos('18456', Erro) > 0) then
    begin
      if (Senha <> 'semsenha') and (Trim(frmprincipal.senhasql) <> '') then
      begin
        if TentarConexaoDireta(Srv, Banco, Usu, 'semsenha', Proto, Erro) then
        begin
          frmprincipal.senhasql := 'semsenha';
          Sucesso := True;
        end;
      end;
    end;

    // Fallback 2: se falhou e for servidor local com instancia nomeada (ex: SDIT-02\SDITBD)
    // Tenta fallback com localhost ou ponto para usar Memória Compartilhada
    if not Sucesso and ServidorEhLocal(Srv) and (Pos('\', Srv) > 0) then
    begin
      P := Pos('\', Srv);
      NomeInstancia := Copy(Srv, P + 1, Length(Srv));

      if UpperCase(Copy(Srv, 1, P - 1)) <> 'LOCALHOST' then
      begin
        Sucesso := TentarConexaoDireta('localhost\' + NomeInstancia, Banco, Usu, Senha, '', Erro);
        if Sucesso then
          frmprincipal.nomeserversql := 'localhost\' + NomeInstancia;
      end;

      if not Sucesso then
      begin
        Sucesso := TentarConexaoDireta('.\' + NomeInstancia, Banco, Usu, Senha, '', Erro);
        if Sucesso then
          frmprincipal.nomeserversql := '.\' + NomeInstancia;
      end;
    end;

    if Sucesso then
    begin
      Result := True;
    end
    else
    begin
      Result := False;
      TratarFalhaConexaoGeral(Erro, Srv, Banco);
    end;
  end;
end;

function conecta_banco_savic: Boolean;
var
  reg: TRegistry;
  sServer, sUser, sPass, sDB: string;
  nPort: Integer;
begin
  Result := False;
  if not Assigned(modulo_dados) then Exit;
  if not Assigned(modulo_dados.fdbancosavic) then Exit;

  sServer := '167.71.28.209';
  sUser   := 'rccbrasilsavic';
  sPass   := 'b2J4earCJuNcM7';
  sDB     := 'rccbrasilsavic';
  nPort   := 3333;

  reg := TRegistry.Create;
  try
    reg.RootKey := HKEY_CURRENT_USER;
    if reg.OpenKeyReadOnly('sdit\configuracoes\DataBase') then
    begin
      if reg.ValueExists('Nome do Servidor SAVIC') and (Trim(reg.ReadString('Nome do Servidor SAVIC')) <> '') then
        sServer := Trim(reg.ReadString('Nome do Servidor SAVIC'))
      else if reg.ValueExists('Nome do Servidor APP') and (Trim(reg.ReadString('Nome do Servidor APP')) <> '') then
        sServer := Trim(reg.ReadString('Nome do Servidor APP'));

      if reg.ValueExists('Usuario admin SAVIC') and (Trim(reg.ReadString('Usuario admin SAVIC')) <> '') then
        sUser := Trim(reg.ReadString('Usuario admin SAVIC'))
      else if reg.ValueExists('Usuario admin APP') and (Trim(reg.ReadString('Usuario admin APP')) <> '') then
        sUser := Trim(reg.ReadString('Usuario admin APP'));

      if reg.ValueExists('Senha SAVIC') and (Trim(reg.ReadString('Senha SAVIC')) <> '') then
        sPass := Trim(reg.ReadString('Senha SAVIC'))
      else if reg.ValueExists('Senha APP') and (Trim(reg.ReadString('Senha APP')) <> '') then
        sPass := Trim(reg.ReadString('Senha APP'));

      if reg.ValueExists('NomeBancoSAVIC') and (Trim(reg.ReadString('NomeBancoSAVIC')) <> '') then
        sDB := Trim(reg.ReadString('NomeBancoSAVIC'))
      else if reg.ValueExists('NomeBancoAPP') and (Trim(reg.ReadString('NomeBancoAPP')) <> '') then
        sDB := Trim(reg.ReadString('NomeBancoAPP'));

      if reg.ValueExists('Porta Comunicacao SAVIC') then
        nPort := reg.ReadInteger('Porta Comunicacao SAVIC')
      else if reg.ValueExists('Porta Comunicacao APP') then
      begin
        try
          nPort := StrToIntDef(Trim(reg.ReadString('Porta Comunicacao APP')), 0);
          if nPort = 0 then
            nPort := reg.ReadInteger('Porta Comunicacao APP');
        except
          nPort := 3306;
        end;
        if nPort = 0 then
          nPort := 3306;
      end;
      reg.CloseKey;
    end;
  finally
    reg.Free;
  end;

  if (Trim(sServer) = '') or (Trim(sDB) = '') or (Trim(sUser) = '') then
  begin
    MessageDlg('Solicite ao Administrador a configuração de acesso aos dados do SAVIC', mtWarning, [mbOK], 0);
    Exit;
  end;

  with modulo_dados.fdbancosavic do
  begin
    Connected := False;
    Params.Clear;
    Params.Values['DriverID']  := 'MySQL';
    Params.Values['Server']    := sServer;
    Params.Values['Database']  := sDB;
    Params.Values['User_Name'] := sUser;
    Params.Values['Password']  := sPass;
    if nPort > 0 then
      Params.Values['Port']    := IntToStr(nPort);
    LoginPrompt                := False;
    ResourceOptions.AutoReconnect := True;
    ResourceOptions.SilentMode    := True;
    TxOptions.AutoCommit          := True;
    FetchOptions.Mode             := fmAll;
    FetchOptions.Items            := [];
    try
      Connected := True;
      Result := True;
    except
      on E: Exception do
      begin
        Result := False;
        MessageDlg('Solicite ao Administrador a configuração de acesso aos dados do SAVIC' + #13#10#13#10 + 'Detalhes técnicos: ' + E.Message, mtError, [mbOK], 0);
      end;
    end;
  end;
end;

function conecta_banco_app_rcc: Boolean;
var
  reg: TRegistry;
  sServer, sUser, sPass, sDB: string;
  nPort: Integer;
begin
  Result := False;
  if not Assigned(modulo_dados) then Exit;
  if not Assigned(modulo_dados.fdbancoapp) then Exit;

  sServer := '';
  sUser   := '';
  sPass   := '';
  sDB     := '';
  nPort   := 3306;

  reg := TRegistry.Create;
  try
    reg.RootKey := HKEY_CURRENT_USER;
    if reg.OpenKeyReadOnly('sdit\configuracoes\DataBase') then
    begin
      if reg.ValueExists('Nome do Servidor APP RCC') and (Trim(reg.ReadString('Nome do Servidor APP RCC')) <> '') then
        sServer := Trim(reg.ReadString('Nome do Servidor APP RCC'))
      else if reg.ValueExists('Nome do Servidor APP') and (Trim(reg.ReadString('Nome do Servidor APP')) <> '') then
        sServer := Trim(reg.ReadString('Nome do Servidor APP'));

      if reg.ValueExists('Usuario admin APP RCC') and (Trim(reg.ReadString('Usuario admin APP RCC')) <> '') then
        sUser := Trim(reg.ReadString('Usuario admin APP RCC'))
      else if reg.ValueExists('Usuario admin APP') and (Trim(reg.ReadString('Usuario admin APP')) <> '') then
        sUser := Trim(reg.ReadString('Usuario admin APP'));

      if reg.ValueExists('Senha APP RCC') and (Trim(reg.ReadString('Senha APP RCC')) <> '') then
        sPass := Trim(reg.ReadString('Senha APP RCC'))
      else if reg.ValueExists('Senha APP') and (Trim(reg.ReadString('Senha APP')) <> '') then
        sPass := Trim(reg.ReadString('Senha APP'));

      if reg.ValueExists('NomeBancoAPP RCC') and (Trim(reg.ReadString('NomeBancoAPP RCC')) <> '') then
        sDB := Trim(reg.ReadString('NomeBancoAPP RCC'))
      else if reg.ValueExists('NomeBancoAPP') and (Trim(reg.ReadString('NomeBancoAPP')) <> '') then
        sDB := Trim(reg.ReadString('NomeBancoAPP'));

      if reg.ValueExists('Porta Comunicacao APP RCC') then
        nPort := reg.ReadInteger('Porta Comunicacao APP RCC')
      else if reg.ValueExists('Porta Comunicacao APP') then
      begin
        try
          nPort := StrToIntDef(Trim(reg.ReadString('Porta Comunicacao APP')), 0);
          if nPort = 0 then
            nPort := reg.ReadInteger('Porta Comunicacao APP');
        except
          nPort := 3306;
        end;
        if nPort = 0 then
          nPort := 3306;
      end;
      reg.CloseKey;
    end;
  finally
    reg.Free;
  end;

  if Trim(sServer) = '' then
  begin
    MessageDlg('Configurações de conexão ao Banco do Aplicativo RCC não foram definidas no Configurador de Banco!', mtWarning, [mbOK], 0);
    Exit;
  end;

  with modulo_dados.fdbancoapp do
  begin
    Connected := False;
    Params.Clear;
    Params.Values['DriverID']  := 'MySQL';
    Params.Values['Server']    := sServer;
    Params.Values['Database']  := sDB;
    Params.Values['User_Name'] := sUser;
    Params.Values['Password']  := sPass;
    if nPort > 0 then
      Params.Values['Port']    := IntToStr(nPort);
    LoginPrompt                := False;
    ResourceOptions.AutoReconnect := True;
    ResourceOptions.SilentMode    := True;
    TxOptions.AutoCommit          := True;
    FetchOptions.Mode             := fmAll;
    FetchOptions.Items            := [];
    try
      Connected := True;
      Result := True;
    except
      on E: Exception do
      begin
        Result := False;
        MessageDlg('ERRO AO CONECTAR AO BANCO DO APLICATIVO RCC: ' + E.Message, mtError, [mbOK], 0);
      end;
    end;
  end;
end;

end.
