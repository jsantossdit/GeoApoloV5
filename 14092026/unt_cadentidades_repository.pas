unit unt_cadentidades_repository;

interface

uses
  System.SysUtils, System.Classes, Data.DB, FireDAC.Comp.Client,
  FireDAC.Stan.Param, FireDAC.Stan.Option, unt_cadentidades_types;

type
  ICadastroEntidadeRepository = interface
    ['{8A6133DF-9C78-4D2B-8147-1D7F54728519}']
    function EntidadeExisteGeoApolo(const ACodigo: string): Boolean;
    procedure GravarGeoApolo(const ADados: TEntidadeCompletaDTO);
    procedure GravarAlvo(const ADados: TEntidadeCompletaDTO);
    function BuscarNomeBanco(const ABcoNum: string): string;
    function BuscarNomeCidadeUF(const ACidCod: string; out ANomeCidade, AUF: string): Boolean;
    procedure AtualizarLogEntidadeApolo(const AEntCod: string);
  end;

  TCadastroEntidadeRepository = class(TInterfacedObject, ICadastroEntidadeRepository)
  private
    FConn: TFDConnection;
  public
    constructor Create(AConnection: TFDConnection);
    function EntidadeExisteGeoApolo(const ACodigo: string): Boolean;
    procedure GravarGeoApolo(const ADados: TEntidadeCompletaDTO);
    procedure GravarAlvo(const ADados: TEntidadeCompletaDTO);
    function BuscarNomeBanco(const ABcoNum: string): string;
    function BuscarNomeCidadeUF(const ACidCod: string; out ANomeCidade, AUF: string): Boolean;
    procedure AtualizarLogEntidadeApolo(const AEntCod: string);
  end;

implementation

constructor TCadastroEntidadeRepository.Create(AConnection: TFDConnection);
begin
  inherited Create;
  if not Assigned(AConnection) then
    raise Exception.Create('TCadastroEntidadeRepository: Instância de TFDConnection é obrigatória.');
  FConn := AConnection;
end;

function TCadastroEntidadeRepository.EntidadeExisteGeoApolo(const ACodigo: string): Boolean;
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    // TODO: [SQLAlchemy Migration]
    // stmt = select(exists().where(UserGeoApoloEntidade.geoentcod == codigo)).with_hint(UserGeoApoloEntidade, 'WITH (NOLOCK)', 'mssql')
    // return await session.scalar(stmt)
    Qry.SQL.Text := 'SELECT 1 FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE geoentcod = :entcod';
    Qry.ParamByName('entcod').AsString := ACodigo;
    Qry.Open;
    Result := not Qry.IsEmpty;
  finally
    Qry.Free;
  end;
end;

