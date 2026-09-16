unit unt_entidades;

interface

uses
  Windows, Messages, SysUtils, Variants, Classes, Graphics, Controls, Forms,
  Dialogs, ComCtrls, StdCtrls, Buttons, ExtCtrls, Grids, DBGrids, Menus, Data.DB,
  IdBaseComponent, IdComponent, IdTCPConnection, IdTCPClient, IdHTTP, System.UITypes,
  IdIOHandler, IdIOHandlerSocket, IdIOHandlerStack, IdSSL, IdSSLOpenSSL,
  System.JSON, FireDAC.Comp.Client, FireDAC.Stan.Param, System.IOUtils, DateUtils,
  uIntegradorGeoApolo, FireDAC.Stan.Option, Vcl.Mask, Clipbrd;

type
  Tfrmentidades = class(TForm)
    panelmenu: TPanel;
    spbsalvar: TSpeedButton;
    spbligacoes: TSpeedButton;
    spbsair: TSpeedButton;
    spblimpar: TSpeedButton;
    lblsair: TLabel;
    spbexcluir: TSpeedButton;
    StatusBar1: TStatusBar;
    GroupBox1: TGroupBox;
    GroupBox7: TGroupBox;
    lblcampo: TLabel;
    lblordem: TLabel;
    lblprocurarpor: TLabeledEdit;
    cbocampo: TComboBox;
    cbordem: TComboBox;
    rdgcrescente: TRadioButton;
    rdgdecrescente: TRadioButton;
    gridentidades: TDBGrid;
    PopupMenu1: TPopupMenu;
    mnugravaconfiguracoes: TMenuItem;
    cbobuscabanco: TComboBox;
    lblbuscaem: TLabel;
    spbexportaentidades: TSpeedButton;
    pnlconfereentidade: TPanel;
    spbatualizaentidadeapolo: TBitBtn;
    memobaseapolo: TMemo;
    lblmensagemgeoapolo: TLabel;
    lblmensagemapolo: TLabel;
    memoplataformasve: TMemo;
    btnignorar: TBitBtn;
    lblentidadeslistadas: TLabel;
    lblnentidadeslistadas: TLabel;
    lbljafoi: TLabel;
    lbltemobservacoes1: TLabel;
    shpobsmoderar: TShape;
    Panel1: TPanel;
    spbjaexportada: TSpeedButton;
    Panel2: TPanel;
    Label1: TLabel;
    spbsobrepoealvo: TBitBtn;
    btnignoraralvo: TBitBtn;
    StringGrid1: TStringGrid;
    procedure FormActivate(Sender: TObject);
    procedure spbsairClick(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction);
    procedure FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure mnugravaconfiguracoesClick(Sender: TObject);
    procedure gridentidadesDblClick(Sender: TObject);
    procedure gridentidadesKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
    procedure cbocampoChange(Sender: TObject);
    procedure cbobuscabancoClick(Sender: TObject);
    procedure FormShow(Sender: TObject);
    procedure gridentidadesDrawColumnCell(Sender: TObject; const Rect: TRect;
      DataCol: Integer; Column: TColumn; State: TGridDrawState);
    procedure btnignorarClick(Sender: TObject);
    procedure rdgcrescenteClick(Sender: TObject);
    procedure rdgdecrescenteClick(Sender: TObject);
    procedure StringGrid1SelectCell(Sender: TObject; ACol, ARow: Integer;
      var CanSelect: Boolean);
    procedure StringGrid1DrawCell(Sender: TObject; ACol, ARow: Integer;
      Rect: TRect; State: TGridDrawState);
    procedure spbsobrepoealvoClick(Sender: TObject);
    procedure lblprocurarporKeyPress(Sender: TObject; var Key: Char);
    procedure spbexportaentidadesClick(Sender: TObject);
  private
    FCarregandoEntidades: Boolean;
    FJaAtivou: Boolean;
    procedure ConfigurarGrid;
    procedure MontarTelaComparacao(QuerySVE, QueryBanco: TFDQuery);
    procedure SelectCell(Sender: TObject; ACol, ARow: Integer; var CanSelect: Boolean);
    procedure ConfigurarGridCompleto(const NomeBase: string);
  public
    filhossimnao, wordem, integraentidadeapolo, falecido, sexo, logradouro,
    codgrauescolar, grauescolaridade, vgeoentcod, ventcod: string;
    vordem: string;
  end;

// =============================================================================
// TIPOS E CONSTANTES — Comparação lado a lado SVE x Alvo
// =============================================================================
type
  TDecisaoLinha = (dlNenhuma, dlManterSVE, dlManterAlvo);

  TMapaCampo = record
    LabelExibicao: string;
    CampoSVE     : string;
    CampoAlvo    : string;
  end;

const
  TOTAL_CAMPOS_MAPA = 14;
  MapaCampos: array[0..TOTAL_CAMPOS_MAPA - 1] of TMapaCampo = (
    (LabelExibicao: 'Nome';             CampoSVE: 'geoentnome';         CampoAlvo: 'entnome'),
    (LabelExibicao: 'CPF / CNPJ';       CampoSVE: 'Documento';          CampoAlvo: 'EntCpfCgc'),
    (LabelExibicao: 'RG / IE';          CampoSVE: 'EntRgIe';            CampoAlvo: 'EntRgIe'),
    (LabelExibicao: 'Logradouro';       CampoSVE: 'tipolograd';         CampoAlvo: 'EntLograd'),
    (LabelExibicao: 'Endereço';         CampoSVE: 'geoentender';        CampoAlvo: 'entender'),
    (LabelExibicao: 'Número';           CampoSVE: 'geoenderno';         CampoAlvo: 'entenderno'),
    (LabelExibicao: 'Complemento';      CampoSVE: 'geoentendercomp';    CampoAlvo: 'EntEnderComp'),
    (LabelExibicao: 'Bairro';           CampoSVE: 'geoentbair';         CampoAlvo: 'entbair'),
    (LabelExibicao: 'CEP';              CampoSVE: 'geoentcep';          CampoAlvo: 'entcep'),
    (LabelExibicao: 'Cidade';           CampoSVE: 'cidnomecomp';        CampoAlvo: 'cidnomecomp'),
    (LabelExibicao: 'Estado';           CampoSVE: 'ufsigla';            CampoAlvo: 'ufsigla'),
    (LabelExibicao: 'E-mail';           CampoSVE: 'Email';              CampoAlvo: 'Email'),
    (LabelExibicao: 'Telefone';         CampoSVE: 'Telefone';           CampoAlvo: 'Telefone'),
    (LabelExibicao: 'Data Aniversário'; CampoSVE: 'geoentdataanivfund'; CampoAlvo: 'EntDataAnivFund')
  );

var
  frmentidades: Tfrmentidades;
  sql: string;
  campos: array[0..29] of string;
  numerocategorias: integer;

  GDecisoes        : array[0..TOTAL_CAMPOS_MAPA - 1] of TDecisaoLinha;
  GLinhasDiferentes: array[0..TOTAL_CAMPOS_MAPA - 1] of Integer;
  GTotalDiferentes : Integer;

function carrega_lista_entidades(basededados: string; tipo_pesquisa: string; filtro: string): string; export;
function verifica_integracao_entidades(empcod: string): string; export;
function retorna_ativ_econ(ativeconcodestr: string): string; export;
function importa_entidade(integracao: string): string; export;
function match_code_com_apolo(geoentcod: string; base_dados: string): string; export;
function atualiza_entcod_alvo_via_cpf(const vcodigogeoentidade: string): string; export;
function match_code_com_alvo(geoentcod: string; base_dados: string): string; export;
function ExtrairConjunto(const Texto: string; Indice: Integer): string; export;

implementation

uses funcoes, unt_dados, unt_logon, unt_cadentidades, unt_principal,
  unt_selecionaempresa, unt_statusbarclock, unt_AlvoEntidade;

{$R *.dfm}

// =============================================================================
// SolicitarSenhaMascarada
// Exibe um dialogo simples (criado em runtime) com campo de senha mascarado
// (PasswordChar), usado para coletar a senha do usuario alvo sem exibi-la.
// =============================================================================
function SolicitarSenhaMascarada(const ATitulo, APrompt: string;
  out ASenha: string): Boolean;
var
  FormSenha : TForm;
  lblProm   : TLabel;
  edtSenha  : TEdit;
  btnOK     : TButton;
  btnCancel : TButton;
begin
  Result := False;
  ASenha := '';
  FormSenha := TForm.CreateNew(Application);
  try
    FormSenha.Caption     := ATitulo;
    FormSenha.ClientWidth  := 340;
    FormSenha.ClientHeight := 120;
    FormSenha.Position    := poScreenCenter;
    FormSenha.BorderStyle := bsDialog;
    FormSenha.BorderIcons := [biSystemMenu];
    FormSenha.KeyPreview  := True;

    lblProm := TLabel.Create(FormSenha);
    lblProm.Parent   := FormSenha;
    lblProm.Left     := 16;
    lblProm.Top      := 12;
    lblProm.Width    := 308;
    lblProm.WordWrap := True;
    lblProm.Caption  := APrompt;

    edtSenha := TEdit.Create(FormSenha);
    edtSenha.Parent       := FormSenha;
    edtSenha.Left         := 16;
    edtSenha.Top          := 44;
    edtSenha.Width        := 308;
    edtSenha.PasswordChar := '*';

    btnOK := TButton.Create(FormSenha);
    btnOK.Parent      := FormSenha;
    btnOK.Caption     := 'OK';
    btnOK.Left        := 168;
    btnOK.Top         := 80;
    btnOK.Width       := 75;
    btnOK.ModalResult := mrOk;
    btnOK.Default     := True;

    btnCancel := TButton.Create(FormSenha);
    btnCancel.Parent      := FormSenha;
    btnCancel.Caption     := 'Cancelar';
    btnCancel.Left        := 249;
    btnCancel.Top         := 80;
    btnCancel.Width       := 75;
    btnCancel.ModalResult := mrCancel;
    btnCancel.Cancel      := True;

    FormSenha.ActiveControl := edtSenha;

    if FormSenha.ShowModal = mrOk then
    begin
      ASenha := edtSenha.Text;
      Result := Trim(ASenha) <> '';
    end;
  finally
    FormSenha.Free;
  end;
end;

// =============================================================================
// btnignorarClick
// =============================================================================
procedure Tfrmentidades.btnignorarClick(Sender: TObject);
var
  vocorcod: string;
begin
  with modulo_dados do
  begin
    resp := messagedlg('Confirma a não atualização deste registro no Alvo (Y/N)',
                       mtconfirmation, [mbyes, mbno], 0);
    if resp = idyes then
    begin
      sql := 'UPDATE USER_geoapolo_Entidade SET atualizou_apolo = :atualizouapolo' +
             ', usucod_atualizou_apolo = :usucodapolo' +
             ' WHERE geoentcod = :geoentcod';
      fdquerysql3.Close;
      fdquerysql3.SQL.Clear;
      fdquerysql3.SQL.Text := sql;
      fdquerysql3.ParamByName('atualizouapolo').AsString := QuotedStr('S');
      fdquerysql3.ParamByName('usucodapolo').AsString    := frmprincipal.usucod_apolo;
      fdquerysql3.ParamByName('geoentcod').AsString      := fdqueryentidade.FieldByName('geoentcod').AsString;
      if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
      begin
        fdquerysql11.Close;
        fdquerysql11.SQL.Clear;
        fdquerysql11.SQL.Text := 'SELECT ocorcod FROM user_geoapolo_entidade WHERE geoentcod = :geoentcod';
        fdquerysql11.ParamByName('geoentcod').AsString := fdqueryentidade.FieldByName('geoentcod').AsString;
        if executaracao(fdquerysql11, fdbanco, true, dtsfdquerysql11) then
          vocorcod := fdquerysql11.FieldByName('ocorcod').AsString;

        sql := 'DECLARE @vocorcod1 varchar(7)' +
               ' exec User_geraocorrencia_projetosv2 ' + frmprincipal.codigo_empresa +
               ', ' + 'F' + ', ' + 'INDIVIDUAL' +
               ', ' + '' + ', ' + '' +
               ', ' + vocorcod + ', ' + '' +
               ', ' + frmlogon.codigousuario +
               ', ' + 'FOI IGNORADA A ATUALIZAÇÃO DE CADASTRO POR ESTAR ATUALIZADO' +
               ', ' + '0000012' + ', ' + '' +
               ', NULL, NULL, ' + '';
        fdcomando.CommandText.Text  := sql;
        try
          fdcomando.Execute;
        except
          on e: exception do ShowMessage(e.Message);
        end;
        gravalog(frmlogon.codigousuario, datetostr(date),
                 'NÃO ATUALIZOU A ENTIDADE ' + campos[0] + ' NO ALVO');
        carrega_lista_entidades(cbobuscabanco.Text, 'Consulta', '');
      end;
    end;
    carrega_lista_entidades(cbobuscabanco.Text, 'Consulta', '');
    pnlconfereentidade.Visible  := False;
    memoplataformasve.Visible   := True;
    memobaseapolo.Visible       := True;
    StringGrid1.Visible         := False;
  end;
end;

// =============================================================================
// cbobuscabancoClick
// =============================================================================
procedure Tfrmentidades.cbobuscabancoClick(Sender: TObject);
begin
  setcursorsql('sql');
  FCarregandoEntidades := False;
  carrega_lista_entidades(cbobuscabanco.Text, 'Consulta', '');
  setcursorsql('');
  ConfigurarGridCompleto(cbobuscabanco.Text);
end;

procedure Tfrmentidades.cbocampoChange(Sender: TObject);
begin
  funcoes.setcursorsql('sql');
  buscanacombo(cbocampo.Text, frmentidades, cbordem);
  cbordem.Refresh;
end;

// =============================================================================
// FormActivate
// =============================================================================
procedure Tfrmentidades.FormActivate(Sender: TObject);
var
  Integrador: TIntegradorGeoApolo;
begin
  setcursorsql('sql');
  with modulo_dados do
  begin
    Integrador := TIntegradorGeoApolo.Create(fdquerysql, fdquerysql2, fdquerysql3);
    try
      Integrador.SincronizaOrigens(cbobuscabanco.Text, integraentidadeapolo);
    finally
      Integrador.Free;
    end;
    lblprocurarpor.SetFocus;
    carrega_lista_entidades('GeoApolo', 'Consulta', '');
    ConfigurarGridCompleto('GeoApolo');
    carrega_config('entidades_geoapolo', frmentidades, cbocampo, cbordem,
                   rdgcrescente, rdgdecrescente);
    funcoes.AjustaLarguraColunas(gridentidades);
    cbobuscabanco.Refresh;
  end;
end;

// =============================================================================
// verifica_integracao_entidades
// =============================================================================
function verifica_integracao_entidades(empcod: string): string;
begin
  setcursorsql('sql');
  with modulo_dados, frmentidades do
  begin
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Add('SELECT integra_entidades_apolo FROM USER_geoapolo_configuracoes WHERE empcod = :empcod');
    fdquerysql.ParamByName('empcod').AsString := empcod;
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
      Result := fdquerysql.FieldByName('integra_entidades_apolo').AsString
    else
       begin
          setcursorsql('sql');
          messagedlg('NÃO EXISTEM PARÂMETROS CONFIGURADOS PARA ESTA EMPRESA, VERIFIQUE !!!', mterror, [mbok], 0);
      Exit;
    end;
  end;
end;

// =============================================================================
// match_code_com_alvo
// =============================================================================
function match_code_com_alvo(geoentcod: string; base_dados: string): string;
begin
  setcursorsql('sql');
  with frmentidades, modulo_dados do
  begin
    setcursorsql('sql');
    ConfigurarGrid;
    if base_dados = 'GeoApolo' then
    begin
      setcursorsql('sql');
      fdquerysql22.Close;
      fdquerysql22.SQL.Clear;
      fdquerysql22.SQL.Text := 'SELECT * FROM entidades_geoapolo WHERE geoentcod = :geoentcod';
      fdquerysql22.ParamByName('geoentcod').AsString := geoentcod;
      if executaracao(fdquerysql22, fdbanco, true, dtsfdquerysql22) then
        dtsfdquerysql22.Dataset := fdquerysql22;
    end
    else if base_dados = 'Alvo' then
    begin
      setcursorsql('sql');
      fdquerysql23.Close;
      fdquerysql23.SQL.Clear;
      fdquerysql23.SQL.Text := 'SELECT * FROM entidades_apolo WHERE entcod = :geoentcod';
      fdquerysql23.ParamByName('geoentcod').AsString := geoentcod;
      if executaracao(fdquerysql23, fdbanco, true, dtsfdquerysql23) then
        dtsfdquerysql23.DataSet := fdquerysql23;
    end;
    if fdquerysql22.Active and fdquerysql23.Active then
      MontarTelaComparacao(fdquerysql22, fdquerysql23);
  end;
