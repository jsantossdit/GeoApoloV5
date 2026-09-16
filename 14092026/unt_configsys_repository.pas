unit unt_configsys_repository;

{
  Repositório FireDAC para Parâmetros do Sistema e Configurações de E-mail.
  Garante persistência segura, queries parametrizadas e hints WITH (NOLOCK).
}

interface

uses
  System.SysUtils, System.Classes, Data.DB,
  FireDAC.Comp.Client, FireDAC.Stan.Param,
  unt_configsys_types;

type
  TConfiguracoesRepository = class
  private
    FConn: TFDConnection;
  public
    constructor Create(AConnection: TFDConnection);

    // Parâmetros do Sistema
    function ObterConfiguracoes(const AEmpresaCodigo: string): TConfiguracoesSistemaDTO;
    function SalvarConfiguracoes(const AConfig: TConfiguracoesSistemaDTO): TOperacaoResultado;

    // Servidores de E-mail
    function ListarServidoresEmail: TArray<TServidorEmailDTO>;
    function SalvarServidorEmail(const AServidor: TServidorEmailDTO; const AModoInclusao: Boolean): TOperacaoResultado;
    function ExcluirServidorEmail(const ACodigo: string): TOperacaoResultado;

    // Contas de E-mail
    function ListarContasEmail: TArray<TContaEmailDTO>;
    function SalvarContaEmail(const AConta: TContaEmailDTO; const AModoInclusao: Boolean): TOperacaoResultado;
    function ExcluirContaEmail(const ACodigo: string): TOperacaoResultado;
  end;

implementation

constructor TConfiguracoesRepository.Create(AConnection: TFDConnection);
begin
  inherited Create;
  FConn := AConnection;
end;

function TConfiguracoesRepository.ObterConfiguracoes(const AEmpresaCodigo: string): TConfiguracoesSistemaDTO;
var
  Qry: TFDQuery;
begin
  FillChar(Result, SizeOf(Result), 0);
  Result.EmpresaCodigo := AEmpresaCodigo;
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT TOP (1) * FROM USER_geoapolo_configuracoes WITH (NOLOCK) WHERE empcod = :emp';
    Qry.ParamByName('emp').AsString := AEmpresaCodigo;
    Qry.Open;

    if not Qry.IsEmpty then
    begin
      Result.CaminhoBackupSistema    := Qry.FieldByName('caminhobackupsistema').AsString;
      Result.InstalacaoLocal         := Qry.FieldByName('instalacaolocal').AsString;
      Result.LocalNovasVersoes       := Qry.FieldByName('localnovasversoes').AsString;
      Result.LocalInstaladorVersoes  := Qry.FieldByName('localinstaladorversoes').AsString;
      Result.CaminhoArquivoConvenio  := Qry.FieldByName('caminhoarquivoconvenio').AsString;
      Result.CaminhoInventario       := Qry.FieldByName('caminhoinventario').AsString;
      Result.CaminhoDocTI            := Qry.FieldByName('caminhodocti').AsString;
      Result.CaminhoDocMissaoPopular := Qry.FieldByName('caminhodocmissaopopular').AsString;
      Result.CaminhoBaseAlvoLoja     := Qry.FieldByName('caminhobasealvoloja').AsString;
      Result.EntCategParceira        := Qry.FieldByName('entcategparceira').AsString;
      Result.EntCodConsumidorFinal   := Qry.FieldByName('entcod_consumidorfinal').AsString;
      Result.OrigCodEstr             := Qry.FieldByName('origcodestr').AsString;
      Result.MotOcorCodEstr          := Qry.FieldByName('motocorcodestr').AsString;
      Result.IntegraEntidadesApolo   := Qry.FieldByName('integra_entidades_apolo').AsString;
      Result.GrupoHardware           := Qry.FieldByName('grupohardware').AsString;
      Result.GrupoSoftware           := Qry.FieldByName('gruposoftware').AsString;
      Result.TempoMaximoMissao       := Qry.FieldByName('tempomaximomissao').AsString;
      Result.StatusFechaPIC          := Qry.FieldByName('status_fechapic').AsString;
    end;
  finally
    Qry.Free;
  end;