procedure TCadastroEntidadeRepository.GravarGeoApolo(const ADados: TEntidadeCompletaDTO);
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    FConn.StartTransaction;
    try
      if ADados.Modo = mgInclusao then
      begin
        // TODO: [SQLAlchemy Migration]
        // session.add(UserGeoApoloEntidade(**dados))
        Qry.SQL.Text :=
          'INSERT INTO USER_geoapolo_entidade ( ' +
          '  geoentcod, geotipotratcod, geoentnome, geoentnomefantasia, tipolograd, ' +
          '  geoentender, geoenderno, geoentendercomp, geoentbair, geoentdatacad, ' +
          '  geoentdesdedata, geoentcep, geocidcod, geoentcxapost, geoentgenero, ' +
          '  geolocalreferencia_ender, geotipofj, geofalecido, codigo_grauescolaridade, ' +
          '  geocargocodestr, geoentdataanivfund, geoentestcivil, entcod, cidcodapolo ' +
          ') VALUES ( ' +
          '  :geoentcod, :geotipotratcod, :geoentnome, :geoentnomefantasia, :tipolograd, ' +
          '  :geoentender, :geoenderno, :geoentendercomp, :geoentbair, :geoentdatacad, ' +
          '  :geoentdesdedata, :geoentcep, :geocidcod, :geoentcxapost, :geoentgenero, ' +
          '  :geolocalreferencia_ender, :geotipofj, :geofalecido, :codigo_grauescolaridade, ' +
          '  :geocargocodestr, :geoentdataanivfund, :geoentestcivil, :entcod, :cidcodapolo ' +
          ')';
      end
      else
      begin
        // TODO: [SQLAlchemy Migration]
        // stmt = update(UserGeoApoloEntidade).where(UserGeoApoloEntidade.geoentcod == codigo).values(**dados)
        // await session.execute(stmt)
        Qry.SQL.Text :=
          'UPDATE USER_geoapolo_entidade SET ' +
          '  geotipotratcod = :geotipotratcod, geoentnome = :geoentnome, ' +
          '  geoentnomefantasia = :geoentnomefantasia, tipolograd = :tipolograd, ' +
          '  geoentender = :geoentender, geoenderno = :geoenderno, ' +
          '  geoentendercomp = :geoentendercomp, geoentbair = :geoentbair, ' +
          '  geoentdatacad = :geoentdatacad, geoentcep = :geoentcep, geocidcod = :geocidcod, ' +
          '  cidcodapolo = :cidcodapolo, geoentcxapost = :geoentcxapost, ' +
          '  geoentgenero = :geoentgenero, geolocalreferencia_ender = :geolocalreferencia_ender, ' +
          '  geofalecido = :geofalecido, codigo_grauescolaridade = :codigo_grauescolaridade, ' +
          '  geocargocodestr = :geocargocodestr, geoentdataanivfund = :geoentdataanivfund, ' +
          '  geoentestcivil = :geoentestcivil, entcod = :entcod ' +
          'WHERE geoentcod = :geoentcod';
      end;

      Qry.ParamByName('geoentcod').AsString                := ADados.Pessoais.Codigo;
      Qry.ParamByName('geotipotratcod').AsString           := ADados.Pessoais.TipoTratamento;
      Qry.ParamByName('geoentnome').AsString               := ADados.Pessoais.Nome;
      Qry.ParamByName('geoentnomefantasia').AsString       := ADados.Pessoais.NomeFantasia;
      Qry.ParamByName('tipolograd').AsString               := ADados.Endereco.Logradouro;
      Qry.ParamByName('geoentender').AsString             := ADados.Endereco.Endereco;
      Qry.ParamByName('geoenderno').AsString              := ADados.Endereco.Numero;
      Qry.ParamByName('geoentendercomp').AsString         := ADados.Endereco.Complemento;
      Qry.ParamByName('geoentbair').AsString              := ADados.Endereco.Bairro;
      Qry.ParamByName('geoentdatacad').AsString           := ADados.Pessoais.DataCadastro;
      Qry.ParamByName('geoentdesdedata').AsString         := ADados.Pessoais.DataCadastro;
      Qry.ParamByName('geoentcep').AsString               := ADados.Endereco.CEP;
      Qry.ParamByName('geocidcod').AsString               := ADados.Endereco.CodigoCidade;
      Qry.ParamByName('cidcodapolo').AsString             := ADados.Endereco.CodigoCidade;
      Qry.ParamByName('geoentcxapost').AsString           := ADados.Endereco.CaixaPostal;
      Qry.ParamByName('geoentgenero').AsString            := ADados.Pessoais.Genero;
      Qry.ParamByName('geolocalreferencia_ender').AsString := ADados.Endereco.Referencia;
      Qry.ParamByName('geotipofj').AsString               := ADados.Pessoais.TipoFJ;
      if ADados.Pessoais.Falecido then
        Qry.ParamByName('geofalecido').AsString := 'S'
      else
        Qry.ParamByName('geofalecido').AsString := 'N';
      Qry.ParamByName('codigo_grauescolaridade').AsString := ADados.Pessoais.GrauEscolaridade;
      Qry.ParamByName('geocargocodestr').AsString         := ADados.Pessoais.CargoCodigo;
      Qry.ParamByName('geoentestcivil').AsString          := ADados.Pessoais.EstadoCivil;
      Qry.ParamByName('entcod').AsString                  := ADados.Pessoais.CodigoAlternativo;

      if Trim(ADados.Pessoais.DataNascimento) = '' then
        Qry.ParamByName('geoentdataanivfund').Clear
      else
        Qry.ParamByName('geoentdataanivfund').AsString := ADados.Pessoais.DataNascimento;

      Qry.ExecSQL;
      FConn.Commit;
    except
      FConn.Rollback;
      raise;
    end;
  finally
    Qry.Free;
  end;
end;