end;

// =============================================================================
// match_code_com_apolo
// =============================================================================
function match_code_com_apolo(geoentcod: string; base_dados: string): string;
var
  cabecalho: array[0..29] of string;
  ponteiro: integer;
  cpfgeoapolo, datanascimento: string;
begin
  setcursorsql('sql');
  with frmentidades, modulo_dados do
  begin
    setcursorsql('sql');
    cabecalho[0]  := 'Código Apolo:';
    cabecalho[1]  := 'Tratamento: ';
    cabecalho[2]  := 'Nome: ';
    cabecalho[3]  := 'Logradouro: ';
    cabecalho[4]  := 'Endereço: ';
    cabecalho[5]  := 'Complem.';
    cabecalho[6]  := 'Número: ';
    cabecalho[7]  := 'Bairro: ';
    cabecalho[8]  := 'Cep: ';
    cabecalho[9]  := 'Cód.Cidade: ';
    cabecalho[10] := 'Cidade: ';
    cabecalho[11] := 'Estado: ';
    cabecalho[12] := 'Tipo Pessoa: ';
    cabecalho[13] := 'RG / IE: ';
    cabecalho[14] := 'CPF / CNPJ:';
    cabecalho[15] := 'Data Aniv.: ';
    cabecalho[16] := 'Gênero: ';
    cabecalho[17] := 'Id.Diocese: ';
    cabecalho[18] := 'Diocese: ';
    cabecalho[19] := 'Tipo Cobrança: ';
    cabecalho[20] := 'Nome Tipo Cob: ';
    cabecalho[21] := 'Dia Contribuição';
    cabecalho[22] := 'Valor Contribuição: ';
    cabecalho[23] := 'Número Bco: ';
    cabecalho[24] := 'Número Agência: ';
    cabecalho[25] := 'Nome Agência: ';
    cabecalho[26] := 'Conta Bancária: ';
    cabecalho[27] := 'Nome Banco: ';
    cabecalho[28] := 'E-Mails: ';
    cabecalho[29] := 'Telefones: ';

    if base_dados = 'GeoApolo' then
    begin
       setcursorsql('sql');
       sql := 'SELECT uge.geoentcod, uge.entcod, uge.geoentnome, uge.geotipentcod,' +
             ' uge.geoentsit, uge.geoentdatcad, uge.geopescod, uge.geotabentcod,' +
             ' uge.geousucod, uge.geocidcod, uge.geousumod, uge.geodatmod,' +
             ' uge.geoentobs, uge.geoentdataalt, uge.geoentdatainativ, uge.geoentdatreab,' +
             ' (SELECT dbo.fnGeoEntidadeEmail(uge.geoentcod,3)) AS Email,' +
             ' (SELECT dbo.fnGeoPessoaTelefone(uge.geoentcod,3)) AS Telefone,' +
             ' (SELECT dbo.fnGeoPessoaEndereco(uge.geoentcod,3)) AS Endereco,' +
             ' (SELECT dbo.fnGeoPessoaCidade(uge.geoentcod,3)) AS Cidade,' +
             ' uged.geonumerodocumento AS Documento' +
             ' FROM USER_geoapolo_entidade uge WITH(NOLOCK)' +
             ' LEFT JOIN USER_geoapolo_entidade_documentos uged WITH(NOLOCK)' +
             '   ON uge.geoentcod = uged.geoentcod AND uged.geotipodocumento = ''CPF/CNPJ''' +
             ' WHERE uge.geoentcod = ' + QuotedStr(geoentcod);
    end
    else if base_dados = 'Alvo' then
    begin
      setcursorsql('sql');
      sql := 'SELECT e.entcod, e.tipotratcod, e.entnome, e.EntLograd, e.entender, e.EntEnderComp, e.entenderno,' +
             ' e.entbair, e.entcep, e.cidcod, cid.cidnomecomp, cid.ufsigla, e.EntTipoFJ, e.EntRgIe, e.EntCpfCgc,' +
             ' e.EntDataAnivFund, e.EntGenero, e1.USERDiocese_id, e1.USERNomeDiocese, e.tipocobcod, tc.tipocobnome,' +
             ' e1.USERDia_Debito_CC, e1.USERValor_Contribuicao,' +
             ' e.bconum, bco.bconome, e.agnum, ag.agnome as agnome, e.entbcoagccornum,' +
             ' (SELECT dbo.fnEntidadeEmail(e.entcod,3)) as Email,' +
             ' (SELECT dbo.fnPessoaTelefone(e.entcod, 3)) as Telefone' +
             ' FROM entidade e WITH(NOLOCK)' +
             ' INNER JOIN cidade cid WITH(NOLOCK) ON e.cidcod = cid.CidCod' +
             ' INNER JOIN u_entidade e1 WITH(NOLOCK) ON e.entcod = e1.EntCod' +
             ' INNER JOIN tipo_cobranca tc WITH(NOLOCK) ON e.tipocobcod = tc.tipocobcod' +
             ' LEFT JOIN banco bco WITH(NOLOCK) ON e.bconum = bco.bconum' +
             ' LEFT JOIN ag_bancaria ag WITH(NOLOCK) ON e.agnum = ag.agnum AND ag.bconum = bco.BcoNum' +
             ' WHERE e.entcod = ' + QuotedStr(geoentcod);
    end;

    fdquerysql17.Close;
    fdquerysql17.SQL.Clear;
    fdquerysql17.SQL.Text := sql;
    if executaracao(fdquerysql17, fdbanco, true, dtsfdquerysql17) then
    begin
       setcursorsql('sql');
       fdquerysql17.First;
       while not fdquerysql17.EOF do
       begin
          setcursorsql('sql');
          for ponteiro := 0 to 29 do
          begin
            if base_dados = 'GeoApolo' then
            begin
              setcursorsql('sql');
              if ponteiro = 15 then
              begin
                 setcursorsql('sql');
                 datanascimento := FormatDateTime('dd/MM/yyyy', ConvertISODate(fdquerysql17.Fields[ponteiro].AsString));
              if datanascimento = '01/01/1970' then
                datanascimento := 'Data Aniv: Não preenchido';
              memoplataformasve.Lines.Add(cabecalho[ponteiro] + ' ' + datanascimento);
              end
            else
               memoplataformasve.Lines.Add(cabecalho[ponteiro] + ' ' +
               fdquerysql17.Fields[ponteiro].AsString);
               campos[ponteiro] := fdquerysql17.Fields[ponteiro].AsString;
               cpfgeoapolo := fdquerysql17.FieldByName('geonumerodocumento').AsString;
            end
          else if base_dados = 'Alvo' then
            memobaseapolo.Lines.Add(cabecalho[ponteiro] + ' ' +
              fdquerysql17.Fields[ponteiro].AsString);
        end;
        fdquerysql17.Next;
      end;
    end;
  end;
end;

// =============================================================================
// spbexportaentidadesClick — mantido igual ao original
// =============================================================================
procedure Tfrmentidades.spbexportaentidadesClick(Sender: TObject);
var
  Campo, Valor, cepvalor, numerolimpo, vusucodapolo, vretorno,
  vorigcodestr, jsonformatado, vMensagem, vsenhaalvoplano,
  vsenhaalvocriptografada: string;
  i, a, ncampos: integer;
  Entidade   : TEntidade;
  API        : TAlvoAPI;
  Tel        : TTelefone;
  Email      : TEmail;
  Cat        : TCategoria;
  vDocCPFCNPJ: string;
  vDocRGIE   : string;
  senhaalvo  : string;
begin
  with frmentidades, modulo_dados do
  begin
    memobaseapolo.Clear;
    memoplataformasve.Clear;

    if (cbobuscabanco.Text = 'GeoApolo') and (fdqueryentidade.FieldByName('entobservacoes').AsString = '') then
    begin
      if (fdqueryentidade.FieldByName('entcod').AsString = null) or (fdqueryentidade.FieldByName('entcod').AsString = '') then
      begin
        ventcod := '';
        sql := 'SELECT geonumerodocumento FROM USER_geoapolo_entidade_documentos' +
               ' WHERE geoentcod = :geoentcod' +
               ' AND geotipodocumento like ' + QuotedStr('%CPF/CNPJ%');
        fdquerysql18.Close; fdquerysql18.SQL.Clear;
        fdquerysql18.SQL.Text := sql;
        fdquerysql18.ParamByName('geoentcod').AsString := fdqueryentidade.FieldByName('geoentcod').AsString;
        if executaracao(fdquerysql18, fdbanco, true, dtsfdquerysql18) then
        begin
          fdquerysql1.Close; fdquerysql1.SQL.Clear;
          fdquerysql1.SQL.Text := 'SELECT entcod FROM entidades_geoapolo WHERE entcpfcgc = :geonumerodocumento';
          fdquerysql1.ParamByName('geonumerodocumento').AsString := fdquerysql18.FieldByName('geonumerodocumento').AsString;
          if executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) then
          begin
            ventcod := fdquerysql1.FieldByName('entcod').AsString;
            fdquerysql3.Close; fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text := 'UPDATE USER_geoapolo_entidade SET entcod = :entcod WHERE geoentcod = :geoentcod';
            fdquerysql3.ParamByName('entcod').AsString    := ventcod;
            fdquerysql3.ParamByName('geoentcod').AsString := fdqueryentidade.FieldByName('geoentcod').AsString;
            executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);
          end;
        end;
      end;

      if fdqueryentidade.FieldByName('entcod').AsString = '' then
        ventcod := ''
      else if fdqueryentidade.Active and (fdqueryentidade.RecordCount > 0) then
        begin
          if fdqueryentidade.FindField('entcod') <> nil then
            ventcod := Trim(fdqueryentidade.FieldByName('entcod').AsString)
          else
            ventcod := '';
        end;

      if Trim(ventcod) <> '' then
        begin
          panel2.Visible := True; panel2.Top := 85; panel2.Left := 24; panel2.Refresh;
          if frmprincipal.usucod_apolo = '' then
            begin
              vusucodapolo := UpperCase(InputBox('Seu Usuário Alvo', 'Login Alvo', ''));
              frmprincipal.usucod_apolo := vusucodapolo;
              fdquerysql3.Close; fdquerysql3.SQL.Clear;
              fdquerysql3.SQL.Text :='UPDATE USER_geoapolo_usuarios SET usucod_apolo = :usucodapolo WHERE usucod = :codigousuario';
              fdquerysql3.ParamByName('usucodapolo').AsString   := vusucodapolo;
              fdquerysql3.ParamByName('codigousuario').AsString := frmlogon.codigousuario;
              executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);
            end;
          match_code_com_alvo(modulo_dados.fdqueryentidade.FieldByName('geoentcod').AsString, 'GeoApolo');
          if ventcod <> '' then
            match_code_com_alvo(ventcod, 'Alvo');
        end
      else if ventcod = '' then
      begin
        resp := messagedlg('Confirma a exportação desta entidade para o Alvo ? (Y/N)', mtconfirmation, [mbyes, mbno], 0);
        if resp = idyes then
        begin
          vDocCPFCNPJ := ''; vDocRGIE := '';
          fdquerysql18.Close; fdquerysql18.SQL.Clear;
          fdquerysql18.SQL.Text :=
            'SELECT geotipodocumento, geonumerodocumento' +
            ' FROM USER_geoapolo_entidade_documentos WHERE geoentcod = :geoentcod';
          fdquerysql18.ParamByName('geoentcod').AsString := fdqueryentidade.FieldByName('geoentcod').AsString;
          if executaracao(fdquerysql18, fdbanco, true, dtsfdquerysql18) then
          begin
            fdquerysql18.First;
            while not fdquerysql18.EOF do
            begin
              if Pos('CPF', UpperCase(fdquerysql18.FieldByName('geotipodocumento').AsString)) > 0 then
                vDocCPFCNPJ := fdquerysql18.FieldByName('geonumerodocumento').AsString
              else if Pos('RG', UpperCase(fdquerysql18.FieldByName('geotipodocumento').AsString)) > 0 then
                vDocRGIE := fdquerysql18.FieldByName('geonumerodocumento').AsString;
              fdquerysql18.Next;
            end;
          end;
          vgeoentcod := fdqueryentidade.FieldByName('geoentcod').AsString;
          Entidade.Operacao          := 'I';
          Entidade.Codigo            :='';
          Entidade.CodigoAlternativo := fdqueryentidade.FieldByName('geoentcod').AsString;
          Entidade.CodigoTipoTratamento := fdqueryentidade.FieldByName('tipotratcod').AsString;
          Entidade.Nome              := fdqueryentidade.FieldByName('geoentnome').AsString;
          Entidade.NomeFantasia      := fdqueryentidade.FieldByName('geoentnomefantasia').AsString;
          Entidade.CodigoAtivEconomica:='null';
          Entidade.CodigoOrigem      := fdqueryentidade.FieldByName('origcodestr').AsString;
          Entidade.EntidadeDesde     := fdqueryentidade.FieldByName('entdesdedata').AsString;
          Entidade.DataCadastro      := fdqueryentidade.Fieldbyname('entdatacad').AsString;
          Entidade.CodigoTipoLograd  := fdqueryentidade.FieldByName('entlograd').AsString;
          Entidade.Endereco          := fdqueryentidade.FieldByName('geoentender').AsString;
          Entidade.NumeroEndereco    := fdqueryentidade.FieldByName('entenderno').AsString;
          Entidade.NumeroEnderecoParImpar:= parouimpar(fdqueryentidade.FieldByName('entenderno').asstring);
          Entidade.ComplementoEndereco := fdqueryentidade.FieldByName('entendercomp').AsString;
          Entidade.Bairro            := fdqueryentidade.FieldByName('entbair').AsString;
          Entidade.CodigoCidade      := fdqueryentidade.FieldByName('cidcod').AsString;
          Entidade.Cep               := fdqueryentidade.FieldByName('entcep').AsString;
          Entidade.Tipo              := fdqueryentidade.FieldByName('enttipofj').AsString;
          Entidade.CPFCNPJ           := vDocCPFCNPJ;
          Entidade.RGIE              := vDocRGIE;
          Entidade.OrgaoExpedidor    := '';
          Entidade.Agropecuarista    := 'Não';
          Entidade.InscricaoAgropecuarista:= 'null';
          Entidade.CaixaPostal       := fdqueryentidade.FieldByName('entcxapost').AsString;
          Entidade.CodigoRegiao      := fdqueryentidade.FieldByName('georegcodestr').AsString;
          Entidade.Conceito          := fdqueryentidade.FieldByName('entconceito').AsString;
          Entidade.CodigoCondPag     := 'null';
          Entidade.AlteraCondicaoPagamento:='Sim';
          Entidade.CodigoTipoCobranca := fdqueryentidade.FieldByName('tipocobcod').asstring;
          Entidade.DataFundacao       := DateToISO8601(fdqueryentidade.fieldbyname('entdataanivfund').AsDateTime);
          Entidade.CodigoCargo        := fdqueryentidade.FieldByName('cargocodestr').AsString;
          Entidade.Genero            := fdqueryentidade.FieldByName('entgenero').AsString;
          Entidade.CodigoStatus      := 'Ativo';
          Entidade.CaracteristicaImovel := 0;
