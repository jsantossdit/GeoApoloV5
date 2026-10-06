unit unt_moderagrupodeoracao;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.ComCtrls, Vcl.StdCtrls, Vcl.Buttons,
  Vcl.ExtCtrls, Data.DB, Vcl.Grids, Vcl.DBGrids, Vcl.Menus, Vcl.Imaging.jpeg,
  System.UITypes, FireDAC.Comp.Client, FireDAC.Stan.Param, FireDAC.DatS, FireDAC.DApt;

type
  Tfrmmoderacaogrupodeoracao = class(TForm)
    Panel1: TPanel;
    spblimpar: TSpeedButton;
    spbretornar: TSpeedButton;
    lblmsg1: TLabel;
    StatusBar1: TStatusBar;
    popmenumoderago: TPopupMenu;
    popmnugravaconfig: TMenuItem;
    SpeedButton1: TSpeedButton;
    imagem: TImage;
    GroupBox1: TGroupBox;
    spbuscategoria: TSpeedButton;
    lblcategnome: TLabel;
    lblsituacaodogrupo: TLabel;
    lbldiocesesdoestado: TLabel;
    lblestado_lbl: TLabel;
    cboestado: TComboBox;
    btnfiltrar: TBitBtn;
    lblcategcodestr: TLabeledEdit;
    cbosituacaogrupos: TComboBox;
    cbodioceses: TComboBox;
    cbocidadesdioceses: TComboBox;
    lblcidadesdadiocese: TLabel;
    spbexportaentidades: TSpeedButton;
    popmnuenviaemail: TMenuItem;
    Panel2: TPanel;
    GroupBox3: TGroupBox;
    gridgrupodeoracao: TDBGrid;
    GroupBox2: TGroupBox;
    Panel3: TPanel;
    gridcoordenadores: TDBGrid;
    lblf5fichafinanceira: TLabel;
    lblf6compara: TLabel;
    grpfichafincoordenador: TGroupBox;
    gridexibedados: TDBGrid;
    grpgrupooracao: TGroupBox;
    gridexibedadosgo: TDBGrid;
    grpgoapolonacidade: TGroupBox;
    gridgoapolonacidade: TDBGrid;
    grpdadossavic: TGroupBox;
    memodadossavic: TMemo;
    grpgruposdacidade: TGroupBox;
    memodetalhesgrupos: TMemo;
    procedure spbretornarClick(Sender: TObject);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cboestadoKeyPress(Sender: TObject; var Key: Char);
    procedure cboestadoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure btnfiltrarClick(Sender: TObject);
    procedure FormActivate(Sender: TObject);
    procedure lblcategcodestrKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure lblnomecidadeKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cbosituacaogruposKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spbuscategoriaClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure cbodiocesesEnter(Sender: TObject);
    procedure cbodiocesesKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cbocidadesdiocesesEnter(Sender: TObject);
    procedure popmnugravaconfigClick(Sender: TObject);
    procedure popmnuenviaemailClick(Sender: TObject);
    procedure DBGrid1CellClick(Column: TColumn);
    procedure gridcoordenadoresCellClick(Column: TColumn);
    procedure gridcoordenadoresDblClick(Sender: TObject);
    procedure gridexibedadosKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure gridgrupodeoracaoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure gridexibedadosgoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure gridcoordenadoresKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure gridgoapolonacidadeKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure memodadossavicKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure memodetalhesgruposKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure spblimparClick(Sender: TObject);
    procedure spbexportaentidadesClick(Sender: TObject);
    procedure gridcoordenadoresDrawColumnCell(Sender: TObject; const Rect: TRect; DataCol: Integer; Column: TColumn; State: TGridDrawState);
    procedure gridgrupodeoracaoDrawColumnCell(Sender: TObject; const Rect: TRect; DataCol: Integer; Column: TColumn; State: TGridDrawState);
    procedure AbrirFichaFinanceiraCoordenador;
  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  frmmoderacaogrupodeoracao: Tfrmmoderacaogrupodeoracao;
  resp: Word;

function mostra_grupodeoracao(idcoordenador: string): string; export;
function detalhe_grupodeoracao(geocidcod: string; basededados: string): string; export;

implementation

{$R *.dfm}

uses
  unt_dados, funcoes, unt_principal, unt_consultav3, unt_logon,
  unt_importa_atualiza_go_savic_apolo, unt_viacep_service;

function ObterEntCodCoordenador(DataSet: TDataSet): string;
var
  Fld: TField;
begin
  Result := '';
  if DataSet = nil then Exit;
  Fld := DataSet.FindField('entcod');
  if Assigned(Fld) and (Trim(Fld.AsString) <> '') then
    Result := Trim(Fld.AsString)
  else
  begin
    Fld := DataSet.FindField('CodigoApolo');
    if Assigned(Fld) then
      Result := Trim(Fld.AsString);
  end;
end;

procedure Tfrmmoderacaogrupodeoracao.btnfiltrarClick(Sender: TObject);
var
  vcidade: string;
  sSql: string;