end;

function TConfiguracoesRepository.SalvarConfiguracoes(const AConfig: TConfiguracoesSistemaDTO): TOperacaoResultado;
var
  Qry: TFDQuery;
  Existe: Boolean;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;

    // Checa se já existe registro para a empresa
    Qry.SQL.Text := 'SELECT COUNT(*) FROM USER_geoapolo_configuracoes WITH (NOLOCK) WHERE empcod = :emp';
    Qry.ParamByName('emp').AsString := AConfig.EmpresaCodigo;
    Qry.Open;
    Existe := Qry.Fields[0].AsInteger > 0;
    Qry.Close;

    if Existe then
    begin
      Qry.SQL.Text := 'UPDATE USER_geoapolo_configuracoes SET ' +
                      '  caminhobackupsistema = :backup, ' +
                      '  instalacaolocal = :inst, ' +
                      '  localnovasversoes = :novas, ' +
                      '  localinstaladorversoes = :instalador, ' +
                      '  caminhoarquivoconvenio = :convenio, ' +
                      '  caminhoinventario = :inv, ' +
                      '  caminhodocti = :docti, ' +
                      '  caminhodocmissaopopular = :docmissao, ' +
                      '  caminhobasealvoloja = :loja, ' +
                      '  entcategparceira = :parceira, ' +
                      '  entcod_consumidorfinal = :consumidor, ' +
                      '  origcodestr = :origem, ' +
                      '  motocorcodestr = :motivo, ' +
                      '  integra_entidades_apolo = :integra, ' +
                      '  grupohardware = :hard, ' +
                      '  gruposoftware = :soft, ' +
                      '  tempomaximomissao = :tempo, ' +
                      '  status_fechapic = :statuspic ' +
                      'WHERE empcod = :emp';
    end
    else
    begin
      Qry.SQL.Text := 'INSERT INTO USER_geoapolo_configuracoes ( ' +
                      '  empcod, caminhobackupsistema, instalacaolocal, localnovasversoes, ' +
                      '  localinstaladorversoes, caminhoarquivoconvenio, caminhoinventario, ' +
                      '  caminhodocti, caminhodocmissaopopular, caminhobasealvoloja, ' +
                      '  entcategparceira, entcod_consumidorfinal, origcodestr, ' +
                      '  motocorcodestr, integra_entidades_apolo, grupohardware, ' +
                      '  gruposoftware, tempomaximomissao, status_fechapic ' +
                      ') VALUES ( ' +
                      '  :emp, :backup, :inst, :novas, :instalador, :convenio, :inv, ' +
                      '  :docti, :docmissao, :loja, :parceira, :consumidor, :origem, ' +
                      '  :motivo, :integra, :hard, :soft, :tempo, :statuspic ' +
                      ')';
    end;

    Qry.ParamByName('emp').AsString        := AConfig.EmpresaCodigo;
    Qry.ParamByName('backup').AsString     := AConfig.CaminhoBackupSistema;
    Qry.ParamByName('inst').AsString       := AConfig.InstalacaoLocal;
    Qry.ParamByName('novas').AsString      := AConfig.LocalNovasVersoes;
    Qry.ParamByName('instalador').AsString := AConfig.LocalInstaladorVersoes;
    Qry.ParamByName('convenio').AsString   := AConfig.CaminhoArquivoConvenio;
    Qry.ParamByName('inv').AsString        := AConfig.CaminhoInventario;
    Qry.ParamByName('docti').AsString      := AConfig.CaminhoDocTI;
    Qry.ParamByName('docmissao').AsString  := AConfig.CaminhoDocMissaoPopular;
    Qry.ParamByName('loja').AsString       := AConfig.CaminhoBaseAlvoLoja;
    Qry.ParamByName('parceira').AsString   := AConfig.EntCategParceira;
    Qry.ParamByName('consumidor').AsString := AConfig.EntCodConsumidorFinal;
    Qry.ParamByName('origem').AsString     := AConfig.OrigCodEstr;
    Qry.ParamByName('motivo').AsString     := AConfig.MotOcorCodEstr;
    Qry.ParamByName('integra').AsString    := AConfig.IntegraEntidadesApolo;
    Qry.ParamByName('hard').AsString       := AConfig.GrupoHardware;
    Qry.ParamByName('soft').AsString       := AConfig.GrupoSoftware;
    Qry.ParamByName('tempo').AsString      := AConfig.TempoMaximoMissao;
    Qry.ParamByName('statuspic').AsString  := AConfig.StatusFechaPIC;
    Qry.ExecSQL;

    Result.Sucesso  := True;
    Result.Mensagem := 'Configurações do sistema gravadas com sucesso!';
    Result.Codigo   := AConfig.EmpresaCodigo;
  except
    on E: Exception do
    begin
      Result.Sucesso  := False;
      Result.Mensagem := 'Erro ao gravar configurações: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TConfiguracoesRepository.ListarServidoresEmail: TArray<TServidorEmailDTO>;
