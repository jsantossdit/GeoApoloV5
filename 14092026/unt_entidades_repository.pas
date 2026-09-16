unit unt_entidades_repository;

interface

uses
  System.SysUtils, System.Classes, Data.DB, FireDAC.Comp.Client,
  FireDAC.Stan.Param, FireDAC.Stan.Option, unt_entidades_types;

type
  IEntidadeRepository = interface
    ['{7C1844B5-7B7B-4B6E-9F93-7848D235D961}']
    function ObterParametroIntegracao(const AEmpCod: string): string;
    function ViewExiste(const ANomeView: string): Boolean;
    procedure CriarViewCasoNaoExista(const ANomeView, ASqlDef: string);
    function ExecutarConsultaLista(const AFiltro: TEntidadeFiltroDTO; ATargetQuery: TFDQuery): Boolean;
    function ObterOcorrenciaCodigo(const AGeoEntCod: string): string;
    function IgnorarAtualizacaoAlvo(const AGeoEntCod, AUsuCodApolo, ACodEmpresa, ACodUsuario: string): Boolean;
    function AtualizarEntCodAlvoViaCPF(const AGeoEntCod: string): string;
    function ObterCredenciaisAlvo(const ACodUsuario: string): TCredencialAlvoDTO;
    procedure SalvarCredenciaisAlvo(const ACodUsuario, AUsuApolo, ASenhaCripto: string);
    procedure AtualizarVinculoEntCod(const AGeoEntCod, AEntCod: string);
    procedure CarregarDadosComparacao(const AGeoEntCod, AEntCod: string; AQrySVE, AQryAlvo: TFDQuery);
    procedure RegistrarOcorrenciaIgnorada(const ACodEmpresa, AOcorCod, ACodUsuario: string);
  end;

  TEntidadeRepository = class(TInterfacedObject, IEntidadeRepository)
  private
    FConn: TFDConnection;
  public
    constructor Create(AConnection: TFDConnection);

    function ObterParametroIntegracao(const AEmpCod: string): string;
    function ViewExiste(const ANomeView: string): Boolean;
    procedure CriarViewCasoNaoExista(const ANomeView, ASqlDef: string);
    function ExecutarConsultaLista(const AFiltro: TEntidadeFiltroDTO; ATargetQuery: TFDQuery): Boolean;
    function ObterOcorrenciaCodigo(const AGeoEntCod: string): string;
    function IgnorarAtualizacaoAlvo(const AGeoEntCod, AUsuCodApolo, ACodEmpresa, ACodUsuario: string): Boolean;
    function AtualizarEntCodAlvoViaCPF(const AGeoEntCod: string): string;
    function ObterCredenciaisAlvo(const ACodUsuario: string): TCredencialAlvoDTO;
    procedure SalvarCredenciaisAlvo(const ACodUsuario, AUsuApolo, ASenhaCripto: string);
    procedure AtualizarVinculoEntCod(const AGeoEntCod, AEntCod: string);
    procedure CarregarDadosComparacao(const AGeoEntCod, AEntCod: string; AQrySVE, AQryAlvo: TFDQuery);
    procedure RegistrarOcorrenciaIgnorada(const ACodEmpresa, AOcorCod, ACodUsuario: string);
  end;

implementation

{ TEntidadeRepository }

constructor TEntidadeRepository.Create(AConnection: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConnection) then
    raise Exception.Create('TEntidadeRepository: Instância de TFDConnection é obrigatória.');
  FConn := AConnection;
end;

function TEntidadeRepository.ObterParametroIntegracao(const AEmpCod: string): string;
var
  Qry: TFDQuery;
begin
  Result := '';
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    // TODO: [SQLAlchemy Migration]
    // stmt = select(Configuracao.integra_entidades_apolo).with_hint(Configuracao, 'WITH (NOLOCK)', 'mssql').where(Configuracao.empcod == empcod)
    // result = await session.execute(stmt)
    // return result.scalar_one_or_none()
    Qry.SQL.Text := 'SELECT integra_entidades_apolo FROM USER_geoapolo_configuracoes WITH (NOLOCK) WHERE empcod = :empcod';
    Qry.ParamByName('empcod').AsString := AEmpCod;
    Qry.Open;
    if not Qry.IsEmpty then
      Result := Qry.FieldByName('integra_entidades_apolo').AsString;
  finally
    Qry.Free;
  end;