begin
  with modulo_dados do
  begin
    // Garante que a coluna entcod exista na tabela de coordenadores (Requisito 2)
    try
      fdbanco.ExecSQL(
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

    fdquerysql4.Active := False;

    vcidade := '';
    if (Trim(cbocidadesdioceses.Text) <> '') and (Trim(cboestado.Text) <> '') then
      vcidade := retorna_cidade_estado(Trim(cbocidadesdioceses.Text), Trim(cboestado.Text), frmmoderacaogrupodeoracao);

    sSql := 'SELECT DISTINCT ugcg.cadastroid_coordenador AS IdSavic, ' +
            '       ISNULL(ugcg.entcod, ugcg.entcod_apolo) AS entcod, ' +
            '       ugcg.coordenador, ugcg.cpfcoordenador, ugcg.rgcoordenador, ugcg.datainiciocoordenacao, ' +
            '       ugcg.datafimcoordenacao, ugcg.mandatoindeterminado, ugcg.generocoordenador AS Genero, ' +
            '       ugcg.telefonefixo_coordenador, ugcg.telefonecomercial_coordenador, ugcg.celular_coordenador, ' +
            '       ugcg.celular2_coordenador, ugcg.email, ugcg.endereco_coordenador, ugcg.numero, ugcg.complemento, ' +
            '       ugcg.bairrocoordenador, ugcg.cepcoordenador, ugcg.go_geocidcod, ugcg.dioceseid, ' +
            '       ugc1.cidnomecomp AS CidadeCoordenador, ' +
            '       ugc1.ufsigla AS EstadoCoordenador, ISNULL(ugcg.flagexportado, ''Não'') AS flagexportado ' +
            'FROM USER_geoapolo_coordenadores_grupodeoracao ugcg WITH(NOLOCK) ' +
            'LEFT JOIN USER_geoapolo_cidades ugc1 WITH(NOLOCK) ON ugcg.go_geocidcod = ugc1.geocidcod ' +
            'INNER JOIN USER_geoapolo_gruposdeoracao uggo WITH(NOLOCK) ON ugcg.cadastroid_coordenador = uggo.cadastroid_coordenador ' +
            'WHERE (1=1) ';

    if (vcidade <> '') and (vcidade <> '0') then
      sSql := sSql + 'AND ugcg.go_geocidcod = ' + QuotedStr(vcidade) + ' '
    else if Trim(cboestado.Text) <> '' then
      sSql := sSql + 'AND ugc1.ufsigla = ' + QuotedStr(Trim(cboestado.Text)) + ' ';

    if Trim(cbodioceses.Text) <> '' then
      sSql := sSql + 'AND (ugcg.diocesecoordenador = ' + QuotedStr(Trim(cbodioceses.Text)) +
              ' OR ugcg.dioceseid IN (SELECT id FROM userdioceses_cnbb WITH (NOLOCK) WHERE UPPER(nome) = UPPER(' + QuotedStr(Trim(cbodioceses.Text)) + '))) ';

    if (Trim(cbosituacaogrupos.Text) <> '') and (UpperCase(Trim(cbosituacaogrupos.Text)) <> 'TODOS') then
      sSql := sSql + 'AND uggo.situacao_grupo = ' + QuotedStr(Trim(cbosituacaogrupos.Text)) + ' ';

    sSql := sSql + 'ORDER BY ugcg.coordenador ASC';

    fdquerysql4.Close;
    fdquerysql4.Connection := fdbanco;
    fdquerysql4.SQL.Text := sSql;
    fdquerysql4.Open;

    if fdquerysql4.RecordCount > 0 then
    begin
      dtsfdquerysql4.DataSet := fdquerysql4;
      gridcoordenadores.DataSource := dtsfdquerysql4;
      configura_grid('MODERACAO_GRUPOSDEORACAO', frmmoderacaogrupodeoracao, frmlogon.nomeusuario, 'gridcoordenadores', gridcoordenadores, dtsfdquerysql4);
      gridcoordenadores.Refresh;
      mostra_grupodeoracao(fdquerysql4.FieldByName('IdSavic').AsString);
    end
    else
    begin
      MessageDlg('NENHUM COORDENADOR ENCONTRADO PARA O FILTRO ESPECIFICADO !', mtInformation, [mbOK], 0);
    end;
  end;
end;

procedure Tfrmmoderacaogrupodeoracao.cbocidadesdiocesesEnter(Sender: TObject);
begin
  with modulo_dados do
  begin
    if Trim(cbodioceses.Text) <> '' then
    begin
      fdquerysql1.Close;
      fdquerysql1.Connection := fdbanco;
      fdquerysql1.SQL.Text := 'SELECT id FROM userdioceses_cnbb WHERE nome = ' + QuotedStr(Trim(cbodioceses.Text));
      fdquerysql1.Open;
      if fdquerysql1.RecordCount > 0 then
      begin
        fdquerysql.Close;
        fdquerysql.Connection := fdbanco;
        fdquerysql.SQL.Text := 'SELECT descricao FROM usercidades_cnbb WHERE diocese_id = ' +
                               QuotedStr(fdquerysql1.FieldByName('id').AsString) +
                               ' ORDER BY descricao ASC';
        fdquerysql.Open;
        if fdquerysql.RecordCount > 0 then
        begin
          cbocidadesdioceses.Clear;
          while not fdquerysql.Eof do
          begin
            cbocidadesdioceses.Items.Add(fdquerysql.FieldByName('descricao').AsString);
            fdquerysql.Next;
          end;
          cbocidadesdioceses.Refresh;
        end;
      end;
    end;
  end;
end;

procedure Tfrmmoderacaogrupodeoracao.cbodiocesesEnter(Sender: TObject);
begin
  with modulo_dados do
  begin
    if Trim(cboestado.Text) <> '' then
    begin
      fdquerysql1.Close;
      fdquerysql1.Connection := fdbanco;
      fdquerysql1.SQL.Text := 'SELECT USERiD FROM userestado_cnbb WHERE USERsigla = ' + QuotedStr(Trim(cboestado.Text));
      fdquerysql1.Open;
      if fdquerysql1.RecordCount > 0 then
      begin
        fdquerysql.Close;
        fdquerysql.Connection := fdbanco;
        fdquerysql.SQL.Text := 'SELECT nome FROM userdioceses_cnbb WHERE estado_id = ' +
                               QuotedStr(fdquerysql1.FieldByName('USERiD').AsString) +
                               ' AND ativo = 1 ORDER BY nome ASC';
        fdquerysql.Open;
        if fdquerysql.RecordCount > 0 then
        begin
          cbodioceses.Clear;
          while not fdquerysql.Eof do
          begin
            cbodioceses.Items.Add(fdquerysql.FieldByName('nome').AsString);
            fdquerysql.Next;
          end;
          cbodioceses.Refresh;
        end;
      end
      else
      begin
        MessageDlg('ESTADO NAO ENCONTRADO OU INVALIDO !', mtError, [mbOK], 0);
        Exit;
      end;
    end;
  end;
end;

procedure Tfrmmoderacaogrupodeoracao.cbodiocesesKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then
    cbocidadesdioceses.SetFocus;
end;

procedure Tfrmmoderacaogrupodeoracao.cbosituacaogruposKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then
    btnfiltrar.Click;
end;

procedure Tfrmmoderacaogrupodeoracao.DBGrid1CellClick(Column: TColumn);
begin
  if not modulo_dados.fdquerysql4.IsEmpty then
    mostra_grupodeoracao(modulo_dados.fdquerysql4.FieldByName('IdSavic').AsString);
end;

procedure Tfrmmoderacaogrupodeoracao.FormActivate(Sender: TObject);
begin
  StatusBar1.Panels[1].Text := nomecomputador;
  StatusBar1.Panels[3].Text := configura_statusbar('a');
  StatusBar1.Panels[5].Text := configura_statusbar('a');
  configura_grid('MODERACAO_GRUPOSDEORACAO', frmmoderacaogrupodeoracao, frmlogon.nomeusuario, 'gridcoordenadores', gridcoordenadores, modulo_dados.dtsfdquerysql4);
  configura_grid('MODERACAO_GORACAO', frmmoderacaogrupodeoracao, frmlogon.nomeusuario, 'gridgrupodeoracao', gridgrupodeoracao, modulo_dados.dtsfdquerysql5);
  StatusBar1.Refresh;

  // Carrega lista de estados na combo
  if cboestado.Items.Count = 0 then
  begin
    cboestado.Items.BeginUpdate;
    try
      cboestado.Clear;
      cboestado.Items.Add('');
      with modulo_dados.fdquerysql do
      begin
        Close;
        Connection := modulo_dados.fdbanco;
        SQL.Text := 'SELECT DISTINCT usersigla FROM userestado_cnbb WITH (NOLOCK) ' +
                    'WHERE usersigla IS NOT NULL AND LTRIM(RTRIM(usersigla)) <> '''' ORDER BY usersigla ASC';
        Open;
        while not Eof do
        begin
          cboestado.Items.Add(Trim(FieldByName('usersigla').AsString));
          Next;
        end;
        Close;
      end;
    finally
      cboestado.Items.EndUpdate;
    end;
  end;
end;

procedure Tfrmmoderacaogrupodeoracao.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Action := caFree;
end;

procedure Tfrmmoderacaogrupodeoracao.FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F10 then
    spbretornar.Click;
end;

procedure Tfrmmoderacaogrupodeoracao.gridcoordenadoresCellClick(Column: TColumn);
begin
  if not modulo_dados.fdquerysql4.IsEmpty then
    mostra_grupodeoracao(modulo_dados.fdquerysql4.FieldByName('IdSavic').AsString);
end;

procedure Tfrmmoderacaogrupodeoracao.AbrirFichaFinanceiraCoordenador;
var
  sSql: string;
  vEntCodCoord: string;
begin
  with modulo_dados do
  begin
    vEntCodCoord := ObterEntCodCoordenador(fdquerysql4);
    if (vEntCodCoord <> '') and (vEntCodCoord <> '0') then
    begin
      grpfichafincoordenador.Visible := True;
      grpfichafincoordenador.Top := 8;
      grpfichafincoordenador.Left := 7;

      sSql := 'SELECT pdf.empcod AS Empresa, pdf.tipocobcod AS Codigo_Tipo_Cobranca, tc.TipoCobNome AS TipoCobranca, ' +
              '       MIN(pdf.parcdocfindataemissao) AS PrimeiroRegistro, MAX(pdf.parcdocfindataemissao) AS UltimoRegistro, ' +
              '       SUM(pdf.parcdocfinvalpag) AS VrTotalDoado ' +
              'FROM parc_doc_fin pdf WITH(NOLOCK) ' +
              'INNER JOIN TIPO_COBRANCA tc WITH(NOLOCK) ON pdf.TipoCobCod = tc.TipoCobCod ' +
              'INNER JOIN entidade e WITH(NOLOCK) ON pdf.entcod = e.EntCod ' +
              'WHERE pdf.entcod = ' + QuotedStr(vEntCodCoord) + ' ' +
              '  AND pdf.empcod IN (''1.01'', ''1.03'') ' +
              '  AND pdf.MovCtrlBancNum IS NOT NULL ' +
              'GROUP BY pdf.TipoCobCod, tc.TipoCobNome, pdf.empcod ' +
              'ORDER BY pdf.empcod, tc.TipoCobNome';

      fdquerysql6.Close;
      fdquerysql6.Connection := fdbanco;
      fdquerysql6.SQL.Text := sSql;
      fdquerysql6.Open;

      if fdquerysql6.RecordCount > 0 then
      begin
        dtsfdquerysql6.DataSet := fdquerysql6;
        gridexibedados.DataSource := dtsfdquerysql6;
        gridexibedados.Refresh;
        gridexibedados.SetFocus;
      end;
    end
    else
    begin
      MessageDlg('SEM O CODIGO DE ENTIDADE DO APOLO E IMPOSSIVEL CONSULTAR A FICHA FINANCEIRA DO GRUPO OU DE SEU COORDENADOR !', mtError, [mbOK], 0);
      Exit;
    end;
  end;
end;

procedure Tfrmmoderacaogrupodeoracao.gridcoordenadoresDblClick(Sender: TObject);
begin
  if not modulo_dados.fdquerysql4.IsEmpty then
    AbrirFichaFinanceiraCoordenador;
end;

procedure Tfrmmoderacaogrupodeoracao.gridcoordenadoresKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F5 then
  begin
    AbrirFichaFinanceiraCoordenador;
  end;
end;

procedure Tfrmmoderacaogrupodeoracao.gridexibedadosgoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_ESCAPE then
    grpgrupooracao.Visible := False;
end;

procedure Tfrmmoderacaogrupodeoracao.gridexibedadosKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_ESCAPE then
  begin
    modulo_dados.fdquerysql6.Active := False;
    grpfichafincoordenador.Visible := False;
  end;
end;

procedure Tfrmmoderacaogrupodeoracao.gridgoapolonacidadeKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_ESCAPE then
    grpgoapolonacidade.Visible := False;

  if Key = VK_F6 then
  begin
    if not modulo_dados.fdquerysql8.IsEmpty then
    begin
      detalhe_grupodeoracao(modulo_dados.fdquerysql8.FieldByName('cidcod').AsString, 'GEOAPOLO');
      detalhe_grupodeoracao(modulo_dados.fdquerysql8.FieldByName('cidcod').AsString, 'APOLO');
    end;
  end;
end;

procedure Tfrmmoderacaogrupodeoracao.gridgrupodeoracaoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
var
  sSql: string;
begin
  with modulo_dados do
  begin
    if Key = VK_F5 then
    begin
      if (fdquerysql5.FieldByName('codigoapolo').AsString <> '') and (fdquerysql5.FieldByName('codigoapolo').AsString <> '0') then
      begin
        grpgrupooracao.Visible := True;
        grpgrupooracao.Left := 3;
        grpgrupooracao.Top := 19;

        sSql := 'SELECT pdf.empcod AS Empresa, pdf.tipocobcod AS Codigo_Tipo_Cobranca, tc.TipoCobNome AS TipoCobranca, ' +
                '       MIN(pdf.parcdocfindataemissao) AS PrimeiroRegistro, MAX(pdf.parcdocfindataemissao) AS UltimoRegistro, ' +
                '       SUM(pdf.parcdocfinvalpag) AS VrTotalDoado ' +
                'FROM parc_doc_fin pdf WITH(NOLOCK) ' +
                'INNER JOIN TIPO_COBRANCA tc WITH(NOLOCK) ON pdf.TipoCobCod = tc.TipoCobCod ' +
                'INNER JOIN entidade e WITH(NOLOCK) ON pdf.entcod = e.EntCod ' +
                'WHERE pdf.entcod = ' + QuotedStr(fdquerysql5.FieldByName('codigoapolo').AsString) + ' ' +
                '  AND pdf.empcod IN (''1.01'', ''1.03'') ' +
                '  AND pdf.MovCtrlBancNum IS NOT NULL ' +
                'GROUP BY pdf.TipoCobCod, tc.TipoCobNome, pdf.empcod ' +
                'ORDER BY pdf.empcod, tc.TipoCobNome';

        fdquerysql6.Close;
        fdquerysql6.Connection := fdbanco;
        fdquerysql6.SQL.Text := sSql;
        fdquerysql6.Open;

        if fdquerysql6.RecordCount > 0 then
        begin
          dtsfdquerysql6.DataSet := fdquerysql6;
          gridexibedadosgo.DataSource := dtsfdquerysql6;
          gridexibedadosgo.Refresh;
        end;
      end;
    end;

    if Key = VK_F6 then
    begin
      grpgoapolonacidade.Visible := True;
      grpgoapolonacidade.Left := 628;
      grpgoapolonacidade.Top := 3;

      sSql := 'SELECT e.entcod, e.tipotratcod, e.entnome, e.entlograd, e.entender, e.entenderno, ' +
              '       e.EntEnderComp, e.EntBair, e.entcep, cid.cidnomecomp, cid.ufsigla, e.cidcod ' +
              'FROM entidade e WITH(NOLOCK) ' +
              'INNER JOIN cidade cid WITH(NOLOCK) ON e.cidcod = cid.cidcod ' +
              'INNER JOIN ent_categ ec WITH(NOLOCK) ON e.entcod = ec.entcod ' +
              'WHERE e.cidcod = ' + QuotedStr(fdquerysql5.FieldByName('go_geocidcod').AsString) + ' ' +
              '  AND SUBSTRING(ec.categcodestr, 1, 6) = ' + QuotedStr('02.001') + ' ' +
              'ORDER BY e.entnome ASC';

      fdquerysql8.Close;
      fdquerysql8.Connection := fdbanco;
      fdquerysql8.SQL.Text := sSql;
      fdquerysql8.Open;

      if fdquerysql8.RecordCount > 0 then
      begin
        dtsfdquerysql8.DataSet := fdquerysql8;
        gridgoapolonacidade.DataSource := dtsfdquerysql8;
        gridgoapolonacidade.Refresh;
        gridgoapolonacidade.SetFocus;
      end;
    end;
  end;
end;

procedure Tfrmmoderacaogrupodeoracao.lblcategcodestrKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F4 then
    spbuscategoria.Click;
  if (Key = VK_RETURN) or (Key = VK_TAB) then
    cbosituacaogrupos.SetFocus;
end;

procedure Tfrmmoderacaogrupodeoracao.cboestadoKeyPress(Sender: TObject; var Key: Char);
var
  i: Integer;
  letra: Char;
begin
  if CharInSet(Key, ['a'..'z', 'A'..'Z']) then
  begin
    letra := UpCase(Key);
    for i := 0 to cboestado.Items.Count - 1 do
    begin
      if (Length(Trim(cboestado.Items[i])) > 0) and (UpCase(cboestado.Items[i][1]) = letra) then
      begin
        cboestado.ItemIndex := i;
        cbodioceses.Clear;
        cbocidadesdioceses.Clear;
        cbodiocesesEnter(cboestado);
        Key := #0;
        Break;
      end;
    end;
  end;
end;

procedure Tfrmmoderacaogrupodeoracao.cboestadoKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then
    cbodioceses.SetFocus;
end;

procedure Tfrmmoderacaogrupodeoracao.lblnomecidadeKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if (Key = VK_RETURN) or (Key = VK_TAB) then
    lblcategcodestr.SetFocus;
end;

procedure Tfrmmoderacaogrupodeoracao.memodadossavicKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_ESCAPE then
  begin
    grpdadossavic.Visible := False;
    grpgruposdacidade.Visible := False;
    gridgoapolonacidade.SetFocus;
  end;
end;

procedure Tfrmmoderacaogrupodeoracao.memodetalhesgruposKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_ESCAPE then
  begin
    grpdadossavic.Visible := False;
    grpgruposdacidade.Visible := False;
    gridgoapolonacidade.SetFocus;
  end;
end;

procedure Tfrmmoderacaogrupodeoracao.popmnuenviaemailClick(Sender: TObject);
begin
  MessageDlg('A funcionalidade de disparo de e-mails em lote utiliza as rotinas integradas do GeoAlvo.', mtInformation, [mbOK], 0);
end;

procedure Tfrmmoderacaogrupodeoracao.popmnugravaconfigClick(Sender: TObject);
begin
  grava_configuracoes_grids(frmconsulta3, 'MODERACAO_GRUPOSDEORACAO', gridcoordenadores, 'gridcoordenadores', frmlogon.nomeusuario, modulo_dados.dtsfdquerysql4);
  grava_configuracoes_grids(frmconsulta3, 'MODERACAO_GORACAO', gridgrupodeoracao, 'gridgrupodeoracao', frmlogon.nomeusuario, modulo_dados.dtsfdquerysql5);
  grava_configuracoes_grids(frmconsulta3, 'FICHAFIN_COORDENADORGO', gridexibedados, 'gridexibedados', frmlogon.nomeusuario, modulo_dados.dtsfdquerysql6);
  grava_configuracoes_grids(frmconsulta3, 'FICHAFIN_GO', gridexibedadosgo, 'gridexibedadosgo', frmlogon.nomeusuario, modulo_dados.dtsfdquerysql7);
end;

procedure Tfrmmoderacaogrupodeoracao.gridcoordenadoresDrawColumnCell(Sender: TObject;
  const Rect: TRect; DataCol: Integer; Column: TColumn; State: TGridDrawState);
begin
  if not (gdSelected in State) then
  begin
    if UpperCase(modulo_dados.fdquerysql4.FieldByName('flagexportado').AsString) = 'SIM' then
    begin
      gridcoordenadores.Canvas.Brush.Color := $0099FFFF; // Amarelo suave
      gridcoordenadores.Canvas.Font.Color := clBlack;
    end;
  end;
  gridcoordenadores.DefaultDrawColumnCell(Rect, DataCol, Column, State);
end;

procedure Tfrmmoderacaogrupodeoracao.gridgrupodeoracaoDrawColumnCell(Sender: TObject;
  const Rect: TRect; DataCol: Integer; Column: TColumn; State: TGridDrawState);
begin
  if not (gdSelected in State) then
  begin
    if UpperCase(modulo_dados.fdquerysql5.FieldByName('flagexportado').AsString) = 'SIM' then
    begin
      gridgrupodeoracao.Canvas.Brush.Color := $0099FFFF; // Amarelo suave
      gridgrupodeoracao.Canvas.Font.Color := clBlack;
    end;
  end;
  gridgrupodeoracao.DefaultDrawColumnCell(Rect, DataCol, Column, State);
end;

procedure Tfrmmoderacaogrupodeoracao.spbexportaentidadesClick(Sender: TObject);
var
  vgeoentcod, vgeoentcodgo: string;
  vcpf, vcpfLimpo, sSql, vidcoord, sTemp: string;
  ventcodApolo, vNomeCoord, vEndCoord, vNumCoord, vCompCoord, vBairCoord, vCepCoord, vCidCod: string;
  vNomeCidadeValidar, vUFValidar, vViaCepCidade, vViaCepUF: string;
  vGenero, vTipoTrat, vRg, vRgLimpo: string;
  vCelular, vCelular2, vTelFixo, vTelCom, vEmail: string;
  vCelLimpo, vCelDDD, vCelNum: string;
  vCel2Limpo, vCel2DDD, vCel2Num: string;
  vFixLimpo, vFixDDD, vFixNum: string;
  vComLimpo, vComDDD, vComNum: string;
  vNumSQL: string;
  vDtIniCoordSQL, vDtFimCoordSQL, vMandatoIndet: string;
  vNomeGrupo, vLocalGrupo, vTipoLocal, vCidCodGrupo, vCepGrupo, vCategGrupo: string;
  vtotalcoord, vtotalgo: Integer;
  vgeoentcodgo_novo, vEntidadeExiste, vViaCepOk: Boolean;
  DTOViaCep: TViaCEPDTO;
  QryTemp, QryGrupo: TFDQuery;
  LogFile, sErrDetail: string;
  SL: TStringList;

  function ApenasDigitos(const S: string): string;
  var
    k: Integer;
  begin
    Result := '';
    for k := 1 to Length(S) do
      if CharInSet(S[k], ['0'..'9']) then
        Result := Result + S[k];
  end;

begin
  if modulo_dados.fdquerysql4.IsEmpty then
  begin
    MessageDlg('Nao ha registros filtrados para exportacao !', mtInformation, [mbOK], 0);
    Exit;
  end;

  if MessageDlg('Deseja exportar os registros filtrados para a tabela de Entidades do GeoAlvo?' + sLineBreak +
                '- Coordenadores (Categoria: 02.001.0006)' + sLineBreak +
                '- Grupos de Oracao (Categoria: 02.001 ou selecionada)' + sLineBreak +
                'Os registros exportados serao marcados como Sim e destacados em amarelo.',
                mtConfirmation, [mbYes, mbNo], 0) <> mrYes then
    Exit;

  vtotalcoord := 0;
  vtotalgo := 0;
  sErrDetail := '';

  QryTemp := TFDQuery.Create(nil);
  QryGrupo := TFDQuery.Create(nil);
  try
    QryTemp.Connection := modulo_dados.fdbanco;
    QryGrupo.Connection := modulo_dados.fdbanco;

    // Garante a existencia das novas colunas e ajustes DDL necessarios
    try
      // flagexportado
      modulo_dados.fdbanco.ExecSQL(
        'IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(''USER_geoapolo_coordenadores_grupodeoracao'') AND name = ''flagexportado'') ' +
        'ALTER TABLE USER_geoapolo_coordenadores_grupodeoracao ADD flagexportado VARCHAR(3) NULL CONSTRAINT DF_ugcg_flagexportado DEFAULT ''Não'' WITH VALUES;');
      modulo_dados.fdbanco.ExecSQL(
        'IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(''USER_geoapolo_gruposdeoracao'') AND name = ''flagexportado'') ' +
        'ALTER TABLE USER_geoapolo_gruposdeoracao ADD flagexportado VARCHAR(3) NULL CONSTRAINT DF_uggo_flagexportado DEFAULT ''Não'' WITH VALUES;');

      // 2. entcod na tabela de coordenadores de grupo de oracao
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

      // 1. idsavic na tabela USER_geoapolo_entidade
      modulo_dados.fdbanco.ExecSQL(
        'IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(''USER_geoapolo_entidade'') AND name = ''idsavic'') ' +
        'ALTER TABLE USER_geoapolo_entidade ADD idsavic VARCHAR(50) NULL;');

      // 5. geoentdtinicio na tabela USER_geoapolo_entidade
      modulo_dados.fdbanco.ExecSQL(
        'IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(''USER_geoapolo_entidade'') AND name = ''geoentdtinicio'') ' +
        'ALTER TABLE USER_geoapolo_entidade ADD geoentdtinicio DATE NULL;');

      // 6. geoentdtfim na tabela USER_geoapolo_entidade
      modulo_dados.fdbanco.ExecSQL(
        'IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(''USER_geoapolo_entidade'') AND name = ''geoentdtfim'') ' +
        'ALTER TABLE USER_geoapolo_entidade ADD geoentdtfim DATE NULL;');

      // 7. geomandatocoord na tabela USER_geoapolo_entidade
      modulo_dados.fdbanco.ExecSQL(
        'IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(''USER_geoapolo_entidade'') AND name = ''geomandatocoord'') ' +
        'ALTER TABLE USER_geoapolo_entidade ADD geomandatocoord VARCHAR(3) NULL CONSTRAINT DF_uge_geomandatocoord DEFAULT ''Não'' WITH VALUES;');

      // 11. bairro na tabela USER_geoapolo_entidade
      modulo_dados.fdbanco.ExecSQL(
        'IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(''USER_geoapolo_entidade'') AND name = ''bairro'') ' +
        'ALTER TABLE USER_geoapolo_entidade ADD bairro VARCHAR(60) NULL;');
    except
    end;

    modulo_dados.fdquerysql4.DisableControls;
    try
      modulo_dados.fdquerysql4.First;
      while not modulo_dados.fdquerysql4.Eof do
      begin
        Application.ProcessMessages;
        vidcoord := modulo_dados.fdquerysql4.FieldByName('IdSavic').AsString;
        vNomeCoord := Trim(modulo_dados.fdquerysql4.FieldByName('coordenador').AsString);
        if vNomeCoord = '' then vNomeCoord := 'COORDENADOR SAVIC';
        vcpf := Trim(modulo_dados.fdquerysql4.FieldByName('cpfcoordenador').AsString);
        vcpfLimpo := ApenasDigitos(vcpf);
        vRg := Trim(modulo_dados.fdquerysql4.FieldByName('rgcoordenador').AsString);
        vRgLimpo := ApenasDigitos(vRg);
        if vRgLimpo = '' then vRgLimpo := vRg;

        vEndCoord := Trim(modulo_dados.fdquerysql4.FieldByName('endereco_coordenador').AsString);
        vNumCoord := Trim(modulo_dados.fdquerysql4.FieldByName('numero').AsString);
        vCompCoord := Trim(modulo_dados.fdquerysql4.FieldByName('complemento').AsString);
        vBairCoord := Trim(modulo_dados.fdquerysql4.FieldByName('bairrocoordenador').AsString);
        vCepCoord := ApenasDigitos(modulo_dados.fdquerysql4.FieldByName('cepcoordenador').AsString);

        // 12. CEP e ViaCEP: Consulta e confronto de endereco
        vViaCepOk := False;
        vViaCepCidade := '';
        vViaCepUF := '';

        if Length(vCepCoord) = 8 then
        begin
          try
            if TViaCEPService.Consultar(vCepCoord, DTOViaCep) and DTOViaCep.Sucesso then
            begin
              vViaCepOk := True;
              vViaCepCidade := Trim(DTOViaCep.Cidade);
              vViaCepUF := Trim(DTOViaCep.UF);

              // Confronta logradouro: se vEndCoord estiver vazio, complementa com o retorno do ViaCEP
              if vEndCoord = '' then
                vEndCoord := Trim(DTOViaCep.Logradouro);

              // Confronta bairro: se vBairCoord estiver vazio, usa o bairro do ViaCEP
              if vBairCoord = '' then
                vBairCoord := Trim(DTOViaCep.Bairro);

              // Confronta complemento: se vCompCoord estiver vazio, complementa
              if (vCompCoord = '') and (Trim(DTOViaCep.Complemento) <> '') then
                vCompCoord := Trim(DTOViaCep.Complemento);
            end;
          except
          end;
        end;

        // 13. Cidade: Salvar somente o codigo da cidade na USER_geoapolo_entidade.
        // Validar na tabela USER_geoapolo_cidades e, se nao existir, inserir.
        vCidCod := '';
        if vViaCepOk and (vViaCepCidade <> '') and (vViaCepUF <> '') then
        begin
          vNomeCidadeValidar := vViaCepCidade;
          vUFValidar := vViaCepUF;
        end
        else
        begin
          if Assigned(modulo_dados.fdquerysql4.FindField('CidadeCoordenador')) then
            vNomeCidadeValidar := Trim(modulo_dados.fdquerysql4.FieldByName('CidadeCoordenador').AsString)
          else
            vNomeCidadeValidar := '';

          if Assigned(modulo_dados.fdquerysql4.FindField('EstadoCoordenador')) then
            vUFValidar := Trim(modulo_dados.fdquerysql4.FieldByName('EstadoCoordenador').AsString)
          else
            vUFValidar := '';
        end;

        if (vNomeCidadeValidar <> '') and (vUFValidar <> '') then
        begin
          // 13.1 Verifica se a cidade ja existe em USER_geoapolo_cidades
          QryTemp.Close;
          QryTemp.SQL.Text := 'SELECT TOP 1 geocidcod FROM USER_geoapolo_cidades WITH (NOLOCK) ' +
                              'WHERE UPPER(cidnomecomp) = ' + QuotedStr(UpperCase(vNomeCidadeValidar)) +
                              '  AND UPPER(ufsigla) = ' + QuotedStr(UpperCase(vUFValidar));
          QryTemp.Open;
          if not QryTemp.IsEmpty then
            vCidCod := Trim(QryTemp.FieldByName('geocidcod').AsString);
          QryTemp.Close;

          // 13.2 Se nao existir em USER_geoapolo_cidades, busca na tabela cidade (Apolo)
          if vCidCod = '' then
          begin
            QryTemp.Close;
            QryTemp.SQL.Text := 'SELECT TOP 1 cidcod FROM cidade WITH (NOLOCK) ' +
                                'WHERE UPPER(cidnomecomp) LIKE ' + QuotedStr(UpperCase(vNomeCidadeValidar) + '%') +
                                '  AND UPPER(ufsigla) = ' + QuotedStr(UpperCase(vUFValidar));
            try
              QryTemp.Open;
              if not QryTemp.IsEmpty then
                vCidCod := Trim(QryTemp.FieldByName('cidcod').AsString);
              QryTemp.Close;
            except
            end;

            // 13.3 Se nao existir nem em cidade, gera novo geocidcod numerico sequencial (8 digitos)
            if vCidCod = '' then
            begin
              QryTemp.Close;
              QryTemp.SQL.Text := 'SELECT RIGHT(''00000000'' + CAST(ISNULL(MAX(TRY_CAST(geocidcod AS INT)), 0) + 1 AS VARCHAR(8)), 8) AS novocod ' +
                                  'FROM USER_geoapolo_cidades WITH (NOLOCK)';
              try
                QryTemp.Open;
                vCidCod := Trim(QryTemp.FieldByName('novocod').AsString);
                QryTemp.Close;
              except
              end;
              if vCidCod = '' then
                vCidCod := '00000001';
            end;

            // Insere a nova cidade na tabela USER_geoapolo_cidades
            try
              modulo_dados.fdbanco.ExecSQL(
                'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_cidades WITH (NOLOCK) WHERE UPPER(cidnomecomp) = ' +
                QuotedStr(UpperCase(vNomeCidadeValidar)) + ' AND UPPER(ufsigla) = ' + QuotedStr(UpperCase(vUFValidar)) + ') ' +
                'INSERT INTO USER_geoapolo_cidades (geocidcod, cidnomecomp, ufsigla) VALUES (' +
                QuotedStr(vCidCod) + ', ' + QuotedStr(vNomeCidadeValidar) + ', ' + QuotedStr(vUFValidar) + ')'
              );
            except
            end;
          end;
        end;

        // Fallback de seguranca para codigo de cidade
        if (vCidCod = '') or (vCidCod = '0') then
          vCidCod := Trim(modulo_dados.fdquerysql4.FieldByName('go_geocidcod').AsString);
        if (vCidCod = '') or (vCidCod = '0') then
          vCidCod := '00000001';

        vGenero := UpperCase(Copy(Trim(modulo_dados.fdquerysql4.FieldByName('Genero').AsString), 1, 1));
        if (vGenero <> 'M') and (vGenero <> 'F') then
          vGenero := 'M';
        if vGenero = 'F' then
          vTipoTrat := 'Sra.'
        else
          vTipoTrat := 'Sr.';

        // 8 e 9. Telefones e Celular
        vCelular := Trim(modulo_dados.fdquerysql4.FieldByName('celular_coordenador').AsString);
        vCelular2 := '';
        if Assigned(modulo_dados.fdquerysql4.FindField('celular2_coordenador')) then
          vCelular2 := Trim(modulo_dados.fdquerysql4.FieldByName('celular2_coordenador').AsString);

        vTelFixo := Trim(modulo_dados.fdquerysql4.FieldByName('telefonefixo_coordenador').AsString);
        vTelCom := '';
        if Assigned(modulo_dados.fdquerysql4.FindField('telefonecomercial_coordenador')) then
          vTelCom := Trim(modulo_dados.fdquerysql4.FieldByName('telefonecomercial_coordenador').AsString);

        // 10. Email
        vEmail := Trim(modulo_dados.fdquerysql4.FieldByName('email').AsString);

        vCelLimpo := ApenasDigitos(vCelular);
        if Length(vCelLimpo) >= 10 then
        begin
          vCelDDD := Copy(vCelLimpo, 1, 2);
          vCelNum := Copy(vCelLimpo, 3, Length(vCelLimpo) - 2);
        end
        else
        begin
          vCelDDD := '';
          vCelNum := vCelLimpo;
        end;

        vCel2Limpo := ApenasDigitos(vCelular2);
        if Length(vCel2Limpo) >= 10 then
        begin
          vCel2DDD := Copy(vCel2Limpo, 1, 2);
          vCel2Num := Copy(vCel2Limpo, 3, Length(vCel2Limpo) - 2);
        end
        else
        begin
          vCel2DDD := '';
          vCel2Num := vCel2Limpo;
        end;

        vFixLimpo := ApenasDigitos(vTelFixo);
        if Length(vFixLimpo) >= 10 then
        begin
          vFixDDD := Copy(vFixLimpo, 1, 2);
          vFixNum := Copy(vFixLimpo, 3, Length(vFixLimpo) - 2);
        end
        else
        begin
          vFixDDD := '';
          vFixNum := vFixLimpo;
        end;

        vComLimpo := ApenasDigitos(vTelCom);
        if Length(vComLimpo) >= 10 then
        begin
          vComDDD := Copy(vComLimpo, 1, 2);
          vComNum := Copy(vComLimpo, 3, Length(vComLimpo) - 2);
        end
        else
        begin
          vComDDD := '';
          vComNum := vComLimpo;
        end;

        if ApenasDigitos(vNumCoord) <> '' then
          vNumSQL := ApenasDigitos(vNumCoord)
        else
          vNumSQL := 'NULL';

        // 5 e 6. Datas Inicio e Fim
        if not modulo_dados.fdquerysql4.FieldByName('datainiciocoordenacao').IsNull then
          vDtIniCoordSQL := QuotedStr(FormatDateTime('yyyy-mm-dd', modulo_dados.fdquerysql4.FieldByName('datainiciocoordenacao').AsDateTime))
        else
          vDtIniCoordSQL := 'NULL';

        if not modulo_dados.fdquerysql4.FieldByName('datafimcoordenacao').IsNull then
          vDtFimCoordSQL := QuotedStr(FormatDateTime('yyyy-mm-dd', modulo_dados.fdquerysql4.FieldByName('datafimcoordenacao').AsDateTime))
        else
          vDtFimCoordSQL := 'NULL';

        // 7. Indeterminado -> geomandatocoord
        vMandatoIndet := 'Não';
        if Assigned(modulo_dados.fdquerysql4.FindField('mandatoindeterminado')) then
        begin
          sTemp := UpperCase(Trim(modulo_dados.fdquerysql4.FieldByName('mandatoindeterminado').AsString));
          if (sTemp = 'S') or (sTemp = 'SIM') or (sTemp = '1') or (sTemp = 'TRUE') then
            vMandatoIndet := 'Sim';
        end;

        // Inicia transação por coordenador para garantir consistência
        modulo_dados.fdbanco.StartTransaction;
        try
          // 1. Localiza ou gera codigo da entidade para o Coordenador
          vgeoentcod := '';

          // 1.1 Busca PRIMÁRIA na tabela USER_geoapolo_entidade_documentos pelo CPF
          if vcpfLimpo <> '' then
          begin
            QryTemp.Close;
            QryTemp.SQL.Text := 'SELECT TOP 1 geoentcod FROM USER_geoapolo_entidade_documentos WITH (NOLOCK) ' +
                                'WHERE (geotipodocumento = ''CPF/CNPJ'' OR geotipodocumento LIKE ''%CPF%'') AND ' +
                                '(REPLACE(REPLACE(REPLACE(geonumerodocumento, ''.'', ''''), ''-'', ''''), ''/'', '''') = ' + QuotedStr(vcpfLimpo) + ')';
            QryTemp.Open;
            if not QryTemp.IsEmpty then
              vgeoentcod := Trim(QryTemp.FieldByName('geoentcod').AsString);
            QryTemp.Close;
          end;

          // 1.2 Fallback: se não encontrou por CPF na tabela de documentos, tenta por entcod pré-existente
          if (vgeoentcod = '') then
          begin
            sTemp := ObterEntCodCoordenador(modulo_dados.fdquerysql4);
            if (sTemp <> '') and (sTemp <> '0') then
            begin
              QryTemp.Close;
              QryTemp.SQL.Text := 'SELECT TOP 1 geoentcod FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(sTemp);
              QryTemp.Open;
              if not QryTemp.IsEmpty then
                vgeoentcod := Trim(QryTemp.FieldByName('geoentcod').AsString);
              QryTemp.Close;
            end;
          end;

          // 1.3 Busca na tabela entidade do Apolo para reaproveitar entcod se existir
          ventcodApolo := '';
          if (vcpfLimpo <> '') then
          begin
            QryTemp.Close;
            QryTemp.SQL.Text := 'SELECT TOP 1 entcod FROM entidade WITH (NOLOCK) ' +
                                'WHERE REPLACE(REPLACE(REPLACE(entcpfcgc, ''.'', ''''), ''-'', ''''), ''/'', '''') = ' + QuotedStr(vcpfLimpo);
            try
              QryTemp.Open;
              if not QryTemp.IsEmpty then
                ventcodApolo := Trim(QryTemp.FieldByName('entcod').AsString);
              QryTemp.Close;
            except
            end;
          end;
          if (ventcodApolo = '') then
          begin
            sTemp := ObterEntCodCoordenador(modulo_dados.fdquerysql4);
            if (sTemp <> '') and (sTemp <> '0') then
              ventcodApolo := sTemp;
          end;

          // 1.4 Verifica se a entidade realmente existe na tabela USER_geoapolo_entidade
          vEntidadeExiste := False;
          if vgeoentcod <> '' then
          begin
            QryTemp.Close;
            QryTemp.SQL.Text := 'SELECT TOP 1 geoentcod FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcod);
            QryTemp.Open;
            vEntidadeExiste := not QryTemp.IsEmpty;
            QryTemp.Close;
          end;

          if vEntidadeExiste then
          begin
            // Atualiza entidade existente com os campos mapeados (1, 3, 5, 6, 7, 11, 12, 13)
            sSql := 'UPDATE USER_geoapolo_entidade SET ' +
                    'geoentnome = CASE WHEN ISNULL(NULLIF(' + QuotedStr(vNomeCoord) + ', ''''), '''') <> '''' THEN ' + QuotedStr(vNomeCoord) + ' ELSE geoentnome END, ' +
                    'geoentnomefantasia = ISNULL(NULLIF(geoentnomefantasia, ''''), ISNULL(NULLIF(' + QuotedStr(vNomeCoord) + ', ''''), geoentnome)), ' +
                    'idsavic = ' + QuotedStr(vidcoord) + ', ' +
                    'geoentdtinicio = ' + vDtIniCoordSQL + ', ' +
                    'geoentdtfim = ' + vDtFimCoordSQL + ', ' +
                    'geomandatocoord = ' + QuotedStr(vMandatoIndet) + ', ' +
                    'tipolograd = ISNULL(NULLIF(tipolograd, 0), 1), ' +
                    'geotipotratcod = CASE WHEN ISNULL(geotipotratcod, '''') IN ('''', ''0'') THEN ' + QuotedStr(vTipoTrat) + ' ELSE geotipotratcod END, ' +
                    'geoentender = CASE WHEN ISNULL(NULLIF(' + QuotedStr(vEndCoord) + ', ''''), '''') <> '''' THEN ' + QuotedStr(vEndCoord) + ' ELSE geoentender END, ' +
                    'geoenderno = CASE WHEN ISNULL(NULLIF(' + QuotedStr(vNumCoord) + ', ''''), '''') <> '''' THEN ' + QuotedStr(vNumCoord) + ' ELSE ISNULL(geoenderno, ''S/N'') END, ' +
                    'geoentendercomp = CASE WHEN ISNULL(NULLIF(' + QuotedStr(vCompCoord) + ', ''''), '''') <> '''' THEN ' + QuotedStr(vCompCoord) + ' ELSE geoentendercomp END, ' +
                    'geoentbair = CASE WHEN ISNULL(NULLIF(' + QuotedStr(vBairCoord) + ', ''''), '''') <> '''' THEN ' + QuotedStr(vBairCoord) + ' ELSE geoentbair END, ' +
                    'bairro = CASE WHEN ISNULL(NULLIF(' + QuotedStr(vBairCoord) + ', ''''), '''') <> '''' THEN ' + QuotedStr(vBairCoord) + ' ELSE bairro END, ' +
                    'geoentcep = CASE WHEN ISNULL(NULLIF(' + QuotedStr(vCepCoord) + ', ''''), '''') <> '''' THEN ' + QuotedStr(vCepCoord) + ' ELSE geoentcep END, ' +
                    'geocidcod = CASE WHEN ISNULL(NULLIF(' + QuotedStr(vCidCod) + ', ''''), '''') <> '''' AND ' + QuotedStr(vCidCod) + ' <> ''00000001'' THEN ' + QuotedStr(vCidCod) + ' ELSE ISNULL(NULLIF(geocidcod, ''''), ' + QuotedStr(vCidCod) + ') END, ' +
                    'cidcodapolo = CASE WHEN ISNULL(NULLIF(cidcodapolo, ''''), '''') IN ('''', ''0'', ''00000001'') THEN ' + QuotedStr(vCidCod) + ' ELSE cidcodapolo END, ' +
                    'geotipofj = ISNULL(NULLIF(geotipofj, ''''), ''Física''), ' +
                    'geoentgenero = ISNULL(NULLIF(geoentgenero, ''''), ' + QuotedStr(vGenero) + '), ' +
                    'geofalecido = ISNULL(NULLIF(geofalecido, ''''), ''N''), ' +
                    'geoentloccobrancaomesmo = ISNULL(NULLIF(geoentloccobrancaomesmo, ''''), ''Sim''), ' +
                    'geoentlocentregaomesmo = ISNULL(NULLIF(geoentlocentregaomesmo, ''''), ''Sim''), ' +
                    'geoenttransporteomesmo = ISNULL(NULLIF(geoenttransporteomesmo, ''''), ''Sim''), ' +
                    'geoentdatacad = ISNULL(geoentdatacad, CONVERT(VARCHAR(10), GETDATE(), 120)), ' +
                    'geoentdesdedata = ISNULL(geoentdesdedata, CONVERT(VARCHAR(10), GETDATE(), 120)), ' +
                    'entcod = CASE WHEN ISNULL(entcod, '''') = '''' AND ' + QuotedStr(ventcodApolo) + ' <> '''' THEN ' + QuotedStr(ventcodApolo) + ' ELSE entcod END ' +
                    'WHERE geoentcod = ' + QuotedStr(vgeoentcod);
            modulo_dados.fdbanco.ExecSQL(sSql);
          end
          else
          begin
            // Inserção da Entidade Coordenador
            if vgeoentcod = '' then
              vgeoentcod := geoapolo_configcod(frmprincipal.codigo_empresa, 'USER_geoapolo_entidade', 'Sim');

            sSql := 'INSERT INTO USER_geoapolo_entidade (' +
                    'geoentcod, idsavic, geotipotratcod, geoentnome, geoentnomefantasia, tipolograd, ' +
                    'geoentender, geoenderno, geoentendercomp, geoentbair, bairro, geoentdatacad, geoentdesdedata, ' +
                    'geoentdtinicio, geoentdtfim, geomandatocoord, ' +
                    'geoentcep, geocidcod, geoentgenero, geotipofj, geofalecido, entcod, cidcodapolo, ' +
                    'geoentloccobrancaomesmo, geoentlocentregaomesmo, geoenttransporteomesmo) VALUES (' +
                    QuotedStr(vgeoentcod) + ', ' +
                    QuotedStr(vidcoord) + ', ' +
                    QuotedStr(vTipoTrat) + ', ' +
                    QuotedStr(vNomeCoord) + ', ' +
                    QuotedStr(vNomeCoord) + ', 1, ' + // 1 = Rua
                    QuotedStr(vEndCoord) + ', ' +
                    QuotedStr(vNumCoord) + ', ' +
                    QuotedStr(vCompCoord) + ', ' +
                    QuotedStr(vBairCoord) + ', ' +
                    QuotedStr(vBairCoord) + ', ' +
                    'CONVERT(VARCHAR(10), GETDATE(), 120), CONVERT(VARCHAR(10), GETDATE(), 120), ' +
                    vDtIniCoordSQL + ', ' +
                    vDtFimCoordSQL + ', ' +
                    QuotedStr(vMandatoIndet) + ', ' +
                    QuotedStr(vCepCoord) + ', ' +
                    QuotedStr(vCidCod) + ', ' +
                    QuotedStr(vGenero) + ', ''Física'', ''N'', ' +
                    QuotedStr(ventcodApolo) + ', ' +
                    QuotedStr(vCidCod) + ', ''Sim'', ''Sim'', ''Sim'')';
            modulo_dados.fdbanco.ExecSQL(sSql);
          end;

          // 1.4 USER_geoapolo_entcateg: Categoria 02.001.0006 e 08.009 (Loja) para Coordenador
          sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entcateg WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND geocategcodestr = ''02.001.0006'') ' +
                  'INSERT INTO USER_geoapolo_entcateg (geoentcod, geocategcodestr) VALUES (' + QuotedStr(vgeoentcod) + ', ''02.001.0006'')';
          modulo_dados.fdbanco.ExecSQL(sSql);

          sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entcateg WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND geocategcodestr = ''08.009'') ' +
                  'INSERT INTO USER_geoapolo_entcateg (geoentcod, geocategcodestr) VALUES (' + QuotedStr(vgeoentcod) + ', ''08.009'')';
          modulo_dados.fdbanco.ExecSQL(sSql);

          // 4. USER_geoapolo_entidade_documentos: CPF e RG garantidos
          if vcpfLimpo <> '' then
          begin
            sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_documentos WITH (NOLOCK) ' +
                    'WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND (geotipodocumento = ''CPF/CNPJ'' OR geotipodocumento LIKE ''%CPF%'')) ' +
                    'INSERT INTO USER_geoapolo_entidade_documentos (geoentcod, geotipodocumento, geonumerodocumento, geoobservacoes) VALUES (' +
                    QuotedStr(vgeoentcod) + ', ''CPF/CNPJ'', ' + QuotedStr(vcpfLimpo) + ', ''SAVIC'') ' +
                    'ELSE UPDATE USER_geoapolo_entidade_documentos SET geonumerodocumento = ' + QuotedStr(vcpfLimpo) + ', geoobservacoes = ''SAVIC'' ' +
                    'WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND (geotipodocumento = ''CPF/CNPJ'' OR geotipodocumento LIKE ''%CPF%'')';
            modulo_dados.fdbanco.ExecSQL(sSql);
          end;

          if vRgLimpo <> '' then
          begin
            sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_documentos WITH (NOLOCK) ' +
                    'WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND (geotipodocumento = ''RG/IE'' OR geotipodocumento LIKE ''%RG%'')) ' +
                    'INSERT INTO USER_geoapolo_entidade_documentos (geoentcod, geotipodocumento, geonumerodocumento, geoobservacoes) VALUES (' +
                    QuotedStr(vgeoentcod) + ', ''RG/IE'', ' + QuotedStr(vRgLimpo) + ', ''SAVIC'') ' +
                    'ELSE UPDATE USER_geoapolo_entidade_documentos SET geonumerodocumento = ' + QuotedStr(vRgLimpo) + ', geoobservacoes = ''SAVIC'' ' +
                    'WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND (geotipodocumento = ''RG/IE'' OR geotipodocumento LIKE ''%RG%'')';
            modulo_dados.fdbanco.ExecSQL(sSql);
          end;

          // 8 e 9. USER_geoapolo_entidade_comunicacao: Celulares, Residencial e Comercial
          if vCelNum <> '' then
          begin
            sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_comunicacao WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND geotipotelefone = ''Celular'') ' +
                    'INSERT INTO USER_geoapolo_entidade_comunicacao (geoentcod, geotipotelefone, geotelefoneddd, geotelefonenumero, flagtelprincipal) VALUES (' +
                    QuotedStr(vgeoentcod) + ', ''Celular'', ' + QuotedStr(vCelDDD) + ', ' + QuotedStr(vCelNum) + ', ''S'') ' +
                    'ELSE UPDATE USER_geoapolo_entidade_comunicacao SET geotelefoneddd = ' + QuotedStr(vCelDDD) + ', geotelefonenumero = ' + QuotedStr(vCelNum) + ', flagtelprincipal = ''S'' WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND geotipotelefone = ''Celular''';
            modulo_dados.fdbanco.ExecSQL(sSql);
          end;

          if vCel2Num <> '' then
          begin
            sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_comunicacao WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND geotelefonenumero = ' + QuotedStr(vCel2Num) + ') ' +
                    'INSERT INTO USER_geoapolo_entidade_comunicacao (geoentcod, geotipotelefone, geotelefoneddd, geotelefonenumero, flagtelprincipal) VALUES (' +
                    QuotedStr(vgeoentcod) + ', ''Celular'', ' + QuotedStr(vCel2DDD) + ', ' + QuotedStr(vCel2Num) + ', ''N'') ' +
                    'ELSE UPDATE USER_geoapolo_entidade_comunicacao SET geotelefoneddd = ' + QuotedStr(vCel2DDD) + ', geotelefonenumero = ' + QuotedStr(vCel2Num) + ' WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND geotelefonenumero = ' + QuotedStr(vCel2Num);
            modulo_dados.fdbanco.ExecSQL(sSql);
          end;

          if vFixNum <> '' then
          begin
            sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_comunicacao WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND geotipotelefone = ''Residencial'') ' +
                    'INSERT INTO USER_geoapolo_entidade_comunicacao (geoentcod, geotipotelefone, geotelefoneddd, geotelefonenumero, flagtelprincipal) VALUES (' +
                    QuotedStr(vgeoentcod) + ', ''Residencial'', ' + QuotedStr(vFixDDD) + ', ' + QuotedStr(vFixNum) + ', ''N'') ' +
                    'ELSE UPDATE USER_geoapolo_entidade_comunicacao SET geotelefoneddd = ' + QuotedStr(vFixDDD) + ', geotelefonenumero = ' + QuotedStr(vFixNum) + ' WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND geotipotelefone = ''Residencial''';
            modulo_dados.fdbanco.ExecSQL(sSql);
          end;

          if vComNum <> '' then
          begin
            sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_comunicacao WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND geotipotelefone = ''Comercial'') ' +
                    'INSERT INTO USER_geoapolo_entidade_comunicacao (geoentcod, geotipotelefone, geotelefoneddd, geotelefonenumero, flagtelprincipal) VALUES (' +
                    QuotedStr(vgeoentcod) + ', ''Comercial'', ' + QuotedStr(vComDDD) + ', ' + QuotedStr(vComNum) + ', ''N'') ' +
                    'ELSE UPDATE USER_geoapolo_entidade_comunicacao SET geotelefoneddd = ' + QuotedStr(vComDDD) + ', geotelefonenumero = ' + QuotedStr(vComNum) + ' WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND geotipotelefone = ''Comercial''';
            modulo_dados.fdbanco.ExecSQL(sSql);
          end;

          // 10. USER_geoapolo_entidade_webcontato: E-mail (marcado como principal)
          if (vEmail <> '') and (Pos('@', vEmail) > 0) then
          begin
            sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_webcontato WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ') ' +
                    'INSERT INTO USER_geoapolo_entidade_webcontato (geoentcod, tipo_contato, website, email, flagemailprincipal, comunicador_instantaneo, endereco_comunicador) VALUES (' +
                    QuotedStr(vgeoentcod) + ', ''E-mail'', '''', ' + QuotedStr(vEmail) + ', ''S'', '''', '''') ' +
                    'ELSE UPDATE USER_geoapolo_entidade_webcontato SET tipo_contato = ''E-mail'', email = ' + QuotedStr(vEmail) + ', flagemailprincipal = ''S'' WHERE geoentcod = ' + QuotedStr(vgeoentcod);
            modulo_dados.fdbanco.ExecSQL(sSql);
          end;

          // 1.8 USER_geoapolo_entidade_endereco_adicionais: Residencial
          if vEndCoord <> '' then
          begin
            sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_endereco_adicionais WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ' AND tipo_endereco = ''Residencial'') ' +
                    'INSERT INTO USER_geoapolo_entidade_endereco_adicionais (geoentcod, tipo_endereco, tipologradabrev, endereco, numero, complemento, bairro, geocidcod) VALUES (' +
                    QuotedStr(vgeoentcod) + ', ''Residencial'', ''R.'', ' + QuotedStr(Copy(vEndCoord, 1, 60)) + ', ' + vNumSQL + ', ' +
                    QuotedStr(Copy(vCompCoord, 1, 45)) + ', ' + QuotedStr(Copy(vBairCoord, 1, 45)) + ', ' + QuotedStr(vCidCod) + ')';
            modulo_dados.fdbanco.ExecSQL(sSql);
          end;

          // 1.9 USER_geoapolo_entidade_ativecon: Atividade Econômica 94.91-0
          sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_ativecon WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcod) + ') ' +
                  'INSERT INTO USER_geoapolo_entidade_ativecon (ativeconcodestr, geoentcod) VALUES (''94.91-0'', ' + QuotedStr(vgeoentcod) + ')';
          modulo_dados.fdbanco.ExecSQL(sSql);

          // 2 e Marcação: Atualiza Coordenador com flagexportado = 'Sim' e entcod = vgeoentcod
          sSql := 'UPDATE USER_geoapolo_coordenadores_grupodeoracao SET ' +
                  '  flagexportado = ''Sim'', ' +
                  '  entcod = ' + QuotedStr(vgeoentcod) + ', ' +
                  '  entcod_apolo = ' + QuotedStr(vgeoentcod) + ' ' +
                  'WHERE cadastroid_coordenador = ' + QuotedStr(vidcoord);
          modulo_dados.fdbanco.ExecSQL(sSql);
          Inc(vtotalcoord);

          // 2. Exporta os Grupos de Oração deste coordenador
          QryGrupo.Close;
          QryGrupo.SQL.Text := 'SELECT gocodigo, gonome_grupodeoracao, go_local_grupo, go_tipo_de_local, go_geocidcod, codigoapolo ' +
                               'FROM USER_geoapolo_gruposdeoracao WITH (NOLOCK) ' +
                               'WHERE cadastroid_coordenador = ' + QuotedStr(vidcoord);
          QryGrupo.Open;
          while not QryGrupo.Eof do
          begin
            vNomeGrupo := Trim(QryGrupo.FieldByName('gonome_grupodeoracao').AsString);
            vLocalGrupo := Trim(QryGrupo.FieldByName('go_local_grupo').AsString);
            vTipoLocal := Trim(QryGrupo.FieldByName('go_tipo_de_local').AsString);
            vCidCodGrupo := Trim(QryGrupo.FieldByName('go_geocidcod').AsString);
            if (vCidCodGrupo = '') or (vCidCodGrupo = '0') then
              vCidCodGrupo := vCidCod;
            vCepGrupo := '';

            vgeoentcodgo := '';
            vgeoentcodgo_novo := False;

            // 2.1 Verifica por codigoapolo pré-existente
            if (Trim(QryGrupo.FieldByName('codigoapolo').AsString) <> '') and
               (Trim(QryGrupo.FieldByName('codigoapolo').AsString) <> '0') then
            begin
              QryTemp.Close;
              QryTemp.SQL.Text := 'SELECT TOP 1 geoentcod FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE geoentcod = ' +
                                  QuotedStr(Trim(QryGrupo.FieldByName('codigoapolo').AsString));
              QryTemp.Open;
              if not QryTemp.IsEmpty then
                vgeoentcodgo := QryTemp.FieldByName('geoentcod').AsString;
              QryTemp.Close;
            end;

            // 2.2 Se não encontrado, verifica por nome e cidade
            if vgeoentcodgo = '' then
            begin
              QryTemp.Close;
              QryTemp.SQL.Text := 'SELECT TOP 1 geoentcod FROM USER_geoapolo_entidade WITH (NOLOCK) WHERE UPPER(geoentnome) = ' +
                                  QuotedStr(UpperCase(vNomeGrupo)) + ' AND geocidcod = ' + QuotedStr(vCidCodGrupo);
              QryTemp.Open;
              if not QryTemp.IsEmpty then
                vgeoentcodgo := QryTemp.FieldByName('geoentcod').AsString;
              QryTemp.Close;
            end;

            if vgeoentcodgo = '' then
            begin
              vgeoentcodgo := geoapolo_configcod(frmprincipal.codigo_empresa, 'USER_geoapolo_entidade', 'Sim');
              vgeoentcodgo_novo := True;

              sSql := 'INSERT INTO USER_geoapolo_entidade (' +
                      'geoentcod, geotipotratcod, geoentnome, geoentnomefantasia, tipolograd, ' +
                      'geoentender, geoenderno, geoentendercomp, geoentbair, bairro, geoentdatacad, geoentdesdedata, ' +
                      'geoentcep, geocidcod, geoentgenero, geotipofj, geofalecido, cidcodapolo, ' +
                      'geoentloccobrancaomesmo, geoentlocentregaomesmo, geoenttransporteomesmo) VALUES (' +
                      QuotedStr(vgeoentcodgo) + ', ''0001'', ' +
                      QuotedStr(vNomeGrupo) + ', ' +
                      QuotedStr(vNomeGrupo) + ', 1, ' + // 1 = Rua (numérico!)
                      QuotedStr(vLocalGrupo) + ', ''S/N'', ' +
                      QuotedStr(vTipoLocal) + ', '''', '''', ' +
                      'CONVERT(VARCHAR(10), GETDATE(), 120), CONVERT(VARCHAR(10), GETDATE(), 120), ' +
                      QuotedStr(vCepGrupo) + ', ' +
                      QuotedStr(vCidCodGrupo) + ', ''M'', ''Jurídica'', ''N'', ' +
                      QuotedStr(vCidCodGrupo) + ', ''Sim'', ''Sim'', ''Sim'')';
              modulo_dados.fdbanco.ExecSQL(sSql);
            end
            else
            begin
              sSql := 'UPDATE USER_geoapolo_entidade SET ' +
                      'geoentnome = ' + QuotedStr(vNomeGrupo) + ', ' +
                      'geoentnomefantasia = ISNULL(NULLIF(geoentnomefantasia, ''''), ' + QuotedStr(vNomeGrupo) + '), ' +
                      'tipolograd = ISNULL(NULLIF(tipolograd, 0), 1), ' +
                      'geotipotratcod = ISNULL(NULLIF(geotipotratcod, ''''), ''0001''), ' +
                      'geoentender = CASE WHEN ISNULL(NULLIF(' + QuotedStr(vLocalGrupo) + ', ''''), '''') <> '''' THEN ' + QuotedStr(vLocalGrupo) + ' ELSE geoentender END, ' +
                      'geoenderno = ISNULL(NULLIF(geoenderno, ''''), ''S/N''), ' +
                      'geoentendercomp = CASE WHEN ISNULL(NULLIF(' + QuotedStr(vTipoLocal) + ', ''''), '''') <> '''' THEN ' + QuotedStr(vTipoLocal) + ' ELSE geoentendercomp END, ' +
                      'geocidcod = ' + QuotedStr(vCidCodGrupo) + ', ' +
                      'cidcodapolo = ' + QuotedStr(vCidCodGrupo) + ', ' +
                      'geotipofj = ISNULL(NULLIF(geotipofj, ''''), ''Jurídica''), ' +
                      'geofalecido = ISNULL(NULLIF(geofalecido, ''''), ''N''), ' +
                      'geoentloccobrancaomesmo = ISNULL(NULLIF(geoentloccobrancaomesmo, ''''), ''Sim''), ' +
                      'geoentlocentregaomesmo = ISNULL(NULLIF(geoentlocentregaomesmo, ''''), ''Sim''), ' +
                      'geoenttransporteomesmo = ISNULL(NULLIF(geoenttransporteomesmo, ''''), ''Sim''), ' +
                      'geoentdatacad = ISNULL(geoentdatacad, CONVERT(VARCHAR(10), GETDATE(), 120)), ' +
                      'geoentdesdedata = ISNULL(geoentdesdedata, CONVERT(VARCHAR(10), GETDATE(), 120)) ' +
                      'WHERE geoentcod = ' + QuotedStr(vgeoentcodgo);
              modulo_dados.fdbanco.ExecSQL(sSql);
            end;

            // 2.3 Categoria para o Grupo de Oração
            vCategGrupo := Trim(lblcategcodestr.Text);
            if vCategGrupo = '' then vCategGrupo := '02.001';
            sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entcateg WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcodgo) + ' AND geocategcodestr = ' + QuotedStr(vCategGrupo) + ') ' +
                    'INSERT INTO USER_geoapolo_entcateg (geoentcod, geocategcodestr) VALUES (' + QuotedStr(vgeoentcodgo) + ', ' + QuotedStr(vCategGrupo) + ')';
            modulo_dados.fdbanco.ExecSQL(sSql);

            sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entcateg WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcodgo) + ' AND geocategcodestr = ''08.009'') ' +
                    'INSERT INTO USER_geoapolo_entcateg (geoentcod, geocategcodestr) VALUES (' + QuotedStr(vgeoentcodgo) + ', ''08.009'')';
            modulo_dados.fdbanco.ExecSQL(sSql);

            // 2.4 Atividade Econômica para o Grupo
            sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_ativecon WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcodgo) + ') ' +
                    'INSERT INTO USER_geoapolo_entidade_ativecon (ativeconcodestr, geoentcod) VALUES (''94.91-0'', ' + QuotedStr(vgeoentcodgo) + ')';
            modulo_dados.fdbanco.ExecSQL(sSql);

            // 2.5 Endereço adicional para o local do Grupo
            if vLocalGrupo <> '' then
            begin
              sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_endereco_adicionais WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcodgo) + ' AND tipo_endereco = ''Principal'') ' +
                      'INSERT INTO USER_geoapolo_entidade_endereco_adicionais (geoentcod, tipo_endereco, tipologradabrev, endereco, numero, complemento, bairro, geocidcod) VALUES (' +
                      QuotedStr(vgeoentcodgo) + ', ''Principal'', ''R.'', ' + QuotedStr(Copy(vLocalGrupo, 1, 60)) + ', NULL, ' +
                      QuotedStr(Copy(vTipoLocal, 1, 45)) + ', '''', ' + QuotedStr(vCidCodGrupo) + ')';
              modulo_dados.fdbanco.ExecSQL(sSql);
            end;

            // 2.6 VÍNCULO GRUPO DE ORAÇÃO <-> COORDENADOR (USER_geoapolo_entidade_contato)
            sSql := 'IF NOT EXISTS (SELECT 1 FROM USER_geoapolo_entidade_contato WITH (NOLOCK) WHERE geoentcod = ' + QuotedStr(vgeoentcodgo) + ' AND EntCodContato = ' + QuotedStr(vgeoentcod) + ') ' +
                    'INSERT INTO USER_geoapolo_entidade_contato (' +
                    'geoentcod, entCod, EntCodContato, TipoTratCod, CargoCodEstr, EntContatoCategPrinc, ' +
                    'EntContatoEMail, EntContatoTelefone, EntContatoCelular, CidCod, data_vigencia_inicial, data_vigencia_final) VALUES (' +
                    QuotedStr(vgeoentcodgo) + ', NULL, ' +
                    QuotedStr(vgeoentcod) + ', ' +
                    QuotedStr(vTipoTrat) + ', ''Coordenador'', ''S'', ' +
                    QuotedStr(vEmail) + ', ' +
                    QuotedStr(vTelFixo) + ', ' +
                    QuotedStr(vCelular) + ', ' +
                    QuotedStr(vCidCod) + ', ' +
                    vDtIniCoordSQL + ', ' +
                    vDtFimCoordSQL + ') ' +
                    'ELSE UPDATE USER_geoapolo_entidade_contato SET ' +
                    'TipoTratCod = ' + QuotedStr(vTipoTrat) + ', CargoCodEstr = ''Coordenador'', EntContatoCategPrinc = ''S'', ' +
                    'EntContatoEMail = ' + QuotedStr(vEmail) + ', EntContatoTelefone = ' + QuotedStr(vTelFixo) + ', ' +
                    'EntContatoCelular = ' + QuotedStr(vCelular) + ', CidCod = ' + QuotedStr(vCidCod) + ', ' +
                    'data_vigencia_inicial = ' + vDtIniCoordSQL + ', data_vigencia_final = ' + vDtFimCoordSQL + ' ' +
                    'WHERE geoentcod = ' + QuotedStr(vgeoentcodgo) + ' AND EntCodContato = ' + QuotedStr(vgeoentcod);
            modulo_dados.fdbanco.ExecSQL(sSql);

            // 2.7 Marca Grupo como exportado
            sSql := 'UPDATE USER_geoapolo_gruposdeoracao SET flagexportado = ''Sim'', codigoapolo = ' + QuotedStr(vgeoentcodgo) +
                    ' WHERE gocodigo = ' + QuotedStr(QryGrupo.FieldByName('gocodigo').AsString);
            modulo_dados.fdbanco.ExecSQL(sSql);
            Inc(vtotalgo);

            QryGrupo.Next;
          end;
          QryGrupo.Close;

          modulo_dados.fdbanco.Commit;

        except
          on ECoord: Exception do
          begin
            if modulo_dados.fdbanco.InTransaction then
              modulo_dados.fdbanco.Rollback;
            sErrDetail := sErrDetail + Format('Coordenador: %s (ID: %s, CPF: %s) - Erro: %s',
                                              [vNomeCoord, vidcoord, vcpf, ECoord.Message]) + sLineBreak;
          end;
        end;

        modulo_dados.fdquerysql4.Next;
      end;
    finally
      modulo_dados.fdquerysql4.EnableControls;
    end;

    if sErrDetail <> '' then
    begin
      try
        LogFile := ExtractFilePath(ParamStr(0)) + 'exportacao_erro.log';
        SL := TStringList.Create;
        try
          if FileExists(LogFile) then
            SL.LoadFromFile(LogFile);
          SL.Add('===========================================================================');
          SL.Add(FormatDateTime('yyyy-mm-dd hh:nn:ss', Now) + ' - ERROS DURANTE EXPORTAÇÃO (Moderação SAVIC)');
          SL.Add(sErrDetail);
          SL.Add('===========================================================================');
          SL.SaveToFile(LogFile);
        finally
          SL.Free;
        end;
      except
      end;
    end;

    if (vtotalcoord > 0) or (vtotalgo > 0) then
    begin
      MessageDlg(Format('Exportacao para Entidades concluida!' + sLineBreak +
                        '- Coordenadores exportados: %d' + sLineBreak +
                        '- Grupos de Oracao exportados: %d' + sLineBreak +
                        'Os registros exportados estao destacados em amarelo no grid.', [vtotalcoord, vtotalgo]),
                 mtInformation, [mbOK], 0);
      btnfiltrar.Click;
    end
    else
    begin
      MessageDlg('Nenhum registro foi exportado.' + sLineBreak +
                 'Verifique o arquivo exportacao_erro.log para detalhes.', mtWarning, [mbOK], 0);
    end;

  finally
    QryGrupo.Free;
    QryTemp.Free;
  end;