var
  Qry: TFDQuery;
  Lista: TArray<TServidorEmailDTO>;
  Item: TServidorEmailDTO;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT codigo_servidor, protocolo, servidor_envio, porta_envio, ' +
                    '  servidor_recebimento, porta_recebimento ' +
                    'FROM USER_geoapolo_mail_server WITH (NOLOCK) ' +
                    'ORDER BY codigo_servidor ASC';
    Qry.Open;
    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Item.CodigoServidor      := Qry.FieldByName('codigo_servidor').AsString;
      Item.Protocolo           := Qry.FieldByName('protocolo').AsString;
      Item.ServidorEnvio       := Qry.FieldByName('servidor_envio').AsString;
      Item.PortaEnvio          := Qry.FieldByName('porta_envio').AsInteger;
      Item.ServidorRecebimento := Qry.FieldByName('servidor_recebimento').AsString;
      Item.PortaRecebimento    := Qry.FieldByName('porta_recebimento').AsInteger;
      Lista[Count] := Item;
      Inc(Count);
      Qry.Next;
    end;
    Result := Lista;
  finally
    Qry.Free;
  end;
end;

function TConfiguracoesRepository.SalvarServidorEmail(const AServidor: TServidorEmailDTO; const AModoInclusao: Boolean): TOperacaoResultado;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    if AModoInclusao then
    begin
      Qry.SQL.Text := 'INSERT INTO USER_geoapolo_mail_server ( ' +
                      '  codigo_servidor, protocolo, servidor_envio, porta_envio, ' +
                      '  servidor_recebimento, porta_recebimento ' +
                      ') VALUES (:cod, :prot, :senv, :penv, :srec, :prec)';
    end
    else
    begin
      // Corrigido o bug histórico da vírgula duplicada no código legado
      Qry.SQL.Text := 'UPDATE USER_geoapolo_mail_server SET ' +
                      '  protocolo = :prot, servidor_envio = :senv, porta_envio = :penv, ' +
                      '  servidor_recebimento = :srec, porta_recebimento = :prec ' +
                      'WHERE codigo_servidor = :cod';
    end;

    Qry.ParamByName('cod').AsString  := AServidor.CodigoServidor;
    Qry.ParamByName('prot').AsString := AServidor.Protocolo;
    Qry.ParamByName('senv').AsString := AServidor.ServidorEnvio;
    Qry.ParamByName('penv').AsInteger := AServidor.PortaEnvio;
    Qry.ParamByName('srec').AsString := AServidor.ServidorRecebimento;
    Qry.ParamByName('prec').AsInteger := AServidor.PortaRecebimento;
    Qry.ExecSQL;

    Result.Sucesso  := True;
    Result.Mensagem := 'Servidor de e-mail gravado com sucesso!';
    Result.Codigo   := AServidor.CodigoServidor;
  except
    on E: Exception do
    begin
      Result.Sucesso  := False;
      Result.Mensagem := 'Falha ao salvar servidor de e-mail: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TConfiguracoesRepository.ExcluirServidorEmail(const ACodigo: string): TOperacaoResultado;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'DELETE FROM USER_geoapolo_mail_server WHERE codigo_servidor = :cod';
    Qry.ParamByName('cod').AsString := ACodigo;
    Qry.ExecSQL;

    Result.Sucesso  := True;
    Result.Mensagem := 'Servidor de e-mail excluído com sucesso!';
    Result.Codigo   := ACodigo;
  except
    on E: Exception do
    begin
      Result.Sucesso  := False;
      Result.Mensagem := 'Falha ao excluir servidor: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TConfiguracoesRepository.ListarContasEmail: TArray<TContaEmailDTO>;