end;

function TEntidadeRepository.ViewExiste(const ANomeView: string): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    // TODO: [SQLAlchemy Migration]
    // Usar sqlalchemy.inspect(engine).has_table(view_name) ou consulta na INFORMATION_SCHEMA.VIEWS
    Qry.SQL.Text := 'SELECT 1 FROM sys.views WITH (NOLOCK) WHERE name = :pview';
    Qry.ParamByName('pview').AsString := ANomeView;
    Qry.Open;
    Result := not Qry.IsEmpty;
  finally
    Qry.Free;
  end;
end;

procedure TEntidadeRepository.CriarViewCasoNaoExista(const ANomeView, ASqlDef: string);
begin
  if not ViewExiste(ANomeView) then
  begin
    // TODO: [SQLAlchemy Migration]
    // Em Python, views são gerenciadas em migrações Alembic versionadas (op.execute("CREATE VIEW ..."))
    FConn.ExecSQL(Format('CREATE VIEW %s AS %s', [ANomeView, ASqlDef]));
  end;
end;

function TEntidadeRepository.ExecutarConsultaLista(const AFiltro: TEntidadeFiltroDTO; ATargetQuery: TFDQuery): Boolean;
var
  SqlText, DirecaoOrdem, CampoOrdenacao, CampoBusca: string;