end;

procedure Tfrmmoderacaogrupodeoracao.spblimparClick(Sender: TObject);
begin
  modulo_dados.fdquerysql4.Close;
  modulo_dados.fdquerysql5.Close;
  cbocidadesdioceses.Clear;
  cbodioceses.Clear;
  cboestado.ItemIndex := -1;
  cboestado.Text := '';
  cbosituacaogrupos.ItemIndex := 0;
  grpfichafincoordenador.Visible := False;
  grpgrupooracao.Visible := False;
  grpgoapolonacidade.Visible := False;
  grpdadossavic.Visible := False;
  grpgruposdacidade.Visible := False;
  cboestado.SetFocus;
end;

procedure Tfrmmoderacaogrupodeoracao.spbretornarClick(Sender: TObject);
begin
  Close;
end;

procedure Tfrmmoderacaogrupodeoracao.spbuscategoriaClick(Sender: TObject);
var
  i: Integer;
  sSql: string;
begin
  with modulo_dados do
  begin
    fdquerysql5.Active := False;
    sSql := 'SELECT cat.categcodestr, cat.categnome ' +
            'FROM categoria cat WITH(NOLOCK) ' +
            'WHERE SUBSTRING(cat.CategCodEstr, 1, 6) IN (' +
            QuotedStr('02.001') + ', ' + QuotedStr('02.002') + ', ' +
            QuotedStr('03.001') + ', ' + QuotedStr('03.002') + ', ' +
            QuotedStr('03.003') + ', ' + QuotedStr('03.004') + ', ' +
            QuotedStr('03.005') + ', ' + QuotedStr('03.006') + ') ' +
            'ORDER BY cat.CategCodEstr ASC';

    fdquerysql5.Close;
    fdquerysql5.Connection := fdbanco;
    fdquerysql5.SQL.Text := sSql;
    fdquerysql5.Open;

    if fdquerysql5.RecordCount > 0 then
    begin
      Application.CreateForm(Tfrmconsulta3, frmconsulta3);
      frmconsulta3.controle := 'CATEGORIA_IMPORTA_GRUPOORACAO';
      frmconsulta3.cbocampo.Items.Clear;
      frmconsulta3.cbordem.Items.Clear;
      for i := 0 to fdquerysql5.Fields.Count - 1 do
      begin
        frmconsulta3.cbocampo.Items.Add(fdquerysql5.Fields[i].DisplayName);
        frmconsulta3.cbordem.Items.Add(fdquerysql5.Fields[i].DisplayName);
      end;
      dtsfdquerysql5.DataSet := fdquerysql5;
      frmconsulta3.gridconsulta.DataSource := dtsfdquerysql5;
      frmconsulta3.gridconsulta.Refresh;
      frmconsulta3.ShowModal;
    end
    else
    begin
      MessageDlg('TABELA DE CATEGORIAS ESTA VAZIA !', mtWarning, [mbOK], 0);
      Exit;
    end;
  end;