var
  Qry: TFDQuery;
  Lista: TArray<TContaEmailDTO>;
  Item: TContaEmailDTO;
  Count: Integer;
begin
  SetLength(Lista, 0);
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT codigo_conta, conta_email, senha, codigo_servidor ' +
                    'FROM USER_geoapolo_contas_email WITH (NOLOCK) ' +
                    'ORDER BY codigo_conta ASC';
    Qry.Open;
    Count := 0;
    while not Qry.Eof do
    begin
      SetLength(Lista, Count + 1);
      Item.CodigoConta    := Qry.FieldByName('codigo_conta').AsString;
      Item.ContaEmail     := Qry.FieldByName('conta_email').AsString;
      Item.Senha          := Qry.FieldByName('senha').AsString;
      Item.CodigoServidor := Qry.FieldByName('codigo_servidor').AsString;
      Lista[Count] := Item;
      Inc(Count);
      Qry.Next;
    end;
    Result := Lista;
  finally
    Qry.Free;
  end;
end;

function TConfiguracoesRepository.SalvarContaEmail(const AConta: TContaEmailDTO; const AModoInclusao: Boolean): TOperacaoResultado;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    if AModoInclusao then
    begin
      Qry.SQL.Text := 'INSERT INTO USER_geoapolo_contas_email (codigo_conta, conta_email, senha, codigo_servidor) ' +
                      'VALUES (:cod, :email, :senha, :serv)';
    end
    else
    begin
      Qry.SQL.Text := 'UPDATE USER_geoapolo_contas_email SET ' +
                      '  conta_email = :email, senha = :senha, codigo_servidor = :serv ' +
                      'WHERE codigo_conta = :cod';
    end;

    Qry.ParamByName('cod').AsString   := AConta.CodigoConta;
    Qry.ParamByName('email').AsString := AConta.ContaEmail;
    Qry.ParamByName('senha').AsString := AConta.Senha;
    Qry.ParamByName('serv').AsString  := AConta.CodigoServidor;
    Qry.ExecSQL;

    Result.Sucesso  := True;
    Result.Mensagem := 'Conta de e-mail salva com sucesso!';
    Result.Codigo   := AConta.CodigoConta;
  except
    on E: Exception do
    begin
      Result.Sucesso  := False;
      Result.Mensagem := 'Falha ao salvar conta de e-mail: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

function TConfiguracoesRepository.ExcluirContaEmail(const ACodigo: string): TOperacaoResultado;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'DELETE FROM USER_geoapolo_contas_email WHERE codigo_conta = :cod';
    Qry.ParamByName('cod').AsString := ACodigo;
    Qry.ExecSQL;

    Result.Sucesso  := True;
    Result.Mensagem := 'Conta de e-mail excluída com sucesso!';
    Result.Codigo   := ACodigo;
  except
    on E: Exception do
    begin
      Result.Sucesso  := False;
      Result.Mensagem := 'Falha ao excluir conta: ' + E.Message;
    end;
  end;
  Qry.Free;
end;

end.