procedure TCadastroEntidadeRepository.GravarAlvo(const ADados: TEntidadeCompletaDTO);
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    FConn.StartTransaction;
    try
      // Atualização na tabela entidade da base Alvo
      Qry.SQL.Text :=
        'UPDATE entidade SET ' +
        '  entnome = :entnome, tipotratcod = :tipotratcod, entnomefant = :entnomefant, ' +
        '  entlograd = :entlograd, entender = :entender, entenderno = :entenderno, ' +
        '  entendercomp = :entendercomp, entbair = :entbair, entcep = :entcep, cidcod = :cidcod, ' +
        '  enttipofj = :enttipofj, entcxapost = :entcxapost, entgenero = :entgenero, ' +
        '  cargocodestr = :cargocodestr, entestcivil = :entestcivil, entgrauescol = :entgrauescol, ' +
        '  entdataanivfund = :entdataanivfund, entdatacad = :entdatacad ' +
        'WHERE entcod = :entcod';

      Qry.ParamByName('entnome').AsString    := ADados.Pessoais.Nome;
      Qry.ParamByName('tipotratcod').AsString := ADados.Pessoais.TipoTratamento;
      Qry.ParamByName('entnomefant').AsString := ADados.Pessoais.NomeFantasia;
      Qry.ParamByName('entlograd').AsString  := ADados.Endereco.Logradouro;
      Qry.ParamByName('entender').AsString   := ADados.Endereco.Endereco;
      Qry.ParamByName('entenderno').AsString := ADados.Endereco.Numero;
      Qry.ParamByName('entendercomp').AsString := ADados.Endereco.Complemento;
      Qry.ParamByName('entbair').AsString    := ADados.Endereco.Bairro;
      Qry.ParamByName('entcep').AsString     := ADados.Endereco.CEP;
      Qry.ParamByName('cidcod').AsString     := ADados.Endereco.CodigoCidade;
      Qry.ParamByName('enttipofj').AsString  := ADados.Pessoais.TipoFJ;
      Qry.ParamByName('entcxapost').AsString := ADados.Endereco.CaixaPostal;
      Qry.ParamByName('entgenero').AsString  := ADados.Pessoais.Genero;
      Qry.ParamByName('cargocodestr').AsString := ADados.Pessoais.CargoCodigo;
      Qry.ParamByName('entestcivil').AsString := ADados.Pessoais.EstadoCivil;
      Qry.ParamByName('entgrauescol').AsString := ADados.Pessoais.GrauEscolaridade;
      Qry.ParamByName('entcod').AsString     := ADados.Pessoais.Codigo;

      if Trim(ADados.Pessoais.DataNascimento) = '' then
        Qry.ParamByName('entdataanivfund').Clear
      else
        Qry.ParamByName('entdataanivfund').AsString := ADados.Pessoais.DataNascimento;

      if Trim(ADados.Pessoais.DataCadastro) = '' then
        Qry.ParamByName('entdatacad').Clear
      else
        Qry.ParamByName('entdatacad').AsString := ADados.Pessoais.DataCadastro;

      Qry.ExecSQL;

      // Atualiza tabela de extensão u_entidade
      Qry.SQL.Text := 'UPDATE u_entidade SET USERFalecido = :falecido WHERE entcod = :entcod';
      if ADados.Pessoais.Falecido then
        Qry.ParamByName('falecido').AsString := 'S'
      else
        Qry.ParamByName('falecido').AsString := 'N';
      Qry.ParamByName('entcod').AsString := ADados.Pessoais.Codigo;
      Qry.ExecSQL;

      AtualizarLogEntidadeApolo(ADados.Pessoais.Codigo);

      FConn.Commit;
    except
      FConn.Rollback;
      raise;
    end;
  finally
    Qry.Free;
  end;
end;

function TCadastroEntidadeRepository.BuscarNomeBanco(const ABcoNum: string): string;
var
  Qry: TFDQuery;
begin
  Result := '';
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT geobconome FROM USER_geoapolo_bancos WITH (NOLOCK) WHERE geobconum = :bconum';
    Qry.ParamByName('bconum').AsString := ABcoNum;
    Qry.Open;
    if not Qry.IsEmpty then
      Result := Qry.FieldByName('geobconome').AsString;
  finally
    Qry.Free;
  end;
end;

function TCadastroEntidadeRepository.BuscarNomeCidadeUF(const ACidCod: string; out ANomeCidade, AUF: string): Boolean;
var
  Qry: TFDQuery;
begin
  Result := False;
  ANomeCidade := '';
  AUF := '';
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text := 'SELECT cidnomecomp, ufsigla FROM user_geoapolo_cidades WITH (NOLOCK) WHERE geocidcod = :cidcod';
    Qry.ParamByName('cidcod').AsString := ACidCod;
    Qry.Open;
    if not Qry.IsEmpty then
    begin
      ANomeCidade := Qry.FieldByName('cidnomecomp').AsString;
      AUF         := Qry.FieldByName('ufsigla').AsString;
      Result      := True;
    end;
  finally
    Qry.Free;
  end;
end;

procedure TCadastroEntidadeRepository.AtualizarLogEntidadeApolo(const AEntCod: string);
var
  Qry: TFDQuery;
begin
  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := FConn;
    Qry.SQL.Text :=
      'UPDATE USER_geoapolo_entidade ' +
      '   SET atualizou_apolo = ''S'', data_atualizou_apolo = GETDATE() ' +
      ' WHERE entcod = :entcod';
    Qry.ParamByName('entcod').AsString := AEntCod;
    Qry.ExecSQL;
  finally
    Qry.Free;
  end;
end;

end.