//          Entidade.InscricaoSuframa       := '';
  //        Entidade.CodigoExcPISCOFINS     := '';
    //      Entidade.MotivoDesoneracaoICMS  := '';
          Entidade.Natureza          := 'Consumidor';
          Entidade.ComunicacaoEtiqueta      := 'Sim';
          Entidade.ComunicacaoEmail         := 'Sim';
          Entidade.ComunicacaoMalaDireta    := 'Não';
          Entidade.ComunicacaoTelemarketing := 'Não';
          Entidade.NumeroBanco         := '';
          Entidade.NumeroAgBancaria    := '';
          Entidade.NumeroContaCorrente := '';
          Entidade.ValorContribuicao   := fdqueryentidade.FieldByName('USERValor_Contribuicao').AsFloat;
          numerocategorias := ContarVirgulas(fdqueryentidade.FieldByName('categcodestr').AsString);
          SetLength(Entidade.Categorias, numerocategorias + 1);
          for a := 0 to numerocategorias do
          begin
            Entidade.Categorias[a].Operacao         := 'I';
            Entidade.Categorias[a].Codigo           :=
            ExtrairConjunto(fdqueryentidade.FieldByName('categcodestr').AsString, a);
            Entidade.Categorias[a].AtivaTabelaPreco := 'Sim';
          end;
          //SetLength(Entidade.Telefones, 0);
          fdquerysql1.Close;
          fdquerysql1.SQL.Clear;
          fdquerysql1.SQL.Text :='SELECT * FROM USER_geoapolo_entidade_comunicacao WHERE geoentcod = :geoentcod';
          fdquerysql1.ParamByName('geoentcod').AsString := fdqueryentidade.FieldByName('geoentcod').AsString;
          if executaracao(fdquerysql1, fdbanco, true, dtsfdquerysql1) then
          begin
            i := 0; fdquerysql1.First;
            while not fdquerysql1.EOF do
            begin
              SetLength(Entidade.Telefones, i + 1);
              Entidade.Telefones[i].Operacao    := 'I';
              Entidade.Telefones[i].Sequencia   := i + 1;
              Entidade.Telefones[i].Tipo        := fdquerysql1.FieldByName('geotipotelefone').AsString;
              Entidade.Telefones[i].DDI         := '55';
              Entidade.Telefones[i].DDD         := fdquerysql1.FieldByName('geotelefoneddd').AsString;
              Entidade.Telefones[i].Numero      := fdquerysql1.FieldByName('geotelefonenumero').AsString;
              Entidade.Telefones[i].NumeroRamal := '';
              Entidade.Telefones[i].Principal   := IfThen(i = 0, 'Sim', 'Não');
              Entidade.Telefones[i].Descricao   := '';
              Entidade.Telefones[i].NFe         := 'Não';
              Entidade.Telefones[i].NFSe        := 'Não';
              Inc(i); fdquerysql1.Next;
            end;
          end;
          SetLength(Entidade.Enderecos, 1);
          Entidade.Enderecos[0].Operacao                  := 'I';
          Entidade.Enderecos[0].Sequencia                 := 1;
          Entidade.Enderecos[0].CodigoEntidade            := Entidade.CodigoAlternativo; // vincula ao mesmo geoentcod
          Entidade.Enderecos[0].CodigoEntidadeRelacionada := '';
          Entidade.Enderecos[0].EnderecoEntrega           := 'Sim';
          Entidade.Enderecos[0].EnderecoCobranca          := 'Não';
          Entidade.Enderecos[0].EnderecoFaturamento       := 'Não';
          Entidade.Enderecos[0].EnderecoColeta            := 'Não';
          Entidade.Enderecos[0].Nome                      := Entidade.Nome;
          Entidade.Enderecos[0].Logradouro                := Entidade.CodigoTipoLograd;
          Entidade.Enderecos[0].Endereco                  := Entidade.Endereco;
          Entidade.Enderecos[0].NumeroEndereco            := Entidade.NumeroEndereco;
          Entidade.Enderecos[0].NumeroEnderecoParImpar    := '';
          Entidade.Enderecos[0].ComplementoEndereco       := Entidade.ComplementoEndereco;
          Entidade.Enderecos[0].Bairro                    := Entidade.Bairro;
          Entidade.Enderecos[0].CodigoCidade              := Entidade.CodigoCidade;
          Entidade.Enderecos[0].Cep                       := Entidade.Cep;
          Entidade.Enderecos[0].TipoFisicaJuridica        := Entidade.Tipo;
          Entidade.Enderecos[0].CPFCNPJ                   := Entidade.CPFCNPJ;
          Entidade.Enderecos[0].RGIE                      := Entidade.RGIE;
          Entidade.Enderecos[0].OrgaoExpedidor            := Entidade.OrgaoExpedidor;
          Entidade.Enderecos[0].CaixaPostal               := '';
          Entidade.Enderecos[0].Email                     := '';
          Entidade.Enderecos[0].PaginaWeb                 := '';
          Entidade.Enderecos[0].NomeContato               := '';
          Entidade.Enderecos[0].TextoLivre                := '';
          Entidade.Enderecos[0].DataValidadeInicial       := Now;
          Entidade.Enderecos[0].DataValidadeFinal         := IncYear(Now, 100); // "sem validade" na prática
          Entidade.Enderecos[0].EnderecoCertificado       := 'Não';
          {------------------ CONTATOS ----------------------------------------------------------------}
          SetLength(Entidade.Contatos, 0);
          fdquerysql3.Close; fdquerysql3.SQL.Clear;
          fdquerysql3.SQL.Text :=
            'SELECT econt.EntCodContato, uge.geoentnome, uge.tipolograd, uge.geoentender, ' +
            ' uge.geoenderno, uge.geoentendercomp, uge.geoentbair, uge.geocidcod, uge.geoentcep, ' +
            ' uge.geotipofj, econt.EntContatoCelular, econt.EntContatoTelefone' +
            ' FROM USER_geoapolo_entidade_contato econt WITH(NOLOCK)' +
            ' INNER JOIN USER_geoapolo_entidade uge WITH(NOLOCK) ON econt.EntCodContato = uge.geoentcod' +
            ' WHERE econt.geoentcod = :geoentcod';
          fdquerysql3.ParamByName('geoentcod').AsString := fdqueryentidade.FieldByName('geoentcod').AsString;
          if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
          begin
            fdquerysql3.First;
            if not fdquerysql3.EOF then
            begin
              SetLength(Entidade.Contatos, 1);
              Entidade.Contatos[0].Operacao      := 'I';
              Entidade.Contatos[0].Codigo        := fdquerysql3.FieldByName('EntCodContato').AsString;
              Entidade.Contatos[0].Nome          := fdquerysql3.FieldByName('geoentnome').AsString;
              Entidade.Contatos[0].Endereco      := fdquerysql3.FieldByName('geoentender').AsString;
              Entidade.Contatos[0].NumeroEndereco:= fdquerysql3.FieldByName('geoentenderno').AsString;
              Entidade.Contatos[0].Bairro        := fdquerysql3.FieldByName('geoentbair').AsString;
              Entidade.Contatos[0].CodigoCidade  := fdquerysql3.FieldByName('geocidcod').AsString;
              Entidade.Contatos[0].Cep           := fdquerysql3.FieldByName('geoentcep').AsString;
              Entidade.Contatos[0].TipoFisicaJuridica := fdquerysql3.FieldByName('geotipofj').AsString;
              Entidade.Contatos[0].Principal     := 'Sim';
              Entidade.Contatos[0].CodigoStatus  := 'Ativo';
              // CPFCNPJ, RGIE, Email: preencher quando souber a fonte certa
              SetLength(Entidade.Contatos[0].Telefones, 1);
              Entidade.Contatos[0].Telefones[0].Operacao  := 'I';
              Entidade.Contatos[0].Telefones[0].Sequencia := 1;
              Entidade.Contatos[0].Telefones[0].Numero    := fdquerysql3.FieldByName('EntContatoCelular').AsString;
              Entidade.Contatos[0].Telefones[0].Principal := 'Sim';
            end;
          end;
          {-------------------------------------------------------------------------------------------------------}
          //SetLength(Entidade.Emails, 0);
          fdquerysql3.Close; fdquerysql3.SQL.Clear;
          fdquerysql3.SQL.Text :=
            'SELECT * FROM USER_geoapolo_entidade_webcontato WHERE geoentcod = :geoentcod';
          fdquerysql3.ParamByName('geoentcod').AsString := fdqueryentidade.FieldByName('geoentcod').AsString;
          if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
          begin
            i := 0; fdquerysql3.First;
            while not fdquerysql3.EOF do
            begin
              SetLength(Entidade.Emails, i + 1);
              Entidade.Emails[i].Operacao  := 'I';
              Entidade.Emails[i].Sequencia := i + 1;
              Entidade.Emails[i].Tipo      := 'COM';
              Entidade.Emails[i].Email     := fdquerysql3.FieldByName('email').AsString;
              Entidade.Emails[i].Principal := IfThen(i = 0, 'S', 'N');
              Entidade.Emails[i].NFe       := 'Não';
              Entidade.Emails[i].NFSe      := 'Não';
              Entidade.Emails[i].Descricao := '';
              Entidade.Emails[i].Url       := '';
              Inc(i); fdquerysql3.Next;
            end;
          end;
          Clipboard.AsText := Entidade.ToJSON.Format(2);
          TFile.WriteAllText('c:\temp\dump_entidade_enviada.json', Entidade.ToJSON.Format(2));
          {SetLength(Entidade.Enderecos, 0);
          SetLength(Entidade.Contatos, 0);
          SetLength(Entidade.Vendedores, 0);
          SetLength(Entidade.Documentos, 0);  }
          // Verifica se o usuario alvo ja esta configurado em memoria (frmprincipal.usucod_apolo).
          // Caso nao esteja, busca no banco pelo codigo do usuario logado; se tambem nao houver
          // registro no banco, solicita ao usuario o Usuario Alvo e a Senha Alvo (mascarada),
          // criptografa a senha com a chave 35, grava no usuario correspondente e alimenta
          // frmprincipal.usucod_apolo / frmprincipal.senha_alvo.
          {frmprincipal.token_alvo := 'bwSqK1/9aFZw/Z5wM1xJWZtQ2W++bjMa+Q3NuTaBgmV2nsMscAocgAzqJxwBEbijLasbEeX9YOzZwviyfhpla9NRsSrDi9v6hAdUqQTYufcSW5TY7u9Y9kjYfJvlTwYKH9nlvUuyBIeIfx6MGPYLYdl4/bb4B6tVv5aGNSgCs4vTKmtpp7CeDgHByZg3iV6cxwbBNHaB5Q6S9DWGg6Jd+nu';
          frmprincipal.token_alvo:= frmprincipal.token_alvo+'/j8lbLQav9ZvkqUIsESt6aLhpexqQrGGd/gQqhENd/X8Dq6lG68jdzfm9LV5uKgPSjNb1G1Yz0OzkM6lvjH0VYa3XOG/CpcLJxncY17c1rnw58CkTKpb3FsUrFjQgupoiQ4gOd4EavxIouxbEM3tLKaZPV6iMbALGPNC9pY1SyNgNmFD5M3t+V9B2/85+lV';
          frmprincipal.token_alvo:= frmprincipal.token_alvo+'/neXdfIg94i8zk+5I5uml3WHwBmR4g9D/yE/kxno7UMh9JFu44aWZIZjca4plkYle5pI3Oc6sedTzziat1L4xZ8VHrJl/9nyaQQU0GjXFjxOcZBUTTyU0=';}
          frmprincipal.token_alvo:='xo35ohxpaf5rXlU7d34YBFpAkZ5OFci+QFLlAbG4rO42Ew4S/RhGmhNmL3WJm1ImO+jgdkKB7K7mxVWKUdEaV72bO7JlLmBJUpD7tCa3S+/D12+7NNLog6EfraFlDGq34ag4oaFYBIRvgWoklHeJ4Vw/SLNLNYvZYmG31y5+MTUBk4Rfcfkytj60LEral+gdatIKfiuVn1KJzYdGQhLVMO6MBZ+Wm2tv7Iyc0GSvzfsZdU/x28QUSlmS';
          frmprincipal.token_alvo:=frmprincipal.token_alvo+'tZ1IHV3dROKe7pPkR+cTo/j6FK8ZZ7OPRDSGLL4U8Er/E6sacRXCniYfOjSVDWyt3KJfGpkYOyNpx870eNLDzemKkkDYatbxglzgdkdMOBv+rDqVfrR9+2RM5mPfxQOZ592JVD1+CnpdMrRsm8Hfy8WoqjHAdCi1fDXkAtNGdWneL2VOdltIT0SkrgYtb0BFbAamaBBmGwE0o680Nwvrd/vsxlYHwHnYO';
          frmprincipal.token_alvo:=frmprincipal.token_alvo+'129kWou56+aFCnXa4k5+lnEcuJe/x2BiZskDA2MlUYuaz8mgxga/rh7X+30y86OZyhH3Qe56FApUFcb6W7lGImf4zrc7LWRyV685htk';
          if Trim(frmprincipal.usucod_apolo) = '' then
          begin
            fdquerysql3.Close;
            fdquerysql3.SQL.Clear;
            fdquerysql3.SQL.Text :='SELECT usucod_apolo, senha_alvo FROM USER_geoapolo_usuarios WHERE usucod = :codigousuario';
            fdquerysql3.ParamByName('codigousuario').AsString := frmlogon.codigousuario;

            if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) and
               (Trim(fdquerysql3.FieldByName('usucod_apolo').AsString) <> '') and
               (Trim(fdquerysql3.FieldByName('senha_alvo').AsString) <> '') then
              begin
                { Ja cadastrado no banco - apenas carrega em memoria }
                frmprincipal.usucod_apolo := fdquerysql3.FieldByName('usucod_apolo').AsString;
                frmprincipal.senha_alvo   := fdquerysql3.FieldByName('senha_alvo').AsString;
              end
            else
            begin
              { Nao cadastrado - solicita ao usuario }
              vusucodapolo := UpperCase(InputBox('Usuário Alvo',
                'Informe o usuário de acesso ao Alvo:', ''));
              if Trim(vusucodapolo) = '' then
              begin
                messagedlg('Operação cancelada. Usuário alvo não foi informado.',
                  mtwarning, [mbok], 0);
                Exit;
              end;

              if not SolicitarSenhaMascarada('Senha do Usuário Alvo',
                   'Informe a senha do usuário alvo (' + vusucodapolo + '):',
                   vsenhaalvoplano) then
              begin
                messagedlg('Operação cancelada. Senha alvo não foi informada.',
                  mtwarning, [mbok], 0);
                Exit;
              end;
              vsenhaalvocriptografada := criptografia(35, vsenhaalvoplano);
              fdquerysql3.Close; fdquerysql3.SQL.Clear;
              fdquerysql3.SQL.Text :=
                'UPDATE USER_geoapolo_usuarios SET usucod_apolo = :usucodapolo, ' +
                'senha_alvo = :senhaalvo WHERE usucod = :codigousuario';
              fdquerysql3.ParamByName('usucodapolo').AsString   := vusucodapolo;
              fdquerysql3.ParamByName('senhaalvo').AsString     := vsenhaalvocriptografada;
              fdquerysql3.ParamByName('codigousuario').AsString := frmlogon.codigousuario;

              if not executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
              begin
                messagedlg('Erro ao salvar os dados do usuário alvo!', mterror, [mbok], 0);
                Exit;
              end;

              frmprincipal.usucod_apolo := vusucodapolo;
              frmprincipal.senha_alvo   := vsenhaalvocriptografada;
            end;
          end;
          panel2.Visible := True; panel2.Top := 85; panel2.Left := 24; panel2.Refresh;
          API := TAlvoAPI.Create('https://alvo.rccbrasil.org.br/api/');
          try
            if frmprincipal.token_alvo = '' then
                begin
                  senhaalvo:=funcoes.decriptografia(35,frmprincipal.senha_alvo, frmprincipal.senhaapp);
                  if not API.Login(frmprincipal.usucod_apolo, senhaalvo )then
                  begin
                    messagedlg('Falha ao autenticar no Alvo!', mterror, [mbok], 0);
                    Exit;
                  end;
                  //frmprincipal.token_alvo := API.Token;
                end
            else
              API.Token := frmprincipal.token_alvo;

            if API.InserirAlterarEntidade(Entidade, vMensagem) then
                begin
                  showmessage(vmensagem);
                  messagedlg('Entidade exportada com sucesso!' + #13 + vMensagem, mtinformation, [mbok], 0);
                  fdquerysql3.Close; fdquerysql3.SQL.Clear;
                  fdquerysql3.SQL.Text :=
                    'UPDATE USER_geoapolo_entidade SET entcod = :entcod WHERE geoentcod = :geoentcod';
                  fdquerysql3.ParamByName('entcod').AsString    := ventcod;
                  fdquerysql3.ParamByName('geoentcod').AsString := vgeoentcod;
                  executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);
                end
            else
              TFile.WriteAllText('c:\temp\dump_erro_export.json', vMensagem);
              messagedlg('Erro ao exportar: ' + #13 + vMensagem, mterror, [mbok], 0);
          finally
            API.Free;
            panel2.Visible := False;
          end;
        end;
      end;
    end
    else if (cbobuscabanco.Text = 'GeoApolo') and
            (fdqueryentidade.FieldByName('entobserevacoes').AsString <> '') then
    begin
      messagedlg('EXISTEM OBSERVAÇÕES QUE PRECISAM SER MODERADAS, DÊ DUPLO CLICK NA ENTIDADE E VERIFIQUE O CAMPO !!!',
                 mterror, [mbok], 0);
      Exit;
    end
    else if cbobuscabanco.Text = 'Alvo' then
    begin
      messagedlg('VOCÊ ESTÁ NA BASE ALVO E NÃO SERÁ PERMITIDA A EXPORTAÇÃO DA ENTIDADE !!!',
                 mterror, [mbok], 0);
      Exit;
    end;
  end;
end;

// =============================================================================
// consumirapi
// =============================================================================
function consumirapi(url: string): string;
var
  IdHTTP1   : TIdHTTP;
  SSLHandler: TIdSSLIOHandlerSocketOpenSSL;
begin
  IdHTTP1    := TIdHTTP.Create(nil);
  SSLHandler := TIdSSLIOHandlerSocketOpenSSL.Create(nil);
  try
    SSLHandler.SSLOptions.Method := sslvTLSv1_2;
    SSLHandler.SSLOptions.Mode   := sslmClient;
    IdHTTP1.IOHandler        := SSLHandler;
    IdHTTP1.HandleRedirects  := True;
    Result := IdHTTP1.Get(url);
    ShowMessage(Result);
  finally
    IdHTTP1.Free;
    SSLHandler.Free;
  end;
end;

procedure Tfrmentidades.spbsairClick(Sender: TObject);
begin
  Close;
  frmprincipal.Show;
end;

// =============================================================================
// spbsobrepoealvoClick — monta o JSON de sobreposição para a API Alvo/Riosoft
// Padronizado conforme o JSON modelo de resposta de Entidade/RetrieveDataSetPage:
//   - Nomes de campo em PascalCase iguais aos retornados pela API (sem espaços,
//     sem abreviações inventadas)
//   - Telefones e Endereços residem em EntFoneChildList / EnderEntChildList,
//     DENTRO de "Entidade1Object" (não no nível raiz da entidade)
//   - Categorias residem em EntCategChildList, também dentro de Entidade1Object
// =============================================================================
procedure Tfrmentidades.spbsobrepoealvoClick(Sender: TObject);
var
  i, b: integer;
  JsonObj, JsonEntidade, Entidade1Obj: TJSONObject;
  TelefonesArray, EnderecosArray, CategoriasArray: TJSONArray;
  TelefoneObj, CategoriaObj, EnderecoObj: TJSONObject;
  Campo, Valor, cepvalor: string;
  Entrada, ddd, numero, numerolimpo: string;
  partes, telefones1, categorias1: TArray<string>;
begin
  resp := messagedlg('Confirma a sobreposição destes dados, sobre os que estão no sistema Alvo ? (Y/N)',
                     mtconfirmation, [mbyes, mbno], 0);
  if resp <> idyes then
    Exit;

  cepvalor := '';

  JsonObj        := TJSONObject.Create;
  JsonEntidade   := TJSONObject.Create;
  Entidade1Obj   := TJSONObject.Create;
  CategoriasArray := TJSONArray.Create;
  TelefonesArray  := TJSONArray.Create;
  EnderecosArray  := TJSONArray.Create;
  try
    JsonObj.AddPair('Operacao', 'A');

    // Natureza é sempre fixa neste fluxo (não depende do grid de comparação)
    JsonEntidade.AddPair('Natureza', 'Consumidor');

    for i := 1 to StringGrid1.RowCount - 1 do
    begin
      Campo := ''; Valor := '';

      if SameText(StringGrid1.Cells[4, i], 'Sim') then
      begin
        Campo := StringGrid1.Cells[2, i];
        Valor := StringGrid1.Cells[1, i];
      end
      else if SameText(StringGrid1.Cells[4, i], 'Não') then
      begin
        Campo := StringGrid1.Cells[2, i];
        Valor := StringGrid1.Cells[3, i];
      end;

      if Campo = '' then
        Continue;

      if UpperCase(Campo) = 'ENTCOD' then
        JsonEntidade.AddPair('Codigo', Valor)

      else if UpperCase(Campo) = 'ENTCODALT' then
        JsonEntidade.AddPair('CodigoAlternativo', Valor)

      else if UpperCase(Campo) = 'TIPOTRATCOD' then
        JsonEntidade.AddPair('CodigoTipoTratamento', Valor)

      else if UpperCase(Campo) = 'ENTNOME' then
        JsonEntidade.AddPair('Nome', Valor)

      else if UpperCase(Campo) = 'ENTNOMEFANT' then
        JsonEntidade.AddPair('NomeFantasia', Valor)

      else if UpperCase(Campo) = 'ENTLOGRAD' then
        JsonEntidade.AddPair('CodigoTipoLograd', Valor)

      else if UpperCase(Campo) = 'ENTENDER' then
        JsonEntidade.AddPair('Endereco', Valor)

      else if UpperCase(Campo) = 'ENTENDERNO' then
        JsonEntidade.AddPair('NumeroEndereco', Valor)

      else if UpperCase(Campo) = 'ENTENDERCOMPL' then
        JsonEntidade.AddPair('ComplementoEndereco', Valor)

      else if UpperCase(Campo) = 'ENTBAIR' then
        JsonEntidade.AddPair('Bairro', Valor)

      else if UpperCase(Campo) = 'CIDCOD' then
        JsonEntidade.AddPair('CodigoCidade', Valor)

      else if UpperCase(Campo) = 'CEP' then
      begin
        cepvalor := Valor;
        JsonEntidade.AddPair('Cep', Valor);
      end

      else if UpperCase(Campo) = 'ENTTIPOFJ' then
      begin
        // Modelo espera "Física" / "Jurídica" por extenso, não a sigla F/J
        if UpperCase(Valor) = 'F' then
          JsonEntidade.AddPair('Tipo', 'Física')
        else if UpperCase(Valor) = 'J' then
          JsonEntidade.AddPair('Tipo', 'Jurídica')
        else
          JsonEntidade.AddPair('Tipo', Valor);
      end

      else if UpperCase(Campo) = 'ENTCPFCGC' then
        JsonEntidade.AddPair('CPFCNPJ', Valor)

      else if UpperCase(Campo) = 'RGIE' then
        JsonEntidade.AddPair('RGIE', Valor)

      else if UpperCase(Campo) = 'ENTRGORDEXPED' then
        JsonEntidade.AddPair('OrgaoExpedidor', Valor)

      else if UpperCase(Campo) = 'ENTGENERO' then
        JsonEntidade.AddPair('Genero', Valor)

      else if UpperCase(Campo) = 'ENTREGCODESTR' then
        JsonEntidade.AddPair('CodigoRegiao', Valor)

      else if UpperCase(Campo) = 'ENTSTATDESCR' then
        JsonEntidade.AddPair('StatusEntidade', Valor)

      else if UpperCase(Campo) = 'ENTDATAANIVFUND' then
        JsonEntidade.AddPair('DataFundacao', Valor)

      else if (UpperCase(Campo) = 'GEOCATEGCODESTR') or (UpperCase(Campo) = 'CATEGCODESTR') then
      begin
        categorias1 := Valor.Split([',']);
        for b := 0 to High(categorias1) do
        begin
          categorias1[b] := Trim(categorias1[b]);
          if categorias1[b] = '' then
            Continue;
          CategoriaObj := TJSONObject.Create;
          CategoriaObj.AddPair('Operacao', 'I');
          CategoriaObj.AddPair('Sequencia', TJSONNumber.Create(CategoriasArray.Count + 1));
          CategoriaObj.AddPair('CodigoCategoria', categorias1[b]);
          CategoriaObj.AddPair('AtivaTabelaPreco', 'Sim');
          CategoriasArray.AddElement(CategoriaObj);
        end;
      end

      else if Campo.StartsWith('Telefone') then
      begin
        Entrada    := Valor;
        telefones1 := Entrada.Split([',']);
        for b := 0 to High(telefones1) do
        begin
          telefones1[b] := Trim(telefones1[b]);
          if telefones1[b] = '' then
            Continue;
          ddd := ''; numero := '';
          partes := telefones1[b].Split(['-']);
          if Length(partes) = 2 then
          begin
            ddd    := Trim(partes[0]);
            numero := Trim(partes[1]);
          end
          else
            numero := telefones1[b];

          numerolimpo := StringReplace(numero, '-', '', [rfReplaceAll]);

          TelefoneObj := TJSONObject.Create;
          TelefoneObj.AddPair('Operacao', 'I');
          TelefoneObj.AddPair('Sequencia', TJSONNumber.Create(TelefonesArray.Count + 1));
          TelefoneObj.AddPair('DDI', '+55');
          TelefoneObj.AddPair('DDD', ddd);
          TelefoneObj.AddPair('Numero', numerolimpo);
          if b <= 1 then
          begin
            TelefoneObj.AddPair('Tipo', 'Residencial');
            TelefoneObj.AddPair('TelefonePrincipal', 'Sim');
          end
          else
          begin
            TelefoneObj.AddPair('Tipo', 'Celular');
            TelefoneObj.AddPair('TelefonePrincipal', 'Não');
          end;
          TelefonesArray.AddElement(TelefoneObj);
        end;
      end

      else if Campo.StartsWith('entender') then
      begin
        EnderecoObj := TJSONObject.Create;
        EnderecoObj.AddPair('Operacao', 'I');
        EnderecoObj.AddPair('Sequencia', TJSONNumber.Create(EnderecosArray.Count + 1));
        EnderecoObj.AddPair('Cep', cepvalor);
        EnderecoObj.AddPair('Endereco', Valor);
        EnderecoObj.AddPair('Numero', '0');
        EnderecoObj.AddPair('Complemento', '');
        EnderecoObj.AddPair('Bairro', '');
        EnderecoObj.AddPair('EnderecoEntrega', 'Sim');
        EnderecoObj.AddPair('EnderecoCobranca', 'Não');
        EnderecoObj.AddPair('EnderecoColeta', 'Não');
        EnderecoObj.AddPair('NomeContato', '');
        EnderecosArray.AddElement(EnderecoObj);
      end;
    end;

    // Arrays filhos ficam dentro de "Entidade1Object", conforme o modelo
    if TelefonesArray.Count > 0 then
      Entidade1Obj.AddPair('EntFoneChildList', TelefonesArray)
    else
      TelefonesArray.Free;

    if EnderecosArray.Count > 0 then
      Entidade1Obj.AddPair('EnderEntChildList', EnderecosArray)
    else
      EnderecosArray.Free;

    if CategoriasArray.Count > 0 then
      Entidade1Obj.AddPair('EntCategChildList', CategoriasArray)
    else
      CategoriasArray.Free;

    if Entidade1Obj.Count > 0 then
      JsonEntidade.AddPair('Entidade1Object', Entidade1Obj)
    else
      Entidade1Obj.Free;

    JsonObj.AddPair('Entidade', JsonEntidade);
    TFile.WriteAllText('c:\temp\dump.json', JsonObj.Format(55));
    panel2.Visible := False; panel2.Top := 300; panel2.Left := 24; panel2.Refresh;
  finally
    JsonObj.Free;
  end;
end;

// =============================================================================
// StringGrid1DrawCell
// =============================================================================
procedure Tfrmentidades.StringGrid1DrawCell(Sender: TObject; ACol, ARow: Integer;
  Rect: TRect; State: TGridDrawState);
var
  CellText : string;
  CellColor: TColor;
  TextRect_: TRect;
begin
  CellText := StringGrid1.Cells[ACol, ARow];

  if ARow = 0 then
  begin
    StringGrid1.Canvas.Brush.Color := $00DCDCDC;
    StringGrid1.Canvas.Font.Style  := [fsBold];
    StringGrid1.Canvas.Font.Size   := 10;
    StringGrid1.Canvas.Font.Color  := clBlack;
    StringGrid1.Canvas.FillRect(Rect);
    TextRect_ := Rect;
    InflateRect(TextRect_, -4, 0);
    DrawText(StringGrid1.Canvas.Handle, PChar(CellText), Length(CellText),
             TextRect_, DT_VCENTER or DT_SINGLELINE or DT_LEFT);
    Exit;
  end;

  if (ARow - 1) >= GTotalDiferentes then
  begin
    StringGrid1.Canvas.Brush.Color := clWindow;
    StringGrid1.Canvas.FillRect(Rect);
    Exit;
  end;

  StringGrid1.Canvas.Font.Style := [];
  StringGrid1.Canvas.Font.Size  := 10;
  StringGrid1.Canvas.Font.Color := clBlack;

  case GDecisoes[ARow - 1] of
    dlNenhuma   : CellColor := $00FFF3CD;
    dlManterSVE : CellColor := $00D4EDDA;
    dlManterAlvo: CellColor := $00CCE5FF;
  end;

  if ACol = 3 then
    case GDecisoes[ARow - 1] of
      dlNenhuma   : CellColor := $00FFE69C;
      dlManterSVE : CellColor := $00A8D5B5;
      dlManterAlvo: CellColor := $009FCCEE;
    end;

  if ACol = 0 then
    StringGrid1.Canvas.Font.Style := [fsItalic];

  StringGrid1.Canvas.Brush.Color := CellColor;
  StringGrid1.Canvas.FillRect(Rect);
  TextRect_ := Rect;
  InflateRect(TextRect_, -4, 0);
  DrawText(StringGrid1.Canvas.Handle, PChar(CellText), Length(CellText),
           TextRect_, DT_VCENTER or DT_SINGLELINE or DT_LEFT);
end;

// =============================================================================
// StringGrid1SelectCell
// =============================================================================
procedure Tfrmentidades.StringGrid1SelectCell(Sender: TObject; ACol, ARow: Integer;
  var CanSelect: Boolean);
var
  Pendentes, i: Integer;
begin
  if (ARow < 1) or not (ACol in [1, 2]) then Exit;
  if (ARow - 1) >= GTotalDiferentes then Exit;

  if ACol = 1 then
  begin
    GDecisoes[ARow - 1] := dlManterSVE;
    StringGrid1.Cells[3, ARow] := '◀ Usar SVE';
  end
  else
  begin
    GDecisoes[ARow - 1] := dlManterAlvo;
    StringGrid1.Cells[3, ARow] := 'Manter Alvo ▶';
  end;

  Pendentes := 0;
  for i := 0 to GTotalDiferentes - 1 do
    if GDecisoes[i] = dlNenhuma then Inc(Pendentes);

  if Pendentes = 0 then
  begin
    lblmensagemgeoapolo.Caption    := Format('✔ %d diferença(s) — todas decididas. Clique em Aplicar.',
                                             [GTotalDiferentes]);
    lblmensagemgeoapolo.Font.Color := clGreen;
    spbatualizaentidadeapolo.Enabled := True;
  end
  else
  begin
    lblmensagemgeoapolo.Caption    := Format('⚠ %d diferença(s) — %d pendente(s)',
                                             [GTotalDiferentes, Pendentes]);
    lblmensagemgeoapolo.Font.Color := clRed;
    spbatualizaentidadeapolo.Enabled := False;
  end;
  StringGrid1.Repaint;
end;

procedure Tfrmentidades.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  Action := caFree;
end;

procedure Tfrmentidades.FormKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  if Key = VK_F10 then spbsair.Click;
end;

// =============================================================================
// FormShow
// =============================================================================
procedure Tfrmentidades.FormShow(Sender: TObject);
begin
  with modulo_dados do
  begin
    try
      integraentidadeapolo := verifica_integracao_entidades(frmprincipal.codigo_empresa);
      if ((integraentidadeapolo = 'Não Integra') or (integraentidadeapolo = 'Mescla')) and
         (cbobuscabanco.Text = 'GeoApolo') then
      begin
        carrega_lista_entidades('GeoApolo', 'Consulta', '');
        ConfigurarGridCompleto('GeoApolo');
      end
      else if ((integraentidadeapolo = 'Integra') or (integraentidadeapolo = 'Mescla')) and
              (cbobuscabanco.Text = 'Alvo') then
        cbobuscabanco.Items.Add('Alvo');

      StatusBar1.Panels[1].Text := configura_statusbar('s');
      StatusBar1.Panels[3].Text := configura_statusbar('s');
      StatusBar1.Panels[5].Text := frmprincipal.nomeserversql;
    except
      on E: Exception do
        ShowMessage('Erro ao inicializar formulário: ' + E.Message);
    end;
  end;
end;

// =============================================================================
// mnugravaconfiguracoesClick
// =============================================================================
procedure Tfrmentidades.mnugravaconfiguracoesClick(Sender: TObject);
begin
  if cbobuscabanco.Text = 'Alvo' then
  begin
    grava_configuracoes_grids(frmentidades, 'entidades_apolo', gridentidades,
      'gridentidades', frmlogon.nomeusuario, modulo_dados.dtsfdqueryentidade);
    grava_config_telabusca('entidades_apolo', cbocampo.Text, cbordem.Text,
      Copy(Trim(vordem), 1, 1), frmentidades);
  end
  else if cbobuscabanco.Text = 'GeoApolo' then
  begin
    grava_configuracoes_grids(frmentidades, 'entidades_geoapolo', gridentidades,
      'gridentidades', frmlogon.nomeusuario, modulo_dados.dtsfdqueryentidade);
    grava_config_telabusca('entidades_geoapolo', cbocampo.Text, cbordem.Text,
      Copy(Trim(vordem), 1, 1), frmentidades);
  end;
end;

procedure Tfrmentidades.rdgcrescenteClick(Sender: TObject);
begin
  if rdgcrescente.Checked then
  begin
    vordem := ' ASC';
    rdgdecrescente.Checked := False;
  end;
end;

procedure Tfrmentidades.rdgdecrescenteClick(Sender: TObject);
begin
  if rdgdecrescente.Checked then
  begin
    vordem := ' DESC';
    rdgcrescente.Checked := False;
    rdgcrescente.Refresh;
  end;
end;

// =============================================================================
// carrega_lista_entidades — VERSÃO CORRIGIDA
//
// CORREÇÕES APLICADAS:
//   FIX 1: FetchOptions configurado para busca sob demanda (fmOnDemand)
//   FIX 2: CommandTimeout = 180 para esta query pesada
//   FIX 3: Campo padrão 'entnome' quando cbocampo está vazio
//   FIX 4: AG_BANCARIA com WITH(NOLOCK) — estava sem hint
//   FIX 5: ENT_CATEG e CATEGORIA com WITH(NOLOCK) dentro do OUTER APPLY
//   FIX 6: USER_geoapolo_entcateg e USER_geoapolo_categoria com WITH(NOLOCK)
//   FIX 7: Verificação da view com try/finally + IsEmpty (não usa executaracao)
//   FIX 8: Parâmetro :procurarpor só atribuído quando realmente existe na query
// =============================================================================
function carrega_lista_entidades(basededados: string; tipo_pesquisa: string; filtro: string): string;
var
  sqlview: string;
  i: integer;
  vCampoBusca: string;
begin
  with frmentidades, modulo_dados do
  begin
    if FCarregandoEntidades then Exit;
    FCarregandoEntidades := True;
    try
      if rdgcrescente.Checked then
      begin
        vordem := ' ASC';
        rdgdecrescente.Checked := False;
      end
      else if rdgdecrescente.Checked then
      begin
        vordem := ' DESC';
        rdgcrescente.Checked := False;
      end;

      // Fecha dataset antes de qualquer operação para liberar locks
      if fdqueryentidade.Active then
        fdqueryentidade.Close;

      // FIX 1: busca sob demanda — não carrega tudo antes de exibir
      fdqueryentidade.FetchOptions.Mode       := fmOnDemand;
      fdqueryentidade.FetchOptions.RowsetSize := 50;
      fdqueryentidade.FetchOptions.RecsMax    := -1;

      // FIX 2: timeout maior para queries pesadas
      //fdqueryentidade.CommandTimeout := 180;
      fdbanco.Params.Values['CommandTimeout'] := '360';

      // FIX 3: campo padrão quando cbocampo está vazio
      if Trim(cbocampo.Text) = '' then
        vCampoBusca := 'entnome'
      else
        vCampoBusca := cbocampo.Text;

      // ===================================================================
      // BASE ALVO
      // ===================================================================
      if ((frmentidades.integraentidadeapolo = 'Integra') or (frmentidades.integraentidadeapolo = 'Mescla')) and  (cbobuscabanco.Text = 'Alvo') then
      begin
        if tipo_pesquisa = 'Consulta' then
        begin
          // Definição da view — usada apenas para (re)criação se necessário
          sqlview :=
            'SELECT e.entcod, e.tipotratcod, e.entnome, e.EntNomeFant, e.EntDesdeData, e.EntDataCad,' +
            ' e.EntLograd, e.entender, e.entenderno, e.entbair, e.entendercomp,' +
            ' cid.cidcod, cid.cidnomecomp, cid.ufsigla, e.EntCep, e.EntTipoFJ, e.EntCxaPost,' +
            ' e.RegCodEstr, r.regnome, e.EntConceito, e.EntDataAnivFund, e.CargoCodEstr, car.cargonome,' +
            ' e.EntGenero, e.EntLocCobrancaOMesmo, e.EntLocEntregaOMesmo, e.EntEstCivil,' +
            ' e.EntNomePai, e.EntNomeMae, e.EntPossuiFilho, e.EntMoraCom,' +
            ' e.EntGrauEscol, e.AtivEconCodEstr, ae.ativeconnome, e.OrigCodEstr, o.orignome,' +
            ' categorias_alvo.categcodestr, categorias_alvo.categorias as CategNome,' +
            ' e.TipoCobCod, tc.tipocobnome, e.bconum, bco.bconome,' +
            ' e.AgNum, ag.AgNome as AgNome, e.EntBcoAgCCorNum,' +
            ' ue.USERDia_Debito_CC, ue.USERGeraCarne, ue.USERDiocese_id,' +
            ' ue.USERNomeDiocese, ue.USERrecebelembretedoacao,' +
            ' e1.entvalcontrib as USERValor_Contribuicao,' +
            ' e.EntCpfCgc, e.EntRgIe, e.entendernopi, ue.UserFalecido,' +
            ' uge.geoobservacoes as Entobservacoes,' +
            ' uge.geoentcod, uge.atualizou_apolo, uge.usucod_atualizou_apolo, e.enttransporteomesmo' +
            ' FROM entidade e WITH(NOLOCK)' +
            ' INNER JOIN entidade1 e1 WITH(NOLOCK) ON e.entcod = e1.entcod' +
            ' INNER JOIN cidade cid WITH(NOLOCK) ON e.cidcod = cid.cidcod' +
            ' LEFT JOIN REGIAO reg WITH(NOLOCK) ON e.RegCodEstr = reg.RegCodEstr' +
            ' LEFT JOIN cargo car WITH(NOLOCK) ON e.CargoCodEstr = car.CargoCodEstr' +
            ' LEFT JOIN origem o WITH(NOLOCK) ON e.OrigCodEstr = o.OrigCodEstr' +
            ' LEFT JOIN ativ_economica ae WITH(NOLOCK) ON e.ativeconcodestr = ae.ativeconcodestr' +
            // FIX 5: WITH(NOLOCK) dentro do OUTER APPLY
            ' OUTER APPLY (' +
            '   SELECT STRING_AGG(cat.categnome, ' + QuotedStr(',') + ') AS categorias,' +
            '          STRING_AGG(ec.categcodestr, ' + QuotedStr(',') + ') AS categcodestr' +
            '   FROM ENT_CATEG ec WITH(NOLOCK)' +
            '   INNER JOIN CATEGORIA cat WITH(NOLOCK) ON ec.categcodestr = cat.categcodestr' +
            '   WHERE ec.entcod = e.entcod' +
            ' ) as categorias_alvo' +
            ' LEFT JOIN tipo_cobranca tc WITH(NOLOCK) ON e.TipoCobCod = tc.TipoCobCod' +
            ' LEFT JOIN banco bco WITH(NOLOCK) ON e.bconum = bco.BcoNum' +
            // FIX 4: AG_BANCARIA com WITH(NOLOCK)
            ' LEFT JOIN AG_BANCARIA ag WITH(NOLOCK) ON e.agnum = ag.AgNum AND bco.bconum = ag.bconum' +
            ' INNER JOIN u_entidade ue WITH(NOLOCK) ON e.entcod = ue.EntCod' +
            ' LEFT JOIN user_geoapolo_entidade uge WITH(NOLOCK) ON e.entcod = uge.entcod' +
            ' LEFT JOIN regiao r WITH(NOLOCK) ON e.regcodestr = r.regcodestr';

          // FIX 7: verificação segura da view
          fdquerysql18.Close;
          fdquerysql18.sql.clear;
          fdquerysql18.sql.Text := 'SELECT name FROM sys.views WHERE name = :pview ';
          fdquerysql18.parambyname('pview').asstring :=  'entidades_apolo';

          try
            fdquerysql18.Open;
            if fdquerysql18.IsEmpty then
              cria_view(sqlview, 'entidades_apolo', 'Apolo', frmentidades);
          finally
            fdquerysql18.Close;
          end;

          // Consulta final usando a view
          sqlview :=
            'SELECT TOP 50 * FROM entidades_apolo e WITH(NOLOCK)' +
            ' WHERE e.' + vCampoBusca + ' LIKE :procurarpor' +
            ' AND SUBSTRING(e.categcodestr, 1, 2) IN (' + QuotedStr('02') + ', ' + QuotedStr('03') + ')' +
            ' ORDER BY e.entnome ASC';
        end
        else if tipo_pesquisa = 'Especifica' then
        begin
          if cbordem.Items.Count = 0 then
            cbordem.Items.Add('entnome');

          sqlview :=
            'SELECT * FROM entidades_apolo e WITH(NOLOCK)' +
            ' WHERE e.' + vCampoBusca + ' LIKE :procurarpor' +
            ' AND SUBSTRING(e.categcodestr, 1, 2) IN (' + QuotedStr('02') + ', ' + QuotedStr('03') + ')' +
            ' ORDER BY e.' + cbordem.Text;
          if rdgcrescente.Checked then sqlview := sqlview + ' ASC'
          else if rdgdecrescente.Checked then sqlview := sqlview + ' DESC';
        end;

        fdqueryentidade.SQL.Clear;
        fdqueryentidade.SQL.Text := sqlview;
        // FIX 8: parâmetro sempre presente nas queries do Alvo
        fdqueryentidade.ParamByName('procurarpor').AsString := '%' + lblprocurarpor.Text + '%';

        if executaracao(fdqueryentidade, fdbanco, True, dtsfdqueryentidade) then
        begin
          gridentidades.DataSource := dtsfdqueryentidade;
          cbocampo.Items.Clear; cbordem.Items.Clear;
          for i := 0 to fdqueryentidade.Fields.Count - 1 do
          begin
            cbocampo.Items.Add(fdqueryentidade.Fields[i].FieldName);
            cbordem.Items.Add(fdqueryentidade.Fields[i].FieldName);
          end;
          carrega_config('entidades_apolo', frmentidades, cbocampo, cbordem,
                         rdgcrescente, rdgdecrescente);
          funcoes.AjustaLarguraColunas(gridentidades);
          configura_grid('entidades_apolo', frmentidades, frmlogon.codigousuario,
                         'gridentidades', gridentidades, modulo_dados.dtsfdqueryentidade);
          lblnentidadeslistadas.Caption := IntToStr(fdqueryentidade.RecordCount);
          lblnentidadeslistadas.Refresh;
          cbobuscabanco.Refresh;
          gridentidades.Refresh;
        end;
        gridentidades.SetFocus;
      end

      // ===================================================================
      // BASE GEOAPOLO
      // ===================================================================
      else if ((frmentidades.integraentidadeapolo = 'Não Integra') or (frmentidades.integraentidadeapolo = 'Mescla')) and (cbobuscabanco.Text = 'GeoApolo') then
      begin
        sql :=
          'SELECT uge.entcod, uge.geotipotratcod as tipotratcod,' +
          ' uge.geoentnome as entnome, uge.geoentnomefantasia as entnomefant,' +
          ' uge.geoentdesdedata as EntDesdeData, uge.geoentdatacad as entdatacad,' +
          ' ugtl.tipologradabrev as entlograd,' +
          ' uge.geoentender as entender, uge.geoenderno as entenderno,' +
          ' uge.geoenderno as ententnopi, uge.geoentbair as entbair,' +
          ' uge.geoentendercomp as entendercomp, cid.geocidcod as cidcod,' +
          ' cid.cidnomecomp, cid.ufsigla, uge.geoentcep as entcep,' +
          ' uge.geotipofj as enttipofj, uge.geoentcxapost as entcxapost,' +
          ' uge.georegcodestr as regcodestr, ugrp.geo_regnome as regnome,' +
          ' uge.geoentconceito as entconceito, uge.geoentdataanivfund as entdataanivfund,' +
          ' uge.geocargocodestr as cargocodestr, car.geocargonome as cargonome,' +
          ' uge.geoentgenero as entgenero,' +
          ' uge.geoentloccobrancaomesmo as entloccobrancaomesmo,' +
          ' uge.geoentlocentregaomesmo as EntLocEntregaOMesmo,' +
          ' uge.geoenttransporteomesmo as EntTransporteOMesmo,' +
          ' uge.geoentestcivil as EntEstCivil,' +
          ' uge.geoentnomepai as EntNomePai, uge.geoentnomemae as EntNomeMae,' +
          ' uge.geoentpossuifilho as EntPossuiFilho, uge.geoentmoracom as EntMoraCom,' +
          ' ggrau.grau_escolaridade as EntGrauEscol,' +
          ' gae.AtivEconcodestr, ugate.ativeconnome,' +
          ' ugoe.geo_origcodestr as OrigCodEstr, ugo.geo_orignome as OrigNome,' +
          ' categorias_apolo.categcodestr as Categcodestr, categorias_apolo.categnome,' +
          ' uge.geotipocobcod as TipoCobCod, ugtc.geotipocobnome as TipoCobNome,' +
          ' uge.geobconum as bconum, ugb.geobconome as bconome,' +
          ' uge.geoagnum as agnum, ugab.geoagnome as AgNome,' +
          ' uge.geoconta as EntBcoAgCCorNum,' +
          ' uge.geodia_contribuicao as USERDia_Debito_CC,' +
          ' uge.geogerarcarne as USERgeraCarne,' +
          ' uge.geodioceseid as UserDiocese_id, udc.nome as USERNomeDiocese,' +
          ' uge.georecebelembrete as USERrecebelembretedoacao,' +
          ' uge.geovalorcontribuicao as USERValor_Contribuicao,' +
          ' MAX(CASE WHEN uged.geotipodocumento = ' + QuotedStr('CPF/CNPJ') +
          '   THEN uged.geonumerodocumento END) AS EntCpfCgc,' +
          ' MAX(CASE WHEN uged.geotipodocumento = ' + QuotedStr('RG/IE') +
          '   THEN uged.geonumerodocumento END) AS EntRgIe,' +
          ' uge.geoentcod, uge.geofalecido as USERFalecido,' +
          ' uge.geoobservacoes as Entobservacoes,' +
          ' uge.usucod_atualizou_apolo as atualizou_apolo' +
          ' FROM user_geoapolo_entidade uge WITH(NOLOCK)' +
          ' LEFT JOIN USER_geoapolo_tipologradouro ugtl WITH(NOLOCK) ON uge.tipolograd = ugtl.tipolograd' +
          ' INNER JOIN user_geoapolo_cidades cid WITH(NOLOCK) ON uge.geocidcod = cid.geoCidCod' +
          ' LEFT JOIN USER_geoapolo_cargos car WITH(NOLOCK) ON uge.geocargocodestr = car.geocargocodestr' +
          ' LEFT JOIN USER_geoapolo_grauescolaridade ggrau WITH(NOLOCK) ON uge.codigo_grauescolaridade = ggrau.codigo_grauescolaridade' +
          ' LEFT JOIN USER_geoapolo_entidade_ativecon gae WITH(NOLOCK) ON uge.geoentcod = gae.geoentcod' +
          ' LEFT JOIN USER_geoapolo_atividade_economica ugate WITH(NOLOCK) ON gae.ativeconcodestr = ugate.ativeconcodestr' +
          ' LEFT JOIN USER_geoapolo_origens_entidade ugoe WITH(NOLOCK) ON uge.geoentcod = ugoe.geoentcod' +
          ' INNER JOIN USER_geoapolo_origens ugo WITH(NOLOCK) ON ugoe.geo_origcodestr = ugo.geo_origcodestr' +
          // FIX 6: WITH(NOLOCK) dentro do OUTER APPLY GeoApolo
          ' OUTER APPLY (' +
          '   SELECT STRING_AGG(gcat.geocategnome, ' + QuotedStr(', ') + ') AS categnome,' +
          '          STRING_AGG(ugec.geocategcodestr, ' + QuotedStr(',') + ') AS categcodestr' +
          '   FROM USER_geoapolo_entcateg ugec WITH(NOLOCK)' +
          '   INNER JOIN USER_geoapolo_categoria gcat WITH(NOLOCK) ON ugec.geocategcodestr = gcat.geocategcodestr' +
          '   WHERE ugec.geoentcod = uge.geoentcod' +
          ' ) as categorias_apolo' +
          ' LEFT JOIN USER_geoapolo_tipo_cobranca ugtc WITH(NOLOCK) ON uge.geotipocobcod = ugtc.geotipocobcod' +
          ' LEFT JOIN USER_geoapolo_bancos ugb WITH(NOLOCK) ON uge.geobconum = ugb.geobconum' +
          ' LEFT JOIN USER_geoapolo_agbancaria ugab WITH(NOLOCK) ON uge.geoagnum = ugab.geoagnum AND ugab.geobconum = ugb.geobconum' +
          ' LEFT JOIN USERdioceses_CNBB udc WITH(NOLOCK) ON uge.geodioceseid = udc.id AND udc.estado_id = (SELECT uecnbb.USERiD FROM USEREstado_CNBB uecnbb WITH(NOLOCK) WHERE uecnbb.USERsigla = cid.ufsigla)' +
          ' LEFT JOIN USER_geoapolo_entidade_documentos uged WITH(NOLOCK) ON uge.geoentcod = uged.geoentcod' +
          ' LEFT JOIN USER_geoapolo_regiao_pais ugrp WITH(NOLOCK) ON uge.georegcodestr = ugrp.geo_regnome' +
          ' GROUP BY' +
          '   uge.entcod, uge.geotipotratcod, uge.geoentnome, uge.geoentnomefantasia,' +
          '   uge.geoentdesdedata, uge.geoentdatacad, ugtl.tipologradabrev,' +
          '   uge.geoentender, uge.geoenderno, uge.geoentbair, uge.geoentendercomp,' +
          '   cid.geocidcod, cid.cidnomecomp, cid.ufsigla, uge.geoentcep,' +
          '   uge.geotipofj, uge.geoentcxapost, uge.georegcodestr, uge.geoentconceito,' +
          '   uge.geoentdataanivfund, uge.geocargocodestr, car.geocargonome,' +
          '   uge.geoentgenero, uge.geoentloccobrancaomesmo, uge.geoentlocentregaomesmo,' +
          '   uge.geoenttransporteomesmo, uge.geoentestcivil, uge.geoentnomepai,' +
          '   uge.geoentnomemae, uge.geoentpossuifilho, uge.geoentmoracom,' +
          '   ggrau.grau_escolaridade, gae.ativeconcodestr, ugoe.geo_origcodestr,' +
          '   ugo.geo_orignome, categorias_apolo.categcodestr, categorias_apolo.categnome,' +
          '   uge.cidcodapolo, uge.geotipocobcod, ugtc.geotipocobnome,' +
          '   uge.geobconum, ugb.geobconome, uge.geoagnum, ugab.geoagnome,' +
          '   uge.geoconta, uge.geodia_contribuicao, uge.geogerarcarne,' +
          '   uge.geodioceseid, udc.nome, uge.georecebelembrete, uge.geovalorcontribuicao,' +
          '   uge.geoobservacoes, uge.tipolograd, uge.geoentcod, uge.geofalecido,' +
          '   uge.usucod_atualizou_apolo, ugate.ativeconnome, ugrp.geo_regnome';
        // FIX 7: verificação segura da view GeoApolo
        fdquerysql18.Close;
        fdquerysql8.sql.clear;
        fdquerysql18.SQL.Text := 'SELECT name FROM sys.views WHERE name = :nomedaview';
        fdquerysql18.parambyname('nomedaview').asstring := 'entidades_geoapolo';
        try
          if not executaracao(fdquerysql18, fdbanco, true, dtsfdquerysql18) then
            cria_view(sql, 'entidades_geoapolo', 'GeoApolo', frmentidades);
        finally
          fdquerysql18.Close;
        end;

        if tipo_pesquisa = 'Consulta' then
        begin
          if filtro = 'JAEXPORTADA' then
            begin
              sqlview :=
                'SELECT * FROM entidades_geoapolo e WITH(NOLOCK)' +
                ' INNER JOIN USER_geoapolo_entidade_documentos uged WITH(NOLOCK)' +
                '   ON e.entcpfcgc = uged.geonumerodocumento AND uged.geotipodocumento = ' + QuotedStr('CPF/CNPJ') +
                ' INNER JOIN user_geoapolo_entidade ue WITH(NOLOCK) ON e.entcpfcgc = ue.entcpfcgc' +
                ' WHERE ue.atualizou_apolo = ' + QuotedStr('S');
            end
          else
          begin
              sqlview :=
                'SELECT * FROM entidades_geoapolo e WITH(NOLOCK)' +
               ' INNER JOIN USER_geoapolo_entidade_documentos uged WITH(NOLOCK)' +
                '   ON e.entcpfcgc = uged.geonumerodocumento AND uged.geotipodocumento = ' + QuotedStr('CPF/CNPJ') +
                ' INNER JOIN user_geoapolo_entidade ue WITH(NOLOCK) ON e.geoentcod = ue.geoentcod' +
                ' WHERE ue.atualizou_apolo = ' + QuotedStr('N');
            end;
            sqlview := sqlview +
              ' ORDER BY CASE WHEN ue.atualizou_apolo = ' + QuotedStr('N') +
              ' AND e.Entobservacoes IS NULL THEN 0 ELSE 1 END';
          end
        else if tipo_pesquisa = 'Especifica' then
        begin
          if cbordem.Items.Count = 0 then
            begin
              cbordem.Items.Add('geoentnome');
              cbordem.ItemIndex := 0;
            end;
          sqlview :=
            'SELECT * FROM entidades_geoapolo e WITH(NOLOCK)' +
            ' INNER JOIN user_geoapolo_entidade ue WITH(NOLOCK) ON e.geoentcod = ue.geoentcod' +
            ' WHERE e.' + vCampoBusca + ' LIKE :procurarpor' +
            ' ORDER BY CASE WHEN ue.atualizou_apolo = ' + QuotedStr('N') +
            ' AND e.Entobservacoes IS NULL THEN 0 ELSE 1 END';
        end;

        fdqueryentidade.SQL.Clear;
        fdqueryentidade.SQL.Text := sqlview;

        // FIX 8: parâmetro só atribuído quando existe na query
        if tipo_pesquisa = 'Especifica' then
          fdqueryentidade.ParamByName('procurarpor').AsString := '%' + lblprocurarpor.Text + '%';

        if executaracao(fdqueryentidade, fdbanco, True, dtsfdqueryentidade) then
        begin
          dtsfdqueryentidade.DataSet := fdqueryentidade;
          gridentidades.DataSource   := dtsfdqueryentidade;
          cbocampo.Items.Clear; cbordem.Items.Clear;
          for i := 0 to fdqueryentidade.Fields.Count - 1 do
          begin
            cbocampo.Items.Add(fdqueryentidade.Fields[i].FieldName);
            cbordem.Items.Add(fdqueryentidade.Fields[i].FieldName);
          end;
          carrega_config('entidades_geoapolo', frmentidades, cbocampo, cbordem,
                         rdgcrescente, rdgdecrescente);
          funcoes.AjustaLarguraColunas(gridentidades);
          configura_grid('entidades_geoapolo', frmentidades, frmlogon.codigousuario,
                         'gridentidades', gridentidades, modulo_dados.dtsfdqueryentidade);
          lblnentidadeslistadas.Caption := IntToStr(fdqueryentidade.RecordCount);
          lblnentidadeslistadas.Refresh;
        end;
        gridentidades.Refresh;
        gridentidades.SetFocus;
      end;

    except
      on E: Exception do
      begin
        FCarregandoEntidades := False;
        ShowMessage('Erro ao carregar entidades: ' + E.Message);
        Exit;
      end;
    end;
    FCarregandoEntidades := False;
  end;
end;

// =============================================================================
// gridentidadesDblClick — CORRIGIDO: Show antes de preencher campos
// =============================================================================
procedure Tfrmentidades.gridentidadesDblClick(Sender: TObject);
var
  vrecebelembrete, vgeracarne, vestadocivil, vfalecido, ventgenero, vtipofj: string;
begin
  with modulo_dados do
  begin
    application.CreateForm(TfrmCadEntidade, frmcadentidade);
    frmcadentidade.controle := 'ALTERAÇÃO';
    // CORREÇÃO: Show ANTES de preencher campos para evitar
    // "Cannot focus an invisible window"
    frmcadentidade.Show;

    with frmcadentidade do
    begin
      if (fdqueryentidade.FieldByName('entcod').AsString = '') or (fdqueryentidade.FieldByName('entcod').IsNull) then
        lblentcod.Text := fdqueryentidade.FieldByName('geoentcod').AsString
      else
        lblentcod.Text := fdqueryentidade.FieldByName('entcod').AsString;

      cin1.ActivePageIndex := 0;
      lbltipotrat.Text         := fdqueryentidade.FieldByName('tipotratcod').AsString;
      lblentnome.Text          := fdqueryentidade.FieldByName('entnome').AsString;
      lblentnomefantasia.Text  := fdqueryentidade.FieldByName('entnomefant').AsString;
      mskcep.Text              := fdqueryentidade.FieldByName('entcep').AsString;
      lbllogradouro.Text       := fdqueryentidade.FieldByName('entlograd').AsString;
      lblentender.Text         := fdqueryentidade.FieldByName('entender').AsString;
      lblentenderno.Text       := fdqueryentidade.FieldByName('entenderno').AsString;
      lblentendercompl.Text    := fdqueryentidade.FieldByName('entendercomp').AsString;
      lblentbair.Text          := fdqueryentidade.FieldByName('entbair').AsString;
      lblcidcod.Text           := fdqueryentidade.FieldByName('cidcod').AsString;
      lblnomecidade.Caption    := fdqueryentidade.FieldByName('cidnomecomp').AsString;
      lbluf.Text               := fdqueryentidade.FieldByName('ufsigla').AsString;
      lblcaixapostal.Text      := fdqueryentidade.FieldByName('EntCxaPost').AsString;

      ventgenero := fdqueryentidade.FieldByName('entgenero').AsString;
      if ventgenero = 'M' then ventgenero := 'MASCULINO'
      else if ventgenero = 'F' then ventgenero := 'FEMININO'
      else if ventgenero = 'N' then ventgenero := 'NENHUM';
      buscanacombo(ventgenero, frmcadentidade, cbosexo);

      vfalecido := fdqueryentidade.FieldByName('USERFalecido').AsString;
      if vfalecido = 'N' then vfalecido := 'Não' else vfalecido := 'Sim';
      buscanacombo(vfalecido, frmcadentidade, cbofalecido);

      vtipofj := fdqueryentidade.FieldByName('enttipofj').AsString;
      buscanacombo(vtipofj, frmcadentidade, cbotipofj);

      vestadocivil := fdqueryentidade.FieldByName('entestcivil').AsString;
      buscanacombo(vestadocivil, frmcadentidade, cboestadocivil);

      mskdtnascimento.Text := fdqueryentidade.FieldByName('entdataanivfund').AsString;
      mskdtcadastro.Text   := fdqueryentidade.FieldByName('entdesdedata').AsString;

      if cboescolaridade.ItemIndex = -1 then carrega_combo_grauescolar;
      buscanacombo(fdqueryentidade.FieldByName('EntGrauEscol').AsString, frmcadentidade, cboescolaridade);

      lblcargocodestr.Text := fdqueryentidade.FieldByName('cargocodestr').AsString;
      lblnomecargo.Caption := fdqueryentidade.FieldByName('cargonome').AsString;

      cin1.ActivePageIndex := 1;
      cin2.ActivePageIndex := 0;
      lblnomedopai.Text := fdqueryentidade.FieldByName('entnomepai').AsString;
      lblnomedamae.Text := fdqueryentidade.FieldByName('entnomemae').AsString;
      lblresidecom.Text := fdqueryentidade.FieldByName('entmoracom').AsString;
      if fdqueryentidade.FieldByName('entpossuifilho').AsString = 'Sim' then
        rdgfilhos_sim.Checked := True
      else
        rdgfilhosnao.Checked := True;

      cin2.ActivePageIndex := 1;
      lbltipocobcod.Text          := fdqueryentidade.FieldByName('tipocobcod').AsString;
      lbltipocobnome.Caption      := fdqueryentidade.FieldByName('tipocobnome').AsString;
      lbltipocobnome.Refresh;
      lblbconum.Text              := fdqueryentidade.FieldByName('bconum').AsString;
      lblnomebanco.Caption        := fdqueryentidade.FieldByName('bconome').AsString;
      lblagnum.Text               := fdqueryentidade.FieldByName('agnum').AsString;
      lblnomeagencia.Caption      := fdqueryentidade.FieldByName('agnome').AsString;
      lblgeocontacorrente.Text    := fdqueryentidade.FieldByName('EntBcoAgCCorNum').AsString;
      lbldiadebitoautomatico.Text := fdqueryentidade.FieldByName('USERDia_Debito_CC').AsString;

      if fdqueryentidade.FieldByName('USERValor_Contribuicao').IsNull or
         (Trim(fdqueryentidade.FieldByName('USERValor_Contribuicao').AsString) = '') or
         (fdqueryentidade.FieldByName('USERValor_Contribuicao').AsString = '0') then
        lblvalorcontribuicao.Text := '25'
      else
        lblvalorcontribuicao.Text := fdqueryentidade.FieldByName('USERValor_Contribuicao').AsString;

      vgeracarne := fdqueryentidade.FieldByName('USERGeraCarne').AsString;
      buscanacombo(UpperCase(vgeracarne), frmcadentidade, cbogeracarne);
      lbldioceseid.Text      := fdqueryentidade.FieldByName('USERDiocese_id').AsString;
      lbldiocesenome.Caption := fdqueryentidade.FieldByName('USERNomeDiocese').AsString;
      vrecebelembrete := fdqueryentidade.FieldByName('USERRecebelembretedoacao').AsString;
      buscanacombo(UpperCase(vrecebelembrete), frmcadentidade, cborecebelembrete);

      cin2.ActivePageIndex := 2;
      lblativecodestr.Text               := fdqueryentidade.FieldByName('ativeconcodestr').AsString;
      lblnomeatividade_economica.Caption := fdqueryentidade.FieldByName('ativeconnome').AsString;
      lblorigcodestr.Text                := fdqueryentidade.FieldByName('origcodestr').AsString;
      lblnomeorigem.Caption              := fdqueryentidade.FieldByName('orignome').AsString;
      lblregiao.Text                     := fdqueryentidade.FieldByName('regcodestr').AsString;
      lblnomeregiao.Caption              := fdqueryentidade.FieldByName('regnome').AsString;
      lblconceito.Text                   := fdqueryentidade.FieldByName('entconceito').AsString;
      vgeoentcod := fdqueryentidade.FieldByName('geoentcod').AsString;

      cin1.ActivePageIndex := 3;
      lblentcontatocod.Text := '';
      carrega_tipologradouro_contato;

      mostra_telefones_entidade(lblentcod.Text, frmentidades.integraentidadeapolo);
      mostra_entidade_contatoweb(lblentcod.Text, frmentidades.integraentidadeapolo);
      mostra_entidade_categoria(lblentcod.Text, frmentidades.integraentidadeapolo);

      cin1.ActivePageIndex := 4;
      mostra_entidade_documentos(lblentcod.Text, frmentidades.integraentidadeapolo);

      memobservacoes.Lines.Clear;
      memobservacoes.Lines.Add(fdqueryentidade.FieldByName('Entobservacoes').AsString);
      tabobservacoes.Refresh;

      cin1.ActivePageIndex := 0;
      cin2.ActivePageIndex := 0;
    end;
  end;
end;

// =============================================================================
// atualiza_entcod_alvo_via_cpf
// =============================================================================
function atualiza_entcod_alvo_via_cpf(const vcodigogeoentidade: string): string;
var
  ventcodalvo: string;
begin
  Result := '';
  with frmentidades, modulo_dados do
  begin
    fdquerysql19.Close;
    fdquerysql19.SQL.Clear;
    fdquerysql19.SQL.Text :=
      'SELECT geonumerodocumento FROM USER_geoapolo_entidade_documentos' +
      ' WHERE geoentcod = :geoentcod AND geotipodocumento = :geotipodocumento';
    fdquerysql19.ParamByName('geoentcod').AsString       := vcodigogeoentidade;
    fdquerysql19.ParamByName('geotipodocumento').AsString := 'CPF/CNPJ';
    fdquerysql19.Open;
    if not fdquerysql19.IsEmpty then
    begin
      fdquerysql20.Close;
      fdquerysql20.SQL.Text := 'SELECT entcod FROM entidade_geoapolo WHERE entcpfcgc = :cpf';
      fdquerysql20.ParamByName('cpf').AsString := fdquerysql19.FieldByName('geonumerodocumento').AsString;
      fdquerysql20.Open;
      if not fdquerysql20.IsEmpty then
      begin
        ventcodalvo := fdquerysql20.FieldByName('entcod').AsString;
        fdquerysql3.Close;
        fdquerysql3.SQL.Text :=
          'UPDATE USER_geoapolo_entidade SET entcod = :entcod WHERE geoentcod = :geoentcod';
        fdquerysql3.ParamByName('entcod').AsString    := ventcodalvo;
        fdquerysql3.ParamByName('geoentcod').AsString := vcodigogeoentidade;
        fdquerysql3.ExecSQL;
        if fdquerysql3.RowsAffected > 0 then
          Result := ventcodalvo;
      end;
    end;
  end;
end;

// =============================================================================
// gridentidadesDrawColumnCell
// =============================================================================
procedure Tfrmentidades.gridentidadesDrawColumnCell(Sender: TObject;
  const Rect: TRect; DataCol: Integer; Column: TColumn; State: TGridDrawState);
begin
  with modulo_dados do
  begin
    if ((integraentidadeapolo = 'Não Integra') or (integraentidadeapolo = 'Mescla')) and
       (cbobuscabanco.Text = 'GeoApolo') then
    begin
      if (fdqueryentidade.FieldByName('entcod').AsString <> '') and
         (fdqueryentidade.FieldByName('atualizou_apolo').AsString = 'S') and
         (fdqueryentidade.FieldByName('usucod_atualizou_apolo').AsString <> '') then
      begin
        gridentidades.Canvas.Brush.Color := clYellow;
        gridentidades.Canvas.FillRect(Rect);
        gridentidades.DefaultDrawDataCell(Rect, Column.Field, State);
      end
      else if not fdqueryentidade.FieldByName('geoobservacoes').IsNull and
              (Trim(fdqueryentidade.FieldByName('geoobservacoes').AsString) <> '') then
      begin
        gridentidades.Canvas.Brush.Color := clRed;
        gridentidades.Canvas.FillRect(Rect);
        gridentidades.DefaultDrawDataCell(Rect, Column.Field, State);
      end;
    end;
  end;
end;

// =============================================================================
// importa_entidade — mantido igual ao original
// =============================================================================
function importa_entidade(integracao: string): string;
var
  tratalogradouro, entcodcontato: string;
  FormatSettings: TFormatSettings;
begin
  with modulo_dados, frmentidades, frmcadentidade do
  begin
    FormatSettings := TFormatSettings.Create;
    FormatSettings.DateSeparator   := '-';
    FormatSettings.ShortDateFormat := 'dd/mm/yyyy';

    if integracao = 'GeoApolo' then
    begin
      lblentcod.Text := fdqueryentidade.FieldByName('entcod').AsString;
      lbllogradouro.Clear; lbllogradouroentrega.Clear; lbllogradourocobranca.Clear;
      lbltipotrat.Text  := fdqueryentidade.FieldByName('tipotratcod').AsString;
      entcodapolo       := atualiza_entcod_alvo_via_cpf(lblentcod.Text);
      lblentnome.Text   := fdqueryentidade.FieldByName('entnome').AsString;
      lblentnomefantasia.Text := fdqueryentidade.FieldByName('entnomefant').AsString;
      logradouro := fdqueryentidade.FieldByName('entlograd').AsString;
      if logradouro <> '' then
        lbllogradouro.Text := logradouro
      else
      begin
        tratalogradouro := Copy(fdqueryentidade.FieldByName('entender').AsString, 1, 3);
        if tratalogradouro = 'RUA' then logradouro := 'R.'
        else if logradouro = 'AVE' then logradouro := 'Av.'
        else if logradouro = 'TRA' then logradouro := 'Tv.'
        else if logradouro = 'PRA' then logradouro := 'Pç.';
      end;
      lbllogradouro.Text      := logradouro;
      lblentender.Text        := fdqueryentidade.FieldByName('entender').AsString;
      lblentenderno.Text      := fdqueryentidade.FieldByName('entenderno').AsString;
      lblentendercompl.Text   := fdqueryentidade.FieldByName('EntEnderComp').AsString;
      lblentbair.Text         := fdqueryentidade.FieldByName('EntBair').AsString;
      mskcep.Text             := fdqueryentidade.FieldByName('Entcep').AsString;
      lblcidcod.Text          := fdqueryentidade.FieldByName('cidcod').AsString;
      retorna_cidade_estado(lblcidcod.Text, frmentidades.integraentidadeapolo);
      lblcaixapostal.Text     := fdqueryentidade.FieldByName('entcxapost').AsString;
      sexo := fdqueryentidade.FieldByName('EntGenero').AsString;
      if sexo = 'F' then
      begin
        if lbltipotrat.Text = '' then lbltipotrat.Text := 'Sra.';
        sexo := 'FEMININO';
      end
      else if sexo = 'M' then
      begin
        if lbltipotrat.Text = '' then lbltipotrat.Text := 'Sr.';
        sexo := 'MASCULINO';
      end;
      buscanacombo(sexo, frmcadentidade, cbosexo);
      buscanacombo(fdqueryentidade.FieldByName('EntTipoFJ').AsString, frmcadentidade, cbotipofj);
      buscanacombo(fdqueryentidade.FieldByName('EntEstCivil').AsString, frmcadentidade, cboestadocivil);
      falecido := fdqueryentidade.FieldByName('USERFalecido').AsString;
      if (falecido = 'Não') or (falecido = '') then falecido := 'Não' else falecido := 'Sim';
      buscanacombo(falecido, frmcadentidade, cbofalecido);
      carrega_combo_grauescolar;
      grauescolaridade := fdqueryentidade.FieldByName('EntGrauEscol').AsString;
      buscanacombo(grauescolaridade, frmcadentidade, cboescolaridade);
      lblcargocodestr.Text  := fdqueryentidade.FieldByName('cargocodestr').AsString;
      mskdtnascimento.EditMask := '';
      if (fdqueryentidade.FieldByName('entdataanivfund').AsString = '01/01/1970') or
         (fdqueryentidade.FieldByName('entdataanivfund').AsString = '') then
        mskdtnascimento.Text := '  /  /    '
      else
        mskdtnascimento.Text :=
          Copy(fdqueryentidade.FieldByName('entdataanivfund').AsString, 9, 2) + '/' +
          Copy(fdqueryentidade.FieldByName('entdataanivfund').AsString, 6, 2) + '/' +
          Copy(fdqueryentidade.FieldByName('entdataanivfund').AsString, 1, 4);
      mskdtcadastro.EditMask := '';
      if (fdqueryentidade.FieldByName('entdatacad').AsString = '01/01/1970') or
         (fdqueryentidade.FieldByName('entdatacad').AsString = '') then
        mskdtcadastro.Text := '  /  /    '
      else
        mskdtcadastro.Text := FormatDateTime('dd/mm/yyyy',
          StrToDate(fdqueryentidade.FieldByName('entdatacad').AsString));

      cin1.ActivePageIndex := 1; cin2.ActivePageIndex := 0;
      lblnomedopai.Text := fdqueryentidade.FieldByName('EntNomePai').AsString;
      lblnomedamae.Text := fdqueryentidade.FieldByName('EntNomeMae').AsString;
      lblresidecom.Text := fdqueryentidade.FieldByName('EntMoraCom').AsString;
      if fdqueryentidade.FieldByName('EntPossuiFilho').AsString = 'Sim' then
      begin
        filhossimnao := 'Sim';
        lblquantosfilhos.Visible := True;
        lblquantosfilhos.Text := fdqueryentidade.FieldByName('numerofilhos').AsString;
      end
      else if fdqueryentidade.FieldByName('EntPossuiFilho').AsString = 'Não' then
        filhossimnao := 'Não';

      cin2.ActivePageIndex := 1;
      lbltipocobcod.Text      := fdqueryentidade.FieldByName('tipocobcod').AsString;
      lbltipocobnome.Caption  := fdqueryentidade.FieldByName('tipocobnome').AsString;
      lblbconum.Text          := fdqueryentidade.FieldByName('bconum').AsString;
      lblnomebanco.Caption    := fdqueryentidade.FieldByName('bconome').AsString;
      lblagnum.Text           := fdqueryentidade.FieldByName('agnum').AsString;
      lblnomeagencia.Caption  := fdqueryentidade.FieldByName('agnome').AsString;
      lblgeocontacorrente.Text := fdqueryentidade.FieldByName('EntBcoAgCCorNum').AsString;
      lbldiadebitoautomatico.Text := fdqueryentidade.FieldByName('USERDia_Debito_CC').AsString;
      lblvalorcontribuicao.Text   := fdqueryentidade.FieldByName('USERValor_Contribuicao').AsString;
      buscanacombo('SIM', frmcadentidade, cbogeracarne); cbogeracarne.Refresh;
      lbldioceseid.Text      := fdqueryentidade.FieldByName('USERDiocese_id').AsString;
      lbldiocesenome.Caption := fdqueryentidade.FieldByName('USERNomeDiocese').AsString;
      buscanacombo('SIM', frmcadentidade, cborecebelembrete); cborecebelembrete.Refresh;

      cin2.ActivePageIndex := 2;
      lblativecodestr.Text               := fdqueryentidade.FieldByName('ativeconcodestr').AsString;
      lblnomeatividade_economica.Caption := retorna_ativ_econ(lblativecodestr.Text);
      lblorigcodestr.Text                := fdqueryentidade.FieldByName('origcodestr').AsString;
      lblnomeorigem.Caption              := fdqueryentidade.FieldByName('orignome').AsString;
      lblorigcodestr.Refresh; lblnomeorigem.Refresh;
      lblregiao.Text := fdqueryentidade.FieldByName('regcodestr').AsString;
      if lblregiao.Text <> '' then
        lblnomeregiao.Caption := retorna_regiaopais(lblregiao.Text);
      lblconceito.Text := fdqueryentidade.FieldByName('entconceito').AsString;
      lblregiao.Refresh; lblconceito.Refresh; lblnomeregiao.Refresh;

      cin1.ActivePageIndex := 3;
      fdquerysql.Close; fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text :=
        'SELECT entcodcontato FROM USER_geoapolo_entidade_contato WHERE geoentcod = ' +
        QuotedStr(lblentcod.Text);
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
        entcodcontato := fdquerysql.FieldByName('entcodcontato').AsString;

      fdquerysql4.Close; fdquerysql4.SQL.Clear;
      fdquerysql4.SQL.Text :=
        'SELECT econt.EntCodContato, econt.tipotratcod, uge.geoentnome, uge.tipolograd,' +
        ' uge.geoentender, uge.geoentendercomp, uge.geoentendernopi, uge.geoentbair,' +
        ' uge.geoentcep, econt.CidCod, cid.cidnomecomp, cid.ufsigla,' +
        ' econt.data_vigencia_inicial, econt.data_vigencia_final, econt.EntContatoCelular,' +
        ' econt.EntContatoTelefone, econt.CargoCodEstr, ugc.geocargonome' +
        ' FROM USER_geoapolo_entidade_contato econt' +
        ' INNER JOIN user_geoapolo_entidade uge WITH(NOLOCK) ON econt.EntCodContato = uge.geoentcod' +
        ' INNER JOIN user_geoapolo_cidades cid WITH(NOLOCK) ON econt.CidCod = cid.geocidcod' +
        ' LEFT JOIN USER_geoapolo_cargos ugc WITH(NOLOCK) ON econt.usercargocodestr = ugc.geocargocodestr' +
        ' WHERE econt.EntCodContato = ' + QuotedStr(entcodcontato);
      if executaracao(fdquerysql4, fdbanco, true, dtsfdquerysql4) then
      begin
        lblentcontatocod.Text    := fdquerysql14.FieldByName('EntCodContato').AsString;
        lbltipotratamento.Caption := fdquerysql14.FieldByName('tipotratcod').AsString;
        lblentcontatonome.Caption := fdquerysql14.FieldByName('entnome').AsString;
        mskcepcontato.Text       := fdquerysql14.FieldByName('entcep').AsString;
        buscanacombo(fdquerysql14.FieldByName('tipolograd').AsString, frmcadentidade, cbologradourocontato);
        lblenderecocontato.Text  := fdquerysql14.FieldByName('entender').AsString;
        lblnumerocontato.Text    := fdquerysql14.FieldByName('entendernopi').AsString;
        lblcomplendercontato.Text := fdquerysql14.FieldByName('entendercomp').AsString;
        lblbairrocontato.Text    := fdquerysql14.FieldByName('entbair').AsString;
        lblcargocontato.Text     := fdquerysql14.FieldByName('CargoCodEstr').AsString;
        lblcargocontatonome.Caption := fdquerysql14.FieldByName('cargonome').AsString;
        if not fdQuerySQL14.FieldByName('data_vigencia_inicial').IsNull then
          mskdtiniciovigencia.Text := FormatDateTime('dd/MM/yyyy',
            fdquerysql14.FieldByName('data_vigencia_inicial').AsDateTime)
        else
          mskdtiniciovigencia.Text := '';
        if not fdquerysql14.FieldByName('data_vigencia_final').IsNull then
          mskdtfinalvigencia.Text := FormatDateTime('dd/MM/yyyy',
            fdquerysql14.FieldByName('data_vigencia_final').AsDateTime)
        else
          mskdtfinalvigencia.Text := '';
      end;

      mostra_telefones_entidade(lblentcod.Text, frmentidades.integraentidadeapolo);
      mostra_entidade_contatoweb(lblentcod.Text, frmentidades.integraentidadeapolo);
      mostra_entidade_categoria(lblentcod.Text, frmentidades.integraentidadeapolo);
      cin1.ActivePageIndex := 4;
      mostra_entidade_documentos(lblentcod.Text, frmentidades.integraentidadeapolo);
      memobservacoes.Lines.Add(fdqueryentidade.FieldByName('geobservacoes').AsString);
      frmcadentidade.tabobservacoes.Refresh;
      cin1.ActivePageIndex := 0;
    end
    else if integracao = 'Alvo' then
    begin
      lblentcod.Text          := fdqueryentidade.FieldByName('entcod').AsString;
      lbllogradouro.Clear; lbllogradouroentrega.Clear; lbllogradourocobranca.Clear;
      lbltipotrat.Text        := fdqueryentidade.FieldByName('tipotratcod').AsString;
      lblentnome.Text         := fdqueryentidade.FieldByName('entnome').AsString;
      lblentnomefantasia.Text := fdqueryentidade.FieldByName('entnomefant').AsString;
      logradouro              := fdqueryentidade.FieldByName('entlograd').AsString;
      lbllogradouro.Text      := logradouro;
      lblentender.Text        := fdqueryentidade.FieldByName('entender').AsString;
      lblentenderno.Text      := fdqueryentidade.FieldByName('entenderno').AsString;
      lblentendercompl.Text   := fdqueryentidade.FieldByName('entendercomp').AsString;
      lblentbair.Text         := fdqueryentidade.FieldByName('entbair').AsString;
      mskcep.Text             := fdqueryentidade.FieldByName('entcep').AsString;
      lblcidcod.Text          := fdqueryentidade.FieldByName('cidcod').AsString;
      retorna_cidade_estado(lblcidcod.Text, frmentidades.integraentidadeapolo);
      lblcaixapostal.Text     := fdquerysql4.FieldByName('entcxapost').AsString;
      sexo := fdqueryentidade.FieldByName('entgenero').AsString;
      if sexo = 'F' then sexo := 'FEMININO'
      else if sexo = 'M' then sexo := 'MASCULINO';
      buscanacombo(sexo, frmcadentidade, cbosexo);
      lbllocaldereferencia.Text := fdqueryentidade.FieldByName('localreferencia_ender').AsString;
      buscanacombo(fdqueryentidade.FieldByName('tipofj').AsString, frmcadentidade, cbotipofj);
      buscanacombo(fdqueryentidade.FieldByName('entestcivil').AsString, frmcadentidade, cboestadocivil);
      falecido := fdqueryentidade.FieldByName('falecido').AsString;
      if falecido = 'S' then falecido := 'Sim' else if falecido = 'N' then falecido := 'Não';
      buscanacombo(falecido, frmcadentidade, cbofalecido);
      carrega_combo_grauescolar;
      if fdqueryentidade.FieldByName('entgrauescol').AsString = '' then
        codgrauescolar := '0'
      else
        codgrauescolar := fdqueryentidade.FieldByName('entgrauescol').AsString;
      fdquerysql11.Close; fdquerysql11.SQL.Clear;
      fdquerysql11.SQL.Text :=
        'SELECT grau_escolaridade FROM USER_geoapolo_grauescolaridade' +
        ' WHERE codigo_grauescolaridade = ' + codgrauescolar;
      if executaracao(fdquerysql11, fdbanco, true, dtsfdquerysql11) then
      begin
        grauescolaridade := modulo_dados.fdquerysql1.FieldByName('grau_escolaridade').AsString;
        buscanacombo(grauescolaridade, frmcadentidade, cboescolaridade);
      end;
      lblcargocodestr.Text    := fdqueryentidade.FieldByName('cargocodestr').AsString;
      mskdtnascimento.Text    := fdqueryentidade.FieldByName('entdataanivfund').AsString;
      mskdtcadastro.Text      := fdqueryentidade.FieldByName('entdatacad').AsString;

      cin1.ActivePageIndex := 1; cin2.ActivePageIndex := 0;
      lblnomedopai.Text := fdqueryentidade.FieldByName('entnomepai').AsString;
      lblnomedamae.Text := fdqueryentidade.FieldByName('entnomemae').AsString;
      lblresidecom.Text := fdqueryentidade.FieldByName('entmoracom').AsString;
      if fdqueryentidade.FieldByName('entpossuifilho').AsString = 'Sim' then
      begin
        filhossimnao := 'Sim';
        lblquantosfilhos.Visible := True;
        lblquantosfilhos.Text := fdqueryentidade.FieldByName('numerofilhos').AsString;
      end
      else if fdqueryentidade.FieldByName('entpossuifilho').AsString = 'Não' then
        filhossimnao := 'Não';

      cin2.ActivePageIndex := 2;
      lblativecodestr.Text               := fdquerysql.FieldByName('ativeconcodestr').AsString;
      lblnomeatividade_economica.Caption := fdquerysql.FieldByName('ativeconnome').AsString;
      lblativecodestr.Refresh; lblnomeatividade_economica.Refresh;
      lblorigcodestr.Text  := fdqueryentidade.FieldByName('origcodestr').AsString;
      lblnomeorigem.Caption := fdqueryentidade.FieldByName('orignome').AsString;
      lblorigcodestr.Refresh; lblnomeorigem.Refresh;
      lblregiao.Text        := fdqueryentidade.FieldByName('regcodestr').AsString;
      lblnomeregiao.Caption := retorna_regiaopais(lblregiao.Text);
      lblconceito.Text      := fdqueryentidade.FieldByName('entconceito').AsString;
      lblregiao.Refresh; lblconceito.Refresh; lblnomeregiao.Refresh;

      cin1.ActivePageIndex := 3;
      mostra_telefones_entidade(lblentcod.Text, frmentidades.integraentidadeapolo);
      mostra_entidade_contatoweb(lblentcod.Text, frmentidades.integraentidadeapolo);
      mostra_entidade_categoria(lblentcod.Text, frmentidades.integraentidadeapolo);

      fdquerysql.Close; fdquerysql.SQL.Clear;
      fdquerysql.SQL.Text :=
        'SELECT ect.entcod, ect.entcodcontato, ect.tipotratcod, ect.cargocodestr,' +
        ' ect.tipologradabrev, ect.entcontatoender, ect.entcontatoenderno, ect.entcontatoendercomp,' +
        ' ect.entcontatobair, ect.entcontatocep, ect.cidcod, cid.cidnomecomp' +
        ' FROM ent_contato ect WITH(NOLOCK)' +
        ' INNER JOIN cidade cid WITH(NOLOCK) ON ect.cidcod = cid.cidcod' +
        ' WHERE ect.entcod = ' + QuotedStr(lblentcod.Text);
      if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
        lblentcontatocod.Text := '';

      cin1.ActivePageIndex := 4;
      memobservacoes.Lines.Add('');
      mostra_entidade_documentos(lblentcod.Text, frmentidades.integraentidadeapolo);
      cin1.ActivePageIndex := 0; cin1.Refresh;
    end;
  end;
end;

// =============================================================================
// retorna_ativ_econ
// =============================================================================
function retorna_ativ_econ(ativeconcodestr: string): string;
begin
  with modulo_dados, frmcadentidade do
  begin
    fdquerysql.Close;
    fdquerysql.SQL.Clear;
    fdquerysql.SQL.Text :=
      'SELECT ae.AtivEconCodEstr, ae.AtivEconNome FROM ATIV_ECONOMICA ae WITH(NOLOCK)' +
      ' WHERE ae.AtivEconCodEstr = ' + QuotedStr(ativeconcodestr);
    if executaracao(fdquerysql, fdbanco, true, dtsfdquerysql) then
    begin
      lblativecodestr.Text               := ativeconcodestr;
      lblnomeatividade_economica.Caption := fdquerysql.FieldByName('ativeconnome').AsString;
      lblativecodestr.Refresh; lblnomeatividade_economica.Refresh;
    end;
  end;
end;

// =============================================================================
// gridentidadesKeyUp
// =============================================================================
procedure Tfrmentidades.gridentidadesKeyUp(Sender: TObject; var Key: Word; Shift: TShiftState);
begin
  with modulo_dados do
  begin
    if Key = VK_INSERT then
    begin
      application.CreateForm(TfrmCadEntidade, frmcadentidade);
      frmcadentidade.controle := 'INCLUSÃO';
      if (integraentidadeapolo = 'Mescla') or (integraentidadeapolo = 'Não Integra') then
        frmcadentidade.lblentcod.Text := geoapolo_configcod(frmprincipal.codigo_empresa,'USER_geoapolo_entidade', 'Sim')
      else if integraentidadeapolo = 'Integra' then
        frmcadentidade.lblentcod.Text := entcod_apolo_busca('S', frmcadentidade);
      frmcadentidade.ShowModal;
    end;

    if Key = VK_DELETE then
    begin
      if integraentidadeapolo = 'N' then
      begin
        resp := messagedlg('Confirma a Exclusão desta Entidade ? (Y/N)',
                           mtconfirmation, [mbyes, mbno], 0);
        if resp = idyes then
        begin
          fdquerysql3.Close; fdquerysql3.SQL.Clear;
          fdquerysql3.SQL.Text :=
            'DELETE FROM USER_geoapolo_entidade_webcontato WHERE geoentcod = :geoentcod';
          fdquerysql3.ParamByName('geoentcod').AsString := fdquerysql4.FieldByName('geoentcod').AsString;
          executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);

          fdquerysql3.Close; fdquerysql3.SQL.Clear;
          fdquerysql3.SQL.Text :=
            'DELETE FROM USER_geoapolo_entidade_comunicacao WHERE geoentcod = :geoentcod';
          fdquerysql3.ParamByName('geoentcod').AsString := fdquerysql4.FieldByName('geoentcod').AsString;
          executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);

          fdquerysql3.Close; fdquerysql3.SQL.Clear;
          fdquerysql3.SQL.Text :=
            'DELETE FROM USER_geoapolo_entidade_documentos WHERE geoentcod = :geoentcod';
          fdquerysql3.ParamByName('geoentcod').AsString := fdquerysql4.FieldByName('geoentcod').AsString;
          executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);

          fdquerysql3.Close; fdquerysql3.SQL.Clear;
          fdquerysql3.SQL.Text :=
            'DELETE FROM USER_geoapolo_entcateg WHERE geoentcod = :geoentcod';
          fdquerysql3.ParamByName('geoentcod').AsString := fdquerysql4.FieldByName('geoentcod').AsString;
          executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3);

          fdquerysql3.Close; fdquerysql3.SQL.Clear;
          fdquerysql3.SQL.Text :=
            'DELETE FROM USER_geoapolo_entidade WHERE geoentcod = :geoentcod';
          fdquerysql3.ParamByName('geoentcod').AsString := fdquerysql4.FieldByName('geoentcod').AsString;
          if executaracao(fdquerysql3, fdbanco, true, dtsfdquerysql3) then
          begin
            messagedlg('ENTIDADE REMOVIDA COM SUCESSO !!!', mtinformation, [mbok], 0);
            carrega_lista_entidades('GEOAPOLO', '', '');
            gridentidades.Refresh;
          end
          else
          begin
            messagedlg('EXISTE VINCULOS DESTA ENTIDADE DENTRO DO SISTEMA, DELEÇÃO NÃO SERÁ PERMITIDA!!!',
                       mtwarning, [mbok], 0);
            gridentidades.Refresh;
          end;
        end;
      end
      else if integraentidadeapolo = 'I' then
      begin
        messagedlg('PARA REMOVER ENTIDADES DA BASE APOLO, UTILIZE O APOLO OU ALVO ERP',
                   mtwarning, [mbok], 0);
        Exit;
      end;
    end;
  end;