end;

function mostra_grupodeoracao(idcoordenador: string): string;
var
  sSql: string;
begin
  Result := '';
  with modulo_dados, frmmoderacaogrupodeoracao do
  begin
    sSql := 'SELECT uggo.gocodigo, uggo.codigoapolo, uggo.gonome_grupodeoracao AS GrupodeOracao, ' +
            '       uggo.go_local_grupo AS Local_Reuniao, uggo.go_tipo_de_local AS Tipo_Local, ' +
            '       UPPER(ugcg.endereco_coordenador) AS Endereco, ugcg.numero, ugcg.complemento, ' +
            '       ugcg.bairrocoordenador, ugcg.cepcoordenador AS cep, uggo.go_geocidcod, ' +
            '       ugc.cidnomecomp, ugc.ufsigla, uggo.dias_semana AS Dias_Reuniao, uggo.horario, ' +
            '       uggo.situacao_grupo, uggo.caracteristica_grupo, ' +
            '       uggo.datainclusao_go AS Data_Inclusao_Savic, uggo.datatualizacao_go AS Ultima_Atualizacao, ' +
            '       ISNULL(uggo.flagexportado, ''Não'') AS flagexportado ' +
            'FROM USER_geoapolo_gruposdeoracao uggo WITH(NOLOCK) ' +
            'INNER JOIN USER_geoapolo_cidades ugc WITH(NOLOCK) ON uggo.go_geocidcod = ugc.geocidcod ' +
            'INNER JOIN USER_geoapolo_coordenadores_grupodeoracao ugcg WITH(NOLOCK) ON uggo.cadastroid_coordenador = ugcg.cadastroid_coordenador ' +
            'WHERE uggo.cadastroid_coordenador = ' + QuotedStr(idcoordenador);

    fdquerysql5.Close;
    fdquerysql5.Connection := fdbanco;
    fdquerysql5.SQL.Text := sSql;
    fdquerysql5.Open;

    if fdquerysql5.RecordCount > 0 then
    begin
      dtsfdquerysql5.DataSet := fdquerysql5;
      gridgrupodeoracao.DataSource := dtsfdquerysql5;
      gridgrupodeoracao.Refresh;
      Result := fdquerysql5.FieldByName('GrupodeOracao').AsString;
    end;
  end;
