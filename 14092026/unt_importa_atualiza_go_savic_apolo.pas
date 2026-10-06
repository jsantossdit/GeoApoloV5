unit unt_importa_atualiza_go_savic_apolo;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.ComCtrls, Vcl.StdCtrls, Vcl.Buttons,
  Vcl.ExtCtrls, Data.DB, Vcl.Grids, Vcl.DBGrids, Vcl.Samples.Gauges, Vcl.Mask,
  FireDAC.Comp.Client, FireDAC.Stan.Param;

type
  Tfrmimporta_atualizaGOSavicGeoApolo = class(TForm)
    Panel1: TPanel;
    spbimportar: TSpeedButton;
    spblimpar: TSpeedButton;
    spblocalizar: TSpeedButton;
    spbexcluir: TSpeedButton;
    spbretornar: TSpeedButton;
    lblmsg1: TLabel;
    StatusBar1: TStatusBar;
    GroupBox1: TGroupBox;
    GroupBox2: TGroupBox;
    gridgruposdeoracao: TDBGrid;
    GroupBox3: TGroupBox;
    lblquantidadegosavic: TLabel;
    lblqtdegohomolog: TLabel;
    lblqtdegonaohomolog: TLabel;
    lblqtdetotalgo: TLabel;
    lblqtdegohomologados: TLabel;
    lblqtdegonaohomologados: TLabel;
    btnimportagruporacao: TBitBtn;
    Gauge1: TGauge;
    btnconectabasesavic: TBitBtn;
    lblgoemandamento: TLabel;
    lblqtdegoemandamento: TLabel;
    lbldtatualizacao: TLabel;
    mskdtinicial: TMaskEdit;
    mskdtfinal: TMaskEdit;
    lblintervalo: TLabel;
    lblregistrosapurados: TLabel;
    lblnregistrosapurados: TLabel;
    GroupBoxCategorias: TGroupBox;
    lblcategcodestr_go: TLabeledEdit;
    spbbuscacat_go: TSpeedButton;
    lblcategnome_go: TLabel;
    lblcategcodestr_coord: TLabeledEdit;
    spbbuscacat_coord: TSpeedButton;
    lblcategnome_coord: TLabel;
    spbmapeamentocampos: TBitBtn;
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbretornarClick(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure btnconectabasesavicClick(Sender: TObject);
    procedure btnimportagruporacaoClick(Sender: TObject);
    procedure mskdtinicialKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure mskdtfinalKeyUp(Sender: TObject; var Key: Word;
      Shift: TShiftState);
    procedure spbbuscacat_goClick(Sender: TObject);
    procedure spbbuscacat_coordClick(Sender: TObject);
    procedure lblcategcodestr_goExit(Sender: TObject);
    procedure lblcategcodestr_coordExit(Sender: TObject);
    procedure spbmapeamentocamposClick(Sender: TObject);
  private
    { Private declarations }
    procedure CarregaNomeCategoria(const ACodigo: string; ALabel: TLabel);
  public
    { Public declarations }
    ventcod: string;
    procedure CalcularApuracao;
  end;

var
  frmimporta_atualizaGOSavicGeoApolo: Tfrmimporta_atualizaGOSavicGeoApolo;

function estatistica_go_savic(consulta: string): string;
function lista_go_jaimportados: string;
function retorna_cidade_estado(cidade: string; estado: string; formulario: TForm): string;

implementation

{$R *.dfm}

uses funcoes, unt_dados, unt_principal, unt_consultav3, System.StrUtils, unt_mapeamento_savic_entidade;

procedure Tfrmimporta_atualizaGOSavicGeoApolo.spbmapeamentocamposClick(Sender: TObject);
begin
  if not Assigned(frmmapeamento_savic_entidade) then
    Application.CreateForm(Tfrmmapeamento_savic_entidade, frmmapeamento_savic_entidade);
  frmmapeamento_savic_entidade.ShowModal;
end;

procedure Tfrmimporta_atualizaGOSavicGeoApolo.btnconectabasesavicClick(Sender: TObject);
begin
  if not conecta_banco_savic then
  begin
    ShowMessage('Não foi possível conectar à base do SAVIC.');
    Exit;
  end;

  lblqtdetotalgo.Caption          := estatistica_go_savic('TOTALGO');
  lblqtdegohomologados.Caption    := estatistica_go_savic('TOTALGOHOMOLOGADO');
  lblqtdegonaohomologados.Caption := estatistica_go_savic('TOTALGONAOHOMOLOGADO');
  lblqtdegoemandamento.Caption    := estatistica_go_savic('EMANDAMENTO');

  lblqtdetotalgo.Refresh;
  lblqtdegohomologados.Refresh;
  lblqtdegonaohomologados.Refresh;
  lblqtdegoemandamento.Refresh;
end;

function estatistica_go_savic(consulta: string): string;
var
  Qry: TFDQuery;
begin
  Result := '0';
  if not Assigned(modulo_dados) or not Assigned(modulo_dados.fdbancosavic) then Exit;
  if not modulo_dados.fdbancosavic.Connected then
  begin
    if not conecta_banco_savic then Exit;
  end;

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := modulo_dados.fdbancosavic;
    if consulta = 'TOTALGO' then
      Qry.SQL.Text := 'SELECT COUNT(1) AS Total FROM go'
    else if consulta = 'TOTALGOHOMOLOGADO' then
      Qry.SQL.Text := 'SELECT COUNT(1) AS Total FROM go INNER JOIN go_situacao gs ON go.go_situacaoid = gs.go_situacaoId WHERE UPPER(gs.descricao) = ''HOMOLOGADO'''
    else if consulta = 'TOTALGONAOHOMOLOGADO' then
      Qry.SQL.Text := 'SELECT COUNT(1) AS Total FROM go INNER JOIN go_situacao gs ON go.go_situacaoid = gs.go_situacaoId WHERE UPPER(gs.descricao) LIKE ''%N%O HOMOLOGADO%'''
    else if consulta = 'EMANDAMENTO' then
      Qry.SQL.Text := 'SELECT COUNT(1) AS Total FROM go INNER JOIN go_situacao gs ON go.go_situacaoid = gs.go_situacaoId WHERE UPPER(gs.descricao) = ''EM ANDAMENTO''';

    Qry.Open;
    if not Qry.IsEmpty then
      Result := Qry.Fields[0].AsString;
    Qry.Close;
  finally
    Qry.Free;
  end;
end;

function lista_go_jaimportados: string;
begin
  Result := '';
  if not Assigned(modulo_dados) or not Assigned(frmimporta_atualizaGOSavicGeoApolo) then Exit;
  with modulo_dados, frmimporta_atualizaGOSavicGeoApolo do
  begin
    fdquerysql4.Close;
    fdquerysql4.Connection := fdbanco;
    fdquerysql4.SQL.Text := 'SELECT * FROM USER_geoapolo_gruposdeoracao ORDER BY gocodigo ASC';
    try
      fdquerysql4.Open;
      dtsfdquerysql4.DataSet := fdquerysql4;
      gridgruposdeoracao.DataSource := dtsfdquerysql4;
      gridgruposdeoracao.Refresh;
    except
    end;
  end;
end;

procedure Tfrmimporta_atualizaGOSavicGeoApolo.CalcularApuracao;
var
  Qry: TFDQuery;
  dIni, dFim: TDateTime;
  sIni, sFim: string;
begin
  if not TryStrToDate(mskdtinicial.Text, dIni) then
  begin
    ShowMessage('Informe uma data inicial válida no formato dd/mm/aaaa.');
    mskdtinicial.SetFocus;
    Exit;
  end;
  if not TryStrToDate(mskdtfinal.Text, dFim) then
  begin
    ShowMessage('Informe uma data final válida no formato dd/mm/aaaa.');
    mskdtfinal.SetFocus;
    Exit;
  end;
  if dIni > dFim then
  begin
    ShowMessage('A data inicial não pode ser superior à data final.');
    mskdtinicial.SetFocus;
    Exit;
  end;

  if not modulo_dados.fdbancosavic.Connected then
  begin
    if not conecta_banco_savic then
    begin
      ShowMessage('Não foi possível conectar ao banco de dados do Savic.');
      Exit;
    end;
  end;

  sIni := FormatDateTime('yyyy-mm-dd', dIni);
  sFim := FormatDateTime('yyyy-mm-dd', dFim);

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := modulo_dados.fdbancosavic;
    Qry.SQL.Text := 'SELECT COUNT(1) AS Total FROM view_go_ativosv2 WHERE DataAtualizacao_go BETWEEN ' +
                    QuotedStr(sIni) + ' AND ' + QuotedStr(sFim);
    Qry.Open;
    if not Qry.IsEmpty then
      lblnregistrosapurados.Caption := Qry.FieldByName('Total').AsString
    else
      lblnregistrosapurados.Caption := '0';
    lblnregistrosapurados.Refresh;
  finally
    Qry.Free;
  end;
end;

procedure Tfrmimporta_atualizaGOSavicGeoApolo.btnimportagruporacaoClick(Sender: TObject);
var
  QrySavic, QryGeo: TFDQuery;
  dIni, dFim: TDateTime;
  sIni, sFim, sSql: string;
  vcidcod, vcadastrocoord, vcpfcoordenador, vcpfLimpo, ventcodApolo: string;
  vgeoentcod, vtipologradouro, vendereco, vgenero: string;
  nTotal, nAtual: Integer;
  vgoid, vNomeGO, vLocalReuniao, vTipoLocal, vSituacao, vDiaSemana, vCaractGrupo: string;
  vDataCadGO, vDataAtuGO, vObsInfo, vObsAtual, vObsFinal, vPendencias: string;
  vgeoentcodgo, ventcodGO, ventcodGOSQL, vCidCodValidado, vCidadeNome, vEstadoUF: string;
  vCatGO, vCatCoord: string;
  vcpfCoordPesq, vcpfCoordLimpo, vgeoentcod_coord_contato, vTipoTratCoord, ventcodCoord: string;
  vDtIniCoordSQL, vDtFimCoordSQL: string;
  vEntidadeGOExiste: Boolean;
  nPosInfo: Integer;
  sArquivoInconsistencias, sLinhaLog, sArquivoOcorrencias: string;
  FLog, FOcorrencias: TextFile;
  slInseridos, slApenasGrupos: TStringList;
  iLog: Integer;
begin
  if not TryStrToDate(mskdtinicial.Text, dIni) or not TryStrToDate(mskdtfinal.Text, dFim) then
  begin
    ShowMessage('Informe as datas inicial e final no formato dd/mm/aaaa.');
    Exit;
  end;

  slInseridos := TStringList.Create;
  slApenasGrupos := TStringList.Create;

  if not modulo_dados.fdbancosavic.Connected then
  begin
    if not conecta_banco_savic then
    begin
      ShowMessage('Não foi possível conectar à base do SAVIC.');
      Exit;
    end;
  end;

  if not modulo_dados.fdbanco.Connected then
  begin
    conecta_banco('FDALVO');
    if not modulo_dados.fdbanco.Connected then
    begin
      ShowMessage('Não foi possível conectar à base GeoAlvo / Alvo.');
      Exit;
    end;
  end;

  sIni := FormatDateTime('yyyy-mm-dd', dIni);
  sFim := FormatDateTime('yyyy-mm-dd', dFim);

  QrySavic := TFDQuery.Create(nil);
  QryGeo   := TFDQuery.Create(nil);
  try
    QrySavic.Connection := modulo_dados.fdbancosavic;
    QryGeo.Connection   := modulo_dados.fdbanco;

    sSql := 'SELECT vga.goid, UPPER(vga.go) AS GrupodeOracao, UPPER(vga.cidade) AS Cidade, UPPER(vga.estado) AS Estado, ' +
            'vga.dias_semana, vga.horario, UPPER(vga.situacao) AS Situacao, UPPER(vga.caracteristica) AS CaracteristicaGrupo, ' +
            'UPPER(vga.local) AS LOCAL, UPPER(vga.tipo_local) AS TipoLocalReuniao, vga.datainclusao_go, vga.dataatualizacao_go, ' +
            'vga.cadastroid_coord, UPPER(vga.coordenador) AS Coordenador, vga.genero_coord, vga.ender_coord AS EnderecoCoordenador, ' +
            'vga.Numero_CasaCoord, vga.Compl_coord, UPPER(vga.bairrocoord) AS Bairro, vga.CepCoord, ' +
            'vga.cpf_coordenador, vga.rgcoord, vga.rgcoordemissor, vga.CaixaPostal_Coord, vga.Telefone_Coord, ' +
            'vga.TelCom_Coord, vga.CelularCoord1, vga.celularcoord2, vga.dioceseId, vga.diocesecoordenador, vga.email, ' +
            'vga.indeterminado AS MandatoIndeterminado, vga.Dataini_coordenacao, vga.datafim_coordenacao, ' +
            'vga.useratualizacao, vga.ultimaalteracaofeitapor ' +
            'FROM view_go_ativosv2 vga ' +
            'WHERE vga.DataAtualizacao_go BETWEEN ' + QuotedStr(sIni) + ' AND ' + QuotedStr(sFim);

    QrySavic.SQL.Text := sSql;
    QrySavic.Open;

    if QrySavic.IsEmpty then
    begin
      ShowMessage('Nenhum registro apurado no SAVIC para o período informado.');
      Exit;
    end;

    // Garante coluna entcod na tabela de coordenadores
    try
      modulo_dados.fdbanco.ExecSQL(
        'IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(''USER_geoapolo_coordenadores_grupodeoracao'') AND name = ''entcod'') ' +
        'BEGIN ' +
        '  IF EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(''USER_geoapolo_coordenadores_grupodeoracao'') AND name = ''entcod_apolo'') ' +
        '  BEGIN ' +
        '    ALTER TABLE USER_geoapolo_coordenadores_grupodeoracao ADD entcod VARCHAR(20) NULL; ' +
        '    EXEC(''UPDATE USER_geoapolo_coordenadores_grupodeoracao SET entcod = entcod_apolo WHERE entcod IS NULL''); ' +
        '  END ' +
        '  ELSE ' +
        '    ALTER TABLE USER_geoapolo_coordenadores_grupodeoracao ADD entcod VARCHAR(20) NULL; ' +
        'END');
    except
    end;

    nTotal := QrySavic.RecordCount;
    lblnregistrosapurados.Caption := IntToStr(nTotal);
    lblnregistrosapurados.Refresh;
    Gauge1.MinValue := 0;
    Gauge1.MaxValue := nTotal;
    Gauge1.Progress := 0;
    nAtual := 0;

    QrySavic.First;
    while not QrySavic.Eof do
    begin
      Inc(nAtual);
      vcidcod := retorna_cidade_estado(QrySavic.FieldByName('cidade').AsString, QrySavic.FieldByName('estado').AsString, Self);
      vcadastrocoord := QrySavic.FieldByName('cadastroid_coord').AsString;
      vcpfcoordenador := Trim(QrySavic.FieldByName('cpf_coordenador').AsString);
      vcpfLimpo := buscatroca(buscatroca(buscatroca(vcpfcoordenador, '.', ''), '-', ''), '/', '');

      // Normaliza Logradouro
      vendereco := Trim(QrySavic.FieldByName('EnderecoCoordenador').AsString);
      if (Copy(vendereco, 1, 3) = 'RUA') or (Copy(vendereco, 1, 3) = 'Rua') then
        vtipologradouro := 'R.'
      else if (Copy(vendereco, 1, 7) = 'AVENIDA') or (Copy(vendereco, 1, 7) = 'Avenida') then
        vtipologradouro := 'Av.'
      else
        vtipologradouro := 'R.';

      vgenero := Trim(QrySavic.FieldByName('genero_coord').AsString);
      if (vgenero = '') or (vgenero = 'M') then vgenero := 'M' else vgenero := 'F';

      // 1. Busca entcod_apolo na base Alvo pelo CPF
      ventcodApolo := '0';
      if vcpfLimpo <> '' then
      begin
        QryGeo.Close;
        QryGeo.SQL.Text := 'SELECT TOP 1 entcod FROM entidade WITH (NOLOCK) WHERE ' +
                           'REPLACE(REPLACE(REPLACE(entcpfcgc, ''.'', ''''), ''-'', ''''), ''/'', '''') = ' + QuotedStr(vcpfLimpo);
        try
          QryGeo.Open;
          if not QryGeo.IsEmpty then
            ventcodApolo := QryGeo.FieldByName('entcod').AsString;
          QryGeo.Close;
        except
        end;
      end;

      // 2. Busca na tabela USER_geoapolo_entidade_documentos pelo CPF
      vgeoentcod := '';
      if vcpfLimpo <> '' then
      begin
        QryGeo.Close;
        QryGeo.SQL.Text := 'SELECT TOP 1 geoentcod FROM USER_geoapolo_entidade_documentos WITH (NOLOCK) ' +
                           'WHERE geotipodocumento = ''CPF/CNPJ'' AND ' +
                           'REPLACE(REPLACE(REPLACE(geonumerodocumento, ''.'', ''''), ''-'', ''''), ''/'', '''') = ' + QuotedStr(vcpfLimpo);
        try
          QryGeo.Open;
          if not QryGeo.IsEmpty then
            vgeoentcod := QryGeo.FieldByName('geoentcod').AsString;
          QryGeo.Close;
        except
        end;
      end;

      if vgeoentcod <> '' then
      begin
        // UPDATE na tabela USER_geoapolo_entidade preenchendo qualquer informacao padrao faltante
        sSql := 'UPDATE USER_geoapolo_entidade SET ' +
                'geoentnome = CASE WHEN ISNULL(NULLIF(' + QuotedStr(QrySavic.FieldByName('Coordenador').AsString) + ', ''''), '''') <> '''' THEN ' + QuotedStr(QrySavic.FieldByName('Coordenador').AsString) + ' ELSE geoentnome END, ' +
                'geoentnomefantasia = ISNULL(NULLIF(geoentnomefantasia, ''''), ISNULL(NULLIF(' + QuotedStr(QrySavic.FieldByName('Coordenador').AsString) + ', ''''), geoentnome)), ' +
                'tipolograd = ISNULL(NULLIF(tipolograd, 0), 1), ' +
                'geotipotratcod = CASE WHEN ISNULL(geotipotratcod, '''') IN ('''', ''0'') THEN ''00000001'' ELSE geotipotratcod END, ' +
                'geoentender = CASE WHEN ISNULL(NULLIF(' + QuotedStr(vendereco) + ', ''''), '''') <> '''' THEN ' + QuotedStr(vendereco) + ' ELSE geoentender END, ' +
                'geoenderno = CASE WHEN ISNULL(NULLIF(' + QuotedStr(QrySavic.FieldByName('Numero_CasaCoord').AsString) + ', ''''), '''') <> '''' THEN ' + QuotedStr(QrySavic.FieldByName('Numero_CasaCoord').AsString) + ' ELSE ISNULL(geoenderno, ''S/N'') END, ' +
                'geoentendercomp = CASE WHEN ISNULL(NULLIF(' + QuotedStr(QrySavic.FieldByName('Compl_coord').AsString) + ', ''''), '''') <> '''' THEN ' + QuotedStr(QrySavic.FieldByName('Compl_coord').AsString) + ' ELSE geoentendercomp END, ' +
                'geoentbair = CASE WHEN ISNULL(NULLIF(' + QuotedStr(QrySavic.FieldByName('Bairro').AsString) + ', ''''), '''') <> '''' THEN ' + QuotedStr(QrySavic.FieldByName('Bairro').AsString) + ' ELSE geoentbair END, ' +
                'geoentcep = CASE WHEN ISNULL(NULLIF(' + QuotedStr(buscatroca(Copy(QrySavic.FieldByName('CepCoord').AsString, 1, 10), '-', '')) + ', ''''), '''') <> '''' THEN ' + QuotedStr(buscatroca(Copy(QrySavic.FieldByName('CepCoord').AsString, 1, 10), '-', '')) + ' ELSE geoentcep END, ' +
                'geocidcod = CASE WHEN ISNULL(NULLIF(' + QuotedStr(vcidcod) + ', ''''), '''') <> '''' AND ' + QuotedStr(vcidcod) + ' <> ''00000001'' THEN ' + QuotedStr(vcidcod) + ' ELSE ISNULL(NULLIF(geocidcod, ''''), ' + QuotedStr(vcidcod) + ') END, ' +
                'cidcodapolo = CASE WHEN ISNULL(NULLIF(cidcodapolo, ''''), '''') IN ('''', ''0'', ''00000001'') THEN ' + QuotedStr(vcidcod) + ' ELSE cidcodapolo END, ' +
                'geotipofj = ISNULL(NULLIF(geotipofj, ''''), ''Física''), ' +
                'geoentgenero = ISNULL(NULLIF(geoentgenero, ''''), ' + QuotedStr(vgenero) + '), ' +
                'geofalecido = ISNULL(NULLIF(geofalecido, ''''), ''N''), ' +
                'geoentloccobrancaomesmo = ISNULL(NULLIF(geoentloccobrancaomesmo, ''''), ''Sim''), ' +
                'geoentlocentregaomesmo = ISNULL(NULLIF(geoentlocentregaomesmo, ''''), ''Sim''), ' +
                'geoenttransporteomesmo = ISNULL(NULLIF(geoenttransporteomesmo, ''''), ''Sim''), ' +
                'geoentdatacad = ISNULL(geoentdatacad, CONVERT(VARCHAR(10), GETDATE(), 120)), ' +
                'geoentdesdedata = ISNULL(geoentdesdedata, CONVERT(VARCHAR(10), GETDATE(), 120)), ' +
                'entcod = CASE WHEN ISNULL(entcod, '''') = '''' AND ' + QuotedStr(ventcodApolo) + ' <> '''' THEN ' + QuotedStr(ventcodApolo) + ' ELSE entcod END ' +
                'WHERE geoentcod = ' + QuotedStr(vgeoentcod);
        modulo_dados.fdbanco.ExecSQL(sSql);

        vCatCoord := Trim(lblcategcodestr_coord.Text);
        if vCatCoord = '' then vCatCoord := '02.001.0006';
        sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_categoria WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND geocategcodigo = ' + QuotedStr(vCatCoord) + ') ' +
                'INSERT INTO USER_geoapolo_entidade_categoria (geoentcod, geocategcodigo) VALUES (' + QuotedStr(vgeoentcod) + ', ' + QuotedStr(vCatCoord) + ')';
        try modulo_dados.fdbanco.ExecSQL(sSql); except end;

        sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entcateg WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND geocategcodestr = ' + QuotedStr(vCatCoord) + ') ' +
                'INSERT INTO USER_geoapolo_entcateg (geoentcod, geocategcodestr) VALUES (' + QuotedStr(vgeoentcod) + ', ' + QuotedStr(vCatCoord) + ')';
        try modulo_dados.fdbanco.ExecSQL(sSql); except end;

        sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entcateg WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND geocategcodestr = ''08.009'') ' +
                'INSERT INTO USER_geoapolo_entcateg (geoentcod, geocategcodestr) VALUES (' + QuotedStr(vgeoentcod) + ', ''08.009'')';
        try modulo_dados.fdbanco.ExecSQL(sSql); except end;
      end
      else
      begin
        // INSERT na tabela USER_geoapolo_entidade
        QryGeo.Close;
        QryGeo.SQL.Text := 'SELECT RIGHT(''00000000'' + CAST(ISNULL(MAX(CAST(geoentcod AS INT)), 0) + 1 AS VARCHAR), 8) AS NextCod FROM USER_geoapolo_entidade';
        QryGeo.Open;
        vgeoentcod := QryGeo.FieldByName('NextCod').AsString;
        QryGeo.Close;

        sSql := 'INSERT INTO USER_geoapolo_entidade (' +
                'geoentcod, geotipotratcod, geoentnome, geoentnomefantasia, tipolograd, ' +
                'geoentender, geoenderno, geoentendercomp, geoentbair, geoentdatacad, ' +
                'geoentdesdedata, geoentcep, geocidcod, geoentcxapost, geoentgenero, ' +
                'geotipofj, geofalecido, entcod, cidcodapolo, ' +
                'geoentloccobrancaomesmo, geoentlocentregaomesmo, geoenttransporteomesmo) VALUES (' +
                QuotedStr(vgeoentcod) + ', ''00000001'', ' +
                QuotedStr(QrySavic.FieldByName('Coordenador').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('Coordenador').AsString) + ', 1, ' + // 1 = Rua (numérico!)
                QuotedStr(vendereco) + ', ' +
                QuotedStr(QrySavic.FieldByName('Numero_CasaCoord').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('Compl_coord').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('Bairro').AsString) + ', ' +
                QuotedStr(FormatDateTime('yyyy-mm-dd', Date)) + ', ' +
                QuotedStr(FormatDateTime('yyyy-mm-dd', Date)) + ', ' +
                QuotedStr(buscatroca(Copy(QrySavic.FieldByName('CepCoord').AsString, 1, 10), '-', '')) + ', ' +
                QuotedStr(vcidcod) + ', ' +
                QuotedStr(QrySavic.FieldByName('CaixaPostal_Coord').AsString) + ', ' +
                QuotedStr(vgenero) + ', ''Física'', ''N'', ' +
                QuotedStr(ventcodApolo) + ', ' + QuotedStr(vcidcod) + ', ''Sim'', ''Sim'', ''Sim'')';
        modulo_dados.fdbanco.ExecSQL(sSql);

        // Documento CPF
        if vcpfcoordenador <> '' then
        begin
          sSql := 'INSERT INTO USER_geoapolo_entidade_documentos (geoentcod, geotipodocumento, geonumerodocumento, geoobservacoes) VALUES (' +
                  QuotedStr(vgeoentcod) + ', ''CPF/CNPJ'', ' + QuotedStr(vcpfcoordenador) + ', ''SAVIC'')';
          try
            modulo_dados.fdbanco.ExecSQL(sSql);
          except
          end;
        end;

        // Categoria selecionada para Coordenador
        vCatCoord := Trim(lblcategcodestr_coord.Text);
        if vCatCoord = '' then vCatCoord := '02.001.0006';
        sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_categoria WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND geocategcodigo = ' + QuotedStr(vCatCoord) + ') ' +
                'INSERT INTO USER_geoapolo_entidade_categoria (geoentcod, geocategcodigo) VALUES (' + QuotedStr(vgeoentcod) + ', ' + QuotedStr(vCatCoord) + ')';
        try modulo_dados.fdbanco.ExecSQL(sSql); except end;

        sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entcateg WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND geocategcodestr = ' + QuotedStr(vCatCoord) + ') ' +
                'INSERT INTO USER_geoapolo_entcateg (geoentcod, geocategcodestr) VALUES (' + QuotedStr(vgeoentcod) + ', ' + QuotedStr(vCatCoord) + ')';
        try modulo_dados.fdbanco.ExecSQL(sSql); except end;

        sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entcateg WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND geocategcodestr = ''08.009'') ' +
                'INSERT INTO USER_geoapolo_entcateg (geoentcod, geocategcodestr) VALUES (' + QuotedStr(vgeoentcod) + ', ''08.009'')';
        try modulo_dados.fdbanco.ExecSQL(sSql); except end;
      end;

      // 3. Atualiza ou insere Coordenador em USER_geoapolo_coordenadores_grupodeoracao
      QryGeo.Close;
      QryGeo.SQL.Text := 'SELECT cadastroid_coordenador FROM USER_geoapolo_coordenadores_grupodeoracao WITH (NOLOCK) ' +
                         'WHERE cpfcoordenador = ' + QuotedStr(vcpfcoordenador) + ' OR cadastroid_coordenador = ' + QuotedStr(vcadastrocoord);
      QryGeo.Open;
      if QryGeo.IsEmpty then
      begin
        sSql := 'INSERT INTO USER_geoapolo_coordenadores_grupodeoracao (' +
                'cadastroid_coordenador, coordenador, generocoordenador, cpfcoordenador, rgcoordenador, ' +
                'rgorgaoexpedidor, mandatoindeterminado, datainiciocoordenacao, datafimcoordenacao, endereco_coordenador, ' +
                'numero, complemento, bairrocoordenador, cepcoordenador, go_geocidcod, ' +
                'caixapostalcoordenador, telefonefixo_coordenador, telefonecomercial_coordenador, celular_coordenador, celular2_coordenador, ' +
                'email, dioceseid, diocesecoordenador, idultimoatualizador, ultimaalteracaofeitapor, entcod_apolo, entcod) VALUES (' +
                QuotedStr(vcadastrocoord) + ', ' +
                QuotedStr(QrySavic.FieldByName('Coordenador').AsString) + ', ' +
                QuotedStr(vgenero) + ', ' +
                QuotedStr(vcpfcoordenador) + ', ' +
                QuotedStr(QrySavic.FieldByName('rgcoord').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('rgcoordemissor').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('MandatoIndeterminado').AsString) + ', ';
        if QrySavic.FieldByName('Dataini_coordenacao').IsNull then sSql := sSql + 'NULL, '
        else sSql := sSql + QuotedStr(FormatDateTime('yyyy-mm-dd', QrySavic.FieldByName('Dataini_coordenacao').AsDateTime)) + ', ';
        if QrySavic.FieldByName('datafim_coordenacao').IsNull then sSql := sSql + 'NULL, '
        else sSql := sSql + QuotedStr(FormatDateTime('yyyy-mm-dd', QrySavic.FieldByName('datafim_coordenacao').AsDateTime)) + ', ';
        sSql := sSql +
                QuotedStr(vendereco) + ', ' +
                QuotedStr(QrySavic.FieldByName('Numero_CasaCoord').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('Compl_coord').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('Bairro').AsString) + ', ' +
                QuotedStr(buscatroca(Copy(QrySavic.FieldByName('CepCoord').AsString, 1, 10), '-', '')) + ', ' +
                QuotedStr(vcidcod) + ', ' +
                QuotedStr(QrySavic.FieldByName('CaixaPostal_Coord').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('Telefone_Coord').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('TelCom_Coord').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('CelularCoord1').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('celularcoord2').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('email').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('dioceseId').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('diocesecoordenador').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('useratualizacao').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('ultimaalteracaofeitapor').AsString) + ', ' +
                QuotedStr(ventcodApolo) + ', ' +
                QuotedStr(ventcodApolo) + ')';
        modulo_dados.fdbanco.ExecSQL(sSql);
      end
      else
      begin
        sSql := 'UPDATE USER_geoapolo_coordenadores_grupodeoracao SET ' +
                'coordenador = ' + QuotedStr(QrySavic.FieldByName('Coordenador').AsString) + ', ' +
                'generocoordenador = ' + QuotedStr(vgenero) + ', ' +
                'rgcoordenador = ' + QuotedStr(QrySavic.FieldByName('rgcoord').AsString) + ', ' +
                'rgorgaoexpedidor = ' + QuotedStr(QrySavic.FieldByName('rgcoordemissor').AsString) + ', ' +
                'mandatoindeterminado = ' + QuotedStr(QrySavic.FieldByName('MandatoIndeterminado').AsString) + ', ' +
                'endereco_coordenador = ' + QuotedStr(vendereco) + ', ' +
                'numero = ' + QuotedStr(QrySavic.FieldByName('Numero_CasaCoord').AsString) + ', ' +
                'complemento = ' + QuotedStr(QrySavic.FieldByName('Compl_coord').AsString) + ', ' +
                'bairrocoordenador = ' + QuotedStr(QrySavic.FieldByName('Bairro').AsString) + ', ' +
                'cepcoordenador = ' + QuotedStr(buscatroca(Copy(QrySavic.FieldByName('CepCoord').AsString, 1, 10), '-', '')) + ', ' +
                'go_geocidcod = ' + QuotedStr(vcidcod) + ', ' +
                'telefonefixo_coordenador = ' + QuotedStr(QrySavic.FieldByName('Telefone_Coord').AsString) + ', ' +
                'celular_coordenador = ' + QuotedStr(QrySavic.FieldByName('CelularCoord1').AsString) + ', ' +
                'email = ' + QuotedStr(QrySavic.FieldByName('email').AsString) + ', ' +
                'entcod_apolo = ' + QuotedStr(ventcodApolo) + ', ' +
                'entcod = ' + QuotedStr(ventcodApolo) + ' ' +
                'WHERE cadastroid_coordenador = ' + QuotedStr(vcadastrocoord);
        modulo_dados.fdbanco.ExecSQL(sSql);
      end;
      QryGeo.Close;

      // 4. Atualiza ou insere Grupo de Oração em USER_geoapolo_gruposdeoracao
      QryGeo.Close;
      QryGeo.SQL.Text := 'SELECT gocodigo FROM USER_geoapolo_gruposdeoracao WITH (NOLOCK) WHERE gocodigo = ' +
                         QuotedStr(QrySavic.FieldByName('goid').AsString);
      QryGeo.Open;
      if QryGeo.IsEmpty then
      begin
        sSql := 'INSERT INTO USER_geoapolo_gruposdeoracao (' +
                'gocodigo, gonome_grupodeoracao, go_local_grupo, go_tipo_de_local, go_geocidcod, ' +
                'cadastroid_coordenador, dias_semana, horario, situacao_grupo, caracteristica_grupo, ' +
                'datainclusao_go, datatualizacao_go) VALUES (' +
                QuotedStr(QrySavic.FieldByName('goid').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('GrupodeOracao').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('local').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('TipoLocalReuniao').AsString) + ', ' +
                QuotedStr(vcidcod) + ', ' +
                QuotedStr(vcadastrocoord) + ', ' +
                QuotedStr(QrySavic.FieldByName('dias_semana').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('horario').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('situacao').AsString) + ', ' +
                QuotedStr(QrySavic.FieldByName('CaracteristicaGrupo').AsString) + ', ';
        if QrySavic.FieldByName('datainclusao_go').IsNull then sSql := sSql + 'NULL, '
        else sSql := sSql + QuotedStr(FormatDateTime('yyyy-mm-dd', QrySavic.FieldByName('datainclusao_go').AsDateTime)) + ', ';
        if QrySavic.FieldByName('dataatualizacao_go').IsNull then sSql := sSql + 'NULL)'
        else sSql := sSql + QuotedStr(FormatDateTime('yyyy-mm-dd', QrySavic.FieldByName('dataatualizacao_go').AsDateTime)) + ')';
        modulo_dados.fdbanco.ExecSQL(sSql);
      end
      else
      begin
        sSql := 'UPDATE USER_geoapolo_gruposdeoracao SET ' +
                'gonome_grupodeoracao = ' + QuotedStr(QrySavic.FieldByName('GrupodeOracao').AsString) + ', ' +
                'go_local_grupo = ' + QuotedStr(QrySavic.FieldByName('local').AsString) + ', ' +
                'go_tipo_de_local = ' + QuotedStr(QrySavic.FieldByName('TipoLocalReuniao').AsString) + ', ' +
                'go_geocidcod = ' + QuotedStr(vcidcod) + ', ' +
                'cadastroid_coordenador = ' + QuotedStr(vcadastrocoord) + ', ' +
                'dias_semana = ' + QuotedStr(QrySavic.FieldByName('dias_semana').AsString) + ', ' +
                'horario = ' + QuotedStr(QrySavic.FieldByName('horario').AsString) + ', ' +
                'situacao_grupo = ' + QuotedStr(QrySavic.FieldByName('situacao').AsString) + ', ' +
                'caracteristica_grupo = ' + QuotedStr(QrySavic.FieldByName('CaracteristicaGrupo').AsString) + ', ' +
                'datatualizacao_go = ' + QuotedStr(FormatDateTime('yyyy-mm-dd', Date)) + ' ' +
                'WHERE gocodigo = ' + QuotedStr(QrySavic.FieldByName('goid').AsString);
        modulo_dados.fdbanco.ExecSQL(sSql);
      end;
      QryGeo.Close;

      // 5. Integração do Grupo de Oração no cadastro de entidades (USER_geoapolo_entidade)
      vgoid := Trim(QrySavic.FieldByName('goid').AsString);
      vNomeGO := Trim(QrySavic.FieldByName('GrupodeOracao').AsString);
      vLocalReuniao := Trim(QrySavic.FieldByName('local').AsString);
      if vLocalReuniao = '' then
        vLocalReuniao := vNomeGO;
      vTipoLocal := Trim(QrySavic.FieldByName('TipoLocalReuniao').AsString);
      vSituacao := Trim(QrySavic.FieldByName('situacao').AsString);
      vDiaSemana := Trim(QrySavic.FieldByName('dias_semana').AsString);
      vCaractGrupo := Trim(QrySavic.FieldByName('CaracteristicaGrupo').AsString);

      if not QrySavic.FieldByName('datainclusao_go').IsNull then
        vDataCadGO := FormatDateTime('yyyy-mm-dd', QrySavic.FieldByName('datainclusao_go').AsDateTime)
      else
        vDataCadGO := '';

      if not QrySavic.FieldByName('dataatualizacao_go').IsNull then
        vDataAtuGO := FormatDateTime('dd/mm/yyyy', QrySavic.FieldByName('dataatualizacao_go').AsDateTime)
      else
        vDataAtuGO := FormatDateTime('dd/mm/yyyy', Date);

      // Código da entidade no GeoAlvo (7 caracteres - limite VARCHAR(7) de USER_geoapolo_entidade)
      if (Length(vgoid) <= 7) and (StrToInt64Def(vgoid, -1) >= 0) then
        vgeoentcodgo := RightStr('0000000' + vgoid, 7)
      else
        vgeoentcodgo := Copy(vgoid, 1, 7);

      // Validação de cidade (Item 2.2)
      vCidCodValidado := '';
      vCidadeNome := UpperCase(Trim(QrySavic.FieldByName('cidade').AsString));
      vEstadoUF := UpperCase(Trim(QrySavic.FieldByName('estado').AsString));

      // Tenta pelo vcidcod já apurado
      if (vcidcod <> '') and (vcidcod <> '0') and (Pos('-', vcidcod) = 0) then
      begin
        QryGeo.Close;
        QryGeo.SQL.Text := 'SELECT TOP 1 geocidcod FROM USER_geoapolo_cidades WITH (NOLOCK) WHERE geocidcod = ' + QuotedStr(vcidcod);
        try
          QryGeo.Open;
          if not QryGeo.IsEmpty then
            vCidCodValidado := QryGeo.FieldByName('geocidcod').AsString;
          QryGeo.Close;
        except
        end;
      end;

      // Se não encontrou, busca por nome e UF em USER_geoapolo_cidades (com collation CI_AI insensível a acento)
      if (vCidCodValidado = '') and (vCidadeNome <> '') then
      begin
        QryGeo.Close;
        QryGeo.SQL.Text := 'SELECT TOP 1 geocidcod FROM USER_geoapolo_cidades WITH (NOLOCK) ' +
                           'WHERE cidnomecomp COLLATE Latin1_General_CI_AI = ' + QuotedStr(vCidadeNome) + ' AND UPPER(ufsigla) = ' + QuotedStr(vEstadoUF);
        try
          QryGeo.Open;
          if not QryGeo.IsEmpty then
            vCidCodValidado := QryGeo.FieldByName('geocidcod').AsString;
          QryGeo.Close;
        except
        end;
      end;

      // Se ainda não encontrou, busca na tabela cidade do Alvo
      if (vCidCodValidado = '') and (vCidadeNome <> '') then
      begin
        QryGeo.Close;
        QryGeo.SQL.Text := 'SELECT TOP 1 cidcod FROM cidade WITH (NOLOCK) ' +
                           'WHERE cidnomecomp COLLATE Latin1_General_CI_AI LIKE ' + QuotedStr(vCidadeNome + '%') + ' AND UPPER(ufsigla) = ' + QuotedStr(vEstadoUF);
        try
          QryGeo.Open;
          if not QryGeo.IsEmpty then
          begin
            vCidCodValidado := QryGeo.FieldByName('cidcod').AsString;
            try
              modulo_dados.fdbanco.ExecSQL(
                'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_cidades WHERE geocidcod = ' + QuotedStr(vCidCodValidado) + ') ' +
                'INSERT INTO USER_geoapolo_cidades (geocidcod, cidnomecomp, ufsigla) VALUES (' +
                QuotedStr(vCidCodValidado) + ', ' + QuotedStr(vCidadeNome) + ', ' + QuotedStr(vEstadoUF) + ')'
              );
            except
            end;
          end;
          QryGeo.Close;
        except
        end;
      end;

      if vCidCodValidado = '' then
      begin
        // Inconsistência de cidade: grava no arquivo e não salva em entidades
        sLinhaLog := 'GOID: ' + vgoid + ' | GO: ' + vNomeGO +
                     ' | Cidade: ' + vCidadeNome + ' - ' + vEstadoUF + ' | Motivo: Cidade não encontrada em USER_geoapolo_cidades ou cidade';
        slApenasGrupos.Add(sLinhaLog);

        sArquivoInconsistencias := ExtractFilePath(Application.ExeName) + 'inconsistencias_integ_entidades.txt';
        try
          AssignFile(FLog, sArquivoInconsistencias);
          if FileExists(sArquivoInconsistencias) then
            Append(FLog)
          else
            Rewrite(FLog);
          WriteLn(FLog, FormatDateTime('yyyy-mm-dd hh:nn:ss', Now) + ' | ' + sLinhaLog);
          CloseFile(FLog);
        except
        end;

        sSql := 'UPDATE USER_geoapolo_gruposdeoracao SET flagexportado = ''Não'' WHERE gocodigo = ' + QuotedStr(vgoid);
        try modulo_dados.fdbanco.ExecSQL(sSql); except end;
      end
      else
      begin
        // Cidade validada com sucesso: prossegue integração

        // Código Alvo se já existente no grupo ou na entidade
        ventcodGO := '';
        QryGeo.Close;
        QryGeo.SQL.Text := 'SELECT codigoapolo FROM USER_geoapolo_gruposdeoracao WITH (NOLOCK) WHERE gocodigo = ' + QuotedStr(vgoid);
        try
          QryGeo.Open;
          if not QryGeo.IsEmpty then
            ventcodGO := Trim(QryGeo.FieldByName('codigoapolo').AsString);
          QryGeo.Close;
        except
        end;
        if ventcodGO = '0' then ventcodGO := '';

        vEntidadeGOExiste := False;
        vObsAtual := '';
        QryGeo.Close;
        QryGeo.SQL.Text := 'SELECT geoentcod, entcod, geoobservacoes FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcodgo);
        try
          QryGeo.Open;
          if not QryGeo.IsEmpty then
          begin
            vEntidadeGOExiste := True;
            vObsAtual := QryGeo.FieldByName('geoobservacoes').AsString;
            if (ventcodGO = '') and (Trim(QryGeo.FieldByName('entcod').AsString) <> '') and (Trim(QryGeo.FieldByName('entcod').AsString) <> '0') then
              ventcodGO := Trim(QryGeo.FieldByName('entcod').AsString);
          end;
          QryGeo.Close;
        except
        end;

        // Monta bloco [INFORMAÇÕES] preservando [PENDÊNCIAS] existentes
        vObsInfo := '[INFORMAÇÕES]' + sLineBreak +
                    'Dia da Semana: ' + vDiaSemana;
        if Trim(QrySavic.FieldByName('horario').AsString) <> '' then
          vObsInfo := vObsInfo + ' às ' + Trim(QrySavic.FieldByName('horario').AsString);
        vObsInfo := vObsInfo + sLineBreak +
                    'Caracteristicas do Grupo: ' + vCaractGrupo + sLineBreak +
                    'Última Atualização do G.O.: ' + vDataAtuGO;

        nPosInfo := Pos('[INFORMAÇÕES]', vObsAtual);
        if nPosInfo = 0 then
          nPosInfo := Pos('[INFORMACOES]', vObsAtual);

        if nPosInfo > 0 then
          vPendencias := Trim(Copy(vObsAtual, 1, nPosInfo - 1))
        else
          vPendencias := Trim(vObsAtual);

        if vPendencias <> '' then
          vObsFinal := vPendencias + sLineBreak + sLineBreak + vObsInfo
        else
          vObsFinal := vObsInfo;

        if ventcodGO <> '' then
          ventcodGOSQL := QuotedStr(ventcodGO)
        else
          ventcodGOSQL := 'NULL';

        if vEntidadeGOExiste then
        begin
          sSql := 'UPDATE USER_geoapolo_entidade SET ' +
                  'geoentnome = ' + QuotedStr(Copy(vNomeGO, 1, 60)) + ', ' +
                  'geoentnomefantasia = ' + QuotedStr(Copy(vLocalReuniao, 1, 60)) + ', ' +
                  'tipolograd = ISNULL(NULLIF(tipolograd, 0), 1), ' +
                  'geotipotratcod = ISNULL(NULLIF(geotipotratcod, ''''), ''0001''), ' +
                  'geoentender = CASE WHEN ISNULL(NULLIF(' + QuotedStr(Copy(vLocalReuniao, 1, 60)) + ', ''''), '''') <> '''' THEN ' + QuotedStr(Copy(vLocalReuniao, 1, 60)) + ' ELSE ISNULL(geoentender, ''S/N'') END, ' +
                  'geoenderno = ISNULL(NULLIF(geoenderno, ''''), ''S/N''), ' +
                  'geolocalreferencia_ender = ' + QuotedStr(Copy(vTipoLocal, 1, 40)) + ', ' +
                  'geoentendercomp = ' + QuotedStr(Copy(vSituacao, 1, 70)) + ', ' +
                  'geoobservacoes = ' + QuotedStr(Copy(vObsFinal, 1, 200)) + ', ' +
                  'geocidcod = ' + QuotedStr(vCidCodValidado) + ', ' +
                  'cidcodapolo = ' + QuotedStr(vCidCodValidado) + ', ' +
                  'geotipofj = ISNULL(NULLIF(geotipofj, ''''), ''Jurídica''), ' +
                  'geofalecido = ISNULL(NULLIF(geofalecido, ''''), ''N''), ' +
                  'geoentloccobrancaomesmo = ISNULL(NULLIF(geoentloccobrancaomesmo, ''''), ''Sim''), ' +
                  'geoentlocentregaomesmo = ISNULL(NULLIF(geoentlocentregaomesmo, ''''), ''Sim''), ' +
                  'geoenttransporteomesmo = ISNULL(NULLIF(geoenttransporteomesmo, ''''), ''Sim'')';
          if vDataCadGO <> '' then
            sSql := sSql + ', geoentdatacad = ISNULL(geoentdatacad, ' + QuotedStr(vDataCadGO) + '), ' +
                           'geoentdesdedata = ISNULL(geoentdesdedata, ' + QuotedStr(vDataCadGO) + ') '
          else
            sSql := sSql + ', geoentdatacad = ISNULL(geoentdatacad, CONVERT(VARCHAR(10), GETDATE(), 120)), ' +
                           'geoentdesdedata = ISNULL(geoentdesdedata, CONVERT(VARCHAR(10), GETDATE(), 120)) ';

          if ventcodGO <> '' then
            sSql := sSql + ', entcod = ' + QuotedStr(ventcodGO) + ' ';

          sSql := sSql + 'WHERE geoentcod = ' + QuotedStr(vgeoentcodgo);
          modulo_dados.fdbanco.ExecSQL(sSql);
        end
        else
        begin
          sSql := 'INSERT INTO USER_geoapolo_entidade (' +
                  'geoentcod, geotipotratcod, geoentnome, geoentnomefantasia, tipolograd, ' +
                  'geoentender, geoenderno, geolocalreferencia_ender, geoentendercomp, geoobservacoes, ' +
                  'geoentdatacad, geoentdesdedata, geocidcod, cidcodapolo, geoentgenero, ' +
                  'geotipofj, geofalecido, entcod, ' +
                  'geoentloccobrancaomesmo, geoentlocentregaomesmo, geoenttransporteomesmo) VALUES (' +
                  QuotedStr(vgeoentcodgo) + ', ''0001'', ' +
                  QuotedStr(Copy(vNomeGO, 1, 60)) + ', ' +
                  QuotedStr(Copy(vLocalReuniao, 1, 60)) + ', 1, ' +
                  QuotedStr(Copy(vLocalReuniao, 1, 60)) + ', ''S/N'', ' +
                  QuotedStr(Copy(vTipoLocal, 1, 40)) + ', ' +
                  QuotedStr(Copy(vSituacao, 1, 70)) + ', ' +
                  QuotedStr(Copy(vObsFinal, 1, 200)) + ', ';
          if vDataCadGO <> '' then
            sSql := sSql + QuotedStr(vDataCadGO) + ', ' + QuotedStr(vDataCadGO) + ', '
          else
            sSql := sSql + 'CONVERT(VARCHAR(10), GETDATE(), 120), CONVERT(VARCHAR(10), GETDATE(), 120), ';
          sSql := sSql + QuotedStr(vCidCodValidado) + ', ' + QuotedStr(vCidCodValidado) + ', ''M'', ''Jurídica'', ''N'', ' +
                  ventcodGOSQL + ', ''Sim'', ''Sim'', ''Sim'')';
          modulo_dados.fdbanco.ExecSQL(sSql);
        end;

        // Vínculo da Categoria para o Grupo de Oração
        vCatGO := Trim(lblcategcodestr_go.Text);
        if vCatGO = '' then vCatGO := '02.001';

        sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_categoria WHERE geoentcod = ' + QuotedStr(vgeoentcodgo) + ' AND geocategcodigo = ' + QuotedStr(vCatGO) + ') ' +
                'INSERT INTO USER_geoapolo_entidade_categoria (geoentcod, geocategcodigo) VALUES (' + QuotedStr(vgeoentcodgo) + ', ' + QuotedStr(vCatGO) + ')';
        try modulo_dados.fdbanco.ExecSQL(sSql); except end;

        sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entcateg WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcodgo) + ' AND geocategcodestr = ' + QuotedStr(vCatGO) + ') ' +
                'INSERT INTO USER_geoapolo_entcateg (geoentcod, geocategcodestr) VALUES (' + QuotedStr(vgeoentcodgo) + ', ' + QuotedStr(vCatGO) + ')';
        try modulo_dados.fdbanco.ExecSQL(sSql); except end;

        sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entcateg WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcodgo) + ' AND geocategcodestr = ''08.009'') ' +
                'INSERT INTO USER_geoapolo_entcateg (geoentcod, geocategcodestr) VALUES (' + QuotedStr(vgeoentcodgo) + ', ''08.009'')';
        try modulo_dados.fdbanco.ExecSQL(sSql); except end;

        sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_ativecon WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcodgo) + ') ' +
                'INSERT INTO USER_geoapolo_entidade_ativecon (ativeconcodestr, geoentcod) VALUES (''94.91-0'', ' + QuotedStr(vgeoentcodgo) + ')';
        try modulo_dados.fdbanco.ExecSQL(sSql); except end;

        // Vínculo Coordenador <-> Grupo de Oração em USER_geoapolo_entidade_contato (Item 2.3)
        vgeoentcod_coord_contato := '';
        vTipoTratCoord := '0001';
        ventcodCoord := '';

        vcpfCoordPesq := '';
        if vcadastrocoord <> '' then
        begin
          QryGeo.Close;
          QryGeo.SQL.Text := 'SELECT TOP 1 cpfcoordenador FROM USER_geoapolo_coordenadores_grupodeoracao WITH (NOLOCK) ' +
                             'WHERE cadastroid_coordenador = ' + QuotedStr(vcadastrocoord);
          try
            QryGeo.Open;
            if not QryGeo.IsEmpty then
              vcpfCoordPesq := Trim(QryGeo.FieldByName('cpfcoordenador').AsString);
            QryGeo.Close;
          except
          end;
        end;

        if vcpfCoordPesq = '' then
          vcpfCoordPesq := vcpfcoordenador;

        vcpfCoordLimpo := buscatroca(buscatroca(buscatroca(vcpfCoordPesq, '.', ''), '-', ''), '/', '');

        if vcpfCoordLimpo <> '' then
        begin
          QryGeo.Close;
          QryGeo.SQL.Text := 'SELECT TOP 1 geoentcod FROM USER_geoapolo_entidade_documentos WITH (NOLOCK) ' +
                             'WHERE (geotipodocumento = ''CPF/CNPJ'' OR geotipodocumento = ''CPFCNPJ'') AND ' +
                             'REPLACE(REPLACE(REPLACE(geonumerodocumento, ''.'', ''''), ''-'', ''''), ''/'', '''') = ' + QuotedStr(vcpfCoordLimpo);
          try
            QryGeo.Open;
            if not QryGeo.IsEmpty then
              vgeoentcod_coord_contato := QryGeo.FieldByName('geoentcod').AsString;
            QryGeo.Close;
          except
          end;
        end;

        if (vgeoentcod_coord_contato = '') and (vgeoentcod <> '') then
          vgeoentcod_coord_contato := vgeoentcod;

        if vgeoentcod_coord_contato <> '' then
        begin
          QryGeo.Close;
          QryGeo.SQL.Text := 'SELECT geotipotratcod, entcod FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcod_coord_contato);
          try
            QryGeo.Open;
            if not QryGeo.IsEmpty then
            begin
              vTipoTratCoord := Trim(QryGeo.FieldByName('geotipotratcod').AsString);
              if (vTipoTratCoord = '') or (vTipoTratCoord = '0') then
                vTipoTratCoord := '0001';
              vTipoTratCoord := Copy(vTipoTratCoord, 1, 6);
              ventcodCoord := Trim(QryGeo.FieldByName('entcod').AsString);
            end;
            QryGeo.Close;
          except
          end;

          if QrySavic.FieldByName('Dataini_coordenacao').IsNull then
            vDtIniCoordSQL := 'NULL'
          else
            vDtIniCoordSQL := QuotedStr(FormatDateTime('yyyy-mm-dd', QrySavic.FieldByName('Dataini_coordenacao').AsDateTime));

          if QrySavic.FieldByName('datafim_coordenacao').IsNull then
            vDtFimCoordSQL := 'NULL'
          else
            vDtFimCoordSQL := QuotedStr(FormatDateTime('yyyy-mm-dd', QrySavic.FieldByName('datafim_coordenacao').AsDateTime));

          sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_contato WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcodgo) + ' AND EntCodContato = ' + QuotedStr(vgeoentcod_coord_contato) + ') ' +
                  'INSERT INTO USER_geoapolo_entidade_contato (' +
                  'geoentcod, entCod, EntCodContato, TipoTratCod, CargoCodEstr, EntContatoCategPrinc, ' +
                  'EntContatoEMail, EntContatoTelefone, EntContatoCelular, CidCod, data_vigencia_inicial, data_vigencia_final) VALUES (' +
                  QuotedStr(vgeoentcodgo) + ', ' +
                  ventcodGOSQL + ', ' +
                  QuotedStr(vgeoentcod_coord_contato) + ', ' +
                  QuotedStr(vTipoTratCoord) + ', ''Coordenador'', ''S'', ' +
                  QuotedStr(Copy(QrySavic.FieldByName('email').AsString, 1, 60)) + ', ' +
                  QuotedStr(Copy(QrySavic.FieldByName('Telefone_Coord').AsString, 1, 20)) + ', ' +
                  QuotedStr(Copy(QrySavic.FieldByName('CelularCoord1').AsString, 1, 20)) + ', ' +
                  QuotedStr(vCidCodValidado) + ', ' +
                  vDtIniCoordSQL + ', ' +
                  vDtFimCoordSQL + ') ' +
                  'ELSE UPDATE USER_geoapolo_entidade_contato SET ' +
                  'entCod = ' + ventcodGOSQL + ', ' +
                  'TipoTratCod = ' + QuotedStr(vTipoTratCoord) + ', CargoCodEstr = ''Coordenador'', EntContatoCategPrinc = ''S'', ' +
                  'EntContatoEMail = ' + QuotedStr(Copy(QrySavic.FieldByName('email').AsString, 1, 60)) + ', ' +
                  'EntContatoTelefone = ' + QuotedStr(Copy(QrySavic.FieldByName('Telefone_Coord').AsString, 1, 20)) + ', ' +
                  'EntContatoCelular = ' + QuotedStr(Copy(QrySavic.FieldByName('CelularCoord1').AsString, 1, 20)) + ', ' +
                  'CidCod = ' + QuotedStr(vCidCodValidado) + ', ' +
                  'data_vigencia_inicial = ' + vDtIniCoordSQL + ', ' +
                  'data_vigencia_final = ' + vDtFimCoordSQL + ' ' +
                  'WHERE geoentcod = ' + QuotedStr(vgeoentcodgo) + ' AND EntCodContato = ' + QuotedStr(vgeoentcod_coord_contato);
          try
            modulo_dados.fdbanco.ExecSQL(sSql);
          except
          end;
        end;

        // Marca Grupo de Oração como exportado com sucesso
        sSql := 'UPDATE USER_geoapolo_gruposdeoracao SET ' +
                'flagexportado = ''Sim'', ' +
                'codigoapolo = ' + QuotedStr(vgeoentcodgo) + ' ' +
                'WHERE gocodigo = ' + QuotedStr(vgoid);
        try modulo_dados.fdbanco.ExecSQL(sSql); except end;

        slInseridos.Add('GOID: ' + vgoid + ' | Cód. Entidade: ' + vgeoentcodgo + ' | GO: ' + vNomeGO + ' | Cidade: ' + vCidadeNome + ' - ' + vEstadoUF);
      end;

      Gauge1.Progress := nAtual;
      Gauge1.Refresh;
      lblnregistrosapurados.Caption := IntToStr(nTotal - nAtual);
      lblnregistrosapurados.Refresh;

      QrySavic.Next;
    end;

    // Salva arquivo texto de ocorrências no diretório do executável
    sArquivoOcorrencias := ExtractFilePath(Application.ExeName) + 'ocorrencias_importacao_savic_alvo.txt';
    try
      AssignFile(FOcorrencias, sArquivoOcorrencias);
      Rewrite(FOcorrencias);
      WriteLn(FOcorrencias, '================================================================================');
      WriteLn(FOcorrencias, 'RELATÓRIO DE OCORRÊNCIAS DA INTEGRAÇÃO SAVIC x ALVO (GRUPOS DE ORAÇÃO)');
      WriteLn(FOcorrencias, 'Gerado em: ' + FormatDateTime('yyyy-mm-dd hh:nn:ss', Now));
      WriteLn(FOcorrencias, 'Período: ' + sIni + ' até ' + sFim);
      WriteLn(FOcorrencias, 'Total de registros apurados: ' + IntToStr(nTotal));
      WriteLn(FOcorrencias, 'Total inseridos/atualizados em USER_geoapolo_entidade: ' + IntToStr(slInseridos.Count));
      WriteLn(FOcorrencias, 'Total apenas em USER_geoapolo_gruposdeoracao (com inconsistências): ' + IntToStr(slApenasGrupos.Count));
      WriteLn(FOcorrencias, '================================================================================');
      WriteLn(FOcorrencias, '');
      WriteLn(FOcorrencias, '--------------------------------------------------------------------------------');
      WriteLn(FOcorrencias, '1. REGISTROS INSERIDOS / ATUALIZADOS EM USER_geoapolo_entidade (' + IntToStr(slInseridos.Count) + ')');
      WriteLn(FOcorrencias, '--------------------------------------------------------------------------------');
      for iLog := 0 to slInseridos.Count - 1 do
        WriteLn(FOcorrencias, slInseridos[iLog]);
      WriteLn(FOcorrencias, '');
      WriteLn(FOcorrencias, '--------------------------------------------------------------------------------');
      WriteLn(FOcorrencias, '2. REGISTROS APENAS EM USER_geoapolo_gruposdeoracao (' + IntToStr(slApenasGrupos.Count) + ')');
      WriteLn(FOcorrencias, '--------------------------------------------------------------------------------');
      for iLog := 0 to slApenasGrupos.Count - 1 do
        WriteLn(FOcorrencias, slApenasGrupos[iLog]);
      WriteLn(FOcorrencias, '================================================================================');
      CloseFile(FOcorrencias);
    except
    end;

    ShowMessage('ATUALIZAÇÃO/IMPORTAÇÃO DE GRUPOS DE ORAÇÃO DO SAVIC CONCLUÍDA!' + sLineBreak +
                'Inseridos/Atualizados em Entidades: ' + IntToStr(slInseridos.Count) + sLineBreak +
                'Apenas em Grupos de Oração (com inconsistências): ' + IntToStr(slApenasGrupos.Count) + sLineBreak +
                'Arquivo de ocorrências gravado em:' + sLineBreak + sArquivoOcorrencias);
    lista_go_jaimportados;
  finally
    slInseridos.Free;
    slApenasGrupos.Free;
    QrySavic.Free;
    QryGeo.Free;
  end;
end;

function retorna_cidade_estado(cidade: string; estado: string; formulario: TForm): string;
var
  Qry: TFDQuery;
  cidNormal: string;
begin
  Result := '0';
  cidNormal := UpperCase(Trim(cidade));
  if cidNormal = '' then Exit;

  if cidNormal = 'ALVORADA D OESTE' then cidNormal := 'ALVORADA DO OESTE'
  else if cidNormal = 'PASSA-VINTE' then cidNormal := 'PASSA VINTE'
  else if ((cidNormal = 'ESTRUTURAL') or (tiracento(cidNormal) = 'NUCLEO BANDEIRANTES') or
           (cidNormal = 'VICENTE PIRES') or (cidNormal = 'AGUAS CLARAS') or
           (cidNormal = 'RIACHO FUNDO I') or (cidNormal = 'RIACHO FUNDO II') or
           (cidNormal = 'COLONIA AGRICOLA SAMAMBAIA') or (cidNormal = 'ITAPUA')) and (estado = 'DF') then
    cidNormal := 'BRASILIA'
  else if cidNormal = 'SANTA RITA DE IBITIPOCA' then cidNormal := 'SANTA RITA DO IBITIPOCA'
  else if cidNormal = 'ALTA FLORESTA DOESTE' then cidNormal := 'ALTA FLORESTA DO OESTE'
  else if (cidNormal = 'MIRASSOL DOESTE') and (estado = 'MT') then cidNormal := 'MIRASSOL DO OESTE'
  else if (cidNormal = 'DONA EUSEBIA') and (estado = 'MG') then cidNormal := 'DONA EUZEBIA'
  else if (cidNormal = 'CONQUISTA D OESTE') and (estado = 'MT') then cidNormal := 'CONQUISTA DO OESTE'
  else if (cidNormal = 'PEROLA D OESTE') and (estado = 'PR') then cidNormal := 'PEROLA DO OESTE'
  else if (cidNormal = 'LAGOA DE ITAENGA') and (estado = 'PE') then cidNormal := 'LAGOA DO ITAENGA'
  else if (cidNormal = 'JANUARIO CICCO') and (estado = 'RN') then cidNormal := 'BOA SAUDE'
  else if (cidNormal = 'AUGUSTO SEVERO') and (estado = 'RN') then cidNormal := 'CAMPO GRANDE';

  Qry := TFDQuery.Create(nil);
  try
    Qry.Connection := modulo_dados.fdbanco;
    Qry.SQL.Text := 'SELECT geocidcod FROM USER_geoapolo_cidades WHERE cidnomecomp COLLATE Latin1_General_CI_AI = ' +
                    QuotedStr(cidNormal) + ' AND ufsigla = ' + QuotedStr(estado);
    try
      Qry.Open;
      if not Qry.IsEmpty then
      begin
        Result := Qry.FieldByName('geocidcod').AsString;
        Exit;
      end;
      Qry.Close;
    except
    end;

    Qry.SQL.Text := 'SELECT cidcod FROM cidade WHERE cidnomecomp COLLATE Latin1_General_CI_AI LIKE ' +
                    QuotedStr(cidNormal + '%') + ' AND ufsigla = ' + QuotedStr(estado);
    try
      Qry.Open;
      if not Qry.IsEmpty then
      begin
        Result := Qry.FieldByName('cidcod').AsString;
        try
          modulo_dados.fdbanco.ExecSQL(
            'INSERT INTO USER_geoapolo_cidades (geocidcod, cidnomecomp, ufsigla) VALUES (' +
            QuotedStr(Result) + ', ' + QuotedStr(cidNormal) + ', ' + QuotedStr(estado) + ')'
          );
        except
        end;
        Exit;
      end;
      Qry.Close;
    except
    end;

    Result := cidNormal + ' - ' + estado;
  finally
    Qry.Free;
  end;
end;

procedure Tfrmimporta_atualizaGOSavicGeoApolo.CarregaNomeCategoria(const ACodigo: string; ALabel: TLabel);
var
  Q: TFDQuery;
begin
  if not Assigned(ALabel) then Exit;
  ALabel.Caption := '';
  if Trim(ACodigo) = '' then Exit;
  if not modulo_dados.fdbanco.Connected then
  begin
    conecta_banco('FDALVO');
    if not modulo_dados.fdbanco.Connected then Exit;
  end;
  Q := TFDQuery.Create(nil);
  try
    Q.Connection := modulo_dados.fdbanco;
    Q.SQL.Text := 'SELECT geocategnome FROM USER_geoapolo_categoria WITH (NOLOCK) WHERE geocategcodestr = ' + QuotedStr(Trim(ACodigo));
    try
      Q.Open;
      if not Q.IsEmpty then
        ALabel.Caption := Q.FieldByName('geocategnome').AsString
      else
        ALabel.Caption := '(Categoria não localizada)';
    except
      ALabel.Caption := '';
    end;
  finally
    Q.Free;
  end;
end;

procedure Tfrmimporta_atualizaGOSavicGeoApolo.spbbuscacat_goClick(Sender: TObject);
var
  frm: Tfrmconsulta3;
  i: Integer;
begin
  with modulo_dados do
  begin
    fdquerysql5.Close;
    fdquerysql5.Connection := fdbanco;
    fdquerysql5.SQL.Text := 'SELECT geocategcodestr, geocategnome FROM USER_geoapolo_categoria WITH (NOLOCK) ORDER BY geocategcodestr ASC';
    try
      fdquerysql5.Open;
    except
      on E: Exception do
      begin
        ShowMessage('Erro ao consultar categorias: ' + E.Message);
        Exit;
      end;
    end;

    if fdquerysql5.IsEmpty then
    begin
      ShowMessage('Tabela de categorias está vazia!');
      Exit;
    end;

    Application.CreateForm(Tfrmconsulta3, frm);
    try
      frm.controle := 'CATEGORIA_IMPORTA_GRUPOORACAO';
      frm.cbocampo.Items.Clear;
      frm.cbordem.Items.Clear;
      for i := 0 to fdquerysql5.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(fdquerysql5.Fields[i].DisplayName);
        frm.cbordem.Items.Add(fdquerysql5.Fields[i].DisplayName);
      end;
      if frm.cbocampo.Items.Count > 0 then frm.cbocampo.ItemIndex := 0;
      if frm.cbordem.Items.Count > 0 then frm.cbordem.ItemIndex := 0;
      dtsfdquerysql5.DataSet := fdquerysql5;
      frm.gridconsulta.DataSource := dtsfdquerysql5;
      frm.gridconsulta.Refresh;
      frm.ShowModal;

      if (frm.ModalResult = mrOk) and (not fdquerysql5.IsEmpty) then
      begin
        lblcategcodestr_go.Text := fdquerysql5.FieldByName('geocategcodestr').AsString;
        lblcategnome_go.Caption := fdquerysql5.FieldByName('geocategnome').AsString;
        lblcategcodestr_go.Refresh;
        lblcategnome_go.Refresh;
      end;
    finally
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql5.DataSet := nil;
      fdquerysql5.Close;
      frm.Free;
    end;
  end;
end;

procedure Tfrmimporta_atualizaGOSavicGeoApolo.spbbuscacat_coordClick(Sender: TObject);
var
  frm: Tfrmconsulta3;
  i: Integer;
begin
  with modulo_dados do
  begin
    fdquerysql5.Close;
    fdquerysql5.Connection := fdbanco;
    fdquerysql5.SQL.Text := 'SELECT geocategcodestr, geocategnome FROM USER_geoapolo_categoria WITH (NOLOCK) ORDER BY geocategcodestr ASC';
    try
      fdquerysql5.Open;
    except
      on E: Exception do
      begin
        ShowMessage('Erro ao consultar categorias: ' + E.Message);
        Exit;
      end;
    end;

    if fdquerysql5.IsEmpty then
    begin
      ShowMessage('Tabela de categorias está vazia!');
      Exit;
    end;

    Application.CreateForm(Tfrmconsulta3, frm);
    try
      frm.controle := 'CATEGORIA_COORDENADOR_GRUPO';
      frm.cbocampo.Items.Clear;
      frm.cbordem.Items.Clear;
      for i := 0 to fdquerysql5.Fields.Count - 1 do
      begin
        frm.cbocampo.Items.Add(fdquerysql5.Fields[i].DisplayName);
        frm.cbordem.Items.Add(fdquerysql5.Fields[i].DisplayName);
      end;
      if frm.cbocampo.Items.Count > 0 then frm.cbocampo.ItemIndex := 0;
      if frm.cbordem.Items.Count > 0 then frm.cbordem.ItemIndex := 0;
      dtsfdquerysql5.DataSet := fdquerysql5;
      frm.gridconsulta.DataSource := dtsfdquerysql5;
      frm.gridconsulta.Refresh;
      frm.ShowModal;

      if (frm.ModalResult = mrOk) and (not fdquerysql5.IsEmpty) then
      begin
        lblcategcodestr_coord.Text := fdquerysql5.FieldByName('geocategcodestr').AsString;
        lblcategnome_coord.Caption := fdquerysql5.FieldByName('geocategnome').AsString;
        lblcategcodestr_coord.Refresh;
        lblcategnome_coord.Refresh;
      end;
    finally
      frm.gridconsulta.DataSource := nil;
      dtsfdquerysql5.DataSet := nil;
      fdquerysql5.Close;
      frm.Free;
    end;
  end;
end;

procedure Tfrmimporta_atualizaGOSavicGeoApolo.lblcategcodestr_goExit(Sender: TObject);
begin
  CarregaNomeCategoria(lblcategcodestr_go.Text, lblcategnome_go);
end;

procedure Tfrmimporta_atualizaGOSavicGeoApolo.lblcategcodestr_coordExit(Sender: TObject);
begin
  CarregaNomeCategoria(lblcategcodestr_coord.Text, lblcategnome_coord);
end;

procedure Tfrmimporta_atualizaGOSavicGeoApolo.FormActivate(Sender: TObject);
begin
  StatusBar1.Panels[1].Text := nomecomputador;
  StatusBar1.Panels[3].Text := configura_statusbar('a');
  StatusBar1.Panels[5].Text := configura_statusbar('a');
  StatusBar1.Refresh;
  mskdtinicial.SetFocus;
  lista_go_jaimportados;

  if Trim(lblcategcodestr_go.Text) = '' then
    lblcategcodestr_go.Text := '02.001';
  CarregaNomeCategoria(lblcategcodestr_go.Text, lblcategnome_go);

  if Trim(lblcategcodestr_coord.Text) = '' then
    lblcategcodestr_coord.Text := '02.001.0006';
  CarregaNomeCategoria(lblcategcodestr_coord.Text, lblcategnome_coord);
end;

procedure Tfrmimporta_atualizaGOSavicGeoApolo.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Action := caFree;
end;

procedure Tfrmimporta_atualizaGOSavicGeoApolo.FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F10 then
    spbretornar.Click;
end;

procedure Tfrmimporta_atualizaGOSavicGeoApolo.mskdtfinalKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) then
    CalcularApuracao;
end;

procedure Tfrmimporta_atualizaGOSavicGeoApolo.mskdtinicialKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_TAB) or (Key = VK_RETURN) then
    mskdtfinal.SetFocus;
end;

procedure Tfrmimporta_atualizaGOSavicGeoApolo.spbretornarClick(Sender: TObject);
begin
  Close;
end;

end.