begin
  ATargetQuery.Close;
  ATargetQuery.Connection := FConn;
  ATargetQuery.FetchOptions.Mode := fmOnDemand;
  ATargetQuery.FetchOptions.RowsetSize := 50;
  ATargetQuery.FetchOptions.RecsMax := -1;

  if AFiltro.OrdemAsc then
    DirecaoOrdem := 'ASC'
  else
    DirecaoOrdem := 'DESC';

  CampoBusca := Trim(AFiltro.CampoBusca);
  if CampoBusca = '' then
  begin
    if AFiltro.BaseDados = 'Alvo' then
      CampoBusca := 'entnome'
    else
      CampoBusca := 'geoentnome';
  end;

  // Sanitização de identificador de coluna
  CampoBusca := StringReplace(CampoBusca, ';', '', [rfReplaceAll]);
  CampoBusca := StringReplace(CampoBusca, '''', '', [rfReplaceAll]);

  if AFiltro.BaseDados = 'Alvo' then
  begin
    // TODO: [SQLAlchemy Migration]
    // T-SQL nativo preservado com:
    // 1. Hint WITH (NOLOCK) em cada tabela
    // 2. Cláusula SUBSTRING(...) IN ('02', '03')
    // 3. Paginação com .limit(50).offset(...)
    if AFiltro.TipoPesquisa = 'Consulta' then
    begin
      SqlText :=
        'SELECT TOP 50 * FROM entidades_apolo e WITH(NOLOCK) ' +
        ' WHERE e.' + CampoBusca + ' LIKE :procurarpor ' +
        ' AND SUBSTRING(e.categcodestr, 1, 2) IN (''02'', ''03'') ' +
        ' ORDER BY e.entnome ASC';
    end
    else
    begin
      CampoOrdenacao := Trim(AFiltro.CampoOrdenacao);
      if CampoOrdenacao = '' then CampoOrdenacao := 'entnome';
      SqlText :=
        'SELECT * FROM entidades_apolo e WITH(NOLOCK) ' +
        ' WHERE e.' + CampoBusca + ' LIKE :procurarpor ' +
        ' AND SUBSTRING(e.categcodestr, 1, 2) IN (''02'', ''03'') ' +
        ' ORDER BY e.' + CampoOrdenacao + ' ' + DirecaoOrdem;
    end;

    ATargetQuery.SQL.Text := SqlText;
    ATargetQuery.ParamByName('procurarpor').AsString := '%' + AFiltro.TextoBusca + '%';
  end
  else
  begin
    // Base GeoApolo
    // TODO: [SQLAlchemy Migration]
    // A view entidades_geoapolo agrupa 15 tabelas com OUTER APPLY e STRING_AGG.
    // Em Python/SQLAlchemy: construir models relacionais orquestrados com subqueries
    if AFiltro.TipoPesquisa = 'Consulta' then
    begin
      if AFiltro.FiltroEspecial = 'JAEXPORTADA' then
      begin
        SqlText :=
          'SELECT * FROM entidades_geoapolo e WITH(NOLOCK) ' +
          ' INNER JOIN USER_geoapolo_entidade_documentos uged WITH(NOLOCK) ' +
          '   ON e.entcpfcgc = uged.geonumerodocumento AND uged.geotipodocumento = ''CPF/CNPJ'' ' +
          ' INNER JOIN user_geoapolo_entidade ue WITH(NOLOCK) ON e.entcpfcgc = ue.entcpfcgc ' +
          ' WHERE ue.atualizou_apolo = ''S'' ' +
          ' ORDER BY CASE WHEN ue.atualizou_apolo = ''N'' AND e.Entobservacoes IS NULL THEN 0 ELSE 1 END';
      end
      else
      begin
        SqlText :=
          'SELECT * FROM entidades_geoapolo e WITH(NOLOCK) ' +
          ' INNER JOIN USER_geoapolo_entidade_documentos uged WITH(NOLOCK) ' +
          '   ON e.entcpfcgc = uged.geonumerodocumento AND uged.geotipodocumento = ''CPF/CNPJ'' ' +
          ' INNER JOIN user_geoapolo_entidade ue WITH(NOLOCK) ON e.geoentcod = ue.geoentcod ' +
          ' WHERE ue.atualizou_apolo = ''N'' ' +
          ' ORDER BY CASE WHEN ue.atualizou_apolo = ''N'' AND e.Entobservacoes IS NULL THEN 0 ELSE 1 END';
      end;
      ATargetQuery.SQL.Text := SqlText;
    end
    else
    begin
      CampoOrdenacao := Trim(AFiltro.CampoOrdenacao);
      if CampoOrdenacao = '' then CampoOrdenacao := 'geoentnome';
      SqlText :=
        'SELECT * FROM entidades_geoapolo e WITH(NOLOCK) ' +
        ' INNER JOIN user_geoapolo_entidade ue WITH(NOLOCK) ON e.geoentcod = ue.geoentcod ' +
        ' WHERE e.' + CampoBusca + ' LIKE :procurarpor ' +
        ' ORDER BY CASE WHEN ue.atualizou_apolo = ''N'' AND e.Entobservacoes IS NULL THEN 0 ELSE 1 END';
      ATargetQuery.SQL.Text := SqlText;
      ATargetQuery.ParamByName('procurarpor').AsString := '%' + AFiltro.TextoBusca + '%';
    end;
  end;

  ATargetQuery.Open;
  Result := ATargetQuery.Active;
end;

function TEntidadeRepository.ObterOcorrenciaCodigo(const AGeoEntCod: string): string;
var
  Qry: TFDQuery;
begin
  Result := '';
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT ocorcod FROM user_geoapolo_entidade WITH(NOLOCK) WHERE geoentcod = :geoentcod';
    Qry.ParamByName('geoentcod').AsString := AGeoEntCod;
    Qry.Open;
    if not Qry.IsEmpty then
      Result := Qry.FieldByName('ocorcod').AsString;
  finally
    Qry.Free;
  end;
end;

procedure TEntidadeRepository.RegistrarOcorrenciaIgnorada(const ACodEmpresa, AOcorCod, ACodUsuario: string);
var
  Cmd: TFDCommand;
begin
  // TODO: [SQLAlchemy Migration]
  // Chamada de Stored Procedure SQL Server com text() e binds:
  // await session.execute(text("EXEC dbo.User_geraocorrencia_projetosv2 @p_empcod=:emp, ..."), {...})
  Cmd := TFDCommand.Create(nil);
  try
    Cmd.Connection := FConn;
    Cmd.CommandText.Text :=
      'EXEC dbo.User_geraocorrencia_projetosv2 ' +
      '  @p_empcod    = :p_empcod, ' +
      '  @p_tipo      = :p_tipo, ' +
      '  @p_modo      = :p_modo, ' +
      '  @p_compl1    = :p_compl1, ' +
      '  @p_compl2    = :p_compl2, ' +
      '  @p_ocorcod   = :p_ocorcod, ' +
      '  @p_compl3    = :p_compl3, ' +
      '  @p_usucod    = :p_usucod, ' +
      '  @p_descricao = :p_descricao, ' +
      '  @p_codmotivo = :p_codmotivo, ' +
      '  @p_compl4    = :p_compl4, ' +
      '  @p_data1     = :p_data1, ' +
      '  @p_data2     = :p_data2, ' +
      '  @p_compl5    = :p_compl5';

    Cmd.ParamByName('p_empcod').AsString    := ACodEmpresa;
    Cmd.ParamByName('p_tipo').AsString      := 'F';
    Cmd.ParamByName('p_modo').AsString      := 'INDIVIDUAL';
    Cmd.ParamByName('p_compl1').AsString    := '';
    Cmd.ParamByName('p_compl2').AsString    := '';
    Cmd.ParamByName('p_ocorcod').AsString   := AOcorCod;
    Cmd.ParamByName('p_compl3').AsString    := '';
    Cmd.ParamByName('p_usucod').AsString    := ACodUsuario;
    Cmd.ParamByName('p_descricao').AsString := 'FOI IGNORADA A ATUALIZAÇÃO DE CADASTRO POR ESTAR ATUALIZADO';
    Cmd.ParamByName('p_codmotivo').AsString := '0000012';
    Cmd.ParamByName('p_compl4').AsString    := '';
    Cmd.ParamByName('p_data1').Clear;
    Cmd.ParamByName('p_data2').Clear;
    Cmd.ParamByName('p_compl5').AsString    := '';

    Cmd.Execute;
  finally
    Cmd.Free;
  end;
end;

function TEntidadeRepository.IgnorarAtualizacaoAlvo(const AGeoEntCod, AUsuCodApolo, ACodEmpresa, ACodUsuario: string): Boolean;
var
  Qry: TFDQuery;
  VOcorCod: string;
begin
  Result := False;
  FConn.StartTransaction;
  try
    Qry := TFDQuery.Create(nil);
    try
      Qry.Connection := FConn;
      Qry.SQL.Text :=
        'UPDATE USER_geoapolo_Entidade ' +
        '   SET atualizou_apolo = ''S'', usucod_atualizou_apolo = :usucodapolo ' +
        ' WHERE geoentcod = :geoentcod';
      Qry.ParamByName('usucodapolo').AsString := AUsuCodApolo;
      Qry.ParamByName('geoentcod').AsString   := AGeoEntCod;
      Qry.ExecSQL;

      VOcorCod := ObterOcorrenciaCodigo(AGeoEntCod);
      RegistrarOcorrenciaIgnorada(ACodEmpresa, VOcorCod, ACodUsuario);

      FConn.Commit;
      Result := True;
    finally
      Qry.Free;
    end;
  except
    FConn.Rollback;
    raise;
  end;
end;

function TEntidadeRepository.AtualizarEntCodAlvoViaCPF(const AGeoEntCod: string): string;
var
  QryBuscaDoc, QryBuscaAlvo, QryUpd: TFDQuery;
  VCPF, VEntCodAlvo: string;
begin
  Result := '';
  QryBuscaDoc  := TFDQuery.Create(nil);
  QryBuscaAlvo := TFDQuery.Create(nil);
  QryUpd       := TFDQuery.Create(nil);
  try
    QryBuscaDoc.Connection  := FConn;
    QryBuscaAlvo.Connection := FConn;
    QryUpd.Connection       := FConn;

    QryBuscaDoc.SQL.Text :=
      'SELECT geonumerodocumento FROM USER_geoapolo_entidade_documentos WITH(NOLOCK) ' +
      ' WHERE geoentcod = :geoentcod AND geotipodocumento = ''CPF/CNPJ''';
    QryBuscaDoc.ParamByName('geoentcod').AsString := AGeoEntCod;
    QryBuscaDoc.Open;

    if not QryBuscaDoc.IsEmpty then
    begin
      VCPF := QryBuscaDoc.FieldByName('geonumerodocumento').AsString;
      QryBuscaAlvo.SQL.Text :=
        'SELECT entcod FROM entidades_geoapolo WITH(NOLOCK) WHERE entcpfcgc = :cpf';
      QryBuscaAlvo.ParamByName('cpf').AsString := VCPF;
      QryBuscaAlvo.Open;

      if not QryBuscaAlvo.IsEmpty then
      begin
        VEntCodAlvo := QryBuscaAlvo.FieldByName('entcod').AsString;
        QryUpd.SQL.Text :=
          'UPDATE USER_geoapolo_entidade SET entcod = :entcod WHERE geoentcod = :geoentcod';
        QryUpd.ParamByName('entcod').AsString    := VEntCodAlvo;
        QryUpd.ParamByName('geoentcod').AsString := AGeoEntCod;
        QryUpd.ExecSQL;
        Result := VEntCodAlvo;
      end;
    end;
  finally
    QryBuscaDoc.Free;
    QryBuscaAlvo.Free;
    QryUpd.Free;
  end;
end;

function TEntidadeRepository.ObterCredenciaisAlvo(const ACodUsuario: string): TCredencialAlvoDTO;
var
  Qry: TFDQuery;
begin
  Result.UsuarioAlvo    := '';
  Result.SenhaAlvoCripto := '';
  Result.TokenAlvo      := '';
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'SELECT usucod_apolo, senha_alvo FROM USER_geoapolo_usuarios WITH(NOLOCK) WHERE usucod = :codigousuario';
    Qry.ParamByName('codigousuario').AsString := ACodUsuario;
    Qry.Open;
    if not Qry.IsEmpty then
    begin
      Result.UsuarioAlvo    := Trim(Qry.FieldByName('usucod_apolo').AsString);
      Result.SenhaAlvoCripto := Trim(Qry.FieldByName('senha_alvo').AsString);
    end;
  finally
    Qry.Free;
  end;
end;

procedure TEntidadeRepository.SalvarCredenciaisAlvo(const ACodUsuario, AUsuApolo, ASenhaCripto: string);
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'UPDATE USER_geoapolo_usuarios ' +
      '   SET usucod_apolo = :usucodapolo, senha_alvo = :senhaalvo ' +
      ' WHERE usucod = :codigousuario';
    Qry.ParamByName('usucodapolo').AsString   := AUsuApolo;
    Qry.ParamByName('senhaalvo').AsString     := ASenhaCripto;
    Qry.ParamByName('codigousuario').AsString := ACodUsuario;
    Qry.ExecSQL;
  finally
    Qry.Free;
  end;
end;

procedure TEntidadeRepository.AtualizarVinculoEntCod(const AGeoEntCod, AEntCod: string);
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'UPDATE USER_geoapolo_entidade SET entcod = :entcod WHERE geoentcod = :geoentcod';
    Qry.ParamByName('entcod').AsString    := AEntCod;
    Qry.ParamByName('geoentcod').AsString := AGeoEntCod;
    Qry.ExecSQL;
  finally
    Qry.Free;
  end;
end;

procedure TEntidadeRepository.CarregarDadosComparacao(const AGeoEntCod, AEntCod: string; AQrySVE, AQryAlvo: TFDQuery);
begin
  AQrySVE.Close;
  AQrySVE.Connection := FConn;
  AQrySVE.SQL.Text := 'SELECT * FROM entidades_geoapolo WITH(NOLOCK) WHERE geoentcod = :geoentcod';
  AQrySVE.ParamByName('geoentcod').AsString := AGeoEntCod;
  AQrySVE.Open;

  AQryAlvo.Close;
  AQryAlvo.Connection := FConn;
  AQryAlvo.SQL.Text := 'SELECT * FROM entidades_apolo WITH(NOLOCK) WHERE entcod = :entcod';
  AQryAlvo.ParamByName('entcod').AsString := AEntCod;
  AQryAlvo.Open;
end;

end.