end;

function detalhe_grupodeoracao(geocidcod: string; basededados: string): string;
begin
  Result := '';
  with modulo_dados, frmmoderacaogrupodeoracao do
  begin
    if basededados = 'GEOAPOLO' then
    begin
      grpdadossavic.Visible := True;
      memodadossavic.Lines.Clear;
      memodadossavic.Lines.Add('Codigo G.O.: ' + fdquerysql5.FieldByName('gocodigo').AsString);
      memodadossavic.Lines.Add('Codigo Apolo: ' + fdquerysql5.FieldByName('codigoapolo').AsString);
      memodadossavic.Lines.Add('Nome do Grupo: ' + fdquerysql5.FieldByName('GrupodeOracao').AsString);
      memodadossavic.Lines.Add('Local Reuniao: ' + fdquerysql5.FieldByName('Local_Reuniao').AsString);
      memodadossavic.Lines.Add('Caracteristica: ' + fdquerysql5.FieldByName('Tipo_Local').AsString);
      memodadossavic.Lines.Add('Endereco: ' + fdquerysql5.FieldByName('endereco').AsString);
      memodadossavic.Lines.Add('Numero: ' + fdquerysql5.FieldByName('numero').AsString);
      memodadossavic.Lines.Add('Bairro: ' + fdquerysql5.FieldByName('bairrocoordenador').AsString);
      memodadossavic.Lines.Add('CEP: ' + fdquerysql5.FieldByName('cep').AsString);
      memodadossavic.Lines.Add('Codigo Cidade: ' + fdquerysql5.FieldByName('go_geocidcod').AsString);
      memodadossavic.Lines.Add('Cidade: ' + fdquerysql5.FieldByName('cidnomecomp').AsString);
      memodadossavic.Lines.Add('Estado: ' + fdquerysql5.FieldByName('ufsigla').AsString);
      memodadossavic.Lines.Add('Dias de Reuniao: ' + fdquerysql5.FieldByName('Dias_Reuniao').AsString);
      memodadossavic.Lines.Add('Horario: ' + fdquerysql5.FieldByName('horario').AsString);
      memodadossavic.Lines.Add('Situacao do Grupo: ' + fdquerysql5.FieldByName('caracteristica_grupo').AsString);
      memodadossavic.Lines.Add('Ultima Atualizacao: ' + fdquerysql5.FieldByName('Ultima_Atualizacao').AsString);
      memodadossavic.Refresh;
      memodadossavic.SetFocus;
    end
    else if basededados = 'APOLO' then
    begin
      grpgruposdacidade.Visible := True;
      memodetalhesgrupos.Lines.Clear;
      memodetalhesgrupos.Lines.Add('Codigo Apolo G.O.: ' + fdquerysql8.FieldByName('entcod').AsString);
      memodetalhesgrupos.Lines.Add('Tratamento: ' + fdquerysql8.FieldByName('tipotratcod').AsString);
      memodetalhesgrupos.Lines.Add('Nome: ' + fdquerysql8.FieldByName('entnome').AsString);
      memodetalhesgrupos.Lines.Add('Endereco: ' + fdquerysql8.FieldByName('entlograd').AsString + ', ' +
                                   fdquerysql8.FieldByName('entender').AsString + ', ' +
                                   fdquerysql8.FieldByName('entenderno').AsString);
      memodetalhesgrupos.Lines.Add('Complemento: ' + fdquerysql8.FieldByName('entendercomp').AsString +
                                   ', Bairro: ' + fdquerysql8.FieldByName('entbair').AsString);
      memodetalhesgrupos.Lines.Add('CEP: ' + fdquerysql8.FieldByName('entcep').AsString);
      memodetalhesgrupos.Lines.Add('Cidade: ' + fdquerysql8.FieldByName('cidnomecomp').AsString + ' - ' +
                                   fdquerysql8.FieldByName('ufsigla').AsString);
      memodetalhesgrupos.Refresh;
      memodetalhesgrupos.SetFocus;
    end;
  end;
end;

end.