end;

procedure Tfrmentidades.lblprocurarporKeyPress(Sender: TObject; var Key: Char);
begin
  if (Key = #13) or (Key = #$F3) then
  begin
    if Trim(lblprocurarpor.Text) <> '' then
      carrega_lista_entidades(cbobuscabanco.Text, 'Especifica', '')
    else
      carrega_lista_entidades(cbobuscabanco.Text, 'Consulta', '');
  end;
end;

// =============================================================================
// ConfigurarGrid
// =============================================================================
procedure Tfrmentidades.ConfigurarGrid;
begin
  with StringGrid1 do
  begin
    Align            := alNone;
    Font.Name        := 'Segoe UI';
    Font.Size        := 10;
    ColCount         := 4;
    FixedCols        := 0;
    FixedRows        := 1;
    DefaultRowHeight := 26;
    ScrollBars       := ssVertical;
    Options          := Options + [goFixedVertLine, goFixedHorzLine,
                                   goVertLine, goHorzLine] - [goEditing];
    ColWidths[0] := 150;
    ColWidths[1] := 200;
    ColWidths[2] := 200;
    ColWidths[3] := 140;
    Left   := memoplataformasve.Left;
    Top    := memoplataformasve.Top;
    Width  := memobaseapolo.Left + memobaseapolo.Width - memoplataformasve.Left;
    Height := memoplataformasve.Height;
  end;
  memoplataformasve.Visible := False;
  memobaseapolo.Visible     := False;
  StringGrid1.Visible       := True;
  StringGrid1.BringToFront;
end;

// =============================================================================
// MontarTelaComparacao
// =============================================================================
procedure Tfrmentidades.MontarTelaComparacao(QuerySVE, QueryBanco: TFDQuery);
var
  i, Row: Integer;
  ValSVE, ValAlvo: string;
begin
  GTotalDiferentes := 0;
  StringGrid1.Cells[0, 0] := 'Campo';
  StringGrid1.Cells[1, 0] := 'SVE  (clique para usar)';
  StringGrid1.Cells[2, 0] := 'Alvo  (clique para manter)';
  StringGrid1.Cells[3, 0] := 'Decisão';

  for i := 0 to TOTAL_CAMPOS_MAPA - 1 do
  begin
    ValSVE := ''; ValAlvo := '';
    if QuerySVE.FindField(MapaCampos[i].CampoSVE) <> nil then
      ValSVE := Trim(QuerySVE.FieldByName(MapaCampos[i].CampoSVE).AsString);
    if QueryBanco.FindField(MapaCampos[i].CampoAlvo) <> nil then
      ValAlvo := Trim(QueryBanco.FieldByName(MapaCampos[i].CampoAlvo).AsString);
    if not SameText(ValSVE, ValAlvo) then
    begin
      GLinhasDiferentes[GTotalDiferentes] := i;
      Inc(GTotalDiferentes);
    end;
  end;

  if GTotalDiferentes = 0 then
  begin
    lblmensagemgeoapolo.Caption    := '✔ Cadastros idênticos — nenhuma diferença encontrada.';
    lblmensagemgeoapolo.Font.Color := clGreen;
    StringGrid1.RowCount           := 2;
    StringGrid1.Cells[0, 1]        := '(cadastros idênticos, nenhuma ação necessária)';
    StringGrid1.Cells[1, 1] := ''; StringGrid1.Cells[2, 1] := ''; StringGrid1.Cells[3, 1] := '';
    spbatualizaentidadeapolo.Enabled := False;
    StringGrid1.Repaint;
    Exit;
  end;

  StringGrid1.RowCount := GTotalDiferentes + 1;
  for i := 0 to GTotalDiferentes - 1 do GDecisoes[i] := dlNenhuma;

  Row := 1;
  for i := 0 to GTotalDiferentes - 1 do
  begin
    ValSVE := ''; ValAlvo := '';
    if QuerySVE.FindField(MapaCampos[GLinhasDiferentes[i]].CampoSVE) <> nil then
      ValSVE := Trim(QuerySVE.FieldByName(MapaCampos[GLinhasDiferentes[i]].CampoSVE).AsString);
    if QueryBanco.FindField(MapaCampos[GLinhasDiferentes[i]].CampoAlvo) <> nil then
      ValAlvo := Trim(QueryBanco.FieldByName(MapaCampos[GLinhasDiferentes[i]].CampoAlvo).AsString);
    StringGrid1.Cells[0, Row] := MapaCampos[GLinhasDiferentes[i]].LabelExibicao;
    StringGrid1.Cells[1, Row] := ValSVE;
    StringGrid1.Cells[2, Row] := ValAlvo;
    StringGrid1.Cells[3, Row] := '— clique num valor —';
    Inc(Row);
  end;

  lblmensagemgeoapolo.Caption :=
    Format('⚠ %d diferença(s) encontrada(s) — %d pendente(s)', [GTotalDiferentes, GTotalDiferentes]);
  lblmensagemgeoapolo.Font.Color   := clRed;
  spbatualizaentidadeapolo.Enabled := False;
  spbatualizaentidadeapolo.Caption := '✔ Aplicar Selecionados';
  StringGrid1.Repaint;
end;

procedure Tfrmentidades.SelectCell(Sender: TObject; ACol, ARow: Integer; var CanSelect: Boolean);
begin
  // Intencionalmente vazia — ver StringGrid1SelectCell
end;

// =============================================================================
// ExtrairConjunto
// =============================================================================
function ExtrairConjunto(const Texto: string; Indice: Integer): string;
var
  Lista: TStringList;
begin
  Result := '';
  Lista := TStringList.Create;
  try
    Lista.CommaText := Texto;
    if (Indice >= 0) and (Indice < Lista.Count) then
      Result := Lista[Indice];
  finally
    Lista.Free;
  end;
end;

// =============================================================================
// ConfigurarGridCompleto
// =============================================================================
procedure Tfrmentidades.ConfigurarGridCompleto(const NomeBase: string);
var
  NomeModulo, NomeConfig: string;
begin
  with modulo_dados do
  begin
    if NomeBase = 'GeoApolo' then
      begin
        NomeModulo := 'entidades_geoapolo';
        NomeConfig := 'GEOENTIDADESGEOAPOLO';
      end
    else if NomeBase = 'Alvo' then
      begin
        NomeModulo := 'entidades_apolo';
        NomeConfig := 'GEOENTIDADESAPOLO';
      end
    else
      Exit;

    if not Assigned(fdqueryentidade) then Exit;
    if not fdqueryentidade.Active then Exit;
    if fdqueryentidade.RecordCount = 0 then Exit;

    try
      carrega_config(NomeConfig, frmentidades, cbocampo, cbordem, rdgcrescente, rdgdecrescente);
      configura_grid(NomeModulo, frmentidades, frmlogon.codigousuario, 'gridentidades',
                     gridentidades, modulo_dados.dtsfdqueryentidade);
      gridentidades.Refresh;
    except
      on E: Exception do
        ShowMessage('Erro ao configurar grid: ' + E.Message);
    end;
  end;
end;

end.
